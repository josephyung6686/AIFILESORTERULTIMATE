"""The target volume's rules, injected. P12 authors none of them.

§8.3 names the CATEGORIES that must be handled -- invalid filename characters,
reserved names, prohibited characters on particular filesystems, platform-specific
path-length limits -- and enumerates no values. The SPEC's Deferred list says the
same in the other direction: *"These are platform facts to be authored as a data
asset, not design decisions."* So this record is required in full at every call
site and has no default anywhere. Absent means refuse, never guess.

`max_component_bytes` and `max_path_bytes` are measured on the UTF-8 encoding
AFTER normalization -- the unit APFS, HFS+ and ext4 enforce. Windows measures
UTF-16 code units; that is a property of the constraint table a platform author
will supply, and naming the unit on the field is what keeps the two from being
confused when they do.
"""
from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from pathlib import Path

#: The four Unicode normalization forms `unicodedata.normalize` accepts.
UNICODE_FORMS: tuple[str, ...] = ("NFC", "NFD", "NFKC", "NFKD")

#: Prohibited in a path COMPONENT on every filesystem, and not part of any
#: platform table. A component containing a separator is not a component, and a
#: component containing NUL cannot be passed to any system call. This is
#: structural, so it is not injected: there is no filesystem for which supplying
#: a different answer would be correct.
ALWAYS_PROHIBITED: frozenset[str] = frozenset({"/", "\\", "\x00"})


class ConstraintsRequired(RuntimeError):
    """A constraint that is absent, empty or self-contradicting."""


@dataclass(frozen=True)
class FilesystemConstraints:
    unicode_form: str
    case_sensitive: bool
    max_component_bytes: int
    max_path_bytes: int
    prohibited_characters: frozenset[str]
    reserved_names: frozenset[str]
    replacement_character: str

    def __post_init__(self) -> None:
        if self.unicode_form not in UNICODE_FORMS:
            raise ConstraintsRequired(
                f"unicode_form must be one of {UNICODE_FORMS}")
        if not isinstance(self.case_sensitive, bool):
            raise ConstraintsRequired(
                "case_sensitive is the target volume's answer, not a guess; it "
                "must be True or False")
        for name in ("max_component_bytes", "max_path_bytes"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ConstraintsRequired(f"{name} must be a positive integer")
        if self.max_component_bytes > self.max_path_bytes:
            raise ConstraintsRequired(
                "a component cannot be permitted to exceed the whole path budget")
        for name in ("prohibited_characters", "reserved_names"):
            if not isinstance(getattr(self, name), frozenset):
                raise ConstraintsRequired(f"{name} must be a frozenset")
        if (not isinstance(self.replacement_character, str)
                or len(self.replacement_character) != 1):
            raise ConstraintsRequired(
                "replacement_character is exactly one character")
        if (self.replacement_character in ALWAYS_PROHIBITED
                or self.replacement_character in self.prohibited_characters):
            raise ConstraintsRequired(
                "the replacement character cannot itself be prohibited; "
                "substitution would not terminate")

    @property
    def prohibited(self) -> frozenset[str]:
        """Everything that may not appear in a component on this volume."""
        return self.prohibited_characters | ALWAYS_PROHIBITED


class VolumeUnmeasurable(ConstraintsRequired):
    """The volume would not answer, so nothing may be declared about it."""


def measure_case_sensitivity(directory: Path) -> bool:
    """Whether `directory` distinguishes two names differing only in case.

    **`sys.platform` is not a fact about the target volume, and this module's
    first line says the table is the target volume's rules.** A Linux process
    reads `sys.platform == "linux"` and declares `case_sensitive=True` while
    filing onto an exFAT stick, an NTFS partition, an SMB share from a NAS or a
    `casefold`-enabled ext4 directory -- every one of which folds. That is not an
    exotic setup; it is what "help me organise my files" looks like when the
    files are on an external drive.

    So the volume is ASKED. A directory is made under a name nobody else will
    choose and the same name is looked for in the other case; if the volume
    hands back the directory that was just made, the two names are one name here.

    **This is a MEASUREMENT, not a policy**, which is why it may live in a part
    package: it authors no value and offers no default. The composition root
    still decides to call it and still owns the table it builds from the answer.

    **A probe that cannot run raises.** `VolumeUnmeasurable` rather than a guess,
    because a guess here is the defect this function exists to remove and the
    standing rule is that absent means refuse. A read-only destination is a real
    case and the honest answer is that this run cannot say what the volume does.

    Scope, stated because the limit matters: this measures ONE DIRECTORY.
    `casefold` on ext4 is a per-directory attribute, so a subdirectory created
    later under a different setting is not covered. That is the honest argument
    for why `movement.move_onto_free_path` is the load-bearing fix and this only
    narrows the miss -- measuring makes the SENTENCE right, the syscall makes the
    FILE safe.
    """
    probe = directory / f".case-probe-{uuid.uuid4().hex}"
    try:
        probe.mkdir()
    except OSError as exc:
        raise VolumeUnmeasurable(
            f"the case-sensitivity of {directory} could not be measured "
            f"({exc}); this run will not declare a rule it has not read"
        ) from exc
    try:
        return not (directory / probe.name.upper()).exists()
    finally:
        os.rmdir(probe)
