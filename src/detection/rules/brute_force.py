from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any


# Tunable rule parameters
@dataclass(frozen=True)
class BruteForceConfig:
    window_minutes: int = 15
    failure_threshold: int = 5
    rule_id: str = "BRUTE_FORCE_001"
    rule_name: str = "Repeated Console Login Failures"
    severity: str = "P2"
    mitre_tactic: str = "Credential Access"
    mitre_technique: str = "T1110"


class BruteForceRule:
    def __init__(self, config: BruteForceConfig | None = None) -> None:
        self.config = config or BruteForceConfig()

    def evaluate(
        self, events: list[dict[str, Any]], now: datetime | None = None
    ) -> list[dict[str, Any]]:
        current_time = now or datetime.now(timezone.utc)
        window_start = current_time - timedelta(minutes=self.config.window_minutes)

        grouped_failures: dict[tuple[str, str], int] = {}

        # Filter + aggregate failures by user/ip within window
        for event in events:
            if event.get("event_type") != "ConsoleLogin":
                continue

            if event.get("result") != "Failure":
                continue

            occurred_at = event.get("occurred_at")
            if not isinstance(occurred_at, datetime):
                continue

            if occurred_at.tzinfo is None:
                occurred_at = occurred_at.replace(tzinfo=timezone.utc)

            if occurred_at < window_start:
                continue

            username = str(event.get("username") or "unknown")
            source_ip = str(event.get("source_ip") or "unknown")

            key = (username, source_ip)
            grouped_failures[key] = grouped_failures.get(key, 0) + 1

        alerts: list[dict[str, Any]] = []

        # Convert threshold hits into normalized alert objects
        for (username, source_ip), failure_count in grouped_failures.items():
            if failure_count < self.config.failure_threshold:
                continue

            alerts.append(
                {
                    "rule_id": self.config.rule_id,
                    "rule_name": self.config.rule_name,
                    "severity": self.config.severity,
                    "mitre_tactic": self.config.mitre_tactic,
                    "mitre_technique": self.config.mitre_technique,
                    "affected_user": username,
                    "source_ip": source_ip,
                    "description": (
                        f"{failure_count} failed ConsoleLogin events for user "
                        f"{username} from {source_ip} in the last "
                        f"{self.config.window_minutes} minutes"
                    ),
                    "triggered_at": current_time,
                    "status": "OPEN",
                }
            )

        return alerts
