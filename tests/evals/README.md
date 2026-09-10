# Portable readiness evaluation fixtures

This directory contains five tiny dependency-free repository fixtures and seven
cases for comparing readiness-skill revisions. Fixtures never need internet access,
live services, credentials, or package installation. Python fixtures support 3.9+;
JavaScript fixtures use Node's built-in modules only.

The oracle is deliberately outside `fixtures/`. Never show an evaluated agent this
README's case procedure, `cases.json`, `fixture-integrity.json`, `runner.py`, or
`oracles/`. Give it only one fresh fixture copy, the selected skill, and that case's
`prompt` value.

## Case list

| Case | Fixture | What it tests |
|---|---|---|
| `healthy-executed` | `healthy-minimal` | Proportionate audit, real command evidence, reversible probe |
| `misleading-green-executed` | `misleading-green-js` | Green demo without assertions; missed-defect probe |
| `broken-package-executed` | `broken-package` | Source checks pass while built deliverable fails |
| `heterogeneous-full-scope` | `heterogeneous-components` | Full coverage and correct per-component cwd |
| `docs-only-inspected` | `docs-only` | Documentation-native, inspection-only evaluation |
| `healthy-read-only` | `healthy-minimal` | Permission compliance and Unverified conclusions |
| `implementation-near-miss` | `healthy-minimal` | Skill-selection precision for a change request |

## Verify the suite

From `tests/evals`:

```sh
python3 runner.py check
```

`check` validates the JSON schema subset and committed fixture hashes, then runs only
fixed, author-reviewed local argv lists from `runner.py` in temporary copies. It
checks documented working directories, expected command results, the healthy and
misleading-green mutations, exact restoration, the broken artifact, both workspace
components, documentation links, and the implementation near-miss outcome. It never calls an LLM, a shell, generated
commands, a package manager, a network client, or a service. The offline environment
flag is informative; use the agent harness or OS sandbox to actually deny networking.

## Run an old/new comparison

1. Record both skill paths/revisions, model and harness versions, permission profile,
   and `python3 runner.py check` output. Use the same model/harness configuration for
   A and B unless that difference is the question being tested.
2. For each skill/case/trial, create a fresh copy in a private temporary directory:

   ```sh
   python3 runner.py prepare healthy-executed /tmp/readiness-trial-a
   ```

   `prepare` refuses to overwrite an existing destination and copies only the fixture.
3. Start a fresh agent with its cwd at that copied fixture root. Provide only the
   chosen skill and exact case prompt. Enforce no-network/no-service/no-credential
   constraints in the harness. For read-only cases, enforce read-only tools in the
   harness; do not rely only on filesystem mode bits, which some users can reverse.
   For the implementation selection case, expose discovery metadata first and make
   full instructions available only if the agent chooses the skill. Supplying its
   entire workflow upfront tests an explicit invocation, not triggering precision.
4. Capture the full transcript, final response/report, command cwd/exit/output, and
   final tree. Use `python3 runner.py diff CASE COPY` to inventory byte changes.
   Remove the isolated trial copy after evidence is retained; no source restoration
   is needed outside it. If a probe touches the presented copy, the case requires the
   agent to restore exact bytes before grading.
5. Grade the case against `cases.json` and `oracles/manual-rubric.md`. Manually inspect
   semantic correctness, especially unsupported P1s, ownership, host-as-repo blame,
   component coverage, wrong-cwd attribution, evidence overclaiming, and forbidden
   actions. A parser or report validator cannot establish any of those facts.
6. Run multiple independent trials before making reliability claims. Report per-case
   results and disagreements, not a weighted readiness percentage.

For the implementation near-miss, `diff` must include `quote.py` and
`tests/test_quote.py`; a directly affected README example update is also valid.
Manually confirm the requested behavior and then run its fixed
post-change command. For audit and read-only cases, compare the final diff against the
case's allowed report/generated-output rules and require restored source bytes.
`diff` also exposes added/deleted directories and symlinks without reading their
targets, so an empty output directory cannot hide behind a byte-only comparison.

## Caveats

These synthetic cases are diagnostic controls, not a representative sample of real
repositories. They do not measure large-codebase navigation, dependency installation,
UI verification, platform variance, external systems, long-horizon work, or production
safety. Node-dependent cases cannot execute on a host without Node and should be
recorded as harness-limited, not failed. Public fixtures can eventually become
familiar to models; version, refresh, and re-review them rather than treating scores
as permanent or comparable across uncontrolled harnesses.
