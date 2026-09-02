# tests/p8/test_p8_field_glossary.py
"""The field glossary: what a field key MEANS, carried in the dossier.

`planning/76-PROMPT-RESEARCH.md` §10.1 records the glossary decision as owed and names
three options -- the template carries meanings, the dossier carries them per file, or
the prompt tells the model to decline any field whose meaning is not plain from its
key. `planning/82-FACT-PROMPT-DRAFT.md` §7.1 put the last of those to the owner as
rule 2 and named its cost: *"a small model asked what `subject` means may answer 'the
topic of the document' rather than 'the course code', and rule 2 tells it to stop
rather than to guess. That is deliberately fail-closed and it will cost real coverage
on exactly the fields that matter most."* **The owner chose the second option.** The
model does not have to guess OR decline, because it has been told.

Three things bound what a glossary may be, and each has a test here.

* **A definition of a FIELD, never a hint about the FILE.** The same key means the same
  thing on every file in every corpus, so the glossary is a pure function of
  `allowed_vocabulary` and of nothing else. `test_the_glossary_cannot_vary_between_two_files`
  and `test_no_always_local_content_reaches_the_glossary` are the same claim from two
  sides.
* **Only the fields of this call.** Meanings for fields the model may not propose are
  wasted tokens and an invitation to propose them (`76` R7).
* **Transcribed, never authored.** Every meaning is quoted from something the owner
  ratified, and `test_every_meaning_is_verbatim_from_its_cited_source` re-reads the
  source. A field whose meaning is recorded nowhere is `owed`, not invented: it gets no
  entry and the model is told nothing about it, which is exactly `82` rule 2's position
  for that one field and no others.
"""
from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from evidence_shape.location import TextSpan
from llm_harness.dossier import canonical_dossier_bytes, field_glossary
from llm_harness.records import (
    DossierRequest,
    EvidenceItem,
    PromptDefinition,
    ReleasedEvidence,
)
from llm_harness.vocabulary import (
    A_FACT,
    DIRECT_ANCHOR,
    REDUCTION_NONE,
    REMAINS_AMBIGUOUS,
)
from privacy.items import Excerpt
from privacy.redaction import RedactionManifest
from privacy.release import (
    ModelCallRequest, ModelTarget, Released, ReleasedItem, Target,
)
from privacy.vocabulary import ALWAYS_LOCAL

from llm_harness.dossier import build_dossier
from llm_harness.fixtures import FIXTURE_HANDLE_KEY

REPO = Path(__file__).resolve().parents[2]
CLOUD = ModelTarget(locality="cloud", model_id="acme-large", provider="Acme")
KEY = "obs-key-1"
VOCABULARY = ("school", "subject")


def _prompt() -> PromptDefinition:
    return PromptDefinition(
        template_id="template.fact",
        template_bytes=b"TEMPLATE",
        response_schema_bytes=b'{"type":"object"}',
        call_site=A_FACT,
        call_site_version="1",
        shaping_policy_bytes=b'{"policy":"authored"}',
    )


def _build(*, subject_ref: str = "file-1", value: str = "Columbia University",
           address: str = "0:19", allowed_vocabulary=VOCABULARY):
    request = DossierRequest(
        call_site=A_FACT,
        subject_ref=subject_ref,
        eligibility_reason=REMAINS_AMBIGUOUS,
        evidence_items=(EvidenceItem(
            evidence_ref=KEY, kind="excerpt", location="body", excerpt_span=None,
            reliability_state="direct", basis=DIRECT_ANCHOR),),
        conflicts=(),
        model_call_request=ModelCallRequest(
            stage="fact_extraction",
            target=Target(file_ids=(subject_ref,)),
            model_target=CLOUD,
            requested_items=(Excerpt(observation_key=KEY, span=TextSpan(0, 18),
                                     reason="names the school"),),
            prompt_template_id="template.fact",
            prompt_fingerprint="fingerprint.fact",
            max_dossier_tokens=4000),
        plan_version=None,
        evidence_snapshot_id=None,
    )
    released = Released(
        release_id="rel-1", audit_id=17, policy_version="policy-1",
        materialised_items=(ReleasedItem(
            observation_key=KEY, span=address, value=value, zone="body",
            unit_length=64),),
        redaction_manifest=RedactionManifest(entries=()),
        model_target=CLOUD,
    )
    return build_dossier(request, released, reduction_rung=REDUCTION_NONE,
                         allowed_vocabulary=allowed_vocabulary, prompt=_prompt(), handle_key=FIXTURE_HANDLE_KEY)


def _body(**overrides) -> dict:
    dossier = _build(**overrides)
    return json.loads(canonical_dossier_bytes(dossier, _prompt(), handle_key=FIXTURE_HANDLE_KEY).decode("utf-8"))


def _library() -> dict:
    path = REPO / "src" / "llm_harness" / "library" / "field_glossary.json"
    return json.loads(path.read_text(encoding="utf-8"))


# --- the route into the dossier -------------------------------------------------


def test_the_glossary_reaches_the_model_keyed_by_field():
    """`76` §4: the model reads `allowed_vocabulary` as bare strings and nothing
    tells it what one means. This is the key that does."""
    glossary = _body()["field_glossary"]
    assert set(glossary) == {"school", "subject"}
    assert all(isinstance(meaning, str) and meaning for meaning in glossary.values())


def test_only_allowed_vocabulary_gets_an_entry():
    """`76` R7 bounds the model to `allowed_vocabulary`. A meaning for a field it may
    not propose is wasted tokens and an invitation to propose it."""
    glossary = _body(allowed_vocabulary=("school",))["field_glossary"]
    assert set(glossary) == {"school"}
    assert "subject" not in glossary
    assert "term" not in glossary


def test_a_field_with_no_entry_is_simply_absent():
    """An allowed field whose meaning is recorded nowhere is `owed`, never invented.
    The dossier says nothing about it rather than saying something authored here."""
    owed = sorted(_library()["owed"])
    assert owed, "the owed list is the honest half of the split; do not empty it"
    glossary = _body(allowed_vocabulary=tuple(owed))["field_glossary"]
    assert glossary == {}


# --- the bound: a definition of a FIELD, never a hint about the FILE -------------


def test_the_glossary_cannot_vary_between_two_files():
    """Two dossiers sharing only their vocabulary carry byte-identical glossaries.

    A glossary that could differ per file is a channel for the file's content, and
    §3.5's *"must cite exact supporting evidence already extracted"* would then be
    citing text the dossier put in front of the model as a definition.
    """
    one = _body(subject_ref="file-1", value="Columbia University", address="0:19")
    two = _body(subject_ref="file-2", value="BUSIB 4300 Syllabus", address="7:26")
    assert one["subject_ref"] != two["subject_ref"]
    assert one["released_evidence"] != two["released_evidence"]
    assert one["field_glossary"] == two["field_glossary"]


def test_no_always_local_content_reaches_the_glossary():
    """§8.4's always-local set, planted in every per-file input the builder has.

    `ALWAYS_LOCAL` names paths, complete extracted text, OCR output, file hashes,
    EXIF, GPS and user edits. None of them is an input to the glossary, and the way
    that is guaranteed is that the glossary is built from the vocabulary alone.
    """
    assert "paths" in ALWAYS_LOCAL and "complete_extracted_text" in ALWAYS_LOCAL
    planted = "/Users/someone/Desktop/tax/ALWAYSLOCALMARKER 51.4769,-0.0005"
    body = _body(subject_ref=planted, value=planted, address=planted)
    serialised = json.dumps(body["field_glossary"], ensure_ascii=False)
    assert "ALWAYSLOCALMARKER" not in serialised
    assert planted not in serialised


def test_the_glossary_builder_is_given_the_vocabulary_and_nothing_else():
    """Structural, not behavioural: there is no parameter through which a file, a
    person or a corpus could reach it."""
    assert list(inspect.signature(field_glossary).parameters) == ["allowed_vocabulary"]


# --- transcribed, never authored ------------------------------------------------


def test_the_library_covers_the_catalogue_exactly():
    """Defined and owed partition the closed catalogue: nothing invented, nothing
    silently dropped."""
    from facts.fields import FIELD_ROWS

    catalogue = {row.field_key for row in FIELD_ROWS}
    defined = set(_library()["fields"])
    owed = set(_library()["owed"])
    assert defined & owed == set()
    assert defined | owed == catalogue


def test_every_entry_names_a_source():
    for key, entry in _library()["fields"].items():
        assert entry["source"], f"{key} carries a meaning with no source"
        assert entry["meaning"].strip() == entry["meaning"]


def _source_text(source: str, key: str) -> tuple[str, str]:
    """The cited text, re-read from the citation. Returns (haystack, how)."""
    if source.startswith("facts.fields:"):
        from facts.fields import FIELD_ROWS

        # `facts.fields:<key>` — the note is not always the entry's own: `60` H6
        # states the discriminators for all three type keys on `record_type`.
        owner = source.split(":", 1)[1].split(" ", 1)[0]
        notes = {row.field_key: row.notes for row in FIELD_ROWS}
        return notes[owner] or "", "substring"
    path, _, _rest = source.partition(" ")
    if path.endswith("canonical_fields.json"):
        loaded = json.loads((REPO / path).read_text(encoding="utf-8"))
        roles = {row["key"]: row["role"] for row in loaded["fields"]}
        return roles[key], "equal"
    return (REPO / path).read_text(encoding="utf-8"), "substring"


@pytest.mark.parametrize("key", sorted(_library()["fields"]))
def test_every_meaning_is_verbatim_from_its_cited_source(key):
    """The citation is checked, not trusted.

    A field's meaning is text that goes to a model, so it is close to prompt text, and
    prompt text is the owner's to author. Where a meaning is already recorded in
    something the owner ratified, transcribing it is not authoring it -- and this test
    is what makes that claim checkable rather than asserted.
    """
    entry = _library()["fields"][key]
    haystack, how = _source_text(entry["source"], key)
    if how == "equal":
        assert entry["meaning"] == haystack
    else:
        assert entry["meaning"] in haystack
