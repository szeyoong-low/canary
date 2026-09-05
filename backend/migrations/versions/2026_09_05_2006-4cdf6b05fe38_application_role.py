"""application_role

Revision ID: 4cdf6b05fe38
Revises: 374a1bc53573
Create Date: 2026-09-05 20:06:33.914272

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4cdf6b05fe38"
down_revision: str | Sequence[str] | None = "374a1bc53573"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# The role the backend connects as, distinct from the migration role that owns
# every object.
#
# ALTER DEFAULT PRIVILEGES would remove that chore, and is deliberately not used.
# It would hand this role rights on tables nobody reviewed.
APPLICATION_ROLE = "canary_app"  # This is the master role of the database


GRANTS: dict[str, tuple[str, ...]] = {
    # Base tables
    "app_user": ("SELECT", "INSERT", "UPDATE"),
    "report": ("SELECT", "INSERT", "UPDATE"),
    "text_store": ("SELECT", "INSERT", "UPDATE"),
    "blob_store": ("SELECT", "INSERT", "UPDATE"),
    "content_container": ("SELECT", "INSERT", "UPDATE"),
    "content_mount": ("SELECT", "INSERT", "UPDATE"),
    
    # Views
    "app_user_live": ("SELECT", "INSERT", "UPDATE"),
    "report_live": ("SELECT", "INSERT", "UPDATE"),
    "text_store_live": ("SELECT", "INSERT", "UPDATE"),
    "blob_store_live": ("SELECT", "INSERT", "UPDATE"),
    "content_container_live": ("SELECT", "INSERT", "UPDATE"),
    "content_mount_live": ("SELECT", "INSERT", "UPDATE"),

    # Ledgers
    "platform_role_ledger": ("SELECT", "INSERT"),
    "report_role_ledger": ("SELECT", "INSERT"),
    "report_visibility": ("SELECT", "INSERT"),

    # Vocabularies
    "platform_role": ("SELECT",),
    "report_role": ("SELECT",),
}


def upgrade() -> None:
    """Upgrade schema."""

    # Roles are cluster-wide but migrations run per database, so this revision
    # may find the role already made by the same migration against a sibling
    # database. Postgres has no CREATE ROLE IF NOT EXISTS, hence the DO block.
    #
    # No password and no LOGIN privilege are set here. A password would be
    # committed to git and echoed into the migration logs.
    # On on RDS the role authenticates with IAM instead and locally it is
    # granted a password out of band.
    op.execute(f"""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT FROM pg_roles WHERE rolname = '{APPLICATION_ROLE}'
            ) THEN
                CREATE ROLE {APPLICATION_ROLE} LOGIN;
            END IF;
        END
        $$
    """)

    # Since PostgreSQL 15 the public schema no longer grants CREATE to PUBLIC,
    # but USAGE is still held. Granting it explicitly means this role keeps
    # working if PUBLIC's rights are ever revoked, which is a common hardening
    # step. https://stackoverflow.com/questions/17338621/what-does-grant-usage-on-schema-do-exactly
    op.execute(f"GRANT USAGE ON SCHEMA public TO {APPLICATION_ROLE}")

    for relation, privileges in GRANTS.items():
        op.execute(f"GRANT {', '.join(privileges)} ON {relation} TO {APPLICATION_ROLE}")

    # `rds_iam` is created by RDS and does not exist on the local Compose
    # Postgres, so the same revision has to run in both places. Holding it lets
    # the backend authenticate with a short-lived IAM token and keeps a database
    # password out of existence entirely.
    op.execute(f"""
        DO $$
        BEGIN
            IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'rds_iam') THEN
                GRANT rds_iam TO {APPLICATION_ROLE};
            END IF;
        END
        $$
    """)


def downgrade() -> None:
    """Downgrade schema."""

    # REVOKE before DROP: a role holding privileges anywhere in the cluster
    # cannot be dropped. This only revokes what was granted in *this* database,
    # which is the honest limit of a per-database migration. If the role was
    # also granted rights in a sibling database, the DROP below will fail and
    # that is better than this revision silently reaching outside its scope.
    for relation in reversed(GRANTS):
        op.execute(f"REVOKE ALL ON {relation} FROM {APPLICATION_ROLE}")

    op.execute(f"REVOKE ALL ON SCHEMA public FROM {APPLICATION_ROLE}")
    op.execute(f"DROP ROLE IF EXISTS {APPLICATION_ROLE}")
