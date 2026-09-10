# Example reports

## Current format: version 5.1

These are untouched outputs from fresh GPT Sol / Codex assessments of the synthetic
[evaluation fixtures](../tests/evals/README.md) on 2026-09-10. Temporary paths identify
the original runs; they are provenance, not expected paths on your machine.

| Example | What to look for |
|---|---|
| [Healthy minimal repository](v5.1/healthy.md) | A detected and restored defect supports bounded work; a small CLI-test improvement can coexist with Ready. |
| [Misleading green check](v5.1/misleading-green.md) | Demonstrated feedback gap, inspected validation risk, separate task boundaries and stable finding Keys. |
| [Mixed Python/JavaScript workspace](v5.1/mixed-components.md) | Both components are exercised; a real bridge check informs conditional advice for shared payload changes. |
| [Broken distributable](v5.1/broken-distributable.md) | Green source tests coexist with an unusable artifact; a no-mutation constraint leaves the probe Unverified. |
| [Documentation-only repository](v5.1/docs-only.md) | A valid manual workflow does not imply a missing application toolchain. |
| [Strict read-only assessment](v5.1/read-only.md) | No repository execution or target writes; useful conditional advice without inventing test results. |

The integrating reviewer also ran the validator after these trials. In the
read-only case, the assessment agent itself performed manual review only. Validation
does not establish evidence truth. [The 5.1 evaluation record](../docs/EVALUATION-5.1.md)
includes failed and ambiguous trials, constraints and limits. Private application
reports are not published here.

## Previous format: version 5.0

These examples assess the synthetic [parcel-quote fixture](../tests/fixtures/tiny-cli).
They came from independent Claude Code / Claude Opus 5 assessments on 2026-09-09,
then received the editorial corrections listed below. They are reviewed examples,
not untouched model output or evidence of compatibility with every harness.

| Example | Mode | Verdict | Published words |
|---|---|---|---:|
| [Executed assessment](v5/executed.md) | Local checks and reversible probe | Ready for bounded changes | 812 |
| [Read-only assessment](v5/read-only.md) | File inspection only | Inconclusive | 734 |

Both retain two inspected improvements: CLI regression coverage and the invalid-input
experience. Execution demonstrated that a pricing defect is caught and restoration
returns the suite to green. Read-only evidence cannot establish that behavior.

Publication edits:

- Replaced the temporary assessed-tree path with `/workspace/parcel-quote` in both.
- Executed: restored omitted `python3` prefixes, recorded the exact probe command and
  bytecode setting from the transcript, and removed an uncaptured numeric probe exit
  status. The observed failing test and restored green result are unchanged.
- Read-only: made delegation conditional on running checks, removed a claim of proven
  regression protection, marked the unexecuted runnable CLI Unverified, and clarified
  that tests alone do not prove the CLI or probe. The verdict and findings are unchanged.

The raw outputs were 789 and 733 words. See [evaluation notes](../docs/EVALUATION.md)
for the upstream comparison, observed failures and limits. No private project report
is published here.

## Historical upstream format: version 4

The [fs-demo-project report](fs-demo-project/agentic-readiness.md) is the original
upstream Next.js example: 71/100, Partially ready, Medium confidence. It uses the old
scoring contract and must not be validated with the v5 validator or compared
numerically with a v5 verdict.

Upstream anonymized the CI host, project group, local database password, machine,
agent product and tool-specific identifiers. Its scores, findings and evidence
remain unchanged in this fork.
