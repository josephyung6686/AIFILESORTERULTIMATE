"""`00` amendment 7(c): a situation record cites the model's own citations beside
the recogniser's, and is `None` when there is nothing to cite.

Every file is asked from the whole library now, a file no recogniser raised
anything for included. Its question carries no observation keys, and the record
built on the recogniser's keys alone raised `UnbackedClassification` eight
situation calls into the first gate run over the owner's corpus -- the run died
on a correct answer. What the classification rests on for such a file is what the
verdict cited, which P8 checked against the released dossier.
"""
from __future__ import annotations

from types import SimpleNamespace

import cli
from evidence_shape.observation import is_observation_key
from llm_harness.records import CheckedCitation
from model_situation import NONE_OF_THESE, SituationQuestion

RAISED = "sha256:" + "ab" * 32
CITED = "sha256:" + "cd" * 32
ALSO_CITED = "sha256:" + "ef" * 32
ORDINARY = next(schema for schema, handling in cli.HANDLING_POLICY.items()
                if not handling.protected)


def _question(*evidence_refs: str) -> SituationQuestion:
    return SituationQuestion(
        file_id="file-1", content_hash="hash-1", reason="no_evidence",
        allowed_situations=(*cli.HANDLING_POLICY, NONE_OF_THESE),
        matched_terms=(), evidence_refs=evidence_refs)


def _verdict(*checked: CheckedCitation):
    return SimpleNamespace(citations_checked=checked)


def test_the_keys_this_pin_mints_are_observation_keys():
    assert all(is_observation_key(key) for key in (RAISED, CITED, ALSO_CITED))


def test_a_resolved_citation_is_an_observation_key_and_an_unresolved_one_is_not():
    cited = cli.cited_observations(_verdict(
        CheckedCitation(CITED, True, True),
        CheckedCitation("handle:" + "0" * 64, False, False),
        CheckedCitation("candidate:academic", True, False),
        CheckedCitation(CITED, True, True)))
    assert cited == (CITED,)


def test_a_file_no_recogniser_raised_rests_on_what_the_model_cited():
    record = cli.situation_classification(
        _question(), ORDINARY, observed_at="2026-09-12T00:00:00+00:00",
        cited=(CITED, ALSO_CITED))
    assert record is not None
    assert record.evidence_refs == (CITED, ALSO_CITED)
    assert record.basis == cli.LOCAL_MODEL_SITUATION


def test_the_recognisers_keys_come_first_and_a_shared_key_is_cited_once():
    record = cli.situation_classification(
        _question(RAISED, CITED), ORDINARY,
        observed_at="2026-09-12T00:00:00+00:00", cited=(CITED, ALSO_CITED))
    assert record.evidence_refs == (RAISED, CITED, ALSO_CITED)


def test_nothing_to_cite_is_no_record_rather_than_a_crash():
    assert cli.situation_classification(
        _question(), ORDINARY, observed_at="2026-09-12T00:00:00+00:00",
        cited=()) is None
