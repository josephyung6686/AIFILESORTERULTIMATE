# src/privacy/defaults.py
"""W1 — §8.4's local-first `must`, made mechanical.

§8.4: "The default posture must therefore be local-first and data-minimizing." The
design names no install mode, so P7 does not pick one: `install_mode` is a required
keyword and the only values it accepts are the two under which no content leaves the
device. `src/privacy/` therefore holds NO default mode, which is what keeps SPEC
Open question 11 -- which of `offline` and `local_model` ships -- open by
construction rather than by discipline, and what makes `hybrid` and `cloud_assisted`
unreachable as a starting state through this door.

Both halves of the `must` are here.

**Local-first** is `LOCAL_FIRST_MODES`: §8.4's "Fully offline mode: No content leaves
the device" and "Local-model mode: Local extraction plus a user-installed local LLM
for eligible dossiers." The other two both permit a cloud model without the user
having asked for one.

**Data-minimizing** is `MORE_REDACTING`. §8.4's own example settles the direction: "A
summary such as '11 protected identity records' may be safe to show, while a visible
list of passport filenames on a shared screen may not be." The aggregate is the
default and the expansion is the user's act, so every facet the design leaves
configurable resolves to `redacted`, nothing is granted, and nothing is permitted to
move automatically.

**The floor binds the DEFAULT, never the choice.** §8.4: either cloud mode "remains a
legitimate mode the user may choose; neither may be what they find on install." So
`resolve_default_policy` returns a stored `cloud_assisted` policy unchanged, and
`assert_local_first` on that same policy raises. Two questions, two functions.

This module reads no file, no environment variable and no build flag. That is not a
style preference: Done-means 12's negative half names "build flag, packaged
configuration file, or first-run flow", and a module that cannot reach one cannot be
handed a mode by one.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from dataclasses import replace
from types import MappingProxyType

from privacy.policy import REDACTED, Policy, UNSET_POLICY_VERSION, current_policy
from privacy.vocabulary import DISPLAY_FACETS, check_mode

#: §8.4's two local modes, named once and validated against Task 2's vocabulary at
#: import so neither can drift into a second spelling.
OFFLINE = check_mode("offline")
LOCAL_MODEL = check_mode("local_model")

#: The floor. NOT a default: the caller names which of the two its build ships.
LOCAL_FIRST_MODES: tuple[str, str] = (OFFLINE, LOCAL_MODEL)

#: Per facet, the more redacting of §8.4's two values. Five facets, one value.
MORE_REDACTING: Mapping[str, str] = MappingProxyType(
    {facet: REDACTED for facet in DISPLAY_FACETS})


class DefaultPostureViolation(Exception):
    """A starting state §8.4's `must` forbids: a cloud mode, or a facet left shown."""


def _check_install_mode(install_mode: str) -> str:
    """A load error and a posture violation are different failures (Task 2, W1)."""
    check_mode(install_mode)
    if install_mode not in LOCAL_FIRST_MODES:
        raise DefaultPostureViolation(
            f"{install_mode!r} permits a cloud model without the user having asked "
            f"for one; §8.4's default posture must be local-first, so the install "
            f"default is one of {LOCAL_FIRST_MODES!r}. Either remains a mode the "
            f"user may choose."
        )
    return install_mode


def resolve_default_policy(stored: Policy | None, *, install_mode: str,
                           plan_version: str, set_at: str) -> Policy:
    """The policy in force, with everything nobody chose resolved to the floor.

    `install_mode` has no default. A build that forgets to name one does not start.
    """
    _check_install_mode(install_mode)
    if stored is None:
        return Policy(
            policy_version=UNSET_POLICY_VERSION,
            operation_mode=install_mode,
            consent_grants=(),
            redaction_settings=dict(MORE_REDACTING),
            automatic_move_permissions={},
            plan_version=plan_version,
            set_at=set_at,
        )
    # The mode is the user's and is not touched. An ABSENT facet is filled; a facet
    # the user set survives -- overwriting it would be the product changing a choice
    # behind their back (§8.8).
    return replace(stored, redaction_settings={**MORE_REDACTING,
                                               **stored.redaction_settings})


def effective_policy(conn: sqlite3.Connection, *, plan_version: str,
                     install_mode: str, set_at: str) -> Policy:
    """`current_policy` with the floor applied. The one composition the gate calls."""
    return resolve_default_policy(
        current_policy(conn, plan_version=plan_version),
        install_mode=install_mode, plan_version=plan_version, set_at=set_at)


def assert_local_first(policy: Policy) -> None:
    """Raise unless this is a posture a user may arrive at without choosing it.

    Applied to a fresh-install or migrated-from-nothing resolution. NOT applied to a
    policy the user set: §8.4 offers all four modes as choices and only constrains
    the default.
    """
    if policy.operation_mode not in LOCAL_FIRST_MODES:
        raise DefaultPostureViolation(
            f"a starting posture of {policy.operation_mode!r} permits a cloud model "
            f"without the user having asked for one (§8.4)")
    missing = sorted(set(DISPLAY_FACETS) - set(policy.redaction_settings))
    if missing:
        raise DefaultPostureViolation(
            f"facets {missing} are unresolved; §8.4's data-minimizing `must` has no "
            f"'unset' value, and an unresolved facet is decided by whoever reads it")
    shown = sorted(facet for facet, value in policy.redaction_settings.items()
                   if value != MORE_REDACTING[facet])
    if shown:
        raise DefaultPostureViolation(
            f"facets {shown} start shown; §8.4's example makes the aggregate the "
            f"default and the expansion the user's act")
