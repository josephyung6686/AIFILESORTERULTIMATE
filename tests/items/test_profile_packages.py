"""Pluggable profiles load through one function. No detector branch on the name."""
from __future__ import annotations

from pathlib import Path

import pytest

from items.profile_loader import ProfileRefused, allows_relationship, load_profile


def test_student_and_files_only_load_through_one_loader():
    student = load_profile("student")
    files_only = load_profile("files_only")
    job = load_profile("job_seeker")
    assert student.profile_id == "student"
    assert files_only.profile_id == "files_only"
    assert job.profile_id == "job_seeker"
    assert "member-of" in student.relationship_types
    assert "member-of" not in files_only.relationship_types
    assert allows_relationship(files_only, "member-of") is False
    assert allows_relationship(files_only, "duplicate-of") is True
    assert "course" not in job.item_types
    assert job.raw.get("required_pairs")


def test_hold_bypass_keys_are_ignored():
    package = load_profile({
        "profile_id": "x",
        "profile_version": "1",
        "item_types": ["file"],
        "relationship_types": ["duplicate-of"],
        "clear_holds": True,
        "release_safety": ["identity"],
    })
    assert "clear_holds" not in package.raw
    assert "release_safety" not in package.raw


def test_bad_shape_is_refused():
    with pytest.raises(ProfileRefused):
        load_profile({"profile_id": "x"})


def test_detector_has_no_student_branch():
    path = Path(__file__).resolve().parents[2] / "src" / "recognition" / "detector.py"
    text = path.read_text(encoding="utf-8")
    assert 'profile == "student"' not in text
    assert 'profile_id == "student"' not in text
