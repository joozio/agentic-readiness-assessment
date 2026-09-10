# Rate-card package

This synthetic Python 3.9+ project is standard-library only. It needs no install,
network, credentials, or service. Run every command below from this directory.

Check source behavior:

```sh
python3 -m unittest discover -s tests -v
```

Build and exercise the distributable directory:

```sh
python3 build.py
python3 dist/ratecard/app.py 4
```

The build output under `dist/` is generated and may be replaced by the build.

