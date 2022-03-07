import unittest
from app import app


class TestApp(unittest.TestCase):

    def test_given_app_running_index_endpoint_returns_200(self):
        with app.test_client() as client:
            response = client.get("/")
            assert response._status_code == 200



