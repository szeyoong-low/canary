"""
Puts the rows in place that the application cannot start without: the role
vocabularies, the system user, and the first administrator.

Idempotent, so it is safe to run against an environment that is already seeded.

Run from `backend/` with the repository root on the import path:
`SEED_ADMIN_SUBJECT=<subject> PYTHONPATH=.. uv run python -m backend.seed`.
"""

import asyncio
import os

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from ..src.dependencies import DatabaseSettings, get_database_settings

# `provider|id` is the shape of an Auth0 subject, and no Auth0 connection is
# named `system`, so no login can ever produce this subject. That is what makes
# the account non-assumable: it exists solely to be the grantor of the first grant.
SYSTEM_SUBJECT = "system|canary"
SYSTEM_DISPLAY_NAME = "Canary"

ADMIN_SUBJECT_VARIABLE = "SEED_ADMIN_SUBJECT"

# Overwritten by just-in-time provisioning when the administrator first signs in
# and the real name arrives from the identity provider.
ADMIN_PLACEHOLDER_DISPLAY_NAME = "Administrator"

ADMIN_ROLE = "admin"

PLATFORM_ROLE_TABLE = "platform_role"

# Sparse, so a level can be inserted between two of these without renumbering
# the rest. Higher outranks lower.
PLATFORM_ROLES: dict[str, int] = {
    "suspended": 100,
    "app_user": 200,
    "admin": 300,
}

REPORT_ROLE_TABLE = "report_role"

REPORT_ROLES: dict[str, int] = {
    "revoked": 100,
    "viewer": 200,
    "commenter": 300,
    "editor": 400,
    "owner": 500,
}


async def seed_roles(
    connection: AsyncConnection, table: str, roles: dict[str, int]
) -> None:
    """
    Insert the vocabulary.

    `ON CONFLICT DO NOTHING` on the role name makes this idempotent. It also
    means an edited precedence in this file will NOT be applied to a database
    that already holds that role: changing one is a migration.
    """

    await connection.execute(
        text(f"""
            INSERT INTO {table} (role, precedence)
            VALUES (:role, :precedence)
            ON CONFLICT (role) DO NOTHING
        """),
        [
            {"role": role, "precedence": precedence}
            for role, precedence in roles.items()
        ],
    )


async def seed_user(
    connection: AsyncConnection, subject: str, display_name: str
) -> None:
    """
    Insert a user or revive one that was soft deleted.

    The display name is left alone on conflict.
    """

    # `auth0_subject` carries a plain unique constraint so a soft-deleted row
    # still occupies the subject and a bare INSERT would fail. Clearing
    # `deleted_at` restores the user to their past roles, data, and audit trails.

    await connection.execute(
        text("""
            INSERT INTO app_user (auth0_subject, display_name)
            VALUES (:subject, :display_name)
            ON CONFLICT (auth0_subject) DO UPDATE SET deleted_at = NULL
        """),
        {"subject": subject, "display_name": display_name},
    )


async def grant_platform_role(
    connection: AsyncConnection, subject: str, role: str, granted_by: str
) -> None:
    """
    Record a platform role grant, unless that role is already in force.

    Written as one statement so the check and the insert cannot be separated by
    a concurrent writer.
    """

    # The ledger is append-only and keyed partly on `set_at`, so nothing stops a
    # second run inserting another grant a few seconds later. It would be valid
    # and harmless to authorisation, which reads the latest row, but it would put
    # grants in the audit trail that nobody made.

    await connection.execute(
        text("""
            INSERT INTO platform_role_ledger (granted_to_user_id, set_by_user_id, role)
            SELECT grantee.user_id, grantor.user_id, :role
            FROM app_user AS grantee, app_user AS grantor
            WHERE grantee.auth0_subject = :subject
              AND grantor.auth0_subject = :granted_by
              AND NOT EXISTS (
                  SELECT 1
                  FROM platform_role_ledger AS current
                  WHERE current.granted_to_user_id = grantee.user_id
                    AND current.role = :role
                    -- Only the newest grant counts.
                    AND current.set_at = (
                        SELECT max(set_at)
                        FROM platform_role_ledger AS history
                        WHERE history.granted_to_user_id = grantee.user_id
                    )
              )
        """),
        {"role": role, "subject": subject, "granted_by": granted_by},
    )


async def seed() -> None:
    settings: DatabaseSettings = get_database_settings()

    # The Auth0 sub claim for the person who should be the first admin
    admin_subject: str | None = os.environ.get(ADMIN_SUBJECT_VARIABLE)

    if not admin_subject:
        raise SystemExit(
            f"{ADMIN_SUBJECT_VARIABLE} must be set to the Auth0 subject "
            "(`provider|id`) of the first administrator."
        )

    # Built here rather than reusing `get_engine`, which is the application's
    # pool and connects as the application role. A one-shot script wants neither.
    engine = create_async_engine(settings.owner_url)

    # `begin` commits when the block leaves without an exception, so a failure
    # part-way through leaves the database as it was rather than half seeded.
    async with engine.begin() as connection:
        await seed_roles(connection, PLATFORM_ROLE_TABLE, PLATFORM_ROLES)
        await seed_roles(connection, REPORT_ROLE_TABLE, REPORT_ROLES)

        await seed_user(connection, SYSTEM_SUBJECT, SYSTEM_DISPLAY_NAME)
        await grant_platform_role(
            connection, SYSTEM_SUBJECT, ADMIN_ROLE, granted_by=SYSTEM_SUBJECT
        )

        await seed_user(connection, admin_subject, ADMIN_PLACEHOLDER_DISPLAY_NAME)
        await grant_platform_role(
            connection, admin_subject, ADMIN_ROLE, granted_by=SYSTEM_SUBJECT
        )

    await engine.dispose()

    print(f"Seeded. Administrator: {admin_subject}")


if __name__ == "__main__":
    asyncio.run(seed())
