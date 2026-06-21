from __future__ import annotations

import os
import sys
from argparse import ArgumentParser
from datetime import datetime, timedelta, timezone
from pathlib import Path
from pprint import pprint

# Add repository root to import path when running this script directly.
sys.path.append(str(Path(__file__).resolve().parents[1]))

import psycopg
from psycopg.types.json import Jsonb

from src.analysis.insider_risk_analyzer import InsiderRiskAnalyzer
from src.detection.detection_engine import DetectionEngine
from src.ingestion.scenarios import build_scenario, scenario_names


MARKET_ROWS = [
    ("SPY", 525.1200, 48_000_000, 524.8000, 8),
    ("QQQ", 449.3300, 36_000_000, 448.9000, 7),
    ("AAPL", 189.4500, 42_000_000, 188.9500, 6),
    ("MSFT", 414.9000, 24_000_000, 413.5000, 5),
    ("NVDA", 965.0000, 2_500_000, 900.0000, 4),
]

def seed_demo_data(db_url: str, scenario_name: str = "quiet_day") -> dict[str, int | str]:
    now = datetime.now(timezone.utc)
    scenario = build_scenario(scenario_name, now=now)

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
                WHERE status IN ('OPEN', 'ACK')
                  AND affected_user IN ('trading-svc', 'quant-analyst', 'analyst01', 'research-analyst')
                """
            )
            cur.execute(
                """
                DELETE FROM alerts
                WHERE status IN ('OPEN', 'ACK')
                  AND rule_id IN (
                    'BRUTE_FORCE_001',
                    'IAM_ACCESS_KEY_001',
                    'IAM_ADMIN_POLICY_001',
                    'IAM_MFA_DISABLED_001',
                    'IAM_PRIV_ROLE_001',
                    'IAM_ROOT_LOGIN_001',
                    'PRIV_ESC_001',
                    'DATA_EXFIL_001'
                  )
                """
            )
            cur.execute(
                """
                DELETE FROM security_events
                WHERE raw_payload ->> 'scenario' = ANY(%s)
                """,
                (scenario_names(),),
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
                        event["event_id"],
                        event["event_type"],
                        event["source_ip"],
                        event["username"],
                        event["user_agent"],
                        event["result"],
                        Jsonb(event["raw_payload"]),
                        event["occurred_at"],
                    )
                    for event in scenario.events
                ],
            )
        conn.commit()

    detection_result = DetectionEngine().run_db_cycle(db_url=db_url, window_minutes=30)
    insider_result = InsiderRiskAnalyzer().run_db_cycle(db_url=db_url, window_minutes=30)

    return {
        "market_rows_inserted": len(MARKET_ROWS),
        "security_events_upserted": len(scenario.events),
        "alerts_inserted": detection_result["alerts_inserted"],
        "insider_findings_inserted": insider_result["findings_inserted"],
        "scenario": scenario.name,
    }


if __name__ == "__main__":
    parser = ArgumentParser(description="Seed QuantShield demo data.")
    parser.add_argument(
        "--scenario",
        choices=scenario_names(),
        default=os.getenv("QUANTSHIELD_SCENARIO", "quiet_day"),
        help="Scenario to seed. Defaults to QUANTSHIELD_SCENARIO or quiet_day.",
    )
    args = parser.parse_args()

    database_url = os.getenv("DATABASE_URL") or os.getenv("DB_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is required to seed live demo data")

    pprint(seed_demo_data(database_url, scenario_name=args.scenario))
