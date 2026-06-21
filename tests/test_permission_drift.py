from __future__ import annotations

from src.analysis.permission_drift import calculate_permission_drift


def test_permission_drift_reports_significant_unused_permissions() -> None:
    reports = calculate_permission_drift(
        {"deploy": {"iam:CreateRole", "iam:DeleteRole", "iam:PassRole", "iam:TagRole"}},
        {"deploy": {"iam:CreateRole"}},
    )

    assert reports[0].used_percentage == 25.0
    assert reports[0].unused_actions == ["iam:deleterole", "iam:passrole", "iam:tagrole"]
    assert reports[0].recommendation["remove_actions"] == reports[0].unused_actions


def test_permission_drift_reports_no_drift_when_all_actions_used() -> None:
    reports = calculate_permission_drift(
        {"lambda": {"logs:CreateLogStream", "logs:PutLogEvents"}},
        {"lambda": {"logs:CreateLogStream", "logs:PutLogEvents"}},
    )

    assert reports[0].used_percentage == 100.0
    assert reports[0].unused_actions == []


def test_permission_drift_handles_missing_usage_without_false_100_percent_drift() -> None:
    reports = calculate_permission_drift(
        {"ec2": {"ssm:UpdateInstanceInformation", "ssmmessages:CreateControlChannel"}},
        {},
    )

    assert reports[0].used_percentage is None
    assert reports[0].used_actions == []
    assert reports[0].recommendation["remove_actions"] == []
