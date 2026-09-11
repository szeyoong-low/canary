from collections.abc import Awaitable, Callable
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from httpx import codes

from ..auth.dependencies import OptionalUser, unauthorised
from ..db.repositories.models import ReportAccess
from ..db.repositories.report_access import get_report_access
from ..db.repositories.report_roles import get_precedence
from ..db.session import DBSession
from .policy import IMPLICIT_PUBLIC_ROLE, is_permitted
from .types import ReportRole

"""Resolving a caller's standing on one report, and enforcing it."""


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
    minimum_role: ReportRole,
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
        access: CallerReportAccess, user: OptionalUser, session: DBSession
    ) -> ReportAccess:
        if is_permitted(
            access,
            await get_precedence(session, minimum_role),
            await get_precedence(session, IMPLICIT_PUBLIC_ROLE),
        ):
            return access

        if user is None:
            raise unauthorised("Not authenticated", token_supplied=False)

        raise HTTPException(
            codes.FORBIDDEN, f"Requires at least the {minimum_role} role"
        )

    return guard
