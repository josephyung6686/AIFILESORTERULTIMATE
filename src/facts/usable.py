# src/facts/usable.py
"""M11 — `no_usable_facts`, the recorded pass, and the ordering guard (§2.2, §2.7).

§2.2 permits targeted OCR on a PDF with a non-empty but BROKEN text layer only when
its stored evidence yields no usable facts. This module is that verdict.

    "A file that technically produces text but yields no usable facts may receive
     targeted OCR as a fallback ... The system should not use unreliable global
     language-quality checks that incorrectly punish multilingual or
     mathematics-heavy documents."          -- §2.2

    "A document with a non-empty but unusable text layer should receive OCR only when
     its extracted evidence fails to produce usable facts, not because a broad quality
     heuristic says the text looks unusual."                              -- §2.7

**DO NOT WIRE THIS INTO legacy `run_wave2`.** `extractors.ocr_policy.text_layer_state`
consults `no_usable_facts` for every document whose run produced any non-empty text
unit, inside the orchestrator's single extraction loop, before P4 has been handed the
observations at all. P6 Task 26 -- the caller restructure -- is CUT (D5), so nothing
reorders that. `FactPassNotRun` is a `ContractViolation` and the orchestrator re-raises
those by name, so passing this verdict to `run_wave2` today would END THE SCAN on the
first text-bearing PDF. That caller keeps
`orchestrator.TARGETED_OCR_UNAVAILABLE`. The production P1–P7 composition instead
binds this persisted verdict after its first P6 pass; the threshold remains an
explicit injected authority.

**Computed from the fact tables and nothing else.** The negative is load-bearing and
the design states it twice. A10 names the failure literally --
`triggered_by: "language_quality_heuristic"` is its forbidden value -- so this module
reads `facts_for_file` and `unresolved_for_file` and touches no text unit, no
character count and no language.

**Why it raises.** Returning `False` for an unrecorded pass would be safe and would
hide the bug forever -- the current stub does exactly that, which is why the defect
survived to now. Returning `True` is the corpus-wide OCR the SPEC names. Raising is
the only option that turns a wrong call sequence into a failing test, and it makes the
SPEC's named disaster UNREACHABLE rather than unlikely: `True` is not a value the
unrecorded-pass branch can produce.

**The pass record is a fifth table and no neighbour reads it.** The four P6 owns are
§3's published records -- `fields`, `values`, `file_facts`, `unresolved`. This one is
bookkeeping, carries no claim about any file, and creates none of anyone else's. It
has no timestamp on purpose: it answers a membership question, and a time column would
invite a caller to reason about "the latest pass", which is an ordering P6 refuses to
infer anywhere else.
"""
from __future__ import annotations

import json
import sqlite3
from typing import Callable, Sequence

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.vocabulary import ANALYSIS_TIERS, check

from extractors.failure import ContractViolation

from facts.file_facts import facts_for_file
from facts.schema import FACT_PASSES_DDL, FACT_PASSES_TABLE
from facts.unresolved import unresolved_for_file

class FactPassNotRun(ContractViolation):
    """The verdict was consulted before the pass that defines it.

    The base class is deliberate. A plain `Exception` raised from inside a
    `no_usable_facts` callable is caught by `orchestrator._extract_one`'s broad
    `except Exception` and becomes one `failed` extraction run: the file recorded as
    unreadable, the scan continuing, and the ordering defect turned into a
    data-quality mystery. The orchestrator re-raises `ContractViolation` by name for
    the reason its own comment gives -- "a ContractViolation is not about this file at
    all, so recording it as the file's failure would be a false statement about the
    corpus AND would hide the defect it exists to surface" -- which is exactly this
    exception's case.
    """


def create_fact_passes(conn: sqlite3.Connection) -> None:
    """Create the pass record, alone. Idempotent.

    `facts.schema.create_facts_schema` already creates this table -- the DDL is in
    `_TABLE_DDL` and `FACT_PASSES_DDL` is imported from there -- so no production
    caller needs this. It stays for a test that wants the one table without the rest.
    An earlier docstring here claimed the schema module CALLED it, which it never did:
    the table then existed only where a test fixture had made it, and the whole point
    of `FactPassNotRun` -- a `ContractViolation` the orchestrator re-raises by name --
    was defeated in production by `sqlite3.OperationalError: no such table`, which
    `_extract_one`'s broad `except Exception` records as the file's own failure.
    """
    conn.execute(FACT_PASSES_DDL)


def record_pass(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                analysis_tiers: frozenset[str]) -> None:
    """A P6 deterministic pass over this file version, at these tiers, completed.

    Idempotent: `pass_id` is derived from the three values, so recording the same
    pass twice writes one row. The tiers are checked against P4's published tuple
    rather than stored as given -- a tier P4 does not publish is a spelling error
    that would make the termination lookup silently wrong. Every tier is checked
    before anything is written, so a refused call leaves no partial row behind.
    """
    for tier in sorted(analysis_tiers):
        check(tier, ANALYSIS_TIERS, name="analysis_tier")
    tiers = canonical_json(sorted(analysis_tiers))
    pass_id = sha256_of(canonical_json([file_id, content_hash, tiers]))
    conn.execute(
        f"INSERT OR IGNORE INTO {FACT_PASSES_TABLE} "
        "(pass_id, file_id, content_hash, analysis_tiers) VALUES (?, ?, ?, ?)",
        (pass_id, file_id, content_hash, tiers))


def passes_for(conn: sqlite3.Connection, *, file_id: str,
               content_hash: str) -> tuple[frozenset[str], ...]:
    """Every recorded pass over this file version, as its set of analysis tiers.

    Ordered by `pass_id` so the sequence is a property of the values rather than of
    insertion order, which P6 inherits from nothing. This is also the termination
    lookup: "have we already tried OCR for this content hash" is
    `any("ocr" in tiers for tiers in passes_for(...))`, a fact on disk rather than a
    flag someone remembers to set.
    """
    rows = conn.execute(
        f"SELECT analysis_tiers FROM {FACT_PASSES_TABLE} "
        "WHERE file_id = ? AND content_hash = ? ORDER BY pass_id",
        (file_id, content_hash)).fetchall()
    return tuple(frozenset(json.loads(row["analysis_tiers"])) for row in rows)


def no_usable_facts_for(
        conn: sqlite3.Connection, *,
        usable_threshold: Callable[[Sequence[sqlite3.Row], Sequence[sqlite3.Row]],
                                   bool]) -> Callable[[str, str], bool]:
    """Done-means 28. The exact `Callable[[str, str], bool]` P5 already requires.

    `usable_threshold` receives the two row lists for the version -- the facts, then
    the `unresolved` rows -- and returns **True when the stored facts ARE usable**.
    This function returns the negation, which is what §2.2 asks for. Which facts count
    and how many is Deferred by name ("The `no_usable_facts` threshold -- M11, P5
    OQ1"), so it is a required keyword with no default and nothing here chooses.

    The `unresolved` rows are passed because the SPEC makes them evidence FOR the
    verdict, not merely the absence of facts: a version whose every attempted field
    ended in a recorded refusal is a version whose evidence yielded nothing, and that
    is a stronger statement than an empty fact list.

    **Read the module docstring before passing this anywhere.**
    """

    def no_usable_facts(file_id: str, content_hash: str) -> bool:
        if not passes_for(conn, file_id=file_id, content_hash=content_hash):
            raise FactPassNotRun(
                f"no P6 deterministic pass is recorded for {file_id!r} at "
                f"{content_hash!r}; §2.2's verdict is defined only after that pass "
                "has completed, and answering here would be a statement about rows "
                "that do not exist yet")
        return not usable_threshold(
            facts_for_file(conn, file_id, content_hash),
            unresolved_for_file(conn, file_id, content_hash))

    return no_usable_facts


def targeted_ocr_needed_for(
        conn: sqlite3.Connection, *,
        usable_threshold: Callable[[Sequence[sqlite3.Row], Sequence[sqlite3.Row]],
                                   bool]) -> Callable[[str, str], bool]:
    """Return P6's completed-pass decision for one targeted OCR attempt.

    The existing usability verdict owns whether the stored P6 result is usable and
    raises when no pass completed. The pass record owns whether OCR evidence was
    already included. Combining those two authorities makes retry termination a
    property of persisted inputs rather than caller memory.
    """
    no_usable_facts = no_usable_facts_for(
        conn, usable_threshold=usable_threshold)
    _filesystem_tier, _native_tier, ocr_tier, _llm_tier = ANALYSIS_TIERS

    def targeted_ocr_needed(file_id: str, content_hash: str) -> bool:
        if not no_usable_facts(file_id, content_hash):
            return False
        return not any(
            ocr_tier in tiers
            for tiers in passes_for(
                conn, file_id=file_id, content_hash=content_hash))

    return targeted_ocr_needed
