"""Reassessment must never silently turn omissions into completed work."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from compare_reports import compare, read_report
from test_validate_report import REPORT, FINDING


class CompareTests(unittest.TestCase):
    def report(self, key='cli-check'):
        finding = FINDING.replace('**Priority:** P1', '**Priority:** P2') + '**Key:** ' + key + '\n'
        return (REPORT.replace('No supported finding in the declared fixture scope.', finding)
                .replace('**Scope:**', '**Repository:** fixture://parcel\n**Scope:**'))

    def test_missing_finding_is_not_fixed(self):
        before = dict(repository='fixture://x', scope='CLI', revision='abc', findings={'cli-check':'F01'})
        after = dict(repository='fixture://x', scope='CLI', revision='def', findings={})
        output = compare(before, after)
        self.assertIn('Not rechecked; absence is not proof of a fix', output)
        self.assertNotIn('| Fixed |', output)

    def test_keys_survive_renumbering_and_new_means_newly_reported(self):
        before = dict(repository='fixture://x', scope='CLI', revision='abc', findings={'cli-check':'F01'})
        after = dict(repository='fixture://x', scope='CLI', revision='def', findings={'cli-check':'F03','build-check':'F01'})
        output = compare(before, after)
        self.assertIn('| cli-check | F01 | F03 | Still reported', output)
        self.assertIn('Newly reported; introduction date unknown', output)

    def test_different_or_missing_identity_and_scope_refuse_comparison(self):
        before = dict(repository='fixture://x', scope='CLI', revision='abc', findings={})
        for change in ({'repository':''}, {'repository':'fixture://y'}, {'scope':'Website'}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                compare(before, dict(before, **change))

    def test_cli_reads_without_writing_and_handles_spaces(self):
        with tempfile.TemporaryDirectory() as temp:
            a, b = Path(temp)/'old report.md', Path(temp)/'new report.md'
            a.write_text(self.report(), encoding='utf-8')
            b.write_text(self.report().replace('snapshot, no Git repository.', 'snapshot two, no Git repository.'), encoding='utf-8')
            original = a.read_bytes(), b.read_bytes()
            result = subprocess.run([sys.executable,str(SCRIPTS/'compare_reports.py'),str(a),str(b)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('Still reported',result.stdout)
            self.assertEqual((a.read_bytes(),b.read_bytes()),original)

    def test_legacy_findings_without_keys_require_manual_mapping(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'old.md'
            p.write_text(self.report().replace('**Key:** cli-check\n',''))
            with self.assertRaisesRegex(ValueError, 'map legacy findings manually'):
                read_report(p)

    def test_malformed_reports_fail_before_comparison(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'bad.md'; p.write_text('# fake\n')
            with self.assertRaises(ValueError):read_report(p)

    def test_fenced_example_cannot_override_comparison_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / 'report.md'
            p.write_text(self.report() + '\n```markdown\n## Scope and limits\n**Repository:** fake\n**Scope:** fake\n```\n')
            parsed = read_report(p)
            self.assertEqual(parsed['repository'], 'fixture://parcel')
            self.assertEqual(parsed['scope'], 'Entire synthetic CLI fixture.')


if __name__ == '__main__':
    unittest.main()
