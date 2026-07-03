from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV_FILE = ".env"


class Environment(BaseSettings):
    allow_origins: str
    allow_origin_regex: str
    fmp_api_key: str
    fmp_base_url: str

    model_config = SettingsConfigDict(env_file=DOTENV_FILE)
