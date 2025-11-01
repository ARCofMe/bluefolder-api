import unittest
from users import Users

class TestUsers(unittest.TestCase):
    def setUp(self):
        self.client = Users(api_key="dummy_key")

    def test_instance(self):
        self.assertIsInstance(self.client, Users)
