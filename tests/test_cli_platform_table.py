# tests/test_cli_platform_table.py
"""`00` amendment 39: Mac and Linux laptops are the target, and the table may not guess.

`_FILESYSTEM_CONSTRAINTS` says of itself that "every field is a fact about the
filesystem this build runs on, and none of them may be guessed inside a part
package". These tests hold it to that sentence, and they hold it to BEHAVIOUR --
a test that asserts `unicode_form == "NFC"` proves only that the constant was
typed twice, and would still pass on a platform whose filesystem does something
else entirely.

So: what a name RESOLVES to and what two names COLLIDE under, per platform; and
that a platform nobody established is refused rather than handed somebody else's
answers. `sys.platform` is the seam, because it is the thing the block reads.
"""
from __future__ import annotations

import sys
import tomllib
import unicodedata
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cli  # noqa: E402
from mutation.names import (  # noqa: E402
    NameUnresolvable, collation_key, resolve_name,
)
from mutation.vocabulary import (  # noqa: E402
    RESERVED_NAME_AVOIDANCE, UNICODE_NORMALIZATION,
)

#: `sys.platform` -> the trove classifier that declares the same platform to
#: anybody installing the wheel. The code's list and the package's list are two
#: statements of one fact and this is the only place they are put side by side.
_CLASSIFIER_FOR = {
    "darwin": "Operating System :: MacOS :: MacOS X",
    "linux": "Operating System :: POSIX :: Linux",
}


def _on(monkeypatch, platform: str):
    """Build the table as it would be built on `platform`."""
    monkeypatch.setattr(sys, "platform", platform)
    return cli._filesystem_constraints()


# --------------------------------------------------------------------------------------
# A platform this build has not been reasoned about
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("platform", ["win32", "cygwin", "freebsd14", "sunos5"])
def test_a_platform_this_build_has_not_established_refuses(monkeypatch, platform):
    """The defect amendment 39 names: three `sys.platform` expressions each had an
    `else`, so every unlisted platform silently collected Linux's answers -- a
    4096-byte path budget, a case-SENSITIVE collision test and a two-character
    prohibited set -- and nothing anywhere said it had been guessed."""
    monkeypatch.setattr(sys, "platform", platform)
    with pytest.raises(SystemExit):
        cli._filesystem_constraints()


@pytest.mark.parametrize("platform", ["win32", "freebsd14"])
def test_the_refusal_names_the_platform_and_the_ones_that_were_established(
        monkeypatch, platform):
    """A refusal with a reason is an answer. It has to say which platform it is
    on and which two this build read, or the person cannot tell whether they are
    unsupported or misconfigured."""
    monkeypatch.setattr(sys, "platform", platform)
    with pytest.raises(SystemExit) as refusal:
        cli._filesystem_constraints()
    said = str(refusal.value)
    assert platform in said
    assert "darwin" in said and "linux" in said


def test_the_refusal_happens_before_a_table_exists(monkeypatch):
    """Not a warning beside a table built anyway. Nothing is returned."""
    monkeypatch.setattr(sys, "platform", "freebsd14")
    with pytest.raises(SystemExit):
        assert cli._filesystem_constraints() is None


# --------------------------------------------------------------------------------------
# The two platforms that were established
# --------------------------------------------------------------------------------------

def test_darwin_takes_a_colon_out_of_a_name_and_linux_leaves_it_in(monkeypatch):
    """A colon is the Finder's path separator and is shown to a person as `/`; on
    Linux it is an ordinary byte in a filename. So the same intended name resolves
    to two different names, and that difference is the field doing its job."""
    intended = "Invoice: March.pdf"
    on_darwin = resolve_name(intended, constraints=_on(monkeypatch, "darwin"),
                             directory_byte_length=10, has_extension=True)
    on_linux = resolve_name(intended, constraints=_on(monkeypatch, "linux"),
                            directory_byte_length=10, has_extension=True)
    assert on_darwin.filesystem_safe_name == "Invoice_ March.pdf"
    assert on_linux.filesystem_safe_name == "Invoice: March.pdf"


def test_darwin_sees_a_collision_between_two_cases_and_linux_does_not(monkeypatch):
    """The field that can destroy a file. APFS and HFS+ are case-insensitive by
    default, so `Resume.pdf` and `resume.pdf` are ONE path there and two on ext4."""
    darwin = _on(monkeypatch, "darwin")
    linux = _on(monkeypatch, "linux")
    assert (collation_key("Resume.pdf", constraints=darwin)
            == collation_key("resume.pdf", constraints=darwin))
    assert (collation_key("Resume.pdf", constraints=linux)
            != collation_key("resume.pdf", constraints=linux))


def test_the_path_budget_is_the_one_each_kernel_enforces(monkeypatch):
    """1024 on darwin (`PC_PATH_MAX`, measured), 4096 on Linux (`PATH_MAX` in
    `include/uapi/linux/limits.h`). A name that fits one does not fit the other,
    so this is checked by what gets truncated rather than by the number."""
    darwin = _on(monkeypatch, "darwin")
    linux = _on(monkeypatch, "linux")
    deep = 2000  # a directory longer than darwin's whole path budget
    with pytest.raises(NameUnresolvable):
        resolve_name("report.pdf", constraints=darwin,
                     directory_byte_length=deep, has_extension=True)
    fits = resolve_name("report.pdf", constraints=linux,
                        directory_byte_length=deep, has_extension=True)
    assert fits.filesystem_safe_name == "report.pdf"


def test_both_platforms_collide_two_names_that_differ_only_in_unicode_form(
        monkeypatch):
    """`unicode_form`'s behaviour, which is the same on both targets for two
    DIFFERENT reasons.

    On APFS the volume itself is normalization-insensitive -- it hashes the
    normalized form -- so `café.txt` and `café.txt` really are one path
    and finding the collision is accuracy. On ext4 a filename is an arbitrary
    byte string and the two would coexist, so finding the collision is the SAFE
    ERROR the block already chose: see one that is not there, stop and ask.
    """
    composed = unicodedata.normalize("NFC", "café.txt")
    decomposed = unicodedata.normalize("NFD", "café.txt")
    assert composed != decomposed
    for platform in ("darwin", "linux"):
        constraints = _on(monkeypatch, platform)
        assert (collation_key(composed, constraints=constraints)
                == collation_key(decomposed, constraints=constraints)), platform


def test_a_name_typed_in_the_composed_form_is_written_as_it_was_typed(monkeypatch):
    """WHICH form, not merely that there is one -- the test above passes under any
    single form and this one does not.

    Text arrives composed: from a keyboard, from a browser, from a PDF's title.
    NFD would rewrite every accented name a person gave this product, and on a
    Mac -- which preserves what it is handed -- that rewrite is what ends up on
    the disk and in the Finder. So a composed name must pass through untouched,
    with only a decomposed one recorded as normalized.
    """
    composed = unicodedata.normalize("NFC", "Café budget.pdf")
    decomposed = unicodedata.normalize("NFD", "Café budget.pdf")
    for platform in ("darwin", "linux"):
        constraints = _on(monkeypatch, platform)
        kept = resolve_name(composed, constraints=constraints,
                            directory_byte_length=10, has_extension=True)
        assert kept.filesystem_safe_name == composed, platform
        assert UNICODE_NORMALIZATION not in kept.normalizations_applied, platform

        changed = resolve_name(decomposed, constraints=constraints,
                               directory_byte_length=10, has_extension=True)
        assert changed.filesystem_safe_name == composed, platform
        assert UNICODE_NORMALIZATION in changed.normalizations_applied, platform


def test_neither_platform_reserves_a_name(monkeypatch):
    """`reserved_names` is empty on both, and empty is the CORRECT answer here --
    POSIX reserves no filename, so `CON.txt` and `aux` are ordinary names on a Mac
    and on Linux. The field exists for platforms where that is false, and this
    records that the emptiness was asked rather than left over."""
    for platform in ("darwin", "linux"):
        constraints = _on(monkeypatch, platform)
        assert constraints.reserved_names == frozenset(), platform
        for name in ("CON.txt", "aux", "NUL", "LPT1.pdf"):
            resolved = resolve_name(name, constraints=constraints,
                                    directory_byte_length=10,
                                    has_extension="." in name)
            assert resolved.filesystem_safe_name == name, (platform, name)
            assert RESERVED_NAME_AVOIDANCE not in resolved.normalizations_applied


# --------------------------------------------------------------------------------------
# What the package says it runs on
# --------------------------------------------------------------------------------------

def test_the_package_declares_the_platforms_the_code_accepts(monkeypatch):
    """`pyproject.toml` declared no operating system at all, so an installer had
    no way to learn what the code enforces. The two lists are one fact; this is
    where they are made to agree, so neither can gain a platform alone.

    THREE lists, in truth, and the third is the one that decides: the dispatch
    matches literal platform strings, so `_ESTABLISHED_PLATFORMS` could name a
    platform the function still refuses and the comparison below would not
    notice. Every name in the tuple is BUILT first, which is what keeps it from
    becoming a claim nothing honours.
    """
    for platform in cli._ESTABLISHED_PLATFORMS:
        _on(monkeypatch, platform)

    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    declared = tomllib.loads(pyproject.read_text())["project"]["classifiers"]
    operating_systems = {line for line in declared
                         if line.startswith("Operating System ::")}
    assert operating_systems == {
        _CLASSIFIER_FOR[platform] for platform in cli._ESTABLISHED_PLATFORMS}
