from __future__ import annotations

from datetime import datetime
from typing import Any

from src.ingestion.scenarios import build_scenario


def build_iam_attack_scenario(now: datetime | None = None) -> list[dict[str, Any]]:
    return build_scenario("full_incident", now=now).events
