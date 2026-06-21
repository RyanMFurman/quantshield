from __future__ import annotations

from functools import lru_cache
from os import getenv


class Settings:
    """Runtime settings loaded from environment variables."""

    app_name: str = "QuantShield API"
    app_version: str = "0.1.0"
    database_url: str | None
    access_analyzer_arn: str | None
    aws_region: str | None

    def __init__(self) -> None:
        self.database_url = getenv("DATABASE_URL")
        self.access_analyzer_arn = getenv("ACCESS_ANALYZER_ARN")
        self.aws_region = getenv("AWS_REGION")


@lru_cache
def get_settings() -> Settings:
    return Settings()
