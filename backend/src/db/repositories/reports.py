from uuid import UUID

from fastapi import status
from sqlalchemy import Row, text
from sqlalchemy.ext.asyncio import AsyncSession

from ...global_types import ImplementationError
from .exceptions import NotFoundError
from .models import ReportHeader
from .platform_roles import SYSTEM_SUBJECT
from .role_vocabulary import REPORT_ROLE_TABLE, get_precedence

"""Every query that touches `report` and its two ledgers."""

DEFAULT_REPORT_TITLE: str = "New report"

# Must keep in sync with seed.__main__.py
CREATOR_ROLE: str = "owner"

# ne statement rather than three keeps it to a single round trip.
#
# If that account is missing, `grantor` is empty, both child inserts write no
# rows, and the final SELECT returns nothing, which the caller turns into an error.
_CREATE_REPORT = """
    WITH grantor AS (
        SELECT user_id FROM app_user WHERE auth0_subject = :system_subject
    ),
    new_report AS (
        INSERT INTO report (title)
        VALUES (:title)
        RETURNING report_id
    ),
    ownership AS (
        INSERT INTO report_role_ledger
            (report_id, granted_to_user_id, set_by_user_id, role)
        SELECT new_report.report_id, :user_id, grantor.user_id, :role
        -- CROSS JOIN because `grantor` is a single row with nothing to join on
        FROM new_report CROSS JOIN grantor
        RETURNING report_id
    ),
    visibility AS (
        INSERT INTO report_visibility (report_id, set_by_user_id, public)
        SELECT new_report.report_id, grantor.user_id, FALSE
        FROM new_report CROSS JOIN grantor
        RETURNING report_id
    )
    SELECT ownership.report_id
    FROM ownership JOIN visibility ON visibility.report_id = ownership.report_id
"""


async def create_report(
    session: AsyncSession, owner_id: UUID, title: str = DEFAULT_REPORT_TITLE
) -> UUID:
    """
    Open a new report owned by `owner_id` and private to them.

    Returns the generated id. Raises `RuntimeError` if the system account the
    first grant is made by does not exist, which is a broken deployment rather
    than anything the caller did.
    """

    row: Row | None = (
        await session.execute(
            text(_CREATE_REPORT),
            {
                "title": title,
                "user_id": owner_id,
                "role": CREATOR_ROLE,
                "system_subject": SYSTEM_SUBJECT,
            },
        )
    ).one_or_none()

    if row is None:
        raise ImplementationError(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"No user with subject {SYSTEM_SUBJECT!r} to grant the first role.",
        )

    return row.report_id


MINIMUM_AUTHOR_ROLE: str = "editor"

# Note this differs from the LATERAL subqueries in `report_access`, which narrow
# to one known user before taking the latest row. Here every grantee is wanted,
# so there is no single id to correlate on.
#
# The whole aggregate hangs off a LATERAL so it can see `report.report_id`, and
# is LEFT joined so that a report whose owners have all been soft deleted still
# comes back (with no authors) rather than vanishing.
_REPORT_HEADER = """
    SELECT
        report.report_id,
        report.title,
        -- `array_agg` over no rows is NULL, not an empty array.
        COALESCE(authors.display_names, ARRAY[]::text[]) AS authors
    FROM report_live AS report

    LEFT JOIN LATERAL (
        SELECT array_agg(author.display_name ORDER BY current_grant.set_at)
            AS display_names
        FROM (
            SELECT DISTINCT ON (ledger.granted_to_user_id)
                ledger.granted_to_user_id, ledger.role, ledger.set_at
            FROM report_role_ledger AS ledger
            WHERE ledger.report_id = report.report_id
            ORDER BY ledger.granted_to_user_id, ledger.set_at DESC
        ) AS current_grant

        -- Inner join removes grants to users who no longer exist
        JOIN app_user_live AS author
            ON author.user_id = current_grant.granted_to_user_id

        JOIN report_role ON report_role.role = current_grant.role

        WHERE report_role.precedence >= :minimum_precedence
    ) AS authors ON TRUE

    WHERE report.report_id = :report_id
"""


async def get_report_header(session: AsyncSession, report_id: UUID) -> ReportHeader:
    """
    Read a report's title and the display names of everyone who can currently
    change its content, oldest grant first.

    Raises `NotFoundError` if the report does not exist or has been soft deleted.
    """

    row: Row | None = (
        await session.execute(
            text(_REPORT_HEADER),
            {
                "report_id": report_id,
                "minimum_precedence": await get_precedence(
                    session, REPORT_ROLE_TABLE, MINIMUM_AUTHOR_ROLE
                ),
            },
        )
    ).one_or_none()

    if row is None:
        raise NotFoundError(f"No report with id {report_id}.")

    return ReportHeader.model_validate(row)
