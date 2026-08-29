# src/grouping/fixtures.py
"""P9's golden dossiers — the two shapes the design specifies by example.

These are contract witnesses that P10 and P11 build against before P9's pipeline
runs. They publish P9-OWNED records only. Nothing here imports P8, P10, P11 or
P13, and nothing under `tests/` is importable from this module.

The two shapes are the design's own: a course dossier and an application
dossier. Each one is a bounded evidence packet in which direct anchors and
context-supported candidates arrive as separate arrays, because the model has to
be able to call a group coherent while still marking a particular member
uncertain.

Every excerpt's `observation_key` is computed with P4's own function over the
same content the test seeds into the evidence store, so a caller can resolve
every citation in these dossiers against a real observation rather than take the
fixture's word for it.
"""
from __future__ import annotations

import hashlib

from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.locator import serialize_locator
from evidence_shape.observation import observation_key

from grouping.records import (
    AnchorFact,
    BudgetSummary,
    CandidateGroupDossier,
    Conflict,
    DossierFile,
    Excerpt,
    Omissions,
    PrivacySummary,
    TypedEdge,
)
from grouping.vocabulary import (
    COMPATIBLE_DOCUMENT_TYPE,
    CONTEXT_SUPPORTED,
    DIRECT_ANCHOR,
    MUTUAL_SEMANTIC_RETRIEVAL,
    SHARED_VALIDATED_FACT,
)

EXTRACTOR = "fixture.text"


def fixture_content_hash(name: str) -> str:
    """A real 64-hex-character digest. P4 refuses anything else (R1), and a
    fixture that carried a readable placeholder could not be seeded at all."""
    return hashlib.sha256(name.encode("utf-8")).hexdigest()


CREATED_AT = "2026-08-26T00:00:00Z"
ZONE = "heading"


def fixture_location() -> Location:
    """One locator shape for every fixture excerpt. P4 owns the serialization."""
    return Location(
        zone=ZONE,
        container_path=(Segment(kind="page", index=1),),
        text_span=TextSpan(start=0, end=8),
    )


def fixture_observation_key(*, content_hash: str, raw_value: str) -> str:
    """P4's key, computed P4's way. A fixture that minted its own would not
    resolve against a seeded observation, and the citation could not be checked."""
    return observation_key(
        content_hash=content_hash,
        extractor_name=EXTRACTOR,
        locator=serialize_locator(fixture_location()),
        raw_value=raw_value,
    )


def _excerpt(*, content_hash: str, raw_value: str) -> Excerpt:
    return Excerpt(
        observation_key=fixture_observation_key(
            content_hash=content_hash, raw_value=raw_value,
        ),
        location=ZONE,
        text=raw_value,
        # From `fixture_location()`, the same locator the seeded observation gets,
        # so a fixture excerpt addresses what a real one would.
        text_span=(fixture_location().text_span.start,
                   fixture_location().text_span.end),
    )


def _anchor_fact(*, field: str, value: str, file_ids: tuple[str, ...],
                 content_hash: str, raw_value: str) -> AnchorFact:
    return AnchorFact(
        field=field,
        value=value,
        file_ids=file_ids,
        reliability_state="validated",
        observation_key=fixture_observation_key(
            content_hash=content_hash, raw_value=raw_value,
        ),
    )


# --- the course dossier ---------------------------------------------------------
#
# The design's own example: a sparse homework file whose neighbourhood contains a
# syllabus and a lecture that each state PHYS1401 directly, and a midterm that
# independently contains a validated course code. `HW 3.pdf` has a homework-like
# name and mutual semantic retrieval links to those files -- and stays a
# candidate, because a name and a semantic link are not an anchor.

COURSE_FILES: tuple[tuple[str, str, str, str], ...] = (
    # (file_id, content_hash, document_type, the raw value the excerpt quotes)
    ("lecture-08", fixture_content_hash("hash-lecture-08"), "lecture", "PHYS1401"),
    ("midterm-practice", fixture_content_hash("hash-midterm"), "exam", "PHYS1401"),
)
COURSE_CANDIDATE = ("hw-3", fixture_content_hash("hash-hw-3"), "homework", "PHYS1401")


def course_dossier_fixture() -> CandidateGroupDossier:
    """PHYS1401 course materials. Two direct anchors, one context candidate."""
    anchors = tuple(
        DossierFile(
            file_id=file_id,
            content_hash=content_hash,
            document_type=document_type,
            basis=DIRECT_ANCHOR,
            key_facts=(
                _anchor_fact(
                    field="course_code", value="PHYS1401", file_ids=(file_id,),
                    content_hash=content_hash, raw_value=raw_value,
                ),
            ),
            excerpts=(_excerpt(content_hash=content_hash, raw_value=raw_value),),
            why_retrieved=None,
        )
        for file_id, content_hash, document_type, raw_value in COURSE_FILES
    )
    file_id, content_hash, document_type, _raw = COURSE_CANDIDATE
    candidate = DossierFile(
        file_id=file_id,
        content_hash=content_hash,
        document_type=document_type,
        basis=CONTEXT_SUPPORTED,
        key_facts=(),
        excerpts=(),
        why_retrieved=(
            f"{MUTUAL_SEMANTIC_RETRIEVAL} to lecture-08 and midterm-practice; "
            f"{COMPATIBLE_DOCUMENT_TYPE} homework in a course neighbourhood"
        ),
    )
    edges = tuple(
        TypedEdge(
            edge_id=f"edge-course-{index}",
            from_file_id=file_id,
            to_file_id=anchor.file_id,
            edge_type=MUTUAL_SEMANTIC_RETRIEVAL,
            evidence_ref=anchor.excerpts[0].observation_key,
            weight=None,
            bridge_entity_ref=None,
            hub_suppressed=False,
            created_at=CREATED_AT,
        )
        for index, anchor in enumerate(anchors)
    )
    return CandidateGroupDossier(
        dossier_id="fixture-course-dossier",
        group_id="fixture-course-group",
        proposed_basis="PHYS1401 course materials",
        anchor_files=anchors,
        candidate_files=(candidate,),
        typed_edges=edges,
        key_facts=tuple(
            fact for anchor in anchors for fact in anchor.key_facts
        ),
        excerpts=tuple(
            excerpt for anchor in anchors for excerpt in anchor.excerpts
        ),
        # Empty because a course group with no conflicting course code is the
        # design's own coherent example (SS4.4) -- NOT because the builder had
        # nowhere to get conflicts from, which is what `()` meant at the five
        # production sites this fixture sits beside. The conflict-bearing shape is
        # `application_dossier_fixture`, whose `target_institution` conflict is
        # what lets P10 and P11 exercise Site B's check against a published
        # fixture. `CONFLICT_FREE_BY_DESIGN` in `tests/p9/test_p9_fixtures.py`
        # names this line for the guard, so a sixth bare `()` cannot appear here
        # silently.
        conflicts=(),
        engine_flagged_outliers=(),
        omissions=Omissions(
            budget_cap_dropped=(), privacy_redacted=(), neighbourhood_capped=(),
        ),
        privacy=PrivacySummary(
            handling_classes=("public_low",), redactions_applied=0,
            release_decision_ref=None,
        ),
        budget=BudgetSummary(token_ceiling=4000, neighbour_cap=25, files_dropped=0),
        dossier_fingerprint="fixture-course-fingerprint",
        created_at=CREATED_AT,
    )


# --- the application dossier ----------------------------------------------------
#
# The design's other example: an application packet whose members share a target
# institution. The conflicting Duke essay is IN the dossier and flagged, not
# omitted -- an application packet must not silently absorb a document with a
# conflicting target institution, and the model can only avoid that if it sees it.

APPLICATION_FILES: tuple[tuple[str, str, str, str], ...] = (
    ("essay-columbia", fixture_content_hash("hash-essay-columbia"), "essay", "Columbia"),
    ("admissions-checklist", fixture_content_hash("hash-checklist"), "checklist", "Columbia"),
)
APPLICATION_CANDIDATE = ("portal-screenshot", fixture_content_hash("hash-portal"), "screenshot", "Columbia")
CONFLICTING_FILE = ("essay-duke", fixture_content_hash("hash-essay-duke"), "essay", "Duke")


def application_dossier_fixture() -> CandidateGroupDossier:
    """Columbia application packet, with the conflicting Duke essay shown."""
    anchors = tuple(
        DossierFile(
            file_id=file_id,
            content_hash=content_hash,
            document_type=document_type,
            basis=DIRECT_ANCHOR,
            key_facts=(
                _anchor_fact(
                    field="target_institution", value="Columbia",
                    file_ids=(file_id,), content_hash=content_hash,
                    raw_value=raw_value,
                ),
            ),
            excerpts=(_excerpt(content_hash=content_hash, raw_value=raw_value),),
            why_retrieved=None,
        )
        for file_id, content_hash, document_type, raw_value in APPLICATION_FILES
    )
    file_id, content_hash, document_type, raw_value = APPLICATION_CANDIDATE
    candidate = DossierFile(
        file_id=file_id,
        content_hash=content_hash,
        document_type=document_type,
        basis=CONTEXT_SUPPORTED,
        key_facts=(),
        excerpts=(_excerpt(content_hash=content_hash, raw_value=raw_value),),
        why_retrieved=(
            f"{SHARED_VALIDATED_FACT} target_institution=Columbia on the checklist"
        ),
    )
    conflicting_id, conflicting_hash, conflicting_type, conflicting_raw = (
        CONFLICTING_FILE
    )
    conflicting = DossierFile(
        file_id=conflicting_id,
        content_hash=conflicting_hash,
        document_type=conflicting_type,
        basis=CONTEXT_SUPPORTED,
        key_facts=(),
        excerpts=(
            _excerpt(content_hash=conflicting_hash, raw_value=conflicting_raw),
        ),
        why_retrieved=(
            f"{COMPATIBLE_DOCUMENT_TYPE} essay in an application neighbourhood"
        ),
    )
    return CandidateGroupDossier(
        dossier_id="fixture-application-dossier",
        group_id="fixture-application-group",
        proposed_basis="Columbia application packet, 2026 cycle",
        anchor_files=anchors,
        candidate_files=(candidate, conflicting),
        typed_edges=(),
        key_facts=tuple(
            fact for anchor in anchors for fact in anchor.key_facts
        ),
        excerpts=tuple(
            excerpt
            for item in (*anchors, candidate, conflicting)
            for excerpt in item.excerpts
        ),
        conflicts=(
            Conflict(
                kind="target_institution",
                competing_values=("Columbia", "Duke"),
                file_ids=("essay-columbia", "essay-duke"),
            ),
        ),
        engine_flagged_outliers=(conflicting_id,),
        omissions=Omissions(
            budget_cap_dropped=(), privacy_redacted=(), neighbourhood_capped=(),
        ),
        privacy=PrivacySummary(
            handling_classes=("public_low",), redactions_applied=0,
            release_decision_ref=None,
        ),
        budget=BudgetSummary(token_ceiling=4000, neighbour_cap=25, files_dropped=0),
        dossier_fingerprint="fixture-application-fingerprint",
        created_at=CREATED_AT,
    )


GOLDEN_DOSSIERS = (course_dossier_fixture, application_dossier_fixture)
