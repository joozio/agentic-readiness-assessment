# Contributing

This fork maintains one portable skill and a human report contract. Improve the
reader's decision, not the number of instructions the agent has to follow.

## Checks

```sh
python3 -m unittest discover -s skills/agentic-readiness-assessment/tests -v
python3 -m unittest discover -s tests -v
```

The first suite tests meaningful validator invariants: false Ready claims,
environment-only blockers, missing evidence, read-only mode, duplicate IDs and CLI
behavior. The second checks packaging/version consistency and self-contained copies.
CI runs both using the Python standard library. For optional Claude packaging:

```sh
claude plugin validate . --strict
```

## Skill changes need behavior evidence

Use disposable fixtures, not production services. `tests/fixtures/tiny-cli` is a
synthetic standard-library project for exercising the full loop. Run a fresh agent
with each relevant prompt, giving it the skill and raw fixture only:

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
