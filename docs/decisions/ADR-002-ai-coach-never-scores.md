# ADR-002: The AI coach suggests rewrites but never changes the score

**Status:** Accepted · **Date:** _YYYY-MM-DD_ · **Decider:** Senthilnathan Abboy Selvaraj

## Context
POs whose stories fail want help fixing them, not just a list of problems. An LLM is good at rewriting a story into user voice with Given / When / Then criteria.

## Decision
The coach is **advisory only**:
1. It sees the story and the scorecard feedback, and returns a suggested rewrite.
2. The rewrite is **not** saved automatically. The PO edits it and submits it through the gate like any other story.
3. The coach marks anything it inferred as "(assumption)" so the PO checks it in refinement.

## Why
- Keeps the gate deterministic (ADR-001).
- Prevents "AI wrote the requirements": the PO stays accountable for content, as SAFe intends.
- If the coach is unavailable, nothing breaks.

## Consequences
- One extra step for the PO (review and resubmit). Accepted: that review *is* the point.
