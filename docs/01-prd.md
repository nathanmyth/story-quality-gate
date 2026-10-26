# PRD: SAFe Story Quality Gate

| | |
|---|---|
| **Owner** | Senthilnathan Abboy Selvaraj (TPM) |
| **Status** | Draft → In review → **Approved** → Shipped |
| **Last updated** | _YYYY-MM-DD_ |

## 1. Problem

On an Agile Release Train (ART), backlog quality varies widely between teams and Product Owners. Stories reach PI Planning and iteration planning without acceptance criteria, without a clear "so that", or sized like features. The cost shows up later:

- Teams can't estimate, so planning runs long and commitments slip
- Stories fail iteration review because "done" was never defined
- Work gets split mid-iteration, which hurts predictability (the ART's PI objectives suffer)

_Replace with real numbers if you have them: e.g., "% of stories carried over per iteration" or "% of stories with no acceptance criteria at PI Planning"._

## 2. Users

| Persona | Need |
|---|---|
| **Product Owner** | Fast, specific feedback before a story goes to refinement |
| **Scrum Master / Team Coach** | Consistent story quality across the team without policing |
| **Release Train Engineer (RTE)** | Ready backlogs going into PI Planning; a quality signal across teams |
| **Team members** | Stories they can estimate and test |

## 3. Goals & success metrics

| Type | Metric | Target |
|---|---|---|
| **North star** | Stories carried over to the next iteration | −30% in 2 PIs |
| **Gate (P0)** | False accepts: weak stories saved to Jira (vs. PO labels) | **0%** on eval set |
| Gate | Agreement with experienced PO judgment | ≥ 90% |
| Gate | False rejects: good stories sent back | ≤ 10% |
| Adoption | Stories created through the gate | ≥ 80% of new stories by PI 2 |
| Quality | Stories in Jira with testable acceptance criteria | 100% of gated stories |

## 4. Scope

**In scope (v1)**
- Score a story 0–5 against a SAFe-based rubric, with feedback per criterion
- **Save to Jira only when the score is ≥ 3.0** and at least one acceptance criterion is testable
- Return failing stories to the PO with specific fixes; optional AI-suggested rewrite
- Log every decision (score, criteria, Jira key) for reporting
- Dry-run mode when Jira isn't configured

**Non-goals (v1)**
- Scoring features, capabilities, or epics (stories only)
- Replacing the backlog refinement conversation (the "Conversation" in the 3 Cs)
- Editing or re-scoring stories already in Jira
- Estimating story points for the team

## 5. Requirements

| ID | Requirement | Priority |
|---|---|---|
| R1 | A story is created in Jira **only** if score ≥ 3.0 **and** it has a testable acceptance criterion | P0 |
| R2 | The same story always gets the same score (deterministic) | P0 |
| R3 | Every point lost comes with feedback the PO can act on | P0 |
| R4 | Rubric (criteria, threshold, term lists) is config, versioned in git | P0 |
| R5 | The AI coach can suggest a rewrite but can never change a score | P1 |
| R6 | Jira credentials are never stored in code or logs | P0 |
| R7 | Score and rubric version are recorded on the Jira issue (label + description) | P1 |

## 6. Dependencies

- Jira Cloud site, project, and an API token for a service account (Jira admin)
- Agreement from the RTE and Product Management that the rubric reflects the ART's Definition of Ready
- 2–3 experienced POs to label a calibration set from real stories

## 7. Open questions

- Should the threshold differ for enabler stories?
- Gate at creation only, or also before PI Planning on existing backlog items?
- Do we surface team-level quality trends to the RTE, and how do we keep that from becoming a performance metric?
