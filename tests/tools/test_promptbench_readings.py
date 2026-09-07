"""The proposed `readings` key, as the bench emulates it for the R-08 packet section.

Nothing here reaches a model. The tests pin what the key is (the situation's
`needs_llm` readings, verbatim), where the product's serialiser would put it
(after the file's keys), and what the frame-first layout puts first.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.promptbench.candidates import candidate, candidates_for  # noqa: E402
from tools.promptbench.dossiers import (  # noqa: E402
    FILE_KEYS, FRAME_KEYS, RECOGNITION_FILE, readings_for, serialise_dossier,
)
from tools.promptbench.suites import all_cases_for, cases_for  # noqa: E402

ROWS = ("academic", "academic.coursework")


def test_every_reading_is_byte_equal_to_a_string_in_the_recognition_library():
    library = json.loads(RECOGNITION_FILE.read_text(encoding="utf-8"))["schemas"]
    authored = {t for schema in library.values() for e in schema["needs_llm"] for t in e["readings"]}
    readings = readings_for(ROWS)
    assert readings, "the situation has readings"
    for item in readings:
        assert item["text"] in authored, item["text"][:60]
        assert item["row"] in ROWS
    assert len(readings) == 11  # academic 5, academic.coursework 6, on 2026-09-06


def test_a_row_with_no_readings_is_refused_rather_than_sent_empty():
    with pytest.raises(KeyError):
        readings_for(("academic.no-such-row",))


def _body():
    return {"allowed_vocabulary": ["subject"], "call_site": "A_fact", "conflicts": [],
            "eligibility_reason": "e", "evidence_items": [], "field_glossary": {"subject": "m"},
            "folder_levels": [], "max_dossier_tokens": 1, "plan_version": None,
            "policy_version": "p", "readings": [{"row": "academic", "text": "t"}],
            "reduction_rung": "r", "released_evidence": [], "response_schema": "{}",
            "shaping_policy": "{}", "subject_ref": "s"}


def test_the_canonical_layout_puts_readings_after_the_files_own_keys():
    text = serialise_dossier(_body(), "canonical")
    order = [k for k in _body() if f'"{k}":' in text]
    positions = {k: text.index(f'"{k}":') for k in order}
    assert positions["policy_version"] < positions["readings"] < positions["reduction_rung"]
    for file_key in ("conflicts", "eligibility_reason", "evidence_items"):
        assert positions[file_key] < positions["readings"], file_key


def test_the_frame_first_layout_puts_every_frame_key_before_every_file_key():
    text = serialise_dossier(_body(), "frame-first")
    positions = {k: text.index(f'"{k}":') for k in _body()}
    assert max(positions[k] for k in FRAME_KEYS) < min(positions[k] for k in FILE_KEYS)
    assert json.loads(text) == _body()   # same content, different order


def test_the_frame_first_layout_refuses_a_key_it_has_no_place_for():
    with pytest.raises(ValueError):
        serialise_dossier(dict(_body(), extra=1), "frame-first")


def test_the_readings_candidates_are_scoped_to_their_own_suite():
    names = {c.name: c for c in candidates_for("A_fact")}
    for name in ("readings-control", "readings-canonical", "readings-frame-first"):
        assert names[name].suite == "a_readings"
    assert names["readings-control"].readings_rows == ()
    assert names["readings-canonical"].readings_rows == ROWS
    assert names["readings-frame-first"].layout == "frame-first"
    assert names["ratified-glossary"].suite is None
    own = {c.case_id for c in cases_for("A_fact")}
    readings = {c.case_id for c in cases_for("A_fact", "a_readings")}
    assert not own & readings and len(readings) >= 6
    assert readings <= {c.case_id for c in all_cases_for("A_fact")}


def test_the_readings_template_names_the_key_and_says_it_is_not_evidence():
    text = candidate("A_fact", "readings-canonical").prompt().template_bytes.decode("utf-8")
    line = next(l for l in text.splitlines() if l.startswith("The dossier has these keys and no others:"))
    assert "readings" in line
    assert "It is guidance and it is not evidence" in text
    assert "not a question you answer here" in text
