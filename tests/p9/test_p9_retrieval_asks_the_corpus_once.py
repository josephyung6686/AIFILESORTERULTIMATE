"""Retrieval asked the database once per candidate file, for every seed.

Three of P9's six channels read a candidate's facts one file at a time --
`_shared_fact_neighbors` through `proposal_eligible`, and `_family_or_session_neighbors`
twice, through `family_facts` and `session_facts`. `run_production_p8_p11` runs
`group_subject` over every file in the corpus, so a corpus of N files issued about 3N
statements per seed and 3N-squared statements per run.

Measured, P8--P11 over a 1,000-file synthetic corpus under cProfile: 2,273,532 calls to
`facts_for_file`, 1,905,098 of them from these three channels, and `retrieve_neighbors`
holding 46.7 of the 106.9 profiled seconds. It is not a constant to be shaved -- it is
the shape that stopped a 5,000-file plan from finishing: five times the files is
twenty-five times the statements.

The answer each channel needs is a property of the CORPUS and not of one candidate:
"which file versions state this exact field and value", and "which state any of the
values the seed states". Each is one statement. So the growth rate is what this file
asserts, because a fix that only made each statement faster would leave the shape intact
and still pass any wall-clock test on a small corpus.

`00`:257 bounds what retrieval may KEEP -- "a vague file should not retrieve five hundred
weakly related neighbors" -- and says nothing about how many statements it takes to find
them. Nothing here moves that bound. The neighbours kept, their order and their channels
are unchanged; `test_p9_retrieval.py` is what holds that, and the second test below pins
the bulk reads to the per-file reads they replace so the two cannot drift apart later.
"""
from __future__ import annotations

import pytest

from database_agent.budget import set_ceiling
from database_agent.db import create_schema
from evidence_shape.schema import create_evidence_schema
from facts.fields import create_fields
from facts.read_surface import (
    DOWNLOAD_SESSION_FIELD, VERSION_FAMILY_FIELD, family_facts,
    proposal_eligible, session_facts,
)
from grouping.retrieval import RetrievalKnowledge, _values, retrieve_neighbors
from grouping.config import grouping_limits
from grouping.vocabulary import (
    BOUNDED_SESSION, COMPATIBLE_DOCUMENT_TYPE, DUPLICATE_OR_VERSION_LINK,
    EXISTING_RELATED_FOLDER, SHARED_VALIDATED_FACT,
)

from p9.test_p9_retrieval import CEILINGS, _fact, _file, _hash, _seed

#: Two corpus sizes, three times apart. A quadratic reader does nine times the work
#: between them and a linear one does three; anything below the bar below is the
#: linear shape, and 8.8 was measured before the fix.
SMALL, LARGE = 20, 60

#: The bar. Generous on purpose -- the per-seed constant (the corpus read, the seed
#: row, and one statement per bulk channel) is not identical at the two sizes, so the
#: ratio never lands exactly on 3.0. It is nowhere near 8.8 either.
LINEAR_ENOUGH = 4.0


@pytest.fixture()
def corpus(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_fields(conn)
    for key, value in CEILINGS.items():
        set_ceiling(conn, key, value)
    return conn


def _knowledge() -> RetrievalKnowledge:
    return RetrievalKnowledge(
        domain="academic",
        channel_weights={
            SHARED_VALIDATED_FACT: 5, DUPLICATE_OR_VERSION_LINK: 4,
            COMPATIBLE_DOCUMENT_TYPE: 3, EXISTING_RELATED_FOLDER: 2,
            BOUNDED_SESSION: 1,
        },
        document_compatible=lambda domain, left, right: left == right,
        similarity=None, similarity_threshold=None, embedding_identity=None,
    )


def _limits(conn):
    return grouping_limits(
        conn, generic_hub_frequency=25, minimum_independent_anchors=2,
        max_excerpt_characters=240,
    )


def _build(conn, tmp_path, files: int) -> list[str]:
    """A corpus where every channel has something to find.

    Every file states the same subject, so the shared-fact channel matches all of
    them; half share a version family and half a download session, so channels 2 and
    5 do real work too. A corpus where the channels found nothing would let a reader
    that short-circuits on an empty result pass this file while still being quadratic
    on a real one.
    """
    ids: list[str] = []
    for index in range(files):
        file_id = _file(conn, tmp_path, f"{index:03d}-notes.pdf",
                        folder=f"Coursework/week-{index % 3}")
        _fact(conn, file_id, field_key="subject", value="PHYS1401",
              run_id=f"run-subject-{index}")
        if index % 2 == 0:
            _fact(conn, file_id, field_key=VERSION_FAMILY_FIELD, value="family-a",
                  reliability_state="possible", run_id=f"run-family-{index}")
        else:
            _fact(conn, file_id, field_key=DOWNLOAD_SESSION_FIELD,
                  value="session-a", reliability_state="possible",
                  run_id=f"run-session-{index}")
        ids.append(file_id)
    return ids


def _statements_for_a_whole_pass(conn, tmp_path, files: int) -> int:
    """One `retrieve_neighbors` per file, which is what the corpus loop does."""
    ids = _build(conn, tmp_path, files)
    knowledge, limits = _knowledge(), _limits(conn)
    counted = 0

    def count(_statement: str) -> None:
        nonlocal counted
        counted += 1

    conn.set_trace_callback(count)
    try:
        for file_id in ids:
            retrieve_neighbors(conn, seed=_seed(conn, file_id), limits=limits,
                               knowledge=knowledge, embeddings_enabled=False)
    finally:
        conn.set_trace_callback(None)
    return counted


def test_a_whole_pass_costs_statements_in_proportion_to_the_corpus(
        corpus, tmp_path):
    """The item, as a growth rate rather than a stopwatch.

    Two databases, because the two corpora have to be measured separately: sixty
    files in the database that already holds twenty would measure eighty against
    twenty and the ratio would mean nothing.
    """
    from database_agent.db import open_database

    small = _statements_for_a_whole_pass(corpus, tmp_path / "small", SMALL)
    other = open_database(tmp_path / "large.sqlite")
    try:
        create_schema(other)
        create_evidence_schema(other)
        create_fields(other)
        for key, value in CEILINGS.items():
            set_ceiling(other, key, value)
        large = _statements_for_a_whole_pass(other, tmp_path / "large", LARGE)
    finally:
        other.close()

    growth = large / small
    assert growth < LINEAR_ENOUGH, (
        f"{SMALL} files cost {small} statements and {LARGE} cost {large}: "
        f"{growth:.1f}x for 3x the corpus. Retrieval is reading the facts of one "
        "candidate at a time, so five times the files is twenty-five times the work "
        "and a 5,000-file plan does not finish")


def test_the_bulk_reads_answer_what_the_per_file_reads_answer(corpus, tmp_path):
    """The fork, pinned.

    The two helpers below are a second way of asking a question `facts.read_surface`
    already answers, and a second way of asking is how the two come to disagree --
    `read_surface.proposal_eligible`'s own docstring records what happened the last
    time two reads in one module disagreed about the same file. So this compares them
    over every file in a corpus, per channel, rather than trusting that the WHERE
    clause was transcribed correctly.
    """
    from facts.read_surface import versions_in_fields, versions_proposing

    ids = _build(corpus, tmp_path, 12)

    stating = versions_proposing(corpus, field_key="subject", value="PHYS1401")
    for file_id in ids:
        version = (file_id, _hash(corpus, file_id))
        expected = _values(proposal_eligible(
            corpus, file_id=file_id, content_hash=version[1])
        ).get(("subject", "PHYS1401"))
        found = stating.get(version)
        assert (found is None) == (expected is None), version
        if expected is not None:
            assert found["fact_id"] == expected["fact_id"]
            assert found["reliability_state"] == expected["reliability_state"]
            assert found["evidence_refs"] == expected["evidence_refs"]

    for read, field in ((family_facts, VERSION_FAMILY_FIELD),
                        (session_facts, DOWNLOAD_SESSION_FIELD)):
        bulk = versions_in_fields(corpus, field_keys=(field,))
        for file_id in ids:
            version = (file_id, _hash(corpus, file_id))
            expected = _values(read(corpus, file_id=file_id,
                                    content_hash=version[1]))
            found = _values(bulk.get(version, ()))
            assert set(found) == set(expected), (field, version)
            for key, row in expected.items():
                assert found[key]["fact_id"] == row["fact_id"]
                assert found[key]["evidence_refs"] == row["evidence_refs"]


def test_a_value_no_file_states_retrieves_nobody(corpus, tmp_path):
    """The empty answer stays empty, which a bulk read can get wrong by returning
    every row it fetched when its filter matched nothing."""
    from facts.read_surface import versions_in_fields, versions_proposing

    _build(corpus, tmp_path, 4)
    assert versions_proposing(corpus, field_key="subject", value="NOBODY") == {}
    assert versions_in_fields(corpus, field_keys=()) == {}
