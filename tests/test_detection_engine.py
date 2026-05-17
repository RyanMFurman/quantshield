from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from src.detection.detection_engine import DetectionEngine, run_detection
from src.response.incident_responder import IncidentResponder


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
    assert any(alert["rule_id"] == "BRUTE_FORCE_001" for alert in alerts)


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
    assert any(alert["rule_id"] == "PRIV_ESC_001" for alert in alerts)


def test_lateral_movement_alert_fires() -> None:
    now = datetime.now(timezone.utc)
    events = [
        {
            "event_type": "AssumeRole",
            "result": "Success",
            "username": "analyst01",
            "source_ip": "203.0.113.10",
            "occurred_at": now - timedelta(minutes=2),
        },
        {
            "event_type": "AssumeRole",
            "result": "Success",
            "username": "analyst01",
            "source_ip": "203.0.113.11",
            "occurred_at": now - timedelta(minutes=3),
        },
        {
            "event_type": "ConsoleLogin",
            "result": "Success",
            "username": "analyst01",
            "source_ip": "203.0.113.12",
            "occurred_at": now - timedelta(minutes=4),
        },
    ]

    alerts = run_detection(events)
    assert any(alert["rule_id"] == "LATERAL_MOVE_001" for alert in alerts)


def test_data_exfiltration_alert_fires() -> None:
    now = datetime.now(timezone.utc)
    events = []
    for i in range(21):
        events.append(
            {
                "event_type": "GetObject",
                "result": "Success",
                "username": "data-user",
                "source_ip": "198.51.100.200",
                "occurred_at": now - timedelta(minutes=1, seconds=i),
            }
        )

    alerts = run_detection(events)
    assert any(alert["rule_id"] == "DATA_EXFIL_001" for alert in alerts)


def test_incident_responder_only_handles_p1_alerts() -> None:
    responder = IncidentResponder()
    actions = responder.handle_alerts(
        [
            {"rule_id": "X", "severity": "P1", "affected_user": "u", "source_ip": "1.1.1.1"},
            {"rule_id": "Y", "severity": "P2", "affected_user": "u", "source_ip": "1.1.1.2"},
        ]
    )
    assert len(actions) == 1
    assert actions[0].action_type == "create_incident_ticket"


class FakeCursor:
    def __init__(self) -> None:
        self.last_query = ""
        self.inserted_rows = 0

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        _ = (exc_type, exc, tb)

    def execute(self, query: str, params: tuple[object, ...] | None = None) -> None:
        _ = params
        self.last_query = query

    def executemany(self, query: str, params: list[tuple[object, ...]]) -> None:
        self.last_query = query
        self.inserted_rows += len(params)

    def fetchall(self) -> list[dict[str, object]]:
        if "FROM security_events" in self.last_query:
            now = datetime.now(timezone.utc)
            return [
                {
                    "event_type": "ConsoleLogin",
                    "source_ip": "198.51.100.10",
                    "username": "trading-svc",
                    "result": "Failure",
                    "raw_payload": {},
                    "occurred_at": now - timedelta(minutes=1),
                }
                for _ in range(6)
            ]
        if "FROM alerts" in self.last_query:
            return []
        return []


class FakeConnection:
    def __init__(self) -> None:
        self.cursor_obj = FakeCursor()
        self.committed = False

    def __enter__(self) -> "FakeConnection":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        _ = (exc_type, exc, tb)

    def cursor(self, row_factory: object | None = None) -> FakeCursor:
        _ = row_factory
        return self.cursor_obj

    def commit(self) -> None:
        self.committed = True


def test_run_db_cycle_with_mocked_connection() -> None:
    engine = DetectionEngine()
    fake_conn = FakeConnection()

    with patch("src.detection.detection_engine.psycopg.connect", return_value=fake_conn):
        result = engine.run_db_cycle(db_url="postgresql://placeholder")

    assert result["events_evaluated"] == 6
    assert result["alerts_generated"] >= 1
    assert result["alerts_inserted"] >= 1
    assert fake_conn.committed is True
