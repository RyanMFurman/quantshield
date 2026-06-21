from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import patch

from src.analysis.insider_risk_analyzer import InsiderRiskAnalyzer, run_insider_risk_analysis


def test_insider_risk_analyzer_generates_nvda_finding() -> None:
    now = datetime.now(timezone.utc)
    market_prices = [
        {
            "symbol": "NVDA",
            "price": Decimal("965.00"),
            "prev_close": Decimal("900.00"),
            "volume": 2_500_000,
            "captured_at": now,
        }
    ]
    security_events = [
        {
            "event_type": "ConsoleLogin",
            "result": "Failure",
            "username": "trading-svc",
            "source_ip": "198.51.100.10",
            "raw_payload": {"symbol": "NVDA"},
            "occurred_at": now - timedelta(minutes=3),
        },
        {
            "event_type": "GetObject",
            "result": "Success",
            "username": "trading-svc",
            "source_ip": "198.51.100.10",
            "raw_payload": {"symbol": "NVDA", "bucket": "quant-research"},
            "occurred_at": now - timedelta(minutes=2),
        },
    ]

    findings = run_insider_risk_analysis(market_prices, security_events, now=now)

    assert len(findings) == 1
    assert findings[0]["symbol"] == "NVDA"
    assert findings[0]["affected_user"] == "trading-svc"
    assert findings[0]["risk_score"] >= Decimal("90")
    assert findings[0]["severity"] == "P1"
    assert findings[0]["related_event_count"] == 2
    assert "NVDA showed" in findings[0]["reason"]


def test_insider_risk_analyzer_ignores_normal_market_activity() -> None:
    now = datetime.now(timezone.utc)
    market_prices = [
        {
            "symbol": "MSFT",
            "price": Decimal("404.00"),
            "prev_close": Decimal("400.00"),
            "volume": 100_000,
            "captured_at": now,
        }
    ]
    security_events = [
        {
            "event_type": "ConsoleLogin",
            "result": "Failure",
            "username": "trading-svc",
            "source_ip": "198.51.100.10",
            "raw_payload": {"symbol": "MSFT"},
            "occurred_at": now - timedelta(minutes=3),
        }
    ]

    assert run_insider_risk_analysis(market_prices, security_events, now=now) == []


def test_insider_risk_analyzer_requires_symbol_specific_security_context() -> None:
    now = datetime.now(timezone.utc)
    market_prices = [
        {
            "symbol": "SPY",
            "price": Decimal("525.12"),
            "prev_close": Decimal("524.80"),
            "volume": 48_000_000,
            "captured_at": now,
        }
    ]
    security_events = [
        {
            "event_type": "GetObject",
            "result": "Success",
            "username": "trading-svc",
            "source_ip": "198.51.100.10",
            "raw_payload": {"symbol": "NVDA", "bucket": "quant-research"},
            "occurred_at": now - timedelta(minutes=2),
        }
    ]

    assert run_insider_risk_analysis(market_prices, security_events, now=now) == []


def test_insider_risk_analyzer_requires_symbol_specific_research_data_access() -> None:
    now = datetime.now(timezone.utc)
    market_prices = [
        {
            "symbol": "MSFT",
            "price": Decimal("414.90"),
            "prev_close": Decimal("413.50"),
            "volume": 24_000_000,
            "captured_at": now,
        }
    ]
    security_events = [
        {
            "event_type": "ConsoleLogin",
            "result": "Success",
            "username": "analyst01",
            "source_ip": "203.0.113.40",
            "raw_payload": {"symbol": "MSFT"},
            "occurred_at": now - timedelta(minutes=9),
        }
    ]

    assert run_insider_risk_analysis(market_prices, security_events, now=now) == []


class FakeCursor:
    def __init__(self) -> None:
        self.last_query = ""
        self.inserted_rows = 0

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        _ = (exc_type, exc, tb)

    def execute(self, query: str, params: tuple[object, ...] | None = None) -> None:
        _ = params
        self.last_query = query

    def executemany(self, query: str, params: list[tuple[object, ...]]) -> None:
        self.last_query = query
        self.inserted_rows += len(params)

    def fetchall(self) -> list[dict[str, object]]:
        now = datetime.now(timezone.utc)
        if "FROM market_prices" in self.last_query:
            return [
                {
                    "symbol": "NVDA",
                    "price": Decimal("965.00"),
                    "prev_close": Decimal("900.00"),
                    "volume": 2_500_000,
                    "captured_at": now,
                }
            ]
        if "FROM security_events" in self.last_query:
            return [
                {
                    "event_type": "ConsoleLogin",
                    "source_ip": "198.51.100.10",
                    "username": "trading-svc",
                    "result": "Failure",
                    "raw_payload": {"symbol": "NVDA"},
                    "occurred_at": now - timedelta(minutes=3),
                },
                {
                    "event_type": "GetObject",
                    "source_ip": "198.51.100.10",
                    "username": "trading-svc",
                    "result": "Success",
                    "raw_payload": {"symbol": "NVDA"},
                    "occurred_at": now - timedelta(minutes=2),
                },
            ]
        return []


class FakeConnection:
    def __init__(self) -> None:
        self.cursor_obj = FakeCursor()
        self.committed = False

    def __enter__(self) -> "FakeConnection":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        _ = (exc_type, exc, tb)

    def cursor(self, row_factory: object | None = None) -> FakeCursor:
        _ = row_factory
        return self.cursor_obj

    def commit(self) -> None:
        self.committed = True


def test_insider_risk_db_cycle_inserts_findings() -> None:
    analyzer = InsiderRiskAnalyzer()
    fake_conn = FakeConnection()

    with patch("src.analysis.insider_risk_analyzer.psycopg.connect", return_value=fake_conn):
        result = analyzer.run_db_cycle(db_url="postgresql://placeholder")

    assert result["market_rows_evaluated"] == 1
    assert result["security_events_evaluated"] == 2
    assert result["findings_generated"] == 1
    assert result["findings_inserted"] == 1
    assert fake_conn.cursor_obj.inserted_rows == 1
    assert fake_conn.committed is True
