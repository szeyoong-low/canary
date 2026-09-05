"""live_views

Revision ID: 374a1bc53573
Revises: a09066d30034
Create Date: 2026-09-05 18:42:02.157194

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "374a1bc53573"
down_revision: str | Sequence[str] | None = "a09066d30034"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# A view per table that can hide rows, so that a query which forgets the filter
# is not a data leak.
#
# Each live view also has `xmin`, the system column Postgres stamps with the
# transaction that last wrote the row. Optimistic locking reads it, but system
# columns are not inherited by view by default. This matters because the
# application role is to be granted rights on these views and the base tables.
#
# These views are auto-updatable (https://www.postgresql.org/docs/current/sql-createview.html#SQL-CREATEVIEW-UPDATABLE-VIEWS),
# but I'd rather be safe and let writes go to the base tables.
#
# The SQL is written out literally rather than derived from the `MetaData`, and
# the views are deliberately absent from it. A migration is a snapshot of the
# schema at one point in time. Importing application code would let a later edit
# silently rewrite what this revision does. It would also make autogenerate treat
# a view as a table it has not created yet.
#
# `SELECT *` is expanded and frozen when the view is created, so it is equivalent
# to spelling out the columns. The consequence is that a later migration adding a
# column to one of these tables must also CREATE OR REPLACE its view, or the new
# column is invisible to every read path.
# CREATE OR REPLACE VIEW can only append columns at the end and can't retype or
# reorder existing ones. Anything else is DROP + CREATE, which fails if another
# view depends on it.

LIVE_VIEWS: dict[str, tuple[str, str]] = {
    "app_user_live": ("app_user", "deleted_at IS NULL"),
    "report_live": ("report", "deleted_at IS NULL"),
    "text_store_live": ("text_store", "deleted_at IS NULL"),
    "blob_store_live": ("blob_store", "deleted_at IS NULL"),
    "content_container_live": ("content_container", "deleted_at IS NULL"),
    "content_mount_live": ("content_mount", "position IS NOT NULL"),
}


def upgrade() -> None:
    """Upgrade schema."""
    
    for name, (table, predicate) in LIVE_VIEWS.items():
        # The f-string interpolation is safe here. These are hardcoded
        # identifiers in a file we control, not user input. 
        op.execute(
            f"CREATE VIEW {name} AS "
            f"SELECT *, xmin FROM {table} WHERE {predicate}"
        )


def downgrade() -> None:
    """Downgrade schema."""

    # No view depends on another, so the order is immaterial, but dropping in
    # reverse keeps the two halves readable as mirrors of each other.
    for name in reversed(LIVE_VIEWS):
        op.execute(f"DROP VIEW {name}")
