"""Deterministic 0-5 quality score against the SAFe story rubric (rubric/rubric.json).

Scoring is rules-based on purpose (ADR-001): the same story always gets the same score,
and every point lost comes with a reason a Product Owner can act on.
"""
import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from src.story import Story

RUBRIC_PATH = Path(__file__).resolve().parent.parent / "rubric" / "rubric.json"

USER_VOICE = re.compile(r"\bas an?\s+(?P<role>.+?),?\s+i\s+(?:want|need|can)\s+(?:to\s+)?(?P<want>.+?)(?:,?\s+so\s+that\s+(?P<value>.+))?$", re.I)
GWT = re.compile(r"\bgiven\b.+\bwhen\b.+\bthen\b", re.I)
MEASURABLE = re.compile(r"\d|\b(?:displays?|shows?|returns?|is saved|are saved|receives?|sends?|downloads?|redirect|error message|disabled|enabled|appears?|is created|is rejected|within)\b", re.I)
WHY = re.compile(r"\b(?:so that|in order to|to enable|to allow|to (?:remove|reduce|meet|decide|support|comply|prevent))\b\s+(?P<why>.+)$", re.I)
STOP = {"a", "an", "the", "to", "i", "my", "can", "of", "and", "for", "in", "on", "it", "be", "is", "so", "that", "we"}


@lru_cache(maxsize=1)
def rubric() -> dict:
    return json.loads(RUBRIC_PATH.read_text(encoding="utf-8"))


@dataclass
class CriterionResult:
    id: str
    name: str
    points: float
    max: float
    feedback: list[str] = field(default_factory=list)


@dataclass
class Scorecard:
    score: float
    max_score: float
    passed: bool
    criteria: list[CriterionResult]
    blockers: list[str]

    @property
    def decision(self) -> str:
        return "Accept: save to Jira" if self.passed else "Return to Product Owner"


def _words(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z']+", s.lower()) if w not in STOP}


def _has_term(text: str, terms: list[str]) -> list[str]:
    t = text.lower()
    return [x for x in terms if re.search(r"(?<![a-z])" + re.escape(x) + r"(?![a-z])", t)]


def _format(s: Story, m) -> CriterionResult:
    r = CriterionResult("format", "User-voice format", 0.0, 1.0)
    if s.type == "enabler":
        if s.enabler_type and len(s.statement.split()) >= 8:
            r.points = 1.0
        else:
            r.points = 0.5
            r.feedback.append("Enabler stories should name their type (exploration, architecture, infrastructure, or compliance) and describe the work in a full sentence.")
        return r
    if m and m.group("value"):
        r.points = 1.0
    elif m:
        r.points = 0.5
        r.feedback.append("Add the 'so that <business value>' part of the user voice.")
    else:
        r.feedback.append("Write the story in user voice: 'As a <role>, I want <activity>, so that <business value>'.")
    return r


def _value(s: Story, m) -> CriterionResult:
    r = CriterionResult("value", "Business value", 0.0, 1.0)
    why = m.group("value") if (m and m.group("value")) else None
    if not why:
        w = WHY.search(s.statement)
        why = w.group("why") if w else None
    if not why:
        r.feedback.append("State why this matters: who benefits and what changes for them.")
        return r
    want = m.group("want") if m else s.statement
    why_words, want_words = _words(why), _words(want)
    overlap = len(why_words & want_words) / max(1, len(why_words))
    if len(why.split()) >= 4 and overlap < 0.6:
        r.points = 1.0
    else:
        r.points = 0.5
        r.feedback.append("The value clause is thin or repeats the activity. Say what outcome the user gets, not what the system does.")
    return r


def _acceptance(s: Story, vague: list[str]) -> CriterionResult:
    r = CriterionResult("acceptance", "Testable acceptance criteria", 0.0, 1.0)
    acs = s.acceptance_criteria
    if not acs:
        r.feedback.append("Add acceptance criteria. They are the 'Confirmation' in the 3 Cs; Given / When / Then works well.")
        return r
    testable = [a for a in acs if GWT.search(a) or MEASURABLE.search(a)]
    pts = 0.4 + 0.6 * len(testable) / len(acs)
    untestable = [a for a in acs if a not in testable]
    if untestable:
        r.feedback.append(f"{len(untestable)} of {len(acs)} criteria can't be verified as written, e.g. \"{untestable[0][:70]}\". Rewrite as Given / When / Then with an observable result.")
    found = sorted({t for a in acs for t in _has_term(a, vague)})
    if found:
        pts -= 0.2
        r.feedback.append(f"Vague terms in acceptance criteria: {', '.join(found)}. Replace them with measurable conditions.")
    r.points = round(max(0.0, min(1.0, pts)), 1)
    return r


def _size(s: Story, rb: dict) -> CriterionResult:
    r = CriterionResult("size", "Estimable and small", 0.0, 1.0)
    p = s.story_points
    if p is None:
        r.feedback.append("Add a relative estimate in story points (1, 2, 3, 5, 8).")
    elif p in rb["story_points_full"]:
        r.points = 1.0
    elif p in rb["story_points_partial"]:
        r.points = 0.5
        r.feedback.append("13 points is at the edge of fitting in one iteration. Consider splitting by workflow step, business rule, or data variation.")
    elif p > max(rb["story_points_partial"]):
        r.feedback.append(f"{p:g} points is feature-sized. Split it into stories that each fit in one iteration.")
    else:
        r.feedback.append(f"{p:g} isn't on the estimation scale. Use 1, 2, 3, 5, 8 (or 13).")
    return r


def _clarity(s: Story, m, rb: dict) -> CriterionResult:
    r = CriterionResult("clarity", "Clear, independent, vertically sliced", 1.0, 1.0)
    vague = _has_term(f"{s.title} {s.statement}", rb["vague_terms"])
    if vague:
        r.points -= 0.5
        r.feedback.append(f"Vague wording in the story: {', '.join(sorted(set(vague)))}. Say exactly what 'good' looks like.")
    want = m.group("want") if m else s.statement
    if re.search(r"\band\b|/", want, re.I) and s.type == "user":
        r.points -= 0.5
        r.feedback.append("The activity combines more than one goal ('and' or '/'). Consider splitting into separate stories.")
    if s.type == "user" and _has_term(f"{s.title} {s.statement}", rb["horizontal_slice_terms"]):
        r.points -= 0.5
        r.feedback.append("This reads like a technical-layer slice. Slice vertically so the story delivers something a user can see.")
    r.points = max(0.0, r.points)
    return r


def score(s: Story) -> Scorecard:
    rb = rubric()
    m = USER_VOICE.search(s.statement)
    criteria = [_format(s, m), _value(s, m), _acceptance(s, rb["vague_terms"]), _size(s, rb), _clarity(s, m, rb)]
    total = round(sum(c.points for c in criteria), 1)
    blockers = []
    if not any(GWT.search(a) or MEASURABLE.search(a) for a in s.acceptance_criteria):
        blockers.append(rb["hard_requirements"][0]["why"])
    passed = total >= rb["pass_threshold"] and not blockers
    return Scorecard(total, rb["max_score"], passed, criteria, blockers)
