import unittest
from app import create_order

class OrderTests(unittest.TestCase):
    def test_valid_order(self):
        self.assertEqual(create_order(2), {"quantity": 2})
