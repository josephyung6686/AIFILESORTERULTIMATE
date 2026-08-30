# tests/p10/test_p10_composition.py
"""P10 Task 3, asked of the RUN instead of of the module.

`tests/p10/test_p10_config.py` proves `tree_limits` refuses an absent ceiling and
reads a present one. It proves it against ceilings the test itself sets, which is
the right scope for a part's own suite and is also why it cannot see the defect
this file is for: **no ceiling `tree_design.config.CEILINGS` names is written by
anything a person runs.**

`src/cli.py` seeds `budget_ceilings` from `placement.config.CEILINGS` -- P11's
seven keys -- and calls that "P1's ceilings". `tree.max_folder_proposals` and
`tree.max_depth`, the two keys P1 split apart on 2026-08-29 *for P10*, are in no
loop. So `tree_limits(conn, ...)` refuses on every real database, and P10 runs
instead on a `TreeLimits` the composition root builds by hand -- which never
passes through `_positive`, so a zero, a `False` or a `None` would be accepted by
the product and refused only by the tests.

This is the composition census (`tests/integration/test_composition_root.py`)
asked from one part's side: not "is the symbol reachable" but "does the run put
this part in a state where its own reader works".

The same instrument catches the second half, which no part's suite can see at all:
`model.max_dossier_tokens_per_call` is ONE §8.6 key that P9, P10 and P11 all read,
and the run currently holds two different answers to it -- `8` in the ledger a
replay reads, `4000` in the two limit objects `cli.py` builds by hand.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

from database_agent.budget import BUDGET_DDL, get_ceiling
from database_agent.db import open_database
from tree_design.config import CEILINGS, ConfigurationRequired, tree_limits

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402

#: §5.9's three thresholds and its flattening test, as `src/cli.py` chooses them.
#: These have no P1 ceiling key -- `tree_design/config.py` says so in as many
#: words -- so they are injected, and this mirrors the composition root's values
#: rather than inventing its own: a test that injected different numbers would
#: pass on limits the product never runs under.
CLI_THRESHOLDS = dict(
    excessive_depth_warning=4,
    tiny_folder_max_files=1,
    tiny_folder_count_warning=2,
    materially_improves_retrieval=lambda option: True,
)


def _bootstrapped(tmp_path: Path):
    """A database in exactly the state a person's run leaves it in."""
    conn = open_database(tmp_path / "agent.sqlite")
    cli._bootstrap(conn)
    return conn


def test_the_bootstrap_writes_every_ceiling_p10_declares_it_reads(tmp_path: Path):
    """The three keys in `CEILINGS` are P10's published reads. A run writes them.

    A ceiling absent from the ledger is not a smaller ceiling -- it is a part that
    cannot start, and `tree_limits` says so by refusing. That refusal has never
    fired in front of a person only because nothing has ever called it.
    """
    conn = _bootstrapped(tmp_path)
    absent = sorted(key for key in CEILINGS.values()
                    if get_ceiling(conn, key) is None)
    assert not absent, (
        f"P10 declares it reads {sorted(CEILINGS.values())}; a person's run writes "
        f"none of {absent}, so `tree_limits` refuses on every real database and the "
        f"limits P10 actually runs under are built by hand in the composition root, "
        f"skipping `_positive` entirely")


test_the_bootstrap_writes_every_ceiling_p10_declares_it_reads = pytest.mark.xfail(
    strict=True,
    reason="`src/cli.py:_bootstrap` seeds `placement.config.CEILINGS` only, so "
           "`tree.max_folder_proposals` and `tree.max_depth` are written by nothing "
           "a person runs. XPASSes -- and fails the suite, forcing this marker off "
           "-- the day the composition root seeds P10's two keys.",
)(test_the_bootstrap_writes_every_ceiling_p10_declares_it_reads)


def test_p10_can_read_its_own_limits_after_a_real_bootstrap(tmp_path: Path):
    """The whole point of `tree_limits`: the run is under limits it validated.

    Distinct from the test above, which asks whether the keys are present. This
    asks whether the READ succeeds, which is the question `cli.py` answers today
    by not asking it -- it hands the pipeline a hand-built `TreeLimits` instead.
    """
    conn = _bootstrapped(tmp_path)
    limits = tree_limits(conn, **CLI_THRESHOLDS)
    assert limits.max_folder_proposals > 0
    assert limits.max_depth > 0
    assert limits.max_dossier_tokens > 0


test_p10_can_read_its_own_limits_after_a_real_bootstrap = pytest.mark.xfail(
    strict=True, raises=ConfigurationRequired,
    reason="`tree_limits` refuses on every database a person's run produces, "
           "because the run writes neither of P10's two ceilings. XPASSes the day "
           "the composition root calls this reader instead of building `TreeLimits` "
           "by hand.",
)(test_p10_can_read_its_own_limits_after_a_real_bootstrap)


def test_the_run_holds_one_answer_to_the_one_ceiling_three_parts_share(
        tmp_path: Path):
    """`model.max_dossier_tokens_per_call` is §8.6's, and it is read three times.

    P9, P10 and P11 all name this one key. P11 reads it from the ledger and gets
    `CEILING_VALUE`; P9 and P10 are handed limit objects the composition root
    builds by hand, carrying a different number. Two answers to one published
    ceiling is not a smaller budget -- it is a run whose §8.5 replay reads a
    ceiling no part obeyed, and neither number is wrong in a way any part's own
    suite can see, because each part is internally consistent.

    Asserted against `GROUPING_LIMITS` rather than `TREE_LIMITS` on purpose: P9's
    object is untouched by anything P10 does, so this stays a measurement of the
    disagreement and not of P10's own fix.
    """
    conn = _bootstrapped(tmp_path)
    assert (get_ceiling(conn, "model.max_dossier_tokens_per_call")
            == cli.GROUPING_LIMITS.max_dossier_tokens)


test_the_run_holds_one_answer_to_the_one_ceiling_three_parts_share = pytest.mark.xfail(
    strict=True,
    reason="measured 2026-08-31: the ledger a run writes says 8 and the two limit "
           "objects `cli.py` builds by hand say 4000, for one §8.6 key. XPASSes the "
           "day the composition root writes the number it actually runs under.",
)(test_the_run_holds_one_answer_to_the_one_ceiling_three_parts_share)


def test_this_file_is_measuring_the_real_composition_root(tmp_path: Path):
    """The falsifying twin, and it has to catch the way THIS census stops measuring.

    Every assertion above reads a ceiling out of a database `cli._bootstrap` filled.
    A `_bootstrap` that silently stopped seeding anything, or a `get_ceiling` that
    returned a number for every key, would make all three report whatever the
    marker already claims and measure nothing. So this pins both directions: a key
    the run really does write must read back, and a key nothing writes must read
    back `None`.

    Both directions are anchored to `placement.max_retrieved_neighbors` and NOT to
    one of P10's two. A twin anchored to the gap would break the day the gap closes,
    which would make this file punish its own finding being fixed. The absent side
    is a database with the ceiling TABLE and no bootstrap, which is the one state
    that isolates `_bootstrap` as the thing being measured -- an unpublished key
    cannot serve, because `get_ceiling` refuses one outright.
    """
    anchor = "placement.max_retrieved_neighbors"
    assert get_ceiling(_bootstrapped(tmp_path), anchor) is not None
    untouched = open_database(tmp_path / "untouched.sqlite")
    untouched.executescript(BUDGET_DDL)
    assert get_ceiling(untouched, anchor) is None
