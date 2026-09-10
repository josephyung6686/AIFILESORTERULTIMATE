# tests/integration/test_a_file_that_is_never_asked_is_named.py
"""`104` §18.2 gaps 4 and 5 -- the two silences a person could not see through.

**Gap 4.** `model_facts.fact_call_stage` returns before building a call in four
states, and until 9 Sep 2026 all four returned a bare `()`: no call, no `unresolved`
row, and `FactResolver` then appending `llm` to `stages_run` because it recorded that
the stage had been INVOKED. So the run's report counted the file as one a model had
been asked about and had had nothing to say -- about a file nothing about which was
ever assembled, let alone sent. §13.1's bar and the constitution's second rule say the
opposite in the same words: what is skipped is counted and NAMED.

**Gap 5.** The dossier ceiling drops the readings that do not fit and did it with a
bare `continue`, so a file that offered forty readings and carried four produced the
same record as a file whose whole evidence reached the model. `00`:257: a prompt over
its budget "should not truncate silently in a way that removes the decisive evidence."

**What this file drives, and what it deliberately does not.** These are seams across
three modules -- the stage decides, the resolver records, the screen prints -- and a
test of any one of them alone would pass while the sentence a person reads stayed
wrong. So the stage is driven against a real corpus with real classification records
and a real `FactCallAuthorities`, and the screen is driven against real stored
`GroundingReport` rows. No model is reached: every state under test is one the stage
returns from before a client is touched, and the cut is recorded by the BUILDER
before any call goes out.

The ladder's own arithmetic -- which rung a trimmed dossier earns, and that the
deferred set is unchanged -- is in
`tests/integration/test_cli_dossier_ceiling_is_measured.py`, beside the other
measurements of the same ceiling.
"""
from __future__ import annotations

import io
import json

import pytest

import cli
from privacy.vocabulary import CLOUD_LOCALITY
import model_facts
from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run, record_text_unit
from evidence_shape.text_units import TextUnit
from facts.resolver import StageOutcome
from facts.unresolved import (
    NO_CANDIDATE_EVIDENCE, PRIVACY_WITHHELD, unresolved_for_file,
)
from llm_harness.transport import ModelClient
from llm_harness.vocabulary import A_FACT
from model_facts import fact_call_stage
from privacy.release import ModelTarget
from readers.model_ollama import LOCAL, PROVIDER as LOCAL_PROVIDER
from readers.model_routing import FAST, LOGIC, REASONING, TierRouting

SITUATION = "academic.coursework"
CLOCK = "2026-09-09T00:00:00Z"

#: THE ZONE NO TARGET MAY BE SHOWN, which is what makes a file whose only readings
#: sit in it the "everything was refused" state. `104` §17.13 opened `path` and `ocr`
#: to both targets, so those two no longer refuse anything;
#: `privacy.vocabulary.ALWAYS_LOCAL_ZONES_FOR_EVERY_TARGET` keeps `filename` closed on
#: every locality, and `releasable_observations` drops it a step earlier so the call
#: is never built rather than built and denied. A file whose extractors found nothing
#: but its own name is the ordinary shape of this: the name is recorded for every
#: indexed file, and it reaches a model as a `Filename` item through its own door or
#: not at all.
A_NAME = "PHYS 1401 homework 3.pdf"


def _local_routing() -> TierRouting:
    one = ModelClient(
        model_target=ModelTarget(locality=LOCAL, model_id="qwen3:8b",
                                 provider=LOCAL_PROVIDER, context_tokens=32768),
        # Nothing here reaches it. Every state under test returns before a client is
        # invoked, and a transport would be a dependency bought for nothing.
        invoke=lambda payload: b'{"claims": []}')
    return TierRouting(tier_of_call_site=cli.TIER_OF_CALL_SITE,
                       client_of_tier={tier: one
                                       for tier in (REASONING, LOGIC, FAST)})


def _cloud_only_routing() -> TierRouting:
    """A run with a cloud destination and no local one (`104` §18.7's other half):
    the target a protected file is refused, with nothing to fall to."""
    one = ModelClient(
        model_target=ModelTarget(locality=CLOUD_LOCALITY, model_id="cloud-model",
                                 provider="cloud-provider", context_tokens=None),
        invoke=lambda payload: b'{"claims": []}')
    return TierRouting(tier_of_call_site=cli.TIER_OF_CALL_SITE,
                       client_of_tier={tier: one
                                       for tier in (REASONING, LOGIC, FAST)})


def _authorities(conn, routing, *, mode=None):
    from production import (
        folder_levels_for, load_shipped_catalogue, read_packaged_library_file,
    )

    catalogue = load_shipped_catalogue(read_packaged_library_file)
    return cli.fact_call_authorities(
        conn, routing=routing, scan_run_id="scan", corpus_file_count=1,
        policy_version="policy", wire_handle_key=bytes(32), schema="academic",
        folder_levels=folder_levels_for(catalogue, SITUATION), user_id="t",
        now=lambda: CLOCK,
        **({} if mode is None else {"operation_mode": mode}))


def _a_file(conn, tmp_path, name: str, body: bytes) -> tuple[str, str]:
    path = tmp_path / name
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=".pdf", observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Courses", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _classify(conn, file_id: str, content_hash: str, *, protected: bool) -> None:
    from privacy.classification import ClassificationRecord
    from privacy.classification_store import ClassificationStore
    from privacy.vocabulary import DETECTOR

    ClassificationStore(conn).write(ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class="sensitive_personal" if protected
        else "personal_non_sensitive",
        protected=protected, basis=DETECTOR,
        evidence_refs=("sha256:" + "b" * 64,), reliability_state="validated",
        observed_at=CLOCK))


def _read(conn, file_id: str, content_hash: str, readings) -> None:
    """Record P4 runs, units and observations for one file version.

    `readings` is `(zone, container_label, text)`. A span-less observation over a
    recorded unit is the shape every text extractor emits, which is what makes the
    always-local zone the deciding term rather than a fixture accident.
    """
    run_id = f"run-{file_id}"
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    for index, (zone, label, text) in enumerate(readings):
        container = (Segment("field", label=label),)
        record_text_unit(conn, TextUnit(
            run_id=run_id, container_path=container, text=text))
        record_observation(conn, Observation(
            file_id=file_id, content_hash=content_hash,
            extractor_name="pdf.text", extractor_version="1.0.0",
            source_type="text_document", raw_value=text,
            location=Location(zone, container, text_span=TextSpan(0, len(text))),
            occurrence_count=1, observed_at=CLOCK, reliability="possible",
            run_id=run_id))


# ================================================================================
# `104` §18.2 gap 4: the stage NAMES the state it declined in
# ================================================================================

def test_a_file_nothing_could_be_read_from_is_named_rather_than_asked(conn,
                                                                     tmp_path):
    """The first of the two ways to have nothing to say, and it is about the READER.

    P5 extracted nothing -- no run, no observation -- so the offer is empty and there
    is no dossier to build. Before gap 4 this returned `()`, the resolver recorded
    `llm` as having run, and the report said a model had considered the file.

    SABOTAGE: return a bare `()` from the `if not offered` arm and the outcome is a
    tuple, `StageOutcome.of` calls it a stage that ran, and both assertions go red.
    """
    cli._bootstrap(conn)
    file_id, content_hash = _a_file(conn, tmp_path, "Unreadable.pdf", b"\x00\x01")
    _classify(conn, file_id, content_hash, protected=False)

    stage = fact_call_stage(_authorities(conn, _local_routing()))
    outcome = stage(conn, file_id, content_hash)

    assert isinstance(outcome, StageOutcome)
    assert outcome.not_asked == model_facts.NOT_ASKED_NOTHING_READ
    assert outcome.unresolved_reason == NO_CANDIDATE_EVIDENCE
    assert outcome.fact_ids == ()


def test_a_file_whose_every_reading_is_refused_says_so_in_its_own_words(conn,
                                                                       tmp_path):
    """`104` §18.2 gap 4's own headline: "a file whose evidence is all refused".

    The file WAS read -- there is a `filename`-zone reading, which every indexed file
    has -- and the release rules refuse that zone on every locality, so the offer is
    empty for a different reason than the test above. A person is owed the different
    sentence: the first is about this product's readers, and this one is about what
    may leave the device. Collapsing them would tell three files out of four the wrong
    one.

    SABOTAGE: return `NOT_ASKED_NOTHING_READ` from both arms -- drop the
    `observations_for_version` read -- and this goes red while the test above it
    still passes, which is the whole of the distinction.
    """
    cli._bootstrap(conn)
    file_id, content_hash = _a_file(conn, tmp_path, A_NAME, b"question one")
    _classify(conn, file_id, content_hash, protected=False)
    _read(conn, file_id, content_hash, [("filename", "name", A_NAME)])

    stage = fact_call_stage(_authorities(conn, _local_routing()))
    outcome = stage(conn, file_id, content_hash)

    assert model_facts.observations_for_version(
        conn, file_id=file_id, content_hash=content_hash), (
        "this fixture is only about a file that WAS read and whose readings were "
        "then all refused")
    assert outcome.not_asked == model_facts.NOT_ASKED_ALL_REFUSED
    assert outcome.unresolved_reason == NO_CANDIDATE_EVIDENCE


def test_a_file_no_model_may_see_is_named_by_the_stage_too(conn, tmp_path):
    """The backstop, and it names its reason like every other decline.

    `FactResolver` bars a file with no route before the stage is reached, so this
    arm is only entered by a caller who wired a stage another way. Reaching it means
    the two predicates disagreed -- and a duplicate `unresolved` row under the right
    reason is a far smaller defect than a file recorded as asked.

    `104` §18.7 (9 Sep 2026): a protected file REACHES the local model, so the file
    no model may see is a protected file on a run whose only destination is a cloud
    one -- `protected_cloud_denies` refuses it that target, and there is no local
    one to fall to.

    SABOTAGE: return `()` from the `chosen is None` arm and the run reports a
    protected file as one a model was asked about, which is the one sentence about a
    protected file this product must never print.
    """
    cli._bootstrap(conn)
    file_id, content_hash = _a_file(conn, tmp_path, "HKID scan.pdf", b"identity")
    _classify(conn, file_id, content_hash, protected=True)
    _read(conn, file_id, content_hash, [("body", "p1", "Homework 3 for PHYS 1401")])

    stage = fact_call_stage(_authorities(conn, _cloud_only_routing(),
                                         mode=cli.CLOUD_ENABLED_MODE))
    outcome = stage(conn, file_id, content_hash)

    assert outcome.not_asked == model_facts.NOT_ASKED_NO_ROUTE
    assert outcome.unresolved_reason == PRIVACY_WITHHELD


def test_no_arm_of_the_stage_returns_before_a_call_without_naming_its_state():
    """The four arms, pinned at the source, because three of them are driven above
    and the fourth cannot be reached with the shipped catalogue.

    `not request.allowlist` needs §3.5's closed vocabulary to be EMPTY, and the
    catalogue's six universal fields are in it for every situation -- so a corpus that
    reached that arm would be a corpus with no field catalogue at all, and building
    one would be a test of the fixture. It is still an arm that returns without
    building a call, so it still owes a name, and the honest guard for an unreachable
    branch is the one that reads the branch.

    The `return ()` at the END of the stage is not here: it returns the fact ids the
    call wrote, which is a stage that RAN. What this pin says is that no return
    ABOVE `run_call` hands the resolver a bare tuple.

    SABOTAGE: put `return ()` back in any of the four arms and this names the line.
    """
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(model_facts))
    factory = next(node for node in ast.walk(tree)
                   if isinstance(node, ast.FunctionDef)
                   and node.name == "fact_call_stage")
    # `104` §18.15: the stage's body moved into the `steps` generator, defined
    # beside `stage` inside `fact_call_stage`, so the cloud lane can hold several
    # round trips at once; `stage` itself is one line that drives it inline. The
    # arms live in `steps`, and the call they return before is `run_call_steps`
    # (the socket is its one `yield`).
    stage = next(node for node in ast.walk(factory)
                 if isinstance(node, ast.FunctionDef) and node.name == "steps")
    call = next(node for node in ast.walk(stage)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "run_call_steps")

    def names_a_state(node: ast.Return) -> bool:
        value = node.value
        return (isinstance(value, ast.Call) and isinstance(value.func, ast.Name)
                and value.func.id == "_not_asked")

    def returns_of(node):
        """`stage`'s OWN returns. `ast.walk` descends into the nested `own_readings`,
        whose return is a `DossierFill` and is not an answer to the resolver at all."""
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if isinstance(child, ast.Return):
                yield child
            yield from returns_of(child)

    early = [node for node in returns_of(stage) if node.lineno < call.lineno]
    # Four arms plus `104` R-13's reuse return, which is a stage that ran (the
    # answer was already given under this identity and reusing it IS asking),
    # plus `104` R-175's over-ceiling arm, which names its state through
    # `refusal_outcome` -- the same row a builder's `MalformedRequest` writes --
    # before it returns, so a file skipped for time never looks like a file the
    # model had nothing to say about.
    assert len(early) == 6, [node.lineno for node in early]

    def writes_a_refusal(node: ast.Return) -> bool:
        """The over-ceiling arm: a `refusal_outcome(...)` call in the same block."""
        block = next((parent for parent in ast.walk(stage)
                      if isinstance(parent, ast.ExceptHandler)
                      and any(child is node for child in ast.walk(parent))), None)
        if block is None:
            return False
        return any(isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name)
                   and inner.func.id == "refusal_outcome"
                   for inner in ast.walk(block))

    over_ceiling = [node for node in early if writes_a_refusal(node)]
    assert len(over_ceiling) == 1, [node.lineno for node in over_ceiling]
    named = [node for node in early if names_a_state(node)]
    assert len(named) == 4, (
        "every arm that returns before a call is built owes the record a reason; "
        f"unnamed at lines {[n.lineno for n in early if not names_a_state(n)]}")


def test_the_resolver_turns_the_stage_s_word_into_rows_and_into_its_own_record(
        conn, tmp_path):
    """The seam, end to end on one file: the stage names the state, the resolver
    writes one row per pending field and publishes the word, and `stages_run` no
    longer claims a model was asked.

    This is the assertion `104` §18.2 gap 4 is written as -- "one unresolved row per
    pending field naming the reason; the resolver records the stage's OUTCOME, not
    merely its invocation" -- and it is here rather than in a unit test because
    neither half is worth anything without the other: a word on a result nobody wrote
    a row for is the same silence with better manners.

    SABOTAGE: revert `resolve` to `stages_run.append(name)` unconditionally and the
    first assertion goes red; revert `_write_bars` to the bars alone and the third
    goes red.
    """
    from facts.resolver import FactResolver

    cli._bootstrap(conn)
    file_id, content_hash = _a_file(conn, tmp_path, "Unreadable.pdf", b"\x00\x01")
    _classify(conn, file_id, content_hash, protected=False)
    authorities = _authorities(conn, _local_routing())
    result = cli.model_fact_resolver(conn, authorities=authorities).resolve(
        conn, file_id=file_id, content_hash=content_hash)

    assert isinstance(
        cli.model_fact_resolver(conn, authorities=authorities), FactResolver)
    assert result.stages_run == ()
    assert result.stages_not_asked == {"llm": model_facts.NOT_ASKED_NOTHING_READ}

    rows = unresolved_for_file(conn, file_id, content_hash)
    pending = model_facts.pending_fields_for(
        conn, file_id=file_id, content_hash=content_hash,
        activation_signals=authorities.activation_signals)
    assert pending, "this fixture is only about a file with open fields"
    assert {row["field_key"] for row in rows} == set(pending)
    assert {row["reason"] for row in rows} == {NO_CANDIDATE_EVIDENCE}
    assert result.reason_counts == {NO_CANDIDATE_EVIDENCE: len(pending)}


def test_the_report_counts_the_file_as_not_asked_and_says_why(conn):
    """What a person actually reads, which is the half of gap 4 that is the gap.

    `_print_fact_pass` had a `not_asked` block for `104` R-37's two FOLDER reasons and
    nothing at all for the file's own four, so a declined file left no trace on the
    screen. The sentence is indexed straight out of `NOT_ASKED_SENTENCE`, so a state
    with no sentence is a `KeyError` on the report of a run that has already done its
    work -- `test_every_state_the_fact_stage_can_decline_in_has_a_reason_and_a_
    sentence` in `tests/p6/test_p6_budgets.py` is the guard against that.

    SABOTAGE: drop the `not_asked` tally from `_model_fact_pass`'s loop and the count
    is zero for every state, so the line never prints and the screen is the screen it
    was.
    """
    out = io.StringIO()
    cli._print_fact_pass(
        written=0, withheld={}, files=3, outcomes=[], model_id="qwen3:8b",
        out=out, not_asked={model_facts.NOT_ASKED_ALL_REFUSED: 2,
                            model_facts.NOT_ASKED_NOTHING_READ: 1})
    printed = out.getvalue()

    assert "2 of 3 files were not asked anything" in printed
    assert "does not leave this device" in printed
    assert "1 of 3 files were not asked anything" in printed
    assert "nothing could be read out of them" in printed


# ================================================================================
# `104` §18.2 gap 5: the cut is recorded on the call, and printed
# ================================================================================

def _fill(readings, ceiling):
    return model_facts.within_dossier_budget(readings, ceiling=ceiling)


def _observation(index: int, text: str) -> Observation:
    return Observation(
        file_id="file-1", content_hash="a" * 64, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=text,
        occurrence_count=1, observed_at=CLOCK, reliability="possible", run_id="r-1",
        location=Location("body", (Segment("field", label=f"p{index}"),),
                          TextSpan(0, len(text))))


def _request(conn, file_id: str = "file-1"):
    """The real prompt and a real `FactRequest`, over a file version with no rows.

    Built off `fact_call_authorities` rather than by hand: the prompt is the shipped,
    ratified A_fact text and `build_request` is the one that reads the allowlist, so
    what `build_fact_request` is handed here is the shape the stage hands it.

    `file_id` is a parameter because a pre-call report is addressed by
    `pre_call_address(call_site, request.subject_ref)`: two requests about one file
    are ONE address, which is right, and a test that needs two addresses needs two
    files.
    """
    authorities = _authorities(conn, _local_routing())
    return authorities.prompt, model_facts.build_request(
        conn, file_id=file_id, content_hash="a" * 64,
        activation_signals=authorities.activation_signals, normalizers={})


def test_the_cut_is_recorded_on_the_request_the_call_is_built_from(conn):
    """`104` §18.2 gap 5: the dropped readings reach the record as a COUNT.

    `build_fact_request` is handed the `DossierFill` its `observations` came out of,
    and the two numbers go onto `DossierRequest` -- never the readings themselves,
    which is why two integers can live on a record whose whole rule is
    reference-only. The harness copies them from there onto the `GroundingReport`,
    which is where a call's counters live.

    SABOTAGE: stop passing `fill=` at the `build_fact_request` call in
    `fact_call_stage` and the request reports a cut of nothing for a call the ceiling
    trimmed -- which is the silence, with the machinery to end it sitting unused.
    """
    from privacy.release import ModelTarget as Target

    cli._bootstrap(conn)
    offer = [_observation(index, "y" * 300) for index in range(40)]
    fill = _fill(offer, cli.GROUPING_LIMITS.max_dossier_tokens)
    assert fill.dropped, "this fixture is only about a ceiling that actually cuts"

    prompt, request = _request(conn)
    built = model_facts.build_fact_request(
        request, fill.taken, model_target=Target(
            locality=LOCAL, model_id="qwen3:8b", provider=LOCAL_PROVIDER),
        prompt=prompt, max_dossier_tokens=cli.GROUPING_LIMITS.max_dossier_tokens,
        fill=fill)

    assert built.readings_dropped == len(fill.dropped)
    assert built.readings_dropped_bytes == fill.dropped_bytes > 0


def test_a_fill_that_describes_other_readings_is_refused(conn):
    """The two arguments could disagree, so they are checked rather than trusted: a
    cut counted against a dossier that was not built from it is a number about
    nothing, and it would be a number a person acted on."""
    from llm_harness.records import MalformedRecord
    from privacy.release import ModelTarget as Target

    cli._bootstrap(conn)
    offer = [_observation(index, "y" * 300) for index in range(40)]
    fill = _fill(offer, cli.GROUPING_LIMITS.max_dossier_tokens)
    prompt, request = _request(conn)

    with pytest.raises(MalformedRecord):
        model_facts.build_fact_request(
            request, fill.taken[:-1], model_target=Target(
                locality=LOCAL, model_id="qwen3:8b", provider=LOCAL_PROVIDER),
            prompt=prompt,
            max_dossier_tokens=cli.GROUPING_LIMITS.max_dossier_tokens, fill=fill)


def test_a_refused_call_still_reports_what_the_ceiling_had_already_cut(conn):
    """The zero-count report is zero about the VALIDATION and not about the cut.

    `_zero_report` builds the report for a gate refusal, a budget deferral and a call
    that did not come back, and every counter on it is zero because nothing was
    validated. The cut is not like them: the builder had already spent the ceiling on
    this file's offer before any of those happened, so a zero here would tell a person
    that the file whose call was refused had all of its evidence assembled.

    SABOTAGE: drop the two `request.readings_dropped` lines from `_zero_report` and
    this goes red -- and the run would then report the trimmed file and the untrimmed
    file identically on exactly the runs where the trimming mattered most.
    """
    from llm_harness.authorship import COMPONENT_VERSION
    from llm_harness.records import PreCallAbstention
    from llm_harness.validation import report_for_pre_call_terminal
    from llm_harness.vocabulary import BUDGET_EXHAUSTED, DEFERRED
    from privacy.release import ModelTarget as Target

    cli._bootstrap(conn)
    offer = [_observation(index, "y" * 300) for index in range(40)]
    fill = _fill(offer, cli.GROUPING_LIMITS.max_dossier_tokens)
    prompt, request = _request(conn)
    built = model_facts.build_fact_request(
        request, fill.taken, model_target=Target(
            locality=LOCAL, model_id="qwen3:8b", provider=LOCAL_PROVIDER),
        prompt=prompt, max_dossier_tokens=cli.GROUPING_LIMITS.max_dossier_tokens,
        fill=fill)

    report = report_for_pre_call_terminal(
        built,
        PreCallAbstention(reason=BUDGET_EXHAUSTED, call_site=A_FACT,
                          subject_ref="file-1"),
        validator_version=COMPONENT_VERSION)

    assert report.reduction_rung == DEFERRED
    assert report.claims_total == 0
    assert report.readings_dropped == len(fill.dropped)
    assert report.readings_dropped_bytes == fill.dropped_bytes


def test_the_screen_reads_the_cut_back_off_the_stored_reports(conn):
    """The last leg: recorded, read back, and printed in a sentence.

    The number a person reads is read back from the records rather than accumulated
    in the loop, which is the rule `ResolveResult.reason_counts` already follows for
    the `unresolved` table: a count on the screen and a count in the database cannot
    then disagree. `_dossier_cut` is scoped by the dossier ids of THIS pass's own
    outcomes, because `llm_grounding_report` has no run column and a second scan
    against the same database writes rows beside these.

    SABOTAGE: make `_dossier_cut` count every row in the table rather than the ids it
    is handed, and the second half of this test -- a report from another call, not in
    the outcomes -- lands in the total.
    """
    from llm_harness.authorship import COMPONENT_VERSION
    from llm_harness.records import PreCallAbstention
    from llm_harness.store import record_grounding_report
    from llm_harness.validation import report_for_pre_call_terminal
    from llm_harness.vocabulary import BUDGET_EXHAUSTED
    from privacy.release import ModelTarget as Target

    cli._bootstrap(conn)
    offer = [_observation(index, "y" * 300) for index in range(40)]
    fill = _fill(offer, cli.GROUPING_LIMITS.max_dossier_tokens)

    def recorded(subject: str):
        prompt, request = _request(conn, subject)
        built = model_facts.build_fact_request(
            request, fill.taken, model_target=Target(
                locality=LOCAL, model_id="qwen3:8b", provider=LOCAL_PROVIDER),
            prompt=prompt,
            max_dossier_tokens=cli.GROUPING_LIMITS.max_dossier_tokens, fill=fill)
        report = report_for_pre_call_terminal(
            built,
            PreCallAbstention(reason=BUDGET_EXHAUSTED, call_site=A_FACT,
                              subject_ref=subject),
            validator_version=COMPONENT_VERSION)
        record_grounding_report(conn, report, observed_at=CLOCK)
        return report.dossier_id

    mine = recorded("file-1")
    # A SECOND CALL THIS PASS DID NOT MAKE, recorded beside it. `llm_grounding_report`
    # has no run column, so this is what a second scan of a second folder against the
    # same database leaves behind, and it must not land in this pass's total.
    other = recorded("some-other-file")
    assert other != mine

    class _Outcome:
        def __init__(self, dossier_id):
            self.dossier_id = dossier_id

    calls, readings, dropped_bytes = cli._dossier_cut(
        conn, [("file-1", _Outcome(mine))])
    assert calls == 1
    assert readings == len(fill.dropped)
    assert dropped_bytes == fill.dropped_bytes

    out = io.StringIO()
    cli._print_fact_pass(
        written=0, withheld={}, files=1, outcomes=[], model_id="qwen3:8b",
        out=out, cut=(calls, readings, dropped_bytes))
    printed = out.getvalue()
    assert f"{readings} readings" in printed
    assert "did not fit in what one call may carry" in printed
    assert "nothing was refused" in printed


def test_a_refusal_carries_no_address_so_the_screen_derives_one(conn):
    """`Refusal` and `CallRefused` hold no `dossier_id`, because at the moment either
    is made no dossier has been recorded -- and a call the GATE refused is exactly the
    call whose cut a person most needs told about, since the builder had already spent
    the ceiling before the door said no.

    Their reports are written all the same, addressed by `pre_call_address`, so the
    screen derives that address from the file id the outcome came in beside rather
    than reporting a cut of nothing.

    SABOTAGE: drop the `pre_call_address` fallback from `_dossier_cut` and a run whose
    calls were all refused reports no cut at all, while every row on disk says
    otherwise -- the screen and the database disagreeing is the one thing reading
    back from the records exists to prevent.
    """
    from llm_harness.authorship import COMPONENT_VERSION
    from llm_harness.records import PreCallAbstention
    from llm_harness.store import record_grounding_report
    from llm_harness.validation import report_for_pre_call_terminal
    from llm_harness.vocabulary import BUDGET_EXHAUSTED
    from privacy.release import ModelTarget as Target

    cli._bootstrap(conn)
    offer = [_observation(index, "y" * 300) for index in range(40)]
    fill = _fill(offer, cli.GROUPING_LIMITS.max_dossier_tokens)
    prompt, request = _request(conn, "file-refused")
    built = model_facts.build_fact_request(
        request, fill.taken, model_target=Target(
            locality=LOCAL, model_id="qwen3:8b", provider=LOCAL_PROVIDER),
        prompt=prompt, max_dossier_tokens=cli.GROUPING_LIMITS.max_dossier_tokens,
        fill=fill)
    record_grounding_report(
        conn,
        report_for_pre_call_terminal(
            built,
            PreCallAbstention(reason=BUDGET_EXHAUSTED, call_site=A_FACT,
                              subject_ref="file-refused"),
            validator_version=COMPONENT_VERSION),
        observed_at=CLOCK)

    class _NoAddress:
        """What a gate refusal looks like to `on_result`: a reason, and no dossier."""
        refusal_class = "ProtectedItemRequested"

    calls, readings, _bytes = cli._dossier_cut(
        conn, [("file-refused", _NoAddress())])
    assert calls == 1
    assert readings == len(fill.dropped)
