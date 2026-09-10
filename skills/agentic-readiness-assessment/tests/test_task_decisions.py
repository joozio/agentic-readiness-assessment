"""Version 5.1 protects task boundaries and evidence calibration; v5.0 stays readable."""
import unittest
from test_validate_report import REPORT, FINDING, validator

TASKS = '''| Change task | State | Boundary and evidence |
|---|---|---|
| Modify pricing rules | Supported | Review the diff and run CLI and behavior checks (E01, E02). |
'''
REPORT_51 = (REPORT.replace('**Confidence:** High', '**Confidence:** High\n**Delegation:** Reviewed pricing-rule changes with the named checks.')
             .replace('## What to improve', TASKS + '\n## What to improve')
             .replace('**Scope:**', '**Repository:** fixture://quote\n**Scope:**')
             .replace('5.0.0', '5.1.0'))
FINDING_51 = (FINDING.replace('**Priority:** P1', '**Key:** demo-outcome-check\n**Priority:** P2')
              .replace('**Owner:** Repo', '**Owner:** Repo\n**Basis:** Inspected\n**Task:** Modify pricing rules\n**Effort:** Small'))


class TaskDecisionTests(unittest.TestCase):
    def errors(self, text):
        return validator.check_report(text)[0]

    def with_finding(self):
        return REPORT_51.replace('No supported finding in the declared fixture scope.', FINDING_51)

    def test_both_contract_versions_are_supported(self):
        self.assertEqual(self.errors(REPORT), [])
        self.assertEqual(self.errors(REPORT_51), [])
        self.assertEqual(self.errors(self.with_finding()), [])

    def test_new_version_requires_identity_and_delegation(self):
        for line in ('**Repository:** fixture://quote\n', '**Delegation:** Reviewed pricing-rule changes with the named checks.\n'):
            self.assertTrue(self.errors(REPORT_51.replace(line, '')))

    def test_blank_metadata_cannot_consume_the_following_line(self):
        text = REPORT_51.replace('**Delegation:** Reviewed pricing-rule changes with the named checks.', '**Delegation:**\nThis prose is not its value.')
        self.assertTrue(self.errors(text))

    def test_ready_cannot_generalize_to_unverified_component(self):
        extra = '| Change migrations | Unverified | Database fixture unavailable (E01). |\n'
        text = REPORT_51.replace(TASKS, TASKS + extra)
        self.assertTrue(self.errors(text))
        text = text.replace('Ready for bounded changes', 'Inconclusive').replace('High', 'Medium')
        text = text.replace('| Primary checks | Passed |', '| Primary checks | Unverified |')
        self.assertEqual(self.errors(text), [])

    def test_read_only_cannot_support_execution_dependent_task(self):
        text = REPORT_51.replace('Ready for bounded changes', 'Inconclusive').replace('High', 'Low')
        text = text.replace('| Passed |', '| Unverified |').replace('**Mode:** Executed', '**Mode:** Read-only')
        text = text.replace('**Kind:** Executed', '**Kind:** Inspected')
        self.assertTrue(self.errors(text))
        self.assertEqual(self.errors(text.replace('| Supported |', '| Unverified |')), [])

    def test_task_table_cannot_be_missing_duplicated_or_uncited(self):
        for text in (REPORT_51.replace(TASKS, ''), REPORT_51.replace(TASKS, TASKS + TASKS),
                     REPORT_51.replace('(E01, E02). |', '(documented). |')):
            self.assertTrue(self.errors(text))

    def test_finding_basis_effort_and_key_are_required(self):
        for line in ('**Basis:** Inspected\n', '**Effort:** Small\n', '**Key:** demo-outcome-check\n'):
            self.assertTrue(self.errors(self.with_finding().replace(line, '')))

    def test_stable_keys_cannot_collide(self):
        text = self.with_finding().replace('## What already works', FINDING_51.replace('F01', 'F02') + '\n## What already works')
        self.assertTrue(self.errors(text))

    def test_demonstrated_failure_needs_observed_evidence(self):
        text = self.with_finding().replace('**Basis:** Inspected', '**Basis:** Demonstrated')
        self.assertEqual(self.errors(text), [])
        text = text.replace('**Kind:** Executed', '**Kind:** Inspected')
        self.assertTrue(any('Demonstrated failure' in e for e in self.errors(text)))

    def test_hypothesis_cannot_create_negative_verdict_or_gap(self):
        text = self.with_finding().replace('**Basis:** Inspected', '**Basis:** Hypothesis').replace('**Priority:** P2', '**Priority:** P3')
        self.assertEqual(self.errors(text), [])
        self.assertTrue(self.errors(text.replace('Ready for bounded changes', 'Needs improvements')))
        self.assertTrue(self.errors(text.replace('**Priority:** P3', '**Priority:** P1')))
        gap = text.replace('Ready for bounded changes', 'Needs improvements').replace('| Probe | Passed |', '| Probe | Gap |').replace('(E02). |', '(E02, F01). |')
        self.assertTrue(self.errors(gap))

    def test_static_high_consequence_risk_gets_manual_review_warning(self):
        text = self.with_finding().replace('**Priority:** P2', '**Priority:** P1').replace('Ready for bounded changes', 'Needs improvements')
        errors, warnings = validator.check_report(text)
        self.assertEqual(errors, [])
        self.assertTrue(any('causal chain' in w for w in warnings))

    def test_global_blocked_cannot_erase_supported_task(self):
        text = self.with_finding().replace('Ready for bounded changes', 'Blocked').replace('**Basis:** Inspected', '**Basis:** Demonstrated')
        text = text.replace('| Setup | Passed |', '| Setup | Gap |').replace('(E01). |', '(E01, F01). |')
        self.assertTrue(self.errors(text))
        text = text.replace('| Supported |', '| Blocked |').replace('(E01, E02). |', '(E01, E02, F01). |')
        self.assertEqual(self.errors(text), [])


if __name__ == '__main__':
    unittest.main()
