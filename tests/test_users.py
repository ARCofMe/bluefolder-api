import unittest
from ..users import BlueFolderUsers

class TestUsers(unittest.TestCase):
    def setUp(self):
        self.client = BlueFolderUsers(api_key="dummy_key")

    def test_instance(self):
        self.assertIsInstance(self.client, Users)
