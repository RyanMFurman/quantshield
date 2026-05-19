from __future__ import annotations

from fastapi import FastAPI, HTTPException

from src.api.config import get_settings
from src.api.database import DatabaseUnavailable, fetch_all
from src.api.schemas import (
    ActiveAlertsResponse,
    AlertSummaryResponse,
    HealthResponse,
    MarketLatestResponse,
    SecurityEventsResponse,
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


@app.get("/api/v1/events/recent", response_model=SecurityEventsResponse, tags=["events"])
def recent_security_events(limit: int = 100) -> SecurityEventsResponse:
    safe_limit = max(1, min(limit, 500))
    query = """
        SELECT
            event_type,
            source_ip::text AS source_ip,
            username,
            result,
            occurred_at
        FROM security_events
        ORDER BY occurred_at DESC
        LIMIT %s
    """

    try:
        rows = fetch_all(query, (safe_limit,))
    except DatabaseUnavailable:
        return SecurityEventsResponse(database_configured=False, items=[])
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to load recent security events",
        ) from exc

    return SecurityEventsResponse(database_configured=True, items=rows)


@app.get("/api/v1/detections/summary", response_model=AlertSummaryResponse, tags=["detections"])
def detection_summary() -> AlertSummaryResponse:
    query = """
        SELECT
            rule_id,
            severity,
            COUNT(*)::int AS open_count
        FROM alerts
        WHERE status = 'OPEN'
        GROUP BY rule_id, severity
        ORDER BY severity, open_count DESC
    """

    try:
        rows = fetch_all(query)
    except DatabaseUnavailable:
        return AlertSummaryResponse(database_configured=False, items=[])
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to load detection summary",
        ) from exc

    return AlertSummaryResponse(database_configured=True, items=rows)
