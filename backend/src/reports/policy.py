from ..db.repositories.models import ReportAccess

"""Turning what a caller holds into whether they may act.

Deliberately pure and synchronous, like `auth.token`, so the rule that decides
who may read and write a report can be tested exhaustively with plain values
and no database, no HTTP and no event loop.
"""

# What being public is worth. A published report is readable by anyone, which
# is the same thing as everyone holding this role on it.
IMPLICIT_PUBLIC_ROLE = "viewer"

_UNGRANTED_PRECEDENCE = 0  # No grant at all


def _effective_precedence(access: ReportAccess, public_role_precedence: int) -> int:
    """
    How much authority the caller actually has over this report.

    The higher of what they were granted and what the report gives away by
    being public. Note this means publishing a report overrides an explicit
    `revoked` grant for reading.
    """

    granted: int = access.precedence or _UNGRANTED_PRECEDENCE

    return max(granted, public_role_precedence) if access.public else granted


def is_permitted(
    access: ReportAccess, minimum_precedence: int, public_role_precedence: int
) -> bool:
    """Whether the caller clears the bar an action sets."""
    return _effective_precedence(access, public_role_precedence) >= minimum_precedence
