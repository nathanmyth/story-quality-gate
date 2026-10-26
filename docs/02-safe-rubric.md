# The SAFe Story Rubric

How each scoring criterion maps to SAFe story guidance. The rubric itself lives in [`rubric/rubric.json`](../rubric/rubric.json) so the RTE and Product Management can change it through a reviewed pull request.

## Scoring (0–5, pass at 3.0)

| # | Criterion | Max | SAFe basis | Full points | Partial | Zero |
|---|---|---|---|---|---|---|
| 1 | **User-voice format** | 1 | Role, activity, business value | "As a…, I want…, so that…" all present. Enablers: type stated + full description | Missing "so that"; enabler without type | No user voice |
| 2 | **Business value** | 1 | INVEST *Valuable* | Value clause of 4+ words that doesn't restate the activity | Thin or repeats the activity | No value stated |
| 3 | **Testable acceptance criteria** | 1 | INVEST *Testable*; 3 Cs *Confirmation* | Every criterion verifiable (Given/When/Then or measurable result), no vague terms | Some criteria untestable (0.4 + 0.6 × share testable); −0.2 for vague terms | None |
| 4 | **Estimable and small** | 1 | INVEST *Estimable*, *Small*; fits one iteration | 1, 2, 3, 5, or 8 points | 13 points (consider splitting) | Missing, off-scale, or > 13 (feature-sized) |
| 5 | **Clear, independent, vertical** | 1 | INVEST *Independent*, *Valuable* | One goal, user-visible slice, no vague words | −0.5 each: vague words; "and" / "/" joining goals; technical-layer slice | |

## Hard requirement

**At least one acceptance criterion must be testable.** A story without one is blocked whatever its score. In SAFe, acceptance criteria are the *Confirmation* in Card / Conversation / Confirmation. Without them nobody can tell whether the story is done. ([ADR-003](decisions/ADR-003-threshold-and-hard-rule.md))

## What the rubric does *not* judge

- **Negotiable** (INVEST): a property of how the team works with the story, not of its text
- **The Conversation** (3 Cs): the gate supports refinement; it doesn't replace it
- **Whether the story is the right thing to build**: that's the PO's call

## Enabler stories

SAFe enablers cover exploration (spikes), architecture, infrastructure, and compliance work. They may not have an end user, so the rubric doesn't require user voice for them. It does require the enabler type, a clear description, a reason ("to remove…", "to meet…"), and testable criteria.

## Sources

- SAFe User Story Primer: role / activity / value, the 3 Cs, INVEST, acceptance criteria, story splitting
- SAFe Story article (framework.scaledagile.com/story): stories as small, user-perspective units of work sized to complete within an iteration; enabler work types
