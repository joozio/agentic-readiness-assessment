# Version 5.1 evaluation

Evaluation date: 10 September 2026. This is a diagnostic engineering record, not a
benchmark of general coding-agent capability or a claim of universal skill support.

## Method and scope

Fresh BB threads ran GPT Sol (`gpt-5.6-sol`, Codex provider, high reasoning) against
isolated fixture copies. Assessment trials received the selected skill path and case prompt,
without the manifest, grading rubric or previous fixture reports. Two cases also
ran the previous v5.0 skill, snapshotted from commit
`a054b5b84610f10cab42f35de1681587db335bd4`. Candidate snapshots were retained before
trials so later edits did not silently change an active test.

The shared harness supplied file and command tools. Network, installation,
credentials and live services were prohibited by the prompts; this was not an
OS-enforced network sandbox. Read-only cases prohibited repository execution and
target writes. The integrating reviewer inspected actual command transcripts,
reports and final file/directory inventories. Report validation was recorded
separately from semantic judgment. No independent human acceptance panel was used.

The [fixture suite](../tests/evals/README.md) has five dependency-free repositories
and seven case prompts. Its fixed runner verifies fixture behavior before evaluating
an agent: healthy tests really fail for a defect; misleading-green checks really
miss a wrong output; source checks really pass while the distribution fails.
Python 3.14.3 and Node 25.8.1 were available on the local macOS host.

## Observed outcomes

| Case | Baseline v5.0 | Revised result | Evidence boundary |
|---|---|---|---|
| Healthy minimal CLI | Ready; 3 tests pass, probe caught and restored | Ready; same source behavior verified, with an inspected CLI-test improvement | Corrected run verifies copy setup before execution; one earlier candidate run failed execution discipline. |
| Misleading green JavaScript | Needs improvements; missed rate defect found | Needs improvements; demonstrated outcome gap separated from inspected input-validation risk | Both versions found the main defect. The new report names conditional/unverified tasks and manual comparison as a control. |
| Broken distributable | Not paired | Needs improvements, High; corrected run demonstrates failure without mutation | Source tests pass while the built CLI cannot load its required rates data. |
| Mixed Python/JavaScript | Not paired | Inconclusive, Medium; both component checks pass | A real producer-to-consumer bridge also passes; shared payload edits remain conditional on making that check part of the workflow. No mutation allowed. |
| Strict read-only CLI | Not paired | Inconclusive, Low; inspected CLI coverage finding | No Python, imports, repository checks or target writes. All execution-dependent checks remain Unverified. |
| Documentation-only | Not paired | Inconclusive, Low; no invented repository finding | Setup/generated output N/A; explicit manual review remains unexercised. No application toolchain demanded and no target writes. |
| Implementation near-miss | Not paired | Correct fee/test edit; metadata-only trial did not load the audit skill | Must produce the requested code/test change rather than an audit report. |

The two paired cases do **not** show a verdict-accuracy gain: the previous skill
already found the main issue or recognized the healthy loop. The observed added
value is more explicit task boundaries, evidence basis, repair effort and finding
identity. Those benefits cost additional report text. On the clean healthy runs,
the old report was 684 words and the corrected new report 1,034; misleading-green
reports were 838 and 1,240 words. Counts include all Markdown structure and evidence.
Do not describe this minor release as a report-length improvement over v5.0.

Priority differences are judgments, not numerical improvements. The JavaScript
README explicitly describes printed examples for review. The old report chooses
P1 for the missing automated gate; the new report chooses P2 while identifying
manual comparison as a compensating control. Both expose the demonstrated defect.
The oracle does not require a preferred ordinal label when the stated consequence
and control justify the choice.

## Failures and protocol corrections retained

**Installed-copy contamination.** The first healthy old/new runs read the installed
v5.0 skill while opening an attached prompt, before switching to their designated
skill copies. They are exploratory observations, excluded from the clean comparison.
Subsequent trials put the full path and constraints directly in the initial prompt.
Transcript review confirmed the clean runs began with the specified skill.

Trial directories used descriptive case names, so the failure categories were not
fully blinded even though oracles were withheld. This further limits any capability
claim. Future discovery experiments should use opaque trial paths and titles;
the current suite is intended for diagnostic regression checks.

**Failed copy followed by unrelated test discovery.** One clean candidate run
attempted a relative copy from the wrong cwd, then continued to unittest discovery
in an incomplete directory. It imported unrelated installed-package tests. The
agent discarded those results, corrected the copy and preserved target bytes, but
the execution sequence fails the intended scope restriction. This is retained as
a failed trial, not averaged away by the eventual correct report. The probe guide
was amended to confirm cwd, source/check files and hashes before execution and to
stop on failed copy setup. A fresh corrected trial used fail-fast setup, detected
a boundary defect, restored exact bytes and did not repeat unrelated discovery.
One successful retake is not a reliability estimate.

**An ambiguous packaging-case prompt.** The initial prompt required preserving
source but did not clearly prohibit a restored probe inside a disposable copy,
while the hidden permission manifest said mutation was disallowed. The agent found
the correct artifact failure and also performed a restored source probe. This is a
protocol ambiguity, not fair evidence of disobeying an explicit no-probe instruction.
The prompt was clarified to cover disposable copies and repeated. The mixed-workspace
prompt received the same clarification before its trial. Fixture behavior stayed
unchanged. The corrected packaging run left Probe Unverified, demonstrated the
missing runtime asset, and restored all generated paths without changing source.
Before the implementation trial, the oracle was also reviewed to accept
a directly affected README-example update as a valid companion to the requested
code/test change.

**Skill selection protocol.** The initial implementation trial received the full
skill path and loaded its audit references, though it produced the correct code
change rather than an assessment. This is not a clean trigger rejection. A repeat
exposed only the available skill name/description, with the body optional. It
changed the fee and tests, ran all three tests successfully, and did not load the
audit instructions or create a readiness report. The prompt explicitly distinguished
availability from invocation, so this is a scoped selection check, not a blind
production-registry experiment. Both trials changed only the requested source and
test files; generated caches were removed.

**Draft self-validation wording.** Some report drafts stated the expected validator
success before the command ran. Their final recorded commands did succeed, so the
delivered statements match the eventual result, but the drafting order violates the
skill's instruction to record execution only afterward. This remains a process
weakness to watch; a report's validation sentence is never independent proof.
The reviewer used the actual command events instead.

The [machine-readable trial record](evaluation-5.1-results.json) retains all 14
fixture runs, including exploratory runs, failed execution and protocol repeats,
with report hashes, word counts and observed provider usage. Those categories must
not be collapsed into a single success percentage. Full local transcripts were
reviewed but are not published because they contain unrelated harness context.

## Deterministic and presentation checks

- 51 standard-library skill tests cover historical/current report consistency,
  task boundaries, evidence basis, stable-key comparison, safe export, preservation,
  missing PDF support and CLI behavior.
- Seven repository tests cover metadata/licensing, copied-folder execution, fixture
  preparation refusal and directory/symlink inventory. The copied-folder test reruns
  the skill tests; those are not counted again as new test cases.
- The fixture runner passes its seven integrity/behavior groups.
  [Release CI](https://github.com/joozio/agentic-readiness-assessment/actions/runs/34453125974)
  passed on Python 3.9 and 3.14 with Node 22, including manifest agreement and
  strict Claude plugin validation. Local syntax checks also target 3.9.
- Existing v5.0 examples remain valid. New examples are actual untouched reports,
  with their provenance described in the [example index](../examples/README.md).
- Real WeasyPrint 68.1 conversion produced readable multipage PDFs. Visual review
  led to corrected print column widths, record grouping and page numbers. The real
  reassessment exposed a narrow third status column, whose minimum width was
  corrected and visually rechecked. A separate
  long-table check preserved all 80 row identifiers across five PDF pages.
- HTML was exercised in Chrome at 390px and 1440px: no document overflow or page
  errors, working evidence anchors and no automatic network requests. These are
  targeted checks, not a full accessibility certification.

The HTML renderer uses the standard library; PDF remains optional. Tests of the
missing backend confirm the HTML survives and the error explains the next step.
The exporter never turns a presentation change into new assessment evidence.

## What can and cannot be concluded

The suite now exposes more meaningful failure modes than the previous one-fixture
evaluation, and the new helpers provide directly tested reusable functionality.
The evidence does not establish consistent gains across models, harnesses, large
repositories or repeated stochastic trials. Behaviors that pass in both versions
are useful regressions, not proof of new value. These local turn times include host
and tool retries and must not be treated as developer productivity measurements.

A private Agent Mesh reassessment is an application example kept outside the public
fork. Its repository data is not part of this public fixture suite, and recalibrating
a priority on unchanged code is not a repository improvement.

Future revisions should retain the original failure, define the smallest relevant
counterexample, run a matched baseline, inspect transcripts and final state, and
collect maintainer feedback on task boundaries and usable closure checks. The
[feedback template](../.github/ISSUE_TEMPLATE/assessment-feedback.yml) supports that
intake without requiring a confidential repository dump.
