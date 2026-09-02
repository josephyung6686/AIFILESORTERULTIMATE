"""§8.3's file-name resolution, and the ONE key that decides collision.

The order of the five transformations is fixed and it matters: normalization form
first, because every later comparison is against the normalized string;
substitution next, because a prohibited character could otherwise survive into a
reserved-name comparison; reserved-name avoidance next, because it LENGTHENS the
name and must therefore happen before the budget is measured; truncation last.
Case folding is not a transformation of the written name at all -- see
`collation_key`.

*"The system should record the intended display name separately from the final
filesystem-safe name, so that collision and normalization changes remain
explainable."* (§8.3). `NameResolution` carries both, always, in every branch,
including the branch where nothing changed.

A4 -- no semantic renaming. `resolve_name` takes ONE name and returns a safe form
of that same name. There is deliberately no parameter through which a caller could
supply a different one, and `tests/p12/test_p12_names.py` checks the signature
rather than the body, because a body can be read two ways and a parameter cannot.
"""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass

from mutation.constraints import FilesystemConstraints
from mutation.vocabulary import (
    CASE_FOLDING, LENGTH_TRUNCATION, PROHIBITED_CHARACTER_SUBSTITUTION,
    RESERVED_NAME_AVOIDANCE, UNICODE_NORMALIZATION,
)


class NameUnresolvable(ValueError):
    """No safe name exists under these constraints. Refused, never emptied."""


@dataclass(frozen=True)
class NameResolution:
    intended_display_name: str
    filesystem_safe_name: str
    normalizations_applied: tuple[str, ...]
    target_case_sensitivity: bool
    target_path_length_limit: int


def _split(name: str, *, has_extension: bool) -> tuple[str, str]:
    """Stem and suffix. A directory label has no suffix, ever: `Taxes 2026.2027`
    is one label and splitting it would put `.2027` beyond the reach of
    truncation and then restore it as an extension it never was."""
    if not has_extension:
        return name, ""
    head, dot, tail = name.rpartition(".")
    if not dot or not head:
        return name, ""
    return head, f".{tail}"


def _truncate_to_bytes(text: str, budget: int) -> str:
    """The longest prefix of `text` whose UTF-8 encoding fits in `budget` bytes.

    Cuts on character boundaries by construction -- it shortens the string and
    re-measures rather than slicing the encoded bytes, so a multi-byte character
    is never left half-written. `budget` may be zero; the result is then empty and
    the caller decides that is unresolvable.
    """
    if len(text.encode("utf-8")) <= budget:
        return text
    cut = text
    while cut and len(cut.encode("utf-8")) > budget:
        cut = cut[:-1]
    return cut


def resolve_name(intended_display_name: str, *,
                 constraints: FilesystemConstraints,
                 directory_byte_length: int,
                 has_extension: bool) -> NameResolution:
    """§8.3's name normalization, applied BEFORE an action is planned.

    `directory_byte_length` is the UTF-8 length of the resolved destination
    directory. The separator between it and this component costs one byte, which
    is why the budget below subtracts one.
    """
    applied: list[str] = []
    if not intended_display_name or not intended_display_name.strip():
        raise NameUnresolvable("an empty or blank name is not a name")
    # A component made only of dots is a path traversal component, not a name.
    # This is structural in the same sense as `ALWAYS_PROHIBITED` -- there is no
    # filesystem on which `..` names a file -- so it is refused here rather than
    # left to an injected table. Under the CLI's own table nothing had an
    # opinion about it: `prohibited_characters` is {'/', '\0', ':'} and
    # `reserved_names` is empty, so `..`, `.` and `...` came back unchanged and
    # became directory components in the composed destination path
    # (`resolution.py`:311-319 puts every ancestor's `display_label` through
    # this function). `--label` is a free string the person types.
    if set(intended_display_name.strip()) == {"."}:
        raise NameUnresolvable(
            "a name made only of dots is a path traversal component, not a "
            "name; it cannot be a folder or a file")

    name = unicodedata.normalize(constraints.unicode_form, intended_display_name)
    if name != intended_display_name:
        applied.append(UNICODE_NORMALIZATION)

    prohibited = constraints.prohibited
    if any(character in prohibited for character in name):
        name = "".join(
            constraints.replacement_character if character in prohibited
            else character
            for character in name)
        applied.append(PROHIBITED_CHARACTER_SUBSTITUTION)

    stem, suffix = _split(name, has_extension=has_extension)
    folded_reserved = {reserved.casefold() for reserved in constraints.reserved_names}
    if stem.casefold() in folded_reserved:
        stem = f"{stem}{constraints.replacement_character}"
        applied.append(RESERVED_NAME_AVOIDANCE)
        name = f"{stem}{suffix}"

    component_budget = min(
        constraints.max_component_bytes,
        constraints.max_path_bytes - directory_byte_length - 1)
    if component_budget <= 0:
        raise NameUnresolvable(
            "the resolved destination directory leaves no room for a name under "
            f"a {constraints.max_path_bytes}-byte path limit")
    if len(name.encode("utf-8")) > component_budget:
        suffix_bytes = len(suffix.encode("utf-8"))
        if suffix_bytes >= component_budget:
            raise NameUnresolvable(
                "the extension alone exceeds the remaining budget; truncating it "
                "would change what kind of file this is")
        stem = _truncate_to_bytes(stem, component_budget - suffix_bytes)
        if not stem:
            raise NameUnresolvable("truncation would leave no name at all")
        name = f"{stem}{suffix}"
        applied.append(LENGTH_TRUNCATION)

    # Not a transformation of `name`: the case-folding DECISION Contract out §3
    # asks to be recorded. A4 forbids semantic renaming and capitalization is part
    # of the name the user chose, so the written name keeps its case on every
    # volume; only `collation_key` folds.
    if not constraints.case_sensitive:
        applied.append(CASE_FOLDING)

    return NameResolution(
        intended_display_name=intended_display_name,
        filesystem_safe_name=name,
        normalizations_applied=tuple(applied),
        target_case_sensitivity=constraints.case_sensitive,
        target_path_length_limit=constraints.max_path_bytes,
    )


def collation_key(name: str, *, constraints: FilesystemConstraints) -> str:
    """The key two names collide under on THIS volume. The only decider.

    Two rules from §8.3, in one function so they cannot drift apart:
    *"Case-insensitive filesystems can treat Resume.pdf and resume.pdf as one
    path, while a case-sensitive filesystem can store both"*, and *"Unicode
    normalization differs across operating systems and cloud services, making
    visually identical names potentially collide"* -- so names are compared under
    a single normalization form regardless of which form either was written in.

    Normalization is unconditional; folding is not. That asymmetry is the design's:
    a normalization difference is invisible to a person on every platform, and a
    case difference is visible on all of them and significant on some.
    """
    normalized = unicodedata.normalize(constraints.unicode_form, name)
    return normalized if constraints.case_sensitive else normalized.casefold()
