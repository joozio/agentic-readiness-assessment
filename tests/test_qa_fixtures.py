"""Check that QA fixtures expose the advertised behavior despite green unit suites."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests/change-qa/fixtures'


class QAFixtureTests(unittest.TestCase):
    def run_check(self, source, arguments):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / 'repo'
            shutil.copytree(source, candidate, ignore=shutil.ignore_patterns('__pycache__'))
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
            return subprocess.run([sys.executable, '-B', *arguments], cwd=candidate,
                                  env=env, capture_output=True, text=True, timeout=10)

    def test_all_supplied_suites_are_green(self):
        expected = json.loads((FIXTURES.parent / 'fixture-hashes.json').read_text())
        actual = {str(path.relative_to(FIXTURES)): hashlib.sha256(path.read_bytes()).hexdigest()
                  for path in FIXTURES.rglob('*') if path.is_file()}
        self.assertEqual(actual, expected)
        for pair in FIXTURES.iterdir():
            for version in ('baseline', 'candidate'):
                with self.subTest(case=pair.name, version=version):
                    result = self.run_check(pair / version,
                                            ['-m', 'unittest', 'discover', '-s', 'tests'])
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn('OK', result.stderr)

    def test_shipping_boundary_distinguishes_incomplete_and_correct_changes(self):
        for group, boundary in [('shipping-boundary', '500'), ('shipping-correct', '0')]:
            for total, expected in [('4999', '500'), ('5000', boundary), ('5001', '0')]:
                with self.subTest(case=group, total=total):
                    result = self.run_check(FIXTURES / group / 'candidate', ['shipping.py', total])
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout.strip(), expected)
            rejected = self.run_check(FIXTURES / group / 'candidate', ['shipping.py', '-1'])
            self.assertNotEqual(rejected.returncode, 0)
            baseline = self.run_check(FIXTURES / group / 'baseline', ['shipping.py', '5001'])
            self.assertEqual(baseline.stdout.strip(), '500')

    def test_checkout_route_bypasses_correct_service_guard(self):
        code = '''import io, json, app
try:
    app.create_order(-1)
except ValueError:
    print("service rejects")
status = []
response = app.application({"PATH_INFO": "/checkout", "REQUEST_METHOD": "POST",
    "wsgi.input": io.BytesIO(b'{"quantity": -1}')}, lambda s, h: status.append(s))
print(json.dumps({"status": status[0], "body": json.loads(b"".join(response)), "orders": app.orders}))
'''
        result = self.run_check(FIXTURES / 'checkout-route/candidate', ['-c', code])
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        self.assertEqual(lines[0], 'service rejects')
        self.assertEqual(json.loads(lines[1]), {'status': '201 Created',
                         'body': {'quantity': -1}, 'orders': [{'quantity': -1}]})

    def test_qa_folder_is_self_contained(self):
        source = ROOT / 'skills/change-qa'
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / source.name
            shutil.copytree(source, target)
            self.assertTrue((target / 'references/report.md').is_file())
            for name in ('LICENSE', 'NOTICE'):
                self.assertEqual((target / name).read_bytes(), (ROOT / name).read_bytes())


if __name__ == '__main__':
    unittest.main()
