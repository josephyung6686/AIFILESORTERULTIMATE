# tests/integration/test_the_school_is_asked_of_anchors.py
"""`105` §14.4 at site A: who is asked the school, and who is not.

`104` §11.2 step 2 withdrew `school` from the per-file question, and `104` R-102
is the cost it left: nothing writes a `school` fact any more, so the coursework
tree has no school level on any corpus. The owner's ruling of 7 September 2026
restores the question to the files that can answer it -- "Answer school only when
a permitted anchor establishes the institution's relevant relationship to the
course or enrollment being organized" -- and leaves it withdrawn everywhere else.

Three things are pinned here, and the first is the one that keeps the other two
honest:

* the anchor kinds are terms the shipped recognition release ALREADY spells, so
  admitting a file to the question adds no vocabulary member;
* the kind is the file's own settled kind, so a model's guess about what a file
  is cannot open the question about it, and a protected file is not asked at all;
* a `school` fact resting on nothing but the file's own name is named as such,
  which is `104` R-95's measurement made checkable.
"""
from __future__ import annotations

import pytest

from cli import (
    SCHOOL_ANCHOR_KINDS, SCHOOL_FIELD, WORK_TYPE_FIELD, WORK_TYPE_VOCABULARY,
    kind_tokens, load_shipped_catalogue, read_packaged_library_file,
    rests_on_a_name_alone,
)
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import record_observation, record_run
from facts.domains import ActivationSignal, ActivationSignals
from facts.fields import create_fields
from facts.llm_seam import build_request
from facts.states import LLM_SUPPORTED
from llm_harness.records import FolderLevel
from model_facts import AnchorOnlyLevels, anchor_only_levels, open_question
from privacy.resolve import FILENAME_ZONE, FILESYSTEM_SOURCE_TYPE
from production import folder_levels_for, group_level_fields_for

from p9.test_p9_retrieval import _fact, _file, _hash

CLOCK = "2026-09-07T00:00:00+00:00"
SCHOOL_LEVEL = FolderLevel(field=SCHOOL_FIELD, label="My school",
                           requirement="optional")
ACADEMIC = ActivationSignals(signals=(
    ActivationSignal(schema_id="academic", activates=lambda facts: True),))


@pytest.fixture(scope="module")
def catalogue():
    return load_shipped_catalogue(read_packaged_library_file)


@pytest.fixture()
def corpus(conn):
    create_fields(conn)
    create_evidence_schema(conn)
    return conn


def _rule(*, may_reach_a_model=lambda file_id: True) -> AnchorOnlyLevels:
    return AnchorOnlyLevels(
        levels=(SCHOOL_LEVEL,), kind_field=WORK_TYPE_FIELD,
        anchor_kinds=SCHOOL_ANCHOR_KINDS, may_reach_a_model=may_reach_a_model)


def _request(conn, file_id: str):
    return build_request(conn, file_id=file_id, content_hash=_hash(conn, file_id),
                         activation_signals=ACADEMIC, normalizers={})


def _named(conn, file_id: str, name: str) -> str:
    """The file's own name as P4 records it, which is what the gate releases.

    `extractors/filesystem.py` writes exactly one `filename`-zone observation per
    indexed version and `privacy.resolve.filename_address` finds it by that zone
    AND the `filesystem` source family. Both halves are here, because a fixture
    that matched on the zone alone would be finding a different observation than
    the product does.
    """
    content_hash = _hash(conn, file_id)
    record_run(conn, ExtractionRun(
        run_id=f"r-name-{file_id}", file_id=file_id, content_hash=content_hash,
        extractor_name="filesystem", extractor_version="1.0.0",
        source_type=FILESYSTEM_SOURCE_TYPE, analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="filesystem",
        extractor_version="1.0.0", source_type=FILESYSTEM_SOURCE_TYPE,
        raw_value=name,
        location=Location(zone=FILENAME_ZONE,
                          container_path=(Segment(kind="field", label="filename"),),
                          text_span=TextSpan(start=0, end=len(name))),
        occurrence_count=1, observed_at=CLOCK, reliability="direct",
        run_id=f"r-name-{file_id}")
    record_observation(conn, observation)
    return observation.observation_key


def test_every_anchor_kind_is_a_term_the_release_already_ships():
    """No vocabulary member is added, and this is what makes that checkable.

    `SCHOOL_ANCHOR_KINDS` is a SELECTION from `WORK_TYPE_VOCABULARY`, which is
    compiled from the shipped recognition release, and the value a `work_type`
    fact carries is the library's own spelling of the term
    (`cli.normalize_for_model`). A member here that the release does not ship
    could never match a file's kind, so the rule would be silently inert -- which
    is `104` R-102's own failure wearing a fix's name.
    """
    for kind in sorted(SCHOOL_ANCHOR_KINDS):
        assert WORK_TYPE_VOCABULARY.terms.get(kind_tokens(kind)) == kind, kind


def test_the_ruling_names_a_kind_the_release_cannot_spell():
    """The gap, pinned so it is owed rather than forgotten.

    §14.4's fourth anchor kind is "a tuition or housing statement" and no schema
    that declares `work_type` ships a term for one. Until the owner adds a member,
    a tuition statement cannot be admitted to the question at all -- and this test
    fails on the day it can, which is the day the comment above
    `SCHOOL_ANCHOR_KINDS` stops being true.
    """
    shipped = set(WORK_TYPE_VOCABULARY.terms.values())
    assert not [term for term in shipped
                if "tuition" in term or "housing" in term]


def test_the_school_level_is_the_one_the_situation_withholds_from_every_file(
        catalogue):
    """The premise of the whole rule, read off the shipped library.

    Coursework binds `school` to the group, so it is withheld from the every-file
    list -- and it is a level the situation really builds, which is why R-102's
    silence costs a folder rather than nothing.
    """
    levels = folder_levels_for(catalogue, "academic.coursework")
    group_level = group_level_fields_for(catalogue, "academic.coursework")
    assert SCHOOL_FIELD in group_level
    restored = tuple(level for level in levels
                     if level.field in group_level
                     and level.field == SCHOOL_FIELD)
    assert restored == (SCHOOL_LEVEL,)


def test_a_syllabus_is_asked_the_school(corpus, tmp_path):
    """The anchor, and the kind is its own settled fact rather than a guess."""
    conn = corpus
    file_id = _file(conn, tmp_path, "BUSIB 4300 Syllabus.pdf")
    _fact(conn, file_id, field_key=WORK_TYPE_FIELD, value="syllabus",
          run_id="r-kind")

    assert anchor_only_levels(_request(conn, file_id), _rule()) == (SCHOOL_LEVEL,)


def test_an_essay_is_not(corpus, tmp_path):
    """`104` §11.1's own five files. An essay states the school it MENTIONS, and
    asking it produced `Coursework/Georgetown Prep/essay` for five essays from a
    university course. Its kind is not an anchor kind, so it is not asked."""
    conn = corpus
    file_id = _file(conn, tmp_path, "Essay 2 Final Draft.pdf")
    _fact(conn, file_id, field_key=WORK_TYPE_FIELD, value="essay",
          run_id="r-kind")

    assert anchor_only_levels(_request(conn, file_id), _rule()) == ()


def test_a_file_whose_kind_nothing_settled_is_not_asked(corpus, tmp_path):
    """`104` R-95's corpus was mostly this file: `todo.txt`, `IMG_4822.jpg`,
    `submission_backup.zip`. No kind, no anchor, no question."""
    conn = corpus
    file_id = _file(conn, tmp_path, "todo.txt")

    assert anchor_only_levels(_request(conn, file_id), _rule()) == ()


def test_a_models_own_guess_about_the_kind_does_not_open_the_question(corpus,
                                                                     tmp_path):
    """The kind comes from `build_request`'s stronger-than-LLM tuple, so a model
    that answered `work_type` cannot use its own answer to be asked a second
    question. Two model answers standing on each other is how one wrong reading
    becomes a folder."""
    conn = corpus
    file_id = _file(conn, tmp_path, "Unknown.pdf")
    _fact(conn, file_id, field_key=WORK_TYPE_FIELD, value="syllabus",
          reliability_state=LLM_SUPPORTED, run_id="r-kind")

    assert anchor_only_levels(_request(conn, file_id), _rule()) == ()


def test_a_protected_anchor_is_not_asked(corpus, tmp_path):
    """§14.4 bound to §14.3: "a tuition or housing statement classified protected
    cannot become model-eligible because it is also an anchor".

    The flag is the route's -- `cli.model_route_permitted`, which already refuses
    a protected file every model on every locality -- and the rule asks it rather
    than reading the classification again.
    """
    conn = corpus
    file_id = _file(conn, tmp_path, "Unofficial Transcript.pdf")
    _fact(conn, file_id, field_key=WORK_TYPE_FIELD, value="unofficial transcript",
          run_id="r-kind")
    request = _request(conn, file_id)

    assert anchor_only_levels(request, _rule()) == (SCHOOL_LEVEL,)
    assert anchor_only_levels(
        request, _rule(may_reach_a_model=lambda file_id: False)) == ()


def test_a_deployment_that_was_handed_no_rule_asks_nobody(corpus, tmp_path):
    """`None` is R-102's state and it stays the default: restoring the question
    is the owner's ruling, and a deployment that has not read it must not start
    asking by omission."""
    conn = corpus
    file_id = _file(conn, tmp_path, "BUSIB 4300 Syllabus.pdf")
    _fact(conn, file_id, field_key=WORK_TYPE_FIELD, value="syllabus",
          run_id="r-kind")

    assert anchor_only_levels(_request(conn, file_id), None) == ()


def test_the_field_and_its_level_are_offered_together(corpus, tmp_path):
    """What the anchor's extra level does to the question the dossier puts.

    `open_question` intersects the pending fields with the shown levels, so the
    vocabulary and the levels are one computation: adding the level is what makes
    `school` askable, and a field offered without its level is the mismatch
    `dossier._folder_levels_body` refuses.
    """
    conn = corpus
    file_id = _file(conn, tmp_path, "BUSIB 4300 Syllabus.pdf")
    _fact(conn, file_id, field_key=WORK_TYPE_FIELD, value="syllabus",
          run_id="r-kind")
    request = _request(conn, file_id)
    every_file = (FolderLevel(field="subject", label="Course",
                              requirement="required"),)
    pending = ("subject", SCHOOL_FIELD)

    withheld, withheld_levels = open_question(pending, every_file)
    assert SCHOOL_FIELD not in withheld
    assert SCHOOL_LEVEL not in withheld_levels

    asked, shown = open_question(
        pending, every_file + anchor_only_levels(request, _rule()))
    assert SCHOOL_FIELD in asked
    assert SCHOOL_LEVEL in shown


def test_a_school_fact_resting_on_the_filename_alone_is_named_as_such(corpus,
                                                                      tmp_path):
    """`104` R-95, as a predicate the tree can ask.

    38 `llm_supported` facts on 52 files, every one a `school`, most of them the
    file's own name. A name is the person's label for a file and not a reading of
    the document, so a fact citing that observation and nothing else rests on the
    name alone.
    """
    conn = corpus
    file_id = _file(conn, tmp_path, "Columbia BUSIB 4300 Syllabus.pdf")
    named = _named(conn, file_id, "Columbia BUSIB 4300 Syllabus.pdf")
    fact_id = _school_fact(conn, file_id, "Columbia", (named,))

    assert rests_on_a_name_alone(conn)(file_id, fact_id) is True


def test_a_school_fact_citing_the_document_is_not(corpus, tmp_path):
    """The same file, the same value, a citation from the document's own text.

    The rule is about WHERE the value came from and never about what it says, so
    the two cases have to be told apart on the citation alone.
    """
    conn = corpus
    file_id = _file(conn, tmp_path, "Columbia BUSIB 4300 Syllabus.pdf")
    _named(conn, file_id, "Columbia BUSIB 4300 Syllabus.pdf")
    read = _fact(conn, file_id, field_key="subject", value="BUSIB4300",
                 run_id="r-body")
    fact_id = _school_fact(conn, file_id, "Columbia", (read,))

    assert rests_on_a_name_alone(conn)(file_id, fact_id) is False


def test_a_file_with_no_addressable_name_rests_on_something_else(corpus,
                                                                 tmp_path):
    """No filesystem observation, no name for the citation to be. The corpus
    assembled without that extractor is a real deployment, and the rule answers
    about the citation rather than refusing the file."""
    conn = corpus
    file_id = _file(conn, tmp_path, "BUSIB 4300 Syllabus.pdf")
    read = _fact(conn, file_id, field_key="subject", value="BUSIB4300",
                 run_id="r-body")
    fact_id = _school_fact(conn, file_id, "Columbia", (read,))

    assert rests_on_a_name_alone(conn)(file_id, fact_id) is False


def _school_fact(conn, file_id: str, value: str,
                 evidence_refs: tuple[str, ...]) -> str:
    """One `school` fact citing exactly the observations named."""
    from facts.file_facts import write_fact
    from facts.states import VALIDATED
    from facts.values import ensure_value

    value_id = ensure_value(
        conn, field_key=SCHOOL_FIELD, canonical_value=value,
        first_evidence_ref=evidence_refs[0], origin="automatic")
    return write_fact(
        conn, file_id=file_id, content_hash=_hash(conn, file_id),
        field_key=SCHOOL_FIELD, value_id=value_id,
        reliability_state=VALIDATED, origin="llm_interpretation",
        evidence_refs=evidence_refs,
        cache_key=f"sha256:{file_id}-{SCHOOL_FIELD}", active=True)
