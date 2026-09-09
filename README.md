# Agentic Readiness Assessment

An agent skill that answers three questions:

**What can an AI coding agent take on here? What gets in its way? What should we fix first?**

The result is a readable Markdown report beginning with **TL:TR — key findings and
insights**, followed by readiness checks, prioritized fixes, strengths and evidence.
It runs locally using the tools your harness already provides. No backend, API key,
MCP server or particular model is required.

This is **version 5 of joozio's fork** of
[Exadel's original skill](https://github.com/exadel-inc/agentic-readiness-assessment).
Original attribution and Apache-2.0 licensing are retained. This fork is independently
maintained and is not an Exadel-endorsed release.

## Install on your harness

The portable unit is the entire folder:

```text
skills/agentic-readiness-assessment/
  SKILL.md
  references/
  scripts/
  tests/
  LICENSE
  NOTICE
```

Clone this fork, then copy that folder into **your harness's documented skill
directory**, retaining its name and supporting files. Select the branch/revision
you intend to install. Do not overwrite an existing installation without backing it up.

```sh
git clone https://github.com/joozio/agentic-readiness-assessment.git
```

For a harness with no skill discovery mechanism, attach or point it at `SKILL.md`
and its references and ask it to follow them. Reading Markdown is the baseline
compatibility requirement; automatic discovery depends on the host.

The repository also retains thin Claude, Codex and Gemini packaging manifests for
clients that support those formats. They reference the same skill. They are not a
promise that every version of every client has been tested. The source folder is
self-contained and remains usable without the plugin manifests.

## Run it

Ask from the repository you want assessed:

> Use the agentic-readiness-assessment skill to assess this repository. Tell me what
> agents can work on today and what we should improve first.

Or specify constraints:

> Assess only the API package. You can run local tests, but don't install anything.

> Review the supplied files only. Don't execute commands or change source files.

Default output: `reports/agentic-readiness.md` under the assessed repository root.
If that tree must remain read-only, use the host's artifact area or chat instead.
Existing reports are preserved;
the user can choose another path. Without file-writing access, the report is
returned in the conversation.

## What the report looks like

1. **TL:TR:** the verdict, key insights, delegation boundary and first action.
2. **Readiness checks:** setup, deliverable, meaningful verification and a reversible probe.
3. **What to improve:** each finding once, with impact, owner, repair and closure test.
4. **What already works:** evidenced strengths worth preserving.
5. **Scope and limits:** what was assessed and what could not be established.
6. **Evidence:** concise commands/results and file locations, after the decision content.

Usually a 2–4 minute read. A small scoped audit should be shorter.
[Example reports and evaluation notes](examples/README.md) show what the skill
actually produced, including a read-only run.

Verdicts are **Ready for bounded changes**, **Needs improvements**, **Blocked** or
**Inconclusive**, paired with evidence confidence. There is no percentage score.
Repository defects, host limitations and external controls have separate owners.
Missing Python or a browser on the audit machine is not a repository defect.

## Execution and trust

The agent reads repository instructions and classifies commands before running them.
It uses synthetic data and preferably a disposable copy. A probe introduces one
reversible behavior defect, checks detection, then restores exact baseline bytes.
No probe is required when mutation or safe restoration is unavailable.

The skill does not grant permissions. Your harness still controls file/network/tool
access. It does not authorize deployment, publication, messages, paid model calls or
production-data testing. The skill sends no telemetry; your model/harness has its
own data-handling policy, and repository setup may download dependencies when allowed.

## Optional validation

The validator needs Python 3.9+ and only the standard library:

```sh
python3 skills/agentic-readiness-assessment/scripts/validate_report.py /path/to/report.md
python3 -m unittest discover -s skills/agentic-readiness-assessment/tests -v
```

Without Python, the agent uses the same report contract manually. The validator
checks structure, evidence references and verdict consistency; it cannot establish
that a command truly ran or a finding is correct. Long reports generate a readability
warning, not a demand to delete useful evidence.

## Why version 5

Version 4's detailed method found useful issues, but generated repetitive reports
and mixed repo readiness with the host's permissions. Its validator also rejected
legitimate guardrail totals from its own scoring rubric.

Version 5 retains evidence, safe execution and the feedback-loop probe while
removing weighted scoring, repetitive sections and mandatory host metadata. It
supports partial and read-only assessments explicitly. **V4 scores and V5 verdicts
are not numerically comparable.** Old reports remain labeled as historical examples.

See [CONTRIBUTING.md](CONTRIBUTING.md) for tests and realistic evaluation cases.

## License and support

[Apache-2.0](LICENSE), with attribution in [NOTICE](NOTICE). Report issues with this
fork in [its issue tracker](https://github.com/joozio/agentic-readiness-assessment/issues).
Do not include private repositories, credentials or raw confidential reports in a
public issue. Upstream's historical legal and design documents are retained as
provenance, not as policies imposed on this independently maintained fork.
