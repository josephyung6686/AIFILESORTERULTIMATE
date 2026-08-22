# Appendix — what the section authors reported rather than resolved

Each section closed by naming its own contradictions instead of silently resolving them. That is the
mechanism that found this project's defects, so the reports are kept **verbatim**, grouped by the
section that made them. **They are dated, and they are not all still true** — several were closed by
rulings made after they were written. Read the preamble first; it wins.

`PLAN-tasks-07-09.md`'s appendix covers Tasks 7, 8 **and** 9, though only Task 7 came from that file.
Its Task 8/9 rows are kept because they are evidence about the **tasks**, not about the file — but
the tasks themselves come from `PLAN-tasks-08-09.md`, whose own appendix follows.

## What in here is no longer true

**The Tasks 7–9 section's item 2 is OVERRULED and must not be followed.** It recommends addressing
the six reliability states **by index** into P4's tuple. Brief §11 ruled the opposite: **Task 1
publishes one named constant per state and every other module imports it** — never a bare string,
never an index, because an index silently couples every consumer to the tuple's order. The *problem*
item 2 identifies is real and was fixed; the *recommendation* it makes is not the fix. The same rule
now extends to `FACT_ORIGINS`, `ATTEMPTED_PRODUCERS` and `UNRESOLVED_REASONS` (preamble §3.1).

**Every "the cache-key rule is written out per module" apology is closed.** One helper in
`facts.cache` — Task 6's — keyed per **(file version, deterministic pass)**, and every producer
imports it. Three of the four section front matters carried the *losing* rule (keying on the
observations a fact cites); the preamble carries the winner and the abstention argument that decides
it. Counts of "five copies" or "seven copies" are historical.

**`field_id` no longer exists.** The column is `field_key` and it is `fields`' PRIMARY KEY. Any row
below discussing the two-name collision is describing a defect that has been fixed — including the
one where Task 2 carried **both** columns holding the identical string.

**`destination_eligible` is TRUE for `target_school` and `client`** (D9), and the academic key is
`subject` with no `course` row (D6). Rows asserting all four §3.8 role fields are ineligible are
stale.

**Still open, and still exactly as reported:** the A04 adversarial fixture contradicts Done-means 22
(it is worded as the suppression tier and carries the demotion tier's expected outcome), and
catalogue 01's 115 entries still have no compiler — the working matcher one section wrote belongs
with the loader, not in `src/facts/`.
