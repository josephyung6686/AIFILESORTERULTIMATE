# src/facts/stage_output.py
"""§8.5 / B7 — P2's envelope, produced by P6 and stored by P2.

"P6 emits a `stage_output` with `stage_id = factual_validation`, a populated
`inputs[]`, and the version tuple, for a file that produced facts and for a file that
produced none."

Produced, not stored: `eval_harness.replay.StageResult` is the shape a stage adapter
returns, and P2 adds `run_id`, `stage_id` and `version_tuple_ref` from the run it is
replaying. P5's `extractors/stage_output.py` set this pattern; this module follows it
with one deliberate difference — P6 fills `values`, because §8.5's `fact` dimension is
P6's to measure and P5 has no dimension of its own to report here.

TWO VOCABULARIES THAT LOOK LIKE ONE. P2 publishes ten `STAGE_IDS` and ten `DIMENSIONS`
and they are different lists: P6's stage is `factual_validation`, P6's dimension is
`fact`, and each raises under the other's checker. They are spelled here and nowhere
else in `facts`.

WHAT `result` IS. `facts.resolver.ResolveResult` (Task 20) is the only input, imported
rather than re-described: this module reads exactly the eight fields that dataclass
publishes and owns none of them.
"""
from __future__ import annotations

import sqlite3

from evidence_shape.canonical import canonical_json
from evidence_shape.store import runs_for_content

from eval_harness.stage_output import DimensionValue
from eval_harness.vocabulary import check_dimension, check_stage

from facts.resolver import ResolveResult

#: Stage 2 of §8.5's ten. Checked at import, so a P2 rename is a startup failure.
STAGE_ID: str = check_stage("factual_validation")

#: §8.5's `fact` dimension — NOT the stage id, and not interchangeable with it.
DIMENSION: str = check_dimension("fact")

#: `eval_harness.replay.StageResult`'s six fields, as P6 fills them. P5 fills five;
#: the sixth is `values`, and it is P6's because the `fact` dimension is P6's.
ENVELOPE_FIELDS: tuple[str, ...] = ("subject_ref", "outcome", "payload", "inputs",
                                    "budget_state", "values")


class UnsettledOutcome(Exception):
    """A result whose §8.5 outcome the design does not settle.

    One case only: zero facts, at least one `privacy_withheld` refusal, and no
    ceiling. The §8.5 table would call it `abstained`; the SPEC's `unresolved`
    rule 4 says `privacy_withheld` is not an abstention; and P2's writer refuses
    `deferred` without `ceiling_reached`. NEEDS-JOSEPH — see this task's preamble.
    Unreachable while P8 is absent, because a route that does not exist is not a
    route that was barred.
    """


def fact_stage_output(*, result: ResolveResult) -> dict:
    """One envelope for one `(file_id, content_hash)` P6 decided about.

    `subject_ref` is the CONTENT HASH — §8.2's identity for a file version, and the
    thing a fact is keyed by. `inputs` is the file id, because that is what P5's
    `extraction` stage keys its own subject by (`extractors.stage_output`), and §8.5
    links the two stages by that ref.
    """
    unresolved_count = sum(result.reason_counts.values())
    outcome, budget_state = _outcome_for(result, unresolved_count=unresolved_count)
    payload = canonical_json({
        # No fact id: §8.5 diffs stored forms across runs and a minted id is not
        # stable between two runs of the same corpus.
        "fact_count": len(result.fact_ids),
        "unresolved_reasons": dict(result.reason_counts),
        "stages_run": list(result.stages_run),
        "stages_barred": dict(result.stages_barred),
        "deferred_against": list(result.deferred_against),
        "error": result.error,
    })
    value = ({"fact_count": len(result.fact_ids),
              "unresolved_count": unresolved_count}
             if outcome == "produced" else None)
    return {
        "stage_id": STAGE_ID,
        "subject_ref": result.content_hash,
        "outcome": outcome,
        "payload": payload,
        "inputs": (result.file_id,),
        "budget_state": budget_state,
        "values": (DimensionValue(dimension=DIMENSION,
                                  subject_ref=result.content_hash,
                                  outcome=outcome, value=value),),
    }


def _outcome_for(result: ResolveResult, *,
                 unresolved_count: int) -> tuple[str, str]:
    """The §8.5 table, in the one order that keeps unfinished work visible.

    The ceiling is checked BEFORE the facts. A run that wrote two facts and then hit
    a ceiling reports `deferred`: §8.6 says to "mark the deferred stage, and leave the
    file or group in review rather than guessing", and `produced` would hide the half
    that never ran. This is not a widening of the SPEC's first row — that row already
    reads `within_ceiling`.
    """
    if result.error is not None:
        return "error", ("ceiling_reached" if result.deferred_against
                         else "within_ceiling")
    if result.deferred_against:
        return "deferred", "ceiling_reached"
    if result.fact_ids:
        return "produced", "within_ceiling"
    if result.reason_counts.get("privacy_withheld"):
        raise UnsettledOutcome(
            "zero facts and a privacy-withheld refusal has no §8.5 outcome: the "
            "table would say 'abstained', the SPEC's unresolved rule 4 forbids it, "
            "and P2 refuses 'deferred' without a ceiling. NEEDS-JOSEPH."
        )
    if unresolved_count:
        return "abstained", "within_ceiling"
    raise ValueError(
        "a result with no fact and no `unresolved` row is the missing row B7 exists "
        "to forbid: P2 cannot tell a considered refusal from a crash or a skip"
    )


def fact_version_axes(conn: sqlite3.Connection, *, content_hash: str,
                      model_identifier: str | None,
                      prompt_fingerprint: str | None) -> dict:
    """P6's three axes of §8.5's seven-field version tuple.

    P6 SUPPLIES axes; it does not assemble the tuple — the other four belong to P9,
    P10, P11 and the caller, and `eval_harness.run.record_version_tuple` refuses a
    partial one. The caller merges these three in.

    `extractor_versions` is P6's slice of P4's runs for this content hash. Two
    versions of one extractor in one tuple is refused rather than resolved: §3.4's
    cache key is per (extractor, version) and a map cannot hold both, so a caller
    comparing two extractor versions is comparing two runs.
    """
    versions: dict[str, str] = {}
    for run in runs_for_content(conn, content_hash):
        name, version = run.extractor_name, run.extractor_version
        if versions.get(name, version) != version:
            raise ValueError(
                f"{name!r} appears at two versions, {versions[name]!r} and "
                f"{version!r}; §8.5's tuple holds one version per extractor"
            )
        versions[name] = version
    return {
        "extractor_versions": versions,
        "model_identifier": model_identifier,
        "prompt_fingerprint": prompt_fingerprint,
    }
