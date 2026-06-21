from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class PermissionSetUsage:
    permission_set: str
    assigned_groups: tuple[str, ...]
    last_used_by_user: dict[str, datetime] = field(default_factory=dict)
    source: str = "manual"
    notes: tuple[str, ...] = ()


DEFAULT_PERMISSION_SET_GROUPS = {
    "IdentityDrift-Admin": ("AWS-Admins",),
    "IdentityDrift-ReadOnly": ("AWS-ReadOnly",),
    "IdentityDrift-Billing": ("AWS-Billing",),
}


def fetch_access_analyzer_unused_findings(
    analyzer_arn: str,
    region_name: str | None = None,
) -> list[dict[str, Any]]:
    """Return active Access Analyzer unused-access findings, if configured.

    This intentionally stays thin: IAM Identity Center usage data varies by
    account configuration, but Access Analyzer unused-access findings are a
    free way to validate the live AWS pipeline when the sandbox account has
    supported findings enabled.
    """

    import boto3

    client = boto3.client("accessanalyzer", region_name=region_name)
    paginator = client.get_paginator("list_findings")
    findings: list[dict[str, Any]] = []
    for page in paginator.paginate(
        analyzerArn=analyzer_arn,
        filter={
            "status": {"eq": ["ACTIVE"]},
            "findingType": {"eq": ["UnusedIAMRole", "UnusedIAMUserAccessKey", "UnusedIAMUserPassword"]},
        },
    ):
        findings.extend(page.get("findings", []))
    return findings


def permission_set_usage_from_access_analyzer(
    findings: list[dict[str, Any]],
    permission_set_groups: dict[str, tuple[str, ...]] | None = None,
) -> list[PermissionSetUsage]:
    mappings = permission_set_groups or DEFAULT_PERMISSION_SET_GROUPS
    findings_by_permission_set = {
        permission_set: [
            finding
            for finding in findings
            if _normalized(permission_set) in _normalized(str(finding.get("resource") or finding.get("resourceOwnerAccount") or ""))
        ]
        for permission_set in mappings
    }

    usage: list[PermissionSetUsage] = []
    for permission_set, groups in mappings.items():
        matched = findings_by_permission_set[permission_set]
        notes = tuple(
            f"Access Analyzer unused-access finding: {finding.get('id', 'unknown')}"
            for finding in matched
        )
        usage.append(
            PermissionSetUsage(
                permission_set=permission_set,
                assigned_groups=groups,
                last_used_by_user={},
                source="access-analyzer",
                notes=notes
                or ("No matching Access Analyzer unused-access finding was returned for this permission set.",),
            )
        )
    return usage


def sample_permission_set_usage(now: datetime | None = None) -> list[PermissionSetUsage]:
    current = now or datetime.now(timezone.utc)
    return [
        PermissionSetUsage(
            permission_set="IdentityDrift-Admin",
            assigned_groups=("AWS-Admins",),
            last_used_by_user={"active.admin@example.com": current},
            source="sample",
        ),
        PermissionSetUsage(
            permission_set="IdentityDrift-ReadOnly",
            assigned_groups=("AWS-ReadOnly",),
            last_used_by_user={},
            source="sample",
            notes=("No observed AWS access for assigned read-only users.",),
        ),
        PermissionSetUsage(
            permission_set="IdentityDrift-Billing",
            assigned_groups=("AWS-Billing",),
            last_used_by_user={},
            source="sample",
            notes=("Permission set exists but currently has no assigned users in sample data.",),
        ),
    ]


def _normalized(value: str) -> str:
    return value.lower().replace("-", "").replace("_", "")
