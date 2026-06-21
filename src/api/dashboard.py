from __future__ import annotations

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


def render_connection_state(data: dict[str, dict[str, Any]]) -> None:
    health = data.get("health", {})
    if health.get("error"):
        st.error("API unreachable")
        st.caption(health["error"])
        return

    payload = health.get("payload") or {}
    st.success(f"{payload.get('service', 'QuantShield API')} online")


def render_overview(data: dict[str, dict[str, Any]]) -> None:
    alerts = items_for(data, "alerts")
    market = items_for(data, "market")
    events = items_for(data, "events")
    risks = items_for(data, "insider_risk")
    p1_alerts = [alert for alert in alerts if alert.get("severity") == "P1"]
    top_risk = max(
        [float(risk.get("risk_score") or 0) for risk in risks],
        default=0.0,
    )

    metric_cols = st.columns(5)
    metric_cols[0].metric("Insider findings", len(risks))
    metric_cols[1].metric("Top risk score", f"{top_risk:.0f}")
    metric_cols[2].metric("Active alerts", len(alerts))
    metric_cols[3].metric("P1 alerts", len(p1_alerts))
    metric_cols[4].metric("Tracked symbols", len(market))

    lower_cols = st.columns((1.2, 1, 1))

    with lower_cols[0]:
        st.subheader("Highest Risk")
        if risks:
            top_findings = sorted(
                risks,
                key=lambda item: float(item.get("risk_score") or 0),
                reverse=True,
            )[:5]
            st.dataframe(
                [
                    {
                        "Symbol": item.get("symbol"),
                        "Score": item.get("risk_score"),
                        "Severity": item.get("severity"),
                        "User": item.get("affected_user"),
                        "Signal": item.get("market_signal"),
                    }
                    for item in top_findings
                ],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No insider-risk findings are active.")

    with lower_cols[1]:
        st.subheader("Detection Summary")
        detection_items = items_for(data, "detections")
        if detection_items:
            st.dataframe(detection_items, use_container_width=True, hide_index=True)
        else:
            st.info("No open detection summary yet.")

    with lower_cols[2]:
        st.subheader("Recent Activity")
        st.metric("Security events", len(events))
        st.metric("Database", "Connected" if database_configured(data) else "Not connected")
        render_connection_state(data)


def render_insider_risk(data: dict[str, dict[str, Any]]) -> None:
    source = data.get("insider_risk", {})
    if source.get("error"):
        st.warning(f"Insider risk unavailable: {source['error']}")
        return

    items = items_for(data, "insider_risk")
    if not items:
        st.info("No insider-risk findings are active.")
        return

    st.dataframe(
        [
            {
                "Symbol": item.get("symbol"),
                "Score": item.get("risk_score"),
                "Severity": item.get("severity"),
                "User": item.get("affected_user"),
                "Source IP": item.get("source_ip"),
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

    selected = items[0]
    st.subheader("Lead Finding")
    st.write(selected.get("reason"))


def render_active_alerts(data: dict[str, dict[str, Any]]) -> None:
    source = data.get("alerts", {})
    if source.get("error"):
        st.warning(f"Active alerts unavailable: {source['error']}")
        return

    items = items_for(data, "alerts")
    if not items:
        st.info("No alerts are active.")
        return

    st.dataframe(
        [
            {
                "Severity": item.get("severity"),
                "Rule": item.get("rule_name"),
                "User": item.get("affected_user"),
                "Source IP": item.get("source_ip"),
                "Status": item.get("status"),
                "Triggered": item.get("triggered_at"),
                "Description": item.get("description"),
            }
            for item in items
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
                "Source IP": item.get("source_ip"),
                "Result": item.get("result"),
                "Occurred": item.get("occurred_at"),
            }
            for item in items
        ],
        use_container_width=True,
        hide_index=True,
    )


def render_system(data: dict[str, dict[str, Any]], api_base_url: str) -> None:
    st.subheader("Runtime")
    render_connection_state(data)
    st.json(
        {
            "api_base_url": api_base_url,
            "database_configured": database_configured(data),
            "refresh_cache_seconds": 30,
        }
    )


def main() -> None:
    st.set_page_config(
        page_title="QuantShield SOC",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("QuantShield SOC")
    st.caption("Financial security operations dashboard")

    with st.sidebar:
        st.subheader("Connection")
        api_base_url = st.text_input("FastAPI base URL", value=DEFAULT_API_URL)

        if st.button("Refresh", use_container_width=True):
            st.cache_data.clear()

    data = load_dashboard_data(api_base_url)

    tab_overview, tab_risk, tab_alerts, tab_market, tab_events, tab_system = st.tabs(
        ["Overview", "Insider Risk", "Alerts", "Market", "Events", "System"]
    )

    with tab_overview:
        render_overview(data)

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
