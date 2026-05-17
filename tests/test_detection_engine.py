from __future__ import annotations

from datetime import datetime, timedelta, timezone

from src.detection.detection_engine import run_detection


def build_failure_events(count: int) -> list[dict[str, object]]:
    now = datetime.now(timezone.utc)
    events: list[dict[str, object]] = []

    for i in range(count):
        events.append(
            {
                "event_type": "ConsoleLogin",
                "result": "Failure",
                "username": "trading-svc",
                "source_ip": "198.51.100.10",
                "occurred_at": now - timedelta(minutes=i + 1),
            }
        )

    return events


def test_brute_force_threshold_met() -> None:
    alerts = run_detection(build_failure_events(6))
    assert len(alerts) == 1
    assert alerts[0]["rule_id"] == "BRUTE_FORCE_001"


def test_brute_force_threshold_not_met() -> None:
    alerts = run_detection(build_failure_events(4))
    assert len(alerts) == 0


def test_dedup_existing_open_alert() -> None:
    existing = [
        {
            "rule_id": "BRUTE_FORCE_001",
            "affected_user": "trading-svc",
            "source_ip": "198.51.100.10",
            "status": "OPEN",
        }
    ]

    alerts = run_detection(build_failure_events(6), existing_open_alerts=existing)
    assert len(alerts) == 0


def test_privilege_escalation_alert_fires() -> None:
    now = datetime.now(timezone.utc)
    events = [
        {
            "event_type": "AttachRolePolicy",
            "result": "Success",
            "username": "api-user",
            "source_ip": "203.0.113.25",
            "occurred_at": now - timedelta(minutes=2),
            "raw_payload": {"policy": "AdministratorAccess"},
        }
    ]

    alerts = run_detection(events)
    assert len(alerts) == 1
    assert alerts[0]["rule_id"] == "PRIV_ESC_001"
