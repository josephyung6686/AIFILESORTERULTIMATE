# tests/p10/test_p10_life_attribute.py
"""`00` amendment 12: the applicability row carries the LIFE its situation is
part of, and `production.life_of` reads it exactly as `folder_levels_for` reads
the levels -- off the one row that IS the situation.

Amendment 9 is the line these tests hold: the life is an attribute of the
template the situation points at, never a name derived from the situation.
`life_of("academic.coursework")` answers "Education" because the ROW says so,
and a row that says nothing answers `None` rather than "academic".
"""
from __future__ import annotations

import json

import pytest

from production import life_of, life_of_kind
from tree_design.catalogue import load_catalogue
from tree_design.config import ConfigurationRequired
from tree_design.templates import TemplateApplicability


def _row(situation: str, schema: str, life: str | None):
    raw = dict(
        applicability_id=f"ap.{situation}", applicability_version=1,
        template_id="def.fixture", template_version=1, uses_schema=schema,
        purpose_profile_ref=None, allowed_fields=[], detection_signal_refs=[
            f"recognition:{situation}"], role_bindings=[], exclusions=[],
        provenance=["row:fixture"], privacy_floor=None)
    if life is not None:
        raw["life"] = life
    return raw


def _catalogue(*rows):
    manifest = {"release_id": "rel-lives", "fragments": [], "definitions": [],
                "applicabilities": list(rows)}
    return load_catalogue(lambda: json.dumps(manifest))


def test_a_row_that_states_a_life_loads_it_and_life_of_reads_it():
    """SABOTAGE: derive the life from the situation's dotted prefix. This stays
    green for `academic.coursework` -> some spelling of academic, and RED here,
    because the row says Education and the prefix does not."""
    catalogue = _catalogue(_row("academic.coursework", "academic", "Education"))

    assert catalogue.applicabilities[("ap.academic.coursework", 1)].life == "Education"
    assert life_of(catalogue, "academic.coursework") == "Education"


def test_a_row_that_states_no_life_answers_none_and_not_its_kind():
    """12a: a row the library has not placed in a life is a row with no life.
    SABOTAGE: fall back to `uses_schema`. Then a kind is a life, which is the
    taxonomy of kinds `104` §18.100 measured and amendment 12 removed."""
    catalogue = _catalogue(_row("academic.coursework", "academic", None))

    assert catalogue.applicabilities[("ap.academic.coursework", 1)].life is None
    assert life_of(catalogue, "academic.coursework") is None


def test_a_situation_the_library_does_not_carry_is_refused_not_guessed():
    """`folder_levels_for`'s posture, for the same reason."""
    catalogue = _catalogue(_row("academic.coursework", "academic", "Education"))

    with pytest.raises(ConfigurationRequired):
        life_of(catalogue, "academic.courswork")


def test_a_situation_two_rows_carry_is_refused_not_picked():
    """`schema_for_situation`'s second refusal, for the same reason: picking
    between two rows would be this module deciding which life somebody's files
    belong to."""
    catalogue = _catalogue(
        _row("academic.coursework", "academic", "Education"),
        dict(_row("academic.coursework", "academic", "Teaching"),
             applicability_id="ap.academic.coursework.again"))

    with pytest.raises(ConfigurationRequired):
        life_of(catalogue, "academic.coursework")


def test_a_kind_has_a_life_of_its_own_and_the_situation_is_the_finer_word():
    """The owner's corpus, measured by the lead on 18 Sep: 257 files carry a
    situation fact and 218 of them carry the KIND (`academic`), because the
    level stage that writes the finer value mostly has not run. `life_of` is
    per situation and found no row for a kind, so one life was emitted and
    218 files fell straight through. A kind belongs to a life just as its
    situations do: `academic` is Education whether or not anyone has said
    which coursework it is. `life_of_kind` reads the library's `schema_lives`
    table; `life_of` stays the finer authority where a situation exists.

    SABOTAGE: derive the kind's life from its rows' plurality. A kind with no
    rows (`medical`, the owner's `Health 4`) answers nothing."""
    catalogue = load_catalogue(lambda: json.dumps({
        "release_id": "rel-kinds", "fragments": [], "definitions": [],
        "applicabilities": [_row("academic.teaching", "academic", "Teaching")],
        "schema_lives": {"academic": "Education", "medical": "Health"}}))

    assert life_of_kind(catalogue, "academic") == "Education"
    assert life_of_kind(catalogue, "medical") == "Health"
    assert life_of_kind(catalogue, "code") is None
    assert life_of(catalogue, "academic.teaching") == "Teaching"


def test_a_manifest_with_no_kind_table_loads_and_answers_none():
    """The `privacy_floor` precedent again: every fixture manifest in
    `tests/p10` predates the table."""
    catalogue = _catalogue(_row("academic.coursework", "academic", "Education"))

    assert catalogue.schema_lives == {}
    assert life_of_kind(catalogue, "academic") is None


def test_the_record_defaults_life_to_none_so_older_manifests_still_load():
    """The `privacy_floor` precedent: a row written before the attribute existed
    is a row that states none. SABOTAGE: make `life` required. Every fixture
    catalogue in `tests/p10` stops loading, and so does a frozen tree's
    manifest from before 17 Sep."""
    row = TemplateApplicability(
        applicability_id="ap.x", applicability_version=1, template_id="def.x",
        template_version=1, uses_schema="academic", purpose_profile_ref=None,
        allowed_fields=(), detection_signal_refs=("recognition:x",),
        role_bindings=(), exclusions=(), provenance=("row:fixture",))

    assert row.life is None
