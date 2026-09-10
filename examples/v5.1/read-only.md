# Agentic readiness assessment — Parcel quote

## TL:TR

**Verdict:** Inconclusive  
**Confidence:** Low  
**Delegation:** Shipping-rule and CLI changes remain conditional on running the documented checks and reviewing the CLI boundary.

- The repository is unusually easy to navigate: one behavior module, one test module, and a README that names the edit and verification paths.
- Inspection shows meaningful assertions for representative and invalid quote inputs, but strict read-only constraints prevented checking the Python prerequisite, running the suite or example, and performing a defect-detection probe.
- CLI argument parsing and printed output are outside the inspected test assertions, so CLI changes need an additional boundary check.
- First action: in an execution-authorized disposable checkout, run the documented unit suite and CLI example, then add a CLI regression test before delegating CLI behavior changes.

## Readiness checks

| Check | State | What this means |
|---|---|---|
| Setup | Unverified | The documented Python 3.9+ prerequisite and stdlib-only setup were inspected but not exercised (E02, E04). |
| Deliverable | Unverified | The runnable `quote.py` script was inspected but its documented entry point was not run (E03, E04). |
| Primary checks | Unverified | Assertions appear relevant, but the documented `unittest` suite was not run (E03, E04). |
| Probe | Unverified | Mutation and execution were forbidden, so defect detection and restoration could not be exercised (E04). |

| Change task | State | Boundary and evidence |
|---|---|---|
| Modify the shipping quote formula or validation | Conditional | The route is documented as `quote.py` to `tests/test_quote.py`, whose assertions cover two positive weights and nonpositive rejection; run the suite before and after the change (E02, E03, E04). |
| Change CLI arguments or printed output | Unverified | The `argparse`/printing boundary is visible in `quote.py`, but no inspected test invokes the script or asserts its output and exit behavior (E03). |

## What to improve

### F01 - Cover the CLI entry point as a deliverable
**Key:** cli-entrypoint-coverage  
**Priority:** P2  
**Owner:** Repo  
**Basis:** Inspected  
**Task:** Change CLI arguments or printed output  
**Effort:** Small  
**Why:** Function-level assertions can miss a regression in argument parsing, exit behavior, or printed output. The documented manual example is a useful workaround, but it is not an automated regression gate.  
**Evidence:** E03; `quote.py:11-15` defines the CLI while `tests/test_quote.py:1-20` imports and calls only `quote`.  
**Change:** Add a standard-library CLI test that invokes the script with a representative valid weight and checks exit status and exact output; include one invalid-input case if CLI error behavior is part of the intended contract.  
**Verify:** The normal suite passes for the current CLI, then fails when the output or argument handling is deliberately made incorrect, and passes again after exact restoration.

## What already works

- The README states the runtime expectation, absence of installation/services/credentials, exact suite command, example command, and source-to-test edit path (E02).
- The implementation has a compact boundary: pure quote behavior is separated from the guarded CLI entry point, making the likely change surface easy to identify (E03).
- Inspection of the tests found exact expected values for two normal inputs plus explicit rejection checks for zero and a negative value; these are meaningful assertions even though their execution is unverified (E03, E04).

## Scope and limits

**Repository:** Local snapshot `/tmp/readiness-v51-evals/healthy-read-only/new/repo`  
**Scope:** Full supplied project: README, quote calculation/CLI, and unit tests.  
**Coverage:** Full  
**Mode:** Read-only  
**Revision:** Unverified local snapshot; Git/VCS metadata was not queried.  
**Skill version:** 5.1.0

Assessment date: 2026-09-10. All three visible non-Git files were read. Per the request, no repository command, import, interpreter/runtime check, test, example, installation, network access, credential access, service, validator, VCS query, or mutation was attempted. Consequently, this report supports navigation and review boundaries only; it does not establish that setup, runtime behavior, or tests work on this host. CI, packaging beyond the source script, and production/deployment behavior were not present in the supplied file set and were not inferred.

The report contract was reviewed manually because the request classifies this as a strict file-only/read-only case. Following the skill presented no difficulty; the constraint simply required execution claims to remain Unverified. No target files were changed, so no restoration was necessary and no changes remain in the target. The only created artifact is the identical report at `/tmp/readiness-v51-evals/healthy-read-only/new/report.md`, outside the target.

## Evidence

### E01 - Supplied-file inventory
**Kind:** Inspected  
Command: `find . -type f -not -path './.git/*' -print | LC_ALL=C sort`  
CWD: `/tmp/readiness-v51-evals/healthy-read-only/new/repo`  
Result: exit 0; it listed `README.md`, `quote.py`, and `tests/test_quote.py`. This was a file inventory only, not repository tooling.

### E02 - Workflow documentation
**Kind:** Inspected  
The combined file-read command in E03 displayed `README.md:1-13`. It documents Python 3.9+, standard-library-only/no-install setup, no live services or credentials, the complete suite command, the example command, and the source/test locations.

### E03 - Source and test trace
**Kind:** Inspected  
Commands, issued as one read-only shell invocation:  
`nl -ba README.md`  
`nl -ba quote.py`  
`nl -ba tests/test_quote.py`  
CWD: `/tmp/readiness-v51-evals/healthy-read-only/new/repo`  
Result: exit 0. `quote.py:5-8` implements validation and pricing; `quote.py:11-15` defines the CLI; `tests/test_quote.py:6-16` asserts two quotes and rejection of 0 and -1. No test invokes the CLI.

### E04 - Repository execution deliberately omitted
**Kind:** Not run  
The documented suite `python3 -m unittest discover -s tests -v`, example `python3 quote.py 4`, imports, setup checks, and a mutation probe were not run because the user prohibited repository command execution, imports, and mutation. There is therefore no observed pass/fail result, test count, runtime version, deliverable output, or probe outcome. The report validator was also not run, as directed for strict file-only/read-only cases.

### E05 - Skill and contract inspection
**Kind:** Inspected  
Commands: `sed -n '1,260p' /tmp/readiness-v51-evals/skill-candidate-2/SKILL.md`; then `sed -n '1,320p' /tmp/readiness-v51-evals/skill-candidate-2/references/report-contract.md` and `sed -n '1,320p' /tmp/readiness-v51-evals/skill-candidate-2/references/judgment.md`.  
CWD: `/tmp/readiness-v51-evals`  
Result: both invocations exited 0. Only the specified skill and its required references were consulted.
