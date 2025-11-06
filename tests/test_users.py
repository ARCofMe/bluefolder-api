import unittest
from users import BlueFolderUsers

class TestUsers(unittest.TestCase):
    def setUp(self):
        self.client = BlueFolderUsers()

    def test_instance(self):
        self.assertIsInstance(self.client, BlueFolderUsers)
