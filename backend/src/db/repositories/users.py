from sqlalchemy import Row, text
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User

"""Every query that touches `app_user`"""

# Spelled out rather than `SELECT *`, so that adding a column to the table does
# not silently feed an extra field.
_USER_COLUMNS = "user_id, auth0_subject, display_name, created_at"

# The transaction is owned by whoever opened it (the request, via `get_session`).
# All repositories called from one handler commit or roll back together.


async def get_active_user_by_subject(
    session: AsyncSession, subject: str
) -> User | None:
    """
    Find an active user by their Auth0 subject.

    `None` rather than a raised `NotFoundError`: the caller that matters is
    authentication, for which "no row yet" is the ordinary first-login path and
    not an error at all.
    """

    result = await session.execute(
        text(
            f"SELECT {_USER_COLUMNS} FROM app_user_live WHERE auth0_subject = :subject"
        ),
        {"subject": subject},
    )

    row: Row | None = result.one_or_none()

    return User.model_validate(row) if row is not None else None


async def provision_user(
    session: AsyncSession, subject: str, display_name: str
) -> User:
    """
    Insert the user if this subject is new, and otherwise bring the existing row
    up to date. Returns the row either way.

    Just-in-time provisioning: the first authenticated request from a subject
    creates the account. Callers reach this only after a read for that subject
    missed, so the conflict path is the exception rather than the rule (either
    a concurrent first request or a row the read could not see).

    Note this differs from `seed.seed_user`, which leaves `display_name` alone
    on conflict. It writes a placeholder that this function is meant to overwrite.
    """

    result = await session.execute(
        text(f"""
            INSERT INTO app_user (auth0_subject, display_name)
            VALUES (:subject, :display_name)
            ON CONFLICT (auth0_subject) DO UPDATE
            SET deleted_at = NULL, display_name = EXCLUDED.display_name
            RETURNING {_USER_COLUMNS}
        """),
        {"subject": subject, "display_name": display_name},
    )

    # The two rows the read cannot see are a soft-deleted user and the seeded
    # administrator placeholder. Both are meant to be reclaimed here.
    return User.model_validate(result.one())
