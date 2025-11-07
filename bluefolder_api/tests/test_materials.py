import unittest
from materials import BlueFolderMaterials

class TestMaterials(unittest.TestCase):
    def setUp(self):
        self.client = BlueFolderMaterials()

    def test_instance(self):
        self.assertIsInstance(self.client, BlueFolderMaterials)
