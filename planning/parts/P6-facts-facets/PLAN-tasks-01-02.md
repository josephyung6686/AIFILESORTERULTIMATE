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

import pytest
import dataclasses

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

