from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class OktaGroupMember:
    user_id: str
    email: str
    display_name: str
    groups: tuple[str, ...]
    last_login: datetime | None


class OktaClient:
    """Small Okta API client for group membership and last-login review."""

    def __init__(self, org_url: str, api_token: str) -> None:
        self.org_url = org_url.rstrip("/") + "/"
        self.api_token = api_token

    def get_aws_group_members(self, group_names: list[str]) -> list[OktaGroupMember]:
        members_by_id: dict[str, OktaGroupMember] = {}

        for group_name in group_names:
            group = self._find_group(group_name)
            if not group:
                continue

            for raw_user in self._get_json(f"/api/v1/groups/{group['id']}/users"):
                profile = raw_user.get("profile", {})
                user_id = str(raw_user.get("id", ""))
                email = str(profile.get("email") or profile.get("login") or user_id)
                display_name = _display_name(profile, email)
                last_login = _parse_okta_datetime(raw_user.get("lastLogin"))
                existing = members_by_id.get(user_id)
                groups = tuple(sorted({*(existing.groups if existing else ()), group_name}))
                members_by_id[user_id] = OktaGroupMember(
                    user_id=user_id,
                    email=email,
                    display_name=display_name,
                    groups=groups,
                    last_login=last_login if existing is None else existing.last_login or last_login,
                )

        return sorted(members_by_id.values(), key=lambda member: member.email)

    def _find_group(self, group_name: str) -> dict[str, Any] | None:
        groups = self._get_json(f"/api/v1/groups?q={quote(group_name)}")
        for group in groups:
            profile = group.get("profile", {})
            if profile.get("name") == group_name:
                return group
        return None

    def _get_json(self, path: str) -> list[dict[str, Any]]:
        url = urljoin(self.org_url, path.lstrip("/"))
        request = Request(
            url,
            headers={
                "Accept": "application/json",
                "Authorization": f"SSWS {self.api_token}",
            },
            method="GET",
        )
        with urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
        data = json.loads(body)
        if not isinstance(data, list):
            raise ValueError(f"Expected Okta list response from {path}")
        return data


def _parse_okta_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    if not isinstance(value, str):
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _display_name(profile: dict[str, Any], fallback: str) -> str:
    first = str(profile.get("firstName") or "").strip()
    last = str(profile.get("lastName") or "").strip()
    full_name = f"{first} {last}".strip()
    return full_name or fallback

