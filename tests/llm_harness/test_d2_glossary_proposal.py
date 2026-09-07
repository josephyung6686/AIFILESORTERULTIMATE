"""The A_fact glossary proposal: two entries changed, transcribed, and nothing else.

`tests/p8/test_p8_field_glossary.py` holds the ratified file to three rules: a
definition of a field and never a hint about a file, only the fields of this
call, transcribed and never authored. The proposal beside it is held to the same
three plus one more: every entry other than `school` and `subject` is
byte-identical to the ratified entry, so the owner reads a two-line diff and not
a 55-line file.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LIBRARY = REPO / "src" / "llm_harness" / "library"
RATIFIED = LIBRARY / "field_glossary.json"
PROPOSAL = LIBRARY / "field_glossary_proposal_2026-09-06.json"
SOURCE = REPO / "planning" / "104-DIAGNOSIS-FINAL.md"

CHANGED = ("school", "subject")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_every_other_entry_is_byte_identical_to_the_ratified_one():
    ratified, proposal = _load(RATIFIED)["fields"], _load(PROPOSAL)["fields"]
    assert set(ratified) == set(proposal)
    for key in ratified:
        if key in CHANGED:
            assert ratified[key] != proposal[key], key
        else:
            assert ratified[key] == proposal[key], key
    assert _load(PROPOSAL)["owed"] == _load(RATIFIED)["owed"]


def test_the_proposal_says_it_is_not_ratified_in_its_header_and_status():
    proposal = _load(PROPOSAL)
    assert proposal["_status"]["status"] == "unratified"
    assert proposal["_status"]["differing_keys"] == list(CHANGED)
    assert proposal["_"].startswith("PROPOSAL, NOT RATIFIED")
    # The ratified header's rules travel with it verbatim.
    assert _load(RATIFIED)["_"] in proposal["_"]


def test_the_two_meanings_are_transcribed_from_104_section_11_2_step_1():
    """The ratified glossary's convention: a meaning names a source that exists
    and the source carries the words. `104` §11.2 step 1 is the owner's text."""
    text = SOURCE.read_text(encoding="utf-8")
    step = text.split("### 11.2 The fix chain", 1)[1].split("2. **Make coursework", 1)[0]
    # The document is hard-wrapped; a phrase may cross a line break and its
    # indentation, so the comparison is over collapsed whitespace.
    step = re.sub(r"\s+", " ", step)
    proposal = _load(PROPOSAL)["fields"]
    for key in CHANGED:
        assert "104-DIAGNOSIS-FINAL.md §11.2 step 1" in proposal[key]["source"], key
    school = proposal["school"]["meaning"]
    subject = proposal["subject"]["meaning"]
    for phrase in ("the institution that offers this course and term",
                   "not any school the person attended",
                   "a school merely mentioned is", "never a level"):
        assert phrase in school and phrase in step, phrase
    for phrase in ("the course as the course names itself (code or title)",
                   "a study guide, textbook or publisher is not one"):
        assert phrase in subject and phrase in step, phrase


def test_a_meaning_is_a_definition_of_a_field_and_never_a_hint_about_a_file():
    """No corpus value, no persona, no folder label: the same words on every file."""
    proposal = _load(PROPOSAL)["fields"]
    forbidden = re.compile(r"Georgetown|Columbia|CliffsNotes|PHYS|Python 1006|Priya|Mara|Tom\b")
    for key in CHANGED:
        assert not forbidden.search(proposal[key]["meaning"]), key
        assert len(proposal[key]["meaning"].split()) <= 40, key


# --- the third `subject` wording: a second proposal differing from the first in one entry

THIRD = LIBRARY / "field_glossary_proposal_subject_2026-09-06.json"


def test_the_third_subject_wording_differs_from_the_proposal_in_subject_alone():
    proposal, third = _load(PROPOSAL), _load(THIRD)
    assert set(proposal["fields"]) == set(third["fields"])
    for key in proposal["fields"]:
        if key == "subject":
            assert proposal["fields"][key] != third["fields"][key]
        else:
            assert proposal["fields"][key] == third["fields"][key], key
    assert third["owed"] == proposal["owed"]
    assert third["_status"]["status"] == "unratified"
    assert third["_"].startswith("PROPOSAL, NOT RATIFIED")
    assert _load(RATIFIED)["_"] in third["_"]


def test_the_third_subject_wording_is_the_one_105_put_to_the_owner():
    packet = (REPO / "planning" / "105-D2-PROMPT-PACKET.md").read_text(encoding="utf-8")
    meaning = _load(THIRD)["fields"]["subject"]["meaning"]
    assert "105-D2-PROMPT-PACKET.md §1.6" in _load(THIRD)["fields"]["subject"]["source"]
    for phrase in ("a course code, or the name a syllabus would give the course",
                   "never the title of this document, its chapter, its book, its study guide or its publisher"):
        assert phrase in meaning and phrase in packet, phrase
    forbidden = re.compile(r"Georgetown|Columbia|CliffsNotes|PHYS|Python 1006|Priya|Mara|Tom\b")
    assert not forbidden.search(meaning)
    assert len(meaning.split()) <= 40
