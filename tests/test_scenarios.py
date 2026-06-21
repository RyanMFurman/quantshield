from __future__ import annotations

from datetime import datetime, timezone

from src.detection.detection_engine import run_detection
from src.ingestion.scenarios import build_scenario, scenario_names


def test_scenario_names_are_available() -> None:
    assert scenario_names() == ["full_incident", "noisy_benign", "p2_only", "quiet_day"]


def test_quiet_day_generates_no_alerts() -> None:
    now = datetime.now(timezone.utc)
    scenario = build_scenario("quiet_day", now=now)

    assert scenario.events
    assert run_detection(scenario.events, now=now) == []


def test_noisy_benign_generates_no_alerts() -> None:
    now = datetime.now(timezone.utc)
    scenario = build_scenario("noisy_benign", now=now)

    assert len(scenario.events) >= 20
    assert run_detection(scenario.events, now=now) == []


def test_p2_only_generates_no_p1_alerts() -> None:
    now = datetime.now(timezone.utc)
    scenario = build_scenario("p2_only", now=now)
    alerts = run_detection(scenario.events, now=now)

    assert alerts
    assert {alert["severity"] for alert in alerts} == {"P2"}


def test_full_incident_generates_p1_alerts() -> None:
    now = datetime.now(timezone.utc)
    scenario = build_scenario("full_incident", now=now)
    alerts = run_detection(scenario.events, now=now)

    assert any(alert["severity"] == "P1" for alert in alerts)
    assert any(alert["rule_id"] == "IAM_ROOT_LOGIN_001" for alert in alerts)
    assert any(alert["rule_id"] == "DATA_EXFIL_001" for alert in alerts)
