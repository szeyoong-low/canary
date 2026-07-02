from fastapi import Depends, FastAPI

from .dependencies import dependency

app = FastAPI(dependencies=[Depends(dependency.get_environment)])


@app.get("/health")
def health():
    return {"status": "healthy"}
