# Agentic readiness assessment: Shipping quote check

## TL:TR

**Verdict:** Needs improvements  
**Confidence:** High  
**Delegation:** Shipping-rate edits are conditional on adding outcome assertions or having a reviewer explicitly verify the printed values; the current green command is not a reliable regression gate.

- The full four-file project is easy to understand and runs without dependencies, network access, credentials, or services.
- Both documented entry points run successfully, but success only means the examples were printed.
- A relevant formula defect changed both quoted prices while `node check.js` and `npm test` still exited 0. This is a demonstrated feedback-loop gap, not an inferred concern.
- First action: turn the example comparisons into assertions that exit nonzero on a wrong result, then retain the two current cases and add invalid-input cases.

## Readiness checks

| Check | State | What this means |
|---|---|---|
| Setup | Passed | Node v25.8.1 and npm 11.11.0 were available; the dependency-free documented commands ran from the repository root (E01, E03). |
| Deliverable | N/A | This snapshot declares a private, source-only module and no package, site, deployment, or other produced artifact (E02). |
| Primary checks | Gap | The only check exits 0 after printing incorrect observed values beside the expected values (E03, E04; F01). |
| Probe | Gap | A pricing-formula mutation reached the executed module and visibly changed results, but neither check rejected it (E04; F01). |

| Change task | State | Boundary and evidence |
|---|---|---|
| Modify the shipping price formula | Conditional | The entry point and examples are clear, but require explicit human comparison until F01 is fixed; the automated exit status missed the exercised pricing defect (E02–E04). |
| Change invalid-weight validation | Unverified | The guard is easy to locate, but the repository check exercises only positive integers and provides no executed feedback for zero, negative, fractional, or non-number inputs (E02, E03; F02). |

## What to improve

### F01 - Make wrong quote outcomes fail the check
**Key:** quote-outcome-assertions  
**Priority:** P2  
**Owner:** Repo  
**Basis:** Demonstrated  
**Task:** Modify the shipping price formula  
**Effort:** Small  
**Why:** The advertised check can signal success for incorrect shipping prices. Its printed `got` and `expected` values are a useful manual control, so the defect is localized and recoverable rather than a complete work blocker.  
**Evidence:** E03, E04; `check.js:5-8` prints comparisons and a completion message without asserting equality or setting a failing exit status.  
**Change:** Assert each result against its expected value using Node's standard library or an equivalent dependency-free mechanism; only print completion after all assertions pass.  
**Verify:** The unchanged examples exit 0, while a temporary `5 + 2 * weight` to `6 + 2 * weight` mutation produces a nonzero exit and identifies the mismatched case; restore the mutation and reconfirm the baseline.

### F02 - Cover the input-validation contract
**Key:** quote-input-validation-cases  
**Priority:** P2  
**Owner:** Repo  
**Basis:** Inspected  
**Task:** Change invalid-weight validation  
**Effort:** Small  
**Why:** `quote()` defines a positive-integer boundary, but the check covers only weights 1 and 4. A validation change can therefore lack repository-provided feedback; this consequence was not mutation-tested.  
**Evidence:** E02, E03; `shipping.js:4-6` defines the guard while `check.js:5` supplies only valid integers.  
**Change:** Add assertions for representative zero, negative, fractional, and non-number inputs, including the expected error contract.  
**Verify:** Valid cases still pass, every invalid case rejects with the documented error, and a temporary boundary reversal causes the check to exit nonzero before exact restoration.

## What already works

- The README names the behavior file, working directory, dependency model, and one-line check; both documented command forms executed locally (E01, E03).
- The implementation has a small, direct boundary: `check.js` imports the single exported `quote()` function, with no storage or external-service path to configure (E02).
- The check prints actual and expected values together, so the exercised defect was immediately visible even though its process status was wrong (E04).

## Scope and limits

**Repository:** Local snapshot `/tmp/readiness-v51-evals/misleading-green-executed/new/repo`  
**Scope:** Full repository: README, package metadata, shipping quote module, and check runner.  
**Coverage:** Full  
**Mode:** Executed  
**Revision:** No Git metadata or origin was present; assessed the four-file snapshot whose initial and final SHA-256 hashes match (E01, E05).  
**Skill version:** 5.1.0

Assessment date: 2026-09-10. Tested with Node v25.8.1 and npm 11.11.0. No network access, installation, credentials, services, CI, packaging, or deployment were exercised; the snapshot contains no declared paths for the latter three. Confidence is high for this small declared scope because every file was inspected, both check entry points ran, and the central behavior received a valid reversible probe. This does not authorize unattended merge, release, or production use.

Following the skill was straightforward because the project and documented workflow are small. The only cleanup difficulty was that the first textual reversal in the disposable copy normalized one redundant trailing newline and failed the exact-hash check. The pristine target bytes were then copied back into that disposable file, `cmp` and SHA-256 confirmed an exact match, the baseline was rerun, and the disposable directory was removed (E04, E05). No target source bytes changed, and no changes remain in the target.

## Evidence

### E01 - Scope, snapshot, and runtime
**Kind:** Executed  
From `/tmp/readiness-v51-evals/misleading-green-executed/new/repo`, `git status --short --branch` and `git rev-parse HEAD` each reported that the directory is not a Git repository. `rg --files -g '!reports/**' -g '!node_modules/**' -g '!vendor/**' | sort` listed `README.md`, `check.js`, `package.json`, and `shipping.js`. `node --version` returned `v25.8.1`; `npm --version` returned `11.11.0`.

### E02 - Workflow and behavior trace
**Kind:** Inspected  
`README.md:3-13` declares a dependency-free local check and points to `shipping.js`; `package.json:1-7` maps `npm test` to `node check.js`; `check.js:3-8` imports `./shipping`, calls it for weights 1 and 4, and only logs results; `shipping.js:3-10` validates the input, computes `5 + 2 * weight`, and exports `quote`. No external or storage boundary exists in the snapshot.

### E03 - Baseline checks
**Kind:** Executed  
From the target root, `node check.js` exited 0 and printed `1kg: got 7, expected 7`, `4kg: got 13, expected 13`, and `2 examples checked`. `npm test` also exited 0 with the same application output. No install step was needed or run.

### E04 - Reversible defect probe
**Kind:** Executed  
The target was copied to `/tmp/readiness-v51-probe.pabDW1/repo`. Baseline `node check.js` and `npm test` exited 0. In only that copy, `shipping.js` was changed from `return 5 + 2 * weight;` to `return 6 + 2 * weight;`. Both commands still exited 0 while printing `got 8, expected 7` and `got 14, expected 13`, proving the mutated source was reached and the required observable result was wrong. After restoration, `node check.js` and `npm test` again exited 0 with 7 and 13. Exact-byte restoration required the cleanup step described in E05.

### E05 - Restoration and remaining changes
**Kind:** Executed  
`shasum -a 256 README.md package.json shipping.js check.js` was run before and after the probe. Final target hashes matched the initial values: README `83a71af7…6438`, package metadata `8e45d30c…e5ee`, implementation `02e8f7fb…293`, and runner `fb8b48fc…44e8b`. In the disposable copy, `cmp -s` confirmed all four files matched the target exactly. `find /tmp/readiness-v51-probe.pabDW1 -depth -delete` removed the audit-created copy, and `test ! -e /tmp/readiness-v51-probe.pabDW1` exited 0. A final target `find . -maxdepth 2 -type f -print | sort` still listed only the original four files. No target changes remain.

### E06 - Report validation
**Kind:** Executed  
`python3 /tmp/readiness-v51-evals/skill-candidate/scripts/validate_report.py /tmp/readiness-v51-evals/misleading-green-executed/new/report.md` completed successfully. A manual semantic review also confirmed that execution claims are limited to observed commands, the missed mutation supports only the pricing task, future closure checks are not presented as evidence, and cleanup is disclosed.
