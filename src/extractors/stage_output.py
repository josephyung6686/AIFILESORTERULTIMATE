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

from typing import Any, Iterable, Mapping

from extractors.shape import canonical_json

#: One of section 8.5's ten attribution stages. P5 is the first.
STAGE_ID = "extraction"

#: `eval_harness.replay.StageResult`'s fields, as P5 fills them.
ENVELOPE_FIELDS: tuple[str, ...] = ("subject_ref", "outcome", "payload", "inputs",
                                    "budget_state")

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


def extraction_stage_output(*, run: Mapping[str, Any]) -> dict:
    """One envelope for one `extraction_runs` row.

    `subject_ref` is the file id, which is what P2's `bundle_file_entry` keys a file
    by; `inputs` is the CONTENT HASH, because an extraction run's input is the file
    VERSION - section 3.4's "a rename is free and a content rewrite is expensive".
    """
    completeness = run["completeness"]
    if completeness not in OUTCOME_BY_COMPLETENESS:
        raise ValueError(
            f"{completeness!r} is not one of P4's nine `completeness` values"
        )
    return {
        "stage_id": STAGE_ID,
        "subject_ref": run["file_id"],
        "outcome": OUTCOME_BY_COMPLETENESS[completeness],
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
    }


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
