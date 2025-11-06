import unittest
from customers import BlueFolderCustomers

class TestCustomers(unittest.TestCase):
    def setUp(self):
        self.client = BlueFolderCustomers()

    def test_instance(self):
        self.assertIsInstance(self.client, BlueFolderCustomers)
