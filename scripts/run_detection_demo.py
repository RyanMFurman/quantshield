from __future__ import annotations

import sys
from argparse import ArgumentParser
from pathlib import Path
from pprint import pprint

# Add repository root to import path when running this script directly.
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.detection.detection_engine import run_detection
from src.ingestion.scenarios import build_scenario, scenario_names


if __name__ == "__main__":
    parser = ArgumentParser(description="Run QuantShield synthetic detection scenarios.")
    parser.add_argument(
        "--scenario",
        choices=scenario_names(),
        default="quiet_day",
        help="Synthetic scenario to evaluate. Defaults to quiet_day.",
    )
    args = parser.parse_args()

    scenario = build_scenario(args.scenario)
    generated_alerts = run_detection(scenario.events)

    print(f"Scenario: {scenario.name}")
    print(f"Description: {scenario.description}")
    print(f"Events evaluated: {len(scenario.events)}")
    print(f"Generated alerts: {len(generated_alerts)}")
    pprint(generated_alerts)
