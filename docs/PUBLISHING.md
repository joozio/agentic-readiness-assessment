# Packaging the fork

The installable artifact is `skills/agentic-readiness-assessment/`. Keep its version,
references, optional standard-library scripts and attribution together. The root
manifests are adapters for clients that support those formats, not runtime dependencies.

Before distributing a revision:

1. Run both unittest suites from CONTRIBUTING.md.
2. Validate every current example report with the bundled validator.
3. Confirm the skill can be copied out of this repo without losing a referenced file.
4. Run the realistic executed and read-only evaluation prompts on an available harness.
5. Record what was tested; do not imply every model or marketplace was verified.

Use the destination client's current official installation documentation. Marketplace
submission is a separate explicit action. No submission or automatic public release
is required to use the folder. Root manifests and SKILL.md version must match.

Original upstream planning notes under docs/superpowers and historical version-4
examples are retained for provenance; they do not override the current skill contract.
