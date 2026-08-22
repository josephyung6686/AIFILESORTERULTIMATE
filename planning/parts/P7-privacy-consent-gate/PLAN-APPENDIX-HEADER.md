# Appendix — what the section authors reported rather than resolved

Each section closed by naming its own contradictions instead of silently resolving them. That is the
mechanism that found this project's defects, so the reports are kept **verbatim**, grouped by the
section that made them. **They are dated, and they are not all still true** — several were closed by
rulings made afterwards. Read the preamble first; it wins.

Two of these appendices belong to files whose **last task lost** — `PLAN-tasks-04-07.md`'s sits after
its Task 7 and `PLAN-tasks-15-22.md`'s three sit after its Task 22. They are kept because they are
evidence about **tasks**, not about files.

## What in here is no longer true

**Two labels are wrong.** Passages citing **NEEDS-JOSEPH C5** for *"does P6 keep a
`sensitivity_status` field row"* mean **C24**; passages citing **C3** for the region origin mean
**C22** (brief §14 renumbered both).

**Three questions below are RULED, and every "held open" / "remains for Joseph" row naming them is
stale:**

| Row as written | Now |
|---|---|
| *"Whether P6 keeps a `sensitivity status` field row beside P7's record … Joseph."* | **D7** — P6 creates **no** such row. P7's `ClassificationRecord` is the sole home, and P7's Contract-in from P6 is empty. **C24 and C25 closed.** |
| *"Which corner `norm` measures from … P4's, and nobody's yet."* | **D10** — `norm` is **TOP-LEFT**. `readers.ocr_vision._box` converts Vision's bottom-left rectangles at the adapter (`87016b0`). **C22 closed**, and Task 8's redaction may rely on it. |
| *"SPEC §6 and §7 cannot both hold for `release_id` … Joseph / Task 10."* | **D14** — `AuditRecord.release_id` is `None` on a release record and the join runs **ledger → events**. SPEC §7 amended; §6's ordering stands. |

**One citation that looks like the first row but is NOT, and must not be swept up with it.**
`PLAN-tasks-11.md` cites **C5** as the reason `SENSITIVE_CLASSES` stays unpublished. That label is
**correct** and the question is **still open**: C5 is *"is `protected` exactly the top two handling
classes?"*, which D7 did not touch. **Reading D7 as licence to publish that set would be exactly the
error the restraint exists to prevent.**

**The five round-5 cuts are ruled KEPT (D13)**, so any row describing one as "unratified, may be
deleted" now means "ruled, kept, and revisitable" — the tasks keep their callouts so a later reader
can decide against them with the plan in front of them.
