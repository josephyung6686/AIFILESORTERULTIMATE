# 94 — Does the built flow match the designed flow?

Date: **2026-09-02**, `build/p6-p7-first-packages`. Every run below was made
against a copy of `src/` taken at **`2bb737a`** (`84` §2b: the shared working tree
is not a fixture). Every `file:line` was re-verified against **`4ac6231`**, the
head when this was committed — `src/cli.py` grew 3,920 → 3,983 lines during the
audit from work unrelated to these findings (wire-handle keying, a tree-limits
refactor), and each mechanism named below was confirmed still present at the new
offset. Ten agents were landing work while this was written, several of them on
the seams named here — read every finding as *as of `4ac6231`*.

North star: `planning/01-product-design-structured.md`, disambiguated by `00`.
Amendments read before writing: `80`, `88`, `91`, `93`, and `84` §1/§3/§5/§6.

---

## 0. What was verified, and what was not

**Verified by running the product**, five corpora of 1–5 files each, through
`cli.main` with a copied `src/`:

- a plain run (no model, no consent) — F2, F4, F6, F8, F11;
- the same run with `--enable-cloud` and a complete fake `DEEPSEEK_*` routing — F2, F3;
- `--freeze` alone, and `--freeze` after `--residual` + `--send-set` — F1, F16, F19;
- the same corpus with the one protected file deleted — **F1's causality, both directions**;
- the same corpus with `--declare-role me=academic` added, to test whether the
  role gesture would change any of it — **it changes nothing**, which corrected
  F5 after it was first written;
- a corpus containing a `.app` bundle — F17.

Every claim about a screen below is a line this session actually printed. Every
claim about a database row is a row read back out of the run's own SQLite.

**Verified by reading, not by running:** the classification of F7, F9, F10,
F12, F13, F14, F15. `tests/integration/test_composition_root.py -rx` was run and
its three xfail messages are quoted where they apply; the module reachability
figure (60 of 307 dead to a run) is a re-run of the lead's own `ast` script.

**NOT verified, and worth someone's time:**

1. **`--apply` and `--undo` over a real move were not run.** `91` §5 measured them
   and they work; this audit reached them only through the freeze that feeds
   them, and F1 means the shipped pipeline could not put a plan in front of them
   on four of the five corpora tried.
2. **No corpus that produces a tied reading was constructed**, so the P15 question
   block and the role-declaration moment (F5) were never seen firing. F5 rests on
   a negative result plus one control run, not on watching the moment work.
3. **Nothing at scale.** The largest corpus here is five files. `93` and `84` §2b
   both record findings that only became visible at 1,000 and 5,000; this audit
   would not have found them.
4. **Extraction (§2) and OCR (§2.7) were exercised only over `.txt`.** Whether a
   PDF, a DOCX, an image or an archive travels the designed path is untested here.
5. **The suite was not run**, on purpose — `84` §2 says re-measure rather than
   quote, and this audit's findings are about composition, which the suite does
   not test (`84` §5).

---

## 1. The design's flow, as an ordered list of stages

Each stage: what the person does · what the system does · what they are shown ·
what may leave the device · what must be refused.

| # | stage | design |
|---|---|---|
| **S1** | **Choose the corpus and the roots** | The person picks which folders are scanned, which high-level locations may be roots, and **whether files may move across high-level folders**. Roots are context, not permission. Excluded directories are named before scanning. §1.1 |
| **S2** | **One reusable local extraction pass** | Path, name, extension, MIME, size, timestamps, hash, scan state; stat cache. Nothing decides meaning. §1.2, §2.1–§2.9 |
| **S3** | **Facts from evidence** | Rules first, then a model only where rules end, with the location of every observation preserved; a fact carries its provenance and its reliability state. The model must return `unknown` rather than guess. §3.1–§3.14 |
| **S4** | **Grouping** | Rules find anchors → the graph assembles a bounded neighbourhood → **the LLM answers four constrained questions with citations and may abstain** → a deterministic validator checks every citation → **the user makes the final decision**. §4.1–§4.10 |
| **S5** | **The person reviews the group suggestions** | §5's opening sentence: the tree stage begins *"after the user has reviewed the evidence-backed group suggestions"*. §4.10 step 5. |
| **S6** | **Horizontal pass** | A small set of candidate top-level branches, each a card with a file count, representative groups, existing related folders and a plain explanation. The person accepts, renames, merges, moves under an existing root, defers, or creates one. Sensitive groups appear differently. §5.1, §5.2 |
| **S7** | **Vertical pass, branch by branch** | Per accepted branch, the product offers the nesting options its facts support (§5.5's Option A/B/C), **with the branch counts shown before committing**, and live structural feedback warning about one-child levels, excess depth and folder swarms. Uneven depth is expected. §5.3–§5.9 |
| **S8** | **Existing folders throughout** | Visible at every step; six gestures over them (attach beneath, merge into, rename to match, adopt, preserve, leave out). Never silently reorganised. §5.10 |
| **S9** | **Tree health** | How much of each group the structure represents; where sensitive material was isolated; which branches still need a decision. §5.11 |
| **S10** | **Freeze** | The person freezes. Freeze records the approved hierarchy and closes the destination set. §5.12 |
| **S11** | **Destination profiles and retrieval** | Every frozen node becomes an evidence-backed profile; an unplaced file retrieves a few legal candidates; conflicting evidence suppresses nodes. §6.1–§6.3 |
| **S12** | **Node-local classification, then the model as hierarchical judge** | Deterministic where the match is unique; the model only for bounded ambiguity, from a placement dossier, choosing child / parent / scoped fallback / nothing, **never filling a missing slot for a tidier path**. §6.4–§6.9 |
| **S13** | **Two-condition validation** | Threshold **and** margin. Correct abstention is a success. Each decision records its evidence type and its required review policy so the person can tell a direct placement from a context-supported one. §6.10, §6.11 |
| **S14** | **Residual surfacing screen** | *"Your main structure is ready. We found 146 files that do not fit."* Divided into understandable review sets — screenshots, standalone PDFs, receipts, protected records, unreadable, multi-home, no-evidence — each with examples, type distribution, age range, sensitivity and **the reason it could not be placed**. §7.5 |
| **S15** | **Set-level decision before file-level AI** | The person answers per set: leave in place / review with AI against approved residual areas / send to an inbox / create a branch. §7.6 |
| **S16** | **LLM residual review, inside the approved library** | A controlled action set; may not invent a folder; must cite; may conclude nothing. §7.7–§7.9 |
| **S17** | **Review and learning** | Editable recommendations, bulk decisions, **negative feedback stored with the evidence that produced it**. §7.10, §8.7 |
| **S18** | **Mutation** | Plan with the complete precondition → staleness recheck → one action or a bounded batch → verify → journal → conditional undo. Never a silent overwrite. §8.3 |
| **S19** | **Privacy across all of it** | Nine `ALWAYS_LOCAL` kinds. Protected material: not in cloud prompts, not shown raw in group summaries, not moved automatically without a policy. Four operation modes. A consent-aware audit record per model call. §8.4 |
| **S20** | **Versioned plans and diffs** | Every edit makes a draft version and **shows a meaningful diff**; a new plan never silently reclassifies. §8.8 |
| **S21** | **Budgets and legible deferral** | Ceilings; predictable degradation; *"89 scanned PDFs deferred after the OCR limit"*. Cost exhaustion must never become lower-quality automatic classification. §8.6 |
| **S22** | **Replay and evaluation** | Stage-decomposed replay, an adversarial suite, shadow mode. §8.5 |

Two amendments change the shape of this list and are treated as design:

- **`91`** splits S10 in two: `--freeze` records the approval **and** is P13's review
  surface; `--apply` (one branch, several, or everything) and `--undo` move files.
- **`80`** adds a stage the design predates: at the **first genuinely ambiguous
  file**, and never at first run, the person may describe their material in their
  own words and pick a layout. The friction budget is spent once (R2).
- **`93`** amends S19's screen: protected filenames are summarised by default and
  `--show-protected` expands them completely.

---

## 2. The built flow

`src/cli.py:main` → `run()` → `production.run_production_corpus` →
`orchestrator.run_p1_p7` → `production.run_production_p8_p11` → `report()` →
optionally `apply_run.freeze` → (later invocation) `_move_frozen_files`.

| # | built | where |
|---|---|---|
| B1 | The person types a folder, one `--situation`, one `--label`. Sources = `[directory]`, **candidate roots = `[]`, cross-folder moves = `False`**, all three literals. | `cli.py:1746` |
| B2 | P3 scan → P5 extract → P4 record → P1 status → P2 bundle → P6 facts → P7 classify. Protected containers marked, never opened, printed the moment they are known. | `orchestrator.py:517`, `cli.py:2181` |
| B3 | P6 runs `direct` and `rule` stages. **`llm` is `None` and `model_route_permitted` is `False`.** | `cli.py:1155-1158` |
| B4 | P9 groups on shared validated facts. **`p8_run_call=None`** — no model, no dossier, no four questions. Embeddings off. | `cli.py:2220`, `2203-2209` |
| B5 | **Every grouping result is accepted, as one group, named `--label`, `decided_by=RULES`.** No screen, no per-group decision. | `cli.py:1297` |
| B6 | P10 designs the tree by rule: one top-level branch from `--label`, the person's own folders adopted as `existing` nodes under their real parents, nesting = the first option that passes and splits. | `cli.py:1421`, `1849` |
| B7 | The nesting choice is **recorded as a question and printed after the tree was already built**; an answer applies on the *next* run. | `cli.py:1486`, report §"You can change how this is organised" |
| B8 | Freeze of the *tree* happens internally on every run. `validate_for_freeze`'s unanswered questions are answered in `DEFAULTED_DECISIONS` and printed. | `cli.py:2629`, `production.py:654` (`_bootstrap` at `cli.py:1544`) |
| B9 | P11 places against the frozen tree, deterministically. **`gate`, `model_client`, `prompt`, `call_dependencies`, `model_call_request`, `chosen_node_of`, `residual_action_of`, `sensitivity_policy`, `p2` are all `None`.** | `cli.py:2165-2178` |
| B10 | §7.5's sets are **two**: "Not yet placed" and "Protected, and not filed in bulk", split by protection and nothing else (`cli.py:2098` says so, and says why). | `cli.py:2098` |
| B11 | §7.6 is `--send-set SET=AREA`, zero model calls, applying only to the run it is typed in. §7.4's residual library is opt-in via `--residual`, **physical destination only**. | `cli.py:2249`, `1913` |
| B12 | The report: protected containers, the tree, one block per *kind* of outcome with names and reasons, open questions, the role panel, the decisions taken on the person's behalf, `Nothing was moved.` | `cli.py:2902` |
| B13 | `--freeze` writes `00`:156-170's plans **and** P13's `review_approval` over exactly the file ids the report named. `--apply BRANCH` / `--apply-everything` / `--undo` / `--undo-everything` read the plan back on a later invocation. | `cli.py:3926`, `3383` |
| B14 | Corrections: `--reject` retracts a fact and it stays retracted; `--answer` settles a blocked reading; `--describe-role` / `--declare-role` record a role. | `cli.py:2306`, `2381`, `3797` |

---

## 3. Findings

Ordered by what a person experiences, worst first.

---

### F1 — One protected file in the folder makes **every** file in it unmovable, and tells the person their coursework is protected · **DIVERGENT (defect)**

**What a person experiences.** A student scans a folder holding a syllabus, a
lecture, a reading list, a homework PDF and one passport scan. They do the
sanctioned thing — enable a residual area, file the review set, freeze. They get:

```
Nothing was frozen: no placement in this run is ready to move.

Not frozen, and still exactly where they are -- 4 file(s):
    PHYS 1401 syllabus.txt
    Uni/PHYS 1401 lecture 08.txt
    reading list.txt
      Each of these is no plan could be made for it.
      protected_without_policy
```

Delete the passport from the folder and re-run the identical command:

```
Frozen: 3 file(s) are ready to move, in 1 branch(es).
  Coursework/Review Later -- 3 file(s)
    Move these:  database-agent … --apply 'Coursework/Review Later'
```

**Causality proven in both directions**, same corpus, same command, one file
added and removed.

**Mechanism.** `cli.py:1817`'s `collapse_handling_classes` gives a branch the
**strongest** handling class among its members, so the single top-level branch
that `--label` creates inherits the passport's. Read back out of the run's own
database:

```
{'display_label': 'Coursework', 'node_type': 'proposed', 'handling_class': 'sensitive_personal'}
{'display_label': 'Review Later', 'parent_node_id': <Coursework>,  'handling_class': 'personal_non_sensitive'}
```

`mutation/resolution.py:166` `_refuse_protected_label` then refuses to compose a
path through any protected ancestor — correctly, on its own terms (`69` §3
blocker 3: a passport number must never become a folder name) — and every
descendant of `Coursework` is such a path. `apply_run/freeze.py:231` records the
refusal class as the hold detail, and `apply_run/report.py:152` prints it raw.

**Why it is a divergence and not the guard working.** §5.2 says a sensitive group
*"may be visible as a protected area"*; §5.11 says the tree health view shows
*"where sensitive material has been isolated"*. Isolation is per-file and P10 does
it — `materialise_branch` already keeps the passport out of the level. What
happened here is the opposite: the protection travelled **up** to a branch that
holds ordinary coursework, and then **down** to every sibling. `84` §1's rule is
that protected material is *marked and counted, never opened*. Nothing here opened
it; what it did was stop four unrelated files and blame them.

**The root cause is that two parts read one field to mean two different things,
and the fix belongs on P12's side, not P10's.**

1. **`Node.handling_class` carries two meanings.** P10 writes it as *the floor for
   what may be filed here* — `cli.py:1817`'s own comment says the collapse to the
   strongest class is what "keep[s] a sensitive file from landing somewhere
   weaker", which is §5.2's privacy ordering and a P10 invariant. P12's
   `_refuse_protected_label` reads the same field as *this label was composed from
   protected material*, which its docstring is explicit about: `69` §3 blocker 3,
   a client's passport number reaching a folder name. **`Coursework` is not
   composed from anything protected. Its floor is high because one member is.**
   Removing the collapse would let a passport be filed into a branch with a weaker
   floor — that is the wrong repair. The right one is on P12: check the
   provenance of the label, or read a field that means provenance, rather than
   reading the floor.
2. **`protected_without_policy` is `mutation`'s only refusal class for this**, and
   it is the wrong word for *"a folder above this one has a strong floor"*.
3. **The class is printed to the person verbatim**, under an ungrammatical
   sentence.

`91` §7 already flags (2) from the apply side. This is the freeze side, and it is
worse: on the apply side the sentence is misleading; here the product refuses.

**This does not contradict `91` §5's successful measurement.** That corpus is
listed there — three PHYS files and a reading list, no protected member — and its
"protected" refusal was the unclassified homework file hitting `91` §7's collapse.
A branch with no `sensitive_personal` member keeps an ordinary floor and freezes,
which is exactly what the control run here did.

**Scope.** This fires whenever the corpus contains anything `SAFETY_DOMAIN_HANDLING`
marks finance, identity, medical or legal. That is the north star's own person.

---

### F2 — The screen says files "may be sent" to three named cloud models. No call site exists. · **DIVERGENT**

**What a person experiences.** With a key in `.env` and `--enable-cloud` typed,
this is the first thing on the screen, before the scan:

```
Cloud sending is ON for this folder.
  Turned on by jy on 2026-09-02T15:04:01…, for:
    …/corpus
  Files that need a judgement may be sent to deepseek-reasoner (facts),
  deepseek-chat (checks) and deepseek-chat (review sets). …
```

Nothing in a run can send anything. The person has spent `80` R2's once-only
friction budget on a capability that cannot fire, and received nothing for it.

**Three layers, and only the third is a screen problem:**

1. **Nothing is connected.** `cli.py:3773` builds `routing` and passes it into
   nothing. P6's model stage is `None` (`cli.py:1155`), P9's is `None`
   (`cli.py:2220`), and P11's seven model injections are all `None`
   (`cli.py:2165-2178`). `84` §2b records the model as having "become reachable";
   what became reachable is the **routing construction and its announcement**, not
   a call.
2. **Even wired, it cannot fire.** `llm_harness/records.py:89` refuses an empty
   `template_bytes` — *"there is no default prompt"* — and prompt text is
   outstanding owner business (`84` §3 item 3, draft at `82`). This is correct and
   is the thing preventing harm.
3. **The sentence does not check either.** `announce_cloud_posture`
   (`cli.py:519`) branches on `routing is None` and on consent, and on nothing
   else. It will keep saying "may be sent" through the whole of (1) and (2).
   **Layer 3 survives the wiring work and should be fixed independently of it.**

The design's requirement is §8.4's: *"a run that sends says so on screen before it
does"*. `88` §3 and `80` §8 restate it. A run that says so and does not send is a
different failure than the one those rules were written against, but the person
cannot tell which they are looking at.

---

### F3 — Turning cloud sending **on** makes the report tell the person **less** · **DIVERGENT**

**What a person experiences**, same corpus, same three files, only the consent
differing:

| consent | what the file's line says |
|---|---|
| off (default) | *"Deciding this file needed a model, and §8.4 did not clear this file for a model call. Nothing about it left this device…"* |
| on | *"No legal destination cleared §6.10's conditions (low_margin). Abstaining is the correct outcome…"* |

The second sentence reads as *a model looked and could not decide*. What happened
is that no model exists. The one fact the person needs in order to act — that a
judgement was required and none was available — is present only while consent is
off.

**Mechanism.** `placement/pipeline.py:505`: `needs_model_call` is true;
`may_assemble_dossier` now passes because the mode permits; `model_path_available()`
is false; and the branch **falls through to step 9** with no reason of its own.
`_abstention_explanation` (`pipeline.py:665`) has a sentence for
`privacy_blocked` and none for *"the model path was not supplied"*, so the
generic evidence-failure sentence is used.

§8.6 states the rule this breaks in the neighbouring case: a ceiling-truncated
run must render differently from *"I looked and could not tell"*, because
otherwise the person gets *"the false impression that an unprocessed file was
understood and found unimportant"*. A missing model path is the same shape and has
no such reason code.

The placement half becomes moot the day F2's layer 1 is wired. The **missing
reason code** does not: an operator whose key expires wants this sentence.

---

### F4 — Files are headed "Waiting for you to say what these are", and the report prints no command that says it · **DIVERGENT**

**What a person experiences.** On the plain run, four of five files are under
that heading. Under them the report offers exactly one command:
`--residual "Review Later"`, then `--send-set`. Filing something into Review
Later is not saying what it is.

`84` §6's second standing rule is that *what the screen tells a person to type
has to be true*. This is the same rule from the other side: the screen tells the
person to **do** something and prints nothing that does it. The gestures that
would — `--answer` for a blocked reading, `--declare-role` for what the material
is — are not offered here. F5 is why: the module that decides when to offer the
role gesture has already concluded that nothing is waiting for the person on
exactly these files.

`OUTCOME_WORDS[ABSTAIN]` is `cli.py:2595`. §6.10's *"correct abstention is a
successful outcome"* is honoured in the record; what the person is handed is a
verb with no gesture.

---

### F5 — Two modules disagree about whether an abstention is the person's to act on · **DIVERGENT**

**This is F4's other half, and it is a contradiction inside the product rather
than a gap against the design.** The same file is described two ways by two
modules on the same run:

| module | what it says about a `needed a model` abstention |
|---|---|
| `cli.py:2595` `OUTCOME_WORDS[ABSTAIN]` | **"Waiting for you to say what these are"** — the person's move |
| `questions/triggers.py:296` `role_declaration_is_due` | not an ambiguity at all; its docstring records that firing the role moment on exactly this case *"told the person that the decisions above were waiting for them, when nothing was"* |

One of those two sentences is wrong and they are on the same screen.

**What was measured.** Five files, every one of them abstaining, three of them
literally *"needed a model"* — and no `--describe-role` or `--declare-role` line
was printed on any run in this audit. `role_declaration_is_due` operationalises
`80` R1's *"precisely when it hits its first genuinely ambiguous file"* as
*"at least one open non-branch P15 question"*, and P15 questions come from
`tied_readings` — a file whose evidence supports two readings of one field. An
abstention raises none.

**And the trigger's author is right on the facts.** Re-running the same corpus
with `--declare-role me=academic` added produces a **byte-identical** outcome
block: same three groups, same reasons, same zero ready to file. A declared role
feeds `activated_schemas` into the detector's `settled_by_user` (`cli.py:1758`),
which settles *tied readings* — the very files that already trigger the moment.
It does nothing for a file blocked on the model path. So the earlier reading of
this finding — that the litigant, householder and parent of `84` §2b are denied
the gesture that would rescue them — is **wrong, and the measurement says so**.

**What is actually owed.** Not a wider trigger. A screen that stops telling
somebody to act when the product has already concluded there is nothing for them
to do, or a gesture that makes the sentence true. Whichever way it is resolved,
`OUTCOME_WORDS[ABSTAIN]` and `triggers.py`'s docstring must end up agreeing.

---

### F6 — The person is never shown a group · **MISSING**

**What a person experiences.** The report prints folders and it prints files. It
never prints *"these seven files look like one course and here is why"*. §5's
opening sentence assumes that screen has already happened.

`cli.py:1297` `review_and_accept` collapses **every** grouping result into one
group, named `--label`, `decided_by=RULES`. Its docstring is honest about being
"the review screen, non-interactively". The consequence is that §4.10 step 5
(*"the user makes the final high-leverage decision"*), §4.3's reviewable candidate
membership record, §4.5's four constrained questions and §4.9's *"the user has
already rejected an equivalent proposal"* stop rule have no surface.

Combined with F7 this is the architectural cause of `84` §2b's *"74 files produced
5 ready to file"*: a command that takes **one** situation for **one** corpus and
makes **one** group cannot serve the person who is several roles at once, which is
the north star's whole definition of the user. `DEFAULTED_DECISIONS`' last entry
says so out loud — *"applied to EVERY file in the folder — including any that are
something else entirely"* — which is the right disclosure of the wrong behaviour.

---

### F7 — One `--situation` for the whole corpus; the question that would fix it is built at both ends and called at neither · **DISCONNECTED (already tracked)**

`tests/integration/test_composition_root.py::test_the_question_that_asks_which_situation_a_branch_is_reaches_a_person`, xfail, its own words:

> `75` B1/B2: §13's third consequence is built at both ends and called at neither.
> `question_for_situation` is asked by nothing and `selected_situation` is read by
> nothing, so `--situation` stays one string for a whole corpus — `68` F6's defect.

Reported as context, not as a new finding. It is F6's other half and the two
should be routed together.

---

### F8 — §5's canvas does not exist; the one question it does ask arrives after the answer was taken and applies next run · **DIVERGENT, disclosed**

The design calls §5 *"the most important user-facing stage"* and gives it a
horizontal pass (S6), a vertical pass (S7), live structural feedback (§5.9) and a
tree health view (§5.11). What is built:

- **S6 horizontal pass — MISSING.** There is one top-level branch and its name is
  `--label`. No cards, no counts, no accept/rename/merge/defer.
- **S7 vertical pass — partial and inverted.** `nesting_chooser` (`cli.py:1486`)
  does the honest thing: it records a real question carrying §5.5's per-option
  child counts and warnings, including the options its own validator rejected.
  But it is asked **after** the tree was built with `choose_option`'s default, and
  an answer takes effect on the **next** invocation. The report says so plainly
  (*"it is already decided; this is yours to overrule"*), which is the right
  disclosure; it is still not §5.5's *"the user sees the actual branch counts
  before committing"*.
- **§5.9 live feedback — the warnings exist and reach the person only inside that
  one question.** `tree_design.health` is reachable; the "one child", "excessive
  depth", "many tiny folders" advisories have no screen of their own.
- **§5.11 tree health — MISSING.** No view.

`DEFAULTED_DECISIONS` (`cli.py:2629`) discloses seven of these on every run and is
the single best thing in the report. It is disclosure, not the stage.

---

### F9 — The six gestures over a person's own folders have no consumer; renaming has no writer · **MISSING / DISCONNECTED (tracked)**

§5.10 gives the person six things to do with an existing folder (attach a branch
beneath it, merge a proposal into it, rename the proposal to match it, adopt it,
preserve it, leave it out). `DEFAULTED_DECISIONS`' first entry says none of the
six has a consumer and that the command takes the only defensible one — keep every
folder exactly where it is.

`test_the_renaming_overlay_has_a_writer_somewhere_in_the_product`, xfail:

> P13's review surface is unbuilt; nothing calls `record_user_level_edit`, so a
> person cannot rename a level.

The adoption half works and is verified: `Uni` appeared as `[yours already]` with
its real path, nested under its own parent, and the report counts yours separately
from proposed — §5.10's *"make the difference visually clear"*, carried in words
because a terminal has no two styles.

---

### F10 — Every run mints a new plan version and nothing ever shows a diff · **MISSING**

**What a person experiences.** They answer the nesting question, re-run, and the
report is a fresh proposal under a name they have never seen. §8.8 requires a
draft version and *"a meaningful diff"* — *"Applications was renamed to Admissions
… twenty-three files now require renewed review"*. There is none, and the person
has to compare two screens of prose by eye to find out what their answer did.

`run_token` (`cli.py:1785`) mints a fresh `plan_version_id` per run — for a good
reason, recorded there. `tree_design.diff` is dead to a run (module reachability
below). `91` §3.1 already fights this from the apply side and works around it by
comparing **plans**, which name paths and hashes; the person still has nothing.

---

### F11 — The permanent record says the person chose things they were never asked · **DIVERGENT**

`refinement_for` (`cli.py:1523`) writes `shallow-by-choice` on every non-root node
with the reason *"This branch holds few enough files that splitting it further
would not help you find anything"* — a sentence in the person's voice about a
judgement nobody made. `approve_plan` (`cli.py:1972`) writes
`user_edited_label=label`. `set_privacy_policy` records the mode as the reason.

The screen is honest: `DEFAULTED_DECISIONS`' third entry says *"Nobody was asked
whether a branch is short on purpose or just unfinished"*, and
`surface=SURFACE_UNATTENDED` (`cli.py:1963`) keeps §8.2's log from claiming a
canvas that does not exist. **But P13 will read the record, not the report.**
§8.2's rule is that the system must be able to reconstruct *what the user
approved*; a `shallow-by-choice` with a first-person reason is a claim the log
cannot distinguish from a real one. The `surface` field fixed the *where*; the
*who* is still overclaimed at the value.

---

### F12 — No budget can ever be exhausted, so §8.6's legible deferral is unreachable · **DISCONNECTED**

`scan_budget_exhausted=lambda: False` (`cli.py:1273`), `budget_exhausted=lambda
ceiling: False` (`cli.py:1157`), `extractors.budgets` dead to a run. §8.6's whole
point — *"1,842 files indexed; 1,611 fully extracted; 89 scanned PDFs deferred
after the OCR limit"* — cannot be printed, because nothing defers. `_abstention`
enforces the `budget_deferred` ↔ `deferred_stage` pairing correctly
(`placement/pipeline.py:752`); nothing reaches it.

Harmless at five files. At a real disk the first person to hit an OCR ceiling gets
no deferral, because there is no ceiling.

---

### F13 — §7.5's surfacing screen is two sets, and §7.6's three answers are one · **DIVERGENT, disclosed**

§7.5 divides residual files into understandable sets — *58 screenshots · 21
standalone PDFs · 17 receipts · 11 protected records · 9 unreadable · 16
multi-home · 20 with no evidence* — each with examples, a type distribution, an
age range and a reason. Built (`cli.py:2098`): **two** sets, split on protection
and nothing else, with `file_type_distribution=()` and `age_range=()`.

The docstring's reasoning is sound and should not be undone casually: declaring
every set unprotected made P11's `require_set_actionable` refusal unreachable, and
*"`--send-set` would have filed a passport in one gesture"*. It is explicitly not
a taxonomy and does not pre-empt SPEC Open question 10.

§7.4 gives a residual template three dispositions — physical destination,
review-only, leave-in-place. `--residual` can express one (`cli.py:1913` says so).
So *"leave all my screenshots exactly where they are"*, which §7.4 opens with as
the archetypal answer, cannot be said.

**Verified working:** the protected set is named, counted, reasoned, and offered
**no** `--send-set` line, because P11 would refuse it — `84` §6's third rule, held.

---

### F14 — §8.5's replay, adversarial suite and shadow mode reach no run · **DISCONNECTED (already claimed)**

`evaluation=None` (`cli.py:2226`) with a reason: a person's own folder has no
hand-labelled expectations. `eval_harness.adversarial`, `scan_agent.replay`,
`evaluation` and `llm_harness.stage_output` are dead to a run. Reported as
context per the brief; `wire-p2-replay` has it.

---

### F15 — Every test of the model half builds a world `cli.py` cannot build · **applying CR-06's lens**

The brief asks: when a test certifies a stage, does its fixture describe a world
that can exist? For the model path, no.

- **50 lines in `tests/` pass a non-`None` `gate=`** to a `PipelineInputs`.
  `src/` passes one in **zero** places — `cli.py:2165` is `gate=None`.
- **8 test sites pass a non-`None` `p8_run_call`.** `cli.py:2220` is `None`.
- `tests/integration/test_live_path.py:472` builds
  `ModelClient(model_target=CLOUD, invoke=recorder)` and hand-assembles the whole
  `PipelineInputs`. It does not import `cli`.
- The only tests that touch the real provider modules
  (`tests/test_cli_model_route.py`, `tests/readers/test_model_deepseek.py`,
  `tests/integration/test_single_egress.py`) test **routing construction and
  egress refusal**, not a call from a run.

So §3.3, §4.5, §6.6 and §7.7 — the model's four jobs, which are most of the
design's intelligence — are green in the suite and unreachable from the product.
This is `84` §5's dominant defect class, and CR-06's specific lesson is that a
suite in this state does not notice when a call site is wrong, because no call
site exists to be wrong. It is stated here as scope, not as blame: `84` §2b names
it and it is being worked.

**Module reachability, re-measured at `2bb737a`:** 307 modules in `src/`, 247
reachable from `cli`, **60 dead to a run**. 21 are `review_surface` (claimed).
The rest include `tree_design.diff` (F10), `tree_design.template_schema` (§5.7's
LLM-generated custom templates — no path to one), `extractors.budgets` (F12),
`privacy.transport_guard`, `placement.review`, `placement.versions`,
`mutation.retention`, `facts.rules`, `facts.plan_versions`, `grouping.failure_points`
(§4.8's *"log and evaluate these failure points separately"*), and the
`stage_output` emitter of six parts.

---

### F16 — The freeze block's own accounting drops the protected file · **DIVERGENT**

Five files in the corpus. The freeze block says *"Not frozen, and still exactly
where they are — 4 file(s)"* and lists four. The passport is not among them.

`apply_run/freeze.py:208`: a decision whose outcome is not `place` produces
neither a plan nor a hold, and the docstring defends this well — recording a
correct abstention as "withheld" would tell a person files were kept back when
they were decided. That reasoning is right for an ordinary abstention. It is not
right for protected material, where `84` §1's rule is **never silently omitted**
and `93` §4 is explicit that the count must be on the screen in both views.

The report body above does count it (`1 protected file, marked and counted`), so
the omission is local to the freeze block rather than total. But the freeze block
is the screen a person reads when they are asking *"what happened to my files"*,
and its total is wrong by one in exactly the category the standing rule protects.

The corresponding branch **is** handled correctly when a protected file reaches a
`place` decision: `apply_run/report.py:149` prints *"N protected file(s), counted
here and not named"* with the reason and no command, which is `93` applied
faithfully.

---

### F17 — Protected containers: correct along the whole flow · **CONFORMS** (verified)

Measured with a `Numbers.app` bundle in the corpus:

```
Protected containers: 1 marked, none opened
  Numbers.app  (untouched_protected)
    …/corpus/Numbers.app
  Nothing inside these was read, indexed, classified or moved, and none of them
  is a place anything can be filed.
…
  Numbers.app   [marked, not a destination]
```

Named, counted, path shown, present in the tree as a node that accepts no
placement, and — per `cli.py:1849`'s `adopted_folders` — deliberately **not**
adopted a second time as an `existing` node, which would have minted a legal
destination inside a sealed bundle. Printed from inside `downstream()`
(`cli.py:2181`) rather than from `report`, so a run that later refuses by name
still says what it set aside. Four rules held at four different points; this is
the best-composed thing in the flow.

---

### F18 — Nothing can leave the device, and the guard that would stop it is unreachable · **context**

The nine `ALWAYS_LOCAL` kinds are trivially safe in the built flow, because there
is no egress path at all (F2, F15). `privacy.transport_guard` is dead to a run.
That is the correct posture for today and it means **this audit could not test the
egress boundary**: whoever wires the model must not read F18 as evidence the gate
works end to end. `92`'s four Criticals are the record of what happens when it is
tested, and CR-06 is the record of what a test can miss.

---

### F19 — Small screen defects, all in lines a person reads · **DIVERGENT (minor)**

1. `apply_run/report.py:39` `_HOLD_SENTENCES` — *"Each of these is no plan could be made for it."*
   and *"This one is nothing has looked inside it yet"*: `_HOLD_SENTENCES` are
   written to follow *"is"* and two of them are full clauses.
2. Same block prints the raw refusal token `protected_without_policy` on its own
   line, verbatim, to a person. (F1.)
3. `cli.py`'s nesting question: *"3 files sit under Coursework"* / *"1 file sit
   under Coursework"* — the verb does not agree.
4. Option `school>term>subject>work_type` is summarised as *"would create 1 term,
   and 1 subject"*: the first level of the chain is absent from the counts the
   person is choosing on. §5.5 makes those counts the whole basis of the choice.

---

## 4. What this adds up to

The flow's **skeleton** is right and its **disclosure discipline** is unusually
good: protected containers are handled correctly at four independent points (F17),
`DEFAULTED_DECISIONS` names seven decisions taken on the person's behalf in the
words of the question, and every refusal this audit provoked was a sentence rather
than a traceback.

What is missing is the middle of the design — the part where **the person is in
the loop**. S5 (review the groups), S6 (choose the branches), S9 (tree health) have
no screen; S7 has a question that arrives after the answer; S15's three answers are
one. And the part where **the model reasons** — S3's llm stage, S4's four
questions, S12's hierarchical judge, S16's residual review — is built, tested, and
reachable from nothing a person can type.

Between them they explain the measurement the lead already has: the run ends with
zero files ready to file because the two stages that would decide a file (a model,
or a person at a screen) are both absent, and the one gesture that reaches the disk
is blocked by F1 for any corpus that contains a passport.

**On the standing rule "absent means refuse, never guess": nothing guesses in a
way that changes a file's fate.** Every absence this audit provoked produced a
refusal or an abstention with a reason attached — `model_route` returns `None` and
says so, `_resolver` treats a missing stage as non-existent rather than empty,
`FactResolver` leaves an unreached fact unresolved rather than absent,
`ask_or_abstain` abstains where §6.9 would have it choose an institution, and
`shared_material` keeps the multi-home decision with the person. The one place a
default is written down as though somebody chose it is **F11**, and it changes a
record rather than a file. The two places a person is told something untrue are
**F2** (a capability that cannot fire) and **F1/F19.2** (a wrong reason for a real
refusal); neither is a guess about their material.

**Routing suggestion.** F1 is one fix on P12's side of a two-part field-meaning
conflation, and with F19.1–2 it unblocks the product's only mutation gesture. F2
layer 3 and F3's missing reason code are independent of the model-wiring work and
should not wait for it. F5 is a one-line contradiction between two modules that
somebody has to adjudicate rather than patch. F16 is one branch. F6/F7 and F8 are
the design's real remaining surface and are somebody's phase, not somebody's patch.

---

## F20 — a folder about ONE thing gets nothing filed, and adding an unrelated file fixes it

Added 2026-09-03 by the lead, measured rather than read. Same command, same situation, same
label, a fresh `database-agent-plan.sqlite` before each run. Only the corpus changes:

```
ONE subject, 3 PHYS 1401 files       ->  Nothing was frozen.
ONE subject + an unrelated passport  ->  Frozen: 3 file(s), Coursework/PHYS1401
TWO subjects (PHYS + BUSIB)          ->  Frozen: 3 file(s)
```

**Adding a passport scan to a folder makes three coursework files placeable.** The passport is
not the mechanism: rows two and three reach the same result by different routes, and what they
share is that the corpus DIVIDES on `subject`.

The candidate cause is a rule the product states in its own report — *"any level your files did
not actually divide … is measured and not built. A level your files DO divide is always built."*
Sound in isolation, and here it means a folder holding one course's material drops the `subject`
level, never builds a `PHYS1401` node, and leaves every file with one unmatchable candidate:
`no_supported_destination`, "needed a model". **F20 and the "every file needs a model" complaint
are one defect seen from two ends.**

Why it outranks its apparent size: *"all my PHYS 1401 stuff is in Downloads"* is the most ordinary
folder a person has, and the behaviour is inverted against intuition — **the clearer a person's
folder is about what it holds, the less the product does for them.**

**Not established here, and routed to `fix-q1-sizing` as evidence rather than conclusion:** which
component drops the level, whether "does not divide" is the predicate or a correlate of it, and
whether it is the same defect as the `school>term>subject>work_type` template refusing a corpus in
which no file carries a `school` fact. **The rule must not simply be deleted** — a level holding
every file, so a person opens one folder to find one folder, is a real defect it exists to
prevent. The question is what should happen when the only dividing level is the one dropped.

### F20, sharpened 2026-09-03 — the boundary checked, and the product says it out loud

`fix-f1-lockout` reported the opposite on its own corpus: *"WITHOUT the passport (4 files): same
three files freeze, into `Coursework/Review Later`."* Two contradicting reports is a reason to
measure, not to pick one. Re-run over three corpus shapes, fresh database each time:

```
mine (3 files, all name-prefixed, flat)      ->  Nothing was frozen.
theirs (4 files, mixed names, Uni/ subdir)   ->  Nothing was frozen.
theirs minus the subfolder                   ->  Nothing was frozen.
```

**F20 reproduces on their corpus too.** Their observation does not reproduce and is not
explained here — a different flag or leftover database state is the likeliest cause, since
`Coursework/Review Later` is a residual area and this command enables none.

And the run states the mechanism in its own words. The single nesting option it offers reads:

> `--answer 'branch:Coursework=school>term>subject>work_type'` — This option would create
> **1 term, and 1 subject. 3 file(s) would stay unresolved and visible.**

So the count is not hidden and the outcome is not a surprise to the product: it has measured that
the subject level yields ONE subject, dropped it for not dividing, and predicts that every file
stays unresolved. **The only option it offers is one it has already computed to be useless for
this corpus, and it offers it anyway without saying so.** That is a second defect beside the
first, and it is the one a person actually meets: `84` §6 — a screen that tells a person what to
type has to be true, and an option predicted to resolve nothing is not an offer.

### F20, resolved 2026-09-03 — and there IS a route, three runs long

`fix-f1-lockout` re-measured with a full flag matrix, fresh directory and database per cell,
against `bb5995b~1` and HEAD. Its earlier without-passport result was a report omission, not a
disagreement: every run in its script carried `--residual`, and the without-passport run also
carried `--send-set`, which its working notes had and its report dropped. **F20 stands.**

```
                                      PRE-FIX          POST-FIX
WITH passport (5 files)
  a) --freeze only                    nothing          3 -> Coursework/PHYS1401
  b) --residual --freeze              nothing          3 -> Coursework/PHYS1401
  c) --residual --send-set --freeze   nothing          3 -> Coursework/PHYS1401
WITHOUT passport (4 files)
  a) --freeze only                    nothing          nothing
  b) --residual --freeze              nothing          nothing
  c) --residual --send-set --freeze   3 -> Review Later 3 -> Review Later
```

**Row b is what settles it: `--residual` alone changes nothing.** It creates the destination;
`--send-set` is the only gesture in the matrix that files anything into a corpus with no subject
node. Confirmed independently on the three-file single-subject corpus — the exact command the
screen prints freezes all three into `Coursework/Review Later`.

**So F20 is not a dead end. It is a three-run maze, and each screen reveals only the next step.**

1. A plain run says *"This plan has nowhere to put them yet: enable an area with `--residual`"*.
   It does **not** mention `--send-set`, measured: `"--send-set" in output` is `False`.
2. A run with `--residual` still freezes nothing — and now prints `--send-set 'Not yet
   placed=Review Later'`.
3. A run with both files all three.

**Three invocations to file a folder of one course's material, with the first screen giving no
sign there are three.** Each individual sentence is true, which is why nothing here trips `84`
§6 — and a person is still walked into two dead ends before the product tells them the whole
route. That is the F20 defect as a person actually meets it, and it is separable from the
placement cause: even once a subject node gets built, the residual path stays the answer for
every corpus that genuinely has no destination, so the sequencing is worth fixing on its own.

Also corrected here: `fix-f1-lockout` withdrew its "causality proven both directions" claim, and
`94` F1's original reproduction shares the weakness. The clean control is the COLUMN — same
corpus, same command, before and after the fix — not the row, which varies corpus and flags at
once. The committed integration test asserts the column.

---

## F21 — an EXIF reader would DELETE OCR from 976 of the owner's images. Ruled: do not build it.

Found by `deepen-extraction`, verified by the lead at `src/extractors/ocr_policy.py:143`.

§2.7's trigger runs OCR on an image only when the file yields **"no usable text AND no usable
metadata"**, and `image_ocr_decision` implements that literally: `_has_metadata_observation(result)`
returns `run_ocr=False`. So a reader that emitted EXIF as observations would **stop OCR running on
every photograph carrying camera EXIF** — which is every phone picture, including the photographed
whiteboard and the snapped receipt that are the whole reason OCR is there.

On the owner's disk that trades **976 images' WORDS for their CAPTURE METADATA.** `image_headers.py`
says "adding EXIF is a reader change and nothing else"; that is true of the mechanism and false of
the consequence, which is exactly the shape of change that ships as an improvement.

**RULED, delegated, 2026-09-03: the EXIF reader is not built.** Three reasons and the third is the
one that settles it:

1. Words beat capture metadata for filing. "PHYS 1401 Lecture 8" written on a whiteboard is what
   places the file; the camera model and the shutter time are not.
2. **`image_exif` and `gps` are both in `ALWAYS_LOCAL`.** EXIF can never inform a model, by
   construction. OCR output is also always-local, but the FACTS derived from it are releasable in
   the ordinary way — so the two are not comparable in what they can reach.
3. §2.7's own wording — *"opaque images without EXIF"* — was written when an image carrying EXIF was
   assumed to be understandable from it. That assumption is false for the case the product is for:
   EXIF tells you which camera, never what the picture says. **So this is a design clause worth
   revisiting, and the trigger has to change BEFORE the reader is written, not after.** Building the
   reader first would silently take the words away and nobody would see it happen.

Whoever wants EXIF later: change `image_ocr_decision` so EXIF does not count as the "usable
metadata" that suppresses OCR, prove OCR still runs on an EXIF-bearing photograph, and only then
write the reader.

---

## F22 — a file can vanish from the freeze block entirely, and F16 fixed only one way in

Measured 2026-09-03 on the tree at `40c6816`, four files in one folder:

```
files in the folder : 4
Frozen              : 2
Not frozen          : 1
ACCOUNTED FOR       : 3
```

`noextension` — a plain text file with no extension — appears in **neither** list and is named
nowhere in the freeze block. F16 closed this for protected material by holding a protected subject
whatever its outcome; the same silent omission remains open for at least one other outcome.

**This is the standing rule's own case**: never silently omitted. A person counting their files
against that block finds one missing and has nothing to search for. It is worse than an unhelpful
reason, because there is no reason at all — the file is simply not there.

Note the interaction with `95`: `readers/signatures.py` now detects an extensionless file by its
magic number, but that detection is not wired into `cli._detect_format`, so this file is still
unrouted at the composition root. **Whether the freeze block's omission survives the wiring is not
established** — fix the omission on its own terms rather than assuming the routing fix covers it,
because a file can be unplaceable for reasons that have nothing to do with its format.

## F23 — a reason string is interpolated into a sentence that then reads as nonsense

Same run, verbatim:

> `problem set 3.docx`
> **This one is nothing has looked inside it yet**, so there is nothing here for you to approve.
> Freezing says where a file goes; it cannot say what a file is. It stays where it is.

"This one is {reason}" is being filled with a reason phrased as a clause rather than a noun. The
sentence is unreadable, and it is on the screen a person reads to find out what happened to their
files. Cheap to fix and worth doing before anyone runs this on a real folder: the surrounding
sentences are careful and well-judged, which makes the broken one read as a bug in the product
rather than a bug in one string.
