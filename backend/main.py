from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .dependencies import dependency

app = FastAPI(dependencies=[Depends(dependency.get_environment)])

env = dependency.get_environment()

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
