"""Edge cases for each validator rule; every assertion names the rule it expects to fire.

The broad contract tests live in test_validate_report.py and test_task_decisions.py.
These pin the individual error messages, empty and malformed input, and the helpers.
"""
import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from test_task_decisions import FINDING_51, REPORT_51, TASKS
from test_validate_report import FINDING, REPORT, validator

INCONCLUSIVE = (REPORT.replace('Ready for bounded changes', 'Inconclusive').replace('High', 'Low')
                .replace('| Passed |', '| Unverified |'))


def errors(text):
    return validator.check_report(text)[0]


def with_finding(text=REPORT, finding=FINDING):
    return text.replace('No supported finding in the declared fixture scope.', finding)


class EmptyAndMalformedInputTests(unittest.TestCase):
    SECTION_ERROR = ['Use the six report sections in order, starting with ## TL:TR.']

    def test_empty_whitespace_and_title_only_stop_at_section_check(self):
        for text in ('', '  \n\n\t\n', '# Title only\n', 'plain prose without headings'):
            with self.subTest(text=text):
                self.assertEqual(validator.check_report(text), (self.SECTION_ERROR, []))

    def test_missing_extra_reordered_or_renamed_sections_are_rejected(self):
        variants = {
            'missing': REPORT.replace('## What already works\n', ''),
            'extra': REPORT.replace('## Evidence', '## Appendix\nNotes.\n\n## Evidence'),
            'reordered': REPORT.replace('## TL:TR', '## TEMP').replace('## Readiness checks', '## TL:TR')
                               .replace('## TEMP', '## Readiness checks'),
            'renamed': REPORT.replace('## TL:TR', '## TL;DR'),
            'level three': REPORT.replace('## Evidence', '### Evidence'),
        }
        for name, text in variants.items():
            with self.subTest(name=name):
                self.assertEqual(errors(text), self.SECTION_ERROR)

    def test_section_heading_inside_fence_does_not_count(self):
        text = REPORT.replace('## Evidence', '```\n## Evidence\n```')
        self.assertEqual(errors(text), self.SECTION_ERROR)

    def test_inline_triple_backticks_before_a_real_fence_keep_the_sections(self):
        text = REPORT.replace('## What to improve',
                              '```npm test``` exited 0.\n\n## What to improve', 1)
        text = text.rstrip('\n') + '\n\n```text\nRan 3 tests\n```\n'
        self.assertEqual(errors(text), [])

    def test_every_truncation_or_dropped_line_returns_messages_without_raising(self):
        for document in (REPORT, with_finding(REPORT_51, FINDING_51)):
            lines = document.split('\n')
            for index in range(len(lines) + 1):
                for text in ('\n'.join(lines[:index]), '\n'.join(lines[:index] + lines[index + 1:])):
                    found, warnings = validator.check_report(text)
                    self.assertIsInstance(found, list)
                    self.assertIsInstance(warnings, list)

    def test_missing_title_is_reported(self):
        self.assertEqual(errors(REPORT.replace('# Fixture readiness\n', '')),
                         ['Missing descriptive report title.'])

    def test_windows_line_endings_are_accepted(self):
        self.assertEqual(validator.check_report(REPORT.replace('\n', '\r\n')), ([], []))

    def test_leading_byte_order_mark_is_accepted(self):
        # Regression: UTF-8 with BOM hid the title line and rejected a valid report.
        self.assertEqual(validator.check_report('﻿' + REPORT), ([], []))
        self.assertEqual(validator.check_report('﻿' + REPORT_51), ([], []))


class HelperTests(unittest.TestCase):
    def test_field_requires_exactly_one_non_blank_value(self):
        self.assertEqual(validator.field('**Kind:**   Executed  \n', 'Kind'), 'Executed')
        self.assertIsNone(validator.field('**Kind:** CI\n**Kind:** Executed\n', 'Kind'))
        self.assertIsNone(validator.field('**Kind:**   \n', 'Kind'))
        self.assertIsNone(validator.field('Kind: Executed\n', 'Kind'))
        self.assertIsNone(validator.field(' **Kind:** Executed\n', 'Kind'))

    def test_field_label_is_literal_not_a_pattern(self):
        self.assertIsNone(validator.field('**Skill_version:** 5.0.0\n', 'Skill.version'))
        self.assertEqual(validator.field('**A+B:** yes\n', 'A+B'), 'yes')

    def test_refs_need_two_digits_and_word_boundaries(self):
        self.assertEqual(validator.refs('E01, E001; (E12) E1 XE02 E03x F04', 'E'), {'E01', 'E001', 'E12'})

    def test_records_accept_three_dash_styles_and_need_a_title(self):
        body = '### E01 — em\nx\n### E02 – en\ny\n### E03 - hyphen\nz\n### E04 —\nno title\n### E5 — short id\n'
        self.assertEqual([key for key, _ in validator.records(body, 'E')], ['E01', 'E02', 'E03'])

    def test_strip_fences_handles_tildes_and_long_markers_but_not_mismatched_closers(self):
        self.assertEqual(validator.strip_fences('a\n~~~\nhidden\n~~~\nb\n'), 'a\n\nb\n')
        self.assertEqual(validator.strip_fences('a\n````md\n```\nhidden\n````\nb\n'), 'a\n\nb\n')
        self.assertIn('kept', validator.strip_fences('a\n```\nkept\n~~~\n'))

    def test_strip_fences_ignores_inline_code_that_starts_a_line(self):
        self.assertEqual(validator.strip_fences('```a``` b\nkept\n```\nhidden\n```\nnext\n'),
                         '```a``` b\nkept\n\nnext\n')


class ScopeAndMetadataTests(unittest.TestCase):
    def test_each_scope_field_is_required(self):
        for label, line in (('Scope', '**Scope:** Entire synthetic CLI fixture.\n'),
                            ('Coverage', '**Coverage:** Full\n'), ('Mode', '**Mode:** Executed\n'),
                            ('Revision', '**Revision:** Test fixture snapshot, no Git repository.\n'),
                            ('Skill version', '**Skill version:** 5.0.0\n')):
            with self.subTest(label=label):
                self.assertIn('Missing or duplicate scope field: ' + label, errors(REPORT.replace(line, '')))

    def test_coverage_and_mode_vocabularies(self):
        self.assertIn('Coverage must be Full or Partial.', errors(REPORT.replace('**Coverage:** Full', '**Coverage:** full')))
        self.assertIn('Mode must be Executed or Read-only.', errors(REPORT.replace('**Mode:** Executed', '**Mode:** Dry run')))

    def test_verdict_and_confidence_vocabularies(self):
        self.assertIn('Missing, duplicate or invalid Verdict.',
                      errors(REPORT.replace('Ready for bounded changes', 'Ready')))
        self.assertIn('Missing, duplicate or invalid Confidence.',
                      errors(REPORT.replace('**Confidence:** High', '**Confidence:** Very high')))

    def test_skill_version_must_be_a_v5_semver(self):
        for value in ('4.2.0', '6.0.0', '5.0', 'v5.0.0', '5.0.0 beta', '5.x.0'):
            with self.subTest(value=value):
                self.assertIn('Skill version must identify the v5 contract.',
                              errors(REPORT.replace('5.0.0', value)))
        for value in ('5.0.1', '5.0.0-rc.1', '5.0.0+build.7'):
            with self.subTest(value=value):
                self.assertEqual(errors(REPORT.replace('5.0.0', value)), [])

    def test_minor_version_is_compared_numerically(self):
        # 5.10 is newer than 5.1, so it must apply the extended task contract.
        self.assertIn('TL:TR needs one task-specific Delegation field.',
                      errors(REPORT.replace('5.0.0', '5.10.0')))
        self.assertEqual(errors(REPORT_51.replace('5.1.0', '5.10.0')), [])


class EvidenceTests(unittest.TestCase):
    def test_report_without_evidence_records(self):
        text = REPORT.split('### E01')[0]
        found = errors(text)
        self.assertIn('At least one evidence record is required, including for read-only audits.', found)
        self.assertIn('Undefined reference: E01', found)

    def test_evidence_kind_vocabulary_and_description(self):
        self.assertIn('E01: missing, duplicate or invalid evidence Kind.',
                      errors(REPORT.replace('**Kind:** Executed', '**Kind:** Observed', 1)))
        short = REPORT.replace('Synthetic evidence: python3 -m unittest discover -s tests, cwd fixture, exit 0.', 'Ran it.')
        self.assertIn('E01: describe the observation, not only its Kind.', errors(short))

    def test_reference_inside_fenced_log_is_not_a_dangling_reference(self):
        self.assertEqual(errors(REPORT + '\n```\nlog line mentions E99 and F42\n```\n'), [])

    def test_duplicate_finding_ids(self):
        text = with_finding(REPORT, FINDING + '\n' + FINDING).replace('Ready for bounded changes', 'Needs improvements')
        self.assertIn('Duplicate finding IDs.', errors(text))


class FindingFieldTests(unittest.TestCase):
    BASE = with_finding().replace('Ready for bounded changes', 'Needs improvements')
    EXTENDED = with_finding(REPORT_51, FINDING_51)

    def test_base_contract_is_valid(self):
        self.assertEqual(errors(self.BASE), [])
        self.assertEqual(errors(self.EXTENDED), [])

    def test_priority_owner_and_evidence_link(self):
        self.assertIn('F01: Priority must be P1, P2 or P3.', errors(self.BASE.replace('**Priority:** P1', '**Priority:** P0')))
        self.assertIn('F01: invalid Owner.', errors(self.BASE.replace('**Owner:** Repo', '**Owner:** Team')))
        self.assertIn('F01: Evidence needs an E ID.',
                      errors(self.BASE.replace('**Evidence:** E01; demo.py:4', '**Evidence:** demo.py:4')))

    def test_each_base_finding_field_is_required(self):
        for label in ('Why', 'Change'):
            with self.subTest(label=label):
                text = '\n'.join(line for line in self.BASE.split('\n') if not line.startswith('**' + label + ':**'))
                self.assertIn('F01: missing or duplicate field ' + label, errors(text))

    def test_stable_key_must_be_a_lowercase_slug(self):
        for key in ('Demo-outcome', 'demo_outcome', 'demo--outcome', '9demo', 'demo-', 'demo outcome'):
            with self.subTest(key=key):
                text = self.EXTENDED.replace('demo-outcome-check', key)
                self.assertIn('F01: Key must be a lowercase hyphenated problem slug.', errors(text))
        self.assertEqual(errors(self.EXTENDED.replace('demo-outcome-check', 'demo2-outcome-3')), [])

    def test_basis_and_effort_vocabularies(self):
        self.assertIn('F01: Basis must be Demonstrated, Inspected or Hypothesis.',
                      errors(self.EXTENDED.replace('**Basis:** Inspected', '**Basis:** Guess')))
        self.assertIn('F01: Effort must be Small, Medium, Large or Unknown.',
                      errors(self.EXTENDED.replace('**Effort:** Small', '**Effort:** Huge')))
        self.assertEqual(errors(self.EXTENDED.replace('**Effort:** Small', '**Effort:** Unknown')), [])

    def test_extended_fields_are_ignored_by_v50_reports(self):
        self.assertEqual(errors(self.BASE.replace('**Priority:** P1', '**Key:** Not_A_Slug\n**Basis:** Guess\n**Priority:** P1')), [])


class ReadinessRowTests(unittest.TestCase):
    def test_duplicate_and_missing_rows(self):
        row = '| Setup | Passed | Clean standard-library environment works (E01). |\n'
        self.assertIn('Duplicate readiness row: Setup', errors(REPORT.replace(row, row + row)))
        probe = '| Probe | Passed | A reversed boundary fails; restoration passes (E02). |\n'
        self.assertIn('Probe: expected a three-column check row with a valid State.', errors(REPORT.replace(probe, '')))

    def test_state_vocabulary_and_column_count(self):
        self.assertIn('Setup: expected a three-column check row with a valid State.',
                      errors(REPORT.replace('| Setup | Passed |', '| Setup | Pass |')))
        self.assertIn('Setup: expected a three-column check row with a valid State.',
                      errors(REPORT.replace('| Setup | Passed |', '| Setup | Passed | extra |')))

    def test_row_needs_an_evidence_reference(self):
        text = INCONCLUSIVE.replace('passes (E02). |', 'passes. |')
        self.assertEqual(errors(text), ['Probe: readiness row needs an evidence reference.'])

    def test_na_allowed_only_for_setup_and_deliverable(self):
        self.assertEqual(errors(REPORT.replace('| Setup | Passed |', '| Setup | N/A |')), [])
        self.assertIn('Primary checks: use Unverified rather than N/A.',
                      errors(INCONCLUSIVE.replace('| Primary checks | Unverified |', '| Primary checks | N/A |')))

    def test_six_column_and_unterminated_rows_are_malformed(self):
        message = 'Malformed or oversized table row; use at most five columns.'
        self.assertIn(message, errors(REPORT.replace('| Check | State | What this means |',
                                                     '| Check | State | What this means | a | b | c |')))
        self.assertIn(message, errors(REPORT.replace('| Check | State | What this means |',
                                                     '| Check | State | What this means')))
        self.assertEqual(1, errors(REPORT.replace('|---|---|---|', '|---|---|---|---|---|---|') + '| a | b | c | d | e | f |\n').count(message))


class VerdictRuleTests(unittest.TestCase):
    def test_ready_requires_every_check_passed(self):
        text = REPORT.replace('| Probe | Passed |', '| Probe | Unverified |')
        self.assertIn('Ready requires all four checks Passed (justified setup/deliverable N/A allowed).', errors(text))

    def test_environment_p1_does_not_block_ready_but_external_p1_does(self):
        environment = with_finding().replace('**Owner:** Repo', '**Owner:** Environment')
        self.assertEqual(errors(environment), [])
        external = with_finding().replace('**Owner:** Repo', '**Owner:** External')
        self.assertIn('Ready requires full declared coverage, High/Medium confidence and no Repo/External P1.',
                      errors(external))

    def test_inconclusive_cannot_hide_gap_or_p1(self):
        message = 'A demonstrated readiness Gap or Repo/External P1 needs a negative verdict.'
        gap = with_finding(INCONCLUSIVE).replace('| Probe | Unverified |', '| Probe | Gap |').replace('(E02). |', '(E02, F01). |')
        self.assertIn(message, errors(gap))
        self.assertIn(message, errors(with_finding(INCONCLUSIVE)))
        self.assertEqual(errors(with_finding(INCONCLUSIVE).replace('**Priority:** P1', '**Priority:** P3')), [])

    def test_needs_improvements_requires_a_substantive_gap(self):
        message = 'Needs improvements requires a verified Repo/External gap, not host limitations alone.'
        self.assertIn(message, errors(REPORT.replace('Ready for bounded changes', 'Needs improvements')))
        external = with_finding().replace('Ready for bounded changes', 'Needs improvements').replace('**Owner:** Repo', '**Owner:** External')
        self.assertEqual(errors(external), [])

    def test_blocked_requires_gap_in_one_of_the_first_three_checks(self):
        text = with_finding().replace('Ready for bounded changes', 'Blocked')
        text = text.replace('| Probe | Passed |', '| Probe | Gap |').replace('(E02). |', '(E02, F01). |')
        self.assertIn('Blocked requires a Repo finding and a setup/deliverable/primary-check Gap.', errors(text))

    def test_read_only_mode_rejects_executed_evidence(self):
        text = INCONCLUSIVE.replace('**Mode:** Executed', '**Mode:** Read-only')
        self.assertEqual(errors(text), ['Read-only mode cannot contain Executed assessment evidence.'])

    def test_high_confidence_conflicts(self):
        message = 'High confidence conflicts with partial coverage or unverified primary checks.'
        partial = INCONCLUSIVE.replace('**Confidence:** Low', '**Confidence:** High').replace('**Coverage:** Full', '**Coverage:** Partial')
        self.assertIn(message, errors(partial))
        unverified = INCONCLUSIVE.replace('**Confidence:** Low', '**Confidence:** High')
        self.assertIn(message, errors(unverified))
        self.assertEqual(errors(unverified.replace('| Primary checks | Unverified |', '| Primary checks | Passed |')), [])


class ChangeTaskTests(unittest.TestCase):
    def test_task_state_vocabulary_columns_and_name(self):
        message = 'Each change task needs three columns and a valid task State.'
        for row in ('| Modify pricing rules | Done | Checked (E01). |',
                    '| Modify pricing rules | Supported |',
                    '|  | Supported | Checked (E01). |'):
            with self.subTest(row=row):
                text = REPORT_51.replace('| Modify pricing rules | Supported | Review the diff and run CLI and behavior checks (E01, E02). |', row)
                self.assertIn(message, errors(text))

    def test_alignment_rules_are_not_tasks(self):
        self.assertEqual(errors(REPORT_51.replace('|---|---|---|\n| Modify', '|:---|:---:|---:|\n| Modify')), [])

    def test_conditional_task_needs_evidence_but_not_execution(self):
        inspected = REPORT_51.replace('| Supported |', '| Conditional |').replace('Ready for bounded changes', 'Inconclusive')
        inspected = inspected.replace('**Confidence:** High', '**Confidence:** Low').replace('| Passed |', '| Unverified |')
        self.assertEqual(errors(inspected.replace('**Kind:** Executed', '**Kind:** Inspected')), [])
        uncited = inspected.replace('(E01, E02). |', 'per the docs. |')
        self.assertIn('Modify pricing rules: task boundary needs an evidence reference.', errors(uncited))

    def test_blocked_task_needs_demonstrated_repo_finding(self):
        text = with_finding(REPORT_51, FINDING_51).replace('Ready for bounded changes', 'Needs improvements')
        text = text.replace('| Supported |', '| Blocked |').replace('(E01, E02). |', '(E01, E02, F01). |')
        self.assertIn('Modify pricing rules: Blocked task must name a Demonstrated Repo finding.', errors(text))
        self.assertEqual(errors(text.replace('**Basis:** Inspected', '**Basis:** Demonstrated')), [])

    def test_table_after_prose_gap_is_not_read_as_tasks(self):
        # Rows only count while the task table is contiguous.
        text = REPORT_51.replace(TASKS, '| Change task | State | Boundary and evidence |\n\n|---|---|---|\n'
                                 '| Modify pricing rules | Supported | Checks (E01, E02). |\n')
        self.assertIn('Add the Change task / State / Boundary and evidence table.', errors(text))


class WarningTests(unittest.TestCase):
    def test_long_tldr_warns_without_error(self):
        text = REPORT.replace('- Tests detected', '- ' + 'word ' * 180 + '\n- Tests detected')
        found, warnings = validator.check_report(text)
        self.assertEqual(found, [])
        self.assertIn('TL:TR exceeds 180 words; shorten the decision summary.', warnings)


class ValidatorMainTests(unittest.TestCase):
    def run_main(self, text=None, raw=None):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'report.md'
            if raw is not None:
                path.write_bytes(raw)
            elif text is not None:
                path.write_text(text, encoding='utf-8')
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = validator.main([str(path)])
            return code, out.getvalue(), err.getvalue()

    def test_valid_report_exits_zero(self):
        code, out, err = self.run_main(REPORT)
        self.assertEqual((code, err), (0, ''))
        self.assertIn('valid', out)

    def test_warnings_alone_still_exit_zero(self):
        code, out, err = self.run_main(REPORT + '\n' + 'detail ' * 1500)
        self.assertEqual(code, 0)
        self.assertIn('Warning: Report exceeds 1,400 words', err)

    def test_errors_exit_one_and_are_listed(self):
        code, out, err = self.run_main(REPORT.replace('**Mode:** Executed', '**Mode:** Dry run'))
        self.assertEqual((code, out), (1, ''))
        self.assertIn('Error: Mode must be Executed or Read-only.', err)

    def test_unreadable_inputs_exit_one(self):
        for kwargs in ({}, {'raw': b'\xff\xfe'}):
            with self.subTest(kwargs=kwargs):
                code, out, err = self.run_main(**kwargs)
                self.assertEqual(code, 1)
                self.assertTrue(err.startswith('Cannot read report: '))

    def test_bom_encoded_file_is_valid(self):
        code, _, err = self.run_main(raw=REPORT.encode('utf-8-sig'))
        self.assertEqual((code, err), (0, ''))


if __name__ == '__main__':
    unittest.main()
