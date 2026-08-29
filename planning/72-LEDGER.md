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

Suite at time of writing: **5316 passed, 19 skipped, 1 xfailed**, fixed and randomised order.

---

## 1. `planning/43-SPEC-vs-code-inspection.md` — the other agent's root causes

Its central claim is correct and is the most useful sentence written about this repo:

> The packages often satisfy Done means **when tested in isolation**, but the **live command path**
> deliberately turns off or never connects the behaviours the SPECs assume.

| | finding | status | what happened |
|---|---|---|---|
| R1 | Chooser under-wires hybrid intelligence: `rule=None`, `llm=None`, `p8_run_call=None`, `EmbeddingsOff()` | **OPEN** | The single largest remaining gap. `--situation`-driven recognition was widened three ways instead (safety-domain precaution, pattern corroboration, user answers), which is why the personas now file at all. The rule and LLM stages remain unwired. |
| R2 | Extraction deployment does not match P5's formats: `read_docx`/`read_image`/`read_manifest`/`read_long_tail` = `_no_reader` | **PARTLY FIXED** | `.docx` wired (`2ab08e1`) — `python-docx` was installed all along, so "ships no library" was false and every Word file recorded "the bytes were never looked at". Images, archives and the long tail are still unwired; `PIL` and `openpyxl` are also installed. |
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
| D | The folders the person already made are read, then discarded | **OPEN** | Under investigation. A four-level hierarchy and a flat control produced identical proposals. |
| — | `preferred_fact` counts rows, not distinct values, so two producers that AGREE delete the file's folder level | **OPEN** | Under repair. |
| — | Protection covers one extension (`.app`) | **OWNER** | The suffix list is Joseph's ruling. |
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

**diag-surface** — never reported. Re-briefed against the changed product; outstanding.

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

Ranked by what it costs the person whose files these are.

1. **`--situation` and `--label` are one value per run.** Tom's household is filed as `Coursework`.
   The report now admits it; nothing fixes it. This is `66` §13's structural-versus-contextual
   split at corpus scale, and P15 is the mechanism that should resolve it.
2. **R1 — no rule stage, no LLM stage, no P8 on the live path.** Recognition is term-matching plus
   three narrow widenings. It is the reason a deposition transcript needs a human to say what it is.
3. **Cause D — existing folders discarded.** A person who has already organised half their disk
   gets no credit for it.
4. **P12/P13 — nothing moves, nothing is really reviewed.**
5. **The audit log names a surface that does not exist**, under a real person's login name.

---

## 6. The two standing questions this ledger does not answer

Both are Joseph's, both are cheap to answer, and both block work that is otherwise ready:

- **May a closed vocabulary gain a member** when it cannot express what happened? Two cases now:
  `REVIEW_SURFACES` has no "no surface", and §8.2 has no event type for a move REFUSED before it was
  attempted. `69` §3a ruled the second one Joseph's; the first is identical in shape.
- **Is the initial release six launch domains or 208 situations?** R4, drift #3 and the residual
  library all reduce to this one question.
