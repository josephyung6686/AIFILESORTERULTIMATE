# 72 — The finding ledger

Date: 2026-08-29. **Every finding from every audit, with what happened to it.**

This exists because the honest answer to "did you fix all the problems the audits found" is *no,
and here is exactly which*. A narrative cannot carry that. Five audits and four diagnosis agents
produced roughly seventy distinct findings; this table is the only place they are all in one list.

**Status vocabulary, and it is closed:**

| | means |
|---|---|
| **FIXED** | changed, tested with a negative twin, verified by running the command over real files |
| **OPEN** | real, unfixed, and nothing blocks fixing it but effort |
| **OWNER** | cannot be fixed without a decision that is Joseph's — a vocabulary, a threshold, a policy |
| **STALE** | the audit was right when written and the finding no longer reproduces |
| **REJECTED** | verified and found not to be a defect; the reason is given |

Suite at time of writing: **5354 passed, 19 skipped, 1 xfailed**, fixed and randomised order.

**Second pass, 2026-08-30.** Joseph answered four of the six owner questions in §8;
three of them are now shipped and their rows below are updated in place. What that
pass found on the way is in §9, and it is the more useful half: adopting the
folders turned out to need five more things, each of which was a defect nothing
had been able to see while every folder was dropped.

---

## 1. `planning/43-SPEC-vs-code-inspection.md` — the other agent's root causes

Its central claim is correct and is the most useful sentence written about this repo:

> The packages often satisfy Done means **when tested in isolation**, but the **live command path**
> deliberately turns off or never connects the behaviours the SPECs assume.

| | finding | status | what happened |
|---|---|---|---|
| R1 | Chooser under-wires hybrid intelligence: `rule=None`, `llm=None`, `p8_run_call=None`, `EmbeddingsOff()` | **OPEN** | The single largest remaining gap. Recognition was widened four ways instead — safety-domain precaution, pattern corroboration, the user's own answers (P15), and `DirectSlot.matches` — which is why the personas file at all. **A local model needs no mode change**: P7 defines `offline` as "only local rules and LOCAL MODELS may run", and `ollama` is installed on this machine. What blocks it is R7's oracles and the prompts, which are "templates and mechanisms" and need approval. |
| R2 | Extraction deployment does not match P5's formats: `read_docx`/`read_image`/`read_manifest`/`read_long_tail` = `_no_reader` | **PARTLY FIXED**, two of four | `.docx` wired (`2ab08e1`) and `.zip` wired (`c7836b7`). Both had the same shape: the comment said "ships no library" and the library was already there — `python-docx` installed, `zipfile` in the standard library — so every Word document and every archive recorded §2.4's `unsupported`, "the bytes were never looked at". The archive reader takes §2.5 literally and yields the manifest WITHOUT extraction, which is also what makes it safe: nothing is decompressed, so a zip bomb is never expanded and an encrypted member is listed by name and never decrypted. Verified live: 9 observations over 3 entries where the same file produced none. Images and the long tail remain unwired; `PIL` is installed and an image reader without OCR yields metadata only, which is why it is not simply the next hour's work. |
| R3 | Targeted OCR disabled by `usable_threshold=lambda: True` | **FIXED** (`c77f302`) | The empty case needs no threshold: a pass that produced no fact and recorded nothing unresolved settled nothing, and "usable" is not a defensible word for it. The Deferred threshold (M11, P5 OQ1) is still not chosen, so no text-bearing PDF is re-read on the strength of an unauthored number. Scope verified rather than assumed — `extract_targeted_ocr` returns immediately for any family but PDF, so an empty `.txt` cannot reach Vision. |
| R4 | Freeze catalogue vs launch-domain posture | **OWNER** | Whether the initial release routes 208 situations or six launch domains is a product decision. |
| R5 | `RESIDUAL_LIBRARY = {}` | **OWNER** | §7.3 fixes nine residual names and leaves their eight attribute slots deferred. Enabling one means inventing slot values. |
| R6 | No apply/undo (P12), no review surface (P13) | **OPEN** | Both have SPECs and PLANs. Unstarted, correctly — `66` §22 sequences them after Find. |
| R7 | Validation oracles (`normalize`/`contradicts`) not injected | **OPEN** | Blocks R1; P6 declines to publish them and the deployment supplies none. |
| R8 | Stale docs hide the real gap | **FIXED** | `43` itself, plus `69`, `70`, `71` and this file. |

**Its seven highest-signal drifts:** #1 P4 fixture coverage — **OPEN**. #2 P1 budget keys, "SPEC says
fifteen, code has seventeen" — **REJECTED**: `00`:256 states two quantities on one line and `f5132a1`
split them deliberately; the SPEC's count is the stale half. #3 P6 field catalogue wider than the
launch set — **OWNER**, same question as R4. #4 = R2. #5 P9 purpose fixture missing — **OPEN**.
#6 = R1/R6. #7 = R6.

---

## 2. `planning/71-DIAGNOSIS.md` — why nothing filed

| | cause | status | what happened |
|---|---|---|---|
| A | The document's words never reach the detector | **FIXED** | `36764b0`. |
| B | No handling class for ordinary schemas | **FIXED** | `36764b0` — all 23 schemas, safety four unchanged. |
| C | Templates need a hierarchy the deployment cannot fill | **FIXED**, and this was the keystone | `689566f`. A level nobody answered COLLAPSED every level beneath it; it is now skipped. Trees nest. |
| D | The folders the person already made are read, then discarded | **FIXED** (`cf7bf2f`) | Traced to one line: `pipeline.py:518` keeps candidates whose `subject_id` is in `branch_group_ids`; a folder candidate's `subject_id` is a directory PATH and `cli.py` passes one synthetic id, so no folder can ever match and eight cards are dropped unread with nothing recording it. `node_type='existing'` is DESIGNED AND ABSENT — storage, validation and a live consumer in `residuals.py` all exist, the only writer is a test fixture, so that consumer is dead by construction. **The tempting fix is actively harmful** and was rejected: putting folder paths into `branch_group_ids` mints top-level *proposed* nodes at the root, so the product would propose moving `Uni/PHYS1401/lab.txt` into a NEW `PHYS1401` — flattening the hierarchy in the name of honouring it, which `00`:100 forbids by name. Joseph ruled: adopt as `existing` nodes. Shipped — and the naive fix is still rejected, now by a test that says so. `_top_level_node` reads the card's SOURCE and writes `00`:102's `existing` node with the real path, nested under whichever of its own parent directories was also adopted, so the person's shape survives adoption instead of being flattened into a row of root-level proposals. Five more things were needed to make it real rather than cosmetic; see §9. Verified over a half-organised corpus: six files, all six placed into the person's own folders, four reading "nothing to do". |
| — | `preferred_fact` counts rows, not distinct values, so two producers that AGREE delete the file's folder level | **FIXED** | Counted by `value_id` now. OQ6 untouched: two values still return `None`, and the falsifying twin pins it. |
| — | Protection covers one extension (`.app`) | **OWNER**, still unasked | The suffix list is Joseph's ruling. One of the two questions in §8 that has not been put to him. |
| — | Five of nine `completeness` values unreachable | **OWNER** | Which value a text-less document gets is Joseph's ruling. |

---

## 3. The four diagnosis agents

**diag-tree** — five ranked causes of the one-folder tree. #1 the `_project` truncation: **FIXED**
(it reached the identical fix independently, which is the strongest corroboration available). #2
`review_and_accept` merges every group into one: **OPEN**, and its docstring's justification is
**verified false** — `engine_proposal` fills `display_label` and `group_category` before
`record_group`, so groups reaching review are already named. #3 the single-signal routing funnel
(`detection_signals_for=lambda group: frozenset({signal})`): **OPEN** — measured, fixing it alone
still yields one folder, but it is why Tom's household routes through `academic.coursework`. #4 V6
is blind to an empty LEVEL (it iterates values): **REJECTED**, and the reasoning is
now in V6's own docstring. The finding is correct about the loop and the fix would be
the fifth instance of the mistake named at the end of §7 — failing a whole candidate
for one level's fault. It is also unnecessary: `_project` and `_v2` both skip a level
that does not divide, zero values is the extreme case of not dividing, and the report
tells the person which levels were left out. #5 `choose_option`: **REJECTED**, behaving
as documented, the last domino rather than a cause. Its bonus finding — horizontal branch nodes carry
no expected values, so only `_project`-minted nodes can receive files — **CONFIRMED**, and it is why
cause C was the single point of failure for the whole product.

**diag-classify** — the arity rule. `00` states recognition as "a course-code PATTERN together with
academic CONTEXT"; the code required two TERMS and `SchemaRules` has no pattern field, so a course
code counted for zero and `00`'s own worked example could not execute: **FIXED** (`245bae5`), by
letting a pattern corroborate a term it may never nominate. Its measured alternative (the declared
`--situation` as second signal) was **REJECTED**: 5 newly classified and 1 wrong, against 4 and 0.
Its finding that a lone safety-domain reading is discarded by alphabetical order: **FIXED**
(`38aa988`, `c516d90`). Its finding that `support_score` is 2/7 for every file because the
DIRECT_FACT channel fires for none: **STALE** — files now place; the ancestor collapse in `689566f`
was the cause.

**diag-questions** — answered NO on the registry, correctly. The registry itself: **FIXED**
(`b382ef9`, P15). Four CLI writes claiming `user` when `rules` decided: **FIXED** (`c3b206d`).
P10's own event text — "The user accepted 'node_1' on the canvas surface", under the real login
name, on a surface that does not exist: **OWNER**. `REVIEW_SURFACES` is a closed set of two, both
P13's, and there is no member meaning "nothing was shown to anyone". `user_level_edits` has no
writer: **OPEN**. The `residual_configuration` freeze check is vacuous over `{}`: **OPEN**.

**diag-surface** — never reported, twice asked. Its brief is covered by the report work in
sections 4 and 7; the outstanding half is a fresh read of the CURRENT output as a user.

---

## 4. Found by running the command, not by any audit

Every one of these was invisible to 5,000 green tests.

| | finding | status |
|---|---|---|
| P11 scored a file's own ANCESTORS as rival homes; three nodes of one chain tied at 0.714 and every file abstained `privacy_blocked`. Step 6 is named `identify_child_parent_fallback_or_none` and had no implementation | **FIXED** (`689566f`) |
| "Ready to file" meant `place`, and `place` is not permission to move anything. Ten files read ready when eight were `blocked_pending_user` and one was protected | **FIXED** (`689566f`) |
| A passport number was a proposed FOLDER. Neither existing lever could stop it: `protected_handling_classes` MARKS rather than removes by design, and V5 refuses the whole branch | **FIXED** (`c516d90`) |
| `handling_class_for_member` answered a flat `ORDINARY_CLASS`, so P10 was told nothing in the corpus was sensitive — and the integration harness had the same defect, which is why no test could reach it | **FIXED** (`c516d90`) |
| `protected_handling_classes` omitted `sensitive_personal`, the class safety domains actually carry: the flag was raised and nothing read it | **FIXED** (`c516d90`) |
| A word in a pytest TEMP DIRECTORY PATH nominated a schema that a code then corroborated — introduced by my own fix and closed in the same commit | **FIXED** (`245bae5`) |
| My docx reader emitted 0-based container-path indices; P4 D3 refuses them, so a real document recorded `failed` — a damaged one | **FIXED** (`2ab08e1`) |

---

## 5. What is honestly still broken

Ranked by what it costs the person whose files these are. Re-ranked on 2026-08-30:
what was third is done, and what was first is now first by a wider margin.

1. **`--situation` and `--label` are one value per run.** Tom's household is filed
   as `Coursework`; the four-role persona's legal matter number `CV20261234` is
   filed under `Coursework` too. Measured this pass: P9 had already named four
   groups correctly and by itself — `PHYS1401`, `PHYS2801`, `CV20261234`,
   `Spring2026`, every one `label_source='engine'` and `coherent` — and
   `review_and_accept` merged them into one. **The merge is not the bug and
   removing it makes things worse**: the names survive through the vertical pass,
   so the tree really does read `Coursework/PHYS1401`, while accepting the four
   separately would put four course codes at the ROOT and destroy the nesting.
   The bug is that one `--situation` overrides four categories. This is `66`
   §13's structural-versus-contextual split at corpus scale, and it needs a
   per-group answer, which is P15's shape or P13's.
2. **R1 — no rule stage, no LLM stage, no P8 on the live path.** Recognition is
   term-matching plus four narrow widenings. It is why a deposition transcript
   needs a human to say what it is, and why `CV20261234` is categorised
   `academic` by the engine itself — that categorisation is upstream of the
   merge above, and fixing the merge would not fix it.
3. **P12/P13 — nothing moves, nothing is really reviewed.** Correctly sequenced
   after Find (`66` §22), and now the largest thing between this and a product.
4. **R2's remaining half.** Images and the long tail still record "the bytes were
   never looked at". An image reader without OCR yields metadata only, so this
   is not merely the next hour's work.
5. ~~Existing folders discarded~~ — **fixed** (`cf7bf2f`), see §9.
6. ~~The audit log names a surface that does not exist~~ — **fixed** (`a1fe0b9`).

## 6. The two standing questions this ledger does not answer

Both were Joseph's. **Both are now answered**, and both were answered the same way:

- **May a closed vocabulary gain a member** when it cannot express what happened?
  **Yes, with approval recorded at the member.** `SURFACE_UNATTENDED` and §8.2's
  `refused move` shipped in `a1fe0b9`. The naming was the agent's and is better
  than the brief's: `unattended` over `none`, because "none" reads as "not filled
  in yet", which is the exact ambiguity the member exists to remove.
- **Is the initial release six launch domains or 208 situations?** **208, at full
  scale.** R4, drift #3 and the residual library all reduce to this and all now
  have their answer: fix recognition rather than shrink the catalogue.

---

## 7. Added after the first version of this ledger

| | finding | status |
|---|---|---|
| `66` §12–§21's structural-question registry does not exist | **FIXED** — P15, `b382ef9`. Raise → print → `--answer` → persist → consume, verified end to end on the litigator's corpus. |
| §3.5 speaks of slots in the PLURAL and `DirectSlot.names` is a predicate over the LOCATOR, so two slots over one body each claim the other's readings — a deployment could ship only ONE text slot | **FIXED** — `DirectSlot.matches`, additive, `None` claims everything as before. |
| **V2 fails the WHOLE candidate when any level has one child.** A household with one term and two subjects gets NO tree rather than a tree without the redundant level | **FIXED** (`8d35912`) — Joseph ruled "skip the level, say so". `<= 1` rather than `< 2`, because `test_p10_no_invention` forbids a part to hold a numeric literal beyond 0 and 1; and counted over the LEVEL's own values rather than per parent, because the first attempt broke thirteen tests that were correct. The term dimension shipped immediately after (`a1fe0b9`) — it had been written, shipped, and reverted once, and V2 was the reason both times. |
| Plan ids were seeded from `COUNT(plan_versions) + COUNT(tree_nodes)` as "an upper bound"; previews mint node ids that are never written, so the highest id ran ahead of the rows and a second run collided with an `IntegrityError` | **FIXED** — unique by construction, per-run token. Hidden while every tree was one node deep. |

**Four instances of one mistake, now named, and all four fixed.** V5, V2,
`_project`'s truncation and — found on 2026-08-30 — an adopted folder's expected
values all took a fault about ONE LEVEL, or one value, and applied it to a WHOLE
composition, branch, or destination. It is worth stating as a class because it has
now recurred four times in four different modules written months apart, and because
the fourth was found only by running the command over a corpus that had already been
organised. The next check written in `validation.py` will face the same choice.


---

## 8. The owner questions, and what Joseph answered

Six were collected. **Four were put to him and answered on 2026-08-29**; all four
are shipped. Two were never asked, and both are still open.

| | question | answer | state |
|---|---|---|---|
| 1 | May V2 skip a level instead of failing the tree? | **Skip the level, say so** | shipped `8d35912`; unblocked the term dimension, shipped `a1fe0b9` |
| 2 | May a closed vocabulary gain a member it cannot express what happened without? | **Add both members** | shipped `a1fe0b9`; the audit log stopped naming a canvas that does not exist |
| 3 | Existing folder vs proposed branch — which wins? | **Adopt as `existing` nodes** | shipped `cf7bf2f`; needed five more things, §9 |
| 4 | Six launch domains or 208 situations? | **208, full scale** | standing direction: fix recognition, do not shrink the catalogue |
| 5 | Which suffixes are protected containers? | — | **unasked.** The list is `(".app",)`. |
| 6 | Which `completeness` value does a text-less document get? | — | **unasked.** Five of nine are unreachable, so a file that could not be read is recorded as read-and-empty. |

**Question 3 carried a second question inside it**, raised by the agent that traced
it: when a folder IS adopted, is a file already in it "placed" into its own folder,
or does that need a sixth product state, "already where it belongs", which `00`
implies at :102 and :104 but never names? `LEAVE_UNTOUCHED` and `PRESERVE` are the
vocabulary and neither has a consumer.

**Answered by building, and the answer is that no sixth state is needed.** The
state is DERIVABLE and now derived: a file whose current directory is the
destination's own `existing_path` is reported as staying put, not moved, and is
excluded from the "ready to file" count. The report distinguishes three cases where
it had words for two — this folder, another folder of the same name, and somewhere
else — because once the person's folders are adopted, "already in a folder CALLED
CHEM1500; the plan would put it in the one it proposes" describes a move out of a
folder and back into it. If a later part needs the state as a first-class outcome,
`LEAVE_UNTOUCHED` is there and its meaning is now settled by use.

**And one that is not a question but a permission:** wiring a LOCAL model needs no
mode change — P7 defines `offline` as "only local rules and local models may run",
and `ollama` is on this machine. What it needs is R7's oracles and a prompt, and a
prompt is a "template and mechanism", which house rules say is approved manually.


---

## 9. What adopting the folders found

Every one of these was invisible while every folder was read and dropped, and each
had to be fixed before adoption was worth having rather than actively worse.

| | finding | status |
|---|---|---|
| **Folder candidates were keyed by their LAST PATH SEGMENT.** A person with `Uni/PHYS1401` and `Physics/PHYS1401` — two real folders, two places, different files — had one overwritten in a dict and dropped with nothing recording it. The one outcome the owner's standing rule forbids without exception | **FIXED** — keyed by path, which is unique; the label was never a workable identity |
| **The scan ROOT was adopted as a folder inside its own proposal** — a node called `organised` holding `Uni` and `Inbox`, which is the whole corpus wearing a folder's clothes | **FIXED** — P3 marks a root by recording no parent |
| **An adopted folder expected nothing, so §6.2 could never choose it.** Adoption would have been cosmetic: the folders would appear and never receive a file | **FIXED** — a folder expects what its own contents AGREE on, read through P6's preferred-fact surface. Nothing composed: §5.4 forbids inventing a value and every one of these is P6's |
| **…and the first version of that expected too much.** Every file in one corpus was Columbia's and in one term, so all four adopted folders expected `term=Spring2026`, each matched every file, §6.10 called it multiple supported homes, and six files that had been placing fine abstained to a model offline mode forbids | **FIXED**, and it is **the fourth appearance of one mistake** — after V5, V2 and `_project`. An expectation the whole corpus satisfies divides nothing. This is V2's own test applied to a folder instead of a level, and it needs no threshold: either some file disagrees or none does |
| **An adopted folder named no accepted group**, so it carried `DIRECT_FACT` alone — 3 of §6.3's 7 points, against a 0.5 threshold — and everything in it abstained `no_supported_destination` | **FIXED** — it names the groups whose files it already holds, which `00`:100 lists by name among what the person should see about their own folder |
| **Step 6 had no cross-branch half.** The person's `Uni/CHEM1500` and the engine's `Coursework/CHEM1500` tied at every file | **FIXED** — a proposal whose expectations the person's folder wholly contains is not a second home but a vaguer copy of one. Three refusals keep it narrow: an expectant proposal only, a superset only, and never one of the person's folders against another |
| **`curated_folder_labels` had been passed `()` since the command was written.** §6.2's `CURATED_FOLDER` channel is `00`:100 in the scoring, and it had never once fired | **FIXED** — fed with the folders the file is already in |
| The report counted the person's folders as "Proposed folders" and drew them identically to proposals | **FIXED** — counted separately and marked `[yours already]`. `00`:100 asks for exactly this distinction and names it as a visual one |

**Two architectural guards refused a first attempt and were right both times.** §7.11
and B3 keep every composed path out of P11 — "P11 names a node and P12 resolves a
path" — so the index carries P10's `node_type` and not `existing_path`; and P10 may
not import a module that can write facts, so the new read goes through
`facts.read_surface` rather than `facts.file_facts`. Both were caught by tests that
existed before this work and knew what they were protecting.


---

## 10. Asking during the freeze (2026-08-30)

Joseph asked for proof that the tree, the sorting and the classification work as
`00` intended, and for the missing half to be built: a person asked questions
**during** the freeze rather than told afterwards what was decided for them.

**What the proof showed working**, over a two-life corpus (two courses already
filed under `Uni/`, three loose files in `Downloads/`, a legal matter in two
places):

| stage | evidence |
|---|---|
| classification | P6 settles `subject`, `term`, `school` per file; P9 forms four engine-named groups |
| existing structure | 5 of the person's folders adopted, nested, marked `[yours already]` |
| tree proposal | `Coursework/{CHEM1500, CV20261234, PHYS1401}` beside them |
| per-file destination | all 8 files given a home and a reason; 4 read "nothing to do" |
| questions | 3 raised from the corpus's own ambiguities, none invented |
| answering | 5 files waiting → 3 ready to file and 4 already correct |

**What was built.** §13 permits a structural answer five consequences and one was
wired. The second, `gate a template`, is now wired: `00`:78's own moment — the
engine builds every shape a branch's facts support, shows what each would create
with the counts, and the person picks. It was being decided by `options[0]` and
disclosed. An unanswered offer changes nothing, so asking costs the person
nothing and the first run is the run they always had.

**A third scope kind, `branch`, was added** under the 2026-08-29 ruling, and is
flagged for veto. `corpus` would let the shape chosen for someone's coursework
decide the shape of their legal matters (§13 forbids it by name); `organization`
promises "an entity the evidence produced" and a branch label is a word the person
typed.

**Two kinds of question now print apart.** A blocked reading stops something; a
nesting offer stops nothing. Under one heading a finished run looked stuck.

**Still not true, and the proof shows it plainly.** `CV20261234` is confirmed
`law_practice` by the person's own answer and still sits under a branch called
`Coursework`, because the branch label is one `--label` per run. That is §5's
first entry and this work did not move it.


---

## 11. What is PROVEN, what is ABSENT (2026-08-30)

Joseph asked three questions this section answers with evidence rather than
prose: is OCR working, is the whole pipeline working, and is the LLM involved in
sorting. Every row was measured by running the command, not by reading the code.

### Proven working, with the evidence

| stage | proof |
|---|---|
| **Scan (P3)** | 8 files, 5 directories read; protected containers counted, none opened |
| **Extraction — text, PDF, DOCX, ZIP (P4/P5)** | `text.structured`, `pdf.text`, `archive.manifest` runs, tier `native`, `complete` |
| **Extraction — OCR (P5 §2.7)** | **image-only PDF**, pdfminer text layer `''`, then `ocr.apple_vision` tier `ocr` `complete`; Vision's reading stored as three units: `PHYS1401 Problem Set 4`, `Columbia University, Spring 2026`, `Due Friday at noon.` |
| **Facts (P6)** | `subject`, `term`, `school` settled per file, cited to observations |
| **Grouping (P9)** | four groups, engine-named and `coherent`, no user input |
| **Tree (P10)** | nested proposal beside 5 adopted folders of the person's own |
| **Placement (P11)** | all 8 files given a destination and a reason; 4 read "nothing to do" |
| **Questions (P15)** | 3 raised from the corpus's own ambiguities; answering moved 5 files from "waiting" to 3 filed + 4 already correct; answering the nesting changed the tree from 3 children to none; revoking put it back |

### Absent, and named

| | state |
|---|---|
| **LLM / model, anywhere** | **ABSENT.** `model_client=None`, `p8_run_call=None`, `prompt=None`, and `group_dossiers` holds **0 rows** after real runs. Nothing is sent anywhere and nothing is judged by a model. Every placement above is deterministic. |
| **Find (`66` §1–§6, §18)** | **ABSENT — and §22 says it ships FIRST.** There is no search module in `src/`. |
| **Apply / undo (P12)** | **ABSENT.** Nothing moves. Every run ends "Nothing was moved." |
| **Review surface (P13)** | **ABSENT.** The CLI report and `--answer` are standing in for it. |
| **Profession/role matcher (§16)** | **ABSENT.** The only hits are template-library DATA, not a matcher. |
| **Household / person-shaped folders (§15)** | **ABSENT.** No relationship-category workflow. |
| **Image and long-tail readers** | **ABSENT.** Still §2.4 `unsupported`. |

### The finding that matters most about OCR

OCR reads the page and **its reading still cannot file the page**, and that is the
design working rather than failing. P4 marks OCR output `possible`; §3.6's
`PROPOSAL_ELIGIBLE_STATES` excludes `possible` by construction, because a weak
reading "must not quietly become a folder proposal". So a scanned page is read,
its words are stored, and the file waits for someone to say what it is.

**The tempting fix is wrong and was refused.** `DirectSlots` applies no test to an
observation's reliability -- §3.5 names a LOCATION, and `direct describes the slot,
not the value's usefulness` -- so adding `ocr:` to the two shipped slots would
turn every recognition into a `direct` fact and launder exactly what §3.6 exists
to stop. What legitimately promotes a `possible` reading is a validation stage
(R7's oracles) or a model (R1) or the person. Two are unbuilt; the third is P15.

**So: OCR is proven to READ, and is not yet proven to be USEFUL**, and the single
thing standing between those two sentences is R1/R7.

### One crash found by asking for this proof

Generating a genuine image-only PDF and running the command over it -- the first
time a real scan had ever gone through the live path -- crashed the whole corpus:
`extract_ocr` addressed every region of a page as `page[N]`, so three text units
were stored under one name and each span resolved against the wrong one. Fixed
(`d6ffee7`). Invisible for the life of the project because every OCR fixture used
`region=1`, the one shape a real scan never has.


---

## 12. How `74` and `75` connect (checked 2026-08-30)

The two plans were written in parallel and neither read the other. Both are sound
alone; two things bind them, and both would bite whoever picks up the second plan
first.

**1. `75` B3's guard is `74`'s to delete, and only `74` can.**
`75` B3 ships `test_no_question_option_requires_review_while_nothing_reads_it` —
a test that FAILS the day `requires_review` gains a producer, on the discipline
that a consequence with no reader is how a question comes to be asked for no
reason. It says the guard "is deleted in the same commit that adds P13's reader".
P13's review queue is `74` Wave A/B. **So a correct `74` change turns the suite
red until that guard goes with it**, and `74` does not mention the guard because
it did not know it existed. Whoever lands P13's queue deletes `75` B3 in the same
commit; the guard is doing its job when it fires.

**2. `74` A5 and `75` B2 are one fix from two ends and must be SEQUENCED.**
Both are the answer to §5's first entry — a legal matter filed under "Coursework".

* `74` A5: per-group acceptance. The CLI collects one decision per P9 group
  instead of merging them under `--label`, so four accepted groups produce four
  branches.
* `75` B2: per-branch situation. `run(..., situation=...)` stops being one value
  for a whole disk.

They edit the same call path in `cli.py` (`review_and_accept` and the situation
argument beside it), so done independently they collide. **A5 first, then B2**,
and the reason is not merely mechanical: a per-branch situation decides nothing
while every group is still merged into ONE branch. A5 creates the branches that
B2 then gives situations to. Reversed, B2 is a consequence with nothing to
consume it — the very thing `75` refuses to ship in B3.

**Nothing else conflicts.** `74`'s six findings touch P10/P11/P12 records; `75`'s
nineteen tasks touch `src/questions/` and the composition root. The only shared
file is `src/cli.py`, and only at the two points above.


---

## 13. Two things that would have stopped the model silently (2026-08-30)

Traced before wiring rather than after. Both are live, both are verified in the
code, and either alone would have made a wired model look connected and do
nothing.

**1. An UNCLASSIFIED file is denied to a local model, and the scanned page is
exactly that file.**

`gate.py:181-188` denies `unclassified` when `unclassified_denies(locality,
local_calls_on_unclassified)` fires, and `denial.py:177-188` is explicit that
`local_calls_on_unclassified` **has no default** — it is SPEC open question 5 and
"the caller answers it and P7 names no winner".

This is a chicken and egg, and it is precisely the OCR case. The scanned page has
no facts, so it is unclassified. It is unclassified, so the gate refuses to show
it to the model. The model is what would have given it facts. **`00`'s own report
line for that file already says it: "This file has not been classified — nothing
has yet said what kind of material it is — so it was not shown to a model."** The
sentence was accurate before the model existed and stays accurate after.

Only the owner can break it, and the question is narrow: **may a LOCAL model read
a file nothing has classified yet?** Note what is NOT at stake — no content leaves
the device under `local_model`, and `mode_forbids` (`denial.py:151-157`) already
refuses every CLOUD target in this mode for every file. Note also what stays
denied either way, because it binds local calls too: §7.3's protected-records
carve-out (`denial.py:191`), a revoked policy, an always-local item, and a
whole-document request.

**2. The call ceiling is zero for every corpus this project tests with.**

`budgets.py:147-150`: `allowed_calls = floor(corpus_file_count *
max_calls_per_1000_files / 1000)`, and the reserve SQL requires `1 <= allowed`.
At any sane per-thousand rate an 8-file corpus floors to **0**, so every call
returns `BudgetExhausted` and every file abstains. The formula is right for a
20,000-file disk and silently forbids all work on a small one.

This one is not an owner ruling so much as a ceiling that needs a floor: a rate
alone cannot express "at least a few calls on a small corpus". Recorded here
because a wired model that abstains on every file of an 8-file corpus looks
exactly like a model that is not wired at all, and that is a day of debugging
nobody should repeat.

**Also established:** no production `Gate` is constructed anywhere in `src/` —
only fixtures build one — so the composition root owes P7 its first real caller,
and `CallDependencies` has **17** fields, all required, none defaulted, with
`estimated_cost`/`actual_cost` needing a real `Decimal` (an int or float raises)
and `allowed_vocabulary=()` failing outright.

### 13a. The rest of the wiring, specified

Traced so the build is a build and not another investigation.

**`pending_fields` is ABSENT and must not be computed from the `unresolved`
table.** Every caller in `src/` and `tests/` returns a literal `()`. What it owes
is "every field the barred route would have attempted" (`resolver.py:236-241`),
and the correct read is `facts.domains.active_field_allowlist` MINUS
`facts.read_surface.facts_for` (which filters `active=1` and `superseded_by IS
NULL`). Not `facts_for_file`, which is unfiltered by its own docstring, and not
the `unresolved` table, which keeps superseded rows on purpose and whose existing
refusals are a different reason from "pending against the LLM route".

**`model_route_permitted` is a DIFFERENT gate from P7's `Gate`, not a second one.**
`Gate.release` takes a built `ModelCallRequest` — content already assembled —
whereas `model_route_permitted` is the pre-check that avoids assembling one, and
`resolver.py:190-194` says why it must come first: a handling class that forbids
the route is a PROHIBITION, and reporting it as a deferral "would promise work
that will never be done". Same facts, different moment; the Gate stays the
enforcing door. Compose it from `ClassificationStore.current` →
`classification.resolve_class` → `denial.mode_forbids`.

**An unclassified file answers False** — `classification.py:170-177`: absence
resolves to `unreadable_unclassified` and never to `public_low`, because a file
nobody has classified "has not met §8.4's precondition for escalation", and
"the gate denies it rather than guessing at it downward".

**One conclusion of that trace is already stale, and the staleness is the point.**
It ended "you do not have to answer OQ5 … this deployment has no local model, so
False is correct either way." True when written and untrue since `67e73bd`: the
local transport exists and `qwen2.5:3b` is installed. `mode_forbids` permits a
LOCAL target under BOTH local modes, so the moment a local model is wired,
`unclassified_denies` stops being moot and defers to
`local_calls_on_unclassified` — the flag with no default. **Building the transport
is what made §13's question live.**

**`activation_signals`** is `ActivationSignals(signals=(ActivationSignal(schema_id,
activates), ...))`, one per schema, duplicates refused. Nothing in `src/` builds
one; `ActivationSignals(())` is legal and yields universal fields only.

**And there is no proven example to copy.** No test and no production site wires a
`FactResolver` `llm` stage to `facts.llm_seam`; the only non-`None` stages in the
suite are recorders returning fixed ids. Every other seam in this project was
built against a working example. This one will not be, which is worth saying out
loud before it is attempted.


---

## 14. Two owner rulings, 2026-08-30

**Ruling 1 — a local model MAY read a file nothing has classified yet.**
P7 SPEC open question 5 (`unclassified_permits_local`) is answered: **yes, for a
LOCAL target only.** This is what breaks §13's chicken and egg — the scanned page
has no facts so it is unclassified, it is unclassified so the gate refused it, and
the model is what would have given it facts.

What the ruling does NOT relax, and every one of these still denies a local call:
`mode_forbids` still refuses every CLOUD target for every file in a local mode
(`denial.py:151-157`); §7.3's protected-records carve-out "binds local calls too"
(`denial.py:191`); a revoked policy, an always-local item and a whole-document
request all still deny (`gate.py:157,171,252`); and a protected file whose scope
has no consent grant still returns `NeedsConsent`. The ruling opens one door, for
one locality, for files nobody has classified — and `classification.py:170-177`'s
reasoning that absence "never resolves to `public_low`" is untouched, because an
unclassified file is still not treated as public; it is treated as readable BY A
MODEL THAT CANNOT SPEAK.

Recorded here and applied at the Gate when the composition root builds P7's first
real caller — which, per §13, does not exist yet anywhere in `src/`.

**Ruling 2 — the call ceiling gains a floor.** `ScanBudget.min_calls_per_scan`,
injected with no default like the rate beside it, and `allowed_calls` returns the
GREATER of the rate's answer and the floor. `max` rather than a replacement: a
floor must raise a small answer and never cap a large one, or a number meant to
keep small corpora working would override the actual budget control.

`0` is a real answer meaning "the rate alone decides", which is exactly the
behaviour before the field existed. All eight pre-existing constructions pass it,
so nothing changed for any test that was written before the question was asked.

**Ruling 3 — the prompt is NOT approved yet**, and is to be researched deeply and
stress-tested first, as detailed tasks. `76` is the requirements half. Nothing in
`src/` contains prompt text and nothing calls a model.


---

## 15. Three things a prompt cannot fix (from `76`'s research)

The prompt research was asked for requirements and returned three CODE findings
as well. They are recorded here because none of them is a prompt's to solve, and
two of them would silently undo work the prompt does.

**15.1 — The stored value is the model's spelling, not the normal form. STRICT
XFAIL, and the fix is P8's.**

`apply_verdict` writes `ensure_value(..., canonical_value=proposal.value, ...)` --
the raw model string. `ensure_value` derives the value id from what it is handed,
so `PHYS 1401` and `PHYS1401` become two rows, two ids and two folders for one
course. That is `65` §4.2's identity-splitting defect, which already cost this
project four one-file groups from one course, arriving a second time through a
different door. §3.6's check 3 asks whether the value "can be normalized safely",
so a passing verdict means a normal form EXISTS -- and it is discarded.

**The obvious local fix is the one the design forbids.**
`tests/integration/test_p8_p6_fact_seam.py:97` deliberately plants a THROWING
normalizer in `request.normalizers` to assert that P6 never calls it:
`FactRequest.normalizers` is DATA carried to P8, and
`FactValidationDependencies.normalize` is Site A's callback. Attempted, reverted.

The boundary-respecting fix is P8's: `fact_validation.py:233` already computes
`dependencies.normalize(proposal.field_key, raw_value)` for check 3 and throws the
result away one line before calling `apply_verdict` at `:322`. Passing it through
changes a published signature between two parts, which is why it is recorded
rather than done. A strict xfail states the case in
`tests/p6/test_p6_llm_seam.py` and goes green the day it is fixed.

**15.2 — Check 3 does not bound a value, and for 54 of 56 fields does nothing.**
`normalize_for_model` finds a `DirectSlot` for the field; this deployment ships
two, `subject` and `term`. Every other field gets whitespace collapsed and
returned, so check 3 rejects only the empty string and the non-string. Measured
against the live function, the exact failure that started this -- the whole line
`PHYS1401 Problem Set 4` proposed for `subject` -- **passes check 3**. It is
caught only by check 4, and only if a stronger `subject` fact already exists, in
which case the record reads `CONTRADICTED_BY_STRONGER`: the evidence disagreed,
when in truth the model agreed and over-quoted. With no stronger fact it is
`ACCEPT_DIRECT`. **The prompt is the only thing standing between a 3B model and a
folder named `PHYS1401 Problem Set 4`**, which is precisely why the owner was
right to refuse to approve one unresearched.

**15.3 — `allowed_vocabulary` and `FactRequest.allowlist` must be the same tuple
and nothing enforces it.** No caller in `src/` builds a Site A `DossierRequest`.
When one is written, the model READS `Dossier.allowed_vocabulary` and check 1
JUDGES against `request.allowlist`. `domains.active_field_allowlist` already
anticipates this -- "Task 17 hands this exact tuple to P8, so the allowlist is one
computation and not two" -- but the equality is documented, not asserted. Two
lists means the model is measured against one and validated against another, and
every correct answer to the list it was shown is rejected.

**And one stale row corrected.** §1's R7 records `normalize`/`contradicts` as
OPEN. They exist as of `db5845b` at `src/cli.py`. R7 is FIXED.
