# Parcel quote

This is a small offline Python 3.9+ project. It uses only the standard library,
does not need installation, and has no live services or credentials.

From this directory, run the complete behavior suite with:

```sh
python3 -m unittest discover -s tests -v
```

Run an example with `python3 quote.py 4`. A shipping-rule change belongs in
`quote.py`, with its behavior covered in `tests/test_quote.py`.

