# P1–P9 audit, and the P10/P11 plans — what is lacking and needs improvement

Date: 2026-08-27. Branch `build/p6-p7-first-packages`. Code audited at HEAD `b7c6e8f`;
re-verified at `9bc36e6`, where `git diff --stat b7c6e8f HEAD -- src/ tests/` is empty and
`git status --short src/ tests/` prints nothing — **`src/` and `tests/` are byte-identical to the
pre-audit tree.**

---

## 1. What this is

Fifteen auditors read the fifteen contracts and the code behind them, in parallel, and this
document is the single consolidated answer to "tell me what is lacking and needs improvement."

**Scope.** Nine built parts (P1–P9, ~34,000 lines of `src/`), the space between them (connectors,
whole-product invariants, the four cross-cutting constraints, the walking skeleton), the two
rewritten plans that are not yet built (P10, P11), and the domain-research → template-library → P10
chain. P12 and P13 are not audited: neither is built and neither has a plan.

**Method.** Each auditor did four things, in this order:

1. **graphify first**, per the repo rule, before any grep. This was not ceremony — it produced
   several findings directly. `graphify explain "SessionWatch"` returned 17 connections and not one
   to `exclusion.py`, which *is* Blocker 1 stated at the graph level. `graphify query
   "group_state_as_of accepted group"` falsified a P11 plan claim that the module does not exist.
   `graphify explain "record_stage_output"` established that only three production callers exist,
   before any file was opened.

   **It also produced this audit's most useful methodological finding, by being used wrongly.** The
   seams auditor originally passed the P8→P9 seam on the strength of
   `graphify path "run_call" "group_subject"`, then caught the error and wrote it up:

   > *"`graphify path` answers 'is there a reference chain from A to B'. Compatibility asks 'do the
   > arguments at the call site satisfy the callee's signature.' The first cannot answer the second,
   > and I substituted one for the other."*

   Worse, the path it had quoted routed through `DossierRequest` — a shared **record type** — not
   through a call edge, because P9 never imports `run_call`; it receives it as an injected
   parameter. The evidence was equally consistent with the seam being wired and with its never
   having been wired. The corrected rule, which this project should adopt for any seam claim:
   **a seam is verified when the caller's arguments have been bound against the callee's live
   signature, or when a test drives the real callee end to end — never when a reference chain exists
   between them.** graphify is the right tool for orientation and for "does a producer exist"; it is
   the wrong tool for "would this call work."
2. **Read the SPEC, the PLAN and the canonical design** (`planning/00-database-agent-product-design.md`
   wins on conflict) and walk the Done-means table item by item.
3. **Guard sabotage.** Copy a source file, delete or invert one invariant, run the part's suite,
   restore, verify byte-identical by md5 or `diff -r` against a pristine `git archive` snapshot of
   HEAD. A guard that stays green under sabotage is a **SILENT guard** — a test that reports it is
   protecting something and is not. 111 sabotages were run; 15 were silent.
4. **Live probes** for behaviour a missing guard cannot reveal — running the real functions and
   printing what they actually return.
5. **Signature binding**, added after the graphify lesson above: AST-walk `src/`, resolve every
   cross-part import to its defining package, and `inspect.signature(callee).bind(...)` each call
   site's actual arguments against the **live** signature. Four scans — direct call sites, typed
   `Callable` seams, injected doubles against the production callables they stand for, and
   hardcoded empty values at cross-part call sites. Results in §3.

The lead then independently re-verified twelve findings by direct command. Those are marked
**CONFIRMED BY LEAD** below. Everything else in this document was also re-verified by command
while writing it; no quotation here is from memory.

**The counts published here are post-verification, and that is deliberate.** The binding scans threw
false positives, and each was checked before anything was reported: four apparent `site_validator`
mismatches turned out to bind the wrong functions (those are called by `sites.dispatch` with full
keywords and are never passed as `site_validator`), and four more — `ocr_engine`, `read_long_tail`,
`now`, `is_protected_container` — were artefacts of a crude positional-count heuristic
(`lambda target, *, config:` is one positional plus one keyword-only, which is exactly right). All
eight were dropped. An audit that verifies its own hits before publishing them is worth more than one
that does not, so the 245 findings in this document are what survived that check, not what the tools
first emitted.

**The honest limits of this audit.**

- **Fifteen sessions shared one working tree.** Every auditor repeatedly saw other sessions'
  in-flight sabotage in `git status`, and twice a concurrent edit to
  `src/database_agent/learning.py` broke test *collection* in unrelated packages for under a minute.
  Every sabotage result quoted is a **delta** against a baseline captured immediately before that
  edit, and every restore was verified by hash against a pristine snapshot. A shared
  basename-keyed backup directory (`scratchpad/audit1/bak/`) was found to be corrupted by
  cross-package collisions — 17 basenames are shared across ten `src/` packages — and was abandoned
  mid-audit in favour of path-keyed snapshots. One incident (grouping's `learning.py` written over
  `database_agent/learning.py`) was detected by md5 within seconds and restored from the git object
  store. **No git history operation was performed by any auditor: no commit, no stash, no checkout,
  no rewrite.**
- **P10 and P11 are plans, not code.** "Would break at Task 4" is a judgement from static
  analysis plus live probes of the symbols the plan imports, not from executing the build. The
  strongest evidence available was obtained for P10: an auditor extracted all 21 `src/tree_design/*.py`
  code blocks and 20 test modules from the plan, staged them outside the repo, and ran the plan's own
  suite (`29 failed, 182 passed, 5 errors`). That is real execution of plan-printed code, but it is
  not the built part.
- **P10/P11 plan line numbers have since drifted.** Two sessions are actively editing those plans.
  `TREE_EDIT_ACTIONS` was cited by its auditor at `PLAN:601-605`; it is live at
  `planning/parts/P10-tree-design-freeze/PLAN.md:634-638`. Plan citations below are the ones I
  re-verified today; treat any plan line number as approximate.
- **Mechanical coverage was measured for one part only.** `pytest-cov` is not installed; the P9
  auditor built a `sys.settrace` collector by hand. The other eight parts' "no test reaches this"
  claims rest on grep plus graphify call edges, which is weaker.
- **The full suite was not re-run at the end by every auditor**, because the tree was moving. Each
  scoped its final green claim to its own package and verified that package byte-identical to HEAD.
- **Things nobody could determine are in §9, not silently omitted.**

---

## 2. Verdict table

| Part | Scope | Verdict | The one sentence |
|---|---|---|---|
| **P1** storage, identity, provenance | `src/database_agent/` | CONFORMS WITH GAPS | Unusually well defended — 11 of 14 sabotages caught — but three published SPEC sentences are not true of the code. |
| **P2** eval and replay harness | `src/eval_harness/` | CONFORMS WITH GAPS | The machinery is real; the thing it exists to measure is not connected to it — 4 of 10 dimensions have a live producer, and no cross-part test ever calls `assert_run`. |
| **P3** scan and corpus selection | `src/scan_agent/` | GAPS + BLOCKER | The scan itself is the strongest work in the repository — zero silent guards — and the session watch, a second entry point, respects none of its rules. |
| **P4** evidence shape | `src/evidence_shape/` | CONFORMS WITH GAPS | The single shape is genuinely singular and provably so; what P4 *publishes about* the shape has drifted from what it enforces. |
| **P5** extractors and readers | `src/extractors/`, `src/readers/` | CONFORMS WITH GAPS | Disciplined, no-invention, no defaults — with one live crash on an ordinary `.eml` and a ratified OCR language set that never shipped. |
| **P6** facts and facets | `src/facts/` | CONFORMS WITH GAPS | Every guard fired; the gaps are behaviours no test ever asserts against the production path, and one of them writes a wrong fact. |
| **P7** privacy and consent gate | `src/privacy/` | GAPS + BLOCKER | The door is real and I could not get past it — but what is carried through it is wider than the SPEC says, over a channel the SPEC never mentions. |
| **P8** LLM harness and validator | `src/llm_harness/` | **DOES NOT CONFORM** | 11 of 13 invariants hold under sabotage; the model chooses what the caller is told by ordering its own claims, and Site A cannot reach 2 of its 5 outcomes. |
| **P9** grouping | `src/grouping/` | **DOES NOT CONFORM** | The deterministic spine is real; hub suppression destroys a group *because* it has more evidence, and the part cannot be composed with the P8 it is specified against. |
| **Seams** P1→P9 | connectors, invariants | GOOD, 2 HIGH | All five whole-product invariants hold and 306/306 cross-part call sites bind. The walking skeleton is eight disjoint segments, and the suite is green in only one collection order. |
| **P10 plan** tree design and freeze | `planning/parts/P10-.../PLAN.md` | Executable with fixes | Closes 30 of the prior audit's 38 — and after all 17 tasks P10 cannot build a tree: `accept` has no writer. |
| **P11 plan** placement and residual | `planning/parts/P11-.../PLAN.md` | Executable with fixes | Nineteen strong components plus an orchestration task that does not orchestrate them. |
| **P10 ↔ P11** | the seam between the plans | **DO NOT CONNECT** | Zero shared field names on the record they both centre on; P11's gate imports a symbol P10 never produces. |
| **Templates / domain research** | `planning/domains/`, library plan | Blocked, correctly | Two research gates and the whole P10 build sit between "research lands" and "build templates" — and one gate names the wrong P10 tasks. |

**Findings by severity across all fifteen audits: 29 BLOCKER · 53 HIGH · 79 MEDIUM · 45 LOW ·
39 NOTE = 245.** Of the 29 BLOCKERs, 8 are in live code and 21 are in the two unbuilt plans.

---

## 3. The through-line

**The parts are individually well-built and their signatures line up. What is missing is that no
seam is ever exercised end to end — and the defects live in the gap between "the types match" and
"the path has run."**

An earlier draft of this document said something stronger and wrong: that every seam is tested
against a hand-built double that does not match the real thing. A four-scan binding check
disproved it, and the corrected numbers matter because they change where to look.

**The signatures line up. This was measured, not assumed.**

| Scan | Result |
|---|---|
| Direct cross-part call sites in `src/`, each bound with `inspect.signature(callee).bind(...)` against the **live** signature | **306 checked — 271 auto-bound COMPATIBLE, 35 resolved manually, all COMPATIBLE, 0 would raise** |
| `Callable`-annotated seams, declared arity vs how `src/` actually invokes them | **53 found — 48 with a declared arity, all consistent, 0 arity mismatches** |
| The five seams that declare `Callable[..., X]` and are therefore unchecked by the type | **4 bind cleanly against the production callable they stand for; 1 does not** |
| Hardcoded empty keyword arguments at cross-part call sites | 20 found; 19 are ordinary optional fields; **1 is a contract field** |

The 35 that needed manual resolution are not judgement calls: 17 are `**event_defaults(...)` into
`append_event`, which is `(conn, **fields)`; 14 are exception constructors with no own `__init__`;
two are genuinely variadic; and two are `**`-unpacks bound explicitly against every live shape they
are called with.

**So the defect class is narrower and sharper than "signatures are broken everywhere."** It is:
*a seam whose type declares nothing, whose production wiring does not exist, and whose only exercise
is a variadic test double.* Exactly one seam in the product has all three properties, and it is
broken. Here is the evidence, in descending order of consequence.

**1. `p8_run_call` — the one genuine signature mismatch, invisible because the seam has no
production wiring.** `src/grouping/pipeline.py:323`:

```python
    outcome_from_model = p8_run_call(conn, request)
```

against the live `run_call` (`src/llm_harness/harness.py:351-358`), which takes five further
keyword-only arguments. Verified by binding:

```
$ PYTHONPATH=src python3 -c "import inspect; from llm_harness.harness import run_call; \
    inspect.signature(run_call).bind(object(), object())"
TypeError: missing a required keyword-only argument: 'gate'
```

The parameter is typed `Callable[..., object] | None` (`pipeline.py:239`), so nothing checks it.
Every P9 test injects `lambda *a, **k:` or a `**kwargs`-absorbing spy, so 370 tests are green.
And **nothing in `src/` ever supplies it**:

```
$ grep -rn "p8_run_call" src/
src/grouping/pipeline.py:18   [docstring]  :239 [declaration]  :309 [None guard]  :323 [the call]
$ grep -rnE "^\s*(from|import)\s+grouping" src/ | grep -v "^src/grouping/"
(no output — no module outside src/grouping/ imports it)
```

**The `TypeError` is therefore latent, not live: P9 is wired to P8 nowhere in production, so that
path never runs.** "P9 cannot call P8" is accurate; "P9 crashes in production" is not. The seam is
unwired *and* incompatible, which is worse than either alone — there is no running code to notice
the mismatch and no test that would. Every injected spy also returns `None`, so mechanical coverage
shows `pipeline.py:329-334`, the entire model-accepting path, **never executing across all 370
tests**.

**The seam test came within one line of catching it.**
`tests/integration/test_p9_p8_group_seam.py:52-54`:

```python
    parameters = inspect.signature(llm_harness.run_call).parameters
    assert "gate" in parameters
    assert "model_client" in parameters
```

It reads the *live* signature and asserts that `gate` and `model_client` exist as parameters — then
never asserts that P9's call site supplies them. It confirms the exact two arguments whose absence
makes the call raise.

**2. P2's `assert_run` is called by no cross-part test.** The join P2 exists to make has never been
exercised against a real producer:

```
$ grep -rln "assert_run" src/ tests/
src/eval_harness/assertions.py
src/eval_harness/shadow.py
tests/eval/test_attribution.py
tests/eval/test_assertions.py
tests/eval/test_comparison.py
tests/eval/test_shadow.py
tests/eval/test_skeleton_p2_step.py
```

`tests/integration/test_p8_p2_replay.py` and `tests/integration/test_p9_p2_replay.py` write
envelopes and read them back; they never assert. The only tests that exercise `assert_run` supply
their own `DimensionValue`s — which is exactly why nobody noticed that P8 supplies none.

**3. P8 Site A tests construct their own `P8Verdict`, so two of five outcomes are unreachable.**
`fact_validation._verdict` is only ever called with `{REJECT, ACCEPT_DIRECT, ABSTAIN}`
(AST-verified). `accept_context_supported` and `weak` cannot be produced. The two tests that appear
to cover them — `test_proposal_state_mapping_uses_p6_states` and
`test_weak_mapping_writes_possible_not_a_duplicate_writer` — hand-build the `P8Verdict` they assert
on. The reason code `SEARCH_HINT_ONLY` has no producer anywhere in `src/`.

**4. P8's fixtures are the only reason two of its site checks look right.** Live, at Site D:
`placement_validation.py:297` compares `item.location` against `dossier.subject_ref` — a
within-document location against a file id. It passes only because P8's own fixture sets
`location="file-1"`. The one real `EvidenceItem` builder in the repository
(`src/grouping/p8_seam.py:125-131`) sets `location=item.document_type`. Change the fixture's
`location` to `"body"` and the same pair rejects.

Historically, at Site B: P8's own prior audit records that its tests built their own `Dossier`
while `run_call` produced one those tests would have rejected. That defect was found and fixed —
and the same shape is live again one part downstream, in the `conflicts=()` that P9's builder
hardcodes (Blocker 3c). A dedicated scan for this shape found 20 hardcoded empty keyword arguments
at cross-part call sites; 19 are ordinary optional fields, and that one is the only field a
connection contract names.

**5. P4 published no predicate for its own citation handle, so P7 wrote a second one.**
`src/privacy/classification.py:92` defines a private `_is_observation_key`. P1 got this right —
it publishes `is_content_hash` (`src/database_agent/identity.py:43`) and P4 imports it rather than
restating "64 lowercase hex". P4 publishes the producer (`sha256_of`) and no recognizer. Downstream,
`tests/p7/test_p7_release.py:283` and four other fixtures cite `"obs-key-1"` — a handle no live
`Observation` could ever produce.

**6. P9's Done-means 3 — §4.6, the design's most-quoted worked example — is proved against a
fixture.** `tests/p9/test_p9_done_means.py:53` opens `course_dossier_fixture()`;
`assemble_group_dossier` is never in the path. And P9's hub tests hand-write
`detail="columbia.edu"` onto neighbours retrieval would never produce for that channel, and never
give two `shared-validated-fact` neighbours the same detail — the *one* arrangement in which the
hub-suppression inversion cannot appear.

**7. P6's discount tests call the production functions directly.** Every test in
`tests/p6/test_p6_discount.py` calls `screen_metadata` or `field_permitted` itself; the one named
`test_the_discount_fires_before_ranking_and_the_second_candidate_wins` says in its own comment that
`facts.facets` "is not imported". Nothing drives `FactResolver.resolve`, which is where the survivor
set is thrown away.

**8. P1's Done-means 7 asserts over a hand-written dict.** `tests/test_events.py:25` builds
`_minimal()` — always `file_id="f1"`, `content_hash="abc"` — and never inspects an event P1's own
code emits. Two P1 emitters violate the rule the test claims to enforce. Its Done-means 3 test has
the same shape: it asserts `extraction_status_by_tier == "{}"` on the **new** row, which
`record_file` writes unconditionally, so the assertion is true whether or not invalidation ran.
Deleting the invalidation left 1,667 tests green.

**9. The walking skeleton is eight disjoint segments.** `planning/02-segmentation-map.md:177`
specifies *"One file, one deterministic path, every seam touched."* What exists is eight per-part
`test_p*_skeleton_step.py` files, each proving its own step against a hand-built neighbour. The P1
step's P3 half is a fixture whose explanation string is literally
`"skeleton fixture stands in for P3"`. The P2 step's one live stage is a hand-written adapter
returning `payload='{"stands in for P4/P5": true}'`. `run_p1_p7` returns a real `bundle_id` and
`replay_bundle` consumes bundles, and **no test in the repository connects them.**

**The conclusion that survives, and it is the document's most important one: the suite measures
part quality, not system quality.** That claim does not rest on signatures being broken everywhere
— they are not — but on the narrower and better-evidenced fact that **no seam is executed end to
end**. A part is verified when its own tests pass. A seam is verified only when a reference chain
exists between the two sides, which is not the same thing and cannot substitute for it.

**What this costs, concretely.** One honest end-to-end test with no doubles — scan a real corpus,
extract with a real reader, resolve facts, group, build a dossier, pass the gate, call a recording
model client — would have caught, simultaneously: the P8 positional-verdict defect (Blocker 3a),
the `run_call` incompatibility (Blocker 3b), the P7 context bypass (Blocker 2), and, the moment the
corpus contained a `.app` under a session watch, the P3 watch breach (Blocker 1). Four independent
BLOCKERs, one test.

**The counter-evidence, which is real and worth stating.** Where guards exist they are unusually
good. P3 has **zero** silent guards across ten sabotages. P6 has zero across nine. P4 has one across
nine. Two of P1's guards fired against sabotage from *other* sessions during the audit
(`test_no_source_identifier_is_an_aggregate` caught an injected `quality_index`;
`test_an_extractor_may_write_only_direct_and_possible` caught an injected `text_quality_score`)
without anyone asking them to. And the four binding scans above are themselves a strong positive
result: 306 cross-part call sites and 48 typed callable seams line up against live signatures, which
is not the state of a codebase that has drifted. The problem is not that the tests are weak, and it
is not that the interfaces have rotted. It is that they all stop at the package boundary.

---

## 4. BLOCKERS

Three defects stop the product from doing what the design says it does. Each is stated as
**what it is → the evidence → why it matters to the product → the fix**.

---

### B1 — The session watch reads inside protected containers and writes their interior paths into an append-only log

**CONFIRMED BY LEAD.** Owner: P3. Severity: BLOCKER — this violates the standing user constraint,
and `events` cannot be un-written.

**What it is.** `src/scan_agent/exclusion.py` implements the protected-container rule completely
and correctly: it is checked **first**, before every other §1.1 rule (`exclusion.py:127-133`), it
protects the whole subtree not the entry (`:83-89`), there is no override parameter, the verdict
carries the container's own path and nothing from inside it, and ten sabotages of it were all
caught. `SessionWatch` — the *other* entry point into the same corpus — implements none of it.

**Evidence.**

```
$ grep -n "protect\|exclusion\|is_protected" src/scan_agent/watch.py
(no output)
```

Zero protection references in the entire module. `src/scan_agent/watch.py:42-50`:

```python
    def open(self, roots) -> None:
        """Begin watching the selected roots and record their current stat."""
        self._roots = tuple(Path(root) for root in roots)
        self._observed = {}
        for root in self._roots:
            for current, _, names in os.walk(root):
                for name in names:
                    path = Path(current) / name
                    self._observed[str(path)] = self._stat(path)
```

A bare `os.walk` with no pruning, and `self._stat(path)` on every file found. `poll()` repeats the
same walk at `:68-73`. `notify()` then writes the interior path into the append-only log,
`src/scan_agent/watch.py:104-112`:

```python
        append_event(self._conn, **event_defaults(
            event_type="external modification detection",
            file_id=row["file_id"] if row else None,
            content_hash=row["content_hash"] if row else None,
            old_path=str(path), new_path=str(path),
```

Reproduced by the auditor over a tmp tree containing
`Numbers.app/Contents/Resources/sheet.numbers`: the file is stat'ed on `open()`, and the event row
carries its full interior path in both `old_path` and `new_path`.

**SPEC says X, code does Y.** `planning/parts/P3-scan-corpus-selection/SPEC.md:39`: *"P3 does not
descend into one, **does not stat its contents**, does not hash a byte of it, and does not create a
`files` row for anything inside it."* SPEC:47: the verdict carries *"the container's own path and
**nothing derived from inside it**."* `planning/11-ops-runtime.md:73` repeats it. The watch does the
stat the rule forbids and then persists the derived path.

**Why it matters to the product.** This is the one rule the user stated as an absolute — *"reports,
apps and system files MUST NOT BE MOVED OR READ OR ANYTHING SYSTEM OR SENSITIVE IN THAT SENSE"* —
and it is the one rule the design says review may not override. `events` is append-only and enforced
by triggers, an authorizer and a no-drop guard (all of which P1 defends well): **a path written
there cannot be removed**. So this is not a bug that can be fixed forward for a corpus that has
already been watched. It is also not theoretical: the watch is the ordinary "user keeps working
while the scan runs" path.

**Why no guard caught it.** There is no test anywhere asking whether `SessionWatch` respects §4b.
The neighbouring case is deliberately and correctly handled the other way —
`tests/p3/test_p3_watch.py:143` asserts the watch *ignores* §1.1's ordinary exclusions, with the
reasoning spelled out that `node_modules` is a corpus rule, not a read rule. That reading is
defensible for `node_modules`. It is not available for §4b, whose stated reason is precisely that
reading puts third-party material into evidence a model may later see.

**Fix.** Prune protected subtrees in `open()` and `poll()` (`os.walk`'s `dirnames` list is mutable
in place), and return early from `notify()` when `is_protected_container(path)`. **Both** entry
points need it: `notify` is the documented entry point a platform FSEvents adapter calls directly
(`watch.py:10-14`), so guarding only the walk leaves the real adapter unprotected. Add the test that
mirrors `tests/p3/test_p3_protected_container.py:42` for the watch, asserting zero events for a
change inside a `.app`.

---

### B2 — The privacy gate releases document text it never redacted, never bounded, and never audited as released

**CONFIRMED BY LEAD.** Owner: P7 (with P8 as the carrier). Severity: BLOCKER — this is content
leaving the device.

**What it is.** `Gate._materialise` redacts `Materialised.value` and copies `context_before` /
`context_after` from the raw observation untouched. Those two fields travel inside
`Released.materialised_items`, and P8's dossier builder writes them verbatim into the bytes handed
to the model.

**Evidence.** `src/privacy/gate.py:481-486`:

```python
            resolved.append(Materialised(
                observation_key=found.observation_key, span=found.span, value=value,
                zone=found.zone, context_before=found.context_before,
                context_after=found.context_after,
                context_truncated=found.context_truncated,
                unit_length=found.unit_length))
```

`value` is the redacted string. `context_before` and `context_after` are `found.*` — the raw
observation fields, never passed through `classifier` or `transform`. `src/llm_harness/dossier.py:52-53`
copies them onto `ReleasedEvidence`, and `src/llm_harness/dossier.py:74-75`, inside `_released_body`,
puts them into the canonical JSON that becomes `payload.model_visible_bytes`:

```python
        "context_after": item.context_after,
        "context_before": item.context_before,
```

Probed against the project's own `tests/integration/test_p8_p7_egress.py` fixture, with the real
`Gate` and the real `build_dossier`:

```
FULL SOURCE TEXT       : 'Passport number A1234567 was issued in 2019 to the applicant.'
requested span         : TextSpan(start=16, end=24) -> raw 'A1234567'
released value         : '[redacted]'
released context_before: 'Passport number '
released context_after : ' was issued in 2019 to the applicant.'
context_before + RAW VALUE + context_after == whole unit? -> True
MODEL-VISIBLE BYTES contain the unredacted context? -> True
AUDIT redaction_manifest holds raw document text? -> True
```

An 8-character requested span shipped 52 of the unit's 60 characters — the whole unit minus the
redacted span.

**SPEC says X, code does Y.**
`planning/parts/P7-privacy-consent-gate/SPEC.md:248` states the field's contract in five words:

```
  materialised_items[] post-redaction values only
```

`context_before` / `context_after` are pre-redaction values, in the same tuple, on the same object.
Design §8.4 puts *"complete extracted text"* in the always-local set — `vocabulary.ALWAYS_LOCAL`
includes `"complete_extracted_text"`, and `items._refuse_always_local_name` makes a `MetadataField`
naming it unconstructible — and the gate then ships a contiguous slice of exactly that text as a
rider on a legal `Excerpt`. §8.4 also says *"It should not send full documents where a short heading
or OCR excerpt is enough."* `items.is_whole_document` inspects `item.span` against `unit_length`
only (`items.py:246-259`); it has no view of the context, so on this shape it can never fire.

**And the SPEC never mentions the channel at all:**

```
$ grep -c -i "context" planning/parts/P7-privacy-consent-gate/SPEC.md
0
```

Zero occurrences in 630 lines. This was not a rule that was weighed and relaxed. It is a channel
nobody looked at.

**Why it matters to the product.** For every consented protected file, the model receives the
surrounding document text in full and unredacted, while `redaction_manifest.any_redacted` reports
`True` and the audit record says `redaction_applied: true`. The audit record is not false about the
*value*; it materially understates what left the device. And the size of the leak is set by a knob
P7 cannot see — `context_window` is supplied to the extractors by the orchestrator's caller, and P7
reads no ceiling over it. On the project's own fixture that window is the entire remaining unit.
Compounding it, `RedactionEntry.to_mapping()` (`redaction.py:87-96`) emits both context fields into
the `model_release` event's explanation, which contradicts `audit.py:21-25`: *"The record says what
left the device without holding a copy of it."*

**Why no guard caught it.** Sabotage S9 — set `context_before=None, context_after=None` in the gate
— produced **zero** new failures across `tests/p7` (817 tests) *and* zero across `tests/p8` plus
`tests/integration/test_p8_p7_egress.py`. Nine of the other ten P7 sabotages went red immediately;
the gate's architecture is genuinely load-bearing. This is not a deaf guard. It is the absence of
any rule at all.

**Fix, in order.**
1. **Decide, in the SPEC, what `context_before` / `context_after` are on a `Released`.** §8.4's
   compact dossier names five releasable item kinds and context is not one of them. This is a
   contract decision, not an implementation choice — see OPEN-1 in §9.
2. Then either run `classifier`/`transform` over the context in `apply_redaction`, or bound it to a
   P7-owned ceiling, or drop it from `Materialised` and let P8 request it as its own addressable
   item that `check_item` can refuse.
3. Extend `is_whole_document` (or add a sibling) to measure
   `len(context_before) + len(value) + len(context_after)` against `unit_length`, so §8.4's
   full-document rule sees the whole payload.
4. Add the test S9 proves is absent.

---

### B3 — The model path cannot run: P8 reports the wrong verdict by position, and P9 cannot call P8 at all

**CONFIRMED BY LEAD.** Owners: P8 and P9. Severity: BLOCKER — these are the two parts the whole
LLM half of the product runs through, and together they mean no model-assisted grouping works end
to end today.

This is one blocker in three parts, and they differ in how they bite. **B3a is live** — `run_call`
runs today and reports the wrong verdict whenever a response carries more than one claim. **B3b is
latent** — the incompatible call site is real but never reached, because P9 is unwired to P8 in
production. **B3c is live** — it sits on the deterministic path, which does run. They are one
blocker because none is survivable alone: wiring P9 (B3b) exposes B3a on the first multi-claim
response, and fixing B3a changes nothing while P9 cannot make the call.

#### B3a — `run_call` reports the last claim, not the worst

`src/llm_harness/harness.py:346-348`:

```python
    if not verdicts:
        return ValidationUnavailable(missing=("claims",))
    return verdicts[-1]
```

The shard level was fixed and is right — `harness.py:472`:

```python
    # One call, one returned verdict, chosen by severity and not by position.
    return min(produced, key=lambda verdict: OUTCOME_SEVERITY.index(verdict.outcome))
```

but `_validate_and_record` still collapses the **claims of one response** positionally.
`src/llm_harness/vocabulary.py:44-49` states the rule the repair was meant to implement, and states
both halves:

```
#: Worst first. `run_call` returns ONE verdict for a call that may have produced
#: several -- one per shard, one per claim -- and `emit_stage_output` maps that
#: one result onto one P2 envelope. Returning the LAST one reported by position:
#: a call whose first shard was rejected and whose second was accepted read
#: `accept_direct`, and the P2 row read `produced`. A caller who is told
#: `accept_direct` must be able to take it as true of the whole call.
```

Only the shard half was implemented. Proven live through `run_call` with a two-claim Site A
response — claim `term` citing a span P7 never released, claim `school` valid:

```
reject_first=True  stored=[('reject','term'),('accept_direct','school')] returned=accept_direct
reject_first=False stored=[('accept_direct','school'),('reject','term')] returned=reject
```

**The model decides what the caller is told by choosing the order of its own claims.**
`stage_output._envelope` maps `accept_direct` to `("produced", "within_ceiling")`, and
`src/grouping/p8_seam.py:259` consumes the single returned verdict as "one authoritative P8 result"
— so at Site B a rejected claim in the same response becomes an accepted group membership, and
§8.5's grounding measurement reports the opposite of what happened.

**Fix.** `return min(verdicts, key=lambda v: OUTCOME_SEVERITY.index(v.outcome))` at `harness.py:348`,
and extend `test_the_returned_verdict_is_the_worst_of_the_shards_not_the_last` with a single-shard
multi-claim case.

#### B3b — P9 cannot call `run_call`, and P9 is wired to P8 nowhere in production

Quoted in §3 above. `src/grouping/pipeline.py:323` versus `src/llm_harness/harness.py:351-358`;
binding the two raises `TypeError: missing a required keyword-only argument: 'gate'`.
PLAN Task 13 Step 5 states *"Production composition passes `llm_harness.run_call`"*. It cannot.
The frozen connection contract (`planning/30-p8-p9-connection-contract.md`) also specifies that P9
passes `llm_harness.sites.SiteDependencies`; the pipeline passes none.

**State this precisely: the `TypeError` is latent, not live.** Nothing in `src/` supplies
`p8_run_call` — the four occurrences are a docstring, the declaration, the `None` guard and the call
— and no module outside `src/grouping/` imports `grouping` at all. `src/orchestrator.py` and
`src/production.py` stop at P7 plus the bundle. So the incompatible call site is never reached by
running code today. **"P9 cannot call P8" is accurate; "P9 crashes in production" is not.**

That makes it worse rather than better, and it is worth being clear why. An incompatible call site
that runs gets found on the first execution. An incompatible call site that is *also* unwired has
nothing to find it: no production path exercises it, the type is `Callable[..., object]` so no
checker examines it, and every test supplies a variadic double. It sat here through a full audit
round and was passed by a reachability check that could not see it. The day someone wires the model
path — which is the point of P9 existing past the deterministic skeleton — this raises immediately.

**Fix.** Either give `group_subject` the five P8 dependencies and call `run_call` with them, or make
the injected callable an explicitly typed adapter `Callable[[Connection, DossierRequest], P8Result]`
with a production factory that closes over gate/client/prompt/dependencies/clock. Then add one
integration test that drives `group_subject` with `llm_harness.run_call` itself — and strengthen
`tests/integration/test_p9_p8_group_seam.py:52-54`, which already reads the live signature and
asserts `gate` and `model_client` exist as parameters, to assert that P9's call site supplies them.

#### B3c — and the dossier P9 hands over re-creates the exact dead check the contract was written to fix

`src/grouping/p8_seam.py:172`:

```python
        conflicts=(),
```

`planning/30-p8-p9-connection-contract.md` records why the field's ownership moved to P9:

> `conflicts: tuple[Conflict, ...]` — the builder's known conflicts. P8 hardcoded `()` here and
> Site B's `target_institution` check could never fire.

P9 hardcodes the same `()`. `src/llm_harness/group_validation.py:113` therefore returns `False` on
every P9 call, and §4.8's rule — *"an application packet does not silently absorb a document with a
conflicting target institution"* — is unenforceable.

**P9 holds the authority it is discarding.** `src/grouping/pipeline.py:75` declares
`conflicts_for: Callable[[Sequence[str]], Sequence[object]]` and `:280` passes it to `build_graph`
for SR4. It is never passed to `build_dossier_request`, and `assemble_group_dossier` is called with
a literal `conflicts=()` at `pipeline.py:193`, `:223` and `:301` — verified. So the conflict set is
computed for the graph and dropped on the way to the model. The same `()` is hardcoded again at
`p8_seam.py:336` on the membership.

Unlike B3b, **this one is live**: it is on the deterministic path, which does run.

A dedicated scan for this shape across all cross-part call sites found 20 hardcoded empty keyword
arguments. Nineteen are ordinary optional fields (`page=None`, `excerpt_span=None`, `start=0`, …).
This is the only one that is a field a connection contract names.

**Fix.** Compute `found = knowledge.conflicts_for(graph.file_ids)` once, pass it to both
`evaluate_stop_rules` and `assemble_group_dossier`, and set `conflicts=dossier.conflicts` in
`build_dossier_request`.

---

### Also labelled BLOCKER by their auditors

These are live-code defects of the same severity class. They are treated in full in §5 and appear in
the prioritized list in §8; they are named here so nothing severe is buried.

| # | Part | What | Evidence |
|---|---|---|---|
| B4 | P5 | Sensitivity signals are attached to the wrong observation, and an ordinary `.eml` with a repeated address **crashes the scan** | `long_tail.py:246` indexes by list position; `sink.py:49` collapses that list afterwards. Three copies of one address → `IndexError` at `orchestrator.py:426`, outside the `try/except` that turns reader failures into a `failed` run |
| B5 | P6 | The §2.2 tool-metadata suppression is advisory: the survivor set is discarded, so `Producer = python-docx` becomes a **`validated` fact `subject = "python-docx"`** | `resolver.py:176` discards the return value of `_screen_metadata`; `field_permitted` (`discount.py:113`) has no caller in `src/` — verified: only `resolver.py:174` (a comment) and three test call sites |
| B6 | P9 | Generic-hub suppression destroys a group **because** it has more corroborating anchors | `retrieval.py:180` sets `detail=f"{seed.field_key}={seed.value}"` — the same string for every corroborating file; `graph.py:160` promotes it to `bridge_entity_ref`; `graph.py:118-133` counts it. At `generic_hub_frequency=3`: two anchors form a group, three produce `no-group` |
| B7 | P9 | §4.7 purpose detection does not exist | `grep -rni "purpose" src/grouping/*.py` returns three unrelated comment hits. SPEC Done-means 6 and PLAN Task 8 both require it; Task 8 was marked done |

---

## 5. Per-part findings

### P1 — Storage, identity, provenance · CONFORMS WITH GAPS
`src/database_agent/` · 12 files, 1,502 lines · baseline **185 passed** · 11 of 14 sabotages caught

Done-means: 7 PASS, 8 PARTIAL, 1 PASS-with-drift, 0 FAIL. Append-only `events` survives `UPDATE`,
`DELETE`, `INSERT OR REPLACE`, `DROP TABLE`, `DROP TRIGGER`, a reopen and a second connection.
Supersede-never-overwrite refuses a second reason, a self-link and a cycle. This is the best-defended
package in the repository.

**HIGH — P1 stores `hash_algorithm = 'sha256'` beside a value that is not a SHA-256.**
`files_table.py:104-116` writes whatever `content_hash=` the caller supplied, with no validation.
SPEC:98-99 requires *"hash present and matching its declared algorithm"*; two of the three named
shape validations are implemented (`events.py:112-118`, `:119-124`) and this one is not. P1 already
publishes the exact predicate — `is_content_hash` at `identity.py:43` — and P4 imports it. Probed:
`record_file` accepted `content_hash='NOT-A-SHA256-AT-ALL'` with `hash_algorithm='sha256'`.
SPEC OQ10 says the algorithm is stored per row *"precisely so such a migration is detectable"*.

**HIGH — `verify_content` returns `"match"` when the expected hash is absent.** `verify.py:44-48`:
if the file cannot be read, `actual` becomes `None`; if `expected_hash` is also `None`,
`None == None` returns `"match"`. SPEC:576-577 forbids this in as many words: *"An absent hash must
never read as a hash match anywhere in the system."* `events.content_hash` is nullable, so this is
reachable. P12 is the caller, and P12 is where the move/undo decision lives — a `match` here
authorises a move.

**MEDIUM-HIGH — `observe_path`'s content-change path is five autocommit transactions.** The R3
branch (`files_table.py:286-315`) appends an event, updates `scan_state`, invalidates extraction
state, inserts a new row and appends a second event. The connection is `isolation_level=None`
(`db.py:43`) and no production caller opens a boundary — `basic_record.py:54` calls it bare, and
`grep -rn "with transaction(" src/scan_agent/` is empty. Demonstrated: a crash between the halves
leaves **zero live `files` rows for a file that exists on disk**, and the superseded row can never
be re-selected. `tests/test_adversarial.py:994` appears to cover this, but it opens
`with transaction(db):` *in the test* — it proves atomicity is available, not that it is used.

**SILENT guards (3).**
- Done-means 3's invalidation half: deleting `invalidate_extraction_state(...)` from `observe_path`
  left **1,667 tests green**. The test asserts on the *new* row, which `record_file` writes as `"{}"`
  unconditionally.
- The B5 base-type rollup: deleting `events.py:133-135` left 185 green.
- `budget.object_version`: removing the increment left 185 green; nothing anywhere selects it.

**Corrected from the auditor's report — `base_event_type` is not structurally dead.** The rollup is
**idle, awaiting P11's eight event names**, and the registry says so in P1's own words,
`src/database_agent/events.py:62-65`:

```
    # P11's eight typed specializations of "placement recommendation" belong here
    # and are ABSENT ON PURPOSE: P11's SPEC declares them as prose descriptions and
    # publishes no identifiers. P1 does not coin a name another part owns. When P11
    # prints the eight, add them here with base="placement recommendation".
```

Verified live: `len(EVENT_TYPES) == 35`, and `[(n,b) for n,b in EVENT_TYPES.items() if b is not None]`
is `[]`. Declining to coin another part's names is correct behaviour, not a defect. **The real
defect is the test:** `tests/test_events.py:127-132` builds `specializations` from that same empty
comprehension and loops over `[]`, so `test_a_specialization_stores_its_reserved_base_type` reports
green while verifying nothing, and the write path could be deleted today unnoticed. The honest
companion test at `:138` (`test_p11s_eight_specializations_are_declared_but_unspelled`) already
records the absence properly.

| Other findings | Sev |
|---|---|
| Done-means 7's guard never inspects an event P1 writes; `verify.py:70` emits `hashing` with no `file_id`, `learning.py:76` emits `review action routed` with no `file_id` and no `content_hash` | MEDIUM |
| Two vector stores: the SPEC'd `put_embedding` has **zero** production callers (graphify: every inbound edge is a test), overwrites on conflict, and Done-means 15 is verified against it. P9 writes `vector_versions` instead, which appears nowhere in P1's SPEC or PLAN | MEDIUM |
| Four published read surfaces exist nowhere: `file_facts_history`, `group_memberships_history`, `placement_history`, `user_decisions_history` — zero hits in `src/` or `tests/`. The PLAN deferred them until "P6 lands"; P6 and P9 have both landed | MEDIUM |
| `set_ceiling` destroys the value it replaces, so §8.5 replay cannot pin what a run executed under; `object_version` has no reader at all | MEDIUM |
| `SCHEMA_VERSION` is stamped on every open and compared to nothing; `CREATE TABLE IF NOT EXISTS` throughout means an old database opens silently and has its version stamped over | LOW |
| `invalidate_extraction_state`, `set_extraction_status`, `set_sensitivity_state` and `record_llm_cost` accept `author`/`component_version` and ignore both — while the docstring claims P1 "records the invalidation under that author" | LOW |
| `supersede_ddl(table)` accepts a table name and discards it; four production call sites pass one | LOW |
| Three DDL strings defined twice each (`db.py` and the owning module); drift in db.py's copy is caught behaviourally, drift in the other direction is not | NOTE |

**Fix first:** `verify_content`'s `None == None` (HIGH, one line, authorises a move today).

---

### P2 — Evaluation and replay harness · CONFORMS WITH GAPS
`src/eval_harness/` · 13 files, 2,150 lines · baseline **156 passed** · 9 of 10 sabotages caught

P2's own machinery is unusually well built: seven verdicts, five envelope outcomes, the
two-ten-item-lists separation, seal triggers, a real shadow foreign-table proof, and
earliest-divergence attribution all have real mechanisms and real tests.

**The stage-coverage matrix is the finding.** §8.5 requires evaluation *decomposed by stage*, and
the decomposition is only real if each stage emits the row P2 asserts on. Today:

| Dimension | Producing part | Live producer of a `DimensionValue` | Verdict reachable |
|---|---|---|---|
| `extraction` | P5 | **NONE** — `ENVELOPE_FIELDS` is five fields, no `values` | `not_run` always |
| `fact` | P6 | `facts/stage_output.py:90` | full set |
| `retrieval` / `graph` / `grouping` | P9 | `grouping/stage_output.py:116` | full set |
| `llm_grounding` | **P8** | **NONE ANYWHERE** | **`not_run` always** |
| `template` / `tree` / `placement` / `residual` | P10, P11 | none (parts unbuilt) | `not_run` — legal |

**HIGH — `llm_grounding` is a dimension with no writer, and P8's real output scores `not_run`.**
**CONFIRMED BY LEAD.** Verified:

```
$ grep -rn "llm_grounding" src/
src/eval_harness/vocabulary.py:37:    "llm_grounding",  # "Did every cited excerpt exist? ...
src/eval_harness/vocabulary.py:48:SHARED_EVIDENCE_DIMENSIONS = frozenset({"extraction", "fact", "retrieval", "graph", "llm_grounding"})
src/llm_harness/store.py:288 / schema.py:24,103-128 / transport.py:129   [llm_grounding_report — an unrelated table]
```

The dimension exists in exactly two lines of P2's vocabulary. P8's `llm_grounding_report` is a
different thing entirely. And `src/llm_harness/stage_output.py:122-132` passes **no**
`dimension_values=` argument to `record_stage_output`. `assertions.py:106-118` reads observations
only from `stage_dimension_value`, and `:54-57` returns `"not_run"` when there is none. Probed with
a real P8-shaped envelope: `envelope outcome: produced` → `assertion verdict: not_run`.

A stage that ran, called the model, validated citations and returned `accept_direct` is recorded
with the verdict reserved for *a stage that does not exist* — and it is the one §8.5 cares most
about. This is the "value that means the opposite of what it says" shape, live, on the LLM
grounding question.

**HIGH — no cross-part test ever calls `assert_run`** (quoted in §3). Both P2 integration files also
start their runs against a bundle that does not exist, because `run_manifest.bundle_id` carries no
`REFERENCES` clause (`run.py:49-60`) unlike `stage_output.run_id` — verified:
`start_run(bundle_id="no-such-bundle")` succeeds and `assert_run` writes 0 assertions with no error.

**HIGH — dimension 1 (`extraction`) has no producer, and P6's source states the opposite of P2's
SPEC.** `src/facts/stage_output.py:10-12` states as settled fact that *"P5 has no dimension of its
own to report here"*, and `tests/p6/test_p6_stage_output.py:147` codifies it. P2's SPEC Contract out
§2 row 1 names P5 as dimension 1's producing part. One of the two documents is wrong and a test now
enforces the wrong one.

**HIGH — `assertion.evidence_ref` is always NULL.** `assertions.py:136` writes `evidence_ref=None`
unconditionally, with an honest comment explaining why. The SPEC states it as a requirement, not an
option: *"Every `assertion` carries `evidence_ref`, so a verdict can be traced to the observation or
event that produced it."* Every machine-written assertion in the system is untraceable to the
evidence that produced it.

**SILENT guard.** Done-means 3's "no aggregate" test is lexical over a nine-word list. A real
per-run scalar added under the name `quality_index()` left **156 passed**. Adding `accuracy_floor`
as a *parameter* to the same function was caught — the guard works only on the word list, not on the
concept §8.5 objects to.

| Other findings | Sev |
|---|---|
| `candidate_node_retrieval` can never be an `attributed_stage` — it is the one §8.5 stage with no dimension, and attribution builds its verdict map exclusively from `stage_dimension_value` | MEDIUM |
| *Raising* a ceiling so a deferral becomes a genuinely wrong answer is filed as `deferral_changed` with an empty attribution histogram — Done-means 6 is one-directional, the code is symmetric | MEDIUM |
| P2's source declares seven members of P11's `outcome` enum verbatim (`stage_output.py:26-29`), and the guard that should catch it (`FORBIDDEN_VOCABULARY`) omits P11's outcomes — the one foreign vocabulary P2 carries is the one the guard does not look for | MEDIUM |
| `shadow_namespace` holds the run id; nothing is written "into" a namespace. A capability represented by an identity | MEDIUM |
| `record_stage_output` is not atomic on P1's autocommit connection; a collision leaves a committed envelope plus a partial dimension-value set — a half-measured stage that later reads as a real measurement | MEDIUM |
| The A1–A12 adversarial gate is invoked only from its own test file: no CI, no hook, no entry point | LOW |
| `metadata_safe` bundles are never re-run in any test, and `bundle.add_text_unit` refuses them outright | LOW |

**Fix first:** have `emit_stage_output` pass a `DimensionValue(dimension="llm_grounding", ...)`, and
add the cross-part test that calls `assert_run` after it.

---

### P3 — Scan and corpus selection · GAPS + BLOCKER (see B1)
`src/scan_agent/` · 18 files, 1,708 lines · baseline **177 passed** · **10 of 10 sabotages caught, zero silent guards**

The scan half is the strongest work audited. All eighteen Done-means pass except one. §1.1's eleven
literal directory names are verbatim and in the design's order; the five unenumerated categories are
named and empty with the rule wired against the mapping so authoring a member is a data change; the
stat cache is a genuine *difference* test (mtime moving backwards recomputes, and there is a test
literally named `test_the_comparison_is_never_a_newer_than_test`); M8 authorship was verified live by
reading `events` after a real scan.

**HIGH — Done-means 14's "identical cache verdicts" fails for any replayed re-scan.**
`replay.py:130-131` records verdicts with `file_id=None`, and `prior_observation`
(`stat_cache.py:99-104`) joins `files` on `file_id`. Since replay writes no `files` row at all, the
join can never match and `cache_verdict` always returns `(recompute, first observation)`.
Reproduced: a live second scan gives `reuse/unchanged` for every file; the replay of that same scan
gives `recompute/first observation` for every file, and a second replay into the same database gives
the same. `VERDICT_REUSE` is unreachable on the replay path under any sequence. SPEC:125 requires
*"identical exclusion **and cache** verdicts"*. The single Done-means-14 test replays a **first**
scan, where every live verdict is also `recompute` — it asserts the contract for the one input where
the bug is invisible.

**HIGH — the ratified rule's "system location" half is unreachable.** SPEC:38 says *"An application
bundle, a macOS package, and **anything under a system location** is a protected container"*, and
SPEC:63-65 says *"Membership of the protected set is authored, not inferred."* The extension-based
rule is implemented. The location-based rule has a hook — `exclusion_for(..., is_protected=…)` —
that nothing can reach: `walk`, `_walk_root`, `scan` and `replay` never take or forward it, and
`grep -rn "is_protected" src tests` shows the keyword supplied only from two test files. A deployment
cannot author the members even if it wanted to.

| Other findings | Sev |
|---|---|
| `require_access` opens a protected container's directory listing (`os.scandir`) before any exclusion rule runs — `scan.py:39` calls it before `walk` can reject the root | MEDIUM |
| `PLAN.md:5440,5450` still state the **opposite** of the ratified rule — *"macOS packages and application bundles **are descended**"* — and the PLAN has no protected-container task at all. The next agent to re-verify this plan would read the shipped protection as an over-build to remove | MEDIUM |
| Two unreachable lines after a `return` in `record_basic_record` (`basic_record.py:103-104`), and the stat-observation event is hand-built inline at `:96-101` duplicating `append_stat_observation` at `:107-117` | LOW |
| Rule precedence means `node_modules` beside a `package.json` is filed under "software project root descendant", so §8.6's per-rule counters will show near-zero for the literal-name rule on real corpora | LOW |
| R6 `directory_inventory` has no reader outside P3 (consumer is P10, unbuilt) — expected, recorded so it is not mistaken later for a column with no writer | NOTE |

**Fix first:** B1. Then the replay cache-verdict divergence, which is a promise the code cannot keep.

---

### P4 — Evidence shape · CONFORMS WITH GAPS
`src/evidence_shape/` · 14 files, 2,579 lines · baseline **405 passed** · 8 of 9 guards live

**The single-shape claim is true and was proved three independent ways.** `graphify affected
"Observation" --depth 2` enumerated the complete consumer set; grep over all of `src/` for the two
fields a format branch could read found the only hits in `src/facts/` are *comments saying the
branch is absent*, and `src/grouping/` and `src/llm_harness/` do not contain the string `source_type`
at all; and a *runtime* introspection guard over every module in `facts` (AST code-strings, not text)
fired when a real `observation.source_type == "image"` branch was injected. The positive case is held
too: `test_p6_reads_an_observation_whose_source_type_it_has_never_seen` reads a `design_creative`
fixture nothing in `facts` was written against.

The gaps are in **what P4 publishes about the shape** — which is exactly where a contract part can do
damage, because six extractor authors and five consuming parts read `CONFORMANCE_RULES` as the
contract.

**HIGH — rule 9's published text names three completeness values; the code enforces five, and the
comment above the enforcement asserts the superseded reading.** **CONFIRMED BY LEAD.** Three
statements, three different answers, within forty lines. `src/evidence_shape/conformance.py:56-57`:

```python
    9: "run.completeness present; unsupported, deferred and failed runs carry zero "
       "observations. Checked by check_run.",
```

`src/evidence_shape/conformance.py:249-251`:

```python
    # Rule 9. The SPEC's three, and no others: M3 keeps `unreadable`, `partial` and
    # `metadata_only` carrying the metadata-level rows §2.9's "indexed" means.
    if record.completeness in ZERO_OBSERVATION_COMPLETENESS and members:
```

`src/evidence_shape/vocabulary.py:75-76` — the thing actually evaluated:

```python
ZERO_OBSERVATION_COMPLETENESS: tuple[str, ...] = (
    "unsupported", "deferred", "failed", "metadata_only", "dataless")
```

Five values, and `metadata_only` is one of them — i.e. it carries **zero**. That is the frozen
reading (SPEC:640-648, *"settled 2026-08-20, because this sentence and the SPEC's own worked example
19 said opposite things and six extractors would have run the gate"*). `vocabulary.py:70-74` gets it
right and explains it; the comment at `conformance.py:249-250` is the pre-ratification text and was
never updated. **Concrete failure mode today:** a P5 author implementing §2.9's safe default reads
`CONFORMANCE_RULES[9]`, sees `metadata_only` is not in the zero list, emits the format's metadata
rows on the stopping run — and is rejected by `validate_run`, after writing the extractor.

**SILENT guard — rule 4's round-trip inequality can never fire.** Replacing
`conformance.py:201` with `if False:` left 403 tests green. A reachability probe enumerated 5,220
structurally valid `Location`s across all 15 zones, 7 segment kinds, 17 adversarial labels
(`docs/transcript.pdf`, `dc:title`, `%2F`, `%zz`, `中文`, `\U0001F600`, `\x00\x01`, …) and 3 span
states: `tried=5220 fired=0`. The branch is unreachable by construction. The test named for it
injects a malformed locator *string*, which raises inside `location_from_mapping` and is caught by
the surrounding `except` — it exercises the exception path, never the comparison.

| Other findings | Sev |
|---|---|
| The validator's docstring claims it *"reports every violation before raising"*; two short-circuits (`:193`, `:209`) suppress the entire constructor-level class as soon as any earlier rule fires. Demonstrated by four probes. The existing test only uses rules that live above the boundary | MEDIUM |
| Rule 8's published text names three key fields; `REPLAY_KEY_FIELDS` uses four; and `determinism.py:22` says the revision *"is not P4's to make"* — while ratification A1 (2026-08-20) already made it | MEDIUM |
| `NULLABLE_FIELDS` has five members; the SPEC states three; the comment above it claims conformance with the rule the constant breaks; and a test pins the code's answer, locking the divergence in | MEDIUM |
| `location_from_mapping` silently drops an unknown region key — the exact defect `REGION_KEYS`' own comment documents as fixed. The fix was applied to the write path only | MEDIUM |
| **P4 publishes no predicate for its own citation handle**, so P7 wrote a private `_is_observation_key` (`privacy/classification.py:92`) and five downstream fixtures cite `"obs-key-1"`, a handle no live `Observation` could produce | MEDIUM |
| `COMPLETENESS`'s comment says "eight"; the tuple has nine (C4 added `dataless`) | LOW |
| SPEC Done-means 5 still demands "all 14 zones and all 14 source types" after B8 amended it — and there are fifteen zones, so the un-amended sentence was already wrong | LOW |
| The no-per-format-branch runtime guard covers `src/facts` only; `grouping`, `llm_harness` and `privacy` are clean today by grep but unguarded | LOW |

**Fix first:** rule 9's published text and its comment (two edits, no behaviour change) plus a test
asserting `CONFORMANCE_RULES[9]` names every member of `ZERO_OBSERVATION_COMPLETENESS`.

---

### P5 — Extractors and readers · CONFORMS WITH GAPS + BLOCKER (B4)
`src/extractors/` (23 files), `src/readers/` (4 files) · baseline **396 passed** · 3 silent guards

One of the more disciplined parts: six extractors share one shape and the shape is P4's, not a
restatement; every library and threshold is an injected callable with no default; the safety gate is
the **first statement of all eight** extractor entry points; §2.6's three traps are all implemented
and tested against the SPEC's named fixtures; and §2.5's absolute prohibition is kept by
construction — `archive.py` imports no archive library and a real-ZIP test asserts byte-equality of
the whole tmp tree.

**BLOCKER (B4) — sensitivity signals are mis-keyed, and the scan crashes on an ordinary email.**
`long_tail.py:246` records `observation_index=len(observations) - 1` — a position in the list
`extract_long_tail` built. `sink.py:49` then collapses that list on `(zone, raw_value)` in
`ExtractionResult.__post_init__`. Every index after the first collapsed duplicate is wrong.
Reproduced with an email whose `From` and `Reply-To` carry the same address: the signal raised for
`Reply-To` lands on the **Subject line**, so §2.9's *"addresses are potentially sensitive"* is
recorded against the wrong value and P7 would gate the wrong row while releasing the address. With
three copies of one address, `record_sensitivity_signals` raises `IndexError` — and its call sites
(`orchestrator.py:426`, `:588`) are **outside** the `try/except` that converts a reader failure into
a `failed` run. An ordinary `.eml` ends the scan.

This is the exact defect `Dispatched.__post_init__` was written to prevent (its comment records
*"the Wave-2 caller resolved E3's signals against the FILESYSTEM run's keys for a day"*), reappearing
one layer down — against the right run and the wrong row.

**HIGH — the ratified OCR language set never shipped.** SPEC:410-412 ratified *"English, CJK
(Chinese, Japanese, Korean), and Western European"* on 2026-08-20.
`src/readers/deployment.py:36-40` ships `"languages": ["en-US"]`. Vision with `en-US` on a CJK scan
returns transliterated noise, the run is stamped `complete`, and the noise becomes evidence P6 ranks.
The repository knows the right answer — `tests/p4/*` use `["en", "zh-Hans"]` throughout.

**HIGH — SILENT: §2.7's three explicit Vision settings are untested where they are set.** Changing
`VISION_CONFIG` to `["xx-YY","zz-ZZ"]` → **396 passed**. Changing it to `dpi: 72,
recognition_level: "fast"` → **396 passed**. `tests/readers/test_ocr_vision.py:48` defines its *own*
`ACCURATE` constant and tests the engine against it — proving the engine honours what it is handed,
and nothing about what the deployment hands it. There is no `tests/readers/test_deployment.py`, and
`deployment.py` is also the one adapter the "no product vocabulary" guard does not cover.

**HIGH — P4's ratification B4 is unimplemented: `context_window` never reaches
`extraction_runs.config`.** **CONFIRMED BY LEAD.** Verified:

```
$ grep -rn "config={" src/extractors/
docx.py:211 / archive.py:184 / pdf.py:176 / structured_text.py:183 / image.py:201   config={"reader": "injected"}
long_tail.py:308                                        config={"reader": "injected", "transcribe": transcribe}
filesystem.py:107,160,227 · failure.py:76,98 · budgets.py:74                        config={}
$ grep -rn "context_window" src/extractors/ | grep config
(no output)
```

Every extractor consumes `context_window` to build P4's three context fields and none records it.
Two runs at window 20 and window 400 produce different observations and an **identical**
`config_fingerprint` — so §3.4's cache serves the stale one and §8.5's replay reports no divergence.
P4's B4 names this exactly: *"A ceiling outside the fingerprint makes two runs at different context
widths look identical — a silent wrong answer."* Note the secondary half: P1's sixteenth ceiling key
`evidence.context_window` has no reader anywhere; every caller hardcodes `context_window=40`.

**HIGH — SILENT: the "no global language-quality check" guard is name-based.** A working alpha-ratio
heuristic named `_alpha_share`, wired into the pre-P6 OCR route with an inline `0.4`, left
**431 passed**. That is a global language-quality check routing maths-heavy and CJK documents to OCR
— the exact thing §2.2 forbids and §2.7 repeats. (Putting the same heuristic inside
`text_layer_state` *did* go red, 9 failures, so the other half is covered.)

**SILENT — the extractors↛readers layering guard, two independent ways.** It fires correctly when
run from the repo root with the dependencies installed. But it globs a **relative** path
(`Path("src/extractors")`), so from any other cwd the assertion is vacuous — `1 passed` with
`import pdfminer` live in an extractor. And it sits behind three module-scope `importorskip` calls,
so on a machine without the `readers` extra the whole module is skipped — which is precisely the
machine the rule *"P5 adds no third-party runtime dependency"* exists to protect. `tests/p5/` has no
layering guard of its own: 363 passed with the violation live.

| Other findings | Sev |
|---|---|
| §2.9's opaque-binary family gets `unsupported`, not `metadata_only` — probed: `.exe`, `.iso`, `.sqlite`, `.db` all `unsupported`, only `.dmg`/`.bin` correct. And `unrouted_result` writes `source_type="opaque_binary"` with `unsupported`, two statements that contradict each other | MEDIUM |
| §2.9's *"message content as potentially sensitive"* has no home: `body` is deliberately absent from `WHOLE_TEXT_ZONES` and the signal table is keyed per-observation, so an email body with no structured-string match reaches the database unflagged | MEDIUM |
| B6 ratified that spreadsheets and presentations ship at launch and that `unsupported` "now means a format genuinely has no extractor" — `deployment.py:73-77` wires `_no_reader` for docx, long-tail, manifest and image, so `.xlsx`/`.pptx`/`.docx`/`.zip`/`.png`/`.heic` all record `unsupported` | MEDIUM |
| A scanned PDF on a deployment with no OCR engine is recorded **`complete` with zero observations** — the database states a photographed page genuinely contained nothing. §8.6 forbids exactly this | MEDIUM |
| Only `.zip` routes to E4; `.tar`/`.gz`/`.7z`/`.rar` are `unsupported`, though the PLAN names stdlib `tarfile` | LOW |
| `readers/ocr_vision.py:148-150` defaults three settings its own docstring says must never be taken privately, three lines below the docstring | LOW |
| The six deferred catalogues have no loader anywhere; the assembled `Readers` supplies constant-empty strategies, which the PLAN predicted would mean "no citations, no camera filenames, no project markers — with nothing failing" | NOTE |

**Fix first:** B4 — it crashes the scan.

---

### P6 — Facts and facets · CONFORMS WITH GAPS + BLOCKER (B5)
`src/facts/` · 29 modules, 5,624 lines · baseline **568 passed** · **9 of 9 sabotages LOUD, zero silent guards**

P6's spine is genuinely built. The six reliability states are P4's tuple **by identity**, not a copy.
`src/facts/` imports nothing from `llm_harness`, `privacy`, `grouping` or `templates`, and that is
enforced by an executable import-delta guard. C-5 is correctly still open — P6 publishes neither
`normalize(` nor `contradicts(`, and a guard fires the moment either appears. The §3.4 cache key has
no path input and inverts on all five parts. Done-means: 28 PASS, 1 PARTIAL, 1 FAIL.

Almost every gap below is **documented in the code that carries it**. That is a real strength of this
codebase's discipline and simultaneously why the green suite is misleading: the modules confess, and
nothing fails.

**BLOCKER (B5) — Done-means 22 fails end to end.** `src/facts/resolver.py:172-176`:

```python
        # §2.2 fires before ranking. The return value is the survivor set;
        # stages that re-query observations still use field_permitted.
        # This call is what writes the unresolved row Done-means 22 requires.
        self._screen_metadata(conn, file_id, content_hash)
```

The return value is discarded, and the second comment line is false. Verified:

```
$ grep -rn "field_permitted" src/ tests/
src/facts/resolver.py:174:        # stages that re-query observations still use field_permitted.
src/facts/discount.py:113:def field_permitted(observation: Observation, field_key: str, *,
tests/p6/test_p6_discount.py:22,161,207,210
```

The only reference in `src/` outside its own definition is that comment. It is also structurally
impossible for a stage to receive the survivors: `Stage = Callable[[Connection, str, str], tuple[str, ...]]`
(`resolver.py:33`) has no channel for them, and every stage re-reads
`observations_for_version(...)`, which returns the **unfiltered** set.

Proven by driving the production `apply_rules` stage after the production `screen_metadata` call,
exactly as the resolver sequences them:

```
survivors after screening: []
unresolved rows: [('authored_by', 'discounted_tool_metadata')]
facts written by the rule stage: 1
   FACT field=subject value='python-docx' state=validated origin=rule
```

The SPEC requires *"no fact in any field and one `unresolved` row"*. The system writes the row **and**
the fact — and §2.2's own words, that such a value *"should not be mistaken for meaningful content"*,
are violated in the worst possible way: it became a `validated` `subject`. §2.3's demotion tier
(*"may populate an authorship role field and nothing else"*) is enforced by nothing at all.

**HIGH — `proposal_eligible` returns superseded and inactive facts.** **CONFIRMED BY LEAD.**
`src/facts/read_surface.py:143-152` filters on `reliability_state` and field scope only:

```python
    return facts_for(conn, file_id=file_id, content_hash=content_hash,
                     states=PROPOSAL_ELIGIBLE_STATES)
```

Proven by execution: after a supersession, both the old and the new conclusion come back
(`rows returned: 2`); an `active = 0` fact also comes back. Forty lines below, `values_with_counts`
in the *same module* gets it right — `WHERE active = 1 AND superseded_by IS NULL AND
reliability_state IN (...)` — and its docstring argues at length that *"the two reads in this one
module disagreed about the same file"*. The defect it names is still present, in the other direction.
This is the read P10 (§5.4) and P11 (§6.3) are promised as *"proposal-eligible facts"*: after any
§3.4 re-resolution, a template populating `subject` sees two competing values with no signal which
one the resolver preferred.

| Other findings | Sev |
|---|---|
| **HIGH** — `file_facts.cited_quote_refs` has no producer: `apply_verdict`, the only `llm_supported` writer, never passes it (probed: `'[]'` on every fact). §3.6's *"cited exact supporting text"* is indistinguishable from ordinary evidence, and P8's span-level checks leave no trace on the fact row | HIGH |
| **HIGH** — the catalogue ships two live keys for one concept: `target_school` (universal) and `target_university` (college_applications), both `destination_eligible=True`, against ratification D8. One corpus splits into two branches for one concept. The code names the violation openly and asks for a ruling | HIGH |
| Three `file_facts` columns have no producer (`cited_quote_refs`, `internal_score`, `rejection_reason`) and **no code path writes a `user_confirmed` or a `rejected` fact at all** — `record_correction` appends an event and returns. §8.7's *"a `user_confirmed` fact … or a `rejected` fact retained with the evidence"* is unimplemented | MEDIUM |
| `sensitivity_status` — one of §3.11's six universal fields — is knowingly absent. The reasoning is sound (D2 made P7's record authoritative) and there is a guard; this is a **SPEC** defect, not a code one: Done-means 2 still says "all six" | MEDIUM |
| §8.7's mandatory query-before-propose guard has no call site. `is_suppressed` exists, is correct, and the module's own docstring says *"IT HAS NO CALL SITE YET, AND THAT IS THE OPEN ITEM"* — including that the previous docstring's claim was untrue | MEDIUM |
| `write_unresolved` is non-idempotent: three identical calls write three rows, while `write_fact` (content-addressed) correctly collapses to one. The resolver works around it at the reader by snapshotting ids — the problem was met and patched at the reader rather than the writer | MEDIUM |
| `FactRequest.normalizers` crosses the P6→P8 seam and P8 does not use it — it uses a separately injected callback, and **both sides ship tests asserting the field is never called** | LOW |
| Five sites spell `unresolved` reasons as bare literals, against the rule their own `vocabulary.py:44-48` states — and five other modules do it correctly by import | LOW |

**Fix first:** B5. The `proposal_eligible` filter is a one-line second.

---

### P7 — Privacy and consent gate · GAPS + BLOCKER (see B2)
`src/privacy/` · 23 files, 6,397 lines · baseline **817 passed** · 9 of 10 sabotages caught

**The gate's architecture is load-bearing and I could not break it.** Fourteen attacks, and every
one that mattered failed closed: a hand-constructed `Released` is inert because `consume_release`
consults a ledger (`ReleaseNotIssued`, client calls = 0); a release is bound to
`(model_target, prompt_fingerprint, policy_version)` and spent exactly once; a cross-locality spend
raises `BindingMismatch` *before* burning the authorization; an unclassified file — which is **every**
file in a real corpus, because no detector exists — resolves to `Denied(unclassified)` and never to
`public_low`; `NeedsConsent` is returned unchanged by all five of its consumers; classification
cannot be inherited across a byte change; and `set_sensitivity_state` is imported at exactly one site
product-wide. The five handling classes and four operation modes are the design's own, verbatim, in
the design's order, with the design's prose pinned beside each identifier so a paraphrase fails.

**HIGH — Done-means 3's static single-egress property is asserted against nothing, and the
instrument would fail the shipped transport.** `tests/p7/test_p7_skeleton_step.py:400-408`:

```python
    transports = [module for _dotted, _path, module in src_modules()
                  if module is not None
                  and getattr(module, "IS_MODEL_TRANSPORT", False)]
    assert transports == [], "a transport appeared; run assert_single_egress over it"
    for module in transports:                      # reachable the day P8 lands
        assert_single_egress(module)
```

The `for` loop iterates a list the line above asserts is empty — a check that can never fire.
`grep -rn "IS_MODEL_TRANSPORT" src/` returns one writer and it writes `False`; the reserved name has
no producer, and `src/llm_harness/transport.py` declares nothing.
`transport_guard.py:27-28` still asserts *"there is no transport module in this repository"*, which
is now false. The auditor pointed the instrument at the real transport: **it fails**
(`UnreleasedContentParameter: ModelClient.__init__(invoke) accepts <class 'bytes'>`). That verdict is
arguably a false positive — the bytes are only constructible from a live `Released` — but that
argument has never been made or recorded anywhere, because the check has never been pointed at its
subject.

**HIGH — three of §8.4's four consent options never close their consent request.**
`policy.grant_consent` appends `consent_granted` without the `consent_request_id`
(`policy.py:302-306`; `_explanation` at `:230-245` builds seven keys and not that one). Only the
`no_model_use` branch writes it. So `consent.pending_consent` returns the open question forever after
`local_model`, `cloud_model` or `redacted_prompt` is recorded, and `ConsentAlreadyRecorded` never
fires for those three. Probed:

```
  pending before answer: True
  pending AFTER a recorded local_model answer: True   <-- the guard is dead
  SECOND answer on the SAME consent id ACCEPTED
  pending AFTER no_model_use: False                   <-- works in this direction only
```

The asymmetry is exactly backwards from the stated intent: the guarded direction is turning a
recorded `no_model_use` into a `cloud_model`; the **unguarded** direction is the one where consent was
actually *granted*. The only closure test exercises `no_model_use`.

| Other findings | Sev |
|---|---|
| `AuditRecord.release_id` has no writer — all three producers write `None`, correctly and by construction (§6 puts the append strictly before the release id exists) — yet `audit_records_for(release_id=...)` is published as a filter and always returns `[]`. The test that covers it hard-codes `release_id="release-1"`, a value no production path can emit | MEDIUM |
| The `unclassified` denial — the one the module's own docstring says the audit log will be full of — prints a JSON literal to the user (*"its extraction completeness is '{}'"*), and its honest alternative branch can never fire because P1's column is `NOT NULL DEFAULT '{}'` | MEDIUM |
| W1's local-first floor has no production caller: `resolve_default_policy`, `effective_policy` and `assert_local_first` are called only from tests. The gate fails **closed** so there is no egress risk, but §8.4's `must` is enforced today only by a function nothing calls | MEDIUM |
| Two dead readers and one duplicated implementation inside P7: `classification.sensitivity_signal_keys` and `items.sensitive_observation_keys` are the same loop; only the second has a caller. `policy.transcription_authorized_for` is never wired to P5's `transcription_authorized` seam, so §2.9's speech-to-text authorization is unenforced in practice | LOW |
| `Gate.__init__` defaults `template_for=None`, which skips §7.3's `protected_records_template` rule entirely — a fail-open default on a §7.3 rule, four lines from `items.check_item`'s docstring refusing precisely that shape for the same reason | LOW |
| `Gate.release`'s two writes are not in one transaction, unlike every other writer in the module. The failure direction is safe (the audit over-reports) but the asymmetry deserves a sentence | NOTE |
| `planning/33-P8-COMPLETION-AUDIT.md:100` cites "P7 SPEC open question 4" for redaction reverse mapping; OQ4 is *"Deletion versus append-only"*. The substance of the claim is correct and verified; the question is genuinely **unowned and unrecorded**, which is worse than being OQ4 — and B2 makes it urgent | NOTE |

**Fix first:** B2.

---

### P8 — LLM harness and validator · **DOES NOT CONFORM** (see B3a)
`src/llm_harness/` · 20 files, 6,184 lines · baseline **496 passed** · 9 of 9 sabotages RED, 1 silent guard

Eleven of thirteen claimed invariants hold under active sabotage, and the sabotage evidence is
strong: rebinding the citation check from `dossier.released_evidence` to the P6 store turned **27
tests red**, including one named `test_raw_store_material_cannot_rescue_a_span_the_release_does_not_carry`.
The no-invention sweep is genuinely **derived** (it walks `pkgutil.iter_modules`), so the P8 failure
mode of a hand-listed sweep falling behind cannot recur. Determinism was proved by replaying through
the real dispatcher into a real P2 row byte-identically across two interpreters (`cmp` exit 0).

**BLOCKER (B3a).** Detailed in §4.

**HIGH — `SEARCH_HINT_ONLY` has no producer; Site A cannot return `weak`; §3.6's possible-clue
downgrade is unimplemented.** **CONFIRMED BY LEAD.** An AST census of every `_verdict(...)` call in
`fact_validation.py` returns `['ABSTAIN', 'ACCEPT_DIRECT', 'REJECT']`. Scanning every reason code
for a use outside `vocabulary.py` returns one: `NO PRODUCER: SEARCH_HINT_ONLY`. Done-means 2 states
the rule — *"A code with no fixture is an unimplemented check"* — and the whole `Possible` lane is
missing at the one site that owns it. `proposal_state_from_p8`'s `WEAK → POSSIBLE` branch can never
fire from production. The test that hides it constructs its own
`P8Verdict(outcome=WEAK, reasons=(SEARCH_HINT_ONLY,))`.

**HIGH — Site A ignores `EvidenceItem.basis`; a context-supported fact enters as `accept_direct`
with `requires_review=False`.** `fact_validation.py:252-256` returns `ACCEPT_DIRECT` unconditionally
on pass. The universal validator gets it right — `validation._acceptance_outcome:306-313` returns
`ACCEPT_CONTEXT_SUPPORTED` when every cited item's basis is context-supported — and Site A does not
call it. Proven live through `run_call`: a request identical to the passing fixture except
`basis=CONTEXT_SUPPORTED` returns `outcome='accept_direct'`. The SPEC's A-row disposition is
`accept_context_supported | LLM-supported + review`, and `records.py:416-419` enforces
`requires_review=True` on that outcome at construction — an invariant that is vacuous because the
outcome is never produced.

**HIGH — Site D's file-record check uses `location` as a file identity** (quoted in §3). Against any
conforming builder every Site D citation rejects; against a builder that happens to write file ids
into `location`, a citation to *another* file's evidence passes whenever that id matches.

**HIGH — `revalidate_for_plan` keeps only claim 0 and supersedes the old verdict with it.**
`placement_validation.py:605`: `fresh = result[0][0]`. A multi-claim C/D response loses every claim
after the first on a plan change: those verdicts are neither re-stamped nor superseded, so they
remain active under a plan version they were never validated against — precisely the silent
reclassification §8.8 forbids. It also links the supersession to a verdict about a different claim.

**SILENT guard.** `test_exactly_three_p7_branches_and_needs_consent_has_no_conversion_path` **passed**
under a sabotage that converted `NeedsConsent` into a `PreCallAbstention` — as did all 49 tests in
`test_p8_architecture.py`, `test_p8_no_invention.py` and `test_p8_records.py`. Its AST check looks
only for one coercion *shape*. The invariant is genuinely enforced (a different test caught it), but
the test carrying its name overstates what it proves.

| Other findings | Sev |
|---|---|
| The two-condition rule reports one code, not both: `placement_validation.py:246-254` short-circuits, so a claim failing support **and** margin reports only `BELOW_SUPPORT_THRESHOLD`. The SPEC says *"Both conditions are evaluated and both codes reported, so P2 can tell a low-support case from a close-call case"* — proven with `support=0.10, margin=0.001` | MEDIUM |
| Site E rejects with an empty `reasons` tuple in three places, so those rejections are invisible to `reasons_histogram` and to §8.5's failure attribution. Two existing universal codes fit and neither needs a new one | MEDIUM |
| P8's `REJECT` outcome constant is used as P1's learning **`polarity`** value (`eligibility.py:55`). P1 publishes no polarity vocabulary and P13, which will write these rows, does not exist. If the eventual producer spells it anything else, §4.9's stop rule and §8.7's suppression silently never fire | MEDIUM |
| `Claim` and `CallResult` are frozen records with **zero** producers in all of `src/`. `Claim`'s "exactly one of citations or Unknown" invariant is re-implemented inline in `validation._validate_claim`, so the contract lives in two places and only the copy is exercised | LOW |
| The `"supersede_verdict has no production caller"` note is stale — `placement_validation.py:622` calls it — though the claim survives one level up, since `revalidate_for_plan` has no `src/` caller | LOW |
| `store.record_dossier`'s read-then-insert is not in a transaction, unlike every other writer in the module | NOTE |

**Fix first:** B3a — one line at `harness.py:348`.

---

### P9 — Grouping · **DOES NOT CONFORM** (see B3b, B3c, B6, B7)
`src/grouping/` · 18 files, 4,604 lines · baseline **370 passed** · 4 BLOCKER, 5 HIGH, 2 silent guards

The deterministic spine is real and verified by sabotage: seeds honour a narrower anchor bar than P6
publishes; six retrieval channels exist and only one may anchor; the graph is typed, hub-suppressed
and bounded; five stop rules run before any dossier; SR1 and the support bar are genuinely two rules
(replacing SR1's predicate with the bar turned two tests red); the seed anchors itself (deleting it
turned **10** red); the eligible embedding set is cut before a single text is read (both halves red);
a context-supported membership and its `pending-review` row are one transaction (both presence and
atomicity red); acceptance is the only plan-versioned record. The privacy withholding is real, names
what it withheld, and both halves went red under sabotage.

**BLOCKER B6 — generic-hub suppression destroys a group because it has more evidence.**
`src/grouping/retrieval.py:180` describes *every* file that independently states the basis value with
the **same** string, `detail=f"{seed.field_key}={seed.value}"`. `graph.py:160` promotes that
description to an entity identity (`bridge = neighbor.detail`), `graph.py:118-133` counts it, and
`anchoring_files` then discards every suppressed edge. Probed with *n* files independently stating
`course_code=PHYS1401` at `generic_hub_frequency=3`:

```
2 independent anchors: hub_suppressed=[False,False]  anchoring_files=3  outcome=None
3 independent anchors: hub_suppressed=[True,True,True]   anchoring_files=1  fired=('SR3',) outcome=no-group
5 independent anchors: hub_suppressed=[True x5]          anchoring_files=1  fired=('SR3',) outcome=no-group
```

§4.3 asks the rules to *"count how many anchor documents independently state the same course"*; this
code punishes that count. §4.9's SR3 is *"one high-frequency entity acts as the only bridge"*, and
the design's own examples are a personal email address and a broad university domain — an entity that
bridges files **across unrelated groups**. Counting occurrences *inside one group's own
neighbourhood* measures corroboration, not genericness. `generic_hub_frequency` is a mandatory
injected positive integer with no default, so **no value escapes this**: any threshold destroys every
group with that many anchors. Four of the six channels emit a constant-per-group `detail`, so the
inversion applies to each. It also corrupts the recorded stage: the same neighbourhood reports SR2 at
frequency 9 and SR3 at frequency 3, and SR2 is the rule Done-means 4 singles out.

**BLOCKER B7 — §4.7 purpose detection is absent.** `grep -rni "purpose" src/grouping/*.py` returns
three comment hits and no code. SPEC Done-means 6 names the exact fixture (ID / transcript / resume /
statement / certificate / portal screenshot) and PLAN Task 8 Step 1 spells the requirement including
its negative. None of it was built and Task 8 was marked done.

**HIGH — the pipeline's P8-accepting path has zero test coverage, and zero production wiring.**
Mechanical line coverage (built by hand with `sys.settrace`, reproducing 370 passed) shows
`pipeline.py:329-334` never executes. Line 325 *is* covered and 327-328 (the `is None` early return)
are covered — so every test's injected `p8_run_call` returns `None`, and `group_subject` has never
once produced a membership from a P8 verdict. Nor does production: `grep -rn "p8_run_call" src/`
finds only the docstring, declaration, guard and call, and no module outside `src/grouping/` imports
`grouping`. **Between them, the path is exercised by nothing at all** — which is the proximate
reason B3b and B3c survived, and the reason B3b's `TypeError` is latent rather than live.

**HIGH — most of §4.5 is typed but not produced.** `_group_for` is the only production constructor of
`Group`, `groups` is append-only with an UPDATE trigger, and nothing supersedes a group — so these
are **final**: `coherence_verdict`, `display_label`, `group_category`, `label_source`, `conflicts`,
`stop_rule_hits`, `dossier_id`, `llm_response_ref`, `validation_verdict_ref` and `sensitivity_state`
have no production writer. §4.5 task 1 (coherence) and task 4 (label + category) are not
implemented. P10 aggregates accepted groups by `group_category` (§5.1) and has nothing to read.

**HIGH — `Group.state` can never become `supported`.** `meets_support_bar` — the function whose
separateness from SR1 is load-bearing rule 2 — has no production caller. Verified:

```
$ grep -rn "meets_support_bar" src/ tests/
src/grouping/graph.py:262:def meets_support_bar(
src/grouping/graph.py:298:        # `meets_support_bar`, and it decides `supported` rather than existence.
tests/p9/test_p9_pipeline.py:235,242 · tests/p9/test_p9_stop_rules.py:151,156,157,159
```

The guard test reaches into the module and calls the bar itself to demonstrate a rule the pipeline
never consults; its asserted `result.group.state == CANDIDATE` would hold either way.

**Two SILENT guards.**
- The no-fact-write guard walks `ast.Name` only. Three real fact-writing calls through an import
  alias and a module attribute left **370 passed**. This is not hypothetical: `src/facts/direct.py:59`
  already uses the alias form, so it is idiom in this codebase.
- Adding a `nodes` property to `LocalEvidenceGraph` — the exact thing the record's own rationale
  forbids — left **346 passed**. `test_p9_no_invention.py:222` bans `node_id`, `parent_node` and
  `node_type` but not bare `nodes`.
- And a third, on ordering: moving `evaluate_stop_rules` to *after* `assemble_group_dossier` left
  **354 passed**, including the test literally named
  `test_a_fired_stop_rule_costs_no_dossier_and_no_call`, whose only assertion is `calls == []`.
  Moving it after `p8_run_call` *does* go red — the "no model call" half is guarded, the "no dossier"
  half is not.

| Other findings | Sev |
|---|---|
| §4.2's pre-model outlier flagging does not exist: `engine_flagged_outliers=()` and `outlier_flag=NOT_FLAGGED` at every site; three of four `OUTLIER_FLAGS` members have zero references anywhere | HIGH |
| The retrieval cap truncates arbitrarily: with no injected channel weight, ordering collapses to `content_hash`. §8.6 requires reduction *"to the strongest anchors and the highest-quality edges — it does not truncate arbitrarily"*. `build_graph` honours this for the node cap; the retrieval cap runs first and does not. `DEFAULT_CHANNEL_ORDER` exists with exactly that comment and is never referenced | HIGH |
| One of §4.3's five pre-model computations is implemented, and the two injected authorities that would supply the others (`active_schema_for`, `signal_evaluator_for`) are **required and never invoked** — guarded by two tests that assert the placeholder is demanded rather than used | HIGH |
| A real run persists no typed edge, no dossier and no stop-rule outcome, and appends no `graph-edge creation` event: `record_edges`, `record_dossier` and `record_stop_rule_outcome` are fully implemented, tested, and called by nothing in `src/` | MEDIUM |
| Direct-anchor support is derived from excerpt presence, not from the Direct/Validated fact. An anchor with a validated `key_fact` and no resolvable excerpt raises `MalformedGroupRecord` **inside** the transaction — probed | MEDIUM |
| `_rehydrate`'s four-arm dispatch is entirely unreachable: it is only ever called with `AnchorFact` or `Conflict`, neither of which has any of the four named fields. Coverage confirms lines 83, 85-86, 88-89 never execute. It reads as proof that nested `support` and `conflicts` round-trip; neither is ever exercised through that path | MEDIUM |
| Done-means 3 (§4.6, the design's central worked example) is asserted against `course_dossier_fixture()`, not `assemble_group_dossier` | MEDIUM |
| `sensitivity_state` is a closed vocabulary with no validator (`_require` checks non-emptiness, not membership), no producer and no consumer | MEDIUM |
| Golden fixtures violate the production invariant `dossier_id == dossier_fingerprint`, so P8/P10/P11 building against them may or may not learn the real rule | LOW |
| P9 labels a live model call that returned `None` as `no_model_call_configured` — a reason that denies the call happened, under a comment stating the opposite intent. MEDIUM rather than HIGH because live P8's declared return union excludes `None`; only a test double reaches it | (seams) |

**Fix first:** B6 — it is the only defect here that makes the product actively worse the more evidence
it has.

---

### Seams — connectors, invariants, the walking skeleton · GOOD, 2 HIGH
0 BLOCKER · 2 HIGH · 3 MEDIUM · 2 LOW · 6 NOTE

**The signatures hold, and this is the strongest positive result in the audit.** Bound against live
signatures rather than traced through the graph: **306 direct cross-part call sites in `src/`, none
of which would raise**, and **48 of 48 `Callable` seams with a declared arity match their
invocation**. Of the five seams that declare `Callable[..., X]` and are therefore unchecked, four
bind cleanly against the production callable they stand for and one does not — `p8_run_call`
(Blocker 3b). Every adjacent pair P1→…→P9 has a live, signature-compatible connector **except**
P8→P9, whose row should read: *connector present, types INCOMPATIBLE, not tested against the real
callee, and unwired in production.*

This corrects an earlier claim in the seams report. Its adjacent-pair table was built from
`graphify path`, and for nine of ten rows the conclusion survives the stronger test — which the
auditor correctly called *"luck, not method"* rather than vindication. See §1's method note.

**All five whole-product invariants hold.**

1. **Single model egress.** `grep -rn "\.invoke(" src/` returns exactly one line,
   `src/llm_harness/transport.py:178`. `grep -rn "def invoke" src/` is empty.
2. **No part writes another part's table.** Probed with an AST walk that extracts SQL from real
   string literals and skips docstrings (necessary — P7 carries four docstrings containing the phrase
   `UPDATE files` saying it does not do it). All ~150 write statements land in the owning package.
   The one projection onto P1's column goes through P1's own setter.
3. **Import direction, all three rules clean.** `src/extractors/` never imports `readers`,
   `pdfminer`, `Vision` or `Quartz`; `src/facts/` knows nothing of destinations, tree or placement;
   `src/grouping/` never calls `write_fact`, `ensure_value` or `apply_verdict`. The full package
   direction map is acyclic and nothing imports P10–P13.
4. **`NeedsConsent` is never coerced** — all twelve handling sites return it unchanged or raise.
5. **Determinism** — the product's canonical serializer is byte-identical across three independent
   interpreters under three `PYTHONHASHSEED` values, and a pristine `git archive` extract of `b7c6e8f`
   gave `3621 passed` twice.

**Authorship (M8) is implemented with unusual discipline.** P1 originates no `discovery`,
`stat observation` or `external modification detection` event anywhere in `src/`; every P1 call site
passes the caller's author through. Ten registered event types have no producer, and **all ten belong
to P10–P13**, which is the expected shape rather than the defect shape.

**HIGH — the walking skeleton's P2 step never replays a real run's bundle**, and **HIGH — the suite is
green in only one collection order**:

```
$ PYTHONPATH=src python3 -m pytest tests/p5 tests/p3 -q
E   ImportError: cannot import name 'FIXED_CLOCK' from 'conftest'
!!!!! Interrupted: 19 errors during collection !!!!!
$ PYTHONPATH=src python3 -m pytest tests/p3 tests/p5 -q
533 passed in 3.06s
```

Three files compete for `sys.modules["conftest"]` and the last imported wins. The repo already knows
— `tests/p7/conftest.py:12-18` and three other files document the mechanism at length — and six
directories were given an `__init__.py` as a shield. `p3`, `p5`, `integration`, `readers`, `wave2`
and `tests/` itself were not, and **p3 and p5 are the two unshielded directories that both carry a
`conftest.py`**. The defence is alphabetical luck. Any CI that shards by directory re-breaks it.
Note this bounds invariant 5: determinism holds *per collection order*, not across orders.
`src/` itself is clean and structurally cannot have this problem — zero relative imports, zero
`sys.path` manipulation, every import package-qualified.

| Other findings | Sev |
|---|---|
| `events.subsystem` means "author" for 34 event types and "performer" for one (V1–V4 `hashing`). The SPEC states both halves four lines apart. A consumer following the SPEC's own instruction to *"filter on `subsystem`"* silently also matches P12's rows and cannot recover P12 without parsing free-text JSON. **The skeleton's own M8 assertion is order-dependent**: it passes only because it runs before `verify_content` | MEDIUM |
| No single test walks the corpus across all built parts. Four overlapping segments exist; the P9 skeleton in particular uses a literal `Observation` rather than a real extractor's output, notwithstanding its docstring's claim that *"nothing here is a fixture standing in for a neighbour"* | MEDIUM |
| P9's SPEC-mandated grouping seam has no orchestrator, and unlike P8's absence — which `production.py:5-6` declares — P9's absence is not declared anywhere | LOW |
| `run_wave2` remains public, seventeen parameters, no privacy gate. Well documented and well fenced by tests; the fence is documentary, not mechanical | LOW |
| P6 and P7 both import P5 — checked against the acknowledged back-edge list and these are **forward** dependencies on published P5 vocabulary, not back-edges. No action | NOTE |
| P7 ships no detector, so a live product classifies nothing and every real file resolves to `Denied(unclassified)` — *"a correct, locked door with nobody holding a key"*. Deliberate, fail-closed, honestly labelled. It bounds what "P1–P7 is live" means | NOTE |
| All three acknowledged back-edges (P5→P7, P8→P10, P8→P11) are mediated by injected callables with no defaults, never by imports. Fixtures are content-free contract witnesses and are verified leaves | NOTE |
| No degradation path anywhere in `src/` silently downgrades instead of abstaining. Every exhaustion path in P4, P5, P6, P8 and P9 terminates in an abstention or a refusal. Recorded as a positive result | NOTE |

**Fix first:** the five missing `tests/*/__init__.py` files (mechanical, removes a class of bug), then
one integration test joining `run_p1_p7(...).bundle_id` to `replay_bundle`.

---

## 6. The plans: P10 and P11

Neither part is built. Both plans were rewritten after a prior audit condemned them, and both
rewrites are substantial improvements. Both are **executable with fixes**, and the fixes are not
cosmetic.

### 6.1 What P10's plan gets right

**It closed 30 of the prior audit's 38 MISSING requirements** (37 distinct; A103 restates A19), and
the closures are real rather than nominal: the 22 mandatory node fields, the two reserved §8.2 events
with an actual producer, the eleven-field freeze record, `anchor_excerpts[]` cited by
`observation_key`, protected profiles redacted **at the boundary**, C1–C8 as eight independently
falsifiable named fixtures, the P3 seam including the three-value curation signal, and the ceiling
P10 owns.

**Every live symbol it names exists.** A script extracted all 63 `(module, name)` import pairs from
the plan and did `hasattr(importlib.import_module(mod), name)` against live `src/`: **63 checked, 0
missing.** Its twelve SPEC corrections were judged one by one and **none discards a requirement**;
several strengthen (correction 4 refuses to round `undetermined` to `incidental`; correction 8 adds
two unrepresentable dimension actions). Its module dependency graph is acyclic and forward-only, with
zero violations. Its no-invention sweep is **derived**, not listed, so the P8 failure mode cannot
recur. The publication boundary is enforced at two independent layers, and the guard is in Task 6
rather than only in Task 16, so it cannot be skipped by stopping early. Its treatment of the standing
user constraint is the best in either plan: `PROTECTED` is one of the five node types so the
container is *present*, `derive_accepts_placement` returns `True` for it only under an explicit
permission so it is *marked but never opened*, every node carries a non-empty explanation enforced at
construction, and `redacted_for_egress` strips the profile at the boundary.

### 6.2 What breaks in P10

**The plan's own code does not pass the plan's own tests.** Staged and executed:
`29 failed, 182 passed, 5 errors`.

| # | Blocker | Evidence |
|---|---|---|
| 1 | **P10 cannot build a tree.** `Node(...)` is constructed in production in exactly two places — residual projection and a row-reader. `apply_review_action` (`PLAN:7928`) handles `RENAME` and `IGNORE` and raises for everything else: *"action has no writer in this task; every tree edit action gets one, and an unhandled action must not silently no-op"*. **`ACCEPT` is not handled.** Verified live: `TREE_EDIT_ACTIONS` (`PLAN:634-638`) has 15 values — `ACCEPT, RENAME, MERGE, SPLIT, NEST, REPARENT, REORDER, IGNORE, DELETE, CREATE_MANUALLY, ADOPT_EXISTING, ENABLE_RESIDUAL, DISABLE_RESIDUAL, ADD_SCOPED_GENERAL, SET_SHARED_MATERIAL_POLICY` — and 13 have no writer in any of the 17 tasks. Nor does any module materialise a routed composition into child nodes: `materialise` is an injected callable. §5.4's *"Each template is populated from the facts and accepted groups that already exist"* and §5.12's *"evidence-backed proposed branches"* have **no producer after all 17 tasks**. **CONFIRMED BY LEAD** |
| 2 | Task 1's own guard tests fail against Task 1's own `vocabulary.py`: 59 values across 12 registry entries have no named constant, and the borrowed sets are *structurally impossible* to satisfy — the module's docstring says a borrowed vocabulary is imported never respelled, and the test demands a per-value constant. A sibling guard finds 26 literal offenders | BLOCKER |
| 3 | `project_residual_nodes` raises `MalformedTreeRecord` on **every** enable: `origin_node_id=""` is passed to a constructor that rejects empty strings, and `_with_origin` runs after construction. Six of seven residual tests fail | BLOCKER |
| 4 | `delete-suggested-area` is in `BRANCH_ACTIONS` but **not** in `TREE_EDIT_ACTIONS`, so §8.7's no-resurfacing rule cannot be recorded and three of the plan's own §8.7 tests raise `OutOfVocabulary`. Four §8.7-required actions (`defer`, `delete-suggested-area`, `relocate`, `flatten`) are outside the recordable set | BLOCKER |
| 5 | `AnchorFact.fact_id` does not exist. Live is `AnchorFact(field, value, file_ids, reliability_state, observation_key)`. The plan's fixture passes `fact_id=`/`field_key=` and omits the required `file_ids`; the **production** module `upstream.py:122` reads `f.fact_id`. Eight upstream tests fail with `TypeError`. The corrections table caught three P9 name divergences and missed this fourth | BLOCKER |
| 6 | The `## Required execution order` section and six ledger rows are numbered against an earlier 16-task draft and every bullet after the first is off by one. The dangerous one is **"Task 15 last"**: Task 16 imports `tree_design.freeze`, so an executor obeying it runs 16 before 15 and gets `ModuleNotFoundError` | HIGH |
| 7 | The ledger's P9 row is **stale**: it says `grouping/store.py` and `acceptance.py` "do not exist yet". Both exist and landed in three named commits. The conclusion survives (there is genuinely no *listing* reader) but the stated reason is false, and it mis-scopes the eventual swap | HIGH |
| 8 | §8.6's dossier-token ceiling is read into `TreeLimits` and consumed by nothing. *"summarise / preserve anchor excerpts / split / defer — never silent truncation"* has no implementation | HIGH |
| 9 | The no-resurfacing query runs only for top-level candidates: `suppressed_branch_basis_keys` is called once with `parent_node_id=None`, and `vertical_options` never consults it, so a nested branch the user deleted can be re-proposed | HIGH |
| 10 | Two of the plan's own no-invention guards fail on the plan's own code (a numeric-literal guard on `fixtures.py`'s ordinals; an event guard on `vocabulary.py`'s own import line). Both guards are right in intent and need narrowing | HIGH |
| 11 | The P10 test DB has no P2, P3 or P7 tables — `conftest.py` calls `open_database` + `create_fields` only, so `record_selection`, `ClassificationStore.current` and `record_version_tuple` all raise `no such table` | BLOCKER (mechanical) |

Three requirements remain **STILL MISSING** from the prior audit's 38: A5 (a `user-attached` member
must not be presented as evidence-derived — actively violated, the explanation string says *"share
validated facts"* over all members), A48 (the ordering doctrine: parent-provides-context,
project/subject before time, **photos the explicit exception** — no module computes or reviews it),
and A87 (the over-budget dossier rule above).

### 6.3 What P11's plan gets right

**Its live-API research is the most accurate thing in either plan.** Four of five spot-checked claims
verify to the character, and 44 of 45 named symbols exist with the exact spelling and signature —
including `_FOREIGN_OUTCOMES`' exact seven members, `CEILING_KEYS`' seven placement keys,
`learning_records`' positional signature, `SITES_REQUIRING_EVIDENCE_SNAPSHOT == {'C_placement',
'D_residual'}`, and `len(EVENT_TYPES) == 35` before P11's nine (35 + 9 = 44, which is what the plan
asserts — I verified the 35 independently). **Eleven of eleven** Site C check citations are correct,
including three exact multi-line ranges, so its central argument — that P11 writes none of Site C's
checks — is sound.

All three of the prior audit's "most serious gaps" are closed at the level of specification: the
placement record is enumerated field by field with validation, the P8 seam supplies authorities
rather than re-implementing Site C, and the three hard blockers (P1 event registration, the §6.4
node-local graph, the P13 receiver) each have a real task. Its strongest single construction is
Task 12, which plants *permissive* authorities and asserts P8 still produces `REJECT`/`INVENTED_NODE`.
Its strongest single test is `test_one_institution_is_never_chosen_over_another`, a property test
over both selector answers. Task 17 ("mark and never match") is the best-argued task in either plan:
`reproject` has literally no third branch, and its falsifier plants a plausible survivor and asserts
an empty result.

### 6.4 What breaks in P11

| # | Blocker | Evidence |
|---|---|---|
| 1 | **The deterministic exact-match path cannot clear the plan's own threshold.** `_CHANNEL_WEIGHT` gives `DIRECT_FACT: 3` out of `_MAX_WEIGHT: 7`; every fixture policy is `support_scale_max=1.0, minimum_support_threshold=0.5`. A lone direct-fact candidate scores `3/7 = 0.4286 < 0.5`. `meets_threshold` is `False`, so `unique_direct` is `False`, so **the walking skeleton's headline test fails**, along with two others. The plan proves the threshold is binding and never proves anything can clear it | BLOCKER |
| 2 | **Task 19 does not orchestrate.** `run_corpus` is promised and never implemented. `pipeline.py` imports nothing from `p8_seam`, `groups` or `residual`; `PipelineInputs.gate`, `.model_client`, `.prompt`, `.call_dependencies`, `.partition` are declared and never read. §6.12 steps 7 and 8, all of §6.8/§6.9's execution, and all of §7's workflow are specified in isolated modules and never wired. Nineteen good components plus an orchestration task that does not orchestrate them | BLOCKER |
| 3 | Every supersession write violates the plan's own partial unique index: `record_decision` INSERTs the new row before calling `mark_superseded` on the old, so two live rows exist at INSERT time for one `(plan_version, subject_ref)`. Two named tests raise `IntegrityError` | BLOCKER |
| 4 | Three more of the plan's own tests contradict the implementation printed beside them: a column-set assertion over 30 record fields against a 14-column DDL; an immutability test whose UPDATE does not touch any column the trigger guards; and a `grouping.vocabulary` import of `VALIDATED`, which does not exist there (it is `VALIDATED_SHARED_FACT`; the reliability state lives at `facts/states.py:45`) — that one raises `ImportError` at collection, taking Tasks 13 and 14 with it | BLOCKER |
| 5 | **26 test imports use `from tests.p11.…`**, a package path this repo does not have. `tests/` has no `__init__.py` and `pyproject.toml` sets `pythonpath = ["src"]` only, so the package is `p11`. The repo's own working idiom is `from p8.conftest import …` / `from p9.p13_fixtures import …`. Reproduced in a replica: `ModuleNotFoundError: No module named 'tests.p11'`. Every test file from Task 4 onward fails at collection. Mechanical | BLOCKER |
| 6 | The §8.7 negative-example loop does not close: Task 11's reader and Task 16's writer mint `basis_key` differently and look up a different `correction_subject`. A rejection recorded through P13 produces `basis_key="n-course->n-course"`; the reader searches for `"file:f1:h1->n-course"`. Both tasks pass their own tests while being mutually unusable | HIGH |
| 7 | `model_eligibility == "redacted"` is unreachable — `Policy.redaction_settings` is keyed on display facets, `handling_class` on handling classes, and the intersection is empty (checked). Worse, §8.4's redacted-prompt option is a **consent** choice that the derivation never reads, and `consent_audit_ref` is `None` at all three construction sites | HIGH |
| 8 | Done-means 7 has no producer: `decision_depth.unsupported_levels` is `()` at every construction, and no code selects a shallower approved node or a scoped `General` fallback. §6.7's central behaviour is representable and never produced | HIGH |
| 9 | §7.9's loop has a record and an event but **no re-entry**. `link_return` is a logger; nothing re-enters retrieval for a returned subject; `place_file` has no `returned_from` parameter; `check_return_cycle` is called from nowhere. This is the reason §6 and §7 are one part, and it is the one thing the fused part does not do | HIGH |
| 10 | Nothing verifies that the injected residual partition covers every unplaced file. A partition that omits files omits them silently — and the design's own example set is *"11 protected personal records"*. **This is the one place the standing user constraint is not held**, and it is conspicuous because the batching *inside* the function is careful (split, never truncate, with a sum assertion) | HIGH |
| 11 | `record_cd_verdict`, `revalidate_for_plan` and `evidence_snapshot_id_for` are never called from `src/placement/` — the only assertion is `assert callable(revalidate_for_plan)` | HIGH |
| 12 | `automatic_move_permissions` is keyed on **`file_id`** in live P7 (`moves.py:107`); the plan keys it on a handling class and re-derives a predicate P7 already publishes, whose docstring is literally *"May P11/P12 move this file without asking the user, under this plan version?"* | HIGH |

Twelve design requirements are **MISSING** in P11, clustering in three places: the two dossiers
(§6.6's eleven-item placement dossier and §7.7's ten-item residual dossier — **no task builds
either**, and `allowed_vocabulary`, the single most load-bearing value P11 hands P8, is named in
prose three times and constructed nowhere); §6.7's shallow-placement and scoped-fallback arms; and
§7.10's two required learning behaviours plus §7.11's lifecycle policies.

### 6.5 The seam that does not join

**P10 and P11 disagree in every record they share.** Verified live:

```
$ grep -c 'FrozenTree' P11=15  FrozenNode=6   FreezeRecord=0
$ grep -c 'FrozenTree' P10=0   FrozenNode=0   FreezeRecord=14
```

P11 uses `FrozenTree`/`FrozenNode` 21 times; P10 uses them zero times. P10 uses `FreezeRecord` 14
times; P11 uses it zero times. **CONFIRMED BY LEAD.**

P11's integration gate does `from tree_design.freeze import frozen_tree`. Verified:

```
$ grep -n "frozen_tree" planning/parts/P10-tree-design-freeze/PLAN.md
8762:def test_a_serialised_frozen_tree_holds_no_separator_composed_destination(seeded):
9220:def frozen_tree_fixture() -> FreezeRecord: ...
9240:    frozen_tree_fixture,
9362:    record = frozen_tree_fixture()
9889:def frozen_tree_fixture() -> FreezeRecord:
```

There is no `frozen_tree`. P10's `freeze.py` produces `FreezeRefused`, `FreezeRecord`,
`validate_for_freeze`, `freeze`, `legal_destination_ids`, `is_legal_destination` and two stage
emitters. The keyword is wrong too (`plan_version` vs P10's `plan_version_id`), and `FreezeRecord`
carries `node_ids: tuple[str, ...]` and no profiles, so it could not feed
`build_destination_index(conn, tree, …)` even if the name existed. Today the gate fails with
`ModuleNotFoundError`, which P11's plan calls correct; **the day P10 ships it becomes a permanent
`ImportError` on a name that will never exist**, and `src/placement/` — five modules across Tasks
6–9 and 13 — has been built against the wrong shape.

| Record | Disagreement |
|---|---|
| `FrozenTree` vs `FreezeRecord` | **Zero overlapping fields.** `nodes`/`profiles` (records) vs `node_ids` (strings); `shared_material_policy: str` vs `shared_material_policy_ids: tuple`; `scoped_general_parents` appears nowhere in P10 |
| `DestinationProfile` | P10 has 17 fields, P11 has 15. P10-only: `template_binding`, `anchor_files`, `anchor_excerpts`. P11-only: `anchor_excerpt_keys` — `anchor_excerpts` renamed *and* retyped from `AnchorExcerpt(observation_key, node_id)` to bare strings. Four further type mismatches (`expected_values`, `parent_context`, `child_context`, `restrictions`). `IndexEntry` copies P11's spellings verbatim |
| `Node` vs `FrozenNode` | P11 drops `origin_node_id`, which P10 calls structural (*"`node_id` is minted per plan version with an explicit `origin_node_id` lineage column"*) — and P11 miscounts its own list, promising 21 fields and listing 20. `template_context`: a record whose first required field is `binding_id` vs a dict with no `binding_id`. `refinement_disposition`: `str \| None` in P10, non-optional `str` in P11, and §6.7 branches on it |
| Legality projection | **Two homes for one published rule.** Both plans compute the identical legal-destination set and neither reads the other's. P11's own text argues *for* single-sourcing while creating the second source |
| Fixtures | P10 Task 16 is literally titled *"Fixtures P11 can build against"* and publishes four. **P11's plan never mentions `tree_design.fixtures`** and writes its own. Both cite resolution B8(b) for the same "second placeable node" requirement and then build two different fixtures to satisfy it |
| `plan_version` spelling | P11 uses `plan_version` 226× / `plan_version_id` 10×; P10 the reverse (172 / 35). Both spellings are live in `src/` (P8 uses one, P9 the other), so this is a decision nobody has made rather than a mistake |
| `node-hub` | P11 raises `NodeIdReserved` at index time. P10 mints ids through an injected callable, has **zero** occurrences of `node-hub`, and can therefore mint, store and **freeze** a node P11 will refuse to serve — with freeze immutable. The guard is at the reading end, not the minting end. The real defect is upstream of both: `src/llm_harness/placement_validation.py:239` carries a P8 *fixture* id into production Site C logic, where `payload.get("generic_hub") is True` already covers the intended case |

---

## 7. Templates and domain research

### 7.1 Answer to the standing question — "is building templates the next step?"

**No, on both halves.** Building templates is not the step after research lands — two research gates
and the entire P10 build sit in between. And template *contents* are not P10's job: P10 builds the
machinery templates run on; a separate plan authors the templates. P10's own plan says so in its
`## Explicitly unresolved` section: the 200–300 template contents, the fragment catalogue and the
compiler are owned by `docs/superpowers/plans/2026-08-26-composable-template-library.md` and gated
behind P10, and `tree_design.catalogue` *"reads a compiled manifest through an injected reader and
never locates one."*

The ordered sequence:

| # | Step | Owner | Status |
|---|---|---|---|
| 1 | Finish the research corpus — 358 roster rows, each `.json` + `.research.md` | domain swarm | **IN PROGRESS** — see live counts below |
| 2 | **R1c merge gate** — adjudicate refusals, the double-proposed shared fields, the edge backlog | R1c | **NOT STARTED** |
| 3 | Final review panel + index over the repaired corpus | research | **NOT STARTED** |
| 4 | **P10 build, Tasks 1–17** | P10 | **NOT STARTED** — `src/tree_design/` does not exist |
| 5 | **Template library, Tasks 1–9**, then `tools/compile_tree_templates.py` | library plan | **NOT STARTED**, and its own do-not-start gates forbid beginning |

Five gates must close first, quoted from the library plan: **G-DOMAINS** (rows ratified *and* the
swarm stopped), **G-P10** (the record types and composition gates exist), **G-FIELDS** (every
mapping targets the live P6 catalogue), **G-SELECTION** (Joseph approves a release-wave manifest),
**G-PROMPTS** (prompt wording never becomes a source of definitions). G-SELECTION is the only gate
whose closer is the user rather than an agent.

### 7.2 Live corpus state, re-measured while writing this

The numbers have moved since the auditor took them at 12:32 today, in the right direction:

| | At audit | **Live now** |
|---|---:|---:|
| Roster rows | 358 | 358 |
| Node JSON on disk | 300 | **316** |
| Complete (JSON + memo) | 292 | **313** |
| JSON-only partials (untrusted drafts) | 4 | **3** — `law_practice.estates-administration`, `manufacturing.asset-register`, `nonprofit.advocacy-campaign` |
| Owed | 67 | **45** |
| `refuse_node: true` rows | 37 | **37** |
| `check_edges.py` findings | 1462 across 300 rows | **1537 across 316 rows** |

Both state documents are stale against this. `planning/26-research-dispatch-state.md:3` still says
*"147 of 358 rows landed, 211 owed"*, and its owed-by-family breakdown names *"creative 42"* when
creative owes one. The run log's newest inventory says 283/8/67. The resume **query** is correct and
self-correcting; the **prose** around it is not, and a reader who trusts the prose will re-dispatch
finished families. The partials list is also wrong by membership, not just by count — at audit time
`nonprofit.political-campaign` was a live untrusted draft appearing in neither document.

**R1c is scoped six times too small.** §0b names six refusals; disk carries **37**, including whole
clusters mentioned nowhere: five `engineering.*`, nine `creative.*`, five `law_practice.*`, four more
`construction_property.*`, two `government.*`, two `nonprofit.*`, four `clinical_practice.*`. A
refused row cannot become an applicability source, so ~10% of the roster is already out of scope for
any release wave — which also sizes G-SELECTION. Note the roster (358) is *larger* than the design's
eventual 200–300 library, so G-SELECTION is doing real work: the roster is not a release list.

**G-DOMAINS is open on both clauses.** `planning/29-DOMAIN-OWNERSHIP.md` gained a handover section
today releasing 8 ids to CODEX for a 16-row two-hour block. Two teams are writing
`planning/domains/nodes/` concurrently. The gate is behaving correctly — it is open and it says so.

### 7.3 The confirmed G-P10 defect

**CONFIRMED BY LEAD.** `docs/superpowers/plans/2026-08-26-composable-template-library.md:26-27`:

> **G-P10:** P10 Tasks 1–4 have published `TemplateFragment`, `TemplateDefinition`,
> `TemplateApplicability`, `BranchTemplateBinding`, and C1–C8 validation.

P10 Tasks 1–4 produce `vocabulary.py`, `records.py`/`schema.py`, `config.py` and `upstream.py` —
groundwork, none of the template seam. The four dataclasses are defined inside **Task 6** ("Four
template records and the packaged catalogue"); C1–C8 validation is **Task 7** ("Route many-to-many
and gate the composition C1–C8"), whose Done-means is *"DM13 (C1–C8 independently falsifiable)"*.
Task 1 publishes only the *names* `COMPOSITION_GATES = ("C1"…"C8")` — a vocabulary tuple, not
validation. P10's own requirement-coverage map assigns "the four records, many-to-many routing,
C1–C8, the Site E fragment boundary" to tasks **6, 7, 8**.

**Consequence:** an executor following the gate literally starts `tools/compile_tree_templates.py`
after P10 Task 4, against record types and a `TemplateCatalogue` that do not exist.

**Correct text:** *"G-P10: P10 Tasks 6–8 have published `TemplateFragment`, `TemplateDefinition`,
`TemplateApplicability`, `BranchTemplateBinding`, `load_catalogue`, C1–C8 validation, and the Site-E
`template_schema_validator`."* Task 8 belongs in the gate because library Task 7 cannot be written
until P10 owns the schema validator. The likely cause is that the gate was written against an earlier
P10 plan; note the stale reference is in the **newer** document (library 2026-08-26, P10 2026-08-25).

### 7.4 The other template-chain findings

| # | Finding | Sev |
|---|---|---|
| 1 | **The compiled manifest has a producer, a consumer, and no courier.** The library plan creates `src/tree_design/catalogue_data/manifest.json` — inside P10's own package — and `grep -n "catalogue_data"` over P10's plan returns **zero hits**. Both plans agree the reader is *injected*; neither names the caller that opens the file. P10's package is structurally barred from doing so: Task 16's `test_no_module_touches_the_filesystem` forbids `pathlib`, `glob`, `open` across every module. The manifest *shape* is specified only on P10's side (four top-level keys), while the library plan names none — and its "source hashes" and "validation-report hashes" have no reader | HIGH |
| 2 | `TemplateFragment.allowed_values` contradicts the scaffolding spec (*"It contains no user values"*), the library plan (*"store no user values or field mappings"*), the library plan's own list of failing fixtures (*"domain labels inside canonical roles"*) — and the dataclass docstring one line above the field (*"No values, no field mappings, no nodes"*). It is populated in tests with `{"artifact_kind": ["Homework", "Exam"]}`, which is exactly a domain label inside a canonical role. It is load-bearing (`merge_fragment_constraints` intersects it), so it cannot simply be deleted — it should move to `TemplateApplicability`, where domain labels legitimately live | MEDIUM |
| 3 | `purpose_profile_ref` distinctness is enforced at the **type** level and only asserted at the **value** level. `PurposeProfileRef(purpose_profile_id="g_columbia_app", ...)` — a real P9 group id inside the right wrapper — is accepted. The `pp.` convention appears only in fixtures | MEDIUM |
| 4 | The Site-E template payload check is a **denylist**, not a closed key set: it asserts the seven required keys are present and never rejects extras. `{"proposed_fragment": …}` or `{"shared_recipe": …}` passes the schema gate and then passes Site E's other three checks, which inspect only `dimensions`, `citations` and `levels`. Every other closed set in P10 goes through `check(value, closed, name=…)`; this one spot inverts the pattern | MEDIUM |
| 5 | `TemplateCatalogue.rows_for_schema` is called from Tasks 7 and 8 but is missing from Task 6's published *Interfaces* block, so it reads as private to a downstream plan | LOW |

**Two positive results worth recording.** The publication boundary is properly enforced on P10's
side, at two independent layers, with the guard in Task 6 rather than only Task 16 — verified by
reading both tests. And the Site-E fragment hole is real, verified independently
(`grep -rni "fragment" src/` returns **one** hit, in `src/facts/session.py:34`, about filesystem
paths; zero in `src/llm_harness/`), correctly deferred rather than a P8 bug, and closed by P10 Task 8
in the right package with the right two mechanisms. Recorded so it is not re-reported as a P8 defect.

---

## 8. What to fix, in order

Two separate lists. **Joseph has not authorized any live-code change** — the tree is byte-identical
to `b7c6e8f` and every auditor left it that way deliberately. List A needs that authorization. List B
is plan edits, which change no shipped behaviour.

### List A — live code (needs authorization)

| # | Sev | Part | Fix | Unblocks |
|---|---|---|---|---|
| **A1** | BLOCKER | P3 | Prune protected subtrees in `SessionWatch.open()` and `poll()` (mutate `os.walk`'s `dirnames` in place) and return early from `notify()` when `is_protected_container(path)`. Add the watch mirror of `tests/p3/test_p3_protected_container.py:42` | The standing user constraint. Every event written before this is permanent |
| **A2** | BLOCKER | P7 → then P8 | Decide in the SPEC what `context_before`/`context_after` are on a `Released` (§9 OPEN-1), then bound or redact or remove them, extend `is_whole_document` to measure the whole payload, and add the test S9 proves absent | Every model call on a consented protected file |
| **A3** | BLOCKER | P8 | `return min(verdicts, key=lambda v: OUTCOME_SEVERITY.index(v.outcome))` at `harness.py:348`; extend the shard test with a multi-claim case | §8.5's grounding measurement; every P9 membership derived from a multi-claim response |
| **A4** | BLOCKER | P5 | Make the sensitivity signal survive the collapse — collapse before indexing, or key it on `(zone, raw_value)` and resolve against the written rows. Add the `max(index) < len(observations)` assertion in `LongTailResult.__post_init__` | Stops the scan crashing on an ordinary `.eml`; stops P7 gating the wrong row |
| **A5** | BLOCKER | P6 | Make the survivor set load-bearing: widen `Stage` to carry it, or move the filter into `observations_for_version` behind an injected screen. Add a test that drives `FactResolver.resolve` with a real rule stage and asserts zero facts | Done-means 22; stops `subject = "python-docx"` |
| **A6** | BLOCKER | P9 | Separate the two concepts `Neighbor.detail` carries: an explicit `bridge_entity` that is `None` unless the channel runs through a named entity, counted **corpus-wide**. Until that exists, `anchoring_files` must not drop `shared-validated-fact` edges on hub suppression — the basis value is never the hub | Grouping stops getting worse as evidence increases |
| **A7** | BLOCKER | P9 | Give `group_subject` the five P8 dependencies (or an explicitly typed adapter plus a production factory), and pass `knowledge.conflicts_for(...)` through to both `assemble_group_dossier` and `build_dossier_request`. Add one integration test driving `group_subject` with the real `run_call`, and extend `tests/integration/test_p9_p8_group_seam.py:52-54` — which already reads the live signature — to assert P9's call site supplies `gate` and `model_client` | The whole model path; and Site B's `target_institution` check, which cannot fire today |
| **A8** | HIGH | P1 | `if actual is None or expected_hash is None: return "mismatch"` in `verify_content`, with a test pinning both arms | Stops an unverified hash authorising a move |
| **A9** | HIGH | P2 + P8 | Have `emit_stage_output` pass `DimensionValue(dimension="llm_grounding", …)`; add `REFERENCES bundle_manifest` to `run_manifest.bundle_id`; extend both P2 integration files to call `assert_run` and assert the verdict is not `not_run` | §8.5's most consequential dimension becomes measurable; the join P2 exists to make gets exercised |
| **A10** | HIGH | P5 | Set `VISION_CONFIG["languages"]` to the ratified list and add `tests/readers/test_deployment.py` asserting all three settings against the ratification | CJK scans stop producing noise stamped `complete` |
| **A11** | HIGH | P5 | Add `"context_window": context_window` to the `config` mapping of all six extractors plus `filesystem`, and read the value from P1's `evidence.context_window` ceiling in `production.py` | §3.4's cache and §8.5's replay stop serving stale answers silently (P4 ratification B4) |
| **A12** | HIGH | P8 | Site A: replace the literal `ACCEPT_DIRECT` with `validation._acceptance_outcome(...)`; either implement the §3.3 search-hint check or remove `SEARCH_HINT_ONLY` from the registry and record the deferral; replace both hand-built tests with ones that run the builder | Site A can reach its five outcomes; §3.6's Possible lane exists |
| **A13** | HIGH | P8 | Make `_same_file_evidence` return `ValidationUnavailable(missing=("evidence_file_identity",))` until `EvidenceItem` carries a file id, and fix the Site D fixture's `location` default in the same change | Site D stops silently passing or wrongly rejecting depending on the builder |
| **A14** | HIGH | P6 | Add `active = 1 AND superseded_by IS NULL` to `proposal_eligible`, exactly as `values_with_counts` already does. One line + one test | P10 and P11 stop being handed competing values with no signal |
| **A15** | HIGH | P4 | Rewrite `CONFORMANCE_RULES[9]` and the comment at `conformance.py:249-250` to the ratified reading; add a test asserting the published text names every member of `ZERO_OBSERVATION_COMPLETENESS` | Six extractor authors stop reading a contract the gate does not enforce |
| **A16** | HIGH | P3 | Fix the replay cache-verdict divergence (key `prior_observation` on `observed_path` for the replay harness, carrying the snapshot's path→hash map), or amend Done-means 14 to say the divergence is accepted. Add a replay test over a **second** scan | Done-means 14 becomes a promise the code keeps |
| **A17** | HIGH | seams | Add `tests/p3/__init__.py`, `tests/p5/__init__.py`, `tests/integration/__init__.py`, `tests/readers/__init__.py`, `tests/wave2/__init__.py`; repoint p5's 22 bare-`conftest` imports | The suite becomes order-independent; CI can shard |
| **A18** | HIGH | seams | **One end-to-end test with no doubles**: `run_p1_p7` over the real-PDF corpus already in `tests/readers/`, then `group_subject` over the fact it produced, then `replay_bundle` on its bundle. Every component exists and is green; only the composition is missing | This is the single highest-leverage item on the list. It would have caught A1, A2, A3 and A7 |
| **A19** | HIGH | repo-wide | **Make the binding check standing.** The four scans that found Blocker 3b were written for this audit and thrown away. Land one as a test: AST-walk `src/`, resolve every cross-part call and every `Callable`-annotated seam, and `inspect.signature(callee).bind(...)` it against the live signature — failing on any mismatch and on any `Callable[..., X]` seam whose production counterpart exists and does not bind. It is cheap, it is deterministic, and it is the only mechanism proposed here that would have caught 3b **without** the end-to-end test | Catches this class permanently, including the three pending seams in §9 the day a real callable is written for them |
| A20–A27 | MEDIUM | various | The silent guards, in one pass: P1's Done-means 3 and 7 tests; P2's structural no-aggregate check; P5's layering guard (absolute path, and move it out from behind `importorskip`) and a behavioural pre-P6 OCR test; P9's `ast.Attribute`/alias handling, the `nodes` ban, and a spy on `assemble_group_dossier`; P8's consent test renamed to what it checks | Stops the next round of defects hiding the same way |

### List B — plan edits (no shipped behaviour changes)

| # | Sev | Plan | Fix |
|---|---|---|---|
| **B1** | BLOCKER | P10 | Add a task between the current 11 and 13 that (a) materialises an approved `VerticalOption` into `Node` rows with `expected_values` drawn through the P6 read surface, and (b) gives every `TREE_EDIT_ACTIONS` member a writer in `apply_review_action`. Without this P10 cannot propose a tree |
| **B2** | BLOCKER | P10 ↔ P11 | **Reconcile the seam before either is built.** Pick one owner for the frozen-tree read and one shape for `DestinationProfile`, `Node` and the legality projection; pick one spelling of `plan_version`; point P11 at `tree_design.fixtures`. Every hour spent building either part before this is decided is rework |
| **B3** | BLOCKER | P10 | Fix the four self-failing items: `vocabulary.py`'s two guard tests, `origin_node_id=""`, `delete-suggested-area`'s absence from `TREE_EDIT_ACTIONS`, and `AnchorFact`'s field names in both the fixture and `upstream.py` |
| **B4** | BLOCKER | P11 | Fix the five self-failing items: the threshold/weight inconsistency, the supersede-before-insert ordering, the 30-vs-14 column assertion, the immutability trigger's guard list, and `from grouping.vocabulary import VALIDATED` |
| **B5** | BLOCKER | P11 | `sed`-repoint 26 imports from `tests.p11.` to `p11.` |
| **B6** | BLOCKER | P11 | Implement `run_corpus`: call `p8_seam.call_placement` when `needs_model_call` and the gate permits; transcribe the verdict; call `record_cd_verdict`; run group placement; run the residual stage; run the §7.9 re-entry |
| **B7** | HIGH | templates | Rewrite G-P10 to name Tasks 6–8 (§7.3) |
| **B8** | HIGH | templates | Name the component that opens `catalogue_data/manifest.json` and injects it, say which layer owns the directory, and reproduce P10's four manifest keys verbatim in the library plan |
| **B9** | HIGH | P10 | Renumber `## Required execution order` and the six ledger rows; "Task 17 last", not "Task 15 last". Rewrite the stale P9 row to say what is actually missing (only the listing read) |
| **B10** | HIGH | P11 | One function mints `basis_key`, and P13's `subject_ref` is resolved to a file/group subject before it is used as a key |
| **B11** | HIGH | P11 | Replace the `automatic_move_permitted` derivation with `privacy.moves.may_move_automatically`; take `redacted` and `consent_audit_ref` from P7's consent grants; add a corrections row saying **P7 owes a `model_eligibility` producer** |
| **B12** | HIGH | P11 | Assert the residual partition covers every unplaced file, and raise otherwise |
| **B13** | HIGH | both | Decide where `node-hub` is guarded. The cheapest correct fix is deleting `or destination == "node-hub"` from `src/llm_harness/placement_validation.py:239` — a P8 file, one line, one test, and `payload.get("generic_hub") is True` already covers the real case. **P10's owner has not been told this exists** |
| **B14** | MEDIUM | research | Regenerate §0a, §0b and the owed-by-family lines from disk rather than by hand — the numbers have now been wrong at three consecutive checkpoints — and carry all 37 refusals into R1c's scope |
| **B15** | MEDIUM | templates | Move `TemplateFragment.allowed_values` onto `TemplateApplicability`; make the Site-E payload check a closed key set |

---

## 9. What the audit could NOT determine

Stated plainly, because a false "verified" is worse than an honest gap.

**Decisions nobody has made — these need a ruling, not an implementation.**

- **OPEN-1 — What are `context_before` / `context_after` on a `Released`?** The word "context" occurs
  zero times in P7's 630-line SPEC. §8.4's compact dossier names five releasable item kinds and
  context is not one of them. Until this is decided, B2's fix cannot be specified. *Decides: Joseph,
  or P7's owner with Joseph's ratification, because it changes what leaves the device.* Related and
  also unowned: `planning/33-P8-COMPLETION-AUDIT.md:100` attributes the redaction reverse-mapping
  question to "P7 SPEC open question 4", which is actually *"Deletion versus append-only"*. The
  question is genuinely unrecorded.
- **OPEN-2 — `target_school` vs `target_university`.** Both live, both `destination_eligible`. The
  code names the violation openly and asks. Either key survives; a migration note is needed for
  stored `college_applications` facts. *Decides: Joseph (D8).*
- **OPEN-3 — Is §8.2's 14-name tree-edit list closed?** If it is, map `delete-suggested-area` → `delete`
  at the writer and say so. If it is not, add the four §8.7 actions and record the SPEC extension.
  *Decides: P10's owner.*
- **OPEN-4 — `plan_version` or `plan_version_id`?** Both are live in `src/` (P8 uses one, P9 the
  other). *Decides: whoever owns `planning/02-segmentation-map.md`.*
- **OPEN-5 — Which side owns the frozen-tree read, and what shape is `DestinationProfile`?**
  See B2 above. *Decides: P10's and P11's owners together, before either builds.*
- **OPEN-6 — Does C4 permit a purpose composition to resolve one role per contributing schema?**
  P10's DM15 fixture — the one test that exists to prove *"the template is a recommendation
  mechanism, not a rule that erases purposeful heterogeneity"* — currently trips C4 with
  `counterpart -> ['subject', 'target_school']`. Either the fixture is wrong or C4 is. *This is a
  design ruling, not an implementation choice.*
- **OPEN-7 — Is P7's transport guard right about `ModelClient`, or is `ModelClient` wrong?** The
  instrument fails the shipped transport on `invoke` accepting `bytes`. That may be a false positive
  — the bytes are only constructible from a live `Released` — but the argument has never been made.
  *Decides: P7's and P8's owners.*

**Marked UNVERIFIED by their auditors.**

- Whether `validate_placement_response` / `validate_residual_response` return a shape such that
  `result[0][0]` is a `P8Verdict`. The P11 plan uses both `[0][0]` and `result[0][0]`; `dispatch`
  was confirmed to return a 2-tuple whose first element is a sequence, but the validators were not run.
- Whether `tests/p11/conftest.py`'s `conn` fixture exists in a parent conftest — the plan assumes it.
- Whether `facts.read_surface.is_destination_eligible` raises or returns `False` for an uncatalogued
  field. The P11 plan says either reading is acceptable, which is itself a softness worth tightening.
- Whether P10 Task 8's integration test's citation path accepts `obs-1` against the fixture dossier's
  released evidence. It needs the code to exist to test.
- P10's SPEC field list (21 node fields) was taken on trust by the P11 auditor; P10's SPEC was not
  read in that pass. It was independently confirmed in the P10 audit.

**Three injected seams are not yet checkable — the same class of risk as Blocker 3b, pending.**
The binding scan can only compare a declared arity to a real callable when a real callable exists.
Four seams in `src/` declare `Callable[..., X]` and have a variadic test double; one
(`p8_run_call`) has a published production counterpart and is broken. The other three have nothing
to differ *from* yet:

| Seam | `src/` invokes it as | Why not checkable | When it becomes checkable |
|---|---|---|---|
| `margin_predicate` | 2 positional | P11 is not built | The first time P11 supplies a real predicate |
| `sensitivity_policy` | 2 positional | P11 is not built | Same |
| `contradicts` (`llm_harness/validation.py:413`, the `oracle`) | 2 positional | Caller-injected **by design**; `harness.py:84`'s `_CALLABLES` enforces callability and an absent one becomes `ValidationUnavailable(missing=("contradicts",))` | Whenever a production caller supplies one — which may be never, and that is legitimate |

These are **not defects today**. They are named here so that the day a real callable is written for
any of them, someone binds it rather than assuming it fits — because that assumption is exactly what
let Blocker 3b survive a full audit round.

**Blocked by P10/P11 not existing.** Nothing about the actual runtime behaviour of tree design,
freeze, placement, residual handling, or the template compiler can be verified. Everything in §6 and
§7 is a judgement about documents. `run_call`'s Site C and Site D paths have never been exercised by
a real caller, only by fixtures. P2's `template_generation`, `tree_design`, `candidate_node_retrieval`
and `placement_scoring` stages, and its `template` / `tree` / `placement` / `residual` dimensions,
have no producer and legitimately report `not_implemented`.

**Where two auditors disagreed, and how it was resolved.**

- **The P8→P9 seam — the disagreement that mattered most.** The seams auditor originally passed it
  (*"Every adjacent pair P1→…→P9 has a live connector"*); the P9 auditor called it a BLOCKER. **The
  P9 auditor is right**, and the seams auditor withdrew the claim after running a binding test
  rather than a reachability test, then wrote up the methodological error itself (§1). Both halves
  of the resolution matter: the seam genuinely does not work, **and** the overall picture is better
  than the seams auditor's retraction alone would suggest — 306 of 306 direct call sites and 48 of
  48 typed seams bind cleanly, so this is one broken seam in a codebase whose interfaces otherwise
  line up, not the tip of a drift problem.
- **P1's `base_event_type`.** The P1 auditor called it *"structurally dead"* and its Done-means-11
  test vacuous. The seams auditor read the same registry and called the absence *"the expected shape,
  not the defect shape"*, quoting P1's own comment declining to coin P11's names. **The seams
  auditor is right about the mechanism and the P1 auditor is right about the test.** Verified: the
  registry holds 35 types, zero carry a base, the comment says the eight will be added when P11
  prints them, and the test loops over `[]`. Stated in the corrected form in §5.
- **`llm_grounding_report`.** P8's report treats it as P8's grounding surface; P2's report shows it is
  an unrelated table and that P2's `llm_grounding` *dimension* has no writer. **CONFIRMED BY LEAD** —
  they are two different things sharing a stem, and the P2 reading is correct.
- **Basename collision count in `src/`.** The lead counted 17 colliding basenames across ten
  packages; the seams auditor counted 16. Not resolved and not worth resolving — both agree it is a
  traceback-readability cost and not a correctness one, because every `src/` import is
  package-qualified with zero relative imports and zero `sys.path` manipulation.
- **P5's `.tar` support.** The auditor flagged `.tar`/`.gz` as LOW because the PLAN names stdlib
  `tarfile`; the routing table's own comment treats the absence as deliberate. Recorded as LOW with
  the tension noted rather than adjudicated.

**Not audited at all.** P12 (apply, undo, move execution) and P13 (review surface). Neither is built,
neither has a plan, and ten registered event types are waiting for them. Nothing in this document
says anything about whether they are feasible as specified.

---

## 10. Provenance

Every claim above carries a `file:line`, and every quotation was produced by a command run against
the working tree while writing this document — not restated from the source reports. Where a source
report's line number had drifted (notably the P10 and P11 plan citations, which two sessions are
editing concurrently), the number given here is the one re-verified today.

Final tree state:

```
$ git rev-parse --short HEAD
9bc36e6
$ git status --short src/ tests/
$ git diff --stat b7c6e8f HEAD -- src/ tests/
```

Both commands print nothing. `src/` and `tests/` are byte-identical to the pre-audit tree at
`b7c6e8f`, across 111 sabotages by fifteen concurrent sessions. No commit, stash, checkout or history
rewrite was performed by any auditor.
