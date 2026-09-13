from collections.abc import Awaitable, Callable
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Response, status

from ..auth.dependencies import OptionalUser, unauthorised
from ..db.repositories.models import ReportAccess
from ..db.repositories.report_access import get_report_access
from ..db.repositories.role_vocabulary import REPORT_ROLE_TABLE, get_precedence
from ..db.session import DBSession
from ..global_constants import REPORT_ROLE_HEADER, ReportRoleName

"""Resolving a caller's standing on one report, and enforcing it."""


"""Turning what a caller holds into whether they may act.

Deliberately pure and synchronous, like `auth.token`, so the rule that decides
who may read and write a report can be tested exhaustively with plain values
and no database, no HTTP and no event loop.
"""

# What being public is worth. A published report is readable by anyone, which
# is the same thing as everyone holding this role on it.
IMPLICIT_PUBLIC_ROLE = "viewer"

_UNGRANTED_PRECEDENCE = 0  # No grant at all


def _is_permitted(
    access: ReportAccess, minimum_precedence: int, public_role_precedence: int
) -> bool:
    """Whether the caller clears the bar an action sets."""
    granted: int = access.precedence or _UNGRANTED_PRECEDENCE

    # The higher of what they were granted and what the report gives away by
    # being public. Note this means publishing a report overrides an explicit
    # `revoked` grant for reading.
    effective_precedence: int = (
        max(granted, public_role_precedence) if access.public else granted
    )

    return effective_precedence >= minimum_precedence


def effective_role(access: ReportAccess, public_role_precedence: int) -> str | None:
    """The role this caller actually holds, which is not always the one granted
    to them: a public report hands `viewer` to everyone, including callers with
    no grant at all.

    `None` means they hold nothing, which only a private report can produce.

    The same question `_is_permitted` answers, phrased as a name rather than a
    yes or no, so a client can be told what it may attempt.
    """

    granted: int = access.precedence or _UNGRANTED_PRECEDENCE

    if access.public and public_role_precedence > granted:
        return IMPLICIT_PUBLIC_ROLE

    return access.role


async def resolve_report_access(
    report_id: UUID, user: OptionalUser, session: DBSession
) -> ReportAccess:
    """Gather everything a route needs to decide what this caller may do with this
    report. `report_id` is a path parameter"""

    return await get_report_access(
        session, report_id, user.user_id if user is not None else None
    )


# Resolved once per request even if several dependencies ask for it, so the
# access query runs once no matter how many rules a route layers on top.
CallerReportAccess = Annotated[ReportAccess, Depends(resolve_report_access)]


def require_report_role(
    minimum_role: ReportRoleName,
) -> Callable[..., Awaitable[ReportAccess]]:
    """
    Build a dependency that lets a caller through only if they hold at least
    `minimum_role` on the report, and returns their access so the route does
    not have to ask for it twice.

    A factory because a FastAPI dependency takes only what it can be given by
    injection, so the one thing that varies per route has to be closed over.

    Used as:
        access: Annotated[ReportAccess, Depends(require_report_role("editor"))]

    A report that does not exist never reaches here: `resolve_report_access`
    raises `NotFoundError`, which `api.errors` already answers with a 404.
    """

    async def guard(
        access: CallerReportAccess,
        user: OptionalUser,
        session: DBSession,
        response: Response,
    ) -> ReportAccess:
        # Read once and used twice: to decide, and to name what was decided.
        public_role_precedence: int = await get_precedence(
            session, REPORT_ROLE_TABLE, IMPLICIT_PUBLIC_ROLE
        )

        if _is_permitted(
            access,
            await get_precedence(session, REPORT_ROLE_TABLE, minimum_role),
            public_role_precedence,
        ):
            role: str | None = effective_role(access, public_role_precedence)
            if role is not None:
                response.headers[REPORT_ROLE_HEADER] = role

            return access

        if user is None:
            raise unauthorised("Not authenticated", token_supplied=False)

        raise HTTPException(
            status.HTTP_403_FORBIDDEN, f"Requires at least the {minimum_role} role"
        )

    return guard
