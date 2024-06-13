import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

ENV_PATH = os.path.expanduser(".env")


class Settings(BaseSettings):
    admins: list[int] = [] 
    admin_chat: int
    token: SecretStr
    days: list[str]
    timetable_file: str
    database_url: str

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8"
    )


config = Settings()