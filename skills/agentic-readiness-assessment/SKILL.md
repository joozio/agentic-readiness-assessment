---
name: agentic-readiness-assessment
description: >-
  Assess how reliably an AI coding agent can understand, change and verify a
  repository. Use for agent-readiness audits, evidence-backed development workflow
  reviews, and prioritized readiness improvements. Produces a readable report
  beginning with TL:TR key findings and insights. Not a general code review,
  product security certification, or request to implement fixes.
license: Apache-2.0
metadata:
  version: "5.0.0"
---

# Agentic Readiness Assessment

Help a maintainer decide **what an agent can take on today, what gets in its way,
and which improvement is worth making first**. Deliver a human-readable Markdown
report with evidence. Do not implement fixes as part of an audit.

## Adapt to the host

Use available file/search/command tools. No particular model, CLI, plugin, MCP or
subagent is required. Work sequentially unless delegation is available and useful.
Never assume a shell, Python, browser, network, permission setting or model pin.

- With execution access, exercise relevant safe repository checks.
- With read-only access or supplied files, inspect them and mark execution-dependent
  conclusions Unverified. Still produce a useful report.
- Without file writing, return the report in the conversation.
- Python 3.9+ can run the optional validator. Without it, check the contract manually.
  Missing audit tools limit evidence; they do not make the repository defective.

Read [the report contract](references/report-contract.md) before reporting. Read
[probe guidance](references/probe.md) only when a safe change probe is feasible.

## Establish scope and baseline

Resolve the actual target: historical copies and nested/generated directories can
mislead. Read local guidance and documented setup/check commands. Follow the user's
scope; clarify only ambiguities that materially change the target or allowed actions.

Record revision, dirty/untracked state and component boundaries when available.
Preserve existing edits. Map all components; cover them or explicitly name exclusions.
A focused audit is valid; silently sampling and calling it full coverage is not.
Prefer a disposable copy/worktree when other workers or services use the checkout.
Tie evidence to the tested revision. Concurrent edits are not yours to revert.
Without Git, identify the supplied snapshot/file set rather than inventing a commit.

## Trace a real change

Find one representative feature's entry point, behavior, storage/external boundary
and verification, including UI where relevant. Assess:

- **Understand:** can an agent find the right code and applicable instructions?
- **Set up:** does a newcomer obtain a working, repeatable environment? Library
  version ranges may be appropriate; assess dev/deployment resolution separately.
  A constraints file does not prove every target-platform dependency is pinned.
- **Produce:** can it build/package/render/validate the actual deliverable?
- **Check:** do tests, policy or schema checks verify meaningful behavior?
- **Deliver:** do local checks, CI and review expectations agree? Test installed
  artifacts where source-tree tests could hide packaging defects.
- **Contain risk and cost:** are fixtures disposable, failure messages actionable,
  generated files recognizable and important boundaries enforced?

Do not demand a formatter, lockfile, browser or container because another ecosystem
uses one. Name the lost capability before declaring a missing tool a finding. File
size is relevant only when it caused friction on the traced change path.

## Gather evidence proportionately

Read commands before running them, including install hooks and fixtures. A command's
name is not proof of safety. Use disposable paths and synthetic data. Required
registry downloads are reasonable when permitted. Authorized authenticated metadata
reads are different from exercising production credentials/data as test fixtures.
Never expose credential values in commands, output or reports.

An audit does not authorize deployment, publication, messages, paid calls, privilege
escalation or destruction of existing state. Record such checks as not run and use
a legitimate local substitute where available. Do not request unnecessary risky
actions merely to finish the audit.

Retain exact command, cwd, result and relevant artifact/failure location. Distinguish
Executed, CI evidence, Inspected and Not run. Configuration is not proof of execution.
Correct your own command mistakes before blaming the repo. A demo that prints states
without asserting them is a walkthrough, not a regression gate.

Respect the documented working directory. A failure caused by running a command
elsewhere is not a repo defect. Likewise, stale caches introduced by the audit's
probe/restoration are audit artifacts unless the normal documented workflow
independently reproduces the problem. Do not recommend duplicating test counts in
documentation just to provide a reference; those counts drift as tests change.

Use frozen installation when supplied. If repo resolution data fails, record it;
one non-mutating fallback can still prove downstream checks. Never rewrite a lockfile
to make an audit pass. Successful installation and repeatable resolution differ.
Bound slow commands and stop investigation when further attempts add no evidence.
Stop only services you started; remove only temporary artifacts you created.

## Test the feedback loop

When primary verification executes and a reversible probe is allowed, read the
probe reference. Prefer a disposable copy. Introduce one relevant small defect,
confirm detection, restore exact bytes and confirm the baseline result.
Skip when mutation, execution or restoration is unavailable. A missed probe is a
verification gap, not evidence that every test is useless or permission to change
production code. Do not weaken host permissions to obtain a better verdict.

## Turn evidence into decisions

For each finding, name the impeded agent task, evidence, smallest useful repair and
an objectively testable verification. Separate owners:

- Repo: source, instructions, fixtures, dependencies or committed controls.
- Environment: this machine, harness, permissions, tools or unavailable context.
- External: CI organization settings, third-party services or access outside checkout.

Do not penalize repo quality for the host model or unavailable browser. Product
agent-to-agent permissions are not coding-agent tool restrictions. An explicit demo
mode or synthetic credential is not automatically a safety defect; trace an actual
consequential unsafe path before making that finding.

Priority: P1 can allow an incorrect, unverifiable or unsafe change; P2 adds material
friction or weak feedback; P3 is a useful refinement. Do not fill categories with
invented issues. Credit evidenced strengths and explain the limits of evidence.

## Write and check the report

Write `reports/agentic-readiness.md` relative to the assessed repository root unless
a different destination was requested. If the target tree itself must remain
read-only, use the host's artifact directory or return the report in conversation.
Preserve an existing report first, or choose a dated filename if its ownership is
unclear. Start with **TL:TR**: key findings and insights, the delegation boundary
and the best next step. Aim for a 2–4 minute read, roughly 700–1,200 words (less for
simple scopes). Keep command detail after the decision. No weighted percentage,
glossary, duplicate finding index or mandatory host metadata dump.

For a tiny repository, aim for about 300–700 words, including structure, with only
consequential findings. This is guidance, not a reason to cut evidence. Do not
turn every observation into a repair task. A correct two-test fixture does not need
the same backlog as a multi-service product.

Follow the report contract. If Python is available, run:

`python3 <skill-directory>/scripts/validate_report.py <report-path>`

Otherwise review the contract manually and say so. Correct report errors and rerun;
never distort findings to satisfy a validator. It checks consistency, not evidence
truth. Compare the tree with baseline and identify audit-created/concurrent changes.
Deliver the report link or text, practical verdict, first action and material limits.
