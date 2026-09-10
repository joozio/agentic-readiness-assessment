# Agentic readiness assessment — Dispatch workspace

## TL:TR

**Verdict:** Inconclusive
**Confidence:** Medium
**Delegation:** Reviewed quote-calculation and widget-formatting changes are supported when their component checks are rerun; shared payload-shape changes require the explicit bridge check.

- Both documented, dependency-free component checks pass on the available Python and Node runtimes.
- The live Python-to-JavaScript payload bridge also passes, but it is absent from the documented regression checks, so coordinated schema work needs an extra check.
- The Python suite does not cover negative weights even though the implementation rejects all non-positive values.
- First action: make the quote-to-widget contract an explicit, documented regression check.
- Overall readiness remains Inconclusive because the requested no-mutation constraint leaves defect-detection sensitivity Unverified; this is an evidence limit, not a repository failure.

## Readiness checks

| Check | State | What this means |
|---|---|---|
| Setup | Passed | Both components require no installation; Python 3.14.3 satisfies the documented 3.9+ requirement and Node v25.8.1 ran the dependency-free widget (E01–E03). |
| Deliverable | N/A | The declared outputs are source-only logic/helpers with no package, site, or release artifact; their runnable behavior was exercised directly (E02–E04). |
| Primary checks | Passed | Both complete checks documented in `README.md` passed from their required working directories (E02, E03). |
| Probe | Unverified | No mutation probe was run because the request explicitly prohibited it (E06). |

| Change task | State | Boundary and evidence |
|---|---|---|
| Modify valid-weight quote calculation | Supported | `quote(4)` is asserted end-to-end within the Python module boundary; rerun the Python suite and review untested inputs (E02, E05). |
| Modify widget currency/amount formatting | Supported | The actual renderer is checked for two currencies and integer/fractional amounts; rerun `node check.js` (E03, E05). |
| Change the shared quote payload shape | Conditional | Current Python output renders correctly, but neither declared component check crosses the language boundary; rerun an explicit bridge check until F01 is closed (E04, E05). |

## What to improve

### F01 - Check the cross-component quote contract
**Key:** quote-widget-contract-check
**Priority:** P2
**Owner:** Repo
**Basis:** Inspected
**Task:** Change the shared quote payload shape
**Effort:** Small
**Why:** `quote.py` produces `currency` and `amount`, while `render.js` consumes those fields. The current bridge works, but the two declared checks can both remain green if one component's source and unit fixture change while the other component does not.
**Evidence:** E04 confirms the current integration; E05 shows that the documented checks exercise only isolated fixtures.
**Change:** Add and document a dependency-free contract check that feeds actual quote output to the actual renderer. It may remain a separate check; a root build system is not required.
**Verify:** Run both component checks and the committed contract check; all exit 0, then confirm a locally isolated payload-field mismatch makes the contract check exit nonzero and restore exact bytes.

### F02 - Cover the full invalid-weight boundary
**Key:** negative-weight-regression-check
**Priority:** P2
**Owner:** Repo
**Basis:** Inspected
**Task:** Modify valid-weight quote calculation
**Effort:** Small
**Why:** The implementation rejects `weight <= 0`, but the test asserts rejection only for zero. A change that accepts negative weights can therefore escape the current suite even though it violates the implementation's present boundary.
**Evidence:** E05; `services/quote/quote.py:5-6` defines the boundary and `services/quote/tests/test_quote.py:10-12` covers only zero.
**Change:** Add a representative negative-weight assertion while preserving the existing zero-boundary assertion.
**Verify:** The normal Python suite exits 0; in an isolated reversible probe, changing the predicate so negative values are accepted makes the negative-weight test fail, after which exact bytes and the green baseline are restored.

## What already works

- The root README clearly names both components, their prerequisites, exact commands, and required working directories, and warns that full-workspace work must account for both (E01).
- The Python check imports the production function and asserts both a concrete quote result and invalid-zero behavior; both tests pass (E02, E05).
- The JavaScript check imports the production renderer and asserts exact observable strings across two currencies and numeric shapes; both checks pass (E03, E05).
- The actual cross-language flow currently produces `USD 13.00`, demonstrating that the checked snapshot's producer and consumer agree today (E04).

## Scope and limits

**Repository:** Local snapshot `/tmp/readiness-v51-evals/heterogeneous-full-scope/new/repo`
**Scope:** Full workspace: root guidance, Python quote logic/tests, and JavaScript widget renderer/check.
**Coverage:** Full
**Mode:** Executed
**Revision:** Non-Git snapshot; five target files with SHA-256 manifest digest `1ecdd0491e70d175518b108a14c609a0171118f6a71e31d1da3339e3a0137282` after checks.
**Skill version:** 5.1.0

Assessment date: 2026-09-10. Tested platform: Darwin 25.4.0 arm64, Python 3.14.3, Node v25.8.1. All five target files were inspected; there were no applicable agent-instruction files, package manifests, generated directories, or Git metadata. No installation, network, credentials, services, source writes, or mutation probe were used. The bridge command is assessment evidence, not a committed repository check. CI, packaging, deployment, performance, browser presentation, and production behavior are outside the declared workspace and were not assessed. The report is stored outside the target. Validation of report shape does not add repository evidence.

## Evidence

### E01 - Inventory, instructions, and runtime prerequisites
**Kind:** Executed
From `/tmp/readiness-v51-evals/heterogeneous-full-scope/new/repo`, `find . -type f -not -path './.git/*' -print | sort` found exactly the README and four component files. `python3 --version` returned `Python 3.14.3`; `node --version` returned `v25.8.1`. Inspection of `README.md:3-12` established the no-install design, two components, exact checks, working directories, and lack of an aggregate command. `git rev-parse --show-toplevel` reported that the snapshot is not a Git repository.

### E02 - Python quote check
**Kind:** Executed
Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`; cwd: `/tmp/readiness-v51-evals/heterogeneous-full-scope/new/repo/services/quote`. Result: exit 0; two tests ran and passed (`test_quote_shape_and_value`, `test_invalid_weight`).

### E03 - JavaScript widget check
**Kind:** Executed
Command: `node check.js`; cwd: `/tmp/readiness-v51-evals/heterogeneous-full-scope/new/repo/web/widget`. Result: exit 0 with `2 widget checks passed`.

### E04 - Actual producer-to-consumer bridge
**Kind:** Executed
Command from the repository root: `set -o pipefail; PYTHONDONTWRITEBYTECODE=1 python3 -c 'import json, sys; sys.path.insert(0, "services/quote"); from quote import quote; print(json.dumps(quote(4)))' | node -e 'const assert = require("assert"); const { renderQuote } = require("./web/widget/render"); let s=""; process.stdin.on("data", c => s += c); process.stdin.on("end", () => { assert.strictEqual(renderQuote(JSON.parse(s)), "USD 13.00"); console.log("quote-to-widget bridge passed"); });'`. It imported both actual implementations and exited 0 with `quote-to-widget bridge passed`.

### E05 - Behavior and check-boundary inspection
**Kind:** Inspected
`services/quote/quote.py:4-7` rejects all non-positive weights and returns the two-field payload. `services/quote/tests/test_quote.py:6-12` checks one valid value and zero only. `web/widget/render.js:3-5` consumes both fields; `web/widget/check.js:3-8` uses hand-built JavaScript objects rather than Python output and asserts exact results.

### E06 - Mutation sensitivity
**Kind:** Not run
The request explicitly prohibited a mutation probe and all source modification. Consequently, no claim is made that the existing checks detect a deliberately introduced relevant defect.

### E07 - Preservation and cleanup
**Kind:** Executed
Before execution and after all repository checks, `find . -type f -not -path './.git/*' -exec shasum -a 256 {} + | sort` returned the same five paths and individual hashes. The final manifest command, `find . -type f -not -path './.git/*' -exec shasum -a 256 {} + | sort | shasum -a 256`, returned the recorded digest. No service was started and no cleanup was required; there were no pre-existing or remaining target changes to report.
