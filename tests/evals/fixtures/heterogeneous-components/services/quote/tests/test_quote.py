import unittest

from quote import quote


class QuoteTests(unittest.TestCase):
    def test_quote_shape_and_value(self):
        self.assertEqual(quote(4), {"currency": "USD", "amount": 13})

    def test_invalid_weight(self):
        with self.assertRaises(ValueError):
            quote(0)


if __name__ == "__main__":
    unittest.main()

