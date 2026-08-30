import os
import unittest
from unittest.mock import patch

os.environ.setdefault("ITAD_API_KEY", "test-key")

from app import app
from app.services.cover_fallback import find_fallback_cover


class CoverFallbackServiceTest(unittest.TestCase):
    @patch("app.services.cover_fallback._request_session.get")
    def test_prefers_exact_title_match(self, mock_get):
        mock_get.return_value.raise_for_status.return_value = None
        mock_get.return_value.json.return_value = {"items": [
            {"id": 317400, "name": "Portal Stories"},
            {"id": 400, "name": "Portal"},
        ]}

        self.assertEqual(
            "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/400/library_600x900.jpg",
            find_fallback_cover("Portal"),
        )

    @patch("app.services.cover_fallback._request_session.get")
    def test_uses_first_result_when_there_is_no_exact_match(self, mock_get):
        mock_get.return_value.raise_for_status.return_value = None
        mock_get.return_value.json.return_value = {"items": [
            {"id": 220, "name": "Half-Life 2"},
        ]}

        self.assertEqual(
            "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/220/library_600x900.jpg",
            find_fallback_cover("Half Life Two"),
        )


class CoverFallbackEndpointTest(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    @patch("app.routes.find_fallback_cover", return_value="https://img.test/game.jpg")
    def test_returns_alternative_cover(self, _mock_find):
        response = self.client.get("/api/game-cover?title=Game%20Title")

        self.assertEqual(200, response.status_code)
        self.assertEqual("https://img.test/game.jpg", response.json["cover_url"])

    def test_rejects_missing_title(self):
        response = self.client.get("/api/game-cover")

        self.assertEqual(400, response.status_code)


if __name__ == "__main__":
    unittest.main()
