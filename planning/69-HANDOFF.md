# 69 — Handoff, 2026-08-29 (evening)

Supersedes `67-HANDOFF.md`, which is now historical. `67` is still correct about the standing
constraints and about where two agents stopped; everything it lists under "what to do next" has
been done or has moved.

**Authority order, unchanged:** `00-database-agent-product-design.md` wins → `66` and the part
SPECs → PLANs → live `src/`.

**Standing constraints, unchanged and non-negotiable:**

- **Security.** Reports, apps, system files and anything sensitive in that sense are **MARKED AND
  COUNTED, NEVER OPENED**. Present-but-untouched, with a reachable explanation, **never silently
  omitted**.
- **North star.** Judge every decision by what a real, multi-role human would want — not the lawyer
  OR the parent OR the researcher, but the person who is several of those at once.
- **Manual approval** for templates and mechanisms.
- **Git.** Stage and commit in ONE shell invocation with EXPLICIT paths. Never `git add -A`.
- **`python3`, not `python`.**
- **`-p no:randomly`** when a `thinc`/spaCy import is in the interpreter, or every test errors in
  setup and teardown. For the order-independence run the invocation is
  `python3 -m pytest tests/ -q -p randomly --randomly-dont-reset-seed`.

---

## 1. Where the gate stands

| | condition | state |
|---|---|---|
| G1 | full suite green | ✅ **5232 passed, 19 skipped, 1 xfailed, 0 failed** |
| G2 | scale suite green | ✅ **CLOSED** — 19 of 19 (`f5132a1`) |
| G3 | no strict xfail standing | ✅ one, correctly argued |
| G4 | order independent | ✅ 5232 passed randomised |
| G5 | every schema can file | ✅ 19 of 23 + 4 named exemptions |
| G6 | `load_catalogue` has a caller | ✅ |
| G7 | P8→P11 production composition | ✅ |
| G8 | nothing inert | ✅ 1 genuine (`sensitivity_policy_ref`), explained by `66` §4 |
| G9 | connection audit | ✅ 3 findings recorded |
| G10 | **the persona re-run** | **RUN — and it does not pass.** `68-PERSONA-RERUN.md` |

**Nine of ten are green. G10 is the one that is not, and it is the one that matters.** It has been
run properly now rather than left "not run": four corpora through the shipped command, with the
output and the database state recorded. It fails for three named reasons, §3 below.

---

## 2. What this session did

### The engine now tells the truth about what a corpus contains (`53c41d1`)

Three defects, one commit, all three found by `65`'s live runs rather than by the suite.

1. **The refusal blamed the step that worked.** Every file said *"nothing has been able to read
   enough of it"* when `file_facts` held a `direct` fact and `classifications` held nothing. Read,
   not classified. P11 now claims what it knows (nothing classified this file) and nothing about
   what it does not (whether the file was readable — that is P4's `extraction_runs`, which P11 does
   not read).
2. **The extractor could not read a course code with a space.** One separator added and no more:
   `PHYS 1401` and `PHYS-1401` now read as the identifier they are and canonicalise to the same
   value as `PHYS1401`. `63` §10's ruling — a reading failure is fixed by reading better, never by
   asking the person.
3. **Four files from one course became four groups.** A group id was derived from its seed's FILE,
   so four files stating one course code minted four one-file groups with one label and an empty
   `Coursework` folder. A fact-backed seed's claim is not about its file, so the address is now the
   identity it states, and a second file stating it JOINS the standing group. A user seed keeps the
   file address — the user said THIS FILE starts a group.

**And the seam underneath all three, which is the one worth remembering.** `cli.py` wrote
`scan_state = "scanned"`; P9's `_corpus` admits `"included"` and nothing else. So on **every live
run, every file had an empty neighbourhood** — no shared-fact edge could be built and no group could
ever hold two files, whatever the corpus said. P9's own tests write `included`, so five thousand
passing tests agreed with a production path that could not work. The composition root now imports
P9's constant instead of respelling it.

`record_edges` also had no caller in `src/`: every run drew a typed-edge graph, decided on it, and
dropped it. `66` §3 makes "also related to" a state a person is SHOWN, and a relationship whose
evidence was never stored cannot be shown. It is written now.

### G2 closed by fixing the shape, not the test (`f5132a1`)

`00`:256 reads *"Maximum folder proposals and maximum depth"* — **two numbers on one line**, where
every other line in §8.6's list is one quantity. P1 published one key for both and P10 read the
single value four times, two of them wanting opposite values. P1 now publishes
`tree.max_folder_proposals` and `tree.max_depth` — seventeen keys. **This adds no ceiling the design
does not state**; publishing one key for two was the deviation.

### G10 run (`68-PERSONA-RERUN.md`, `c1ddc8f`, correction `c9f7ebf`)

Four corpora — a litigator, a student who also teaches, a two-child household, and one person who is
all three — through the shipped command. See §3.

### `66` §17's property is pinned (`ae04cff`)

`63` §10 left one thing to verify when `build-edit-durability` landed. Both halves now have a test:
the edit record carries no plan version and is keyed on the vocabulary triple, and recording an edit
leaves the frozen tree byte-identical. Falsified rather than assumed — making the writer also touch
`tree_nodes` fails the assertion.

### P12 and P13 have implementation plans (`93b788d`)

`planning/parts/P12-apply-undo/PLAN.md` (14 tasks) and
`planning/parts/P13-review-approval-surface/PLAN.md` (20 tasks), written to the house standard.
**Neither part is started, and neither should be started before `66` §22's sequence says so.**

---

## 3. G10's three blockers, which are the real state of the product

Four people, four disks, one outcome: **0 files ready to file, a one-folder tree, 26 of 26 files
"waiting for you to say what these are".** Nothing was misfiled and nothing was lost — the product
is honest at every step — but nobody got an organisation.

| | blocker | whose |
|---|---|---|
| 1 | **No classifier ships**, so every file for every persona stops unclassified | **Joseph** — `65` §2.2's sizing question, open by decision. `68` measures its price: it is the terminal state for everyone, and no other improvement is visible until it is decided. |
| 2 | **The non-interactive review merges every group into one**, so the tree cannot be deeper than one folder | **P13.** Verified by experiment: accepting each group as itself gives Priya `PHYS1401` and `PHYS2801` — and loses the branch name she asked for. No default can decide that; a review screen can. |
| 3 | **A client's passport number became a group's display label**, and under per-group acceptance printed as a proposed FOLDER NAME | **P13 + P12** — must close before anything materialises a folder from a label. |

Two more, both `66` design work already owed and correctly unbuilt: **no field names the child**
(Tom's two report cards are one group — `66` §15), and **one `--situation` per run mislabels half
the disk of a person with two roles** (`66` §13).

---

## 3a. What writing the two plans found, which is not future work

Both plan authors flagged conflicts rather than resolving them, per the authoring brief. Most are
about parts that do not exist yet and stay in the plans. **Two are claims about the repo as it
stands today, and I verified both.**

### Three incompatible `review_action` fixtures are already shipped, and only one can be right

P13 publishes ONE `review_action` record. Three parts have already written a fixture for it, each
encoding the view of the part that expects to RECEIVE the action:

| | identity field | when | how the subject is named |
|---|---|---|---|
| `tests/p9/p13_fixtures.py` | *(none)* | `decided_at` | `group_id` + `membership_id` |
| `tests/p10/p13_fixtures.py` | `review_action_id` | `observed_at` | `subject_ref` |
| `tests/p11/p13_fixtures.py` | `action_id` | `acted_at` | `subject_ref` + `session_id` |

Three names for the identity, three for the timestamp, and two different ways of naming what was
acted on. Only P11's matches the SPEC. **This is the same shape as the `scan_state` defect fixed
today** — two parts, two spellings of one thing, each correct in its own vocabulary, both green —
and it will bite in exactly the same way when P13 ships the real record. P13's plan handles it
correctly: Task 9 ships a strict-xfail compatibility report, not a shim that hides it.

### §8.2 has no event type for an action that was REFUSED

`RESERVED_EVENT_TYPES` is `00` §8.2's nineteen, verbatim, and registration is *"a spec-level act…
There is no run-time registration call."* It carries `failed move` — a move attempted that failed.
P12's Done-means 13 needs a record for a move **refused or paused before it was attempted**, which
is a different event, and the distinction is the same one this project already enforces between
"unreadable" and "unclassified". **Adding an event type is Joseph's**, not a part's.

### Everything else stays in the plans

P12 flagged 17, P13 flagged 6 plus ten still-open SPEC questions. The rest are all one of: an
authority with no producer yet (`root_anchor` paths, the §8.4 permitting policy, any filing-policy
record — so `66` §9's dry-run surface, §10's distinct filing refusals and the activity list's
"authorizing policy" are carried as explicit `None` with a note, never faked), or a SPEC open
question neither author would answer on Joseph's behalf.

---

## 4. What to do next, in order

1. **Joseph decides the sizing question** (`65` §2.2, `68` F1). Widen the extractor, narrow the
   detector, or ask the user. Everything a person sees is downstream of it. **This is the single
   highest-value decision available and no code should pre-empt it.**
2. **Joseph confirms `66` §24's judgement repair** — §7's sentence about what a wrong move costs was
   reconstructed. Still open from `67` §6.
3. **The role-declaration guidance he still owes** (`66` §16). Nothing in §16 should be built until
   it arrives.
4. **Answer: what subset of P1–P11 does Find actually need?** Find needs the index, evidence,
   retrieval and privacy. It does not obviously need frozen trees or placement, in which case it
   ships earlier than the full gate. Still open from `67` §6.
5. Then `66` §22's sequence, unchanged: **Find** (local, read-only) → connect Find to the review
   surfaces → the onboarding question registry → P12 → automatic filing.

**Do not start P12 or P13 from their new PLANs yet.** They exist so that the work is ready when the
sequence reaches it, and `66` §22 puts automatic filing last for reasons `68` did not weaken.

---

## 5. One thing worth carrying forward about how the defects were found

Every defect fixed today was found by **running the product over files on a disk**, and none of them
by the 5,000-test suite — which was green throughout and agreed with a production path that could
not form a group of two files. The suite is not weak; it is a claim about parts, and every one of
these was a claim about the seam between two parts that each tested correctly in its own vocabulary.

`65` said this once already about the first run. It is now true of the second and the third. **The
cheapest audit available to this project is to point the command at a real folder and read what it
says.**
