# tests/p6/test_p6_year_cannot_anchor_a_move.py
"""`year` became a folder level, so it joins the fields that cannot carry a file.

**THE SET'S OWN INSTRUCTION, AND THIS IS THE DAY IT NAMED.**
`cli.FIELDS_THAT_CANNOT_ANCHOR_A_MOVE`'s comment says it is *"the list of FIELDS
this catalogue can actually fill"* with a what-or-when role, and *"the day either
changes, this set is where it changes."* Two things had to be true for a field to
belong: a producer fills it, and a folder expects it. `year` has had a producer
since `year_facts`, and as of the `ap.career.recruiting` v2 binding a folder level
expects it. Before that binding it was correctly absent -- the comment's own words
for such a field are "a rule with nothing to act on".

**THE HARM IT NOW PREVENTS IS `00`:42's, ONE FIELD OVER.** Six physics papers were
placed into `Desktop/AP world` on `work_type = exam` alone, because that folder's
only expectation was the one word its files happened to share --
`materialise._project`'s `stated`, recorded on the folder because the level did not
divide and there was no child to put it on. A career branch whose files all carry
one year absorbs `year` the same way. Any other file carrying that year and nothing
else would then be carried into it.

**AND IT DOES NOT COST THE YEAR FOLDER ITSELF.**
`placement.pipeline._without_kind_only_moves` drops a candidate only where the
folder is something ELSE: *"a folder may claim a file on what-kind-or-when alone
exactly when THAT IS WHAT THE FOLDER IS, and never when it is something else that
merely holds some."* A `2024/` node built as the `year` LEVEL carries
`dimension = year`, so it still claims its files. This membership refuses the
absorbed expectation and leaves the real level alone -- which is why the fix is
here and not in the predicate.

`capture_year` stays OUT, and the contrast is the argument: `photos` alone declares
it, so a capture time reaching `photos` is the truth about the file. `year` is
UNIVERSAL -- every schema declares it -- which is the widest possible version of
the reach the set exists to refuse.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402


def test_year_cannot_anchor_a_move_now_that_a_folder_level_binds_it():
    """SABOTAGE: remove `YEAR_FIELD` from the set. A file whose only fact is a
    year can be carried out of the folder it is in, into any folder that absorbed
    that year as a `stated` expectation -- `00`:42's shape on a universal field.
    """
    assert cli.YEAR_FIELD in cli.FIELDS_THAT_CANNOT_ANCHOR_A_MOVE


def test_capture_year_is_still_out_and_that_is_the_contrast():
    """The membership rule is about REACH, not about the word "year".

    SABOTAGE: add `CAPTURE_YEAR_FIELD` too. A capture time reaching `photos` is
    the truth about the file, and refusing it would refuse the photos tree its own
    evidence -- the over-refusal this package has already met three times.
    """
    assert cli.CAPTURE_YEAR_FIELD not in cli.FIELDS_THAT_CANNOT_ANCHOR_A_MOVE


def test_the_set_is_exactly_the_fields_a_producer_fills_and_a_folder_expects():
    """The whole set, pinned, so a later addition has to argue for itself here.

    SABOTAGE: add a field no folder level binds. The rule gains a member with
    nothing to act on, which is the comment's own reason for leaving `media_type`
    out.
    """
    assert cli.FIELDS_THAT_CANNOT_ANCHOR_A_MOVE == frozenset(
        {*cli.TYPE_KEYS, cli.TERM_FIELD, cli.YEAR_FIELD})
