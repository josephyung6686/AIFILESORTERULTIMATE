# tools/promptbench/site_a.py
"""Site A needs a real P6 world: the validator reads facts, not a fixture.

`validate_fact_proposal` checks a claim against P6's `FactRequest` -- the active
schema's allowlist, the file version's citable observations, its stronger facts
-- and writes nothing here (`apply_consequence=False`). So an A case is turned
into one file in a throwaway database with its evidence recorded as real P4
observations, exactly the way `tests/p8/test_p8_prompt_stress_cases.py` builds
its world. The observation keys the model is shown are the ones P4 minted for
those rows, so the case's own minted keys are replaced, not trusted.

The glossary under test is swapped per candidate: `llm_harness.dossier` reads a
module-level path through an `lru_cache`, and the bench points it at the
candidate's file and clears the cache, recording which file was in force. This
is a bench-only substitution; the product's path constant is untouched on disk.
"""
from __future__ import annotations

import dataclasses
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from database_agent.db import create_schema, open_database  # noqa: E402
from database_agent.files_table import get_file, record_file  # noqa: E402
from evidence_shape.location import Location, Segment, TextSpan  # noqa: E402
from evidence_shape.observation import Observation  # noqa: E402
from evidence_shape.runs import ExtractionRun  # noqa: E402
from evidence_shape.schema import create_evidence_schema  # noqa: E402
from evidence_shape.store import record_observation, record_run  # noqa: E402
from facts.domains import ActivationSignal, ActivationSignals  # noqa: E402
from facts.fields import create_fields  # noqa: E402
from facts.llm_seam import build_request  # noqa: E402
from llm_harness import dossier as dossier_module  # noqa: E402
from llm_harness.fact_validation import FactValidationDependencies  # noqa: E402
from llm_harness.schema import create_llm_schema  # noqa: E402
from llm_harness.sites import FactSiteDependencies, SiteDependencies  # noqa: E402
from model_facts import open_question, pending_fields_for  # noqa: E402

from tools.promptbench.cases import Case, Evidence

CLOCK = "2026-09-06T00:00:00+00:00"


@dataclasses.dataclass(frozen=True)
class SiteAWorld:
    conn: object
    case: Case                     # the case with P4's real keys substituted
    allowed_vocabulary: tuple[str, ...]
    folder_levels: tuple
    site_dependencies: SiteDependencies
    resolver: object
    file_id: str


def _zone_location(item: Evidence, index: int) -> Location:
    span = None if item.span is None else TextSpan(*item.span)
    return Location(item.zone, (Segment("field", label=f"{item.zone}-{index}"),),
                    text_span=span)


def build_world(case: Case, workdir: Path, *, catalogue) -> SiteAWorld:
    """One synthetic file, its observations, and P6's authorities over them."""
    from cli import contradicts_stronger, normalize_for_model, normalize_for_review
    from production import folder_levels_for

    workdir.mkdir(parents=True, exist_ok=True)
    # A world is rebuilt from the case every time and is never reused: a database
    # left by an earlier run would make the second build collide on its own rows.
    for leftover in workdir.glob(f"{case.case_id}.sqlite*"):
        leftover.unlink()
    conn = open_database(workdir / f"{case.case_id}.sqlite")
    create_schema(conn)
    create_evidence_schema(conn)
    create_fields(conn)
    create_llm_schema(conn)

    path = workdir / f"{case.case_id}.bin"
    path.write_bytes(f"promptbench:{case.subject_ref}".encode("utf-8"))
    file_id = record_file(
        conn, path, filename=f"{case.case_id}.pdf",
        normalized_filename=f"{case.case_id.lower()}.pdf", extension=".pdf",
        observed_size=path.stat().st_size,
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="bench", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    content_hash = get_file(conn, file_id)["content_hash"]
    record_run(conn, ExtractionRun(
        run_id=f"run-{case.case_id}", file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))

    rekeyed: list[Evidence] = []
    for index, item in enumerate(case.evidence):
        observation = Observation(
            file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
            extractor_version="1.0.0", source_type="text_document",
            raw_value=item.value, location=_zone_location(item, index),
            occurrence_count=1, observed_at=CLOCK, reliability="possible",
            run_id=f"run-{case.case_id}")
        record_observation(conn, observation)
        rekeyed.append(dataclasses.replace(item, key=observation.observation_key))

    schema_id = case.schema_id or "academic"
    signals = ActivationSignals(signals=(
        ActivationSignal(schema_id=schema_id, activates=lambda rows: True),))
    request = build_request(conn, file_id=file_id, content_hash=content_hash,
                            activation_signals=signals, normalizers={})
    levels = folder_levels_for(catalogue, case.situation or "academic.coursework")
    pending = pending_fields_for(conn, file_id=file_id, content_hash=content_hash,
                                 activation_signals=signals)
    vocabulary, visible = open_question(pending, levels)

    dependencies = SiteDependencies(
        fact=FactSiteDependencies(
            fact_request=request,
            fact_dependencies=FactValidationDependencies(
                normalize=normalize_for_model, contradicts=contradicts_stronger,
                # The bench emulates the product's own composition, so it carries
                # check 3's review half too (`104` R-98): a title-named course is
                # accepted into review here exactly as it is in the product.
                normalize_for_review=normalize_for_review)),
        placement=None, residual=None, template=None)
    values = {item.key: item.value for item in rekeyed if item.released}
    rekeyed_case = dataclasses.replace(
        case, evidence=tuple(rekeyed), subject_ref=file_id,
        allowed_vocabulary=vocabulary,
        folder_levels=tuple((l.field, l.label, l.requirement) for l in visible))
    return SiteAWorld(
        conn=conn, case=rekeyed_case, allowed_vocabulary=vocabulary,
        folder_levels=visible, site_dependencies=dependencies,
        resolver=lambda key: values.get(key), file_id=file_id)


def use_glossary(path: Path | None) -> str:
    """Point the product's glossary reader at `path` for this process; return the
    path in force so the run record can name it."""
    if path is not None:
        dossier_module.GLOSSARY_FILE = path
    dossier_module._meanings.cache_clear()
    return str(dossier_module.GLOSSARY_FILE)


def contradicts_for_a():
    from cli import contradicts_stronger
    return contradicts_stronger


__all__ = ["SiteAWorld", "build_world", "contradicts_for_a", "use_glossary"]
