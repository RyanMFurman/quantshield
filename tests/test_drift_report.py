from __future__ import annotations

from datetime import datetime, timedelta, timezone

from src.identity.aws_usage import PermissionSetUsage, permission_set_usage_from_access_analyzer
from src.identity.drift_report import build_identity_drift_report, render_markdown_report
from src.identity.okta_client import OktaGroupMember


NOW = datetime(2026, 6, 21, tzinfo=timezone.utc)


def test_stale_user_in_aws_group_is_flagged() -> None:
    report = build_identity_drift_report(
        users=[
            OktaGroupMember(
                user_id="00u1",
                email="stale@example.com",
                display_name="Stale User",
                groups=("AWS-ReadOnly",),
                last_login=NOW - timedelta(days=90),
            )
        ],
        permission_sets=[
            PermissionSetUsage(
                permission_set="IdentityDrift-ReadOnly",
                assigned_groups=("AWS-ReadOnly",),
                last_used_by_user={},
            )
        ],
        stale_after_days=30,
        now=NOW,
    )

    assert len(report.stale_users) == 1
    assert report.stale_users[0].email == "stale@example.com"
    assert report.stale_users[0].days_since_aws_use is None


def test_active_user_is_not_flagged() -> None:
    report = build_identity_drift_report(
        users=[
            OktaGroupMember(
                user_id="00u2",
                email="active@example.com",
                display_name="Active User",
                groups=("AWS-Admins",),
                last_login=NOW - timedelta(days=1),
            )
        ],
        permission_sets=[
            PermissionSetUsage(
                permission_set="IdentityDrift-Admin",
                assigned_groups=("AWS-Admins",),
                last_used_by_user={"active@example.com": NOW - timedelta(days=2)},
            )
        ],
        stale_after_days=30,
        now=NOW,
    )

    assert report.stale_users == []


def test_permission_set_with_no_assigned_users_does_not_crash() -> None:
    report = build_identity_drift_report(
        users=[],
        permission_sets=[
            PermissionSetUsage(
                permission_set="IdentityDrift-Billing",
                assigned_groups=("AWS-Billing",),
                last_used_by_user={},
            )
        ],
        stale_after_days=30,
        now=NOW,
    )

    assert len(report.unused_permission_sets) == 1
    assert report.unused_permission_sets[0].assigned_user_count == 0
    assert "no assigned Okta users" in report.unused_permission_sets[0].reason


def test_markdown_report_contains_findings() -> None:
    report = build_identity_drift_report(
        users=[
            OktaGroupMember(
                user_id="00u3",
                email="review@example.com",
                display_name="Review User",
                groups=("AWS-ReadOnly",),
                last_login=None,
            )
        ],
        permission_sets=[],
        now=NOW,
    )

    markdown = render_markdown_report(report)

    assert "# IdentityDrift Report" in markdown
    assert "review@example.com" in markdown


def test_access_analyzer_findings_normalize_to_permission_set_usage() -> None:
    usage = permission_set_usage_from_access_analyzer(
        [
            {
                "id": "finding-123",
                "resource": "arn:aws:iam::111122223333:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_IdentityDrift-ReadOnly_abcd",
            }
        ]
    )

    read_only = next(item for item in usage if item.permission_set == "IdentityDrift-ReadOnly")

    assert read_only.source == "access-analyzer"
    assert read_only.assigned_groups == ("AWS-ReadOnly",)
    assert read_only.notes == ("Access Analyzer unused-access finding: finding-123",)
