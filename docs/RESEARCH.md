# Making a readiness skill useful for maintainers

Research and design review, 10 September 2026. Applies to this fork's 5.1 revision.

## TL:TR

The useful output is a decision about a specific kind of change: what an agent can
implement with review, what verification is available, and which repair would
remove the next obstacle. A repository-wide score cannot establish that decision.

The revision therefore adds task boundaries, explicit finding basis, proportionate
priorities, reusable HTML/PDF export and evidence-based reassessment. It keeps
Markdown as the portable source and avoids making particular tools or instruction
files prerequisites for readiness. A larger, separate evaluation suite tests the
known ways an assessment can mislead its reader.

These are design decisions informed by research, not evidence that this skill
improves every model's performance. External studies use different task populations
and sometimes preliminary methods. Our own trial results are reported separately
in [evaluation notes](EVALUATION-5.1.md), including failures and limitations.

## What was investigated

The review covered four questions: whether procedural skills reliably add value;
what repository evidence can support delegation; how to preserve a readable report
without losing traceability; and how to measure later revisions without grading
only their formatting. Three independent GPT Sol workers investigated decision
calibration, export implementation and evaluation design. The integrating reviewer
checked primary research, challenged recommendations and inspected the code.

The source set prioritizes the Agent Skills specification and creation guidance,
primary agent-evaluation papers, direct developer studies, and first-party renderer
documentation. Recent arXiv papers are identified as preprints. Versions matter:
this review uses Evaluating AGENTS.md v2 and SkillsBench v4, rather than quoting
older abstracts as current results. This is a focused engineering review, not an
exhaustive systematic literature review.

## Evidence and its implications

### Skills can help, but usefulness must be measured locally

SkillsBench v4 evaluates 87 tasks across eight domains under 18 model/harness
configurations. It reports a mean pass-rate increase from 33.9% without skills to
50.5% with curated skills, with varying gains by configuration. Its task inventory,
curation and deterministic verifiers define the population being measured; it does
not establish the benefit of an arbitrary newly written skill. [SkillsBench v4](https://arxiv.org/abs/2602.12670v4)

SWE-Skills-Bench, a preliminary March 2026 preprint, reports much smaller benefits
for its requirement-driven software-engineering tasks and notes cases where
version-mismatched guidance harmed performance. Its selected tasks, public skills
and acceptance-test construction differ from SkillsBench. The contrast is a reason
to evaluate domain fit, not to average the two numbers into a universal effect.
[SWE-Skills-Bench v1](https://arxiv.org/abs/2603.15401v1)

**Design inference:** the skill must earn each added instruction through a real
failure it prevents or a repeated operation it simplifies. We add a reusable export
helper because repeatedly hand-writing a renderer is avoidable work. We do not add
a long universal inventory of preferred development tools. Findings must connect
a condition to the selected change task.

### Repository instructions are context, not a readiness badge

Evaluating AGENTS.md v2 finds that context files did not generally improve task
success in its evaluated settings, while inference cost increased by more than
20% on average. The authors still identify value in non-standard coding practices.
The study is a preprint covering particular models, agents and issue populations;
it does not show that every instruction file is harmful. [Evaluating AGENTS.md v2](https://arxiv.org/abs/2602.11988v2)

**Design inference:** inspect the actual instruction surface and credit concrete
guidance. Do not award readiness merely for the existence of AGENTS.md, a long
README or a named framework. Conversely, absence alone should not create a finding
in a tiny, obvious repository. A useful documentation finding explains a wrong turn,
contradiction or missing decision that affects real work.

### A test result belongs to a task and execution environment

SWE-agent's experiments show that changes to the agent-computer interface alter
results even with the underlying model held fixed. Its task population is bounded,
but the experiment demonstrates that the harness is part of the evaluated system.
[SWE-agent, NeurIPS 2024](https://papers.neurips.cc/paper_files/paper/2024/file/5a7c947568c1b1328ccc5230172e1e7c-Paper-Conference.pdf)

**Design inference:** an assessment describes observed development conditions; it
does not certify an agent's success rate. “The pricing rule has an executable test
and an exercised CLI” is useful evidence. “This repository is agent-ready” without
a task boundary loses the conditions that made the evidence useful. Inventorying
every directory also does not prove behavioral coverage of every component.

The 5.1 task table preserves useful distinctions: reviewed CLI edits can be
Supported while a service integration remains Unverified. The overall verdict is
a summary and cannot override the narrower rows. Existing review, merge and release
authority remains outside this assessment.

### One mutation establishes one piece of feedback

Mutation-testing research supports the relationship between detecting artificial
faults and detecting real faults, while documenting limitations. A surviving mutant
may be equivalent to the original behavior; selection and reachability matter.
[Just et al., FSE 2014](https://homes.cs.washington.edu/~mernst/pubs/mutation-effectiveness-fse2014-abstract.html)

**Design inference:** retain the small reversible probe, but state the fault shape,
task and observable consequence. A relevant wrong output that leaves the check
green demonstrates a verification gap. A check importing a different copy of the
code demonstrates an invalid audit setup. A killed boundary mutant cannot establish
the quality of unrelated release or integration checks.

This distinction also prevents an auditor's temporary cache or working-directory
mistake from becoming a repository finding. The probe must be attributable, and
restoration must recover both bytes and the baseline check result.

### Technical readiness is not a productivity estimate

METR's early-2025 randomized study found slower completion for experienced
developers working in familiar open-source repositories. Its February 2026 update
explicitly describes the later experiment as an unreliable estimate of current
effects because of participant selection and measurement problems. The old result
should not be presented as a current universal claim about AI assistance.
[METR 2025 study](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/),
[METR 2026 update](https://metr.org/blog/2026-02-24-uplift-update/)

**Design inference:** this skill should not claim percentage productivity gains.
If a maintainer wants an economic assessment, collect local accepted-change time,
review effort, rework and escaped defects for named task classes. Keep that separate
from whether a build or regression check works. A short readiness audit cannot
substitute for observing the team's actual work.

## The resulting design

### Decisions first, evidence close enough to inspect

The six-section Markdown report remains familiar. TL:TR contains a direct delegation
sentence and the first useful action. The readiness table retains the core checks;
a compact task table explains their practical boundary. Findings appear once, and
long commands stay in the evidence section with stable links.

The finding basis separates Demonstrated failures from Inspected risks and
Hypotheses. A missing assertion is inspected evidence of a weakness; it is not
proof that incorrect behavior has actually been accepted. Unknown premises usually
belong in the limitations. A speculative concern cannot supply a readiness Gap.

Priority remains one action-order field. We considered adding a second severity
scale but rejected the extra rubric and report bulk. Instead, Why must connect
consequence, exposure and existing controls. P1 can still be justified by a tightly
evidenced high-consequence static risk; the skill must not demand a dangerous
reproduction just to strengthen its label. The validator flags that case for review.

Effort is a coarse relative size, with Unknown available. It supports choosing the
next repair without pretending to know an organization's delivery estimates.
Stable finding Keys support later correspondence even when F01 becomes F03.

### Portable instructions and optional presentation

The Agent Skills specification makes SKILL.md the entry point, with supporting
references and scripts. It recommends progressive disclosure and clearly described
dependencies; tool-allowance support varies among implementations. [Agent Skills specification](https://agentskills.io/specification)

Accordingly, the skill's baseline is readable instructions and Markdown output.
Host-specific orchestration, a browser, Python and PDF libraries are optional.
Manual use remains possible in a harness without automatic discovery. This is a
portable package design, not a claim that all harness versions have been tested.

The shared renderer creates a responsive HTML document from the Markdown rather
than asking another model to rewrite the findings for presentation. PDF is an
optional conversion using an installed renderer. It has no fixed page count and
preserves unfamiliar fields. Raw HTML and images remain text; conversion does not
fetch report-supplied network or local resources. The detailed decisions and
primary security/accessibility references are in the [export guide](../skills/agentic-readiness-assessment/references/export.md).

The research report itself is kept outside the installed skill. Most users need
the decision procedure, not several thousand words of literature on every audit.

### Reassessment requires new closure evidence

The compare helper matches stable Keys only when repository identity and scope
match. It deliberately labels absent findings “Not rechecked”; a missing paragraph
is not proof that the code was fixed. New appearances are “Newly reported”, because
the report cannot establish when an issue was introduced.

The assessment agent still owns closure judgment. It must run the relevant check
or inspect decisive current evidence, name the revision, and account for changes
to scope or environment. Renaming a scope or changing the harness may require
manual correspondence. Conservative refusal is preferable to a false improvement
trend. One anchor task can help comparisons; an additional different task is useful
when it resolves uncertainty, but is not a mandatory second probe on every run.

## How future improvements will be judged

The official skill-evaluation guidance recommends fresh contexts, a previous-version
or no-skill baseline, retained outputs, concrete assertions and human review. For
small samples, raw results are more defensible than impressive-looking statistical
summaries. [Evaluating skill output quality](https://agentskills.io/skill-creation/evaluating-skills)

Anthropic's agent-evaluation guidance distinguishes deterministic, model and human
graders and emphasizes the limitations of each. A transcript and an outcome answer
different questions; a structurally valid artifact is only one observation.
[Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

Our evaluation package therefore separates tiny presented repositories from hidden
oracles. Cases cover healthy minimal code, misleading green output, broken
distributables, multiple components, documentation, read-only use and an
implementation near-miss. Deterministic tests verify that the fixture actually
exhibits the intended behavior. Fresh-agent trials evaluate the skill. These are
different suites and their counts must be reported separately.

For each change, retain the prompt, skill/fixture revision, model/harness, actual
report, command evidence and restoration result. Compare the previous version on
the same difficult cases. Grade unsupported findings, priority, scope, ownership,
delegation and permission compliance separately from parser success. Record human
disagreement rather than adjusting the oracle to make the new release win.

The highest-value next evidence is repeated use on real repositories and independent
maintainer feedback: could they identify the first useful repair, was its acceptance
check executable, and did a later report accurately recognize closure? Add regression
cases when a real failure appears. Do not expand instructions merely because another
checklist has more categories.

## Limitations and source record

The thresholds in the judgment guide are engineering choices, not validated
psychometric scales. Synthetic repositories omit most operational complexity.
Single trials cannot measure reliability, and the author reviewing the result is
not a substitute for independent maintainer acceptance. Portable packaging does
not demonstrate equivalent model behavior. These limits remain visible in release
evaluation notes.

All linked sources were reviewed for this September 2026 decision. Primary research
sources are versioned where available; first-party specification and evaluation
guides are living documents. The implementation follows the design above selectively:
it does not import every recommendation from a paper or delegated research note.
External findings motivate tests; actual local evaluation determines what this fork
can claim about its own behavior.
