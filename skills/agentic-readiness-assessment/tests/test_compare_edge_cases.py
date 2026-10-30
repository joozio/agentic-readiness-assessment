"""Edge cases for reassessment comparison: identity, escaping, empty findings and the CLI."""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import compare_reports
from compare_reports import cell, compare, identity, read_report
from test_task_decisions import FINDING_51, REPORT_51
from test_validate_report import FINDING, REPORT

BASE = dict(repository='fixture://x', scope='CLI', revision='abc', findings={})


def report_51(*keys):
    findings = '\n'.join(FINDING_51.replace('F01', 'F%02d' % (index + 1)).replace('demo-outcome-check', key)
                         for index, key in enumerate(keys))
    return REPORT_51.replace('No supported finding in the declared fixture scope.',
                             findings or 'No supported finding in the declared fixture scope.')


class IdentityAndCellTests(unittest.TestCase):
    def test_identity_normalizes_whitespace_and_trailing_slash(self):
        self.assertEqual(identity('  fixture://x/  '), 'fixture://x')
        self.assertEqual(identity('Entire\n  CLI\tfixture'), 'Entire CLI fixture')
        self.assertEqual(identity(None), '')

    def test_equivalent_identities_compare(self):
        current = dict(BASE, repository=identity('fixture://x/'), scope=identity(' CLI '))
        self.assertIn('# Reassessment review aid', compare(BASE, current))

    def test_cell_escapes_pipes_and_flattens_newlines(self):
        self.assertEqual(cell('a|b\nc'), r'a\|b c')


class CompareOutputTests(unittest.TestCase):
    def test_no_findings_on_either_side_is_not_proof_of_no_change(self):
        output = compare(BASE, dict(BASE, revision='def'))
        self.assertIn('Neither report lists findings. This does not establish unchanged repository behavior.', output)
        self.assertNotIn('Still reported', output)

    def test_rows_are_sorted_by_key_and_cover_all_statuses(self):
        before = dict(BASE, findings={'zeta': 'F01', 'alpha': 'F02'})
        after = dict(BASE, revision='def', findings={'alpha': 'F01', 'middle': 'F02'})
        rows = [line for line in compare(before, after).splitlines() if line.startswith('| ') and 'Key' not in line]
        self.assertEqual(rows, [
            '| alpha | F02 | F01 | Still reported; review current evidence |',
            '| middle | — | F02 | Newly reported; introduction date unknown |',
            '| zeta | F01 | — | Not rechecked; absence is not proof of a fix |',
        ])

    def test_pipes_in_revision_and_key_cannot_break_the_table(self):
        output = compare(dict(BASE, revision='a|b', findings={'x|y': 'F01'}), dict(BASE, revision='c'))
        self.assertIn(r'**Previous revision:** a\|b', output)
        self.assertIn(r'| x\|y | F01 | — |', output)

    def test_missing_scope_refuses_even_when_both_are_missing(self):
        with self.assertRaisesRegex(ValueError, 'different scope'):
            compare(dict(BASE, scope=''), dict(BASE, scope=''))

    def test_output_never_claims_a_fix(self):
        output = compare(dict(BASE, findings={'a': 'F01'}), dict(BASE, revision='def'))
        self.assertNotRegex(output, r'\| (Fixed|Resolved|Closed) \|')


class ReadReportTests(unittest.TestCase):
    def read(self, text, encoding='utf-8'):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'report.md'
            path.write_text(text, encoding=encoding)
            return read_report(path)

    def test_extended_report_maps_keys_to_finding_ids(self):
        parsed = self.read(report_51('alpha-check', 'beta-check').replace('Ready for bounded changes', 'Needs improvements'))
        self.assertEqual(parsed, dict(repository='fixture://quote', scope='Entire synthetic CLI fixture.',
                                      revision='Test fixture snapshot, no Git repository.',
                                      findings={'alpha-check': 'F01', 'beta-check': 'F02'}))

    def test_report_without_findings_reads_as_empty(self):
        self.assertEqual(self.read(REPORT_51)['findings'], {})

    def test_duplicate_keys_in_v50_report_are_refused(self):
        # v5.0 does not validate Key, so the comparer must catch the collision itself.
        finding = FINDING.replace('**Priority:** P1', '**Priority:** P2') + '**Key:** same-key\n'
        text = REPORT.replace('No supported finding in the declared fixture scope.',
                              finding + '\n' + finding.replace('F01', 'F02'))
        text = text.replace('Ready for bounded changes', 'Needs improvements')
        with self.assertRaisesRegex(ValueError, 'duplicate finding Key same-key'):
            self.read(text)

    def test_v50_report_without_repository_cannot_be_compared(self):
        parsed = self.read(REPORT)
        self.assertEqual(parsed['repository'], '')
        with self.assertRaisesRegex(ValueError, 'different repository'):
            compare(parsed, parsed)

    def test_invalid_report_error_names_the_file_and_rule(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'bad.md'
            path.write_text(REPORT_51.replace('**Mode:** Executed', '**Mode:** Dry run'), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, r'bad\.md: .*Mode must be Executed or Read-only'):
                read_report(path)

    def test_bom_encoded_report_is_readable(self):
        self.assertEqual(self.read(REPORT_51, encoding='utf-8-sig')['repository'], 'fixture://quote')


class CompareMainTests(unittest.TestCase):
    def run_main(self, previous, current):
        with tempfile.TemporaryDirectory() as temp:
            paths = []
            for name, text in (('old.md', previous), ('new.md', current)):
                path = Path(temp) / name
                if text is not None:
                    path.write_text(text, encoding='utf-8')
                paths.append(str(path))
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = compare_reports.main(paths)
            return code, out.getvalue(), err.getvalue()

    def test_success_prints_review_aid(self):
        code, out, err = self.run_main(report_51('alpha-check'), report_51().replace('snapshot,', 'snapshot two,'))
        self.assertEqual((code, err), (0, ''))
        self.assertIn('| alpha-check | F01 | — | Not rechecked; absence is not proof of a fix |', out)

    def test_refusals_exit_two_without_output(self):
        cases = {
            'missing file': (report_51(), None),
            'invalid report': (report_51(), '# not a report\n'),
            'different repository': (report_51(), report_51().replace('fixture://quote', 'fixture://other')),
            'legacy without Repository': (REPORT, REPORT),
        }
        for name, (previous, current) in cases.items():
            with self.subTest(name=name):
                code, out, err = self.run_main(previous, current)
                self.assertEqual((code, out), (2, ''))
                self.assertTrue(err.startswith('Cannot compare: '))


if __name__ == '__main__':
    unittest.main()
