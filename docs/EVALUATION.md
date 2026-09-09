# Version 5 evaluation

## Method

On 2026-09-09, fresh Claude Code threads using Claude Opus 5 assessed separate copies
of `tests/fixtures/tiny-cli`. Each received a realistic request, the skill path and
raw files, without suggested findings. The fixture has three files, a standard-library
CLI and two behavior tests; it has no Git metadata or CI. Execution runs permitted
local commands and a reversible probe, but no installs or production access.
Read-only runs prohibited repository commands, imports, installs and source edits,
while permitting a new report file. Transcripts and final source bytes were reviewed.

The upstream baseline used Exadel version 4.5.0 at
`ab8b60b5a379c2ec047e74bf37b37a87176d8163`. The revised runs used the working v5
instructions. This is a small behavioral comparison, not a statistical benchmark.

## Results

Word counts include headings, tables and evidence, using whitespace-separated tokens.

| Run | Raw words | Outcome | Observed behavior |
|---|---:|---|---|
| Upstream v4, executed | 6,499 | 52/100; Partially ready | Two tests pass; boundary defect caught and restored; validator passes. |
| V5 first pass, executed | 1,150 | Needs improvements | Probe caught; wrong-directory and audit-created cache findings were false positives. |
| V5 first pass, read-only | 1,187 | Inconclusive | No forbidden execution; minor findings exposed a verdict/validator ambiguity. |
| V5 retest, executed | 789 | Ready for bounded changes | Two tests pass; wrong multiplier caught and restored; two useful findings. |
| V5 retest, read-only | 733 | Inconclusive | No forbidden execution; two inspected findings; overconfident prose still needed correction. |

The executed retest was about 88% shorter than the same-fixture upstream report.
Both versions caught a real behavior defect. V5 removed repeated score/finding
sections and did not turn the documented working-directory requirement into a defect.
The differing verdicts reflect changed decision rules, not an improved fixture.

Source files in the baseline and both retests matched the original fixture byte for
byte after completion. The revised executable run used a disposable probe copy and
disabled bytecode writing. The read-only run wrote only its allowed report.

A separate fresh-thread selection check exposed just the new skill description and
asked: “Change the shipping base fee to 7 and update the tests.” The agent did not
select the audit skill, made the change and passed three tests. This checks one
near-miss decision; it does not test any client's automatic skill registry.

## Changes supported by the runs

- Allow inspected P2/P3 findings with an Inconclusive execution verdict; align the
  validator with that rule. A demonstrated check Gap or critical finding still wins.
- Separate absent host tools, incorrect audit commands and audit-created cache
  effects from repository defects.
- Make field syntax explicit and accept ASCII hyphens in finding/evidence headings.
- Treat tiny-report length as guidance so agents do not remove necessary evidence.
- Define the report destination relative to the assessed root, with artifact/chat
  fallback when the tree itself must remain read-only.
- Distinguish host metadata from repository execution; narrower user limits prevail.
- Clarify that an unexecuted runnable script is an Unverified deliverable even when
  no packaging step exists, and keep read-only delegation advice conditional.

The last two semantic clarifications were reviewed and applied to the published
examples, not tested in another blind round. The examples document their editorial
changes. We do not present those corrections as raw model behavior.

## Deterministic checks and limits

The standard-library validator has 21 tests for evidence references, verdict
consistency, read-only constraints, ownership and CLI behavior. Five packaging tests
check version agreement, attribution, local references and copied-folder execution.
The two published v5 examples validate. CI tests Python 3.9 and 3.14.

Behavior was evaluated on one harness/model and one small Python fixture. Cross-model
reliability, large monorepos, no-shell hosts, other ecosystems and marketplace
installation remain unproven. The skill has no mandatory harness dependency and
supports manual report review, but portability of instructions is not proof of
identical behavior everywhere. The validator cannot establish evidence truth or
prevent unsupported prose; the read-only retest demonstrated that limitation.
