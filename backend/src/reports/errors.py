from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exception_handlers import http_exception_handler
from httpx import codes

from ..db.repositories.exceptions import (
    MissingVersionError,
    NotFoundError,
    StaleWriteError,
)
from .optimistic_locking import ETAG_HEADER, format_etag

"""Decides what a repository failure looks like over HTTP.

Registered as exception handlers rather than caught in each route for uniformity
and automatic enforcement.

Each handler translates the failure into an `HTTPException` and hands it to
FastAPI's own handler rather than building a response.
https://fastapi.tiangolo.com/tutorial/handling-errors/#reuse-fastapis-exception-handlers
"""

# Starlette types a handler as taking a bare `Exception`, so each one narrows the
# type back with an assert.


async def handle_not_found(request: Request, exception: Exception) -> Response:
    """The row is absent or soft deleted. Indistinguishable to a client."""
    assert isinstance(exception, NotFoundError)

    return await http_exception_handler(
        request, HTTPException(codes.NOT_FOUND, exception.message)
    )


async def handle_stale_write(request: Request, exception: Exception) -> Response:
    """The client's `If-Match` did not match the row, so the write was refused.

    412 rather than 409 as the client is well-aware of the source of conflict.
    https://www.rfc-editor.org/info/rfc9110/#name-409-conflict

    The version now in force rides back on the `ETag`, so a client that wants to
    re-read and merge does not need a second round trip to learn it."""

    assert isinstance(exception, StaleWriteError)

    return await http_exception_handler(
        request,
        HTTPException(
            codes.PRECONDITION_FAILED,
            exception.message,
            headers={ETAG_HEADER: format_etag(exception.current_version)},
        ),
    )


async def handle_missing_version(request: Request, exception: Exception) -> Response:
    """The request omitted `If-Match` on a route that cannot be written blind."""
    assert isinstance(exception, MissingVersionError)

    return await http_exception_handler(
        request, HTTPException(codes.PRECONDITION_REQUIRED, exception.message)
    )


def register_error_handlers(app: FastAPI) -> None:
    """Called once at startup. `DatabaseError` itself is intentionally not
    registered: a failure nobody has classified is a 500."""

    # `add_exception_handler` rather than the `@app.exception_handler` decorator,
    # which would need the `app` object at import time and make this module and
    # `main` import each other.
    #
    # Kept out of `main` for neatness

    app.add_exception_handler(NotFoundError, handle_not_found)
    app.add_exception_handler(StaleWriteError, handle_stale_write)
    app.add_exception_handler(MissingVersionError, handle_missing_version)
