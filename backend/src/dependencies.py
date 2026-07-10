from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

"""Dependency injection as shown in https://fastapi.tiangolo.com/advanced/settings/#lru-cache-technical-details"""


DOTENV_FILE: str = ".env"


class Environment(BaseSettings):
    """
    Load environment variables from the provided .env file case-insensitively.
    The .env file must contain exactly the variables specified below.
    For example, ALLOW_ORIGINS is loaded into allow_origins.
    """

    allow_origins: str
    allow_origin_regex: str

    model_config = SettingsConfigDict(env_file=DOTENV_FILE)


@lru_cache
def get_environment() -> Environment:
    return Environment()  # pyright: ignore[reportCallIssue] (Initialised by pydantic_settings)
