import unittest
from appointments import Appointments

class TestAppointments(unittest.TestCase):
    def setUp(self):
        self.client = Appointments(api_key="dummy_key")

    def test_instance(self):
        self.assertIsInstance(self.client, Appointments)
