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
