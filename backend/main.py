from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from http import HTTPMethod

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from .src.db.engine import get_engine, verify_connection
from .src.dependencies import Environment, get_environment
from .src.global_constants import (
    AUTHORIZATION_HEADER,
    CONTENT_TYPE_HEADER,
    LOCATION_HEADER,
    REPORT_ROLE_HEADER,
)
from .src.observability.telemetry import setup_logging
from .src.reports import dev_router as agent
from .src.reports import router as reports
from .src.reports.errors import register_error_handlers
from .src.reports.optimistic_locking import ETAG_HEADER, IF_MATCH_HEADER
from .src.terminal import dev_router as terminal


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Runs either side of the application serving requests.
    https://fastapi.tiangolo.com/advanced/events/"""

    # First, so that a failure below is reported in the structured format.
    # Inside lifespan, not at module top, so it runs only when a server
    # actually serves
    setup_logging()

    await verify_connection()

    yield

    # Closes the pooled connections rather than leaving the server to drop them,
    # which would leave the database holding backends open until they time out.
    await get_engine().dispose()


def generate_operation_id(route: APIRoute) -> str:
    """Names an endpoint in the OpenAPI schema.

    FastAPI's default mangles the path into the name, giving
    `get_specific_report_reports__report_id__get`, which becomes the method name
    in any generated client. `route.name` is the endpoint function's own name,
    so the frontend reads back the same names this file declares.

    Names must be unique across every router. FastAPI warns about duplicates at
    startup rather than failing quietly; should that ever bite, tag the routers
    and prefix the tag here.
    https://fastapi.tiangolo.com/advanced/generate-clients/
    """

    return route.name


app: FastAPI = FastAPI(
    lifespan=lifespan, generate_unique_id_function=generate_operation_id
)

env: Environment = get_environment()

# Browsers enforce a Same-Origin Policy, which blocks clients from making requests
# to servers from a different origin unless explicitly allowed by the server
# through a Cross-Origin Resource Sharing (CORS) whitelist.
# Source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS#simple_requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=env.allow_origins.split(
        ","
    ),  # Comma-separated list of origins allowed to call this API
    allow_origin_regex=env.allow_origin_regex,  # Allow all development previews
    allow_headers=[AUTHORIZATION_HEADER, CONTENT_TYPE_HEADER, IF_MATCH_HEADER],
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Access-Control-Expose-Headers
    expose_headers=[ETAG_HEADER, LOCATION_HEADER, REPORT_ROLE_HEADER],
    allow_methods=[HTTPMethod.GET, HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.DELETE],
)

register_error_handlers(app)

app.include_router(reports.router)

if env.development:
    app.include_router(agent.router)
    app.include_router(terminal.router)


@app.get("/health")
def health():
    return {"status": "healthy"}
