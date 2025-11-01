import unittest
from materials import Materials

class TestMaterials(unittest.TestCase):
    def setUp(self):
        self.client = Materials(api_key="dummy_key")

    def test_instance(self):
        self.assertIsInstance(self.client, Materials)
