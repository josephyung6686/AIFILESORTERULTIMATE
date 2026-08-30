# tests/p7/test_p7_composition.py
"""Done-means 12 asked of the RUN: is the posture the product STORES local-first?

`tests/p7/test_p7_defaults.py` proves W1's floor thoroughly -- that
`resolve_default_policy` fills every absent facet with its more redacting value,
that `assert_local_first` refuses a cloud starting mode, and that no reachable
stored state produces one. It proves all of it about `privacy.defaults`, and
`privacy.defaults` is reached by nothing a person runs.

`src/cli.py`'s `set_privacy_policy` builds the `Policy` by hand and writes
`redaction_settings={}`. So the record the product puts in force -- the one §8.4
says an audit names, the one §8.8 places inside the plan version -- states no
posture at all. Verified against a real run of the real command:

    sqlite> SELECT operation_mode, redaction_settings FROM privacy_policies;
    offline|{}

The mode is right. The data-minimizing half of §8.4's `must` is absent, and
`assert_local_first` -- the function whose whole job is to say so -- has never
been called by anything but a test.

**Why this is not merely cosmetic.** `display.display_policy` resolves an absent
facet through `MORE_REDACTING` at READ time, so a surface that goes through P7's
own door sees the floor and a person is not harmed today. What is missing is that
the floor is never WRITTEN, so it is not in the policy version, not in the
`policy_set` event's payload, and not in what any future reader of the row sees.
§8.4's posture is a claim the product makes and does not record.

This file drives `cli.main` rather than reaching into it, because the closure that
writes the policy is nested inside `cli.run` and cannot be called directly. One
run over three files takes about three seconds.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

from database_agent.db import open_database
from privacy.defaults import DefaultPostureViolation, assert_local_first
from privacy.policy import current_policy
from privacy.vocabulary import DISPLAY_FACETS

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402

#: Enough of a corpus for the chain to reach a frozen plan version, which is what
#: `set_privacy_policy` is keyed to. Two files that share a course and one that
#: does not, because a corpus the chain refuses never reaches the policy write.
CORPUS: dict[str, str] = {
    "Uni/phys1401-hw3.txt": "PHYS 1401 Homework 3\nDue 2026-03-04\nMechanics.\n",
    "Uni/phys1401-hw4.txt": "PHYS 1401 Homework 4\nDue 2026-03-11\nEnergy.\n",
    "lease.txt": "Lease agreement for 4B Maple Street\nTerm begins 2026-06-01\n",
}


def _real_run(tmp_path: Path):
    """Run the shipped command on a real folder and hand back its database.

    The same invocation a person types, through `cli.main`'s own argument parser,
    so nothing here can be right about a call the product does not make.
    """
    corpus = tmp_path / "corpus"
    for name, text in CORPUS.items():
        path = corpus / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    database = tmp_path / "plan.sqlite"
    exit_code = cli.main(
        [str(corpus), "--situation", "academic.coursework", "--label", "Columbia",
         "--database", str(database)], out=io.StringIO())
    assert exit_code == 0, "the run must reach a plan before its policy means anything"
    conn = open_database(database)
    plan_version = conn.execute(
        "SELECT plan_version FROM privacy_policies").fetchone()["plan_version"]
    policy = current_policy(conn, plan_version=plan_version)
    assert policy is not None, "the run wrote no policy at all"
    return policy


def test_the_posture_a_real_run_puts_in_force_is_local_first(tmp_path: Path):
    """§8.4's `must`, applied to the record the product actually wrote.

    Both halves. The mode must be one under which no content leaves the device,
    and every one of §8.4's five facets must be resolved to its more redacting
    value -- because `assert_local_first`'s own reason for refusing an unresolved
    facet is that "an unresolved facet is decided by whoever reads it", and a
    policy row is read by more than one reader.
    """
    assert_local_first(_real_run(tmp_path))


test_the_posture_a_real_run_puts_in_force_is_local_first = pytest.mark.xfail(
    strict=True, raises=DefaultPostureViolation,
    reason="measured 2026-08-31 against a real run: `src/cli.py`'s "
           "`set_privacy_policy` writes `redaction_settings={}`, so all five of "
           "§8.4's facets are unresolved in the stored policy and "
           "`assert_local_first` refuses it. XPASSes -- and fails the suite, "
           "forcing this marker off -- the day the composition root resolves the "
           "policy through `privacy.defaults.effective_policy`.",
)(test_the_posture_a_real_run_puts_in_force_is_local_first)


def test_the_stored_policy_names_the_posture_rather_than_leaving_it_to_a_reader(
        tmp_path: Path):
    """The half a person could actually read: does the record say what it is?

    Separate from the assertion above, which is P7's `must`. This is §8.2's
    question -- the policy version travels on every decision and an audit reads it
    back -- and the answer today is an empty object. `display_policy` filling the
    floor at read time is what keeps that from harming anyone; it is not what
    makes the record true.
    """
    assert set(_real_run(tmp_path).redaction_settings) == set(DISPLAY_FACETS)


test_the_stored_policy_names_the_posture_rather_than_leaving_it_to_a_reader = (
    pytest.mark.xfail(
        strict=True,
        reason="the stored policy's `redaction_settings` is `{}` on every run, so "
               "the record states none of §8.4's five facets. XPASSes the day the "
               "composition root writes the floor it claims to run under.",
    )(test_the_stored_policy_names_the_posture_rather_than_leaving_it_to_a_reader))


def test_this_file_is_really_reading_the_run_and_the_guard_can_really_refuse(
        tmp_path: Path):
    """The falsifying twin, and it has to catch both ways this file stops measuring.

    A `_real_run` that quietly returned a hand-built `Policy` would make the two
    xfails above report the composition root while measuring a fixture, and an
    `assert_local_first` that had stopped being able to raise would make them
    report a gap that had closed. So this pins both: the policy really came from
    the command's own database and carries the mode `cli.py` chose, and the guard
    really refuses a posture §8.4 forbids.

    The refusal is anchored to a CLOUD MODE and not to the unresolved facets the
    xfails are about. A twin anchored to the gap would break the day the gap
    closes, which would make this file punish its own finding being fixed.
    """
    from dataclasses import replace

    policy = _real_run(tmp_path)
    assert policy.operation_mode == cli.OPERATION_MODE
    assert policy.plan_version.startswith("version_"), (
        "the policy must be keyed to the plan version the run actually froze")
    with pytest.raises(DefaultPostureViolation):
        assert_local_first(replace(policy, operation_mode="cloud_assisted",
                                   redaction_settings={
                                       facet: "redacted" for facet in DISPLAY_FACETS}))
