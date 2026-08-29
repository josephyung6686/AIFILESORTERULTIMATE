# tests/p10/test_p10_config.py
"""P10 Task 3 — every limit is read or injected; none is chosen here.

SPEC open questions 1 and 2 are open on purpose: §5.7 forbids exceeding
"practical depth limits" and §5.9 asks for a warning on "a large number of tiny
folders", and the design states no number for either. A default here would run a
user's corpus under a bound nobody chose, with nothing to say so.
"""
from __future__ import annotations

import pytest

from database_agent.budget import set_ceiling
from tree_design.config import CEILINGS, ConfigurationRequired, tree_limits

INJECTED = dict(
    excessive_depth_warning=6,
    tiny_folder_max_files=3,
    tiny_folder_count_warning=12,
    materially_improves_retrieval=lambda preview: None,
)


def test_the_three_ceilings_come_from_p1s_published_keys(conn):
    """Three since 2026-08-29. `00`:256 names two numbers -- "Maximum folder
    proposals and maximum depth" -- and P1 published one key for both, which made
    a depth limit big enough for `00`:78's own five-level tree into a picker
    offering five options per branch."""
    set_ceiling(conn, "tree.max_folder_proposals", 9)
    set_ceiling(conn, "tree.max_depth", 5)
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    limits = tree_limits(conn, **INJECTED)
    assert limits.max_folder_proposals == 9
    assert limits.max_depth == 5
    assert limits.max_dossier_tokens == 4000
    assert set(CEILINGS.values()) == {
        "tree.max_folder_proposals", "tree.max_depth",
        "model.max_dossier_tokens_per_call",
    }


def test_an_absent_ceiling_refuses_rather_than_defaulting(conn):
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    with pytest.raises(ConfigurationRequired) as excinfo:
        tree_limits(conn, **INJECTED)
    assert "tree.max_folder_proposals" in str(excinfo.value)


def test_an_absent_depth_ceiling_refuses_too(conn):
    """The negative twin of the split: two keys means two ways to be unset, and
    a depth limit nobody chose must refuse exactly as the breadth one does."""
    set_ceiling(conn, "tree.max_folder_proposals", 9)
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    with pytest.raises(ConfigurationRequired) as excinfo:
        tree_limits(conn, **INJECTED)
    assert "tree.max_depth" in str(excinfo.value)


def test_a_non_positive_ceiling_is_refused(conn):
    set_ceiling(conn, "tree.max_folder_proposals", 0)
    set_ceiling(conn, "tree.max_depth", 5)
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    with pytest.raises(ConfigurationRequired):
        tree_limits(conn, **INJECTED)


def test_every_59_threshold_is_mandatory_and_has_no_default(conn):
    set_ceiling(conn, "tree.max_folder_proposals", 9)
    set_ceiling(conn, "tree.max_depth", 5)
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    for missing in ("excessive_depth_warning", "tiny_folder_max_files",
                    "tiny_folder_count_warning"):
        supplied = {**INJECTED, missing: None}
        with pytest.raises(ConfigurationRequired) as excinfo:
            tree_limits(conn, **supplied)
        assert missing in str(excinfo.value)


def test_the_retrieval_gain_test_is_injected_and_may_answer_unknown(conn):
    """§5.9 wants a flattening recommendation "when a dimension does not
    materially improve retrieval" and states no test. `None` is the honest
    answer until one is authored, and it must not round to False."""
    set_ceiling(conn, "tree.max_folder_proposals", 9)
    set_ceiling(conn, "tree.max_depth", 5)
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    with pytest.raises(ConfigurationRequired):
        tree_limits(conn, **{**INJECTED, "materially_improves_retrieval": None})
    limits = tree_limits(conn, **INJECTED)
    assert limits.materially_improves_retrieval(object()) is None


def test_no_module_in_the_package_holds_a_numeric_literal_beyond_zero_and_one():
    """P9's precedent, applied to P10: a threshold in source is a policy an
    author chose. Introspection, not text search — a text search matches
    comments and docstrings and has produced a false result nine times here.

    `fixtures.py` (Task 17) is the ONLY exemption, and it is stated rather than
    silent: its sibling `ordinal`s run 0..9 by construction, which are positions
    in a fixed example tree and not limits any check consults. Every other
    module holds no integer beyond 0 and 1 — which is what makes one exemption
    safe rather than a hole. `tests/p10/test_p10_no_invention.py` carries the
    same test and the same exemption; if either is relaxed further, the other
    stops being a ratchet."""
    import ast
    from pathlib import Path

    src = Path(__file__).resolve().parents[2] / "src" / "tree_design"
    offenders = []
    for path in sorted(src.glob("*.py")):
        if path.name == "fixtures.py":
            continue
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant):
                continue
            if isinstance(node.value, bool) or not isinstance(node.value, int):
                continue
            if node.value in (0, 1):
                continue
            offenders.append(f"{path.name}:{node.lineno} {node.value}")
    assert offenders == []
