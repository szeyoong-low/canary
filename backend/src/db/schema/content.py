from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    ForeignKey,
    Identity,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ENUM, JSONB, TIMESTAMP, UUID

from . import metadata

"""Content blocks, the containers that group them, and where they are mounted."""


text_store = Table(
    "text_store",
    metadata,
    Column("text_id", BigInteger, Identity(), primary_key=True),
    Column("payload", Text, nullable=False),
    # Written by the application, just a cached value for displaying a preview.
    # A generated column would keep it honest, but `blob_store` cannot have one
    # (see below), and it is better to have both stores behave the same way than
    # to have one of the two silently drift.
    Column("size_bytes", BigInteger, nullable=False),
    Column(
        "created_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    Column(
        "content_last_modified_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    Column("deleted_at", TIMESTAMP(timezone=True), nullable=True),
    CheckConstraint("size_bytes >= 0", name="size_bytes_non_negative"),
)


# Bound to the `metadata` so the type is created before, and dropped after, the
# tables that use it.
BLOB_TYPE = ENUM("chart", "dataset", name="blob_type", metadata=metadata)


blob_store = Table(
    "blob_store",
    metadata,
    Column("blob_id", BigInteger, Identity(), primary_key=True),
    Column("payload", JSONB, nullable=False),
    # A native Postgres ENUM. Not a lookup table, unlike the role vocabularies.
    # `ALTER TYPE ... ADD VALUE` extends it later, but values cannot be dropped
    # or renamed without recreating the type and rewriting every column that
    # uses it.
    Column("type", BLOB_TYPE, nullable=False),
    # Written by the application, just a cached value for displaying a preview.
    # Cannot be a generated column: Postgres requires the expression to be
    # IMMUTABLE, and the jsonb-to-text cast is only STABLE (its output depends on
    # server settings), so `octet_length(payload::text)` is rejected.
    Column("size_bytes", BigInteger, nullable=False),
    Column(
        "created_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    Column(
        "content_last_modified_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    Column("deleted_at", TIMESTAMP(timezone=True), nullable=True),
    CheckConstraint("size_bytes >= 0", name="size_bytes_non_negative"),
)


# Note that nothing at this level forces `chart_id` to reference a blob whose
# `type` is 'chart'. Enforcing that needs a composite unique on
# `blob_store` plus a discriminator column here to hang a two-column foreign key
# on — deliberately deferred, as the application writes both sides.
content_container = Table(
    "content_container",
    metadata,
    Column("container_id", BigInteger, Identity(), primary_key=True),
    Column("chart_id", BigInteger, ForeignKey("blob_store.blob_id"), nullable=False),
    Column("prose_id", BigInteger, ForeignKey("text_store.text_id"), nullable=False),
    Column("dataset_id", BigInteger, ForeignKey("blob_store.blob_id"), nullable=False),
    Column(
        "created_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    Column("deleted_at", TIMESTAMP(timezone=True), nullable=True),
    # Blocks are not reusable, so the chart and the dataset must be separate
    # rows even though both live in `blob_store`.
    CheckConstraint("chart_id <> dataset_id", name="chart_and_dataset_distinct"),
)


# Where a container sits, if anywhere. Split out from the container itself so
# that a container can exist with no report at all (a future personal
# collection), and so the reorder path rewrites this narrow table rather than
# rows carrying the block pointers.
#
# Two states, distinguished by `position`:
#
#   report_id | position | meaning
#   ----------|----------|-----------------------------------------------
#   non-null  | non-null | mounted in the report at that position
#   non-null  | null     | unmounted, in the report's recycling bin
#
# The second state additionally requires the container's `deleted_at` to be set,
# since that is what drives the retention period. A CHECK cannot express this:
# Postgres only evaluates checks against a single row of a single table. It is
# enforced in the repository layer for now, and a trigger is the escalation if
# that proves too loose.
content_mount = Table(
    "content_mount",
    metadata,
    Column(
        "container_id",
        BigInteger,
        ForeignKey("content_container.container_id"),
        primary_key=True,
    ),
    Column("report_id", UUID(), ForeignKey("report.report_id"), nullable=False),
    Column("position", BigInteger, nullable=True),
    # DEFERRABLE INITIALLY DEFERRED so a reorder can rewrite the whole list in
    # one transaction without staging around transient duplicates. The cost is
    # that a deferrable constraint's index is not usable for query planning and
    # cannot back a foreign key.
    UniqueConstraint(
        "report_id",
        "position",
        deferrable=True,
        initially="DEFERRED",
    ),
    CheckConstraint("position >= 0", name="position_non_negative"),
)
