"""Optional LLM coach: suggests a rewrite that addresses the scorecard feedback.

The coach never changes the score (ADR-002). A rewrite has to go back through the gate.
"""
import os

from src.scorer import Scorecard
from src.story import Story

MODEL = os.getenv("LLM_MODEL", "claude-haiku-5-5")

SYSTEM = """You are a SAFe Product Owner coach. Rewrite the story so it meets SAFe story guidance:
- User voice: "As a <role>, I want <activity>, so that <business value>" (enabler stories: state the enabler type instead)
- One goal per story, sliced vertically, no vague words
- 2-4 acceptance criteria in Given / When / Then form with observable results
- Keep the original intent. Do not invent requirements beyond what the story implies; mark assumptions with "(assumption)".

Reply in exactly this format:
Title: ...
As a ..., I want ..., so that ...
Acceptance criteria:
- Given ..., when ..., then ...
Story points: <keep the original estimate, or suggest one and add "(suggested)">"""


def available() -> bool:
    return bool(os.getenv("ANTHROPIC_API_KEY"))


def suggest_rewrite(story: Story, card: Scorecard) -> str:
    import anthropic

    feedback = "\n".join(f"- {f}" for c in card.criteria for f in c.feedback)
    original = (f"Title: {story.title}\n{story.statement}\nAcceptance criteria:\n"
                + "\n".join(f"- {a}" for a in story.acceptance_criteria)
                + f"\nStory points: {story.story_points if story.story_points is not None else 'not set'}")
    resp = anthropic.Anthropic().messages.create(
        model=MODEL, max_tokens=600, system=SYSTEM,
        messages=[{"role": "user", "content": f"Original story:\n{original}\n\nQuality gate feedback:\n{feedback}"}],
    )
    return "".join(b.text for b in resp.content if b.type == "text").strip()
