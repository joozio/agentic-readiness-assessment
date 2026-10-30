"""Pin the eval runner checks that decide whether a trial is graded fairly."""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SUITE = Path(__file__).resolve().parent / 'evals'


class CopiedSuite:
    """A disposable suite copy, so manifest and fixture edits never touch the repo."""

    def __enter__(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'evals'
        shutil.copytree(SUITE, self.root, ignore=shutil.ignore_patterns('__pycache__'))
        spec = importlib.util.spec_from_file_location('copied_eval_runner', self.root / 'runner.py')
        self.runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.runner)
        return self

    def __exit__(self, *exc):
        self.temp.cleanup()

    def cli(self, *args):
        return subprocess.run([sys.executable, str(self.root / 'runner.py'), *map(str, args)],
                              capture_output=True, text=True)

    def edit_manifest(self, change):
        data = json.loads((self.root / 'cases.json').read_text(encoding='utf-8'))
        change(data['cases'])
        (self.root / 'cases.json').write_text(json.dumps(data), encoding='utf-8')

    def rehash(self):
        integrity = self.root / 'fixture-integrity.json'
        data = json.loads(integrity.read_text(encoding='utf-8'))
        data['sha256'] = self.runner.tree(self.runner.FIXTURES)
        integrity.write_text(json.dumps(data), encoding='utf-8')


class ManifestTests(unittest.TestCase):
    def assert_rejected(self, change, message):
        with CopiedSuite() as suite:
            suite.edit_manifest(change)
            with self.assertRaises(suite.runner.CheckFailure) as raised:
                suite.runner.validate_manifest()
            self.assertIn(message, str(raised.exception))

    def test_committed_manifest_is_valid(self):
        with CopiedSuite() as suite:
            suite.runner.validate_manifest()

    def test_fixture_paths_cannot_escape_the_fixture_directory(self):
        for unsafe in ('/tmp/fixtures/x', 'fixtures/../oracles', 'oracles', '../fixtures/docs-only'):
            with self.subTest(fixture=unsafe):
                self.assert_rejected(lambda cases: cases[0].update(fixture=unsafe),
                                     'unsafe fixture path')

    def test_forbidden_operations_cannot_be_permitted(self):
        for operation in ('install', 'network', 'credentials', 'live_services'):
            with self.subTest(operation=operation):
                self.assert_rejected(
                    lambda cases: cases[0]['permitted_operations'].update({operation: True}),
                    'permits ' + operation)

    def test_permission_set_must_be_complete(self):
        self.assert_rejected(lambda cases: cases[0]['permitted_operations'].pop('network'),
                             'incomplete permissions')

    def test_case_ids_must_be_unique(self):
        self.assert_rejected(lambda cases: cases[1].update(id=cases[0]['id']), 'unique')

    def test_grading_criteria_are_required(self):
        self.assert_rejected(lambda cases: cases[0]['expected'].update(must_not=[]),
                             'must/must_not')
        self.assert_rejected(lambda cases: cases[0]['expected'].pop('observable_outcomes'),
                             'observable outcomes')


class IntegrityTests(unittest.TestCase):
    def test_any_fixture_byte_change_addition_or_removal_is_detected(self):
        edits = {
            'changed': lambda root: (root / 'healthy-minimal/quote.py').write_bytes(
                (root / 'healthy-minimal/quote.py').read_bytes() + b' '),
            'added': lambda root: (root / 'healthy-minimal/extra.txt').write_text('x'),
            'missing': lambda root: (root / 'docs-only/CONTRIBUTING.md').unlink(),
        }
        for kind, edit in edits.items():
            with self.subTest(kind=kind), CopiedSuite() as suite:
                edit(suite.runner.FIXTURES)
                with self.assertRaises(suite.runner.CheckFailure) as raised:
                    suite.runner.validate_integrity()
                self.assertIn(kind + '=', str(raised.exception))
                self.assertNotIn(kind + '=[]', str(raised.exception))

    def test_oracle_like_names_are_rejected_even_with_updated_hashes(self):
        with CopiedSuite() as suite:
            (suite.runner.FIXTURES / 'healthy-minimal/expected-output.txt').write_text('7\n')
            suite.rehash()
            with self.assertRaises(suite.runner.CheckFailure) as raised:
                suite.runner.validate_integrity()
            self.assertIn('oracle-like path', str(raised.exception))


class TrialCopyTests(unittest.TestCase):
    def test_prepare_copies_only_the_fixture_and_diff_of_it_is_empty(self):
        with CopiedSuite() as suite, tempfile.TemporaryDirectory() as temp:
            trial = Path(temp) / 'trial'
            self.assertEqual(suite.cli('prepare', 'healthy-executed', trial).returncode, 0)
            self.assertEqual(suite.runner.tree(trial),
                             suite.runner.tree(suite.runner.FIXTURES / 'healthy-minimal'))
            result = suite.cli('diff', 'healthy-executed', trial)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), {
                'added': [], 'added_directories': [], 'deleted': [],
                'deleted_directories': [], 'modified': [], 'symlinks': {}})

    def test_diff_reports_every_kind_of_change(self):
        with CopiedSuite() as suite, tempfile.TemporaryDirectory() as temp:
            trial = Path(temp) / 'trial'
            suite.cli('prepare', 'healthy-executed', trial)
            (trial / 'quote.py').write_bytes((trial / 'quote.py').read_bytes() + b'\n')
            (trial / 'README.md').unlink()
            shutil.rmtree(trial / 'tests')
            (trial / 'reports').mkdir()
            (trial / 'reports/agentic-readiness.md').write_text('# Report\n')
            changes = json.loads(suite.cli('diff', 'healthy-executed', trial).stdout)
            self.assertEqual(changes['modified'], ['quote.py'])
            self.assertEqual(changes['added'], ['reports/agentic-readiness.md'])
            self.assertEqual(changes['deleted'], ['README.md', 'tests/test_quote.py'])
            self.assertEqual(changes['added_directories'], ['reports'])
            self.assertEqual(changes['deleted_directories'], ['tests'])

    def test_unknown_case_and_missing_candidate_fail_without_side_effects(self):
        with CopiedSuite() as suite, tempfile.TemporaryDirectory() as temp:
            trial = Path(temp) / 'trial'
            prepared = suite.cli('prepare', 'no-such-case', trial)
            self.assertEqual(prepared.returncode, 1)
            self.assertIn('unknown case', prepared.stderr)
            self.assertFalse(trial.exists())
            missing = suite.cli('diff', 'healthy-executed', trial)
            self.assertEqual(missing.returncode, 1)
            self.assertIn('not a directory', missing.stderr)


class FixedCommandTests(unittest.TestCase):
    def test_wrong_exit_or_missing_output_fails_the_check(self):
        with CopiedSuite() as suite:
            run = suite.runner.run_fixed
            command = [sys.executable, '-c', 'import sys; print("ok"); sys.exit(3)']
            self.assertEqual(run(command, suite.root, 3, 'ok').returncode, 3)
            with self.assertRaises(suite.runner.CheckFailure) as raised:
                run(command, suite.root, 0)
            self.assertIn('exited 3, expected 0', str(raised.exception))
            with self.assertRaises(suite.runner.CheckFailure):
                run(command, suite.root, 3, 'missing text')
            with self.assertRaises(suite.runner.CheckFailure):
                run(command, suite.root, 3, stderr_contains='ok')

    def test_fixed_commands_run_offline_without_bytecode_writes(self):
        with CopiedSuite() as suite:
            result = suite.runner.run_fixed(
                [sys.executable, '-c', 'import os; print(os.environ["READINESS_EVAL_OFFLINE"],'
                 ' os.environ["PYTHONDONTWRITEBYTECODE"])'], suite.root, 0)
            self.assertEqual(result.stdout.split(), ['1', '1'])


if __name__ == '__main__':
    unittest.main()
