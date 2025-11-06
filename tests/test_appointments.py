import unittest
from appointments import BlueFolderAppointments

class TestAppointments(unittest.TestCase):
    def setUp(self):
        self.client = BlueFolderAppointments()

    def test_instance(self):
        self.assertIsInstance(self.client, BlueFolderAppointments)
