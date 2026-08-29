# tests/p3/test_p3_access.py
import os
from pathlib import Path

import pytest

from scan_agent.access import FullDiskAccessRequired, require_access, unreadable_roots

needs_unprivileged = pytest.mark.skipif(
    hasattr(os, "geteuid") and os.geteuid() == 0,
    reason="root can list a 0o000 directory, so the TCC denial cannot be simulated",
)


def test_a_readable_root_passes(tmp_path: Path):
    (tmp_path / "Downloads").mkdir()
    require_access([tmp_path / "Downloads"])
    assert unreadable_roots([tmp_path / "Downloads"]) == ()


@needs_unprivileged
def test_an_unreadable_root_is_refused(tmp_path: Path):
    # 11 §1: "Until it is granted, P3 does not traverse."
    protected = tmp_path / "Documents"
    protected.mkdir()
    protected.chmod(0o000)
    try:
        assert unreadable_roots([protected]) == (protected,)
        with pytest.raises(FullDiskAccessRequired) as raised:
            require_access([protected])
        assert str(protected) in str(raised.value)
    finally:
        protected.chmod(0o700)


@needs_unprivileged
def test_one_unreadable_root_refuses_the_whole_check(tmp_path: Path):
    # A corpus quietly missing a whole root is §8.6's "understood and found
    # unimportant" failure. The refusal names every denied root, not just the first.
    ok = tmp_path / "Downloads"
    ok.mkdir()
    protected = tmp_path / "Documents"
    protected.mkdir()
    protected.chmod(0o000)
    try:
        with pytest.raises(FullDiskAccessRequired):
            require_access([ok, protected])
    finally:
        protected.chmod(0o700)


def test_a_missing_root_is_not_a_permission_problem(tmp_path: Path):
    # A path absent at scan time is SPEC Q14's territory and is recorded by the
    # traversal, not classified as a TCC denial here.
    assert unreadable_roots([tmp_path / "never-existed"]) == ()
    require_access([tmp_path / "never-existed"])


def test_p3_holds_no_list_of_protected_folders():
    # 11 §1 names Desktop, Downloads and Documents as examples. P3 encodes no
    # gazetteer of them: the OS's PermissionError is the oracle. (The module's
    # docstring quotes §1, so this checks bindings, not prose.)
    import scan_agent.access as module
    collections = [name for name, value in vars(module).items()
                   if not name.startswith("__")
                   and isinstance(value, (list, tuple, set, frozenset, dict))]
    assert collections == []
