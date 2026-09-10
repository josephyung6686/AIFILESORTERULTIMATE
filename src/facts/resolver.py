# src/facts/resolver.py
"""The one entry point, sequencing P6's producers in §8.6's order.

The order is a contract, not an implementation detail, which is why it is a
sequencer and not three calls scattered through a caller: §00 says "The engine
should degrade in a predictable order. Direct facts and high-precision rules run
first because they are cheap and reliable."

The producers arrive as injected `Stage` callables. This module imports none of
them, so no threshold, gazetteer, regex catalogue or producer-string list can reach
it — the caller binds those into the stage it hands over. It also means Tasks 17 and
19, written in the same wave, are not build-order dependencies of this one.

`resolve` never swallows an exception. P6's failures are ContractViolations and must
propagate; a caller that catches one still owes P2 an envelope, and constructs it
with `ResolveResult.errored`.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Callable, Mapping

from facts.budgets import (
    CEILING_GATED_STAGES, DEGRADATION_ORDER, exhausted_ceilings,
)
from facts.unresolved import (
    BUDGET_DEFERRED, PRIVACY_WITHHELD, unresolved_for_file, write_unresolved,
)

@dataclass(frozen=True)
class StageOutcome:
    """What one producer DID, for a producer that can decline to run at all.

    `104` §18.2 gap 4 (9 Sep 2026). A stage used to answer one thing -- the fact ids
    it wrote -- and `resolve` recorded its INVOCATION: it appended the name to
    `stages_run` whether or not anything had happened inside. That is true of the two
    deterministic producers, which always look, and false of the model producer,
    which returns `()` at four different points before a call is built: every field is
    already settled, no model may see this file, nothing about it is releasable, or
    the schema left no field to ask about. In all four the run said the stage had run,
    the payload said `stages_run: ["llm"]`, and a person reading the report was told
    the file had been asked and the model had had nothing to say. `00`'s standing rule
    is the opposite -- what was skipped is counted and named, never silently omitted --
    and constitution rule two says any successfully-read file must reach the model or
    the reason must be recorded.

    So a stage MAY answer this record instead of a bare tuple. Three fields:
    `fact_ids` is exactly what the tuple was; `not_asked` is the outcome word, `None`
    for a producer that did its work; `unresolved_reason` is P6's own published reason
    for the row `resolve` then writes per open field, `None` when there is no field to
    name (nothing was pending) or when the rows are already on disk.

    **The stage does not write the rows and that is deliberate.** `write_unresolved`
    needs the §3.4 cache key and the pending field list, both of which `FactResolver`
    already holds -- `_write_bars` has written "one row per pending field" for the two
    bars since Task 20 -- and a second writer inside the stage would need a second
    answer to "what is still open on this file" and a cache key invented at a point
    where no model and no prompt have been chosen. One writer, two callers.

    A bare tuple still means what it always meant: the stage ran and this is what it
    produced. Nothing that returns one changes.
    """
    fact_ids: tuple[str, ...] = ()
    not_asked: str | None = None
    unresolved_reason: str | None = None

    def __post_init__(self) -> None:
        if self.not_asked is None and self.unresolved_reason is not None:
            raise ValueError(
                "a stage that ran needs no not-asked reason: an `unresolved_reason` "
                "without a `not_asked` word would have `resolve` write refusal rows "
                "for a producer it also records as having run"
            )

    @classmethod
    def of(cls, produced) -> "StageOutcome":
        """Normalise what a `Stage` returned. A tuple is a stage that ran."""
        if isinstance(produced, StageOutcome):
            return produced
        return cls(fact_ids=tuple(produced))


#: One producer, one shape. The caller binds every strategy and every threshold into
#: the callable before handing it over, so this module sees neither.
#:
#: **TWO SHAPES SINCE `104` §18.2 gap 4**, and the second is a widening rather than a
#: replacement: a stage returns the fact ids it wrote, or a `StageOutcome` when it can
#: also decline to run and owes the record a reason. `StageOutcome.of` normalises, so
#: `facts.direct` and `facts.rules` are untouched.
Stage = Callable[[sqlite3.Connection, str, str],
                 "tuple[str, ...] | StageOutcome"]

#: `facts.usable.record_pass`, bound by the caller to supply the tier set it needs.
#: Injected rather than imported because `resolve`'s signature is fixed by the
#: skeleton and has nowhere to carry `analysis_tiers`, and because determining which
#: tiers a pass covered is a read over P4's runs that belongs to Task 19's owner.
PassRecorder = Callable[[sqlite3.Connection, str, str], None]

#: The two ways a ceiling-gated stage can fail to run. Named rather than spelled at
#: the branch, because `stages_barred` publishes them to a caller.
PRIVACY_BAR = "privacy"
BUDGET_BAR = "budget"

#: Why a ceiling-gated stage did not run, and the `unresolved` reason each produces.
#: Two bars, two reasons, no shared bucket — and neither reason is an abstention.
#: The reasons are Task 5's published constants, never a second copy (preamble §3.1).
REASON_BY_BAR: Mapping[str, str] = MappingProxyType({
    PRIVACY_BAR: PRIVACY_WITHHELD,
    BUDGET_BAR: BUDGET_DEFERRED,
})


class StageSetInvalid(Exception):
    """The stage map is not exactly §8.6's three producers."""


@dataclass(frozen=True)
class ResolveResult:
    """What one pass over one file version did, in the terms §8.5 measures.

    `fact_ids` is what the producers returned. `reason_counts` is read back from the
    `unresolved` table rather than accumulated in memory, so Done-means 20's "the two
    are distinguishable from the records alone" is true by construction rather than
    by care.

    **`stages_run` MEANS RAN, SINCE `104` §18.2 gap 4.** It used to mean "was
    invoked", which was the same thing while every producer always did its work and
    stopped being the same thing when the model producer learned four ways to decline
    before a call is built. A stage that declined is in `stages_not_asked` with its
    reason and is absent from `stages_run`, so a reader can no longer take a name in
    that tuple as evidence that a model was asked about this file.
    """
    file_id: str
    content_hash: str
    fact_ids: tuple[str, ...] = ()
    reason_counts: Mapping[str, int] = field(default_factory=dict)
    stages_run: tuple[str, ...] = ()
    stages_barred: Mapping[str, str] = field(default_factory=dict)
    deferred_against: tuple[str, ...] = ()
    #: The `unresolved` rows THIS pass wrote, so a caller can scope to them instead of
    #: re-reading the version's whole history. `budgets.deferred_counts` charged four
    #: against two rows on disk before this existed.
    unresolved_ids: tuple[str, ...] = ()
    #: Whether the file VERSION carries any `unresolved` row at all, this pass's or an
    #: earlier one's. Two different questions were being answered by one number:
    #: "what did THIS pass do", which must be pass-scoped or the §8.5 payload stops
    #: being byte-stable across identical runs, and "what is the STATE of this
    #: version", which is what §8.5's outcome reports. Scoping both to the pass made a
    #: re-resolve that wrote nothing new accuse B7 of a missing row that was on disk.
    version_has_unresolved: bool = False
    #: WHICH PRODUCERS DECLINED TO RUN, and the word each gave for it (`104` §18.2
    #: gap 4). `stages_run` is now what its name says -- the producers that DID the
    #: work -- and this is its complement for the producers that were reached and
    #: answered "not this file, because...". It is not `stages_barred`: a bar is the
    #: sequencer's own decision taken BEFORE the stage is called, for a privacy class
    #: or a spent ceiling, and this is the stage's own answer from inside. Both are
    #: published because the screen says different sentences about them -- a withheld
    #: file is about the person's policy, a file with nothing releasable is about what
    #: this run could read.
    stages_not_asked: Mapping[str, str] = field(default_factory=dict)
    error: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "reason_counts",
                           MappingProxyType(dict(self.reason_counts)))
        object.__setattr__(self, "stages_barred",
                           MappingProxyType(dict(self.stages_barred)))
        object.__setattr__(self, "stages_not_asked",
                           MappingProxyType(dict(self.stages_not_asked)))

    @classmethod
    def errored(cls, *, file_id: str, content_hash: str,
                error: str) -> "ResolveResult":
        """The stage failed. §8.5's fourth outcome still needs an envelope."""
        return cls(file_id=file_id, content_hash=content_hash, error=error)


class FactResolver:
    """P6's single entry point. Constructed with every injected strategy; holds none.

    `stages` maps each of `DEGRADATION_ORDER` to a `Stage` or to `None`. `None` means
    the route does not exist — which is the ordinary case for `llm`, because P8 does
    not exist. A route that does not exist is NOT a route that was barred: nothing is
    withheld, nothing is deferred, and no `unresolved` row is written for it.

    `screen_metadata` is required and has no default. §2.2's tool-metadata
    suppression must fire **before** any producer; without this call `python-docx`
    can become a `direct` fact and Done-means 22 is unreachable. Task 9 publishes
    the helper; this constructor is the caller. `DEGRADATION_ORDER` stays the three
    producers — screening is not a fourth producer.

    Task 9's helper is keyword-only and takes the version's observations plus the
    two catalogue predicates. The production composition site binds a thin adapter
    with this constructor's three-positional shape::

        def screen(conn, file_id, content_hash):
            observations = observations_for_version(conn, file_id, content_hash)
            return screen_metadata(
                conn, file_id=file_id, content_hash=content_hash,
                observations=observations,
                tool_producer_strings=TOOL_PRODUCER_STRINGS,
                metadata_property_names=METADATA_PROPERTY_NAMES,
            )

    Tests in this task bind a no-op or a recorder. They do not import Task 9.
    """

    def __init__(self, *, stages: Mapping[str, Stage | None],
                 pending_fields: Callable[[sqlite3.Connection, str, str],
                                          "tuple[str, ...]"],
                 budget_exhausted: Callable[[str], bool],
                 model_route_permitted: Callable[[str], bool],
                 record_pass: PassRecorder,
                 cache_key_for: Callable[[str, str], str],
                 screen_metadata: Callable[[sqlite3.Connection, str, str],
                                           object]) -> None:
        if set(stages) != set(DEGRADATION_ORDER):
            raise StageSetInvalid(
                f"stages must be exactly {DEGRADATION_ORDER}, got "
                f"{tuple(sorted(stages))}"
            )
        self._stages = dict(stages)
        self._pending_fields = pending_fields
        self._budget_exhausted = budget_exhausted
        self._model_route_permitted = model_route_permitted
        self._record_pass = record_pass
        self._cache_key_for = cache_key_for
        self._screen_metadata = screen_metadata

    def resolve(self, conn: sqlite3.Connection, *, file_id: str,
                content_hash: str) -> ResolveResult:
        """One file, resolved on this thread, every stage run to its end.

        `104` §18.15 split the body into `resolve_steps` so a pass that drives a
        cloud lane can hold several files' round trips at once. This is that
        generator driven inline, and it is what every caller that walks one file at
        a time still gets.

        **IT DRIVES ITSELF RATHER THAN CALLING `harness.drive_inline`, AND THAT IS
        THE LAYERING AND NOT AN OVERSIGHT.** P8 imports P6 -- `llm_harness.sites`
        reads `facts.llm_seam` -- so a P6 module importing P8 would make the two
        packages mutually dependent for four lines of generator plumbing. What is
        yielded here is a thing that knows how to perform itself and this sequencer
        needs to know nothing else about it, which is why it can be driven without
        naming what it is.
        """
        steps = self.resolve_steps(
            conn, file_id=file_id, content_hash=content_hash)
        try:
            pending = next(steps)
            while True:
                pending = steps.send(pending.perform())
        except StopIteration as done:
            return done.value

    def resolve_steps(self, conn: sqlite3.Connection, *, file_id: str,
                      content_hash: str):
        """`resolve`, with a model stage's socket left for the caller to run.

        `104` §18.15. Every statement here reads or writes the database and stays
        on the thread that owns the connection; the one thing that may leave is a
        `PendingSend` a producer hands up, and only the `llm` producer has one.
        Every other stage is called exactly as it was, because `getattr(stage,
        "steps", None)` is the whole of the protocol widening: a producer with a
        round trip says so by carrying one, and the fifteen that have none say
        nothing and are not asked.
        """
        stages_run: list[str] = []
        barred: dict[str, str] = {}
        # `104` §18.2 gap 4: the producers that were REACHED and declined, and the
        # reason each gave. Kept apart from `barred` because the two are decided in
        # different places -- a bar is this sequencer's, before the call; a decline is
        # the producer's, from inside -- and a report that merged them would tell a
        # person their privacy policy withheld a file whose evidence was simply all
        # in an always-local zone.
        not_asked: dict[str, str] = {}
        # The `unresolved` reason each decline owes a row under, or `None` where there
        # is no open field to name one for. Collected here and written once below,
        # beside the bars, through the one writer that holds the cache key.
        decline_reasons: dict[str, str] = {}
        deferred_against: tuple[str, ...] = ()
        fact_ids: list[str] = []

        # THE ROWS THIS PASS WRITES, and no earlier pass's. `unresolved_for_file` is
        # scoped to the file VERSION, not to a pass, so counting it directly reported
        # every prior pass's refusals as this one's: a second resolve of one version
        # wrote a single row and was charged two. That propagated into Task 21's
        # `fact_stage_output` payload and broke its byte-stability across two
        # identical runs -- the exact divergence that payload design exists to
        # prevent. Snapshotting the ids is still "read back from the records rather
        # than accumulated in memory" (Done-means 20): the ids ARE records, and this
        # makes them ONE PASS's records.
        already = {row["unresolved_id"]
                   for row in unresolved_for_file(conn, file_id, content_hash)}

        # §2.2 fires BEFORE any producer, and this call is what writes the one
        # `unresolved` row Done-means 22 requires. It is not the filter and must not
        # be read as one: the suppression it decides needs no field, but §2.3's
        # demotion -- "may populate `authored_by` and no other field" -- is only
        # answerable where a producer PICKS a field, and this sequencer has no field.
        # `facts.rules` and `facts.direct` call `field_permitted` at that point, with
        # the `MetadataScreen` the caller binds into each stage. While the return
        # value here was treated as the whole story, `python-docx` reached `subject`
        # as a `validated` fact with the row beside it saying it had been refused.
        self._screen_metadata(conn, file_id, content_hash)

        for name in DEGRADATION_ORDER:
            stage = self._stages[name]
            if stage is None:
                continue
            if name in CEILING_GATED_STAGES:
                # §8.4 first: a handling class that forbids the model route is a
                # PROHIBITION, and a file that may never reach a model is not a file
                # waiting for budget to free up. Reporting it as a deferral would
                # promise work that will never be done.
                if not self._model_route_permitted(file_id):
                    barred[name] = PRIVACY_BAR
                    continue
                exhausted = exhausted_ceilings(
                    budget_exhausted=self._budget_exhausted)
                if exhausted:
                    barred[name] = BUDGET_BAR
                    deferred_against = exhausted
                    continue
            # `104` §18.2 gap 4: THE STAGE'S OUTCOME, NOT ITS INVOCATION. This line
            # was `fact_ids.extend(stage(...)); stages_run.append(name)` -- the name
            # was appended whether or not anything had happened inside, so a file the
            # model producer declined before building a call was reported as a file
            # the model was asked about and had nothing to say. `StageOutcome.of`
            # keeps a bare tuple meaning what it always meant.
            # `104` §18.15: THE PRODUCER'S OWN SUSPENDABLE FORM WHEN IT HAS ONE.
            # `yield from` runs it here, statement for statement, until it reaches
            # a socket -- and a socket is the only thing it can hand up, so this
            # line is the same line for every stage that has none.
            producing = getattr(stage, "steps", None)
            produced = (stage(conn, file_id, content_hash) if producing is None
                        else (yield from producing(conn, file_id, content_hash)))
            outcome = StageOutcome.of(produced)
            fact_ids.extend(outcome.fact_ids)
            if outcome.not_asked is None:
                stages_run.append(name)
                continue
            not_asked[name] = outcome.not_asked
            if outcome.unresolved_reason is not None:
                decline_reasons[name] = outcome.unresolved_reason

        if barred or decline_reasons:
            self._write_bars(conn, file_id=file_id, content_hash=content_hash,
                             barred=barred, attempted=tuple(stages_run),
                             declined=decline_reasons)

        # Only now: preamble rule 5's recorded pass means a pass that COMPLETED. A
        # producer that raised skipped this line, so `no_usable_facts` still raises
        # `FactPassNotRun` for that content hash rather than answering from a
        # half-written table.
        self._record_pass(conn, file_id, content_hash)

        counts: dict[str, int] = {}
        written: list[str] = []
        rows = unresolved_for_file(conn, file_id, content_hash)
        for row in rows:
            if row["unresolved_id"] in already:
                continue
            written.append(row["unresolved_id"])
            counts[row["reason"]] = counts.get(row["reason"], 0) + 1

        return ResolveResult(
            file_id=file_id, content_hash=content_hash,
            fact_ids=tuple(fact_ids), reason_counts=counts,
            stages_run=tuple(stages_run), stages_barred=barred,
            deferred_against=deferred_against,
            unresolved_ids=tuple(written),
            version_has_unresolved=bool(rows),
            stages_not_asked=not_asked,
        )

    def _write_bars(self, conn: sqlite3.Connection, *, file_id: str,
                    content_hash: str, barred: Mapping[str, str],
                    attempted: "tuple[str, ...]",
                    declined: Mapping[str, str] = MappingProxyType({})) -> None:
        """The unfinished work, recorded AS unfinished.

        §00: the product must avoid "the false impression that an unprocessed file
        was understood and found unimportant". An absent row gives exactly that
        impression, so every field the barred route would have attempted gets one.

        `evidence_refs` is empty and that is correct rather than lazy: the barred
        route never looked at an observation, and the SPEC's own column note says
        the refs are "the observation keys considered, where any were (may be
        empty)". The extracted evidence is retained where it always was — in P4's
        `evidence` table, which P6 never writes and which P4's
        `evidence_never_overwritten` trigger makes unfalsifiable.

        **`declined` IS THE SECOND CALLER, AND IT IS THE SAME OBLIGATION (`104` §18.2
        gap 4).** A bar is decided here and a decline is decided inside the producer,
        but the row a person is owed is identical: this field is still open, and here
        is the reason nobody answered it. `barred` names the bar and the mapping
        turns it into a reason; `declined` carries the reason already, because it is
        the PRODUCER's word about its own evidence and only the producer can know
        whether nothing was releasable or everything was refused. Both go through this
        one writer because the §3.4 cache key and the pending field list live here and
        nowhere else -- a producer writing its own rows would need a cache key at a
        point where no model and no prompt have been chosen.

        A decline for which the producer named no reason writes nothing, and that is
        the case where there IS no open field: every one was already settled, so
        `self._pending_fields` is empty and a row would have no field to name.
        """
        cache_key = self._cache_key_for(file_id, content_hash)
        reasons = {stage_name: REASON_BY_BAR[bar]
                   for stage_name, bar in barred.items()}
        reasons.update(declined)
        for stage_name, reason in reasons.items():
            for field_key in self._pending_fields(conn, file_id, content_hash):
                write_unresolved(
                    conn, file_id=file_id, content_hash=content_hash,
                    field_key=field_key, reason=reason,
                    attempted_producers=attempted + (stage_name,),
                    evidence_refs=(), cache_key=cache_key,
                )
