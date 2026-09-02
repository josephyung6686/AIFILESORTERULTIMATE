# tests/p7/test_p7_self_description_item.py
"""The narrow door `80` §8 opens, and the eight it must leave shut.

The owner ruled on 2026-09-02 for a narrow P7 release path over a local model and
over deferring, with the tradeoff in front of him, and said in his own words that
**the scoping is the hard part**. So the ruling is not "loosen P7". It is "open
exactly one door, and make the other eight unreachable by construction".

**They already were, and this file is what proves it stayed true.** `items.py` does
not take a kind as a parameter. It holds one frozen dataclass per releasable kind and
`kind_of` maps type to name, raising on a foreign type -- so the failure the ruling
was most worried about, a caller passing `ocr_output` to a path that happens to be
called with `user_edits` today, has nothing to pass. There is no `OcrOutput` type and
this file asserts there is none.

Two seals are structural and one is not, and the third is named rather than buried:

1. **WHICH KIND** -- a type, not a check. Only a `SelfDescription` can be a
   self-description, and the eight always-local kinds have no type at all.
2. **WHICH ROW** -- a type, not a check. `SelfDescription` carries a role
   `question_id` and refuses any other prefix, so it cannot address an OCR row, a
   path row, or any other row in the questions store.
3. **WHO CONSTRUCTS** -- a scan, and it could not be a type. Nothing in Python stops
   a module constructing `SelfDescription("role:me")`; a type can seal what a value
   IS and cannot seal where it was made. `tests/integration/test_single_egress.py`
   holds that one, in the file that already scans `src/` for undeclared doors.

`80` §8's three conditions are untouched by the ruling and are tested with it: local
is the DEFAULT, a run that sends says so on screen BEFORE sending, and it reverts.
The first is why `suspension_permits_self_description` has no default anywhere it appears.
"""
from __future__ import annotations

import dataclasses
import inspect
import pathlib

import pytest

from privacy.items import (
    ROLE_QUESTION_PREFIX, SelfDescription, SelfDescriptionNotAdmitted,
    UnratifiedItemKind, _KIND_BY_TYPE, check_item, kind_of,
)
from privacy.vocabulary import ALWAYS_LOCAL, ITEM_KINDS
from questions.registry import ROLE_KIND

A_ROLE = "role:me"


def _check(item, **overrides):
    kwargs = dict(unit_length=None, protected=False, sensitive_keys=frozenset(),
                  allow_unratified=False, suspension_permits_self_description=False)
    kwargs.update(overrides)
    return check_item(item, **kwargs)


# --- seal 1: which kind ---------------------------------------------------------------


def test_the_eight_always_local_kinds_still_have_no_type_to_be_named_by():
    """The seal the ruling asked for, and it predates the ruling.

    A release path taking a kind as a parameter would let the next caller pass
    `ocr_output`. This one cannot: `kind_of` reads a TYPE, and seven types exist. A
    ninth door would have to be a ninth dataclass, written on purpose, by somebody
    who had to name it.
    """
    kinds = set(_KIND_BY_TYPE.values())
    for always_local in ALWAYS_LOCAL:
        assert always_local not in kinds, (
            f"{always_local!r} has acquired a releasable type; §8.4's always-local "
            "set is not a posture and nothing may name one")
        assert always_local not in ITEM_KINDS


def test_a_self_description_is_the_seventh_type_and_the_seventh_kind():
    assert kind_of(SelfDescription(question_id=A_ROLE)) == "self_description"
    assert len(_KIND_BY_TYPE) == len(ITEM_KINDS) == 7


def test_a_foreign_type_is_still_a_load_error():
    """The property that makes the count above mean something."""
    from privacy.vocabulary import OutOfVocabulary

    with pytest.raises(OutOfVocabulary):
        kind_of(object())


# --- seal 2: which row ----------------------------------------------------------------


def test_it_carries_a_reference_and_never_the_sentence():
    """SPEC §6: "references only, never materialised content", which every other item
    obeys. A field holding the words would make that sentence false for the one item
    whose words are the most sensitive thing in the product."""
    fields = {field.name for field in dataclasses.fields(SelfDescription)}

    assert fields == {"question_id"}
    for content in ("text", "value", "wording", "sentence", "description"):
        assert content not in fields


def test_it_cannot_address_any_row_but_a_role_declaration():
    """The second structural seal. A `question_id` is a key into P15's store, and
    without this the type could name any answer in it -- including one whose wording
    came from a file rather than from the person."""
    for other in ("reading.organization:CHEM2210", "branch:Coursework",
                  "nesting:x", "", "role", "rolex:me"):
        with pytest.raises(ValueError):
            SelfDescription(question_id=other)


def test_the_prefix_is_the_one_p15_actually_mints():
    """Spelled in `privacy` rather than imported, because P7 importing P15 is a
    layering inversion -- `readers/model_deepseek.py` states the same reason for
    spelling `locality="local"`. Spelling it means a test has to say the two are one
    value, or the seal quietly stops matching the ids P15 writes."""
    assert ROLE_QUESTION_PREFIX == f"{ROLE_KIND.kind_id}:"


# --- the tier: `80` §8.3's condition C1, which is that local is the default ------------


def test_the_flag_that_admits_a_filename_does_not_admit_this():
    """`gate.py` passes `allow_unratified=True` at both of its call sites. Reusing
    that flag would have admitted a self-description everywhere a filename is
    admitted -- a path that "happens to be called with" the right thing today, which
    is exactly what the ruling refused."""
    with pytest.raises(SelfDescriptionNotAdmitted):
        _check(SelfDescription(question_id=A_ROLE), allow_unratified=True)


def test_it_is_admitted_only_when_a_caller_asks_for_it_by_name():
    assert _check(SelfDescription(question_id=A_ROLE),
                  suspension_permits_self_description=True) is None


def test_neither_flag_has_a_default_anywhere_it_appears():
    """C1: "a developer who forgets this exception exists gets the safe behaviour."
    A default of False would be safe; a default of anything is a caller who never
    made the choice. No default means the TypeError arrives at import-time review."""
    parameters = inspect.signature(check_item).parameters

    assert parameters["suspension_permits_self_description"].default is inspect.Parameter.empty
    assert parameters["allow_unratified"].default is inspect.Parameter.empty


def test_the_other_six_kinds_are_unaffected_by_the_new_flag():
    """The suspension "reaches nothing but the self-description" (`80` §8.1). A flag
    that also loosened the filename would be the scope creep the amendment forbids."""
    from privacy.items import Filename

    with pytest.raises(UnratifiedItemKind):
        _check(Filename(file_id="f1"), suspension_permits_self_description=True)


# --- what the member has to carry -----------------------------------------------------


def test_the_seventh_member_records_its_own_approval():
    """`84` §1: adding a member to a closed vocabulary requires owner approval
    RECORDED AT THE MEMBER. Read from the source, because the whole point is that a
    later reader finds the reason beside the value rather than in a commit message."""
    text = (pathlib.Path(__file__).resolve().parents[2]
            / "src" / "privacy" / "vocabulary.py").read_text()
    # From the approval's own heading to the value it is about, so the window is
    # the record rather than a character count that silently stops covering it.
    member = text[text.index("THE SEVENTH"):
                  text.index("ITEM_KINDS: tuple[str, ...]")].lower()

    assert "2026-09-02" in member, "the approval is undated"
    assert "self_description" in member
    for owed in ("narrow", "local model", "deferring", "no tenth member"):
        assert owed in member, (
            f"the record does not mention {owed!r}. An approval that omits what was "
            "rejected, or which neighbouring vocabulary was NOT changed, is a note "
            "and not a record -- and this is the one the next reader will find "
            "instead of the ruling.")


def test_the_always_local_set_did_not_gain_a_member():
    """The vocabulary this is NOT. `80` §2: "NO TENTH MEMBER IS ADDED." The
    classification of a self-description as a `user_edits` item stands; what the
    ruling opens is a releasable KIND beside it, which is a different closed set."""
    assert len(ALWAYS_LOCAL) == 9
    assert "user_edits" in ALWAYS_LOCAL
    assert "self_description" not in ALWAYS_LOCAL
