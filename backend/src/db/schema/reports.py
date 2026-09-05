from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    Table,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID

from . import metadata

"""Reports, the roles they can be shared under, and the grant history."""


report = Table(
    "report",
    metadata,
    Column(
        "report_id",
        UUID(),
        primary_key=True,
        server_default=text("uuidv7()"),
    ),
    Column("title", Text, nullable=False),
    Column(
        "created_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    # Denormalised from the content blocks: a cache so listing reports does not
    # have to aggregate over every container. Whoever writes a block is
    # responsible for bumping it in the same transaction.
    Column(
        "content_last_modified_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    Column("deleted_at", TIMESTAMP(timezone=True), nullable=True),
)


# Data rather than a type, exactly as `platform_role` is. Adding roles later is
# an INSERT, not a migration.
#
# Kept separate from `platform_role` despite the identical shape: the two
# vocabularies are unrelated, and a shared table would need a discriminator
# column that every foreign key would then have to carry.
report_role = Table(
    "report_role",
    metadata,
    Column("role", Text, primary_key=True),
    # Higher outranks lower. Seed sparsely (100, 200, 300) so a level can be
    # inserted between two existing ones without renumbering the rest.
    Column("precedence", Integer, nullable=False, unique=True),
    CheckConstraint("precedence > 0", name="precedence_positive"),
)


# Append-only history of report role grants. As with `platform_role_ledger`,
# nothing here is ever updated or deleted, so there is no `deleted_at`: the
# current role is the row with the greatest `set_at`, and the rows behind it are
# the audit trail.
report_role_ledger = Table(
    "report_role_ledger",
    metadata,
    Column("report_id", UUID(), ForeignKey("report.report_id"), nullable=False),
    Column(
        "granted_to_user_id",
        UUID(),
        ForeignKey("app_user.user_id"),
        nullable=False,
    ),
    # Who made the grant. Non-nullable, so the first grant on a report is made
    # by its creator (self-grant), and the very first grant of all by the system
    # user the seed script creates.
    Column(
        "set_by_user_id",
        UUID(),
        ForeignKey("app_user.user_id"),
        nullable=False,
    ),
    Column("role", Text, ForeignKey("report_role.role"), nullable=False),
    Column(
        "set_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    # Report first, because the primary key's index is only usable from its
    # leading column. That ordering serves both "who has access to this report"
    # (admin and share dialogs) and, on the two-column prefix, "what is this
    # user's role on this report" — the lookup the authorisation layer runs on
    # nearly every request. Keying user-first would serve only the latter.
    PrimaryKeyConstraint("report_id", "granted_to_user_id", "set_at"),
)


# Append-only history of public/private flips, kept apart from the role ledger
# because visibility is a property of the report rather than a grant to a user.
report_visibility = Table(
    "report_visibility",
    metadata,
    Column("report_id", UUID(), ForeignKey("report.report_id"), nullable=False),
    Column(
        "set_by_user_id",
        UUID(),
        ForeignKey("app_user.user_id"),
        nullable=False,
    ),
    Column("public", Boolean, nullable=False),
    Column(
        "set_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    # One flip per report per instant, and the leading column is what the
    # "current visibility of this report" lookup filters on.
    PrimaryKeyConstraint("report_id", "set_at"),
)
