# 63 — Implementation plan for what comes after the engine

Date: 2026-08-28. Owner instruction: *"add building this into the task plan but only
implementation plan, and only when you are confident that P1–P11 is perfect."*

Design for items 2–4 is `62-DESIGN-EXTENSION.md`; contract is `61-ONBOARDING-AND-SEARCH.md`.
This document is sequencing and a gate. **Nothing below starts until §0 passes in full.**

---

## 0. THE GATE — what "P1–P11 is perfect" means, checkably

Not a feeling. Ten conditions, each verifiable by a command, each currently FALSE or UNKNOWN.
Re-run the whole list; a single failure holds the gate closed.

| # | condition | how it is checked | today |
|---|---|---|---|
| G1 | Full suite green | `python3 -m pytest tests/ -q` → 0 failed | 1 failed |
| G2 | Scale suite green | `SCALE_STRESS=1 python3 -m pytest tests/integration/test_scale_stress.py -q` → 0 failed | ≥1 failed |
| G3 | No strict xfail left standing | grep `xfail(strict=True)` → each one closed or argued in writing | 1 open (P9 versions) |
| G4 | Test order independent | `pytest-randomly` installed, three seeded runs agree | never run |
| G5 | Every schema can file | all 23 either have templates or are a named protection/safety exemption | 6 of 23 |
| G6 | `load_catalogue` has a caller in `src/` | the existing guard in `tests/integration/test_ambiguity_cases.py` inverts | no caller |
| G7 | P8→P11 has a production composition | a callable in `src/` runs the chain, as `run_production_p1_p7` does for P1–P7 | absent |
| G8 | Nothing inert | every concept has a reader, or a guard that fails when a producer appears | 7 of 10 wired |
| G9 | graphify audit clean | `graphify update .` then a connection pass over every part boundary | not run |
| G10 | The persona re-run | `59`'s evaluation redone against the new state; no persona fails on a defect this plan could have fixed | not run |

**G10 is the one that matters most and the one most easily skipped.** The other nine measure
whether the machine works. G10 measures whether a person can use it, which is the north star and
is not implied by any of the others.

---

## 1. Finish the engine (in flight or queued — this is not "after")

Listed for completeness because the gate depends on it, not because it is part of this plan.

1. Multi-domain branching, P9 acceptance across versions, placement retrieval cost, the
   two-home message, identity resolution cost — all in flight.
2. Templates for the 17 uncovered schemas — in flight, four agents.
3. `load_catalogue` caller · merge the wave-2 library · tree-health quadratic · width cap ·
   residual questions ordering · `sensitivity_policy_ref`.
4. P8→P11 production composition, and a CLI.

---

## 2. The corpus role declaration — FIRST after the gate

It is first because it is an **engine input**, not a feature: it changes what the engine can
resolve, so building it after P12 would mean re-validating P12 against a changed input.

- **2a** Store and record shape. Facts carry `basis="user"` (already a live
  `CLASSIFICATION_BASES` member) and outrank an inferred fact of any reliability.
- **2b** The structural/contextual split, enforced by types rather than convention. The test
  that matters: a contextual answer cannot reach a gating decision, and a deliberate attempt to
  route one there fails.
- **2c** The four questions, all skippable, product correct with all four skipped.
- **2d** The profession matcher — free text onto the closed schema vocabulary, recording an
  unmatched answer **as unmatched**. This is the interesting problem; budget for it separately.
- **2e** Wire to schema activation and dimension eligibility. Discriminating pair: a dependant's
  name may become a folder level, a third party's name may not.

**Done means:** the four role inversions `62` §A names — take-or-teach, own-lease-or-client's,
own-résumé-or-candidate's, which-child — each resolve on a corpus where they previously abstained,
and each still abstain when the question is skipped.

## 3. Retrieval — SECOND

Second because it is the cheapest thing that makes the product usable by a person, and it needs
no P12 and no P13.

- **3a** Query over the existing index; **no second ranking**.
- **3b** Every home, not the best one.
- **3c** Abstention as a result, in its own words — a passport is not a low-confidence extraction.
- **3d** Protected areas present, counted, unopened, with a reachable explanation.
- **3e** Read-only, asserted: a search leaves database and filesystem byte-identical.

**Done means:** a person can find a file they have not organised, and a protected area appears in
the result set rather than being absent from it.

## 4. P12 — apply and undo — THIRD

Third because automatic filing (§5) is undo plus a policy, and building §5 first would mean
shipping irreversible movement.

- **4a** Apply a frozen plan; **4b** undo, per action, durable across restart; **4c** conflict
  handling when the disk moved under the plan; **4d** never touches protected, applications, or
  system files.

**Done means:** every move is individually reversible, and reversal is tested by reversing.

## 5. Automatic filing — FOURTH

- **5a** Per-branch policy the user sets, scoped to the branch reviewed, never generalised.
- **5b** Declines on small margin, genuine tie, thin evidence, or protected material — and
  declines in the words that describe what happened.
- **5c** Dry run, default on first enable.
- **5d** Reviewable list afterwards, each action individually reversible.
- **5e** Never creates a destination; a file with no approved home stays and is surfaced.

**Done means:** the dangerous capability is only ever reachable by a deliberate, scoped act, and
every automatic action can be undone by someone who noticed it a week later.

## 6. P13 — the review canvas — LAST

Last because it is the surface for everything above, and building it earlier means building it
twice. It carries §5.10's six existing-folder gestures and the five unimplemented canvas actions.

---

## 7. What this plan does not do

- It does not schedule the three open questions in `62` §C — the profession matcher's failure
  mode, re-running onboarding after freeze, and how long "individually reversible" lasts. Those
  are owner decisions and are listed there to be answered, not assumed.
- It sets no dates. Every item above is gated on the one before it, and the gate in §0 is gated
  on work that is still in flight.
