# tests/integration/test_scale_stress.py
"""What the product does when the corpus is the size of a real disk.

The largest fixture corpus anywhere else in this suite is 100 files and almost
every test uses two or three. A real personal corpus is 10,000-500,000 files.
Every threshold, warning, budget and query in this system was written and proved
against a handful, so this file drives the same real code over corpora big enough
and lumpy enough to have the shape of a disk somebody actually owns.

NOT COLLECTED BY DEFAULT. Every test here is skipped unless `SCALE_STRESS=1` is
set, because several take tens of seconds by construction -- the measurement IS
the test. To run them:

    SCALE_STRESS=1 python -m pytest tests/integration/test_scale_stress.py -v -s

Two kinds of test live here and they fail for different reasons.

* **Promise tests** assert something `planning/00-database-agent-product-design.md`
  states outright. They fail TODAY, on a corpus of any size, and they pass when
  the defect is fixed. `test_example_members_is_a_sample_not_the_whole_branch` is
  the type case.
* **Shape tests** assert the COMPLEXITY CURVE, never an absolute number of
  seconds, because a wall-clock threshold measures the machine and not the
  product. Each holds one variable fixed and moves another, so a failure names a
  cause rather than reporting that something was slow.

The corpora are long-tailed on purpose. A uniform corpus is the one shape a real
disk never has, and two of the findings below are invisible without duplicate
basenames, large duplicate families and a fat Screenshots folder.
"""
from __future__ import annotations

import dataclasses
import os
import random
import shutil
import tempfile
import time
from pathlib import Path

import pytest

from database_agent.budget import set_ceiling
from database_agent.db import create_schema, open_database
from eval_harness.store import create_eval_schema
from facts.fields import create_fields
from grouping.schema import create_grouping_schema
from placement import vocabulary as pv
from placement.config import PlacementLimits
from placement.index import build_destination_index, entries_for_plan
from placement.records import MatchingFact, Subject
from placement.retrieval import retrieve
from placement.schema import create_placement_schema
from privacy.schema import create_privacy_schema
from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.scan import scan
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection
from tree_design.candidates import vertical_options
from tree_design.config import tree_limits
from tree_design.health import (
    branch_counts,
    parent_concepts_for,
    tree_health,
    warnings_for,
)
from tree_design.materialise import (
    BranchEvidence,
    LevelEvidence,
    project_branch_preview,
)
from tree_design.records import Node
from tree_design.routing import CompositionCandidate, RoutingReport
from tree_design.templates import ApplicabilityRef, ResolvedDimension
from tree_design.validation import ValidationReport
from tree_design.vocabulary import (
    ACTION_SELECTED,
    SCOPE_SCHEMA_FIELD,
    WARN_EXCESSIVE_DEPTH,
    WARN_ONE_CHILD,
    WARN_TINY_FOLDERS,
)

from p11.p10_fixtures import (
    FREEZE_RECORD,
    ExpectedValue,
    FrozenTree,
    _node,
    _profile,
)

pytestmark = pytest.mark.skipif(
    os.environ.get("SCALE_STRESS") != "1",
    reason="scale stress harness; run with SCALE_STRESS=1 (takes minutes)",
)

CLOCK = "2026-08-27T00:00:00Z"


# --------------------------------------------------------------------------
# Corpora. Long-tailed, because a uniform corpus hides two of the findings.
# --------------------------------------------------------------------------

def _fresh_db(base: Path):
    conn = open_database(base / "agent.sqlite")
    create_schema(conn)
    create_scan_schema(conn)
    return conn


def _scan_corpus(corpus: Path, conn) -> float:
    """Run the real scan over a real directory. Returns elapsed seconds."""
    selection = record_selection(conn, sources=[corpus], candidate_roots=[],
                                 cross_folder_moves=False, selected_by="scale")
    started = time.perf_counter()
    scan(conn, selection, source=FilesystemCorpusSource(),
         mime_type_for=lambda path: "application/octet-stream",
         scan_state="complete", budget_exhausted=lambda: False)
    conn.commit()
    return time.perf_counter() - started


def _branch_node(label="Academics", node_id="n_branch") -> Node:
    return Node(
        node_id=node_id, plan_version_id="plan_1", node_type="proposed",
        display_label=label, parent_node_id=None, root_anchor="root_documents",
        ordinal=0, associated_group_ids=(),
        explanation="The accepted groups beneath it produced this area.",
        node_role="ordinary", accepts_placement=True,
        handling_class="personal_non_sensitive", origin_node_id=node_id,
        dimension=None, dimension_role=None)


def _node_at(node_id, parent, label, dimension=None) -> Node:
    return Node(
        node_id=node_id, plan_version_id="plan_1", node_type="proposed",
        display_label=label, parent_node_id=parent, root_anchor="root_documents",
        ordinal=0, associated_group_ids=(),
        explanation=f"{label} appeared from the accepted groups beneath it.",
        node_role="ordinary", accepts_placement=True,
        handling_class="personal_non_sensitive", origin_node_id=node_id,
        dimension=dimension, dimension_role=dimension)


def _limits(conn, **over):
    set_ceiling(conn, "tree.max_folder_proposals", 6)
    set_ceiling(conn, "tree.max_depth", 6)
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    kwargs = dict(excessive_depth_warning=3, tiny_folder_max_files=2,
                  tiny_folder_count_warning=3,
                  materially_improves_retrieval=lambda preview: None)
    kwargs.update(over)
    return tree_limits(conn, **kwargs)


def _evidence_for(members_by_value_per_level) -> BranchEvidence:
    """A `BranchEvidence` of the shape `materialise_branch` produces."""
    levels = []
    everything: set[str] = set()
    for index, (role, by_value) in enumerate(members_by_value_per_level):
        for files in by_value.values():
            everything |= set(files)
        levels.append(LevelEvidence(
            dimension_role=role, field_ref=role, order_index=index,
            metadata_only=False, dimension_label=role,
            display_labels={value: value for value in by_value},
            members_by_value={value: frozenset(files)
                              for value, files in by_value.items()},
            handling_classes_by_value={
                value: frozenset({"personal_non_sensitive"})
                for value in by_value}))
    return BranchEvidence(
        branch_node_id="n_branch", levels=tuple(levels),
        member_file_ids=frozenset(everything), unresolved_by_field={},
        protected_file_ids=frozenset())


def _picker(conn, evidence, roles, **limit_over):
    """The real §5.5 picker, with the real preview and the real §5.9 warnings."""
    counter = iter(range(5_000_000))
    accepted = ValidationReport(report_id="vr_scale", passed=("V1",), failures=())

    def preview(_candidate, built):
        return project_branch_preview(
            built, accepted, parent=_branch_node(), plan_version_id="plan_1",
            mint_node_id=lambda: f"n_prev_{next(counter)}",
            handling_class_for=lambda classes: "personal_non_sensitive",
            template_context_for=lambda field_ref, order_index: None)

    candidate = CompositionCandidate(
        applicability_refs=(ApplicabilityRef("a1", 1),),
        resolved_dimensions=tuple(
            ResolvedDimension(role, role, ACTION_SELECTED, index, None,
                              SCOPE_SCHEMA_FIELD)
            for index, role in enumerate(roles)),
        privacy_floor="policy.public",
        covered_file_ids=evidence.member_file_ids,
        gates_passed=("C1",), overridden_gates=(),
        explanation="one row resolves these dimensions")
    report = RoutingReport(candidates=(candidate,), conflicts=(), deferred=0)
    return vertical_options(
        report, branch_members=tuple(sorted(evidence.member_file_ids)),
        materialise=lambda _c: evidence, validate=lambda _c: None,
        limits=_limits(conn, **limit_over), preview=preview)


# --------------------------------------------------------------------------
# 1. The scan. Two independent quadratics, each isolated from the other.
# --------------------------------------------------------------------------

def test_scan_is_quadratic_in_the_size_of_a_duplicate_family():
    """The file count is FIXED at 2,000. Only how many files share a content hash
    changes, so anything that moves is identity resolution and not per-file work.

    `files_table.observe_path` reads every row sharing the observed content hash
    and then walks that list twice with a SYSCALL in each pass -- the inode check
    lstats two paths, and the dead-path branch stats a third. A family of k files
    therefore costs O(k^2) lstats to admit.

    §2.9's duplicate families and §8.3's identical-file collisions are the design
    saying real corpora contain many identical files. They do: empty files, stub
    configs, repeated downloads, thumbnails, `.DS_Store`. This is not an exotic
    input, it is the one the design names.
    """
    total = 2000
    timings: dict[int, float] = {}
    for families in (500, 1):
        base = Path(tempfile.mkdtemp())
        try:
            corpus = base / "corpus"
            corpus.mkdir()
            per_family = total // families
            for family in range(families):
                directory = corpus / f"dir_{family:04d}"
                directory.mkdir()
                for index in range(per_family):
                    # Content is per-FAMILY, so family size is the only variable.
                    (directory / f"file_{index:04d}.bin").write_bytes(
                        b"D" * (family + 1))
            conn = _fresh_db(base)
            timings[per_family] = _scan_corpus(corpus, conn)
            assert conn.execute(
                "SELECT COUNT(*) c FROM files").fetchone()["c"] == total
            conn.close()
        finally:
            shutil.rmtree(base, ignore_errors=True)

    small, large = timings[4], timings[total]
    print(f"\n  2,000 files in families of 4:     {small:.2f}s"
          f"\n  2,000 files in ONE family:        {large:.2f}s"
          f"\n  slowdown from duplicate shape:    x{large / small:.1f}")
    assert large < small * 2.0, (
        f"scanning the same 2,000 files took {large:.1f}s when they form one "
        f"duplicate family against {small:.1f}s when they form families of four "
        f"(x{large / small:.1f}). The file count never changed, so this is "
        "`observe_path` resolving identity against the whole family: O(k^2) "
        "lstat calls for a family of k. A real disk's zero-byte and stub-file "
        "families run to tens of thousands."
    )


def test_identity_resolution_does_not_stat_the_whole_duplicate_family():
    """The same finding as the test above, counted instead of timed.

    Counting is the sharper instrument: the syscalls are the cause and the seconds
    are only the symptom, so this fails on a slow machine and a fast one alike and
    it names `observe_path`'s identity walk rather than reporting that a scan was
    slow. Constant per-file work (hashing, one stat from the walker) cancels out
    because what is asserted is the RATIO of per-file syscalls between two family
    sizes, not their absolute number.

    `observe_path` reads every live row sharing the observed content hash and walks
    that list with a filesystem call per candidate -- the inode check lstats two
    paths and the dead-path branch stats a third. Admitting a family of k costs
    O(k^2) syscalls, so per-file syscalls rise linearly with family size.
    """
    counts: dict[int, int] = {}
    real_lstat, real_stat = os.lstat, os.stat
    for family_size in (200, 800):
        base = Path(tempfile.mkdtemp())
        try:
            corpus = base / "corpus"
            corpus.mkdir()
            for index in range(family_size):
                # One family: identical bytes, distinct names.
                (corpus / f"copy_{index:05d}.bin").write_bytes(b"IDENTICAL")
            conn = _fresh_db(base)
            calls = [0]

            def counted_lstat(target, *a, _r=real_lstat, _c=calls, **k):
                _c[0] += 1
                return _r(target, *a, **k)

            def counted_stat(target, *a, _r=real_stat, _c=calls, **k):
                _c[0] += 1
                return _r(target, *a, **k)

            os.lstat, os.stat = counted_lstat, counted_stat
            try:
                _scan_corpus(corpus, conn)
            finally:
                os.lstat, os.stat = real_lstat, real_stat
            assert conn.execute(
                "SELECT COUNT(*) c FROM files").fetchone()["c"] == family_size
            counts[family_size] = calls[0]
            conn.close()
        finally:
            shutil.rmtree(base, ignore_errors=True)

    per_file = {size: total / size for size, total in counts.items()}
    growth = per_file[800] / per_file[200]
    print(f"\n  family of 200: {counts[200]:>9,} syscalls "
          f"({per_file[200]:.0f} per file)"
          f"\n  family of 800: {counts[800]:>9,} syscalls "
          f"({per_file[800]:.0f} per file)"
          f"\n  per-file syscalls grew x{growth:.1f} for a family four times as big")
    assert growth < 1.5, (
        f"admitting a file cost {per_file[200]:.0f} filesystem calls in a family of "
        f"200 and {per_file[800]:.0f} in a family of 800 (x{growth:.1f}). Per-file "
        "cost rises with the size of the duplicate family, so the family costs "
        "O(k^2) to admit. Identical files are not an exotic input -- empty files, "
        "`.DS_Store`, stub configs, thumbnails and repeated downloads all form "
        "families in the tens of thousands on a real disk."
    )


class _RowCountingConnection:
    """Forwards to a real connection and counts the rows SQLite hands back.

    Rows read is the right unit for the question below: re-observing a file that
    has not changed does no filesystem work either way, so a syscall count cannot
    see the difference. What it costs is how much of the `files` table has to be
    materialised to recognise the file, and that is what this counts.
    """

    def __init__(self, conn):
        object.__setattr__(self, "_conn", conn)
        object.__setattr__(self, "rows", 0)

    def __getattr__(self, name):
        return getattr(object.__getattribute__(self, "_conn"), name)

    def __setattr__(self, name, value):
        setattr(object.__getattribute__(self, "_conn"), name, value)

    def execute(self, sql, *args, **kwargs):
        cursor = object.__getattribute__(self, "_conn").execute(sql, *args, **kwargs)
        if " FROM files " in f" {' '.join(sql.split())} ":
            return _RowCountingCursor(cursor, self)
        return cursor


class _RowCountingCursor:
    def __init__(self, cursor, owner):
        self._cursor, self._owner = cursor, owner

    def __getattr__(self, name):
        return getattr(self._cursor, name)

    def _charge(self, rows):
        object.__setattr__(self._owner, "rows",
                           object.__getattribute__(self._owner, "rows") + rows)

    def fetchall(self):
        rows = self._cursor.fetchall()
        self._charge(len(rows))
        return rows

    def fetchone(self):
        row = self._cursor.fetchone()
        self._charge(1 if row is not None else 0)
        return row

    def __iter__(self):
        for row in self._cursor:
            self._charge(1)
            yield row


def test_reobserving_an_unchanged_duplicate_family_does_not_read_the_family():
    """The steady-state case, which is the one a real disk is in most of the time:
    the file is already recorded at the path it is observed at, and its bytes are
    unchanged.

    `observe_path` is driven directly rather than through `scan`, because a second
    scan is answered by the stat cache and never reaches identity resolution at
    all — measuring it through `scan` would measure the cache and report a result
    about something else.

    Recognising an unchanged file is a single question — is there a live row with
    this path and these bytes? — and an index answers it. Reading the whole
    duplicate family to find the one row whose `current_path` matches in Python
    costs O(k) per file for files that have not changed.

    Companion to `test_identity_resolution_does_not_stat_the_whole_duplicate_family`
    above: that one is about admitting a family, this one is about living with it.
    """
    from database_agent.files_table import observe_path
    from p1_contract import p3_basic_record

    per_file: dict[int, float] = {}
    for family_size in (200, 800):
        base = Path(tempfile.mkdtemp())
        try:
            corpus = base / "corpus"
            corpus.mkdir()
            members = []
            for index in range(family_size):
                member = corpus / f"copy_{index:05d}.bin"
                member.write_bytes(b"IDENTICAL")
                members.append(member)
            conn = _fresh_db(base)

            def observe(target, connection):
                return observe_path(
                    connection, target, author="scale", component_version="1",
                    parent_folder_context=None, mime_type=None,
                    detected_format=None, scan_state="complete",
                    materialized=True, **p3_basic_record(target))

            for member in members:                       # admit the family
                observe(member, conn)
            counting = _RowCountingConnection(conn)
            for member in members:                       # observe it again, unchanged
                observe(member, counting)
            assert conn.execute(
                "SELECT COUNT(*) c FROM files").fetchone()["c"] == family_size
            per_file[family_size] = counting.rows / family_size
            conn.close()
        finally:
            shutil.rmtree(base, ignore_errors=True)

    growth = per_file[800] / per_file[200]
    print(f"\n  re-observing a family of 200: {per_file[200]:.0f} `files` rows read "
          f"per file"
          f"\n  re-observing a family of 800: {per_file[800]:.0f} `files` rows read "
          f"per file"
          f"\n  grew x{growth:.1f} for a family four times as big")
    assert growth < 1.5, (
        f"re-observing an unchanged file read {per_file[200]:.0f} rows of `files` in "
        f"a family of 200 and {per_file[800]:.0f} in a family of 800 "
        f"(x{growth:.1f}). Nothing about the file changed, so every one of those "
        "reads is spent recognising a file already recorded at the path it was "
        "found at."
    )


def test_scan_stays_linear_when_every_file_is_unique():
    """No duplicate family at all, so the previous quadratic cannot contribute.

    Anything superlinear left is the OTHER one: `files` carries no index on
    `current_path`, and `observe_path` runs two `WHERE current_path = ?` queries
    per observed file. `EXPLAIN QUERY PLAN` says `SCAN files` for both, so every
    file read costs a full pass over every file recorded so far.
    """
    timings: dict[int, float] = {}
    for count in (1000, 4000):
        base = Path(tempfile.mkdtemp())
        try:
            corpus = base / "corpus"
            corpus.mkdir()
            for index in range(count):
                directory = corpus / f"d{index // 50:04d}"
                directory.mkdir(exist_ok=True)
                (directory / f"f{index:06d}.bin").write_bytes(
                    f"unique-{index}".encode())
            conn = _fresh_db(base)
            timings[count] = _scan_corpus(corpus, conn)
            conn.close()
        finally:
            shutil.rmtree(base, ignore_errors=True)

    small, large = timings[1000], timings[4000]
    per_file_small, per_file_large = small / 1000, large / 4000
    print(f"\n  1,000 unique files: {small:.2f}s  ({1000 / small:.0f} files/s)"
          f"\n  4,000 unique files: {large:.2f}s  ({4000 / large:.0f} files/s)"
          f"\n  per-file cost grew x{per_file_large / per_file_small:.1f}")
    assert per_file_large < per_file_small * 1.6, (
        f"four times the files cost {large / small:.1f} times the time with no "
        "duplicate content anywhere, so per-file cost is rising with corpus "
        f"size ({1000 / small:.0f} files/s falling to {4000 / large:.0f}). "
        "`files` has no index on `current_path` and `observe_path` scans the "
        "whole table twice per file."
    )


def test_the_scan_finishes_a_realistic_disk_shaped_corpus():
    """A long-tailed corpus: a fat Screenshots folder, deep project trees, a tail
    of tiny folders, and duplicate basenames across all of them.

    This is the shape rather than the size of a real disk. It exists to state the
    throughput the two tests above explain, in the units a product decision needs.
    """
    count = 4000
    base = Path(tempfile.mkdtemp())
    try:
        corpus = base / "corpus"
        rng = random.Random(5)
        shots = corpus / "Pictures" / "Screenshots"
        shots.mkdir(parents=True)
        made = int(count * 0.35)
        for index in range(made):
            (shots / f"Screenshot 2026-0{index % 9 + 1}-{index % 28 + 1} at "
                     f"{index % 12 + 1}.{index % 60:02d}.png").write_bytes(
                b"x" * rng.randint(20, 200))
        for project in range(max(1, int(count * 0.25) // 40)):
            deep = (corpus / "Projects" / f"proj{project}" / "src" / "core"
                    / "lib" / "impl")
            deep.mkdir(parents=True, exist_ok=True)
            for index in range(40):
                (deep / f"module_{index}.py").write_bytes(b"y" * 64)
                made += 1
        index = 0
        while made < count:
            directory = corpus / "Documents" / f"folder_{index // 3:05d}"
            directory.mkdir(parents=True, exist_ok=True)
            # Duplicate basenames across directories, which is what a real
            # Documents folder looks like after a decade.
            (directory / rng.choice(["Untitled.pdf", "scan.pdf", "notes.txt",
                                     "Untitled.pdf", "receipt.pdf"])
             ).write_bytes(b"z" * 32)
            made += 1
            index += 1

        conn = _fresh_db(base)
        elapsed = _scan_corpus(corpus, conn)
        rows = conn.execute("SELECT COUNT(*) c FROM files").fetchone()["c"]
        conn.close()
    finally:
        shutil.rmtree(base, ignore_errors=True)

    rate = rows / elapsed
    print(f"\n  {rows} files recorded in {elapsed:.1f}s ({rate:.0f} files/s)"
          f"\n  at this rate 100,000 files would take "
          f"{100_000 / rate / 60:.0f} minutes -- and the rate FALLS with size")
    assert rate > 400, (
        f"the scan managed {rate:.0f} files/s on a {rows}-file disk-shaped "
        "corpus. Because both scan costs above grow with corpus size, the rate "
        "on a real disk is lower still, and the scan is the first thing the "
        "product does."
    )


# --------------------------------------------------------------------------
# 2. `00`:99's picker. What the user is shown before they choose a split.
# --------------------------------------------------------------------------

def test_example_members_is_a_sample_not_the_whole_branch(conn):
    """`00`:99 -- before the user chooses a split the system shows "the resulting
    number of child branches, the number of files under each child, EXAMPLE
    MEMBERS, unresolved files, and any evidence gaps".

    `VerticalOption.example_members` is every member of the branch. At 100 files
    that reads like a design decision nobody had to make; at 20,000 it is the
    corpus, and the field is named `example_members`.

    `candidates.py:463` is `example_members=members[:len(members)]` -- a slice
    that truncates nothing, written in the shape of a truncation.
    """
    files = {f"f{index}" for index in range(20_000)}
    evidence = _evidence_for([
        ("subject", {f"COURSE{i:03d}": {f for f in files if hash(f) % 200 == i}
                     for i in range(200)}),
    ])
    # Every file lands under exactly one subject, so nothing is unresolved and
    # the size below cannot be blamed on a fallback bucket.
    evidence = dataclasses.replace(evidence, member_file_ids=frozenset(files))
    option = _picker(conn, evidence, ("subject",))[0]

    print(f"\n  branch holds {len(files)} files"
          f"\n  example_members holds {len(option.example_members)}")
    assert len(option.example_members) < len(files), (
        f"`example_members` holds all {len(option.example_members)} of the "
        "branch's files. `00`:99 asks for examples so the user can judge a split "
        "before taking it; handing back the whole membership is the corpus, not "
        "an example, and every option carries its own copy."
    )


def test_nothing_caps_the_number_of_folders_one_split_would_create(conn):
    """§8.6's ceiling is called "Maximum folder proposals and maximum depth" and
    P1 publishes it as one key. It caps candidate OPTIONS in the picker
    (`routing.py:481`) and tree DEPTH (`validation.py:130`) and NOT the number of
    folders a single option would create.

    `00`:88 recommends exactly the split that exposes this: "Photos and
    capture-based media are the major exception: time often belongs first."
    """
    photos = [f"IMG_{index:06d}" for index in range(8000)]
    rng = random.Random(3)
    by_date: dict[str, set[str]] = {}
    for photo in photos:
        day = rng.randint(0, 1460)
        by_date.setdefault(f"20{22 + day // 365}-{day % 12 + 1:02d}-"
                           f"{day % 28 + 1:02d}", set()).add(photo)
    evidence = _evidence_for([("capture_date", by_date)])

    # The ceiling is set to six, the value P10's own tests use.
    option = _picker(conn, evidence, ("capture_date",))[0]
    print(f"\n  ceilings max_folder_proposals = max_depth = 6"
          f"\n  folders this one option would create   = "
          f"{option.total_child_branches}"
          f"\n  summary the user reads: {option.summary}")
    assert option.total_child_branches <= 100, (
        f"one option proposes {option.total_child_branches} folders with the "
        "'maximum folder proposals' ceiling set to 6. The ceiling bounds how "
        "many OPTIONS are offered and how DEEP a candidate may go; no ceiling "
        "anywhere bounds how WIDE one is. A capture-date split on a real photo "
        "library proposes a folder per day."
    )


def _one_level_evidence(file_count, folder_count):
    """`file_count` files spread evenly over exactly `folder_count` values.

    Spreading evenly is what makes the two sweeps below controlled: the preview
    tree has exactly `folder_count` nodes whatever `file_count` is, so each test
    moves one variable and holds the other genuinely fixed.
    """
    files = [f"f{index}" for index in range(file_count)]
    by_value: dict[str, set[str]] = {}
    for index, name in enumerate(files):
        by_value.setdefault(f"v{index % folder_count}", set()).add(name)
    return _evidence_for([("d", by_value)])


def test_the_picker_is_linear_in_the_files_a_branch_holds(conn):
    """FOLDER COUNT FIXED at 50, file count moves from 2,000 to 16,000.

    The eager preview `00`:99 asks for -- "before the user chooses a split" --
    costs the same per file however many files the branch holds. This is a real
    result and the control for the test below: the picker's problem is not the
    size of the corpus.
    """
    timings = {}
    for count in (2000, 16000):
        evidence = _one_level_evidence(count, 50)
        started = time.perf_counter()
        option = _picker(conn, evidence, ("d",))[0]
        timings[count] = time.perf_counter() - started
        assert option.total_child_branches == 50
        print(f"\n  {count:>6} files over 50 folders -> {timings[count]:.4f}s")

    growth = (timings[16000] / 16000) / (timings[2000] / 2000)
    print(f"  per-file cost x{growth:.2f} for eight times the files")
    assert growth < 1.6, f"per-file preview cost grew x{growth:.1f}"


def test_the_picker_is_quadratic_in_the_folders_a_split_would_create(conn):
    """FILE COUNT FIXED at 4,000, folder count moves from 100 to 1,600.

    `_counts_for_preview` calls `branch_counts` once per node in the preview
    tree, and `branch_counts` calls `_children`, which filters every node in the
    tree to find one node's children, and `_descendants`, which calls `_children`
    again per node it reaches. `warnings_for` then repeats the same walks plus
    `_depth`, which rebuilds a `{node_id: node}` dict on every call.

    This is what makes the previous test's finding narrow: the picker is cheap in
    files and expensive in FOLDERS, and nothing caps how many folders one split
    proposes (see `test_nothing_caps_the_number_of_folders_one_split_would_create`).
    """
    timings = {}
    for folders in (400, 1600):
        evidence = _one_level_evidence(4000, folders)
        started = time.perf_counter()
        option = _picker(conn, evidence, ("d",))[0]
        timings[folders] = time.perf_counter() - started
        assert option.total_child_branches == folders
        print(f"\n  4,000 files over {folders:>5} folders -> "
              f"{timings[folders]:.4f}s")

    growth = (timings[1600] / 1600) / (timings[400] / 400)
    projected = timings[1600] * (10_000 / 1600) ** 2
    print(f"  per-folder cost x{growth:.2f} for four times the folders"
          f"\n  a 10,000-folder split projects to {projected:.0f}s PER OPTION")
    assert growth < 1.6, (
        f"per-folder preview cost grew x{growth:.1f} for four times the folders, "
        f"so the picker is quadratic in the width of the split it is previewing: "
        f"{timings[400]:.3f}s at 400 folders becomes {timings[1600]:.3f}s at "
        f"1,600 and projects to {projected:.0f}s at 10,000 -- per option, and "
        "the ceiling permits several options."
    )


# --------------------------------------------------------------------------
# 3. §5.9's warnings and §5.11's health.
# --------------------------------------------------------------------------

def _preferential_tree(node_count, seed=7):
    """A tree shaped like a real one: a few fat hubs, a long tail of thin nodes."""
    rng = random.Random(seed)
    dims = ["area", "school", "term", "course", "work_type", "year"]
    nodes = [_node_at("n_0", None, "Root", "area")]
    depth = {"n_0": 0}
    for index in range(1, node_count):
        parent = nodes[int(len(nodes) * (rng.random() ** 2.2))]
        node_depth = depth[parent.node_id] + 1
        node = _node_at(f"n_{index}", parent.node_id, f"L{index}",
                        dims[min(len(dims) - 1, node_depth)])
        depth[node.node_id] = node_depth
        nodes.append(node)
    return tuple(nodes)


def test_tree_health_is_linear_enough_to_render_a_real_tree(conn):
    """§5.11's health view and §5.9's warnings are computed per node over the
    whole tree, and `health.py`'s helpers rescan the whole tree per node.

    `_children` filters every node to find one node's children. `_descendants`
    calls `_children` once per node it reaches. `_depth` rebuilds a `{id: node}`
    dict on every call. `warnings_for` runs all three inside a loop over nodes.
    """
    limits = _limits(conn)
    timings = {}
    for count in (800, 3200):
        nodes = _preferential_tree(count)
        members = {node.node_id: [f"f{i}" for i in range(3)] for node in nodes}
        started = time.perf_counter()
        counts = {node.node_id: branch_counts(
            nodes, node_id=node.node_id, members_by_node=members,
            unresolved_by_node={}, evidence_gaps_by_node={},
            sensitive_node_ids=frozenset()) for node in nodes}
        warnings_for(nodes, counts, limits=limits,
                     parent_concepts=parent_concepts_for(nodes))
        timings[count] = time.perf_counter() - started
        print(f"\n  {count:>5} nodes -> {timings[count]:.3f}s")

    growth = (timings[3200] / 3200) / (timings[800] / 800)
    projected = timings[3200] * (50_000 / 3200) ** 2
    print(f"  per-node cost grew x{growth:.1f} for a four-fold larger tree"
          f"\n  a 50,000-node tree projects to {projected / 60:.0f} minutes")
    assert growth < 1.6, (
        f"per-node cost grew x{growth:.1f} for four times the nodes, which is "
        f"quadratic: {timings[800]:.2f}s at 800 nodes becomes "
        f"{timings[3200]:.2f}s at 3,200 and projects to {projected / 60:.0f} "
        "minutes at 50,000. This is the canvas the user is waiting on."
    )


def test_the_warning_list_does_not_outgrow_the_tree_it_describes(conn):
    """§5.9's warnings exist so the user can fix a few high-leverage problems.
    §5.11 is explicit that the goal is "a good enough structural gist of the
    corpus so that only a limited number of high-leverage changes remain".

    A list with more entries than the tree has folders is not a gist.
    """
    limits = _limits(conn)
    nodes = _preferential_tree(3200)
    members = {node.node_id: [f"f{i}" for i in range(3)] for node in nodes}
    counts = {node.node_id: branch_counts(
        nodes, node_id=node.node_id, members_by_node=members,
        unresolved_by_node={}, evidence_gaps_by_node={},
        sensitive_node_ids=frozenset()) for node in nodes}
    fired = warnings_for(nodes, counts, limits=limits,
                         parent_concepts=parent_concepts_for(nodes))

    by_kind: dict[str, int] = {}
    for warning in fired:
        by_kind[warning.kind] = by_kind.get(warning.kind, 0) + 1
    print(f"\n  {len(nodes)} nodes produced {len(fired)} warnings"
          f"\n  {by_kind}")
    assert len(fired) < len(nodes) / 2, (
        f"a {len(nodes)}-node tree produced {len(fired)} warnings "
        f"({by_kind}). The user cannot read a list of problems longer than the "
        "thing it describes, and §5.9's warnings are unranked and unsummarised: "
        "each is one node with one sentence."
    )


def test_the_one_child_warning_does_not_fire_on_the_designs_own_example(conn):
    """`00`:78-88's worked example, verbatim:

        Academics/Columbia/2026-Spring/PHYS1401/Homework

    §5.9 says to warn "when a level produces only one child". A user with one
    school, in one term, taking one course produces three such levels, and every
    one of them is correct. §5.8 insists uneven and shallow branches are a
    REQUIREMENT, so the tree is right and the warnings still fire.

    On a real disk single-child levels are everywhere: one employer, one tax year
    with documents, one university, a project with one subproject.
    """
    canonical = (
        _node_at("n0", None, "Academics", "area"),
        _node_at("n1", "n0", "Columbia", "school"),
        _node_at("n2", "n1", "2026-Spring", "term"),
        _node_at("n3", "n2", "PHYS1401", "course"),
        _node_at("n4", "n3", "Homework", "work_type"),
        _node_at("n5", "n3", "Lectures", "work_type"),
        _node_at("n6", "n3", "Syllabus", "work_type"),
    )
    members = {"n4": [f"hw{i}" for i in range(12)],
               "n5": [f"lec{i}" for i in range(20)], "n6": ["syllabus"]}
    limits = _limits(conn)
    counts = {node.node_id: branch_counts(
        canonical, node_id=node.node_id, members_by_node=members,
        unresolved_by_node={}, evidence_gaps_by_node={},
        sensitive_node_ids=frozenset()) for node in canonical}
    fired = warnings_for(canonical, counts, limits=limits,
                         parent_concepts=parent_concepts_for(canonical))

    for warning in fired:
        print(f"\n  {warning.kind:26} {warning.node_id:4} {warning.reason}")
    one_child = [w for w in fired if w.kind == WARN_ONE_CHILD]
    assert not one_child, (
        f"{len(one_child)} single-child warnings fire on `00`:78's own example "
        "tree, which is correct in every respect. The warning has no way to tell "
        "a level that is thin because the evidence is thin from one that is thin "
        "because the split was wrong."
    )


def test_the_depth_warning_threshold_admits_the_designs_own_example(conn):
    """`excessive_depth_warning` has no source: §5.9 states no number, §8.6
    publishes no key for it, and it is a mandatory injected argument.

    Every call site in this repository passes 3 (or 5, once). `00`:78's own
    example puts Homework at depth 4.
    """
    canonical = (
        _node_at("n0", None, "Academics", "area"),
        _node_at("n1", "n0", "Columbia", "school"),
        _node_at("n2", "n1", "2026-Spring", "term"),
        _node_at("n3", "n2", "PHYS1401", "course"),
        _node_at("n4", "n3", "Homework", "work_type"),
    )
    limits = _limits(conn, excessive_depth_warning=3)
    counts = {node.node_id: branch_counts(
        canonical, node_id=node.node_id, members_by_node={},
        unresolved_by_node={}, evidence_gaps_by_node={},
        sensitive_node_ids=frozenset()) for node in canonical}
    fired = warnings_for(canonical, counts, limits=limits,
                         parent_concepts=parent_concepts_for(canonical))
    depth_warnings = [w for w in fired if w.kind == WARN_EXCESSIVE_DEPTH]
    for warning in depth_warnings:
        print(f"\n  {warning.node_id}: {warning.reason}")
    assert not depth_warnings, (
        "the depth threshold every test in this repository uses flags "
        "`Academics/Columbia/2026-Spring/PHYS1401/Homework` as excessively deep. "
        "That path is the design document's own recommendation. The threshold "
        "has no source in §5.9 or §8.6 and nothing has ever calibrated it."
    )


def test_the_tiny_folder_warning_says_something_a_user_can_act_on(conn):
    """§5.9's fourth warning fires correctly here -- that is not the finding.

    The finding is its payload. One `Warning_` carries every offending node id in
    `evidence`, and the reason is one sentence with one number. At real width the
    warning is right and unusable.
    """
    files = [f"r{index}" for index in range(4000)]
    by_vendor = {f"vendor_{index}": {files[index]} for index in range(len(files))}
    evidence = _evidence_for([("vendor", by_vendor)])
    option = _picker(conn, evidence, ("vendor",))[0]
    tiny = [w for w in option.warnings if w.kind == WARN_TINY_FOLDERS]
    assert tiny, "the tiny-folder warning should fire on 4,000 one-file folders"
    warning = tiny[0]
    print(f"\n  reason:   {warning.reason}"
          f"\n  evidence: {len(warning.evidence)} node ids")
    assert len(warning.evidence) < 200, (
        f"the warning names {len(warning.evidence)} node ids in one `evidence` "
        "tuple. It fires for the right reason and tells the user to read four "
        "thousand identifiers; §5.9's warnings carry no summary and no ranking."
    )


def test_tree_health_group_coverage_scales_with_the_accepted_groups(conn):
    """§5.11 asks health to "summarize how much of each accepted group is
    represented". `tree_health` builds two sets per group and intersects them.

    This is the one hot path in P10 that is NOT quadratic, and saying so is worth
    as much as naming the ones that are.
    """
    timings = {}
    for count in (2000, 8000):
        members_by_group = {f"g{i}": [f"f{i}_{j}" for j in range(20)]
                            for i in range(count)}
        placed_by_group = {gid: files[:10]
                           for gid, files in members_by_group.items()}
        started = time.perf_counter()
        health = tree_health(
            (), members_by_group=members_by_group,
            placed_by_group=placed_by_group, files_with_enough_facts=count,
            unresolved_node_ids=(), context_supported_node_ids=(),
            sensitive_isolated_node_ids=(), nodes_needing_decisions=())
        timings[count] = time.perf_counter() - started
        assert len(health.group_coverage) == count
        print(f"\n  {count:>5} accepted groups -> {timings[count]:.3f}s")
    growth = (timings[8000] / 8000) / (timings[2000] / 2000)
    assert growth < 1.6, f"group coverage grew x{growth:.1f} per group"


# --------------------------------------------------------------------------
# 4. §6.2/§6.3 placement retrieval.
# --------------------------------------------------------------------------

@pytest.fixture()
def p11_scale_conn(conn):
    create_schema(conn)
    create_eval_schema(conn)
    create_grouping_schema(conn)
    create_fields(conn)
    create_privacy_schema(conn)
    create_placement_schema(conn)
    return conn


def _scaled_frozen_tree(node_count):
    """A frozen tree of `node_count` legal destinations, built from P10's live
    `Node` record through the same helper P11's own tests use."""
    nodes = tuple(
        _node(node_id=f"n-course-{index}", display_label=f"COURSE{index:05d}",
              ordinal=index, associated_group_ids=(f"g-course-{index}",),
              expected_values=(ExpectedValue(field="subject",
                                             value=f"COURSE{index:05d}"),),
              parent_node_id=None)
        for index in range(node_count))
    record = dataclasses.replace(
        FREEZE_RECORD, node_ids=tuple(node.node_id for node in nodes),
        legal_destination_ids=frozenset(
            node.node_id for node in nodes if node.accepts_placement))
    return FrozenTree(
        plan_version_id="plan-1", freeze_record=record, nodes=nodes,
        profiles=tuple(_profile(node) for node in nodes),
        shared_material_policy="mandatory-review",
        shared_material_policy_scope=None)


LIMITS = PlacementLimits(
    max_retrieved_neighbors=4, max_local_graph_neighborhood=8,
    max_candidate_cluster_size=6, max_residual_files_per_batch=50,
    max_dossier_tokens=4000, max_llm_calls_per_thousand_files=100,
    max_cost_per_scan=5)


def test_retrieval_does_not_read_every_legal_node_for_every_file(p11_scale_conn):
    """`00`:105 -- "the engine retrieves the few most relevant approved
    destination nodes, RATHER THAN SEARCHING THE ENTIRE FILESYSTEM or
    re-inventing a category".

    `retrieval.retrieve` opens with `entries_for_plan`, which issues one
    `SELECT ... WHERE node_id = ?` and one `json.loads` per legal node, and then
    loops over all of them. It does that once per subject placed. The index is
    §6.2's "destination-node retrieval index" and is used as a full table read.

    The cost per file therefore rises with the size of the user's tree, which is
    the opposite of what a retrieval index is for.
    """
    timings = {}
    for node_count in (200, 800):
        base = Path(tempfile.mkdtemp())
        try:
            conn = open_database(base / "agent.sqlite")
            create_schema(conn)
            create_eval_schema(conn)
            create_grouping_schema(conn)
            create_fields(conn)
            create_privacy_schema(conn)
            create_placement_schema(conn)
            build_destination_index(conn, _scaled_frozen_tree(node_count),
                                    component_version="scale", observed_at=CLOCK)
            fact = MatchingFact(file_fact_id="ff-1", field="subject",
                                value="COURSE00007", reliability=pv.DIRECT,
                                evidence_ref="obs-1")
            warm = Subject(kind=pv.FILE, file_id="warm", content_hash="h",
                           group_id=None, member_file_ids=())
            retrieve(conn, subject=warm, plan_version="plan-1", limits=LIMITS,
                     facts=(fact,), group_ids=(), curated_folder_labels=(),
                     semantic_neighbours=(), component_version="scale",
                     observed_at=CLOCK)
            repeats = 20
            started = time.perf_counter()
            for index in range(repeats):
                subject = Subject(kind=pv.FILE, file_id=f"f{index}",
                                  content_hash=f"h{index}", group_id=None,
                                  member_file_ids=())
                retrieve(conn, subject=subject, plan_version="plan-1",
                         limits=LIMITS, facts=(fact,), group_ids=(),
                         curated_folder_labels=(), semantic_neighbours=(),
                         component_version="scale", observed_at=CLOCK)
            timings[node_count] = (time.perf_counter() - started) / repeats
            assert len(entries_for_plan(conn, plan_version="plan-1")) == node_count
            conn.close()
        finally:
            shutil.rmtree(base, ignore_errors=True)

    small, large = timings[200], timings[800]
    print(f"\n  200 nodes: {small * 1000:.1f} ms per file"
          f"\n  800 nodes: {large * 1000:.1f} ms per file"
          f"\n  x{large / small:.1f} for four times the tree"
          f"\n  10,000 files against an 800-node tree: "
          f"{large * 10_000 / 60:.1f} minutes")
    assert large < small * 1.6, (
        f"per-file retrieval cost grew x{large / small:.1f} when the tree grew "
        "four-fold, so total placement cost is files x nodes. `retrieve` reads "
        "and deserialises every legal node for every subject: at 10,000 files "
        f"against an 800-node tree that is {large * 10_000 / 60:.1f} minutes and "
        "8 million SQLite queries before any scoring or model call."
    )


def test_building_the_destination_index_scales_with_the_tree(p11_scale_conn):
    """The build side is linear and worth recording as the control for the test
    above: the index is cheap to WRITE and expensive to USE."""
    timings = {}
    for node_count in (200, 800):
        base = Path(tempfile.mkdtemp())
        try:
            conn = open_database(base / "agent.sqlite")
            create_schema(conn)
            create_eval_schema(conn)
            create_grouping_schema(conn)
            create_fields(conn)
            create_privacy_schema(conn)
            create_placement_schema(conn)
            tree = _scaled_frozen_tree(node_count)
            started = time.perf_counter()
            build_destination_index(conn, tree, component_version="scale",
                                    observed_at=CLOCK)
            timings[node_count] = time.perf_counter() - started
            conn.close()
        finally:
            shutil.rmtree(base, ignore_errors=True)
    growth = (timings[800] / 800) / (timings[200] / 200)
    print(f"\n  200 nodes: {timings[200]:.3f}s   800 nodes: {timings[800]:.3f}s"
          f"   per-node x{growth:.2f}")
    assert growth < 1.6, f"index build grew x{growth:.1f} per node"


# --------------------------------------------------------------------------
# 5. Ceilings. The two that scale, and the one key doing two jobs.
# --------------------------------------------------------------------------

def test_the_budget_that_scales_with_the_corpus_is_enforced():
    """§8.6's `model.max_llm_calls_per_thousand_files` is the ONE ceiling whose
    units are per-corpus-size. It is the only published bound on what a bigger
    disk costs, and `placement/config.py` reads it into `PlacementLimits` and
    nothing consumes it.

    `max_cost_per_scan` and `max_candidate_cluster_size` are in the same
    position. `config.py`'s own docstring says a default here would be "running a
    corpus under a limit nobody chose, with nothing to say so" -- reading a limit
    and never applying it lands in the same place by a different route.

    This is a source-level check because the failure is the ABSENCE of a call.
    No corpus size makes an unenforced ceiling fire.
    """
    root = Path(__file__).resolve().parents[2] / "src" / "placement"
    sources = {path.name: path.read_text() for path in root.glob("*.py")
               if path.name != "config.py"}
    unenforced = []
    for limit in ("max_llm_calls_per_thousand_files", "max_cost_per_scan",
                  "max_candidate_cluster_size"):
        if not any(limit in body for body in sources.values()):
            unenforced.append(limit)
    print(f"\n  modules searched: {sorted(sources)}"
          f"\n  ceilings with no consumer: {unenforced}")
    assert not unenforced, (
        f"{unenforced} are read from P1 into `PlacementLimits` and used by no "
        f"module in src/placement/. `max_llm_calls_per_thousand_files` is the "
        "only §8.6 ceiling expressed per thousand files, so nothing bounds what "
        "the model costs as the corpus grows."
    )


def test_one_ceiling_can_serve_both_the_picker_and_the_depth_limit(conn):
    """P1 published `tree.max_folder_proposals_and_depth` as ONE key and P10 used
    the single value for two unrelated things, which `config.py` documented:
    `routing.py:481` caps how many OPTIONS the picker offers, and
    `validation.py:130` refuses a candidate whose DEPTH exceeds it.

    The two want opposite values. `00`:78's own tree is five levels deep, so the
    depth limit must be at least 5; a picker offering five or more options for
    every branch of a real tree is not a picker. One number cannot be both.
    """
    from tree_design.validation import _v3
    from tree_design.validation import MaterialisedCandidate, MaterialisedLevel

    def academic_candidate():
        """`Academics/Columbia/2026-Spring/PHYS1401/Homework`, as V3 reads it."""
        roles = ("school", "term", "course", "work_type")
        return MaterialisedCandidate(
            branch_node_id="n_branch", ancestor_field_refs=(), ancestor_depth=1,
            member_file_ids=frozenset({"f1"}),
            levels=tuple(
                MaterialisedLevel(
                    dimension_role=role, field_ref=role, order_index=index,
                    metadata_only=False, values=("v",),
                    members_by_value={"v": 1},
                    handling_classes_by_value={
                        "v": frozenset({"personal_non_sensitive"})})
                for index, role in enumerate(roles)),
        )

    # `00`:256 names TWO numbers on one line -- "Maximum folder proposals and
    # maximum depth" -- and P1 published one key for both, which `config.py`
    # recorded as a complaint: that single value caps the picker's OPTIONS, a
    # candidate's DEPTH, a date level's WIDTH and the sample size of the printed
    # lists. The first two want opposite values and no P10 change can reconcile
    # them. P1 now publishes the two numbers the design names.
    set_ceiling(conn, "tree.max_folder_proposals", 4)
    set_ceiling(conn, "tree.max_depth", 5)
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    limits = tree_limits(conn, excessive_depth_warning=9, tiny_folder_max_files=2,
                         tiny_folder_count_warning=3,
                         materially_improves_retrieval=lambda preview: None)
    failure = _v3(academic_candidate(), limits)
    print(f"\n  picker ceiling=4, depth ceiling=5: V3 says "
          f"{failure.reason if failure else 'accepted'}")
    assert failure is None, (
        "with four options -- a readable picker -- V3 still refuses `00`:78's "
        f"own recommended tree: {failure.reason}"
    )
    # And the two are genuinely independent: a picker of four, a tree of five.
    assert limits.max_folder_proposals == 4
    assert limits.max_depth == 5
