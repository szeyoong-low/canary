from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .src.dependencies import Environment, get_environment

app: FastAPI = FastAPI()

env: Environment = get_environment()

# Browsers enforce a Same-Origin Policy, which blocks clients from making requests
# to servers from a different origin unless explicitly allowed by the server
# through a Cross-Origin Resource Sharing (CORS) whitelist.
# Source: https://fastapi.tiangolo.com/tutorial/cors/
app.add_middleware(
    CORSMiddleware,
    # Comma-separated list of origins allowed to call this API.
    allow_origins=env.allow_origins.split(","),
    # Allow all Vercel previews.
    allow_origin_regex=env.allow_origin_regex,
    allow_headers=["*"],
    # By default, only GET methods are allowed
)


@app.get("/health")
def health():
    return {"status": "healthy"}
