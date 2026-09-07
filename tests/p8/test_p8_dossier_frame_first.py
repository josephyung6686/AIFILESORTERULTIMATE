# tests/p8/test_p8_dossier_frame_first.py
"""R-58: the dossier body is emitted frame first, so the prompt prefix is shared.

`canonical_json` sorts keys, and `_body` used it for the top level. Sorted, the
fifteen keys interleave the material that is the SAME for every file of one
situation with the material that describes THIS file: `conflicts` is third and
`evidence_items` fifth, so the shared prefix ended 205 bytes into an 8,999-byte
body -- 2.3% of it. Everything after that, `field_glossary` and `folder_levels`
included, was re-read by the provider on every call even though not one byte of it
had changed.

Measured by the prompt agent on the provider's own `prompt_cache_hit_tokens` over
one dossier: **90% of the prompt served from cache frame-first against 39% sorted,
about 2,560 tokens a call.** `104` R-52 already records that a stable prefix is what
lets a KV cache carry across files; this is the same argument at the byte level, and
it is the whole of the change.

**What did not change.** The same fifteen keys with the same values -- every
assertion in `test_p8_dossier.py` is about a value and all of them still hold. The
form is still one per value: nested objects still go through `canonical_json`, so
they are still key-sorted, still unpadded, still UTF-8 and never ASCII-escaped. Only
the TOP-LEVEL order moved, and it moved to a documented constant rather than to
insertion order, so it cannot drift with an edit to `_body`.

**What did change, and it is by design.** `dossier_id` is the content address of
these bytes, so every dossier assembled after this commit has a different id from
one assembled before it over the same content. That is what a content address is
for; nothing persisted carries a literal one.

**Where the prefix really starts.** `records.assemble` is
`prompt_definition.template_bytes + canonical_dossier_bytes`, and the template is
8,020 constant bytes, so the shared prefix a provider sees is the template plus
whatever of the body follows it.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402
from llm_harness.dossier import _BODY_ORDER, _FILE_KEYS, _FRAME_KEYS, _body  # noqa: E402
from llm_harness.records import (  # noqa: E402
    EvidenceItem,
    MalformedRecord,
    ReleasedEvidence,
)
from production import (  # noqa: E402
    folder_levels_for, load_shipped_catalogue, read_packaged_library_file,
)

SITUATION = "academic.coursework"
VOCABULARY = ("school", "term", "subject", "work_type")
KEY = bytes(32)


@pytest.fixture(scope="module")
def levels():
    return folder_levels_for(
        load_shipped_catalogue(read_packaged_library_file), SITUATION)


def _items(tag: str) -> tuple[EvidenceItem, ...]:
    return tuple(
        EvidenceItem(evidence_ref=f"sha256:{tag * 64}-{index}", kind="excerpt",
                     location=f"page:{index}", excerpt_span=(0, 10),
                     reliability_state="direct", basis="direct-anchor")
        for index in range(3))


def _released(tag: str, items) -> tuple[ReleasedEvidence, ...]:
    return tuple(
        ReleasedEvidence(observation_key=item.evidence_ref,
                         address=f"page:{index}",
                         value=f"a reading from file {tag}, number {index}",
                         zone="body")
        for index, item in enumerate(items))


def _raw(levels, tag: str = "a", **overrides) -> bytes:
    items = _items(tag)
    values = dict(
        call_site=cli.A_FACT, subject_ref=f"file-{tag}",
        eligibility_reason="remains_ambiguous", plan_version=None,
        policy_version="policy-1", max_dossier_tokens=4000,
        reduction_rung="none", allowed_vocabulary=VOCABULARY,
        folder_levels=levels, evidence_items=items, conflicts=(),
        released_evidence=_released(tag, items),
        prompt=cli.a_fact_prompt(), handle_key=KEY)
    values.update(overrides)
    return _body(**values)


def _shared_prefix(first: bytes, second: bytes) -> int:
    shared = 0
    for left, right in zip(first, second):
        if left != right:
            break
        shared += 1
    return shared


# --- the order is a constant, and it is the one emitted -------------------------


def test_the_order_is_declared_and_it_partitions_the_fifteen_keys():
    assert _BODY_ORDER == _FRAME_KEYS + _FILE_KEYS
    assert len(_BODY_ORDER) == 15
    assert len(set(_BODY_ORDER)) == 15
    assert set(_FRAME_KEYS) & set(_FILE_KEYS) == set()
    # The four that describe THIS file and nothing else. If a key ever moves
    # between the two halves it is because somebody decided it did, not because a
    # dict happened to iterate that way.
    assert _FILE_KEYS == ("subject_ref", "conflicts", "evidence_items",
                          "released_evidence")


def test_the_bytes_are_emitted_in_that_order(levels):
    """Read off the bytes, not off a set. `json.loads` keeps insertion order, so
    this is the sequence the provider actually receives."""
    assert tuple(json.loads(_raw(levels).decode("utf-8"))) == _BODY_ORDER


def test_no_key_about_this_file_precedes_any_key_of_the_frame(levels):
    order = tuple(json.loads(_raw(levels).decode("utf-8")))
    last_frame = max(order.index(key) for key in _FRAME_KEYS)
    first_file = min(order.index(key) for key in _FILE_KEYS)
    assert last_frame < first_file


# --- and the prefix is therefore shared -----------------------------------------


def test_two_files_of_one_situation_share_the_whole_frame(levels):
    """The measurement, as an assertion. Sorted, this was 205 bytes of 8,999.

    The shared run must reach the first file-specific key exactly: one byte less
    would mean something in the frame is not constant, and one byte more is not
    possible because `subject_ref` differs.
    """
    first, second = _raw(levels, "a"), _raw(levels, "b")
    shared = _shared_prefix(first, second)

    assert len(first) == len(second)
    assert shared > 205 * 20
    assert shared / len(first) > 0.85
    # It ends inside the first file-specific key's value, and that key is named in
    # the bytes immediately around where the run stops.
    assert b'"subject_ref":' in first[shared - 40:shared + 20]


def test_every_frame_value_is_the_same_on_both_files(levels):
    """The prefix above is a consequence of this, and this is the thing that has to
    be true. Anything situation-constant that leaked into a per-file value would
    show up here rather than as a mysteriously short prefix."""
    first = json.loads(_raw(levels, "a").decode("utf-8"))
    second = json.loads(_raw(levels, "b").decode("utf-8"))
    for key in _FRAME_KEYS:
        assert first[key] == second[key], key
    for key in _FILE_KEYS:
        assert first[key] != second[key] or first[key] == [], key


# --- one form per value, still ---------------------------------------------------


def test_equal_input_still_gives_identical_bytes(levels):
    assert _raw(levels, "a") == _raw(levels, "a")


def test_nested_objects_are_still_key_sorted(levels):
    """Only the top level moved. An evidence item's own keys still come out in
    `canonical_json`'s order, which is what every cache key and replay diff in the
    product outside this body still depends on."""
    raw = _raw(levels).decode("utf-8")
    item = json.loads(raw)["evidence_items"][0]
    assert list(item) == sorted(item)
    glossary = json.loads(raw)["field_glossary"]
    assert list(glossary) == sorted(glossary)


def test_a_sixteenth_key_is_refused_rather_than_appended(levels):
    """The order is the contract. A key the constant does not name has no place in
    the sequence, and guessing one would put it wherever the code happened to build
    it -- which is the drift this commit removes."""
    from llm_harness.dossier import _ordered_body

    with pytest.raises(MalformedRecord):
        _ordered_body({key: None for key in _BODY_ORDER} | {"readings": []})
    with pytest.raises(MalformedRecord):
        _ordered_body({key: None for key in _BODY_ORDER[:-1]})
