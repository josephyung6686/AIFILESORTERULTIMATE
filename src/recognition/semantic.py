# src/recognition/semantic.py
"""RUNTIME. What a file MEANS, where what it SAYS matched nothing.

`detector.py` matches authored terms literally, and measured over the owner's own
199 files it classified 37 of them. The reason is not that the library is thin.
It holds 8,429 distinct authored terms, and 38.9% of them are PROSE -- an
authoring note compiled into the matchable table, of the shape *"proposal note:
none of these terms appears in 00..."*. No file can ever carry one of those as a
string. They are also, sentence for sentence, the richest description of a
situation the library contains, so literal matching throws away exactly the part
that says the most.

**The library was never wrong. The matching was.** This module reads the same
compiled rules `detector.py` reads, turns them into ANCHORS, and asks which schema
a file's own evidence is NEAREST to. It writes no term, no schema and no number of
its own: `build_schema_anchors` is a rearrangement of the shipped manifest, and
every threshold arrives from the caller.

**Nothing here computes a vector.** `SchemaSimilarity` is an injected callable
that answers "how near is this file version to each schema", and this module never
sees a float array, an encoder or a model name. That is the same seam
`detector.py` uses for its identifier patterns and for the same reason: the
DEPLOYMENT owns the model, and `pyproject.toml` keeps `dependencies` empty because
"every format reader is a caller-supplied callable, so the libraries are installed
by a deployment that chose them, never by the part that consumes their output".

FOUR RULES DO THE WORK, and every one of them exists because a similarity path can
RELEASE a file that the term path was holding shut.

**Protection is a UNION and never a REPLACEMENT.** `__call__` runs the term
detector first and returns its answer untouched. This path is reached only where
that one said nothing at all, so no protection it raises can be lowered by a
vector, and no classification it made can be second-guessed by one.

**A safety domain is never claimed, in EITHER direction.** A protect floor was
written here first, on `00`:52's rule that the four safety domains are *"detected
and protected before any cloud or automated placement decision is allowed"*, and
then measured away. Over the 199-file ground-truth corpus the four do not separate
at all: the eight hand-labelled protected files score 0.084-0.151 and sit at the
43rd to 90th percentiles of the corpus -- two of them BELOW the median -- while the
single highest safety score of all 199 belongs to a Red Cross first-aid
certificate, and an open-source `LICENSE` outranks the owner's actual HKID card.
No floor catches the eight without protecting 142 of 199 files, which is the
over-protection collapse `cli.py`'s `classifier` already records.

So `caution` is a VETO and not a floor. Near one of the four -- leading, or merely
within the caution line -- this path says nothing at all and the file keeps exactly
what the term detector gave it. It cannot protect and it cannot release, and
`__call__` raises rather than emit a record naming a safety domain, so that is
structural rather than a consequence of two numbers being ordered well.

**A vector over a filename is ONE SIGNAL.** `never_alone`, in the form a vector can
state it. Mean pooling hides how much text was pooled: a vector over 22 characters
has the same shape and the same magnitude as a vector over four pages. Measured,
`min_chars` is the one rule that separates safe from unsafe here -- the only two
protected files this path ever claimed as ordinary carry 22 and 84 characters.

**A protected container is MARKED AND COUNTED, NEVER OPENED.** Checked on P3's own
predicate before any evidence row is read and before the similarity callable is
reached. The detector guards this "because a detector's natural instinct is to open
a file to classify it"; a similarity path's instinct is worse, because it wants the
whole document rather than a word of it.

**The absolute path is not one of the file's own words.** `_matches` adopted that
refusal after `IMG_4471.jpg`, an ordinary photograph carrying no evidence of its
own, sitting in a folder called `Passport and Visa Documents`, came back
`sensitive_personal, protected=True`. A vector over the same string reaches the
same answer and leaves no term behind to explain it, so `evidence_text` applies the
identical refusal to the identical rows.

RELIABILITY IS THE FLOOR AND IS UNCHANGED. §3.13's `possible` is D11's own
description of *"free text, OCR, a filename or any unlabeled position"*, which is
exactly where a nearest neighbour lands. `classification_store.strongest` still
ranks `user_confirmed`, `direct` and `validated` above it, so a person's correction
always beats a vector and never the other way.
"""
from __future__ import annotations

import json as _json
import sqlite3
import sys as _sys
from array import array as _array
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

from pathlib import PurePath

from database_agent.files_table import get_file

from facts.domains import SCHEMA_IDS, UnknownSchema

from privacy.classification import ClassificationRecord

from scan_agent.exclusion import is_protected_container

from recognition.detector import RELIABILITY, Handling
from recognition.rules import RecognitionRules
from recognition.vocabulary import (
    ABSTENTION_REASONS, SAFETY_DOMAIN_IDS, UnknownAbstentionReason,
)

#: The two outcomes only a SIMILARITY can reach, added to the ones the detector
#: already publishes rather than beside them. A second tuple holding the same
#: meanings is this project's costliest defect, so `ABSTENTION_REASONS` is imported
#: and widened: a reason the deterministic detector can reach keeps one spelling
#: across both paths, and a consumer counting abstentions counts one vocabulary.
#:
#: None of these is reachable by a term match. `below_similarity_floor` is "the
#: nearest schema is not near enough", which a literal match has no analogue for --
#: a term either matched or did not. `inside_margin` is `00`'s "abstain where two
#: readings are both supported" restated as a DISTANCE, because two vectors never
#: tie exactly and `ambiguous` means an exact tie everywhere else in this package.
#: `too_little_text` is `never_alone` in the form a vector can state it. And
#: `safety_domain_uncertain` is the whole of what this path learned about `00`'s
#: four domains: MEASURED, it cannot tell them apart from ordinary files, so where
#: it smells of one at all it says nothing and leaves the door exactly as the term
#: detector left it.
SEMANTIC_ONLY_REASONS: tuple[str, ...] = (
    "below_similarity_floor", "inside_margin", "too_little_text",
    "safety_domain_uncertain")
for _reason in SEMANTIC_ONLY_REASONS:
    if _reason in ABSTENTION_REASONS:
        raise UnknownAbstentionReason(
            f"{_reason!r} is already one of the detector's reasons; widening the "
            "vocabulary with a spelling it already holds would make one meaning "
            "have two homes, which is what importing it exists to prevent")
del _reason

SEMANTIC_ABSTENTION_REASONS: tuple[str, ...] = (
    *ABSTENTION_REASONS, *SEMANTIC_ONLY_REASONS)


class VetoUnreachable(ValueError):
    """The caution veto is set so high it can never fire.

    Not a range check. `caution` at its maximum is a recogniser with the safety
    veto switched off while still claiming files, which is the one configuration
    that can release an HKID -- and it would look, in a config file, exactly like
    a number somebody had thought about. The guard is on the PAIR because neither
    number is wrong alone.
    """


def check_semantic_abstention_reason(value: object) -> str:
    if not isinstance(value, str) or value not in SEMANTIC_ABSTENTION_REASONS:
        raise UnknownAbstentionReason(
            f"{value!r} is not one of the {len(SEMANTIC_ABSTENTION_REASONS)} "
            "reasons this path can reach. An abstention nobody can name is "
            "indistinguishable from a recogniser that did not run.")
    return value


@dataclass(frozen=True, slots=True)
class SemanticFloors:
    """The three numbers that decide, and this module supplies none of them.

    `caution` is the SAFETY VETO: any of `00`'s four domains scoring at or above
    it and the recogniser says nothing at all. `release` is what an ordinary schema
    must reach to claim a file. `margin` is how far clear of the runner-up that
    claim must stand, which is `00`'s "abstain where two readings are both
    supported" stated as a distance because two vectors never tie exactly.

    THE VETO IS NOT A PROTECT FLOOR, AND THE DIFFERENCE IS MEASURED. A protect
    floor was written first and taken out. Over the owner's 199-file ground-truth
    corpus the four safety domains do not separate at all: the eight
    hand-labelled protected files score between 0.084 and 0.151 against the safety
    centroids and sit at the 43rd, 48th, 54th, 58th, 69th, 85th, 89th and 90th
    percentiles of the corpus -- two of them BELOW the median. The single highest
    safety score in the corpus belongs to a Red Cross first-aid certificate, and an
    open-source `LICENSE` file outranks the owner's actual HKID card. No floor
    catches the eight without protecting half the disk, which is the
    over-protection collapse `cli.py` already records.

    So the vector never protects and never releases: where it is near a safety
    domain it abstains, and the file stays exactly as the term detector left it.
    """

    caution: float
    release: float
    margin: float

    def __post_init__(self) -> None:
        for name in ("caution", "release", "margin"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{name} is a similarity and must be a number")
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(
                    f"{name}={value!r} is outside the similarity range; this "
                    "module supplies no default and cannot clamp one either")
        if float(self.caution) >= 1.0:
            raise VetoUnreachable(
                f"caution={self.caution} is at or above the maximum cosine, so the "
                "safety veto can never fire while the recogniser goes on claiming "
                "files. An over-release is worse than an over-protection, and a "
                "veto that cannot trigger is the shape an over-release ships in")


@dataclass(frozen=True, slots=True)
class SimilarityReading:
    """One file version's nearness to each schema, and what it was read from.

    `evidence_refs` are the P4 observation keys whose text went into the vector.
    A classification cites what raised it, and a vector's citation is the set of
    observations it was computed over -- there is no narrower true answer, because
    every one of them moved it.
    """

    scores: Mapping[str, float]
    evidence_refs: tuple[str, ...]
    scope: str
    #: How much of the file's OWN text the vector was computed over. Carried
    #: because mean pooling hides it: a vector over a filename and a vector over
    #: four pages are the same shape and the same magnitude, and the recogniser
    #: has to be able to tell them apart.
    chars: int


@dataclass(frozen=True, slots=True)
class SemanticProposal:
    """One schema this file version's evidence is NEAREST to."""

    schema_id: str
    similarity: float
    runner_up: str | None
    runner_up_similarity: float
    #: The best any of `00`'s four safety domains scored on this file. Carried on
    #: the PROPOSAL and not only on the abstention, because it is what a reader
    #: needs to see that the veto was asked and answered rather than skipped.
    safety_similarity: float
    evidence_refs: tuple[str, ...]
    scope: str

    def __post_init__(self) -> None:
        if self.schema_id not in SCHEMA_IDS:
            raise UnknownSchema(self.schema_id)


@dataclass(frozen=True, slots=True)
class SemanticAbstention:
    """A RESULT. The recogniser measured and declined, and this says why."""

    reason: str
    schema_id: str | None
    detail: str
    tied_schema_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        check_semantic_abstention_reason(self.reason)
        if self.schema_id is not None and self.schema_id not in SCHEMA_IDS:
            raise UnknownSchema(self.schema_id)


#: (conn, file_id, content_hash) -> how near this file version is to each schema.
#: Injected, exactly as `detector.py` injects `corroborating_observations`: the
#: DEPLOYMENT owns the model, the vector arithmetic and the third-party library,
#: and this package consumes an answer. `None` means "there was nothing to read",
#: which is not the same as "it is near nothing".
SchemaSimilarity = Callable[
    [sqlite3.Connection, str, str], "SimilarityReading | None"]


# --- the text a vector is computed over ------------------------------------------

#: P4's own locator for the ancestor chain, refused wherever evidence is read.
PATH_LOCATOR: str = "path"


def scope_for(zones: Sequence[str], char_budget: int) -> str:
    """The name a vector computed over these zones under this budget is filed under.

    P9's rule is that it "defines no default scope and never implicitly
    concatenates a whole file", because *"what a vector was computed over is part
    of what it means, so a silent default would make two vectors incomparable while
    looking identical"*. The zones and the budget ARE what it was computed over, so
    the scope is DERIVED from them and cannot drift away from them: change either
    and the vector is filed under a different identity rather than silently
    replacing one computed under the old rule.
    """
    if not zones:
        raise ValueError(
            "a vector over no zone would be a similarity anchor with no content "
            "behind it; the zones are the caller's and there is no default")
    ordered = tuple(str(zone) for zone in zones)
    if PATH_LOCATOR in ordered:
        raise ValueError(
            "the `path` zone holds the whole ancestor chain, and the absolute path "
            "is not one of the file's own words. Measured: an ordinary photograph "
            "under a folder called `Passport and Visa Documents` was classified "
            "`sensitive_personal`, and every file in that folder with it")
    if (not isinstance(char_budget, int) or isinstance(char_budget, bool)
            or char_budget <= 0):
        raise ValueError("char_budget must be a positive integer")
    return f"evidence[{'+'.join(ordered)}]@{char_budget}"


def evidence_text(conn: sqlite3.Connection, file_id: str, content_hash: str, *,
                  zones: Sequence[str], char_budget: int
                  ) -> tuple[str, tuple[str, ...]]:
    """This file version's own words, in the order the caller ranked their zones.

    Reads `evidence` -- P4's observations, which another part already wrote -- and
    binds no text materialiser: `detector._matches` refuses to pull whole text
    units because that would be "a second materialisation locus, which
    `tests/p7/test_p7_no_invention.py` guards repo-wide", and the same holds here.
    NOTHING HERE OPENS A FILE.

    ZONE ORDER IS SPENT ORDER. The budget is finite and SPEC 2.2 ranks "a filename,
    title, or page-one heading" above the rest, so a truncation keeps the half that
    says what the file IS rather than whichever page P4 happened to write first.
    Which zones, and in which order, is the caller's -- `metadata` is the interesting
    exclusion and it is the caller's to make, not this function's: measured over the
    owner's real corpora what lands there is `Producer`, `CreationDate`, `Creator`
    and `pixel dimensions`, the format talking about the software that wrote it.

    Returns the text and the observation keys it came from, so a classification
    built on the vector can cite the rows that moved it.
    """
    scope_for(zones, char_budget)  # the same refusals, stated once, applied here
    ranked = {zone: order for order, zone in enumerate(zones)}
    found: list[tuple[int, int, str, str]] = []
    for order, row in enumerate(conn.execute(
            "SELECT observation_key, raw_value, normalized_value, location "
            "FROM evidence WHERE file_id = ? AND content_hash = ? "
            "AND superseded_by IS NULL ORDER BY rowid",
            (file_id, content_hash))):
        where = _json.loads(row["location"])
        # Refused on the LOCATOR and not on the zone, because the locator is what
        # `detector._matches` refuses and one rule wants one spelling.
        if where.get("locator") == PATH_LOCATOR:
            continue
        rank = ranked.get(where.get("zone"))
        if rank is None:
            continue
        text = row["raw_value"] or row["normalized_value"]
        if not text or not text.strip():
            continue
        found.append((rank, order, row["observation_key"], text.strip()))

    spent = 0
    parts: list[str] = []
    refs: list[str] = []
    seen: set[str] = set()
    for _rank, _order, key, text in sorted(found, key=lambda item: item[:2]):
        if text in seen:
            continue
        seen.add(text)
        room = char_budget - spent
        if room <= 0:
            break
        parts.append(text[:room])
        spent += min(len(text), room) + 1
        if key not in refs:
            refs.append(key)
    return "\n".join(parts)[:char_budget], tuple(refs)


def embedding_text_for(zones: Sequence[str], char_budget: int):
    """P9's `EmbeddingTextFor` seam, bound to one zone list and one budget.

    `grouping.embeddings` takes text "only through
    `embedding_text_for(conn, file_id, content_hash, scope)`" and this is that
    function for this scope. It REFUSES a scope it did not compute rather than
    answering for one it does not implement: P9 files the vector under the scope
    it was handed, so a reader that answered for any scope would let a vector over
    the filename alone be stored as a vector over the whole document.
    """
    mine = scope_for(zones, char_budget)

    def read(conn: sqlite3.Connection, file_id: str, content_hash: str,
             scope: str) -> str | None:
        if scope != mine:
            raise ValueError(
                f"this reader computes scope {mine!r} and was asked for "
                f"{scope!r}; a vector filed under a scope nothing read for it is "
                "a similarity to a document that was never assembled")
        text, _refs = evidence_text(conn, file_id, content_hash, zones=zones,
                                    char_budget=char_budget)
        return text or None

    return read


# --- the anchors, which are the library's own words ------------------------------

def build_schema_anchors(rules: RecognitionRules, *, max_words: int | None
                         ) -> Mapping[str, tuple[str, ...]]:
    """Every authored term, per schema, as a thing to be NEAR rather than to match.

    `max_words` DROPS THE AUTHORING PROSE, and it is the caller's number because it
    is a property of this library rather than of the method. 13.5% of the 8,925
    compiled terms are seven words or longer, because several rows used
    `work_types` and `proposed_context_terms` as a notes field: one `government`
    entry is a 77-word editorial aside beginning "proposed for r6, not design",
    another "proposal note: none of these terms appears in 00". They are prose
    ABOUT the research rather than about a document.

    The expectation going in was that these would be the RICHEST anchors -- a
    sentence says more than a phrase, and it is unmatchable as a literal string,
    which is the whole argument for embedding them. Measured, they are the worst:
    dropping them moves top-1 schema accuracy from 29.1% to 32.2% over the
    ground-truth corpus. An editorial note is generic English and sits near every
    document, so it drags a schema's centroid toward the middle of the space.
    `None` keeps them, which is what the measurement was made against.

    A rearrangement of the shipped manifest and nothing else: this module writes no
    anchor of its own. Both roles are kept -- `TERM_ROLES` records that the detector
    "counts DISTINCT terms and does not gate on role, because `identity` and
    `research` authored no context terms at all" -- and the same is true here, more
    so: a role split would leave two of the twenty-three schemas with nothing to be
    near.

    A SCHEMA THAT AUTHORED NOTHING GETS NO ANCHOR. An empty anchor set has to be
    scored somehow, and every arithmetic answer to "how near is this to nothing" is
    a schema that either matches every file or none; both are worse than its
    absence, and its absence is honest -- the library says nothing about it.
    """
    anchors: dict[str, tuple[str, ...]] = {}
    for schema_id in SCHEMA_IDS:
        schema = rules.schemas.get(schema_id)
        if schema is None:
            continue
        terms = tuple(dict.fromkeys(
            term.strip() for term in (*schema.terms, *schema.work_type_terms)
            if term and term.strip()
            and (max_words is None or len(term.split()) <= max_words)))
        if terms:
            anchors[schema_id] = terms
    return anchors


# --- deciding ---------------------------------------------------------------------

class SemanticRecogniser:
    """The term detector, and one more door behind it. Never a door in front of it."""

    def __init__(self, *, lexical, schema_similarity: SchemaSimilarity,
                 floors: SemanticFloors, handling_for: Mapping[str, Handling],
                 now: Callable[[], str], min_chars: int,
                 is_protected: Callable[[PurePath], bool] | None = None,
                 safety_domain_ids: Sequence[str] = SAFETY_DOMAIN_IDS) -> None:
        if not callable(lexical):
            raise TypeError(
                "the term detector is composed AROUND, not replaced; it runs first "
                "and its answer is returned untouched")
        if not callable(schema_similarity):
            raise TypeError(
                "the similarity is injected: the deployment owns the model, and "
                "this package computes no vector and names no encoder")
        if not isinstance(floors, SemanticFloors):
            raise TypeError(
                "the floors are a SemanticFloors, which is what refuses a veto "
                "that can never fire; a bare tuple would carry the numbers and "
                "not the rule that relates them")
        if not callable(now):
            raise TypeError("the clock is injected; §8.2 preserves an observed_at")
        if (not isinstance(min_chars, int) or isinstance(min_chars, bool)
                or min_chars <= 0):
            raise ValueError(
                "min_chars must be a positive integer: `never_alone` in the form a "
                "vector can state it, and there is no default for it here")
        for schema_id, handling in dict(handling_for).items():
            if schema_id not in SCHEMA_IDS:
                raise UnknownSchema(
                    f"the handling policy names {schema_id!r}, which is not one of "
                    f"the {len(SCHEMA_IDS)} schemas the product recognises")
            if not isinstance(handling, Handling):
                raise TypeError(f"{schema_id!r} maps to {handling!r}, not a Handling")
        for schema_id in safety_domain_ids:
            if schema_id not in SCHEMA_IDS:
                raise UnknownSchema(schema_id)
        self._lexical = lexical
        self._similarity = schema_similarity
        self._floors = floors
        self._handling = dict(handling_for)
        self._now = now
        self._min_chars = min_chars
        self._is_protected = is_protected
        self._safety = tuple(safety_domain_ids)

    def explain(self, conn: sqlite3.Connection, file_id: str,
                content_hash: str) -> SemanticProposal | SemanticAbstention:
        """Which schema this file version's evidence is nearest to, and whether
        that is near enough to say so."""
        file_row = get_file(conn, file_id)
        if file_row is None:
            return SemanticAbstention("no_evidence", None,
                                      f"{file_id} has no P1 row to classify")
        # FIRST, before any evidence is read and before the encoder is reached.
        # P3's own predicate, not a second copy of it.
        if is_protected_container(PurePath(file_row["current_path"]),
                                  extra=self._is_protected):
            return SemanticAbstention(
                "protected_container", None,
                f"{file_id} at {file_row['current_path']} is inside a protected "
                "container and is marked, counted and never opened; none of its "
                "text was read and no vector of it exists")

        reading = self._similarity(conn, file_id, content_hash)
        if reading is None or not reading.scores:
            return SemanticAbstention(
                "no_evidence", None,
                f"{file_id} has no text in the configured zones to compute a "
                "vector over; nothing was near anything")
        for schema_id in reading.scores:
            if schema_id not in SCHEMA_IDS:
                raise UnknownSchema(
                    f"the similarity scored {schema_id!r}, which is not one of the "
                    f"{len(SCHEMA_IDS)} schemas the product recognises. The encoder "
                    "is injected, so its labels are checked and never trusted")

        if reading.chars < self._min_chars:
            # `never_alone`, in the form a vector can state it. The detector's rule
            # is that one signal never activates a schema; a document with 22
            # characters of its own text has one signal -- its filename -- and mean
            # pooling turns it into a vector that looks exactly as confident as a
            # vector over a whole page. MEASURED, this is the single rule that
            # separates safe from unsafe here: the only two hand-labelled protected
            # files this path ever claimed as ordinary carry 22 and 84 characters
            # (a vaccination-record photograph and a screenshot). At 100 it claims
            # neither, and it claims nothing else it was getting right either way.
            return SemanticAbstention(
                "too_little_text", None,
                f"{file_id} carries {reading.chars} characters of its own text and "
                f"the caller requires {self._min_chars}; a vector over a filename "
                "is one signal wearing a whole document's confidence")

        ranked = sorted(reading.scores.items(), key=lambda item: (-item[1], item[0]))
        leader, best = ranked[0]
        runner_up, second = ranked[1] if len(ranked) > 1 else (None, 0.0)
        safety = max((score for schema_id, score in reading.scores.items()
                      if schema_id in self._safety), default=0.0)

        # THE VETO, and it is the whole of what this path says about `00`'s four
        # domains. It does not protect and it does not release: it falls silent and
        # leaves the file exactly as the term detector left it, which is the only
        # move a signal this poor is entitled to make. See `SemanticFloors` for the
        # measurement -- a Red Cross certificate outscores an HKID.
        #
        # Two doors, because they fail differently. A safety domain LEADING is the
        # file the vector thinks is sensitive; a safety domain merely NEAR the
        # caution line is the file it has no opinion about. Both abstain.
        if leader in self._safety or safety >= self._floors.caution:
            return SemanticAbstention(
                "safety_domain_uncertain", leader if leader in self._safety else None,
                f"the nearest safety domain scores {safety:.3f} against a caution "
                f"line of {self._floors.caution:.3f}"
                + (f" and {leader} leads outright" if leader in self._safety else "")
                + "; this path can neither protect nor release one of `00`'s four "
                "domains and says nothing rather than guessing",
                tied_schema_ids=tuple(schema_id for schema_id in self._safety
                                      if reading.scores.get(schema_id, 0.0) >= safety))

        if best < self._floors.release:
            return SemanticAbstention(
                "below_similarity_floor", leader,
                f"{leader} is the nearest schema at {best:.3f} and the caller's "
                f"release floor is {self._floors.release:.3f}; the file's words "
                "resemble it and do not resemble it enough to be filed as it")
        if best - second < self._floors.margin:
            tied = tuple(schema_id for schema_id, score in ranked
                         if best - score < self._floors.margin)
            return SemanticAbstention(
                "inside_margin", leader,
                f"{leader} at {best:.3f} stands {best - second:.3f} clear of "
                f"{runner_up} and the caller's margin is {self._floors.margin:.3f}; "
                "`00` requires abstention where two readings are both supported",
                tied_schema_ids=tied)
        return SemanticProposal(
            schema_id=leader, similarity=float(best), runner_up=runner_up,
            runner_up_similarity=float(second), safety_similarity=float(safety),
            evidence_refs=reading.evidence_refs, scope=reading.scope)

    # --- the seam ----------------------------------------------------------------

    def __call__(self, conn: sqlite3.Connection, file_id: str,
                 content_hash: str) -> ClassificationRecord | None:
        """`orchestrator.ClassificationProducer`, with the term detector inside it.

        THE TERM DETECTOR SPEAKS FIRST AND IS NEVER OVERRULED. That single line of
        composition is the whole of the over-release guard: a similarity can add a
        classification where there was none, and can never change, lower or
        second-guess one that exists. The protected-container refusal reaches here
        as `None` -- `Detector.__call__` collapses its abstention -- which is why
        `explain` above asks P3's predicate again rather than inferring anything
        from that `None`.
        """
        record = self._lexical(conn, file_id, content_hash)
        if record is not None:
            return record
        outcome = self.explain(conn, file_id, content_hash)
        if isinstance(outcome, SemanticAbstention):
            return None
        if outcome.schema_id in self._safety:
            # Unreachable through `explain`, which vetoes a safety leader above.
            # Stated anyway, because the invariant a reviewer needs is "no record
            # this path emits ever carries a safety domain", and an invariant that
            # lives only inside a branch is one refactor from being untrue.
            raise AssertionError(
                f"{outcome.schema_id} is one of `00`'s four safety domains and "
                "this path neither protects nor releases them")
        handling = self._handling.get(outcome.schema_id)
        if handling is None:
            # Recognised and not classified. `_CONTRACT.md` rule 5 is unchanged by
            # the method that reached the schema: a class picked here to let the
            # pipeline continue would be this package inventing P7's vocabulary.
            return None
        if not outcome.evidence_refs:
            # A classification cites what raised it, and a vector with no
            # observation behind it has nothing to cite.
            return None
        return ClassificationRecord(
            file_id=file_id, content_hash=content_hash,
            handling_class=handling.handling_class, protected=handling.protected,
            basis=handling.basis, evidence_refs=outcome.evidence_refs,
            reliability_state=RELIABILITY, observed_at=self._now())


# --- the vector, computed once and stored as a file VERSION's own ----------------

#: The one serialization this module reads back. P9 is right that "P9's injected
#: encoder owns serialization" and that P1 "stores opaque bytes"; something has to
#: read a stored vector back to score it, and the honest form of that is to name
#: the one codec this reader implements and REFUSE any other rather than sniff a
#: byte length. A deployment shipping a different codec brings its own reader.
FLOAT32_LE: str = "float32-le"


def decode_vector(array_bytes: bytes, encoding: str, dimension: int) -> tuple[float, ...]:
    """P1's opaque bytes, back into numbers, under one declared codec."""
    if encoding != FLOAT32_LE:
        raise ValueError(
            f"this reader implements {FLOAT32_LE!r} and was handed {encoding!r}; "
            "guessing a codec from a byte length is how a 5-dimension vector gets "
            "filed under a 3-dimension identity and noticed months later")
    values = _array("f", bytes(array_bytes))
    if _sys.byteorder != "little":
        values.byteswap()
    if len(values) != dimension:
        raise ValueError(
            f"{len(values)} floats under a record declaring {dimension}")
    return tuple(values)


def schema_similarity_from(
        *, anchor_scores: Callable[[Sequence[float]], Mapping[str, float]],
        config, encode: Callable[[str], Sequence[float]],
        zones: Sequence[str], char_budget: int, now: Callable[[], str],
        ensure_embedding=None) -> SchemaSimilarity:
    """P9's stored vector, scored against the library's anchors. The whole wiring.

    THE VECTOR GOES THROUGH P1. `grouping.embeddings` was written, tested and
    connected to nothing -- `cli.py` passed `EmbeddingsOff()` and reported
    `embeddings_enabled: False` -- so this is the assignment it was waiting for
    rather than a second one beside it. A vector belongs to a file version, a new
    content hash gets a new vector, and the old one stays readable: all three are
    P9's rules and none of them is restated here.

    The text is read ONCE. `evidence_text` gives the citations, and P9's seam is
    handed a reader that returns the text already in hand under the scope it was
    already read for -- so the two never disagree about what was embedded.

    A VECTOR IS DERIVED FROM THE DOCUMENT'S TEXT AND IS TREATED AS THE TEXT. It is
    stored in P1 beside the observations it came from and is never a value this
    module hands outward; `privacy.vocabulary.ALWAYS_LOCAL` covers the zones it is
    read from, and a 384-float summary of a payslip is a payslip's contents in a
    lossier coat, not a fact about it.
    """
    from grouping.embeddings import (
        EmbeddingConfig, EncodedVector, ensure_file_embedding,
    )
    if not isinstance(config, EmbeddingConfig):
        raise TypeError("config is P9's EmbeddingConfig; the model identity, the "
                        "scope and the dimension are the caller's to state")
    mine = scope_for(zones, char_budget)
    if config.scope != mine:
        raise ValueError(
            f"the config files vectors under scope {config.scope!r} and this "
            f"reader assembles {mine!r}; a vector filed under a scope nothing read "
            "for it is a similarity to a document that was never assembled")
    if config.encoding != FLOAT32_LE:
        raise ValueError(
            f"this reader decodes {FLOAT32_LE!r} and the config declares "
            f"{config.encoding!r}")
    if not callable(anchor_scores) or not callable(encode) or not callable(now):
        raise TypeError("anchor_scores, encode and the clock are all injected")
    store = ensure_file_embedding if ensure_embedding is None else ensure_embedding

    def similarity(conn: sqlite3.Connection, file_id: str,
                   content_hash: str) -> SimilarityReading | None:
        text, refs = evidence_text(conn, file_id, content_hash, zones=zones,
                                   char_budget=char_budget)
        if not text or not refs:
            return None
        computed: list[Sequence[float]] = []

        def encoder(passed: str, cfg) -> "EncodedVector":
            vector = encode(passed)
            if len(vector) != cfg.dimension:
                raise ValueError(
                    f"the encoder returned {len(vector)} dimensions under a "
                    f"configuration declaring {cfg.dimension}")
            computed.append(vector)
            values = _array("f", (float(value) for value in vector))
            if _sys.byteorder != "little":
                values.byteswap()
            return EncodedVector(array_bytes=values.tobytes(),
                                 dimension=cfg.dimension, encoding=cfg.encoding)

        record = store(
            conn, file_id=file_id, content_hash=content_hash, config=config,
            encoder=encoder,
            # The text is already read, under this exact scope. P9 asks for it
            # through its own seam and gets what `evidence_text` returned rather
            # than a second read that could differ from the citations above.
            embedding_text_for=lambda _c, _f, _h, scope: (
                text if scope == config.scope else None),
            embeddings_enabled=True, created_at=now())
        if record is None:
            return None
        vector = (computed[0] if computed
                  else decode_vector(record.array_bytes, record.encoding,
                                     record.dimension))
        scores = anchor_scores(vector)
        return SimilarityReading(scores=dict(scores), evidence_refs=refs,
                                 scope=config.scope, chars=len(text))

    return similarity


#: The name this refusal shipped under while there was a protect floor to invert.
#: Kept as an alias rather than removed: a caller catching it is catching the same
#: event, and a rename that turns a caught exception into an uncaught one is a
#: worse outcome than a second name for one class.
FloorsInverted = VetoUnreachable
