# tests/integration/test_situation_launch.py
"""Launching a run under a situation, and launching a second one beside it.

Two crashes lived here, and both of them were the first thing a person saw.

The first: `--situation applications.graduate-professional` ended in
`MalformedGroupRecord: group_category='applications' is not one of the 23
domains`. The domain was being read off the SITUATION NAME -- the segment before
the dot -- and the name is the template library's while the domains are
`facts.domains.SCHEMA_IDS`. The two spellings agree for 201 of the library's 208
situations and disagree for seven, so the command worked until somebody picked
one of the seven.

The second: a second situation pointed at a database a first run had already
written ended in `ValueError: a group plan with no member decisions is not a
plan`. P9's group ids are derived from their evidence, so the second run
re-proposes the SAME group -- and the first run had superseded that group's
memberships onto its own merged group. The second run read the proposal it had
just made, found no live members on it, carried none, and asked P11 to plan an
empty branch.

Both are guarded here the same way: over the real shipped library, and over the
real command, because both defects were invisible to every test that supplied its
own fixture library.
"""
from __future__ import annotations

import io
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402
from facts.domains import SCHEMA_IDS  # noqa: E402
from production import (  # noqa: E402
    load_shipped_catalogue, nearest_situations, read_packaged_library_file,
    schema_for_situation, shipped_situations,
)


def _shipped_situations(catalogue):
    return sorted({signal.removeprefix("recognition:")
                   for row in catalogue.applicabilities.values()
                   for signal in row.detection_signal_refs})


def _live_members_by_label(database: Path) -> dict[str, int]:
    """How many files each named group still holds, by the name a person gave it.

    By label rather than by group id: the id is the composition's business and
    has already changed shape once while fixing this, and a guard that spells it
    would fail for a reason that has nothing to do with what it guards.
    """
    conn = sqlite3.connect(database)
    counted = dict(conn.execute(
        "SELECT groups.display_label, count(memberships.membership_id) "
        "FROM groups LEFT JOIN memberships "
        "ON memberships.group_id = groups.group_id "
        "AND memberships.superseded_by IS NULL "
        "WHERE groups.label_source = 'user-edited' "
        "GROUP BY groups.display_label"))
    conn.close()
    return counted


def _corpus(root: Path) -> Path:
    """Files with an identifier in them, so P9 has a group to propose.

    A corpus P9 groups nothing in never reaches the review both defects live in,
    so it would pass these tests by not exercising them.
    """
    corpus = root / "corpus"
    corpus.mkdir()
    (corpus / "personal statement.txt").write_text(
        "Personal statement for the Fall2026 intake.\nFall2026 deadline.\n")
    (corpus / "recommendation.txt").write_text(
        "Recommendation letter, Fall2026 intake.\n")
    return corpus


def test_every_situation_the_command_offers_names_a_domain_the_product_knows():
    """The whole shipped library, resolved the way a run resolves it.

    Named over all 208 rather than over the seven that were broken: the seven are
    an accident of which names somebody chose, and a library that gains a 209th
    situation under a ninth new prefix would reintroduce the crash without
    touching a line of code. What has to hold is the RULE -- a situation's domain
    is the one its own applicability row carries -- and this asserts it wherever
    the library puts it.
    """
    catalogue = load_shipped_catalogue(read_packaged_library_file)
    situations = _shipped_situations(catalogue)
    assert len(situations) > 200, (
        f"only {len(situations)} situations loaded; this is not the shipped "
        "library and the guard below would be asserting almost nothing")

    unrecognised = {situation: schema_for_situation(catalogue, situation)
                    for situation in situations
                    if schema_for_situation(catalogue, situation) not in SCHEMA_IDS}
    assert not unrecognised, (
        f"{len(unrecognised)} situations resolve to something that is not one of "
        f"the {len(SCHEMA_IDS)} domains, so a run under any of them dies in "
        f"`Group.__post_init__`: {unrecognised}")


def test_the_domain_is_read_from_the_library_and_not_from_the_situations_name():
    """The negative twin of the guard above, and the defect stated as data.

    If every situation's name happened to start with its domain, the guard above
    would pass over an implementation that split the name on a dot -- which is
    exactly the implementation that crashed. So this says out loud that the
    library does NOT hold that property: some of its rows are filed under a
    domain their name does not spell, and any rule that reads the name instead of
    the row gets those wrong.
    """
    catalogue = load_shipped_catalogue(read_packaged_library_file)
    disagreeing = {
        situation: (situation.split(".", 1)[0],
                    schema_for_situation(catalogue, situation))
        for situation in _shipped_situations(catalogue)
        if schema_for_situation(catalogue, situation) != situation.split(".", 1)[0]
    }
    assert disagreeing, (
        "every situation now begins with its own domain, so nothing here "
        "distinguishes reading the library from splitting the name -- and the "
        "crash this file guards would come back silently the next time one does "
        "not")


def test_a_situation_whose_name_is_not_its_domain_still_reaches_a_report(tmp_path):
    """The command, end to end, on one of the seven.

    `applications.graduate-professional` is filed under `college_applications`.
    Asserting the CATEGORY and not just the exit code, because a run that
    survived by writing no group at all would exit 0 too.
    """
    database = tmp_path / "plan.sqlite"
    out = io.StringIO()
    code = cli.main([str(_corpus(tmp_path)),
                     "--situation", "applications.graduate-professional",
                     "--label", "Applications", "--user", "jy",
                     "--database", str(database)], out=out)

    assert code == 0, out.getvalue()
    conn = sqlite3.connect(database)
    categories = {row[0] for row in conn.execute(
        "SELECT group_category FROM groups WHERE display_label = 'Applications'")}
    conn.close()
    assert categories == {"college_applications"}, (
        f"the merged group is filed under {categories}; the domain came from the "
        "situation's name rather than from the row the library carries it in")


def test_a_second_situation_in_the_same_database_still_gets_its_files(tmp_path):
    """Two situations, one database -- the second one used to end in a traceback.

    The person here has more than one life and one plan file, which is the
    ordinary case and not an edge one. The assertion is about MEMBERS rather than
    about the exit code: the second run crashed because its group had none, and a
    run whose group is empty has not planned anything for the files it read even
    if it prints a report.
    """
    corpus = _corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    first = io.StringIO()
    assert cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Coursework", "--user", "jy",
                     "--database", str(database)], out=first) == 0, first.getvalue()

    second = io.StringIO()
    code = cli.main([str(corpus), "--situation", "finance.tax-filings",
                     "--label", "Taxes", "--user", "jy",
                     "--database", str(database)], out=second)
    assert code == 0, second.getvalue()

    counted = _live_members_by_label(database)
    assert set(counted) == {"Coursework", "Taxes"}, counted
    assert counted["Taxes"] == counted["Coursework"] > 0, (
        f"the second run holds {counted['Taxes']} of the files the first run "
        f"holds {counted['Coursework']} of. It read the group P9 proposed over "
        "the same corpus and found its members already claimed by the run "
        "before it")


def test_two_situations_sharing_one_label_are_two_groups_and_not_a_collision(
        tmp_path):
    """The same folder name, twice, for two different kinds of material.

    Nothing stops a person calling both of these "Records", and nothing should:
    `--label` names the top-level folder and folder names are not unique across
    a life. The merged group's id is built from the label, so two situations
    under one label used to be asked to be one record with two categories --
    `MalformedGroupRecord: group ... is already recorded with different
    content`, a traceback with nothing wrong behind it.
    """
    corpus = _corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    first = io.StringIO()
    assert cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Records", "--user", "jy",
                     "--database", str(database)], out=first) == 0, first.getvalue()

    second = io.StringIO()
    code = cli.main([str(corpus), "--situation", "finance.tax-filings",
                     "--label", "Records", "--user", "jy",
                     "--database", str(database)], out=second)
    assert code == 0, second.getvalue()

    conn = sqlite3.connect(database)
    categories = sorted(row[0] for row in conn.execute(
        "SELECT group_category FROM groups WHERE display_label = 'Records'"))
    conn.close()
    assert categories == ["academic", "finance"], (
        f"the two runs left {categories} under the label 'Records'; one of them "
        "was written over the other rather than kept beside it")


# ======================================================================================
# Finding a situation in the first place
# ======================================================================================


def test_the_listing_offers_every_situation_a_run_can_actually_be_given():
    """The list a person picks from and the names a run accepts are one set.

    A listing that omitted a situation would hide a working answer; one that
    offered a name `_validate_situation` refuses would send a person to a
    refusal. Both are the same defect -- two enumerations of one thing -- so this
    checks them against each other rather than against a number.
    """
    catalogue = load_shipped_catalogue(read_packaged_library_file)
    offered = [row.name for row in shipped_situations(catalogue)]
    accepted = _shipped_situations(catalogue)

    assert sorted(offered) == accepted, (
        "the listing and the names a run accepts have drifted apart: "
        f"only listed {sorted(set(offered) - set(accepted))}, "
        f"only accepted {sorted(set(accepted) - set(offered))}")
    assert len(offered) == len(set(offered)), (
        "a situation is printed twice, so the same line asks to be read as two "
        "different answers")


def test_every_situation_is_filed_under_the_domain_a_run_would_give_it():
    """The heading a person reads it under is the category their group gets.

    This is what makes the listing worth grouping at all: `travel.trip-photos`
    printed beneath `photos` is not a curiosity, it is the group category the run
    will write. If the two came from different rules, the listing would be
    teaching a person something the command then contradicts.
    """
    catalogue = load_shipped_catalogue(read_packaged_library_file)
    disagreeing = {row.name: (row.schema, schema_for_situation(catalogue, row.name))
                   for row in shipped_situations(catalogue)
                   if row.schema != schema_for_situation(catalogue, row.name)}
    assert not disagreeing, (
        f"{len(disagreeing)} situations are listed under one domain and run "
        f"under another: {disagreeing}")


def test_no_situation_is_offered_as_a_bare_name_with_nothing_to_judge_it_by():
    """208 names with nothing beside them is a list nobody can choose from.

    The folder levels are the library's own `role_bindings` labels, so this
    asserts against shipped data and invents no description. A row that carried
    none would print as a bare name and put the person back where they started.
    """
    catalogue = load_shipped_catalogue(read_packaged_library_file)
    bare = [row.name for row in shipped_situations(catalogue)
            if not row.folder_levels]
    assert not bare, (
        f"{len(bare)} situations would print with nothing beside them: {bare}")
    assert all(label.strip() for row in shipped_situations(catalogue)
               for label in row.folder_levels), (
        "a folder level is blank, which prints as a gap rather than as a level")


def test_a_near_miss_is_told_which_name_it_nearly_typed():
    """The typo case, which is most of them.

    `--list-situations` prints 208 names; a person who has already chosen one and
    mistyped it does not need the list again, they need the letter they dropped.
    """
    catalogue = load_shipped_catalogue(read_packaged_library_file)
    assert "academic.coursework" in nearest_situations(
        catalogue, "academic.courswork")
    assert "applications.undergraduate-packet" in nearest_situations(
        catalogue, "applications.undergrad")


def test_a_name_nothing_resembles_is_answered_with_no_suggestion_at_all():
    """The negative twin, and the reason this is `difflib` and not a substring.

    A person pastes what the refusal prints. A confident wrong suggestion sends
    them to a situation that files their files under the wrong domain, which is
    worse than the flat list they would otherwise fall back to -- so nothing
    close means nothing offered.
    """
    catalogue = load_shipped_catalogue(read_packaged_library_file)
    for nonsense in ("qqqqqqqq", "zzzz.wwww", ""):
        assert nearest_situations(catalogue, nonsense) == (), (
            f"{nonsense!r} was answered with a suggestion a person would paste")

    assert all(name in _shipped_situations(catalogue)
               for name in nearest_situations(catalogue, "academic.courswork")), (
        "a suggestion names something that is not a situation, so taking it "
        "would produce the same refusal again")
