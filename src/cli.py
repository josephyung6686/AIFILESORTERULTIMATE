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
import dataclasses
import getpass
import random
import hashlib
import json
import os
import re
import secrets
import shlex
import sqlite3
import sys
import uuid
import textwrap
import unicodedata
from collections import namedtuple
from decimal import Decimal
from itertools import count
from pathlib import Path, PurePosixPath
from functools import lru_cache, partial
from types import MappingProxyType
from typing import Callable, Mapping, Sequence

from database_agent.budget import set_ceiling
from database_agent.cloud_consent import (
    DISABLED, ENABLED, CloudConsent, cloud_consent_for, record_cloud_consent,
)
from database_agent.db import DatabaseInsideCorpus, open_database
from database_agent.files_table import (
    PATH_NO_LONGER_EXISTS, SUPERSEDED_CONTENT, get_file,
)
from extractors.archive import (
    EXTRACTOR_NAME as ARCHIVE_EXTRACTOR_NAME,
    LOCKED_REASON_PREFIX,
)
from extractors.image import PERCEPTUAL_HASH_FIELD
# `SOURCE_TYPE_BY_FORMAT` was imported here for `_detect_format`'s extension
# shortcut, which `104` §18.2 gap 21 deleted. `readers/signatures.py` imports it
# directly -- it is the reader that needs to know which extensions the router
# already understands, and this module no longer asks that question.
from extractors.reading import StructuredString
from extractors.structured_text import EXTRACTOR_NAME as STRUCTURED_EXTRACTOR
from extractors.filesystem import SOURCE_TYPE as FILESYSTEM_SOURCE_TYPE
from extractors.safety import SafetyPolicy
from facts.date_facts import date_facts
from facts.dates import (
    ACADEMIC_YEAR_RANGE, NAMED_TERM_YEAR, SEASON_YEAR, YEAR_RANGE_SEMESTER_NUMBER,
    YEAR_RANGE_TERM_NUMBER, DatePattern, DatePatterns,
)
from facts.direct import DirectSlot, DirectSlots, direct_facts
from facts.families import (
    DUPLICATE_FAMILY_FIELD, VERSION_FAMILY_FIELD, duplicate_family,
    shared_family_field,
)
from facts.discount import MetadataScreen
from facts.learning import NoSuchClaim, reject_claim
from facts.domains import ActivationSignal, ActivationSignals
from branch_situation import (
    Branch, BranchPartition, partition_by_branch, single_owner_terms,
)
# `MEDIA_TYPE_FIELD` left this import with `104` R-09: the retired
# `active_schema_for` literal was the only line in this file that named it.
from facts.photo_event import media_type
from facts.budgets import LLM_ROUTE
from facts.resolver import BUDGET_BAR, PRIVACY_BAR, FactResolver
from facts.anchor_statements import (
    anchor_statements_for, record_anchor_statements,
)
from facts.rules import ACADEMIC_CONTEXT_TERMS, Rule, apply_rules
from facts.unresolved import BUDGET_DEFERRED, NO_CANDIDATE_EVIDENCE
from facts.usable import record_pass
from facts.fields import DOMAIN_FIELDS
from facts.read_surface import (
    DanglingCitation, confirmed_spellings, evidence_chain, versions_in_fields,
)
from facts.file_facts import facts_for_file
from facts.states import (
    LLM_SUPPORTED as LLM_SUPPORTED_STATE,
    POSSIBLE,
    REJECTED as REJECTED_STATE,
    VALIDATED,
    strength,
)
from facts.kind import tokens as kind_tokens
from facts.kind import compile_vocabulary, kind_facts
from grouping.acceptance import group_state_as_of, record_acceptance
from grouping.seeds import ANCHOR_STATES
from grouping.config import GroupingLimits
from grouping.embeddings import (
    EmbeddingConfig, EmbeddingsOff, EmbeddingsOn, EncodedVector,
    FileVersionRef)
from grouping.p8_seam import Answered, MemberDecision, ModelAnswer, ObservedOnly
from placement.vocabulary import GROUP
from grouping.pipeline import (
    GroupingKnowledge, GroupingResult, ModelCallAuthorities,
)
from grouping.records import Group, GroupAcceptance
from grouping.retrieval import EmbeddingIdentity, RetrievalKnowledge
from grouping.schema import create_grouping_schema
from grouping.store import (
    carry_memberships, current_group, live_memberships_of_file,
    memberships_for_group, record_group, record_membership,
    stop_rule_outcome_for,
)
from grouping.vocabulary import (
    ABSTAINED, ACCEPTED, BOUNDED_SESSION, COHERENT, COMPATIBLE_DOCUMENT_TYPE,
    DUPLICATE, EDGE_TYPES as P9_EDGE_TYPES, EXCLUDED, EXISTING_RELATED_FOLDER,
    INCLUDED, MUTUAL_SEMANTIC_RETRIEVAL, NOT_COHERENT, P1_INCLUDED_SCAN_STATE,
    PENDING_REVIEW, RULES, SHARED_VALIDATED_FACT, UNCERTAIN, USER_EDITED,
    VERSION_FAMILY, fact_bridge_ref,
)
from llm_harness.budgets import ScanBudget, create_budget_schema
from llm_harness.prompt_library import (
    a_fact_response_schema_bytes, a_fact_shaping_policy_bytes,
    DRAFT_STATUS_WORDS, RATIFIED, RATIFIED_LOCAL,
    a_fact_row as prompt_library_a_fact_row,
    a_fact_template_folder_levels_bytes, draft_bytes, draft_status,
)
from llm_harness.harness import CallDependencies, run_call
from llm_harness.records import (
    CallRefused, FolderLevel, P8Verdict, PromptDefinition,
)
from llm_harness.situation_validation import is_decline
from llm_harness.store import grounding_counters, last_response_bytes
from llm_harness.sites import SiteDependencies
from llm_harness.schema import create_llm_schema
from llm_harness.vocabulary import (
    A_FACT, B_GROUP, C_PLACEMENT, CONTEXT_SUPPORTED, D_RESIDUAL, DIRECT_ANCHOR,
    ACCEPT_CONTEXT_SUPPORTED, ACCEPT_DIRECT,
    E_TEMPLATE, G_SITUATION_SENSITIVITY, LLM_SUPPORTED, PRE_CALL_NAMESPACE,
    SCOPE_FILE, SCOPE_TEMPLATE as TEMPLATE_SCOPE, pre_call_address,
)

#: The two outcomes that mean P8 accepted the answer. `OUTCOMES` also holds `weak`,
#: `reject` and `abstain`, and none of those is an answer to apply -- `worst_outcome`
#: is what makes one verdict speak for a whole call, and this is the pair that lets
#: a caller act on it. Named because `104` §17.1's site tests membership and a
#: literal pair at the call site would be the second spelling brief §11 bans.
ACCEPTING_OUTCOMES: frozenset[str] = frozenset(
    {ACCEPT_DIRECT, ACCEPT_CONTEXT_SUPPORTED})
from model_situation import (
    NONE_OF_THESE, SITUATION_SENSITIVITY, NothingToAsk, build_situation_request,
    question_for,
)
from placement import vocabulary as pv
from placement.config import CEILINGS, SupportPolicy, placement_limits
from placement.graph import (
    COMPATIBLE_DOCUMENT_TYPE as P11_COMPATIBLE_DOCUMENT_TYPE,
    DUPLICATE as P11_DUPLICATE,
    EDGE_TYPES as P11_EDGE_TYPES,
    EXISTING_RELATED_FOLDER as P11_EXISTING_RELATED_FOLDER,
    SHARED_VALIDATED_FACT as P11_SHARED_VALIDATED_FACT,
    VERSION_FAMILY as P11_VERSION_FAMILY,
)
from placement.pipeline import (
    PipelineInputs, ResidualSendRefused, act_on_residual_sets,
)
from placement.residual import ProtectedSetNotReadable, prior_set_decisions
from placement.schema import create_placement_schema
from model_facts import (
    AnchorOnlyLevels, FactCallAuthorities, dossier_tokens, fact_call_stage,
    measure_released_tokens, pending_fields_for, releasable_observations,
    releasable_readings, zone_evidence_counts,
)
# `104` §18.2 gap 4: the module and not its names, because `NOT_ASKED_SENTENCE`
# below reads five of its constants and a five-name import line beside the one above
# would be the same list written twice.
import model_facts
from privacy.classification import (
    ClassificationRecord, UNREADABLE_UNCLASSIFIED, privacy_class_for,
    resolve_class,
)
from privacy.classification_store import ClassificationStore
from privacy.learning_seam import assign
from privacy.denial import (
    UNCLASSIFIED_PERMITS_LOCAL, mode_forbids, protected_cloud_denies,
    unclassified_denies)
from privacy.gate import Gate
from privacy.defaults import LOCAL_FIRST_MODES
from privacy.display import display_policy
from privacy.moves import may_move_automatically
from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy
from privacy.resolve import (
    AmbiguousObservationKey, UnresolvableSpan, current_location,
    current_observation, filename_address,
)
from privacy.vocabulary import (
    ALWAYS_LOCAL_ZONES, CLOUD_LOCALITY, CONSENT_OPTIONS, LOCAL_MODEL_SITUATION,
    MODE_SEMANTICS, RESTRICTED_KINDS,
)
from questions.explanation import explain_question, render_explanation
from questions.effects import changed_answer, diff_for_answer_change
from questions.explanation import explain_question, render_explanation
from questions.proposal import propose_roles
# TWO `questions.records` LINES, DELIBERATELY, AND THIS IS THE WHOLE REASON.
# `../reach/CLI-PATCH.txt`'s PATCH C1 anchors on `from questions.records import
# StructuralAnswer` verbatim. Merging `AnswerNotPermitted` into that line would
# consume their anchor, so applying this patch first would make C1 fail to
# match -- measured, not assumed. Leaving the line untouched makes the two patch
# files independent in BOTH directions rather than in one, which is a property
# instead of an ordering rule somebody has to remember. Once both have landed,
# the two lines may be merged into one.
from questions.records import AnswerNotPermitted
from questions.records import StructuralAnswer
from questions.role_report import (
    questions_a_run_could_not_settle, role_moment_lines, role_panel_lines,
    shortlist_lines,
)
from questions.registry import SITUATION_KIND, kind_of
from questions.roles import (
    apply_declarations, apply_descriptions, described_sentences, live_roles,
)
from questions.schema import create_questions_schema
from questions.store import (
    activated_schemas, chosen_destination, gated_template, live_answer,
    selected_situation,
    live_answer_id,
    open_questions,
    record_answer,
    record_question, set_aside_questions,
)
from questions.triggers import (
    DestinationChoice, NestingChoice, question_for_nesting,
    question_for_situation,
    question_for_unreadable_folder, tied_readings_and_the_files_they_reach,
)
from questions.vocabulary import (
    CONFIRMED, REVOKED, SCOPE_BRANCH, SCOPE_FOLDER, SKIPPED,
)
from production import (
    CorpusAuthorities, CorpusDecisions, P1P7Authorities, ProductionRun,
    bootstrap_p1_p7, corpus_roster, folder_levels_for, group_level_fields_for,
    GROUP_LEVEL_ROLES, load_shipped_catalogue,
    nearest_situations, read_packaged_library_file, schema_for_situation,
    shipped_situations, situation_schema_family,
    run_production_corpus,
)
from readers.deployment import macos_readers
from readers.pdf_pdfium import pdfium_reader
from readers.signatures import signature_detector
from extraction_pool import ExtractionContext, ProcessPool
from model_placement import (
    PlacementCallAuthorities, model_path_injections, releasable_excerpts,
)
from readers.model_deepseek import BASE_URL_NAME, CLOUD, CREDENTIAL_NAME
from readers.model_ollama import (
    BASE_URL_NAME as LOCAL_BASE_URL_NAME,
    LOCAL,
    MODEL_NAME as LOCAL_MODEL_NAME,
)
from readers.model_routing import (
    FAST, LOGIC, MODEL_NAME_OF_TIER, REASONING, TierRouting,
    cloud_and_local_routing, deepseek_routing, ollama_routing,
)
from facts.domains import SCHEMA_IDS
from recognition.detector import (
    FIRST_PAGE, NAMING_ZONES, SAFETY_DOMAIN_HANDLING, Abstention, Detector, Handling,
)
from recognition.rules import load_rules
from recognition.semantic import (
    FLOAT32_LE, SemanticFloors, SemanticRecogniser, build_schema_anchors,
    evidence_text,
    schema_similarity_from, scope_for,
)
from scan_agent.corpus_source import FilesystemCorpusSource

# §8.5's replay. `evaluation` is the composition layer's own module, beside
# `orchestrator` and `production`: the stage adapter it publishes reads P2's
# bundle and hands the row to P5's mapping, and neither part may import the
# other -- P5's only run-time dependency is P1, and P2 re-spells P5 rather than
# importing it. A function that touches both is therefore neither part's.
from evaluation import (
    BUNDLE_ADAPTERS, bundle_baseline, record_bundle, recorded_bundles,
    recorded_lines, replay_lines, resolve_bundle, stage_status,
)
from eval_harness.bundle import RecordingNameTaken, bundle_named
from grouping.acceptance import group_state_as_of
from scan_agent.replay import CORPUS_FORM_SNAPSHOT, RecordingCorpusSource, snapshot_from
from scan_agent.exclusion import is_protected_container
#: `104` §18.2 gap 21's second guard. `_detect_format` opens files now, and the OTHER
#: class of file that must not be opened is the iCloud-evicted one -- see that
#: function for the whole argument.
from scan_agent.dataless import is_dataless
from scan_agent.selection import record_selection
from scan_agent.summary import scan_run_summary, set_aside_paths
from tree_design.catalogue import TemplateCatalogue
from tree_design.config import ConfigurationRequired, TreeLimits
from tree_design.freeze import FreezeRefused
from tree_design.materialise import MaterialisationRefused
from tree_design.pipeline import (
    NothingToDesign, SharedMaterialAnswer, TreeDesignAuthorities,
    TreeDesignDecisions,
)
from tree_design.store import ReviewActionRefused
from tree_design.template_schema import (
    allowed_vocabulary_for, template_dependencies,
)
from model_template import template_request_for
from tree_design.templates import CompositionConflict
from scan_agent.selection import selection_candidate_roots
from tree_design.upstream import (
    AnchorAgreement, UpstreamUnavailable, existing_folders,
    file_ids_in_directory, handling_class_for, protected_areas,
    settled_values_by_directory,
)
from tree_design.schema import create_tree_schema
#: The one word this command may put in a record's subject position. P10 already
#: spells it for §8.2's event sentences; `refinement_for` and the residual home's
#: reason read it from the same place, so the frozen tree and the audit log cannot
#: end up naming two different actors for one run.
from tree_design.provenance import actor_phrase
from mutation.schema import create_mutation_schema
from mutation import vocabulary as mv
from mutation.constraints import FilesystemConstraints
from mutation.resolution import source_high_level_folder
from tree_design.store import nodes_for_version
from apply_run.approval import approval_reader, approval_writer
from apply_run.branches import BranchRefused, branches_named
from apply_run.freeze import freeze, frozen_plans
from apply_run.report import apply_lines, freeze_lines, undo_lines
from apply_run.run import (
    already_applied, applied_entries, apply_selected, plans_under, take_back,
)
from review_run.progress import progress_lines
# `104` §18.2 gap 10. The rule -- "no indexed file may be absent from every entry"
# -- asked for BY NAME, from the module that owns it, rather than restated here by
# the pass it is meant to check. `progress_lines` above reaches the same function
# through P13's own §8.6 line, which is a different question over P4's extraction
# states; this run needs the rule over a set of buckets P13 knows nothing about, so
# the function is imported directly and nothing in P13 is widened to hold them.
from review_surface.progress import (
    UNREADABLE, assert_every_file_accounted, bucket_for,
)
from review_surface.records import ProgressEntry
from review_surface.schema import create_review_schema
from review_surface.vocabulary import (
    ACTION_REJECT, SOURCE_P4_RUNS, SOURCE_P8, STATE_BLOCKED, STATE_COMPLETED,
    STATE_DEFERRED,
)
# `104` §18.2 gap 10: P4's own extraction record, for the files the fact pass
# never reached. Read through P4's published reader rather than a query of this
# file's own, so "this file could not be read" means here exactly what it means on
# §8.6's line and the two screens cannot disagree about one file.
from evidence_shape.store import runs_for_content
from tree_design.residuals import (
    ResidualChoice, ResidualTemplate, build_library,
)
from tree_design.vocabulary import (
    ENABLE, MANDATORY_REVIEW, PHYSICAL_DESTINATION, REFINE_LATER, REFINED,
    RESIDUAL_TEMPLATE_NAMES, SHALLOW_BY_CHOICE, SURFACE_UNATTENDED,
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
#: scale, 0.50 as the support bar, and 0.20 as the margin. A run under these is
#: auditable because `policy_id` travels on every decision -- change a number and
#: change the id with it, or a replay silently compares two different rules.
#:
#: **THE NUMBERS DID NOT MOVE AND THE SCALE UNDER THEM DID (`104` §18.2 gap 13),
#: which is why the id moves.** The old comment justified 0.50 as "the band a
#: direct fact alone (3/7 = .429) falls below and a direct fact plus an accepted
#: group (5/7 = .714) clears" -- an argument that reads as a choice and was a
#: consequence: the scorer divided by all four deciding weights while
#: `placement/retrieval.py` produced two of them, so two sevenths of the scale
#: belonged to channels with no producer anywhere and a file whose facts uniquely
#: matched one folder could not clear the bar on facts. `00`:110's unique direct
#: match was unreachable without a group membership, and "ready to file" read near
#: zero whatever the evidence said.
#:
#: `scoring.producible_weight` now derives the denominator from the channels the
#: retrieval declares it produces, so the attainable set is {0, .4, .6, 1.0}
#: instead of {0, .286, .429, .714}: an accepted group alone falls short at .4,
#: direct facts alone clear at .6, and both together are 1.0 of what is
#: producible. THE BAR IS THE SAME 0.50 AND NOW DIVIDES A SCALE THE RUN CAN
#: REACH.
#:
#: **The id is `cli-support-v2` because every recorded `support_score` means
#: something different from here on.** The policy's own docstring says a changed
#: threshold must be identifiable in a replay; a changed SCALE under an unchanged
#: threshold is the same hazard wearing the number's old clothes, and a replay
#: comparing a v1 decision's .714 against a v2 decision's 1.0 would be comparing
#: two rules that share an id. Nothing else about the policy changed.
SUPPORT_POLICY = SupportPolicy(
    policy_id="cli-support-v2", support_scale_max=1.0,
    minimum_support_threshold=0.50, margin_threshold=0.20)

#: P1's ceilings, which every other part reads through its own config module.
#: `00` §8.6 names the ceilings and states no values, so these are this
#: deployment's. Eight is small on purpose: it bounds a first run on a real
#: person's disk rather than optimising one.
CEILING_VALUE: int = 8

#: ONE OF THE SEVEN IS NOT A SPEND CEILING, and it carried `CEILING_VALUE` only
#: because it was in the same loop. `residual.max_files_per_review_batch` does
#: not bound what a run COSTS -- it bounds how many files a person is shown in
#: one review set, and §8.6 splits a set at this number rather than truncating
#: it. So the name says what it is: a screenful of files, not a spend.
#:
#: TWENTY-FIVE, AND NOT EIGHT, IS A NUMBER SOMEBODY CHOSE. Eight was the spend
#: ceiling's, and `104` R-93 is the row that says so: a person read "Not yet
#: placed (1 of 4)" through "(4 of 4)" on 52 files and nobody had picked the 4.
#: Twenty-five is one screen's worth -- the count a person can still read
#: before saying yes to it -- and it is PROPOSED IN `104` §15.3, pending the
#: owner's word. It is not ratified and this comment may not say it is.
#:
#: TWO CLAUSES TRAVEL WITH THE NUMBER. It applies WITHIN a reason set (R-115),
#: which is the division a person can act on, so it never divides files that
#: belong together until 25 of them share one reason. And a set of 25 or fewer
#: is UNNUMBERED: "(1 of 1)" names a split that did not happen.
#:
#: It also decides how many separate `--send-set` commands a person must type to
#: file one hold. That was measured at eight -- 420 sets from a single hold on a
#: 5,000-file corpus, and therefore 420 commands -- and 25 divides the same hold
#: into roughly a third as many. The trade the old comment named is real and the
#: number does not settle it: a larger set is fewer commands AND a bigger set
#: accepted in one gesture with no per-file look, which is exactly the scrutiny
#: `--send-set` spends. One screen is where the two meet.
#:
#: The question beside it is still open and is still the owner's: whether one
#: gesture should be able to address a HOLD instead of a batch (`84` §1). That
#: is a gesture change, not a number.
FILES_PER_REVIEW_SCREEN: int = 25

#: §5.7's and §5.9's tree bounds. `00` states no numbers for these either.
TREE_LIMITS = TreeLimits(
    # `00`:256's two numbers, since P1 publishes them separately. Four options
    # is a picker a person can read; five levels is `00`:78's own recommended
    # tree, `Academics/Columbia/2026-Spring/PHYS1401/Homework`, which a depth
    # limit of four would refuse.
    max_folder_proposals=4, max_depth=5, max_dossier_tokens=4000,
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
#:
#: IT IS ALSO THE REASON NO MODEL RUNS, and that had been invisible.
#: `privacy.denial.mode_forbids` denies every `locality="cloud"` release under
#: `offline`, so a file that needed a judgement reported "§8.4 did not clear this
#: file for a model call" -- a sentence a person reads as a fact about their own
#: file when it is a fact about this line. `model_route` below says which it is.
OPERATION_MODE: str = "offline"

# §8.4's Open question 5 -- may an unclassified file reach a LOCAL model? -- IS NO
# LONGER ANSWERED HERE. It was a `True` pinned on this line while
# `placement/privacy.py` pinned `False` on another, which is `104` R-121: one
# question, two places deciding it, and the second one blocking the 86 unclassified
# files of the owner's local run before the gate was ever asked. The owner ruled it
# one answer under one name (`104` §15.3), and that name is
# `privacy.denial.UNCLASSIFIED_PERMITS_LOCAL`, imported at the top of this module
# and read as `cli.UNCLASSIFIED_PERMITS_LOCAL` at both call sites below, by
# `tools/groundtruth/payload.py`, and by the tests that pin the route and the gate
# to one answer. Importing it rather than restating it is the whole fix.

#: The mode a person selects by enabling cloud sending, and the choice between
#: §8.4's two non-local modes is not a detail.
#:
#: `cloud_assisted` is the one that SOUNDS right -- "User explicitly permits
#: selected corpus areas to use a cloud model" is almost a description of
#: `--enable-cloud`. It is refused for two reasons, and the second decides it.
#:
#: 1. It cannot be spelled honestly today. What a "corpus area" IS is P7's **Open
#:    question 3** (`privacy/vocabulary.py`): *"A scan root, a frozen tree node, an
#:    accepted group, a domain? Consent grants cannot be scoped until this is
#:    named."* It is unanswered, and `tests/p7/test_p7_no_invention.py` fails the
#:    moment it is answered inside `src/privacy/`.
#: 2. **`cloud_assisted` is the WEAKER mode, not the stronger one.**
#:    `privacy/denial.py`'s `protected_cloud_denies` lets a PROTECTED file reach a
#:    cloud target under exactly one condition: `cloud_assisted` plus a grant
#:    naming its scope. Under `hybrid` that function returns True unconditionally
#:    and protected material can never leave. The permissive-sounding name is the
#:    one carrying the carve-out for the material this product promises never to
#:    open, so choosing it would trade a standing guarantee for a sentence.
#:
#: `hybrid`'s own sentence -- "Sensitive files remain local; non-sensitive bounded
#: dossiers may use a cloud LLM" -- is also the one that is TRUE of what is built:
#: `ALWAYS_LOCAL` and the classification store are untouched by any of this, which
#: `83` §4 requires ("No tier changes what may be SENT").
CLOUD_ENABLED_MODE: str = "hybrid"


def _weakest_consent(consents) -> "CloudConsent | None":
    """The least permissive decision across the folders one run reads.

    `00`:20 lets a person name several folders and §8.4 keys consent to a
    folder, so a multi-source run holds several answers to one question. They
    are not averaged and the first is not preferred: one dossier is built from
    all of them, so a single folder that nobody cleared is enough to keep the
    whole run off the cloud. A `None` among them -- nobody decided -- is
    returned as `None`, which is what `operation_mode_for` already reads as the
    local-first floor.
    """
    settled = None
    for consent in consents:
        if consent is None or not consent.permits_sending:
            return consent
        settled = settled if settled is not None else consent
    return settled


def operation_mode_for(consent: CloudConsent | None) -> str:
    """Which of §8.4's modes this run operates under. THE policy, in one place.

    Absent is not ambiguous and is not a gap: nobody has decided, so the run stays
    on the local-first floor. The default is what happens by NOT choosing, which is
    `80` §8's first condition and the only arrangement under which forgetting is
    safe.
    """
    if consent is not None and consent.permits_sending:
        return CLOUD_ENABLED_MODE
    return OPERATION_MODE


def _unranked(candidates: frozenset[str]) -> tuple[str, ...]:
    """`80` §5 (R7): the order a person sees, chosen where policy is chosen.

    > Shortlist ORDER itself is information the person will use whether or not you
    > intend it to be. Even "unordered" presentation isn't neutral if the UI renders
    > a list top-to-bottom -- position seven versus position one still reads as
    > ranked to a human, regardless of your intent.

    and the mitigation "must be stronger than 'do not sort by confidence'". The data
    already refuses to carry an order -- `RoleProposal.candidates` is a `frozenset`,
    which cannot be indexed -- so the only place left for a ranking to reappear is
    the geometry of the render, and this is that place.

    Every alternative available here is a ranking. Sorted ranks by an irrelevance and
    puts `academic` first for everybody forever; set iteration is an order nobody
    chose, which is worse because it looks deliberate; the model's own order is the
    one R7 exists to remove. `80` §7 names randomising per render as acceptable, so
    that is what this is.

    UNSEEDED, deliberately. A seed makes the order stable between renders, and an
    order that is stable is an order a person learns, which is the ranking again.
    The cost is that this function is the one thing in the report a test cannot
    assert the exact output of; asserting the SET is what a test of an unranked
    list should be doing anyway.
    """
    return tuple(random.sample(sorted(candidates), len(candidates)))

#: `83` §3's table, and the only place in the product where it exists. WHICH tier a
#: call site requires is a judgement about what being wrong COSTS THE PERSON, so it
#: is chosen here and nowhere else; WHICH model a tier resolves to is a deployment
#: fact and lives in `.env`. `83` §3's last row -- "anything not listed refuses" --
#: is `TierRouting`'s behaviour rather than a row here: a site absent from this
#: mapping gets a refusal naming it, never a tier it did not choose.
TIER_OF_CALL_SITE: Mapping[str, str] = MappingProxyType({
    # The one that becomes folder structure, and the one a person finds out about
    # months later. `83` §3 gave it REASONING, and measurement on the owner's own
    # files took it back: on four real dossiers `deepseek-v4-pro` answered NONE of
    # them -- `finish_reason == "length"`, the whole ceiling spent on reasoning,
    # `content` empty, ~110 seconds each -- while a non-reasoning model answered all
    # four in under five seconds with every claim cited and every unevidenced field
    # returned as an insufficiency statement.
    #
    # `00` §3.6 demands the model return `unknown` rather than guess, and the model
    # that actually did that is the cheaper one. The cause is `82`'s ratified line
    # "Think for as long as you need to before you answer": a reasoning model sharing
    # one budget between thinking and writing never starts writing. The template is
    # the owner's, so this row is the end that moves.
    #
    # LOGIC and not FAST: A_fact is `83`'s own "bounded, checkable,
    # verification-shaped" -- every claim is re-checked against extracted evidence --
    # and it is not FAST's "low stakes, individually cheap to get wrong".
    A_FACT: LOGIC,
    # Bounded, checkable, verification-shaped: each verdict is re-checked against
    # evidence already extracted, so a cheaper reasoner is not a risk.
    B_GROUP: LOGIC,
    C_PLACEMENT: LOGIC,
    E_TEMPLATE: LOGIC,
    # High volume by construction -- these are the files nothing else could place
    # -- and §7.6 makes the person authorise the spend per set beforehand.
    D_RESIDUAL: FAST,
    # `104` §17.1's seventh site. LOGIC, on A_FACT's own argument and not on a new
    # one: the answer is one identifier out of a list the recognisers raised, every
    # citation behind it is re-checked against evidence already extracted, and the
    # decline is always available -- which is `83`'s "bounded, checkable,
    # verification-shaped" exactly. It is NOT FAST: this site is where a medical
    # record either is or is not recognised as one before anything else happens to
    # it, so being wrong here is not "low stakes, individually cheap to get wrong".
    # It is not REASONING either, for the reason measured at A_FACT one row up: the
    # ratified text says "Think for as long as you need to before you answer", and a
    # reasoning model sharing one budget between thinking and writing never starts
    # writing.
    G_SITUATION_SENSITIVITY: LOGIC,
})

#: §8.6's response ceiling, in tokens. `00` names the ceiling and states no value,
#: so this is this deployment's. The cost of it being too small is a REFUSAL that
#: says so: `readers.model_deepseek` raises on `finish_reason == "length"` rather
#: than returning half a document for P8 to reject on the model's behalf.
#:
#: **RAISED FROM 2048 TO 8192, AND THE CEILING WAS NEVER THE FIX.** An earlier
#: comment stood here claiming 8192 had been measured to solve the empty answers, on
#: the strength of one call that returned `work_type = "Syllabus"`. Re-measured on
#: four real dossiers built from the owner's own files, that result did not
#: reproduce: at 8192 the reasoning tier returned `finish_reason == "length"`,
#: `completion_tokens == 8192` and ZERO answer characters on four of four. Raising a
#: shared thinking-and-writing budget buys a reasoning model more thinking, not an
#: answer, and the correction is recorded here rather than quietly deleted.
#:
#: What fixed it is `TIER_OF_CALL_SITE` above -- the model, not the number.
#:
#: 8192 is kept because the value is now nearly free: a non-reasoning model is billed
#: for what it writes, and the ANSWER is bounded by the response schema at a claim
#: per field. The measured answers ran 522 to 2,961 characters, so the headroom is
#: real and unspent. What the ceiling still buys is the refusal below it: a truncated
#: answer is refused by name rather than validated in half.
MAX_RESPONSE_TOKENS: int = 8192

#: HOW LONG ONE MODEL CALL MAY TAKE BEFORE THE RUN GIVES UP ON IT, in seconds, and
#: the only place the number is chosen. `deepseek_invoke` refuses to be built
#: without one.
#:
#: WHY IT EXISTS. The transport built its client with no timeout and no retry
#: ceiling, and the library's own defaults are ten minutes PER ATTEMPT with retries
#: on top. Measured: the first time a real client reached a `--enable-cloud` test,
#: the whole suite stopped dead for ten minutes with no output -- twice. In a
#: person's ten-thousand-file scan the same silence is a run that never finishes.
#:
#: WHY NINETY. Measured against the live API on this owner's account: a ten-file
#: batch answered in 3.4 seconds on `deepseek-chat`, and 16.5 seconds on a
#: reasoning tier that spends its budget thinking before it writes. Ninety is
#: roughly five times the slowest observed answer -- long enough that a slow but
#: healthy call is never cut off, short enough that a dead socket is not mistaken
#: for patience.
#:
#: **IT IS NOT A DEADLINE, AND THE DIFFERENCE IS MEASURED.** `httpx` applies this
#: per read, not to the call as a whole, so a request that keeps trickling bytes
#: outlives it: one observed call ran 109 seconds under this ninety. It bounds a
#: SILENT socket, which is the failure that stopped the suite dead for ten minutes,
#: and it does not bound a slow one. A total deadline is a different mechanism and
#: is not built here. §8.6 bounds model SPEND and says nothing about a call that never
#: returns, so this is not a budget ceiling and a call that hits it is not
#: `budget_deferred`; it is a failed call, and P8 records it as one.
MODEL_CALL_TIMEOUT_SECONDS: float = 90.0

#: HOW LONG ONE LOCAL CALL MAY TAKE, and it is not the cloud number. A provider
#: answers a bounded dossier in seconds and closes an idle socket itself; a model
#: on this machine is doing the arithmetic on this machine, sharing the GPU with
#: whatever else the person is running, and has nobody to close the connection.
#:
#: Measured 2026-09-05, `qwen3:8b` on this deployment: 8,194 prompt tokens plus a
#: short answer took 81.7 seconds; a cold model added 8.1 seconds of load on top of
#: the first call of a run. The cloud number (90 s) would have refused that call and
#: recorded the file as one the model declined.
#:
#: The cost of the two directions is not symmetric. Too long and a person waits;
#: too short and the file is recorded as unanswered by a model that was answering.
LOCAL_MODEL_TIMEOUT_SECONDS: float = 600.0

#: THE LARGEST CONTEXT WINDOW THIS DEPLOYMENT WILL ASK A LOCAL MODEL TO HOLD OPEN,
#: in tokens, and the bound `readers.model_ollama` refuses above rather than letting
#: ollama truncate a dossier in silence. It is also the window every call in a run
#: ACTUALLY ASKS FOR, and not merely a ceiling over smaller ones: ollama holds one
#: context length per loaded model, so a request naming a different `num_ctx`
#: unloads and reloads it -- measured at 283 seconds, more than the prompt
#: evaluation and the answer together -- and a scan whose dossiers differ in size
#: would pay that on every crossing, to save KV cache no scan can spend.
#:
#: 32,768, and both directions are measured. It is under `qwen3:8b`'s own advertised
#: 40,960, so the model can actually hold what is asked for. And the KV cache is
#: real memory: measured on 2026-09-05, ollama's resident set went 5.11 GB -> 5.72 GB
#: at `num_ctx` 8,192 and -> 6.85 GB at 16,384, so this ceiling is about 3 GB above
#: the model itself in the worst case and fits the machines this product is for.
#:
#: A dossier that will not fit is refused BY NAME and the file keeps its open
#: fields. The alternative was measured and is why this number exists at all: at
#: every window tried, an oversized prompt was silently cut and answered anyway,
#: with a value that was never in the evidence.
#:
#: ONE LOAD PER RUN IS THE PROMISE, AND A SHARED SERVER IS WHAT BREAKS IT. Measured
#: 2026-09-06 on the five-file smoke: `num_ctx` was 32,768 on all four calls and
#: ollama still reported 62-87 seconds of `load_duration` on EVERY one of them,
#: 319.5 seconds out of 598.8 -- 53% of the run spent loading a model that should
#: have loaded once. The cause is not this number and not `readers.model_ollama`.
#: `/api/ps` reported `context_length` 8,192, then 16,384, then 16,384 again either
#: side of the run: another bench on this machine is calling the same ollama with a
#: different window, and one context length per loaded model means the two evict
#: each other. The premise above holds for a single consumer of the server, which
#: is the deployment this product ships into; it is not a defect to fix here, and
#: a latency number measured against a shared server is an upper bound.
#:
#: AND THE PROMPT'S ORDER IS A LATENCY LEVER, which is the A_fact template's to
#: pull and not this file's. ollama reuses its KV cache across requests for as long
#: as the prompts share a PREFIX, so a template that puts what every file has in
#: common first -- the authored prompt, the folder levels, the allowed vocabulary --
#: and the file's own dossier LAST lets each call re-evaluate only its own tail.
#: Put the dossier first and every file is a fresh prompt from its first token, at
#: the ~4,200 prompt tokens and ~85 seconds of evaluation this smoke measured. The
#: window is what makes the cache POSSIBLE by staying constant; the section order
#: is what makes it PAY.
#:
#: 24,576 SINCE 10 Sep 2026 (`104` §18.15, the owner's word at 00:05), AND THE
#: ARITHMETIC IS THE REASON. 32,768 was sized when a dossier could be 96 KB;
#: `104` R-174 bounds the released list in wire bytes, so the largest prompt the
#: product can build is the largest template in the library (~11.6 KB) plus the
#: dossier frame plus the released bound plus the evidence items that count bounds
#: -- about 24 KB, ~12,400 tokens at `BYTES_PER_TOKEN_FLOOR`, ~8,700 measured on
#: r18's 199 files -- and with `MAX_RESPONSE_TOKENS` on top it needs ~20,600. The
#: window holds it with ~4,000 tokens to spare on the conservative bound; a prompt
#: past it is REFUSED (`OllamaContextExceeded`), never truncated, so nothing is
#: lost in silence -- and `tests/readers/test_local_window_holds_the_largest_
#: prompt.py` builds that bound from the library and the limits and holds it. What
#: the smaller window buys is ~1.2 GB of KV cache the server no longer reserves,
#: which is the memory that pushed the machine into swap on 9 Sep.
LOCAL_CONTEXT_CEILING: int = 24576

#: Where this deployment keeps its own values. Read here and nowhere else in `src/`.
ENV_FILE: Path = Path(__file__).resolve().parents[1] / ".env"

#: WHICH call sites in this run can actually reach a model. A SET, since 2026-09-03,
#: and the shape is the correction.
#:
#: A ROUTE IS NOT A CALL SITE, and conflating them put an untruth on the one screen
#: that must not carry one. `model_route` builds a client and this file announced
#: that files "may be sent to" three named models -- while `p8_run_call`,
#: `model_client`, `gate`, `prompt` and `call_dependencies` were `None` at every
#: injection point below, so nothing in `src/` could construct a model request at
#: all. A person who read that sentence and turned sending off was acting on a fear
#: the product had given them about something that could not happen; a person who
#: read it and left it on believed they had been told the truth about their files.
#:
#: A BOOLEAN WOULD NOW TELL THE SAME KIND OF UNTRUTH FROM THE OTHER SIDE. `A_fact`
#: is wired -- `_fact_call_authorities` builds the gate, the client, the ratified
#: prompt and the dependencies, and `model_facts.fact_call_stage` runs them as P6's
#: third producer. `C_placement` and `D_residual` are NOT: `placement_inputs` below
#: still passes `gate=None, model_client=None, prompt=None, call_dependencies=None`,
#: and `p8_run_call=None, p8_authorities=None` still go to P9. One flag that said
#: "wired" would have made the announcement claim a person's files may be sent for
#: checks and review sets, which is exactly as false as the sentence it replaced.
#: So the set is what is true, and `announce_cloud_posture` reads it per site.
#:
#: A SITE IS IN HERE ONLY WHEN A PROMPT IS RATIFIED FOR IT TOO. `run_call` refuses
#: without a `PromptDefinition` (`llm_harness/records.py:89`), so a route plus a key
#: plus a wired site still sends nothing until there is text to send -- which means
#: adding a member on the strength of the wiring alone would restore the same
#: untruth one step later. `A_fact` qualifies: `planning/82-FACT-PROMPT-DRAFT.md` §0
#: records the owner's ratification and `llm_harness.prompt_library` holds the
#: bytes. `tests/integration/test_cli_cloud_announcement.py` asserts this set
#: against the injections themselves, so it cannot drift from what is true.
WIRED_CALL_SITES: frozenset[str] = frozenset({A_FACT})

#: Whether ANY site can reach a model. Derived, never written: two spellings of one
#: fact is how the announcement got out of step with the code the first time.
MODEL_CALL_SITES_WIRED: bool = bool(WIRED_CALL_SITES)


#: THE FOUR SITES THAT RUN AND APPLY NOTHING. `104` §7 Phase 1 step 6: *"R-04 for
#: B, C, D, E in observe-only mode: inject the built authorities; record dossiers,
#: responses and verdicts; apply nothing until Phase 3 fixes R-15 and R-16."*
#:
#: SEPARATE FROM `WIRED_CALL_SITES` AND NOT AN EXTENSION OF IT, because the two
#: sets answer different questions and one set answering both is how the
#: announcement lied the first time. `WIRED_CALL_SITES` is "a person's files may be
#: SENT here", which is what the screen promises and what consent is about. This is
#: "the product asks and then throws the answer away". A member here sends nothing
#: over the internet and changes nothing about the plan, so folding it into the
#: other set would put four false sentences on the screen.
OBSERVE_CALL_SITES: frozenset[str] = frozenset(
    {B_GROUP, C_PLACEMENT, D_RESIDUAL, E_TEMPLATE})

#: The two sets are disjoint BY CONSTRUCTION and the assertion is here rather than
#: in a test, because a site in both would be a site that both applies its answer
#: and discards it, and there is no run that could be correct.
assert not (WIRED_CALL_SITES & OBSERVE_CALL_SITES)


#: WHICH DRAFT EACH OBSERVE SITE IS ASKED UNDER, `105` §9's winner per site. One
#: line each, and the id is the whole of what points at the text: `draft_bytes`
#: resolves it through the packet's manifest and verifies the bytes against the
#: digest recorded there, so re-pointing a site is an edit to this table and to
#: nothing else.
#:
#: B IS ON v3. `anchors-first-v3` is `105` §4.7's put-forward text (v1 with the
#: G13 bracket defect gone); it entered this branch's manifest with the prompts
#: merge, so `draft_bytes` can verify its bytes against a recorded digest. It is
#: unratified like the other three: `ratified` stays false and the site applies
#: nothing under it.
OBSERVE_TEMPLATE_ID: Mapping[str, str] = MappingProxyType({
    B_GROUP: "b_group.unratified.anchors-first-v3.2026-09-06",
    # `104` §18.13 (9 Sep 2026): eliminate-v2r -- v2 with the owner's tie sentence
    # (gap 7) and the set-aside sentence (gap 2), C's policy v2; ratified, cloud
    # open. `v3` stays reserved for 105 §14's amendments.
    C_PLACEMENT: "c_placement.unratified.eliminate-v2r.2026-09-09",
    D_RESIDUAL: "d_residual.unratified.ladder.2026-09-06",
    E_TEMPLATE: "e_template.unratified.what-a-person-opens-v2.2026-09-06",
})

assert set(OBSERVE_TEMPLATE_ID) == OBSERVE_CALL_SITES

#: `104` R-144: THE MANIFEST ROW SITE A RUNS UNDER, `(template_id, candidate)`.
#: Site A's text, schema, policy and glossary used to be loaded straight from the
#: library files, so a second version of A's text could not be run locally
#: without editing the ratified file. Now A resolves through a manifest row as the
#: observe sites do, and a v2 is a new row with its own id, `ratified_local`, and
#: this constant pointed at it.
#:
#: THE ID IS THE ONE THE RECORDS ALREADY CARRY. `prompt_fingerprint` hashes the
#: template id with the bytes, so a row that renamed the id for the same text
#: would change the fingerprint of every A_fact record written since 2026-09-04;
#: the library's own rule is that a row's status word is not its id
#: (`prompt_library.draft_status`). The row's `status` is what says the text is
#: ratified; its `candidate` tells it from the glossary arms sharing the id.
# `104` R-144: the ratified row is the deployment default; the v2 row
# (`a_fact.unratified.folder-levels-v2.2026-09-07`, `v2-code-subject`, `ratified_local`)
# is selected for a measurement run by pointing this pair at it in that run's checkout.
#: `104` §18.13 (9 Sep 2026): v3 -- the v2 text (R-144, the code-subject rules,
#: ratified for the cloud on 9 Sep) plus the owner's two sentences: the conflicts
#: flag explained (gap 1) and an unseen value may be proposed (gap 3), with A's
#: policy v2. The scoreboard scripts that patched this constant to v2 in a
#: worktree are superseded by the row itself.
A_FACT_ROW: tuple[str, str] = (
    "a_fact.unratified.folder-levels-v3.2026-09-09", "v3-conflicts-open-values")


#: `104` §17.1's THIRD WALL: THE MANIFEST ROW SITE G RUNS UNDER, `(template_id,
#: candidate)`, on `A_FACT_ROW`'s own pattern and for the same reason -- the row is
#: what points at bytes, and the digests in the packet are what verify them.
#:
#: THE PAIR IS THE BAKEOFF'S ANSWER AND NOT A PREFERENCE. `103` §28.1 is the
#: protocol and the two authored candidates were `situation.unratified.shortlist.
#: 2026-09-06` and `situation.unratified.safety-first.2026-09-06`. The measurement
#: is recorded in the commit that set this line; re-pointing the site is an edit
#: here and to nothing else.
#:
#: MEASURED 9 Sep 2026 (`tools/promptbench/out/g-bakeoff-1`, 14 synthetic cases,
#: local qwen3:8b): the two candidates answered EVERY case identically -- 4 of 4
#: should-abstain cases abstained, 4 of 10 should-answer cases right, 1 wrong (a
#: journal abstract about a disease called a medical record: the over-protective
#: direction), 5 unnecessary abstentions. Safety-first is the one named because its
#: median call was faster (56 s against 61 s) and because it asks the four protected
#: kinds before it reads the shortlist, which is the order the owner's ruling puts
#: them in. The tie is the record, not a preference.
#:
#: **`ratified_local` AND NOT `ratified`.** `104` §17.1: "Nothing leaves the device
#: under this ruling." The word is the row's, in the manifest, and it is the one
#: `prompt_library` invented for exactly this: the site ACTS on the answer and the
#: cloud stays shut. The population this site exists for is the unclassified files,
#: and `privacy.denial.unclassified_denies` refuses every cloud release of one
#: unconditionally -- so a `ratified` here would name a permission no file at this
#: site could use.
#: `104` §18.7 S2 and §18.11 (9 Sep 2026): the v2 row, ratified by the owner for
#: local use, asks the same question plus one -- which of `105` §13.3's ten
#: restricted kinds the file is, in `restricted_kind` -- so that the local model
#: is the kind recogniser `privacy_class` has been waiting for.
#: v3 (`104` §18.13, gap 8): the v2 text and schema with site G's OWN shaping
#: policy, so the model-visible description of the call is true of the call.
SITUATION_ROW: tuple[str, str] = (
    "situation.unratified.safety-first-v3.2026-09-09", "situation-safety-first-v3")


#: WHAT EACH STATUS WORD BUYS, and the two questions it answers are not one
#: question. `prompt_library` holds the vocabulary and judges nothing with it; the
#: meaning of a word is a policy and policies are the composition root's.
#:
#: **APPLY** is "the site acts on this answer instead of recording it and moving
#: on" -- `PromptDefinition.ratified`, which every applier reads off the object.
#: **CROSS** is "these bytes may leave the device" -- the `104` §13 count.
#:
#: `ratified_local` is in the first and not the second, and that gap is the whole
#: point of the word: `104` §15.1 ratifies C's `eliminate-v2` FOR THE LOCAL MODEL
#: and leaves the cloud to R-82, because a local run sends nothing anywhere and
#: showing a person's folder labels to a provider is a different consent. A single
#: word would have made the owner grant both to get either.
STATUS_APPLIES: frozenset[str] = frozenset({RATIFIED_LOCAL, RATIFIED})
STATUS_MAY_CROSS_THE_INTERNET: frozenset[str] = frozenset({RATIFIED})

#: Both are read against the library's closed vocabulary HERE, at import, because
#: a typo in either would be a set that silently never matches -- an approval that
#: never takes effect, or a gate that never opens -- and a run would look normal
#: the whole way through. Crossing implies applying: text nobody will act on has
#: no business on the internet either.
assert STATUS_APPLIES <= DRAFT_STATUS_WORDS
assert STATUS_MAY_CROSS_THE_INTERNET < STATUS_APPLIES


#: WHAT A REJECTED B PROPOSAL IS CALLED, spelled once. `proposal_class` is not a
#: harness vocabulary: `eligibility.py:51` matches it EXACTLY against
#: `learning_records.proposal_class`, so it is an identity the composition root
#: names and must keep stable -- a rename stops every past rejection suppressing
#: what it was recorded to suppress. `model_facts` spells its own
#: `fact.llm_extraction`, and this follows that shape: the subject kind, then what
#: the model was asked to do.
GROUP_PROPOSAL_CLASS: str = "group.llm_coherence"

#: And site E's, on the same terms and for the same reason. The subject kind is a
#: template, and what the model was asked to do is design one.
TEMPLATE_PROPOSAL_CLASS: str = "template.llm_design"


def observe_allowed_vocabulary(call_site: str) -> tuple[str, ...]:
    """The closed set the answer must come from, READ OUT OF THE SCHEMA.

    **The B schema defines no closed set for the category, and that is deliberate
    rather than missing.** `$defs.payload.properties.category` is
    `{"type": "string", "minLength": 1}` -- free text -- which is `104` §13.7
    already honoured in the text the model is shown: *"Model names, user
    confirms... A value the library has not seen is proposed once; the user
    confirms or renames it."* A closed category list here would reverse that
    ruling in code while the prompt beside it said otherwise.

    What the payload DOES close is `basis`, and that is the group's judgement
    rather than one member's: direct anchor, context supported, or generic
    similarity. `allowed_vocabulary` reaches the dossier the model is shown
    (`harness.py:303`), so it is that set.

    READ FROM THE SCHEMA AND NOT SPELLED HERE. The model is shown one list and
    validated against another the moment those are two literals, and this is the
    file that would hold the second one.
    """
    _template, response_schema, _policy = draft_bytes(
        OBSERVE_TEMPLATE_ID[call_site])
    schema = json.loads(response_schema)
    payload = schema.get("$defs", {}).get("payload", {})
    basis = payload.get("properties", {}).get("basis", {}).get("enum")
    if not basis:
        raise ValueError(
            f"the response schema for {call_site!r} closes no `basis` set, so "
            f"there is no vocabulary to show the model. `84` §1: absent means "
            f"refuse. A caller that invented one would show the model options "
            f"its own instructions do not list.")
    return tuple(basis)


def _no_group_contradiction(*_args: object, **_kwargs: object) -> bool:
    """B's `contradicts`. There is no per-field fact at a group site to contradict.

    Named and spelled once rather than passed as a lambda, so the reason survives
    where the value is read: this is not "no check", it is the check answered.
    """
    return False


def _no_placement_contradiction(*_args: object, **_kwargs: object) -> bool:
    """C's and D's `contradicts`, for the reason B's docstring already gives.

    **Found by giving the placement sites a budget of their own.** C and D took
    `fact_authorities.contradicts` -- `contradicts_stronger`, which indexes its
    argument as a P6 fact row -- so the first real C call handed it a `Dossier`
    and raised `TypeError: 'Dossier' object is not subscriptable` inside
    `validation._validate_claim`. B's own comment records that exact failure and
    that exact shape, "injecting one site's authority at another"; C had it too,
    and nothing had reached it because C never won a slot from the budget site A
    was emptying. The two defects were hiding each other.

    The check is ANSWERED and not skipped: a placement answer names a destination
    node and a residual answer names one of §7.7's actions, neither of which is a
    value at a P6 field, so there is no stronger fact for one to contradict. The
    truthful answer is the same `False` B gives one site over.
    """
    return False


def placeable_file_count(conn: sqlite3.Connection, scan_run_id: str) -> int:
    """How many files this run may PLACE, which is not how many site A asks about.

    `104` R-139. `observe_scan_budget` copied `corpus_file_count` from the fact
    pass's budget, and that number is `len(roster)` at the fact pass -- the files A
    still had to ask. On the seeded C-live run r6 that was a handful, so
    `allowed_calls` floored the observe purse to its minimum of ONE: the ledgers
    read `calls_reserved=7` for the fact scan and `calls_reserved=1` for
    `<scan>:observe`, with ten reservations released, and site C recorded 52
    `BUDGET_EXHAUSTED` abstentions in one second.

    Site A's purse sized by A's roster is right -- a fact call is about a file A
    asks about. The placement sites ask about the whole corpus, including every
    file whose facts were already settled and every file A was seeded past, so
    their purse is sized by the scan's own roster and never by A's.
    """
    return len(corpus_roster(conn, scan_run_id))


def observe_scan_budget(fact_budget: ScanBudget, *,
                        corpus_file_count: int) -> ScanBudget:
    """The ledger the observe and placement sites spend from, which is not A's.

    Built from the fact pass's budget rather than beside it, because two of the
    three inputs are facts about the RUN and not about the site: which scan this
    is, and how many files it holds. What changes is the purse -- its own
    `scan_id`, its own rate, floor and ceiling -- so a fact question can no longer
    spend a slot a placement question needed.

    **The defect this ends, measured.** Site A asks one call per FILE, so a corpus
    where every file has an open question spends every slot the run has. On the
    six-file corpus of `tests/integration/test_local_model_fact_pass.py` that is
    five fact calls, after which site B is refused before a call and site C
    records `BUDGET_EXHAUSTED`; on the owner's 199 files it is every run. The
    sites that decide WHERE a file goes were being starved by the site that
    decides WHAT it is, and nothing in the run said so: a starved site looks
    exactly like a site nobody wired (`104` R-04).

    **The other authorities are still A's and are still taken, not rebuilt.** The
    gate, the costs, the policy version and the wire handle key are facts about
    this deployment and this run; a second gate would be a second answer to "what
    may leave this device". The budget is the one that was never a fact about the
    run, and it is the only one this function replaces.

    Not cached and not memoised: a `ScanBudget` is a value, the ledger lives in
    the database under its `scan_id`, and two calls with one fact budget produce
    two equal values that reserve from one row.
    """
    return ScanBudget(
        scan_id=fact_budget.scan_id + OBSERVE_BUDGET_SUFFIX,
        corpus_file_count=corpus_file_count,
        max_calls_per_1000_files=OBSERVE_CALLS_PER_1000_FILES,
        max_estimated_cost=OBSERVE_CALLS_PER_SCAN_CEILING,
        min_calls_per_scan=OBSERVE_MIN_CALLS_PER_SCAN)


def situation_scan_budget(fact_budget: ScanBudget, *,
                          corpus_file_count: int) -> ScanBudget:
    """`104` §17.1's site G, spending from a THIRD ledger. Same rate, own purse.

    `observe_scan_budget`'s whole argument, applied one site along and measured the
    same way. Site G asks one call per file the rules could not settle and it runs
    BEFORE the fact pass, so pointing it at the observe purse reproduced exactly the
    defect R-131 ended: on the six-file corpus of
    `tests/integration/test_local_model_fact_pass.py` it emptied the observe ledger
    and site C recorded `BUDGET_EXHAUSTED` for five tests that had been green, with
    nothing in the run saying so.

    **The rate, the floor and the ceiling are the observe ones and are not new
    numbers.** "How many model calls may one scan make about one corpus" is a
    deployment answer and this deployment has given it once; a fourth set of
    constants here would be a second answer to a question nobody asked again. What
    is site G's own is the `scan_id`, which is what makes it a separate ledger --
    and a separate ledger is the entire fix.
    """
    return ScanBudget(
        scan_id=fact_budget.scan_id + SITUATION_BUDGET_SUFFIX,
        corpus_file_count=corpus_file_count,
        max_calls_per_1000_files=OBSERVE_CALLS_PER_1000_FILES,
        max_estimated_cost=OBSERVE_CALLS_PER_SCAN_CEILING,
        min_calls_per_scan=OBSERVE_MIN_CALLS_PER_SCAN)


def observe_group_authorities(fact_authorities, *, routing: TierRouting,
                              situation: str, placeable_file_count: int):
    """Site B, wired to run and to change nothing. `(p8_run_call, authorities)`.

    **Everything shared with site A is TAKEN from A's authorities rather than
    rebuilt.** The gate, the budget, the costs, the policy version and the wire
    handle key are facts about this deployment and this run, not about which site
    is asking; a second `Gate` built beside the first would be a second answer to
    "what may leave this device" and the two would drift on the next ruling. What
    differs is the client, the prompt, and the five learning fields below.

    **THE DESTINATION MUST SERVE EVERY MEMBER (`104` §17.13 ruling 3), and B is
    the site where "the members" is not one file.** A group call carries readings
    from every file in the group, so the rule is cloud only if every member is
    cloud-permitted, else local. `site_destination` carries how this deployment
    satisfies that -- B's text is unratified, so its only destination is the model
    on this machine and every member may use it -- and why the per-file gate is not
    folded over the corpus here: it would refuse the whole call for one protected
    file anywhere in it, and buy nothing, because that file's readings are already
    refused one by one at the door.

    `(None, None)` when there is no routing, or when B's tier resolves to no
    destination its own text permits. That second case is not an error: a
    deployment with a cloud key and no local model is correctly configured and
    simply does not run the observe sites, because their text is unratified.
    `require_observe_locality` is the backstop for anyone who builds these another
    way.

    **ONE PURSE, unchanged.** `observe_scan_budget` is site B's own `ScanBudget`
    and the destination does not divide it: a group is one call and spends one
    reservation whichever model answers it.
    """
    if routing is None:
        return None, None
    chosen = site_destination(routing, B_GROUP)
    if chosen is None:
        return None, None
    client, group_target = chosen
    require_observe_locality(B_GROUP, group_target.locality)
    #: The half that is the same for every group in the run. The two that are not
    #: -- which group, and on what basis -- are set per call below, because
    #: `ModelCallAuthorities` is built once and `group_subject` runs per subject.
    shared = CallDependencies(
        proposal_class=GROUP_PROPOSAL_CLASS,
        # §8.7's SCOPE VOCABULARY, and it is closed: file, group, node, template,
        # domain, corpus. The convention `model_facts` sets is that the scope names
        # the KIND of subject and `learning_subject_id` is that subject's id --
        # `"file"` beside `request.file_id`. A group verdict is about a group, so
        # the pair is `"group"` beside the group id, which is also what keeps a
        # rejection of one group from suppressing another.
        learning_scope=GROUP,
        # Both replaced per call, from the request. Present here because
        # `run_call` reads the whole set before the first call and a `None` in
        # either would refuse every one of them.
        basis_key=GROUP,
        learning_subject_id=GROUP,
        evidence_resolver=fact_authorities.evidence_resolver,
        # B has no bundle of its own: `SiteDependencies` names fact, placement,
        # residual and template, and `validate_group_response` takes none of them.
        # Four `None`s is the truthful answer and not an omission.
        site_dependencies=SiteDependencies(
            fact=None, placement=None, residual=None, template=None),
        # NOT A's `contradicts_stronger`, and the difference is the site rather
        # than a preference. That function answers "does this proposed FIELD VALUE
        # contradict a stronger fact already on the file", reads `field_key` and
        # `canonical_value` off a row, and B hands its validator a dossier and a
        # group. There is no per-field fact at the group site for a coherence
        # answer to contradict, so the truthful answer is always no --
        # `tools/promptbench/judge.py` reaches the same conclusion and spells it
        # `_never_contradicts`. A callable is required, and passing A's raised
        # `TypeError: 'Dossier' object is not subscriptable` on the first real B
        # call, which is the shape of injecting one site's authority at another.
        contradicts=_no_group_contradiction,
        # One rung, for `model_facts`' reason: the dossier is built at the cap
        # already and there is no smaller shape of it to fall back to.
        unreduced_fits=True, summarized_fits=False, anchors_fit=False,
        split_shard_fits=(), split_shards=(),
        # NOT SITE A's, since `104` R-131's merge. `observe_scan_budget`
        # carries why: one call per file spends every slot before an
        # observe question is put, so this site drew from a purse the fact
        # pass had already emptied.
        scan_budget=observe_scan_budget(
            fact_authorities.scan_budget,
            corpus_file_count=placeable_file_count),
        estimated_cost=fact_authorities.estimated_cost,
        actual_cost=fact_authorities.actual_cost,
        allowed_vocabulary=observe_allowed_vocabulary(B_GROUP),
        # B judges an existing group's coherence. It proposes no field and builds
        # no level, so the truthful list is empty rather than `None`.
        folder_levels=(),
        policy_version=fact_authorities.policy_version,
        wire_handle_key=fact_authorities.wire_handle_key)

    return partial(
        # `104` R-71. THE SINK IS BOUND HERE AND NOT PASSED THROUGH P9. A's
        # authorities already hold the mailbox `run` built beside the transport that
        # fills it, and it is taken from A for the same reason the gate and the
        # budget are: it is a fact about this deployment and this run, not about
        # which site is asking. Bound rather than added to the bundle because
        # `ModelCallAuthorities` is exactly `run_call`'s keywords as P9 forwards
        # them, and a seventh field P9 cannot construct would be the required-slot-
        # nothing-fills defect `104` R-09 removed. `NOT_P9_AUTHORITIES` stays the
        # name of the one keyword P9 does not carry, and it stays true.
        observed_run_call,
        usage_recorder=fact_authorities.usage_recorder,
    ), ModelCallAuthorities(
        gate=fact_authorities.gate,
        model_client=client,
        prompt=prompt_for(B_GROUP),
        validation_dependencies=shared,
        observed_at=fact_authorities.observed_at,
        # The SAME target the client is pointed at, read off the client rather than
        # than built beside it.
        model_target=client.model_target)


def observe_template_call(conn: sqlite3.Connection, fact_authorities, *,
                          placeable_file_count: int,
                          routing: TierRouting, catalogue):
    """Site E, wired to run and to change nothing. Packet G12's missing caller.

    `None` on the same three terms site B's builder uses: no routing, or E's tier
    does not resolve to a model on this device. A deployment with a cloud key and
    no local model is correctly configured and simply does not run the observe
    sites, because their text is unratified and `observe_locality_permits` is what
    keeps that from being a promise nobody enforces.

    **Everything shared with site A is TAKEN from A's authorities**, for the reason
    `observe_group_authorities` gives at length: the gate, the budget, the costs,
    the policy version, the handle key and `104` R-14's mailbox are facts about
    this deployment and this run, not about which site is asking. A second `Gate`
    beside the first would be a second answer to "what may leave this device".

    **The answer is wrapped whatever `prompt.ratified` says, and site E is the one
    site where that is not a lever waiting to be moved.** B, C and D withhold while
    their text is a draft and begin applying the day the owner ratifies it. `00`:97
    ends with "valid shape is not activation -- the person reviews, edits and
    accepts or discards", and that canvas is Release 2 (`104` §13.3). So the
    condition here is not the ratification; there is no condition.
    """
    if routing is None:
        return None
    # THE DESTINATION MUST SERVE EVERY MEMBER, as at site B and for the reason
    # `site_destination` carries: a template call is built from a group's anchors,
    # so one client serves every group this pass will be handed and it may only be
    # one every member may use. E's text is unratified, so that is this machine.
    chosen = site_destination(routing, E_TEMPLATE)
    if chosen is None:
        return None
    client, template_target = chosen
    require_observe_locality(E_TEMPLATE, template_target.locality)
    prompt = prompt_for(E_TEMPLATE)

    def ask(groups, plan_version: str) -> None:
        for group in groups:
            request = template_request_for(
                conn, group=group, plan_version=plan_version,
                model_target=client.model_target, prompt=prompt,
                max_dossier_tokens=GROUPING_LIMITS.max_dossier_tokens)
            if request is None:
                # A group whose anchors cite nothing P7 may release has nothing to
                # design a template FROM, and `00`:97 forbids inventing one. Not
                # asked rather than asked emptily.
                continue
            run_call(
                conn, request, gate=fact_authorities.gate, model_client=client,
                prompt=prompt,
                validation_dependencies=dataclasses.replace(
                    _template_dependencies(
                        fact_authorities, catalogue, group,
                        placeable_file_count=placeable_file_count),
                    basis_key=group.group_id,
                    learning_subject_id=group.group_id),
                observed_at=fact_authorities.observed_at,
                usage_recorder=fact_authorities.usage_recorder)

    return ask


def _template_dependencies(fact_authorities, catalogue, group, *,
                           placeable_file_count: int) -> CallDependencies:
    """One site-E call's `CallDependencies`. P10's two authorities, and A's rest.

    `allowed_vocabulary` is `allowed_vocabulary_for`, which is P10's own closure
    over ONE schema's allowed fields and is deliberately not extendable -- it
    reaches the dossier as the set a proposed dimension name is classified
    against, and a name outside it is a template-local label rather than a
    rejection (Contract W2). The schema is the group's own `group_category`; a
    group with none gets the empty closure, which is the honest answer and still
    produces a reviewable design.
    """
    return CallDependencies(
        proposal_class=TEMPLATE_PROPOSAL_CLASS,
        learning_scope=TEMPLATE_SCOPE,
        basis_key=TEMPLATE_SCOPE,
        learning_subject_id=TEMPLATE_SCOPE,
        evidence_resolver=fact_authorities.evidence_resolver,
        site_dependencies=SiteDependencies(
            fact=None, placement=None, residual=None,
            template=template_dependencies(catalogue)),
        # A template proposal names no per-file field value, so there is no
        # stronger fact for one to contradict. Site B's answer, at a site whose
        # subject is a group for the same reason.
        contradicts=_no_group_contradiction,
        unreduced_fits=True, summarized_fits=False, anchors_fit=False,
        split_shard_fits=(), split_shards=(),
        # NOT SITE A's, since `104` R-131's merge. `observe_scan_budget`
        # carries why: one call per file spends every slot before an
        # observe question is put, so this site drew from a purse the fact
        # pass had already emptied.
        scan_budget=observe_scan_budget(
            fact_authorities.scan_budget,
            corpus_file_count=placeable_file_count),
        estimated_cost=fact_authorities.estimated_cost,
        actual_cost=fact_authorities.actual_cost,
        allowed_vocabulary=allowed_vocabulary_for(
            catalogue, uses_schema=group.domain or ""),
        # E DESIGNS the levels rather than filling them, so the situation's own
        # folder levels are not what it is shown. Empty is the truthful list.
        folder_levels=(),
        policy_version=fact_authorities.policy_version,
        wire_handle_key=fact_authorities.wire_handle_key)


def observed_run_call(conn, request, *, gate, model_client, prompt,
                      validation_dependencies, observed_at,
                      usage_recorder=None):
    """`run_call`, with the per-group half of the learning key filled in, and
    with B's answer withheld while B's text is a draft.

    `group_subject` runs per subject and `ModelCallAuthorities` is built once, so
    the two fields that identify WHICH proposal a past rejection would suppress
    cannot be set at composition. They are set here, from the request the pipeline
    just built, which is the same thing `_judge_with_model` does for C and D and
    for the same reason.

    `basis_key` IS THE SUBJECT ADDRESS AND NOT THE GROUP'S `proposed_basis`, which
    is what it should become. The basis is on the DOSSIER and `p8_run_call` is
    handed only the request, so it is not reachable from here. Inert while B
    applies nothing -- `assess_call` uses the pair to find a user's past REJECT,
    and an observe run writes none -- and it must be the basis before B applies
    anything.

    **`ObservedOnly` IS NOW CONDITIONAL, AND THAT IS THE FIX.** It wrapped
    unconditionally and never read `prompt.ratified`, so B's answer was withheld by
    the SHAPE of this function while every other site read the field:
    `_observed_only` at C and D, `PipelineInputs.model_decides` at P11. The day the
    owner ratifies `anchors-first-v3`, A, C and D would begin applying and B would
    go on discarding, with nothing in the product saying why.

    A MODULE-LEVEL FUNCTION and no longer a closure, because the prompt arrives as
    an argument -- `grouping.pipeline` passes `p8_authorities.prompt` through -- so
    closing over one was a second copy of a value already in the signature, and one
    a test could not reach.

    **`usage_recorder` ARRIVES HERE AND NOT IN THE BUNDLE, which is `104` R-71's
    whole shape.** A B response had no `llm_call_usage` row while A's rows matched
    A's responses one for one, because P9 forwards `ModelCallAuthorities` under
    `run_call`'s own keywords and that bundle deliberately carries no sink
    (`NOT_P9_AUTHORITIES`). Putting one on the bundle would put a required slot on
    P9 that P9 cannot fill -- the mailbox is built beside the transport by the
    composition root, and `src/grouping/` may not import either -- which is the
    defect `104` R-09 took OFF `GroupingKnowledge`.

    So the sink is bound HERE, where both sides are known, and `observe_group_
    authorities` binds it before P9 ever sees the callable. P9's forwarding is
    unchanged, `NOT_P9_AUTHORITIES` still names the one keyword the bundle does not
    carry, and B's call reads the same one-slot mailbox A's does: one transport,
    one reading per call, taken by whoever made it.

    Defaulted for `run_call`'s own reason -- a deployment that records no usage is a
    real deployment, and the local transport's own `Usage` has no cache count to
    give.
    """
    subject = getattr(request, "subject_ref", "") or ""
    deps = dataclasses.replace(
        validation_dependencies,
        basis_key=subject or validation_dependencies.basis_key,
        learning_subject_id=(subject.partition(":")[2]
                             or validation_dependencies.learning_subject_id))
    result = run_call(
        conn, request, gate=gate, model_client=model_client, prompt=prompt,
        validation_dependencies=deps, observed_at=observed_at,
        usage_recorder=usage_recorder)
    if not getattr(prompt, "ratified", False):
        return ObservedOnly(result)
    answer = group_answer_of(conn, result)
    if answer is None:
        # RECORD AND APPLY NOTHING, which is the safe direction and not a
        # fallback. A verdict whose response this root cannot read is a verdict
        # whose per-member decisions, label and category are unknown, and applying
        # it would put back exactly the blanket memberships `104` R-16 names.
        return ObservedOnly(result)
    return Answered(result=result, answer=answer)


def group_answer_of(conn: sqlite3.Connection, result: object):
    """The model's §4.5 four answers for one B call, read back at the boundary.

    **This is the composition root's job and nobody else's.** `P8Verdict` names a
    `claim_ref` and carries no payload, so the model's own answers "can only be read
    by whoever knows the response shape -- which is whoever supplied the prompt"
    (`model_placement`, for `chosen_node_of` at site C). `src/grouping/` may not
    import `llm_harness.records` at all, so P9 could not read one if it wanted to.

    **Read here rather than later**, and `last_response_bytes` says why: this runs
    the statement after `run_call` returned, so the row it reads is the row that
    call wrote.

    `None` whenever there is nothing to apply -- not a verdict, no response on
    disk, unparseable bytes, a claim that is not the one the verdict judged -- and
    the caller turns every one of those into "recorded, applied to nothing".

    The two vocabularies are translated HERE, from the response schema's words to
    P9's, for the reason `MemberDecision` gives: a table in P9 would be a second
    copy of a contract the prompt owns.
    """
    if not isinstance(result, P8Verdict):
        return None
    raw = last_response_bytes(conn, result.dossier_id)
    if raw is None:
        return None
    try:
        claims = json.loads(raw).get("claims")
    except (json.JSONDecodeError, AttributeError):
        return None
    if not isinstance(claims, list) or not claims:
        return None
    claim = claims[0]
    if not isinstance(claim, dict):
        return None
    payload = claim.get("payload")
    if not isinstance(payload, dict):
        return None
    members = []
    for entry in payload.get("members") or ():
        if not isinstance(entry, dict):
            continue
        decision = GROUP_MEMBER_DECISION.get(entry.get("decision"))
        if decision is None or not entry.get("file_id"):
            continue
        members.append(MemberDecision(
            file_id=str(entry["file_id"]), decision=decision,
            why=str(entry.get("why") or "")))
    citations = tuple(
        str(item.get("evidence_ref")) for item in (claim.get("citations") or ())
        if isinstance(item, dict) and item.get("evidence_ref"))
    coherent = GROUP_COHERENCE.get(payload.get("coherent"))
    label = payload.get("label")
    category = payload.get("category")
    return ModelAnswer(
        coherent=coherent,
        category=str(category) if isinstance(category, str) else None,
        label=str(label) if isinstance(label, str) else None,
        members=tuple(members), citations=citations)


#: The B response schema's words for a member, and P9's. The left column is
#: `$defs.payload.properties.members.items.properties.decision.enum` and the right
#: is `grouping.vocabulary.MEMBERSHIP_DECISIONS`. Spelled at the composition root
#: because that is where both contracts are known: P9 does not read a response and
#: the schema does not know P9's words.
GROUP_MEMBER_DECISION: Mapping[str, str] = MappingProxyType({
    "include": INCLUDED,
    "exclude": EXCLUDED,
    "uncertain": UNCERTAIN,
})

#: The same translation for §4.5's first task. `insufficient` is `abstained` and
#: not `not-coherent`: the model saying it could not tell is a different answer
#: from the model saying these files are not one group, and `COHERENCE_VERDICTS`
#: keeps them apart.
GROUP_COHERENCE: Mapping[str, str] = MappingProxyType({
    "yes": COHERENT,
    "no": NOT_COHERENT,
    "insufficient": ABSTAINED,
})


class PlacementAnswerUnreadable(RuntimeError):
    """A C or D verdict this root cannot read the model's own answer behind.

    UNREACHABLE UNLESS THE ROW `run_call` WROTE IS GONE. A verdict P8 accepted was
    produced by parsing the response and validating the payload, so the
    destination is a non-empty string that was in the shortlist and the action is
    one of §7.7's eight; the bytes are on disk because `issue` recorded them before
    the validator ran. What is left is a contract failure -- no response for the
    dossier, bytes that no longer parse, no claim carrying the verdict's own
    `claim_ref` -- and it is raised rather than turned into an abstention for the
    reason `place_file` already raises three lines below `chosen_node_of`: naming
    one of §6.10's closed abstention reasons would record a conclusion nothing
    reached, and placing on a guess would file a file the model never chose.
    """


def _validated_payload(conn: sqlite3.Connection, verdict) -> dict | None:
    """The payload of the CLAIM THIS VERDICT JUDGED, or `None`.

    **The composition root's job and nobody else's**, for the reason
    `group_answer_of` gives at site B and `model_placement` gives for
    `chosen_node_of`: `P8Verdict` names a `claim_ref` and carries no payload, so
    the model's own answer "can only be read by whoever knows the response shape --
    which is whoever supplied the prompt". `src/placement/` never sees a response
    body and P8 hands back a judgement rather than an answer.

    **Read at the call boundary**, which is what makes `last_response_bytes` exact
    here: `place_file` consults `chosen_node_of` with no other call in between, and
    `_review_set_with_model` consults `residual_action_of` the same way, so the
    most recent response for that dossier is the one the call just wrote.

    **Matched on `claim_ref`, never taken by position.** C's schema allows exactly
    one claim today, but the verdict says WHICH claim it judged, and a reader that
    took the first would read a different claim's destination the day a schema
    allows two. The effective ref is `validation._validate_claim`'s own rule: the
    claim's own `claim_ref` when it has one, `claim-<index>` otherwise.
    """
    raw = last_response_bytes(conn, verdict.dossier_id)
    if raw is None:
        return None
    try:
        claims = json.loads(raw).get("claims")
    # `ValueError` covers `JSONDecodeError` and the `UnicodeDecodeError` bytes that
    # are not UTF-8 raise; `AttributeError` is a body that parsed to something with
    # no `get`. Every one of them is "this root cannot read the answer", and the
    # caller turns that into a refusal rather than a placement.
    except (ValueError, TypeError, AttributeError):
        return None
    if not isinstance(claims, list):
        return None
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            continue
        ref = (str(claim["claim_ref"]) if claim.get("claim_ref")
               else f"claim-{index}")
        if ref != verdict.claim_ref:
            continue
        payload = claim.get("payload")
        return payload if isinstance(payload, dict) else None
    return None


def _chosen_node_of(conn: sqlite3.Connection):
    """Site C's real resolver: the node id the VALIDATED verdict names.

    **It re-validates nothing, and that restraint is the whole of it.** P8's Site C
    checks have all run by the time a verdict exists: `_placement_site` refuses a
    destination outside `allowed_vocabulary` as `INVENTED_NODE` -- and
    `allowed_vocabulary` is the ranked shortlist P11 showed the model -- refuses
    one the frozen tree does not hold as `NODE_NOT_IN_FROZEN_TREE`, and applies the
    two-condition reason codes above both. A second opinion here would be a rule
    with no way to be reconciled with the first, which is `p8_seam`'s own position,
    and `place_file` re-checks the resolved node against `legal_node_ids` anyway
    before it writes. So this reads the accepted payload and hands back what it
    says.

    **Reached only when the verdict PLACED.** `place_file` transcribes first and
    takes the abstention path for every outcome that is not `place`, so an
    abstaining, weak or rejected answer never arrives here -- including the
    abstention `_observed_only` writes over an unratified site's verdict, which is
    why the raising stub is still what the composition root injects while C's text
    is a draft.
    """
    def resolve(verdict) -> str:
        payload = _validated_payload(conn, verdict)
        destination = payload.get("destination") if payload else None
        if not isinstance(destination, str) or not destination:
            raise PlacementAnswerUnreadable(
                f"the accepted Site C verdict {verdict.verdict_id!r} names claim "
                f"{verdict.claim_ref!r} of dossier {verdict.dossier_id!r}, and "
                f"this deployment cannot read a destination out of the response "
                f"P8 validated to reach it. P11 places nothing on a guess.")
        return destination
    return resolve


def _residual_action_of(conn: sqlite3.Connection):
    """Site D's real resolver: §7.7's action and its target, as the verdict names.

    The same restraint as `_chosen_node_of`, for the same reason. P8 has already
    checked the action against `RESIDUAL_ACTIONS`, checked a target-bearing
    action's target against the approved residual set and the frozen tree, and
    rewritten `mark_review_later` and `abstain` into its own outcomes. The
    `disposition` it hands back is deliberately coarser than the eight --
    `residual_destination` covers both the destination choice and the broad parent,
    `return_to_placement` covers both returns -- so which of the eight was chosen
    can only be read from the response, and `_residual_action_and_target` refuses
    an action outside `ACTION_OUTCOME` on the way out.

    `target` is passed through as the response carries it: a node id for the two
    choices, a group or packet id for the two returns, one of `MARKED_STATES` for
    the mark, and `None` for the three that name nothing. `outcome_for_action` owns
    which of those each action may have, and refuses the rest.
    """
    def resolve(verdict) -> tuple[str, object]:
        payload = _validated_payload(conn, verdict)
        action = payload.get("action") if payload else None
        if not isinstance(action, str) or not action:
            raise PlacementAnswerUnreadable(
                f"the Site D verdict {verdict.verdict_id!r} names claim "
                f"{verdict.claim_ref!r} of dossier {verdict.dossier_id!r}, and "
                f"this deployment cannot read an action out of the response P8 "
                f"validated to reach it. §7.7 has eight actions and none of them "
                f"is a guess.")
        return action, payload.get("target")
    return resolve


class ObservedSiteMustNotApply(RuntimeError):
    """An observe-only site reached the code that would act on its answer."""


def _must_not_apply(call_site: str):
    """`chosen_node_of` and `residual_action_of` for a site that applies nothing.

    **STILL THE INJECTION WHILE THE SITE'S TEXT IS A DRAFT, and no longer the only
    one.** `_chosen_node_of` and `_residual_action_of` above are the real
    resolvers, and `observe_placement_injections` picks between them and this one
    off the site's OWN prompt: a ratified C gets the real reader, an unratified C
    gets this. That is the same field `_observed_only`, `PipelineInputs.
    model_decides` and `observed_run_call` read, so one site can be turned on
    without the other three, and none of them is turned on by a rename.

    `model_path_available()` reads all eight injections as a set, so these must be
    present for C and D to run at all. Under an unratified prompt they must also
    never be REACHED: the observe lever in `_judge_with_model` rewrites the verdict
    to an abstention, and both callers take their existing abstention path without
    consulting a resolver.

    So they raise. A resolver that returned a plausible node under text nobody
    approved would place a file on an answer to a question the product has not
    agreed to ask, and it would do it silently. This fails loudly instead, which is
    what an unreachable branch owes the next person to make it reachable.
    """
    def resolve(_verdict: object):
        raise ObservedSiteMustNotApply(
            f"{call_site} is observe-only and something asked it to apply an "
            f"answer. `104` §7 Phase 1 step 6 records the verdict and applies "
            f"nothing while the site's text is a draft, and the abstention that "
            f"keeps this unreachable is in `_judge_with_model`. Ratify the text "
            f"and the composition root injects the real resolver instead.")
    return resolve


def observe_placement_injections(conn: sqlite3.Connection, fact_authorities, *,
                                 placeable_file_count: int,
                                 routing: TierRouting, plan_version: str,
                                 operation_mode: str = OPERATION_MODE) -> dict:
    """Sites C and D, wired to run and to change nothing. Eight of the nine.

    `sensitivity_policy` is NOT here: R-55 supplies it at `placement_inputs`
    already, and P8's two sensitivity checks refuse with it whether or not a model
    is configured. Overwriting it from here would take a refusal away.

    `{}` when there is no routing or when C's tier is not on this device, which
    leaves every field as `placement_inputs` had it and the model path off.

    **THE RESOLVERS ARE PICKED PER SITE, OFF THAT SITE'S OWN PROMPT.** A ratified
    site gets the real reader -- `_chosen_node_of` for C, `_residual_action_of` for
    D -- and an unratified one gets `_must_not_apply`, which raises. Two prompts
    are read and two decisions are made, because C and D are ratified separately
    and a shared answer would turn one site on with the other; the field is the
    prompt's own `ratified`, exactly as `_observed_only` reads it, so the loader
    turns a site on and no line of this function changes.
    """
    if routing is None:
        return {}
    # `104` §17.13 ruling 3: C's destination is PER FILE, so what is asked here is
    # only whether the site has any destination at all. `target_for` drops the
    # cloud candidate for a site whose text may not cross the internet -- C's word
    # is `ratified_local` -- so on a two-target deployment every file C is asked
    # about goes to the model on this machine, and the site keeps running where
    # reading `locality_for` would have handed it a cloud client and turned it off.
    placement_route = target_for(conn, routing, C_PLACEMENT,
                                 operation_mode=operation_mode)
    if not site_has_a_destination(conn, routing, C_PLACEMENT,
                                  operation_mode=operation_mode):
        return {}
    placement_prompt = prompt_for(C_PLACEMENT)
    # D IS ASKED ONLY WHERE ITS OWN WORD PERMITS. C and D are ratified separately,
    # and the day C's word opened a target that D's did not, this line RAISED over
    # D -- turning C off on that target for a refusal about D's text. `None` is the
    # deployment `PipelineInputs.prompt_for` already knows: C wired and D not, and
    # a residual set that asks for a model is refused there, at the moment it
    # asks, naming the site that has no text. Nothing of D's leaves the device
    # under a word that forbids it, which is the count this gate keeps.
    residual_permitted = site_has_a_destination(conn, routing, D_RESIDUAL,
                                                operation_mode=operation_mode)
    residual_prompt = prompt_for(D_RESIDUAL) if residual_permitted else None
    authorities = PlacementCallAuthorities(
        # NO SINGLE PAIR: `route_for` below answers per file, and the two
        # spellings must not both be in force (`104` §17.13 ruling 3).
        model_client=None,
        gate=fact_authorities.gate,
        # ONE PROMPT EACH. This said "the prompt it sends is C's for both -- which
        # is a REAL limitation of wiring two sites through one function", and the
        # limitation is gone rather than reported: `PipelineInputs.prompt_for`
        # picks by call site and `run_call` refuses a request whose site is not the
        # prompt's. D's answer names one of §7.7's eight actions and C's schema has
        # no `action` key, so every residual answer was heading for
        # `SCHEMA_INVALID` -- for obeying text that was not its own either.
        prompt=placement_prompt,
        residual_prompt=residual_prompt,
        model_target=None,
        route_for=placement_route,
        evidence_resolver=fact_authorities.evidence_resolver,
        # NOT A's ORACLE, for the reason `_no_placement_contradiction` carries:
        # `contradicts_stronger` reads its argument as a P6 fact row and a
        # placement claim is not one.
        contradicts=_no_placement_contradiction,
        # NOT SITE A's, since `104` R-131's merge. `observe_scan_budget`
        # carries why: one call per file spends every slot before an
        # observe question is put, so this site drew from a purse the fact
        # pass had already emptied.
        scan_budget=observe_scan_budget(
            fact_authorities.scan_budget,
            corpus_file_count=placeable_file_count),
        estimated_cost=fact_authorities.estimated_cost,
        actual_cost=fact_authorities.actual_cost,
        policy_version=fact_authorities.policy_version,
        wire_handle_key=fact_authorities.wire_handle_key,
        sensitivity_policy=sensitivity_policy_for(conn),
        chosen_node_of=(_chosen_node_of(conn) if placement_prompt.ratified
                        else _must_not_apply(C_PLACEMENT)),
        residual_action_of=(_residual_action_of(conn)
                            if residual_prompt is not None
                            and residual_prompt.ratified
                            else _must_not_apply(D_RESIDUAL)),
        # `104` R-145: the SAME mailbox site A's `run_call` takes from. Site C's
        # responses carried no usage row until this line existed.
        usage_recorder=fact_authorities.usage_recorder)
    built = model_path_injections(conn, authorities, plan_version=plan_version)
    built.pop("sensitivity_policy", None)
    return built


#: The nine `model_path_injections` fills for C and D. `sensitivity_policy` is
#: the tenth and is supplied at `placement_inputs` by R-55 whether or not a model
#: is configured, so it is not in this set and is never overwritten from here.
OBSERVE_PLACEMENT_FIELDS: tuple[str, ...] = (
    "gate", "model_client", "prompt", "residual_prompt", "call_dependencies",
    "model_call_request", "chosen_node_of", "residual_action_of",
    "model_target", "route_for", "usage_recorder",
)


def observe_prompt(call_site: str) -> PromptDefinition:
    """The draft this deployment asks `call_site` under. Composed HERE, not in P8.

    `a_fact_prompt`'s rule, applied to a site whose text is not ratified: the
    library holds the bytes and verifies them against their digests, and the
    composition root picks the id, the call site and the version. The difference
    is the id itself, which carries `unratified` and the packet's date, so every
    `llm_response` and `llm_verdict` row written here says on its face that the
    text behind it was a draft.
    """
    template_id = OBSERVE_TEMPLATE_ID[call_site]
    template, response_schema, shaping_policy = draft_bytes(template_id)
    return PromptDefinition(
        template_id=template_id,
        template_bytes=template,
        response_schema_bytes=response_schema,
        call_site=call_site,
        call_site_version="1",
        # THIS DRAFT'S OWN STATUS, read from its manifest row and falling back to
        # the packet's word (`prompt_library.draft_status`), so the owner can
        # ratify one site's text without ratifying the other three.
        #
        # `ratified_local` COUNTS AS RATIFIED HERE and not at the locality gate:
        # this field is "act on the answer", which a local run may do, and the
        # gate is "these bytes may leave the device", which it may not.
        #
        # THE ID KEEPS `unratified` IN ITS NAME AFTER THE ROW IS RATIFIED: the id
        # names the FILE, not the file's standing, so the record written under it
        # says which text was used and the manifest row says whether that text was
        # ratified at the time. Renaming on ratification would strand every record
        # already written under the old id.
        ratified=draft_status(template_id) in STATUS_APPLIES,
        shaping_policy_bytes=shaping_policy)


def prompt_for(call_site: str) -> PromptDefinition:
    """THE ONE SEAM: what this deployment asks `call_site` under. `104` R-05.

    Five sites, five texts, five response schemas and five shaping policies, and
    exactly one function that pairs a site with its own. Two entry points would be
    two places for a site to be handed a neighbour's contract -- and that was not
    hypothetical: `observe_placement_injections` gave site D site C's prompt, so a
    residual answer naming one of §7.7's eight actions would have been judged
    against a schema with no `action` key in it.

    **Nothing is composed here.** `a_fact_prompt` reads the ratified bytes and
    their pinned digests, `observe_prompt` reads the D2 manifest and its digests,
    and both refuse rather than fall back. What this adds is the routing, and the
    routing is a lookup on `CALL_SITES`.

    **`ratified` is the definition's, everywhere it is read.** `_observed_only`,
    `PipelineInputs.model_decides` and `observed_run_call` all read the field off
    the object rather than parsing the id, so the day the owner ratifies a draft
    the site asked under it starts applying and no line of this file changes.
    """
    if call_site == A_FACT:
        return a_fact_prompt()
    if call_site == G_SITUATION_SENSITIVITY:
        return situation_prompt()
    if call_site in OBSERVE_CALL_SITES:
        return observe_prompt(call_site)
    raise ValueError(
        f"{call_site!r} is not a call site this deployment has text for. The "
        f"ratified site is {sorted(WIRED_CALL_SITES)} and the observe sites are "
        f"{sorted(OBSERVE_CALL_SITES)}; a site with no prompt is refused here "
        f"rather than given somebody else's.")


class UnratifiedPromptOnACloudTarget(RuntimeError):
    """An observe-only site was pointed at a model off this device."""


def observe_locality_permits(call_site: str, locality: str) -> bool:
    """Whether this site may be asked at this destination. LOCAL ONLY, in code.

    **`104` §13's standing count is "0 cloud calls with unratified prompts", and a
    count nobody enforces is a hope.** Today every prompt these four sites would
    send is a D2 DRAFT: `drafts_2026-09-06.json` carries `"status": "unratified"`,
    no row overrides it, and every `template_id` in it says `unratified` in the id
    itself, so a record written under one says so. `planning/82` §0 records the
    owner ratifying `A_fact`'s text and nothing else.

    Unratified text is text nobody has agreed to send. On this machine that is a
    question of taste; over the internet it is a person's dossier reaching a
    provider under a prompt their owner never approved, and it cannot be taken
    back. So the difference is enforced where it is a fact rather than promised in
    a comment: a cloud target for an UNRATIFIED observe site RAISES, and the raise
    happens at the composition root before a corpus has been read.

    **THE GATE IS THE TEXT'S STANDING, NOT THE SITE'S NAME**, and it is read per
    draft (`prompt_library.draft_status`) rather than per packet, so one site's
    word never speaks for the other three.

    **AND RATIFYING IS NOT THE SAME ACT AS OPENING THE CLOUD.** `104` §15.1 puts
    C's `eliminate-v2` to the owner FOR THE LOCAL MODEL, with the cloud waiting on
    R-82's signature, so the two are separate words and this gate reads only the
    second: `ratified_local` acts on its answer here and is still refused a cloud
    target; `ratified` is the word that says these bytes may leave the device.
    Local is permitted under every word, including `unratified`, which is the
    behaviour that has always been true -- nothing leaves the machine.

    `A_fact` is unaffected and stays cloud-eligible: it is not in this set, its
    text is ratified, and `WIRED_CALL_SITES` is what governs it.
    """
    if call_site not in _SITES_WITH_A_ROW:
        return True
    if locality == LOCAL:
        return True
    # `104` R-144: site A reads the same gate off its own row, so an A_fact v2
    # under `ratified_local` runs here and is refused a cloud target, as C is.
    # `104` §17.1: site G reads it off its own row too, and its row is
    # `ratified_local` -- "Nothing leaves the device under this ruling."
    return (draft_status(_template_id_for(call_site))
            in STATUS_MAY_CROSS_THE_INTERNET)


#: EVERY SITE WHOSE TEXT COMES THROUGH A MANIFEST ROW, which is the set this gate
#: can answer about. A site with no row has no word to read and is left alone; a
#: site with one is asked its own word before its bytes may cross the internet.
#: The four observe sites, site A since `104` R-144, and site G since `104` §17.1.
_SITES_WITH_A_ROW: frozenset[str] = (
    OBSERVE_CALL_SITES | {A_FACT, G_SITUATION_SENSITIVITY})


def _template_id_for(call_site: str) -> str:
    if call_site == A_FACT:
        return A_FACT_ROW[0]
    if call_site == G_SITUATION_SENSITIVITY:
        return SITUATION_ROW[0]
    return OBSERVE_TEMPLATE_ID[call_site]


def require_observe_locality(call_site: str, locality: str) -> None:
    """`observe_locality_permits`, as a refusal that names what was wrong.

    **THE SENTENCE NAMES THIS DRAFT'S OWN WORD, not the packet's.** The packet's
    word is only a default now, so a refusal quoting it could be flatly false
    about the row it is refusing -- a packet reading `ratified` over a row that
    says `unratified` would print "a D2 DRAFT ('ratified')" and send a reader to
    argue with the wrong line. The word here is the word the gate actually read.
    """
    if observe_locality_permits(call_site, locality):
        return
    raise UnratifiedPromptOnACloudTarget(
        f"call site {call_site!r} may not cross the internet under its prompt's "
        f"word ({draft_status(_template_id_for(call_site))!r}), but the routing "
        f"sends it to a {locality!r} model. "
        f"`104` §13 counts 0 cloud calls with unratified prompts and this is where "
        f"that count is kept. Unratified text is text nobody has agreed to send: "
        f"on this device that is a question of taste, and over the internet it is "
        f"a person's dossier reaching a provider under a prompt their owner never "
        f"approved. Configure {LOCAL_MODEL_NAME} and the observe sites run here; "
        f"ratify the text and the site joins WIRED_CALL_SITES instead.")

#: How many of a file's observations may be offered to a call about that file, and
#: the only place the NUMBER is chosen. §8.4 asks for "a compact dossier ... selected
#: excerpts", states no count, and `model_facts.releasable_observations` takes the
#: cap with no default.
#:
#: SITE C TAKES THE SAME NUMBER (`104` R-148), because it is the same question about
#: the same file: `cli.reading_citations` offers a placement call the readings the
#: fact call was offered, so the judge that decides where a file goes sees what the
#: judge that read its fields saw. A second cap would be a second answer to "how much
#: of this document may leave the device", and the ceiling both calls are measured
#: against (`model.max_dossier_tokens_per_call`) is one ceiling.
#:
#: TWELVE, and the cost of each direction is real. Too few and the model is shown a
#: title and three metadata fields and honestly declines every field -- which is a
#: call paid for and a fact not gained. Too many and §8.4's "data-minimizing" stops
#: meaning anything: every additional excerpt is more of a person's document at a
#: provider, and the response ceiling (`MAX_RESPONSE_TOKENS`) is fixed, so past some
#: point the extra evidence only crowds out the answer. Twelve is the count at which
#: a real coursework PDF's title, its page-one heading, its PDF metadata and a few
#: body readings all fit, measured on the owner's own Downloads.
#:
#: **IT BINDS A CLOUD CALL. A LOCAL CALL IS BOUND BY THE CEILING** (`104` R-159, the
#: owner's ruling of §15.4 item 14 on 8 Sep 2026). The number is unchanged and stays
#: exactly what it was for a cloud target. What changed is that a local target may be
#: shown a whole text unit, and once a page is releasable a COUNT stops being the
#: honest bound on how much of a document leaves: twelve spreadsheet cells are a few
#: hundred characters and twelve PDF pages are twenty thousand. So
#: `model_facts.within_dossier_budget` spends this cap for a cloud call and
#: `max_dossier_tokens` for a local one -- measured over the same corpus r15 ran,
#: keeping the twelve under local rules left 47 files over the ceiling and 26
#: PDF/docx files with no body reading at all, their slots taken by heading
#: fragments. Neither number is invented here; both were already stored.
FACT_CALL_MAX_RELEASED_OBSERVATIONS: int = 12

#: §8.6's spend ceilings for the fact pass, as a `ScanBudget`. `00` names them and
#: states no values.
#:
#: ONE CALL PER FILE is the shape of site A -- a fact is about a file -- so the rate
#: is a thousand per thousand files rather than a number that would silently make
#: most of a corpus unaskable. The FLOOR matters more than it looks: a rate per
#: thousand floors to zero on any corpus smaller than `1000 / rate`, and a wired
#: model that abstains on everything is indistinguishable from a model nobody wired.
FACT_CALLS_PER_1000_FILES: int = 1000
FACT_MIN_CALLS_PER_SCAN: int = 1

#: §8.6's spend ceilings for the OBSERVE AND PLACEMENT sites, which are not site A's
#: and were site A's until now. `00` names these ceilings and states no values; the
#: numbers below are the deployment's, exactly as the fact pair above.
#:
#: WHY A SECOND BUDGET AND NOT A LARGER ONE. B, C and D took `fact_authorities.
#: scan_budget` -- the same object, the same `scan_id`, the same reservations -- on
#: the argument that a budget is a fact about the run rather than about which site
#: is asking. The measurement says otherwise: site A is one call per FILE, so a
#: corpus where every file has an open question spends every slot before a
#: placement question is ever put. Measured on the six-file local corpus of
#: `tests/integration/test_local_model_fact_pass.py`: five fact calls, then site B
#: refused before a call and site C recording `BUDGET_EXHAUSTED` -- the sites that
#: decide WHERE a file goes starved by the site that decides WHAT it is. A larger
#: shared number moves the corpus at which that happens and does not change it.
#:
#: The rate and the floor are the fact pass's own values, stated again rather than
#: aliased: these are two policies that agree today, and a deployment that raises
#: one has no reason to raise the other by accident.
OBSERVE_CALLS_PER_1000_FILES: int = 1000
OBSERVE_MIN_CALLS_PER_SCAN: int = 1

#: The most calls the observe and placement sites may make in one scan. The same
#: argument as `FACT_CALLS_PER_SCAN_CEILING` and the same units -- one call costs
#: one -- and a separate number, because a run that spends its fact ceiling must
#: still be able to place what it learned.
OBSERVE_CALLS_PER_SCAN_CEILING: Decimal = Decimal("200")

#: The observe budget's own `scan_id`, DERIVED from the fact pass's rather than
#: minted, so a reader of `llm_budget_reservation` can see which run a row belongs
#: to. That column is a bare key with no foreign key to the scan and is indexed on
#: its own, so two ids are two ledgers -- and one id was the shared purse this
#: separation exists to end.
OBSERVE_BUDGET_SUFFIX: str = ":observe"

#: SITE G'S OWN LEDGER, and it exists because the defect `104` R-131 measured
#: happened again the moment site G was wired to `observe_scan_budget`. That purse
#: is B's, C's and D's; site G asks one call per UNSETTLED FILE and runs BEFORE all
#: three, so on the six-file corpus of `tests/integration/test_local_model_fact_
#: pass.py` it spent every observe slot and site C recorded `BUDGET_EXHAUSTED` for
#: five tests that had been green. A starved site looks exactly like a site nobody
#: wired (`104` R-04), which is why this is a third id and not a bigger second one.
SITUATION_BUDGET_SUFFIX: str = ":situation"

#: What one A_fact call is charged, and what it settles for. THIS DEPLOYMENT
#: MEASURES NEITHER A TOKEN NOR A PRICE: `readers.model_deepseek` returns no usage
#: figures, so a number here pretending to be dollars would be one nobody could
#: check. It is a UNIT -- one call costs one -- which makes the ceiling below a
#: count of calls in the same units as the rate above, and leaves the real
#: accounting owed rather than faked. `ScanBudget` takes both with no default and
#: reads nothing from P1's ceiling store, so this is the only place they are chosen.
FACT_CALL_COST: Decimal = Decimal("1")

#: The most calls one scan may make, whatever the rate works out to. Two hundred is
#: a bound on a first real run rather than an optimisation of one: it is more than
#: the folders `00`:20 describes a person naming, and small enough that a
#: misconfigured run costs a person a bounded amount of money before they see the
#: count printed at the end of it.
FACT_CALLS_PER_SCAN_CEILING: Decimal = Decimal("200")

#: `104` R-14's price hook, and it is `None` because nobody has supplied a rate
#: card. `00`:251 budgets "maximum model cost per scan" in MONEY, and the two
#: numbers above are denominated in CALLS -- one per call, two hundred per scan --
#: so what the budget enforces today is a call count wearing a cost's name.
#:
#: `llm_call_usage` now records what each call actually consumed beside what was
#: reserved for it, so the tokens exist; turning them into money needs prices, and a
#: price is a deployment fact this file may not invent any more than it invents a
#: model id. When the owner supplies one this is where it goes -- a mapping from
#: model id to a per-token rate, read by whatever prices the usage rows -- and until
#: then nothing multiplies a token by a number somebody guessed.
#:
#: MEASURED, as the proposal for a token-denominated ceiling rather than as a change
#: made here: an A_fact dossier on this branch is about 5,000 prompt tokens (`104`
#: R-58: 8,020 template bytes plus a body under 9,000, and a real call reported
#: 4,480 cache-hit of ~4,970 prompt tokens), so 200 calls is on the order of
#: 1,000,000 prompt tokens per scan. Re-denominating the ceiling is the owner's:
#: `00`:259 names coverage throttling as the failure a wrong number causes.
TOKEN_PRICES = None

#: §8.6's page cap for PDFs, and the only place the NUMBER is chosen. The reader
#: takes `max_pages=None` -- read everything -- and this file hands it a ceiling
#: through `macos_readers(read_pdf=...)`, the override seam that module's docstring
#: exists to offer. The measurements below were taken with pdfminer, which was the
#: reader at the time; `extraction_context()` says why they are pdfium's now. A
#: ceiling that costs nothing under the slower parser costs nothing under the faster
#: one, and the three files it was chosen to protect are the same three files.
#:
#: WHY THERE IS A CEILING AT ALL. Measured 2026-09-03 over a real 639-file
#: `~/Documents`: the run took 705 seconds, and 332 of them were ONE file --
#: `rp2040-datasheet.pdf`, 642 pages, vendored inside `Arduino/libraries/`. Layout
#: analysis is per page and unbounded, so a single vendored datasheet cost a person
#: half their run while 638 of their own files waited behind it.
#:
#: WHY FIFTY, AND NOT TWENTY. Twenty was the first value tried, and it was wrong:
#: measured over the same folder it classified 115 files where an uncapped run
#: classified 118, losing three PDFs of nine. A ceiling that reads fewer headings
#: recognises fewer documents, and buying 22 seconds with three files is not a
#: trade this product gets to make quietly.
#:
#: Fifty is the smallest ceiling measured that costs NOTHING. Whole-folder runs:
#:
#:      no ceiling   705.0s   118 files classified   9 of 41 PDFs
#:      50           306.4s   118 files classified   9 of 41 PDFs
#:      20           284.6s   115 files classified   6 of 41 PDFs
#:
#: 120 was also measured and classified the same 118 for 30 seconds more, so fifty
#: is where the curve flattens rather than a guess between two numbers. 24 of this
#: corpus's 41 PDFs are ten pages or shorter and no ceiling touches them at all.
#:
#: WHAT IT COSTS, STATED RATHER THAN HIDDEN. A capped read is recorded
#: `completeness="capped"` with `coverage {"processed": 20, "total": 642}` -- P4's
#: own vocabulary, the shape `extractors/ocr.py` has used since it was written. §2.4
#: forbids a partial read that calls itself complete, so the ceiling had to arrive
#: with the sentence that says it was reached. A ceiling that reported `complete`
#: would be a worse product than a slow one.
PDF_PAGE_CEILING: int = 50

#: HOW MANY SPREADSHEET CELLS ARE STORED PER FILE, and the only place that number is
#: chosen. A ceiling of the same kind as the page ceiling above, for the same reason
#: and with the same honesty attached.
#:
#: WHY A SPREADSHEET NEEDS ONE AND THE OTHER FIVE FAMILIES DO NOT. §2.9 asks a
#: spreadsheet for "visible cell values" and names no limit, so the reader stored
#: every non-empty cell of every sheet -- and each one becomes a `text_units` row AND
#: an `evidence` row, roughly 300 bytes of database apiece once the locators are
#: written. A presentation has slides, an email has one body, a calendar has events
#: and a contact card has fields; a spreadsheet is the one family whose size is
#: unbounded in the unit that costs. Measured on the owner's 199-file corpus,
#: 2026-09-04, with no ceiling at all:
#:
#:      13,994 of 23,983 text units were spreadsheet cells      58% of the rows
#:          82,428 of 2,357,143 characters were in them        3.5% of the text
#:       7,563 of 11,953 evidence rows came from that family
#:
#: WHAT THE CORPUS COULD AND COULD NOT SETTLE. Whole runs, varying only this number:
#:
#:      no ceiling   33.04 MB   23,983 units   176 of 199 read   101 classified
#:      10,000       31.82 MB   23,983 units   176 of 199        101 classified
#:       2,000       27.99 MB   20,293 units   176 of 199        101 classified
#:         500       23.28 MB   13,304 units   176 of 199        101 classified
#:
#: 10,000 is above every sheet in this corpus and changes not one row, which is what
#: makes the other two readable. EVERY ceiling measured, down to 500, cost NOTHING --
#: the same files read, the same prose recovered, the same files classified. So
#: unlike `PDF_PAGE_CEILING`, this
#: corpus does not pick the number: its largest sheet is 5,352 cells and none of them
#: is big enough for a ceiling to reach anything that carries meaning. What the runs
#: DO establish is the negative that matters -- 2,000 takes nothing away -- and the
#: number itself has to be argued rather than fitted, because fitting it to a corpus
#: whose spreadsheets are small is how a ceiling ends up too low for a disk whose
#: spreadsheets are not.
#:
#: WHY TWO THOUSAND. It is more than a person ever reads to find out what a sheet IS:
#: a 40-column table 50 rows deep, or a 5-column export 400 rows deep. §2.9's own
#: spreadsheet list leads with "workbook or file metadata, sheet names, column
#: headers", and the ceiling reaches none of those -- sheet names are entries,
#: workbook metadata is package properties, and the header row is row 1. Below about
#: 500 the header row of a wide sheet starts to be at risk, which is the one thing
#: that must never be cut; above about 10,000 the file is a data table rather than a
#: document and the rows bought stop being evidence.
#:
#: WHAT IT IS WORTH WHERE IT BITES. The corpus understates this badly, because it
#: holds no large spreadsheet. ONE synthetic 200,000-cell sensor export -- 1.9 MB of
#: `.csv`, the shape any lab or finance disk has several of -- through the real
#: extraction path, alone in its own folder:
#:
#:      no ceiling   483.6 MB db   200,001 text units   120,044 evidence   336.8 s
#:       2,000         5.2 MB db     2,001 text units     1,244 evidence     0.7 s
#:
#: 92x the database and 480x the time, for one file, for a table nobody will read
#: back. The SECONDS are the half a person actually feels: five and a half minutes
#: of a scan spent on one sensor log while every document they wrote waits behind it.
#: And the capped run says so -- `capped`, `2,000 of 200,000 cells` -- rather than
#: reporting a complete reading of a file it read one percent of.
#:
#: WHAT IT COSTS, STATED RATHER THAN HIDDEN. A capped read is recorded
#: `completeness="capped"` with `coverage {"units": "cells", "processed": 2000,
#: "total": 5352}`. §2.4 forbids a partial read that calls itself complete, so the
#: ceiling arrives with the sentence that says it was reached -- and the cells past it
#: are COUNTED before they are dropped, so that total is the file's real size and not
#: the ceiling wearing a full count.
SPREADSHEET_CELL_CEILING: int = 2000

#: §8.6's "Maximum pages OCRed per file" (`00`:245), and the only place it is chosen.
#:
#: WHY IT WAS MISSING RATHER THAN SET WRONG. `readers/ocr_vision.py` has honoured a
#: `page_cap` since it was written -- it stops between pages, reports `capped=True`,
#: and `extractors/ocr.py` turns that into `completeness="capped"` with P4's own
#: `coverage {"processed": n, "total": m}`. `VISION_CONFIG` carried languages, dpi
#: and recognition level and no ceiling, so `page_cap` was `None` on every run this
#: product has made and §8.6's most expensive operation was the one with no bound.
#:
#: THE NUMBER, MEASURED. Over the owner's ground-truth corpus on 2026-09-06 with
#: pdfium, no OCR and no model: 68 readable PDFs, median 2 pages, longest 287. At 20
#: pages, 61 of the 68 are untouched; at 50 it is 63. Seven files buy the whole tail,
#: and the tail is what §8.6 means by "a large scanned textbook should not consume
#: the same budget as hundreds of ordinary PDFs". Twenty pages of Vision at 200 DPI
#: is the order of a minute; 287 would be twenty.
OCR_PAGE_CEILING: int = 20

#: §8.6's "Maximum OCR time per file" (`00`:246), in seconds, and it is deliberately
#: a fraction of `EXTRACTION_SECONDS_PER_FILE` below.
#:
#: THE TWO CLOCKS ARE RELATED AND THE ORDER MATTERS. R-50 gave `ProcessPool` a
#: per-extraction ceiling that kills a worker wedged inside Vision, because a Python
#: timeout cannot interrupt a C dispatch wait. That rescue costs the file everything:
#: the worker dies holding whatever it had read. This ceiling is checked BETWEEN
#: pages, so when it fires the run keeps the pages it finished and records why it
#: stopped. An in-process limit is only worth having if it is reached first, which is
#: why 120 sits well under 600 and why a test asserts the inequality rather than
#: trusting whoever next edits one of them.
OCR_SECONDS_PER_FILE: int = 120

#: HOW MANY PROCESSES READ FILES AT ONCE, and the only place the number is chosen.
#: `extraction_pool.ProcessPool` refuses to default it, for the reason every number
#: in this product refuses to default: absent means refuse, never guess.
#:
#: WHY THERE IS A POOL AT ALL. `grep -rn "multiprocessing\|concurrent" src/` returned
#: nothing, on a machine with eight cores, while a whole-run profile of eighteen real
#: files put 64.6 of 72.0 seconds inside `extract_initial`. Reading a file is the only
#: part of a run that is embarrassingly parallel: every database write stays on the
#: calling thread in roster order, and sqlite is a serial writer anyway.
#:
#: WHY SEVEN AND NOT EIGHT. The calling thread is not idle while the workers read --
#: it writes every row, runs P4's resolution and P6's detector, and holds the only
#: connection. Taking all eight cores for readers makes the thread that consumes
#: their output compete with them for the last one.
EXTRACTION_WORKERS: int = 7

#: HOW FAR THE CALLER READS AHEAD, per worker. Deep enough that a worker is never
#: idle waiting for the next submit -- one request each would leave every worker
#: blocked whenever the caller stopped to write a row -- and shallow enough that a
#: 5,760-file run holds a handful of extraction batches in memory rather than all of
#: them. Two is the smallest depth that keeps a worker busy across one write.
EXTRACTION_LOOKAHEAD_PER_WORKER: int = 2

#: R-50. HOW LONG ONE EXTRACTION MAY TAKE BEFORE ITS WORKER IS KILLED.
#:
#: The pool already survives a worker that DIES. It could not survive one that never
#: returns, and that is not hypothetical: measured on the owner's corpus, three of
#: seventeen scoreboard situations hung for ever at 0% CPU --
#: `applications.undergraduate-packet`, `business_operations.project-delivery` and
#: `code.notebooks-experiments`. Sampled, one worker's main thread was inside
#: `-[VNRecognizeTextRequest ...]` -> `-[CIContext render:toCVPixelBuffer:...]` ->
#: CoreImage -> `_dispatch_sync_f_slow` -> `__DISPATCH_WAIT_FOR_QUEUE__`, a dispatch
#: deadlock inside Apple's frameworks reached through PyObjC by the OCR reader; the
#: other six workers sat in `sem_wait`. `00`:257 says a single file may not consume
#: the run, and nothing could enforce it against a file that consumes the run by
#: doing nothing at all.
#:
#: WHAT IT MEASURES, because the first draft measured the wrong thing and the suite
#: said so within the hour. It is the time this file has been THE ONE HOLDING UP THE
#: RUN -- the clock starts when the consuming loop begins waiting for it, not when it
#: was submitted. Measured from submit, a hung file burns the ceiling while the files
#: behind it sit in the queue, so when their turn comes they are already over it: one
#: deadlock marked `01-alpha.pdf` and `02-bravo.pdf` timed out having done nothing
#: wrong, which is one deadlock failing the whole look-ahead window.
#:
#: So this is a DEADLOCK DETECTOR and not a performance budget. It is not competing
#: with queueing depth, and it does not need to exceed `lookahead` extractions; it
#: needs to exceed the slowest single honest extraction this deployment permits. That
#: is OCR over a scanned page, measured at up to about twenty seconds on the owner's
#: files, against a 50-page PDF ceiling and a 2,000-cell spreadsheet ceiling that are
#: both faster.
#:
#: Six hundred seconds is ten minutes, thirty times the slowest honest read. A run
#: that spends ten minutes waiting on one file has something wrong with it in every
#: case this product can name.
#:
#: WHAT THE FILE GETS FOR IT, since R-112: a second attempt, in the same run, in a
#: pool holding nothing but itself. The wedge this ceiling catches is a race on a
#: machine-wide lock inside Apple's frameworks and not a property of the bytes --
#: measured, the same PNG read in ten runs of eleven and wedged in one -- so a single
#: attempt sent a person away with a file that was never unreadable. Only a file that
#: wedges twice is recorded `unexamined`, with the ceiling, the reader and the fact
#: that it was tried twice in the row, which is a sentence an operator can act on.
#: The bound a file may cost this run is therefore two of these ceilings, which is
#: the same bound the death path has always allowed a file that segfaults.
EXTRACTION_SECONDS_PER_FILE: float = 600.0

#: The wire handle key. `llm_harness.wire_handles` digests every identifier that
#: leaves this device under it -- `subject_ref`, every `conflict_id`, every released
#: `observation_key`, every `evidence_ref` that is a P4 key -- because an un-keyed
#: digest of the person's own content is a dictionary attack the recipient can run
#: in a second, and two of them were run against this product.
#:
#: 32 bytes: HMAC-SHA256 hashes any key longer than its 64-byte block down to no
#: benefit, and a key shorter than its 32-byte output is the weakest part of the
#: digest. It is the length below which the key, rather than the guess space, is
#: what an attacker goes after.
WIRE_HANDLE_KEY_BYTES: int = 32

#: Beside the database and NOT INSIDE IT, which is the whole point of a separate
#: file. A database is the thing that gets copied -- to a backup, into a support
#: bundle, alongside a shared corpus snapshot -- and a key stored in a row travels
#: with every one of those copies, protecting nothing the moment one is shared. The
#: key is what makes a released handle uninvertible; separating it from the data
#: whose identifiers it protects is why copying the database leaks no handles.
#: `open_database` already refuses a database inside a scan root, and the key
#: follows the database, so it inherits that refusal for free.
WIRE_HANDLE_KEY_FILENAME: str = ".wire-handle-key"

#: Readable and writable by this user and by nobody else.
WIRE_HANDLE_KEY_MODE: int = 0o600


def wire_handle_key_for(database: Path) -> bytes:
    """The local-only key, minted once per database and read back ever after.

    It is a CREDENTIAL. It is never printed, never logged, never written to an
    audit row, never put in an exception message and never sent. Nothing in `src/`
    outside this function reads the file.

    **Per database, not per run, and that is a trade made here rather than in the
    package.** `dossier_id` is the content address of the model-visible bytes, and
    those bytes carry keyed handles -- so a key that changed between runs would give
    two calls over identical content two different addresses, and
    `llm_harness.store.record_dossier` would stop recognising the second as the
    first. Every cross-run replay and every cache lookup leans on that recognition.
    The cost of keeping it: a handle is stable for as long as the key is, so a
    provider can still see that two calls named the same observation, even though it
    can no longer discover WHICH observation. Inversion is closed; linkage is not.

    Rotation costs exactly that recognition and nothing else: the local
    `observation_key` never changes, so `privacy.resolve`, the audit record, P6's
    citations and every stored evidence row still address what they always did.
    """
    path = database.expanduser().resolve().parent / WIRE_HANDLE_KEY_FILENAME
    if path.exists():
        key = path.read_bytes()
        if len(key) != WIRE_HANDLE_KEY_BYTES:
            # Never echo the contents. Say where and how long, and stop.
            raise SystemExit(
                f"{path} is {len(key)} bytes; a wire handle key is "
                f"{WIRE_HANDLE_KEY_BYTES}. Refusing rather than digesting "
                "identifiers under something that is not a key."
            )
        return key
    key = secrets.token_bytes(WIRE_HANDLE_KEY_BYTES)
    # O_EXCL so two runs racing to mint the first key cannot each write one.
    descriptor = os.open(
        path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, WIRE_HANDLE_KEY_MODE)
    with os.fdopen(descriptor, "wb") as sink:
        sink.write(key)
    return key


def _dotenv(path: Path) -> Mapping[str, str]:
    """`KEY=value` lines from a file, for names the environment has not set.

    Ten lines rather than a dependency. `pyproject.toml`'s `dependencies` is empty
    on purpose, and the one thing this needs -- read a file of `KEY=value` lines --
    is not worth a package that also does interpolation, shell quoting and variable
    expansion that this deployment would then have to reason about. A missing file
    is the ordinary state of a fresh checkout and is not an error.

    THE REAL ENVIRONMENT WINS. A person who exports a key for one run means it for
    that run, and a file that quietly overrode them would send their files to a
    model they did not choose -- a surprise in the one direction that costs money
    and leaves the device.
    """
    values: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return values
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        name, _, value = stripped.partition("=")
        values[name.strip()] = value.strip().strip('"').strip("'")
    return values


class UsageMailbox:
    """One slot holding what the provider reported for the call just made.

    `104` R-14. The transport reads usage inside `invoke`; `harness.run_call` needs
    it a moment later, when it holds the reservation, the release and the dossier at
    once. `ModelClient.invoke` is `Callable[[bytes], bytes]`, so the number cannot
    ride the return path, and this is the smallest thing that carries it: the
    composition root builds one, hands it to the transport as `on_usage` and to
    `run_call` as `usage_recorder`, and the two never learn about each other.

    ONE SLOT AND NOT A QUEUE. `run_call` takes immediately after the call it made,
    so a second value in the box would mean a call nobody settled; losing it loudly
    at the next `take` is better than a queue quietly pairing one call's tokens with
    another call's row.

    IT IS ALSO THE TRANSLATION. `llm_harness` may not import `readers`, so a
    provider's `Usage` type cannot cross that line; what crosses is a mapping whose
    keys `store.USAGE_COLUMNS` names, built here, where both sides are known. `{}`
    is a real answer and is not `None`: it means a call was made and the provider
    reported nothing, which the row records as nulls.
    """

    def __init__(self) -> None:
        self._held: dict | None = None

    def __call__(self, usage) -> None:
        self._held = {} if usage is None else {
            "model_id": usage.model_id,
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "prompt_cache_hit_tokens": usage.prompt_cache_hit_tokens,
            "prompt_cache_miss_tokens": usage.prompt_cache_miss_tokens,
            "response_format": usage.response_format,
        }

    def take(self) -> dict | None:
        held, self._held = self._held, None
        return held


def model_route(*, out, on_usage=None) -> TierRouting | None:
    """`83`'s three clients, or `None` and a sentence saying why not.

    **`None` is a real answer and not a failure.** P6's direct and rule stages,
    P4's evidence locations and P7's gate settle files with no model at all, and
    `83` §5 is explicit that the cheapest saving is not a smaller model but not
    making the call. A run with no key does every one of those things and then says
    what it could not do -- which is the opposite of the silence it replaces.

    **What it must never be is a traceback.** No key is the ordinary state of a
    fresh checkout, and a misspelled model name is an ordinary mistake. Both print
    one sentence and the run continues without a model.

    **It no longer announces.** Whether these models will actually be ASKED is a
    question about this folder's consent, which this function does not read;
    `announce_cloud_posture` holds both halves and says one true thing rather than
    two half-true ones.
    """
    from os import environ

    # THE ENVIRONMENT MAY WITHHOLD THE KEY, and until now it could not. `ENV_FILE`
    # is the repository's own `.env`, read unconditionally, so a process that set
    # no credential still got one -- including every test in this suite. Measured:
    # `test_a_second_source_does_not_send_under_the_first_ones_consent` passes
    # `--enable-cloud`, found a real key, built a real client and made a real call
    # to a paid API; the run stopped for ten minutes with no output, twice, and the
    # whole suite became unrunnable the moment the A_fact site was wired.
    #
    # A test that spends the owner's money is a defect whatever it asserts, and a
    # deployment with no way to say "not this run" has no way to be tested at all.
    # `GRAPH_AGENT_NO_DOTENV` is that way: set it and the file is not read. The
    # environment still wins over the file when it is not set, which is unchanged.
    supplied = ({} if environ.get("GRAPH_AGENT_NO_DOTENV")
                else _dotenv(ENV_FILE))

    def value(name: str) -> str:
        # The environment first, then the file, then nothing. Never a literal.
        return (environ.get(name) or supplied.get(name) or "").strip()

    local_model = value(LOCAL_MODEL_NAME)
    if not value(CREDENTIAL_NAME) and not local_model:
        # BOTH NAMES, because there are now two ways to have a model and a person
        # who is told only about the cloud one is told the product needs a paid
        # account to think at all. `00`:189-193's second mode is a model on their
        # own machine, and it costs nothing and sends nothing.
        print(_wrapped(
            f"No model was consulted: neither {CREDENTIAL_NAME} nor "
            f"{LOCAL_MODEL_NAME} is set, so this run used only what it could read "
            f"and decide on this device. Files that needed a judgement are named "
            f"below and say so. To enable one, either install a local model "
            f"(`ollama pull qwen3:8b`) and set {LOCAL_MODEL_NAME} to its id, which "
            f"sends nothing anywhere, or copy `.env.example` to `.env` and put a "
            f"key in it.", indent=""), file=out)
        return None
    cloud: TierRouting | None = None
    if value(CREDENTIAL_NAME):
        try:
            cloud = deepseek_routing(
                api_key=value(CREDENTIAL_NAME),
                base_url=value(BASE_URL_NAME),
                model_id_of_tier={tier: value(name)
                                  for tier, name in MODEL_NAME_OF_TIER.items()},
                tier_of_call_site=TIER_OF_CALL_SITE,
                max_response_tokens=MAX_RESPONSE_TOKENS,
                timeout_seconds=MODEL_CALL_TIMEOUT_SECONDS,
                # `104` R-14, threaded and not read here. Both routes take it:
                # the local one usually SERVES A_fact, so a sink wired only to the
                # cloud would leave the ordinary deployment's rows tokenless.
                on_usage=on_usage)
        except (ValueError, RuntimeError) as refusal:
            # Every refusal `readers/` can raise names what was missing and what to
            # set. Printed, not raised: a misconfigured model is not a reason to
            # refuse a scan that needs no model to do most of its work.
            print(f"\nNo cloud model was consulted, and here is what it needed:\n"
                  f"  {refusal}", file=out)
            if not local_model:
                return None
    if not local_model:
        return cloud
    try:
        if cloud is not None:
            # `104` §17.13 ruling 3: BOTH, and the choice is made per file rather
            # than per site. `serves=A_FACT` used to hand the local model site A's
            # whole tier and leave the rest on the key -- so a run either sent
            # every fact question to a provider or none of them, and half the
            # corpus was refused outright because the cloud gate cannot see an
            # unclassified file. Holding both clients is what lets `target_for`
            # send the classified, unprotected files to the cloud and keep the
            # rest here.
            return cloud_and_local_routing(
                beside=cloud,
                model_id=local_model,
                base_url=value(LOCAL_BASE_URL_NAME),
                max_response_tokens=MAX_RESPONSE_TOKENS,
                context_ceiling=LOCAL_CONTEXT_CEILING,
                timeout_seconds=LOCAL_MODEL_TIMEOUT_SECONDS,
                on_usage=on_usage)
        # D1's local half, alone: one installed model answers every site.
        return ollama_routing(
            model_id=local_model,
            base_url=value(LOCAL_BASE_URL_NAME),
            tier_of_call_site=TIER_OF_CALL_SITE,
            max_response_tokens=MAX_RESPONSE_TOKENS,
            context_ceiling=LOCAL_CONTEXT_CEILING,
            timeout_seconds=LOCAL_MODEL_TIMEOUT_SECONDS,
            serves=None,
            beside=None,
            # `104` R-14, and this is the route that answers every site here: a
            # deployment with only a local model gives it every question, so a
            # usage row with no tokens on it would be the ordinary case rather
            # than the exception.
            on_usage=on_usage)
    except (ValueError, RuntimeError) as refusal:
        # NO MODEL AT ALL, and deliberately not the cloud one. A person who set
        # {LOCAL_MODEL_NAME} asked for the model on their own machine; quietly
        # sending their files to a provider instead because their local setup is
        # wrong is the one direction that costs money and leaves the device, and
        # it is the surprise `_dotenv` refuses for the same reason.
        print(f"\nNo model was consulted, and here is what the local one needed:\n"
              f"  {refusal}", file=out)
        return None


def _turn_off_line(corpus_root: Path, *other_sources: Path) -> str:
    """The command that revokes, pasteable. `84` §6: what the screen tells a person
    to type has to be true, which is why the path is quoted rather than
    interpolated bare -- the folders this product is for have spaces in their
    names.

    **EVERY source, or the sentence is a trap.** `00`:20 lets a run read several
    folders and `--enable-cloud` clears each of them separately, so a turn-off
    line naming only the first is an instruction that leaves the rest sending.
    A person pastes it, reads that sending is off, and a later run over the
    second folder sends -- the exact footgun `--disable-cloud` was widened to
    close, reintroduced by the line the product tells them to type. "What the
    screen tells a person to type has to be true" is the whole rule.
    """
    return ("    database-agent " + shlex.quote(str(corpus_root))
            + "".join(f" --also-read {shlex.quote(str(source))}"
                      for source in other_sources)
            + " --disable-cloud")


def _fact_pass_models(routing: TierRouting) -> str:
    """The model or models site A's files were sent to, named for the screen.

    One name on a one-destination deployment, which is every deployment before
    `104` §17.13 ruling 3 and most of them after it. Two when a key and a local
    model are both configured, because that run really did send some files to each
    and a sentence naming one of them is a sentence about half the corpus. Which
    files went where is on each file's own line; this is the header.
    """
    cloud = routing.model_id_for(A_FACT)
    if not _local_beside_cloud(routing, A_FACT):
        return cloud
    return f"{cloud}, or {_local_model_id(routing, A_FACT)} on this device"


def _announced_locality(routing: TierRouting, call_site: str,
                        consent: "CloudConsent | None") -> str:
    """WHERE THIS RUN'S FILES ACTUALLY GO at this site, for the screen.

    `locality_for` answers about the cloud half of a two-target deployment, which
    is what the observe gates want and is the wrong answer for a person reading
    what happened to their folder: with sending off, `mode_forbids` drops the cloud
    candidate and every file is answered here. A notice that named the provider
    would be describing a destination this run cannot use.

    `104` §17.13 ruling 3 is why the two came apart at all. Before it the routing
    had one client per site and this question had one answer.
    """
    if (routing.locality_for(call_site) == CLOUD
            and not mode_forbids(operation_mode_for(consent), CLOUD)):
        return CLOUD
    return routing.route_for(call_site, cloud_permitted=False)[1].locality


def _local_beside_cloud(routing: TierRouting, call_site: str) -> bool:
    """Whether this site has a cloud destination AND a local one behind it.

    The two-target deployment `104` §17.13 ruling 3 describes, asked as one
    question so the screen and the route cannot disagree about which deployment
    this is. `route_for` is the only reader of the second client anywhere, and this
    is how the announcement reaches it without learning the routing's shape.
    """
    return (routing.locality_for(call_site) == CLOUD
            and routing.route_for(
                call_site, cloud_permitted=False)[1].locality == LOCAL)


#: The question each MODEL SITE asks, in the person's own words, for the consent
#: notice. Screen text and nothing else: no reader decides anything by it.
#:
#: **Site G joined this table on `104` §18.2 gap 9, and it is not cloud-eligible.**
#: The comment here read "each cloud-eligible site" while site G -- the site that
#: decides whether a file may reach the cloud AT ALL -- was in no per-site line of
#: the notice and in no posture branch. A person reading the notice was told about
#: the three sites that act on a file's situation and nothing about the site that
#: chooses it, which is the one they would most want named. Its row is
#: `ratified_local` (§17.14), so `observe_locality_permits` refuses it the internet
#: and it never appears among the recipients below; it appears in a sentence of its
#: own, and `_situation_site_sentence` is where the difference is kept.
_QUESTION_OF_SITE: dict[str, str] = {
    A_FACT: "a FACT judgement -- what course, what school, what kind of document --",
    C_PLACEMENT: "a placement CHECK -- whether a proposed folder is the right one --",
    D_RESIDUAL: "a REVIEW SET -- what to do with what nothing else placed --",
    G_SITUATION_SENSITIVITY:
        "a SITUATION judgement -- which situation a file is asked under, and "
        "whether it may reach the cloud at all --",
}

#: The three sites a file's text may be sent to, and the ONLY three this notice
#: names recipients for. Spelled once because two lines below read it and a fourth
#: member arriving in one of them and not the other is how site C came to be hidden
#: for a day (`104` §17.13). Site G is deliberately absent: it has a row in
#: `_QUESTION_OF_SITE` above and no place here, because a site whose text may not
#: cross the internet has no recipient to name.
_SITES_THAT_MAY_SEND: tuple[str, str, str] = (A_FACT, C_PLACEMENT, D_RESIDUAL)


def _local_model_id(routing: TierRouting, call_site: str) -> str:
    """The NAME of the model on this device, for the sentence that names it.

    `model_id_for` answers about the cloud half on a two-target deployment, which
    is right for every other sentence and wrong for this one. A person told their
    file is going to "a model on your device" has been told less than a person told
    which model.
    """
    return routing.route_for(call_site, cloud_permitted=False)[1].model_id


def _situation_site_sentence(routing: TierRouting) -> str:
    """Site G's line in the posture notice, or `""` where G cannot run.

    **`104` §18.2 gap 9, second half.** Site G was absent from the per-site table
    and from every posture branch, so the notice described three sites that act on
    a file's situation and never named the one that DECIDES it. `104` §17.14 is
    what makes that the worst omission of the four: G "is the site that decides
    whether a file may go to the cloud at all", and a person deciding about sending
    was being shown every consequence of that decision and not the decision.

    **THE SENTENCE CLAIMS ONLY WHAT G DOES**, in the vocabulary the branches around
    it already use -- "answered by X on this device", "do not leave it" -- with the
    question itself read out of `_QUESTION_OF_SITE` so the notice cannot describe
    this site in two ways. Nothing here says G is accurate, or that its answer is
    final, because neither is this screen's claim to make.

    **`""` WHERE G HAS NO LOCAL DESTINATION, and that is not a detail.** G's row is
    `ratified_local`, so `target_for` drops its cloud candidate for every file and a
    deployment with a key and no local model simply does not run this site -- the
    pass is `_NOTHING_ASKED` and no file is asked its own situation. A sentence
    saying G decides anything on such a run would be the notice describing work
    that did not happen, on the one screen where being believed is the whole point.

    The name comes off the LOCAL half of the route for `_local_model_id`'s reason:
    `model_id_for` answers about the cloud half on a two-target deployment, and
    this site never reaches it.
    """
    _client, target = routing.route_for(G_SITUATION_SENSITIVITY,
                                        cloud_permitted=False)
    if target.locality != LOCAL:
        return ""
    # THE SENTENCE STOPS WHERE THE CLAIM DOES. A first version added "decided
    # here before anything about it is assembled for any other model", which is
    # true of this build by construction and is a claim about ORDERING that
    # nothing on this screen is being asked to make. On the notice a person
    # decides by, every extra clause is another thing that has to stay true.
    return _wrapped(
        f"Files that need {_QUESTION_OF_SITE[G_SITUATION_SENSITIVITY]} are "
        f"answered by {target.model_id} on this device and do not leave it.",
        indent="  ")


def announce_cloud_posture(routing: TierRouting | None,
                           consent: CloudConsent | None, *,
                           corpus_root: Path,
                           other_sources: Sequence[Path] = (),
                           out) -> None:
    """Say, BEFORE the scan, whether this run may send and why.

    **Before, and not after.** `80` §8's second condition and `88` §3 both say it in
    the same words: a run that sends says so on screen BEFORE sending -- not after,
    not in a log. A notice printed at the end is a receipt, and a receipt is what a
    person gets instead of a choice.

    **It names the date and the person, because the consent is durable.** The owner
    accepted that "consent outlives the moment it was given", and this sentence is
    what makes that survivable: a person who reads "you turned this on for this
    folder on 14 June" can recognise a decision they have forgotten. "Cloud sending
    is on" tells them nothing they can act on.

    **It always says how to turn it off.** Consent that cannot be withdrawn is not
    consent, and a withdrawal a person has to go and look up is one they will not
    make. `80` R2's friction budget is spent on the decision, not on undoing it.

    **The off case earns its sentence too.** A file that could not be judged says
    "§8.4 did not clear this file for a model call", which reads as a fact about
    that file and is a fact about this folder's consent. The header is where the
    difference gets said.
    """
    if consent is not None and consent.permits_sending:
        print(f"\nCloud sending is ON for this folder"
              f"{'' if routing else ', but no model is configured'}.", file=out)
        if routing is not None and _local_beside_cloud(routing, A_FACT):
            # BOTH MODELS, AND THE PERSON IS TOLD WHICH FILES GO WHERE (`104`
            # §17.13 ruling 3). Naming only the cloud model would be true of the
            # files that reach it and silent about the rest -- and "the rest" is
            # protected material and everything site G has not classified yet,
            # which is the half of their corpus they would most want to ask
            # about. A person who is told one destination assumes one destination.
            print(_wrapped(
                f"Files this folder's rules keep off the internet -- protected "
                f"material, and anything not yet classified -- are answered by "
                f"{_local_model_id(routing, A_FACT)} on this device instead, and "
                f"do not leave it.", indent="  "), file=out)
        elif routing is not None and routing.locality_for(A_FACT) == LOCAL:
            # FACTS ARE NOT PART OF WHAT WAS TURNED ON. Consent is about what
            # leaves the device, and with the fact question answered on this
            # machine the sentence below -- "may be sent to X" -- would name a
            # model on their own hard disk as a recipient of their files.
            print(_wrapped(
                f"Facts are answered by {routing.model_id_for(A_FACT)} on this "
                f"device and do not leave it, whatever this folder's sending "
                f"says.", indent="  "), file=out)
        # The path on its OWN line, never inside a wrapped paragraph. `textwrap`
        # breaks a long unbroken token across lines, and half a path on each of two
        # lines is a path a person cannot read and must not copy. The folders this
        # product is for have spaces and long names; that is the ordinary case.
        # EVERY folder the run reads, one per line. The consent record this
        # sentence quotes belongs to one of them -- `_weakest_consent` returns a
        # single decision -- but the SENDING is this run's, over every source it
        # was given. Naming one of several would tell a person the scope of a
        # permission is smaller than what is about to leave their device.
        print(f"  Turned on by {consent.user_id} on {consent.decided_at}, for:",
              file=out)
        for folder in (corpus_root, *other_sources):
            print(f"    {folder}", file=out)
        if routing is None:
            print(_wrapped(
                "Nothing was sent and nothing could have been: no model is "
                "configured for this run. Turn sending off with:",
                indent="  "), file=out)
        elif not MODEL_CALL_SITES_WIRED:
            # A CONFIGURED MODEL IS NOT A REACHABLE ONE. The route exists and the
            # key works; no call site does. Saying "may be sent" here would be the
            # product frightening a person about something it cannot do, on the one
            # screen where being believed is the whole point.
            #
            # But the two things this notice already earned stay: the models are
            # NAMED, because a person told "an external provider" has been told
            # less than a person told the name; and protected material is said to
            # be excluded, because that is the standing rule and this is where a
            # person is deciding. Both were dropped by a first version of this
            # branch and both matter MORE once the wiring lands, not less -- a
            # person reading today's notice is deciding about tomorrow's runs.
            print(_wrapped(
                f"Nothing was sent and nothing could have been. Three models are "
                f"configured -- {routing.model_id_for(A_FACT)} (facts), "
                f"{routing.model_id_for(C_PLACEMENT)} (checks) and "
                f"{routing.model_id_for(D_RESIDUAL)} (review sets) -- but no part "
                f"of this run can call one yet, so every file was judged on this "
                f"device. Protected material and §8.4's always-local kinds are "
                f"refused by P7 and would not be among what they receive when that "
                f"changes. Sending stays ON for this folder until you turn it off "
                f"with:", indent="  "), file=out)
        else:
            # PER SITE, READ OFF THE TWO GATES THE ROUTE ITSELF READS (`104`
            # §17.13, R-170): a site names a recipient only if its cloud client
            # serves it AND its text may cross (`observe_locality_permits`, the
            # row's own word). A sentence that named all three would frighten a
            # person about things that cannot happen; one that named only site A
            # -- what this branch said until 9 Sep 2026 -- hid site C the moment
            # C's text was ratified. Every model is still NAMED, including the
            # ones that will not be asked: a person deciding today is deciding
            # about tomorrow's runs.
            #
            # WHAT LEAVES is said in the person's own terms, and it is `104` R-82's
            # sentence: since §17.13 a cloud model is shown what the local one is
            # shown -- the file's name, the path of the folder it sits in, its
            # extracted or recognised text within the dossier bound -- and the
            # earlier clause here ("your paths, your filenames, whole documents
            # ... are not among what is sent") would now misstate two of its
            # three items on the one screen where being believed is the point.
            #
            # THE FOLDER PATH IS RELATIVE, and that clause is `104` §18.7's ruling
            # ("Folder path: relative to the scanned folder for the cloud; the
            # local model may still see the full path"), which answered §18.1's
            # "one honest addition": the path this notice promised was ABSOLUTE,
            # so the home directory and the account name crossed with it and the
            # model gained nothing from the part above the corpus root. The
            # sentence names the folders it is relative TO by standing directly
            # under the "for:" list this branch has just printed -- a person who
            # reads "relative to the folder you scanned" can see, three lines up,
            # which folder that is. The half the ruling did NOT move is said in
            # the same breath rather than left to be inferred: the part above the
            # scanned folder stays on this machine, because a person told what
            # leaves is owed the boundary and not only the item.
            #
            # THE BOUNDARY SENTENCE NAMES NO CONTENTS, and that is deliberate. On
            # this machine the part above the corpus root is usually the home
            # directory and the account name -- which is why §18.1 called this a
            # leak worth closing, and it is said HERE, in a comment, where it is
            # a motivation. On the screen it would be a claim, and it is false
            # for a scan of an external volume (`/Volumes/...`), false for a scan
            # of the home directory itself, and imprecise whenever the corpus
            # sits some folders down. "The part of the path above the folder you
            # scanned" is true of every one of those, which is the only standard
            # a sentence on this screen is allowed to meet (`84` §6).
            #
            # This sentence is true only while `Gate` is given the run's scanned
            # folders and makes a `path`-zone value relative to them before a
            # CLOUD release (`104` §18.7, the edit `src/privacy/gate.py` carries).
            # If that door is ever unwired, this clause is the first thing that
            # becomes false, and `84` §6 is what it would be false against.
            crossing = tuple(
                site for site in _SITES_THAT_MAY_SEND
                if routing.locality_for(site) == CLOUD
                and observe_locality_permits(site, CLOUD))
            kept = tuple(site for site in _SITES_THAT_MAY_SEND
                         if site not in crossing)
            if crossing:
                sending = "; ".join(
                    f"files that need {_QUESTION_OF_SITE[site]} may be sent to "
                    f"{routing.model_id_for(site)}" for site in crossing)
                sending = sending[:1].upper() + sending[1:] + "."
            else:
                sending = ("No site's text is ratified to cross the internet in "
                           "this run, so nothing is sent.")
            held = ("" if not kept else " " + " and ".join(
                routing.model_id_for(site) for site in kept)
                + (" is" if len(kept) == 1 else " are")
                + " configured and no part of this run sends anything there.")
            print(_wrapped(
                f"{sending}{held} What leaves about a file: its name, the path of "
                f"the folder it sits in relative to the folder you scanned, and "
                f"its extracted or recognised text within the dossier bound -- a "
                f"document longer than that bound is cut to its opening. The part "
                f"of the path above the folder you scanned stays on this machine. "
                f"Protected material, and any file not yet classified, is never "
                f"sent. Sending stays ON for this folder until you turn it off "
                f"with:",
                indent="  "), file=out)
        # SITE G, IN EVERY CONSENT-ON BRANCH AND NOT IN ONE OF THEM. `104` §18.2
        # gap 9: the site that decides whether a file may be sent belongs beside
        # the sentence about what is sent, whichever of the three branches above
        # wrote that sentence -- and it is placed HERE, after them and before the
        # command that turns sending off, so a person who reads only the last two
        # lines still reads it. Empty and silent where G has no local destination.
        if routing is not None:
            said = _situation_site_sentence(routing)
            if said:
                print(said, file=out)
        print(_turn_off_line(corpus_root, *other_sources), file=out)
        return
    if routing is None:
        # `model_route` has already said no model is configured. A second sentence
        # about consent would answer a question the person cannot yet be asking.
        return
    if _announced_locality(routing, A_FACT, consent) == LOCAL:
        # THE ONE SENTENCE A LOCAL MODEL CHANGES, and it has to change because
        # every other sentence in this branch says nothing will be asked. With a
        # model on this machine something IS asked, and a person reading "cloud
        # sending is off" would otherwise conclude that nothing was.
        #
        # It names the model, says where it is, and says the thing that makes the
        # difference matter: `00`:189-193's `offline` is "No content leaves the
        # device; only local rules and LOCAL MODELS may run", so this run asking a
        # model and this run sending nothing are both true at once, and a person
        # who cannot see that has been told the weaker half.
        #
        # "FULL" is the word `104` §18.7 makes load-bearing here, and it is the
        # asymmetry the ruling IS: the cloud is shown the folder path relative to
        # the folder that was scanned, this model is shown the whole of it. The
        # two sentences say different things because the product now does two
        # different things, and a notice that used one wording for both would
        # hide the half a person might care about most. Nothing leaves on this
        # branch, so the full path here is a statement of what one process on
        # this machine hands another -- which is why it can be said plainly.
        print(_wrapped(
            f"Model: {_local_model_id(routing, A_FACT)}, running on this device, "
            f"for facts -- what course, what school, what kind of document. It is "
            f"asked over loopback, no key is used, and NOTHING LEAVES YOUR "
            f"DEVICE; `{OPERATION_MODE}` is \"{MODE_SEMANTICS[OPERATION_MODE]}\", "
            f"and a local model is one of them. It is shown a file's name, the "
            f"full path of the folder it sits in and its text within the dossier "
            f"bound; protected material is shown to it and to no other model.",
            indent=""), file=out)
        # SITE G HERE TOO, for the reason it appears in the consent-ON branch.
        # `104` §18.2 gap 9. With sending off it is the same site doing the same
        # work -- G runs on every deployment that has a model on this machine,
        # whatever this folder's consent says -- and a person who reads it only on
        # the runs where sending is on has been told it is a thing about sending.
        said = _situation_site_sentence(routing)
        if said:
            print(said, file=out)
        elsewhere = tuple(sorted({
            routing.model_id_for(site) for site in (C_PLACEMENT, D_RESIDUAL)
            if routing.locality_for(site) != LOCAL}))
        if elsewhere:
            print(_wrapped(
                f"{' and '.join(elsewhere)} {'are' if len(elsewhere) > 1 else 'is'}"
                f" also configured and would be reached over the internet, but no "
                f"part of this run asks {'them' if len(elsewhere) > 1 else 'it'} "
                f"and cloud sending is off for this folder anyway. To turn sending "
                f"on for this folder, add --enable-cloud.", indent="  "), file=out)
        return
    print(f"\nModel: {routing.model_id_for(A_FACT)} for facts, "
          f"{routing.model_id_for(C_PLACEMENT)} for checks, "
          f"{routing.model_id_for(D_RESIDUAL)} for review sets.", file=out)
    # TWO independent reasons nothing is sent, and both are said. An earlier
    # version of this branch returned early when the call sites were unwired, and
    # in doing so dropped the entire consent explanation -- a person with sending
    # off lost the sentence saying so and the command that turns it on. That
    # traded one untruth for a worse silence. The wiring sentence is ADDED to the
    # consent one rather than replacing it, because a person who turns sending on
    # tomorrow needs to know that today's quiet had two causes and only one of
    # them was their choice.
    # WHAT TURNING IT ON WOULD DO. While nothing was wired this sentence could only
    # say "still nothing", and a notice that gives only the consent reason lets a
    # person believe turning it on tomorrow changes something about today. Now that
    # `A_fact` is wired the answer is a real one -- and it names the ONE question
    # that can be asked, because a person deciding needs the size of the thing they
    # would be turning on, not the number of models that happen to be configured.
    unwired = (
        f" If you turned it on, files whose fields this device could not settle "
        f"would be sent to {routing.model_id_for(A_FACT)} to be asked what course, "
        f"what school or what kind of document they are -- and to no other model: "
        f"the checks and the review sets are not wired to anything yet."
        if MODEL_CALL_SITES_WIRED else
        " No part of this run can call a model yet either, so turning "
        "sending on today would still send nothing.")
    print(_wrapped(
        f"None of them will be asked on this run. Cloud sending is off for this "
        f"folder, which is what happens by not choosing -- this run operates "
        f"under `{OPERATION_MODE}`, \"{MODE_SEMANTICS[OPERATION_MODE]}\" -- so a "
        f"file below that says a model was not cleared for it is saying that, and "
        f"nothing about itself. Nothing was sent and no key was used.{unwired} To "
        f"turn sending on for this folder, add --enable-cloud.",
        indent="  "), file=out)

#: P7's handling class for an ordinary file and for a protected area. The set is
#: P7's vocabulary; which one a node carries is a deployment decision, and the
#: protected one is deliberately the strongest so a marked container can never
#: inherit a weaker floor than its contents would require.
ORDINARY_CLASS: str = "personal_non_sensitive"
PROTECTED_CLASS: str = "highly_sensitive_credential_bearing"

#: EVERY class this deployment treats as protected, strongest first. P7 publishes
#: `HANDLING_CLASSES` as a set with no ordering and `protected` as a separate flag
#: it tells neighbours to consume rather than infer, so which classes carry the
#: flag HERE is this file's to state: the marked containers above, and
#: `sensitive_personal`, which is what `SAFETY_DOMAIN_HANDLING` gives finance,
#: identity, medical and legal material.
#:
#: Naming only the first left every safety-domain file looking ordinary to P10.
PROTECTED_CLASSES: frozenset[str] = frozenset(
    {PROTECTED_CLASS, "sensitive_personal"})
_PROTECTED_ORDER: tuple[str, ...] = (PROTECTED_CLASS, "sensitive_personal")

#: WHICH CLASS EACH RECOGNISED SCHEMA GETS. `71` cause B: the detector recognises
#: 23 schemas and `SAFETY_DOMAIN_HANDLING` names a class for FOUR of them, so a
#: file recognised perfectly from its own words came back
#: `unassigned_handling` -- "recognition is not classification" -- and the run
#: ended with everything unclassified and nothing filed.
#:
#: The four safety schemas keep exactly the handling they had, protected flag and
#: all: that map is P7's own and is imported rather than restated. The other
#: nineteen get `ORDINARY_CLASS`, which is the class THIS FILE already declares an
#: ordinary file to carry (it is what every tree node gets, two lines up).
#:
#: The basis is `detector` -- P7's closed vocabulary of three, and the honest one:
#: it IS the detector concluding, from terms the file itself carries. `safety_domain`
#: stays the basis of the four, because that is a different claim about a different
#: thing.
#:
#: `protected=False` for those nineteen is the decision here, and it is the
#: conservative one in the direction that matters. Marking coursework protected
#: would refuse to file it and would tell a person their homework is sensitive --
#: the over-protection `classifier` below records as a COLLAPSE: it "made an
#: unreadable scan and a passport identical in P7's store". Protection is still
#: decided by the safety schemas and by P3's container rule, neither of which this
#: widens.
HANDLING_POLICY: Mapping[str, Handling] = MappingProxyType({
    **{schema_id: Handling(handling_class=ORDINARY_CLASS, protected=False,
                           basis="detector")
       for schema_id in SCHEMA_IDS},
    **SAFETY_DOMAIN_HANDLING,
})

#: THE BASIS A PRECAUTION'S ROW CARRIES, derived from the policy that writes it
#: rather than spelled (`104` §18 gap 24). `privacy.vocabulary` publishes the five
#: bases as a tuple and names no constant for this one, and a literal here would
#: be a second home for a word `SAFETY_DOMAIN_HANDLING` already states four times.
#:
#: A SET, because `Handling` carries the basis PER SCHEMA and nothing says the four
#: safety domains must always agree on it. Reading whatever they actually say keeps
#: this true if one of them ever differs, and `in` is the same question either way.
SAFETY_DOMAIN_BASES: frozenset[str] = frozenset(
    handling.basis for handling in SAFETY_DOMAIN_HANDLING.values())

# --- RECOGNITION BY MEANING: every number the similarity path decides with -----
#
# `recognition/semantic.py` authors none of these and refuses to default one. They
# are all MEASURED on the 199-file ground-truth corpus under `.groundtruth/`, and
# the measurement is in `planning/97-SEMANTIC-RECOGNITION-MEASURED.md`.
#
# THE PATH IS OFF UNLESS `--semantic-model DIR` NAMES THE WEIGHTS. Absent means
# the product behaves exactly as it did before, which is the honest reading of
# "absent means refuse, never guess": a missing model is a feature that is off,
# not a number to invent.

#: P4 zones the vector is read from, in SPEC 2.2's ranking -- where a document
#: names itself first, so a truncation keeps the identifying half. `metadata` is
#: deliberately absent: measured over the owner's corpora it holds `Producer`,
#: `CreationDate` and `pixel dimensions`, the format talking about the software
#: that wrote it, and `HW 9.pdf`'s only authored term came out of it.
SEMANTIC_ZONES: tuple[str, ...] = (
    "filename", "title", "heading", "header_footer", "body", "table", "ocr")

#: How much of a file's own text is assembled. Matched to `SEMANTIC_MAX_TOKENS`
#: rather than chosen: 256 word-pieces is about a thousand characters, and a
#: budget larger than the model reads would put a number in the vector's SCOPE --
#: which is part of what the vector means -- that nothing was ever computed over.
SEMANTIC_CHAR_BUDGET: int = 1_000
SEMANTIC_MAX_TOKENS: int = 256
SEMANTIC_BATCH: int = 32
SEMANTIC_THREADS: int = 4

#: Anchors longer than this are dropped. 13.5% of the 8,925 compiled terms are
#: authoring prose -- one `government` row is a 77-word aside beginning "proposed
#: for r6, not design" -- and they were expected to be the RICHEST anchors, being
#: unmatchable as literal strings. Measured, they are the worst: dropping them
#: moves top-1 schema accuracy from 29.1% to 32.2%, because an editorial note is
#: generic English and pulls a schema's centroid toward the middle of the space.
SEMANTIC_MAX_ANCHOR_WORDS: int = 6

#: `never_alone` in the form a vector can state it. Mean pooling hides how much
#: text was pooled, so a vector over a filename looks exactly as confident as a
#: vector over four pages. This is the ONE rule that separates safe from unsafe
#: here: the only two hand-labelled protected files the path ever claimed as
#: ordinary carry 22 and 84 characters. At 100 it claims neither.
SEMANTIC_MIN_CHARS: int = 100

#: caution / release / margin. The caution line sits ABOVE the release floor
#: because they measure different things: `release` is how near the leader must
#: be, `caution` is how near ANY of `00`'s four safety domains may be before the
#: path falls silent.
#:
#: THERE IS NO PROTECT FLOOR AND THE ABSENCE IS THE FINDING. The four safety
#: domains do not separate: the eight hand-labelled protected files score
#: 0.084-0.151 and sit at the 43rd to 90th percentiles of the corpus, the highest
#: safety score of all 199 files belongs to a Red Cross first-aid certificate, and
#: an open-source `LICENSE` outranks the owner's own HKID card. No floor catches
#: the eight without protecting half the disk, which is the over-protection
#: collapse `classifier` below already records. So the vector neither protects nor
#: releases one of `00`'s four domains: near one, it says nothing.
SEMANTIC_FLOORS: SemanticFloors = SemanticFloors(
    caution=0.137, release=0.10, margin=0.01)

#: §1.1's root anchor -- the top of the tree the plan is written against.
ROOT_ANCHOR: str = "root_documents"


#: `00`:173's platform table. Every field is a fact about the filesystem this
#: build runs on, and none of them may be guessed inside a part package.
#:
#: `case_sensitive=False` on darwin is deliberate and is the field that can
#: destroy a file if it is wrong. APFS and HFS+ are case-INSENSITIVE by default,
#: so `Resume.pdf` and `resume.pdf` are one path; declaring the filesystem
#: case-sensitive would let `find_collision` decide there was no collision and
#: let the rename that follows overwrite the incumbent. The safe error is to see
#: a collision that is not there -- that stops and asks -- not to miss one.
_FILESYSTEM_CONSTRAINTS: FilesystemConstraints = FilesystemConstraints(
    unicode_form="NFC",
    case_sensitive=sys.platform not in ("darwin", "win32"),
    max_component_bytes=255,
    max_path_bytes=1024 if sys.platform == "darwin" else 4096,
    prohibited_characters=(frozenset({"/", "\0", ":"})
                           if sys.platform == "darwin"
                           else frozenset({"/", "\0"})),
    reserved_names=frozenset(),
    replacement_character="_")

#: **`74` §8 Q6, the half of it this build needs: the halt rule.** The batch
#: BOUND is not needed -- `apply_run` applies one plan at a time, which is
#: `00`:155's first option verbatim -- but a run of many plans still has to say
#: when it stops. Every stop before the move leaves the disk exactly as it was,
#: so a refusal, a staleness and a pause are reported and stepped past; a
#: `failed` is not, because it is the one result meaning something happened that
#: P12 could not confirm. THE OWNER'S TO CONFIRM; it is here, in one place.
_HALT_ON: frozenset[str] = frozenset({mv.FAILED})

#: **`74` §8 Q7 is open**, so a move crossing to another drive is not attempted:
#: `apply_plan` demands a disposition for a copy it cannot confirm BEFORE it
#: touches anything, and none has been ruled. This is the sentence the person
#: reads. It promises nothing about later, because nothing has been decided.
_CROSS_VOLUME_UNRULED_SENTENCE: str = (
    "This file would move to a different drive. Moving between drives means "
    "copying and then removing the original, and what happens to a copy that "
    "cannot be confirmed is not settled yet -- so nothing was copied and "
    "nothing was removed.")

#: `00`:170's expiration state. No expiry rule exists anywhere in the design, so
#: this says so rather than inventing a clock a pending move goes stale against.
_EXPIRATION_STATE: str = "no expiry configured"

#: The review this run's groups and acceptances belong to.
PLAN_VERSION: str = "plan_0"

#: P13's Open question 4, answered by the caller because the seam supplies no
#: default: a file with several extraction runs is reported by its WORST one, so
#: a file that failed once and succeeded once is not counted as read.
#: `tests/p13/test_p13_progress_lines.py` spells the same order and says in a
#: comment that it is "exactly as it will be spelled in `src/cli.py`".
WORST_FIRST: tuple[str, ...] = (
    "failed", "unreadable", "unsupported", "dataless", "metadata_only",
    "deferred", "capped", "partial", "complete")

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
#:
#: ONE separator was added on 2026-08-29, and no more: a single space or hyphen
#: between the letters and the digits, so that `PHYS 1401` and `PHYS-1401` read as
#: the identifier they are. `65` §2.1 is why -- the first run on a real folder
#: returned `NothingToDesign` because the files said `PHYS 1401` and the pattern
#: wanted `PHYS1401`. `63` §10 rules that this is a READING failure and is fixed by
#: reading better, never by asking the person: "No onboarding answer could have
#: recovered that course code."
#:
#: THE CASE OF THE LETTERS LEFT THIS PATTERN ON 2026-09-08, and `104` R-146 is the
#: measurement. Read with the uppercase-only shape
#: `\b[A-Z][A-Z0-9]*[ -]?[0-9]{3,}\b`, on this file's own strings:
#:
#:     'Physics 1401'         -> []                 'PHYS 1401'  -> ['PHYS 1401']
#:     'French 1101 syllabus' -> []                 'W3134'      -> ['W3134']
#:     'COMS W3134'           -> ['W3134']          'BUSIB 4300' -> ['BUSIB 4300']
#:
#: A syllabus that prints its course as a capitalised WORD and a number was invisible
#: -- no reading, so no observation, so nothing for §3.5's rule to test and nothing
#: for the anchor pass to find. R-146, measured on the owner's corpus in shapes only:
#: of 43 labelled files, the label's subject is stated by a recognised anchor in the
#: file's own folder family for NONE, and 9 of the model's 19 `subject` answers on
#: that run are a one-letter identifier naming something else, copied from a cited
#: neighbour because it was the only anchor sharing the digits.
#:
#: **A DEPARTMENT IS WHATEVER WORD THE DOCUMENT PRINTS BEFORE ITS NUMBER.** No word
#: list decides this and none may: the constitution's first rule is that code
#: delivers candidates and the model judges, and a list of department names would be
#: this file answering "which words are departments" -- the question the model is
#: asked. So the letters may be title case, and the second alternative below reads a
#: department WORD followed by a section letter glued to the digits, which is the
#: reading `COMS W3134` was cut in half by.
#:
#: **THE SECOND ALTERNATIVE'S SECOND TOKEN IS ONE LETTER, AND THAT IS THE WHOLE
#: RESTRAINT ON IT.** `[A-Z][A-Za-z]*[ -][A-Z][0-9]{3,}` -- a word, a separator, ONE
#: capital, the digits. The reasoning is `_SUBJECT_IDENTIFIER`'s own, below: a
#: one-letter glued token is a FRAGMENT (`E1006` is the tail of `ENGI E1006`), so the
#: capitalised word in front of it completes a reading this deployment was already
#: making badly; a multi-letter glued token (`PHYS1401`, `ELTU3017`) is already
#: whole, so the word in front of it is prose. Measured both ways before choosing:
#: with a multi-letter second token, `Homework PHYS1401` reads as one identifier and
#: `Syllabus ELTU3017` as another -- and `canonical` keeps those spaces (`_SEPARATOR`
#: wants a capital before the space and a digit after), so `PHYS1401` and
#: `Homework PHYS1401` would arrive at P6 as TWO identities, which is `65` §4.2's
#: recorded failure exactly. With one letter: `Homework PHYS1401` -> `PHYS1401`,
#: `Syllabus ELTU3017` -> `ELTU3017`, `COMS W3134` -> `COMS W3134`,
#: `ENGI E1006` -> `ENGI E1006`.
#:
#: **WHAT IT NOW READS OUT OF ORDINARY PROSE, DECIDED CASE BY CASE AND NOT REGRETTED.**
#: `Chapter 101`, `Room 1234`, `The 2026`, `Room B101` and `March 2026` are all
#: candidate readings now, and `page 12345` and `iPhone 12345` are not -- a lowercase
#: word is not a candidate (`\b` also refuses the `P` inside `iPhone`), a capitalised
#: one is. Nothing distinguishes `Chapter 101` from `Physics 1401` by SHAPE, and the
#: only thing that could tell them apart is a list of words, which is refused above.
#: So they are delivered and judged elsewhere: §3.5's rule refuses every one of them
#: unless a context term naming an act of teaching sits beside it, `_is_term` holds
#: the term readings off `subject`, and the model is the one asked which line names
#: the course. THE DATE CASE IS THE HONEST ONE: `14 March 2026` now reads
#: `March 2026`. It is not a new door -- `14 MARCH 2026` produced `MARCH 2026` under
#: the uppercase shape too -- so "not a reader of dates" was never true; it was true
#: only of months this deployment's own users happen not to shout.
#:
#: The digits must still be three or more and the separator is still at most one, so
#: a sum of money, a page number, a two-digit day and a sentence are all still
#: invisible to it.
_STRUCTURED = re.compile(
    r"\b(?:[A-Z][A-Za-z]*[ -][A-Z][0-9]{3,}|[A-Z][A-Za-z0-9]*[ -]?[0-9]{3,})\b")

#: THE SECOND DIMENSION, and §3.10's three named forms rather than one of them.
#: `00`:78's recommended tree is `Academics/Columbia/2026-Spring/PHYS1401/Homework`,
#: so a term is one of the four levels the design asks for by name -- and until
#: 2026-08-31 this deployment recognised only a season and a year. A person whose
#: university writes `AY 2024-25` or `Michaelmas Term 2024` got NO term folder, and
#: `AY 2024-25` was worse than nothing: `_STRUCTURED` claimed `AY 2024` and filed
#: their essays under a course called AY2024.
#:
#: The three sources are one each for §3.10's three worked cases. They are the
#: deployment's, like every other pattern in this file: `facts.dates` authors the
#: three IDS the design names and not one character of regex, because the date and
#: academic-term regex catalogue beyond those three is Deferred.
_SEASON = r"(?:Spring|Summer|Fall|Autumn|Winter)"
_TERM_NAME = r"(?:Michaelmas|Hilary|Trinity|Lent|Easter)"
#: A YEAR, not any four digits. `[0-9]{4}` matched the COURSE NUMBER in
#: `BUSIB 4300 Spring 2026` and, because the second alternative below reads
#: `<four digits> <season>`, the leftmost match was `4300 Spring` -- which then
#: CONSUMED the string so the correct `Spring 2026` after it was never seen. That
#: file was filed under a term of `Spring4300`, conflicted with its own subject of
#: `BUSIB4300`, and was never placed. It is not one file: `PHYS 1401 Fall 2023`
#: gives `Fall1401` and `ECON 4100 Fall 2025` gives `Fall4100` -- every academic
#: filename of the shape `CODE NNNN Season YYYY`, which is the commonest one there
#: is.
#:
#: `19|20` is this deployment's, like every other pattern in this block, and it is a
#: NARROWING of the four-digit run already chosen here rather than a new policy.
#: Measured before it was made: over 6,679 real observations it drops ZERO matches
#: and keeps all 44; over the 18-file live corpus it drops only `2926 Summer` and
#: `2548 Summer` -- two more course numbers -- and corrects `Spring4300` to
#: `Spring2026`. A term outside 1900-2099 is not a term this product will meet.
_YEAR = r"(?:19|20)[0-9]{2}"
_SEASON_YEAR_SOURCE = (
    rf"\b(?:{_SEASON}[ \-_]?{_YEAR}|{_YEAR}[ \-_]?{_SEASON})\b")
_ACADEMIC_YEAR_SOURCE = rf"\bAY[ \-_]?{_YEAR}[ ]?[-/][ ]?[0-9]{{2}}\b"
_NAMED_TERM_SOURCE = rf"\b{_TERM_NAME}(?:[ \-_]Term)?[ \-_]{_YEAR}\b"

#: THE TWO-TERM ACADEMIC YEAR'S OWN SPELLING, RULED IN BY THE OWNER ON 7 SEP 2026.
#: `105` §13.2 proposed them and §14.2 ruled "Keep the proposed accepted forms and
#: refusals". `104` R-101 is the measurement that asked for them: on the owner's
#: corpus, 114 `term` answers were refused `VALUE_NOT_NORMALIZABLE` and the single
#: commonest refused shape was `2023-2024 Term 1`, fifteen times. A person whose
#: university writes its calendar that way got no term folder at all.
#:
#: TWO SOURCES AND TWO IDS, NEVER ONE WITH THE WORD IN A GROUP. §14.2: "`Term 1` and
#: `Semester 1` are not automatically one value" and no equivalence is inferred
#: "between numbered terms, semesters, or seasons without evidence for that course's
#: calendar". One source with `(?:Term|Semester)` would still parse both, but it
#: would hand `date_matches` ONE pattern id for two calendars, and the id is what
#: `DateMatch` carries so a test can assert which pattern claimed the span.
#:
#: `[1-9]` and not `[0-9]+`: a term number is a small ordinal, and `Term 0` and
#: `Term 12` are not calendars anyone writes. The years are both `_YEAR` for the
#: reason `_YEAR` exists at all -- `[0-9]{4}` claimed the COURSE NUMBER in
#: `BUSIB 4300 Spring 2026` -- and the separator is `[-/]` because that is what
#: `_ACADEMIC_YEAR_SOURCE` already accepts between the halves of an academic year.
#:
#: NOT WIDENED BEYOND THE RULING. `Semester 1 2023-2024` (reversed), `2023-24 Term 1`
#: (a two-digit second half) and a check that the two years are consecutive are all
#: absent on purpose: the owner ruled on two forms, and a fourth spelling admitted
#: here would be this file adding to a vocabulary the owner closed.
_TERM_NUMBER_SOURCE = rf"\b{_YEAR}[ ]?[-/][ ]?{_YEAR}[ \-_]Term[ \-_]?[1-9]\b"
_SEMESTER_NUMBER_SOURCE = rf"\b{_YEAR}[ ]?[-/][ ]?{_YEAR}[ \-_]Semester[ \-_]?[1-9]\b"

#: THE ORDER OF THE FIVE IS NOT LOAD-BEARING, AND THAT IS WORTH STATING because
#: alternation order usually is. No two of these can claim overlapping text: the
#: three older sources each require a word the numbered forms do not contain -- a
#: season, the letters `AY`, or one of the five term names -- and the numbered forms
#: require two four-digit years in front of `Term` or `Semester`, which none of the
#: three can supply. `test_p6_term_forms` asserts it rather than resting on this
#: paragraph: every ruled form is claimed by EXACTLY ONE pattern of the catalogue.
#: The two new sources lead because they are the two the owner ruled in.
_TERM = re.compile("|".join(
    (_TERM_NUMBER_SOURCE, _SEMESTER_NUMBER_SOURCE,
     _SEASON_YEAR_SOURCE, _ACADEMIC_YEAR_SOURCE, _NAMED_TERM_SOURCE)),
    re.IGNORECASE)


def _is_term(raw: str) -> bool:
    """Whether a reading is a term rather than an identifier.

    Asked of the READING, which is the only place the two can be told apart: they
    sit in the same body text and share every locator prefix. It survives the
    removal of the term DIRECT slot below, because its job here is the other one --
    keeping the `subject` slot off a term.
    """
    return _TERM.fullmatch(raw.strip()) is not None


def _is_an_identifier(raw: str) -> bool:
    """Whether a reading is one of the things `_STRUCTURED` above describes.

    **This is the refusal the `subject` slot did not have, and the measurement that
    demanded it.** 54 files of the owner's real Downloads, run `academic.coursework`:
    the catalogue declares 56 fields, two ever took a value, and `subject` took 196
    DISTINCT values across 18 files -- eleven "subjects" per document. They were `!`,
    `&`, `-`, `(i)`, `* DIEI ==outcomes in E` and `#corre 1 . 4 - 1 : 4 . 10 - 4`. A
    probability lecture reported punctuation as what it is about.

    **They arrived because one stated invariant is false for one emitter.**
    `reads_a_structured_string` below admits a `body`/`heading` locator carrying a
    span, and rests that bound on "a structured string always carries a span because
    it is a substring the pass located; a whole zone never does". In `extract_pdf`,
    the heading-REGION candidate is emitted with an explicit
    `span={"start": 0, "end": len(heading_text)}` -- so a whole heading is addressed
    exactly like a located substring, while the whole-page candidate beside it takes
    `span=None` and is not. All 158 heading-zone observations in that run were whole
    regions. That is P4's shape and not this file's to change; what this file can do
    is stop claiming them.

    **It is a predicate over the READING, not the locator, because the locator cannot
    answer it.** `extract_pdf`'s `find_structured_strings` loop gives an identifier
    found INSIDE a heading the heading's own zone (`ZONE_BY_STRUCTURED_KIND` names
    none for an `identifier` and the fallback is the region's), so `PHYS 1401` in a
    slide title is `heading:page=1/heading=3#9-18` -- `00`:78's own worked tree.
    Narrowing `_TEXT_ZONES` would have cleaned the noise and thrown that away with it.

    **Nothing is authored here.** The slot is `cli.text.identifier`; this deployment
    already spells what an identifier is, once, in `_STRUCTURED`, and a located
    structured string's raw value IS its match -- that same loop slices it out of the
    unit as `raw = unit_text[start:end]`. So the test is the pattern the reading would
    have had to satisfy to be produced by the pass the slot claims to read. Whitespace
    is collapsed first, for the same reason the canonicaliser collapses it:
    `PHYS  1401` off a two-column page is one identifier.

    **Every citation above names a symbol and not a line.** All four were
    `extractors/pdf.py:NNN` until 2026-09-04 and all four had moved -- `:143` had
    come to point at a comment about the recogniser, not at the page candidate it
    claimed. Commit 90aadd6 is about exactly this: a line number is a citation that
    decays, and a docstring that cites one is wrong on a schedule nobody is watching.
    """
    return _STRUCTURED.fullmatch(" ".join(raw.split())) is not None


#: ONE VALUE PER TERM, WHATEVER IT WAS WRITTEN AS. `Spring 2026`, `Spring2026` and
#: `2026-Spring` are one semester, and a semester that reaches §3.7 as several
#: values reaches it as several candidates, which tie, which the margin refuses.
#: Measured 2026-08-31: on the `direct` path there is no margin at all, so
#: `Spring 2025` and `2025-Spring` in one corpus proposed the folders `Spring2025`
#: AND `2025Spring`. Order is a spelling, not a fact.
#:
#: Every token that DISTINGUISHES two terms is kept and nothing else is: the season
#: or the term's name, and the year or the year range. Only case, separators and the
#: written order are dropped.
#:
#: **`Term` IS DROPPED FROM `Michaelmas Term 2024` AND KEPT IN `2023-2024 Term 1`,
#: AND THAT IS NOT AN INCONSISTENCY.** In `Michaelmas Term 2024` the word carries
#: nothing: `Michaelmas` already names the term and `Michaelmas 2024` is the same
#: calendar written shorter. In `2023-2024 Term 1` the word is the ONLY thing that
#: says which calendar the number counts in, and `105` §14.2 makes that identity:
#: "`Term 1` and `Semester 1` are not automatically one value". Drop it there and
#: two universities on different calendars share a folder on the strength of an
#: ordinal. So the four canonicalisers below keep exactly what tells two terms
#: apart, which for the numbered forms includes the word.
def _canonical_season_year(raw: str) -> str:
    season = re.search(_SEASON, raw, re.IGNORECASE).group(0)
    return f"{season.capitalize()}{re.search(r'[0-9]{4}', raw).group(0)}"


def _canonical_academic_year(raw: str) -> str:
    match = re.search(r"([0-9]{4})[^0-9]+([0-9]{2})", raw)
    return f"AY{match.group(1)}-{match.group(2)}"


def _canonical_named_term(raw: str) -> str:
    name = re.search(_TERM_NAME, raw, re.IGNORECASE).group(0)
    return f"{name.capitalize()}{re.search(r'[0-9]{4}', raw).group(0)}"


def _canonical_year_range_number(raw: str, *, word: str) -> str:
    """`2023-2024 Term 1` and `2023 / 2024 term-1` are one value; `Semester 1` is not.

    The word is passed in rather than read out of the text, because the two forms
    are two PATTERNS with two ids and each one already knows which it is. Reading it
    back out would be the generic parsing §3.10 forbids, one step downstream of the
    pattern that decided.

    THE NUMBER IS THE ONE THE WORD INTRODUCES, and it is found through the word for
    that reason. `[0-9](?![0-9])` -- the first digit with no digit after it -- reads
    `2023-2024 Term 1` as `Term 3`, because `2023` ends in a lone `3`. Anchoring on
    the word is the only reading that cannot be fooled by a year's own last digit.
    """
    years = re.findall(_YEAR, raw)
    number = re.search(rf"{word}[ \-_]?([1-9])", raw, re.IGNORECASE).group(1)
    return f"{years[0]}-{years[1]}{word}{number}"


def _canonical_year_range_term(raw: str) -> str:
    return _canonical_year_range_number(raw, word="Term")


def _canonical_year_range_semester(raw: str) -> str:
    return _canonical_year_range_number(raw, word="Semester")


DATE_PATTERNS = DatePatterns(patterns=(
    DatePattern(pattern_id=SEASON_YEAR,
                pattern=re.compile(_SEASON_YEAR_SOURCE, re.IGNORECASE),
                canonical=_canonical_season_year),
    DatePattern(pattern_id=ACADEMIC_YEAR_RANGE,
                pattern=re.compile(_ACADEMIC_YEAR_SOURCE, re.IGNORECASE),
                canonical=_canonical_academic_year),
    DatePattern(pattern_id=NAMED_TERM_YEAR,
                pattern=re.compile(_NAMED_TERM_SOURCE, re.IGNORECASE),
                canonical=_canonical_named_term),
    # `105` §14.2's two additions. Their ids are `facts.dates`', their expressions
    # and canonical forms are this deployment's, exactly as the three above.
    DatePattern(pattern_id=YEAR_RANGE_TERM_NUMBER,
                pattern=re.compile(_TERM_NUMBER_SOURCE, re.IGNORECASE),
                canonical=_canonical_year_range_term),
    DatePattern(pattern_id=YEAR_RANGE_SEMESTER_NUMBER,
                pattern=re.compile(_SEMESTER_NUMBER_SOURCE, re.IGNORECASE),
                canonical=_canonical_year_range_semester),
))

#: THE THREE SHAPES THE OWNER REFUSED, NAMED SO A REFUSAL CAN SAY WHICH.
#: `105` §13.2 stated them and §14.2 kept them: a bare year (`2019`), a bare range
#: with no term word (`2023-2024`), and a season initial with a year (`S2026`, which
#: is Spring or Summer and there is no way to tell). All three were already refused
#: by not matching any pattern; what they did not have was a NAME, and §13.2 asks for
#: them "stated so the validator's reason names them".
#:
#: **THE NAME REACHES THE DEPLOYMENT AND NOT THE P8 VERDICT, AND THAT IS THE HONEST
#: LIMIT.** `P8Verdict.reasons` is checked against `llm_harness.vocabulary`'s closed
#: `ALL_REASON_CODES`, so a fourth reason code would be a new member of a vocabulary
#: this ruling did not open. The outcome on the wire is `VALUE_NOT_NORMALIZABLE`
#: exactly as before; `term_refusal` below is what says which of the three shapes
#: earned it, and it is asked directly by this deployment's own tests.
#:
#: THE FIRST TWO USE `_YEAR` AND NOT `[0-9]{4}`, for the reason `_YEAR` exists:
#: `4300` is a course number, not a year, and calling it a refused bare year would
#: name the wrong defect for a value that was never a term candidate.
TERM_REFUSAL_BARE_YEAR = "bare_year"
TERM_REFUSAL_BARE_RANGE = "bare_range"
TERM_REFUSAL_SEASON_INITIAL = "season_initial"

_TERM_REFUSALS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (TERM_REFUSAL_BARE_YEAR, re.compile(rf"{_YEAR}\Z")),
    (TERM_REFUSAL_BARE_RANGE,
     re.compile(rf"{_YEAR}[ ]?[-/][ ]?(?:{_YEAR}|[0-9]{{2}})\Z")),
    (TERM_REFUSAL_SEASON_INITIAL,
     re.compile(rf"[SFWA][ \-_]?{_YEAR}\Z", re.IGNORECASE)),
)


def term_refusal(text: str) -> str | None:
    """Which refused shape this value is, or `None` if it is not one of the three.

    A YEAR IS NOT A TERM. `2019` says which year a document is from and says nothing
    about which semester's work it is, and a folder called `2019` beside `Fall2019`
    and `Spring2019` is a fourth folder holding the files the other two could not
    claim. `2023-2024` is the same refusal with the range's shape: it is an academic
    YEAR, and §14.2 rules that "`AY 2024-25` does not identify a semester" -- so a
    range that does not even carry the `AY` marker certainly does not.
    `S2026` is refused because it is genuinely two answers: five of the owner's 114
    refused values were `S2026`, and Spring and Summer are different semesters.
    `[SFWA]` and not `S` alone: the refusal is that an INITIAL is not a season word,
    and `F2026` and `W2026` are refused by every pattern above for the same reason
    `S2026` is. Naming only the ambiguous one would leave the other three refused
    with no name, which is the state this constant exists to end. Nothing is admitted
    by widening a refusal.

    Asked of the whole value, never of a span. A document that PRINTS `2019` in a
    sentence is not proposing it as a term; this is the model's answer to "what term
    is this", and the shapes above are answers that name something else.
    """
    for name, pattern in _TERM_REFUSALS:
        if pattern.fullmatch(text) is not None:
            return name
    return None


#: The field §3.10's producer fills. Spelled once, because `_rule_stage` and
#: `normalize_for_model` both need it and neither may re-spell it. (The third
#: caller was P9's `active_schema_for`, retired with `104` R-09.)
TERM_FIELD = "term"

#: The same identifier, however it was printed. `PHYS 1401`, `PHYS-1401` and
#: `PHYS1401` are one course code and must reach P6 as ONE value: `65` §4.2 records
#: what happens when one identity arrives as several -- four files from one course
#: became four one-file groups carrying the same label, and the course folder was
#: proposed and left empty.
_SEPARATOR = re.compile(r"(?<=[A-Z])[ -](?=[0-9])")

#: Zones whose readings are the document's own words. `title`, `filename`, `path`
#: and `metadata:*` are deliberately outside it: §3.5's slot names a LOCATION, and
#: these four are things said ABOUT a file rather than in it.
#:
#: **`ocr` IS DELIBERATELY NOT HERE, and adding it is the tempting fix that must
#: stay refused.** `direct_facts` writes `reliability_state=DIRECT_STATE`
#: unconditionally -- §3.5's slot names a location and applies no test to the
#: reading's reliability -- so an OCR region reaching a slot would turn a `possible`
#: RECOGNITION into a `direct` FACT, which §3.6's `PROPOSAL_ELIGIBLE_STATES` exists
#: to stop and which would put a scanner's guess straight onto a folder. A PDF text
#: layer is a different thing: `body:page=1#62-72` is extracted text, not a
#: recognition, and it is what this filter was always meant to admit. What promotes
#: an OCR reading is a validation stage, a model, or the person -- never the zone
#: list.
_TEXT_ZONES: tuple[str, ...] = ("body", "heading")


def reads_a_structured_string(locator: str) -> bool:
    """Whether a direct slot may take this reading: A SPAN, INSIDE A TEXT ZONE.

    **This replaced `locator.startswith(("body#", "heading"))`, which starved the
    whole fact layer.** A locator is `zone[":" container][# span]`
    (`evidence_shape/locator.py:134`), so a span inside a container reads
    `body:page=1#62-72` and does NOT start with `body#`. Every PDF page and every
    OCR region is addressed that way -- they are P4's own two worked examples at
    `tests/p4/test_p4_locator.py:34-35`, §2.2's page-eighteen reference and §2.8's
    OCR region. Measured on a 26-file corpus: 229 observations, 2 reached the slots,
    and both were `.docx` headings. A person's PDFs and scans were read, stored, and
    never seen by the fact layer.

    **The span requirement is the bound, and it is why widening is safe.** Widening
    by zone prefix alone also admits `body:page=1` -- the WHOLE PAGE -- and `title`,
    the whole document title. That is measured too: it produced a proposed folder
    named `Fudan application checklist [x] transcript [x] personal statement [ ]
    recommendation [ ] HSK certificate`. A structured string always carries a span
    because it is a substring the pass located; a whole zone never does. So the same
    predicate that lets a scan reach `subject` forbids a page from becoming one, and
    §3.6's check 3 is not asked to do a job §3.5 can do at the slot.
    """
    zone = locator.split(":", 1)[0].split("#", 1)[0]
    return zone in _TEXT_ZONES and "#" in locator

#: The field §3.5's rule fills, spelled once beside `TERM_FIELD` for the same
#: reason: two callers need it and neither may re-spell it.
SUBJECT_FIELD = "subject"

#: `_STRUCTURED`, ANCHORED TO THE WHOLE READING AND HELD OFF A TERM. The pattern
#: §3.5's `subject` rule matches, and the only regex in this file that is built from
#: another rather than written out -- there is still exactly ONE spelling of what an
#: identifier is, and this adds two refusals to it and no new shape.
#:
#: **The anchors replace a gate the rule does not have.** `facts.rules.apply_rules`
#: SEARCHES `observation.raw_value`; the slot it replaces matched the LOCATOR, and
#: `reads_a_structured_string` above kept whole pages out by refusing a span-less
#: one. A rule sees no locator, so a whole page carrying `PHYS 1401` somewhere in it
#: would match -- which is the reading that produced a proposed folder named "Fudan
#: application checklist [x] transcript [x] personal statement [ ] recommendation [ ]
#: HSK certificate". Anchoring costs nothing real: a located structured string's raw
#: value IS its match, because `find_structured_strings` slices it out of the unit,
#: and `_STRUCTURED` admits at most one separator so a match never holds two spaces.
#: Simulated over the owner's 6,679 observations before the change: bare `search`
#: writes 214 `context_check_failed` rows against the anchored pattern's 93, and the
#: two produce THE SAME FIVE FACTS. The 121 rows are pages, not identifiers. The
#: shipped run then wrote 158 refusal rows over 51 files -- 89 `context_truncated`,
#: 69 `context_check_failed`.
#:
#: **THE SECOND LOOKAHEAD REFUSES A CONCATENATION ACROSS A SPACE.** A capital and a
#: SECOND letter, OR one capital GLUED TO A DIGIT -- and the difference between those
#: two is the whole rule, so it is worth saying what it is about rather than what it
#: matches. (It read `[A-Z]{2}|[A-Z][0-9]` until `104` R-146 let `_STRUCTURED` read a
#: title-case word; `[A-Z][A-Za-z0-9]` is the same sentence over the wider shape, and
#: the refusal it exists for -- a ONE-letter word before a number -- is untouched:
#: `I 1403`, `A 2150`, `B 4100`, `A 9999` and `A-2150` are all still refused here,
#: while `Ph`ysics, `CO`MS, `E1`006 and `W3`134 are all admitted.)
#:
#: `_STRUCTURED` admits one optional separator. When that separator is PRESENT, the
#: letters before it are a standalone word of the running text, and a one-letter word
#: before a number is not a department -- it is a roman numeral or a list marker that
#: the pattern then glues onto the number beside it. Byte-exact from the owner's disk:
#:
#:     General Chemistry I 1403        Dr. Beer
#:     Sample Exam 1 - No. 2
#:
#: `I 1403` is "General Chemistry **I**" plus "1403" concatenated across the space,
#: and the product filed three of the owner's chemistry exams under a course called
#: `I1403`. The same shape claims `Music Theory A 2150` and `Organic Chemistry B
#: 4100`; the refusal is about the trailing capital of a COURSE TITLE, not about one
#: document, and `TRUNCATIONS` in `tests/p6/test_p6_subject_rule.py` holds all three.
#:
#: **WHEN THERE IS NO SEPARATOR THE READING IS ONE TOKEN AND IT STAYS.** `E1006` in
#: `# ENGI E1006: Introduction to Computing` is a single word that nothing else in
#: the sentence claims -- Columbia's own spelling, where the school letter leads the
#: number. On a glued reading the choice here is the token or nothing, and MEASURED
#: it is worth keeping: the five notebooks of that course match their own folder on
#: it, and refusing it took `right parent` from 6 to 2 and `not placed` from 73.2% to
#: 82.9% over the ground-truth corpus while removing no value the labels call correct.
#:
#: **THIS PARAGRAPH SAID THE TRUNCATION "CANNOT BE REPAIRED" AND THAT STOPPED BEING
#: TRUE ON 2026-09-08.** The reasoning was `apply_rules` searches
#: `observation.raw_value`, which P4 had already cut down to `E1006` because the
#: RECOGNISER cut it there, so `ENGI` survived only in `context_before` and no rule
#: could reach it. `104` R-146 moved the cut: `_STRUCTURED`'s second alternative reads
#: a word before a one-letter glued token, so `# ENGI E1006: Introduction to
#: Computing` now yields the reading `ENGI E1006` and this pattern admits it whole.
#: The repair is the RECOGNISER's and nothing here changed to make it: no rule was
#: widened, no canonicaliser was taught a spelling (`104` R-147 is the owner's ruling
#: on that and it is not made here), and `canonical("ENGI E1006")` is `ENGI E1006` --
#: `_SEPARATOR` wants a digit after the space and finds `E`. A document that prints
#: only `E1006` still yields only `E1006`, which is what the corpus test fixtures do.
#:
#: THE LABELS DISAGREE WITH BOTH READINGS AND THAT IS RECORDED, NOT RESOLVED. They
#: want `PYTHON1006` -- the person's own FOLDER name, which appears in the corpus 22
#: times but only in `path` and `filename` zones, never in a form this shape reads --
#: and `PHYS1403` for a document that is plainly General Chemistry. Reaching either
#: is a producer this file does not have; inventing one to match a label is not a fix.
#:
#: IT CANNOT BE EXPRESSED BY TIGHTENING `_STRUCTURED`, AND THAT IS DELIBERATE TWICE
#: OVER. The shape's letter run lets digits into its own "prefix" -- `E1006` matches
#: as `E` + `1` + `006` -- so the shape has no notion of a letter RUN to
#: tighten. And `_STRUCTURED` is what the product SEES: it feeds P4's extraction and
#: `recognition`'s identifier observations, and narrowing it there would silently
#: stop the product reading an identifier it has always read.
#: `tests/p6/test_p6_subject_rule.py` states that separation as an invariant -- what
#: the product sees and what it ASSERTS are two knobs, and only the second one moves
#: here.
#:
#: **The other lookahead is `not _is_term`, which `Rule` has no other place to keep.**
#: `DirectSlot` carries a `matches` predicate over the reading and `Rule` carries a
#: pattern, a context list and a field -- so the term refusal, which the slot held,
#: has to move into the pattern or be lost. Losing it re-arms the incident recorded
#: above: `AY 2024-25` claimed as `AY2024` and a person's essays filed under a course
#: by that name. `SPRING 2026` beside the word `semester` is precisely the reading
#: that would otherwise walk through the context check.
_SUBJECT_IDENTIFIER = re.compile(
    rf"\A\s*(?=[A-Z][A-Za-z0-9])(?!(?i:{_TERM.pattern})\s*\Z)"
    rf"(?:{_STRUCTURED.pattern})\s*\Z")

#: §3.5's rule for `subject`, quoted: *"Rules create validated facts when a candidate
#: passes strict context checks. For example, BUSIB 4300 becomes a course fact only
#: when the engine finds a course-code pattern together with academic context such as
#: 'syllabus,' 'lecture,' 'credits,' 'instructor,' or 'semester.'"*
#:
#: **This replaced the `cli.text.identifier` DIRECT slot, and the measurement is why.**
#: 199 of the owner's real files, `academic.coursework`, no model: `subject` was
#: **0 correct and 14 wrong** against the hand-made labels -- every value it produced
#: on a labelled file was false -- and its two commonest values on this person's disk
#: were the postal codes `NY 11794` and `MD 20852`, eight files each. Beside them:
#: a Keyence `VHX-7000` microscope, a United booking reference `UARF470911`, `U238`
#: out of a physics exam, `BOEING 777` out of a flight itinerary, and `USA 107` out
#: of `Proc. Natl. Acad. Sci. USA 107, 4335-4340`.
#:
#: **A slot was the wrong home, whatever the pattern.** §3.5's direct slot "names a
#: LOCATION and applies no test to the reading's reliability", and `direct_facts`
#: writes `DIRECT_STATE` unconditionally -- so a regex over body text, which is a
#: JUDGEMENT and not a location, arrived at the one reliability §3.6 ranks above
#: everything a model can propose. A ZIP code outranked the right answer about the
#: same file. Narrowing the shape does not fix that and was measured not to fix the
#: values either (`99` §4: 61 distinct values become 26, of which ONE is a course; it
#: drops the real courses `E1006` and `I1403` and keeps every flight number).
#:
#: **The sentence encoder was measured here and rejected.** The neighbourhood of
#: every candidate in that run was embedded with the shipped MiniLM weights and
#: scored against course-language prototypes: `MD20852` scores 0.296 and outranks
#: BOTH real courses, `I1403` at 0.266 and `E1006` at 0.193. These documents genuinely
#: ARE academic -- the affiliation block carrying the ZIP code is full of universities
#: and departments -- so topic similarity answers "is this an academic document" and
#: the question is "is this token the course".
#:
#: **Nothing is authored here that this deployment did not already own.** The terms
#: are `facts.rules.ACADEMIC_CONTEXT_TERMS`, which is §3.5's own five words quoted in
#: the design and refused a sixth by that module; the pattern is `_STRUCTURED` above;
#: the canonicaliser is the slot's, unchanged, because `PHYS 1401` and `PHYS1401` are
#: one course and `65` §4.2 records what happens when one identity arrives as two.
#: There is no threshold, no weight and no cutoff -- this producer takes no number.
#: §3.5's five terms PLUS this deployment's, and the deployment's are the ones that
#: make the rule usable. `facts.rules` authors the five the design states literally
#: and refuses a sixth by name -- "adding one is a design change, not an
#: implementation detail" -- and says where the rest come from: "Every other domain's
#: terms arrive on the `Rule`, because the SPEC defers them." This is that arrival.
#: The five are a SUBSET, so nothing that used to fill stops filling.
#:
#: **The five alone were measured and they are not enough.** Over the owner's 199
#: files they admit ONE course, `E1006`, on 5 files. The corpus contains two more
#: real courses and neither prints any of the five words anywhere near itself:
#: `I 1403` sits in "General Chemistry I 1403  Dr. Beer / Sample Exam 2", and
#: `ELTU3017` in a citation ending "eltu.cuhk.edu.hk/courses/eltu3017/". Silencing
#: them is not free: measured end to end, it costs four of the five working
#: placements and takes not-placed from 85.4% to 97.6%. A producer that refuses
#: everything scores better on wrong-fields and makes the product worse.
#:
#: **THE ONE RULING THAT SHAPES THIS LIST: an institution is not an act of teaching.**
#: Every postal code in `99` §3 -- `NY11794`, `MD20852`, `MA01003`, `IN46256`,
#: `NY10172`, `CA94588`, `MA01923` -- sits in an author-affiliation block, and an
#: affiliation block is the densest academic prose in the corpus: universities,
#: faculties, departments, institutes, medical centres. A list built from what makes
#: a document ACADEMIC admits every one of them. That is also, exactly, why the
#: sentence encoder failed here: it answers "is this an academic document", and these
#: documents are. So `university`, `school`, `faculty`, `department` and `institute`
#: are deliberately absent, and every term below names TEACHING or BEING TAUGHT.
#:
#: **The second exclusion: a word whose commonest sense is not academic.** `grade`
#: (a school year, a slope, a quality), `quarter` (fiscal), `term` (terms and
#: conditions), `class` (class action), `credit` singular (a credit card),
#: `transcript` (seven schemas author it) and `dr` (a title) are all out. This one is
#: honestly reported: the principle is real, but it was PROMPTED by measurement --
#: an earlier draft carrying `grade` and `quarter` admitted exactly two false
#: positives out of 101 candidate values, `MD20852` off the owner's school
#: transcript and `RATE2018` off a financial table. Both are held shut by
#: `tests/p6/test_p6_subject_rule.py` so the words cannot come back unnoticed.
#:
#: **Measured on the whole corpus with the list below: 3 of 3 real courses kept
#: across 11 files, and 0 false positives out of 101 candidate values.** That zero
#: is an IN-SAMPLE number on the corpus the exclusions were drawn from; the general
#: claim it supports is only that teaching words and institution words separate, and
#: `99` §4 records that this remains the owner's vocabulary to ratify.
SUBJECT_CONTEXT_TERMS: tuple[str, ...] = ACADEMIC_CONTEXT_TERMS + (
    "course", "courses", "coursework", "seminar", "tutorial", "recitation",
    "lectures", "prerequisite", "prerequisites", "professor", "lecturer",
    "homework", "assignment", "assignments", "problem set",
    "exam", "midterm", "quiz", "office hours", "enrolled in", "registrar")

SUBJECT_RULE = Rule(pattern=_SUBJECT_IDENTIFIER,
                    required_context_terms=SUBJECT_CONTEXT_TERMS,
                    field_key=SUBJECT_FIELD,
                    canonical=lambda raw: _SEPARATOR.sub("", " ".join(raw.split())))

#: `104` R-135 HAD A SECOND VOCABULARY HERE AND IT IS GONE, on the measurement.
#: `COURSE_ANCHOR_TERMS` was a strict subset of `SUBJECT_CONTEXT_TERMS` above --
#: `syllabus`, `registrar`, `enrolled in` -- asked of the text beside a course code so
#: that only a document STATING what a course is called became an anchor. The reasoning
#: read well: a homework sheet prints `W3134` beside `Problem Set 4`, and the syllabus
#: prints it beside the course's own name.
#:
#: Run against the owner's own corpus it refused everything. 9283 observations, 1554
#: read from inside a document, 106 passing the rule's own `is_code`, and all 106
#: refused by this gate; three files in the whole corpus mention any of these words
#: anywhere in their text, and not one of those prints a code. The document the premise
#: described is not in this corpus. What is in it is 44 files that print a course code
#: in their own text, and none of them could become evidence for any of the others.
#:
#: A gate that refuses 106 of 106 is not a narrowing, and choosing which lines name one
#: course is the model's job at sites A and C -- the constitution's first rule, and site
#: C's own sentence, "two spellings can be one thing ... yours to judge". So the list is
#: removed rather than widened: widening it would be authoring a better guess at the
#: same forbidden question. `SUBJECT_CONTEXT_TERMS` above is untouched; it answers a
#: different question for `SUBJECT_RULE` and still does.

#: §3.5's direct slot set, and §2.2/§2.3's suppression catalogue. `DirectSlots` has
#: no default because the slot is the caller's, and THIS DEPLOYMENT NOW SHIPS NONE.
#: That is a decision and not an omission: the one slot it had read a shape out of
#: body text and stated it `direct`, which `SUBJECT_RULE` above records in full, and
#: §3.5's own example of a direct fact is a filesystem timestamp, which does not
#: come through a slot. An empty set is honest -- `direct_facts` runs, claims
#: nothing, and the stage stays bound so a slot with a real location to name can be
#: added without re-deciding the composition.
#:
#: The `/Title` metadata slot §3.5 also names is deliberately absent for its own
#: reason: its observation carries no text span, P7's gate cannot release a span-less
#: excerpt, and a group anchored on it could never be reviewed.
DIRECT_SLOTS = DirectSlots(slots=())

#: THE TERM SLOT IS GONE, AND THE SPEC IS WHY. P6 SPEC:409-410: "Filesystem
#: timestamps are direct; dates recovered from text or filenames are not, and take
#: the §3.10 path." This slot read a date out of BODY TEXT and stated it `direct`,
#: which that sentence forbids by name. The term is now filled by `_rule_stage`,
#: `validated`, through the §3.10 path the SPEC points at.
#:
#: It could not be left beside the producer. `file_facts` has no uniqueness
#: constraint over (file_id, content_hash, field_key), so both would have written:
#: one file, two live `term` facts, two reliability states, two spellings, two term
#: folders.

METADATA_SCREEN = MetadataScreen(tool_producer_strings=(),
                                 metadata_property_names=())

#: §7.3 fixes nine residual template names and leaves their eight attribute slots
#: deferred. Until now this deployment shipped NONE rather than inventing slot
#: values, which was right while the values did not exist. They exist: the nine
#: are authored in full at `planning/deferred-catalogues/09-residual-library/
#: 01-nine-templates.json`, every value provenance-tagged, and `library/
#: residuals.json` is that file with its wrappers removed and its provenance
#: kept. Nothing is invented here and nothing is enabled here.
_RESIDUAL_SLOTS_FILE = (
    Path(__file__).resolve().parent / "tree_design" / "library" / "residuals.json")

#: The one slot the catalogue deliberately leaves unvalued: "`00` defines the
#: slot and states no number; every threshold in this product is injected." This
#: is the injection site, and the number is `RESEARCH.md` §4's recommendation --
#: zero for eight of the nine, and zero for Reference Clips too because its
#: optional clip-kind subfolders did not ship (NJ-R3-2: "if they are dropped, 0
#: there too"), which `residuals.json` confirms by carrying none.
#:
#: Zero means the home is flat. §7.3's homes are "safe, intentionally broad
#: destinations" and `00` holds that "an isolated file should normally remain
#: high in the tree because there is no evidence that it deserves a deep
#: project-specific path" -- so any depth inside a residual home would be
#: structure built without evidence, which is the second filing system this
#: design exists to avoid.
RESIDUAL_MAX_DEPTH: int = 0


def _residual_library() -> Mapping[str, ResidualTemplate]:
    """The nine, with this deployment's one injected number.

    Built, not enabled. §7.4: "These templates are not automatically created."
    Enabling one is `--residual`, and a run that names none gets none.
    """
    raw = json.loads(_RESIDUAL_SLOTS_FILE.read_text(encoding="utf-8"))
    slot_values = {
        name: dict(values, max_permitted_depth=RESIDUAL_MAX_DEPTH)
        for name, values in raw.items() if name in RESIDUAL_TEMPLATE_NAMES
    }
    return build_library(slot_values)

_RECOGNITION_MANIFEST = (
    Path(__file__).resolve().parent / "recognition" / "library" / "recognition.json")


class NotConfigured(RuntimeError):
    """The run was asked for something this deployment has not been given."""


#: Every way the chain refuses BY NAME. Caught in `main` and printed, because a
#: refusal with a reason is an answer and a traceback is not. Imported here rather
#: than caught as `Exception`: an unexpected error must still crash loudly.
REFUSALS: tuple[type[BaseException], ...] = (
    CompositionConflict, FreezeRefused, MaterialisationRefused, NothingToDesign,
    ProtectedSetNotReadable, ResidualSendRefused, ReviewActionRefused,
    UpstreamUnavailable,
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
    """Both patterns this deployment ships, as §2.2 `identifier` readings.

    ONE `kind` for both. §2.2's classes are "URLs, email addresses, DOI values,
    citations, identifiers" -- a closed list with no member for a term, and
    `ZONE_BY_STRUCTURED_KIND` maps a kind to a P4 ZONE. Inventing a kind here
    would be this file adding to P4's vocabulary, and calling a term a `citation`
    to borrow its zone would be worse. So both arrive as identifiers and
    `DIRECT_SLOTS` tells them apart by VALUE through `matches`.

    The term pattern runs FIRST and its spans are taken: `SPRING2026` matches both
    patterns, and two observations of one span would become two facts about one
    reading -- a term and a course code, from the same characters.

    **THAT ORDERING STOPPED BEING A PRECAUTION AND BECAME THE GUARD ON 2026-09-08.**
    `SPRING2026` was the only overlap worth naming while `_STRUCTURED` was uppercase-
    only: `Spring 2026` matched the term pattern and nothing else, because a title-
    case word was invisible to the identifier shape. `104` R-146 made that word
    visible, so the season spellings a person actually types -- `Spring 2026`,
    `Fall 2023`, `Winter 2024` -- now match BOTH patterns, and the only reason they
    are read as terms and not as courses is that `_TERM` runs first here and claims
    the characters. Measured after the widening: `PHYS 1401 Fall 2023` yields exactly
    two readings, `PHYS 1401` and `Fall 2023`, and `AY 2024-25` yields the one term
    (`_STRUCTURED` alone would have claimed `AY 2024` out of it, which is `65` §2.1's
    recorded incident). Swapping the two lines would file a person's essays under a
    course named after their semester.
    """
    found: list[StructuredString] = []
    taken: set[int] = set()
    for pattern in (_TERM, _STRUCTURED):
        for match in pattern.finditer(text):
            span = range(match.start(), match.end())
            if any(position in taken for position in span):
                continue
            taken.update(span)
            found.append(StructuredString(
                kind="identifier", start=match.start(), end=match.end()))
    return tuple(sorted(found, key=lambda one: one.start))


#: §3.11's universal format key. Named once, beside the one rule that canonicalises
#: it, because a second spelling of a field key is how a normalizer stops running.
FILE_TYPE_FIELD = "file_type"


def _canonical_file_type(text: str) -> str | None:
    """ONE vocabulary for `file_type`: the bare lowercase extension token.

    **The defect this closes, measured on a real run.** The same field, in the same
    run, took `.pdf` from one file, `application/pdf` from another and `.docx` from a
    third -- all three `llm_interpretation`, all three accepted, because a field with
    no direct slot reached this function and got whitespace collapsed and nothing
    else. Any folder level built on `file_type` would have split `.pdf` from
    `application/pdf` into two folders holding the same kind of file.

    **Why the extension token and not the MIME type**, which is a real choice:

    1. It is the product's OWN format vocabulary already. `extractors.router` keys
       `SOURCE_TYPE_BY_FORMAT` and `HANDLER_BY_FORMAT` on exactly these tokens
       (`"pdf"`, `"docx"`, `"png"`), and `_detect_format` above returns them. The MIME
       string is a second vocabulary, from `mimetypes`, that nothing routes on.
    2. **The MIME form cannot legally become a folder.** `application/pdf` contains
       `/`, and `tree_design.user_edits` refuses a display label holding a path
       separator -- "a renamed level is a display label, never a path fragment". A
       canonical form that the tree layer must reject is not a canonical form.
    3. `file_type` is a routing signal and not a meaning (the glossary's own words),
       so the shorter token loses nothing a person or a level needs.

    A MIME string is MAPPED rather than refused, through `mimetypes` -- a standard
    library table, not a vocabulary authored here. The model was RIGHT about the file
    type and wrong only about the spelling, and this function's whole promise is that
    one identity in several spellings becomes one value. What has no mapping returns
    `None`, which is check 3's ordinary `normalization_failed` refusal rather than a
    guess.
    """
    import mimetypes

    token = text.strip().lower()
    if "/" in token:
        guessed = mimetypes.guess_extension(token)
        if guessed is None:
            return None
        token = guessed
    token = token.lstrip(".")
    return token or None


def normalize_for_model(field_key: str, raw_value: str) -> str | None:
    """§3.6 check 3: "the proposed value can be normalized safely". `None` = it cannot.

    **This closes the C-5 deadlock, and where it closes it is the point.**
    `facts/llm_seam.py` records it: P8's SPEC names `normalize` and `contradicts`
    as P6's, P8's own Deferred table files them back to P6, "so each part hands
    them to the other and neither builds them... The ruling is owed." Neither part
    owns them because they are neither part's to own -- they are a DEPLOYMENT's
    answer, and this file is the only one in `src/` that answers those. A test
    already forbids any module in `facts` from publishing one, which is the same
    ruling seen from the other side.

    **Nothing is authored here.** The model's value is canonicalised by the SAME
    rule the deterministic slot uses for that field, so `PHYS 1401` proposed by a
    model and `PHYS1401` read from a heading cannot become two courses. That
    failure is on this project's record: `65` §4.2, four files of one course
    became four one-file groups because one identity arrived as several spellings.
    A second normaliser here would have re-created it across two stages instead of
    two files.

    A field with no slot gets whitespace collapsed and nothing else, because this
    deployment has authored no rule for it and inventing one at the model's
    boundary is exactly what §3.5 forbids ("not allowed to invent a new fact
    schema"). A value the field's own `matches` predicate rejects is NOT
    normalizable: a model proposing `Spring 2026` as a SUBJECT is proposing
    something the field's own rule says is not one, and returning a canonical form
    would launder it into a folder name.
    """
    if not isinstance(raw_value, str):
        return None
    text = " ".join(raw_value.split())
    if not text:
        return None
    slot = next((one for one in DIRECT_SLOTS.slots
                 if one.field_key == field_key), None)
    if slot is None:
        if field_key == FILE_TYPE_FIELD:
            return _canonical_file_type(text)
        if field_key == TERM_FIELD:
            # The term has no slot any more (SPEC:409-410) but it is still a filled
            # field, and this function's promise is that a model's value is
            # canonicalised by the SAME rule the deterministic path uses. Without
            # this, a model proposing `Spring 2026` would store `Spring 2026`
            # beside the producer's `Spring2026` -- the several-spellings failure,
            # re-created across the seam instead of inside one stage.
            #
            # THE NAMED REFUSALS ARE ASKED FIRST, and the order is what makes the
            # name true rather than decorative: after the pattern loop every value
            # that reaches `None` is indistinguishable, and `104` R-101 is a table of
            # 114 refusals nobody could sort. `term_refusal` runs on the whole value
            # and none of its three shapes is also an accepted form, so asking it
            # first admits nothing and refuses nothing new -- it only says WHICH.
            #
            # **AND `104` §18.2 GAP 3 CHANGED WHAT THE SECOND `None` MEANS.** A
            # value no pattern claims is no longer refused outright: it falls
            # through to `normalize_for_review`, which offers it to the person as
            # a term the catalogue has not seen. The FIRST `None` -- the three
            # shapes `term_refusal` names -- is refused there too, because those
            # are shapes the owner ruled against rather than shapes nobody has met
            # (`105` §14.2). The five patterns are now the seed, not the gate.
            refused = term_refusal(text)
            if refused is not None:
                return None
            claimed = next((one for one in DATE_PATTERNS.patterns
                            if one.pattern.fullmatch(text)), None)
            return None if claimed is None else claimed.canonical(text)
        if field_key == WORK_TYPE_FIELD:
            # `work_type` IS THE LIBRARY'S SEED AND HAD NO BRANCH HERE. Measured
            # on a cloud run with retrieval on: the rule wrote `lecture`,
            # `homework`, `exam` -- all members of the 942 terms the library ships
            # -- and the model wrote `.pdf`, `Proposed Scope` and
            # `GRC Proposed Scope V2.1`, none of them members. `.pdf` became a
            # folder: four files were placed into
            # `Coursework/Daniel Lacker/IEOR3658/.pdf`.
            #
            # This function's own promise already covers it -- "the model's value is
            # canonicalised by the SAME rule the deterministic slot uses for that
            # field", and "a value the field's own `matches` predicate rejects is
            # NOT normalizable". The rule for this field is membership, and nothing
            # is authored here: `WORK_TYPE_VOCABULARY` is the library's, and it is
            # the same object `kind_facts` reads.
            #
            # The LIBRARY's spelling is returned rather than the model's, for the
            # reason `KindVocabulary` states: that spelling becomes a folder name
            # and the document's casing must not.
            #
            # **WHAT THIS `None` MEANS CHANGED ON 2026-09-09 AND THE LOOKUP DID
            # NOT.** Until `104` §18.2 gap 3 a miss here ended the value's life at
            # `VALUE_NOT_NORMALIZABLE`; it now falls through to
            # `normalize_for_review`, which turns it into a proposal the person is
            # shown. So this line stopped being a gate and became what `00`:298
            # calls "the vocabulary the model is shown first" -- the seed the
            # review path starts from. The paragraph above still holds in every
            # word: `.pdf` must not become a folder, and it does not, because a
            # proposal is written `possible` and `PROPOSAL_ELIGIBLE_STATES` keeps
            # a `possible` fact out of every folder proposal until somebody says
            # yes.
            return WORK_TYPE_VOCABULARY.terms.get(kind_tokens(text))
        if field_key == SUBJECT_RULE.field_key:
            # AND NEITHER HAS `subject`, SINCE 2026-09-04. It moved from a slot to
            # `SUBJECT_RULE` above, and this branch is what stops that move from
            # re-opening the cloud path the deterministic path just shut. Without
            # it `subject` falls to `return text` below and EVERY value a model
            # proposes is normalizable -- `!`, `Spring 2026`, a whole heading --
            # which is the laundering this function's docstring forbids by name and
            # which `tests/p6/test_p6_subject_slot.py` asks about directly.
            #
            # The pattern is the rule's, not a second one: check 3 has to agree
            # with §3.5 or the two producers disagree about what a course is. Asked
            # of `text` rather than `raw_value` because the collapse above is the
            # same one the rule's canonicaliser applies, so `PHYS  1401` off a
            # two-column page is the one identifier it was before the move.
            if SUBJECT_RULE.pattern.search(text) is None:
                return None
            return SUBJECT_RULE.canonical(text) or None
        return text
    if slot.matches is not None and not slot.matches(raw_value):
        return None
    return slot.canonical(raw_value) or None


#: A TITLE'S SHAPE, AND IT IS THIS DEPLOYMENT'S, MEASURED RATHER THAN CHOSEN.
#: `105` §1.3-§1.4 record every course name the model produced on the bench --
#: `University Writing`, `AP World History`, `Introduction to Organic Chemistry`,
#: `Machine Learning`, `Thermodynamics`, `Rotational Dynamics` -- and the longest is
#: four words and 33 characters. Six words and 64 characters is that measurement with
#: room above it, and it is the bound `'a' * 300` fails: a value longer than any title
#: anyone has written is not a title somebody can be asked to confirm.
SUBJECT_TITLE_MAX_WORDS: int = 6
SUBJECT_TITLE_MAX_CHARACTERS: int = 64

#: WORDS, AND THE FOUR MARKS THAT APPEAR INSIDE REAL COURSE NAMES. Letters, digits,
#: single spaces, an apostrophe (`Women's History`), an ampersand (`Health & Society`)
#: and an internal hyphen (`Anglo-Saxon Verse`), beginning and ending on a letter or a
#: digit. Everything else is refused, and the refusals are the point rather than the
#: admissions: `report.pdf` carries a dot, `(i)` carries brackets, `#corre 1 . 4 - 1 :
#: 4 . 10 - 4` and `* DIEI ==outcomes in E` carry marks no name has, and `Addition
#: principle-` ends on a hyphen because it is half of a heading. All six of those are
#: values the deterministic `subject` slot was measured storing off a real disk
#: (`tests/p6/test_p6_subject_slot.py`), and not one of them may return through here.
_TITLE_SHAPE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9 '&-]*[A-Za-z0-9])?")


def _a_title_a_person_could_confirm(text: str) -> str | None:
    """`subject`'s three refusals beyond the shared shape, unchanged since R-98.

    1. *A code, or a line containing one.* `_STRUCTURED` is the one definition of an
       identifier this file authors; if it fires anywhere in the value, the direct
       path owns the value and the phrase around it is what A_fact rule 4 refuses
       ("the smallest run of characters that identifies the thing, not the phrase that
       contains it"). This is what keeps `PHYS1401 Problem Set 4` -- stress case S1 --
       refused.
    2. *A term.* `_is_term` is the same test the `subject` rule holds itself off with,
       so `Spring 2026` proposed as a subject is refused here for the reason it is
       refused there and not for a second one.
    3. *Nothing lower-case anywhere.* A course code and its fragments are written in
       capitals and digits; a name is written in words. This is what keeps `PHYS` --
       stress case S6's control, "a bare uppercase token ... a fragment of something
       longer" -- and the measured whole headings `AUDIENCES IN GA4` and `ADVERTISING
       REPORTS` out. It is also the honest limit of the rule: a title a document
       prints in capitals is refused with them, and the person is not asked.

    THE TWO LENGTH BOUNDS ARE SUBJECT'S ALONE and stay in this function rather than
    moving up to the shared shape. `105` §1.3-§1.4 measured them on COURSE NAMES; the
    library's own `work_type` terms run to a 77-word editorial aside
    (`facts.kind.KindVocabulary` records it), so a bound measured on titles applied to
    another field's values would be a number this file authored for a vocabulary it
    does not own -- which is exactly what `00`:298 forbids.
    """
    if len(text) > SUBJECT_TITLE_MAX_CHARACTERS:
        return None
    if len(text.split(" ")) > SUBJECT_TITLE_MAX_WORDS:
        return None
    if not any(character.islower() for character in text):
        return None
    if _is_term(text) or _STRUCTURED.search(text) is not None:
        return None
    return text


def _a_kind_of_work_a_person_could_confirm(text: str) -> str | None:
    """`work_type`'s two refusals: it must not be a WHEN, and it must not be a WHO-or-WHAT.

    Both are the same refusal in two spellings -- *this value is another field's
    answer with words around it* -- and neither is a vocabulary. `_is_term` is asked
    first so a refusal can say WHICH: `FIELDS_THAT_CANNOT_ANCHOR_A_MOVE` holds
    `work_type` and `term` as the two fields that can say "what, or when", and a
    proposal that says when is the other one of the pair. `_STRUCTURED` is refusal 1
    above, unchanged in its reasoning: `Homework PHYS1401` proposed as a kind of work
    is a course code with a word in front of it, and a folder named after both is the
    `65` §4.2 failure with a longer label.

    **NOTHING ELSE IS REFUSED, AND THAT IS THE WHOLE OF `104` §18.2 GAP 3 FOR THIS
    FIELD.** `Proposed Scope` and `Abstract` -- two of the four values a real cloud
    run produced that the 942-term library has never seen -- come back from here and
    become proposals the person is shown. Under the closed vocabulary they were
    `VALUE_NOT_NORMALIZABLE`, which on r15 was the largest rejection class. The two
    measured values that must NOT come back, `.pdf` and `GRC Proposed Scope V2.1`, are
    refused by the shared shape one level up because both carry a dot; `.pdf` is the
    one that became the folder `Coursework/Daniel Lacker/IEOR3658/.pdf`.
    """
    if _is_term(text):
        return None
    if _STRUCTURED.search(text) is not None:
        return None
    return text


def _a_term_a_person_could_confirm(text: str) -> str | None:
    """`term`'s one refusal: the three shapes the owner ruled are NOT terms.

    `term_refusal` already names them -- a bare year, a bare range, a season initial
    -- and `105` §14.2 ruled each one out by hand. They are not values the library has
    not seen; they are values the owner has seen and decided against, on stated
    grounds: `2019` says which year and not which semester, `2023-2024` is an academic
    year and §14.2 rules that even `AY 2024-25` "does not identify a semester", and
    `S2026` is genuinely two answers because Spring and Summer share an initial.
    Proposing one of those to a person would be asking them to ratify an ambiguity the
    owner has already resolved, so the ruling survives the opening of the field.

    **`_STRUCTURED` IS DELIBERATELY NOT ASKED HERE, and the asymmetry with `work_type`
    one function up is the point.** Every term names a year, and `_STRUCTURED` reads
    `<capitalised word><optional separator><three or more digits>` -- so it matches
    `Trimester 2025` and `Semester 2024` exactly as it matches `PHYS 1401`. That is
    not a new observation: `find_structured_strings` runs `_TERM` FIRST for this
    reason, and its docstring records that swapping the two lines "would file a
    person's essays under a course named after their semester". Asking `_STRUCTURED`
    here would refuse the very shape this change exists to propose.

    The whitespace-collapsed value comes back as it was written. There is no library
    spelling to prefer -- that is what "a value the library has not seen" means -- and
    `DATE_PATTERNS`' per-pattern canonicalisers each belong to a pattern that did not
    match, so borrowing one would be canonicalising by a rule that does not apply.
    """
    if term_refusal(text) is not None:
        return None
    return text


def normalize_for_review(field_key: str, raw_value: object) -> str | None:
    """§3.6 check 3's SECOND question: is this a value a person could confirm?

    **This exists because ten correct answers were thrown away.** On the owner's
    pinned corpus, cloud, the model answered `subject` ten times on the files that are
    genuinely coursework and all ten were refused `VALUE_NOT_NORMALIZABLE`: every one
    was a course TITLE and `SUBJECT_RULE.pattern` requires a code. `105` §1.5 reports
    the same thing as gap G15 -- until a title becomes "confirm this new value", *"no
    title-named course can be filed"* -- and `104` §11.2 step 1 defines `subject` as
    *"the course as the course names itself (code or title)"*.

    **It is a second question and not a wider answer to the first one.**
    `normalize_for_model` above is unchanged: it still asks whether the value is the
    identifier the deterministic rule reads, and its `None` is still what stops a
    model laundering `!` or a whole heading into a folder name. What this function
    answers is `104` §13.7's question instead -- *"the model names, the user
    confirms"* -- and its answer reaches P6 as `possible`, which `00`:42 fixes as the
    state of a model output that *"may remain a possible clue for review"* and which
    `facts.read_surface.PROPOSAL_ELIGIBLE_STATES` keeps out of every folder proposal.
    So a title is offered to the person and cannot become a level until they answer.

    **`work_type` AND `term` ARRIVED HERE ON 2026-09-09, AND THE SENTENCE THIS
    DOCSTRING USED TO END ON IS WITHDRAWN.** It read: *"Only `subject` has one ...
    answering it here would be authoring a vocabulary."* `104` §18.2 gap 3 measures
    what that cost -- `VALUE_NOT_NORMALIZABLE` was r15's largest rejection class and
    `term` and `work_type` were most of it -- and rules the reasoning wrong end up.
    `00`:298 is the amendment the old sentence was arguing against without saying so:
    *"`work_type`, `subject`, `term` and user labels are model decisions grounded in
    the file's evidence. A value the shipped library has not seen is proposed once;
    the user confirms or renames it; it then belongs to that user's vocabulary in the
    database."* A closed set in code that turns an unseen value into a rejection is
    the code deciding, which is the one thing the constitution's first rule forbids.

    **THE CLOSED SETS ARE NOT DELETED. THEY BECOME THE SEED.** `WORK_TYPE_VOCABULARY`
    and `DATE_PATTERNS` still answer FIRST, in `normalize_for_model` above, and a
    value either of them knows is still `accept_direct` in the library's own spelling
    -- which is what `00`:298's last clause means by *"the ratified library is the
    vocabulary the model is shown first"*. What changed is only what happens to a
    value they do not know: it used to be a rejection and it is now a proposal. Not
    one assertion in
    `tests/p6/test_p6_kind.py::test_a_model_work_type_outside_the_librarys_vocabulary_
    is_not_normalizable` moved, because that test pins the seed.

    **THE SHARED SHAPE, AND WHY ONE SHAPE SERVES THREE FIELDS.** `_TITLE_SHAPE` was
    written for course titles and its content is not about courses: letters, digits,
    single spaces, an apostrophe, an ampersand, an internal hyphen, beginning and
    ending on a letter or a digit. That is the shape of a LEVEL'S LABEL, and all three
    of these fields bind to levels -- so the values it refuses are refused for the
    same reason at each of them. It is §13.5's bar and no more than that: *a rule may
    reject only a structurally invalid answer*. What it keeps out is what this
    deployment has actually measured -- `report.pdf` and `.pdf` carry a dot, `(i)`
    carries brackets, `* DIEI ==outcomes in E` and `#corre 1 . 4 - 1 : 4 . 10 - 4`
    carry marks no label has, `Addition principle-` ends on a hyphen because it is
    half of a heading, and `GRC Proposed Scope V2.1` carries a dot for the same reason
    a version string does.

    A field with no review normaliser still returns `None` and is still
    `VALUE_NOT_NORMALIZABLE`: `instructor` and `school` name PEOPLE and INSTITUTIONS,
    and neither `00`:298's sentence nor gap 3 opens them. That is a scope line and not
    a ruling -- when the owner opens one, it is one more branch here.
    """
    if not isinstance(raw_value, str):
        return None
    text = " ".join(raw_value.split())
    if not text:
        return None
    if _TITLE_SHAPE.fullmatch(text) is None:
        return None
    if field_key == SUBJECT_RULE.field_key:
        return _a_title_a_person_could_confirm(text)
    if field_key == WORK_TYPE_FIELD:
        return _a_kind_of_work_a_person_could_confirm(text)
    if field_key == TERM_FIELD:
        return _a_term_a_person_could_confirm(text)
    return None


def contradicts_stronger(proposal, existing_fact) -> bool:
    """§3.6 check 4: does a stronger fact contradict this proposal?

    `build_request` supplies only facts ALREADY STRONGER than an LLM conclusion --
    `validated`, `direct`, `user_confirmed` -- so reaching here means the model is
    disagreeing with something better supported than itself, and §3.6 says the
    better-supported thing wins.

    **Compared after canonicalisation, which is the whole reason this is not a
    string comparison.** `PHYS 1401` and `PHYS1401` are one course. Comparing raw
    values would make the model's own AGREEMENT read as a conflict and reject a
    correct answer with `CONTRADICTED_BY_STRONGER` on the record -- a particularly
    misleading thing to be wrong about, since it says the evidence disagreed when
    it agreed in a different spelling.

    A stronger fact about ANOTHER FIELD is not a contradiction. Knowing the term
    cannot contradict a claim about the subject, and treating every stronger fact
    as a rival would let one settled field veto every proposal about the file.

    An unnormalizable proposal answers `False` rather than `True`: check 3 runs
    first and has already rejected it, and claiming a contradiction as well would
    put a second, wrong reason on a record that §3.6 keeps one reason per refusal.
    """
    if existing_fact["field_key"] != proposal.field_key:
        return False
    proposed = normalize_for_model(proposal.field_key, proposal.value)
    if proposed is None:
        return False
    return existing_fact["canonical_value"] != proposed


def _direct_stage(conn, file_id: str, content_hash: str) -> tuple[str, ...]:
    return direct_facts(conn, file_id=file_id, content_hash=content_hash,
                        slots=DIRECT_SLOTS, screen=METADATA_SCREEN)


#: §3.7's positional weights, over P4's fifteen zones. The SPEC defers them by name
#: and `facts.facets.rank` RAISES on a zone it was given no weight for rather than
#: defaulting, so all fifteen are here. The shape is §3.7's own sentence: "a value
#: in a filename or document title carries more meaning than the same value in a
#: footer or a late body-page reference."
#:
#: **`104` §18.2 GAP 6 NAMED THIS TABLE AND IT STANDS, WITH ITS REASON (9 Sep 2026).**
#: The gap reads this as the product's second ordering of what the model sees,
#: disagreeing with `model_facts._ZONE_PREFERENCE`; the other half of the pair is
#: gone, replaced by `model_facts.zone_evidence_counts`, and this one is not. It is
#: not an ordering of what the model sees at all: nothing in a dossier reads it. Its
#: two consumers are `date_facts` and `kind_facts` below, through `facets.rank`,
#: where it decides which candidate value a DETERMINISTIC producer writes to
#: `file_facts` -- and two consequences follow that the gap does not weigh. A weight
#: map derived from the store would make file N's facts depend on files 1..N-1, which
#: is the property `facts/evidence.py` states this package does not have ("the same
#: corpus extracted in a different order produces the same facts", §8.5 replay); an
#: ORDER may be corpus-derived because nothing is decided by it, a stored fact may
#: not. And the neutral answer where nothing has been measured -- every zone equal --
#: turns §3.7's 3:1 title-over-footer into a `below_margin` abstention on every
#: first-seen field, against `MINIMUM_SCORE` and `MINIMUM_MARGIN` below, which are
#: set to these numbers. So this is recorded rather than deleted, on §18.6's own
#: pattern for S6: the arm is not dead, and the owner rules whether §3.7's weights
#: become something else.
ZONE_WEIGHT = {"filename": 3.0, "title": 3.0, "heading": 2.0, "body": 1.0,
               "header_footer": 0.25, "metadata": 1.0, "path": 1.0, "table": 1.0,
               "notes": 1.0, "link": 1.0, "annotation": 1.0, "reference_list": 0.5,
               "manifest": 1.0, "ocr": 1.0, "transcript": 1.0}

#: §2.6's three bands, likewise deferred and likewise required.
TIER_WEIGHT = {1: 4.0, 2: 2.0, 3: 1.0}

#: §3.7's two thresholds. One reading of a term in a document's body scores exactly
#: 1.0, so the floor is set where a single honest mention clears it and nothing
#: below one does. The margin is half of that: two different terms in one file are
#: within it and fill nothing, which is the refusal §3.7 asks for rather than a
#: guess between them.
MINIMUM_SCORE = 1.0
MINIMUM_MARGIN = 0.5

#: The field `artifact_kind` binds, spelled once beside `TERM_FIELD` and
#: `SUBJECT_FIELD` for the same reason: several callers need it and none may
#: re-spell it. `def.subject-work-record` marks it REQUIRED, and until 2026-09-04
#: nothing in `src/` produced it -- so the second of the recipe's two required
#: levels could never be built and every file in the situation went unplaced.
WORK_TYPE_FIELD = "work_type"

#: THE TWO FIELDS THAT CAN SAY WHAT, OR WHEN, AND NEVER WHOSE. P11's
#: `_without_kind_only_moves` refuses to carry a file out of the folder it is in
#: on one of these alone; this is where the deployment says which fields they are,
#: because the roles are the template library's and the FIELDS each role binds to
#: are this catalogue's.
#:
#: `src/tree_design/library` authors forty-five dimension roles and SEVERAL of them
#: are what-or-when: `artifact_kind`, `cycle_period`, `capture_time`,
#: `capture_kind`, `scope_period`, `lifecycle_stage` and every other `*_period`.
#: This is not a list of those roles. It is the list of FIELDS this catalogue can
#: actually fill with one, and there are two: §8.6's producers fill `work_type`
#: and `term` and nothing else that answers what-or-when.
#:
#: `media_type` is the omission that shows the shape of the decision. §2.6's
#: photograph-or-screenshot answer is a what-kind fact and belongs here on the
#: reasoning; it is left out because no folder in this deployment expects it, so
#: naming it would be a rule with nothing to act on. The same is true of every
#: role above that no producer fills. The day either changes, this set is where
#: it changes.
FIELDS_THAT_CANNOT_ANCHOR_A_MOVE = frozenset({WORK_TYPE_FIELD, TERM_FIELD})
#: `artifact_kind`'s closed vocabulary, WHICH THE LIBRARY ALREADY SHIPPED. The
#: compiled recognition release carries `work_type_terms` per schema and nothing had
#: ever read them for a field -- the detector tokenises them to decide handling and
#: throws the term away. They are the same closed set the library's own example
#: chains draw on, and twelve of the thirteen distinct leaf values the ground-truth
#: labels use for `academic.coursework` are members of it verbatim.
#:
#: THE JOIN IS `60` H6.2, APPLIED TO THE VOCABULARY. Only the four schemas that
#: DECLARE this field contribute: "a file whose routed type key is not declared by
#: the active schema returns unknown; it is never re-routed to the nearest declared
#: type key." Taking the union over all twenty-three would let `medical`'s
#: `discharge summary` become a `work_type`, which is the re-route that sentence
#: forbids. The four are `academic`, `career`, `law_practice` and
#: `construction_property`, and they are read off `DOMAIN_FIELDS` rather than listed
#: here, so a catalogue that declares the field on a fifth schema widens this with
#: no edit and one that drops a schema narrows it.
#:
#: The schema is not known when this runs -- `run_p1_p7` resolves facts BEFORE it
#: classifies -- so the vocabulary cannot be narrowed per file. It does not need to
#: be: a term two of the four authored is the same VALUE either way, and the
#: `work_type` a file carries does not change with which of them claims it.
def _work_type_vocabulary():
    """The shipped terms of every schema that declares the field. Read once."""
    schemas = json.loads(_RECOGNITION_MANIFEST.read_text())["schemas"]
    return compile_vocabulary(
        term
        for schema_id, fields in DOMAIN_FIELDS.items()
        if WORK_TYPE_FIELD in fields
        for term in schemas.get(schema_id, {}).get("work_type_terms", ()))


WORK_TYPE_VOCABULARY = _work_type_vocabulary()

#: THE THREE FIELDS `normalize_for_review` ANSWERS FOR, spelled once because two
#: readers need the set and neither may re-spell it: the normaliser branches on it,
#: and `_print_values_to_confirm` prints exactly the proposals it produced. `00`:298
#: names these three and one more class -- *"`work_type`, `subject`, `term` and user
#: labels"* -- and user labels are P10's renamed levels, which have their own gesture
#: and never pass through §3.6 check 3, so three is the whole of it here.
#:
#: `instructor` and `school` are the omission that shows the shape of the decision.
#: Both were refused on the same run for the same reason, and both name a PERSON or an
#: INSTITUTION rather than a property of the work; neither `00`:298 nor `104` §18.2
#: gap 3 opens them, and opening a field nobody ruled on would be this file deciding
#: which of a person's values are theirs to name.
REVIEW_NORMALISED_FIELDS: tuple[str, ...] = (
    SUBJECT_FIELD, WORK_TYPE_FIELD, TERM_FIELD)

assert SUBJECT_RULE.field_key == SUBJECT_FIELD, (
    "the review normaliser branches on `SUBJECT_RULE.field_key` and this set is "
    "spelled from `SUBJECT_FIELD`; two spellings of one field key is how a screen "
    "comes to print a set the normaliser never filled")


def normalize_with_the_persons_own_values(
        conn: sqlite3.Connection) -> Callable[[str, str], str | None]:
    """§3.6 check 3, asked of the LIBRARY first and of the PERSON'S ANSWERS second.

    **This is the second half of `104` §18.2 gap 3, and without it the first half
    asks the same question forever.** `normalize_for_review` turns a value the shipped
    library has not seen into a proposal instead of a rejection; `00`:298 says what
    happens after the person answers it -- *"the user confirms or renames it; IT THEN
    BELONGS TO THAT USER'S VOCABULARY IN THE DATABASE"*. Until this closure existed
    nothing read that vocabulary back, so a value confirmed on Monday was proposed
    again on Tuesday, and `possible` is below `PROPOSAL_ELIGIBLE_STATES`, so it could
    never become a folder however many times the person said yes.

    **THE ORDER IS THE RULING.** The pure `normalize_for_model` answers first, so the
    ratified library is still *"the vocabulary the model is shown first"* and its
    spelling still wins for a term it ships -- `Lecture` is still `lecture`, in the
    library's casing, exactly as before. Only where the library has nothing to say is
    the person's own vocabulary consulted, which is the only place their answer could
    be about.

    **NO ALIAS TABLE, NO EQUIVALENCE MAP, NO LIST.** `00`:298 forbids all three by
    name and this closure holds none: it reads
    `facts.read_surface.confirmed_spellings`, which is a query over the `values` and
    `file_facts` rows the person's own answers wrote. The equivalences are DATA in
    their database, put there by `facts.values.merge_values` when they rename
    something -- so two people who answer differently get different normalisers out of
    the same code, which is what "that user's vocabulary" means.

    **THE PURE FUNCTION IS NOT TOUCHED, and that is deliberate rather than shy.**
    `normalize_for_model(field_key, raw_value)` keeps its exact signature and its
    exact answers; dozens of pins call it bare and P6's own tests read it as a
    deployment's rule. What is injected at the seam is a normaliser that knows a
    database, because a database is the one thing a pure canonicaliser cannot have and
    the one thing a user-specific vocabulary must be.

    A confirmed value comes back as `accept_direct` and therefore as `llm_supported`,
    which IS proposal-eligible -- the person said yes, so a folder may rest on it. That
    is the whole point of asking them, and it is why nothing here shortcuts to the
    review half.
    """

    def normalize(field_key: str, raw_value: str) -> str | None:
        seeded = normalize_for_model(field_key, raw_value)
        if seeded is not None:
            return seeded
        if not isinstance(raw_value, str):
            return None
        # THE SAME COLLAPSE BOTH NORMALISERS ALREADY APPLY, so `PHYS  1401` off a
        # two-column page and the person's stored answer are compared as one string
        # rather than as one string and its whitespace.
        text = " ".join(raw_value.split())
        if not text:
            return None
        return confirmed_spellings(conn, field_key=field_key).get(text)

    return normalize


def _cited_line(conn: sqlite3.Connection, fact_id: str, value: str) -> str | None:
    """The line of a cited reading that carries the value, or `None`.

    §3.1 is unconditional -- "Every fact preserves where it came from" -- so a
    proposal always cites something; the two `except` arms below are for a database
    whose evidence a later pass retired, and they answer `None` rather than raising,
    because a report that dies on one missing observation tells the person nothing
    about the other twenty.

    **THE LINE CARRYING THE VALUE, AND ONLY THEN THE FIRST LINE.** A citation can be
    a whole-zone reading -- a whole page, a whole document -- and its first line is
    then a sentence about something else entirely, printed under a question about a
    value that does not appear in it. §3.6 check 2 has already established that the
    value occurs in the released text, so the line that carries it exists whenever
    the reading is the one the model quoted; the fallback covers a citation whose
    text was normalised between the claim and this read.

    A LINE AND NOT THE FIRST N CHARACTERS. A truncation length here would be a number
    this file authored to decide what a person sees; a line is the document's own
    unit.
    """
    try:
        chain = evidence_chain(conn, fact_id=fact_id)
    except (LookupError, DanglingCitation):
        return None
    first: str | None = None
    for observation in chain:
        for line in observation.raw_value.splitlines():
            collapsed = " ".join(line.split())
            if not collapsed:
                continue
            if value in collapsed:
                return collapsed
            if first is None:
                first = collapsed
    return first


def _print_values_to_confirm(conn: sqlite3.Connection, out) -> None:
    """`104` §18.2 gap 3's last clause: *a proposal the person SEES*.

    **AND SINCE GAP 1, THE SCREEN WHERE A DISAGREEMENT LANDS.** Gap 1 stops check 4
    rejecting a model answer that contradicts a rule's fact: the answer is flagged
    `requires_review` and written `possible` beside the rule's, so it arrives in
    exactly the state this block already reads. What it needed was a second sentence
    -- the rules' own value, and which of the two is in force -- because the heading
    said every proposal here was a value the shipped vocabulary had not seen, and a
    contradicting value usually IS in the vocabulary. `84` §6: what the screen tells
    a person has to be true.

    **THE BOUND, AND IT IS `REVIEW_NORMALISED_FIELDS`.** This block reads three
    fields, and gap 1 can flag any field the situation builds a folder from. The
    three are where every measured contradiction was -- `104` §18.2 gap 1 counts 16
    `subject` and 17 `work_type` facts on r15 -- and widening the read is the confirm
    gesture's question rather than this one's, because a field with no review path
    has nothing for the person to answer with. Stated here so the absence is a
    decision and not an oversight.

    **The screen this block ends the absence of.** `normalize_for_review` has turned
    an unseen value into a `possible` fact since R-98, and `possible` is below
    `PROPOSAL_ELIGIBLE_STATES` -- so from the day it shipped, the product's answer to
    "the model names, the user confirms" was a row in a table with no line anywhere
    on the report and no way for a person to know it existed. `00`:298 says the value
    *"is proposed once"*, and a proposal nobody is shown is not a proposal; it is the
    same silent loss the rejection was, with a better state name. Gap 3 says it in as
    many words: *"A rejected value must become a proposal the person sees, with the
    model's evidence beside it."*

    **IT PRINTS ALL THREE FIELDS, INCLUDING `subject`.** The gap is filed against
    `work_type` and `term`, and the screen it asks for was missing for `subject` too;
    a block that showed the two new fields and not the one whose review path they were
    given would put a person's course titles back in the dark to keep a diff small.

    **THE EVIDENCE IS THE MODEL'S OWN CITATION**, walked back through
    `facts.read_surface.evidence_chain` to the P4 observation the claim cited. §3.6
    check 2 has already established that the value occurs in that released text, so
    the line printed is where the model got it -- which is what makes the question
    answerable rather than a request to trust a machine.

    **WHAT THIS SCREEN DOES NOT YET OFFER, SAID HERE AND ON THE SCREEN ITSELF.** There
    is no confirm gesture and no rename gesture in this command. `--reject` exists and
    is printed because it is TRUE and typeable; confirming writes a `user_confirmed`
    fact and renaming calls `facts.values.merge_values`, and neither has a flag. The
    read side is built and tested (`normalize_with_the_persons_own_values` above), so
    the day the owner shapes those two gestures the vocabulary they write is already
    consulted. Printing a gesture that does not exist would break `84` §6 -- what the
    screen tells a person to type has to be true -- so the block says plainly that the
    answer is not typeable yet rather than inventing a flag to look finished.

    **AND IT PRINTS WITH THE FACT PASS, WHICH IS A BOUND WORTH NAMING.** The call site
    is inside `_model_fact_pass`, so a run that reaches none of its four early returns
    prints this and a run that reaches one of them does not -- even though a standing
    proposal from an earlier run is still open. The reconciliation `104` §18.2 gap 10
    built has the same shape of answer for coverage and solved it by printing outside
    the pass; doing the same here belongs with the confirm gesture, because a person
    shown an open question on a run that asked nothing needs a way to answer it.
    """
    proposals: dict[tuple[str, str], list[sqlite3.Row]] = {}
    # `104` §18.2 GAP 1: WHAT THE RULES ALREADY SAID ABOUT THE SAME SLOT. Free, and
    # that is why it is gathered here rather than queried: `versions_in_fields` is
    # UNFILTERED by state -- its own docstring says so -- so the `validated` row the
    # regex wrote is already in `rows` beside the `possible` row the model wrote, and
    # a second read would be a second answer to one question.
    #
    # Keyed by FILE and field rather than by file version, because that is the key the
    # print loop below has: `versions` carries `(file_id, fact_id)` pairs and adding a
    # content hash to them would change what `files` counts. A file with two live
    # versions carrying two different rule values would show both, which is more than
    # a person needs and never less.
    settled: dict[tuple[str, str], set[str]] = {}
    for rows in versions_in_fields(
            conn, field_keys=REVIEW_NORMALISED_FIELDS).values():
        for row in rows:
            if not row["active"] or row["superseded_by"] is not None:
                continue
            # `possible` AND LIVE. A superseded or deactivated proposal is a
            # readable old row (§8.2) and not a question still open, and asking a
            # person about one would be re-asking something they have answered.
            if row["reliability_state"] == POSSIBLE:
                proposals.setdefault(
                    (row["field_key"], row["canonical_value"]), []).append(row)
                continue
            # STRONGER THAN AN LLM CONCLUSION, which is §3.13's own comparison and
            # the same one `facts.llm_seam.build_request` uses to decide which facts
            # check 4 is run against. `strength` raises for `rejected`, so membership
            # is tested before the ladder is: a rejected fact is an exclusion, not a
            # weaker answer, and it is not what the rules say about the file.
            if row["reliability_state"] == REJECTED_STATE:
                continue
            if strength(row["reliability_state"]) > strength(LLM_SUPPORTED_STATE):
                settled.setdefault(
                    (row["file_id"], row["field_key"]), set()).add(
                        row["canonical_value"])
    if not proposals:
        return
    print("\nNew values the model proposed, waiting on you:", file=out)
    print(_wrapped(
        "None of these is filing anything: nothing is placed under a value until it "
        "is confirmed. Most are values this product's own vocabulary has not seen. "
        "Where a line below says the rules read something else, the model was shown "
        "what the rules had already decided and disagreed with it -- the rules' "
        "value is the one still in force, and yours is the answer that settles it. "
        "Each is proposed once, with the line the model was reading beside it.",
        indent="  "), file=out)
    for (field_key, value), rows in sorted(proposals.items()):
        # ONE ROW PER FILE VERSION, so a value read from six files says six and not
        # however many facts those six files carry.
        versions = sorted({(row["file_id"], row["fact_id"]) for row in rows})
        files = len({file_id for file_id, _fact in versions})
        named = get_file(conn, versions[0][0])
        # `--reject` TAKES A FILENAME AND NOTHING ELSE, and refuses one that names
        # two files. Printing a path or a file id here would tell the person to type
        # something the gesture rejects, which is `84` §6's own failure.
        filename = "<no name on record>" if named is None else named["filename"]
        print(f"\n  {field_key.replace('_', ' ')}: {value!r} "
              f"-- on {files} {'file' if files == 1 else 'files'}, "
              f"first {filename!r}.", file=out)
        line = _cited_line(conn, versions[0][1], value)
        if line is not None:
            print(_wrapped(f"The model was reading: {line!r}", indent="    "),
                  file=out)
        # `104` §18.2 GAP 1: THE DISAGREEMENT, IN FRONT OF THE PERSON. Until tonight
        # this value could not exist -- check 4 rejected a model answer a stronger
        # fact contradicted, and the claim was discarded with no row and no line. It
        # is now written `possible` beside the rule's fact, which is `00`:42's
        # "possible clue for review", and this is the sentence that makes it one: a
        # proposal nobody is shown is not a proposal.
        #
        # THE RULES' VALUE IS NAMED AND THE ORDER IS STATED. `possible` is below
        # `PROPOSAL_ELIGIBLE_STATES` and `facts.supersede.preferred_of_slot` does not
        # let it out-vote a `validated` row, so the rules' value is what the product
        # is still acting on -- and a screen that showed the model's value alone
        # would read as if it had won.
        rules_said = sorted({
            other
            for file_id, _fact in versions
            for other in settled.get((file_id, field_key), ())
            if other != value})
        if rules_said:
            spelled = ", ".join(repr(other) for other in rules_said)
            print(_wrapped(
                f"The rules read {spelled} for this field and that is what is "
                f"still in force; the model was shown so and answered {value!r} "
                "anyway.", indent="    "), file=out)
        # PRINTED RAW, NEVER WRAPPED. `_role_lines` states the rule and `84` §6 is
        # the defect behind it: "textwrap breaking a command across two lines
        # produces a command that does not work". A filename with a space in it is
        # exactly where `_wrapped` would break this one.
        print(f"    --reject {shlex.quote(f'{filename}:{field_key}={value}')}"
              f"   No, that is not right", file=out)
    print("", file=out)
    print(_wrapped(
        "Saying YES to one of these is not a gesture this command has yet: the "
        "product can store your answer and will use it on every later run, and "
        "there is no flag to type it with. Until there is, a proposal stays a "
        "proposal and files nothing.", indent="  "), file=out)


#: The field the coursework `holder_institution` role resolves to, spelled here for
#: the same reason `TERM_FIELD` and `WORK_TYPE_FIELD` are: the composition root is
#: where a field key this deployment acts on is named, and P6, P8 and P10 each read
#: it from what they are handed rather than from a second spelling of their own.
SCHOOL_FIELD = "school"

#: `105` §14.4's PERMITTED ANCHORS, as this deployment's shipped vocabulary already
#: spells them. The owner's ruling names four kinds -- "a syllabus, an enrollment or
#: registration letter, a transcript, a tuition or housing statement" -- and every
#: member below is a term `WORK_TYPE_VOCABULARY` already ships for `academic`, so
#: nothing here is a new vocabulary member and a test pins each one to the compiled
#: release rather than to this list.
#:
#: WHAT IS DELIBERATELY OUT. `caption transcript` is a media captions file and not a
#: record of study, so it is the one `transcript` term left out; `credit transcript`
#: is in, because a transcript of academic credit is exactly the document §14.4
#: names. The library ships no term for the ruling's fourth kind -- a TUITION OR
#: HOUSING STATEMENT has no `work_type` term in any of the four schemas that declare
#: the field -- so that kind cannot be admitted here at all today, and it is owed to
#: the owner as a vocabulary member rather than invented in this file.
#:
#: The library also has no "letter" spelling for the enrollment and registration
#: kinds; what it ships is the certificate, form, verification and confirmation an
#: institution issues, which is the same document class under the names the release
#: gives it. The owner's ruling is the wording, and this is the transcription.
#:
#: ANCHOR KIND IS NECESSARY AND NOT SUFFICIENT (§14.4). Membership here decides only
#: that the file may be ASKED; whether its text establishes the institution's
#: relationship to the course or enrollment being organised is the drafted rule 12
#: of the A_fact text, the owner's to ratify, and whether an answer becomes a
#: folder level is the two-anchor rule at P10.
SCHOOL_ANCHOR_KINDS: frozenset[str] = frozenset({
    "syllabus",
    "enrollment certificate", "enrollment form", "enrollment verification",
    "registration confirmation", "registration form",
    "transcript", "transcript of records", "unofficial transcript",
    "credit transcript",
})


def rests_on_a_name_alone(conn: sqlite3.Connection):
    """`105` §14.4's pin: a FILENAME is never a source for a folder level.

    `104` R-95 measured what a name-only answer produces. On a 52-file corpus the
    local run wrote 38 `llm_supported` facts, every one of them a `school`, and
    most of them were the file's own name -- `todo.txt`, `IMG_4822.jpg`,
    `submission_backup.zip`. A name is the person's label for a file, not a
    reading of what the document says, and §14.4 asks the anchor's own text to
    establish the institution's relationship to the course.

    **The question is asked of the CITATION and not of the value**, which is what
    makes it checkable: the name is one observation with one key, `filename_
    address` is where the gate and the builder both get it (`model_facts.
    filename_citation` says so in its own words), and a fact citing that key and
    nothing else rests on the name alone.

    Two absences answer `True` -- a fact whose citations resolve to nothing, and a
    fact citing nothing at all -- because a value with no reading behind it is
    weaker than one resting on a name, not stronger. A `user_confirmed` value
    legitimately cites nothing, and it never reaches here: the person's own answer
    is admitted before this rule is asked (`upstream._group_level_agreed`).

    A file with no addressable name answers `False`: there is no name for the
    citation to be, so the value rests on something else by construction.
    """

    def rests(file_id: str, fact_id: str) -> bool:
        try:
            named = filename_address(conn, file_id).observation_key
        except (UnresolvableSpan, AmbiguousObservationKey):
            return False
        try:
            cited = {observation.observation_key
                     for observation in evidence_chain(conn, fact_id=fact_id)}
        except (LookupError, DanglingCitation):
            return True
        return not cited or cited == {named}

    return rests


#: `104` R-37's anchor table: `work_type` term -> the ONE schema that authored it,
#: over the same four schemas as the vocabulary above. Measured: 940 of the 942
#: terms have one owner; `reference letter` and `reference list` are academic's
#: and career's both, and anchor neither. `branch_situation` carries the argument.
WORK_TYPE_OWNER: Mapping[str, str] = MappingProxyType(single_owner_terms({
    schema_id: json.loads(_RECOGNITION_MANIFEST.read_text())["schemas"]
    .get(schema_id, {}).get("work_type_terms", ())
    for schema_id, fields in DOMAIN_FIELDS.items()
    if WORK_TYPE_FIELD in fields}))

#: P7's naming zones, MINUS `heading`, and the subtraction is the composition root's
#: because it is a policy rather than a rule. A heading names a SECTION; a filename
#: and a document title name the DOCUMENT, and `work_type` is a claim about the
#: whole file. P7 keeps `heading` because it is deciding PROTECTION, where reading a
#: section title as the file's own kind errs toward sealing a file that did not need
#: it -- the safe direction. Here the same reading errs toward a folder name, which
#: is the unsafe one.
#:
#: Measured over the ground-truth corpus, of the 36 files this producer filled:
#: every fill whose ONLY evidence was a heading was wrong -- three of three, a
#: market analysis called `diploma` off a section title, an `index.html` called
#: `notes` -- and not one correct fill depended on a heading. Filename and title
#: carried all 20 correct ones. `header_footer` stays: it weighs 0.25, so a single
#: reading there cannot clear §3.7's floor by itself, and it can still corroborate.
WORK_TYPE_NAMING_ZONES = NAMING_ZONES - {"heading"}


def _rule_stage(conn, file_id: str, content_hash: str) -> tuple[str, ...]:
    """§8.6's second producer: §3.5's rule, §3.10's dates, and §2.6's one question.

    `apply_rules` stopped being uncalled on 2026-09-04. It had been written and
    tested since P6 landed with no caller at all, while `subject` was filled by a
    DIRECT slot over the same pattern and no context check -- which measured 0
    correct and 14 wrong on the owner's own files, and named two ZIP codes as the
    courses his documents were about. `SUBJECT_RULE` above carries the whole of that
    decision; what changes HERE is only that the producer runs.

    THE ORDER OF THE THREE IS ARBITRARY AND IS NOT LOAD-BEARING. They write three
    different fields, none reads another's output, and `_SUBJECT_IDENTIFIER`'s
    lookahead refuses a term wherever in this function it runs. It is written down
    because the opposite is easy to assume from the removed term SLOT, which shared
    every locator with the identifier slot and did have to be sequenced against it.
    Fixed rather than arbitrary at RUNTIME, though: §8.5 replays a run and compares
    it, so the sequence is stated here once instead of emerging from a set.
    """
    written = apply_rules(conn, file_id=file_id, content_hash=content_hash,
                          rules=(SUBJECT_RULE,), screen=METADATA_SCREEN)
    # `FIRST_PAGE` is P7's, and it reaches BOTH producers below for one reason
    # stated once: a term and a work type are the same kind of claim -- about what
    # THIS file is -- and a reading deep inside a document is the document talking
    # about something else. `date_facts` takes the page half of that test only; its
    # docstring records the measurement, and `WORK_TYPE_NAMING_ZONES` below is where
    # the zone half applies. The one correct `term` in the ground-truth corpus is in
    # `body`, so the zone half must not reach this call.
    written += date_facts(conn, file_id=file_id, content_hash=content_hash,
                          field_key=TERM_FIELD, patterns=DATE_PATTERNS,
                          first_page=FIRST_PAGE,
                          zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT,
                          minimum_score=MINIMUM_SCORE, minimum_margin=MINIMUM_MARGIN)
    # `artifact_kind`, the recipe's OTHER required level. `NAMING_ZONES` and
    # `FIRST_PAGE` are P7's, imported rather than restated: a term in body prose is
    # a document mentioning some other document, and `work_type` is a claim about
    # what this file IS. The four §3.7 numbers are the ones already above, shared
    # with the date producer so one reading of one band cannot fill a field here
    # and fail to fill one there.
    written += kind_facts(
        conn, file_id=file_id, content_hash=content_hash,
        field_key=WORK_TYPE_FIELD, vocabulary=WORK_TYPE_VOCABULARY,
        naming_zones=WORK_TYPE_NAMING_ZONES, first_page=FIRST_PAGE,
        zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT,
        minimum_score=MINIMUM_SCORE, minimum_margin=MINIMUM_MARGIN)
    return written + _media_type_stage(conn, file_id, content_hash)


#: The one thing about a file this deployment reads before asking §2.6's question:
#: is it an image at all. P1 stored the answer (`mime_type_for` is `_mime_type_for`
#: above), so this is a read and not a second detection.
IMAGE_MIME_PREFIX = "image/"


def _media_type_stage(conn, file_id: str, content_hash: str) -> tuple[str, ...]:
    """§2.6's photograph-or-screenshot question, asked of images and of nothing else.

    **The gate is the point.** `media_type` abstains honestly on a file with no
    tiered observation -- it writes `no_candidate_evidence` -- and asking it about
    every PDF in the corpus would put a refusal row on each one for a question
    nobody asked about it. `facts.families`' own rule is the one being followed
    here: "a relation nobody proposed was never attempted." Measured on a real
    42-file corpus, the gate is the difference between 5 refusal rows and 31.

    The three numbers are already this file's and are not re-chosen: `TIER_WEIGHT`
    is §2.6's three bands, and the two thresholds are §3.7's, shared with the date
    producer above so one reading of one band cannot fill a field here and fail to
    fill one there.
    """
    if not (get_file(conn, file_id)["mime_type"] or "").startswith(
            IMAGE_MIME_PREFIX):
        return ()
    written = media_type(conn, file_id=file_id, content_hash=content_hash,
                         tier_weight=TIER_WEIGHT, minimum_score=MINIMUM_SCORE,
                         minimum_margin=MINIMUM_MARGIN)
    return () if written is None else (written,)


def _resolver(*, tiers: frozenset[str], cache_key: str) -> FactResolver:
    """P6, deterministic. `llm` is `None`, which is a decision.

    §3 allows all three stages. This deployment ships no model route, and
    `FactResolver` treats `None` as "this stage does not exist" rather than as an
    empty one -- so a fact this run could not reach stays unresolved and visible
    instead of being recorded as absent.

    `rule` stopped being `None` on 2026-08-31. It is §3.10's date producer, not an
    authored rule set: `facts.dates` and `facts.facets` had both existed since P6
    landed and nothing joined them, so Done-means 10's three written forms produced
    two nothings and one `direct` fact the SPEC forbids.
    """
    return FactResolver(
        stages={"direct": _direct_stage, "rule": _rule_stage, "llm": None},
        pending_fields=lambda conn, file_id, content_hash: (),
        budget_exhausted=lambda ceiling: False,
        model_route_permitted=lambda file_id: False,
        record_pass=lambda conn, file_id, content_hash: record_pass(
            conn, file_id=file_id, content_hash=content_hash,
            analysis_tiers=tiers),
        cache_key_for=lambda file_id, content_hash: f"{cache_key}:{content_hash}",
        screen_metadata=lambda conn, file_id, content_hash: ())


class AFactRowNotRatified(RuntimeError):
    """`A_FACT_ROW` names a row whose status does not let site A apply answers."""


def a_fact_row() -> dict:
    """The manifest row `A_FACT_ROW` names, checked for what site A needs of it.

    `104` R-144. Refused at composition, before a corpus is read, when the row's
    word is `unratified`: A is a site that APPLIES its answers, and applying under
    text nobody approved is the thing `ratified` exists to say yes to.

    **The row's `glossary_file` is read by nobody here, deliberately.** The
    glossary the dossier ships is `llm_harness.dossier.GLOSSARY_FILE`, and the
    promptbench swaps that global to run another glossary arm under this same
    text; a check here that the row named the swapped-in file made
    `a_fact_prompt` refuse in whichever test ran after such a swap (the R-144
    merge turned about thirty tests red under `pytest-randomly` for exactly this).
    Which glossary is in the bytes is the dossier's fact, not the row's.
    """
    template_id, candidate = A_FACT_ROW
    row = prompt_library_a_fact_row(template_id, candidate)
    status = draft_status(template_id)
    if status not in STATUS_APPLIES:
        raise AFactRowNotRatified(
            f"A_FACT_ROW names {template_id!r} / {candidate!r}, whose status is "
            f"{status!r}. Site A applies its answers, so its row must carry "
            f"{sorted(STATUS_APPLIES)}; a v2 of A's text runs under "
            f"`ratified_local` on this device, never under `unratified`.")
    return row


def a_fact_prompt() -> PromptDefinition:
    """The one prompt this deployment may send at site A. Composed HERE, not in P8.

    **`104` R-144: the bytes come through `A_FACT_ROW`, a manifest row, exactly
    as the observe sites' do.** Same id, same three files, same digests, so the
    fingerprint is the one every A_fact record already carries; `ratified` is the
    row's own word rather than a literal here, and `a_fact_row` refuses an
    `unratified` row before anything is read.

    `llm_harness.prompt_library` holds the bytes and verifies them against their
    digests; it "picks no `template_id`, no `call_site_version`, no tier and no
    model; those are the composition root's". These are the composition root's.

    `template_id` names the ratification rather than the file, because that is what
    a record pointing at it needs to mean: `planning/82-FACT-PROMPT-DRAFT.md` §0
    records the owner ratifying this text on 2026-09-02, and a revision is a new
    file with a new id beside this one rather than an edit to either.

    **The text in force is the REVISION, and its id says `unratified`.** The dossier
    now carries a `folder_levels` key -- the folders the person's chosen situation
    would build, from the shipped template library -- and the ratified text says in
    its own words that the dossier "has these keys and no others", listing fourteen.
    Sending the new key under the old text would make the model's own instructions
    false about the bytes beside them, so the revision describes it: four lines,
    re-derived from the ratified file in `tests/p8/test_p8_a_fact_prompt_folder_
    levels.py`, adding no meaning for any field and quoting the ratified text itself
    for the two sentences that keep a `required` level from being guessed at.

    It is an agent's text and the owner has not read it. The id is where that is
    said, because the id is what every audit row, fact row and cache key written
    under it carries: `a_fact.unratified.folder-levels.2026-09-04`. Ratifying it is
    recording the text and renaming the id, and both are the owner's. Choosing which
    of the two files is in force is a policy, which is why it is chosen here.
    """
    a_fact_row()
    template_id = A_FACT_ROW[0]
    template, response_schema, shaping_policy = draft_bytes(template_id)
    return PromptDefinition(
        template_id=template_id,
        template_bytes=template,
        response_schema_bytes=response_schema,
        call_site=A_FACT,
        call_site_version="1",
        # THE ROW'S WORD. `planning/82-FACT-PROMPT-DRAFT.md` §0 records the owner
        # ratifying this text; the row is where that is written down now, and
        # `a_fact_row` has already refused a row that does not carry it.
        ratified=draft_status(template_id) in STATUS_APPLIES,
        shaping_policy_bytes=shaping_policy)


def situation_prompt() -> PromptDefinition:
    """The text site G asks under. Composed HERE, on `observe_prompt`'s pattern.

    `104` §17.1's third wall. The bytes come through `SITUATION_ROW`, a manifest
    row, exactly as site A's and the observe sites' do: `draft_bytes` resolves the
    id through the packet and verifies each of the three files against the digest
    recorded there, so this function picks an id and a version and reads nothing
    else.

    **`ratified` IS THE ROW'S WORD AND NOT A LITERAL HERE**, which is why this
    follows `observe_prompt` rather than `a_fact_prompt`: `a_fact_row` REFUSES a row
    that is not applying, because site A applying nothing is a broken run. Site G
    asking and recording is a legitimate state -- it is what every observe site does
    -- so an unratified row leaves `ratified` false and the site records its answer
    without acting on it. The day the row is ratified the site starts applying and
    no line of this function changes.

    **`ratified_local` counts as ratified here and not at the locality gate.** This
    field is "act on the answer", which a local run may do; the gate is "these bytes
    may leave the device", which they may not. `observe_locality_permits` is the
    other half and site G is subject to it.
    """
    template_id, candidate = SITUATION_ROW
    # THE PAIR, RESOLVED BEFORE ANYTHING IS READ. `prompt_library.a_fact_row` is
    # the one reader that resolves a row by id AND candidate; it is named for site
    # A's glossary arms and it is a general reader, so site G uses it rather than a
    # second one. The two situation candidates carry different ids today, so the id
    # alone would resolve -- naming the candidate as well is what makes re-pointing
    # this site a change to `SITUATION_ROW` and never a change the manifest makes
    # on its own.
    prompt_library_a_fact_row(template_id, candidate)
    template, response_schema, shaping_policy = draft_bytes(template_id)
    return PromptDefinition(
        template_id=template_id,
        template_bytes=template,
        response_schema_bytes=response_schema,
        call_site=G_SITUATION_SENSITIVITY,
        call_site_version="1",
        ratified=draft_status(template_id) in STATUS_APPLIES,
        shaping_policy_bytes=shaping_policy)


#: The consent option the owner's ruling answers with. Spelled here for the
#: reason `review_surface.consent_surface.OPTION_SENTENCES` spells the four --
#: P7 publishes the tuple and no constant per member -- and checked against P7's
#: closed set at import so a rename upstream is an ImportError here.
STANDING_LOCAL_CONSENT: str = "local_model"
if STANDING_LOCAL_CONSENT not in CONSENT_OPTIONS:
    raise ImportError(
        f"{STANDING_LOCAL_CONSENT!r} is not one of P7's consent options "
        f"{CONSENT_OPTIONS}; the owner's standing ruling names an option that "
        f"no longer exists")


def standing_consent_grants(scan_run_id: str) -> tuple[tuple[str, str], ...]:
    """The owner's ruling of 9 Sep 2026 (`104` §18.7), recorded as the consent it is.

    §8.4's door asks the person before any model reads text from a file entered
    into protected state: with no grant for the file's corpus area the gate
    answers `NeedsConsent`, the four options go to the review screen, and --
    since no command-line path answers a consent request -- the file waits
    there for ever. That is what the owner's protected files did on every run,
    and the owner answered the question in session, asked twice and confirmed:
    protected material reaches the LOCAL model, on this machine, and never the
    cloud. "Allow a local model to read this text" is that answer in P7's own
    vocabulary, so the run's policy carries it as a grant over the run's one
    corpus area -- the scan (`fact_call_authorities` names the scan as the scope
    for the same reason) -- and the door releases to a local target what it
    would otherwise have asked about.

    Only the local option. `grant_authorizes("local_model", "cloud")` is False,
    so nothing here widens a cloud release: `protected_cloud_denies` still
    refuses a protected file every cloud target under this deployment's modes,
    and a cloud grant is still the person's to give on the screen.
    """
    return ((scan_run_id, STANDING_LOCAL_CONSENT),)


def model_route_permitted(conn: sqlite3.Connection, *, locality: str,
                          unclassified_permits_local: bool,
                          operation_mode: str):
    """§8.4 as `FactResolver` asks it: may THIS file's route reach a model at all?

    Two files never may, and the resolver's own docstring says why the answer
    belongs here rather than at the door: "a handling class that forbids the model
    route is a PROHIBITION, and a file that may never reach a model is not a file
    waiting for budget to free up. Reporting it as a deferral would promise work
    that will never be done." A `False` here writes an `unresolved` row per pending
    field reading `privacy_withheld`, spends no budget, and mints no release.

    * **Unclassified.** `resolve_class(None)` is `unreadable_unclassified` and
      `privacy.denial.unclassified_denies` refuses every cloud release of one
      unconditionally. This is the common case on a real folder and it is not a
      defect in the gate: measured on the owner's own 54-file slice, the safety
      detector reached a verdict about 9 files and abstained on 45, so 45 files
      have no classification and no route. The remedy the design already has is
      the person's -- `Detector` takes `settled_by_user` and P15's `--answer`
      feeds it -- and whether a file the detector examined and did not flag should
      instead be `personal_non_sensitive` is a decision with a test standing on it
      (`tests/test_cli.py::test_the_cli_does_not_invent_a_classification...`), so
      it is NOT taken here.
    * **Protected.** §8.4 keeps protected material out of cloud prompts by default,
      and this deployment runs `hybrid`, under which `protected_cloud_denies`
      refuses it with no carve-out at all. Barred here so the refusal is recorded
      against the file rather than discovered at the door -- the same posture
      `placement_inputs` takes when it abstains rather than asking.
    """
    store = ClassificationStore(conn)

    def permitted(file_id: str) -> bool:
        row = get_file(conn, file_id)
        if row is None:
            return False
        record = store.current(file_id, row["content_hash"])
        # UNCLASSIFIED IS NOT UNREADABLE, AND THE RUN IS WHY. The premise this
        # refused on -- "an unclassified file is one nothing has read successfully"
        # -- was measured false on the owner's own corpus on 2026-09-05: 95 of 199
        # files carried no classification, EVERY ONE of them had evidence, and they
        # are ordinary lecture PDFs, `.py` files and a club logo. All 95 were
        # refused the model with `privacy_withheld`, which is 57% of the corpus
        # never reaching the engine that decides where files go.
        #
        # `resolve_class(None)` is still `unreadable_unclassified` and P7 is right
        # to spell it that way: it is the name for "no record", and P11 reads it to
        # say `blocked_pending_user`. What was wrong is this deployment treating
        # that name as a finding about the BYTES. The detector abstaining is a
        # sentence about the detector.
        #
        # No second definition of "was read" is invented here, because
        # `model_facts` already holds one: it declines to build a call with
        # "nothing releasable -- every observation is in an always-local zone, is
        # unbounded, or was signalled sensitive, so the dossier would be empty and
        # the model would be asked to answer from nothing". A file nothing read has
        # no releasable observation and therefore still costs no call. Permitting
        # here and refusing there keeps one definition rather than two that drift.
        #
        # PROTECTED IS UNTOUCHED. §8.4 keeps protected material out of cloud
        # prompts with no carve-out under `hybrid`, and the standing rule is
        # stricter still: marked and counted, never opened. That is the branch
        # below, and the widening above must never reach it -- which is why a file
        # WITH a record still answers `not record.protected`.
        if record is None:
            # `104` R-02, AND THE PREDICATE IS THE GATE'S OWN. This answered `True`
            # for every locality, so on a cloud target the route counted a file as
            # routed that `Gate.release` then refused -- 19 withheld at the route
            # against 149 stopped at the gate on the owner's 199 files, and the
            # scoreboard read the route's number as files that reached a model.
            #
            # `unclassified_denies` is CALLED rather than reproduced. A second
            # spelling of the gate's rule beside the gate's rule is exactly how the
            # two came to disagree, and a copy would drift again the first time P7
            # changed its mind -- which it has done twice this month.
            return not unclassified_denies(
                locality=locality,
                local_calls_on_unclassified=unclassified_permits_local)
        # PROTECTED REACHES THE LOCAL MODEL ONLY -- the owner's ruling of 9 Sep
        # 2026 (`104` §18.7), asked twice and confirmed. Until that day this
        # route barred a protected file on EVERY locality while the gate's own
        # rule, `protected_cloud_denies`, bars it from the cloud alone; the route
        # was stricter than the door, which is the safe direction, and it was
        # also 100% of the protected files never reaching the engine that decides
        # where files go. The owner's word: files should not be refused; make
        # sure the necessary information is processed and used.
        #
        # THE GATE'S RULE IS CALLED, NOT COPIED, exactly as the unclassified
        # branch above calls `unclassified_denies`: one spelling of "may a
        # protected file reach this target", at the door, and the route asks it.
        # Under this deployment's `hybrid` mode that rule has no carve-out, so a
        # cloud target is refused whatever scope is named; the empty scope here
        # is "no grant", which is the route being no wider than the door.
        #
        # What this does NOT change: a protected file is still marked and counted
        # on its own line in every report (`no_route` at site G becomes the
        # cloud-refused count on a cloud run, not a silence); it is still never
        # sent to the cloud; and it is still never FILED automatically -- §7.3's
        # placement rule at `placement_inputs` is a separate question about
        # moving, and it stands. Protected CONTAINERS (`.app` bundles, system
        # items; `scan_agent.exclusion.is_protected_container`) are a different
        # mechanism again: the walk creates no `files` row inside one, so nothing
        # here can route them, and nothing should.
        return not protected_cloud_denies(
            protected=record.protected, locality=locality,
            operation_mode=operation_mode, scope="", granted_scopes=())

    return permitted


def _route_locality(route_for, file_id: str) -> str:
    """Where THIS file's readings are going, for the release rules that ask.

    `104` R-159: a neighbour's reading leaves by the door this file's own readings
    leave by, so the release question is asked with the same answer to "where is
    this going" -- which since `104` §17.13 ruling 3 is a per-file answer.

    A file with no destination cannot reach here: `model_facts` asks the route
    before it asks for context, and `FactResolver` asks before that. The refusal
    names what went wrong rather than defaulting to a locality, because defaulting
    to `local` would understate the release and defaulting to `cloud` would
    overstate it, and both are decided elsewhere.
    """
    chosen = route_for(file_id)
    if chosen is None:
        raise ValueError(
            f"file {file_id!r} is routed to no model, so there is no destination "
            f"for its neighbours' readings to be released to. Nothing should have "
            f"asked for them")
    return chosen[1].locality


def site_has_a_destination(conn: sqlite3.Connection, routing: TierRouting,
                           call_site: str, *,
                           operation_mode: str = OPERATION_MODE) -> bool:
    """Whether this site has any model it may use at all, before any file is asked.

    The observe sites turn themselves off when their tier resolves to nowhere they
    are allowed to send, and until `104` §17.13 ruling 3 that was one question --
    `observe_locality_permits(site, routing.locality_for(site))`. With two clients
    behind one tier it is two: a site whose text may not cross the internet still
    has a destination if this deployment installed a local model. Asked through the
    same candidate list `target_for` builds, so "the site is on" and "this file has
    a route" cannot answer from two different readings of the same configuration.
    """
    return bool(_route_candidates(conn, routing, call_site,
                                  operation_mode=operation_mode))


def target_for(conn: sqlite3.Connection, routing: TierRouting, call_site: str,
               *, operation_mode: str = OPERATION_MODE):
    """WHICH MODEL ANSWERS ABOUT EACH FILE at this site. `104` §17.13 ruling 3.

    The owner's words: *"a protected file, and an unclassified file until site G
    classifies it, goes to the local model; everything else goes to the cloud"* --
    and no call at all where neither destination is permitted. This is where that
    becomes a callable: `callable(file_id) -> (client, target) | None`.

    **It asks `model_route_permitted` for CLOUD first, then LOCAL**, which is the
    order the ruling reads in and the order that puts the wider capability first.
    The predicate is the one the gate is built from, called and never respelled: a
    second spelling of the gate's rule beside the gate's rule is how the two came
    to disagree once already (`104` R-02), and this one decides where bytes go.

    **A DESTINATION IS A CANDIDATE ONLY IF THE ROUTING ACTUALLY HAS ONE THERE.**
    `TierRouting.route_for` answers with the single configured client when only one
    kind is configured, whichever way it is asked, so the LOCALITY of what comes
    back is checked against the locality being asked about. Without that check, a
    deployment with a cloud key and no local model would send a file the cloud may
    not see to the cloud, under the name of the local route. With the check it gets
    `None`, which is exactly what it got before this function existed.

    **AND ONLY IF THIS SITE'S TEXT MAY CROSS THE INTERNET.** `observe_locality_
    permits` is asked about the cloud candidate for the same reason it is asked
    everywhere else: sites B, D and E run under unratified drafts, C under
    `ratified_local`, and G under an unratified one, so their bytes stay on this
    machine whatever a file's classification says. Only site A's text is
    `ratified`. Without this the two-client routing would hand every observe site a
    cloud client and either send a person's dossier under a prompt nobody approved
    or -- where the site checks first -- turn the site off entirely, which is a
    coverage loss dressed as a safety measure.

    **`operation_mode` DEFAULTS TO THE LOCAL-FIRST FLOOR**, which is what
    `operation_mode_for` returns when nobody has decided: absent means refuse, and
    a caller that has not said this folder's consent permits sending gets a route
    that does not send. The cost of the default being wrong is a local answer
    instead of a cloud one; the cost of the other default is a person's file
    leaving their device under a permission they never gave.

    The predicates are built ONCE, here, and only the per-file question is asked in
    the loop: the routing's pairs do not vary by file and only the permission does.

    `None` for a file no destination permits. `FactResolver` reads that through its
    own `model_route_permitted`, bound to this same callable, and writes one
    `unresolved` row per pending field reading `privacy_withheld` -- so the route's
    answer and the destination are one answer rather than two that can disagree.
    """
    candidates = _route_candidates(conn, routing, call_site,
                                   operation_mode=operation_mode)

    def chosen(file_id: str):
        for permitted, pair in candidates:
            if permitted(file_id):
                return pair
        return None

    return chosen


def _route_candidates(conn: sqlite3.Connection, routing: TierRouting,
                      call_site: str, *, operation_mode: str):
    """The destinations this site really has, widest first, each with its gate.

    Built once per site because the routing's pairs do not vary by file and only
    the permission does. Cloud is first because the ruling reads that way and
    because it is the wider capability; a candidate that survives all three checks
    here is a destination a file can actually be sent to.

    **THE THREE CHECKS, and each is a different question.** Does the routing have a
    client THERE -- `route_for` answers with the one configured client when only
    one kind is configured, so the returned target's locality is what says whether
    the destination exists. May this SITE's text go there -- `observe_locality_
    permits`, which refuses the cloud to every draft. And does this RUN's mode
    permit it -- `mode_forbids`, the gate's own rule, called and not respelled.

    **The mode check is not redundant with the gate, and leaving it out starved a
    corpus.** `--enable-cloud` unset is `offline`, and under `offline` the gate
    refuses every cloud release. Without this line a classified, unprotected file
    would be routed to the cloud client, reach the gate and be denied -- no answer
    at all, where the same file used to be answered by the local model. Cost:
    every classified file in a run nobody enabled the cloud for. The route is asked
    the same question the gate will answer, which is `104` R-02's whole rule.
    """
    candidates = []
    for locality, cloud_permitted in ((CLOUD, True), (LOCAL, False)):
        client, target = routing.route_for(
            call_site, cloud_permitted=cloud_permitted)
        if target.locality != locality:
            continue
        if locality == CLOUD and not observe_locality_permits(call_site, CLOUD):
            continue
        if mode_forbids(operation_mode, locality):
            continue
        candidates.append((
            model_route_permitted(
                conn, locality=locality,
                unclassified_permits_local=UNCLASSIFIED_PERMITS_LOCAL,
                operation_mode=operation_mode),
            (client, target)))
    return candidates


def site_destination(routing: TierRouting, call_site: str):
    """The one pair a MANY-FILE site may use, or `None`. `104` §17.13 ruling 3.

    **Why sites B and E do not get a per-file route.** A group call and a template
    call each carry readings from several files under ONE `ModelCallAuthorities`,
    built before P9 has formed a single group -- so there is one client for every
    group of the run and no file to ask about when it is chosen. The rule for a
    call that carries several files is that its destination must be one EVERY
    member may use: cloud only if every member is cloud-permitted, else local.

    **This deployment satisfies that rule by construction rather than by a fold,
    and the difference is coverage.** B's and E's texts are unratified, so
    `observe_locality_permits` refuses them the cloud whatever any file's
    classification says, and the only destination either site has is the model on
    this machine. Folding the per-file gate over the run's files instead would
    refuse the WHOLE call the moment one protected file appeared anywhere in the
    corpus -- taking every other member's observe row with it -- and it would buy
    no safety, because a protected member's readings are already refused one by one
    by `Gate.release` when the dossier is built. The bar for an individual file
    stays where it already holds; what is decided here is the destination.

    The day either text is ratified this stops being enough, and the fold becomes
    real work: the members are named on the request, so it belongs at
    `observed_run_call`, where a group's own file ids are in hand.

    `None` when the site has no destination its own text permits, which is a
    deployment with a cloud key and no local model -- correctly configured, and it
    simply does not run the observe sites.
    """
    for cloud_permitted in (True, False):
        client, target = routing.route_for(
            call_site, cloud_permitted=cloud_permitted)
        if observe_locality_permits(call_site, target.locality):
            return client, target
    return None


def fact_call_authorities(conn: sqlite3.Connection, *, routing: TierRouting,
                          scan_run_id: str, corpus_file_count: int,
                          policy_version: str, wire_handle_key: bytes,
                          schema: str, folder_levels: tuple[FolderLevel, ...],
                          user_id: str, now,
                          deferred_readings: tuple[str, ...] = (),
                          anchor_levels: tuple[FolderLevel, ...] = (),
                          usage_recorder: object | None = None,
                          operation_mode: str = OPERATION_MODE,
                          corpus_roots: Sequence[Path] = (),
                          on_result=None) -> FactCallAuthorities:
    """Everything one A_fact call needs, chosen here and nowhere else.

    `model_facts` authors none of these and P8 authors none of them either. The two
    that are this deployment's answer to a question both parts filed back to the
    other are `normalize_for_model` and `contradicts_stronger` (C-5); the rest are
    numbers, a clock, a key and a client.

    **The activation signal is the SITUATION the person named.** `active_field_
    allowlist` is §3.5's closed vocabulary and it is empty beyond the six universal
    fields unless a domain schema activates. P6 authors no signal -- "Which evidence
    activates which domain is unauthored" -- and this command already asked the
    person which situation they are in and resolved it to a schema through the
    template library. Answering `True` for that one schema is the same answer P9's
    `signal_evaluator_for` already gives, from the same source, and it is the
    difference between offering the model `school`, `instructor`, `work_type` and
    offering it `file_type` and `language`.

    **The folder levels are the template library's answer for the SITUATION**, read
    by `production.folder_levels_for` and passed in with no default. The allowlist
    above decides which fields the model MAY propose; it says nothing about which of
    them this person's chosen situation builds folders out of. Measured over 199
    real files with the levels absent: 59 `file_type`, 34 `authored_by`, 19
    `creation_date` and ONE `work_type` -- and `work_type` is a required level, so
    the file it decides the place for stayed unplaced. The library has held the
    answer all along, on the same applicability row `schema_for_situation` already
    reads: an ordered list of `(field, label, requirement)` with the labels written
    for a person -- "My school", "Semester", "Course", "Kind of work".

    Nothing about the person's files is added to them. A level is the same on every
    file in the situation, which is what makes it safe to send at all: §8.4's
    always-local set has no route into a library constant, and an example drawn from
    the corpus -- which would have one -- is not offered.

    **`anchor_levels` is the second half of that answer** (`105` §14.4, `104`
    R-131 with R-102). `folder_levels` above is what EVERY file of the situation is
    asked; this is what only an ANCHOR is asked -- the school level, withheld from
    every file by `104` §11.2 step 2 and restored by the owner's ruling to the
    files whose own settled kind is one of `SCHOOL_ANCHOR_KINDS`. Empty is the
    state R-102 measured (nothing writes a `school` fact and no corpus grows a
    school level), so a caller that supplies none keeps that behaviour rather than
    starting to ask by omission.

    The protected half of §14.4 is `model_route_permitted`, CALLED here rather than
    respelled: the same predicate the resolver's route is built from, so a
    protected anchor is refused the question by the one rule that already refuses
    it the call.

    **The gate's span classifier declines**, and that is the honest binding rather
    than a stub. P7's SPEC files identifier classes and the redaction transform
    under *Deferred* and nothing in `src/` classifies a span into one, so a
    classifier that claimed to would be inventing the vocabulary §8.4 says P7 does
    not own. What holds the always-local set is not that function: it is
    `releasable_observations`' zone and whole-document exclusions, P5's
    `sensitive_observation_keys`, the file-level bar above, and the gate's own
    `_precheck_items`.
    """
    # ONE CALLABLE FOR THE WHOLE OF SITE A, built once here: the authorities'
    # route, the anchor readings' locality and the anchor bar below all read it,
    # and `model_fact_resolver` binds its own `model_route_permitted` to it, so the
    # route's answer and the destination cannot be two answers (`104` R-02).
    route_for = target_for(conn, routing, A_FACT,
                           operation_mode=operation_mode)
    return FactCallAuthorities(
        gate=Gate(
            conn, store=ClassificationStore(conn), plan_version=PLAN_VERSION,
            classifier=lambda value, *, context_before=None, context_after=None: None,
            transform=lambda value, *, identifier_class: "[redacted]",
            # §8.4's Open question 5, and the ONE answer to it (`104` §15.3,
            # R-121). The value is not restated here: it is
            # `privacy.denial.UNCLASSIFIED_PERMITS_LOCAL`, the same name P11's
            # `may_assemble_dossier` reads and the same name the route below is
            # given, so the gate and the two callers ahead of it cannot answer
            # differently. It used to be a literal at this call.
            #
            # The answer it replaces was reasoned from a premise the run
            # disproved: "an unclassified file is one nothing has read
            # successfully". 95 of the owner's 199 files were unclassified and
            # every one had evidence. `no_safety_evidence_denies` answers the
            # sibling question the same way, permitting local unconditionally.
            #
            # Nothing leaves the device on this branch: `unclassified_denies`
            # refuses every CLOUD release of an unclassified file unconditionally
            # and this flag cannot reach that decision.
            unclassified_permits_local=UNCLASSIFIED_PERMITS_LOCAL,
            # Open question 3 -- what a "corpus area" is -- is unanswered, so the
            # scope is the SCAN. It is internal, it never leaves the device, and it
            # is the one boundary this run can name truthfully.
            scope_for=lambda file_id: scan_run_id,
            files_in_scope=lambda scope: tuple(
                file_id for file_id, _hash in corpus_roster(conn, scan_run_id)),
            # M9's backstop, supplied at last (`103` C7, `104` SF-5). `Gate` takes
            # this with a `None` default because "P7 owns no tokenizer and inventing
            # one would invent a number", and with nothing measuring,
            # `over_dossier_ceiling` never ran -- so the stored ceiling could not
            # have denied anything however it was set. The measurement is this
            # deployment's and it says what it counts: characters, used as an upper
            # bound on tokens, which errs towards refusing and never towards
            # sending. `model_facts.dossier_tokens` carries the reasoning.
            measure_tokens=measure_released_tokens,
            # `104` §18.7. The folders this run was asked to scan, handed to the
            # door so a `path`-zone value can be made relative to one of them before
            # a CLOUD release. The SOURCES and not the candidate roots: §1.1's roots
            # are context, and `scan.py` writes no `files` row from one, so a root
            # here would be a prefix no released value can carry.
            corpus_roots=corpus_roots,
            component_version=COMPONENT_VERSION, now=now, user_id=user_id),
        # NO SINGLE PAIR, because site A no longer has one destination
        # (`104` §17.13 ruling 3). `target_for` answers per file -- the cloud model
        # where the cloud gate permits the file, the local one where it does not,
        # `None` where neither does -- and `FactCallAuthorities` refuses to hold
        # both spellings at once, so this is the whole answer.
        model_client=None,
        prompt=a_fact_prompt(),
        model_target=None,
        route_for=route_for,
        activation_signals=ActivationSignals(signals=(
            ActivationSignal(schema_id=schema, activates=lambda facts: True),)),
        folder_levels=folder_levels,
        # §3.6 check 3's per-field alias tables are a Deferred row and this
        # deployment authors none, so the mapping is empty and `normalize_for_model`
        # below is what actually canonicalises. Injected empty rather than omitted:
        # `FactRequest` carries it and a caller that skipped it would be choosing
        # for P6.
        normalizers={},
        # THE LIBRARY'S SEED, THEN THIS PERSON'S OWN ANSWERS (`104` §18.2 gap 3).
        # `normalize_for_model` is still what canonicalises and is still asked
        # first; what the closure adds is the vocabulary the person built by
        # confirming and renaming proposals, which lives in their database and
        # nowhere in this file. `00`:298 is the sentence it pays.
        normalize=normalize_with_the_persons_own_values(conn),
        # Check 3's second question (`104` R-98, widened by `104` §18.2 gap 3).
        # Without it, a course that names itself in words instead of a code is
        # refused rather than offered: ten of ten `subject` answers on the owner's
        # coursework files were, and on r15 `term` and `work_type` were most of the
        # largest rejection class there was.
        normalize_for_review=normalize_for_review,
        contradicts=contradicts_stronger,
        evidence_resolver=_stored_value_of(conn),
        scan_budget=ScanBudget(
            scan_id=scan_run_id, corpus_file_count=corpus_file_count,
            max_calls_per_1000_files=FACT_CALLS_PER_1000_FILES,
            max_estimated_cost=FACT_CALLS_PER_SCAN_CEILING,
            min_calls_per_scan=FACT_MIN_CALLS_PER_SCAN),
        estimated_cost=FACT_CALL_COST, actual_cost=FACT_CALL_COST,
        policy_version=policy_version,
        wire_handle_key=wire_handle_key,
        max_released_observations=FACT_CALL_MAX_RELEASED_OBSERVATIONS,
        max_dossier_tokens=GROUPING_LIMITS.max_dossier_tokens,
        observed_at=now,
        on_result=on_result,
        # `104` R-14, forwarded and not read here for the same reason as the
        # readings below: the composition root owns it and `model_facts` decides
        # what a call does with it.
        usage_recorder=usage_recorder,
        # `104` R-08. The situation's authored readings, forwarded and no more:
        # `model_facts` carries the whole of why they stop at this record rather
        # than reaching the dossier, and the composition root's only job is to read
        # them off the release it already loaded.
        deferred_readings=deferred_readings,
        # `104` R-135. WHICH NEIGHBOURS SPEAK FOR A FILE IS THIS DEPLOYMENT'S ANSWER,
        # which is why it is bound here and not defaulted in `model_facts`: it rests
        # on `SUBJECT_FIELD`, on the corpus's own folders, and on this run's
        # classification records, and P6 and P8 own none of the three. The cap is the
        # same `max_released_observations` the file's own readings are drawn under,
        # because a neighbour's readings are released through the same door.
        #
        # `104` R-159: the locality is the ROUTE'S, read off the same client the
        # target above is read off. A neighbour's reading leaves by the door this
        # file's own readings leave by, so the release question is asked with the
        # same answer to "where is this going".
        anchor_context_for=lambda db, *, file_id, content_hash, fields: (
            anchor_context_observations(
                db, scan_run_id=scan_run_id, file_id=file_id, fields=fields,
                limit=FACT_CALL_MAX_RELEASED_OBSERVATIONS,
                locality=_route_locality(route_for, file_id))),
        # `104` R-145: the same offer in §8.6's preserved-anchors shape, asked only
        # when the lines above do not fit the dossier ceiling. `model_facts` says
        # when; this file says what the shape is.
        anchor_excerpts_for=lambda db, *, file_id, content_hash, fields: (
            anchor_context_observations(
                db, scan_run_id=scan_run_id, file_id=file_id, fields=fields,
                limit=FACT_CALL_MAX_RELEASED_OBSERVATIONS,
                locality=_route_locality(route_for, file_id),
                preserved_anchors=True)),
        # `105` §14.4. Built here because every part of it is this file's: which
        # levels only an anchor is asked, which field says what a file IS, which
        # kinds the shipped release spells as anchors, and the route's own
        # protected bar. `None` when the caller withholds nothing, so a deployment
        # that has not read the ruling asks exactly what it asked before.
        anchor_only=(AnchorOnlyLevels(
            levels=anchor_levels,
            kind_field=WORK_TYPE_FIELD,
            anchor_kinds=SCHOOL_ANCHOR_KINDS,
            # THE ROUTE'S OWN ANSWER, not a second reading of the flag and no
            # longer a second reading of one locality: `route_for` already asked
            # `model_route_permitted` for both, so "may this file reach a model"
            # is "did the route find it a destination" and there is one answer.
            may_reach_a_model=lambda file_id: route_for(file_id) is not None)
            if anchor_levels else None))


def _stored_value_of(conn: sqlite3.Connection):
    """§3.6 check 2's coarse half: does this citation handle still resolve at all?

    `None` is an answer -- `validation._check_citation` reads it as
    `CITATION_NOT_FOUND` -- and it is never the SPAN-matching source: the model was
    shown P7's released (possibly redacted) value, and matching a quotation against
    the raw stored text would accept one the model could not have read.
    """
    def resolve(observation_key: str) -> str | None:
        row = conn.execute(
            "SELECT raw_value FROM evidence WHERE observation_key = ? "
            "AND superseded_by IS NULL", (observation_key,)).fetchone()
        return None if row is None else row["raw_value"]

    return resolve


# --- `104` §17.1's SEVENTH SITE, wired ----------------------------------------


#: §8.7's learning key for a situation answer. The convention `model_facts` sets is
#: `<subject kind>.<what was asked>`; this site asks one question about one file and
#: the shortlist is what makes the question answerable, so the class says both.
SITUATION_PROPOSAL_CLASS: str = "situation.llm_shortlist"


def situation_call_dependencies(fact_authorities, *, allowed_vocabulary,
                                placeable_file_count: int) -> CallDependencies:
    """Site G's authorities for one call. Built off site A's, never beside them.

    **The gate, the key, the costs and the policy version are site A's OBJECTS**,
    on `observe_placement_injections`' rule: a second `Gate` here would be a second
    answer to what may leave this device, and the two would drift on the next
    ruling.

    **The budget is NOT site A's**, for `observe_scan_budget`'s measured reason:
    site A asks one call per file, so on a corpus where every file has an open
    question it spends every slot the run has, and a site drawing from the same
    purse afterwards is starved by it -- which looks exactly like a site nobody
    wired (`104` R-04).

    **`allowed_vocabulary` is this file's shortlist and it is not a field list.**
    At A, B, C and E the vocabulary is a set of field keys or node ids; here it is
    the situations the recognisers raised, with the decline last. `dossier._body`
    builds `field_glossary` from it and finds no meaning for a schema id, which is
    why the ratified prompt tells the model that key is empty at this site.
    """
    return CallDependencies(
        proposal_class=SITUATION_PROPOSAL_CLASS,
        # §8.7's closed scope vocabulary. The subject of a situation verdict is one
        # FILE -- not a group, not a node -- which is also `_SCOPE_BY_SITE`'s answer
        # for this site and the scope the verdict itself carries.
        learning_scope=SCOPE_FILE,
        # Both replaced per call, from the request. Present because `run_call` reads
        # the whole bundle before the first call and a `None` in either refuses
        # every one of them.
        basis_key=SCOPE_FILE,
        learning_subject_id=SCOPE_FILE,
        evidence_resolver=fact_authorities.evidence_resolver,
        # NO BUNDLE, which is site B's answer and is the truthful one here: the
        # validator checks the answer against the shortlist the dossier already
        # carries, and needs no tree, no action set and no catalogue.
        site_dependencies=SiteDependencies(
            fact=None, placement=None, residual=None, template=None),
        # NOT A's `contradicts_stronger`, and the reason is site B's: that function
        # reads `field_key` and `canonical_value` off a P6 fact row, and a situation
        # claim is not one. There is no per-field fact for "this file is coursework"
        # to contradict -- the recogniser's own verdict is an ABSTENTION, which is
        # why the question is being asked -- so the truthful answer is always no.
        contradicts=_no_group_contradiction,
        # One rung. `releasable_observations` fills the offer up to the ceiling
        # before the request is built, so there is no smaller shape of this dossier
        # to fall back to -- the same argument `model_facts` makes at site B.
        unreduced_fits=True, summarized_fits=False, anchors_fit=False,
        split_shard_fits=(), split_shards=(),
        # SITE G'S OWN PURSE, not the observe sites'. `observe_scan_budget` is B's,
        # C's and D's, and this site runs before all three and asks one call per
        # unsettled file -- exactly the shape that starved them the first time
        # (`104` R-131). The rate, the floor and the ceiling are the observe ones,
        # because the question "how many model calls may one scan make about one
        # corpus" has one deployment answer; what differs is the LEDGER.
        scan_budget=situation_scan_budget(
            fact_authorities.scan_budget,
            corpus_file_count=placeable_file_count),
        estimated_cost=fact_authorities.estimated_cost,
        actual_cost=fact_authorities.actual_cost,
        allowed_vocabulary=tuple(allowed_vocabulary),
        # THIS SITE DESIGNS NO FOLDER TREE. `()` is the truthful value and `None`
        # would be a caller who never read the library -- `harness._NONE_OK` is
        # where that distinction is enforced, and the ratified prompt tells the
        # model the key is empty here.
        folder_levels=(),
        policy_version=fact_authorities.policy_version,
        wire_handle_key=fact_authorities.wire_handle_key)


def situation_named_by_verdict(conn: sqlite3.Connection, verdict,
                               allowed_vocabulary) -> str | None:
    """Site G's real resolver: the situation the VALIDATED verdict names.

    `_chosen_node_of`'s restraint, at this site and for its reason. P8 has already
    checked that the answer is on the list (`situation_validation._situation_site`),
    that every citation resolves against what P7 released and that every quoted span
    appears in the released value. A second opinion here would be a rule with no way
    to be reconciled with the first.

    `None` for every answer that is not one named situation -- a decline, an
    unreadable payload, an outcome that did not accept. All of them mean the same
    thing to the caller: leave the file where the rules left it, which is LOCAL.
    The membership test is repeated once here and it is not a second opinion: it is
    the same list, and it is what keeps a payload read out of a verdict this
    deployment mis-addressed from becoming a placement.
    """
    if verdict is None or verdict.outcome not in ACCEPTING_OUTCOMES:
        return None
    payload = _validated_payload(conn, verdict)
    situation = payload.get("situation") if payload else None
    if not isinstance(situation, str) or not situation:
        return None
    if is_decline(situation, decline_word=NONE_OF_THESE):
        return None
    return situation if situation in set(allowed_vocabulary) else None


def restricted_kind_named_by_verdict(conn: sqlite3.Connection, verdict) -> str | None:
    """`104` §18.7 S2 / §18.11: the restricted document KIND the validated verdict
    names, or `None` when it names none.

    The second question site G's v2 text asks, read the way the first is: off the
    payload of the claim the verdict judged, at the composition root, by whoever
    supplied the prompt. `None` here means "the model named no restricted kind" --
    the schema makes the field optional and the template says to leave it out for
    a file that is none of the ten -- and it is `privacy_class_for`'s `()` (assessed,
    ordinary), NOT its `None` (never assessed): the caller passes the empty tuple,
    because a file the local model looked at and found to be no restricted kind is
    §13.3's "on neither list is ordinary", and calling it pending would refuse the
    cloud to every file the recogniser cleared.

    The membership test is the vocabulary's own (`RESTRICTED_KINDS`) and it is not a
    second opinion: the schema's enum is the same ten, so a value outside them is a
    payload this deployment mis-addressed rather than a kind, and it names nothing.
    """
    if verdict is None or verdict.outcome not in ACCEPTING_OUTCOMES:
        return None
    payload = _validated_payload(conn, verdict)
    kind = payload.get("restricted_kind") if payload else None
    if not isinstance(kind, str) or kind not in RESTRICTED_KINDS:
        return None
    return kind


def situation_classification(question, schema_id: str, *, observed_at: str,
                             restricted_kind: str | None = None,
                             held: bool = False,
                             handling_for=HANDLING_POLICY) -> ClassificationRecord:
    """`104` §17.1's second wall, spent: one model verdict, written down truthfully.

    **THE BASIS IS THE MODEL'S AND THE CLASS IS THE DEPLOYMENT'S**, and keeping
    those apart is the whole design of this record. `basis` says WHO concluded that
    this file is part of this situation: a model on this device, answering the
    situation question. `handling_class` and `protected` say what THIS DEPLOYMENT
    does with a file of that situation, and they are read off `HANDLING_POLICY` --
    the same table the detector's own records are written from -- so a model naming
    `medical` produces exactly the handling a detector naming `medical` produces.
    The model is not asked what handling class to apply and could not be trusted
    with the question; it is asked which situation, and the deployment already has
    an answer for each one.

    **The citations are the recogniser's**, which is the honest set: they are the
    observations the shortlist was raised from, they resolve against P4's live table
    for this file version, and `test_a_tie_is_a_question_for_the_model` measures
    that. The model's own citation is checked by P8 and recorded on the verdict;
    what this record cites is what the CLASSIFICATION rests on.

    `llm_supported` is P4's own word for a fact a model supported, and it ranks
    below `user_confirmed`, `direct` and `validated` -- so a later record from the
    person, or from an extractor reading the file's own words, supersedes this one
    rather than being refused by it.

    **`held` IS THE HOLD THE RULES HAD ALREADY TAKEN, and it only ever ADDS
    protection (`104` §18 gap 24, the owner's ruling of 10 Sep).** `llm_supported`
    outranks `possible`, so this record supersedes the detector's own the moment
    it is assigned -- which means a verdict naming an ORDINARY situation lifts a
    `safety_domain` hold, and that is exactly what the ruling asks for. What it
    must NOT do is lift a hold the verdict did not contradict: a model that names
    an ordinary situation AND one of `105` §13.3's ten restricted kinds has said
    the file is a passport in a coursework folder, and `privacy_class_for`'s
    precedence already says such a file is protected. `HANDLING_POLICY` answers
    for the SITUATION and knows nothing about the kind, so it would drop the flag
    to `False` and the file would be released to placement -- the one direction
    this is not allowed to move. The hold therefore stands wherever a kind is
    named, and a file this pass was never holding is untouched by the argument.
    """
    handling = handling_for[schema_id]
    return ClassificationRecord(
        file_id=question.file_id,
        content_hash=question.content_hash,
        handling_class=handling.handling_class,
        protected=handling.protected or (held and restricted_kind is not None),
        basis=LOCAL_MODEL_SITUATION,
        evidence_refs=tuple(question.evidence_refs),
        reliability_state=LLM_SUPPORTED,
        observed_at=observed_at,
        # `104` §18.7 S2 / §18.11 (9 Sep 2026): THE KIND IS THE MODEL'S AND THE
        # CLASS IS THE VOCABULARY'S, on the same terms as the two lines above it.
        # The local model names which of `105` §13.3's ten restricted kinds the
        # file is, or none; `privacy_class_for` turns that into the class with the
        # owner's precedence (protected over always-local over ordinary). The
        # empty tuple is deliberate: this file WAS assessed, so "no restricted
        # kind" is ordinary and never pending -- §14.3's own distinction.
        privacy_class=privacy_class_for(
            () if restricted_kind is None else (restricted_kind,)))


@dataclasses.dataclass(frozen=True, slots=True)
class PrecautionHolds:
    """WHAT BECAME OF THE HOLDS THE RULES TOOK, over the files site G walked.

    `104` §18 gap 24 and the owner's ruling of 10 Sep: the protected hold must be
    "a little more sure than now". Site G is the product's kind recogniser, so the
    files the term detector's precaution marked are exactly the files whose hold
    the local model is asked to confirm or release -- and a person is owed the
    four numbers that say what happened, because on r19 the answer was 16 marks,
    5 of them right, and no line on any screen said so.

    **THESE DO NOT PARTITION THE ROSTER, and that is why they are their own
    record.** `SituationPass`'s six counters do: every file the pass walked lands
    in exactly one of them, and `_print_situation_pass` prints an arithmetic a
    person can check against the total. A held file is ALSO in one of those six --
    it was asked, or it was not, for one of the six reasons -- so adding these
    beside them would break the sum on the screen. `released`, `confirmed` and
    `still_held` partition `held`, and nothing else.
    """

    #: Files this pass found under a `safety_domain` hold when it reached them.
    #: The detector's precaution wrote the row; this is the count of the files it
    #: wrote it for, over this run's roster.
    held: int
    #: Holds the local model LIFTED: it named an ordinary situation, its citations
    #: resolved, P8 accepted the claim, and it named no restricted kind. The row it
    #: wrote supersedes the precaution's, so the file is ordinary for every later
    #: pass of this run -- site A's route and placement included.
    released: int
    #: Holds the local model AGREED WITH: it named one of `00`'s four safety
    #: domains, or it named one of `105` §13.3's ten restricted kinds. G's own
    #: protected row supersedes the precaution's, so the record shows the model
    #: agreed rather than showing only that the rules had guessed.
    confirmed: int
    #: Holds that STAND because nothing lifted them: the model declined, or the
    #: check refused its answer, or the call failed, or the file was never askable
    #: at all. Silence never lifts a hold, and this is the count of the silences.
    still_held: int


@dataclasses.dataclass(frozen=True, slots=True)
class SituationPass:
    """What site G left behind, counted. Every field is a number a report can print.

    `named` is the answer this pass exists to produce: the file's OWN situation,
    where a model named one. Everything else says what happened to the files it did
    not name, because `104` §17.2 is what a number with no provenance costs.
    """

    #: file_id -> the schema id a model named for it, validated and recorded.
    named: dict
    #: Files the recognisers settled without a model. Not asked, and rightly.
    settled: int
    #: Files with an abstention and no candidate at all -- `no_evidence` with no
    #: semantic recogniser behind it. `NothingToAsk`, and 60 of the owner's 112
    #: abstentions on the measured corpus.
    nothing_to_ask: int
    #: Files with a shortlist and no releasable reading. A question `00`:42 permits
    #: no answer to.
    nothing_to_read: int
    #: Files a model was asked about and declined to name, or whose answer P8 did
    #: not accept. `00`: correct abstention is a successful outcome, and either way
    #: the file stays where the rules left it -- which is local.
    declined: int
    #: Files no model in this run may be asked about at all (`104` §17.13 ruling
    #: 3): protected material, which the route bars on every locality. COUNTED and
    #: not folded into `nothing_to_read`, because the two are different facts about
    #: a file -- one had nothing to say, the other was never allowed to be asked --
    #: and the standing rule is that protected material is marked and counted,
    #: never silently omitted.
    no_route: int
    #: `104` §18 gap 24. What became of the holds the rules had taken, over the
    #: same walk. A RECORD and not four more counters, because the six above
    #: partition the roster and these three partition `held` -- see
    #: `PrecautionHolds`, and `_print_situation_pass`, which prints them as their
    #: own block so the arithmetic on the screen stays checkable.
    holds: PrecautionHolds


#: THE PASS THAT DID NOT RUN, and it is a value rather than a `None` for the
#: reason every count in `SituationPass` exists: a run where site G was not asked
#: and a run where it was asked and named nothing must not read the same
#: downstream. Both leave every file under the run's own `--situation`; only one
#: of them means the model was consulted.
_NOTHING_ASKED: "SituationPass"


class ProtectedFileOfferedACloudTarget(RuntimeError):
    """A file the rules are holding was routed somewhere off this device.

    `104` §18.7 and the standing rule: protected material reaches the LOCAL model
    only, opened on this machine for it and never sent to the cloud. `target_for`
    already asks `model_route_permitted`, which asks the gate's own
    `protected_cloud_denies`, so this is unreachable through a correctly built
    routing -- and it RAISES rather than asserts for §18 S5's reason: an invariant
    that disappears under `-O` is an invariant that is not enforced. The bytes of
    somebody's passport are what is on the other side of it.
    """


def ask_the_situation(conn: sqlite3.Connection, *, roster, explain,
                      precaution_of, fact_authorities, routing: TierRouting,
                      prompt, now, user_id: str,
                      component_version: str = COMPONENT_VERSION,
                      semantic_of=None) -> SituationPass:
    """`104` §17.9's defect, addressed: each file asked about ITS OWN situation.

    **WHAT THIS IS FOR, and the register got it wrong once.** The earlier account
    was that a recogniser tie makes a file unclassified, the gate refuses an
    unclassified file, and the file is never asked. On a LOCAL target that is false
    at the third step: `privacy.denial.UNCLASSIFIED_PERMITS_LOCAL` is `True` and
    `no_safety_evidence_denies` permits local unconditionally. Nothing was silent.
    What actually happens is that `fact_call_authorities` builds site A's activation
    as one signal for the run\'s single `--situation`, firing for every file -- so a
    vaccination record is asked which course it belongs to. That is R-23, and this
    pass is what puts each file\'s own question instead.

    **IT RUNS BEFORE THE FACT PASS AND ITS ANSWER IS WHAT THE FACT PASS USES.** A
    situation named after the fields were asked would be a situation nothing acts
    on -- the schema decides the allowlist, the folder levels and the readings, and
    all three are chosen when the resolver is built.

    **A FILE THIS PASS DOES NOT NAME IS NOT MOVED.** It stays under the run\'s own
    `--situation`, exactly as it was before this pass existed, and it stays LOCAL:
    a wrong "ordinary" is what sends somebody\'s medical record away, and every
    outcome here that is not one accepted, cited, on-the-list answer leads to the
    same place.

    **AND SINCE `104` §18 gap 24, THE HOLD THE RULES TOOK IS PART OF THE
    QUESTION.** `precaution_of` is `Detector.precaution_report` -- INJECTED, on
    `explain`'s own terms, because the rules are another part's and this pass
    re-derives none of them. Where it answers, three things follow, and each is
    the owner's ruling of 10 Sep read literally:

    * the file is ASKED, and the hold is what makes the asking accountable. A
      hold is a reason to put the question, never a reason to skip it: the whole
      point of asking is that the rules were only a little sure. Three doors can
      still turn a file away here and only two of them can turn a HELD one away --
      no releasable reading (`00`:42 permits no answer to a question with no
      evidence) and no local target -- and both must stay shut, so a held file
      that goes through either is counted as a hold that STANDS and is said out
      loud rather than disappearing into a bucket shared with ordinary files. It
      is asked on the LOCAL route and there is no other: `route_for` refuses a
      cloud target for a protected file and `ProtectedFileOfferedACloudTarget`
      above is what says so if a routing ever stops refusing.
    * the hold's own REPORT rides in the dossier, on the `recogniser_abstention`
      item the ratified text already describes: which safety domain, which of its
      work types, in which zones. The model was being asked to judge a file the
      rules were holding and was never shown the hold.
    * the verdict SUPERSEDES the hold or leaves it standing, and `assign` is what
      writes the supersession -- `llm_supported` outranks `possible`, so the row
      G writes retires the precaution's through the store's own columns and the
      old row stays readable. Silence never lifts a hold: a decline, a refused
      claim, a failed call and a file that was never askable all leave the
      precaution row exactly as the detector wrote it.
    """
    named: dict = {}
    settled = nothing_to_ask = nothing_to_read = declined = no_route = 0
    held = released = confirmed = 0
    dependencies_for = situation_call_dependencies
    store = ClassificationStore(conn)
    # `104` §17.13 ruling 3: PER FILE, not per site. Site G's own text is
    # unratified, so `target_for` drops the cloud candidate for it and every file
    # this pass asks about goes to the model on this machine -- which is what
    # `104` §17.1 already said in words and what this now makes mechanical rather
    # than a consequence of which tier the local model happened to take.
    route_for = target_for(conn, routing, G_SITUATION_SENSITIVITY)
    for file_id, content_hash in roster:
        outcome = explain(conn, file_id, content_hash)
        if not isinstance(outcome, Abstention):
            # The rules settled it. `00`:110 sanctions exactly this: "The LLM should
            # not be called for direct, unique matches."
            settled += 1
            continue
        # THE HOLD, READ BEFORE THE QUESTION IS BUILT, because it is part of the
        # question. `104` §18 gap 24: the precaution's own report -- which of
        # `00`'s four safety domains, which of its work types, in which zones --
        # is the one thing the model judging a held file was never shown.
        #
        # THE MARK IS THE ROW, AND THE ROW IS WHAT IS ASKED. The ruling names
        # "every file the precaution marked (`basis='safety_domain'`)", and
        # `precaution_report` answers a different question -- would the rules hold
        # this file -- which is the same answer only while the precaution's row is
        # still the live one. It stops being live the moment anything stronger
        # supersedes it: a person's own `user_confirmed` correction through P15,
        # or an earlier run of this pass over the same database. On the next run
        # the detector still reads the same terms, so a report taken on its word
        # alone would tell the model "the rules are holding this file" about a
        # file the person had already released, count it as held, and -- because
        # `assign` is outranked and writes nothing -- print it as STILL HELD on
        # the one screen that is about somebody's protected files. So the store is
        # asked first, and only a live `safety_domain` row makes this a hold.
        current = store.current(file_id, content_hash)
        precaution = (
            precaution_of(conn, outcome, file_id=file_id,
                          content_hash=content_hash)
            if current is not None and current.basis in SAFETY_DOMAIN_BASES
            else None)
        if precaution is not None:
            held += 1
        try:
            question = question_for(
                outcome, file_id=file_id, content_hash=content_hash,
                matched_terms=getattr(outcome, "matched_terms", ()),
                evidence_refs=getattr(outcome, "evidence_refs", ()),
                semantic=None if semantic_of is None else semantic_of(file_id),
                precaution=precaution)
        except NothingToAsk:
            nothing_to_ask += 1
            continue
        chosen = route_for(file_id)
        if chosen is None:
            # NOTHING IS ASSEMBLED AND NOTHING IS SENT. A file with no route is
            # one `model_route_permitted` refused every target this site has:
            # since `104` §18.7 (9 Sep 2026) a protected file reaches the LOCAL
            # model, so on a run with a local target this is no longer the
            # protected count -- it is the files no target may take (a cloud-only
            # site asked about protected material, or no target wired). It is
            # counted here, on its own line, so the report cannot read it as a
            # file with nothing to say.
            no_route += 1
            continue
        client, target = chosen
        if precaution is not None and target.locality != LOCAL:
            # `104` §18.7, as an invariant rather than a hope. The route already
            # refuses it -- `model_route_permitted` asks the gate's own
            # `protected_cloud_denies` for the protected record the precaution
            # wrote -- so reaching here means the record and the route disagree
            # about the same file, and the next line would assemble a held file's
            # readings for a destination off this device.
            raise ProtectedFileOfferedACloudTarget(
                f"{file_id} is held {precaution.schema_id} by the rules and was "
                f"routed to a {target.locality} target "
                f"({target.provider}/{target.model_id}); protected material "
                "reaches the local model only, opened on this machine for it")
        observations = releasable_observations(
            conn, file_id=file_id, content_hash=content_hash,
            limit=FACT_CALL_MAX_RELEASED_OBSERVATIONS,
            locality=target.locality,
            ceiling=GROUPING_LIMITS.max_dossier_tokens)
        try:
            request = build_situation_request(
                question, observations, model_target=target, prompt=prompt,
                max_dossier_tokens=GROUPING_LIMITS.max_dossier_tokens)
        except NothingToAsk:
            nothing_to_read += 1
            continue
        verdict = run_call(
            conn, request,
            gate=fact_authorities.gate,
            # THE CLIENT THIS FILE WAS ROUTED TO, and the same object the
            # target above was read off: two reads would let the gate decide
            # about one destination while the bytes went to another.
            model_client=client,
            prompt=prompt,
            validation_dependencies=dependencies_for(
                fact_authorities,
                allowed_vocabulary=question.allowed_situations,
                placeable_file_count=len(roster)),
            observed_at=now,
            # `104` R-172: THE SAME MAILBOX EVERY OTHER SITE IS HANDED. R-14 says
            # what each call consumed is recorded beside what was reserved, and
            # R-71 closed the gap for site B by binding the sink at the composition
            # root; site G was built after both and was never handed one, so every
            # file this pass asked about wrote an `llm_response` with no
            # `llm_call_usage` row beside it -- three of fourteen on the local
            # deployment, which is what `len(usage) == responses` was failing on.
            # A response with no usage row is indistinguishable from a call that
            # spent nothing, and G spends a call per file like every other site.
            # Taken from A's authorities for R-71's own reason: the mailbox is a
            # fact about this run and this transport, not about which site asks.
            usage_recorder=fact_authorities.usage_recorder)
        situation = None
        if isinstance(verdict, P8Verdict):
            situation = situation_named_by_verdict(
                conn, verdict, question.allowed_situations)
        if situation is None:
            declined += 1
            continue
        if not prompt.ratified:
            # OBSERVE-ONLY UNTIL THE ROW SAYS OTHERWISE. `104` §7 Phase 1 step 6:
            # the verdict is recorded and nothing is applied while the text is a
            # draft. The answer is counted so a run under an unratified text still
            # reports what the site WOULD have decided, which is the whole value of
            # an observe pass -- and no classification is written, because a record
            # is an act on the answer.
            declined += 1
            continue
        # `104` §18.7 S2: the second answer of the same verdict.
        restricted_kind = restricted_kind_named_by_verdict(conn, verdict)
        record = situation_classification(
            question, situation, observed_at=now(),
            restricted_kind=restricted_kind,
            # `104` §18 gap 24: G's answer may not lift a hold it did not
            # contradict. `situation_classification` carries the argument.
            held=precaution is not None)
        # THE SUPERSESSION IS `assign`'S AND IS NOT SPELLED AGAIN HERE. This
        # record is `llm_supported` and the precaution's is `possible`, so
        # `assign` writes it, retires the precaution row through
        # `supersedes`/`superseded_by`/`supersede_reason`, and leaves the old row
        # readable -- §8.2's "supersede, never overwrite". Nothing here edits or
        # deletes what the detector concluded.
        written = assign(conn, record, store=store,
                         component_version=component_version)
        if precaution is not None and written is record:
            # WHICH WAY THE HOLD WENT, read off the record that actually
            # superseded it rather than off the answer a second time: the flag on
            # the row IS what every later pass reads, so counting anything else
            # would be a screen that could disagree with the store. `assign`
            # returns something OTHER than this record when it wrote none of it --
            # the person has rejected this class for this file, or a stronger
            # record already stands -- and in both cases the precaution row was
            # never retired, so the hold is standing and is counted as standing.
            if record.protected:
                confirmed += 1
            else:
                released += 1
        named[file_id] = situation
    return SituationPass(
        named=named, settled=settled, nothing_to_ask=nothing_to_ask,
        nothing_to_read=nothing_to_read, declined=declined, no_route=no_route,
        # `still_held` IS DERIVED AND IS NOT A SEVENTH TALLY. A hold that was
        # neither released nor confirmed is standing, whichever of the pass's six
        # buckets its file fell into -- and deriving it is what makes "these three
        # partition `held`" true by construction rather than by six `+= 1`s
        # staying in step with each other.
        holds=PrecautionHolds(held=held, released=released, confirmed=confirmed,
                              still_held=held - released - confirmed))


_NOTHING_ASKED = SituationPass(
    named={}, settled=0, nothing_to_ask=0, nothing_to_read=0, declined=0,
    no_route=0,
    holds=PrecautionHolds(held=0, released=0, confirmed=0, still_held=0))


def model_fact_resolver(conn: sqlite3.Connection, *,
                        authorities: FactCallAuthorities) -> FactResolver:
    """P6 again, with ONLY the model producer. A second pass, and deliberately so.

    **Why it is not the `llm` stage of the resolver P1-P7 already runs.** Two
    things the gate requires do not exist yet at that point in the run, and neither
    is a detail:

    * `orchestrator.run_p1_p7` calls `classify` AFTER `resolve_native` for the same
      file, in the same loop, so during the first pass EVERY file is unclassified
      and every cloud release would be `Denied(unclassified)`.
    * `set_privacy_policy` is a `CorpusDecisions` callback and
      `run_production_p8_p11` calls it after the tree is designed --
      `production.py:733` -- so during the first pass `current_policy` returns
      `None` and `Gate.release` raises `NoPolicyInForce` rather than deciding.

    So the model pass runs where both are true: after P7 has classified and after a
    policy is in force, and before P9 groups -- which it must be, because a fact
    that arrives after grouping is a fact no group could form on.

    `record_pass` records NOTHING, and the reason is at the argument itself: a
    `fact_passes` row is a claim about EXTRACTION coverage, and this pass reads no
    bytes.
    """
    return FactResolver(
        stages={"direct": None, "rule": None,
                "llm": fact_call_stage(authorities)},
        # WHAT THE BARRED ROUTE WOULD HAVE ATTEMPTED. `_write_bars` writes one
        # `unresolved` row per pending field when the privacy or budget bar fires,
        # and `()` here -- which is what the deterministic resolvers pass, because
        # neither of their stages is ceiling-gated -- would write none of them and
        # leave a withheld file looking like a file with nothing to say.
        pending_fields=lambda db, file_id, content_hash: pending_fields_for(
            db, file_id=file_id, content_hash=content_hash,
            activation_signals=authorities.activation_signals),
        # `ScanBudget` is P8's ceiling and `reserve_call` enforces it inside
        # `run_call`, which is where the reservation and the settlement live. A
        # second budget read here would be a second answer to one question, and the
        # bar it writes -- `budget_deferred` -- would then describe a deferral P8
        # never made.
        budget_exhausted=lambda ceiling: False,
        # R-02: the route is asked the same question the gate will answer -- and
        # since `104` §17.13 ruling 3 it is the SAME CALLABLE rather than a second
        # predicate built on the same locality. The stage asks `authorities.route`
        # for the destination and this asks whether there was one, so a file
        # counted as routed is a file with a model to route it to.
        model_route_permitted=lambda file_id: (
            authorities.route(file_id) is not None),
        # NOTHING IS RECORDED, and `"llm"` being a member of P4's `ANALYSIS_TIERS`
        # is exactly why the temptation had to be refused. `facts.usable` publishes
        # one reader of that table and it asks two questions: `no_usable_facts`
        # RAISES when `passes_for` is empty, on the ground that §2.2's verdict "is
        # defined only after that pass has completed"; `targeted_ocr_needed` then
        # asks whether any recorded pass covered `ocr`. A row reading `{llm}` is a
        # true statement about this pass and a false answer to the first question:
        # it says a pass completed for this version when no extractor has read a
        # byte of it, so a file whose deterministic pass never ran would stop
        # raising and start answering. Today the ordering hides that -- this
        # resolver runs after P1-P7 has recorded a native pass for every file -- and
        # a guard that is correct only because of where it is called is the kind
        # this project has paid for. The model pass reads no bytes and covers no
        # extraction tier, so it records no coverage.
        record_pass=lambda db, file_id, content_hash: None,
        cache_key_for=lambda file_id, content_hash: f"cli-llm-v1:{content_hash}",
        # §2.2's suppression already fired in the pass that read the bytes, and
        # `screen_metadata` is not idempotent-by-nature: it writes an `unresolved`
        # row. Running it twice would accuse this file of a second refusal it did
        # not receive.
        screen_metadata=lambda db, file_id, content_hash: ())


def _mime_type_for(path: Path) -> str | None:
    import mimetypes

    return mimetypes.guess_type(str(path))[0]


#: The format token for a file that has NO extension, by the convention its name
#: follows. Nine files on the measured corpus have no extension at all and every one
#: of them recovered nothing (`.groundtruth/baseline/scorecard.txt`: `(none) 0 of 9`)
#: for a mechanical reason -- `route()` keys on a token, and the declared extension of
#: `LICENSE` is the empty string, which is a key in no table.
#:
#: Every name here is one a tool or a licence body requires by that exact spelling, so
#: this is a statement about those conventions and not a judgement about a project --
#: the same claim `readers/text_documents._MARKERS_BY_FILENAME` makes about its own
#: list. It lives HERE because §2.9 puts the mapping from a real-world signal onto the
#: router's token space in the deployment: "A real deployment maps libmagic's MIME
#: type or macOS's UTType onto that token space, and THAT mapping belongs to the
#: reader." This is that mapping, keyed on the filename instead of a MIME type,
#: because a filename is the only signal an extensionless file has.
#:
#: Prose on the left, code on the right, and the split is §2.4's: a LICENCE is a
#: document a person reads, and a Dockerfile is a recipe whose text §2.4 keeps out of
#: the prose path. `dockerfile` and `makefile` are format tokens no extension can
#: produce, which is why `extractors/router.py` carries them as keys of their own.
#: EACH NAME WAS COUNTED, which is the rule `extractors/router.py`'s own additions
#: follow -- "nothing is here for a language the owner does not write". These are the
#: seven extensionless files on the measured corpus, plus `readme` and `copying`:
#: `readers/text_documents._markers_for` already recognises a README by stem, so a
#: table that routed every convention EXCEPT that one would be the odd omission, and
#: `COPYING` is the GNU spelling of `LICENSE` sitting beside it in the same trees.
#: Nothing speculative: no `TODO`, no `CHANGELOG`, no `VERSION`. When one of those
#: turns up on a real disk it can be added, with the count that earned it.
_FORMAT_BY_EXTENSIONLESS_NAME: dict[str, str] = {
    "license": "txt",     # Desktop/ThirdEye/LICENSE, .../GazeFollower/LICENSE-CC-BY-NC-SA
    "notice": "txt",      # Desktop/vision claw /VisionClaw/NOTICE
    "authors": "txt",     # .../ai-file-sorter/external/libzip/AUTHORS
    "thanks": "txt",      # .../ai-file-sorter/external/libzip/THANKS
    "copying": "txt",     # the GNU spelling of the two above
    "readme": "txt",      # already a "README file" marker; see the note above
    "dockerfile": "dockerfile",   # Desktop/ThirdEye/gaze2/Dockerfile
    "makefile": "makefile",       # Desktop/Database agent/ai-file-sorter/app/Makefile
}


#: `_FORMAT_BY_EXTENSION` STOOD HERE AND IS DELETED BY `104` §18.2 GAP 21. It mapped
#: five suffixes onto the five format tokens they already spell -- `.pdf` -> `pdf`,
#: `.docx` -> `docx` -- and `_detect_format` RETURNED from it before the signature
#: reader could run. Its two effects, measured against what `route()` does with the
#: answer: for those five it returned the token `declared` already is, so the
#: operative format was identical either way; for every OTHER extension the router
#: knows -- `.png`, `.py`, `.csv`, `.psd`, `.jpg` -- `.get()` missed and it returned
#: None, which is where "detected format null for most files" comes from.
#:
#: NOTHING READ IT AS A HINT, so nothing replaces it. The extension IS still the
#: hint and two places still read it: `readers/signatures.py` defers its weak
#: "these bytes are text" answer to any extension the router knows, and `route()`
#: falls back to `declared` when the signature declines. `route()` records it in
#: its own column (`extraction_routing.declared_extension`) beside the detected
#: format, which is the record §2.9 asks for and this map was quietly emptying.
#: §2.9's other half, wired here and nowhere else. Built once: `signature_detector`
#: compiles nothing per call, and building it per file would put the protected-
#: container predicate behind a fresh closure on every path this command touches.
_FORMAT_BY_SIGNATURE = signature_detector(
    is_protected_container=is_protected_container)


def _detect_format(path: Path) -> str | None:
    """What the FILE ITSELF says it is: the naming convention, then the bytes.

    **`104` §18.2 gap 21 deleted a third answer that came before both.** This
    function used to open with `if declared in SOURCE_TYPE_BY_FORMAT: return
    _FORMAT_BY_EXTENSION.get(...)`, so for every file with an extension the router
    recognised -- which is nearly every file on a disk -- `readers/signatures.py`
    never ran. §2.9 asks the engine to "INSPECT THE REAL MIME TYPE OR FILE SIGNATURE
    WHERE POSSIBLE"; the module written to do that was reached by extensionless
    files alone. Three things died with it, and none of them is the routing:

      * `extraction_routing.detected_format` was NULL for most files -- five
        extensions got the token they already spelled and everything else got None;
      * the disagreement column could not fire, because a value read off the
        extension cannot contradict the extension. A PDF saved as `notes.txt` was
        detected `txt`, agreed with itself, and was handed to the plain-text reader,
        while `readers/signatures.py`'s own docstring promised it "is read as a PDF";
      * `filesystem.unrouted_result` writes §2.9's indexed-but-unreadable `format`
        observation only `if detected:`, so a `.psd` -- the M3 case that clause was
        written for -- recorded the filename and no format.

    **The measurement that argued for the old order is kept, and it does not argue
    for it any more.** Tried on 2026-09-06 against the owner's 21-file sample, asking
    the signature first changed seven operative formats: five `.ipynb` and one
    `.code-workspace` to `json` (they ARE JSON) and one `.jpeg` to `jpg` (one format,
    two spellings). The objection was that `route()` would then record seven
    "manufactured" disagreements. Re-checked against the router's tables rather than
    against the tokens: `ipynb`, `code-workspace` and `json` all carry
    `code_structured` and `text.structured`; `jpeg` and `jpg` both carry `image` and
    `image.metadata`. NOT ONE of the seven changes the family or the extractor -- the
    routing is byte-identical and what they gain is a true row saying the name and
    the bytes spell the format differently, which is a spelling variant for the owner
    to read and not a claim that anybody misnamed a file.

    Two files DO change where they go, and both move toward the truth. A camera raw
    beginning `II*\\x00` now detects `tiff` and reaches the image family instead of
    the spreadsheet one -- `router.py`'s `raw` key is annotated "RAISED FOR RULING:
    on a photographer's disk this key would be wrong more often than right, and the
    router cannot tell the two apart without opening the file", and it can now. A
    `.numbers` export is a ZIP and detects as one, so it yields a manifest under
    §2.5 where `readers/long_tail_stdlib` returned None and the run said
    `unsupported`.

    **THE NAME STILL COMES BEFORE THE BYTES, for a file that has no extension.** A
    real `Dockerfile` decodes as text, so the signature's weak answer for it is
    `txt`, and taking that would move every Dockerfile on a disk out of
    `code_structured`. A file named by a convention a tool requires has already said
    what it is. That table answers for extensionless files only; a `Makefile.md` is
    Markdown.

    **What stays null, said plainly.** `signature_detector` returns None rather than
    its weak `txt` whenever the router already knows the extension -- deliberately,
    because "these bytes are text" identifies nothing and returning `txt` would route
    every `.csv`, `.md` and `.ics` to the plain-text handler. So a plain `.txt`,
    `.md`, `.csv` or `.py` still records no detected format, and that is the honest
    answer: nothing about those bytes identified a format. What changed is that the
    files whose bytes DO identify one now say so.

    **THE ONE RULE THAT FORBIDS OPENING A FILE IS STILL OBEYED, and it now covers
    more files rather than fewer.** The class of file that must never be opened is
    decided by PATH before any format question; `signature_detector` takes that
    predicate as a REQUIRED argument and answers None for a protected path without
    reading a byte. A file inside a protected container therefore records NO detected
    format where the extension map used to supply one -- which is the truth, because
    nothing looked.

    **AND THERE IS A SECOND SUCH CLASS, which the extension shortcut used to hide.**
    An iCloud-evicted file's bytes are not on this machine, and 11 §5 is absolute
    about it: *"P3 detects a dataless / not-downloaded ubiquitous item before hashing
    ... DO NOT MATERIALIZE, hash, or extract."* Opening one does not raise -- it
    triggers the download the rule exists to prevent -- so `signature_detector`'s
    OSError arm is no help, and `SafetyPolicy.is_dataless` is no help either because
    it guards `admit()`, which runs in the EXTRACTOR, long after the router has
    chosen one. `orchestrator.py` calls `route()` for every evicted file (its pass
    2b, the one that writes C4's `dataless` run), so before this guard the deleted
    shortcut was the only thing standing between a corpus in iCloud and a full
    download. The flag is read from the file's own `stat`, which reads metadata and
    materialises nothing, and the answer is the same shape as the protected one: no
    detected format, because nothing looked. `route()` then falls back to the
    declared extension exactly as it did yesterday.
    """
    try:
        if is_dataless(path.stat()):
            return None
    except OSError:
        # Not this function's to diagnose, and not a reason to stop: the signature
        # reader has the same arm and answers from the extension there.
        pass
    if not path.suffix:
        name = path.name.lower()
        # `LICENSE-CC-BY-NC-SA` is on this disk, and `LICENSE-APACHE` and
        # `COPYING-LESSER` are the same convention: the licence body's name follows
        # the word, after a hyphen. The word before the first hyphen carries it.
        by_name = (_FORMAT_BY_EXTENSIONLESS_NAME.get(name)
                   or _FORMAT_BY_EXTENSIONLESS_NAME.get(name.split("-")[0]))
        if by_name is not None:
            return by_name
    return _FORMAT_BY_SIGNATURE(path)


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


def _usable(facts, unresolved) -> bool:
    """§3.6's usability verdict: are the stored facts worth keeping as they are?

    This answered `True` unconditionally, which made targeted OCR unreachable --
    so a scanned page whose text layer is broken was read once, yielded nothing,
    and was never looked at again. That was the honest answer at the time, and
    the alternative it was avoiding is real: answering `False` would send every
    text-bearing PDF through Apple Vision on the strength of a threshold nobody
    chose. The `no_usable_facts` threshold is Deferred by name (M11, P5 OQ1) and
    nothing here chooses it.

    **The empty case needs no threshold.** A deterministic pass that produced no
    fact AND recorded nothing unresolved settled nothing whatsoever, and "usable"
    is not a defensible word for it. That is a boundary, not a bar: it asks
    whether there is anything at all, never how much is enough.

    `unresolved` counts as evidence FOR usability here, exactly as
    `no_usable_facts_for` says it should -- "a version whose every attempted field
    ended in a recorded refusal is a version whose evidence yielded nothing, and
    that is a stronger statement than an empty fact list". A refusal means the
    pass ran and reached a conclusion about that field; re-reading the bytes with
    a different engine is not what such a file needs.

    So the second look is offered to exactly one kind of file: the one the read
    produced nothing about. Every other corpus keeps the deferred answer, and no
    document that yielded so much as one fact is ever re-read.
    """
    # `no_candidate_evidence` is excluded, and this function's own words are
    # why: the second look is offered to exactly one kind of file, the one the
    # read produced nothing about. That reason IS "nothing was there to look at",
    # so counting it would answer the question with itself. Every other reason is
    # a refusal the product reached having looked, and those still count, because
    # re-reading the bytes is not what such a file needs.
    return bool(facts) or any(row["reason"] != NO_CANDIDATE_EVIDENCE
                              for row in unresolved)


def extraction_context() -> ExtractionContext:
    """The three authorities `extract_initial` needs, wired once and named here.

    **A module-level function, and that is the whole design.** A worker process is
    spawned, not forked, so it cannot inherit `readers`: `pdfium_reader()` and
    `vision_ocr()` RETURN the functions they wire and a closure has no name for
    `pickle` to write down. What crosses the boundary is this function's NAME, and
    the worker calls it to build its own. Both halves of a run are therefore wired by
    one function rather than by two that happen to agree today -- which matters
    because `readers` is folded into §3.4's cache key by way of the extractor
    versions, and a worker with a different PDF reader from its caller would write
    rows the caller could never reproduce.

    It is also what `p1_p7_authorities` uses for the serial path, so there is exactly
    one place in this product where the deployment's readers are chosen.
    """
    return ExtractionContext(
        # THE standing rule, at its first enforcement point. `is_protected_container`
        # is P3's own predicate; P3 writes an exclusion verdict for the container and
        # never walks inside it, so no `files` row for its interior is ever created
        # and nothing downstream can read one.
        policy=SafetyPolicy(is_protected_container=is_protected_container,
                            is_dataless=lambda path: False),
        # `read_pdf` IS pdfium's and no longer pdfminer's, and that swap is the
        # single largest measured change in this product's speed. Over eighteen of
        # the owner's real files, 55.0 of 72.0 profiled seconds were inside
        # `read_pdf`, essentially all of it in `pdfminer.psparser.nexttoken` --
        # pdfminer.six is a pure-Python parser and that IS the cost. On the same
        # seventeen PDFs under this same 50-page ceiling: pdfminer 30.98s, pypdf
        # 16.23s, PyMuPDF 3.74s, pdfium 2.02s.
        #
        # THE LICENCE, because it is the reason this is pdfium and not MuPDF. pdfium
        # is BSD-3-Clause and pypdfium2 is Apache-2.0 OR BSD-3-Clause; PyMuPDF is
        # AGPL-3.0, which for a product that may ship is a real constraint. The
        # faster library is also the permissive one, so there was no trade to put to
        # anybody. `readers/pdf_pdfium.py` carries the fidelity comparison that
        # earns the swap: zones and heading labels, not prose similarity.
        readers=macos_readers(find_structured_strings=find_structured_strings,
                              read_pdf=pdfium_reader(
                                  max_pages=PDF_PAGE_CEILING),
                              spreadsheet_cell_ceiling=SPREADSHEET_CELL_CEILING,
                              # §8.6's two per-file OCR ceilings. `_bootstrap`
                              # publishes these same two numbers on P1's table, so
                              # what bounded a run can be read back from the run's
                              # own database rather than from this file.
                              ocr_page_ceiling=OCR_PAGE_CEILING,
                              ocr_seconds_per_file=OCR_SECONDS_PER_FILE),
        # Transcription opens audio and video. Not authorised, and saying so is
        # what keeps it off rather than the absence of a transcriber.
        transcription_authorized=lambda: False)


def extraction_pool(*, workers: int):
    """WHERE `extract_initial` runs, given how many processes may run it.

    **A PROCESS AT EVERY WORKER COUNT, INCLUDING ONE, and R-138 is why.** One worker
    used to be `InlinePool` -- the same thread, the same call order, no spawn and no
    interpreter start for a run of three text files -- and that is the behaviour this
    product had before `extraction_pool` existed. It is also a reader with no
    deadline, and `readers/ocr_vision.py` and `readers/doc_cocoa.py` reach into
    Apple's Vision, Quartz and AppKit through PyObjC, where a wedge is not
    hypothetical: R-138's r6 hung ten minutes at 0 % CPU inside CoreImage's
    `CI::Context::recursive_render`, waiting on a dispatch group.

    `ProcessPool`'s ceiling is the only thing in this product that can end such a
    wait, and it ends it by KILLING A PROCESS -- a Python timeout does not interrupt
    a C dispatch wait on the thread doing the waiting. So a deployment that reads on
    the calling thread is a deployment whose runs can hang, whatever its worker
    count, and there is now no such deployment. `InlinePool` remains what the suite
    drives when it wants extraction without concurrency; it is not what a person's
    scan runs on.
    """
    return ProcessPool(
        workers=workers, context_factory=extraction_context,
        lookahead_per_worker=EXTRACTION_LOOKAHEAD_PER_WORKER,
        seconds_per_extraction=EXTRACTION_SECONDS_PER_FILE)


def p1_p7_authorities(*, now, detector,
                      operation_mode: str = OPERATION_MODE,
                      source=None, bundle_content: bool = False) -> P1P7Authorities:
    # `assemble_bundle` DEFAULTS OFF HERE, and only here. §8.5's envelope is read by
    # `evaluate_bundle` and named by `--record`; this command declares no evaluation
    # (see `evaluation=None` below, and the note beside it) and most runs record no
    # name, so the bundle was assembled in full and never opened. Measured on a real
    # 413-file folder: 192,221 rows and 230 MB, half the database, duplicating
    # `text_units` and `evidence` row for row. `--record` turns it back on, because
    # that is the gesture whose whole purpose is to keep the run.
    # `source` is an ARGUMENT with the live filesystem as its default, because
    # `--record` needs the scan wrapped in a `RecordingCorpusSource` -- the
    # listings it serves ARE the corpus snapshot, and they cannot be recovered
    # afterwards. Not a policy: the default is unchanged and every ordinary run
    # still reads the disk.
    context = extraction_context()
    return P1P7Authorities(
        native_resolver=_resolver(tiers=frozenset(("filesystem", "native")),
                                  cache_key="cli-native-v1"),
        ocr_resolver=_resolver(
            tiers=frozenset(("filesystem", "native", "ocr")),
            cache_key="cli-ocr-v1"),
        usable_threshold=_usable,
        classify=classifier(detector, now=now),
        bundle_content=bundle_content,
        source=FilesystemCorpusSource() if source is None else source,
        # IMPORTED, never respelled -- and the import is the fix. This wrote the
        # literal `"scanned"`; P9's `_corpus` admits `scan_state = 'included'`
        # and nothing else, so on every live run the neighbourhood of every file
        # was EMPTY, no shared-fact edge was ever built, and every group was a
        # group of one whatever the corpus said. P9's own tests write `included`,
        # so 5,000 of them agreed with a production path that could not form a
        # group of two. P3's SPEC Q4 leaves the vocabulary to the caller (
        # `scan_agent/basic_record.py:50`), which makes this deployment's job to
        # write the word its readers read, from their constant.
        mime_type_for=_mime_type_for, scan_state=P1_INCLUDED_SCAN_STATE,
        scan_budget_exhausted=lambda: False, detect_format=_detect_format,
        # All three come from `extraction_context()` and are not respelled here: the
        # caller's `readers` and the workers' `readers` have to be the same wiring,
        # and two constructions of "the same" wiring is exactly how they would drift.
        # `policy` matters most -- it carries `is_protected_container`.
        policy=context.policy,
        readers=context.readers,
        transcription_authorized=context.transcription_authorized,
        pool=extraction_pool(workers=EXTRACTION_WORKERS),
        now=now,
        # §2.6's excerpt window, in characters. `00` states none.
        context_window=240,
        corpus_form="snapshot", policy_settings={"operation_mode": operation_mode},
        file_entry_body=lambda row: {"payload_ref": row["content_hash"]},
        p7_component_version=COMPONENT_VERSION)


def _file_id_of_subject(subject_ref: str) -> str | None:
    """`placement.store.subject_ref_of`, read back, and only the file form.

    P11 spells a file version `file:<id>:<hash>` and a group `group:<id>`. The
    hash is dropped because §8.4's predicate re-reads it from `files` itself: a
    caller-supplied hash would let a stale dossier ask about a version of the file
    that is no longer the current one, and the answer would look authoritative.

    Anything that is not the file form returns `None` and the caller refuses.
    That includes P8's fixture shorthand `file-1`: a bare string read as a file id
    would make this answer about a file nobody addressed, and a wrong answer here
    is a protected file filed automatically.
    """
    kind, separator, rest = subject_ref.partition(":")
    if not separator or kind != pv.FILE:
        return None
    file_id, _separator, _content_hash = rest.partition(":")
    return file_id or None


def _proposes_a_move(payload: Mapping[str, object]) -> bool:
    """Does this response put the file somewhere? Site C's key and Site D's.

    A response that moves nothing cannot ignore a move restriction, and refusing
    one would be worse than pointless: `leave_in_current_location` and
    `mark_review_later` are the two dispositions that leave a protected file
    exactly where its owner put it, and a policy that rejected them would be
    pushing protected material out of its own shelter.
    """
    for key in ("destination", "target"):
        value = payload.get(key)
        if isinstance(value, str) and value and value != "none":
            return True
    return False


def sensitivity_policy_for(conn: sqlite3.Connection):
    """P7's answer to P8's two sensitivity checks. An adapter, and nothing more.

    **What was wrong.** `SENSITIVITY_POLICY_VIOLATION` (Site C) and
    `SENSITIVITY_RESTRICTION_IGNORED` (Site D) are two of P8's fifteen placement
    checks and both call one injected predicate. This file passed `None` for it on
    every run this product has ever made and every test in the tree stubbed it
    `True`, so nobody was asking P7 the question. The D2 bakeoff measured the
    consequence: both local D texts filed the redacted statement into Receipts and
    P8 accepted it.

    **Why this is not a new rule.** §8.4's automatic-move predicate already exists
    and is published as `privacy.moves.may_move_automatically`. It reads the live
    classification record and, for a protected one, the user policy that permits
    that file's move; it refuses by default; it writes nothing. This function
    hands P8 that answer and adds two things only: which subject the dossier is
    about, and whether the response proposes a move at all. Any further judgement
    belongs in P7, which owns the classification.

    **A proposal is not a move, and that is the one judgement this adapter makes.**
    §8.4's predicate answers "may this be moved automatically" and refuses a file
    P7 has never classified. That refusal is right for a move and wrong for a
    proposal: P8 is validating something a person then reviews, automatic filing is
    Release 2, and on the owner's corpus 95 of 199 readable files carry no
    classification record. Refusing those would spend coverage protecting them from
    a move this release does not make. So absence of a record permits the proposal
    and P7 owns every other branch unchanged -- not protected is permitted,
    protected is refused unless a user policy names the file. The handling class is
    not read at all: `privacy/classification.py` says neighbouring parts consume
    the `protected` flag rather than inferring it from the class, and leaves open
    whether the two coincide.

    Injected alongside seven `None`s. `model_path_available` reads this field, so
    supplying it alone does not switch the model path on -- there is still no
    ratified placement prompt, and `model_placement` says why the other seven are
    withheld together. A refusal, unlike a call, needs no prompt to be correct.
    """
    def permitted(dossier, payload: Mapping[str, object]) -> bool:
        if not _proposes_a_move(payload):
            return True
        file_id = _file_id_of_subject(getattr(dossier, "subject_ref", "") or "")
        if file_id is None:
            return False
        row = get_file(conn, file_id)
        if row is None:
            return False
        # AN UNCLASSIFIED FILE MAY BE PROPOSED, AND THIS IS THE ONE PLACE THE TWO
        # QUESTIONS COME APART. §8.4's predicate answers "may this be moved
        # automatically", and for a file P7 has never classified its answer is
        # `unreadable_unclassified` and its refusal is right: it will not read
        # absence as permission. P8 is judging a PROPOSAL that a person reviews,
        # and automatic filing is Release 2. Refusing the proposal would take 95
        # of the owner's 199 readable files out of the engine to protect them from
        # a move nothing is going to make -- coverage spent on a risk that does not
        # exist in this release. The file still reaches the person through the
        # review-required path the offline run already gives it.
        #
        # THE CLASS IS NOT CONSULTED, deliberately. `privacy/classification.py`
        # states the rule: "Neighbouring parts should consume the `protected` flag,
        # not infer it from the class", and its Open question 1 -- whether
        # `protected` is exactly the top two classes -- is unsettled. So P7's flag
        # is the whole of the answer here and a handling class read as a second
        # opinion would be P11 deciding a question P7 has left open.
        if ClassificationStore(conn).current(file_id, row["content_hash"]) is None:
            return True
        # Classified. P7 owns every remaining branch: not protected is permitted,
        # protected is refused unless a user policy names this file. `or ""` is both
        # validator sites' own convention for a dossier with no plan version --
        # `current_policy` finds no row, so a protected file is refused and an
        # unprotected one is not held hostage to the version.
        return may_move_automatically(
            conn, file_id, getattr(dossier, "plan_version", None) or "").allowed

    return permitted


# ======================================================================================
# The user's decisions
# ======================================================================================


def review_and_accept(conn: sqlite3.Connection,
                      results: Sequence[GroupingResult], *,
                      group_category: str, label: str,
                      created_at: str,
                      branch_for: Callable[[str], Branch | None] | None = None,
                      default_branch: Branch | None = None,
                      on_accepted: Callable[[str, Branch | None], None] | None = None,
                      ) -> tuple[str, ...]:
    """The review screen, non-interactively: keep everything, as one named group.

    **`104` R-37: one named group PER BRANCH, when the run proposes more than
    one.** `branch_for(file_id)` is `BranchPartition.branch_of` bound to this
    run's partition; with it, each P9 group is accepted under the branch a strict
    majority of its members are under -- its label and its schema -- and every
    other group under `default_branch`, which is the `--label`/`--situation`
    the person typed: ruling (1), the folder's default, "unchanged when nothing
    else is known". A group whose members two branches reach, or that two
    branches tie over, is exactly the case where nothing else is known (`104`
    R-140 already puts a file NO branch reaches under the default).

    **Dropping such a group instead was the reverted merge 8b9280d.** On the
    owner's corpus a course whose files carry no kind word in their names has
    no anchor, its files are held, its `subject` group went unaccepted, and the
    coursework branch lost the course and term levels it had -- 14 labelled
    coursework files landed in `Coursework/exam`, `Coursework/homework`.
    Reproduced on a synthetic corpus (`tests/integration/test_r37_per_branch_
    situation.py`): `Coursework/Fall2025/MATH2000` (3 files) vanished. The
    site-A half of the ruling is untouched by this: a held file is still asked
    nothing; where its group is FILED offline is the default's, as before.

    `None` keeps every group under `label`, which is the run with one branch and
    is byte-identical to the run before. `on_accepted` is told each merged id
    and its branch, so the design can hand P10 the branch's own situation
    signal.

    **The justification this docstring used to give was false, and correcting it
    matters more than it looks.** It said `src/grouping/pipeline.py` writes
    `display_label=None` on every group and that `--label` is therefore the only
    name available. `pipeline.py` does write `None` -- but `naming.engine_proposal`
    runs after the stop rules and fills in `display_label`, `group_category` and a
    coherence verdict from the group's own anchor facts. Measured on a four-role
    corpus: P9 produced four groups named `PHYS1401`, `PHYS2801`, `CV20261234` and
    `Spring2026`, every one `label_source='engine'` and `coherent`, and this
    function merged them into one called `Coursework`.

    **It still merges, and that is the right call today.** The names are not lost:
    the vertical pass rebuilds them from the subject dimension, so the tree really
    does read `Coursework/PHYS1401`. Accepting the four separately would put four
    course codes at the ROOT and destroy the nesting -- a worse tree, arriving
    from a fix aimed at a real defect.

    What `--label` and `--situation` genuinely supply is the TOP-LEVEL branch's
    name and the category that makes it routable at all: an accepted group with no
    category is eligible for no applicability row and C3 refuses the branch
    outright. What they also do, and should not, is flatten four categories into
    one -- a legal matter number filed under "Coursework". That is `66` §13's
    structural-versus-contextual split at corpus scale, it is the largest thing
    still wrong with this command for a person with more than one life, and it
    needs a per-group answer that only P15 or a review surface can collect.

    Recorded as a supersession through P9's own writers rather than as an edit, so
    what P9 proposed and what the user answered are both still on disk.
    """
    # A halted group is not a proposal. `grouping/pipeline.py:539` returns the
    # `Group` on a result whose stop rule fired so the caller can say WHY
    # nothing formed, and deliberately does not record it -- "a group that
    # cannot form should not cost either one". So `group is not None` is not
    # the question. Merging one puts its anchor facts and its count into a
    # group a person is shown, and `supersedes` below then names a row that is
    # not in `groups`: on `68`'s multi-life corpus that was a `RecordAbsent`
    # traceback instead of a plan, via SR3 -- "one high-frequency entity acts
    # as the only bridge", which is what a disk with several lives on it looks
    # like. The more multi-role the person, the likelier they hit it.
    grouped = [result for result in results
               if result.group is not None and result.stop_rule_outcome is None]
    if not grouped:
        return ()
    if branch_for is None:
        buckets = [(None, group_category, label, grouped)]
    else:
        if default_branch is None:
            raise ValueError("accepting per branch needs the default branch to "
                             "accept the rest under")
        buckets = _grouped_by_branch(conn, grouped, branch_for, default_branch)
    accepted: list[str] = []
    for branch, category, branch_label, bucket in buckets:
        merged_id = _accept_as_one(
            conn, bucket, group_category=category, label=branch_label,
            created_at=created_at)
        if on_accepted is not None:
            on_accepted(merged_id, branch)
        accepted.append(merged_id)
    return tuple(accepted)


def _grouped_by_branch(conn: sqlite3.Connection,
                       grouped: Sequence[GroupingResult],
                       branch_for: Callable[[str], Branch | None],
                       default: Branch):
    """P9's formed groups, bucketed by the branch most of their members are under.

    In BRANCH order, the default first, and within a bucket in P9's own order, so
    two runs over one folder accept the same groups under the same addresses.
    A group with no member under any branch, or with two branches tied for its
    members, is the DEFAULT's -- see `review_and_accept` for why it is not
    dropped.

    **The vote is over the group's STORED members, not over `result.memberships`.**
    A `GroupingResult` is one subject file through the sequence and carries that
    one file's membership only, so a vote over it was a vote of one: a course
    group whose seed happened to be a held file was dropped whole, and on the
    owner's corpus that emptied the coursework branch of its courses and left it
    built flat by kind (the reverted merge 8b9280d). `memberships_for_group` is
    what `_accept_as_one` carries into the merged group, so the vote and the
    merge read the same members.
    """
    buckets: dict[str, tuple[Branch, list[GroupingResult]]] = {}
    for result in grouped:
        votes: dict[str, int] = {}
        branches: dict[str, Branch] = {}
        for membership in memberships_for_group(conn, result.group.group_id):
            branch = branch_for(membership.file_id)
            if branch is None:
                continue
            votes[branch.label] = votes.get(branch.label, 0) + 1
            branches[branch.label] = branch
        chosen = default
        if votes:
            most = max(votes.values())
            leaders = [name for name, count_ in votes.items() if count_ == most]
            if len(leaders) == 1:
                chosen = branches[leaders[0]]
        buckets.setdefault(chosen.label, (chosen, []))[1].append(result)
    ordered = sorted(buckets.values(),
                     key=lambda pair: (not pair[0].is_default, pair[0].label))
    return [(branch, branch.schema, branch.label, bucket)
            for branch, bucket in ordered]


def _accept_as_one(conn: sqlite3.Connection, grouped: Sequence[GroupingResult],
                   *, group_category: str, label: str, created_at: str) -> str:
    """One merged, accepted group over these formed groups. `review_and_accept`'s
    body, unchanged, so the single-branch run writes the records it always wrote."""
    first = grouped[0].group
    # DERIVED FROM WHAT IT MERGES, which is P9's own rule for its own ids:
    # "a group id derived from its seed is an address, so a rerun over unchanged
    # evidence is the same group and not a conflict."
    #
    # This id used to be `{PLAN_VERSION}:{category}:{label}`, and `PLAN_VERSION`
    # is a fixed constant -- so the address was perfectly stable across runs
    # while its contents were the person's corpus, which is not. Delete one file
    # and the next run raised `MalformedGroupRecord` at the store, correctly,
    # because a revision supersedes rather than replaces. A disk that changes
    # between runs is the normal case, and that traceback blocked every
    # second-run gesture at once: answering a question, revoking one, sending a
    # review set, rejecting a fact -- each of them is a second run by
    # definition.
    #
    # The category stays in the address for the reason it was put there: two
    # situations filed under one `--label` are two groups of two different
    # kinds. The digest is over the group ids being merged, which are themselves
    # content-derived, so an unchanged corpus still produces one address and one
    # accepted group rather than a new one per run.
    merged_of = ",".join(sorted(result.group.group_id for result in grouped))
    digest = hashlib.sha256(merged_of.encode("utf-8")).hexdigest()[:12]
    merged_id = f"{PLAN_VERSION}:{group_category}:{label}:{digest}"
    reviewed = Group(
        group_id=merged_id, seed_ref=first.seed_ref, seed_kind=first.seed_kind,
        # RULES, not USER. `--label` and `--situation` really are the person's
        # answers -- they are required flags and this command refuses to guess
        # them. The FILE SET is not: this review keeps every group P9 proposed
        # and shows nobody. Saying "the user confirmed these files" writes a
        # human judgement into a record P13, a replay and the audit log all read
        # back, about an act nobody performed.
        proposed_basis=(
            f"the rules kept every group P9 proposed and the user named them "
            f"{label!r}; nobody was shown which files went into this one"),
        anchor_facts=tuple(
            fact for result in grouped for fact in result.group.anchor_facts),
        pre_model_signals={"reviewed_proposals": len(grouped)},
        anchor_count=sum(result.group.anchor_count for result in grouped),
        coherence_verdict=COHERENT,
        coherence_citations=tuple(
            fact.observation_key for result in grouped
            for fact in result.group.anchor_facts),
        group_category=group_category, display_label=label,
        label_source=USER_EDITED,
        conflicts=(), stop_rule_hits=(), state=first.state,
        sensitivity_state=first.sensitivity_state, dossier_id=None,
        llm_response_ref=None, validation_verdict_ref=None, created_by=RULES,
        created_at=created_at, supersedes=first.group_id,
        supersede_reason=("the rules merged P9's groups under the label and "
                          "situation the user supplied on the command line"))
    record_group(conn, reviewed)
    for result in grouped:
        # `grouping.store`'s carry, not a local one. `104` R-80 gives the MODEL a
        # supersession too -- a second, differing answer mints a superseding group
        # the same way this does -- and two transforms for one act is two things
        # to drift. The comment that used to be here is on the transform.
        carry_memberships(conn, from_group_id=result.group.group_id,
                          into_group_id=merged_id)
    record_acceptance(conn, GroupAcceptance(
        acceptance_id=f"acc:{merged_id}", plan_version_id=PLAN_VERSION,
        group_id=merged_id, membership_id=None, acceptance=ACCEPTED,
        review_state=PENDING_REVIEW, user_edited_label=label, aliases=(),
        review_decision_ref=None, decided_by=RULES, created_at=created_at))
    return merged_id


def choose_option(candidate, options) -> str:
    """§5.5, non-interactively: the first nesting §5.7's checks say may be built.

    Stated rather than hidden, because it IS a choice and a person at a review
    screen would make a different one. The options carry their counts, their
    warnings and their validation report; this takes the first that passes and
    would BUILD something, and falls back to the last option -- which is always
    `no-split` -- rather than raising, because a branch nobody could nest is
    still a branch.

    "Would build something" is not the same as "has children". A composition
    every level of which divides nothing creates no folder and is not empty: it
    populates the BRANCH with the values its files share, which is what makes the
    branch a destination P11's `direct_fact` channel can reach. Skipping it left
    a corpus that agrees on everything -- three files, one course, one term --
    with a branch that stated nothing, one candidate scored on group membership
    alone at 2/7, and "deciding this file needed a model" printed against facts
    P6 had already settled. `tree_design.materialise.branch_expectations` is
    where those values come from, and `VerticalOption.branch_expectations` is
    what carries them here.

    It is still a CHOICE, and still one this function makes without asking. The
    option beside it -- `keep-as-it-is` -- produces the same folders (none) and
    leaves the branch stating nothing, so a person who wants that can still say
    so and the question is still printed.
    """
    for option in options:
        report = option.validation
        if ((option.total_child_branches or option.branch_expectations)
                and (report is None or report.accepted)):
            return option.option_id
    return options[-1].option_id


#: `opt_no_split`'s key. `00`:99 offers "keep this branch as it is" beside every
#: composition and §5.5 makes it an answer rather than a fallback, so it needs a
#: name a person can choose by. Its `resulting_child_counts` is empty, which would
#: otherwise give it the same empty chain as any other unbuilt option.
NO_SPLIT_KEY: str = "keep-as-it-is"


def _nesting_key(option) -> str:
    """The stable identity of the shape one option would build.

    `resulting_child_counts` is keyed `field_ref or dimension_role`, one entry per
    level, built by iterating the levels IN ORDER -- so its keys are the chain,
    and a dict preserves that order. This is the value an answer records, and it
    has to outlive the run: `opt_2` names a different shape the moment the corpus
    changes, so a person would get a tree they never picked from an answer they
    really gave.
    """
    chain = tuple(option.resulting_child_counts)
    return ">".join(chain) if chain else NO_SPLIT_KEY


def _nesting_choices(options) -> tuple[NestingChoice, ...]:
    """`00`:99's cards, as P15 sees them.

    Every option the engine built, including the ones its own checks rejected --
    with the rejection IN the warnings. §5.5 shows the user what each option would
    create and why; hiding the failures would leave a person choosing between two
    shapes without being told the product thinks a third is wrong.
    """
    choices = []
    for option in options:
        # P10's `Warning_` is a record: a `reason` written for the person, wrapped
        # in three internal node ids they cannot act on. `NestingChoice.warnings`
        # is declared `tuple[str, ...]` and lands on the `--answer` line the
        # person is told to TYPE, so what goes there is the reason and nothing
        # else -- a repr on that line was the defect
        # `test_the_screen_never_prints_a_python_repr_or_an_internal_node_id`
        # pinned.
        #
        # QUOTED, because the reason is English and English has apostrophes:
        # "2 of this level's children hold 1 file(s) or fewer". The line it
        # lands on is one a person may paste whole, and a bare apostrophe
        # opens a shell quote that never closes -- the shell waits, and the
        # command the line exists to carry never runs. Inside double quotes
        # the words are the same words and the line still lexes as a line.
        warnings = [f'"{warning.reason}"' if hasattr(warning, "reason")
                    else warning for warning in option.warnings]
        report = option.validation
        if report is not None and report.failures:
            warnings.extend(f"{failure.check}: {failure.reason}"
                            for failure in report.failures)
        choices.append(NestingChoice(
            chain=tuple(option.resulting_child_counts) or (NO_SPLIT_KEY,),
            summary=option.summary,
            # The whole `label_chain`, joined -- two children of one name under
            # different parents are different folders, and `00`:99 puts "the
            # number of files under each child" in front of the person, which is
            # only readable if they can tell the children apart.
            child_counts=tuple(("/".join(child.label_chain), child.file_count)
                               for child in option.children),
            warnings=tuple(warnings)))
    return tuple(choices)


def nesting_chooser(conn: sqlite3.Connection, *, asked_at: str):
    """§5.5's choice, asked instead of taken -- `66` §12 inside the freeze.

    This is the moment `00`:78 describes: the engine has routed a branch, built
    every shape its facts support, and can say what each would create. The command
    took `options[0]` and disclosed that it had. The disclosure was honest and is
    not the same as asking.

    **Asking costs the person nothing, which is what makes it safe to ask here.**
    An unanswered question does not stop the run: the default is taken exactly as
    before, the tree is the tree they would have got, and the question is printed
    beside it. So the first run is no worse than it was, and the second run --
    `--answer branch:Coursework=subject` -- is theirs.

    One question per BRANCH, scoped to it, because §13 forbids reusing an answer
    "outside its stated scope" and how somebody wants their coursework shaped says
    nothing about how they want their legal matters shaped.
    """

    def choose(candidate, options) -> str:
        scope = f"{SCOPE_BRANCH}:{candidate.display_label}"
        by_key = {_nesting_key(option): option for option in options}
        answered = gated_template(conn, scope=scope)
        if answered is not None and answered in by_key:
            return by_key[answered].option_id
        # Two shapes or more is a decision; one is not, and §12 permits a question
        # only where "a specific decision is blocked".
        if len(by_key) > 1:
            record_question(conn, question_for_nesting(
                branch_label=candidate.display_label,
                choices=_nesting_choices(options),
                file_count=candidate.supporting_file_count), asked_at=asked_at)
        return choose_option(candidate, options)

    return choose


def refinement_for(node, file_count: int, *, was_split: bool) -> tuple[str, str]:
    """§5.8, per node. Every legal destination needs an answer or freeze refuses.

    A top-level branch is `refined` -- its levels came from settled facts. SO IS
    ANY BRANCH THAT WAS ACTUALLY SPLIT, and `was_split` is how this function is
    told. Until 2026-09-05 an adopted folder could not be split at all, so the
    question never arose; now `Desktop/Python 1006` gains `lecture` and
    `homework` from its own files, and the sentence about a top-level branch --
    "The levels beneath this branch were populated from facts that were already
    settled in your files" -- became literally true of it. It was being told
    `refine-later` instead, because the verdict is stamped BEFORE the branch is
    routed and `_with_refinement` skips a node that already carries one.
    `refine-later` on a branch that has just been refined is the same kind of
    false statement in the person's own voice that the file-count band was
    written to end, one field over.

    `was_split` is REQUIRED and keyword-only, for the reason `file_count` is: a
    default would let this function claim a branch was left unsplit without
    anything having looked. Both callers know the answer for certain -- the
    pre-routing stamp has genuinely not split anything yet, and the re-stamp in
    `_projection` is only reached when children were built.

    Below it the answer is a claim about a NUMBER, and until this function was
    handed one it made that claim without being able to check it: every node with
    a parent got `shallow-by-choice` and the sentence "This branch holds few
    enough files that splitting it further would not help you find anything". On
    a real corpus that sentence sat on `Desktop/Python 1006`, which holds 21
    files. A frozen tree is permanent and P13 shows the reason back to the person
    as their own words, so the sentence was a false statement about somebody's
    folder, in their voice, that nothing had measured.

    The band is `TREE_LIMITS.tiny_folder_max_files`, which is ALREADY this file's
    answer to "how few files is too few to be worth a folder" -- §5.9's tiny-folder
    warning reads the same number to tell the person a level's children hold one
    file or fewer. One reading of one band: at or under it, splitting genuinely
    cannot help, and the sentence now says the count so the person can disagree
    with it. A new number tuned until this corpus came out shallow would be the
    same false claim with arithmetic in front of it.

    Above the band the honest answer is `refine-later` and NOT `shallow-by-choice`.
    §5.8 keeps the two apart precisely so a deliberate design does not look like
    unfinished work, and `shallow-by-choice` literally means the person chose the
    shallowness. Run with nobody at the screen nobody chose anything, so the one
    thing that is true of a branch holding more files than the band is that its
    depth is still an open question -- which is what `refine-later` says. The
    reason deliberately makes no claim about whether the branch has children:
    this answer is stamped before the branch is routed, so a sentence that said
    "left as one folder" would be a second unchecked claim in the same place.

    **Every reason names its author, and none of them is the person.** The
    count fixed WHICH branches are called shallow; it did not fix WHO is
    recorded as having called them that, and `shallow-by-choice` on a branch
    nobody was shown is R-28's live half. SPEC:231 makes the reason the
    "user/evidence-backed explanation", so the reason is exactly where the
    author belongs -- and the word is not invented here: `actor_phrase`
    (`tree_design.provenance`) already returns "The rules" for
    `SURFACE_UNATTENDED`, and it is the subject §8.2's own event sentences
    carry on this run. One source, so a rename is one edit and the frozen tree
    and the audit log cannot disagree about who acted.

    The VALUE is left as the count found it. `refine-later` on a one-file
    branch would trade one false statement for another -- it says the depth is
    unfinished work, and there is nothing a single file can usefully be split
    into. What was wrong was never that a measured branch is called shallow; it
    was that the sentence beside it was written in the person's voice about a
    judgement they were never asked to make.

    **Each reason claims the actor and the count, and nothing else.** The rule
    two paragraphs up is not suspended by adding a subject to the sentence: a
    reason saying "left as one folder" would be the same unchecked claim about
    SHAPE that the paragraph forbids, and it would be false in a case that
    already exists -- an adopted folder nested under another adopted folder is
    never `was_split`, keeps its pre-routing verdict, and is not one folder. The
    actor and the number are both things this function has in its hands.
    """
    actor = actor_phrase(SURFACE_UNATTENDED)
    if node.parent_node_id is None or was_split:
        return (REFINED,
                f"{actor} built the levels beneath this branch from facts that "
                "were already settled in your files.")
    if file_count <= TREE_LIMITS.tiny_folder_max_files:
        return (SHALLOW_BY_CHOICE,
                f"{actor} counted {file_count} file(s) in this branch -- few "
                "enough that splitting it further could not help anyone find "
                "them. Nobody was asked, so say so if you want it split.")
    return (REFINE_LATER,
            f"{actor} counted {file_count} files in this branch. Nobody was "
            "asked how deep it should go, so it is not shallow on purpose -- "
            "how far it is split is yours to decide.")


# ======================================================================================
# The run
# ======================================================================================


def _bootstrap(conn: sqlite3.Connection) -> None:
    """Install every part's tables. `bootstrap_p1_p7` stops at P7; the rest are here.

    P8's eleven tables are created even though this deployment wires no model
    (`_resolver`'s `"llm": None`). That is not speculative: it is the same posture
    `bootstrap_p1_p7` already takes for P2, whose `create_eval_schema` it calls while
    the composition root passes `evaluation=None` a few hundred lines below. A part's
    durable surface belongs to the part, not to whether today's run reaches it.

    The alternative -- install P8's tables on the day a model is wired -- puts the
    install inside a branch, and a schema that exists only on some runs is the thing
    `record_dossier`'s ABORT triggers exist to make impossible. `create_budget_schema`
    follows `create_llm_schema` because its own docstring requires that order.
    """
    bootstrap_p1_p7(conn)
    create_grouping_schema(conn)
    create_tree_schema(conn)
    create_placement_schema(conn)
    create_questions_schema(conn)
    create_llm_schema(conn)
    create_budget_schema(conn)
    # P12's six and P13's three, on the same terms and for the same reason. The
    # census (`tests/integration/test_composition_root.py`) exists to catch a
    # part whose tables the run never creates, and it caught these: declared in
    # `src/` and created by nothing a person runs. A part's durable surface
    # belongs to the part, not to whether today's run reaches it.
    create_mutation_schema(conn)
    create_review_schema(conn)
    for name, key in CEILINGS.items():
        # Named, so the one that is not a spend ceiling is visibly not one, and so
        # that the one with a SECOND ANSWER elsewhere is visibly the same number as
        # the other answer. `model.max_dossier_tokens_per_call` was seeded at
        # `CEILING_VALUE` (8) while every request this deployment builds carries
        # `GROUPING_LIMITS.max_dossier_tokens` (4000) -- two answers to one question,
        # four hundred times apart, and the gate reads the stored one on purpose
        # ("a caller must not raise its own ceiling by echoing a larger one"). Eight
        # tokens is not a small budget, it is an unreachable one: no dossier that
        # says anything fits under it, so the number could only ever have been
        # decorative or catastrophic depending on whether anything measured. Now
        # something does (`fact_call_authorities`' `measure_tokens`), so the two
        # have to be one number, and `00`:251 names one ceiling, not two.
        if name == "max_residual_files_per_batch":
            value = FILES_PER_REVIEW_SCREEN
        elif name == "max_dossier_tokens":
            value = GROUPING_LIMITS.max_dossier_tokens
        # THE SAME RULING, TWICE MORE (`104` R-145). P11 replaces the observe
        # purse's rate and cost ceiling with these two stored numbers before every
        # site-C call ("a caller must not raise its own ceiling by echoing a
        # larger one"), and both were seeded at `CEILING_VALUE`. Eight calls per
        # THOUSAND files is one call on the owner's 199, and site B had spent it:
        # r12's ledger reads `calls_reserved=1` for `<scan>:observe` beside 60
        # site-C `BUDGET_EXHAUSTED` abstentions and no site-C dossier at all,
        # while `observe_scan_budget` had sized that purse at 199. Two answers to
        # one question again, and the stored one is the one that decides, so the
        # stored one is the purse's own number.
        elif name == "max_llm_calls_per_thousand_files":
            value = OBSERVE_CALLS_PER_1000_FILES
        elif name == "max_cost_per_scan":
            value = int(OBSERVE_CALLS_PER_SCAN_CEILING)
        else:
            value = CEILING_VALUE
        set_ceiling(conn, key, value)
    # §8.6's two per-file OCR ceilings, published because something obeys them.
    #
    # THE OTHER TWO P5 KEYS ARE LEFT UNSET ON PURPOSE. `ocr.max_time_per_scan` and
    # `image.max_analysis_ops_per_scan` have no enforcement point anywhere in `src/`:
    # nothing accumulates a per-scan OCR clock and nothing counts image operations.
    # `database_agent/budget.py` opens by saying "P1 holds and publishes values; P1
    # enforces none of them. Reading a ceiling is not enforcing it", and a published
    # number nothing obeys is worse than an absent one, because it reads as a bound
    # somebody chose. They stay absent until there is something to obey them.
    set_ceiling(conn, "ocr.max_pages_per_file", OCR_PAGE_CEILING)
    set_ceiling(conn, "ocr.max_time_per_file", OCR_SECONDS_PER_FILE)


def _validate_residuals(names: Sequence[str]) -> tuple[str, ...]:
    """Each name is one of §7.3's nine, spelled as §7.3 spells it.

    A misspelling that quietly enabled nothing would be the run reporting
    success for work it did not do, and the person would find out by looking for
    a folder that is not there. So it refuses, and it prints the nine -- a
    refusal that does not say what to type is half a refusal.
    """
    unknown = [name for name in names if name not in RESIDUAL_TEMPLATE_NAMES]
    if unknown:
        raise NotConfigured(
            f"{unknown[0]!r} names no residual area. §7.3 fixes nine and this "
            f"product invents none: {', '.join(RESIDUAL_TEMPLATE_NAMES)}. "
            f"`--list-residuals` prints them.")
    # Order is §7.3's, not the order they were typed, so two runs that enable
    # the same areas produce the same plan.
    return tuple(name for name in RESIDUAL_TEMPLATE_NAMES if name in set(names))


def _parse_sends(raw: Sequence[str]) -> Mapping[str, str]:
    """`--send-set "SET=AREA"`, split the way `--answer` splits its own pair.

    Only the SHAPE is checked here. Whether that set was surfaced and whether the
    plan has that area are questions about this run's plan version, which does not
    exist yet, and `act_on_residual_sets` refuses both by name once it does.
    """
    sends: dict[str, str] = {}
    for item in raw:
        label, sep, area = item.partition("=")
        if not sep or not label.strip() or not area.strip():
            raise NotConfigured(
                f"{item!r} is not a review set and a destination. Write it as "
                '--send-set "<the set as the report named it>=<a residual area '
                'this plan has>".')
        sends[label.strip()] = area.strip()
    return sends


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
        # The names this one nearly is, when there are any. A refusal saying
        # only how many situations exist leaves somebody who dropped a letter to
        # find it again in a list of 208, and `nearest_situations` offers
        # nothing at all rather than a wrong name -- a person pastes what this
        # prints, so a confident bad suggestion is worse than none.
        nearby = nearest_situations(catalogue, situation, limit=3)
        raise NotConfigured(
            f"{situation!r} names no situation the shipped template library "
            f"recognises. It carries {len(known)}, and `--list-situations` "
            f"prints them with what each one files."
            + (f"\n  Did you mean: {', '.join(nearby)}" if nearby else ""))
    return ref


def _identifier_observations(conn: sqlite3.Connection, file_id: str,
                             content_hash: str) -> frozenset[str]:
    """Which of this file's observations are structured identifiers.

    `00` states the recognition rule as "a course-code PATTERN TOGETHER WITH
    academic context such as 'syllabus,' 'lecture,' 'credits,' 'instructor,' or
    'semester'" -- one pattern and one term. The detector could only count TERMS,
    and `SchemaRules` carries no patterns, so a course code contributed exactly
    zero and `00`'s own worked example could not execute.

    THIS FILE owns the pattern: `_STRUCTURED` above is the only one that ships,
    and P5's SPEC keeps patterns in its Deferred table precisely so that no part
    holds one. So the detector is TOLD which observations are identifiers rather
    than working it out, which is the same seam `find_structured_strings` already
    is.

    Identified by the extractor that emitted them and by carrying a text span:
    the structured-string pass writes one observation per identifier, spanned
    inside the body, beside the span-less whole-body observation that is the
    document's own text. A locator test rather than a re-run of the regex, so
    this cannot disagree with what P4 actually recorded.
    """
    return frozenset(
        row[0] for row in conn.execute(
            "SELECT observation_key, location FROM evidence "
            "WHERE file_id = ? AND content_hash = ? "
            "AND extractor_name = ? AND superseded_by IS NULL",
            (file_id, content_hash, STRUCTURED_EXTRACTOR))
        if json.loads(row[1]).get("text_span") is not None)


def _sent_and_abstained(
        outcomes: Sequence[tuple[str, object]]) -> tuple[int, dict[str, int]]:
    """How many files a model ANSWERED about, and what stopped the rest short.

    `104` R-03: the screen said "from M files sent" and M was every outcome the
    pass produced, refusals included. A gate refusal sends nothing -- P7 denies
    before `transport.issue` opens a socket -- so the sentence counted files that
    never left the machine as files that did, on the one line a person reads to
    find out what happened to their folder.

    **A response is the test, and `P8Verdict` alone is not it.** A pre-call
    abstention comes back as a `P8Verdict` too: `_persist_abstention` mints one
    with `outcome=ABSTAIN` and hands it back, so a run that deferred every file
    for budget would report every file as sent while no model was asked at all.
    What separates them is `claim_ref`, which the harness sets to
    `PRE_CALL_NAMESPACE` for exactly this class of verdict, and that is what is
    read here rather than a type name.

    The second value is those abstentions by their own reason, so the caller can
    name them instead of leaving a file that was never asked looking like a file a
    model had nothing to say about.
    """
    sent = 0
    abstained: dict[str, int] = {}
    for _file_id, result in outcomes:
        claim_ref = getattr(result, "claim_ref", None)
        if claim_ref is None:
            # A refusal, a failed call, a consent question, a missing capability.
            # None of them is a response and none of them is counted as one.
            continue
        if claim_ref == PRE_CALL_NAMESPACE:
            # No fallback for an unstated reason, because there is no such verdict:
            # `P8Verdict.__post_init__` checks every member of `reasons` against
            # `ALL_REASON_CODES`, so one cannot be built without at least one. A
            # default here would be a case that cannot happen, written as though it
            # could, and the next reader would keep it alive for that reason.
            for reason in result.reasons:
                abstained[reason] = abstained.get(reason, 0) + 1
            continue
        sent += 1
    return sent, abstained


#: WHY THE ROUTE WITHHELD A FILE, in the words the screen uses. One `PRIVACY_BAR`
#: covers three different sentences and a person is owed the one that is true about
#: their file: a protected file was withheld BECAUSE it is protected, and telling
#: them nothing had classified it is false about a file the detector classified.
WITHHELD_UNCLASSIFIED: str = "unclassified"
WITHHELD_PROTECTED: str = "protected"
WITHHELD_PRIVACY: str = "privacy"

#: `104` R-37's two reasons a file is asked nothing, beside the three above.
#: `NOT_ASKED_AMBIGUOUS` is a file TWO branches of this folder reach, so no one
#: branch's question applies (`104` R-140: a file NO branch reaches is asked the
#: default branch's questions, and is not here); `NOT_ASKED_UNSETTLED` is a file
#: under a branch whose situation the person has not yet chosen, so there is no
#: question of that branch's to put to a model.
NOT_ASKED_AMBIGUOUS: str = "two_branches"
NOT_ASKED_UNSETTLED: str = "branch_unsettled"

NOT_ASKED_SENTENCE: Mapping[str, str] = MappingProxyType({
    NOT_ASKED_AMBIGUOUS:
        "two of the folders this run proposes reach them equally, so neither "
        "folder's question applies to them yet. They are held for you below, "
        "under the reason the plan records for each.",
    NOT_ASKED_UNSETTLED:
        "they sit under a folder you have not yet said the situation of, and a "
        "model is asked a folder's questions only once its situation is known. "
        "The question is printed below with the answers you can give.",
    # `104` §18.2 GAP 4'S FIVE, AND THEY ARE THE HALF OF THIS SCREEN THAT WAS
    # MISSING. The two rows above are about the FOLDER a file sits in; these are
    # about the file itself, and until this ruling every one of them was reported
    # as a file a model had been asked about and had had nothing to say. The words
    # are `model_facts.NOT_ASKED_REASONS`' own -- one sentence per word, never a
    # shared bucket, because the thing a person would DO about each is different:
    # nothing (settled), change the policy (no route), install a reader (nothing
    # read), nothing (every reading refused, which is the privacy rules working),
    # choose a different situation (no field in schema).
    model_facts.NOT_ASKED_SETTLED:
        "every field this situation asks about them was already settled by what "
        "this device could read on its own, so there was nothing left to ask a "
        "model. Nothing about them is missing.",
    model_facts.NOT_ASKED_NO_ROUTE:
        "no model this run could reach is cleared to see them, so nothing about "
        "them was assembled for one. Each open field has an `unresolved` row "
        "saying `privacy_withheld`.",
    model_facts.NOT_ASKED_NOTHING_READ:
        "nothing could be read out of them, so there was no evidence to put in "
        "front of a model. That is about this product's readers and the file's "
        "format, not about what the file contains.",
    model_facts.NOT_ASKED_ALL_REFUSED:
        "everything this run read out of them is material that does not leave "
        "this device -- a file path, an image's text, or a value something "
        "recognised as personal -- so a model was shown none of it and was not "
        "asked. The readings are still on this machine and are still yours.",
    model_facts.NOT_ASKED_NO_SCHEMA:
        "the situation this run is working under declares no field that could "
        "hold an answer about them, so there was nothing to ask. A different "
        "`--situation` asks a different set of questions.",
})

#: The sentence each cause earns. Written out rather than assembled, because a
#: reason a person reads is prose and not a code with a template around it.
WITHHELD_SENTENCE: Mapping[str, str] = MappingProxyType({
    WITHHELD_UNCLASSIFIED:
        "nothing has said yet what kind of material they are, and this product "
        "will not ask a model about a file until something has. This is about "
        "the detector, not about your files.",
    WITHHELD_PROTECTED:
        "they are protected material, so nothing about them was "
        "assembled for a model. That is a decision about sensitivity and not a "
        "gap in what this run could read.",
    WITHHELD_PRIVACY:
        "this folder's privacy policy does not clear them for the model this "
        "run would ask.",
})

#: `104` §18.2 gap 10, and the constitution's "coverage is sacred". THE SIX
#: BUCKETS EVERY INDEXED FILE FALLS IN, exactly one each.
#:
#: **Every one of them is a word this build already uses.** `WITHHELD_PROTECTED`
#: is the fact pass's own name for a file P7 marked; `UNREADABLE` is P13's, off
#: `review_surface.progress`, where §8.6's line spells it; `DEFERRED` is P4's, and
#: is the constant this file already declares for the ceiling that never started.
#: The other three name outcomes the code has always had and never had a word for
#: -- a file the rules settled, a file a model answered about, a file that was not
#: asked -- and they are spelled once, here, so no screen respells one.
#:
#: A SEVENTH BUCKET WOULD BE A DEFECT and not an addition. The sum is what a person
#: checks the report with, and a bucket is only worth having if a file can be in it
#: and in no other; the moment two of them could hold one file the arithmetic stops
#: meaning anything. `_reconcile_the_roster` states the precedence that keeps them
#: disjoint and argues it, because an order that decides an outcome is a ruling.
COVERAGE_SETTLED: str = "settled by rule"
COVERAGE_ASKED: str = "asked a model"
COVERAGE_NOT_ASKED: str = "not asked"

#: WHY THE FACT PASS NEVER RAN AT ALL, for the reconciliation that must print
#: anyway. `104` §18.2 gap 10 says the sum runs on an ORDINARY run, and the four
#: conditions `_model_fact_pass` returns on are ordinary: no key and no local
#: model, a key whose site has no destination this mode permits, an empty roster,
#: no wire handle key. Under every one of them the old report simply had no line
#: for any file, which is the silence the whole gap is about.
#:
#: Each is a condition the pass already tests and already comments on; what is new
#: is that the reason is CARRIED OUT rather than dropped at a bare `return`. A file
#: under one of these is `COVERAGE_NOT_ASKED` and not `COVERAGE_SETTLED`: nothing
#: settled its open fields, and reporting it as settled would be the false
#: impression `00`:259 names in as many words.
NOT_RUN_NO_MODEL: str = "no_model_configured"
NOT_RUN_NO_DESTINATION: str = "no_destination_this_mode_permits"
NOT_RUN_NO_HANDLE_KEY: str = "no_wire_handle_key"

#: The sentence each cause earns, on `WITHHELD_SENTENCE`'s rule: prose, not a code
#: with a template around it. The three not-run causes are here beside the reasons
#: the pass produces when it DOES run, because a person reading one line does not
#: care which of the two produced it -- they care what happened to their file.
COVERAGE_SENTENCE: Mapping[str, str] = MappingProxyType({
    NOT_RUN_NO_MODEL:
        "no model is configured for this run, so nothing could be asked about "
        "them. What this device could read and decide on its own still stands.",
    NOT_RUN_NO_DESTINATION:
        "no model this run may use has a destination for the fact question -- a "
        "cloud model needs this folder's sending turned on, and there is no "
        "model on this device to fall back to.",
    NOT_RUN_NO_HANDLE_KEY:
        "this run has no wire handle key, and every identifier that reaches a "
        "model is digested under one. There is no un-keyed form to fall back to.",
    NOT_ASKED_AMBIGUOUS: NOT_ASKED_SENTENCE[NOT_ASKED_AMBIGUOUS],
    NOT_ASKED_UNSETTLED: NOT_ASKED_SENTENCE[NOT_ASKED_UNSETTLED],
    # `104` §18.2 gap 4's five: the stage's own reasons for declining to ask,
    # each with the sentence `NOT_ASKED_SENTENCE` already gives it, so the
    # coverage sum and the fact block say the same thing about one file.
    **{reason: NOT_ASKED_SENTENCE[reason]
       for reason in model_facts.NOT_ASKED_REASONS},
    WITHHELD_UNCLASSIFIED: WITHHELD_SENTENCE[WITHHELD_UNCLASSIFIED],
    WITHHELD_PRIVACY: WITHHELD_SENTENCE[WITHHELD_PRIVACY],
    WITHHELD_PROTECTED: WITHHELD_SENTENCE[WITHHELD_PROTECTED],
})


def _dossier_cut(conn: sqlite3.Connection,
                 outcomes: Sequence[tuple[str, object]]) -> tuple[int, int, int]:
    """What the dossier ceiling took from this pass's calls: calls, readings, bytes.

    `104` §18.2 gap 5. `model_facts.within_dossier_budget` drops the readings that do
    not fit and `GroundingReport.readings_dropped` / `readings_dropped_bytes` record
    what it dropped; this sums those over the calls this pass made and hands
    `_print_fact_pass` three numbers.

    **Off the STORED reports, not off a counter in the loop.** The rule this screen
    is built on is that a count a person reads is read back from the records -- the
    same rule `ResolveResult.reason_counts` follows for the `unresolved` table -- so
    that a number on the screen and a number in the database cannot disagree. The
    address is the outcome's own `dossier_id`: a verdict carries the dossier it was
    judged from, and a pre-call abstention carries `pre_call_address`, so a deferred
    call whose evidence had already been trimmed is counted too. An outcome with no
    address at all -- a `NeedsConsent`, a request that could not be described -- is
    skipped rather than guessed at.

    **A call is counted as trimmed once, however many readings it lost.** "Twelve
    readings were dropped" is a different sentence when it is twelve calls losing one
    each and when it is one spreadsheet losing twelve, and the call count is what
    tells the two apart.

    **AND A REFUSAL CARRIES NO ADDRESS OF ITS OWN, so one is derived.** `Refusal` is
    built from P7's `Denied` and `CallRefused` from an exception's class name;
    neither holds a `dossier_id`, because at the moment either is made no dossier has
    been recorded. Their reports are still written -- `_zero_report` reads the cut
    straight off the request -- and they are addressed by `pre_call_address`, which
    this derives from the file id the outcome came in beside. Derived ONLY when the
    outcome names no address itself: a file deferred on one pass and answered on the
    next has a report at each address, and asking for both would count one file's cut
    twice.
    """
    addresses: list[str] = []
    for file_id, result in outcomes:
        address = getattr(result, "dossier_id", None)
        if not isinstance(address, str):
            # A call that HAPPENED and failed carries its own request identity;
            # anything else is a refusal at or before the door.
            address = getattr(result, "request_identity", None)
        if not isinstance(address, str):
            address = pre_call_address(A_FACT, file_id)
        addresses.append(address)
    calls = readings = dropped_bytes = 0
    for report in grounding_counters(conn, addresses):
        dropped = report.get("readings_dropped") or 0
        if not dropped:
            continue
        calls += 1
        readings += dropped
        dropped_bytes += report.get("readings_dropped_bytes") or 0
    return calls, readings, dropped_bytes


def _print_fact_pass(*, written: int, withheld: Mapping[str, int], files: int,
                     outcomes: Sequence[tuple[str, object]], model_id: str,
                     out, not_asked: Mapping[str, int] = MappingProxyType({}),
                     cut: "tuple[int, int, int]" = (0, 0, 0),
                     ) -> None:
    """What the model pass actually did, in counts a person can check.

    **The withheld count is the line that earns this block.** On a real folder most
    files reach `model_route_permitted` with no classification and are never asked
    -- 45 of 54 on the owner's own measured slice -- and without this sentence the
    report reads as a model having nothing to say about them. It is a fact about
    THIS PRODUCT'S detector and about a decision that is still open, not a fact
    about their files, and the standing rule is that what was skipped is counted and
    named rather than silently omitted.

    **Every other outcome is named too, by its own reason.** A refused release, a
    call that failed, an abstention and a validation that could not run are four
    different things that all look like "no fact" from the outside, and collapsing
    them into one number is how a person reads a broken key as an unhelpful model.

    **`cut` IS `104` §18.2 GAP 5'S LINE: what the dossier ceiling took (calls,
    readings, bytes).** The ceiling has always dropped readings that would not fit
    and until this ruling it dropped them in silence -- a bare `continue` in
    `model_facts.within_dossier_budget` -- so a file whose whole evidence reached the
    model and a file that offered forty readings and carried four produced the same
    line on this screen. `00`:257 asks for the opposite: a prompt over its budget
    "should not truncate silently in a way that removes the decisive evidence."
    Three numbers because one cannot say it -- how many CALLS were trimmed is what
    tells a person whether this is their whole folder or one spreadsheet, and the
    readings and the bytes are how much. Summed by the caller off the stored
    `GroundingReport`s of this pass's own calls, which is where the builder recorded
    the cut.
    """
    if not files:
        return
    kinds: dict[str, int] = {}
    for _file_id, result in outcomes:
        kinds[type(result).__name__] = kinds.get(type(result).__name__, 0) + 1
    # RESPONSES, NOT OUTCOMES. `104` R-03: a gate refusal sends nothing, and this
    # line used to count one as a file sent.
    asked, abstained = _sent_and_abstained(outcomes)
    print(f"\nFacts from a model: {written} written, from {asked} "
          f"{'file' if asked == 1 else 'files'} sent to {model_id}.", file=out)
    if abstained:
        # THE STAGE THAT RECORDED ITSELF AND SAID NOTHING. `_persist_abstention`
        # writes an `llm_pre_call_abstention` row and mints an abstaining verdict,
        # and the screen had no line for either -- so a file the run decided not
        # to ask about read exactly like a file a model shrugged at. One line,
        # named by the reason the harness recorded, because "the dossier would not
        # fit" and "this scan has spent its budget" are different sentences to a
        # person and only one of them is about their file.
        for reason, count_ in sorted(abstained.items()):
            print(f"  {count_} not asked: {reason.replace('_', ' ')} "
                  f"({reason}), decided before any call was made.", file=out)
    trimmed_calls, dropped_readings, dropped_bytes = cut
    if trimmed_calls:
        # `104` §18.2 gap 5. Printed whenever anything was cut, including on a run
        # where every call was then refused: the builder had already spent the
        # ceiling by then, and a person told nothing was cut because the call never
        # went out would be told the wrong thing twice.
        print(_wrapped(
            f"{dropped_readings} "
            f"{'reading' if dropped_readings == 1 else 'readings'} "
            f"({dropped_bytes:,} bytes) did not fit in what one call may carry and "
            f"were left out of {trimmed_calls} of them. The model was shown the "
            f"rest, in the order the document is read in; nothing was deleted and "
            f"nothing was refused -- what did not fit is still on this machine and "
            f"is read again on the next run.", indent="  "), file=out)
    for cause, count_ in sorted(withheld.items()):
        print(_wrapped(
            f"{count_} of {files} files were not sent, and were not skipped "
            f"quietly: {WITHHELD_SENTENCE[cause]} Each one has an `unresolved` "
            f"row per open field saying `privacy_withheld`, so none of them is "
            f"recorded as a file with nothing to say.", indent="  "), file=out)
    # `104` R-37. A file two of the run's branches reach, or a file under a
    # branch whose situation the person has not yet said, was not shown to a
    # model under a question that does not apply to it. Named by its own reason,
    # like the withheld files above, and only when a run has more than one
    # branch: with one, nothing is here and the screen is the screen it was.
    for reason, count_ in sorted(not_asked.items()):
        print(_wrapped(
            f"{count_} of {files} files were not asked anything: "
            f"{NOT_ASKED_SENTENCE[reason]}", indent="  "), file=out)
    named = {"CallFailed": "the call did not come back",
             "ValidationUnavailable": "something the check needed was missing",
             "NeedsConsent": "it needs an answer from you first"}
    for kind, count_ in sorted(kinds.items()):
        if kind in named:
            print(f"  {count_} refused: {named[kind]} ({kind}).", file=out)
    # `104` R-O's line. A refusal raised inside a model-site call used to end the
    # run with a traceback and no report at all, so there was nothing here to
    # print; now it is an outcome, and an outcome a person is never told about is
    # the same silence with better manners. Grouped by WHAT REFUSED, because
    # "the gate could not read one of the items" and "the request could not be
    # described" are different things for the lead to fix and the same
    # non-event for the person.
    refused_calls: dict[str, int] = {}
    for _file_id, result in outcomes:
        if isinstance(result, CallRefused):
            refused_calls[result.refusal_class] = (
                refused_calls.get(result.refusal_class, 0) + 1)
    for refusal_class, count_ in sorted(refused_calls.items()):
        print(_wrapped(
            f"{count_} refused: a part of this product declined to answer and the "
            f"run went on without it ({refusal_class}). Nothing about "
            f"{'those files' if count_ != 1 else 'that file'} was decided by a "
            f"model; what this device could read and decide on its own still "
            f"stands, and the next run asks again.", indent="  "), file=out)
    # THE GATE'S OWN WORD, NOT THE CLASS NAME. "the gate refused the release
    # (Refusal)" names the Python type that carried the answer and says nothing
    # about the answer: protected material and a dossier over the ceiling are
    # different things to do something about, and P7 already decided which it was.
    # `Denied.reason` is that decision, and it is a closed vocabulary the gate
    # checks on construction, so it is safe to print as-is.
    refused: dict[str, int] = {}
    for _file_id, result in outcomes:
        denied = getattr(result, "denied", None)
        reason = getattr(denied, "reason", None)
        if isinstance(reason, str):
            refused[reason] = refused.get(reason, 0) + 1
    for reason, count_ in sorted(refused.items()):
        print(f"  {count_} refused by the gate before anything was sent: "
              f"{reason.replace('_', ' ')} ({reason}).", file=out)


#: `104` §18.2 gap 9. ONE SENTENCE PER `SituationPass` COUNTER, in the person's
#: own words, written out rather than assembled -- `WITHHELD_SENTENCE`'s rule one
#: block up, and for its reason: a reason a person reads is prose and not a code
#: with a template around it. Each value begins with the outcome's own short name,
#: because the line it goes on is `"{count} {value}"` and the count is meaningless
#: without the word beside it.
#:
#: `no_route` BORROWS THE FACT PASS'S OWN SENTENCE rather than restating it. It is
#: the same fact about the same files -- `target_for` returns nothing for a file
#: P7 marked, on every locality, so nothing about it was assembled for site G
#: either -- and two sentences about one fact are how two blocks on one screen come
#: to disagree. `104` §18.2 gap 9 calls this counter "the protected-file count the
#: design wanted surfaced", and this is where it is surfaced.
SITUATION_SENTENCE: Mapping[str, str] = MappingProxyType({
    "settled":
        "settled by rule: the recognisers named what they are from their own "
        "words, so no model was asked about them. `00`:110 reserves the model "
        "for what the rules cannot settle, and this is that rule holding.",
    # TWO "NOT ASKED" LINES, AND EACH SAYS WHICH ONE IT IS IN ITS FIRST THREE
    # WORDS. A first version began both with the bare phrase, and the block then
    # printed two lines reading "0 not asked" with different paragraphs under
    # them -- a reader has to get to the third line of prose to find out they are
    # different facts, and a reader scanning counts never gets there at all.
    "nothing_to_ask":
        "not asked, no candidate: nothing that could be read out of them offered "
        "a candidate situation at all, so there was no question to put to a "
        "model. That is about what this product could read, not about what they "
        "are.",
    "nothing_to_read":
        "not asked, nothing to read: a shortlist of situations existed for them "
        "and no releasable reading did, so the question could not be asked from "
        "anything. Nothing about them was assembled and nothing was sent.",
    "declined":
        "asked and left alone: a model was asked and named no situation it could "
        "cite, or the check did not accept the one it named. They keep this "
        "run's own situation, which is where the rules had already left them.",
    # `104` §18.7 (9 Sep 2026): protected material reaches the LOCAL model, so
    # this is no longer the protected count on a run with a local target. It is
    # the files no model this site may use could take -- protected material
    # where the only destination is a cloud one, or no destination wired. The
    # sentence says what the counter IS rather than borrowing the fact pass's
    # protected line, which would name a reason that is no longer the reason.
    "no_route":
        "no target: no model this site may use could take them -- protected "
        "material where the only destination was a cloud one, or no model "
        "wired at all. Nothing about them was assembled and nothing was sent; "
        "they keep this run's own situation.",
})

assert set(SITUATION_SENTENCE) | {"named", "holds"} == {
    field.name for field in dataclasses.fields(SituationPass)}, (
    "every counter site G leaves behind earns a sentence on the screen. A "
    "counter with no sentence would be a number this report silently drops, "
    "which is the defect `104` §18.2 gap 9 is about -- so a new one fails to "
    "import rather than going unprinted")

#: `104` §18 gap 24: WHAT BECAME OF THE HOLDS, in the person's words.
#:
#: A block of its own and not four more lines under the six above, because these
#: do not partition the roster -- see `PrecautionHolds`. `held` is the
#: denominator and is stated once in the block's header, exactly as `named` heads
#: the block above; the three sentences here divide it, so the numbers under the
#: header add up to it. Same arithmetic, same reason for offering it.
#:
#: The word "the rules" and the word "the model on this device" are the two
#: actors a person has to be able to tell apart here. A hold the rules took and a
#: hold the model agreed with are different facts about their file, and until
#: this block existed both read as "protected" with nothing saying which.
HOLD_SENTENCE: Mapping[str, str] = MappingProxyType({
    "released":
        "released by the model: it named an ordinary situation, cited it, the "
        "check accepted the answer, and it named no restricted kind. The hold "
        "is superseded -- not deleted -- and those files are ordinary for the "
        "rest of this run.",
    "confirmed":
        "confirmed by the model: it agreed the file is one of the four "
        "protected kinds, or it named a restricted document kind. The hold "
        "stands and the record now shows the model agreed rather than showing "
        "only that the rules had guessed.",
    "still_held":
        "still held because nothing could say: the model declined, or the "
        "check refused its answer, or the call did not come back, or there was "
        "nothing releasable to ask from. Silence never lifts a hold, so they "
        "stay protected and stay on this device.",
})

assert set(HOLD_SENTENCE) | {"held"} == {
    field.name for field in dataclasses.fields(PrecautionHolds)}, (
    "the same rule one record along: a hold count with no sentence is a number "
    "about somebody's protected file that no screen says out loud. `held` is "
    "the block's own header, exactly as `named` is the block above's")


def _print_situation_pass(situation: SituationPass, *, files: int,
                          model_id: str, out) -> None:
    """Site G's six counters, in the shape the fact pass prints its own.

    **`104` §18.2 gap 9: these counts reached nobody.** `cli.py` initialised the
    cell, the pass filled it, and no line of the report ever read it -- so the one
    site that decides whether a file may reach the cloud at all ran on every
    ordinary run and left nothing a person could see. `00`:259 is the standing rule
    it broke: the interface "should show the difference between completed work and
    deferred work", and it exists so a person is not left with "the false
    impression that an unprocessed file was understood and found unimportant".
    Every file site G did not name is exactly such a file.

    **THE SHAPE IS `_print_fact_pass`'S AND IS NOT A SECOND ONE.** A header naming
    what was decided and for how many of how many files, then one indented line per
    outcome carrying its own count and its own reason -- because "a model declined
    to name this file's situation" and "this file may never be asked at all" are
    different sentences to a person and only one of them is about their file. Two
    blocks in two shapes on one screen would read as two products.

    **ALL SIX, INCLUDING THE ZEROS, and that is the difference from the fact pass
    block.** These counters PARTITION the roster -- every file the pass walked
    lands in exactly one of them -- so the six numbers are an arithmetic a person
    can check against the total, and a zero that disappears makes that arithmetic
    unreadable. `104` §17.2 is what a number with no provenance costs; a missing
    line is the same cost paid silently.

    **A PASS THAT DID NOT RUN PRINTS NOTHING**, and that is `_NOTHING_ASKED`'s own
    ruling one layer up: a run where site G was not asked and a run where it was
    asked and named nothing "must not read the same downstream". Six zeros under a
    header is precisely how the two would come to read the same.

    The model is named for `_local_model_id`'s reason and G's row is why it is the
    local one: `ratified_local` (`104` §17.14), so `target_for` drops the cloud
    candidate for every file and this site is answered on this machine or not at
    all.
    """
    if situation is _NOTHING_ASKED or not files:
        return
    named = len(situation.named)
    # The blank line on its own `print`, because `textwrap.fill` collapses the
    # whitespace in its input and a `\n` inside the header would simply vanish.
    print("", file=out)
    print(_wrapped(
        f"Situations from a model: {named} of {files} "
        f"{'file was' if files == 1 else 'files were'} given "
        f"{'its' if named == 1 else 'their'} own situation by {model_id} on this "
        f"device, instead of being asked this run's questions. Nothing about any "
        f"of them left the device: this is the site that decides whether a file "
        f"may be sent at all, so it is never asked anywhere else.", indent=""),
        file=out)
    for field in dataclasses.fields(SituationPass):
        if field.name in ("named", "holds"):
            continue
        print(_wrapped(f"{getattr(situation, field.name)} "
                       f"{SITUATION_SENTENCE[field.name]}", indent="  "),
              file=out)
    _print_the_holds(situation.holds, out=out)


def _print_the_holds(holds: PrecautionHolds, *, out) -> None:
    """`104` §18 gap 24: what became of the holds the rules had taken.

    **A BLOCK OF ITS OWN, and the reason is arithmetic.** The six lines above
    partition the roster and their sum is the total a person can check. These
    three partition `held` instead -- a released file is also one of the six --
    so printing them in that loop would give a reader six numbers that no longer
    add up and no way to know which of them to distrust.

    **NOTHING IS PRINTED WHERE THE RULES HELD NOTHING**, on the same rule
    `_print_situation_pass` applies to a pass that did not run: a heading over
    four zeros invites a person to wonder which of their files it is about, and
    the answer is none of them. A run with no held file has nothing to say here
    and says nothing.

    The header names the denominator once, so the three lines under it are a sum
    a person can check against it -- and `still_held` is derived from the other
    two, so the check cannot fail for a reason that is this screen's fault.
    """
    if not holds.held:
        return
    print("", file=out)
    print(_wrapped(
        f"Protected holds the model looked at: the rules were holding "
        f"{holds.held} {'file' if holds.held == 1 else 'files'} on a safety "
        f"term, and every one of them was put to the model on this device -- "
        f"never anywhere else. A hold is only ever lifted by an answer; nothing "
        f"here is lifted by silence, and no hold was deleted.", indent=""),
        file=out)
    for field in dataclasses.fields(PrecautionHolds):
        if field.name == "held":
            continue
        print(_wrapped(f"{getattr(holds, field.name)} "
                       f"{HOLD_SENTENCE[field.name]}", indent="  "), file=out)


def _protected_file_ids(conn: sqlite3.Connection) -> set[str]:
    """Every file P7 currently marks protected. ONE query, for three readers.

    `_protected_file_count`, `_nothing_could_be_read_report` and (since `104` §18.2
    gap 10) the roster reconciliation all need the same set, and the SAME set: the
    screen prints a protected count in three places and three readings of one
    column is how they would come to differ by one and leave a person deciding
    which number is about their folder.
    """
    return {row[0] for row in conn.execute(
        "SELECT DISTINCT file_id FROM classifications "
        "WHERE protected = 1 AND superseded_by IS NULL")}


def _protected_file_count(conn: sqlite3.Connection, scan_run_id: str) -> int:
    """How many of THIS scan's files P7 marked protected. `104` R-J.

    Over the roster and not over the whole table, because the count sits beside a
    count of this run's containers and a number from an earlier scan of another
    folder would make the total a sum of two different questions.

    The same query `folders_nothing_could_be_read_from` already asks -- current
    classification rows, `protected = 1` -- so the screen's two protected counts
    cannot come from two readings of the same column.
    """
    withheld = _protected_file_ids(conn)
    return sum(1 for file_id, _hash in corpus_roster(conn, scan_run_id)
               if file_id in withheld)


def _verdicts_from_outcomes(
        outcomes: Sequence[tuple[str, object]]) -> dict[str, tuple[str, str | None]]:
    """What the model calls say about each file, for `104` §18.2 gap 10's sum.

    **`_sent_and_abstained`'S RULING, PER FILE INSTEAD OF PER RUN.** That function
    already decides what counts as a response and what does not, and its reasons
    are `104` R-03's: a gate refusal sends nothing, and a pre-call abstention comes
    back as a `P8Verdict` too, so neither is a model answering. Deciding it a second
    time here would let the closed sum and the "from N files sent" line printed a
    few lines above it come to disagree about the same run -- which is the whole
    class of defect this block exists to make visible.

    **A FILE WITH SEVERAL OUTCOMES IS ONE FILE.** `on_result` fires per result and a
    file may produce more than one, so the strongest wins: a response outranks an
    abstention, and an abstention outranks a refusal that carries no reason of its
    own. Anything else would make the sum depend on the order the pass happened to
    append in.

    **A REFUSAL AND A FAILED CALL COUNT AS `COVERAGE_NOT_ASKED`, WITH THEIR OWN
    REASON BESIDE THEM.** Calling them "asked a model" would restate the number
    `104` R-03 was fixed to stop overstating; leaving them out of the sum would be
    the omission this whole block is against. What a person reads is "not asked"
    with the honest reason on the next line -- the call did not come back, the gate
    refused the release -- rather than a file that looks like one a model shrugged
    at.
    """
    verdicts: dict[str, tuple[str, str | None]] = {}
    for file_id, result in outcomes:
        claim_ref = getattr(result, "claim_ref", None)
        if claim_ref is not None and claim_ref != PRE_CALL_NAMESPACE:
            verdicts[file_id] = (COVERAGE_ASKED, None)
            continue
        if verdicts.get(file_id, (None, None))[0] == COVERAGE_ASKED:
            continue
        if claim_ref == PRE_CALL_NAMESPACE:
            # `P8Verdict.__post_init__` checks every member of `reasons`, so one
            # cannot be built without at least one. The first is the one named:
            # a line naming all of them would be a paragraph about one file.
            verdicts[file_id] = (COVERAGE_NOT_ASKED, result.reasons[0])
            continue
        # A refusal that named itself keeps its own word; one that did not is
        # named by the class that carried it, which is what `_print_fact_pass`
        # already does two paragraphs above and for the same reason -- "the gate
        # could not read one of the items" and "the request could not be
        # described" are different things and the same non-event.
        verdicts.setdefault(file_id, (
            COVERAGE_NOT_ASKED,
            getattr(result, "refusal_class", None) or type(result).__name__))
    return verdicts


#: P4's two ceiling completenesses, and they are NOT interchangeable: `capped` read
#: something and stopped, `deferred` never started. `extractors/stage_output.py`
#: holds them as one tuple because both mean "a budget was reached"; the sentences
#: they earn are different, which is why each is named here.
#:
#: MOVED UP FROM BESIDE `_no_extractor_cause` on `104` §18.2 gap 10, AND NOT
#: COPIED: the roster reconciliation below names `DEFERRED` as one of its six
#: buckets, and a second spelling of a P4 completeness state in this file is
#: exactly the second home a published vocabulary exists to prevent.
#: `_no_extractor_cause` and `_CAPPED_BY_SOURCE_TYPE` still read these two from
#: further down the file and are otherwise unchanged.
CAPPED: str = "capped"
DEFERRED: str = "deferred"


#: The six buckets in the order they are printed, and the order is an argument.
#: `00`:259 asks the interface to "show the difference between completed work and
#: deferred work", so the line reads from the most finished outcome to the least:
#: a file the rules settled needed nothing, a file a model answered about got what
#: it needed, and everything below those is work that did not happen, ending with
#: the two that say the product could not or would not do it. A person scanning
#: down stops where the news starts.
_COVERAGE_ORDER: tuple[str, ...] = (
    COVERAGE_SETTLED, COVERAGE_ASKED, COVERAGE_NOT_ASKED, WITHHELD_PROTECTED,
    UNREADABLE, DEFERRED)

#: WHICH §8.6 STATE EACH BUCKET REPORTS AS, and P13's three words rather than any
#: of this file's own. A `ProgressEntry` carries one, `assert_every_file_accounted`
#: is written against that record, and a fourth state invented here would be a
#: second vocabulary for the thing P13 publishes.
_COVERAGE_STATE: Mapping[str, str] = MappingProxyType({
    COVERAGE_SETTLED: STATE_COMPLETED,
    COVERAGE_ASKED: STATE_COMPLETED,
    COVERAGE_NOT_ASKED: STATE_DEFERRED,
    WITHHELD_PROTECTED: STATE_BLOCKED,
    UNREADABLE: STATE_BLOCKED,
    DEFERRED: STATE_DEFERRED,
})


class FileInTwoBuckets(RuntimeError):
    """One indexed file reached two of the six buckets. The sum does not close.

    The mirror of `review_surface.progress.FileAbsentFromEveryEntry`, and it is a
    refusal for the same reason: a coverage line a person cannot add up is a
    coverage line that tells them nothing, and one that quietly overcounts tells
    them something false. `104` §18.2 gap 10 asks for a CLOSED sum, and closed is
    both directions.
    """


def _reconcile_the_roster(conn: sqlite3.Connection, *, run_id: str,
                          verdicts: Mapping[str, tuple[str, str | None]],
                          not_run: str | None, out) -> None:
    """One closed sum over every indexed file, at the end of the fact pass.

    **`104` §18.2 gap 10, and the constitution's "coverage is sacred".**
    `assert_every_file_accounted` -- "no indexed file may be absent from every
    entry" -- was written, tested, and reachable from `src/` only down
    `_nothing_could_be_read_report`, the screen for a folder NOTHING could be read
    out of. So the rule held on the one run where a person could see the answer by
    looking, and held on no ordinary run at all: a file the deterministic producers
    settled got no line anywhere, and a person had a report full of counts with no
    way to tell whether the counts covered their folder. `00`:259 names exactly the
    impression that leaves -- "that an unprocessed file was understood and found
    unimportant".

    **IT RUNS WHETHER OR NOT THE FACT PASS DID.** That is why it is a function of
    its own called after the pass rather than a block at the end of it: the pass has
    four early returns -- no model, no destination this mode permits, an empty
    roster, no wire handle key -- and every one of them is an ordinary way for a run
    to go. A sum that disappeared under them would be missing on precisely the runs
    where a person is most likely to wonder what happened to their files. The pass
    hands out its reason instead of dropping it at a bare `return`.

    **THE PRECEDENCE IS A RULING AND NOT A SORT ORDER**, so it is stated:

    1. **The fact pass's own verdict for that file first**, because it is the finer
       answer and because it is what the block directly above already printed: if
       the sum called a file "unreadable" that the fact pass had just counted among
       "N files sent", the two blocks would contradict each other on one screen and
       a person would have no way to tell which was lying. Since `104` §18.7
       (9 Sep 2026) that includes a PROTECTED file the local model was asked
       about: the owner ruled protected material reaches the local model, so a
       protected file the pass sent is "asked a model", and one the pass withheld
       carries the pass's own `WITHHELD_PROTECTED` verdict onto this line.
    2. **Then protected, for a file the pass never reached.** The standing rule is
       that protected material is marked and counted and never silently omitted. A
       protected file reported as "unreadable" would say the product tried to read
       it and failed, and one reported as "settled by rule" would hide it in the
       largest bucket on the screen; when no pass ran at all, "protected" is the
       one true thing this line can say about it.
    3. **Then what was read out of it**, for a file the pass never reached --
       which is every file when the pass did not run. Unreadable before deferred,
       because "nothing could be read out of it" is a settled outcome and a ceiling
       is not, and unreadable answered by `_files_something_was_read_out_of` rather
       than by P4's worst run: a file several extractors were pointed at, one of
       which reported `unreadable`, has still been read, and calling it unreadable
       on this line while the report proposes a folder for it two blocks down is
       the screen contradicting itself about the same file.
    4. **Then the pass's own reason for not running**, as the cause on a
       `COVERAGE_NOT_ASKED` line. Never `COVERAGE_SETTLED`: nothing settled those
       files' open fields, and saying so would be the false impression itself.

    A file that reaches none of the four is a defect in this function, and
    `assert_every_file_accounted` raises on it rather than letting the sum print
    short. That is the same choice `review_surface/progress.py` made and for the
    reason its module docstring gives: a progress line that omits a file looks
    complete.
    """
    roster = corpus_roster(conn, run_id)
    if not roster:
        return
    protected = _protected_file_ids(conn)
    # NOTHING WAS READ OUT OF IT IS THE TEST, AND NOT P4'S WORST RUN. The first
    # version of this function bucketed by `bucket_for(..., WORST_FIRST)`, which
    # answers a different question: worst-first is P13's tie-break for its own
    # §8.6 line, where a file with runs in several states has to be SHOWN as one
    # of them, and it makes `unreadable` win as soon as ONE extractor among
    # several reports it. This line makes a claim about the file instead --
    # "nothing could be read out of it" -- and under worst-first a file two
    # readers handled and a third could not would carry that claim on this line
    # while the report proposed a folder for it two blocks down, which is the
    # screen contradicting itself about one file. `_files_something_was_read_out_of`
    # is this build's one definition of read -- an observation that did not come
    # from the filesystem -- and it is the rule the folder screen and R-24's report
    # already answer with, so the three cannot come to disagree about one file.
    read = _files_something_was_read_out_of(conn)
    buckets: dict[str, list[str]] = {label: [] for label in _COVERAGE_ORDER}
    causes: dict[str, dict[str, list[str]]] = {
        label: {} for label in _COVERAGE_ORDER}
    for file_id, content_hash in roster:
        if file_id in verdicts:
            label, cause = verdicts[file_id]
        elif file_id in protected:
            label, cause = WITHHELD_PROTECTED, None
        elif file_id not in read:
            label, cause = UNREADABLE, None
        else:
            mine = [run for run in runs_for_content(conn, content_hash)
                    if run.file_id == file_id]
            state = bucket_for(mine, precedence=WORST_FIRST)
            if state in (CAPPED, DEFERRED):
                # A CEILING, AND P4'S OWN WORD FOR WHICH ONE. `capped` read
                # something and stopped; `deferred` never started. Both mean a
                # budget was reached and neither means the product could not read
                # the file, which is why they are here and not above.
                label, cause = DEFERRED, state
            elif not_run is not None:
                label, cause = COVERAGE_NOT_ASKED, not_run
            else:
                # NO BUCKET, DELIBERATELY. The assertion below names the file and
                # refuses the report rather than printing a sum that is short by
                # one, which is the only way a person could ever find out.
                continue
        buckets[label].append(file_id)
        if cause is not None:
            causes[label].setdefault(cause, []).append(file_id)

    entries = [ProgressEntry(
        label=label, count=len(buckets[label]), state=_COVERAGE_STATE[label],
        # WHERE THE ANSWER CAME FROM, in P13's own two words for it. The buckets
        # a model call or the route decided are P8's; the two read off P4's
        # extraction record are P4's. Neither is P3's population, which is what
        # this whole line is being reconciled against.
        source=SOURCE_P4_RUNS if label in (UNREADABLE, DEFERRED) else SOURCE_P8,
        cause=None, file_ids=tuple(sorted(buckets[label])))
        for label in _COVERAGE_ORDER]
    # BOTH HALVES OF "EXACTLY ONE", and one function answers only the first.
    # `assert_every_file_accounted` is P13's own rule -- no indexed file is absent
    # from every entry -- and it is asked for by name because it is the rule `104`
    # §18.2 gap 10 says was unreachable. It cannot catch the other direction: two
    # entries that both hold one file satisfy it and still make the printed sum
    # overshoot the roster, and a sum a person cannot trust is worse than none.
    assert_every_file_accounted(dict(roster), entries)
    total = len(roster)
    counted = sum(entry.count for entry in entries)
    if counted != total:
        raise FileInTwoBuckets(
            f"the six buckets hold {counted} files over a roster of {total}. "
            f"Every indexed file belongs in exactly one of them, and a sum that "
            f"does not close is a report that cannot be checked -- which is the "
            f"whole reason `104` §18.2 gap 10 asks for one. Counts: "
            f"{ {entry.label: entry.count for entry in entries} }")

    print("", file=out)
    # "COVERAGE", AND NOT "EVERY FILE IS ACCOUNTED FOR". Those words are already
    # on this screen: `_nothing_could_be_read_report` opens with them and then
    # NAMES the files, so a run down that path printed one sentence twice a few
    # lines apart -- one block summing, one block listing -- and left a reader to
    # work out whether they were the same claim about the same files. The word
    # here is the constitution's own for the rule this block enforces.
    print(f"Coverage: {total} file{'' if total == 1 else 's'} indexed.",
          file=out)
    for entry in entries:
        print(f"    {entry.count} {entry.label}", file=out)
        for cause, ids in sorted(causes[entry.label].items()):
            print(_wrapped(
                f"{len(ids)} of {'them' if entry.count != 1 else 'these'}: "
                f"{COVERAGE_SENTENCE.get(cause, cause.replace('_', ' '))} "
                f"({cause})", indent="      "), file=out)
    # THE ARITHMETIC ON THE SCREEN, not just in an assertion nobody sees pass. The
    # rule this block enforces is one a person has to be able to CHECK, and six
    # numbers with no sum beneath them is six numbers they would have to add up
    # themselves to find out whether their folder was covered.
    print(f"  {' + '.join(str(entry.count) for entry in entries)} = {total}, "
          f"and every file is on exactly one line above.", file=out)


#: One locked container, as the screen needs it: the name the person calls it and
#: the reader's own sentence about why it was not opened.
LockedContainer = namedtuple("LockedContainer", "name reason")


def locked_reasons(conn: sqlite3.Connection,
                   scan_run_id: str) -> dict[str, str]:
    """Section 2.5's password-protected archives in this scan, by file. `104` R-D.

    Read off P4's own extraction record rather than re-derived: the reader put the
    reason there, P5 made the run `unreadable`, and that table is "THE
    extraction-outcome record for the whole system". Matched on
    `LOCKED_REASON_PREFIX` and on the archive extractor, so `malformed archive:` --
    the other thing an `unreadable_reason` can say -- is never counted as marked.

    Over THIS scan's roster, for the reason `_protected_file_count` gives: the
    number stands beside a count of this run's containers and files, and a locked
    archive from an earlier scan of another folder would make the total a sum of
    two questions.

    ONE LOOKUP, read twice: by the block at the top of the report and by the line
    where the file itself is listed. Two lookups would be two answers to "is this
    archive locked", and the screen would eventually carry both.
    """
    reasons = {
        row["file_id"]: row["failure_reason"]
        for row in conn.execute(
            "SELECT file_id, failure_reason FROM extraction_runs "
            "WHERE extractor_name = ? AND completeness = 'unreadable' "
            "AND failure_reason LIKE ?",
            (ARCHIVE_EXTRACTOR_NAME, f"{LOCKED_REASON_PREFIX}%"))}
    found: dict[str, str] = {}
    for file_id, _hash in corpus_roster(conn, scan_run_id):
        reason = reasons.get(file_id)
        if reason is None:
            continue
        # The reader's sentence, without P5's tail. `extract_archive` appends
        # "; section 2.5 marks it rather than forcing it open" -- true, and it is
        # what the block's own heading already says, so printing it here would say
        # the same thing twice on one screen.
        found[file_id] = (
            reason.split(f"{LOCKED_REASON_PREFIX}: ", 1)[-1].split("; section")[0])
    return found


def locked_containers(conn: sqlite3.Connection, scan_run_id: str,
                      names: Mapping[str, str]) -> tuple[LockedContainer, ...]:
    """The same archives, named the way the person names them, for the block."""
    return tuple(sorted(
        LockedContainer(name=names.get(file_id, file_id), reason=reason)
        for file_id, reason in locked_reasons(conn, scan_run_id).items()))


def _print_protected(areas, *, protected_files: int,
                     locked: Sequence[LockedContainer] = (), out=None) -> None:
    """Everything this run marked and set aside, under ONE word and ONE total.

    **`104` R-J.** Two lines apart the report used to say "Protected containers: 0
    marked, none opened" and, further down, "4 protected files, marked and
    counted". §1.1's folders and §8.4's files, both called protected, two counts,
    and nothing on the screen saying that one of them was not the other. A person
    reads that as a contradiction, and they are right to.

    `00`'s rule is one rule -- marked and counted, never opened, never silently
    omitted -- so there is one heading and one total, and each KIND says
    underneath it what is true of that kind.

    **"Never opened" moved down to the folders, and that is not a wording
    choice.** It is false of a §8.4 file: that file WAS opened -- read, indexed
    and classified, on this device. What it was not is sent to a model or filed in
    one gesture with everything else. Printing "none opened" over it would be a
    comfort the run has not earned, which is the same defect as the two
    vocabularies, one rung quieter.

    **Folders are named; files are not.** A protected container is a folder on the
    person's own disk that Finder shows them anyway, and `00`:201 is about the
    other list: "a summary such as '11 protected identity records' may be safe to
    show, while a visible list of passport filenames on a shared screen may not
    be." `93-PROTECTED-DISCLOSURE-RULING.md` is the owner's decision behind that,
    and `--show-protected` is on the screen every time so the summary is never a
    hiding place.
    """
    out = out if out is not None else sys.stdout
    print(f"\nProtected: {len(areas) + len(locked) + protected_files} "
          f"marked and counted", file=out)
    if areas:
        print(f"  Application and system folders: {len(areas)}, never opened",
              file=out)
        for area in areas:
            print(f"    {area.display_label}  ({area.label})", file=out)
            print(f"      {area.path}", file=out)
        print("  Nothing inside these was read, indexed, classified or moved, and "
              "none of them is a place anything can be filed.", file=out)
    if locked:
        # `104` R-D. A THIRD KIND, and it belongs with the folders rather than
        # with the files: nothing inside it was read either. Section 2.5 -- an
        # archive whose members are encrypted is "marked as unreadable ... rather
        # than forced open" -- and the standing rule is that what is marked is
        # COUNTED, on the screen and not only in the database. `03938ae` recorded
        # it correctly and said it nowhere.
        #
        # NAMED, like the folders above and unlike the files below. The name is
        # the archive's own, which the person sees in Finder anyway; what stays
        # unprinted is the MEMBER list, because a locked archive's members can be
        # `passport.pdf` and `00`:201 is exactly about that list.
        print(f"  Password-protected containers: {len(locked)}, never opened",
              file=out)
        for container in locked:
            print(f"    {container.name}", file=out)
            print(_wrapped(container.reason, indent="      "), file=out)
    if protected_files:
        print(_wrapped(
            f"Protected material: {protected_files} "
            f"{'file' if protected_files == 1 else 'files'}, read on this device, "
            f"shown to no model off it, and filed only one at a time by you. Their "
            f"names are not printed here, because a list of them is the part of "
            f"this report least safe to have on a screen somebody else can see. "
            f"Nothing is being kept from you -- to see every one:", indent="  "),
            file=out)
        print("      --show-protected", file=out)


def _print_set_aside(summary: Mapping[str, object], aside, out) -> None:
    """§1.1's OTHER three rules, said out loud. The other half of the block above.

    "Marked and counted, never silently omitted" has no exception for the three
    rules that are not `protected container`, and until this printed, a person
    whose `Library/` or `node_modules/` was skipped was told nothing at all. That
    is `summary.py`'s own complaint about itself: "a person cannot ask for a
    folder back that they were never told was left behind."

    Deliberately a SECOND block and not an extension of the first. A protected
    container is never openable by any policy, approval or gesture; a folder
    excluded by name is a rule this product chose and could be asked to revisit.
    Printing them in one list in one voice is how a person comes to believe the
    same thing happened to both.

    The count and the names are both printed because they answer different
    questions -- `paths_excluded_by_rule` says how many, `set_aside_paths` says
    which -- and a count with no names is the omission this fixes.
    """
    out = out if out is not None else sys.stdout
    if not aside:
        return
    print(f"\nSet aside by rule: {len(aside)}, not read and not in this plan",
          file=out)
    for entry in aside:
        print(f"  {entry.display_label}  ({entry.rule}"
              f"{f': {entry.rule_subject}' if entry.rule_subject else ''})",
              file=out)
        print(f"    {entry.path}", file=out)
    print("  These were skipped before anything was read. If one of them is "
          "material you want organised, it has to be scanned on its own.",
          file=out)
    # §8.6's counters, and only where there is a set-aside block for them to
    # qualify. On a corpus nothing was excluded from they would be a bare
    # statistics line, which is not a question anybody asked.
    print(f"  Files indexed: {summary['files_indexed']}. "
          f"Reused from the last scan: {summary['files_reused_from_stat_cache']}. "
          f"Re-read: {summary['files_recomputed']}. "
          f"Deferred: {summary['files_deferred']}.", file=out)


def _print_candidate_roots(candidate_roots: Sequence[Path],
                           folders: Sequence[object], out) -> None:
    """`00`:21 said out loud: what a root IS, and what naming one did not do.

    "At this stage, roots are context for the proposal canvas, not permission to
    move files… to show where a proposed branch could eventually live." A flag
    that recorded the answer into a database and put nothing on screen would be
    the same defect as the literal it replaced, one layer further in: the person
    would have told the product something and have no way to see that it heard.

    So the root is named, the folders already standing in it are named under it,
    and the sentence that separates a root from a destination is printed every
    time. The folders are P3's own inventory of that root -- observed, never
    walked into for content -- which is exactly the "current folder landscape"
    §21 asks the engine to understand. The immediate children only: a root's
    whole subtree is a file browser, and the question a person is answering here
    is which high-level place a branch could sit in.
    """
    out = out if out is not None else sys.stdout
    if not candidate_roots:
        return
    print("\nCould eventually live in:", file=out)
    for root in candidate_roots:
        print(f"  {root}", file=out)
        children = sorted(
            Path(folder.directory_path).name for folder in folders
            if folder.parent_directory is not None
            and Path(folder.parent_directory) == Path(root))
        if children:
            print(f"    already there: {', '.join(children)}", file=out)
    print("  Nothing is filed there by this plan. These are the places a branch "
          "could eventually live, and naming one moves nothing and approves "
          "nothing.", file=out)


#: §4.4's similarity threshold, MEASURED AND NOT CHOSEN. `planning/103` records
#: the run: every pair of the owner's own labelled files, encoded by the same
#: MiniLM weights this deployment names, split by whether the ground truth puts
#: them in one course.
#:
#:     SAME course   n=73   p10=0.212  p50=0.417  p90=0.603
#:     DIFFERENT     n=362  p10=-0.045 p50=0.057  p90=0.165
#:
#: The distributions separate -- the 90th percentile of DIFFERENT sits below the
#: 10th of SAME -- and F1 peaks here at 90.7% precision for 67.1% recall. A
#: threshold picked rather than measured is the thing `_require_semantic_
#: configuration` refuses to supply a default for, and this is the measurement it
#: was waiting on.
SEMANTIC_SIMILARITY_THRESHOLD: float = 0.30

#: §4.4's precedence when the neighbourhood is capped, and `00`:56 is the whole of
#: the reasoning: "embeddings never establish the group by themselves. A semantic
#: neighbor is simply a file worth bringing into the evidence packet." So a shared
#: validated fact must survive the cut before a cosine does. Only the two channels
#: this deployment actually produces are weighted; a channel with no weight ranks
#: last, which is the correct place for one nothing has measured.
SEMANTIC_CHANNEL_WEIGHTS: Mapping[str, int] = MappingProxyType({
    SHARED_VALIDATED_FACT: 2, MUTUAL_SEMANTIC_RETRIEVAL: 1})

#: P9 RETRIEVAL's own floor, split from recognition's `SEMANTIC_MIN_CHARS` on the
#: owner's ruling of 2026-09-06 (`104` R-59). The two ask different questions of the
#: same encoder -- recognition asks "what kind of thing is this", retrieval asks
#: "which other file is this near" -- and `00`:56 names the second for exactly the
#: files the first has least to say about: "embeddings ... can find files such as
#: HW 3.pdf that lack the course code but resemble lecture notes and earlier problem
#: sets". Recognition's 100 is measured in `planning/97` and is not moved here.
SEMANTIC_RETRIEVAL_MIN_CHARS: int = 100


def semantic_retrieval_text(conn: sqlite3.Connection, file_id: str,
                            content_hash: str) -> str | None:
    """The words P9's semantic channel encodes for one file version, or nothing.

    **R-59, and it is the whole of why this is a named function.** The two lines
    below used to sit inside `_embedding_runtime`'s `text_for` closure and read:

        text = evidence_text(conn, file_id, content_hash, zones=..., char_budget=...)
        return text if text and len(text) >= SEMANTIC_MIN_CHARS else None

    `recognition.semantic.evidence_text` returns `(text, observation_keys)`. So
    `len(text)` was 2 for every file that has ever been scanned, the guard returned
    `None` unconditionally, and the channel `3ac0c0b` built has never computed a
    vector -- for any file, at any length, in any run. `_mutual_semantic_neighbours`
    returns `[]` at its `seed_vector is None` line, so no `mutual-semantic-retrieval`
    edge has ever existed. Measured on the owner's 199 files: a tuple 199 times.

    `d75dcb5`, the recognition commit that added the second return value, is an
    ANCESTOR of `3ac0c0b`: the channel was written against this signature and was
    dead on arrival rather than severed later.

    A closure is why nothing caught it. `_embedding_runtime` cannot be entered
    without loading MiniLM weights, which are machine state and not repository
    state, and `tests/integration/test_p9_embedding_pipeline.py` injects its own
    `embedding_text_for` -- so P9's half was tested and the composition root's half
    was unreachable from any test. It is a module-level function now, and
    `text_for` is one line.

    **The zones are recognition's list and the filename leads it.** `00`:56 names
    the filename among what a sparse file has, and `SEMANTIC_ZONES[0]` is
    `filename`, so it is already in the vector: nothing is added here for it.
    """
    text, _keys = evidence_text(conn, file_id, content_hash,
                                zones=SEMANTIC_ZONES,
                                char_budget=SEMANTIC_CHAR_BUDGET)
    return text if text and len(text) >= SEMANTIC_RETRIEVAL_MIN_CHARS else None


# --- P9's typed edges, read by P11 (`104` R-12) -------------------------------------
#
# P9 and P11 publish the same five relationships under different spellings --
# `grouping.vocabulary` hyphenates and `placement.graph` uses underscores -- and
# `build_node_local_graph` raises `ValueError` on a type it does not know. So a P9
# edge row cannot be handed to P11 as it stands, and the translation belongs HERE:
# the composition root is where two parts' vocabularies are allowed to meet, and
# neither part may hold a second spelling of the other's.
#
# NOT AN ALIAS TABLE, and the difference is checkable rather than asserted: every
# key and every value is the OTHER MODULE'S OWN CONSTANT, imported by name, so a
# member renamed on either side is an `ImportError` and a member ADDED on either
# side fails `test_cli_p9_p11_edge_seam.py`, which compares this mapping against
# both published tuples. Nothing here invents a relationship, and nothing here
# decides what a relationship means.

#: P9's spelling -> P11's, for the five relationships both parts carry.
P9_TO_P11_EDGE_TYPE: Mapping[str, str] = MappingProxyType({
    SHARED_VALIDATED_FACT: P11_SHARED_VALIDATED_FACT,
    DUPLICATE: P11_DUPLICATE,
    VERSION_FAMILY: P11_VERSION_FAMILY,
    COMPATIBLE_DOCUMENT_TYPE: P11_COMPATIBLE_DOCUMENT_TYPE,
    EXISTING_RELATED_FOLDER: P11_EXISTING_RELATED_FOLDER,
})

#: P9's other two, named as DROPPED rather than left out of the mapping silently.
#: `placement/graph.py` is explicit that neither is an edge there: "a semantic
#: neighbour is deliberately absent: it is a retrieval channel and never an edge,
#: because an embedding alone is insufficient". `00`:63 is the same sentence --
#: a group is not supported "when the graph is connected only by embeddings". The
#: semantic channel reaches P11 as `semantic_neighbours`, which is a retrieval
#: channel, and never as an edge.
NOT_A_PLACEMENT_EDGE: tuple[str, ...] = (BOUNDED_SESSION, MUTUAL_SEMANTIC_RETRIEVAL)


def bridge_entity_for(edge_type: str, bridge: str | None) -> str | None:
    """The entity an edge rests on, in a form that may be shown.

    §6.5's hub test asks whether a neighbourhood is held together by one entity
    that appears everywhere, and `NodeLocalGraph` carries the entity onto the
    review surface. P9 records the `existing-related-folder` channel's bridge as
    the folder's ABSOLUTE PATH -- measured on the owner's corpus:
    `/Users/<name>/.../Desktop/Python 1006` -- and §8.4's always-local list opens
    with the word "Paths". So that one channel's bridge is reduced to the folder's
    LABEL, which is the form `_folders_this_file_is_already_in` already uses for
    exactly this value and exactly this reason.

    KEYED ON THE EDGE TYPE, never on the shape of the string. "Does this look like
    a path" is a guess; "this channel's bridge IS a folder" is P9's own definition
    of the channel, and the type vocabulary is closed.

    Every other channel's bridge is passed through as recorded. Today that is
    `None` on all 204 of the owner's `shared-validated-fact` edges -- P9 stores no
    bridge on the one channel §6.5's hub test is actually about -- which is a P9
    finding and not something to reconstruct here: `build_node_local_graph`'s own
    docstring says P11 "discovers no relationship of its own here, because that
    would be a second grouping engine and P9 owns grouping".
    """
    if edge_type == EXISTING_RELATED_FOLDER and bridge:
        return str(bridge).rstrip("/\\").rsplit("/", 1)[-1]
    return bridge


def citation_basis_for(reliability_state: str) -> str:
    """`00`:57's split -- direct anchors against context-supported members -- read
    off §3.13's own ladder rather than from a list written out here.

    `validated`, `direct` and `user_confirmed` are readings of the file's own bytes
    or the person's own word, which is what `00`:58 calls direct evidence. Below
    them, `llm_supported` is inference by definition and `possible` is P4's state
    for "free text, OCR, A FILENAME or any unlabeled position" -- which is exactly
    `00`:57's HW 3.pdf, included on a homework-like NAME and called
    context-supported there in those words.

    Reading the ladder rather than enumerating a set means a state added to §3.13
    is placed by its rank instead of silently falling to one side. `rejected` has
    no rank and raises; the caller has already excluded it, because a placement
    resting on a claim the person retracted is a contradiction and not a weak fact.
    """
    return (DIRECT_ANCHOR if strength(reliability_state) >= strength(VALIDATED)
            else CONTEXT_SUPPORTED)


def content_hash_of(conn: sqlite3.Connection, file_id: str) -> str | None:
    row = conn.execute("SELECT content_hash FROM files WHERE file_id = ?",
                       (file_id,)).fetchone()
    return None if row is None else row["content_hash"]


def accepted_memberships_of(conn: sqlite3.Connection, file_id: str, *,
                            accepted: Sequence[str]) -> tuple[str, ...]:
    """The accepted groups THIS FILE is in (`104` R-11).

    This used to be `tuple(accepted_ids)` -- every accepted group in the run,
    offered to every file in it, so `retrieval.retrieve`'s `ACCEPTED_GROUP`
    channel fired for a file that belonged to nothing and scored it into the
    branch some other file's group had built. Measured (`104` §11.1, `exp1`):
    removing the fabricated credit moved "not placed" 32 -> 35 and left `wrong`
    and spillover unchanged, so it was never the regression -- it was three
    placements resting on evidence that did not exist.

    Keyed on the content hash as well as the file, which is `live_memberships_
    of_file`'s own rule and P9's: a membership belongs to a file VERSION, so a
    file edited between runs does not inherit the memberships of its old bytes.

    `decision` is checked, not assumed. `review_and_accept` writes `included`
    for everything today (`104` R-16 is that defect), and the day it writes
    `excluded` or `uncertain` this must not go on reading them as membership.
    """
    content_hash = content_hash_of(conn, file_id)
    if content_hash is None:
        return ()
    wanted = frozenset(accepted)
    return tuple(dict.fromkeys(
        membership.group_id
        for membership in live_memberships_of_file(
            conn, file_id=file_id, content_hash=content_hash)
        if membership.group_id in wanted and membership.decision == INCLUDED))


def located_citations(conn: sqlite3.Connection, file_id: str,
                      refs: Sequence[str]) -> tuple:
    """Every citation of a fact that resolves to a live location IN THIS FILE.

    `00`:62 requires the validator to check "that every cited text span or
    metadata field exists in SQLite", so a citation that does not resolve is not
    evidence and is dropped rather than carried with a made-up address. On the
    owner's corpus all 525 citations resolve; the filter is what makes that
    checkable rather than assumed.

    EVERY citation, not `refs[0]` (`104` R-11). The owner's 97 live facts carry
    525 citations between them -- one carries 65 -- and the dossier was showing
    the model 97 of them and calling the rest absent.
    """
    located = []
    for ref in dict.fromkeys(refs):
        try:
            current = current_location(conn, ref, within_file_ids=(file_id,))
        except (UnresolvableSpan, AmbiguousObservationKey):
            continue
        if current.file_id != file_id:
            continue
        located.append((ref, current.location))
    return tuple(located)


def anchor_line_citations(conn: sqlite3.Connection, *, scan_run_id: str,
                          file_id: str) -> tuple:
    """`104` R-135: the whole LINE each of this file's course codes was printed on.

    `(observation_key, location, reliability)` per line, or an empty tuple. The caller
    turns them into `EvidenceItem`s; nothing is decided here.

    **The defect this exists for, measured.** `extractors/pdf.py:181` emits two readings
    over a syllabus heading: the heading, whose words are `COMS W3134: Data Structures`,
    and the identifier inside it, whose words are `W3134`. Only the identifier is ever
    CITED -- §3.5's `subject` rule matches a code and a fact carries the citation that
    matched -- so `evidence_for` offered site C five characters, and site C's own
    instruction, *"two spellings can be one thing ... yours to judge from the
    evidence"*, had nothing beside the code to judge against. 19 of the owner's 43
    labelled course codes came back missing and 19 more were a title recorded where the
    code belonged.

    **It offers; it does not pair, rank or choose.** `facts.anchor_statements` already
    found the containing reading STRUCTURALLY -- the shortest reading whose span covers
    the identifier's inside one container path -- and stores it as a citation with no
    title column and no value column. This reads that citation back and hands the
    address to the release. Two anchors naming one course come back as two, in
    `anchor_statements_for`'s order, and neither is preferred: choosing between them is
    the model's, and a caller taking the first would be the sorting rule the product
    constitution forbids.

    **The gate still decides.** These are addresses, not text. `releasable_excerpts`
    applies P7's own refusals to them like any other ref -- a value P5 signalled, a
    dead key -- and the door materialises and redacts. What changed in `104` R-135
    is only that a span covering a whole HEADING unit is no longer refused, which is
    what makes an address like this releasable at all.

    **The always-local zone is asked HERE now** (`104` R-150), which is the pattern
    R-135 already took from the excerpt builder: *"each is one of the gate's own
    refusals applied a step early, so the request is never BUILT rather than built
    and denied."* An anchor whose line reading is a `filename` or a `path` is one
    the gate can never release, so offering it built a site-C dossier carrying an
    item that was dead on arrival -- measured on the six-file stub corpus as
    `excerpt / filename / [0, 22] / possible` beside the fact item at the same
    address, and every such dossier one item larger than what the model may see.

    A filename reading reaches a statement through no fault of its own:
    `extractors/filesystem.py` gives the name "the run's single `container_path: ()`
    text unit" and reads it as one span over the whole of it, a text extractor gives
    the body a `()` unit too, and `anchor_statements._containing_span_reading`
    compares spans within a container path and asks nothing about the zone. The
    STATEMENT is right to record it -- what the document contains is P4's and P6's
    answer -- and this site is where what may be OFFERED is decided.

    A statement whose `line_evidence_ref` is `None` yields nothing HERE, and that is
    site C's own answer rather than a gap. `facts.anchor_statements` returns `None` for
    a code whose line it will not mint -- no stored unit text, or a line whose
    characters are the code's own -- and at this site the code is already offered, by
    the loop above, as the citation of the fact that matched it. Falling back to it
    would offer one reading twice. The site-A path has no such duplicate and does fall
    back; `anchor_context_observations` says so where it does.

    A key that no longer resolves in this file also yields nothing. `located_citations`
    states the reason: "a citation that does not resolve is not evidence and is dropped
    rather than carried with a made-up address."
    """
    lines = []
    for statement in anchor_statements_for(conn, scan_run_id,
                                           stating_file_ids=(file_id,)):
        ref = statement.line_evidence_ref
        if ref is None:
            continue
        try:
            observation = current_observation(conn, ref, within_file_ids=(file_id,))
        except (UnresolvableSpan, AmbiguousObservationKey):
            continue
        if observation.file_id != file_id:
            continue
        # `104` R-150: §8.4's own always-local exclusion, asked a step early. The
        # SET is imported and never a pair of zone names typed here -- `ocr` joined
        # it on 2026-09-04 as member 3, and `tests/integration/test_model_placement`
        # states what a hand-written list costs: it goes on passing while the path
        # offers whatever the newest member is.
        if observation.location.zone in ALWAYS_LOCAL_ZONES:
            continue
        # P4's OWN reliability for that reading, never a constant typed here.
        # `model_facts.filename_citation` states the rule for the same field.
        lines.append((ref, observation.location, observation.reliability))
    return tuple(lines)


def reading_citations(conn: sqlite3.Connection, file_id: str, *,
                      limit: int, locality: str, ceiling: int) -> tuple:
    """`104` R-148: the file's OWN releasable readings, as citable addresses.

    `(observation_key, location, reliability)` per reading, in
    `releasable_observations`' own order, or an empty tuple. The caller turns them
    into `EvidenceItem`s and nothing is decided here -- the shape
    `anchor_line_citations` above returns, for the same reason.

    **The defect this exists for, measured.** `evidence_for` built a placement
    call's evidence out of FACTS -- `file_facts` rows whose citations still resolve
    -- plus the anchor lines above. A file P6 settled nothing about therefore
    arrived at `pipeline._judge_with_model` with no `evidence_items`, and was
    recorded `NOT_ELIGIBLE_FOR_MODEL` before any dossier existed. On the owner's
    corpus that was 103 of 199 files on r12: 64 unclassified, 39 classified, 52% of
    their coursework. `00` §5 builds site C for "files or groups that remain
    ambiguous", and the most ambiguous file in the corpus was the one it refused.

    **It is site A's own question, asked of the same file.**
    `model_facts.releasable_observations` is that file's capped, gate-checked
    reading set and this is a read of it -- not a second spelling of "what may this
    file offer", which would be two answers to one question. The five exclusions
    live there, `model_placement.releasable_excerpts` applies them again on the way
    out, and the door materialises and redacts: nothing here widens what P7
    releases.

    **The cap is the caller's**, because `FACT_CALL_MAX_RELEASED_OBSERVATIONS` is
    where this deployment chooses the number and a second default here would be a
    second choice.

    **AND SO IS THE CEILING, AND AT THIS SITE IT IS A REMAINDER (`104` R-159).**
    Site A has §8.6's ladder: it measures the dossier it is about to build and
    defers the call rather than sending one the door will refuse. Site C has no
    ladder -- `_judge_with_model` builds its request and the gate answers -- so an
    over-ceiling C dossier is denied `over_dossier_ceiling` outright and the file
    loses the one stage `00` §5 built for ambiguity. With whole units releasable to
    a local target that stopped being hypothetical, so `evidence_for` passes what
    `max_dossier_tokens` has LEFT after the facts and the anchor lines it has
    already built, and `model_facts.within_dossier_budget` fills that. For a cloud
    target the count cap binds exactly as before and the remainder is slack.

    Neither number is chosen here: the cap is `FACT_CALL_MAX_RELEASED_OBSERVATIONS`
    and the ceiling is `GROUPING_LIMITS.max_dossier_tokens`, both already stored.

    A file version this run has no row for yields nothing, on
    `located_citations`' own rule: an address nothing carries is not evidence.
    """
    content_hash = content_hash_of(conn, file_id)
    if content_hash is None:
        return ()
    return tuple(
        (observation.observation_key, observation.location,
         observation.reliability)
        for observation in releasable_observations(
            conn, file_id=file_id, content_hash=content_hash, limit=limit,
            locality=locality, ceiling=ceiling))


def released_characters(conn: sqlite3.Connection, items) -> int:
    """How many characters the gate will release for these evidence items. `104` R-159.

    Site C's half of the same arithmetic site A does in `model_facts.fact_call_stage`:
    before the file's own readings are filled in, the items already built have to be
    paid for, or the dossier the ceiling was supposed to bound is the one the door
    refuses. `evidence_for` builds two sets before it asks for the readings -- the
    citations of the facts P6 settled, and R-135's anchor lines -- and this is what
    they cost.

    **Measured PER ITEM and not per distinct ref**, because that is what the gate
    measures. `model_placement._model_call_request_builder` turns every item with a
    ref into a requested `Excerpt` without de-duplicating, so an address carried by
    two items under two reliabilities is resolved twice and counted twice by
    `measure_released_tokens`. Counting it once here would leave a remainder larger
    than the room actually left. If the door ever did de-duplicate, this errs by
    reserving space it did not need, which is the direction a ceiling has to err in.

    **On the RAW value**, the same measurement `model_facts._call_dependencies` and
    `_within_ceiling` take, and for the same reason: this runs before `gate.release`,
    the redacted text does not exist yet, and redaction only ever shortens.

    A ref with no live row costs nothing, which is exact rather than a fallback:
    `releasable_excerpts` drops it and the door releases nothing for it.
    """
    lengths: dict[str, int] = {}
    total = 0
    for item in items:
        ref = getattr(item, "evidence_ref", None)
        if not ref:
            continue
        if ref not in lengths:
            row = conn.execute(
                "SELECT raw_value FROM evidence WHERE observation_key = ? "
                "AND superseded_by IS NULL LIMIT 1", (ref,)).fetchone()
            lengths[ref] = 0 if row is None else dossier_tokens((row["raw_value"],))
        total += lengths[ref]
    return total


def releasable_items(conn: sqlite3.Connection, items, *, locality: str) -> tuple:
    """`104` R-156: the offered items, filtered by the door's OWN predicate.

    `evidence_for` builds three kinds of `EvidenceItem` from three producers, and
    `model_placement.releasable_excerpts` is what the request builder then asks
    about every one of them on the way out. Five refusals live there -- the
    always-local zone, a value P5 signalled, an empty raw value, and the two
    whole-unit tests (`104` R-135's heading and `104` R-152's line exempted) --
    and `validation._check_citation` resolves the model's citation against what
    was RELEASED. So an item offered that the door drops is not a smaller
    dossier: the model is shown it, told to cite, cites it, and rule 10 of the
    site-C text takes the WHOLE answer with it. Measured on r13: 10 of 44 site-C
    dossiers rejected `CITATION_NOT_IN_DOSSIER`, every cited handle an exact
    handle the dossier had issued.

    R-154 closed the zone by asking that one exclusion a step early. The other
    four cannot be asked that way: they need the observation row and the length
    of the unit the span points into, which `located_citations` does not carry --
    which is why this asks the predicate rather than retyping them. There is one
    question here, *may this reading leave the device*, and one function that
    answers it; a second spelling at this seam is what R-154's three surviving
    rejections (body 1, metadata 2) were.

    **Keyed on the REF, and that is exact rather than convenient.**
    `releasable_excerpts` decides per `evidence_refs` entry, resolving the live
    observation itself and reading its own span -- so releasability is a function
    of the ref alone, and two items carrying one ref under two reliabilities are
    both released or both refused. The items keep their order and their fields:
    nothing here rewrites an item, and an item this drops was never one the model
    could have used.

    A file left with no item at all is a file `pipeline._judge_with_model` records
    as a pre-call abstention, which is R-148's own sentence about the same state:
    the dossier would cite nothing, and saying so is truer than sending one whose
    every citation the gate will strip.
    """
    releasable = {excerpt.observation_key for excerpt in releasable_excerpts(
        conn, evidence_refs=tuple(dict.fromkeys(
            item.evidence_ref for item in items)),
        # `104` R-159: the placement call's own target. Two of the five refusals now
        # depend on it, and asking them about the wrong destination is how a whole
        # page would be dropped from a dossier the door would have released -- or,
        # the other way, offered to a cloud model the ruling did not open.
        locality=locality)}
    return tuple(item for item in items if item.evidence_ref in releasable)


def _folder_family(subject_path: str, stating_path: str) -> bool:
    """Whether a document at `stating_path` speaks for a file at `subject_path`.

    THE FOLDER, AND ITS ANCESTORS, AND NOTHING ELSE. A syllabus in `Courses/Data
    Structures/` speaks for the coursework beside it and for whatever sits in the
    sub-folders under it; a syllabus in a sibling folder speaks for nothing here. That
    is a containment test over the two paths and it is the whole rule -- no shared
    word, no similar name, no distance score. `00`:56's own example is the file
    `HW 3.pdf` that "lacks the course code but resembles lecture notes"; the folder the
    person filed it in is a fact about it that the product already has.

    **The paths never leave the device and this is where that is enforced.** §8.4 puts
    paths in the always-local set as member 1, `releasable_observations` drops every
    `path`-zone observation, and nothing here returns one: the answer is a boolean, and
    what travels afterwards is an OBSERVATION KEY that the gate resolves for itself.
    A neighbour is FOUND by the path and is never described by it.
    """
    subject = Path(subject_path).parent
    stating = Path(stating_path).parent
    return subject == stating or stating in subject.parents


def anchor_context_observations(conn: sqlite3.Connection, *, scan_run_id: str,
                                file_id: str, fields: Sequence[str],
                                limit: int, locality: str,
                                preserved_anchors: bool = False) -> tuple:
    """`104` R-135: the anchor headings near this file that a `subject` call may show.

    **`locality` is the call's own target (`104` R-159), required and forwarded.**
    It reaches `model_facts.releasable_readings` below and decides nothing here: a
    neighbour's reading leaves the device by the same door this file's own readings
    leave by, and the composition root reads the answer off the client the call is
    pointed at.

    **`preserved_anchors` is §8.6's second shape of the same offer (`104` R-145).**
    `False` offers the LINE each anchor sits on, which is what a person would point at
    on a syllabus; `True` offers each anchor's own span -- the code and nothing round
    it -- which is `00`:257's "preserve anchor excerpts" when the lines do not fit
    the dossier ceiling. Same statements, same neighbours, same release check; only
    which reading of each statement is named. Measured on r12: one neighbour's
    "line" was a 27,510-character paragraph of extracted text, and every one of the
    17 files in its folder family was deferred at site A without a call.

    **The defect, measured.** 19 of the owner's 43 labelled course codes came back
    MISSING, and 35 of the 43 files whose label carries a course name carry no course
    code anywhere in their own bytes. The code is printed once, on the syllabus, and a
    stage asked about one file version at a time can never see it -- so the model
    answered `unknown` about those files, correctly, from evidence that was never
    there. `facts.anchor_statements` recorded WHERE the corpus states a course; this
    is what carries that reading to the file the sentence is about.

    **Four narrowings, each structural.**

      * *Only the field the deployment ties this to.* `SUBJECT_FIELD` is cli's, beside
        `SUBJECT_RULE`, because which field a course code
        answers is a deployment's question and `model_facts` may not spell it. A call
        that is not asking it gets nothing.
      * *Only a document in this file's folder or above it.* `_folder_family`, over
        paths that stay here.
      * *Never the file itself.* Its own readings are already offered as direct
        evidence; the same reading twice, once as context, would tell the model a file
        corroborates itself.
      * *Only a classified, unprotected neighbour.* The gate would refuse the rest, and
        it would refuse the WHOLE call: the target gains this file's id, so
        `Gate._decisive` classifies it and an unclassified or protected syllabus denies
        the fact call of an unrelated file beside it. That is `releasable_observations`'
        own rule applied once more -- "each is one of the gate's own refusals applied a
        step early, so the call is never BUILT rather than built and denied". It is a
        question about the FILE and is asked once per stating file.
      * *And only readings the gate would release.* `model_facts.releasable_readings`
        asks the four exclusions OF THE NAMED READINGS -- the zone rules, P5's
        per-value signal, the whole-unit rule with `104` R-135's heading exemption --
        with no ranking and no per-file cap, so nothing is dropped for placing badly
        in a competition it was never entered in. Its docstring carries what asking the
        other question cost.

    Nothing is chosen and nothing is preferred by distance. Every anchor near the file
    is offered and the model decides; two syllabuses naming two courses both arrive,
    which is the case the constitution's "no sorting rules" exists for. When more
    arrive than `limit` allows, the order is the product's own zone preference and then
    the order `anchor_statements_for` recorded -- a nearer folder is not a stronger
    claim, and treating it as one would be this module answering the model's question.
    """
    if SUBJECT_FIELD not in tuple(fields):
        return ()
    row = get_file(conn, file_id)
    if row is None:
        return ()
    subject_path = row["current_path"]
    store = ClassificationStore(conn)
    # STATEMENT ORDER, kept, because it is the tie-break below. `anchor_statements_for`
    # imposes `(canonical_code, stating_file_id, code_evidence_ref)` for §8.5's replay,
    # and a dict keyed on the stating file threw that away.
    wanted: list[tuple[str, str]] = []
    for statement in anchor_statements_for(conn, scan_run_id):
        # `104` R-135's fallback: the LINE when the corpus has one and the code's own
        # span when it does not. `facts.anchor_statements` mints a line for a code that
        # sits inside a span-less body reading, and returns `None` for the two cases it
        # refuses -- no stored unit text to read the line back from, and a line whose
        # characters are the code's own. In both, the code span is what there is, and a
        # code beside a neighbouring file is more than the model is shown without it.
        # Skipping instead is what this loop used to do, and on the measured run it
        # skipped 91 of 99 statements and every dossier carried no context at all.
        ref = (statement.code_evidence_ref if preserved_anchors
               else statement.line_evidence_ref or statement.code_evidence_ref)
        if statement.stating_file_id == file_id:
            continue
        stating = get_file(conn, statement.stating_file_id)
        if stating is None or not _folder_family(subject_path,
                                                 stating["current_path"]):
            continue
        record = store.current(statement.stating_file_id, stating["content_hash"])
        if record is None or record.protected:
            # The gate's own two refusals, a step early. An unclassified neighbour is
            # `Denied(unclassified)` for a cloud target and a protected one is
            # `ProtectedItemRequested`; either would cost this file its whole call.
            continue
        wanted.append((statement.stating_file_id, ref))

    # THE RELEASE CHECK IS ASKED OF THESE READINGS, and that is `104` R-135's third
    # defect. It used to ask `releasable_observations` for the stating file's own
    # ranked, capped dossier and keep the wanted keys that appeared in it -- so a
    # minted body line, `possible` reliability in the `body` zone, was dropped for
    # failing to reach a syllabus's top twelve, a competition it was never in.
    # Measured over the first 9 files asked on r9: 120 statements refused as "line not
    # among releasable" and 7 of those 9 files ending with no context at all, while
    # nothing about the readings was unreleasable. `releasable_readings` asks the same
    # four exclusions of the named readings, with no ranking and no per-file cap.
    by_file: dict[str, list[str]] = {}
    for stating_file_id, ref in wanted:
        by_file.setdefault(stating_file_id, []).append(ref)
    offered: dict[str, object] = {}
    for stating_file_id, keys in by_file.items():
        stating = get_file(conn, stating_file_id)
        for observation in releasable_readings(
                conn, file_id=stating_file_id,
                content_hash=stating["content_hash"], keys=keys,
                locality=locality):
            offered[observation.observation_key] = observation

    # THE CAP IS ON THE CONTEXT ITEMS, not on any file's candidates: it bounds what
    # this call sends, which is what a release cap is for. Ordered by the SAME term
    # the file's own offer is ordered by and then by statement order. Nothing here
    # prefers a nearer folder or a shorter path; which anchor names this file's course
    # is the model's judgement, and a distance rule would be this module answering it.
    #
    # **`104` §18.2 gap 6: THE TERM IS A MEASUREMENT AND IT IS ASKED, NOT COPIED.**
    # This read `model_facts.zone_rank`, a six-name table typed in that module, while
    # `cli.ZONE_WEIGHT` a few hundred lines above weighed metadata, body, ocr and path
    # equally -- two hand-typed orderings of the same fifteen zones, disagreeing, one
    # of them deciding what the model is shown. `zone_evidence_counts` answers the
    # question by counting: for the fields this call is asking, the zones this
    # corpus's own recognisers have cited. It is asked for THESE fields, so the
    # context lines are ordered by the same evidence the file's own readings are, and
    # a zone nobody has measured scores zero and falls to statement order rather than
    # behind every named zone.
    cited = zone_evidence_counts(conn, fields=fields)
    order = {ref: index for index, (_file, ref) in enumerate(wanted)}
    return tuple(sorted(
        offered.values(),
        key=lambda one: (-cited.get(one.location.zone, 0),
                         order[one.observation_key]))[:limit])


def files_stating_each_fact(conn: sqlite3.Connection) -> dict[str, int]:
    """§6.5's generic-entity count, MEASURED and spelled the way P9 names a bridge.

    Two defects, one lookup. The count was `{fact.value: 1}` -- every value
    declared unique, so the hub test `00`:63 asks for ("one high-frequency entity
    acts as the only bridge") could never fire on any corpus by construction
    (`104` R-11). And the key was the bare `canonical_value`, while the entity
    `placement/graph.py:156` looks up is the bridge P9 recorded on the edge, which
    since `104` R-59's third finding is `field=value` -- so every shared-fact
    lookup missed and answered 0 whatever the ceiling was. `fact_bridge_ref` is
    the one spelling all three sites read.

    A folder label is not a key here and should not be. `existing-related-folder`
    bridges through a folder the person made; it has no fact row, its frequency is
    genuinely unknown to this map, and 0 is an honest answer rather than a missed
    lookup.

    Retracted facts are excluded. §3.13's `rejected` is a claim the person told
    the product was wrong, and counting it would let a retraction go on making an
    entity look common.
    """
    counts: dict[str, int] = {}
    for row in conn.execute(
            'SELECT ff.field_key AS field, v.canonical_value AS value, '
            'COUNT(DISTINCT ff.file_id) AS files FROM file_facts ff '
            'JOIN "values" v ON ff.value_id = v.value_id '
            'WHERE ff.active = 1 AND ff.superseded_by IS NULL '
            'AND ff.reliability_state != ? '
            'GROUP BY ff.field_key, v.canonical_value',
            (pv.DROPPED_RELIABILITY_STATE,)):
        counts[fact_bridge_ref(row["field"], row["value"])] = row["files"]
    return counts


def typed_edges_of(conn: sqlite3.Connection,
                   file_id: str) -> tuple[dict, ...]:
    """P9's typed edges touching this file, in P11's shape (`104` R-12).

    P9 records these in `group_edges` and P11 read `()` -- so
    `build_node_local_graph` saw no relationships at all, `is_typed_support`
    was False for every file in every corpus, and `00`:109's "the node-local
    graph should include typed relationships" described nothing.

    `hub_suppressed` edges are left out. P9 has already judged those a
    generic-hub bridge with the ceiling P9 was given; re-offering them here
    would be P11 overturning that judgement with a different threshold, and on
    the owner's corpus it would also carry 294 folder PATHS into the graph.

    `weight` is P9's when P9 has one and 1.0 when it has none, which today is
    every edge (`grouping/graph.py` constructs them `weight=None`). So §8.6's
    "reduce to the strongest" cut ranks nothing, and WHAT BREAKS THE TIE IS THIS
    ORDER BY -- which is why the rows come back in a content order and not in
    `rowid`.

    **IT USED TO BE `ORDER BY rowid`, AND THAT WAS `104` R-111.** This docstring
    said the equal weights left the cut to "the file-id tiebreak
    `build_node_local_graph` already applies -- deterministic, and honest about
    ranking nothing". Deterministic WITHIN one database, and a `file_id` is a
    `uuid4` P1 mints when it first indexes a path: on two runs over one folder
    from an empty database, §8.6's two ceilings kept a different draw of edges
    and `placement_decisions.payload.graph_anchors` -- the evidence a reviewer is
    shown for a placement -- differed in 24 of 36 rows on the R-78 corpus and 870
    of 1,000 on the scale corpus, while every other derived table was identical.

    So the OTHER end's own bytes and its own path decide, which is R-78's key
    (`grouping/retrieval._corpus` reads `ORDER BY content_hash, current_path`)
    read at this seam. `edge_type` and the bridge follow, and the last term
    separates the two directions one pair can be related in; below them two rows
    are the same relationship recorded under two groups, and which comes first
    cannot be seen. Ordering by `rowid` was ordering by P9's insertion, which is
    an order this function has no contract for.

    The join is LEFT because a `group_edges` row whose other end is not in
    `files` is not something a run produces -- P9 draws edges between indexed
    files -- but a unit fixture that writes edges without files still deserves an
    answer rather than an empty tuple that looks like "no relationships".

    `anchor_file_id` is P9's `from_file_id`: the seed the neighbourhood was
    drawn around. `to_file_id` is the OTHER file, whichever end this one is.
    """
    related = []
    for row in conn.execute(
            "SELECT e.from_file_id, e.to_file_id, e.edge_type, e.weight, "
            "e.bridge_entity_ref FROM group_edges e "
            "LEFT JOIN files f ON f.file_id = CASE WHEN e.from_file_id = ? "
            "  THEN e.to_file_id ELSE e.from_file_id END "
            "WHERE (e.from_file_id = ? OR e.to_file_id = ?) "
            "AND e.superseded_by IS NULL AND e.hub_suppressed = 0 "
            "ORDER BY f.content_hash, f.current_path, e.edge_type, "
            "  e.bridge_entity_ref, e.from_file_id = ?",
            (file_id, file_id, file_id, file_id)):
        spelling = P9_TO_P11_EDGE_TYPE.get(row["edge_type"])
        if spelling is None:
            continue
        related.append({
            "edge_type": spelling,
            "to_file_id": (row["to_file_id"] if row["from_file_id"] == file_id
                           else row["from_file_id"]),
            "anchor_file_id": row["from_file_id"],
            "weight": 1.0 if row["weight"] is None else float(row["weight"]),
            "entity": bridge_entity_for(row["edge_type"],
                                        row["bridge_entity_ref"]),
        })
    return tuple(related)


def semantic_neighbour_nodes(conn: sqlite3.Connection, file_id: str, *,
                             nodes_listing) -> tuple[str, ...]:
    """§4.4's channel, delivered where §6.3 reads it (`104` R-12).

    `3ac0c0b` built the semantic channel and stored its edges; nothing read
    them. `00`:56 is why the channel exists -- "embeddings ... can find files
    such as HW 3.pdf that lack the course code but resemble lecture notes" --
    and `00`:107 is why they arrive here rather than as edges: "Full-text and
    OCR embeddings should retrieve semantically compatible node profiles and
    representative files, especially when the target file is sparse."

    So a semantic neighbour brings the DESTINATIONS it is already listed in,
    and it brings nothing else. `00`:56's other half is enforced by that shape:
    "embeddings never establish the group by themselves. A semantic neighbor is
    simply a file worth bringing into the evidence packet."

    Empty without `--semantic-model`, because P9 writes no such edge then.
    """
    neighbours = dict.fromkeys(
        (row["to_file_id"] if row["from_file_id"] == file_id
         else row["from_file_id"])
        for row in conn.execute(
            "SELECT from_file_id, to_file_id FROM group_edges "
            "WHERE (from_file_id = ? OR to_file_id = ?) AND edge_type = ? "
            "AND superseded_by IS NULL AND hub_suppressed = 0 ORDER BY rowid",
            (file_id, file_id, MUTUAL_SEMANTIC_RETRIEVAL)))
    return tuple(dict.fromkeys(
        node_id for neighbour in neighbours
        for node_id in nodes_listing(neighbour)))


@lru_cache(maxsize=2)
def _encoder_at(model_dir: Path):
    """One loaded model per directory per process, shared by both consumers.

    Recognition and P9 retrieval read the same weights for different questions,
    and loading them twice costs 3-6 seconds and 90 MB for nothing. Keyed on the
    directory because that is what identifies the weights -- `MiniLmEncoder`
    itself digests the file, so two directories holding the same bytes still get
    one entry each and neither is wrong.
    """
    from readers.embedding_minilm import MiniLmEncoder  # noqa: PLC0415

    return MiniLmEncoder(model_dir, max_tokens=SEMANTIC_MAX_TOKENS,
                         batch=SEMANTIC_BATCH, threads=SEMANTIC_THREADS)


def _embedding_runtime(semantic_model, *, versions_for):
    """P9's §4.4 semantic channel, and the retrieval knowledge that reads it.

    **Why this returns BOTH.** `EmbeddingsOn` says vectors will be computed and
    `RetrievalKnowledge` says how they are compared; a run with one and not the
    other either stores vectors nothing reads or asks retrieval for vectors that
    were never stored. `_require_semantic_configuration` catches the second and
    nothing catches the first, so they are built together or not at all.

    **Off unless the weights are named.** `--semantic-model` has no default and
    this file names no download, so an absent directory turns the channel off
    rather than failing a run. Off is the complete `None` shape retrieval reads as
    "there is no semantic channel", never a threshold with no encoder behind it.

    **Nothing leaves the device.** `onnxruntime` opens no socket and a vector is
    computed, stored and compared locally. A vector is not releasable and is not
    made releasable here: `readers.embedding_minilm` says why in its own words --
    mean-pooled MiniLM embeddings are invertible enough that "a vector of a payslip
    is a payslip in a lossier coat".
    """
    if semantic_model is None:
        return EmbeddingsOff(), RetrievalKnowledge(
            document_compatible=None, channel_weights={}, similarity=None,
            similarity_threshold=None, embedding_identity=None, domain=None)

    encoder = _encoder_at(Path(semantic_model))
    config = EmbeddingConfig(
        model_id="sentence-transformers/all-MiniLM-L6-v2",
        # The truncation is part of what produced the vector, so it is part of the
        # model's identity -- the same reasoning `_semantic_classifier` records.
        model_version=f"{encoder.weights_digest}@{SEMANTIC_MAX_TOKENS}tok",
        scope=scope_for(SEMANTIC_ZONES, SEMANTIC_CHAR_BUDGET),
        encoding=FLOAT32_LE, dimension=encoder.dimension)

    def encode(text: str, cfg: EmbeddingConfig) -> EncodedVector:
        vector = encoder.encode([text])[0].astype("<f4")
        return EncodedVector(array_bytes=vector.tobytes(),
                             dimension=int(vector.shape[0]), encoding=cfg.encoding)

    def text_for(conn, file_id: str, content_hash: str, scope: str):
        """This file version's own words. One line, so it can be tested (R-59)."""
        del scope        # the runtime's `config.scope`, already bound above
        return semantic_retrieval_text(conn, file_id, content_hash)

    def similarity(left: bytes, right: bytes) -> float:
        """Cosine, and it IS a dot product here: `MiniLmEncoder.encode` returns
        unit-norm vectors, which is the property that makes this correct."""
        import numpy  # noqa: PLC0415  a deployment import, as everywhere else

        a = numpy.frombuffer(left, dtype="<f4")
        b = numpy.frombuffer(right, dtype="<f4")
        return float(numpy.dot(a, b)) if a.shape == b.shape else 0.0

    return (
        EmbeddingsOn(config=config, encoder=encode, embedding_text_for=text_for,
                     eligible_versions_for=lambda conn, seed, cap: versions_for(
                         conn, cap)),
        RetrievalKnowledge(
            # §4.4's compatibility predicate is a separate channel and nothing has
            # measured one, so it stays absent rather than being guessed at beside
            # a threshold that was measured.
            document_compatible=None,
            channel_weights=SEMANTIC_CHANNEL_WEIGHTS,
            similarity=similarity,
            similarity_threshold=SEMANTIC_SIMILARITY_THRESHOLD,
            embedding_identity=EmbeddingIdentity(
                scope=config.scope, model_id=config.model_id,
                model_version=config.model_version),
            domain=None),
    )


def _semantic_classifier(rules, detector, semantic_model, now):
    """The term detector, with recognition-by-meaning composed behind it.

    RETURNS THE DETECTOR UNCHANGED WHEN NO MODEL IS NAMED. That is the whole of
    the off switch, and it is the honest reading of "absent means refuse, never
    guess": a deployment that did not fetch the weights gets the product it had
    before -- not a guessed model path, and not a crash.

    WHAT IT BUYS, MEASURED on the 199-file ground-truth corpus: the term detector
    classifies 90 files and this adds 13 more, releasing none of the eight
    hand-labelled protected files and protecting none that are not. It is a modest
    number and it is the honest one; the same measurement is why there is no
    protect floor beside `SEMANTIC_FLOORS`.

    THE WEIGHTS ARE READ FROM DISK AND NOTHING LEAVES THE DEVICE. `onnxruntime`
    opens no socket; the 90.4 MB `all-MiniLM-L6-v2` ONNX model (Apache-2.0) is
    fetched ONCE, by hand, from huggingface.co, and this names no download.

    A VECTOR IS THE DOCUMENT, not a fact about it. It is stored by P1 beside the
    observations it was computed from and is never sent anywhere: the nine
    `ALWAYS_LOCAL` kinds are as local in 384 floats as they are in words.
    """
    if semantic_model is None:
        return detector
    from grouping.embeddings import EmbeddingConfig
    from readers.embedding_minilm import MiniLmEncoder, build_anchor_index

    encoder = MiniLmEncoder(semantic_model, max_tokens=SEMANTIC_MAX_TOKENS,
                            batch=SEMANTIC_BATCH, threads=SEMANTIC_THREADS)
    index = build_anchor_index(
        build_schema_anchors(rules, max_words=SEMANTIC_MAX_ANCHOR_WORDS), encoder,
        # Encoding the anchors takes about half a minute and a run pays it once
        # per process. Keyed on the library AND the weights together, so a stale
        # cache is not read rather than being noticed later as a similarity that
        # quietly moved.
        cache_path=Path(semantic_model) / "anchors.npz")
    config = EmbeddingConfig(
        model_id="sentence-transformers/all-MiniLM-L6-v2",
        # The truncation is part of what produced the vector, so it is part of the
        # model's identity. Without it, two vectors read to different depths would
        # be stored under one identity and silently compared.
        model_version=f"{encoder.weights_digest}@{SEMANTIC_MAX_TOKENS}tok",
        scope=scope_for(SEMANTIC_ZONES, SEMANTIC_CHAR_BUDGET),
        encoding=FLOAT32_LE, dimension=encoder.dimension)
    return SemanticRecogniser(
        lexical=detector,
        schema_similarity=schema_similarity_from(
            anchor_scores=index.scores_for, config=config,
            encode=encoder.encode_one, zones=SEMANTIC_ZONES,
            char_budget=SEMANTIC_CHAR_BUDGET, now=now),
        floors=SEMANTIC_FLOORS, handling_for=HANDLING_POLICY, now=now,
        min_chars=SEMANTIC_MIN_CHARS, is_protected=is_protected_container)


#: `104` R-115. §7.5's review sets, DIVIDED BY THE REASON THE SCREEN ALREADY PRINTS.
#:
#: `00` §residual asks for "understandable review sets using reliable
#: characteristics, rather than presenting a single intimidating pile", and names
#: them by what their files SHARE -- "screenshots with no accepted project",
#: "encrypted, unreadable, or unsupported", "multiple plausible destinations", "no
#: extractable text". What shipped was one pile called "Not yet placed" plus one
#: protected set, which §8.6's ceiling then cut into eight-file batches: a person
#: read "Not yet placed (1 of 4)" through "(4 of 4)" and a group of six files was
#: told "3 review sets of it have files under this heading" with nothing on the
#: screen saying which set held which file. A batch index is a ceiling, not a
#: characteristic, and dividing by it divides files that belong together.
#:
#: **The characteristic was already on the screen.** "Same reason for each" is
#: `PlacementDecision.explanation`, and `pipeline._abstention_explanation` writes
#: that off exactly three things: P7's protected flag, whether anything has
#: classified the file, and `abstention_reason` -- a CLOSED vocabulary
#: (`placement.vocabulary.ABSTENTION_REASONS`). So the division below is that same
#: switch, read off the decision the run recorded.
#:
#: **The sentences are the SET's and not `REASON_IN_WORDS`'.** Those are written
#: about one file -- "matched it well enough to be worth proposing" -- and a set is
#: many, so reusing them verbatim would put a pronoun with no antecedent under a
#: heading that has just counted twelve files. What must not be said twice is the
#: DIVISION, and that is the vocabulary rather than the prose;
#: `test_every_abstention_reason_has_a_review_set_of_its_own` pins the two together
#: so a code added to P11 cannot silently fall into the last row here.
#:
#: The last row keeps the name and the sentence the one pile had. It is the set for
#: a reason this deployment has no row for, and it exists because
#: `surface_residual_sets` refuses a partition that misses a file: a file in no set
#: is a file the residual screen never shows.
NOT_YET_CLASSIFIED: str = "not-yet-classified"
NO_MODEL_ALLOWED: str = "no-model-allowed"
WAITING_ON_AN_ANSWER: str = "waiting-on-an-answer"
#: `104` R-113. A placement whose destination is settled and whose MOVE is not:
#: `00`:20 makes crossing a top-level folder the person's own choice, they have
#: not made it, and `mutation/resolution.py` refuses the move when the freeze
#: reaches it. The file has somewhere to go and cannot go there, which is a
#: reason of its own and not "no folder matched".
NOT_ALLOWED_TO_CROSS: str = "not-allowed-to-cross-folders"
NOT_YET_PLACED: str = "not-yet-placed"
PROTECTED_REVIEW_SET: str = "protected"

REVIEW_SET_REASONS: tuple[tuple[str, str, str], ...] = (
    (NOT_YET_CLASSIFIED, "Not yet said what kind of material",
     "nothing has yet said what kind of material these are, so they were not "
     "shown to a model and nothing moved. They are waiting for you to say what "
     "they are: they are not marked sensitive and were not judged on thin "
     "evidence."),
    (NO_MODEL_ALLOWED, "A model was not allowed to look",
     "deciding these needed a model, and the privacy settings on the folder "
     "they are in do not let one be asked about them. Nothing about them left "
     "this device and nothing moved; the evidence is retained."),
    (NOT_ALLOWED_TO_CROSS, "Not allowed to move across folders",
     "this plan has somewhere for these to go and it is under a different "
     "top-level folder from the one they are in now. Moving between your "
     "top-level folders is your choice and you have not made it, so nothing "
     "moved. `--may-cross-folders` is that permission."),
    (pv.NO_SUPPORTED_DESTINATION, "No folder matched",
     "no folder in this plan matched them well enough to be worth proposing."),
    (pv.MULTIPLE_SUPPORTED_HOMES, "More than one folder fits",
     "more than one folder in this plan matches each of these well enough on "
     "its own, and nothing in the evidence separates them. Which one is home is "
     "a choice about your material, not a gap in the evidence."),
    (pv.LOW_MARGIN, "Two folders fit about equally well",
     "two folders in this plan fit each of these about equally well, so picking "
     "one would have been a guess rather than a decision."),
    (pv.CONFLICTING_FACTS, "The readings disagree",
     "what this run read about these points at more than one folder, and the "
     "readings disagree with each other."),
    (pv.SEMANTIC_ONLY, "They only read like a folder",
     "the only thing linking these to a folder was that they read alike, which "
     "is not enough on its own to move a file."),
    (pv.GENERIC_HUB_ONLY, "They share only a word many files share",
     "the only thing these share with a folder is a word many of your files "
     "share, which says nothing about where any of them belongs."),
    (pv.NO_SHARED_BRANCH, "The files these belong with are spread out",
     "the files each of these belongs with are not all under one branch, so "
     "there is no single home to propose for them."),
    (pv.BUDGET_DEFERRED, "This run stopped before reaching them",
     "this run reached its ceiling before deciding these, so nothing was "
     "concluded about them. That is not the same as looking and being unable to "
     "tell (§8.6); the next run picks them up where this one stopped."),
    # `104` §18.2 gap 15 gave this set a SECOND kind of member and the old
    # sentence -- "nothing this run could read says what these are" -- became
    # false for it. A file in two accepted packets is the opposite case: the run
    # read plenty, and two homes have an equal claim on it. §18.3 ranks a false
    # sentence in front of the person the worst class of defect there is, so the
    # words name both askers rather than the older one. What they still refuse to
    # say is that the product could not tell: it could, and what it cannot do is
    # choose for somebody.
    (WAITING_ON_AN_ANSWER, "Waiting on a question you have been asked",
     "this run put a question to you about each of these rather than deciding "
     "on thin evidence: either nothing it could read says what they are, or "
     "more than one home has an equal claim on them. Answering the question "
     "each one carries is what moves them."),
    (NOT_YET_PLACED, "Not yet placed",
     "no destination in this tree matched them well enough to decide without "
     "asking you."),
)

#: Protection is not one of the rows above and never merges into one. Its label and
#: its sentence are exactly what they were before R-115: the set carries the flag
#: `require_set_actionable` raises on, and it is named and counted like every other
#: set and never opened.
PROTECTED_REVIEW_SET_WORDS: tuple[str, str] = (
    "Protected, and not filed in bulk",
    "these are protected material, so they are counted and named here and "
    "nothing was assembled about them. They are not filed in one gesture with "
    "everything else; each one is yours to decide.",
)

REVIEW_SET_WORDS: Mapping[str, tuple[str, str]] = MappingProxyType({
    **{key: (label, reason) for key, label, reason in REVIEW_SET_REASONS},
    PROTECTED_REVIEW_SET: PROTECTED_REVIEW_SET_WORDS,
})

#: The rows a decision's own reason may name, and the protected key is NOT in it.
#: `PROTECTED_REVIEW_SET` is the string `"protected"`, which is also
#: `placement.vocabulary.PROTECTED`; a lookup over `REVIEW_SET_WORDS` would let
#: any code spelled that way put a file into the protected set without P7 having
#: marked it -- a set carrying the flag `require_set_actionable` raises on, filled
#: by something other than the classification that decides it. Protection is
#: decided by `_protected_among` and by nothing else.
ORDINARY_REVIEW_SET_KEYS: frozenset[str] = frozenset(
    key for key, _, _ in REVIEW_SET_REASONS)


def _ask_when_there_are_two_homes_to_offer(node_ids) -> str:
    """§6.9's selector: THE TWO-HOMES CASE IS A QUESTION, NOT AN ABSTENTION.

    **`104` §18.2 gap 15.** This deployment used to be `lambda node_ids:
    pv.ABSTAIN` under a comment reading "there is no screen here to ask on".
    That sentence was true when it was written and has not been true for some
    time. `WAITING_ON_AN_ANSWER` is a review set of its own, `_why` routes every
    `ask_user` decision into it off the decision's own outcome, and
    `review_surface.items.render_state_for` gives such a decision
    `RENDER_ASK` with the `Ask` and the ranked `alternatives` attached -- which
    is the review-surface record for a question to the person, already built,
    already carried by the plan, and reached by nothing because the one selector
    that could produce an `ask_user` always said no.

    So a file with accepted membership in two packets now carries "this fits two
    places: A or B" -- the two node ids as the `Ask`'s options, the ranked
    `alternatives` and the §6.9 explanation beside them -- instead of joining the
    pile of files the run could not explain. `00`:113 is the design's own words
    for the difference: with no shared branch the system "should abstain OR ASK
    THE USER TO CHOOSE A PRIMARY HOME", and only one of those two was reachable.

    **WHAT IS STILL MISSING, SAID HERE SO NOBODY READS MORE INTO THIS THAN IT
    DOES.** The question reaches the REVIEW-SURFACE RECORD and the review set:
    the file is listed under "Waiting on a question you have been asked" and its
    `PlacementReviewItem` renders `ask_user_state` carrying the options. It does
    NOT reach the text report's "Questions only you can answer" panel, because
    that panel prints the `questions` store and this Ask is never
    `record_question`'d -- so there is no `--answer` gesture that resolves it and
    no folder LABELS printed beside the two node ids. Closing that is the same
    shape `_home_questions` already builds (a recorded question whose options are
    folder chains, resolved back through `chosen_destination`), and it is a
    follow-up rather than part of gap 15.

    **NOTHING HERE CHOOSES A HOME.** `resolve_multi_home` has no branch that
    returns a member of `node_ids`, so the strongest thing this selector can do
    is turn an abstention into a question; the packets stay exactly as competing
    as they were and the file still moves nowhere until a person says so.

    **ABSTAIN REMAINS THE ANSWER WHEN THE OPTIONS ARE NOT THERE.**
    `placement.records.Ask` refuses fewer than two options in as many words --
    "one option is a placement wearing a question mark" -- so a question this
    deployment cannot put honestly is not put. `resolve_multi_home` refuses fewer
    than two candidates before this is ever called, so that clause is unreachable
    through today's only caller; it is written anyway because this function is a
    POLICY and the shape of a legal question is the policy's own business, not
    something to be inherited from whichever caller happens to guard it first --
    and `tests/test_ask_about_a_file.py::test_a_question_with_one_option_is_a_
    placement_wearing_a_question_mark` is what holds it. Where §6.9's abstention
    still lands, it lands as `no_shared_branch` and reads "the files these belong
    with are spread out".

    Protected material never reaches here as a question, and the lock for that
    is `placement.pipeline`'s, beside the privacy state this selector cannot
    see: it is handed node ids and nothing else.
    """
    return pv.ASK_USER if len(tuple(node_ids)) >= 2 else pv.ABSTAIN


def run(conn: sqlite3.Connection, directory: Path, *, situation: str, label: str,
        user_id: str, now, out=None,
        also_read: Sequence[Path] = (),
        candidate_roots: Sequence[Path] = (),
        cross_folder_moves: bool = False,
        residuals: Sequence[str] = (),
        sends: Mapping[str, str] = MappingProxyType({}),
        operation_mode: str = OPERATION_MODE,
        record: str | None = None,
        routing: TierRouting | None = None,
        semantic_model: Path | None = None,
        # `104` R-14's mailbox, built beside `routing` by `main` and handed to both
        # the transport and `run_call`. Defaulted: a deployment that records no
        # usage is a real deployment, and every caller that predates this still
        # composes a run.
        usage_recorder: object | None = None,
        # `104` R-92's mailbox, built beside `usage_recorder` by `main` and read
        # by the report: which files each question this run raised would settle.
        # A dict rather than a return value because this function's answer is the
        # RUN, and a second thing bolted onto that record would be a fact about
        # the screen living inside the plan.
        questions_reach: dict[str, tuple[str, ...]] | None = None,
        wire_handle_key: bytes | None = None) -> ProductionRun:
    """One corpus, end to end. Assembles the authorities and calls the composition.

    `out` is here so the protected-container block can be printed the moment the
    scan knows it, ahead of every stage that may refuse. It follows `report`'s own
    convention -- `None` means `sys.stdout` -- rather than taking a policy default.
    """
    catalogue = load_shipped_catalogue(read_packaged_library_file)
    signal = _validate_situation(catalogue, situation)
    # ASKED of the library, not split off the name. The dotted prefix is the
    # template library's word; the 23 domains are `facts.domains.SCHEMA_IDS`.
    # They agree for 201 of 208 situations and disagree for seven, and every
    # applicability row has carried the true answer in `uses_schema` all along.
    schema = schema_for_situation(catalogue, situation)
    # The folders this situation would build, from the same applicability row the
    # line above reads. Here rather than inside the fact pass so a release that has
    # lost its levels refuses before anything is scanned, and so this file -- the
    # one place a policy may be chosen -- is visibly the one that decides what the
    # model is asked.
    folder_levels = folder_levels_for(catalogue, situation)
    # `104` §11.2 STEP 2. The levels whose value the GROUP carries, split off here
    # and used twice below: they are withheld from site A, and P10 is told to read
    # them off the accepted group instead. Read from the same row as the levels
    # themselves, so a release that binds a role differently moves both halves at
    # once and neither can be true of the other's data.
    group_level_fields = group_level_fields_for(catalogue, situation)
    # WHAT SITE A IS ASKED, which is no longer every level. `model_facts.
    # pending_fields_for` offers `pending & {level.field}` and that set becomes the
    # dossier's `allowed_vocabulary`, so a level withheld here is a question not
    # asked -- which is exactly `00`:57's rule that the course's school and term
    # belong to the syllabus anchor and reach a sparse file through its GROUP. Asked
    # per file, `school` was answered by twenty files with the school each of them
    # happened to mention, and five essays from a university course were filed under
    # a high school (`104` §11.1).
    file_level_fields = tuple(level for level in folder_levels
                              if level.field not in group_level_fields)
    # WHAT AN ANCHOR IS ASKED AND NO OTHER FILE IS (`105` §14.4, `104` R-131 with
    # R-102). Step 2's withdrawal above is right about every file except the one
    # that can answer: the syllabus, the enrollment or registration record and the
    # transcript state the institution the course belongs to, and withholding the
    # question from them too is what left R-102 -- nothing writes a `school` fact
    # any more, so the coursework tree has no school level on any corpus. Split off
    # the SAME row as the two lines above, so a release that binds the role
    # differently moves all three together.
    #
    # `school` alone. The other group-level role -- coursework's `cycle_period` --
    # stays withheld from every file: R-101 puts the term on B's per-course
    # acceptances, and nothing here changes B.
    anchor_level_fields = tuple(level for level in folder_levels
                                if level.field in group_level_fields
                                and level.field == SCHOOL_FIELD)
    clock = now()
    _bootstrap(conn)
    # `00`:20's THREE choices, as the person answered them. These were three
    # literals -- one source, no roots, crossing off -- and every reader of R1
    # has been reading an answer nobody was asked for. `scan.py` walks every
    # source and every root from this row and has since it was written.
    sources = [directory, *also_read]
    selection_id = record_selection(
        conn, sources=sources, candidate_roots=list(candidate_roots),
        cross_folder_moves=cross_folder_moves, selected_by=user_id)
    rules = load_rules(_RECOGNITION_MANIFEST.read_text)
    detector = Detector(rules,
                        handling_for=HANDLING_POLICY, now=now,
                        is_protected=is_protected_container,
                        corroborating_observations=_identifier_observations,
                        # P15. What the PERSON has confirmed about readings their
                        # own files could not settle. Read fresh on every call
                        # rather than captured, so an answer given by `--answer`
                        # earlier in this same invocation is already in force.
                        settled_by_user=lambda: activated_schemas(conn))
    # RECOGNITION BY MEANING, composed AROUND the term detector and never in front
    # of it: `SemanticRecogniser` calls it first and returns its answer untouched,
    # so a vector can add a classification where there was none and can never
    # change, lower or second-guess one that exists. No model named, no change at
    # all -- `_semantic_classifier` hands `detector` straight back.
    classify_producer = _semantic_classifier(rules, detector, semantic_model, now)

    #: P7's store, read rather than re-derived. §5.2 and §8.4 make sensitivity
    #: P7's to own; P10 asks and never classifies.
    classifications = ClassificationStore(conn)

    def design_authorities(release: TemplateCatalogue,
                           accepted: Sequence[str]) -> TreeDesignAuthorities:
        # UNIQUE BY CONSTRUCTION, not by counting. This used to seed a counter
        # at `COUNT(plan_versions) + COUNT(tree_nodes)`, on the argument that the
        # count "only has to be an upper bound on what exists". It is not one:
        # `project_branch_preview` mints node ids for every OPTION it previews,
        # and an option the user does not take is never written. So the highest
        # id minted runs ahead of the rows that exist, and a second run over the
        # same folder re-mints an id the first one already used --
        # `IntegrityError: UNIQUE constraint failed: plan_versions.plan_version_id`,
        # a traceback in the one command whose whole report argues that a refusal
        # should be a sentence.
        #
        # It stayed hidden while every tree was one node deep: with one level
        # there were almost no previews to lose ids to. It appeared the moment a
        # second dimension made the option set real.
        #
        # A per-run token rather than a parser over the id format: §5.12 makes a
        # node id opaque, `00` never promises it is a number, and parsing what
        # this file itself spells is how the next spelling becomes a crash. The
        # sequence still reads in mint order within a run, which is what makes a
        # log legible.
        run_token = uuid.uuid4().hex[:8]
        ids = count()
        return TreeDesignAuthorities(
            catalogue=release, group_reader=AcceptedGroupEnumeration(conn),
            # `104` §11.2 step 2, and it is the SAME constant the fact pass split
            # its levels on, handed to P10 as roles rather than as field keys
            # because a role is what a dimension carries and the applicability row
            # is what turns one into the other.
            group_level_roles=GROUP_LEVEL_ROLES,
            # `105` §14.4 with `104` R-131, and every field key in it is spelled
            # here because this is the file that spells them. A school value
            # becomes a folder level only from two anchors that ORIGINATE
            # independently -- different bytes, and neither the other's copy
            # (`duplicate_family`) or re-export (`version_family`) -- and that are
            # about ONE course, which is the subject the anchors share. Two syllabi
            # of unrelated courses name a school between them and no course's
            # school, which is §14.4's own example.
            anchor_agreement=AnchorAgreement(
                fields=frozenset({SCHOOL_FIELD}),
                origin_fields=(DUPLICATE_FAMILY_FIELD, VERSION_FAMILY_FIELD),
                scope_field=SUBJECT_FIELD,
                rests_on_a_name_alone=rests_on_a_name_alone(conn)),
            # PACKET G12. A C3 refusal -- "no recipe recognises the situation
            # these files are in" -- becomes a site-E request, observe-only.
            # `None` when the fact pass did not run, when there is no model, or
            # when E's tier is not on this device, which is the ordinary run and
            # designs the branch exactly as it always has.
            template_call_for=(observe_template_call(
                conn, fact_authorities[0], routing=routing, catalogue=release,
                placeable_file_count=placeable_file_count(conn, scan_run_id[0]))
                if fact_authorities else None),
            limits=TREE_LIMITS, root_anchor=ROOT_ANCHOR,
            selection_id=selection_id, scan_run_id=scan_run_id[0],
            # `104` R-37: every branch's schema, not only the typed situation's.
            # With one branch this is `(schema,)`, exactly as it was.
            active_domains=tuple(dict.fromkeys(
                branch.schema for branch in (
                    partition_cell[0].branches if partition_cell else ()))
                or (schema,)),
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
            # `104` R-37: the branch's OWN situation, read off the group it was
            # accepted under. A branch whose situation is unsettled names no
            # signal, so P10 routes it on its schema alone; a group accepted
            # with one branch is the typed situation's, as it always was.
            detection_signals_for=lambda group: _signals_for_branch(
                branch_of_group.get(group.group_id)),
            # §5.7's ranking. The router already emits candidates in the library's
            # own order and this deployment has no telemetry to re-rank them with,
            # so it keeps that order rather than inventing a score.
            rank_candidates=lambda candidates: list(candidates),
            # P7's OWN class for the file, read through the accessor P10's
            # docstring names -- "the caller passes `upstream.handling_class_for`
            # already bound to a `ClassificationStore`". This answered a flat
            # `ORDINARY_CLASS` instead, which told P10 that nothing in the corpus
            # was sensitive and made its isolation of protected files unreachable.
            # The price was a client's passport number proposed as a FOLDER.
            handling_class_for_member=lambda member: handling_class_for(
                classifications, file_id=member.file_id,
                content_hash=member.content_hash),
            collapse_handling_classes=lambda classes: next(
                (cls for cls in _PROTECTED_ORDER if cls in classes),
                ORDINARY_CLASS),
            handling_class_for_area=lambda area: PROTECTED_CLASS,
            # BOTH classes that carry §8.4's flag in this deployment, not just the
            # strongest. `SAFETY_DOMAIN_HANDLING` gives finance, identity, medical
            # and legal material `sensitive_personal` with `protected=True`, so a
            # set holding only `highly_sensitive_credential_bearing` left every
            # safety-domain file looking ordinary to P10 -- the flag was raised and
            # nothing read it.
            protected_handling_classes=PROTECTED_CLASSES,
            collector_field_keys=COLLECTOR_FIELD_KEYS,
            # §5.11's disclosure test. It asks whether a DIMENSION would expose
            # protected material -- `00`:97 lists it among the structural faults
            # of a proposed template -- and `_v5` refuses the WHOLE candidate when
            # it fires. `subject` is not such a dimension: a course code and a
            # matter number are ordinary folder names, and answering `True`
            # because one value in the level is a passport number would take the
            # person's whole organisation away to hide one folder. That is the
            # failure V5's own docstring records ("the user lost the organisation
            # and kept none of the protection"), arriving from the other side.
            #
            # A single disclosing VALUE is handled where V5's docstring says it is
            # -- protected files are ISOLATED in `materialise_branch`, so the
            # value never reaches the level at all -- which is why the detector
            # below marks a file protected when its evidence names a safety
            # domain, and why nothing needs to be answered here.
            value_discloses_protected_material=lambda field_ref, value: False,
            template_context_for=lambda field_ref, order_index: None,
            mint_node_id=lambda: f"node_{run_token}_{next(ids)}",
            mint_version_id=lambda: f"version_{run_token}_{next(ids)}")

    def _signals_for_branch(branch: Branch | None) -> frozenset[str]:
        if branch is None:
            return frozenset({signal})
        if branch.situation is None:
            return frozenset()
        return frozenset({f"recognition:{branch.situation}"})

    def adopted_folders() -> tuple[str, ...]:
        """The person's own folders, offered to the design as branches (`00`:100).

        `00`:67 builds the top level "out of the accepted groups, domain
        memberships, existing curated folders, and user-approved labels". This
        command used to supply exactly one of the four, and the consequence was
        not that folders were ranked low -- it was that every one of them was
        read, built into a card, and dropped, because the selection filter
        matches on `subject_id` and a folder's is its directory PATH. Eight
        directories in, eight cards built, none chosen, and a tree byte-identical
        to the one the same files produce with no folders at all.

        Every folder is offered, not only the curated ones, because P3 returns
        `undetermined` for every directory today -- §1.1 gives one worked case and
        no threshold -- so a curated-only filter would adopt nothing at all and
        look like a working feature. The card itself says which signal it carries,
        which is §8.6's "leave it in review rather than guess".

        **A candidate root's folders are excluded, and this is §21 enforced
        rather than restated.** P3 records the directories under a candidate root
        -- that is the landscape §21 asks it to understand -- and this function
        offers every directory in the inventory to the design as a branch. Left
        alone, `Academic/Semester One` would become an `existing` node, an
        `existing` ancestor short-circuits `resolve_destination` to its own path,
        and `resolve_destination` decides crossing by looking at where the file
        comes FROM and never at where it lands. A root named as context would
        have become a legal destination with crossing switched off. "Roots are
        context for the proposal canvas, not permission to move files" is a rule
        about what may be built, so it is enforced where branches are chosen.

        **Protected containers are excluded by path, and that is not belt and
        braces.** `represent_protected_areas` already puts them in the tree as
        `protected` nodes that accept no placement; adopting the same directory a
        second time as an `existing` node would mint a node over the same bytes
        that DOES accept placement, turning "marked and counted, never opened"
        into a legal destination inside a sealed bundle. The area is still shown
        and still counted -- it is simply not a folder anything may be filed into.
        """
        sealed = tuple(area.path for area in protected_areas(
            conn, scan_run_id=scan_run_id[0]))

        def _within(path: str, holders: Sequence[str]) -> bool:
            return any(path == holder or path.startswith(holder.rstrip("/\\") + "/")
                       or path.startswith(holder.rstrip("/\\") + "\\")
                       for holder in holders)

        def inside_a_protected_area(path: str) -> bool:
            return _within(path, sealed)

        context_only = tuple(str(root) for root in candidate_roots)

        return tuple(
            folder.directory_path
            for folder in existing_folders(conn, scan_run_id=scan_run_id[0])
            # A scan ROOT is not one of the person's folders inside the picture;
            # it is the ground the picture stands on. P3 marks it by recording no
            # parent directory ("NULL at a scan root: the top of the observed
            # landscape"), and adopting it put the scanned folder inside its own
            # proposal -- a node called `organised` holding `Uni` and `Inbox`,
            # which is the whole corpus wearing a folder's clothes.
            if folder.parent_directory is not None
            and not inside_a_protected_area(folder.directory_path)
            and not _within(folder.directory_path, context_only))

    # §7.4's enablement, and only what the person named. `00`: "These templates
    # are not automatically created", so a run that names none passes an empty
    # library and the tree is exactly the tree it was. The disposition is a
    # physical destination because that is what `--residual` asks for -- a place
    # for these files to go; the other two dispositions (review-only, leave in
    # place) are real §7.4 choices with no flag yet, and inventing a way to say
    # them here would be guessing at a gesture nobody designed.
    #
    # The anchor is this run's own root anchor -- §7.3 leaves five of the
    # nine default parents unstated and P10 refuses to invent one, and the
    # top of the tree the plan is written against is the one place that is
    # not an invention. `_enable_residual_library` then puts a branch that
    # named no parent inside this run's top-level branch rather than at the
    # root, which is `00`:99's rule that a catch-all must not become the
    # product's default answer to ambiguity.
    residual_library = _residual_library() if residuals else {}
    residual_choices = tuple(
        ResidualChoice(template_name=name, action=ENABLE,
                       disposition=PHYSICAL_DESTINATION, display_label=None,
                       parent_node_id=None, root_anchor=ROOT_ANCHOR,
                       merge_into=None,
                       replaces_node_id=None)
        for name in residuals)
    residual_configuration = {name: ENABLE for name in residuals}

    def design_decisions(accepted: Sequence[str]) -> TreeDesignDecisions:
        return TreeDesignDecisions(
            from_plan_version=PLAN_VERSION,
            branch_group_ids=tuple(accepted) + adopted_folders(),
            choose_option=nesting_chooser(conn, asked_at=clock), refinement_for=refinement_for,
            residual_library=residual_library,
            residual_choices=residual_choices,
            residual_configuration=residual_configuration,
            residual_handling_class=lambda name: ORDINARY_CLASS,
            # §5.8, for a residual home. `shallow-by-choice` is the truthful
            # answer and not a convenience: `RESIDUAL_MAX_DEPTH` is zero, so
            # the home is flat DELIBERATELY, and `refine-later` would say the
            # opposite -- that it is unfinished and something should still
            # split it. P11 reads this rather than re-deriving it.
            #
            # Whose deliberate design, though. `--residual` is the person's
            # gesture and the template is here because they typed its name, but
            # the FLATNESS is the product's: nothing could split this home
            # however they answered. So the sentence opens with the same actor
            # `refinement_for` uses, for the same reason -- a `shallow-by-choice`
            # that does not say whose choice it was is R-28 in one more place.
            residual_refinement=(
                SHALLOW_BY_CHOICE,
                f"{actor_phrase(SURFACE_UNATTENDED)} keep this home flat. It is "
                "for files that do not belong to any one folder, so nothing "
                "here will be split into deeper folders."),
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
            # P13's canvas and its plan-version list are the two surfaces the
            # design names, and this command draws NEITHER: it keeps every branch
            # by rule and freezes by rule, with nobody at the screen. Saying
            # `canvas` here put a screen that does not exist into §8.2's
            # permanent log, next to the login name `--user` supplied -- the same
            # overclaim the group records above were repaired for. The third
            # surface exists so the log can say what actually happened.
            surface=SURFACE_UNATTENDED,
            created_at=clock, user_id=user_id,
            component_version=COMPONENT_VERSION)

    def accept_groups(db: sqlite3.Connection,
                      results: Sequence[GroupingResult]) -> tuple[str, ...]:
        partition = partition_cell[0] if partition_cell else None
        if partition is None or partition.single:
            # ONE branch: the acceptance the run has always made, unchanged.
            return review_and_accept(db, results, group_category=schema,
                                     label=label, created_at=clock)

        def remember(merged_id: str, branch: Branch | None) -> None:
            if branch is not None:
                branch_of_group[merged_id] = branch

        return review_and_accept(db, results, group_category=schema, label=label,
                                 created_at=clock,
                                 branch_for=partition.branch_of,
                                 default_branch=partition.default,
                                 on_accepted=remember)

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
                review_decision_ref=None, decided_by=RULES, created_at=clock))

    def set_privacy_policy(db: sqlite3.Connection, plan_version: str) -> None:
        set_policy(db, Policy(
            policy_version=UNSET_POLICY_VERSION, operation_mode=operation_mode,
            # `104` §18.7: the owner's standing answer for protected material on
            # this machine, carried on the plan's policy as on the fact pass's.
            consent_grants=standing_consent_grants(scan_run_id[0]),
            redaction_settings={},
            # §8.4: protected material is not moved automatically without a policy
            # that permits it. This deployment permits none, so nothing protected
            # moves and P11 records the refusal on the decision.
            automatic_move_permissions={}, plan_version=plan_version,
            set_at=clock), component_version=COMPONENT_VERSION, user_id=user_id,
            # The mode, not the word "offline". This said `offline` unconditionally
            # and would have gone on saying it under a mode that sends -- a policy
            # whose own stored reason contradicted the policy, in the one record
            # §8.5's replay reads back to find out what a run was allowed to do.
            reason=f"{operation_mode} run from the command line")

    def _folders_this_file_is_already_in(file_id: str) -> tuple[str, ...]:
        """The names of the folders the person has ALREADY put this file inside.

        §6.2's `CURATED_FOLDER` channel is `00`:100 in the scoring -- "a folder
        that has been deliberately curated should be treated as a strong
        expression of user intent" -- and this command fed it an empty tuple, so
        the channel existed and never once fired. The consequence was measurable
        the moment folders were adopted: the person's own `Uni/CHEM1500` scored
        3/7 against a 0.5 threshold and every file in it abstained
        `no_supported_destination`, because a folder that belongs to no accepted
        group cannot reach the threshold on facts alone.

        Nothing is inferred. The file is IN these folders right now, which is the
        strongest statement of intent available about it and the one piece of
        evidence that costs nothing to read. Ancestors are included as well as
        the immediate parent, because `Uni` is also a folder the person chose to
        put this file under -- retrieval matches on label, so a folder that is
        not in the tree simply matches nothing.

        The scan root is excluded: it is the folder being organised, not a
        statement about any file inside it, and every file would carry it.
        """
        row = conn.execute(
            "SELECT current_path FROM files WHERE file_id = ?", (file_id,)
        ).fetchone()
        if row is None:
            return ()
        roots = {str(path).rstrip("/\\")
                 for path in selection_candidate_roots(conn, selection_id)}
        labels: list[str] = []
        cursor = str(row["current_path"]).rstrip("/\\")
        while "/" in cursor:
            cursor = cursor.rsplit("/", 1)[0]
            if not cursor or cursor in roots:
                break
            labels.append(cursor.rsplit("/", 1)[-1])
        return tuple(labels)

    #: `field=value` -> how many FILES in this corpus state it, built on first
    #: use. The key is P9's bridge spelling, not the bare value: see
    #: `files_stating_each_fact`.
    _files_stating: dict[str, int] = {}
    #: file id -> the frozen destination nodes that already list it, built on
    #: first use. One pass over the index entries for the whole run.
    _nodes_listing: dict[str, tuple[str, ...]] = {}

    def _how_many_files_state_each_fact() -> Mapping[str, int]:
        """§6.5's count, held for the run.

        Built once and held, because P6 has finished writing facts by the time P11
        asks: the rule pass, the family pass and the model fact pass all run inside
        `downstream`, and `evidence_for` is called from P11 and from
        `act_on_residual_sets`, both after. An EMPTY answer is not cached -- a
        corpus whose facts are not written yet must not have emptiness frozen into
        it for the rest of the run.
        """
        if not _files_stating:
            _files_stating.update(files_stating_each_fact(conn))
        return _files_stating

    def _nodes_that_already_list(file_id: str) -> tuple[str, ...]:
        """The frozen destination nodes whose profile names this file.

        §6.2's node profile carries "representative member files", and this is that
        list read backwards. It is how a SEMANTIC neighbour turns into a destination:
        `retrieval.retrieve` takes `semantic_neighbours` as NODE ids, and what P9's
        channel knows about is FILES, so the two are joined by the node profiles the
        freeze already wrote.
        """
        if not _nodes_listing:
            collected: dict[str, list[str]] = {}
            for row in conn.execute(
                    "SELECT node_id, payload FROM placement_index_entries "
                    "WHERE superseded_by IS NULL ORDER BY rowid"):
                for member in json.loads(row["payload"]).get(
                        "representative_files", ()):
                    collected.setdefault(member, []).append(row["node_id"])
            _nodes_listing.update((member, tuple(dict.fromkeys(nodes)))
                                  for member, nodes in collected.items())
        return _nodes_listing.get(file_id, ())

    #: WHERE A PLACEMENT DOSSIER ABOUT THIS FILE WOULD GO, built once for the run
    #: (`104` §17.13 ruling 3). `None` routing is a run with no model at all; a
    #: file the route gives no destination is one no dossier is ever sent for, and
    #: both answer `cloud`, which is the strictest release and therefore the
    #: honest default -- a reading offered under it is one every destination may
    #: see.
    _placement_route = (None if routing is None else target_for(
        conn, routing, C_PLACEMENT, operation_mode=operation_mode))

    def _placement_locality(file_id: str) -> str:
        if _placement_route is None:
            return CLOUD_LOCALITY
        chosen = _placement_route(file_id)
        return CLOUD_LOCALITY if chosen is None else chosen[1].locality

    def evidence_for(file_id: str) -> dict:
        """§6.3's evidence for one file: what this run can address about it.

        Three sources, offered together and never ranked against each other: the
        facts P6 settled and the citations they resolve to, R-135's whole anchor
        lines, and R-148's releasable readings -- the file's own words, which is
        the set site A was shown. A file none of the three can speak for has no
        `evidence_items`, and `pipeline._judge_with_model` records that as a
        pre-call abstention rather than sending a dossier that cites nothing.

        **Every item offered is one the gate will release** (`104` R-154, and
        `104` R-156 for the rest of it). The item set is passed through
        `releasable_items` -- `model_placement.releasable_excerpts`, the door's
        own predicate, asked over the candidate refs -- so what the model is shown
        is exactly what P7 will hand it. R-154 asked the first of those five
        refusals a step early in this loop; the other four need the observation
        row and the length of the unit a span points into, which
        `located_citations` does not carry, so this asks the function that has
        them rather than retyping them at the seam.

        The FACTS are not narrowed with the items. `facts` is P11's own tuple,
        read by retrieval and by §6.10's scoring, and a fact whose only citation
        sits in an always-local zone still reaches both; only its citable item is
        withheld. A file therefore keeps every candidate its facts reached, and
        arrives at site C with R-148's readings to be judged on.
        """
        facts, items = [], []
        seen_items: set[tuple] = set()
        # §3.13's `rejected` is P11's DROPPED state, and this is the third of the
        # three stages that believed a retracted fact (8260f46 fixed P9's and
        # P11's and named this one). A `--reject` writes a `rejected` row that is
        # `active` with no `superseded_by`, which is the exact shape the old
        # WHERE clause selected -- so the claim the person had just told the
        # product was wrong went on scoring their placement. The reliability is
        # the row's own from here on, not `direct` for everything: `MatchingFact`
        # checks it against `EVIDENCE_TYPES`, and a caller that reports every row
        # as `direct` is what made that check unreachable.
        for row in conn.execute(
                "SELECT ff.fact_id, ff.field_key, ff.evidence_refs, "
                "ff.reliability_state, "
                'v.canonical_value FROM file_facts ff JOIN "values" v '
                "ON ff.value_id = v.value_id WHERE ff.file_id = ? "
                "AND ff.active = 1 AND ff.superseded_by IS NULL "
                "AND ff.reliability_state != ?",
                (file_id, pv.DROPPED_RELIABILITY_STATE)):
            from llm_harness.records import EvidenceItem
            from placement.records import MatchingFact

            # THE REAL ADDRESSES, and every one of them (`104` R-11). This read
            # `refs[0]` and then described it as `location="heading"`, span
            # `(0, len(value))`, basis `direct-anchor` -- three values invented at
            # the seam. The span was the length of the FACT VALUE, so a model asked
            # to check a citation was handed coordinates into a string that is not
            # the document; the zone said `heading` for a value read out of a table,
            # a filename or OCR; and `direct-anchor` was printed over an
            # `llm_supported` guess. Nothing downstream could tell the difference,
            # which is what made `00`:58's "the dossier explicitly distinguishes
            # direct evidence from inferred context" untrue at the byte level.
            located = located_citations(
                conn, file_id, json.loads(row["evidence_refs"] or "[]"))
            if not located:
                # A fact whose every citation has gone is a fact nothing can cite.
                # `00`:62's validator checks that each cited span exists; carrying
                # this one forward would put an unresolvable address in front of it.
                continue
            basis = citation_basis_for(row["reliability_state"])
            # `evidence_ref` IS THE FACT'S FIRST RESOLVING CITATION, WHATEVER ITS
            # ZONE, and `104` R-154 deliberately leaves it that way. It is P11's
            # own address for the fact and never a citation the model is offered:
            # its two readers are `retrieval.ConflictConsidered.evidence_ref` --
            # which reaches the dossier as a `conflict_id` and a `kind`, and as
            # nothing else (`dossier._body`) -- and `versions._revalidates`,
            # which hashes it into an evidence snapshot id. Neither resolves it
            # to text and neither sends it. Filtering it here would move P11's
            # record as a side effect of a RELEASE rule, and for a fact whose
            # every citation is always-local there is no other address to move it
            # to: `MatchingFact` requires a non-empty ref, so the choice would be
            # between the true address and dropping a fact P6 settled. The design
            # calls such a fact "supporting evidence" rather than a span; it is
            # offered by its VALUE, on the `facts` tuple, with no citable item.
            facts.append(MatchingFact(
                file_fact_id=row["fact_id"], field=row["field_key"],
                value=row["canonical_value"],
                reliability=row["reliability_state"],
                evidence_ref=located[0][0]))
            for ref, location in located:
                # `104` R-154 lives at the bottom of this function now, with the
                # other four refusals (`104` R-156). The zone test that stood here
                # asked the first of `releasable_excerpts`' five a step early;
                # `releasable_items` asks all five over the same refs, and the
                # zone is part of an observation key's own address -- the key is
                # minted over `serialize_locator(location)`, which carries it --
                # so every live row for a ref this loop resolved has the zone this
                # loop read. The two questions cannot disagree, and one of them is
                # the door's.
                #
                # THE FACT ITSELF IS UNTOUCHED, and that is the difference between
                # this and dropping the row. `MatchingFact` is appended above,
                # before this loop, so retrieval and §6.10's scoring -- which read
                # `facts` and never `evidence_items` -- still see everything P6
                # settled, and the file keeps every candidate its facts reached.
                # What changes is only what may be OFFERED as a citable item: a
                # fact whose every citation the door refuses is offered by its
                # VALUE, which the design calls supporting evidence rather than a
                # span.
                span = location.text_span
                item = (ref, location.zone,
                        None if span is None else (span.start, span.end),
                        row["reliability_state"], basis)
                # An identical item twice says nothing twice. Two facts citing one
                # observation under DIFFERENT reliabilities are two readings of that
                # address and both are kept.
                if item in seen_items:
                    continue
                seen_items.add(item)
                items.append(EvidenceItem(
                    evidence_ref=ref, kind="fact", location=location.zone,
                    excerpt_span=item[2],
                    reliability_state=row["reliability_state"], basis=basis))
        # `104` R-135: THE LINE THE CODE WAS PRINTED ON, beside the code itself.
        #
        # A fact cites the reading that MATCHED it, which for `subject` is the five
        # characters `W3134`; the words `: Data Structures` sit in a second reading of
        # the same heading that no fact has any reason to cite. So the judge was shown
        # a code and never a name, while its own prompt asked it to decide whether two
        # spellings are one thing.
        #
        # `kind="excerpt"`, which is the word the ratified `c_placement` text uses for
        # this: "a reference to text of the file. It carries no text; the text is in
        # released_evidence". `basis` is `direct-anchor` because this is the subject
        # file's OWN reading of its own words -- the same file, the same heading, one
        # reading wider -- and not a neighbour's inference about it.
        #
        # Offered, never paired. Two anchors in one document come back as two items and
        # the model decides; `anchor_line_citations` says why nothing here may choose.
        from llm_harness.records import EvidenceItem

        for ref, location, reliability in anchor_line_citations(
                conn, scan_run_id=scan_run_id[0], file_id=file_id):
            span = location.text_span
            item = (ref, location.zone,
                    None if span is None else (span.start, span.end),
                    reliability, DIRECT_ANCHOR)
            if item in seen_items:
                # Already offered as a fact's own citation. The line is one reading
                # however many ways it was reached.
                continue
            seen_items.add(item)
            items.append(EvidenceItem(
                evidence_ref=ref, kind="excerpt", location=location.zone,
                excerpt_span=item[2], reliability_state=reliability,
                basis=DIRECT_ANCHOR))
        # `104` R-148: THE FILE'S OWN READINGS, which is the set site A was shown.
        #
        # **The defect, measured.** Everything above is built out of FACTS -- rows in
        # `file_facts` with a citation that still resolves -- so a file P6 settled
        # nothing about arrived at `pipeline._judge_with_model` with `evidence_items`
        # empty and was recorded `NOT_ELIGIBLE_FOR_MODEL` before any dossier existed.
        # On the owner's corpus that was 103 of 199 files on r12: 64 unclassified, 39
        # classified, and 52% of their coursework. The most ambiguous file in the
        # corpus was refused the one stage `00` §5 built for ambiguity -- "an LLM
        # receives only compact evidence packets for files or groups that remain
        # ambiguous".
        #
        # **It is the SAME question site A already answers about the SAME file.**
        # `releasable_observations` is that file's capped, gate-checked reading set,
        # and `fact_call_stage` asks for it with this same cap. Reaching for a second
        # spelling of "what may this file offer" would be two answers to one question;
        # `model_placement.releasable_excerpts` applies the five exclusions again on
        # the way out, so nothing here widens what P7 will release.
        #
        # **ALWAYS, and not only when the file has no fact.** A fact's citation is ONE
        # SPAN -- the five characters a rule matched -- and the person placing a file
        # reads the whole excerpt set before deciding where it goes. R-135 is that
        # argument already won for one reading (`W3134` without `: Data Structures`);
        # this is it for the rest of the document. The narrower rule would also make
        # the dossier's contents depend on whether some earlier pass happened to
        # settle a field, which is a fact about P6's luck rather than about the file.
        # The ceiling is what would argue the other way -- `model.max_dossier_tokens_
        # per_call` is 4000 characters, measured by `model_facts.dossier_tokens`, and
        # the gate refuses a request over it with `dossier_over_budget` -- and it does
        # not: the cap is `FACT_CALL_MAX_RELEASED_OBSERVATIONS`, the same twelve
        # readings site A sends under the same ceiling, and the fact items and anchor
        # lines de-duplicate INTO this set rather than adding to it.
        #
        # De-duplicated on `(ref, zone, span)` alone, which is NARROWER than the
        # five-tuple the two loops above use. Their key keeps two reliabilities of one
        # address because two facts reading one observation differently are two
        # readings; here there is no second reading to keep -- one released span shown
        # twice is one span shown twice, and the model would be counting the same
        # words as two pieces of evidence.
        placed = {(offered.evidence_ref, offered.location, offered.excerpt_span)
                  for offered in items}
        # `104` R-159: WHAT THE CEILING HAS LEFT, and site C is where it has to be
        # computed rather than measured after the fact. Site A runs §8.6's ladder and
        # defers a call whose dossier will not fit; this site has no ladder --
        # `_judge_with_model` builds the request and the gate answers -- so an
        # over-ceiling dossier here is `Denied(over_dossier_ceiling)` and the file
        # loses the one stage `00` §5 built for ambiguity. The facts' citations and
        # the anchor lines above are already committed, so the readings fill what
        # they left. `GROUPING_LIMITS.max_dossier_tokens` is the same number the
        # request below is built with and the same one the door measures against.
        remainder = (GROUPING_LIMITS.max_dossier_tokens
                     - released_characters(conn, items))
        for ref, location, reliability in reading_citations(
                conn, file_id, limit=FACT_CALL_MAX_RELEASED_OBSERVATIONS,
                # The PLACEMENT destination for THIS FILE, not site A's and no
                # longer the site's: `routing` points the two sites at their own
                # tiers, a fact call's destination says nothing about where a
                # placement dossier goes, and since `104` §17.13 ruling 3 the
                # placement destination is per file too. `CLOUD_LOCALITY` is a run
                # with no model configured and a file with no route -- no dossier
                # is ever sent for either, and the strict half is the honest
                # default, since cloud releases the least.
                locality=_placement_locality(file_id),
                ceiling=remainder):
            span = location.text_span
            address = (ref, location.zone,
                       None if span is None else (span.start, span.end))
            if address in placed:
                continue
            placed.add(address)
            items.append(EvidenceItem(
                evidence_ref=ref, kind="excerpt", location=location.zone,
                excerpt_span=address[2],
                # The reading's OWN state and the direct-anchor basis, exactly as
                # `model_facts._evidence_items` spells the same observation at site
                # A: this is P4's reading of the file's own words, not a neighbour's
                # inference about it. Nothing here is invented at the seam -- `104`
                # R-11 records what that cost the last time it was.
                reliability_state=reliability, basis=DIRECT_ANCHOR))
        return dict(
            # `104` R-156: the door's own predicate over the whole candidate set,
            # asked once, so the item set the model sees is the set P7 releases.
            facts=tuple(facts), evidence_items=releasable_items(
                conn, items,
                # THE SAME ANSWER the citations above were gathered under. Two
                # reads would offer the model a reading one call collected and the
                # other refuses.
                locality=_placement_locality(file_id)),
            group_ids=accepted_memberships_of(
                conn, file_id, accepted=accepted_ids),
            curated_folder_labels=_folders_this_file_is_already_in(file_id),
            semantic_neighbours=semantic_neighbour_nodes(
                conn, file_id, nodes_listing=_nodes_that_already_list),
            related_files=typed_edges_of(conn, file_id),
            # §6.5's generic-entity suppression. A fact stated by more files than
            # this is treated as a hub rather than as a discriminator. Both numbers
            # are this deployment's; `00` states neither.
            #
            # THE FREQUENCIES ARE NOW MEASURED (`104` R-11) and keyed the way P9
            # names a bridge (R-59), so this lookup answers something for the first
            # time. THE CEILING is still unmeasured, and that is the owner's
            # decision rather than this file's: on the owner's 199 files the 32
            # distinct facts put the commonest at 11, so 200 cannot fire.
            #
            # This is now the ONLY place §4.3 could fire at all. P9's own hub test
            # counts within ONE neighbourhood, and a neighbourhood retrieved on the
            # seed's fact contains that fact and no other -- so with the seed's own
            # basis exempt (as §4.3 requires: a group's basis is not an entity
            # bridging UNRELATED groups) the shared-fact channel can never raise a
            # hub, at any ceiling. P9's ceiling governs `existing-related-folder`
            # and nothing else. A corpus-wide count is what finds an entity that
            # bridges unrelated groups, and this map is the corpus-wide count.
            entity_frequency=_how_many_files_state_each_fact(),
            generic_entity_frequency=200)

    def _protected_among(file_ids: Sequence[str]) -> frozenset[str]:
        """Which of these files carry a live protected classification."""
        if not file_ids:
            return frozenset()
        marks = ",".join("?" * len(file_ids))
        return frozenset(row[0] for row in conn.execute(
            "SELECT DISTINCT file_id FROM classifications "
            f"WHERE file_id IN ({marks}) AND protected = 1 "
            "  AND superseded_by IS NULL", tuple(file_ids)))

    def _file_records(file_ids: Sequence[str]) -> dict:
        """The scan's own row for each of these files, for §7.5's description.

        `00` §residual asks each set to display "representative examples,
        file-type distribution, age range" beside the reason. All three are
        facts P3 already recorded about the file, so they are READ here rather
        than re-observed: a second look at the disk would be a second answer to
        "what is this file", and a residual screen is the last place a file is
        mentioned at all.
        """
        if not file_ids:
            return {}
        marks = ",".join("?" * len(file_ids))
        return {row["file_id"]: row for row in conn.execute(
            "SELECT file_id, filename, extension, observed_timestamps "
            f"FROM files WHERE file_id IN ({marks})", tuple(file_ids))}

    def residual_partition(unplaced: Sequence[str], *, plan_version: str,
                           crossed=None) -> tuple[dict, ...]:
        """§7.5's review sets, divided by the reason the screen already prints.

        `104` R-115. This used to be ONE set of every ordinary unplaced file plus
        one protected set, and §8.6's ceiling then cut the first into eight-file
        batches -- so a person read "Not yet placed (1 of 4)" through "(4 of 4)",
        and a group of six files was told "3 review sets of it have files under
        this heading" with nothing on the screen saying which set held which
        file. `00` §residual asks for sets divided "using reliable
        characteristics", and a batch index is a ceiling rather than a
        characteristic: it divides files that belong together and it names the
        division after a number nobody chose.

        **The characteristic is the one the screen already prints.** "Same reason
        for each" is `PlacementDecision.explanation`, which
        `pipeline._abstention_explanation` writes off exactly three things: P7's
        protected flag, whether anything has classified the file, and
        `abstention_reason`, a closed vocabulary. So the recorded decision is READ
        here rather than the reason being derived a second time out of the same
        evidence -- two derivations of one fact are two answers waiting to
        disagree, and the person would be reading the one that lost.

        **The split by PROTECTION is unchanged, and still comes from
        `classifications`.** P11 builds a real refusal on `residual_set.protected`
        -- `require_set_actionable` raises before it reads any decision -- so the
        flag has to be true of what the set holds. `_protected_among` is the
        source it was before R-115; reading `privacy.protected` off the decision
        instead would move files between protected and ordinary as a side effect
        of renaming the ordinary ones, which is the one line this function may
        not cross.

        **Every unplaced file is still in exactly one set.** A file whose reason
        this deployment has no row for keeps the name the one pile had rather
        than being dropped: `surface_residual_sets` refuses a partition that
        misses a file, and a set nobody can name is a file nobody is shown.

        **AND EVERY BLOCKED PLACEMENT IS IN ONE TOO (`104` R-113).** R-115's
        invariant was "every non-`place` decision", and it left a hole the shape
        of a decision that named a destination and could not act on it: an
        unclassified file whose review policy is `blocked_pending_user`, and a
        move the person has not permitted across their own top-level folders.
        Both are `place` decisions, so neither reached `unplaced`, so neither was
        in any review set -- and `--send-set` is the gesture the residual screen
        offers, so the screen said "nothing on this screen says what these are"
        about files no gesture on it could reach. They arrive here through
        `run_corpus`, which now hands the blocked placements to
        `surface_residual_sets` beside the unplaced files; what this function
        adds is the NAME of the set each one lands in, off the same record.

        **The order is the table's, protected last.** Dict insertion order would
        follow the order files were decided in, so the same corpus would name its
        sets differently between runs and the `--send-set` lines beneath them
        would move -- which is a person's typed command changing under them.
        """
        if not unplaced:
            return ()
        from datetime import datetime, timezone

        from placement.privacy import is_unclassified
        from placement.store import decisions_for_plan

        protected = _protected_among(unplaced)
        records = _file_records(unplaced)
        decided = {decision.subject.file_id: decision
                   for decision in decisions_for_plan(conn,
                                                      plan_version=plan_version)
                   if decision.subject.file_id}

        def _by_name(file_id: str) -> tuple[str, str]:
            row = records.get(file_id)
            return (row["filename"] if row is not None else "", file_id)

        def _why(file_id: str) -> str:
            """Which set this file is in, off its own recorded decision."""
            decision = decided.get(file_id)
            if decision is None:
                return NOT_YET_PLACED
            if decision.outcome == pv.PLACE:
                # `104` R-113. A placement is here only because a POLICY is
                # holding it, and the policy is the set it belongs in.
                #
                # PRIVACY FIRST, because it is on the record and the crossing is
                # derived: `blocked_pending_user` is reachable from exactly one
                # place -- `review_policy_for`'s first rule, an unclassified
                # subject -- so the same switch `_abstention_explanation` uses is
                # asked here and gives the same answer it gives an abstention
                # that stopped for the same fact. Two names for one state would
                # be two names on one screen.
                if decision.review_policy == pv.BLOCKED_PENDING_USER:
                    return (NOT_YET_CLASSIFIED
                            if is_unclassified(decision.privacy)
                            else NO_MODEL_ALLOWED)
                if (crossed is not None and decision.destination is not None
                        and crossed(file_id,
                                    decision.destination.node_id) is not None):
                    return NOT_ALLOWED_TO_CROSS
                # A placement nothing is holding is not residual at all, and
                # `run_corpus` does not send one here. Reached only if it ever
                # does, and then it keeps the name the one pile had rather than
                # being dropped, exactly as an unknown abstention reason does.
                return NOT_YET_PLACED
            reason = decision.abstention_reason
            if reason == pv.PRIVACY_BLOCKED:
                # The two halves `_abstention_explanation` already tells apart,
                # and it is the same question asked of the same record: one is
                # "nothing has said what this is yet", the other is "a model was
                # not allowed to look". `66` §4 forbids them sharing a message,
                # so they may not share a set either.
                return (NOT_YET_CLASSIFIED if is_unclassified(decision.privacy)
                        else NO_MODEL_ALLOWED)
            if reason in ORDINARY_REVIEW_SET_KEYS:
                return reason
            if decision.outcome == pv.ASK_USER:
                # Not an abstention: the run turned it into a question the report
                # prints. Folding it into "no folder matched" would tell somebody
                # their file has no home when what it has is a question.
                return WAITING_ON_AN_ANSWER
            return NOT_YET_PLACED

        held: dict[str, list[str]] = {}
        for file_id in sorted(unplaced, key=_by_name):
            held.setdefault(PROTECTED_REVIEW_SET if file_id in protected
                            else _why(file_id), []).append(file_id)

        def _day(stamp: float) -> str:
            return datetime.fromtimestamp(stamp, timezone.utc).date().isoformat()

        def _set(key: str, members: tuple[str, ...]) -> dict:
            label, reason = REVIEW_SET_WORDS[key]
            is_protected = key == PROTECTED_REVIEW_SET
            extensions: dict[str, int] = {}
            stamps: list[float] = []
            for file_id in members:
                row = records.get(file_id)
                if row is None:
                    continue
                extensions[row["extension"] or "(no extension)"] = 1 + extensions.get(
                    row["extension"] or "(no extension)", 0)
                mtime = json.loads(
                    row["observed_timestamps"] or "{}").get("mtime")
                if mtime is not None:
                    stamps.append(float(mtime))
            return {"label": label, "member_file_ids": members,
                    # Named files, so a person can see WHICH of theirs is here.
                    # Protected files are named and counted like any other: the
                    # rule is that they are never opened, not that they are
                    # never mentioned, and a set that hid them would be the
                    # silent omission the same rule forbids.
                    "representative_examples": members[:3],
                    # Commonest first, then alphabetical, so the reading is
                    # "mostly screenshots" rather than a list in scan order.
                    "file_type_distribution": tuple(sorted(
                        extensions.items(), key=lambda pair: (-pair[1], pair[0]))),
                    # THE STAMP P3 RECORDED, rendered as a UTC day and nothing
                    # more. SPEC Q2 is open on timestamp representation and P3
                    # deliberately stores the `stat` value rather than choosing a
                    # format; `age_range` is two strings and a float is not one,
                    # so a day is the narrowest reading of that value this field
                    # can carry. A set whose files carry no mtime leaves it EMPTY
                    # rather than dating them from anything else on the row.
                    "age_range": ((_day(min(stamps)), _day(max(stamps)))
                                  if stamps else ()),
                    "evidence_availability": "partial",
                    "sensitivity_status": "protected" if is_protected else "none",
                    "protected": is_protected, "weak_graph_neighbours": (),
                    "reason_not_placed": reason}

        return tuple(
            _set(key, tuple(held[key]))
            for key in (*(row[0] for row in REVIEW_SET_REASONS),
                        PROTECTED_REVIEW_SET)
            if held.get(key))

    def _every_destination(frozen) -> tuple[DestinationChoice, ...]:
        """Every place a file can go in this plan, with the path a person reads.

        The `display_path` is the answer's identity -- what a `--answer` line
        carries and what the store keeps -- and the `node_id` is this run's address
        for it. Both come from the same walk so they cannot disagree, which is the
        whole reason the resolution is a lookup rather than a second derivation.

        A node that accepts no placement is not here: an answer naming one would be
        refused by `legal_node_ids` after the person had already given it, which is
        a question whose answer is rejected on the way in.

        **IN THE TREE'S OWN ORDER, and `104` R-116 is why.** "Where should the
        files in Downloads go?" offered sixteen folders as `frozen.nodes` happened
        to hold them -- Coursework, Spring2026, CS3134, ECON2010/lecture,
        PHYS1401/lecture, W3134/lecture, cover letter, ECON2010 -- which is a
        list with no order a person can follow, printed nine lines under a
        picture of the same folders in the order they nest. The list IS the tree,
        so it is walked the way `report` draws it: children under their parent,
        siblings in the order the tree holds them. NOT sorted by string, which
        would put `Coursework/W3134` above `Coursework/W3134/exam` by accident
        and break the moment a label starts with a digit.

        A node the walk never reaches -- one whose parent id names nothing in
        this tree -- is APPENDED rather than dropped. Ordering a list is not a
        licence to shorten it, and a destination missing from a question is one
        an answer can never name.
        """
        labels = {node.node_id: node.display_label for node in frozen.nodes}
        parents = {node.node_id: node.parent_node_id for node in frozen.nodes}

        def path_of(node_id: str) -> str:
            parts: list[str] = []
            walk: str | None = node_id
            while walk is not None and walk in labels:
                parts.append(labels[walk])
                walk = parents[walk]
            return "/".join(reversed(parts))

        by_parent: dict[str | None, list] = {}
        for node in frozen.nodes:
            by_parent.setdefault(node.parent_node_id, []).append(node)
        walked: list = []
        seen: set[str] = set()

        def descend(parent: str | None) -> None:
            for node in by_parent.get(parent, ()):
                # Marked BEFORE the recursion, so a tree that somehow names
                # itself as its own ancestor is a short list rather than a
                # recursion error on somebody's folder.
                if node.node_id in seen:
                    continue
                seen.add(node.node_id)
                walked.append(node)
                descend(node.node_id)

        descend(None)
        walked.extend(node for node in frozen.nodes if node.node_id not in seen)

        return tuple(
            DestinationChoice(node_id=node.node_id,
                              display_path=path_of(node.node_id))
            for node in walked if node.accepts_placement)

    def _destinations_to_offer(frozen):
        """The folders a person is offered when asked where something goes.

        **What this run PROPOSES, plus the folder the files are in already.** A real
        run freezes 43 places a file can go, 39 of them the person's own folders,
        and a question offering 43 options is a directory listing with a question
        mark on it. The four the run proposes are the structure the plan is actually
        asking the person to adopt, so they are the choice already in front of them.

        The folder the files are in is the fifth, and it is not a rounding-out: it
        is the answer "leave them where they are", which the ground-truth labeller
        wrote in as many words for two of these files -- *"a person may not want it
        filed at all"* and *"the honest outcome is to leave it where it is"*. A
        question that offered only the new structure would make moving the only
        expressible answer, which is the product deciding the thing it is asking
        about.

        P10 already tells the two apart through the `existing_path` the report reads
        to print "[yours already]", so that is what is read here -- a second way of
        distinguishing the person's folders from the engine's is a second answer
        waiting to disagree. A node that accepts no placement is never offered:
        `legal_node_ids` would refuse the answer afterwards, which is a question
        whose answer is rejected after it is given.
        """
        every = _every_destination(frozen)
        by_node = {choice.node_id: choice for choice in every}
        existing_of = {node.node_id: getattr(node, "existing_path", None)
                       for node in frozen.nodes}
        proposed = tuple(choice for choice in every
                         if not existing_of.get(choice.node_id))
        theirs: dict[str, DestinationChoice] = {}
        for choice in every:
            existing = existing_of.get(choice.node_id)
            if not existing:
                continue
            try:
                relative = str(Path(existing).relative_to(directory).as_posix())
            except ValueError:
                continue
            theirs.setdefault(relative, by_node[choice.node_id])

        def for_folder(folder: str) -> tuple[DestinationChoice, ...]:
            here = theirs.get(folder)
            # `104` R-116. FILTERED OUT OF THE WALK, not concatenated onto the
            # end of it. `proposed + (here,)` puts the folder the files are in
            # last wherever the tree puts it, which is the tree's order broken
            # by the last line -- and the whole point of the row is that a
            # person can follow the list against the picture above it.
            offered = {choice.node_id for choice in proposed}
            if here is not None:
                offered.add(here.node_id)
            return tuple(choice for choice in every
                         if choice.node_id in offered)

        return for_folder

    def _node_for(frozen) -> dict[str, str]:
        """Folder chain -> this plan version's node id, built once per tree.

        The answer store holds folder chains and P11 places on node ids, and this
        is the one place the two are joined -- a second one would be a second
        opinion about which folder a person meant.
        """
        return {choice.display_path: choice.node_id
                for choice in _every_destination(frozen)}

    def _home_questions(frozen, unreadable) -> dict[
            str, tuple[str, tuple[str, ...]]]:
        """One question per folder nothing could be read from, and the words and
        destinations each of its files carries into P11.

        Recorded HERE rather than in `_raise_blocked_questions`, and the reason is
        the tree: a question offering destinations cannot be written before the
        destinations exist, and they exist when the plan is frozen. The recording
        is idempotent by question id, so the second call for the residual pass adds
        nothing.

        `unreadable` is `folders_nothing_could_be_read_from`'s answer, passed IN
        rather than asked for again: it stands on `_files_something_was_read_out_of`,
        a `DISTINCT` over `evidence` this codebase has measured as its largest
        single read, and `already_answered` needs the very same list to know which
        files a question named (`104` R-86). One reading, two readers.
        """
        node_for = _node_for(frozen)
        offer_for = _destinations_to_offer(frozen)
        asks: dict[str, tuple[str, tuple[str, ...]]] = {}
        for folder, file_ids, held in unreadable:
            offered = offer_for(folder)
            if len(offered) < 2:
                # Fewer than two places to put anything is not a choice, and
                # offering it as one would dress the engine's only option as the
                # person's decision. `question_for_unreadable_folder` refuses that
                # outright; this returns first so a corpus that simply built a
                # shallow tree gets silence rather than a traceback.
                continue
            question = question_for_unreadable_folder(
                folder=folder, choices=offered, file_count=len(file_ids),
                protected_count=held,
                # The scan root's relative name is `.`; the person typed a
                # folder with a name, and that is the one the question uses.
                shown_as=directory.name if folder == "." else None)
            record_question(conn, question, asked_at=clock)
            # The WORDS and the DESTINATIONS, not a `placement.records.Ask`. P11
            # owns that record and `test_ambiguity_cases` asserts `pipeline.py` is
            # its only builder -- a guard from when §6.9's question had a shape and
            # no producer. Minting one here would put its invariants in a second
            # place and make the review surface's "what P11 asked" partly this
            # file's account instead.
            #
            # The option ids are folder CHAINS, so the node ids are looked up in
            # the same map the answer is resolved through: the person is offered
            # exactly the destinations an answer can later reach.
            offered_nodes = tuple(
                node_for[option.option_id] for option in question.options
                if option.option_id in node_for)
            if len(offered_nodes) < 2:
                continue
            for file_id in file_ids:
                asks[file_id] = (question.prompt, offered_nodes)
        return asks

    def _their_own_folder_made_for_what_it_holds(frozen) -> dict[str, str]:
        """WHICH OF THE PERSON'S FOLDERS WERE BUILT FOR WHAT IS IN THEM.

        P11's `_a_folder_made_for_this_keeps_it` refuses to carry a file out of
        one of these on an artifact kind or a period alone, and it is told which
        files are in one rather than working it out: which folders qualify turns
        on how many files a folder needs before "every one of them agrees" means
        anything, and that band is this file's to author.

        THE BAND IS `TREE_LIMITS.tiny_folder_max_files`, ALREADY THIS FILE'S
        ANSWER to how few files is too few to be worth a folder -- §5.9's
        tiny-folder warning and `_depth_disposition` both read the same number,
        and P10's own floor inside `settled_values_by_directory` refuses a folder
        of one for the same reason ("a set of one is always unanimous"); the
        coverage half of the question is `stated_by_every_file`, which
        `settled_values_stated_by_every_file` names and explains in P10.
        One reading of one band, in one place. A number tuned until this corpus
        came out right would be a rule nobody authored.

        AT THIS SETTING IT RESTATES P10'S OWN FLOOR RATHER THAN TIGHTENING IT,
        and it is written here anyway because the floor is the load-bearing part
        and it should be visible where the rule is composed. What it excludes,
        measured: five of the nine résumés this product places sit ALONE in a
        folder of their own -- `Desktop/Resume - Joseph Yung (9 Aug)/` holds one
        file and that file is a résumé -- so with no floor at all each of those
        folders would be "made for" résumés and the person's own copies would
        stop being filed. The four résumés sitting loose in `Desktop` beside
        seven other things are excluded by coverage instead, being four of eleven
        and not eleven of eleven. The day either number moves, one band moves.

        Read off the ADOPTED NODES rather than off paths, so the folders asked
        about are exactly the ones the tree shows the person as theirs, and no
        separator rule is invented here to find a file's parent.
        """
        # The band first, then ONE read for every folder that clears it. P10's
        # coverage read walks the corpus once per destination-eligible field, so
        # asking it per node made the walk once per node as well (`104` R-79);
        # asked together it is the same question with the corpus read once.
        # Folders that fail the band are never asked, exactly as before.
        holding: list[tuple[object, frozenset[str]]] = []
        for node in frozen.nodes:
            if node.existing_path is None:
                continue
            here = file_ids_in_directory(conn, directory_path=node.existing_path)
            if len(here) <= TREE_LIMITS.tiny_folder_max_files:
                continue
            holding.append((node, here))
        made_of = settled_values_by_directory(
            conn, directory_paths=[node.existing_path for node, _ in holding],
            stated_by_every_file=True)
        made_for: dict[str, str] = {}
        for node, here in holding:
            if not made_of[node.existing_path]:
                continue
            for file_id in here:
                made_for[file_id] = node.node_id
        return made_for

    def _the_folder_each_file_is_in(frozen) -> dict[str, str]:
        """WHICH OF THE PERSON'S FOLDERS EACH FILE IS ACTUALLY SITTING IN.

        P11 tells REFINEMENT from REMOVAL with this (`00`'s amendment of line 22,
        `104` §13.8): a candidate inside the folder a file is already in is the
        file going deeper into the arrangement its owner built, which is allowed;
        anything else is coming out of that arrangement, which stays constrained.

        THE SAME READ AS `_their_own_folder_made_for_what_it_holds` ABOVE, WITHOUT
        ITS TWO GATES, and the difference is the whole point. That one answers
        "was this folder BUILT for this kind of thing", so it needs a floor under
        "every file agrees" and it needs them to agree. This one answers "is this
        where the file LIVES", which is true of a folder whose files agree about
        nothing. `Desktop/Python 1006` holds twenty-one files that agree about
        nothing, so it is absent from that mapping and present in this one -- and
        it is the folder whose six lecture files stop one level short of the child
        built for them (R-48).

        Read off the ADOPTED NODES for the same reason: the folders named here are
        exactly the ones the tree shows the person as theirs, and no separator rule
        is invented to find a file's parent.
        """
        here: dict[str, str] = {}
        for node in frozen.nodes:
            if node.existing_path is None:
                continue
            for file_id in file_ids_in_directory(
                    conn, directory_path=node.existing_path):
                here[file_id] = node.node_id
        return here

    def placement_inputs(tree) -> PipelineInputs:
        observe_cd = (observe_placement_injections(
            conn, fact_authorities[0], routing=routing,
            plan_version=tree.tree.plan_version_id,
            placeable_file_count=placeable_file_count(conn, scan_run_id[0]),
            # THIS RUN'S MODE, and it stopped being cosmetic the day C's
            # `eliminate-v2` was ratified for the cloud: the site now HAS a cloud
            # candidate, so a default here would have kept every placement call on
            # this device under a consent that permits sending, and the evidence
            # gathered for it -- which does read the mode -- would have been
            # collected for a destination the call never used.
            operation_mode=operation_mode)
            if fact_authorities else {})
        unreadable = folders_nothing_could_be_read_from(conn, root=directory)
        asks = _home_questions(tree.tree, unreadable)
        node_of = _node_for(tree.tree)
        # `104` R-86. THE FILES EACH HOME QUESTION WAS ASKED ABOUT, which is the
        # scope its answer reaches. Derived from the very list the question was
        # built from, so the two cannot come apart: `_home_questions` walks
        # `unreadable` to write the questions and this walks it to say who they
        # named. Protected files fall out here exactly as they fall out there --
        # counted in the question, named in no list, and so decided one at a time
        # rather than by an answer given about the folder around them.
        asked_about = {file_id: folder
                       for folder, file_ids, _ in unreadable
                       for file_id in file_ids}
        # `104` R-113. WOULD THIS MOVE CROSS A FOLDER THE PERSON KEEPS, asked of
        # the same landscape `main` hands the report and the freeze: the three
        # arguments are the ones this run was called with, so the dict cannot
        # differ from the one built there. `None` when the person has already
        # said such moves are allowed, because then nothing is being held.
        crossed = (None if cross_folder_moves else crossing_folder_for(
            conn, nodes=tree.tree.nodes,
            landscape=high_level_folders(directory, also_read,
                                         candidate_roots)))

        def already_answered(subject) -> str | None:
            """The node the person's answer names, in THIS plan version's tree.

            **THE ANSWER REACHES THE FILES THE QUESTION NAMED, AND NO OTHERS**
            (`104` R-86). The screen says "This decides where those 2 files are
            filed"; this used to key on the folder the file happens to sit in, so
            `--answer home:.=Coursework` about two unreadable scans re-homed all
            33 files in the folder and the freeze that followed froze nothing.
            The sentence and the reach are one fact and the sentence was right:
            `chosen_destination` already states the rule -- "a person who says a
            folder of unreadable scans belongs under `Vaccine records` has said
            that about THOSE files" -- and this is the reading that was
            contradicting it. A folder-wide answer needs a folder-wide question,
            which this screen does not ask.

            So a file the question did not name gets `None` and is decided by the
            run exactly as it was before anybody answered: a readable file beside
            the scans, a file that arrived after the question was asked, a
            protected file that was counted and never named.

            **The stored answer is a folder chain and the resolution to a node id
            happens HERE, once per run.** Every run freezes a new plan version and
            mints new node ids for the same folders, so an answer that had stored an
            id would have been refused by the next run as a destination from a tree
            that no longer exists -- the person's answer silently ceasing to mean
            anything, one run after they gave it. `gates_template` records the same
            decision for the same reason, and this is that reason measured: the
            round trip failed exactly this way before the chain replaced the id.

            `None` when the chain resolves to nothing. A folder the person named and
            the plan no longer builds is a real change they should see as the
            question coming back, not as a placement into a folder that is gone.
            """
            folder = asked_about.get(subject.file_id)
            if folder is None:
                return None
            named = chosen_destination(conn, scope=f"{SCOPE_FOLDER}:{folder}")
            return None if named is None else node_of.get(named)

        return PipelineInputs(
            plan_version=tree.tree.plan_version_id, tree=tree.tree,
            policy=SUPPORT_POLICY, limits=placement_limits(conn),
            # `104` R-115. The partition divides by the reason each file's own
            # decision recorded, and a decision is addressed by
            # `(plan_version, subject_ref)` -- every run mints a new plan
            # version, so a lookup without one would read the answer some
            # earlier run gave about the same bytes. It is bound HERE because
            # this is the first place the frozen tree exists; `residual_partition`
            # is defined before the tree is built and P11 calls it with the
            # unplaced ids and nothing else.
            partition=lambda unplaced: residual_partition(
                unplaced, plan_version=tree.tree.plan_version_id,
                crossed=crossed),
            # `104` R-113. WHICH OF THIS RUN'S PLACEMENTS A CROSSING RULE IS
            # HOLDING, so P11 can put them in a review set beside the files it
            # never placed. P11 cannot ask this for itself: the answer needs
            # §1.1's folder landscape, which is a fact about the command this
            # run was typed in and not about the corpus, and this is the same
            # reading the report marks with and the freeze refuses on.
            a_move_the_person_has_not_permitted=crossed,
            # §6.9, when a file has two homes. `104` §18.2 gap 15.
            ask_or_abstain=_ask_when_there_are_two_homes_to_offer,
            max_return_cycles=1,
            # §6.12 step 7's model path, absent in every part. `model_path_available`
            # reads these as a set: with them `None`, a file that needs a judgement
            # abstains with a reason instead of being decided by nothing.
            # `104` §7 Phase 1 step 6: C and D run and apply nothing. Eight of
            # the nine arrive together or not at all -- `model_path_injections`
            # is all-or-nothing, and a half set is the failure
            # `model_path_available` exists to catch. Empty when no model is
            # configured or when C's tier is not on this device, which leaves
            # every one of them `None` and the model path off, exactly as before.
            **{**dict.fromkeys(OBSERVE_PLACEMENT_FIELDS), **observe_cd},
            # EIGHT of the nine, not nine. This one is the exception and R-55 is
            # why: P8's two sensitivity checks REFUSE with it, and a refusal that
            # needs no ratified prompt should not wait for one. `None` here meant
            # `SENSITIVITY_RESTRICTION_IGNORED` could never fire, which the D2
            # bakeoff measured -- both local D texts filed the redacted statement
            # into Receipts and P8 accepted it. Supplying it alone leaves
            # `model_path_available` false, so the path stays off.
            sensitivity_policy=sensitivity_policy_for(conn),
            # THE POLICY, and this file is where it belongs. P11 asks which files
            # are worth a person's attention and holds no answer of its own;
            # `folders_nothing_could_be_read_from` is the answer and carries the
            # measurement behind it.
            ask_about_file=lambda subject: asks.get(subject.file_id),
            chosen_by_user=already_answered,
            fields_that_cannot_anchor_a_move=FIELDS_THAT_CANNOT_ANCHOR_A_MOVE,
            their_own_folder_made_for_what_it_holds=(
                _their_own_folder_made_for_what_it_holds(tree.tree)),
            p2=None,
            the_folder_each_file_is_in=_the_folder_each_file_is_in(tree.tree))

    #: One slot, filled by `_model_fact_pass` when it builds A's authorities and
    #: read by `downstream` for the observe sites. A list because the pass is a
    #: closure and this is the one value that has to cross out of it.
    fact_authorities: list = []

    #: `104` §17.1 and §17.9: what site G answered, filled by `_model_fact_pass`
    #: and read by the report. One slot for the same reason as `fact_authorities`:
    #: the pass is a closure and this is the one value that has to cross out of it.
    #:
    #: THE NUMBER THAT SAYS WHETHER THIS WORKED is `len(named)` against the roster:
    #: how many files were asked about their OWN situation instead of the run's.
    #: `104` §17.2 is what a number with no provenance costs, so the counts beside
    #: it say what happened to every file that is not in it.
    situation_cell: list = [_NOTHING_ASKED]

    #: `104` §18.2 gap 10: file_id -> (bucket, cause), what the fact pass decided
    #: about each file it walked. Filled by `_model_fact_pass` and read by
    #: `_reconcile_the_roster`, which runs whether or not the pass reached its end.
    #:
    #: A DICT AND NOT A COUNT, for `ProgressEntry.file_ids`' own reason: the rule
    #: being checked is "every indexed file is in exactly one bucket", and that is
    #: not assertable from counts -- two buckets of four and five over nine files
    #: could both have missed the same file and double-counted another and the
    #: arithmetic would still look right.
    fact_pass_verdicts: dict[str, tuple[str, str | None]] = {}

    #: WHY THE FACT PASS DID NOT RUN, or `None` because it did. One slot for
    #: `fact_authorities`' reason. Carried out of the closure rather than dropped
    #: at a bare `return`, because `104` §18.2 gap 10's sum has to print on those
    #: runs too and "nothing was asked" is not a reason a person can act on.
    fact_pass_not_run: list[str | None] = [None]

    #: `104` R-37: the run's top-level branches and the situation each carries,
    #: filled by `_partition_branches` in `downstream` once the deterministic
    #: facts exist, and read by the fact pass, the acceptance and the design.
    #: One slot for the same reason as `fact_authorities`.
    partition_cell: list[BranchPartition] = []
    #: merged accepted group id -> the branch it was accepted under, filled by
    #: `accept_groups` and read by `design_authorities` for P10's signals.
    branch_of_group: dict[str, Branch] = {}
    #: `104` R-37's questions and the files each reaches, merged into R-92's
    #: mailbox at the end of the run.
    branch_reaches: dict[str, tuple[str, ...]] = {}

    def _anchor_facts_of(file_id: str, content_hash: str) -> tuple[tuple[str, str], ...]:
        """The file's `(field, value)` facts at P9's anchor bar, and no lower."""
        return tuple(
            (row["field_key"], row["canonical_value"])
            for row in facts_for_file(conn, file_id, content_hash)
            if row["active"] and row["superseded_by"] is None
            and row["reliability_state"] in ANCHOR_STATES)

    def _situations_of(schema_id: str) -> tuple[str, ...]:
        return tuple(row.name for row in shipped_situations(catalogue)
                     if row.schema == schema_id)

    def _partition_branches(run_id: str) -> BranchPartition:
        """`104` R-37. Which branch each file is under, from the facts P6 wrote.

        AFTER the deterministic passes and BEFORE the model pass, because the
        anchor is a validated `work_type` and the whole point is that a model is
        asked a branch's questions only of that branch's files. The recogniser is
        `detector.explain`, the same term detector `classify` ran, read here and
        written nowhere: `test_step4_recognition_as_a_gate` pins that its verdict
        reaches no column, and this keeps it so.

        A branch whose situation is unsettled has its question recorded here --
        `question_for_situation`, the trigger that was registered and never
        fired -- and the files it reaches are remembered for the screen.
        """
        partition = partition_by_branch(
            roster=corpus_roster(conn, run_id),
            default_label=label, default_situation=situation,
            default_schema=schema,
            anchor_facts_of=_anchor_facts_of, owner_of_term=WORK_TYPE_OWNER,
            fields_of_schema=lambda schema_id: DOMAIN_FIELDS.get(schema_id, ()),
            verdict_of=lambda file_id, content_hash: detector.explain(
                conn, file_id, content_hash),
            situations_of=_situations_of,
            chosen_situation=lambda scope: selected_situation(conn, scope=scope))
        for branch in partition.branches:
            if branch.settled or not branch.file_ids:
                continue
            question = question_for_situation(
                branch_label=branch.label,
                situations=branch.candidate_situations,
                file_count=len(branch.file_ids))
            record_question(conn, question, asked_at=clock)
            branch_reaches[question.question_id] = branch.file_ids
        return partition

    def _model_fact_pass(run_id: str) -> None:
        """Ask a model about the fields the deterministic producers left open.

        **It happens only when both things are true**, and the gate is not the
        switch. `routing` is `None` when no key is configured, and
        `operation_mode` is `hybrid` only when this folder's stored consent says
        so -- `main` reads it through `operation_mode_for`. `mode_forbids` at the
        door is the defence behind that, not the decision: a run that reached the
        gate to be told `offline` would have built a request about a person's file
        that they had not agreed to have built.

        **The policy is put in force HERE, and it is a second policy row rather
        than an early copy of `set_privacy_policy`'s.** That one is written against
        the FROZEN plan version, after the tree exists, because that is the version
        P11 asks about. This one is written against `PLAN_VERSION`, the working
        version P9's groups are recorded under, because the gate is asked now and
        §8.4's audit record names the authorizing policy -- and there has to BE one
        to name. Two versions, two rows, and each says the mode its own stage ran
        under.
        """
        if routing is None:
            # `104` §18.2 gap 10: THE REASON LEAVES WITH THE RETURN. Every one
            # of the four returns in this function used to drop it, and
            # `_reconcile_the_roster` then had to choose between calling every
            # file "settled by rule" -- which would be false about their open
            # fields -- and leaving them out of the sum, which is the omission
            # the sum exists against.
            fact_pass_not_run[0] = NOT_RUN_NO_MODEL
            return
        if not site_has_a_destination(conn, routing, A_FACT,
                                      operation_mode=operation_mode):
            # BY DESTINATION, not by mode alone, and the cloud half is unchanged: a
            # cloud target still requires `hybrid`, which still requires this
            # folder's stored consent. What the mode-only test also refused was a
            # model on the person's OWN MACHINE, which `00`:189-193 permits under
            # every mode including `offline` -- "No content leaves the device;
            # only local rules and LOCAL MODELS may run". Nothing is released to a
            # local target that would not be released to a cloud one; the gate
            # makes that decision below, from the same `model_target`, and it is
            # `Gate.release` that reads the locality rather than this line.
            #
            # `104` §17.13 ruling 3 IS WHY THE READING MOVED. This line asked
            # `routing.locality_for(A_FACT) == CLOUD`, which on a two-target
            # routing is now True -- so a person with a key AND a local model, and
            # sending off, would have had the whole fact pass return here and every
            # file answered by nothing, where the same run used to answer every one
            # of them on their own machine. `site_has_a_destination` asks the three
            # questions the route asks and returns False only when there is
            # genuinely nowhere to send.
            fact_pass_not_run[0] = NOT_RUN_NO_DESTINATION
            return
        roster = corpus_roster(conn, run_id)
        if not roster:
            return
        if wire_handle_key is None:
            # A credential, not a convenience: `dossier._body` keys every
            # identifier that reaches a model under it and there is no un-keyed
            # fallback, because an un-keyed digest sitting beside the locator it
            # digests is reversible by whoever receives it.
            print(_wrapped(
                "No model was consulted about facts: this run has no wire handle "
                "key, and every identifier that reaches a model is digested under "
                "one. There is no un-keyed form to fall back to.", indent="  "),
                file=out)
            fact_pass_not_run[0] = NOT_RUN_NO_HANDLE_KEY
            return

        policy_version = set_policy(
            conn,
            Policy(policy_version=UNSET_POLICY_VERSION,
                   operation_mode=operation_mode,
                   # `104` §18.7: protected material reaches the local model.
                   consent_grants=standing_consent_grants(run_id),
                   redaction_settings={}, automatic_move_permissions={},
                   plan_version=PLAN_VERSION, set_at=clock),
            component_version=COMPONENT_VERSION, user_id=user_id,
            reason=f"{operation_mode} run: fact extraction, before grouping")

        outcomes: list[tuple[str, object]] = []
        authorities = fact_call_authorities(
            conn, routing=routing, scan_run_id=run_id,
            corpus_file_count=len(roster), policy_version=policy_version,
            wire_handle_key=wire_handle_key, schema=schema,
            # THE FILE'S OWN LEVELS, not the situation's whole set. `104` §11.2
            # step 2: a level the group carries is not a question to ask each file,
            # and the fields split off above are the ones `00`:57 puts on the
            # syllabus anchor.
            folder_levels=file_level_fields, user_id=user_id,
            now=now,
            # THIS RUN'S MODE, read off the folder's own consent by
            # `operation_mode_for` and stated rather than inherited: it is what
            # decides whether the cloud is a destination at all, and the default
            # is the local-first floor.
            operation_mode=operation_mode,
            # `104` §18.7: the scanned folders, the same list `record_selection`
            # was handed, so a cloud release of a folder path is relative to one.
            corpus_roots=sources,
            # `105` §14.4. The school level, asked of the anchors and of nothing
            # else. Empty when this situation binds no such role, which is every
            # situation but coursework's today.
            anchor_levels=anchor_level_fields,
            # `104` R-08, off the release `rules` above already loaded rather than a
            # second read of the library. Direct indexing and not `.get`: every one
            # of the nineteen schemas a `--situation` can resolve to is in the
            # compiled manifest, so a miss is a release that does not match this
            # build and is worth the crash.
            deferred_readings=rules.schemas[schema].deferred_readings,
            # `104` R-14. `run` was handed this beside the routing it was handed,
            # so the mailbox the transport fills is the mailbox `run_call` reads.
            usage_recorder=usage_recorder,
            on_result=lambda file_id, result: outcomes.append((file_id, result)))
        # KEPT FOR THE OBSERVE SITES, which need the same gate, budget, costs,
        # policy version and handle key. Stashed rather than rebuilt: a second
        # `Gate` beside this one would be a second answer to "what may leave this
        # device", and the two would drift on the next ruling. Every early return
        # above leaves the cell empty, which is what stops B being asked on a run
        # where A was not.
        fact_authorities[:] = [authorities]
        resolver = model_fact_resolver(conn, authorities=authorities)
        # `104` R-37. One resolver PER SETTLED BRANCH, each asking that branch's
        # situation's own questions: its schema's allowlist, its folder levels
        # less the group-level ones, its schema's authored readings. Built by
        # `replace` over the default branch's authorities so the gate, the
        # budget, the key, the client and the counting sink are the SAME objects
        # -- a second gate would be a second answer to what may leave this
        # device. With one branch this map holds the default resolver and the
        # loop below is the loop it was.
        partition = partition_cell[0] if partition_cell else None
        resolvers: dict[str, FactResolver] = {}
        if partition is not None:
            for branch in partition.branches:
                if branch.is_default:
                    resolvers[branch.label] = resolver
                    continue
                if not branch.settled:
                    continue
                levels = folder_levels_for(catalogue, branch.situation)
                group_levels = group_level_fields_for(catalogue, branch.situation)
                resolvers[branch.label] = model_fact_resolver(
                    conn, authorities=dataclasses.replace(
                        authorities,
                        activation_signals=ActivationSignals(signals=(
                            ActivationSignal(schema_id=branch.schema,
                                             activates=lambda facts: True),)),
                        folder_levels=tuple(
                            level for level in levels
                            if level.field not in group_levels),
                        deferred_readings=rules.schemas[
                            branch.schema].deferred_readings))
        # THE FILE IDS AND NOT JUST HOW MANY, since `104` §18.2 gap 10. A count
        # cannot be reconciled: two buckets of four and five over nine files could
        # both have missed the same file and double-counted another, and the
        # arithmetic would still look right. `ProgressEntry.file_ids` carries the
        # same argument in the same words, and this is the same rule one pass
        # earlier. `_print_fact_pass` is still handed counts -- it prints counts --
        # and takes them off `len` here rather than keeping a second tally.
        not_asked: dict[str, list[str]] = {}

        # `104` §17.1 AND §17.9: EACH FILE'S OWN SITUATION, ASKED BEFORE THE
        # FIELDS. This runs first because its answer is what decides the fact
        # call's questions -- the schema chooses the allowlist, the folder levels
        # and the readings, and all three are fixed when a resolver is built. A
        # situation named afterwards would be a situation nothing acts on.
        #
        # A file this pass does not name keeps the run's own `--situation`,
        # exactly as before it existed. That is the whole of the fallback and it
        # is deliberate: `--situation` is the person's own answer for the corpus
        # and the model's is a per-file refinement of it, never a replacement for
        # the thing they typed.
        situation_prompt_in_force = prompt_for(G_SITUATION_SENSITIVITY)
        situation_pass = (
            ask_the_situation(
                conn, roster=roster,
                # THE SEMANTIC-COMPOSED RECOGNISER, which is what the run
                # classifies with. `_semantic_classifier` hands the term detector
                # straight back when no weights are named, so this is the term
                # detector on a run without `--semantic-model` and the composed one
                # with it -- and the composed one is what raises a candidate for
                # the 60 `no_evidence` files that have no lexical one.
                explain=classify_producer.explain,
                # THE TERM DETECTOR'S OWN, and deliberately not the composed
                # recogniser's (`104` §18 gap 24). The precaution is
                # `Detector._precaution` and nothing else writes it:
                # `SemanticRecogniser.__call__` runs the term detector FIRST and
                # returns its record untouched, and the similarity path is
                # forbidden to protect or release one of `00`'s four domains at
                # all. So the hold has one author, and this is that author --
                # asking the composed object would be asking a wrapper about a
                # decision it is not allowed to make.
                precaution_of=detector.precaution_report,
                fact_authorities=authorities, routing=routing,
                prompt=situation_prompt_in_force, now=now, user_id=user_id)
            # LOCAL ONLY, and the check is `observe_locality_permits` rather than a
            # word of this function's own: `104` §17.1's ruling is that nothing
            # leaves the device under it, and the site's row is `ratified_local`.
            # A cloud target would also be refused at the door for every
            # unclassified file, which is the whole population this site asks
            # about -- so a run that got past this line would pay for a call per
            # file to be denied per file.
            # `104` §17.13 ruling 3: THE SITE'S DESTINATION, not the cloud half's
            # locality. `locality_for(G)` on a two-target routing answers CLOUD,
            # which this guard would read as "G may not run" and turn the pass off
            # in exactly the deployment the ruling is for -- while `target_for`
            # inside the pass was already keeping every file on this device.
            if site_has_a_destination(conn, routing, G_SITUATION_SENSITIVITY,
                                      operation_mode=operation_mode)
            else _NOTHING_ASKED)
        situation_cell[:] = [situation_pass]
        # `104` §18.2 gap 9: THE CELL NOW HAS A READER. It was written here and
        # read by nothing, so site G's whole account of the roster -- including
        # the protected count `no_route` holds -- reached nobody. Printed HERE,
        # immediately after the pass and before the fact pass's own block, because
        # that is the order the two ran in and because the situation a file is
        # asked under is chosen before its fields are asked: a person reading down
        # the screen reads the decisions in the order the run made them.
        _print_situation_pass(situation_pass, files=len(roster),
                              model_id=_local_model_id(
                                  routing, G_SITUATION_SENSITIVITY),
                              out=out)
        # ONE RESOLVER PER SCHEMA A MODEL NAMED, on `104` R-37's own pattern one
        # row up. Built by `replace` over the default authorities so the gate, the
        # budget, the key, the client and the counting sink are the SAME objects:
        # a second gate would be a second answer to what may leave this device.
        by_schema: dict[str, FactResolver] = {}
        for answered in sorted(set(situation_pass.named.values())):
            if answered == schema:
                # The run's own situation, named again. Nothing to build: the
                # default resolver already asks exactly these questions, and a
                # second one would be a second object for one set of answers.
                continue
            situations = _situations_of(answered)
            if not situations:
                # A schema no shipped situation resolves to has no folder levels
                # and no readings, so there is nothing for a fact call under it to
                # be asked FROM. The file keeps the run's questions rather than
                # being asked an empty set -- which is `require_folder_levels`'
                # refusal reached from three modules away.
                continue
            levels = folder_levels_for(catalogue, situations[0])
            group_levels = group_level_fields_for(catalogue, situations[0])
            by_schema[answered] = model_fact_resolver(
                conn, authorities=dataclasses.replace(
                    authorities,
                    activation_signals=ActivationSignals(signals=(
                        ActivationSignal(schema_id=answered,
                                         activates=lambda facts: True),)),
                    folder_levels=tuple(
                        level for level in levels
                        if level.field not in group_levels),
                    deferred_readings=rules.schemas[answered].deferred_readings))

        def resolver_for(file_id: str) -> FactResolver | None:
            # THE FILE'S OWN SITUATION FIRST, and it outranks the branch. A branch
            # is a folder of this corpus and its situation is the person's answer
            # for a whole folder; a site G verdict is a model's answer about THIS
            # FILE, cited and validated, and `104` §17.9's defect is precisely a
            # folder-wide answer being applied to a file it is wrong about.
            own = by_schema.get(situation_pass.named.get(file_id, ""))
            if own is not None:
                return own
            if partition is None or partition.single:
                return resolver
            branch = partition.branch_of(file_id)
            if branch is None:
                # `104` R-140: only a file TWO branches reach is here; a file
                # none reaches is under the default branch and asked its
                # questions.
                not_asked.setdefault(NOT_ASKED_AMBIGUOUS, []).append(file_id)
                return None
            chosen = resolvers.get(branch.label)
            if chosen is None:
                not_asked.setdefault(NOT_ASKED_UNSETTLED, []).append(file_id)
            return chosen

        written: list[str] = []
        # WHY EACH FILE WAS WITHHELD, not just how many. The route bars for two
        # different reasons and `PRIVACY_BAR` is one word for both, so the screen
        # said "nothing has classified them" about a file that IS classified and
        # was withheld for being protected. `104` R-02 widened the route to bar
        # unclassified files on a cloud target as well, which puts a third
        # sentence behind the same word. The store is asked here, where the file
        # ids still are, and `_print_fact_pass` prints what it is told.
        store = ClassificationStore(conn)
        withheld: dict[str, list[str]] = {}
        #: `104` §18.2 gap 10: THE FILES THIS PASS WALKED AND NEITHER BARRED NOR
        #: ASKED ABOUT. The deterministic producers had left nothing pending for
        #: them, which is `ask_the_situation`'s `settled` one site over and
        #: `00`:110's own rule -- "The LLM should not be called for direct, unique
        #: matches". Until this gap they were the invisible majority of a run: no
        #: line in the fact block, no line anywhere.
        settled_by_rule: list[str] = []
        deferred_by_budget: list[str] = []
        for file_id, content_hash in roster:
            asking = resolver_for(file_id)
            if asking is None:
                continue
            result = asking.resolve(
                conn, file_id=file_id, content_hash=content_hash)
            written.extend(result.fact_ids)
            # `104` §18.2 GAP 4: THE FILE THE STAGE DECLINED TO ASK ABOUT, COUNTED
            # UNDER ITS OWN REASON. Before this the stage returned `()` at four
            # points, the resolver recorded `llm` as having RUN, and the file left no
            # trace anywhere on this screen -- so a person read the pass as a model
            # having considered their file and found nothing worth saying. Counted
            # here, where the file ids still are, on the same pattern as the withheld
            # counts below (ids, so gap 10's sum can name the files): the loop
            # tallies and `_print_fact_pass` prints what it is told. A declined
            # file is not "settled by rule" either -- nothing settled its fields.
            declined = result.stages_not_asked.get(LLM_ROUTE)
            if declined is not None:
                not_asked.setdefault(declined, []).append(file_id)
                continue
            barred = result.stages_barred.get(LLM_ROUTE)
            if barred == BUDGET_BAR:
                # A CEILING, NOT A REFUSAL, and `facts/resolver.py` keeps the two
                # apart for the reason `00`:257 gives: a file that may never reach
                # a model is not a file waiting for budget to free up, and
                # reporting one as the other "would promise work that will never
                # be done". The same separation has to survive into the sum.
                deferred_by_budget.append(file_id)
                continue
            if barred != PRIVACY_BAR:
                settled_by_rule.append(file_id)
                continue
            row = get_file(conn, file_id)
            record = (store.current(file_id, row["content_hash"])
                      if row is not None else None)
            cause = (WITHHELD_UNCLASSIFIED if record is None
                     else WITHHELD_PROTECTED if record.protected
                     else WITHHELD_PRIVACY)
            withheld.setdefault(cause, []).append(file_id)
        _print_fact_pass(
            written=len(written),
            withheld={cause: len(ids) for cause, ids in withheld.items()},
            files=len(roster), outcomes=outcomes,
            # BOTH NAMES WHEN BOTH ANSWERED (`104` §17.13 ruling 3). `model_id_for`
            # describes the cloud half, and on a two-target run it would tell a
            # person one model was sent their files when the file they most care
            # about -- the one nothing has classified -- went to the other.
            model_id=_fact_pass_models(routing), out=out,
            not_asked={reason: len(ids) for reason, ids in not_asked.items()},
            # `104` §18.2 gap 5: WHAT THE DOSSIER CEILING CUT, READ BACK FROM THE
            # RECORDS. The dossier ids are this pass's own -- every outcome
            # `on_result` collected carries the address of the call it is about, and
            # a pre-call abstention carries `pre_call_address`, which is an address
            # of exactly this shape -- so the reports summed here are the reports of
            # the calls this pass made and no earlier run's. A counter incremented
            # in the loop above would be a second measurement of the same event and
            # would part company with the stored one the first time a refusal left
            # the loop early.
            cut=_dossier_cut(conn, outcomes))
        # `104` §18.2 gap 3. DIRECTLY UNDER THE COUNTS, because a proposal is what
        # some of those written facts ARE and a person reading "12 written" is owed
        # the ones that are questions rather than conclusions. Read from the
        # database and not from `outcomes`: a `P8Verdict` carries no field and no
        # value (`llm_harness.records.P8Verdict`), so the only place the pair the
        # person must judge exists is the row the pass just wrote.
        _print_values_to_confirm(conn, out)
        # `104` §18.2 gap 10. WHAT THE PASS SAW, HANDED OUT WHOLE. The
        # reconciliation runs whether or not this function reached this line, so
        # it cannot be written here; what it can be given is every verdict this
        # pass reached, per file, and it fills in the rest of the roster itself.
        fact_pass_verdicts.update(
            {file_id: (COVERAGE_NOT_ASKED, reason)
             for reason, ids in not_asked.items() for file_id in ids})
        fact_pass_verdicts.update(
            {file_id: (COVERAGE_NOT_ASKED, cause)
             for cause, ids in withheld.items()
             if cause != WITHHELD_PROTECTED for file_id in ids})
        # PROTECTED IS ITS OWN BUCKET AND NOT A KIND OF "NOT ASKED". The standing
        # rule is that protected material is marked and counted, never silently
        # omitted, and folding it under a reason among reasons is the soft form of
        # omitting it -- a person scanning the sum would have to read a cause line
        # to find out that any of their files are protected at all.
        fact_pass_verdicts.update(
            {file_id: (WITHHELD_PROTECTED, None)
             for file_id in withheld.get(WITHHELD_PROTECTED, ())})
        fact_pass_verdicts.update(
            {file_id: (DEFERRED, BUDGET_DEFERRED)
             for file_id in deferred_by_budget})
        fact_pass_verdicts.update(
            {file_id: (COVERAGE_SETTLED, None) for file_id in settled_by_rule})
        # LAST, so a response OVERRIDES the walk's own guess. A file the loop put
        # in `settled_by_rule` is a file whose LLM stage was not barred, and the
        # stage running is not the same event as a model answering -- `104` R-03
        # is that distinction costing a wrong number on this very screen.
        # `_sent_and_abstained` already rules what counts as a response and is
        # reused rather than re-derived, so the sum and the "from N files sent"
        # line two paragraphs above cannot come to disagree.
        fact_pass_verdicts.update(_verdicts_from_outcomes(outcomes))

    def _anchor_statement_pass(run_id: str) -> None:
        """`104` R-135: where in this corpus does a document STATE a course's name?

        **A corpus producer, for `_family_pass`'s reason in a different field.** The
        sentence "this is what W3134 is called" is printed on ONE document -- the
        syllabus -- and is about every other file of that course. A `FactResolver` stage
        is asked about one file version at a time and can never see it, which is why 19
        of the owner's 43 labelled course codes were missing outright and 19 more were
        the title recorded where the code belonged.

        **It decides nothing.** It records WHERE a line printed a course code, as a
        citation. Whether the words on that line and the words on some other file mean
        one course is site C's own question -- "two spellings can be one thing ... yours
        to judge from the evidence" -- and the constitution puts that judgement with the
        model. What was missing was the evidence, not the ruling.

        **And it once decided one thing, which is why it now decides none.** It required
        an anchor word beside the code, and on this corpus that refused all 106 readings
        that pass `is_code`, so the table held zero rows and no dossier ever carried
        context. See `COURSE_ANCHOR_TERMS`' former place above for the count. Every line
        of a document's own text that prints a code is a statement now, and the release
        cap on the call bounds how many of them reach one model.

        HERE, before `_model_fact_pass`, because a statement that arrives after the
        model has been asked is a statement nothing could be judged against.
        """
        roster = corpus_roster(conn, run_id)
        if not roster:
            return
        record_anchor_statements(
            conn, scan_run_id=run_id, file_versions=roster,
            # TWO KNOBS AND ONLY THE ASSERTING ONE DECIDES. `_SUBJECT_IDENTIFIER`'s own
            # comment fixes the separation: "what the product SEES and what it ASSERTS
            # are two knobs". `_STRUCTURED` is what it sees; the rule's pattern is what
            # it asserts, and only that may say a reading is a course. Without the
            # split, `General Chemistry I 1403` and `Spring 2026` both become courses --
            # the two readings the rule's own lookaheads exist to refuse.
            is_code=lambda text: SUBJECT_RULE.pattern.search(text) is not None,
            canonical=SUBJECT_RULE.canonical,
            # A SPAN INSIDE THE DOCUMENT'S OWN WORDS. `filename`, `path`, `title` and
            # every `metadata:*` zone sit outside this predicate by construction, so a
            # folder named after a course can never become the evidence for what that
            # course is called.
            reads_in_document=reads_a_structured_string)

    def _family_pass(run_id: str) -> None:
        """§3.11's two family fields, over the whole corpus at once.

        **A corpus producer, which is why it is not a `FactResolver` stage.** Every
        stage that resolver runs is asked about ONE file version; a duplicate family
        is a statement about a SET, and neither of these two can be computed from a
        file on its own. So it runs here, once, over `corpus_roster` -- the same
        roster `_model_fact_pass` uses, which is P3's stat-cache order and includes
        the unchanged files an extraction loop skips. A duplicate family assembled
        from only the re-extracted files would break up on the second run of an
        unchanged folder.

        HERE, and before `_model_fact_pass` and P9: a fact that arrives after
        grouping is a fact no group could form on, and `grouping.seeds` reads
        `family_facts` into its anchor rows deliberately.

        **THE COST IS LINEAR IN THE ROSTER, and that is a requirement rather than a
        happy accident.** `duplicate_family`'s exact half groups the roster into a
        dict keyed on `content_hash` and only looks inside a bucket holding two or
        more files, so a corpus of unique files compares nothing. Its near half
        enumerates pairs, but of PERCEPTUAL-HASH CARRIERS and never of the roster --
        and `readers.image_headers`, the wired reader, supplies no perceptual hash,
        so that set is empty (measured: 0 carriers on both real corpora) and
        `_near_families` returns before the loop.

        **`version_family` IS NOT CALLED, and that is the same refusal one step
        further out.** §2.9 lists "duplicate and version-family signals" among what
        extraction produces and defines none of them, so there is no lineage rule to
        bind -- see `planning/97-VERSION-LINEAGE-PROPOSAL.md`. Binding it to a rule
        that answers `None` would have been honest about the FACTS and dishonest
        about the COST: `version_family` compares every pair of file versions,
        because a version family is by definition files whose content hashes DIFFER
        and no hash bucket can group them. On 10,000 files that is 50 million pairs
        enumerated to answer "no rule" 50 million times. A producer whose rule can
        establish nothing is not a producer this run has; calling it would buy a
        quadratic and no fact. When a lineage rule is ruled, it arrives here with
        the call, and whoever authors it owns the blocking strategy that keeps the
        comparison bounded.

        `near_match` answers False always, for the same reason one field over: §2.6
        names the perceptual hash and states no distance metric and no threshold, and
        equality would be a threshold of zero. See
        `planning/98-NEAR-DUPLICATE-METRIC-PROPOSAL.md`. Byte identity needs no
        threshold and is unaffected -- measured on a real 42-file corpus, 15 files in
        7 families.

        `perceptual_hash_label` is IMPORTED from `extractors.image` and never
        respelled. It has a space in it, P5 owns the spelling, and a second home for
        one string is the defect this repo has paid for most often.
        """
        roster = corpus_roster(conn, run_id)
        if not roster:
            return
        duplicate_family(conn,
                         file_ids=tuple(file_id for file_id, _hash in roster),
                         perceptual_hash_label=PERCEPTUAL_HASH_FIELD,
                         near_match=lambda left, right: False)

    #: P6's two field keys onto P9's two verdicts. THE ONLY PLACE either vocabulary
    #: may be spelled beside the other, which is why the mapping is here and not in
    #: `facts.families`: P6 answers with its own key and never learns P9's word.
    P9_VERDICT_BY_FAMILY_FIELD = {DUPLICATE_FAMILY_FIELD: DUPLICATE,
                                  VERSION_FAMILY_FIELD: VERSION_FAMILY}

    def _duplicate_or_version(seed_file_id: str, neighbour_file_id: str):
        """P9's sixth channel names an edge it cannot type. This types it.

        **Compulsory the moment `_family_pass` is bound, not optional.**
        `grouping.retrieval` opens the `duplicate-or-version-link` channel off
        `family_facts`, which covers BOTH fields, and `grouping.graph._edge_type`
        raises `ConfigurationRequired` without an authority rather than guessing:
        "the wrong answer puts two revisions of one document into a group as two
        documents." Verified by running the product -- with the families written and
        this left at `None`, a corpus holding one duplicate pair stops the run.

        `None` is returned rather than raised, and deliberately. The channel only
        opens on a shared family VALUE, so a pair reaching here with no shared field
        is a contract failure and not a close call -- and P9 already has the right
        sentence for it, naming both legal answers. Inventing a second error here
        would be a worse copy of one that is already written.
        """
        return P9_VERDICT_BY_FAMILY_FIELD.get(shared_family_field(
            conn, left_file_id=seed_file_id, right_file_id=neighbour_file_id))

    scan_run_id = [""]
    accepted_ids: list[str] = []

    #: §4.4's semantic channel, built once for the run. `00`:56 is why it exists:
    #: "Embeddings are useful at this stage because they can find files such as
    #: HW 3.pdf that lack the course code but resemble lecture notes and earlier
    #: problem sets." Measured on the owner's corpus, 35 of the 43 files whose
    #: label carries a course name no course anywhere in their own bytes, and the
    #: model answered `unknown` about them -- correctly, because the evidence is in
    #: their neighbours and nothing was retrieving those.
    #:
    #: The eligible set is the SCAN's own roster, WHOLE. A vector is computed for
    #: a file this run included and for no other, and that roster is the bound:
    #: the corpus the person asked to organise.
    #:
    #: IT USED TO BE `[:cap]` (`104` R-59's second finding), and `cap` is P9's
    #: `max_graph_nodes`, which is 10. So every seed in the owner's 199 files was
    #: compared against the same nine versions -- the ones that sort first by
    #: content hash -- and `00`:56's own example could only have worked if the
    #: lecture notes happened to be among them. The slice also threw away the
    #: `seed` argument the signature offers, which is what made the same nine
    #: right for every file at once. `_bounded_versions` says why the cut belonged
    #: after the similarity rather than before it; `ensure_file_embedding` is
    #: idempotent per version, so the run pays for each file once whatever the
    #: seed count.
    _embeddings, _retrieval_knowledge = _embedding_runtime(
        semantic_model,
        versions_for=lambda db, cap: tuple(
            FileVersionRef(file_id=file_id, content_hash=content_hash)
            for file_id, content_hash in corpus_roster(db, scan_run_id[0])))

    def downstream(p1_p7) -> CorpusAuthorities:
        scan_run_id[0] = p1_p7.scan_run_id
        # §3.11's universal families, BEFORE the model pass and before P9 groups.
        # See `_family_pass` for why a corpus producer cannot be a resolver stage.
        _family_pass(p1_p7.scan_run_id)
        # `104` R-135. BEFORE the model pass: a statement that arrives after the model
        # has been asked is a statement nothing could be judged against.
        _anchor_statement_pass(p1_p7.scan_run_id)
        # `104` R-37. The branches, once every deterministic fact exists and
        # before a model is asked anything: the fact pass asks per branch.
        partition_cell[:] = [_partition_branches(p1_p7.scan_run_id)]
        # §8.6's THIRD producer, and the only point in the run where it can stand.
        # See `model_fact_resolver` for why it is a second pass and not the `llm`
        # stage of the pass P1-P7 already ran. BEFORE the three blocks below on
        # purpose: they report what the scan found, and a fact this pass writes is
        # part of what the scan found.
        _model_fact_pass(p1_p7.scan_run_id)
        # `104` §18.2 gap 10, AND IT IS OUTSIDE THE PASS ON PURPOSE. The pass has
        # four early returns and every one of them is an ordinary way for a run to
        # go -- no model, no destination this mode permits, an empty roster, no
        # wire handle key -- so a sum written at the end of the pass would be
        # missing on precisely the runs where a person is most likely to wonder
        # what happened to their files. Here it runs on every run, immediately
        # after the pass and before anything else prints, which is where the two
        # blocks it reconciles already are.
        _reconcile_the_roster(
            conn, run_id=p1_p7.scan_run_id, verdicts=fact_pass_verdicts,
            not_run=fact_pass_not_run[0], out=out)
        # AFTER the fact pass, because that is what builds the authorities these
        # borrow, and BEFORE P9 groups, because that is what asks site B.
        observe_b = (observe_group_authorities(
            fact_authorities[0], routing=routing, situation=situation,
            placeable_file_count=placeable_file_count(
                conn, p1_p7.scan_run_id))
            if fact_authorities else (None, None))
        # HERE, and not in `report`. The scan has finished and every design stage
        # after this point can refuse by name -- and `main` reaches `report` only
        # when none of them does. Printed at the end, the count of what was marked
        # and left unopened was dropped from every refused run: the verdict sat in
        # `exclusion_verdicts` and the person was told nothing. "Marked, counted,
        # never silently omitted" has no success-path exception, so it is said as
        # soon as it is known.
        _print_protected(
            protected_areas(conn, scan_run_id=p1_p7.scan_run_id),
            protected_files=_protected_file_count(conn, p1_p7.scan_run_id),
            locked=locked_containers(
                conn, p1_p7.scan_run_id,
                file_names(conn, directory, *also_read)),
            out=out)
        # HERE for the reason above it, one rule further out. Every argument that
        # comment makes for the protected block is an argument for §1.1's other
        # three rules: the verdict is in `exclusion_verdicts` by now, a stage
        # after this may refuse, and a refused run that never said what it had
        # skipped is the silent omission the standing rule forbids.
        _print_set_aside(
            scan_run_summary(conn, p1_p7.scan_run_id),
            set_aside_paths(conn, scan_run_id=p1_p7.scan_run_id), out)
        # HERE for the same reason as the two above: the landscape is known as
        # soon as the walk is, and a stage after this may refuse. A person who
        # named a root and then hit a refusal was told nothing about the one
        # answer of the three that has no other way to show itself.
        _print_candidate_roots(
            candidate_roots,
            existing_folders(conn, scan_run_id=p1_p7.scan_run_id), out)
        return CorpusAuthorities(


# NOTE for A2: `Mapping` is already imported in cli.py (`from typing import ...`
# / `collections.abc`) — confirmed in use at `sends: Mapping[str, str]` on `run`.
# If the annotation is inconvenient, dropping it to a bare `summary` parameter
# changes nothing.
            catalogue=catalogue, design_authorities=design_authorities,
            grouping_limits=GROUPING_LIMITS,
            grouping_knowledge=GroupingKnowledge(
                # §4.4's retrieval channels. Both halves come from
                # `_embedding_runtime` so they cannot disagree: a run either stores
                # vectors AND knows how to compare them, or does neither. Without
                # `--semantic-model` this is the same all-`None` shape it always
                # was, and retrieval is by shared validated fact alone -- the
                # deterministic path P9 is explicit is a complete path.
                retrieval=_retrieval_knowledge,
                # `active_schema_for` STOOD HERE AND IS GONE (`104` R-09). The
                # comment it carried argued, correctly, that a field missing from
                # the tuple "is a field P9 will not group on" -- and the tuple had
                # by then lost `school` and `subject` to `fd68cb6`, which emptied
                # `DIRECT_SLOTS` and left the literal evaluating to
                # `('term', 'media_type', 'work_type')`. Those two are exactly where
                # `104` R-10's 22 model-written facts landed.
                #
                # Both halves of that argument were false, and only a run says so.
                # P9 read the slot NOWHERE: `assemble_group_dossier` checked it
                # callable and never called it. Handing in a callable that raises on
                # any call leaves 57 of 57 P9 tests passing. What decides whether a
                # fact may anchor a group is `grouping.seeds.ANCHOR_STATES` --
                # `{direct, validated}` -- which is field-independent, so no
                # derivation from `role_bindings` could have changed a single
                # grouping outcome. Deriving it would have replaced a wrong dead
                # value with a right dead one; wiring it into the seed path to give
                # it a purpose would have widened the anchor bar behind a schema
                # fix, and `00`:42 keeps a model conclusion out of a folder proposal
                # deliberately. `tests/integration/test_p9_active_schema_slot_
                # retired.py` carries both measurements.
                signal_evaluator_for=lambda domain: True,
                classification_store=ClassificationStore(conn).current,
                conflicts_for=lambda file_ids: (),
                duplicate_or_version=_duplicate_or_version,
                # `104` §11.2 step 2, the other end of the split made at the top
                # of `run`. Site A is no longer asked these; the group's anchors
                # carry them into B's dossier, and P10 reads a level's value off
                # the group. THE SAME SET at both ends, computed once from the
                # person's own situation, so "not asked per file" and "carried by
                # the group" cannot come to mean two different field sets.
                group_level_fields=group_level_fields),
            user_seed_for=lambda file_id, content_hash: None,
            # `104` §7 Phase 1 step 6: site B runs and applies nothing. Both are
            # `None` when no model was configured, when B's tier is not on this
            # device, or when the fact pass did not run -- and a `None` pair is
            # the deterministic run P9 has always made.
            embeddings=_embeddings,
            p8_run_call=observe_b[0], p8_authorities=observe_b[1],
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

    # Wrapped only when a recording was asked for. A `RecordingCorpusSource`
    # keeps every listing the scan was served, and those listings ARE §8.5's
    # frozen corpus snapshot -- what a pruned directory never listed stays
    # unlisted, which is what reproduces the pruning on replay rather than
    # replaying it as a conclusion. They cannot be recovered after the scan, so
    # the decision has to be made before it starts.
    recording = (RecordingCorpusSource(FilesystemCorpusSource())
                 if record is not None else None)
    result = run_production_corpus(
        conn, selection_id, authorities=p1_p7_authorities(
            now=now, detector=classify_producer, operation_mode=operation_mode,
            source=recording,
            # THE ONE CONDITION, and it is the same one that decides `recording`
            # two lines up: §8.5's envelope is built when the person asked to keep
            # this run. `record_bundle` below reads `result.p1_p7.bundle_id`, so
            # the bundle has to exist by the time it is called and cannot be
            # assembled afterwards -- a sealed bundle is immutable by trigger.
            bundle_content=record is not None),
        downstream=downstream,
        decisions=CorpusDecisions(
            plan_version_id=PLAN_VERSION, accept_groups=accept_and_remember,
            design=design_decisions, approve_plan=approve_plan,
            set_privacy_policy=set_privacy_policy))
    if record is not None:
        # AFTER P11, and that is the whole reason a SECOND bundle exists.
        # `run_p1_p7` sealed the first at the end of P1--P7 and a sealed bundle is
        # immutable by trigger, so the accepted groups -- the user's decision,
        # which has only just been made -- and the corpus snapshot have no lawful
        # moment to be written into it. `record_bundle` opens one that SUPERSEDES
        # it and carries the first's contents plus those three things.
        plan_version = result.tree.tree.plan_version_id
        recorded = record_bundle(
            conn, from_bundle_id=result.p1_p7.bundle_id, name=record,
            snapshot=snapshot_from(conn, recording, selection_id=selection_id,
                                   corpus_form=CORPUS_FORM_SNAPSHOT),
            # P9's own per-version projection, asked for rather than derived: P2
            # "does not re-derive acceptance from membership records".
            accepted=tuple(
                {"group_id": group_id, "plan_version_id": plan_version,
                 "acceptance": group_state_as_of(
                     conn, group_id=group_id, plan_version_id=plan_version)}
                for group_id in dict.fromkeys(accepted_ids)),
        )
        conn.commit()
        # Recorded here and ANNOUNCED at the end of `main`, after the report.
        # The recording is done at this point so that a later refusal in
        # `--send-set` cannot lose it, but the notice is the last thing a person
        # should read -- it ends in a command to type, and a command printed
        # above forty lines of report is a command nobody sees.

    # AFTER the run, because §7.5's sets do not exist until §6 has finished trying,
    # and IN the same run, because a residual set answer belongs to the plan
    # version it was given in (P11 SPEC, "Plan versioning") and this run has just
    # minted a new one. So `--send-set` is applied to the sets it was typed at and
    # is not remembered between runs: the run that files the files is the run the
    # person named them in.
    if sends:
        try:
            result = dataclasses.replace(result, placement=act_on_residual_sets(
                conn, result=result.placement,
                inputs=placement_inputs(result.tree), sends=sends,
                evidence_for=evidence_for, component_version=COMPONENT_VERSION,
                observed_at=now(), user_id=user_id))
        except ResidualSendRefused as refusal:
            # REFUSED, AND THE PLAN SURVIVES. Refusing is right -- a renumbered
            # set holds different files, and filing them would be the gesture
            # acting on something other than what the person named. Letting the
            # refusal end the run was not: `result` is already the whole run,
            # and discarding it left a person who re-typed yesterday's command
            # with no plan at all. Review sets are named by POSITION in a
            # chunking, so deleting a file anywhere renumbers them and a name
            # that was correct yesterday names nothing today -- which is what
            # makes shell history a hazard for this command.
            #
            # Nothing was written on this path: `act_on_residual_sets` resolves
            # every pair before recording any, precisely so that a refusal
            # cannot half happen. So `result` is exactly the run that would
            # have been reported had the flag not been typed at all.
            #
            # THE `--residual` SENTENCE IS KEPT, AND MADE TRUE. It was in
            # `main`, printed for EVERY `ResidualSendRefused` -- and the
            # exception has three raise sites: an unknown SET, an unenabled
            # AREA, and an ambiguous one. Only the second is about enabling an
            # area, so a person who mistyped a SET name was told to add a
            # `--residual` flag that was already in the command they had just
            # typed. Measured, not reasoned.
            #
            # The test is NOT "which raise site fired". P11 does not publish
            # that, and inferring it from the prose of a message is how a
            # second home for one rule gets built. It is a fact this command
            # owns outright: DID THIS COMMAND ENABLE THE AREA IT IS SENDING TO?
            # `residuals` is what `--residual` validated and `sends` is what
            # `--send-set` parsed, so the answer is already here and needs
            # nothing from P11. It gets all three sites right -- an unknown set
            # whose area IS enabled says nothing about `--residual`; an
            # unenabled area says it; an ambiguous area is by definition
            # enabled, and enabling it again is not the answer. Only the areas
            # actually missing are named, where `main` named every area the
            # person had mentioned.
            unenabled = [area for area in dict.fromkeys(sends.values())
                         if area not in residuals]
            advice = (
                "\n  `--residual` enables an area for the run it is typed in, "
                "so it belongs in the same command as the `--send-set` that "
                "uses it: "
                + " ".join(f"--residual {shlex.quote(area)}"
                           for area in unenabled)) if unenabled else ""
            print(f"\nThat send was refused, and the plan below is unaffected:"
                  f"\n  {refusal}{advice}\n  Nothing was filed in bulk, and "
                  "the plan below is the run that was already computed.",
                  file=out)
    reaches = _raise_blocked_questions(conn, detector=detector, asked_at=clock)
    # `104` R-37's branch questions reach their branch's files, and the screen
    # prints the `--answer` lines beside those files for the same reason R-92
    # prints a reading's beside its files.
    reaches.update(branch_reaches)
    if questions_reach is not None:
        # `104` R-92's mailbox, filled the way `usage_recorder` is: the tie a
        # question was raised from is a fact about a file that no table holds
        # afterwards, and the report is in `main`. A caller that wants none
        # passes none and this run is exactly what it was.
        questions_reach.update(reaches)
    return result


def _raise_blocked_questions(conn: sqlite3.Connection, *, detector,
                             asked_at: str) -> dict[str, tuple[str, ...]]:
    """Record every question THIS corpus's own ambiguities raise (P15).

    Returns which files each question would settle, keyed by question id, because
    `104` R-92 needs it on the screen and this is the one place that knows: the
    tie a question is raised from is a fact about a file that no table holds
    afterwards. Read here and handed to `report` by `main`, the way every other
    fact the report prints arrives.

    Run AFTER the corpus, not before, because `66` §12 permits a question only
    when "a specific decision is blocked" -- and which decisions are blocked is
    not knowable until the run has tried. A question list assembled up front would
    be a questionnaire wearing a trigger's clothes.

    Recording is idempotent by question id, so a second run over the same folder
    re-derives the same questions from the same evidence and adds nothing: it is
    one question asked twice, not two.
    """
    # A PROTECTED FILE'S OWN WORDS ARE NOT A QUESTION. Measured on a passport: its
    # number, its date of birth and its expiry became `subject` values, and the date
    # of birth was printed on the terminal -- "What kind of material is JUN1998?" --
    # with an option that would have made it a folder dimension. §8.4 marks such a
    # file so it is NOT assembled for anything, and `00`:201 says a visible list of
    # protected specifics "may not be" safe to show.
    #
    # The classification is already settled here: `_raise_questions` runs after
    # P1-P7, so this needs no reordering of the pipeline and costs nothing. The tree
    # side was already covered -- `materialise_branch` isolates protected files -- but
    # isolation stops a value becoming a FOLDER; it does not stop it being read out.
    #
    # The fact itself is left standing. It is evidence-backed and §8.2 does not
    # delete; what changes is that nothing offers it to the person.
    subject_of: dict[str, str] = {}
    for row in conn.execute(
            'SELECT f.file_id, v.canonical_value FROM file_facts AS f '
            'JOIN "values" AS v ON v.value_id = f.value_id '
            "WHERE f.field_key = 'subject' AND f.active = 1 "
            "AND f.superseded_by IS NULL "
            "AND NOT EXISTS (SELECT 1 FROM classifications AS c "
            "                WHERE c.file_id = f.file_id AND c.protected = 1 "
            "                  AND c.superseded_by IS NULL)"):
        subject_of.setdefault(row[0], row[1])
    reaches: dict[str, tuple[str, ...]] = {}
    for question, files in tied_readings_and_the_files_they_reach(
            conn, explain=detector.explain,
            files=files_with_observations(conn), subject_of=subject_of):
        record_question(conn, question, asked_at=asked_at)
        reaches[question.question_id] = files
    return reaches


def _files_something_was_read_out_of(conn: sqlite3.Connection) -> set[str]:
    """Every file with an observation that did not come from the filesystem.

    ONE DEFINITION OF "READ", used by the two callers that both need it: the
    question this run asks a person about a folder, and R-24's report about a
    folder where the answer is every file. Written once because it is one rule --
    a second copy is a second rule the day either changes.
    """
    return {row[0] for row in conn.execute(
        "SELECT DISTINCT file_id FROM evidence "
        "WHERE superseded_by IS NULL AND source_type <> ?",
        (FILESYSTEM_SOURCE_TYPE,))}


def _nothing_could_be_read_report(
        conn: sqlite3.Connection, *, directory: Path,
        also_read: Sequence[Path], now) -> tuple[str, ...] | None:
    """R-24: the screen for a folder every extractor finished and none could read.

    Returns the lines, or `None` when this is not that case -- and the caller then
    prints the refusal it always printed. THE TEST IS THE EVIDENCE AND NOT THE
    EXCEPTION. `NothingToDesign` says a tree had no branch candidate, which is true
    of several corpora; what makes this one an answer rather than a failure is that
    there is nothing for the product to be wrong ABOUT. Every file was reached,
    every extractor ran, and the only observations anything holds are the ones the
    filesystem recorded -- the same rule `folders_nothing_could_be_read_from`
    applies one folder at a time, asked here of the whole scan.

    A PROTECTED FILE COUNTS AS UNREAD AND IS NAMED BY ITS COUNT, NOT BY ITS NAME.
    §8.4 marks them so nothing about them is assembled and `00`:201 keeps a list of
    protected specifics off a screen somebody else can see. So a folder of protected
    material reaches this path -- nothing was read out of it either -- and the
    person is told how many rather than which, which is the standing order: marked,
    counted, never opened, never silently omitted.

    §8.6'S LINE IS P13'S AND IS ASKED FOR RATHER THAN IMITATED. `progress_lines`
    was written, tested and never called from `src/`; its `assert_every_file_
    accounted` is the rule that "no indexed file may be absent from every entry",
    and a paragraph this file assembled itself would be that rule restated by the
    part it is meant to check. `WORST_FIRST` is the caller's choice under P13's own
    Open question 4, spelled here because the seam supplies none -- and
    `tests/p13/test_p13_progress_lines.py` says in a comment that it will be
    spelled "exactly as it will be spelled in `src/cli.py`".
    """
    scan = conn.execute(
        "SELECT scan_run_id FROM scan_runs ORDER BY started_at DESC, "
        "scan_run_id DESC LIMIT 1").fetchone()
    if scan is None:
        return None
    roster = corpus_roster(conn, scan[0])
    if not roster:
        return None
    readable = _files_something_was_read_out_of(conn)
    if any(file_id in readable for file_id, _hash in roster):
        return None

    #: NAMED FROM THE ROSTER AND NOT FROM THE FOLDER WALK, so the list cannot be
    #: shorter than the count above it. `folders_nothing_could_be_read_from`
    #: answers per folder, relative to ONE root, and drops a file outside it --
    #: correct where it is used, and here it would leave a `--also-read` folder's
    #: files counted and unnamed, which is the omission this whole screen is about.
    withheld = {row[0] for row in conn.execute(
        "SELECT DISTINCT file_id FROM classifications "
        "WHERE protected = 1 AND superseded_by IS NULL")}
    paths = dict(conn.execute("SELECT file_id, current_path FROM files"))
    named = sorted(
        _relative_to_any(paths[file_id], (directory, *also_read))
        for file_id, _hash in roster
        if file_id not in withheld and file_id in paths)
    held = sum(1 for file_id, _hash in roster if file_id in withheld)

    lines = [
        "",
        _wrapped(
            f"Nothing could be read out of anything in {directory}, so there is "
            "no folder to propose and nothing has moved.", indent=""),
        "",
        f"Every file is accounted for -- {len(roster)} "
        f"file{'' if len(roster) == 1 else 's'}:",
        *(f"    {name}" for name in named),
    ]
    if held:
        lines.append(
            f"    and {held} protected file(s), marked and counted, never opened "
            "and never named on a screen")
    lines += [
        "",
        _wrapped(
            "This is not a failure and nothing was skipped. Every extractor ran "
            "and finished; what they found was the name, the size and the dates "
            "the filesystem keeps, and no words inside the files. A scan with no "
            "text layer and a filename that is a counter is the ordinary case, "
            "and only you know what these are.", indent="  "),
    ]
    lines.extend(progress_lines(
        conn, scan_ref=scan[0], plan_version=PLAN_VERSION, rendered_at=now(),
        indexed_files=dict(roster), precedence=WORST_FIRST,
        awaiting_model_review=tuple, flagged_by_model_review=tuple,
        cause_for=_no_extractor_cause(conn)))
    return tuple(lines)


#: WHICH CEILING STOPPED A `capped` RUN, by the `source_type` that recorded it.
#: Three extractors write `capped` under three different ceilings and every one of
#: those numbers is chosen in THIS file, which is why the mapping lives here and
#: not in `review_run/progress.py`: P13 renders a cause and holds none.
#:
#: `text_document` is pdfium's, because `pdf.py` is the only extractor writing that
#: source type that caps. The long-tail families other than `spreadsheet` carry no
#: ceiling at all -- `readers/deployment.py` says why for the archive manifest and
#: the same holds for the rest -- so `spreadsheet` is the only one of the six here.
#: A source type absent from this mapping produces no sentence rather than a guess.
_CAPPED_BY_SOURCE_TYPE: Mapping[str, str] = MappingProxyType({
    "ocr": ("OCR stopped at this deployment's per-file ceiling of "
            f"{OCR_PAGE_CEILING} pages or {OCR_SECONDS_PER_FILE} seconds"),
    "text_document": ("PDF text extraction stopped at this deployment's ceiling "
                      f"of {PDF_PAGE_CEILING} pages per file"),
    "spreadsheet": ("a spreadsheet stopped at this deployment's ceiling of "
                    f"{SPREADSHEET_CELL_CEILING} cells per file"),
})


def _no_extractor_cause(conn: sqlite3.Connection):
    """P13's `cause_for`, answered where this run actually knows the answer.

    Its default sentence for a bucket with no recorded cause is "no ceiling is
    recorded as the cause, so this build cannot say which limit stopped it" -- true
    of a budget deferral and wrong here, where no limit stopped anything. These
    files stopped at the router: `extraction_routing` holds the reason and nothing
    was printing it.

    `None` for every other bucket, which returns P13's own sentence. A cause this
    function cannot support is not one it invents.
    """
    unrouted = conn.execute(
        "SELECT count(*) FROM extraction_routing WHERE extractor_name IS NULL"
    ).fetchone()[0]
    routed = conn.execute(
        "SELECT count(*) FROM extraction_routing WHERE extractor_name IS NOT NULL"
    ).fetchone()[0]

    def cause_for(label: str) -> str | None:
        if label == CAPPED:
            # §8.6 requires the cause NAMED rather than implied, and THREE
            # extractors write `capped` -- `ocr.py`, `pdf.py` and `long_tail.py` --
            # under three different ceilings. `review_surface.progress` buckets by
            # state, so one bucket holds all of them, and a sentence naming one
            # ceiling for the whole bucket would be a wrong cause printed with
            # confidence. That is worse than the gap it replaced: the gap was true.
            # So the run is asked which ceilings actually fired.
            fired = sorted(row[0] for row in conn.execute(
                "SELECT DISTINCT source_type FROM extraction_runs "
                "WHERE completeness = ?", (CAPPED,)))
            named = [_CAPPED_BY_SOURCE_TYPE[source] for source in fired
                     if source in _CAPPED_BY_SOURCE_TYPE]
            if not named:
                # A ceiling this file does not hold. P13's own sentence says the
                # cause is unrecorded, which is the truth here.
                return None
            return ("; ".join(named)
                    + " -- and what was read before stopping was kept")
        if label == DEFERRED:
            # A budget stopped this extractor BEFORE it started, so nothing about
            # it is a routing failure and the sentence below would misattribute it.
            # This build records no deferral -- `extractors/budgets.deferred_result`
            # has no caller -- and P13's own "no ceiling is recorded" is the honest
            # answer for one until something records which budget fired.
            return None
        if routed or not unrouted:
            return None
        return ("no reader in this deployment handles these files' format, so "
                "what the filesystem records about them is all there is")

    return cause_for


def _relative_to_any(path: str, roots: Sequence[Path]) -> str:
    """The shortest name that still says which of the scanned folders it is in.

    A path relative to the root the person typed, because `privacy.vocabulary.
    ALWAYS_LOCAL`'s first member is `paths` and an absolute one puts a home
    directory on a screen. A file under none of the roots cannot happen through a
    live scan and is named by its own filename rather than dropped.
    """
    for root in roots:
        try:
            return Path(path).relative_to(root).as_posix()
        except ValueError:
            continue
    return Path(path).name


def folders_nothing_could_be_read_from(
        conn: sqlite3.Connection, *,
        root: Path) -> tuple[tuple[str, tuple[str, ...], int], ...]:
    """THE POLICY: which files are worth a person's attention, and which are not.

    Returns `(folder, files nothing was read out of, protected among them)` per
    folder, the folder given relative to the scan root.

    **This is the whole of the rule, and it is a rule about the EVIDENCE and not
    about the outcome.** 73% of a real 199-file corpus goes unplaced. Asking about
    all of it would be worse than the silence it replaced, so "the run could not
    place it" is deliberately not the trigger. The trigger is narrower and it is
    the one case where a person is the only possible source: every extractor ran,
    and the only observations the file has are the ones the FILESYSTEM recorded
    ABOUT it -- its name, its size, its dates. Nothing was read OUT of it, so there
    is no reading for the product to be wrong about and nothing better it could do
    with more effort.

    Measured on `.groundtruth/corpus` against 215 hand-written labels: 24 files
    corpus-wide, 76% of which the labeller independently marked "the right answer
    is ask the person", against a base rate of 41%. Inside the one scored
    situation, three files and three of three. The labeller's own words for these
    are *"a scan or export with no text layer and a filename that is a scanner
    counter or a content hash. Nothing but the person knows what it is."*

    **WHAT WAS MEASURED AND REJECTED.** Every abstaining decision carries a ranked
    `alternatives` list and `requires_review: true`, which reads like a
    multiple-choice question with the options already computed. On the real corpus
    it is not one: all 181 abstentions score 0.2857 against a support threshold of
    0.5, and no file anywhere has two candidates above that threshold -- the
    distribution is 0.2857 or 0.7143 and nothing between. So `alternatives` is not
    a set of competing destinations; it is the person's own top-level folders
    (`Desktop/MONEY`, `Desktop/Vaccine records`) tied at a score none of them
    earned. Asking from it would have been 43% precise against a 41% base rate,
    across 62 files -- noise with a question mark on it.

    **THE TWO SCORES ABOVE ARE THE MEASUREMENT'S OWN AND ARE NOT RE-DERIVED.**
    They were read off a run under `cli-support-v1`, whose scale reserved two
    sevenths for channels nothing produced; under `cli-support-v2` the same two
    populations read 0.4 and 1.0 (`104` §18.2 gap 13). The measurement is left in
    the units it was taken in, because rewriting a number nobody re-ran would
    make a record of what was observed into a claim about what would be. What the
    finding turns on -- that the ties are the person's own top-level folders and
    not competing destinations -- is a fact about `alternatives`, not about the
    denominator, and gap 13 does not touch it. Re-measure before quoting either
    pair as current.

    **PROTECTED FILES ARE COUNTED AND NEVER RETURNED.** §8.4 marks them so nothing
    about them is assembled, and `00`:201 says a visible list of protected
    specifics may not be safe to show. A question is printed on a screen somebody
    else can see, so a protected file never becomes one -- and it is counted, because
    dropping it silently would make the question describe a folder smaller than the
    one the person is looking at. Marked, counted, never opened, never silently
    omitted, in that order.

    **The path is made relative HERE.** `privacy.vocabulary.ALWAYS_LOCAL`'s first
    member is `paths`, and a scope is stored, printed, and carried between runs, so
    an absolute one would put a person's home directory into a record that outlives
    the run. A file outside the scan root has no relative name and is skipped
    rather than named absolutely.
    """
    readable = _files_something_was_read_out_of(conn)
    protected = {row[0] for row in conn.execute(
        "SELECT DISTINCT file_id FROM classifications "
        "WHERE protected = 1 AND superseded_by IS NULL")}

    folders: dict[str, list[str]] = {}
    held: dict[str, int] = {}
    for file_id, current_path in conn.execute(
            "SELECT file_id, current_path FROM files"):
        if file_id in readable:
            continue
        try:
            folder = str(PurePosixPath(
                Path(current_path).relative_to(root).as_posix()).parent)
        except ValueError:
            continue
        if file_id in protected:
            held[folder] = held.get(folder, 0) + 1
            continue
        folders.setdefault(folder, []).append(file_id)
    return tuple((folder, tuple(sorted(folders[folder])), held.get(folder, 0))
                 for folder in sorted(folders))


def files_with_observations(
        conn: sqlite3.Connection) -> list[tuple[str, str]]:
    """Every `(file_id, content_hash)` that has at least one observation.

    **This was `SELECT DISTINCT file_id, content_hash FROM evidence`, and that one
    line was the largest single cost in a real run.** It reads 365,690 rows to
    produce 200 -- one per file -- because `DISTINCT` over two columns with no
    covering index means a full pass plus a temporary B-tree. Measured on a real
    200-file database: 2.34 seconds warm and committed. IN SITU it is far worse than
    that, and the difference is the reason it went unnoticed for so long: the whole
    of P1--P7 runs inside ONE uncommitted transaction, so this scan reads a 725 MB
    table through a 256 MB write-ahead log, paying a WAL frame lookup per page. A
    whole-run sample attributed 97 % of stacks to this single `execute`, and the
    200-file run spent about fifteen of its twenty-three minutes inside it.

    `extraction_runs` holds the same pairs and is 425 rows rather than 365,690:
    every observation belongs to a run, `RunWriter` writes both from one record, and
    `observation_count` is how many that run wrote. So a run with observations is
    exactly a pair with evidence. Verified on three real databases -- the owner's
    18-file corpus twice and the 200-file corpus -- as identical SETS, not merely
    equal counts. 2.34s becomes 0.0025s.

    It is a function rather than a line in `_raise_questions` so that
    `tests/integration/test_questions_query.py` can hold the two formulations
    against each other on a database a real run produced. An equivalence that only a
    comment asserts is an equivalence that stops being true.
    """
    return [(row[0], row[1]) for row in conn.execute(
        "SELECT DISTINCT file_id, content_hash FROM extraction_runs "
        "WHERE observation_count > 0")]


class RejectionRefused(NotConfigured):
    """`--reject` named something this plan has never proposed."""


def apply_rejections(conn: sqlite3.Connection, rejections: Sequence[str], *,
                     user_id: str, observed_at: str) -> None:
    """Record what the person typed at `--reject`, before the run reads anything.

    §8.7 is the promise this pays: the product must "store negative feedback so the
    same attractive but incorrect conclusion is not resurfaced". Every other
    proposing part already asks that question on its live path -- P7's
    `privacy.learning_seam.suppressed`, P9's `grouping.graph`, P10's
    `tree_design.provenance`, P11's `placement.learning.suppressed_nodes` -- and P6
    now asks it too, inside `facts.direct.direct_facts`. Until this flag existed
    there was no gesture anywhere in this command that could put a fact-level answer
    INTO the store those guards read, so the guards were reachable and nothing could
    ever reach them.

    Applied after `--answer` and before the run, for the same reason `--answer` is: a
    person who has just been shown a wrong conclusion and said so should see the
    difference on this invocation, not the next one.

    The lookup and the two writes belong to P6 (`facts.learning.reject_claim`), not
    here. This turns one typed string into three words and hands them over; a SELECT
    over `file_facts` written in this file would be a second home for P6's schema in
    the one module that is supposed to hold none.

    A name this plan has not proposed is REFUSED rather than ignored, exactly as an
    unknown `--answer` is: the person believes they have told the product something,
    and a silently dropped rejection is the worst of both.
    """
    for raw in rejections:
        target, _, value = raw.partition("=")
        filename, _, field_key = target.rpartition(":")
        if not filename or not field_key or not value:
            raise RejectionRefused(
                f"{raw!r} is not a rejection. The form is "
                "`--reject <file>:<field>=<value>`, naming something this plan "
                "proposed -- for example "
                "`--reject 'week 3.pdf:subject=PHYS1401'`.")
        # EVERY row, not the first. `notes.txt` in two course folders is the
        # most ordinary thing on a real disk, and taking the first match would
        # retract a conclusion about a file the person did not name while the
        # screen said it worked. A gesture that acts on something other than
        # what was named is worse than one that stops and asks -- the same
        # ruling a bare label for a split review set gets.
        #
        # EVERY row P1 HAS NOT RETIRED (R-25). Two versions of one file are not
        # two files, and the refusal below could not tell them apart: a file
        # edited between runs left the old row at the SAME path, so `--reject`
        # refused with "names 2 files" and offered the person the identical path
        # twice as the way to say which one they meant. `84` §6 -- what the screen
        # tells a person to type has to be true, and there was no way to type it.
        rows = conn.execute(
            "SELECT file_id, content_hash, current_path FROM files "
            "WHERE filename = ? AND scan_state NOT IN (?, ?) "
            "ORDER BY current_path",
            (filename, SUPERSEDED_CONTENT, PATH_NO_LONGER_EXISTS)).fetchall()
        if not rows:
            raise RejectionRefused(
                f"{filename!r} is not a file in this plan. Run the command without "
                "`--reject` first: there is nothing to reject until the product has "
                "proposed something.")
        if len(rows) > 1:
            paths = "\n    ".join(row["current_path"] for row in rows)
            raise RejectionRefused(
                f"{filename!r} names {len(rows)} files in this plan, and this "
                f"rejection would only reach one of them. Name the one you mean "
                f"by its path:\n    {paths}")
        row = rows[0]
        try:
            reject_claim(conn, file_id=row["file_id"],
                         content_hash=row["content_hash"], field_key=field_key,
                         value=value, action=ACTION_REJECT, user_id=user_id,
                         observed_at=observed_at)
        except NoSuchClaim as refusal:
            # P6 names the file by its id, which is the right word inside P6 and
            # the wrong one on a screen: the person typed a filename and has
            # never seen a uuid. Re-said in their words, with P6's reason kept.
            raise RejectionRefused(
                str(refusal).replace(repr(row["file_id"]), repr(filename))
            ) from refusal


class AnswerRefused(NotConfigured):
    """`--answer` named something this database has never asked about."""


def apply_answers(conn: sqlite3.Connection, answers: Sequence[str], *,
                  user_id: str, recorded_at: str) -> tuple[tuple[str, str], ...]:
    """Record what the person typed at `--answer`, before the run reads anything.

    Applied FIRST so an answer takes effect on the very run that supplies it. A
    person who has just been asked a question and answers it should not have to
    run the command a third time to see what their answer did.

    A `question_id` this database has not asked about is REFUSED rather than
    ignored: the person believes they have told the product something, and a
    silently dropped answer is the worst of both -- no effect, and no way to tell.
    """
    # WHAT WAS SETTLED, not how many. §17's diff is per question and per scope,
    # and the scope is read from the question here already -- a second SELECT in
    # the printer would be a second home for P15's schema in the one file that is
    # supposed to hold none.
    settled: list[tuple[str, str]] = []
    for raw in answers:
        question_id, _, option_id = raw.partition("=")
        if not question_id or not option_id:
            raise AnswerRefused(
                f"{raw!r} is not an answer. The form is "
                "`--answer <question>=<option>`, `--answer <question>=skip` "
                "and `--answer <question>=revoke` "
                "puts it aside without answering it.")
        row = conn.execute(
            "SELECT scope FROM structural_questions WHERE question_id = ?",
            (question_id,)).fetchone()
        if row is None:
            raise AnswerRefused(
                f"{question_id!r} names no question this plan has asked. Run the "
                "command without `--answer` first: questions are raised from the "
                "evidence in your own files, so they exist only once a run has "
                "found the ambiguity they are about.")
        skipped = option_id in (SKIPPED, "skip")
        # §12 requires an answer to be "edited, revoked, or re-run". `live_answer`
        # has honoured revocation since P15 shipped -- a revoked answer reopens
        # its question -- and there was no way to SAY it: a person who chose
        # wrongly could re-confirm a different option but could not withdraw the
        # answer and be asked again. That gap is worst for the answer hardest to
        # get right first time, which is the one taken before they had seen what
        # it would do.
        revoked = option_id in (REVOKED, "revoke")
        state = REVOKED if revoked else SKIPPED if skipped else CONFIRMED
        # The ID, not the record: `supersedes` names the row this answer replaces,
        # and `live_answer` returns a `StructuralAnswer`, which carries no id. Passing
        # `None` here left every answer live at once -- `live_answer` defines the live
        # one as the one NOTHING supersedes -- so a person who answered twice had the
        # winner chosen by `ORDER BY recorded_at DESC, answer_id DESC`. `main` computes
        # `now()` once, so the timestamps tie and a uuid4 breaks the tie: the person's
        # own correction was decided at random.
        previous_id = live_answer_id(conn, question_id=question_id, scope=row[0])
        if revoked and previous_id is None:
            raise AnswerRefused(
                f"{question_id!r} has no answer to revoke. Revoking is how you "
                "take back something you told the product, so there has to be "
                "something there to take back.")
        record_answer(conn, StructuralAnswer(
            question_id=question_id,
            option_id=None if (skipped or revoked) else option_id,
            state=state,
            scope=row[0], user_id=user_id, recorded_at=recorded_at,
            supersedes=previous_id,
            supersede_reason=("the user withdrew this answer" if revoked else
                              "the user answered this again"
                              if previous_id is not None else None)))
        settled.append((question_id, row[0]))
    return tuple(settled)


def _print_answer_effects(conn: sqlite3.Connection, settled, out) -> None:
    """§17:577's diff, for the answers this invocation actually changed.

    `changed_answer` returns `None` for a FIRST answer, which is why this prints
    nothing for one: §17's trigger is "edits or re-runs", and a first answer is
    the ordinary case the rest of P15 already handles.

    The three questions P15 cannot produce are PRINTED with their reasons rather
    than left out. A diff naming the three it can would read as a complete account
    of what the correction did, and that is the one a person acts on --
    `PlanEffectDiff.is_empty` refuses to be read as "the answer had no effect" for
    the same reason, in its own docstring.
    """
    out = out if out is not None else sys.stdout
    for question_id, scope in settled:
        change = changed_answer(conn, question_id=question_id, scope=scope)
        if change is None:
            continue
        diff = diff_for_answer_change(change)
        print(f"\nWhat changing {question_id} does to this plan:", file=out)
        if diff.is_empty:
            print("  Nothing this can see. Your answer was recorded and the "
                  "shape of the plan is unchanged.", file=out)
        for schema in diff.schemas_activated:
            print(f"  Turns on the `{schema}` schema.", file=out)
        for schema in diff.schemas_deactivated:
            print(f"  Turns off the `{schema}` schema.", file=out)
        if diff.templates_affected:
            # §17:577's own phrase, and no direction claimed: `templates_affected`
            # is a symmetric difference, so which of these you are leaving and
            # which you are taking is not in the data. Saying "was X, now Y" would
            # be the report deciding it.
            print("  Templates affected: "
                  + ", ".join(diff.templates_affected), file=out)
        for branch in diff.branches_needing_review:
            print(f"  {branch} may need looking at again.", file=out)
        print("  Not worked out here, and why:", file=out)
        for name, reason in diff.why_not_computed.items():
            print(f"    {name}: {reason}", file=out)


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
#: WHAT A PLACEMENT IS ACTUALLY CALLED, which is not decided by the outcome
#: alone. `place` is P11's answer about WHERE a file belongs; it is not
#: permission to move it. Three review policies ride alongside it and the report
#: keyed its headline on the outcome only, so on the four-role persona EIGHT
#: files of ten printed under "Ready to file into X" when nothing had classified
#: them, and a file carrying protected material printed there too. A person
#: reading that would have believed the product was ready to move a passport.
#:
#: The destination is kept in the headline in all three cases. Not being ready is
#: not a reason to withhold the answer -- the person still wants to know where
#: the file WOULD go and what is being waited on, and `00`'s standing rule is
#: that nothing is silently omitted.
#: `{where}` is the destination and is always present, so the three read as one
#: sentence each rather than as a word with a folder appended.
PLACEMENT_WORDS: dict[str, str] = {
    pv.AUTO_ELIGIBLE: "Ready to file into {where}",
    pv.REVIEW_REQUIRED: "Ready for you to approve, then file into {where}",
    pv.BLOCKED_PENDING_USER: "Would go into {where}, once you say what these are",
}

#: What to say when the file is ALREADY in a folder of the destination's name.
#:
#: `00`:100: "Existing folders must not be automatically flattened, renamed, or
#: reorganized simply because a template would produce a different structure." A
#: person with `Uni/PHYS1401/lab-report.txt` was told "Ready to file into
#: PHYS1401" -- the flattening that sentence forbids, announced as progress.
#:
#: This decides NOTHING. Which of `00`:100's six gestures applies to a folder the
#: person already made is their choice and the design states no default, so it
#: stays open and the "Decisions made for you" block says so. What changes is that
#: the report stops describing a no-op as an action. The fact is one the run
#: already holds: the file's immediate parent is named what the destination is
#: named.
#: When the destination IS the folder the file is sitting in -- the same folder,
#: not another one wearing its name. Only reachable since the person's own folders
#: are adopted as `existing` nodes carrying their real path, and worth its own
#: wording because "the plan would put it in the one it proposes" describes a move
#: out of a folder and back into it.
SAME_FOLDER: dict[str, str] = {
    pv.AUTO_ELIGIBLE: "Already in {where} -- nothing to do",
    pv.REVIEW_REQUIRED: (
        "Already in {where}; the plan agrees it belongs there and is waiting on "
        "your review"),
    pv.BLOCKED_PENDING_USER: (
        "Already in {where}, and waiting on you to say what these are"),
}

#: When the file sits in a folder of the same NAME somewhere else -- a real move
#: between two folders a person would have to tell apart.
ALREADY_THERE: dict[str, str] = {
    pv.AUTO_ELIGIBLE: "Already in a folder called {where} -- nothing to do",
    pv.REVIEW_REQUIRED: (
        "Already in a folder called {where}; the plan would put it in the one it "
        "proposes"),
    pv.BLOCKED_PENDING_USER: (
        "Already in a folder called {where}, and waiting on you to say what "
        "these are"),
}

#: `104` R-92 / R-H. WHAT TO SAY WHEN NOTHING ON THE SCREEN LETS THEM SAY IT.
#:
#: Measured on a 52-file folder: after every question the report printed had been
#: answered, five files still read "Would go into lecture, once you say what
#: these are" and no `--answer`, `--send-set` or `--describe-role` anywhere in
#: the report reached one of them. They are `unreadable_unclassified` -- nothing
#: has said what kind of material they are -- and offline nothing in this build
#: can say it for them.
#:
#: `84` §6's standing ruling is that what the screen tells a person to type has
#: to be true, and a sentence that says "once you say" when there is no way to
#: say it fails that in the worst direction: the person goes looking for the
#: gesture, does not find it, and concludes the fault is theirs.
#:
#: THE DESTINATION IS STILL IN THE SENTENCE, exactly as it is in the three tables
#: above. Not being able to act on it is not a reason to withhold where the file
#: would go, and the standing rule is that nothing is silently omitted. What
#: changes is the promise, and the note printed under the group says what these
#: files are actually waiting on.
#:
#: Keyed the way the three tables above are selected between -- the same folder,
#: a folder of the same name, or a move -- because there is one of these
#: sentences for each and a policy key would say nothing: this table is reached
#: only for `blocked_pending_user`.
#: "SOMETHING" AND NOT "YOU", which is the whole edit. The three tables above say
#: "once you say what these are" and mean it; these say the file is waiting on a
#: classification that nothing here made, which is `104` R-H's own wording of what
#: the sentence should name -- "the missing thing (a classification) rather than
#: imply an answer exists".
NOTHING_SAYS_WHAT_THESE_ARE: dict[str, str] = {
    "same_folder": ("Already in {where}, and waiting on something to say what "
                    "these are"),
    "already_there": ("Already in a folder called {where}, and waiting on "
                      "something to say what these are"),
    "moving": "Would go into {where}, once something can say what these are",
}


def _already_in(name: str, where: str | None) -> bool:
    """Whether this file's own parent folder is already named `where`.

    Compared on the IMMEDIATE parent only, and case-insensitively. A grandparent
    of the same name is not the same claim -- `Coursework/PHYS1401/old/x.txt` is
    not already filed under `PHYS1401` in the sense a person means -- and a
    filename that happens to match is not a folder at all.
    """
    if not where:
        return False
    parts = PurePosixPath(name).parts
    return len(parts) > 1 and parts[-2].casefold() == where.casefold()


def _is_the_same_folder(name: str, existing_path: str | None) -> bool:
    """Whether the destination is THE folder this file is in, not one like it.

    `name` is the path relative to the corpus root and `existing_path` is what P3
    recorded, absolute. The whole relative parent is compared against the tail of
    the real path -- not the last segment -- so `Uni/PHYS1401` and
    `Downloads/PHYS1401` cannot be mistaken for one another, which is the case
    that made the name comparison too weak to carry this sentence.
    """
    if not existing_path:
        return False
    parent = str(PurePosixPath(name).parent)
    if parent in ("", "."):
        return False
    real = existing_path.replace("\\", "/").rstrip("/")
    return real == parent or real.endswith("/" + parent)

OUTCOME_WORDS: dict[str, str] = {
    pv.PLACE: "Ready to file",
    pv.LEAVE_IN_PLACE: "Staying exactly where they are",
    pv.MARK_STATE: "Marked and left alone",
    pv.MARK_REVIEW_LATER: "Set aside for you to look at later",
    pv.RETURN_TO_PLACEMENT: "Sent back round for another look",
    pv.ASK_USER: "Waiting for you to choose where these go",
    pv.ABSTAIN: "Waiting for you to say what these are",
}

#: THE QUESTIONS THE FREEZE DEMANDS, AND THE ANSWERS THIS COMMAND GAVE.
#:
#: `66`'s onboarding question registry is not built. What IS built is a P10 that
#: refuses to freeze until these are answered -- `TreeDesignDecisions` documents
#: every one of them as the USER's, and `validate_for_freeze` rejects any legal
#: destination carrying no refinement disposition. Run non-interactively there is
#: nobody to ask, so this file answers them, and until now it said nothing about
#: having done so.
#:
#: That silence was not neutral. A frozen tree is PERMANENT, and it records
#: `shallow-by-choice` -- a value that literally means the user chose it -- with a
#: reason written in their voice: "This branch holds few enough files that
#: splitting it further would not help you find anything." Nobody said that. P13
#: will show it back to them as their own words unless something says otherwise.
#:
#: TWO things now say otherwise, and both are needed. This list says it on the
#: screen; `refinement_for` says it IN THE RECORD, by opening every reason with
#: the actor that produced it -- "The rules", `actor_phrase(SURFACE_UNATTENDED)`,
#: the same subject §8.2's events carry on this run. The screen is read by a
#: person once; the record is read by P13, by a replay and by the audit log
#: forever, and R-28 is about the second one.
#:
#: This is not the registry and does not pretend to be: no question has an id, no
#: answer is persisted, nothing is asked. It is the smaller thing the registry
#: cannot be built without -- the list of what was decided on the person's behalf,
#: in the words of the question rather than the field.
#:
#: Each entry is (the question, the answer taken). The answers restate what
#: `choose_option`, `refinement_for` and `design_decisions` below actually do; a
#: line here that drifts from them is a lie, so they are written next to the
#: reasons that produced them and are checked by `tests/test_cli.py`.
DEFAULTED_DECISIONS: tuple[tuple[str, str], ...] = (
    # First, because §5.3 builds the top level "out of the accepted groups,
    # domain memberships, existing curated folders, and user-approved labels"
    # (`00:67`) and for most of this command's life it supplied exactly one of
    # the four. The folders were read and offered and then dropped, because the
    # selection filter matches on `subject_id` and a folder candidate's is a
    # directory PATH while this command passed one synthetic id minted from
    # `--label`. Measured then: eight directories in, eight cards built, none
    # chosen, and a tree byte-identical to the one the same ten files produce
    # when flattened into a single directory.
    #
    # They are adopted now, as `00:102`'s `existing` nodes carrying the real
    # path, nested under whichever of their own parent directories was adopted
    # too. What is still decided on the person's behalf is WHICH -- `00:100`
    # gives them six gestures over their own folders (attach beneath, merge into,
    # rename to match, leave untouched among them) and none of the six has a
    # consumer, so this command takes the only one it can defend with nobody at
    # the screen: keep every folder exactly where it is and change none of them.
    ("Which of the folders you have already made to keep",
     "all of them, exactly where they are. Every folder under the one you "
     "scanned is in this proposal as your folder -- its real path is recorded "
     "and its parent folder is still its parent -- so nothing of yours is "
     "moved, renamed or merged, and a file already sitting where it belongs is "
     "described here as staying put. Nobody was asked whether to attach one of "
     "your folders beneath another, merge two that overlap, or leave one out "
     "of the picture, so none of that was done."),
    ("Which nesting to use, out of the ones your files support",
     "the first one that passed every check and actually splits the folder. A "
     "person looking at the counts and warnings would reasonably pick another."),
    ("How deep each folder goes",
     "the top-level folder is treated as fully refined. Every branch under it is "
     f"counted: one holding {TREE_LIMITS.tiny_folder_max_files} file(s) or fewer "
     "is marked shallow, because splitting it could not help anyone find "
     "anything, and every other one is marked as left for you to split "
     "further. Nobody was asked which a branch should be, so the count is "
     "standing in for an answer only you can give -- and each of those "
     "answers is recorded as the rules', in the rules' words, not yours."),
    ("Where material that belongs to two folders goes",
     "kept as your decision, file by file, rather than sent to one of them. It "
     "is the only answer a command with nobody to ask may make for you."),
    ("Whether to add a catch-all folder for things the branch does not cover",
     "not added. An unasked question answered by default is a folder nobody "
     "wanted."),
    ("Which levels to leave out",
     "any level your files did not actually divide. If every file names the same "
     "term, a folder for it would hold all of them and you would open it to find "
     "one folder -- so it is measured and not built. A level your files DO divide "
     "is always built."),
    ("What to call the top-level folder, and what kind of material this is",
     "taken from `--label` and `--situation` exactly as you typed them, and "
     "applied to EVERY file in the folder -- including any that are something "
     "else entirely."),
)

#: How many files of one kind are named before the rest are counted instead.
#: `src/tree_design/health.py` shortens its warning list for the same reason --
#: a list longer than the thing it describes is not a summary of anything -- and
#: this follows it. `00` states no number; ten is enough to recognise a folder's
#: worth of files by eye and short enough to stay a summary.
#:
#: It no longer carries an exemption for protected groups. Those are not
#: shortened to ten either -- they are summarised entirely and expanded by
#: `--show-protected`, which is `PROTECTED_SUMMARY` below.
NAMES_LISTED_PER_GROUP: int = 10

#: WHAT THE REPORT SAYS INSTEAD OF A PERSON'S PROTECTED FILENAMES, and the
#: command that prints them.
#:
#: THE OWNER RULED THIS ON 2026-09-02, REVERSING HIS OWN EARLIER DECISION.
#: `planning/93-PROTECTED-DISCLOSURE-RULING.md` records what he chose, over what,
#: and on which numbers -- read it before changing this, because the code here
#: contradicts one half of `00` on purpose and the next person to notice will
#: otherwise "fix" it back.
#:
#: The short version. He first chose "listed in full, and last" when the longest
#: such list anyone had seen was four names in a demo folder. Measured on a
#: corpus the size of a real disk it was 710 filenames -- 73 % of the whole
#: report -- so what the screen mostly showed was the person's own payslips,
#: bank statements, medical notes and passport scans, by name. Shown that, he
#: took `00`:201's other half: "a summary such as '11 protected identity
#: records' may be safe to show, while a visible list of passport filenames on a
#: shared screen may not be."
#:
#: "MARKED AND COUNTED, NEVER SILENTLY OMITTED" IS UNCHANGED, and both lines
#: below are what keeps it true. The count is on the screen every time, so a
#: person never has to ask whether something was set aside. The command is on the
#: screen every time, so the names are one paste away -- a summary a person
#: cannot get out of would be the concealment the rule forbids, and dropping the
#: second line is the way this stops being a summary and starts being a hiding
#: place. The expansion is COMPLETE and not the first ten, for the same reason.
#:
#: `{count}` and `{plural}` are the group's own, so the number here and the
#: number in the heading above it can never disagree. The second line is indented
#: and is therefore printed verbatim -- `_role_lines`' convention, because a
#: command a text wrapper has broken is not a command.
#: "AND NONE OF THEM OPENED" IS GONE (`104` R-J). It was never true of a §8.4
#: file: this product read it, indexed it and classified it on this device --
#: that is how it knows the file is protected at all. What it did not do is send
#: it to a model or file it in one gesture with everything else, and those are
#: the two sentences the group's own heading already carries. "Of the N counted
#: at the top" ties this number to the one in `_print_protected`, so a person
#: meeting the word twice can see it is one count and not two.
PROTECTED_SUMMARY: tuple[str, ...] = (
    "{count} protected file{plural}, of the ones counted at the top of this "
    "report. Their names are not printed here, because a list of them is the "
    "part of this report least safe to have on a screen somebody else can see. "
    "Nothing is being kept from you -- to see every one:",
    "      --show-protected",
)


def file_names(conn: sqlite3.Connection, *roots: Path) -> dict[str, str]:
    """Every indexed file, by the name its owner calls it.

    `files.current_path` is P1's own column and has always been there, so a
    report printing `74ce335f-110b-42c0-8a50-ecdc8f8734b7` was never showing the
    only thing it had. A person cannot tell which of their own files that is,
    which makes every line built on it unusable.

    Shown relative to the folder that was scanned, because that is the name the
    person typed and the part that tells two `notes.txt` apart. A file outside
    every folder that was scanned keeps its full path rather than being guessed
    at.

    Several roots, because `00`:20 lets a person name several folders to read and
    a report that showed the second one's files as absolute paths and the first
    one's as bare names would be saying two different things in one column. The
    DEEPEST matching root wins, so a name is relative to the folder the person
    actually typed rather than to whichever one happened to be checked first.

    Nothing inside a protected container appears here, and not by omission: P3
    never walks into one, so no `files` row for its interior exists to read.

    NOR A VERSION P1 HAS RETIRED (R-25). A file edited between two runs leaves the
    old row `superseded_content` at the SAME path, so this map held two ids for
    one name and every screen built on it counted the person's four files as five.
    `84` §1 is not broken by leaving the ghost out: a superseded version is not
    material the person has, so there is nothing here to mark or count.

    P1's two sentinels by name, never "not the scanned value" -- `scan_state` is
    P3's column and most of its vocabulary means the file is present.
    """
    ordered = sorted(roots, key=lambda root: len(Path(root).parts), reverse=True)
    names: dict[str, str] = {}
    for row in conn.execute(
            "SELECT file_id, current_path FROM files "
            "WHERE scan_state NOT IN (?, ?)",
            (SUPERSEDED_CONTENT, PATH_NO_LONGER_EXISTS)):
        path = Path(row["current_path"])
        names[row["file_id"]] = str(path)
        for root in ordered:
            try:
                names[row["file_id"]] = str(path.relative_to(root))
            except ValueError:
                continue
            break
    return names


def _wrapped(text: str, *, indent: str, first: str | None = None) -> str:
    """`first` differs from `indent` only for a bullet, whose marker belongs on
    the first line and whose continuation lines must line up past it.

    NOTHING IS BROKEN MID-TOKEN, and both switches are load-bearing rather than
    tidy. `_role_lines` below already records the rule -- "textwrap breaking a
    command across two lines produces a command that does not work, which is `84`
    §6's recurring defect" -- and applies it by keeping pasteable lines out of the
    wrapper. But a flag named INSIDE a sentence never reaches that escape, and
    `textwrap` splits on hyphens by default, so `--enable-cloud` was printing as
    `--enable-` then `cloud`: the product telling a person to type something that
    is not typeable. `model-for-D_residual` split the same way, leaving a model
    name a person could not read or search for.

    `break_on_hyphens=False` is the one that fixes both; `break_long_words=False`
    covers the token with no hyphen in it at all -- a long path or an unbroken
    identifier -- which is the same hazard the send-set line and the database path
    already dodge by printing on their own line.
    """
    return textwrap.fill(text, width=78,
                         initial_indent=indent if first is None else first,
                         subsequent_indent=indent,
                         break_on_hyphens=False, break_long_words=False)


def _role_lines(lines: Sequence[str], *, out) -> None:
    """Prose wrapped; a line a person is meant to paste printed exactly as it is.

    `textwrap` breaking a command across two lines produces a command that does not
    work, which is `84` §6's recurring defect: what the screen tells a person to
    type has to be true. `role_report` indents its own pasteable lines, so the
    leading space is the mark, and it is the same mark `ask()` uses above.
    """
    for line in lines:
        print(line if line.startswith(" ") else _wrapped(line, indent="  "),
              file=out)


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


def _typable(question, option_id: str) -> str:
    """One `QUESTION=OPTION` argument the person can actually paste.

    The scope of a branch question is the person's OWN label -- `--label "Legal
    Matters"` produces `branch:Legal Matters` -- so the line the report offers
    contains a space, and a shell splits it into two arguments. The report's one
    actionable instruction then fails, and it fails looking like the person's
    mistake rather than ours.

    `shlex.quote` leaves an argument that needs no quoting exactly as it was, so
    the ordinary line is unchanged and only the one that would break is altered.
    """
    return shlex.quote(f"{question.question_id}={option_id}")


def _option_lines(question, family: Sequence[str], *,
                  only_the_ones_that_classify: bool = False,
                  ) -> tuple[str, ...]:
    """One `--answer` line per option, with the person's own situation first.

    `104` R-90. A person who typed `--situation academic.coursework` was asked
    "What kind of material is ECON2010?" and offered `clinical_practice`,
    `construction_property` and `retail_hospitality` among seven equal readings.
    The tie is real -- the file's own words do support all seven -- and the
    QUESTION is load-bearing: answering the three of them `academic` moved this
    corpus from 7 ready to file to 10. What was wrong is the presentation. The
    person had already said which life these files belong to, on the command
    line, and the screen asked them to find that answer again in a list of
    domains they never named.

    So the readings the typed situation's own family carries are printed first,
    and the rest are FOLDED behind `--explain`, which prints every option this
    question has ever offered. `situation_schema_family` is where the family
    comes from and it is the library's own hierarchy, not a rule invented here.

    NOTHING IS REMOVED. The closed vocabulary is the evidence's answer and stays
    exactly as the record holds it: `--explain <question>` lists all of them, an
    `--answer` naming a folded reading is accepted as it always was, and a run
    with no family (every caller that passes none) prints what it printed before.
    Folding is presentation and it is reversible by one command that is printed
    beside it.

    `not_mine` and the trailing `skip` are never folded. §14 makes both
    first-class answers, and an answer a person has to run a second command to
    find is not first-class.

    `only_the_ones_that_classify` is the file-group caller's (`104` R-92): under
    "Would go into X, once you say what these are" the point of the line is that
    it REACHES those files, and neither "it is not about me" nor "skip for now"
    says what the material is. The question block below prints both, so nothing
    is hidden by leaving them out of a sentence about reaching.
    """
    inside, outside, plain = [], [], []
    for option in question.options:
        schema = option.activates_schema
        if schema is None and option.selects_situation:
            # `104` R-37: choosing a branch's situation says what the material
            # under it is, as a reading does, so under "each of these answers
            # reaches these files" it is printed rather than left out.
            inside.append(option)
        elif schema is None:
            plain.append(option)
        elif schema in family:
            inside.append(option)
        else:
            outside.append(option)
    # Folding needs somewhere to fold TO and something worth folding. With no
    # option inside the family the situation says nothing about this question,
    # and hiding readings behind a command would be the screen keeping evidence
    # back for no gain; with one option outside it, the fold line costs a line
    # and saves a line and loses an option.
    folding = bool(inside) and len(outside) > 1
    shown = inside + ([] if folding else outside)
    lines = [f"      --answer {_typable(question, option.option_id)}"
             f"   {option.label}" for option in shown]
    if folding:
        # NEITHER "this file's" NOR "these files'". The question above it says
        # "4 files mention ECON2010, and their own words support 7 readings" and
        # the same sentence is printed under a group of one; a possessive here
        # contradicts one of the two every time it is printed.
        lines.append(_wrapped(
            f"...and {len(outside)} other readings this run also found support "
            f"for, which are not the kind of material you named. They are still "
            f"offered and this lists every one of them:", indent="    "))
        lines.append(f"      --explain {shlex.quote(question.question_id)}")
    if only_the_ones_that_classify:
        return tuple(lines)
    lines.extend(f"      --answer {_typable(question, option.option_id)}"
                 f"   {option.label}" for option in plain)
    lines.append(f"      --answer {_typable(question, 'skip')}   Skip for now")
    return tuple(lines)


def _questions_by_file(
        reaches: Mapping[str, Sequence[str]]) -> dict[str, tuple[str, ...]]:
    """`104` R-92, turned round: which questions settle each file.

    The run produces the other direction -- one question, the files whose tie it
    would settle -- because that is the shape the trigger has. The report groups
    FILES, so it asks the opposite question, and inverting once here keeps the
    grouping loop from doing it once per decision.
    """
    by_file: dict[str, list[str]] = {}
    for question_id, file_ids in reaches.items():
        for file_id in file_ids:
            by_file.setdefault(file_id, []).append(question_id)
    return {file_id: tuple(sorted(set(ids))) for file_id, ids in by_file.items()}


def _how_to_say_what_these_are(questions: Sequence,
                               family: Sequence[str]) -> tuple[str, ...]:
    """`104` R-92: the gesture that reaches a file the run is waiting on.

    "Would go into lecture, once you say what these are -- 5 files", and no
    `--answer` the report offered reached one of the five. Measured on a 52-file
    folder after every printed question had been answered: two of those files
    were reachable and three were not, and the same sentence covered both. `84`
    §6's standing ruling is that what the screen tells a person to type has to be
    true, and this is the sentence that was not.

    So a group that a printed question WOULD settle names it, and names the
    answers themselves, on their own lines, in the words the question block below
    prints them in -- `_option_lines` is the same function that prints them
    there, so the two cannot disagree about what exists.

    NOT `not_mine`, NOT `skip`. Both are first-class answers and both are printed
    with the question; neither says what the material is, so neither belongs in a
    sentence whose whole claim is that these lines REACH these files.

    A group nothing reaches gets the truth instead of a command. There is no
    `--answer` for a file whose own words matched nothing, no review set holds a
    file that already has a destination, and inventing a gesture here would be
    the defect again with a citation. What is said instead is what the file is
    actually waiting on -- a classification, which this run did not make -- and
    the two things a person can actually do about it: give the run a model, which
    the report's own first lines explain, or look at what this plan can hold with
    `--list-residuals`.

    `00`'s standing rule is that nothing is silently omitted, and this is the
    other half of it: a file counted on the screen with nothing said about how to
    move it forward is counted and abandoned.
    """
    if not questions:
        # SAYS NOTHING ABOUT THE REST OF THE SCREEN. An earlier draft pointed at
        # "the lines at the top of this report", which are printed only when no
        # model is configured -- so on a run that has one, this sentence would
        # have cited a paragraph that is not there, which is the same defect
        # wearing the fix's clothes.
        return (
            "Nothing on this screen says what these are: no question this run "
            "raised is about them, and no answer, no `--send-set` and no "
            "`--describe-role` here reaches them. What they "
            "are waiting on is something saying what kind of material they are, "
            "and this run produced nothing that did. They stay exactly where "
            "they are meanwhile, and the folder above is where they would go "
            "once something can say what they are. The areas this plan can hold "
            "material in are printed by",
            "      --list-residuals")
    lines: list[str] = []
    for question in questions:
        lines.append(
            f'Saying what these are is "{question.prompt}" below, and each of '
            f"these answers reaches these files:")
        lines.extend(_option_lines(question, family,
                                   only_the_ones_that_classify=True))
    return tuple(lines)


def _review_note(items: Sequence, areas: Sequence[str], *,
                 reason_already_said: bool = False
                 ) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Why these sets are being held, and what a person can type about each one.

    TWO blocks, and the split is `104` R-122: this group's own lines, and the one
    sentence about the PLAN. The caller prints the first under every group and
    the second once on the screen.

    LINES, not one sentence, and a line that begins with a space is printed
    exactly as it is -- `_role_lines`' convention, for `_role_lines`' reason. A
    command `textwrap` has broken across two lines is not a command, because the
    quote never closes: this built `--send-set` into prose and let `report` wrap
    it, so `Receipts and Confirmations` -- one of §7.3's nine -- printed as
    `--send-set "Not yet placed=Receipts and` with `Confirmations"` underneath.

    **A hold's reason is one fact however many sets carry it.** §8.6 splits a set
    over the batch ceiling rather than truncating it, so over a real disk one
    hold arrives as `Not yet placed (1 of 420)` through `(420 of 420)`: 420 sets,
    one reason, and the reason was printed 420 times -- 9,460 lines for 4,068
    files, measured at the eight-file ceiling `104` R-93 replaced. A screenful of
    25 divides the same hold into fewer sets and changes nothing about this: the
    reason is said once here and the batches are named beneath it.

    **The batches are not one fact.** `act_on_residual_sets` addresses a set by
    the label the report printed and refuses a bare label that names no surfaced
    set, so one `--send-set` files ONE batch -- and the sentence beside it may
    not say it files them all, which is what it used to say.

    A hold with no command beside it is the product saying it noticed and will do
    nothing. With no residual area enabled the sentence says how to make one
    rather than naming a flag that would refuse.

    **AND THAT SENTENCE IS ABOUT THE PLAN, NOT ABOUT THIS GROUP.** `104` R-122:
    after R-114 the 52-file screen was still 412 lines because this block is what
    kept repeating -- eight groups, eight printings of "this plan has nowhere to
    put them yet", which R-114's fold could not touch because the `Held for
    review as "<set>"` line above it names a different set each time and the fold
    keys on the block being word for word the same. The set name is this group's
    fact and stays under it; whether the plan has anywhere to put anything is one
    fact about the plan, and it is returned separately so the caller can say it
    once. Returned rather than printed here for the same reason `report` folds
    rather than `_review_note` does: this function sees one group and the fold is
    a fact about the whole screen.

    It is lifted OUT of the per-reason loop as well, so a group whose held sets
    stopped for two reasons says it after both rather than after each.

    **AND THE REASON ITSELF IS SAID ONCE.** `104` R-124: after R-115 divided the
    sets by the reason the screen already prints, a held group said that reason
    twice in different words -- four lines of "Same reason for each: deciding
    this file needed a model, and this folder's privacy settings only let one
    that runs on this device be asked about it" and then four more of `Held for
    review as "A model was not allowed to look": deciding these needed a model,
    and the privacy settings on the folder they are in do not let one be asked
    about them`. `reason_already_said` is the caller saying it has printed the
    first, and then the held line is only the NAME -- which is the part a person
    types after `--send-set` and the part the first sentence does not carry.

    **Only when the group really said it.** `report` computes its group reason as
    `"" if outcome is PLACE else explanation`, so a placement waiting on somebody
    -- which is a group that can hold a review set -- prints no "Same reason for
    each" at all, and there the set's reason is the only reason on the screen.
    The flag is off there and the words stay. Off, too, where this group holds
    sets stopped for MORE than one reason, because then the reasons are what tell
    the sets apart and the group's single sentence cannot be all of them.

    The set's own `reason_not_placed` is not lost either way: a set covering no
    decided file prints it under its own heading, and `review_surface` carries it
    to the residual listing.
    """
    by_reason: dict[tuple[bool, str], list] = {}
    for item in items:
        by_reason.setdefault((item.protected, item.reason_not_placed),
                             []).append(item)
    lines: list[str] = []
    # Whether anything under this heading is a hold a `--residual` area could
    # take. A group holding only PROTECTED sets gets no closing sentence, because
    # `--send-set` refuses protected material and the sentence offers it.
    unprotected = False
    # One reason per group is what makes this safe: with two, dropping both
    # would leave two sets under one sentence that describes neither exactly.
    say_the_name_only = reason_already_said and len(by_reason) == 1
    for (protected, reason), held in by_reason.items():
        opening = (f'Held for review as "{held[0].label}".' if say_the_name_only
                   else f'Held for review as "{held[0].label}": {reason}')
        if len(held) > 1:
            # Says what this function can SEE, and no more. §8.6's batches do not
            # respect the boundaries the report groups by, so one batch can hold
            # files printed under two headings: `items` is the batches touching
            # THIS group, not the whole hold. "these N files" beside a heading
            # that just counted a different N points at nothing, and "the hold is
            # split into N" is simply false when the hold is split into more.
            opening += (f" {len(held)} review sets of it have files under this "
                        "heading, and each is addressed by the name beside it.")
        lines.append(opening)
        # One batch is already named in the sentence above, so a hold that is one
        # batch says it once and only a SPLIT hold gets the roll-call. In that
        # roll-call a PROTECTED set is named however long the list is:
        # shortening the ordinary list is fine, and shortening the part that
        # says what was marked protected and left alone is the silent omission
        # the standing rule exists to forbid.
        shown = () if len(held) == 1 else (
            held if protected else held[:NAMES_LISTED_PER_GROUP])
        for item in shown:
            if protected:
                # No command, because there is no command. `--send-set` files a
                # set in one gesture with no per-file look, and P11 refuses that
                # over protected material before it reads any decision. Printing
                # the flag here would offer an instruction that always fails, and
                # it would contradict the sentence immediately above it. The set
                # is still shown, named and counted; what is withheld is a
                # suggestion that was never true.
                lines.append(f'"{item.label}" -- {item.file_count} file(s)')
            elif areas:
                # NOTHING after the command on its line. `--answer` learned this
                # too: a count appended for readability is pasted along with the
                # command and arrives at the shell as stray arguments.
                lines.append(f'      --send-set '
                             f'{shlex.quote(f"{item.label}={areas[0]}")}')
            else:
                lines.append(f'"{item.label}" -- {item.file_count} file(s)')
        if len(held) == 1 and not protected and areas:
            lines.append(f'      --send-set '
                         f'{shlex.quote(f"{held[0].label}={areas[0]}")}')
        rest = len(held) - len(shown) if shown else 0
        if rest:
            lines.append(
                f"...and {rest} more review sets held for the same reason, "
                "counted here rather than listed one by one so that the list "
                "stays shorter than the folder it describes; none of them is "
                "protected, which is never summarised away")
        if protected:
            continue
        unprotected = True
    # Word for word what used to sit at the end of each reason's block, so the
    # screen loses a repeat and no sentence. Exactly one of the two is possible:
    # with one area every set already carries its `--send-set` line and there is
    # nothing further to say, which is why a single area produces no closing
    # sentence at all and never did.
    closing: tuple[str, ...] = ()
    if unprotected:
        if areas[1:]:
            closing = (f'This plan also has {", ".join(areas[1:])}.',)
        elif not areas:
            closing = (
                "This plan has nowhere to put them yet: enable an area with "
                '`--residual "Review Later"` and each of these sets can be sent '
                "there with one command.",)
    return tuple(lines), closing


def high_level_folders(directory: Path, also_read: Sequence[Path],
                       candidate_roots: Sequence[Path]) -> dict[str, Path]:
    """§1.1's folder landscape, built once for the screen and for the freeze.

    It was built inline where the freeze is composed, and `104` R-N is what that
    cost: the report had no landscape, so it could not say which of its own
    proposals crossed one of these folders, and it offered a Desktop file a home
    under Downloads that the freeze then refused. One landscape, two readers.

    The candidate roots are in it because they are part of the landscape, and
    being in it makes nothing a destination: a destination needs a NODE whose
    `root_anchor` names it.
    """
    return {ROOT_ANCHOR: directory,
            **{str(folder): folder
               for folder in (*also_read, *candidate_roots)}}


def crossing_folder_for(conn: sqlite3.Connection, *, nodes,
                        landscape: Mapping[str, Path]):
    """THE ONE READING of "would this move cross a folder the person keeps".

    Returns `(file_id, node_id) -> the folder the file is in now` or `None`,
    named the way a person names it.

    One derivation, three readers: the screen marks such a proposal (`104` R-N),
    the review sets hold it so `--send-set` can reach it (`104` R-113), and the
    freeze refuses it. A second reading of this would eventually tell somebody a
    move is fine that the freeze refuses, which is R-N exactly, and telling them
    a file is in a review set that the screen says is ready to file, which is
    R-113 from the other side.

    P12's own predicate, imported rather than restated: `00`:20 makes crossing
    the person's third choice and `mutation/resolution.py` is where that choice
    is enforced.
    """
    paths = dict(conn.execute("SELECT file_id, current_path FROM files"))
    anchors = {node.node_id: node.root_anchor for node in nodes}

    def crossed(file_id: str, node_id: str) -> str | None:
        anchor = anchors.get(node_id)
        here = paths.get(file_id)
        if anchor is None or here is None:
            return None
        source = source_high_level_folder(Path(here), landscape)
        if source is None or source == anchor:
            return None
        # The folder's own name, not its path and not P10's anchor id.
        return Path(landscape[source]).name if source in landscape else source

    return crossed


def _crossing_moves(conn: sqlite3.Connection, result: ProductionRun, *,
                    landscape: Mapping[str, Path]) -> dict[str, str]:
    """Every proposed placement that would cross a high-level folder. `104` R-N.

    `file_id -> the folder the file is in now`, named the way a person names it.
    Empty when the person has already said such moves are allowed, because then
    there is nothing to mark: the proposal is one the plan will carry out.

    The reading itself is `crossing_folder_for`; this walks the run's decisions
    through it.
    """
    crossed = crossing_folder_for(conn, nodes=result.tree.tree.nodes,
                                  landscape=landscape)
    crossing: dict[str, str] = {}
    for decision in result.placement.decisions:
        if decision.destination is None:
            continue
        for file_id in _files_of(decision):
            source = crossed(file_id, decision.destination.node_id)
            if source is not None:
                crossing[file_id] = source
    return crossing


def duplicate_families(conn: sqlite3.Connection,
                       scan_run_id: str) -> dict[str, tuple[str, ...]]:
    """§3.11's `duplicate_family`, as families rather than as per-file facts.

    `104` R-K. Four `(1)` twins on a 52-file corpus each got an independent,
    identical decision and no line said "same file as", while the fact had been
    on both members all along -- resolution G5 makes duplicate family a universal
    fact and P9's `duplicate_or_version` already reads it to type an edge. What
    was missing was the sentence.

    Families of ONE are dropped: a `duplicate_family` value a single file carries
    is a family with nothing to compare it to, and telling a person their file is
    a duplicate of nothing is worse than saying nothing.

    Over THIS scan's roster, for the reason `_protected_file_count` gives.
    """
    roster = {file_id for file_id, _hash in corpus_roster(conn, scan_run_id)}
    families: dict[str, list[str]] = {}
    for row in conn.execute(
            'SELECT ff.file_id AS file_id, v.canonical_value AS family '
            'FROM file_facts ff JOIN "values" v ON ff.value_id = v.value_id '
            'WHERE ff.field_key = ? AND ff.active = 1 '
            'AND ff.superseded_by IS NULL',
            (DUPLICATE_FAMILY_FIELD,)):
        if row["file_id"] in roster:
            families.setdefault(row["family"], []).append(row["file_id"])
    return {family: tuple(sorted(members))
            for family, members in families.items() if len(members) > 1}


def report(result: ProductionRun, names: dict[str, str], *, out=None,
           questions: Sequence = (), set_aside: Sequence = (),
           role_moment: Sequence[str] = (),
           roles_held: Sequence[str] = (),
           invite_freeze: bool = False,
           list_every_name: bool = False,
           show_protected: bool = False,
           locked: Mapping[str, str] = MappingProxyType({}),
           crossing: Mapping[str, str] = MappingProxyType({}),
           duplicates: Mapping[str, tuple[str, ...]] = MappingProxyType({}),
           reading_family: Sequence[str] = (),
           reaching: Mapping[str, tuple[str, ...]] = MappingProxyType({}),
           not_carried: Sequence = ()) -> tuple[str, ...]:
    """The run, in the order a person would ask about it.

    Four questions, in this order: what was left alone, what folders are being
    proposed, what happens to each file, and what this needs from you.

    The protected containers come FIRST and are never folded into a total.
    "Marked and counted, never opened" is only true if the count is somewhere the
    person reads, and a line at the bottom of a long report is not that. The
    grouping below never reaches this block -- count, name, path and sentence are
    what the rest of the report is shortened around, not with.

    `show_protected` is the person asking for the FILENAMES inside a protected
    group, which are summarised by default under the owner's 2026-09-02 ruling
    (`PROTECTED_SUMMARY`, and `planning/93-PROTECTED-DISCLOSURE-RULING.md`). It
    reaches nothing else: the protected containers block above is a different
    thing and is always whole, the protected review sets are named either way,
    and an ordinary group stays shortened to ten. It is not a verbosity flag.

    It defaults to `False`, and that is the one default in this function that is
    deliberately not `names`' rule. A forgotten `names` argument brought the
    id-only report back; a forgotten `show_protected` prints fewer of somebody's
    passport filenames than they asked for, which is the safe direction to fail.

    `names` is required rather than optional. A default would let the id-only
    report back in by nothing more than a forgotten argument.

    `questions` are P15's open ones, passed IN rather than read from the database
    here, because this function takes a finished run and a naming table and holds
    no connection -- and giving it one so it could ask a second part a question
    would make the report a place where new facts are discovered.

    `reading_family` is `104` R-90's, and arrives the same way: the domains the
    situation the person TYPED belongs among, read from the template library by
    the caller. It orders and folds what a reading question shows and removes
    nothing -- `_option_lines` says how, and an empty one prints what this
    function printed before it existed.

    `reaching` is `104` R-92's, and arrives the same way again: which files each
    question this run raised would actually settle, keyed by file id. It decides
    whether a blocked group's heading may promise "once you say what these are"
    and what is printed under it, and an empty one means no group can claim a
    gesture -- the safe direction, because the defect was claiming one.
    """
    out = out if out is not None else sys.stdout
    tree = result.tree.tree
    places = len(result.destinations)
    # `00`:100 -- "the canvas should make the difference between existing
    # structure and proposed structure visually clear". The person's own folders
    # are in this tree now, and counting them as PROPOSALS would tell someone who
    # has already organised half their disk that the product intends to build
    # seven new folders when it intends to build three.
    yours = sum(1 for node in tree.nodes if getattr(node, "existing_path", None))
    proposed = len(tree.nodes) - yours
    print(f"\nFolders in this plan: {len(tree.nodes)}. {proposed} proposed, "
          f"{yours} yours already. {places} of them "
          f"{'is' if places == 1 else 'are'} somewhere a file can go.", file=out)
    by_parent: dict[str | None, list] = {}
    for node in tree.nodes:
        by_parent.setdefault(node.parent_node_id, []).append(node)

    def draw(parent, depth):
        for node in by_parent.get(parent, ()):
            mark = "" if node.accepts_placement else "   [marked, not a destination]"
            # A terminal has no two styles, so the difference `00`:100 asks for
            # is carried in words. Only an `existing` node has a real path.
            if getattr(node, "existing_path", None):
                mark = f"   [yours already]{mark}"
            print(f"  {'  ' * depth}{node.display_label}{mark}", file=out)
            draw(node.node_id, depth + 1)

    draw(None, 0)

    # The residual areas this plan actually has, so the held-for-review line can
    # name what to type instead of leaving the person to guess it. `getattr` for
    # the same reason `existing_path` uses it below: this function takes a
    # finished run and reads it, and a fixture that models a node with fewer
    # fields must not turn a report into a traceback.
    areas = tuple(node.display_label for node in tree.nodes
                  if getattr(node, "node_role", None) == pv.RESIDUAL_ROLE)
    labels = {node.node_id: node.display_label for node in tree.nodes}
    # Only an `existing` node has one; `Node` refuses the field on every other
    # type, so this is exactly the set of destinations that are already folders.
    existing_paths = {node.node_id: getattr(node, "existing_path", None)
                      for node in tree.nodes}
    decisions = result.placement.decisions
    def _is_move(decision) -> bool:
        """A placement that would actually MOVE something.

        A file already sitting in a folder of the destination's name is not one:
        counting it as ready to file makes the headline promise an action the
        body then describes as "nothing to do".
        """
        label = (labels.get(decision.destination.node_id)
                 if decision.destination else None)
        return not all(_already_in(names.get(file_id, file_id), label)
                       for file_id in _files_of(decision))

    # "Ready to file" counts the files something may actually be DONE with, which
    # is the placements the review policy clears MINUS the ones already there.
    # Counting every `place` here put ten on this line for the four-role persona
    # when eight were waiting on the person -- the same overstatement
    # `PLACEMENT_WORDS` fixes in the headlines, and the two must not disagree.
    placed = sum(1 for d in decisions
                 if d.outcome == pv.PLACE and d.review_policy == pv.AUTO_ELIGIBLE
                 and _is_move(d))
    # And the ones the body then heads "Ready for you to approve". Found by
    # running the product: a run that had just filed a review set printed
    # "0 ready to file" one line above "Ready for you to approve, then file into
    # Review Later -- 6 files". The count was right by its own vocabulary and
    # the screen still contradicted itself -- the number a person reads
    # disagreeing with the list they read next, which is the same fault
    # `PLACEMENT_WORDS` fixed in the headlines and this line kept.
    #
    # Same three conditions as `placed` so the two can only ever differ about
    # the policy, and omitted entirely when it is zero, so every run that has no
    # approvals prints exactly the line it printed before.
    awaiting = sum(1 for d in decisions
                   if d.outcome == pv.PLACE
                   and d.review_policy == pv.REVIEW_REQUIRED and _is_move(d))
    # `104` R-92. The questions THIS REPORT PRINTS, by id. A question sitting in
    # the database that the screen does not show is not a gesture a person
    # reading the screen can find, so it may not be named as one -- and naming
    # the question object rather than the id is what lets the group print the
    # same answer lines the question block below prints.
    asked_here = {question.question_id: question for question in questions}
    sets_by_file: dict[str, list] = {}
    for item in result.placement.residual_sets:
        for file_id in item.member_file_ids:
            sets_by_file.setdefault(file_id, []).append(item)

    # One line per KIND of outcome, not one per file. Four files that stopped for
    # the same reason are four names and one reason, because the reason was one
    # fact the first time it was printed and stayed one fact the other three.
    members: dict[tuple, list[str]] = {}
    shielded: dict[tuple, bool] = {}
    # The batches holding each group, collected rather than re-derived, so one
    # batch is named on the screen exactly once however many of its files
    # reached this group.
    held_sets: dict[tuple, list] = {}
    held_seen: dict[tuple, set] = {}
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
        # Grouped by whether the file is already there, so the two never share a
        # heading: four files moving and one staying put is two facts.
        settled = all(_already_in(names.get(file_id, file_id), where)
                      for file_id in _files_of(decision))
        # And the stronger claim: not merely a folder of that name, but this one.
        real_path = (existing_paths.get(decision.destination.node_id)
                     if decision.destination else None)
        same_folder = bool(real_path) and all(
            _is_the_same_folder(names.get(file_id, file_id), real_path)
            for file_id in _files_of(decision))
        # A placement's folder is its whole answer; every other outcome owes the
        # person the sentence saying why it stopped.
        reason = "" if decision.outcome == pv.PLACE else decision.explanation
        # A file whose decision CAME OUT of residual review is not still being
        # held by the set that surfaced it. Printing the hold anyway would tell
        # someone who has just filed a set that nothing happened to it.
        held = tuple(item for item in sets
                     if getattr(decision, "residual", None) is None)
        # KEYED ON WHAT THE HOLD MEANS, NOT ON WHICH BATCH IT LANDED IN. §8.6
        # splits a set over the batch ceiling rather than truncating it, so one
        # hold over a real disk arrives as 420 sets differing only in the
        # `(i of n)` in their labels. Keying on the note -- which carries that
        # label -- made those 420 report groups, each repeating the same reason
        # and the same file-level explanation: 9,460 lines for 4,068 files, 236
        # screens, with the one block a person can act on at line 9,317.
        # `protected` stays in the key, so a protected hold never merges into an
        # ordinary one; two holds with different reasons still key apart.
        review = tuple(dict.fromkeys(
            (item.protected, item.reason_not_placed) for item in held))
        # THE DECISION'S OWN PROTECTION IS PART OF THE KEY. `shielded` below
        # is OR-ed over a group, so a group that held one protected file and
        # nine ordinary ones printed as "10 protected files, marked and
        # counted" with no names -- measured after `--answer home:.=...`, which
        # gives a folder's files one destination and one policy and so one
        # key. A protected file is marked and counted as ITSELF; it does not
        # take the syllabus beside it behind the summary with it.
        protected_here = _protected(decision, sets)
        # `104` R-D. A PASSWORD-PROTECTED ARCHIVE KEYS APART. Its decision reads
        # like every other unplaced file's -- "No legal destination cleared
        # §6.10's conditions" -- which is true and says nothing about the one
        # thing this file's record does know, so it was folded in with twelve
        # others and, past the ten-name cap, was not even printed. Section 2.5
        # marks it; the standing rule counts what is marked; and a count a person
        # cannot find the file behind is half a count.
        locked_here = tuple(sorted(
            file_id for file_id in _files_of(decision) if file_id in locked))
        # `104` R-N. A MOVE THAT CROSSES A HIGH-LEVEL FOLDER KEYS APART, because
        # it is not the same offer: `00`:20 makes crossing the person's own
        # choice, they have not made it, and `mutation/resolution.py` refuses
        # this one when the freeze reaches it. Printed beside moves that WILL
        # happen, with nothing telling the two apart, it is a proposal a person
        # cannot act on -- measured on a real Desktop file offered a home under
        # Downloads. The folder names are in the key so two sources do not merge
        # into one sentence naming one of them.
        crossing_here = tuple(sorted({
            crossing[file_id] for file_id in _files_of(decision)
            if file_id in crossing}))
        # `104` R-92. WHICH QUESTIONS ON THIS SCREEN REACH THESE FILES, in the
        # key, because two files waiting on different things are two facts. The
        # five files under "Would go into lecture, once you say what these are"
        # were two that a printed question would settle and three that nothing
        # would, and one heading covering both is what made the sentence a
        # promise the report could not keep for three of them.
        #
        # Restricted to the questions this report is PRINTING. A question that
        # exists in the database and is not on the screen reaches nothing a
        # person reading the screen can type.
        reaching_here = tuple(sorted({
            question_id for file_id in _files_of(decision)
            for question_id in reaching.get(file_id, ())
            if question_id in asked_here}))
        key = (decision.outcome, where, reason, review,
               decision.review_policy if decision.outcome == pv.PLACE else None,
               settled, same_folder, protected_here, locked_here, crossing_here,
               reaching_here)
        members.setdefault(key, []).extend(_files_of(decision))
        shielded[key] = shielded.get(key, False) or protected_here
        marks = held_seen.setdefault(key, set())
        for item in held:
            if id(item) not in marks:
                marks.add(id(item))
                held_sets.setdefault(key, []).append(item)

    # Every file id this function PRINTS BY NAME. `apply_run.freeze` reads it
    # to decide what a freeze may approve, so it is collected where the printing
    # happens rather than re-derived from the same grouping afterwards: a second
    # copy of this loop would be a second answer to "what was on the screen",
    # and the two would drift.
    named: list[str] = []
    rank = {outcome: index for index, outcome in enumerate(OUTCOME_WORDS)}
    ordered = sorted(members, key=lambda key: (
        # Protected LAST. `00`:201 -- "a summary such as '11 protected identity
        # records' may be safe to show, while a visible list of passport filenames
        # on a shared screen may not be". Ranking them first opened every report
        # over a real disk with the person's passport, tax return and medical
        # records by name, above their homework.
        #
        # This is NOT the rule below it. `shielded` still lists a protected group
        # IN FULL and elides nothing -- that is the standing "marked, counted,
        # never silently omitted" rule and it is untouched. Being last and being
        # summarised away are different things, and only the first is changed here.
        shielded[key], rank.get(key[0], len(rank)), key[1] or "", key[2]))

    # `104` R-114. WHAT THIS SCREEN HAS ALREADY SAID IN FULL, and where.
    #
    # Fresh run on a 52-file folder: 430 lines, of which the eight-line "Nothing
    # on this screen says what these are" explanation was printed once per group
    # in that state -- six times -- and the "Held for review as ... this plan has
    # nowhere to put them yet" block eight times, each followed by the same list
    # of review sets. Every printing was honest and a person stops reading at the
    # third. This is the rule the grouping loop above already follows for a
    # file-level explanation ("one line per KIND of outcome, not one per file"),
    # applied to the paragraphs under the groups instead of the ones inside them.
    #
    # KEYED ON THE RENDERED BLOCK, so a block is folded only when every line of
    # it has already been printed word for word. Two groups held for different
    # reasons, or naming different review sets, or offered different commands,
    # are two facts and both are printed in full: what collapses is a repeat and
    # nothing else. The value is the handle of the group that carried it, so the
    # one line left behind says where the paragraph is.
    already_said: dict[tuple[str, ...], str] = {}

    def say(block: Sequence[str], *, handle: str, again: str) -> bool:
        """A shared paragraph, in full the first time and pointed at after.

        `_role_lines`' convention holds inside the block: a line that begins with
        a space is a line the person is meant to paste and is printed exactly as
        it is. The line that REPLACES a repeat is prose and carries no command --
        the command is up where the block is, which is what it says.

        True when the block was printed IN FULL, which `104` R-122 reads to
        decide whether a SECOND block below it needs saying: a group already
        holding a one-line pointer at another group is pointed at a place that
        carries both, and a second pointer under the first would be a repeat of
        the kind this function exists to remove.
        """
        if not block:
            return False
        printed = tuple(block)
        first = already_said.get(printed)
        if first is None:
            already_said[printed] = handle
            for line in printed:
                print(line if line.startswith(" ")
                      else _wrapped(line, indent="    "), file=out)
            return True
        print(_wrapped(again.format(first=first), indent="    "), file=out)
        return False

    print(f"\nFiles: {len(decisions)} decided, {placed} ready to file"
          + (f", {awaiting} waiting for you to approve" if awaiting else ""),
          file=out)
    for key in ordered:
        outcome, where, reason, review, policy, settled, same_folder, _, \
            locked_here, crossing_here, reaching_here = key
        files = sorted(members[key], key=lambda f: names.get(f, f))
        # A placement's headline comes from its REVIEW POLICY, because that is
        # what says whether anything may happen to the file. An unknown policy
        # falls back to the outcome's word rather than to silence, for the same
        # reason `OUTCOME_WORDS` prints an unknown outcome's own name: a gap in
        # this deployment's vocabulary must never become a file that vanished.
        words = (SAME_FOLDER if same_folder
                 else ALREADY_THERE if settled else PLACEMENT_WORDS)
        sentence = words.get(policy) if outcome == pv.PLACE else None
        # `104` R-92, on the heading rather than under it. "Once you say what
        # these are" is a promise, and it is kept only where the screen carries
        # a gesture that reaches these files. Where it does not, the sentence
        # says so and the note below says what they are waiting on instead.
        if (outcome == pv.PLACE and policy == pv.BLOCKED_PENDING_USER
                and not reaching_here):
            sentence = NOTHING_SAYS_WHAT_THESE_ARE[
                "same_folder" if same_folder
                else "already_there" if settled else "moving"]
        if sentence is not None and where:
            heading = sentence.format(where=where)
        else:
            heading = OUTCOME_WORDS.get(outcome, outcome)
            if where:
                heading = f"{heading} into {where}"
        plural = "" if len(files) == 1 else "s"
        if crossing_here:
            # ON THE HEADING, not in a footnote: the heading is what a person
            # reads to decide whether to freeze, and this branch will not move
            # until they answer `00`:20's third question.
            #
            # Joined with "and" when the heading already carries a clause, so a
            # file waiting on two answers reads as one sentence rather than as
            # two headings run together. `, once ` and not `, once you `:
            # `104` R-92's heading for a file nothing on the screen reaches says
            # "once something can say what these are", and testing for the
            # narrower phrase appended a second comma clause to it.
            heading = (f"{heading} and once you allow moves across folders"
                       if ", once " in heading
                       else f"{heading}, once you allow moves across folders")
        print(f"\n  {heading} -- {len(files)} file{plural}", file=out)
        # `104` R-114's handle for this group: what a person calls it when they
        # look back up the screen for a paragraph that was printed once. The
        # DESTINATION when there is one, because "the CS3134 group" is how
        # somebody says it out loud, and the heading itself when there is not --
        # a group of files going nowhere has no folder name to be called by, and
        # "the None group above" would send them looking for nothing.
        handle = (f"{where} group above" if where
                  else f'group above headed "{heading}"')
        # `list_every_name` is set by the freeze run and by nothing else. The
        # owner ruled that a freeze IS the person's approval, and an approval
        # covers what they were shown -- so under the ordinary ten-name cap the
        # eleventh file in a group could never be approved by any gesture that
        # exists, because the next run groups it the same way and caps it again.
        # A freeze run is long over a big folder. That is the cost of the
        # ruling, and the alternative is a person approving a line that says
        # "...and 4,058 more".
        #
        # It widens the PROTECTED group not at all, and the protected clause is
        # left exactly as it was found. A freeze cannot approve protected
        # material -- `apply_run.freeze` holds every protected placement before
        # it reaches an approval -- so naming more of it than the ordinary
        # report does would buy nothing and would fight the ruling that
        # protected filenames sit behind `--show-protected`. Whatever that work
        # makes of the first clause, this one does not reach into it.
        if shielded[key] and not show_protected:
            # The owner's 2026-09-02 ruling, and it is the clause the freeze
            # patch above deliberately left room for: the count and the command,
            # and no filenames. `PROTECTED_SUMMARY` carries the reasoning and
            # points at the planning note, because this contradicts half of `00`
            # on purpose and a reader who finds only one half will put it back.
            # An indented line is printed verbatim: it is a command.
            #
            # `named` is untouched here, and that is not an omission. Nothing
            # printed under this clause may ever be approved by a freeze, which
            # is the same conclusion the `not shielded[key]` guard below reaches
            # by the other road.
            # NOTHING WAS NAMED, so nothing may be named about it below either.
            shown_here = ()
            for line in PROTECTED_SUMMARY:
                said = line.format(count=len(files), plural=plural)
                print(said if said.startswith(" ")
                      else _wrapped(said, indent="    "), file=out)
        else:
            # EVERY one when it was asked for. A `--show-protected` that listed
            # the first ten and counted the rest would be the silent omission the
            # standing rule forbids, wearing the fix's clothes.
            listed = (files if shielded[key]
                      else files if list_every_name
                      else files[:NAMES_LISTED_PER_GROUP])
            if not shielded[key]:
                # And what a freeze may approve never includes a protected file,
                # so a protected name does not enter this set even on the day the
                # first clause prints one -- which is now every day somebody
                # types `--show-protected`. A flag about what is on the SCREEN
                # may not widen what a gesture is allowed to MOVE. The exclusion
                # is here as well as in `freeze` because two independent refusals
                # are what "never" means.
                named.extend(listed)
            shown_here = listed
            for file_id in listed:
                print(f"    {names.get(file_id, file_id)}", file=out)
            rest = len(files) - len(listed)
            if rest:
                print(_wrapped(
                    f"...and {rest} more, counted here rather than listed one by "
                    "one so that the list stays shorter than the folder it "
                    "describes. None of these is protected material: that is "
                    "counted in its own block, with the way to see it printed "
                    "there -- summarised, but never silently omitted.",
                    indent="    "),
                    file=out)
        if reason:
            print(_wrapped(f"Same reason for each: {reason}", indent="    "),
                  file=out)
        # `104` R-D, said where the file is listed and not only at the top. The
        # member NAMES are not printed: a locked archive's members can be
        # `passport.pdf`, which is the list `00`:201 is about.
        # `104` R-K. SAID OVER THE NAMES THIS GROUP PRINTED, and over no others.
        # A duplicate line naming a file the screen is withholding would hand
        # back exactly what `PROTECTED_SUMMARY` holds, and one naming a file
        # inside the "...and N more" fold would name what the fold exists not to
        # name. So `listed` is the whole world here, and a family with fewer
        # than two of its members on this screen says nothing -- which is
        # honest: what the person can act on is what they can see.
        for family in sorted({
                family for family, members in duplicates.items()
                if len(set(members) & set(shown_here)) > 1}):
            together = sorted(
                names.get(file_id, file_id)
                for file_id in duplicates[family] if file_id in shown_here)
            elsewhere = len(duplicates[family]) - len(together)
            also = (f" {elsewhere} more file(s) in this plan have the same "
                    f"bytes and are listed elsewhere in this report."
                    if elsewhere else "")
            print(_wrapped(
                f"{' and '.join(together)} are the same bytes, not two "
                f"documents. Keeping one is probably what you want; nothing "
                f"here deletes either, and both are filed the same way until "
                f"you say otherwise.{also}", indent="    "), file=out)
        if crossing_here:
            where_from = ", ".join(crossing_here)
            print(_wrapped(
                f"These are in {where_from} and this folder is not, so filing "
                f"them here would move them out of the folder they are in. "
                f"`--may-cross-folders` is the permission for that and it was "
                f"not given, so a freeze refuses this branch and nothing moves. "
                f"Run the same command with `--may-cross-folders` to allow it, "
                f"or leave it off and these stay where they are.",
                indent="    "), file=out)
        for file_id in locked_here:
            print(_wrapped(
                f"{names.get(file_id, file_id)} is password-protected: "
                f"{locked[file_id]}. It is counted with the protected material "
                f"at the top of this report: a locked archive is marked rather "
                f"than forced open, so nothing inside it was read and nothing "
                f"about it was assembled for a model.",
                indent="    "), file=out)
        if outcome == pv.PLACE and policy == pv.BLOCKED_PENDING_USER:
            asked = tuple(asked_here[question_id]
                          for question_id in reaching_here)
            note = _how_to_say_what_these_are(asked, reading_family)
            if asked:
                # THIS GROUP'S OWN FACTS AND NEVER FOLDED. The claim these lines
                # make is that these answers reach THESE files, which is `104`
                # R-92's whole subject: two groups whose answer lines happen to
                # render alike are still two claims about two sets of files, and
                # replacing one with a pointer at the other would put a sentence
                # on the screen that is true of a group other than the one it
                # sits under. That is the defect R-92 fixed, arriving by way of
                # a shortening.
                for line in note:
                    print(line if line.startswith(" ")
                          else _wrapped(line, indent="    "), file=out)
            else:
                # And the other branch is one paragraph, word for word, however
                # many groups nothing on the screen reaches. `104` R-114.
                say(note, handle=handle,
                    again="Waiting on the same thing as the {first}, and what "
                          "to do about it is printed there.")
        elif reaching_here:
            # `104` R-37. A held group under a branch whose situation is not yet
            # answered is reached by that branch's question, and the answer
            # lines are printed beside the files they reach for R-92's reason:
            # the gesture that moves these files forward is on this screen, and
            # a person should not have to find it. Only the situation question:
            # every other kind prints beside the placements it blocks, above.
            asked = tuple(asked_here[question_id]
                          for question_id in reaching_here
                          if kind_of(question_id) is SITUATION_KIND)
            for line in _how_to_say_what_these_are(asked, reading_family) if asked else ():
                print(line if line.startswith(" ")
                      else _wrapped(line, indent="    "), file=out)
        # `_role_lines`' convention: a line that begins with a space is a line
        # the person is meant to paste, and it is printed exactly as it is.
        # THE COUNT TRAVELS WITH THE POINTER. "N review sets of it have files
        # under this heading" is a fact about THIS heading -- it is the sentence
        # that stopped the screen claiming a total it could not see -- so it is
        # said again rather than folded away with the paragraph that carries it.
        # A block only folds when it is identical, so the number is the same
        # number; being the same is not a reason to stop saying it under the
        # heading it is about.
        under_here = len(held_sets.get(key, ()))
        # `104` R-124. `reason` is this group's "Same reason for each" line and
        # is empty exactly where that line was not printed, so the flag is the
        # screen's own record of whether the reason has been said.
        note, closing = _review_note(held_sets.get(key, ()), areas,
                                     reason_already_said=bool(reason))
        said_in_full = say(note, handle=handle,
            again=("Held for review; the set and the command are under the "
                   "{first}." if under_here < 2 else
                   f"Held for review, and {under_here} review sets of it have "
                   "files under this heading; they are named there with the "
                   "command, under the {first}."))
        # `104` R-122. WHETHER THE PLAN HAS ANYWHERE TO PUT A HELD SET is one
        # fact about the plan, so it is said in full under the first held group
        # that has one and pointed at under every later one. The set's name and
        # its `--send-set` line stay above, under every group, because those are
        # the group's own facts and the name is what a person types.
        #
        # Two sentences and two pointers: with no residual area the sentence says
        # how to make one, and with more than one it names the others. A single
        # pointer worded to fit both would be true of neither.
        #
        # NO `{first}` HANDLE HERE, and R-114's own measurement is why. A held
        # group is usually a group with no destination, so its handle is the
        # whole heading -- `group above headed "Waiting for you to choose where
        # these go"` -- and a pointer carrying it wraps to two lines, which is
        # exactly the length of the sentence it replaced: measured on a 60-file
        # corpus, folding with the handle saved nothing at all, and with two
        # `--residual` areas it replaced a one-line sentence with a two-line
        # pointer and made the screen LONGER. A fold that does not shorten is
        # not a fold.
        #
        # "The first held group above" is EXACT and not approximate. `ordered`
        # sorts on `shielded` first, so every protected group is last; a
        # protected file keys its own group through `protected_here`, so the
        # first group on the screen holding anything is holding an unprotected
        # set; and nothing is in `already_said` when it is reached, so it prints
        # its note in full and carries the sentence. There is no screen on which
        # the first held group is not the one this line points at.
        #
        # Skipped where the block above it FOLDED, because that group is already
        # carrying one line pointing at a group that says both.
        if said_in_full:
            say(closing, handle=handle,
                again=("Sent the same way as the first held group above, once "
                       "an area exists."
                       if not areas else
                       "The other areas are named under the first held group "
                       "above."))

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

    if questions:
        # BEFORE the defaulted decisions, and after the files, because this is the
        # one block the person can act on. `66` §12: a question must "explain the
        # exact decision it unlocks" and "state what it will not affect", and §14
        # requires the person to see "why the question arose" -- so all three are
        # printed, every time, rather than being available somewhere else.
        # TWO SECTIONS, because these are two different things to a person and
        # printing them together made one look like the other.
        #
        # A blocked reading STOPS something: until it is answered those files are
        # not classified and go nowhere. A nesting offer stops nothing -- the
        # branch has a shape either way, and the question is `00`:78's "which of
        # these shapes do you want", which the design assigns to the user rather
        # than to the engine. Under one heading, "Questions only you can answer",
        # the offer read as a blockage and the run looked stuck when it was not.
        #
        # Discriminated on SCOPE KIND, which already carries the distinction:
        # a `branch:` question is about the shape of one branch and always has a
        # default; every other kind is about what something MEANS, and meaning is
        # what placement is blocked on.
        # `104` R-37: a SITUATION question shares the branch scope and is not an
        # offer. Until it is answered the files under that branch are asked
        # nothing and its folders cannot be designed, which is a blockage.
        def _blocks(question) -> bool:
            return (not question.scope.startswith(f"{SCOPE_BRANCH}:")
                    or kind_of(question.question_id) is SITUATION_KIND)

        blocking = [q for q in questions if _blocks(q)]
        offers = [q for q in questions if not _blocks(q)]

        def ask(question) -> None:
            print(f"\n  {question.prompt}", file=out)
            print(_wrapped(question.evidence_context, indent="    "), file=out)
            for line in _option_lines(question, reading_family):
                print(line, file=out)
            print(_wrapped(question.unlocks, indent="    "), file=out)
            print(_wrapped(question.will_not_do, indent="    "), file=out)

        if blocking:
            print("\nQuestions only you can answer:", file=out)
            for question in blocking:
                ask(question)
        if offers:
            print("\nYou can change how this is organised "
                  "(it is already decided; this is yours to overrule):", file=out)
            for question in offers:
                ask(question)

    if role_moment:
        # `80` §3 (R1): the self-description question is "triggered by the first
        # genuinely ambiguous file", never by first run -- so it belongs directly
        # under the decisions this run could not settle, which are the evidence
        # that it is needed. Nothing here decides whether to print it:
        # `role_moment_lines` returns nothing unless `role_declaration_is_due`
        # says the moment has arrived, and R2's once-only friction budget lives
        # inside that call rather than in a condition this file could forget.
        print("", file=out)
        _role_lines(role_moment, out=out)

    if roles_held:
        # `80` §4 (R6): "a light, editable settings panel the person can glance at
        # and adjust anytime, not a one-time gate they went through and now can't
        # see again." AFTER the set-aside block and before the defaults, because
        # this is the one part of the report that is about the person rather than
        # about their files, and it is where they look to change something.
        print("", file=out)
        _role_lines(roles_held, out=out)

    if set_aside:
        # NOT the question again. §14 makes "skip for now" first-class and §12
        # forbids the pressure of re-asking, so the prompt, the evidence and the
        # options all stay gone -- what comes back is the ID, because that is
        # what `revoke` needs and it was printed nowhere else. A reversible
        # decision whose reversal is unreachable is not reversible.
        print("\nSet aside by you, and still here if you want them back:",
              file=out)
        for question in set_aside:
            print(f"      --answer {_typable(question, 'revoke')}"
                  f"   Ask me this again", file=out)

    print("\nDecisions made for you, because nobody was at the screen to ask:",
          file=out)
    for question, answer in DEFAULTED_DECISIONS:
        print(_wrapped(f"{question} -- {answer}", indent="    ", first="  - "),
              file=out)

    if not_carried:
        # NAMED, not applied. The label is the words the person typed; the date
        # is trimmed to the day because a microsecond timestamp is a machine's
        # answer to "when". No node id and no choice token: `node_id` is an
        # internal address and `choice` is a vocabulary member, and neither is
        # something a person has ever seen on this screen.
        print("\nWhat you decided on an earlier run, which this plan does not "
              "carry:", file=out)
        for decision in not_carried:
            print(_wrapped(
                f'"{decision.label}", decided {decision.decided_at[:10]}. A '
                "review set belongs to the plan it was surfaced in and this run "
                "built a new one, so your answer was not applied again and "
                "nothing was filed from it. The sets above are this run's.",
                indent="    ", first="  - "), file=out)

    print(f"\nNothing was moved.\nPlan version: {tree.plan_version_id}  "
          f"(the name this proposal is saved under)", file=out)
    if invite_freeze:
        # A gesture nothing on screen names is a gesture nobody finds. This says
        # what freezing does and what it does NOT do, because freezing is the
        # point at which a person starts wondering whether their files are about
        # to move.
        print(_wrapped(
            "Run the same command again with --freeze to turn this proposal "
            "into a plan you can move files with. Freezing moves nothing "
            "either: what it prints is one line per branch saying exactly what "
            "to type to move that branch, and you can move one branch, "
            "several, or all of it.", indent="  "), file=out)
    return tuple(named)


def _record_cloud_decision(args, decision: str, *, out) -> int:
    """Write one decision and say what it means, without running a scan.

    Its own function because the withdrawal path shares almost nothing with a run:
    no situation, no label, no catalogue, no scan roots -- and deliberately no
    `is_dir` check, so a folder that has been deleted can still have its consent
    withdrawn.
    """
    from datetime import datetime, timezone

    directory = args.directory.expanduser().resolve()
    # EVERY folder named, not only the first. Consent is recorded per folder,
    # and `--enable-cloud` on a run with `--also-read` records one per source --
    # so a withdrawal that reached only the first would leave the second still
    # sending, which is the worst possible outcome for a person who typed the
    # word "disable" and read a sentence saying it was off. No `is_dir` check
    # here either, for the reason above: a deleted folder's consent is still
    # withdrawable.
    folders = list(dict.fromkeys(
        [directory, *(Path(raw).expanduser().resolve()
                      for raw in args.also_read)]))
    database = args.database or (Path.cwd() / "database-agent-plan.sqlite")
    try:
        conn = open_database(database, scan_roots=folders)
    except DatabaseInsideCorpus as refusal:
        print(f"\n{refusal}", file=out)
        return 2
    try:
        for folder in folders:
            record_cloud_consent(
                conn, corpus_root=str(folder), decision=decision,
                user_id=args.user,
                decided_at=datetime.now(timezone.utc).isoformat())
        conn.commit()
    finally:
        conn.close()
    for folder in folders:
        print(f"\nCloud sending is off for {folder}.", file=out)
    print(_wrapped(
        "Nothing further from this folder will be sent to a model. What earlier "
        "runs already sent cannot be recalled, and the record of when it was "
        "enabled is kept rather than erased -- so the question of what was "
        "authorised, and when, stays answerable.", indent="  "), file=out)
    return 0


def _volume_of(path: Path) -> str:
    """Which device a path is on, asking the nearest ancestor that exists.

    A destination directory is usually not there yet -- that is the point of a
    plan -- so `stat` on it would raise. The nearest existing ancestor is on the
    same volume by construction, because a mount point is a directory.
    """
    import os

    cursor = path
    while not cursor.exists() and cursor != cursor.parent:
        cursor = cursor.parent
    return str(os.stat(cursor).st_dev)


ROLE_READ = "a folder to read"
ROLE_ROOT = "a place a branch could live in"


def _folder_landscape(directory: Path, also_read: Sequence[Path],
                      could_live_in: Sequence[Path], *, out
                      ) -> tuple[list[Path], list[Path]] | None:
    """`00`:20's other two answers, resolved and checked. `None` means refused.

    Two rules, and neither is a style choice.

    **A folder that is not there is a sentence, not a traceback.** The positional
    argument has had that sentence since the first day; a person who mistypes the
    second folder is making the same mistake and deserves the same answer.

    **A path may not be both.** §21 spends a paragraph insisting that a root is
    context and not permission, so a folder named as both the material and the
    landscape is a person asking for two incompatible things at once -- and which
    one they meant cannot be read off the command. Guessing would resolve it
    silently in whichever direction the code happened to be written, which is
    exactly the way a root turns into permission. It is refused, with both paths
    named, so the person can say which they meant. The same check catches a
    folder nested inside another folder to read, where the cost is quieter but
    real: it would be walked twice and every file in it counted twice.

    Duplicates are dropped rather than refused: naming the same folder twice is
    not two answers in conflict, it is one answer typed twice.
    """
    out = out if out is not None else sys.stdout
    named: list[tuple[Path, str]] = [(directory, ROLE_READ)]
    for group, role in ((also_read, ROLE_READ), (could_live_in, ROLE_ROOT)):
        for raw in group:
            path = Path(raw).expanduser().resolve()
            if not path.is_dir():
                print(f"{path} is not a folder", file=out)
                return None
            if any(path == seen for seen, _ in named):
                continue
            named.append((path, role))
    for path, role in named:
        for other, other_role in named:
            if other == path or path not in other.parents:
                continue
            print(f"\n{path} is inside {other}, and this run was given them as "
                  f"two different things: {other} as {other_role} and {path} as "
                  f"{role}. One folder cannot be both the material being "
                  f"organised and a place a branch could eventually live in, "
                  f"and which of the two you meant is not something this "
                  f"command will guess. Name one or the other.", file=out)
            return None
    return ([path for path, role in named[1:] if role == ROLE_READ],
            [path for path, role in named if role == ROLE_ROOT])


def _typed(directory: Path, database: Path | None, tail: str) -> str:
    """One command line a person can paste, with the database named if it was.

    `84` §6: what the screen tells a person to type has to be true. A run given
    `--database` that printed an `--apply` line without it would send the person
    at a different database -- which holds no frozen plan, so the honest-looking
    answer would be "nothing to move".
    """
    parts = ["database-agent", shlex.quote(str(directory))]
    if database is not None:
        parts += ["--database", shlex.quote(str(database))]
    return " ".join(parts) + " " + tail


def _move_frozen_files(args, *, moving: bool, branches: Sequence[str],
                       everything: bool, out) -> int:
    """`--apply` and `--undo`: act on the frozen plan, running no pipeline.

    Its own function because it shares almost nothing with a run: no situation,
    no label, no catalogue, no scan, no model. What it reads is the plans
    `--freeze` wrote, which are `00`:156-170's record of what was approved.
    """
    from datetime import datetime, timezone

    directory = args.directory.expanduser().resolve()
    database = args.database or (Path.cwd() / "database-agent-plan.sqlite")
    try:
        conn = open_database(database, scan_roots=[directory])
    except DatabaseInsideCorpus as refusal:
        print(f"\n{refusal}", file=out)
        return 2
    print(f"Plan database: {database}", file=out)
    try:
        create_mutation_schema(conn)
        # `--apply` opens its own connection and runs no pipeline, so nothing
        # else on this path has created P13's tables. A database frozen by an
        # older build has none of them, and the approval lookup below would meet
        # a missing table rather than an unapproved plan.
        create_review_schema(conn)
        plans = frozen_plans(conn)
        if not plans:
            # NO command is printed here, deliberately. Freezing needs the
            # situation and the label, and this invocation was not given
            # either -- so any line printed would carry a placeholder, and a
            # line with a placeholder in it is not a line a person can paste.
            # `84` §6: what the screen tells a person to type has to be true.
            print(_wrapped(
                "There is no frozen plan for this folder yet, so there is "
                "nothing to move and nothing to put back. Run the ordinary "
                "command over this folder again with --freeze added -- the one "
                "with your --situation and --label on it. Freezing still moves "
                "nothing; it prints the lines that do.", indent="  "), file=out)
            return 2

        versions = sorted({plan.organization_plan_version for plan in plans})
        nodes = tuple(node for version in versions
                      for node in nodes_for_version(conn, version))
        legal = frozenset(node.node_id for node in nodes
                          if node.accepts_placement)

        if everything:
            selected = frozenset(node.node_id for node in nodes)
        else:
            try:
                selected = branches_named(branches, nodes=nodes)
            except BranchRefused as refusal:
                print(f"\n{refusal}", file=out)
                return 2

        names = file_names(conn, directory)
        counter = count()

        def now() -> str:
            return datetime.now(timezone.utc).isoformat()

        def mint_id() -> str:
            return f"{uuid.uuid4().hex}:{next(counter)}"

        if moving:
            chosen = plans_under(plans, selected)
            filed = already_applied(conn, chosen)
            outcome = apply_selected(
                conn, tuple(plan for plan in chosen
                            if plan.plan_id not in filed),
                legal_destination_ids=legal,
                source_root=directory, destination_root=directory,
                # No cloud-sync conflict detection is built, so none is claimed:
                # `conflict_copies` returning nothing says "none was found", and
                # `00`:174's sync-conflict pause is a NAMED GAP, not a check
                # that ran and passed.
                extra_protected=None, conflict_copies=lambda path: (),
                dataless_of=lambda path: False,
                # `mutation.approval`: absence of a `ReviewApproval` IS the
                # refusal. The record now exists -- `--freeze` is the surface
                # that collects it (the owner's ruling, 2026-09-02) -- so this
                # reads the rows back instead of returning `None` forever. A
                # plan nobody approved still gets `None`, which is the refusal
                # and not a gap in the wiring.
                approval_for=approval_reader(conn),
                constraints=_FILESYSTEM_CONSTRAINTS,
                normalize_filename=lambda name: unicodedata.normalize(
                    _FILESYSTEM_CONSTRAINTS.unicode_form, name),
                unruled_cross_volume_sentence=_CROSS_VOLUME_UNRULED_SENTENCE,
                halt_on=_HALT_ON, scan_state="included", materialized=True,
                component_version=COMPONENT_VERSION, user_id=args.user,
                now=now, mint_id=mint_id)
            conn.commit()
            for line in apply_lines(
                    outcome, names=names,
                    # `104` R-117. IN `chosen`'S ORDER, which `plans_under` now
                    # makes destination-then-name -- the same order as the two
                    # lists printed above this one. Sorting the FILE IDS put
                    # this block in the order of a uuid, which is stable and
                    # says nothing: a person reading three listings on one
                    # screen reads them in one order or in none.
                    already_filed=tuple(plan.file_id for plan in chosen
                                        if plan.plan_id in filed),
                    undo_command=_typed(
                        directory, args.database,
                        " ".join(f"--undo {shlex.quote(name)}"
                                 for name in branches)
                        if branches else "--undo-everything")):
                print(line, file=out)
            return 0

        # `--undo-everything` takes EVERY entry, with no node filter. The
        # freeze report promises that anything already filed under an earlier
        # proposal "stays filed and can still be taken back", and the real
        # pipeline mints a new plan version on every run -- so an entry from a
        # superseded proposal has node ids that are in no current branch and
        # filtering by them would silently skip exactly the files the sentence
        # was about. `--undo BRANCH` still resolves against the current version,
        # because resolving a label across every version a database has ever
        # held would make every label ambiguous with its own older self.
        entries = [entry for entry, node_id in applied_entries(conn)
                   if everything or node_id in selected]
        by_entry = {entry.entry_id: entry.file_id for entry in entries}
        outcome = take_back(
            conn, entries, constraints=_FILESYSTEM_CONSTRAINTS,
            normalize_filename=lambda name: unicodedata.normalize(
                _FILESYSTEM_CONSTRAINTS.unicode_form, name),
            scan_state="included", materialized=True,
            component_version=COMPONENT_VERSION, user_id=args.user,
            now=now, mint_id=mint_id)
        conn.commit()
        for line in undo_lines(outcome, names=names, file_of=by_entry):
            print(line, file=out)
        return 0
    finally:
        conn.close()


def _replay_bundle(args, *, out) -> int:
    """§8.5's replay, over a bundle a run already recorded. Reads no folder.

    Its own function for the reason `_record_cloud_decision` is: it shares almost
    nothing with a run. No situation, no label, no catalogue, no scan roots and
    no `is_dir` check -- a bundle is evaluable after the folder it came from has
    been deleted, which is most of the point of sealing one.

    Every policy-bearing value P2 needs is chosen HERE and nowhere below. The
    ceilings are the set this database was given, snapshotted from P1's budget
    table rather than restated. The two run disables are what this deployment
    actually wires: `p8_run_call=None` and `EmbeddingsOff()`, so both are off,
    and saying so on the manifest is what lets a later comparison tell a run with
    a model from one without. Four of the six version axes are None because this
    deployment wires no graph algorithm, no model and no placement scorer
    version, and a made-up string there would name a version nobody shipped.

    It prints no aggregate and computes none: §8.5, "a single overall 'accuracy'
    number hides the mechanism that needs repair."
    """
    from database_agent.budget import all_ceilings
    from eval_harness.bundle import extraction_runs
    from eval_harness.comparison import compare_runs, get_comparison
    from eval_harness.driver import evaluate_bundle
    from extractors.stage_output import extractor_versions

    database = args.database or (Path.cwd() / "database-agent-plan.sqlite")
    # No `scan_roots`: nothing is scanned, so there is no root the database could
    # be inside of.
    conn = open_database(database)
    print(f"Plan database: {database}", file=out)
    try:
        _bootstrap(conn)
        held = recorded_bundles(conn)
        if not args.replay:
            print("\n--replay needs the bundle to replay. It is never guessed "
                  "and never the most recent one: two bundles are two different "
                  "corpora, and picking one for you would report on files you "
                  "did not name.", file=out)
            if not held:
                print("\nThis plan database has recorded no bundle yet.",
                      file=out)
            else:
                print("\nBundles this plan database holds:", file=out)
                for record in held:
                    # The name first when there is one, because it is what a
                    # person typed and what they will type again. An UNNAMED
                    # bundle -- every one the ordinary run seals -- is listed
                    # without a name rather than omitted, so someone hunting for
                    # their recording can see the other rows exist too.
                    named = ("--record " + record["name"] if record["name"]
                             else "not recorded under a name")
                    print(f"  {record['bundle_id']}   {record['created_at']}"
                          f"   {named}", file=out)
            return 2
        bundle_id = resolve_bundle(conn, args.replay)
        if bundle_id is None:
            # Refused rather than ignored, exactly as an unknown `--answer` is.
            # A name and an id are both accepted and neither is guessed at: there
            # is no nearest match and no most recent, because two bundles are two
            # different corpora.
            print(f"\n{args.replay!r} is not the name or the id of a sealed "
                  f"bundle in this plan database. Run --replay with nothing "
                  f"after it to see the ones it holds.", file=out)
            return 2

        # Derived from what the bundle RECORDED, not from this machine: §8.5
        # re-processes a bundle, so the tuple must describe the runs inside it.
        # `extractor_versions` REFUSES a bundle holding one extractor at two
        # versions rather than resolving it -- its own words are that "a caller
        # comparing two extractor versions is comparing two runs" -- and that is
        # a real bundle, produced by re-scanning a corpus after an extractor
        # upgrade. Caught here so it is a sentence rather than a traceback, and
        # BEFORE `evaluate_bundle`, so no half-opened run is left behind.
        try:
            versions = extractor_versions(extraction_runs(conn, bundle_id))
        except ValueError as refusal:
            print(f"\nThis bundle cannot be replayed as one run: {refusal}",
                  file=out)
            print(_wrapped(
                "It records one extractor at two versions, and §8.5's version "
                "tuple holds one version per extractor -- so what is in it is "
                "two runs to compare, not one to replay. Recording each version "
                "into its own bundle is what makes the comparison the thing "
                "§8.5 asks for.", indent="  "), file=out)
            return 2

        # AFTER the id and the tuple are both known good, so neither a mistyped
        # id nor an unreplayable bundle ever opens a run.
        baseline = bundle_baseline(conn, bundle_id)
        driven = evaluate_bundle(
            conn, bundle_id,
            version_tuple=dict(
                extractor_versions=versions,
                graph_algorithm_version=None, prompt_fingerprint=None,
                model_identifier=None, template_library_version=None,
                placement_scorer_version=None,
                # I4's tiers this deployment resolves under: `_resolver` is built
                # for filesystem+native and for filesystem+native+ocr. `llm` is
                # absent because no model is wired, which is the same fact the
                # disable below records.
                analysis_tiers_enabled=["filesystem", "native", "ocr"]),
            budget_ceilings=all_ceilings(conn),
            # `embeddings_enabled` is P9's GROUPING channel and is still off:
            # §4.4's similarity retrieval needs a threshold, channel weights and a
            # compatibility predicate that nothing has measured. The RECOGNITION
            # vectors are a different consumer -- `--semantic-model` computes and
            # stores them through P9's own `ensure_file_embedding` -- so
            # `vector_embeddings` carries rows on such a run while grouping
            # continues to retrieve by shared validated fact alone.
            run_settings={"model_enabled": False, "embeddings_enabled": False},
            adapters=BUNDLE_ADAPTERS)
        comparison = None
        if baseline is not None and baseline != driven.run_id:
            comparison = get_comparison(
                conn, compare_runs(conn, baseline, driven.run_id))
        # Read before the connection closes. Which of the ten stages ran, which
        # were absent and which FAILED: a stage that raised attributes nothing
        # and would otherwise be printed at zero, which reads exactly like a
        # stage that ran cleanly and found nothing wrong.
        stages = stage_status(conn, driven.run_id)
        conn.commit()
    finally:
        conn.close()
    print("", file=out)
    for line in replay_lines(driven, stages=stages, comparison=comparison):
        print(line, file=out)
    return 0


def main(argv: Sequence[str] | None = None, *, out=None) -> int:
    # Bound at CALL time, not as a default: a default argument is evaluated when
    # this module is imported, which pins the stream that existed then.
    out = out if out is not None else sys.stdout
    parser = argparse.ArgumentParser(
        prog="database-agent",
        # NO ABBREVIATIONS. argparse defaults `allow_abbrev=True`, which makes
        # any unique prefix of a flag that flag -- so `--apply-`, a stray
        # trailing dash and no value, is a unique prefix of `--apply-everything`
        # and MOVES THE WHOLE PLAN. Measured: `--apply-`, `--apply-e` and
        # `--undo-` all fire. `--apply-everything` is spelled out precisely so
        # that no slip in a branch name can reach it, and an abbreviation
        # silently undoes that: the guard and the hole were the same length.
        #
        # It is off for every flag, not just those two. A person who types
        # `--res` and gets `--residual` has been taught that prefixes work, and
        # the lesson transfers to the flag that moves their files. This product
        # asks people to paste what it prints; a refusal naming the flag they
        # meant is the behaviour that keeps that true.
        allow_abbrev=False,
        description="Read a directory, propose a folder tree for it, and say "
                    "where each file would go. A plain run moves nothing. "
                    "--freeze turns the proposal into a plan; --apply moves "
                    "one branch of it, or several, or all of it; --undo puts "
                    "any of it back.")
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
    parser.add_argument(
        "--also-read", action="append", default=[], metavar="FOLDER", type=Path,
        help="another folder to read in the same run, e.g. --also-read "
             "~/Desktop. `00`:20's own example is several at once -- Downloads "
             "AND Desktop AND the loose files at the top of Documents -- and "
             "material split across two folders is the ordinary case. Can be "
             "given more than once. Every folder named here is read the same "
             "way the first one is, and the same exclusions apply to all of "
             "them.")
    parser.add_argument(
        "--could-live-in", action="append", default=[], metavar="FOLDER",
        type=Path,
        help="a high-level place a proposed branch could eventually live, e.g. "
             "--could-live-in ~/Documents/Academic. THIS IS NOT PERMISSION TO "
             "PUT ANYTHING THERE. Nothing inside it is read, indexed or "
             "organised, and this plan files nothing into it; what naming it "
             "does is let the proposal show the folders you already have, so a "
             "branch can be judged against the landscape it would join. "
             "Whether files may actually move between high-level folders is "
             "--may-cross-folders, which is a separate answer. Can be given "
             "more than once.")
    parser.add_argument(
        "--may-cross-folders", action="store_true",
        help="allow a file to be filed under a different high-level folder "
             "from the one it is in now -- a file in Downloads going to a "
             "Personal Projects folder on Desktop, rather than staying in "
             "Downloads organised in place. Off unless you say it: an "
             "unanswered permission is not a granted one. It still moves "
             "nothing by itself; --freeze and --apply are what move files.")
    parser.add_argument("--user", default=getpass.getuser(),
                        help="who this plan belongs to (recorded, never sent)")
    parser.add_argument(
        "--database", type=Path, default=None,
        help="where to keep the plan (default: ./database-agent-plan.sqlite). It "
             "may not live inside the folder being read.")
    parser.add_argument("--list-situations", action="store_true",
                        help="print every situation the shipped library carries")
    parser.add_argument(
        "--answer", action="append", default=[], metavar="QUESTION=OPTION",
        help="answer one of the questions the last run printed, e.g. "
             "--answer reading.organization:CV20261234=law_practice. Use "
             "`=skip` to put it aside. Answers are remembered between runs and "
             "can be given more than once.")
    parser.add_argument(
        "--describe-role", action="append", default=[], metavar="NAME=WORDS",
        help="say what this material is for you, in your own words, e.g. "
             "--describe-role me=\"I teach one course and I am doing my own "
             "PhD\". The name before the = is yours to choose and is how you "
             "change or withdraw it later. Your words are kept and turn nothing "
             "on by themselves; what prints next is the layouts you can choose "
             "from. Can be given more than once, and holding several at once is "
             "normal.")
    parser.add_argument(
        "--declare-role", action="append", default=[], metavar="NAME=LAYOUT",
        help="turn on one of the layouts this product knows, for this material, "
             "e.g. --declare-role teaching=research. `=not_listed` says none of "
             "them fits, which is a real answer that turns nothing on, and "
             "`=skip` puts it aside. Using a name again changes that role and "
             "leaves your others alone.")
    parser.add_argument(
        "--reject", action="append", default=[], metavar="FILE:FIELD=VALUE",
        help="tell the product that something it concluded about one of your "
             "files is wrong, e.g. --reject 'week 3.pdf:subject=PHYS1401'. The "
             "claim is retracted and it is not proposed again on later runs. "
             "Nothing is deleted -- the old conclusion and its evidence stay "
             "readable. Can be given more than once.")
    parser.add_argument(
        "--residual", action="append", default=[], metavar="NAME",
        help="enable one of §7.3's residual areas as a destination in this "
             "plan, e.g. --residual \"Reading Inbox\". These are the homes for "
             "material that belongs to no folder in particular. None is "
             "created unless you name it, and it can be given more than once. "
             "`--list-residuals` prints them.")
    parser.add_argument(
        "--show-protected", action="store_true",
        help="print the name of every protected file, instead of the count. "
             "They are counted and named as a group on every run and nothing "
             "about them is read, indexed or moved either way -- what this "
             "changes is only whether their filenames are on your screen, which "
             "is the part of the report least safe to have somebody read over "
             "your shoulder. It does not widen what any gesture may move: a "
             "freeze still cannot approve a protected file.")
    parser.add_argument(
        "--send-set", action="append", default=[], metavar="SET=AREA",
        help="file a whole review set into one of the residual areas this plan "
             "has, e.g. --send-set \"Not yet placed=Review Later\". Name the "
             "set exactly as the report printed it. No model is consulted -- "
             "the answer names the destination -- and it applies to the run "
             "that prints it, because a plan version's review sets are its own.")
    parser.add_argument(
        "--explain", action="append", default=[], metavar="QUESTION",
        help="print what one answer controls, where it applies, when it was "
             "given, how it was settled and how to change it.")
    parser.add_argument(
        "--list-residuals", action="store_true",
        help="print the residual areas `--residual` accepts, and stop.")
    parser.add_argument(
        "--enable-cloud", action="store_true",
        help="allow this folder's files to be sent to a cloud model, from this "
             "run on. Recorded against THIS FOLDER and remembered between runs, "
             "so it is typed once and not every time; another folder is another "
             "decision. Every run that may send says so before it does, and names "
             "the day you enabled it. Protected material is never sent.")
    parser.add_argument(
        "--disable-cloud", action="store_true",
        help="stop sending this folder's files to a cloud model, and stop. Takes "
             "effect immediately and needs nothing else -- not a situation, not a "
             "label, not even the folder still existing.")
    parser.add_argument(
        "--freeze", action="store_true",
        help="turn this run's proposal into a plan you can move files with. "
             "Freezing moves nothing. What it prints is one line per branch "
             "saying exactly what to type to move that branch.")
    parser.add_argument(
        "--apply", action="append", default=[], metavar="BRANCH",
        help="move the files frozen for one branch, e.g. --apply Coursework. "
             "Name it exactly as --freeze printed it; naming a parent moves "
             "everything under it. Give it more than once for several "
             "branches. A name that fits two branches is refused and both are "
             "printed -- it is never guessed. Needs no situation and no label: "
             "it moves what you already approved.")
    parser.add_argument(
        "--apply-everything", action="store_true",
        help="move every file this plan has frozen. Spelled out in full, and "
             "separate from --apply, so no slip in a branch name reaches it.")
    parser.add_argument(
        "--undo", action="append", default=[], metavar="BRANCH",
        help="put every file this product moved into one branch back exactly "
             "where it came from. Same spelling as --apply. A file you have "
             "edited or moved yourself since is reported, never overwritten.")
    parser.add_argument(
        "--undo-everything", action="store_true",
        help="put back every file this product has moved and not yet put back.")
    parser.add_argument(
        # `nargs="?"` with a `const` and NOT a bare flag, for BOTH of these two:
        # each on its own must be a refusal this file writes -- naming the
        # bundles the database holds, or saying a recording needs a name --
        # rather than argparse's "expected one argument". A person cannot type
        # an id they have never been shown, and a discovery flag that requires
        # the answer it supplies is the closed door `--list-situations` exists
        # to open. Absent stays absent: `default=None` means the flag was not
        # passed, so nothing is recorded and nothing is replayed.
        "--record", nargs="?", const="", default=None, metavar="NAME",
        help="record this run as a replay bundle you can come back to, e.g. "
             "--record before-upgrade. It runs exactly as it would anyway and "
             "moves nothing; what it adds is a frozen copy of what was read, "
             "which --replay re-reads without touching your folder again. The "
             "name is yours and must not already be taken.")
    parser.add_argument(
        "--semantic-model", type=Path, default=None, metavar="DIR",
        help="the folder holding a local sentence encoder (model.onnx and "
             "tokenizer.json). With it, recognition falls back to MEANING where "
             "matching your authored terms found nothing. OFF unless you name "
             "it, and nothing leaves your device either way -- the model runs "
             "here. Measured on a 199-file corpus it classifies 13 more files "
             "and changes no protection in either direction.")
    parser.add_argument(
        "--replay", nargs="?", const="", default=None, metavar="BUNDLE",
        help="re-evaluate one recorded bundle without touching the files: it "
             "reads what the run recorded, never the folder. Pass the bundle "
             "id; --replay on its own prints the ones this plan database "
             "holds. Never guesses, and never picks the latest.")
    args = parser.parse_args(argv)

    if args.list_residuals:
        for name in RESIDUAL_TEMPLATE_NAMES:
            print(name, file=out)
        return 0

    catalogue = load_shipped_catalogue(read_packaged_library_file)
    if args.list_situations:
        # Under the domain each one is FILED under, with the folder levels it
        # would build beside it. The flat alphabetical column this replaced
        # printed 208 bare names, which asks a person to already know which one
        # they want in order to find it -- the closed door this flag exists to
        # open. Nothing here is written for the listing: the domain and the
        # labels are both the library's own.
        situations = shipped_situations(catalogue)
        for schema in dict.fromkeys(row.schema for row in situations):
            rows = [row for row in situations if row.schema == schema]
            # Per domain and not across all of them: one 47-character name in
            # `business_operations` would otherwise indent every other line in
            # the listing to clear it.
            width = max(len(row.name) for row in rows)
            print(f"\n{schema}", file=out)
            for row in rows:
                print(f"  {row.name:<{width}}   {' / '.join(row.folder_levels)}",
                      file=out)
        print(f"\n{len(situations)} situations. Pass one to --situation. The "
              "words beside each are the folders it would build.", file=out)
        return 0

    if args.enable_cloud and args.disable_cloud:
        # `84` §6, applied for the fourth time: a gesture that acts on something
        # other than what the person named is worse than one that stops and asks.
        # Neither order of these two is more obviously right than the other, and
        # picking one would decide what may leave the device by argument order.
        parser.error("--enable-cloud and --disable-cloud say opposite things "
                     "about the same folder; pass one")

    # BEFORE the required-argument check, because turning sending OFF must not
    # require a full run's worth of arguments. A person who wants it to stop should
    # not have to name a situation and a label to say so, and the folder does not
    # even have to still exist -- `--disable-cloud` on a folder you have deleted is
    # a person tidying up after themselves, and refusing it would leave a record
    # saying "enabled" with nothing able to change it.
    if args.disable_cloud:
        if args.directory is None:
            parser.error("--disable-cloud needs the folder to stop sending for: "
                         "consent is recorded per folder, so there is no single "
                         "switch to throw")
        return _record_cloud_decision(args, DISABLED, out=out)

    # BEFORE the required-argument check, for the reason `--disable-cloud` is:
    # moving files you already approved needs no situation and no label. The
    # approval IS the frozen plan, and re-running the pipeline to move it would
    # mint a whole new proposal under names nothing has ever seen.
    moving = bool(args.apply) or args.apply_everything
    undoing = bool(args.undo) or args.undo_everything
    if moving and undoing:
        # `84` §6 for the fifth time. Moving and putting back in one invocation
        # is not a thing anyone means, and choosing an order would decide which
        # of somebody's files ends up where by argument order.
        parser.error("--apply and --undo say opposite things about the same "
                     "files; pass one")
    if moving or undoing:
        if args.directory is None:
            parser.error(
                ("--apply" if moving else "--undo")
                + " needs the folder whose plan you froze: a plan belongs to "
                  "one folder, so there is no single switch to throw")
        return _move_frozen_files(
            args, moving=moving,
            branches=tuple(args.apply if moving else args.undo),
            everything=(args.apply_everything if moving
                        else args.undo_everything),
            out=out)

    # BEFORE the required-argument check, for the reason `--disable-cloud` and
    # `--apply` are: replaying a bundle needs no folder, no situation and no
    # label. It reads what a run already recorded, and re-running the pipeline to
    # get at it would scan a person's disk to answer a question about a snapshot.
    if args.replay is not None:
        return _replay_bundle(args, out=out)

    # Absent means refuse, never guess. `--record` with no name would have to
    # invent one, and a recording called something the person did not choose is
    # one they will not find again -- which is the whole of what a name is for.
    if args.record is not None and not args.record:
        parser.error("--record needs a name to record under, e.g. --record "
                     "before-upgrade. It is never invented: a recording named "
                     "something you did not choose is one you will not find "
                     "again.")

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

    # `00`:20's other two answers, checked before anything is opened. A folder
    # that is not there gets the same sentence the first one gets, because a
    # traceback is what this command prints when a person makes a typo and
    # nothing else.
    landscape = _folder_landscape(directory, args.also_read, args.could_live_in,
                                  out=out)
    if landscape is None:
        return 2
    also_read, candidate_roots = landscape

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
        # Every folder this run touches, not only the first: the database may
        # not be created inside a folder being read, and `00`:20 lets a person
        # name several. A root counts too -- P3 walks it for its landscape, and
        # a database file appearing inside it would be a file this product made
        # in a place it promised to leave alone.
        conn = open_database(database,
                             scan_roots=[directory, *also_read, *candidate_roots])
    except DatabaseInsideCorpus as refusal:
        print(f"\n{refusal}", file=out)
        return 2
    print(f"Plan database: {database}", file=out)
    # `104` R-14. Built HERE and not inside `model_route`, because both halves of
    # the wire start from this frame: the route hands it to the transport as
    # `on_usage`, and `run` hands it to `run_call` as `usage_recorder`. One object,
    # two faces, and neither side learns about the other.
    usage_recorder = UsageMailbox()
    # `104` R-92, built beside it for the same reason: which files each question
    # this run raises would settle is known only while the run is deriving them,
    # and the report that has to print it runs here.
    questions_reach: dict[str, tuple[str, ...]] = {}
    # BEFORE the run, and printed whichever way it goes. If this deployment cannot
    # call a model the person is told once, at the top, in a sentence about the
    # deployment -- rather than left to infer it from thirty file-level sentences
    # at the bottom that each read as a statement about one of their files.
    routing = model_route(out=out, on_usage=usage_recorder)
    if args.enable_cloud:
        # Applied on the invocation that supplies it, exactly as `--answer` and
        # `--reject` are: a person who has just said yes should not have to run the
        # command again to see what it did.
        #
        # One record per SOURCE. `--enable-cloud` says it is "Recorded against
        # THIS FOLDER … another folder is another decision", and with several
        # folders in one run that promise is only kept by writing several
        # records. A single record against the first would let the second
        # folder's files leave under a permission that never named it.
        for source in (directory, *also_read):
            record_cloud_consent(conn, corpus_root=str(source), decision=ENABLED,
                                 user_id=args.user, decided_at=now())
    # The WEAKEST answer across the sources, not the first one's. A run reads
    # every source into one corpus and one dossier, so a folder that has not
    # been cleared cannot be protected by a mode chosen for a folder that has.
    # Absent is refusal, and refusal wins.
    consent = _weakest_consent(
        cloud_consent_for(conn, str(source)) for source in (directory, *also_read))
    announce_cloud_posture(routing, consent, corpus_root=directory,
                           other_sources=also_read, out=out)
    try:
        # BEFORE the run, so an answer takes effect on the very invocation that
        # supplies it. A person who has just been asked something and answers it
        # should not have to run the command a third time to see what it did.
        if args.answer:
            _bootstrap(conn)
            _print_answer_effects(
                conn,
                apply_answers(conn, args.answer, user_id=args.user,
                              recorded_at=now()), out)
        # After the answers and before the run, for the same reason, and in
        # this order: describing then confirming under one name is a correction
        # that supersedes, so the confirmation must be the later write.
        if args.describe_role or args.declare_role:
            _bootstrap(conn)
        if args.describe_role:
            apply_descriptions(conn, args.describe_role, schemas=SCHEMA_IDS,
                               user_id=args.user, recorded_at=now())
            for name, sentence in described_sentences(args.describe_role):
                # `propose=None` is `80` §1's Option 1 and not a gap: no local
                # model is configured, so the closed list arrives unnarrowed and
                # the person picks from all of it. `sending` is absent, which
                # is `80` §8.3's condition C1: sending a person's own sentence
                # to a provider is an explicit act, never what happens by not
                # choosing.
                _role_lines(shortlist_lines(
                    propose_roles(sentence, offered=SCHEMA_IDS, propose=None,
                                  mode=OPERATION_MODE),
                    name=name, order=_unranked), out=out)
        if args.declare_role:
            apply_declarations(conn, args.declare_role, schemas=SCHEMA_IDS,
                               user_id=args.user, recorded_at=now())
        if args.reject:
            _bootstrap(conn)
            apply_rejections(conn, args.reject, user_id=args.user,
                             observed_at=now())
        if args.explain:
            _bootstrap(conn)
            for question_id in args.explain:
                explanation = explain_question(conn, question_id)
                if explanation is None:
                    # Refused rather than ignored, exactly as an unknown
                    # `--answer` is: a person who mistyped believes they were
                    # shown an explanation of the thing they meant.
                    print(f"\n{question_id!r} is not a question this plan has "
                          f"raised. The report prints the ones that are open.",
                          file=out)
                else:
                    print("", file=out)
                    print(render_explanation(explanation), file=out)
        if args.record:
            # BEFORE the scan, and that ordering is the whole point. The writer
            # refuses a taken name too, but by then the person has waited out a
            # full run over their corpus to be told something that was knowable
            # from the argument and the database alone. `_bootstrap` is
            # idempotent and `run` calls it again in a moment.
            _bootstrap(conn)
            held = bundle_named(conn, args.record)
            if held is not None:
                print(f"\nThis run was not started, because the name is taken:"
                      f"\n  {args.record!r} already names bundle {held}.",
                      file=out)
                print(_wrapped(
                    "Two recordings under one name make a replay of that name a "
                    "question with two answers, so it is refused rather than "
                    "guessed. Pick another name. The recording that holds this "
                    "one is kept, never overwritten, and `--replay` with nothing "
                    "after it lists every recording this plan database has.",
                    indent="  "), file=out)
                return 2
        result = run(conn, directory, situation=args.situation, label=args.label,
                     user_id=args.user, now=now, out=out,
                     also_read=also_read, candidate_roots=candidate_roots,
                     cross_folder_moves=args.may_cross_folders,
                     residuals=_validate_residuals(args.residual),
                     sends=_parse_sends(args.send_set),
                     operation_mode=operation_mode_for(consent),
                     record=args.record,
                     # BOTH, or the fact pass does not happen. `routing` is `None`
                     # with no key and the mode is `offline` without this folder's
                     # consent, so the two arguments carry the two independent
                     # reasons a run sends nothing -- which is the same pair
                     # `announce_cloud_posture` has just told the person about.
                     routing=routing,
                     usage_recorder=usage_recorder,
                     questions_reach=questions_reach,
                     semantic_model=args.semantic_model,
                     wire_handle_key=wire_handle_key_for(database))
    except RecordingNameTaken as refusal:
        # Belt and braces behind hunk 13. The name is checked before the scan, so
        # this is reachable only if a second process recorded that name while
        # this run was going -- and a traceback would be the person's reward for
        # a race they did not cause. The scan's own bundle is sealed and kept
        # either way (§8.2); what did not happen is the recording.
        print(f"\nThe run finished, and the recording was refused:\n  {refusal}",
              file=out)
        return 2
    except (AnswerNotPermitted, NotConfigured, ConfigurationRequired) as refusal:
        print(f"\nThis run was refused, and here is what it needed:\n  {refusal}",
              file=out)
        return 2
    except REFUSALS as refusal:
        # R-24 FIRST, because it is not one of these. A folder nothing could be
        # read from produces no accepted group, so `design_tree` refuses -- and the
        # refusal is true about the tree and false about the run, which read
        # everything there was and found nothing in it. The block below is that
        # case and only that case; every other refusal keeps the sentence and the
        # exit code it has always had.
        if isinstance(refusal, NothingToDesign):
            said = _nothing_could_be_read_report(
                conn, directory=directory, also_read=also_read, now=now)
            if said is not None:
                for line in said:
                    print(line, file=out)
                return 0
        # A NAMED refusal, printed rather than raised. §5's chain refuses by name
        # -- C1-C8, V1-V6, §5.4's empty branch -- and each refusal says which
        # judgement failed and why. A traceback here would turn an answer the
        # design worked hard to give into a crash.
        print(f"\nNo plan was made for {directory}, and this is why:\n"
              f"  {type(refusal).__name__}: {refusal}", file=out)
        return 1
    # `questions_a_run_could_not_settle` and not `open_questions` raw. A revoked
    # role question REOPENS -- that is what revocation means -- and printing it
    # under "Questions only you can answer" put a 23-option identity question in
    # the blocking section of a run where no file was blocked on anything of the
    # kind. Found by running this, not by reading it.
    open_now = questions_a_run_could_not_settle(open_questions(conn))
    # Read here and passed IN, for the reason `report`'s own docstring gives: it
    # takes a finished run and a naming table and holds no connection, and giving
    # it one so it could ask a second part a question would make the report a
    # place where new facts are discovered.
    held = live_roles(conn)
    _landscape = high_level_folders(directory, also_read, candidate_roots)
    shown = report(result, file_names(conn, directory, *also_read), out=out,
                   questions=open_now,
                   set_aside=set_aside_questions(conn),
                   role_moment=role_moment_lines(blocked=open_now,
                                                 already_declared=held),
                   roles_held=role_panel_lines(held),
                   invite_freeze=not args.freeze,
                   list_every_name=args.freeze,
                   show_protected=args.show_protected,
                   # Read here and passed IN, for the reason `report`'s own
                   # docstring gives about `questions`: it takes a finished run
                   # and a naming table and holds no connection.
                   locked=locked_reasons(conn, result.p1_p7.scan_run_id),
                   # `104` R-N, and the landscape below is the same object the
                   # freeze resolves against, so the screen and the plan cannot
                   # disagree about which folder a file is in.
                   crossing=({} if args.may_cross_folders
                             else _crossing_moves(conn, result,
                                                  landscape=_landscape)),
                   # `104` R-K, read here and passed IN like the rest.
                   duplicates=duplicate_families(
                       conn, result.p1_p7.scan_run_id),
                   # `104` R-90. WHAT THE PERSON TYPED, asked of the library that
                   # owns the answer -- and read HERE, from `args.situation`,
                   # rather than off the run, because it is a fact about the
                   # command and not about the corpus. The run has already
                   # validated the situation against this same catalogue, so
                   # nothing here can refuse for the first time.
                   reading_family=situation_schema_family(
                       load_shipped_catalogue(read_packaged_library_file),
                       args.situation),
                   # `104` R-92, turned the way the report reads it: the run
                   # answers "which files does this question settle" and a group
                   # of files asks "which question settles me". Inverted here,
                   # once, rather than in the loop that groups the decisions.
                   reaching=_questions_by_file(questions_reach),
                   # A §7.6 set answer belongs to the plan version it was given
                   # in, and every run mints a new one, so an answer given
                   # yesterday is not applied today. That is
                   # `act_on_residual_sets`'s decision and it stands -- a later
                   # run's set may hold different files. What did NOT stand is
                   # saying nothing: the row sits in `residual_set_decisions`
                   # for ever and the block it produced simply vanished from
                   # the screen. `84` §6 -- a decision that no longer applies is
                   # named, never silently omitted. Read here and passed IN, for
                   # the same reason the roles and the questions above are.
                   not_carried=prior_set_decisions(
                       conn,
                       plan_version=result.tree.tree.plan_version_id))
    if args.record:
        # AFTER the report, because it ends in a command to type and a command
        # printed above forty lines of report is a command nobody sees. The
        # bundle is looked up by the name the person just chose, and the group
        # count is read back off the recording rather than carried down here --
        # what is reported is then what was actually stored.
        from eval_harness.bundle import accepted_groups
        recorded = resolve_bundle(conn, args.record)
        for line in recorded_lines(args.record, recorded,
                                   count=len(accepted_groups(conn, recorded))):
            print(line, file=out)
    if not args.freeze:
        return 0

    # `00`:51 and `00`:102: freezing is what turns a proposal into an approved
    # destination tree. It moves nothing. What it writes is one plan per file,
    # holding `00`:156-170's complete expected precondition -- which is what
    # `--apply` reads, on a later invocation, instead of re-running a pipeline
    # that would mint a whole new proposal under names nothing has ever seen.
    plan_counter = count()
    approval_counter = count()

    def mint_plan_id() -> str:
        return f"{uuid.uuid4().hex}:{next(plan_counter)}"

    def mint_approval_id() -> str:
        # Prefixed, because an approval id and a plan id are two different
        # things a person may be asked about later and a bare uuid says which of
        # the two it is only by where it was found.
        return f"approval-{uuid.uuid4().hex}:{next(approval_counter)}"

    proposal = freeze(
        conn, result.placement.decisions, nodes=result.tree.tree.nodes,
        legal_destination_ids=frozenset(
            node.node_id for node in result.tree.tree.nodes
            if node.accepts_placement),
        # `00`:20's third choice, as the person answered it -- and the SAME
        # answer R1 holds, because two places that each decide whether a file
        # may cross a high-level folder is one place too many. Off unless
        # `--may-cross-folders` was typed: `review_surface/move_permission.py`
        # already rules that no policy at all is no permission, and a movement
        # permission is the last thing to infer from silence.
        cross_folder_moves=args.may_cross_folders,
        constraints=_FILESYSTEM_CONSTRAINTS,
        # §1.1's folder landscape, which is what P12 means by this argument.
        # With one entry, a file from a second source was under NO high-level
        # folder, `_source_folder` returned None, and P12's refusal named
        # nothing a person could act on. The candidate roots are in it for the
        # same reason -- they are part of the landscape -- and being in it makes
        # nothing a destination: a destination needs a NODE whose `root_anchor`
        # names it, and `adopted_folders` refuses to build one over a root.
        high_level_folders=_landscape,
        volume_of=_volume_of,
        protected_handling_classes=PROTECTED_CLASSES,
        # `74` §8 Q3 is open, so the only behaviour that can be frozen is the
        # one of `00`:172's four that needs no suffix. A collision stops and
        # asks; nothing is written over and no name is invented.
        collision_policy=mv.STOP_AND_ASK,
        expiration_state=_EXPIRATION_STATE,
        # The owner's ruling of 2026-09-02: `--freeze` IS P13's review surface.
        # A person who has read the proposal and typed the word has approved
        # those placements -- so the freeze writes P13's `review_approval`, and
        # `mutation.approval`'s gate is satisfied by a record a person actually
        # produced rather than by nothing.
        #
        # `shown` is what the report printed by name, and it is the whole of
        # what "informed" means here: a placement this run did not name is not
        # approved by this run, and `freeze` holds it and says so.
        shown_file_ids=frozenset(shown),
        approve_reviewed=approval_writer(
            conn,
            # Read from P7 at the moment of display rather than assumed. §8.4
            # makes what was displayed a privacy-relevant fact, and this run has
            # no standing to guess which policy the person was reading under.
            settings=display_policy(
                conn, plan_version=result.tree.tree.plan_version_id),
            # The plan version IS this sitting: `run_token` mints a fresh one on
            # every run, so it names the reading and the freezing that followed
            # it, and nothing else in this process has a longer or truer claim
            # to being the session.
            session_id=result.tree.tree.plan_version_id,
            user_id=args.user, component_version=COMPONENT_VERSION,
            mint_id=mint_approval_id),
        component_version=COMPONENT_VERSION, now=now, mint_id=mint_plan_id)
    conn.commit()
    for line in freeze_lines(
            proposal, names=file_names(conn, directory, *also_read),
            nodes=result.tree.tree.nodes,
            apply_command=lambda branch: _typed(
                directory, args.database, f"--apply {shlex.quote(branch)}"),
            apply_everything_command=_typed(
                directory, args.database, "--apply-everything")):
        print(line, file=out)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
