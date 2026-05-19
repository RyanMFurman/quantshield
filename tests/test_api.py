from __future__ import annotations

import os
import unittest

from fastapi.testclient import TestClient

from src.api.config import get_settings
from src.api.main import app


class ApiRoutesTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def setUp(self) -> None:
        self.original_database_url = os.environ.pop("DATABASE_URL", None)
        get_settings.cache_clear()

    def tearDown(self) -> None:
        if self.original_database_url is not None:
            os.environ["DATABASE_URL"] = self.original_database_url
        get_settings.cache_clear()

    def test_health_returns_service_metadata(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_market_latest_returns_empty_state_without_database(self) -> None:
        response = self.client.get("/market/latest")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"database_configured": False, "items": []},
        )

    def test_alerts_active_returns_empty_state_without_database(self) -> None:
        response = self.client.get("/alerts/active")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"database_configured": False, "items": []},
        )

    def test_recent_events_returns_empty_state_without_database(self) -> None:
        response = self.client.get("/api/v1/events/recent")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"database_configured": False, "items": []},
        )

    def test_detection_summary_returns_empty_state_without_database(self) -> None:
        response = self.client.get("/api/v1/detections/summary")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"database_configured": False, "items": []},
        )


if __name__ == "__main__":
    unittest.main()
