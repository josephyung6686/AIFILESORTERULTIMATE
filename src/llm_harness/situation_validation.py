# src/llm_harness/situation_validation.py
"""Site G: which situation is this file part of, and is the answer anchored.

`104` §17.1's seventh call site. The question is `00`:39's -- an LLM receives
evidence packets for files that "remain ambiguous, have multiple plausible
domains, or contain language that requires interpretation" -- and the answer is
one identifier out of the shortlist the recognisers themselves raised, or a
decline.

**THIS MODULE ADDS NO CITATION CHECK AND WANTS NONE.** `validation.
check_citations` is the one check every site runs: the reference must be an item
of this dossier, that item must have been RELEASED, the resolver must still find
it, and the quoted span must appear inside the released (possibly redacted)
value. Site A's history is why a second one is not written here -- it ran its own,
took the citable set from P6's `FactRequest` rather than from the release, and
copied `resolved` into `span_matched`, so a key P7 withheld quoted with an
invented span was accepted and the fact was written. `validate_response` is
therefore the whole of this file's machinery and `_situation_site` is a hook
inside it, exactly as `group_validation` is at site B.

**WHAT THE SITE HOOK ADDS IS ONE THING: the answer is on the list.**
`recognition/_CONTRACT.md` rule 5 forbids the recogniser inventing a class to let
the pipeline continue, and `00`:42 forbids the LLM inventing a fact schema. A
model naming a situation nobody proposed is both of those wearing a model's face,
and it is the failure that would be least visible downstream: an invented
identifier that happens to be a real schema id would place files.

**NO NEW REASON CODE, AND THAT IS DELIBERATE.** The reason codes are a closed
vocabulary the owner approves member by member (`vocabulary.py` records the last
two such approvals in full). An answer outside the list is refused as
`SCHEMA_INVALID` with the RULE NAMED IN THE ADDRESS, which is `104` R-99's
pattern at site A: "The reason code is unchanged ... and the `claim_ref` now says
which claim and which rule." One approval was taken for this site, and it was
spent on the call site itself.

**A DECLINE IS A SUCCESS.** `00`: "Correct abstention is a successful outcome",
and the ratified prompt's own paragraph says so to the model: "'none' is a
correct answer and it is recorded as one. It costs nothing and it is not counted
against you." The shape the prompt asks for is a claim carrying `unknown`, which
`validation._validate_claim` turns into an `ABSTAIN` verdict before this hook is
reached. A model that instead writes the decline word into `payload.situation`
means the same thing and is recorded the same way rather than refused on a
formatting difference -- and `_situation_site` is where that equivalence lives,
because the alternative is a `REJECT` on a file the model correctly declined to
name, which would then read as the model getting it wrong.
"""
from __future__ import annotations

import dataclasses
from collections.abc import Mapping, Sequence

from llm_harness.records import Dossier, P8Verdict, ValidationUnavailable
from llm_harness.validation import validate_response
from llm_harness.vocabulary import (
    ABSTAIN,
    SCHEMA_INVALID,
    UNRESOLVED,
)

#: The one answer that is not a schema id. Spelled in `model_situation` -- which is
#: where the shortlist is built and where the product's own name for declining
#: lives -- and read here rather than respelled, because two words for "I will not
#: name one" is two vocabularies and the file that stays local depends on which one
#: a reader tested.
#:
#: THE WIRE WORD AND THE PRODUCT WORD ARE NOT THE SAME STRING, and this is the seam
#: that holds them together. The ratified prompt says `"none"` -- its rule 1: the
#: situation "must be copied character for character from `allowed_vocabulary`, or
#: be the word `none`" -- and the product's own name is `none_of_these`, which is
#: unambiguous in a column beside twenty-three schema ids. Both are accepted here
#: and both mean the same verdict, because a model that obeyed the ratified text
#: must not be refused for obeying it, and a caller reading the product's own
#: constant must not have to know the prompt's spelling.
_PROMPT_DECLINE_WORD: str = "none"

#: Named for `104` R-99's reason: the refusal address says which RULE the answer
#: broke, in the ratified template's own terms, while the reason code stays the
#: closed-vocabulary word it already was.
#:
#: Rule 1: *"`situation` must be copied character for character from
#: `allowed_vocabulary`, or be the word `none`. An identifier you compose is a
#: situation that does not exist."*
_NOT_IN_ALLOWED_VOCABULARY: str = "situation_not_in_allowed_vocabulary"
#: Rule 4: *"`alternatives` lists other identifiers from `allowed_vocabulary` that
#: the text also fits, or is empty. Nothing else goes in it."* Refused rather than
#: dropped: an alternative is a second reading of the same file, and a reader who
#: sees it silently removed cannot tell a model that named two situations from one
#: that named one.
_ALTERNATIVE_NOT_IN_VOCABULARY: str = "alternative_not_in_allowed_vocabulary"
#: The payload shape rule 1 rests on: there is a `situation` and it is a non-empty
#: string. `validate_response` checks the claim's envelope and not this site's
#: payload, so an answer with no situation at all would otherwise be accepted on
#: the strength of a citation that supports nothing named.
_SITUATION_MISSING: str = "payload_situation_missing"


def _payload_of(raw: object) -> Mapping[str, object]:
    if not isinstance(raw, Mapping):
        return {}
    payload = raw.get("payload")
    return payload if isinstance(payload, Mapping) else {}


def is_decline(situation: object, *, decline_word: str) -> bool:
    """Whether this answer is the model declining to name a situation.

    Two spellings, one meaning -- see `_PROMPT_DECLINE_WORD`. Published so the
    composition root asks the same question this validator answered rather than
    testing one of the two words and getting the other.
    """
    return situation in (decline_word, _PROMPT_DECLINE_WORD)


def _schema_invalid(verdict: P8Verdict, address: str) -> P8Verdict:
    """`SCHEMA_INVALID`, with the broken rule in the verdict's own address.

    Not `_make_verdict`, because the universal machinery has already built the
    verdict for this claim and its `citations_checked` are a real measurement of
    what the model cited. Throwing them away to rebuild the verdict would lose the
    only record of whether the answer was anchored at all, on a refusal that is
    about the ANSWER and not about the anchoring.
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


def _abstained(verdict: P8Verdict) -> P8Verdict:
    """A correct abstention, recorded as the success `00` says it is.

    `may_propose=False` and `UNRESOLVED` say the same thing the ABSTAIN branch of
    `validation._validate_claim` says for the `unknown` shape: nothing is written
    onto the file, and the file stays where the rules left it -- which for an
    unclassified file means it stays LOCAL. That is the safe direction, and it is
    the direction the prompt tells the model to take when the two are close.
    """
    return dataclasses.replace(
        verdict,
        outcome=ABSTAIN,
        disposition=UNRESOLVED,
        reasons=(),
        may_propose=False,
        requires_review=False,
    )


def _situation_site(dossier: Dossier, raw: object, verdict: P8Verdict):
    """The one thing this site checks beyond the universal citation rules.

    Returns a replacement verdict, or `None` to leave the universal one standing.
    """
    payload = _payload_of(raw)
    situation = payload.get("situation")
    if not isinstance(situation, str) or not situation:
        return _schema_invalid(verdict, f"situation:{_SITUATION_MISSING}")

    allowed = set(dossier.allowed_vocabulary)
    if is_decline(situation, decline_word=_decline_word_of(dossier)):
        return _abstained(verdict)
    if situation not in allowed:
        # THE INVENTION, CAUGHT AT THE ONE PLACE IT IS STILL LEGIBLE. Downstream
        # this is a string that either is or is not a `SCHEMA_IDS` member, and a
        # model that named a real schema nobody shortlisted would place files under
        # a situation the recognisers never raised for them.
        return _schema_invalid(
            verdict, f"situation:{_NOT_IN_ALLOWED_VOCABULARY}:{situation[:40]}")

    alternatives = payload.get("alternatives")
    if alternatives is None:
        alternatives = []
    if isinstance(alternatives, (str, bytes)) or not isinstance(
            alternatives, Sequence):
        return _schema_invalid(
            verdict, f"situation:{_ALTERNATIVE_NOT_IN_VOCABULARY}")
    for item in alternatives:
        if not isinstance(item, str) or item not in allowed:
            return _schema_invalid(
                verdict,
                f"situation:{_ALTERNATIVE_NOT_IN_VOCABULARY}:{str(item)[:40]}")
    return None


def _decline_word_of(dossier: Dossier) -> str:
    """The product's own decline word, read off the list the model was shown.

    The shortlist `model_situation.shortlist_for` builds ends with it, always, and
    `SituationQuestion` refuses a list that does not. Reading it from the dossier
    rather than importing `model_situation` keeps P8 free of a composition-root
    import and keeps this validator honest about one thing: the word it accepts is
    the word the model was actually offered, not the word this build believes in.
    """
    vocabulary = tuple(dossier.allowed_vocabulary)
    return vocabulary[-1] if vocabulary else _PROMPT_DECLINE_WORD


def validate_situation_response(
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
    """Site G's validator: the universal checks, plus "the answer is on the list".

    No `dependencies` argument, on site B's precedent: C, D and E take typed
    authority bundles because they need a frozen tree, a controlled action set or a
    fragment catalogue, and this site needs none of them. Everything it checks is
    already in the dossier -- the shortlist it showed the model and the evidence it
    released -- so a bundle here would be a slot a caller could fill with an
    acceptance callback, which is the shape `sites.py` exists to refuse.
    """
    return validate_response(
        dossier,
        response_bytes,
        evidence_resolver=evidence_resolver,
        site_validator=_situation_site,
        contradicts=contradicts,
        model_id=model_id,
        prompt_fingerprint=prompt_fingerprint,
        dossier_builder=dossier_builder,
        release_audit_id=release_audit_id,
        handle_key=handle_key,
    )


def situation_named_by(response_bytes: bytes, dossier: Dossier) -> str | None:
    """The situation the model named, or `None` for a decline or a bad shape.

    THE READER, and it decides nothing. `run_call` returns ONE verdict and a
    verdict carries an outcome, not an answer -- `cli._chosen_node_of` has the same
    shape at site C for the same reason. A caller applies this only after the
    verdict says the answer passed; reading it off a rejected response would apply
    an answer P8 refused.

    `None` is returned for every shape that is not one accepted answer, including
    the decline, because the caller's action for all of them is the same one:
    leave the file where the rules left it.
    """
    from llm_harness.validation import decode_response

    parsed, decode_ref = decode_response(response_bytes)
    if decode_ref is not None or not isinstance(parsed, Mapping):
        return None
    claims = parsed.get("claims")
    if not isinstance(claims, list) or len(claims) != 1:
        return None
    situation = _payload_of(claims[0]).get("situation")
    if not isinstance(situation, str) or not situation:
        return None
    if is_decline(situation, decline_word=_decline_word_of(dossier)):
        return None
    if situation not in set(dossier.allowed_vocabulary):
        return None
    return situation


__all__ = ["is_decline", "situation_named_by", "validate_situation_response"]
