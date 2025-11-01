import unittest
from customers import Customers

class TestCustomers(unittest.TestCase):
    def setUp(self):
        self.client = Customers(api_key="dummy_key")

    def test_instance(self):
        self.assertIsInstance(self.client, Customers)
