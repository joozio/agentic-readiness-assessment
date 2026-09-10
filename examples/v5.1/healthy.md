# Agentic readiness assessment: Parcel quote

## TL:TR

**Verdict:** Ready for bounded changes  
**Confidence:** High  
**Delegation:** Reviewed changes to the shipping calculation and its existing input boundary are supported when the behavior suite and documented CLI example are rerun.

- The repository is unusually small and direct: its README identifies the only behavior file, test file, supported Python version, complete test command, and runnable example.
- Python 3.14.3 ran all three tests successfully, and the documented CLI example produced the expected quote of `13`.
- A reversible boundary defect was detected by the relevant test; exact source bytes were restored and the same suite passed again.
- The main remaining weakness is localized: automated tests exercise `quote()` but not argument parsing or printed CLI output. Add a subprocess-level CLI test first if the command-line contract will evolve.

## Readiness checks

| Check | State | What this means |
|---|---|---|
| Setup | Passed | The documented Python prerequisite is present, no installation is required by design, and the complete suite ran from the repository root (E01, E03). |
| Deliverable | Passed | The documented runnable script executed with weight `4` and printed `13` (E02). |
| Primary checks | Passed | The complete documented behavior suite passed all three tests on the assessed snapshot (E03). |
| Probe | Passed | Changing the zero-weight boundary caused the named boundary test to fail; exact restoration returned the suite to its baseline result (E04). |

| Change task | State | Boundary and evidence |
|---|---|---|
| Modify the parcel quote calculation or its nonpositive-weight boundary while preserving the current CLI contract | Supported | `quote.py:5-8` is directly covered for representative prices and the zero/negative boundary. Run the full suite and the CLI example, and review any CLI-facing change because CLI integration is not automated (E02, E03, E04, E05). |

## What to improve

### F01 - Automate the command-line contract
**Key:** automate-cli-contract  
**Priority:** P2  
**Owner:** Repo  
**Basis:** Inspected  
**Task:** Modify the parcel quote calculation or its nonpositive-weight boundary while preserving the current CLI contract  
**Effort:** Small  
**Why:** The function-level suite can miss a regression in argument parsing, invocation, or printed output. The documented manual example is a useful workaround, and it passed in this assessment.  
**Evidence:** E02, E05; `tests/test_quote.py:3-16` imports and calls `quote()` directly, while the CLI wrapper is in `quote.py:11-15`.  
**Change:** Add a standard-library subprocess test for the documented `python3 quote.py 4` behavior; define and test invalid-input behavior only if it is intended to be a stable CLI contract.  
**Verify:** The complete suite passes for the normal implementation, then fails when the CLI print or argument-handling path is deliberately altered in a disposable copy.

## What already works

- The README gives a correct supported runtime, states that installation and live dependencies are unnecessary, names the complete suite, and maps shipping-rule changes to their source and tests (E01).
- The primary tests assert two concrete quote outcomes and both sides of the nonpositive-weight rejection boundary; all three tests passed (E03).
- The boundary assertion provided effective, well-localized feedback: the probe failure named `test_nonpositive_weight_is_rejected`, the `value=0` subtest, and the missing `ValueError` (E04).
- The source-only delivery path is directly runnable and the documented example worked without credentials, services, downloads, or generated setup state (E02).

## Scope and limits

**Repository:** Local Parcel quote snapshot at `/tmp/readiness-v51-evals/healthy-executed/new-corrected/repo`  
**Scope:** Full three-file repository: quote behavior, unit tests, README workflow, and documented CLI delivery. The assessed task is a bounded shipping-rule change that preserves the current CLI shape.  
**Coverage:** Full  
**Mode:** Executed  
**Revision:** No VCS metadata was present; source snapshot identified by the SHA-256 values in E01.  
**Skill version:** 5.1.0

Assessment date: 2026-09-10. Tested on Darwin 25.4.0 arm64 with Python 3.14.3. No network, installation, credentials, live services, deployment, packaging, performance behavior, or alternate Python versions were exercised. The repository documents a source-only runnable deliverable, so no separate package artifact was required. The defect probe ran only in an audit-created disposable copy, which was removed after exact restoration and a green rerun. The three original source files retained their baseline hashes; the report is the only intended addition. Report structure was checked with the supplied validator (E06).

## Evidence

### E01 - Snapshot, instructions, and runtime
**Kind:** Executed  
From `/tmp/readiness-v51-evals/healthy-executed/new-corrected/repo`, `git rev-parse --show-toplevel`, `git remote -v`, `git rev-parse HEAD`, and `git status --short` each reported that this is not a Git repository. `rg --files -g '!reports/**'` found only `README.md`, `quote.py`, and `tests/test_quote.py`; all were inspected. `python3 --version` returned `Python 3.14.3`. Baseline SHA-256: README `3c5d037ec3758327b59272a0aa9f042a7b827e9c58beb396de450d635e330c91`, source `184d4efeaf2803082e0a92b7302863ce39a5f38e49fa450d4c9eae5fcc6b1592`, test `631e269069ee65588a980229d88bd3af612919d609368a4285eefc5e6e68eb78`.

### E02 - Runnable deliverable
**Kind:** Executed  
From the repository root, `PYTHONDONTWRITEBYTECODE=1 python3 quote.py 4` exited 0 and printed `13`, matching the documented example and inspected formula. In the same command group, `PYTHONDONTWRITEBYTECODE=1 python3 quote.py 0` exited 1 with the function's `ValueError`; that observation establishes current behavior only, not a documented CLI error contract.

### E03 - Complete behavior suite
**Kind:** Executed  
From the repository root, `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` exited 0: three tests ran and passed, covering quotes at weights 1 and 4 and rejection of 0 and -1.

### E04 - Reversible boundary probe
**Kind:** Executed  
In `.agentic-readiness-probe`, a disposable copy whose `quote.py` and test hashes matched E01, `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` first passed all three tests. An `apply_patch` changed only `if weight <= 0` to `if weight < 0`; rerunning the same command exited 1 and failed the `value=0` subtest because `ValueError` was not raised. `cp quote.py.original quote.py`, followed by `cmp -s` and SHA-256 comparison, restored the exact original bytes; the same suite then exited 0 with all three tests passing. The disposable directory was removed afterward.

### E05 - CLI coverage boundary
**Kind:** Inspected  
`tests/test_quote.py:3-16` imports `quote` and asserts function behavior only. No test executes the `argparse` and print path at `quote.py:11-15`; the manual execution in E02 is the available control.

### E06 - Preservation and report validation
**Kind:** Executed  
After probe cleanup, `shasum -a 256 README.md quote.py tests/test_quote.py` reproduced all three E01 hashes, and `find . -maxdepth 3 -type f -print | sort` showed only the original three files before report creation. `python3 /tmp/readiness-v51-evals/skill-candidate-2/scripts/validate_report.py reports/agentic-readiness.md` was run against the final report from the repository root and exited 0.
