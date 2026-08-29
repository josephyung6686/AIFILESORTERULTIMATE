# tests/p4/test_p4_emit_order.py
"""`observation_keys_for_run` promised emit order and delivered uuid4 order.

Its docstring says "Ordered by `observation_id`, which is insertion order, so position
N in the emitted batch is position N here", and it is published precisely so a caller
that emits a per-located-value record alongside a batch has a handle -- "P5's §2.9
sensitivity signal is the first such caller, and keyed on batch position until this
existed."

`record_observation` mints `uuid.uuid4()`, so `ORDER BY observation_id` is
lexicographic order over random ids. Executed 2026-08-21: a batch emitted
00,01,02,…,11 came back 07,10,02,04,09,05,06,01,03,08,11,00.

The consequence is not cosmetic. `long_tail.record_sensitivity_signals` does
`observation_keys[signal.observation_index]`, so §2.9's "treating addresses and
message content as potentially sensitive" attached the signal to the WRONG
observation -- and the row it writes is keyed on `observation_key`, which is what P7
later redacts against.

Rule 8 is unaffected and deliberately so: `determinism._lines` sorts, because "a set
has no order". This is about the ordered handle, not the set.
"""
import json

from evidence_shape.store import (
    RunWriter, observation_keys_for_run, observations_for_run,
)

from extractors.shape import location, observation, run
from extractors.sink import ExtractionResult

HASH = "5f7b1a1c9d4e6f2a3b8c0d1e2f3a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c"
#: Twelve, because a scrambled order can agree with emit order by luck on two or
#: three. 12! is 479,001,600.
WIDTH = 12


def a_batch(width: int = WIDTH) -> ExtractionResult:
    def one(index: int):
        return observation(
            file_id="f1", content_hash=HASH, extractor_name="pdf.text",
            extractor_version="0.1.0", source_type="text_document",
            raw_value=f"value-{index:02d}", location=location(zone="body"),
            observed_at="2026-08-21T12:00:00+00:00", reliability="direct")
    return ExtractionResult(
        run=run(file_id="f1", content_hash=HASH, extractor_name="pdf.text",
                extractor_version="0.1.0", source_type="text_document",
                analysis_tier="native", config={}, completeness="complete",
                coverage={"units": "pages", "processed": 1, "total": 1},
                observation_count=width,
                started_at="2026-08-21T12:00:00+00:00",
                finished_at="2026-08-21T12:00:00+00:00"),
        observations=tuple(one(i) for i in range(width)))


def test_position_n_in_the_batch_is_position_n_in_the_keys(p4_conn):
    batch = a_batch()
    run_id = RunWriter(p4_conn, author="P5").write(batch)

    keys = observation_keys_for_run(p4_conn, run_id)
    stored = observations_for_run(p4_conn, run_id)
    assert [o.raw_value for o in stored] == [
        o["raw_value"] for o in batch.observations]
    assert keys == [o.observation_key for o in stored]


def test_the_sensitivity_signal_lands_on_the_value_it_was_raised_for(p4_conn):
    """The live consumer: `long_tail.record_sensitivity_signals` indexes into these
    keys by the observation's position in the batch."""
    batch = a_batch()
    run_id = RunWriter(p4_conn, author="P5").write(batch)
    keys = observation_keys_for_run(p4_conn, run_id)

    for index, emitted in enumerate(batch.observations):
        addressed = [o for o in observations_for_run(p4_conn, run_id)
                     if o.observation_key == keys[index]]
        assert len(addressed) == 1
        assert addressed[0].raw_value == emitted["raw_value"], index


def test_the_events_key_list_is_in_batch_order_too(p4_conn):
    """Two identical batches must produce one event explanation, not two orderings.

    Nothing compares event explanations today, so this is a hazard rather than a live
    break -- but `record_run_event` reads the same query, and §8.5's whole business is
    diffing stored forms.
    """
    run_id = RunWriter(p4_conn, author="P5").write(a_batch())
    explanation = json.loads(p4_conn.execute(
        "SELECT explanation FROM events WHERE event_type = 'extraction'"
    ).fetchone()["explanation"])
    assert explanation["observation_keys"] == observation_keys_for_run(p4_conn, run_id)
    assert explanation["observation_keys"] == [
        o.observation_key for o in observations_for_run(p4_conn, run_id)]


def test_two_identical_batches_produce_one_event_explanation(p4_conn):
    first = RunWriter(p4_conn, author="P5").write(a_batch())
    second = RunWriter(p4_conn, author="P5").write(a_batch())
    explanations = [
        json.loads(row["explanation"])["observation_keys"] for row in p4_conn.execute(
            "SELECT explanation FROM events WHERE event_type = 'extraction' "
            "ORDER BY event_id")]
    assert len(explanations) == 2
    assert explanations[0] == explanations[1]
    assert first != second
