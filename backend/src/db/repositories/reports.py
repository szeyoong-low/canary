from uuid import UUID

from fastapi import status
from sqlalchemy import Row, text
from sqlalchemy.ext.asyncio import AsyncSession

from ...global_types import ImplementationError
from .platform_roles import SYSTEM_SUBJECT

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
