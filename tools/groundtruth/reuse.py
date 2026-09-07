"""Seeding a fresh run's database with a prior run's model ANSWERS. `104` R-123.

`run.py` gives every run a fresh database and says why: "answers, plan versions and
consent are all remembered between runs against one database, so sharing one would
let the first situation's decisions reach the second". That is right, and it costs.
R-109's reuse -- an identical question under an identical key is answered from the
record and no call is made -- reads the PRODUCT's own database, so under the
scoreboard it never fires: the 7 Sep local rerun re-asked all 172 A_fact dossiers
although no file, no prompt and no model had changed, and a cloud rerun is billed
twice for the same reason.

So the fresh database stays fresh in every respect that made it fresh, and is given
one thing before the run starts: the rows a reuse can be DECIDED from.

**What is copied, and why each.**

  * `llm_call_identity` -- the key itself. `store.prior_call` looks the newest row
    for an identity up, and every dimension of that identity is read off the call
    the next run would build (`model_facts.call_identity_dimensions`). A changed
    file's `content_hash`, a changed `prompt_fingerprint`, a different `model_id`
    or a changed policy make a DIFFERENT digest, and a seeded row under the old
    digest is then never looked up. That is the whole safety argument: this seeds a
    cache, it does not seed an answer, and a stale row is inert rather than wrong.
  * `llm_verdict` -- what the model actually answered. `store.answered_fields` reads
    every non-superseded verdict under the prior dossier, whatever its outcome, and
    that set is what the reuse decision compares the still-open fields against.
    Without it a seeded identity resolves to no answers and every file is re-asked.
  * `llm_dossier` -- the question those verdicts answered. Not read by the reuse
    decision; copied because `record_call_reuse` writes `prior_dossier_id` onto every
    reuse row, and a provenance column naming a row that is not in the database is
    the kind of dangling reference every append-only table here exists to prevent.
  * `llm_response` -- the bytes the answer was parsed out of, for the same reason.
    `shadow.py` reads `llm_response` by dossier, and a verdict whose response is
    absent cannot be explained to anyone who asks why a file was not asked again.
  * `llm_verdict_supersession` -- copied only when BOTH of its verdicts are, so it
    can never dangle. A re-judgement is a different answer and `answered_fields`
    excludes the superseded row; the audit trail for that exclusion travels with it.

**What is NOT copied, and this list is the point of the flag rather than a caveat.**
Nothing about placement, nothing under `structural_answers`, no consent grant, no
plan version, and none of the `llm_call_reuse` rows themselves. Those are exactly
what the fresh database exists to keep out: a decision the previous situation made
is not evidence for this one, and a reuse row copied forward would report savings
this run did not make. Refusals, call failures and pre-call abstentions record no
identity, so the dossier filter drops them and the file is asked again -- which is
what R-109 already promises, and is preserved here rather than restated.

`llm_response.release_id` and `release_audit_id` name rows in `release_ledger`, which
is deliberately NOT seeded: a single-use capability that paid for a call in another
run has not paid for anything in this one, and minting a fresh run's ledger from an
old one would be a lie about what this run spent. The two columns dangle on purpose.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

_ROOT = Path(__file__).resolve().parents[2]

#: The `--user` every scoreboard run is given. Here rather than spelled twice,
#: because `_one_run` passes it to `cli` and the pre-scan below passes it to
#: `record_selection`, and a selection recorded under a different name than the run
#: that follows it would say two people chose this corpus.
SCOREBOARD_USER = "groundtruth"


class ReuseRefused(Exception):
    """The prior directory cannot be seeded from, and nothing has been run yet.

    Every one of these is raised BEFORE the first run starts. `run.py` deletes each
    situation's database at the top of its own run, so a refusal discovered inside a
    run would arrive after the thing it was protecting had already been destroyed.
    """


#: The tables copied verbatim, in insert order, once the identity and the dossier
#: have been TRANSLATED. Each filter reads `main`, which by then holds exactly the
#: dossiers whose file this corpus still has at that path with those bytes: a prior
#: answer about a file that moved or changed is left behind, and so is everything
#: under it. Filtering against the prior instead would copy a response and a verdict
#: whose dossier never arrived.
SEED_PLAN: tuple[tuple[str, str], ...] = (
    ("llm_response", "WHERE dossier_id IN (SELECT dossier_id FROM main.llm_dossier)"),
    ("llm_verdict", "WHERE dossier_id IN (SELECT dossier_id FROM main.llm_dossier)"),
    # Both endpoints, so a supersession can never name a verdict that is not here.
    # `llm_verdict` is filled by the line above before this one reads it.
    ("llm_verdict_supersession",
     "WHERE old_verdict_id IN (SELECT verdict_id FROM main.llm_verdict) "
     "AND new_verdict_id IN (SELECT verdict_id FROM main.llm_verdict)"),
)


def _canonical(mapping) -> str:
    """The dimensions as `store.canonical_json` writes them, so a re-read matches."""
    _src_on_path()
    from evidence_shape.canonical import canonical_json

    return canonical_json(mapping)


@dataclass(frozen=True)
class Seeded:
    """What one fresh database was given before its run started."""

    #: Distinct `identity_id`s, which is one per QUESTION and so the number that is
    #: comparable with the `llm_call_reuse` count the run leaves behind.
    answers: int
    #: Rows per table, so "seeded 172" can be taken apart by whoever doubts it.
    rows: Mapping[str, int]
    #: Kept apart from `rows` because it is the one number the spend arithmetic
    #: needs: a response row that was seeded is not a call this run made.
    responses: int
    #: Prior answers left behind because this corpus has no file at that path with
    #: those bytes -- a file changed, moved, renamed or deleted since. Reported
    #: rather than swallowed: it is the difference between "the prior directory
    #: had nothing for this corpus" and "the corpus moved on", and a person
    #: choosing whether to trust a cheap rerun needs to know which.
    skipped: int = 0


def _src_on_path() -> None:
    """`src/` is not on the path for `tools/`. Done lazily, as `__main__` does it.

    At import time this module would put `src` on the path for everything that
    imports `run.py`, including the whole `tests/tools` package, which is a
    side effect nobody asked this file for.
    """
    if str(_ROOT / "src") not in sys.path:
        sys.path.insert(0, str(_ROOT / "src"))


def prior_database(directory: Path, situation: str) -> Path:
    """Where a prior run of `situation` left its database. `run.py`'s own naming."""
    return directory / f"{situation.replace('.', '_')}.sqlite"


def seeded_note(out_dir: Path, situation: str) -> Path:
    """Where a run records what it was handed, beside the database it was handed to.

    A file rather than a column: every `llm_*` table is append-only by trigger, and
    a "this row was seeded" column would be a change to the PRODUCT's schema made
    for the scoreboard's convenience. `--score-only` re-reads these databases long
    after the run, and without this it would report seeded rows as calls somebody
    paid for.
    """
    return out_dir / f"{situation.replace('.', '_')}.seeded.json"


def write_seeded(out_dir: Path, situation: str, given: "Seeded") -> None:
    seeded_note(out_dir, situation).write_text(
        json.dumps({"answers": given.answers, "skipped": given.skipped,
                    "rows": dict(given.rows)}, indent=2, sort_keys=True),
        encoding="utf-8")


def read_seeded(out_dir: Path, situation: str) -> dict[str, int]:
    """Rows seeded into this situation's database, or `{}` if none ever were.

    Unreadable is treated as none, and deliberately: this decides how a number is
    LABELLED, and a scoreboard that refused to print because a note beside it was
    malformed would withhold the measurement to protect its footnote.
    """
    note = seeded_note(out_dir, situation)
    if not note.exists():
        return {}
    try:
        return {str(k): int(v)
                for k, v in json.loads(note.read_text(encoding="utf-8"))
                .get("rows", {}).items()}
    except (TypeError, ValueError):
        return {}


def _llm_schema_objects(conn: sqlite3.Connection) -> set[tuple[str, str, str]]:
    """Every table, index and trigger `schema.py` owns, as SQLite stored it.

    Compared verbatim rather than normalised, because both sides are generated by
    the one `create_llm_schema` and any difference at all in the text IS a
    difference in the schema. `sql` is NULL for the indexes SQLite makes itself
    from a PRIMARY KEY, and those are deterministic too, so the null is carried
    rather than filtered.
    """
    _src_on_path()
    from llm_harness.schema import TASK3_TABLES

    names = ", ".join("?" * len(TASK3_TABLES))
    return {
        (row[0], row[1], row[2] or "")
        for row in conn.execute(
            f"SELECT type, name, sql FROM sqlite_master WHERE tbl_name IN ({names})",
            TASK3_TABLES,
        )
    }


def _expected_llm_schema() -> set[tuple[str, str, str]]:
    _src_on_path()
    from llm_harness.schema import create_llm_schema

    conn = sqlite3.connect(":memory:")
    try:
        create_llm_schema(conn)
        return _llm_schema_objects(conn)
    finally:
        conn.close()


def refuse_unless_seedable(directory: Path, situations, *, out_dir: Path,
                           score_only: bool) -> None:
    """Every reason this cannot work, said before the first database is deleted."""
    if score_only:
        raise ReuseRefused(
            "--reuse-answers-from cannot be used with --score-only: --score-only "
            "runs nothing, so there is no run to seed and nothing to save."
        )
    if directory.resolve() == out_dir.resolve():
        raise ReuseRefused(
            f"--reuse-answers-from {directory} is also --out. Each run deletes its "
            f"own database before it starts, so the prior answers would be "
            f"destroyed before they could be read. Write this run to a different "
            f"--out."
        )
    if not directory.is_dir():
        raise ReuseRefused(
            f"--reuse-answers-from {directory}: no such directory. Nothing has "
            f"been run."
        )
    expected = _expected_llm_schema()
    for situation in situations:
        path = prior_database(directory, situation)
        if not path.exists():
            raise ReuseRefused(
                f"--reuse-answers-from {directory}: no database for {situation} at "
                f"{path.name}. Nothing has been run. Score only the situations that "
                f"directory holds, with --situation, or point somewhere else."
            )
        try:
            conn = sqlite3.connect(path)
            try:
                found = _llm_schema_objects(conn)
            finally:
                conn.close()
        except sqlite3.Error as error:
            raise ReuseRefused(
                f"--reuse-answers-from {path}: SQLite cannot read it ({error}). "
                f"Nothing has been run."
            ) from error
        if found != expected:
            missing = sorted(name for _kind, name, _sql in expected - found)
            extra = sorted(name for _kind, name, _sql in found - expected)
            raise ReuseRefused(
                f"--reuse-answers-from {path}: its llm_* schema is not this "
                f"checkout's. This checkout has and it has not: "
                f"{', '.join(missing) or 'nothing'}; it has and this checkout does "
                f"not: {', '.join(extra) or 'nothing'}. Seeding half a schema "
                f"would put rows under columns that mean something else. Nothing "
                f"has been run. Re-run that corpus from scratch with this "
                f"checkout, or point at a directory written by it."
            )


def _scan_the_corpus(conn, corpus: Path) -> None:
    """`cli.run`'s own P3 step, with `cli.p1_p7_authorities`' own arguments.

    THE FILE ID IS WHY THIS IS HERE. `store.CALL_IDENTITY_DIMENSIONS` carries
    `subject_ref`, `model_facts.call_identity_dimensions` fills it with the
    `file_id`, and `files_table.py:286` mints that as `str(uuid.uuid4())` the first
    time a path is seen -- so it names a file WITHIN one database and nothing
    across two. Seeding a prior run's identity rows verbatim is therefore inert:
    measured, 2 calls, seed, 2 calls again, `llm_call_reuse` empty, with
    `subject_ref` the only dimension of nine that moved. The fix is not to weaken
    the key but to learn what this database will call each file, which means
    scanning it, which means running the scan the run itself runs.

    Every argument is read off the composition root rather than chosen here, and
    the path is resolved the way `cli.main` resolves it (`cli.py:8714`). That last
    one is not a detail: on macOS the corpus arrives as `/var/...` and the run
    records `/private/var/...`, so an unresolved path matches no file and every
    answer is silently skipped. Measured, before it was fixed: 0 of 2 translated.

    The run then scans again and finds this scan's rows unchanged --
    `observe_path` matches on path and content hash and returns the same
    `file_id` -- so the run's own work is not skipped and not repeated. Measured
    against a plain run of the same corpus: `files`, `text_units`, `evidence`,
    `extraction_runs` and `file_facts` identical. What differs is a second
    `scan_runs` row and its cache verdicts, which are records OF this scan and not
    changes to the run's.
    """
    _src_on_path()
    import cli
    from scan_agent.corpus_source import FilesystemCorpusSource
    from scan_agent.scan import scan
    from scan_agent.selection import record_selection

    cli._bootstrap(conn)
    selection_id = record_selection(
        conn, sources=[corpus.expanduser().resolve()], candidate_roots=[],
        cross_folder_moves=False, selected_by=SCOREBOARD_USER)
    scan(conn, selection_id, source=FilesystemCorpusSource(),
         mime_type_for=cli._mime_type_for, scan_state=cli.P1_INCLUDED_SCAN_STATE,
         budget_exhausted=lambda: False)


def _file_versions(rows) -> dict:
    """`(current_path, content_hash) -> file_id`, which is a file VERSION.

    The pair and not the hash alone, and the difference decides a correctness
    question rather than a lookup one. `00`:44 promises a rename costs nothing,
    and matching on the hash would keep that promise -- but the dossier carries
    `filename_citation`, and `work_type` is a field the filename can settle, so a
    renamed file's prior answer may rest on a name it no longer has. Matching on
    the pair re-asks that file. Conservative in the direction that spends money
    rather than the one that files a person's work under a stale answer.

    The pair is unique: `observe_path` keeps two live copies of identical bytes as
    two rows (I1), each under its own path.
    """
    return {(row["current_path"], row["content_hash"]): row["file_id"]
            for row in rows}


def seed(fresh: Path, prior: Path, *, corpus: Path) -> Seeded:
    """Create `fresh`, scan the corpus into it, and translate the prior's answers.

    The database is created HERE rather than by the run, because "before the run
    starts" is the only moment at which seeding leaves the run itself untouched:
    the product's `_bootstrap` re-runs every `CREATE TABLE IF NOT EXISTS` over the
    file it is handed and writes exactly what it would have written into an empty
    one.

    The prior is attached and never written to. Columns are named from the FRESH
    database's `table_info` rather than with `SELECT *`, because `llm_verdict`
    carries `record_id` as a VIRTUAL generated column: `SELECT *` returns it and
    `table_info` does not, and an INSERT that offered it would be rejected.

    A prior answer whose file is not in this corpus at that path with those bytes
    is SKIPPED, and so is everything under its dossier: a dossier row naming a
    file id this database does not have would be a dangling reference of exactly
    the kind the rest of this module refuses to write.
    """
    _src_on_path()
    from database_agent.db import open_database
    from llm_harness.schema import create_llm_schema
    from llm_harness.store import call_identity

    conn = open_database(fresh)
    try:
        _scan_the_corpus(conn, corpus)
        create_llm_schema(conn)
        here = _file_versions(conn.execute(
            "SELECT current_path, content_hash, file_id FROM files"))
        conn.execute("ATTACH DATABASE ? AS prior", (str(prior),))
        rows: dict[str, int] = {}
        try:
            there = {row["file_id"]: (row["current_path"], row["content_hash"])
                     for row in conn.execute(
                         "SELECT current_path, content_hash, file_id "
                         "FROM prior.files")}
            conn.execute("BEGIN IMMEDIATE")
            # The identity is rewritten and not copied, and the digest is
            # recomputed by the PRODUCT's own `call_identity` over the rewritten
            # mapping. Never by editing the stored digest: the row carries the
            # mapping the digest was taken over precisely so the two can be
            # checked against each other, and a hand-made digest would be the one
            # thing that reads back as sound and is not.
            # `translated` maps a DOSSIER to the file id this database gives it,
            # and `digests` counts the QUESTIONS. They are not the same number and
            # a run says why: two identities reach one dossier when the same file
            # is asked of two different models, because `model_id` is a dimension
            # of the identity and is not in the bytes the dossier addresses. That
            # is the rerun-with-a-different-model case this flag exists for, so
            # counting dossiers as answers would under-report exactly it.
            translated: dict[str, str] = {}
            digests: set[str] = set()
            written: set[tuple[str, str]] = set()
            skipped = 0
            for row in conn.execute(
                    "SELECT identity_id, dossier_id, call_site, subject_ref, "
                    "dimensions, observed_at FROM prior.llm_call_identity"
                    ).fetchall():
                version = there.get(row["subject_ref"])
                mine = here.get(version) if version is not None else None
                if mine is None:
                    skipped += 1
                    continue
                # A row whose mapping this checkout cannot take a digest over is
                # SKIPPED and never fatal. The schema check upstream compares
                # tables, not row contents, so a database written by a checkout
                # whose dimension set differed reaches here -- and the cost of
                # skipping is that the file is asked again, which is the only
                # direction a reuse may ever fail in.
                try:
                    dimensions = json.loads(row["dimensions"])
                    dimensions["subject_ref"] = mine
                    digest = call_identity(dimensions)
                except Exception:
                    skipped += 1
                    continue
                # `(identity, dossier)` is the primary key, and two prior rows
                # CAN land on one pair here: their prior file ids differ and both
                # resolve to the same file version of this corpus. Skipped rather
                # than inserted twice, because the second insert would abort the
                # whole seeding over two rows that say the same thing.
                if (digest, row["dossier_id"]) in written:
                    skipped += 1
                    continue
                conn.execute(
                    "INSERT INTO main.llm_call_identity (identity_id, dossier_id, "
                    "call_site, subject_ref, dimensions, observed_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (digest, row["dossier_id"], row["call_site"], mine,
                     _canonical(dimensions), row["observed_at"]))
                written.add((digest, row["dossier_id"]))
                translated[row["dossier_id"]] = mine
                digests.add(digest)
            rows["llm_call_identity"] = len(written)

            # The dossier's own `subject_ref` is translated for the same reason
            # the identity's is, and `measure.py` is the reason it matters:
            # `_blocked_tally` counts a file with no dossier row as one that
            # reached no model, so a seeded dossier still naming the prior run's
            # file id would report every reused file as never built.
            rows["llm_dossier"] = 0
            for row in conn.execute(
                    "SELECT dossier_id, call_site, eligibility_reason, "
                    "plan_version, policy_version, reduction_rung, payload, "
                    "observed_at FROM prior.llm_dossier").fetchall():
                if row["dossier_id"] not in translated:
                    continue
                conn.execute(
                    "INSERT INTO main.llm_dossier (dossier_id, call_site, "
                    "subject_ref, eligibility_reason, plan_version, "
                    "policy_version, reduction_rung, payload, observed_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (row["dossier_id"], row["call_site"],
                     translated[row["dossier_id"]], row["eligibility_reason"],
                     row["plan_version"], row["policy_version"],
                     row["reduction_rung"], row["payload"], row["observed_at"]))
                rows["llm_dossier"] += 1

            for table, where in SEED_PLAN:
                columns = [column["name"] for column in
                           conn.execute(f"PRAGMA main.table_info({table})")]
                named = ", ".join(columns)
                cursor = conn.execute(
                    f"INSERT INTO main.{table} ({named}) "
                    f"SELECT {named} FROM prior.{table} {where}")
                rows[table] = cursor.rowcount
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
        finally:
            conn.execute("DETACH DATABASE prior")
        return Seeded(answers=len(digests), rows=rows, skipped=skipped,
                      responses=rows.get("llm_response", 0))
    finally:
        conn.close()


def spend(database: Path, seeded: Seeded) -> tuple[int, int]:
    """What the run did with what it was given: (questions reused, calls made).

    `llm_call_reuse` is written only by `model_facts.fact_call_stage`, one row per
    question not asked, so it is this run's own number and no seeded row can be
    mistaken for one -- reuse rows are never copied.

    Calls are responses plus call failures, because both were sent and both were
    paid for, minus the responses this run was HANDED. A failure is never seeded,
    so it needs no subtraction.
    """
    conn = sqlite3.connect(database)
    try:
        def count(table: str) -> int:
            return conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]

        reused = count("llm_call_reuse")
        made = count("llm_response") + count("llm_call_failure") - seeded.responses
    finally:
        conn.close()
    return reused, made
