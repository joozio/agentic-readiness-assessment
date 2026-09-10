# Dispatch workspace

This offline workspace has two independently checked components and no root build.
Neither component needs installation, network access, credentials, or a service.

| Component | Purpose | Complete check and working directory |
|---|---|---|
| `services/quote` | Python 3.9+ quote service logic | From `services/quote`: `python3 -m unittest discover -s tests -v` |
| `web/widget` | Dependency-free Node.js rendering helper | From `web/widget`: `node check.js` |

A full-workspace change should account for both components or explicitly state why
one is excluded. There is intentionally no repository-wide aggregate command.

