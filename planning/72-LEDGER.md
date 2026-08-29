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
| R3 | Targeted OCR disabled by `usable_threshold=lambda: True` | **OPEN** | Verified. A broken text layer never gets the second pass. |
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
is blind to an empty LEVEL (it iterates values): **OPEN**. #5 `choose_option`: **REJECTED**, behaving
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
