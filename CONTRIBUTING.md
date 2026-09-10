# Contributing

This fork maintains one portable skill and a human report contract. Improve the
reader's decision, not the number of instructions the agent has to follow.

## Checks

```sh
python3 -m unittest discover -s skills/agentic-readiness-assessment/tests -v
python3 -m unittest discover -s tests -v
python3 tests/evals/runner.py check
```

The first suite checks task/verdict consistency, evidence basis, stable finding
comparison, safe export and CLI behavior. The second checks packaging/version
consistency and self-contained copies. The fixture runner verifies the known local
behaviors of five tiny repositories; JavaScript cases need Node. These deterministic
checks are separate from evaluating an agent. For optional Claude packaging:

```sh
claude plugin validate . --strict
```

## Skill changes need behavior evidence

Use the [evaluation suite](tests/evals/README.md) in disposable copies, with its
oracles kept outside the agent's view. Preserve a baseline skill before editing.
Run a fresh agent for each old/new case with the same prompt and permissions.
The historical `tests/fixtures/tiny-cli` remains available for v5 reproduction.
Examples of supported cases:

- "Assess this repo. Run safe local checks and give me a short human report."
  Expect evidenced checks, a restored relevant probe, and a readable TL:TR.
- "Assess supplied files only. No repository commands, imports, installs or source
  edits. Write the report and review its contract manually."
  Expect unverified execution, explicit limits, no invented run or repo penalty
  solely for the constraint. Findings may still follow from inspected code.
- Near miss: "Change the shipping base fee to 7 and update the tests."
  This is implementation work, not an instruction to launch a readiness assessment.

Inspect the transcript and final tree, not just the final response. Compare scope,
correctness, evidence, safety, word count and next-action clarity against a baseline.
Record the tested harness/model when available without claiming universal testing.
Keep timing/token telemetry when available and label missing telemetry unavailable.
Grade semantic outcomes separately from validator success. Re-run relevant cases
after prompt corrections, preserve the failed trial, and report the actual revision
tested. A single attempt is an observation, not a reliability estimate.

## Report and version changes

`metadata.version` in the self-contained SKILL.md and all plugin manifest versions
must agree. A breaking report/verdict change requires a major bump. Prompt behavior
changes use a minor bump; packaging-only fixes use a patch. Preserve licensed
upstream attribution and synchronize the bundled NOTICE/LICENSE.

Examples must state whether they are real runs, synthetic fixture runs or editorial
renderings of previously collected evidence. Never publish private project reports
or turn a hand-written example into supposed model evaluation evidence.

Open a PR to this fork with the user-visible change, checks and behavioral evidence.
No CLA signing workflow is used here; upstream's retained CLA is historical provenance.
