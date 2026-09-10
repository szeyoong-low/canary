from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from http import HTTPMethod

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .src.agent import router as agent
from .src.api.errors import register_error_handlers
from .src.api.preconditions import ETAG_HEADER, IF_MATCH_HEADER
from .src.auth.dependencies import authenticate
from .src.db.engine import get_engine, verify_connection
from .src.dependencies import Environment, get_environment
from .src.global_constants import AUTHORIZATION_HEADER, CONTENT_TYPE_HEADER
from .src.terminal import dev_router as terminal


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Runs either side of the application serving requests.
    https://fastapi.tiangolo.com/advanced/events/"""

    await verify_connection()

    yield

    # Closes the pooled connections rather than leaving the server to drop them,
    # which would leave the database holding backends open until they time out.
    await get_engine().dispose()


app: FastAPI = FastAPI(lifespan=lifespan)

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
    expose_headers=[ETAG_HEADER],
    allow_methods=[HTTPMethod.GET, HTTPMethod.POST],
)

register_error_handlers(app)

# Applied to every route the router carries, so a new endpoint is authenticated.
# by existing here rather than by remembering to ask. `/health` below is exempt
# by not being on a router at all.
# FastAPI caches dependency results per request, so no double work
REQUIRES_AUTHENTICATION = [Depends(authenticate)]

app.include_router(agent.router)  # , dependencies=REQUIRES_AUTHENTICATION)

if env.development:
    app.include_router(terminal.router)


@app.get("/health")
def health():
    return {"status": "healthy"}
