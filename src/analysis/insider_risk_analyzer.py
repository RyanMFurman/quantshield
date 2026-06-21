from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

import psycopg


class InsiderRiskAnalyzer:
    def __init__(
        self,
        price_move_threshold_pct: Decimal = Decimal("5.0"),
        volume_spike_threshold: int = 1_000_000,
        minimum_score: Decimal = Decimal("70.0"),
    ) -> None:
        self.price_move_threshold_pct = price_move_threshold_pct
        self.volume_spike_threshold = volume_spike_threshold
        self.minimum_score = minimum_score

    def analyze(
        self,
        market_prices: list[dict[str, Any]],
        security_events: list[dict[str, Any]],
        now: datetime | None = None,
    ) -> list[dict[str, Any]]:
        _ = now or datetime.now(timezone.utc)
        findings: list[dict[str, Any]] = []

        for price in self._latest_price_by_symbol(market_prices).values():
            signal = self._market_signal(price)
            if signal is None:
                continue

            symbol = str(price.get("symbol") or "").upper()
            related_events = self._related_security_events(symbol, security_events)
            if not related_events:
                continue

            affected_user = str(related_events[0].get("username") or "unknown")
            source_ip = str(related_events[0].get("source_ip") or "unknown")
            risk_score = self._risk_score(price, related_events)

            if risk_score < self.minimum_score:
                continue

            findings.append(
                {
                    "symbol": symbol,
                    "risk_score": risk_score,
                    "severity": self._severity(risk_score),
                    "affected_user": affected_user,
                    "source_ip": source_ip,
                    "market_signal": signal,
                    "related_event_count": len(related_events),
                    "reason": self._reason(symbol, signal, affected_user, related_events),
                    "status": "OPEN",
                    "detected_at": now or datetime.now(timezone.utc),
                }
            )

        return findings

    def run_db_cycle(self, db_url: str | None = None, window_minutes: int = 60) -> dict[str, int]:
        resolved_db_url = db_url or os.getenv("DATABASE_URL") or os.getenv("DB_URL")
        if not resolved_db_url:
            raise ValueError("DATABASE_URL is required for insider risk analysis")

        now = datetime.now(timezone.utc)
        since = now - timedelta(minutes=window_minutes)

        with psycopg.connect(resolved_db_url) as conn:
            with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
                market_prices = self._fetch_recent_market_prices(cur, since)
                security_events = self._fetch_recent_security_events(cur, since)
                findings = self.analyze(market_prices, security_events, now=now)

                inserted_count = 0
                if findings:
                    inserted_count = self._insert_findings(cur, findings)

            conn.commit()

        return {
            "market_rows_evaluated": len(market_prices),
            "security_events_evaluated": len(security_events),
            "findings_generated": len(findings),
            "findings_inserted": inserted_count,
        }

    @staticmethod
    def _latest_price_by_symbol(
        market_prices: list[dict[str, Any]]
    ) -> dict[str, dict[str, Any]]:
        latest: dict[str, dict[str, Any]] = {}

        for row in market_prices:
            symbol = str(row.get("symbol") or "").upper()
            if not symbol:
                continue

            captured_at = row.get("captured_at")
            current_latest = latest.get(symbol)

            if current_latest is None:
                latest[symbol] = row
                continue

            current_captured_at = current_latest.get("captured_at")
            if isinstance(captured_at, datetime) and isinstance(current_captured_at, datetime):
                if captured_at > current_captured_at:
                    latest[symbol] = row

        return latest

    def _market_signal(self, price: dict[str, Any]) -> str | None:
        price_value = self._decimal(price.get("price"))
        prev_close = self._decimal(price.get("prev_close"))
        volume = int(price.get("volume") or 0)

        if price_value is None or prev_close is None or prev_close == 0:
            return None

        move_pct = ((price_value - prev_close) / prev_close) * Decimal("100")
        absolute_move_pct = abs(move_pct)

        if absolute_move_pct >= self.price_move_threshold_pct and volume >= self.volume_spike_threshold:
            return f"{absolute_move_pct.quantize(Decimal('0.01'))}% price move with volume spike"

        if absolute_move_pct >= self.price_move_threshold_pct:
            return f"{absolute_move_pct.quantize(Decimal('0.01'))}% price move"

        if volume >= self.volume_spike_threshold:
            return "volume spike"

        return None

    @staticmethod
    def _related_security_events(
        symbol: str, security_events: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        suspicious_types = {"ConsoleLogin", "GetObject"}

        related: list[dict[str, Any]] = []
        for event in security_events:
            event_type = str(event.get("event_type") or "")
            if event_type not in suspicious_types:
                continue

            payload = event.get("raw_payload")
            payload_symbol = ""
            if isinstance(payload, dict):
                payload_symbol = str(payload.get("symbol") or payload.get("ticker") or "")

            symbol_matches = payload_symbol.upper() == symbol

            if symbol_matches:
                related.append(event)

        return related

    def _risk_score(
        self, price: dict[str, Any], related_events: list[dict[str, Any]]
    ) -> Decimal:
        score = Decimal("45")

        signal = self._market_signal(price) or ""
        if "price move" in signal:
            score += Decimal("20")
        if "volume spike" in signal:
            score += Decimal("15")

        event_types = {str(event.get("event_type") or "") for event in related_events}
        if "ConsoleLogin" in event_types:
            score += Decimal("10")
        if "GetObject" in event_types:
            score += Decimal("10")
        if event_types.intersection({"AttachRolePolicy", "PutUserPolicy", "CreatePolicyVersion"}):
            score += Decimal("10")

        return min(score, Decimal("100"))

    @staticmethod
    def _severity(score: Decimal) -> str:
        if score >= Decimal("90"):
            return "P1"
        if score >= Decimal("75"):
            return "P2"
        return "P3"

    @staticmethod
    def _reason(
        symbol: str,
        signal: str,
        affected_user: str,
        related_events: list[dict[str, Any]],
    ) -> str:
        event_names = sorted({str(event.get("event_type") or "unknown") for event in related_events})
        return (
            f"{symbol} showed {signal} while {affected_user} had related security "
            f"activity in the same window: {', '.join(event_names)}"
        )

    @staticmethod
    def _decimal(value: Any) -> Decimal | None:
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except Exception:
            return None

    @staticmethod
    def _fetch_recent_market_prices(cur: Any, since: datetime) -> list[dict[str, Any]]:
        cur.execute(
            """
            SELECT symbol, price, volume, prev_close, captured_at
            FROM market_prices
            WHERE captured_at >= %s
            ORDER BY symbol, captured_at DESC
            """,
            (since,),
        )
        return [dict(row) for row in cur.fetchall()]

    @staticmethod
    def _fetch_recent_security_events(cur: Any, since: datetime) -> list[dict[str, Any]]:
        cur.execute(
            """
            SELECT event_type, source_ip::text, username, result, raw_payload, occurred_at
            FROM security_events
            WHERE occurred_at >= %s
            ORDER BY occurred_at DESC
            """,
            (since,),
        )
        return [dict(row) for row in cur.fetchall()]

    @staticmethod
    def _insert_findings(cur: Any, findings: list[dict[str, Any]]) -> int:
        payload = [
            (
                finding["symbol"],
                finding["risk_score"],
                finding["severity"],
                finding.get("affected_user"),
                finding.get("source_ip"),
                finding.get("market_signal"),
                finding.get("related_event_count", 0),
                finding["reason"],
                finding.get("status", "OPEN"),
                finding.get("detected_at", datetime.now(timezone.utc)),
            )
            for finding in findings
        ]

        cur.executemany(
            """
            INSERT INTO insider_risk_findings (
                symbol, risk_score, severity, affected_user, source_ip,
                market_signal, related_event_count, reason, status, detected_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            payload,
        )
        return len(payload)


def run_insider_risk_analysis(
    market_prices: list[dict[str, Any]],
    security_events: list[dict[str, Any]],
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    analyzer = InsiderRiskAnalyzer()
    return analyzer.analyze(market_prices, security_events, now=now)
