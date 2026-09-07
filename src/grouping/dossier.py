# src/grouping/dossier.py
"""The bounded, reference-only group dossier. P9 assembles; P8 materialises.

Nothing here reaches a model, a gate or a released span. This module selects
REFERENCES — observation keys, file version identities, typed edges — and records
what it left out. `build_dossier_request` in the P8 seam turns this record into
P8's `DossierRequest`; P8 alone materialises released evidence through P7 and
constructs a `Dossier`.

Three rules carry the weight.

**Anchor and candidate files are separate arrays and are never merged.** The model
must be able to say a group is coherent while still marking particular members
uncertain, and it can only do that if direct evidence and inferred context arrive
apart.

**Nothing is dropped silently.** A file withheld for privacy, a file cut by the
neighbourhood cap and a file cut by a budget are three different omissions with
three different fields, and every one is present-and-named rather than absent.
Silence about a dropped file is the failure, not the drop.

**P9 runs no token ladder.** It measures no dossier tokens, summarises no fact,
drops no excerpt by a budget, splits no request and creates no budget-deferred
decision. M9's summarize -> preserve anchors -> split/defer ladder is P8's
`run_call`, under P1's `model.max_dossier_tokens_per_call` ceiling.
"""
from __future__ import annotations

import dataclasses
import hashlib
import sqlite3
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from evidence_shape.canonical import canonical_json
from evidence_shape.store import observations_by_key
from facts.read_surface import proposal_eligible
from privacy.classification import UNREADABLE_UNCLASSIFIED, resolve_class

from grouping.config import ConfigurationRequired, GroupingLimits
from grouping.graph import LocalEvidenceGraph
from grouping.records import (
    AnchorFact,
    BudgetSummary,
    CandidateGroupDossier,
    Conflict,
    DossierFile,
    Excerpt,
    Group,
    Omissions,
    PrivacySummary,
)
from grouping.seeds import first_evidence_ref
from grouping.vocabulary import CONTEXT_SUPPORTED, DIRECT_ANCHOR

#: What P3 records when it cannot name a format. P9 asserts nothing about a file
#: it cannot describe.
UNCLASSIFIED_DOCUMENT_TYPE: str = "unclassified"

#: `ActiveSchemaFor` STOOD HERE AND IS GONE (`104` R-09). It was demanded of every
#: caller, checked callable below, and invoked by no line in `src/`: assembly reads
#: the group's own anchor facts and never asked which fields the situation's schema
#: carries. Measured before removing it -- the three P9 suites that supplied it
#: patched to hand in a callable that raises on any call, 57 of 57 passing. What
#: actually decides whether a fact may anchor a group is `seeds.ANCHOR_STATES`, and
#: that bar is field-independent, so no schema derivation could have moved it.
SignalEvaluatorFor = Callable[[str], object]
ClassificationStore = Callable[[str, str], object]


@dataclass(frozen=True)
class DossierRefused:
    """No dossier, and the reason. Never a dossier with the reason missing."""

    group_id: str
    reason: str
    withheld: tuple[str, ...]


def _require_knowledge(signal_evaluator_for, classification_store) -> None:
    missing = [
        name for name, value in (
            ("signal_evaluator_for", signal_evaluator_for),
            ("classification_store", classification_store),
        )
        if not callable(value)
    ]
    if missing:
        raise ConfigurationRequired(
            f"{missing} were not supplied. P9 authors no signal evaluator and no "
            "handling class; without them there is no category to propose, and "
            "inventing one is how a group acquires a name nobody can trace."
        )


def _file_row(conn: sqlite3.Connection, file_id: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT content_hash, detected_format FROM files WHERE file_id = ?",
        (file_id,),
    ).fetchone()


def _excerpts_for(
    conn: sqlite3.Connection, keys: Sequence[str], *, limit: int, file_id: str,
) -> tuple[Excerpt, ...]:
    """One short excerpt per cited observation key, in the order cited.

    A key that resolves to nothing is skipped rather than carried. P8 verifies a
    citation by resolving it, so an excerpt whose key resolves to nothing would be
    a quotation the model could not be held to.

    THE FILE'S OWN OBSERVATION, OR NONE, AND THE CALLER NOW ASKS FOR IT BY NAME.
    An `AnchorFact` shared by several files used to carry ONE `observation_key`,
    the observation of whichever file stated the value first; attached to a second
    file that key is a quotation from somewhere else, and P7's gate resolves every
    requested item to the file it belongs to and raises `UnresolvableSpan` when
    that file is outside the request's target -- which it is whenever the first
    file was withheld or bounded out of the graph. Measured on a 52-file Downloads
    with a local model: the whole run died with that traceback after 37 minutes of
    A-site calls, at the first B dossier, because two cover letters cited a job
    posting's `Summer2026`.

    `AnchorFact.key_for` is the fix at the cause (`104` R-97): the fact carries one
    key per stating file, so the caller hands this function the file's OWN key and
    a shared fact no longer costs the second file its excerpt. The narrowing below
    stays as the guard it always was -- a key that resolves to no observation of
    this file is skipped, whoever chose it -- so the release can never be asked to
    resolve a span to a file the request did not name.
    """
    found: list[Excerpt] = []
    for key in dict.fromkeys(keys):
        observations = [item for item in observations_by_key(conn, key)
                        if item.file_id == file_id]
        if not observations:
            continue
        observation = observations[0]
        span = observation.location.text_span
        found.append(Excerpt(
            observation_key=key,
            location=observation.location.zone,
            text=observation.raw_value[:limit],
            # The observation's OWN span, `None` included. Not derived from
            # `text` above: `text` is truncated to `limit`, so a length taken from
            # it is a span the observation never had.
            text_span=None if span is None else (span.start, span.end),
        ))
    return tuple(found)


def _facts_for(group: Group, file_id: str) -> tuple[AnchorFact, ...]:
    return tuple(fact for fact in group.anchor_facts if file_id in fact.file_ids)


def _group_level_facts(conn: sqlite3.Connection, *, file_id: str,
                       content_hash: str,
                       fields: frozenset[str]) -> tuple[AnchorFact, ...]:
    """What one ANCHOR file states at the fields the group carries. `104` §11.2 (2).

    `00`:57 is the whole argument: the syllabus states `PHYS1401`, `Columbia` and
    `Spring 2026`, and the sparse homework beside it states none of them. The
    course's school and term are facts about the COURSE, so they belong in the
    dossier as the group's own anchors rather than as a question asked of every
    file -- which is what produced twenty `school` values and five essays under a
    high school (`104` §11.1).

    **Proposal-eligible only, which is `00`:42's bar and not a new one.** A weak
    reading "may remain a possible clue for review; it must not quietly become a
    folder proposal", and a group-level anchor IS a folder proposal for every
    member of the group -- so the same read P10 uses for a per-file level
    (`read_surface.proposal_eligible`) is the read used here. A `possible` school
    on the syllabus stays a clue on the syllabus.

    **The anchor file, and only the anchor file.** A candidate is in the
    neighbourhood because something retrieved it; what it says about a school is
    not what the course's school is. `assemble_group_dossier` calls this for the
    files that state the group's basis directly and for no others.
    """
    if not fields:
        return ()
    found = []
    for row in proposal_eligible(conn, file_id=file_id, content_hash=content_hash):
        if row["field_key"] not in fields:
            continue
        # THE CITATION, taken the way `seeds.first_evidence_ref` takes it: a fact
        # row carries `evidence_refs` as P4 keys and no `observation_key` column,
        # and `AnchorFact` requires one because "a fact that cites nothing cannot
        # be checked or replayed". A `user_confirmed` value legitimately cites no
        # observation and is skipped rather than given an invented handle -- the
        # person's own answer reaches the tree through P6 either way.
        cited = first_evidence_ref(row)
        if not cited:
            continue
        found.append(AnchorFact(
            field=row["field_key"],
            # THE CANONICAL VALUE, which is what `preferred_value_for` reads at
            # P10 and what a level is keyed on. A display label is words for a
            # person and would make the dossier and the tree disagree about which
            # value two anchors share.
            value=row["canonical_value"],
            file_ids=(file_id,),
            reliability_state=row["reliability_state"],
            observation_key=cited))
    return tuple(found)


def _merged(facts: Sequence[AnchorFact]) -> tuple[AnchorFact, ...]:
    """One entry per (field, value), naming every file that states it.

    Two syllabi stating the same term are one fact with two files behind it, which
    is `AnchorFact`'s own meaning of `file_ids` -- "the number of files that
    INDEPENDENTLY state the basis value" -- and two entries would understate that
    support to the model exactly the way `_group_for`'s one-tuple understated it
    to P10. Two anchors stating DIFFERENT schools stay two facts, because that
    disagreement is what the model is being shown.
    """
    merged: dict[tuple[str, str], AnchorFact] = {}
    for fact in facts:
        key = (fact.field, fact.value)
        held = merged.get(key)
        if held is None:
            merged[key] = fact
            continue
        # The two tuples move together or they pair a file with another file's
        # citation, which is the whole of `104` R-97. Built as a mapping and
        # unzipped rather than sorted twice.
        cited: dict[str, str | None] = dict(zip(held.file_ids,
                                                held.observation_keys))
        cited.update(zip(fact.file_ids, fact.observation_keys))
        ordered = tuple(sorted(cited))
        merged[key] = dataclasses.replace(
            held, file_ids=ordered,
            observation_keys=tuple(cited[one] for one in ordered))
    return tuple(merged.values())


def _why_retrieved(graph: LocalEvidenceGraph, file_id: str) -> str:
    """The channel that brought this file, named.

    A reviewer has to be able to tell a shared validated fact from a semantic
    guess; without the channel both read as "it was in the neighbourhood".
    """
    kinds = sorted({
        edge.edge_type for edge in graph.edges
        if edge.to_file_id == file_id and not edge.hub_suppressed
    })
    return "+".join(kinds) if kinds else graph.seed_file_id


def _fingerprint(group_id: str, anchors, candidates, edges) -> str:
    """A stable hash of the references assembled, for cache keying and replay.

    Content-derived rather than random: two assemblies over the same references
    are the same dossier, and a replay has to be able to say so. `created_at` is
    deliberately not in it, or the same dossier assembled twice would be two.
    """
    body = canonical_json({
        "anchors": [
            [item.file_id, item.content_hash,
             [excerpt.observation_key for excerpt in item.excerpts]]
            for item in anchors
        ],
        "candidates": [
            [item.file_id, item.content_hash,
             [excerpt.observation_key for excerpt in item.excerpts]]
            for item in candidates
        ],
        "edges": sorted(edge.edge_id for edge in edges),
        "group_id": group_id,
    })
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def assemble_group_dossier(
    conn: sqlite3.Connection,
    *,
    group: Group,
    graph: LocalEvidenceGraph,
    limits: GroupingLimits,
    signal_evaluator_for: SignalEvaluatorFor | None,
    classification_store: ClassificationStore | None,
    group_level_fields: frozenset[str] = frozenset(),
    conflicts: Sequence[Conflict] = (),
    created_at: str,
) -> CandidateGroupDossier | DossierRefused:
    """One reference-only dossier over one bounded graph.

    Returns `DossierRefused` when withholding leaves no direct evidence: a group
    with no anchor file has nothing for the model to judge, and building the record
    anyway would put an empty question in front of a paid model call.

    `group_level_fields` are the fields `104` §11.2 step 2 routes HERE instead of
    to site A: the course's school and term, which `00`:57 puts on the syllabus
    anchor. They join the anchors' `key_facts` and the dossier's, so the model
    judging this group's coherence can see what the group is a course AT and IN.
    They do NOT decide who is an anchor -- `stating` below is still the group's
    basis and nothing else, because a file that names a school and not the course
    is not an independent statement of the course.

    Empty is the ordinary answer: 22 of the 23 schemas name no group-level role.
    """
    _require_knowledge(signal_evaluator_for, classification_store)

    stating = {
        file_id for fact in group.anchor_facts for file_id in fact.file_ids
    }
    #: `104` §11.2 step 2, collected as the anchors are walked and merged once at
    #: the end so two syllabi stating one term are one fact with two files behind
    #: it rather than two facts each claiming one.
    carried: list[AnchorFact] = []
    anchors: list[DossierFile] = []
    candidates: list[DossierFile] = []
    withheld: list[str] = []
    classes: set[str] = set()

    for file_id in graph.file_ids:
        row = _file_row(conn, file_id)
        content_hash = row["content_hash"] if row is not None else ""
        handling_class = resolve_class(classification_store(file_id, content_hash))
        classes.add(handling_class)
        if handling_class == UNREADABLE_UNCLASSIFIED:
            # Marked and counted, never opened. §8.4 requires classification before
            # escalation, so an unclassified file is withheld -- and named in
            # `omissions`, so a later reader shows it as present-but-untouched
            # rather than as a file that was never there.
            withheld.append(file_id)
            continue
        is_anchor = file_id in stating
        facts = _facts_for(group, file_id)
        if is_anchor:
            # THE ANCHOR'S OWN GROUP-LEVEL FACTS, added to what it already states
            # about the basis. Carried on the file as well as on the group so the
            # model can see WHICH anchor said the school, which is the difference
            # between one syllabus's answer and a neighbourhood's consensus.
            level_facts = _group_level_facts(
                conn, file_id=file_id, content_hash=content_hash,
                fields=group_level_fields)
            carried.extend(level_facts)
            facts = facts + level_facts
        item = DossierFile(
            file_id=file_id,
            content_hash=content_hash,
            document_type=(
                row["detected_format"] if row is not None and row["detected_format"]
                else UNCLASSIFIED_DOCUMENT_TYPE
            ),
            basis=DIRECT_ANCHOR if is_anchor else CONTEXT_SUPPORTED,
            key_facts=facts,
            excerpts=_excerpts_for(
                # THIS FILE'S citation for each fact it states, never the fact's
                # first stating file's (`104` R-97). `key_for` answers `None` for
                # a file that cites nothing of its own -- a `user_confirmed`
                # value has no reading behind it -- and none is offered for it.
                conn, [key for key in (fact.key_for(file_id) for fact in facts)
                       if key],
                # How short a short excerpt is decides how much of a file
                # reaches a model. That is a policy, and it arrives injected.
                limit=limits.max_excerpt_characters, file_id=file_id),
            why_retrieved=None if is_anchor else _why_retrieved(graph, file_id),
        )
        (anchors if is_anchor else candidates).append(item)

    if not anchors:
        return DossierRefused(
            group_id=group.group_id,
            reason=(
                "every file carrying direct evidence was withheld; a dossier with "
                "no anchor has nothing for the model to judge"
                if withheld else
                "no file in the graph states the group's basis directly"
            ),
            withheld=tuple(withheld),
        )
    if not any(item.excerpts for item in (*anchors, *candidates)):
        # Anchors, and not one quotation among them. Since `104` R-97 a shared
        # `AnchorFact` carries each stating file's own key, so this is no longer
        # what a withheld first file costs -- it is what a group of
        # `user_confirmed` anchors looks like: every file states the basis by the
        # person's word and cites no reading of its own. A request with
        # no items is what `ModelCallRequest` refuses to construct -- measured:
        # `MalformedRequest: a request with no items has nothing to release`
        # ended a 48-minute local-model run at this site. Refused HERE, as a
        # dossier that names why, so P9 records "not judged" and moves on.
        return DossierRefused(
            group_id=group.group_id,
            reason=(
                "no file in the graph carries an observation of its own for the "
                "group's basis, so there is no excerpt a release could resolve"
            ),
            withheld=tuple(withheld),
        )

    capped = tuple(
        line.split(": ", 1)[1] for line in graph.omissions if ": " in line
    )
    fingerprint = _fingerprint(group.group_id, anchors, candidates, graph.edges)
    return CandidateGroupDossier(
        dossier_id=fingerprint,
        group_id=group.group_id,
        proposed_basis=group.proposed_basis,
        anchor_files=tuple(anchors),
        candidate_files=tuple(candidates),
        typed_edges=graph.edges,
        # THE BASIS FIRST, THEN WHAT THE GROUP CARRIES. `group.anchor_facts` is
        # untouched on the row -- the group's identity, its label, its learning key
        # and its category are all read off that tuple, and widening it would
        # rename the group after a school. What widens is the DOSSIER, which is
        # what `104` §11.2 step 2 asks for: route them "to site B's dossier as
        # anchor facts".
        key_facts=group.anchor_facts + _merged(carried),
        excerpts=tuple(
            excerpt
            for item in (*anchors, *candidates)
            for excerpt in item.excerpts
        ),
        conflicts=tuple(conflicts),
        engine_flagged_outliers=(),
        omissions=Omissions(
            # P9 applies no token budget, so this stays empty by construction.
            budget_cap_dropped=(),
            privacy_redacted=tuple(withheld),
            neighbourhood_capped=capped,
        ),
        privacy=PrivacySummary(
            handling_classes=tuple(sorted(classes)),
            redactions_applied=len(withheld),
            # P7 decides at release time, which is P8's call, not this assembly.
            release_decision_ref=None,
        ),
        budget=BudgetSummary(
            token_ceiling=limits.max_dossier_tokens,
            neighbour_cap=limits.max_graph_nodes,
            files_dropped=len(capped),
        ),
        dossier_fingerprint=fingerprint,
        created_at=created_at,
    )
