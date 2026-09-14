# tests/integration/test_a_situation_is_never_the_first_of_twenty_six.py
"""`branch_situation.the_one_situation`, arm by arm, and the library it runs on.

Site G answers in SCHEMAS -- `academic`, `research`, `finance` -- and every reader
below it needs a SITUATION, because the situation is what carries the field
allowlist, the folder levels and the readings. Three places resolved the one to
the other with `situations_of(schema)[0]`: `cli._the_situation_this_file_is_under`
twice (site G's name, and the branch's vote) and `branch_situation.
partition_by_branch` once, for a branch site G opened. All three are the same
silent first pick in alphabetical order, and all three now ask this function.

**THE MEASUREMENT IS IN THIS FILE AND NOT IN A COMMENT**, because it is what makes
the third arm the live one rather than the exception: `test_the_shipped_library_
resolves_no_schema_by_its_shape_alone` counts the shipped release and asserts what
it finds. No schema carries exactly one situation, four carry none, and the rest
carry between two and twenty-eight -- so on this release the first arm never fires
and the pick decided every file site G ever named.

**WHY THE FIRST TWO ARMS ARE PINNED WITHOUT A CORPUS.** They cannot be produced by
one on this release. The first needs a schema with exactly one situation and there
is none; the second needs a recogniser to raise one of a schema's SITUATIONS, and
`recognition.SituationOutcome.candidates` is validated against `facts.domains.
SCHEMA_IDS`, so a candidate is a schema id and can only be a situation name where
the two spellings coincide. `nonprofit` is the one place on the shipped release
where they do, and it is pinned below against the real library. Everywhere else
the second arm is a rule waiting for a library that can feed it, which is what
`situations_of` being a parameter is for.

The third arm is pinned END TO END, on the synthetic corpora of
`test_a_silent_file_is_asked_and_filed_under_one_situation` and
`test_each_file_is_filed_under_its_own_situation`: a file whose situation is
unresolved is asked no fields, is filed nowhere with the reason word
`no_model_judgement`, and its branch's `question_for_situation` is on the screen.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from branch_situation import the_one_situation  # noqa: E402
from facts.domains import SCHEMA_IDS  # noqa: E402
from production import (  # noqa: E402
    load_shipped_catalogue, read_packaged_library_file, shipped_situations,
)

#: The one schema on the shipped release the second arm can fire for: its two
#: situations are `nonprofit` and `nonprofit.member-association`, and the first of
#: them is spelled exactly like the schema a recogniser raises.
NONPROFIT = "nonprofit"


def _situations_of(schema_id: str):
    """`cli._situations_of`, built the way `cli.run` builds it and no other way."""
    catalogue = load_shipped_catalogue(read_packaged_library_file)
    return tuple(row.name for row in shipped_situations(catalogue)
                 if row.schema == schema_id)


# --- the three arms, on a library this test states ------------------------------


def test_one_shipped_situation_under_the_schema_is_the_answer():
    """Arm one. One situation is an answer and not a choice.

    `104` §11.2 step 4 reserves the CHOICE for the person or for a model given
    valid options; where the library carries one option there is no choice to
    reserve, and `branch_situation._situation_for` has settled a branch this way
    since it was written.
    """
    assert the_one_situation(
        "research", situations_of=lambda _s: ("research.thesis-dissertation",),
        raised=()) == "research.thesis-dissertation"
    # And the raised set changes nothing when there is one: it is evidence for
    # telling several apart, not a second vote.
    assert the_one_situation(
        "research", situations_of=lambda _s: ("research.thesis-dissertation",),
        raised=("research.reading-library",)) == "research.thesis-dissertation"


def test_the_one_the_recognisers_raised_for_this_file_is_the_answer():
    """Arm two. Evidence about THIS FILE, and never an order over the library.

    The raised set is `model_situation.raised_for` off `recognition.
    SituationOutcome.candidates` -- what site G was handed about this file -- and
    it is read here rather than a ranking, because there is no ranking to read:
    the library states no preference between a schema's situations and inventing
    one would be this function deciding what kind of material somebody's files
    are.
    """
    assert the_one_situation(
        "research", situations_of=lambda _s: ("research.grants-funding",
                                              "research.reading-library"),
        raised=("research.reading-library",)) == "research.reading-library"
    # A raised name that is not one of the schema's situations decides nothing:
    # the arm asks which of THIS schema's situations was raised.
    assert the_one_situation(
        "research", situations_of=lambda _s: ("research.grants-funding",
                                              "research.reading-library"),
        raised=("finance.cap-table-equity",)) is None


def test_otherwise_nothing_is_picked():
    """Arm three, which is the one the shipped release actually reaches.

    Two situations and nothing to tell them apart is the state the person is
    asked about. `situations_of(schema)[0]` answered `a` here, on nothing but the
    letter it starts with.
    """
    assert the_one_situation(
        "research", situations_of=lambda _s: ("a", "b"), raised=()) is None
    # TWO raised is not a tie broken by order either -- it is two, and a tie
    # decides nothing, which is `_grouped_by_branch`'s own rule.
    assert the_one_situation(
        "research", situations_of=lambda _s: ("a", "b"),
        raised=("a", "b")) is None
    # A schema the library carries no situation for resolves to nothing, which is
    # four of the twenty-three on this release.
    assert the_one_situation(
        "medical", situations_of=lambda _s: (), raised=("medical",)) is None


# --- the shipped library, which is what makes arm three the live one ------------


def test_the_shipped_library_resolves_no_schema_by_its_shape_alone():
    """THE MEASUREMENT. Counted off the release, not written down from memory.

    Every schema `recognition.json` carries, against how many situations
    `shipped_situations` lists under it. If this ever fails because a schema
    gained or lost its one situation, the first arm has come alive for it and the
    number in this file's docstring is the thing to correct.
    """
    catalogue = load_shipped_catalogue(read_packaged_library_file)
    under: dict[str, int] = {schema_id: 0 for schema_id in SCHEMA_IDS}
    for row in shipped_situations(catalogue):
        under[row.schema] = under.get(row.schema, 0) + 1

    assert len(under) == 23, sorted(under)
    assert sum(under.values()) == 208, under
    # NOT ONE of the twenty-three carries exactly one, so the first arm is
    # unreachable on this release and the pick decided every named file.
    assert [schema_id for schema_id, count in under.items() if count == 1] == []
    # Four carry none at all, which is the state `cli` already refuses to build a
    # resolver for.
    assert sorted(schema_id for schema_id, count in under.items()
                  if count == 0) == ["clinical_practice", "identity", "legal",
                                     "medical"]
    # And the rest carry between two and twenty-eight.
    rest = [count for count in under.values() if count]
    assert (min(rest), max(rest)) == (2, 28), sorted(under.items())


def test_the_first_pick_this_replaced_was_alphabetical_order():
    """WHAT THE THREE READERS USED TO SPEND, spelled out on the real library.

    Not a hypothetical: these are the situations `_situations_of(schema)[0]`
    returned for the two schemas the sibling pins measure site G naming, and
    neither is anything but the first name in sorted order.
    """
    assert _situations_of("research")[0] == "research.conference-presentation"
    assert _situations_of("finance")[0] == "finance.cap-table-equity"
    for schema_id in ("research", "finance"):
        situations = _situations_of(schema_id)
        assert list(situations) == sorted(situations)
        assert the_one_situation(schema_id,
                                 situations_of=_situations_of) is None


def test_the_second_arm_is_live_on_the_shipped_library_for_nonprofit():
    """Arm two against the REAL catalogue, at the one place the release allows it.

    `nonprofit` carries two situations and one of them is spelled `nonprofit` --
    the same string a recogniser raises as a schema id. So a file the recognisers
    raised `nonprofit` for resolves to the `nonprofit` situation, and a file they
    raised nothing for does not resolve at all. The arm is a mechanism on this
    release and not only a rule for a future one.
    """
    assert _situations_of(NONPROFIT) == (NONPROFIT,
                                         "nonprofit.member-association")
    assert the_one_situation(NONPROFIT, situations_of=_situations_of,
                             raised=(NONPROFIT,)) == NONPROFIT
    assert the_one_situation(NONPROFIT, situations_of=_situations_of,
                             raised=()) is None
