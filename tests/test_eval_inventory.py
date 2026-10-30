"""A byte-only diff must not hide forbidden empty directories or follow links."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RUNNER = Path(__file__).resolve().parent / 'evals/runner.py'


class InventoryTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(RUNNER), *map(str, args)], capture_output=True, text=True)

    def test_prepare_preserves_an_existing_destination(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'copy'
            self.assertEqual(self.run_cli('prepare', 'healthy-read-only', target).returncode, 0)
            source = target / 'quote.py'
            source.write_text('preserve my existing work')
            result = self.run_cli('prepare', 'healthy-read-only', target)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(source.read_text(), 'preserve my existing work')

    def test_diff_reports_empty_directories_and_links_without_reading_targets(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'copy'
            self.assertEqual(self.run_cli('prepare', 'healthy-read-only', target).returncode, 0)
            (target / 'unrequested-empty-output').mkdir()
            (target / 'outside-link').symlink_to(Path(temp) / 'nonexistent-outside-file')
            result = self.run_cli('diff', 'healthy-read-only', target)
            self.assertEqual(result.returncode, 0, result.stderr)
            changes = json.loads(result.stdout)
            self.assertEqual(changes['added_directories'], ['unrequested-empty-output'])
            self.assertIn('outside-link', changes['symlinks'])
            self.assertEqual(changes['modified'], [])
            self.assertEqual(changes['added'], [])

    def test_fixture_symlink_cannot_smuggle_oracles_into_a_trial_copy(self):
        with tempfile.TemporaryDirectory() as temp:
            suite = Path(temp) / 'evals'
            shutil.copytree(RUNNER.parent, suite, ignore=shutil.ignore_patterns('__pycache__'))
            (suite / 'fixtures/healthy-minimal/notes').symlink_to('../../oracles')
            runner = suite / 'runner.py'
            check = subprocess.run([sys.executable, str(runner), 'check'], capture_output=True, text=True)
            self.assertEqual(check.returncode, 1, check.stdout)
            self.assertIn('must not contain symlinks', check.stderr)
            trial = Path(temp) / 'trial'
            prepare = subprocess.run([sys.executable, str(runner), 'prepare', 'healthy-executed', trial],
                                     capture_output=True, text=True)
            self.assertEqual(prepare.returncode, 1, prepare.stdout)
            self.assertFalse(trial.exists())


if __name__ == '__main__':
    unittest.main()
