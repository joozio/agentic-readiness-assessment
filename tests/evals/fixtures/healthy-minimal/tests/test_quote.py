import unittest

from quote import quote


class QuoteTests(unittest.TestCase):
    def test_one_kilogram(self):
        self.assertEqual(quote(1), 7)

    def test_four_kilograms(self):
        self.assertEqual(quote(4), 13)

    def test_nonpositive_weight_is_rejected(self):
        for value in (0, -1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                quote(value)


if __name__ == "__main__":
    unittest.main()

