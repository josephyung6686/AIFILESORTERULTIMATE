# tests/p9/test_p9_seeds.py
"""P9 Task 4 — only legal seeds, and no numeric fallback anywhere.

A seed is where a group's claim to exist starts, so the evidence bar for one is
narrower than P6's proposal bar. `proposal_eligible` is a CANDIDATE read surface,
not the anchor authority: it includes `llm_supported` and `user_confirmed`, and
neither may automatically anchor a group.

`user_confirmed` staying out is deliberate and is the subtle one. It is the
strongest state P6 has, and it still does not anchor: user intent enters through
the explicit user-seed channel, where it carries a decision the user actually
made, rather than by silently widening the evidence bar so that any confirmed
fact starts a group.

`grouping_limits` ships no default. Every ceiling is read from P1 and a missing
or non-positive one is `ConfigurationRequired` — a numeric fallback would be P9
authoring a policy.
"""
from __future__ import annotations

import pytest

from database_agent.budget import set_ceiling
from database_agent.db import create_schema
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import record_observation, record_run
from facts.fields import create_fields
from facts.file_facts import write_fact
from facts.values import ensure_value
from grouping.config import ConfigurationRequired, GroupingLimits, grouping_limits
from grouping.seeds import Seed, UserSeed, seeds_for_file
from grouping.vocabulary import (
    STRONGLY_IDENTIFIED_FILE,
    STRUCTURAL_FAMILY,
    USER_CREATED_STARTING_POINT,
    VALIDATED_SHARED_FACT,
)

FILE_ID = "file-1"
CONTENT_HASH = "a" * 64
OBSERVED_AT = "2026-08-26T00:00:00Z"

CEILINGS = {
    "grouping.max_retrieved_neighbors": 40,
    "grouping.max_local_graph_neighborhood": 60,
    "grouping.max_candidate_cluster_size": 25,
    "model.max_dossier_tokens_per_call": 4000,
}


@pytest.fixture()
def seed_conn(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_fields(conn)
    for key, value in CEILINGS.items():
        set_ceiling(conn, key, value)
    record_run(conn, ExtractionRun(
        run_id="run-1", file_id=FILE_ID, content_hash=CONTENT_HASH,
        extractor_name="fixture.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=OBSERVED_AT, finished_at=OBSERVED_AT,
    ))
    return conn


def _observe(conn, raw_value: str) -> str:
    location = Location(
        zone="heading",
        container_path=(Segment(kind="page", index=1),),
        text_span=TextSpan(start=0, end=len(raw_value)),
    )
    observation = Observation(
        file_id=FILE_ID, content_hash=CONTENT_HASH, extractor_name="fixture.text",
        extractor_version="1.0.0", source_type="text_document",
        raw_value=raw_value, location=location, occurrence_count=1,
        observed_at=OBSERVED_AT, reliability="direct", run_id="run-1",
    )
    record_observation(conn, observation)
    return observation.observation_key


def _fact(conn, *, field_key: str, value: str, reliability_state: str,
          origin: str = "deterministic_extractor") -> str:
    key = _observe(conn, value)
    value_id = ensure_value(
        conn, field_key=field_key, canonical_value=value,
        first_evidence_ref=key, origin="automatic",
    )
    write_fact(
        conn, file_id=FILE_ID, content_hash=CONTENT_HASH, field_key=field_key,
        value_id=value_id, reliability_state=reliability_state, origin=origin,
        evidence_refs=(key,), cache_key=f"sha256:{field_key}-{reliability_state}",
        active=True,
    )
    return key


def _no_user_seed(_file_id: str, _content_hash: str) -> UserSeed | None:
    return None


def _seeds(conn, user_seed_for=_no_user_seed) -> tuple[Seed, ...]:
    return seeds_for_file(
        conn, file_id=FILE_ID, content_hash=CONTENT_HASH,
        user_seed_for=user_seed_for,
    )


# --- what may seed --------------------------------------------------------------


@pytest.mark.parametrize("reliability_state", ["direct", "validated"])
def test_a_strongly_identified_fact_seeds(seed_conn, reliability_state):
    _fact(seed_conn, field_key="subject", value="PHYS1401",
          reliability_state=reliability_state)
    seeds = _seeds(seed_conn)
    assert [seed.seed_kind for seed in seeds] == [STRONGLY_IDENTIFIED_FILE]
    assert seeds[0].field_key == "subject"
    assert seeds[0].value == "PHYS1401"
    assert seeds[0].observation_key


def test_a_photo_event_fact_seeds_as_a_validated_shared_fact(seed_conn):
    from facts.read_surface import EVENT_FIELD

    _fact(seed_conn, field_key=EVENT_FIELD, value="event-2026-08-01",
          reliability_state="validated")
    kinds = {seed.seed_kind for seed in _seeds(seed_conn)}
    assert VALIDATED_SHARED_FACT in kinds


def test_a_version_family_whose_anchor_is_validated_seeds_as_structural(seed_conn):
    from facts.read_surface import VERSION_FAMILY_FIELD

    _fact(seed_conn, field_key=VERSION_FAMILY_FIELD, value="family-1",
          reliability_state="validated")
    kinds = {seed.seed_kind for seed in _seeds(seed_conn)}
    assert STRUCTURAL_FAMILY in kinds


def test_an_explicit_user_seed_seeds_whatever_the_facts_say(seed_conn):
    def user_seed_for(file_id: str, content_hash: str) -> UserSeed:
        return UserSeed(
            file_id=file_id, content_hash=content_hash,
            basis="the user made this folder the start of a group",
            decided_at=OBSERVED_AT,
        )

    seeds = _seeds(seed_conn, user_seed_for=user_seed_for)
    assert [seed.seed_kind for seed in seeds] == [USER_CREATED_STARTING_POINT]
    assert seeds[0].basis


# --- what may not ---------------------------------------------------------------


@pytest.mark.parametrize(
    "reliability_state", ["possible", "llm_supported", "user_confirmed"],
)
def test_a_fact_below_the_anchor_bar_never_seeds(seed_conn, reliability_state):
    """`llm_supported` is retrieval-eligible; neither it nor `user_confirmed`
    anchors. A model confirming its own earlier guess is the failure this stops."""
    origin = (
        "llm_interpretation" if reliability_state == "llm_supported"
        else "deterministic_extractor"
    )
    _fact(seed_conn, field_key="subject", value="PHYS1401",
          reliability_state=reliability_state, origin=origin)
    assert _seeds(seed_conn) == ()


def test_a_user_confirmed_fact_needs_the_explicit_user_seed_channel(seed_conn):
    """User intent enters where the user made a decision, not by widening the bar."""
    _fact(seed_conn, field_key="subject", value="PHYS1401",
          reliability_state="user_confirmed")
    assert _seeds(seed_conn) == ()

    def user_seed_for(file_id: str, content_hash: str) -> UserSeed:
        return UserSeed(
            file_id=file_id, content_hash=content_hash,
            basis="the user confirmed this course and started a group from it",
            decided_at=OBSERVED_AT,
        )

    assert [seed.seed_kind for seed in _seeds(seed_conn, user_seed_for)] == [
        USER_CREATED_STARTING_POINT,
    ]


def test_a_bounded_session_fact_never_seeds(seed_conn):
    """§3.9: a download session is not a basis for automatic propagation."""
    from facts.read_surface import DOWNLOAD_SESSION_FIELD

    _fact(seed_conn, field_key=DOWNLOAD_SESSION_FIELD, value="session-1",
          reliability_state="possible")
    assert _seeds(seed_conn) == ()


def test_a_file_with_no_facts_at_all_seeds_nothing(seed_conn):
    assert _seeds(seed_conn) == ()


def test_seeds_are_deterministic_and_ordered(seed_conn):
    from facts.read_surface import EVENT_FIELD

    _fact(seed_conn, field_key="subject", value="PHYS1401",
          reliability_state="direct")
    _fact(seed_conn, field_key=EVENT_FIELD, value="event-1",
          reliability_state="validated")
    assert _seeds(seed_conn) == _seeds(seed_conn)
    assert len(_seeds(seed_conn)) == 2


def test_p9_spells_no_domain_field_name(seed_conn):
    """P6 owns the field catalogue. A field name in P9 is a second catalogue."""
    import ast
    import pathlib

    import grouping

    root = pathlib.Path(grouping.__file__).resolve().parent
    banned = {"subject", "target_school", "instructor", "term",
              "work_type", "project", "institution", "school"}
    offenders = []
    for path in sorted(root.glob("*.py")):
        if path.name == "fixtures.py":
            continue  # fixtures are the design's own worked examples
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Constant) and node.value in banned:
                offenders.append(f"{path.name}:{node.lineno}:{node.value}")
    assert offenders == [], offenders


# --- the limits adapter ---------------------------------------------------------


def _limits(conn, **overrides) -> GroupingLimits:
    values = dict(generic_hub_frequency=25, minimum_independent_anchors=2,
                  max_excerpt_characters=240)
    values.update(overrides)
    return grouping_limits(conn, **values)


def test_grouping_limits_reads_the_four_live_ceilings(seed_conn):
    limits = _limits(seed_conn)
    assert limits.max_retrieved_neighbors == 40
    assert limits.max_graph_nodes == 60
    assert limits.max_candidate_members == 25
    assert limits.max_dossier_tokens == 4000
    assert limits.generic_hub_frequency == 25
    assert limits.minimum_independent_anchors == 2


@pytest.mark.parametrize("key", sorted(CEILINGS))
def test_a_missing_ceiling_is_configuration_required(seed_conn, key):
    seed_conn.execute("DELETE FROM budget_ceilings WHERE key = ?", (key,))
    with pytest.raises(ConfigurationRequired) as excinfo:
        _limits(seed_conn)
    assert key in str(excinfo.value)


@pytest.mark.parametrize("value", [0, -1])
def test_a_non_positive_ceiling_is_configuration_required(seed_conn, value):
    seed_conn.execute(
        "UPDATE budget_ceilings SET value = ? WHERE key = ?",
        (value, "grouping.max_retrieved_neighbors"),
    )
    with pytest.raises(ConfigurationRequired):
        _limits(seed_conn)


@pytest.mark.parametrize(
    "name", ["generic_hub_frequency", "minimum_independent_anchors"],
)
@pytest.mark.parametrize("value", [None, 0, -1])
def test_a_missing_oq1_value_is_configuration_required(seed_conn, name, value):
    """The two open-question numbers are injected. P9 ships neither."""
    with pytest.raises(ConfigurationRequired):
        _limits(seed_conn, **{name: value})


def test_p9_adds_no_fifth_ceiling_key_and_no_default():
    import inspect

    from database_agent.budget import CEILING_KEYS
    from grouping import config

    used = {
        value
        for name, member in vars(config).items()
        if name.isupper() and isinstance(member, (tuple, dict))
        for value in (member if isinstance(member, tuple) else member.values())
        if isinstance(value, str)
    }
    assert used <= set(CEILING_KEYS), used - set(CEILING_KEYS)
    for parameter in inspect.signature(grouping_limits).parameters.values():
        if parameter.name == "conn":
            continue
        assert parameter.default is inspect.Parameter.empty, parameter.name


def test_grouping_limits_holds_no_numeric_literal_as_a_fallback():
    import ast
    import pathlib

    from grouping import config

    tree = ast.parse(pathlib.Path(config.__file__).read_text())
    literals = [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, int)
        and not isinstance(node.value, bool)
        and node.value not in (0, 1)
    ]
    assert literals == [], literals
