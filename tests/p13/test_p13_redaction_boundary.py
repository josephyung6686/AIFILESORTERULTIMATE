"""§8.4's boundary, at the one place a label becomes a folder name.

`74` §5.6, from `69` §3 blocker 3: **a client's passport number became a group's
`display_label` and, under per-group acceptance, printed as a proposed FOLDER
NAME.** It is filed as "P13 + P12" and neither part's PLAN had a task for it.
This is the P13 half; P12's is `74` §6 C4.

A folder name is not a display. Redacting a filename on a screen is a display
decision that follows §8.4's policy; putting a passport number on the disk as a
directory is not, because the directory outlives the screen, is visible to
everyone with the volume, and appears in every backup, sync client and search
index thereafter. So the refusal here does NOT consult the redaction policy: it
holds whether names are shown or redacted.
"""
from __future__ import annotations

import inspect
import typing

import pytest

from privacy.display import HANDLING_CLASSES, RedactionSettings

from review_surface.redaction_boundary import (
    AggregateSafeLabel,
    ProposedNameFromProtectedMaterial,
    aggregate_safe_label,
    carries_no_material,
    proposed_folder_chain,
    proposed_folder_name,
)

SHOWN = RedactionSettings(names="shown", previews="shown", thumbnails="shown",
                          ocr_text="shown", location_data="shown")
NAMES_REDACTED = RedactionSettings(
    names="redacted", previews="shown", thumbnails="shown", ocr_text="shown",
    location_data="shown")

#: `69` §3 blocker 3's own case, in the shape it reached the report.
PASSPORT = "A1234567"
CREDENTIAL_BEARING = "highly_sensitive_credential_bearing"


# --------------------------------------------------------------------------
# `74` §6 A6's named failing test.
# --------------------------------------------------------------------------

def test_a_label_derived_from_protected_material_is_never_presented_as_a_folder_name():
    """`74` §6 A6's named test, and `69` §3 blocker 3 in one assertion.

    The refusal carries the aggregate the caller may show instead, so the answer
    to "what do I render then?" travels with the refusal rather than being left
    to whoever catches it.
    """
    with pytest.raises(ProposedNameFromProtectedMaterial) as caught:
        proposed_folder_name(display_label=PASSPORT, protected=True,
                             handling_class=CREDENTIAL_BEARING)
    assert PASSPORT not in str(caught.value), (
        "the refusal must not print the very material it refused")
    assert caught.value.aggregate == aggregate_safe_label(
        count=1, handling_class=CREDENTIAL_BEARING)


def test_the_aggregate_form_is_not_reachable_by_concatenating_the_redacted_parts():
    """`74` §6 A6's negative twin, against a masking redactor.

    Masking is the implementation this guard exists to catch: `A1234567` becomes
    `A1****67` and the reader now has both ends of a passport number, so the
    "redacted" form is the material minus some of its middle. Three halves:

    * the real aggregate carries no run of the material longer than one
      character;
    * the masked stand-in does, and the same check says so -- a check asserted
      only against the safe value passes just as well when it compares nothing;
    * and there is no PARAMETER through which the material could enter the
      aggregate in the first place, so there is nothing to concatenate. That is
      the structural half, and it is the one that keeps holding when someone
      later adds a field in a hurry.
    """
    safe = aggregate_safe_label(count=1, handling_class=CREDENTIAL_BEARING)
    assert carries_no_material(safe.text, PASSPORT)

    masked = "A1****67"
    assert not carries_no_material(masked, PASSPORT), (
        "a masking redactor leaves both ends of the material in place and the "
        "check must say so")

    parameters = inspect.signature(aggregate_safe_label).parameters
    assert set(parameters) == {"count", "handling_class"}, (
        f"aggregate_safe_label takes {sorted(parameters)}; a parameter that "
        "could carry the label is a route for the material to arrive")
    hints = typing.get_type_hints(AggregateSafeLabel)
    assert hints["count"] is int
    assert hints["handling_class"] is str
    assert set(hints) == {"count", "handling_class"}, (
        "there is no field a label could occupy, and a field that does not "
        "exist cannot be populated by a later caller in a hurry")


# --------------------------------------------------------------------------
# The rest of the boundary.
# --------------------------------------------------------------------------

def test_an_unprotected_label_becomes_its_folder_name_unchanged():
    assert proposed_folder_name(display_label="Academics", protected=False,
                                handling_class="public_low") == "Academics"


def test_the_refusal_does_not_consult_the_redaction_policy():
    """A folder name is not a display. `names = shown` is a decision about a
    screen; the directory outlives the screen."""
    assert "settings" not in inspect.signature(proposed_folder_name).parameters
    for settings in (SHOWN, NAMES_REDACTED):
        assert settings.names in ("shown", "redacted")
        with pytest.raises(ProposedNameFromProtectedMaterial):
            proposed_folder_name(display_label=PASSPORT, protected=True,
                                 handling_class=CREDENTIAL_BEARING)


def test_protectedness_is_p7s_flag_and_p13_derives_it_from_no_class():
    """P7's own rule: the protected COUNT follows the `protected` flag, never
    the handling class -- a `highly_sensitive_credential_bearing` record with
    `protected=False` is legal while P7's Open question 1 is unsettled. So P13
    publishes no sensitive-class set of its own and takes the flag it is given.

    `74` §5.6's P12 half (task C4) is written the other way round -- "a segment
    whose source node carries a protected `handling_class`" -- and that reading
    disagrees with P7. Flagged here, not resolved.
    """
    import ast
    import pathlib

    import review_surface.redaction_boundary as module

    assert proposed_folder_name(display_label="Passport Scans",
                                protected=False,
                                handling_class=CREDENTIAL_BEARING) == (
        "Passport Scans")

    source = pathlib.Path(module.__file__).read_text()
    tree = ast.parse(source)
    documentation = {id(node.value) for node in ast.walk(tree)
                     if isinstance(node, ast.Expr)
                     and isinstance(node.value, ast.Constant)
                     and isinstance(node.value.value, str)}
    spelled = [node.value for node in ast.walk(tree)
               if isinstance(node, ast.Constant)
               and isinstance(node.value, str)
               and node.value in HANDLING_CLASSES
               and id(node) not in documentation]
    assert spelled == [], (
        f"{spelled} are P7's handling classes spelled inside P13; publishing a "
        "second set of them answers P7's open question in P13's code")


def test_an_unknown_handling_class_is_refused():
    from review_surface.vocabulary import OutOfVocabulary

    with pytest.raises(OutOfVocabulary):
        aggregate_safe_label(count=1, handling_class="very_secret")


def test_the_aggregate_names_a_count_and_a_class_and_nothing_else():
    """§8.4's own example is "11 protected identity records": a number and a
    kind. Every WORD of it is deferred by the SPEC -- P13 fixes the information
    contract and fixes no copy -- so the text carries P7's class verbatim rather
    than inventing an English noun for it."""
    aggregate = aggregate_safe_label(count=11, handling_class=CREDENTIAL_BEARING)
    assert aggregate.count == 11
    assert aggregate.handling_class == CREDENTIAL_BEARING
    assert "11" in aggregate.text
    assert CREDENTIAL_BEARING in aggregate.text


def test_a_chain_refuses_at_the_protected_segment_and_names_which_one():
    """`69` §3's case is a chain: the group label became a TOP-LEVEL folder. A
    chain that refused only at the leaf would still have materialised it."""
    clean = proposed_folder_chain(
        (("Clients", False), ("Matters", False)),
        handling_class="public_low")
    assert clean == ("Clients", "Matters")

    with pytest.raises(ProposedNameFromProtectedMaterial) as caught:
        proposed_folder_chain(
            ((PASSPORT, True), ("Correspondence", False)),
            handling_class=CREDENTIAL_BEARING)
    assert caught.value.position == 0
    assert PASSPORT not in str(caught.value)


def test_a_protected_segment_anywhere_in_the_chain_is_refused():
    with pytest.raises(ProposedNameFromProtectedMaterial) as caught:
        proposed_folder_chain(
            (("Clients", False), ("Matters", False), (PASSPORT, True)),
            handling_class=CREDENTIAL_BEARING)
    assert caught.value.position == 2


def test_the_module_holds_no_numeric_literal_beyond_zero_and_one():
    """A count is read or passed, never chosen. A literal is how one gets chosen
    by accident."""
    import ast
    import pathlib

    import review_surface.redaction_boundary as module

    tree = ast.parse(pathlib.Path(module.__file__).read_text())
    offenders = [f"{node.lineno}:{node.value}" for node in ast.walk(tree)
                 if isinstance(node, ast.Constant)
                 and isinstance(node.value, int)
                 and not isinstance(node.value, bool)
                 and node.value not in (0, 1)]
    assert offenders == []
