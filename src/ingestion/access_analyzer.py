from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def list_access_analyzer_findings(
    analyzer_arn: str,
    region_name: str | None = None,
    status: str = "ACTIVE",
) -> list[dict[str, Any]]:
    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError
    except ImportError as exc:
        raise RuntimeError("boto3 is required for Access Analyzer ingestion") from exc

    try:
        client = boto3.client("accessanalyzer", region_name=region_name)
        paginator = client.get_paginator("list_findings")
        findings: list[dict[str, Any]] = []
        for page in paginator.paginate(analyzerArn=analyzer_arn, filter={"status": {"eq": [status]}}):
            findings.extend(_normalize_finding(item) for item in page.get("findings", []))
        return findings
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(f"Failed to list Access Analyzer findings: {exc}") from exc


def _normalize_finding(finding: dict[str, Any]) -> dict[str, Any]:
    resource = str(finding.get("resource") or "unknown")
    finding_type = str(finding.get("findingType") or finding.get("finding_type") or "unknown")
    status = str(finding.get("status") or "unknown")
    created_at = finding.get("createdAt") or finding.get("created_at") or datetime.now(timezone.utc)

    return {
        "source": "aws_access_analyzer",
        "finding_id": str(finding.get("id") or ""),
        "finding_type": finding_type,
        "resource": resource,
        "resource_type": finding.get("resourceType") or finding.get("resource_type"),
        "status": status,
        "principal": finding.get("principal"),
        "condition": finding.get("condition"),
        "created_at": created_at,
        "description": f"Access Analyzer {finding_type} finding for {resource}",
    }
