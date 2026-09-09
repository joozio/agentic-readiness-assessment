"""Behavioral contract cases; all evidence here is deliberately synthetic."""
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('validator', SKILL / 'scripts/validate_report.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

REPORT = '''# Fixture readiness

## TL:TR
**Verdict:** Ready for bounded changes
**Confidence:** High

- The documented loop works for this small CLI; scoped behavior changes are reasonable.
- Tests detected a boundary defect. Keep running them when changing the quote.

## Readiness checks
| Check | State | What this means |
|---|---|---|
| Setup | Passed | Clean standard-library environment works (E01). |
| Deliverable | Passed | The CLI returns the expected result (E01). |
| Primary checks | Passed | Both behavior tests pass (E01). |
| Probe | Passed | A reversed boundary fails; restoration passes (E02). |

## What to improve
No supported finding in the declared fixture scope.

## What already works
The error boundary has executable tests (E01, E02).

## Scope and limits
**Scope:** Entire synthetic CLI fixture.
**Coverage:** Full
**Mode:** Executed
**Revision:** Test fixture snapshot, no Git repository.
**Skill version:** 5.0.0

Synthetic validator input, not a claim about a real execution.

## Evidence
### E01 — Baseline checks
**Kind:** Executed
Synthetic evidence: python3 -m unittest discover -s tests, cwd fixture, exit 0.

### E02 — Boundary probe
**Kind:** Executed
Synthetic evidence: changed a comparison, one test failed, exact bytes restored,
then both tests passed; the snapshot comparison matched the starting files.
'''

FINDING = '''### F01 — Make delivery checks meaningful
**Priority:** P1
**Owner:** Repo
**Why:** The script prints the result without detecting a wrong result.
**Evidence:** E01; demo.py:4 only prints the number.
**Change:** Assert the expected state and exit nonzero on mismatch.
**Verify:** A wrong result exits nonzero; the correct result exits zero.
'''


class ReportTests(unittest.TestCase):
    def errors(self, text):
        return validator.check_report(text)[0]

    def with_finding(self, text=REPORT):
        return text.replace('No supported finding in the declared fixture scope.', FINDING)

    def test_ready_execution(self):
        self.assertEqual(self.errors(REPORT), [])

    def test_read_only_with_no_python_remains_useful(self):
        text = REPORT.replace('Ready for bounded changes', 'Inconclusive').replace('High', 'Low')
        text = text.replace('| Passed |', '| Unverified |').replace('**Mode:** Executed', '**Mode:** Read-only')
        text = text.replace('**Kind:** Executed', '**Kind:** Inspected')
        self.assertEqual(self.errors(text), [])

    def test_host_only_limitation_is_not_repo_failure(self):
        text = self.with_finding().replace('**Owner:** Repo', '**Owner:** Environment')
        text = text.replace('Ready for bounded changes', 'Inconclusive').replace('High', 'Low')
        text = text.replace('| Passed |', '| Unverified |')
        self.assertEqual(self.errors(text), [])
        self.assertTrue(self.errors(text.replace('Inconclusive', 'Needs improvements')))

    def test_read_only_can_note_minor_inspected_improvements(self):
        text = self.with_finding().replace('Ready for bounded changes', 'Inconclusive')
        text = text.replace('**Priority:** P1', '**Priority:** P2').replace('High', 'Low')
        text = text.replace('| Passed |', '| Unverified |').replace('**Mode:** Executed', '**Mode:** Read-only')
        text = text.replace('**Kind:** Executed', '**Kind:** Inspected')
        self.assertEqual(self.errors(text), [])

    def test_gap_cannot_be_sourced_only_to_environment_finding(self):
        text = self.with_finding().replace('Ready for bounded changes', 'Needs improvements')
        text = text.replace('**Owner:** Repo', '**Owner:** Environment')
        text = text.replace('| Setup | Passed |', '| Setup | Gap |').replace('(E01).', '(E01; F01).')
        self.assertTrue(self.errors(text))

    def test_repo_blocker_has_a_failed_primary_surface(self):
        text = self.with_finding().replace('Ready for bounded changes', 'Blocked')
        text = text.replace('| Setup | Passed |', '| Setup | Gap |').replace('(E01).', '(E01; F01).')
        self.assertEqual(self.errors(text), [])
        self.assertTrue(self.errors(text.replace('| Setup | Gap |', '| Setup | Unverified |')))

    def test_missed_probe_means_improvement_not_total_block(self):
        text = self.with_finding().replace('Ready for bounded changes', 'Needs improvements')
        text = text.replace('| Probe | Passed |', '| Probe | Gap |').replace('(E02).', '(E02; F01).')
        self.assertEqual(self.errors(text), [])

    def test_na_for_deliverable_not_missing_probe(self):
        self.assertEqual(self.errors(REPORT.replace('| Deliverable | Passed |', '| Deliverable | N/A |')), [])
        self.assertTrue(self.errors(REPORT.replace('| Probe | Passed |', '| Probe | N/A |')))

    def test_ready_cannot_hide_critical_finding(self):
        self.assertTrue(self.errors(self.with_finding()))

    def test_ready_cannot_hide_partial_scope_or_low_confidence(self):
        for old, new in [('**Coverage:** Full', '**Coverage:** Partial'), ('High', 'Low')]:
            with self.subTest(new=new):
                self.assertTrue(self.errors(REPORT.replace(old, new)))

    def test_configuration_is_not_executed_proof(self):
        self.assertTrue(self.errors(REPORT.replace('**Kind:** Executed', '**Kind:** Inspected')))

    def test_exact_revision_ci_can_prove_a_check(self):
        self.assertEqual(self.errors(REPORT.replace('**Kind:** Executed', '**Kind:** CI')), [])

    def test_undefined_evidence_and_findings_are_rejected(self):
        for marker in ('E99', 'F99'):
            with self.subTest(marker=marker):
                self.assertTrue(self.errors(REPORT.replace('(E01).', '(' + marker + ').')))

    def test_duplicate_metadata_or_ids_is_rejected(self):
        for suffix in ('\n### E01 — duplicate\n**Kind:** Executed\nA second record cannot reuse this identifier.\n',):
            self.assertTrue(self.errors(REPORT + suffix))
        self.assertTrue(self.errors(REPORT.replace('**Confidence:** High', '**Confidence:** High\n**Confidence:** Low')))

    def test_missing_fix_verification_is_rejected(self):
        text = self.with_finding().replace('Ready for bounded changes', 'Needs improvements')
        text = text.replace('**Verify:** A wrong result exits nonzero; the correct result exits zero.\n', '')
        self.assertTrue(self.errors(text))

    def test_escaped_table_pipe_is_supported(self):
        self.assertEqual(self.errors(REPORT.replace('environment works', 'environment works with `one \\| two`')), [])

    def test_long_report_warns_without_rejecting_evidence(self):
        errors, warnings = validator.check_report(REPORT + '\n' + 'detail ' * 1500)
        self.assertEqual(errors, [])
        self.assertTrue(warnings)

    def test_fenced_example_cannot_spoof_metadata(self):
        text = REPORT.replace('**Verdict:** Ready for bounded changes', '```\n**Verdict:** Ready for bounded changes\n```')
        self.assertTrue(self.errors(text))

    def test_non_repo_gap_cannot_claim_blocked(self):
        text = self.with_finding().replace('Ready for bounded changes', 'Blocked').replace('**Owner:** Repo', '**Owner:** Environment')
        text = text.replace('| Setup | Passed |', '| Setup | Gap |').replace('(E01).', '(E01; F01).')
        self.assertTrue(self.errors(text))

    def test_cli_handles_spaces_unicode_and_does_not_modify_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'report café.md'
            p.write_text(REPORT, encoding='utf-8')
            before = p.read_bytes()
            result = subprocess.run([sys.executable, str(SKILL / 'scripts/validate_report.py'), str(p)], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(p.read_bytes(), before)

    def test_cli_missing_file_and_bad_encoding_fail_cleanly(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'report.md'
            for data in (None, b'\xff'):
                if data is not None:
                    p.write_bytes(data)
                result = subprocess.run([sys.executable, str(SKILL / 'scripts/validate_report.py'), str(p)], capture_output=True)
                self.assertEqual(result.returncode, 1)
                self.assertNotIn(b'Traceback', result.stderr)


if __name__ == '__main__':
    unittest.main()
