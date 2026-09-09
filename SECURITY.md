# Security Policy

## Supported versions

Security fixes are applied to the latest released version of the plugin. The current version is recorded in [`plugin.json`](plugin.json).

## Reporting a vulnerability

For this independently maintained fork, use its [issue tracker](https://github.com/joozio/agentic-readiness-assessment/issues) for non-sensitive reports. For a sensitive problem, request a confidential reporting channel without posting exploit details, credentials or repository contents. Upstream vulnerabilities should be reported through upstream's own security policy.

This fork makes no response-time guarantee. Do not publish confidential audit evidence while waiting for a response.

## What this plugin does on your machine

The plugin ships a single Agent Skill, and everything it does happens on your machine. When your agent runs it:

- It reads the repository in the current working directory.
- It runs commands that already belong to that repository, such as its install, build, lint and test commands, and it records every command it ran.
- The audit does not authorize pushes, publication, deployment, paid calls, production-data testing or privilege escalation. Host permissions remain authoritative.
- It writes a report, normally `reports/agentic-readiness.md`, preserving an existing report. With no file-writing capability, it returns Markdown in the conversation.
- When safe and permitted, it makes a small reversible probe in a disposable copy and restores it. Read-only assessments skip mutation.
- The skill contains no telemetry or upload client. The model/harness has its own data-handling policy; authorized setup commands may download dependencies.

The plugin carries no secrets and requires none. Reported findings name paths, never values.
