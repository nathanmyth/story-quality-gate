"""Tests run without Jira or an API key (dry-run mode)."""
from pathlib import Path

import pytest

from eval.run_eval import run as run_eval
from src import gate, jira_client
from src.scorer import score
from src.story import from_dict, parse_text

EX = Path(__file__).resolve().parent.parent / "examples"


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    for k in ("JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN", "JIRA_PROJECT_KEY"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setattr(jira_client, "OUTBOX", tmp_path / "outbox.jsonl")
    monkeypatch.setattr(gate, "DECISIONS", tmp_path / "decisions.jsonl")


def test_parse_text_example():
    s = parse_text((EX / "good_story.txt").read_text())
    assert s.title == "Export monthly usage as CSV"
    assert len(s.acceptance_criteria) == 2 and s.story_points == 3


def test_good_story_passes_and_is_saved():
    res = gate.run(parse_text((EX / "good_story.txt").read_text()))
    assert res.scorecard.score >= 3.0 and res.scorecard.passed
    assert res.jira["key"] == "DRYRUN-1"


def test_weak_story_is_not_saved():
    res = gate.run(parse_text((EX / "weak_story.txt").read_text()))
    assert not res.scorecard.passed and res.jira is None
    assert not jira_client.OUTBOX.exists()


def test_enabler_story_passes():
    assert score(parse_text((EX / "enabler_story.txt").read_text())).passed


def test_high_score_without_testable_criteria_is_blocked():
    s = from_dict({"title": "Notifications", "statement": "As a user, I want notifications, so that I get notifications.",
                   "acceptance_criteria": ["Notifications work well"], "story_points": 3})
    card = score(s)
    assert card.score >= 3.0 and not card.passed and card.blockers


def test_feature_sized_story_loses_size_points():
    s = from_dict({"title": "X", "statement": "As a buyer, I want to compare two products side by side, so that I can choose faster with confidence.",
                   "acceptance_criteria": ["Given two products, when I click Compare, then their specs are shown in two columns"], "story_points": 40})
    assert next(c for c in score(s).criteria if c.id == "size").points == 0


def test_jira_payload_uses_adf_and_labels():
    s = parse_text((EX / "good_story.txt").read_text())
    p = jira_client.build_payload(s, score(s))["fields"]
    assert p["issuetype"]["name"] == "Story"
    assert p["description"]["type"] == "doc" and p["description"]["version"] == 1
    assert "quality-gate" in p["labels"] and "qg-score-5" in p["labels"]


def test_eval_has_no_false_accepts():
    m = run_eval()["metrics"]
    assert m["false_accept_rate"] == 0
    assert m["agreement"] >= 0.9
