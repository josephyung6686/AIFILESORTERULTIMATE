# tests/integration/test_the_situation_judge_is_shown_the_folder.py
"""`cli.SITUATION_ZONES_LAST`'s own sentence, made true: the path stays first.

That constant says, in the register of a thing already decided -- *"The path stays
first: a folder is named after the situation its files are in, and that is evidence
this site is asked for"* -- and until 13 Sep 2026 nothing expressed it. The order
`ordered_releasable_observations` sorts by is `(zone in zones_last, -citations in
this zone, document order, span start, key)`, and site G asks about no field, so
`zone_evidence_counts` measures nothing, every zone ties at 0, and DOCUMENT ORDER
decides: the folder path went wherever the extractor happened to write it.

Measured on the corpus below at the cloud bound (`cli.SITUATION_DOSSIER_TOKENS_
CLOUD`, 2,750): a text file whose body unit runs to about 2,400 characters spends
2,725 of the 2,750 on that one reading, and the fill then CUTS the folder path,
both metadata readings and the rest of the text. `00`'s amendment of 9 Sep 2026 is
that the stored ceiling is the single bound and that "selected excerpts" means
"whole units, folder paths and OCR text within that ceiling, FOR EVERY TARGET" --
and the cloud route `00` amendment 7(c) opened is the one where the folder was
being dropped, on files where the folder is the only place its situation is named:
an event photograph in a named club's folder carries the club's name nowhere else.

`zones_first` is the mirror of the `zones_last` this site already passes, and
`cli.SITUATION_ZONES_FIRST` is site G's word for it.

THE SABOTAGE EACH TEST CATCHES is named at the test. No model is configured
(`conftest` sets `GRAPH_AGENT_NO_DOTENV=1`) and nothing here reaches a network.
"""
from __future__ import annotations

import io
import sqlite3

import pytest

import cli
from model_facts import document_order, ordered_releasable_observations

#: Long enough that its body unit alone very nearly fills the cloud bound, which is
#: the only condition under which the order can be observed to matter. Below it
#: everything fits and any order is the same dossier.
LONG = "week 3 problem set.txt"
FOLDER = "Photography Club 2026"


#: A RUN OF ITS OWN FOR EVERY TEST, and not one shared across the module (13 Sep
#: 2026). `ordered_releasable_observations` MINTS an opening excerpt and records
#: it, sized by the bound of the call that minted it, so a test reading this file
#: at the local ceiling leaves an excerpt behind that is longer than the cloud
#: ceiling a later test reads it under -- and `released_wire_cost <= ceiling` then
#: takes the body and its opening both off the offer, leaving the path first by
#: default and making `test_the_term_...`'s first assertion depend on which
#: sibling ran before it. Each test states its claim about a run's own database.
@pytest.fixture
def measured(tmp_path_factory):
    root = tmp_path_factory.mktemp("folder")
    corpus = root / FOLDER
    corpus.mkdir()
    (corpus / LONG).write_text(
        "PHYS1401 Problem Set 3\nSpring 2026\nColumbia University\n"
        "Answer every question. Show your working.\n"
        + ("Mechanics and momentum body paragraph. " * 60))
    database = root / "plan.sqlite"
    out = io.StringIO()
    assert cli.main(
        [str(corpus), "--situation", "academic.coursework", "--label",
         "Coursework", "--user", "t", "--database", str(database)],
        out=out) == 0, out.getvalue()
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def _version(conn) -> tuple[str, str]:
    row = conn.execute(
        "SELECT file_id, content_hash FROM files WHERE filename = ?",
        (LONG,)).fetchone()
    assert row is not None, f"{LONG!r} is not in the run"
    return row["file_id"], row["content_hash"]


def _offered(conn, *, ceiling: int, locality: str, zones_first):
    """What site G would carry, asked exactly as `ask_the_situation` asks it."""
    file_id, content_hash = _version(conn)
    return cli.releasable_observations(
        conn, file_id=file_id, content_hash=content_hash,
        limit=cli.FACT_CALL_MAX_RELEASED_OBSERVATIONS, locality=locality,
        ceiling=ceiling, zones_last=cli.SITUATION_ZONES_LAST,
        zones_first=zones_first)


def test_the_folder_path_reaches_the_cloud_judge_under_its_own_bound(measured):
    """SABOTAGE: drop `zones_first=SITUATION_ZONES_FIRST` at `ask_the_situation`'s
    `releasable_observations` call, or empty `cli.SITUATION_ZONES_FIRST`. The
    file's body unit then takes the budget first and this goes red -- which is the
    state measured on 13 Sep 2026."""
    taken = _offered(measured, ceiling=cli.SITUATION_DOSSIER_TOKENS_CLOUD,
                     locality=cli.CLOUD, zones_first=cli.SITUATION_ZONES_FIRST)
    zones = [observation.location.zone for observation in taken]
    assert "path" in zones, (
        "the cloud judge is shown no folder path for this file; `00`'s amendment "
        "of 9 Sep 2026 puts folder paths inside the ceiling for every target, and "
        "a folder is where a situation is often the only thing named")
    assert zones[0] == "path", (
        f"`SITUATION_ZONES_LAST` says the path stays first and the order is "
        f"{zones}; a term that is not in the sort key is a comment, not an order")


def test_the_term_is_what_puts_the_path_first_and_nothing_else_does(measured):
    """The defect itself, so the fix cannot be read as decoration.

    Asked of the ORDER rather than of the fill: `ordered_releasable_observations`
    mints an opening excerpt and RECORDS it, so a second read of the same file
    under a different ceiling is a read of a database the first read changed --
    which is exactly the state this test would otherwise be pinning. The order is
    the property; the fill above is the consequence on the corpus.

    AND ASKED OF THE TIE RATHER THAN OF THE OUTCOME (13 Sep 2026). The half of
    this test that says nothing else puts the path first was written as
    `order(())[0] != "path"`, and that is a coin toss: measured here, the path
    record and this file's opening body reading are BOTH outside `zones_last`,
    both uncited (this call names no field, so `zone_evidence_counts` measures
    nothing and every zone ties at 0), and both carry the same document order and
    the same span start -- so the default sort falls through to
    `observation_key`, a hash of the reading's own content, and the path's
    content is whichever temporary folder the fixture was handed. The assertion
    was red about one run in three for the length of a directory name.

    THE TIE IS THE DEFECT, so the tie is what is pinned: a reading whose place is
    settled by a content hash is a reading nothing puts anywhere, which is
    exactly what `SITUATION_ZONES_LAST`'s sentence claimed was already true. The
    three assertions together are the whole claim -- the terms the default order
    names settle nothing between the path and the text, the ORDER IT RETURNS is
    therefore the two keys' own order and nothing else's, and the term is what
    puts the path first. The middle one is what keeps the product in the test: a
    tie the test computes from two observations would go on holding under a
    printer that put the path first for a reason of its own, and the answer the
    product actually gave is the only thing that would not.

    SABOTAGE: fold `zones_first` into `zones_last`'s term, or re-sort in the
    caller, and one of the two below stops being true."""
    file_id, content_hash = _version(measured)

    def offer(zones_first):
        return ordered_releasable_observations(
            measured, file_id=file_id, content_hash=content_hash,
            locality=cli.CLOUD,
            limit=cli.FACT_CALL_MAX_RELEASED_OBSERVATIONS, fields=(),
            ceiling=cli.SITUATION_DOSSIER_TOKENS_CLOUD,
            zones_last=cli.SITUATION_ZONES_LAST, zones_first=zones_first)

    def settled(observation) -> tuple:
        """Every term the DEFAULT order settles before the content hash."""
        span = observation.location.text_span
        return (observation.location.zone in cli.SITUATION_ZONES_LAST,
                document_order(observation), 0 if span is None else span.start)

    default = offer(())
    path = next(o for o in default if o.location.zone == "path")
    body = next(o for o in default if o.location.zone == "body")
    assert settled(path) == settled(body), (
        f"this file's path record no longer ties with a body reading -- "
        f"{settled(path)} against {settled(body)} -- so the default order does "
        f"place the path on its own and the term cannot be observed to do "
        f"anything on this corpus. Change the fixture rather than deleting the "
        f"test")
    # AND THE PRODUCT'S OWN ANSWER FALLS THROUGH TO THE HASH. Given the tie
    # above, the order it returned for these two IS their key order -- so a term
    # nobody asked for that puts the path first goes red here on every run whose
    # temporary folder hashes high, which is half of them.
    places = [o.observation_key for o in default]
    assert ((places.index(path.observation_key)
             < places.index(body.observation_key))
            == (path.observation_key < body.observation_key)), (
        "something outside the sort's named terms is placing the path: it ties "
        "with a body reading on every one of them and did not come back in the "
        "order their keys give")
    assert [o.location.zone for o in offer(cli.SITUATION_ZONES_FIRST)][0] == "path"


def test_the_local_route_carries_the_same_readings_in_the_new_order(measured):
    """The term changes an ORDER and never what may be released.

    SABOTAGE: make `zones_first` a filter rather than a sort term -- keep only the
    first zone, or drop what is not in it -- and the set below stops matching."""
    without = _offered(measured, ceiling=cli.GROUPING_LIMITS.max_dossier_tokens,
                       locality=cli.LOCAL, zones_first=())
    with_it = _offered(measured, ceiling=cli.GROUPING_LIMITS.max_dossier_tokens,
                       locality=cli.LOCAL, zones_first=cli.SITUATION_ZONES_FIRST)
    assert ({o.observation_key for o in without}
            == {o.observation_key for o in with_it}), (
        "the local ceiling holds every reading either way, so the two fills must "
        "be the same set of readings in a different order")
    assert with_it[0].location.zone == "path"


def test_site_as_own_order_is_untouched(measured):
    """`zones_first` DEFAULTS TO EMPTY and site A passes none.

    SABOTAGE: give the parameter a non-empty default, or pass site G's tuple at
    site A's call, and the fact pass silently re-orders every dossier in the
    product. The two fills below must be identical."""
    file_id, content_hash = _version(measured)
    fields = ("work_type", "subject")
    plain = cli.releasable_observations(
        measured, file_id=file_id, content_hash=content_hash,
        limit=cli.FACT_CALL_MAX_RELEASED_OBSERVATIONS, locality=cli.CLOUD,
        ceiling=cli.GROUPING_LIMITS.max_dossier_tokens, fields=fields)
    spelled = cli.releasable_observations(
        measured, file_id=file_id, content_hash=content_hash,
        limit=cli.FACT_CALL_MAX_RELEASED_OBSERVATIONS, locality=cli.CLOUD,
        ceiling=cli.GROUPING_LIMITS.max_dossier_tokens, fields=fields,
        zones_first=())
    assert ([o.observation_key for o in plain]
            == [o.observation_key for o in spelled])
