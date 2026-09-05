from functools import cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ..dependencies import DatabaseSettings, get_database_settings

"""The connection pool and the session factory."""

# Both are built lazily behind `@cache` rather module-level constants, which run
# on import and demand a fully-populated `.env`. This breaks unit tests and any
# tooling that merely imports the package. Lazy factories allow patching in tests.


@cache
def get_engine() -> AsyncEngine:
    """
    The engine owns the connection pool, so there must be exactly one per process.
    https://docs.sqlalchemy.org/en/20/core/engines.html

    Pool sizing is left at the SQLAlchemy defaults: `pool_size=5` plus
    `max_overflow=10`, so at most 15 connections per process.

    A db.t4g.micro has 2 vCPU and 1 GB of memory, so it permits around 100.
    This gives us headroom for around 6 concurrent processes.
    https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Limits.html
    """

    settings: DatabaseSettings = get_database_settings()

    return create_async_engine(
        settings.application_url,
        # The engine holds TCP connections open between requests. Anything that
        # kills them server-side leaves dead sockets in the pool that may still
        # be handed out. Pre-ping spends one trivial round trip per checkout to
        # verify the connection is alive, and silently replaces it if not.
        # https://docs.sqlalchemy.org/en/20/core/pooling.html
        pool_pre_ping=True,
    )


@cache
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    Builds sessions bound to the shared engine. A session is a single unit of
    work that holds one checked-out connection and one transaction.

    The factory is process-wide, but the sessions it produces are not shared —
    a request handler takes one, uses it, and returns it.
    """

    return async_sessionmaker(
        get_engine(),
        # By default a commit marks every object loaded in the session as stale,
        # so the next attribute read silently re-queries the database. Under
        # asyncio that implicit IO raises instead of loading, which is a
        # confusing way to discover the behaviour.
        expire_on_commit=False,
    )
