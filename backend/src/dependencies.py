from functools import cache
from typing import Literal, Self

from pydantic import model_validator
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

    # The owner for migrations
    username: str
    password: str

    # The role the application connects as
    app_username: str

    # Unset under `iam`, where there is no password to hold. Optional rather
    # than absent so that local development, which has no IAM, still works.
    app_password: str | None = None

    auth: Literal["password", "iam"] = "password"

    # Needed to sign an IAM token. boto3 would fall back to AWS_REGION in the
    # task environment, but a missing region surfaces there as an obscure
    # NoRegionError at the first connection rather than at startup.
    region: str | None = None

    # `env_prefix` means the fields are read from `DATABASE_*` variables
    model_config = SettingsConfigDict(
        env_file=DOTENV_FILE, env_prefix="database_", extra="ignore"
    )

    @model_validator(mode="after")
    def check_credentials_match_auth(self) -> Self:

        if self.auth == "password" and self.app_password is None:
            raise ValueError(
                "DATABASE_APP_PASSWORD is required when DATABASE_AUTH=password"
            )

        if self.auth == "iam" and self.region is None:
            raise ValueError("DATABASE_REGION is required when DATABASE_AUTH=iam")

        return self

    def _url(self, username: str, password: str | None) -> URL:
        """
        A connection URL, assembled from its parts.

        Built with `URL.create` rather than an f-string because RDS generates
        passwords containing punctuation. `URL.create` escapes each component.

        Returning the `URL` object keeps the password out of logs.
        """

        return URL.create(
            # https://docs.sqlalchemy.org/en/21/core/engines.html
            # https://github.com/magicstack/asyncpg
            drivername="postgresql+asyncpg",
            username=username,
            password=password,
            host=self.host,
            port=self.port,
            database=self.name,
        )

    @property
    def owner_url(self) -> URL:
        """For migrations only"""

        return self._url(self.username, self.password)

    @property
    def application_url(self) -> URL:
        """
        For everything that serves a request.

        Under `iam` the password is deliberately absent: an IAM token lasts
        fifteen minutes and is only checked when a connection is opened, so it
        cannot be baked into a URL the engine holds for its lifetime. The engine
        mints one per connection instead.
        """

        return self._url(
            self.app_username, self.app_password if self.auth == "password" else None
        )


@cache
def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings()  # pyright: ignore[reportCallIssue] (Initialised by pydantic_settings)
