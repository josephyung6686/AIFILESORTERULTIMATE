# src/extractors/stage_output.py
"""Section 8.5 / B7 - P2's envelope, produced by P5 and stored by P2.

"Emits P2 `stage_output` with `stage_id = extraction`, carrying `inputs[]`, an
explicit abstention value, a distinct budget-deferral value, and the version tuple."

Produced, not stored: `eval_harness.replay.StageResult` is the shape a stage adapter
returns and P2 adds `run_id`, `stage_id` and `version_tuple_ref` from the run it is
replaying. This module imports no part of P2 - P5's only run-time dependency is P1.

The mapping below is the join between two closed vocabularies neither part owns
alone, so every row carries its reason. Two rows are genuinely unsettled by the
design and are NEEDS JOSEPH items rather than quiet choices: `metadata_only` and
`unreadable`, both of which produce real metadata rows while leaving section 8.5's
extraction question ("did the expected text, metadata, table values, OCR text, or
image facts appear?") unanswered.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from extractors.shape import canonical_json

#: One of section 8.5's ten attribution stages. P5 is the first.
STAGE_ID = "extraction"

#: One of section 8.5's ten measured DIMENSIONS, which is a different ten-item list
#: that happens to share this spelling. Re-spelled rather than imported, for the same
#: reason every P2 outcome below is: P5 imports no part of P2. The test side pins it
#: against P2's live `DIMENSIONS`, exactly as it pins `STAGE_ID`.
DIMENSION = "extraction"

#: `eval_harness.replay.StageResult`'s six fields, as P5 fills them. The sixth is
#: `values`, and P2 reads it structurally -- see `DimensionValue` below.
ENVELOPE_FIELDS: tuple[str, ...] = ("subject_ref", "outcome", "payload", "inputs",
                                    "budget_state", "values")


@dataclass(frozen=True)
class DimensionValue:
    """The four fields `eval_harness.stage_output.record_stage_output` reads off a
    handed-over measurement, defined here rather than imported.

    P6's `facts/stage_output.py` imports P2's class for this. P5 cannot: it produces
    the envelope and P2 stores it, and `test_p5_imports_no_part_of_p2` holds P5's
    only run-time dependency at P1. P2 reads these by attribute and never by type,
    so the same four names are the whole contract -- the same way every P2 outcome
    string in `OUTCOME_BY_COMPLETENESS` is re-spelled rather than imported.
    """
    dimension: str
    subject_ref: str
    outcome: str
    value: Any

#: P4's nine `completeness` values to P2's five outcomes.
OUTCOME_BY_COMPLETENESS: dict[str, str] = {
    "complete": "produced",       # ran to the end, section 2.4
    "partial": "produced",        # some parts readable, section 2.5
    "capped": "produced",         # kept the text it recognized, section 2.7
    "deferred": "deferred",       # section 8.6's budget deferral
    "unsupported": "abstained",   # no extractor exists, section 2.4
    "metadata_only": "abstained",  # section 2.9's deliberate safe stop
    "unreadable": "abstained",    # indexed-but-unreadable, section 2.9 / M3
    "failed": "error",            # "an error is not an empty document", section 2.4
    "dataless": "abstained",      # C4: the bytes are not on this machine, 11 section 5
}

#: Section 8.6: a run that met a ceiling says so, and is never `abstained` - P2's
#: writer refuses that pairing outright, because a budget event must not become a
#: judgement about evidence.
CEILING_REACHED_COMPLETENESS: tuple[str, ...] = ("deferred", "capped")


def extraction_subject_ref(content_hash: str, extractor_name: str) -> str:
    """The subject one extraction measurement is ABOUT: a file version, read by
    one extractor.

    P11's `candidate_subject_ref` is the shape this copies, and the reason is the
    same: `stage_dimension_value` declares `PRIMARY KEY (run_id, dimension,
    subject_ref)`, so a key that does not distinguish two real measurements makes
    them one contested row.

    The hash ALONE was that key until it was measured against a live corpus. Every
    file version there carries two recorded runs -- a `filesystem`-tier pass that
    re-emits filesystem observations and a `native`-tier pass that reads the
    bytes -- with different observation counts, so the second insert raised. They
    are two facts about extraction and not one fact with a tie to break: they read
    different things, they can be right or wrong independently, and section 8.5's
    question ("did the expected text, metadata, table values, OCR text, or image
    facts appear?") has a different answer for each.

    The alternative was naming one tier authoritative, which throws a real
    measurement away -- and the discarded one is exactly where a regression could
    hide with nothing left to report it.

    **The extractor VERSION is not in the key, deliberately.** Section 8.7 keeps a
    citation alive across an upgrade -- P4's `observation_key` excludes the version
    for that reason -- and a subject that changed on every bump would throw away
    the hand-authored label on a schedule. It would also make section 8.5's
    central comparison impossible: two extractor versions over one bundle are
    compared by measuring THE SAME subject twice.
    """
    return f"{content_hash}:{extractor_name}"


def extraction_stage_output(*, run: Mapping[str, Any]) -> dict:
    """One envelope for one `extraction_runs` row.

    `subject_ref` is the file id, which is what P2's `bundle_file_entry` keys a file
    by; `inputs` is the CONTENT HASH, because an extraction run's input is the file
    VERSION - section 3.4's "a rename is free and a content rewrite is expensive".

    The DIMENSION value is keyed the other way round, on the file version AND the
    extractor that read it -- see `extraction_subject_ref`, which says why the hash
    alone could not carry it. A `DimensionValue` carries its own subject_ref for
    exactly this reason.
    """
    completeness = run["completeness"]
    if completeness not in OUTCOME_BY_COMPLETENESS:
        raise ValueError(
            f"{completeness!r} is not one of P4's nine `completeness` values"
        )
    outcome = OUTCOME_BY_COMPLETENESS[completeness]
    return {
        "stage_id": STAGE_ID,
        "subject_ref": run["file_id"],
        "outcome": outcome,
        "payload": canonical_json({
            "extractor_name": run["extractor_name"],
            "extractor_version": run["extractor_version"],
            "source_type": run["source_type"],
            "analysis_tier": run["analysis_tier"],
            "completeness": completeness,
            "coverage": dict(run["coverage"]),
            "observation_count": run["observation_count"],
        }),
        "inputs": (run["content_hash"],),
        "budget_state": ("ceiling_reached"
                         if completeness in CEILING_REACHED_COMPLETENESS
                         else "within_ceiling"),
        "values": (DimensionValue(dimension=DIMENSION,
                                  subject_ref=extraction_subject_ref(
                                      run["content_hash"], run["extractor_name"]),
                                  outcome=outcome,
                                  value=_measurement(run, outcome)),),
    }


def _measurement(run: Mapping[str, Any], outcome: str) -> dict | None:
    """Section 8.5's extraction question - "did the expected text, metadata, table
    values, OCR text, or image facts appear?" - answered from the run that ran.

    `observation_count` is how much appeared and `coverage` is how much of the file
    it was drawn from. Both are P4's own numbers, counted by the extractor; nothing
    here scores them. What counts as enough is the label's business, and the label is
    P2's `bundle_expectation.expected_value`.

    Coverage is not decoration: `complete`, `partial` and `capped` all map to
    `produced`, and section 8.6 forbids a degraded result being reported as a good
    one. Without coverage the three are one measurement.

    NULL for every other outcome, which is a row saying the stage RAN and measured
    nothing - not an absent row, which P2 reads as `not_run`. The two rows this
    module's preamble flags as NEEDS JOSEPH, `metadata_only` and `unreadable`, land
    here: they produce real metadata rows and leave section 8.5's question
    unanswered, so they abstain and measure nothing. That is unchanged by this
    function and is still unsettled.
    """
    if outcome != "produced":
        return None
    return {"observation_count": run["observation_count"],
            "coverage": dict(run["coverage"])}


def extractor_versions(runs: Iterable[Mapping[str, Any]]) -> dict[str, str]:
    """P5's half of section 8.5's version tuple: its first axis, "one version per
    extractor".

    Two versions of one extractor in one tuple is refused rather than resolved:
    section 3.4's cache key is per (extractor, version) and a map cannot hold both,
    so a caller comparing two extractor versions is comparing two runs.
    """
    versions: dict[str, str] = {}
    for record in runs:
        name, version = record["extractor_name"], record["extractor_version"]
        if versions.get(name, version) != version:
            raise ValueError(
                f"{name!r} appears at two versions, {versions[name]!r} and "
                f"{version!r}; section 8.5's tuple holds one version per extractor"
            )
        versions[name] = version
    return versions
