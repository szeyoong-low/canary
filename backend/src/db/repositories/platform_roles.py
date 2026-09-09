from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# The non-assumable account that grants what nobody else can. `provider|id` is
# the shape of an Auth0 subject and no Auth0 connection is named `system`, so no
# login can ever produce this subject.
SYSTEM_SUBJECT = "system|canary"
SYSTEM_DISPLAY_NAME = "Canary"

# What a newly provisioned account starts as: an ordinary signed-in user.
DEFAULT_PLATFORM_ROLE = "app_user"


async def grant_first_platform_role(
    session: AsyncSession, user_id: UUID, role: str
) -> None:
    """Give a user their opening platform role, granted by the system account.
    Does nothing if the user already holds any grant."""

    # Written as one statement so the check and the insert cannot be separated
    # by a concurrent writer. The grantor is resolved in the same statement
    # rather than read first, which saves a round trip.

    await session.execute(
        text("""
            INSERT INTO platform_role_ledger (granted_to_user_id, set_by_user_id, role)
            SELECT :user_id, grantor.user_id, :role
            FROM app_user AS grantor
            WHERE grantor.auth0_subject = :granted_by
              AND NOT EXISTS (
                  SELECT 1
                  FROM platform_role_ledger AS history
                  WHERE history.granted_to_user_id = :user_id
              )
        """),
        {
            "user_id": user_id,
            "role": role,
            "granted_by": SYSTEM_SUBJECT,
        },
    )
