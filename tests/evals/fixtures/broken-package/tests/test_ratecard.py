import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "ratecard"))

from pricing import quote


class RateCardTests(unittest.TestCase):
    def test_quote(self):
        self.assertEqual(quote(4, 5, 2), 13)

    def test_source_entry_point(self):
        result = subprocess.run(
            [sys.executable, "src/ratecard/app.py", "4"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "13")


if __name__ == "__main__":
    unittest.main()

