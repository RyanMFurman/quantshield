from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from pprint import pprint

# Add repository root to import path when running this script directly.
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.detection.detection_engine import run_detection


def build_demo_events() -> list[dict[str, object]]:
    now = datetime.now(timezone.utc)
    events: list[dict[str, object]] = []

    # Simulate 6 failed login attempts from same user/IP inside 15-minute window.
    for minutes_ago in [1, 2, 3, 4, 5, 6]:
        events.append(
            {
                "event_type": "ConsoleLogin",
                "result": "Failure",
                "username": "trading-svc",
                "source_ip": "198.51.100.10",
                "occurred_at": now - timedelta(minutes=minutes_ago),
            }
        )

    # Noise event that should not trigger the brute-force rule.
    events.append(
        {
            "event_type": "ConsoleLogin",
            "result": "Success",
            "username": "trading-svc",
            "source_ip": "198.51.100.10",
            "occurred_at": now - timedelta(minutes=1),
        }
    )

    return events


if __name__ == "__main__":
    demo_events = build_demo_events()
    generated_alerts = run_detection(demo_events)

    print(f"Generated alerts: {len(generated_alerts)}")
    pprint(generated_alerts)
