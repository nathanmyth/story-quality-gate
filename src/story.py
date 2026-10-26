"""Parse a story from plain text or a dict into one structure.

Plain-text format (fields in any order; labels are case-insensitive):

    Title: Export monthly usage report
    Type: user                       # or: enabler - architecture
    As a facility manager, I want to export monthly energy usage as CSV,
    so that I can share it with finance.
    Acceptance criteria:
    - Given I am on the usage page, when I click Export, then a CSV for the selected month downloads
    Story points: 3
"""
import re
from dataclasses import dataclass, field


@dataclass
class Story:
    title: str
    statement: str
    acceptance_criteria: list[str] = field(default_factory=list)
    story_points: float | None = None
    type: str = "user"            # "user" or "enabler"
    enabler_type: str | None = None


_LABEL = re.compile(r"^\s*(title|type|story points|points|estimate|acceptance criteria|ac)\s*:\s*(.*)$", re.I)


def parse_text(text: str) -> Story:
    title, kind, enabler_type, points = "", "user", None, None
    statement_lines, acs, in_ac = [], [], False

    for raw in text.strip().splitlines():
        line = raw.strip()
        if not line:
            continue
        m = _LABEL.match(line)
        if m:
            label, value = m.group(1).lower(), m.group(2).strip()
            in_ac = False
            if label == "title":
                title = value
            elif label == "type":
                kind, enabler_type = _parse_type(value)
            elif label in ("story points", "points", "estimate"):
                points = _parse_points(value)
            else:  # acceptance criteria
                in_ac = True
                if value:
                    acs.append(value)
            continue
        if in_ac:
            acs.append(re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", line))
        else:
            statement_lines.append(line)

    statement = " ".join(statement_lines)
    if not title:
        title = statement[:80]
    return Story(title, statement, [a for a in acs if a], points, kind, enabler_type)


def from_dict(d: dict) -> Story:
    kind, etype = _parse_type(d.get("type", "user"))
    pts = d.get("story_points")
    return Story(
        title=d.get("title", ""),
        statement=d.get("statement", ""),
        acceptance_criteria=list(d.get("acceptance_criteria", [])),
        story_points=_parse_points(str(pts)) if pts is not None else None,
        type=kind,
        enabler_type=etype,
    )


def _parse_type(value: str) -> tuple[str, str | None]:
    v = value.lower()
    if "enabler" in v:
        for t in ("exploration", "architecture", "infrastructure", "compliance"):
            if t in v:
                return "enabler", t
        return "enabler", None
    return "user", None


def _parse_points(value: str) -> float | None:
    m = re.search(r"\d+(?:\.\d+)?", value)
    return float(m.group(0)) if m else None
