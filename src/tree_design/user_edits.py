# src/tree_design/user_edits.py
"""What the user said about a level, kept where re-derivation cannot reach it.

`64` §2: **the catalogue is a proposal; the user's edits are facts.** A proposal
may be re-derived at any time and a fact may not be overwritten by
re-derivation. That precedence is not new here — P7 already ranks a record on
`privacy.vocabulary.USER` above an inferred one of any reliability, and this
module reuses that basis rather than inventing a second word for the same idea.

THE KEY IS THE WHOLE DESIGN (`64` §3). An overlay is durable only if it is keyed
to something that survives the events that would otherwise destroy it, and two
of the three obvious keys fail:

* `node_id` fails. §8.8 mints a new one per plan version, which is exactly the
  bug the seam pass found in `learned_preferences_still_applicable`: filtering on
  `node_id` made every learned preference silently stop applying at the first
  tree edit.
* `template_id@version` fails. It is the PACKAGING, and packaging is precisely
  what a library upgrade changes.
* `(uses_schema, role_ref, field_ref)` holds. It is the VOCABULARY, and the
  vocabulary is what the catalogue and the user are both talking about. The
  sentence it records — "whatever level shows my `subject` field in an `academic`
  context, I call it Class" — stays true across a re-route, a re-version and an
  upgrade, because none of those change what a `subject` is.

**Per-schema, not global.** Renaming *Course* to *Class* in an academic context
renames nothing in a research context. That is the same reason `RoleBinding.label`
lives on the applicability row rather than on the definition: one role reads
differently per audience, and the audience is what the row selects.

**Four of the six dimension actions have no writer here, and are refused by
name.** The RECORD holds any of `DIMENSION_ACTIONS`, so the overlay is shaped to
carry a reorder or an omission the day one is built (`64` §6: "the overlay should
be designed to hold them rather than retrofitted per action"); the WRITER refuses
everything but a rename, before storing anything, exactly as `apply_review_action`
refuses its twelve. A stored edit nothing can apply is a silent no-op that
outlives every session.
"""
from __future__ import annotations

import os
import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from tree_design.templates import MalformedTemplateRecord, ResolvedDimension
from tree_design.vocabulary import (
    ACTION_OMITTED,
    ACTION_RENAMED,
    BASIS_USER,
    DIFF_REMOVED,
    DIFF_RENAMED,
    DIFF_RETEMPLATED,
    DIMENSION_ACTIONS,
    check,
)

#: `templates.py`'s and `records.py`'s set, restated here for the same reason
#: they each restate it: the rule travels with the record that must obey it.
_SEPARATORS = frozenset({"/", "\\", os.sep, os.altsep or "/"})

#: The dimension actions this overlay can apply. `64` §6 names the edit actions
#: still without a writer and says making renames durable does not make those
#: exist; this tuple is where that list grows, ONE ACTION AT A TIME, and each
#: member is here because something honours it.
#:
#: `omitted` joined on `110` §2.2, and it is the smaller of the two changes it
#: looks like: the record already held any of `DIMENSION_ACTIONS` (`64` §6: "the
#: overlay should be designed to hold them rather than retrofitted per action"),
#: and what it gained is an applier -- `apply_user_level_edits` marks the
#: dimension omitted and `materialise` does not build a folder for it. It is
#: `107`'s *change depth* as `110` reads it: not the `max_depth` ceiling, which
#: is one number for every tree, but leaving out ONE level of ONE branch.
OVERLAY_ACTIONS_WITH_A_WRITER: tuple[str, ...] = (ACTION_RENAMED, ACTION_OMITTED)


class UserEditRefused(RuntimeError):
    """An edit that cannot be stored, or two of the user's own that disagree."""


@dataclass(frozen=True)
class UserLevelEdit:
    """One thing the user said about one level, keyed to the vocabulary.

    There is deliberately NO `node_id`, `plan_version_id`, `template_id` or
    `binding_id` on this record. Each of them would make the edit expire at the
    next event the user did not cause, and `64` §3 rules out the first two by
    name.

    `proposed_label` is what the library called the level at the moment the user
    overrode it. It is kept because §5b requires that "the fact that the library
    proposed something different is recorded, not discarded" — the version of
    that fact from the edit's own moment, which is what lets an upgrade say
    *"the library called this Course when you renamed it to Class; it now calls
    it Module."*
    """

    uses_schema: str
    role_ref: str
    field_ref: str
    action: str
    display_label: str
    proposed_label: str | None
    user_id: str
    recorded_at: str
    #: P7's word, reused. `64` §2 is explicit that this is the same precedence
    #: rule, and a parallel vocabulary would be two things to keep in step.
    basis: str = BASIS_USER

    def __post_init__(self) -> None:
        # `display_label` IS NOT REQUIRED OF AN OMISSION, and that is the field
        # being honest rather than the check being relaxed. It holds "what the
        # user calls this level", and a person who left a level out has not
        # called it anything -- so an empty one here is a real answer, exactly as
        # `record_presentation`'s empty `evidence_refs` is. A stand-in word would
        # be the record inventing a name nobody typed, and `describe_applied_edits`
        # would then say the library was overruled on a label.
        required = ["uses_schema", "role_ref", "field_ref", "user_id",
                    "recorded_at"]
        if self.action != ACTION_OMITTED:
            required.append("display_label")
        for name in required:
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise MalformedTemplateRecord(
                    f"UserLevelEdit.{name} is required and cannot be empty")
        check(self.action, DIMENSION_ACTIONS, name="dimension action")
        # This overlay holds the USER's own act and nothing else. `BASIS_USER` is
        # imported from P7's vocabulary rather than respelled (`vocabulary.py`),
        # so the reuse `64` §2 asks for cannot quietly become a copy that drifts.
        if self.basis != BASIS_USER:
            raise MalformedTemplateRecord(
                f"basis {self.basis!r} is not {BASIS_USER!r}. The catalogue is a "
                "proposal and this record holds a FACT: an inferred basis here "
                "would be the system overruling the person on their own words")
        # `templates.py`'s rule, preserved literally and at the earliest moment:
        # "a renamed level is a display label, never a path fragment". The same
        # check exists on `ResolvedDimension`, but by the time it fires there the
        # edit is already stored and every later route raises on it.
        if any(sep in (self.display_label or "") for sep in _SEPARATORS):
            raise MalformedTemplateRecord(
                f"{self.display_label!r} holds a path separator. A renamed level "
                "is a display label, never a path fragment; P12 alone composes "
                "paths (resolution B3)."
            )

    def key(self) -> tuple[str, str, str]:
        """`64` §3's stable triple. The vocabulary, never the packaging."""
        return (self.uses_schema, self.role_ref, self.field_ref)


@dataclass(frozen=True)
class UnappliedUserEdit:
    """An edit this composition cannot honour, surfaced rather than resolved.

    `64` §5c: if the new library removes a level the user had kept, or resolves
    its role to another field, "that is a question for the user, not a decision
    for the product". `kind` is one of `diff.py`'s own words (§5d) so that "what
    changed when I updated" and "what changed when I edited" read the same way.
    """

    edit: UserLevelEdit
    kind: str
    explanation: str


def record_user_level_edit(conn: sqlite3.Connection,
                           edit: UserLevelEdit) -> None:
    """Store one edit, replacing any earlier answer for the same triple.

    One key holds one answer: a user who renames a level twice has changed their
    mind, not made two facts, and keeping both would put the shipped name at the
    mercy of a row order.
    """
    if edit.action not in OVERLAY_ACTIONS_WITH_A_WRITER:
        raise UserEditRefused(
            f"{edit.action!r} is one of the dimension actions this overlay holds "
            f"and has no writer for; only {list(OVERLAY_ACTIONS_WITH_A_WRITER)} "
            "can be applied. It is refused here rather than stored: an edit "
            "nothing can apply is a silent no-op that survives every future "
            "session, and the user would see their edit accepted and never "
            "honoured"
        )
    conn.execute(
        "INSERT OR REPLACE INTO user_level_edits "
        "(uses_schema, role_ref, field_ref, action, display_label, "
        " proposed_label, basis, user_id, recorded_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (edit.uses_schema, edit.role_ref, edit.field_ref, edit.action,
         edit.display_label, edit.proposed_label, edit.basis, edit.user_id,
         edit.recorded_at))
    conn.commit()


def user_level_edits(conn: sqlite3.Connection, *,
                     schemas: Sequence[str] | None = None,
                     ) -> tuple[UserLevelEdit, ...]:
    """Every edit, or every edit in the named schemas. Deterministic order."""
    sql = ("SELECT * FROM user_level_edits "
           "ORDER BY uses_schema, role_ref, field_ref")
    rows = conn.execute(sql).fetchall()
    wanted = None if schemas is None else set(schemas)
    return tuple(
        UserLevelEdit(
            uses_schema=row["uses_schema"], role_ref=row["role_ref"],
            field_ref=row["field_ref"], action=row["action"],
            display_label=row["display_label"],
            proposed_label=row["proposed_label"], user_id=row["user_id"],
            recorded_at=row["recorded_at"], basis=row["basis"])
        for row in rows
        if wanted is None or row["uses_schema"] in wanted)


def apply_user_level_edits(
    dimensions: Sequence[ResolvedDimension],
    edits: Sequence[UserLevelEdit],
    *,
    schemas_for_binding: Mapping[tuple[str, str], frozenset[str]],
    composition_schemas: frozenset[str],
) -> tuple[tuple[ResolvedDimension, ...], tuple[UnappliedUserEdit, ...]]:
    """The user's last word about a level, applied to gated dimensions.

    Called at the END of routing and never at the start (`64` §4). The C1-C8
    gates must go on judging THE RECIPE rather than the recipe-as-the-user-
    rewrote-it: a rename applied first could collapse two rows that name one role
    two ways into one name, and a composition C4 exists to refuse would ship.

    Only `display_label`, `action` and `proposed_label` move. `field_ref`,
    `order_index` and `scope` are untouched, because a rename that changed any of
    those would be a structural edit wearing a label's clothes — and `templates.py`
    already fixes what a rename is: "a renamed level is a display label, never a
    path fragment".

    **AN OMISSION IS STRUCTURAL AND THIS FUNCTION STILL ONLY WRITES AN ACTION**
    (`110` §2.2). It was once true that everything here was about presentation,
    and it is not any more: leaving a level out changes which folders exist. What
    has not changed is where the change is MADE. The level stays in the list,
    keeps its field, its order and its label, and is marked `omitted`;
    `materialise` is what then builds no folder for it, on exactly the branch it
    already takes for a level the corpus does not divide at. Rewriting the list
    here instead would put a second spelling of "this level is not built" in
    front of the one the projection already has, and the level would vanish from
    the screen that has to keep naming it (`84` §1).

    An edit for a schema this composition does not use is not this composition's
    business and is neither applied nor reported; an edit for a schema it DOES
    use, naming a level it does not have, is reported in `diff.py`'s vocabulary
    and resolved by nobody.
    """
    by_key = {(dimension.role_ref, dimension.field_ref): index
              for index, dimension in enumerate(dimensions)}
    roles = {dimension.role_ref for dimension in dimensions}

    applied: dict[int, UserLevelEdit] = {}
    unapplied: list[UnappliedUserEdit] = []
    for edit in edits:
        if edit.uses_schema not in composition_schemas:
            continue
        index = by_key.get((edit.role_ref, edit.field_ref))
        if index is None:
            kind = DIFF_RETEMPLATED if edit.role_ref in roles else DIFF_REMOVED
            unapplied.append(UnappliedUserEdit(
                edit, kind,
                f"you {_said_of(edit)} {edit.role_ref!r} when "
                f"it resolved to {edit.field_ref!r}; this release "
                + ("resolves it to another field"
                   if kind == DIFF_RETEMPLATED
                   else "does not include that level")
                + ", so your edit is not applied and nothing was invented in "
                  "its place"))
            continue
        if edit.uses_schema not in schemas_for_binding.get(
                (edit.role_ref, edit.field_ref), frozenset()):
            continue
        standing = applied.get(index)
        if standing is not None and (
                (standing.action, standing.display_label)
                != (edit.action, edit.display_label)):
            # C4's shape, applied to the user's own edits. One question with two
            # answers has none, and taking either would make the shipped tree
            # depend on the order the rows happened to be listed in. The ACTION
            # is compared as well as the label, because "call it Class" and
            # "leave it out" are two answers to one question just as two names
            # are, and comparing labels alone read an omission (which carries no
            # label) as agreeing with every other omission and with nothing else.
            raise UserEditRefused(
                f"{edit.role_ref!r} is {_said_of(standing)} in "
                f"{standing.uses_schema!r} and {_said_of(edit)} in "
                f"{edit.uses_schema!r}, and this composition uses both schemas. "
                "P10 takes neither silently"
            )
        applied[index] = edit

    resolved = list(dimensions)
    for index, edit in applied.items():
        dimension = resolved[index]
        resolved[index] = ResolvedDimension(
            role_ref=dimension.role_ref,
            field_ref=dimension.field_ref,
            # `ACTION_RENAMED` is `DIFF_RENAMED` — one word, so the edit is
            # legible to the diff surface without a translation table.
            action=edit.action,
            order_index=dimension.order_index,
            # AN OMISSION KEEPS THE LIBRARY'S OWN LABEL, and that is `84` §1
            # rather than an oversight: the level is still MEASURED and still
            # named on the screen, and a level that vanished from the list would
            # be a level the person could no longer see they had left out.
            display_label=(dimension.display_label
                           if edit.action == ACTION_OMITTED
                           else edit.display_label),
            scope=dimension.scope,
            # What THIS release proposed, kept beside what the user said. §5b:
            # the user wins AND the library's proposal is recorded, not
            # discarded — a proposal that vanished cannot be offered back and an
            # upgrade could not be explained. For an omission the proposal was
            # to BUILD it, which is what lets a later release say "this release
            # would have built a Purpose level here; you omitted it".
            proposed_label=dimension.display_label,
        )
    return tuple(resolved), tuple(unapplied)


def _said_of(edit: UserLevelEdit) -> str:
    """What the person said about one level, as a clause naming the action.

    One spelling for the three sentences that have to say it -- the conflict
    refusal, the unapplied-edit explanation and the composition's own
    description -- because three of them written separately is how one gesture
    comes to be described three ways on one screen.
    """
    if edit.action == ACTION_OMITTED:
        return "left out"
    return f"renamed {edit.display_label!r}"


def describe_applied_edits(dimensions: Sequence[ResolvedDimension]) -> str:
    """One sentence about the user's edits to a composition, in `diff.py`'s words."""
    renamed = [d for d in dimensions if d.action == ACTION_RENAMED]
    omitted = [d for d in dimensions if d.action == ACTION_OMITTED]
    said = ""
    if renamed:
        parts = ", ".join(
            f"{d.proposed_label!r} -> {d.display_label!r}" for d in renamed)
        said += (f" The user {DIFF_RENAMED} {len(renamed)} level(s) and this "
                 f"release proposed otherwise: {parts}.")
    if omitted:
        # NAMED, not counted only. `84` §1's shape applied to a level: a person
        # reading this has to be able to tell WHICH level they left out, and a
        # bare number is the sentence that sounds complete and answers nothing.
        parts = ", ".join(repr(d.proposed_label or d.role_ref) for d in omitted)
        said += (f" The user left {len(omitted)} level(s) out of this shape and "
                 f"this release would have built them: {parts}.")
    return said
