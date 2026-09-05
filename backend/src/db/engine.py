import ssl
from functools import cache
from typing import Any

import boto3
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ..dependencies import DatabaseSettings, get_database_settings

"""The connection pool and the session factory."""

# Amazon's root certificates for every region, placed here by the Dockerfile.
# Verifying against the public trust store instead would accept any certificate
# a public CA has issued for the endpoint's name, which is a weaker claim than
# "RDS issued this".
RDS_CA_BUNDLE = "/etc/ssl/certs/rds-global-bundle.pem"


@cache
def _rds_client(region: str) -> Any:
    """
    Cached because constructing a boto3 client is slow, while asking an existing
    one for a token is not.

    The client is only a signer here. `generate_db_auth_token` performs no API
    call: it builds a SigV4 signature locally, so calling it on the connection
    path costs no round trip. Fetching the task role's credentials the first time
    does, but botocore caches and refreshes those in the background.
    """
    return boto3.client("rds", region_name=region)


def _use_iam_tokens(engine: AsyncEngine, settings: DatabaseSettings) -> None:
    """
    Supply a freshly signed IAM token as the password for each new connection.

    A token lasts fifteen minutes and is only checked when a connection is
    opened, so it cannot be part of the URL the engine holds for its lifetime —
    the pool would keep presenting an expired one. `do_connect` fires immediately
    before the driver connects, which is the one place the value can be current.

    The listener is attached to `sync_engine`: SQLAlchemy's asyncio layer drives
    the ordinary synchronous dialect underneath, and that is what emits the event.
    https://docs.sqlalchemy.org/en/20/core/events.html
    """

    # Guaranteed by `DatabaseSettings`, which refuses to build in `iam` mode
    # without one. Asserted rather than assumed so the type is narrowed.
    assert settings.region is not None

    @event.listens_for(engine.sync_engine, "do_connect")
    def provide_token(
        dialect: Any, conn_rec: Any, cargs: Any, cparams: dict[str, Any]
    ) -> None:
        # Mutating `cparams` and returning None lets SQLAlchemy carry on and make
        # the connection itself. Returning a connection here would bypass it.
        cparams["password"] = _rds_client(settings.region).generate_db_auth_token(
            DBHostname=settings.host,
            Port=settings.port,
            DBUsername=settings.app_username, # Must match the database role exactly
            Region=settings.region,
        )


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

    engine = create_async_engine(
        settings.application_url,

        # The engine holds TCP connections open between requests. Anything that
        # kills them server-side leaves dead sockets in the pool that may still
        # be handed out. Pre-ping spends one trivial round trip per checkout to
        # verify the connection is alive, and silently replaces it if not.
        # https://docs.sqlalchemy.org/en/20/core/pooling.html
        pool_pre_ping=True,

        # RDS refuses IAM authentication over an unencrypted connection, so the
        # two are enabled together. `create_default_context` already requires a
        # valid certificate and a matching hostname; naming the bundle only
        # narrows who is trusted to issue it.
        #
        # This ties transport security to the authentication mode, which is not
        # strictly the same question. It holds while `iam` means "on RDS" and
        # `password` means "the local container", and would need separating the
        # day a password-authenticated connection points at a real server.
        connect_args=(
            {"ssl": ssl.create_default_context(cafile=RDS_CA_BUNDLE)}
            if settings.auth == "iam"
            else {}
        ),
    )

    if settings.auth == "iam":
        _use_iam_tokens(engine, settings)

    return engine


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
