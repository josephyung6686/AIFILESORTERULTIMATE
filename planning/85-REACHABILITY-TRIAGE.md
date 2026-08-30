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
