from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 应用配置
    app_name: str = "便签小程序"
    app_version: str = "1.0.0"

    # 数据库配置
    database_url: str = "sqlite+aiosqlite:///./data/notes.db"

    # JWT配置
    secret_key: str = "your-secret-key-please-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7

    # 服务器配置
    host: str = "127.0.0.1"
    port: int = 8000

    # 网页前端开关
    enable_web_frontend: bool = False

    # 注册配置
    registration_enabled: bool = True
    registration_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
