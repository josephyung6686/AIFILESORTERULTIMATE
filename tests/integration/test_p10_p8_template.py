"""P10 -> P8 Site E. P10 supplies the schema; P8 owns the verdict.

This is the seam the prior audit found unenforced: `grep -rn "fragment" src/`
returned one hit and it was about paths. With P10's two authorities injected, a
proposal naming an unpublished fragment comes back REJECT with
FRAGMENT_NOT_PUBLISHED, one attempting to publish comes back
FRAGMENT_PUBLICATION_ATTEMPTED, and a caller supplying no published-fragment
authority gets ValidationUnavailable — all three from P8's own machinery. P10
coins no refusal type and runs no second validator vocabulary; it answers one
question P8 cannot, "does this fragment exist".

The last test is the one that decides whether this product is limited to the
domains in this repository's research
(`planning/43-ROLE-VOCABULARY-AND-RECUT.md` §9): an evidence-backed dimension
from an unresearched domain reaches ACCEPT, and reaching ACCEPT promotes it to
nothing.
"""
from __future__ import annotations

import dataclasses
import json

from llm_harness.fixtures import FIXTURE_HANDLE_KEY, SITE_E_OUTCOME_PAIRS
from llm_harness.template_validation import validate_template_response
from llm_harness.vocabulary import ACCEPT_DIRECT, E_TEMPLATE, REJECT, SCOPE_TEMPLATE
from tree_design.template_schema import allowed_vocabulary_for, template_dependencies

# `tests/` carries no `__init__.py`, so `tests.p10...` is not an importable
# path. `tests/p10/__init__.py` makes `p10` the package, exactly as
# `tests/integration/test_p8_p2_replay.py` imports `from p8.conftest import`.
from p10.test_p10_template_schema import CATALOGUE, _payload  # noqa: F401

RELEASED = "span-1"


def _resolver(observation_key: str) -> str | None:
    return RELEASED if observation_key.startswith("obs-") else None


def _never_contradicts(*_a, **_k) -> bool:
    return False


def _response(payload: dict) -> bytes:
    claim = {
        "claim_ref": "c1",
        "payload": payload,
        "citations": [{
            "evidence_ref": "obs-1",
            "cited_span": RELEASED,
            "why_it_supports": "supports the recorded claim",
        }],
    }
    return json.dumps({"claims": [claim]}, separators=(",", ":")).encode("utf-8")


def _validate(dossier, payload):
    return validate_template_response(
        dossier, _response(payload), evidence_resolver=_resolver,
        contradicts=_never_contradicts, dependencies=template_dependencies(CATALOGUE),
        model_id="fixture-model", prompt_fingerprint="fp-canonical",
        dossier_builder="p10", release_audit_id=17, handle_key=FIXTURE_HANDLE_KEY)


def _dossier(vocabulary=("event", "capture_year")):
    pair = next(p for p in SITE_E_OUTCOME_PAIRS if p.name == "direct_accept")
    assert pair.dossier.call_site == E_TEMPLATE
    # P10 supplies the closure; the fixture's is P8's own two-word vocabulary.
    return dataclasses.replace(pair.dossier, allowed_vocabulary=tuple(vocabulary))


def test_a_published_fragment_reference_reaches_an_accept_verdict():
    verdicts, _report = _validate(_dossier(), _payload())
    assert verdicts[0].outcome == ACCEPT_DIRECT
    assert verdicts[0].scope == SCOPE_TEMPLATE


def test_an_unpublished_fragment_reference_gets_its_own_reason_code():
    """Not `SCHEMA_INVALID`. The shape is legal; the reference is not published.
    Site C already keeps this pair apart — `INVENTED_NODE` for a destination
    outside the dossier vocabulary, `NODE_NOT_IN_FROZEN_TREE` for one the frozen
    tree does not contain — and collapsing Site E's pair into one code would tell
    a reader "malformed" about a well-formed proposal."""
    payload = _payload(fragment_refs=[
        {"fragment_id": "counterpart-cycle", "fragment_version": 1}])
    verdicts, report = _validate(_dossier(), payload)
    assert verdicts[0].outcome == REJECT
    assert "FRAGMENT_NOT_PUBLISHED" in verdicts[0].reasons
    assert report.reasons_histogram["FRAGMENT_NOT_PUBLISHED"] == 1


def test_a_payload_attempting_to_publish_a_fragment_is_rejected_at_p8():
    """P8 scans the response, because reading a model response is P8's, and Site
    E is the only place a response could carry one of these."""
    payload = _payload(fragment_definitions=[
        {"fragment_id": "new-thing", "roles": ["x"]}])
    verdicts, _report = _validate(_dossier(), payload)
    assert verdicts[0].outcome == REJECT
    assert "FRAGMENT_PUBLICATION_ATTEMPTED" in verdicts[0].reasons


def test_a_site_e_call_with_no_published_fragment_authority_is_unavailable():
    """The point of a distinct authority: absence is REPORTABLE. A caller that
    supplies only `schema_validator` — `tests/p8/test_p8_sites.py` was one — must
    get `ValidationUnavailable`, exactly as it already does when the schema
    validator itself is missing. Silence here is what
    `planning/33-P8-COMPLETION-AUDIT.md:116-120` said not to ship."""
    from llm_harness.records import ValidationUnavailable
    from llm_harness.template_validation import TemplateDependencies

    result = validate_template_response(
        _dossier(), _response(_payload()), evidence_resolver=_resolver,
        contradicts=_never_contradicts,
        dependencies=TemplateDependencies(
            schema_validator=lambda payload: True, published_fragment=None),
        model_id="fixture-model", prompt_fingerprint="fp-canonical",
        dossier_builder="p10", release_audit_id=17, handle_key=FIXTURE_HANDLE_KEY)
    assert isinstance(result, ValidationUnavailable)
    assert result.missing == ("published_fragment",)


def _novel_payload(scope: str) -> dict:
    """One dimension from a field-less schema, cited, declaring its tier."""
    return _payload(
        domain="legal",
        allowed_fields=["matter_number"],
        fragment_refs=[],
        dimensions=[{"name": "matter_number", "evidence_ref": "obs-1",
                     "requirement": "required", "metadata_only": False,
                     "order_index": 0, "scope": scope}],
        levels=[{"dimension": "matter_number",
                 "retrieval_justification": "Every filing for one matter is one folder."}],
        example_label_chains=[["Legal", "M-2026-014"]],
    )


def test_t1_an_evidence_backed_novel_dimension_is_accepted_as_template_local():
    """T1, and the ruling this whole design exists to satisfy.

    `legal` declares no fields, so the closure P10 supplies is EMPTY — Contract
    W1 keeps it that way. Under the old whole-payload gate an empty closure
    rejected every proposal, which made a field-less schema undesignable. Under
    Contract W2 the name is classified `template-local` and the proposal is
    accepted, so a group from an unresearched domain still gets a reviewable
    branch design.
    """
    assert allowed_vocabulary_for(CATALOGUE, uses_schema="legal") == ()
    verdicts, _report = _validate(_dossier(()), _novel_payload("template-local"))
    assert verdicts[0].outcome == ACCEPT_DIRECT
    assert verdicts[0].scope == SCOPE_TEMPLATE


def test_t2_the_same_dimension_claiming_schema_field_is_still_rejected():
    """T2. The old gate's protective force is preserved intact; only its blast
    radius changes. Claiming `schema-field` for a name outside the closure is the
    model asserting a field it was not given, and that is still a REJECT."""
    verdicts, _report = _validate(_dossier(()), _novel_payload("schema-field"))
    assert verdicts[0].outcome == REJECT
    assert verdicts[0].may_propose is False


def test_t3_a_borrowed_field_key_is_rejected_as_schema_invalid():
    """T3. `target_school` is another schema's live P6 field. Relabelling it
    `template-local` inside a `photos` proposal fails P10's schema validator, and
    P8 reports SCHEMA_INVALID — not a fragment code, because it is a shape
    defect in what the payload claims."""
    payload = _payload(
        allowed_fields=["event", "capture_year", "target_school"],
        dimensions=[{"name": "target_school", "evidence_ref": "obs-1",
                     "requirement": "required", "metadata_only": False,
                     "order_index": 0, "scope": "template-local"}],
        levels=[{"dimension": "target_school",
                 "retrieval_justification": "borrowed from another schema"}],
    )
    verdicts, _report = _validate(_dossier(), payload)
    assert verdicts[0].outcome == REJECT
    assert "SCHEMA_INVALID" in verdicts[0].reasons


def test_t4_an_uncited_template_local_dimension_is_still_rejected():
    """T4 — a regression guard on a gate that must not be relaxed. Widening the
    tier must not widen the citation requirement: a template-local dimension
    whose `evidence_ref` is not in the response's own citations is still a
    REJECT, exactly as it was."""
    payload = _novel_payload("template-local")
    payload["dimensions"][0]["evidence_ref"] = "obs-uncited"
    verdicts, _report = _validate(_dossier(()), payload)
    assert verdicts[0].outcome == REJECT


def test_t8_publishing_a_fragment_beside_a_template_local_dimension_is_refused():
    """T8. Contract W4.5: a template-local dimension is a proposal about ONE
    branch, and it may never become a canonical fragment from inside a model
    call. The existing gate is load-bearing for layer 2, so it gets a layer-2
    fixture."""
    payload = _novel_payload("template-local")
    payload["fragment_definitions"] = [{"fragment_id": "matter", "roles": ["x"]}]
    verdicts, _report = _validate(_dossier(()), payload)
    assert verdicts[0].outcome == REJECT
    assert "FRAGMENT_PUBLICATION_ATTEMPTED" in verdicts[0].reasons


def test_t6_site_as_allow_list_is_unmoved_by_an_accepted_template_local_name():
    """T6 — "the single most important test in this document."

    A template-local dimension is a label, not a fact. Accepting one at Site E
    must not make `matter_number` proposable as a FACT at Site A, whose closure
    is P6's active schema and is a different field on a different dossier.
    """
    from facts.fields import FIELD_ROWS

    verdicts, _report = _validate(_dossier(()), _novel_payload("template-local"))
    assert verdicts[0].outcome == ACCEPT_DIRECT
    # P6's catalogue is untouched: `matter_number` is not a field, so Site A's
    # allow-list cannot contain it and a fact proposal for it has nowhere to go.
    assert "matter_number" not in {row.field_key for row in FIELD_ROWS}


def test_p10_supplies_no_transport_gate_or_verdict():
    """P8 owns the only model invocation and the only verdict. If P10 ever grows
    an import of the gate or the transport, this fails and says why."""
    import ast
    from pathlib import Path

    src = Path(__file__).resolve().parents[2] / "src" / "tree_design"
    forbidden = {"privacy.gate", "llm_harness.transport", "llm_harness.harness"}
    offenders = []
    for path in sorted(src.glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.ImportFrom) and node.module in forbidden:
                offenders.append(f"{path.name} imports {node.module}")
    assert offenders == []
