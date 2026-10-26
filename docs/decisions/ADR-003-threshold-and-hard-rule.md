# ADR-003: Pass at 3.0, plus a testable-acceptance-criteria hard rule

**Status:** Accepted (rubric v1.1) · **Date:** _YYYY-MM-DD_ · **Decider:** Senthilnathan Abboy Selvaraj

## Context
The requirement is that a story is saved to Jira only when it scores 3 or above. The eval showed that a score threshold alone isn't enough.

## Findings (18 PO-labeled stories)

**Rubric v1.0 (score threshold only + "has any acceptance criteria"):**
- 100% agreement with PO labels, but three weak stories scored **2.9**, just 0.1 below the line.
- A probe showed "As a user, I want notifications, so that I get notifications. AC: Notifications work well" would **pass at 3.9** if estimated at 3 points instead of 4. Its only criterion can't be tested.
- "Dashboard for sales" scored **4.0** with no acceptance criteria at all. Only the hard rule stopped it.

**Rubric v1.1 (this decision):**
- Hard rule tightened from "has acceptance criteria" to "has at least one **testable** acceptance criterion".
- Added "well", "properly", "good", "cleaner", "everything" to vague terms.
- Result: 100% agreement, 0% false accepts, 0% false rejects; the notifications probe is now blocked at any estimate.

## Decision
Pass = **score ≥ 3.0 AND at least one testable acceptance criterion**.

## Consequences
- A story can fail with a score above 3. The UI and CLI say why ("Blocked: …") so it isn't confusing.
- **Known limitation:** the PO labels were written by the same person who wrote the rubric, so 100% agreement is optimistic. M3 calibrates against real stories labeled by 2–3 POs who haven't seen the rubric (risk R-03).
