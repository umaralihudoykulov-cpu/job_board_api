from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Primary env-backed settings (use uppercase names to match .env)
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Application metadata (provide sensible defaults, can be overridden by env)
    project_name: str = Field("Job Board API", env="PROJECT_NAME")
    project_version: str = Field("0.1.0", env="PROJECT_VERSION")
    debug: bool = Field(False, env="DEBUG")

    # CORS origins: either a comma-separated env var CORS_ORIGINS or default to allow-all
    cors_origins_list: List[str] = Field(default_factory=lambda: ["*"])  # can be overridden by CORS_ORIGINS

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Compatibility properties for code that expects different attribute names
    @property
    def database_url(self) -> str:
        return self.DATABASE_URL

    @property
    def jwt_secret_key(self) -> str:
        return self.SECRET_KEY

    @property
    def jwt_algorithm(self) -> str:
        return self.ALGORITHM

    @property
    def access_token_expire_minutes(self) -> int:
        return self.ACCESS_TOKEN_EXPIRE_MINUTES

    @property
    def refresh_token_expire_days(self) -> int:
        return self.REFRESH_TOKEN_EXPIRE_DAYS


settings = Settings()