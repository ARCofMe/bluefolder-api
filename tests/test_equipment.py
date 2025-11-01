import unittest
from equipment import Equipment

class TestEquipment(unittest.TestCase):
    def setUp(self):
        self.client = Equipment(api_key="dummy_key")

    def test_instance(self):
        self.assertIsInstance(self.client, Equipment)
