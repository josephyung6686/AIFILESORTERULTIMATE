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
two things before the run starts: the corpus as the product's own P3 scan records
it, and the rows a reuse can be DECIDED from.

The scan is not a convenience. R-109's key carries `subject_ref`, which is the
`file_id`, and `files_table.py:286` mints that as `str(uuid.uuid4())` the first time
a path is seen -- so it names a file within ONE database and nothing across two, and
a verbatim copy of a prior run's identities sits under a digest this run will never
compute. Measured before the scan was added: 2 calls, seed, 2 calls again,
`llm_call_reuse` empty, with `subject_ref` the only one of nine dimensions that
moved. Scanning first is what lets the prior's answers be re-keyed to the ids THIS
database will use. `_scan_the_corpus` says what it costs and what it does not.

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

import hashlib
import json
import os
import sqlite3
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

# The runner's own reading of the semantic setting, imported rather than
# respelled: the note beside the databases must say what the runs were GIVEN, and
# a second `os.environ` lookup here would be a second answer to that question the
# day the two disagree. `_one_run` imports this module only from inside `main`,
# so this direction of the dependency costs nothing at import time.
from tools.groundtruth._one_run import semantic_weights

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
    #: Prior answers LEFT BEHIND: this corpus has no file at that path with those
    #: bytes (changed, moved, renamed or deleted), or the row's dimensions are not
    #: a mapping this checkout can take a digest over, or two prior rows resolved
    #: to one question here. Reported rather than swallowed: it is the difference
    #: between "the prior directory had nothing for this corpus" and "the corpus
    #: moved on", and a person choosing whether to trust a cheap rerun needs to
    #: know which. Every one of them costs a question asked again, and nothing else.
    skipped: int = 0
    #: OLD ADDRESS -> NEW, one entry per seeded dossier. `104` R-137 moves the
    #: address because the bytes it is taken over now name this run's file, and a
    #: content address that changed silently is a record nobody can check. This is
    #: where the prior's own address is kept, so a seeded row can still be found in
    #: the database it came from.
    addresses: Mapping[str, str] = field(default_factory=dict)
    #: Seeded dossiers whose address could NOT be recomputed and so kept the
    #: prior's: not an A_fact dossier, no stored response to name a release, or a
    #: payload that is not a dossier. Each one costs a question asked again the
    #: first time the validator moves, which is what it cost before R-137.
    untranslated: int = 0
    #: WHY each left-behind answer was left, counted per reason. `104` R-141: a
    #: bare `skipped` cannot be diagnosed, and it covers five different faults --
    #: the prior did not know the subject, this corpus does not hold those bytes,
    #: the path moved, the dimensions would not digest, or two prior answers
    #: reached one question here.
    skipped_reasons: Mapping[str, int] = field(default_factory=dict)
    #: Dimensions this checkout digests that a prior identity did not carry, filled
    #: with their empty value and counted per row. `104` R-141: this is a key that
    #: changed shape, which is the thing a reuse must never do in silence.
    defaulted_dimensions: Mapping[str, int] = field(default_factory=dict)
    #: Dimensions a prior identity carried that this checkout no longer digests.
    dropped_dimensions: Mapping[str, int] = field(default_factory=dict)


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


def _wire_handle_key_name() -> str:
    """`cli`'s own name for the key file. Spelled there, read here, never re-typed.

    Lazily, like every other `src` import in this module: naming it at import time
    would put the whole CLI behind `import reuse`.
    """
    _src_on_path()
    from cli import WIRE_HANDLE_KEY_FILENAME
    return WIRE_HANDLE_KEY_FILENAME


def wire_handle_key_file(directory: Path) -> Path:
    """The local-only key beside a directory of run databases.

    `cli.wire_handle_key_for` puts it next to the database and mints it "once per
    database", so a directory holding one run's situations holds one key.
    """
    return directory / _wire_handle_key_name()


def carry_the_wire_handle_key(prior_dir: Path, fresh_dir: Path) -> None:
    """Give the fresh run the key the seeded answers were written under. `104` R-127.

    **Without this the seeding stops working the day a validator changes**, and it
    fails by spending rather than by saying anything. The seeded `llm_dossier` and
    `llm_response` rows carry wire HANDLES, and a handle is a digest under a key
    `cli.wire_handle_key_for` mints per database directory. `Dossier.dossier_id` is
    the content address of the bytes those handles sit in, so a fresh directory
    with a fresh key cannot reach the address its own seeded rows are filed under.
    `model_facts._reuse_is_current` checks exactly that before it re-judges a
    stored response, and refuses -- correctly, because judging bytes whose handles
    resolve to nothing would reject every citation in them and then reuse THAT. The
    honest consequence of the refusal is a question, and a question is a model
    call: R-123's measured 0 calls would quietly become every call, billed.

    **Copied and not regenerated.** The key is the one thing about a prior run that
    is not in its database and is derivable from nothing that is -- it is
    `secrets.token_bytes`. `cli` says what rotation costs, "exactly that
    recognition and nothing else", and seeding is the case that would pay it.

    Nothing is overwritten. A key already beside the fresh databases and equal to
    the prior's is this function having run for an earlier situation of the same
    run; one that DIFFERS is a directory that has already minted or inherited some
    other run's key, and the rows about to be seeded would be unreadable under it.
    That is a refusal, not something to settle by choosing one of the two.
    """
    source = wire_handle_key_file(prior_dir)
    if not source.exists():
        raise ReuseRefused(
            f"--reuse-answers-from {prior_dir}: no {_wire_handle_key_name()} "
            f"beside its databases. The seeded answers name their evidence "
            f"through handles keyed by that file, so without it this run cannot "
            f"read the bytes it was handed and would ask every question again. "
            f"Nothing has been run."
        )
    key = source.read_bytes()
    destination = wire_handle_key_file(fresh_dir)
    if destination.exists():
        if destination.read_bytes() == key:
            return
        raise ReuseRefused(
            f"--out {fresh_dir} already holds a different "
            f"{_wire_handle_key_name()}. The answers about to be seeded were "
            f"written under {prior_dir}'s key and cannot be read under this one, "
            f"and choosing between two keys is not this tool's to do. Write this "
            f"run to an empty --out. Nothing has been run."
        )
    _src_on_path()
    from cli import WIRE_HANDLE_KEY_MODE

    fresh_dir.mkdir(parents=True, exist_ok=True)
    # `O_EXCL` and the mode `cli` mints under. A credential copied into a
    # world-readable file is a credential this tool leaked, and two situations
    # racing to copy the first one cannot each write it.
    handle = os.open(
        destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, WIRE_HANDLE_KEY_MODE)
    with os.fdopen(handle, "wb") as sink:
        sink.write(key)


#: What a run of the scoreboard records about the checkout that produced it. The
#: product's own database holds no commit -- `cli.COMPONENT_VERSION` is a hand-
#: written string and `run_manifest` belongs to P2's eval harness -- so a directory
#: of databases cannot say what code wrote it unless the scoreboard says so. Written
#: on every run that actually runs something, because the run that needs it is the
#: one AFTER it, and a note written only when `--reuse-answers-from` is passed would
#: never be there the first time anybody wanted one.
PROVENANCE = "checkout.json"


def provenance_note(out_dir: Path) -> Path:
    return out_dir / PROVENANCE


def _checkout() -> dict:
    """The commit these databases were produced by, and whether it was clean.

    `None` rather than a guess when git cannot answer -- a tarball, no git, a
    detached worktree that has lost its repository. A missing commit is a fact
    about the record and is reported as one; an invented one is not recoverable
    by anybody reading it later.
    """
    def git(*arguments: str) -> str | None:
        try:
            done = subprocess.run(("git", "-C", str(_ROOT), *arguments),
                                  capture_output=True, text=True, timeout=30)
        except (OSError, subprocess.SubprocessError):
            return None
        return done.stdout.strip() if done.returncode == 0 else None

    commit = git("rev-parse", "HEAD")
    changes = git("status", "--porcelain")
    name, digest = _prompt_library()
    return {
        "commit": commit,
        # A dirty checkout is the case where the commit alone is a lie, so it is
        # recorded beside it rather than left for somebody to assume.
        "dirty": None if changes is None else bool(changes),
        # `104` §12.12 and §12.7, and both are recorded HERE rather than read at
        # scoring time. `--score-only` re-reads these databases days later, out of
        # a checkout whose library may have moved and a shell whose environment
        # certainly has; a digest or a setting read then would describe the
        # SCORER and print a false line about the runs.
        "prompt_library": name,
        "prompt_library_sha256": digest,
        "semantic_model": semantic_weights(),
        "written_at": datetime.now(timezone.utc).isoformat(),
    }


def _prompt_library() -> tuple[str, str]:
    """The packet manifest this run asked its questions out of, and its digest.

    **WHICH PROMPT ROWS A SCORECARD MEASURED** (`104` §12.12). The manifest is the
    index of every draft and ratified row in the library -- it names the template,
    schema and policy files and carries the digests that verify them -- so one
    digest over its bytes says which set of questions a run was asking. Two
    scorecards that disagree are comparing different prompts unless this line
    matches, which is exactly the claim the corpus digest makes about the files.

    Taken over the manifest's OWN bytes rather than composed out of the digests
    inside it: a row added, retitled or repointed changes this, and a change to
    the text a row points at changes the row's digest and so these bytes too.

    `("", "")` when the library cannot be read at all, which is a fact about the
    record and is reported as one -- `_checkout`'s rule for a commit git cannot
    answer, applied to the same note.
    """
    _src_on_path()
    try:
        from llm_harness.prompt_library import DRAFTS_FILE
        raw = DRAFTS_FILE.read_bytes()
    except (ImportError, OSError):
        return "", ""
    return DRAFTS_FILE.name, hashlib.sha256(raw).hexdigest()


def write_provenance(out_dir: Path) -> None:
    provenance_note(out_dir).write_text(
        json.dumps(_checkout(), indent=2, sort_keys=True), encoding="utf-8")


def read_provenance(out_dir: Path) -> dict:
    note = provenance_note(out_dir)
    if not note.exists():
        return {}
    try:
        loaded = json.loads(note.read_text(encoding="utf-8"))
    except (TypeError, ValueError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def describe_source(directory: Path) -> str:
    """One line naming where answers came from, for the sidecar and the scorecard.

    Says "commit not recorded" rather than nothing when the prior directory
    predates this note or was written outside a checkout: a reader has to be able
    to tell "produced by an unknown commit" from "produced by no commit", and the
    two look identical if the sentence just goes quiet.
    """
    checkout = read_provenance(directory)
    commit = checkout.get("commit")
    if not commit:
        return f"{directory} (commit not recorded)"
    dirty = checkout.get("dirty")
    state = "" if dirty is False else (
        ", checkout was dirty" if dirty else ", cleanliness not recorded")
    return f"{directory} at {commit[:12]}{state}"


def seeded_note(out_dir: Path, situation: str) -> Path:
    """Where a run records what it was handed, beside the database it was handed to.

    A file rather than a column: every `llm_*` table is append-only by trigger, and
    a "this row was seeded" column would be a change to the PRODUCT's schema made
    for the scoreboard's convenience. `--score-only` re-reads these databases long
    after the run, and without this it would report seeded rows as calls somebody
    paid for.
    """
    return out_dir / f"{situation.replace('.', '_')}.seeded.json"


def write_seeded(out_dir: Path, situation: str, given: "Seeded", *,
                 source: Path) -> None:
    """What this run was handed, and WHERE FROM, beside the database it went into.

    The source is recorded and not just the counts, because the counts alone
    cannot be checked by anybody: a person reading "verdict=5" months later has to
    be able to go and look at the five.
    """
    seeded_note(out_dir, situation).write_text(
        json.dumps({"answers": given.answers, "skipped": given.skipped,
                    "rows": dict(given.rows),
                    "from": str(source),
                    "from_database": str(prior_database(source, situation)),
                    "source": describe_source(source),
                    # `104` R-137. A seeded dossier is filed under an address this
                    # run recomputed, and the address it had in the prior run is
                    # how anybody checks it against the database it came from. The
                    # old address is never overwritten in silence; it is written
                    # down here.
                    "addresses": dict(given.addresses),
                    "skipped_reasons": dict(given.skipped_reasons),
                    "defaulted_dimensions": dict(given.defaulted_dimensions),
                    "dropped_dimensions": dict(given.dropped_dimensions),
                    "untranslated": given.untranslated,
                    "prior_checkout": read_provenance(source)},
                   indent=2, sort_keys=True),
        encoding="utf-8")


def read_seeded(out_dir: Path, situation: str) -> tuple[dict[str, int], str]:
    """Rows seeded into this situation's database and where from, or `({}, "")`.

    Unreadable is treated as none, and deliberately: this decides how a number is
    LABELLED, and a scoreboard that refused to print because a note beside it was
    malformed would withhold the measurement to protect its footnote.
    """
    note = seeded_note(out_dir, situation)
    if not note.exists():
        return {}, ""
    try:
        loaded = json.loads(note.read_text(encoding="utf-8"))
        rows = {str(k): int(v) for k, v in loaded.get("rows", {}).items()}
    except (AttributeError, TypeError, ValueError):
        return {}, ""
    return rows, str(loaded.get("source", ""))


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
    # `104` R-127, and it belongs in this function rather than in `seed` for this
    # function's own stated reason: a key discovered missing inside a run arrives
    # after the databases it was protecting have been deleted. `seed` copies it;
    # this says, before anything is destroyed, whether there is one to copy.
    if not wire_handle_key_file(directory).exists():
        raise ReuseRefused(
            f"--reuse-answers-from {directory}: no {_wire_handle_key_name()} "
            f"beside its databases. The answers there name their evidence through "
            f"handles keyed by that file, so this run could not read the bytes it "
            f"was handed and would ask every question again -- which is the whole "
            f"cost this flag exists to avoid. Nothing has been run."
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
                columns = {row[1] for row in conn.execute(
                    "PRAGMA table_info(files)")}
            finally:
                conn.close()
        except sqlite3.Error as error:
            raise ReuseRefused(
                f"--reuse-answers-from {path}: SQLite cannot read it ({error}). "
                f"Nothing has been run."
            ) from error
        # The `llm_*` comparison above says nothing about `files`, and the
        # translation cannot happen without it: these three columns are the whole
        # of what turns a prior run's file id into this run's. Checked HERE with
        # everything else, because the alternative is an `OperationalError` out of
        # a worker thread after that situation's database has been deleted.
        wanted = {"file_id", "current_path", "content_hash"}
        if not wanted <= columns:
            raise ReuseRefused(
                f"--reuse-answers-from {path}: its `files` table has no "
                f"{', '.join(sorted(wanted - columns))}, so a prior answer cannot "
                f"be matched to a file of this corpus. Nothing has been run."
            )
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


def _re_address(row, mine: str, *, release_id, key: bytes, prompt) -> tuple[str, str]:
    """One prior dossier, re-addressed for the file id THIS database gives it.

    `104` R-137. The seeder already translates `llm_dossier.subject_ref`, the
    column; the PAYLOAD kept the prior run's file id, and `dossier_id` is the
    content address of bytes that carry `subject_ref` as a wire handle. So a
    seeded dossier named a file this database does not have, and R-127's
    re-judgement refused it -- `validate_fact_proposal` will not judge a dossier
    and a request that name different files, and it is right not to. Every rerun
    across a validator change therefore paid for every answer again, which is the
    measured cost this closes.

    The address is RECOMPUTED by the product's own `dossier_address` over the
    rewritten record, exactly as the identity's digest is recomputed by
    `call_identity` over the rewritten mapping, and for the same reason: a
    hand-edited address is the one thing that reads back as sound and is not.

    Returns the address unchanged when the row cannot be rebuilt into a `Dossier`
    -- a payload that is not one, a dossier no response was ever stored for, a
    call site whose address this function has no prompt for. Unchanged is what
    the seeder did for every row before this existed, so such a row costs a
    question asked again and nothing else; the count is reported rather than
    swallowed.
    """
    _src_on_path()
    from llm_harness.dossier import dossier_address, dossier_from_stored_body
    from llm_harness.vocabulary import A_FACT

    if row["call_site"] != A_FACT or not release_id:
        return row["dossier_id"], row["payload"]
    try:
        body = json.loads(row["payload"])
        body["subject_ref"] = mine
        dossier = dossier_from_stored_body(body, release_id=release_id)
        address = dossier_address(dossier, prompt, handle_key=key)
    except Exception:
        return row["dossier_id"], row["payload"]
    body["dossier_id"] = address
    return address, _canonical(body)


def _copy_responses(conn: sqlite3.Connection, addresses: Mapping[str, str]) -> int:
    """The stored bytes, under this run's address for the dossier they answer.

    `response_bytes` are the model's own and carry no address: what the model
    said about a file does not change because this database calls that file
    something else.
    """
    columns = [column["name"] for column in
               conn.execute("PRAGMA main.table_info(llm_response)")]
    named = ", ".join(columns)
    marks = ", ".join("?" for _ in columns)
    copied = 0
    for row in conn.execute(
            f"SELECT {named} FROM prior.llm_response").fetchall():
        address = addresses.get(row["dossier_id"])
        if address is None:
            continue
        values = [address if name == "dossier_id" else row[name]
                  for name in columns]
        conn.execute(
            f"INSERT INTO main.llm_response ({named}) VALUES ({marks})", values)
        copied += 1
    return copied


def _copy_verdicts(conn: sqlite3.Connection,
                   addresses: Mapping[str, str]) -> tuple[int, dict[str, str]]:
    """Every verdict, re-keyed onto the dossier's new address. `104` R-137.

    Site A's `verdict_id` BEGINS with the dossier it judged --
    `fact_validation._verdict` builds `dossier:field` and two suffixes are added
    after it -- so moving the dossier moves the verdict's own address with it. The
    prefix is replaced by slice rather than reassembled, because the two suffixes
    are P8's to compose and this is not the place to learn their shape.

    The payload is rewritten with it. `store._payload` is `_jsonable` of the
    record, so the two ids inside it must say what the columns say; a row whose
    payload names an address its own column does not is exactly the disagreement
    every content-addressed table here exists to prevent. A verdict whose id does
    not begin with its dossier is left where it is and counted, never guessed at.
    """
    columns = [column["name"] for column in
               conn.execute("PRAGMA main.table_info(llm_verdict)")]
    named = ", ".join(columns)
    marks = ", ".join("?" for _ in columns)
    moved: dict[str, str] = {}
    copied = 0
    for row in conn.execute(f"SELECT {named} FROM prior.llm_verdict").fetchall():
        address = addresses.get(row["dossier_id"])
        if address is None:
            continue
        verdict_id = row["verdict_id"]
        if verdict_id.startswith(row["dossier_id"]):
            verdict_id = address + verdict_id[len(row["dossier_id"]):]
        payload = row["payload"]
        try:
            body = json.loads(payload)
            if isinstance(body, dict) and "dossier_id" in body:
                body["dossier_id"] = address
                body["verdict_id"] = verdict_id
                payload = _canonical(body)
        except Exception:
            pass
        values = []
        for name in columns:
            if name == "dossier_id":
                values.append(address)
            elif name == "verdict_id":
                values.append(verdict_id)
            elif name == "payload":
                values.append(payload)
            else:
                values.append(row[name])
        conn.execute(
            f"INSERT INTO main.llm_verdict ({named}) VALUES ({marks})", values)
        moved[row["verdict_id"]] = verdict_id
        copied += 1
    return copied, moved


def _copy_supersessions(conn: sqlite3.Connection,
                        verdict_ids: Mapping[str, str]) -> int:
    """Only when BOTH endpoints travelled, so a supersession can never dangle."""
    columns = [column["name"] for column in
               conn.execute("PRAGMA main.table_info(llm_verdict_supersession)")]
    named = ", ".join(columns)
    marks = ", ".join("?" for _ in columns)
    copied = 0
    for row in conn.execute(
            f"SELECT {named} FROM prior.llm_verdict_supersession").fetchall():
        old_id = verdict_ids.get(row["old_verdict_id"])
        new_id = verdict_ids.get(row["new_verdict_id"])
        if old_id is None or new_id is None:
            continue
        values = []
        for name in columns:
            if name == "old_verdict_id":
                values.append(old_id)
            elif name == "new_verdict_id":
                values.append(new_id)
            else:
                values.append(row[name])
        conn.execute(
            f"INSERT INTO main.llm_verdict_supersession ({named}) "
            f"VALUES ({marks})", values)
        copied += 1
    return copied


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
    from llm_harness.store import (
        DimensionWithoutAnEmptyValue, call_identity,
        under_these_dimensions,
    )

    # BEFORE the fresh database exists, because `cli.wire_handle_key_for` mints a
    # key the first time anything opens a database in that directory and refuses to
    # overwrite one. `104` R-127: the answers about to be seeded are addressed
    # under the prior's key, and a run that minted its own could not read them.
    carry_the_wire_handle_key(prior.parent, fresh.parent)
    # `104` R-137 re-addresses every A_fact dossier it seeds, and the address is
    # taken over the MODEL-VISIBLE bytes: the key the handles in them are digests
    # under, and the prompt whose response schema the address also covers. Both
    # are this checkout's. A prior row built under a different prompt carries a
    # different `prompt_fingerprint` and `schema_id` in its identity, so it is
    # never looked up and the mismatch is inert rather than wrong.
    from cli import a_fact_prompt

    key = wire_handle_key_file(fresh.parent).read_bytes()
    prompt = a_fact_prompt()
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
            pending_identities: list[tuple] = []
            digests: set[str] = set()
            written: set[tuple[str, str]] = set()
            skipped = 0
            reasons: dict[str, int] = {}
            defaulted: dict[str, int] = {}
            no_longer_digested: dict[str, int] = {}

            def leave_behind(reason: str) -> None:
                """One answer not seeded, and WHY. `104` R-141.

                A bare count cannot be diagnosed. The owner's r8 reported "238 not
                in this corpus" against a prior whose `files` table paired 199 of
                199 with this run's, and the number could not say whether the
                prior did not know the subject, this corpus does not hold the
                file, or the path had moved -- three different faults wearing one
                number, and no way to tell which without the databases in hand.
                """
                nonlocal skipped
                skipped += 1
                reasons[reason] = reasons.get(reason, 0) + 1

            for row in conn.execute(
                    "SELECT identity_id, dossier_id, call_site, subject_ref, "
                    "dimensions, observed_at FROM prior.llm_call_identity"
                    ).fetchall():
                version = there.get(row["subject_ref"])
                if version is None:
                    # The PRIOR's own `files` table does not know the subject this
                    # identity names. Nothing about this corpus is involved, and a
                    # message about this corpus would send a reader to the wrong
                    # database.
                    leave_behind("subject_not_in_the_prior")
                    continue
                mine = here.get(version)
                if mine is None:
                    # The pair is `(current_path, content_hash)`. Which HALF of it
                    # missed is the whole diagnosis: bytes this scan holds under
                    # another path is a rename or a re-spelled corpus root, and
                    # bytes it does not hold at all is a file that changed or went.
                    _path, content = version
                    leave_behind(
                        "path_moved_or_renamed"
                        if content in {key[1] for key in here}
                        else "not_in_this_corpus")
                    continue
                # A row whose mapping this checkout cannot take a digest over is
                # SKIPPED and never fatal. The schema check upstream compares
                # tables, not row contents, so a database written by a checkout
                # whose dimension set differed reaches here -- and the cost of
                # skipping is that the file is asked again, which is the only
                # direction a reuse may ever fail in.
                # A PRIOR KEY IS READ UNDER THIS CHECKOUT'S DIMENSIONS, NOT
                # REFUSED FOR NOT HAVING THEM. `104` R-141: r9 left all 238 of
                # r6's answers behind because r6 recorded nine dimensions and this
                # checkout digests ten, including the files the tenth is EMPTY for
                # -- whose digest under the new set is byte-identical to the one
                # they would compute today. `store.under_these_dimensions` fills a
                # missing dimension with the value a call with nothing to put
                # there carries and drops one this checkout no longer digests, so
                # the addition does exactly what it was added to do: the files it
                # is non-empty for are asked again, the rest reuse.
                try:
                    dimensions = json.loads(row["dimensions"])
                    dimensions["subject_ref"] = mine
                    dimensions, added, dropped = under_these_dimensions(dimensions)
                    digest = call_identity(dimensions)
                except DimensionWithoutAnEmptyValue as gap:
                    # The one case that stays a refusal, and it says which.
                    leave_behind(f"no_empty_value_for_{gap.name}")
                    continue
                except Exception:
                    leave_behind("dimensions_this_checkout_cannot_digest")
                    continue
                for name in added:
                    defaulted[name] = defaulted.get(name, 0) + 1
                for name in dropped:
                    no_longer_digested[name] = no_longer_digested.get(name, 0) + 1
                # `(identity, dossier)` is the primary key, and two prior rows
                # CAN land on one pair here: their prior file ids differ and both
                # resolve to the same file version of this corpus. Skipped rather
                # than inserted twice, because the second insert would abort the
                # whole seeding over two rows that say the same thing.
                if (digest, row["dossier_id"]) in written:
                    leave_behind("two_prior_answers_to_one_question")
                    continue
                # HELD, not written, until the dossier's new address is known.
                # `104` R-137 moves that address, and `(identity_id, dossier_id)`
                # is the primary key: a row written here would name the prior
                # run's dossier and no reuse would ever find the one this run has.
                pending_identities.append(
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
            addresses: dict[str, str] = {}
            untranslated = 0
            for row in conn.execute(
                    "SELECT dossier_id, call_site, eligibility_reason, "
                    "plan_version, policy_version, reduction_rung, payload, "
                    "observed_at FROM prior.llm_dossier").fetchall():
                if row["dossier_id"] not in translated:
                    continue
                mine = translated[row["dossier_id"]]
                release = conn.execute(
                    "SELECT release_id FROM prior.llm_response WHERE "
                    "dossier_id = ? LIMIT 1", (row["dossier_id"],)).fetchone()
                address, payload = _re_address(
                    row, mine, release_id=None if release is None
                    else release["release_id"], key=key, prompt=prompt)
                if address == row["dossier_id"]:
                    untranslated += 1
                addresses[row["dossier_id"]] = address
                conn.execute(
                    "INSERT INTO main.llm_dossier (dossier_id, call_site, "
                    "subject_ref, eligibility_reason, plan_version, "
                    "policy_version, reduction_rung, payload, observed_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (address, row["call_site"], mine, row["eligibility_reason"],
                     row["plan_version"], row["policy_version"],
                     row["reduction_rung"], payload, row["observed_at"]))
                rows["llm_dossier"] += 1

            for identity in pending_identities:
                digest, old_dossier, call_site, mine, dimensions, observed = identity
                if old_dossier not in addresses:
                    continue
                conn.execute(
                    "INSERT INTO main.llm_call_identity (identity_id, dossier_id, "
                    "call_site, subject_ref, dimensions, observed_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (digest, addresses[old_dossier], call_site, mine,
                     dimensions, observed))
            rows["llm_call_identity"] = min(
                rows["llm_call_identity"],
                conn.execute("SELECT count(*) FROM main.llm_call_identity"
                             ).fetchone()[0])

            rows["llm_response"] = _copy_responses(conn, addresses)
            rows["llm_verdict"], verdict_ids = _copy_verdicts(conn, addresses)
            rows["llm_verdict_supersession"] = _copy_supersessions(
                conn, verdict_ids)
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
        finally:
            conn.execute("DETACH DATABASE prior")
        return Seeded(answers=len(digests), rows=rows, skipped=skipped,
                      responses=rows.get("llm_response", 0),
                      addresses=addresses, untranslated=untranslated,
                      skipped_reasons=reasons, defaulted_dimensions=defaulted,
                      dropped_dimensions=no_longer_digested)
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
