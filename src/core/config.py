import os

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, '.env')


class AppSettings(BaseSettings):
    app_title: str = 'Base Title'
    project_host: str = 'localhost'
    project_port: int = 8000
    database_dsn: PostgresDsn
    url_aws: str
    bucket_name: str
    debug: bool = False

    model_config = SettingsConfigDict(env_file=ENV_PATH)


settings = AppSettings()
