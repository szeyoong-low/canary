from functools import lru_cache

from . import Environment


@lru_cache
def get_environment():
    """For dependency injection, as shown in https://fastapi.tiangolo.com/advanced/settings/#lru-cache-technical-details"""
    return Environment()  # pyright: ignore[reportCallIssue] (Initialised by pydantic_settings)