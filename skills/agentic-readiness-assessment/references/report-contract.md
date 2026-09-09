# Human report contract · version 5

Use Markdown: short paragraphs, few bullets, tables at most five columns. No JSON
companion or renderer required. Use a descriptive title followed by these six `##`
headings in order. Structural labels stay English; prose may use the user's language.

## TL:TR

Begin with these labels, then 3–5 short bullets; aim for at most 180 words total.

```
**Verdict:** Needs improvements
**Confidence:** High
```

Explain the main insight, what an agent can do today, the biggest constraint and
the first action. No hashes or tool inventories here. Verdict is about declared scope:

- **Ready for bounded changes:** all applicable readiness checks Passed, full
  coverage of declared scope, High/Medium confidence, no open Repo/External P1 finding. Never a
  production-security certificate or permission for unattended deployment.
- **Needs improvements:** a verified gap impedes work but useful changes remain
  possible. Use for a missed probe or known P1 issue. Unknowns can coexist.
- **Blocked:** a repo-owned setup/deliverable/primary-check failure prevents reliable
  work in scope. Name its blocking finding.
- **Inconclusive:** insufficient evidence to decide the execution-dependent checks,
  with no demonstrated readiness-check Gap or verified Repo/External P1. Inspected
  P2/P3 improvements may coexist; they do not establish that the primary loop fails.
  This is the usual read-only or environment-only result. Keep delegation advice
  conditional on running the missing checks; inspected assertions do not prove a
  working regression gate.

Confidence: High = components inspected and relevant checks executed or tied to
exact-revision CI artifacts, probe completed where feasible; Medium = useful direct
evidence with specific execution/coverage limits; Low = mostly static claims,
unexecuted primary checks or important scope missing. Failing tests can provide
high-confidence evidence. Historical green CI from another revision proves nothing.

## Readiness checks

Use four rows with State Passed, Gap, Unverified or N/A. Each cites E01-style evidence.
N/A is only for an irrelevant property, never an unavailable tool. Only Setup and
Deliverable may be N/A; explain why. Their justified N/A satisfies the Ready condition.
A stdlib-only executable still requires a supported interpreter: Setup is Unverified
if that prerequisite was not checked. A source-only deliverable may be N/A by design
based on inspection; do not invent a packaging requirement. A runnable script is
itself a deliverable: no packaging step does not make its execution N/A. Mark that
row Unverified when the documented entry point was not exercised.

| Check | State | What this means |
|---|---|---|
| Setup | Passed | Clean installation and appropriate repeatability verified (E01). |
| Deliverable | Passed | Actual package/site/plan produced or validated (E02). |
| Primary checks | Passed | Scope's meaningful tests/policies passed (E03). |
| Probe | Passed | Relevant defect detected and baseline restored (E04). |

Gap requires a finding and repo evidence. A successful install may still have a
repeatability Gap. Unverified means documented-but-not-run, read-only constraints
or missing host prerequisites. Do not turn missing host tools into repo Gaps.

## What to improve

Usually 3–7 findings, fewer when warranted. Order by impact then plausible effort.
Use one compact record per problem, no repeated index table. If none, say so.

```
### F01 - Make the demo fail on wrong outcomes
**Priority:** P1
**Owner:** Repo
**Why:** A green demo can hide a refused or undelivered answer.
**Evidence:** E03; examples/demo.sh:94 prints the state without checking it.
**Change:** Assert the final state; fail on timeout or a mismatched audit event.
**Verify:** The normal demo exits 0; a simulated wrong state makes it exit nonzero.
```

Owners: Repo, Environment, External. Priorities: P1/P2/P3. Each field takes one or
two sentences. Verify describes an objective future closure test; an invented future
command must not appear as executed evidence. Missing optional tools are not a
mandatory installation task unless they block a meaningful decision.

## What already works

Two to four evidence-backed strengths, or one honest sentence if none established.
Label unexecuted guidance as documented. Credit enforcement only with evidence of
preventive/detection behavior. Every strength should cite an E ID.

## Scope and limits

Use these labels; add date, tested platform and material constraints in short prose.

```
**Scope:** Full repository: CLI, worker and docs.
**Coverage:** Full
**Mode:** Executed
**Revision:** abc123; pre-existing edits preserved.
**Skill version:** 5.0.0
```

Coverage: Full or Partial relative to declared scope. Mode: Executed or Read-only;
running repository checks or a probe makes it Executed. Host version/metadata reads,
report writing and report validation alone do not. The user's narrower file-only
restrictions still take precedence. Without Git,
name the snapshot. Explicitly name exclusions. Host/model identity is optional;
report only known, useful facts. Disclose probe/service cleanup, prior-report
preservation and concurrent edits outside the tested revision. Record validator
execution only after it actually ran; missing Python means manual review.

## Evidence

One short record per meaningful check or grouped related reads. Each starts
`### E01 - Description`. Put **Kind:** on its own line with exactly one value:
Executed, CI, Inspected or Not run (e.g. `**Kind:** Inspected`). Put explanation
on the next line. ASCII hyphens and typographic dashes are both accepted in ID headings.
Execution: exact command, cwd, result; inspection: paths/lines; CI: revision, job
and artifact; Not run: reason. Include red/restored probe results and baseline
comparison here. No raw logs; link safe full logs only when useful and available.
Every readiness row and finding cites an E ID; referenced F/E IDs must exist.

## Manual final check

TL:TR first; six sections; coherent verdict/checks/confidence; evidence references;
owned, verifiable fixes; no repeated backlog; host limits separated; baseline
preserved; no credential values. The validator checks this shape and consistency,
not the truth of claims or whether an alleged command was actually executed.
