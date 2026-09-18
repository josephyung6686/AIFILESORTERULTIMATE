# tests/p10/test_library_lives.py
"""`00` amendment 12 with 12a: every shipped situation is placed in one of the
owner's sixteen lives, and the sixteen are a MENU.

The sixteen are spelled here in the owner's words because they are the owner's
ratified vocabulary (`00` amendment 12, 17 Sep 2026: "use my reference's
list"). They are NOT spelled anywhere in `src/`: the product reads lives off
the rows and never off a list, which is how a life the library never imagined
can be added by the person without a library change (12a(ii)).
"""
from __future__ import annotations

import pytest

from production import (
    life_of, life_of_kind, load_shipped_catalogue, read_packaged_library_file,
    shipped_situations,
)

THE_OWNERS_SIXTEEN = frozenset({
    "Personal", "Family and Household", "Work", "Career", "Education",
    "Teaching", "Finance and Taxes", "Home and Property", "Health",
    "Legal and Insurance", "Vehicles", "Travel", "Photos and Media",
    "Creative and Hobbies", "Technology", "Reference Library",
})


@pytest.fixture(scope="module")
def catalogue():
    return load_shipped_catalogue(read_packaged_library_file)


def test_every_shipped_situation_is_placed_in_a_life(catalogue):
    """SABOTAGE: ship one row without `life`. Its files fall through to the
    default branch on every corpus, with nothing on any screen saying why."""
    missing = sorted(row.name for row in shipped_situations(catalogue)
                     if life_of(catalogue, row.name) is None)
    assert missing == [], missing


def test_every_life_a_row_names_is_one_of_the_owners_sixteen(catalogue):
    """Closed to the model (12a(iii)): the judge reaches a life only through a
    row, so the rows may name only the ratified words. SABOTAGE: a row with
    `"life": "Academics"`. A seventeenth root appears that nobody ratified."""
    named = {row.life for row in catalogue.applicabilities.values()
             if row.life is not None}
    assert named <= THE_OWNERS_SIXTEEN, sorted(named - THE_OWNERS_SIXTEEN)


def test_the_owners_rulings_of_18_sep_are_on_the_rows(catalogue):
    """The owner, reading a tree of exactly this shape over their own files:
    Education holds BOTH `academic` and `research`, and the life called
    `Work` is `Career` -- the whole mapping is theirs to set. SABOTAGE: keep
    `research` under Work. Their 60 research files leave Education."""
    lives_by_kind = {}
    for row in catalogue.applicabilities.values():
        lives_by_kind.setdefault(row.uses_schema, set()).add(row.life)
    assert lives_by_kind["research"] == {"Education"}
    assert "Work" not in {row.life for row in catalogue.applicabilities.values()}


def test_every_kind_has_a_life_and_it_is_one_of_the_owners_sixteen(catalogue):
    """A kind belongs to a life just as its situations do. Measured by the
    lead on the owner's corpus: 218 of 257 situation facts hold the KIND, and
    a life answerable only per situation left one folder standing. Every
    schema P6 can name -- the four with no situation rows included (`medical`
    is the owner's `Health 4`) -- has a life in the library's own table.
    SABOTAGE: drop `medical`. Four health records reach no life."""
    from facts.domains import SCHEMA_IDS
    missing = [schema for schema in SCHEMA_IDS
               if life_of_kind(catalogue, schema) is None]
    assert missing == [], missing
    named = {life_of_kind(catalogue, schema) for schema in SCHEMA_IDS}
    assert named <= THE_OWNERS_SIXTEEN, sorted(named - THE_OWNERS_SIXTEEN)
    assert life_of_kind(catalogue, "academic") == "Education"
    assert life_of_kind(catalogue, "research") == "Education"
    assert "Work" not in named


def test_a_kinds_life_agrees_with_its_rows_where_the_rows_agree(catalogue):
    """The kind's word and its rows' words are two spellings of one table:
    where every row of a kind carries one life, the kind carries that life.
    SABOTAGE: `code` rows Technology, `code` kind Career. A file with the
    finer fact and one with the kind fact land in two folders."""
    rows_by_kind = {}
    for row in catalogue.applicabilities.values():
        rows_by_kind.setdefault(row.uses_schema, set()).add(row.life)
    disagree = sorted(kind for kind, lives in rows_by_kind.items()
                      if len(lives) == 1 and life_of_kind(catalogue, kind) not in lives)
    assert disagree == [], disagree


def test_no_life_is_spelled_in_src():
    """The menu lives in the rows, not in code. A list in `src/` would be the
    skeleton 12a forbids one step from being poured over every corpus."""
    import pathlib
    src = pathlib.Path(__file__).resolve().parents[2] / "src"
    offenders = [path for path in src.rglob("*.py")
                 if "Finance and Taxes" in path.read_text(encoding="utf-8")]
    assert offenders == [], offenders


def test_the_library_alone_does_not_decide_how_many_lives_a_tree_shows(catalogue):
    """12a(i) stated as a property of the READER: `life_of` is per situation,
    so a corpus of coursework alone reaches Education and nothing else. This
    is the pin against a producer that emits every life the library names.
    SABOTAGE: have `partition_by_branch` open a branch per distinct `life` in
    the catalogue -- this test cannot see that, which is why §D's gate exists
    and why `test_branch_situation_lives.py` pins it on the partition."""
    reached = {life_of(catalogue, "academic.coursework")}
    assert reached == {"Education"}
    assert len({row.life for row in catalogue.applicabilities.values()}) > 1
