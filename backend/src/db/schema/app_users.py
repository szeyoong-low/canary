from sqlalchemy import (
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

"""Users, the platform roles they can hold, and the grant history."""


app_user = Table(
    "app_user",  # `user` is reserved in SQL
    metadata,
    Column(
        "user_id",
        UUID(),
        primary_key=True,
        server_default=text("uuidv7()"),
    ),
    # The `sub` claim from Auth0. Opaque, and the only stable link to the
    # identity provider.
    Column("auth0_subject", Text, nullable=False, unique=True),
    Column("display_name", Text, nullable=False),
    Column(
        "created_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        # `now()` is transaction start time, so every row written in one
        # transaction shares a timestamp.
        server_default=func.now(),
    ),
    Column("deleted_at", TIMESTAMP(timezone=True), nullable=True),
)


# As data rather than as a type. Adding one is an INSERT, not a migration.
#
# The role name is the primary key, so `platform_role_ledger.role` already holds
# the readable value and only needs a join when precedence is actually wanted.
platform_role = Table(
    "platform_role",
    metadata,
    Column("role", Text, primary_key=True),
    # Higher outranks lower. Seed sparsely (100, 200, 300) so a level can be
    # inserted between two existing ones without renumbering the rest.
    Column("precedence", Integer, nullable=False, unique=True),
    CheckConstraint("precedence > 0", name="precedence_positive"),
)


# Append-only history of platform role grants. Nothing here is ever updated or
# deleted, which is why there is no `deleted_at`: the current role for a user is
# the row with the greatest `set_at`, and the rows behind it are the audit trail
# admins will query.
#
# Immutability is enforced by revoking UPDATE/DELETE from the application role.
platform_role_ledger = Table(
    "platform_role_ledger",
    metadata,
    Column(
        "granted_to_user_id",
        UUID(),
        ForeignKey("app_user.user_id"),
        nullable=False,
    ),
    # Who made the grant. Non-nullable, which means the first grant of all needs
    # a pre-existing actor: the non-assumable system user, created by the seed
    # script before any other row.
    Column(
        "set_by_user_id",
        UUID(),
        ForeignKey("app_user.user_id"),
        nullable=False,
    ),
    Column("role", Text, ForeignKey("platform_role.role"), nullable=False),
    Column(
        "set_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    # One grant per user per instant. Ordering the key by user first makes it
    # usable for the "latest role for this user" lookup, which is the query the
    # authorisation layer runs on nearly every request.
    PrimaryKeyConstraint("granted_to_user_id", "set_at"),
)
