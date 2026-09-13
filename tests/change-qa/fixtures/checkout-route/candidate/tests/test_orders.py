import unittest
from app import create_order

class OrderTests(unittest.TestCase):
    def test_valid_order(self):
        self.assertEqual(create_order(2), {"quantity": 2})
    def test_negative_quantity(self):
        with self.assertRaises(ValueError):
            create_order(-1)
