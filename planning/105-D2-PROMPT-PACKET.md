# 105 — D2 prompt packet: four unwired sites and the A_fact glossary, drafted, stressed and measured, for ratification

Date: 2026-09-06. Status: **drafts for the owner's ratification — nothing here is ratified and nothing here is wired.**
Protocol: `103` §28.1 (requirements traced to `00`; a traced draft; stress cases; a bakeoff of at least two candidates under both models; ratification with the numbers attached). Governing rulings: `104` §13.5 (model decides, rules validate), §13.6 (grounding hard, the rest shown), §13.7 (model names, user confirms), §13.8 (refinement allowed, removal constrained); `00` Amendments of 2026-09-05.

Every template id below carries `unratified` and its date. The ratified A_fact files are untouched; every new file sits beside them under `src/llm_harness/library/`. The bench is `tools/promptbench/` and every number in this document was produced by a command written next to it.

## 0. How to read this packet, and what changed on 2026-09-06

Three process additions from the coordinator, all honoured here: work is committed per unit (each requirements trace, each draft, each bakeoff run), anything that may run longer than three minutes runs in the background and is polled, and every local request sets `num_ctx` explicitly above the measured prompt length and records the value used — Ollama otherwise truncates silently to 2,048 tokens and answers anyway.

Sections 1 to 5 follow the site order `103` §28.1 fixes (C and D, then B, then E), with the A_fact glossary revision (fix-chain step 1, `104` §11.2) placed first because every other site's numbers are downstream of it. Each site section has the same six parts: requirements traced to `00`; research applied; the candidates, with the winner and the loser and their numbers; the stress-case table; contract gaps found; the ratification question.

## 1. A_fact — the `school` and `subject` glossary entries (fix-chain step 1)

*(pending)*

## 2. C_placement

*(pending)*

## 3. D_residual

*(pending)*

## 4. B_group

*(pending)*

## 5. E_template

*(pending)*

## 6. Research applied across the five sites, with citations

*(pending)*

## 7. Contract gaps register

| # | Site | What the contract cannot express or does wrongly | Where | Pinned by | Consequence for ratification |
|---|---|---|---|---|---|
| *(pending)* | | | | | |

## 8. Cloud calls used and tokens spent

*(pending — the bench ledger is the source; the cap is 400 calls.)*
