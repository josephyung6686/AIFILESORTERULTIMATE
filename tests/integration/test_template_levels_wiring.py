# tests/integration/test_template_levels_wiring.py
"""From the shipped template library to the bytes the model is shown.

`tests/p8/test_p8_folder_levels.py` pins what the dossier does with a level list.
This pins where the list comes from -- the library the owner already ratified --
and that the composition root is the only place that reads it.

**The route.** `--situation` names one applicability row. That row carries
`role_bindings` (role -> field -> the label a person reads, "Kind of work"), and the
template definition it points at carries `default_order.dimensions` (the order the
levels are built in, and `required` or `optional` for each). Joining the two is the
whole of the answer, and until now nothing joined them for the model: `production.
shipped_situations` took the labels alone, for a menu, in `role_bindings` order.

**Why the order is the definition's and not the row's.** They agree for 206 of the
208 situations and disagree for two, and the definition's `order_index` is the one
that says which folder sits above which.
"""
from __future__ import annotations

import pytest

from cli import fact_call_authorities, load_shipped_catalogue, read_packaged_library_file
from facts.domains import DOMAIN_FIELDS, UNIVERSAL_SCOPE
from llm_harness.records import FolderLevel
from production import folder_levels_for, schema_for_situation, shipped_situations
from tree_design.config import ConfigurationRequired


@pytest.fixture(scope="module")
def catalogue():
    return load_shipped_catalogue(read_packaged_library_file)


def test_coursework_resolves_to_the_four_levels_the_library_declares(catalogue):
    """The situation the ground-truth corpus is scored under, in full.

    `subject` and `work_type` are `required`; `work_type` is the one the measured
    run filled once in 199 files.
    """
    assert folder_levels_for(catalogue, "academic.coursework") == (
        FolderLevel(field="school", label="My school", requirement="optional"),
        FolderLevel(field="term", label="Semester", requirement="optional"),
        FolderLevel(field="subject", label="Course", requirement="required"),
        FolderLevel(field="work_type", label="Kind of work", requirement="required"),
    )


def test_every_shipped_situation_yields_at_least_one_level(catalogue):
    """208 of 208. This is what lets the A_fact composition REFUSE an empty list
    instead of treating it as a situation that happens to design no folders."""
    for situation in sorted({row.name for row in shipped_situations(catalogue)}):
        levels = folder_levels_for(catalogue, situation)
        assert levels, situation


def test_every_level_field_is_inside_that_situations_own_allowlist(catalogue):
    """The projection invariant, at the source rather than at the door.

    `active_field_allowlist` is the universal fields plus `DOMAIN_FIELDS[schema]`.
    A level naming a field outside that would be the model told to fill a key the
    validator rejects for not being in the active schema -- the exact failure
    `pending_fields_for` warns about -- so it is checked across all 208 rows here,
    where a library edit meets it, and not only on the one situation we measure.
    """
    universal = {"file_type", "creation_date", "language", "authored_by",
                 "media_type", "duplicate_family"}
    for situation in sorted({row.name for row in shipped_situations(catalogue)}):
        schema = schema_for_situation(catalogue, situation)
        allowed = set(DOMAIN_FIELDS.get(schema, ())) | universal
        for level in folder_levels_for(catalogue, situation):
            assert level.field in allowed, (situation, schema, level.field)


def test_a_situation_the_library_does_not_carry_is_refused(catalogue):
    with pytest.raises(ConfigurationRequired):
        folder_levels_for(catalogue, "academic.courswork")


def test_the_labels_are_the_librarys_own_and_not_authored_here(catalogue):
    """Every label a dossier can carry is a `RoleBinding.label` from the shipped
    release. Nothing in `src/` may mint one: the glossary rule -- meanings are
    transcribed, never authored -- holds for these too."""
    shipped = {label for row in catalogue.applicabilities.values()
               for label in (binding.label for binding in row.role_bindings)}
    for situation in sorted({row.name for row in shipped_situations(catalogue)}):
        for level in folder_levels_for(catalogue, situation):
            assert level.label in shipped, (situation, level.label)


# --- the composition root is the only place that chooses ------------------------


def test_the_fact_call_authorities_will_not_be_built_without_levels(conn):
    """"Absent means refuse, never guess." A deployment that forgot the levels gets
    a `TypeError` at composition, not a dossier that quietly asks the old question."""
    with pytest.raises(TypeError):
        fact_call_authorities(
            conn, routing=None, scan_run_id="scan-1", corpus_file_count=1,
            policy_version="policy-1", wire_handle_key=b"k" * 32,
            schema="academic", user_id="user-1", now=lambda: "2026-09-04T00:00:00Z")


def test_an_empty_level_list_is_refused_at_site_a():
    """Every situation has levels, so an empty list at A_fact is a wiring failure
    rather than a situation with nothing to build -- and it would be invisible: the
    dossier is well-formed and the model is simply asked the old question again."""
    from model_facts import require_folder_levels

    with pytest.raises(ValueError):
        require_folder_levels(())
    with pytest.raises(TypeError):
        require_folder_levels(({"field": "subject"},))
    assert require_folder_levels(
        [FolderLevel(field="subject", label="Course", requirement="required")]
    ) == (FolderLevel(field="subject", label="Course", requirement="required"),)


def test_the_vocabulary_the_model_reads_leads_with_the_levels(catalogue):
    """Same SET, different order -- and the set is what the validator holds.

    `active_field_allowlist` lists the universal rows first, so the model read
    `file_type`, `creation_date`, `language` and `authored_by` before it reached any
    field the person's situation builds a folder out of. It answered in that order:
    59, 19, 4 and 34 of them against one `work_type`. The levels lead now, in the
    library's own order, and membership is untouched -- reordering a list the
    validator reads by membership cannot reject an answer it used to accept.
    """
    from model_facts import order_vocabulary_by_levels

    allowlist = ("file_type", "creation_date", "language", "authored_by",
                 "media_type", "duplicate_family",
                 "school", "term", "subject", "instructor", "work_type")
    ordered = order_vocabulary_by_levels(
        allowlist, folder_levels_for(catalogue, "academic.coursework"))
    assert ordered[:4] == ("school", "term", "subject", "work_type")
    assert sorted(ordered) == sorted(allowlist)
    assert len(ordered) == len(allowlist)


def test_a_level_the_allowlist_does_not_carry_is_refused_rather_than_prepended():
    """The one-computation rule again, at the seam that builds the printed list."""
    from model_facts import order_vocabulary_by_levels

    with pytest.raises(ValueError):
        order_vocabulary_by_levels(
            ("file_type",),
            (FolderLevel(field="subject", label="Course", requirement="required"),))


# --- a settled field is not a question ------------------------------------------


def test_the_open_question_drops_fields_a_stronger_fact_has_already_closed(catalogue):
    """The dossier asks about what is still OPEN, not about the whole schema.

    Measured on a real cloud run: of the 27 files the model answered about, 8 already
    carried a `work_type` written by a rule at `validated` strength. §3.13 ranks
    `validated` above `llm_supported`, so check 4 rejects any model answer there
    before it can become a fact. The model was spending a claim on a closed question
    and being punished for it, and every extra claim is another chance to malform --
    one malformed claim destroys every claim in the answer.

    `pending_fields_for` already computes the open set and `model_fact_resolver`
    already calls it. This is that same tuple reaching the bytes.
    """
    from model_facts import open_question

    levels = folder_levels_for(catalogue, "academic.coursework")
    pending = ("file_type", "creation_date", "school", "term", "work_type")

    vocabulary, visible = open_question(pending, levels)
    assert vocabulary == ("school", "term", "work_type")
    # `subject` is settled, so it is neither offered as a field nor shown as a level.
    assert [level.field for level in visible] == ["school", "term", "work_type"]
    # UPDATED 2026-09-05 under Constitution 3. This read
    # `sorted(vocabulary) == sorted(pending)` -- every pending field offered, levels
    # merely sorted first. `file_type` and `creation_date` are pending and can never
    # become a folder of this situation, so they are no longer offered at all. The
    # measured cost of offering them is in `open_question`'s own comment.
    assert set(vocabulary) <= {level.field for level in levels}


def test_a_file_whose_levels_are_all_settled_is_not_asked_at_all(catalogue):
    """RENAMED AND REVERSED 2026-09-05, under Constitution 3.

    It used to read `..._is_asked_about_the_rest` and assert that `file_type` and
    `language` were still worth a call. They are not. Neither can become a folder of
    this situation, so a call spending them buys nothing the tree can use -- measured
    at 28 `file_type` and 16 `authored_by` answers on one 199-file run, against zero
    `subject`.

    An empty vocabulary here is truthful and is NOT the composition failure
    `require_folder_levels` refuses: the situation has four levels and this file has
    none still open. `model_facts`' own first refusal -- "nothing pending, so the
    question has no content and the spend buys a repetition of what is known" --
    then declines to build the call, which is the cheapest correct outcome.
    """
    from model_facts import open_question

    levels = folder_levels_for(catalogue, "academic.coursework")
    vocabulary, visible = open_question(("file_type", "language"), levels)
    assert vocabulary == ()
    assert visible == ()


def test_the_narrowed_list_is_never_wider_than_what_the_validator_holds(catalogue):
    """The direction of the one-computation rule that matters.

    Check 1 measures a proposal against `FactRequest.allowlist`, the FULL active
    schema. Showing the model a SUBSET of that is safe -- everything it is offered is
    something the validator accepts. Showing it a SUPERSET would be the failure
    `pending_fields_for` names, so the subset relation is asserted rather than
    assumed.
    """
    from model_facts import open_question

    levels = folder_levels_for(catalogue, "academic.coursework")
    allowlist = ("file_type", "creation_date", "language", "authored_by",
                 "school", "term", "subject", "instructor", "work_type")
    for settled in ("subject", "work_type", "school", "file_type"):
        pending = tuple(f for f in allowlist if f != settled)
        vocabulary, visible = open_question(pending, levels)
        assert set(vocabulary) <= set(allowlist)
        assert settled not in vocabulary
        assert all(level.field in vocabulary for level in visible)


def test_the_stage_asks_open_question_about_pending_and_not_the_whole_allowlist():
    """The call site, pinned -- because `open_question` is correct either way.

    Every test above passes an explicit `pending` tuple, so all of them stay green
    if `fact_call_stage` hands over `request.allowlist` instead. Sabotaging exactly
    that produced no red test, which is the definition of an unguarded seam: the
    whole point of narrowing is lost and nothing says so.

    AST rather than prose, the way `tests/p8/test_p8_architecture.py` reads import
    directions: a docstring explaining which tuple is meant must not satisfy it.
    """
    import ast
    import inspect

    import model_facts

    tree = ast.parse(inspect.getsource(model_facts))
    stage = next(node for node in ast.walk(tree)
                 if isinstance(node, ast.FunctionDef)
                 and node.name == "fact_call_stage")
    calls = [node for node in ast.walk(stage)
             if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Name)
             and node.func.id == "open_question"]
    assert len(calls) == 1, "one question per call, built in one place"
    first = calls[0].args[0]
    assert isinstance(first, ast.Name) and first.id == "pending", (
        "the vocabulary offered is the PENDING set. `request.allowlist` here is the "
        "whole active schema, which spends claims on questions a stronger fact has "
        "already closed and gives the answer more ways to malform")


def test_the_model_is_shown_the_filename_and_not_only_the_body():
    """§7.7's sixth releasable kind is BUILT, GATED, and never constructed.

    **Measured on the owner's 199 files before this test existed.** Every file
    carries exactly one `filename` observation and one `path` observation -- the
    only two zones present on all 199 -- and `releasable_observations` drops both
    because they are in `ALWAYS_LOCAL_ZONES`. Dropping them there is RIGHT for what
    it refuses: a filename arriving as an `Excerpt` is the sixth kind coming through
    a door where §7.3's protected-records ban does not apply, which `privacy.
    vocabulary` says in those words.

    The defect is that nothing then sends it through the door where the ban DOES
    apply. `Filename(file_id=...)` exists, `items.UNRATIFIED_ITEM_KINDS` names it,
    and `gate._precheck_items` passes `allow_unratified=True` for the express
    purpose of admitting it for ordinary files and refusing it as
    `ProtectedItemRequested` for protected ones. The only construction of one in
    `src/` is a fixture. So the model is asked what kind of work a file is while
    being shown, for `Desktop/Python 1006/homework0.py`, two metadata rows and
    nothing else -- with the word `homework` sitting in a field it never receives.

    The reference is a `file_id`, never a name: the gate resolves it, and `Filename`
    itself raises `AlwaysLocalRequested` on an id carrying a path separator.
    """
    from llm_harness.records import PromptDefinition
    from llm_harness.vocabulary import A_FACT
    from model_facts import build_fact_request
    _HASH = "a" * 64
    from evidence_shape.location import Location, Segment, TextSpan
    from evidence_shape.observation import Observation
    from privacy.items import Filename
    from privacy.release import ModelTarget

    from facts.llm_seam import FactRequest

    #: One ordinary body reading, so the dossier is well formed and the assertion is
    #: about what was ADDED beside it rather than about an empty request.
    reading = Observation(
        file_id="file-1", content_hash=_HASH, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document",
        raw_value="Homework 3", occurrence_count=1, observed_at="2026-09-05T00:00:00Z",
        reliability="possible", run_id="r-1",
        location=Location("heading", (Segment("field", label="h1"),),
                          TextSpan(0, 10)))
    request = FactRequest(
        file_id="file-1", content_hash=_HASH, allowlist=("work_type",),
        citable_observations=(reading,), existing_facts=(), normalizers={})
    built = build_fact_request(
        request, (reading,),
        model_target=ModelTarget(
            locality="cloud", model_id="m", provider="p"),
        prompt=PromptDefinition(
            template_id="t", template_bytes=b"{}", response_schema_bytes=b"{}",
            call_site=A_FACT, call_site_version="1", shaping_policy_bytes=b"{}"),
        max_dossier_tokens=1000)

    assert Filename(file_id="file-1") in built.model_call_request.requested_items


def test_the_model_is_never_offered_a_field_that_cannot_become_a_folder(catalogue):
    """Constitution 3: never ask the model to choose among structurally invalid options.

    **Measured, cloud run, 199 real files, 2026-09-05.** The model answered
    `file_type` 28 times, `authored_by` 16, `creation_date` 9 -- and `subject`, the
    REQUIRED level of the situation being run, zero. Every one of those answers is
    tokens bought and thrown away: the library says in its own words that
    "instructor, authored_by and programming_language may never become a level", and
    a `file_type` fact cannot divide a branch either.

    `open_question` used to offer everything still pending and merely SORT the levels
    to the front. Ordering does not stop a model answering what it was offered. The
    situation's own `role_bindings` already name the fields this person's tree is
    built from, so those are the valid options and the rest are not options at all.

    The subset direction that `test_the_narrowed_list_is_never_wider_than_what_the_
    validator_holds` pins is unaffected and is strengthened: a narrower list is still
    inside `FactRequest.allowlist`, so nothing offered can be rejected by check 1.
    """
    from model_facts import open_question

    levels = folder_levels_for(catalogue, "academic.coursework")
    level_fields = {level.field for level in levels}
    pending = ("file_type", "creation_date", "language", "authored_by",
               "instructor", "school", "term", "subject", "work_type")

    vocabulary, visible = open_question(pending, levels)

    assert set(vocabulary) <= level_fields, (
        f"offered {sorted(set(vocabulary) - level_fields)}, which no folder of "
        f"academic.coursework can ever be built from")
    assert "subject" in vocabulary and "work_type" in vocabulary
    assert {level.field for level in visible} <= level_fields
