from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from src.identity.aws_usage import PermissionSetUsage
from src.identity.okta_client import OktaGroupMember


@dataclass(frozen=True)
class StaleUserFinding:
    email: str
    display_name: str
    groups: tuple[str, ...]
    days_since_okta_login: int | None
    days_since_aws_use: int | None
    reason: str


@dataclass(frozen=True)
class UnusedPermissionSetFinding:
    permission_set: str
    assigned_groups: tuple[str, ...]
    assigned_user_count: int
    reason: str


@dataclass(frozen=True)
class IdentityDriftReport:
    generated_at: datetime
    stale_users: list[StaleUserFinding]
    unused_permission_sets: list[UnusedPermissionSetFinding]
    total_users_reviewed: int
    total_permission_sets_reviewed: int
    source: str


def build_identity_drift_report(
    users: list[OktaGroupMember],
    permission_sets: list[PermissionSetUsage],
    stale_after_days: int = 30,
    now: datetime | None = None,
    source: str = "live",
) -> IdentityDriftReport:
    current = now or datetime.now(timezone.utc)
    users_by_group = _users_by_group(users)
    last_aws_use_by_user = _last_aws_use_by_user(permission_sets)
    stale_users: list[StaleUserFinding] = []

    for user in users:
        aws_last_used = last_aws_use_by_user.get(user.email)
        days_since_aws_use = _days_since(aws_last_used, current)
        days_since_okta_login = _days_since(user.last_login, current)

        if aws_last_used is None:
            stale_users.append(
                StaleUserFinding(
                    email=user.email,
                    display_name=user.display_name,
                    groups=user.groups,
                    days_since_okta_login=days_since_okta_login,
                    days_since_aws_use=None,
                    reason="User is in an AWS-granting Okta group but has no observed AWS usage.",
                )
            )
            continue

        if days_since_aws_use is not None and days_since_aws_use > stale_after_days:
            stale_users.append(
                StaleUserFinding(
                    email=user.email,
                    display_name=user.display_name,
                    groups=user.groups,
                    days_since_okta_login=days_since_okta_login,
                    days_since_aws_use=days_since_aws_use,
                    reason=f"Last observed AWS use is older than {stale_after_days} days.",
                )
            )

    unused_permission_sets = [
        UnusedPermissionSetFinding(
            permission_set=permission_set.permission_set,
            assigned_groups=permission_set.assigned_groups,
            assigned_user_count=sum(len(users_by_group.get(group, [])) for group in permission_set.assigned_groups),
            reason=_permission_set_reason(permission_set, users_by_group),
        )
        for permission_set in permission_sets
        if not permission_set.last_used_by_user
    ]

    return IdentityDriftReport(
        generated_at=current,
        stale_users=stale_users,
        unused_permission_sets=unused_permission_sets,
        total_users_reviewed=len(users),
        total_permission_sets_reviewed=len(permission_sets),
        source=source,
    )


def render_markdown_report(report: IdentityDriftReport) -> str:
    lines = [
        "# IdentityDrift Report",
        "",
        f"Generated: {report.generated_at.isoformat()}",
        f"Source: {report.source}",
        "",
        "## Summary",
        "",
        f"- AWS-granting Okta users reviewed: {report.total_users_reviewed}",
        f"- AWS permission sets reviewed: {report.total_permission_sets_reviewed}",
        f"- Stale AWS access findings: {len(report.stale_users)}",
        f"- Unused permission set findings: {len(report.unused_permission_sets)}",
        "",
        "## Stale AWS Access Findings",
        "",
    ]

    if report.stale_users:
        lines.extend(["| User | Groups | Okta Last Login | AWS Last Used | Reason |", "|---|---|---:|---:|---|"])
        for finding in report.stale_users:
            lines.append(
                "| "
                f"{finding.email} | "
                f"{', '.join(finding.groups)} | "
                f"{_days_label(finding.days_since_okta_login)} | "
                f"{_days_label(finding.days_since_aws_use)} | "
                f"{finding.reason} |"
            )
    else:
        lines.append("No stale AWS access findings.")

    lines.extend(["", "## Unused Permission Sets", ""])
    if report.unused_permission_sets:
        lines.extend(["| Permission Set | Groups | Assigned Users | Reason |", "|---|---|---:|---|"])
        for finding in report.unused_permission_sets:
            lines.append(
                "| "
                f"{finding.permission_set} | "
                f"{', '.join(finding.assigned_groups) or 'none'} | "
                f"{finding.assigned_user_count} | "
                f"{finding.reason} |"
            )
    else:
        lines.append("No unused permission set findings.")

    lines.extend(
        [
            "",
            "## Analyst Notes",
            "",
            "- A finding means access should be reviewed; it does not prove misuse.",
            "- Users with no observed AWS use are strong candidates for group removal or permission set review.",
            "- Permission sets with zero usage should be validated with the business owner before removal.",
        ]
    )
    return "\n".join(lines) + "\n"


def sample_okta_members(now: datetime | None = None) -> list[OktaGroupMember]:
    current = now or datetime.now(timezone.utc)
    return [
        OktaGroupMember(
            user_id="00u-active-admin",
            email="active.admin@example.com",
            display_name="Active Admin",
            groups=("AWS-Admins",),
            last_login=current,
        ),
        OktaGroupMember(
            user_id="00u-stale-readonly",
            email="stale.readonly@example.com",
            display_name="Stale ReadOnly",
            groups=("AWS-ReadOnly",),
            last_login=current.replace(year=current.year - 1),
        ),
    ]


def _users_by_group(users: list[OktaGroupMember]) -> dict[str, list[OktaGroupMember]]:
    grouped: dict[str, list[OktaGroupMember]] = {}
    for user in users:
        for group in user.groups:
            grouped.setdefault(group, []).append(user)
    return grouped


def _last_aws_use_by_user(permission_sets: list[PermissionSetUsage]) -> dict[str, datetime]:
    last_used: dict[str, datetime] = {}
    for permission_set in permission_sets:
        for email, observed_at in permission_set.last_used_by_user.items():
            if email not in last_used or observed_at > last_used[email]:
                last_used[email] = observed_at
    return last_used


def _permission_set_reason(
    permission_set: PermissionSetUsage,
    users_by_group: dict[str, list[OktaGroupMember]],
) -> str:
    assigned_count = sum(len(users_by_group.get(group, [])) for group in permission_set.assigned_groups)
    if assigned_count == 0:
        return "Permission set has no assigned Okta users through its mapped groups."
    return "Permission set has assigned users but no observed AWS usage."


def _days_since(value: datetime | None, now: datetime) -> int | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return max((now - value).days, 0)


def _days_label(value: int | None) -> str:
    return "never observed" if value is None else f"{value} days ago"

