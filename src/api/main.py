from __future__ import annotations

from fastapi import FastAPI, HTTPException

from src.api.config import get_settings
from src.api.database import DatabaseUnavailable, fetch_all
from src.api.schemas import (
    ActiveAlertsResponse,
    HealthResponse,
    MarketLatestResponse,
)

app = FastAPI(
    title="QuantShield API",
    version="0.1.0",
    description="Backend API for QuantShield security operations data.",
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
    )


@app.get("/market/latest", response_model=MarketLatestResponse, tags=["market"])
def latest_market_prices() -> MarketLatestResponse:
    query = """
        SELECT DISTINCT ON (symbol)
            symbol,
            price,
            volume,
            prev_close,
            captured_at
        FROM market_prices
        ORDER BY symbol, captured_at DESC
    """

    try:
        rows = fetch_all(query)
    except DatabaseUnavailable:
        return MarketLatestResponse(database_configured=False, items=[])
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to load latest market prices",
        ) from exc

    return MarketLatestResponse(database_configured=True, items=rows)


@app.get("/alerts/active", response_model=ActiveAlertsResponse, tags=["alerts"])
def active_alerts() -> ActiveAlertsResponse:
    query = """
        SELECT
            id,
            rule_id,
            rule_name,
            severity,
            mitre_tactic,
            mitre_technique,
            affected_user,
            source_ip::text AS source_ip,
            description,
            status,
            triggered_at
        FROM alerts
        WHERE status IN ('OPEN', 'ACK')
        ORDER BY triggered_at DESC
    """

    try:
        rows = fetch_all(query)
    except DatabaseUnavailable:
        return ActiveAlertsResponse(database_configured=False, items=[])
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to load active alerts",
        ) from exc

    return ActiveAlertsResponse(database_configured=True, items=rows)


@app.get("/api/v1/alerts/active", response_model=ActiveAlertsResponse, tags=["alerts"])
def active_alerts_v1() -> ActiveAlertsResponse:
    return active_alerts()
