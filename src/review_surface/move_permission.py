"""The moment a person grants automatic movement for named protected files.

`74` §5.3, which narrowed P12's F15: §8.4 says protected material "should not be
moved automatically without a user policy that explicitly permits it", and P7's
PREDICATE for that is live and complete -- `privacy.moves.may_move_automatically`
checks absence first, reads the flag rather than the class, reads the policy at the
asked-for plan version, and treats no policy at all as no permission. What had no
producer anywhere in `src/` is the SURFACE that writes
`Policy.automatic_move_permissions`: the moment a person actually grants it. Until
this exists, `may_move_automatically` refuses every protected file, which is the
correct posture and not a bug.

**P13 authors no P7 record.** The policy write is INJECTED with no default, like
every other seam in this package. P13 presents the named files, collects the
gesture, routes it to P7, and hands the grant to a writer the composition root
supplies. A default writer would make P13 the silent author of a privacy policy the
first time somebody forgot to inject one -- and that authorship would be invisible,
because the call would simply succeed.

**The permission names files.** §8.4 permits named material, not a category, and
`Policy.automatic_move_permissions` is keyed by `file_id` for exactly that reason.
A grant over no file is refused rather than stored as an empty permission: an empty
grant is a gesture that looks like consent and permits nothing, and no later reader
can tell it from a grant that was meant to be wide.

**A grant belongs to its plan version.** §8.8: a new plan never silently moves old
files. The plan version is a required argument and is handed to the writer, so a
permission collected against one tree cannot authorise a move under a tree the user
has not yet adopted.

The gesture is collected as `mark_private`, which is P13's one action about a
file's privacy standing and which already routes to P7 and P6 jointly. Minting a
nineteenth action would be a SPEC-level act: the eighteen are the SPEC's own list
and adding a member to a closed vocabulary requires owner approval recorded at the
member. The action's payload says which way the permission was set.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

from privacy.policy import current_policy

from review_surface.collect import collect
from review_surface.records import ReviewAction
from review_surface.vocabulary import (
    ACTION_MARK_PRIVATE,
    SURFACE_PRIVACY_SETTINGS,
)

#: What the composition root injects: P7's policy writer, already composed so that
#: it merges into the policy in force and lets P7 mint the version. It returns the
#: `policy_version` P7 minted, which is what `MoveVerdict.permitting_policy`
#: carries and what P11 and P12 record.
PolicyWriter = Callable[..., str]


class MovePermissionWriterRequired(RuntimeError):
    """No policy writer was injected. P13 does not author P7's policy itself."""


class ProtectedFilesRequired(ValueError):
    """A grant naming no file. §8.4 permits named material, not a category."""


@dataclass(frozen=True)
class MovePermissionItem:
    """What the surface shows: which files, and what is true of them right now."""

    plan_version: str
    file_ids: tuple[str, ...]
    currently_permitted: Mapping[str, bool]


@dataclass(frozen=True)
class MovePermissionGrant:
    """The collected gesture and the policy version P7 minted for it."""

    action: ReviewAction
    policy_version: str
    plan_version: str
    file_ids: tuple[str, ...]
    permitted: bool


def move_permission_item(conn: sqlite3.Connection, *,
                         file_ids: Sequence[str],
                         plan_version: str) -> MovePermissionItem:
    """Read the policy in force and say, per file, whether it permits a move.

    A file the policy does not mention reads as NOT permitted, which is P7's own
    answer: no policy at all is no permission, and a missing key is the same fact
    as a policy that has never been set.
    """
    policy = current_policy(conn, plan_version=plan_version)
    permissions = (
        dict(policy.automatic_move_permissions) if policy is not None else {})
    return MovePermissionItem(
        plan_version=plan_version, file_ids=tuple(file_ids),
        currently_permitted={file_id: permissions.get(file_id) is True
                             for file_id in file_ids})


def grant_automatic_movement(conn: sqlite3.Connection, *,
                             file_ids: Sequence[str], permitted: bool,
                             plan_version: str, action_id: str,
                             session_id: str, correction_scope: str,
                             presented_state_ref: str, user_id: str,
                             acted_at: str, component_version: str,
                             write_policy: PolicyWriter) -> MovePermissionGrant:
    """Collect the grant, route it to P7, and hand the permission to P7's writer.

    `permitted=False` is the revocation. It is the same gesture in the other
    direction rather than a second function, because a revocation that took a
    different path could take a different set of files, and §8.4's permission is
    per file both ways.
    """
    named = tuple(file_ids)
    if not named:
        raise ProtectedFilesRequired(
            "a grant of automatic movement names the files it covers. §8.4 "
            "permits named material and not a category, and an empty grant is a "
            "gesture that looks like consent while permitting nothing -- no "
            "later reader could tell it from a grant meant to be wide")
    if write_policy is None:
        raise MovePermissionWriterRequired(
            "no policy writer was injected. P13 presents and collects; the "
            "policy is P7's record and P7 authors it. There is no default here, "
            "because a default would make P13 the silent author of a privacy "
            "policy the first time one was not supplied")
    action = collect(
        conn, action_id=action_id, surface=SURFACE_PRIVACY_SETTINGS,
        subject_ref=plan_version, plan_version=plan_version,
        session_id=session_id, action=ACTION_MARK_PRIVATE,
        correction_scope=correction_scope,
        presented_state_ref=presented_state_ref, user_id=user_id,
        acted_at=acted_at, component_version=component_version,
        payload={"automatic_move_permitted": permitted,
                 "file_ids": list(named)})
    policy_version = write_policy(
        conn, plan_version=plan_version,
        permissions={file_id: permitted for file_id in named},
        user_id=user_id, component_version=component_version,
        reason=("the user granted automatic movement for these files"
                if permitted else
                "the user revoked automatic movement for these files"))
    return MovePermissionGrant(
        action=action, policy_version=policy_version,
        plan_version=plan_version, file_ids=named, permitted=permitted)
