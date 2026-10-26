"""The quality gate: score the story, save to Jira only if it passes, log every decision."""
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from src import jira_client
from src.scorer import Scorecard, rubric, score
from src.story import Story

DECISIONS = Path(__file__).resolve().parent.parent / "data" / "decisions.jsonl"


@dataclass
class GateResult:
    scorecard: Scorecard
    jira: dict | None   # {"key", "mode", "url"} when saved, else None


def run(story: Story, save: bool = True) -> GateResult:
    card = score(story)
    jira = jira_client.create_issue(story, card) if (card.passed and save) else None
    _log(story, card, jira)
    return GateResult(card, jira)


def _log(story: Story, card: Scorecard, jira: dict | None) -> None:
    DECISIONS.parent.mkdir(exist_ok=True)
    rec = {
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "rubric_version": rubric()["version"],
        "title": story.title,
        "score": card.score,
        "passed": card.passed,
        "blockers": card.blockers,
        "criteria": {c.id: c.points for c in card.criteria},
        "jira_key": jira["key"] if jira else None,
    }
    with DECISIONS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def scorecard_dict(card: Scorecard) -> dict:
    return {**asdict(card), "decision": card.decision}
