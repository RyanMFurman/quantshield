from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from src.api.main import app


class ApiRoutesTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

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


if __name__ == "__main__":
    unittest.main()
