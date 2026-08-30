"""A real P1-P11 database with P13's tables. No mock, no in-memory stand-in.

Every part whose records P13 projects is created, for the reason P11's conftest
gives for creating P9's: a read against an absent table proves nothing about the
read, only about the table. P13 projects more parts than any other, so it creates
more of them.
"""
from __future__ import annotations

import pytest

from database_agent.budget import all_ceilings
from database_agent.db import create_schema
from eval_harness.run import ANALYSIS_TIERS, record_version_tuple, start_run
from eval_harness.store import create_eval_schema
from facts.fields import create_fields
from grouping.schema import create_grouping_schema
from placement.schema import create_placement_schema
from privacy.schema import create_privacy_schema

from review_surface.schema import create_review_schema

FIXED_CLOCK = "2026-08-29T00:00:00Z"
COMPONENT_VERSION = "p13-fixture-1"
USER = "jy"


@pytest.fixture()
def p13_conn(conn):
    create_schema(conn)
    create_eval_schema(conn)
    create_grouping_schema(conn)
    create_fields(conn)
    create_privacy_schema(conn)
    create_placement_schema(conn)
    create_review_schema(conn)
    return conn


@pytest.fixture()
def p13_version_tuple(p13_conn) -> str:
    return record_version_tuple(
        p13_conn, extractor_versions={}, graph_algorithm_version="1",
        prompt_fingerprint="fp-canonical", model_identifier="fixture-model",
        template_library_version="1", placement_scorer_version="fixture-v1",
        analysis_tiers_enabled=list(ANALYSIS_TIERS))


@pytest.fixture()
def p13_run_id(p13_conn, p13_version_tuple) -> str:
    """A replay run. P13 emits no stage output, but every surface must be
    renderable from a bundle (Done-means 23), and that needs a run to hang on."""
    return start_run(
        p13_conn, bundle_id="bundle-p13", run_kind="replay",
        version_tuple_ref=p13_version_tuple,
        budget_ceilings=all_ceilings(p13_conn),
        run_settings={"model_enabled": False, "embeddings_enabled": False},
        pinned_plan_id="plan", pinned_plan_version="plan-1")
