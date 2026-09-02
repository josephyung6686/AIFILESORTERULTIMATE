# 85 — The reachability backlog, triaged

`84` §2 points at the census xfail's message as "the real backlog". This is that list
with a verdict and a reason attached to each entry, so the next person starts from a
worked list instead of from a number.

**Status: partial and honest about it.** 35 of 413 are triaged here — one agent's
ownership slice, done to evidence. The other 378 are listed by module, untriaged, so
the backlog lives in one place rather than only in a test's `reason=` string.

---

## 1. The measurement

```
python3 -m pytest tests/integration/test_composition_root.py -p no:randomly -rx
```

`test_every_public_mechanism_in_the_source_is_reachable_from_the_entry_point`. To get
the live list rather than the marker's prose:

```python
import importlib.util, sys, collections
sys.path.insert(0, "src")
spec = importlib.util.spec_from_file_location(
    "cr", "tests/integration/test_composition_root.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
un = [q for q in m._unreachable(m._reachable_from_cli_main()) if q not in m.EXEMPT]
by = collections.defaultdict(list)
for q in un:
    module, _, name = q.rpartition("."); by[module].append(name)
print(len(un), "in", len(by), "modules; population", len(m._public_callables()))
```

**Measured 2026-08-31 02:00: 413 unexplained, across 129 modules, population 1,490.**

The count is RISING, not falling: the xfail's own message records 261/1,226 on
2026-08-30 and the population has grown by 264 in a day, because P12 and P13 are
landing faster than anything is being wired. Do not read a larger number as a
regression, and do not read a smaller one as progress without checking the
population. **Always re-measure; never quote a number from this file.**

---

## 2. The three verdicts, and the rule

- **Design promise with no caller.** The design says the product does this and a
  person would feel its absence. Wire it.
- **Correctly dormant.** Nothing built legitimately has occasion to call it. Wiring it
  would mean INVENTING a call site — which is worse than the gap, because it puts an
  untested path on a person's run.
- **Should be deleted.** Genuinely surplus.

**"Correctly dormant, and here is the evidence" is a real result and usually the
commonest one.** The rule that separates it from laziness is the one `LAZY_TABLES` and
`EXEMPT` already use: a verdict earns its place by a reason that is TRUE OF THAT
SYMBOL, checked one at a time. A verdict with a generic reason is a whitelist entry.

---

## 3. The reframe — two causes, not 413 findings

Of the 30 unwired mechanisms in the triaged slice, **28 are dark for exactly two
reasons**, and both are one decision rather than many:

| Cause | Count in slice | What it gates |
|---|---|---|
| **No model transport is wired.** `cli.py:1610` passes `p8_run_call=None, p8_authorities=None`; `ModelClient` is constructed only in tests. | 13 | every prompt-shaping, egress-redaction and consent mechanism |
| **P13's review surface is built but unreachable.** `cli.py` imports only `review_surface.schema` and `review_surface.vocabulary`. | 9 | every diff, health, rename and version-action surface |

This is the same shape `privacy/transport_guard.py` was already found to have — dark
because nothing transports, so the guard has nothing to guard. It is worth checking
whether the untriaged 378 collapse the same way before treating them as 378 problems.
On inspection of the module names alone, `eval_harness.*` (31) looks like a third such
cause — P2's replay driver is unbuilt — and `mutation.*` (63) plus `review_surface.*`
(120) are P12/P13 in flight and should not be triaged until Wave G lands.

---

## 4. Triaged: `privacy/defaults`, `privacy/consent`, `placement/`, `tree_design/`

35 mechanisms, 15 modules. Evidence is `file:line` in the shipped source.

### 4.1 Wired — design promise with no caller (5)

| Symbol | Evidence |
|---|---|
| `tree_design.config.tree_limits` | `pipeline.py:180` states the chain "runs under P1's tree ceilings and §5.9's thresholds, read through `tree_design.config.tree_limits`". False on every run: `cli._bootstrap` seeds only `placement.config.CEILINGS`, so `tree.max_folder_proposals` and `tree.max_depth` — the two keys P1 split apart on 2026-08-29 *for P10* — are written by nothing, `tree_limits` refuses on every real database, and P10 runs on a hand-built `TreeLimits` that never passes `_positive`. |
| `privacy.defaults.effective_policy` `resolve_default_policy` `assert_local_first` `DefaultPostureViolation` | `gate.py:129` names the owed caller from the other side: "W1's local-first floor is resolved in `defaults.effective_policy`, not here, so the gate refuses to invent one". `cli.py:1418` builds the `Policy` by hand with `redaction_settings={}`, so the record the product puts in force states none of §8.4's five facets. Verified on a real run: `SELECT operation_mode, redaction_settings FROM privacy_policies` → `offline\|{}`. |

Both fixes live in `src/cli.py` and are held as a diff for the composition root's owner
(§6). Tests landed in `90c6767`.

**A contradiction found on the way, worth its own line:**
`model.max_dossier_tokens_per_call` is ONE §8.6 key that P9, P10 and P11 all read, and
the run holds two answers to it — `8` in the ledger a §8.5 replay reads
(`cli.py:1043`'s blanket `CEILING_VALUE`), `4000` in the two limit objects `cli.py`
builds by hand. Neither number is wrong in a way any part's own suite can see, because
each part is internally consistent. P9 has the same gap: its three `grouping.*` keys
are also seeded by nothing.

### 4.2 Correctly dormant (28)

| Module | Symbols | The evidence that decides it |
|---|---|---|
| `privacy.consent` | 4 | `open_consent_request` has ONE caller — `gate.py:242`, the model-release path. No model is wired, so no consent request is ever opened, so `pending_consent` has nothing to find and `record_consent_choice` nothing to answer. Wiring from cli would mean inventing a request no run opens. |
| `tree_design.template_schema` | 5 | `SiteDependencies` is constructed once in all of `src/` — `p8_seam.py:119`, with `template=None`, deliberately ("passing None is how P11 says it has no authority to offer there"). The state these serve, `ACCEPTED_GROUP_FITS_NO_EXISTING_TEMPLATE`, is a hard refusal today: `routing.py:316` raises `CompositionConflict(C3)`. |
| `tree_design.profiles` | `redacted_for_egress` | Redaction is correct at a prompt boundary and there is none. Profiles go to LOCAL storage (`freeze.py:303,433,490`); redacting them would destroy audit content, which is the opposite of the rule. The configuration it needs already exists at `cli.py:1253` — only the boundary is missing. |
| `tree_design.templates` | 2 | `cli.py:1271` is `template_context_for=lambda field_ref, order_index: None`, so every node in every run carries `template_context=None`. `BranchTemplateBinding` is never constructed anywhere in `src/`. Wiring needs a UI gesture offering candidate orders, which does not exist. |
| `tree_design.provenance` | `record_template_application` | Its three identity arguments come from that same always-`None` `TemplateContext`. Its sibling `record_tree_edit` IS wired (`store.py:452,553,599`), which is what makes this look like a promise — but a call today could only pass invented ids. **The honest defect it exposes is `cli.py:1271`, not the missing event.** |
| `tree_design.stage_output` | 2 | "Replay only" by declaration (`grouping/stage_output.py:16`). P11's identical pair LOOKS reached but both call sites sit behind `if inputs.p2 is not None` (`placement/pipeline.py:385,459`) and `cli.py:1575` passes `p2=None` unconditionally — so no shipped run writes a stage row through either. The census cannot see a runtime guard; the asymmetry is an instrument artifact. |
| `tree_design.diff` | 2 | Its one caller, `versions_view.py:126`, is itself unreachable. A run's N+1 versions are the chain's own bookkeeping — `_open_first_draft` opens an EMPTY draft, so diffing first against last reports every node as added, which is a transaction log printed to someone who made no change. |
| `tree_design.health` | `tree_health` | Five of its six fields are pass-through; it is a data contract for a canvas. `cli.report` already answers the question better for a terminal, one outcome at a time, and §5.11 explicitly forbids the single completeness number a per-group ratio would be ("a grade to raise"). |
| `tree_design.freeze` | 3 | §5a — recording the release — landed: `pipeline.py:769`. §5b–§5e, the only thing that would ever COMPARE two releases, is unbuilt, and a run loads exactly one catalogue. `is_legal_destination` has three near-consumers (`index.py:516`, `plan.py:182`, `preconditions.py:156`) and each needs a strictly LARGER test, which is why none calls it. |
| `tree_design.upstream` | 2 | The filtering is centralised inside `accepted_groups` (`upstream.py:157`) precisely so no caller can forget it — "one caller forgetting is one folder the user never agreed to". These are the same predicates re-exposed for a canvas surface that was never built. **Checked and refuted: `cli.py:471-523` does NOT duplicate them**; it implements the four Protocol methods and nothing more. |
| `placement.versions` | 3 | `cli.py:1211` mints a fresh `uuid4` run token per run and `tree_design/pipeline.py:789` writes each root version with `predecessor_id=None`, so two runs share no `origin_node_id`. `reproject` across them would classify EVERY placed decision as needing renewed review. That is a wrong answer, not a missing one. The thing to build is cross-run version lineage, not the call. |
| `placement.store` | `decision_history`, `decisions_for_plan` | `decision_history`'s consumer is a Find/reader surface that does not exist; `cli.report` prints decisions from the in-memory run and never reads them back. `decisions_for_plan` is unreachable ONLY via `reproject` (`versions.py:99`) — triage it with that, and do not delete it. |

### 4.3 Should be deleted (1)

| Symbol | Evidence |
|---|---|
| `placement.store.placed_node_ids` (`store.py:180`) | **One line in the entire repository** — its own definition. Zero callers in `src/`, zero in `tests/`. Its promised consumer is named in its docstring ("Task 17 diffs this against the tree") and was never written; the diff it would feed operates on node records, not placement outcomes. Named in three planning inventories that would need updating with it. Not deleted here — flagged for the owner of `src/placement/`. |

Weaker sibling, same shape: `tree_design.freeze.legal_destination_ids` (`freeze.py:149`)
is a pure field getter whose only test asserts it equals the field it returns. It does
not appear in the census only because the instrument's name resolution over-reaches.

### 4.4 Promise with no caller, owned elsewhere (1)

`tree_design.user_edits.record_user_level_edit` — tracked by its own strict xfail at
`tests/integration/test_composition_root.py:133`. `src/review_surface/` now has 25
modules and still no writer; it has built the DISPLAY of edits that could not be
honoured, not the RECORDING of an edit. The read path is fully live
(`pipeline.py:667` → `routing.py:506`), so only the writer is absent. **P13's to wire.**

---

## 5. Untriaged — the remaining 378

Listed so the backlog is in one place. **Do not treat a row as a defect until it has a
verdict**; the slice above came out 28 dormant to 5 wirable, and there is no reason to
expect a different ratio here.

Do not triage `mutation.*` or `review_surface.*` while P12/P13 are in flight — their
reachability lands with Wave G.

Counted 2026-08-31 02:00, excluding the 35 triaged above.

| Package | Count | Modules | First read |
|---|---|---|---|
| `review_surface.*` | 125 | 23 | P13, in flight. Unreachable as a package: `cli.py` imports only its `schema` and `vocabulary`. |
| `mutation.*` | 63 | 14 | P12, in flight. |
| `facts.*` | 50 | 20 | Includes P5's date grammar (8 in `facts.dates`). |
| `eval_harness.*` | 31 | 6 | Likely one cause: P2's replay driver is unbuilt. `test_p10_done_means.py:29` already records the posture for the stage emitters. |
| `questions.*` | 28 | 6 | |
| `scan_agent.*` | 13 | 7 | Mostly replay/snapshot. |
| `llm_harness.*` | 12 | 7 | Gated on the missing transport. |
| `database_agent.*` | 11 | 8 | |
| `extractors.*` | 10 | 6 | |
| `grouping.*` | 10 | 5 | Two are the stage emitters above. |
| `readers.*` | 10 | 3 | The model transports themselves — gated on the same decision. |
| `privacy.*` | 8 | 4 | `audit`, `classification`, `learning_seam`, plus `policy.grant_consent` / `transcription_authorized_for`, which are consent-gated and therefore transport-gated. |
| `evidence_shape.*` | 3 | 3 | |
| `cli`, `orchestrator` | 4 | 2 | |

---

## 6. Traps the instrument has, stated so they are not rediscovered

1. **It cannot see a runtime guard.** It is a pure AST reference walk. `placement`'s
   stage emitters read as reachable and P10's identical pair does not, purely because
   P11 wrote `if inputs.p2 is not None` around a call and P10 did not write the call.
   Neither fires. **Reachable is not "runs".**
2. **It resolves names, not namespaces** — deliberately over-stating reachability, so
   "unreachable" is safe and "reachable" is not.
3. **A stale REASON on a live instrument is the real hazard.** Two were found and
   corrected in `6289643`: `tests/p11/test_p11_versions.py` said P13's version-diff
   surface was unbuilt (it is built, unreached, and correct not to call `reproject`),
   and `tests/p10/test_p10_done_means.py` said two emitters had no `src/` caller (they
   gained guarded ones). Both verdicts survived; both reasons had gone false. This is
   exactly how "deliberate" decays into "forgotten".
4. **A part's own suite cannot see this defect class**, because every part builds its
   own fixture and sets up the state the run never reaches. The two tests added in
   `90c6767` are the counter-pattern: ask the part's own reader whether it works
   against a database `cli._bootstrap` actually produced.

---

## 7. Open, for whoever picks this up

- **`review_surface/consent_surface.py`'s docstring claims obligation 3, "The chosen
  option is routed to P7". There is no code for it** — it never calls
  `record_consent_choice`. For P13's owner.
- Wiring `tree_limits` requires the composition root to decide one number that is
  currently held twice (§4.1). It is a `cli.py` decision, not P10's.
- P11's residual return cycle — 13 mechanisms named in the 2026-08-30 xfail message —
  is **closed** and no longer on the list.

---

# Second slice — 142 more, 2026-09-02

Same method, same three verdicts, appended rather than merged so §4's slice stays as
its author left it. Nothing above this line was edited.

**Re-measured 2026-09-02 with §1's snippet: 401 unexplained across 127 modules,
population 1,490.** Down 12 from §1's 413 on a population that has not moved. Do not
read that as progress or as regression without checking both numbers; and do not
quote it — re-measure.

Ownership at the time of writing: `review_surface.*` and `mutation.*` are two other
agents' and are still in flight, so they are untouched here, as §5 asks.
`readers.*` and `llm_harness.*` belong to whoever is wiring DeepSeek. This slice is
everything else: `facts` (34), `eval_harness` (31), `questions` (28), `scan_agent`
(13), `database_agent` (11), `extractors` (10), `grouping` (10), `evidence_shape` (3)
and `orchestrator` (2).

**Split: 26 wired, 111 correctly dormant, 4 flagged for deletion, 1 instrument
artifact.** The ratio is close to §5's prediction and to §4's own 28:5.

---

## 8. Wired — design promise with no caller (26)

Three patches, all in `src/cli.py`, held for the composition root's owner at
`scratchpad/reach/CLI-PATCH.txt` as PATCH A, B and C. Each was applied to a COPY of
`cli.py` and the real command run against it, so the hunks are measured rather than
proposed. Each has a strict-xfail test committed that XPASSes — and so fails the
suite, forcing the marker off — the day its patch lands. Every twin was proven by
sabotaging the implementation and watching it go red.

### 8.1 PATCH A — §1.1's other three exclusion rules reach no screen (2)

`scan_agent.summary.set_aside_paths`, `scan_agent.summary.scan_run_summary`.
Test: `tests/p3/test_p3_composition.py` (`94fe3f5`).

**This is the most important thing in this slice.** §1 of `84`'s standing rules —
"marked and counted, NEVER SILENTLY OMITTED" — is honoured for exactly one of §1.1's
four exclusion rules. `cli.py:1672` prints `tree_design.upstream.protected_areas`,
which filters to `RULE_PROTECTED_CONTAINER`. Literal directory name, category and
software-project-root descendant are written to `exclusion_verdicts` and told to
nobody.

Measured by running the real command on a corpus of one syllabus plus
`node_modules/`, `Library/` and a `myproject/` holding `package.json`. The report
printed `Protected containers: 0 marked, none opened` and nothing else, while
`set_aside_paths` on that same database returned four rows — `Library`,
`node_modules`, and BOTH files under the project root. `summary.py`'s own module
docstring already names the case: *"That is `Library/` on a real person's machine,
which is where their mail and their app data live."*

The same run puts `myproject/` in the plan as `[yours already]` while both files
inside it were set aside unread, so a person sees a folder of their own in the
proposal with nothing in it and no reason given.

### 8.2 PATCH B — P15's role surface has no gesture (20)

`questions.roles` (7: `apply_declarations`, `apply_descriptions`, `declare_role`,
`described_sentences`, `live_roles`, `outcome_of_roles`, `skip_role`),
`questions.triggers.role_declaration_is_due`, `questions.proposal` (4:
`propose_roles`, `shortlist_for_question`, `RoleProposal`, `ProposalRefused`),
`questions.explanation` (6), `questions.store` (2: `questions_for`, `answer_by_id`,
reached through the two above).
Test: `tests/p15/test_p15_composition.py` (`4b33e3c`).

Two owner rulings land here and neither has a surface. `80` §3 (R1) puts the
self-description question at the moment a run "hits its first genuinely ambiguous
file"; `role_declaration_is_due` decides exactly that, mints nothing, and is called
by nothing, so the moment never arrives. §13:453 requires a person to be able to
inspect an answer, and `explain_question` is imported by nothing in `src/`.

**The part says so about itself, which is what makes this a defect and not an
absence.** `roles._split` refuses a malformed gesture with *"The form is
`--declare-role <name>=<what>`"* and `apply_declarations` points at
`--describe-role`. Those are flags `argparse` rejects. `84` §6: what the screen
tells a person to type has to be true.

With PATCH B on a copy: the run prints the invitation; `--describe-role` echoes the
sentence and offers all 23 layouts alphabetically — Option 1, `propose=None`, which
`80` §1 makes the fallback "whenever no local model is present"; `--declare-role`
records it and `outcome_of_roles` reports `exact_activation`; a second run does NOT
invite again, which is R2's friction budget spent once; and
`--declare-role teaching=barrister` is refused with the whole closed list and exit
code 2 rather than a traceback.

**A defect found on the way, fixed in `c17c76a`.** Wiring `--explain` and reading
what came out: §13's "how to change it" printed
`--answer branch:Coursework=<school>term>subject>work_type | keep-as-it-is>`. Two
things wrong on one line. It is manual-page notation, where the brackets and the bar
are not the person's to type — while the report prints one whole
`--answer <typable>   <label>` per option, so the same product said the same thing
two ways. And it was unquoted: `school>term>subject>work_type` is a real shipped
option id and `>` is the shell's redirect, so pasting that line does not fail — it
silently creates files called `term`, `subject` and `work_type` wherever the person
is standing. `explanation._how_to_change` now goes through the same `shlex.quote`
computation `cli._typable` does, in the report's own form.

### 8.3 PATCH C — §17's "meaningful diff" is built and nothing prints it (4)

`questions.effects.changed_answer`, `diff_for_answer_change`, `AnswerChange`,
`PlanEffectDiff`. Test: `tests/p15/test_p15_effects_composition.py` (`57812aa`).

§17:576-582 requires that editing an answer show a meaningful diff. Today `--answer`
supersedes a row, the run comes out different, and nothing says what the correction
did. `61` A.5: *"An answer that quietly rewrote a tree the user could not trace is
the defect this whole design exists to avoid."*

**The split inside that module is the finding, and only two thirds of it is wired.**
`changed_answer` and `diff_for_answer_change` need nothing but P15's own rows.
`draft_for_answer_change` needs P10's `open_draft` and stays **correctly dormant**
for the reason §4.2 already recorded against `tree_design.diff`: `_open_first_draft`
opens an EMPTY draft, so a diff of first against last reports every node as added.

The half of PATCH C that matters is that the diff prints the three of §17's six
questions P15 CANNOT produce, each with its reason. A diff printing only the three
it has would read as a complete account of the consequences, which is the one a
person acts on. `PlanEffectDiff.is_empty` refuses to be read that way in its own
docstring; the screen has to keep that promise too.

---

## 9. The reframe again — four more one-decision causes

§3 found two causes behind 28 of 30. The same collapse holds here: **97 of the 111
dormant are dark for seven decisions, none of them a defect in the part.**

| Cause | Count | Evidence |
|---|---|---|
| **P2's evaluation is passed `None`.** `cli.py:1105`'s own comment says so: "the composition root passes `evaluation=None` a few hundred lines below". | 38 | all 31 of `eval_harness.*`, plus the four stage emitters (`facts.stage_output` 3, `extractors.stage_output` 2, `grouping.stage_output` 2 — minus overlap) that exist to fill a replay bundle |
| **`orchestrator.run_wave2` is LEGACY.** `facts/usable.py:16` says it in capitals — "**DO NOT WIRE THIS INTO legacy `run_wave2`**" — and `production.py` composes `run_p1_p7` instead. | 3 | `orchestrator.run_wave2`, `orchestrator.TARGETED_OCR_UNAVAILABLE`, `extractors.dispatch.extract` (whose own docstring calls it "the backward-compatible composition") |
| **No encoder is wired.** `cli.py:1697` passes `embeddings=EmbeddingsOff()` and the retrieval channels are all `None` at `cli.py:1681-1684`. | 4 | `grouping.embeddings.recompute_file_embedding`, `database_agent.vectors.get_embedding`/`put_embedding`, `database_agent.vector_versions.embedding_history` |
| **The corpus source is the filesystem one.** `cli.py:826` passes `FilesystemCorpusSource()`; replay needs the snapshot one. | 8 | `scan_agent.replay.*` (5), `scan_agent.corpus_source.SnapshotCorpusSource`, `scan_agent.selection.selection_payload`/`record_selection_from_payload` |
| **P14 "Find" is NOT being built** — owner declined 2026-08-31 (`84` §3). Every read-back-later surface loses its consumer with it. | ~14 | `facts.read_surface.*` (6), `facts.supersede.fact_history`, `facts.values.*` (5), `database_agent.files_table.file_path_history`, `evidence_shape.store.supersede_chain`, `grouping.store.*` (4) |
| **No model transport** (§3's first cause, still). | ~7 | `facts.llm_seam.build_request`, `facts.domains.active_field_allowlist` (its only two callers are `llm_seam` and `read_surface`), `database_agent.scan_usage.record_llm_cost`, `questions.proposal.SelfDescriptionSending`/`sending_notice`, `grouping.failure_points.*` |
| **P13's review surface is unreachable** (§3's second cause, still). | ~3 | `database_agent.learning.reset_preferences` — its own docstring names the caller: "P13 collects the gesture as `review_action` with surface = learning and action = reset_learning and routes it here"; `grouping.acceptance.membership_review_state_as_of` |

**This matters more than the count.** Seven decisions, five of them deliberate and
recorded, account for two thirds of what this slice found. §3's advice was right and
should be applied to the remainder: check whether a module collapses before treating
its symbols as findings.

---

## 10. Correctly dormant, with the reason that is true of that symbol

The residue that is NOT explained by §9. One at a time, because that is the rule.

| Symbol(s) | Why it is dormant, and what would legitimately call it |
|---|---|
| `facts.session.bounded_sessions`, `facts.photo_event.photo_events` | **These are Done-means 25 and 26 — P6's own done criteria — built, tested and blocked on numbers nobody has ruled.** `SessionBoundary` requires `window_seconds`, `require_same_parent_folder_context` and `minimum_members`; `PhotoEventClustering` requires `same_event` (the time window, GPS radius and camera-identity test, Deferred together) and `minimum_members`. Both docstrings say the design states none and that a default here "would be P6 answering a deferred question inside an implementation". `84` §1: absent means refuse, never guess. **This is an owner decision, not a wiring gap — see §12.** |
| `facts.families.duplicate_family`, `facts.families.version_family`, `facts.families.Lineage` | The same shape, one step further out: `perceptual_hash_label` + `near_match`, and `lineage_rule`, are required with no default because "§2.6 names the perceptual hash and states no distance metric and no threshold". `cli.py:1695` passes `duplicate_or_version=None`, which is that refusal made explicit at the composition root. |
| `extractors.budgets.p5_ceilings`, `facts.budgets.ceiling_values`, `facts.budgets.UnknownCeiling`, `database_agent.budget.all_ceilings` | **The same family as §4.1's `tree_limits`, and worth stating as a family.** Each is a part's declared reader of its own ceilings; each says in its own words that reading a ceiling is not enforcing one; and `cli._bootstrap` seeds `placement.config.CEILINGS` only, so P5's four `ocr.*`/`image.*` keys and P6's three are written by nothing. Unlike `tree_limits` these harm nobody today, because nothing consults them — but the day an OCR engine is wired, P5's four ceilings are absent and `p5_ceilings` returns four `None`s. |
| `extractors.budgets.deferred_result`, `extractors.budgets.extraction_counts` | §8.6's user-facing sentence — "1,842 files indexed; 1,611 fully extracted; 89 scanned PDFs deferred after the OCR limit; 18 files remain unreadable". **The report prints none of it, and I did not wire it**: `extraction_counts` takes P4 run rows and there is no corpus-wide reader for them, so wiring from `cli.py` would mean writing a `SELECT` over `extraction_runs` in the one file that is supposed to hold no part's schema. PATCH A prints the counters `scan_run_summary` already computes, which is the half that needed no new query. **The other half is owed and named in §12.** |
| `extractors.events.extraction_event`, `extractors.events.ocr_event` | Already triaged, in the module's own header, in capitals: "NOTHING IN `src/` CALLS EITHER ONE... Their only callers today are tests/p5/." P4's `record_run_event` builds its own payload from stored rows. Kept as "payload builders and as the guard that P5 authors none of P3's event types" — see §11, because that guard is a test's job. |
| `extractors.router.routing_decisions`, `extractors.runs.analysis_tier_for` | Read-back surfaces over routing. `route(...)` and `record_routing_decision` are both live in `run_p1_p7`; the WRITE happens and the READ has no consumer, because there is no screen that explains why a file went to one extractor. `analysis_tier_for` is a lookup its writers already have inline. |
| `extractors.stage_output.extraction_stage_output`, `extractor_versions`; `facts.stage_output.*`; `grouping.stage_output.*` | §8.5 stage emitters, gated on §9's first cause. Note the trap §6.1 records: `extraction_stage_output` is exercised by `tests/integration/test_live_path.py`, so it LOOKS live and no shipped run reaches it. |
| `scan_agent.deferrals.scan_deferrals`, `scan_agent.run.get_scan_run`, `scan_agent.summary` (the rest) | Readers whose one consumer is the summary block. `scan_run_summary` reads `scan_deferrals` internally for its budget counter, so PATCH A reaches it indirectly; `scan_deferrals`' OTHER reasons — Q7, Q14, and the directory that could not be read — still have no surface. `summary.py` says they are "readable from `scan_deferrals` without an invented counter", which is true of a reader and not of a person. |
| `scan_agent.watch.SessionWatch` | `11` §3's per-session watch: "Closing it ends the watch; nothing survives." A single-shot command has no session to watch. The legitimate caller is the long-running app, which is also `default_database_path`'s caller — see below. |
| `database_agent.db.default_database_path` | Composes `~/Library/Application Support/<bundle>/agent.sqlite` per `11` §2. Its own docstring says the bundle identifier "is NOT specified by `11` and is not invented here: the application that launches P1 supplies it". A CLI has no bundle id; `cli.py:2589` puts the database in the working directory instead, and `open_database` already refuses one inside the corpus. The legitimate caller is the packaged macOS app. |
| `database_agent.verify.verify_content`, `confirm_cross_volume_copy` | P12's, and reached only from `mutation.execute`/`undo`/`cross_volume`. Triage them WITH P12 when Wave G lands; do not delete. |
| `database_agent.scan_usage.scan_resource_usage` | The reader for a row `scan_agent.run.start_scan` already writes. Its consumer is a progress or resource surface that does not exist. |
| `evidence_shape.conformance.validate_observation` | "The extractor's gate... It never returns a repaired record." The live path constructs observations through `RunWriter`, which validates on write; a second gate ahead of it would be the same check in two places, which is the defect this repo has paid for most often. |
| `evidence_shape.observation.collapse_key` | "Published so six extractors collapse the same way. P4 enforces no uniqueness on it." A published convention with no enforcement point is reached by whichever extractor chooses to collapse; none currently does. |
| `facts.cache.is_stale`, `facts.usable.create_fact_passes` | `is_stale`'s job is done inside `FactResolver`'s cache key; `create_fact_passes` says outright that `create_facts_schema` already creates its table and that "it stays for a test that wants the one table without the rest" — a stated, checked reason, which is the difference between dormant and surplus. |
| `facts.evidence.context_pair`, `facts.facets.word_boundary_match`, `facts.rules.context_check` | All three have exactly one caller, `facts.rules.apply_rules`, and it is dormant for the reason below. Triage them with it. |
| `facts.rules.apply_rules` | `cli.py:696` states the reason and **I re-verified it rather than trusting it**, because `84` §5.4 records a case where exactly this reason had expired: no authored `facts.rules.Rule` set ships. `src/recognition/rules.py` is the near-miss and it is a DIFFERENT vocabulary — `SchemaRules` with context terms and extensions, not `(field_key, pattern, context)` — so it is not the missing rule set. The date half of §3.10 IS bound, at `cli._rule_stage`. |
| `facts.states.is_stronger` | The ladder comparison. `cli.py:660`'s `contradicts_stronger` re-implements the one comparison it needs against `normalize_for_model`; `is_stronger` is the general predicate and nothing needs the general form. |
| `facts.values.set_display_label` vs `facts.plan_versions.set_display_label` | Two functions with one name, deliberately: the version-independent default and the per-plan-version rendering. Both are dormant for §9's Find cause; recorded together so nobody "fixes" the duplicate name. |
| `facts.plan_versions.create_plan_version_tables` | Its own docstring: "**NO LONGER OWED.** `facts.schema.create_facts_schema` now creates this table." See §11. |
| `questions.triggers.question_for_situation` | §13's third consequence and `68` F6's real measured cost — Priya files her teaching as coursework because `--situation` takes one string for a whole disk. The function refuses fewer than two situations, and **nothing in the product decides which situations fire on a branch**: `shipped_situations` is read by `--list-situations` and by nothing else. Wiring it would mean inventing a per-branch situation detector. That detector is the thing to build. |
| `questions.proposal.SelfDescriptionSending`, `sending_notice` | `80` §8's suspension, which is an opt-in to SEND. There is nothing to send to. The moment a transport exists these are the first things that should be wired, because C2 requires the notice on the line before the send. |
| `questions.effects.draft_for_answer_change` | See §8.3. |
| `grouping.acceptance.membership_review_state_as_of`, `grouping.failure_points.*`, `grouping.store.*` | §9's causes six and seven. `record_failure` in particular is explicit that P9 does not emit the `llm_interpretation` stage for a failure "that stage measures the model call, P8 makes the call" — so it is transport-gated twice over. |

---

## 11. Flagged for deletion (4)

Not deleted here. Each is flagged for the owner of its package, the way §4.3 flagged
`placement.store.placed_node_ids`.

| Symbol | Why |
|---|---|
| `extractors.events.extraction_event`, `extractors.events.ocr_event` | The module header already establishes that nothing in `src/` calls either and that P4's `record_run_event` builds its own payload. The one stated reason to keep them — "the guard that P5 authors none of P3's event types" — is a property a test asserts, not a `src/` symbol. The header also records that `ocr_event()`'s claim "to describe a shape the database will produce" is FALSE today, since `record_run_event` leaves `prompt_fingerprint` NULL. A payload builder that describes a payload nothing builds is the definition of surplus. **For P5's owner.** |
| `facts.plan_versions.create_plan_version_tables` | "NO LONGER OWED" by its own docstring; `create_facts_schema` creates the table. **For P6's owner.** |
| `facts.usable.create_fact_passes` | The weaker sibling of the row above: same redundancy, but it carries a stated reason to survive ("a test that wants the one table without the rest"). Listed so the two are decided together; if that test does not exist, this goes with the row above. **For P6's owner.** |

---

## 12. Instrument artifact — NOT unreachable (1)

`facts.learning.is_suppressed` **is called on every live run**, at
`facts/direct.py:188`, inside `direct_facts`, which is `cli._direct_stage`. The census
misses it because `direct.py:63` imports it as `_is_suppressed` and the census
matches READ NAMES against symbol names (`_references_and_imports`, which collects
`ast.Name` in a Load context). The alias is a different name.

**Measured: exactly one symbol in the whole population is affected.** An AST pass over
every `ImportFrom`/`Import` with an `asname` whose target is in the unreachable set
returns this and nothing else, so the class is real but tiny and the 401 is
overstated by one. Recorded here and in §13 so nobody spends an afternoon on it.

---

## 13. Traps, continued from §6

5. **It matches read NAMES, so an aliased import hides a live call.** `from x import
   f as _f` makes `f` look unreachable. One occurrence today (§12). This is the
   opposite direction from §6.2's over-statement, and it is the more dangerous one,
   because "unreachable" was supposed to be the safe verdict.
6. **A test on the live path is not the live path.** `extraction_stage_output` is
   exercised by `tests/integration/test_live_path.py`, whose name says the opposite
   of what it proves about reachability. Read the CALL, not the test's name.
7. **CLOSED, `5e0f835`. The instrument that underwrites "no model transport is
   wired" could be evaded and nothing checked.** §3's first cause and §9's sixth
   are both the claim that nothing in `src/` transports, and that rested on a scan
   for modules DECLARING `IS_MODEL_TRANSPORT` — a module calling a client's
   `invoke` without setting the flag was invisible to it. The role-matcher agent
   raised it and closed it repo-wide: `tests/integration/test_single_egress.py`,
   four rules over every module in `src/` (exactly one declarer; `.invoke(...)`
   only where the flag is declared; a network reaches `src/` only through
   `readers/model_*.py`; `src/questions/` may not even name a client), each proven
   by sabotage. Every transport-gated verdict in §10 may now cite it.
   **One limit to carry:** its network rule is a NAMED list of client modules, so
   an SDK nobody has used yet is not on it; the `.invoke` rule is what covers the
   gap meanwhile.

8. **A guard can be written in a lexer that cannot see the hazard it names.**
   `c17c76a` fixed a `--answer` line that a shell would act on as a redirect, and
   `tests/p15/test_p15_typable.py` read that line back with `shlex.split` — which
   has no opinion about `>` at all: `shlex.split("--answer q=a>b")` returns one
   happy token. The test called itself "survives a shell" and could not detect a
   redirect. It went red on the unquoted case only because its fixture ALSO had a
   space in the question id, and the space is the louder of the two hazards, so
   the quieter one was never tested. Modelling a shell takes
   `shlex.shlex(line, posix=True, punctuation_chars=True)` with
   `whitespace_split=True`. Raised by the role-matcher agent, who hit the identical
   hole in `role_report`'s three renders (`061cfff`); measured here by sabotage —
   with the quoting removed, reverting the lexer turns the redirect test GREEN on
   the live defect. **Fixed in this file's own guard; `tests/test_cli.py:1740` and
   `:2553` still read the REPORT's `--answer` and `--send-set` lines with
   `shlex.split`, masked the same way by a deliberate `--label "Legal Matters"`.
   The code they guard is correct today, so this is a weak guard rather than a
   live defect — for that file's owner.**

9. **The three verdicts do not cover "the owner has not chosen a number yet."**
   `bounded_sessions` and `photo_events` are not dormant in the sense §2 means — the
   producers exist, the tests pass, and the only thing missing is three numbers a
   person has to decide. Calling that "correctly dormant" files an owner decision as
   an engineering verdict. It is recorded as dormant in §10 with the reason stated,
   and raised as an owner item in §14.

---

## 14. Open, for whoever picks this up

- **NEW OWNER ITEM. Two of P6's own done-means criteria are blocked on three
  deferred numbers.** Done-means 25 (`bounded_sessions`) needs a session window, a
  same-folder rule and a minimum member count; Done-means 26 (`photo_events`) needs a
  time window, a GPS radius, a camera-identity test and a minimum member count. Both
  are built and tested. `84` §3's outstanding list does not carry them and should:
  they are the same KIND of item as `74` §8's Q3/Q5/Q6, and they are cheaper, because
  each is a number rather than a vocabulary.
- **§8.6's count line is half-wired.** PATCH A prints P3's four counters.
  `extractors.budgets.extraction_counts` — "89 scanned PDFs deferred; 18 files remain
  unreadable" — still has no surface, and wiring it needs P4 to publish a
  corpus-wide run reader. Writing that `SELECT` in `cli.py` would put P4's schema in
  the composition root. **For P4's or P5's owner: publish the reader, and PATCH A's
  block is where it goes.**
- **The four §1.1 rules should be reported by one mechanism, not two.** PATCH A adds
  a second block deliberately — a protected container is never openable by any
  gesture, and a folder excluded by name is a rule this product chose — but the two
  blocks now read the same table through two readers (`upstream.protected_areas` and
  `summary.set_aside_paths`), filtered on complementary halves of one column. That is
  fine and it is also exactly the shape that drifts. Worth a look when P3 next moves.
- ~~Generalise `test_p15_no_second_egress.py` to all of `src/`.~~ **Done,
  `5e0f835`** — see §13.7, including the one limit its network rule carries.
- **Two guards in `tests/test_cli.py` cannot fail for the hazard they name**
  (§13.8), at `:1740` and `:2553`. Not edited here: that file had another agent's
  traffic on it, and the code it guards is correct, so nothing is broken today.
- **`questions.triggers.question_for_situation` is waiting on a detector nobody has
  started.** It is `68` F6's measured defect — the graduate student who also teaches,
  filing her teaching as coursework — and it is the one entry in §10 whose fix is a
  new producer rather than a call. If P15 gets more time, this is where it goes.
