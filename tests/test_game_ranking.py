import os
import unittest

os.environ.setdefault("ITAD_API_KEY", "test-key")

from app.scrapers.game_scraper import rank_games, result_order_key


class GameRankingTest(unittest.TestCase):
    def test_popular_api_result_stays_above_cheaper_indie_result(self):
        games = [
            {"id": "cyberpunk-2077", "title": "Cyberpunk 2077", "type": "game"},
            {"id": "indie", "title": "Cyberpunk Indie Adventure", "type": "game"},
        ]

        ranked_games = rank_games(games, "Cyberpunk")
        ranked_games[0]["lowest_price"] = 59.99
        ranked_games[1]["lowest_price"] = 1.99
        ranked_games.sort(key=result_order_key)

        self.assertEqual("Cyberpunk 2077", ranked_games[0]["title"])

    def test_price_is_secondary_for_same_relevance(self):
        games = [
            {"id": "expensive", "title": "Cyberpunk Alpha", "type": "game"},
            {"id": "cheap", "title": "Cyberpunk Beta", "type": "game"},
        ]

        ranked_games = rank_games(games, "Cyberpunk")
        for game in ranked_games:
            game["_relevance_score"] = 100
        ranked_games[0]["lowest_price"] = 19.99
        ranked_games[1]["lowest_price"] = 9.99
        ranked_games.sort(key=result_order_key)

        self.assertEqual("Cyberpunk Beta", ranked_games[0]["title"])


if __name__ == "__main__":
    unittest.main()
