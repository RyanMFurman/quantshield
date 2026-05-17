from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ResponseAction:
    action_type: str
    severity: str
    affected_user: str
    source_ip: str
    note: str


class IncidentResponder:
    """Minimal response hook for P1 alerts.

    This intentionally starts as a safe non-destructive implementation:
    we emit structured action records that can later map to Lambda/WAF/IAM calls.
    """

    def handle_alerts(self, alerts: list[dict[str, Any]]) -> list[ResponseAction]:
        actions: list[ResponseAction] = []

        for alert in alerts:
            severity = str(alert.get("severity") or "")
            if severity != "P1":
                continue

            affected_user = str(alert.get("affected_user") or "unknown")
            source_ip = str(alert.get("source_ip") or "unknown")
            rule_id = str(alert.get("rule_id") or "unknown")

            actions.append(
                ResponseAction(
                    action_type="create_incident_ticket",
                    severity=severity,
                    affected_user=affected_user,
                    source_ip=source_ip,
                    note=f"Escalate {rule_id} for analyst triage and containment.",
                )
            )

        return actions
