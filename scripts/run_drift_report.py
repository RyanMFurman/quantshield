from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.identity.aws_usage import (
    fetch_access_analyzer_unused_findings,
    permission_set_usage_from_access_analyzer,
    sample_permission_set_usage,
)
from src.identity.drift_report import build_identity_drift_report, render_markdown_report, sample_okta_members
from src.identity.okta_client import OktaClient


DEFAULT_GROUPS = ("AWS-Admins", "AWS-ReadOnly", "AWS-Billing")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an IdentityDrift Okta-to-AWS governance report.")
    parser.add_argument("--days", type=int, default=30, help="Flag AWS access not used within this many days.")
    parser.add_argument("--groups", default=os.getenv("OKTA_AWS_GROUPS", ",".join(DEFAULT_GROUPS)))
    parser.add_argument("--output", help="Optional markdown output path.")
    parser.add_argument("--sample-data", action="store_true", help="Run with deterministic sample data.")
    args = parser.parse_args()

    group_names = [group.strip() for group in args.groups.split(",") if group.strip()]

    if args.sample_data:
        users = sample_okta_members()
        permission_sets = sample_permission_set_usage()
        source = "sample-data"
    else:
        org_url = os.getenv("OKTA_ORG_URL")
        api_token = os.getenv("OKTA_API_TOKEN")
        if not org_url or not api_token:
            print(
                "Missing OKTA_ORG_URL or OKTA_API_TOKEN. Re-run with --sample-data for an offline proof.",
                file=sys.stderr,
            )
            return 2
        users = OktaClient(org_url, api_token).get_aws_group_members(group_names)
        analyzer_arn = os.getenv("ACCESS_ANALYZER_ARN")
        if analyzer_arn:
            findings = fetch_access_analyzer_unused_findings(analyzer_arn, os.getenv("AWS_REGION"))
            permission_sets = permission_set_usage_from_access_analyzer(findings)
            source = "okta-live/access-analyzer"
        else:
            permission_sets = sample_permission_set_usage()
            source = "okta-live/aws-usage-sample"

    report = build_identity_drift_report(
        users=users,
        permission_sets=permission_sets,
        stale_after_days=args.days,
        source=source,
    )
    markdown = render_markdown_report(report)

    if args.output:
        Path(args.output).write_text(markdown, encoding="utf-8")

    print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
