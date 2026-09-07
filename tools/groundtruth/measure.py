"""What one run of the product actually did, read out of its plan database.

The database is the measurement surface, not the report on screen. The report is
written for a person and changes as its sentences improve; `placement_decisions`,
`tree_nodes`, `file_facts`, `extraction_runs` and `classifications` are the
product's own record of what it concluded, and they say things the report does
not -- including, on the day this was written, that three files were marked
protected while the screen said none were.

Nothing here opens a file of the owner's. It reads a SQLite database the product
wrote, and the one thing it deliberately does NOT read is `text_units.text`:
`complete_extracted_text` is in `privacy.vocabulary.ALWAYS_LOCAL`, and the
harness only ever needs to know HOW MANY units there are, never what is in them.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

#: `filesystem.record` observes the directory entry -- name, size, timestamps --
#: and never the bytes. Every other extractor opens the file.
FILESYSTEM_ONLY = "filesystem.record"

#: Extractors that recover text a person would recognise as the file's content.
#: `image.metadata` is not among them: a JPEG's EXIF coming back `complete` is
#: metadata recovered, not content, and counting it as content would flatter the
#: extraction number for every photograph in the corpus.
TEXT_PRODUCING = frozenset({
    "pdf.text", "text.structured", "docx.structure", "ocr", "ocr.apple_vision",
    "archive.manifest", "pptx.structure", "xlsx.structure", "html.structure",
    "email.structure",
})

#: P4's completeness words, best first. A file gets the best word any of its
#: content extractors returned: if `pdf.text` says `complete`, the content was
#: recovered, whatever a second-tier attempt said afterwards.
COMPLETENESS_ORDER = (
    "complete", "capped", "partial", "metadata_only", "deferred",
    "unsupported", "failed", "unreadable",
)
_RANK = {word: i for i, word in enumerate(COMPLETENESS_ORDER)}


@dataclass(frozen=True)
class Observation:
    """What the run concluded about one file."""

    path: str                      # corpus-relative
    indexed: bool
    excluded_by: str | None        # the §1.1 rule that set it aside, if any
    opened: bool                   # any extractor beyond `filesystem.record`
    text_units: int                # how many, never what
    #: `evidence` rows from the file's own BYTES -- `filesystem.record` excluded,
    #: because it observes the directory entry and every file has four of them.
    #: Counting those made a first attempt at this line read "199 of 199, 100%",
    #: which is true and says nothing.
    evidence_rows: int
    #: Of those, the ones a vocabulary could match a word against: the same
    #: text-producing extractors `content_recovered` uses. EXIF from a JPEG is
    #: an observation and is not prose, and the difference decides whether a
    #: file that went unmarked was SHOWN the words or merely never read.
    prose_evidence_rows: int
    extractors: tuple[str, ...]
    completeness: str              # the P4 word
    content_recovered: bool
    protected_marked: bool
    handling_class: str | None
    fields: Mapping[str, str]      # field_key -> canonical value, active facts
    #: Where each filled field came from -- 'rule', 'direct', 'llm_interpretation'.
    #: The only way to tell which half of the pipeline earned a number.
    field_origins: Mapping[str, str]
    unresolved_fields: tuple[str, ...]
    outcome: str | None            # 'place', 'abstain', ... or None
    destination: tuple[str, ...]   # folder labels, root first
    asked: bool                    # the decision carried a question for the person

    @property
    def extension(self) -> str:
        suffix = Path(self.path).suffix.lower()
        return suffix or "(none)"

    @property
    def classified(self) -> bool:
        """P7 gave this file a handling class.

        §8.4 makes a handling class a precondition of asking a model, so an
        unclassified file cannot reach one whatever else is wired. This is the
        gate every later stage stands behind, which is why it is reported on a
        line of its own rather than folded into extraction.
        """
        return self.handling_class is not None


@dataclass(frozen=True)
class RunObservation:
    """What one `--situation` run of the product did to the whole corpus."""

    situation: str
    label: str
    promised_levels: tuple[str, ...]
    files: Mapping[str, Observation]
    structural_questions: int
    node_count: int
    built_depth: int               # deepest folder chain below the top level
    report: str
    #: What the model path actually did this run. Every count is a table the
    #: product wrote, never a guess from the report on screen.
    model: Mapping[str, int] = field(default_factory=dict)
    #: How many of `model`'s rows were HANDED to this run by
    #: `--reuse-answers-from` rather than bought by it (`104` R-123). Empty on
    #: every ordinary run. Carried beside `model` and never subtracted from it
    #: here: this class reports what is in the database, and what that means for a
    #: reader is the scorecard's sentence to write.
    seeded: Mapping[str, int] = field(default_factory=dict)
    #: The prior run those rows came from, as a line a person can act on: the
    #: directory and the commit that produced it. Counts without a source cannot
    #: be checked by anybody, which is the whole reason a seeded row is labelled.
    seeded_from: str = ""
    #: R-46's two-sided count: files this run stopped BEFORE a model, split by
    #: which of the two stops caught them. A scoreboard that asked
    #: `cli.model_route_permitted` and stopped reported "19 blocked" while 130
    #: more were refused at the door, and a number meaning "the route let N
    #: through" was read as "N reached a model".
    blocked_at_route: int = 0
    #: The door's own refusals, keyed by the word it refused with. Read from what
    #: the run RECORDED, not predicted by re-running the gate --
    #: `tools.groundtruth.payload` is the instrument that predicts, and the two
    #: answer different questions about the same corpus.
    gate_refusals: Mapping[str, int] = field(default_factory=dict)
    #: Files that reached neither: nothing releasable, so no dossier was built and
    #: there was nothing for the gate to refuse. Counted because R-46 is that a
    #: file which did not reach a model must be counted somewhere.
    never_built: int = 0


#: The tables the LLM path writes. A run that called nothing leaves them all at
#: zero, which is a measurement and not an absence of one.
MODEL_TABLES = ("llm_dossier", "llm_response", "llm_verdict", "llm_refusal",
                "llm_call_failure", "llm_pre_call_abstention",
                "llm_grounding_report", "llm_budget_reservation")


#: Where `record_refusal` puts P7's word. `_payload` serialises the whole
#: `Refusal`, whose `denied` half carries the reason, so the word is one level in.
#: Read defensively: a payload this cannot read is counted under its own name
#: rather than dropped, because dropping it would be the undercount again.
def _refusal_reason(payload: str) -> str:
    try:
        loaded = json.loads(payload)
    except (TypeError, ValueError):
        return "unreadable_refusal_payload"
    if isinstance(loaded, dict):
        denied = loaded.get("denied")
        if isinstance(denied, dict) and isinstance(denied.get("reason"), str):
            return denied["reason"]
        if isinstance(loaded.get("reason"), str):
            return loaded["reason"]
    return "unstated"


def _blocked_tally(connection) -> tuple[int, dict[str, int], int]:
    """The three numbers R-46 needed, all from tables the product wrote.

    **Route.** `unresolved` rows reading `privacy_withheld` are what
    `facts.resolver` writes when `cli.model_route_permitted` says no, one per open
    field, so the FILES are what is counted and not the rows.

    **Gate.** `llm_refusal`, grouped by the reason inside the payload P7 denied
    with. Grouped rather than summed because "protected" and "no safety evidence"
    are different things to fix and one number hides which.

    **Never built.** Files with no dossier, no refusal and no response: nothing
    releasable, so there was nothing to refuse. A file that reached no model has
    to be counted somewhere, and this is the somewhere for these.
    """
    try:
        route = _rows(connection, "select count(distinct file_id) as n from "
                                  "unresolved where reason = 'privacy_withheld'")
        at_route = route[0]["n"] if route else 0
    except sqlite3.Error:
        at_route = 0
    gate: dict[str, int] = {}
    try:
        for row in _rows(connection, "select payload from llm_refusal"):
            reason = _refusal_reason(row["payload"])
            gate[reason] = gate.get(reason, 0) + 1
    except sqlite3.Error:
        gate = {}
    # THE REMAINDER, SO THE THREE PARTITION AND CANNOT DOUBLE-COUNT. A file
    # withheld at the route has no dossier row, and so does a file the gate
    # refused: `record_dossier` fires inside `_issue_and_validate`, which
    # `run_call` reaches only after `gate.release` has returned `Released`. So
    # "included files with no dossier" is all three groups at once, and printing
    # it as the third beside the other two would report 19 + 149 + 176 blocked
    # files out of 176 -- R-46's own failure, counting one file twice, on the
    # line built to stop it.
    #
    # Never-built is therefore what is LEFT: no dossier, not withheld at the
    # route, and not one of the door's refusals. One refusal is one file here
    # because A_fact asks once per file, which is what makes the subtraction
    # sound; a negative would mean that stopped being true, so it is reported
    # rather than clamped away.
    try:
        without = _rows(connection, """
            select count(*) as n from files f
             where f.scan_state = 'included'
               and not exists (select 1 from llm_dossier d
                                where d.subject_ref = f.file_id)
               and not exists (select 1 from unresolved u
                                where u.file_id = f.file_id
                                  and u.reason = 'privacy_withheld')
        """)[0]["n"]
    except sqlite3.Error:
        without = 0
    never = without - sum(gate.values())
    return (at_route, dict(sorted(gate.items(), key=lambda kv: (-kv[1], kv[0]))),
            never)


def _model_tally(connection) -> dict[str, int]:
    tally = {}
    for table in MODEL_TABLES:
        try:
            tally[table] = _rows(connection, f'select count(*) as n from "{table}"')[0]["n"]
        except sqlite3.Error:
            tally[table] = 0          # an older database without the table
    return tally


def _rows(connection, sql, *args):
    connection.row_factory = sqlite3.Row
    return list(connection.execute(sql, args))


def _destination_of(node_id, nodes) -> tuple[str, ...]:
    chain, seen = [], set()
    while node_id and node_id in nodes and node_id not in seen:
        seen.add(node_id)
        label, parent = nodes[node_id]
        chain.append(label)
        node_id = parent
    return tuple(reversed(chain))


def observe_run(database: str | Path, corpus_root: str | Path, *,
                situation: str, label: str, promised_levels=(), report: str = "",
                seeded: Mapping[str, int] | None = None,
                seeded_from: str = "") -> RunObservation:
    """Read one plan database into observations, one per corpus-relative path."""
    root = str(Path(corpus_root).resolve())
    connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        return _observe(connection, root, situation, label,
                        tuple(promised_levels), report, dict(seeded or {}),
                        seeded_from)
    finally:
        connection.close()


def _relative(path: str, root: str) -> str | None:
    if path == root:
        return None
    prefix = root.rstrip("/") + "/"
    return path[len(prefix):] if path.startswith(prefix) else None


def _observe(connection, root, situation, label, promised_levels, report,
             seeded=None, seeded_from=""):
    nodes = {r["node_id"]: (r["display_label"], r["parent_node_id"])
             for r in _rows(connection, "select node_id, display_label, "
                                        "parent_node_id from tree_nodes")}

    excluded: dict[str, str] = {}
    for row in _rows(connection, "select path, rule from exclusion_verdicts"):
        relative = _relative(row["path"], root)
        if relative is not None:
            excluded[relative] = row["rule"]

    files, by_id = {}, {}
    for row in _rows(connection, "select file_id, current_path from files"):
        relative = _relative(row["current_path"], root)
        if relative is not None:
            by_id[row["file_id"]] = relative

    runs: dict[str, list[sqlite3.Row]] = {}
    for row in _rows(connection, "select file_id, extractor_name, completeness, "
                                 "run_id from extraction_runs"):
        runs.setdefault(row["file_id"], []).append(row)

    units: dict[str, int] = {}
    for row in _rows(connection,
                     "select e.file_id as file_id, count(*) as n from text_units t "
                     "join extraction_runs e on t.run_id = e.run_id group by e.file_id"):
        units[row["file_id"]] = row["n"]

    observations: dict[str, int] = {}
    prose: dict[str, int] = {}
    for row in _rows(connection, "select file_id, extractor_name, count(*) as n "
                                 "from evidence where superseded_by is null "
                                 "group by file_id, extractor_name"):
        if row["extractor_name"] == FILESYSTEM_ONLY:
            continue
        observations[row["file_id"]] = observations.get(row["file_id"], 0) + row["n"]
        if row["extractor_name"] in TEXT_PRODUCING:
            prose[row["file_id"]] = prose.get(row["file_id"], 0) + row["n"]

    protected, handling = {}, {}
    for row in _rows(connection, "select file_id, protected, handling_class from "
                                 "classifications where superseded_by is null"):
        protected[row["file_id"]] = bool(row["protected"])
        handling[row["file_id"]] = row["handling_class"]

    facts: dict[str, dict[str, str]] = {}
    origins: dict[str, dict[str, str]] = {}
    for row in _rows(connection,
                     'select f.file_id as file_id, f.field_key as field_key, '
                     'f.origin as origin, v.canonical_value as value from file_facts f '
                     'join "values" v on f.value_id = v.value_id where f.active = 1'):
        facts.setdefault(row["file_id"], {})[row["field_key"]] = row["value"]
        origins.setdefault(row["file_id"], {})[row["field_key"]] = row["origin"]

    unresolved: dict[str, set[str]] = {}
    for row in _rows(connection, "select file_id, field_key from unresolved "
                                 "where superseded_by is null"):
        unresolved.setdefault(row["file_id"], set()).add(row["field_key"])

    routing: dict[str, str] = {}
    for row in _rows(connection, "select file_id, unrouted_completeness from "
                                 "extraction_routing where unrouted_completeness "
                                 "is not null"):
        routing[row["file_id"]] = row["unrouted_completeness"]

    decisions: dict[str, sqlite3.Row] = {}
    for row in _rows(connection, "select subject_ref, outcome, node_id, payload from "
                                 "placement_decisions where superseded_by is null"):
        parts = row["subject_ref"].split(":")
        if len(parts) >= 2 and parts[0] == "file":
            decisions[parts[1]] = row

    for file_id, relative in by_id.items():
        my_runs = runs.get(file_id, [])
        content = [r for r in my_runs if r["extractor_name"] != FILESYSTEM_ONLY]
        extractors = tuple(sorted({r["extractor_name"] for r in my_runs}))
        n_units = units.get(file_id, 0)

        if content:
            word = min((r["completeness"] for r in content), key=lambda w: _RANK.get(w, 99))
        else:
            word = routing.get(file_id, "unreadable" if not my_runs else "unsupported")

        recovered = any(
            r["extractor_name"] in TEXT_PRODUCING
            and r["completeness"] in ("complete", "capped", "partial")
            for r in content) and n_units > 0

        decision = decisions.get(file_id)
        outcome = decision["outcome"] if decision else None
        destination = _destination_of(decision["node_id"], nodes) if decision else ()
        asked = False
        if decision:
            try:
                asked = json.loads(decision["payload"]).get("ask") is not None
            except (ValueError, TypeError):
                asked = False

        files[relative] = Observation(
            path=relative,
            indexed=True,
            excluded_by=excluded.get(relative),
            opened=bool(content) or n_units > 0,
            text_units=n_units,
            evidence_rows=observations.get(file_id, 0),
            prose_evidence_rows=prose.get(file_id, 0),
            extractors=extractors,
            completeness=word,
            content_recovered=recovered,
            protected_marked=protected.get(file_id, False),
            handling_class=handling.get(file_id),
            fields=facts.get(file_id, {}),
            field_origins=origins.get(file_id, {}),
            unresolved_fields=tuple(sorted(unresolved.get(file_id, ()))),
            outcome=outcome,
            destination=destination,
            asked=asked,
        )

    # A file the scan set aside never becomes a `files` row, and "never silently
    # omitted" means it still has to appear in the scorecard. The corpus on disk
    # is what decides which files exist, not the `files` table -- otherwise a
    # file the product dropped would be invisible to the instrument that exists
    # to notice it.
    #
    # An exclusion verdict may name a DIRECTORY: §1.1's software-project rule
    # sets aside `matcher/match`, not the eleven modules under it. So a verdict
    # is matched against a path and against every path beneath it.
    for path in sorted(Path(root).rglob("*")):
        if not path.is_file():
            continue
        relative = _relative(str(path), root)
        if relative is None or relative in files:
            continue
        rule = excluded.get(relative)
        if rule is None:
            parts = relative.split("/")
            for cut in range(len(parts) - 1, 0, -1):
                rule = excluded.get("/".join(parts[:cut]))
                if rule is not None:
                    break
        files[relative] = Observation(
            path=relative, indexed=False, excluded_by=rule, opened=False,
            text_units=0, evidence_rows=0, prose_evidence_rows=0,
            extractors=(), completeness="unreadable",
            content_recovered=False, protected_marked=False, handling_class=None,
            fields={}, field_origins={}, unresolved_fields=(), outcome=None,
            destination=(), asked=False)

    depth = 0
    for node_id in nodes:
        depth = max(depth, len(_destination_of(node_id, nodes)))

    _blocked = _blocked_tally(connection)
    return RunObservation(
        situation=situation,
        label=label,
        promised_levels=promised_levels,
        files=files,
        structural_questions=_rows(connection, "select count(*) as n from "
                                               "structural_questions")[0]["n"],
        model=_model_tally(connection),
        seeded=dict(seeded or {}),
        seeded_from=seeded_from,
        blocked_at_route=_blocked[0],
        gate_refusals=_blocked[1],
        never_built=_blocked[2],
        node_count=len(nodes),
        built_depth=max(0, depth - 1),   # below the top-level folder
        report=report,
    )
