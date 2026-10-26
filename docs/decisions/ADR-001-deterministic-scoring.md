# ADR-001: Deterministic rubric scoring

**Status:** Accepted · **Date:** _YYYY-MM-DD_ · **Decider:** Senthilnathan Abboy Selvaraj

## Context
The score decides whether a story enters Jira. POs will challenge scores, and RTEs will compare teams. The score must be consistent and explainable.

## Options
| Option | Pros | Cons |
|---|---|---|
| **A. Rules-based rubric** | Same input → same score; every point has a reason; free; runs in CI | Misses nuance (e.g., value that's real but tersely worded) |
| B. LLM scores the story | Understands nuance and context | Scores vary run to run; hard to explain or audit; a PO can re-run until it passes |
| C. LLM scores, rules check | Some nuance plus a floor | Still non-deterministic at the threshold, which is where it matters most |

## Decision
**Option A.** A gate that decides what enters the system of record must be repeatable and explainable. Nuance is handled by the Conversation in refinement, and by the coach (ADR-002).

## Consequences
- Heuristics will produce some false rejects; tracked against the ≤ 10% target and tuned in `rubric.json`.
- Rubric changes are versioned; the version is logged with every decision.
