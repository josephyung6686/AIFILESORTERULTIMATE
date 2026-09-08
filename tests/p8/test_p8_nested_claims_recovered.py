# tests/p8/test_p8_nested_claims_recovered.py
"""`104` R-162: the model closed the citation list late, and the answer was binned.

**The measurement, in `104`'s own words.** R-153 recorded the shape off r13:
*"the response is `claims: [{payload, citations: [{evidence_ref, cited_span,
why_it_supports}, {payload, citations: [...]}]}]` -- the model closed the citation
list one object late, twice, so the second and third claims sit where a citation
should. The first claim and its citation are well-formed and are thrown away with
the rest."* R-162 counted what that costs: **234 of r15's 619 site-A responses**
(38%; 28 of 56 fresh ones), every one `SCHEMA_INVALID claim-0:citation_malformed`,
and un-nested they hold 694 claims of which 141 responses carry at least one that
would be accepted. `104` §16.2: *"when the model does answer well, two of five
responses are thrown away for their bracket shape."*

**This is a parser change and not a validator change.** Every claim recovered here
goes through the same `sites.dispatch` the flat ones do, and is judged by the same
four checks over the same P6 world (`00`:42). Nothing below asserts a recovered
claim is accepted because it was recovered: one is accepted, one is rejected for
a value the cited text does not carry, one is rejected for citing a key that is
not in the dossier, and the response that carried them survives either way.

**AMBIGUITY IS A REFUSAL.** A member of a `citations` list is read as a claim only
when it carries no `evidence_ref` at all and does carry `payload` or `unknown`. An
object carrying both is two readings and stays refused; a citation sitting AFTER a
nested claim cannot be assigned to either claim and stays refused. Recovering an
answer the model did not clearly give would be inventing one, so those two shapes
keep the verdict they have today.

The nested shape is forbidden by the ratified `a_fact_response_schema.json` --
`citation` is `additionalProperties: false` and requires `evidence_ref` -- so
nothing the schema permits changes meaning here. What changes is the reading of a
shape the schema already forbids.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from llm_harness.vocabulary import (
    ABSTAIN,
    ACCEPT_DIRECT,
    CITATION_NOT_FOUND,
    REJECT,
    SCHEMA_INVALID,
    VALUE_NOT_IN_CITED_TEXT,
)

# The matrix's world, judge and shape builders. Imported rather than re-authored so
# that a recovered claim is measured by the same apparatus that measures a flat one
# and cannot drift from it. `conn`-backed fixtures are imported for pytest to find.
from p8.test_p8_a_fact_schema_failures import (  # noqa: F401
    RELEASED,
    World,
    _cite,
    _decline,
    _judge,
    _support,
    site_a_conn,
    world,
)

LIBRARY = Path(__file__).resolve().parents[2] / "src" / "llm_harness" / "library"
RESPONSE_SCHEMA = json.loads(
    (LIBRARY / "a_fact_response_schema.json").read_text(encoding="utf-8"))


# --- the shape r13 and r15 actually recorded --------------------------------------


def _term_claim(world: World) -> dict:
    """A second well-formed claim, about a second field of the same evidence."""
    return {"payload": {"field": "term", "value": "Spring 2026"},
            "citations": [{"evidence_ref": world.handle,
                           "cited_span": "Spring 2026",
                           "why_it_supports": "the heading names the term"}]}


def _nested_once(world: World) -> dict:
    """R-153's shape: claim 2 sits in claim 1's citation list, after the citation."""
    return {"claims": [{
        "payload": {"field": "subject", "value": "PHYS 1401"},
        "citations": [_cite(world), _term_claim(world)],
    }]}


def _nested_twice(world: World) -> dict:
    """R-153's *"one object late, twice"*: claim 3 inside claim 2 inside claim 1."""
    inner = _decline()
    middle = _term_claim(world)
    middle["citations"] = [middle["citations"][0], inner]
    return {"claims": [{
        "payload": {"field": "subject", "value": "PHYS 1401"},
        "citations": [_cite(world), middle],
    }]}


def test_the_shape_recovered_here_is_the_one_the_run_recorded(world):
    """The premise, asserted against `104` R-153's sentence rather than assumed.

    One top-level claim; its `citations[0]` is a citation; its `citations[1]` is an
    object with `payload` and `citations` and no `evidence_ref`. If a future edit to
    the builders above stops producing that, every assertion below is measuring
    something the run never sent.
    """
    body = _nested_once(world)
    assert len(body["claims"]) == 1
    citations = body["claims"][0]["citations"]
    assert set(citations[0]) == {"evidence_ref", "cited_span", "why_it_supports"}
    assert "evidence_ref" not in citations[1]
    assert set(citations[1]) == {"payload", "citations"}


def test_the_ratified_schema_forbids_the_nested_object(world):
    """Nothing the ratified schema permits is being re-read as something else.

    `citation` is a closed object requiring `evidence_ref`, so the member this file
    recovers is a shape the schema already refuses. The recovery reads a
    schema-illegal object as the claim it plainly is; it does not widen `citation`.
    """
    citation = RESPONSE_SCHEMA["$defs"]["citation"]
    assert citation["additionalProperties"] is False
    assert "evidence_ref" in citation["required"]
    assert "payload" not in citation["properties"]


# --- what the product does with it ------------------------------------------------


def test_a_nested_second_claim_is_read_and_both_claims_are_judged(world):
    """The 234. Two claims went out; two verdicts come back, in the order sent.

    Today this whole response is one REJECT, `claim-0:citation_malformed`, and the
    well-formed first claim dies with it.
    """
    assert _judge(world, _nested_once(world)) == (
        (ACCEPT_DIRECT, (), "subject"),
        (ACCEPT_DIRECT, (), "term"),
    )


def test_two_levels_of_nesting_are_read_and_all_three_claims_are_judged(world):
    """*"one object late, twice"* -- the support, the support, and the decline."""
    assert _judge(world, _nested_twice(world)) == (
        (ACCEPT_DIRECT, (), "subject"),
        (ACCEPT_DIRECT, (), "term"),
        (ABSTAIN, (), "school"),
    )


def test_the_flat_response_and_the_nested_one_are_judged_identically(world):
    """The faithfulness test: same claims, same brackets or wrong brackets, same
    verdicts. If the two ever differ, the recovery is doing something other than
    moving a claim out of a list it was never a member of.
    """
    flat = {"claims": [_support(world), _term_claim(world)]}
    assert _judge(world, flat) == _judge(world, _nested_once(world))


def test_the_host_claim_keeps_only_the_citations_it_really_made(world):
    """A claim whose citation list held ONLY a nested claim cited nothing.

    The recovery does not hand the host a citation to make it survive. Site A's
    own word for a supporting claim with no citation is `CITATION_NOT_FOUND`
    (`fact_validation`, check two: *"a key that is not a P6 observation at all fails
    the coarse check"*, and no key at all is the same coarse failure), and that is
    what the host gets -- which is what its bytes say. The nested claim is judged on
    its own and the response lives.
    """
    body = {"claims": [{
        "payload": {"field": "subject", "value": "PHYS 1401"},
        "citations": [_term_claim(world)],
    }]}
    assert _judge(world, body) == (
        (REJECT, (CITATION_NOT_FOUND,), "subject"),
        (ACCEPT_DIRECT, (), "term"),
    )


def test_a_recovered_claim_still_faces_every_check(world):
    """No claim is accepted for having been un-nested. `00`:42's four checks run.

    The nested claim below cites a real span of the released value and proposes a
    value that span does not carry, which is `llm_harness.value_grounding`'s case.
    """
    bad = {"payload": {"field": "term", "value": "Autumn 2019"},
           "citations": [{"evidence_ref": world.handle,
                          "cited_span": "PHYS 1401",
                          "why_it_supports": "the heading names it"}]}
    body = {"claims": [{
        "payload": {"field": "subject", "value": "PHYS 1401"},
        "citations": [_cite(world), bad],
    }]}
    assert _judge(world, body) == (
        (ACCEPT_DIRECT, (), "subject"),
        (REJECT, (VALUE_NOT_IN_CITED_TEXT,), "term"),
    )


def test_two_claims_about_one_field_still_destroy_the_response(world):
    """Rule 8 is the validator's and the recovery does not soften it.

    Un-nested, these are two claims about `subject`, and P8 does not choose which
    of the model's two answers it meant.
    """
    body = {"claims": [{
        "payload": {"field": "subject", "value": "PHYS 1401"},
        "citations": [_cite(world), _support(world)],
    }]}
    assert _judge(world, body) == (
        (REJECT, (SCHEMA_INVALID,), "claims:duplicate_field:subject"),)


# --- ambiguity is a refusal -------------------------------------------------------


def test_an_object_that_is_both_a_citation_and_a_claim_stays_refused(world):
    """Two readings, so no reading. The address says which shape was ambiguous."""
    both = dict(_cite(world))
    both["payload"] = {"field": "term", "value": "Spring 2026"}
    body = {"claims": [{
        "payload": {"field": "subject", "value": "PHYS 1401"},
        "citations": [both],
    }]}
    assert _judge(world, body) == (
        (REJECT, (SCHEMA_INVALID,), "claim-0:citation_or_claim_ambiguous"),)


def test_a_citation_after_a_nested_claim_stays_refused(world):
    """It belongs to the host or to the nested claim and the bytes do not say.

    Assigning it to either would be inventing a citation the model did not make,
    so the response keeps the refusal it has today.
    """
    body = {"claims": [{
        "payload": {"field": "subject", "value": "PHYS 1401"},
        "citations": [_cite(world), _term_claim(world), _cite(world)],
    }]}
    assert _judge(world, body) == (
        (REJECT, (SCHEMA_INVALID,), "claim-0:citation_after_nested_claim"),)


def test_an_ambiguous_object_deeper_in_the_nest_refuses_the_whole_response(world):
    """The refusal is not skipped because the outer levels read cleanly."""
    both = dict(_cite(world))
    both["unknown"] = {"insufficiency_statement": "s"}
    middle = _term_claim(world)
    middle["citations"] = [middle["citations"][0], both]
    body = {"claims": [{
        "payload": {"field": "subject", "value": "PHYS 1401"},
        "citations": [_cite(world), middle],
    }]}
    assert _judge(world, body) == (
        (REJECT, (SCHEMA_INVALID,), "claim-0:citation_or_claim_ambiguous"),)


@pytest.mark.parametrize(
    ("case", "member"),
    [
        ("a bare reference", "@handle"),
        ("neither span nor metadata field",
         {"evidence_ref": "@handle", "why_it_supports": "w"}),
        ("both span and metadata field",
         {"evidence_ref": "@handle", "cited_span": "PHYS 1401",
          "metadata_field_name": "heading:course", "why_it_supports": "w"}),
        ("an empty evidence_ref",
         {"evidence_ref": "", "cited_span": "PHYS 1401", "why_it_supports": "w"}),
        ("no why_it_supports",
         {"evidence_ref": "@handle", "cited_span": "PHYS 1401"}),
        ("an object that is neither", {"note": "I could not find one"}),
    ],
)
def test_a_malformed_citation_is_still_a_malformed_citation(world, case, member):
    """The matrix rows of `test_p8_a_fact_schema_failures` do not move.

    None of these carries `payload` or `unknown`, so none of them is a claim in the
    wrong brackets, and each keeps `claim-0:citation_malformed`. A recovery that
    swallowed these would be reading refusals as answers.
    """
    resolved = copy.deepcopy(member)
    if resolved == "@handle":
        resolved = world.handle
    elif isinstance(resolved, dict) and resolved.get("evidence_ref") == "@handle":
        resolved["evidence_ref"] = world.handle
    body = {"claims": [{
        "payload": {"field": "subject", "value": "PHYS 1401"},
        "citations": [resolved],
    }]}
    assert _judge(world, body) == (
        (REJECT, (SCHEMA_INVALID,), "claim-0:citation_malformed"),)


# --- the fixture set, and how each recovery is known to be faithful ---------------


def _flat(*claims: dict) -> dict:
    return {"claims": list(claims)}


def _nested_deeper(world: World) -> tuple[dict, dict]:
    """Three claims, the third nested inside the second inside the first."""
    return _nested_twice(world), _flat(
        _support(world), _term_claim(world), _decline())


def _nested_decline(world: World) -> tuple[dict, dict]:
    """A DECLINING claim in the wrong brackets: `unknown`, no citations of its own."""
    return {"claims": [{
        "payload": {"field": "subject", "value": "PHYS 1401"},
        "citations": [_cite(world), _decline()],
    }]}, _flat(_support(world), _decline())


def _nested_after_two_citations(world: World) -> tuple[dict, dict]:
    """The list closed late after a second real citation, not only after the first."""
    metadata = {"evidence_ref": world.handle,
                "metadata_field_name": "heading:course",
                "why_it_supports": "the address names the heading"}
    host = {"payload": {"field": "subject", "value": "PHYS 1401"},
            "citations": [_cite(world), metadata, _term_claim(world)]}
    flat_host = {"payload": {"field": "subject", "value": "PHYS 1401"},
                 "citations": [_cite(world), metadata]}
    return {"claims": [host]}, _flat(flat_host, _term_claim(world))


def _nested_beside_a_flat_claim(world: World) -> tuple[dict, dict]:
    """The model closed one list late and then wrote a third claim flat."""
    return {"claims": [
        {"payload": {"field": "subject", "value": "PHYS 1401"},
         "citations": [_cite(world), _term_claim(world)]},
        _decline(),
    ]}, _flat(_support(world), _term_claim(world), _decline())


def _nested_in_the_second_claim(world: World) -> tuple[dict, dict]:
    """The first claim is flat and the SECOND one closed its list late."""
    return {"claims": [
        _support(world),
        {"payload": {"field": "term", "value": "Spring 2026"},
         "citations": [_term_claim(world)["citations"][0], _decline()]},
    ]}, _flat(_support(world), _term_claim(world), _decline())


#: EVERY NESTED SHAPE THIS FILE RECOVERS, each with the FLAT response carrying the
#: same claims in the same order. `104` R-162 counted the shape and not its variants,
#: so the set is the recorded shape (`_nested_once`, `_nested_deeper`) plus the ways
#: one response can carry it that the recorded shape does not settle: a declining
#: claim in the wrong brackets, a list closed late after two citations, a nested
#: claim beside a flat one, and the nesting starting at the second claim.
RECOVERED: tuple[tuple[str, object], ...] = (
    ("the recorded shape",
     lambda w: (_nested_once(w), _flat(_support(w), _term_claim(w)))),
    ("one object late, twice", _nested_deeper),
    ("a declining claim in the wrong brackets", _nested_decline),
    ("the list closed late after two citations", _nested_after_two_citations),
    ("a nested claim beside a flat one", _nested_beside_a_flat_claim),
    ("the nesting starts at the second claim", _nested_in_the_second_claim),
)


@pytest.mark.parametrize(
    ("case", "build"), RECOVERED, ids=[name for name, _b in RECOVERED])
def test_a_recovered_response_is_judged_as_its_flat_twin_is(world, case, build):
    """**How each recovery is known to be faithful.**

    Not "the response was accepted" -- that would only say the parser is permissive.
    The property is that the nested response and the FLAT response carrying the same
    claims in the same order produce the identical verdicts, in the identical order,
    with the identical reasons. A recovery that added a claim, dropped one, reordered
    them, handed a host a citation it did not make, or softened a check would break
    this equality for one of the six.
    """
    nested, flat = build(world)
    assert _judge(world, nested) == _judge(world, flat)
    assert _judge(world, flat) != ()


def test_the_fixture_set_recovers_every_response_and_loses_no_claim(world):
    """The count, on the fixture set: 6 responses recovered, 15 claims judged.

    Today all six are one `SCHEMA_INVALID claim-0:citation_malformed` verdict each
    and nothing in them is judged -- six responses in, six verdicts out, no claim
    read. `104` R-162's corpus figure is the same arithmetic at scale: 234 responses
    discarded, 694 claims inside them.
    """
    verdicts = [_judge(world, build(world)[0]) for _name, build in RECOVERED]
    assert len(verdicts) == 6
    assert [len(item) for item in verdicts] == [2, 3, 2, 2, 3, 3]
    assert sum(len(item) for item in verdicts) == 15
    assert not any(
        reason == SCHEMA_INVALID
        for item in verdicts for _outcome, reasons, _ref in item
        for reason in reasons)


#: THE SHAPES THAT STAY REFUSED. Each has two readings, and the address says which.
REFUSED: tuple[tuple[str, str], ...] = (
    ("a citation that is also a claim", "claim-0:citation_or_claim_ambiguous"),
    ("a citation after a nested claim", "claim-0:citation_after_nested_claim"),
)


def test_the_refused_shapes_are_still_refused_and_named(world):
    """Ambiguity is a refusal, and the record says which ambiguity it was."""
    both = dict(_cite(world))
    both["payload"] = {"field": "term", "value": "Spring 2026"}
    bodies = (
        {"claims": [{"payload": {"field": "subject", "value": "PHYS 1401"},
                     "citations": [both]}]},
        {"claims": [{"payload": {"field": "subject", "value": "PHYS 1401"},
                     "citations": [_cite(world), _term_claim(world),
                                   _cite(world)]}]},
    )
    assert tuple(
        (name, _judge(world, body))
        for (name, _address), body in zip(REFUSED, bodies, strict=True)
    ) == tuple(
        (name, ((REJECT, (SCHEMA_INVALID,), address),))
        for name, address in REFUSED
    )
