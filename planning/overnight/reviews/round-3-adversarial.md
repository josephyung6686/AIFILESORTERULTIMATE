# Round 3 — adversarial

Date: 2026-08-21 (overnight)
Lens: **where will P6 and P7 reproduce the eight defect classes this project keeps shipping?**
Subjects: [`P6 PLAN-SKELETON.md`](../../parts/P6-facts-facets/PLAN-SKELETON.md) ·
[`P7 PLAN-SKELETON.md`](../../parts/P7-privacy-consent-gate/PLAN-SKELETON.md)
Checklist: [`_ROUNDS.md`](_ROUNDS.md) · not re-reported: [`round-1-fidelity.md`](round-1-fidelity.md)
(round 2 had not been written when this pass ran).

Everything marked CONFIRMED was **executed** against live `src/`, this pass. Nothing in `src/` or
`tests/` was modified: three probe files were written under `tests/wave2/`, run, and deleted;
`git status` is clean of them. Two `planning/` files were being edited by other agents while this
ran — findings cite the P6 skeleton as read at 03:20.

---

## Verdict

**The class most likely to ship is class 4 — a dead path — and it ships from P6 Task 19, wearing the
costume of the fix.** Task 19's whole argument is that raising `FactPassNotRun` is the only option
that *"makes a wrong call sequence a failing test rather than a silent behaviour."* Against the
caller as built, that is false. `src/orchestrator.py:153` is a blanket `except Exception` that maps
any exception out of `extract()` to a `completeness = failed` run; `FactPassNotRun` is not one of the
two refusals it re-raises. Executed, on the repo's own Wave-2 corpus fixture: the raising verdict
does not surface, the scan completes, the bundle seals, and `pdf.text / native` is written
`failed`, `failure_reason = "FactPassNotRun: no recorded P6 deterministic pass for this content
hash"`. Task 26's stated acceptance test — *"injecting a verdict that raises `FactPassNotRun` and
running a full corpus without it firing"* — **passes**, because from `run_wave2`'s vantage nothing
fired. The guard is green and inert, which is §2.7's OCR route exactly: a branch that no real input
reaches, proven by a test that synthesised the only input that reaches it.

It gets worse downstream rather than better. `failed` is one of the `completeness` values P7 Task 3
maps to `unreadable_unclassified`, and `unreadable_unclassified` is `Denied(unclassified)`. So the
chain P6 Task 19 → orchestrator catcher → `failed` → P7 Task 3 → gate denial ends with **the privacy
gate refusing every text-bearing PDF in the corpus while the scan reports success.** One defect,
both plans, no failing test anywhere along it.

Second most likely, and the one with a live corpus behind it today: class 8, in the form the project
already paid for once. `observation_keys_for_run` was changed from uuid4 order to `rowid` order
specifically because `record_sensitivity_signals` indexes into it positionally. The consumer is now
handed **a different run's key list**, so the ordering fix did not close the defect — executed below.
P7's ninth always-local item reads the table that defect writes.

Neither plan is careless. Both are unusually alert to seven of the eight classes and say so in their
own words. The failures below are almost all of one kind: **a guard whose instrument cannot see the
thing it forbids**, and **a branch specified against a shape the substrate does not produce.**

---

## Findings, by expected damage

### A1 (CRITICAL · class 4, and a refusal that silently succeeds) — `FactPassNotRun` becomes `completeness = failed`, and the guard's own test passes

**Where:** P6 Task 19 (`PLAN-SKELETON.md:1016-1035`, *"Why raise rather than default"*), P6 Task 26
(`:1222-1224`). **Substrate:** `src/orchestrator.py:145-158`.

**The failing case, executed.** The repo's Wave-2 corpus fixture (`syllabus.pdf`, text-bearing;
`notes.md`) run through `run_wave2` with `no_usable_facts` = a callable that raises, i.e. exactly what
Task 26 says loop 1 injects:

```
RUN: ('filesystem.record', 'filesystem', 'complete', None)
RUN: ('text.structured',   'native',     'complete', None)
RUN: ('filesystem.record', 'filesystem', 'complete', None)
RUN: ('pdf.text',          'native',     'failed',
      'FactPassNotRun: no recorded P6 deterministic pass for this content hash')
scan completed, bundle: True
```

`src/orchestrator.py:151-158`:

```python
    except (ProtectedContainerRefused, DatalessRefused):
        raise
    except Exception as error:                       # noqa: BLE001 -- see docstring
        return (failed_result(...),), ()
```

The catcher is correct for its own purpose (join-break 3, closed 2026-08-21) and its docstring is
explicit that *"a reader that raises becomes one `failed` run rather than the end of the scan."*
`FactPassNotRun` is not a reader failure and is not exempted.

**Why it is not caught by the plan's own test.** Task 26 asserts the guard by *"running a full corpus
without it firing."* Nothing escapes `run_wave2`, so the assertion holds while the guard is being
swallowed on every file. Verified by execution: consults happen (spy: `CONSULTS: 1` on the two-file
fixture — `text_layer_state` consults for **every** PDF with non-empty text,
`src/extractors/ocr_policy.py`), and the raising verdict produced no exception at the call site.

**Blast radius.** `set_extraction_status` writes `native: failed` for every text-bearing PDF. §8.6's
progress line reports them unreadable. P7 Task 3 maps `failed` toward `unreadable_unclassified`
(round 1 F-9 already flags that the mapping table has no design source; this is what makes the
mapping load-bearing). §8.4 makes classification a precondition of escalation, so the gate returns
`Denied(unclassified)` for the whole document corpus.

**Status:** CONFIRMED — executed against live `src/`, output above.

**Smallest change that prevents it.** Two lines, both required:
1. `_extract_one` re-raises `FactPassNotRun` beside the two admit refusals — a control-flow signal
   from a downstream part is not a reader failure, and this is the same distinction the docstring
   already draws.
2. Loop 1 must not hand `extract()` a verdict at all. The honest shape is a sentinel the dispatcher
   never consults — disable the OCR branch structurally for pass 1 rather than arm a landmine inside
   it. As written, "the branch cannot fire early" is implemented as "the branch raises", and the two
   are not the same thing when a catcher stands between them.

Note for the plan text: Task 19's decision criterion (*"makes a wrong outcome impossible rather than
merely unlikely"*) argues for raising against a caller that propagates. Against this caller, raising
is the **more** silent of the two options — `False` at least leaves the run `complete`.

---

### A2 (CRITICAL · class 8 + class 6) — the sensitivity signal is keyed to the filesystem run's observations, and P7's ninth always-local rule reads that table

**Where:** `src/orchestrator.py:189` and `:245-259`; consumed by P7 Task 3 (`:612-614`), Task 7
(`:727`, and the negative-test row *"raw sensitive values … the value set comes from P5's
`extraction_sensitivity_signal`, not from a P7 rule"*, `:1207`).

**The failing case, executed.** A `contacts.vcf` whose long-tail reader yields one address value,
run through `run_wave2`:

```
=== extraction_sensitivity_signal rows ===
  run 0d97df93… | key sha256:76cae9f4… | 'potentially sensitive'
signal run: ('filesystem.record', 'filesystem')
key names : [('contacts.vcf', 'filesystem.record', 'filesystem')]

=== all evidence rows ===
   ('filesystem.record', 'contacts.vcf',   'filesystem')
   ('filesystem.record', '/…/Documents',   'filesystem')
   ('filesystem.record', 'contacts.vcf',   'filesystem')
   ('filesystem.record', '.vcf',           'filesystem')
   ('filesystem.record', 'text/vcard',     'filesystem')
   ('text.structured',   'prof@wustl.edu', 'contacts')     <-- the sensitive value
```

The §2.9 flag lands on the **filename**. The email address is unflagged.

**Mechanism.** `results = [extract_filesystem(...)]` is index 0 (`orchestrator.py:189`); `routed` —
the long-tail results that raised the signals — are appended after. The write loop attaches the whole
`signals` tuple to the first result with observations, and `extract_filesystem` always has some (O5
re-emits P3's row). `SensitivitySignal.observation_index` is *"the observation's position in the
batch"* — the **long-tail** batch — and is then used to index
`observation_keys_for_run(conn, filesystem_run_id)`.

**Second failure mode, also executed:** eight values instead of one →

```
IndexError: signal at batch position 5 has no key: P4 assigned 5 for run 99ecc3ef…
  at src/orchestrator.py:256
```

Uncaught — the `try` covers only `_extract_one`. A real macOS contacts export has hundreds of values.
**This kills the scan.**

**Why no test sees it.** `tests/wave2/test_wave2_orchestrator.py:388` reads, in its own words:
*"If E3 raised nothing for this fixture the table is legitimately empty — so assert the mechanism,
not a count"*, then `for row in rows: assert row["observation_key"]`. Vacuous on an empty table, and
green on a wrong key.

**Consequence for P7, which is why it is in this review.** Task 7 makes *"raw sensitive values"*
unconstructible **by reading this table**. Given the rows above, the gate would refuse a `Filename`
item for `contacts.vcf` (right refusal, wrong reason) and would **permit** an `Excerpt` naming the
observation key of `prof@wustl.edu`, because that key carries no signal. §8.4's ninth always-local
item is enforced against the wrong observation on every real file.

**Status:** CONFIRMED — both outcomes executed against live `src/`.

**Smallest change that prevents it.** Attach signals to the run they were emitted from, not to the
first run with observations: `_extract_one` should return `(results, signals)` paired per result, or
`Dispatched` should carry the signals on the routed result. And the wave2 test must assert a **count
and a key identity** (`the flagged key resolves to an observation whose raw_value is the address`),
not the existence of a column.

---

### A3 (HIGH · class 4, gate hole) — `Gate.release` cannot name the thing it classifies: no `content_hash`, and no group expansion

**Where:** P7 Task 11 `ModelCallRequest` (`:842-845`), SPEC §6 (`SPEC.md:224-233`), classification
record keyed `(file_id, content_hash)` (SPEC §2, P7 Task 3 `:615`).

Two holes in one shape.

**(a) `target = { file_ids[], group_id? }` and nothing expands a group.** No task in P7 takes a
`members_of(group_id)` callable; P9 does not exist; the Contract-in table has no row for it. A
`ModelCallRequest` whose target is `{file_ids: [], group_id: "g-1"}` presents the classification loop
with an empty list. Every per-file check — `unclassified`, `protected_cloud_target`,
`protected_records_template` — iterates nothing and passes. `Released`. That is a refusal that
silently succeeds, at the door, and §4.4/§7.7 group dossiers are exactly what the request shape was
widened for.

**(b) No `content_hash` anywhere in the request.** The classification is per file *version*; the
excerpt is addressed by `observation_key`, which **contains** a content hash by construction. Nothing
requires the two to be the same version. A file re-extracted after a reclassification releases text
from version A under version B's handling class. `Denied(unclassified)` is also unreachable for the
common case if the gate resolves the class from `files.content_hash` (always current) while the item
cites an older one.

**Status:** PLAUSIBLE for (b) — it depends on a resolution rule no task states, which is the finding.
CONFIRMED for (a) as a gap: `ModelCallRequest`'s seven fields and every Interfaces block in Tasks
2–22 were read; no group-member source exists.

**Smallest change.** Task 11 states the expansion rule and the version rule explicitly: `group_id`
requires an injected `members_of` with no default and a non-empty result, and the gate derives
`content_hash` **from the requested items' observation keys**, denying a request whose items span two
content hashes for one file. One sentence each; both are currently unwritten.

---

### A4 (HIGH · class 4) — P7 Task 9's "current, non-superseded row" rule is inverted: it is dead where it was written for, and fires where it must not

**Where:** P7 Task 9 (`:790-793`), the Contract-in note on `observations_by_key` (`:349-353`), and
SPEC-vs-code item 8 (`:1325-1326`).

The plan's rule: *"`observations_by_key` returning two rows … resolves to the current, non-superseded
row, and an unresolvable ambiguity raises rather than picking the first."*

**Executed against live P4:**

```
keys equal:            True          # same content_hash · extractor_name · locator · raw_value
rows under one key:    2
  (obs-A, extractor_version 1.0.0, supersedes=None, superseded_by=None)
  (obs-B, extractor_version 2.0.0, supersedes=None, superseded_by=None)
both non-superseded:   True
```

And from P4's own suite (`tests/p4/test_p4_supersession.py:130-141`), a **superseded** observation:

```python
assert old_key != new_key
assert len(observations_by_key(p4_conn, old_key)) == 1
```

The two cases are disjoint, and the plan's rule is written for a case that does not exist:

- **Two rows on one key ⇒ two non-superseded rows.** The filter selects both. So the branch the plan
  calls "the ambiguity" is not an edge case — it is the *only* multi-row case, and it is the ordinary
  state of a corpus after an extractor upgrade, which is the exact state MINOR 8 built the key to
  survive (§8.7: a citation recorded today still resolves). Task 9 as written raises
  `AmbiguousObservationKey`, and **the gate stops resolving every excerpt in the corpus the day an
  extractor version is bumped.**
- **A superseded observation has a different key** (the key hashes `raw_value`; a corrected value is a
  new key), so it is alone under its key and the "non-superseded" filter has nothing to do. Dead.

**Status:** CONFIRMED — both halves executed / read from P4's asserted behaviour.

**Smallest change.** The selection rule is not "non-superseded" — it is **highest
`extractor_version`, tie-broken by `observation_id`**, and the plan should say so and say why: rows
under one key are the *same value* read by two versions, so any of them materialises the same text and
the choice is about provenance, not content. Reserve the raise for a genuinely different `raw_value`
under one key, which cannot happen and is therefore an integrity assertion, not a branch.

*(Related, LOW: `database_agent.supersede.chain` and `evidence_shape.store.supersede_chain` both
promise "the full supersede chain, oldest first" and in fact walk **forward from the id passed**.
Called with the newest row's id they return a one-element list — "no supersession" — which is how a
Task 9 implementation would most naturally ask the question.)*

---

### A5 (HIGH · class 4 + class 5) — `Denied(protected_records_template)` has no input surface anywhere in P7

**Where:** P7 Task 13 Interfaces (`:899-903`), negative-test row (`:1213`), coverage row 6 (`:1171`),
SPEC §7.3 rows.

Task 13 consumes `vocabulary.DENIAL_REASONS`, `classification`, `policy`, `items`,
`audit.append_audit`, `database_agent.budget.get_ceiling`. **None of them can answer "is this file
held under the `Protected Records` residual template."** P7's SPEC Contract-in has no P10 or P11 row
supplying a template assignment — its P10 row runs the other way (*"populated from P7's policy"*), and
its own Held-elsewhere note says *"P7 publishes the denial; P11 consumes it."* P11 does not exist and
is not injected.

So one of the eight denials is reachable only by a fixture that hands the gate a fact no code path
can produce — and Task 20 requires *"at least one fixture per `Denied.reason` — eight"*, so the
fixture will exist and be green. This is §2.7's OCR route with a different name.

**Status:** CONFIRMED — every Interfaces block in Tasks 1–22 read; no template source in any of them.

**Smallest change.** Task 13 takes an injected `residual_template_for(file_id) -> str | None` with no
default, exactly as Task 4 injects `SensitivityStateWriter` for the same reason, and the plan reports
that P11 owns it. A denial with no input is not a denial.

---

### A6 (HIGH · class 7) — both plans replace the banned source-text scan with `vars(module)` introspection, which cannot see most of what they ask it to forbid

**Where:** P6 Global Constraints (`:101-103`), Task 1 (`:555-557`), Task 7 (`:709-711`), Task 16
(`:928-929`), Task 18 (`:982-983`), Task 19 (`:1006-1008`), Task 25 (`:1175-1184`). P7 Global
Constraints (`:199-205`), Task 6 (`:711-715`), Task 21 (`:1120-1132`), coverage note (`:1180-1187`).

Both plans correctly ban the source-text scan and both name the reason. Both then specify the
replacement as *"runtime introspection of `vars(module)`"* / *"module-level constants"*. Executed
demonstration — a module importing real `evidence_shape`:

```python
from evidence_shape import store                      # binds `store`, not `raw_value_at`
def resolve_default_policy(stored, *, mode="hybrid"): # a default in a signature
    threshold = 0.85                                  # a threshold in a body
def materialise(conn, run_id, path, span):
    unit = store.text_unit_at(conn, run_id, path)     # a P4 materialiser
    return tu.raw_value_at(unit, span)
def branch(obs):
    if obs.source_type == "image": ...                # a branch on source_type
```

```
--- vars(module) guard, as both plans specify it ---
binds a P4 materialiser by name?   False
module-level str constants:        {}
module-level numeric constants:    {}
a mapping keyed by a source_type?  False
=> vars() guard verdict: CLEAN
--- ast walk over the same file ---
materialisers reached by attribute: ['raw_value_at', 'text_unit_at']
numeric literals in bodies:         [0.85, 0.85]
mode/source_type literals:          ['hybrid', 'image']
=> ast verdict: DIRTY
```

Obligations that are **unenforceable by the instrument the plan names**, each of which will therefore
be implemented by someone reaching for `read_text()` — which is the defect the ban exists to prevent,
now with a plan sentence authorising the reach:

| Plan | Obligation | Why `vars()` cannot see it |
|---|---|---|
| P6 Task 1 `:556` | *"the absence of any string literal spelling a state name anywhere else in `facts`"* | literals live in function bodies |
| P6 Task 7 `:709`, Task 25 `:1184` | *"no module branches on `source_type` or `extractor_name`"* | a branch is a statement; only a module-level dict is visible |
| P6 Task 16 `:928` | no `media type` candidate derived from a `text_unit` length | call-site property |
| P6 Task 18 `:982` | `preferred` read in none of three call paths | call-site property |
| P6 Task 19 `:1006` | *"no read of a `text_unit` anywhere in the module"* | attribute access on an imported module is invisible |
| P7 Task 6 `:711` | **no path yields a default of `hybrid`/`cloud_assisted`** | the most likely home is a signature default or a body literal |
| P7 Task 21 `:1130` | **L2: the set of packages *binding* a materialiser is `{evidence_shape, extractors, privacy}`** | `import evidence_shape.store as store` binds `store` |

P7's Task 6 case is the sharpest: Done-means 12's negative half is the safety-critical assertion in
the part, the plan explicitly *strengthens* the SPEC's "by grep" to introspection and flags it for the
reviewer — and the strengthened instrument is blind to the two most likely hiding places.

**Status:** CONFIRMED — executed, output above.

**Smallest change.** Both plans already name the right tool: `code_tokens()` in
`tests/p3/test_p3_no_invention.py`, which walks the AST and excludes docstrings — P7's Global
Constraints cite it and then neither Task 6 nor Task 21 uses it; P6's plan never mentions it. Every
row above becomes an AST assertion over the package's files (`ast.walk` for `ast.Attribute`,
`ast.Constant`, `ast.Compare`), with `vars()` kept only for the module-level-constant half where it is
genuinely sufficient. This is one shared helper, written once, imported by both `test_p6_no_invention`
and `test_p7_no_invention`.

---

### A7 (HIGH · class 3) — B7's "`privacy_withheld` is not an abstention" reached the `unresolved` table and not the §8.5 outcome table

**Where:** P6 Task 5 (`:659-660`, `NOT_ABSTENTIONS = {budget_deferred, privacy_withheld}`) vs P6
Task 21 (`:1078-1080`, *"every attempted field ended in a non-budget `unresolved` → `abstained`"*).
Both are faithful to the SPEC, which contradicts itself: `SPEC.md:360-366` rule 4 —
*"`budget_deferred` and `privacy_withheld` are **not** abstentions"* — against `SPEC.md:611` —
*"every attempted field ended in an `unresolved` row with a **non-budget** reason | `abstained`."*

**The failing case.** A file under a handling class that forbids the model route. Every LLM-only field
gets `privacy_withheld`. Task 21 maps the stage to `abstained` / `within_ceiling`. §8.5's Fact-quality
question — *"Did it abstain when evidence was absent?"* — is answered **yes** about a field whose
evidence was never examined. That is §8.6's named prohibition verbatim: deferred work reported as
*"understood and found unimportant."*

**Why nothing catches it.** P2's `record_stage_output` enforces only the budget pairing
(`deferred` ⇔ `ceiling_reached`). It has no view of `privacy_withheld`, so the plan's strongest
claim — *"provable end-to-end through the live writer"* — is true of the half that was already safe.

**Status:** CONFIRMED — both SPEC lines read; both plan tasks read; P2's writer's two raises read.

**Smallest change.** Task 21's mapping excludes **`NOT_ABSTENTIONS`**, not "budget". A stage whose
fields all ended `privacy_withheld` is `deferred`; P2's writer will then demand
`budget_state = ceiling_reached`, which is wrong, so this needs one line in the plan saying which
outcome a privacy stop carries — and that is a real question, not a typo. It belongs in NEEDS JOSEPH.

---

### A8 (HIGH · class 4) — six of the thirteen `unresolved` reasons are unreachable in the shipping configuration, and the one reason that configuration needs does not exist

**Where:** P6 Task 5 (`:645`), the SPEC's reason table (`SPEC.md:344-357`), Done-means 17
(`:1280`), the P8 seam row (`:434`).

The thirteen, sorted by what can reach them with **P8 absent** — which is Wave 2, and which Done-means
17 makes the shipping assertion:

| Reachable deterministically | Reachable only from a hand-authored `Verdict` |
|---|---|
| `no_candidate_evidence`, `below_score_threshold`, `below_margin`, `context_check_failed`, `context_truncated`, `discounted_tool_metadata`, `budget_deferred` | `field_not_in_active_schema`, `citation_absent_from_evidence`, `normalization_failed`, `contradicted_by_stronger_fact`, `model_returned_unknown`, **`privacy_withheld`** |

Done-means 17 is stated as *"items 4–10, 13–16 and 18–27 pass with P8 absent"* — quietly omitting 11
and 12, the LLM items. So the plan half-knows. What it does not price:

- **Task 17's five reasons will be green forever without proving anything about P8.** The tests
  construct `Verdict` objects by hand; nothing cross-checks that P8 can produce that shape. This is
  the §2.7 pattern with the synthesis moved into the test file, and it is the *right* device for
  building against an absent part — but the plan should name it as an obligation transferred to P8's
  Done-means, the way P7 Task 19 honestly does for its transport instrument.
- **`privacy_withheld` is worse than dead — it is ambiguous.** Its definition is *"P7's handling class
  forbids the model route."* With P8 absent, the LLM rung does not run at all. Does the resolver write
  `privacy_withheld` (a lie: no privacy decision was made), `budget_deferred` (a lie, and P2's writer
  will then force `ceiling_reached`, fabricating a §8.6 ceiling report), `no_candidate_evidence` (§8.6's
  named prohibition), or **nothing** (violating B7 and Done-means 18, *"every refusal … writes an
  `unresolved` row"*)? All four are wrong and the plan chooses none of them. Whichever a builder picks
  will be written once per unfillable field per file — a mass-produced abstention with the wrong name,
  which is the shape of the original `no_usable_facts` warning.

**Status:** CONFIRMED as a gap — the thirteen enumerated from the SPEC, each traced to its producer in
the plan's task list.

**Smallest change.** A fourteenth reason, `producer_unavailable` (or an explicit statement that a
route that was never attempted is absent from `attempted_producers[]` and writes no row, with
Done-means 18 amended to say "every refusal it **makes**"). One line, and it decides what P2 reports
about every deterministic-only deployment.

---

### A9 (MEDIUM-HIGH · class 1) — P6 injects a P7 surface at an arity P7 does not publish, and P7 publishes no such surface at all

**Where:** P6 `:433` — `handling_class(file_id) -> str`, *"resolved before any model request"*.
P7 `:422-427` — `SensitivityFacts.current(file_id, content_hash) -> ClassificationRecord | None`;
P7's Contract-out table (`:476-488`) lists `Gate.release`, `Gate.revoke`, `Gate.reclassify`,
`Gate.may_move_automatically`, `Gate.display_policy`, `Gate.summarize_protected`,
`transcription_authorized_for`, `consume_release`, `assert_single_egress`, the vocabularies and the
fixtures. **There is no per-file handling-class read on it.**

So: P6 injects a function P7 does not publish; the nearest P7 surface takes two arguments where P6
passes one; and the arrow in P7's own table runs the other way — `ClassificationRecord` → *"P6
(stores)"*, i.e. P7 expects P6 to hold the value P6 expects to ask P7 for. This is the
`config_fingerprint` shape before it was executed: two plans, written the same night, each internally
consistent, joining on a name.

The dropped argument is the dangerous half: a classification is bound to a file **version** (SPEC §2,
§8.2). A one-argument `handling_class(file_id)` cannot express that, so P6's privacy check and P7's
classification would key on different things the first time a file is re-extracted.

**Status:** CONFIRMED — both Contract tables read side by side.

**Smallest change.** One of the two plans wins and the other cites it. Recommended: P6 consumes
`SensitivityFacts.current(file_id, content_hash)` — P7's shape, already keyed correctly — and P7 adds
one row to its Contract-out table naming P6 as a consumer. It is a two-line edit in each plan and it
closes the largest remaining seam in the wave.

---

### A10 (MEDIUM-HIGH · class 1) — `mirror_state` gives `files.sensitivity_state` a writer, and then the ratified fix and its regression become the same edit

**Where:** P7 Task 4 (`:649-651`, `mirror_state(record) -> str`, `SensitivityStateWriter`), Task 22
(`:1152-1153`). **Substrate:** `src/orchestrator.py:305-311`, which now reads:

```python
                       # §8.4's, and P7 is unbuilt. This passed P1's
                       # `sensitivity_state` -- a DIFFERENT field on a different
                       # record. Both are NULL on a live scan, so nothing failed and
                       # the name was still wrong: one concept wearing two names one
                       # column apart. The honest value is None because the class is
                       # unknown, not because another column happened to be empty.
                       handling_class=None,
```

Round 1 F-7 caught that P7's citations to this line are stale and that Task 22 asserts a change no
task makes. This finding is the part that is not a citation error: **once `mirror_state` exists, the
pre-fix line becomes green.** Task 22 asserts only *"the Wave-2 bundle's `handling_class` is
non-null"*, and `handling_class = file_row["sensitivity_state"]` satisfies that assertion perfectly —
it is the shortest edit that makes the test pass, it restores exactly the line the 2026-08-21 pass
removed, and it will be indistinguishable from correct because both columns are now populated.

Compounding it: **the plan never states what vocabulary `files.sensitivity_state` holds.**
`mirror_state` is a *mapper*, which implies the target is not the five handling classes — otherwise it
would be an identity. If it is not, then a bundle fed from that column carries a fourth spelling of
the concept the connection contract §3 already calls *"the exact defect class that has cost this
project the most."*

**Status:** CONFIRMED as a plan-level hazard; the orchestrator line and the two P7 tasks read.

**Smallest change.** Task 4 states the target vocabulary in one sentence (recommended: identity —
`files.sensitivity_state` holds a `HANDLING_CLASSES` member and `mirror_state` is a validator, not a
translator), and Task 22 asserts **the value**, not non-nullness: `bundle_file_entry.handling_class ==
gate.classification(file).handling_class`. A non-null assertion cannot tell the two columns apart,
which is precisely how the previous instance survived.

---

### A11 (MEDIUM · class 5 + class 3) — `display_label` has two homes and one of them has no writer

**Where:** P6 Task 3 (`:595-597`, `ValueRow(..., display_label, aliases, ...)`; `ensure_value` takes
no `display_label`) vs Task 23 (`:1119-1122`, `PLAN_VERSIONED = ("display_label", "aliases")`,
`set_display_label(conn, *, value_id, plan_version, label)`).

Task 3's test requires *"`display_label` is `UChicago`"* on the `values` row. Task 23's test requires
that the display label **is** plan-versioned while *"the underlying value and every fact pointing at
it"* are shared (§8.8). Both cannot be true of one column: a column on `values` is shared across plan
versions by construction, which is the §8.8 violation Task 23 exists to prevent; if the real store is
plan-versioned, the `values.display_label` column has no writer and Task 3's assertion is testing a
field nothing fills in production.

**Status:** CONFIRMED as an internal contradiction between two tasks in the same plan.

**Smallest change.** `values` carries `canonical_value` and `raw_variants` only; `display_label` and
`aliases` live in Task 23's plan-versioned table from the start, and Task 3's test reads them through
`display_label(conn, value_id, plan_version)`. Delete the two columns from `ValueRow`.

---

### A12 (MEDIUM · class 8) — two published sequences with order-dependent consumers and no stated order

**(a) `passes_for(conn, *, file_id, content_hash) -> tuple[frozenset[str], ...]`** — P6 Task 19
(`:996`), consumed by Task 26's termination condition (`:1229-1230`): *"a file whose OCR pass also
produced nothing is not OCRed a second time … read from the pass record."* Answering that requires
either a **union** over the tuple or **the last element**. The plan says neither, and the underlying
query is not specified to order. If a builder writes `passes_for(...)[-1]` — the natural reading of
"has the latest pass covered `ocr`" — the termination condition is decided by SQLite row order, and
`observation_keys_for_run` is the precedent for what that costs. A union is order-free and correct;
say so.

**(b) `values.first_evidence_ref`** — P6 Task 3 (`:597`), *"a `first_evidence_ref` that is an
observation key"*. "First" is defined by the order producers iterate P4's reads, which the plan's own
Global Constraints (`:194-204`) establish is **insertion order and not a property of the corpus** —
verified by execution in the plan itself. Task 11's shuffle test covers `rank` only. So the same
corpus written in a different run order stores a different `first_evidence_ref`, and §8.5's replay
compares a bundle against itself and reports a difference.

**Status:** PLAUSIBLE for both — each is an unstated ordering with a consumer that needs one.

**Smallest change.** Task 19 states that the verdict and the termination check read the **union** of
`passes_for`, and `passes_for` is documented as a set-valued read with no order. Task 3 defines
`first_evidence_ref` as `min(observation_key)` over the candidate set, and Task 11's shuffle test is
extended to cover `ensure_value` — the sort-before-you-decide rule the plan already states, applied to
the one place it currently is not.

---

### A13 (MEDIUM · class 2) — `basis_key` has two independent serializers, a third writer that does not exist, and a failure mode that is silently permissive

**Where:** P6 Task 22 (`:1093`, `basis_key(*, file_id, field_key, value_id)`, *"serialized in one
place, canonically"*); P7 Task 16 (`:985`, `basis_key_for(file_id, handling_class)`, *"a
canonical-JSON encoding P7 composes"*). `10-i4-learning-ops.md` fixes the **tuples**
(`fact` → `(file_id, field, value_id)`, author P6; `privacy` → `(file_id, handling_class)`, author P7)
and says P1 *"stores all three opaquely."* Confirmed live: `CORRECTION_FIELDS` has one `basis_key`
TEXT column and `learning_records` filters on neither `proposal_class` nor `basis_key`.

Nothing fixes the **encoding**. `json.dumps(["f-1","course","v-9"])`,
`canonical_json({"file_id": ..., "field": ..., "value_id": ...})` and `"f-1|course|v-9"` are three
different strings for one basis, and the writer and the reader are not guaranteed to be the same part:
P13's `review_action` with `action = mark_private` is listed in P7's Contract-in as **"P6+P7
jointly"**, and I4 assigns authorship of the event to *"the acting part"* without saying which part
that is when the gesture is collected by P13.

**The failure mode is the dangerous half.** `is_suppressed` / `suppressed` return **False** when the
query matches nothing. A mis-encoded key does not error — it silently re-proposes a claim the user
rejected, forever, which is the one thing §8.7 exists to prevent. And no test can catch it, because
each part's test writes and reads through its own encoder.

**Status:** PLAUSIBLE, high damage. CONFIRMED that the encoding is unspecified in both plans and in
I4, and that `learning_records` returns rows the caller must match by string equality.

**Smallest change.** One serializer, owned by P1 beside the column it writes into:
`events.basis_key(proposal_class, **parts) -> str`, canonical JSON of a sorted mapping. Both plans
consume it. Failing that, the two plans must at minimum state the byte-level encoding, and each
part's test must include one case that composes the key on the *writer's* side and matches it on the
*reader's*.

---

### A14 (MEDIUM · class 5/6) — the audit record's `content_hashes` is plural and `events` has one `file_id`

**Where:** P7 preamble *"The audit record's home"* (`:284-300`), Task 10 (`:824-826`), Task 15
(`:962-965`). **Substrate, executed:**

```
EVENT_FIELDS ('event_type', 'file_id', 'content_hash', 'old_path', 'new_path', 'subsystem',
              'component_version', 'prompt_fingerprint', 'user_id', 'observed_at', 'explanation')
```

Singular, and MINOR 1 fixes the list at eleven forever. A group release covering twelve files writes
**one** `events` row. `content_hashes` and the target's `file_ids[]` go into the JSON `explanation`;
the native `file_id` column holds one of them, or NULL.

`audit_records_for(conn, *, file_id=...)` is specified as a native-column query (Task 10 `:814-815`).
It therefore **misses** every group release that included that file. The consumer is Task 15:
`RevocationResult.prior_releases`, which the plan itself calls *"what makes `retraction_limit`
truthful and specific rather than a generic disclaimer."* A user revoking consent for one file is told
their file was never sent, when it was — inside a twelve-file dossier.

**Status:** CONFIRMED — `EVENT_FIELDS` executed; both task texts read.

**Smallest change.** `audit_records_for(file_id=...)` must query the JSON, not the column:
`json_extract(explanation, '$.content_hashes')` / `'$.file_ids'` with a `LIKE` prefilter, and Task 10's
test must include a **group** release and assert it is returned for each member. Task 15's test needs
the same case, or Done-means 8's guarantee is proven only for single-file calls.

---

### A15 (MEDIUM · class 4, gate hole) — `assert_single_egress` proves the signature and never that the transport consumes the release

**Where:** P7 Task 19 (`:1063-1079`), the L1 claim (`:106-113`), Done-means 5 (`:1170`).

`Released` carries `materialised_items[]` — the post-redaction **values** (SPEC §6). The payload is in
the token. `consume_release` is a ledger write that happens *when the transport chooses to call it*.
`assert_single_egress` checks `inspect.signature(...).parameters` and each parameter's resolved
annotation. A transport with exactly one public function, one parameter, annotated `Released`, that
**never calls `consume_release`**, passes the checker, sends the payload, and can send it again — and
every replay is unaudited, because only the mint was recorded.

So the plan's strongest sentence — *"a call that bypasses P7 is not a policy violation to be caught in
review, it is a call that cannot be constructed"* — is true of *forging* a token and false of
*spending* one. The plan says L1 is *"entirely testable with no P8 in existence"*; the testable half is
the ledger's behaviour when it is asked, not that it is asked.

**Status:** CONFIRMED from Task 19's Produces list — nothing in it inspects a function body.

**Smallest change.** `assert_single_egress` additionally AST-walks the egress function and requires a
call to `consume_release` **before** any other call, and Task 19 adds a fifth non-conforming fixture:
a correctly-typed transport that never consumes. That fixture is the one that matters, and it is the
one currently missing.

---

### A16 (LOW · class 5) — columns with no named writer, beyond round 1 F-2's four

Round 1 found four universal `fields` rows with no producer. The same check applied to the other
tables both plans create:

| Column | Table | Named writer in the plan |
|---|---|---|
| `internal_score` | `file_facts` | none — Task 11 computes `Candidate.score` and `fill_or_abstain` returns `str \| None`; the score is dropped. OQ10's third option (*"defer to the internal score"*) needs it. |
| `cited_quote_refs[]` | `file_facts` | LLM path only — unwritten in every P8-absent run |
| `rejection_reason` | `file_facts` | none; Task 22 reads `rejected` rows and never writes the reason |
| `normalizer_id` | `fields` | none — Task 2 declares it, and *"per-field normalizers"* are Deferred and **injected at call time** (Tasks 3, 17), so the catalogue column points at nothing |
| `reliability_state` | `ClassificationRecord` | Task 16 writes `user_confirmed`; nothing states what a `basis = detector` classification carries |

Each is small on its own. Together they are §5 of the connection contract's standing rule — *"any part
added from here must carry a check that every column it publishes has a writer, or state plainly that
it does not yet"* — and **neither plan carries that check.** P6 Task 25 and P7 Task 21 are the natural
homes: one test that reads `PRAGMA table_info` for every table the part creates and asserts each column
is either written by a named function or listed in that part's Deferred table.

---

### A17 (LOW · class 3) — both plans edit `run_wave2`, and neither knows the other does

P6 Task 26 (`:1186-1198`) modifies `src/orchestrator.py`: removes the `no_usable_facts` parameter, adds
a `resolver` parameter, splits stage 2 into four loops. P7 Task 22 (`:1136-1153`) asserts a **change in
`run_wave2`'s behaviour** (`handling_class` non-null) while its Files list contains **only a test
file**. P7's plan never mentions that P6 rewrites the function; P6's plan never mentions that P7 needs
a `handling_class` source threaded through it.

P6's plan does say Task 26 *"is the one to schedule with the lead rather than around them."* That
instruction needs to appear in P7's plan too, and P7 Task 22 needs a line in its Files list — otherwise
the assertion is written against a caller nobody was asked to change, which is round 1 F-7's finding
arriving as a scheduling collision on the one shared file in the wave.

---

## Class-by-class table

| # | Class | P6 | P7 | What was checked |
|---|---|---|---|---|
| 1 | **Two vocabularies for one concept** | A9 (`handling_class` arity), A11 (`display_label` two homes) | A9, A10 (`mirror_state`'s unstated target vocabulary) | Every value either plan names was traced to an owner: `sensitivity`/`sensitivity status`/`sensitivity_state`/`handling_class` (already recorded, §3 of the connection contract — not re-reported), `observation_key`, `analysis_tier`, `content_hash`, `policy_version`, `prompt_fingerprint`, `cache_key` (P6 F11 handles), `field_key` spelling (round 1 F-14), `basis` vs `origin` (plan reports it), the four `protected` spellings (P7 Task 2 pins them — good). **New: `prompt_fingerprint` has four consumers and no owner** — P1's `events` column, P2's version-tuple axis, P6's `fact_cache_key`, P7's binding tuple — and no part computes it. It is the next `config_fingerprint` and neither plan claims it. |
| 2 | **Two computations for one value** | A13 (`basis_key`) | A13 | `fact_cache_key` vs `extractors.runs.cache_key` — P6 Task 6 asserts they differ and does not import P5's: **correct, no finding**. `observation_key` — P6 never recomputes, verified in Global Constraints: **correct**. `signal_tier`, `analysis_tier` — read from P4, never re-derived: **correct**. Redaction: `apply_redaction` (Task 8) is the only transform and `release.py` the only caller: **correct**. Audit digest: `canonical_json` from P4, one place: **correct**. |
| 3 | **A decision reaching one document and not another** | A7 (B7 vs the §8.5 outcome table), A17 | A7's mirror on the release side, A17 | C4 ("the gate raises and writes nothing") — P7's preamble §2 reconciles it explicitly and correctly. B5 (one log) — applied consistently. M8 (acting part authors) — both plans assert one `subsystem` write site. M1/§8.2 supersede-never-overwrite — both apply it. I4's basis-key tuples — both match. **The one that did not travel is B7's second half.** |
| 4 | **A dead path** | A1, A8 (six of thirteen reasons; the missing fourteenth) | A3(a), A4, A5, A15 | Every `unresolved` reason and every `Denied` reason was traced to a constructible input. Round 1 F-12 already has `always_local_item`; the same argument extends to `whole_document_requested` (Task 7 raises at construction, so `Gate.release` can never return it) — noted, not re-reported. `dossier_over_budget` is declared a backstop by the plan and is honestly labelled. `policy_revoked`, `mode_forbids_target`, `unclassified`, `protected_cloud_target` are all reachable. |
| 5 | **A column with no writer** | A11, A16 | A5 (a denial with no input is the same defect one level up), A16 | `PRAGMA`-shaped walk over every column both plans declare. Round 1 F-2's four universal fields not re-reported. `fields.multiplicity` is declared unanswered by the plan — honest, no finding. |
| 6 | **A value computed and dropped** | A16 (`internal_score`), A12(b) | A2 (the signal reaches the database keyed to the wrong observation — computed correctly and *mis*-delivered, which is worse than dropped), A14 | Traced every task's Produces to a consumer. `context_truncated` → Task 10's reason: consumed. `ResolveResult` → Task 21: consumed. `active_field_allowlist` → Task 17: consumed, and the plan explicitly makes it one computation. `RedactionManifest` → audit: consumed. `deferred_counts` has no named consumer (minor). |
| 7 | **Scanning text for a token** | A6 — seven obligations | A6 — two, one of them Done-means 12's negative half | Neither plan specifies a `read_text()` scan; both ban it by name. The defect has mutated: the *replacement* instrument is under-powered, and every obligation it cannot meet is an invitation to reach for the banned one. `code_tokens()` is the answer and is used by neither. |
| 8 | **A published order that is not an order** | A12(a) `passes_for`, A12(b) `first_evidence_ref` | A2 (the original defect, still live via a different run's key list), A4's `chain()` docstring | Checked every published sequence: P6 `rank` imposes a total order — **correct and well argued**; `evidence_chain`, `history`, `values_with_counts`, `facts_for` have no stated order but no order-sensitive consumer named; P7 `audit_records_for`, `prior_releases`, `SensitivityFacts.history` likewise; `learning_records` is `ORDER BY event_id DESC` — **correct**; `fixtures.by_number` is a dict lookup, not an index — **correct** in P4 and the pattern P7 Task 20 should copy. |

---

## The gate-hole attempt

§8.4: *"Privacy policy must be enforced before content reaches any model or external connector."*
Ten attacks on that sentence as the two plans build it. **Four succeeded.**

| # | Attack | Result |
|---|---|---|
| 1 | Hand-construct a `Released` with a fabricated `release_id` and hand it to the transport | **Blocked, conditionally.** `consume_release` raises `ReleaseNotIssued` — *if the transport calls it.* See #2. |
| 2 | Write a transport with the conforming signature (one public function, one `Released` parameter) that never calls `consume_release`, then feed it a hand-built `Released` | **HOLE (A15).** `assert_single_egress` inspects the signature only. Nothing in P7 requires the body to consume. Single-use and replay-failure are properties of a ledger nobody is required to consult. |
| 3 | Materialise text outside `privacy` by binding a P4 reader through a module alias — `from evidence_shape import store; store.text_unit_at(...)` | **HOLE (A6).** Executed: `vars(module)` shows `store`, not `text_unit_at`; L2's repo-wide guard passes. |
| 4 | Take the text from `extractors` instead of P4 — `ExtractionResult.text_units` in memory, or `extractors`' own materialisers | **HOLE (A6, scope).** L2's allowlist is `{evidence_shape, extractors, privacy}`. `extractors` is *inside* it, so anything built on P5's in-memory result never passes the gate and never trips the guard. The allowlist encodes who may *read*, and the property needed is who may *send*. |
| 5 | Send a group dossier: `target = {file_ids: [], group_id: "g-1"}` | **HOLE (A3a).** No task expands a group. The per-file checks iterate an empty list. `Released`. |
| 6 | Cite an excerpt whose `observation_key` embeds content hash A while the file's current classification is for hash B | **HOLE (A3b), unspecified.** No `content_hash` in `ModelCallRequest`; no task states the resolution rule. |
| 7 | Request an unclassified file under a **local** model target | Blocked-by-design and honestly open: Task 13's `unclassified` denial is parameterised on locality with **no default** (OQ5). A production wiring can open it, but only by an explicit choice someone must make. No hidden hole. |
| 8 | Request `Filename` for a protected file | Blocked (Task 7), though *whether* `filename` is releasable at all is round 1 F-5's finding, not re-reported. |
| 9 | Request an `Excerpt` covering the whole text unit | Blocked at construction (`WholeDocumentRequested`) — so thoroughly that the corresponding `Denied` reason is unreachable (round 1 F-12's argument, extended). |
| 10 | Release a raw sensitive value — an email address P5 flagged — as an `Excerpt` | **HOLE (A2), executed.** The signal is stored against the *filename's* observation key, so the address's key carries no signal and Task 7's always-local rule does not fire on it. |

The three architectural layers, honestly scored: **L1 is half-proven** (the ledger is real; the
obligation to consult it is not enforced — #2). **L2 is not proven** (#3 and #4 both pass its guard).
**L3 is correctly reported by the plan as P8's**, and P7's decision to ship and prove the *instrument*
is the right call — it is the most honest thing in either document, and it is undercut only by the
instrument checking a signature where it needs to check a body.

---

## NEEDS JOSEPH

Verbatim, unresolved, and not answered here. Only items this pass **adds** to the two plans' existing
lists.

1. **What does P6 write for a field only the LLM could fill, when no model is configured?**
   The thirteen `unresolved` reasons contain no member for it. `privacy_withheld` claims a privacy
   decision that was not made; `budget_deferred` forces P2's writer into `ceiling_reached` and
   fabricates a §8.6 ceiling report; `no_candidate_evidence` is §8.6's named prohibition
   (*"never as 'understood and found unimportant'"*); writing nothing violates B7 and Done-means 18.
   This fires once per unfillable field per file on every deterministic-only deployment, which is
   every deployment in Wave 2. (A8)

2. **What outcome does a §8.5 stage carry when every field ended `privacy_withheld`?**
   `SPEC.md:360-366` rule 4 says it is not an abstention. `SPEC.md:611` maps every non-budget
   `unresolved` to `abstained`. P2's writer will demand `ceiling_reached` for `deferred`, which is
   false. The two SPEC sentences cannot both stand. (A7)

3. **Who owns `prompt_fingerprint`, and how is it computed?**
   Four consumers today — P1's `events` column, P2's version-tuple axis, P6's §3.4 fact cache key,
   P7's release binding term — and no part defines the computation. A byte-level disagreement between
   any two of them means a fact's cache key does not match the audit record of the call that produced
   it. This is `config_fingerprint`'s exact shape, one wave earlier than it was caught last time.

4. **Which part appends the `basis_key`-carrying correction event when the gesture is collected by
   P13?** I4 says *"the acting part"*; P7's Contract-in lists `mark_private` as *"P6+P7 jointly"*.
   Until it is one part, the encoding is unowned and `is_suppressed` fails **open** — a claim the user
   rejected is silently re-proposed, which §8.7 exists to prevent. (A13)

5. **Does `files.sensitivity_state` hold a `HANDLING_CLASSES` member, or a different vocabulary?**
   `mirror_state` being a mapper implies the latter. If it is the latter, P2's `handling_class` gains a
   fourth spelling of one concept the moment Task 22 makes the bundle non-null. (A10)

Carried, not re-argued: P7's I6 (deletion vs append-only) blocks Task 15 and the plan says so; P6's
five naming questions (F2–F6) block five Done-means items and the plan says so; P6 OQ11 (one record or
three) remains the largest open seam in the wave and both plans correctly refuse to answer it.
