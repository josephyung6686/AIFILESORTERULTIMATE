# tests/p6/test_p6_the_situation_question_is_asked_once_per_accepted_group.py
"""`00` amendment 32: ONE ANSWER SETTLES A PACKET, not one answer per file.

**THE MEASUREMENT THE OWNER RULED ON.** 218 of 257 situation facts still carry
only a KIND. Site G names the kind (amendment 30) and the situation within it is
the person's answer -- and the only per-file door to that answer is
`--situation-of FILE=SITUATION`, one line per file. A question asked once per
file is a question nobody finishes, and the corpus is the evidence.

**WHY A GROUP IS THE RIGHT UNIT AND A KIND IS NOT.** Coursework and teaching both
mention the same institution and the same course vocabulary, so the course code
discriminates nothing. The discriminator is the HOLDER'S ROLE -- author or
recipient -- and a role is constant across a course-term. P9's accepted group IS
that course-term packet, so one answer over it is an answer about every file in
it. **What that costs, and the owner accepted it: a group holding both roles gets
one answer applied to all of it.**

**THE THREE THINGS THIS MUST NOT COST, one test each below.**

1. **OLD KEYS STILL READ.** The per-group key is a NEW key. Every answer already
   in the person's database is filed under the bare kind (`situation:academic`)
   or under the default's own scope, and amendment 28 ruled in as many words that
   the old key is read as a FALLBACK and not migrated away -- *"a reader that
   looks only for the new key silently loses every answer they have already
   given, and no test would catch it, because the fixtures write both halves"*.
   So the old key here is CONSTRUCTED BY HAND, as a literal string, and never by
   running the writer that would agree with the reader whatever both did.
2. **COVERAGE IS SACRED.** A file in no accepted group keeps the question it has
   today, at the key it has today. The residue is not a rounding error.
3. **THE QUESTION IS STILL PRINTED.** The saving must not come from swallowing a
   question: every open file is in exactly one question, and the question minted
   for a group is a real `question_for_situation` with a key the person can type.

Unit-level and in `files_of_kind_still_open`'s own module shape, for that
function's reason: the rule is about a handful of inputs, and site G -- which is
what puts files of a named kind in front of this loop at all -- does not run under
`offline`, so there is no deterministic corpus that reaches it.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from cli import (  # noqa: E402
    groups_of_files_still_open,
    situation_scope_of_group,
    the_situation_chosen_for,
)
from questions.triggers import question_for_situation  # noqa: E402

#: One kind, three files, two accepted packets and a file in neither. The shape a
#: person's real corpus has: two course-terms P9 grouped and accepted, and a
#: loose file no group claimed.
OPEN = ("syllabus", "lecture", "marking", "loose")

#: Which accepted group each file is in, by the group's own name. `loose` is in
#: none, which is not a defect -- P9 accepts what it can and the rest stays loose.
GROUPS = {"syllabus": "Term One BIO 101",
          "lecture": "Term One BIO 101",
          "marking": "Term Two BIO 210"}

KIND = "academic"
TWO_SITUATIONS = ("academic.coursework", "academic.teaching")


def _group_of(file_id):
    return GROUPS.get(file_id)


def _in_no_group(_file_id):
    """The first run over any corpus: P9 has accepted nothing yet."""
    return None


def test_one_question_per_accepted_group_and_not_one_per_file():
    """THE RULING, as one assertion.

    Four open files, two accepted packets and a loose file: THREE questions, not
    four. The two files of one course-term are one question because their holder's
    role is one role.

    SABOTAGE: return one pair per file. The person is asked four times about four
    files, which is the state amendment 32 was ruled against and the state 218 of
    257 situation facts are in.
    """
    assert groups_of_files_still_open(OPEN, group_of=_group_of) == (
        ("Term One BIO 101", ("syllabus", "lecture")),
        ("Term Two BIO 210", ("marking",)),
        (None, ("loose",)))


def test_a_file_in_no_accepted_group_keeps_the_kinds_own_question():
    """COVERAGE IS SACRED. The residue is a question, not a remainder.

    A file P9 grouped with nothing is exactly the file this change is most able to
    lose: it belongs to no packet, so a loop that asks packets asks it nothing --
    no situation, no question, and no way to acquire either. It keeps the KIND's
    question, which is the question it has today, and the residue is LAST so the
    packets are read first.

    SABOTAGE: drop the `None` pair. Every ungrouped file in the corpus falls out
    of every question and is silently unanswerable.
    """
    assert groups_of_files_still_open(OPEN, group_of=_in_no_group) == (
        (None, OPEN),)

    assert groups_of_files_still_open(("loose",), group_of=_group_of) == (
        (None, ("loose",)),)


def test_every_open_file_is_in_exactly_one_question():
    """THE QUESTION IS STILL PRINTED, counted rather than asserted about.

    The saving amendment 32 buys is fewer QUESTIONS over the same files, never
    fewer files. Nothing may be dropped and nothing may be asked twice -- a person
    answering one packet and finding the same file inside another is `00`:57's
    question nobody should see twice.

    SABOTAGE: any filter inside the split. The sum stops matching and this says
    which file went missing.
    """
    asked = [file_id
             for _group, files in groups_of_files_still_open(
                 OPEN, group_of=_group_of)
             for file_id in files]

    assert sorted(asked) == sorted(OPEN)
    assert len(asked) == len(set(asked))


def test_the_answer_already_in_the_database_under_the_bare_kind_is_still_read():
    """AMENDMENT 28'S WHOLE RISK, pinned where amendment 32 creates it again.

    THE OLD KEY IS BUILT BY HAND. `chosen_at` is a literal map with one literal
    entry, `"academic"`, which is what `selected_situation(conn,
    scope="branch:academic")` reads and what every answer already in the person's
    database is filed under. Nothing in this test runs the writer: a fixture that
    wrote the key through the code under test would agree with it whichever key
    that turned out to be, which is precisely why amendment 28 records that no
    test caught this.

    SABOTAGE: read the group's key alone. Every standing answer the person has
    given is lost in silence, and their corpus reverts to unanswered.
    """
    standing = {"academic": "academic.coursework"}

    assert the_situation_chosen_for(
        "syllabus", KIND, group_of=_group_of,
        chosen_at=standing.get) == "academic.coursework"


def test_the_packets_own_answer_outranks_the_kinds():
    """The refinement, and it is only ever a refinement.

    An answer given about THIS packet is about these files; an answer at the kind
    is about every file of that kind the person has ever had. The narrower word
    wins, exactly as `--situation-of`'s per-file word already outranks the
    branch's.

    SABOTAGE: read the kind first. The packet question is recorded, printed,
    answered -- and has no effect, which is worse than not asking it.
    """
    standing = {"academic": "academic.coursework",
                situation_scope_of_group(KIND, "Term Two BIO 210"):
                    "academic.teaching"}

    assert the_situation_chosen_for(
        "marking", KIND, group_of=_group_of,
        chosen_at=standing.get) == "academic.teaching"
    # AND THE OTHER PACKET IS NOT TOUCHED BY IT. One answer settles one packet;
    # a second packet of the same kind still reads the kind's standing answer.
    assert the_situation_chosen_for(
        "syllabus", KIND, group_of=_group_of,
        chosen_at=standing.get) == "academic.coursework"


def test_a_file_in_no_group_reads_the_kinds_key_and_nothing_else():
    """The read half of COVERAGE IS SACRED, and the first run's whole behaviour.

    Before P9 has accepted anything -- which is every first run -- `group_of` is
    `None` everywhere, no group key exists, and the reader must behave exactly as
    it does today.

    SABOTAGE: compose a key out of a `None` group. The reader asks for
    `academic/None`, finds nothing, and a corpus with no accepted groups loses
    every answer it has.
    """
    asked_for: list[str] = []

    def _watch(key):
        asked_for.append(key)
        return {"academic": "academic.coursework"}.get(key)

    assert the_situation_chosen_for(
        "loose", KIND, group_of=_in_no_group, chosen_at=_watch
    ) == "academic.coursework"
    assert asked_for == ["academic"]


def test_the_key_asked_under_is_the_key_the_question_was_recorded_under():
    """THE ONE FAILURE THAT WOULD BE SILENT: ask and read disagreeing.

    The person reads a question, types its id back with an answer, and a reader
    that composed the key differently finds nothing -- a recorded question, a
    recorded answer, and no effect. So the key the question is RECORDED under and
    the key the reader ASKS for are built by one function, and this pins that they
    are the same string end to end.

    SABOTAGE: change either side's composition. The question id and the key the
    reader asks for stop matching, and this names both.
    """
    group = "Term One BIO 101"
    key = situation_scope_of_group(KIND, group)
    question = question_for_situation(
        branch_label=group, situations=TWO_SITUATIONS, file_count=2,
        scope_label=key)
    asked_for: list[str] = []

    the_situation_chosen_for("syllabus", KIND, group_of=_group_of,
                             chosen_at=lambda k: asked_for.append(k))

    assert question.question_id == f"situation:{key}"
    assert asked_for[0] == key
    # AND THE KIND'S OWN KEY IS UNTOUCHED BY THE COMPOSITION -- it is the kind,
    # bare, which is what amendment 28's fallback and every standing answer need.
    assert key != KIND and asked_for[-1] == KIND
