import unittest
from shipping import shipping

class ShippingTests(unittest.TestCase):
    def test_small_order(self):
        self.assertEqual(shipping(2000), 500)
    def test_large_order(self):
        self.assertEqual(shipping(6000), 0)
    def test_negative(self):
        with self.assertRaises(ValueError):
            shipping(-1)
