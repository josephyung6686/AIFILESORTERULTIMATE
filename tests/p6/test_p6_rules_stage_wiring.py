# tests/p6/test_p6_rules_stage_wiring.py
"""§3.5's context check, composed as `FactResolver`'s `rule` stage. NOT YET SHIPPED.

`src/cli.py`'s `_resolver` binds `stages={"direct": ..., "rule": None, "llm": None}`,
and its docstring calls that a decision: "This deployment ships no authored rule set
and no model route." It was the right decision while no rule set existed. What it
costs is measurable, and it was measured on a real three-file corpus:

    invoice.txt | subject = INV20261        reliability_state = direct

An invoice number became a `subject` fact -- the field folders are named after -- with
no academic context anywhere near it. §3.5's worked requirement is the one thing that
would have refused it: "BUSIB 4300 becomes a course fact only when the engine finds a
course-code pattern together with academic context such as 'syllabus,' 'lecture,'
'credits,' 'instructor,' or 'semester.'" Done-means 8 states both halves, and only the
negative half is reachable today, from a producer that is never run.

THIS FILE PROVES THE COMPOSITION, NOT THE RULE. `tests/p6/test_p6_rules.py` already
drives `apply_rules` and covers the check itself. What was never tested is that
`apply_rules` FITS: that binding it as the `rule` stage of the resolver this command
builds produces §3.5's two outcomes over one file's real observations. It does, and it
needs no change to `facts.rules` -- `apply_rules` already has the `Stage` shape once a
caller binds `rules` and `screen`, which is what the `src/cli.py` patch does.

WHAT IS STILL THE DEPLOYMENT'S. The pattern is not P6's to author (§3.10's catalogue
beyond the three named date patterns is Deferred and a course-code pattern is not
among them), so the regex below is this TEST's, exactly as it would be `src/cli.py`'s.
`facts.rules` authors the five context terms §3.5 states literally and nothing else.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file

from evidence_shape.location import Location, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run

from facts.discount import MetadataScreen
from facts.file_facts import facts_for_file
from facts.resolver import FactResolver
from facts.rules import ACADEMIC_CONTEXT_TERMS, Rule, apply_rules
from facts.states import VALIDATED
from facts.unresolved import unresolved_for_file
from facts.usable import record_pass

CLOCK = "2026-08-19T12:00:00+00:00"
NO_CATALOGUE = MetadataScreen(tool_producer_strings=(), metadata_property_names=())

#: `src/cli.py:_STRUCTURED`, verbatim. The deployment's identifier pattern, reused
#: rather than reinvented so this test asks the question the shipped command would.
IDENTIFIER = re.compile(r"\b[A-Z][A-Z0-9]*[ -]?[0-9]{3,}\b")

SUBJECT_RULE = Rule(pattern=IDENTIFIER,
                    required_context_terms=ACADEMIC_CONTEXT_TERMS,
                    field_key="subject")


def _file(conn, tmp_path, *, name, body):
    path = tmp_path / name
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="text/plain",
        detected_format="txt", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, before, after):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="text.plain", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    record_observation(conn, Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="text.plain",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location("body", (), TextSpan(0, len(raw))), occurrence_count=1,
        observed_at=CLOCK, reliability="direct", run_id=run_id,
        context_before=before, context_after=after))


def _resolver_with_the_rule_stage():
    """`src/cli.py:_resolver`, with `rule` bound instead of `None`.

    Every other argument is that function's, unchanged, so the only difference
    between this composition and the shipped one is the line the patch changes.
    """
    def rule_stage(conn, file_id, content_hash):
        return apply_rules(conn, file_id=file_id, content_hash=content_hash,
                           rules=(SUBJECT_RULE,), screen=NO_CATALOGUE)

    return FactResolver(
        stages={"direct": None, "rule": rule_stage, "llm": None},
        pending_fields=lambda conn, file_id, content_hash: (),
        budget_exhausted=lambda ceiling: False,
        model_route_permitted=lambda file_id: False,
        record_pass=lambda conn, file_id, content_hash: record_pass(
            conn, file_id=file_id, content_hash=content_hash,
            analysis_tiers=frozenset(("filesystem", "native"))),
        cache_key_for=lambda file_id, content_hash: f"test-rule:{content_hash}",
        screen_metadata=lambda conn, file_id, content_hash: ())


def test_an_invoice_number_does_not_become_a_subject_when_the_rule_stage_runs(
        p6_conn, tmp_path):
    """Done-means 8's negative half, in composition. THE MEASURED DEFECT.

    On the shipped command this file yields `subject = INV20261`, `direct`, and a
    folder is proposed from it.
    """
    file_id, content_hash = _file(p6_conn, tmp_path, name="invoice.txt",
                                  body=b"Invoice INV20261 from Northside Plumbing.")
    _observe(p6_conn, run_id="run-invoice", file_id=file_id,
             content_hash=content_hash, raw="INV20261",
             before="Invoice ", after=" from Northside Plumbing.")

    result = _resolver_with_the_rule_stage().resolve(
        p6_conn, file_id=file_id, content_hash=content_hash)

    assert result.fact_ids == ()
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    # And the refusal is RECORDED, with the reason §3.5 gives it -- not silence.
    assert [row["reason"] for row in
            unresolved_for_file(p6_conn, file_id, content_hash)] == [
                "context_check_failed"]


def test_the_same_shape_with_academic_context_does_become_a_subject(p6_conn,
                                                                    tmp_path):
    """Done-means 8's positive half, which is unreachable in the shipped command.

    P4's skeleton fixture 1 carries `context_before: "Syllabus - "` with a capital S,
    and N-6 makes the §3.5 check case-insensitive precisely so that fixture resolves.
    """
    file_id, content_hash = _file(p6_conn, tmp_path, name="syllabus.txt",
                                  body=b"PHYS1401 syllabus")
    _observe(p6_conn, run_id="run-syllabus", file_id=file_id,
             content_hash=content_hash, raw="PHYS1401",
             before="Syllabus - ", after=" Introductory Physics")

    result = _resolver_with_the_rule_stage().resolve(
        p6_conn, file_id=file_id, content_hash=content_hash)

    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert [(row["field_key"], row["canonical_value"], row["reliability_state"])
            for row in rows] == [("subject", "PHYS1401", VALIDATED)]
    assert len(result.fact_ids) == 1


def test_the_rule_stage_is_the_only_change_the_deployment_needs(p6_conn, tmp_path):
    """`apply_rules` already has the `Stage` shape. Nothing in `facts.rules` moves.

    This is the claim the `src/cli.py` patch rests on, so it is asserted rather than
    assumed: bind two things the caller owns and the result is `(conn, file_id,
    content_hash) -> tuple[str, ...]`, which is exactly what `FactResolver` calls.
    """
    import inspect

    parameters = inspect.signature(apply_rules).parameters
    assert list(parameters) == ["conn", "file_id", "content_hash", "rules", "screen"]
    for name in ("rules", "screen"):
        assert parameters[name].default is inspect.Parameter.empty, (
            f"{name} has a default; §3.5's catalogue is the deployment's and a "
            "default here would let a run ship with a rule set nobody chose")


def test_p6_authors_the_five_context_terms_and_no_pattern(p6_conn):
    # The division the patch depends on: the terms are §3.5's, quoted; the pattern is
    # the deployment's. A course-code regex inside `facts` would be P6 authoring a
    # catalogue the SPEC defers.
    assert ACADEMIC_CONTEXT_TERMS == (
        "syllabus", "lecture", "credits", "instructor", "semester")
    import facts.rules as rules_module
    assert not [value for value in vars(rules_module).values()
                if isinstance(value, re.Pattern)]


# --- WHAT THE CHECK REFUSES THAT IT SHOULD NOT ------------------------------------
#
# The defect this stage fixes is visible: a wrong folder, named after an invoice
# number. The defect it can CAUSE is not. A real course code whose file happens not
# to say any of §3.5's five words produces no `subject` fact at all, and a fact that
# never appears is far harder for a person to notice than a wrong folder they can
# see. So the false negatives are written down here as tests rather than left to be
# discovered, and each one says whether the answer is right.


def test_a_real_course_file_that_says_none_of_the_five_words_is_refused(p6_conn,
                                                                       tmp_path):
    """THE FALSE NEGATIVE, and it is a real file rather than a contrived one.

    "Course outline", "Professor", "Assignments", "Grading", "Office hours" -- the
    vocabulary of an actual syllabus, and not one of §3.5's five. The check refuses
    it, and `PHYS1401` gets no `subject` fact.

    IS THAT THE RIGHT ANSWER? For the rule in isolation, yes: §3.5's five terms are
    quoted from the design and a sixth is a design change, not an implementation
    detail. What makes it SAFE is that the refusal is recorded rather than silent --
    the `unresolved` row below is what a person can be shown -- and what makes it
    survivable today is that the direct slot still claims this reading, so binding
    the rule stage takes nothing away. Both halves matter; see the test below.
    """
    file_id, content_hash = _file(p6_conn, tmp_path, name="outline.txt",
                                  body=b"PHYS1401 course outline")
    _observe(p6_conn, run_id="run-outline", file_id=file_id,
             content_hash=content_hash, raw="PHYS1401",
             before="Course outline for ",
             after=". Professor Ramirez. Assignments, grading, office hours.")

    _resolver_with_the_rule_stage().resolve(
        p6_conn, file_id=file_id, content_hash=content_hash)

    assert facts_for_file(p6_conn, file_id, content_hash) == []
    # RECORDED, not silent. §8.5 asks "did it abstain when evidence was absent?" and
    # this is the row that answers it for a person who wonders where their course
    # went.
    rows = unresolved_for_file(p6_conn, file_id, content_hash)
    assert [(row["field_key"], row["reason"]) for row in rows] == [
        ("subject", "context_check_failed")]


def test_binding_the_rule_stage_takes_no_course_fact_away(p6_conn, tmp_path):
    """The patch is ADDITIVE, and this is the test that says so.

    `src/cli.py` binds `cli.text.identifier` as a DIRECT slot over the same pattern.
    With both stages bound, the file above still gets its `subject` -- from the slot,
    which asks no context question -- and gains an `unresolved` row saying the rule
    could not confirm it. Nothing a person sees today disappears.

    Which is also the patch's limit, stated honestly: `INV20261` still becomes a
    `subject` fact, because the slot still claims it. Binding the rule stage alone
    adds records and changes no proposal. The invoice defect is fixed by NARROWING
    THE SLOT, which is the second, riskier half of the decision.
    """
    from facts.direct import DirectSlot, DirectSlots, direct_facts
    from facts.states import DIRECT

    slot = DirectSlot(slot_id="cli.text.identifier", field_key="subject",
                      names=lambda locator: locator.startswith("body#"),
                      canonical=lambda raw: "".join(raw.split()))

    def direct_stage(conn, file_id, content_hash):
        return direct_facts(conn, file_id=file_id, content_hash=content_hash,
                            slots=DirectSlots(slots=(slot,)), screen=NO_CATALOGUE)

    def rule_stage(conn, file_id, content_hash):
        return apply_rules(conn, file_id=file_id, content_hash=content_hash,
                           rules=(SUBJECT_RULE,), screen=NO_CATALOGUE)

    resolver = FactResolver(
        stages={"direct": direct_stage, "rule": rule_stage, "llm": None},
        pending_fields=lambda conn, file_id, content_hash: (),
        budget_exhausted=lambda ceiling: False,
        model_route_permitted=lambda file_id: False,
        record_pass=lambda conn, file_id, content_hash: record_pass(
            conn, file_id=file_id, content_hash=content_hash,
            analysis_tiers=frozenset(("filesystem", "native"))),
        cache_key_for=lambda file_id, content_hash: f"test-both:{content_hash}",
        screen_metadata=lambda conn, file_id, content_hash: ())

    file_id, content_hash = _file(p6_conn, tmp_path, name="outline.txt",
                                  body=b"PHYS1401 course outline")
    _observe(p6_conn, run_id="run-both", file_id=file_id,
             content_hash=content_hash, raw="PHYS1401",
             before="Course outline for ",
             after=". Professor Ramirez. Assignments, grading, office hours.")

    resolver.resolve(p6_conn, file_id=file_id, content_hash=content_hash)

    # The course fact survives, from the slot.
    assert [(row["field_key"], row["canonical_value"], row["reliability_state"])
            for row in facts_for_file(p6_conn, file_id, content_hash)] == [
                ("subject", "PHYS1401", DIRECT)]
    # And the rule's disagreement is on the record beside it.
    assert [row["reason"] for row in
            unresolved_for_file(p6_conn, file_id, content_hash)] == [
                "context_check_failed"]


def test_a_cut_off_context_is_not_reported_as_a_considered_refusal(p6_conn,
                                                                   tmp_path):
    """§8.6 forbids silent truncation, and this is the case that matters most here.

    `src/cli.py` sets `context_window=240` characters. A course code far from the
    word "syllabus" in a long document has a context P4 flagged as CUT, and the
    engine cannot say whether the term was there. Reporting `context_check_failed`
    would claim a refusal it never made; `context_truncated` says what happened.

    This is the honest half of the false-negative story: the fact is still absent,
    but the record distinguishes "we looked and it was not there" from "we could not
    see far enough to look".
    """
    file_id, content_hash = _file(p6_conn, tmp_path, name="long.txt",
                                  body=b"PHYS1401 buried in a long document")
    record_run(p6_conn, ExtractionRun(
        run_id="run-cut", file_id=file_id, content_hash=content_hash,
        extractor_name="text.plain", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    record_observation(p6_conn, Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="text.plain",
        extractor_version="1.0.0", source_type="text_document",
        raw_value="PHYS1401",
        location=Location("body", (), TextSpan(0, 8)), occurrence_count=1,
        observed_at=CLOCK, reliability="direct", run_id="run-cut",
        context_before="... a great deal of text before ",
        context_after=" and a great deal after ...",
        context_truncated=True))

    _resolver_with_the_rule_stage().resolve(
        p6_conn, file_id=file_id, content_hash=content_hash)

    assert [row["reason"] for row in
            unresolved_for_file(p6_conn, file_id, content_hash)] == [
                "context_truncated"]


# --- THE BLOCKER, FOUND END TO END AND NOT BY ANY UNIT TEST -----------------------
#
# Every test above passed with the rule stage bound, and the real command then got
# WORSE: the PHYS1401 folder vanished and all four course files went unplaced.
#
#   PHYS 1401 homework 3.txt   PHYS1401    direct     deterministic_extractor
#   PHYS 1401 homework 3.txt   PHYS 1401   validated  rule
#
# `DirectSlot` carries a `canonical` callable and `Rule` does not, so `apply_rules`
# stores `match.group(0)` verbatim. The deployment's slot canonicalises `PHYS 1401`
# to `PHYS1401`; the rule kept the space. One course arrived as two values, which is
# `65` §4.2's recorded failure -- "four files of one course became four one-file
# groups because one identity arrived as several spellings" -- reproduced exactly.
#
# The tests above did not catch it because they fed `PHYS1401` with no separator.
# The corpus has `PHYS 1401`, because that is how people write it.


def test_a_rule_can_canonicalise_its_match_the_way_a_slot_can(p6_conn, tmp_path):
    """The fix, and it is `DirectSlot`'s own shape rather than a new idea.

    `canonical` is the CALLER'S, for the reason `DirectSlot.canonical` already
    gives: round 4's C-5 records that `normalize(field, raw_value)` is claimed by
    P8's Contract-in and disowned by P6's Task 17, so no part builds it. P6 gains no
    opinion about what a course code looks like; it gains only the ability to be
    told, which is the difference between a rule that can ship and one that cannot.
    """
    import re

    separator = re.compile(r"(?<=[A-Z])[ -](?=[0-9])")   # `src/cli.py:_SEPARATOR`
    rule = Rule(pattern=IDENTIFIER,
                required_context_terms=ACADEMIC_CONTEXT_TERMS,
                field_key="subject",
                canonical=lambda raw: separator.sub("", " ".join(raw.split())))

    file_id, content_hash = _file(p6_conn, tmp_path, name="syllabus.txt",
                                  body=b"PHYS 1401 syllabus")
    _observe(p6_conn, run_id="run-spaced", file_id=file_id,
             content_hash=content_hash, raw="PHYS 1401",
             before="Syllabus - ", after=" Introductory Physics")

    from facts.rules import apply_rules as run_rules
    run_rules(p6_conn, file_id=file_id, content_hash=content_hash,
              rules=(rule,), screen=NO_CATALOGUE)

    assert [row["canonical_value"] for row in
            facts_for_file(p6_conn, file_id, content_hash)] == ["PHYS1401"]


def test_a_rule_with_no_canonicaliser_still_stores_the_match_verbatim(p6_conn,
                                                                      tmp_path):
    """The default is today's behaviour exactly, so nothing already written moves.

    `canonical=None` means "the match is the value", which is what `apply_rules` has
    always done. The parameter adds a capability; it changes no existing caller.
    """
    file_id, content_hash = _file(p6_conn, tmp_path, name="syllabus.txt",
                                  body=b"PHYS 1401 syllabus")
    _observe(p6_conn, run_id="run-plain", file_id=file_id,
             content_hash=content_hash, raw="PHYS 1401",
             before="Syllabus - ", after=" Introductory Physics")

    from facts.rules import apply_rules as run_rules
    run_rules(p6_conn, file_id=file_id, content_hash=content_hash,
              rules=(SUBJECT_RULE,), screen=NO_CATALOGUE)

    assert [row["canonical_value"] for row in
            facts_for_file(p6_conn, file_id, content_hash)] == ["PHYS 1401"]


def test_the_rule_and_the_slot_reach_one_value_when_both_are_bound(p6_conn,
                                                                   tmp_path):
    """THE REGRESSION TEST for the folder that disappeared.

    Both producers bound, a course code written the way people write it, and one
    value at the end. Without the canonicaliser this is two.
    """
    import re

    from facts.direct import DirectSlot, DirectSlots, direct_facts
    from facts.values import values_in_field

    separator = re.compile(r"(?<=[A-Z])[ -](?=[0-9])")
    canonical = lambda raw: separator.sub("", " ".join(raw.split()))

    slot = DirectSlot(slot_id="cli.text.identifier", field_key="subject",
                      names=lambda locator: locator.startswith("body#"),
                      canonical=canonical)
    rule = Rule(pattern=IDENTIFIER,
                required_context_terms=ACADEMIC_CONTEXT_TERMS,
                field_key="subject", canonical=canonical)

    file_id, content_hash = _file(p6_conn, tmp_path, name="syllabus.txt",
                                  body=b"PHYS 1401 syllabus")
    _observe(p6_conn, run_id="run-both-spaced", file_id=file_id,
             content_hash=content_hash, raw="PHYS 1401",
             before="Syllabus - ", after=" Introductory Physics")

    direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                 slots=DirectSlots(slots=(slot,)), screen=NO_CATALOGUE)
    from facts.rules import apply_rules as run_rules
    run_rules(p6_conn, file_id=file_id, content_hash=content_hash,
              rules=(rule,), screen=NO_CATALOGUE)

    assert [value["canonical_value"] for value in
            values_in_field(p6_conn, "subject")] == ["PHYS1401"]
