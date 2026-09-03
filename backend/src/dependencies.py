from functools import cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

"""Dependency injection as shown in https://fastapi.tiangolo.com/advanced/settings/"""


DOTENV_FILE: str = ".env"


class Environment(BaseSettings):
    """
    Load environment variables from the provided .env file case-insensitively.
    The .env file must contain exactly the variables specified below.
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

    # Database
    database_host: str
    database_port: int
    database_name: str
    database_username: str
    database_password: str

    model_config = SettingsConfigDict(env_file=DOTENV_FILE)

    @property
    def database_url(self) -> URL:
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
            username=self.database_username,
            password=self.database_password,
            host=self.database_host,
            port=self.database_port,
            database=self.database_name,
        )


@cache
def get_environment() -> Environment:
    return Environment()  # pyright: ignore[reportCallIssue] (Initialised by pydantic_settings)
