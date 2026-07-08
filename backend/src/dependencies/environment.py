from pydantic_settings import BaseSettings, SettingsConfigDict

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
