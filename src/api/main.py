from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException

from src.api.config import get_settings
from src.api.database import DatabaseUnavailable, fetch_all
from src.api.schemas import (
    AccessAnalyzerResponse,
    ActiveAlertsResponse,
    AlertSummaryResponse,
    HealthResponse,
    InsiderRiskResponse,
    MarketLatestResponse,
    PermissionDriftResponse,
    SecurityEventsResponse,
)
from src.analysis.permission_drift import (
    build_usage_by_role,
    calculate_permission_drift,
    load_terraform_role_policies,
)
from src.ingestion.access_analyzer import list_access_analyzer_findings

app = FastAPI(
    title="QuantShield API",
    version="0.1.0",
    description="Backend API for QuantShield security operations data.",
)


@app.get("/", tags=["system"])
def root() -> dict[str, Any]:
    return {
        "service": "QuantShield API",
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
        "routes": [
            "/market/latest",
            "/alerts/active",
            "/api/v1/events/recent",
            "/api/v1/detections/summary",
            "/api/v1/insider-risk",
            "/api/v1/access-analyzer/findings",
            "/api/v1/permission-drift",
        ],
    }


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
            raw_payload ->> 'scenario' AS scenario,
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


@app.get("/api/v1/insider-risk", response_model=InsiderRiskResponse, tags=["risk"])
def insider_risk_findings(limit: int = 50) -> InsiderRiskResponse:
    safe_limit = max(1, min(limit, 200))
    query = """
        SELECT
            id,
            symbol,
            risk_score,
            severity,
            affected_user,
            source_ip::text AS source_ip,
            market_signal,
            related_event_count,
            reason,
            status,
            detected_at
        FROM insider_risk_findings
        WHERE status IN ('OPEN', 'ACK')
        ORDER BY detected_at DESC
        LIMIT %s
    """

    try:
        rows = fetch_all(query, (safe_limit,))
    except DatabaseUnavailable:
        return InsiderRiskResponse(database_configured=False, items=[])
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to load insider risk findings",
        ) from exc

    return InsiderRiskResponse(database_configured=True, items=rows)


@app.get("/api/v1/access-analyzer/findings", response_model=AccessAnalyzerResponse, tags=["iam"])
def access_analyzer_findings() -> AccessAnalyzerResponse:
    settings = get_settings()
    if not settings.access_analyzer_arn:
        return AccessAnalyzerResponse(aws_configured=False, items=[])

    try:
        findings = list_access_analyzer_findings(
            settings.access_analyzer_arn,
            region_name=settings.aws_region,
        )
    except Exception as exc:
        return AccessAnalyzerResponse(aws_configured=True, items=[], error=str(exc))

    return AccessAnalyzerResponse(aws_configured=True, items=findings)


@app.get("/api/v1/permission-drift", response_model=PermissionDriftResponse, tags=["iam"])
def permission_drift(limit: int = 500) -> PermissionDriftResponse:
    safe_limit = max(1, min(limit, 1000))
    query = """
        SELECT event_type, username, raw_payload
        FROM security_events
        ORDER BY occurred_at DESC
        LIMIT %s
    """

    try:
        rows = fetch_all(query, (safe_limit,))
    except DatabaseUnavailable:
        return PermissionDriftResponse(database_configured=False, items=[])
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to load permission drift") from exc

    role_policies = load_terraform_role_policies("terraform/modules/iam")
    usage_by_role = build_usage_by_role(rows)
    reports = calculate_permission_drift(role_policies, usage_by_role)

    return PermissionDriftResponse(
        database_configured=True,
        items=[report.__dict__ for report in reports],
    )
