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

#: One producer, one shape. The caller binds every strategy and every threshold into
#: the callable before handing it over, so this module sees neither.
Stage = Callable[[sqlite3.Connection, str, str], "tuple[str, ...]"]

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
    error: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "reason_counts",
                           MappingProxyType(dict(self.reason_counts)))
        object.__setattr__(self, "stages_barred",
                           MappingProxyType(dict(self.stages_barred)))

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
        stages_run: list[str] = []
        barred: dict[str, str] = {}
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

        # §2.2 fires before ranking. The return value is the survivor set;
        # stages that re-query observations still use field_permitted.
        # This call is what writes the unresolved row Done-means 22 requires.
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
            fact_ids.extend(stage(conn, file_id, content_hash))
            stages_run.append(name)

        if barred:
            self._write_bars(conn, file_id=file_id, content_hash=content_hash,
                             barred=barred, attempted=tuple(stages_run))

        # Only now: preamble rule 5's recorded pass means a pass that COMPLETED. A
        # producer that raised skipped this line, so `no_usable_facts` still raises
        # `FactPassNotRun` for that content hash rather than answering from a
        # half-written table.
        self._record_pass(conn, file_id, content_hash)

        counts: dict[str, int] = {}
        written: list[str] = []
        for row in unresolved_for_file(conn, file_id, content_hash):
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
        )

    def _write_bars(self, conn: sqlite3.Connection, *, file_id: str,
                    content_hash: str, barred: Mapping[str, str],
                    attempted: "tuple[str, ...]") -> None:
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
        """
        cache_key = self._cache_key_for(file_id, content_hash)
        for stage_name, bar in barred.items():
            reason = REASON_BY_BAR[bar]
            for field_key in self._pending_fields(conn, file_id, content_hash):
                write_unresolved(
                    conn, file_id=file_id, content_hash=content_hash,
                    field_key=field_key, reason=reason,
                    attempted_producers=attempted + (stage_name,),
                    evidence_refs=(), cache_key=cache_key,
                )
