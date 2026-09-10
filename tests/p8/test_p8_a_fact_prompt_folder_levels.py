# tests/p8/test_p8_a_fact_prompt_folder_levels.py
"""The A_fact revision that describes `folder_levels`. NOT RATIFIED, and pinned so.

`test_p8_a_fact_prompt.py` re-derives the ratified bytes from the ratification
documents, on the ground that "pinning the digest alone would say only that the file
has not changed since somebody typed a digest for it". The same argument applies
here and there is no document to derive from, so this derives the revision from the
RATIFIED FILE instead: the delta is four substitutions, each applied exactly once,
and the result must equal the shipped bytes. What is pinned is not a number but the
whole of what an agent added to the owner's text.

**Why a revision exists at all.** The dossier now carries a `folder_levels` key --
the folder levels the person's chosen situation would build, read off the shipped
template library. The ratified text tells the model the dossier "has these keys and
no others" and lists fourteen. Sending a fifteenth under that text makes the model's
own instructions false about the bytes beside them.

**What the delta may not do.** It may not describe a FIELD: meanings live in
`library/field_glossary.json`, which records that every one of them is transcribed
from something already ratified and names the source. And it may not turn the
library's word `required` -- which is about the TREE -- into an instruction to fill a
field the evidence does not carry. The sentences that hold that line are quoted from
the ratified text rather than written here, and this file asserts they are quotes.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from llm_harness.prompt_library import (
    A_FACT_TEMPLATE_FOLDER_LEVELS_FILE,
    A_FACT_TEMPLATE_FOLDER_LEVELS_SHA256,
    RatifiedTextChanged,
    a_fact_template_bytes,
    a_fact_template_folder_levels_bytes,
)


#: The four substitutions, in the order they are applied. Each must match exactly
#: once in the ratified text: a delta that matched twice or not at all would mean
#: the shipped revision is bytes this test did not derive.
KEY_LIST_OLD = (
    "The dossier has these keys and no others: allowed_vocabulary, call_site, "
    "conflicts, eligibility_reason, evidence_items, field_glossary, "
    "max_dossier_tokens, plan_version, policy_version, reduction_rung, "
    "released_evidence, response_schema, shaping_policy, subject_ref."
)
KEY_LIST_NEW = (
    "The dossier has these keys and no others: allowed_vocabulary, call_site, "
    "conflicts, eligibility_reason, evidence_items, field_glossary, "
    "folder_levels, max_dossier_tokens, plan_version, policy_version, "
    "reduction_rung, released_evidence, response_schema, shaping_policy, "
    "subject_ref."
)
COUNT_OLD = "Five of them are yours."
COUNT_NEW = "Six of them are yours."

WHAT_IT_IS = (
    '"folder_levels" is the list of folder levels this file\'s filing plan is built '
    'from, in the order they nest. Each entry has "field", which is a key that also '
    'appears in "allowed_vocabulary"; "label", the name that folder level is given; '
    'and "requirement", which is "required" when the plan cannot be built without '
    'that field and "optional" when it can. It is the same list on every file and '
    'it says nothing about this one.'
)
WHAT_TO_DO = (
    "Consider every field it names before you consider the rest of the vocabulary. "
    "You are still not choosing a folder: the plan is already decided, and this "
    "only tells you which fields it rests on. Considering a field is not filling it."
)
ANCHOR = ('"released_evidence" is a list of objects, each with "observation_key", '
          '"address", "value" and "zone".')

#: The two sentences that keep `required` from becoming "fill this". They are the
#: owner's, not this delta's, and the assertion below is what makes that checkable.
QUOTED_FROM_THE_RATIFIED_TEXT = (
    "Declining is a correct answer and it is recorded as one.",
    "A field you get wrong becomes a permanent property of someone's file.",
)


def _ratified() -> str:
    return a_fact_template_bytes().decode("utf-8")


def test_the_revision_is_the_ratified_text_plus_exactly_this_delta():
    text = _ratified()
    for fragment in (KEY_LIST_OLD, COUNT_OLD, ANCHOR):
        assert text.count(fragment) == 1, fragment[:60]

    revised = text.replace(KEY_LIST_OLD, KEY_LIST_NEW, 1)
    revised = revised.replace(COUNT_OLD, COUNT_NEW, 1)
    revised = revised.replace(
        ANCHOR, f"{WHAT_IT_IS}\n\n{WHAT_TO_DO}\n\n{ANCHOR}", 1)

    assert revised.encode("utf-8") == a_fact_template_folder_levels_bytes()


def test_the_shipped_digest_is_the_digest_of_that_derivation():
    raw = a_fact_template_folder_levels_bytes()
    assert hashlib.sha256(raw).hexdigest() == A_FACT_TEMPLATE_FOLDER_LEVELS_SHA256
    assert len(raw) == 8020
    assert len(raw.decode("utf-8").split()) == 1359


def test_the_ratified_file_is_untouched_beside_it():
    """A revision is a new file, never an edit to the old one. Both are loadable,
    and every record already written under the ratified digest still points at text
    that exists."""
    assert a_fact_template_bytes() != a_fact_template_folder_levels_bytes()
    assert A_FACT_TEMPLATE_FOLDER_LEVELS_FILE.name != "a_fact_template.txt"


def test_what_disarms_required_is_the_ratified_text_and_not_this_delta():
    """`required` is the template library's word about the TREE. Shown to a model it
    reads as "you must fill this", and a required level filled with a guess is worse
    than an empty one: a wrong value suppresses candidate folders for OTHER files.
    What holds that line is the ratified text's own position on declining, so the
    delta quotes it rather than restating it."""
    ratified = _ratified()
    # Still said, and said where the shape for saying it is defined. The delta
    # repeated them two sections earlier and 7 declines came back with `unknown`
    # nested inside `payload`; the repetition is gone and the ratified text is not.
    for sentence in QUOTED_FROM_THE_RATIFIED_TEXT:
        assert sentence in ratified, sentence
        assert sentence not in WHAT_TO_DO, sentence
    # What holds `required` down in the delta itself: it defines the word as a
    # property of the PLAN, never as an obligation on the answer.
    assert "the plan cannot be built without that field" in WHAT_IT_IS
    assert "Considering a field is not filling it." in WHAT_TO_DO


def test_the_delta_describes_the_key_and_never_a_field():
    """Field meanings are `library/field_glossary.json`'s, transcribed and never
    authored. A revision that explained what `work_type` means would author one in
    the one place no test re-reads a source for it.

    Two checks, because the rule is about MEANINGS and a key check alone would pass
    over "the course code printed on the syllabus" -- prose that names no key and
    still tells the model what to look for. So the delta must also carry none of the
    glossary's own sentences: a meaning belongs in the file whose test re-reads the
    document it was transcribed from, never in prose beside it.
    """
    added = f"{WHAT_IT_IS} {WHAT_TO_DO}"
    for field_key in ("work_type", "subject", "school", "term", "instructor",
                      "authored_by", "file_type", "creation_date"):
        assert field_key not in added, field_key

    meanings = json.loads(
        (Path(__file__).resolve().parents[2]
         / "src/llm_harness/library/field_glossary.json").read_text(encoding="utf-8")
    )["fields"]
    for key, entry in meanings.items():
        assert entry["meaning"] not in added, key

    # And the delta says nothing about what any field CONTAINS. These are the words
    # a description of a field would need and a description of a key does not.
    for smell in ("course", "institution", "semester", "author", "format",
                  "timestamp", "look for", "printed on", "found in the"):
        assert smell not in added.lower(), smell


def test_a_changed_byte_in_the_revision_is_refused_rather_than_loaded(tmp_path,
                                                                     monkeypatch):
    from llm_harness import prompt_library

    edited = tmp_path / "a_fact_template_folder_levels.txt"
    edited.write_bytes(a_fact_template_folder_levels_bytes() + b" ")
    monkeypatch.setattr(
        prompt_library, "A_FACT_TEMPLATE_FOLDER_LEVELS_FILE", edited)
    prompt_library.a_fact_template_folder_levels_bytes.cache_clear()
    with pytest.raises(RatifiedTextChanged):
        prompt_library.a_fact_template_folder_levels_bytes()
    prompt_library.a_fact_template_folder_levels_bytes.cache_clear()


def test_the_prompt_in_force_says_unratified_in_its_own_id():
    """The id is on every audit row, fact row and cache key -- and the STATUS, not the
    id, is the word that says the owner has read the text.

    **This pin used to name the 2026-09-04 row and it is re-argued to the row in force
    (`104` §18.14).** The owner ratified §18.13's two sentences on 9 Sep 2026 -- gap
    1's conflicts flag explained and gap 3's "an unseen value may be proposed" -- and
    the lead applied them as a NEW row, `v3-conflicts-open-values`, with A's policy v2;
    `cli.A_FACT_ROW` points at it, which is how the product runs a ratified text
    without a worktree patch (`local-w3-r18.sh`'s A_FACT_ROW patch is superseded by
    exactly this). The old pin asserted the v1 revision's id and the v1 revision's
    bytes, so it now says the deployment is running a text it stopped running.

    **The word `unratified` STAYS IN THE ID, and that is not a lie: it is
    `prompt_library`'s own rule that a row's status word is not its id.**
    `prompt_fingerprint` hashes the template id with the bytes, so renaming an id to
    match a status would move the fingerprint of every A_fact record written under it
    and orphan the audit trail -- `cli.A_FACT_ROW`'s comment records that reasoning in
    the product itself. What says the owner read this text is `draft_status`, and
    `a_fact_row` refuses an `unratified` row before a byte is loaded. So the two are
    asserted TOGETHER here: the id carries the word, the status carries the
    ratification, and `PromptDefinition.ratified` is what the composition root reads.

    SABOTAGE: this file derives the folder-levels delta from the ratified text and
    would be satisfied by a v3 that quietly dropped it, since the delta lives in a v1
    file that is still shipped and still verified. So the last two assertions say the
    delta SURVIVED into the text in force -- the fifteen-key list and its count -- and
    that the bytes in force are no longer the v1 file's.
    """
    from cli import A_FACT_ROW, a_fact_prompt
    from llm_harness.prompt_library import draft_bytes, draft_status

    prompt = a_fact_prompt()
    assert prompt.template_id == "a_fact.unratified.folder-levels-v3.2026-09-09"
    assert prompt.template_id == A_FACT_ROW[0]
    assert "unratified" in prompt.template_id
    assert draft_status(prompt.template_id) == "ratified"
    assert prompt.ratified is True

    template, _schema, _policy = draft_bytes(A_FACT_ROW[0])
    assert prompt.template_bytes == template
    assert prompt.template_bytes != a_fact_template_folder_levels_bytes()
    in_force = prompt.template_bytes.decode("utf-8")
    assert in_force.count(KEY_LIST_NEW) == 1
    assert in_force.count(COUNT_NEW) == 1
