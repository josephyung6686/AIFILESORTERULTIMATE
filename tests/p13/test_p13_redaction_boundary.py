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
        proposed_folder_name(display_label=PASSPORT,
                             derived_from_protected_material=True,
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
    assert proposed_folder_name(display_label="Academics",
                                derived_from_protected_material=False,
                                handling_class="public_low") == "Academics"


def test_the_refusal_does_not_consult_the_redaction_policy():
    """A folder name is not a display. `names = shown` is a decision about a
    screen; the directory outlives the screen."""
    parameters = inspect.signature(proposed_folder_name).parameters
    assert "settings" not in parameters
    # The keyword asks about the LABEL'S PROVENANCE, not the folder's contents.
    # A caller that handed it the folder's protectedness would strip the name
    # off every protected folder the person already has.
    assert "derived_from_protected_material" in parameters
    for settings in (SHOWN, NAMES_REDACTED):
        assert settings.names in ("shown", "redacted")
        with pytest.raises(ProposedNameFromProtectedMaterial):
            proposed_folder_name(display_label=PASSPORT,
                             derived_from_protected_material=True,
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
                                derived_from_protected_material=False,
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


# ==========================================================================
# `74` §6 B8 -- the rest of the boundary: the aggregate, the filename P13 never
# asks for, and the retraction limit.
#
# B8's named test is `test_no_review_action_is_constructible_over_untouched_protected`
# and its negative twin is `test_count_and_class_breakdown_never_produce_a_ratio`.
# The twin is a guard over the package, asserted against sabotage modules, because
# D11's two denominators are the kind of mistake that is invisible in a passing
# suite: the arithmetic runs, the number is plausible, and it describes an
# unprotected file as protected.
# ==========================================================================
import ast as _ast
import pathlib as _pathlib

from privacy.display import ProtectedSummary
from privacy.revocation import PriorRelease, RevocationResult

from review_surface.collect import ProtectedContainerHasNoAction, collect
from review_surface.presentation import record_presentation
from review_surface.redaction_boundary import (
    NameRedacted,
    ProtectedSetNotExpandable,
    name_for,
    protected_aggregate,
    retraction_statement,
)
from review_surface.vocabulary import (
    ACTIONS,
    SURFACES,
    UNTOUCHED_PROTECTED,
)

T0 = "2026-08-29T00:00:00Z"

#: §8.4's own example numbers, in P7's own record shape. `count` is the PROTECTED
#: count; `class_breakdown` is a census of the WHOLE SCOPE (D11).
SUMMARY = ProtectedSummary(
    count=11, scope_total=1842,
    class_breakdown={"public_low": 1600, "personal_non_sensitive": 231,
                     "sensitive_personal": 8,
                     "highly_sensitive_credential_bearing": 3,
                     "unreadable_unclassified": 0})


def test_no_review_action_is_constructible_over_untouched_protected(p13_conn):
    """`74` §6 B8's named test, and the wave's most important assertion.

    P13 SPEC:260-262 and `67` §1: a protected container is presented as its own
    inspectable list, labelled `untouched_protected`, and carries NO ACTION AT
    ALL. Applications and system items are never read or moved, so offering the
    user a choice would imply one exists.

    Asserted across the WHOLE product of surfaces and actions, and through both
    doors -- the subject itself and the payload's `subject_kind` -- because a
    refusal that held on the placement surface and not on the canvas would be a
    refusal in name only.
    """
    ref = record_presentation(
        p13_conn, surface=SURFACES[0], subject_ref=UNTOUCHED_PROTECTED,
        plan_version="plan-1", session_id="s-1", settings=SHOWN,
        evidence_refs=(), user_id="jy", component_version="p13-1",
        rendered_at=T0).presented_state_ref
    for surface in SURFACES:
        for action in ACTIONS:
            with pytest.raises(ProtectedContainerHasNoAction):
                collect(p13_conn, action_id="a-x", surface=surface,
                        subject_ref=UNTOUCHED_PROTECTED,
                        plan_version="plan-1", session_id="s-1", action=action,
                        correction_scope="file", presented_state_ref=ref,
                        user_id="jy", acted_at=T0, component_version="p13-1",
                        bulk_member_refs=("f-1",))
            with pytest.raises(ProtectedContainerHasNoAction):
                collect(p13_conn, action_id="a-y", surface=surface,
                        subject_ref="app-bundle-1", plan_version="plan-1",
                        session_id="s-1", action=action,
                        correction_scope="file", presented_state_ref=ref,
                        user_id="jy", acted_at=T0, component_version="p13-1",
                        bulk_member_refs=("f-1",),
                        payload={"subject_kind": UNTOUCHED_PROTECTED})
    # And nothing was written by any of those attempts.
    assert p13_conn.execute(
        "SELECT count(*) AS c FROM review_actions").fetchone()["c"] == 0
    # `untouched_protected` is not a surface and not an action, so there is no
    # place a gesture could be made even before `collect` is reached.
    assert UNTOUCHED_PROTECTED not in SURFACES
    assert UNTOUCHED_PROTECTED not in ACTIONS


#: Every name that carries one of D11's denominators. A division touching any of
#: these mixes two populations: `count` is the protected count, `class_breakdown`
#: is a census of the whole scope, and `scope_total` is files-in-scope.
_DENOMINATORS: tuple[str, ...] = ("count", "scope_total", "class_breakdown")


def _package_modules():
    import review_surface

    root = _pathlib.Path(review_surface.__file__).resolve().parent
    return [(path, _ast.parse(path.read_text()))
            for path in sorted(root.glob("*.py"))]


def _fake(source: str, name: str = "offender.py"):
    return [(_pathlib.Path(name), _ast.parse(source))]


def _ratios(trees) -> list[str]:
    """Every division or percentage whose operands touch D11's denominators."""
    offenders: list[str] = []
    for path, tree in trees:
        for node in _ast.walk(tree):
            if not isinstance(node, _ast.BinOp):
                continue
            if not isinstance(node.op, (_ast.Div, _ast.FloorDiv, _ast.Mod)):
                continue
            names = {sub.id for sub in _ast.walk(node)
                     if isinstance(sub, _ast.Name)}
            names |= {sub.attr for sub in _ast.walk(node)
                      if isinstance(sub, _ast.Attribute)}
            hit = names & set(_DENOMINATORS)
            if hit:
                offenders.append(f"{path.name}:{node.lineno} {sorted(hit)}")
    return offenders


def test_count_and_class_breakdown_never_produce_a_ratio(p13_conn):
    """`74` §6 B8's negative twin. D11, asserted arithmetically AND structurally.

    The two are different denominators. A percentage built from them would
    describe an unprotected file as protected, and it is exactly the sort of
    error a passing suite hides: the arithmetic runs and the number looks
    reasonable. So the aggregate is asserted to keep them apart, and the package
    is parsed for any division that touches either -- with the guard shown
    rejecting three sabotage modules, since one that found nothing in a clean
    package proves nothing about the guard.
    """
    aggregate = protected_aggregate(SUMMARY, settings=NAMES_REDACTED)
    assert sum(aggregate.class_breakdown.values()) == aggregate.scope_total
    assert sum(aggregate.class_breakdown.values()) != aggregate.count
    assert set(aggregate.class_breakdown) == set(HANDLING_CLASSES), (
        "`67` §1: every class is present and counted, zero-filled, never omitted")
    assert _ratios(_package_modules()) == []
    assert _ratios(_fake("share = summary.count / summary.scope_total\n"))
    assert _ratios(_fake("pct = count / sum(class_breakdown.values())\n"))
    assert _ratios(_fake("x = a / b\ny = scope_total // n\n"))
    # And an unrelated division is not caught, so the guard is about D11 rather
    # than about arithmetic.
    assert _ratios(_fake("half = width / two\n")) == []


def test_an_unprotected_file_shows_its_name_under_any_policy():
    assert name_for(protected=False, settings=NAMES_REDACTED,
                    filename="notes.pdf") == "notes.pdf"
    assert name_for(protected=False, settings=SHOWN,
                    filename="notes.pdf") == "notes.pdf"


def test_a_protected_file_shows_its_name_only_while_names_are_shown():
    assert name_for(protected=True, settings=SHOWN,
                    filename="passport.pdf") == "passport.pdf"


def test_no_surface_renders_a_filename_for_a_protected_file_when_names_redact():
    """Done-means 14. It RAISES rather than returning a masked string: a mask is
    still a code path that received the name and hid it."""
    with pytest.raises(NameRedacted) as caught:
        name_for(protected=True, settings=NAMES_REDACTED,
                 filename="passport.pdf")
    message = str(caught.value)
    assert "passport.pdf" not in message, (
        "the refusal must not leak the very name it refused")
    assert "passport" not in message
    # NOT `carries_no_material`: that instrument is for high-entropy material
    # like `A1234567`, where any two-character run is a leak. A filename is
    # ordinary English and shares runs with any sentence -- "as" appears in both
    # "passport" and "canvas" -- so applying it here would fail on a message that
    # leaks nothing. The right check for a name is the name.


def test_a_protected_set_renders_as_an_aggregate_and_does_not_expand():
    """Done-means 15, both clauses. §8.4's own example.

    "A summary such as '11 protected identity records' may be safe to show,
    while a visible list of passport filenames on a shared screen may not be."
    """
    aggregate = protected_aggregate(SUMMARY, settings=NAMES_REDACTED)
    assert aggregate.count == 11
    assert "11" in aggregate.sentence
    assert "protected" in aggregate.sentence
    assert aggregate.expandable is False
    with pytest.raises(ProtectedSetNotExpandable):
        aggregate.expand()


def test_the_aggregate_is_expandable_when_names_are_shown():
    aggregate = protected_aggregate(SUMMARY, settings=SHOWN)
    assert aggregate.expandable is True
    assert aggregate.expand() == ()


def test_a_revocation_lists_the_prior_releases_and_is_not_a_generic_disclaimer():
    """Done-means 17: a specific statement listing the prior releases."""
    result = RevocationResult(
        effective_from=T0,
        prior_releases=(
            PriorRelease(model="claude-x", provider="anthropic",
                         when="2026-08-01T00:00:00Z",
                         excerpts=("obs-1", "obs-2")),
            PriorRelease(model="claude-x", provider="anthropic",
                         when="2026-08-14T00:00:00Z", excerpts=("obs-9",)),
        ),
        retraction_limit=(
            "revocation cannot retract data already sent to an external "
            "provider"))
    statement = retraction_statement(result)
    assert statement.is_generic is False
    assert "2" in statement.sentence
    assert "anthropic" in statement.sentence
    assert "2026-08-01T00:00:00Z" in statement.sentence
    assert len(statement.prior_releases) == 2


def test_a_revocation_with_no_prior_releases_says_so_specifically():
    result = RevocationResult(
        effective_from=T0, prior_releases=(),
        retraction_limit="nothing was released under this policy")
    statement = retraction_statement(result)
    assert statement.is_generic is False
    assert "no" in statement.sentence.lower()


def test_the_statement_never_collapses_to_a_bare_disclaimer():
    """P7's own limit sentence survives INSIDE the statement, never as it."""
    result = RevocationResult(
        effective_from=T0,
        prior_releases=(PriorRelease(model="m", provider="p", when="t",
                                     excerpts=()),),
        retraction_limit="limit")
    statement = retraction_statement(result)
    assert statement.sentence != result.retraction_limit
    assert result.retraction_limit in statement.sentence
