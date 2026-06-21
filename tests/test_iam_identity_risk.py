from __future__ import annotations

from datetime import datetime, timedelta, timezone

from src.detection.detection_engine import run_detection
from src.ingestion.cloudtrail_simulator import build_iam_attack_scenario


def test_iam_attack_scenario_generates_identity_alerts() -> None:
    now = datetime.now(timezone.utc)
    events = build_iam_attack_scenario(now)

    alerts = run_detection(events, now=now)

    iam_alerts = [alert for alert in alerts if alert["rule_id"].startswith("IAM_")]
    assert len(iam_alerts) >= 4
    assert any("Access key created" in alert["description"] for alert in iam_alerts)
    assert any("MFA was disabled" in alert["description"] for alert in iam_alerts)
    assert any("Root account console login" in alert["description"] for alert in iam_alerts)
    assert any(alert["severity"] == "P1" for alert in iam_alerts)


def test_iam_rule_ignores_old_identity_events() -> None:
    now = datetime.now(timezone.utc)
    events = [
        {
            "event_type": "CreateAccessKey",
            "source_ip": "203.0.113.44",
            "username": "quant-analyst",
            "result": "Success",
            "raw_payload": {"target_user": "quant-analyst"},
            "occurred_at": now - timedelta(hours=2),
        }
    ]

    alerts = run_detection(events, now=now)

    assert [alert for alert in alerts if alert["rule_id"].startswith("IAM_")] == []
