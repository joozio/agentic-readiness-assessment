# Agentic readiness assessment: Rate-card package

## TL:TR

**Verdict:** Needs improvements  
**Confidence:** High  
**Delegation:** Reviewed source pricing and source CLI happy-path changes are supported; distributable changes are blocked by F01.

- The documented source check is fast and green: two tests exercise the pricing function and the source CLI with asserted output.
- The documented distributable workflow is broken. The build exits 0 but omits `data/rates.json`, so the built CLI exits 1 with `FileNotFoundError`.
- The primary test command stays green despite that broken deliverable because it never builds or runs `dist/`.
- First action: copy the runtime data into the distributable and add a test that builds and executes it from the produced directory.
- Agents can safely handle bounded source changes under review today, but should not be delegated packaging/release work until the build and regression gate pass together.

## Readiness checks

| Check | State | What this means |
|---|---|---|
| Setup | Passed | The documented Python 3.9+ prerequisite was satisfied by Python 3.14.3; the project is standard-library-only and the source check ran without installation (E02, E03). |
| Deliverable | Gap | The documented build completed, but its actual output could not run because a required data file was absent (E04, E05; F01). |
| Primary checks | Gap | The documented two-test suite passed while the documented distributable remained broken, so it does not protect that workflow (E03, E05, E06; F02). |
| Probe | Unverified | No mutation probe was run because the request explicitly prohibited one (E07). |

| Change task | State | Boundary and evidence |
|---|---|---|
| Modify positive-weight pricing calculation | Supported | The pure function and its value at weight 4 are directly tested; review remains necessary for untested weights and validation behavior (E03, E06). |
| Change the source CLI happy path | Supported | A subprocess test asserts exit 0 and exact output `13` for weight 4 using source data (E03, E06). |
| Build or change the distributable directory | Blocked | The documented artifact cannot execute until its runtime data is included; the current primary check does not detect this (E04, E05; F01, F02). |

## What to improve

### F01 - Include runtime data in the distributable
**Key:** include-distributable-rate-data  
**Priority:** P1  
**Owner:** Repo  
**Basis:** Demonstrated  
**Task:** Build or change the distributable directory  
**Effort:** Small  
**Why:** `build.py` reports success but produces an unusable documented deliverable; every invocation of the built CLI needs the missing rate file. Source execution remains a workaround, so not all development is blocked.  
**Evidence:** E04, E05, E06; `build.py:13-14` copies only Python files while `src/ratecard/app.py:13` reads `data/rates.json`.  
**Change:** Make the build create `dist/ratecard/data/` and copy `src/ratecard/data/rates.json` while preserving its relative path.  
**Verify:** From a clean generated-output state, the documented build exits 0, the output contains the data file, and `python3 dist/ratecard/app.py 4` exits 0 with exactly `13`.

### F02 - Put the distributable workflow behind the primary regression gate
**Key:** test-built-distributable  
**Priority:** P2  
**Owner:** Repo  
**Basis:** Demonstrated  
**Task:** Build or change the distributable directory  
**Effort:** Small  
**Why:** The current primary command passed even though the documented artifact failed, allowing packaging regressions to look healthy. The separately documented manual build/run commands expose the problem, but only when someone remembers to run both.  
**Evidence:** E03, E05, E06; `tests/test_ratecard.py:13-25` tests the pricing function and source entry point only.  
**Change:** Add a test that invokes the build in an isolated generated-output location or safely controls and cleans the repository’s documented `dist/`, then runs the produced CLI and asserts its exit status and output.  
**Verify:** The normal suite passes with a valid artifact; omitting the runtime data from a disposable build fixture makes the new test fail. This is a future closure check, not an executed probe.

## What already works

- The repository documents its Python requirement and gives concise, root-relative commands for both source verification and the distributable workflow (E02, E06).
- The executed source test uses a real subprocess and asserts both return code and exact output, while the pricing unit test asserts the current calculation (E03, E06).
- The six-file project has clear boundaries among CLI loading, pure pricing logic, runtime data, build logic, and tests; it has no declared network, service, credential, or third-party dependency boundary (E01, E06).

## Scope and limits

**Repository:** Local snapshot `/tmp/readiness-v51-evals/broken-package-executed/new-corrected/repo`  
**Scope:** Full repository: source pricing, source CLI, tests, runtime data, and documented distributable workflow.  
**Coverage:** Full  
**Mode:** Executed  
**Revision:** Non-Git six-file snapshot; initial and final SHA-256 inventories match (E01, E08).  
**Skill version:** 5.1.0

Assessed 2026-09-10 on Darwin arm64 with Python 3.14.3. No installation, network, credentials, services, commits, source edits, or mutation probe were used. Execution covered the documented source suite, build, and built CLI at weight 4; it did not cover other Python versions, invalid CLI inputs, pricing boundaries beyond the inspected `weight <= 0` guard, CI, deployment, or publication. There is no Git metadata or origin, so no commit revision or exact-revision CI evidence exists.

The build and tests created only `dist/` and Python `__pycache__` directories. Those generated paths were removed, and the final tree again contains only the original six files with identical hashes; no changes remain in the target (E08). The report was written outside the target as requested. Difficulty following the skill was low: its evidence and report requirements fit the request; the host rejected the first broad cleanup command before execution, so cleanup used explicit generated paths and was verified.

## Evidence

### E01 - Snapshot identity and initial inventory
**Kind:** Inspected  
From cwd `/tmp/readiness-v51-evals/broken-package-executed/new-corrected/repo`, `pwd` resolved to `/private/tmp/readiness-v51-evals/broken-package-executed/new-corrected/repo`; `git rev-parse --show-toplevel`, `git remote -v`, `git branch --show-current`, `git rev-parse HEAD`, and `git status --short --untracked-files=all` each reported that this is not a Git repository. `rg --files -g '!node_modules' -g '!vendor' -g '!dist' -g '!build' | sort`, `wc -l ...`, and `shasum -a 256 README.md build.py src/ratecard/app.py src/ratecard/pricing.py src/ratecard/data/rates.json tests/test_ratecard.py` established a six-file, 98-line snapshot and its baseline hashes.

### E02 - Supported interpreter and host
**Kind:** Executed  
`python3 --version` in the repository exited 0 with `Python 3.14.3`; `uname -s -m` exited 0 with `Darwin arm64`. This satisfies the documented Python 3.9+ prerequisite but does not verify other supported versions.

### E03 - Documented source check
**Kind:** Executed  
`python3 -m unittest discover -s tests -v` in the repository exited 0. It ran `test_quote` and `test_source_entry_point`; both passed, and the suite reported `Ran 2 tests` and `OK`.

### E04 - Documented build
**Kind:** Executed  
`python3 build.py` in the repository exited 0 and printed the generated `dist/ratecard` path. `find dist -type f -print -exec shasum -a 256 {} \;` then showed only `dist/ratecard/app.py` and `dist/ratecard/pricing.py` (plus no runtime data file); their hashes matched the corresponding source Python files.

### E05 - Documented distributable execution
**Kind:** Executed  
`python3 dist/ratecard/app.py 4` in the repository exited 1. The traceback ended in `FileNotFoundError` for `dist/ratecard/data/rates.json`, so no quote was produced.

### E06 - Workflow and assertion inspection
**Kind:** Inspected  
`nl -ba README.md build.py src/ratecard/app.py src/ratecard/pricing.py tests/test_ratecard.py` confirmed the documented commands (`README.md:6-17`), the build’s two-file copy list (`build.py:13-14`), the CLI’s relative data dependency (`src/ratecard/app.py:13`), the positive-weight guard and formula (`src/ratecard/pricing.py:4-7`), and the tests’ source-only scope (`tests/test_ratecard.py:13-25`). All repository files were read; no generated or historical report was used.

### E07 - Probe restriction
**Kind:** Not run  
A mutation probe was not run because the request explicitly prohibited source changes and mutation probes. No equivalent future result is treated as evidence.

### E08 - Cleanup and byte preservation
**Kind:** Executed  
An attempted `rm -rf` of the three exact generated paths was rejected by the host before execution. Cleanup then used `find /private/tmp/readiness-v51-evals/broken-package-executed/new-corrected/repo/dist -depth -delete` and the same command form for `src/ratecard/__pycache__` and `tests/__pycache__`; it exited 0. Final `find . -type f -print | sort`, directory inventory, and the same six-file `shasum -a 256 ...` command showed only the original files and hashes, with no remaining generated output or target change.

### E09 - Report validation
**Kind:** Executed  
`python3 /tmp/readiness-v51-evals/skill-candidate-2/scripts/validate_report.py /tmp/readiness-v51-evals/broken-package-executed/new-corrected/report.md` was run outside the target and exited 0. Validation checks report structure and consistency only; it does not establish the repository evidence.
