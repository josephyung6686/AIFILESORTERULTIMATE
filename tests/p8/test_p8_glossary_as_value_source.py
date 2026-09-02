# tests/p8/test_p8_glossary_as_value_source.py
"""The sixteenth stress case: a value lifted out of `field_glossary` prose.

`82-FACT-PROMPT-DRAFT.md` §4 closes with *"the fifteen do not cover the surface v3
opens"*, and §7.1 names the surface: the glossary was built to tell the model what a
field means, and several entries define a field by listing what goes in it --
`media_type` is *"photo, screenshot, scan, video"*, `application_document_type` is
*"essay, transcript, form, portal record"*. Put that beside `86` §4 -- **the proposed
value is never compared to the citation or to any released text** -- and a model can
cite a real span, lift a word out of the glossary, and get `accept_direct`.

`82` §7.1: *"There is no stress case for this and no test."* This file is that case.

**No `PromptDefinition` is constructed here and no model is called.** Same method as
`test_p8_prompt_stress_cases.py`, whose helpers this file imports rather than
re-authoring: recorded response bytes through the real `llm_harness.sites.dispatch`
at `A_FACT`, over a real P1 file, a real P4 observation, P6's own `build_request` and
this deployment's own oracles.

What it measures is not whether a model would do this. It is the same sharper
question `86` asked of the fifteen: if the model does it, does the machine catch it.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from facts.domains import DOMAIN_FIELDS, ActivationSignal, ActivationSignals
from facts.file_facts import facts_for_file
from facts.llm_seam import build_request
from llm_harness.fact_validation import FactValidationDependencies
from llm_harness.records import Dossier, EvidenceItem, ReleasedEvidence
from llm_harness.sites import FactSiteDependencies, SiteDependencies
from llm_harness.vocabulary import (
    A_FACT,
    CITATION_SPAN_MISMATCH,
    DIRECT_ANCHOR,
    REDUCTION_NONE,
    REMAINS_AMBIGUOUS,
    VALUE_NOT_IN_CITED_TEXT,
)

from cli import contradicts_stronger, normalize_for_model  # noqa: E402

# The fifteen's world builder, verdict reader and response builders. Imported so that
# this case is measured by the same apparatus and cannot drift from it. `site_a_conn`
# is a fixture and is imported for pytest to find.
from p8.test_p8_prompt_stress_cases import (  # noqa: F401
    ADDRESS,
    MODEL,
    ONE_ABSTAIN,
    ONE_ACCEPT,
    POLICY,
    PROMPT_FP,
    World,
    _claim,
    _decline,
    _judge,
    _observe,
    _one_reject,
    _record_file,
    _response,
    site_a_conn,
)

GLOSSARY = json.loads(
    (Path(__file__).resolve().parents[2]
     / "src/llm_harness/library/field_glossary.json").read_text(encoding="utf-8")
)["fields"]


#: The glossary entries that define a field by ENUMERATING what goes in it, and the
#: words they enumerate. Written out rather than parsed, because a parser would be
#: guessing at prose; `test_every_enumerated_word_is_really_in_the_glossary` re-reads
#: the shipped file and fails if one of these words stops being in it, so the list
#: cannot rot into a claim about a glossary that no longer says this.
#:
#: `schema_id` is the domain schema whose field set carries the key -- none of them
#: is academic, which is why this file builds its own world rather than reusing the
#: fifteen's.
ENUMERATING_ENTRIES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("media_type", "photos", ("photo", "screenshot", "scan", "video")),
    ("application_document_type", "college_applications",
     ("essay", "transcript", "form", "portal record")),
    ("site", "logistics", ("plant", "works", "depot", "store", "field")),
    ("supplier", "logistics",
     ("Carrier", "Haulier", "Forwarder", "Shipping Line", "Airline")),
    ("issuing_body", "business_operations",
     ("regulator", "examining board", "licensing authority", "certifying body")),
)

#: Released prose that mentions none of the enumerated words. The span the model
#: cites is real and is copied out of this exactly; the value it proposes is not in
#: here at all. That gap is the whole case.
RELEASED = "Prepared by the office in the autumn and filed under reference 88."
REAL_SPAN = "the office"


def _world_for_schema(conn, tmp_path, *, schema_id: str,
                      released: str = RELEASED, run_id: str = "r-1") -> World:
    """One file whose evidence activates `schema_id`, and the real P6/P8 authorities.

    A copy of the fifteen's `_world` narrowed to what this case needs and widened by
    the one thing it does not have: a schema other than academic. The allowlist is
    P6's own (`build_request`), so a field this file proposes is allowed because the
    catalogue allows it, not because the test said so.
    """
    file_id, content_hash = _record_file(conn, tmp_path, b"office record, autumn")
    released_key = _observe(
        conn, file_id=file_id, content_hash=content_hash, raw=released,
        label="heading", run_id=run_id)
    request = build_request(
        conn, file_id=file_id, content_hash=content_hash,
        activation_signals=ActivationSignals(signals=(
            ActivationSignal(schema_id=schema_id, activates=lambda rows: True),
        )),
        normalizers={},
    )
    dossier = Dossier(
        dossier_id="dossier-glossary",
        call_site=A_FACT,
        subject_ref=file_id,
        eligibility_reason=REMAINS_AMBIGUOUS,
        plan_version=None,
        policy_version=POLICY,
        allowed_vocabulary=tuple(request.allowlist),
        evidence_items=(EvidenceItem(
            evidence_ref=released_key, kind="excerpt", location="body",
            excerpt_span=(0, len(released)), reliability_state="direct",
            basis=DIRECT_ANCHOR),),
        conflicts=(),
        released_evidence=(ReleasedEvidence(
            observation_key=released_key, address=ADDRESS, value=released,
            zone="body"),),
        max_dossier_tokens=4000,
        reduction_rung=REDUCTION_NONE,
        release_id="rel-1",
    )
    dependencies = SiteDependencies(
        fact=FactSiteDependencies(
            fact_request=request,
            fact_dependencies=FactValidationDependencies(
                normalize=normalize_for_model,
                contradicts=contradicts_stronger,
            ),
        ),
        placement=None, residual=None, template=None,
    )
    return World(
        conn=conn, file_id=file_id, content_hash=content_hash, dossier=dossier,
        dependencies=dependencies, resolver=lambda key: released,
        released_key=released_key, second_key=None,
    )


# --- the shape of the hazard, before any response is judged ----------------------


def test_every_enumerated_word_is_really_in_the_glossary():
    """The premise, re-read from the shipped file rather than asserted.

    If a meaning is retranscribed and stops enumerating, this fails and the rest of
    the file is measuring a hazard that no longer exists.
    """
    for field_key, schema_id, words in ENUMERATING_ENTRIES:
        meaning = GLOSSARY[field_key]["meaning"]
        for word in words:
            assert word in meaning, (field_key, word, meaning)
        assert field_key in DOMAIN_FIELDS[schema_id], (field_key, schema_id)


def test_no_enumerated_word_appears_in_the_released_evidence():
    """The gap the case turns on: the value is in the glossary and nowhere else.

    A word that also appeared in the released prose would make the case ambiguous --
    the model might have found it. None of them does.
    """
    for _field_key, _schema_id, words in ENUMERATING_ENTRIES:
        for word in words:
            assert word.lower() not in RELEASED.lower(), word


def test_every_enumerated_word_survives_check_three(site_a_conn, tmp_path):
    """The hazard surface, counted: 22 glossary words, 22 that the value check passes.

    `82` §5.5 and `86` §3 record that check 3 has a real slot for `subject` and `term`
    and for nothing else. That is the general claim; this is the specific one that
    matters here -- for every field whose glossary entry lists its own candidate
    values, `normalize_for_model` returns each listed word unchanged. Nothing about
    a value's provenance is available to the check, so there is nothing it could do.

    This number is a property of the glossary and the oracle. **No prompt text moves
    it**, which is why a bake-off between prompt candidates cannot be scored on it.
    """
    surviving = [
        (field_key, word)
        for field_key, _schema_id, words in ENUMERATING_ENTRIES
        for word in words
        if normalize_for_model(field_key, word) == word
    ]
    total = sum(len(words) for _f, _s, words in ENUMERATING_ENTRIES)
    assert total == 22
    assert len(surviving) == 22


# --- S16: the lift itself --------------------------------------------------------


@pytest.mark.parametrize(
    ("field_key", "schema_id", "word"),
    [(field_key, schema_id, word)
     for field_key, schema_id, words in ENUMERATING_ENTRIES
     for word in words],
    ids=[f"{field_key}-{word.replace(' ', '_')}"
         for field_key, _schema_id, words in ENUMERATING_ENTRIES
         for word in words],
)
def test_s16_a_value_lifted_from_the_glossary_is_refused(
        field_key, schema_id, word, site_a_conn, tmp_path):
    """A real citation carrying a value that exists only in the glossary.

    **All 22 of these were `accept_direct` when this file was written.** The span is
    copied exactly out of `released_evidence`, so check 2 passes. The value
    normalizes, so check 3 passes. The field is in `allowed_vocabulary`, so check 1
    passes. No stronger fact exists, so check 4 passes. Nothing looked at the value.

    `llm_harness.value_grounding` looks at it. None of the 22 words is in
    `RELEASED`, so none of them is a value the cited text carries, and all 22 are
    `VALUE_NOT_IN_CITED_TEXT`.

    The control is the answer the draft directs -- decline, because no released value
    carries the thing -- and it still abstains. The two are one word apart in the
    response bytes and the machine no longer ranks them equally well.
    """
    world = _world_for_schema(site_a_conn, tmp_path, schema_id=schema_id)
    assert field_key in world.dossier.allowed_vocabulary

    lifted = _response(_claim(
        field_key, word, key=world.released_key, span=REAL_SPAN,
        why="the office prepared it"))
    assert _judge(world, lifted) == _one_reject(VALUE_NOT_IN_CITED_TEXT)

    declined = _response(_decline(
        field_key, "no released value names one"))
    assert _judge(world, declined) == ONE_ABSTAIN


def test_the_lifted_value_no_longer_becomes_a_real_llm_supported_fact(
        site_a_conn, tmp_path):
    """The consequence, not just the verdict -- the shape `86` §2 used for S1.

    A refused verdict that still wrote the row would be no fix at all, so this runs
    the consequence and reads P6's own table back. It used to hold
    `media_type = "screenshot"`, active, `llm_supported`, for a file whose evidence
    never used the word, on the strength of a citation about an office. It now holds
    nothing for that field.
    """
    world = _world_for_schema(site_a_conn, tmp_path, schema_id="photos")
    lifted = _response(_claim(
        "media_type", "screenshot", key=world.released_key, span=REAL_SPAN,
        why="the office prepared it"))

    assert _judge(world, lifted, apply=True) == _one_reject(
        VALUE_NOT_IN_CITED_TEXT)

    rows = [row for row in facts_for_file(
        site_a_conn, world.file_id, world.content_hash)
        if row["field_key"] == "media_type"]
    assert rows == []


def test_a_lift_and_a_find_are_told_apart_when_the_word_is_not_in_the_evidence(
        site_a_conn, tmp_path):
    """S16 was S1's sibling. It is not any more, and this is where that changed.

    `86` §1 records that S1's correct minimal answer and its over-quoted one produce
    the identical `(outcome, reasons)` pair, and this test used to assert that these
    two did as well. The first cites a span about an office and proposes a word from
    the glossary; the second cites a span that really is the word, from evidence that
    really says it. One is an invention and one is a correct reading.

    They now produce different pairs, and the correct reading is still accepted --
    which is the half that matters, because a check that refused both would have
    bought nothing.
    """
    invented = _world_for_schema(site_a_conn, tmp_path, schema_id="photos")
    from_the_glossary = _response(_claim(
        "media_type", "screenshot", key=invented.released_key, span=REAL_SPAN,
        why="the office prepared it"))

    found = _world_for_schema(
        site_a_conn, tmp_path, schema_id="photos", run_id="r-2",
        released="Saved as a screenshot on the phone.")
    from_the_evidence = _response(_claim(
        "media_type", "screenshot", key=found.released_key, span="screenshot",
        why="the line names the kind of capture"))

    assert _judge(invented, from_the_glossary) != _judge(found, from_the_evidence)
    assert _judge(invented, from_the_glossary) == _one_reject(
        VALUE_NOT_IN_CITED_TEXT)
    assert _judge(found, from_the_evidence) == ONE_ACCEPT


def test_a_lift_and_a_find_stay_indiscriminable_when_the_word_IS_in_the_evidence(
        site_a_conn, tmp_path):
    """The limit of the check, asserted rather than promised.

    `90` §2.2 warns that several of the 22 are ordinary English -- *form*, *field*,
    *store*, *scan* -- and will legitimately appear in real released text. When the
    word is there, a model that read it off the glossary and a model that read it off
    the page produce byte-identical claims, and no comparison of characters can
    separate them. The check NARROWS S16; it does not close it, and a report that
    said "closed" would be false.

    Both claims below cite a span about an office over prose that also happens to
    mention a screenshot. One found the word and one lifted it. Both are accepted.
    """
    world = _world_for_schema(
        site_a_conn, tmp_path, schema_id="photos",
        released="Prepared by the office; a screenshot of the ledger is attached.")

    lifted_but_present = _response(_claim(
        "media_type", "screenshot", key=world.released_key, span=REAL_SPAN,
        why="the office prepared it"))
    genuinely_found = _response(_claim(
        "media_type", "screenshot", key=world.released_key, span=REAL_SPAN,
        why="the line names the kind of capture"))

    assert _judge(world, lifted_but_present) == _judge(world, genuinely_found)
    assert _judge(world, lifted_but_present) == ONE_ACCEPT


def test_a_glossary_sentence_quoted_as_a_span_is_caught(site_a_conn, tmp_path):
    """The asymmetry `82` §3 claims, verified rather than asserted.

    *"A quoted span from the glossary is caught (`CITATION_SPAN_MISMATCH`); a value
    is not caught by anything."* The first half is what this pins. A model that
    treats the glossary as quotable text -- cites the meaning sentence it read the
    field from -- is rejected, because the span is matched against
    `released_evidence[].value` and the glossary is not released evidence.

    So the draft's *"nothing written in it may be quoted"* is machine-backed and its
    *"a word that appears only there is not a value you found"* is not. The two
    halves of one sentence sit on opposite sides of the seam, which is worth knowing
    before deciding how hard that sentence has to work.
    """
    world = _world_for_schema(site_a_conn, tmp_path, schema_id="photos")
    quoting_the_glossary = _response(_claim(
        "media_type", "screenshot", key=world.released_key,
        span="what kind of capture this is",
        why="the glossary says so"))

    assert _judge(world, quoting_the_glossary) == _one_reject(CITATION_SPAN_MISMATCH)


def test_s16_is_machine_defended_and_the_prompt_only_set_is_the_fifteen_s_two(
        site_a_conn, tmp_path):
    """The deliverable, as an assertion, in the form `86` used for the fifteen.

    `86` §1: twelve machine, two prompt-only, one neither. S16 was a THIRD prompt-only
    case -- a value with no relationship to the evidence, supplied by the dossier
    itself -- and the sentence in `82` §2 was the entire defence for it.

    It is machine-defended now. The five `site` words that this test used to watch
    sail through are refused, and the prompt-only set is back to `86`'s two: S1's
    over-quotation, whose value IS in the evidence, and S2's plausible misreading,
    whose value is also in the evidence. Both are outside what a character
    comparison can see, which is exactly why they stay where they are.

    The old docstring said: *"If a check is ever added that compares a value to the
    released text, this test is where it will announce itself."* This is the
    announcement.
    """
    world = _world_for_schema(site_a_conn, tmp_path, schema_id="logistics")
    for word in ("plant", "works", "depot", "store", "field"):
        assert _judge(world, _response(_claim(
            "site", word, key=world.released_key, span=REAL_SPAN,
            why="the office prepared it"))) == _one_reject(
                VALUE_NOT_IN_CITED_TEXT)
