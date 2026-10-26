"""Create a Story in Jira Software (Cloud REST API v3), or write to a local outbox in dry-run mode.

Set these in .env to save to real Jira:
    JIRA_BASE_URL=https://your-site.atlassian.net
    JIRA_EMAIL=you@company.com
    JIRA_API_TOKEN=...            # from id.atlassian.com → Security → API tokens
    JIRA_PROJECT_KEY=TEAM
Optional:
    JIRA_ISSUE_TYPE=Story
    JIRA_STORY_POINTS_FIELD=customfield_10016   # varies by site; leave blank to skip
Without them, the client runs in dry-run mode and appends payloads to data/jira_outbox.jsonl.
"""
import json
import os
from pathlib import Path

from src.scorer import Scorecard
from src.story import Story

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

OUTBOX = Path(__file__).resolve().parent.parent / "data" / "jira_outbox.jsonl"


def configured() -> bool:
    return all(os.getenv(k) for k in ("JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN", "JIRA_PROJECT_KEY"))


def _p(text: str) -> dict:
    return {"type": "paragraph", "content": [{"type": "text", "text": text}]}


def _heading(text: str) -> dict:
    return {"type": "heading", "attrs": {"level": 3}, "content": [{"type": "text", "text": text}]}


def _bullets(items: list[str]) -> dict:
    return {"type": "bulletList", "content": [{"type": "listItem", "content": [_p(i)]} for i in items]}


def build_payload(story: Story, card: Scorecard) -> dict:
    """Jira issue payload. The description uses Atlassian Document Format (ADF), which API v3 requires."""
    content = [_p(story.statement), _heading("Acceptance criteria"), _bullets(story.acceptance_criteria),
               _heading("Quality gate"),
               _p(f"Score {card.score:g} / {card.max_score:g} against the SAFe story rubric.")]
    if story.type == "enabler":
        content.insert(1, _p(f"Enabler story ({story.enabler_type or 'type not set'})."))

    fields = {
        "project": {"key": os.getenv("JIRA_PROJECT_KEY", "DRYRUN")},
        "issuetype": {"name": os.getenv("JIRA_ISSUE_TYPE", "Story")},
        "summary": story.title[:255],
        "description": {"type": "doc", "version": 1, "content": content},
        "labels": ["quality-gate", f"qg-score-{int(card.score)}"] + (["enabler"] if story.type == "enabler" else []),
    }
    sp_field = os.getenv("JIRA_STORY_POINTS_FIELD")
    if sp_field and story.story_points is not None:
        fields[sp_field] = story.story_points
    return {"fields": fields}


def create_issue(story: Story, card: Scorecard) -> dict:
    payload = build_payload(story, card)
    if not configured():
        OUTBOX.parent.mkdir(exist_ok=True)
        n = sum(1 for _ in OUTBOX.open()) + 1 if OUTBOX.exists() else 1
        key = f"DRYRUN-{n}"
        with OUTBOX.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"key": key, "payload": payload}) + "\n")
        return {"key": key, "mode": "dry-run", "url": None}

    import requests

    base = os.environ["JIRA_BASE_URL"].rstrip("/")
    resp = requests.post(
        f"{base}/rest/api/3/issue",
        json=payload,
        auth=(os.environ["JIRA_EMAIL"], os.environ["JIRA_API_TOKEN"]),
        headers={"Accept": "application/json"},
        timeout=20,
    )
    if resp.status_code >= 400:
        raise RuntimeError(f"Jira rejected the story ({resp.status_code}): {resp.text[:300]}")
    key = resp.json()["key"]
    return {"key": key, "mode": "jira", "url": f"{base}/browse/{key}"}
