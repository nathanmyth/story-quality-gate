# Risk Register

L = likelihood, I = impact (High / Medium / Low). Reviewed each iteration.

| ID | Risk | L | I | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|
| R-01 | **Gaming the gate:** POs add boilerplate ("Given… when… then works") to pass | M | M | Measurability checks on criteria; random review of passed stories in refinement; the gate supports the Conversation, it doesn't replace it | Scrum Masters | 🟡 Open |
| R-02 | **Gate seen as policing:** teams resent a tool that rejects their work | M | H | Position as PO self-check; coach suggests fixes; no team-by-team leaderboard | RTE | 🟡 Open |
| R-03 | **Rubric overfit:** labels and rubric written by the same person, so eval is optimistic | H | M | M3 calibration with real stories labeled blind by 2–3 POs | TPM | 🟡 Open |
| R-04 | **False rejects slow teams down** | M | M | Track false-reject rate; PO can request override with a reason (v2) | TPM | 🟡 Open |
| R-05 | **Jira API token exposure** | L | H | Service account with project-scoped permissions; token in `.env` / secret store only; never logged | Jira admin | 🟢 Monitoring |
| R-06 | **Jira schema differences** (story points field, issue types) break creation | M | M | Configurable field IDs; sandbox test in M2; clear error messages | TPM | 🟡 Open |
| R-07 | **AI coach invents requirements** | M | M | Coach marks assumptions; rewrite must be reviewed and resubmitted (ADR-002) | PO | 🟢 Monitoring |
| R-08 | **Quality score used as a performance metric** for individuals | L | H | Report only at ART level; agreed with RTE and HR in M1 | RTE | 🟡 Open |
