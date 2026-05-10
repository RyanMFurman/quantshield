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


def render_health(api_base_url: str) -> None:
    payload, error = fetch_json(api_base_url, "/health")

    if error:
        st.error(f"Unable to reach the FastAPI service: {error}")
        return

    st.success("FastAPI service is reachable.")
    st.json(payload)


def render_market_feed(api_base_url: str) -> None:
    payload, error = fetch_json(api_base_url, "/market/latest")

    if error:
        st.warning(f"Market feed is unavailable: {error}")
        return

    items = payload.get("items", [])
    database_configured = payload.get("database_configured", False)

    col1, col2 = st.columns(2)
    col1.metric("Tracked symbols", len(items))
    col2.metric("Database configured", "Yes" if database_configured else "No")

    if not items:
        st.info("No market prices are available yet. Connect PostgreSQL or run the ingestor next.")
        return

    st.dataframe(items, use_container_width=True, hide_index=True)


def render_active_alerts(api_base_url: str) -> None:
    payload, error = fetch_json(api_base_url, "/alerts/active")

    if error:
        st.warning(f"Active alerts are unavailable: {error}")
        return

    items = payload.get("items", [])
    database_configured = payload.get("database_configured", False)

    col1, col2 = st.columns(2)
    col1.metric("Open or acknowledged alerts", len(items))
    col2.metric("Database configured", "Yes" if database_configured else "No")

    if not items:
        st.info("No alerts are active right now. Detection wiring can layer on top of this view next.")
        return

    st.dataframe(items, use_container_width=True, hide_index=True)


def main() -> None:
    st.set_page_config(
        page_title="QuantShield Dashboard",
        layout="wide",
    )

    st.title("QuantShield Operations Dashboard")
    st.caption(
        "Streamlit skeleton for market visibility and security alert triage."
    )

    with st.sidebar:
        st.subheader("Connection")
        api_base_url = st.text_input("FastAPI base URL", value=DEFAULT_API_URL)
        st.caption("Point this at the local FastAPI app or a deployed API endpoint.")

        if st.button("Refresh data", use_container_width=True):
            st.cache_data.clear()

    overview1, overview2, overview3 = st.columns(3)
    overview1.metric("API base URL", api_base_url)
    overview2.metric("Dashboard mode", "Skeleton")
    overview3.metric("Refresh cadence", "30s cache")

    tab_health, tab_market, tab_alerts = st.tabs(
        ["System Health", "Market Feed", "Active Alerts"]
    )

    with tab_health:
        render_health(api_base_url)

    with tab_market:
        render_market_feed(api_base_url)

    with tab_alerts:
        render_active_alerts(api_base_url)


if __name__ == "__main__":
    main()
