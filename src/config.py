from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, RedisDsn


class Config(BaseSettings):
    APP_NAME: str = 'IBAN Validator'
    DEBUG: bool = False
    DB_URI: PostgresDsn
    REDIS_URI: RedisDsn
    TESTING: bool = False

    model_config = SettingsConfigDict(env_file='.env')


config = Config()
