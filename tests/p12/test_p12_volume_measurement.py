"""The case-sensitivity of the target volume, read rather than assumed.

`sys.platform` answers for the process. The file goes on the disk.
"""
from __future__ import annotations

import pytest

from mutation.constraints import (
    VolumeUnmeasurable, measure_case_sensitivity,
)


def test_the_answer_matches_what_the_volume_actually_does(tmp_path):
    """Measured against the volume itself, in the other direction.

    The probe claims a folding volume returns False. The check writes one name
    and looks for the other -- if those two ever disagree the measurement is
    wrong, and it is the only thing standing between a person and a sentence
    about their file that is not true.
    """
    measured = measure_case_sensitivity(tmp_path)

    (tmp_path / "Ground.txt").write_bytes(b"A")
    folds = (tmp_path / "ground.txt").exists()
    assert measured is not folds


def test_the_probe_leaves_nothing_behind(tmp_path):
    """It runs in the person's own corpus root before they asked for a
    mutation, so it may not leave a directory there."""
    before = sorted(p.name for p in tmp_path.iterdir())
    measure_case_sensitivity(tmp_path)
    assert sorted(p.name for p in tmp_path.iterdir()) == before


def test_a_volume_that_will_not_answer_refuses_rather_than_guessing(tmp_path):
    """Absent means refuse. A guess here is the defect this removes."""
    read_only = tmp_path / "read-only"
    read_only.mkdir()
    read_only.chmod(0o500)
    try:
        with pytest.raises(VolumeUnmeasurable):
            measure_case_sensitivity(read_only)
    finally:
        read_only.chmod(0o700)


def test_a_directory_that_does_not_exist_refuses(tmp_path):
    with pytest.raises(VolumeUnmeasurable):
        measure_case_sensitivity(tmp_path / "never-made")
