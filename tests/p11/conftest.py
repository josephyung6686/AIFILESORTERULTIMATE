"""A real P1 database with P11's tables. No mock, no in-memory stand-in."""
from __future__ import annotations

import pytest

from database_agent.budget import all_ceilings
from database_agent.db import create_schema
from eval_harness.run import ANALYSIS_TIERS, record_version_tuple, start_run
from eval_harness.store import create_eval_schema
from facts.fields import create_fields
from grouping.schema import create_grouping_schema

from privacy.schema import create_privacy_schema

from placement.schema import create_placement_schema

FIXED_CLOCK = "2026-08-27T00:00:00Z"


@pytest.fixture()
def p11_conn(conn):
    # P9's tables are created because P11 reads them for real (G-P9 is closed):
    # `group_state_as_of` and `memberships_for_group` query `group_acceptance`
    # and `memberships`, and a test against an absent table would prove nothing.
    create_schema(conn)
    create_eval_schema(conn)
    create_grouping_schema(conn)
    # P6's field catalogue, for the same reason as P9's tables: §6.3 asks
    # `is_destination_eligible` per fact field and P6 raises on a field the
    # catalogue does not carry, so a test against an absent table would prove
    # nothing about which fields may build a folder. `create_fields` is P6's
    # only writer of this table and is idempotent.
    create_fields(conn)
    # P7's tables, for the same reason as P9's: §8.4's gate is a real read of
    # `classifications` and `policies`, and `privacy_state_for` blocking because a
    # table is missing would prove nothing about blocking because a file is
    # unclassified.
    create_privacy_schema(conn)
    create_placement_schema(conn)
    return conn


@pytest.fixture()
def p11_version_tuple(p11_conn) -> str:
    """P2's seven axes. `placement_scorer_version` is already one of them, so a
    changed support policy reads as a version delta and not as a mystery diff."""
    return record_version_tuple(
        p11_conn, extractor_versions={}, graph_algorithm_version="1",
        prompt_fingerprint="fp-canonical", model_identifier="fixture-model",
        template_library_version="1", placement_scorer_version="fixture-v1",
        analysis_tiers_enabled=list(ANALYSIS_TIERS))


@pytest.fixture()
def p2_run_id(p11_conn, p11_version_tuple) -> str:
    """A replay run. There is no live run kind: P2 measures replays, shadows and
    adversarial runs, and P11 emits stage output in those only."""
    return start_run(
        p11_conn, bundle_id="bundle-p11", run_kind="replay",
        version_tuple_ref=p11_version_tuple,
        budget_ceilings=all_ceilings(p11_conn),
        run_settings={"model_enabled": False, "embeddings_enabled": False},
        pinned_plan_id="plan", pinned_plan_version="plan-1")
