from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Stock Workbench"
    app_env: str = "development"
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    tushare_token: str | None = None
    polygon_api_key: str | None = None
    alpha_vantage_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
