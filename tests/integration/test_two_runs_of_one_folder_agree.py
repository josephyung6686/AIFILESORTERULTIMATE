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

**And it has to hold to the end of the pipeline, not to the end of P9 (`104`
R-111).** The tables below stopped at `unresolved`, so the day P9 became
reproducible the guard went green while `placement_decisions` was still writing a
different `graph_anchors` for 24 of this corpus's 36 files. The record of what a
reviewer is shown is part of the answer; a stage left out of the list is a stage
nothing measures.

**What "the same" means here.** A `file_id` is a `uuid4` and a plan version, a
group and a tree node all carry a minted address, so two from-empty runs can never
be byte-identical as raw rows and it would be no virtue if they were. Every minted
id is therefore replaced by what it NAMES — a file by its path, a tree node by its
chain of labels from the root — and what is left is what the run concluded. That
is the same normalisation `w4-scale` used to compare plan rows across a code
change, spelled out here so the guard says what it is checking.

**The pool is real.** The corpus is deliberately larger than
`cli.EXTRACTION_WORKERS`, so the files are read in seven worker processes that
finish in whatever order the operating system schedules and at least two of them
are always reading at once. A run at ONE worker has to reach the same answer, and
the last test asks for that: a product whose plan depends on how many cores it was
given is not one either. Both counts are `ProcessPool` since R-138 -- the deadline
that stops a wedged reader stops it by killing a process -- so what the last test
varies is overlap and nothing else.
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
#: A plan version is minted `version_<hex>_<counter>`: no dashes, so `UUID` cannot
#: see it, and it reaches every P11 table as a column AND inside three record ids.
#: What a version IS to a reader is its place in the chain -- draft, refined,
#: frozen -- which the counter names and the hex does not.
PLAN_VERSION = re.compile(r"version_[0-9a-f]{6,}_(\d+)")

#: What a run DERIVES, as opposed to what it was handed. Both halves are here on
#: purpose: if `file_facts` and `evidence` ever disagree between two runs the
#: cause is upstream of P9 and the diagnosis is a different one, so the guard
#: should say which half moved rather than only that something did.
#:
#: **The three P11 tables are here because of `104` R-111.** Everything above
#: `placement_decisions` agreed run to run from the day R-78 was closed, and the
#: record of WHAT WAS SHOWN for a placement did not: `payload.graph_anchors`
#: differed in 24 of this corpus's 36 rows, and in 870 of 1,000 on the scale
#: agent's synthetic corpus. Stopping the guard at `unresolved` is what let a
#: whole stage's reproducibility go unmeasured for one register row.
DERIVED = (
    "extraction_runs", "evidence", "text_units", "file_facts",
    "groups", "memberships", "group_edges", "stop_rule_outcomes",
    "tree_nodes", "node_expected_values", "unresolved",
    "placement_decisions", "placement_index_entries", "placement_group_plans",
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

#: `104` R-105. Two files that share ONE labelled line and nothing else: two
#: content hashes, one stated value, and a group whose anchor is stated by both.
#: The homework files above share lines too, but they share five of them and sit
#: in a folder named after the course, so nothing there separates "the anchor
#: names each file's own observation" from "the anchor names the folder's". These
#: two do.
SHARED_COURSE = "CHEM2200"
SHARED_LINE_FILES = (
    ("safety sheet.txt",
     "Rinse the burette twice before the titration begins."),
    ("reading list.txt",
     "Bring the green notebook and read chapter nine first."),
)


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

    # THE SHARED LINE, in its own folder so the path says nothing about the
    # course. Before `104` R-97 the group these two form carried one observation
    # key for both of them -- whichever file the corpus loop reached first -- and
    # the other was recorded as citing a reading of bytes it does not contain.
    shared = root / "Shared"
    shared.mkdir()
    for name, sentence in SHARED_LINE_FILES:
        (shared / name).write_text(
            f"Course: {SHARED_COURSE}\n\n{sentence}\n", encoding="utf-8")

    written = sum(1 for path in root.rglob("*") if path.is_file())
    # ENOUGH FILES THAT THE WORKERS ARE GENUINELY CONCURRENT. It used to be a
    # comparison against `cli.EXTRACTION_POOL_FLOOR`: below that floor every read
    # happened on the calling thread, so a corpus under it would have tested a
    # serial run while claiming to test a parallel one. R-138 removed the floor --
    # a reader on the calling thread cannot be given a deadline -- so every corpus
    # is now read in workers and the question this guards is the other one: a
    # corpus smaller than the worker count never has two readers running at once,
    # and an ordering defect needs two.
    assert written > cli.EXTRACTION_WORKERS, (
        f"{written} files against {cli.EXTRACTION_WORKERS} workers, so no two "
        "reads would ever overlap and this file would not be testing a parallel "
        "run at all")
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
        # And the third: `unresolved_id` is a `uuid4().hex`, so it carries no
        # dashes and the regex below cannot see it either, and `record_id`
        # projects it. Every file in the original corpus stated all five fields,
        # so this table was empty and the hole was invisible; the two files that
        # share ONE line state one field and attempt four, which is what a real
        # folder looks like. Replaced by what the row is ABOUT rather than
        # dropped, so two runs that record a different SET of unresolved fields
        # still differ here.
        for row in conn.execute(
                "SELECT unresolved_id, file_id, field_key, reason, cache_key "
                "FROM unresolved"):
            names[row["unresolved_id"]] = (
                f"<unresolved:{names.get(row['file_id'], row['file_id'])}|"
                f"{row['field_key']}|{row['reason']}|{row['cache_key']}>")

        # One alternation rather than a pass per name: a run of this size mints
        # some hundreds of addresses and every string cell would otherwise be
        # scanned once for each of them.
        minted = re.compile("|".join(
            re.escape(name) for name in sorted(names, key=len, reverse=True)))

        def say(value):
            if not isinstance(value, str):
                return value
            value = minted.sub(lambda found: names[found.group(0)], value)
            value = PLAN_VERSION.sub(lambda found: f"<plan:{found.group(1)}>",
                                     value)
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
def databases(corpus, tmp_path_factory) -> tuple[Path, Path]:
    """The same command twice, each into a database that did not exist before.

    Separate from `two_runs` so that the property below can read the rows AS
    WRITTEN -- normalisation replaces every minted id with what it names, which is
    what makes two runs comparable and what would erase the join a citation is.
    """
    workspace = tmp_path_factory.mktemp("r78-runs")
    first, second = workspace / "one.sqlite", workspace / "two.sqlite"
    _run(corpus, first)
    _run(corpus, second)
    return first, second


@pytest.fixture(scope="module")
def two_runs(databases) -> tuple[dict, dict]:
    first, second = databases
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


@pytest.mark.parametrize("table", ["placement_decisions",
                                   "placement_index_entries",
                                   "placement_group_plans"])
def test_the_two_runs_record_the_same_placements(two_runs, table):
    """`104` R-111. The placement was the same; the RECORD of it was not.

    `placement_decisions.payload.graph_anchors` is §6.4's node-local graph as a
    reviewer sees it -- which files were shown as connecting this one to that
    folder. On two runs over this corpus 24 of 36 rows carried a different set,
    while every table above agreed to the byte, so the file went to the same
    place both times and could not be shown the same reason twice.

    The mechanism was R-78's, one seam further down. `build_node_local_graph`
    cut §8.6's two ceilings over `sorted(kept, key=(-weight, to_file_id))`, and
    `cli.typed_edges_of` gives every edge `weight = 1.0` because P9 stores none
    -- so the entire ranking was a comparison of two `uuid4`s minted by P1, and
    the Downloads copies in this corpus are files that tie on everything else.

    Parametrised over all three P11 tables rather than asserted on the payload
    alone: if the cut ever starts moving `outcome` or `node_id`, the anchors were
    feeding `is_typed_support` into a decision and that is a larger finding than
    a record that reads differently.
    """
    first, second = two_runs
    assert len(first[table]) == len(second[table]), (
        f"two runs over one folder wrote {len(first[table])} and "
        f"{len(second[table])} rows of `{table}`")
    assert first[table] == second[table], (
        f"`{table}` has the same number of rows in both runs and they are not "
        "the same rows, so P11 recorded a different answer about two files it "
        "could not tell apart by content (`104` R-111)")


def test_a_serial_run_reaches_the_same_answer_as_a_parallel_one(
        corpus, tmp_path_factory, two_runs):
    """Nothing about the plan may depend on how many cores read the files.

    One worker and seven are both `ProcessPool` since R-138 -- a deadline is
    enforced by killing a process, so a deployment that read on the calling thread
    was a deployment whose runs could hang -- and what differs between them is
    only how many readers overlap. That is exactly what must not reach the plan.
    If the two disagree, the guard above is measuring one path and the product
    ships the other.
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


# --- `104` R-105 / R-97: a shared line is not a shared citation -------------------


def _anchor_facts(database: Path):
    """Every anchor fact every group recorded, with the run's own file paths."""
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        names = {row["file_id"]: row["current_path"].rsplit("/", 1)[-1]
                 for row in conn.execute(
                     "SELECT file_id, current_path FROM files")}
        owners: dict[str, set[str]] = {}
        for row in conn.execute(
                "SELECT observation_key, file_id FROM evidence"):
            owners.setdefault(row["observation_key"], set()).add(row["file_id"])
        facts = []
        for row in conn.execute("SELECT group_id, anchor_facts FROM groups"):
            for fact in json.loads(row["anchor_facts"] or "[]"):
                facts.append((row["group_id"], fact))
        return facts, names, owners
    finally:
        conn.close()


def test_every_anchor_fact_pairs_each_stating_file_with_its_own_observation(
        databases):
    """The cause R-105 named, asserted over every group a real run produced.

    An `AnchorFact` carried ONE observation key and a list of the files that state
    the value, so every file after the first was recorded as citing the first
    file's reading. P7 resolves each requested item to the file it belongs to and
    refuses with `UnresolvableSpan` when that file is outside the request's
    targets -- which is how a 52-file run died at its first B dossier.

    `file_id in owners` and not `owners == {file_id}`: two byte-identical files
    genuinely share a key, because `observation_key` is content-addressed and
    `facts.families` depends on exactly that. The Downloads copies in this corpus
    are that case, and it stays legal.
    """
    facts, names, owners = _anchor_facts(databases[0])
    assert facts, "no group recorded an anchor fact; this guard would be vacuous"

    for group_id, fact in facts:
        file_ids = fact["file_ids"]
        keys = fact["observation_keys"]
        assert len(keys) == len(file_ids), (group_id, fact["field"])
        for file_id, key in zip(file_ids, keys):
            if key is None:
                continue
            assert file_id in owners.get(key, set()), (
                f"{group_id}: {names.get(file_id, file_id)} is recorded as "
                f"citing an observation of "
                f"{sorted(names.get(one, one) for one in owners.get(key, set()))}")


def test_the_two_files_that_share_a_line_cite_two_different_observations(
        databases):
    """And the guard above is not vacuous: this corpus really does produce a
    multi-file anchor with more than one citation under it."""
    facts, names, _owners = _anchor_facts(databases[0])
    wanted = {name for name, _ in SHARED_LINE_FILES}

    shared = [
        fact for _group_id, fact in facts
        if fact["value"] == SHARED_COURSE
        and {names.get(one) for one in fact["file_ids"]} == wanted
    ]
    assert shared, (
        f"the two files sharing `Course: {SHARED_COURSE}` did not form an anchor "
        "stated by both, so nothing here tests a shared line")
    for fact in shared:
        assert len(fact["file_ids"]) == 2
        assert len(set(fact["observation_keys"])) == 2, (
            "both files were recorded as citing one observation, which is the "
            "borrowed citation `104` R-97 is about")


def test_the_shared_line_does_not_cost_the_two_runs_their_agreement(two_runs):
    """R-78's property with R-105's shape present. The per-file keys are content
    addresses and the order they are written in is `anchoring_files`' order, which
    is the graph's -- ranked by content, never by a per-run `uuid4`."""
    first, second = two_runs
    assert first["groups"] == second["groups"]
