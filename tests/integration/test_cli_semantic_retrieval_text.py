"""P9's semantic channel had never computed a vector, for any file, at any length.

`104` R-59, which corrects R-12. R-12 read the defect as "the recogniser is silent
under 100 characters, which is the sparse file `00`:56 names". It is not a length
rule. `cli._embedding_runtime.text_for` did:

    text = evidence_text(conn, file_id, content_hash, zones=..., char_budget=...)
    return text if text and len(text) >= SEMANTIC_MIN_CHARS else None

and `recognition.semantic.evidence_text` returns a two-TUPLE, `(text, keys)`. So
`len(text)` was 2 for every file that has ever been scanned, the guard returned
`None` unconditionally, no vector was stored, and `grouping.graph._mutual_semantic_
neighbours` returned `[]` at its `seed_vector is None` line. Measured on the owner's
199 files before the fix: `evidence_text` returned a tuple 199 times out of 199.

`d75dcb5`, the recognition commit that gave `evidence_text` its second return
value, is an ANCESTOR of `3ac0c0b`, which built this channel -- so the channel was
written against the tuple signature and was dead on arrival rather than severed
later. `tests/integration/test_p9_embedding_pipeline.py` is green throughout,
because it injects its own `embedding_text_for`: the P9 half was tested and the
composition root's half was not.

`semantic_retrieval_text` is module-level rather than a closure inside
`_embedding_runtime` for exactly that reason: the closure cannot be reached without
loading MiniLM weights, which are machine state and not repository state, so the
one line that decides whether the channel runs at all had no test that could see it.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402
from evidence_shape.location import Location, Segment, TextSpan  # noqa: E402
from evidence_shape.observation import Observation  # noqa: E402
from evidence_shape.runs import ExtractionRun  # noqa: E402
from evidence_shape.schema import create_evidence_schema  # noqa: E402
from evidence_shape.store import record_observation, record_run  # noqa: E402

CONTENT_HASH = "d" * 64
AT = "2026-09-06T00:00:00+00:00"
PAGE = (Segment(kind="page", index=1),)

#: Comfortably over any floor this deployment might choose.
A_PARAGRAPH = (
    "PHYS 1401 Introduction to Mechanics, Fall 2024. Kinematics, Newton's laws, "
    "work and energy, momentum and rotational motion. Problem sets are due at the "
    "start of lecture each Thursday and are graded coursework for the course."
)


@pytest.fixture()
def evidence(conn):
    create_evidence_schema(conn)
    record_run(conn, ExtractionRun(
        run_id="run-1", file_id="file-1", content_hash=CONTENT_HASH,
        extractor_name="fixture.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=AT, observation_count=1))
    return conn


def _body(conn, text: str, *, file_id: str = "file-1") -> None:
    record_observation(conn, Observation(
        file_id=file_id, content_hash=CONTENT_HASH,
        extractor_name="fixture.text", extractor_version="1.0.0",
        source_type="text_document", raw_value=text,
        location=Location(zone="body", container_path=PAGE,
                          text_span=TextSpan(0, len(text))),
        occurrence_count=1, observed_at=AT, reliability="direct", run_id="run-1",
        context_before=None, context_after=None, context_truncated=False))


def test_a_file_with_plenty_of_text_gets_text_to_encode(evidence):
    """The whole of R-59. Before the fix this returned `None` -- and returned it
    for a file with a thousand characters exactly as readily as for an empty one,
    because the value being measured was a tuple of length two."""
    _body(evidence, A_PARAGRAPH)

    text = cli.semantic_retrieval_text(evidence, "file-1", CONTENT_HASH)

    assert isinstance(text, str), (
        "the channel is handed something other than a string to encode; this is "
        "R-59, and `evidence_text` returns `(text, observation_keys)`")
    assert "PHYS 1401" in text


def test_the_floor_is_applied_to_the_text_and_not_to_a_tuple(evidence):
    """A floor is only a floor if it is measured against the thing it is about."""
    _body(evidence, "short")

    assert cli.semantic_retrieval_text(evidence, "file-1", CONTENT_HASH) is None


def test_a_file_with_no_readable_evidence_has_nothing_to_encode(evidence):
    """Absent means refuse: a file P4 recovered nothing from is not encoded as an
    empty string, which would put every such file at one point in the space."""
    assert cli.semantic_retrieval_text(evidence, "file-2", CONTENT_HASH) is None


def test_the_retrieval_floor_is_its_own_number(evidence):
    """`104` §13's ruling: P9's retrieval channel gets a floor of its own and
    recognition keeps `SEMANTIC_MIN_CHARS`. Two consumers of one constant is how a
    number measured for one question ends up deciding another."""
    assert cli.SEMANTIC_RETRIEVAL_MIN_CHARS >= 1
    assert cli.SEMANTIC_MIN_CHARS == 100, (
        "recognition's floor is not this agent's to move")


def test_the_filename_is_already_in_the_retrieval_text(evidence):
    """`00`:56 names the filename among what a sparse file has, and
    `SEMANTIC_ZONES` already leads with it -- so a filename observation reaches the
    vector without anything being added here."""
    assert cli.SEMANTIC_ZONES[0] == "filename"
