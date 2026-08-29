# P6 / P7 plan review — five rounds, five lenses

Fresh context each round. Distinct lenses so rounds deepen rather than repeat, and
each round reads the prior rounds' findings so it does not re-report a closed one.

| Round | Lens | Question it answers |
|---|---|---|
| 1 | **Contract fidelity** | Does the plan say what the SPEC and the design say? Every Done-means, every citation, every vocabulary. |
| 2 | **Buildability** | Could an engineer with no context execute this? Missing interfaces, undefined types, unstated ordering. |
| 3 | **Adversarial** | Where will this reproduce the defect classes this project keeps hitting? |
| 4 | **Connection** | Does it actually attach to built P1–P5, and will P1–P7 join? |
| 5 | **Simplification and scope** | What is overbuilt, invented, or beyond the design? What can be deleted? |

## The defect classes round 3 hunts for — all observed in this repo

1. **Two vocabularies for one concept** — one value under two names (`sensitivity` / `sensitivity status` / `sensitivity_state`).
2. **Two computations for one value** — `config_fingerprint` computed two ways; P4 rejected every P5 run.
3. **A decision reaching one document and not another** — ratification B8 amended a Done-means item that still reads the old way.
4. **A dead path** — §2.7's OCR route no real image could reach; green in every test.
5. **A column with no writer** — `extraction_status_by_tier`, `extraction_routing`, `sensitivity_state`.
6. **A value computed and dropped** — `Dispatched.sensitivity`, discarded by the caller.
7. **Scanning text for a token** — matches comments and docstrings. **Ten occurrences.**
8. **A published order that is not an order** — "emit order" that was uuid4 order, with a live consumer indexing into it.
