import os
import unittest

os.environ.setdefault("ITAD_API_KEY", "test-key")

from app import app


class WishlistPageTest(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_wishlist_page_is_available(self):
        response = self.client.get("/wishlist")

        self.assertEqual(200, response.status_code)
        self.assertIn(b'data-wishlist-list', response.data)
        self.assertIn(b'Wishlist', response.data)

    def test_navigation_exposes_wishlist_on_homepage(self):
        response = self.client.get("/")

        self.assertIn(b'href="/wishlist"', response.data)
        self.assertIn(b'data-wishlist-count', response.data)


if __name__ == "__main__":
    unittest.main()
