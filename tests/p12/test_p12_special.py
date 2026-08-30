"""SPEC §9's settled defaults for special objects and volumes.

`00`:174 supplies exactly three: *"avoid following symbolic links during
mutation, avoid moving package bundles unless explicitly approved, and refuse a
move if the source or destination is unavailable"*, plus the cloud rule --
*"treat cloud-synced paths as externally mutable, verify them immediately before
and after action, and pause when sync conflicts appear."*

Two things this file is careful about.

**The order is a security rule.** `69` §0: protected material is MARKED AND
COUNTED, NEVER OPENED. The package / system-item test runs FIRST, from the path
shape alone, before any link is resolved and before any `stat` that could follow
one into a bundle. The negative twin proves that by RUNTIME INTROSPECTION -- it
records every filesystem call the process makes and asserts none of them names
the container or anything beneath it. A text search for `os.stat` would pass an
implementation that reached the same syscall through `Path.exists()`.

**`74` §8 Q5 is the owner's and is open.** Locked files, files open in another
application, aliases and shortcuts have no defined behaviour anywhere in the
design. Nothing here detects one and no refusal class names one; the last test
in this file asserts that absence rather than leaving it to be discovered.
"""
from __future__ import annotations

import builtins
import os
import stat
from contextlib import contextmanager
from pathlib import Path

import pytest

from scan_agent.exclusion import REASON_PROTECTED_CONTAINER

from mutation import vocabulary as v
from mutation.special import ObjectVerdict, inspect_objects

RUNNING_AS_ROOT = hasattr(os, "geteuid") and os.geteuid() == 0


def _inspect(source, destination_directory, *, source_root=None,
             destination_root=None, conflicts=(), dataless=False,
             extra_protected=None):
    return inspect_objects(
        source=source, destination_directory=destination_directory,
        source_root=source_root if source_root is not None else source.parent,
        destination_root=(destination_root if destination_root is not None
                          else destination_directory),
        extra_protected=extra_protected,
        conflict_copies=lambda path: tuple(conflicts),
        dataless_of=lambda path: dataless)


@pytest.fixture()
def pair(fixture_root: Path):
    source = fixture_root / "Inbox" / "Syllabus.pdf"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"bytes")
    destination = fixture_root / "Coursework"
    destination.mkdir()
    return source, destination


# ---------------------------------------------------------------------------
# The runtime recorder the negative twin needs.
# ---------------------------------------------------------------------------

#: Every way this process can look at, list, or open a path. `os.stat` is the
#: one `Path.exists()`, `Path.is_file()` and `Path.stat()` all reach; `os.lstat`
#: is the one `os.path.islink` reaches; `os.open` and `open` are the two ways
#: bytes get read. Patching the `os` module functions catches `pathlib` and
#: `posixpath` because both look the name up on the module at call time.
_WATCHED = ("stat", "lstat", "scandir", "listdir", "open", "access", "readlink",
            "walk")


@contextmanager
def _recording():
    """Record the path argument of every filesystem call made inside the block.

    Runtime introspection, not a text search: an implementation that reached a
    protected container's bytes through `Path.exists()` or `shutil` would never
    contain the string `os.stat` and would be caught here anyway.
    """
    calls: list[tuple[str, str]] = []
    originals = {name: getattr(os, name) for name in _WATCHED}
    original_open = builtins.open

    def wrap(name, function):
        def recorder(path, *args, **kwargs):
            calls.append((name, str(path)))
            return function(path, *args, **kwargs)
        return recorder

    for name, function in originals.items():
        setattr(os, name, wrap(f"os.{name}", function))
    builtins.open = wrap("open", original_open)
    try:
        yield calls
    finally:
        for name, function in originals.items():
            setattr(os, name, function)
        builtins.open = original_open


def _touching(calls, root: Path) -> list[tuple[str, str]]:
    """Every recorded call naming `root` itself or anything beneath it."""
    prefix = str(root)
    return [call for call in calls
            if call[1] == prefix or call[1].startswith(f"{prefix}{os.sep}")]


# ---------------------------------------------------------------------------
# The pair Wave D4 names.
# ---------------------------------------------------------------------------


def test_a_package_bundle_is_refused_from_its_path_shape_without_being_opened(
        pair, fixture_root):
    """Done-means 10's package half. SPEC §9: *"Refuse. Absolutely, with no
    override."*

    The verdict comes from the SUFFIX ON THE PATH, and P3's ratified predicate
    supplies it. The unit of protection is the SUBTREE, not the entry -- P3's
    own docstring records an earlier version that protected `Numbers.app` and
    admitted `Numbers.app/Contents/sheet.numbers`, which is the exact read the
    rule forbids -- so a file inside one is refused too, and so is a bundle on
    the DESTINATION side.

    P12 also never receives such a file in the running system, because P3
    creates no `files` row inside a protected container. This check exists so a
    future caller that constructs a plan by hand is refused as well.
    """
    source, destination = pair
    bundle = source.parent / "Numbers.app"
    inside = bundle / "Contents" / "sheet.numbers"
    inside.parent.mkdir(parents=True)
    inside.write_bytes(b"never read")

    for path in (bundle, inside):
        verdict = _inspect(path, destination, source_root=fixture_root)
        assert verdict.refusal_class == v.PACKAGE_BUNDLE_UNAPPROVED
        assert verdict.permits_mutation is False
        assert verdict.detail["rule"] == REASON_PROTECTED_CONTAINER
        # Marked and counted, never opened, never silently omitted.
        assert verdict.detail["marked_and_counted"] == 1
        assert verdict.detail["message"] == v.decline_message(
            v.PACKAGE_BUNDLE_UNAPPROVED)

    # The destination end is checked by the same rule.
    into = destination / "Keynote.app" / "Contents"
    into.mkdir(parents=True)
    assert _inspect(source, into).refusal_class == v.PACKAGE_BUNDLE_UNAPPROVED

    # The path shape is the whole answer: a bundle whose contents cannot be
    # read at all is refused identically, and a bundle that does not exist on
    # disk at all is refused too.
    assert _inspect(source.parent / "Ghost.app", destination,
                    source_root=fixture_root).refusal_class == \
        v.PACKAGE_BUNDLE_UNAPPROVED

    # And it is not a blanket refusal: the ordinary pair still passes.
    assert _inspect(source, destination).permits_mutation is True


def test_no_stat_read_or_descent_occurs_on_a_protected_container(pair,
                                                                 fixture_root):
    """The negative twin, by RUNTIME INTROSPECTION.

    `69` §0's standing constraint is that a protected container is marked and
    counted and never opened. A text search for `os.stat` in the module would
    prove nothing: `Path.exists()`, `Path.is_file()`, `os.path.islink` and
    `shutil` all reach the same syscalls without containing that string. So
    every filesystem call the process makes is recorded and the assertion is
    that not one of them names the container or anything beneath it.

    Four cases, and then the check that makes the whole thing non-vacuous: an
    ORDINARY source is stat'd, so a recorder that recorded nothing would fail
    here rather than passing everything above.
    """
    source, destination = pair
    bundle = source.parent / "Numbers.app"
    inside = bundle / "Contents" / "sheet.numbers"
    inside.parent.mkdir(parents=True)
    inside.write_bytes(b"never read")
    destination_bundle = destination / "Keynote.app" / "Contents"
    destination_bundle.mkdir(parents=True)

    cases = (
        (bundle, destination, fixture_root, destination),
        (inside, destination, fixture_root, destination),
        (source, destination_bundle, source.parent, destination),
    )
    for source_path, destination_path, source_root, destination_root in cases:
        with _recording() as calls:
            verdict = inspect_objects(
                source=source_path, destination_directory=destination_path,
                source_root=source_root, destination_root=destination_root,
                extra_protected=None,
                conflict_copies=lambda path: (),
                dataless_of=lambda path: False)
        assert verdict.refusal_class == v.PACKAGE_BUNDLE_UNAPPROVED
        protected = (bundle if source_path in (bundle, inside)
                     else destination / "Keynote.app")
        assert _touching(calls, protected) == [], (
            f"a protected container was touched: {_touching(calls, protected)}")

    # A symlink INSIDE a bundle is a protected refusal, not a symlink one --
    # which is what proves the protected test runs BEFORE the link is resolved.
    link = bundle / "alias.pdf"
    link.symlink_to(source)
    with _recording() as calls:
        verdict = inspect_objects(
            source=link, destination_directory=destination,
            source_root=fixture_root, destination_root=destination,
            extra_protected=None, conflict_copies=lambda path: (),
            dataless_of=lambda path: False)
    assert verdict.refusal_class == v.PACKAGE_BUNDLE_UNAPPROVED
    assert _touching(calls, bundle) == []

    # Non-vacuous: an ordinary source IS looked at, so the recorder works.
    with _recording() as calls:
        assert inspect_objects(
            source=source, destination_directory=destination,
            source_root=source.parent, destination_root=destination,
            extra_protected=None, conflict_copies=lambda path: (),
            dataless_of=lambda path: False).permits_mutation is True
    assert _touching(calls, source) != []


# ---------------------------------------------------------------------------
# The rest of Done-means 10, and 11's decision half.
# ---------------------------------------------------------------------------


def test_an_ordinary_pair_permits_mutation(pair):
    verdict = _inspect(*pair)
    assert verdict.permits_mutation is True
    assert verdict.refusal_class is None and verdict.pause_reason is None


def test_a_symlink_source_is_not_followed(pair):
    source, destination = pair
    link = source.parent / "Shortcut.pdf"
    link.symlink_to(source)
    verdict = _inspect(link, destination)
    assert verdict.refusal_class == v.SYMLINK_NOT_FOLLOWED
    assert verdict.permits_mutation is False
    assert verdict.detail["target_not_resolved"] is True
    # The target is not in the record either. `00`:174 says do not FOLLOW it,
    # and a record naming where it points has followed it.
    assert str(source) not in str(verdict.detail)


def test_an_extra_predicate_can_only_add_protection(pair):
    """P3's predicate takes `extra` and it can only ADD: a caller cannot
    un-protect a `.app`, because the rule has no override and a predicate that
    could return False for one would be that override."""
    source, destination = pair
    assert _inspect(source, destination,
                    extra_protected=lambda path: True).refusal_class == \
        v.PACKAGE_BUNDLE_UNAPPROVED
    bundle = source.parent / "Safari.app"
    bundle.mkdir()
    assert _inspect(bundle, destination, source_root=source.parent,
                    extra_protected=lambda path: False).refusal_class == \
        v.PACKAGE_BUNDLE_UNAPPROVED


def test_a_missing_source_root_is_unavailable(pair, fixture_root):
    source, destination = pair
    verdict = _inspect(source, destination,
                       source_root=fixture_root / "DetachedDrive")
    assert verdict.refusal_class == v.SOURCE_OR_DESTINATION_UNAVAILABLE
    assert verdict.detail["unavailable"] == "source"


def test_a_missing_destination_root_is_unavailable(pair, fixture_root):
    source, destination = pair
    verdict = _inspect(source, destination,
                       destination_root=fixture_root / "UnmountedVolume")
    assert verdict.refusal_class == v.SOURCE_OR_DESTINATION_UNAVAILABLE
    assert verdict.detail["unavailable"] == "destination"


def test_a_vanished_source_is_unavailable(pair):
    source, destination = pair
    source.unlink()
    assert _inspect(source, destination).refusal_class == \
        v.SOURCE_OR_DESTINATION_UNAVAILABLE


def test_a_dataless_item_is_refused_and_never_downloaded(pair):
    """SPEC §9: *"Refuse -- do not hash, copy, or download in order to move."*
    This is §8.3's existing source-unavailable refusal wearing a detail, not a
    sixth staleness trigger. Materialization is a user action."""
    source, destination = pair
    with _recording() as calls:
        verdict = _inspect(source, destination, dataless=True)
    assert verdict.refusal_class == v.SOURCE_OR_DESTINATION_UNAVAILABLE
    assert verdict.detail["dataless"] is True
    assert [call for call in calls if call[0] == "open"] == []


def test_a_cloud_sync_conflict_pauses_rather_than_refusing(pair):
    """Done-means 11's decision half. A pause is not a refusal: the plan is
    still good and a sync agent is mid-flight, so the person is told to wait
    rather than told no."""
    source, destination = pair
    copies = ("Syllabus (conflicted copy 2026-08-29).pdf",)
    verdict = _inspect(source, destination, conflicts=copies)
    assert verdict.pause_reason == v.CLOUD_SYNC_CONFLICT
    assert verdict.refusal_class is None
    assert verdict.permits_mutation is False
    assert verdict.detail["conflict_copies"] == copies


def test_every_verdict_carries_the_66_10_sentence_for_what_it_decided(pair):
    source, destination = pair
    link = source.parent / "link.pdf"
    link.symlink_to(source)
    assert _inspect(link, destination).detail["message"] == \
        v.decline_message(v.SYMLINK_NOT_FOLLOWED)
    assert _inspect(source, destination, conflicts=("x",)).detail["message"] == \
        v.decline_message(f"paused:{v.CLOUD_SYNC_CONFLICT}")
    assert _inspect(source, destination,
                    dataless=True).detail["message"] == v.decline_message(
        v.SOURCE_OR_DESTINATION_UNAVAILABLE)


def test_a_verdict_cannot_be_both_a_refusal_and_a_pause(pair):
    """They are different things to tell a person -- *"no"* and *"not yet"* --
    and a record carrying both would let a caller show either."""
    source, destination = pair
    with pytest.raises(ValueError):
        ObjectVerdict(refusal_class=v.SYMLINK_NOT_FOLLOWED,
                      pause_reason=v.CLOUD_SYNC_CONFLICT, detail={})


# ---------------------------------------------------------------------------
# Injected with no default, and the gap Q5 leaves, stated rather than filled.
# ---------------------------------------------------------------------------


def test_the_three_environment_predicates_are_injected_with_no_default(pair):
    """A7. Whether a path is dataless, whether a sync agent has left conflict
    copies beside it, and which extra containers a deployment protects are all
    facts about the machine. `src/mutation/` answers none of them and defaults
    none of them: omitting one is a `TypeError`, and there is no branch that
    treats an absent answer as `False`."""
    source, destination = pair
    common = dict(source=source, destination_directory=destination,
                  source_root=source.parent, destination_root=destination)
    with pytest.raises(TypeError):
        inspect_objects(**common, extra_protected=None,
                        conflict_copies=lambda path: ())
    with pytest.raises(TypeError):
        inspect_objects(**common, extra_protected=None,
                        dataless_of=lambda path: False)
    with pytest.raises(TypeError):
        inspect_objects(**common, conflict_copies=lambda path: (),
                        dataless_of=lambda path: False)


@pytest.mark.skipif(RUNNING_AS_ROOT, reason="root opens a mode-000 file")
def test_a_locked_or_open_file_has_no_defined_behaviour_and_none_is_invented(
        pair):
    """`74` §8 Q5, stated as a test rather than left to be discovered.

    §8.3 *"requires defined behavior for locked files, files currently open in
    another application, ... aliases, shortcuts"* and supplies none. So P12
    detects none of them and no refusal class names one -- a class invented
    here would be P12 answering an open question of the owner's in code, which
    is the one thing this package may not do.

    What that means concretely, and what the composition root must know: an
    unreadable file passes THIS check and is caught one step later, by §8.3's
    fifth staleness trigger, which is why `permission_lost` is not among the
    classes below either.
    """
    source, destination = pair
    for word in ("lock", "open_in", "alias", "shortcut"):
        assert not any(word in refusal for refusal in v.REFUSAL_CLASSES)

    original = source.stat().st_mode
    os.chmod(source, 0)
    try:
        verdict = _inspect(source, destination)
    finally:
        os.chmod(source, stat.S_IMODE(original))
    assert verdict.permits_mutation is True
    assert verdict.refusal_class is None
