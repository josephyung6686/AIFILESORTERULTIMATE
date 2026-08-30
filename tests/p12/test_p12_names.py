"""§8.3's name rules. Nothing here reads a real filesystem: resolution is
evaluated against the TARGET volume's stated constraints, which is why the frozen
tree can hold no paths (SPEC, Contract out §3, rule 4).

The two composed forms below are built with `unicodedata.normalize` rather than
typed as literals. A combining acute is invisible in a diff and any tool that
normalizes this file on save would quietly turn the test into a tautology.
"""
from __future__ import annotations

import inspect
import unicodedata

import pytest

from mutation import names as names_module
from mutation import vocabulary as v
from mutation.constraints import (
    ALWAYS_PROHIBITED, ConstraintsRequired, FilesystemConstraints,
)
from mutation.names import NameUnresolvable, collation_key, resolve_name

MACOS = FilesystemConstraints(
    unicode_form="NFC", case_sensitive=False,
    max_component_bytes=255, max_path_bytes=1024,
    prohibited_characters=frozenset({":"}),
    reserved_names=frozenset(), replacement_character="_")

WINDOWS_LIKE = FilesystemConstraints(
    unicode_form="NFC", case_sensitive=False,
    max_component_bytes=255, max_path_bytes=260,
    prohibited_characters=frozenset('<>:"|?*'),
    reserved_names=frozenset({"CON", "PRN", "AUX", "NUL"}),
    replacement_character="_")

LINUX = FilesystemConstraints(
    unicode_form="NFC", case_sensitive=True,
    max_component_bytes=255, max_path_bytes=4096,
    prohibited_characters=frozenset(),
    reserved_names=frozenset(), replacement_character="_")

COMPOSED = unicodedata.normalize("NFC", "Café.pdf")
DECOMPOSED = unicodedata.normalize("NFD", "Café.pdf")


# --------------------------------------------------------------------------
# The pair Wave C2 names.
# --------------------------------------------------------------------------


def test_nfc_and_nfd_forms_of_one_name_collide_on_a_case_insensitive_volume():
    """§8.3: *"Unicode normalization differs across operating systems and cloud
    services, making visually identical names potentially collide."*

    The two strings are different sequences of code points and the same name to
    anyone looking at a folder. `collation_key` is the ONE function that decides
    collision, so the two must share a key -- on the case-insensitive volume the
    task names, and on the case-sensitive one too, because normalization is
    unconditional while folding is not.
    """
    assert COMPOSED != DECOMPOSED
    assert collation_key(COMPOSED, constraints=MACOS) == \
        collation_key(DECOMPOSED, constraints=MACOS)
    assert collation_key(COMPOSED, constraints=LINUX) == \
        collation_key(DECOMPOSED, constraints=LINUX)
    # And the resolved names themselves converge, so neither is written twice.
    assert resolve_name(COMPOSED, constraints=MACOS, directory_byte_length=20,
                        has_extension=True).filesystem_safe_name == \
        resolve_name(DECOMPOSED, constraints=MACOS, directory_byte_length=20,
                     has_extension=True).filesystem_safe_name


def _channels_for_a_different_name(function) -> tuple[str, ...]:
    """Every parameter of `function` through which a caller could hand it a name
    other than the one it was asked to make safe.

    A4 forbids semantic renaming: *"the only permitted name changes are
    filesystem-safety normalization and a deterministic collision suffix"*. The
    check is over the signature rather than the body, because a body can be read
    two ways and a parameter cannot: any string-typed parameter beside
    `intended_display_name` is a channel, whatever it is called.
    """
    signature = inspect.signature(function)
    channels = []
    for name, parameter in signature.parameters.items():
        if name == "intended_display_name":
            continue
        # `from __future__ import annotations` makes every annotation a string,
        # so this splits the union and compares WHOLE tokens. A substring test
        # would flag `FilesystemConstraints`, which contains "str" and carries
        # no name.
        annotation = str(parameter.annotation).strip("'\"")
        tokens = {piece.strip() for piece in annotation.split("|")}
        if "str" in tokens or "Optional[str]" in tokens:
            channels.append(name)
    return tuple(channels)


def test_resolve_name_has_no_parameter_through_which_a_different_name_can_be_supplied():
    """A4's negative twin. `_channels_for_a_different_name` is run below against
    a sabotage function that HAS such a parameter, so "the guard found nothing"
    is distinguishable from "the guard cannot find anything"."""
    assert _channels_for_a_different_name(resolve_name) == ()
    assert "intended_display_name" in inspect.signature(resolve_name).parameters

    def sabotage(intended_display_name: str, *,
                 constraints: FilesystemConstraints,
                 directory_byte_length: int,
                 has_extension: bool,
                 preferred_name: str | None = None):
        """The rename P12 is forbidden to perform, offered as a keyword."""

    assert _channels_for_a_different_name(sabotage) == ("preferred_name",)

    # The behavioural half: whatever comes back, the intended name is the one
    # that went in, in every branch including the untouched one.
    for name, constraints in (("Resume.pdf", LINUX), ("CON.txt", WINDOWS_LIKE),
                              ("Q3: Offer.pdf", WINDOWS_LIKE)):
        assert resolve_name(name, constraints=constraints,
                            directory_byte_length=20,
                            has_extension=True).intended_display_name == name


# --------------------------------------------------------------------------
# P12 PLAN Task 2.
# --------------------------------------------------------------------------


def test_constraints_have_no_defaults_and_refuse_an_absurd_value():
    with pytest.raises(TypeError):
        FilesystemConstraints(unicode_form="NFC", case_sensitive=False)
    with pytest.raises(ConstraintsRequired):
        FilesystemConstraints(
            unicode_form="NFC", case_sensitive=False, max_component_bytes=0,
            max_path_bytes=1024, prohibited_characters=frozenset(),
            reserved_names=frozenset(), replacement_character="_")
    with pytest.raises(ConstraintsRequired):
        FilesystemConstraints(
            unicode_form="utf8", case_sensitive=False, max_component_bytes=255,
            max_path_bytes=1024, prohibited_characters=frozenset(),
            reserved_names=frozenset(), replacement_character="_")
    with pytest.raises(ConstraintsRequired):
        FilesystemConstraints(
            unicode_form="NFC", case_sensitive=False, max_component_bytes=255,
            max_path_bytes=1024, prohibited_characters=frozenset(),
            reserved_names=frozenset(), replacement_character="/")


def test_an_ordinary_name_is_returned_untouched_and_records_no_normalization():
    got = resolve_name("Resume.pdf", constraints=LINUX,
                       directory_byte_length=20, has_extension=True)
    assert got.intended_display_name == "Resume.pdf"
    assert got.filesystem_safe_name == "Resume.pdf"
    assert got.normalizations_applied == ()
    assert got.target_case_sensitivity is True
    assert got.target_path_length_limit == 4096


def test_a_decomposed_name_is_normalized_and_the_change_is_recorded():
    got = resolve_name(DECOMPOSED, constraints=MACOS,
                       directory_byte_length=20, has_extension=True)
    assert got.filesystem_safe_name == COMPOSED
    assert v.UNICODE_NORMALIZATION in got.normalizations_applied
    assert got.intended_display_name == DECOMPOSED


def test_a_prohibited_character_is_substituted_and_recorded():
    got = resolve_name("Q3: Offer.pdf", constraints=WINDOWS_LIKE,
                       directory_byte_length=20, has_extension=True)
    assert got.filesystem_safe_name == "Q3_ Offer.pdf"
    assert v.PROHIBITED_CHARACTER_SUBSTITUTION in got.normalizations_applied


def test_a_separator_is_prohibited_even_when_the_injected_set_omits_it():
    assert "/" in ALWAYS_PROHIBITED and "\x00" in ALWAYS_PROHIBITED
    got = resolve_name("2026/2027 Offer.pdf", constraints=LINUX,
                       directory_byte_length=20, has_extension=True)
    assert got.filesystem_safe_name == "2026_2027 Offer.pdf"
    assert v.PROHIBITED_CHARACTER_SUBSTITUTION in got.normalizations_applied


def test_a_reserved_stem_is_avoided_by_appending_the_injected_character():
    got = resolve_name("CON.txt", constraints=WINDOWS_LIKE,
                       directory_byte_length=20, has_extension=True)
    assert got.filesystem_safe_name == "CON_.txt"
    assert v.RESERVED_NAME_AVOIDANCE in got.normalizations_applied


def test_reserved_matching_ignores_case_and_leaves_a_non_match_alone():
    assert resolve_name("con.txt", constraints=WINDOWS_LIKE,
                        directory_byte_length=20,
                        has_extension=True).filesystem_safe_name == "con_.txt"
    assert resolve_name("CONTRACT.txt", constraints=WINDOWS_LIKE,
                        directory_byte_length=20,
                        has_extension=True).filesystem_safe_name == "CONTRACT.txt"


def test_an_over_long_component_truncates_the_stem_and_keeps_the_extension():
    long_stem = "A" * 400
    got = resolve_name(f"{long_stem}.pdf", constraints=LINUX,
                       directory_byte_length=20, has_extension=True)
    assert got.filesystem_safe_name.endswith(".pdf")
    assert len(got.filesystem_safe_name.encode("utf-8")) == 255
    assert v.LENGTH_TRUNCATION in got.normalizations_applied
    assert got.intended_display_name == f"{long_stem}.pdf"


def test_truncation_also_respects_the_whole_path_budget():
    got = resolve_name("B" * 200 + ".pdf", constraints=WINDOWS_LIKE,
                       directory_byte_length=240, has_extension=True)
    assert len(got.filesystem_safe_name.encode("utf-8")) == 260 - 240 - 1
    assert v.LENGTH_TRUNCATION in got.normalizations_applied


def test_truncation_never_splits_a_character():
    got = resolve_name("é" * 400 + ".pdf", constraints=LINUX,
                       directory_byte_length=20, has_extension=True)
    encoded = got.filesystem_safe_name.encode("utf-8")
    assert len(encoded) <= 255
    assert encoded.decode("utf-8") == got.filesystem_safe_name


def test_a_name_with_no_room_left_is_unresolvable_rather_than_silently_empty():
    with pytest.raises(NameUnresolvable):
        resolve_name("report.pdf", constraints=WINDOWS_LIKE,
                     directory_byte_length=259, has_extension=True)
    with pytest.raises(NameUnresolvable):
        resolve_name("   ", constraints=LINUX,
                     directory_byte_length=20, has_extension=True)


def test_case_folding_is_a_recorded_decision_and_the_written_name_keeps_its_case():
    got = resolve_name("Resume.pdf", constraints=MACOS,
                       directory_byte_length=20, has_extension=True)
    assert got.filesystem_safe_name == "Resume.pdf"
    assert v.CASE_FOLDING in got.normalizations_applied
    assert got.target_case_sensitivity is False
    assert v.CASE_FOLDING not in resolve_name(
        "Resume.pdf", constraints=LINUX, directory_byte_length=20,
        has_extension=True).normalizations_applied


def test_resume_and_resume_are_one_name_on_a_folding_volume_and_two_otherwise():
    assert collation_key("Resume.pdf", constraints=MACOS) == \
        collation_key("resume.pdf", constraints=MACOS)
    assert collation_key("Resume.pdf", constraints=LINUX) != \
        collation_key("resume.pdf", constraints=LINUX)


def test_a_directory_label_is_not_split_on_its_last_dot():
    got = resolve_name("Taxes 2026.2027", constraints=LINUX,
                       directory_byte_length=20, has_extension=False)
    assert got.filesystem_safe_name == "Taxes 2026.2027"
    long_label = resolve_name("C" * 400, constraints=LINUX,
                              directory_byte_length=20, has_extension=False)
    assert len(long_label.filesystem_safe_name.encode("utf-8")) == 255


def test_names_is_the_one_home_for_the_collation_key():
    """Both §8.3 comparison rules -- case and Unicode form -- live in one
    function, so they cannot drift apart. Nothing else in P12 may fold or
    normalize for comparison."""
    assert names_module.collation_key is collation_key
