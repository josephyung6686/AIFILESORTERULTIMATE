"""Production-only composition of the implemented parts, P1 through P11.

This module chooses plumbing, lifecycle and ORDER only. Domain producers,
thresholds, classification, readers, policies, clocks, catalogues, limits and
payload storage remain mandatory injected authorities, and every user decision
arrives as one too. P8 has no stage of its own here; whether an LLM stage exists
is a decision already frozen inside each supplied P6 resolver, each supplied P9
`p8_run_call`, and each supplied P11 `PipelineInputs`.

Two compositions, and the split is not cosmetic. `run_production_p1_p7` ends at a
scan run and a bundle. Everything after it -- P9's groups, P10's tree, P11's
placements -- needs the `scan_run_id` that run produced, so the downstream
authorities cannot exist before it does. `run_production_p8_p11` therefore takes
them ready-made, and `run_production_corpus` takes a factory over the finished
`P1P7Run` and calls both in order. Nothing here patches an authority record after
the caller built it.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from database_agent.db import create_schema
from database_agent.files_table import get_file
from eval_harness.driver import EvaluationRun, evaluate_bundle
from eval_harness.store import create_eval_schema
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import RunWriter
from extractors.authorship import SUBSYSTEM as P5_SUBSYSTEM
from extractors.dispatch import Readers
from extractors.safety import SafetyPolicy
from extractors.schema import create_extraction_schema
from facts.fields import create_fields
from facts.resolver import FactResolver
from facts.usable import targeted_ocr_needed_for
from orchestrator import ClassificationProducer, P1P7Run, run_p1_p7
from privacy.classification_store import ClassificationStore
from privacy.schema import create_privacy_schema
from grouping.config import GroupingLimits
from grouping.pipeline import GroupingKnowledge, GroupingResult, group_subject
from placement.index import build_destination_index
from placement.pipeline import CorpusResult, PipelineInputs, run_corpus
from placement.records import Subject
from placement.vocabulary import FILE
from scan_agent.corpus_source import CorpusSource
from scan_agent.schema import create_scan_schema
from scan_agent.stat_cache import cache_verdicts
from tree_design.catalogue import TemplateCatalogue, load_catalogue
from tree_design.config import ConfigurationRequired
from tree_design.pipeline import (
    TreeDesignAuthorities, TreeDesignDecisions, TreeDesignResult, design_tree,
)


class InvalidP1P7Authority(ValueError):
    """A required production authority is absent or has the wrong public type."""


class MissingClassificationAuthority(InvalidP1P7Authority):
    """P7 has no detector default; production cannot classify without one."""


@dataclass(frozen=True)
class P1P7Authorities:
    """Every policy-bearing dependency required by the live P1--P7 path."""

    native_resolver: FactResolver
    ocr_resolver: FactResolver
    usable_threshold: Callable[[Any, Any], bool]
    classify: ClassificationProducer
    source: CorpusSource
    mime_type_for: Callable[[Path], str | None]
    scan_state: str
    scan_budget_exhausted: Callable[[], bool]
    detect_format: Callable[[Path], str | None]
    policy: SafetyPolicy
    readers: Readers
    now: Callable[[], str]
    context_window: int
    transcription_authorized: Callable[[], bool]
    corpus_form: str
    policy_settings: Mapping[str, Any]
    file_entry_body: Callable[[Mapping[str, Any]], Mapping[str, str]]
    p7_component_version: str
    #: §8.5's hand-labelled expected side, carried to `_assemble_bundle` and applied
    #: before the seal. Empty by default: an unlabelled scan captures a bundle with
    #: no expectations, which is a corpus snapshot rather than a reference corpus.
    #: P2 SPEC's Deferred table: "P2 publishes `bundle_expectation`; it does not
    #: fill it" -- and neither does this module.
    bundle_expectations: Sequence[Mapping[str, Any]] = ()

    def __post_init__(self) -> None:
        if self.classify is None:
            raise MissingClassificationAuthority(
                "P7 classification requires an explicit producer; no detector or "
                "domain default exists")
        if not isinstance(self.native_resolver, FactResolver):
            raise InvalidP1P7Authority(
                "native_resolver must be a real FactResolver")
        if not isinstance(self.ocr_resolver, FactResolver):
            raise InvalidP1P7Authority("ocr_resolver must be a real FactResolver")
        required_callables = {
            "usable_threshold": self.usable_threshold,
            "classify": self.classify,
            "mime_type_for": self.mime_type_for,
            "scan_budget_exhausted": self.scan_budget_exhausted,
            "detect_format": self.detect_format,
            "now": self.now,
            "transcription_authorized": self.transcription_authorized,
            "file_entry_body": self.file_entry_body,
        }
        for name, authority in required_callables.items():
            if not callable(authority):
                raise InvalidP1P7Authority(
                    f"{name} must be an explicit callable authority")
        for name in ("source", "policy", "readers", "policy_settings"):
            if getattr(self, name) is None:
                raise InvalidP1P7Authority(f"{name} is required")
        for name in ("scan_state", "corpus_form", "p7_component_version"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise InvalidP1P7Authority(f"{name} must be a non-empty string")
        if not isinstance(self.context_window, int) or self.context_window <= 0:
            raise InvalidP1P7Authority("context_window must be a positive integer")


# --- the shipped template library ---------------------------------------------------

#: Every file that makes up one release of the packaged library, in the order the
#: records are read. `tree_design.catalogue.load_catalogue` parses ONE manifest and
#: the library ships as seven files, so somebody has to join them; this module is
#: that somebody, because `catalogue.py` takes an injected reader rather than a
#: path on purpose -- "an injected reader rather than a path keeps this module out
#: of the filesystem entirely", which is what makes its no-repository-scanning
#: guard checkable by import inspection.
#:
#: `wave2_organisational.json` also carries a `refusals` list. It is authored
#: analysis of what the wave declined to template and the loader reads no such
#: key, so it is left where it is rather than folded into a release record.
LIBRARY_FILES: tuple[str, ...] = (
    "fragments.json",
    "definitions.json",
    "applicabilities.json",
    "wave2_commerce.json",
    "wave2_industrial.json",
    "wave2_organisational.json",
    "wave2_practice.json",
)

#: The three record kinds a manifest carries. A library file supplies any subset.
LIBRARY_SECTIONS: tuple[str, ...] = ("fragments", "definitions", "applicabilities")

#: The identity of ONE record inside each section, used only to refuse duplicates.
_LIBRARY_KEYS: Mapping[str, tuple[str, str]] = {
    "fragments": ("fragment_id", "fragment_version"),
    "definitions": ("template_id", "template_version"),
    "applicabilities": ("applicability_id", "applicability_version"),
}

_LIBRARY_DIR = Path(__file__).resolve().parent / "tree_design" / "library"


def read_packaged_library_file(name: str) -> str:
    """Read one shipped library file. THE filesystem touch, named and in one place.

    Passed to `load_shipped_catalogue` by the caller rather than reached for
    inside it, so a deployment that ships the library some other way -- a wheel's
    resource loader, a signed bundle, a test harness -- substitutes this one
    function and nothing else changes.
    """
    if name not in LIBRARY_FILES:
        raise ConfigurationRequired(
            f"{name!r} is not part of the packaged library release; the files are "
            f"{list(LIBRARY_FILES)} and locating others would be the repository "
            "scanning P10 refuses")
    return (_LIBRARY_DIR / name).read_text(encoding="utf-8")


def shipped_catalogue_manifest(
        read_library_file: Callable[[str], str]) -> str:
    """Join the shipped files into the one manifest `load_catalogue` parses.

    The `release_id` is DERIVED, not chosen. `load_catalogue` refuses a manifest
    without one because "two different libraries are indistinguishable in a
    frozen tree", and a constant here would make every edit to the library
    indistinguishable from the release before it. So it is the digest of exactly
    the bytes that were read, in `LIBRARY_FILES` order: a library that changed
    moves the id, and one that did not cannot.

    A record repeated across two files is refused rather than merged. Seven files
    share one namespace, and a duplicate that quietly won would make which
    definition a tree froze depend on the order this module happens to read in.
    """
    digest = hashlib.sha256()
    sections: dict[str, list[dict]] = {name: [] for name in LIBRARY_SECTIONS}
    seen: dict[str, dict[tuple, str]] = {name: {} for name in LIBRARY_SECTIONS}
    for name in LIBRARY_FILES:
        raw = read_library_file(name)
        digest.update(name.encode("utf-8"))
        digest.update(raw.encode("utf-8"))
        document = json.loads(raw)
        for section in LIBRARY_SECTIONS:
            id_key, version_key = _LIBRARY_KEYS[section]
            for record in document.get(section, ()):
                key = (record[id_key], record[version_key])
                first = seen[section].get(key)
                if first is not None:
                    raise ConfigurationRequired(
                        f"{section[:-1]} {key} appears in both {first!r} and "
                        f"{name!r}. Seven files make one release and one release "
                        "holds one record per identity; merging them would make "
                        "the tree depend on read order")
                seen[section][key] = name
                sections[section].append(record)
    manifest = {"release_id": f"lib-{digest.hexdigest()[:16]}"}
    manifest.update(sections)
    return json.dumps(manifest)


def load_shipped_catalogue(
        read_library_file: Callable[[str], str]) -> TemplateCatalogue:
    """The packaged library, through the real loader. P10's `catalogue` authority.

    This is the call `load_catalogue` was written for and had never had: until it
    existed, the 22 fragments, 63 definitions and 208 applicability rows under
    `src/tree_design/library/` were loaded by nothing, and a production run had
    no recipes at all.
    """
    return load_catalogue(lambda: shipped_catalogue_manifest(read_library_file))


def schema_for_situation(catalogue: TemplateCatalogue, situation: str) -> str:
    """Which of P6's twenty-three domains a situation belongs to, ASKED of the library.

    A situation name looks like a dotted path -- `academic.coursework`,
    `travel.trip-photos` -- and the segment before the dot looks like a domain.
    It is not one. The names are the template library's, the domains are
    `facts.domains.SCHEMA_IDS`, and nothing holds the two spellings together:
    `applications.*` belongs to `college_applications`, and `travel.*` splits
    between `finance` and `photos` depending on the row. Reading the domain off
    the name agrees with the library for 201 of its 208 situations and is a crash
    for the other seven -- `MalformedGroupRecord: group_category='applications' is
    not one of the 23 domains`, raised where nothing catches it, on the first
    command a person typed.

    So the answer is READ, off the same applicability rows that make the situation
    a situation at all. `uses_schema` is that answer, each row carries exactly
    one, and a library that gains a situation therefore brings its domain with it
    instead of bringing a spelling this module would have to guess at.

    Refused rather than resolved when the release carries no row for the
    situation, and when two rows that carry it disagree: picking between them here
    would be this module deciding what kind of material somebody's files are,
    which is the one question `--situation` exists to ask them.
    """
    ref = f"recognition:{situation}"
    schemas = sorted({row.uses_schema
                      for row in catalogue.applicabilities.values()
                      if ref in row.detection_signal_refs})
    if not schemas:
        raise ConfigurationRequired(
            f"{situation!r} names no situation in template release "
            f"{catalogue.release_id}, so there is no row to read a domain from")
    if len(schemas) > 1:
        raise ConfigurationRequired(
            f"{situation!r} is carried by rows in {schemas}, and which kind of "
            "material these files are is the person's answer to give rather than "
            "this module's to pick")
    return schemas[0]


@dataclass(frozen=True)
class ShippedSituation:
    """One situation, as much of it as a person choosing between 208 can use.

    `folder_levels` is the row's own `role_bindings` labels, in the order the
    library declares them -- "My school / Semester / Course / Kind of work". They
    are not a description of the situation and are better than one: they are the
    folder levels this situation would actually build, written for a person by
    whoever ratified the row, and already reviewed as shipped data.
    """

    name: str
    schema: str
    folder_levels: tuple[str, ...]


def shipped_situations(
        catalogue: TemplateCatalogue) -> tuple[ShippedSituation, ...]:
    """Every situation the release carries, in the order a person would read them.

    Sorted by DOMAIN first and name second, because the domain is the thing a
    person is actually choosing between -- "these are my school files" -- and 208
    names in one flat alphabetical column asks them to already know the answer in
    order to find it. It also puts the seven whose name and domain disagree under
    the domain that owns them, so `travel.trip-photos` appearing beneath `photos`
    reads as information rather than as the bug it used to be.

    A situation carried by rows in two domains is listed under each: this reports
    the library and resolves nothing. `schema_for_situation` is the one that has
    to refuse such a row, because a RUN has to pick exactly one and this does not.
    """
    seen: dict[tuple[str, str], ShippedSituation] = {}
    for row in catalogue.applicabilities.values():
        for signal in row.detection_signal_refs:
            name = signal.removeprefix("recognition:")
            seen.setdefault((row.uses_schema, name), ShippedSituation(
                name=name, schema=row.uses_schema,
                folder_levels=tuple(binding.label
                                    for binding in row.role_bindings)))
    return tuple(seen[key] for key in sorted(seen))


def nearest_situations(catalogue: TemplateCatalogue, situation: str, *,
                       limit: int = 5) -> tuple[str, ...]:
    """The names closest to one the library does not carry. Possibly none.

    For the refusal, which currently says how many situations exist and not one
    of them -- so a person who typed `academic.courswork` is told the library
    carries 208 and left to find the missing `e` themselves.

    `difflib` over the names the release actually carries: this suggests nothing
    that is not already a situation, and returns an empty tuple rather than a bad
    guess when nothing is close. A wrong suggestion is worse than none, because a
    person will paste it.
    """
    names = sorted({row.name for row in shipped_situations(catalogue)})
    return tuple(difflib.get_close_matches(situation, names, n=limit))


def bootstrap_p1_p7(conn: sqlite3.Connection) -> None:
    """Create implemented schemas in dependency order: P1, P3, P4, P5, P6, P7, P2."""
    create_schema(conn)
    create_scan_schema(conn)
    create_evidence_schema(conn)
    create_extraction_schema(conn)
    # `create_fields` creates P6's schema and installs its closed, source-owned
    # catalogue. It reads no unfinished domain or prompt directory.
    create_fields(conn)
    create_privacy_schema(conn)
    create_eval_schema(conn)


def compose_p1_p7(
        conn: sqlite3.Connection, *, authorities: P1P7Authorities
) -> Callable[[str], P1P7Run]:
    """Bind concrete storage adapters while preserving all injected authorities."""
    # Revalidate here so bypassing dataclass construction cannot let a scan start.
    authorities.__post_init__()
    sink = RunWriter(conn, author=P5_SUBSYSTEM)
    classification_store = ClassificationStore(conn)
    targeted_ocr_needed = targeted_ocr_needed_for(
        conn, usable_threshold=authorities.usable_threshold)

    def resolve(resolver: FactResolver):
        return lambda db, file_id, content_hash: resolver.resolve(
            db, file_id=file_id, content_hash=content_hash)

    def run(selection_id: str) -> P1P7Run:
        return run_p1_p7(
            conn, selection_id, source=authorities.source,
            mime_type_for=authorities.mime_type_for,
            scan_state=authorities.scan_state,
            budget_exhausted=authorities.scan_budget_exhausted,
            detect_format=authorities.detect_format, policy=authorities.policy,
            readers=authorities.readers, sink=sink, now=authorities.now,
            context_window=authorities.context_window,
            transcription_authorized=authorities.transcription_authorized,
            corpus_form=authorities.corpus_form,
            policy_settings=authorities.policy_settings,
            file_entry_body=authorities.file_entry_body,
            resolve_native=resolve(authorities.native_resolver),
            targeted_ocr_needed=targeted_ocr_needed,
            resolve_with_ocr=resolve(authorities.ocr_resolver),
            classify=authorities.classify,
            classification_store=classification_store,
            p7_component_version=authorities.p7_component_version,
            bundle_expectations=authorities.bundle_expectations)

    return run


def run_production_p1_p7(
        conn: sqlite3.Connection, selection_id: str, *,
        authorities: P1P7Authorities) -> P1P7Run:
    """Compose and execute one production P1--P7 run."""
    return compose_p1_p7(conn, authorities=authorities)(selection_id)


# --- P9 through P11, in order, deciding nothing --------------------------------------


class InvalidCorpusAuthority(ValueError):
    """A required downstream authority is absent or has the wrong public type."""


class MissingCatalogueAuthority(InvalidCorpusAuthority):
    """P10 has no template catalogue; a run without one can route nothing.

    The twin of `MissingClassificationAuthority`, one layer down.
    `TreeDesignAuthorities` types `catalogue` as `object` and checks it nowhere,
    so `catalogue=None` builds a valid-looking authorities record and fails deep
    inside `route_branch` after a draft plan version has already been written.
    Checked here, before P9 has run, because a refusal that arrives after rows
    exist is a refusal the user has to clean up after.
    """


@dataclass(frozen=True)
class EvaluationAuthorities:
    """§8.5's replay, and everything a comparison must be able to name.

    `evaluate_bundle` states it plainly -- "there is no threshold, no tolerance
    and no clock, because §8.5 states none" -- so all five arrive from the caller
    and are recorded verbatim on the run manifest. `adapters` may be empty: a
    stage with no adapter reports `not_implemented` and its dimension scores
    `not_run`, so a bundle is evaluable while most measured stages are absent.
    """

    version_tuple: Mapping[str, Any]
    budget_ceilings: Mapping[str, int]
    run_settings: Mapping[str, bool]
    adapters: Mapping[str, Any]
    run_kind: str


@dataclass(frozen=True)
class CorpusAuthorities:
    """Every policy-bearing dependency P9, P10 and P11 need. None has a default.

    `design` is P10's own record, built by the caller: it names the catalogue,
    the ranking, the privacy ordering and the handling-class collapse, and
    `tree_design.pipeline` already states the rule -- absent means refuse, never
    guess. It arrives whole rather than field by field so that this module cannot
    quietly answer one of its questions.

    `placement_inputs` is a factory rather than a record for the same reason
    `run_production_corpus` takes one: `PipelineInputs.plan_version` and `.tree`
    are what P10 MINTS, so a `PipelineInputs` built before the design run would
    have to name a plan version that does not exist yet.
    """

    #: The compiled release P10 routes against. Held here AS WELL AS inside the
    #: authorities the factory below builds, because it is the one P10 authority
    #: that can be checked before a single row is written -- and because
    #: `TreeDesignAuthorities` types `catalogue` as `object` and checks it
    #: nowhere, so a `None` there survives construction and fails deep inside
    #: `route_branch` with a draft plan version already on disk.
    catalogue: TemplateCatalogue
    #: P10's authorities, built once the groups exist. A factory and not a record
    #: because two of its fields cannot be known any earlier:
    #: `scan_run_id` is minted by P3 inside the scan, and `sensitive_group_ids`
    #: names P9 groups, and their ids are derived from the file ids that scan
    #: found. It is handed the ids the user ACCEPTED rather than everything P9
    #: proposed, because that is the set §5.3 builds the top level out of.
    #: The checked release is handed back in so the run cannot silently route
    #: against a different one, which `run_production_p8_p11` then verifies.
    design_authorities: Callable[
        [TemplateCatalogue, Sequence[str]], TreeDesignAuthorities]
    grouping_limits: GroupingLimits
    grouping_knowledge: GroupingKnowledge
    user_seed_for: Callable[[str, str], Any]
    embeddings: Any
    #: P9's route to a model, and the six authorities the call needs. `None` for
    #: both is a legal deterministic run: `group_subject` returns a candidate with
    #: `no_model_call_configured` rather than synthesising a verdict.
    p8_run_call: Callable[..., Any] | None
    p8_authorities: Any
    placement_inputs: Callable[[TreeDesignResult], PipelineInputs]
    #: §6.3's per-file evidence, as `place_file` reads it. P11 states no producer
    #: for it and neither does this module.
    evidence_for: Callable[[str], Mapping[str, Any]]
    component_version: str
    #: §8.5's replay over the bundle P1--P7 sealed, or `None` for a run that
    #: measures nothing. `None` is a DECLARATION and not an omission: the eval
    #: harness needs a version tuple, ceilings and a stage-adapter set that only a
    #: deployment can name, and a composition that invented them would publish a
    #: comparison against a baseline nobody chose.
    evaluation: EvaluationAuthorities | None
    #: ONE clock for the whole downstream run, read once so that every P9 group,
    #: every index entry and every placement decision carries the same
    #: `observed_at`. §8.2 preserves an observed_at rather than re-deriving one.
    now: Callable[[], str]

    def __post_init__(self) -> None:
        if not isinstance(self.catalogue, TemplateCatalogue):
            raise MissingCatalogueAuthority(
                "P10 routing requires a compiled template catalogue; no default "
                "release exists and an empty one would make C1 pass by having "
                "nothing to resolve. `production.load_shipped_catalogue` reads "
                "the packaged library")
        if not isinstance(self.grouping_limits, GroupingLimits):
            raise InvalidCorpusAuthority(
                "grouping_limits must be a real GroupingLimits; P9 runs under "
                "P1's ceilings and a run with none is a run under a bound nobody "
                "chose")
        if not isinstance(self.grouping_knowledge, GroupingKnowledge):
            raise InvalidCorpusAuthority(
                "grouping_knowledge must be a real GroupingKnowledge")
        if (self.p8_run_call is None) != (self.p8_authorities is None):
            raise InvalidCorpusAuthority(
                "P9's model route is both halves or neither: a `run_call` with no "
                "authorities cannot reach the gate, and authorities with no "
                "`run_call` name a route nothing takes")
        for name in ("design_authorities", "user_seed_for", "placement_inputs",
                     "evidence_for", "now"):
            if not callable(getattr(self, name)):
                raise InvalidCorpusAuthority(
                    f"{name} is an injected authority with no default")
        if self.evaluation is not None and not isinstance(
                self.evaluation, EvaluationAuthorities):
            raise InvalidCorpusAuthority(
                "evaluation is a real EvaluationAuthorities or an explicit None")
        if not isinstance(self.component_version, str) or not self.component_version:
            raise InvalidCorpusAuthority(
                "component_version is stamped on every row this run writes; a run "
                "that cannot be identified cannot be replayed")


@dataclass(frozen=True)
class CorpusDecisions:
    """Everything the USER decides between P7 and P11. Not one of them is ours.

    `accept_groups` is the review screen §5.3 assumes has already happened: P10
    builds the top level out of ACCEPTED groups, and P9 writes none -- acceptance
    is a separate record a person creates. A composition that accepted P9's own
    output would be the engine approving its own groups.

    `set_privacy_policy` is P7's operation mode, put in force for the plan version
    P10 minted. `placement.privacy.privacy_state_for` refuses a run with no policy
    -- "the operation mode decides whether anything may leave the device and P11
    assumes none" -- and the mode is the user's, so it arrives as a callable that
    is handed the one thing it cannot know in advance.
    """

    #: The review the user is working in. P9 writes its groups against this
    #: version and P10 designs FROM it, so naming it once here is what stops the
    #: two halves reading different reviews.
    plan_version_id: str
    #: The review screen. Returns the ids of the groups now accepted in this plan
    #: version -- which need not be P9's own ids, because a review that renames,
    #: merges or splits a group writes a new one that supersedes what P9 proposed.
    accept_groups: Callable[
        [sqlite3.Connection, Sequence[GroupingResult]], Sequence[str]]
    #: §5's decisions, over the groups the user accepted. A factory and not a
    #: record because `branch_group_ids` names those ids, and P9 derives them from
    #: the file ids the scan found -- a caller naming them in advance has chosen
    #: branches in a corpus nobody has looked at.
    design: Callable[[Sequence[str]], TreeDesignDecisions]
    #: The user approving the plan P10 froze, and with it the groups inside it.
    #:
    #: This exists because of a break at the P10 -> P11 join. §8.8 mints a NEW
    #: plan version for every edit, so the version P11 reads is never the version
    #: P9 wrote its acceptances against -- and `placement.groups`'s own docstring
    #: says it asks "P9's own read, AS OF P10's frozen plan version". Nothing in
    #: any part carries an acceptance across the chain, so §6.8's group pass
    #: refuses every group with `GroupNotAcceptedInVersion` and P11 places files
    #: one at a time with no shared context.
    #:
    #: It is a DECISION and not plumbing because approving the frozen plan IS the
    #: user accepting those groups in it. A composition that wrote the row itself
    #: would be recording an approval nobody gave, in a version nobody saw.
    #: Takes the connection, the accepted group ids, and the frozen plan version.
    approve_plan: Callable[[sqlite3.Connection, Sequence[str], str], None]
    set_privacy_policy: Callable[[sqlite3.Connection, str], None]

    def __post_init__(self) -> None:
        if not isinstance(self.plan_version_id, str) or not self.plan_version_id:
            raise InvalidCorpusAuthority(
                "plan_version_id names the review this run belongs to; P9 writes "
                "acceptances against it and P10 designs from it")
        for name in ("accept_groups", "design", "approve_plan",
                     "set_privacy_policy"):
            if not callable(getattr(self, name)):
                raise InvalidCorpusAuthority(
                    f"{name} is the user's decision arriving as a callable; a "
                    "composition that answered it would be choosing for them")


@dataclass(frozen=True)
class ProductionRun:
    """One corpus, all the way through. Every field is something a part returned."""

    p1_p7: P1P7Run
    #: One per file in P1's roster, in roster order, INCLUDING the files that
    #: produced no group. A file P9 found no seed for is a real outcome and
    #: dropping it here would be the silent omission the standing rule forbids.
    grouping: tuple[GroupingResult, ...]
    tree: TreeDesignResult
    destinations: tuple[Any, ...]
    placement: CorpusResult
    #: §8.5's replay of this run's own bundle, or `None` when the deployment
    #: declared no evaluation. Never a silently absent field: `None` here means
    #: nobody asked for a measurement, not that one was taken and lost.
    evaluation: EvaluationRun | None = None

    @property
    def protected_areas(self):
        """The containers P3 marked and nothing opened, carried up from P10.

        Present on the run rather than left for a caller to dig out of `tree`,
        because "marked and counted, never opened" needs the count to be
        reachable from the thing the user was handed.
        """
        return self.tree.protected_areas


def corpus_roster(conn: sqlite3.Connection,
                  scan_run_id: str) -> tuple[tuple[str, str], ...]:
    """Every file version P1 indexed in this scan run, in P3's own order.

    Read from P3's stat-cache verdicts rather than from `P1P7Run.fact_results`,
    and the difference is a file. `fact_results` holds only the files that went
    through extraction THIS run: a REUSE file -- unchanged since the last scan,
    with perfectly good stored facts -- is skipped by the extraction loop and has
    no entry. Grouping and placing only the re-extracted files would leave every
    unchanged file out of the plan with nothing to say so.

    Nothing inside a protected container is here, because P3 never wrote a `files`
    row for one. That is the marking; the counting is `TreeDesignResult`'s.
    """
    roster: list[tuple[str, str]] = []
    for verdict in cache_verdicts(conn, scan_run_id):
        file_id = verdict["file_id"]
        if file_id is None:
            continue
        roster.append((file_id, get_file(conn, file_id)["content_hash"]))
    return tuple(roster)


def _group_corpus(conn: sqlite3.Connection, roster, *,
                  authorities: CorpusAuthorities,
                  decisions: CorpusDecisions,
                  created_at: str) -> tuple[GroupingResult, ...]:
    """P9 over every file, one subject at a time. `group_subject` takes one."""
    return tuple(
        group_subject(
            conn, file_id=file_id, content_hash=content_hash,
            plan_version_id=decisions.plan_version_id,
            limits=authorities.grouping_limits,
            knowledge=authorities.grouping_knowledge,
            user_seed_for=authorities.user_seed_for,
            p8_run_call=authorities.p8_run_call,
            p8_authorities=authorities.p8_authorities,
            embeddings=authorities.embeddings, created_at=created_at)
        for file_id, content_hash in roster)


def run_production_p8_p11(
        conn: sqlite3.Connection, p1_p7: P1P7Run, *,
        authorities: CorpusAuthorities,
        decisions: CorpusDecisions) -> ProductionRun:
    """P9, P10 and P11 over one finished P1--P7 run. This function owns the order.

    The order is contractual at four points, and each one is a raise somewhere
    else if it is broken:

    1. **Acceptance before design.** §5.3 builds the top level out of accepted
       groups; `design_tree` raises `NothingToDesign` over a version with none.
    2. **The approval and the policy before the index.** Both are about the plan
       version P10 minted and neither exists until it does: `accepted_group_as_of`
       refuses a group this version has no opinion on, and `privacy_state_for`
       refuses a run with no operation mode in force.
    3. **The index before the placements.** `retrieve` reads the projected
       destination index, and P10's freeze record is the one legality authority
       it is a projection of.
    4. **Groups before files.** `run_corpus` does that internally -- a member's
       decision belongs to its group's plan -- which is why the whole corpus goes
       through one call rather than a loop of `place_file`.
    5. **§8.5's replay last, or not at all.** It reads the sealed bundle and no
       live filesystem, so it cannot affect what came before it and must not be
       able to; running it first would only mean a failed measurement stopped a
       plan the user could otherwise have had.
    """
    authorities.__post_init__()
    decisions.__post_init__()
    observed_at = authorities.now()

    roster = corpus_roster(conn, p1_p7.scan_run_id)
    grouping = _group_corpus(conn, roster, authorities=authorities,
                             decisions=decisions, created_at=observed_at)
    accepted = tuple(decisions.accept_groups(conn, grouping) or ())
    if any(not isinstance(group_id, str) or not group_id for group_id in accepted):
        raise InvalidCorpusAuthority(
            "accept_groups returns the ids of the groups the user accepted; an "
            "empty or non-string id names no group P10 can read")

    design = authorities.design_authorities(authorities.catalogue, accepted)
    if not isinstance(design, TreeDesignAuthorities):
        raise InvalidCorpusAuthority(
            "design_authorities must return a real TreeDesignAuthorities")
    if design.catalogue is not authorities.catalogue:
        raise MissingCatalogueAuthority(
            "the design authorities route against a different release from the "
            "one this run was checked against; a tree frozen under an unchecked "
            "catalogue names a library nobody validated")
    tree_decisions = decisions.design(accepted)
    if not isinstance(tree_decisions, TreeDesignDecisions):
        raise InvalidCorpusAuthority(
            "the design decisions must be a real TreeDesignDecisions; §5.7 makes "
            "a template inert until approved and the approval lives there")
    if tree_decisions.from_plan_version != decisions.plan_version_id:
        raise InvalidCorpusAuthority(
            f"the design reads {tree_decisions.from_plan_version!r} and P9 wrote "
            f"its groups against {decisions.plan_version_id!r}; a tree designed "
            "from a different review is designed from groups this run never made")
    tree = design_tree(conn, authorities=design, decisions=tree_decisions)
    plan_version = tree.tree.plan_version_id
    decisions.approve_plan(conn, accepted, plan_version)
    decisions.set_privacy_policy(conn, plan_version)
    destinations = build_destination_index(
        conn, tree.tree, component_version=authorities.component_version,
        observed_at=observed_at)

    # The groups that BECAME branches, read off the design rather than off P9's
    # output. A group the user accepted and then did not keep as a branch has no
    # destination in this tree, and asking P11 to plan it would be planning into
    # a node nobody approved.
    group_ids = tuple(dict.fromkeys(
        group_id for branch in tree.branches
        for group_id in branch.candidate.accepted_group_ids))
    placement = run_corpus(
        conn,
        subjects=tuple(
            Subject(kind=FILE, file_id=file_id, content_hash=content_hash,
                    group_id=None, member_file_ids=())
            for file_id, content_hash in roster),
        group_ids=group_ids,
        inputs=authorities.placement_inputs(tree),
        evidence_for=authorities.evidence_for,
        component_version=authorities.component_version,
        observed_at=observed_at)

    # §8.5 LAST, and over the bundle P1--P7 sealed rather than over anything P9
    # to P11 wrote. `replay_bundle` reads the bundle with no live filesystem
    # present, so it measures the run that happened rather than the disk as it is
    # now -- which is the whole point of sealing one.
    evaluation = None
    if authorities.evaluation is not None:
        evaluation = evaluate_bundle(
            conn, p1_p7.bundle_id,
            version_tuple=dict(authorities.evaluation.version_tuple),
            budget_ceilings=authorities.evaluation.budget_ceilings,
            run_settings=authorities.evaluation.run_settings,
            adapters=authorities.evaluation.adapters,
            run_kind=authorities.evaluation.run_kind)

    return ProductionRun(p1_p7=p1_p7, grouping=grouping, tree=tree,
                         destinations=destinations, placement=placement,
                         evaluation=evaluation)


def run_production_corpus(
        conn: sqlite3.Connection, selection_id: str, *,
        authorities: P1P7Authorities,
        downstream: Callable[[P1P7Run], CorpusAuthorities],
        decisions: CorpusDecisions) -> ProductionRun:
    """A directory to a placement decision, in one call.

    `downstream` is a factory over the finished `P1P7Run` and not a record,
    because `TreeDesignAuthorities.scan_run_id` is the one thing the ORDER
    produces: P3 mints it inside the scan. Handing this module a record with a
    placeholder in that field and letting it overwrite one would be exactly the
    thing every authority record in this project exists to prevent -- a
    policy-bearing value chosen by the composition. So the caller builds them,
    once the run identity exists.
    """
    p1_p7 = run_production_p1_p7(conn, selection_id, authorities=authorities)
    return run_production_p8_p11(conn, p1_p7, authorities=downstream(p1_p7),
                                 decisions=decisions)
