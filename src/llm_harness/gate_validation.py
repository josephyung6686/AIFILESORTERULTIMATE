# src/llm_harness/gate_validation.py
"""Site H: is this file a record of one of the ten restricted kinds, and which.

`00` amendment 7(c)'s gate. The question is narrower than any other site's and it
is the one the whole cloud route rests on: a file this site clears may be sent to
a provider, and a file it names stays on this machine. Everything else about the
file -- what it is about, which situation it is part of, where it belongs -- is
site G's question and is asked afterwards, of the whole library.

**THIS MODULE ADDS NO CITATION CHECK AND WANTS NONE**, which is
`situation_validation`'s own sentence and is true here for the same reason:
`validation.check_citations` is the one check every site runs, and a second one
beside it is how site A came to accept a span it had invented. `validate_response`
is the whole of the machinery and `_gate_site` is a hook inside it.

**WHAT THE HOOK ADDS IS ONE THING: the kind is on the list.** The ten are a closed
vocabulary the owner ruled member by member (`105` §13.3) and the eleventh option
is the structural decline. A model naming an eleventh kind has invented a class,
which `recognition/_CONTRACT.md` rule 5 forbids the recogniser and `00`:42 forbids
the model; and an invented kind that happened to resemble a real one would decide
whether somebody's file leaves their device.

**`none_of_these` IS AN ANSWER AND NOT A SILENCE, and that is the difference
between this site and site G.** At G a decline leaves the file where the rules
left it, which is local, and costs nothing. Here the ratified shape for
`none_of_these` is the `unknown` shape, so it arrives as an `ABSTAIN` verdict
through `validation._validate_claim` before this hook is reached at all -- and the
CALLER reads the payload to tell the two apart. That reading is
`cli.gate_kind_named_by_verdict`'s and it is deliberately not made here: P8 judges
whether an answer is admissible and never what the product does with it, and what
the product does with a clearance is release a file to a provider.

**NO NEW REASON CODE**, on site G's precedent: the reason codes are a closed
vocabulary the owner approves member by member, and an answer outside the list is
refused as `SCHEMA_INVALID` with the broken rule named in the address (`104`
R-99's pattern).
"""
from __future__ import annotations

import dataclasses
from collections.abc import Mapping, Sequence

from llm_harness.records import Dossier, P8Verdict, ValidationUnavailable
from llm_harness.validation import validate_response
from llm_harness.vocabulary import SCHEMA_INVALID

#: Rule 1 of the gate text: *"`restricted_kind` must be copied character for
#: character from `allowed_vocabulary`. An identifier you compose is a kind that
#: does not exist."* Named for `104` R-99's reason -- the address says which rule
#: broke while the reason code stays the closed-vocabulary word it already was.
_NOT_IN_ALLOWED_VOCABULARY: str = "restricted_kind_not_in_allowed_vocabulary"
#: Rule 4: *"`alternatives` lists other identifiers from `allowed_vocabulary` that
#: the text also fits, or is empty."* Refused rather than dropped, on site G's own
#: argument: an alternative is a second reading of the same file, and a reader who
#: sees it silently removed cannot tell a model that named two kinds from one that
#: named one -- which at this site is the difference between a file that leaves
#: and a file that does not.
_ALTERNATIVE_NOT_IN_VOCABULARY: str = "alternative_not_in_allowed_vocabulary"
#: The payload shape rule 1 rests on. `validate_response` checks the claim's
#: envelope and not this site's payload, so an answer with no kind at all would
#: otherwise be accepted on the strength of a citation supporting nothing named.
_KIND_MISSING: str = "payload_restricted_kind_missing"


def _payload_of(raw: object) -> Mapping[str, object]:
    if not isinstance(raw, Mapping):
        return {}
    payload = raw.get("payload")
    return payload if isinstance(payload, Mapping) else {}


def _schema_invalid(verdict: P8Verdict, address: str) -> P8Verdict:
    """`SCHEMA_INVALID`, with the broken rule in the verdict's own address.

    `situation_validation._schema_invalid`, one site along and for its reason: the
    universal machinery has already measured what the model cited, and rebuilding
    the verdict would throw away the only record of whether the answer was
    anchored at all, on a refusal that is about the ANSWER.
    """
    return dataclasses.replace(
        verdict,
        verdict_id=f"{verdict.dossier_id}:{address}",
        claim_ref=address,
        outcome="reject",
        disposition="rejected",
        reasons=(SCHEMA_INVALID,),
        may_propose=False,
        requires_review=False,
    )


def _gate_site(dossier: Dossier, raw: object, verdict: P8Verdict):
    """The one thing this site checks beyond the universal citation rules.

    Returns a replacement verdict, or `None` to leave the universal one standing.

    THE DECLINE IS NOT SPECIAL-CASED HERE and that is not an omission. A claim
    carrying `unknown` never reaches this hook -- `validation._validate_claim`
    returns `ABSTAIN` for it directly -- so what arrives here is always a claim
    that cited something, whether the kind it named is one of the ten or the
    eleventh option. Both are checked the same way: the value must be on the list
    the model was shown.
    """
    payload = _payload_of(raw)
    kind = payload.get("restricted_kind")
    if not isinstance(kind, str) or not kind:
        return _schema_invalid(verdict, f"gate:{_KIND_MISSING}")

    allowed = set(dossier.allowed_vocabulary)
    if kind not in allowed:
        # THE INVENTION, CAUGHT WHERE IT IS STILL LEGIBLE. Downstream this is a
        # string that either is or is not one of `105` §13.3's ten, and a model
        # that invented an eleventh would either protect a file for a kind the
        # product cannot act on or -- read the other way by a later reader --
        # clear it.
        return _schema_invalid(
            verdict, f"gate:{_NOT_IN_ALLOWED_VOCABULARY}:{kind[:40]}")

    alternatives = payload.get("alternatives")
    if alternatives is None:
        alternatives = []
    if isinstance(alternatives, (str, bytes)) or not isinstance(
            alternatives, Sequence):
        return _schema_invalid(verdict, f"gate:{_ALTERNATIVE_NOT_IN_VOCABULARY}")
    for item in alternatives:
        if not isinstance(item, str) or item not in allowed:
            return _schema_invalid(
                verdict,
                f"gate:{_ALTERNATIVE_NOT_IN_VOCABULARY}:{str(item)[:40]}")
    return None


def validate_gate_response(
    dossier: Dossier,
    response_bytes: bytes,
    *,
    evidence_resolver,
    contradicts,
    model_id: str,
    prompt_fingerprint: str,
    dossier_builder: str,
    release_audit_id: int | None,
    handle_key: bytes,
) -> tuple[tuple[P8Verdict, ...], object] | ValidationUnavailable:
    """Site H's validator: the universal checks, plus "the kind is on the list".

    No `dependencies` argument, on sites B and G's precedent: C, D and E take typed
    authority bundles because they need a frozen tree, a controlled action set or a
    fragment catalogue, and this site needs none of them. Everything it checks is
    already in the dossier -- the eleven options it showed the model and the
    evidence it released -- so a bundle here would be a slot a caller could fill
    with an acceptance callback, which is the shape `sites.py` exists to refuse.
    """
    return validate_response(
        dossier,
        response_bytes,
        evidence_resolver=evidence_resolver,
        site_validator=_gate_site,
        contradicts=contradicts,
        model_id=model_id,
        prompt_fingerprint=prompt_fingerprint,
        dossier_builder=dossier_builder,
        release_audit_id=release_audit_id,
        handle_key=handle_key,
    )


__all__ = ["validate_gate_response"]
