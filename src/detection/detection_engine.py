from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import psycopg

from src.detection.rules.brute_force import BruteForceRule
from src.detection.rules.privilege_escalation import PrivilegeEscalationRule


class DetectionEngine:
    def __init__(self) -> None:
        self.rules = [BruteForceRule(), PrivilegeEscalationRule()]

    def run(
        self,
        events: list[dict[str, Any]],
        existing_open_alerts: list[dict[str, Any]] | None = None,
        now: datetime | None = None,
    ) -> list[dict[str, Any]]:
        evaluation_time = now or datetime.now(timezone.utc)
        generated_alerts: list[dict[str, Any]] = []

        for rule in self.rules:
            generated_alerts.extend(rule.evaluate(events, now=evaluation_time))

        return self._deduplicate(generated_alerts, existing_open_alerts or [])

    def run_db_cycle(self, db_url: str | None = None, window_minutes: int = 15) -> dict[str, int]:
        resolved_db_url = db_url or os.getenv("DB_URL")
        if not resolved_db_url:
            raise ValueError("DB_URL is required for database detection runs")

        now = datetime.now(timezone.utc)
        since = now - timedelta(minutes=window_minutes)

        with psycopg.connect(resolved_db_url) as conn:
            with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
                events = self._fetch_recent_events(cur, since)
                existing_open_alerts = self._fetch_open_alerts(cur)
                new_alerts = self.run(events, existing_open_alerts=existing_open_alerts, now=now)

                inserted_count = 0
                if new_alerts:
                    inserted_count = self._insert_alerts(cur, new_alerts)

            conn.commit()

        return {
            "events_evaluated": len(events),
            "alerts_generated": len(new_alerts),
            "alerts_inserted": inserted_count,
        }

    @staticmethod
    def _fetch_recent_events(cur: Any, since: datetime) -> list[dict[str, Any]]:
        cur.execute(
            """
            SELECT event_type, source_ip::text, username, result, raw_payload, occurred_at
            FROM security_events
            WHERE occurred_at >= %s
            ORDER BY occurred_at DESC
            """,
            (since,),
        )
        return [dict(row) for row in cur.fetchall()]

    @staticmethod
    def _fetch_open_alerts(cur: Any) -> list[dict[str, Any]]:
        cur.execute(
            """
            SELECT rule_id, affected_user, source_ip::text, status
            FROM alerts
            WHERE status = 'OPEN'
            """
        )
        return [dict(row) for row in cur.fetchall()]

    @staticmethod
    def _insert_alerts(cur: Any, alerts: list[dict[str, Any]]) -> int:
        payload = [
            (
                alert["rule_id"],
                alert["rule_name"],
                alert["severity"],
                alert.get("mitre_tactic"),
                alert.get("mitre_technique"),
                alert.get("affected_user"),
                alert.get("source_ip"),
                alert.get("description"),
                alert.get("status", "OPEN"),
                alert.get("triggered_at", datetime.now(timezone.utc)),
            )
            for alert in alerts
        ]

        cur.executemany(
            """
            INSERT INTO alerts (
                rule_id, rule_name, severity, mitre_tactic, mitre_technique,
                affected_user, source_ip, description, status, triggered_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            payload,
        )
        return len(payload)

    def _deduplicate(
        self,
        new_alerts: list[dict[str, Any]],
        existing_open_alerts: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        existing_keys = {
            self._alert_key(alert)
            for alert in existing_open_alerts
            if alert.get("status") == "OPEN"
        }

        deduped_alerts: list[dict[str, Any]] = []
        seen_new_keys: set[tuple[str, str, str]] = set()

        for alert in new_alerts:
            key = self._alert_key(alert)

            if key in existing_keys:
                continue

            if key in seen_new_keys:
                continue

            seen_new_keys.add(key)
            deduped_alerts.append(alert)

        return deduped_alerts

    @staticmethod
    def _alert_key(alert: dict[str, Any]) -> tuple[str, str, str]:
        rule_id = str(alert.get("rule_id") or "")
        affected_user = str(alert.get("affected_user") or "unknown")
        source_ip = str(alert.get("source_ip") or "unknown")
        return (rule_id, affected_user, source_ip)


def run_detection(
    events: list[dict[str, Any]],
    existing_open_alerts: list[dict[str, Any]] | None = None,
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    engine = DetectionEngine()
    return engine.run(events, existing_open_alerts=existing_open_alerts, now=now)


def handler(event: dict[str, Any], context: Any) -> dict[str, int]:
    _ = (event, context)
    engine = DetectionEngine()
    return engine.run_db_cycle()
