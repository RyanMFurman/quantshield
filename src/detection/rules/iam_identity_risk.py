from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any


@dataclass(frozen=True)
class IamIdentityRiskConfig:
    window_minutes: int = 60
    rule_id: str = "IAM_RISK_001"
    rule_name: str = "High-Risk IAM Identity Activity"
    mitre_tactic: str = "Privilege Escalation"
    mitre_technique: str = "T1098"


class IamIdentityRiskRule:
    def __init__(self, config: IamIdentityRiskConfig | None = None) -> None:
        self.config = config or IamIdentityRiskConfig()

    def evaluate(
        self, events: list[dict[str, Any]], now: datetime | None = None
    ) -> list[dict[str, Any]]:
        current_time = now or datetime.now(timezone.utc)
        window_start = current_time - timedelta(minutes=self.config.window_minutes)
        alerts: list[dict[str, Any]] = []

        for event in events:
            if not self._is_recent_event(event, window_start):
                continue

            finding = self._classify_event(event)
            if finding is None:
                continue

            username = self._principal(event)
            source_ip = str(event.get("source_ip") or "unknown")

            alerts.append(
                {
                    "rule_id": finding["rule_id"],
                    "rule_name": finding["rule_name"],
                    "severity": finding["severity"],
                    "mitre_tactic": self.config.mitre_tactic,
                    "mitre_technique": self.config.mitre_technique,
                    "affected_user": username,
                    "source_ip": source_ip,
                    "description": finding["description"],
                    "triggered_at": current_time,
                    "status": "OPEN",
                }
            )

        return alerts

    def _classify_event(self, event: dict[str, Any]) -> dict[str, str] | None:
        event_type = str(event.get("event_type") or "")
        payload = event.get("raw_payload")
        payload_dict = payload if isinstance(payload, dict) else {}
        username = self._principal(event)
        source_ip = str(event.get("source_ip") or "unknown")

        if event_type == "ConsoleLogin" and username == "root":
            return {
                "rule_id": "IAM_ROOT_LOGIN_001",
                "rule_name": "Root Account Console Login",
                "severity": "P1",
                "description": f"Root account console login observed from {source_ip}",
            }

        if event_type == "DeactivateMFADevice":
            return {
                "rule_id": "IAM_MFA_DISABLED_001",
                "rule_name": "MFA Device Disabled",
                "severity": "P1",
                "description": f"MFA was disabled for {username} from {source_ip}",
            }

        if event_type == "CreateAccessKey":
            target_user = str(payload_dict.get("target_user") or username)
            return {
                "rule_id": "IAM_ACCESS_KEY_001",
                "rule_name": "Access Key Created",
                "severity": "P2",
                "description": f"Access key created for {target_user} by {username} from {source_ip}",
            }

        if event_type in {"AttachUserPolicy", "AttachRolePolicy", "PutUserPolicy"}:
            policy_name = str(payload_dict.get("policy") or payload_dict.get("policy_name") or "")
            if "AdministratorAccess" in policy_name or "Admin" in policy_name:
                return {
                    "rule_id": "IAM_ADMIN_POLICY_001",
                    "rule_name": "Administrative Policy Change",
                    "severity": "P1",
                    "description": (
                        f"Administrative policy {policy_name or 'unknown'} attached or "
                        f"modified by {username} from {source_ip}"
                    ),
                }

        if event_type == "AssumeRole":
            role_name = str(payload_dict.get("role") or payload_dict.get("role_name") or "")
            if "Admin" in role_name or "BreakGlass" in role_name or "TradingProd" in role_name:
                return {
                    "rule_id": "IAM_PRIV_ROLE_001",
                    "rule_name": "Privileged Role Assumption",
                    "severity": "P2",
                    "description": f"{username} assumed privileged role {role_name} from {source_ip}",
                }

        return None

    @staticmethod
    def _is_recent_event(event: dict[str, Any], window_start: datetime) -> bool:
        occurred_at = event.get("occurred_at")
        if not isinstance(occurred_at, datetime):
            return False

        if occurred_at.tzinfo is None:
            occurred_at = occurred_at.replace(tzinfo=timezone.utc)

        return occurred_at >= window_start

    @staticmethod
    def _principal(event: dict[str, Any]) -> str:
        payload = event.get("raw_payload")
        if isinstance(payload, dict):
            principal = payload.get("principal") or payload.get("user_identity")
            if principal:
                return str(principal)

        return str(event.get("username") or "unknown")
