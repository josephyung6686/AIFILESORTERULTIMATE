"""What the placement row WOULD be if site C's observed verdicts were applied.

`104` §7 Phase 1 step 6: since Wave 3 a run with a model configured asks site C and
records everything -- the dossier, the model's response and the validator's verdict
-- and applies none of it, because the prompt is not ratified. `_observed_only`
rewrites the verdict to an abstention before P11 sees it, so `placement_decisions`
holds the DETERMINISTIC answer and the scoreboard's sorting row cannot move however
good the model's answers are. The owner has to decide whether to ratify the text
BEFORE that row can tell him anything, which is the wrong way round.

This is the answer to "what would the row be". It reads the same databases the
scoreboard reads, substitutes the node the validator ACCEPTED for the node the run
APPLIED, and scores the result through `report.sorting_lines` and
`score.score_situation` -- the same code, not the same rules re-implemented, because
a second scorer would drift and the drift would read as a fact about the model.

Three rules it does not bend:

  * **It applies nothing.** No file moves, no database is written, every connection
    is `mode=ro`. This is a second reading of a run that already happened.
  * **It asks nobody.** No model, no socket, no network module imported. The
    verdicts are already on disk; this reads them.
  * **It prints no file content.** `text_units.text` is never read -- it is
    `complete_extracted_text`, `ALWAYS_LOCAL` -- and neither is the dossier payload
    (released excerpts), a citation's `cited_span`, a refusal's explanation or a
    failure's. Of the model's response this takes ONE string, the destination node
    id, and drops the rest in the function that parsed it.

WHAT IS SUBSTITUTED, AND WHAT IS CARRIED. Only a recorded `P8Verdict` at
`C_placement` replaces a file's outcome, and it does so the way `p8_seam.transcribe`
does: `accept_direct` and `accept_context_supported` are placements, and `weak`,
`reject` and `abstain` are abstentions. Everything else -- a gate refusal, a
pre-call abstention, a failed call, a file site C was never asked about -- CARRIES
the applied outcome unchanged and is counted under the reason it was carried.

Carrying rather than scoring those as "not placed" is the honest direction and not
the flattering one. `transcribe` never sees them either: a `Refusal` takes P11's
`PRIVACY_BLOCKED` path before it, and R-74 rules that a gate-blocked file takes the
deterministic placement rather than losing its home. A shadow row that zeroed them
would be answering "what if site C were the only placer", which is not the question,
and it would move the denominator away from the real row so the two could not be
read side by side.
"""
from __future__ import annotations

import collections
import dataclasses
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from tools.groundtruth.labels import Label
# The private names are imported rather than copied ON PURPOSE. `_destination_of`
# is how the scoreboard turns a node id into the folder chain it prints, and
# `_relative` is how it turns a stored absolute path into the corpus-relative one a
# label names. A second copy of either would be a second thing to keep true, and
# the first divergence would show up as a shadow row that disagreed with the real
# one for a reason that was not the model's.
from tools.groundtruth.measure import (
    Observation, RunObservation, _destination_of, _refusal_reason, _relative,
    _rows,
)
from tools.groundtruth.report import (
    row_104, row_128, sorting_lines, spillover_lines,
)
from tools.groundtruth.score import SituationScore, score_situation

#: P8's spelling for the placement site. Spelled here rather than imported from
#: `src/llm_harness/vocabulary.py` for the reason every other value in this package
#: is read from the database and not from the product: the harness measures what a
#: run WROTE, and a run written by an older build is still a run this must read.
C_PLACEMENT = "C_placement"

#: The two verdict outcomes `placement.p8_seam.transcribe` turns into a placement.
#: Every other member of `OUTCOMES` is an abstention there and is one here.
ACCEPTING = ("accept_direct", "accept_context_supported")

#: Why a file's applied outcome was carried instead of replaced. One of these, or
#: `SUBSTITUTED`, is recorded for EVERY scored file: "never silently omitted" is the
#: standing rule and a shadow row whose provenance is unstated is exactly that.
SUBSTITUTED = "verdict"
NEVER_ASKED = "carried: site C was never asked"
REFUSED = "carried: refused at the gate"
PRE_CALL = "carried: abstained before the call"
FAILED = "carried: the call failed"
NO_RESPONSE = "carried: no readable response"
NO_SUCH_NODE = "carried: accepted a node this plan does not hold"
NO_DESTINATION = "carried: accepted with no destination"

#: The word the placement record uses for a file that was filed somewhere.
PLACE = "place"
ABSTAIN = "abstain"

#: `llm_harness.vocabulary.PRE_CALL_NAMESPACE`. A call stopped BEFORE a dossier
#: exists is addressed `pre-call:{call_site}:{subject_ref}` -- an address that
#: deliberately cannot be joined to `llm_dossier`, because there is no dossier row
#: to join to. It is also the only place a gate refusal records WHICH FILE it
#: refused, so reading it is how a refused file is attributed to its label rather
#: than counted as one nobody asked about.
PRE_CALL_NAMESPACE = "pre-call"


@dataclass(frozen=True)
class ObservedVerdict:
    """One file's recorded site-C answer, read back and applied to nothing."""

    path: str
    outcome: str                   # P8's own word: accept_direct, abstain, ...
    reasons: tuple[str, ...]
    #: The folder chain the validator accepted, root first -- empty for an
    #: abstention, a refusal, or an accepted node the tree does not hold.
    destination: tuple[str, ...]
    source: str                    # `SUBSTITUTED`, or why it was carried


@dataclass(frozen=True)
class SiteTally:
    """Where one call site's answers ended up. Every count is a row on disk."""

    site: str
    outcomes: Mapping[str, int]      # llm_verdict.outcome -> files
    reasons: Mapping[str, int]       # reason code -> verdicts, non-accepting only
    refusals: Mapping[str, int]      # P7's denial reason -> refusals
    pre_call: Mapping[str, int]      # PreCallAbstention.reason -> rows
    failures: Mapping[str, int]      # failure_class -> rows

    @property
    def accepted(self) -> int:
        return sum(n for word, n in self.outcomes.items() if word in ACCEPTING)

    @property
    def total(self) -> int:
        return (sum(self.outcomes.values()) + sum(self.refusals.values())
                + sum(self.pre_call.values()) + sum(self.failures.values()))


def _connect(database: str | Path) -> sqlite3.Connection:
    """Read-only, always. This instrument writes nothing, ever."""
    return sqlite3.connect(f"file:{database}?mode=ro", uri=True)


def _file_id_of(subject_ref: str) -> str:
    """`placement.store.subject_ref_of`, read back. THE FILE FORM HAS THREE PARTS.

    `file:{file_id}:{content_hash}`. The kind comes off the front by the FIRST
    colon, which is safe because the kinds are a closed vocabulary with no colon in
    them; the hash comes off the back by the LAST, which is safe because a sha256
    hex digest contains none and P11 promises nothing about a file id's shape.
    `model_placement._file_id_of` is the same reading at the other end of the seam.
    """
    kind, separator, rest = subject_ref.partition(":")
    if not separator:
        return subject_ref
    if kind != "file":
        return rest or subject_ref
    identifier, hash_separator, _hash = rest.rpartition(":")
    if not hash_separator:
        return rest
    return identifier or rest


def _pre_call_subject(address: str) -> tuple[str, str] | None:
    """`(call site, subject ref)` out of a pre-call address, or `None`.

    `vocabulary.pre_call_address` writes `pre-call:{call_site}:{subject_ref}` and
    the subject ref has colons of its own, so the split is bounded at two: the
    namespace, the site, and everything else. A real dossier id is a content
    address and never starts with the namespace, so this cannot mistake one.
    """
    namespace, _, rest = address.partition(":")
    if namespace != PRE_CALL_NAMESPACE or not rest:
        return None
    site, separator, subject = rest.partition(":")
    if not separator or not subject:
        return None
    return site, subject


def _site_of_dossier(connection) -> dict[str, str]:
    """dossier id -> call site, from both tables that record one.

    A dossier ROW exists only for a call that got past the gate: `record_dossier`
    fires inside `_issue_and_validate`, which `run_call` reaches after
    `gate.release` returned `Released`. A refusal and a pre-call abstention still
    write a `llm_grounding_report`, and that carries the call site -- which is the
    only way a gate refusal can be attributed to the site it was refused at.
    """
    site: dict[str, str] = {}
    for table in ("llm_grounding_report", "llm_dossier"):
        try:
            for row in _rows(connection,
                             f'select dossier_id, call_site from "{table}"'):
                site[row["dossier_id"]] = row["call_site"]
        except sqlite3.Error:
            continue          # an older database without the table
    return site


def _verdict_reasons(payload: str) -> tuple[str, ...]:
    """The reason codes on one verdict, and NOTHING else out of its payload.

    `store._payload` serialises the whole `P8Verdict`, whose `citations_checked`
    carry spans of the file. Only `reasons` -- a closed vocabulary of code names --
    is read, and the parsed object goes out of scope here.
    """
    try:
        loaded = json.loads(payload)
    except (TypeError, ValueError):
        return ("unreadable_verdict_payload",)
    reasons = loaded.get("reasons") if isinstance(loaded, dict) else None
    if not isinstance(reasons, list):
        return ()
    return tuple(str(item) for item in reasons if isinstance(item, str))


def _accepted_node_id(response_bytes: object) -> str | None:
    """The destination the model named, and nothing else out of its response.

    The C response schema is `{"claims": [{"payload": {"destination": ...}}]}` with
    exactly one claim -- one file, one decision. Beside `destination` sit
    `citations[].cited_span`, `citations[].why_it_supports` and
    `unknown.insufficiency_statement`, every one of which can quote the file. This
    returns ONE string, an identifier out of `allowed_vocabulary`, and the parsed
    response is unreachable the moment it returns.

    `None` for the word `none` -- the schema's own spelling for "I could not choose"
    -- and for every shape this cannot read.
    """
    if not isinstance(response_bytes, (bytes, bytearray, memoryview)):
        return None
    try:
        claims = json.loads(bytes(response_bytes)).get("claims")
    except (TypeError, ValueError, AttributeError):
        return None
    if not isinstance(claims, list) or not claims:
        return None
    claim = claims[0]
    if not isinstance(claim, dict):
        return None
    payload = claim.get("payload")
    if not isinstance(payload, dict):
        return None
    destination = payload.get("destination")
    if not isinstance(destination, str) or destination in ("", "none"):
        return None
    return destination


def site_tallies(database: str | Path) -> tuple[SiteTally, ...]:
    """Per call site: where every recorded answer ended up.

    Four terminal shapes and all four are counted, because a file whose answer
    died has to be counted somewhere: a verdict (by outcome, and by reason code
    when the outcome is not an acceptance), a gate refusal (by P7's denial
    reason), a pre-call abstention (by its reason), and a transport failure (by
    its class). Anything whose site cannot be established is counted under a name
    of its own rather than dropped.
    """
    connection = _connect(database)
    try:
        site_of = _site_of_dossier(connection)
        unknown = "(site not recorded)"

        def site_for(dossier_id: str) -> str:
            """The call site behind one address, from the row or from the address.

            The grounding report carries it for every terminal the harness writes.
            The address itself is the fallback, and it exists because a database
            missing that table is still a database whose refusals happened at a
            site -- and counting them under "site not recorded" when the answer is
            in the key would be losing a fact this instrument holds.
            """
            recorded = site_of.get(dossier_id)
            if recorded:
                return recorded
            parsed = _pre_call_subject(dossier_id)
            return parsed[0] if parsed else unknown

        outcomes: dict[str, collections.Counter] = collections.defaultdict(
            collections.Counter)
        reasons: dict[str, collections.Counter] = collections.defaultdict(
            collections.Counter)
        refusals: dict[str, collections.Counter] = collections.defaultdict(
            collections.Counter)
        pre_call: dict[str, collections.Counter] = collections.defaultdict(
            collections.Counter)
        failures: dict[str, collections.Counter] = collections.defaultdict(
            collections.Counter)

        try:
            for row in _rows(connection,
                             "select dossier_id, outcome, payload from llm_verdict "
                             "where superseded_by is null"):
                site = site_for(row["dossier_id"])
                outcomes[site][row["outcome"]] += 1
                if row["outcome"] not in ACCEPTING:
                    for reason in _verdict_reasons(row["payload"]) or ("unstated",):
                        reasons[site][reason] += 1
        except sqlite3.Error:
            pass
        try:
            for row in _rows(connection,
                             "select dossier_id, payload from llm_refusal"):
                refusals[site_for(row["dossier_id"])][
                    _refusal_reason(row["payload"])] += 1
        except sqlite3.Error:
            pass
        try:
            for row in _rows(connection, "select call_site, reason from "
                                         "llm_pre_call_abstention"):
                pre_call[row["call_site"] or unknown][row["reason"]] += 1
        except sqlite3.Error:
            pass
        try:
            for row in _rows(connection, "select dossier_id, failure_class from "
                                         "llm_call_failure"):
                failures[site_for(row["dossier_id"])][
                    row["failure_class"]] += 1
        except sqlite3.Error:
            pass
    finally:
        connection.close()

    names = sorted(set(outcomes) | set(refusals) | set(pre_call) | set(failures))
    return tuple(SiteTally(
        site=name,
        outcomes=dict(outcomes[name].most_common()),
        reasons=dict(reasons[name].most_common()),
        refusals=dict(refusals[name].most_common()),
        pre_call=dict(pre_call[name].most_common()),
        failures=dict(failures[name].most_common()),
    ) for name in names)


def observed_placements(database: str | Path, corpus_root: str | Path,
                        ) -> dict[str, ObservedVerdict]:
    """Every file with a recorded site-C answer, by corpus-relative path.

    One entry per FILE, not per call: two calls over identical content are one
    dossier and two responses, and a site can be asked twice about one subject. The
    LAST recorded verdict wins, by insertion order, which is the same "most recent
    for this dossier" rule `store.last_response_bytes` states -- and it is stated
    rather than assumed because a reader of an old database has no other ordering.
    """
    root = str(Path(corpus_root).resolve())
    connection = _connect(database)
    try:
        return _observed(connection, root)
    finally:
        connection.close()


def _observed(connection, root: str) -> dict[str, ObservedVerdict]:
    try:
        nodes = {r["node_id"]: (r["display_label"], r["parent_node_id"])
                 for r in _rows(connection, "select node_id, display_label, "
                                            "parent_node_id from tree_nodes")}
        paths = {r["file_id"]: _relative(r["current_path"], root)
                 for r in _rows(connection, "select file_id, current_path from files")}
        dossiers = _rows(connection, "select dossier_id, subject_ref from llm_dossier "
                                     "where call_site = ? order by rowid", C_PLACEMENT)
    except sqlite3.Error:
        # No model tables at all: an offline run, or a database written before P8's
        # schema existed. That is a measurement -- "site C was asked nothing" -- and
        # not a failure, so it comes back empty rather than raising.
        return {}

    live_verdicts: dict[str, sqlite3.Row] = {}
    for row in _rows(connection, "select dossier_id, outcome, payload from llm_verdict "
                                 "where superseded_by is null order by rowid"):
        live_verdicts[row["dossier_id"]] = row
    refused = {r["dossier_id"] for r in _rows(
        connection, "select dossier_id from llm_refusal")}
    abstained = {r["dossier_id"] for r in _rows(
        connection, "select dossier_id from llm_pre_call_abstention")}
    failed = {r["dossier_id"] for r in _rows(
        connection, "select dossier_id from llm_call_failure")}

    observed: dict[str, ObservedVerdict] = {}

    # THE CALLS THAT NEVER REACHED A DOSSIER, FIRST. A gate refusal and a pre-call
    # abstention write no `llm_dossier` row, so neither appears in the loop below;
    # what they do write is a `pre-call:{site}:{subject_ref}` address, and that is
    # the only record of which FILE was stopped. Read first so a real verdict for
    # the same file -- a second, later call that did get through -- overwrites the
    # terminal rather than the other way round.
    for address in sorted(refused | abstained):
        parsed = _pre_call_subject(address)
        if parsed is None or parsed[0] != C_PLACEMENT:
            continue
        path = paths.get(_file_id_of(parsed[1]))
        if path is None:
            continue
        observed[path] = ObservedVerdict(
            path=path, outcome="", reasons=(), destination=(),
            source=REFUSED if address in refused else PRE_CALL)

    for dossier in dossiers:
        path = paths.get(_file_id_of(dossier["subject_ref"]))
        if path is None:
            # A subject that is not a file of this corpus -- a group, or a file the
            # run has since forgotten. Nothing on the scorecard names it.
            continue
        identifier = dossier["dossier_id"]
        verdict = live_verdicts.get(identifier)
        if verdict is None:
            source = (REFUSED if identifier in refused else
                      PRE_CALL if identifier in abstained else
                      FAILED if identifier in failed else NO_RESPONSE)
            observed[path] = ObservedVerdict(
                path=path, outcome="", reasons=(), destination=(), source=source)
            continue
        reasons = _verdict_reasons(verdict["payload"])
        if verdict["outcome"] not in ACCEPTING:
            observed[path] = ObservedVerdict(
                path=path, outcome=verdict["outcome"], reasons=reasons,
                destination=(), source=SUBSTITUTED)
            continue
        response = _rows(connection, "select response_bytes from llm_response "
                                     "where dossier_id = ? order by rowid desc "
                                     "limit 1", identifier)
        node_id = _accepted_node_id(response[0]["response_bytes"]) if response else None
        if node_id is None:
            observed[path] = ObservedVerdict(
                path=path, outcome=verdict["outcome"], reasons=reasons,
                destination=(),
                source=NO_DESTINATION if response else NO_RESPONSE)
            continue
        if node_id not in nodes:
            # The validator accepted a destination the frozen tree does not hold.
            # P11 REFUSES to place on that (`pipeline` raises rather than filing a
            # file into a folder the index disagrees about), so it is carried and
            # named -- calling it an abstention would credit the model with a
            # caution it did not show.
            observed[path] = ObservedVerdict(
                path=path, outcome=verdict["outcome"], reasons=reasons,
                destination=(), source=NO_SUCH_NODE)
            continue
        observed[path] = ObservedVerdict(
            path=path, outcome=verdict["outcome"], reasons=reasons,
            destination=_destination_of(node_id, nodes), source=SUBSTITUTED)
    return observed


def shadow_run(run: RunObservation, observed: Mapping[str, ObservedVerdict],
               ) -> tuple[RunObservation, dict[str, str]]:
    """One run, re-read as if its site-C verdicts had been applied.

    Returns the run and, beside it, why each file's shadow outcome is what it is.
    Every file in the run gets a word, including the ones site C was never asked
    about, because a shadow row whose provenance is unstated is the silent omission
    this whole harness exists to refuse.

    `104` R-151: a SUBSTITUTED outcome carries NO review policy. P11 computes one
    for every decision it writes, abstentions included, and an abstention's is
    almost always `review_required` -- so a shadow placement that kept the applied
    decision's policy would report "held for the person" about a hold nobody ever
    decided. The shadow row is a placement P11 never made, so the honest value is
    "not on the record", which is what None means everywhere else in `Observation`.
    A file whose applied outcome is CARRIED keeps its own policy, because that one
    was really written.

    `104` R-165's field travels with it, by the identical argument. A substituted
    row is the placement site C's verdict WOULD have made, and the applied
    decision's decider is a fact about the placement P11 really made -- so keeping
    it would credit `rule` or `user` with a node the rules and the person never
    chose, and the shadow half of the model's share would be counted off the wrong
    record. `None` is the truth: nobody decided this, because it did not happen.
    """
    files: dict[str, Observation] = dict(run.files)
    sources: dict[str, str] = {}
    for path, observation in run.files.items():
        answer = observed.get(path)
        if answer is None:
            sources[path] = NEVER_ASKED
            continue
        sources[path] = answer.source
        if answer.source != SUBSTITUTED:
            continue
        if answer.destination:
            files[path] = dataclasses.replace(
                observation, outcome=PLACE, destination=answer.destination,
                review_policy=None, decided_by=None)
        else:
            files[path] = dataclasses.replace(
                observation, outcome=ABSTAIN, destination=(), review_policy=None,
                decided_by=None)
    return dataclasses.replace(run, files=files), sources


def _render_sites(tallies: Sequence[SiteTally]) -> list[str]:
    lines = ["VERDICTS BY SITE   where the model's answers died. Every count is a "
             "row the run wrote."]
    if not tallies:
        lines.append("            nothing was asked of any site in these databases")
        return lines
    for tally in tallies:
        lines.append(f"            {tally.site}  {tally.total} answers, "
                     f"{tally.accepted} accepted")
        if tally.outcomes:
            lines.append("              verdicts:   " + ", ".join(
                f"{word}={n}" for word, n in tally.outcomes.items()))
        if tally.reasons:
            lines.append("              why not:    " + ", ".join(
                f"{code}={n}" for code, n in tally.reasons.items()))
        if tally.refusals:
            lines.append("              refused at the gate: " + ", ".join(
                f"{reason}={n}" for reason, n in tally.refusals.items()))
        if tally.pre_call:
            lines.append("              abstained before the call: " + ", ".join(
                f"{reason}={n}" for reason, n in tally.pre_call.items()))
        if tally.failures:
            lines.append("              the call failed: " + ", ".join(
                f"{cls}={n}" for cls, n in tally.failures.items()))
    return lines


def render(runs: Sequence[RunObservation],
           shadow_runs: Sequence[RunObservation],
           shadow_scores: Sequence[SituationScore],
           labels: Mapping[str, Label],
           sources: Mapping[str, str],
           tallies: Sequence[SiteTally],
           *, applied_scores: Sequence[SituationScore]) -> str:
    """The SHADOW block, beside the real one and never instead of it."""
    lines = ["SHADOW      OBSERVED SITE-C VERDICTS, NOT APPLIED. Nothing here moved a "
             "file or changed a",
             "            record: it is the scoreboard's own sorting rules run over the "
             "node the",
             "            validator ACCEPTED instead of the node the run applied. The "
             "prompt is not",
             "            ratified, so the product recorded these answers and acted on "
             "none of them.",
             ""]

    counted = collections.Counter(
        word for path, word in sources.items() if path in labels)
    substituted = counted.pop(SUBSTITUTED, 0)
    carried = sum(counted.values())
    lines.append(f"            {substituted} labelled files carry a site-C verdict; "
                 f"{carried} keep the applied outcome")
    for word, n in counted.most_common():
        lines.append(f"              {n:4d}  {word}")
    lines.append("")

    confident = sum(s.confident_on_uncertain for s in shadow_scores)
    lines.extend(sorting_lines(shadow_runs, labels, heading="SHADOW SORT",
                               confident_on_uncertain=confident))
    lines.append("")
    lines.extend(spillover_lines(shadow_scores, heading="SHADOW SPL"))
    lines.append("")
    lines.append(f"            applied:  {row_104(runs, labels, applied_scores)}")
    lines.append(f"            shadow:   {row_104(shadow_runs, labels, shadow_scores)}")
    lines.append("            -- `104` §14.5's order. The applied line is the row "
                 "above, repeated here so the")
    lines.append("               two can be read without scrolling. A shadow line "
                 "that is better than the")
    lines.append("               applied one is an argument for ratifying the text; "
                 "it is not a result.")
    lines.append("")
    # `105` §14.7's five, the same pair and the same rule.
    #
    # `invalid output` will usually read the SAME on both lines, and that is
    # correct rather than a bug: whether the validator refused a file's answer is a
    # fact about what the run recorded, not about which placement was afterwards
    # applied, so both readings see it. The two lines part company on the other
    # four, which is the comparison this block exists to make.
    lines.append(f"            applied:  {row_128(runs, labels)}")
    lines.append(f"            shadow:   {row_128(shadow_runs, labels)}")
    lines.append("")
    lines.extend(_render_sites(tallies))
    return "\n".join(lines)


def shadow_block(runs: Sequence[RunObservation],
                 applied_scores: Sequence[SituationScore],
                 labels: Mapping[str, Label],
                 out: Path, corpus: Path,
                 ) -> tuple[str, tuple[RunObservation, ...], dict[str, str]]:
    """The whole of `--shadow`: read, substitute, score, render.

    Returns the block, the shadow runs and the per-file provenance, because
    `per-file.tsv` wants the last two and re-deriving them would read every
    database a second time.
    """
    shadow_runs: list[RunObservation] = []
    sources: dict[str, str] = {}
    tallies: list[SiteTally] = []
    for run in runs:
        database = out / f"{run.situation.replace('.', '_')}.sqlite"
        if not database.exists():
            continue
        observed = observed_placements(database, corpus)
        shadowed, mine = shadow_run(run, observed)
        shadow_runs.append(shadowed)
        tallies.extend(site_tallies(database))
        # One observation per file, from the run whose situation its label names --
        # `report._merged_view`'s rule, applied to the provenance words so a file
        # observed in seventeen runs does not get seventeen answers.
        for path, word in mine.items():
            label = labels.get(path)
            if label is not None and label.situation == run.situation:
                sources[path] = word

    merged: dict[str, SiteTally] = {}
    for tally in tallies:
        prior = merged.get(tally.site)
        merged[tally.site] = tally if prior is None else _add(prior, tally)
    shadow_scores = [score_situation(run, labels) for run in shadow_runs]
    block = render(runs, shadow_runs, shadow_scores, labels, sources,
                   tuple(merged[name] for name in sorted(merged)),
                   applied_scores=applied_scores)
    return block, tuple(shadow_runs), sources


def _add(left: SiteTally, right: SiteTally) -> SiteTally:
    """Two situation runs' tallies for one site, summed.

    Summed and NOT merged per file, unlike every per-file line on the scorecard:
    one call is one answer whichever run made it, and a site asked in seventeen runs
    genuinely produced seventeen sets of answers. The scorecard's own note about
    per-run and per-file lines applies -- this is a per-RUN line.
    """
    def merge(a: Mapping[str, int], b: Mapping[str, int]) -> dict[str, int]:
        total = collections.Counter(a)
        total.update(b)
        return dict(total.most_common())

    return SiteTally(
        site=left.site,
        outcomes=merge(left.outcomes, right.outcomes),
        reasons=merge(left.reasons, right.reasons),
        refusals=merge(left.refusals, right.refusals),
        pre_call=merge(left.pre_call, right.pre_call),
        failures=merge(left.failures, right.failures),
    )
