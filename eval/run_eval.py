"""Compare gate decisions with Product Owner labels.

    python -m eval.run_eval

False accepts (a weak story saved to Jira) are the P0 metric: they are what the gate exists to stop.
"""
import json
from datetime import datetime
from pathlib import Path

from src.scorer import score
from src.story import from_dict

HERE = Path(__file__).parent
TARGETS = {"agreement": (0.90, ">="), "false_accept_rate": (0.0, "<="), "false_reject_rate": (0.10, "<=")}


def run() -> dict:
    rows = []
    for line in (HERE / "eval_set.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        c = json.loads(line)
        card = score(from_dict(c))
        rows.append({"id": c["id"], "title": c["title"], "expected": c["expected"],
                     "predicted": "accept" if card.passed else "reject", "score": card.score})
    acc = [r for r in rows if r["expected"] == "accept"]
    rej = [r for r in rows if r["expected"] == "reject"]
    m = {
        "agreement": sum(r["expected"] == r["predicted"] for r in rows) / len(rows),
        "false_accept_rate": sum(r["predicted"] == "accept" for r in rej) / max(1, len(rej)),
        "false_reject_rate": sum(r["predicted"] == "reject" for r in acc) / max(1, len(acc)),
        "n": len(rows),
        "min_score_accepted_by_po": min((r["score"] for r in acc), default=None),
        "max_score_rejected_by_po": max((r["score"] for r in rej), default=None),
    }
    return {"run_at": datetime.now().isoformat(timespec="seconds"), "metrics": m, "rows": rows}


def main() -> None:
    res = run()
    m = res["metrics"]
    print(f"\n{'id':<5}{'PO label':<10}{'gate':<9}{'score':>6}  title")
    print("-" * 64)
    for r in res["rows"]:
        flag = "" if r["expected"] == r["predicted"] else "  ← disagree"
        print(f"{r['id']:<5}{r['expected']:<10}{r['predicted']:<9}{r['score']:>6.1f}  {r['title'][:32]}{flag}")
    print("\nTargets:")
    for k, (t, op) in TARGETS.items():
        v = m[k]
        ok = v >= t if op == ">=" else v <= t
        print(f"  {k:<20}{v:>6.0%}  target {op} {t:.0%}   {'PASS' if ok else 'FAIL'}")
    print(f"\nScore separation: lowest PO-accepted story = {m['min_score_accepted_by_po']}, "
          f"highest PO-rejected story = {m['max_score_rejected_by_po']} (threshold 3.0)")
    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / f"{datetime.now():%Y%m%d-%H%M%S}.json").write_text(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
