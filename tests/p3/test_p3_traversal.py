# tests/p3/test_p3_traversal.py
import os
from pathlib import Path

import pytest

from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.deferrals import (
    DEFERRED_BUDGET, DEFERRED_DIRECTORY_UNREADABLE, DEFERRED_PATH_ABSENT,
    DEFERRED_TRAVERSAL_UNRESOLVED,
)
from scan_agent.exclusion import (
    APPLIES_TO_CANDIDATE_ROOT, APPLIES_TO_SCANNED_SOURCE, EXCLUDED_DIRECTORY_NAMES,
    PROJECT_ROOT_MARKERS, ExclusionVerdict, RULE_LITERAL_DIRECTORY_NAME,
    RULE_PROJECT_ROOT_DESCENDANT,
)
from scan_agent.traversal import Deferred, ObservedDirectory, ObservedFile, walk

NEVER = lambda: False           # a caller with no ceiling (§8.6 names none for traversal)

needs_unprivileged = pytest.mark.skipif(
    hasattr(os, "geteuid") and os.geteuid() == 0,
    reason="root can list a 0o000 directory, so the refusal cannot be simulated",
)


def _walk(root, *, sources=None, roots=None, budget=NEVER):
    return list(walk(FilesystemCorpusSource(),
                     sources=[root] if sources is None else sources,
                     candidate_roots=[] if roots is None else roots,
                     budget_exhausted=budget))


class RecordingSource(FilesystemCorpusSource):
    def __init__(self):
        self.listed = []

    def entries(self, directory):
        self.listed.append(str(directory))
        return super().entries(directory)


def test_no_source_set_means_no_traversal(corpus: Path):
    # Done-means 2: "Given no source set, zero rows and zero traversal — no default
    # corpus is synthesized."
    source = RecordingSource()
    items = list(walk(source, sources=[], candidate_roots=[], budget_exhausted=NEVER))
    assert items == []
    assert source.listed == []


def test_one_observed_file_per_non_excluded_file(corpus: Path):
    (corpus / "a.txt").write_bytes(b"a")
    (corpus / "sub").mkdir()
    (corpus / "sub" / "b.pdf").write_bytes(b"b")
    files = [i for i in _walk(corpus) if isinstance(i, ObservedFile)]
    assert sorted(f.path for f in files) == [
        str(corpus / "a.txt"), str(corpus / "sub" / "b.pdf"),
    ]
    assert all(f.applies_to == APPLIES_TO_SCANNED_SOURCE for f in files)


def test_each_of_the_eleven_names_is_pruned(corpus: Path):
    # Done-means 3, and the walking skeleton's assertion on node_modules.
    for name in EXCLUDED_DIRECTORY_NAMES:
        directory = corpus / name
        directory.mkdir()
        (directory / "buried.txt").write_bytes(b"x")
        (directory / "deeper").mkdir()
        (directory / "deeper" / "deeper.txt").write_bytes(b"x")
    (corpus / "keep.txt").write_bytes(b"k")

    items = _walk(corpus)
    files = [i for i in items if isinstance(i, ObservedFile)]
    assert [f.path for f in files] == [str(corpus / "keep.txt")]

    verdicts = [i for i in items if isinstance(i, ExclusionVerdict)]
    assert {v.rule_subject for v in verdicts} == set(EXCLUDED_DIRECTORY_NAMES)
    assert {v.rule for v in verdicts} == {RULE_LITERAL_DIRECTORY_NAME}
    # pruned, not filtered: nothing inside them was ever listed
    assert not any("buried" in v.path or "deeper" in v.path for v in verdicts)


def test_a_pruned_directory_is_never_listed(corpus: Path):
    (corpus / "node_modules").mkdir()
    (corpus / "node_modules" / "pkg").mkdir()
    source = RecordingSource()
    list(walk(source, sources=[corpus], candidate_roots=[], budget_exhausted=NEVER))
    assert str(corpus / "node_modules") not in source.listed


def test_a_project_root_yields_no_files_from_its_descendants(corpus: Path):
    # Done-means 4, for each of §1.1's four markers.
    for index, marker in enumerate(PROJECT_ROOT_MARKERS):
        project = corpus / f"project{index}"
        (project / "src").mkdir(parents=True)
        (project / marker).write_bytes(b"{}")
        (project / "notes.md").write_bytes(b"notes")
        (project / "src" / "main.rs").write_bytes(b"code")
    (corpus / "essay.docx").write_bytes(b"essay")

    items = _walk(corpus)
    files = [i for i in items if isinstance(i, ObservedFile)]
    assert [f.path for f in files] == [str(corpus / "essay.docx")]
    rejected = [i for i in items if isinstance(i, ExclusionVerdict)
                and i.rule == RULE_PROJECT_ROOT_DESCENDANT]
    assert {i.rule_subject for i in rejected} == set(PROJECT_ROOT_MARKERS)


def test_the_same_rules_fire_on_a_candidate_root(corpus: Path):
    # Done-means 5: the exclusion "must apply both to scanned sources and to
    # candidate roots". Same tree, same rules, same subjects — only applies_to differs.
    (corpus / "node_modules").mkdir()
    (corpus / "app").mkdir()
    (corpus / "app" / "package.json").write_bytes(b"{}")
    (corpus / "app" / "index.js").write_bytes(b"x")

    as_source = [i for i in _walk(corpus) if isinstance(i, ExclusionVerdict)]
    as_root = [i for i in _walk(corpus, sources=[], roots=[corpus])
               if isinstance(i, ExclusionVerdict)]

    assert [(v.path, v.rule, v.rule_subject) for v in as_source] == \
           [(v.path, v.rule, v.rule_subject) for v in as_root]
    assert {v.applies_to for v in as_source} == {APPLIES_TO_SCANNED_SOURCE}
    assert {v.applies_to for v in as_root} == {APPLIES_TO_CANDIDATE_ROOT}


def test_a_root_that_is_itself_excluded_is_rejected_before_listing(corpus: Path):
    excluded_root = corpus / "Library"
    excluded_root.mkdir()
    (excluded_root / "inside.txt").write_bytes(b"x")
    source = RecordingSource()
    items = list(walk(source, sources=[], candidate_roots=[excluded_root],
                      budget_exhausted=NEVER))
    assert [type(i) for i in items] == [ExclusionVerdict]
    assert items[0].applies_to == APPLIES_TO_CANDIDATE_ROOT
    assert source.listed == []


def test_every_excluded_path_carries_a_verdict_naming_its_rule(corpus: Path):
    # Done-means 6.
    (corpus / "dist").mkdir()
    (corpus / "app").mkdir()
    (corpus / "app" / "go.mod").write_bytes(b"module x")
    verdicts = [i for i in _walk(corpus) if isinstance(i, ExclusionVerdict)]
    assert verdicts
    for verdict in verdicts:
        assert verdict.rule
        assert verdict.rule_subject
        assert verdict.applies_to


def test_every_non_excluded_directory_is_observed(corpus: Path):
    (corpus / "sub" / "deep").mkdir(parents=True)
    (corpus / "sub" / "a.txt").write_bytes(b"a")
    directories = [i for i in _walk(corpus) if isinstance(i, ObservedDirectory)]
    by_path = {d.directory_path: d for d in directories}
    assert set(by_path) == {str(corpus), str(corpus / "sub"), str(corpus / "sub" / "deep")}
    assert by_path[str(corpus)].parent_directory is None
    assert by_path[str(corpus / "sub")].parent_directory == str(corpus)
    assert by_path[str(corpus / "sub")].file_count == 1
    assert by_path[str(corpus / "sub")].subdirectory_count == 1
    assert by_path[str(corpus / "sub")].extension_mix == {".txt": 1}


def test_counts_exclude_what_the_rules_rejected(corpus: Path):
    (corpus / "build").mkdir()
    (corpus / "a.txt").write_bytes(b"a")
    root = [i for i in _walk(corpus) if isinstance(i, ObservedDirectory)][-1]
    assert root.file_count == 1
    assert root.subdirectory_count == 0


def test_a_project_root_keeps_its_own_directory_row_and_its_markers(corpus: Path):
    # SPEC Q9 is OPEN. The marker-bearing directory is not rejected by §1.1's
    # "descendants" rule, so it keeps an inventory row and the markers land on it as
    # evidence (R6). Nothing here says whether it may be a candidate root.
    (corpus / "app").mkdir()
    (corpus / "app" / "package.json").write_bytes(b"{}")
    (corpus / "app" / "Cargo.toml").write_bytes(b"[package]")
    row = [i for i in _walk(corpus) if isinstance(i, ObservedDirectory)
           and i.directory_path == str(corpus / "app")][0]
    assert row.project_root_markers == ("package.json", "Cargo.toml")
    assert row.file_count == 0


def test_a_symlink_is_recorded_as_unresolved_not_indexed(corpus: Path):
    # SPEC Q7 is OPEN: traversal of symlinks, aliases, packages and mounts is
    # unstated. P3 records the case and decides nothing.
    (corpus / "real").mkdir()
    (corpus / "link").symlink_to(corpus / "real")
    items = _walk(corpus)
    deferred = [i for i in items if isinstance(i, Deferred)]
    assert [(d.path, d.reason) for d in deferred] == [
        (str(corpus / "link"), DEFERRED_TRAVERSAL_UNRESOLVED),
    ]
    assert not any(isinstance(i, ObservedFile) for i in items)


def test_a_directory_that_vanished_is_recorded_not_crashed(corpus: Path):
    items = list(walk(FilesystemCorpusSource(), sources=[corpus / "gone"],
                      candidate_roots=[], budget_exhausted=NEVER))
    assert [(i.path, i.reason) for i in items] == [
        (str(corpus / "gone"), DEFERRED_PATH_ABSENT),
    ]


@needs_unprivileged
def test_an_unreadable_directory_is_recorded_and_the_rest_of_the_scan_continues(
        corpus: Path):
    # §8.6: the difference between completed and deferred work must be visible "so
    # that no unscanned file reads as one that was understood and found unimportant."
    # `11` §1's check (Task 8) covers the selected ROOTS; a directory below one can
    # still refuse, and an unhandled refusal would abandon the walk with part of the
    # corpus written and nothing on the record naming what was missed.
    (corpus / "ok.txt").write_bytes(b"x")
    locked = corpus / "locked"
    locked.mkdir()
    (locked / "inside.txt").write_bytes(b"x")
    locked.chmod(0o000)
    try:
        items = _walk(corpus)
    finally:
        locked.chmod(0o700)

    # the walk finished: the sibling file is still observed
    assert [i.path for i in items if isinstance(i, ObservedFile)] == \
           [str(corpus / "ok.txt")]
    # and the directory it could not read is on the record, by name
    assert [(i.path, i.reason) for i in items if isinstance(i, Deferred)] == [
        (str(locked), DEFERRED_DIRECTORY_UNREADABLE),
    ]
    # nothing inside it is claimed: it was never listed, so it gets no R6 row and no
    # entry of its own appears anywhere in the output
    assert not [i for i in items if isinstance(i, ObservedDirectory)
                and i.directory_path == str(locked)]
    assert not any("inside.txt" in getattr(i, "path", "") for i in items)


def test_budget_exhaustion_defers_the_remainder_and_keeps_what_was_seen(corpus: Path):
    # Done-means 13's traversal half. §8.6: "retain extracted evidence, mark the
    # deferred stage… Cost exhaustion must never turn into lower-quality automatic
    # classification." The observations already made survive.
    for name in ("a.txt", "b.txt", "c.txt"):
        (corpus / name).write_bytes(b"x")
    (corpus / "sub").mkdir()
    (corpus / "sub" / "d.txt").write_bytes(b"x")

    seen = {"n": 0}

    def after_two():
        seen["n"] += 1
        return seen["n"] > 2

    items = _walk(corpus, budget=after_two)
    observed = [i for i in items if isinstance(i, ObservedFile)]
    deferred = [i for i in items if isinstance(i, Deferred)]
    assert observed                                     # retained, not discarded
    assert deferred
    assert {d.reason for d in deferred} == {DEFERRED_BUDGET}
    # the partially-listed directory has no inventory row: R6 has no partial count
    assert not [i for i in items if isinstance(i, ObservedDirectory)
                and i.directory_path == str(corpus)]
    assert str(corpus) in {d.path for d in deferred}


def test_budget_exhaustion_defers_unreached_directories_too(corpus: Path):
    (corpus / "sub").mkdir()
    (corpus / "sub" / "a.txt").write_bytes(b"x")
    (corpus / "other").mkdir()
    (corpus / "other" / "b.txt").write_bytes(b"x")

    calls = {"n": 0}

    def after_the_root():
        calls["n"] += 1
        return calls["n"] > 2

    deferred = [i for i in _walk(corpus, budget=after_the_root) if isinstance(i, Deferred)]
    assert {str(corpus / "sub"), str(corpus / "other")} <= {d.path for d in deferred}


def test_budget_exhausted_is_required_with_no_default(corpus: Path):
    # §8.6 names no ceiling for traversal (SPEC Q15 is open), so P3 holds none and
    # the caller must supply the predicate.
    with pytest.raises(TypeError):
        list(walk(FilesystemCorpusSource(), sources=[corpus], candidate_roots=[]))
