from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379"
    rate_limit_requests: int = 10
    rate_limit_window_seconds: int = 60
    database_url: str = "None"
    app_name: str = "SupportPilot"
    app_version: str = "0.1.0"
    environment: str = "development"
    jwt_secret_key: str = "your_secret_key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
