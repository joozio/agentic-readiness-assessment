# Test coverage: validator and reassessment comparer

This pass raised unit coverage of the two modules that decide report outcomes:

- `validate_report.py` turns a Markdown report into verdict, finding and evidence errors.
- `compare_reports.py` matches findings across two reports by stable Key.

## Numbers

| Module | Statements | Before | After |
|---|---|---|---|
| `skills/agentic-readiness-assessment/scripts/validate_report.py` | 216 → 217 | 81.9% (39 missed) | 99.5% (1 missed) |
| `skills/agentic-readiness-assessment/scripts/compare_reports.py` | 49 | 75.5% (12 missed) | 98.0% (1 missed) |
| `skills/agentic-readiness-assessment/scripts/render_report.py` | 287 | 71.8% | 71.8% (not targeted) |
| `tests/evals/runner.py` | 243 | 0% | 0% (see below) |
| **Total** | 795 → 796 | 52.8% | 59.0% |

Tests: 58 → 124 in-process unit tests (skill suite 51 → 117, packaging suite unchanged at 7).

The one remaining missed line in each target module is `raise SystemExit(main())` under
`if __name__ == '__main__'`. The existing subprocess CLI tests run that line, but
in-process tracing cannot see it.

### How this was measured

`coverage.py` is not installed in this environment, and installing it was avoided to keep
the run offline. The numbers come from a small standard-library tracer. It runs both CI
unittest suites in-process under `sys.settrace` and counts `ast` statement lines, excluding
docstrings. A statement counts as covered if its first line executes. Child processes
started by the existing CLI tests are not traced. `coverage.py` would give slightly
different numbers, mainly for multi-line statements and with branch coverage, but the
ranking would be the same.

`tests/evals/runner.py` is the fixture/eval harness, not scoring logic. CI runs it end to
end as `python tests/evals/runner.py check`, which passes, and no unit tests import it.
It was left out of scope.

## What the new tests pin down

New files: `skills/agentic-readiness-assessment/tests/test_validate_edge_cases.py` (50 tests)
and `test_compare_edge_cases.py` (16 tests). Most existing tests only assert that *some*
error occurs. The new tests assert the exact message of the rule they target, so a
change that makes a different rule fire still fails the test.

**Empty and malformed input (validator)**
- An empty, whitespace-only, title-only or heading-free document gets exactly the
  section-order error and stops there.
- Missing, extra, reordered or renamed sections are rejected, as are sections demoted to
  `###` or hidden inside a fence.
- Robustness sweep: for both a v5.0 report and a v5.1 report with a finding, every
  truncation and every single-line deletion returns error lists and never raises.
- Windows line endings and a leading UTF-8 byte-order mark (BOM) are accepted (BOM: see
  Bugs fixed below).

**Helpers**
- `field`: needs exactly one non-blank value at the start of a line; labels are matched
  literally, not as regex.
- `refs`: IDs need two or more digits and word boundaries (`E1`, `XE02`, `E03x` are not
  references).
- `records`: accepts em dash, en dash and hyphen separators; requires a title on the same
  line.
- `strip_fences`: handles tilde fences and nested shorter fences; a mismatched closer
  does not end the block.

**Scope, metadata and evidence**
- Each scope field is required individually. Coverage, Mode, Verdict and Confidence only
  accept their allowed values (matching is case-sensitive).
- Skill version must be a v5 semantic version. Pre-release and build suffixes are
  allowed; `4.2.0`, `6.0.0`, `5.0` and `v5.0.0` are rejected.
- Minor versions are compared as numbers: `5.10.0` applies the v5.1 task contract.
- An evidence record needs a valid Kind and at least 8 words. Without any evidence, the
  report errors and its references become undefined.
- E/F IDs mentioned inside fenced logs do not count as dangling references.

**Findings**
- Each rule has its own message: Priority, Owner, E-ID link, required fields, duplicate
  IDs.
- v5.1 rules: Key must be a lowercase hyphenated slug (six bad shapes are tested), plus
  the Basis and Effort values.
- v5.0 reports ignore the v5.1-only fields.

**Readiness rows and verdicts**
- Rows: duplicate or missing rows, invalid State, wrong column count, and a missing
  evidence reference are each rejected.
- N/A is allowed only for Setup and Deliverable.
- Rows wider than five columns, or without a closing pipe, are rejected, with one
  message per report.
- Ready needs all four checks Passed. An Environment-owned P1 does not block Ready; an
  External P1 does.
- Inconclusive cannot hide a Gap or a Repo P1, but may carry a P3.
- Needs improvements needs a Repo or External gap. Blocked needs a Gap in Setup,
  Deliverable or Primary checks; a Gap in Probe does not count.
- Read-only mode rejects Executed evidence. High confidence conflicts with Partial
  coverage or Unverified primary checks.

**Change tasks (v5.1)**
- A task row needs a valid State, three columns and a non-empty name. Alignment rows are
  not tasks.
- Conditional tasks need an evidence reference, not necessarily execution.
- A Blocked task needs a Demonstrated Repo finding.
- A blank line breaks the task table, so its rows are not read as tasks.

**Warnings and CLI**
- A TL:TR over 180 words only warns.
- `main()` exit codes: 0 for valid, 0 with warnings only, 1 with listed errors, 1 for a
  missing or non-UTF-8 file, 0 for a BOM-encoded file.

**Comparer**
- Repository and scope identity ignore whitespace and a trailing slash. Missing identity
  on either side refuses comparison, including two v5.0 reports without Repository.
- Rows are sorted by Key and cover all three statuses. Output never claims a finding is
  Fixed, Resolved or Closed.
- When neither report has findings, the output says this does not prove nothing changed.
- Pipes in Keys or revisions are escaped and cannot break the table.
- v5.0 reports with duplicate Keys are refused. The validator does not check Keys before
  v5.1, so only the comparer catches this collision.
- `read_report` returns exactly the Key → ID mapping and metadata. Error messages name the
  file and the failing rule.
- `main()` exits 2 with no stdout for a missing file, an invalid report, different
  repositories, or legacy reports.

## Bugs fixed (application code, `validate_report.py`)

Both bugs were exposed by the new tests. Each fix is one line.

1. **A UTF-8 BOM made valid reports fail.** Some Windows editors and PowerShell's
   `Out-File -Encoding utf8` write a byte-order mark (BOM) at the start of the file.
   Reading with `utf-8` keeps it as `﻿`, so the `^# ` title check failed on line 1.
   A correct report was rejected with "Missing descriptive report title." The validator
   exited 1, and `compare_reports.py` refused the file (exit 2) because it relies on the
   same check. Fix: `check_report` removes one leading BOM before parsing. All valid
   examples in CI still pass.
2. **A heading without a title took the next line as its title.** In `records()`, the
   pattern `^### (E\d{2,})\s+[—–-]\s+\S.*$` uses `\s+`, which can match a newline. For
   `### E04 —` followed by body text, the next line became the title and dropped out of
   the record's body. This bypassed the requirement that a record heading have a title,
   and could hide a `**Kind:**` or `**Priority:**` line from its record. Fix: use
   `[ \t]+` so the heading stays on one line. All shipped examples still validate the
   same way.

## Observations not changed

- **The HTML renderer has the same BOM issue.** `render_report.py` reads with `utf-8`,
  so a BOM-prefixed report gets the default `<title>` and its first heading is not found.
  The renderer is presentation code outside this pass's scope. The fix would be
  `encoding='utf-8-sig'` in its `main()`.
- **A table row with whitespace after its closing pipe is rejected as malformed.** This
  fails closed (it rejects rather than wrongly accepting), and the contract does not say
  how trailing whitespace should be treated, so it was left as is and not pinned by a
  test.
- **`examples/fs-demo-project/agentic-readiness.md` fails validation.** It is a pre-v5
  report, not in CI's example list, and it failed the same way before this change.
- **Python versions:** the suites were run on 3.11, 3.12 and 3.13 here. CI's 3.9 and
  3.14 are not installed locally. The new tests use only syntax and APIs available in 3.9.
