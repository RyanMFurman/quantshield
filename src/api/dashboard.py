from __future__ import annotations

from html import escape
from os import getenv
from typing import Any

import httpx
import streamlit as st

DEFAULT_API_URL = getenv("QUANTSHIELD_API_URL", "http://127.0.0.1:8000")


@st.cache_data(ttl=30, show_spinner=False)
def fetch_json(api_base_url: str, path: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{api_base_url}{path}")
            response.raise_for_status()
            return response.json(), None
    except httpx.HTTPError as exc:
        return None, str(exc)


def load_dashboard_data(api_base_url: str) -> dict[str, dict[str, Any]]:
    paths = {
        "health": "/health",
        "market": "/market/latest",
        "alerts": "/alerts/active",
        "events": "/api/v1/events/recent",
        "detections": "/api/v1/detections/summary",
        "insider_risk": "/api/v1/insider-risk",
    }

    data: dict[str, dict[str, Any]] = {}
    for key, path in paths.items():
        payload, error = fetch_json(api_base_url, path)
        data[key] = {"payload": payload, "error": error}

    return data


def items_for(data: dict[str, dict[str, Any]], key: str) -> list[dict[str, Any]]:
    payload = data.get(key, {}).get("payload") or {}
    return list(payload.get("items", []))


def database_configured(data: dict[str, dict[str, Any]]) -> bool:
    for key in ["market", "alerts", "events", "detections", "insider_risk"]:
        payload = data.get(key, {}).get("payload") or {}
        if payload.get("database_configured"):
            return True
    return False


def as_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def clean_ip(value: Any) -> str:
    return str(value or "unknown").replace("/32", "")


def severity_class(severity: Any) -> str:
    level = str(severity or "").upper()
    if level == "P1":
        return "sev-p1"
    if level == "P2":
        return "sev-p2"
    return "sev-p3"


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --qs-bg: #080b10;
            --qs-panel: #111722;
            --qs-panel-2: #151d2a;
            --qs-line: #283244;
            --qs-text: #f3f6fb;
            --qs-muted: #9ca8ba;
            --qs-red: #ff4d5e;
            --qs-amber: #f5b84b;
            --qs-green: #42d392;
            --qs-cyan: #64d8ff;
        }
        .stApp {
            background: var(--qs-bg);
            color: var(--qs-text);
        }
        section[data-testid="stSidebar"] {
            background: #0d111a;
            border-right: 1px solid var(--qs-line);
        }
        .block-container {
            max-width: 1220px;
            padding-top: 2.1rem;
        }
        h1, h2, h3 {
            letter-spacing: 0;
        }
        .qs-topline {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            padding: 16px 18px;
            border: 1px solid var(--qs-line);
            background: linear-gradient(90deg, #111722 0%, #0c111a 100%);
            border-radius: 8px;
            margin-bottom: 18px;
        }
        .qs-title {
            font-size: 34px;
            font-weight: 800;
            line-height: 1.05;
        }
        .qs-subtitle {
            color: var(--qs-muted);
            margin-top: 6px;
            font-size: 14px;
        }
        .qs-badge {
            display: inline-flex;
            align-items: center;
            border: 1px solid var(--qs-line);
            border-radius: 999px;
            padding: 6px 10px;
            font-size: 12px;
            color: var(--qs-muted);
            background: #0b1018;
            white-space: nowrap;
        }
        .qs-kpi-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 12px;
            margin-bottom: 18px;
        }
        .qs-kpi {
            min-height: 104px;
            padding: 14px;
            border: 1px solid var(--qs-line);
            background: var(--qs-panel);
            border-radius: 8px;
        }
        .qs-kpi-label {
            color: var(--qs-muted);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: .06em;
        }
        .qs-kpi-value {
            font-size: 32px;
            line-height: 1;
            font-weight: 800;
            margin-top: 12px;
        }
        .qs-kpi-note {
            color: var(--qs-muted);
            font-size: 12px;
            margin-top: 10px;
        }
        .qs-panel {
            border: 1px solid var(--qs-line);
            background: var(--qs-panel);
            border-radius: 8px;
            padding: 16px;
            min-height: 180px;
            margin-bottom: 16px;
        }
        .qs-panel h3 {
            font-size: 17px;
            margin: 0 0 12px 0;
        }
        .qs-incident {
            border-left: 4px solid var(--qs-red);
        }
        .qs-row {
            display: grid;
            grid-template-columns: 70px 76px minmax(0, 1fr) 120px;
            gap: 10px;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,.06);
            font-size: 13px;
        }
        .qs-row:last-child {
            border-bottom: 0;
        }
        .qs-table {
            display: grid;
            gap: 0;
            margin-top: 8px;
        }
        .qs-table-row {
            display: grid;
            align-items: center;
            gap: 14px;
            padding: 12px 0;
            border-bottom: 1px solid rgba(255,255,255,.06);
            font-size: 13px;
            min-width: 0;
        }
        .qs-table-row:last-child {
            border-bottom: 0;
        }
        .qs-iam-row {
            grid-template-columns: 52px minmax(170px, 1.4fr) minmax(120px, .9fr) 128px;
        }
        .qs-risk-row {
            grid-template-columns: 64px 52px 54px minmax(100px, 1fr);
        }
        .qs-cell {
            min-width: 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .qs-rule {
            font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
            font-size: 12px;
        }
        .qs-source {
            color: var(--qs-text);
            text-align: right;
            font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
            font-size: 12px;
        }
        .qs-muted {
            color: var(--qs-muted);
        }
        .sev {
            display: inline-block;
            min-width: 36px;
            text-align: center;
            border-radius: 999px;
            padding: 3px 8px;
            font-size: 12px;
            font-weight: 800;
        }
        .sev-p1 {
            color: #fff;
            background: rgba(255,77,94,.88);
        }
        .sev-p2 {
            color: #121212;
            background: rgba(245,184,75,.96);
        }
        .sev-p3 {
            color: #07140d;
            background: rgba(66,211,146,.95);
        }
        .qs-progress {
            height: 8px;
            background: #202838;
            border-radius: 999px;
            overflow: hidden;
            margin-top: 7px;
        }
        .qs-progress span {
            display: block;
            height: 8px;
            background: linear-gradient(90deg, var(--qs-amber), var(--qs-red));
        }
        .qs-timeline {
            display: grid;
            gap: 10px;
        }
        .qs-timeline-item {
            border-left: 2px solid var(--qs-cyan);
            padding-left: 12px;
            color: var(--qs-muted);
            font-size: 13px;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid var(--qs-line);
            border-radius: 8px;
            overflow: hidden;
        }
        @media (max-width: 900px) {
            .qs-kpi-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
            .qs-row {
                grid-template-columns: 56px 60px minmax(0, 1fr);
            }
            .qs-row .qs-source {
                display: none;
            }
            .qs-iam-row,
            .qs-risk-row {
                grid-template-columns: 52px minmax(0, 1fr);
            }
            .qs-iam-row .qs-user,
            .qs-iam-row .qs-source,
            .qs-risk-row .qs-score,
            .qs-risk-row .qs-source {
                display: none;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_kpi(label: str, value: str, note: str = "") -> str:
    return (
        "<div class='qs-kpi'>"
        f"<div class='qs-kpi-label'>{escape(label)}</div>"
        f"<div class='qs-kpi-value'>{escape(value)}</div>"
        f"<div class='qs-kpi-note'>{escape(note)}</div>"
        "</div>"
    )


def render_header(data: dict[str, dict[str, Any]]) -> None:
    db_state = "DB connected" if database_configured(data) else "DB offline"
    api_state = "API online" if not data.get("health", {}).get("error") else "API offline"
    st.markdown(
        """
        <div class="qs-topline">
          <div>
            <div class="qs-title">QuantShield SOC</div>
            <div class="qs-subtitle">Local financial security lab for IAM abuse, cloud telemetry, insider risk, and alert triage.</div>
          </div>
          <div>
            <span class="qs-badge">"""
        + escape(api_state)
        + """</span>
            <span class="qs-badge">"""
        + escape(db_state)
        + """</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_overview(data: dict[str, dict[str, Any]]) -> None:
    alerts = items_for(data, "alerts")
    market = items_for(data, "market")
    events = items_for(data, "events")
    risks = sorted(
        items_for(data, "insider_risk"),
        key=lambda item: as_float(item.get("risk_score")),
        reverse=True,
    )
    p1_risks = [risk for risk in risks if risk.get("severity") == "P1"]
    p1_alerts = [alert for alert in alerts if alert.get("severity") == "P1"]
    top_risk = as_float(risks[0].get("risk_score")) if risks else 0.0

    kpis = [
        render_kpi("Lab posture", "High" if top_risk >= 90 else "Elevated", "Driven by correlated market/security signals"),
        render_kpi("Top risk score", f"{top_risk:.0f}", "NVDA scenario should hit 100 in demo data"),
        render_kpi("Insider-risk findings", str(len(risks)), f"{len(p1_risks)} P1 correlated risk finding(s)"),
        render_kpi("Active alerts", str(len(alerts)), f"{len(p1_alerts)} P1 alert(s), {len(alerts)} total"),
        render_kpi("Telemetry", str(len(events)), f"{len(market)} tracked market symbols"),
    ]
    st.markdown("<div class='qs-kpi-grid'>" + "".join(kpis) + "</div>", unsafe_allow_html=True)

    left, middle, right = st.columns((1.35, 1.05, 1))

    with left:
        lead = risks[0] if risks else {}
        reason = str(lead.get("reason") or "No active lead finding.")
        score = as_float(lead.get("risk_score"))
        st.markdown(
            f"""
            <div class="qs-panel qs-incident">
              <h3>Lead Risk Case</h3>
              <div class="qs-muted">Identity + research-data + market-context correlation</div>
              <div style="font-size:24px;font-weight:800;margin-top:8px;">
                {escape(str(lead.get("symbol") or "No symbol"))} risk score {score:.0f}
              </div>
              <div class="qs-progress"><span style="width:{min(score, 100):.0f}%"></span></div>
              <p style="margin-top:14px;">{escape(reason)}</p>
              <div class="qs-muted">User: {escape(str(lead.get("affected_user") or "unknown"))} &middot; Source: {escape(clean_ip(lead.get("source_ip")))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with middle:
        rows = []
        for risk in risks[:5]:
            rows.append(
                "<div class='qs-table-row qs-risk-row'>"
                f"<div class='qs-cell'>{escape(str(risk.get('symbol') or ''))}</div>"
                f"<div class='qs-cell qs-score'>{as_float(risk.get('risk_score')):.0f}</div>"
                f"<div class='qs-cell'><span class='sev {severity_class(risk.get('severity'))}'>{escape(str(risk.get('severity') or ''))}</span></div>"
                f"<div class='qs-cell qs-source'>{escape(clean_ip(risk.get('source_ip')))}</div>"
                "</div>"
            )
        st.markdown(
            "<div class='qs-panel'><h3>Risk Queue</h3>"
            + "<div class='qs-table'>"
            + ("".join(rows) if rows else "<div class='qs-muted'>No open findings.</div>")
            + "</div>"
            + "</div>",
            unsafe_allow_html=True,
        )

    with right:
        timeline_items = [
            f"{len(events)} security events ingested",
            f"{len(alerts)} alert(s) open for analyst review",
            f"{len(risks)} insider-risk finding(s) correlated",
            "Docker lab running locally",
        ]
        timeline = "".join(
            f"<div class='qs-timeline-item'>{escape(item)}</div>" for item in timeline_items
        )
        st.markdown(
            f"<div class='qs-panel'><h3>Activity Timeline</h3><div class='qs-timeline'>{timeline}</div></div>",
            unsafe_allow_html=True,
        )


def render_insider_risk(data: dict[str, dict[str, Any]]) -> None:
    source = data.get("insider_risk", {})
    if source.get("error"):
        st.warning(f"Insider risk unavailable: {source['error']}")
        return

    items = sorted(
        items_for(data, "insider_risk"),
        key=lambda item: as_float(item.get("risk_score")),
        reverse=True,
    )
    if not items:
        st.info("No insider-risk findings are active.")
        return

    for item in items[:3]:
        st.markdown(
            f"""
            <div class="qs-panel">
              <h3>{escape(str(item.get("symbol") or "Unknown"))} &middot; {as_float(item.get("risk_score")):.0f}</h3>
              <span class="sev {severity_class(item.get("severity"))}">{escape(str(item.get("severity") or ""))}</span>
              <p>{escape(str(item.get("reason") or ""))}</p>
              <div class="qs-muted">User {escape(str(item.get("affected_user") or "unknown"))} &middot; Source {escape(clean_ip(item.get("source_ip")))} &middot; {escape(str(item.get("related_event_count") or 0))} related events</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.dataframe(
        [
            {
                "Symbol": item.get("symbol"),
                "Score": item.get("risk_score"),
                "Severity": item.get("severity"),
                "User": item.get("affected_user"),
                "Source IP": clean_ip(item.get("source_ip")),
                "Signal": item.get("market_signal"),
                "Events": item.get("related_event_count"),
                "Status": item.get("status"),
                "Detected": item.get("detected_at"),
            }
            for item in items
        ],
        use_container_width=True,
        hide_index=True,
    )


def render_active_alerts(data: dict[str, dict[str, Any]]) -> None:
    source = data.get("alerts", {})
    if source.get("error"):
        st.warning(f"Active alerts unavailable: {source['error']}")
        return

    items = items_for(data, "alerts")
    if not items:
        st.info("No alerts are active.")
        return

    for item in items:
        st.markdown(
            f"""
            <div class="qs-panel">
              <h3>{escape(str(item.get("rule_name") or "Alert"))}</h3>
              <span class="sev {severity_class(item.get("severity"))}">{escape(str(item.get("severity") or ""))}</span>
              <p>{escape(str(item.get("description") or ""))}</p>
              <div class="qs-muted">MITRE {escape(str(item.get("mitre_technique") or "unmapped"))} &middot; User {escape(str(item.get("affected_user") or "unknown"))} &middot; Source {escape(clean_ip(item.get("source_ip")))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_iam_risk(data: dict[str, dict[str, Any]]) -> None:
    events = items_for(data, "events")
    alerts = items_for(data, "alerts")
    iam_event_types = {
        "AttachRolePolicy",
        "AttachUserPolicy",
        "PutUserPolicy",
        "CreatePolicyVersion",
        "CreateAccessKey",
        "DeactivateMFADevice",
        "AssumeRole",
        "ConsoleLogin",
    }
    iam_events = [event for event in events if event.get("event_type") in iam_event_types]
    iam_alerts = [
        alert
        for alert in alerts
        if str(alert.get("rule_id") or "").startswith("IAM_")
        or str(alert.get("rule_id") or "").startswith("PRIV_ESC")
    ]
    privileged_events = [
        event
        for event in iam_events
        if event.get("event_type")
        in {"AttachRolePolicy", "AttachUserPolicy", "PutUserPolicy", "CreateAccessKey", "DeactivateMFADevice", "AssumeRole"}
    ]

    st.markdown(
        "<div class='qs-kpi-grid'>"
        + render_kpi("IAM alerts", str(len(iam_alerts)), "Identity-risk detections requiring review")
        + render_kpi("IAM events", str(len(iam_events)), "CloudTrail-style identity telemetry")
        + render_kpi("Privileged actions", str(len(privileged_events)), "Policy, key, role, and MFA activity")
        + render_kpi("Root/MFA signals", str(len([e for e in iam_events if e.get("username") == "root" or e.get("event_type") == "DeactivateMFADevice"])), "High-value identity controls")
        + render_kpi("Lab mode", "Local", "No AWS spend required")
        + "</div>",
        unsafe_allow_html=True,
    )

    left, right = st.columns((1.35, 1))
    with left:
        rows = []
        if iam_alerts:
            for alert in iam_alerts[:5]:
                rows.append(
                    f"""
                    <div class="qs-table-row qs-iam-row">
                      <div class="qs-cell"><span class="sev {severity_class(alert.get("severity"))}">{escape(str(alert.get("severity") or ""))}</span></div>
                      <div class="qs-cell qs-rule">{escape(str(alert.get("rule_id") or ""))}</div>
                      <div class="qs-cell qs-user">{escape(str(alert.get("affected_user") or "unknown"))}</div>
                      <div class="qs-cell qs-source">{escape(clean_ip(alert.get("source_ip")))}</div>
                    </div>
                    """
                )
        st.markdown(
            "<div class='qs-panel'><h3>IAM Alert Queue</h3><div class='qs-table'>"
            + ("".join(rows) if rows else "<div class='qs-muted'>No IAM alerts are active.</div>")
            + "</div></div>",
            unsafe_allow_html=True,
        )

    with right:
        timeline = "".join(
            f"<div class='qs-timeline-item'>{escape(str(event.get('event_type') or 'unknown'))} by {escape(str(event.get('username') or 'unknown'))} from {escape(clean_ip(event.get('source_ip')))}</div>"
            for event in iam_events[:8]
        )
        st.markdown(
            "<div class='qs-panel'><h3>Identity Attack Timeline</h3><div class='qs-timeline'>"
            + (timeline if timeline else "<div class='qs-muted'>No IAM telemetry loaded.</div>")
            + "</div></div>",
            unsafe_allow_html=True,
        )

    st.dataframe(
        [
            {
                "Event": event.get("event_type"),
                "Principal": event.get("username"),
                "Source IP": clean_ip(event.get("source_ip")),
                "Result": event.get("result"),
                "Occurred": event.get("occurred_at"),
            }
            for event in iam_events
        ],
        use_container_width=True,
        hide_index=True,
    )


def render_market_feed(data: dict[str, dict[str, Any]]) -> None:
    source = data.get("market", {})
    if source.get("error"):
        st.warning(f"Market feed unavailable: {source['error']}")
        return

    items = items_for(data, "market")
    if not items:
        st.info("No market prices are available.")
        return

    st.markdown(
        """
        <div class="qs-panel">
          <h3>Market Context</h3>
          <div class="qs-muted">Supporting signal for the quant-firm scenario. IAM and research-data access remain the primary detection story.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.dataframe(
        [
            {
                "Symbol": item.get("symbol"),
                "Price": item.get("price"),
                "Previous Close": item.get("prev_close"),
                "Volume": item.get("volume"),
                "Captured": item.get("captured_at"),
            }
            for item in items
        ],
        use_container_width=True,
        hide_index=True,
    )


def render_security_events(data: dict[str, dict[str, Any]]) -> None:
    source = data.get("events", {})
    if source.get("error"):
        st.warning(f"Security events unavailable: {source['error']}")
        return

    items = items_for(data, "events")
    if not items:
        st.info("No security events are available.")
        return

    st.dataframe(
        [
            {
                "Type": item.get("event_type"),
                "User": item.get("username"),
                "Source IP": clean_ip(item.get("source_ip")),
                "Result": item.get("result"),
                "Occurred": item.get("occurred_at"),
            }
            for item in items
        ],
        use_container_width=True,
        hide_index=True,
    )


def render_system(data: dict[str, dict[str, Any]], api_base_url: str) -> None:
    health = data.get("health", {})
    payload = health.get("payload") or {}
    st.markdown("<div class='qs-panel'><h3>Runtime</h3>", unsafe_allow_html=True)
    st.json(
        {
            "api_base_url": api_base_url,
            "api_status": "online" if not health.get("error") else "offline",
            "service": payload.get("service"),
            "database_configured": database_configured(data),
            "refresh_cache_seconds": 30,
        }
    )
    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(
        page_title="QuantShield SOC",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_styles()

    with st.sidebar:
        st.subheader("Connection")
        api_base_url = st.text_input("FastAPI base URL", value=DEFAULT_API_URL)

        if st.button("Refresh", use_container_width=True):
            st.cache_data.clear()

    data = load_dashboard_data(api_base_url)
    render_header(data)

    tab_overview, tab_iam, tab_risk, tab_alerts, tab_market, tab_events, tab_system = st.tabs(
        ["Overview", "IAM Risk", "Insider Risk", "Alerts", "Market Context", "Events", "System"]
    )

    with tab_overview:
        render_overview(data)

    with tab_iam:
        render_iam_risk(data)

    with tab_risk:
        render_insider_risk(data)

    with tab_alerts:
        render_active_alerts(data)

    with tab_market:
        render_market_feed(data)

    with tab_events:
        render_security_events(data)

    with tab_system:
        render_system(data, api_base_url)


if __name__ == "__main__":
    main()
