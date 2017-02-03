import unittest

from app import create_app

HEARTBEAT_ENDPOINT = '/api/v0/status/'

class APIBasicsTestCase(unittest.TestCase):

    def setUp(self):
        """
        this is my doc string
        """
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(self.app is None)

    def test_heartbeat(self):
        response = self.client.get(HEARTBEAT_ENDPOINT)
        self.assertEqual(response.status_code, 200)
