# Change QA behavioral cases

These synthetic cases test acceptance decisions, not report headings. Expected outcomes
live in `cases.json`; never give that file or this guide to the evaluating agent.

Copy one baseline/candidate pair into an opaque fresh directory. Give the agent only
the original request, the two snapshot paths, output destination, and the chosen skill
path (or explicitly no skill for a matched control). Do not expose other trials.
Allow local standard-library execution and external scratch checks; prohibit installs,
network, credentials, mutation probes, source writes and delegation. Invoke the WSGI
callable directly without a network listener for the checkout case.

Require a report outside both snapshots. Review the actual commands, expected/observed
outcomes, scope and final bytes. Hash files and inventory directories before and after;
a correct report does not excuse target changes. Preserve failed trials and check that
a reported regression is distinguished from a pre-existing unfulfilled requirement.

The shipping boundary case has a passing supplied test suite but fails the exact
inclusive threshold. The correct case checks whether QA invents a blocker. The checkout
case contains a correctly tested service guard bypassed by the public WSGI entry point.
The baseline lacks the newly requested behavior, so the issue is an incomplete fix;
that need not be called a newly introduced regression.

Run the deterministic fixture checks from the repository root:

```sh
python3 -m unittest discover -s tests -p test_qa_fixtures.py -v
```

For future evaluation, also add inspection-only access, missing intent, changed callers,
packaged/UI wiring, retry/migration contracts, and an implementation-request near miss.
The initial prototype does not establish performance on those cases.
