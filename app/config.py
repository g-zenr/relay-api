from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "Relay API"
    app_version: str = "1.0.0"
    debug: bool = False

    mock: bool = False

    vendor_id: int = 0x16C0
    product_id: int = 0x05DF
    relay_channels: int = 2

    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = ["*"]

    api_key: str = ""
    rate_limit: int = 0
    pulse_ms: int = 0

    model_config = SettingsConfigDict(
        env_prefix="RELAY_",
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
