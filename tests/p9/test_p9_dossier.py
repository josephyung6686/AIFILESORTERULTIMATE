# tests/p9/test_p9_dossier.py
"""P9 Task 8 — a bounded, reference-only, privacy-first group dossier.

P9 assembles REFERENCES. P8 materialises. Nothing here reaches a model, a gate or
a released span, and the test at the bottom enforces that by reading the module's
imports rather than trusting the prose.

Three invariants carry the task.

**Anchor and candidate files are separate arrays and are never merged.** The model
must be able to say a group is coherent while still marking particular members
uncertain, and it can only do that if direct evidence and inferred context arrive
apart.

**Nothing is dropped silently.** A file withheld for privacy, a file cut by the
neighbourhood cap and a file cut by the budget cap are three different omissions
with three different fields. Silence about a dropped file is the failure, not the
drop.

**P9 runs no token ladder.** No dossier tokens are measured, no fact is
summarised, no excerpt is dropped by a budget, no request is split. M9's ladder
belongs to P8's `run_call`.
"""
from __future__ import annotations

import pytest

from database_agent.db import create_schema
from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import record_observation, record_run
from grouping.config import ConfigurationRequired, GroupingLimits
from grouping.dossier import DossierRefused, assemble_group_dossier
from grouping.graph import build_graph
from grouping.records import (
    AnchorFact, CandidateGroupDossier, Conflict, Group, MalformedGroupRecord,
)
from grouping.retrieval import Neighbor, Neighborhood
from grouping.seeds import Seed
from grouping.vocabulary import (
    CANDIDATE,
    COMPATIBLE_DOCUMENT_TYPE,
    CONTEXT_SUPPORTED,
    DIRECT_ANCHOR,
    MUTUAL_SEMANTIC_RETRIEVAL,
    RULES,
    SHARED_VALIDATED_FACT,
    STRONGLY_IDENTIFIED_FILE,
)
from privacy.classification import ClassificationRecord

T0 = "2026-08-27T00:00:00Z"
GROUP = "group-1"
SEED_FILE = "file-seed"


@pytest.fixture()
def dossier_conn(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    return conn


def _record(conn, tmp_path, *, name, body, detected_format="pdf"):
    import json

    path = tmp_path / name
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=".pdf", observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="application/pdf",
        detected_format=detected_format, scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, file_id, content_hash, raw, run_id, text_span=None):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=T0, finished_at=T0))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location("heading", (Segment("field", label="heading"),),
                          text_span=text_span),
        occurrence_count=1, observed_at=T0, reliability="direct", run_id=run_id)
    record_observation(conn, observation)
    return observation.observation_key


@pytest.fixture()
def corpus(dossier_conn, tmp_path):
    """A seed and two neighbours, each with one real P4 observation."""
    made = {}
    for index, name in enumerate(("Syllabus.pdf", "Lecture.pdf", "Homework.pdf")):
        file_id, content_hash = _record(
            dossier_conn, tmp_path, name=name,
            body=f"PHYS1401 {name}".encode("utf-8"))
        key = _observe(
            dossier_conn, file_id=file_id, content_hash=content_hash,
            raw=f"PHYS1401 stated in {name} " + "x" * 400, run_id=f"r-{index}")
        made[name] = (file_id, content_hash, key)
    return made


def _limits(**overrides) -> GroupingLimits:
    values = dict(
        max_retrieved_neighbors=50, max_graph_nodes=10, max_candidate_members=10,
        max_dossier_tokens=4000, generic_hub_frequency=9,
        minimum_independent_anchors=1, max_excerpt_characters=240,
    )
    values.update(overrides)
    return GroupingLimits(**values)


def _group(*anchor_facts, **overrides) -> Group:
    values = dict(
        group_id=GROUP, seed_ref="seed-1", seed_kind=STRONGLY_IDENTIFIED_FILE,
        proposed_basis="course_code=PHYS1401", anchor_facts=tuple(anchor_facts),
        pre_model_signals={}, anchor_count=len(anchor_facts),
        coherence_verdict=None, coherence_citations=(), group_category=None,
        display_label=None, label_source=None, conflicts=(), stop_rule_hits=(),
        state=CANDIDATE, sensitivity_state="none", dossier_id=None,
        llm_response_ref=None, validation_verdict_ref=None, created_by=RULES,
        created_at=T0,
    )
    values.update(overrides)
    return Group(**values)


def _fact(file_id, key) -> AnchorFact:
    return AnchorFact(
        field="subject", value="PHYS1401", file_ids=(file_id,),
        reliability_state="validated", observation_key=key)


def _graph(corpus, *, channels=None, limits=None):
    seed_id, seed_hash, seed_key = corpus["Syllabus.pdf"]
    channels = channels or {
        "Lecture.pdf": (SHARED_VALIDATED_FACT, True),
        "Homework.pdf": (MUTUAL_SEMANTIC_RETRIEVAL, False),
    }
    neighbors = []
    for name, (channel, anchors) in channels.items():
        file_id, content_hash, key = corpus[name]
        neighbors.append(Neighbor(
            file_id=file_id, content_hash=content_hash, channel=channel,
            anchors=anchors, evidence_ref=key, detail=f"subject=PHYS1401:{name}"))
    return build_graph(
        group_id=GROUP,
        neighborhood=Neighborhood(
            seed=Seed(
                seed_kind=STRONGLY_IDENTIFIED_FILE, file_id=seed_id,
                content_hash=seed_hash, field_key="subject", value="PHYS1401",
                reliability_state="validated", observation_key=seed_key,
                basis=None),
            neighbors=tuple(neighbors)),
        limits=limits or _limits(),
        duplicate_or_version=None,
        created_at=T0,
    )


def _classified(handling_class="public_low", *, missing=()):
    """P7's own record, evidence-backed. A classification is itself evidence."""

    def store(file_id, content_hash):
        if file_id in missing:
            return None
        key = "sha256:" + "a" * 64
        return ClassificationRecord(
            file_id=file_id, content_hash=content_hash,
            handling_class=handling_class, protected=False,
            basis="detector", evidence_refs=(key,), reliability_state="direct",
            observed_at=T0)
    return store


def _assemble(conn, corpus, *, group=None, graph=None, limits=None, **overrides):
    seed_id, _hash, seed_key = corpus["Syllabus.pdf"]
    lecture_id, _lh, lecture_key = corpus["Lecture.pdf"]
    values = dict(
        group=group or _group(_fact(seed_id, seed_key), _fact(lecture_id, lecture_key)),
        graph=graph if graph is not None else _graph(corpus),
        limits=limits or _limits(),
        signal_evaluator_for=lambda domain: True,
        classification_store=_classified(),
        conflicts=(),
        created_at=T0,
    )
    values.update(overrides)
    return assemble_group_dossier(conn, **values)


# --- the two arrays stay apart ---------------------------------------------------


def test_direct_evidence_and_inferred_context_arrive_in_separate_arrays(
    dossier_conn, corpus,
):
    dossier = _assemble(dossier_conn, corpus)
    assert isinstance(dossier, CandidateGroupDossier)
    anchors = {item.file_id for item in dossier.anchor_files}
    candidates = {item.file_id for item in dossier.candidate_files}
    assert anchors == {corpus["Syllabus.pdf"][0], corpus["Lecture.pdf"][0]}
    assert candidates == {corpus["Homework.pdf"][0]}
    assert anchors & candidates == set()
    assert all(item.basis == DIRECT_ANCHOR for item in dossier.anchor_files)
    assert all(item.basis == CONTEXT_SUPPORTED for item in dossier.candidate_files)


# --- `104` §11.2 step 2: the fields the group carries ---------------------------


def _write_fact(conn, *, file_id, content_hash, key, field_key, value,
                state="validated"):
    """One P6 fact, through P6's own writers. `tests/p10/p6_fixtures` in miniature."""
    from facts.values import ensure_value
    from facts.file_facts import write_fact

    value_id = ensure_value(conn, field_key=field_key, canonical_value=value,
                            first_evidence_ref=key, origin="automatic")
    write_fact(conn, file_id=file_id, content_hash=content_hash,
               field_key=field_key, value_id=value_id, reliability_state=state,
               origin="rule", evidence_refs=(key,),
               cache_key=f"ck_{file_id}_{field_key}_{value}", active=True)


@pytest.fixture()
def facts_conn(dossier_conn):
    from facts.fields import create_fields

    create_fields(dossier_conn)
    return dossier_conn


def test_the_anchors_school_and_term_reach_the_dossier_as_anchor_facts(
    facts_conn, corpus,
):
    """`104` §11.2 step 2, and `00`:57 is the sentence it implements.

    Site A no longer asks each file what school it is for, so the only place the
    course's school can be seen is the group -- and the group is what the model is
    asked about at B. The syllabus states it; the dossier carries it beside the
    basis, on the group AND on the anchor that said it, so the model can tell one
    syllabus's answer from a neighbourhood's consensus.
    """
    seed_id, seed_hash, seed_key = corpus["Syllabus.pdf"]
    _write_fact(facts_conn, file_id=seed_id, content_hash=seed_hash, key=seed_key,
                field_key="school", value="Columbia")
    _write_fact(facts_conn, file_id=seed_id, content_hash=seed_hash, key=seed_key,
                field_key="term", value="Spring 2026")

    dossier = _assemble(facts_conn, corpus,
                        group_level_fields=frozenset({"school", "term"}))

    carried = {(fact.field, fact.value) for fact in dossier.key_facts}
    assert ("school", "Columbia") in carried
    assert ("term", "Spring 2026") in carried
    assert ("subject", "PHYS1401") in carried, "the basis is still first and still here"
    syllabus = next(item for item in dossier.anchor_files if item.file_id == seed_id)
    assert ("school", "Columbia") in {
        (fact.field, fact.value) for fact in syllabus.key_facts}


def test_what_a_candidate_says_about_the_school_is_not_the_groups_answer(
    facts_conn, corpus,
):
    """`00`:44's collector, refused at the source.

    A candidate is in the neighbourhood because something retrieved it. The school
    it happens to mention is `authored_by`-class metadata about that one file and
    never the course's -- which is exactly how five essays from a university course
    came to be filed under a high school (`104` §11.1).
    """
    homework_id, homework_hash, homework_key = corpus["Homework.pdf"]
    _write_fact(facts_conn, file_id=homework_id, content_hash=homework_hash,
                key=homework_key, field_key="school", value="Georgetown Prep")

    dossier = _assemble(facts_conn, corpus,
                        group_level_fields=frozenset({"school", "term"}))

    assert "Georgetown Prep" not in {fact.value for fact in dossier.key_facts}
    homework = next(item for item in dossier.candidate_files
                    if item.file_id == homework_id)
    assert "school" not in {fact.field for fact in homework.key_facts}


def test_a_weak_reading_on_the_anchor_stays_a_clue_and_does_not_become_the_groups(
    facts_conn, corpus,
):
    """`00`:42: a weak reading "may remain a possible clue for review; it must not
    quietly become a folder proposal". A group-level anchor IS a folder proposal
    for every member of the group, so the bar is the one P10 uses for a per-file
    level and not a looser one."""
    seed_id, seed_hash, seed_key = corpus["Syllabus.pdf"]
    _write_fact(facts_conn, file_id=seed_id, content_hash=seed_hash, key=seed_key,
                field_key="school", value="Columbia", state="possible")

    dossier = _assemble(facts_conn, corpus,
                        group_level_fields=frozenset({"school", "term"}))

    assert "school" not in {fact.field for fact in dossier.key_facts}


def test_two_anchors_stating_one_term_are_one_fact_with_two_files_behind_it(
    facts_conn, corpus,
):
    """`AnchorFact.file_ids` means "the files that INDEPENDENTLY state this", and
    two rows each claiming one file would understate that support to the model the
    same way `_group_for`'s one-tuple understated it to P10."""
    for name in ("Syllabus.pdf", "Lecture.pdf"):
        file_id, content_hash, key = corpus[name]
        _write_fact(facts_conn, file_id=file_id, content_hash=content_hash,
                    key=key, field_key="term", value="Spring 2026")

    dossier = _assemble(facts_conn, corpus,
                        group_level_fields=frozenset({"school", "term"}))

    terms = [fact for fact in dossier.key_facts if fact.field == "term"]
    assert len(terms) == 1
    assert set(terms[0].file_ids) == {corpus["Syllabus.pdf"][0],
                                      corpus["Lecture.pdf"][0]}


def test_the_group_level_fields_do_not_decide_who_is_an_anchor(facts_conn, corpus):
    """`stating` is the group's BASIS and nothing else. A file that names a school
    and not the course is not an independent statement of the course, and promoting
    it to a direct anchor would merge the two arrays the dossier keeps apart."""
    homework_id, homework_hash, homework_key = corpus["Homework.pdf"]
    _write_fact(facts_conn, file_id=homework_id, content_hash=homework_hash,
                key=homework_key, field_key="school", value="Columbia")

    dossier = _assemble(facts_conn, corpus,
                        group_level_fields=frozenset({"school"}))

    assert homework_id in {item.file_id for item in dossier.candidate_files}
    assert homework_id not in {item.file_id for item in dossier.anchor_files}


def test_a_candidate_names_the_channel_that_retrieved_it(dossier_conn, corpus):
    """A reviewer has to be able to tell a shared validated fact from a semantic
    guess; without the channel, both read as "it was in the neighbourhood"."""
    dossier = _assemble(dossier_conn, corpus)
    candidate = dossier.candidate_files[0]
    assert candidate.why_retrieved == MUTUAL_SEMANTIC_RETRIEVAL
    assert all(item.why_retrieved is None for item in dossier.anchor_files)


def test_a_group_whose_graph_states_the_basis_nowhere_is_refused(
    dossier_conn, corpus,
):
    seed_id, _hash, seed_key = corpus["Syllabus.pdf"]
    result = _assemble(
        dossier_conn, corpus,
        group=_group(),  # no anchor facts at all
    )
    assert isinstance(result, DossierRefused)
    assert result.group_id == GROUP
    assert result.reason


# --- excerpts are short, addressed, and resolvable --------------------------------


def test_every_excerpt_resolves_to_a_stored_observation(dossier_conn, corpus):
    from evidence_shape.store import observations_by_key

    dossier = _assemble(dossier_conn, corpus)
    assert dossier.excerpts
    for excerpt in dossier.excerpts:
        assert observations_by_key(dossier_conn, excerpt.observation_key)


def test_an_excerpt_is_a_span_and_never_the_whole_observation(dossier_conn, corpus):
    """P4 holds 400+ characters for each of these files. What reaches the dossier
    is a short addressed span; the key is the reference, the text is for a human
    reading beside it."""
    from evidence_shape.store import observations_by_key

    dossier = _assemble(dossier_conn, corpus)
    for excerpt in dossier.excerpts:
        assert len(excerpt.text) <= 240
        stored = observations_by_key(
            dossier_conn, excerpt.observation_key)[0].raw_value
        assert len(stored) > len(excerpt.text)
        assert stored.startswith(excerpt.text)


def test_an_unresolvable_key_becomes_no_excerpt_rather_than_a_quotation(
    dossier_conn, corpus,
):
    """P8 verifies a citation by resolving it. An excerpt whose key resolves to
    nothing would be a quotation the model could not be held to."""
    seed_id, _hash, seed_key = corpus["Syllabus.pdf"]
    lecture_id, _lh, lecture_key = corpus["Lecture.pdf"]
    ghost = "sha256:" + "f" * 64
    dossier = _assemble(
        dossier_conn, corpus,
        group=_group(
            AnchorFact(field="subject", value="PHYS1401", file_ids=(seed_id,),
                       reliability_state="validated", observation_key=ghost),
            _fact(lecture_id, lecture_key)),
    )
    assert ghost not in {excerpt.observation_key for excerpt in dossier.excerpts}
    assert lecture_key in {excerpt.observation_key for excerpt in dossier.excerpts}


def test_a_shared_fact_never_lends_one_files_observation_to_another(
    dossier_conn, corpus,
):
    """`104` R-97, and the fix is on the record rather than at this seam.

    An `AnchorFact` stated by two files used to carry ONE observation key -- the
    first file's. Attached to the second file it is a quotation from somewhere
    else, and P7's gate resolves every requested item to its file and raises
    `UnresolvableSpan` when that file is outside the request's target -- which it
    is the moment the first file is withheld or bounded out of the graph.

    Measured on a 52-file Downloads with qwen3:8b: the whole run died with that
    traceback after 37 minutes of A-site calls, at the first B dossier, because
    two cover letters cited a job posting's `term = Summer2026`.

    The fact now names one key per stating file, so every excerpt on a dossier
    file is that file's OWN observation -- and the second file keeps an excerpt
    instead of losing one, which is the difference between this and narrowing the
    dossier.
    """
    from evidence_shape.store import observations_by_key

    seed_id, _sh, seed_key = corpus["Syllabus.pdf"]
    lecture_id, _lh, lecture_key = corpus["Lecture.pdf"]
    shared = AnchorFact(field="subject", value="PHYS1401",
                        file_ids=(seed_id, lecture_id),
                        reliability_state="validated", observation_key=seed_key,
                        observation_keys=(seed_key, lecture_key))
    dossier = _assemble(dossier_conn, corpus, group=_group(shared))

    by_file = {item.file_id: item
               for item in (*dossier.anchor_files, *dossier.candidate_files)}
    assert seed_key in {e.observation_key for e in by_file[seed_id].excerpts}
    assert seed_key not in {e.observation_key for e in by_file[lecture_id].excerpts}
    # Its own, and it HAS one: the shared fact costs the second file nothing.
    assert lecture_key in {e.observation_key for e in by_file[lecture_id].excerpts}
    # And the whole dossier: every excerpt resolves to the file it sits on.
    for item in by_file.values():
        for excerpt in item.excerpts:
            owners = {o.file_id for o in observations_by_key(
                dossier_conn, excerpt.observation_key)}
            assert item.file_id in owners, (item.file_id, excerpt.observation_key)


def test_the_record_refuses_to_say_two_files_cite_one_observation(corpus):
    """The cause, refused where it was written. Two stating files and one key is
    not a record P9 may build any more: the caller says which key each file cites,
    and `None` is how it says a file cites nothing of its own."""
    seed_id, _sh, seed_key = corpus["Syllabus.pdf"]
    lecture_id, _lh, lecture_key = corpus["Lecture.pdf"]
    with pytest.raises(MalformedGroupRecord):
        AnchorFact(field="subject", value="PHYS1401",
                   file_ids=(seed_id, lecture_id),
                   reliability_state="validated", observation_key=seed_key)
    with pytest.raises(MalformedGroupRecord):
        AnchorFact(field="subject", value="PHYS1401",
                   file_ids=(seed_id, lecture_id),
                   reliability_state="validated", observation_key=seed_key,
                   observation_keys=(seed_key,))

    fact = AnchorFact(field="subject", value="PHYS1401",
                      file_ids=(seed_id, lecture_id),
                      reliability_state="validated", observation_key=seed_key,
                      observation_keys=(seed_key, lecture_key))
    assert fact.key_for(seed_id) == seed_key
    assert fact.key_for(lecture_id) == lecture_key
    assert fact.key_for("a-file-that-does-not-state-it") is None


def test_a_dossier_with_no_excerpt_of_its_own_is_refused_not_requested(
    dossier_conn, corpus,
):
    """The other half of the shared-fact case, and since R-97 it is a narrower
    one: a file that states the basis and cites NOTHING of its own, which is what
    a `user_confirmed` value is -- the person's answer, with no extractor reading
    behind it. `key_for` returns `None` there and no excerpt is offered.

    When the only file that does cite something is withheld, the dossier has no
    item a release could resolve, and `ModelCallRequest` refuses to be built from
    it -- measured as `MalformedRequest: a request with no items has nothing to
    release` ending a 48-minute local-model run. It is refused here, with the
    reason named, and P9 records the group as not judged.
    """
    seed_id, _sh, seed_key = corpus["Syllabus.pdf"]
    lecture_id, _lh, _lk = corpus["Lecture.pdf"]
    shared = AnchorFact(field="subject", value="PHYS1401",
                        file_ids=(seed_id, lecture_id),
                        reliability_state="validated", observation_key=seed_key,
                        observation_keys=(seed_key, None))
    result = _assemble(
        dossier_conn, corpus, group=_group(shared),
        classification_store=_classified(missing=(seed_id,)))

    assert isinstance(result, DossierRefused)
    assert "no excerpt" in result.reason
    assert result.withheld == (seed_id,)


# --- privacy: marked and counted, never opened -----------------------------------


def test_a_file_with_no_current_classification_is_withheld_and_named(
    dossier_conn, corpus,
):
    """§8.4 requires classification before escalation. An unclassified file is
    withheld from the dossier AND named in `omissions`, so a later reader can show
    it as present-but-untouched rather than pretend it was never there."""
    homework_id = corpus["Homework.pdf"][0]
    dossier = _assemble(
        dossier_conn, corpus,
        classification_store=_classified(missing=(homework_id,)),
    )
    assert homework_id not in {item.file_id for item in dossier.candidate_files}
    assert dossier.omissions.privacy_redacted == (homework_id,)
    assert dossier.privacy.redactions_applied == 1
    assert "unreadable_unclassified" in dossier.privacy.handling_classes


def test_withholding_every_anchor_refuses_rather_than_shipping_an_empty_question(
    dossier_conn, corpus,
):
    seed_id = corpus["Syllabus.pdf"][0]
    lecture_id = corpus["Lecture.pdf"][0]
    result = _assemble(
        dossier_conn, corpus,
        classification_store=_classified(missing=(seed_id, lecture_id)),
    )
    assert isinstance(result, DossierRefused)
    assert set(result.withheld) == {seed_id, lecture_id}


def test_the_handling_classes_present_are_recorded(dossier_conn, corpus):
    dossier = _assemble(
        dossier_conn, corpus, classification_store=_classified("sensitive_personal"))
    assert dossier.privacy.handling_classes == ("sensitive_personal",)
    assert dossier.privacy.release_decision_ref is None


# --- omissions are three fields, not one -----------------------------------------


def test_a_neighbourhood_cap_is_a_different_omission_from_a_redaction(
    dossier_conn, corpus,
):
    graph = _graph(corpus, limits=_limits(max_graph_nodes=2))
    dossier = _assemble(
        dossier_conn, corpus, graph=graph, limits=_limits(max_graph_nodes=2))
    assert graph.capped is True
    assert dossier.omissions.neighbourhood_capped
    assert dossier.omissions.privacy_redacted == ()
    assert dossier.budget.files_dropped == len(dossier.omissions.neighbourhood_capped)


def test_p9_drops_nothing_for_a_token_budget(dossier_conn, corpus):
    """M9's summarize -> preserve anchors -> split/defer ladder is P8's. P9 records
    the ceiling it was given and applies none of it."""
    dossier = _assemble(dossier_conn, corpus, limits=_limits(max_dossier_tokens=1))
    assert dossier.budget.token_ceiling == 1
    assert dossier.omissions.budget_cap_dropped == ()
    assert len(dossier.anchor_files) == 2


# --- missing domain knowledge is a refusal, not a guess --------------------------


#: `active_schema_for` WAS THE FIRST OF THREE AND IS GONE (`104` R-09). It was the
#: one of the three that no line in `src/` ever called, so demanding it here demanded
#: a value assembly could not have used; `tests/integration/
#: test_p9_active_schema_slot_retired.py` carries the measurement. The two that stay
#: are read: `classification_store` resolves a handling class for every file in the
#: graph, and `signal_evaluator_for` is P9's own open seam (`104` §14.2).
@pytest.mark.parametrize(
    "absent", ["signal_evaluator_for", "classification_store"])
def test_missing_domain_knowledge_is_configuration_required(
    dossier_conn, corpus, absent,
):
    with pytest.raises(ConfigurationRequired) as excinfo:
        _assemble(dossier_conn, corpus, **{absent: None})
    assert absent in str(excinfo.value)


def test_no_label_or_category_is_ever_written_by_assembly(dossier_conn, corpus):
    """The label is the model's to propose and the user's to approve. P9's
    assembly names the basis it already had and invents nothing."""
    dossier = _assemble(dossier_conn, corpus)
    assert dossier.proposed_basis == "course_code=PHYS1401"
    assert not hasattr(dossier, "display_label")
    assert not hasattr(dossier, "group_category")


# --- the fingerprint is content-derived ------------------------------------------


def test_two_assemblies_of_the_same_references_have_one_fingerprint(
    dossier_conn, corpus,
):
    """A replay has to be able to say two dossiers are the same dossier."""
    first = _assemble(dossier_conn, corpus)
    second = _assemble(dossier_conn, corpus, created_at="2026-09-01T00:00:00Z")
    assert first.dossier_fingerprint == second.dossier_fingerprint
    assert first.dossier_id == second.dossier_id


def test_a_different_reference_set_is_a_different_fingerprint(dossier_conn, corpus):
    full = _assemble(dossier_conn, corpus)
    fewer = _assemble(
        dossier_conn, corpus,
        graph=_graph(corpus, channels={
            "Lecture.pdf": (SHARED_VALIDATED_FACT, True)}))
    assert full.dossier_fingerprint != fewer.dossier_fingerprint


# --- reference-only, enforced by reading the imports -----------------------------


def test_the_dossier_module_reaches_no_gate_no_transport_and_no_p8_dossier():
    """`build_dossier_request` in the P8 seam converts this record into P8's
    `DossierRequest`. P8 alone materialises released evidence through P7."""
    import ast
    import pathlib

    import grouping.dossier as module

    banned = {
        "llm_harness", "privacy.gate", "privacy.release", "privacy.binding",
        "privacy.resolve",
    }
    imported: set[str] = set()
    tree = ast.parse(pathlib.Path(module.__file__).read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {alias.name for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    for name in imported:
        assert not any(
            name == item or name.startswith(item + ".") for item in banned
        ), name


def test_the_dossier_record_carries_no_materialised_or_transport_field():
    import dataclasses

    names = {field.name for field in dataclasses.fields(CandidateGroupDossier)}
    for banned in ("release_id", "released_evidence", "model_call_request",
                   "prompt", "token_estimate", "reduction_rung", "model_client",
                   "split_shards"):
        assert banned not in names, banned


def test_a_conflict_is_carried_and_never_invented(dossier_conn, corpus):
    conflict = Conflict(
        kind="term", competing_values=("Spring", "Fall"),
        file_ids=(corpus["Homework.pdf"][0],))
    dossier = _assemble(dossier_conn, corpus, conflicts=(conflict,))
    assert dossier.conflicts == (conflict,)
    assert _assemble(dossier_conn, corpus).conflicts == ()


# --- the span P9 asks P7 to release ----------------------------------------------


def _request_for(dossier):
    from privacy.release import ModelTarget

    from grouping.p8_seam import build_dossier_request

    return build_dossier_request(
        dossier,
        model_target=ModelTarget(
            locality="local", model_id="m", provider="p"),
        prompt_template_id="template.grouping",
        prompt_fingerprint="sha256:fp",
        max_dossier_tokens=4000)


def test_p9_asks_for_the_whole_citation_when_the_observation_carries_no_span(
    dossier_conn, corpus,
):
    """`privacy/items.py:116`: an `Excerpt.span` of `None` is SS2.3's cell and
    SS2.8's EXIF field -- "the address is the whole citation", a valid reference and
    not a missing value.

    `build_dossier_request` sent `TextSpan(0, len(excerpt.text))` regardless, so
    for an observation with no span P7 refused the whole call:
    `UnresolvableSpan: requested span TextSpan(start=0, end=19) disagrees with the
    live location's span None ... consent records the exact requested reference and
    never repairs one`. The corpus here is that case: every observation's location
    carries `text_span=None`.
    """
    request = _request_for(_assemble(dossier_conn, corpus))

    assert request.model_call_request.requested_items
    for item in request.model_call_request.requested_items:
        assert item.span is None, item


def test_p9_asks_for_exactly_the_span_the_observation_carries(
    dossier_conn, tmp_path,
):
    """The other half: a bounded observation must be requested at ITS bounds, not
    at `(0, len(text))`. The two agree only when the span starts at 0 and the
    excerpt is not truncated, which is why the synthesised value looked right."""
    from evidence_shape.location import TextSpan

    span = TextSpan(9, 17)
    made = {}
    for index, name in enumerate(("Syllabus.pdf", "Lecture.pdf", "Homework.pdf")):
        file_id, content_hash = _record(
            dossier_conn, tmp_path, name=name,
            body=f"PHYS1401 {name}".encode("utf-8"))
        made[name] = (file_id, content_hash, _observe(
            dossier_conn, file_id=file_id, content_hash=content_hash,
            raw=f"PHYS1401 stated in {name}", run_id=f"r-span-{index}",
            text_span=span))

    request = _request_for(_assemble(dossier_conn, made))

    spans = [item.span for item in request.model_call_request.requested_items]
    assert spans, "the request carried no items"
    assert set(spans) == {span}, spans
