# tools/promptbench/judge.py
"""One model answer, judged by the product's own validator and by the case.

Two judgements, kept apart because they answer different questions:

* **What the machine says.** `llm_harness.sites.dispatch` at the case's site,
  with the site's real authorities injected (`placement_validation`'s two
  oracles from `cli.SUPPORT_POLICY`, P10's template dependencies over the
  shipped catalogue, P6's fact machinery at A). This is the verdict the product
  would record, reason codes included.
* **What the case says.** Whether the answer the model gave is the answer the
  case author labelled -- the destination, the action, the membership decisions,
  the dimensions, the field values. The validator cannot know this; it is the
  `00`:223 metric ("did the model return unknown when evidence was insufficient")
  and the site's outcome metric from `103` §28.1 step 4.

A response the case calls correct that the validator rejects is recorded as
both, because that pair is exactly how a contract gap shows up in numbers.
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

import jsonschema  # noqa: E402

from llm_harness.placement_validation import (  # noqa: E402
    PlacementDependencies, ResidualDependencies,
)
from llm_harness.sites import SiteDependencies, dispatch  # noqa: E402
from llm_harness.vocabulary import (  # noqa: E402
    A_FACT, ABSTAIN, ACCEPT_CONTEXT_SUPPORTED, ACCEPT_DIRECT, B_GROUP,
    C_PLACEMENT, D_RESIDUAL, E_TEMPLATE, LEAVE_IN_CURRENT_LOCATION,
    MARK_REVIEW_LATER, SCHEMA_INVALID,
)

from tools.promptbench.cases import Case
from tools.promptbench.dossiers import BENCH_HANDLE_KEY, resolver_for

ACCEPTED = frozenset({ACCEPT_DIRECT, ACCEPT_CONTEXT_SUPPORTED})
#: D actions that name no destination. A case whose expectation is one of these
#: is a should-abstain case for the `00`:223 metric.
D_NO_DESTINATION = frozenset({ABSTAIN, LEAVE_IN_CURRENT_LOCATION, MARK_REVIEW_LATER})


@dataclass
class Judgement:
    case_id: str
    site: str
    parsed: bool
    json_schema_valid: bool
    json_schema_errors: list[str]
    verdicts: list[dict]
    worst_outcome: str | None
    accepted: bool
    citations_total: int
    citations_resolved: int
    citations_span_matched: int
    abstained: bool
    answer: dict
    should_abstain: bool
    correct: bool | None
    abstain_correct: bool | None
    detail: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return asdict(self)


def _never_contradicts(payload, dossier) -> bool:
    return False


def site_dependencies_for(case: Case, *, catalogue=None,
                          support_policy=None) -> SiteDependencies:
    """The authorities the site's validator needs, from the case and the product."""
    site = case.site
    plan = case.plan_version or ""
    frozen = frozenset(case.authorities.get("frozen_nodes", case.allowed_vocabulary))

    def node_exists(node_id: str, plan_version: str) -> bool:
        return plan_version == plan and node_id in frozen

    def sensitivity_ok(dossier, payload) -> bool:
        return True

    if site == C_PLACEMENT:
        if support_policy is None:
            from cli import SUPPORT_POLICY as support_policy  # the deployment's
        return SiteDependencies(
            fact=None, residual=None, template=None,
            placement=PlacementDependencies(
                node_exists=node_exists,
                support_threshold=support_policy.minimum_support_threshold,
                margin_predicate=support_policy.margin_predicate,
                sensitivity_policy=sensitivity_ok))
    if site == D_RESIDUAL:
        return SiteDependencies(
            fact=None, placement=None, template=None,
            residual=ResidualDependencies(
                node_exists=node_exists, sensitivity_policy=sensitivity_ok,
                approved_target_ids=tuple(
                    case.authorities.get("approved_target_ids", ()))))
    if site == E_TEMPLATE:
        from tree_design.template_schema import template_dependencies
        if catalogue is None:
            from production import load_shipped_catalogue, read_packaged_library_file
            catalogue = load_shipped_catalogue(read_packaged_library_file)
        return SiteDependencies(fact=None, placement=None, residual=None,
                                template=template_dependencies(catalogue))
    if site == B_GROUP:
        return SiteDependencies(fact=None, placement=None, residual=None,
                                template=None)
    raise ValueError(f"site A builds its authorities in site_a.py, not here: {site}")


def _parse(response_bytes: bytes):
    try:
        parsed = json.loads(response_bytes.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None
    if not isinstance(parsed, dict) or not isinstance(parsed.get("claims"), list):
        return None
    return parsed


def _claims(parsed) -> list[dict]:
    if parsed is None:
        return []
    return [claim for claim in parsed["claims"] if isinstance(claim, dict)]


def _payload(claim: dict) -> dict:
    payload = claim.get("payload")
    return payload if isinstance(payload, dict) else {}


def _schema_check(parsed, schema: dict) -> tuple[bool, list[str]]:
    if parsed is None:
        return False, ["not a JSON object with a claims list"]
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(parsed), key=lambda e: list(e.path))
    return (not errors), [f"{'/'.join(str(p) for p in e.path)}: {e.message}"[:200]
                          for e in errors[:6]]


# --- site readers ---------------------------------------------------------------


def _read_c(case: Case, claims: list[dict]) -> tuple[dict, bool]:
    claim = claims[0] if claims else {}
    payload = _payload(claim)
    destination = payload.get("destination")
    abstained = destination in (None, "none") or claim.get("unknown") is not None
    return {
        "destination": destination,
        "per_dimension_support": payload.get("per_dimension_support"),
        "alternatives": payload.get("alternatives"),
        "conflicts_considered": payload.get("conflicts_considered"),
        "support": payload.get("support"),
        "next_support": payload.get("next_support"),
        "refinement": payload.get("refinement"),
        "unknown": claim.get("unknown"),
    }, abstained


def _read_d(case: Case, claims: list[dict]) -> tuple[dict, bool]:
    claim = claims[0] if claims else {}
    payload = _payload(claim)
    action = payload.get("action")
    abstained = action in D_NO_DESTINATION or (
        action is None and claim.get("unknown") is not None)
    return {
        "action": action,
        "target": payload.get("target"),
        "stop_reason": payload.get("stop_reason"),
        "relationships_considered": payload.get("relationships_considered"),
        "unknown": claim.get("unknown"),
    }, abstained


def _read_b(case: Case, claims: list[dict]) -> tuple[dict, bool]:
    claim = claims[0] if claims else {}
    payload = _payload(claim)
    coherent = payload.get("coherent")
    members = {}
    raw_members = payload.get("members")
    if isinstance(raw_members, list):
        for item in raw_members:
            if isinstance(item, dict) and isinstance(item.get("file_id"), str):
                members[item["file_id"]] = item.get("decision")
    outliers = []
    raw_outliers = payload.get("outliers")
    if isinstance(raw_outliers, list):
        outliers = [item.get("file_id") for item in raw_outliers
                    if isinstance(item, dict)]
    abstained = coherent in ("no", "insufficient") or claim.get("unknown") is not None
    return {
        "coherent": coherent, "basis": payload.get("basis"),
        "category": payload.get("category"), "label": payload.get("label"),
        "members": members, "outliers": outliers,
        "merge_terms": payload.get("merge_terms"),
        "unknown": claim.get("unknown"),
    }, abstained


def _read_e(case: Case, claims: list[dict]) -> tuple[dict, bool]:
    claim = claims[0] if claims else {}
    payload = _payload(claim)
    names = []
    dims = payload.get("dimensions")
    if isinstance(dims, list):
        for item in dims:
            if isinstance(item, dict):
                names.append(item.get("name"))
    levels = []
    raw_levels = payload.get("levels")
    if isinstance(raw_levels, list):
        levels = [item.get("dimension") for item in raw_levels
                  if isinstance(item, dict)]
    abstained = claim.get("unknown") is not None
    return {
        "domain": payload.get("domain"), "dimensions": names, "levels": levels,
        "scopes": [item.get("scope") for item in dims
                   if isinstance(item, dict)] if isinstance(dims, list) else [],
        "example_label_chains": payload.get("example_label_chains"),
        "unknown": claim.get("unknown"),
    }, abstained


def _read_a(case: Case, claims: list[dict]) -> tuple[dict, bool]:
    fields: dict[str, object] = {}
    for claim in claims:
        payload = _payload(claim)
        key = payload.get("field")
        if not isinstance(key, str):
            continue
        if claim.get("unknown") is not None:
            fields[key] = None
        else:
            fields[key] = payload.get("value")
    expected = case.expect.get("fields", {})
    abstained = all(fields.get(k, "MISSING") is None for k, v in expected.items()
                    if v is None) if expected else False
    return {"fields": fields}, abstained


READERS = {C_PLACEMENT: _read_c, D_RESIDUAL: _read_d, B_GROUP: _read_b,
           E_TEMPLATE: _read_e, A_FACT: _read_a}


# --- correctness --------------------------------------------------------------


def _correct(case: Case, answer: dict, accepted: bool) -> tuple[bool | None, dict]:
    expect = case.expect
    site = case.site
    detail: dict = {}
    if site == C_PLACEMENT:
        want = expect.get("destination")
        if want in (None, "none"):
            return None, detail
        detail["destination_matches"] = answer["destination"] == want
        detail["accepted"] = accepted
        return bool(answer["destination"] == want), detail
    if site == D_RESIDUAL:
        want_action = expect.get("action")
        ok = answer["action"] == want_action
        if "target" in expect and expect["target"] is not None:
            ok = ok and answer["target"] == expect["target"]
            detail["target_matches"] = answer["target"] == expect["target"]
        detail["action_matches"] = answer["action"] == want_action
        if want_action in D_NO_DESTINATION:
            return None, detail
        return bool(ok), detail
    if site == B_GROUP:
        want = expect.get("coherent")
        ok = answer["coherent"] == want
        detail["coherent_matches"] = ok
        members_expected = expect.get("members", {})
        member_hits = sum(1 for f, d in members_expected.items()
                          if answer["members"].get(f) == d)
        detail["members_expected"] = len(members_expected)
        detail["members_correct"] = member_hits
        outliers_expected = set(expect.get("outliers", ()))
        detail["outliers_found"] = len(outliers_expected & set(answer["outliers"]))
        detail["outliers_expected"] = len(outliers_expected)
        if want in ("no", "insufficient"):
            return None, detail
        ok = ok and member_hits == len(members_expected)
        ok = ok and outliers_expected <= set(answer["outliers"])
        if expect.get("label_required"):
            ok = ok and bool(answer.get("label"))
        if expect.get("category_in") is not None:
            ok = ok and answer.get("category") in set(expect["category_in"])
            detail["category_valid"] = answer.get("category") in set(expect["category_in"])
        return bool(ok), detail
    if site == E_TEMPLATE:
        if expect.get("abstain"):
            return None, detail
        names = [n for n in answer["dimensions"] if isinstance(n, str)]
        must = set(expect.get("must_include", ()))
        forbid = set(expect.get("must_exclude", ()))
        detail["must_include_met"] = must <= set(names)
        detail["must_exclude_met"] = not (forbid & set(names))
        detail["accepted"] = accepted
        ok = accepted and must <= set(names) and not (forbid & set(names))
        if expect.get("first") is not None:
            detail["first_matches"] = bool(names) and names[0] == expect["first"]
            ok = ok and detail["first_matches"]
        return bool(ok), detail
    if site == A_FACT:
        expected = expect.get("fields", {})
        got = answer["fields"]
        per_field = {}
        for key, want in expected.items():
            value = got.get(key, "MISSING")
            if want is None:
                per_field[key] = value is None
            else:
                per_field[key] = isinstance(value, str) and value == want
        detail["per_field"] = per_field
        answer_fields = {k for k, v in expected.items() if v is not None}
        if not answer_fields:
            return None, detail
        return all(per_field[k] for k in answer_fields), detail
    raise ValueError(site)


def judge(case: Case, dossier, response_bytes: bytes, *, schema: dict,
          site_dependencies: SiteDependencies, evidence_resolver=None,
          contradicts=None, conn=None, model_id: str = "bench",
          prompt_fingerprint: str = "bench") -> Judgement:
    parsed = _parse(response_bytes)
    schema_ok, schema_errors = _schema_check(parsed, schema)
    result = dispatch(
        conn, dossier, response_bytes,
        site_dependencies=site_dependencies,
        evidence_resolver=evidence_resolver or resolver_for(case),
        contradicts=contradicts or _never_contradicts,
        model_id=model_id, prompt_fingerprint=prompt_fingerprint,
        dossier_builder="promptbench", release_audit_id=None,
        policy_version=dossier.policy_version, apply_consequence=False,
        handle_key=BENCH_HANDLE_KEY)
    if not isinstance(result, tuple):
        raise RuntimeError(f"validation unavailable: {result}")
    verdicts, report = result
    worst = None
    if verdicts:
        from llm_harness.harness import worst_outcome
        worst = worst_outcome(verdicts).outcome
    accepted = bool(verdicts) and all(v.outcome in ACCEPTED for v in verdicts)
    claims = _claims(parsed)
    answer, abstained = READERS[case.site](case, claims)
    correct, detail = _correct(case, answer, accepted)
    should = case.should_abstain
    abstain_correct = (abstained if should else None)
    if not should and correct is not None:
        detail["false_abstention"] = abstained
    return Judgement(
        case_id=case.case_id, site=case.site, parsed=parsed is not None,
        json_schema_valid=schema_ok, json_schema_errors=schema_errors,
        verdicts=[{"claim_ref": v.claim_ref, "outcome": v.outcome,
                   "disposition": v.disposition, "reasons": list(v.reasons)}
                  for v in verdicts],
        worst_outcome=worst, accepted=accepted,
        citations_total=report.citations_total,
        citations_resolved=report.citations_resolved,
        citations_span_matched=report.citations_span_matched,
        abstained=abstained, answer=answer, should_abstain=should,
        correct=correct, abstain_correct=abstain_correct, detail=detail)


__all__ = ["ACCEPTED", "Judgement", "judge", "site_dependencies_for"]
