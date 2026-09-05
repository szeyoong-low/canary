import asyncio
from logging.config import fileConfig

from alembic import context
from backend.src.db.schema import metadata
from backend.src.dependencies import get_environment
from sqlalchemy import URL, pool, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

# The Alembic Config object, providing access to the values in alembic.ini.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# What autogenerate diffs the live database against.
target_metadata = metadata

# An arbitrary but stable identifier for the migration lock.
# Advisory locks live in a single server-wide namespace.
MIGRATION_LOCK_KEY: int = 4_919_202_501


def database_url() -> URL:
    return get_environment().database_url


def run_migrations_offline() -> None:
    """
    Render migrations as SQL to stdout instead of running them (`--sql`).

    Nothing connects, so this is the way to review the DDL a revision would emit
    before it reaches RDS. Offline mode cannot read `alembic_version` to work out
    where the database currently is, so it needs an explicit range:
    `alembic upgrade base:head --sql`.
    """

    context.configure(
        url=database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # Off by default, which means a changed column type is silently missed.
        # `compare_server_default` stays off: it reports spurious differences,
        # because Postgres echoes defaults back in a normalised form that rarely
        # matches the string we wrote.
        compare_type=True,
    )

    with context.begin_transaction():
        # Migrations run at container startup, so a deployment that replaces
        # several tasks at once has several of them racing to migrate. Postgres
        # advisory locks serialise that.
        #
        # The `_xact_` variant is bound to the surrounding transaction and is
        # released when that transaction ends, including when it fails. A plain
        # `pg_advisory_lock` would survive a crashed migration and deadlock every
        # later deployment.
        #
        # https://www.postgresql.org/docs/current/explicit-locking.html#ADVISORY-LOCKS
        connection.execute(
            text("SELECT pg_advisory_xact_lock(:key)"), {"key": MIGRATION_LOCK_KEY}
        )

        context.run_migrations()


async def run_async_migrations() -> None:
    """Open a connection and hand it to the synchronous migration machinery."""

    # Built directly rather than with `async_engine_from_config`, because the URL
    # no longer lives in alembic.ini. Feeding it back in via `set_main_option`
    # would send the password through configparser, which reads `%` as
    # interpolation syntax — and RDS generates passwords with punctuation.
    #
    # NullPool because this process runs a handful of statements and exits;
    # pooling would only leave connections to clean up.
    connectable = create_async_engine(database_url(), poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        # Alembic's migration API is synchronous. `run_sync` runs it against a
        # sync-style façade over the async connection, on the same event loop.
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations against a live database."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
