# 108 — HANDOFF, 19 September 2026

**Read this, then `104` §18.108–18.115, then `00`'s amendments 12a and 16–25.**
Everything below is either a commit you can read or a measurement you can re-run.
Where a number is stated, its grain is stated with it, because three of this
session's errors were row counts reported as file counts.

---

## 1. The one-paragraph state

All eight phases of `planning/106-SORT-PLAN.md` are merged. The product builds a
tree whose top level is a **life** (`Education`, not `research`), records the
judge's answer as a fact, lets the person file a protected record by hand, and has
producers for fields the folder templates are actually built from. **41 commits on
19 Sep.** Main is `build/p6-p7-first-packages`, green apart from what §4 lists.

**The product is not finished.** What remains is mostly not plumbing: the template
library does not cover the person it is run for, and many files do not say what
they are.

---

## 2. START HERE — the one thing that blocks a usable run

**`00` amendment 25 is merged and its consequence exceeds what the owner
ratified.** They approved "the unjudged default has no folders beneath IT". What
actually happens is that `downstream` returns `None` when the default branch is
unsettled (`cli.py` ~20290), so **the owner's corpus now yields the question screen
and NO TREE AT ALL** until they answer at `branch:<label>` or a model judges the
residue. `Education` disappears with it.

**The task:** teach the run to build the rest of the tree around an unsettled
default. The agent that built 25 identified the seam and deliberately did not
touch it because other work was live in those files:

```
said() readers to teach:  cli.py 16765, 16979, 17185, 17192, 17202, 20340
plus:                     P11 taught to run with an unsettled default
```

Do this first. Until it is done the product cannot be demonstrated end to end.

---

## 3. What is ratified and NOT YET BUILDABLE

Three of the owner's rulings are recorded and blocked. **None of them is blocked on
a decision — each is blocked on a missing mechanism.**

| ruling | blocked on |
| --- | --- |
| **19** — a club goes to the school that hosts it | a `school` fact per file. `106` Task 6.4 (merged, `6bbfae67`) now SHOWS a one-anchor school and takes the person's `--confirm`, but the club→host-school ROUTING is not built. 36 files have no life until it is. |
| **22** — `year` bound as a folder level on Current work and Career applications | **rows cannot do it.** `folder_levels_for` (`production.py:610-616`) builds levels only from the template's default-order dimensions and silently DROPS any other binding — proved by script. Needs a dimension in `definitions.json`, and one default order cannot serve both `employer → year` and `year → organization`. |
| **21** — situations authored for Health and Travel | the rows exist at `src/tree_design/library/drafts/health_travel.json`, wired to NOTHING, with a gate test asserting the names are absent from the shipped release. **`travel.trip-records` is a NEW name and would enter the `finance` menu, which goes to the CLOUD.** Do not wire before the owner ratifies the name. |

---

## 4. Known red / known wrong

- `tests/integration/test_r37_*` tree-shape failures appear in some runs; they were
  byte-identical to the pre-change baseline when last diffed. **Diff before
  recapturing** — a recapture that is not diffed proves only that the code equals
  itself.
- **A residual regression from amendment 16**, declared in `e9b7c550`: a file under
  a two-kind life branch whose kind came from a deterministic ANCHOR, and which
  site G left silent, gets no question. Before the Education ruling it had its own
  one-kind branch and was asked. Closing it needs `kind_of` on `Branch`.
- `tools/groundtruth/measure.py` now reads ONE plan version or refuses
  (`AmbiguousPlanVersion`). **The owner's database has two frozen plans, so it
  refuses there.** Pass `--plan-version` explicitly.

---

## 5. The measurements that matter (all file-grained unless said)

```
files                                    371
files with a situation FACT              227   (257 is the ROW count -- do not use it)
files reaching a life                    227   (0 reach none, after Phases 3+4)
files in a group                         133
grouping purity                        89.2 %  (over the 133; reads memberships, not nodes)
classification, key-in-what-it-said     97.7 %  (run 22; NOT re-claimable -- see below)

subject                    35 of 371     institution   17 of 371
work_type                  46            file_type    249  (a FORMAT, not a purpose)

model_returned_unknown:  work_type 163 | term 144 | subject 128 | institution 119
no_candidate_evidence:   term 368 | work_type 332   <- ALL `attempted_producers=["rule"]`
```

**`no_candidate_evidence` is the deterministic RULE abstaining. It says NOTHING
about the model's packaging** (`104` §18.109's correction). The lead built a whole
false diagnosis on the column's name.

**The 97.7 % may not be re-claimed** until the grader prefers the fact's own value
where it is already a situation id: `106` Phase 2(b) changed that fact from holding
the KIND to holding the SITUATION, and the grader's prefix fallback would score a
real disagreement as a match.

---

## 6. Why the tree is thin — three causes, not one

1. **The library does not cover this person** (`104` §18.112). 113 of 208
   situations serve law practice, construction, manufacturing, engineering, retail,
   logistics, HR and government. `academic` has 11 situations for their 95 academic
   files; `creative` has 28 for their 3; **`medical` has 0**. No code fixes this.
2. **Many files genuinely do not say what they are.** 35 of 43 labelled files carry
   no course code anywhere in their own bytes. `subject`'s 128 declines are
   substantially HONEST. No packaging invents a course a document does not name.
3. **One field's definition describes nothing.** `field_glossary.json` gives
   `work_type.meaning` as `record_type`'s ROUTING NOTE. 163 declines sit on it. A
   replacement is proposed in `d8dd85b1`'s message, **not wired** — it is library
   text and the owner's alone.

---

## 7. How to work here

**The owner's standing orders.** Never stop or ask permission to continue; commit
per deliverable; conservative with credits. Agents never spawn subagents. Agents
never edit `src/privacy/**`; in `src/llm_harness/library/**` and
`src/recognition/library/**` they may ADD a versioned row, never edit one.
**Prompt text and closed-vocabulary members are ratified by the owner alone, and an
unratified text never crosses the internet.** Never `git add -A`. The `.groundtruth/`
corpus and `labels.json` are the owner's personal data: never committed, copied or
printed — no filename, folder name or course code in any message or document,
aggregates and masked shapes only. Only the lead runs scans, replays or
`tools.groundtruth`. Commits end with the Co-Authored-By and Claude-Session lines.

**`00` amendment 24 is the one that changes how you ask questions.** The owner:
*"the questions you ask me — these are arbitrary right, it depends on the user."*
They are right. Separate **preferences** (which level comes first, whether
Education holds research, what a life is called) from **truths** (that `year` and
`tax_year` are different ideas, that a derivation cannot outrank its source, that
medical records reach no model). Only the second kind is the library's to settle.
`107` promises *"every split can be changed before freeze"* and **that control does
not exist** — most of the questions put to the owner on 18 Sep should have been a
setting.

**What actually worked this session.** Every real defect was found by an agent
READING the code, not by a test. Briefs that said *"report the diagnosis even if it
contradicts this brief"* caught five lead errors. The suite was green while a P11
guard was silently inert, while `106` Phase 2(a) was dead code, and while a
`cli.py` that did not parse was committed. **Parse-check every file you edit.**

**What failed.** Two agents stalled after long runs with uncommitted work; both
were rescued by the lead making a WIP commit on their branch. Worktrees are
provisioned from a stale commit (`4a9f7469`) — every agent hit it; reset your own
branch to `build/p6-p7-first-packages` and confirm `planning/107-...md` exists
before reading anything.

---

## 8. The target

`planning/107-IDEAL-TREE-REFERENCE.md` and `107-ideal-tree.txt` are **the owner's
own words**, stored 18 Sep after an analyst found only four second-hand fragments
of it in this repository. Eleven lines arrived truncated and are marked
`[TRUNCATED]` — **do not reconstruct them**; ask the owner.

`tools/groundtruth/ideal_tree.py` grades a run against it — exact path, prefix from
root, per-level reach. **Key convention:** a BLANK level means "nobody has said
yet" and is owed; `""` means "no value applies" and the file rests at the parent.

---

## 9. Waiting on the owner

- **The coursework sheet**, `~/.graph-agent/lead/corpus2-gate1/review/18_coursework_key/` — 79 rows. `Course` blank on 52, `Kind of work` on 60, both REQUIRED. `My school` is answered once per group and unblocks amendment 19's 36 files.
- **Site D ratification** — `review/16_site_d_to_ratify/`: "ratify ladder", "ratify shelves", or "not yet".
- **Three situation names** for Health and Travel (§3), one of which is cloud-bound.
- **`work_type`'s glossary meaning** (§6.3).
- **The EXIF year question** — `[12]\d{3}` admits 1970/1980/2000, the defaults an unset camera clock writes.
- **111 → 25 over-protected files.** 25 files the key calls ordinary are held protected (70 of the earlier "111" were ROWS). Narrowing the gate sends more off-device and is gated by a classifier: **escalate to the owner, never reformulate to pass.**

---

## 10. One competitor fact worth keeping

`thedrive.ai` attempted this problem and retreated from it in writing
(`104` §18.115). Their Sept 2026 blog: *"a workflow files into folders that already
exist rather than inventing a tree… no tool can decide that for you."* Their
`/decide` endpoint is this product's constitution built independently. And their
own post-mortem is a warning aimed at the approve-the-tree step:

> *"Approvals cleared in under three seconds each… a control that has never said no
> is not a control."*

**Nothing in this repository measures whether an approval was considered.**
