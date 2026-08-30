"""P12's closed vocabularies. Named constant == string value, one home each.

Every module in `src/mutation/` imports the NAMED CONSTANT from here. Never a bare
string, never an index into a tuple: an index is single-homed and unreadable, and
it silently couples every consumer to the tuple's order (the repo's ruling,
`_PLAN-AUTHORING-BRIEF.md` §11).

`DECLINE_MESSAGES` is here rather than at each call site because `66` §10's
requirement is that the messages are DISTINCT, and distinctness is a property of
the set, not of any one sentence. Five of them are `66`'s own words.
"""
from __future__ import annotations

import unicodedata
from types import MappingProxyType
from typing import Mapping

#: §8.2's "responsible subsystem" for everything P12 authors. ONE place.
SUBSYSTEM: str = "P12"


class OutOfVocabulary(ValueError):
    """A value outside a closed set. The set is named; the nearest match is not."""


def check(value: object, closed: tuple[str, ...], *, name: str) -> str:
    """One membership test for every closed set here.

    The offending value is deliberately absent from the message: P12's vocabularies
    include `stale:<trigger>` and `conflict:<class>` compounds, and echoing an
    attacker- or caller-supplied string into a log line that a person reads is a
    habit worth not having in the one part that touches the filesystem.
    """
    if not isinstance(value, str) or value not in closed:
        raise OutOfVocabulary(f"not one of {name}: {closed}")
    return value


# --- §8.3's five staleness triggers -----------------------------------------
CONTENT_HASH_DIFFERS: str = "content_hash_differs"
SOURCE_PATH_CHANGED: str = "source_path_changed"
DESTINATION_CHANGED: str = "destination_changed"
SOURCE_VANISHED: str = "source_vanished"
PERMISSION_LOST: str = "permission_lost"
STALENESS_TRIGGERS: tuple[str, ...] = (
    CONTENT_HASH_DIFFERS, SOURCE_PATH_CHANGED, DESTINATION_CHANGED,
    SOURCE_VANISHED, PERMISSION_LOST,
)

# --- Contract out §5's refusal classes ---------------------------------------
NODE_NOT_IN_FROZEN_TREE: str = "node_not_in_frozen_tree"
NODE_REFUSES_PLACEMENT: str = "node_refuses_placement"
NODE_PATH_COLLISION: str = "node_path_collision"
CROSS_FOLDER_NOT_PERMITTED: str = "cross_folder_not_permitted"
REVIEW_POLICY_UNSATISFIED: str = "review_policy_unsatisfied"
PROTECTED_WITHOUT_POLICY: str = "protected_without_policy"
SOURCE_OR_DESTINATION_UNAVAILABLE: str = "source_or_destination_unavailable"
SYMLINK_NOT_FOLLOWED: str = "symlink_not_followed"
PACKAGE_BUNDLE_UNAPPROVED: str = "package_bundle_unapproved"
HASH_UNVERIFIABLE: str = "hash_unverifiable"
REFUSAL_CLASSES: tuple[str, ...] = (
    NODE_NOT_IN_FROZEN_TREE, NODE_REFUSES_PLACEMENT, NODE_PATH_COLLISION,
    CROSS_FOLDER_NOT_PERMITTED, REVIEW_POLICY_UNSATISFIED,
    PROTECTED_WITHOUT_POLICY, SOURCE_OR_DESTINATION_UNAVAILABLE,
    SYMLINK_NOT_FOLLOWED, PACKAGE_BUNDLE_UNAPPROVED, HASH_UNVERIFIABLE,
)

#: The five refusals evaluated at plan CONSTRUCTION as well as at the pre-apply
#: recheck. `review_policy_unsatisfied` is deliberately not among them: §8.3
#: requires the plan to be built so it can be shown (SPEC, Contract out §5).
CONSTRUCTION_REFUSALS: tuple[str, ...] = (
    NODE_NOT_IN_FROZEN_TREE, NODE_REFUSES_PLACEMENT, NODE_PATH_COLLISION,
    CROSS_FOLDER_NOT_PERMITTED,
)

# --- §8.3's four user-approved collision behaviours --------------------------
PRESERVE_BOTH_DETERMINISTIC_SUFFIX: str = "preserve_both_deterministic_suffix"
MERGE_ONLY_IF_HASHES_IDENTICAL: str = "merge_only_if_hashes_identical"
RETAIN_NEWER_OLDER_TO_VERSION_FAMILY_REVIEW: str = (
    "retain_newer_older_to_version_family_review")
STOP_AND_ASK: str = "stop_and_ask"
COLLISION_BEHAVIOURS: tuple[str, ...] = (
    PRESERVE_BOTH_DETERMINISTIC_SUFFIX, MERGE_ONLY_IF_HASHES_IDENTICAL,
    RETAIN_NEWER_OLDER_TO_VERSION_FAMILY_REVIEW, STOP_AND_ASK,
)

NAME_ONLY: str = "name_only"
CONTENT_HASH_MATCH: str = "content_hash_match"
COLLISION_KINDS: tuple[str, ...] = (NAME_ONLY, CONTENT_HASH_MATCH)

SUFFIXED_PATH: str = "suffixed path"
MERGED_NO_WRITE: str = "merged, no write"
OLDER_SENT_TO_VERSION_FAMILY_REVIEW: str = "older sent to version-family review"
HALTED_AWAITING_USER: str = "halted awaiting user"
COLLISION_OUTCOMES: tuple[str, ...] = (
    SUFFIXED_PATH, MERGED_NO_WRITE, OLDER_SENT_TO_VERSION_FAMILY_REVIEW,
    HALTED_AWAITING_USER,
)

# --- Contract out §5's execution record --------------------------------------
ATOMIC_RENAME: str = "atomic_rename"
CROSS_VOLUME_COPY_AND_DELETE: str = "cross_volume_copy_and_delete"
EXECUTION_MODES: tuple[str, ...] = (ATOMIC_RENAME, CROSS_VOLUME_COPY_AND_DELETE)

APPLIED: str = "applied"
REFUSED: str = "refused"
STALE: str = "stale"
PAUSED: str = "paused"
FAILED: str = "failed"
RESULT_KINDS: tuple[str, ...] = (APPLIED, REFUSED, STALE, PAUSED, FAILED)

V3_HASH_MISMATCH: str = "v3_hash_mismatch"
V4_DESTINATION_UNCONFIRMED: str = "v4_destination_unconfirmed"
FAILURE_CLASSES: tuple[str, ...] = (V3_HASH_MISMATCH, V4_DESTINATION_UNCONFIRMED)

CLOUD_SYNC_CONFLICT: str = "cloud_sync_conflict"
#: §8.3's `stop and ask the user`, and the two other collision outcomes that
#: write nothing and need a person: a hash-identical merge and a `retain_newer`
#: whose incumbent is the newer file. All three mean the same thing to the person
#: -- this collision needs your decision -- and WHICH of them occurred is on the
#: collision record, which is that value's one home. Contract out §5 shows
#: `paused:<reason>` and enumerates no reasons, so naming the ones P12's own
#: defined behaviours produce is P12's, and a fourth spelling of "a person must
#: choose" would not be.
AWAITING_COLLISION_DECISION: str = "awaiting_collision_decision"
PAUSE_REASONS: tuple[str, ...] = (CLOUD_SYNC_CONFLICT, AWAITING_COLLISION_DECISION)

# --- Contract out §7's undo verdicts -----------------------------------------
REVERSED: str = "reversed"
CONFLICT_DESTINATION_CONTENT_CHANGED: str = "conflict:destination_content_changed"
CONFLICT_DESTINATION_MISSING_OR_MOVED: str = "conflict:destination_missing_or_moved"
CONFLICT_SOURCE_PATH_OCCUPIED: str = "conflict:source_path_occupied"
UNDO_REFUSED_UNAVAILABLE: str = "refused:source_or_destination_unavailable"
UNDO_VERDICTS: tuple[str, ...] = (
    REVERSED, CONFLICT_DESTINATION_CONTENT_CHANGED,
    CONFLICT_DESTINATION_MISSING_OR_MOVED, CONFLICT_SOURCE_PATH_OCCUPIED,
    UNDO_REFUSED_UNAVAILABLE,
)

DIR_REMOVED: str = "removed"
DIR_RETAINED_NOT_EMPTY: str = "retained:not_empty"
DIR_RETAINED_REFERENCED: str = "retained:referenced_by_other_entry"
DIR_RETAINED_NOT_CREATED: str = "retained:not_created_by_this_entry"
DIRECTORY_REVERSAL_OUTCOMES: tuple[str, ...] = (
    DIR_REMOVED, DIR_RETAINED_NOT_EMPTY, DIR_RETAINED_REFERENCED,
    DIR_RETAINED_NOT_CREATED,
)

# --- `66` §11's four undo-retention choices ----------------------------------
#: *"The user should be able to select 30 days, 90 days, one year, or retention
#: until manually cleared"* (`66` §11). The four CHOICES are `66`'s and so are
#: closed here. What each one MEANS in elapsed time is not: `66` recommends 90
#: days as a default, that recommendation is a product decision belonging to the
#: composition root, and A7 admits no numeric literal here anyway. So
#: `retention.py` takes the duration injected and refuses when it is absent.
RETENTION_THIRTY_DAYS: str = "thirty_days"
RETENTION_NINETY_DAYS: str = "ninety_days"
RETENTION_ONE_YEAR: str = "one_year"
RETENTION_UNTIL_MANUALLY_CLEARED: str = "until_manually_cleared"
UNDO_RETENTION_CHOICES: tuple[str, ...] = (
    RETENTION_THIRTY_DAYS, RETENTION_NINETY_DAYS, RETENTION_ONE_YEAR,
    RETENTION_UNTIL_MANUALLY_CLEARED,
)

#: The one choice that carries no period. Named rather than compared by string
#: at each site, and named as a single member rather than as a set, because
#: there is exactly one unbounded choice and a set would invite a second.
UNBOUNDED_RETENTION: str = RETENTION_UNTIL_MANUALLY_CLEARED

# --- Contract out §3's cross-folder verdict ----------------------------------
WITHIN_ROOT: str = "within_root"
CROSS_ROOT_PERMITTED: str = "cross_root_permitted"
CROSS_ROOT_REFUSED: str = "cross_root_refused"
CROSS_FOLDER_VERDICTS: tuple[str, ...] = (
    WITHIN_ROOT, CROSS_ROOT_PERMITTED, CROSS_ROOT_REFUSED)

# --- P13's review_approval verdicts (Contract in -> From P13) ----------------
APPROVED: str = "approved"
REJECTED: str = "rejected"
DEFERRED: str = "deferred"
REFRESH_REQUIRED: str = "refresh_required"
REVIEW_VERDICTS: tuple[str, ...] = (APPROVED, REJECTED, DEFERRED, REFRESH_REQUIRED)

# --- Contract out §3's `Normalizations applied` ------------------------------
UNICODE_NORMALIZATION: str = "unicode_normalization"
CASE_FOLDING: str = "case_folding"
PROHIBITED_CHARACTER_SUBSTITUTION: str = "prohibited_character_substitution"
RESERVED_NAME_AVOIDANCE: str = "reserved_name_avoidance"
LENGTH_TRUNCATION: str = "length_truncation"
NORMALIZATIONS: tuple[str, ...] = (
    UNICODE_NORMALIZATION, CASE_FOLDING, PROHIBITED_CHARACTER_SUBSTITUTION,
    RESERVED_NAME_AVOIDANCE, LENGTH_TRUNCATION,
)

# --- Contract out §2's two evaluation points ---------------------------------
PREPARE: str = "prepare"
PRE_APPLY: str = "pre_apply"
CHECKPOINTS: tuple[str, ...] = (PREPARE, PRE_APPLY)

# --- Contract out §6's journal -----------------------------------------------
ENTRY_APPLIED: str = "applied"
ENTRY_REVERSAL: str = "reversal"
JOURNAL_ENTRY_KINDS: tuple[str, ...] = (ENTRY_APPLIED, ENTRY_REVERSAL)

FRESH: str = "fresh"

# --- The six §8.2 event types P12 authors. P1 writes them. -------------------
PLANNED_MOVE: str = "planned move"
EXECUTED_MOVE: str = "executed move"
FAILED_MOVE: str = "failed move"
FILENAME_COLLISION_RESOLUTION: str = "filename-collision resolution"
EXTERNAL_MODIFICATION_DETECTION: str = "external modification detection"
UNDO: str = "undo"
EVENT_TYPES: tuple[str, ...] = (
    PLANNED_MOVE, EXECUTED_MOVE, FAILED_MOVE, FILENAME_COLLISION_RESOLUTION,
    EXTERNAL_MODIFICATION_DETECTION, UNDO,
)

#: The seventh. `74` §5.2 closes PLAN F13: the P12 PLAN says minting a name for a
#: refused action is a spec-level act P12 may not perform, and it has since been
#: performed -- `database_agent/events.py:30-54` records the owner's approval on
#: 2026-08-29 and notes that P12 is its only intended writer. Kept separate from
#: `EVENT_TYPES` because that tuple is §8.2's own six and this one is not.
REFUSED_MOVE: str = "refused move"

#: Every event type P12 authors, six plus the seventh. This is the tuple a caller
#: iterating "what does P12 write?" wants; `EVENT_TYPES` is the tuple a reader
#: checking "what does §8.2 give P12?" wants, and they are different questions.
AUTHORED_EVENT_TYPES: tuple[str, ...] = (*EVENT_TYPES, REFUSED_MOVE)

# --- `66` §10: one distinct sentence per declinable outcome ------------------
# Five are `66` §10's own words, quoted:
#   "This file has two approved homes"      -- not P12's; the shared-material case
#                                              is P10's policy and P11's outcome
#   "I could not read this file"            -- not P12's; a reading failure never
#                                              reaches a move plan
#   "This item is protected by your privacy policy"
#   "This file changed after the preview"
#   "No approved destination fits"
# The three P12 owns are used verbatim. The rest are written to the same standard:
# each says WHAT OCCURRED and what action is available (`66` §10), and no two are
# the same sentence -- that is the requirement and `messages_that_read_alike` is
# its guard.
_MESSAGES: dict[str, str] = {
    NODE_NOT_IN_FROZEN_TREE:
        "No approved destination fits.",
    NODE_REFUSES_PLACEMENT:
        "That folder is not one you approved as a destination. "
        "Approve it in your folder plan, or choose another.",
    NODE_PATH_COLLISION:
        "Two folders in your plan would end up with the same name on disk. "
        "Rename one of them in your folder plan.",
    CROSS_FOLDER_NOT_PERMITTED:
        "You asked the product not to move files between your top-level folders, "
        "and this move would. Change that setting or pick a destination "
        "under the same folder.",
    REVIEW_POLICY_UNSATISFIED:
        "This move is waiting for your approval. Review it to let it run.",
    PROTECTED_WITHOUT_POLICY:
        "This item is protected by your privacy policy.",
    SOURCE_OR_DESTINATION_UNAVAILABLE:
        "The drive or folder this move needs is not available right now. "
        "Reconnect it and try again.",
    SYMLINK_NOT_FOLLOWED:
        "This is a link to a file somewhere else, so the product left it alone. "
        "Move the original if you meant to move the file.",
    PACKAGE_BUNDLE_UNAPPROVED:
        "This is an application or package. The product never moves one.",
    HASH_UNVERIFIABLE:
        "The product could not confirm this file's contents, so it did not move it.",
    f"stale:{CONTENT_HASH_DIFFERS}":
        "This file changed after the preview.",
    f"stale:{SOURCE_PATH_CHANGED}":
        "This file is no longer where the preview found it.",
    f"stale:{DESTINATION_CHANGED}":
        "The destination changed after the preview.",
    f"stale:{SOURCE_VANISHED}":
        "This file is no longer there.",
    f"stale:{PERMISSION_LOST}":
        "The product no longer has permission to touch this file.",
    f"paused:{CLOUD_SYNC_CONFLICT}":
        "Your cloud drive is still syncing a conflicting copy of this file, "
        "so the product paused instead of moving it.",
    f"paused:{AWAITING_COLLISION_DECISION}":
        "Something with this name is already in that folder, and your collision "
        "setting asks you to decide. Nothing was moved or written over.",
    f"failed:{V3_HASH_MISMATCH}":
        "The file at the destination is not byte-identical to the one that was "
        "moved. Nothing was removed; both copies are named below.",
    f"failed:{V4_DESTINATION_UNCONFIRMED}":
        "The copy on the other drive could not be confirmed, so the original was "
        "left exactly where it was.",
    CONFLICT_DESTINATION_CONTENT_CHANGED:
        "This action cannot be undone automatically because the file changed "
        "after it was moved.",
    CONFLICT_DESTINATION_MISSING_OR_MOVED:
        "This action cannot be undone automatically because the file is no longer "
        "where the product put it.",
    CONFLICT_SOURCE_PATH_OCCUPIED:
        "Undoing this would write over a different file that is now sitting where "
        "the original used to be.",
    UNDO_REFUSED_UNAVAILABLE:
        "Undo needs a drive or folder that is not available right now.",
}

DECLINE_MESSAGES: Mapping[str, str] = MappingProxyType(_MESSAGES)
DECLINABLE_OUTCOMES: tuple[str, ...] = tuple(_MESSAGES)


def decline_message(outcome: str) -> str:
    """`66` §10's user-facing sentence for one declined outcome.

    An unknown outcome RAISES. Returning a generic sentence would be the exact
    failure `66` §10 names -- *"unclassified and unreadable are two of five states
    that may never share a message"* is the same rule one part over.
    """
    check(outcome, DECLINABLE_OUTCOMES, name="declinable outcome")
    return _MESSAGES[outcome]


def reading_key(message: str) -> str:
    """What one refusal message looks like to the person who reads it.

    Casefolded, stripped of punctuation and of the difference between one space
    and three. `66` §10 asks for messages a person can tell apart, and two
    sentences differing only in a full stop are not two messages -- so equality
    on the raw string is too weak a test for the property the design states.
    """
    kept = [
        character.casefold()
        for character in unicodedata.normalize("NFC", message)
        if character.isalnum() or character.isspace()
    ]
    return " ".join("".join(kept).split())


def messages_that_read_alike(
        table: Mapping[str, str]) -> tuple[tuple[str, str], ...]:
    """Every pair of outcomes in `table` whose messages read alike.

    Takes the table as an argument rather than closing over `DECLINE_MESSAGES`
    so a test can run this guard against a deliberately indistinct table: a guard
    only ever run against clean input passes just as well when it is unreachable.
    Pairs come back in the table's own order.
    """
    grouped: dict[str, list[str]] = {}
    for outcome, message in table.items():
        grouped.setdefault(reading_key(message), []).append(outcome)
    # Written as a nested walk rather than `itertools.combinations(outcomes, 2)`
    # because A7 admits no numeric literal beyond 0 and 1 in `src/mutation/`, and
    # a `2` here would be the first one.
    pairs: list[tuple[str, str]] = []
    for outcomes in grouped.values():
        for index, first in enumerate(outcomes):
            for second in outcomes[index + 1:]:
                pairs.append((first, second))
    return tuple(pairs)
