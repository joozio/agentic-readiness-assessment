# Parcel quote fixture

Synthetic, offline evaluation fixture. Python 3.9 or newer, standard library only.
No installation or network is needed. There is no packaged release or CI service.

`python3 -m unittest discover -s tests -v` runs the behavior checks.
`python3 quote.py 4` prints the shipping quote for four kilograms.

Change shipping behavior in `quote.py`, add cases in `tests/test_quote.py`, run
the full suite and include its result when proposing a change. Generated Python
caches may be removed; source and existing reports must be preserved.
