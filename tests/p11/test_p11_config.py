"""Limits are read; thresholds are injected; neither is ever guessed."""
from __future__ import annotations

import pytest

from database_agent.budget import CEILING_KEYS, set_ceiling

from placement.config import (
    CEILINGS, ConfigurationRequired, PlacementLimits, SupportPolicy,
    placement_limits, require_policy,
)

POLICY = SupportPolicy(policy_id="fixture-v1", support_scale_max=1.0,
                       minimum_support_threshold=0.5, margin_threshold=0.2)


def _set_all(conn, value=8):
    for key in CEILINGS.values():
        set_ceiling(conn, key, value)


def test_every_ceiling_p11_reads_is_one_p1_already_publishes():
    # A key P1 does not know is a policy P11 authored, and `set_ceiling` raises
    # on one, so this is the compile-time half of the same rule.
    assert set(CEILINGS.values()) <= set(CEILING_KEYS)
    assert len(CEILINGS) == 7


def test_an_absent_ceiling_refuses_rather_than_defaulting(p11_conn):
    with pytest.raises(ConfigurationRequired) as excinfo:
        placement_limits(p11_conn)
    assert "placement." in str(excinfo.value) or "model." in str(excinfo.value)


def test_a_non_positive_ceiling_refuses(p11_conn):
    _set_all(p11_conn)
    set_ceiling(p11_conn, "placement.max_retrieved_neighbors", 0)
    with pytest.raises(ConfigurationRequired):
        placement_limits(p11_conn)


def test_configured_ceilings_read_back(p11_conn):
    _set_all(p11_conn, 12)
    limits = placement_limits(p11_conn)
    assert isinstance(limits, PlacementLimits)
    assert limits.max_retrieved_neighbors == 12
    assert limits.max_residual_files_per_batch == 12


def test_a_missing_support_policy_refuses(p11_conn):
    with pytest.raises(ConfigurationRequired):
        require_policy(None)


def test_the_margin_predicate_is_the_policys_and_carries_no_default():
    assert POLICY.margin_predicate(0.9, 0.5) is True
    assert POLICY.margin_predicate(0.9, 0.8) is False
    with pytest.raises(ConfigurationRequired):
        SupportPolicy(policy_id="", support_scale_max=1.0,
                      minimum_support_threshold=0.5, margin_threshold=0.2)
    with pytest.raises(ConfigurationRequired):
        SupportPolicy(policy_id="bad", support_scale_max=1.0,
                      minimum_support_threshold=1.5, margin_threshold=0.2)


def test_the_policy_id_is_recordable_so_a_changed_threshold_is_auditable():
    # SPEC:802-804: both must be recorded on every decision so a changed
    # threshold is auditable and replayable.
    assert POLICY.policy_id
    assert POLICY.minimum_support_threshold == 0.5
    assert POLICY.margin_threshold == 0.2


def test_no_module_under_placement_binds_a_bare_number(p11_conn):
    # By runtime introspection, not text search: a text search matches comments,
    # and scanning text for a token has produced a false result on this project.
    import importlib
    import pkgutil

    import placement

    allowed = {0, 1}
    offenders = []
    for info in pkgutil.iter_modules(placement.__path__):
        module = importlib.import_module(f"placement.{info.name}")
        for name, value in vars(module).items():
            if name.startswith("_") or not isinstance(value, (int, float)):
                continue
            if isinstance(value, bool) or value in allowed:
                continue
            offenders.append((info.name, name, value))
    assert offenders == []
