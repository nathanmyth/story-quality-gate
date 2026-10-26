# Architecture

```
Story (text / form / JSON)
        │
        ▼
   Parser (src/story.py) ──► title, statement, acceptance criteria, points, type
        │
        ▼
   Scorer (src/scorer.py) ◄── rubric/rubric.json (versioned config)
        │  5 criteria × 0–1 point, feedback per criterion, hard rule check
        ▼
   Gate (src/gate.py)
        ├── score ≥ 3.0 AND testable AC ──► Jira client ──► POST /rest/api/3/issue ──► STORY-123
        │                                    (dry-run → data/jira_outbox.jsonl when Jira isn't configured)
        └── otherwise ──► feedback to PO ──► optional AI coach rewrite ──► back through the gate
        │
        ▼
   Decision log (data/decisions.jsonl): score, criteria, rubric version, Jira key
```

## Components

| Component | File | Notes |
|---|---|---|
| Rubric | `rubric/rubric.json` | Criteria, threshold, term lists. Owned by RTE / Product Management |
| Parser | `src/story.py` | Plain text with labels (Title, Type, Acceptance criteria, Story points) or JSON |
| Scorer | `src/scorer.py` | Deterministic; returns a scorecard with feedback |
| Jira client | `src/jira_client.py` | Jira Cloud REST API v3; description in Atlassian Document Format; labels `quality-gate`, `qg-score-N` |
| Gate | `src/gate.py` | Decides, saves, logs |
| Coach | `src/coach.py` | Optional LLM rewrite; never scores (ADR-002) |
| UI | `app.py` | Streamlit: paste story → scorecard → save button only when passing |
| Browser demo | `demo/index.html` | Scorer in JavaScript; Jira save is simulated |

## Jira integration details

- **Auth:** basic auth with account email + API token (service account recommended), from `.env` only
- **Payload:** `project.key`, `issuetype.name` (default "Story"), `summary`, ADF `description` (statement, acceptance criteria list, gate score), `labels`
- **Story points:** custom field ID differs per Jira site, so it's configurable (`JIRA_STORY_POINTS_FIELD`); skipped if blank
- **Failure handling:** Jira errors are shown to the user with Jira's message; nothing is retried silently
