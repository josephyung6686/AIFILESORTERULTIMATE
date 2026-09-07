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

import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

_ROOT = Path(__file__).resolve().parents[2]


class ReuseRefused(Exception):
    """The prior directory cannot be seeded from, and nothing has been run yet.

    Every one of these is raised BEFORE the first run starts. `run.py` deletes each
    situation's database at the top of its own run, so a refusal discovered inside a
    run would arrive after the thing it was protecting had already been destroyed.
    """


#: Which rows of each table a reuse can be decided from, in insert order. The filter
#: is written against the ATTACHED prior, never against `main`: `main` is empty when
#: this runs and a filter that read it would silently copy nothing.
_DOSSIERS = "(SELECT dossier_id FROM prior.llm_call_identity)"
_COPIED_VERDICTS = (
    f"(SELECT verdict_id FROM prior.llm_verdict WHERE dossier_id IN {_DOSSIERS})"
)
SEED_PLAN: tuple[tuple[str, str], ...] = (
    ("llm_call_identity", ""),
    ("llm_dossier", f"WHERE dossier_id IN {_DOSSIERS}"),
    ("llm_response", f"WHERE dossier_id IN {_DOSSIERS}"),
    ("llm_verdict", f"WHERE dossier_id IN {_DOSSIERS}"),
    ("llm_verdict_supersession",
     f"WHERE old_verdict_id IN {_COPIED_VERDICTS} "
     f"AND new_verdict_id IN {_COPIED_VERDICTS}"),
)


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


def seed(fresh: Path, prior: Path) -> Seeded:
    """Create `fresh` and give it the rows a reuse can be decided from.

    The database is created HERE rather than by the run, because "before the run
    starts" is the only moment at which seeding leaves the run itself untouched:
    the product's `_bootstrap` re-runs every `CREATE TABLE IF NOT EXISTS` over the
    file it is handed and writes exactly what it would have written into an empty
    one.

    The prior is attached and never written to. Columns are named from the FRESH
    database's `table_info` rather than with `SELECT *`, because `llm_verdict`
    carries `record_id` as a VIRTUAL generated column: `SELECT *` returns it and
    `table_info` does not, and an INSERT that offered it would be rejected.
    """
    _src_on_path()
    from database_agent.db import open_database
    from llm_harness.schema import create_llm_schema

    conn = open_database(fresh)
    try:
        create_llm_schema(conn)
        conn.execute("ATTACH DATABASE ? AS prior", (str(prior),))
        rows: dict[str, int] = {}
        try:
            conn.execute("BEGIN IMMEDIATE")
            for table, where in SEED_PLAN:
                columns = [row["name"] for row in
                           conn.execute(f"PRAGMA main.table_info({table})")]
                named = ", ".join(columns)
                cursor = conn.execute(
                    f"INSERT INTO main.{table} ({named}) "
                    f"SELECT {named} FROM prior.{table} {where}"
                )
                rows[table] = cursor.rowcount
            answers = conn.execute(
                "SELECT count(DISTINCT identity_id) AS n FROM main.llm_call_identity"
            ).fetchone()["n"]
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
        finally:
            conn.execute("DETACH DATABASE prior")
        return Seeded(answers=answers, rows=rows,
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
