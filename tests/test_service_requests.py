import unittest
from service_requests import ServiceRequests

class TestServiceRequests(unittest.TestCase):
    def setUp(self):
        self.client = ServiceRequests(api_key="dummy_key")

    def test_instance(self):
        self.assertIsInstance(self.client, ServiceRequests)
