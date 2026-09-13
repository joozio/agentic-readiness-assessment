# QA report guide

Use these four sections. Omit empty defect records and avoid repeating an improvement
backlog. This report is not subject to the readiness skill's different verdict rules.

## TL:TR

Give the decision, tested scope/snapshot, key result, largest remaining uncertainty,
and next action in a few sentences.

- **Verified for stated scope:** every material acceptance criterion has direct,
  relevant evidence on the identified candidate, and no material observed regression
  remains. Name exclusions; this is not a universal pass.
- **Changes needed:** a requirement mismatch or material in-scope defect is evidenced.
  A tightly supported inspected contradiction may justify this in read-only mode;
  label it Inspected and do not invent a reproduction.
- **Inconclusive:** material acceptance evidence or an essential requirement is
  missing, with no established mismatch supporting Changes needed.

A demonstrated defect takes precedence over unrelated unknowns. Check results can be
Verified, Failed or Unverified independently of the overall decision. Product failures
and inability to perform a test are different states. Do not use scores or test counts
as the acceptance decision.

## Acceptance and regressions

| Criterion / risk | Expected result and source | State | Observed evidence |
|---|---|---|---|
| A named requirement or relevant regression boundary | Observable outcome derived from request, specification or established contract | Verified / Failed / Unverified | Evidence ID and actual outcome, or why not checked |

State material assumptions. Retain legitimate existing behavior when the requirement
changes only one path. Do not manufacture work by calling unrelated conventions defects.

## Defects and retest

For each justified defect give a short ID/title, consequence, basis (Demonstrated or
Inspected), introduced/pre-existing/unknown attribution, expected versus observed
behavior, location, reproducer when available, and exact retest condition. A proposed
repair is optional; do not repeat all evidence or silently implement it.

Order by impact on accepting this change. Name any supplied readiness finding key and
whether its actual closure check passed; carry incomplete checks as Not rechecked.
No defect records are needed for a correctly verified change.

## Evidence and limits

Record candidate identity and baseline identity, environment relevant to the claim,
execution constraints, exclusions, reviewer context, and state preservation. For each
cited E ID record Kind (Executed, Inspected, or Not run), exact command/action and cwd
when applicable, observed result/exit, and relevant location or durable artifact link.
Only executed actions may have execution results. In inspection-only mode do not
silently run an interpreter, imports, checks or a validator forbidden by the request.

A readable inline account is enough for a small check; large logs may be adjacent
artifacts. State missing dependencies and partial coverage without assigning them to
the repository. Verify the reported candidate is the one the check actually exercised.
