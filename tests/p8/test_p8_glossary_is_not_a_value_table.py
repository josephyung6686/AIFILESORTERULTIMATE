# tests/p8/test_p8_glossary_is_not_a_value_table.py
"""`104` R-163: the dossier handed the model a field-keyed table of strings.

**The measurement.** R-163: *"the literal `work_type` was proposed as a value 16
times, the phrase `work product of a bounded engagement or ...` 6 times, and
`term`'s own sentence 3 times"*, and R-159 adds *"155 `work_type` answers are a
single word off the extension or the glossary"*. `104` §16.3 is explicit that the
normaliser is not at fault and that a quote-stripping rule would launder the
symptom, so nothing here reads a response. This file is about the INPUT.

**The composition defect, as a fact about the bytes.** The answer the model must
produce is `payload`: an answerable field key beside one string
(`a_fact_response_schema.json`, `$defs.payload`). `field_glossary` was emitted as a
JSON object mapping each answerable field key to one string. That is the same
table. Meanwhile `released_evidence` -- the only place a value may come from -- is a
list of objects carrying `observation_key`, `address`, `value` and `zone`, and is
not indexed by field at all. So the one structure in the dossier shaped like the
answer was the one place a value may never be taken from, and the model filled the
answer from it.

**What changed, and what did not.** Every sentence is still the library's, byte for
byte; `field_glossary` is still built from `allowed_vocabulary` and nothing else,
which is what keeps a file, a person or a corpus out of it
(`test_p8_field_glossary`). Only the container moved: the glossary now wears the
shape the dossier already uses for per-field material that is instruction and not
evidence -- `folder_levels`, a list of objects whose first key is `field`.

**And it fixes a second contradiction.** `model_facts.order_vocabulary_by_levels`
puts the situation's own folder levels at the head of `allowed_vocabulary` on
purpose, measured: *"over 199 real files the model answered in that order -- 59, 19,
4 and 34 claims against a single `work_type`"*. `canonical_json` then re-sorted the
glossary object's keys, so the dossier printed the vocabulary in the tree's nesting
order and the glossary alphabetically. `order_vocabulary_by_levels` names that
failure in its own words: *"two orders of one list in one document is a
contradiction the model has to resolve."* A list holds the vocabulary's order.

**Owed to the owner, and not written here.** The two sentences R-163 is actually
about are §15.4 item 16's -- `work_type`'s meaning is a routing arrow ending in the
literal token `work_type`, and `term`'s is a bare description a model can echo. The
library's text is the owner's and no sentence in it is touched. The ratified
template's line 21 describes this key as one that *"maps a field key to one sentence
describing what that field is"*, which a list of `field`/`meaning` pairs still does;
its neighbouring line 23 already teaches the model to read exactly this shape for
`folder_levels`. A sentence making line 21 as precise as line 23 is the owner's.
"""
from __future__ import annotations

import json
from pathlib import Path

from llm_harness.dossier import field_glossary

from p8.test_p8_field_glossary import _body, _library

LIBRARY = Path(__file__).resolve().parents[2] / "src" / "llm_harness" / "library"
RESPONSE_SCHEMA = json.loads(
    (LIBRARY / "a_fact_response_schema.json").read_text(encoding="utf-8"))


# --- the defect, as a fact about the answer's own shape ---------------------------


def test_the_answer_pairs_a_field_key_with_one_string():
    """The premise, read off the ratified schema rather than asserted.

    If `payload` ever stops being "one answerable field key, one string", the
    isomorphism this file is about is gone and the rest of it is measuring nothing.
    """
    payload = RESPONSE_SCHEMA["$defs"]["payload"]
    assert payload["required"] == ["field"]
    assert payload["properties"]["field"]["type"] == "string"
    assert payload["properties"]["value"]["type"] == "string"


def test_the_glossary_is_not_a_map_from_an_answerable_field_key_to_a_string():
    """The change itself: the dossier no longer carries a ready-made answer table."""
    glossary = _body()["field_glossary"]
    assert not isinstance(glossary, dict)
    assert isinstance(glossary, list)


def test_the_glossary_wears_the_shape_the_dossier_gives_per_field_instruction():
    """`folder_levels` is the dossier's existing shape for this, and it is a list of
    objects whose `field` names an `allowed_vocabulary` member. The glossary was the
    only per-field block not using it.
    """
    body = _body()
    allowed = set(body["allowed_vocabulary"])
    for entry in body["field_glossary"]:
        assert set(entry) == {"field", "meaning"}
        assert entry["field"] in allowed
        assert isinstance(entry["meaning"], str) and entry["meaning"]


# --- and what did not change ------------------------------------------------------


def test_every_meaning_is_the_library_s_sentence_byte_for_byte():
    """A composition change and not a text change. No sentence is edited here, and
    the two R-163 is about (`work_type`, `term`) are §15.4 item 16's, the owner's.
    """
    shipped = {key: entry["meaning"] for key, entry in _library()["fields"].items()}
    for entry in _body()["field_glossary"]:
        assert entry["meaning"] == shipped[entry["field"]]


def test_only_the_fields_of_this_call_get_an_entry():
    """`76` R7's bound is unchanged: the vocabulary is the only input."""
    assert [entry["field"] for entry
            in _body(allowed_vocabulary=("school",))["field_glossary"]] == ["school"]
    assert field_glossary(tuple(sorted(_library()["owed"]))) == []


def test_the_glossary_reads_in_the_vocabulary_s_order_and_not_alphabetically():
    """One order of one list in one document.

    `order_vocabulary_by_levels` puts the situation's folder levels first on purpose
    and `canonical_json` used to re-alphabetise the glossary behind it. `subject`
    sorts after `school`; asked in the order a coursework tree nests, it comes first,
    and the glossary now says so too.
    """
    ordered = ("subject", "school")
    body = _body(allowed_vocabulary=ordered)
    assert tuple(body["allowed_vocabulary"]) == ordered
    assert tuple(entry["field"] for entry in body["field_glossary"]) == ordered


def test_no_field_is_explained_twice():
    """A list can repeat where an object could not. It does not."""
    fields = [entry["field"] for entry
              in field_glossary(("subject", "school", "subject"))]
    assert fields == ["subject", "school"]


def test_the_glossary_still_cannot_vary_between_two_files():
    """The bound that makes the glossary instruction rather than evidence, re-read
    through the new shape: two dossiers sharing only their vocabulary carry the
    identical glossary.
    """
    one = _body(subject_ref="file-1", value="Columbia University", address="0:19")
    two = _body(subject_ref="file-2", value="BUSIB 4300 Syllabus", address="7:26")
    assert one["released_evidence"] != two["released_evidence"]
    assert one["field_glossary"] == two["field_glossary"]


def test_the_glossary_carries_no_observation_key_and_so_is_not_citable():
    """What makes text citable in this dossier is an `observation_key` in
    `released_evidence`. The glossary has none, and the two blocks now do not even
    share a shape: one is keyed by field, the other by observation.
    """
    body = _body()
    for entry in body["field_glossary"]:
        assert "observation_key" not in entry
        assert "value" not in entry
    citable = {item["observation_key"] for item in body["released_evidence"]}
    assert citable and not any(
        entry["field"] in citable for entry in body["field_glossary"])
