# Agentic readiness: parcel quote fixture

## TL:TR

**Verdict:** Inconclusive
**Confidence:** Low

- Three-file, standard-library Python fixture. The documented commands match the
  files that exist, so an agent finds the change path in one read.
- This run was supplied read-only, so the suite, the CLI and the interpreter
  prerequisite are documented rather than proven. Nothing was executed.
- The one substantive gap visible from source is coverage shape: the tests exercise
  the `quote` function, while the documented entry point `python3 quote.py 4` has no
  regression coverage.
- An agent can propose a bounded pricing change from these files; accept it only
  after the documented checks run successfully.
- First action: run `python3 -m unittest discover -s tests -v` from the repository
  root. Then exercise the CLI; a reversible probe is a separate check.

## Readiness checks

| Check | State | What this means |
|---|---|---|
| Setup | Unverified | Install-free and stdlib-only by design, but the Python 3.9+ prerequisite was not checked in a read-only run (E01, E04). |
| Deliverable | Unverified | No packaging step exists, but the source CLI is the deliverable and its documented entry point was not run (E01, E02, E04). |
| Primary checks | Unverified | The suite's assertions were read but it was not run (E03, E04). |
| Probe | Unverified | Mutation and execution were both out of scope (E04). |

## What to improve

### F01 - Cover the CLI entry point, not only the function
**Priority:** P2
**Owner:** Repo
**Why:** The README sends agents to `python3 quote.py 4`, but nothing asserts what it
prints or how it exits, so argument parsing or output can break with a green suite.
**Evidence:** E02 (quote.py:11-15 parses and prints); E03 (the tests call `quote`
directly and never the CLI).
**Change:** Add one test that runs the module as a subprocess, or extract `main()`
and assert stdout plus exit status for a valid weight.
**Verify:** Changing the print format in `quote.py` fails the suite; reverting passes.

### F02 - Return a usage error instead of a traceback
**Priority:** P3
**Owner:** Repo
**Why:** A non-positive weight is a deliberate rejection in the library, but at the
CLI it surfaces as an uncaught `ValueError` traceback, which reads as a crash.
**Evidence:** E02; quote.py:6-7 raises and quote.py:11-15 has no handler.
**Change:** Catch `ValueError` in the `__main__` block, print to stderr, exit nonzero.
**Verify:** `python3 quote.py 0` gives the message and a nonzero status with no
traceback; `python3 quote.py 4` is unchanged.

## What already works

Documented commands correspond exactly to the files present, so an agent following
the README does not guess (E01, E02, E03).

The inspected tests contain behavioral assertions: a concrete value for a valid
weight, and `subTest` asserting that both 0 and -1 raise. Their execution and
defect detection remain unverified (E03, E04). The README also states
the change protocol and the preservation rule, as documented guidance (E01).

## Scope and limits

**Scope:** Full supplied snapshot: `README.md`, `quote.py`, `tests/test_quote.py`.
**Coverage:** Full
**Mode:** Read-only
**Revision:** No Git metadata present; assessed as the supplied three-file snapshot at
`/workspace/parcel-quote`.
**Skill version:** 5.0.0

Assessed 2026-09-09 on macOS. The user restricted this run to file reads: no repository
command, import, install or source edit ran, which is why execution-dependent rows are
Unverified. The optional validator was not run at the user's direction; the contract was
reviewed manually. No prior report existed. The only tree change is this file.

## Evidence

### E01 - README instructions and constraints
**Kind:** Inspected
`README.md:1-11`. Python 3.9+, stdlib only, no install, no network, no packaged
release, no CI. Documents the test command, the CLI command and the change protocol.

### E02 - CLI and pricing source
**Kind:** Inspected
`quote.py:5-15`. `quote(weight)` raises `ValueError` for `weight <= 0`, else returns
`5 + 2 * weight`. The `__main__` block parses one integer argument and prints the
result, with no exception handling.

### E03 - Test module
**Kind:** Inspected
`tests/test_quote.py:1-16`. Two methods: `quote(4) == 13`, and `ValueError` for 0 and
-1 via `subTest`. Imports `quote` as a top-level module, which resolves from the
repository root as documented.

### E04 - Execution withheld
**Kind:** Not run
Neither `python3 -m unittest discover -s tests -v`, the CLI, an interpreter version
check, nor any probe was executed; the user scoped this run to file reads only. A
directory listing showed three files and no `.git`, so no commit could be recorded.
