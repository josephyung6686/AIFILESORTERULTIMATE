"""What the model would actually be SENT, measured offline, through the real gate.

    python3 -m tools.groundtruth.payload --database DB --corpus DIR

`104` §7 "Instruments" asks for this in one sentence: "add payload inspection
(largest dossier, count over ceiling, canary scan) and a 'blocked' line that counts
gate refusals by reason as well as route withholding, so R-46 cannot recur."

**What R-46 was.** A scoreboard reported "files blocked from the model 114 -> 19".
Nineteen is what `cli.model_route_permitted` withheld. One hundred and thirty more
were refused by `Gate.release` on the same code, and the scoreboard never asked the
gate, so a number that meant "the route let 180 through" was read as "180 reached a
model". The two are different questions with different answers and this reports both.

**Offline, and it means it.** No model is invoked and no network socket is opened:
the routing object exists only so the composition root can be built the way a real
run builds it, and the one method that would send -- `ModelClient.invoke` -- is never
called. What runs is `releasable_observations` -> `build_fact_request` ->
`Gate.release`, which is the whole of what A_fact does before a model sees anything.

**It writes to a COPY.** `Gate.release` is not a query: it appends §8.4's audit
record and mints a release capability before returning `Released`. Running it over a
person's plan database would leave audit rows for calls nobody made, so the database
is copied first and the copy is what is opened. The owner's database is opened
read-only, once, to copy it.

**It prints no value.** Sizes, counts, reasons, and corpus-relative paths -- the same
things `per-file.tsv` already carries. The canary check is a substring test whose
answer is a number.

**The canary, on real files.** A planted sentence only works on synthetic input. On
a person's corpus the canary is each file's OWN whole-document text: the span-less
`body` observation at the empty container path, which is what `structured_text.py`
and `docx.py` emit and what `privacy.vocabulary.ALWAYS_LOCAL` calls
`complete_extracted_text`. A hit means that file's entire text appeared inside
something the gate released, which is `104` SF-1 and has exactly one explanation.
The text is read to compare against and is never printed, stored or returned.
"""
from __future__ import annotations

import argparse
import shutil
import sqlite3
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
for _path in (str(_ROOT), str(_ROOT / "src")):
    if _path not in sys.path:
        sys.path.insert(0, _path)

#: A base URL that cannot resolve and a key that is not the owner's. The routing
#: object is built because `fact_call_authorities` requires one and because a
#: measurement of a composition root that was built differently measures a different
#: product; nothing here calls `invoke`, so neither value is ever used.
UNREACHABLE_BASE_URL = "https://model.invalid"
NOT_A_KEY = "not-a-key"

#: What A_fact is asked. The instrument scores no placement, so any situation the
#: shipped library carries would do -- this is the one `104` §9's numbers are taken
#: under, so the dossiers measured are the dossiers those numbers describe.
DEFAULT_SITUATION = "academic.coursework"


@dataclass(frozen=True)
class FilePayload:
    """One file's answer to "what would be sent, and was it allowed to be?".

    TWO SIZES, and the difference between them is the whole point. `built_*` is the
    dossier `model_facts` OFFERED -- measured before the door sees it, and recorded
    whatever the door then says. `released_*` is what came back out of `Released`,
    and is zero for every other outcome.

    Reporting only the released size would make this instrument blind to exactly
    what it exists to find. A dossier over the ceiling is DENIED
    `dossier_over_budget`, so it releases nothing, so a "largest released" line can
    never exceed the ceiling and a "count over the ceiling" taken over released
    files is 0 by construction, on any corpus, forever. `104` R-07's number --
    45,843 bytes -- is a BUILT size, and this is the field that can hold it.
    """

    path: str                       # corpus-relative
    route_permitted: bool
    #: `released`, `denied`, `needs_consent`, `not_built` or `unreadable_request`.
    outcome: str
    #: The denial's reason word, the `not_built` cause, or the exception's type.
    reason: str | None
    built_items: int
    built_bytes: int
    built_tokens: int
    over_ceiling: bool              # the BUILT dossier, whatever the gate then said
    canary_offered: bool            # a whole document was in what was offered
    released_items: int
    released_bytes: int
    measured_tokens: int
    canary_hit: bool                # a whole document was in what was RELEASED


@dataclass
class PayloadReport:
    ceiling: int
    files: list[FilePayload] = field(default_factory=list)

    @property
    def built(self) -> list[FilePayload]:
        return [f for f in self.files if f.outcome != "not_built"]

    @property
    def released(self) -> list[FilePayload]:
        return [f for f in self.files if f.outcome == "released"]

    @property
    def largest_built(self) -> FilePayload | None:
        return max(self.built, key=lambda f: f.built_bytes, default=None)

    @property
    def largest(self) -> FilePayload | None:
        return max(self.released, key=lambda f: f.released_bytes, default=None)

    @property
    def over_ceiling(self) -> list[FilePayload]:
        """Measured on what was BUILT. See `FilePayload`: over the released set this
        is 0 by construction, because over-ceiling is a denial."""
        return [f for f in self.built if f.over_ceiling]

    @property
    def canary_offered(self) -> list[FilePayload]:
        return [f for f in self.built if f.canary_offered]

    @property
    def canary_hits(self) -> list[FilePayload]:
        return [f for f in self.released if f.canary_hit]

    def gate_refusals_by_reason(self) -> dict[str, int]:
        """Every file the door stopped, keyed by the word it stopped it with.

        `needs_consent` and an unresolvable request are in here beside the eight
        denial reasons, under their own names rather than folded into one. They are
        not denials -- one is a question for the person and the other is a contract
        failure by the caller -- but they are files that did not reach a model, and
        the whole of R-46 is that a file which did not reach a model must be counted
        somewhere. Their names say which they are.
        """
        tally: dict[str, int] = {}
        for one in self.files:
            if one.outcome in ("denied", "needs_consent", "unreadable_request"):
                key = one.reason or one.outcome
                tally[key] = tally.get(key, 0) + 1
        return dict(sorted(tally.items(), key=lambda kv: (-kv[1], kv[0])))

    def not_built_by_reason(self) -> dict[str, int]:
        tally: dict[str, int] = {}
        for one in self.files:
            if one.outcome == "not_built":
                key = one.reason or "unstated"
                tally[key] = tally.get(key, 0) + 1
        return dict(sorted(tally.items(), key=lambda kv: (-kv[1], kv[0])))


# --- reading the database ----------------------------------------------------

def _scan_run_id(conn: sqlite3.Connection) -> str:
    row = conn.execute(
        "SELECT scan_run_id FROM scan_runs ORDER BY started_at DESC LIMIT 1"
    ).fetchone()
    if row is None:
        raise SystemExit("no scan_runs row: this is not a plan database a run wrote")
    return row[0]


def _relative(path: str, root: str) -> str:
    prefix = root.rstrip("/") + "/"
    return path[len(prefix):] if path.startswith(prefix) else path


def _whole_document_texts(conn: sqlite3.Connection, file_id: str,
                          content_hash: str) -> tuple[str, ...]:
    """This file's own whole-text values, which are its canaries.

    Both shapes are taken: the span-less `body` observation standing at the EMPTY
    container path -- §2.4's "the whole file", which is what `structured_text.py`
    and `docx.py` emit -- and the text of the unit standing at that same path.
    They are the same characters when both exist; taking both means a fix that
    moves one and not the other cannot hide behind the one it did not move, and
    a run written BEFORE the unit existed still yields a canary.

    Read here and nowhere else. The values are compared against and dropped: they
    are not returned in the report, not written to a file, and not printed.
    """
    from facts.evidence import observations_for_version

    texts: list[str] = []
    runs: set[str] = set()
    for observation in observations_for_version(conn, file_id, content_hash):
        where = observation.location
        if (where.zone == "body" and where.text_span is None
                and not where.container_path):
            if observation.raw_value:
                texts.append(observation.raw_value)
            runs.add(observation.run_id)
    for run_id in sorted(runs):
        row = conn.execute(
            "SELECT text FROM text_units WHERE run_id = ? AND unit_locator = ''",
            (run_id,)).fetchone()
        if row is not None and row[0]:
            texts.append(row[0])
    return tuple(texts)


def canary_hit(released_values, canaries) -> bool:
    """Did any whole-document text turn up inside anything released?

    Its own function so it can be tested in both directions without a corpus. The
    test is `in` rather than `==` on purpose: a dossier that released the document
    plus a heading, or the document with a byte of context around it, is still the
    document leaving, and an equality test would call that a miss.

    An empty canary matches every string and is dropped: a file whose extractors
    recovered no text has no whole text to leak, and counting it as a hit would
    report the emptiest files as the worst breaches.
    """
    wanted = tuple(text for text in canaries if text)
    return any(text in value for value in released_values for text in wanted)


# --- the measurement ---------------------------------------------------------

def inspect_database(database: Path, corpus: Path, *,
                     situation: str = DEFAULT_SITUATION,
                     canary: str | None = None,
                     scratch: Path | None = None) -> PayloadReport:
    """Build every file's A_fact dossier through the real gate and measure it.

    `canary` is an extra sentence to look for on top of each file's own whole text.
    A synthetic corpus plants one; a real one has no need of it.
    """
    import cli
    from database_agent.budget import get_ceiling
    from database_agent.files_table import get_file
    from model_facts import (
        build_fact_request, dossier_tokens, measure_released_tokens,
        releasable_observations,
    )
    from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy
    from privacy.release import Denied, MalformedRequest, NeedsConsent, Released
    from privacy.resolve import AmbiguousObservationKey, UnresolvableSpan
    from production import (
        corpus_roster, folder_levels_for, load_shipped_catalogue,
        read_packaged_library_file, schema_for_situation,
    )
    from readers.model_routing import FAST, LOGIC, REASONING, deepseek_routing

    scratch = scratch or Path(tempfile.mkdtemp(prefix="payload-"))
    scratch.mkdir(parents=True, exist_ok=True)
    working = scratch / "payload-copy.sqlite"
    shutil.copyfile(database, working)

    conn = sqlite3.connect(working)
    conn.row_factory = sqlite3.Row
    try:
        root = str(Path(corpus).resolve())
        scan_run_id = _scan_run_id(conn)
        roster = corpus_roster(conn, scan_run_id)

        catalogue = load_shipped_catalogue(read_packaged_library_file)
        levels = folder_levels_for(catalogue, situation)
        schema = schema_for_situation(catalogue, situation)
        routing = deepseek_routing(
            api_key=NOT_A_KEY, base_url=UNREACHABLE_BASE_URL,
            model_id_of_tier={REASONING: "r", LOGIC: "l", FAST: "f"},
            tier_of_call_site=cli.TIER_OF_CALL_SITE,
            max_response_tokens=cli.MAX_RESPONSE_TOKENS, timeout_seconds=1.0)

        # The SAME policy `cli.run._model_fact_pass` puts in force before the fact
        # pass: `CLOUD_ENABLED_MODE` at `PLAN_VERSION`. Without it the gate answers
        # `mode_forbids_target` for all 199 files -- an offline run stores `offline`
        # -- and the instrument would measure the operation mode instead of the
        # payload, which is a different and already-known fact.
        policy_version = set_policy(
            conn,
            Policy(policy_version=UNSET_POLICY_VERSION,
                   operation_mode=cli.CLOUD_ENABLED_MODE, consent_grants=(),
                   redaction_settings={}, automatic_move_permissions={},
                   plan_version=cli.PLAN_VERSION,
                   set_at="2026-01-01T00:00:00+00:00"),
            component_version=cli.COMPONENT_VERSION, user_id="payload-inspection",
            reason="offline payload inspection: no model is invoked")

        authorities = cli.fact_call_authorities(
            conn, routing=routing, scan_run_id=scan_run_id,
            corpus_file_count=len(roster), policy_version=policy_version,
            wire_handle_key=bytes(32), schema=schema, folder_levels=levels,
            user_id="payload-inspection",
            now=lambda: "2026-01-01T00:00:00+00:00")
        # R-02: the route now answers per LOCALITY, because that is the question
        # `Gate.release` answers and the two disagreeing is what this instrument
        # was built to measure. The target is the one the routing above built, so
        # the route is asked about the same destination the gate is asked about.
        permitted = cli.model_route_permitted(
            conn, locality=authorities.model_target.locality,
            operation_mode=cli.OPERATION_MODE,
            unclassified_permits_local=cli.UNCLASSIFIED_PERMITS_LOCAL)

        ceiling = get_ceiling(conn, "model.max_dossier_tokens_per_call")
        if ceiling is None:
            ceiling = cli.GROUPING_LIMITS.max_dossier_tokens
        report = PayloadReport(ceiling=int(ceiling))

        for file_id, content_hash in roster:
            row = get_file(conn, file_id)
            path = _relative(row["current_path"], root) if row else file_id
            route = bool(permitted(file_id))

            observations = releasable_observations(
                conn, file_id=file_id, content_hash=content_hash,
                limit=authorities.max_released_observations)
            if not observations:
                report.files.append(_nothing(
                    path=path, route=route, outcome="not_built",
                    reason="nothing_releasable"))
                continue

            # MEASURED HERE, before the door, and kept whatever the door then says.
            # A dossier over the ceiling is DENIED, so a size read off `Released`
            # can never exceed the ceiling and a count taken there is 0 on every
            # corpus forever. `104` R-07's 45,843 bytes is a size at this line.
            offered = tuple(one.raw_value for one in observations)
            built_tokens = dossier_tokens(offered)
            wanted = _whole_document_texts(conn, file_id, content_hash)
            if canary:
                wanted = wanted + (canary,)
            built = dict(
                built_items=len(offered),
                built_bytes=sum(len(value) for value in offered),
                built_tokens=built_tokens,
                over_ceiling=built_tokens > report.ceiling,
                canary_offered=canary_hit(offered, wanted))

            request = build_fact_request(
                _fact_request(conn, file_id, content_hash, authorities),
                observations, model_target=authorities.model_target,
                prompt=authorities.prompt,
                max_dossier_tokens=authorities.max_dossier_tokens)

            try:
                decision = authorities.gate.release(request.model_call_request)
            except (MalformedRequest, UnresolvableSpan,
                    AmbiguousObservationKey) as caught:
                report.files.append(_nothing(
                    path=path, route=route, outcome="unreadable_request",
                    reason=type(caught).__name__, **built))
                continue

            if isinstance(decision, Denied):
                report.files.append(_nothing(
                    path=path, route=route, outcome="denied",
                    reason=decision.reason, **built))
                continue
            if isinstance(decision, NeedsConsent):
                report.files.append(_nothing(
                    path=path, route=route, outcome="needs_consent",
                    reason="needs_consent", **built))
                continue
            if not isinstance(decision, Released):
                report.files.append(_nothing(
                    path=path, route=route, outcome="unreadable_request",
                    reason=type(decision).__name__, **built))
                continue

            values = tuple(item.value for item in decision.materialised_items)
            report.files.append(FilePayload(
                path=path, route_permitted=route, outcome="released", reason=None,
                released_items=len(values),
                released_bytes=sum(len(value) for value in values),
                measured_tokens=measure_released_tokens(
                    request.model_call_request, decision.materialised_items),
                canary_hit=canary_hit(values, wanted), **built))
        return report
    finally:
        conn.close()


def _nothing(*, path: str, route: bool, outcome: str, reason: str | None,
             built_items: int = 0, built_bytes: int = 0, built_tokens: int = 0,
             over_ceiling: bool = False, canary_offered: bool = False
             ) -> FilePayload:
    """A file that reached an outcome other than `Released`. The BUILT size travels
    with it -- a dossier the door refused was still assembled, and its size is the
    number `104` R-07 is about."""
    return FilePayload(
        path=path, route_permitted=route, outcome=outcome, reason=reason,
        built_items=built_items, built_bytes=built_bytes,
        built_tokens=built_tokens, over_ceiling=over_ceiling,
        canary_offered=canary_offered,
        released_items=0, released_bytes=0, measured_tokens=0, canary_hit=False)


def _fact_request(conn, file_id: str, content_hash: str, authorities):
    """`facts.llm_seam.build_request`, exactly as `fact_call_stage` calls it."""
    from facts.llm_seam import build_request

    return build_request(
        conn, file_id=file_id, content_hash=content_hash,
        activation_signals=authorities.activation_signals,
        normalizers=authorities.normalizers)


# --- the report --------------------------------------------------------------

def render(report: PayloadReport) -> str:
    """`104` §7's four measurements, plus the two-sided blocked line R-46 needed."""
    lines = [
        "PAYLOAD INSPECTION -- what the model would be sent, measured offline",
        "  No model was invoked and no socket was opened. Every dossier below was",
        "  built by `model_facts` and decided by the real `privacy.gate.Gate`, on a",
        "  copy of the plan database, under the hybrid policy the fact pass sets.",
        "",
        f"  files in the roster            {len(report.files)}",
        f"  dossiers built                 {len(report.built)}",
        f"  released by the gate           {len(report.released)}",
    ]
    built = report.largest_built
    if built is None:
        lines.append("  largest dossier BUILT          none built")
    else:
        lines.append(
            f"  largest dossier BUILT          {built.built_bytes} bytes, "
            f"{built.built_tokens} measured tokens, {built.built_items} items")
        lines.append(f"                                 {built.path}")
    largest = report.largest
    if largest is None:
        lines.append("  largest dossier RELEASED       none released")
    else:
        lines.append(
            f"  largest dossier RELEASED       {largest.released_bytes} bytes, "
            f"{largest.measured_tokens} measured tokens, "
            f"{largest.released_items} items")
        lines.append(f"                                 {largest.path}")
    lines += [
        f"  ceiling                        {report.ceiling} tokens "
        f"(model.max_dossier_tokens_per_call)",
        f"  BUILT over the ceiling         {len(report.over_ceiling)}",
        "                                 (read off what was assembled, not off "
        "what was",
        "                                  released -- an over-ceiling dossier is "
        "denied, so",
        "                                  a count taken at the door is 0 on every "
        "corpus)",
        f"  canary: offered                {len(report.canary_offered)}",
        f"  canary: RELEASED               {len(report.canary_hits)}",
        "                                 (a file's own whole text found inside a "
        "dossier;",
        "                                  offered is what was assembled, released "
        "is what left)",
        "",
        f"  blocked: "
        f"{sum(1 for f in report.files if not f.route_permitted)} withheld at the "
        f"route, "
        f"{sum(report.gate_refusals_by_reason().values())} stopped at the gate, "
        f"{sum(report.not_built_by_reason().values())} never built",
        "  Three different questions, and R-46 was reporting the first as if it "
        "were all",
        "  three. `cli.model_route_permitted` decides whether a file's route may "
        "reach a",
        "  model at all; `Gate.release` decides whether this particular call may "
        "leave;",
        "  `model_facts` declines to build a call it has nothing to put in.",
    ]
    refusals = report.gate_refusals_by_reason()
    if refusals:
        lines.append("    at the gate, by reason:")
        for reason, count in refusals.items():
            lines.append(f"      {reason:<28} {count}")
    never = report.not_built_by_reason()
    if never:
        lines.append("    never built, by cause:")
        for reason, count in never.items():
            lines.append(f"      {reason:<28} {count}")
    if report.canary_hits:
        lines.append("")
        lines.append("  !! WHOLE-DOCUMENT RELEASE. These files' entire text appeared "
                     "in a released payload:")
        for one in report.canary_hits:
            lines.append(f"      {one.path}")
    offered_only = [one for one in report.canary_offered if not one.canary_hit]
    if offered_only:
        lines.append("")
        lines.append("  !! WHOLE-DOCUMENT OFFERED. These files' entire text was put "
                     "into a dossier and")
        lines.append("     stopped at the door rather than at the builder. The door "
                     "is the last line:")
        for one in offered_only:
            lines.append(f"      {one.path}  ({one.reason or one.outcome})")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tools.groundtruth.payload", description=__doc__)
    parser.add_argument("--database", type=Path, required=True,
                        help="a plan database a run of the product wrote")
    parser.add_argument("--corpus", type=Path, required=True,
                        help="the corpus that run read, for relative paths")
    parser.add_argument("--situation", default=DEFAULT_SITUATION,
                        help=f"the situation to ask A_fact under "
                             f"(default {DEFAULT_SITUATION})")
    parser.add_argument("--canary", default=None,
                        help="an extra sentence to scan released payloads for; "
                             "a synthetic corpus plants one, a real one does not "
                             "need one because each file's own text is its canary")
    parser.add_argument("--out", type=Path, default=None,
                        help="write the block here as well as printing it")
    args = parser.parse_args(argv)

    report = inspect_database(args.database, args.corpus,
                              situation=args.situation, canary=args.canary)
    block = render(report)
    print(block)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(block + "\n", encoding="utf-8")
        print(f"\nwritten: {args.out}")
    # Non-zero on either finding, and `canary_offered` counts as a finding: a whole
    # document the builder assembled and the door refused is `104` SF-1 still open,
    # caught one layer later than it should have been.
    return 1 if (report.canary_offered or report.canary_hits
                 or report.over_ceiling) else 0


if __name__ == "__main__":
    raise SystemExit(main())
