import unittest
from tasks import Tasks

class TestTasks(unittest.TestCase):
    def setUp(self):
        self.client = Tasks(api_key="dummy_key")

    def test_instance(self):
        self.assertIsInstance(self.client, Tasks)
