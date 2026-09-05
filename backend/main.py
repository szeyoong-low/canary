from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from http import HTTPMethod

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .src.agent import router as agent
from .src.db.engine import get_engine, verify_connection
from .src.dependencies import Environment, get_environment
from .src.global_constants import CONTENT_TYPE_HEADER
from .src.terminal import router as terminal


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
    # Comma-separated list of origins allowed to call this API.
    allow_origins=env.allow_origins.split(","),
    # Allow all Vercel previews.
    allow_origin_regex=env.allow_origin_regex,
    allow_headers=[CONTENT_TYPE_HEADER],
    allow_methods=[HTTPMethod.GET, HTTPMethod.POST],
)

app.include_router(agent.router)
app.include_router(terminal.router)


@app.get("/health")
def health():
    return {"status": "healthy"}
