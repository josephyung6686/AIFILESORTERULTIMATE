"""A draft's category is a domain, read the way `said().schema` reads one.

The unsettled single-branch path used to pass `Branch.schemas[0]` or, failing
that, the folder's label. `schemas` is documented beside situation names, and
the prefix of `applications.undergraduate-packet` is `applications`, which is
not one of the 23 domains. `Group` then raises `MalformedGroupRecord` where
nothing catches it. A coursework fixture stays green because `academic` is
both a prefix and a domain.

The label is worse: a display string in a closed-vocabulary field.
"""
from __future__ import annotations

from facts.domains import SCHEMA_IDS
from production import (
    domain_for_a_draft, load_shipped_catalogue, read_packaged_library_file,
    schema_for_situation,
)


def _catalogue():
    return load_shipped_catalogue(read_packaged_library_file)


def _situations(catalogue):
    return sorted({signal.removeprefix("recognition:")
                   for row in catalogue.applicabilities.values()
                   for signal in row.detection_signal_refs})


def test_a_situation_whose_name_is_not_its_domain_resolves_to_the_row():
    catalogue = _catalogue()
    situation = "applications.undergraduate-packet"
    domain = domain_for_a_draft(catalogue, situation=situation)
    assert domain == "college_applications"
    assert domain == schema_for_situation(catalogue, situation)
    assert domain != situation.split(".", 1)[0]
    assert domain in SCHEMA_IDS
    # The same answer when the situation was stored where a kind was expected.
    assert domain_for_a_draft(catalogue, kinds=(situation,)) == domain


def test_every_situation_the_prefix_gets_wrong_is_asked_of_the_library():
    catalogue = _catalogue()
    disagreeing = [
        situation for situation in _situations(catalogue)
        if schema_for_situation(catalogue, situation)
        != situation.split(".", 1)[0]]
    assert disagreeing, (
        "the library no longer has a situation whose name and domain disagree, "
        "so this no longer distinguishes reading the row from splitting the name")
    for situation in disagreeing:
        domain = domain_for_a_draft(catalogue, situation=situation)
        assert domain == schema_for_situation(catalogue, situation)
        assert domain in SCHEMA_IDS
        assert domain != situation.split(".", 1)[0]
        assert domain_for_a_draft(catalogue, kinds=(situation,)) == domain


def test_a_kind_that_is_already_a_domain_stays_that_domain():
    """PHYS 1401's branch stores `academic`. That is already a domain, and
    asking the library to treat the domain id as a situation name would refuse."""
    catalogue = _catalogue()
    assert domain_for_a_draft(catalogue, kinds=("academic",)) == "academic"


def test_a_folder_label_is_not_a_domain():
    catalogue = _catalogue()
    assert domain_for_a_draft(catalogue, kinds=("Fall intake",)) is None
    assert domain_for_a_draft(catalogue) is None


def test_two_carried_situations_of_two_domains_are_not_picked():
    catalogue = _catalogue()
    assert domain_for_a_draft(
        catalogue,
        situations=("academic.coursework",
                    "applications.undergraduate-packet")) is None
