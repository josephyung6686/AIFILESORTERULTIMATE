### Task 1: Package skeleton, P6's authorship, and the six states published once

**Files:**
- Create: `src/facts/__init__.py`
- Create: `src/facts/authorship.py`
- Create: `src/facts/states.py`
- Create: `tests/p6/conftest.py`
- Test: `tests/p6/test_p6_authorship.py`
- Test: `tests/p6/test_p6_states.py`

**Interfaces:**
- Consumes: `database_agent.events.RESERVED_EVENT_TYPES`, `evidence_shape.vocabulary.RELIABILITY_STATES`, `evidence_shape.vocabulary.EXTRACTOR_RELIABILITY_STATES`, `evidence_shape.vocabulary.check`, `evidence_shape.vocabulary.NotInVocabulary`, `evidence_shape.conformance.validate_observation`, `evidence_shape.fixtures.by_number`.
- Produces: `SUBSYSTEM: str`, `COMPONENT_VERSION: str`, `AUTHORED_EVENT_TYPES: tuple[str, str]`, `event_defaults(**fields) -> dict`; `STATES: tuple[str, ...]` (re-export), `STRENGTH_ORDER: tuple[str, ...]`, `EXCLUDED_STATE: str`, `strength(state: str) -> int`, `is_stronger(a: str, b: str) -> bool`.

**Done-means:** foundational to all; directly none.

**Why this is Task 1.** Two things every later task touches are settled here and nowhere else: whose
name lands in `events.subsystem`, and how the six reliability states are spelled. Both are the kind
of value that, left to the task that first needs it, gets typed by hand in twenty places. Putting
them first means Task 25's guard has exactly one module to look at for each.

**`event_defaults` is a helper, not a writer.** It fills §8.2's authorship fields and returns a
plain `dict` for the caller to hand to P1's `append_event`. It opens no connection and writes
nothing, so there is no path on which `facts` appends an event without a caller having decided one
is due. This is P3's shape verbatim (`src/scan_agent/authorship.py`, read on 2026-08-22), and P6
follows it rather than inventing a second one.

**The two event names carry a space.** `RESERVED_EVENT_TYPES` was introspected on 2026-08-22 and
contains `fact creation` and `fact rejection` — nineteen names, both present. `fact_creation` raises
`UnregisteredEventType` at run time, not at review, which is the same class of defect as MINOR 2's
`OCR`/`ocr`. P6 registers neither name, because registration is a spec-level act (P1 *Contract out*
§3, rule 4).

> **A skeleton line corrected against live code, 2026-08-22.** The skeleton's Task 1 says
> *"`conformance.validate_observation` raises `NonConforming` on an observation whose `reliability`
> is `validated`"*. It raises **`NotInVocabulary`**. Verified by execution:
>
> ```text
> RAISED NotInVocabulary : reliability='validated' is not one of ('direct', 'possible');
> adding a member is a P4 contract revision and a shape-version bump, not a local decision
> inside an extractor (segment-kind rule 5)
> ```
>
> `NonConforming` and `NotInVocabulary` are unrelated classes (`NotInVocabulary` subclasses
> `ValueError`; `NonConforming` subclasses `Exception`), so a test written to the skeleton's wording
> would fail against shipped, green P4. The test below expects `NotInVocabulary`. The boundary the
> skeleton wanted asserted — extractors write two of the six, P6 owns all six — is asserted exactly
> as it asked, from both sides, in one test.

> **A skeleton line narrowed, for the same reason.** The skeleton asks Task 1 to prove *"the absence
> of any string literal spelling a state name anywhere else in `facts`"*. Three sibling task files,
> already written against this skeleton, put state literals inside `src/facts/`:
> `PLAN-tasks-14-15.md` has `VERSION_FAMILY_STATES = ("validated", "possible")` and
> `SESSION_STATE = "possible"`; `PLAN-tasks-16-19.md` has `EVENT_STATE = "validated"` and
> `LLM_STATES = ("llm_supported", "possible")`. A producer naming the one or two states it is
> allowed to write is not a second copy of the vocabulary — it is the producer's own contract, and
> forbidding it would make this task's test the thing that blocks three correct tasks.
>
> What preamble rule 2 actually forbids is *"a second copy and no alias table"*. So the guard here
> is the precise one: **no module in `facts` other than `states.py` binds a module-level collection
> whose members are the six**. That is runtime introspection over `vars(module)`, not a source-text
> search, and it catches the defect the skeleton was aiming at while permitting the three subsets
> above. Task 25 owns the whole-package version of it.

**`rejected` has no strength, and asking for one raises.** §3.13: *"A rejected fact is a proposal
that the user or validator marked as incorrect."* It is an exclusion, not the bottom of a ladder — a
`rejected` fact that compared as merely weaker than a `possible` one would be resurfaced by any
comparison that picks the strongest, which is exactly what §8.7 forbids (*"Otherwise the system will
repeatedly resurface the same attractive but incorrect grouping"*). So `STRENGTH_ORDER` has five
members, `STATES` has six, and the sixth is named as excluded rather than omitted silently.

- [ ] **Step 1: Write the two failing tests**

```python
# tests/p6/test_p6_authorship.py
"""M8: the acting part authors, P1 writes. P6 authors two of §8.2's nineteen."""
import pytest

from database_agent.events import RESERVED_EVENT_TYPES, append_event

from facts.authorship import (
    AUTHORED_EVENT_TYPES, COMPONENT_VERSION, SUBSYSTEM, event_defaults,
)


def test_the_two_event_names_are_8_2s_own_and_carry_a_space():
    # Introspected from P1 on 2026-08-22: RESERVED_EVENT_TYPES contains
    # "fact creation" and "fact rejection". `fact_creation` raises
    # UnregisteredEventType at run time — the MINOR 2 `OCR`/`ocr` defect again.
    assert AUTHORED_EVENT_TYPES == ("fact creation", "fact rejection")
    for name in AUTHORED_EVENT_TYPES:
        assert " " in name
        assert "_" not in name


def test_both_names_are_already_reserved_so_p6_registers_nothing():
    # P1 Contract out §3, rule 4: registration is a spec-level act. Both names are
    # in P1's frozen table of nineteen; P6 declares neither.
    assert set(AUTHORED_EVENT_TYPES) <= set(RESERVED_EVENT_TYPES)
    assert len(RESERVED_EVENT_TYPES) == 19


def test_facts_publishes_no_registration_call():
    import facts.authorship as module
    assert not [n for n, v in vars(module).items()
                if callable(v) and n.lower().startswith("register")]


def test_p6_is_named_in_exactly_one_module_at_this_task():
    # The whole-package version of this is Task 25's. Here it is the two modules
    # that exist: authorship names P6, states names nobody.
    import facts.authorship as authorship
    import facts.states as states
    assert authorship.SUBSYSTEM == "P6"
    assert not hasattr(states, "SUBSYSTEM")


def test_event_defaults_fill_in_8_2s_authorship_fields():
    fields = event_defaults(event_type="fact creation", file_id="f1",
                            content_hash="sha256:abc", explanation='{"field": "subject"}')
    assert fields["subsystem"] == SUBSYSTEM
    assert fields["component_version"] == COMPONENT_VERSION
    assert fields["event_type"] == "fact creation"
    assert fields["file_id"] == "f1"
    assert fields["observed_at"]


def test_a_caller_supplied_observed_at_wins_so_a_replay_can_pin_the_clock():
    # §8.5 replays a run and compares it against a prior result; two readings of the
    # wall clock would be a false diff.
    fields = event_defaults(event_type="fact rejection", explanation="{}",
                            observed_at="2026-08-19T14:03:22+00:00")
    assert fields["observed_at"] == "2026-08-19T14:03:22+00:00"


def test_event_defaults_refuse_an_event_type_p6_does_not_author():
    # P3 authors `hashing` and `stat observation`; P5 authors `extraction` and `OCR`;
    # P12 authors the move events. P6 authors exactly two.
    for foreign in ("hashing", "extraction", "OCR", "planned move", "fact_creation"):
        with pytest.raises(ValueError):
            event_defaults(event_type=foreign, explanation="{}")


def test_event_defaults_refuse_to_name_another_subsystem():
    # M8: a `fact creation` event whose subsystem reads "P8" records that the model
    # harness wrote the fact table. P6 authors its facts; P8 proposes.
    with pytest.raises(ValueError):
        event_defaults(event_type="fact creation", subsystem="P8", explanation="{}")
    # Naming P6 explicitly is not an error — it is a no-op.
    assert event_defaults(event_type="fact creation", subsystem="P6",
                          explanation="{}")["subsystem"] == "P6"


def test_what_event_defaults_produces_is_accepted_by_p1s_live_writer(conn):
    # The contract is only real if P1 takes it. `events.file_id` carries no foreign
    # key, so this needs no `files` row, no observation and no extractor.
    event_id = append_event(conn, **event_defaults(
        event_type="fact creation", file_id="f1", content_hash="sha256:abc",
        explanation='{"field_key": "subject", "evidence_refs": ["sha256:deadbeef"]}'))
    row = conn.execute("SELECT * FROM events WHERE event_id = ?", (event_id,)).fetchone()
    assert row["event_type"] == "fact creation"
    assert row["subsystem"] == "P6"
    assert row["component_version"] == COMPONENT_VERSION
    assert row["explanation"]
```

```python
# tests/p6/test_p6_states.py
"""§3.13's six reliability states, spelled once — by P4, and re-exported here."""
import importlib
import pkgutil

import dataclasses

import pytest

from evidence_shape.conformance import validate_observation
from evidence_shape.fixtures import by_number
from evidence_shape.vocabulary import (
    EXTRACTOR_RELIABILITY_STATES, RELIABILITY_STATES, NotInVocabulary,
)

from facts.states import EXCLUDED_STATE, STATES, STRENGTH_ORDER, is_stronger, strength


def test_states_is_p4s_tuple_and_not_a_copy_of_it():
    # Preamble rule 2: "The six literals are P4's, already published, and P6
    # re-spells none of them." Identity, not equality: a copy would drift.
    assert STATES is RELIABILITY_STATES
    assert STATES == ("user_confirmed", "direct", "validated", "llm_supported",
                      "possible", "rejected")


def test_the_3_13_prose_spellings_are_prose_and_are_not_members():
    # §3.13 writes "LLM-supported" and "user confirmed"; §3.5 writes "LLM-supported"
    # too. Those are English, not values. A value outside the six is a load error,
    # never a spelling to normalize.
    for prose in ("LLM-supported", "User-confirmed", "user confirmed", "Direct"):
        assert prose not in STATES


def test_no_module_in_facts_publishes_a_second_copy_of_the_six():
    # Preamble rule 2: "P6 publishes no second copy and no alias table." A producer
    # naming the one or two states it may write is not a copy; a module-level
    # collection whose members ARE the six is.
    import facts
    offenders = []
    for info in pkgutil.iter_modules(facts.__path__):
        module = importlib.import_module(f"facts.{info.name}")
        if module.__name__ == "facts.states":
            continue
        for name, value in vars(module).items():
            if not isinstance(value, (tuple, list, set, frozenset)):
                continue
            if all(isinstance(m, str) for m in value) and set(value) == set(STATES):
                offenders.append(f"{module.__name__}.{name}")
    assert offenders == []


def test_the_strength_order_is_3_13s_and_has_five_members():
    assert STRENGTH_ORDER == ("possible", "llm_supported", "validated", "direct",
                              "user_confirmed")
    assert strength("user_confirmed") > strength("direct") > strength("validated") \
        > strength("llm_supported") > strength("possible")
    assert set(STRENGTH_ORDER) < set(STATES)


def test_rejected_has_no_strength_because_3_13_makes_it_an_exclusion():
    # "A rejected fact is a proposal that the user or validator marked as incorrect."
    # A rejected fact that merely ranked below `possible` would be resurfaced by any
    # comparison that picks the strongest — §8.7's own failure mode.
    assert EXCLUDED_STATE == "rejected"
    assert EXCLUDED_STATE in STATES
    assert EXCLUDED_STATE not in STRENGTH_ORDER
    with pytest.raises(NotInVocabulary):
        strength("rejected")
    with pytest.raises(NotInVocabulary):
        is_stronger("direct", "rejected")


def test_a_string_that_is_not_a_state_at_all_raises_rather_than_scoring_zero():
    with pytest.raises(NotInVocabulary):
        strength("probable")
    with pytest.raises(NotInVocabulary):
        strength("")


def test_is_stronger_is_strict_and_total_over_the_five():
    assert is_stronger("direct", "possible")
    assert not is_stronger("possible", "direct")
    assert not is_stronger("direct", "direct")


def test_extractors_write_two_of_the_six_and_p6_owns_all_six(p6_conn):
    # Takes `p6_conn` so Task 1's step 4 proves the fixture builds — P1's schema plus
    # P4's three tables — before Task 2 extends it with P6's own.
    #
    # P4 conformance rule 3 / P4 D11: an *observation* may carry only `direct` or
    # `possible`. A *fact* may carry any of the six. The same tuple, two admissible
    # subsets, asserted from both sides — not a comment in a docstring.
    assert EXTRACTOR_RELIABILITY_STATES == ("direct", "possible")
    assert set(EXTRACTOR_RELIABILITY_STATES) < set(STATES)

    observation = by_number(1).observations[0]
    assert observation.reliability == "possible"
    assert validate_observation(observation) == observation

    # Verified live 2026-08-22: P4 raises NotInVocabulary here, not NonConforming.
    with pytest.raises(NotInVocabulary):
        validate_observation(dataclasses.replace(observation, reliability="validated"))

    # And the same word is a rank P6 can ask for.
    assert strength("validated") > strength("llm_supported")
```

```python
# tests/p6/conftest.py
"""P6's fixtures. P1's `tests/conftest.py` supplies `conn` and is not modified.

Nothing here may be imported across parts by name: under pytest's default prepend
import mode, with no `__init__.py` under `tests/`, every `conftest.py` is imported as
the top-level module `conftest` and the last one wins.
"""
from __future__ import annotations

import pytest

from database_agent.db import create_schema

from evidence_shape.schema import create_evidence_schema

#: §8.5 replays a run and compares it against a prior result, so any test that
#: compares two records must be comparing what the resolver produced and not two
#: readings of the wall clock.
FIXED_OBSERVED_AT = "2026-08-19T14:03:22+00:00"


@pytest.fixture()
def observed_at() -> str:
    return FIXED_OBSERVED_AT


@pytest.fixture()
def p6_conn(conn):
    """P1's database with P4's three tables added. Task 2 extends this fixture with
    P6's own tables and the `fields` catalogue; it is the same shape
    `tests/p4/conftest.py` builds as `p4_conn`."""
    create_schema(conn)
    create_evidence_schema(conn)
    return conn
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/p6/test_p6_authorship.py tests/p6/test_p6_states.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'facts'` — collection fails on both
files before any test runs, because `src/facts/` does not exist. (Verified 2026-08-22:
`ls src/facts` → `No such file or directory`.)

- [ ] **Step 3: Write the implementation**

```python
# src/facts/__init__.py
"""P6 — facts and facets (§3.1–§3.14).

Claims with their evidence attached: four tables (`fields`, `values`, `file_facts`,
`unresolved`) inside P1's single database, three producers writing one fact format
in §8.6's order, and an abstention that is a row rather than a silence.

No path, no destination, no folder and no group column anywhere (§3.14, §4.3).
"""
```

```python
# src/facts/authorship.py
"""P6 authors its two §8.2 events; P1 writes them (M8).

M8 (04-resolutions.md): "The acting part authors; P1 writes. P1 appends no event on
its own initiative." §8.2 requires "the responsible subsystem" on every event, and a
`fact creation` row whose subsystem named P1 or P8 would record that the storage
substrate, or the model harness, wrote the fact table.

Both names are already among §8.2's nineteen reserved types (introspected from
`database_agent.events.RESERVED_EVENT_TYPES`, 2026-08-22), so P6 registers nothing —
registration is a spec-level act (P1 Contract out §3, rule 4).

**Both names carry a space.** `fact_creation` raises `UnregisteredEventType` at run
time rather than at review. This is the same defect class as MINOR 2's `OCR`/`ocr`.

This module is the ONE place `subsystem = "P6"` is written (Task 25 asserts there is
no second). It holds no connection and writes nothing.
"""
from __future__ import annotations

from datetime import datetime, timezone

#: §8.2's "responsible subsystem" for every event this part appends.
SUBSYSTEM = "P6"

#: §8.2's "extractor or model version" field. P1's Done-means 7 requires it
#: populated and `append_event` rejects an empty one. P3's spelling, followed.
COMPONENT_VERSION = "P6/0.1.0"

#: The two reserved §8.2 types P6 authors, in §8.2's order. Spelled with a space,
#: because that is how §8.2 spells them and how P1's frozen table stores them.
AUTHORED_EVENT_TYPES: tuple[str, str] = ("fact creation", "fact rejection")


def event_defaults(**fields) -> dict:
    """Fill §8.2's authorship fields and return the row for P1's `append_event`.

    Writes nothing and holds no connection: P6 authors, and the caller still has to
    decide an event is due and hand it to P1. A caller-supplied `observed_at` wins,
    so §8.5's replay can pin the clock.
    """
    event_type = fields.get("event_type")
    if event_type not in AUTHORED_EVENT_TYPES:
        raise ValueError(
            f"P6 does not author {event_type!r}; it authors {AUTHORED_EVENT_TYPES}. "
            f"Note the space: `fact_creation` is not a registered §8.2 type."
        )
    if fields.get("subsystem", SUBSYSTEM) != SUBSYSTEM:
        raise ValueError(
            f"P6 events name P6 as the responsible subsystem, not "
            f"{fields['subsystem']!r} (M8)"
        )
    return {
        **fields,
        "subsystem": SUBSYSTEM,
        "component_version": COMPONENT_VERSION,
        "observed_at": fields.get(
            "observed_at", datetime.now(timezone.utc).isoformat()
        ),
    }
```

```python
# src/facts/states.py
"""§3.13's six reliability states — P4's tuple, re-exported, never re-spelled.

Preamble rule 2: "There is one `file_facts` table and one set of six reliability
states." §3.5 settles why: "A file fact is not inherently rule-based or LLM-based. It
is the common format into which both systems write their conclusions." The producer
is a column, not a schema.

`STATES` IS `evidence_shape.vocabulary.RELIABILITY_STATES` — the same object, not a
copy, so the two cannot drift. The §3.13 prose spellings ("LLM-supported", "user
confirmed") are English; a value outside the six is a load error, not a spelling to
normalize.

**Extractors write two of the six; P6 owns all six.** P4 conformance rule 3 (P4 D11)
rejects the other four on an *observation*; `file_facts` accepts all six on a *fact*.
That boundary is asserted from both sides in `tests/p6/test_p6_states.py`.

**`rejected` has no strength.** §3.13: "A rejected fact is a proposal that the user
or validator marked as incorrect." It is an exclusion, not the bottom of a ladder: a
rejected fact that merely ranked below `possible` would be resurfaced by any
comparison that picks the strongest candidate, which is the failure §8.7 names —
"Otherwise the system will repeatedly resurface the same attractive but incorrect
grouping." Asking for its strength raises.
"""
from __future__ import annotations

from evidence_shape.vocabulary import (
    RELIABILITY_STATES as STATES,
    NotInVocabulary,
    check,
)

#: §3.13's five ranked states, weakest first, so `strength` is an index and the order
#: is readable in one line. §3.13's own sentence order is strongest-first; the ladder
#: is written the other way round only so that a larger number means a stronger fact.
STRENGTH_ORDER: tuple[str, ...] = (
    "possible",
    "llm_supported",
    "validated",
    "direct",
    "user_confirmed",
)

#: The sixth state, named as excluded rather than left out silently.
EXCLUDED_STATE = "rejected"


def strength(state: str) -> int:
    """Where `state` sits on §3.13's ladder. Larger is stronger.

    Raises `NotInVocabulary` for `rejected` (an exclusion, not a rank) and for any
    string that is not one of the six.
    """
    check(state, STATES, name="reliability_state")
    if state == EXCLUDED_STATE:
        raise NotInVocabulary(
            f"{EXCLUDED_STATE!r} is §3.13's exclusion, not a rank: 'a proposal that "
            f"the user or validator marked as incorrect'. Compare membership, never "
            f"strength — a rejected fact that merely ranked below 'possible' would be "
            f"resurfaced by any comparison that picks the strongest candidate (§8.7)."
        )
    return STRENGTH_ORDER.index(state)


def is_stronger(a: str, b: str) -> bool:
    """Strictly stronger on §3.13's ladder. Both arguments must be ranked states."""
    return strength(a) > strength(b)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/p6/test_p6_authorship.py tests/p6/test_p6_states.py -v`
Expected: PASS — 9 passed in `test_p6_authorship.py`, 8 passed in `test_p6_states.py`, 17 total.

- [ ] **Step 5: Run the whole suite and confirm nothing else moved**

Run: `pytest tests/ -q`
Expected: PASS — the 1300 P1–P5 tests still pass, plus 17. `src/facts/` and `tests/p6/` are new
directories; `pyproject.toml` already carries `pythonpath = ["src"]` and `testpaths = ["tests"]`,
so `facts` is importable and `tests/p6/` is collected with no change to any file P6 does not own.

- [ ] **Step 6: Commit**

```bash
git add src/facts/__init__.py src/facts/authorship.py src/facts/states.py tests/p6/conftest.py tests/p6/test_p6_authorship.py tests/p6/test_p6_states.py
git commit -m "feat(P6): the two §8.2 fact events, spelled with a space; §3.13's six states re-exported from P4"
```

---

### Task 2: `fields` — the closed catalogue, and the field that cannot be created at runtime

**Files:**
- Create: `src/facts/vocabulary.py`
- Create: `src/facts/fields.py`
- Create: `src/facts/schema.py`
- Modify: `tests/p6/conftest.py`
- Test: `tests/p6/test_p6_fields.py`

> **The skeleton says "modify `src/facts/schema.py`". Nothing creates it earlier**, so Task 2
> creates it. Tasks 3, 4 and 5 then modify it, which is what the skeleton's later "modify" lines
> assume. `create_facts_schema(conn)` is the name three sibling task files already import
> (`PLAN-tasks-07-09.md`, `PLAN-tasks-14-15.md`), and it is honoured unchanged.

**Interfaces:**
- Consumes: `evidence_shape.vocabulary.check`, `evidence_shape.vocabulary.NotInVocabulary`; `database_agent.db.transaction`.
- Produces: `FIELD_SCOPES: tuple[str, ...]` (`universal`, `academic`, `college_applications`, `research`, `finance`, `photos`, `code`), `VALUE_KINDS: tuple[str, ...]`, `UNIVERSAL_FIELDS: tuple[str, ...]`, `ROLE_FIELDS: tuple[str, ...]`, `DOMAIN_FIELDS: Mapping[str, tuple[str, ...]]`, `FIELD_ROWS: tuple[FieldRow, ...]`, `FieldRow(field_key, display_name, scope, value_kind, normalizer_id, destination_eligible, multiplicity)`, `FIELDS_COLUMNS: tuple[str, ...]`, `create_fields(conn) -> None`, `get_field(conn, field_key) -> sqlite3.Row`, `fields_in_scope(conn, scope) -> list[sqlite3.Row]`, `FieldNotInCatalogue`; `facts.schema.create_facts_schema(conn) -> None`.

> **`ROLE_FIELDS` and `VALUE_KINDS` and `FIELDS_COLUMNS` are additions to the skeleton's
> `Produces:` line, not renames.** Nothing the skeleton names is renamed, dropped or re-signatured.
> `ROLE_FIELDS` exists because §3.8's mandatory-`FALSE` rule needs one home rather than four
> literals scattered across the tests that assert it; `VALUE_KINDS` because the `value_kind` column
> is checked through P4's `check` like every other closed vocabulary in this part; `FIELDS_COLUMNS`
> because the column set is asserted from `PRAGMA table_info` and the expected list has to live
> somewhere. No sibling task file binds any of the three.

**Done-means:** 2, and the negative half of 3.

---

#### What the catalogue contains, and how each row was decided

`FIELD_ROWS` is **37 rows**. Its content comes from `planning/domains/canonical_fields.json` — the
R1a canonical field catalogue, 37 keys, another agent's read-only output — with **two changes, each
forced by a ruling that postdates it**:

| | Change | Why |
|---|---|---|
| **−1** | `sensitivity_status` is **withheld** | NEEDS-JOSEPH **C5**, still open: *"Create no such row either way."* See the contradiction recorded below. |
| **+1** | `capture_date` is **added** | Done-means 2(b) and Done-means 5. §3.2: *"an EXIF field called DateTimeOriginal is raw metadata; capture date = 2026-07-17 is the file fact derived from it"*. `canonical_fields.json` does not carry it. |

37 − 1 + 1 = **37**. The two changes cancel in count and not in content; the test asserts the
membership, never the number alone.

**`planning/domains/` is a source to read, not a runtime dependency.** `src/facts/` imports nothing
from it, loads no JSON at import time, and does not read the file at run time. `FIELD_ROWS` is an
authored module-level table, typed out in full below. The skeleton's own table says why: the 574
domain entries are *"a menu someone may one day draw from, entry by entry, with a decision each
time"*, and their own gate currently reports 566 failures. `canonical_fields.json` is the small
grep-verified subset of that work — every one of its `00_cite` strings was re-checked against
`planning/00-database-agent-product-design.md` before this plan was written, and all fifteen
quotations used below returned exactly one match.

**The seven groups, and the design sentence each comes from.** Every one of the six sentences below
was grep-verified verbatim on 2026-08-22 (`grep -cF` → `1`).

| Scope | Design sentence | Keys |
|---|---|---|
| `universal` | §3.11: *"a small shared set of universal file facts, such as file type, creation date, language, duplicate family, version family, and sensitivity status"* | `file_type`, `creation_date`, `language`, `duplicate_family`, `version_family` — **and not** `sensitivity_status` (C5) |
| `universal` | §3.9: *"It may be supported more weakly by a tightly bounded download session"* | `download_session` — P6's one recorded addition (SPEC, *Table: `fields`*) |
| `academic` | §3.11: *"Academic files may use school, term, course, instructor, and work type"* | `school`, `term`, **`subject`**, `instructor`, `work_type` |
| `college_applications` | §3.11: *"College application files may use target university, application cycle, application document type, and purpose"* | `target_university`, `application_cycle`, `application_document_type`, `purpose` |
| `research` | §3.11: *"Research files may use project, stage, artifact type, lab, and venue"* | `project`, `stage`, `artifact_type`, `lab`, `venue` |
| `finance` | §3.11: *"Finance files may use institution, account type, tax year, and record type"* | `institution`, `account_type`, `tax_year`, `record_type` |
| `photos` | §3.11: *"Photos may use capture year, event, location, people, camera information, and media type"* | `capture_year`, `event`, `location`, `people`, `camera_information`, `media_type` — **plus `capture_date`** |
| `code` | §3.11: *"Code files may use project, repository, programming language, and artifact type"* | `repository`, `programming_language` declared here; `project` and `artifact_type` **referenced** from `research` |
| `universal` | §3.8: *"distinct facets, such as authored_by and target_school, or our_firm and client"* | `authored_by`, `target_school`, `our_firm`, `client` |

**Why `subject` and not `course`.** D6, ratified 2026-08-21: the stored academic key is `subject`,
every stored key is `snake_case`, and §3.11's word "course" is the design's prose for the same
field. §3.2's own sentence is *"the system can create facts such as subject = BUSIB 4300"*. A field
key is a join handle, and two spellings are two columns. The catalogue carries a `subject` row and
**no** `course` row; the test asserts both halves. **OQ4 is closed and Task 25's guard inverts.**

**Why `project` and `artifact_type` are one row each, referenced twice.** §3.11 names both under
Research and under Code. `field_key` is unique, so two rows would be two join handles for one
concept — the tie-break rule's exact failure (*"one stored key per concept"*). `canonical_fields.json`
records the same model: *"One global table: schemas REFERENCE these keys and declare no private
spellings."* So the `scope` **column** records where a key is *declared* — Research, the first §3.11
sentence that names it — while `DOMAIN_FIELDS["code"]` **references** it. The two published views
mean different things and the test says so out loud:

- `DOMAIN_FIELDS[scope]` — the §3.11 sentence, literal. `DOMAIN_FIELDS["code"]` has four keys.
- `fields_in_scope(conn, scope)` — the rows *declared* at that scope. `fields_in_scope(conn, "code")`
  has two.

Task 14's `active_field_allowlist` is the consumer that wants the first of these; nothing in this
plan consumes the second except a reviewer checking the catalogue.

**Where `capture_date` sits, and why it is a recorded choice rather than a quotation.** The design
gives it no scope: §3.11's universal list does not name it, and §3.11's Photos row names `capture
year`, not the date. `FIELD_SCOPES` is closed at seven, so the row must take one of them. It is
placed at **`photos`**, on the producer evidence: Done-means 5 ties it to an EXIF `DateTimeOriginal`
observation, which arrives only as `source_type="image"` from `image.metadata` (P5's seam, §2.6). A
universal field is one any file may carry; a file with no capture metadata can never carry this one.
The alternative — `universal` — was rejected because P6's own SPEC says *"Exactly one further
universal field is added here"* and that one is `download_session`. Placing it at `photos` makes the
Photos scope seven rows where §3.11 names six; the test asserts that count explicitly, with this
reason, so the deviation is visible rather than discovered.

`capture_date`, `capture_year` and `creation_date` are **three different fields** and the test
proves it. §3.2 separates the first two from the third by name; the brief's field-naming ruling
separates the first from the second (*"`capture_date` is the EXIF-derived fact … `capture_year` is
the Photos destination dimension"*). `capture_date` is `destination_eligible = FALSE` — the Photos
template's time dimension is the year.

**What is NOT here, and stays not here.** Career and recruiting, identity, medical and legal get
**no field rows**. §5's Career template words (*"company → role or recruiting cycle → document
type"*) name no `fields` row in this catalogue and the test asserts each is absent.

> **D1, narrowed by Joseph 2026-08-21 — what the test may and may not assert.** The clause *"and
> acquiring one fails the test"* is **struck**. The test asserts what the catalogue contains today;
> it does **not** assert that the contents can never change. S3's deferral stands on its own, and
> P6's suite is not where that resolution is held — otherwise a later, deliberate reversal of S3
> would arrive as a regression rather than as a decision. **Do not author career fields**: not here,
> not as domain-catalogue field rows. Career is owed before P10, which is where a destination
> dimension first needs one. Anyone adding one before then is reversing S3 and must say so.

**`document type` is never a key** (brief, field-naming rulings). It is the design's generic word —
twelve uses — for whichever specific field the active domain declares: `application_document_type`
for College applications, `artifact_type` for Research and Code. The test asserts `document_type`
and `document type` are both absent while those two are present.

**`jurisdiction` is a value, never a field name** (D4). The test asserts no key contains it.

---

#### Three contradictions this task hits, resolved in the open

**1. `sensitivity_status`: the SPEC's Done-means 2 and the brief's C5 disagree.**

- SPEC Done-means 2: *"All six universal fields … are present, and no field outside them."*
- Brief §7, NEEDS-JOSEPH **C5**: *"whether P6 keeps a `sensitivity_status` field row. P7's SPEC
  Contract-in says 'P6 must accept `sensitivity` as a first-class universal field'; D2 makes P7's
  record authoritative; round 1 found the field has no producer. **Create no such row either way.**"*
- Skeleton, Task 2 note on D2: *"Round 1 F-2 found it has no producer. Create no such row until asked."*

**Resolved for the brief, which is binding and later.** The catalogue carries **five** §3.11
universal keys, not six. Done-means 2's "all six" is therefore **not satisfied by this task**, and
that is deliberate: C5 is open, D2 makes P7's `ClassificationRecord` authoritative and
`files.sensitivity_state` its projection, and a field row with no producer would be a column
somebody later writes into from the wrong side. The test asserts the **absence** and names C5, so
the day Joseph answers, one row and one assertion change together. **Do not "fix" Done-means 2 by
adding the row.**

**2. `destination_eligible` for `target_school` and `client`: the skeleton and `canonical_fields.json`
disagree.**

- Skeleton, Task 2: *"every one of the four is `destination_eligible = FALSE`"*, quoting §3.8's
  *"It should avoid using authorship or creator identity as a destination dimension"*.
- `canonical_fields.json` marks `target_school` **true** and `client` **true**, reasoning that the
  §3.8 sentence binds the authorship side only and that §3.8 *"places a document's purpose, project,
  subject, or target above its authorship"*.

**Resolved for the skeleton**, which outranks `planning/domains/` in the brief's precedence order
(§3: design → SPEC → skeleton; `planning/domains/` is a *source to read*). All four are `FALSE`.
The reading costs nothing today and is the reversible direction: `target_school` is held as a key
**unreferenced by any domain**, pending the ROSTER NEEDS-JOSEPH that may fold it into
`target_university` (which **is** `destination_eligible = TRUE`, as §3.11's College-applications row
requires); and `client` is referenced by no §3.11 domain either, because the business schemas are
deferred. Widening a field to destination-eligible later is a decision; narrowing one after a tree
has been built from it is a migration. The disagreement is recorded here rather than silently
picked.

**3. `value_kind` cannot carry the SPEC's "date/term" obligation.** The SPEC's column comment is
*"how this field's values normalize; date/term fields must use §3.10 rules"*, but
`canonical_fields.json` types `term` as `string`, not as a term kind. Rather than invent a fifth
`value_kind` member, `VALUE_KINDS` is exactly the four kinds that file uses — `string`, `date`,
`identifier`, `enum` — and the §3.10 obligation stays where it is enforceable: Task 10's `dates.py`,
keyed on the field, with its three required injected patterns. The gap is named, not closed here.

**`normalizer_id` and `multiplicity` are `NULL` on every row, and that is the answer.**
Per-field normalizers are a **Deferred** row in the SPEC (*"`U Chicago` → `University of Chicago` →
`UChicago` is one worked example, not a table"*), and round 4's C-5 has P8's Contract-in naming
`normalize(field, raw_value)` as P6's while P6 Task 17 disowns it — each part hands it to the other,
so neither builds it. **OQ6** (multiplicity) is Joseph's: *"May one (file, field) hold several
simultaneously active values, and if so how does the §3.7 margin rule apply?"* Both columns exist so
a later answer has somewhere to land; both are unanswered, and the test asserts they are unanswered
rather than asserting a guess.

**A trap for Task 4's author, stated here because this is where the column is born.** Task 4's
`FORBIDDEN_COLUMN_SUBSTRINGS` check must **not** be run against `fields`: the column
`destination_eligible` contains the substring `destination`. §3.14's negative contract is about the
**fact** row carrying no path, destination, folder or group — not about the catalogue declaring
which fields may ever become a folder level. Applying the same guard to both tables would fail on a
column §3.8 requires.

---

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_fields.py
"""§3.12's closed catalogue: the LLM may create values, never fields.

Done-means 2 and the negative half of Done-means 3.
"""
import re

import pytest

from evidence_shape.vocabulary import NotInVocabulary

from facts.fields import (
    DOMAIN_FIELDS, FIELDS_COLUMNS, FIELD_ROWS, FIELD_SCOPES, ROLE_FIELDS,
    UNIVERSAL_FIELDS, VALUE_KINDS, FieldNotInCatalogue, create_fields,
    fields_in_scope, get_field,
)

KEYS = tuple(row.field_key for row in FIELD_ROWS)


def test_the_catalogue_is_thirty_seven_rows_with_no_duplicate_key():
    assert len(FIELD_ROWS) == 37
    assert len(set(KEYS)) == 37


def test_the_catalogue_is_exactly_these_keys_and_nothing_else():
    # §3.11's six sentences + §3.9's download session + §3.8's four roles +
    # capture_date (Done-means 2(b)), minus sensitivity_status (NEEDS-JOSEPH C5).
    assert set(KEYS) == {
        # universal (§3.11, five of six — see C5 below)
        "file_type", "creation_date", "language", "duplicate_family", "version_family",
        # universal (§3.9, P6's one recorded addition)
        "download_session",
        # academic (§3.11)
        "school", "term", "subject", "instructor", "work_type",
        # college applications (§3.11)
        "target_university", "application_cycle", "application_document_type", "purpose",
        # research (§3.11)
        "project", "stage", "artifact_type", "lab", "venue",
        # finance (§3.11)
        "institution", "account_type", "tax_year", "record_type",
        # photos (§3.11), plus §3.2's capture_date
        "capture_year", "event", "location", "people", "camera_information",
        "media_type", "capture_date",
        # code (§3.11) — project and artifact_type are declared under research
        "repository", "programming_language",
        # §3.8's four role fields
        "authored_by", "target_school", "our_firm", "client",
    }


def test_the_three_published_groups_partition_the_catalogue():
    referenced = {key for keys in DOMAIN_FIELDS.values() for key in keys}
    assert set(UNIVERSAL_FIELDS) | set(ROLE_FIELDS) | referenced == set(KEYS)
    assert not set(UNIVERSAL_FIELDS) & set(ROLE_FIELDS)


def test_every_key_is_snake_case():
    # D6: "every stored field key is snake_case".
    for key in KEYS:
        assert re.fullmatch(r"[a-z][a-z0-9_]*", key), key


def test_the_academic_key_is_subject_and_there_is_no_course_row():
    # D6, ratified 2026-08-21. §3.2: "the system can create facts such as
    # subject = BUSIB 4300". §3.11's word "course" is prose for the same field and
    # survives inside quotations only. Two spellings would be two join handles.
    assert "subject" in KEYS
    assert "course" not in KEYS
    assert "course_code" not in KEYS
    assert DOMAIN_FIELDS["academic"] == ("school", "term", "subject", "instructor",
                                         "work_type")
    assert all(row.display_name != "course" for row in FIELD_ROWS)


def test_sensitivity_status_has_no_row_because_C5_is_open():
    # NEEDS-JOSEPH C5. P7's SPEC Contract-in wants `sensitivity` as a first-class
    # universal field; D2 makes P7's ClassificationRecord authoritative and
    # `files.sensitivity_state` its projection; round 1 F-2 found the field has no
    # producer. The brief: "Create no such row either way."
    #
    # This is knowingly at odds with SPEC Done-means 2 ("all six universal fields").
    # Do not close it by adding the row.
    for spelling in ("sensitivity_status", "sensitivity", "sensitivity_state"):
        assert spelling not in KEYS
    assert len([k for k in UNIVERSAL_FIELDS if k != "download_session"]) == 5


def test_document_type_is_never_a_key():
    # The design's generic word (twelve uses) for whichever field the active domain
    # declares. The specific ones are keys; the generic one is not.
    assert "document_type" not in KEYS
    assert "document type" not in KEYS
    assert "application_document_type" in KEYS
    assert "artifact_type" in KEYS


def test_jurisdiction_is_a_value_and_never_a_field_name():
    # D4: "jurisdiction is a value, never a field name and never a destination
    # dimension."
    assert not [k for k in KEYS if "jurisdiction" in k]


def test_career_identity_medical_and_legal_have_no_field_rows():
    # §5's Career template words are "company → role or recruiting cycle → document
    # type"; none of them is a `fields` row. S3 deferred those schemas.
    #
    # D1 (narrowed 2026-08-21): this asserts the catalogue's contents today. It does
    # NOT assert that the contents can never change — a later deliberate reversal of
    # S3 is a decision, not a regression, and P6's suite is not where it is held.
    for absent in ("company", "role", "recruiting_cycle", "job_title", "employer",
                   "resume_version", "passport_number", "identity_document_type",
                   "patient", "diagnosis", "medical_record_type",
                   "matter", "case_number", "counterparty"):
        assert absent not in KEYS


def test_the_four_3_8_role_fields_exist_and_none_is_destination_eligible():
    # §3.8: "distinct facets, such as authored_by and target_school, or our_firm and
    # client" — the design's own spelling, underscores included.
    #
    # Round 1's F-1: Done-means 13 and 22 both require `authored_by` to exist, so a
    # catalogue without these four made two of the SPEC's own Done-means unwritable.
    assert ROLE_FIELDS == ("authored_by", "target_school", "our_firm", "client")
    for key in ROLE_FIELDS:
        row = next(r for r in FIELD_ROWS if r.field_key == key)
        assert row.destination_eligible is False, key
        assert row.scope == "universal", key
    # §3.8: "It should avoid using authorship or creator identity as a destination
    # dimension." Recorded disagreement: canonical_fields.json marks target_school
    # and client eligible; the skeleton says all four are FALSE and outranks it.


def test_the_application_target_is_destination_eligible_under_its_3_11_spelling():
    # §3.11's College-applications row names "target university" as a dimension, so
    # target_university IS eligible. target_school is §3.8's spelling of the same
    # concept, held as a key referenced by no domain until the ROSTER NEEDS-JOSEPH
    # about folding the two is answered.
    assert get_row("target_university").destination_eligible is True
    assert "target_school" not in DOMAIN_FIELDS["college_applications"]


def test_capture_date_capture_year_and_creation_date_are_three_fields():
    # Brief, field-naming rulings: capture_date is §3.2's EXIF-derived fact
    # ("capture date = 2026-07-17 is the file fact derived from it"); capture_year is
    # §3.11's Photos destination dimension; creation_date is what §3.2 separates both
    # from by name.
    assert {"capture_date", "capture_year", "creation_date"} <= set(KEYS)
    assert get_row("capture_date").value_kind == "date"
    assert get_row("capture_date").destination_eligible is False
    assert get_row("capture_year").destination_eligible is True
    assert get_row("creation_date").scope == "universal"
    assert get_row("capture_date").scope == "photos"


def test_the_photos_scope_carries_seven_rows_and_the_reason_is_recorded():
    # §3.11 names six. capture_date is the seventh: the design gives it no scope,
    # FIELD_SCOPES is closed at seven members, and its only producer is an EXIF
    # DateTimeOriginal observation (Done-means 5), which arrives only for an image.
    assert DOMAIN_FIELDS["photos"] == ("capture_year", "event", "location", "people",
                                       "camera_information", "media_type",
                                       "capture_date")


def test_download_session_is_universal_and_never_a_folder_level():
    # §3.9: "It may be supported more weakly by a tightly bounded download session."
    # A session is a purpose clue and a review aid, never proof of topic.
    row = get_row("download_session")
    assert row.scope == "universal"
    assert row.destination_eligible is False
    assert "download_session" in UNIVERSAL_FIELDS


def test_the_seven_scopes_are_the_specs_seven_and_every_row_uses_one():
    assert FIELD_SCOPES == ("universal", "academic", "college_applications",
                            "research", "finance", "photos", "code")
    for row in FIELD_ROWS:
        assert row.scope in FIELD_SCOPES, row.field_key
        assert row.value_kind in VALUE_KINDS, row.field_key


def test_project_and_artifact_type_are_one_row_each_referenced_by_two_domains():
    # canonical_fields.json's own model: "One global table: schemas REFERENCE these
    # keys and declare no private spellings." Two rows would be two join handles for
    # one concept — the tie-break rule's exact failure.
    assert DOMAIN_FIELDS["research"] == ("project", "stage", "artifact_type", "lab",
                                         "venue")
    assert DOMAIN_FIELDS["code"] == ("project", "repository", "programming_language",
                                     "artifact_type")
    assert get_row("project").scope == "research"
    assert get_row("artifact_type").scope == "research"
    assert len([r for r in FIELD_ROWS if r.field_key == "project"]) == 1


def test_no_normalizer_and_no_multiplicity_is_answered_anywhere():
    # Per-field normalizers are a Deferred SPEC row, and round 4's C-5 has P6 and P8
    # each handing `normalize(field, raw_value)` to the other. OQ6 (multiplicity) is
    # Joseph's. Both columns exist so an answer has somewhere to land.
    assert all(row.normalizer_id is None for row in FIELD_ROWS)
    assert all(row.multiplicity is None for row in FIELD_ROWS)


def test_the_module_publishes_no_way_to_add_a_field_at_runtime(p6_conn):
    # §3.12: "The system may create new values when it sees a new course, project,
    # company, university, or event, but it should not invent new fields
    # automatically." §3.5: "The LLM is not allowed to invent a new fact schema,
    # create an unsupported field, or make a free-form filing decision."
    #
    # Runtime introspection of the module namespace, not a source-text search: a text
    # search matches comments and docstrings.
    import facts.fields as module
    forbidden = ("add_field", "create_field", "register_field", "new_field",
                 "ensure_field", "upsert_field")
    assert not [n for n in vars(module) if n in forbidden]
    assert not [n for n, v in vars(module).items()
                if callable(v) and n.lower().endswith("_field")
                and n not in ("get_field",)]


def test_an_unknown_field_key_raises_rather_than_creating_a_row(p6_conn):
    before = p6_conn.execute("SELECT count(*) FROM fields").fetchone()[0]
    with pytest.raises(FieldNotInCatalogue):
        get_field(p6_conn, "vibe")
    with pytest.raises(FieldNotInCatalogue):
        get_field(p6_conn, "course")          # D6: prose, not a key
    with pytest.raises(FieldNotInCatalogue):
        get_field(p6_conn, "sensitivity_status")   # C5: open, so no row
    assert p6_conn.execute("SELECT count(*) FROM fields").fetchone()[0] == before


def test_create_fields_loads_the_authored_table_and_is_idempotent(p6_conn):
    # `p6_conn` has already called it once.
    assert p6_conn.execute("SELECT count(*) FROM fields").fetchone()[0] == 37
    create_fields(p6_conn)
    create_fields(p6_conn)
    assert p6_conn.execute("SELECT count(*) FROM fields").fetchone()[0] == 37


def test_the_stored_row_carries_exactly_the_specs_columns(p6_conn):
    # Read from the database, so a future column fails the test the day it is added.
    # NOTE for Task 4: `destination_eligible` contains the substring "destination".
    # §3.14's forbidden-substring guard is for `file_facts` and `unresolved`; running
    # it against `fields` would fail on a column §3.8 requires.
    stored = tuple(r[1] for r in p6_conn.execute("PRAGMA table_info(fields)"))
    assert stored == FIELDS_COLUMNS
    assert FIELDS_COLUMNS == ("field_id", "field_key", "display_name", "scope",
                              "value_kind", "normalizer_id", "destination_eligible",
                              "multiplicity")


def test_the_row_identity_is_the_field_key_under_both_names(p6_conn):
    # SPEC: "field_key — stable identifier". Task 3's `values.field_id` joins on it.
    # One identity, two names — never two identities.
    row = get_field(p6_conn, "subject")
    assert row["field_id"] == row["field_key"] == "subject"
    assert row["display_name"] == "subject"
    assert row["scope"] == "academic"
    assert row["value_kind"] == "string"
    assert row["normalizer_id"] is None
    assert row["multiplicity"] is None
    assert row["destination_eligible"] == 1


def test_fields_in_scope_returns_the_rows_declared_at_that_scope(p6_conn):
    # `fields_in_scope` answers "declared here"; `DOMAIN_FIELDS` answers "referenced
    # by this §3.11 sentence". They differ for exactly the two shared keys.
    assert [r["field_key"] for r in fields_in_scope(p6_conn, "code")] == [
        "repository", "programming_language"]
    assert [r["field_key"] for r in fields_in_scope(p6_conn, "finance")] == [
        "institution", "account_type", "tax_year", "record_type"]
    assert [r["field_key"] for r in fields_in_scope(p6_conn, "universal")] == [
        "file_type", "creation_date", "language", "duplicate_family",
        "version_family", "download_session",
        "authored_by", "target_school", "our_firm", "client"]
    assert len(fields_in_scope(p6_conn, "photos")) == 7


def test_fields_in_scope_refuses_a_scope_outside_the_seven(p6_conn):
    for absent in ("career", "identity", "medical", "legal", "Universal"):
        with pytest.raises(NotInVocabulary):
            fields_in_scope(p6_conn, absent)


def test_every_destination_eligible_flag_round_trips_as_a_boolean(p6_conn):
    for row in FIELD_ROWS:
        stored = get_field(p6_conn, row.field_key)
        assert bool(stored["destination_eligible"]) is row.destination_eligible


def get_row(field_key):
    return next(r for r in FIELD_ROWS if r.field_key == field_key)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/p6/test_p6_fields.py -v`
Expected: FAIL — collection fails with
`ModuleNotFoundError: No module named 'facts.fields'`. (`src/facts/` exists after Task 1; `fields.py`
does not.)

- [ ] **Step 3: Write the implementation**

```python
# src/facts/vocabulary.py
"""P6's own closed vocabularies, published once, checked through P4's `check`.

Global constraint: "`unresolved` reasons and `origin` values are P6's own closed
vocabularies, published once, in one module, checked with P4's
`evidence_shape.vocabulary.check(value, vocabulary, *, name)` so a bad value raises
`NotInVocabulary` rather than being stored."

The six reliability states are NOT here — they are P4's, re-exported by
`facts.states`, and a second copy is what preamble rule 2 forbids.

Task 5 adds `UNRESOLVED_REASONS` and `ATTEMPTED_PRODUCERS` to this module.
"""
from __future__ import annotations

#: §3.11's six domain families plus the universal scope. Exactly the SPEC's list, in
#: the SPEC's order. Adding a member is a contract revision: §3.15 names Career and
#: recruiting, identity, medical and legal, and §3.11 gives them no field row, so
#: they are Deferred rather than empty scopes (S3).
FIELD_SCOPES: tuple[str, ...] = (
    "universal",
    "academic",
    "college_applications",
    "research",
    "finance",
    "photos",
    "code",
)

#: How a field's values normalize (SPEC, `fields` table). Exactly the four kinds
#: `planning/domains/canonical_fields.json` uses; P6 invents no fifth.
#:
#: The SPEC's column comment adds "date/term fields must use §3.10 rules", but that
#: file types `term` as `string`. Rather than mint a `term` kind the design does not
#: name, the §3.10 obligation stays in `facts.dates`, keyed on the field, with its
#: injected patterns. The gap is named in the plan, not closed here.
VALUE_KINDS: tuple[str, ...] = ("string", "date", "identifier", "enum")
```

```python
# src/facts/schema.py
"""P6's tables, created inside P1's single local database (§0).

P6 owns four — `fields`, `values`, `file_facts`, `unresolved` — and creates none of
anyone else's. `database_agent.db.create_schema` and
`evidence_shape.schema.create_evidence_schema` are separate calls and are never
invoked from here.

Task 2 creates `fields`. Tasks 3, 4 and 5 add their own DDL to `_TABLE_DDL`.
"""
from __future__ import annotations

import sqlite3

from database_agent.db import transaction

#: The `fields` catalogue (SPEC, Table: `fields`). `field_id` and `field_key` hold
#: the same string: the SPEC calls `field_key` the "stable identifier", and Task 3's
#: `values.field_id` joins on it. One identity under the two names the two tables
#: use — never two identities.
#:
#: `destination_eligible` is INTEGER because SQLite has no boolean; `create_fields`
#: writes 0/1 and the reader coerces with `bool()`.
#:
#: `normalizer_id` and `multiplicity` are nullable and NULL on every authored row:
#: per-field normalizers are a Deferred SPEC row, and multiplicity is open question 6.
_FIELDS_DDL = """
CREATE TABLE IF NOT EXISTS fields (
    field_id             TEXT PRIMARY KEY,
    field_key            TEXT NOT NULL UNIQUE,
    display_name         TEXT NOT NULL,
    scope                TEXT NOT NULL,
    value_kind           TEXT NOT NULL,
    normalizer_id        TEXT,
    destination_eligible INTEGER NOT NULL,
    multiplicity         TEXT
)
"""

_TABLE_DDL: tuple[str, ...] = (_FIELDS_DDL,)


def create_facts_schema(conn: sqlite3.Connection) -> None:
    """Create P6's tables. Idempotent; creates no other part's table."""
    with transaction(conn):
        for ddl in _TABLE_DDL:
            conn.execute(ddl)
```

```python
# src/facts/fields.py
"""§3.12's closed field catalogue: values may auto-create, fields may not.

§3.12: "The system may create new values when it sees a new course, project, company,
university, or event, but it should not invent new fields automatically."
§3.5: "The LLM is not allowed to invent a new fact schema, create an unsupported
field, or make a free-form filing decision."

So the write path is this module-level authored table, loaded by `create_fields`.
There is no `add_field`, no `register_field`, and no path on which a producer — rules,
the LLM seam, or a user correction — inserts a `fields` row. `get_field` raises
`FieldNotInCatalogue` for an unknown key, which is what makes an unknown field a
refusal rather than a schema change.

**`planning/domains/` is not this catalogue and is never imported.** That directory is
a research artifact of 574 proposed entries. This table's content was READ from
`planning/domains/canonical_fields.json` (37 grep-verified canonical keys) when the
plan was written, with two changes forced by later rulings: `sensitivity_status` is
withheld (NEEDS-JOSEPH C5, open) and `capture_date` is added (Done-means 2(b), §3.2).
Nothing here loads a file at import time or at run time.

**The scope column records where a key is DECLARED; `DOMAIN_FIELDS` records which
§3.11 sentence REFERENCES it.** §3.11 names `project` and `artifact type` under both
Research and Code, and one concept gets one stored key (the tie-break rule), so those
two are declared at `research` and referenced by `code`.

**Every field a §3.8 role names is `destination_eligible = False`.** §3.8: "It should
avoid using authorship or creator identity as a destination dimension."
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from evidence_shape.vocabulary import check

from database_agent.db import transaction

from facts.schema import create_facts_schema
from facts.vocabulary import FIELD_SCOPES, VALUE_KINDS

__all__ = [
    "DOMAIN_FIELDS", "FIELDS_COLUMNS", "FIELD_ROWS", "FIELD_SCOPES", "ROLE_FIELDS",
    "UNIVERSAL_FIELDS", "VALUE_KINDS", "FieldNotInCatalogue", "FieldRow",
    "create_fields", "fields_in_scope", "get_field",
]


class FieldNotInCatalogue(KeyError):
    """A producer named a field §3.12 does not let it create.

    Raised instead of inserting a row: "it should not invent new fields
    automatically" is enforced by there being no code that could.
    """


@dataclass(frozen=True, slots=True)
class FieldRow:
    """One row of the catalogue, in the SPEC's column order."""

    field_key: str
    display_name: str
    scope: str
    value_kind: str
    normalizer_id: str | None
    destination_eligible: bool
    multiplicity: str | None


#: The stored columns, asserted against `PRAGMA table_info(fields)`.
FIELDS_COLUMNS: tuple[str, ...] = (
    "field_id", "field_key", "display_name", "scope", "value_kind",
    "normalizer_id", "destination_eligible", "multiplicity",
)


def _row(field_key: str, display_name: str, scope: str, value_kind: str,
         destination_eligible: bool) -> FieldRow:
    """One catalogue row. `normalizer_id` and `multiplicity` are NULL on every row:
    per-field normalizers are Deferred and multiplicity is open question 6."""
    return FieldRow(field_key=field_key, display_name=display_name, scope=scope,
                    value_kind=value_kind, normalizer_id=None,
                    destination_eligible=destination_eligible, multiplicity=None)


#: §3.11: "a small shared set of universal file facts, such as file type, creation
#: date, language, duplicate family, version family, and sensitivity status".
#:
#: FIVE of that six are here. `sensitivity_status` is WITHHELD: NEEDS-JOSEPH C5 is
#: open (P7's SPEC wants it first-class; D2 makes P7's ClassificationRecord
#: authoritative and `files.sensitivity_state` its projection; round 1 F-2 found the
#: field has no producer), and the instruction is to create no such row either way.
#: This is knowingly at odds with SPEC Done-means 2's "all six"; do not close it by
#: adding the row.
_UNIVERSAL_3_11: tuple[FieldRow, ...] = (
    _row("file_type", "file type", "universal", "string", False),
    _row("creation_date", "creation date", "universal", "date", False),
    _row("language", "language", "universal", "string", False),
    _row("duplicate_family", "duplicate family", "universal", "identifier", False),
    _row("version_family", "version family", "universal", "identifier", False),
)

#: P6's one recorded addition to the universal list. §3.9: "It may be supported more
#: weakly by a tightly bounded download session." §4.2 requires it retrievable. It is
#: not `purpose` — the session names no purpose value — and it is never a folder
#: level, because a session is a clue and a review aid, not proof of topic.
_DOWNLOAD_SESSION: tuple[FieldRow, ...] = (
    _row("download_session", "download session", "universal", "identifier", False),
)

#: §3.8: "distinct facets, such as authored_by and target_school, or our_firm and
#: client" — the design's own spelling, underscores included, so `display_name` keeps
#: it rather than inventing English the design does not use.
#:
#: All four are `destination_eligible = False`: §3.8, "It should avoid using
#: authorship or creator identity as a destination dimension." Recorded disagreement:
#: `canonical_fields.json` marks `target_school` and `client` eligible on the reading
#: that the sentence binds the authorship side only. The skeleton says all four are
#: FALSE and outranks that file; it costs nothing today, because no §3.11 domain
#: references either key, and it is the reversible direction.
#:
#: They take `scope = "universal"`: no §3.11 domain sentence names any of them, and
#: FIELD_SCOPES has no eighth member to hold them. `authored_by` in particular is
#: produced from document metadata on any file, in any domain (§3.8's demotion tier).
_ROLES_3_8: tuple[FieldRow, ...] = (
    _row("authored_by", "authored_by", "universal", "string", False),
    _row("target_school", "target_school", "universal", "string", False),
    _row("our_firm", "our_firm", "universal", "string", False),
    _row("client", "client", "universal", "string", False),
)

#: §3.11: "Academic files may use school, term, course, instructor, and work type."
#: D6: the stored key is `subject`; "course" is the design's prose for the same field
#: and survives inside quotations only. §3.2: "the system can create facts such as
#: subject = BUSIB 4300."
#:
#: `instructor` is not destination-eligible: §3.11's Academic template is school →
#: term → course → work type, and §3.8 disfavours person-identity collectors.
_ACADEMIC: tuple[FieldRow, ...] = (
    _row("school", "school", "academic", "string", True),
    _row("term", "term", "academic", "string", True),
    _row("subject", "subject", "academic", "string", True),
    _row("instructor", "instructor", "academic", "string", False),
    _row("work_type", "work type", "academic", "enum", True),
)

#: §3.11: "College application files may use target university, application cycle,
#: application document type, and purpose."
#:
#: `purpose` stays exactly where that sentence puts it. No per-domain `purpose` clone
#: is minted; a purpose-coherent packet outside admissions activates the nearest
#: schema on its own evidence or falls through to residual.
_COLLEGE_APPLICATIONS: tuple[FieldRow, ...] = (
    _row("target_university", "target university", "college_applications", "string", True),
    _row("application_cycle", "application cycle", "college_applications", "string", True),
    _row("application_document_type", "application document type",
         "college_applications", "enum", True),
    _row("purpose", "purpose", "college_applications", "string", True),
)

#: §3.11: "Research files may use project, stage, artifact type, lab, and venue."
#: `project` and `artifact_type` are DECLARED here and REFERENCED by `code`.
_RESEARCH: tuple[FieldRow, ...] = (
    _row("project", "project", "research", "string", True),
    _row("stage", "stage", "research", "string", True),
    _row("artifact_type", "artifact type", "research", "enum", True),
    _row("lab", "lab", "research", "string", True),
    _row("venue", "venue", "research", "string", True),
)

#: §3.11: "Finance files may use institution, account type, tax year, and record type."
_FINANCE: tuple[FieldRow, ...] = (
    _row("institution", "institution", "finance", "string", True),
    _row("account_type", "account type", "finance", "string", True),
    _row("tax_year", "tax year", "finance", "string", True),
    _row("record_type", "record type", "finance", "enum", True),
)

#: §3.11: "Photos may use capture year, event, location, people, camera information,
#: and media type."
#:
#: Plus `capture_date`, which the design gives no scope. §3.2: "an EXIF field called
#: DateTimeOriginal is raw metadata; capture date = 2026-07-17 is the file fact
#: derived from it." Its only producer is an image-metadata observation, so it is
#: declared here rather than as an eighth universal field; the Photos template's time
#: dimension is `capture_year`, so the date itself is not destination-eligible.
#:
#: `people` and `camera_information` are not destination-eligible: §3.11's Photos
#: template is year → event, and person-folders are privacy-loaded (§8.4). Widening
#: either is Joseph's call, never a schema's.
_PHOTOS: tuple[FieldRow, ...] = (
    _row("capture_year", "capture year", "photos", "string", True),
    _row("event", "event", "photos", "string", True),
    _row("location", "location", "photos", "string", True),
    _row("people", "people", "photos", "string", False),
    _row("camera_information", "camera information", "photos", "string", False),
    _row("media_type", "media type", "photos", "enum", True),
    _row("capture_date", "capture date", "photos", "date", False),
)

#: §3.11: "Code files may use project, repository, programming language, and artifact
#: type." `project` and `artifact_type` are declared under Research.
#:
#: `programming_language` is not destination-eligible: the design treats code projects
#: as structural units whose existing layout is preserved, and scattering a project by
#: language would break that.
_CODE: tuple[FieldRow, ...] = (
    _row("repository", "repository", "code", "string", True),
    _row("programming_language", "programming language", "code", "string", False),
)

#: The catalogue, in declaration order. Thirty-seven rows.
FIELD_ROWS: tuple[FieldRow, ...] = (
    *_UNIVERSAL_3_11,
    *_DOWNLOAD_SESSION,
    *_ROLES_3_8,
    *_ACADEMIC,
    *_COLLEGE_APPLICATIONS,
    *_RESEARCH,
    *_FINANCE,
    *_PHOTOS,
    *_CODE,
)

#: §3.11's universal list (five of six, C5) plus §3.9's download session.
UNIVERSAL_FIELDS: tuple[str, ...] = tuple(
    row.field_key for row in (*_UNIVERSAL_3_11, *_DOWNLOAD_SESSION)
)

#: §3.8's four role fields.
ROLE_FIELDS: tuple[str, ...] = tuple(row.field_key for row in _ROLES_3_8)

#: §3.11's six domain sentences, literal — the keys each REFERENCES, which is not the
#: same question as which scope declares them. `project` and `artifact_type` appear
#: under two domains and are one row each.
DOMAIN_FIELDS: Mapping[str, tuple[str, ...]] = MappingProxyType({
    "academic": tuple(row.field_key for row in _ACADEMIC),
    "college_applications": tuple(row.field_key for row in _COLLEGE_APPLICATIONS),
    "research": tuple(row.field_key for row in _RESEARCH),
    "finance": tuple(row.field_key for row in _FINANCE),
    "photos": tuple(row.field_key for row in _PHOTOS),
    "code": ("project", "repository", "programming_language", "artifact_type"),
})


def create_fields(conn: sqlite3.Connection) -> None:
    """Load the authored catalogue. Idempotent, and the only writer of this table.

    There is deliberately no counterpart that adds a row (§3.12, §3.5). A drifted
    row raises `NotInVocabulary` through P4's `check` rather than being stored.
    """
    create_facts_schema(conn)
    with transaction(conn):
        for row in FIELD_ROWS:
            check(row.scope, FIELD_SCOPES, name="field scope")
            check(row.value_kind, VALUE_KINDS, name="value_kind")
            conn.execute(
                "INSERT OR IGNORE INTO fields (field_id, field_key, display_name, "
                "scope, value_kind, normalizer_id, destination_eligible, "
                "multiplicity) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (row.field_key, row.field_key, row.display_name, row.scope,
                 row.value_kind, row.normalizer_id,
                 1 if row.destination_eligible else 0, row.multiplicity),
            )


def get_field(conn: sqlite3.Connection, field_key: str) -> sqlite3.Row:
    """The catalogue row for `field_key`.

    Raises `FieldNotInCatalogue` for anything else — including `course` (D6: prose,
    not a key) and `sensitivity_status` (NEEDS-JOSEPH C5: no row until asked).
    """
    row = conn.execute(
        "SELECT * FROM fields WHERE field_key = ?", (field_key,)
    ).fetchone()
    if row is None:
        raise FieldNotInCatalogue(
            f"{field_key!r} is not in the field catalogue. §3.12: the system 'should "
            f"not invent new fields automatically'; §3.5: the LLM may not 'create an "
            f"unsupported field'. Adding one is a design decision, not a write."
        )
    return row


def fields_in_scope(conn: sqlite3.Connection, scope: str) -> list[sqlite3.Row]:
    """The rows DECLARED at `scope`, in catalogue order.

    Not the same question as `DOMAIN_FIELDS[scope]`, which is the §3.11 sentence's
    own list: `project` and `artifact_type` are declared at `research` and referenced
    by `code`, so `fields_in_scope(conn, "code")` returns two rows where
    `DOMAIN_FIELDS["code"]` names four.
    """
    check(scope, FIELD_SCOPES, name="field scope")
    return list(conn.execute(
        "SELECT * FROM fields WHERE scope = ? ORDER BY rowid", (scope,)
    ))
```

```python
# tests/p6/conftest.py   — MODIFY: extend `p6_conn` with P6's tables and catalogue
"""P6's fixtures. P1's `tests/conftest.py` supplies `conn` and is not modified.

Nothing here may be imported across parts by name: under pytest's default prepend
import mode, with no `__init__.py` under `tests/`, every `conftest.py` is imported as
the top-level module `conftest` and the last one wins.
"""
from __future__ import annotations

import pytest

from database_agent.db import create_schema

from evidence_shape.schema import create_evidence_schema

from facts.fields import create_fields

#: §8.5 replays a run and compares it against a prior result, so any test that
#: compares two records must be comparing what the resolver produced and not two
#: readings of the wall clock.
FIXED_OBSERVED_AT = "2026-08-19T14:03:22+00:00"


@pytest.fixture()
def observed_at() -> str:
    return FIXED_OBSERVED_AT


@pytest.fixture()
def p6_conn(conn):
    """P1's database with P4's three tables, P6's own tables, and the `fields`
    catalogue loaded — the same shape `tests/p4/conftest.py` builds as `p4_conn`.

    `create_fields` calls `create_facts_schema` itself, so there is no ordering trap
    for a test that only wants the catalogue.
    """
    create_schema(conn)
    create_evidence_schema(conn)
    create_fields(conn)
    return conn
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/p6/test_p6_fields.py -v`
Expected: PASS — 25 passed.

- [ ] **Step 5: Re-run Task 1's tests against the extended fixture**

Run: `pytest tests/p6/ -v`
Expected: PASS — 42 passed (17 from Task 1, 25 here).
`tests/p6/test_p6_states.py::test_extractors_write_two_of_the_six_and_p6_owns_all_six` takes
`p6_conn`, which now also creates P6's tables and loads the catalogue; nothing in that test reads
`fields`, so it is unaffected. `test_no_module_in_facts_publishes_a_second_copy_of_the_six` now
walks five modules instead of two — `authorship`, `fields`, `schema`, `states`, `vocabulary`, of
which four are inspected because `states` is skipped by name — and must still report no offender:
`FIELD_SCOPES` and `VALUE_KINDS` are collections of strings, and neither is the six.

- [ ] **Step 6: Run the whole suite**

Run: `pytest tests/ -q`
Expected: PASS — the 1300 P1–P5 tests, plus 42.

- [ ] **Step 7: Commit**

```bash
git add src/facts/vocabulary.py src/facts/fields.py src/facts/schema.py tests/p6/conftest.py tests/p6/test_p6_fields.py
git commit -m "feat(P6): the closed field catalogue — 37 rows, no add_field, sensitivity_status held open (C5)"
```

---

