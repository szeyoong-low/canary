from uuid import UUID

from sqlalchemy import Row, text
from sqlalchemy.ext.asyncio import AsyncSession

from .exceptions import NotFoundError
from .models import ReportAccess

"""Who may do what with a report, read in one round trip."""

# Two ledgers, each append-only, each holding the current answer in its most
# recent row. `LATERAL` is what lets a subquery in the FROM clause see a column
# from the row to its left, which is how each one narrows to this report or this
# caller before taking the latest row. Without it the subqueries could not be
# correlated and would have to aggregate over the whole ledger.
# https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-LATERAL
#
# Every join is LEFT: a report may have no visibility history, and a caller may
# hold no grant. A missing row is an answer, not a failure, so neither may drop
# the report from the result.
#
# `:user_id` is NULL for an anonymous caller. The grant join then matches
# nothing and yields NULLs of its own accord, so signed-in and signed-out take
# the same path through the same statement.
#
# The caller's platform role is deliberately absent: it is not report-scoped, so
# it is read by its own dependency and would be unreusable welded in here.
_ACCESS_QUERY = """
    SELECT
        report.report_id,
        -- A report with no visibility row has never been published, so private.
        COALESCE(visibility.public, FALSE) AS public,
        report_grant.role,
        report_role.precedence
    FROM report_live AS report

    LEFT JOIN LATERAL (
        SELECT history.public
        FROM report_visibility AS history
        WHERE history.report_id = report.report_id
        ORDER BY history.set_at DESC
        LIMIT 1
    ) AS visibility ON TRUE

    LEFT JOIN LATERAL (
        SELECT history.role
        FROM report_role_ledger AS history
        WHERE history.report_id = report.report_id
          AND history.granted_to_user_id = :user_id
        ORDER BY history.set_at DESC
        LIMIT 1
    ) AS report_grant ON TRUE

    -- A plain join onto the vocabulary: a ledger row's role is a foreign key,
    -- so where there is a grant there is always a precedence to go with it.
    LEFT JOIN report_role ON report_role.role = report_grant.role

    -- LATERAL because each subquery references the outer report_id/user_id
    -- LEFT JOIN because all three may legitimately be absent
    WHERE report.report_id = :report_id
"""


async def get_report_access(
    session: AsyncSession, report_id: UUID, user_id: UUID | None
) -> ReportAccess:
    """
    Read what `user_id` may do with `report_id`. Pass `None` for a visitor who
    is not signed in.

    Raises `NotFoundError` if the report does not exist or has been soft deleted
    """

    row: Row | None = (
        await session.execute(
            text(_ACCESS_QUERY), {"report_id": report_id, "user_id": user_id}
        )
    ).one_or_none()

    if row is None:
        raise NotFoundError(f"No report with id {report_id}")

    return ReportAccess.model_validate(row)
