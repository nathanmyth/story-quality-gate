"""Streamlit app:  streamlit run app.py"""
import streamlit as st

from src import coach, jira_client
from src.gate import run
from src.scorer import rubric, score
from src.story import parse_text

st.set_page_config(page_title="SAFe Story Quality Gate", page_icon="✅", layout="wide")
rb = rubric()
st.title("✅ SAFe Story Quality Gate")
st.caption(f"Rubric v{rb['version']} · Saves to Jira only when the score is ≥ {rb['pass_threshold']:g} / {rb['max_score']} "
           "and at least one acceptance criterion is testable.")
st.caption("Jira: " + ("connected" if jira_client.configured() else "dry run (set JIRA_* in .env to save to Jira)"))

EXAMPLE = open("examples/good_story.txt", encoding="utf-8").read()
left, right = st.columns([5, 6])

with left:
    text = st.text_area("Story", EXAMPLE, height=300,
                        help="Labels: Title, Type (user / enabler - <type>), Acceptance criteria, Story points")
    check = st.button("Score story", type="primary")

if check or "card" in st.session_state:
    story = parse_text(text)
    card = score(story)
    st.session_state["card"] = True
    with right:
        icon = "🟢" if card.passed else "🔴"
        st.subheader(f"{icon} {card.score:g} / {card.max_score:g} · {card.decision}")
        st.progress(card.score / card.max_score)
        for c in card.criteria:
            st.markdown(f"**{c.name}**: {c.points:g} / {c.max:g}")
            for f in c.feedback:
                st.caption(f"↳ {f}")
        for b in card.blockers:
            st.error(f"Blocked: {b}")

        if card.passed:
            if st.button("Save to Jira"):
                res = run(story)
                if res.jira["url"]:
                    st.success(f"Created [{res.jira['key']}]({res.jira['url']})")
                else:
                    st.success(f"Dry run: {res.jira['key']} written to data/jira_outbox.jsonl")
        else:
            st.info("Not eligible for Jira. Fix the items above and score again.")
            if coach.available() and st.button("Suggest a rewrite"):
                with st.spinner("Drafting a rewrite…"):
                    st.code(coach.suggest_rewrite(story, card), language="markdown")
                st.caption("Review the rewrite, paste it into the box, and score it again.")
