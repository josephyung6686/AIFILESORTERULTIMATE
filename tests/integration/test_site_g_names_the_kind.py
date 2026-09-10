"""`104` §18.7 S2 and §18.11 (9 Sep 2026): the local model is the kind recogniser.

`105` §13.3's ten restricted kinds were a closed vocabulary with no writer: no
detector named a kind, so `ClassificationRecord.privacy_class` read `ordinary` on
every row and the gate's two kind refusals never fired (S2). The owner ratified one
optional field on site G's answer -- `restricted_kind`, one of the ten -- and one
sentence in the local situation text asking for it. These tests hold that seam:
the v2 row is the one site G runs under, its schema's enum IS the vocabulary, the
kind the model names becomes the record's privacy class with the owner's
precedence, and a file the model clears is ordinary rather than pending.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import cli  # noqa: E402
from llm_harness.prompt_library import draft_bytes  # noqa: E402
from model_situation import NONE_OF_THESE  # noqa: E402
from privacy.vocabulary import (  # noqa: E402
    PRIVACY_CLASS_ALWAYS_LOCAL, PRIVACY_CLASS_ORDINARY, PRIVACY_CLASS_PROTECTED,
    PROTECTED_KIND_IDENTITY_DOCUMENT, ALWAYS_LOCAL_KIND_RECEIPT,
    RESTRICTED_KIND_LABELS, RESTRICTED_KINDS, LOCAL_MODEL_SITUATION,
)
from test_site_g_end_to_end import _rows, _run, _situation_answer  # noqa: E402


def _answer_naming(kind: str):
    """The end-to-end stub's answer with the second question answered too."""
    def answer(dossier: dict) -> str:
        raw = json.loads(_situation_answer(dossier))
        claim = raw["claims"][0]
        if claim["payload"]["situation"] != NONE_OF_THESE:
            claim["payload"]["restricted_kind"] = kind
        return json.dumps(raw)
    return answer


def test_site_g_runs_under_the_ratified_row_and_its_enum_is_the_vocabulary():
    """The row the owner ratified is the row the site reads, and the schema's ten
    are `RESTRICTED_KINDS` in the vocabulary's order -- one list, not two.

    SABOTAGE: point `cli.SITUATION_ROW` back at the v1 row, or edit the enum in
    the v2 schema, and this goes red.
    """
    template_id, candidate = cli.SITUATION_ROW
    # v2 added the field; v3 (gap 8) carries the same template and schema.
    assert candidate.startswith("situation-safety-first-v")
    template, schema, _policy = draft_bytes(template_id)
    payload = json.loads(schema)["properties"]["claims"]["items"]["properties"]["payload"]
    assert tuple(payload["properties"]["restricted_kind"]["enum"]) == RESTRICTED_KINDS
    assert "restricted_kind" not in payload["required"]
    text = template.decode("utf-8")
    assert '"restricted_kind"' in text
    for kind in RESTRICTED_KINDS:
        assert f'"{kind}"' in text, kind
        assert RESTRICTED_KIND_LABELS[kind] in text, kind


def test_a_kind_the_model_names_becomes_the_records_privacy_class(tmp_path, monkeypatch):
    """The recogniser writes the column S2 said had no writer.

    An identity document is a PROTECTED kind and a receipt an ALWAYS-LOCAL one;
    `privacy_class_for` carries the owner's precedence and this test asks only
    that the model's word reaches it.

    SABOTAGE: drop `restricted_kind=` from the `situation_classification` call in
    `ask_the_situation` and every row below reads `ordinary`.
    """
    for kind, expected in ((PROTECTED_KIND_IDENTITY_DOCUMENT, PRIVACY_CLASS_PROTECTED),
                           (ALWAYS_LOCAL_KIND_RECEIPT, PRIVACY_CLASS_ALWAYS_LOCAL)):
        root = tmp_path / kind
        root.mkdir()
        database, _report, _stub = _run(root, monkeypatch, _answer_naming(kind))
        rows = _rows(database, "SELECT privacy_class FROM classifications WHERE basis = ?",
                     LOCAL_MODEL_SITUATION)
        assert rows, "site G answered and no classification records its verdict"
        assert {row["privacy_class"] for row in rows} == {expected}, (kind, rows)


def test_a_file_the_model_clears_is_ordinary_and_never_pending(tmp_path, monkeypatch):
    """§14.3's distinction, kept: a file the local model LOOKED AT and found to be
    none of the ten is "on neither list", which is ordinary. Calling it pending
    would refuse the cloud to every file the recogniser cleared, which is the
    trade the owner declined (S2: recogniser first, then the closed default).

    SABOTAGE: pass `None` instead of `()` to `privacy_class_for` for a verdict
    with no kind and this reads `pending` -- which the store refuses to write.
    """
    database, _report, _stub = _run(tmp_path, monkeypatch, _situation_answer)
    rows = _rows(database, "SELECT privacy_class FROM classifications WHERE basis = ?",
                 LOCAL_MODEL_SITUATION)
    assert rows
    assert {row["privacy_class"] for row in rows} == {PRIVACY_CLASS_ORDINARY}


def test_a_kind_outside_the_ten_names_nothing(monkeypatch):
    """The schema's enum refuses it before a verdict exists; this is the reader's
    half, for a payload this deployment mis-addressed: a value outside
    `RESTRICTED_KINDS` is no kind, and the record is ordinary rather than a
    KeyError or a guess.

    SABOTAGE: return `kind` unconditionally from `restricted_kind_named_by_verdict`.
    """
    class _Verdict:
        outcome = next(iter(cli.ACCEPTING_OUTCOMES))
        dossier_id = "d-1"

    monkeypatch.setattr(cli, "_validated_payload",
                        lambda conn, verdict: {"situation": "x",
                                               "restricted_kind": "reciept"})
    assert cli.restricted_kind_named_by_verdict(None, _Verdict()) is None
    monkeypatch.setattr(cli, "_validated_payload",
                        lambda conn, verdict: {"situation": "x",
                                               "restricted_kind": ALWAYS_LOCAL_KIND_RECEIPT})
    assert cli.restricted_kind_named_by_verdict(None, _Verdict()) == ALWAYS_LOCAL_KIND_RECEIPT
