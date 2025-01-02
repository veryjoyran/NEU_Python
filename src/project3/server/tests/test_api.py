# tests/test_api.py
import unittest
import requests

class TestAPI(unittest.TestCase):
    BASE_URL = "http://localhost:5000/api"

    def test_scrape(self):
        payload = {"city_code": "bj", "pages": 1}
        response = requests.post(f"{self.BASE_URL}/scrape", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("data_count", response.json())

    def test_get_houses(self):
        response = requests.get(f"{self.BASE_URL}/houses")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_statistics(self):
        response = requests.get(f"{self.BASE_URL}/statistics")
        self.assertEqual(response.status_code, 200)
        self.assertIn("total", response.json())
        self.assertIn("statistics", response.json())

if __name__ == '__main__':
    unittest.main()
