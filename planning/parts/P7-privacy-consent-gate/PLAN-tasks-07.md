### Task 7: The six releasable item kinds, the always-local nine, and `whole_document_requested`

> **DUPLICATE-AUTHORING NOTICE — read before assembling.** A `### Task 7` was being written into
> [`PLAN-tasks-04-07.md`](PLAN-tasks-04-07.md) at line 2414 while this file was being written
> (file mtime 2026-08-22 02:56, thirty seconds before this section started). Two sections now
> claim Task 7. They agree on A11/A12/A13 — the additions table that file publishes at its own
> lines 113–116 — and they **disagree on three field lists**, which is the whole of the difference:
>
> | | `PLAN-tasks-04-07.md`'s Task 7 | This section |
> |---|---|---|
> | `MetadataField` | `(name, value)` | `(name,)` — **no value** |
> | `Filename` | `(file_id, value)` | `(file_id,)` — **no value** |
> | `Excerpt.span` / `RedactedIdentifier.span` | `TextSpan` | `TextSpan \| None` |
>
> **This section's shapes are the ones SPEC §6 and the already-written Task 9 require, and the
> other section's cannot be built.** SPEC §6 line 227 spells the request field as
> *"`requested_items[]`    item kinds from §4 above — references only, never materialised content"*.
> A `MetadataField` carrying a `value` and a `Filename` carrying a `value` **are** materialised
> content in the request, so the two-field forms make that line false. And Task 9
> ([`PLAN-tasks-08-11.md`](PLAN-tasks-08-11.md), *"Task 9 pins one field of Task 7's items"*)
> states the span pin outright: *"`Excerpt.span` and `RedactedIdentifier.span` are
> `evidence_shape.location.TextSpan | None` — `None` for the container-path form, where the address
> is the whole citation."* A non-optional `span` makes §2.3's cell and §2.8's EXIF field
> unaddressable, and Task 9's `test_a_container_path_address_has_no_unit_length` fails on
> construction. **Take this section's field lists.** Everything else in the other section — the
> B5d/C9a flagging, `allow_unratified`, `sensitive_observation_keys`, the `current_path` gap —
> is the same decision reached independently and is preserved here.

**Files:**
- Create: `src/privacy/items.py`
- Test: `tests/p7/test_p7_items.py`

**Interfaces:**
- Consumes: `privacy.vocabulary.ALWAYS_LOCAL`, `.ITEM_KINDS`, `.check_item_kind(value) -> str`,
  `.OPEN_QUESTIONS`, `.OutOfVocabulary`, `evidence_shape.location.TextSpan(start, end)`,
  `evidence_shape.store.runs_for_file(conn, file_id) -> list[ExtractionRun]`,
  `extractors.long_tail.POTENTIALLY_SENSITIVE`,
  `.sensitivity_signals_for(conn, run_id) -> list[sqlite3.Row]`.
- Produces (`items.py`):
  - `Excerpt(observation_key: str, span: TextSpan | None, reason: str)`
  - `RedactedIdentifier(observation_key: str, span: TextSpan | None, identifier_class: str)`
  - `CandidateLabel(label: str)`
  - `MetadataField(name: str)`
  - `EvidenceReference(observation_key: str)`
  - `Filename(file_id: str)`
  - `RequestedItem` — the union of the six.
  - `ITEM_FIELDS: Mapping[str, tuple[str, ...]]` — kind → field names, read from
    `dataclasses.fields`, never retyped.
  - `RATIFIED_ITEM_KINDS: tuple[str, ...]` (§8.4's five), `UNRATIFIED_ITEM_KINDS: tuple[str, ...]`
    (`("filename",)`), `FILENAME_OPEN_QUESTION: str`.
  - `kind_of(item) -> str` (A13)
  - `is_whole_document(item, *, unit_length) -> bool`
  - `check_item(item, *, unit_length, protected, sensitive_keys, allow_unratified) -> None` (A11)
  - `sensitive_observation_keys(conn, file_id) -> frozenset[str]` (A13)
  - `AlwaysLocalRequested`, `WholeDocumentRequested`, `UnratifiedItemKind`, `ProtectedItemRequested`.

**Done-means:** 6 (the `always_local_item` and `whole_document_requested` reasons).

---

**The sixth kind is built, is named as unratified, and cannot ship by accident — NEEDS-JOSEPH B5d
and C9a.** §8.4's sentence names **five**: *"the engine should send only a compact dossier relevant
to the current question: selected excerpts, redacted identifiers, candidate labels, non-sensitive
metadata, and evidence references"*, and **the same sentence** puts *"Paths"* in the always-local
set. §7.7's residual dossier *"includes the filename"*. §7.3 forbids filenames in prompts **only**
for `Protected Records`: *"it should normally remain local-only and must not cause filenames or
content to be exposed in model prompts."* P7's SPEC §4 reads directory path ≠ filename — §7.3's
carve-out is vacuous under any other reading — permits `filename` for non-protected files, denies it
for protected ones, and lists the whole thing as its own **Open question 2**.

**This plan does not settle it, and three separate mechanisms make that visible rather than
implicit:**

1. `UNRATIFIED_ITEM_KINDS = ("filename",)` sits beside `RATIFIED_ITEM_KINDS` (§8.4's five) in the
   module, so the split is a value a reviewer can print, not a comment.
2. `allow_unratified` is a **required keyword with no default** on `check_item`. A caller who has
   not typed the word cannot admit a `Filename`; a build that forgets it raises `TypeError`, not a
   release.
3. `FILENAME_OPEN_QUESTION` names the three sections that disagree and is asserted equal to
   `vocabulary.OPEN_QUESTIONS[2]`, so the module and the SPEC's open-questions list cannot drift
   apart, and `test_filename_is_the_unratified_sixth_kind_needs_joseph_b5d_c9a` is the named test
   the reviewer greps for.

Task 21 can then assert that **no module under `src/privacy/` passes `allow_unratified=True`** —
the opt-in exists for a caller outside this part, and P7 itself never takes it.

**The always-local nine are refused at CONSTRUCTION, not at release, and that is the skeleton's own
word.** The skeleton: each of the nine is *"**not expressible** as any of the six item kinds,
asserted by attempting to construct one and catching `AlwaysLocalRequested`"*. Task 13 says the same
from its side — *"Task 7 refuses those at construction with `AlwaysLocalRequested`"* — and Task 20
has already been written against it: *"Task 7 makes the nine named kinds unconstructible, so a
request holding 'OCR output' cannot be built and cannot be a fixture."* Three sections agree, so the
check lives in `__post_init__` and `check_item` does not repeat it. SPEC §3 is the sentence being
made mechanical: *"Nothing in this set can be named as a releasable item kind. The gate has no code
path that materialises one."*

**Eight of the nine have no field to live in; the ninth is a name, and only one field names a kind
of data.** `Excerpt`, `RedactedIdentifier` and `EvidenceReference` carry an `observation_key` and at
most a span — an address, never content. `CandidateLabel` carries a label, which §4.5 and §5.4 make
a **destination** name rather than a kind of data. `Filename` carries a `file_id` — an id, not a
name — because SPEC §6 says requests carry *"references only, never materialised content"*, and the
gate is what turns the reference into a string. That leaves `MetadataField.name` as the single
channel through which one of §8.4's nine could be *named*, and it is checked against
`vocabulary.ALWAYS_LOCAL` — **the nine names exactly, after one normalisation, with no synonym
list.**

**The normalisation is Task 2's, not a second one.** Task 2 derived `ALWAYS_LOCAL` from §8.4's
sentence with `word.lower().replace(" ", "_")` and its own test asserts the round trip. `_normalise`
here is that transformation and nothing more, so `"GPS"`, `"image EXIF"` and `"Complete extracted
text"` all land on their key and a caller cannot evade the check by matching the design's surface
spelling instead of P7's. A test asserts `_normalise` is the identity on every member of
`ALWAYS_LOCAL`, which is what makes "same transformation" checkable rather than asserted.

**The gap this leaves is real, is deliberate, and is reported rather than papered over.**
`MetadataField(name="current_path")` is **not** caught by this layer. A synonym list would be a
detection rule, and SPEC's own constraint is that *"`src/privacy/` contains no regex, no gazetteer,
no filename pattern, no keyword list"* — Task 21 asserts it by introspection. What catches
`current_path` is that a `metadata_field` is *"a named non-sensitive field"* whose name the **caller
declares**; Task 13 decides on the declared name, and P7 owns no detector that could second-guess
it. One test asserts the gap by name so a later reader finds a decision instead of an oversight.

**`paths` gets a second, structural home because it is a value shape, not only a name.**
`Filename.file_id` is P1's opaque id. A `file_id` carrying a path separator **is** a path wearing an
id's field name, so `Filename.__post_init__` refuses one with `AlwaysLocalRequested`. That is one
character, not a pattern catalogue, and it closes the only kind whose field could plausibly carry
§8.4's first always-local word.

**"Raw sensitive values" is the one always-local item that cannot be recognised by name, and P5
already publishes the only thing that recognises it.** P5's `long_tail` marks each located value it
emits with `POTENTIALLY_SENSITIVE` (`= "potentially sensitive"`, verified by import), keyed on P4's
`observation_key`: *"the row is keyed on `observation_key`, which is what survives a re-run and what
P7 can redact against."* So the resolution-time half of the rule is:

> an **`Excerpt`** over a key P5 marked is `AlwaysLocalRequested`; a **`RedactedIdentifier`** over
> the **same** key is permitted.

That asymmetry is exactly what §8.4's *"redacted identifiers"* allowance means, and it is why
Task 8's transform is injected with no default — the permitted path cannot silently emit the raw
value. `sensitive_keys` is a **required keyword** on `check_item` and `check_item` opens no database:
the walk is `runs_for_file` → `sensitivity_signals_for`, composed once here as
`sensitive_observation_keys`. P7 adds no reader to P4 or P5.

**"OCR output" is the whole output; an OCR excerpt is not — and this contradicts a sentence already
written in Task 20.** §8.4 permits *"a short heading or OCR excerpt"* in the very sentence that puts
*"OCR output"* in the always-local set, so an `Excerpt` over an observation in the `ocr` zone is
releasable and the complete OCR text is not; what stops the complete text is
`WholeDocumentRequested`. [`PLAN-tasks-20-22.md`](PLAN-tasks-20-22.md) reaches fixture 7's
`Denied(always_local_item)` *"by a CONSTRUCTIBLE `Excerpt` that RESOLVES to always-local content --
P4's fixture 8 is an `ocr.apple_vision` run in zone `ocr`, and §8.4 puts 'OCR output' in the
always-local set."* **`items.py` does not branch on `zone` and will not deny that excerpt.**
Reported, not resolved: the two readings cannot both hold, §8.4's *"OCR excerpt"* clause is the
evidence against the zone reading, and if Task 20's fixture 7 is to stay reachable it should stand
on a **P5-signalled key** (the mechanism above, which fires for a real reason) rather than on the
zone. Naming it here so assembly finds it; no fixture is edited by this task.

**Task 6's local-first default is a DEFAULT; these nine are not, and the two must not be read as one
rule.** Task 6's own words: *"W1 binds the DEFAULT, never the choice"* — `resolve_default_policy`
returns a stored `cloud_assisted` policy unchanged, and `MORE_REDACTING` fills a facet the user has
not set. The always-local nine are the opposite kind of rule: **no mode, no policy, no consent
option and no default makes one of them expressible.** SPEC §3: *"The gate has no code path that
materialises one."* So `items.py` consumes neither `defaults` nor `policy`, takes no mode argument,
and has no branch a mode could change — which is the structural statement that the nine are not a
posture. A test asserts the absence of both imports.

**What this task does NOT own, so the rule keeps one home each.** `check_item`'s `protected` refuses
a **`Filename`** on a protected file and nothing else. §7.3 also forbids *content* for a
`Protected Records` file, and §8.4 forbids protected material in cloud prompts by default — those
are the gate's `protected_records_template` and `protected_cloud_target` denials, which Task 13
builds and `release.DECISION_ORDER` sequences. A second copy here would be a rule with two homes,
and this task refuses to hold one. The stricter of the two readings is taken for the filename
itself: §7.3 has **no locality qualifier** — *"must not cause filenames or content to be exposed in
model prompts"*, full stop — while §8.4's *"not included in cloud-model prompts **by default**"* is
what the consent path reopens. So a protected `Filename` is refused for **any** target and
`NeedsConsent` is where the user reopens it. Reported as a reading.

**`UnratifiedItemKind` deliberately maps to NO denial reason.** `DENIAL_REASONS` has eight and none
of them says "the caller named an unratified kind", which is correct: that is a **build defect**,
not a policy outcome, and it must propagate to the developer rather than reach a user as a `Denied`
they could try to consent around. Task 13's eight builders are complete without a ninth.

---

### Two cross-task demands this task raises

Both are on **Task 11**, both are one-line changes to code already written in
[`PLAN-tasks-08-11.md`](PLAN-tasks-08-11.md), and the second is a **live defect** rather than a
tidying.

| Demanded of | What, and why |
|---|---|
| **P7 Task 11** | `Gate._materialise` calls `check_item(item, unit_length=found.unit_length)`. A11 — published in [`PLAN-tasks-04-07.md`](PLAN-tasks-04-07.md) line 114 — gives `check_item` three further **required** keywords. The call must become `check_item(item, unit_length=found.unit_length, protected=<the record's flag>, sensitive_keys=sensitive_observation_keys(self._conn, file_id), allow_unratified=False)`. As written it is a `TypeError` on the first release. |
| **P7 Task 11** | `Gate._materialise` runs `if not isinstance(item, TEXT_BEARING): continue` **before** `check_item`, so `CandidateLabel`, `MetadataField`, `EvidenceReference` and `Filename` are never checked at all. `release.DECISION_ORDER` lists `always_local_item` as a step and `PLAN-tasks-15-22.md`'s fixture 7 is *"GPS requested as an item"* — under the current loop a `MetadataField` reaching the gate is released unchecked. The fix is to split the loop: **check every requested item, materialise only the text-addressed ones.** |

One further note, not a demand: `release.TEXT_BEARING: tuple[type, ...] = (Excerpt, RedactedIdentifier)`
in Task 11 is a second home for a fact `ITEM_FIELDS` already carries — an item is text-addressed iff
`"span" in ITEM_FIELDS[kind_of(item)]`. `items.py` therefore publishes **no** type tuple of its own
and keys every branch off `kind_of`, so there is exactly one place to change if a seventh kind is
ever ratified. Task 11 may keep `TEXT_BEARING` or derive it; this task will not add a competing one.

---

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_items.py
"""§8.4's compact dossier: what a request may name, and what it may not.

Three of the assertions here are held open on purpose, and each says so in its own
docstring rather than in a comment a reader has to find.

`filename` is a SIXTH kind and §8.4's sentence names FIVE. §7.7 puts the filename in
the residual dossier and §7.3 forbids filenames in prompts only for Protected
Records. P7's SPEC adopts the reading that makes §7.3 non-vacuous and lists it as its
own Open question 2. NEEDS-JOSEPH B5d and C9a. The tests below prove the kind is
unadmittable without an explicit opt-in; they never prove the reading is right.

The always-local check over `MetadataField.name` is a VOCABULARY check against §8.4's
nine names, not a detector. `MetadataField(name="current_path")` is NOT caught and a
test says so by name, because a synonym list would be the gazetteer P7 is forbidden
to own.

`_normalise` is Task 2's transformation -- `word.lower().replace(" ", "_")` -- and a
test asserts it is the identity on every member of `ALWAYS_LOCAL`. If Task 2's
derivation ever changes, that test fails here rather than opening a hole.
"""
from __future__ import annotations

import dataclasses
import inspect

import pytest

from evidence_shape.location import TextSpan
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_run
from extractors.long_tail import (
    POTENTIALLY_SENSITIVE,
    SensitivitySignal,
    record_sensitivity_signals,
)

import privacy.items as items
from privacy.items import (
    FILENAME_OPEN_QUESTION,
    ITEM_FIELDS,
    RATIFIED_ITEM_KINDS,
    UNRATIFIED_ITEM_KINDS,
    AlwaysLocalRequested,
    CandidateLabel,
    EvidenceReference,
    Excerpt,
    Filename,
    MetadataField,
    ProtectedItemRequested,
    RedactedIdentifier,
    RequestedItem,
    UnratifiedItemKind,
    WholeDocumentRequested,
    check_item,
    is_whole_document,
    kind_of,
    sensitive_observation_keys,
)
from privacy.vocabulary import ALWAYS_LOCAL, ITEM_KINDS, OPEN_QUESTIONS, OutOfVocabulary

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
CONTENT_HASH = "a" * 64
KEY = "sha256:" + "b" * 64
OTHER_KEY = "sha256:" + "c" * 64
BODY_LENGTH = 39

#: The six kinds, constructed once, so every structural assertion runs over all six
#: rather than over whichever one the test author remembered.
ONE_OF_EACH: tuple[RequestedItem, ...] = (
    Excerpt(observation_key=KEY, span=TextSpan(16, 27), reason="the group's subject"),
    RedactedIdentifier(observation_key=KEY, span=TextSpan(16, 27),
                       identifier_class="passport_number"),
    CandidateLabel(label="Passport"),
    MetadataField(name="page_count"),
    EvidenceReference(observation_key=KEY),
    Filename(file_id="file-1"),
)

#: A permissive default for the three keywords a given test is not about. Every one
#: of them is REQUIRED on `check_item` (A11); this helper spells them so a test that
#: IS about one of them can override exactly that one and nothing else.
def admit(item, *, unit_length=None, protected=False, sensitive_keys=frozenset(),
          allow_unratified=True) -> None:
    check_item(item, unit_length=unit_length, protected=protected,
               sensitive_keys=sensitive_keys, allow_unratified=allow_unratified)


# --- the six kinds, and the five that §8.4 actually names ----------------------

def test_the_six_kinds_are_task_twos_six_and_split_five_plus_one():
    assert RATIFIED_ITEM_KINDS + UNRATIFIED_ITEM_KINDS == ITEM_KINDS
    assert len(RATIFIED_ITEM_KINDS) == 5
    assert UNRATIFIED_ITEM_KINDS == ("filename",)


def test_every_kind_has_a_dataclass_and_every_dataclass_has_a_kind():
    assert set(ITEM_FIELDS) == set(ITEM_KINDS)
    assert {kind_of(item) for item in ONE_OF_EACH} == set(ITEM_KINDS)


def test_kind_of_refuses_a_type_that_is_not_one_of_the_six():
    # A foreign object is not "an unknown kind" to be tolerated: §8.4's list is
    # closed and Task 2's `OutOfVocabulary` is the load error that says so.
    with pytest.raises(OutOfVocabulary):
        kind_of("excerpt")
    with pytest.raises(OutOfVocabulary):
        kind_of(TextSpan(0, 1))


def test_item_fields_are_read_from_the_dataclasses_and_never_retyped():
    for item in ONE_OF_EACH:
        expected = tuple(f.name for f in dataclasses.fields(item))
        assert ITEM_FIELDS[kind_of(item)] == expected


def test_the_four_reference_only_shapes_are_the_ones_spec_six_requires():
    # SPEC §6: "requested_items[] item kinds from §4 above -- references only, never
    # materialised content." A `value` on any of these four would make that false.
    assert ITEM_FIELDS["candidate_label"] == ("label",)
    assert ITEM_FIELDS["metadata_field"] == ("name",)
    assert ITEM_FIELDS["evidence_reference"] == ("observation_key",)
    assert ITEM_FIELDS["filename"] == ("file_id",)


def test_no_item_kind_has_a_field_that_could_carry_document_content():
    # The structural half of "not expressible": eight of §8.4's nine always-local
    # items have nowhere to live, because no kind has a content-bearing field.
    forbidden = {"value", "text", "content", "raw_value", "path", "current_path",
                 "excerpt", "ocr_text", "bytes", "content_hash", "filename"}
    for item in ONE_OF_EACH:
        assert not set(ITEM_FIELDS[kind_of(item)]) & forbidden, kind_of(item)


def test_evidence_reference_is_an_id_only_with_no_content_field():
    # SPEC §4: "evidence_reference   an id only -- no content". Checked with
    # `dataclasses.fields`, not by reading the class body.
    names = [f.name for f in dataclasses.fields(EvidenceReference)]
    assert names == ["observation_key"]


def test_every_item_is_frozen():
    # A request the gate has already decided on must not change under it.
    for item in ONE_OF_EACH:
        with pytest.raises(dataclasses.FrozenInstanceError):
            setattr(item, ITEM_FIELDS[kind_of(item)][0], "anything else")


def test_the_two_addressed_kinds_accept_a_span_of_none():
    # Task 9's pin: `None` is the container-path form -- §2.3's cell and §2.8's EXIF
    # field, where `unit_for_observation` returns None and the address is the whole
    # citation. A non-optional span makes those unaddressable.
    assert Excerpt(observation_key=KEY, span=None, reason="the cell").span is None
    assert RedactedIdentifier(observation_key=KEY, span=None,
                              identifier_class="account_number").span is None


# --- the always-local nine: one test per name ---------------------------------
# §8.4: "Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS,
# user edits, group memberships, and raw sensitive values should remain local."
# SPEC §3: "Nothing in this set can be named as a releasable item kind. The gate has
# no code path that materialises one."

@pytest.mark.parametrize("surface, key", [
    ("Paths", "paths"),
    ("complete extracted text", "complete_extracted_text"),
    ("OCR output", "ocr_output"),
    ("file hashes", "file_hashes"),
    ("image EXIF", "image_exif"),
    ("GPS", "gps"),
    ("user edits", "user_edits"),
    ("group memberships", "group_memberships"),
    ("raw sensitive values", "raw_sensitive_values"),
])
def test_an_always_local_name_is_not_expressible_as_an_item(surface, key):
    """Nine names, nine cases, refused at CONSTRUCTION.

    The skeleton's word is "not expressible", and Task 20 has already been written
    against it: "Task 7 makes the nine named kinds unconstructible, so a request
    holding 'OCR output' cannot be built and cannot be a fixture." So the refusal is
    in `__post_init__` and `check_item` does not repeat it.

    `MetadataField.name` is the only field that names a KIND OF DATA. The other five
    kinds carry an address, an id, or a destination label, and a test above proves
    none of them has a content-bearing field to smuggle one through.
    """
    assert key in ALWAYS_LOCAL
    with pytest.raises(AlwaysLocalRequested) as caught:
        MetadataField(name=surface)
    assert key in str(caught.value)


def test_normalise_is_task_twos_transformation_and_not_a_second_one():
    # Task 2 derived ALWAYS_LOCAL from §8.4's sentence with
    # `word.lower().replace(" ", "_")`. If that derivation ever changes, this fails
    # here rather than silently opening a hole in the check above.
    for key in ALWAYS_LOCAL:
        assert items._normalise(key) == key


def test_the_always_local_check_is_exact_and_not_a_prefix_match():
    # "GPS Logs" normalises to "gps_logs", which is not "gps". A check that matched
    # loosely would be a keyword list, and §8.4 does not authorise one.
    assert MetadataField(name="GPS Logs").name == "GPS Logs"
    assert MetadataField(name="page_count").name == "page_count"


def test_a_candidate_label_naming_a_data_kind_is_not_refused():
    """§4.5 and §5.4 make a candidate label a DESTINATION name, not a data kind.

    The always-local set is a set of kinds of DATA. Applying the check to a label
    would refuse a legitimate folder called "GPS" while releasing nothing extra:
    the label carries no observation and no value.
    """
    assert CandidateLabel(label="GPS").label == "GPS"


def test_a_metadata_field_named_current_path_is_not_caught_and_that_is_deliberate():
    """The reported gap. `current_path` is not one of §8.4's nine names.

    Catching it would need a synonym list, and SPEC's constraint is that
    `src/privacy/` "contains no regex, no gazetteer, no filename pattern, no keyword
    list" -- Task 21 asserts that by introspection. A `metadata_field` is "a named
    non-sensitive field" whose name the CALLER declares; Task 13 decides on the
    declared name and P7 owns no detector that could second-guess it.

    This test exists so a later reader finds a decision instead of an oversight.
    """
    assert MetadataField(name="current_path").name == "current_path"
    assert "current_path" not in ALWAYS_LOCAL


def test_a_file_id_that_is_a_path_is_refused_as_the_first_always_local_name():
    # §8.4's first always-local word is "Paths". A `file_id` carrying a separator is
    # a path wearing an id's field name. One character, not a pattern catalogue.
    with pytest.raises(AlwaysLocalRequested) as caught:
        Filename(file_id="/Users/j/Documents/passport.pdf")
    assert "paths" in str(caught.value)
    assert Filename(file_id="file-1").file_id == "file-1"


def test_items_imports_no_mode_and_no_policy_so_the_nine_are_not_a_default():
    """Task 6's local-first posture is a DEFAULT; these nine are not.

    Task 6: "W1 binds the DEFAULT, never the choice" -- a stored `cloud_assisted`
    policy comes back unchanged. The always-local set is the opposite kind of rule:
    no mode, no policy, no consent option and no default makes one expressible. The
    structural statement of that is that this module has no branch a mode could
    change, so it binds neither `defaults` nor `policy`.
    """
    bound = {value.__name__ for value in vars(items).values()
             if inspect.ismodule(value)}
    bound |= {getattr(value, "__module__", "") for value in vars(items).values()}
    assert "privacy.defaults" not in bound
    assert "privacy.policy" not in bound
    assert not any(f.name == "operation_mode"
                   for item in ONE_OF_EACH
                   for f in dataclasses.fields(item))


# --- whole_document_requested -------------------------------------------------

def test_an_excerpt_covering_the_whole_unit_is_a_whole_document():
    # §8.4: "It should not send full documents where a short heading or OCR excerpt
    # is enough to resolve the question."
    whole = Excerpt(observation_key=KEY, span=TextSpan(0, BODY_LENGTH),
                    reason="all of it")
    assert is_whole_document(whole, unit_length=BODY_LENGTH) is True
    with pytest.raises(WholeDocumentRequested) as caught:
        admit(whole, unit_length=BODY_LENGTH)
    assert "0" in str(caught.value) and str(BODY_LENGTH) in str(caught.value)


def test_a_span_that_over_covers_the_unit_is_still_a_whole_document():
    # A span wider than the unit is not "outside the rule"; it is the same request
    # with worse arithmetic. `<= 0` and `>= unit_length`, not `== `.
    wide = Excerpt(observation_key=KEY, span=TextSpan(0, BODY_LENGTH + 400),
                   reason="all of it and then some")
    assert is_whole_document(wide, unit_length=BODY_LENGTH) is True


def test_a_bounded_excerpt_is_not_a_whole_document():
    short = Excerpt(observation_key=KEY, span=TextSpan(16, 27), reason="the number")
    assert is_whole_document(short, unit_length=BODY_LENGTH) is False
    admit(short, unit_length=BODY_LENGTH)


def test_a_redacted_identifier_over_the_whole_unit_is_also_refused():
    # The rule is about the SPAN, not about the kind. A redaction that covered the
    # whole unit would send the whole unit with one value starred out.
    whole = RedactedIdentifier(observation_key=KEY, span=TextSpan(0, BODY_LENGTH),
                               identifier_class="passport_number")
    with pytest.raises(WholeDocumentRequested):
        admit(whole, unit_length=BODY_LENGTH)


def test_a_container_path_address_is_never_a_whole_document():
    # Task 9: `unit_for_observation` returns None for §2.3's cell and §2.8's EXIF
    # field. There is no unit, so there is nothing for a span to cover, and a
    # `None` unit_length must not be read as "length zero" -- which would make every
    # cell a whole document.
    cell = Excerpt(observation_key=KEY, span=None, reason="the cell")
    assert is_whole_document(cell, unit_length=None) is False
    admit(cell, unit_length=None)


def test_a_kind_with_no_span_is_never_a_whole_document():
    for item in (CandidateLabel(label="Passport"), MetadataField(name="page_count"),
                 EvidenceReference(observation_key=KEY), Filename(file_id="file-1")):
        assert is_whole_document(item, unit_length=BODY_LENGTH) is False


# --- raw sensitive values: P5's signal, and the excerpt/identifier asymmetry ----

def test_an_excerpt_over_a_p5_signalled_key_is_always_local():
    """§8.4's ninth always-local name, and the only one that needs P5.

    P5 marks each located value it emits with POTENTIALLY_SENSITIVE, keyed on P4's
    `observation_key`. P7 owns no detector, so this signal is the only thing in the
    product that can recognise a "raw sensitive value" at all.
    """
    with pytest.raises(AlwaysLocalRequested) as caught:
        admit(Excerpt(observation_key=KEY, span=TextSpan(16, 27), reason="it"),
              unit_length=BODY_LENGTH, sensitive_keys=frozenset({KEY}))
    assert "raw_sensitive_values" in str(caught.value)


def test_a_redacted_identifier_over_the_same_key_is_permitted():
    # This asymmetry IS §8.4's "redacted identifiers" allowance. Task 8's transform
    # is injected with no default, so the permitted path cannot emit a raw value.
    admit(RedactedIdentifier(observation_key=KEY, span=TextSpan(16, 27),
                             identifier_class="passport_number"),
          unit_length=BODY_LENGTH, sensitive_keys=frozenset({KEY}))


def test_an_excerpt_over_an_unsignalled_key_is_permitted():
    admit(Excerpt(observation_key=OTHER_KEY, span=TextSpan(16, 27), reason="it"),
          unit_length=BODY_LENGTH, sensitive_keys=frozenset({KEY}))


def test_check_item_requires_every_one_of_its_four_keywords():
    # A11: none of the four has a default. A build that forgets one is a TypeError,
    # never a release. `sensitive_keys` in particular: a default of `frozenset()`
    # would mean "nothing is sensitive" for a caller who never wired P5.
    item = Excerpt(observation_key=KEY, span=TextSpan(16, 27), reason="it")
    for omit in ("unit_length", "protected", "sensitive_keys", "allow_unratified"):
        kwargs = dict(unit_length=BODY_LENGTH, protected=False,
                      sensitive_keys=frozenset(), allow_unratified=False)
        del kwargs[omit]
        with pytest.raises(TypeError):
            check_item(item, **kwargs)


def test_sensitive_observation_keys_walks_p4_runs_to_p5_signals(p7_conn):
    record_run(p7_conn, ExtractionRun(
        run_id="run-1", file_id="file-1", content_hash=CONTENT_HASH,
        extractor_name="long_tail", extractor_version="1.0.0",
        source_type="contacts", analysis_tier="native", config={},
        completeness="complete", started_at=FIXED_CLOCK, observation_count=2))
    record_sensitivity_signals(
        p7_conn, run_id="run-1",
        signals=(SensitivitySignal(observation_index=0,
                                   signal=POTENTIALLY_SENSITIVE,
                                   basis="every VCF value"),),
        observation_keys=(KEY, OTHER_KEY), now=FIXED_CLOCK)
    assert sensitive_observation_keys(p7_conn, "file-1") == frozenset({KEY})


def test_sensitive_observation_keys_is_empty_for_a_file_with_no_runs(p7_conn):
    # The honest v1 posture: nothing signalled is not "nothing sensitive". It is the
    # caller's job to know that, and the empty set says so without inventing a rule.
    assert sensitive_observation_keys(p7_conn, "file-404") == frozenset()


def test_only_the_potentially_sensitive_signal_counts(p7_conn):
    record_run(p7_conn, ExtractionRun(
        run_id="run-2", file_id="file-2", content_hash=CONTENT_HASH,
        extractor_name="long_tail", extractor_version="1.0.0",
        source_type="contacts", analysis_tier="native", config={},
        completeness="complete", started_at=FIXED_CLOCK, observation_count=1))
    record_sensitivity_signals(
        p7_conn, run_id="run-2",
        signals=(SensitivitySignal(observation_index=0, signal="something else",
                                   basis="not P5's word"),),
        observation_keys=(KEY,), now=FIXED_CLOCK)
    assert sensitive_observation_keys(p7_conn, "file-2") == frozenset()


# --- filename: the unratified sixth kind -- NEEDS-JOSEPH B5d and C9a -----------

def test_filename_is_the_unratified_sixth_kind_needs_joseph_b5d_c9a():
    """SPEC Open question 2 -- the one place the contract resolved a conflict.

    §8.4 names FIVE releasable kinds and puts *paths* in the always-local set. §7.7
    puts *the filename* in the residual dossier. §7.3 forbids filenames in prompts
    ONLY for Protected Records, which is vacuous under any reading that forbade them
    everywhere. P7's SPEC reads directory path != filename, permits `filename` for
    non-protected files, denies it for protected ones, and lists the reading as its
    own Open question 2 for the reviewer.

    NEEDS-JOSEPH B5d and C9a. This test proves the kind is UNADMITTABLE without an
    explicit opt-in. It does not prove the reading is right, and nothing in P7 does.
    """
    assert UNRATIFIED_ITEM_KINDS == ("filename",)
    assert "filename" not in RATIFIED_ITEM_KINDS
    assert FILENAME_OPEN_QUESTION == OPEN_QUESTIONS[2]
    for section in ("8.4", "7.7", "7.3"):
        assert section in FILENAME_OPEN_QUESTION


def test_a_filename_cannot_be_admitted_without_the_explicit_opt_in():
    with pytest.raises(UnratifiedItemKind) as caught:
        check_item(Filename(file_id="file-1"), unit_length=None, protected=False,
                   sensitive_keys=frozenset(), allow_unratified=False)
    assert "filename" in str(caught.value)
    assert "B5d" in str(caught.value) and "C9a" in str(caught.value)


def test_the_five_ratified_kinds_need_no_opt_in():
    for item in ONE_OF_EACH:
        if kind_of(item) in UNRATIFIED_ITEM_KINDS:
            continue
        check_item(item, unit_length=None, protected=False,
                   sensitive_keys=frozenset(), allow_unratified=False)


def test_a_filename_is_permitted_for_a_non_protected_file():
    admit(Filename(file_id="file-1"), protected=False)


def test_a_filename_is_denied_for_a_protected_file():
    """§7.3: Protected Records "must not cause filenames or content to be exposed in
    model prompts" -- no locality qualifier, so this refuses for ANY target, which is
    the stricter of the two available readings. §8.4's "not included in cloud-model
    prompts BY DEFAULT" is what the consent path reopens, and that path is
    `NeedsConsent`, not a weaker check here.
    """
    with pytest.raises(ProtectedItemRequested) as caught:
        admit(Filename(file_id="file-1"), protected=True)
    assert "7.3" in str(caught.value)


def test_protected_does_not_refuse_the_other_five_kinds_here():
    # One rule, one home. §7.3's content half and §8.4's cloud-prompt half are the
    # gate's `protected_records_template` and `protected_cloud_target` denials, which
    # Task 13 builds and `release.DECISION_ORDER` sequences. A second copy here would
    # be a rule with two homes.
    for item in ONE_OF_EACH:
        if kind_of(item) in UNRATIFIED_ITEM_KINDS:
            continue
        admit(item, unit_length=None, protected=True)


def test_unratified_maps_to_no_denial_reason():
    # A caller naming an unratified kind has a BUILD defect, not a policy problem.
    # It must propagate to the developer rather than reach a user as a `Denied` they
    # could try to consent around. Task 13's eight builders are complete without a
    # ninth.
    from privacy.vocabulary import DENIAL_REASONS
    assert not any("unratified" in reason for reason in DENIAL_REASONS)
    assert len(DENIAL_REASONS) == 8
```

- [ ] **Step 2: Run the test and watch it fail**

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p7/test_p7_items.py -q
```

Expected: **FAIL** — `ModuleNotFoundError: No module named 'privacy.items'`, at collection, on the
`import privacy.items as items` line. Nothing in `src/privacy/` defines the six kinds yet.

- [ ] **Step 3: Write `src/privacy/items.py` — the six kinds and the two refusals in `__post_init__`**

```python
# src/privacy/items.py
"""§8.4's compact dossier: the six kinds a request may name, and the nine it may not.

§8.4: "When a cloud model is used, the engine should send only a compact dossier
relevant to the current question: selected excerpts, redacted identifiers, candidate
labels, non-sensitive metadata, and evidence references." That is FIVE. `filename` is
a sixth, adopted by P7's SPEC and held unratified here -- see `FILENAME_OPEN_QUESTION`
and `UNRATIFIED_ITEM_KINDS`, NEEDS-JOSEPH B5d and C9a.

Every item carries a REFERENCE. SPEC §6: "requested_items[] item kinds from §4 above
-- references only, never materialised content." A field named `value` on any of these
would make that sentence false, so there is none: an excerpt is an
`(observation_key, span)` address, an evidence reference is "an id only -- no
content", a metadata field is a NAME, and a filename is a `file_id`. `resolve.py` is
the one module that turns a reference into a string.

Two refusals fire at CONSTRUCTION, because the skeleton's word is "not expressible"
and Task 20 is already written against it: a request naming one of §8.4's nine
always-local items cannot be built, so it cannot be a fixture either.

  AlwaysLocalRequested  -- a `MetadataField` naming one of the nine, or a `Filename`
                           whose `file_id` is a path.
  WholeDocumentRequested -- raised by `check_item`, not here: it needs the stored unit
                           length, which only `resolve.materialise` can supply.

This module holds no threshold, no regex, no gazetteer and no keyword list. The nine
names come from `vocabulary.ALWAYS_LOCAL`, which Task 2 derives from §8.4's own
sentence; `_normalise` is Task 2's transformation and nothing more. The consequence is
that `MetadataField(name="current_path")` is NOT caught, and that gap is deliberate
and tested: a synonym list would be a detection rule P7 is forbidden to own.

It also imports neither `defaults` nor `policy`. Task 6's local-first posture is a
DEFAULT that a user may change; the always-local nine are not a posture at all, and a
module with no mode to branch on is the structural way to say so.
"""
from __future__ import annotations

import dataclasses
import sqlite3
from collections.abc import Container, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from evidence_shape.location import TextSpan
from evidence_shape.store import runs_for_file
from extractors.long_tail import POTENTIALLY_SENSITIVE, sensitivity_signals_for

from privacy.vocabulary import (
    ALWAYS_LOCAL, ITEM_KINDS, OPEN_QUESTIONS, OutOfVocabulary, check_item_kind,
)


class AlwaysLocalRequested(ValueError):
    """§8.4's nine, named in a request. SPEC §3: "Nothing in this set can be named as
    a releasable item kind. The gate has no code path that materialises one."

    Task 13's `deny_always_local_item` translates a caught instance into the gate's
    `Denied(always_local_item)`; it does not re-decide which names are always-local.
    """


class WholeDocumentRequested(ValueError):
    """§8.4: the engine "should not send full documents where a short heading or OCR
    excerpt is enough to resolve the question." Raised by `check_item`, which is the
    first point at which the stored unit length is known.
    """


class UnratifiedItemKind(ValueError):
    """A kind §8.4's own sentence does not name, admitted without the opt-in.

    Deliberately NOT one of `vocabulary.DENIAL_REASONS`: this is a build defect, not
    a policy outcome, and it must reach the developer rather than a user who might
    try to consent around it.
    """


class ProtectedItemRequested(ValueError):
    """§7.3: `Protected Records` "must not cause filenames or content to be exposed
    in model prompts." Scoped here to the filename; the content half is Task 13's
    `protected_records_template`, so the rule keeps one home each.
    """


def _normalise(name: str) -> str:
    """Task 2's transformation, and not a second one.

    Task 2 derives `ALWAYS_LOCAL` from §8.4's sentence with
    `word.lower().replace(" ", "_")`. Using anything wider here would be a keyword
    rule; using anything narrower would let "GPS" through while refusing "gps".
    """
    return name.strip().lower().replace(" ", "_")


def _refuse_always_local_name(field: str, value: str) -> None:
    key = _normalise(value)
    if key in ALWAYS_LOCAL:
        raise AlwaysLocalRequested(
            f"{field}={value!r} names {key!r}, which §8.4 places in the always-local "
            f"set: 'Paths, complete extracted text, OCR output, file hashes, image "
            f"EXIF, GPS, user edits, group memberships, and raw sensitive values "
            f"should remain local.' Nothing in that set can be named as a releasable "
            f"item kind, so the request is not constructible rather than merely "
            f"denied. §8.4's releasable five are: selected excerpts, redacted "
            f"identifiers, candidate labels, non-sensitive metadata, and evidence "
            f"references."
        )


@dataclass(frozen=True)
class Excerpt:
    """SPEC §4: `{ observation_key, span, reason }`, "resolved by the gate from local
    storage". The span is the whole of what bounds it -- an excerpt with no bound is
    the full document §8.4 forbids.

    `span` is `TextSpan | None`: `None` is §2.3's cell and §2.8's EXIF field, where
    `unit_for_observation` returns `None` and the address is the whole citation
    (Task 9's pin). It is never "unbounded".
    """

    observation_key: str
    span: TextSpan | None
    reason: str


@dataclass(frozen=True)
class RedactedIdentifier:
    """SPEC §4: `{ observation_key, span, identifier_class }`.

    `identifier_class` is an OPAQUE string. SPEC *Deferred*: "Which identifier classes
    exist and how each is transformed is not enumerated anywhere in the design." Task 8
    carries it through to the manifest; this module enumerates none.
    """

    observation_key: str
    span: TextSpan | None
    identifier_class: str


@dataclass(frozen=True)
class CandidateLabel:
    """SPEC §4: "a label already present in the local database (§4.5, §5.4)".

    A DESTINATION name, not a kind of data -- which is why the always-local check does
    not run over it. A label carries no observation and no value, so a label reading
    "GPS" releases the word and nothing else.
    """

    label: str


@dataclass(frozen=True)
class MetadataField:
    """SPEC §4: "a named non-sensitive field (e.g. file type, page count, capture
    year)". The NAME only -- the gate looks the value up, per SPEC §6's "references
    only, never materialised content".

    This is the single field in the product through which one of §8.4's nine could be
    NAMED, which is why it is the one that is checked.
    """

    name: str

    def __post_init__(self) -> None:
        _refuse_always_local_name("name", self.name)


@dataclass(frozen=True)
class EvidenceReference:
    """SPEC §4: "an id only -- no content"."""

    observation_key: str


@dataclass(frozen=True)
class Filename:
    """The unratified sixth kind. NEEDS-JOSEPH B5d and C9a; SPEC Open question 2.

    Carries a `file_id`, not a name: SPEC §6 says requests carry references only, and
    the gate is what resolves the reference. A `file_id` holding a path separator is
    a path wearing an id's field name, and §8.4's first always-local word is "Paths".
    """

    file_id: str

    def __post_init__(self) -> None:
        if "/" in self.file_id or "\\" in self.file_id:
            raise AlwaysLocalRequested(
                f"file_id={self.file_id!r} carries a path separator, and §8.4 places "
                f"'paths' in the always-local set. `Filename` carries P1's opaque "
                f"file id; the gate resolves the name. A file id that is a path is a "
                f"path wearing an id's field name."
            )


RequestedItem = (Excerpt | RedactedIdentifier | CandidateLabel | MetadataField
                 | EvidenceReference | Filename)

#: Every branch in this module keys off `kind_of`, so `ITEM_KINDS` is the one place a
#: seventh kind would have to be added. Validated through Task 2's checker at import,
#: so these are provably members of the closed vocabulary and not a second spelling.
_KIND_BY_TYPE: Mapping[type, str] = MappingProxyType({
    Excerpt: check_item_kind("excerpt"),
    RedactedIdentifier: check_item_kind("redacted_identifier"),
    CandidateLabel: check_item_kind("candidate_label"),
    MetadataField: check_item_kind("metadata_field"),
    EvidenceReference: check_item_kind("evidence_reference"),
    Filename: check_item_kind("filename"),
})

#: §8.4's own five, in the design's order.
RATIFIED_ITEM_KINDS: tuple[str, ...] = (
    _KIND_BY_TYPE[Excerpt], _KIND_BY_TYPE[RedactedIdentifier],
    _KIND_BY_TYPE[CandidateLabel], _KIND_BY_TYPE[MetadataField],
    _KIND_BY_TYPE[EvidenceReference],
)

#: The sixth. Built, named, and unadmittable without `allow_unratified=True`.
UNRATIFIED_ITEM_KINDS: tuple[str, ...] = (_KIND_BY_TYPE[Filename],)

#: SPEC Open question 2, quoted from `vocabulary.OPEN_QUESTIONS` rather than retyped,
#: so the module and the SPEC's list cannot drift apart. NEEDS-JOSEPH B5d and C9a.
FILENAME_OPEN_QUESTION: str = OPEN_QUESTIONS[2]

#: Kind -> field names, READ from the dataclasses. Retyping them would be a second
#: home for a shape SPEC §4 already fixes, and the field list is what the "no content
#: field" guard reads.
ITEM_FIELDS: Mapping[str, tuple[str, ...]] = MappingProxyType({
    kind: tuple(field.name for field in dataclasses.fields(cls))
    for cls, kind in _KIND_BY_TYPE.items()
})


def kind_of(item: object) -> str:
    """The `ITEM_KINDS` name for one item. A foreign type is a load error (A13)."""
    kind = _KIND_BY_TYPE.get(type(item))
    if kind is None:
        raise OutOfVocabulary(
            f"{type(item).__name__!r} is not one of the {len(ITEM_KINDS)} releasable "
            f"item kinds the design defines {ITEM_KINDS}. §8.4's vocabularies are "
            f"closed: an unrecognised kind is a load error, not a fallback."
        )
    return kind


def is_whole_document(item: object, *, unit_length: int | None) -> bool:
    """§8.4: "It should not send full documents where a short heading or OCR excerpt
    is enough to resolve the question."

    `unit_length is None` is the container-path form -- §2.3's cell, §2.8's EXIF
    field -- where `unit_for_observation` returns `None` and there is no unit for a
    span to cover. Reading it as length zero would make every cell a whole document.
    """
    if "span" not in ITEM_FIELDS[kind_of(item)]:
        return False
    span = item.span
    if span is None or unit_length is None:
        return False
    return span.start <= 0 and span.end >= unit_length


def check_item(item: object, *, unit_length: int | None, protected: bool,
               sensitive_keys: Container[str], allow_unratified: bool) -> None:
    """The release-time half of §8.4's item rules. Returns None or raises (A11).

    Four required keywords, no defaults. `sensitive_keys` in particular: a default of
    the empty set would mean "nothing is sensitive" for a caller who never wired P5,
    which is the same shape of failure as a column with no writer.

    The order matches `release.DECISION_ORDER`: always-local before whole-document,
    so an item that fails both is reported as the stronger refusal.

    Not checked here, on purpose:
      * the always-local NAMES -- refused in `__post_init__`, so a request holding one
        is unconstructible;
      * protected CONTENT and the cloud-prompt default -- Task 13's
        `protected_records_template` and `protected_cloud_target`.
    """
    kind = kind_of(item)

    if kind in UNRATIFIED_ITEM_KINDS and not allow_unratified:
        raise UnratifiedItemKind(
            f"{kind!r} is a releasable item kind §8.4's own sentence does not name. "
            f"§8.4 names five -- selected excerpts, redacted identifiers, candidate "
            f"labels, non-sensitive metadata, and evidence references -- and puts "
            f"paths in the always-local set. P7's SPEC adds this sixth on the reading "
            f"that §7.3's carve-out is otherwise vacuous, and flags it as its own "
            f"Open question 2. NEEDS-JOSEPH B5d and C9a. Pass allow_unratified=True "
            f"to admit it deliberately; there is no default."
        )

    if protected and kind in UNRATIFIED_ITEM_KINDS:
        raise ProtectedItemRequested(
            f"§7.3: a Protected Records file 'should normally remain local-only and "
            f"must not cause filenames or content to be exposed in model prompts.' "
            f"That sentence carries no locality qualifier, so a {kind!r} on a "
            f"protected file is refused for any target. §8.4's 'not included in "
            f"cloud-model prompts by default' is what the consent path reopens, and "
            f"that path is NeedsConsent."
        )

    if kind == _KIND_BY_TYPE[Excerpt] and item.observation_key in sensitive_keys:
        raise AlwaysLocalRequested(
            f"observation {item.observation_key!r} was marked "
            f"{POTENTIALLY_SENSITIVE!r} at emission, and §8.4 places "
            f"'raw_sensitive_values' in the always-local set. §8.4 permits 'redacted "
            f"identifiers', so the same key is releasable as a RedactedIdentifier, "
            f"whose transform is injected with no default."
        )

    if is_whole_document(item, unit_length=unit_length):
        raise WholeDocumentRequested(
            f"span {item.span.start}-{item.span.end} covers the whole of a "
            f"{unit_length}-character text unit. §8.4: the engine 'should not send "
            f"full documents where a short heading or OCR excerpt is enough to "
            f"resolve the question.'"
        )


def sensitive_observation_keys(conn: sqlite3.Connection,
                               file_id: str) -> frozenset[str]:
    """P4's runs for a file -> P5's per-value sensitivity signals (A13).

    P7 owns no detector, and this is the only per-value sensitivity signal in the
    product. P5 assigns no handling class -- §8.4 gives classification to P7 -- so
    this says "P5 saw a value worth redacting", never "this file is sensitive".

    An empty set means NOTHING WAS SIGNALLED, not "nothing is sensitive". The two
    published readers are composed here; no reader is added to P4 or P5.
    """
    keys: set[str] = set()
    for run in runs_for_file(conn, file_id):
        for row in sensitivity_signals_for(conn, run.run_id):
            if row["signal"] == POTENTIALLY_SENSITIVE:
                keys.add(row["observation_key"])
    return frozenset(keys)
```

- [ ] **Step 4: Run the test and watch it pass**

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p7/test_p7_items.py -q
```

Expected: **PASS** — 39 passed (the nine parametrised always-local cases count as nine). No test
asserts that `filename` belongs in §8.4's list, and no test asserts that Task 20's `ocr`-zone
reading is right; both are held open by name.

- [ ] **Step 5: Prove the two things the guard tasks will re-assert repo-wide**

```bash
cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 - <<'PY'
import inspect
import privacy.items as items

# 1. No module-level constant in this module is a threshold, a pattern, or a class
#    catalogue. Every public string or tuple constant is drawn from a vocabulary some
#    OTHER module publishes, or is the SPEC's own open-question text. Task 21
#    re-asserts the same property over the whole package.
from extractors.long_tail import POTENTIALLY_SENSITIVE
from privacy.vocabulary import ALWAYS_LOCAL, ITEM_KINDS, OPEN_QUESTIONS

#: The published sets a constant here is allowed to be drawn from, and who owns each.
OWNED_ELSEWHERE = {
    "privacy.vocabulary.ITEM_KINDS": frozenset(ITEM_KINDS),
    "privacy.vocabulary.ALWAYS_LOCAL": frozenset(ALWAYS_LOCAL),
    "extractors.long_tail.POTENTIALLY_SENSITIVE": frozenset({POTENTIALLY_SENSITIVE}),
    "privacy.vocabulary.OPEN_QUESTIONS[2]": frozenset({OPEN_QUESTIONS[2]}),
}
constants = {name: value for name, value in vars(items).items()
             if not name.startswith("_") and not inspect.isclass(value)
             and isinstance(value, (str, tuple))}
for name, value in constants.items():
    members = frozenset((value,) if isinstance(value, str) else value)
    owner = next((who for who, published in OWNED_ELSEWHERE.items()
                  if members <= published), None)
    assert owner is not None, f"{name} is an invented constant: {value!r}"
    print(f"   {name:<24} <- {owner}")
print("1. no invented constant:", len(constants), "checked")

# 2. This module binds no P4 text materialiser. Task 9's `resolve.py` is the ONLY
#    module under src/privacy/ that may, and Task 21 re-asserts it repo-wide against
#    the authoritative `resolve.MATERIALISERS`, which does not exist yet at Task 7.
#
#    BY IDENTITY, not by name. `evidence_shape.text_units` RE-EXPORTS `TextSpan`,
#    `Mapping` and `dataclass`, all three of which this module legitimately binds, so
#    a name-set intersection reports three false positives -- measured, 2026-08-22.
#    `evidence_shape.store` re-exports nothing but DOES own `runs_for_file`, which
#    this module legitimately binds, so its three materialisers are named one by one.
import evidence_shape.store as store
import evidence_shape.text_units as tu

materialisers = [getattr(tu, name) for name in dir(tu)
                 if not name.startswith("_") and callable(getattr(tu, name))
                 and getattr(getattr(tu, name), "__module__", None) == tu.__name__]
materialisers += [store.text_unit_at, store.text_units_for_run,
                  store.unit_for_observation]
bound = [value for value in vars(items).values()]
for materialiser in materialisers:
    assert not any(value is materialiser for value in bound), materialiser
print("2. binds no P4 text materialiser:", len(materialisers),
      "checked by identity; resolve.py stays the one door")
PY
```

Expected output:

```text
   POTENTIALLY_SENSITIVE    <- extractors.long_tail.POTENTIALLY_SENSITIVE
   ALWAYS_LOCAL             <- privacy.vocabulary.ALWAYS_LOCAL
   ITEM_KINDS               <- privacy.vocabulary.ITEM_KINDS
   RATIFIED_ITEM_KINDS      <- privacy.vocabulary.ITEM_KINDS
   UNRATIFIED_ITEM_KINDS    <- privacy.vocabulary.ITEM_KINDS
   FILENAME_OPEN_QUESTION   <- privacy.vocabulary.OPEN_QUESTIONS[2]
1. no invented constant: 6 checked
2. binds no P4 text materialiser: 9 checked by identity; resolve.py stays the one door
```

Six constants, six owners, and **not one of them is owned here** — which is the whole claim. If a
later edit adds a seventh, the script names it as invented rather than letting it pass.

`POTENTIALLY_SENSITIVE` is P5's published constant, re-exported by import rather than retyped, and
`ALWAYS_LOCAL` / `ITEM_KINDS` are Task 2's — the check above is written to fail if any of the three
becomes a local literal. If it fails on `POTENTIALLY_SENSITIVE` on the day P5 changes the word, that
is the check working: the string has one home and it is P5's.

- [ ] **Step 6: Run the whole P7 suite, then commit**

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p7 -q
```

Expected: **PASS** — Tasks 1–7 green. Nothing in `src/privacy/items.py` is imported by Tasks 1–6, so
no earlier test changes.

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/privacy/items.py tests/p7/test_p7_items.py && \
git commit -m "feat(P7): the six releasable item kinds, the always-local nine held unconstructible, and filename kept unratified"
```

---

### What this task deliberately did not do

- **It did not settle Open question 2.** `filename` is built, named `UNRATIFIED`, and unadmittable
  without `allow_unratified=True`. NEEDS-JOSEPH **B5d** and **C9a**.
- **It did not build a detector.** `sensitive_keys` carries P5's signal and nothing infers one. On a
  corpus P5 never ran over, `sensitive_observation_keys` returns the empty set, and that means
  *nothing was signalled* — never *nothing is sensitive*.
- **It did not close the `current_path` gap.** A synonym list is the gazetteer P7 may not own; the
  gap is asserted by a named test and decided on the caller's declared name by Task 13.
- **It did not rule on C22.** `Region` carries no origin, so a region address is not resolvable and
  `items.py` binds no `Region`: an `Excerpt.span` is a `TextSpan | None` and Task 8's `span_address`
  is where a region raises `RegionOriginUnspecified`. Assume no origin; nothing here depends on one.
