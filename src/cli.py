"""One command that points the composed pipeline at a directory. THE choosing place.

`production.py` composes P1 through P11 and decides nothing: every threshold,
every ceiling, every clock, every catalogue, every policy and every user answer
arrives as an injected authority with no default. That discipline has to end
somewhere, because a real run needs actual numbers -- and this module is where it
ends. **Every constant below is a deployment decision, and this is the only file
in `src/` that makes one.** If a number appears here that `00` states, the comment
says where; if `00` states none, the comment says that instead and names who owns
the question.

What it does NOT choose is the two things that are the user's:

* `--situation` says which of the researched situations this corpus is, which is
  what selects the applicability row that routes it. P9 emits `group_category =
  None` on every path it has (`src/grouping/pipeline.py:230` is the only writer
  and it is unconditional), so nothing upstream can answer it and a value chosen
  here would be this file inventing what the user's files are about.
* `--label` names the branch. §5's tree is the user's, and P9's deterministic run
  produces no `display_label` either.

Both are required flags for exactly that reason.

**The standing rule, and where it is honoured.** Reports, applications and system
files are never moved, read or opened. A protected container is MARKED AND
COUNTED, NEVER OPENED: P3 refuses to index inside one, the detector never
classifies one, P10 writes a node for it that is not a legal destination, and P11
never places into it. This command prints the count and the path of every one, so
the marking is reachable rather than merely true.
"""
from __future__ import annotations

import argparse
import getpass
import json
import re
import sqlite3
import sys
import textwrap
from itertools import count
from pathlib import Path
from typing import Sequence

from database_agent.budget import set_ceiling
from database_agent.db import DatabaseInsideCorpus, open_database
from extractors.reading import StructuredString
from extractors.safety import SafetyPolicy
from facts.direct import DirectSlot, DirectSlots, direct_facts
from facts.discount import MetadataScreen
from facts.resolver import FactResolver
from facts.usable import record_pass
from grouping.acceptance import group_state_as_of, record_acceptance
from grouping.config import GroupingLimits
from grouping.embeddings import EmbeddingsOff
from grouping.pipeline import GroupingKnowledge, GroupingResult
from grouping.records import Group, GroupAcceptance
from grouping.retrieval import RetrievalKnowledge
from grouping.schema import create_grouping_schema
from grouping.store import (
    current_group, memberships_for_group, record_group, record_membership,
    stop_rule_outcome_for,
)
from grouping.vocabulary import (
    ACCEPTED, COHERENT, PENDING_REVIEW, USER, USER_EDITED,
)
from placement import vocabulary as pv
from placement.config import CEILINGS, SupportPolicy, placement_limits
from placement.pipeline import PipelineInputs
from placement.schema import create_placement_schema
from privacy.classification_store import ClassificationStore
from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy
from production import (
    CorpusAuthorities, CorpusDecisions, P1P7Authorities, ProductionRun,
    bootstrap_p1_p7, load_shipped_catalogue, read_packaged_library_file,
    run_production_corpus,
)
from readers.deployment import macos_readers
from recognition.detector import SAFETY_DOMAIN_HANDLING, Detector
from recognition.rules import load_rules
from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.exclusion import is_protected_container
from scan_agent.selection import record_selection
from tree_design.catalogue import TemplateCatalogue
from tree_design.config import TreeLimits
from tree_design.freeze import FreezeRefused
from tree_design.materialise import MaterialisationRefused
from tree_design.pipeline import (
    NothingToDesign, SharedMaterialAnswer, TreeDesignAuthorities,
    TreeDesignDecisions,
)
from tree_design.store import ReviewActionRefused
from tree_design.templates import CompositionConflict
from tree_design.upstream import UpstreamUnavailable
from tree_design.schema import create_tree_schema
from tree_design.vocabulary import (
    MANDATORY_REVIEW, REFINED, SHALLOW_BY_CHOICE,
)

# ======================================================================================
# THE CHOICES. Nothing above this line and nothing in `production.py` picks a number.
# ======================================================================================

#: This deployment's identity, stamped on every row it writes so a replay can name
#: the code that produced it. §8.5 requires the version tuple to be recorded; it
#: states no format for it.
COMPONENT_VERSION: str = "cli-0.1.0"

#: §6.10's two conditions. SPEC Open questions 1 and 2 leave BOTH the thresholds
#: and the scale open, so these are declared here rather than derived: 1.0 as the
#: scale because the scorer's weights already sum to it, 0.50 as the support bar
#: because that is the band a direct fact alone (3/7) falls below and a direct fact
#: plus an accepted group (5/7) clears, and 0.20 as the margin. A run under these
#: is auditable because `policy_id` travels on every decision -- change a number
#: and change the id with it, or a replay silently compares two different rules.
SUPPORT_POLICY = SupportPolicy(
    policy_id="cli-support-v1", support_scale_max=1.0,
    minimum_support_threshold=0.50, margin_threshold=0.20)

#: P1's ceilings, which every other part reads through its own config module.
#: `00` §8.6 names the ceilings and states no values, so these are this
#: deployment's. Eight is small on purpose: it bounds a first run on a real
#: person's disk rather than optimising one.
CEILING_VALUE: int = 8

#: §5.7's and §5.9's tree bounds. `00` states no numbers for these either.
TREE_LIMITS = TreeLimits(
    max_folder_proposals_and_depth=5, max_dossier_tokens=4000,
    excessive_depth_warning=4, tiny_folder_max_files=1,
    tiny_folder_count_warning=2,
    # §5.9's flattening test. A deployment with no retrieval telemetry cannot
    # measure it, and answering `False` would suppress every vertical option; this
    # answers `True` and leaves the judgement to the user, who sees the option's
    # counts and warnings before taking it.
    materially_improves_retrieval=lambda option: True)

#: P9's bounds. Same status as the tree limits: named by §8.6, valued here.
GROUPING_LIMITS = GroupingLimits(
    max_retrieved_neighbors=50, max_graph_nodes=10, max_candidate_members=10,
    max_dossier_tokens=4000, generic_hub_frequency=9,
    minimum_independent_anchors=1, max_excerpt_characters=240)

#: §8.4's operation mode. `offline` is chosen, not defaulted: it is the only mode
#: under which nothing about any file can leave the device, and a first run on
#: somebody's home directory is not the moment to ask for less. Every other part
#: reads it through P7's policy and refuses to run without one.
OPERATION_MODE: str = "offline"

#: P7's handling class for an ordinary file and for a protected area. The set is
#: P7's vocabulary; which one a node carries is a deployment decision, and the
#: protected one is deliberately the strongest so a marked container can never
#: inherit a weaker floor than its contents would require.
ORDINARY_CLASS: str = "personal_non_sensitive"
PROTECTED_CLASS: str = "highly_sensitive_credential_bearing"

#: §1.1's root anchor -- the top of the tree the plan is written against.
ROOT_ANCHOR: str = "root_documents"

#: The review this run's groups and acceptances belong to.
PLAN_VERSION: str = "plan_0"

#: §3.8's collector roles, which V4 uses and refuses to receive empty. P6 owns
#: which fields collect and its vocabulary is still widening, so this names the two
#: that plainly do rather than pinning a count that other work would break.
COLLECTOR_FIELD_KEYS = frozenset({"authored_by", "organization"})

#: §2.2's structured-string patterns. P5's SPEC puts these in its Deferred table
#: and ships none, so they are the deployment's. ONE, and deliberately narrow: an
#: identifier token -- letters then digits, like PHYS1401, INV20261, AC4471 -- which
#: is §2.2's own "identifiers" class. A wider pattern would put more of the file's
#: text into P4's observations, and a first run on somebody's disk is not the place
#: to widen what gets read.
_STRUCTURED = re.compile(r"\b[A-Z][A-Z0-9]*[0-9]{3,}\b")

#: §3.5's direct slot set, and §2.2/§2.3's suppression catalogue. `DirectSlots` has
#: no default because the slot is the caller's; this deployment reads ONE -- the
#: identifier the structured-string pass found in the document's text -- into
#: `subject`. The claim it makes is narrow and it is this deployment's to make: an
#: identifier printed in a document is what that document is ABOUT.
#:
#: The `/Title` metadata slot §3.5 also names is deliberately absent: its
#: observation carries no text span, P7's gate cannot release a span-less excerpt,
#: and a group anchored on it could never be reviewed.
DIRECT_SLOTS = DirectSlots(slots=(
    DirectSlot(
        slot_id="cli.text.identifier", field_key="subject",
        names=lambda locator: locator.startswith(("body#", "heading")),
        canonical=lambda raw: " ".join(raw.split())),
))
METADATA_SCREEN = MetadataScreen(tool_producer_strings=(),
                                 metadata_property_names=())

#: §7.3 fixes nine residual template names and leaves their eight attribute slots
#: deferred. This deployment enables NONE rather than inventing slot values: an
#: unplaced file still reaches §7.5's review set with its reason, so it is counted
#: and explained -- which is the property that matters -- and it does so without a
#: folder nobody designed.
RESIDUAL_LIBRARY: dict = {}

_RECOGNITION_MANIFEST = (
    Path(__file__).resolve().parent / "recognition" / "library" / "recognition.json")


class NotConfigured(RuntimeError):
    """The run was asked for something this deployment has not been given."""


#: Every way the chain refuses BY NAME. Caught in `main` and printed, because a
#: refusal with a reason is an answer and a traceback is not. Imported here rather
#: than caught as `Exception`: an unexpected error must still crash loudly.
REFUSALS: tuple[type[BaseException], ...] = (
    CompositionConflict, FreezeRefused, MaterialisationRefused, NothingToDesign,
    ReviewActionRefused, UpstreamUnavailable,
)


# ======================================================================================
# The seam P9 has not published, supplied here because somebody must
# ======================================================================================


class AcceptedGroupEnumeration:
    """`tree_design.upstream.AcceptedGroupReader`, over P9's own rows.

    Three of its four methods delegate straight to P9. The fourth,
    `accepted(plan_version_id)`, has NO live P9 implementation: P9 publishes
    `group_state_as_of` for ONE group and nothing that enumerates the groups a plan
    version accepted (`src/tree_design/upstream.py` records this as SPEC
    corrections row 17). P10 deliberately does not work around it, because "an
    enumeration P10 wrote itself would be P10 deciding which groups a plan version
    contains".

    So it is written HERE, by the composition root that created the acceptances in
    the first place. The day P9 publishes the enumeration this class loses its
    first method and keeps the rest.
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def accepted(self, plan_version_id: str) -> tuple[GroupAcceptance, ...]:
        rows = self._conn.execute(
            "SELECT acceptance_id, group_id, membership_id, review_state, "
            "user_edited_label, aliases, review_decision_ref, decided_by, "
            "created_at FROM group_acceptance WHERE plan_version_id = ? "
            "AND superseded_by IS NULL ORDER BY group_id",
            (plan_version_id,)).fetchall()
        return tuple(
            GroupAcceptance(
                acceptance_id=row["acceptance_id"],
                plan_version_id=plan_version_id, group_id=row["group_id"],
                membership_id=row["membership_id"],
                # P9's own answer, asked per group rather than read off the row, so
                # a superseded opinion cannot be reported as current.
                acceptance=group_state_as_of(
                    self._conn, group_id=row["group_id"],
                    plan_version_id=plan_version_id),
                review_state=row["review_state"],
                user_edited_label=row["user_edited_label"],
                aliases=tuple(json.loads(row["aliases"] or "[]")),
                review_decision_ref=row["review_decision_ref"],
                decided_by=row["decided_by"], created_at=row["created_at"])
            for row in rows)

    def group(self, group_id: str):
        return current_group(self._conn, group_id)

    def memberships(self, group_id: str):
        return memberships_for_group(self._conn, group_id)

    def stop_rule_outcome(self, group_id: str):
        return stop_rule_outcome_for(self._conn, group_id)


# ======================================================================================
# P1--P7's authorities
# ======================================================================================


def find_structured_strings(text: str) -> tuple[StructuredString, ...]:
    return tuple(
        StructuredString(kind="identifier", start=match.start(), end=match.end())
        for match in _STRUCTURED.finditer(text))


def _direct_stage(conn, file_id: str, content_hash: str) -> tuple[str, ...]:
    return direct_facts(conn, file_id=file_id, content_hash=content_hash,
                        slots=DIRECT_SLOTS, screen=METADATA_SCREEN)


def _resolver(*, tiers: frozenset[str], cache_key: str) -> FactResolver:
    """P6, deterministic. `rule` and `llm` are `None`, which is a decision.

    §3 allows all three stages. This deployment ships no authored rule set and no
    model route, and `FactFesolver` treats `None` as "this stage does not exist"
    rather than as an empty one -- so a fact this run could not reach stays
    unresolved and visible instead of being recorded as absent.
    """
    return FactResolver(
        stages={"direct": _direct_stage, "rule": None, "llm": None},
        pending_fields=lambda conn, file_id, content_hash: (),
        budget_exhausted=lambda ceiling: False,
        model_route_permitted=lambda file_id: False,
        record_pass=lambda conn, file_id, content_hash: record_pass(
            conn, file_id=file_id, content_hash=content_hash,
            analysis_tiers=tiers),
        cache_key_for=lambda file_id, content_hash: f"{cache_key}:{content_hash}",
        screen_metadata=lambda conn, file_id, content_hash: ())


def _mime_type_for(path: Path) -> str | None:
    import mimetypes

    return mimetypes.guess_type(str(path))[0]


def _detect_format(path: Path) -> str | None:
    """Which extractor family the bytes belong to, by extension only.

    Extension rather than content sniffing, and that is a choice: sniffing means
    opening the file, and the one class of file this command must never open is
    decided by PATH (`is_protected_container`) before any format question is asked.
    """
    return {".pdf": "pdf", ".txt": "txt", ".md": "md"}.get(path.suffix.lower())


def classifier(detector, *, now):
    """P7's candidate producer: the real detector, and nothing behind it.

    A file the detector declines to answer about stays UNCLASSIFIED, and that is
    the whole policy. It used to be classified `highly_sensitive_credential_bearing,
    protected=True` -- a deliberate over-protection, written when
    `placement.privacy` raised `ClassificationRequired` for an unclassified file
    and one unrecognised file therefore refused the entire corpus run.

    That refusal is fixed: P11 now reads P7's own `resolve_class(None) ->
    unreadable_unclassified` and returns the file as `blocked_pending_user`. So the
    over-protection has stopped being a precaution and become a COLLAPSE. It made
    an unreadable scan and a passport identical in P7's store -- same class, same
    flag, same sentence to the user -- and made the honest unclassified path
    unreachable from this command. `00`: "sensitive personal material is not the
    same thing as `Numbers.app`."

    Over-protecting is not free. "We deliberately did not look" and "we could not
    tell" are different answers, they ask the user for different things, and a
    product that says the first when it means the second is lying in the direction
    that happens to feel safe.
    """

    def classify(conn: sqlite3.Connection, file_id: str, content_hash: str):
        return detector(conn, file_id, content_hash)

    return classify


def p1_p7_authorities(*, now, detector) -> P1P7Authorities:
    return P1P7Authorities(
        native_resolver=_resolver(tiers=frozenset(("filesystem", "native")),
                                  cache_key="cli-native-v1"),
        ocr_resolver=_resolver(
            tiers=frozenset(("filesystem", "native", "ocr")),
            cache_key="cli-ocr-v1"),
        # §3.6's usability verdict. This deployment answers "usable" always, which
        # means targeted OCR is never triggered -- the honest state for a run with
        # no authored per-field usability bar, and the alternative (answering
        # `False`) would send every text-bearing PDF through Apple Vision on the
        # strength of a threshold nobody chose.
        usable_threshold=lambda facts, unresolved: True,
        classify=classifier(detector, now=now),
        source=FilesystemCorpusSource(),
        mime_type_for=_mime_type_for, scan_state="scanned",
        scan_budget_exhausted=lambda: False, detect_format=_detect_format,
        # THE standing rule, at its first enforcement point. `is_protected_container`
        # is P3's own predicate; P3 writes an exclusion verdict for the container and
        # never walks inside it, so no `files` row for its interior is ever created
        # and nothing downstream can read one.
        policy=SafetyPolicy(is_protected_container=is_protected_container,
                            is_dataless=lambda path: False),
        readers=macos_readers(find_structured_strings=find_structured_strings),
        now=now,
        # §2.6's excerpt window, in characters. `00` states none.
        context_window=240,
        # Transcription opens audio and video. Not authorised, and saying so is
        # what keeps it off rather than the absence of a transcriber.
        transcription_authorized=lambda: False,
        corpus_form="snapshot", policy_settings={"operation_mode": OPERATION_MODE},
        file_entry_body=lambda row: {"payload_ref": row["content_hash"]},
        p7_component_version=COMPONENT_VERSION)


# ======================================================================================
# The user's decisions
# ======================================================================================


def review_and_accept(conn: sqlite3.Connection,
                      results: Sequence[GroupingResult], *,
                      situation: str, label: str, created_at: str) -> tuple[str, ...]:
    """The review screen, non-interactively: keep everything, as one named group.

    Two things happen here that P9 cannot do for itself, and both are the user's:

    * a NAME. `src/grouping/pipeline.py` writes `display_label=None` on every
      group it makes, and `apply_p8_verdict` never sets one either, so
      `tree_design.upstream` refuses an unlabelled group by name. `--label` is it.
    * a CATEGORY. `group_category` is `None` for the same reason, and an accepted
      group with no category is eligible for no applicability row at all -- C3
      refuses the branch outright. `--situation` is it.

    Recorded as a supersession through P9's own writers rather than as an edit, so
    what P9 proposed and what the user answered are both still on disk.
    """
    grouped = [result for result in results if result.group is not None]
    if not grouped:
        return ()
    first = grouped[0].group
    merged_id = f"{PLAN_VERSION}:{label}"
    schema = situation.split(".", 1)[0]
    reviewed = Group(
        group_id=merged_id, seed_ref=first.seed_ref, seed_kind=first.seed_kind,
        proposed_basis=f"the user confirmed these files are {label!r}",
        anchor_facts=tuple(
            fact for result in grouped for fact in result.group.anchor_facts),
        pre_model_signals={"reviewed_proposals": len(grouped)},
        anchor_count=sum(result.group.anchor_count for result in grouped),
        coherence_verdict=COHERENT,
        coherence_citations=tuple(
            fact.observation_key for result in grouped
            for fact in result.group.anchor_facts),
        group_category=schema, display_label=label, label_source=USER_EDITED,
        conflicts=(), stop_rule_hits=(), state=first.state,
        sensitivity_state=first.sensitivity_state, dossier_id=None,
        llm_response_ref=None, validation_verdict_ref=None, created_by=USER,
        created_at=created_at, supersedes=first.group_id,
        supersede_reason="the user named and categorised this group at review")
    record_group(conn, reviewed)
    for result in grouped:
        for membership in memberships_for_group(conn, result.group.group_id):
            record_membership(conn, _carried(membership, merged_id))
    record_acceptance(conn, GroupAcceptance(
        acceptance_id=f"acc:{merged_id}", plan_version_id=PLAN_VERSION,
        group_id=merged_id, membership_id=None, acceptance=ACCEPTED,
        review_state=PENDING_REVIEW, user_edited_label=label, aliases=(),
        review_decision_ref=None, decided_by=USER, created_at=created_at))
    return (merged_id,)


def _carried(membership, group_id: str):
    import dataclasses

    return dataclasses.replace(
        membership, membership_id=f"{membership.membership_id}:{group_id}",
        group_id=group_id, supersedes=membership.membership_id,
        supersede_reason="carried onto the group the user confirmed")


def choose_option(candidate, options) -> str:
    """§5.5, non-interactively: the first nesting §5.7's checks say may be built.

    Stated rather than hidden, because it IS a choice and a person at a review
    screen would make a different one. The options carry their counts, their
    warnings and their validation report; this takes the first that passes and has
    children, and falls back to the last option -- which is always `no-split` --
    rather than raising, because a branch nobody could nest is still a branch.
    """
    for option in options:
        report = option.validation
        if option.total_child_branches and (report is None or report.accepted):
            return option.option_id
    return options[-1].option_id


def refinement_for(node) -> tuple[str, str]:
    """§5.8, per node. Every legal destination needs an answer or freeze refuses.

    A top-level branch is `refined` -- its levels came from settled facts. Anything
    below it is `shallow-by-choice`, and the reason says so in the user's words
    rather than in a code's.
    """
    if node.parent_node_id is None:
        return (REFINED,
                "The levels beneath this branch were populated from facts that "
                "were already settled in your files.")
    return (SHALLOW_BY_CHOICE,
            "This branch holds few enough files that splitting it further would "
            "not help you find anything.")


# ======================================================================================
# The run
# ======================================================================================


def _bootstrap(conn: sqlite3.Connection) -> None:
    bootstrap_p1_p7(conn)
    create_grouping_schema(conn)
    create_tree_schema(conn)
    create_placement_schema(conn)
    for key in CEILINGS.values():
        set_ceiling(conn, key, CEILING_VALUE)


def _validate_situation(catalogue: TemplateCatalogue, situation: str) -> str:
    """The situation names a row the shipped library actually carries.

    Checked against the catalogue rather than against a list here, so a library
    that gains or loses a situation moves this check with it and a typo is refused
    before a single file is read.
    """
    ref = f"recognition:{situation}"
    known = {signal for row in catalogue.applicabilities.values()
             for signal in row.detection_signal_refs}
    if ref not in known:
        raise NotConfigured(
            f"{situation!r} names no situation the shipped template library "
            f"recognises. It carries {len(known)}; "
            f"`--list-situations` prints them.")
    return ref


def run(conn: sqlite3.Connection, directory: Path, *, situation: str, label: str,
        user_id: str, now) -> ProductionRun:
    """One corpus, end to end. Assembles the authorities and calls the composition."""
    catalogue = load_shipped_catalogue(read_packaged_library_file)
    signal = _validate_situation(catalogue, situation)
    schema = situation.split(".", 1)[0]
    clock = now()
    _bootstrap(conn)
    selection_id = record_selection(
        conn, sources=[directory], candidate_roots=[], cross_folder_moves=False,
        selected_by=user_id)
    detector = Detector(load_rules(_RECOGNITION_MANIFEST.read_text),
                        handling_for=SAFETY_DOMAIN_HANDLING, now=now,
                        is_protected=is_protected_container)

    def design_authorities(release: TemplateCatalogue,
                           accepted: Sequence[str]) -> TreeDesignAuthorities:
        ids = count()
        return TreeDesignAuthorities(
            catalogue=release, group_reader=AcceptedGroupEnumeration(conn),
            limits=TREE_LIMITS, root_anchor=ROOT_ANCHOR,
            selection_id=selection_id, scan_run_id=scan_run_id[0],
            active_domains=(schema,),
            # Which accepted groups hold sensitive material. P7 classifies FILES
            # and publishes no group-level answer, so this deployment names none
            # and every group is offered; the per-file floors below are what keep
            # a sensitive file from landing somewhere weaker.
            sensitive_group_ids=frozenset(),
            # §5.2's privacy ordering. P7 publishes HANDLING_CLASSES as a SET and
            # no rank, so one is chosen here: everything ranks equal, which is the
            # only ordering that cannot give a branch a weaker floor than one of
            # its files by accident.
            privacy_rank=lambda floor: 0,
            satisfies_purpose_profile=lambda ref, groups: True,
            detection_signals_for=lambda group: frozenset({signal}),
            # §5.7's ranking. The router already emits candidates in the library's
            # own order and this deployment has no telemetry to re-rank them with,
            # so it keeps that order rather than inventing a score.
            rank_candidates=lambda candidates: list(candidates),
            handling_class_for_member=lambda member: ORDINARY_CLASS,
            collapse_handling_classes=lambda classes: (
                PROTECTED_CLASS if PROTECTED_CLASS in classes else ORDINARY_CLASS),
            handling_class_for_area=lambda area: PROTECTED_CLASS,
            protected_handling_classes=frozenset({PROTECTED_CLASS}),
            collector_field_keys=COLLECTOR_FIELD_KEYS,
            # §5.11's disclosure test. This deployment ships no detector for it and
            # answers `False`, which means a value is never suppressed for
            # disclosure -- stated rather than silent, because the alternative
            # (answering `True`) would suppress every label in the tree.
            value_discloses_protected_material=lambda field_ref, value: False,
            template_context_for=lambda field_ref, order_index: None,
            mint_node_id=lambda: f"node_{next(ids)}",
            mint_version_id=lambda: f"version_{next(ids)}")

    def design_decisions(accepted: Sequence[str]) -> TreeDesignDecisions:
        return TreeDesignDecisions(
            from_plan_version=PLAN_VERSION, branch_group_ids=tuple(accepted),
            choose_option=choose_option, refinement_for=refinement_for,
            residual_library=RESIDUAL_LIBRARY, residual_choices=(),
            residual_configuration={},
            residual_handling_class=lambda name: ORDINARY_CLASS,
            residual_refinement=None,
            # §6.9's policy. NOT optional -- `validate_for_freeze` refuses a plan
            # version without one, because a file that belongs to two homes leaves
            # P11 having to pick an institution. `mandatory-review` is the answer
            # that keeps that decision with the person, file by file, which is the
            # only one a command with nobody to ask may make on their behalf.
            #
            # `00`:99's scoped General is genuinely optional and stays unanswered:
            # it puts a folder in the tree to catch things the branch does not
            # cover, and an unasked question answered by default is a folder
            # nobody wanted.
            shared_material=SharedMaterialAnswer(
                parent_origin_id=None, policy=MANDATORY_REVIEW,
                reason="Nobody was at the screen to say where material shared "
                       "between two of these folders belongs, so it stays your "
                       "decision, one file at a time.",
                display_label="Shared Material", policy_scope=None),
            scoped_general=(),
            created_at=clock, user_id=user_id,
            component_version=COMPONENT_VERSION)

    def accept_groups(db: sqlite3.Connection,
                      results: Sequence[GroupingResult]) -> tuple[str, ...]:
        return review_and_accept(db, results, situation=situation, label=label,
                                 created_at=clock)

    def approve_plan(db: sqlite3.Connection, accepted: Sequence[str],
                     plan_version: str) -> None:
        """The user approves the frozen plan, and the groups in it with it.

        Non-interactively, that means: this command showed nobody the plan, so it
        carries forward exactly the acceptance the review already recorded and
        adds none. Written through P9's own `record_acceptance` against the FROZEN
        version, because that is the version P11 asks about.
        """
        for group_id in accepted:
            record_acceptance(db, GroupAcceptance(
                acceptance_id=f"acc:{plan_version}:{group_id}",
                plan_version_id=plan_version, group_id=group_id,
                membership_id=None, acceptance=ACCEPTED,
                review_state=PENDING_REVIEW, user_edited_label=label, aliases=(),
                review_decision_ref=None, decided_by=USER, created_at=clock))

    def set_privacy_policy(db: sqlite3.Connection, plan_version: str) -> None:
        set_policy(db, Policy(
            policy_version=UNSET_POLICY_VERSION, operation_mode=OPERATION_MODE,
            consent_grants=(), redaction_settings={},
            # §8.4: protected material is not moved automatically without a policy
            # that permits it. This deployment permits none, so nothing protected
            # moves and P11 records the refusal on the decision.
            automatic_move_permissions={}, plan_version=plan_version,
            set_at=clock), component_version=COMPONENT_VERSION, user_id=user_id,
            reason="offline run from the command line")

    def evidence_for(file_id: str) -> dict:
        """§6.3's evidence for one file: the facts P6 actually settled about it."""
        facts, items = [], []
        for row in conn.execute(
                "SELECT ff.fact_id, ff.field_key, ff.evidence_refs, "
                'v.canonical_value FROM file_facts ff JOIN "values" v '
                "ON ff.value_id = v.value_id WHERE ff.file_id = ? "
                "AND ff.active = 1 AND ff.superseded_by IS NULL", (file_id,)):
            from llm_harness.records import EvidenceItem
            from placement.records import MatchingFact

            refs = json.loads(row["evidence_refs"] or "[]")
            ref = refs[0] if refs else None
            facts.append(MatchingFact(
                file_fact_id=row["fact_id"], field=row["field_key"],
                value=row["canonical_value"], reliability=pv.DIRECT,
                evidence_ref=ref))
            items.append(EvidenceItem(
                evidence_ref=ref, kind="fact", location="heading",
                excerpt_span=(0, len(row["canonical_value"])),
                reliability_state="direct", basis="direct-anchor"))
        return dict(
            facts=tuple(facts), evidence_items=tuple(items),
            group_ids=tuple(accepted_ids), curated_folder_labels=(),
            semantic_neighbours=(), related_files=(),
            # §6.5's generic-entity suppression. A value seen in more files than
            # this is treated as a hub rather than as a discriminator. Both numbers
            # are this deployment's; `00` states neither.
            entity_frequency={fact.value: 1 for fact in facts},
            generic_entity_frequency=200)

    def residual_partition(unplaced: Sequence[str]) -> tuple[dict, ...]:
        """§7.5's review sets. SPEC Open question 10 leaves the taxonomy open, so
        this deployment surfaces ONE set holding everything §6 could not place --
        the smallest partition that still shows every file with a reason."""
        if not unplaced:
            return ()
        return ({"label": "Not yet placed",
                 "member_file_ids": tuple(unplaced),
                 "representative_examples": tuple(unplaced)[:3],
                 "file_type_distribution": (), "age_range": (),
                 "evidence_availability": "partial", "sensitivity_status": "none",
                 "protected": False, "weak_graph_neighbours": (),
                 "reason_not_placed":
                     "no destination in this tree matched them well enough to "
                     "decide without asking you."},)

    def placement_inputs(tree) -> PipelineInputs:
        return PipelineInputs(
            plan_version=tree.tree.plan_version_id, tree=tree.tree,
            policy=SUPPORT_POLICY, limits=placement_limits(conn),
            partition=residual_partition,
            # §6.9, when a file has two homes. This deployment abstains rather than
            # asking, because there is no screen here to ask on and choosing one
            # institution is the failure §6.9 exists to prevent.
            ask_or_abstain=lambda node_ids: pv.ABSTAIN,
            max_return_cycles=1,
            # §6.12 step 7's model path, absent in every part. `model_path_available`
            # reads these as a set: with them `None`, a file that needs a judgement
            # abstains with a reason instead of being decided by nothing.
            gate=None, model_client=None, prompt=None, call_dependencies=None,
            model_call_request=None, chosen_node_of=None, residual_action_of=None,
            sensitivity_policy=None, p2=None)

    scan_run_id = [""]
    accepted_ids: list[str] = []

    def downstream(p1_p7) -> CorpusAuthorities:
        scan_run_id[0] = p1_p7.scan_run_id
        return CorpusAuthorities(
            catalogue=catalogue, design_authorities=design_authorities,
            grouping_limits=GROUPING_LIMITS,
            grouping_knowledge=GroupingKnowledge(
                # §4.4's retrieval channels. This deployment runs no embeddings, so
                # every similarity channel is off and retrieval is by shared
                # validated fact alone -- the deterministic path P9 is explicit is
                # a complete path.
                retrieval=RetrievalKnowledge(
                    document_compatible=None, channel_weights={}, similarity=None,
                    similarity_threshold=None, embedding_identity=None,
                    domain=None),
                active_schema_for=lambda db, file_id, content_hash: (
                    tuple(slot.field_key for slot in DIRECT_SLOTS.slots)),
                signal_evaluator_for=lambda domain: True,
                classification_store=ClassificationStore(conn).current,
                conflicts_for=lambda file_ids: (),
                duplicate_or_version=None),
            user_seed_for=lambda file_id, content_hash: None,
            embeddings=EmbeddingsOff(), p8_run_call=None, p8_authorities=None,
            placement_inputs=placement_inputs, evidence_for=evidence_for,
            # §8.5's replay measures a run against a reference corpus with
            # hand-labelled expectations. This command scans a person's own
            # folder, which has none, so it declares no evaluation rather than
            # publishing a score against a baseline that does not exist.
            evaluation=None,
            component_version=COMPONENT_VERSION, now=now)

    def accept_and_remember(db, results):
        ids = accept_groups(db, results)
        accepted_ids.extend(ids)
        return ids

    return run_production_corpus(
        conn, selection_id, authorities=p1_p7_authorities(now=now,
                                                          detector=detector),
        downstream=downstream,
        decisions=CorpusDecisions(
            plan_version_id=PLAN_VERSION, accept_groups=accept_and_remember,
            design=design_decisions, approve_plan=approve_plan,
            set_privacy_policy=set_privacy_policy))


# ======================================================================================
# What the person sees
# ======================================================================================


#: P11's outcome vocabulary, in the words the person whose files these are would
#: use. `00` §5.1 asks labels to "reflect the user's vocabulary rather than a
#: universal corporate taxonomy", and a report is as much a label as a folder is.
#: An outcome missing from this table prints its own name rather than nothing: a
#: gap in this deployment's vocabulary must never become a file that vanished.
#: The order is the order these are printed in -- what is settled first, what
#: needs the person last.
OUTCOME_WORDS: dict[str, str] = {
    pv.PLACE: "Ready to file",
    pv.LEAVE_IN_PLACE: "Staying exactly where they are",
    pv.MARK_STATE: "Marked and left alone",
    pv.MARK_REVIEW_LATER: "Set aside for you to look at later",
    pv.RETURN_TO_PLACEMENT: "Sent back round for another look",
    pv.ASK_USER: "Waiting for you to choose where these go",
    pv.ABSTAIN: "Waiting for you to say what these are",
}

#: How many files of one kind are named before the rest are counted instead.
#: `src/tree_design/health.py` shortens its warning list for the same reason --
#: a list longer than the thing it describes is not a summary of anything -- and
#: this follows it, INCLUDING the one exemption: a protected group is never one
#: of the counted ones. `00` states no number; ten is enough to recognise a
#: folder's worth of files by eye and short enough to stay a summary.
NAMES_LISTED_PER_GROUP: int = 10


def file_names(conn: sqlite3.Connection, root: Path) -> dict[str, str]:
    """Every indexed file, by the name its owner calls it.

    `files.current_path` is P1's own column and has always been there, so a
    report printing `74ce335f-110b-42c0-8a50-ecdc8f8734b7` was never showing the
    only thing it had. A person cannot tell which of their own files that is,
    which makes every line built on it unusable.

    Shown relative to the folder that was scanned, because that is the name the
    person typed and the part that tells two `notes.txt` apart. A file outside
    that folder keeps its full path rather than being guessed at.

    Nothing inside a protected container appears here, and not by omission: P3
    never walks into one, so no `files` row for its interior exists to read.
    """
    names: dict[str, str] = {}
    for row in conn.execute("SELECT file_id, current_path FROM files"):
        path = Path(row["current_path"])
        try:
            names[row["file_id"]] = str(path.relative_to(root))
        except ValueError:
            names[row["file_id"]] = str(path)
    return names


def _wrapped(text: str, *, indent: str) -> str:
    return textwrap.fill(text, width=78, initial_indent=indent,
                         subsequent_indent=indent)


def _files_of(decision) -> tuple[str, ...]:
    """The files one decision is about: a file version, or a group's members."""
    subject = decision.subject
    return ((subject.file_id,) if subject.file_id
            else tuple(subject.member_file_ids))


def _protected(decision, sets: Sequence) -> bool:
    """Whether this decision is about material that was marked, not opened.

    Three records can say so and they are not interchangeable: P7's flag travels
    on `privacy.protected`, P11's own `marked_state` says the file was marked
    rather than placed, and §7.5's review set carries the flag for a whole set.
    Any of them is enough, because the cost of treating an ordinary group as
    protected is a slightly longer list and the cost of the reverse is the
    silent omission the standing rule exists to forbid.
    """
    return bool(decision.privacy.protected
                or decision.marked_state == pv.PROTECTED
                or any(item.protected for item in sets))


def report(result: ProductionRun, names: dict[str, str], *, out=None) -> None:
    """The run, in the order a person would ask about it.

    Four questions, in this order: what was left alone, what folders are being
    proposed, what happens to each file, and what this needs from you.

    The protected containers come FIRST and are never folded into a total.
    "Marked and counted, never opened" is only true if the count is somewhere the
    person reads, and a line at the bottom of a long report is not that. The
    grouping below never reaches this block -- count, name, path and sentence are
    what the rest of the report is shortened around, not with.

    `names` is required rather than optional. A default would let the id-only
    report back in by nothing more than a forgotten argument.
    """
    out = out if out is not None else sys.stdout
    areas = result.protected_areas
    print(f"\nProtected containers: {len(areas)} marked, none opened", file=out)
    for area in areas:
        print(f"  {area.display_label}  ({area.label})", file=out)
        print(f"    {area.path}", file=out)
    if areas:
        print("  Nothing inside these was read, indexed, classified or moved, and "
              "none of them is a place anything can be filed.", file=out)

    tree = result.tree.tree
    places = len(result.destinations)
    print(f"\nProposed folders: {len(tree.nodes)}. {places} of them "
          f"{'is' if places == 1 else 'are'} somewhere a file can go.", file=out)
    by_parent: dict[str | None, list] = {}
    for node in tree.nodes:
        by_parent.setdefault(node.parent_node_id, []).append(node)

    def draw(parent, depth):
        for node in by_parent.get(parent, ()):
            mark = "" if node.accepts_placement else "   [marked, not a destination]"
            print(f"  {'  ' * depth}{node.display_label}{mark}", file=out)
            draw(node.node_id, depth + 1)

    draw(None, 0)

    labels = {node.node_id: node.display_label for node in tree.nodes}
    decisions = result.placement.decisions
    placed = sum(1 for d in decisions if d.outcome == pv.PLACE)
    sets_by_file: dict[str, list] = {}
    for item in result.placement.residual_sets:
        for file_id in item.member_file_ids:
            sets_by_file.setdefault(file_id, []).append(item)

    # One line per KIND of outcome, not one per file. Four files that stopped for
    # the same reason are four names and one reason, because the reason was one
    # fact the first time it was printed and stayed one fact the other three.
    members: dict[tuple, list[str]] = {}
    shielded: dict[tuple, bool] = {}
    for decision in decisions:
        # Deduplicated by identity, not by value: two review sets that happen to
        # read alike are still two sets, and folding them would lose one.
        sets, seen = [], set()
        for file_id in _files_of(decision):
            for item in sets_by_file.get(file_id, ()):
                if id(item) not in seen:
                    seen.add(id(item))
                    sets.append(item)
        where = (labels.get(decision.destination.node_id,
                            decision.destination.node_id)
                 if decision.destination else None)
        # A placement's folder is its whole answer; every other outcome owes the
        # person the sentence saying why it stopped.
        reason = "" if decision.outcome == pv.PLACE else decision.explanation
        review = tuple(f'Held for review as "{item.label}": {item.reason_not_placed}'
                       for item in sets)
        key = (decision.outcome, where, reason, review)
        members.setdefault(key, []).extend(_files_of(decision))
        shielded[key] = shielded.get(key, False) or _protected(decision, sets)

    rank = {outcome: index for index, outcome in enumerate(OUTCOME_WORDS)}
    ordered = sorted(members, key=lambda key: (
        # Protected first, exactly as `tree_design.health` ranks its warnings.
        not shielded[key], rank.get(key[0], len(rank)), key[1] or "", key[2]))

    print(f"\nFiles: {len(decisions)} decided, {placed} ready to file", file=out)
    for key in ordered:
        outcome, where, reason, review = key
        files = sorted(members[key], key=lambda f: names.get(f, f))
        heading = OUTCOME_WORDS.get(outcome, outcome)
        if where:
            heading = f"{heading} into {where}"
        plural = "" if len(files) == 1 else "s"
        print(f"\n  {heading} -- {len(files)} file{plural}", file=out)
        listed = files if shielded[key] else files[:NAMES_LISTED_PER_GROUP]
        for file_id in listed:
            print(f"    {names.get(file_id, file_id)}", file=out)
        rest = len(files) - len(listed)
        if rest:
            print(_wrapped(
                f"...and {rest} more, counted here rather than listed one by one "
                "so that the list stays shorter than the folder it describes; "
                "none of them is a protected area, which is never summarised "
                "away", indent="    "), file=out)
        if reason:
            print(_wrapped(f"Same reason for each: {reason}", indent="    "),
                  file=out)
        for note in review:
            print(_wrapped(note, indent="    "), file=out)

    # §7.5's sets are printed where the files they cover are printed, so the same
    # four files are never counted twice in two vocabularies. A set covering no
    # decided file has nowhere to be folded into and gets its own line: shortening
    # the report may not drop one.
    accounted = {file_id for files in members.values() for file_id in files}
    for item in result.placement.residual_sets:
        if not set(item.member_file_ids) & accounted:
            print(f"\n  Held for review as \"{item.label}\" -- "
                  f"{item.file_count} file(s), none of them decided here", file=out)
            print(_wrapped(item.reason_not_placed, indent="    "), file=out)

    print(f"\nNothing was moved.\nPlan version: {tree.plan_version_id}  "
          f"(the name this proposal is saved under)", file=out)


def main(argv: Sequence[str] | None = None, *, out=None) -> int:
    # Bound at CALL time, not as a default: a default argument is evaluated when
    # this module is imported, which pins the stream that existed then.
    out = out if out is not None else sys.stdout
    parser = argparse.ArgumentParser(
        prog="database-agent",
        description="Read a directory, propose a folder tree for it, and say "
                    "where each file would go. Nothing is moved.")
    # These three are required for a run and are NOT marked required here, because
    # `--list-situations` exists to tell a person what to pass to `--situation`. A
    # discovery flag that requires the answer it supplies is a closed door: the only
    # way to learn a situation name would be to already know one. argparse cannot
    # express "required unless another flag is set", so the requirement is enforced
    # below, after the listing returns, and it is enforced through `parser.error`
    # so the message and the exit code are the ones argparse would have given.
    parser.add_argument("directory", type=Path, nargs="?",
                        help="the folder to read")
    parser.add_argument(
        "--situation",
        help="which situation these files are, e.g. academic.coursework. Required: "
             "nothing upstream can answer it and this command will not guess. "
             "`--list-situations` prints every one the shipped library carries.")
    parser.add_argument(
        "--label",
        help="what to call the top-level folder, e.g. 'Coursework'. Required for "
             "the same reason.")
    parser.add_argument("--user", default=getpass.getuser(),
                        help="who this plan belongs to (recorded, never sent)")
    parser.add_argument(
        "--database", type=Path, default=None,
        help="where to keep the plan (default: ./database-agent-plan.sqlite). It "
             "may not live inside the folder being read.")
    parser.add_argument("--list-situations", action="store_true",
                        help="print every situation the shipped library carries")
    args = parser.parse_args(argv)

    catalogue = load_shipped_catalogue(read_packaged_library_file)
    if args.list_situations:
        for signal in sorted({s for row in catalogue.applicabilities.values()
                              for s in row.detection_signal_refs}):
            print(signal.removeprefix("recognition:"), file=out)
        return 0

    # The requirement argparse could not express. Same message and same exit code
    # it would have produced, so a run that forgets one reads no differently.
    missing = [name for name, value in (("directory", args.directory),
                                        ("--situation", args.situation),
                                        ("--label", args.label)) if value is None]
    if missing:
        parser.error("the following arguments are required: "
                     + ", ".join(missing))

    directory = args.directory.expanduser().resolve()
    if not directory.is_dir():
        print(f"{directory} is not a folder", file=out)
        return 2

    from datetime import datetime, timezone

    def now() -> str:
        return datetime.now(timezone.utc).isoformat()

    # `open_database` and not `sqlite3.connect`. It sets WAL, autocommit and
    # recursive triggers -- and `build_destination_index` issues a
    # `wal_checkpoint`, which fails outright ("database table is locked") on a
    # connection in Python's implicit-transaction mode. It also refuses a database
    # inside the folder being scanned, which is why the roots are passed in.
    database = args.database or (Path.cwd() / "database-agent-plan.sqlite")
    try:
        conn = open_database(database, scan_roots=[directory])
    except DatabaseInsideCorpus as refusal:
        print(f"\n{refusal}", file=out)
        return 2
    print(f"Plan database: {database}", file=out)
    try:
        result = run(conn, directory, situation=args.situation, label=args.label,
                     user_id=args.user, now=now)
    except NotConfigured as refusal:
        print(f"\nThis run was refused, and here is what it needed:\n  {refusal}",
              file=out)
        return 2
    except REFUSALS as refusal:
        # A NAMED refusal, printed rather than raised. §5's chain refuses by name
        # -- C1-C8, V1-V6, §5.4's empty branch -- and each refusal says which
        # judgement failed and why. A traceback here would turn an answer the
        # design worked hard to give into a crash.
        print(f"\nNo plan was made for {directory}, and this is why:\n"
              f"  {type(refusal).__name__}: {refusal}", file=out)
        return 1
    report(result, file_names(conn, directory), out=out)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
