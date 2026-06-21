from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from pprint import pprint

# Add repository root to import path when running this script directly.
sys.path.append(str(Path(__file__).resolve().parents[1]))

import psycopg
from psycopg.types.json import Jsonb

from src.analysis.insider_risk_analyzer import InsiderRiskAnalyzer
from src.detection.detection_engine import DetectionEngine


MARKET_ROWS = [
    ("SPY", 525.1200, 48_000_000, 524.8000, 8),
    ("QQQ", 449.3300, 36_000_000, 448.9000, 7),
    ("AAPL", 189.4500, 42_000_000, 188.9500, 6),
    ("MSFT", 414.9000, 24_000_000, 413.5000, 5),
    ("NVDA", 965.0000, 2_500_000, 900.0000, 4),
]

SECURITY_EVENTS = [
    (
        "11111111-1111-4111-8111-111111111111",
        "ConsoleLogin",
        "198.51.100.10",
        "trading-svc",
        "Mozilla/5.0",
        "Failure",
        {"count": 1, "symbol": "NVDA", "demo_batch": "live-demo"},
        6,
    ),
    (
        "22222222-2222-4222-8222-222222222222",
        "ConsoleLogin",
        "198.51.100.10",
        "trading-svc",
        "Mozilla/5.0",
        "Failure",
        {"count": 2, "symbol": "NVDA", "demo_batch": "live-demo"},
        5,
    ),
    (
        "33333333-3333-4333-8333-333333333333",
        "ConsoleLogin",
        "198.51.100.10",
        "trading-svc",
        "Mozilla/5.0",
        "Failure",
        {"count": 3, "symbol": "NVDA", "demo_batch": "live-demo"},
        4,
    ),
    (
        "44444444-4444-4444-8444-444444444444",
        "ConsoleLogin",
        "198.51.100.10",
        "trading-svc",
        "Mozilla/5.0",
        "Failure",
        {"count": 4, "symbol": "NVDA", "demo_batch": "live-demo"},
        3,
    ),
    (
        "55555555-5555-4555-8555-555555555555",
        "ConsoleLogin",
        "198.51.100.10",
        "trading-svc",
        "Mozilla/5.0",
        "Failure",
        {"count": 5, "symbol": "NVDA", "demo_batch": "live-demo"},
        2,
    ),
    (
        "66666666-6666-4666-8666-666666666666",
        "ConsoleLogin",
        "198.51.100.10",
        "trading-svc",
        "Mozilla/5.0",
        "Failure",
        {"count": 6, "symbol": "NVDA", "demo_batch": "live-demo"},
        1,
    ),
    (
        "77777777-7777-4777-8777-777777777777",
        "GetObject",
        "198.51.100.10",
        "trading-svc",
        "aws-cli/2.15",
        "Success",
        {
            "bucket": "quant-research",
            "object": "nvda-model-inputs.csv",
            "symbol": "NVDA",
            "demo_batch": "live-demo",
        },
        2,
    ),
    (
        "88888888-8888-4888-8888-888888888888",
        "ConsoleLogin",
        "203.0.113.40",
        "analyst01",
        "Mozilla/5.0",
        "Success",
        {"symbol": "MSFT", "demo_batch": "live-demo-noise"},
        9,
    ),
]


def seed_demo_data(db_url: str) -> dict[str, int]:
    now = datetime.now(timezone.utc)

    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM market_prices
                WHERE symbol = ANY(%s)
                  AND captured_at < NOW() - INTERVAL '2 hours'
                """,
                ([row[0] for row in MARKET_ROWS],),
            )
            cur.execute(
                """
                DELETE FROM insider_risk_findings
                WHERE symbol = 'NVDA'
                  AND status IN ('OPEN', 'ACK')
                  AND reason LIKE 'NVDA showed%%'
                """
            )
            cur.executemany(
                """
                INSERT INTO market_prices (symbol, price, volume, prev_close, captured_at)
                VALUES (%s, %s, %s, %s, %s)
                """,
                [
                    (symbol, price, volume, prev_close, now - timedelta(minutes=minutes_ago))
                    for symbol, price, volume, prev_close, minutes_ago in MARKET_ROWS
                ],
            )
            cur.executemany(
                """
                INSERT INTO security_events (
                    event_id, event_type, source_ip, username, user_agent,
                    result, raw_payload, occurred_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (event_id) DO UPDATE SET
                    source_ip = EXCLUDED.source_ip,
                    username = EXCLUDED.username,
                    user_agent = EXCLUDED.user_agent,
                    result = EXCLUDED.result,
                    raw_payload = EXCLUDED.raw_payload,
                    occurred_at = EXCLUDED.occurred_at
                """,
                [
                    (
                        event_id,
                        event_type,
                        source_ip,
                        username,
                        user_agent,
                        result,
                        Jsonb(raw_payload),
                        now - timedelta(minutes=minutes_ago),
                    )
                    for (
                        event_id,
                        event_type,
                        source_ip,
                        username,
                        user_agent,
                        result,
                        raw_payload,
                        minutes_ago,
                    ) in SECURITY_EVENTS
                ],
            )
        conn.commit()

    detection_result = DetectionEngine().run_db_cycle(db_url=db_url, window_minutes=30)
    insider_result = InsiderRiskAnalyzer().run_db_cycle(db_url=db_url, window_minutes=30)

    return {
        "market_rows_inserted": len(MARKET_ROWS),
        "security_events_upserted": len(SECURITY_EVENTS),
        "alerts_inserted": detection_result["alerts_inserted"],
        "insider_findings_inserted": insider_result["findings_inserted"],
    }


if __name__ == "__main__":
    database_url = os.getenv("DATABASE_URL") or os.getenv("DB_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is required to seed live demo data")

    pprint(seed_demo_data(database_url))
