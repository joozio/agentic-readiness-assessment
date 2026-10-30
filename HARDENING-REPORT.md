# Hardening report

Branch `claude/agentic-readiness-security-hardening-4rzirq`, starting from `57ee637`.
Three phases, each committed separately:

| Phase | Commit | Summary |
|---|---|---|
| A, security audit | `6fbd4cc` | Eval fixtures may no longer contain symlinks (oracle leak into trial copies) |
| B, critical-path tests | `133efc5` | 29 new tests for the renderer and eval runner; four render bugs fixed |
| C, user flows | `7fcab51` | The documented validate step no longer rejects a valid report |

Findings: 0 HIGH, 3 MEDIUM (all fixed), 7 LOW (3 fixed, 4 not fixed, all four being
hardening ideas). No committed secrets were found.

## Test commands and results

Run from the repository root, matching `.github/workflows/validate.yml`. Each command
was run before any change (at `57ee637`) and again after the last code commit
(`7fcab51`), on Python 3.13.17, 3.9.25 and 3.14.6. CI's matrix is 3.9 and 3.14.

| Command | Before | After |
|---|---|---|
| `python3 -m unittest discover -s skills/agentic-readiness-assessment/tests -v` | 117 tests, OK | 135 tests, OK |
| `python3 -m unittest discover -s tests -v` | 7 tests, OK | 21 tests, OK |
| `python3 tests/evals/runner.py check` | 7 of 7 PASS | 7 of 7 PASS |
| `for report in examples/v5/*.md examples/v5.1/*.md; do python3 skills/agentic-readiness-assessment/scripts/validate_report.py "$report"; done` | 8 of 8 valid | 8 of 8 valid |
| `claude plugin validate . --strict` (Claude Code 2.1.314) | passed | passed |

Nothing was failing before the changes.

Coverage, measured with coverage.py 7.17.0 in a scratch virtualenv (not added to the
repository), counting statements:

| Module | Measurement | Before | After |
|---|---|---|---|
| `render_report.py` | in-process unit tests only (the TEST-COVERAGE.md method) | 70% (88 of 294 missed) | 82% (57 of 314 missed) |
| `render_report.py` | unit tests including their CLI subprocesses | 86% (42 missed) | 95% (17 missed) |
| `tests/evals/runner.py` | unit tests including subprocesses | 33% | 57% |
| `tests/evals/runner.py` | the above plus `runner.py check` | 86% | 93% |

The in-process figure for the renderer is 70% here, not the 71.8% in
TEST-COVERAGE.md, because that file used a hand-written tracer. Most of what remains
uncovered in-process is `main()`, which the CLI subprocess tests exercise.

## Phase A: security audit

What was examined:

- `render_report.py`, all of it. It is the only code that turns untrusted text
  (assessed-repository content copied into the Markdown report) into HTML and PDF.
- The output path handling and the PDF path.
- `tests/evals/runner.py`, plus a secret scan across the tree and git history.

There are no HTTP routes, auth, sessions, payments, webhooks, CORS or
templates. There are no dependency manifests apart from a fixture
`package.json` that has no dependencies.

Evidence that the renderer's escaping holds:

- **Fuzzing.** 40,000 random documents were built from hostile atoms: raw tags, event
  handlers, `javascript:`, `data:`, `file:`, `//host`, `../`, `%2e%2e`, credentials in
  URLs, quote breakouts, `</title>`, `</code>`, bidi overrides and images. Each output
  was parsed with `html.parser`. Zero outputs held a tag, attribute or link target
  outside the allowlist. A 400-document version of this check is now a unit test.
- **PDF export.** A real run with WeasyPrint 70.0 (scratch virtualenv) produced a PDF.
  An injected `<img src="file:///etc/passwd">` and a remote stylesheet were not
  fetched.
- **Output paths.** Symlinked, dangling-symlink, hard-linked, directory and colliding
  output paths were each tried with and without `--force`. None overwrote the source
  or a symlink target.

| ID | Severity | Location | Failure scenario | Status |
|---|---|---|---|---|
| A1 | MEDIUM | `tests/evals/runner.py:38` (`tree` skipped symlinks) and `:312` (`prepare` used `copytree`, which follows them), at `57ee637` | A contributed fixture adds `fixtures/healthy-minimal/notes -> ../../oracles`. `runner.py check` still prints `PASS: manifest and fixture integrity`. `runner.py prepare healthy-executed DEST` then copies `oracles/manual-rubric.md` into `DEST/notes/`, the copy given to the agent under evaluation. That contaminates the trial, which the oracle-like-name check exists to prevent. | Fixed in `6fbd4cc`. `check` and `prepare` fail on any symlink under the fixtures (`runner.py:42`, `:102`, `:321`). Regression test: `tests/test_eval_inventory.py::test_fixture_symlink_cannot_smuggle_oracles_into_a_trial_copy`, which fails before the fix and passes after. |
| A2 | LOW | `render_report.py:23` (`INLINE_TOKEN`) | Rendering time is quadratic for one very long line of `[` or `![` with no `]`. Measured: 20,000 characters take 1.2 s and 40,000 take 4.9 s. It only affects someone rendering their own report locally, and reaching it needs a pathological line. | Not fixed. This is a hardening idea with no realistic trigger. The fix (bounding label length) would change which long links render. |
| A3 | LOW | `render_report.py:141` (link rendering) | A link label can show one URL while pointing at another, e.g. `[https://good.example](https://evil.example)`. Markdown itself behaves this way, and opening the link is still an explicit click. | Not fixed. Hardening idea: show the host beside external links whose label looks like a URL. |
| A4 | LOW | `render_report.py:134` | Relative links to dotfiles such as `[x](.env)` stay clickable. Nothing is fetched automatically, and clicking only opens a local file in the user's own browser. | Not fixed. Hardening idea only. |
| A5 | LOW | `render_report.py:437` with WeasyPrint 70.0 `weasyprint/urls.py:428` | WeasyPrint 70 reads `url_fetcher._fail_on_errors`, so a plain-function fetcher raises AttributeError if anything is ever fetched. Nothing is fetched (it fails closed), and the renderer never emits a fetchable resource, so normal reports are unaffected (verified with a real PDF). | Not fixed. Hardening idea: subclass `weasyprint.urls.URLFetcher` when it exists. |

Secrets: none found in tracked files or git history (patterns for AWS, GitHub, Slack,
Anthropic and OpenAI style keys, private keys, and literal passwords or API keys).

## Phase B: critical-path tests

The paths where a defect hurts most, and what now pins them:

1. **Hostile report text cannot inject markup or unsafe links.**
   `test_render_critical_paths.py::HostileInputTests` runs a seeded 400-document
   hostile corpus checked against a tag, attribute and link-target allowlist. It also
   checks the title breakout.
2. **Report text stays visible and record links work.** `TextPreservationTests` and
   `RecordLinkTests` cover a seeded property test that words in every block type
   remain visible, plus fence handling and link targets.
3. **Writing output never destroys data.** `OutputSafetyTests` covers:
   - a failed `--force` replace keeps the old file and leaves no temp file;
   - a dangling symlink is never written through;
   - `--force` replaces a symlink itself, not its target;
   - a symlink to the source is refused;
   - `--pdf` on a `.pdf`-named source is refused;
   - a directory at the output path is never replaced;
   - invalid UTF-8 gives a clean error;
   - a PDF conversion failure gives a clean error.
4. **Eval manifest safety.** `tests/test_eval_runner.py::ManifestTests` rejects fixture
   paths that escape `fixtures/`, forbidden operations being permitted, incomplete
   permissions, duplicate IDs and missing grading criteria.
5. **Fixture integrity.** `IntegrityTests` detects a changed byte, an added file or a
   missing file, and an oracle-like name even when the hashes have been updated.
6. **Trial copy and diff accuracy.** `TrialCopyTests` and `FixedCommandTests` cover:
   - `prepare` copies exactly the fixture;
   - `diff` reports every change kind;
   - an unknown case leaves no side effects;
   - a wrong exit code or missing output fails the check;
   - fixed commands get the offline environment.

Mutation check: deleting the `..` fixture-path guard, blanking `deleted_directories`
in `diff`, or removing the temp-file cleanup in `_write_bytes` each makes a new test
fail.

Bugs the tests exposed, all fixed in `133efc5`. Each regression test fails before the
fix and passes after. All 27 Markdown files in the repository render byte-identically
before and after.

| ID | Severity | Location (at `57ee637`) | Failure scenario | Status |
|---|---|---|---|---|
| B1 | MEDIUM | `render_report.py:155` | `[F01 upstream issue](https://example.test/1)` was rendered as an `<a>` for F01 nested inside the external `<a>`. In Chromium, the external link then covers only the text before `F01`, and `[F01](url)` becomes an empty, unclickable link. Evidence links written in that natural style were lost. | Fixed: link labels no longer contain record links (`render_report.py:157`). |
| B2 | MEDIUM | `render_report.py:19` (`FENCE`) | A report line such as ```` ```npm test``` exited 0. ```` was taken as a fence opener. Its text went into an attribute, and the rest of the report became one code block. Repro: inserting that line into `examples/v5.1/healthy.md` before `## What to improve` still validates, but the HTML had 2 of 6 sections and 0 of 7 finding and evidence headings. After the fix it has 6 of 6 and 7 of 7. | Fixed: a backtick fence's info string may not contain backticks, per CommonMark (`render_report.py:20`). |
| B3 | LOW | `render_report.py:230` | A `### F07 - ...` line inside a fenced excerpt (for example a quoted previous report) counted as a record, so `F07` in prose linked to an anchor that does not exist. | Fixed: record IDs are collected outside fences only (`_record_refs`, `render_report.py:233`). |
| B4 | LOW | `render_report.py:214` | A heading like `#### F01 follow-up` placed before `### F01 - ...` took the id `f01`, so every F01 link jumped to it instead of the finding. | Fixed: record ids are reserved for their level-3 headings (`render_report.py:256`, `:292`). |

No bugs were found in `tests/evals/runner.py` beyond A1.

## Phase C: user flows

Every step below was followed literally from README.md, SKILL.md,
`references/export.md`, CONTRIBUTING.md and `tests/evals/README.md`:

- **Install by copying.** Cloned the repo, copied
  `skills/agentic-readiness-assessment/` to another directory, and ran from there all
  three README "Read and reuse" commands, the validator and the bundled unit tests.
  All behaved as documented.
- **Install as a Claude Code plugin.** In a throwaway `HOME`, ran
  `claude plugin marketplace add <clone>` and then
  `claude plugin install agentic-readiness-assessment@joozio-agent-skills`. Both
  succeeded, and the installed copy contains SKILL.md and all three scripts.
- **Error paths.** A missing report, a missing output directory, an existing output
  without `--force`, a report used as its own output, and HTML and PDF outputs that
  collide each give one actionable `Error:` line and exit 1.
- **Reassessment.** `compare_reports.py` on reports from different repositories
  refuses, as documented.
- **Eval suite.** `runner.py check`, `prepare` (including refusing an existing
  destination), and `diff` (modified files and added directories) all work as
  documented.
- **PDF export.** HTML and PDF export succeed with WeasyPrint 70.0 installed. Without
  it, the HTML is kept and the documented message is printed.
- **Mobile widths.** All 9 example reports were rendered to HTML and loaded in
  headless Chromium at 320, 375 and 768 px. There was no horizontal page overflow
  outside the scrollable tables and code blocks, and no console or CSP errors.
- **Docs links.** Every relative link in the README, docs, skill references and
  examples resolves.

| ID | Severity | Location | Failure scenario | Status |
|---|---|---|---|---|
| C1 | LOW | `skills/agentic-readiness-assessment/scripts/validate_report.py:41` (`strip_fences`) | SKILL.md says to run `validate_report.py` on each report. A valid report with ```` ```npm test``` exited 0. ```` followed later by a real fenced block was rejected with "Use the six report sections in order". The stripper treated the inline-code line as a fence opener and deleted every section up to the real fence. Repro: `examples/v5.1/healthy.md` with that line before `## What to improve` and a `text` fence appended. | Fixed in `7fcab51`, with the same backtick rule as B2, so both tools agree. Two regression tests in `test_validate_edge_cases.py` fail before and pass after. |

Observed but not changed, because these are not broken flows:

- The README lists `render_report.py report.md` and then `render_report.py report.md
  --pdf`. Run in that order, the second refuses to overwrite the HTML until `--force`
  is added. The behaviour and the message are documented and actionable.
- `claude plugin validate . --strict` passes, with advisory output suggesting a
  marketplace install line in the README. Adding it would be a copy change, so it
  is left to the owner.

## Not verified

- **A real assessment run.** An agent running the skill end to end was not tried,
  because it needs live model API calls. Only the deterministic scripts and the
  install steps were exercised.
- **Codex and Gemini installs.** Those CLIs are not available here; only the
  manifests' JSON and version consistency were checked (by the existing tests).
- **Other platforms and versions.** WeasyPrint versions other than 70.0, and
  macOS or Windows file-system behaviour (case-insensitive paths, Windows
  symlinks), were not tested.
- **CI.** GitHub Actions does not run for this branch: the workflow triggers on
  pushes to `main` and `human-first-portable-skill` and on pull requests, and no PR
  was requested. Locally, the same commands pass on Python 3.9.25, 3.13.17 and
  3.14.6.
