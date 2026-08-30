"""SPEC §9's settled defaults for special objects and volumes, and only those.

`00`:174 supplies three: *"avoid following symbolic links during mutation, avoid
moving package bundles unless explicitly approved, and refuse a move if the
source or destination is unavailable"*, plus the cloud rule -- *"treat
cloud-synced paths as externally mutable, verify them immediately before and
after action, and pause when sync conflicts appear."*

**The check order is a security rule, not a style choice.** `69` §0: protected
material is MARKED AND COUNTED, NEVER OPENED. So the package / system-item test
runs FIRST, from the path shape alone, before any symlink is resolved and before
any `stat` that could follow one into a bundle. The predicate is P3's ratified
`is_protected_container`, whose unit of protection is the SUBTREE; P12 authors no
bundle-suffix table of its own and imports P3's, because a second copy of a
safety table is a second answer, and the day the two disagree the wrong one is
the one that admitted something.

The class name `package_bundle_unapproved` reads as though an approval could lift
it, and none can: SPEC §9 says *"Refuse. Absolutely, with no override … unlike
every other row in this table, this one has no approved path."* The name is
Contract out §5's and is not a plan author's to change. The BEHAVIOUR is right --
there is no parameter here through which an approval could arrive -- and the name
is flagged rather than renamed.

**What is NOT here, deliberately.** `74` §8 Q5: locked files, files open in
another application, aliases and shortcuts. §8.3 demands a defined behaviour for
each and supplies none, so none is detected and no refusal class names one.
Inventing one would be P12 answering an owner's open question in code. Permission
failure is absent for a different reason -- it is §8.3's fifth staleness trigger
and belongs to `preconditions.py`, one step later in the same transaction.
"""
from __future__ import annotations

import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path

from scan_agent.exclusion import REASON_PROTECTED_CONTAINER, is_protected_container

from mutation.vocabulary import (
    CLOUD_SYNC_CONFLICT, PACKAGE_BUNDLE_UNAPPROVED, PAUSE_REASONS,
    REFUSAL_CLASSES, SOURCE_OR_DESTINATION_UNAVAILABLE, SYMLINK_NOT_FOLLOWED,
    check, decline_message,
)


@dataclass(frozen=True)
class ObjectVerdict:
    refusal_class: str | None
    pause_reason: str | None
    detail: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.refusal_class is not None:
            check(self.refusal_class, REFUSAL_CLASSES, name="refusal class")
        if self.pause_reason is not None:
            check(self.pause_reason, PAUSE_REASONS, name="pause reason")
        if self.refusal_class is not None and self.pause_reason is not None:
            # "No" and "not yet" are different things to tell a person, and a
            # record carrying both would let a caller show whichever it liked.
            raise ValueError(
                "an object verdict is a refusal or a pause, never both")

    @property
    def permits_mutation(self) -> bool:
        return self.refusal_class is None and self.pause_reason is None


def _refuse(refusal_class: str, **detail: object) -> ObjectVerdict:
    return ObjectVerdict(
        refusal_class=refusal_class, pause_reason=None,
        detail={**detail, "message": decline_message(refusal_class)})


def inspect_objects(*, source: Path,
                    destination_directory: Path,
                    source_root: Path,
                    destination_root: Path,
                    extra_protected: Callable[[Path], bool] | None,
                    conflict_copies: Callable[[Path], tuple[str, ...]],
                    dataless_of: Callable[[Path], bool]) -> ObjectVerdict:
    """One verdict for both ends of a move. No mutation, and no read of content.

    `extra_protected` is handed straight to P3's predicate, which can only ADD:
    a caller cannot un-protect a `.app`, because the rule has no override and a
    predicate that could return False for one would be that override. It is
    still a required argument with no default -- `None` is the deployment
    saying *"nothing beyond P3's own table"*, which is an answer, and an
    omitted argument is not.

    `conflict_copies` and `dataless_of` are injected for the same reason and
    with no default either. Production answers datalessness from
    `os.lstat(...).st_flags & SF_DATALESS`, which no fixture can produce
    portably and which a replay must be able to answer from its bundle.
    """
    for path in (source, destination_directory):
        if is_protected_container(path, extra=extra_protected):
            # From the path shape alone. Nothing below this line has run, so
            # nothing has been stat'd, opened, listed or descended into.
            return _refuse(
                PACKAGE_BUNDLE_UNAPPROVED, path=str(path),
                rule=REASON_PROTECTED_CONTAINER,
                # Present-but-untouched, and legible without anyone reopening
                # the question of what is inside. The count is of this one item.
                marked_and_counted=1)

    if os.path.islink(source):
        # `00`:174's safe default is not to FOLLOW it, so the target is not
        # resolved and does not appear in the record -- a detail naming where
        # the link points would have followed it.
        return _refuse(SYMLINK_NOT_FOLLOWED, path=str(source),
                       target_not_resolved=True)

    for root, which in ((source_root, "source"),
                        (destination_root, "destination")):
        if not root.exists():
            return _refuse(SOURCE_OR_DESTINATION_UNAVAILABLE,
                           unavailable=which, root=str(root))
    if not source.exists():
        return _refuse(SOURCE_OR_DESTINATION_UNAVAILABLE, unavailable="source",
                       path=str(source))

    if dataless_of(source):
        # SPEC §9: do not hash, copy, or download in order to move.
        # Materialization is a user action (`11-ops-runtime.md` §5). This is
        # §8.3's existing source-unavailable refusal wearing a detail, not a
        # sixth staleness trigger.
        return _refuse(SOURCE_OR_DESTINATION_UNAVAILABLE, unavailable="source",
                       path=str(source), dataless=True)

    conflicts = tuple(conflict_copies(source))
    if conflicts:
        # A pause, not a refusal. The plan is still good; a sync agent is
        # mid-flight, so the person is told to wait rather than told no.
        return ObjectVerdict(
            refusal_class=None, pause_reason=CLOUD_SYNC_CONFLICT,
            detail={"path": str(source), "conflict_copies": conflicts,
                    "message": decline_message(
                        f"paused:{CLOUD_SYNC_CONFLICT}")})

    return ObjectVerdict(refusal_class=None, pause_reason=None,
                         detail={"path": str(source)})
