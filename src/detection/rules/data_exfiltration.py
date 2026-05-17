from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any


@dataclass(frozen=True)
class DataExfiltrationConfig:
    window_minutes: int = 15
    object_count_threshold: int = 20
    rule_id: str = "DATA_EXFIL_001"
    rule_name: str = "Potential Data Exfiltration via S3 Object Access"
    severity: str = "P1"
    mitre_tactic: str = "Exfiltration"
    mitre_technique: str = "T1567"


class DataExfiltrationRule:
    def __init__(self, config: DataExfiltrationConfig | None = None) -> None:
        self.config = config or DataExfiltrationConfig()

    def evaluate(
        self, events: list[dict[str, Any]], now: datetime | None = None
    ) -> list[dict[str, Any]]:
        current_time = now or datetime.now(timezone.utc)
        window_start = current_time - timedelta(minutes=self.config.window_minutes)

        download_counts: dict[tuple[str, str], int] = {}

        for event in events:
            if not self._is_recent_event(event, window_start):
                continue

            if str(event.get("event_type") or "") != "GetObject":
                continue

            username = str(event.get("username") or "unknown")
            source_ip = str(event.get("source_ip") or "unknown")
            key = (username, source_ip)
            download_counts[key] = download_counts.get(key, 0) + 1

        alerts: list[dict[str, Any]] = []

        for (username, source_ip), count in download_counts.items():
            if count < self.config.object_count_threshold:
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
                        f"{count} S3 GetObject requests detected for {username} from {source_ip} "
                        f"within {self.config.window_minutes} minutes"
                    ),
                    "triggered_at": current_time,
                    "status": "OPEN",
                }
            )

        return alerts

    @staticmethod
    def _is_recent_event(event: dict[str, Any], window_start: datetime) -> bool:
        occurred_at = event.get("occurred_at")
        if not isinstance(occurred_at, datetime):
            return False

        if occurred_at.tzinfo is None:
            occurred_at = occurred_at.replace(tzinfo=timezone.utc)

        return occurred_at >= window_start
