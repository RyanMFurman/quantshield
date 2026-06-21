from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EVENT_ACTION_MAP = {
    "AssumeRole": "sts:AssumeRole",
    "AttachRolePolicy": "iam:AttachRolePolicy",
    "AttachUserPolicy": "iam:AttachUserPolicy",
    "ConsoleLogin": "signin:ConsoleLogin",
    "CreateAccessKey": "iam:CreateAccessKey",
    "CreatePolicyVersion": "iam:CreatePolicyVersion",
    "DeactivateMFADevice": "iam:DeactivateMFADevice",
    "GetObject": "s3:GetObject",
    "PutUserPolicy": "iam:PutUserPolicy",
    "SSMStartSession": "ssm:StartSession",
}


@dataclass(frozen=True)
class DriftReport:
    role_name: str
    granted_actions: list[str]
    used_actions: list[str]
    unused_actions: list[str]
    used_percentage: float | None
    recommendation: dict[str, list[str]]


def calculate_permission_drift(
    role_policies: dict[str, set[str]],
    usage_by_role: dict[str, set[str]],
) -> list[DriftReport]:
    reports: list[DriftReport] = []

    for role_name, granted in sorted(role_policies.items()):
        used = usage_by_role.get(role_name)
        granted_normalized = {action.lower() for action in granted}
        used_normalized = {action.lower() for action in used or set()}
        used_granted = granted_normalized.intersection(used_normalized)
        unused = granted_normalized - used_granted
        used_percentage = None if used is None else _percentage(len(used_granted), len(granted_normalized))

        reports.append(
            DriftReport(
                role_name=role_name,
                granted_actions=sorted(granted_normalized),
                used_actions=sorted(used_normalized),
                unused_actions=sorted(unused),
                used_percentage=used_percentage,
                recommendation={"remove_actions": sorted(unused) if used is not None else []},
            )
        )

    return reports


def build_usage_by_role(events: list[dict[str, Any]]) -> dict[str, set[str]]:
    usage: dict[str, set[str]] = {}
    for event in events:
        event_type = str(event.get("event_type") or "")
        action = EVENT_ACTION_MAP.get(event_type)
        if not action:
            continue

        payload = event.get("raw_payload")
        payload_dict = payload if isinstance(payload, dict) else {}
        role = str(payload_dict.get("role") or payload_dict.get("role_name") or event.get("username") or "unknown")
        usage.setdefault(role, set()).add(action)

    return usage


def load_terraform_role_policies(module_path: str | Path) -> dict[str, set[str]]:
    main_tf = Path(module_path) / "main.tf"
    content = main_tf.read_text(encoding="utf-8")
    policies: dict[str, set[str]] = {}

    for policy_name, block in _policy_document_blocks(content).items():
        policies[policy_name] = _actions_from_block(block)

    return {
        "lambda": policies.get("lambda_logs", set()),
        "ec2": policies.get("ec2_ssm", set()),
        "github_actions_deploy": policies.get("github_actions_deploy", set()),
        "deploy_permission_boundary": policies.get("deploy_permission_boundary", set()),
    }


def _policy_document_blocks(content: str) -> dict[str, str]:
    starts = list(re.finditer(r'data\s+"aws_iam_policy_document"\s+"([^"]+)"\s+\{', content))
    blocks: dict[str, str] = {}
    for index, match in enumerate(starts):
        start = match.end()
        end = starts[index + 1].start() if index + 1 < len(starts) else len(content)
        blocks[match.group(1)] = content[start:end]
    return blocks


def _actions_from_block(block: str) -> set[str]:
    actions: set[str] = set()
    for list_match in re.finditer(r"actions\s*=\s*\[(.*?)\]", block, re.DOTALL):
        actions.update(re.findall(r'"([^"]+)"', list_match.group(1)))
    for scalar_match in re.finditer(r'actions\s*=\s*"([^"]+)"', block):
        actions.add(scalar_match.group(1))
    return actions


def _percentage(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)
