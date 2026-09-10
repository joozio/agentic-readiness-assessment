# Calibrate decisions to evidence and work

This is a development-conditions assessment, not a model benchmark. Passing checks
support a named change path under the tested conditions. They do not predict agent
success rates, productivity gains or readiness for unrelated components.

## Finding basis

- **Demonstrated:** an attributable in-scope failure or wrong outcome was observed
  locally or in exact-revision CI. Name the actual command/path and consequence.
- **Inspected:** files establish a weakness, but its operational consequence was
  not exercised. Explain the inference and any compensating control. Say “can miss
  an incorrect outcome”, not “accepted incorrect outcomes”, unless observed.
- **Hypothesis:** a needed premise is missing. Usually record the question in
  Scope and limits. If resolving it warrants an action, use a P3 investigation with
  a confirmation check. It cannot establish a readiness Gap or a negative verdict.

An inspected contradiction is a documentation defect; that does not demonstrate
that installation fails. A test command exiting zero demonstrates its execution,
not the behavior of skipped tests. A missing lockfile in a library is not inherently
a defect. A documented supported range may be intentional.

## Priority means action order

Judge consequence, task exposure, evidence and existing controls together. Put the
reason in Why; avoid a second numerical severity score.

| Priority | Threshold |
|---|---|
| P1 | A demonstrated failure blocks necessary work or creates a consequential wrong outcome; alternatively, tightly evidenced high-consequence exposure with no effective control. |
| P2 | A meaningful recoverable defect, recurring friction, or localized verification weakness; a useful path or workaround remains. |
| P3 | A small refinement or a clearly labeled investigation of an unconfirmed concern. |

Do not promote every absent assertion, unpinned dependency or missing CI tool to
P1. Ask what actually goes wrong, on which selected task, and what already catches
it. A statically visible destructive path can merit P1 without executing it, but
spell out the complete causal chain and why existing controls do not contain it.
Do not run a dangerous reproduction merely to obtain a stronger evidence label.

## Bound delegation

Choose concrete tasks from the user's purpose or observed entry points. For each,
identify the relevant setup, behavior check, artifact and review gate. If the CLI
is tested but a service integration is only inspected, support reviewed CLI work
and leave that integration Conditional or Unverified. Directory inventory alone is
not execution coverage. A host prerequisite failure narrows evidence; a repo-owned
broken setup can block the task even on a fully capable host.

Examples:

- A stdlib CLI with meaningful behavior tests and a detected boundary defect can
  support reviewed pricing-rule edits without a linter, CI or instruction file.
- A demo that merely prints its output has an inspected verification weakness.
  A contract-violating, exercised mutation that stays green demonstrates a gap.
- A passing source-tree import does not prove the installed wheel contains its
  runtime assets. Exercise the installed artifact outside the source directory.
- A surviving equivalent mutation or a check importing another copy is an invalid
  probe. Correct the audit setup or report Unverified; do not blame the repository.

For read-only assessment, useful inspected P2 findings may coexist with Inconclusive.
No execution evidence means delegation stays conditional. A strong negative claim
requires equally specific evidence; validator success cannot supply it.
