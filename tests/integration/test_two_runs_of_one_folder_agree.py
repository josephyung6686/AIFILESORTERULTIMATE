# tests/integration/test_two_runs_of_one_folder_agree.py
"""`104` R-78. The same command, the same bytes, twice — and the same answer.

Two runs of identical code over the owner's 199 files produced 511 edges and 510,
so every number this product reports about that corpus was a number from one
draw. The scale agent's identity check had to be run from a fixed P1--P7 snapshot
to mean anything, which is a way of saying the pipeline could not be measured.

Reproduced here on synthetic files. Three runs over the 34-file folder this file
builds, from an empty database each time, gave 463 edges, 456 and 457; a
63-file version of the same corpus with PDFs and OCR'd images in it gave 574 and
573. Diagnosed by minting `file_id` from the path instead of `uuid4` for one
experiment, which made every derived table identical — so the difference was not
extraction, not OCR and not the pool's landing order, but a derivation choosing in
an order made out of THIS run's minted ids.
`tests/p9/test_p9_the_cap_cuts_by_content.py` holds the mechanism; this file holds
the property the product actually has to have.

**What "the same" means here.** A `file_id` is a `uuid4` and a plan version, a
group and a tree node all carry a minted address, so two from-empty runs can never
be byte-identical as raw rows and it would be no virtue if they were. Every minted
id is therefore replaced by what it NAMES — a file by its path, a tree node by its
chain of labels from the root — and what is left is what the run concluded. That
is the same normalisation `w4-scale` used to compare plan rows across a code
change, spelled out here so the guard says what it is checking.

**The pool is real.** The corpus is deliberately larger than
`cli.EXTRACTION_POOL_FLOOR`, so `ProcessPool` starts and the files are read in
seven worker processes that finish in whatever order the operating system
schedules. A run under `InlinePool` has to reach the same answer, and the last
test asks for that: a product whose plan depends on how many cores it was given is
not one either.
"""
from __future__ import annotations

import io
import json
import re
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402

UUID = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
STAMP = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:\d{2}|Z)?")

#: What a run DERIVES, as opposed to what it was handed. Both halves are here on
#: purpose: if `file_facts` and `evidence` ever disagree between two runs the
#: cause is upstream of P9 and the diagnosis is a different one, so the guard
#: should say which half moved rather than only that something did.
DERIVED = (
    "extraction_runs", "evidence", "text_units", "file_facts",
    "groups", "memberships", "group_edges", "stop_rule_outcomes",
    "tree_nodes", "node_expected_values", "unresolved",
)

#: Columns dropped rather than normalised, because the whole of their value is a
#: per-run address with no content behind it. Everything else stays and is
#: normalised in place: `value_id` and `cache_key` are content-addressed
#: (`facts.values._value_identity`, `facts.cache.fact_cache_key`) and dropping
#: them would stop this guard noticing that P6 settled a different value.
MINTED = frozenset({
    "plan_version_id", "origin_node_id", "membership_id", "dossier_id",
    "llm_response_ref", "validation_verdict_ref", "supersedes", "superseded_by",
})

#: Two courses, each stated by more files than `GROUPING_LIMITS.max_graph_nodes`,
#: so the graph's node cap actually binds and has to choose. A corpus under the
#: cap would leave the very decision this file is about untaken.
COURSES = (("PHYS1401", "Columbia", "Dr. Ramirez"),
           ("BUSIB4300", "NYU", "Prof. Lindqvist"))
PER_COURSE = 14


def _body(course: str, school: str, instructor: str, index: int) -> str:
    return (
        f"{course} Homework {index}\n"
        f"School: {school}\n"
        f"Course: {course}\n"
        f"Term: Fall2025\n"
        f"Instructor: {instructor}\n"
        f"Document type: Homework\n\n"
        f"Problem {index}: this is homework {index} for {course} at {school}.\n")


@pytest.fixture(scope="module")
def corpus(tmp_path_factory) -> Path:
    """One folder, written once, read twice. Module-scoped so it cannot drift."""
    root = tmp_path_factory.mktemp("r78-corpus")
    for course, school, instructor in COURSES:
        folder = root / school / course
        folder.mkdir(parents=True)
        for index in range(1, PER_COURSE + 1):
            (folder / f"{course} homework {index:02d}.txt").write_text(
                _body(course, school, instructor, index), encoding="utf-8")

    # DUPLICATES, and they are the reason the tie-break has to be content. Two
    # byte-identical files tie on every content key a run can compute except
    # where each of them lives, so before `104` R-78 the order between them was
    # decided by comparing two `uuid4`s.
    downloads = root / "Downloads"
    downloads.mkdir()
    for course, school, _ in COURSES:
        for index in (1, 2, 3):
            source = root / school / course / f"{course} homework {index:02d}.txt"
            (downloads / f"copy of {source.name}").write_bytes(source.read_bytes())

    written = sum(1 for path in root.rglob("*") if path.is_file())
    assert written > cli.EXTRACTION_POOL_FLOOR, (
        f"{written} files is at or below the pool floor of "
        f"{cli.EXTRACTION_POOL_FLOOR}, so every read would happen on the calling "
        "thread and this file would not be testing a parallel run at all")
    return root


def _run(corpus: Path, database: Path) -> None:
    code = cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Coursework", "--user", "jy",
                     "--database", str(database)], out=io.StringIO())
    assert code == 0, f"the run over {corpus} exited {code}"


def _normalised(database: Path) -> dict[str, list[str]]:
    """Every derived table, with every minted id replaced by what it names."""
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        root = None
        names: dict[str, str] = {}
        for row in conn.execute("SELECT file_id, current_path FROM files"):
            names[row["file_id"]] = row["current_path"]
            root = (row["current_path"] if root is None
                    else _shared_prefix(root, row["current_path"]))
        for file_id, path in list(names.items()):
            names[file_id] = "<file:" + path[len(root or ""):].lstrip("/") + ">"

        # A tree node's id is minted per plan version; what it IS is its chain of
        # labels from the root, which two runs over one folder must agree on.
        nodes = {row["node_id"]: dict(row) for row in conn.execute(
            "SELECT node_id, parent_node_id, display_label, node_type, dimension "
            "FROM tree_nodes")}

        def address(node_id: str, depth: int = 0) -> str:
            row = nodes.get(node_id)
            if row is None or depth > 32:
                return node_id
            parent = row["parent_node_id"]
            head = address(parent, depth + 1) + "/" if parent else ""
            return f"{head}{row['node_type']}:{row['dimension']}:" \
                   f"{row['display_label']}"

        for node_id in nodes:
            names[node_id] = "<node:" + address(node_id) + ">"

        # The two addresses that are `sha256` rather than `uuid4`, so the regex
        # below cannot see them, and that TRAVEL: `file_facts.record_id` projects
        # `fact_id`, and a `group_edges` row on a channel that cites no
        # observation carries its own `edge_id` as its `evidence_ref`. Each is
        # replaced by what it addresses rather than by a placeholder, so two
        # facts about two files stay two different strings.
        for row in conn.execute(
                "SELECT fact_id, file_id, field_key, value_id, origin "
                "FROM file_facts"):
            names[row["fact_id"]] = (
                f"<fact:{names.get(row['file_id'], row['file_id'])}|"
                f"{row['field_key']}|{row['value_id']}|{row['origin']}>")
        for row in conn.execute(
                "SELECT edge_id, from_file_id, to_file_id, edge_type, "
                "bridge_entity_ref FROM group_edges"):
            names[row["edge_id"]] = (
                f"<edge:{names.get(row['from_file_id'], row['from_file_id'])}|"
                f"{names.get(row['to_file_id'], row['to_file_id'])}|"
                f"{row['edge_type']}|{row['bridge_entity_ref']}>")

        # One alternation rather than a pass per name: a run of this size mints
        # some hundreds of addresses and every string cell would otherwise be
        # scanned once for each of them.
        minted = re.compile("|".join(
            re.escape(name) for name in sorted(names, key=len, reverse=True)))

        def say(value):
            if not isinstance(value, str):
                return value
            value = minted.sub(lambda found: names[found.group(0)], value)
            value = UUID.sub("<uuid>", value)
            value = STAMP.sub("<stamp>", value)
            return value.replace(str(root), "<root>") if root else value

        tables: dict[str, list[str]] = {}
        for table in DERIVED:
            rows = []
            for row in conn.execute(f"SELECT * FROM {table}"):
                rows.append(json.dumps(
                    {key: say(row[key]) for key in row.keys()
                     if key not in MINTED},
                    sort_keys=True, default=str))
            tables[table] = sorted(rows)
        return tables
    finally:
        conn.close()


def _shared_prefix(left: str, right: str) -> str:
    index = 0
    while index < min(len(left), len(right)) and left[index] == right[index]:
        index += 1
    return left[:index]


@pytest.fixture(scope="module")
def two_runs(corpus, tmp_path_factory) -> tuple[dict, dict]:
    """The same command twice, each into a database that did not exist before."""
    workspace = tmp_path_factory.mktemp("r78-runs")
    first, second = workspace / "one.sqlite", workspace / "two.sqlite"
    _run(corpus, first)
    _run(corpus, second)
    return _normalised(first), _normalised(second)


# --- the property ---------------------------------------------------------------


def test_the_two_runs_read_the_same_files_the_same_way(two_runs):
    """Extraction first, because it is upstream of everything else.

    R-78 named OCR as its first suspect. On this corpus it is not: these three
    tables agreed run to run even while the edge count did not, and that is the
    measurement that moved the diagnosis downstream to P9.
    """
    first, second = two_runs
    for table in ("extraction_runs", "evidence", "text_units"):
        assert first[table] == second[table], (
            f"two runs over identical bytes disagree in `{table}`: "
            f"{len(first[table])} rows against {len(second[table])}. This is "
            "UPSTREAM of R-78's mechanism -- a reader answered differently on "
            "the same file, which is a different diagnosis from a derivation "
            "cutting in a per-run order")


def test_the_two_runs_settle_the_same_facts(two_runs):
    first, second = two_runs
    assert first["file_facts"] == second["file_facts"], (
        "P6 settled a different set of facts on the second reading of the same "
        "bytes")


@pytest.mark.parametrize(
    "table", ["groups", "memberships", "group_edges", "stop_rule_outcomes"])
def test_the_two_runs_derive_the_same_groups_and_edges(two_runs, table):
    """R-78 itself: 511 edges and 510 over one folder, twice."""
    first, second = two_runs
    assert len(first[table]) == len(second[table]), (
        f"two runs over one folder derived {len(first[table])} and "
        f"{len(second[table])} rows of `{table}` (`104` R-78)")
    assert first[table] == second[table], (
        f"`{table}` has the same number of rows in both runs and they are not "
        "the same rows, so a derivation chose differently between two files it "
        "could not tell apart by content")


@pytest.mark.parametrize("table", ["tree_nodes", "node_expected_values",
                                   "unresolved"])
def test_the_two_runs_propose_the_same_tree(two_runs, table):
    first, second = two_runs
    assert first[table] == second[table], (
        f"the folder tree this product proposes for one folder is not the same "
        f"tree on a second run: `{table}` differs")


def test_a_serial_run_reaches_the_same_answer_as_a_parallel_one(
        corpus, tmp_path_factory, two_runs):
    """Nothing about the plan may depend on how many cores read the files.

    `InlinePool` is what a run below the pool floor does and what every one of
    the suite's other end-to-end tests exercises; `ProcessPool` is what a real
    folder gets. If the two disagree, the guard above is measuring one path and
    the product ships the other.
    """
    workspace = tmp_path_factory.mktemp("r78-serial")
    database = workspace / "serial.sqlite"
    parallel = cli.EXTRACTION_WORKERS
    cli.EXTRACTION_WORKERS = 1
    try:
        _run(corpus, database)
    finally:
        cli.EXTRACTION_WORKERS = parallel
    serial = _normalised(database)

    for table in DERIVED:
        assert serial[table] == two_runs[0][table], (
            f"the run that read its files on one thread and the run that read "
            f"them in {parallel} processes disagree in `{table}`")
