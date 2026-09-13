# Change QA companion, prototype 0.1

## TL:TR

Use two skills in one repository. Readiness identifies whether a named development
task has usable feedback and what to improve first. Change QA verifies whether a
specific implementation meets the requester’s intent and preserves relevant behavior.
A QA pass is bounded evidence for review, not merge or deployment authority.

## The improvement cycle

Readiness finding with a closure check → bounded implementation → change QA with
current acceptance evidence → reassessment of the original finding key. Reuse the
same finding key when closing a readiness gap; omission is never proof of closure.
This connects the reports to actual improvements without expanding the audit itself
into automatic product changes.

The companion takes the original request, a concrete diff or comparable snapshots,
permitted execution, and optional prior findings. Its report has four sections:
TL:TR; acceptance and regressions; defects and retest; evidence and limits. A material
unknown is explicit. A product failure is distinguished from inability to execute a
check. The readiness validator is intentionally not applied to QA's different claims.
Markdown works by itself; an available renderer can provide HTML/PDF without being
a mandatory installation dependency.

## Decisions that make QA useful

Derive acceptance checks from the requester’s original clauses, before relying on an
implementer’s summary. Exercise the entry point the user actually reaches, including
routing, configuration flags, build output, affected callers and meaningful failure
paths. A tested helper can be correct while its public entry point bypasses it.

Where a change promises new behavior, compare the acceptance result on compatible
isolated old and new snapshots. Old failure/new success can distinguish a meaningful
check; an import failure is not a behavioral red result. Existing-behavior and pure
refactor tests may correctly pass both versions, so this is not a universal demand
that every test fail on old code. Similarly, retries and idempotency are tested where
the operation's contract calls for them; repetition is not safe or appropriate for
every operation.

Allow external throwaway tests as evidence gathering, preserving the candidate and
its existing tests. Bound effort and stop with the missing evidence when access is
insufficient. Read-only inspection remains useful, but cannot create executed results.
A new reviewer label does not establish independence; disclose shared implementation
context. Findings from static inspection remain distinguishable from reproductions.

These choices are consistent with [Playwright’s user-visible behavior and isolation
guidance](https://playwright.dev/docs/best-practices) and [Anthropic’s distinction
between agent transcripts and actual outcomes](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents).
Those sources inform the design; they do not establish this skill's effectiveness.

## Initial evaluation, 13 September 2026

Fresh GPT Sol / Codex threads with high reasoning received isolated baseline/candidate
snapshots, the original request, and explicit permissions. One matched control received
no skill. Network, installs, credentials, source edits, mutation probes and delegation
were prohibited. Public manifest/oracle files were withheld. Commands and final bytes
were reviewed separately from report wording.

The first three trials used the initial draft. A second frozen draft incorporated
applicability-qualified old/new checks and public-entry wiring, then was used for the
checkout case. A third draft clarified cache/output handling for protected snapshots and was tested
in a fresh repeat of the checkout case. These are diagnostic iterations, not identical
repeated trials.

| Trial | Result | Boundary |
|---|---|---|
| Incorrect shipping threshold, no skill | Reject; exact 5000 boundary found through function and CLI | 253-word report; ordinary QA already catches this defect. |
| Same incorrect threshold, initial skill | Changes needed; exact same defect found | 630-word report adds criterion/evidence mapping; no demonstrated accuracy gain. |
| Correct shipping threshold, initial skill | Verified for stated scope | 567-word report; no unrelated tooling demanded; relevant CLI and negative paths checked. |
| Checkout guard bypass, revised skill | Changes needed; endpoint returned 201 and created a negative order | Correctly calls this pre-existing and unfixed; final bytes restored, but temporary bytecode writes violated the no-writes constraint. |
| Same route case, protected-snapshot correction | Changes needed; same defect and positive control verified | Bytecode disabled; final file, directory and symlink inventories unchanged; no cleanup required. |

The healthy report and control each corrected a shell harness variable error. Their
final product claims were checked against actual commands. The healthy report abbreviates
an inline test matrix rather than preserving its complete command; its report alone is
less reproducible than the retained local transcript. This is a prototype limitation,
not a reason to claim a validator establishes evidence truth.

The first checkout trial created Python bytecode in the protected snapshots, then
removed it and restored their original inventories. Its diagnosis is correct, but
restoration does not satisfy an explicit no-writes instruction. That execution failure
is retained. The guide now calls for disabling/redirecting generated output or using
an authorized disposable copy. The fresh retake used `PYTHONDONTWRITEBYTECODE=1`, repeated the same real-boundary
checks, and left the snapshots untouched. No cache cleanup was needed. One successful
retake is not a reliability estimate.

The four deterministic fixture checks verify recorded fixture hashes and establish
that supplied suites are green, the
boundary distinguishes incomplete/correct changes, the route bypass is real, and the
copied QA folder retains its reference and licensing. See [runnable cases](../tests/change-qa/README.md).

Unproven: additional models/harnesses, repeated trials, missing intent, inspection-only
execution discipline, browser/packaged deployment paths, migrations/retries and selection
near misses. Those are future evaluation targets, not tested capabilities. Prioritize
real maintainer decisions and examples over expanding the checklist or report length.

[Machine-readable trial observations](change-qa-trials.json) retain report hashes,
length and local wall times, including the failed execution. Timings include host/tool
retries and are not developer productivity estimates. Full local transcripts contain
harness context and are not published.
