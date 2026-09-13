"""
Prints every row in the database to stdout, so that a remote environment's data
can be read in CloudWatch.

For looking, not for restoring. The rows are printed as Postgres' COPY text
format, one tab separated line each, because that is what the database can hand
over without a client library and it stays readable in a log viewer.

Run from `backend/` with the repository root on the import path:
`PYTHONPATH=.. uv run python -m backend.debug`.
"""

import asyncio
import sys
from typing import Any

from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from ..src.db.schema import metadata
from ..src.dependencies import DatabaseSettings, get_database_settings

# Tables to leave out, by name.
#
# `blob_store` holds the full chart specification behind every report as JSON. It
# dwarfs everything else, it is unreadable in a log viewer, and a single row can
# exceed CloudWatch's 256 KB limit on one event and be split mid-value. Clear
# this set when a blob is the thing being looked at.
SKIP_TABLES: frozenset[str] = frozenset({"blob_store"})

# Precedes each table's rows. Written as an SQL comment so that the output is
# still something psql would accept, and so that it is easy to search the log
# for where one table ends and the next begins.
TABLE_MARKER = "-- table: "


async def dump_table(connection: AsyncConnection, table: str, sink: Any) -> None:
    """
    Write one table's rows to `sink` in Postgres' COPY text format.

    SQLAlchemy has no COPY support of its own: it is a protocol-level operation
    rather than a statement whose results come back as rows. So this reaches past
    the engine to the asyncpg connection underneath, which implements it.
    """

    # `get_raw_connection` returns SQLAlchemy's pool wrapper; `driver_connection`
    # is the asyncpg connection inside it.
    raw_connection = await connection.get_raw_connection()
    asyncpg_connection = raw_connection.driver_connection

    sink.write(f"{TABLE_MARKER}{table}\n".encode())

    # asyncpg accepts a file-like object here and performs the writes in a thread
    # so that a slow sink cannot block the event loop. Rows are streamed as they
    # arrive rather than collected first, which is the point of COPY over a
    # SELECT: nothing here ever holds the whole table.
    await asyncpg_connection.copy_from_table(table, output=sink)


async def dump() -> None:
    settings: DatabaseSettings = get_database_settings()

    # The owner rather than the application role, so that nothing is filtered out
    # by the permissions the application deliberately runs under. Built here
    # rather than reusing `get_engine` for the same reason the seed does: a
    # one-shot script wants neither the pool nor the application's identity.
    #
    # `REPEATABLE READ` because the dump spans many statements. Under the default
    # `READ COMMITTED` each one takes its own snapshot, so a write landing
    # part-way through can be visible to a later table but not an earlier one,
    # which is how a child row appears to have no parent.
    engine = create_async_engine(settings.owner_url, isolation_level="REPEATABLE READ")

    # `sorted_tables` orders the tables parent before child, following the
    # foreign keys, so a row's parent is always printed above it. It also means a
    # table added to the schema later appears here without editing this file.
    tables = [
        table.name for table in metadata.sorted_tables if table.name not in SKIP_TABLES
    ]

    # COPY hands over bytes, so this writes to the binary stream underneath
    # stdout. Everything goes through that one stream rather than mixing `print`
    # with it, because the two buffer separately and their output would interleave
    # out of order.
    sink = sys.stdout.buffer

    # The transaction is what makes the isolation level above mean anything: a
    # snapshot is taken by the first statement and held until the block ends, so
    # every table is read as the database stood at one instant. Nothing is
    # written, so there is nothing to commit; leaving the block ends it.
    async with engine.connect() as connection, connection.begin():
        for table in tables:
            await dump_table(connection, table, sink)

    sink.flush()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(dump())
