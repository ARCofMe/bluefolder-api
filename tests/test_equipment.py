import unittest
from equipment import BlueFolderEquipment

class TestEquipment(unittest.TestCase):
    def setUp(self):
        self.client = BlueFolderEquipment()

    def test_instance(self):
        self.assertIsInstance(self.client, BlueFolderEquipment)
