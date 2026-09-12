from collections.abc import Sequence
from json import dumps
from typing import Any
from uuid import UUID

from sqlalchemy import Row, text
from sqlalchemy.ext.asyncio import AsyncSession

from .exceptions import MissingVersionError, NotFoundError, StaleWriteError
from .models import BlobBlock, ReportContentContainer, TextBlock

"""Every query that touches `text_store` and `blob_store`, and the
containers and mounts that point at them."""

# Spelled out rather than `SELECT *`, so that adding a column to a table does
# not silently feed an extra field.
_TEXT_COLUMNS = (
    "text_id",
    "payload",
    "size_bytes",
    "created_at",
    "content_last_modified_at",
)

_BLOB_COLUMNS = (
    "blob_id",
    "payload",
    "type",
    "size_bytes",
    "created_at",
    "content_last_modified_at",
)


def _select_list(columns: tuple[str, ...], table_alias: str = "") -> str:
    """
    Render a column list, optionally qualified by a table alias.

    `xmin` is appended to every list as it is the row's version. To be returned
    as ETag. The driver decodes `xid` to a Python `int`.
    """

    prefix: str = f"{table_alias}." if table_alias else ""

    return ", ".join(
        [*(f"{prefix}{column}" for column in columns), f"{prefix}xmin AS version"]
    )


async def get_active_text_block(session: AsyncSession, text_id: UUID) -> TextBlock:
    """Read one prose block, with the version a later update must present."""

    row: Row | None = (
        await session.execute(
            text(
                f"SELECT {_select_list(_TEXT_COLUMNS)} FROM text_store_live"
                " WHERE text_id = :row_id"
            ),
            {"row_id": text_id},
        )
    ).one_or_none()

    if row is None:
        raise NotFoundError(f"No text block with id {text_id}.")

    return TextBlock.model_validate(row)


async def get_active_blob_block(session: AsyncSession, blob_id: UUID) -> BlobBlock:
    """Read one chart or dataset block, with its version."""

    row: Row | None = (
        await session.execute(
            text(
                f"SELECT {_select_list(_BLOB_COLUMNS)} FROM blob_store_live"
                " WHERE blob_id = :row_id"
            ),
            {"row_id": blob_id},
        )
    ).one_or_none()

    if row is None:
        raise NotFoundError(f"No blob block with id {blob_id}.")

    return BlobBlock.model_validate(row)


def _versioned_update(
    table: str, id_column: str, assignments: str, returned_columns: str
) -> str:
    """
    Build the compare-and-set statement for a soft-deletable table.

    Doing the read and the write as two arms of one statement means both see the
    same snapshot, so three outcomes are distinguishable in one round trip:

    | rows | new_version | meaning |
    |---|---|---|
    | none | - | no such row or soft deleted |
    | one | NULL | written since the caller last read it |
    | one | present | updated and this is the new version |
    """

    # Everything interpolated is a hardcoded identifier from this module.

    # `t.xmin` in the RETURNING is the *new* value: an UPDATE stamps the row it
    # writes with the current transaction's id, which is what the caller sends
    # back as `If-Match` next time.

    return f"""
        WITH existing AS (
            SELECT {id_column}, xmin AS version
            FROM {table}
            WHERE {id_column} = :row_id AND deleted_at IS NULL
        ),
        updated AS (
            UPDATE {table} AS t
            SET {assignments}, content_last_modified_at = now()
            FROM existing AS e -- Implicit JOIN
            WHERE t.{id_column} = e.{id_column} AND t.xmin = :version
            RETURNING {returned_columns}
        )
        SELECT e.version AS current_version, u.*
        -- Check if row exists in the first place
        FROM existing AS e LEFT JOIN updated AS u ON TRUE
    """


async def _execute_versioned_update(
    session: AsyncSession, statement: str, parameters: dict[str, Any]
) -> Row:
    """Run a statement built by `_versioned_update` and translates its outcomes.
    Returns the updated row."""

    # The version is the client's, and a client that never read the row cannot
    # have one. Caught here rather than at the route so the invariant holds for
    # every caller, including scripts.

    if not parameters["version"]:
        raise MissingVersionError("This update requires the row's current version.")

    row: Row | None = (await session.execute(text(statement), parameters)).one_or_none()

    if row is None:
        raise NotFoundError(f"No row with id {parameters['row_id']}.")

    if row.version is None:
        raise StaleWriteError(
            "The row has been modified since it was read.",
            current_version=row.current_version,
        )

    return row


_UPDATE_TEXT = _versioned_update(
    "text_store",
    "text_id",
    "payload = :payload, size_bytes = :size_bytes",
    # Qualified, because `existing` is also in scope inside the RETURNING.
    _select_list(_TEXT_COLUMNS, "t"),
)


async def update_text_block(
    session: AsyncSession, text_id: UUID, payload: str, version: int
) -> TextBlock:
    """
    Replace a prose block's payload, provided nobody has written it since
    `version` was read.

    Raises: `NotFoundError`, `StaleWriteError`, `MissingVersionError`
    """

    row: Row = await _execute_versioned_update(
        session,
        _UPDATE_TEXT,
        {
            "row_id": text_id,
            "payload": payload,
            "size_bytes": len(payload.encode()),
            "version": version,
        },
    )

    return TextBlock.model_validate(row)


_UPDATE_BLOB = _versioned_update(
    "blob_store",
    "blob_id",
    # asyncpg has no idea what type a parameter in a raw statement should be, and
    # sends this one as text. The cast is what makes Postgres store it as JSONB.
    "payload = CAST(:payload AS jsonb), size_bytes = :size_bytes",
    _select_list(_BLOB_COLUMNS, "t"),
)


async def update_blob_block(
    session: AsyncSession, blob_id: UUID, payload: Any, version: int
) -> BlobBlock:
    """
    Replace a blob block's payload, provided nobody has written it since
    `version` was read.

    `type` is deliberately not updatable: a chart does not become a dataset, and
    a container's pointers are typed by position.

    Raises: `NotFoundError`, `StaleWriteError`, `MissingVersionError`
    """

    # Serialised here rather than left to the driver
    # - asyncpg expects a string for a JSONB parameter
    # - the byte count below must be of something concrete
    # Postgres re-serialises JSONB on the way in, so the stored size is close to
    # but not exactly this. Just a preview figure.
    serialised: str = dumps(payload, separators=(",", ":"))  # For most compact JSON

    row: Row = await _execute_versioned_update(
        session,
        _UPDATE_BLOB,
        {
            "row_id": blob_id,
            "payload": serialised,
            "size_bytes": len(serialised.encode()),
            "version": version,
        },
    )

    return BlobBlock.model_validate(row)


# One row per mounted container, with both payloads already resolved.
#
# `content_mount_live` is the live view, so it carries only rows whose
# `position` is set: containers in the recycling bin are filtered out before
# anything else is joined, and the ORDER BY below is over a column that cannot
# be NULL.
#
# Every join is INNER. A container whose chart or prose has been soft deleted is
# broken rather than partial, and dropping it is better than returning a card
# with a hole in it. The consequence is that deleting one block hides the whole
# container, which is the intended reading of these tables: blocks are not
# reusable and a container owns all three.
_REPORT_CONTAINERS = """
    SELECT
        container.container_id,
        chart.payload AS chart,
        prose.payload AS prose
    FROM content_mount_live AS mount

    JOIN content_container_live AS container
        ON container.container_id = mount.container_id
    JOIN blob_store_live AS chart ON chart.blob_id = container.chart_id
    JOIN text_store_live AS prose ON prose.text_id = container.prose_id

    WHERE mount.report_id = :report_id
    ORDER BY mount.position
"""


async def get_report_containers(
    session: AsyncSession, report_id: UUID
) -> list[ReportContentContainer]:
    """
    Read every container mounted in a report, in the order they are displayed.

    An empty list is an ordinary answer. Whether it exists is a separate
    question, answered by the dependency.
    """

    rows: Sequence[Row] = (
        await session.execute(text(_REPORT_CONTAINERS), {"report_id": report_id})
    ).all()

    return [ReportContentContainer.model_validate(row) for row in rows]
