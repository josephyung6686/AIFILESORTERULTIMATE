# P7 — Privacy and consent gate — PLAN, Tasks 1–3

> This file is one section of P7's implementation plan. Tasks 4–22 are written by other authors
> against the same [`PLAN-SKELETON.md`](PLAN-SKELETON.md); everything published here is consumed
> there under the names the skeleton's `Interfaces:` blocks fix, and those names are honoured
> literally. Format and standard are [`../P4-evidence-shape/PLAN.md`](../P4-evidence-shape/PLAN.md)
> and [`../P5-extractors/PLAN.md`](../P5-extractors/PLAN.md); the finished sibling section is
> [`PLAN-tasks-15-16.md`](PLAN-tasks-15-16.md).

**Verified against the live substrate, 2026-08-22.** Every P1–P5 name quoted below was read with
`inspect.signature` or by importing the module, not from a PLAN. Every design sentence quoted below
was matched by `grep` against
[`../../00-database-agent-product-design.md`](../../00-database-agent-product-design.md) before it
was written down. Five facts that changed what this section says:

- **P7's eight event types are already in P1's frozen table.** `database_agent.events._REGISTERED`
  carries them under the comment *"P7 SPEC, Cross-cutting answers -> Provenance. Eight."*, each with
  `base = None` (`src/database_agent/events.py:43-51`). `REGISTERED_EVENT_TYPES` holds sixteen names
  in total (P7's eight, P8's five, P13's three) and `EVENT_TYPES` holds thirty-five. Registration is
  a spec-level act; Task 1 asserts and adds nothing.
- **`append_event(conn, **fields) -> int`** accepts exactly seventeen named columns —
  `_WRITABLE = EVENT_FIELDS (11) + CORRECTION_FIELDS (5) + "base_event_type"` — and raises
  `MalformedEvent` on an eighteenth. `_REQUIRED` is
  `("event_type", "subsystem", "component_version", "observed_at", "explanation")` and rejects both
  `None` and `""`. So every P7 event carries a non-empty structured explanation by construction.
- **`observation_key(*, content_hash, extractor_name, locator, raw_value) -> str`** returns
  `"sha256:" + 64 hex` (71 characters) via `evidence_shape.canonical.sha256_of`, while
  `evidence_shape.store.new_id()` — the minter of `observation_id` — returns `str(uuid.uuid4())`.
  M14's two handles are shape-distinguishable, so Task 3's refusal is mechanical, not stylistic.
- **`evidence_shape.vocabulary.ZERO_OBSERVATION_COMPLETENESS` exists** and is
  `("unsupported", "deferred", "failed", "metadata_only", "dataless")`. Task 3's per-value table is
  cross-checked against it instead of against a set this author guessed.
- **Four schema creators coexist in one database.** `database_agent.db.create_schema`,
  `scan_agent.schema.create_scan_schema`, `evidence_shape.schema.create_evidence_schema` and
  `extractors.schema.create_extraction_schema` were run in sequence against one connection and
  produced nineteen tables with no collision. That is what `tests/p7/conftest.py` builds on.

---

## Four rulings that bind this section, applied rather than restated

**D2 (ratified) makes `ClassificationRecord` P7's own authoritative record.** Keyed
`(file_id, content_hash)` — on the hash, because a classification is about BYTES and new bytes at a
path are a new file version that inherits nothing. `files.sensitivity_state` is its **projection**,
written through P1's published
`files_table.set_sensitivity_state(conn, file_id, *, state: dict, author: str, component_version:
str) -> None`, which exists and was introspected. There is **no** `SensitivityFacts` protocol to
inject and **no** `SensitivityStateWriter`; D2 killed both. Task 3 therefore builds a record, not a
seam, and imports nothing from P6 — because there is no P6, and after D2 there is nothing in P6 for
this record to read.

**`Unreadable or unclassified` is a GATE OUTCOME, not a file fact.** It belongs on the release
decision and must never be written into `files.sensitivity_state`, so that *"nothing has looked"* can
never be read as *"this file carries nothing"*. **Task 3 is where that distinction becomes
concrete**: `resolve_class` is a decision function that returns a string to a caller, and
`src/privacy/classification.py` contains no writer at all — no `conn`-taking function that inserts or
updates, no import of `set_sensitivity_state`, no name beginning `set_`, `write_`, `record_` or
`mirror_`. A test asserts each of those by introspection. Task 4 owns the mirror and is the only task
allowed to hold both halves.

**The detector is unwritten (D2).** It is P7's, injected, and no task in any plan produces one. Until
one is supplied, every real file resolves to `Denied(unclassified)`. Nothing in these three tasks
defaults an absent classification to a public or low class, and Task 3 carries a test that says so in
the strongest available form: a file that P5 has already marked `potentially sensitive` on every
value still has **no** classification and still resolves to `unreadable_unclassified`. Signals are
not a class. A signal reader is not a detector.

**Handling classes are P7's vocabulary and no other part's, and the words with `protected` in them
must stay distinguishable.** Five strings share one stem across two parts:

| String | Owner | What it is |
|---|---|---|
| `protected` | P7 | the boolean flag on `ClassificationRecord` (Task 3) |
| `protected_cloud_target` | P7 | a `Denied.reason` (Task 2) |
| `protected_records_template` | P7 | a `Denied.reason` (Task 2) |
| `untouched_protected` | P3 | `exclusion.LABEL_UNTOUCHED_PROTECTED` |
| `protected_container` | P3 | `exclusion.REASON_PROTECTED_CONTAINER` |

The skeleton's Task 2 heading counts four and its body names five. The body is right, so **this
section's Task 2 heading says five**; the discrepancy with the skeleton is reported below. Conflating any two of the five is how this part goes
wrong, and Task 2's test pins all five side by side so a later normalization pass is a red test
rather than an editorial choice.

---

## What these three tasks add to the skeleton's `Produces` blocks, and why

The skeleton's `Interfaces:` blocks are a contract with the authors of Tasks 4–22 and every name in
them is honoured exactly. Seven names are **added**, each because the task cannot be written without
it. Each is reported here rather than smuggled in.

| Added | Task | Why the task is not writable without it |
|---|---|---|
| `vocabulary.OPEN_QUESTIONS: Mapping[int, str]` | 2 | The skeleton's own File Structure line says `vocabulary.py` holds *"every closed vocabulary, and OPEN_QUESTIONS"*, and Task 21's `Interfaces:` block says *"`vocabulary.OPEN_QUESTIONS: Mapping[int, str]` is asserted here"*. Task 2's `Produces` list omits it. Task 21 fails without it. |
| `vocabulary.HANDLING_CLASS_LABELS: Mapping[str, str]` | 2 | Nothing else in the codebase ties the identifier `unreadable_unclassified` to the design's own line *"Unreadable or unclassified"*. Without it the five snake_case identifiers are five words a P7 author chose. It is the exact analogue of `MODE_SEMANTICS`, which the skeleton does list. |
| `vocabulary.SHOWN`, `.REDACTED`, `.REDACTION_VALUES: tuple[str, str]` | 2 | SPEC §10's `display_settings` is *"each shown \| redacted"*, and three sections wrote the pair out under three names — `REDACTION_VALUES` in Task 5's `policy.py`, `SETTING_VALUES` in Task 18, `FACET_VALUES` in a third. Task 5's own A7 reported it and asked for this home: *"if Task 2 publishes them, `policy.py` re-exports and deletes its own."* Task 2 publishes; `policy.py` re-exports. The names are Task 5's three, because renaming a consumed surface to gain one home is a cost with no return. |
| `vocabulary.RELIABILITY_STATES` (re-export), `.USER_CONFIRMED`, `.USER` | 2 | Brief §11 makes a named constant the rule for every closed vocabulary either part publishes, and P7 was writing `basis="user"` / `reliability_state="user_confirmed"` as **bare literals** across five sections. `CLASSIFICATION_BASES` was published with no per-value constant and P7 had no reliability-state vocabulary at all. Under D7 there is no P6 tuple to import — but the six states are **P4's**: `evidence_shape.vocabulary.RELIABILITY_STATES`, verified by import, in the design's own line-50 order. `privacy` already binds `evidence_shape`, so Task 2 re-exports P4's tuple and names the two members P7 writes. |
| `classification.COMPLETENESS_RULE: Mapping[str, tuple[bool, str]]` | 3 | The skeleton requires the completeness mapping be *"stated explicitly per value rather than by an `in`-check over a set the author guessed"*. An unpublished internal frozenset **is** that set. The published nine-entry table, each carrying the sentence that decides it, is the requirement. |
| `classification.sensitivity_signal_keys(conn, file_id) -> tuple[str, ...]` | 3 | Task 3's `Consumes` block lists `extractors.long_tail.POTENTIALLY_SENSITIVE`, `.sensitivity_signals_for` and `evidence_shape.store.runs_for_file`, and its `Produces` block names nothing that could consume them. The skeleton's prose settles the intent — *"P7 adds no reader to P5; it composes the two P4 and P5 already publish"* — so the composition is published under one name and decides nothing. |

**One name the skeleton's File Structure asks for and Task 1 cannot supply.**
`src/privacy/__init__.py` is described as *"package marker; exports Gate and the three decision
types"*. `Gate` is Task 20 and `Released` / `Denied` / `NeedsConsent` are Tasks 11–14. Task 1's
`__init__.py` is therefore a docstring-only package marker, exactly as `src/evidence_shape/__init__.py`
and `src/extractors/__init__.py` are, and the re-export lands with `gate.py`. Reported.

---

## Tasks

### Task 1: Package skeleton, and the eight event types P1 already registered

**Files:**
- Create: `src/privacy/__init__.py`
- Create: `src/privacy/authorship.py`
- Create: `tests/p7/conftest.py`
- Test: `tests/p7/test_p7_authorship.py`

**Interfaces:**
- Consumes: `database_agent.events.REGISTERED_EVENT_TYPES: MappingProxyType`,
  `.RESERVED_EVENT_TYPES: frozenset[str]`, `.EVENT_TYPES: MappingProxyType`,
  `.EVENT_FIELDS: tuple[str, ...]`, `.CORRECTION_FIELDS: tuple[str, ...]`,
  `.append_event(conn, **fields) -> int`, `.MalformedEvent`, `.UnregisteredEventType`.
- Produces (`authorship.py`):
  - `SUBSYSTEM: str = "P7"` — §8.2's *"responsible subsystem"*, bound in exactly one place.
  - `COMPONENT_VERSION: str` — P7's own version, the default for §8.2's version slot.
  - `CLASSIFICATION_ASSIGNED`, `CLASSIFICATION_SUPERSEDED`, `POLICY_SET`, `CONSENT_GRANTED`,
    `CONSENT_REVOKED`, `MODEL_RELEASE`, `MODEL_RELEASE_DENIED`, `CONSENT_REQUESTED` — all `str`.
  - `P7_EVENT_TYPES: tuple[str, ...]` — the eight, in the SPEC's order.
  - `event_defaults(*, event_type, **fields) -> dict[str, object]`.
- Produces (`tests/p7/conftest.py`): the `p7_conn` fixture and `FIXED_CLOCK`.

**Done-means:** substrate for 4, 6, 7, 8.

**Why this is Task 1.** Every P7 surface that records anything appends an event, and the one thing
that must never be got wrong is whose name lands in `subsystem`. M8 — *"the acting part authors; P1
writes"* — is unmeetable from a log where the author is a parameter anyone may set. Putting the
authorship helper first means no later task has a plausible reason to type `"P7"` by hand, and Task
21's *"there is one place in `privacy` where that value is written"* guard has exactly one place to
look.

**`event_defaults` writes nothing and takes no connection.** It fills §8.2's authorship fields and
returns a plain `dict` for the caller to hand to P1's `append_event`. There is no code path in which
importing `privacy.authorship` appends an event, and no code path in which P7 writes without a caller
having decided to. C4's rule — *"the gate still raises and writes nothing — a gate that also wrote
would be doing two jobs"* — starts being true here.

**It raises P1's exceptions, not its own, and that is why both are in the `Consumes` list.**
`event_defaults` pre-validates the same shape `append_event` validates: an unknown field is
`MalformedEvent`, an event type outside P7's eight is `UnregisteredEventType`. A caller therefore
catches one exception type whether the refusal came early or at the writer. A third exception class
here would mean two vocabularies for one refusal.

**P7's helper is narrower than P1's writer, on purpose.** `append_event` accepts any of the
thirty-five registered names; `event_defaults` accepts eight. P8's `model_call_issued` is a
perfectly valid event that P7 has no business authoring, and a helper that stamps
`subsystem = "P7"` onto it would produce a true-looking row that names the wrong actor.

**`base_event_type` is refused rather than defaulted.** All eight of P7's names carry `base = None`
in P1's table — none is a typed specialization of one of §8.2's nineteen — so a caller supplying one
is asserting a relationship the registration does not record. P1 would store it; P7 refuses it.

**`explanation` is deliberately not defaulted.** P1's `_REQUIRED` includes it and rejects the empty
string, so every P7 event carries a non-empty *"structured explanation or evidence reference"*
(§8.2) by construction. That slot is where the consent-aware audit record lives — §8.4's record has
thirteen fields `events` has no column for, and Task 10 puts them there as canonical JSON. A default
here would let an event ship with placeholder prose in the one column the audit record needs.

**`observed_at` defaults to now and a caller-supplied value wins.** §8.5's replay must be able to pin
the clock, and every call site in the finished sibling section passes one explicitly.

**`tests/p7/conftest.py` holds P7 names only.** The skeleton's constraint is that nothing imported
across parts by name may live there — `tests/` has no `__init__.py`, so pytest puts each test
directory on `sys.path` and a helper module named the same thing in two directories is one module.
P7's own fixtures are safe; a name another part's conftest or helper also defines is not. The fixture
composes the four substrate schema creators and **does not** create P7's own tables: `schema.py` and
`create_privacy_schema` are Task 5's, and Task 5 adds that one call to this fixture. The request
builders the File Structure line mentions need `ModelCallRequest`, which is Task 11's, and arrive
with it.

- [ ] **Step 1: Write `tests/p7/conftest.py`**

```python
# tests/p7/conftest.py
"""P7's test fixtures.

`p7_conn` is P1's root `conn` fixture with the substrate P7 reads from added:
P1's own tables, P3's scan tables, P4's evidence tables and P5's extraction
tables. `tests/conftest.py` is not modified — P1 owns it.

P7's OWN tables are absent here on purpose. `privacy.schema.create_privacy_schema`
is Task 5's, and Task 5 adds the one call below. Everything Tasks 1-4 need already
exists in the substrate.

Nothing in this file may be a name another part's conftest or test helper also
defines: `tests/` carries no `__init__.py`, so pytest puts each test directory on
`sys.path` and two helpers sharing a name are one module. Only P7 fixtures live
here.
"""
from __future__ import annotations

import pytest

from database_agent.db import create_schema

from scan_agent.schema import create_scan_schema

from evidence_shape.schema import create_evidence_schema

from extractors.schema import create_extraction_schema

#: §8.5 requires replay to reproduce a run, and every P7 record carries §8.2's
#: "time of observation". An injectable clock is what makes an equality assertion
#: on a stored record possible at all.
FIXED_CLOCK = "2026-08-22T12:00:00+00:00"


@pytest.fixture()
def p7_conn(conn):
    """P1's database with P3's, P4's and P5's tables added.

    P7 creates and owns its own tables inside this one database and creates no
    table belonging to another part. Four creators, run in dependency order, were
    verified to coexist: nineteen tables, no collision.
    """
    create_schema(conn)
    create_scan_schema(conn)
    create_evidence_schema(conn)
    create_extraction_schema(conn)
    return conn
```

- [ ] **Step 2: Write the failing test**

```python
# tests/p7/test_p7_authorship.py
"""P7's eight event types are P1's already, and P7's name is written once.

Two things are proved here and they pull in opposite directions. Registration is a
SPEC-level act, so this package must be unable to perform one: the eight names are
asserted present and nothing is added. Authorship is a run-time act, so this package
must perform it in exactly one place: `event_defaults` fills `subsystem` and refuses
to let a caller set it, because M8's "the acting part authors" is unmeetable from a
log where the author is a parameter anyone may set.
"""
import importlib

import pytest

from database_agent.events import (
    CORRECTION_FIELDS, EVENT_FIELDS, EVENT_TYPES, REGISTERED_EVENT_TYPES,
    RESERVED_EVENT_TYPES, MalformedEvent, UnregisteredEventType, append_event,
)

import privacy.authorship as authorship
from privacy.authorship import (
    CLASSIFICATION_ASSIGNED, CLASSIFICATION_SUPERSEDED, COMPONENT_VERSION,
    CONSENT_GRANTED, CONSENT_REQUESTED, CONSENT_REVOKED, MODEL_RELEASE,
    MODEL_RELEASE_DENIED, P7_EVENT_TYPES, POLICY_SET, SUBSYSTEM, event_defaults,
)

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"

#: A ninth name that looks exactly like one of P7's and is registered nowhere. It is
#: the shape of the mistake this test exists to catch: a later author needing an
#: event, inventing a plausible name, and discovering at run time that registration
#: is not something this package can do.
UNREGISTERED = "classification_downgraded"

#: P8's, registered in P1's table and not P7's to author.
ANOTHER_PARTS_EVENT = "model_call_issued"


def an_event(**over):
    fields = dict(event_type=CLASSIFICATION_ASSIGNED, observed_at=FIXED_CLOCK,
                  explanation='{"handling_class": "sensitive_personal"}')
    fields.update(over)
    return fields


# --- the eight names, and the fact that P7 did not add them ------------------

def test_the_eight_are_the_specs_eight_in_the_specs_order():
    # SPEC, Cross-cutting answers -> Provenance, in its own order: "Appends:
    # classification_assigned, classification_superseded (including user
    # reclassification), policy_set, consent_granted, consent_revoked,
    # model_release, model_release_denied, consent_requested."
    assert P7_EVENT_TYPES == (
        "classification_assigned", "classification_superseded", "policy_set",
        "consent_granted", "consent_revoked", "model_release",
        "model_release_denied", "consent_requested",
    )
    assert len(P7_EVENT_TYPES) == 8


def test_each_constant_names_its_own_string():
    assert (CLASSIFICATION_ASSIGNED, CLASSIFICATION_SUPERSEDED, POLICY_SET,
            CONSENT_GRANTED, CONSENT_REVOKED, MODEL_RELEASE, MODEL_RELEASE_DENIED,
            CONSENT_REQUESTED) == P7_EVENT_TYPES


def test_all_eight_are_already_registered_in_p1_with_no_base():
    # src/database_agent/events.py:43-51, under the comment "P7 SPEC, Cross-cutting
    # answers -> Provenance. Eight." P1 compiled them from this SPEC; P7 asserts.
    for name in P7_EVENT_TYPES:
        assert name in REGISTERED_EVENT_TYPES, name
        assert REGISTERED_EVENT_TYPES[name] is None, name


def test_none_of_the_eight_collides_with_8_2s_nineteen():
    # §8.2's list is reserved and may not be redefined by any part. P1 checks this at
    # IMPORT, so a collision is an ImportError; this asserts the property P1 checked.
    assert len(RESERVED_EVENT_TYPES) == 19
    assert set(P7_EVENT_TYPES).isdisjoint(RESERVED_EVENT_TYPES)


def test_importing_privacy_authorship_registers_nothing():
    # Registration is a spec-level act (P1 Contract out §3, rule 4) and there is no
    # run-time registration call. Reloading the module must not grow P1's table.
    before = len(EVENT_TYPES)
    importlib.reload(authorship)
    from database_agent.events import EVENT_TYPES as after_table
    assert len(after_table) == before == 35
    assert not [n for n, v in vars(authorship).items()
                if callable(v) and n.lower().startswith("register")]


def test_p1s_registry_is_a_read_only_mapping_so_p7_could_not_add_one():
    with pytest.raises(TypeError):
        REGISTERED_EVENT_TYPES["classification_downgraded"] = None


# --- authorship: one place, and not a parameter -------------------------------

def test_subsystem_is_p7_and_event_defaults_always_stamps_it():
    assert SUBSYSTEM == "P7"
    for name in P7_EVENT_TYPES:
        assert event_defaults(**an_event(event_type=name))["subsystem"] == SUBSYSTEM


def test_a_caller_may_not_supply_or_override_the_subsystem():
    # M8: "The acting part authors; P1 writes." An author that is a parameter is not
    # an author. This is the check Task 21 counts on when it asserts there is exactly
    # one place in `privacy` where "P7" is written.
    with pytest.raises(MalformedEvent):
        event_defaults(**an_event(subsystem="P7"))
    with pytest.raises(MalformedEvent):
        event_defaults(**an_event(subsystem="P8"))


def test_component_version_defaults_and_a_caller_wins():
    assert event_defaults(**an_event())["component_version"] == COMPONENT_VERSION
    assert event_defaults(**an_event(component_version="9.9.9"))[
        "component_version"] == "9.9.9"


def test_observed_at_defaults_to_now_and_a_caller_supplied_value_wins():
    # §8.5's replay must be able to pin the clock; §8.2 requires "time of observation"
    # on every event, so it can never be absent.
    assert event_defaults(**an_event())["observed_at"] == FIXED_CLOCK
    fields = an_event()
    del fields["observed_at"]
    assert event_defaults(**fields)["observed_at"]


def test_event_defaults_writes_nothing(p7_conn):
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    event_defaults(**an_event())
    assert p7_conn.execute(
        "SELECT count(*) c FROM events").fetchone()["c"] == before
    assert "conn" not in event_defaults.__code__.co_varnames


# --- what the helper accepts, and what it refuses -----------------------------

def test_a_ninth_p7_looking_name_is_refused_here_and_at_p1s_writer(p7_conn):
    with pytest.raises(UnregisteredEventType):
        event_defaults(**an_event(event_type=UNREGISTERED))
    with pytest.raises(UnregisteredEventType):
        append_event(p7_conn, event_type=UNREGISTERED, subsystem=SUBSYSTEM,
                     component_version=COMPONENT_VERSION, observed_at=FIXED_CLOCK,
                     explanation="{}")


def test_another_parts_registered_name_is_refused_by_p7s_helper(p7_conn):
    # P8's event is valid at P1's writer and is not P7's to author. A helper that
    # stamped subsystem="P7" onto it would produce a true-looking row naming the
    # wrong actor.
    assert ANOTHER_PARTS_EVENT in EVENT_TYPES
    with pytest.raises(UnregisteredEventType):
        event_defaults(**an_event(event_type=ANOTHER_PARTS_EVENT))


def test_a_field_p1_has_no_column_for_is_refused():
    # The largest shape decision in this part: §8.4's audit record has thirteen
    # fields `events` has no column for. They go into `explanation` as canonical JSON
    # (Task 10), never into a field name P1 would reject.
    for absent in ("release_id", "audit_id", "policy_version", "outcome"):
        with pytest.raises(MalformedEvent):
            event_defaults(**an_event(**{absent: "x"}))


def test_every_one_of_8_2s_eleven_fields_passes_through():
    passable = [n for n in EVENT_FIELDS
                if n not in ("event_type", "subsystem", "component_version")]
    fields = an_event(**{n: "v" for n in passable if n != "observed_at"})
    defaults = event_defaults(**fields)
    for name in passable:
        assert name in defaults, name


def test_the_five_correction_fields_pass_through():
    # §8.7's columns ride beside §8.2's eleven on a user-action event. Task 16's
    # reclassify needs all five and this helper is its only writer path.
    defaults = event_defaults(**an_event(
        event_type=CLASSIFICATION_SUPERSEDED, correction_scope="file",
        correction_subject="file-1", polarity="reject", proposal_class="privacy",
        basis_key='{"file_id": "file-1"}'))
    for name in CORRECTION_FIELDS:
        assert name in defaults, name


def test_base_event_type_is_refused_because_all_eight_carry_no_base():
    # P1 stores it; P7 refuses it. None of the eight is a typed specialization of one
    # of §8.2's nineteen, so a caller supplying one asserts a relationship the
    # registration does not record.
    with pytest.raises(MalformedEvent):
        event_defaults(**an_event(base_event_type="extraction"))


# --- the round trip, against the real writer ----------------------------------

def test_p1_accepts_an_event_of_each_of_the_eight_types(p7_conn):
    for name in P7_EVENT_TYPES:
        append_event(p7_conn, **event_defaults(**an_event(event_type=name)))
    rows = p7_conn.execute(
        "SELECT event_type, subsystem, base_event_type FROM events "
        "ORDER BY event_id").fetchall()
    assert [r["event_type"] for r in rows] == list(P7_EVENT_TYPES)
    assert {r["subsystem"] for r in rows} == {SUBSYSTEM}
    assert {r["base_event_type"] for r in rows} == {None}


def test_p1_refuses_a_p7_event_with_an_empty_explanation(p7_conn):
    # §8.2's "structured explanation or evidence reference" is where §8.4's
    # consent-aware record lives. P1 rejects None and "", so a P7 event without one
    # is unwritable rather than merely discouraged.
    with pytest.raises(MalformedEvent):
        append_event(p7_conn, **event_defaults(**an_event(explanation="")))
```

- [ ] **Step 3: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_authorship.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'privacy'`. `pyproject.toml` already carries
`pythonpath = ["src"]` and `[tool.setuptools.packages.find] where = ["src"]`, so the package becomes
importable the moment `src/privacy/__init__.py` exists and no build-configuration change is needed.
Collection fails on the first import, so no test runs.

- [ ] **Step 4: Write `src/privacy/__init__.py`**

```python
# src/privacy/__init__.py
"""P7 — the privacy and consent gate (§8.4).

The only door through which file content may reach a model or an external connector.
Five handling classes, four operation modes, nine always-local items, six releasable
item kinds, one `Gate.release` with three branches, and a consent-aware audit record
appended before any release is returned.

The package marker re-exports nothing yet: `Gate` and the three decision types arrive
with `gate.py`. `src/evidence_shape/__init__.py` and `src/extractors/__init__.py` are
the same shape, and a marker that imported a module later tasks have not written
would make every task before that one uncollectable.
"""
```

- [ ] **Step 5: Write `src/privacy/authorship.py`**

```python
# src/privacy/authorship.py
"""P7 authors its events; P1 writes them (M8). The name "P7" is written here, once.

Two rules pull in opposite directions and both are enforced in this module.

**Registration is a SPEC-level act, so this package cannot perform one.** P7's eight
event types are already in P1's frozen `_REGISTERED` table, compiled from this SPEC
under the comment "P7 SPEC, Cross-cutting answers -> Provenance. Eight." There is no
run-time registration call anywhere in P1, and there is none here: the eight names
below are ASSERTED by this part's tests, never added. None collides with §8.2's
nineteen reserved names, and P1 checks that at import, so a collision is an
ImportError rather than a run-time rejection.

**Authorship is a run-time act, so this package performs it in exactly one place.**
M8: "The acting part authors; P1 writes. P1 appends no event on its own initiative."
`event_defaults` stamps `subsystem = SUBSYSTEM` and refuses a caller who supplies
one, because an author that is a parameter is not an author. Task 21 asserts there is
no second place under `src/privacy/` where that value is written.

This module opens no connection and appends nothing. `event_defaults` returns a plain
mapping for a caller to hand to `database_agent.events.append_event`, so there is no
code path in which importing P7 writes to the log.
"""
from __future__ import annotations

from datetime import datetime, timezone

from database_agent.events import (
    CORRECTION_FIELDS, EVENT_FIELDS, MalformedEvent, REGISTERED_EVENT_TYPES,
    UnregisteredEventType,
)

#: §8.2's "responsible subsystem", for every event this part authors. THE one place.
SUBSYSTEM: str = "P7"

#: §8.2's "extractor or model version" slot, for a part that is neither. P7's own
#: package version, and the default a caller may override for a replay (§8.5).
COMPONENT_VERSION: str = "0.1.0"

#: A classification was assigned to a (file_id, content_hash). D2 makes P7's record
#: authoritative, so this event is the record OF the record, not of a write to P6.
CLASSIFICATION_ASSIGNED: str = "classification_assigned"

#: A classification was superseded — including by a user reclassification (§8.4's
#: "revised by the user"). §8.2 forbids overwriting: both records remain inspectable.
CLASSIFICATION_SUPERSEDED: str = "classification_superseded"

#: A privacy/consent policy version was set. §8.8 puts "Privacy and model-consent
#: policies" inside the plan version, so a change must be diffable, which needs a row.
POLICY_SET: str = "policy_set"

#: Consent was granted for a scope. §8.4's four options are the user's, not P7's.
CONSENT_GRANTED: str = "consent_granted"

#: Consent was withdrawn. Forward-only: §8.4 requires the product to say what already
#: left the device, which is unsatisfiable once the send record is erasable.
CONSENT_REVOKED: str = "consent_revoked"

#: Content was released to a model. §8.4: "Every model call should be recorded in a
#: consent-aware audit record" — every, with no exemption for a local model.
MODEL_RELEASE: str = "model_release"

#: A release was refused. Appended on the strength of §8.2's "Every significant event
#: affecting a file" and §8.6's requirement that the UI show what was deferred and why.
MODEL_RELEASE_DENIED: str = "model_release_denied"

#: The gate asked the user. §8.4: "the user should see that requirement and choose".
CONSENT_REQUESTED: str = "consent_requested"

#: The eight, in the SPEC's own order (Cross-cutting answers -> Provenance).
P7_EVENT_TYPES: tuple[str, ...] = (
    CLASSIFICATION_ASSIGNED, CLASSIFICATION_SUPERSEDED, POLICY_SET,
    CONSENT_GRANTED, CONSENT_REVOKED, MODEL_RELEASE, MODEL_RELEASE_DENIED,
    CONSENT_REQUESTED,
)

#: What a caller may pass through: §8.2's eleven minus the three this module owns,
#: plus §8.7's five correction columns. `base_event_type` is P1-writable and is NOT
#: here: all eight of P7's names carry `base = None`, so a caller supplying one is
#: asserting a relationship the registration does not record.
_PASSTHROUGH: frozenset[str] = frozenset(
    set(EVENT_FIELDS) | set(CORRECTION_FIELDS)
) - {"event_type", "subsystem"}

#: The fields this module fills and a caller may not: authorship itself.
_AUTHORED: tuple[str, ...] = ("subsystem",)


def event_defaults(*, event_type: str, **fields) -> dict[str, object]:
    """§8.2's authorship fields for one P7 event, ready for P1's `append_event`.

    Writes nothing and takes no connection. Raises P1's own exceptions rather than
    inventing a third vocabulary for the same refusal: an unknown or authored field
    is `MalformedEvent`, an event type outside P7's eight is `UnregisteredEventType`.

    `explanation` is deliberately not defaulted. P1's writer requires it and rejects
    the empty string, so every P7 event carries a non-empty "structured explanation or
    evidence reference" (§8.2) by construction — and that column is where §8.4's
    consent-aware record lives, since `events` has no column for thirteen of its
    fields. A default here would let an event ship with placeholder prose in the one
    column the audit record needs.
    """
    if event_type not in P7_EVENT_TYPES:
        raise UnregisteredEventType(
            f"{event_type!r} is not one of P7's eight declared event types "
            f"{P7_EVENT_TYPES}. Registration is a spec-level act (P1 Contract out "
            "§3, rule 4): a new P7 event is a SPEC revision, and an event another "
            "part declared is that part's to author (M8)."
        )
    for name in _AUTHORED:
        if name in fields:
            raise MalformedEvent(
                f"{name} is authored by this module and is not a parameter. M8: "
                '"the acting part authors; P1 writes." An author a caller may set '
                "is not an author."
            )
    unknown = sorted(set(fields) - _PASSTHROUGH)
    if unknown:
        raise MalformedEvent(
            f"{unknown} are not among §8.2's eleven event fields (MINOR 1) or §8.7's "
            "five correction columns; P7 adds no column to `events` and does not ask "
            "P1 to. §8.4's audit fields with no column go into `explanation` as "
            "canonical JSON (B5)."
        )
    return {
        "event_type": event_type,
        "subsystem": SUBSYSTEM,
        "component_version": COMPONENT_VERSION,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        **fields,
    }
```

- [ ] **Step 6: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_authorship.py -v`
Expected: PASS — 19 passed

- [ ] **Step 7: Run P1–P5 and confirm P7 broke nothing**

Run: `pytest tests/ -q`
Expected: PASS — every pre-existing test still green. P7 created `src/privacy/` and `tests/p7/` and
modified no file belonging to another part: not `pyproject.toml`, not `tests/conftest.py`, and
nothing under `src/database_agent/`, `src/scan_agent/`, `src/evidence_shape/`, `src/extractors/` or
`src/eval_harness/`.

- [ ] **Step 8: Commit**

```bash
git add src/privacy/__init__.py src/privacy/authorship.py tests/p7/conftest.py tests/p7/test_p7_authorship.py
git commit -m "feat(P7): package skeleton, and the eight event types asserted against P1's frozen registry"
```

---

### Task 2: The closed vocabularies, and the five words with `protected` in them

**Files:**
- Create: `src/privacy/vocabulary.py`
- Test: `tests/p7/test_p7_vocabulary.py`

**Interfaces:**
- Consumes: `scan_agent.exclusion.LABEL_UNTOUCHED_PROTECTED: str`, `.REASON_PROTECTED_CONTAINER: str`
  — imported **in the test only**, to pin the distinction. `src/privacy/` imports neither, and
  `privacy.vocabulary` binds no value equal to either.
- Consumes: `evidence_shape.vocabulary.RELIABILITY_STATES: tuple[str, ...]` — imported by the
  **module**, not copied. P4's shipped six, in the design's own line-50 order.
- Produces (`vocabulary.py`):
  - `HANDLING_CLASSES: tuple[str, ...]` (5), `HANDLING_CLASS_LABELS: Mapping[str, str]` (added — the
    design's own five lines).
  - `OPERATION_MODES: tuple[str, ...]` (4), `MODE_SEMANTICS: Mapping[str, str]` (§8.4 verbatim).
  - `ALWAYS_LOCAL: tuple[str, ...]` (9).
  - `ITEM_KINDS: tuple[str, ...]` (6).
  - `DENIAL_REASONS: tuple[str, ...]` (8).
  - `CONSENT_OPTIONS: tuple[str, ...]` (4).
  - `DISPLAY_FACETS: tuple[str, ...]` (5).
  - `CLASSIFICATION_BASES: tuple[str, ...]` (3), and `USER: str = "user"` — the one member P7 writes
    (added, brief §11).
  - `AUDIT_OUTCOMES: tuple[str, ...]` (3).
  - `RELIABILITY_STATES: tuple[str, ...]` — **re-exported** from `evidence_shape.vocabulary`, not
    retyped — and `USER_CONFIRMED: str`, the one member P7 writes (added, brief §11).
  - `SHOWN: str = "shown"`, `REDACTED: str = "redacted"`,
    `REDACTION_VALUES: tuple[str, str] = (SHOWN, REDACTED)` (added — SPEC §10's *"each shown |
    redacted"*; Task 5's A7 reported these and asked for this home).
  - `OPEN_QUESTIONS: Mapping[int, str]` (added — the SPEC's eleven, held open).
  - `OutOfVocabulary`.
  - `check_handling_class(value) -> str`, `check_mode(value) -> str`,
    `check_item_kind(value) -> str`, `check_denial_reason(value) -> str`.

**Done-means:** 1.

**Why this is Task 2 and not later.** Every subsequent task validates against one of these tuples,
and a vocabulary that arrives after its consumers is a vocabulary each consumer has already spelled
its own way. D2's warning from P4's equivalent task applies verbatim in shape: six callers produce
six spellings and nothing has a stable key.

**A value outside the set is a load error, not a fallback.** The SPEC states it once and it is the
whole point of the four `check_*` functions: *"A value outside this set is a load error, not a
fallback."* The refusal message therefore names the closed set and **does not suggest a nearest
match**. `check_handling_class("public")` must not mention `public_low`. A suggestion is how a
misspelling becomes a silent downgrade, and a silent downgrade in this vocabulary is the failure
§8.6 forbids by name.

**Four checkers, not nine, and that is the skeleton's contract.** The four vocabularies with a
checker are the four a caller supplies a value into from outside P7: a handling class arrives from a
detector or a user, a mode from a policy, an item kind from P8's request, a denial reason from P7's
own branches under test. `CONSENT_OPTIONS`, `DISPLAY_FACETS`, `CLASSIFICATION_BASES`,
`AUDIT_OUTCOMES`, `REDACTION_VALUES` and `RELIABILITY_STATES` are consumed as membership tests by
the tasks that own them (5, 10, 14, 16). A checker on each of the rest would be six more names for
Task 21 to introspect and six more places for the same refusal to be spelled differently.

**`SHOWN` and `REDACTED` live here, and nowhere else.** SPEC §10 spells `display_settings` as *"each
shown | redacted"*, and three separate sections wrote the pair out under three names —
`REDACTION_VALUES` in Task 5's `policy.py`, `SETTING_VALUES` in Task 18, `FACET_VALUES` in a third.
Three homes and three names for two strings is this project's most expensive defect class, and the
Task 5 author reported it against themselves: *"they arguably belong in Task 2's `vocabulary.py`; if
Task 2 publishes them, `policy.py` re-exports and deletes its own"* (A7). Task 2 publishes them, so
`policy.py` re-exports and deletes its own, and Task 18 and its sibling import rather than respell.
The names are **`SHOWN`, `REDACTED`, `REDACTION_VALUES`** — Task 5's own three, because they are
already written and already consumed under those names, and the cheapest single home is the one that
renames nothing. They sit beside `DISPLAY_FACETS` because that is the tuple they are the values of:
`redaction_settings` is a mapping from a facet to one of these two, and a facet vocabulary published
without its value vocabulary is half a contract.

**The classification basis and the reliability state get named constants, and the six states are
P4's.** Brief §11 makes named constants the rule for every closed vocabulary either part publishes —
*"Never a bare string, never an index"* — and P7 was writing `basis="user"` and
`reliability_state="user_confirmed"` as bare literals in five sections. `CLASSIFICATION_BASES` was
published with no per-value constant, and there was **no reliability-state vocabulary in P7 at all**.
Under D7, P7's Contract-in from P6 is empty and P7 imports nothing from P6, so a P6-published tuple
was not available to import — which is how the literals survived.

**They did not need P6.** The six states are **P4's**, shipped:
`evidence_shape.vocabulary.RELIABILITY_STATES == ("user_confirmed", "direct", "validated",
"llm_supported", "possible", "rejected")`, verified by import, and that order is the design's own
line 50 read in sequence — *"A **user confirmed** fact … A **direct** fact … A **validated** fact …
An **LLM-supported** fact … A **possible** fact … A **rejected** fact"*. P6's Task 1 publishes the
same six for `facts` (brief §11); P7 imports **P4's**, because `privacy` already binds
`evidence_shape` — it is one of the three packages in the L2 guard set `{evidence_shape,
orchestrator, privacy}` — and because D7 forbids the P6 import. The tuple is **re-exported, not
copied**: a second literal spelling of six strings is the thing the rule exists to prevent, and a
re-export means a P4 revision reaches P7 by import rather than by memory.

**One named constant per member P7 actually writes, not six.** `USER_CONFIRMED` and `USER` are the
two P7 writes — a user reclassifying is the only classification P7 itself originates (Task 16), and
`basis="user"` and `reliability_state="user_confirmed"` are what that record carries. The other five
states are read, never written, and `check`ing membership against the re-exported tuple is what
reading needs. Publishing a constant for a member nothing writes would be five more names for Task 21
to introspect, which is the same argument as the four checkers above.

**No threshold, no ceiling, no number.** This module contains no `int` and no `float` at all, and a
test asserts it by walking the module namespace. §8.6 names the knobs, states they are
*"configurable"*, and gives no values; the SPEC's *Deferred* table puts *"Numeric values for every
ceiling"* outside this contract. A number here would be the first invented value in the part.

**The five spellings, pinned side by side.** The skeleton's heading counts four words with
`protected` in them and its body enumerates five strings; the body is right, and this task follows
it. The five are P7's `protected` flag (Task 3's boolean field), P7's `protected_cloud_target` and
`protected_records_template` denial reasons, P3's `untouched_protected` label and P3's
`protected_container` exclusion reason. Two facts make the distinction load-bearing rather than
tidy:

- **P3's two are about *reading*, P7's three are about *release*.** A protected container is a
  filesystem rule: P3 *"does not descend into one, does not stat its contents, does not hash a byte
  of it, and does not create a `files` row for anything inside it"*. A file inside one never acquires
  the `(file_id, content_hash)` pair P7 keys on, so `Gate.release` cannot be asked about it. The
  guarantee is structural, not a check P7 performs.
- **P7's `Denial.reason` vocabulary contains no bare `protected`.** It contains
  `protected_cloud_target` — a protected file with a cloud target — and `protected_records_template`
  — §7.3's residual template, whose design sentence is *"it should normally remain local-only and
  must not cause filenames or content to be exposed in model prompts"*. A normalization pass that
  collapsed either onto `protected` would produce a denial that cannot say which rule fired.

**`filename` is the one item kind the design's own sentence does not list, and it is flagged in
code.** §8.4 permits *"selected excerpts, redacted identifiers, candidate labels, non-sensitive
metadata, and evidence references"* — five. The sixth, `filename`, comes from the SPEC's flagged
reading: §8.4 puts *paths* in the always-local set, §7.7 puts the filename in the residual dossier,
and §7.3 forbids filenames in prompts **only** for Protected Records, which is vacuous under any
reading that already forbade them everywhere. The SPEC calls this *"the one place where the contract
resolves an apparent conflict rather than deferring it, because P8 and P11 cannot build without an
answer"*, and it is Open question 2. The test asserts `filename` is the only member of `ITEM_KINDS`
absent from §8.4's five, and `OPEN_QUESTIONS[2]` keeps the question open.

**What this task does not do.** It publishes no detection rule, no regex, no gazetteer, no filename
pattern and no keyword list. SPEC *Deferred*: *"The design states *what* is protected and never *how
it is recognised*. The detector rule set, its signals, and its thresholds are hand-authored. P7
publishes the vocabulary the detectors write into."* This module is that vocabulary and nothing else.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_vocabulary.py
"""§8.4's closed vocabularies, and the five strings that share the stem "protected".

Two kinds of assertion live here. Most pin a tuple against the design's own words, in
the design's own order, so a later edit is a red test and not an editorial choice. The
rest pin the boundary: an out-of-vocabulary value is a load error that suggests no
neighbour, no member is a number, and nothing in this module is one of P3's strings
wearing P7's clothes.

Where a vocabulary can be DERIVED from a design sentence mechanically, it is. A test
that retypes the nine always-local items proves the author can retype; a test that
splits the design's sentence proves the identifiers are the design's words.
"""
import re
from collections.abc import Mapping

import pytest

from evidence_shape import vocabulary as p4_vocabulary
from scan_agent.exclusion import LABEL_UNTOUCHED_PROTECTED, REASON_PROTECTED_CONTAINER

import privacy.vocabulary as vocabulary
from privacy.vocabulary import (
    ALWAYS_LOCAL, AUDIT_OUTCOMES, CLASSIFICATION_BASES, CONSENT_OPTIONS,
    DENIAL_REASONS, DISPLAY_FACETS, HANDLING_CLASSES, HANDLING_CLASS_LABELS,
    ITEM_KINDS, MODE_SEMANTICS, OPEN_QUESTIONS, OPERATION_MODES, OutOfVocabulary,
    REDACTED, REDACTION_VALUES, REJECTED, RELIABILITY_STATES, SHOWN, USER,
    USER_CONFIRMED, DETECTOR,
    check_denial_reason, check_handling_class, check_item_kind, check_mode,
)

#: The design's line 50, verbatim. The six reliability states are derived from this
#: sentence run rather than retyped, which is what makes the tuple's ORDER the
#: design's and not an author's.
RELIABILITY_SENTENCES = (
    "A user confirmed fact has been explicitly accepted, entered, renamed, merged, "
    "or corrected by the user. A direct fact was read from a reliable and explicit "
    "source. A validated fact was found by a deterministic rule and passed "
    "contextual checks. An LLM-supported fact was proposed by a language model. "
    "A possible fact is a useful but insufficient clue. A rejected fact is a "
    "proposal that the user or validator marked as incorrect."
)

#: §8.4, verbatim. The nine names are derived from this sentence rather than retyped.
ALWAYS_LOCAL_SENTENCE = (
    "Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, "
    "user edits, group memberships, and raw sensitive values should remain local."
)

#: §8.4, verbatim. The five facets are derived from this sentence.
DISPLAY_SENTENCE = (
    "The user can choose whether names, previews, thumbnails, OCR text, or "
    "location data are shown."
)

#: §8.4's compact dossier, verbatim. Five kinds; `filename` is not among them.
DOSSIER_SENTENCE = (
    "selected excerpts, redacted identifiers, candidate labels, non-sensitive "
    "metadata, and evidence references"
)


def _identifiers(listed: str) -> tuple[str, ...]:
    """Split a design list into P7's snake_case identifiers, mechanically."""
    out = []
    for part in listed.split(","):
        word = part.strip().removeprefix("and ").removeprefix("or ")
        out.append(word.lower().replace(" ", "_"))
    return tuple(out)


def _states(prose: str) -> tuple[str, ...]:
    """Pull `A <name> fact` / `An <name> fact` out of line 50, in order."""
    return tuple(
        match.group(1).strip().lower().replace("-", "_").replace(" ", "_")
        for match in re.finditer(r"\b(?:A|An) ((?:[\w-]+ )+?)fact\b", prose)
    )


# --- the five handling classes -----------------------------------------------

def test_the_five_classes_are_the_designs_five_in_the_designs_order():
    assert HANDLING_CLASSES == (
        "public_low", "personal_non_sensitive", "sensitive_personal",
        "highly_sensitive_credential_bearing", "unreadable_unclassified",
    )


def test_each_identifier_is_the_designs_own_line():
    # "The system should classify data into handling classes before LLM escalation:"
    # then five lines. Without this mapping the five identifiers are five words a P7
    # author chose; with it they are the design's, spelled in snake_case.
    assert tuple(HANDLING_CLASS_LABELS[name] for name in HANDLING_CLASSES) == (
        "Public or low sensitivity",
        "Personal but non-sensitive",
        "Sensitive personal",
        "Highly sensitive or credential-bearing",
        "Unreadable or unclassified",
    )
    assert tuple(HANDLING_CLASS_LABELS) == HANDLING_CLASSES


def test_no_sixth_class_was_added():
    assert len(HANDLING_CLASSES) == 5
    assert len(set(HANDLING_CLASSES)) == 5


def test_an_out_of_vocabulary_class_is_a_load_error_that_suggests_no_neighbour():
    # "A value outside this set is a load error, not a fallback." A suggestion is how
    # a misspelling becomes a silent downgrade, which is what §8.6 forbids by name.
    with pytest.raises(OutOfVocabulary) as caught:
        check_handling_class("public")
    assert "public_low" not in str(caught.value)
    with pytest.raises(OutOfVocabulary):
        check_handling_class("")
    with pytest.raises(OutOfVocabulary):
        check_handling_class(None)
    assert check_handling_class("unreadable_unclassified") == "unreadable_unclassified"


# --- the four operation modes ------------------------------------------------

def test_the_four_modes_are_the_designs_four_in_order():
    assert OPERATION_MODES == ("offline", "local_model", "hybrid", "cloud_assisted")


def test_mode_semantics_reproduces_8_4s_four_sentences_verbatim():
    # Verbatim so a later paraphrase is a failing test. "Sensitive files remain local"
    # is the whole of what `hybrid` promises; a reworded version could promise less.
    assert MODE_SEMANTICS == {
        "offline":
            "No content leaves the device; only local rules and local models may run.",
        "local_model":
            "Local extraction plus a user-installed local LLM for eligible dossiers.",
        "hybrid":
            "Sensitive files remain local; non-sensitive bounded dossiers may use a "
            "cloud LLM.",
        "cloud_assisted":
            "User explicitly permits selected corpus areas to use a cloud model.",
    }
    assert tuple(MODE_SEMANTICS) == OPERATION_MODES


def test_an_out_of_vocabulary_mode_is_refused():
    with pytest.raises(OutOfVocabulary):
        check_mode("cloud")
    assert check_mode("offline") == "offline"


# --- the always-local nine ---------------------------------------------------

def test_the_nine_always_local_items_are_the_designs_own_words():
    listed = ALWAYS_LOCAL_SENTENCE.split(" should remain local.")[0]
    assert ALWAYS_LOCAL == _identifiers(listed)
    assert len(ALWAYS_LOCAL) == 9


def test_nothing_in_the_always_local_set_is_a_releasable_item_kind():
    # "Nothing in this set can be named as a releasable item kind. The gate has no
    # code path that materialises one." The vocabulary makes it unnameable; Task 7
    # makes it a denial.
    assert set(ALWAYS_LOCAL).isdisjoint(ITEM_KINDS)


def test_paths_are_always_local_and_filename_is_a_separate_string():
    # Open question 2, and the SPEC's flagged reading: directory path is not filename.
    assert "paths" in ALWAYS_LOCAL
    assert "filename" in ITEM_KINDS
    assert "filename" not in ALWAYS_LOCAL


# --- the six releasable item kinds -------------------------------------------

def test_the_six_item_kinds_are_the_specs_six_in_order():
    assert ITEM_KINDS == (
        "excerpt", "redacted_identifier", "candidate_label", "metadata_field",
        "evidence_reference", "filename",
    )


def test_filename_is_the_only_kind_the_designs_own_sentence_does_not_list():
    # §8.4 permits five. P7 singularises each and spells "non-sensitive metadata" as
    # `metadata_field`, because the item carries ONE named field. The sixth kind
    # corresponds to no phrase in that sentence: it is the SPEC's flagged reading of
    # §7.3 versus §7.7, adopted because P8 and P11 cannot build without an answer,
    # and held open as Open question 2 rather than treated as settled.
    from_design = {
        "excerpt": "selected excerpts",
        "redacted_identifier": "redacted identifiers",
        "candidate_label": "candidate labels",
        "metadata_field": "non-sensitive metadata",
        "evidence_reference": "evidence references",
    }
    assert [k for k in ITEM_KINDS if k not in from_design] == ["filename"]
    for phrase in from_design.values():
        assert phrase in DOSSIER_SENTENCE, phrase
    assert "filename" not in DOSSIER_SENTENCE
    assert 2 in OPEN_QUESTIONS


def test_an_out_of_vocabulary_item_kind_is_refused():
    with pytest.raises(OutOfVocabulary):
        check_item_kind("whole_document")
    assert check_item_kind("excerpt") == "excerpt"


# --- the eight denial reasons and the five protected spellings ---------------

def test_the_eight_denial_reasons_are_the_specs_eight_in_order():
    assert DENIAL_REASONS == (
        "protected_cloud_target", "unclassified", "policy_revoked",
        "protected_records_template", "whole_document_requested",
        "dossier_over_budget", "always_local_item", "mode_forbids_target",
    )
    assert check_denial_reason("unclassified") == "unclassified"
    with pytest.raises(OutOfVocabulary):
        check_denial_reason("protected")


def test_the_five_protected_spellings_coexist_and_no_two_are_equal():
    # P3's two are about READING and P7's three are about RELEASE. A file inside a
    # protected container has no `files` row, so the gate cannot be asked about it;
    # a protected file under `hybrid` has one and is denied a cloud target.
    spellings = (
        "protected",                     # P7's flag on ClassificationRecord (Task 3)
        "protected_cloud_target",        # P7's denial reason
        "protected_records_template",    # P7's denial reason (§7.3)
        LABEL_UNTOUCHED_PROTECTED,       # P3: "untouched_protected"
        REASON_PROTECTED_CONTAINER,      # P3: "protected_container"
    )
    assert len(set(spellings)) == 5
    assert all("protected" in s for s in spellings)
    assert LABEL_UNTOUCHED_PROTECTED == "untouched_protected"
    assert REASON_PROTECTED_CONTAINER == "protected_container"


def test_no_p7_vocabulary_contains_a_bare_protected():
    for closed in (HANDLING_CLASSES, OPERATION_MODES, ALWAYS_LOCAL, ITEM_KINDS,
                   DENIAL_REASONS, CONSENT_OPTIONS, DISPLAY_FACETS,
                   CLASSIFICATION_BASES, AUDIT_OUTCOMES, RELIABILITY_STATES,
                   REDACTION_VALUES):
        assert "protected" not in closed


def test_p7s_vocabulary_module_holds_none_of_p3s_strings():
    # The test imports P3 to pin the distinction; `src/privacy/` imports neither
    # constant and holds no copy of either literal.
    p3 = {LABEL_UNTOUCHED_PROTECTED, REASON_PROTECTED_CONTAINER, "protected container"}

    def strings_in(value):
        if isinstance(value, str):
            return {value}
        if isinstance(value, tuple):
            return {v for v in value if isinstance(v, str)}
        if isinstance(value, Mapping):
            return {v for v in value.values() if isinstance(v, str)}
        return set()

    for name, value in vars(vocabulary).items():
        if name.startswith("_"):
            continue
        assert not strings_in(value) & p3, name


# --- consent options, display facets, bases, outcomes ------------------------

def test_the_four_consent_options_are_8_4s_own_four():
    # "the user should see that requirement and choose whether to allow a local
    # model, a cloud model, a redacted prompt, or no model use" -- those four,
    # exactly, and in that order.
    assert CONSENT_OPTIONS == (
        "local_model", "cloud_model", "redacted_prompt", "no_model_use")


def test_local_model_is_both_a_mode_and_a_consent_option_and_that_is_not_a_bug():
    # §8.4 names it in both lists. Open question 6 asks whether a local call is a
    # consent event or only an audit event; the shared string is where that question
    # touches the code, and nothing here answers it.
    assert "local_model" in OPERATION_MODES
    assert "local_model" in CONSENT_OPTIONS
    assert 6 in OPEN_QUESTIONS


def test_the_five_display_facets_are_the_designs_own_words():
    listed = DISPLAY_SENTENCE.split("whether ")[1].split(" are shown.")[0]
    assert DISPLAY_FACETS == _identifiers(listed)
    assert DISPLAY_FACETS == (
        "names", "previews", "thumbnails", "ocr_text", "location_data")


def test_three_classification_bases_and_three_audit_outcomes():
    assert CLASSIFICATION_BASES == ("detector", "safety_domain", "user")
    assert AUDIT_OUTCOMES == ("released", "denied", "consent_requested")


def test_the_one_basis_p7_writes_has_a_named_constant():
    # Brief §11: never a bare string, never an index. `basis="user"` was written as a
    # literal in five sections before this constant existed.
    assert USER == "user"
    assert USER in CLASSIFICATION_BASES


# --- the six reliability states, imported from P4 and not retyped ------------

def test_the_six_states_are_p4s_tuple_and_not_a_second_copy():
    # Re-exported, not copied. `is` and not `==`: a second tuple with the same six
    # strings would pass equality and would be exactly the second home the rule
    # exists to prevent. D7 makes P7's Contract-in from P6 empty, so this is P4's
    # tuple -- `privacy` already binds `evidence_shape` -- and never P6's.
    assert RELIABILITY_STATES is p4_vocabulary.RELIABILITY_STATES


def test_the_states_are_the_designs_line_50_in_the_designs_order():
    # The order is the ranking Task 4 reads (§3.13), so it is derived from the
    # design's own sentence run rather than retyped: "A user confirmed fact ... A
    # direct fact ... A validated fact ... An LLM-supported fact ... A possible fact
    # ... A rejected fact."
    assert RELIABILITY_STATES == _states(RELIABILITY_SENTENCES)
    assert RELIABILITY_STATES == (
        "user_confirmed", "direct", "validated", "llm_supported", "possible",
        "rejected")


def test_the_one_state_p7_writes_has_a_named_constant():
    # Task 16's reclassification is the only classification P7 originates, and it
    # writes USER_CONFIRMED. Task 4's store also needs REJECTED as an exclusion, so
    # that literal is published here rather than respelt in classification_store.
    assert USER_CONFIRMED == "user_confirmed"
    assert USER_CONFIRMED in RELIABILITY_STATES
    assert RELIABILITY_STATES[0] == USER_CONFIRMED


def test_rejected_is_published_as_the_exclusion_not_a_second_spelling():
    assert REJECTED == "rejected"
    assert REJECTED in RELIABILITY_STATES
    assert REJECTED == RELIABILITY_STATES[-1]


def test_p7_publishes_no_second_spelling_of_a_state():
    # The failure this whole section exists to prevent: a module-level string in
    # `privacy.vocabulary` whose value happens to be one of P4's six, bound under a
    # name that is not a published constant.
    allowed = {"USER_CONFIRMED": USER_CONFIRMED, "REJECTED": REJECTED}
    for name, value in vars(vocabulary).items():
        if name.startswith("_") or not isinstance(value, str):
            continue
        if value in RELIABILITY_STATES:
            assert name in allowed, name
            assert value == allowed[name]


def test_detector_is_the_named_basis_constant():
    assert DETECTOR == "detector"
    assert DETECTOR in CLASSIFICATION_BASES


# --- SPEC §10's two display values, one home ---------------------------------

def test_the_two_display_values_are_spec_10s_two():
    # SPEC §10: `display_settings` is "each shown | redacted". Before this constant
    # existed the pair had three homes and three names -- `REDACTION_VALUES` in
    # `policy.py`, `REDACTION_VALUES` in Task 18, `REDACTION_VALUES` in a third section.
    assert (SHOWN, REDACTED) == ("shown", "redacted")
    assert REDACTION_VALUES == (SHOWN, REDACTED)


def test_a_display_facet_maps_to_one_of_exactly_two_values():
    # The reason the pair belongs beside DISPLAY_FACETS: it is the value vocabulary
    # of that key vocabulary, and a facet list published without one is half a
    # contract. W1's "the more redacting option is the default" is Task 6's rule and
    # no default lives here.
    assert len(REDACTION_VALUES) == 2
    assert set(REDACTION_VALUES).isdisjoint(DISPLAY_FACETS)


def test_unreadable_unclassified_is_a_class_and_unclassified_is_a_denial_reason():
    # D2: "Unreadable or unclassified is a GATE OUTCOME, not a file fact." The class
    # is what `resolve_class` returns to a caller; the denial reason is what the gate
    # says when it has no classification to release against. Two strings, one idea,
    # and neither may be written into `files.sensitivity_state`.
    assert "unreadable_unclassified" in HANDLING_CLASSES
    assert "unclassified" in DENIAL_REASONS
    assert "unclassified" not in HANDLING_CLASSES
    assert "unreadable_unclassified" not in DENIAL_REASONS


# --- the boundary: eleven questions, and no numbers --------------------------

def test_all_eleven_open_questions_are_present_and_unanswered():
    assert set(OPEN_QUESTIONS) == set(range(1, 12))
    for number, question in OPEN_QUESTIONS.items():
        assert isinstance(question, str) and question.strip(), number


def test_the_module_holds_no_number_at_all():
    # "no numeric ceiling, no retention period" -- the SPEC's Deferred table puts
    # "Numeric values for every ceiling" outside this contract, and §8.6 gives none.
    # A number here would be the first invented value in the part.
    for name, value in vars(vocabulary).items():
        if name.startswith("_"):
            continue
        assert not isinstance(value, (int, float)), name


def test_every_vocabulary_is_a_tuple_of_unique_nonempty_strings():
    for closed in (HANDLING_CLASSES, OPERATION_MODES, ALWAYS_LOCAL, ITEM_KINDS,
                   DENIAL_REASONS, CONSENT_OPTIONS, DISPLAY_FACETS,
                   CLASSIFICATION_BASES, AUDIT_OUTCOMES, RELIABILITY_STATES,
                   REDACTION_VALUES):
        assert isinstance(closed, tuple)
        assert len(set(closed)) == len(closed)
        assert all(isinstance(v, str) and v and v == v.strip() for v in closed)


def test_the_mappings_are_read_only_so_a_caller_cannot_add_a_member():
    with pytest.raises(TypeError):
        MODE_SEMANTICS["air_gapped"] = "no"
    with pytest.raises(TypeError):
        HANDLING_CLASS_LABELS["top_secret"] = "no"
    with pytest.raises(TypeError):
        OPEN_QUESTIONS[12] = "no"
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_vocabulary.py -v`
Expected: FAIL — `ImportError: cannot import name 'ALWAYS_LOCAL' from 'privacy.vocabulary'`, because
`src/privacy/vocabulary.py` does not exist yet and collection fails on the first import. `privacy`
itself imports, since Task 1 created the package.

- [ ] **Step 3: Write `src/privacy/vocabulary.py`**

```python
# src/privacy/vocabulary.py
"""§8.4's closed vocabularies, and the eleven questions P7 holds open.

Closed means a caller may not add a value. SPEC §1: "A value outside this set is a
load error, not a fallback." Adding a member is a P7 contract revision, not an
implementation decision, and the four `check_*` functions below refuse an outsider
WITHOUT suggesting a neighbour -- a suggestion is how a misspelling becomes a silent
downgrade, and a silent downgrade in this vocabulary is the failure §8.6 names:
"Cost exhaustion must never turn into lower-quality automatic classification."

Every member is the design's, in the design's order, and nothing here is invented.
Where the design writes prose, the prose is carried beside the identifier
(`HANDLING_CLASS_LABELS`, `MODE_SEMANTICS`) so a later paraphrase is a failing test.

**One home per vocabulary, and one named constant per member P7 writes.** Brief §11:
"Never a bare string, never an index." Two vocabularies reach this module from
outside their obvious owners for that reason. §3.13's six reliability states are
RE-EXPORTED from `evidence_shape.vocabulary` -- P4 ships them, `privacy` already
binds `evidence_shape`, and D7 empties P7's Contract-in from P6, so importing P4's
tuple is both the closest home and the only one available. SPEC §10's `shown` /
`redacted` pair lands here rather than in `policy.py` because three sections had
written it out under three names; `policy.py` re-exports these and deletes its own.

**This module holds no detection rule and no number.** SPEC *Deferred*: "The design
states *what* is protected and never *how it is recognised*. The detector rule set,
its signals, and its thresholds are hand-authored. P7 publishes the vocabulary the
detectors write into." There is no regex, no gazetteer, no filename pattern, no
keyword list, no threshold and no ceiling; §8.6 names the knobs, calls them
"configurable", and gives no values.

**Five strings share the stem "protected" and no two of them are the same word.**
P7's `protected` flag (`classification.ClassificationRecord`), P7's
`protected_cloud_target` and `protected_records_template` denial reasons, P3's
`untouched_protected` exclusion label and P3's `protected_container` exclusion reason.
P3's two are about READING -- a file inside a protected container never acquires the
(file_id, content_hash) pair the gate keys on, so `Gate.release` cannot be asked about
it. P7's three are about RELEASE, which is a policy the user can override through
consent, and that is exactly what makes it a different refusal. `src/privacy/` imports
neither of P3's constants; the distinction is pinned in `tests/p7/test_p7_vocabulary.py`.
"""
from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

# §3.13's six reliability states, RE-EXPORTED and not retyped. The import IS the
# publication: rebinding it -- `RELIABILITY_STATES = _RELIABILITY_STATES` -- would put
# a second module-level collection in `privacy` under a private alias, and a leading
# underscore exempts nothing from an introspecting guard. See the block beside
# `USER_CONFIRMED` below for why the states are P4's and not P6's.
from evidence_shape.vocabulary import RELIABILITY_STATES


class OutOfVocabulary(ValueError):
    """A value outside a closed set. SPEC §1: a load error, not a fallback."""


def _check(value: object, closed: tuple[str, ...], what: str) -> str:
    """Refuse an outsider by naming the closed set, never a nearest match."""
    if not isinstance(value, str) or value not in closed:
        raise OutOfVocabulary(
            f"{value!r} is not one of the {len(closed)} {what} the design defines "
            f"{closed}. §8.4's vocabularies are closed: a value outside the set is a "
            "load error, not a fallback, and adding a member is a P7 contract "
            "revision rather than an implementation decision."
        )
    return value


# --- §8.4: five handling classes, assigned before LLM escalation -------------

#: "The system should classify data into handling classes before LLM escalation".
#: The five, in the design's order. Absence of a classification resolves to the last
#: of them and NEVER to the first -- see `classification.resolve_class`.
HANDLING_CLASSES: tuple[str, ...] = (
    "public_low",
    "personal_non_sensitive",
    "sensitive_personal",
    "highly_sensitive_credential_bearing",
    "unreadable_unclassified",
)

#: The design's own five lines, so the snake_case identifiers above are traceable to
#: the words that define them rather than to a P7 author's choice of spelling.
HANDLING_CLASS_LABELS: Mapping[str, str] = MappingProxyType({
    "public_low": "Public or low sensitivity",
    "personal_non_sensitive": "Personal but non-sensitive",
    "sensitive_personal": "Sensitive personal",
    "highly_sensitive_credential_bearing": "Highly sensitive or credential-bearing",
    "unreadable_unclassified": "Unreadable or unclassified",
})


def check_handling_class(value: object) -> str:
    return _check(value, HANDLING_CLASSES, "handling classes")


# --- §8.4: four operation modes ----------------------------------------------

#: "The product should support clear operation modes". Four, in the design's order.
OPERATION_MODES: tuple[str, ...] = (
    "offline", "local_model", "hybrid", "cloud_assisted",
)

#: The design's four sentences, verbatim. A paraphrase can promise less than the
#: original -- "Sensitive files remain local" is the whole of what `hybrid` promises --
#: so the words are pinned and a rewording is a failing test.
MODE_SEMANTICS: Mapping[str, str] = MappingProxyType({
    "offline":
        "No content leaves the device; only local rules and local models may run.",
    "local_model":
        "Local extraction plus a user-installed local LLM for eligible dossiers.",
    "hybrid":
        "Sensitive files remain local; non-sensitive bounded dossiers may use a "
        "cloud LLM.",
    "cloud_assisted":
        "User explicitly permits selected corpus areas to use a cloud model.",
})


def check_mode(value: object) -> str:
    return _check(value, OPERATION_MODES, "operation modes")


# --- §8.4: the always-local set ----------------------------------------------

#: "Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user
#: edits, group memberships, and raw sensitive values should remain local." Nine, in
#: the design's order. Nothing here can be named as a releasable item kind, and Task 7
#: turns an attempt into the `always_local_item` denial.
ALWAYS_LOCAL: tuple[str, ...] = (
    "paths", "complete_extracted_text", "ocr_output", "file_hashes", "image_exif",
    "gps", "user_edits", "group_memberships", "raw_sensitive_values",
)

# --- §8.4: the compact dossier -----------------------------------------------

#: "the engine should send only a compact dossier relevant to the current question:
#: selected excerpts, redacted identifiers, candidate labels, non-sensitive metadata,
#: and evidence references." Five from that sentence; `filename` is the sixth and is
#: the SPEC's flagged reading -- §8.4 puts *paths* in the always-local set, §7.7 puts
#: the filename in the residual dossier, and §7.3 forbids filenames in prompts only
#: for Protected Records, which is vacuous under any reading that forbade them
#: everywhere. Adopted because P8 and P11 cannot build without an answer; held open as
#: Open question 2 rather than treated as settled.
ITEM_KINDS: tuple[str, ...] = (
    "excerpt", "redacted_identifier", "candidate_label", "metadata_field",
    "evidence_reference", "filename",
)


def check_item_kind(value: object) -> str:
    return _check(value, ITEM_KINDS, "releasable item kinds")


# --- §8.4 + §7.3 + §8.6: the eight denial reasons ----------------------------

#: SPEC Contract out §6, in the SPEC's order. `dossier_over_budget` is a backstop that
#: should never fire: M9 puts the ceiling and §8.6's four-rung ladder in P8, BEFORE
#: the call, because a gate-only check runs after the last point at which the dossier
#: could still be reduced. A `dossier_over_budget` denial in a running pipeline is a
#: P8 defect to fix, not a normal outcome.
#:
#: There is no bare `protected` here. `protected_cloud_target` is a protected file
#: with a cloud target; `protected_records_template` is §7.3's residual template,
#: which "should normally remain local-only and must not cause filenames or content
#: to be exposed in model prompts". Collapsing either onto `protected` would produce
#: a denial that cannot say which rule fired.
DENIAL_REASONS: tuple[str, ...] = (
    "protected_cloud_target", "unclassified", "policy_revoked",
    "protected_records_template", "whole_document_requested",
    "dossier_over_budget", "always_local_item", "mode_forbids_target",
)


def check_denial_reason(value: object) -> str:
    return _check(value, DENIAL_REASONS, "denial reasons")


# --- §8.4: the four consent options ------------------------------------------

#: "If a model needs text containing sensitive content, the user should see that
#: requirement and choose whether to allow a local model, a cloud model, a redacted
#: prompt, or no model use." Those four, exactly. `NeedsConsent` is a question only
#: the user can answer, and no caller may absorb it into an abstention (B2).
CONSENT_OPTIONS: tuple[str, ...] = (
    "local_model", "cloud_model", "redacted_prompt", "no_model_use",
)

# --- §8.4: the five configurable display facets ------------------------------

#: "The user can choose whether names, previews, thumbnails, OCR text, or location
#: data are shown." Where the design is silent on a default, W1 makes the more
#: redacting option the default -- that rule is Task 6's and no default lives here.
DISPLAY_FACETS: tuple[str, ...] = (
    "names", "previews", "thumbnails", "ocr_text", "location_data",
)

#: SPEC §10's `display_settings`: "each shown | redacted". The value vocabulary for
#: the facet vocabulary above, and the ONE home for these two strings. They were
#: written three times under three names -- `REDACTION_VALUES` in `policy.py`,
#: `SETTING_VALUES` in Task 18, `REDACTION_VALUES` in a third section -- and Task 5's own
#: A7 asked for this home: "if Task 2 publishes them, `policy.py` re-exports and
#: deletes its own." `policy.py` re-exports; nothing else respells.
SHOWN: str = "shown"
REDACTED: str = "redacted"
REDACTION_VALUES: tuple[str, str] = (SHOWN, REDACTED)

# --- SPEC §2 and §7: bases, states and outcomes ------------------------------

#: SPEC §2's classification record: "basis  detector | safety_domain | user".
#: `safety_domain` is §3.15's: finance, identity, medical and legal material ship
#: first as safety domains, "meaning the system detects and protects them before any
#: cloud or automated placement decision is allowed". This is NOT P6's five-value
#: `origin` vocabulary (§3.1) and the two are never mapped onto one another here.
CLASSIFICATION_BASES: tuple[str, ...] = ("detector", "safety_domain", "user")

#: The one basis P7 itself writes: Task 16's reclassification records the user's own
#: act. Named rather than spelled at the call site -- brief §11, "never a bare string,
#: never an index" -- because `basis="user"` was a literal in five sections before it.
USER: str = "user"

# §3.13's six reliability states are `RELIABILITY_STATES`, imported at the top of
# this module from `evidence_shape.vocabulary` and re-exported unchanged. A second
# tuple holding the same six strings is the second home the named-constant rule
# exists to prevent, and a re-export means a P4 revision reaches P7 by import rather
# than by memory. P4's order is the design's line 50 read in sequence -- "A user
# confirmed fact ... A direct fact ... A validated fact ... An LLM-supported fact ...
# A possible fact ... A rejected fact" -- and Task 4 ranks against it. The states are
# taken from P4 and not P6 deliberately: `privacy` already binds `evidence_shape`,
# and D7 empties P7's Contract-in from P6, so P7 imports nothing from P6 at all.

#: The one state P7 itself writes, beside `USER`. Task 16's record is the only
#: classification P7 originates; the other five states are read, never written, and
#: membership in the tuple above is what reading needs. Spelled, not indexed: brief
#: §11 bans `USER_CONFIRMED` because it couples every consumer to the tuple's ORDER, and
#: a reorder would then change meanings with no test failing. The test asserts
#: membership in P4's tuple instead, so a P4 rename goes red here.
USER_CONFIRMED: str = "user_confirmed"

#: SPEC §7's audit record: "outcome  released | denied | consent_requested". Every
#: model call is recorded -- §8.4 says "Every model call" with no exemption for a
#: local model -- and denials and consent requests are recorded too, on §8.2's "Every
#: significant event affecting a file" and §8.6's requirement that the UI show what
#: has been deferred and why.
AUDIT_OUTCOMES: tuple[str, ...] = ("released", "denied", "consent_requested")


# --- the eleven questions the design leaves open -----------------------------

#: P7's SPEC Open questions 1-11, held open. An entry here means "still unanswered".
#: Task 21 reads this mapping and fails if any of them is answered in an
#: implementation instead of in a SPEC. Where the design leaves a value open -- a
#: threshold, a ceiling, an identifier class, a redaction transform, a detection rule,
#: a retention period -- this part holds a caller-supplied strategy or a required
#: keyword, never a number and never a list.
OPEN_QUESTIONS: Mapping[int, str] = MappingProxyType({
    1: "Is `protected` exactly the top two handling classes? §8.4 lists five classes "
       "and, separately, five kinds of material that enter a protected state "
       "immediately, without stating the relation. Neighbouring parts consume the "
       "flag and never infer it from the class.",
    2: "Filename versus path. §8.4 puts paths in the always-local set, §7.7 puts the "
       "filename in the residual dossier, and §7.3 forbids filenames in prompts only "
       "for Protected Records. The contract adopts the reading that makes §7.3 "
       "non-vacuous and flags it.",
    3: "What is a corpus area? `cloud_assisted` permits a cloud model for selected "
       "corpus areas. A scan root, a frozen tree node, an accepted group, a domain? "
       "Consent grants cannot be scoped until this is named.",
    4: "Deletion versus append-only. §8.4 gives the user the right to review and "
       "delete local derived data; §8.2 forbids updating or deleting an event. "
       "Which wins, what counts as derived, and are audit records themselves "
       "deletable? Tracked as I6.",
    5: "Does `unreadable_unclassified` permit a LOCAL model call? Reading escalation "
       "strictly denies local calls on unclassified files, which may block exactly "
       "the OCR-opaque screenshots §2.7 and §7.8 want a model to interpret.",
    6: "Is a local-model call a consent event or only an audit event? §8.4 audits "
       "every model call and offers a local model as one of the four consent "
       "options. The threshold at which a local call needs a prompt is unstated.",
    7: "Does repeated reclassification generalize? §8.7 allows a repeated residual "
       "destination to become a corpus-level preference; it does not say whether "
       "repeated privacy corrections may raise a sensitivity floor.",
    8: "May a replay bundle carry audit records and excerpt spans? §8.5 allows a "
       "metadata-safe representation and lists policy settings; whether a bundle "
       "intended to leave the machine may carry records that name excerpts is "
       "unstated.",
    9: "What is an external connector besides a model? §8.4 gates any model or "
       "external connector, but no non-model connector is named in the twelve parts. "
       "If one is added later, does it route through `Gate.release`?",
    10: "Retention. How long audit records, consent grants and superseded "
        "classifications are kept. The design states no retention period anywhere.",
    11: "Which of `offline` and `local_model` ships as the install default. W1 closes "
        "the floor -- the default must be one of those two and may never be `hybrid` "
        "or `cloud_assisted` -- and the design names no answer between them.",
})
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_vocabulary.py -v`
Expected: PASS — 33 passed

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–2 green, and every pre-existing test still green.

- [ ] **Step 6: Commit**

```bash
git add src/privacy/vocabulary.py tests/p7/test_p7_vocabulary.py
git commit -m "feat(P7): the closed vocabularies, one home for shown|redacted, P4's six reliability states re-exported, and the five strings that share the stem protected"
```

---

### Task 3: The classification record, and absence resolving to `unreadable_unclassified`

**Files:**
- Create: `src/privacy/classification.py`
- Test: `tests/p7/test_p7_classification.py`

**Interfaces:**
- Consumes: `privacy.vocabulary.CLASSIFICATION_BASES`, `.check_handling_class(value) -> str`,
  `.OutOfVocabulary`; `evidence_shape.observation.observation_key(*, content_hash, extractor_name,
  locator, raw_value) -> str`; `evidence_shape.store.runs_for_file(conn, file_id) ->
  list[ExtractionRun]`; `extractors.long_tail.POTENTIALLY_SENSITIVE: str`,
  `.sensitivity_signals_for(conn, run_id) -> list[sqlite3.Row]`;
  `evidence_shape.runs.COMPLETENESS` — consumed **in the test**, as the cross-check that the
  nine-value table names P4's nine and no tenth.
- Produces (`classification.py`):
  - `ClassificationRecord` — frozen: `file_id: str`, `content_hash: str`, `handling_class: str`,
    `protected: bool`, `basis: str`, `evidence_refs: tuple[str, ...]`, `reliability_state: str`,
    `observed_at: str`.
  - `CLASSIFICATION_FIELDS: tuple[str, ...]` — SPEC §2's eight, in SPEC §2's order.
  - `UnbackedClassification`.
  - `resolve_class(record: ClassificationRecord | None) -> str`.
  - `completeness_implies_unclassified(completeness) -> bool`.
  - `COMPLETENESS_RULE: Mapping[str, tuple[bool, str]]` (added — see below).
  - `sensitivity_signal_keys(conn, file_id) -> tuple[str, ...]` (added — see below).

**Done-means:** 2 (first half), and the input side of 6.

**Two readings of the `Consumes` block, stated so a reviewer can reject them rather than discover
them.** The skeleton lists `vocabulary.HANDLING_CLASSES` and `.CLASSIFICATION_BASES`. This module
imports `CLASSIFICATION_BASES` directly and reaches `HANDLING_CLASSES` **through Task 2's published
`check_handling_class`**, which is the checker over that exact tuple; importing both would give this
module two ways to say the same no, which is what Task 2's *"four checkers, not nine"* paragraph
argues against. `OutOfVocabulary` comes with them, because consuming a closed vocabulary without its
refusal type forces a second refusal vocabulary. Both are Task 2 products already in Task 2's
`Produces` list, so no new surface is created. The skeleton also lists
`evidence_shape.runs.COMPLETENESS`; the module deliberately does **not** import it, because the
requirement is that the mapping be *"stated explicitly per value rather than by an `in`-check over a
set the author guessed"* and deriving the table from P4's tuple is that `in`-check wearing a better
name. The tuple is consumed in the **test**, as the cross-check that the table covers P4's nine and
no tenth.

**`ClassificationRecord` is authoritative and it is keyed on bytes (D2).**
`(file_id, content_hash)` — on the hash, because *a classification is about BYTES* and new bytes at
a path are a new file version that inherits nothing. `files.sensitivity_state` is the projection of
this record onto the current row, and **this module does not write it**. Task 4 owns `mirror_state`
and P1's `set_sensitivity_state`; Task 3 owns the record. That split is not tidiness — it is what
keeps the next paragraph true.

**`Unreadable or unclassified` is a gate outcome and this is the module where that becomes
concrete.** `resolve_class` returns a string to a caller. There is no writer in this file: no
function takes a connection and inserts or updates, no name begins `set_`, `write_`, `record_`,
`mirror_` or `update_`, and `database_agent.files_table` is not imported. A test asserts each of
those by walking the module namespace. The reason is D2's: *"nothing has looked"* and *"this file
carries nothing"* must never be the same value in the same column, and the only durable way to hold
that apart is for the string that means the first to be produced by a decision function and by
nothing that can reach a column.

**The detector is unwritten, and the strongest available proof of that is a test.** D2 puts the rule
set behind an injection and no task in any plan produces one. Until one is supplied, every real file
resolves to `Denied(unclassified)`. The test that says so is
`test_a_file_with_every_value_marked_sensitive_still_has_no_classification`: P5 marks a value
`potentially sensitive` at emission, the signal is in the database, `sensitivity_signal_keys` returns
its `observation_key` — and the file still has no `ClassificationRecord`, so `resolve_class(None)`
still returns `unreadable_unclassified`. **A signal is not a class.** P5's own docstring says so:
*"Email addresses, message content and every VCF value are marked POTENTIALLY SENSITIVE at emission,
for P7 to act on. P5 assigns no handling class: section 8.4 gives classification to P7."*

**`sensitivity_signal_keys` is added, and it is not a detector.** Task 3's `Consumes` block lists
`POTENTIALLY_SENSITIVE`, `sensitivity_signals_for` and `runs_for_file` and its `Produces` block names
nothing that could consume them — an interface block with three unconsumed imports is incoherent. The
skeleton's prose settles the intent: *"The reader is keyed by `run_id` only, so the file-level walk is
`runs_for_file(conn, file_id)` → `sensitivity_signals_for(conn, run.run_id)`. P7 adds no reader to P5;
it composes the two P4 and P5 already publish."* The composition decides nothing: it applies no rule,
assigns no class, and returns the citation handles a detector would pass as `evidence_refs`. It
deduplicates while preserving first-seen order, because a re-run of the same extractor at the same
content hash produces the same `observation_key`, and the same key listed twice would make a
classification look doubly backed by one observation.

**`evidence_refs` holds `observation_key` values and refuses anything shaped like an
`observation_id` (M14).** *"The key, not the id, is what makes that durable"* — a per-row
`observation_id` dies when the extractor is upgraded, so a negative example recorded today would
silently stop resolving and the same false protection would return. The shape check is **derived from
P4's own function** rather than hard-coded: the module mints one probe key at import and reads the
algorithm prefix and digest length off it, so a change in `evidence_shape.canonical.sha256_of`
propagates instead of drifting. It was introspected: `observation_key(...)` returns
`"sha256:" + 64 lowercase hex` (71 characters) and `evidence_shape.store.new_id()` — the minter of
`observation_id` — returns `str(uuid.uuid4())`, so the two handles are mechanically
distinguishable. P1's `content_hash` carries **no** algorithm prefix, which the test also pins.

**`evidence_refs` is required non-empty for `basis = "detector"` and for that basis only.** SPEC §2:
*"`evidence_refs` is non-empty for any `basis = detector` classification"*, on §3.1's principle that
every fact preserves where it came from. `basis = "user"` needs none — the user's act is the
evidence, and §8.4 makes the classification *"revised by the user"* a first-class outcome.
`basis = "safety_domain"` needs none either: §3.15's four domains are *"implemented first as safety
domains, meaning the system detects and protects them before any cloud or automated placement
decision is allowed"*, which is a rule about a domain and not a reading of a span. Requiring evidence
there would be inventing a stricter rule than the SPEC states.

**`protected` is a boolean the caller supplies and this module never derives it.** SPEC §2:
*"Neighbouring parts should consume the `protected` flag, not infer it from the class."* Whether
`protected` is exactly co-extensive with the top two classes is Open question 1, unsettled and not
settled by D2. A record with `handling_class = "public_low"` and `protected = True` constructs, and so
does its opposite; the test asserts both, and asserts the module publishes no function mapping one to
the other.

**`reliability_state` is stored and not validated here.** §3.13's six are **P4's**, shipped as
`evidence_shape.vocabulary.RELIABILITY_STATES` and re-exported by Task 2, and Task 4 publishes
`RELIABILITY_ORDER` and the `strongest` resolution over it. Validating in two places invites two
vocabularies, which is the defect this part is most exposed to. This module requires it to be a
non-empty string and stores it. Where a test needs the one state P7 writes, it uses Task 2's
`USER_CONFIRMED` rather than the literal — brief §11, *"never a bare string, never an index"*.

**`COMPLETENESS_RULE` is added because the requirement is a per-value statement.** Nine entries, in
P4's order, each carrying `(implies_unclassified, the sentence that decides it)`. An unpublished
internal frozenset **is** the *"set the author guessed"* the skeleton forbids; a published table with
a citation per value is not. The test cross-checks the six `True` values against P4's own
`evidence_shape.vocabulary.ZERO_OBSERVATION_COMPLETENESS` — `("unsupported", "deferred", "failed",
"metadata_only", "dataless")`, five values where *"nothing was opened, so nothing was seen"* — plus
`unreadable`, which is §2.9's *"indexed-but-unreadable"* and which M3 keeps carrying metadata-level
rows. That cross-check is what makes the table grounded rather than asserted.

**One factual correction to the skeleton, applied here.** The skeleton's Task 3 paragraph says
*"the case of a file with **no run row at all**, which is what a dataless file has."* The skeleton's
own refusal table says the opposite and is right: a dataless file gets **one run row**,
`completeness = dataless`, *"recording that the bytes are elsewhere"*; it is a file inside a
**protected container** that has no row — and no `files` row either, so the gate cannot be asked
about it at all. Both cases are covered: `completeness_implies_unclassified("dataless") is True`
covers the run row, and `resolve_class(None)` covers every file with no classification, including one
with no runs. Reported.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_classification.py
"""SPEC §2's record, and the one resolution the design states twice.

"Absence of a classification resolves to `unreadable_unclassified`, never to
`public_low`." §8.6 says why: "Cost exhaustion must never turn into lower-quality
automatic classification." The failure that sentence forbids is precisely defaulting
an unclassified file to public so the pipeline can continue, and the tests below are
written to fail if any input at all produces `public_low` without a record saying so.

The second thing proved here is D2's: `Unreadable or unclassified` is a GATE OUTCOME.
This module returns it to a caller and cannot write it anywhere, and the namespace
tests are what keep that true when someone later needs a shortcut.
"""
import dataclasses
import json
import re
import uuid

import pytest

from database_agent.files_table import get_file, record_file

from evidence_shape.observation import observation_key
from evidence_shape.runs import COMPLETENESS, ExtractionRun
from evidence_shape.store import record_run
from evidence_shape.vocabulary import ZERO_OBSERVATION_COMPLETENESS

from extractors.long_tail import (
    POTENTIALLY_SENSITIVE, SensitivitySignal, record_sensitivity_signals,
)

import privacy.classification as classification
from privacy.classification import (
    CLASSIFICATION_FIELDS, COMPLETENESS_RULE, ClassificationRecord,
    UnbackedClassification, completeness_implies_unclassified, resolve_class,
    sensitivity_signal_keys,
)
from privacy.vocabulary import (
    CLASSIFICATION_BASES, HANDLING_CLASSES, OutOfVocabulary, USER, USER_CONFIRMED,
)

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"


@pytest.fixture()
def file_id(p7_conn, tmp_path):
    """A real P1 row. The record is keyed on (file_id, content_hash) and a synthesized
    pair would not exercise the identity D2 makes authoritative."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    document = corpus / "passport-scan.pdf"
    document.write_bytes(b"%PDF-1.4 fixture bytes")
    return record_file(
        p7_conn, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=".pdf",
        observed_size=document.stat().st_size,
        observed_timestamps=json.dumps({"mtime": 1.0}),
        parent_folder_context=str(corpus), mime_type="application/pdf",
        detected_format="pdf", scan_state="fixture-scan-state", materialized=True)


@pytest.fixture()
def content_hash(p7_conn, file_id):
    return get_file(p7_conn, file_id)["content_hash"]


def a_key(content_hash, raw_value="Passport No. X", locator="zone=body/page=1"):
    return observation_key(content_hash=content_hash, extractor_name="pdf_text",
                           locator=locator, raw_value=raw_value)


def a_record(file_id, content_hash, **over):
    fields = dict(file_id=file_id, content_hash=content_hash,
                  handling_class="highly_sensitive_credential_bearing",
                  protected=True, basis="detector",
                  evidence_refs=(a_key(content_hash),),
                  reliability_state="validated", observed_at=FIXED_CLOCK)
    fields.update(over)
    return ClassificationRecord(**fields)


def a_run(file_id, content_hash, run_id="run-1", completeness="complete"):
    return ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="pdf_text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native",
        config={"reader": "injected"}, completeness=completeness,
        started_at=FIXED_CLOCK, observation_count=1, finished_at=FIXED_CLOCK)


# --- SPEC §2's eight fields ---------------------------------------------------

def test_the_eight_fields_are_specs_eight_in_specs_order():
    assert CLASSIFICATION_FIELDS == (
        "file_id", "content_hash", "handling_class", "protected", "basis",
        "evidence_refs", "reliability_state", "observed_at",
    )
    assert tuple(f.name for f in dataclasses.fields(ClassificationRecord)) == \
        CLASSIFICATION_FIELDS


def test_the_record_is_frozen(file_id, content_hash):
    record = a_record(file_id, content_hash)
    with pytest.raises(dataclasses.FrozenInstanceError):
        record.handling_class = "public_low"


def test_the_record_is_keyed_on_bytes_not_on_a_path(file_id, content_hash):
    # D2: "keyed on the hash because a classification is about BYTES, and new bytes at
    # a path are a new file version that inherits nothing."
    old = a_record(file_id, content_hash)
    new = a_record(file_id, "0" * 64, evidence_refs=(a_key("0" * 64),))
    assert old.file_id == new.file_id
    assert old != new
    assert (old.file_id, old.content_hash) != (new.file_id, new.content_hash)


def test_a_sequence_of_refs_is_frozen_on_the_way_in(file_id, content_hash):
    record = a_record(file_id, content_hash, evidence_refs=[a_key(content_hash)])
    assert isinstance(record.evidence_refs, tuple)


def test_a_bare_string_is_not_a_sequence_of_refs(file_id, content_hash):
    # tuple("sha256:...") is 71 one-character refs. Refusing the string is the only
    # way that mistake is visible.
    with pytest.raises(UnbackedClassification):
        a_record(file_id, content_hash, evidence_refs=a_key(content_hash))


# --- evidence-backed (§8.4) ---------------------------------------------------

def test_a_detector_record_with_no_evidence_is_unbacked(file_id, content_hash):
    # §8.4: the classification "is itself evidence-backed". §3.1's principle: every
    # fact preserves where it came from.
    with pytest.raises(UnbackedClassification) as caught:
        a_record(file_id, content_hash, evidence_refs=())
    assert "detector" in str(caught.value)


def test_a_user_record_and_a_safety_domain_record_need_no_evidence(
        file_id, content_hash):
    # The SPEC scopes the rule to one basis: "evidence_refs is non-empty for any
    # basis = detector classification". The user's act is the evidence (§8.4's
    # "revised by the user"); a safety domain is §3.15's rule about a domain, not a
    # reading of a span. Requiring evidence here would invent a stricter rule.
    assert a_record(file_id, content_hash, basis=USER,
                    evidence_refs=(), reliability_state=USER_CONFIRMED)
    assert a_record(file_id, content_hash, basis="safety_domain", evidence_refs=())


def test_evidence_refs_must_be_observation_keys_and_not_observation_ids(
        file_id, content_hash):
    # M14: "The key, not the id, is what makes that durable." A per-row
    # observation_id dies on extractor upgrade, so a negative example recorded today
    # would silently stop resolving. `evidence_shape.store.new_id()` mints uuid4.
    with pytest.raises(UnbackedClassification) as caught:
        a_record(file_id, content_hash, evidence_refs=(str(uuid.uuid4()),))
    assert "observation_key" in str(caught.value)


def test_a_content_hash_is_not_an_observation_key(file_id, content_hash):
    # P1's content_hash carries no algorithm prefix; P4's key does. Introspected.
    assert ":" not in content_hash
    assert a_key(content_hash).startswith("sha256:")
    with pytest.raises(UnbackedClassification):
        a_record(file_id, content_hash, evidence_refs=(content_hash,))


def test_a_truncated_or_uppercased_key_is_refused(file_id, content_hash):
    real = a_key(content_hash)
    for bad in (real[:-1], real.upper(), real.replace("sha256", "sha512"), "", None):
        with pytest.raises(UnbackedClassification):
            a_record(file_id, content_hash, evidence_refs=(bad,))


def test_a_real_p4_key_is_accepted_and_survives_an_extractor_version_change(
        file_id, content_hash):
    # MINOR 8: `observation_key` deliberately excludes extractor_version, which is
    # what lets a classification survive an upgrade.
    key = a_key(content_hash)
    assert a_record(file_id, content_hash, evidence_refs=(key,)).evidence_refs == (key,)


# --- the closed vocabularies -------------------------------------------------

def test_an_out_of_vocabulary_handling_class_is_refused(file_id, content_hash):
    with pytest.raises(OutOfVocabulary):
        a_record(file_id, content_hash, handling_class="secret")


def test_p6s_origin_vocabulary_is_not_p7s_basis_vocabulary(file_id, content_hash):
    # P6's five §3.1 origins include "rule" and "LLM interpretation"; P7's basis is
    # three values. The two are never mapped onto one another.
    assert CLASSIFICATION_BASES == ("detector", "safety_domain", "user")
    with pytest.raises(OutOfVocabulary):
        a_record(file_id, content_hash, basis="rule")


def test_reliability_state_is_stored_and_not_validated_here(file_id, content_hash):
    # §3.13's six are P4's -- `evidence_shape.vocabulary.RELIABILITY_STATES`, which
    # Task 2 re-exports -- and Task 4 publishes the ordering. Two validators would be
    # two vocabularies. Non-empty is the only requirement this module makes.
    assert a_record(file_id, content_hash,
                    reliability_state="llm_supported").reliability_state == \
        "llm_supported"
    with pytest.raises(UnbackedClassification):
        a_record(file_id, content_hash, reliability_state="")


def test_protected_is_a_boolean_and_is_never_derived_from_the_class(
        file_id, content_hash):
    # Open question 1: "Is `protected` exactly the top two handling classes?" The
    # design lists five classes and, separately, five kinds of material that enter a
    # protected state, without stating the relation. Both combinations construct.
    assert a_record(file_id, content_hash,
                    handling_class="public_low", protected=True).protected is True
    assert a_record(file_id, content_hash,
                    handling_class="highly_sensitive_credential_bearing",
                    protected=False).protected is False
    with pytest.raises(UnbackedClassification):
        a_record(file_id, content_hash, protected="yes")


def test_no_function_here_maps_a_class_onto_the_protected_flag():
    names = [n for n in vars(classification) if not n.startswith("_")]
    assert not [n for n in names if "protect" in n.lower() and callable(
        getattr(classification, n))]


# --- resolve_class: the one resolution the design states twice ---------------

def test_absence_resolves_to_unreadable_unclassified():
    assert resolve_class(None) == "unreadable_unclassified"


def test_no_input_at_all_produces_public_low_without_a_record_saying_so(
        file_id, content_hash):
    # §8.6: "Cost exhaustion must never turn into lower-quality automatic
    # classification." There is no default-to-public code path anywhere.
    assert resolve_class(None) != "public_low"
    for name in HANDLING_CLASSES:
        record = a_record(file_id, content_hash, handling_class=name)
        assert resolve_class(record) == name
    produced = {resolve_class(None)} | {
        resolve_class(a_record(file_id, content_hash, handling_class=n))
        for n in HANDLING_CLASSES if n != "public_low"}
    assert "public_low" not in produced


def test_resolve_class_refuses_something_that_is_not_a_record():
    for wrong in ({"handling_class": "public_low"}, "public_low", 0, ()):
        with pytest.raises(TypeError):
            resolve_class(wrong)


# --- D2: a gate outcome, and therefore no writer in this module --------------

def test_this_module_contains_no_writer():
    # "Unreadable or unclassified is a GATE OUTCOME, not a file fact." It must never
    # reach `files.sensitivity_state`, and the durable guarantee is that the string is
    # produced by a decision function in a module that can reach no column.
    forbidden = ("set_", "write_", "record_", "mirror_", "update_", "insert_")
    for name, value in vars(classification).items():
        if name.startswith("_") or not callable(value):
            continue
        assert not name.startswith(forbidden), name
    assert "set_sensitivity_state" not in vars(classification)
    for name, value in vars(classification).items():
        assert getattr(value, "__module__", "") != "database_agent.files_table", name


def test_the_only_connection_taking_function_here_reads(p7_conn, file_id):
    assert "conn" not in resolve_class.__code__.co_varnames
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    sensitivity_signal_keys(p7_conn, file_id)
    assert p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"] == before
    assert get_file(p7_conn, file_id)["sensitivity_state"] is None


# --- COMPLETENESS_RULE: stated per value, cross-checked against P4 -----------

def test_the_rule_names_p4s_nine_values_and_no_tenth():
    assert tuple(COMPLETENESS_RULE) == COMPLETENESS
    assert len(COMPLETENESS_RULE) == 9


def test_every_value_carries_the_sentence_that_decides_it():
    for name, (implies, reason) in COMPLETENESS_RULE.items():
        assert isinstance(implies, bool), name
        assert isinstance(reason, str) and reason.strip(), name


def test_the_six_that_imply_unclassified_are_p4s_five_plus_unreadable():
    # Grounded against P4's own tuple rather than against a set this author guessed:
    # ZERO_OBSERVATION_COMPLETENESS is where "nothing was opened, so nothing was
    # seen", and `unreadable` is §2.9's "indexed-but-unreadable", which the SPEC maps
    # to this class by name.
    implied = {n for n, (yes, _) in COMPLETENESS_RULE.items() if yes}
    assert implied == set(ZERO_OBSERVATION_COMPLETENESS) | {"unreadable"}
    assert len(implied) == 6


def test_the_three_that_do_not_are_the_ones_where_content_was_read():
    assert {n for n, (yes, _) in COMPLETENESS_RULE.items() if not yes} == \
        {"complete", "capped", "partial"}
    for name in ("complete", "capped", "partial"):
        assert completeness_implies_unclassified(name) is False


def test_a_dataless_run_row_implies_unclassified(p7_conn, file_id, content_hash):
    # 11 §5: "Do not materialize, hash, or extract." A dataless file gets ONE run row
    # recording that the bytes are elsewhere -- it is a file inside a protected
    # container that has no row at all, and no `files` row either, so the gate cannot
    # be asked about it. Both cases end at `unreadable_unclassified`, by two routes.
    record_run(p7_conn, a_run(file_id, content_hash, completeness="dataless"))
    assert completeness_implies_unclassified("dataless") is True
    assert resolve_class(None) == "unreadable_unclassified"


def test_an_unknown_completeness_value_is_refused():
    for wrong in ("indexed-but-unreadable", "empty", "", None, 1):
        with pytest.raises(OutOfVocabulary):
            completeness_implies_unclassified(wrong)


# --- sensitivity_signal_keys: a detector input, and not a detector -----------

def test_signal_keys_are_p4_keys_in_run_then_emit_order(
        p7_conn, file_id, content_hash):
    record_run(p7_conn, a_run(file_id, content_hash, run_id="run-1"))
    record_run(p7_conn, a_run(file_id, content_hash, run_id="run-2"))
    first = a_key(content_hash, raw_value="Passport No. X")
    second = a_key(content_hash, raw_value="a@b.example", locator="zone=body/page=2")
    record_sensitivity_signals(
        p7_conn, run_id="run-1",
        signals=(SensitivitySignal(0, POTENTIALLY_SENSITIVE, "vcf value"),),
        observation_keys=(first,), now=FIXED_CLOCK)
    record_sensitivity_signals(
        p7_conn, run_id="run-2",
        signals=(SensitivitySignal(0, POTENTIALLY_SENSITIVE, "email address"),),
        observation_keys=(second,), now=FIXED_CLOCK)
    assert sensitivity_signal_keys(p7_conn, file_id) == (first, second)


def test_a_file_with_every_value_marked_sensitive_still_has_no_classification(
        p7_conn, file_id, content_hash):
    # THE test for D2's open posture. P5's docstring: "P5 assigns no handling class:
    # section 8.4 gives classification to P7." The detector is unwritten, so a file
    # covered in signals is still unclassified and the gate still denies it.
    record_run(p7_conn, a_run(file_id, content_hash))
    record_sensitivity_signals(
        p7_conn, run_id="run-1",
        signals=(SensitivitySignal(0, POTENTIALLY_SENSITIVE, "vcf value"),),
        observation_keys=(a_key(content_hash),), now=FIXED_CLOCK)
    assert sensitivity_signal_keys(p7_conn, file_id)
    assert resolve_class(None) == "unreadable_unclassified"
    assert get_file(p7_conn, file_id)["sensitivity_state"] is None


def test_signal_keys_deduplicates_across_runs(p7_conn, file_id, content_hash):
    # A re-run of the same extractor at the same content hash produces the same key
    # (MINOR 8). Listing it twice would make one observation look like two.
    same = a_key(content_hash)
    for run_id in ("run-1", "run-2"):
        record_run(p7_conn, a_run(file_id, content_hash, run_id=run_id))
        record_sensitivity_signals(
            p7_conn, run_id=run_id,
            signals=(SensitivitySignal(0, POTENTIALLY_SENSITIVE, "vcf value"),),
            observation_keys=(same,), now=FIXED_CLOCK)
    assert sensitivity_signal_keys(p7_conn, file_id) == (same,)


def test_signal_keys_is_empty_for_a_file_with_no_runs(p7_conn, file_id):
    assert sensitivity_signal_keys(p7_conn, file_id) == ()


def test_signal_keys_ignores_a_signal_that_is_not_p5s(
        p7_conn, file_id, content_hash):
    record_run(p7_conn, a_run(file_id, content_hash))
    key = a_key(content_hash)
    p7_conn.execute(
        "INSERT INTO extraction_sensitivity_signal (run_id, observation_key, signal, "
        "basis, observed_at) VALUES (?, ?, ?, ?, ?)",
        ("run-1", key, "something else", "unknown", FIXED_CLOCK))
    assert sensitivity_signal_keys(p7_conn, file_id) == ()


def test_this_module_publishes_no_detector():
    # SPEC Deferred: "The design states *what* is protected and never *how it is
    # recognised*." No regex, no gazetteer, no filename pattern, no keyword list.
    for name, value in vars(classification).items():
        if name.startswith("_"):
            continue
        assert not isinstance(value, re.Pattern), name
        assert "detect" not in name.lower(), name
        assert "classify" not in name.lower(), name
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_classification.py -v`
Expected: FAIL — `ImportError: cannot import name 'CLASSIFICATION_FIELDS' from
'privacy.classification'`, because `src/privacy/classification.py` does not exist yet and collection
fails on the first import. Tasks 1 and 2 are green, so `privacy`, `privacy.authorship` and
`privacy.vocabulary` all import.

- [ ] **Step 3: Write `src/privacy/classification.py`**

```python
# src/privacy/classification.py
"""SPEC §2's classification record, and the resolution the design states twice.

"Absence of a classification resolves to `unreadable_unclassified`, never to
`public_low`." §8.6 gives the reason: "Cost exhaustion must never turn into
lower-quality automatic classification." The failure that sentence forbids is exactly
defaulting an unclassified file to public so the pipeline can continue, so there is no
default-to-public code path in this module or anywhere under `src/privacy/`.

**The record is authoritative and it is keyed on BYTES (D2).** `(file_id,
content_hash)` -- on the hash, because a classification is about the bytes, and new
bytes at a path are a new file version that inherits nothing.
`files.sensitivity_state` is this record's PROJECTION onto the current row, written
through P1's published `set_sensitivity_state`; that is Task 4's `mirror_state`, and
it is not here.

**`Unreadable or unclassified` is a GATE OUTCOME, not a file fact (D2), and this
module is where that becomes concrete.** `resolve_class` returns a string to a caller
and this file contains no writer at all: no function inserts or updates, no name
begins `set_`, `write_`, `record_`, `mirror_` or `update_`, and
`database_agent.files_table` is not imported. "Nothing has looked" and "this file
carries nothing" must never become the same value in the same column, and the durable
way to hold them apart is for the string meaning the first to be produced by a
decision function in a module that can reach no column.

**No detector lives here (D2).** SPEC *Deferred*: "The design states *what* is
protected and never *how it is recognised*. The detector rule set, its signals, and
its thresholds are hand-authored. P7 publishes the vocabulary the detectors write
into." There is no regex, no gazetteer, no filename pattern and no keyword list.
`sensitivity_signal_keys` composes two readers P4 and P5 already publish and decides
nothing: it returns the citation handles a detector would pass as `evidence_refs`.
Until a detector is supplied, every real file resolves to `Denied(unclassified)` --
a correct, locked door with nobody holding a key, and the honest v1 posture.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType

from evidence_shape.observation import observation_key
from evidence_shape.store import runs_for_file

from extractors.long_tail import POTENTIALLY_SENSITIVE, sensitivity_signals_for

from privacy.vocabulary import (
    CLASSIFICATION_BASES, OutOfVocabulary, check_handling_class,
)

#: SPEC §2's eight, in SPEC §2's order.
CLASSIFICATION_FIELDS: tuple[str, ...] = (
    "file_id", "content_hash", "handling_class", "protected", "basis",
    "evidence_refs", "reliability_state", "observed_at",
)

#: §8.4's fifth class, validated against Task 2's closed vocabulary at import: a
#: rename there becomes an ImportError here rather than a string that silently stops
#: matching. Private, because it is a value this module RETURNS and never stores.
_UNREADABLE_UNCLASSIFIED: str = check_handling_class("unreadable_unclassified")

#: The one basis §8.4's "evidence-backed" binds. `user` needs no evidence -- the
#: user's act is the evidence -- and `safety_domain` is §3.15's rule about a domain,
#: not a reading of a span.
_EVIDENCE_REQUIRED_BASIS: str = "detector"

#: M14's citation handle, shaped by asking P4 rather than by hard-coding a pattern.
#: One probe key at import yields the algorithm prefix and the digest width, so a
#: change in `evidence_shape.canonical.sha256_of` propagates instead of drifting.
_PROBE_KEY: str = observation_key(
    content_hash="", extractor_name="", locator="", raw_value="")
_KEY_PREFIX, _, _KEY_DIGEST = _PROBE_KEY.partition(":")
_HEX = frozenset("0123456789abcdef")


class UnbackedClassification(ValueError):
    """§8.4: the classification "is itself evidence-backed".

    Raised when a `detector` classification carries no evidence, when a reference is
    not a P4 `observation_key` (M14), or when a field of the record is not the kind of
    value §8.2 can preserve.
    """


def _is_observation_key(value: object) -> bool:
    """P4's content-addressed handle, never the per-row `observation_id` (M14).

    `evidence_shape.store.new_id()` mints `str(uuid.uuid4())` and P1's `content_hash`
    carries no algorithm prefix, so both are rejected by shape rather than by policy.
    """
    if not isinstance(value, str):
        return False
    prefix, separator, digest = value.partition(":")
    if not separator or prefix != _KEY_PREFIX or len(digest) != len(_KEY_DIGEST):
        return False
    return all(character in _HEX for character in digest)


@dataclass(frozen=True, slots=True)
class ClassificationRecord:
    """One handling class for one file VERSION. D2 makes this record authoritative.

    `protected` is supplied and never derived: SPEC §2, "Neighbouring parts should
    consume the `protected` flag, not infer it from the class", and Open question 1 --
    whether `protected` is exactly the top two classes -- is unsettled.

    `reliability_state` is P4's vocabulary (§3.13's six, shipped as
    `evidence_shape.vocabulary.RELIABILITY_STATES` and re-exported by Task 2) and is
    stored, not validated: Task 4 publishes the ordering and the `strongest`
    resolution over it, and two validators would be two vocabularies.
    """

    file_id: str
    content_hash: str
    handling_class: str
    protected: bool
    basis: str
    evidence_refs: tuple[str, ...]
    reliability_state: str
    observed_at: str

    def __post_init__(self) -> None:
        for name in ("file_id", "content_hash", "reliability_state", "observed_at"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise UnbackedClassification(
                    f"{name} must be a non-empty string; §8.2 preserves a record and "
                    f"cannot preserve {value!r}")
        check_handling_class(self.handling_class)
        if self.basis not in CLASSIFICATION_BASES:
            raise OutOfVocabulary(
                f"basis {self.basis!r} is not one of {CLASSIFICATION_BASES}. P6's "
                "five §3.1 `origin` values are a different vocabulary and are never "
                "mapped onto this one.")
        if not isinstance(self.protected, bool):
            raise UnbackedClassification(
                f"protected is §8.4's flag and is a boolean, not {self.protected!r}. "
                "It is supplied by the caller and never derived from the handling "
                "class (SPEC §2, Open question 1).")
        refs = self.evidence_refs
        if isinstance(refs, str) or not isinstance(refs, Sequence):
            raise UnbackedClassification(
                "evidence_refs is a sequence of P4 observation keys; a bare string "
                f"would become {len(refs) if isinstance(refs, str) else 0} "
                "one-character references")
        refs = tuple(refs)
        object.__setattr__(self, "evidence_refs", refs)
        if self.basis == _EVIDENCE_REQUIRED_BASIS and not refs:
            raise UnbackedClassification(
                f"a basis={_EVIDENCE_REQUIRED_BASIS!r} classification carries no "
                "evidence. §8.4: the classification 'is itself evidence-backed', on "
                "§3.1's principle that every fact preserves where it came from.")
        for ref in refs:
            if not _is_observation_key(ref):
                raise UnbackedClassification(
                    f"{ref!r} is not a P4 observation_key. M14: 'The key, not the id, "
                    "is what makes that durable' -- a per-row observation_id dies on "
                    "extractor upgrade, so a negative example recorded today would "
                    "silently stop resolving and the same false protection would "
                    "return.")


def resolve_class(record: ClassificationRecord | None) -> str:
    """The handling class a caller must treat this file version as carrying.

    A GATE OUTCOME (D2), returned to a caller and stored by nothing here. Absence
    resolves to `unreadable_unclassified` and never to `public_low` (SPEC §1, §8.4,
    §8.6): a file that has not been classified has not met §8.4's precondition for
    escalation -- "classify data into handling classes before LLM escalation" -- and
    the gate denies it rather than guessing at it downward.
    """
    if record is None:
        return _UNREADABLE_UNCLASSIFIED
    if not isinstance(record, ClassificationRecord):
        raise TypeError(
            f"resolve_class takes a ClassificationRecord or None, not "
            f"{type(record).__name__}. A mapping that looks like one has not been "
            "through the evidence-backed check.")
    return record.handling_class


#: Per value, with the sentence that decides it, for each of P4's nine
#: `completeness` markings. Stated one at a time rather than as a membership test over
#: a set, because the set is what an author guesses and the sentences are what the
#: design says. Six imply unclassified; they are P4's own
#: ZERO_OBSERVATION_COMPLETENESS plus `unreadable`, and the test cross-checks that.
COMPLETENESS_RULE: Mapping[str, tuple[bool, str]] = MappingProxyType({
    "complete": (False,
        "The run finished on its own terms and the content was read. Whether a "
        "classification EXISTS is a separate question this function does not answer."),
    "capped": (False,
        "§2.7 requires that 'whether extraction was complete or capped' be preserved. "
        "Capped text exists and a detector can read it."),
    "partial": (False,
        "§2.5's 'partially inspected'. M3 keeps the metadata-level rows on a partial "
        "run, so content was read."),
    "metadata_only": (True,
        "In P4's ZERO_OBSERVATION_COMPLETENESS: the stopping extractor emits nothing "
        "and the file stays indexed through its filesystem observations. No content "
        "was read, so no evidence-backed classification is possible."),
    "deferred": (True,
        "§8.6: 'If the budget is exhausted, the product should retain extracted "
        "evidence, mark the deferred stage, and leave the file or group in review "
        "rather than guessing.' The stage did not run."),
    "unsupported": (True,
        "§2.4: 'an empty extraction result is different from an extractor that does "
        "not yet exist.' No extractor looked, so nothing was seen."),
    "unreadable": (True,
        "§2.9: 'unsupported proprietary formats should be recorded as "
        "indexed-but-unreadable rather than silently treated as empty.' The SPEC maps "
        "an unreadable extraction result to this handling class by name."),
    "failed": (True,
        "In P4's ZERO_OBSERVATION_COMPLETENESS: the run did not complete and emitted "
        "nothing."),
    "dataless": (True,
        "11 §5: 'Do not materialize, hash, or extract.' C4: nothing was opened, so "
        "nothing was seen. The bytes are elsewhere and the row records that."),
})


def completeness_implies_unclassified(completeness: object) -> bool:
    """Whether a run at this marking leaves the file with nothing to classify.

    True does not mean the class was WRITTEN -- nothing writes it, and D2 forbids
    `unreadable_unclassified` from reaching `files.sensitivity_state`. It means no
    content was read, so no evidence-backed classification is possible and the gate's
    resolution for this file version is `unreadable_unclassified`.
    """
    try:
        implies, _ = COMPLETENESS_RULE[completeness]
    except (KeyError, TypeError):
        raise OutOfVocabulary(
            f"{completeness!r} is not one of P4's nine completeness markings "
            f"{tuple(COMPLETENESS_RULE)}. There is no marking literally named "
            "'indexed-but-unreadable': §2.9's phrase is spelled `unreadable`."
        ) from None
    return implies


def sensitivity_signal_keys(conn: sqlite3.Connection,
                            file_id: str) -> tuple[str, ...]:
    """P4 observation keys P5 marked "potentially sensitive" for this file.

    A detector INPUT and not a detector. It applies no rule, assigns no class and
    returns no value: only the citation handles a detector would pass as
    `evidence_refs`. P5's own docstring is explicit about who it is for -- "Email
    addresses, message content and every VCF value are marked POTENTIALLY SENSITIVE at
    emission, for P7 to act on. P5 assigns no handling class: section 8.4 gives
    classification to P7."

    P5's reader is keyed by `run_id` only, so this is the file-level walk P7 composes
    from the two readers P4 and P5 already publish; P7 adds no reader to P5. Keys are
    deduplicated in first-seen order, because a re-run of the same extractor at the
    same content hash produces the same key (MINOR 8) and listing it twice would make
    one observation look like two.
    """
    seen: dict[str, None] = {}
    for run in runs_for_file(conn, file_id):
        for row in sensitivity_signals_for(conn, run.run_id):
            if row["signal"] == POTENTIALLY_SENSITIVE:
                seen.setdefault(row["observation_key"], None)
    return tuple(seen)
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_classification.py -v`
Expected: PASS — 33 passed

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–3 green, and every pre-existing test still green. P7 has created
`src/privacy/` and `tests/p7/` and modified no file belonging to another part.

- [ ] **Step 6: Commit**

```bash
git add src/privacy/classification.py tests/p7/test_p7_classification.py
git commit -m "feat(P7): the classification record, evidence-backed, with absence resolving to unreadable_unclassified"
```

---

## What these three tasks leave open, and for whom

**C24 — whether a P6 `sensitivity` field exists — is CLOSED by D7, and the conclusion these tasks
were written to survive is the one that was ruled.** P7's SPEC Contract in said *"**P6 must accept
`sensitivity` as a first-class universal field** (§3.11) rather than a domain-scoped one"*, and the
design does list *"sensitivity status"* among §3.11's universal file facts. D2 made P7's
`ClassificationRecord` authoritative and round 1 found that the P6 field has no producer; D2 settled
which record is AUTHORITATIVE and did not settle whether a second, P6-owned field row continues to
exist beside it. **D7 settles it: P6 creates no `sensitivity_status` field row, and P7's
`ClassificationRecord` is the sole home** — the reconciliation would have made a *third* home for one
concept, beside P1's `files.sensitivity_state` column. The SPEC Contract-in sentence is amended to
name `ClassificationRecord`; round 1's F-2 is closed by deletion rather than by inventing a writer.
**Task 3 needs no change:** `src/privacy/classification.py` imports nothing from P6 and reads no
`file_facts` row, which is now the ruled shape rather than a hedge against an open question. It uses
no P6 vocabulary at all — `reliability_state` is **P4's**
(`evidence_shape.vocabulary.RELIABILITY_STATES`, re-exported by Task 2), which is what lets P7 keep
the states without the P6 import D7 forbids.

**Open questions this section holds and does not answer.** Question 1 (`protected` versus the top
two classes) is held by `ClassificationRecord.protected` being a required caller-supplied boolean
with no derivation. Question 2 (filename versus path) is held by `filename` being the one item kind
absent from §8.4's own sentence, marked as such in `vocabulary.py`'s comment and asserted in the
test. Questions 3–11 are held by `vocabulary.OPEN_QUESTIONS`, which Task 21 reads. None of the eleven
is answered in code.

**Contract deviations, all four reported above and repeated here so a reviewer can find them in one
place.** `vocabulary.OPEN_QUESTIONS` and `vocabulary.HANDLING_CLASS_LABELS` are added to Task 2;
`classification.COMPLETENESS_RULE` and `classification.sensitivity_signal_keys` are added to Task 3.
`src/privacy/__init__.py` is a docstring-only package marker rather than the re-export the File
Structure describes, because `Gate` is Task 20. Task 3 reaches `vocabulary.HANDLING_CLASSES` through
`check_handling_class` and does not import `evidence_shape.runs.COMPLETENESS` into the module. The
skeleton's Task 2 heading counts four `protected` spellings and its body names five; the body is
followed. The skeleton's Task 3 paragraph says a dataless file has no run row; the skeleton's own
refusal table says it has one, and the table is followed.
