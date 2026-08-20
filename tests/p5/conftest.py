# tests/p5/conftest.py
"""P5's test fixtures: the recording sink that stands in for P4's writer, a fixed
clock so section 8.5's determinism assertion is a real assertion, and the fixture
readers the six extractors are driven by (added by the tasks that need them)."""
from __future__ import annotations

import pytest

from extractors.sink import ExtractionResult

from p4_stub import validate_observation, validate_run

#: Section 8.5 and P4 conformance rule 8 require two runs at the same content hash,
#: extractor version and config fingerprint to produce a byte-identical observation
#: set. The record carries `observed_at`, so the clock must be injectable for that to
#: be literally true. Every extractor below takes `now` as a required keyword.
FIXED_CLOCK = "2026-08-19T12:00:00+00:00"


class RecordingSink:
    """P4's writer, recorded. Appends only: nothing here updates or deletes, because
    P5 never overwrites an observation, a run or a text unit (section 8.2)."""

    def __init__(self) -> None:
        self.runs: list[dict] = []
        self.observations: list[dict] = []
        self.text_units: list[dict] = []
        self.supersessions: list[tuple[str, str]] = []

    def write(self, result: ExtractionResult, *,
              supersede_reason: str | None = None) -> str:
        run_id = f"run-{len(self.runs) + 1}"
        self.runs.append({"run_id": run_id, **result.run})
        for observation in result.observations:
            self.observations.append({"run_id": run_id, **observation})
        for unit in result.text_units:
            self.text_units.append({"run_id": run_id, **unit})
        if supersede_reason is not None:
            self.supersessions.append((run_id, supersede_reason))
        return run_id

    # --- read helpers, so tests never reach into the lists directly ---

    def units_for(self, run_id: str) -> list[dict]:
        return [u for u in self.text_units if u["run_id"] == run_id]

    def observations_for(self, run_id: str) -> list[dict]:
        return [o for o in self.observations if o["run_id"] == run_id]

    def run_for(self, run_id: str) -> dict:
        return next(r for r in self.runs if r["run_id"] == run_id)

    def conforms(self) -> None:
        """Every observation and every run, through P4's validator."""
        for run in self.runs:
            validate_run(run, len(self.observations_for(run["run_id"])))
        for observation in self.observations:
            validate_observation(
                {k: v for k, v in observation.items() if k != "run_id"},
                text_units=[{k: v for k, v in u.items() if k != "run_id"}
                            for u in self.units_for(observation["run_id"])],
            )


@pytest.fixture()
def sink() -> RecordingSink:
    return RecordingSink()
