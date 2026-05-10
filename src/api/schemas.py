from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class MarketPrice(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    price: Decimal
    volume: int | None = None
    prev_close: Decimal | None = None
    captured_at: datetime


class MarketLatestResponse(BaseModel):
    database_configured: bool
    items: list[MarketPrice]


class Alert(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rule_id: str
    rule_name: str
    severity: str
    mitre_tactic: str | None = None
    mitre_technique: str | None = None
    affected_user: str | None = None
    source_ip: str | None = None
    description: str | None = None
    status: str
    triggered_at: datetime


class ActiveAlertsResponse(BaseModel):
    database_configured: bool
    items: list[Alert]
