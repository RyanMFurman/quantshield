from __future__ import annotations

import sys
from pathlib import Path
from pprint import pprint

# Add repository root to import path when running this script directly.
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.analysis.insider_risk_analyzer import InsiderRiskAnalyzer


if __name__ == "__main__":
    result = InsiderRiskAnalyzer().run_db_cycle()
    pprint(result)
