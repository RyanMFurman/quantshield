from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid5


NAMESPACE = UUID("12345678-1234-5678-1234-567812345678")


def build_iam_attack_scenario(now: datetime | None = None) -> list[dict[str, Any]]:
    current_time = now or datetime.now(timezone.utc)
    scenario = [
        (
            "ConsoleLogin",
            "203.0.113.44",
            "quant-analyst",
            "Success",
            {"mfa": False, "principal": "quant-analyst", "scenario": "iam-attack"},
            12,
        ),
        (
            "CreateAccessKey",
            "203.0.113.44",
            "quant-analyst",
            "Success",
            {"target_user": "quant-analyst", "principal": "quant-analyst", "scenario": "iam-attack"},
            10,
        ),
        (
            "AssumeRole",
            "203.0.113.44",
            "quant-analyst",
            "Success",
            {"role": "TradingProdAdminRole", "principal": "quant-analyst", "scenario": "iam-attack"},
            8,
        ),
        (
            "AttachUserPolicy",
            "203.0.113.44",
            "quant-analyst",
            "Success",
            {
                "policy": "AdministratorAccess",
                "target_user": "quant-analyst",
                "principal": "quant-analyst",
                "scenario": "iam-attack",
            },
            6,
        ),
        (
            "GetObject",
            "203.0.113.44",
            "quant-analyst",
            "Success",
            {
                "bucket": "quant-research",
                "object": "nvda-alpha-model.ipynb",
                "symbol": "NVDA",
                "principal": "quant-analyst",
                "scenario": "iam-attack",
            },
            4,
        ),
        (
            "DeactivateMFADevice",
            "203.0.113.44",
            "quant-analyst",
            "Success",
            {"target_user": "quant-analyst", "principal": "quant-analyst", "scenario": "iam-attack"},
            3,
        ),
        (
            "ConsoleLogin",
            "198.51.100.200",
            "root",
            "Success",
            {"principal": "root", "mfa": False, "scenario": "iam-attack"},
            2,
        ),
    ]

    events: list[dict[str, Any]] = []
    for event_type, source_ip, username, result, raw_payload, minutes_ago in scenario:
        occurred_at = current_time - timedelta(minutes=minutes_ago)
        event_key = f"{event_type}:{username}:{source_ip}:{minutes_ago}:{raw_payload.get('scenario')}"
        events.append(
            {
                "event_id": str(uuid5(NAMESPACE, event_key)),
                "event_type": event_type,
                "source_ip": source_ip,
                "username": username,
                "user_agent": "cloudtrail-simulator/1.0",
                "result": result,
                "raw_payload": raw_payload,
                "occurred_at": occurred_at,
            }
        )

    return events
