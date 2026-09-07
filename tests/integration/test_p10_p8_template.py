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

import pytest

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


# --- packet G12: the C3 refusal that never became a request ----------------------
#
# "E: No live caller: `routing.py`'s C3 refusal never becomes an E request. E can
# be ratified and stay inert; the bakeoff is the only exercise it gets." Every
# other half existed -- the request builder, the two authorities, the validator,
# the drafted text. What nothing did was ask.


def _report(*gates):
    from tree_design.routing import RoutingReport
    from tree_design.templates import CompositionConflict

    return RoutingReport(
        candidates=(),
        conflicts=tuple(
            CompositionConflict(gate, ["ap.academic.coursework"],
                                "no recipe recognises this situation")
            for gate in gates),
        deferred=0)


def _authorities(**over):
    from types import SimpleNamespace

    values = dict(template_call_for=None)
    values.update(over)
    return SimpleNamespace(**values)


def test_a_c3_refusal_becomes_a_template_request():
    """The gate that says "no recipe recognises the situation these files are in"
    is exactly the sentence `00`:97's site E answers."""
    from tree_design.pipeline import _ask_for_a_template

    asked = []
    _ask_for_a_template(
        _authorities(template_call_for=lambda groups, version: asked.append(
            (tuple(groups), version))),
        _report("C3"), groups=("g-1", "g-2"), plan_version="plan-1")

    assert asked == [(("g-1", "g-2"), "plan-1")]


def test_a_branch_a_recipe_covers_asks_for_no_template():
    """A branch the library already has a recipe for does not need one designed,
    and a call made anyway would spend a release on a question nobody asked."""
    from tree_design.pipeline import _ask_for_a_template

    asked = []
    _ask_for_a_template(
        _authorities(template_call_for=lambda groups, version: asked.append(1)),
        _report(), groups=("g-1",), plan_version="plan-1")
    # A different refusal is a different question. C6 names material no recipe
    # covers and is answered by naming the files, not by designing a template.
    _ask_for_a_template(
        _authorities(template_call_for=lambda groups, version: asked.append(1)),
        _report("C6"), groups=("g-1",), plan_version="plan-1")

    assert asked == []


@pytest.fixture()
def academics(conn, tmp_path):
    """§5.5's three files as real P1/P4/P6 rows, plus P5's and P7's tables.

    The same corpus P10's materialiser is tested against, because a site-E request
    is built out of exactly what that corpus holds: the group's anchors, the facts
    they settled and the observations those facts cite.
    """
    from database_agent.db import create_schema
    from evidence_shape.schema import create_evidence_schema
    from extractors.schema import create_extraction_schema
    from facts.fields import create_fields

    from p10.p6_fixtures import seed_academics

    create_schema(conn)
    create_evidence_schema(conn)
    create_extraction_schema(conn)
    create_fields(conn)
    return seed_academics(conn, tmp_path)


def _accepted(seeded, *names):
    from grouping.vocabulary import CONTEXT_SUPPORTED, DIRECT_ANCHOR
    from tree_design.upstream import AcceptedGroup, GroupMember

    return AcceptedGroup(
        group_id="g_busib", label="BUSIB 4300", domain="academic",
        members=tuple(
            GroupMember(file_id=seeded.subjects[name][0],
                        content_hash=seeded.subjects[name][1],
                        basis=DIRECT_ANCHOR if index == 0 else CONTEXT_SUPPORTED)
            for index, name in enumerate(names)),
        anchor_facts=(), excluded_members=())


def test_the_request_is_addressed_to_site_e_under_its_own_eligibility_reason(
        academics):
    """The record P8 refuses to build wrongly. `E_template` is in P8's
    `SITES_REQUIRING_PLAN_VERSION` and `ACCEPTED_GROUP_FITS_NO_EXISTING_TEMPLATE`
    is its one controlled reason, so a request that reached P8 with either wrong
    would be refused rather than answered."""
    from types import SimpleNamespace

    from llm_harness.vocabulary import ACCEPTED_GROUP_FITS_NO_EXISTING_TEMPLATE
    from model_template import TEMPLATE_STAGE, template_request_for

    prompt = SimpleNamespace(template_id="e.draft", template_bytes=b"t",
                             response_schema_bytes=b"{}", call_site=E_TEMPLATE,
                             call_site_version="1", ratified=False,
                             shaping_policy_bytes=b"{}")
    request = template_request_for(
        academics.conn, group=_accepted(academics, "syllabus", "hw3"),
        plan_version="plan-1",
        model_target=SimpleNamespace(locality="local", model_id="m",
                                     provider="on-device"),
        prompt=prompt, max_dossier_tokens=4000)

    assert request is not None
    assert request.call_site == E_TEMPLATE
    assert request.eligibility_reason == ACCEPTED_GROUP_FITS_NO_EXISTING_TEMPLATE
    assert request.plan_version == "plan-1"
    assert request.model_call_request.stage == TEMPLATE_STAGE
    assert request.model_call_request.target.group_id == "g_busib"


def test_the_request_carries_the_group_and_cites_only_its_anchors(academics):
    """`00`:97's input is "the group dossier, representative files, validated
    facts". Every member is named as a REFERENCE, because a template designed
    without knowing what it is designing for is guessing; only the ANCHORS' facts
    are cited, because a context-supported member is in the group by retrieval and
    a dimension justified by what it happens to say is a level built on a guess.
    """
    from types import SimpleNamespace

    from model_template import EXCERPT_KIND, MEMBER_KIND, template_request_for

    prompt = SimpleNamespace(template_id="e.draft", template_bytes=b"t",
                             response_schema_bytes=b"{}", call_site=E_TEMPLATE,
                             call_site_version="1", ratified=False,
                             shaping_policy_bytes=b"{}")
    request = template_request_for(
        academics.conn, group=_accepted(academics, "syllabus", "hw3"),
        plan_version="plan-1",
        model_target=SimpleNamespace(locality="local", model_id="m",
                                     provider="on-device"),
        prompt=prompt, max_dossier_tokens=4000)

    members = {item.evidence_ref for item in request.evidence_items
               if item.kind == MEMBER_KIND}
    cited = {item.location for item in request.evidence_items
             if item.kind == EXCERPT_KIND}

    assert members == {academics.file_id("syllabus"), academics.file_id("hw3")}
    # The anchor settled three fields and the context-supported member's are not
    # offered, so the fields named are the anchor's own.
    assert cited and cited <= {"school", "subject", "work_type"}
    # Nothing about where the file IS. `releasable_excerpts` refuses the path and
    # the filename at this site for the reason it refuses them at C: how a
    # person's folders should be shaped is exactly what those look like evidence
    # for, and they are the one thing that may never leave the device.
    assert "path" not in cited and "filename" not in cited


def test_a_group_whose_anchors_cite_nothing_releasable_is_not_asked(academics):
    """`00`:97 forbids inventing an unsupported fact, and a template designed from
    no evidence is that at the one site whose whole output is structure. `None` is
    a real state and is not an error."""
    from types import SimpleNamespace

    from model_template import template_request_for

    prompt = SimpleNamespace(template_id="e.draft", template_bytes=b"t",
                             response_schema_bytes=b"{}", call_site=E_TEMPLATE,
                             call_site_version="1", ratified=False,
                             shaping_policy_bytes=b"{}")
    # A group with no DIRECT anchor: every member is context-supported, so there
    # is no anchor's reading to cite.
    group = _accepted(academics, "syllabus", "hw3")
    context_only = dataclasses.replace(group, members=group.members[1:])

    assert template_request_for(
        academics.conn, group=context_only, plan_version="plan-1",
        model_target=SimpleNamespace(locality="local", model_id="m",
                                     provider="on-device"),
        prompt=prompt, max_dossier_tokens=4000) is None


def test_a_deployment_with_no_model_designs_the_branch_exactly_as_before():
    """`None` is the ordinary run and is not a refusal: the C3 conflict is still
    in the report and still reaches the person."""
    from tree_design.pipeline import _ask_for_a_template

    _ask_for_a_template(_authorities(), _report("C3"), groups=("g-1",),
                        plan_version="plan-1")


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
