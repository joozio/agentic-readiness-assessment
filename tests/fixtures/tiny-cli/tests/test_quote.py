import unittest
from quote import quote


class QuoteTests(unittest.TestCase):
    def test_positive_quote(self):
        self.assertEqual(quote(4), 13)

    def test_nonpositive_rejected(self):
        for value in (0, -1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                quote(value)


if __name__ == '__main__':
    unittest.main()
