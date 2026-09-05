from functools import cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

"""Dependency injection as shown in https://fastapi.tiangolo.com/advanced/settings/"""


DOTENV_FILE: str = ".env"


class Environment(BaseSettings):
    """
    Excludes database settings.

    Load environment variables from the provided .env file case-insensitively.
    For example, ALLOW_ORIGINS is loaded into allow_origins.
    """

    # CORS
    allow_origins: str
    allow_origin_regex: str

    # FMP
    fmp_api_key: str
    fmp_base_url: str

    # Agent
    openrouter_api_key: str
    planning_node_model: str
    planning_node_provider: str

    model_config = SettingsConfigDict(env_file=DOTENV_FILE, extra="ignore")


@cache
def get_environment() -> Environment:
    return Environment()  # pyright: ignore[reportCallIssue] (Initialised by pydantic_settings)


class DatabaseSettings(BaseSettings):
    """The connection settings alone, kept apart from `Environment` so that the
    things which only talk to the database do not fail to start because an
    unrelated setting is missing."""

    host: str
    port: int
    name: str
    username: str
    password: str

    # `env_prefix` means the fields are read from `DATABASE_*` variables
    model_config = SettingsConfigDict(
        env_file=DOTENV_FILE, env_prefix="database_", extra="ignore"
    )

    @property
    def url(self) -> URL:
        """
        The connection URL, assembled from its parts.

        Built with `URL.create` rather than an f-string because RDS generates
        passwords containing punctuation. `URL.create` escapes each component.

        Returning the `URL` object keeps the password out of logs.
        """

        return URL.create(
            # https://docs.sqlalchemy.org/en/21/core/engines.html
            # https://github.com/magicstack/asyncpg
            drivername="postgresql+asyncpg",
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.name,
        )


@cache
def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings()  # pyright: ignore[reportCallIssue] (Initialised by pydantic_settings)
