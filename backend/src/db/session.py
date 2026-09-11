from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .engine import get_session_factory

"""One database transaction per request, scoped by a FastAPI dependency."""


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """
    Hand a handler a session that is already inside a transaction, and settle
    that transaction on the way out.

    Deliberately NOT applied application-wide. The transaction is open for as
    long as the handler runs, holding one of the pool's fifteen connections.
    Only routers that need to perform CRUD operations should opt in.
    """

    # The factory is cached, so this is the one process-wide factory
    #
    # The outer context manager owns the session. On exit it closes it, which
    # returns the pooled connection to the engine.
    #
    # The inner context manager owns the transaction. Leaving the block normally
    # emits COMMIT. Leaving it because an exception passed through emits ROLLBACK.
    #
    # FastAPI throws an exception raised inside the handler back into this
    # generator at the `yield` before re-raising it to the client, so a handler
    # that raises HTTPException(409) rolls back rather than committing a partial
    # write.
    #
    # https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/
    async with get_session_factory()() as session, session.begin():
        yield session


type DBSession = Annotated[AsyncSession, Depends(get_db_session)]
