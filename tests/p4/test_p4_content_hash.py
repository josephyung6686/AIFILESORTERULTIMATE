# tests/p4/test_p4_content_hash.py
"""One content hash, one spelling -- P1's.

The stress test of 2026-08-21 found P4 and P5 fixtures carrying
`content_hash="sha256:abc"` while live P1 returns 64 bare hex characters, and both
passing every test. Two spellings in one database split one file into two evidence
sets: `observation_key` hashes `content_hash` as its first part, so one value read
from one file under two spellings is two citation handles, and §3.4's cache would
miss on a file it had already extracted.

P1 owns the format (R1: "the content hash is the stable identity of a file
version"), so P1 publishes the predicate and P4 enforces it. P4 restating "64
lowercase hex characters" would be a second definition of one rule -- the defect
class that produced the fingerprint break.
"""
import pytest

from database_agent.identity import hash_file, is_content_hash

from evidence_shape.location import Location, Segment
from evidence_shape.observation import MalformedObservation, Observation
from evidence_shape.runs import ExtractionRun, MalformedRun

GOOD = "f16d05ec6b29248d2c61adb1e9263f78e4f7bace1b955014a2d17872cfe4064d"


def an_observation(**over) -> Observation:
    return Observation(**{
        "file_id": "f1", "content_hash": GOOD, "extractor_name": "pdf.text",
        "extractor_version": "3.1.0", "source_type": "text_document",
        "raw_value": "BUSIB 4300",
        "location": Location("heading", (Segment("page", 1),)),
        "occurrence_count": 1, "observed_at": "2026-08-19T14:03:22+00:00",
        "reliability": "possible", "run_id": "r1", **over})


def a_run(**over) -> ExtractionRun:
    return ExtractionRun(**{
        "run_id": "r1", "file_id": "f1", "content_hash": GOOD,
        "extractor_name": "pdf.text", "extractor_version": "3.1.0",
        "source_type": "text_document", "analysis_tier": "native", "config": {},
        "completeness": "complete", "started_at": "2026-08-19T14:00:00+00:00",
        **over})


def test_p1s_live_digest_is_a_content_hash(sample_file):
    assert is_content_hash(hash_file(sample_file, materialized=True))


@pytest.mark.parametrize("bad", [
    "sha256:abc",                 # the fixture spelling: algorithm-prefixed
    "sha256:" + "a" * 64,         # prefixed, and 64 hex after the prefix
    "A" * 64,                     # uppercase; `hexdigest()` is lowercase
    "a" * 63, "a" * 65,           # wrong length
    "g" * 64,                     # not hex
    "", None, 64,
])
def test_a_value_p1_never_produces_is_not_a_content_hash(bad):
    assert not is_content_hash(bad)


def test_p4s_own_digest_is_not_a_content_hash():
    """`sha256_of` is algorithm-prefixed and P1's is not, deliberately.

    P4's keys are P4's; P1's hash is P1's. The two shapes must stay
    distinguishable, or a key could be stored in a `content_hash` column and
    nothing would notice.
    """
    from evidence_shape.canonical import sha256_of
    assert not is_content_hash(sha256_of("anything"))


def test_an_observation_refuses_a_hash_p1_never_produced():
    with pytest.raises(MalformedObservation):
        an_observation(content_hash="sha256:abc")


def test_a_run_refuses_a_hash_p1_never_produced():
    with pytest.raises(MalformedRun):
        a_run(content_hash="sha256:abc")


def test_the_citation_handle_is_built_from_the_hash_p1_stored(sample_file):
    """The walking skeleton copies `get_file()["content_hash"]` unchanged."""
    digest = hash_file(sample_file, materialized=True)
    assert an_observation(content_hash=digest).observation_key.startswith("sha256:")
