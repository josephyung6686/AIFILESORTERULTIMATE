# tests/p3/test_p3_authored_categories.py
"""§1.1's five categories, authored from a real disk instead of left empty.

§1.1 names eleven literal directory names AND five open-ended categories -- "build
artifacts, caches, auto-save folders, previews, and generated dependency trees". The
eleven were transcribed; the five were mapped to empty tuples, with the module saying
why: *"the category members are a hand-authored list and are not guessed here"* and
*"the rule below is wired against this mapping, so authoring the list is a data
change, not a code one."*

This is that data change, and every member below was measured on the owner's own
disk rather than recalled:

    .venv           23,372 files in 4 directories   generated dependency trees
    .next            1,241 files in 1 directory     build artifacts
    coverage            75 files in 1 directory     build artifacts
    .pytest_cache       33 files in 6 directories   caches
    .cache               0 files in 1 directory     caches

`.venv` alone is 23,372 files -- more than twice the 10,476 real files on that
Desktop. Read as the person's own material, it would have been scanned, extracted,
classified and offered a home.

Nothing here is a guess about directories the owner does not have. A name is added
when a real directory carries it, which is what keeps this a list of observations
rather than a gazetteer of everything a package manager has ever produced.
"""
from __future__ import annotations

from pathlib import Path

from scan_agent.exclusion import (
    CATEGORY_MEMBERS, EXCLUDED_DIRECTORY_NAMES, EXCLUSION_CATEGORIES,
    PROJECT_ROOT_MARKERS, RULE_CATEGORY, RULE_PROJECT_ROOT_DESCENDANT,
    exclusion_for, project_root_markers_in)


def test_every_category_key_is_still_one_of_the_designs_five():
    """The keys are §1.1's, and authoring members may not invent a sixth."""
    assert set(CATEGORY_MEMBERS) == set(EXCLUSION_CATEGORIES)


def test_the_eleven_literal_names_are_untouched():
    """The literal list is §1.1 verbatim. Authoring a CATEGORY must not edit it."""
    assert EXCLUDED_DIRECTORY_NAMES == (
        "node_modules", ".git", "venv", "build", "dist", "target", "vendor",
        "Pods", "site-packages", "Library", "__pycache__")


def test_a_dot_venv_is_a_generated_dependency_tree(tmp_path):
    """The list carries `venv`; the modern spelling is `.venv`, and it is 23,372
    files on this disk. A literal-name list cannot reach it -- the name differs --
    and that is exactly what the categories are for."""
    verdict = exclusion_for(tmp_path / ".venv", is_dir=True, applies_to="scanned")
    assert verdict is not None
    assert verdict.rule == RULE_CATEGORY
    assert verdict.rule_subject == "generated dependency trees"


def test_a_next_build_directory_is_a_build_artifact(tmp_path):
    verdict = exclusion_for(tmp_path / ".next", is_dir=True, applies_to="scanned")
    assert verdict is not None
    assert verdict.rule_subject == "build artifacts"


def test_a_pytest_cache_is_a_cache(tmp_path):
    verdict = exclusion_for(tmp_path / ".pytest_cache", is_dir=True,
                            applies_to="scanned")
    assert verdict is not None
    assert verdict.rule_subject == "caches"


def test_an_ordinary_folder_of_the_persons_own_work_is_untouched(tmp_path):
    """The negative twin, and the one that matters most.

    Every test above passes for a rule that excluded everything. These names are
    close to real folders a person keeps -- `coverage` is a build artifact AND a
    word an insurance file would use -- so the refusal has to be checked directly.
    """
    for name in ("Documents", "Vaccine records", "SAT Tests", "Arduino",
                 "Chinese University Application Materials", "research"):
        assert exclusion_for(tmp_path / name, is_dir=True,
                             applies_to="scanned") is None, name


def test_a_FILE_named_like_a_category_member_is_not_excluded(tmp_path):
    """§1.1's categories are DIRECTORIES. A file called `coverage` is a file."""
    assert exclusion_for(tmp_path / "coverage", is_dir=False,
                         applies_to="scanned") is None


# --------------------------------------------------------------------------
# The fifth project-root marker.
# --------------------------------------------------------------------------

def test_an_arduino_library_is_a_software_project_root(tmp_path):
    """`library.properties` is Arduino's `package.json`, and 226 of the owner's 228
    Arduino files sit under one.

    §1.1's list is "files such as `package.json`, `requirements.txt`, `Cargo.toml`,
    or `go.mod`" -- the module's own note says "such as" signals an extensible set
    and any extension is hand-authored. This is that extension, and it is the same
    kind of thing as the other four: the manifest a dependency manager writes.
    """
    assert "library.properties" in PROJECT_ROOT_MARKERS
    markers = project_root_markers_in(
        [("library.properties", False), ("src", True), ("README.adoc", False)])
    assert markers == ("library.properties",)


def test_the_original_four_markers_still_come_first(tmp_path):
    """Order is §1.1's, and the authored fifth goes after the design's four."""
    assert PROJECT_ROOT_MARKERS[:4] == (
        "package.json", "requirements.txt", "Cargo.toml", "go.mod")


def test_a_directory_named_library_properties_is_not_a_marker():
    """§1.1 says the markers are FILES. The negative twin the helper already had."""
    assert project_root_markers_in([("library.properties", True)]) == ()


def test_a_file_under_an_arduino_library_is_excluded_as_a_descendant(tmp_path):
    verdict = exclusion_for(tmp_path / "Adafruit_GFX" / "Adafruit_GFX.cpp",
                            is_dir=False, applies_to="scanned",
                            project_root_markers=("library.properties",))
    assert verdict is not None
    assert verdict.rule == RULE_PROJECT_ROOT_DESCENDANT
    assert verdict.rule_subject == "library.properties"


# --------------------------------------------------------------------------
# The markers §1.1's four do not reach.
# --------------------------------------------------------------------------

def test_a_python_project_root_is_recognised_by_pyproject_toml():
    """§1.1 names `requirements.txt`; modern Python projects ship `pyproject.toml`.

    Measured on the owner's disk: 5 directories carry one, 3 carry `setup.py`,
    18 carry `CMakeLists.txt`. Between them they hold 71,517 files -- vendored C++
    libraries (libzip 907, Catch2 575, pugixml 83) and two large project trees
    (a podcast generator at 36,409 files, an archived app at 31,269) -- every one
    of them read as the owner's own writing because the four markers §1.1 spells
    happen not to appear at their roots.

    §1.1's list is "files such as `package.json`, `requirements.txt`,
    `Cargo.toml`, or `go.mod`" and the module's own note calls "such as" an
    extensible set whose extensions are hand-authored. These three are the same
    KIND of thing as the four: the manifest that marks the root of a source tree.
    """
    for marker in ("pyproject.toml", "setup.py", "CMakeLists.txt"):
        assert marker in PROJECT_ROOT_MARKERS, marker
        assert project_root_markers_in(
            [("README.md", False), (marker, False), ("src", True)]) == (marker,)


def test_the_designs_four_still_come_first_and_unedited():
    """Authoring a fifth, sixth or seventh may not reorder or edit §1.1's own."""
    assert PROJECT_ROOT_MARKERS[:4] == (
        "package.json", "requirements.txt", "Cargo.toml", "go.mod")


def test_a_source_file_under_a_cmake_tree_is_excluded_as_a_descendant(tmp_path):
    """The libzip case: 907 files, including the `filename_duplicate.zip` that
    crashed a whole 5,760-file run before commit 446d7f3."""
    verdict = exclusion_for(tmp_path / "libzip" / "regress" / "add_from_zip.c",
                            is_dir=False, applies_to="scanned",
                            project_root_markers=("CMakeLists.txt",))
    assert verdict is not None
    assert verdict.rule == RULE_PROJECT_ROOT_DESCENDANT


def test_a_folder_of_the_persons_own_documents_is_not_a_project_root():
    """The negative twin. A marker is a FILE at the root of a source tree; a
    folder of essays that happens to contain a text file is not one."""
    assert project_root_markers_in(
        [("Additional information.docx", False), ("CU Activities list.xlsx", False),
         ("notes.txt", False), ("Essays", True)]) == ()
