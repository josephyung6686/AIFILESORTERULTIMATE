# Assembly rulings and the fix backlog

Date: 2026-08-22
For: whoever assembles `P6-facts-facets/PLAN.md` and `P7-privacy-consent-gate/PLAN.md`.
Companion to `_PLAN-AUTHORING-BRIEF.md` (read that first; §23 carries D7–D10).

This file settles **which copy of each duplicated task wins**, and carries the defect backlog the
rulings turned up. Every entry is cited `file:line`. Nothing here is a guess: each ruling was made by
reading both versions side by side, and the load-bearing ones were confirmed by execution.

---

## 1. THE WINNER TABLE — one file per task, no exceptions

Assembly takes each task's section from exactly the file named here. **The winners are split across
files**, which is why this had to be ruled per task rather than per file.

### P6 — `P6-facts-facets/`

| Tasks | File | Note |
|---|---|---|
| 1, 2 | `PLAN-tasks-01-02.md` | sole copy |
| 3, 4 | `PLAN-tasks-03-04.md` | sole copy |
| 5, 6 | `PLAN-tasks-05-06.md` | sole copy |
| **7** | `PLAN-tasks-07-09.md` | **sole copy of Task 7** — this file loses 8 and 9 but keeps 7 |
| **8** | **`PLAN-tasks-08-09.md`** | **HIGH** — see §2.1 |
| **9** | **`PLAN-tasks-08-09.md`** | **HIGH**, raised by D9 — see §2.2 |
| 10–13 | `PLAN-tasks-10-13.md` | sole copy |
| 14, 15 | `PLAN-tasks-14-15.md` | sole copy |
| 16–19 | `PLAN-tasks-16-19.md` | sole copy |
| 20, 21 | `PLAN-tasks-20-21.md` | sole copy |
| 22, 23 | `PLAN-tasks-22-23.md` | sole copy |
| 24, 25 | `PLAN-tasks-24-25.md` | sole copy |
| 27 | `PLAN-task-27.md` | sole copy (Task 26 is CUT — D5) |

### P7 — `P7-privacy-consent-gate/`

| Tasks | File | Note |
|---|---|---|
| 1–3 | `PLAN-tasks-01-03.md` | sole copy |
| 4, 5, 6 | `PLAN-tasks-04-07.md` | this file loses Task 7 |
| **7** | **`PLAN-tasks-07.md`** | brief §20 — `MetadataField(name)`, `Filename(file_id)`, `span: TextSpan \| None` |
| 8, 9, 10 | `PLAN-tasks-08-11.md` | this file loses Task 11 |
| **11** | **`PLAN-tasks-11.md`** | brief §19/§22 — the other copy has the **gate bypass** |
| 12, 13, 14 | `PLAN-tasks-12-14.md` | sole copy |
| **15** | **`PLAN-tasks-15-22.md`** | HIGH — see §2.3 |
| **16** | **`PLAN-tasks-15-22.md`** | HIGH — see §2.4 |
| **17** | **`PLAN-tasks-17-19.md`** | medium-high — see §2.5 |
| **18** | **`PLAN-tasks-15-22.md`** | see §2.6 |
| **19** | **`PLAN-tasks-17-19.md`** | see §2.6 |
| **20** | **`PLAN-tasks-20-22.md`** | HIGH, **with four grafts from `15-22`** — see §2.7 |
| **21** | **`PLAN-tasks-20-22.md`** | **medium — D7/D10 nearly flipped it.** See §2.8. |
| **22** | **`PLAN-tasks-20-22.md`** | medium-high — see §2.9 |

**`PLAN-tasks-15-16.md` is discarded entirely.** It contributes nothing `15-22` lacks.
`PLAN-tasks-15-22.md` wins Tasks 15, 16 and 18; `PLAN-tasks-17-19.md` wins 17 and 19;
`PLAN-tasks-20-22.md` wins 20, 21 and 22 — which also keeps the fixture numbering consistent across
20 and 22.

**Assembly hygiene, and it is not optional.** `PLAN-tasks-07-09.md` keeps Task 7 but loses 8 and 9,
and it carries a **file preamble (lines 1–128) and two appendices (lines 2179–2265) that cover 7, 8
AND 9**. Its preamble's index-addressing convention (`:44-50`) and appendix items 1, 4, 5 and 6 are
Task 8/9 material. Copied wholesale they arrive attached to Task 7 and **contradict the winning
Task 8/9's own ambiguities section** (`08-09:1626-1664`). They must be **split**, not copied.

---

## 2. WHY, PER RULING

### 2.1 P6 Task 8 → `PLAN-tasks-08-09.md` (HIGH)

**The loser does not pass its own tests.** `07-09:1186`'s guard puts `"content_hash"` in its
forbidden set while `07-09:1342` writes `identity["content_hash"]`; running A's own `_code_strings`
AST helper over A's own implementation returns `{'content_hash', 'normalization_failed'}`, so Step 4's
claim *"PASS — 16 passed"* is false.

**Worse, and this is the deciding one:** A's test helper `_observe` (`07-09:858`) has **no
`reliability` parameter** — every observation it builds is `direct`. An implementation that wrongly
gated on `Observation.reliability` would pass **all sixteen** of A's tests while making one of §3.5's
four named slots unreachable. B tests exactly that at `08-09:371` against P4 fixture 12
(`raw_value='2025'`, `reliability='possible'`, locator `table:sheet=2/row=7/column=3`), verified live.

Other A defects: `07-09:914` — `WORK_TYPE`, the document-title slot fixture, is used by **no test**
(dead path); `07-09:1342` — the content-hash branch is unreachable in production by A's own admission
(`07-09:2251`); `07-09:1274/1278/1281` — `STATES[1]` / `FACT_ORIGINS[0]` index form, which brief §11
names and overrules, and A's appendix at `07-09:2214` then **recommends** it.

### 2.2 P6 Task 9 → `PLAN-tasks-08-09.md` (HIGH, raised by D9)

**D9 turns a loser test red.** `07-09:1770-1771` loops all four §3.8 role fields and asserts
`not destination_eligible`. Under D9 that is **wrong for `target_school` and `client`**. A's prose
repeats the now-wrong rule at `07-09:1466` and `07-09:1944`. B's equivalent (`08-09:1157-1163`) loops
only `AUTHORSHIP_FIELDS == ("authored_by",)` and still passes — and B's prose at `08-09:873-876` had
already given **D9's exact argument** as its reason: *"target_school and client are targets, not
authorship."* B reasoned to the ruling before the ruling existed.

Two defects decided it independently of D9:

1. **A moves catalogue 01's matching grammar into `src/facts/`.** A's `discount.py` holds
   `'case_sensitive'`, `'exact'`, `'match_kind'`, `'pattern'`, `'prefix'`, `'regex'`,
   `'tail_required'`, plus `import re` and `re.search(entry["pattern"], …)`, and module-level
   frozensets `_BOUNDARY` / `_ASCII_DIGITS` (`07-09:2001-2002`). That is **brief §18 inverted** — §18
   records that Task 9 *"correctly takes compiled predicates so `facts` holds no regex catalogue"*,
   which describes **B**. It also freezes catalogue v1.0's `boundary_rule` into P6 where a v2.0 could
   not change it.
2. **A writes one `unresolved` row per suppressed observation** (`07-09:2070`, inside the
   per-observation loop) against `SPEC.md:738`'s *"one `unresolved` row"*. A's own test
   (`07-09:1655`) uses a single observation, so it **passes immediately and proves nothing**. B writes
   one row per version citing every suppressed observation (`08-09:1532-1543`) and tests the two-slot
   DOCX case (`08-09:1304`).

### 2.3 P7 Task 15 → `PLAN-tasks-15-22.md` (HIGH, narrow margin)

The two texts are ~97% identical and every structural judgement is shared and correct in both.
`delete_derived` is **not** a dead path: it refuses on both sides of D3's enumeration
(`15-22:653-682`). A wins on three concrete deltas: it keeps
`assert payload["effective_from"] == LATER` (`15-22:301`) where B drops it **while both
implementations still write that key** — B ships a logged value with no reader; B carries three dead
imports in its test file (`15-16:183-184`); and B annotates its `released` fixture `-> str`
(`15-16:263`) over an `-> int` producer, casting back with `int(released)` at three sites.

**Nothing to graft from the loser.** Every B-only line is reflow, a dead import, or a dropped
assertion.

### 2.4 P7 Task 16 → `PLAN-tasks-15-22.md` (HIGH)

§8.7 **query-before-classify is honoured in both** — this is *not* the Task 11 bypass shape. `assign`
(`15-22:1292`) validates, then `if suppressed(...): return None`, and only then `store.write(record)`.
The filters inside `suppressed` sit on the **records returned**, which is *"filter only where the
filter is what the check needs"*.

A wins on the Interfaces contract, which is what assembly joins on. **B states the ratified rename
wrong**: `15-16:767` attaches *"the skeleton's `facts_seam.SensitivityFacts` — see the rename note"*
to `ClassificationRecord`, but the rename is `SensitivityFacts → classification_store.ClassificationStore`
— **a record where a store belongs**, in the exact vocabulary D2 exists to pin. A attaches the same
parenthetical to `.mirror_state`, correctly. B's `Consumes` also omits
`database_agent.learning.reset_preferences`, which B's own test imports (`:844`) and calls (`:997`).

### 2.5 P7 Task 17 → `PLAN-tasks-17-19.md` (medium-high)

**Both predicates are safe on the move gate** — absence first, then `protected`, then policy. Neither
has the brief-§19 filter-before-check shape, and neither can return `allowed=True` for a protected
record without explicit permission.

B wins on vocabulary and signature fidelity. B's four reasons are snake_case identifiers closed by
`MOVE_REASONS` (`17-19:117-121`) with `UNREADABLE_UNCLASSIFIED` **bound** to `resolve_class(None)`
rather than retyped. A's four reasons are **English prose sentences** (`15-22:1774-1785`) tested by
substring scan (`assert "explicitly permits" in REASON_NO_PERMITTING_POLICY`, `:1704`) — defect class
8 — creating a second home for Task 3's `unreadable_unclassified` and putting UX copy into a value
P11/P12 will store verbatim. A also injects `store: ClassificationStore` (`:1425`), **the injection
D2 and brief §10 removed**; B constructs `ClassificationStore(conn)` inline.

### 2.6 P7 Task 18 → `PLAN-tasks-15-22.md`; Task 19 → `PLAN-tasks-17-19.md`

Detail pending in the ruling's part 2. D10 is a **no-op** for 17–19: neither version touches a span,
region, `norm` unit or origin — grepped, zero hits. `field_id`: zero occurrences in either file.

### 2.7 P7 Task 20 → `PLAN-tasks-20-22.md` (HIGH) — **with two grafts**

Both publish sixteen fixtures; both are broken against the ruled `PLAN-tasks-11.md`, but not
comparably.

**B's fixtures are content-addressed against P4's live nineteen** — `_key(3)`, `_hash(3)`,
`_unit_length(3)`, `TextSpan(12043, 12051)` (`20-22:1067`) — and B's `seed()` (`:270-296`) writes the
run, text units and observations, so a replay addresses evidence **that exists**.

**A invents its keys** — `OBSERVATION_KEY` / `SENSITIVE_KEY` are hand-typed sha256 literals
(`15-22:3241-3245`) — and its `materialise()` (`:2937-2963`) seeds **no P4 run, text unit or
observation at all**, so fixtures 5, 9, 10 and 15 cannot resolve a span and **Done-means 11's entire
substance is unbuildable**. A also **does not import**: `_GPS = MetadataField(name="gps")` at module
scope raises `AlwaysLocalRequested` in `__post_init__` (`PLAN-tasks-07.md:832-846`) — all 68 tests
error at collection. Three more import-time `TypeError`s at `:3250`, `:3256-3259`.

**Graft from A (four things):**
1. `GATE_ARGUMENTS` / `gate_arguments()` (`15-22:3223-3228`, `:3319-3339`) — the constructor
   `PLAN-tasks-11.md:124` adopted verbatim. **Widen to twelve keywords**; A pins ten and
   `PLAN-tasks-11.md:1440-1447` has twelve.
2. **Fixtures 14 and 15 as Open question 5's two branches** (`15-22:3660-3690`) — the only place in
   either version where OQ5 is held open **as data**, and Task 21's OQ5 guard depends on the
   parameter existing with no default. FIXTURES becomes **eighteen**.
3. `p8_obligation` / `classification` as defaulted additions (`:2860-2866`).
4. **The 22-row "Where the skeleton was ambiguous or self-contradictory" table** (`:4959-5001`) and
   **"What remains for Joseph"** (`:5003-5022`) — the best reconciliation artifact in either file.
   Take both **whole into the assembled preamble**.

The Gate keyword is **`scope_for`**, not A's invented `area_of`.

---

## 3. CORPUS-WIDE DEFECTS — fix once, across whichever files win

### 3.1 `set_policy` is called with a parameter it does not have — **18 sites**

Published (`PLAN-tasks-04-07.md:1052`, impl `:1761`):

```python
set_policy(conn, policy, *, component_version: str, user_id: str, reason: str) -> str
```

There is **no `author`** — A14 dropped it, and the implementation says why: *"M8 makes the acting part
the author, and a log where the author is a caller-supplied value cannot [be trusted]"*. And `reason`
is **required**. Eighteen call sites pass `author=` and omit `reason`; every one is a `TypeError`.

Sites: `08-11:2381` · `12-14:2174` · `20-22:310, 2480, 2501, 2518, 2596, 2614, 2631, 2652, 2711` ·
`15-22:1532, 1962, 2951, 4799, 4840` (+2). The canonical form is Task 5's own helper
(`04-07:1179-1181`):

```python
set_policy(conn, a_policy(**over), component_version=COMPONENT,
           user_id="joseph", reason="the user chose local-model mode")
```

**This is the join defect the `Interfaces:` check cannot see** — the *name* `set_policy` resolves
fine; it is the *signature* that does not. Worth remembering as its own defect class:
**a producer with a consumer that calls it wrong.**

### 3.2 `a_policy(policy_version=…)` makes every calling test fail

`17-19:233` feeds `a_policy(policy_version="policy-1")` to `set_policy` via `stored()`. Task 5's A8
(`04-07:111`) makes `set_policy` **raise `CallerSuppliedPolicyVersion`** for any `policy_version !=
UNSET_POLICY_VERSION` — its own negative test is that exact call (`04-07:1219`). Every test calling
`stored()` fails. Fix: `policy_version=UNSET_POLICY_VERSION`, as `15-22:1523` and `04-07:1172` have it.

### 3.3 Six tasks omit `Modify: src/privacy/gate.py` — so six `Gate` methods have no producer

`PLAN-tasks-11.md:368` names it: *"The other six Gate methods — `revoke`, `reclassify`,
`delete_derived`, `may_move_automatically`, `display_policy`, `summarize_protected` … Each of those
tasks needs a `Modify: src/privacy/gate.py` line that its `Files` block currently omits."*
Confirmed absent in Tasks 15 (`15-22:88-90`), 16 (`:760-762`), 17 and 18. **Consumer with no
producer**, on the part's own facade.

### 3.4 Brief §11's named constants reach **neither** version of anything

Measured across both P6 Task 8/9 copies: `STATES[n]` indices and bare state literals in both, **zero**
named-constant uses. This is an assembly job on every winner, not a discriminator. Sites include
`08-09:673, 677, 740, 1538` and `07-09:1274, 1278, 1281, 2005`. Same rule for P7: `15-22:1356-1357`
builds `ClassificationRecord(basis="user", reliability_state="user_confirmed")` as bare literals.
**Task 2 owes `USER` and `USER_CONFIRMED`** — P7 Task 2 publishes `CLASSIFICATION_BASES`
(`01-03:1239`) but no per-value constant, and **no reliability-state vocabulary at all**. The literal
also recurs at `01-03:1591` and `04-07:387, 405, 414, 478, 488`.

### 3.5 Private aliases do not escape Task 25's guard

`08-09:641-652` binds imports to `_FACT_ORIGINS` / `_VALUE_ORIGINS`. Task 25's
`test_every_module_level_collection_is_a_declared_closed_vocabulary` (`24-25:1075-1087`) checks the
**binding name** against `DECLARED_VOCABULARIES` (`24-25:878-898`), and `module_constants` skips only
`__dunder__` names (`24-25:948`) — a leading underscore does **not** exempt. **The winner fails a
sibling's guard on two bindings.** Same class: `DISCOUNT_OUTCOMES` and `AUTHORSHIP_FIELDS`
(`08-09:1447, 1457`) are absent from `DECLARED_VOCABULARIES` in **both** versions. `AUTHORSHIP_FIELDS`
is the skeleton's own name, so that is a **Task 25 omission**, not a Task 9 invention.

Also stale there: `24-25:886` declares `SLOT_KINDS` as *"Task 8 §3.5's slot kinds"* — that is the
**losing** Task 8's name. The winner publishes no `SLOT_KINDS`. Drop the line or have Task 8 publish it.

### 3.6 The §3.4 cache-key rule is now copied **eight** times

Brief §18 said seven. `08-09:751-773` and `08-09:1571-1590` are the seventh and eighth. One helper in
`facts.cache` — Task 6's module, which already publishes `fact_cache_key` (`05-06:690`) — deletes all
eight. **No other task may add to `facts.cache`** (brief §15), so this is Task 6's line to widen.

### 3.7 `current_policy` returns `Policy | None` and consumers do not check

A6 (`04-07:1053`, impl `:1781`): *"None is a fact, not a gap."* `17-19:672` calls
`policy.automatic_move_permissions.get(...)` with no `None` check → `AttributeError` on the
unconfigured path. Worse: Task 6 publishes `effective_policy(conn, *, plan_version, install_mode,
set_at)` (A16, `04-07:1908`) as *"the function the gate calls"* — and **both versions bypass it**.
A published function with no caller.

---

## 4. FINDINGS THAT ARE NOT MECHANICAL — these need a decision

### 4.1 **Nothing in P6's plan ever calls the discount.** ← the biggest one

`screen_metadata`, `suppress_tool_metadata`, `may_populate` and `field_permitted` appear in **no
sibling file**, and Task 20's `DEGRADATION_ORDER` binds exactly three stages — direct, rule, llm
(`20-21:105-107`). §2.2's suppression **must fire before ranking** and has **no caller**. So a
`DirectSlots` declaring a metadata-property slot turns `python-docx` into a `direct` fact and **no
test in the part would see it**.

This is a **producer with no consumer** — the mirror of the class round 4 was built to find, and it
sits on Done-means 22. Task 20 or Task 24 must add the stage.

### 4.2 D9's positive half is asserted nowhere

Now that `target_school` and `client` are `destination_eligible = TRUE`, **no test asserts it** — and
the losing Task 9's now-red test was the only test touching those two keys at all. Task 2 is the
natural home for `test_target_school_and_client_are_destination_eligible`.

### 4.3 `prior_releases` under-reports every group release

`15-22:690`'s `_prior_releases` loops `audit_records_for(conn, file_id=file_id)`, and Task 10's reader
(`08-11:2100-2103`) filters `file_id = ?` on the **column only**. Brief §15 demands it also match the
`explanation` — **that demand is unimplemented in Task 10**, and Task 15 is its only consumer. §8.4's
*"truthful and specific"* retraction limit is exactly what breaks. **Neither version flags it.**

### 4.4 A broader `correction_scope` is written and never read

`reclassify` accepts all six of §8.7's scopes and writes `correction_scope=correction_scope`
(`15-22:1383`), but `suppressed` (`:1275`) only ever calls `learning_records(conn, FILE_SCOPE,
file_id)`, and P1's reader filters `correction_scope` in SQL. **A group- or corpus-scoped rejection is
structurally unreadable by the only consumer of rejections.** SPEC says *"Broader scope is applied
only where the user selects it"* — nothing applies it. Value computed and dropped, identical in both
versions. Name it against OQ7.

### 4.5 A test that does not test what it claims

`test_p7_does_the_filtering_because_p1s_reader_does_not` (`15-22:1006`): delete the
`proposal_class != PROPOSAL_CLASS: continue` line from `suppressed` and **the test still passes**. It
needs a case where the other part's record is the only record. Identical in both versions.

### 4.6 `ATTEMPTED_PRODUCERS[0] == "direct"` collides with the reliability state `direct`

Task 5 publishes that literal (`05-06:409`), and Task 1's *"no string literal spelling a state name"*
guard forbids it on its face. Neither version resolves it. Brief §16 narrowed the guard to
collections whose members **are** the six states, which probably saves it — **confirm, do not assume.**

### 4.7 The A04 fixture contradicts Done-means 22

`tests/eval/fixtures/adversarial/A04.json` is worded as the **suppression** tier but carries
`expected_outcome_kind: "produced"` with `retained_as: "supporting_evidence"` — the **demotion** tier
(`07-09:1878-1879`). A live contradiction with Done-means 22, which asserts both halves.

### 4.8 The 115-entry catalogue compiler still has no home

Brief §18 says something must compile catalogue 01's 115 entries and no P6 task does. The **losing**
Task 9 wrote a boundary-rule matcher (`07-09:2113-2129`) that was executed against all 115 entries
with **0 misses / 0 false positives**, correctly handling `Notion`/`Notional` and
`Microsoft Word`/`Microsoft Word skills certificate`. **Keep the work; move it to the loader** — it is
exactly the compiler §18 says does not exist. It must **not** go in `src/facts/`.

Also from the loser: the 115-entry conformance test (`07-09:1885-1900`), with its
`@pytest.mark.skipif(not CATALOGUE.exists())` (`07-09:1881`) **removed** and the catalogue injected —
as written, the only test exercising the 115 entries silently vanishes if the artifact moves, and it
reaches from `tests/p6/` into `planning/`.

### 4.9 Two names for one unwritten thing

B's `field_permitted` (`08-09:1462`) vs A's `may_populate` (`07-09:2032`). Neither is in the skeleton
and **no sibling file references either name**. Pick one and record it.

### 4.10 `document_title` has a publisher and no catalogue field

The winner routes it to `FieldNotInCatalogue` (the honest outcome); the loser routes it to `work_type`
via a fixture it never runs. If a PDF title should reach a fact, **the catalogue owes a row** —
Task 2's call.

### 4.11 Does `p6_conn` seed Task 2's catalogue rows?

`07-09:41-42` alone says the fixture creates *"Task 2's `fields` catalogue rows"*; `10-13:44-47` and
`14-15:48-50` say only *"P6's own tables"*. **Tasks 7–9's tests assume it does and Tasks 10–15's do
not say so.** Brief §17 gives the conftest to Task 1 but says nothing about its contents. `10-13:46`
alone also adds `tmp_path` to the fixture list. **Rule it, or the first executor guesses.**

---

## 5. SMALLER FIXES QUEUED FOR ASSEMBLY

- `15-22:742` — *"Expected: PASS — 22 passed"*; the file defines **25** `def test_` functions.
- `15-22:519` and `:1180` — *"Expected: FAIL — ImportError"* where the module does not exist yet. That
  is `ModuleNotFoundError`. Both versions.
- `15-22:1668` — writes `"sha256:different-bytes"` into `files.content_hash`; the live digest carries
  **no `sha256:` prefix**. Cosmetic, but it teaches a wrong shape.
- `20-22:264-266` — `Gate(conn, component_version=…, area_of=…)` misses nine required keywords and
  **invents `area_of`** where Task 11 publishes `scope_for` + `files_in_scope`.
- `20-22:1180-1186` — fixture 10 sets `protected=False` **and** a grant, so Task 11's branch
  (`PLAN-tasks-11.md:1551`) yields `Released`, not `NeedsConsent`. Both conditions must flip.
  **A's fixture 10 has the identical defect.**
- `20-22:1177` — `ConsentRequirement(items=…)` holds **item kinds** (`kind_of(item)`,
  `PLAN-tasks-11.md:1556`), not observation keys. Withdraw the front-matter pin at `20-22:104-107`.
- `20-22:1156-1158` — `RedactionEntry` omits three of Task 8's seven fields (`08-11:105-107`).
- `20-22:1066` — fixture 6's `max_dossier_tokens=1` is never read; Task 13 reads P1's stored ceiling.
  Needs `budget.set_ceiling` in `seed()` **and** `measure_tokens`.
- `20-22:895-902` — `_audit()` builds values from `AUDIT_FIELDS` only, so `_audit(redaction_manifest=…)`
  on fixture 9 is **silently dropped** — the exact failure its own docstring at `:884` warns of.
  Widen to `AUDIT_FIELDS + CARRIED_FIELDS`.
- `20-22:1216-1219` — `_denied(*remedies: str)` bypasses Task 13's `deny()`; bare strings where
  `RemedyOption` belongs.
- `08-09:727-729` — `_observations_for_version` called **inside** the per-slot loop: N identical
  queries for N slots. Hoist it.
- `08-09:172` — `_refuse` defined and never used.
- `08-09:7-8` — `Consumes:` omits `facts.fields`, though `08-09:415` imports `FieldNotInCatalogue`.
- `08-09:1465` — `_METADATA_ZONE = _check("metadata", _ZONES, …)` runs a P4 validation at **import**
  time, so an upstream rename becomes an import failure rather than a first-use failure. Good
  property; confirm it is intended.
- `15-16:1` — H1 reads *"PLAN, Tasks 15–22"*; the file contains 15–16 only. (Loser, but it shows how
  the duplication happened.)

---

## 6. WHAT THE RULINGS CONFIRMED IS **NOT** WRONG

Worth recording, because each was suspected:

- **§8.7 query-before-classify is honoured in both Task 16 versions.** Not the Task 11 bypass shape.
- **Both Task 17 versions are safe on the move gate.** Absence, then `protected`, then policy.
- **`delete_derived` is not a dead path** — it refuses on both sides of D3's enumeration.
- **`DERIVED_PROJECTIONS` matches the live schema**, verified by introspection.
- **D10 is a no-op for P7 Tasks 17–19** — zero hits for span, region, `norm`, origin.
- **`field_id` had zero occurrences in P7 Tasks 17–19** — that ruling was P6-only in practice.
- The **`Interfaces:` name-level join is clean** in both parts — every consumed symbol resolves to a
  live P1–P5 symbol or a sibling's `Produces:`. §3.1 is a *signature* defect, not a name defect.
- **Done-means coverage is complete**: P6 30/30, P7 13/13, nothing claimed outside the SPEC's list.

---

## 7. THE REMAINING RULINGS — Tasks 18, 19, 21, 22, and what they turned up

### 7.1 P7 Task 18 → `PLAN-tasks-15-22.md` — **decided by the standing safety rule**

**The loser silently drops every file it has not classified.** `17-19:1155`:
`if record is None or not record.protected: continue` — and its own test pins the consequence,
`assert summary == ProtectedSummary(count=0, class_breakdown={})` over five real files (`:1056`).
**With no detector (D2) that is every file in a real corpus rendering as an empty summary**, which is
precisely §8.6's *"false impression that an unprocessed file was understood and found unimportant"*.
Its docstring concedes it and punts the deferred count to P13 (`:1052-1054`) **while handing P13 no
number to render.**

The winner counts **every** file in scope by resolved class, zero-filled across `HANDLING_CLASSES`
(`15-22:2213-2221`), so an unlooked-at corpus reports `count = 0` with
`class_breakdown["unreadable_unclassified"] == len(corpus)` — **marked and counted, never omitted.**

**But the winner has a two-denominator bug that must be fixed at assembly.** `count` is the protected
count; `class_breakdown` is a census of the whole scope. A's own test has
`class_breakdown["highly_sensitive_credential_bearing"] == 1` for a file whose flag is **False**
(`15-22:2081-2090`). A UI rendering §8.4's *"11 protected identity records"* off the breakdown would
**describe an unprotected file as protected**. Keep the whole-scope census — it is what satisfies the
safety rule — but rename the field or add `scope_total` / `protected_breakdown`, and document that
`sum(class_breakdown)` is files-in-scope, not `count`.

Graft from the loser: `settings_for(policy) -> RedactionSettings` as a pure function
(`17-19:1120-1132`); `test_the_summary_has_two_fields_and_neither_can_hold_a_filename` using
`typing.get_type_hints` (`:1004-1015`) — a **true type-level proof**, where the winner only compares
field *names*; `test_the_breakdown_is_ordered_by_the_closed_vocabulary` (`:1023`);
`test_neither_surface_writes_anything` (`:1088`) — **the winner has no C4 test at all**; and the
loser's verbatim P13 OQ quotation (`:1105`) over the winner's paraphrase.

### 7.2 P7 Task 19 → `PLAN-tasks-17-19.md` (HIGH) — **the loser has the §19 bypass, blessed by a test**

`egress_functions` filters to public, module-level functions (`15-22:2694-2698`) and
`assert_single_egress` then checks the parameters of **`functions[0]` only** (`:2712-2735`) — so a
private `_format(text: str)` beside the entry point is **never checked**, and the loser ships a
fixture asserting that this **passes**: `test_a_private_helper_is_not_an_egress_point` (`:2522-2523`).
**A filter placed before the only check, with a test blessing it** — the exact shape brief §19 exists
to catch, found a second time.

It is also **blind to classes**: `inspect.isfunction` (`:2695`) skips them, so
`Client.send(self, prompt: str)` — the likeliest real SDK-wrapper shape — is invisible.

The winner checks **every** function the module defines, public or private, module-level or method,
and takes the entry-point *count* only over the public ones (`17-19:1710-1741`, `:1996-2013`).
Twenty-six tests against four conforming and seventeen non-conforming fixtures, versus seventeen.

Fix at assembly: `17-19:1381` is **missing the `assert` keyword** — the call runs, the comparison is
discarded. Graft the loser's **live tripwire** (`15-22:2624-2626`):
`assert importlib.util.find_spec("llm_harness") is None` with the message *"P8 has landed: run
assert_single_egress over its transport module and replace this test with that assertion."* The
winner's equivalent only introspects its own signature and **can never fire**.

### 7.3 P7 Task 21 → `PLAN-tasks-20-22.md` (medium) — **D7 and D10 nearly flipped this one**

The original margin was almost entirely that the winner held **C24** and **C22** open. **D7 and D10
erase that margin and turn it into a liability.** `HELD_OPEN` (`20-22:1993-2020`) has three entries and
**two are now ruled**: `P6-sensitivity-field-row` (C24 → D7) and `P4-region-origin` (C22 → D10).

> **A guard asserting that a ruled question is open fails the day the plan executes** — exactly the
> failure both authors correctly diagnosed for P6 OQ11 under D2, reproduced twice in the very file
> that diagnosed it.

It still wins on grounds D7/D10 do not touch: the loser **re-publishes the entire eleven-entry
`OPEN_QUESTIONS` mapping** (`15-22:4290-4356`) that Task 2 already writes (`01-03:1257`) — a second
home for a vocabulary, **created inside the guard task whose job is to prevent exactly that**.

**Mandatory fixes:**
- `20-22:1993-2020` — drop `P4-region-origin` and `P6-sensitivity-field-row`; **`I6` is the only
  survivor.** Update `:1737-1739`'s `assert set(HELD_OPEN) == {…}` to one key, then **add** the still
  open items: the five round-5 cuts and `filename`.
- `20-22:1800-1817` — `test_p7_assumes_no_origin_for_a_normalized_bounding_box` forbids all
  `ast.BinOp` on a Region field. **D10 permits that arithmetic.** Delete, or invert to assert
  top-left.
- `20-22:1748-1758` — the first half dies under D7; **the second half strengthens.** *"P7 reads no P6
  surface, holds no `file_facts`"* now asserts the **ruled** outcome. Rename to
  `test_p7s_classification_record_is_the_sole_home_d7` and keep.
- `20-22:1753` — the forbidden-token list forbids **`field_id`**, a name that no longer exists
  corpus-wide. Change to **`field_key`** or the guard checks nothing.
- `20-22:1712-1716` — asserts `"area_of" in Gate.__init__`. Rewrite against `scope_for` /
  `files_in_scope`.
- `20-22:2035-2041` — the gazetteer guard allows module-level tuples of `len <= 20`; `AUDIT_FIELDS`
  is **19**. It passes by one. Allowlist the published vocabularies by name instead.

Graft from the loser: **one named test per SPEC Open question 1–11** (`15-22:4013-4131`) — the winner
covers only 1, 3, 7, 10, 11, and the skeleton asks for all eleven. **The single most valuable graft.**
Also `test_d2_privacy_issues_no_write_against_a_table_it_does_not_own` (`:4177-4198`), which collects
the tables P7 owns and checks every SQL write literal against that set — strictly stronger than the
winner's three hard-coded string checks; plus `test_oq8_…`, `test_oq9_…`, and
`test_privacy_never_calls_the_upstream_safety_gate` (`:4218-4223`), which asserts `safety.admit` is
**un-bound**, not merely un-imported.

The loser's `NEEDS_JOSEPH["C5"]` entry (`15-22:3760`, `:4368`) is the C24 question **under the wrong
label** (brief §14). Under D7 it is **deleted outright**, not relabelled.

### 7.4 P7 Task 22 → `PLAN-tasks-20-22.md` (medium-high)

The closest of the three. The winner has three tests the loser lacks, each converting a paragraph into
an assertion: `test_the_wave_2_caller_has_nowhere_to_put_a_gate` (`:2417-2425`) proves *"release was
called zero times"* **structurally**; `test_the_policy_parameter_is_p5s_safety_policy_and_not_p7s`
(`:2428-2436`) nails a live two-vocabularies trap one parameter wide; and
`test_with_no_detector_every_real_file_resolves_to_denied_unclassified` (`:2704-2722`) is **the
no-detector honesty clause as a passing test** — the loser states it only in prose.

Fixes: `:2420` asserts `len(parameters) == 18` — **`run_wave2` has 17**, verified by execution, and
the winner's own front matter lists exactly seventeen names while calling them eighteen.
`:2520-2521` calls `transcription_authorized_for("Academics")` against a published
`(conn, scope, *, plan_version)` — TypeError. `:2437-2452` asserts `transports == []` then loops the
empty list, so **`assert_single_egress` is never called** — a test that passes immediately.

### 7.5 CUT 2 — **not cheaply deletable.** Done-means 3 loses its only instrument

`assert_single_egress` has exactly one consumer and it is a **test in Task 22** (`20-22:2117`,
`:2256`, `:2436-2452`) — Done-means 13's second clause. Nothing under `src/privacy/` imports it, so
the **module** deletes cleanly. Deleting the **task** costs: two lines and a for-loop in Task 22;
`tests/p7/transport_fixtures.py` vanishing from the skeleton's File Structure; and **Done-means 3
losing its only instrument** — *"P7 proves the instrument, the unforgeable token, and the single
materialisation locus"* becomes two of three. L1 (Task 12) and L2 (Tasks 9/21) survive untouched.

**Neither Task 22 version flags CUT 2 or CUT 4 at all**, though both import `transport_guard` and both
pin the `Gate` facade. Brief §9: *"Do not silently comply with a cut, and do not silently ignore
one."* Both callouts are a **required addition** to the winners.

---

## 8. FIXTURES: SIXTEEN BECOMES EIGHTEEN, AND THREE ARE BROKEN IN BOTH

Both Task 20 versions publish sixteen, and **thirteen of the sixteen agree exactly** (1–12, 16), with
identical `FIXTURE_COVERAGE` keys. Only 13/14/15 diverge, and **each side holds something the other
lacks** — the loser carries **OQ5 as a two-branch pair** (14/15), the winner carries a real §2.9
**unreadable** extraction on P4 fixture 18 and the item-kind-independence of the protected rule.

**All belong in the assembled set → eighteen fixtures.** Every `len(FIXTURES) == 16`, `range(1, 17)`,
`MODE_SWEEP`, `SKELETON_FIXTURE = 10` and `by_number(n)` reference in Tasks 20 and 22 needs **one
renumbering pass**.

### Three fixtures are broken in **both** versions

1. **Fixture 7 — `always_local_item` is unreachable either way.** The loser uses
   `MetadataField(name="gps")`, which is **unconstructible**: `__post_init__` refuses any always-local
   name (`PLAN-tasks-07.md:844-846`), so the module cannot even import. The winner uses an `Excerpt`
   in the `ocr` **zone**, which `check_item` never branches on (`PLAN-tasks-07.md:941-990`) — and P4
   fixture 8's text unit carries **`zone = None`**; the string `ocr` lives only in the locator prefix.
   Its failure is **silent** (the fixture resolves and is released), which is worse to diagnose.
   **The fix, identical for both:** the only `AlwaysLocalRequested` the gate can catch on an `Excerpt`
   is `item.observation_key in sensitive_keys` (`PLAN-tasks-07.md:983`). Fixture 7 must stand on a
   **P5-signalled key**, and `seed()` must write that signal.
2. **No P5 sensitivity signal is seeded in either suite**, so `sensitive_keys` is empty and
   `always_local_item` is unreachable regardless. **Named nowhere before now.**
3. **Fixture 10 cannot return `NeedsConsent` in either version** — it sets `protected=False` *and* a
   grant for the scope, so Task 11's branch (`PLAN-tasks-11.md:1551`) yields `Released`. Both
   conditions must flip.

### `Gate.__init__` is twelve keywords and **neither version has it**

`PLAN-tasks-11.md:1440-1447` adopts the loser's ten **verbatim** and adds `measure_tokens=None`,
`template_for=None` → **twelve**. The loser's equality test therefore **fails**; the winner pins
**two** and invents `area_of`. Fixtures **4 and 16** (`protected_records_template`) reach their denial
only through `template_for`, and fixture **6** only through `measure_tokens` — with the `None`
defaults **none of the three replays**. Fix: widen to twelve, have `gate_arguments()` supply
`template_for=lambda _fid: "Protected Records"` and a `measure_tokens`, relax the equality.

**`Gate.__init__` has no owner:** Task 11 says Task 20 pins it (`:124`); Task 20 says it reports a pin
on Task 11 (`:2794`). Each defers to the other.

### `release_id` — only the loser states it honestly

`AuditRecord.release_id` is `None` on a release record and **the join runs ledger → events**. The
loser asserts it (`15-22:3005-3007`); the winner publishes
`Released(release_id="release-fixture-09")` and excuses `release_id` from comparison, so it never
confronts the conflict. Graft the loser's assertions and carry `PLAN-tasks-11.md:1766` into the
preamble as an open Contract-out item owed to Task 10.

---

## 9. P6 FRONT-MATTER HARVEST — what the shared preamble must and must not say

Four P6 files carry front matter (`07-09` 1–128, `10-13` 1–139, `14-15` 1–99, `16-19` 1–91). It is
**substantive** and must be harvested, not dropped. Clean result first: grepped for `sensitivity`,
`target_school`, `destination`, `field_id`, `subject`/`course`, `norm`/top-left/bottom-left,
`jurisdiction` and every test count — **zero hits on every one**. D6–D10 and the `field_key` ruling are
**uncontaminated** by P6 front matter.

### 9.1 MUST NOT reach the preamble

- **The six states by index.** `10-13:95-105` states as a shared convention *"The six reliability
  states are addressed by index into P4's tuple, never spelled"*, with a `_VALIDATED = STATES[2]` code
  block. **Brief §11 overrules it.** Delete the block, do not adapt it. The index is *correct today*,
  which is exactly why it passes review and still has to go.
- **The guard's misstatement**, `10-13:97`: *"Task 1's test asserts the absence of any string literal
  spelling a state name anywhere else in `facts`."* Brief **§16** narrows it. Read literally the broad
  form forbids `VERSION_FAMILY_STATES`, `SESSION_STATE`, `EVENT_STATE` and `LLM_STATES` — **it breaks
  three sibling tasks.**
- **`FACT_ORIGINS` / `ATTEMPTED_PRODUCERS` by index — in THREE files** (`07-09:47-50`, `10-13:106-109`,
  `14-15:52-56`). Brief §11's closing sentence — *"The same rule applies to every closed vocabulary
  either part publishes"* — overrules these too, but never spelled them out. **This needs an explicit
  preamble ruling**: Task 4 publishes a named constant per `FACT_ORIGINS` member, Task 5 per
  `ATTEMPTED_PRODUCERS` member. Keep the surviving half — *"Tasks 4 and 5 own the literal spelling of
  each member"*. Same call for `16-19:52-54`'s `SIGNAL_TIERS[-1:]`: bless it explicitly or convert it,
  **do not leave it silent.**
- **`unresolved` reasons spelled as bare literals at the call site** (`07-09:50-55`, `10-13:109-112`).
  Runtime validation catches a typo; **it does not stop the literal being a second home.** Keep the
  mechanism, delete the conclusion.

### 9.2 The cache key — **three of four files carry the LOSING rule**

`07-09:110-111`, `14-15:80-82` and `16-19:76-77` all key on *"the observations the **fact cites**"*.
**Only `10-13:119-121` carries the winner** — *"every observation of that **file version**"*, keyed per
(file version, deterministic pass). Brief §15 settles it that way, and `10-13:128-131` carries the
deciding argument, which must reach the preamble verbatim:

> **The fact and the abstention produced by one pass share one key.** … an abstention with no
> citations has no cited observations to compute a key from. One key per pass answers both.

**Assemble from the majority and you ship the rule the brief already rejected.**

And **all four** files license the per-module copy (*"the helper is written out in each module that
needs it"*), with each author apologising that they *"cannot add to `facts.cache`, which Task 6
owns"*. Brief §18 deleted that: **one helper in `facts.cache` taking `(conn, content_hash,
observations)`**. If the apology reaches the preamble it *licenses* eight copies of a deleted rule.

### 9.3 The build order, which exists nowhere else

**1–6 → 7–9 → 10–13 → 14–16 → 17–19**, and inside Wave B: **execute Task 11 before Task 10 and
Task 12** (`10-13:69-84`). Task 13 may run at any point. Run Task 10 before Task 11 and its Step 2
failure is the *wrong* failure and Step 4 cannot pass. Also load-bearing and stated once: **`chain()`
walks forward only** (`16-19:46-48`), so a history read must start at the **oldest** row — Task 18's
`fact_history` finds the tail before it walks.

### 9.4 Three things the preamble must PIN, because the files disagree

1. **`write_fact`'s signature is written three ways, and two end in a banned `...` placeholder**
   (`10-13:26-28`, `14-15:26-28` vs `07-09:25-27`). Brief §2 forbids placeholders. **Three tasks
   consume it and two are guessing at its tail.**
2. **The published-surface import lists disagree; only the UNION is correct.** `facts.evidence`'s
   `context_pair` appears in one front matter; `facts.file_facts`'s `FILE_FACTS_COLUMNS` /
   `FORBIDDEN_COLUMN_SUBSTRINGS` in one; `facts.fields`'s `FIELD_SCOPES` / `DOMAIN_FIELDS` /
   `fields_in_scope` in one. **Take the union or three of Tasks 16–19's imports vanish.** Note
   `facts.states.strength` / `is_stronger` are **CUT 6's target** and Tasks 14–19 depend on
   `is_stronger` — that dependence is the evidence a reader needs to decide CUT 6.
3. **Does `p6_conn` seed Task 2's catalogue rows?** `07-09:41-42` alone says yes; `10-13` and `14-15`
   say only *"P6's own tables"*. **Tasks 7–9's tests assume it does and Tasks 10–15's do not say so.**
   Brief §17 gives the conftest to Task 1 and is silent on its contents. `10-13:46` alone also adds
   `tmp_path`. **Rule it, or the first executor guesses.**

### 9.5 Evidence to preserve verbatim

The four "Verified live, 2026-08-22" blocks, with their rationale (`07-09:60-61`): *"Every one of
these was run before a line of this plan was written, because three defects on this project came from
reading a signature instead of importing it."* The strongest single item (`07-09:82-87`): writing
fixture 1's observation at `extractor_version = "1.0.0"` and again at `"2.0.0"` produces the **same**
`observation_key`, and `observations_by_key` returns both rows — *"which is the whole of M14 and
Done-means 30, provable rather than asserted."* Also the **byte-exact bytes of P4 fixtures 1, 6, 7 and
18** (`07-09:89-99`) — the only place in P6's plan where fixture bytes are written down; drop it and
every Step-2 expectation in Tasks 7–9 becomes a guess. (That block says *"the three these tasks use"*
and pins **four**.)

### 9.6 Dangling references that break at assembly

`14-15:93` and `:886` both say *"See Contract ambiguities at the end"* — **that file has no such
section**, dead in the source. `16-19:4` says *"Read `PLAN-tasks-14-15.md` first"*. `07-09:44` and
`10-13:134-135` both name a file that will not exist. `14-15:1` claims *"Tasks 14–19"* and `:3-4`
*"Wave C (14–16) and Wave D (17–19)"* — the file holds **only 14 and 15**; build the assembled wave
structure off that header and you inherit a four-task overcount.

---

## 10. NEW OPEN QUESTIONS — these need Joseph, and none existed before today

- **Is `ProtectedSummary.class_breakdown` a breakdown of the protected set, or a census of the
  scope?** `SPEC.md:363`, `PLAN-SKELETON.md:1152` and Done-means 10 (`SPEC.md:430`) are **all silent**;
  the two authors read it in opposite directions and both readings are defensible from the text. This
  decides **whether §8.6's unprocessed-file count has a home in P7 at all.**
- **Where does the "deferred / not yet looked at" count live?** If P7's summary is protected-only,
  nothing in P7 lets P13 render *"31 files, none classified"*, and §8.6's *"false impression that an
  unprocessed file was understood and found unimportant"* has **no instrument on either side**.
- **Three names for one concept**: `scope_for` (Task 11), `files_in_scope` (Tasks 15/18), `area_of`
  (Task 22). OQ3 is held open by three device names. One name, or an explicit statement that resolving
  a scope and enumerating a scope are two jobs.
- **Who validates `redaction_settings`?** A7 puts it on `policy.py`; both Task 18 versions validate
  **again** in `display.py`. Two computations for one value, and it silently changes which exception
  Task 18's load-error tests see.
- **`IS_MODEL_TRANSPORT`** (`20-22:2445`) — Task 22 reads it; **no task writes it.**
- **`SHOWN` / `REDACTED` get a third home.** Task 18 publishes them plus `SETTING_VALUES` in
  `display.py` claiming *"no earlier task's Produces block claims them"* — **now false**: Task 5's A7
  publishes them in `policy.py` (`04-07:110`, `:1045-1046`). Pick one owner and re-export.
- **Where do P7's reliability-state and basis constants live?** D2 makes P7's record authoritative and
  P7 must not import P6, so `"user_confirmed"` and `"user"` have **no published home and no named
  owner**. Task 2 is the obvious place; nobody has been told to build it.

---

## 11. BACKLOG STATUS — what is applied, what is not

Both `PLAN.md` files are assembled and rebuild reproducibly from
`planning/parts/build.py`. **Assembled is not the same as executable**, and this is the line.

### APPLIED (commit `fa8d7ae` unless noted)

| | What | Where |
|---|---|---|
| ✅ | **`set_policy` — 21 call sites** (not 18). `author=` dropped, required `reason=` supplied per site. | 5 files |
| ✅ | **`policy_version`** — the two helpers that hardcoded `"policy-1"` and fed `set_policy` now use `UNSET_POLICY_VERSION`; a bare `""` for the same constant replaced too. | `17-19`, `15-22` |
| ✅ | **`area_of` → `scope_for`**, 16 sites, **plus widening the published type to `Callable[[str], str \| None]`** with the reason stated. | `20-22`, `11` |
| ✅ | **Task 21's `HELD_OPEN`** no longer asserts C24 and C22 are open; the C24 test asserts D7's outcome, the C22 test inverts to pin the flip to the Vision adapter. | `20-22` |
| ✅ | **Four `Modify: src/privacy/gate.py` lines** — six `Gate` methods now have a producer (mandatory under D13). | `15-22`, `17-19` |
| ✅ | `field_key` corpus-wide, incl. deleting Task 2's second identifier column (`1474de7`) | P6 |
| ✅ | 26 stale test-count claims → **1302** (`d7607f0`) | both |
| ✅ | D6/D8 propagated into P6's SPEC (`c0aad4e`); P7's SPEC amended under D7 (`6acdce5`) | both |
| ✅ | **Back matter is no longer dropped** — the extractor absorbed it into the last task and lost it when that task lost. Three appendices recovered across both parts. | assembler |

**Checked and deliberately NOT changed:** three further `policy_version="policy-1"` sites feed
`revoke()` and `mint_release()`, where `policy_version` is a **binding term** and an already-minted
version is correct. `PLAN-tasks-20-22.md`'s forbidden-token guard names `field_key`, which is right
under the rename. `PLAN-tasks-11.md`'s **C5** citations are correct and still live.

### NOT APPLIED — still blocks execution

| | What | Cost |
|---|---|---|
| ❌ | **`Gate.__init__` is twelve keywords and no fixture supplies them.** Task 20 pins two; the graft of `gate_arguments()` from `15-22:3319-3339` is the fix, widened to twelve, supplying `template_for` and `measure_tokens` so fixtures 4, 6 and 16 can replay. **Task 20 owns it** (§3.3 of the preamble closes the deferral loop). | medium |
| ❌ | **Fixtures: sixteen → eighteen**, then one renumbering pass over every `len(FIXTURES) == 16`, `range(1, 17)`, `MODE_SWEEP`, `SKELETON_FIXTURE` and `by_number(n)` in Tasks 20 and 22. | medium |
| ❌ | **Fixture 7 cannot deny in either version**, and **no P5 sensitivity signal is seeded in either suite**, so `always_local_item` is unreachable. `seed()` must write the signal and the fixture must stand on a P5-signalled key. | medium |
| ❌ | **Fixture 10 cannot return `NeedsConsent`** — `protected=False` *and* a grant. Both flip. | small |
| ❌ | **Named constants** — brief §11 reaches **neither** version of anything. P6's states, `FACT_ORIGINS`, `ATTEMPTED_PRODUCERS`, `UNRESOLVED_REASONS`; P7's `basis="user"` / `reliability_state="user_confirmed"`, which **Task 2 does not yet publish** (see the D7 open item). | large |
| ❌ | **The §3.4 cache key is still written out eight times.** One helper in `facts.cache`. | medium |
| ❌ | **`ProtectedSummary` gains `scope_total`** (D11) — implementation is small, the test change is large, and the type-level "no field a filename could occupy" proof must move with it. | medium |
| ❌ | **`AuditRecord.release_id`** — `assert record.release_id == decision.release_id` and two fixtures building `release_id="release-1"` are wrong under D14. | small |
| ❌ | **`SHOWN` / `REDACTED` have three homes and three names** (`REDACTION_VALUES`, `SETTING_VALUES`, `FACET_VALUES`). One home, everyone re-exports. | small |
| ❌ | **The discount has no caller** (§4.1). Task 24 adds the stage. | medium |
| ❌ | **CUT 2 and CUT 4 callouts** are missing from both Task 22 versions, and Task 19's is unlabelled prose in which the author ruled the cut themselves. | small |
| ❌ | **`IS_MODEL_TRANSPORT`** is read by Task 22 and written by no task. | small |
| ❌ | **`prior_releases` under-reports every group release** (§4.3) — Task 10's reader filters the column only. | medium |

### Still unruled

`run_wave2`'s parameter count is **17**, and two sections say eighteen. The `NeedsConsent` ownership
contradiction resolves to `consent.py` (brief §15's direction), and the losing reasoning is kept as
the justification. Neither is applied yet.
