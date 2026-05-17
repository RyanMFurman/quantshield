from __future__ import annotations

import json

from src.detection.detection_engine import DetectionEngine


if __name__ == "__main__":
    engine = DetectionEngine()
    result = engine.run_db_cycle()
    print(json.dumps(result, indent=2))
