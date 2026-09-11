"""One file's trail, read from the plan database and from nothing else.

`104` §18.27 gap 25 (owner, 10 Sep): *"the person can open any file's trail --
extracted → sent → answered → judged → classified → placed -- from the product
itself; `00`'s 'a person can see why' has no surface today."* The owner could not
see what the product does: the CLI printed counts and review questions, the
scorer printed scores, and nothing anywhere printed, for ONE file, what was
extracted, what the model was sent, what it answered, or why the validator
refused it.

**Nothing here opens a file and nothing here builds a model target.** Every
sentence below comes off a row this run already wrote. That is the difference
between a trail and a re-run: a trail of a file that has since been deleted,
edited or moved must still print, because what it describes is what the product
DID, not what the file says now. So no path is stat'd, resolved or opened --
`Path.resolve` alone would readlink -- and the resolver matches the recorded
`current_path` as the string it is.

**The dossier and the answer print exactly as they are.** They are the person's
own data on the person's own screen, and a trail that summarised them would be
the same black box one layer further in (`00`:284: never "require the user to
trust a black box when the evidence, decision history, and correction path can
be shown directly"). What is redacted stays redacted, because what is stored IS
the released form -- P7 reduced the dossier before it was recorded, so the wire
handles a reader sees here are the handles the model saw. This module removes
nothing and restores nothing.

**Every stage prints, including the empty ones.** `00`:259 is the standing rule:
the interface "should show the difference between completed work and deferred
work", so a person is not left with "the false impression that an unprocessed
file was understood and found unimportant". A stage that has no rows says so and
says what the absence means, because a heading followed by nothing reads as a
product that forgot rather than one that never ran.

**A reason that is not in the database is not printed.** Where the four
model-call sources are all empty the sentence says exactly that: the database
records no reason. `104` §17.2 is what a number with no provenance costs, and a
made-up reason on a trail is that cost paid where a person is least able to
check it.

**SITE G'S NO-ROUTE FILE NOW HAS ONE (`104` §18.33 gap 25).** This paragraph used
to end "so this module cannot say 'no site had a model to ask' about a particular
file without inventing it", and that was true of a counter that existed only in
memory. `cli.ask_the_situation` writes one `llm_pre_call_abstention` row per file
it could route nowhere, so the reason is a row and the ASKED stage prints it
beside every other call that did not happen. What still has no row is site E's own
`no_route` count, and this module still invents nothing for it.
"""
from __future__ import annotations

import json
import sqlite3
import textwrap
from dataclasses import dataclass

#: Every stage prints a heading even when it has nothing under it, so the five
#: are named once here rather than spelled at each printer.
EXTRACTED: str = "EXTRACTED"
CLASSIFIED: str = "CLASSIFIED"
ASKED: str = "ASKED"
JUDGED: str = "JUDGED"
PLACED: str = "PLACED"

STAGES: tuple[str, ...] = (EXTRACTED, CLASSIFIED, ASKED, JUDGED, PLACED)

#: The prefix `placement.store.subject_ref_of` composes a file's address under:
#: `file:{file_id}:{content_hash}`. Spelled here rather than imported so that
#: reading a trail does not import the placement pipeline.
_FILE_SUBJECT_PREFIX: str = "file:"

#: The event `llm_harness.store.record_call_refusal` appends when a call was
#: refused before any dossier existed -- the over-the-ceiling skip at site G and
#: every builder raise. It writes NO row: `llm_call_failure` would need the
#: release it never spent and `llm_pre_call_abstention` would need a reason code
#: that does not mean this, so the event is the whole record and this is the only
#: place a person can read it back.
_CALL_REFUSED: str = "call_refused"


@dataclass(frozen=True)
class Trail:
    """The lines of one file's trail, and whether one file was found at all.

    Two fields because the caller needs both and must not derive either. The
    `found` flag is what an exit code is made of, and a caller inferring it from
    the text would be parsing this module's sentences -- which is how a wording
    change becomes an exit-code change.
    """

    lines: tuple[str, ...]
    found: bool


def _wrapped(text: str, *, indent: str, width: int) -> str:
    """A sentence a person reads, wrapped where a person can read it.

    `break_on_hyphens=False` for `cli._wrapped`'s measured reason: `textwrap`
    splits on hyphens, so `--trail` printed as `--trail` broken in two is the
    product telling somebody to type something that is not typeable.

    **`width` IS PASSED IN, AND `104` §18.35 IS WHY.** It was `width=78` here, and
    78 is a number P13 has no authority to choose:
    `tests/p13/test_p13_no_invention.py::
    test_no_numeric_literal_beyond_zero_and_one_lives_in_the_package` is the
    package's own standing rule -- "every number is injected, and absent means
    refuse" -- and `presentation.py` states the same doctrine at its digest ("a
    truncation would be a number this package has no authority to choose"). It
    cannot be a constant anywhere in `src/review_surface/` either; that is the
    same literal one file across.

    It is also the wrong number to copy rather than share. This width exists to
    MATCH `cli._wrapped`, which is why the paragraph above cites it, and
    `tests/test_cli_trail.py` asserts the identity outright -- the lines this
    returns must appear verbatim in what `--trail` prints. Two spellings of one
    width is one edit away from that assertion being false for a reason nobody
    can see. So the surface that owns the screen owns the number, and hands it
    down: `cli.WRAP_WIDTH`, through `file_trail`.
    """
    return textwrap.fill(text, width=width, initial_indent=indent,
                         subsequent_indent=indent, break_on_hyphens=False,
                         break_long_words=False)


def _verbatim(raw: object, *, indent: str) -> list[str]:
    """Stored bytes, as they are, indented and never truncated.

    NOT through `_wrapped`, and that is the whole of this function. `textwrap`
    collapses whitespace, so a dossier through it is JSON a person cannot read
    and cannot check a citation against. Pretty-printed where it parses, handed
    back as its own decoded text where it does not -- because a payload that is
    not JSON is still what was sent, and printing nothing for it would hide the
    one case where a reader most needs to see the bytes.
    """
    if isinstance(raw, (bytes, bytearray, memoryview)):
        text = bytes(raw).decode("utf-8", "replace")
    else:
        text = "" if raw is None else str(raw)
    try:
        text = json.dumps(json.loads(text), indent=1, ensure_ascii=False)
    except (ValueError, TypeError):
        pass
    return [f"{indent}{line}" for line in text.splitlines()] or [""]


def _payload(raw: object) -> dict:
    """A stored JSON payload as a mapping, or an empty one when it is not."""
    try:
        body = json.loads(raw if isinstance(raw, str) else bytes(raw).decode())
    except (ValueError, TypeError):
        return {}
    return body if isinstance(body, dict) else {}


def _rows(conn: sqlite3.Connection, query: str, *args) -> list[sqlite3.Row]:
    """Rows by column NAME, whatever factory the caller's connection carries.

    Set on a cursor of our own rather than on the connection: this module is
    handed a connection it does not own, and a reader that changed how every
    other caller's rows come back would be a surface with a side effect.
    """
    cursor = conn.cursor()
    cursor.row_factory = sqlite3.Row
    return cursor.execute(query, args).fetchall()


def files_named(conn: sqlite3.Connection, wanted: str) -> list[sqlite3.Row]:
    """Every `files` row a person's one word names: an id, a path, or a name.

    **Three tries in this order, and the first that matches wins.** A file id is
    a primary key and cannot collide with anything; a recorded `current_path` is
    what a plan prints for a file it has moved; a filename is what a person
    actually reads off their own screen and retypes. Trying the id first means a
    person who pastes an id never has it read as a path.

    **NOTHING IS TOUCHED ON DISK, and the string is not normalised.** No
    `expanduser`, no `resolve`, no `is_file`: those read the filesystem, and a
    trail must print for a file that has since been deleted. The comparison is
    against the path this run RECORDED, which is the path it printed.

    More than one row is returned rather than picked between. A path is not
    unique in `files` -- a superseded version keeps its path while the new one
    records the same -- so two rows is a real answer and the caller refuses.
    """
    for column in ("file_id", "current_path", "filename"):
        found = _rows(conn, f"SELECT * FROM files WHERE {column} = ? "
                            "ORDER BY rowid", wanted)
        if found:
            return found
    return []


def _subject_refs(row: sqlite3.Row) -> tuple[str, str]:
    """The two addresses a file is asked and decided about under.

    Site A, E and G write the bare `file_id` as `subject_ref`; site C and every
    `placement_decisions` row write `placement.store.subject_ref_of`'s
    `file:{file_id}:{content_hash}`, because §8.8 versions the plan and §8.2
    versions the file. A reader that knew only one of the two would print a
    trail that silently omits every placement call -- which is the shape of
    failure this whole surface exists to end.

    The LIKE takes any content hash and not only this row's: a decision made
    before the file was edited is still a decision about this file, and dropping
    it would make an edited file look like one nothing ever decided about.
    `file_id` is a uuid4, so it carries no `%` and no `_` to be read as a
    wildcard.
    """
    file_id = row["file_id"]
    return file_id, f"{_FILE_SUBJECT_PREFIX}{file_id}:%"


def _extracted(conn: sqlite3.Connection, row: sqlite3.Row, *,
               width: int) -> list[str]:
    """Which reader, how complete, how much coverage, how much text, what failed.

    `00`:259's completed-versus-deferred line, per file. `completeness` and
    `coverage` are the extractor's own words for how much of the file it got,
    and `failure_reason` is the difference between a file that had nothing to say
    and a file this product could not read -- which look identical from a count.
    """
    lines: list[str] = []
    runs = _rows(conn, "SELECT * FROM extraction_runs WHERE file_id = ? "
                       "ORDER BY started_at, run_id", row["file_id"])
    if not runs:
        return [_wrapped(
            "Nothing was extracted, because this plan database holds no "
            "extraction run for this file. Nothing was read out of it, so every "
            "stage below that would have used its text had none.", indent="  ", width=width)]
    for run in runs:
        units = conn.execute(
            "SELECT count(*) AS units, sum(length) AS chars FROM text_units "
            "WHERE run_id = ?", (run["run_id"],)).fetchone()
        count, chars = (units[0] or 0), (units[1] or 0)
        lines.append(_wrapped(
            f"{run['extractor_name']} {run['extractor_version']} read it as "
            f"{run['source_type']} at the {run['analysis_tier']} tier and got "
            f"{run['completeness']}, coverage "
            f"{run['coverage'] or 'not recorded'}: {run['observation_count']} "
            f"{'observation' if run['observation_count'] == 1 else 'observations'}"
            f", {count} {'text unit' if count == 1 else 'text units'}, "
            f"{chars} characters. Started {run['started_at']}, "
            f"finished {run['finished_at'] or 'never'}.", indent="  ", width=width))
        if run["failure_reason"]:
            lines.append(_wrapped(
                f"It failed: {run['failure_reason']}. What the stages below had "
                f"of this file is whatever this run got before it stopped.",
                indent="    ", width=width))
    # `files.extraction_status_by_tier` is where a DEFERRAL lives -- a tier this
    # run did not reach is not a tier that found nothing -- and it is a per-file
    # column rather than a per-run one, so it is stated once under the runs.
    by_tier = _payload(row["extraction_status_by_tier"])
    if by_tier:
        lines.append(_wrapped(
            "The tiers this run recorded for it: "
            + ", ".join(f"{tier} {status}"
                        for tier, status in sorted(by_tier.items()))
            + ".", indent="  ", width=width))
    return lines


def _classified(conn: sqlite3.Connection, row: sqlite3.Row, *,
                width: int) -> list[str]:
    """Every classification row in order, live or retired, and what retired it.

    §8.2's whole point, made readable: *"a user reviewing a placement should
    still be able to inspect the origin of the conclusion"* (`00`:137). A retired
    row is printed WITH the reason it was retired, because a superseded
    classification that vanishes from the screen is exactly the overwrite the
    supersede columns exist to prevent -- hidden one layer up instead of in the
    table.
    """
    rows = _rows(conn, "SELECT * FROM classifications WHERE file_id = ? "
                       "ORDER BY observed_at, fact_id", row["file_id"])
    if not rows:
        return [_wrapped(
            "Nothing classified this file, because no classification row names "
            "it. No detector reached it and no handling class was decided, so "
            "nothing here says whether it is protected.", indent="  ", width=width)]
    lines: list[str] = []
    for fact in rows:
        state = ("still stands" if fact["superseded_by"] is None
                 else f"retired by {fact['superseded_by']}")
        lines.append(_wrapped(
            f"{fact['handling_class']}, "
            f"{'protected' if fact['protected'] else 'not protected'}, privacy "
            f"class {fact['privacy_class'] or 'not recorded'}, on the basis of "
            f"{fact['basis']}, reliability {fact['reliability_state']}, "
            f"recorded {fact['observed_at']} as {fact['fact_id']} -- {state}.",
            indent="  ", width=width))
        if fact["supersede_reason"]:
            lines.append(_wrapped(
                f"It was retired because: {fact['supersede_reason']}. The row "
                f"itself is kept and is the one above.", indent="    ", width=width))
    return lines


def _one_call(conn: sqlite3.Connection, dossier: sqlite3.Row, *,
              width: int) -> list[str]:
    """One dossier: what was released, what came back, what it cost, what broke.

    **Every attempt, not the last one.** `store.record_dossier`'s own words are
    that "two calls over identical content are one dossier and two releases", so
    `llm_response`, `llm_call_usage` and `llm_call_failure` all hold several rows
    per dossier and each names the `release_id` that paid for it. A reader that
    kept one row per dossier would print a retry as though it were the only try.
    """
    usage = _rows(conn, "SELECT * FROM llm_call_usage WHERE dossier_id = ? "
                        "ORDER BY observed_at, usage_id", dossier["dossier_id"])
    answers = _rows(conn, "SELECT * FROM llm_response WHERE dossier_id = ? "
                          "ORDER BY observed_at, response_id",
                    dossier["dossier_id"])
    failures = _rows(conn, "SELECT * FROM llm_call_failure WHERE dossier_id = ? "
                           "ORDER BY observed_at, failure_id",
                     dossier["dossier_id"])
    refusals = _rows(conn, "SELECT * FROM llm_refusal WHERE dossier_id = ? "
                           "ORDER BY observed_at, refusal_id",
                     dossier["dossier_id"])
    model = next((answer["model_id"] for answer in answers),
                 next((spend["model_id"] for spend in usage
                       if spend["model_id"]), "no model that answered"))
    lines = [_wrapped(
        f"{dossier['call_site']} to {model}, eligible because "
        f"{dossier['eligibility_reason']}, reduced to rung "
        f"{dossier['reduction_rung']}, under policy {dossier['policy_version']}, "
        f"built {dossier['observed_at']} as {dossier['dossier_id']}.",
        indent="  ", width=width)]
    lines.append("    This is the dossier, exactly as it was released:")
    lines.extend(_verbatim(dossier["payload"], indent="      "))
    for answer in answers:
        lines.append(f"    This is what {answer['model_id']} answered, exactly "
                     f"as it came back:")
        lines.extend(_verbatim(answer["response_bytes"], indent="      "))
    if not answers and not failures and not refusals:
        lines.append(_wrapped(
            "Nothing came back and nothing recorded a failure: this plan "
            "database holds a dossier for this call and no answer to it.",
            indent="    ", width=width))
    for spend in usage:
        lines.append(_wrapped(
            f"It cost {spend['prompt_tokens']} prompt and "
            f"{spend['completion_tokens']} answer tokens by the provider's own "
            f"count, against the {spend['reserved_cost']} the budget had put "
            f"aside for it.", indent="    ", width=width))
    for failure in failures:
        lines.append(_wrapped(
            f"It failed: {failure['failure_class']}: {failure['explanation']}. "
            f"The release it spent was {failure['release_id']}.", indent="    ", width=width))
    for refusal in refusals:
        lines.append(_wrapped(
            "The privacy gate refused to release this dossier, so nothing was "
            "sent. What it refused:", indent="    ", width=width))
        lines.extend(_verbatim(refusal["payload"], indent="      "))
    return lines


def _asked(conn: sqlite3.Connection, row: sqlite3.Row, *,
           width: int) -> list[str]:
    """Every model call about this file, in the order the run made them.

    **Four sources, one order.** A dossier that was built, a question that was
    abstained from before a dossier existed, a call refused before anything was
    grounded, and a question not asked because a prior answer already covered it
    are four different things -- and to a person reading a trail they are one
    sequence, so they are sorted into one by the time each was written rather
    than printed in four blocks by table.

    **The refusal that has no row.** `record_call_refusal` writes an event and
    nothing else, on purpose: *"The two rows that exist would each have to lie."*
    That event is where the over-the-ceiling skip at site G lands (`104` R-175),
    so a file dropped for time is visible here as a file this run did not decide
    about, rather than as a file with nothing to say. It is picked out by
    `refusal_class`, which no other writer of this event puts in its explanation.
    """
    bare, prefixed = _subject_refs(row)
    entries: list[tuple[str, str, list[str]]] = []
    for dossier in _rows(
            conn, "SELECT * FROM llm_dossier WHERE subject_ref = ? OR "
                  "subject_ref LIKE ? ORDER BY observed_at, dossier_id",
            bare, prefixed):
        entries.append((dossier["observed_at"], dossier["dossier_id"],
                        _one_call(conn, dossier, width=width)))
    for held in _rows(
            conn, "SELECT * FROM llm_pre_call_abstention WHERE subject_ref = ? "
                  "OR subject_ref LIKE ? ORDER BY observed_at, abstention_id",
            bare, prefixed):
        entries.append((held["observed_at"], held["abstention_id"], [_wrapped(
            f"{held['call_site']} was not asked at all, because "
            f"{held['reason']}. Nothing was assembled and nothing was sent.",
            indent="  ", width=width)]))
    for reused in _rows(
            conn, "SELECT * FROM llm_call_reuse WHERE subject_ref = ? OR "
                  "subject_ref LIKE ? ORDER BY observed_at, reuse_id",
            bare, prefixed):
        entries.append((reused["observed_at"], reused["reuse_id"], [_wrapped(
            f"{reused['call_site']} was not asked again: the answer at dossier "
            f"{reused['prior_dossier_id']} already covered "
            f"{reused['reused_fields']}, under the same identity "
            f"{reused['identity_id']}.", indent="  ", width=width)]))
    for event in _rows(
            conn, "SELECT * FROM events WHERE event_type = ? "
                  "ORDER BY observed_at, event_id", _CALL_REFUSED):
        body = _payload(event["explanation"])
        if not body.get("refusal_class"):
            continue
        ref = body.get("subject_ref")
        if ref != bare and not str(ref).startswith(
                f"{_FILE_SUBJECT_PREFIX}{row['file_id']}:"):
            continue
        entries.append((event["observed_at"], str(event["event_id"]), [_wrapped(
            f"{body.get('call_site')} was refused before anything was sent: "
            f"{body['refusal_class']}. No dossier was recorded for it, so there "
            f"is nothing below to read.", indent="  ", width=width)]))
    if not entries:
        return [_wrapped(
            "No model was asked about this file. This plan database holds no "
            "dossier, no abstention, no refusal and no reuse that names it, and "
            "so it records no reason either -- a run that had no route to a "
            "model and a run that never reached this file leave exactly this.",
            indent="  ", width=width)]
    lines: list[str] = []
    # `(entry[0], entry[1])` rather than `entry[:2]`: the same two-element
    # key, spelled without the literal `2` `104` §18.35 removed from this
    # module. The pair is `(observed_at, id)` and naming both halves says
    # which two, where a slice width said how many.
    for _at, _id, block in sorted(
            entries, key=lambda entry: (entry[0], entry[1])):
        lines.extend(block)
    return lines


def _judged(conn: sqlite3.Connection, row: sqlite3.Row, *,
            width: int) -> list[str]:
    """Every verdict on this file's answers, with its reasons and review flag.

    The reasons are the validator's closed reason codes and are the answer to
    "why was this refused" -- the question `104` §18.27 says the product could
    not answer at all. `requires_review` is printed as its own sentence rather
    than a field, because it is the one thing on this line that asks something of
    the person reading it.
    """
    bare, prefixed = _subject_refs(row)
    rows = _rows(
        conn,
        "SELECT v.* FROM llm_verdict v JOIN llm_dossier d "
        "ON d.dossier_id = v.dossier_id "
        "WHERE d.subject_ref = ? OR d.subject_ref LIKE ? "
        "ORDER BY v.observed_at, v.verdict_id", bare, prefixed)
    if not rows:
        return [_wrapped(
            "Nothing judged this file, because no model answer about it reached "
            "the validator. No claim about it was accepted or refused on a "
            "model's word.", indent="  ", width=width)]
    lines: list[str] = []
    for verdict in rows:
        body = _payload(verdict["payload"])
        reasons = body.get("reasons") or ()
        state = ("still stands" if verdict["superseded_by"] is None
                 else f"retired by {verdict['superseded_by']}")
        lines.append(_wrapped(
            f"{verdict['claim_ref']}: {verdict['outcome']}, "
            f"{verdict['disposition']}, by validator "
            f"{verdict['validator_version']} on dossier "
            f"{verdict['dossier_id']} -- {state}.", indent="  ", width=width))
        lines.append(_wrapped(
            ("Its reasons: " + ", ".join(str(reason) for reason in reasons) + "."
             if reasons else
             "It gave no reason code, which is what an accepted claim looks "
             "like: there was nothing to refuse."), indent="    ", width=width))
        if body.get("requires_review"):
            lines.append(_wrapped(
                "It asks for a person to look at it before anything acts on it.",
                indent="    ", width=width))
        if verdict["supersede_reason"]:
            lines.append(_wrapped(
                f"It was retired because: {verdict['supersede_reason']}.",
                indent="    ", width=width))
    return lines


def _placed(conn: sqlite3.Connection, row: sqlite3.Row, *,
            width: int) -> list[str]:
    """Where the file was sent, and which stage decided it.

    `origin_stage` is the "who decided" half and is why this stage is not just a
    folder name: a destination reached by the rules and a destination reached by
    a model are different things to a person judging it. `group_plan_id` is
    `00`:112's own distinction -- "one coherent group plan rather than several
    unrelated file moves" -- which cannot be read off a folder name at all.
    """
    _bare, prefixed = _subject_refs(row)
    rows = _rows(conn, "SELECT * FROM placement_decisions WHERE subject_ref "
                       "LIKE ? ORDER BY created_at, record_id", prefixed)
    if not rows:
        return [_wrapped(
            "Nothing was placed, because no placement decision names this file. "
            "This run proposed no destination for it, so no plan moves it and "
            "no branch carries it.", indent="  ", width=width)]
    lines: list[str] = []
    for decision in rows:
        state = ("still stands" if decision["superseded_by"] is None
                 else f"retired by {decision['superseded_by']}")
        lines.append(_wrapped(
            f"{decision['outcome']} at node {decision['node_id'] or 'none'}, "
            f"decided by {decision['origin_stage']} in plan version "
            f"{decision['plan_version']}, {decision['created_at']} -- {state}.",
            indent="  ", width=width))
        if decision["group_plan_id"]:
            lines.append(_wrapped(
                f"It went where its group went: group plan "
                f"{decision['group_plan_id']} was judged as a whole and this "
                f"file followed it.", indent="    ", width=width))
        if decision["returned_from"]:
            lines.append(_wrapped(
                f"It was returned from {decision['returned_from']} before it "
                f"reached here.", indent="    ", width=width))
        if decision["review_policy"]:
            lines.append(_wrapped(
                f"Before anything moves it, it needs "
                f"{decision['review_policy']}.", indent="    ", width=width))
        if decision["supersede_reason"]:
            lines.append(_wrapped(
                f"It was retired because: {decision['supersede_reason']}.",
                indent="    ", width=width))
    return lines


def file_trail(conn: sqlite3.Connection, wanted: str, *,
               width: int) -> Trail:
    """The five stages of one file, as lines, from this database alone.

    The one entry point. `--trail` prints what this returns and any other surface
    can print the same walk without re-deriving it -- which is the second half of
    gap 25: one rendering, so what a person is shown on one screen cannot drift
    from what they are shown on another.

    **A word that names two files is refused, and both are printed.** It is
    `--apply`'s doctrine ("A name that fits two branches is refused and both are
    printed -- it is never guessed") and it is not hypothetical here: a
    superseded file version keeps its path while the new version records the
    same one, so a path is genuinely two answers and picking the newer would
    quietly answer a different question than the one asked.
    """
    found = files_named(conn, wanted)
    if not found:
        return Trail(found=False, lines=(
            _wrapped(f"{wanted!r} is not a file in this plan database. A trail "
                     f"is read from what a run recorded, so a file this "
                     f"database never saw has none -- pass the path, the "
                     f"filename or the file id exactly as the report printed "
                     f"it.", indent="", width=width),))
    if len(found) > 1:
        lines = [_wrapped(
            f"{wanted!r} names {len(found)} files in this plan database, and "
            f"which of them you meant is not something to guess at. Pass one of "
            f"these file ids to --trail:", indent="", width=width)]
        lines.extend(f"  {row['file_id']}   {row['current_path']}"
                     for row in found)
        return Trail(found=False, lines=tuple(lines))
    row = found[0]
    lines = [
        _wrapped(f"The trail of {row['filename']}", indent="", width=width),
        _wrapped(f"{row['current_path']}", indent="  ", width=width),
        _wrapped(f"file id {row['file_id']}, {row['hash_algorithm']} "
                 f"{row['content_hash']}, {row['observed_size']} bytes, "
                 f"extension {row['extension'] or 'none'}, format declared "
                 f"{row['mime_type'] or 'none'} and detected "
                 f"{row['detected_format'] or 'none'}, scan {row['scan_state']}, "
                 f"sensitivity {row['sensitivity_state'] or 'not recorded'}.",
                 indent="  ", width=width),
        _wrapped("Nothing below was read from your disk and no model was asked "
                 "anything to print it: every line is a row this run already "
                 "wrote.", indent="  ", width=width),
    ]
    for stage, walk in ((EXTRACTED, _extracted), (CLASSIFIED, _classified),
                        (ASKED, _asked), (JUDGED, _judged), (PLACED, _placed)):
        lines.append("")
        lines.append(stage)
        lines.extend(walk(conn, row, width=width))
    return Trail(found=True, lines=tuple(lines))
