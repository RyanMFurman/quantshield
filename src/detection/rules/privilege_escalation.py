from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any


@dataclass(frozen=True)
class PrivilegeEscalationConfig:
    window_minutes: int = 15
    rule_id: str = "PRIV_ESC_001"
    rule_name: str = "Suspicious IAM Privilege Escalation"
    severity: str = "P1"
    mitre_tactic: str = "Privilege Escalation"
    mitre_technique: str = "T1078.004"


class PrivilegeEscalationRule:
    def __init__(self, config: PrivilegeEscalationConfig | None = None) -> None:
        self.config = config or PrivilegeEscalationConfig()

    def evaluate(
        self, events: list[dict[str, Any]], now: datetime | None = None
    ) -> list[dict[str, Any]]:
        current_time = now or datetime.now(timezone.utc)
        window_start = current_time - timedelta(minutes=self.config.window_minutes)
        alerts: list[dict[str, Any]] = []

        for event in events:
            if not self._is_recent_event(event, window_start):
                continue

            event_type = str(event.get("event_type") or "")
            if event_type not in {"AttachRolePolicy", "PutUserPolicy", "CreatePolicyVersion"}:
                continue

            policy_name = self._extract_policy_name(event)
            if policy_name != "AdministratorAccess":
                continue

            username = str(event.get("username") or "unknown")
            source_ip = str(event.get("source_ip") or "unknown")

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
                        f"{event_type} granted {policy_name} for user {username} "
                        f"from source IP {source_ip}"
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

    @staticmethod
    def _extract_policy_name(event: dict[str, Any]) -> str:
        payload = event.get("raw_payload")
        if isinstance(payload, dict):
            return str(payload.get("policy") or "")

        policy_field = event.get("policy")
        return str(policy_field or "")
