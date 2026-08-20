# Overnight run — start here

Date: 2026-08-21 · Joseph asleep · **1,244 tests passing**

Everything I could decide, I decided and built. Everything that was yours, I refused and wrote down.
This page is the entry point; read it in order.

---

## 1. If you have ten minutes

Open **[`council/DECISION-BRIEF.md`](council/DECISION-BRIEF.md)**. It opens with the whole thing
on one page — six decisions in the order to answer them, with the recommendation, the dissent, and
whether each is a one-way door. Then six sections, each with the
question, what is already settled, the options, and where three independent seats disagree and what
the disagreement turns on. Every quotation in it was matched mechanically against your words — 61
spans, 0 failures.

Then skim **[`NEEDS-JOSEPH.md`](NEEDS-JOSEPH.md)** — the full decision log, about 25 items, each with
the assumption the code currently holds so nothing was decided by silence.

## 2. The three findings I would want you to see even if you read nothing else

**Your words have no tables in them.** `00-database-agent-product-design.md` contains zero pipe
characters and zero section numbers. The `| Domain | Fields |` table that four artifacts cite as the
design, and the §-numbers this whole project is written in, exist only in
`01-product-design-structured.md` — a rendering that calls itself *"derived from the source of truth,
not a substitute for it"*. What you actually wrote is six hedged sentences: *"Academic files **may
use** school, term, course, instructor, and work type."* P6's SPEC turned that into a closed list of
~37 fields and forbids everything else. **You never closed it.** I verified this myself rather than
taking it on report.

**Nothing classifies a file.** P7's gate is specified in detail and works. But no part's SPEC claims
the *detector* that writes the classification — P7 says the rule set is "hand-authored" and that it
merely "publishes the vocabulary the detectors write into". So after P7 ships, `sensitivity_state`
stays NULL, every file is `unreadable_unclassified`, and §8.4's gate denies the entire corpus while
working exactly as designed. This is a hole between all thirteen SPECs, not a defect in one.

**The label you asked for never reached the database.** Your constraint had two halves. The first —
apps and system files never read or moved — is implemented and defended, and a council seat tried to
break it and could not. The second was *"we have a label for it as unread or untouched… and there
will be a place where the user can find this later in the UI."* `LABEL_UNTOUCHED_PROTECTED` existed
as a constant whose only use anywhere was a test asserting it equalled its own literal. **Fixed** —
it is now a field on the verdict, persisted, and probed on a real scan.

## 3. What was built and fixed

Nine defects, each found by execution and fixed test-first. In rough order of how badly they would
have hurt:

| | |
|---|---|
| The sensitivity signal was keyed to the **wrong run** — §2.9's "addresses and message content as potentially sensitive" landed on the filename | fixed, probed |
| A published "emit order" that was random-UUID order, with a live consumer indexing into it | fixed, probed |
| A caller's ordering error became `completeness=failed` for every text-bearing PDF, and downstream would have made the gate deny them all | fixed |
| Routing decisions and sensitivity signals were computed and dropped by the caller | fixed |
| `handling_class` was being fed P1's `sensitivity_state` — a different field on a different record | fixed |
| An extractor upgrade did not invalidate the stat-cache reuse, so a shipped bug would live forever | fixed |
| The untouched-protected label reached no row | fixed |
| An unrouted run's observations carried the indexer's extractor name | fixed (parallel session) |
| P6's absent verdict was faked as `False` rather than named | fixed |

## 4. The deliverables

| What | Where | Size |
|---|---|---|
| **Decision brief** | [`council/DECISION-BRIEF.md`](council/DECISION-BRIEF.md) | six decisions, three seats |
| Council seats | [`council/`](council/) | design reading · what ships · what goes wrong |
| **P6 plan skeleton** | [`../parts/P6-facts-facets/PLAN-SKELETON.md`](../parts/P6-facts-facets/PLAN-SKELETON.md) | 27 tasks, coverage table |
| **P7 plan skeleton** | [`../parts/P7-privacy-consent-gate/PLAN-SKELETON.md`](../parts/P7-privacy-consent-gate/PLAN-SKELETON.md) | 22 tasks, negative-test table |
| **Five review rounds** | [`reviews/`](reviews/) | fidelity · buildability · adversarial · connection · scope |
| **Domain catalogue** | [`../domains/`](../domains/) | **574 domains**, 14 slices, gated clean |
| P1–P7 connection contract | [`../22-p1-p7-connection-contract.md`](../22-p1-p7-connection-contract.md) | the seams |

## 5. The domain catalogue

560 domains across thirteen slices — education, career, research, personal, finance and legal admin,
healthcare, legal practice, software, engineering, creative, business operations, government, and the
trades/property/logistics slice. Each entry carries a schema, recognition rules split into
deterministic / needs-LLM / never-alone, work types, grouping reasons, a template dimension order with
its justification, collisions with neighbours, and an honest `design | inference | proposal` marking.

`planning/domains/check.py` gates them: required fields, §3.13's six reliability states, §2.9's two
sensitivity values, no held thresholds, no duplicate ids, and — the one that matters — **every design
quotation checked against your words. Zero fabrications across all thirteen files.**

A **fourteenth slice** closed a demonstrated gap: no domain in the first 560 owned calendar
artifacts, though `.ics` routes to a `calendar` source type and two authors cited a calendar domain
expecting one. **574 domains, and every cross-reference now resolves — the gate reports zero
problems, in-file and cross-file.**

## 6. What I did not do

- **Answer anything in `NEEDS-JOSEPH.md`.** Where I had to proceed, the assumption is stated.
- **Build P6 or P7.** They are planned and reviewed five times; the first task is not written.
- **Wire a production reader.** P1–P5 still cannot open a real PDF — every reader is injected and
  has no implementation. That is by design and it is the thing "P1–P5 works" most easily hides.
- **Rename 1,287 catalogue fields** to one convention, though two are in use. That is B3, and doing
  it on my own reading is the kind of silent decision this log exists to prevent.
