from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    APP_NAME: str = 'IBAN Validator'
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file='.env')


config = Config()
