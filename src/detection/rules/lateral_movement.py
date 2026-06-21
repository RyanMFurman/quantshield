from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any


@dataclass(frozen=True)
class LateralMovementConfig:
    window_minutes: int = 20
    distinct_ip_threshold: int = 3
    rule_id: str = "LATERAL_MOVE_001"
    rule_name: str = "Potential Lateral Movement via Multi-Host Access"
    severity: str = "P2"
    mitre_tactic: str = "Lateral Movement"
    # This cloud scenario is identity/role reuse across locations, not remote-service execution.
    # Valid Accounts: Cloud Accounts is more defensible than T1021 for AWS role hopping.
    mitre_technique: str = "T1078.004"


class LateralMovementRule:
    def __init__(self, config: LateralMovementConfig | None = None) -> None:
        self.config = config or LateralMovementConfig()

    def evaluate(
        self, events: list[dict[str, Any]], now: datetime | None = None
    ) -> list[dict[str, Any]]:
        current_time = now or datetime.now(timezone.utc)
        window_start = current_time - timedelta(minutes=self.config.window_minutes)

        user_ip_map: dict[str, set[str]] = {}

        for event in events:
            if not self._is_recent_event(event, window_start):
                continue

            event_type = str(event.get("event_type") or "")
            if event_type not in {"AssumeRole", "ConsoleLogin", "SSMStartSession"}:
                continue

            result = str(event.get("result") or "")
            if result and result != "Success":
                continue

            username = str(event.get("username") or "unknown")
            source_ip = str(event.get("source_ip") or "unknown")
            user_ip_map.setdefault(username, set()).add(source_ip)

        alerts: list[dict[str, Any]] = []

        for username, unique_ips in user_ip_map.items():
            if len(unique_ips) < self.config.distinct_ip_threshold:
                continue

            sorted_ips = sorted(unique_ips)
            alerts.append(
                {
                    "rule_id": self.config.rule_id,
                    "rule_name": self.config.rule_name,
                    "severity": self.config.severity,
                    "mitre_tactic": self.config.mitre_tactic,
                    "mitre_technique": self.config.mitre_technique,
                    "affected_user": username,
                    "source_ip": sorted_ips[0],
                    "description": (
                        f"User {username} accessed from {len(unique_ips)} unique source IPs "
                        f"within {self.config.window_minutes} minutes: {', '.join(sorted_ips)}"
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
