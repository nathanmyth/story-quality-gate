"""Score a story and save it to Jira if it passes.

    python -m src.cli examples/good_story.txt
    python -m src.cli examples/weak_story.txt --coach     # suggest a rewrite (needs ANTHROPIC_API_KEY)
    python -m src.cli story.txt --score-only               # never save
"""
import argparse
from pathlib import Path

from src import coach, gate, jira_client
from src.story import parse_text


def main() -> None:
    ap = argparse.ArgumentParser(description="SAFe story quality gate")
    ap.add_argument("file", help="Story as a text file")
    ap.add_argument("--score-only", action="store_true")
    ap.add_argument("--coach", action="store_true", help="Suggest a rewrite when the story fails")
    a = ap.parse_args()

    story = parse_text(Path(a.file).read_text(encoding="utf-8"))
    res = gate.run(story, save=not a.score_only)
    card = res.scorecard

    print(f"\n{story.title}")
    print(f"Score: {card.score:g} / {card.max_score:g}  →  {card.decision}\n")
    for c in card.criteria:
        print(f"  {c.points:>3.1f} / {c.max:g}  {c.name}")
        for f in c.feedback:
            print(f"           ↳ {f}")
    for b in card.blockers:
        print(f"\n  BLOCKED: {b}")

    if res.jira:
        where = res.jira["url"] or "data/jira_outbox.jsonl (dry run: set JIRA_* in .env to save to Jira)"
        print(f"\nSaved {res.jira['key']} → {where}")
    elif card.passed and a.score_only:
        print("\nPasses the gate (not saved: --score-only).")
    else:
        print("\nNot saved to Jira. Fix the items above and run again.")
        if a.coach and coach.available():
            print("\nSuggested rewrite:\n")
            print(coach.suggest_rewrite(story, card))

    if not jira_client.configured() and not a.score_only:
        print("\n(Jira not configured: running in dry-run mode.)")


if __name__ == "__main__":
    main()
