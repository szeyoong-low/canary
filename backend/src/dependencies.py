from functools import cache

from pydantic_settings import BaseSettings, SettingsConfigDict

"""Dependency injection as shown in https://fastapi.tiangolo.com/advanced/settings/"""


DOTENV_FILE: str = ".env"


class Environment(BaseSettings):
    """
    Load environment variables from the provided .env file case-insensitively.
    The .env file must contain exactly the variables specified below.
    For example, ALLOW_ORIGINS is loaded into allow_origins.
    """

    allow_origins: str
    allow_origin_regex: str
    fmp_api_key: str
    fmp_base_url: str
    openrouter_api_key: str
    planning_node_model: str
    planning_node_provider: str

    model_config = SettingsConfigDict(env_file=DOTENV_FILE)


@cache
def get_environment() -> Environment:
    return Environment()  # pyright: ignore[reportCallIssue] (Initialised by pydantic_settings)
