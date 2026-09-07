# src/facts/anchor_statements.py
"""`104` R-135: which readings are an anchor document STATING what a course is called.

**This module decides nothing about what a course is.** It records that one line of one
document, in a document that is teaching the course, printed a course code. It stores a
CITATION and never text: the stating file, its content hash, and P4's observation key.
What that line says is delivered to the model by the release path, from the document,
under P7's gate -- so the words the model reads are the document's own and this module
never holds a copy of them.

**Why it holds no text and no mapping.** The product constitution's first rule: *"LLM
decides, code delivers. Never hardcode domain knowledge: no alias tables, no equivalence
maps, no sorting rules. Reconciliation, naming, and tree structure are model decisions.
Code extracts, stores, packages, and presents inputs."* An earlier draft of this row
built the forbidden thing -- a per-corpus table mapping `Data Structures` to `W3134`,
consulted by the normalisers, with ties broken by sort order. It is gone. Deciding that
two spellings are one course is site C's own sentence -- *"two spellings can be one
thing ... yours to judge from the evidence"* -- and the defect this module addresses is
that the evidence never arrived.

**Two refusals, and each is structural rather than a judgement.**

* *A statement is read from the document, never from its name.* Only readings the
  caller's `reads_in_document` predicate admits, which in this deployment is a SPAN
  inside `body` or `heading`. `filename`, `path`, `title` and every `metadata:*` zone
  are outside it by construction, so a folder called `Data Structures` can never make
  itself the evidence for what `Data Structures` means.
* *A reading is a course code only if the deployment's own rule says so.* `is_code` is
  the caller's, and it is the rule's asserting pattern rather than the wider shape the
  product reads everywhere.

**There was a third and it is GONE, removed on the measurement rather than on the
argument.** It required an anchor word -- `syllabus`, `registrar`, `enrolled in` --
beside the code, on the reasoning that "a homework sheet prints `W3134` beside `Problem
Set 4`; the syllabus prints it beside the course's own name". Run against the owner's
own corpus: 9283 observations, 1554 of them read from inside a document, 106 passing
`is_code`, and ALL 106 refused by that gate. Three files in the whole corpus mention any
anchor term anywhere in their text and not one of those prints a code. So the table held
zero rows, no dossier ever carried context, and the premise the gate was built on --
that some document here prints `COMS W3134: Data Structures` -- was never true of this
corpus. What it holds is 44 files that print a course code in their own text.

**So a statement is any line of a document's own text that prints a course code**, and
which of those lines mean the same course is the model's judgement at sites A and C.
That is the constitution's first rule read straight: a gate refusing 106 of 106 was code
deciding, badly, a question the model was already asked to decide. What bounds how many
reach one call is the release cap the call already has, not a vocabulary.

**Two citations per statement, and the second is the point.** The identifier reading is
cited because it is what made the line findable. The reading that CONTAINS it -- the
heading, when P4 emitted one over the same container path -- is cited beside it, because
that is the reading whose words are `COMS W3134: Data Structures` rather than `W3134`.
Which of the two the gate will actually release is P7's decision and not this module's;
both are offered so the decision has something to make.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Callable

from evidence_shape.canonical import sha256_of
from evidence_shape.locator import serialize_container_path
from evidence_shape.store import (
    DERIVED_NAMESPACE, line_reading_for, record_observation,
)

from facts.evidence import cite, observations_for_version
from facts.schema import ANCHOR_STATEMENTS_TABLE

__all__ = [
    "AnchorStatement",
    "anchor_statements_for",
    "record_anchor_statements",
]


@dataclass(frozen=True, slots=True)
class AnchorStatement:
    """One anchor document's line, as a citation and never as a copy of its words.

    **The file is the STATING file and never the "anchor file".** `anchor_file_id` is a
    group handle in this codebase -- P9's anchor is the file a GROUP is built around --
    and `tests/p6/test_p6_no_invention.py`'s OQ9 guard refuses any callable in `facts`
    that accepts one, because §4.1 forbids copying a group's facts onto its sparse
    members. This record is not group-derived: it comes from one file's own readings of
    its own words, and nothing here knows what a group is. The name says so.

    `code_evidence_ref` is the identifier reading; `line_evidence_ref` is the reading
    that contains it, or `None` when P4 emitted no such reading. A consumer offers both
    to the release and lets the gate choose; a consumer that reads `canonical_code` and
    decides something about a course's identity from it has stepped outside this
    module's promise.
    """

    stating_file_id: str
    stating_content_hash: str
    canonical_code: str
    code_evidence_ref: str
    line_evidence_ref: str | None


def _statement_identity(*, scan_run_id: str, stating_content_hash: str,
                        code_evidence_ref: str) -> str:
    """Content-addressed, so a re-scan rewrites a row rather than adding a second and
    two databases that saw the same corpus hold the same ids (§8.5's replay)."""
    return sha256_of("facts.anchor_statements", scan_run_id, stating_content_hash,
                     code_evidence_ref)


#: The extractor name the MINTED line reading carries. Its own, and never the name of
#: the extractor that read the document: this reading was not produced by that pass, and
#: `observation_key` hashes the extractor name, so a minted line and a real one are two
#: different handles even over identical characters.
#:
#: IN P4'S DERIVED NAMESPACE, which is what makes `evidence_shape.store.is_derived`
#: true of it. `104` R-135's ruling: a minted line is an addressable copy for citation
#: and for another file's context, and never evidence about the file it was cut from.
#: The rule pass and the recogniser skip it through that one predicate; the release
#: path does not, because the words are the file's own.
LINE_EXTRACTOR: str = DERIVED_NAMESPACE + "anchor_statements.line"

#: This producer's version, moved when what it mints changes. `observation_key` does NOT
#: hash it (MINOR 8), so a bump re-reads the same corpus into the same handles.
LINE_EXTRACTOR_VERSION: str = "1.0.0"


def _containing_span_reading(observation, siblings) -> str | None:
    """The reading that CONTAINS this one, by container path and span. Structural.

    `extractors/pdf.py` emits a heading twice over: once as the whole heading, whose
    `raw_value` is the line, and once per identifier inside it. Both carry the same
    `container_path`, so "the reading this one sits inside" is a comparison of spans
    within one container and needs no text and no parsing.

    The SHORTEST containing reading wins, so a heading is preferred over a page when a
    document offers both. Ties cannot happen: two readings with the same span and the
    same container are the same reading.
    """
    own = observation.location.text_span
    if own is None:
        return None
    path = serialize_container_path(observation.location.container_path)
    best = None
    for other in siblings:
        if other.observation_key == observation.observation_key:
            continue
        span = other.location.text_span
        if span is None:
            continue
        if serialize_container_path(other.location.container_path) != path:
            continue
        if span.start <= own.start and span.end >= own.end:
            width = span.end - span.start
            if best is None or width < best[0]:
                best = (width, cite(other))
    return None if best is None else best[1]


def _minted_line(conn: sqlite3.Connection, observation, *,
                 reads_in_document: Callable[[str], bool]) -> str | None:
    """Mint the LINE this code sits on as a reading of its own, and cite it.

    **Measured, which is why this exists.** On the owner's corpus the citation shapes
    were `code: body span` 91 and `line: none` 91 against `code: heading span` 8 and
    `line: heading span` 8. `extractors/pdf.py` gives a heading its own text unit and a
    reading over it, so a PDF heading has a containing reading to cite; a `.txt` or
    `.docx` body is ONE reading with no span, which `_containing_span_reading` skips,
    so 91 of 99 statements carried no line at all. `anchor_context_observations` then
    passed over every one of them, and the first 18 fresh `A_fact` dossiers of a live
    run carried 125 released items, all `direct-anchor` and not one context item. The
    whole path was built and unreachable.

    **A NEW READING, never an edit of an existing one.** The code's own reading stays
    exactly as P4 wrote it. `evidence_shape.store.line_reading_for` builds the second
    reading -- P4 holds the unit's text and the repo keeps it that way, `104` R-135's
    producer is not one of the three packages `tests/p7/test_p7_no_invention.py` allows
    to bind a materialiser -- and this module decides whether it may exist and records
    it, carrying `LINE_EXTRACTOR` as its provenance so nothing later reads it as
    something a document extractor found.

    **Two refusals, and neither is a judgement.** P4 returns `None` when there is no
    stored unit to read the line back from and when the line is the code's own
    characters; either way the caller offers the code span instead, which
    `cli.anchor_context_observations` says in its own words. And a locator the CALLER's
    `reads_in_document` does not admit is refused here -- the minted span keeps the
    code's zone and container path, so this can only fire if the code itself was
    outside, which `record_anchor_statements` already refused, and it is asked anyway
    because "never mint over a filename, a path or a title" is a rule this module must
    not be able to break by accident.

    Recording is idempotent: the handle is content-addressed, so a re-scan finds the
    row it wrote last time and cites it rather than writing a second.
    """
    minted = line_reading_for(conn, observation,
                              extractor_name=LINE_EXTRACTOR,
                              extractor_version=LINE_EXTRACTOR_VERSION)
    if minted is None or not reads_in_document(minted.locator):
        return None
    key = minted.observation_key
    seen = conn.execute(
        "SELECT 1 FROM evidence WHERE observation_key = ? AND file_id = ? LIMIT 1",
        (key, observation.file_id)).fetchone()
    if seen is None:
        record_observation(conn, minted)
    return key


def _containing_line(conn: sqlite3.Connection, observation, siblings, *,
                     reads_in_document: Callable[[str], bool]) -> str | None:
    """The reading whose words are the whole LINE: the document's own, or a minted one.

    A reading the document already carries is always preferred, so a PDF heading cites
    the heading `extractors/pdf.py` wrote and nothing is invented for it. Minting is
    what happens when the containing reading has no span to be found by, which on this
    corpus is 91 statements of 99.
    """
    found = _containing_span_reading(observation, siblings)
    if found is not None:
        return found
    return _minted_line(conn, observation, reads_in_document=reads_in_document)


def record_anchor_statements(conn: sqlite3.Connection, *, scan_run_id: str,
                             file_versions: Sequence[tuple[str, str]],
                             is_code: Callable[[str], bool],
                             canonical: Callable[[str], str],
                             reads_in_document: Callable[[str], bool],
                             ) -> tuple[str, ...]:
    """Record every line of the corpus that prints a course code. Returns the ids.

    A CORPUS producer, which is why it is not a `FactResolver` stage: what one document
    states is about every other file of that course, and a stage asked about one file
    version at a time cannot see it. `facts.families` runs at the same place for the
    same reason.

    **`anchor_terms` is gone**, and the module docstring carries the measurement that
    removed it: it refused 106 of the 106 readings this corpus has, because no document
    here prints an anchor word beside a code. A gate that refuses everything is not a
    narrowing, and deciding which lines name one course is the model's.

    Nothing is authored here. The predicate that says a reading is a course, its
    canonicaliser and the predicate that says which readings are the document's own
    words are all the caller's, exactly as `Rule` takes its three. `facts.rules` states
    the rule this follows: "Every other domain's terms arrive on the `Rule`, because the
    SPEC defers them."

    No `unresolved` row is ever written. A statement is not a FIELD anybody attempted,
    and B7's abstention is a record about a field.
    """
    written: list[str] = []
    for file_id, content_hash in sorted(set(file_versions)):
        observations = observations_for_version(conn, file_id, content_hash)
        for observation in observations:
            if not reads_in_document(observation.locator):
                continue
            reading = " ".join(observation.raw_value.split())
            if not is_code(reading):
                continue
            code = canonical(reading)
            if not code:
                continue
            statement_id = _statement_identity(
                scan_run_id=scan_run_id, stating_content_hash=content_hash,
                code_evidence_ref=cite(observation))
            conn.execute(
                f"INSERT OR REPLACE INTO {ANCHOR_STATEMENTS_TABLE} "
                "(statement_id, scan_run_id, stating_file_id, stating_content_hash, "
                " canonical_code, code_evidence_ref, line_evidence_ref) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (statement_id, scan_run_id, file_id, content_hash, code,
                 cite(observation),
                 _containing_line(conn, observation, observations,
                                  reads_in_document=reads_in_document)))
            written.append(statement_id)
    return tuple(written)


def anchor_statements_for(conn: sqlite3.Connection, scan_run_id: str, *,
                          stating_file_ids: Sequence[str] = (),
                          ) -> tuple[AnchorStatement, ...]:
    """Every statement of one scan, or of the named anchor files within it.

    Ordering is imposed and never inherited: P4's reads are in insertion order, which is
    a property of one database rather than of the corpus, and §8.5 replays a run and
    compares it.

    EVERY statement is returned, including two that name different codes. Choosing
    between them is the model's, and a reader that took the first would be the sorting
    rule the constitution forbids.
    """
    query = (f"SELECT stating_file_id, stating_content_hash, canonical_code, "
             f"code_evidence_ref, line_evidence_ref FROM {ANCHOR_STATEMENTS_TABLE} "
             "WHERE scan_run_id = ?")
    parameters: list[object] = [scan_run_id]
    if stating_file_ids:
        names = sorted(set(stating_file_ids))
        query += f" AND stating_file_id IN ({', '.join('?' * len(names))})"
        parameters.extend(names)
    query += " ORDER BY canonical_code, stating_file_id, code_evidence_ref"
    return tuple(
        AnchorStatement(
            stating_file_id=row["stating_file_id"],
            stating_content_hash=row["stating_content_hash"],
            canonical_code=row["canonical_code"],
            code_evidence_ref=row["code_evidence_ref"],
            line_evidence_ref=row["line_evidence_ref"])
        for row in conn.execute(query, tuple(parameters)).fetchall())
