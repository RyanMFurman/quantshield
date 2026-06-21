from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid5


NAMESPACE = UUID("12345678-1234-5678-1234-567812345678")


@dataclass(frozen=True)
class DetectionScenario:
    name: str
    description: str
    events: list[dict[str, Any]]


SCENARIO_DESCRIPTIONS = {
    "quiet_day": "Normal low-volume IAM and S3 telemetry. Expected detection result: zero alerts.",
    "noisy_benign": "High-volume legitimate activity from expected locations. Expected detection result: zero alerts.",
    "p2_only": "Lower-severity identity activity without P1 conditions.",
    "full_incident": "Worst-case IAM incident path with root login, MFA disablement, admin policy change, and data access.",
}


def scenario_names() -> list[str]:
    return sorted(SCENARIO_DESCRIPTIONS)


def build_scenario(name: str = "quiet_day", now: datetime | None = None) -> DetectionScenario:
    current_time = now or datetime.now(timezone.utc)
    normalized_name = name.strip().lower().replace("-", "_")

    if normalized_name == "quiet_day":
        rows = _quiet_day()
    elif normalized_name == "noisy_benign":
        rows = _noisy_benign()
    elif normalized_name == "p2_only":
        rows = _p2_only()
    elif normalized_name == "full_incident":
        rows = _full_incident()
    else:
        raise ValueError(f"Unknown scenario '{name}'. Valid scenarios: {', '.join(scenario_names())}")

    return DetectionScenario(
        name=normalized_name,
        description=SCENARIO_DESCRIPTIONS[normalized_name],
        events=[_event(current_time, normalized_name, index, row) for index, row in enumerate(rows, start=1)],
    )


def _event(
    current_time: datetime,
    scenario_name: str,
    index: int,
    row: tuple[str, str, str, str, dict[str, Any], int],
) -> dict[str, Any]:
    event_type, source_ip, username, result, raw_payload, minutes_ago = row
    payload = {"scenario": scenario_name, **raw_payload}
    occurred_at = current_time - timedelta(minutes=minutes_ago)
    event_key = f"{scenario_name}:{index}:{event_type}:{username}:{source_ip}:{minutes_ago}"

    return {
        "event_id": str(uuid5(NAMESPACE, event_key)),
        "event_type": event_type,
        "source_ip": source_ip,
        "username": username,
        "user_agent": "cloudtrail-simulator/1.0",
        "result": result,
        "raw_payload": payload,
        "occurred_at": occurred_at,
    }


def _quiet_day() -> list[tuple[str, str, str, str, dict[str, Any], int]]:
    return [
        ("ConsoleLogin", "203.0.113.20", "research-analyst", "Success", {"mfa": True, "principal": "research-analyst"}, 12),
        ("AssumeRole", "203.0.113.20", "research-analyst", "Success", {"role": "ResearchReadOnlyRole", "principal": "research-analyst"}, 9),
        ("GetObject", "203.0.113.20", "research-analyst", "Success", {"bucket": "quant-research", "object": "daily-summary.csv"}, 6),
    ]


def _noisy_benign() -> list[tuple[str, str, str, str, dict[str, Any], int]]:
    rows: list[tuple[str, str, str, str, dict[str, Any], int]] = []
    for index in range(18):
        rows.append(
            (
                "ConsoleLogin",
                "203.0.113.20",
                "research-analyst",
                "Success",
                {"mfa": True, "principal": "research-analyst", "batch": "normal-logins"},
                index % 14 + 1,
            )
        )
    for index in range(12):
        rows.append(
            (
                "GetObject",
                "203.0.113.20",
                "research-analyst",
                "Success",
                {"bucket": "quant-research", "object": f"daily-factor-{index}.csv"},
                index % 14 + 1,
            )
        )
    return rows


def _p2_only() -> list[tuple[str, str, str, str, dict[str, Any], int]]:
    return [
        ("ConsoleLogin", "203.0.113.44", "quant-analyst", "Success", {"mfa": True, "principal": "quant-analyst"}, 12),
        ("AssumeRole", "203.0.113.44", "quant-analyst", "Success", {"role": "TradingProdAdminRole", "principal": "quant-analyst"}, 8),
        ("GetObject", "203.0.113.44", "quant-analyst", "Success", {"bucket": "quant-research", "object": "risk-model.csv"}, 4),
    ]


def _full_incident() -> list[tuple[str, str, str, str, dict[str, Any], int]]:
    rows: list[tuple[str, str, str, str, dict[str, Any], int]] = [
        ("ConsoleLogin", "203.0.113.44", "quant-analyst", "Success", {"mfa": False, "principal": "quant-analyst"}, 12),
        ("CreateAccessKey", "203.0.113.44", "quant-analyst", "Success", {"target_user": "quant-analyst", "principal": "quant-analyst"}, 10),
        ("AssumeRole", "203.0.113.44", "quant-analyst", "Success", {"role": "TradingProdAdminRole", "principal": "quant-analyst"}, 8),
        ("AttachUserPolicy", "203.0.113.44", "quant-analyst", "Success", {"policy": "AdministratorAccess", "target_user": "quant-analyst", "principal": "quant-analyst"}, 6),
        ("GetObject", "203.0.113.44", "quant-analyst", "Success", {"bucket": "quant-research", "object": "nvda-alpha-model.ipynb", "symbol": "NVDA", "principal": "quant-analyst"}, 4),
        ("DeactivateMFADevice", "203.0.113.44", "quant-analyst", "Success", {"target_user": "quant-analyst", "principal": "quant-analyst"}, 3),
        ("ConsoleLogin", "198.51.100.200", "root", "Success", {"principal": "root", "mfa": False}, 2),
    ]

    for minutes_ago in [1, 2, 3, 4, 5, 6]:
        rows.append(("ConsoleLogin", "198.51.100.10", "trading-svc", "Failure", {"count": minutes_ago, "symbol": "NVDA"}, minutes_ago))

    for index in range(21):
        rows.append(
            (
                "GetObject",
                "198.51.100.10",
                "trading-svc",
                "Success",
                {"bucket": "quant-research", "object": f"nvda-model-inputs-{index}.csv", "symbol": "NVDA"},
                index % 10 + 1,
            )
        )

    return rows
