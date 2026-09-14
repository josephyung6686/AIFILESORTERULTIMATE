"""Fixture-driven tests for the safety-critical paths.

Sizes matter (aborted-run detection is a size gap), so the fixture uses sparse files:
real byte counts, near-zero disk cost.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path, PurePosixPath

import pytest

from labsort.apply import Applier, CollisionError, move_exclusive, undo
from labsort.resolve import DateResolver, ExperimentResolver, InstrumentResolver, infer_year
from labsort.model import DateEvidence, Decision, Disposition, FileRef, Group, Plan


def sparse(path: Path, size: int, tag: bytes = b"") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(tag or b"\x01")
        if size > len(tag or b"\x01"):
            fh.truncate(size)
    return path


def make_group(gid: str, files: list[Path], cohort: str) -> Group:
    refs = tuple(FileRef.stat(f) for f in files)
    return Group(group_id=gid, members=refs, cohort_id=cohort, primary=refs[0])


def full(gid: str, dest: str) -> Decision:
    return Decision(
        group_id=gid, disposition=Disposition.FULL, reason="test",
        destination=PurePosixPath(dest),
        date_evidence=DateEvidence(value=date(2026, 8, 6), source="filename_iso"),
    )


def test_mmdd_year_inferred_from_mtime_ceiling():
    v, inferred = infer_year(7, 31, not_after=date(2026, 8, 14))
    assert (v, inferred) == (date(2026, 7, 31), True)


def test_mmdd_rolls_back_across_new_year():
    v, _ = infer_year(12, 31, not_after=date(2026, 1, 3))
    assert v == date(2025, 12, 31)


def test_filename_iso_beats_folder_and_mtime(tmp_path):
    f = sparse(tmp_path / "0731" / "Leica_2026-07-28 well3.jpeg", 2048)
    ev = DateResolver().resolve(FileRef.stat(f))
    assert (ev.value, ev.source) == (date(2026, 7, 28), "filename_iso")


def test_new_folder_dated_from_unanimous_siblings(tmp_path):
    d = tmp_path / "New Folder-copy-copy"
    sibs = [sparse(d / f"Leica_2026-08-06 well{i}.jpeg", 1024) for i in range(3)]
    target = sparse(d / "QS_0004.jpg", 1024)
    ev = DateResolver().resolve(FileRef.stat(target),
                               siblings=[FileRef.stat(s) for s in sibs])
    assert (ev.value, ev.source) == (date(2026, 8, 6), "sibling_filename")


def test_disagreeing_siblings_do_not_produce_a_date(tmp_path):
    d = tmp_path / "New Folder"
    sibs = [sparse(d / "Leica_2026-07-28 a.jpeg", 512),
            sparse(d / "Leica_2026-08-06 b.jpeg", 512)]
    target = sparse(d / "QS_0001.jpg", 512)
    ev = DateResolver().resolve(FileRef.stat(target),
                                siblings=[FileRef.stat(s) for s in sibs])
    assert ev.source == "mtime"
    assert not ev.sufficient_for_auto_move


def test_mtime_only_cannot_be_auto_moved():
    with pytest.raises(ValueError, match="better than mtime"):
        Decision(group_id="g", disposition=Disposition.FULL, reason="x",
                 destination=PurePosixPath("raw/2026-08-06/flow"),
                 date_evidence=DateEvidence(value=date(2026, 8, 6), source="mtime"))


def test_move_never_overwrites(tmp_path):
    src = sparse(tmp_path / "a" / "x.fcs", 100, b"AAAA")
    dst = sparse(tmp_path / "b" / "x.fcs", 200, b"BBBB")
    with pytest.raises(CollisionError):
        move_exclusive(src, dst)
    assert src.exists() and FileRef.stat(dst).size == 200


def test_same_name_different_size_is_not_a_duplicate(tmp_path):
    """Exp_20260806_1 (3 MB) vs _2 (13 KB): an aborted run, not a dupe."""
    a = sparse(tmp_path / "Exp_1" / "well 3.fcs", 3_000_000, b"REAL")
    b = sparse(tmp_path / "Exp_2" / "well 3.fcs", 13_000, b"ABRT")
    assert FileRef.stat(a).digest() != FileRef.stat(b).digest()


def build_plan(root: Path):
    img = sparse(root / "New Folder" / "Leica_2026-08-06 fib 2-5.jpeg", 4096, b"IMG")
    side = sparse(root / "New Folder" / "Leica_2026-08-06 fib 2-5.jpeg.metadata", 300, b"MET")
    g = make_group("g1", [img, side], cohort="New Folder")
    return Plan(run_id="run1", root=root, groups={"g1": g},
                decisions=[full("g1", "raw/2026-08-06/microscopy/leica")]), img, side


def test_dry_run_is_default_and_touches_nothing(tmp_path):
    plan, img, _ = build_plan(tmp_path)
    res = Applier(tmp_path, tmp_path / ".state").apply(plan)
    assert res.moved_files == 2 and img.exists()
    assert not (tmp_path / "raw").exists()


def test_sidecar_moves_with_its_image(tmp_path):
    plan, img, side = build_plan(tmp_path)
    res = Applier(tmp_path, tmp_path / ".state").apply(plan, dry_run=False)
    dest = tmp_path / "raw/2026-08-06/microscopy/leica"
    assert res.moved_files == 2
    assert (dest / img.name).exists() and (dest / side.name).exists()
    assert not img.exists()


def test_undo_restores_files_and_pruned_directories(tmp_path):
    plan, img, side = build_plan(tmp_path)
    res = Applier(tmp_path, tmp_path / ".state").apply(plan, dry_run=False)
    assert not (tmp_path / "New Folder").exists()
    restored, problems = undo(res.journal)
    assert (restored, problems) == (2, [])
    assert img.exists() and side.exists()


def test_group_rolls_back_when_one_member_fails(tmp_path):
    plan, img, side = build_plan(tmp_path)
    blocker = tmp_path / "raw/2026-08-06/microscopy/leica" / side.name
    sparse(blocker, 999, b"XXX")
    res = Applier(tmp_path, tmp_path / ".state").apply(plan, dry_run=False)
    assert res.moved_files == 0 and res.collisions == ["g1"]
    assert img.exists() and side.exists()


def test_rerun_skips_already_filed_without_error(tmp_path):
    plan, _, _ = build_plan(tmp_path)
    app = Applier(tmp_path, tmp_path / ".state")
    app.apply(plan, dry_run=False)
    dest = tmp_path / "raw/2026-08-06/microscopy/leica"
    refs = tuple(FileRef.stat(p) for p in sorted(dest.iterdir()))
    g = Group("g1", refs, cohort_id="raw", primary=refs[0])
    plan2 = Plan("run2", tmp_path, {"g1": g},
                 [full("g1", "raw/2026-08-06/microscopy/leica")])
    res = Applier(tmp_path, tmp_path / ".state").apply(plan2, dry_run=False)
    assert res.skipped_already_filed == 2 and res.collisions == []


def test_undo_leaves_edited_file_in_place(tmp_path):
    plan, img, _ = build_plan(tmp_path)
    res = Applier(tmp_path, tmp_path / ".state").apply(plan, dry_run=False)
    moved = tmp_path / "raw/2026-08-06/microscopy/leica" / img.name
    sparse(moved, 4096, b"EDIT")
    restored, problems = undo(res.journal)
    assert restored == 1 and any("changed since run" in p for p in problems)
    assert moved.exists()


def test_one_folder_can_mix_instruments(tmp_path):
    d = tmp_path / "20260806"
    leica = sparse(d / "Leica_2026-08-06 fib 2-5.jpeg", 512)
    evos = sparse(d / "QS_0004.jpg", 512)
    r = InstrumentResolver()
    assert r.resolve(FileRef.stat(leica)).subpath == "microscopy/leica"
    assert r.resolve(FileRef.stat(evos)).subpath == "microscopy/evos"


def test_flow_files_resolve_to_flow(tmp_path):
    r = InstrumentResolver()
    for n in ("well 3.fcs", "Exp_20260806_1.xit", "ExpSummaryForAPI.xml"):
        f = sparse(tmp_path / n, 256)
        assert r.resolve(FileRef.stat(f)).subpath == "flow"


def test_experiment_from_sibling_xit(tmp_path):
    d = tmp_path / "0806"
    xit = sparse(d / "Exp_20260806_1.xit", 128)
    fcs = sparse(d / "well 3.fcs", 4096)
    ev = ExperimentResolver().resolve(FileRef.stat(fcs), siblings=[FileRef.stat(xit)])
    assert (ev.name, ev.source) == ("Exp_20260806_1", "sibling_xit")


def test_experiment_from_folder_when_no_xit(tmp_path):
    fcs = sparse(tmp_path / "Exp_20260806_2" / "well 3.fcs", 4096)
    ev = ExperimentResolver().resolve(FileRef.stat(fcs))
    assert (ev.name, ev.source) == ("Exp_20260806_2", "folder_name")


def test_no_experiment_is_omitted_not_blocking(tmp_path):
    """raw/{date}/flow/ is a legal destination; a missing experiment segment must
    not push an otherwise routable tube into review."""
    fcs = sparse(tmp_path / "0731" / "f2.5.fcs", 4096)
    assert ExperimentResolver().resolve(FileRef.stat(fcs)) is None
