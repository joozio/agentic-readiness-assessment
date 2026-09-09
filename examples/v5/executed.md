# Agent readiness: parcel quote fixture

## TL:TR

**Verdict:** Ready for bounded changes
**Confidence:** High

- Three files, one function, one documented command. An agent can read the whole
  repository and get a truthful pass/fail on a pricing change in under a second.
- Both README commands work exactly as written, no install or network (E01-E03).
- The feedback loop is real: a wrong price multiplier was caught by the existing
  suite with the file, line and expected value named (E04).
- The one gap: tests cover the `quote` function, never the CLI wrapper the README
  advertises as the deliverable (F01).
- First action: add a test that runs `quote.py` as a process and asserts its
  output and exit code.

## Readiness checks

| Check | State | What this means |
|---|---|---|
| Setup | Passed | Stdlib only; CPython 3.14.3 meets the documented 3.9+ floor and a fresh copy ran clean, no install step (E01, E05). |
| Deliverable | Passed | The deliverable is the runnable script; `python3 quote.py 4` printed `13` (E02). |
| Primary checks | Passed | The documented unittest suite ran 2 tests, both green (E03). |
| Probe | Passed | A pricing defect failed the suite with an attributable message; exact bytes restored (E04). |

## What to improve

### F01 - Cover the CLI entry point, not just the function
**Priority:** P2
**Owner:** Repo
**Why:** The README presents `python3 quote.py 4` as the thing to run, yet every
test imports `quote` directly, so an agent can break argument parsing and still
see a green suite.
**Evidence:** E03; tests/test_quote.py:7,12 call `quote()` only, while the CLI is
a separate layer at quote.py:12-15.
**Change:** Add a test using `subprocess.run([sys.executable, 'quote.py', '4'])`
asserting stdout `13` and exit 0, plus one for the rejection path.
**Verify:** Breaking the argparse type or the print line fails the suite; the
unmodified repository still passes.

### F02 - Decide how the rejection path should surface
**Priority:** P3
**Owner:** Repo
**Why:** `python3 quote.py 0` exits 1 with a raw `ValueError` traceback, a
user-facing behavior an agent has no stated intent to preserve.
**Evidence:** E02; quote.py:7 raises and nothing at quote.py:11-15 catches it.
**Change:** Either catch `ValueError` and exit with a one-line message, or note in
the README that the traceback is intentional.
**Verify:** `python3 quote.py 0` produces the chosen output and exit code,
asserted by the CLI test from F01.

## What already works

The README is accurate for its size: both commands were run verbatim and behaved
as described, with no undocumented setup step (E01, E02, E03).

The two tests assert meaning, not shape. One pins an exact price, the other the
rejection contract across two inputs, and the probe showed the suite turns red on
a plausible regression with a message that locates it (E03, E04).

## Scope and limits

**Scope:** Full repository: `quote.py`, `tests/test_quote.py`, `README.md`.
**Coverage:** Full
**Mode:** Executed
**Revision:** No version control; assessed the on-disk snapshot at
/workspace/parcel-quote, quote.py sha1 7252fba9. No prior report existed.
**Skill version:** 5.0.0

Assessed 2026-09-09 on macOS 25.4.0, CPython 3.14.3. The probe ran in a disposable
/tmp copy, since deleted; the assessed tree is byte-identical before and after and
gained only this `reports/` directory. Bytecode writing was disabled throughout, so
no `__pycache__` was created. Older 3.9+ interpreters were unavailable and untested.
No CI service exists, so there is no CI evidence.

## Evidence

### E01 - Setup: interpreter, clean-copy repeatability, containment
**Kind:** Executed
`python3 -VV` in /workspace/parcel-quote reported CPython 3.14.3,
meeting the README's 3.9+ floor. A full copy of the tree in a fresh mktemp
directory ran the documented suite green with no install step.

### E02 - Deliverable executed
**Kind:** Executed
In /workspace/parcel-quote: `python3 quote.py 4` printed `13`, exit 0;
`python3 quote.py 0` exited 1 with `ValueError: weight must be positive` from quote.py:7;
`python3 quote.py 4.5` exited 2 with the argparse usage error.

### E03 - Primary checks
**Kind:** Executed
With `PYTHONDONTWRITEBYTECODE=1`, in /workspace/parcel-quote:
`python3 -m unittest discover -s tests -v`
ran 2 tests, OK, exit 0. tests/test_quote.py imports `quote` directly and never
invokes the CLI.

### E04 - Reversible probe
**Kind:** Executed
In a disposable mktemp copy of the snapshot, `python3 -m unittest discover -s tests`
returned OK at baseline. `PYTHONDONTWRITEBYTECODE=1` was set for all Python checks. Changed quote.py:8 from
`return 5 + 2 * weight` to `return 5 + 3 * weight`; the suite reported
`FAIL: test_positive_quote`, `AssertionError: 17 != 13` at tests/test_quote.py:7,
The failing output established detection. Restored the original bytes from a pre-edit backup, sha1 matched 7252fba9,
suite back to OK. Copy and backup deleted.

### E05 - Repository contents
**Kind:** Inspected
The tree holds exactly README.md, quote.py and tests/test_quote.py; quote.py
imports only `argparse`, the tests only `unittest`. No installer, lockfile,
credential, generated artifact or CI configuration exists. README.md:9-11 states
the change workflow and which files are disposable. A post-assessment listing
matched that set plus this report.
