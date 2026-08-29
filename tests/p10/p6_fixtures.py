"""§5.5's Academics example as REAL P1/P4/P6 rows. Tests only.

A materialiser tested against a stubbed fact reader proves nothing about the seam
it exists to cross, so every row here goes through the live writers. Their
vocabularies were confirmed by execution and neither accepts the obvious guess
`"rules"`:

* `facts.values.ensure_value(conn, *, field_key, canonical_value,
  first_evidence_ref, origin)` — `origin` is one of `('automatic', 'user')`, and
  `first_evidence_ref` must be a real P4 observation key or it raises "an
  automatically created value cites the observation that introduced it (§3.1)".
* `facts.file_facts.write_fact(conn, *, file_id, content_hash, field_key,
  value_id, reliability_state, origin, evidence_refs, cache_key, active, ...)` —
  `origin` is one of `('deterministic_extractor', 'rule', 'llm_interpretation',
  'user_correction', 'user_approved_folder')`.

The three files reproduce §5.5 exactly: one school, two courses, two work types,
and one file (`lab`) with no work type at all, so the unresolved case is in the
fixture rather than bolted on by a later test.
"""
from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass

from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from facts.file_facts import write_fact
from facts.states import VALIDATED
from facts.values import ensure_value
from grouping.vocabulary import DIRECT_ANCHOR
from tree_design.upstream import GroupMember

CLOCK = "2026-08-27T00:00:00+00:00"

#: (file_id, raw text, facts). `lab` carries no `work_type`: §5.11's unresolved file.
ACADEMICS = (
    ("syllabus", "BUSIB 4300 Syllabus",
     (("school", "Columbia"), ("subject", "BUSIB 4300"), ("work_type", "Syllabus"))),
    ("hw3", "BUSIB 4300 Homework 3",
     (("school", "Columbia"), ("subject", "BUSIB 4300"), ("work_type", "Homework"))),
    ("lab", "PHYS1401 Lab",
     (("school", "Columbia"), ("subject", "PHYS1401"))),
)


def _subject(conn, tmp_path, name, raw):
    path = tmp_path / f"{name}.pdf"
    path.write_bytes(raw.encode("utf-8"))
    file_id = record_file(
        conn, path, filename=path.name, normalized_filename=path.name.lower(),
        extension=".pdf", observed_size=len(raw),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    content_hash = get_file(conn, file_id)["content_hash"]
    record_run(conn, ExtractionRun(
        run_id=f"r_{name}", file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location("heading", (Segment("field", label="heading"),)),
        occurrence_count=1, observed_at=CLOCK, reliability="possible",
        run_id=f"r_{name}")
    record_observation(conn, observation)
    return file_id, content_hash, observation.observation_key


@dataclass(frozen=True)
class SeededCorpus:
    """§5.5's three files, and the ONLY way a test names one.

    `record_file` mints its own `file_id`; the friendly names above are fixture
    labels and never reach the database. A test that passed `"syllabus"` as a
    `GroupMember.file_id` would read no facts at all and every level would come
    back empty — which looks exactly like a broken materialiser and is not one.
    """

    conn: object
    subjects: Mapping[str, tuple[str, str, str]]

    def members(self, *names: str) -> tuple[GroupMember, ...]:
        return tuple(
            GroupMember(file_id=self.subjects[name][0],
                        content_hash=self.subjects[name][1],
                        basis=DIRECT_ANCHOR)
            for name in names)

    def file_id(self, name: str) -> str:
        return self.subjects[name][0]

    def add(self, name: str, field_key: str, value: str) -> None:
        """A SECOND simultaneous value for one field, which is how the OQ6 case
        is exercised without a second fixture."""
        file_id, content_hash, key = self.subjects[name]
        _fact(self.conn, file_id, content_hash, key, field_key, value)


def seed_academics(conn, tmp_path) -> SeededCorpus:
    """Write §5.5's three files with their real facts."""
    subjects = {}
    for name, raw, facts in ACADEMICS:
        file_id, content_hash, key = _subject(conn, tmp_path, name, raw)
        subjects[name] = (file_id, content_hash, key)
        for field_key, value in facts:
            _fact(conn, file_id, content_hash, key, field_key, value)
    return SeededCorpus(conn=conn, subjects=subjects)


def _fact(conn, file_id, content_hash, key, field_key, value):
    value_id = ensure_value(
        conn, field_key=field_key, canonical_value=value,
        first_evidence_ref=key, origin="automatic")
    return write_fact(
        conn, file_id=file_id, content_hash=content_hash, field_key=field_key,
        value_id=value_id, reliability_state=VALIDATED, origin="rule",
        evidence_refs=(key,), cache_key=f"ck_{file_id}_{field_key}_{value}",
        active=True)
