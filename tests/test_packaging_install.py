"""Installed wheel must ship profiles and a runnable entry point (Task 1)."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import venv
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ("student", "files_only", "job_seeker")


def _build_wheel(dist_dir: Path) -> Path:
    """Build from an isolated project copy so concurrent pytest/build cannot
    race on the shared ``./build`` directory (empty wheels / missing profiles).
    """
    staging = Path(tempfile.mkdtemp(prefix="ga-wheel-src-"))
    try:
        # Minimal tree for setuptools src-layout discovery.
        for name in ("pyproject.toml", "README.md", "LICENSE"):
            src = ROOT / name
            if src.is_file():
                shutil.copy2(src, staging / name)
        shutil.copytree(
            ROOT / "src", staging / "src",
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
        )
        here = os.getcwd()
        try:
            os.chdir(staging)
            from setuptools import build_meta

            built = build_meta.build_wheel(str(dist_dir))
        finally:
            os.chdir(here)
        wheel = dist_dir / built
        assert wheel.is_file(), built
        return wheel
    finally:
        shutil.rmtree(staging, ignore_errors=True)


@pytest.fixture(scope="module")
def installed_wheel(tmp_path_factory):
    dist = tmp_path_factory.mktemp("dist")
    return _build_wheel(dist)


def test_wheel_contains_profiles_and_entry_point(installed_wheel: Path):
    with zipfile.ZipFile(installed_wheel) as archive:
        names = set(archive.namelist())
        ep = next(n for n in names if n.endswith(".dist-info/entry_points.txt"))
        text = archive.read(ep).decode("utf-8")
    for profile in PROFILES:
        assert f"items/profiles/{profile}.json" in names, (
            f"wheel missing items/profiles/{profile}.json"
        )
    assert "database-agent" in text
    assert "cli:main" in text


def test_installed_wheel_loads_profiles_and_cli(installed_wheel: Path, tmp_path: Path):
    """Install into a clean venv and exercise CLI without repo PYTHONPATH."""
    venv_dir = tmp_path / "venv"
    # Runtime deps stay empty; optional reader libs (docx, etc.) are host-provided.
    # system_site_packages keeps the install free of repo PYTHONPATH while still
    # allowing `database-agent --help` to import the optional readers layer.
    venv.create(venv_dir, with_pip=True, clear=True, system_site_packages=True)
    if sys.platform == "win32":
        python = venv_dir / "Scripts" / "python"
        script = venv_dir / "Scripts" / "database-agent"
    else:
        python = venv_dir / "bin" / "python"
        script = venv_dir / "bin" / "database-agent"

    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    env["PYTHONPATH"] = ""
    # Offline local wheel install; runtime deps are empty.
    pip = subprocess.run(
        [str(python), "-m", "pip", "install", "--no-deps", str(installed_wheel)],
        cwd=str(tmp_path),
        env=env,
        capture_output=True,
        text=True,
    )
    assert pip.returncode == 0, pip.stderr

    load_src = (
        "from items.profile_loader import load_profile\n"
        + "".join(
            f"p = load_profile({name!r}); assert p.profile_id\n"
            for name in PROFILES
        )
        + "print('profiles-ok')\n"
    )
    loaded = subprocess.run(
        [str(python), "-c", load_src],
        cwd=str(tempfile.gettempdir()),
        env=env,
        capture_output=True,
        text=True,
    )
    assert loaded.returncode == 0, loaded.stderr
    assert "profiles-ok" in loaded.stdout

    help_run = subprocess.run(
        [str(script), "--help"],
        cwd=str(tempfile.gettempdir()),
        env=env,
        capture_output=True,
        text=True,
    )
    assert help_run.returncode == 0, help_run.stderr + help_run.stdout

    cap = subprocess.run(
        [str(script), "ask", "--show-local-capability"],
        cwd=str(tempfile.gettempdir()),
        env=env,
        capture_output=True,
        text=True,
    )
    assert cap.returncode == 0, cap.stderr + cap.stdout
    assert (cap.stdout or cap.stderr).strip()
