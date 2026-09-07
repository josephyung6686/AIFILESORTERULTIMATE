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
from decimal import Decimal
from itertools import count
from pathlib import Path, PurePosixPath
from functools import lru_cache, partial
from types import MappingProxyType
from typing import Mapping, Sequence

from database_agent.budget import set_ceiling
from database_agent.cloud_consent import (
    DISABLED, ENABLED, CloudConsent, cloud_consent_for, record_cloud_consent,
)
from database_agent.db import DatabaseInsideCorpus, open_database
from database_agent.files_table import (
    PATH_NO_LONGER_EXISTS, SUPERSEDED_CONTENT, get_file,
)
from extractors.image import PERCEPTUAL_HASH_FIELD
from extractors.router import SOURCE_TYPE_BY_FORMAT
from extractors.reading import StructuredString
from extractors.structured_text import EXTRACTOR_NAME as STRUCTURED_EXTRACTOR
from extractors.filesystem import SOURCE_TYPE as FILESYSTEM_SOURCE_TYPE
from extractors.safety import SafetyPolicy
from facts.date_facts import date_facts
from facts.dates import (
    ACADEMIC_YEAR_RANGE, NAMED_TERM_YEAR, SEASON_YEAR, DatePattern, DatePatterns,
)
from facts.direct import DirectSlot, DirectSlots, direct_facts
from facts.families import (
    DUPLICATE_FAMILY_FIELD, VERSION_FAMILY_FIELD, duplicate_family,
    shared_family_field,
)
from facts.discount import MetadataScreen
from facts.learning import NoSuchClaim, reject_claim
from facts.domains import ActivationSignal, ActivationSignals
# `MEDIA_TYPE_FIELD` left this import with `104` R-09: the retired
# `active_schema_for` literal was the only line in this file that named it.
from facts.photo_event import media_type
from facts.budgets import LLM_ROUTE
from facts.resolver import PRIVACY_BAR, FactResolver
from facts.rules import ACADEMIC_CONTEXT_TERMS, Rule, apply_rules
from facts.unresolved import NO_CANDIDATE_EVIDENCE
from facts.usable import record_pass
from facts.fields import DOMAIN_FIELDS
from facts.states import VALIDATED, strength
from facts.kind import tokens as kind_tokens
from facts.kind import compile_vocabulary, kind_facts
from grouping.acceptance import group_state_as_of, record_acceptance
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
    current_group, live_memberships_of_file, memberships_for_group, record_group,
    record_membership, stop_rule_outcome_for,
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
    a_fact_template_folder_levels_bytes, draft_bytes, drafts_status,
)
from llm_harness.harness import CallDependencies, run_call
from llm_harness.records import FolderLevel, P8Verdict, PromptDefinition
from llm_harness.store import last_response_bytes
from llm_harness.sites import SiteDependencies
from llm_harness.schema import create_llm_schema
from llm_harness.vocabulary import (
    A_FACT, B_GROUP, C_PLACEMENT, CONTEXT_SUPPORTED, D_RESIDUAL, DIRECT_ANCHOR,
    E_TEMPLATE, PRE_CALL_NAMESPACE,
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
    FactCallAuthorities, fact_call_stage, measure_released_tokens,
    pending_fields_for,
)
from privacy.classification import UNREADABLE_UNCLASSIFIED, resolve_class
from privacy.classification_store import ClassificationStore
from privacy.denial import unclassified_denies
from privacy.gate import Gate
from privacy.defaults import LOCAL_FIRST_MODES
from privacy.display import display_policy
from privacy.moves import may_move_automatically
from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy
from privacy.resolve import (
    AmbiguousObservationKey, UnresolvableSpan, current_location,
)
from privacy.vocabulary import MODE_SEMANTICS
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
from questions.roles import (
    apply_declarations, apply_descriptions, described_sentences, live_roles,
)
from questions.schema import create_questions_schema
from questions.store import (
    activated_schemas, chosen_destination, gated_template, live_answer,
    live_answer_id,
    open_questions,
    record_answer,
    record_question, set_aside_questions,
)
from questions.triggers import (
    DestinationChoice, NestingChoice, question_for_nesting,
    question_for_unreadable_folder, tied_readings,
)
from questions.vocabulary import (
    CONFIRMED, REVOKED, SCOPE_BRANCH, SCOPE_FOLDER, SKIPPED,
)
from production import (
    CorpusAuthorities, CorpusDecisions, P1P7Authorities, ProductionRun,
    bootstrap_p1_p7, corpus_roster, folder_levels_for, load_shipped_catalogue,
    nearest_situations, read_packaged_library_file, schema_for_situation,
    shipped_situations,
    run_production_corpus,
)
from readers.deployment import macos_readers
from readers.pdf_pdfium import pdfium_reader
from readers.signatures import signature_detector
from extraction_pool import ExtractionContext, InlinePool, ProcessPool
from model_placement import (
    PlacementCallAuthorities, model_path_injections,
)
from readers.model_deepseek import BASE_URL_NAME, CLOUD, CREDENTIAL_NAME
from readers.model_ollama import (
    BASE_URL_NAME as LOCAL_BASE_URL_NAME,
    LOCAL,
    MODEL_NAME as LOCAL_MODEL_NAME,
)
from readers.model_routing import (
    FAST, LOGIC, MODEL_NAME_OF_TIER, REASONING, TierRouting, deepseek_routing,
    ollama_routing,
)
from facts.domains import SCHEMA_IDS
from recognition.detector import (
    FIRST_PAGE, NAMING_ZONES, SAFETY_DOMAIN_HANDLING, Detector, Handling,
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
from tree_design.templates import CompositionConflict
from scan_agent.selection import selection_candidate_roots
from tree_design.upstream import (
    UpstreamUnavailable, existing_folders, file_ids_in_directory,
    handling_class_for, protected_areas, settled_values_stated_by_every_file,
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
from tree_design.store import nodes_for_version
from apply_run.approval import approval_reader, approval_writer
from apply_run.branches import BranchRefused, branches_named
from apply_run.freeze import freeze, frozen_plans
from apply_run.report import apply_lines, freeze_lines, undo_lines
from apply_run.run import (
    already_applied, applied_entries, apply_selected, plans_under, take_back,
)
from review_run.progress import progress_lines
from review_surface.schema import create_review_schema
from review_surface.vocabulary import ACTION_REJECT
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

#: ONE OF THE SEVEN IS NOT A SPEND CEILING, and it had this value only because
#: it was in the same loop. `residual.max_files_per_review_batch` does not bound
#: what a run COSTS -- it bounds how many files a person is shown in one review
#: set, and §8.6 splits a set at this number rather than truncating it. So it
#: also decides how many separate `--send-set` commands they must type to file
#: one hold: measured on a 5,000-file corpus, 420 sets from a single hold and
#: therefore 420 commands.
#:
#: It is separated here rather than re-valued, because the two directions are a
#: real trade and the trade is not this file's to settle. A larger batch is
#: fewer commands AND a bigger set accepted in one gesture with no per-file
#: look, which is exactly the scrutiny `--send-set` spends. `00` states no value
#: and the design's own answer -- §7.6 makes the person authorise a set before
#: anything happens to it -- is about spend, not about typing.
#:
#: So this stays at `CEILING_VALUE` and the question is named rather than
#: quietly answered: whether 420 commands is fixed by a bigger batch or by
#: letting one gesture address a HOLD instead of a batch, is the owner's, and
#: the second is a gesture change (`84` §1).
RESIDUAL_REVIEW_BATCH: int = CEILING_VALUE

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
#: §8.4's Open question 5, answered once for this deployment and read by BOTH the
#: gate and the route. It was a literal at the `Gate(...)` call and a `True` the
#: route did not consult at all, which is `104` R-02 in one line: two places
#: deciding whether an unclassified file may reach a model, and only one of them
#: was asked. One name, so they cannot answer differently.
#:
#: ANSWERED `True` ON 2026-09-05 against the premise the run disproved -- "an
#: unclassified file is one nothing has read successfully". 95 of the owner's 199
#: files were unclassified and every one had evidence.
UNCLASSIFIED_PERMITS_LOCAL: bool = True

OPERATION_MODE: str = "offline"

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
LOCAL_CONTEXT_CEILING: int = 32768

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
    C_PLACEMENT: "c_placement.unratified.eliminate-v2.2026-09-06",
    D_RESIDUAL: "d_residual.unratified.ladder.2026-09-06",
    E_TEMPLATE: "e_template.unratified.what-a-person-opens-v2.2026-09-06",
})

assert set(OBSERVE_TEMPLATE_ID) == OBSERVE_CALL_SITES


#: WHAT A REJECTED B PROPOSAL IS CALLED, spelled once. `proposal_class` is not a
#: harness vocabulary: `eligibility.py:51` matches it EXACTLY against
#: `learning_records.proposal_class`, so it is an identity the composition root
#: names and must keep stable -- a rename stops every past rejection suppressing
#: what it was recorded to suppress. `model_facts` spells its own
#: `fact.llm_extraction`, and this follows that shape: the subject kind, then what
#: the model was asked to do.
GROUP_PROPOSAL_CLASS: str = "group.llm_coherence"


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


def observe_group_authorities(fact_authorities, *, routing: TierRouting,
                              situation: str):
    """Site B, wired to run and to change nothing. `(p8_run_call, authorities)`.

    **Everything shared with site A is TAKEN from A's authorities rather than
    rebuilt.** The gate, the budget, the costs, the policy version and the wire
    handle key are facts about this deployment and this run, not about which site
    is asking; a second `Gate` built beside the first would be a second answer to
    "what may leave this device" and the two would drift on the next ruling. What
    differs is the client, the prompt, and the five learning fields below.

    `(None, None)` when there is no routing, or when B's tier does not resolve to
    a model on this device. That second case is not an error: a deployment with a
    cloud key and no local model is correctly configured and simply does not run
    the observe sites, because their text is unratified. `require_observe_locality`
    is the backstop for anyone who builds these another way.
    """
    if routing is None:
        return None, None
    locality = routing.locality_for(B_GROUP)
    if not observe_locality_permits(B_GROUP, locality):
        return None, None
    require_observe_locality(B_GROUP, locality)
    client = routing.client_for(B_GROUP)
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
        scan_budget=fact_authorities.scan_budget,
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
        # The SAME target the client is pointed at, read off the client rather
        # than built beside it.
        model_target=client.model_target)


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


class ObservedSiteMustNotApply(RuntimeError):
    """An observe-only site reached the code that would act on its answer."""


def _must_not_apply(call_site: str):
    """`chosen_node_of` and `residual_action_of` for a site that applies nothing.

    `model_path_available()` reads all eight injections as a set, so these must be
    present for C and D to run at all. They must also never be REACHED: the
    observe lever in `_judge_with_model` rewrites the verdict to an abstention, and
    both callers take their existing abstention path without consulting a resolver.

    So they raise. A resolver that returned a plausible node would place a file on
    the strength of a validator `104` R-15 says is wrong about every real value,
    and it would do it silently the first time the lever was moved or removed. This
    fails loudly instead, which is what an unreachable branch owes the next person
    to make it reachable.
    """
    def resolve(_verdict: object):
        raise ObservedSiteMustNotApply(
            f"{call_site} is observe-only and something asked it to apply an "
            f"answer. `104` §7 Phase 1 step 6 records the verdict and applies "
            f"nothing until Phase 3 fixes R-15 and R-16, and the abstention that "
            f"keeps this unreachable is in `_judge_with_model`. Writing a real "
            f"resolver is the LAST step of turning this site on, not the first.")
    return resolve


def observe_placement_injections(conn: sqlite3.Connection, fact_authorities, *,
                                 routing: TierRouting, plan_version: str) -> dict:
    """Sites C and D, wired to run and to change nothing. Eight of the nine.

    `sensitivity_policy` is NOT here: R-55 supplies it at `placement_inputs`
    already, and P8's two sensitivity checks refuse with it whether or not a model
    is configured. Overwriting it from here would take a refusal away.

    `{}` when there is no routing or when C's tier is not on this device, which
    leaves every field as `placement_inputs` had it and the model path off.
    """
    if routing is None:
        return {}
    locality = routing.locality_for(C_PLACEMENT)
    if not observe_locality_permits(C_PLACEMENT, locality):
        return {}
    require_observe_locality(C_PLACEMENT, locality)
    require_observe_locality(D_RESIDUAL, routing.locality_for(D_RESIDUAL))
    authorities = PlacementCallAuthorities(
        gate=fact_authorities.gate,
        model_client=routing.client_for(C_PLACEMENT),
        # ONE PROMPT EACH. This said "the prompt it sends is C's for both -- which
        # is a REAL limitation of wiring two sites through one function", and the
        # limitation is gone rather than reported: `PipelineInputs.prompt_for`
        # picks by call site and `run_call` refuses a request whose site is not the
        # prompt's. D's answer names one of §7.7's eight actions and C's schema has
        # no `action` key, so every residual answer was heading for
        # `SCHEMA_INVALID` -- for obeying text that was not its own either.
        prompt=prompt_for(C_PLACEMENT),
        residual_prompt=prompt_for(D_RESIDUAL),
        model_target=routing.client_for(C_PLACEMENT).model_target,
        evidence_resolver=fact_authorities.evidence_resolver,
        contradicts=fact_authorities.contradicts,
        scan_budget=fact_authorities.scan_budget,
        estimated_cost=fact_authorities.estimated_cost,
        actual_cost=fact_authorities.actual_cost,
        policy_version=fact_authorities.policy_version,
        wire_handle_key=fact_authorities.wire_handle_key,
        sensitivity_policy=sensitivity_policy_for(conn),
        chosen_node_of=_must_not_apply(C_PLACEMENT),
        residual_action_of=_must_not_apply(D_RESIDUAL))
    built = model_path_injections(conn, authorities, plan_version=plan_version)
    built.pop("sensitivity_policy", None)
    return built


#: The eight `model_path_injections` fills for C and D. `sensitivity_policy` is
#: the ninth and is supplied at `placement_inputs` by R-55 whether or not a model
#: is configured, so it is not in this set and is never overwritten from here.
OBSERVE_PLACEMENT_FIELDS: tuple[str, ...] = (
    "gate", "model_client", "prompt", "residual_prompt", "call_dependencies",
    "model_call_request", "chosen_node_of", "residual_action_of",
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
        # THE PACKET'S OWN STATUS, read from the manifest. Every one of these is a
        # D2 draft and `drafts_status()` says `unratified`; when the owner ratifies
        # the packet this becomes true without a line of this file changing.
        ratified=drafts_status() == "ratified",
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
    the object rather than parsing the id, so the day the owner ratifies the packet
    every site starts applying on the same run and no line of this file changes.
    """
    if call_site == A_FACT:
        return a_fact_prompt()
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
    count nobody enforces is a hope.** Every prompt these four sites would send is
    a D2 DRAFT: `drafts_2026-09-06.json` carries `"status": "unratified"` and every
    `template_id` in it says `unratified` in the id itself, so a record written
    under one says so. `planning/82` §0 records the owner ratifying `A_fact`'s text
    and nothing else.

    Unratified text is text nobody has agreed to send. On this machine that is a
    question of taste; over the internet it is a person's dossier reaching a
    provider under a prompt their owner never approved, and it cannot be taken
    back. So the difference is enforced where it is a fact rather than promised in
    a comment: a cloud target for an observe site RAISES, and the raise happens at
    the composition root before a corpus has been read.

    `A_fact` is unaffected and stays cloud-eligible: it is not in this set, its
    text is ratified, and `WIRED_CALL_SITES` is what governs it.
    """
    if call_site not in OBSERVE_CALL_SITES:
        return True
    return locality == LOCAL


def require_observe_locality(call_site: str, locality: str) -> None:
    """`observe_locality_permits`, as a refusal that names what was wrong."""
    if observe_locality_permits(call_site, locality):
        return
    raise UnratifiedPromptOnACloudTarget(
        f"call site {call_site!r} is observe-only and its prompt is a D2 DRAFT "
        f"({drafts_status()!r}), but the routing sends it to a {locality!r} model. "
        f"`104` §13 counts 0 cloud calls with unratified prompts and this is where "
        f"that count is kept. Unratified text is text nobody has agreed to send: "
        f"on this device that is a question of taste, and over the internet it is "
        f"a person's dossier reaching a provider under a prompt their owner never "
        f"approved. Configure {LOCAL_MODEL_NAME} and the observe sites run here; "
        f"ratify the text and the site joins WIRED_CALL_SITES instead.")

#: How many of a file's observations may be offered to the A_fact call, and the only
#: place the NUMBER is chosen. §8.4 asks for "a compact dossier ... selected
#: excerpts", states no count, and `model_facts.releasable_observations` takes the
#: cap with no default.
#:
#: TWELVE, and the cost of each direction is real. Too few and the model is shown a
#: title and three metadata fields and honestly declines every field -- which is a
#: call paid for and a fact not gained. Too many and §8.4's "data-minimizing" stops
#: meaning anything: every additional excerpt is more of a person's document at a
#: provider, and the response ceiling (`MAX_RESPONSE_TOKENS`) is fixed, so past some
#: point the extra evidence only crowds out the answer. Twelve is the count at which
#: a real coursework PDF's title, its page-one heading, its PDF metadata and a few
#: body readings all fit, measured on the owner's own Downloads.
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

#: HOW MANY FILES A RUN MUST WANT TO READ before seven interpreters are worth
#: starting. Below it `ProcessPool` reads on the calling thread; above it the pool is
#: built. Measured on the owner's real files on an idle machine, wall seconds:
#:
#:      LIGHT files (notes, json, source)     HEAVY files (PDF)
#:      files   workers=1  workers=7          files   workers=1  workers=7
#:          4      1.0        3.4                 8    65.5       61.0
#:         12      2.7        8.2                16    95.4       89.2
#:         24      5.5        6.7                32   152.8      145.0
#:
#: The two columns disagree, and that disagreement is why this number is 32 and not
#: 8. On heavy files the pool already wins at eight. On light files it is THREE TIMES
#: SLOWER at twelve and still behind at twenty-four. The harm is asymmetric -- the win
#: on PDFs is 7 per cent, the loss on a folder of notes is 200 -- so the floor sits
#: above the highest count where the pool was MEASURED TO LOSE, rather than at the
#: lowest where it was measured to win.
#:
#: A count is the wrong axis, and it is the only axis available. What decides the
#: crossover is the WEIGHT of what is about to be read, and a run cannot know that
#: until it has read it. Thirty-two is where the two answers stop disagreeing.
#:
#: A spawned worker re-imports this file and Apple's Vision framework, about five
#: seconds of CPU each, so seven of them cost thirty-five CPU-seconds before one file
#: is read. Small folders are the owner's ORDINARY case -- one course's material, the
#: loose files at the top of Documents -- so paying that to read four files is wrong
#: for the product, not merely wasteful.
#:
#: It counts SUBMISSIONS and not files in the folder: a ten-thousand-file corpus that
#: is entirely cached submits nothing and stays inline, which is the right answer.
EXTRACTION_POOL_FLOOR: int = 32

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
#: case this product can name, and the file is recorded `unexamined` with the ceiling
#: and the reader in the row, which is a sentence an operator can act on.
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
        # D1's local half, and `serves` is what makes it FIRST rather than
        # instead-of: beside a cloud key the local model takes the tier A_fact
        # requires and the other tiers keep the models the key paid for.
        return ollama_routing(
            model_id=local_model,
            base_url=value(LOCAL_BASE_URL_NAME),
            tier_of_call_site=TIER_OF_CALL_SITE,
            max_response_tokens=MAX_RESPONSE_TOKENS,
            context_ceiling=LOCAL_CONTEXT_CEILING,
            timeout_seconds=LOCAL_MODEL_TIMEOUT_SECONDS,
            serves=A_FACT if cloud is not None else None,
            beside=cloud,
            # `104` R-14, and this is the route that usually serves A_fact: a
            # deployment with a local model gives it that site, so a usage row with
            # no tokens on it would be the ordinary case rather than the exception.
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
        if routing is not None and routing.locality_for(A_FACT) == LOCAL:
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
            # PER SITE, because only one of the three is wired. `A_fact` can send
            # and the other two cannot, and a sentence that named all three as
            # recipients would frighten a person about two things that cannot
            # happen -- the same untruth `WIRED_CALL_SITES` replaced, inverted.
            # Every model is still NAMED, including the two that will not be
            # asked: a person deciding today is deciding about tomorrow's runs,
            # and "an external provider" tells them less than a name does.
            print(_wrapped(
                f"Files that need a FACT judgement -- what course, what school, "
                f"what kind of document -- may be sent to "
                f"{routing.model_id_for(A_FACT)}. That is the only question this "
                f"run can ask a model. {routing.model_id_for(C_PLACEMENT)} "
                f"(checks) and {routing.model_id_for(D_RESIDUAL)} (review sets) "
                f"are configured and no part of this run can reach them yet, so "
                f"nothing goes to either. Protected material and §8.4's "
                f"always-local kinds -- your paths, your filenames, whole "
                f"documents -- are refused by P7 and are not among what is sent. "
                f"Sending stays ON for this folder until you turn it off with:",
                indent="  "), file=out)
        print(_turn_off_line(corpus_root, *other_sources), file=out)
        return
    if routing is None:
        # `model_route` has already said no model is configured. A second sentence
        # about consent would answer a question the person cannot yet be asking.
        return
    if routing.locality_for(A_FACT) == LOCAL:
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
        print(_wrapped(
            f"Model: {routing.model_id_for(A_FACT)}, running on this device, for "
            f"facts -- what course, what school, what kind of document. It is "
            f"asked over loopback, no key is used, and NOTHING LEAVES YOUR "
            f"DEVICE; `{OPERATION_MODE}` is \"{MODE_SEMANTICS[OPERATION_MODE]}\", "
            f"and a local model is one of them. Protected material and §8.4's "
            f"always-local kinds are refused by P7 and are not among what it is "
            f"shown, the same way they would be refused a model anywhere else.",
            indent=""), file=out)
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
#: The posture above is unchanged. The letters must still be a single uppercase
#: token and the digits must still be three or more, so a date, a sum of money, a
#: page number and a sentence are all still invisible to it.
_STRUCTURED = re.compile(r"\b[A-Z][A-Z0-9]*[ -]?[0-9]{3,}\b")

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

_TERM = re.compile("|".join(
    (_SEASON_YEAR_SOURCE, _ACADEMIC_YEAR_SOURCE, _NAMED_TERM_SOURCE)),
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
#: or the term's name, and the year or the year range. Only case, separators, the
#: written order and the noise word `Term` are dropped.
def _canonical_season_year(raw: str) -> str:
    season = re.search(_SEASON, raw, re.IGNORECASE).group(0)
    return f"{season.capitalize()}{re.search(r'[0-9]{4}', raw).group(0)}"


def _canonical_academic_year(raw: str) -> str:
    match = re.search(r"([0-9]{4})[^0-9]+([0-9]{2})", raw)
    return f"AY{match.group(1)}-{match.group(2)}"


def _canonical_named_term(raw: str) -> str:
    name = re.search(_TERM_NAME, raw, re.IGNORECASE).group(0)
    return f"{name.capitalize()}{re.search(r'[0-9]{4}', raw).group(0)}"


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
))

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
#: **THE SECOND LOOKAHEAD REFUSES A CONCATENATION ACROSS A SPACE.** Two capitals, OR
#: one capital GLUED TO A DIGIT -- and the difference between those two is the whole
#: rule, so it is worth saying what it is about rather than what it matches.
#:
#: `_STRUCTURED` admits one optional separator: `[A-Z][A-Z0-9]*[ -]?[0-9]{3,}`. When
#: that separator is PRESENT, the letters before it are a standalone word of the
#: running text, and a one-letter word before a number is not a department -- it is a
#: roman numeral or a list marker that the pattern then glues onto the number beside
#: it. Byte-exact from the owner's disk:
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
#: number. It IS a truncation of `ENGI E1006`, and it is a truncation this rule
#: cannot repair: `apply_rules` searches `observation.raw_value`, which P4 already
#: cut down to `E1006`, and `ENGI` survives only in `context_before`. So the choice
#: on a glued reading is the token or nothing, and MEASURED it is worth keeping: the
#: five notebooks of that course match their own folder on it, and refusing it took
#: `right parent` from 6 to 2 and `not placed` from 73.2% to 82.9% over the
#: ground-truth corpus while removing no value the labels call correct.
#:
#: THE LABELS DISAGREE WITH BOTH READINGS AND THAT IS RECORDED, NOT RESOLVED. They
#: want `PYTHON1006` -- the person's own FOLDER name, which appears in the corpus 22
#: times but only in `path` and `filename` zones, never in a form this shape reads --
#: and `PHYS1403` for a document that is plainly General Chemistry. Reaching either
#: is a producer this file does not have; inventing one to match a label is not a fix.
#:
#: IT CANNOT BE EXPRESSED BY TIGHTENING `_STRUCTURED`, AND THAT IS DELIBERATE TWICE
#: OVER. The shape's `[A-Z][A-Z0-9]*` lets digits into its own "prefix" -- `E1006`
#: matches as `E` + `1` + `006` -- so the shape has no notion of a letter RUN to
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
    rf"\A\s*(?=[A-Z]{{2}}|[A-Z][0-9])(?!(?i:{_TERM.pattern})\s*\Z)"
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
            claimed = next((one for one in DATE_PATTERNS.patterns
                            if one.pattern.fullmatch(text)), None)
            return None if claimed is None else claimed.canonical(text)
        if field_key == WORK_TYPE_FIELD:
            # `work_type` IS A CLOSED VOCABULARY AND HAD NO BRANCH HERE. Measured
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


def a_fact_prompt() -> PromptDefinition:
    """The one prompt this deployment may send at site A. Composed HERE, not in P8.

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
    return PromptDefinition(
        template_id="a_fact.unratified.folder-levels.2026-09-04",
        template_bytes=a_fact_template_folder_levels_bytes(),
        response_schema_bytes=a_fact_response_schema_bytes(),
        call_site=A_FACT,
        call_site_version="1",
        # RATIFIED, and `planning/82-FACT-PROMPT-DRAFT.md` §0 is the record of it.
        # The id says `unratified` because the folder-levels REVISION has not been
        # put to the owner; what is ratified is the text this revision derives
        # from, and site A has always applied its answers on that basis. Stated
        # here rather than parsed out of the id, which is the whole of the ruling.
        ratified=True,
        shaping_policy_bytes=a_fact_shaping_policy_bytes())


def model_route_permitted(conn: sqlite3.Connection, *, locality: str,
                          unclassified_permits_local: bool):
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
        # PROTECTED IS BARRED ON EVERY LOCALITY, AND THAT IS NOT THIS FIX'S
        # BUSINESS TO WIDEN. `protected_cloud_denies` permits a protected file a
        # LOCAL target, and this route refuses it one anyway: the standing rule is
        # marked and counted, NEVER OPENED, and `tests/integration/
        # test_local_model_fact_pass.py::test_a_protected_file_is_never_sent_to_
        # the_local_model_either` holds it there.
        #
        # That is the route being STRICTER than the gate, which is the safe
        # direction and not the defect R-02 names. R-02 is the route permitting
        # what the gate denies -- a file counted as routed that never had a route.
        # A route that withholds something the gate would have allowed sends
        # nothing it should not; it is a coverage question, and the owner has
        # already answered this one.
        return not record.protected

    return permitted


def fact_call_authorities(conn: sqlite3.Connection, *, routing: TierRouting,
                          scan_run_id: str, corpus_file_count: int,
                          policy_version: str, wire_handle_key: bytes,
                          schema: str, folder_levels: tuple[FolderLevel, ...],
                          user_id: str, now,
                          deferred_readings: tuple[str, ...] = (),
                          usage_recorder: object | None = None,
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

    **The gate's span classifier declines**, and that is the honest binding rather
    than a stub. P7's SPEC files identifier classes and the redaction transform
    under *Deferred* and nothing in `src/` classifies a span into one, so a
    classifier that claimed to would be inventing the vocabulary §8.4 says P7 does
    not own. What holds the always-local set is not that function: it is
    `releasable_observations`' zone and whole-document exclusions, P5's
    `sensitive_observation_keys`, the file-level bar above, and the gate's own
    `_precheck_items`.
    """
    return FactCallAuthorities(
        gate=Gate(
            conn, store=ClassificationStore(conn), plan_version=PLAN_VERSION,
            classifier=lambda value, *, context_before=None, context_after=None: None,
            transform=lambda value, *, identifier_class: "[redacted]",
            # §8.4's Open question 5. ANSWERED `True` ON 2026-09-05, and the
            # answer it replaces was reasoned from a premise the run disproved:
            # "an unclassified file is one nothing has read successfully". 95 of
            # the owner's 199 files were unclassified and every one had evidence.
            # P7 leaves this to the caller precisely because the design does not
            # settle it -- `unclassified_denies`' own docstring warns that denying
            # local calls here "may block exactly the OCR-opaque screenshots §2.7
            # and §7.8 want a model to interpret" -- and `no_safety_evidence_denies`
            # answers the sibling question the same way, permitting local
            # unconditionally. That sibling's own escape hatch read "LOCAL IS
            # PERMITTED, and that is the half that keeps this from being a coverage
            # regression wearing a safety fix's name", and no local model existed,
            # so it became one; the owner narrowed it on 2026-09-07 (`104` §13.2,
            # `96` §20.1). The answer here is untouched by that: local was permitted
            # before and is permitted after.
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
            component_version=COMPONENT_VERSION, now=now, user_id=user_id),
        model_client=routing.client_for(A_FACT),
        prompt=a_fact_prompt(),
        # The SAME target the client is pointed at, read off the client rather than
        # built beside it: two values here would let the gate decide about one
        # destination while the bytes went to another.
        model_target=routing.client_for(A_FACT).model_target,
        activation_signals=ActivationSignals(signals=(
            ActivationSignal(schema_id=schema, activates=lambda facts: True),)),
        folder_levels=folder_levels,
        # §3.6 check 3's per-field alias tables are a Deferred row and this
        # deployment authors none, so the mapping is empty and `normalize_for_model`
        # below is what actually canonicalises. Injected empty rather than omitted:
        # `FactRequest` carries it and a caller that skipped it would be choosing
        # for P6.
        normalizers={},
        normalize=normalize_for_model,
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
        deferred_readings=deferred_readings)


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
        # R-02: the route is asked the same question the gate will answer, with
        # the same locality and the same one answer to Open question 5.
        model_route_permitted=model_route_permitted(
            conn, locality=authorities.model_target.locality,
            unclassified_permits_local=UNCLASSIFIED_PERMITS_LOCAL),
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


#: `router` maps "zip" to the `archive` family, which yields the manifest without
#: extracting anything (§2.5).
_FORMAT_BY_EXTENSION: dict[str, str] = {
    ".pdf": "pdf", ".txt": "txt", ".md": "md", ".docx": "docx", ".zip": "zip"}

#: §2.9's other half, wired here and nowhere else. Built once: `signature_detector`
#: compiles nothing per call, and building it per file would put the protected-
#: container predicate behind a fresh closure on every path this command touches.
_FORMAT_BY_SIGNATURE = signature_detector(
    is_protected_container=is_protected_container)


def _detect_format(path: Path) -> str | None:
    """Which extractor family the bytes belong to: extension, then name, then bytes.

    THREE ANSWERS IN THAT ORDER, AND THE ORDER IS MEASURED. §2.9 reads, on its own,
    as "the detected format wins over the declared extension", and asking the
    signature FIRST is what that sentence says. It was tried against the owner's
    21-file sample on 2026-09-06 and seven files changed their operative format,
    every one of them a file nobody had misnamed:

        five `.ipynb` and one `.code-workspace`  ->  `json`   (they ARE JSON)
        one `.jpeg`                              ->  `jpg`    (one format, two spellings)

    `router.route` records `disagree` when a detected format contradicts a declared
    one, and its own comment keeps that column honest precisely so the disagreement
    "is not manufactured". Seven manufactured rows on twenty-one files is the price
    of reading §2.9 that way, and the extension is the better answer in all seven:
    `ipynb` and `code-workspace` are what those files ARE and `json` is merely what
    they are written in.

    So the extension answers whenever the ROUTER already knows it -- which is a
    wider set than the five formats this deployment maps, and deliberately: a
    `.jpeg` the router understands is not a file the bytes need to rescue.

    THE NAME COMES BEFORE THE BYTES for the same kind of reason. A real `Dockerfile`
    decodes as text, so the signature's weak answer for it is `txt`, and taking that
    would move every Dockerfile on a disk out of `code_structured`. A file named by
    a convention a tool requires has already said what it is.

    THE BYTES ARE THE LAST ANSWER AND THE ONLY NEW ONE. `94` F22: a plain text file
    called `noextension` was named in neither list of the freeze block, and the
    omission half of that is fixed while the routing half was not -- the reason it
    now gives is "nothing has looked inside this one yet", and nothing ever would.
    An extensionless file declares nothing, so there is no routing signal to
    overrule and no disagreement to manufacture. R-30, and the 1,057 extensionless
    files `readers/signatures.py` counted on this disk.

    OPENING A FILE IS NOW POSSIBLE HERE AND THE ONE RULE THAT FORBIDS IT IS OBEYED.
    The older form of this function opened nothing at all and gave that as its
    reason for answering from the path alone: the class of file that must never be
    opened is decided by PATH, before any format question. `signature_detector`
    takes that predicate as a REQUIRED argument and answers `None` for a protected
    path without reading a byte, which is why the reason survives the change and the
    behaviour does not.
    """
    declared = path.suffix.lower().lstrip(".")
    if declared in SOURCE_TYPE_BY_FORMAT:
        return _FORMAT_BY_EXTENSION.get(path.suffix.lower())
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

    One worker is not a pool of one: it is `InlinePool`, the same thread, the same
    call order, no spawn and no seven-second interpreter start for a run of three
    text files. That is the behaviour this product had before the module existed and
    it stays reachable by asking for it, rather than by an option nobody can find.
    """
    if workers == 1:
        return InlinePool(extraction_context())
    return ProcessPool(
        workers=workers, context_factory=extraction_context,
        lookahead_per_worker=EXTRACTION_LOOKAHEAD_PER_WORKER,
        floor=EXTRACTION_POOL_FLOOR,
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
                      created_at: str) -> tuple[str, ...]:
    """The review screen, non-interactively: keep everything, as one named group.

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
        for membership in memberships_for_group(conn, result.group.group_id):
            record_membership(conn, _carried(membership, merged_id))
    record_acceptance(conn, GroupAcceptance(
        acceptance_id=f"acc:{merged_id}", plan_version_id=PLAN_VERSION,
        group_id=merged_id, membership_id=None, acceptance=ACCEPTED,
        review_state=PENDING_REVIEW, user_edited_label=label, aliases=(),
        review_decision_ref=None, decided_by=RULES, created_at=created_at))
    return (merged_id,)


def _carried(membership, group_id: str):
    import dataclasses

    return dataclasses.replace(
        membership, membership_id=f"{membership.membership_id}:{group_id}",
        # NOT a supersession. A file's membership of the group P9 proposed and
        # its membership of the group those were merged into are two records
        # about two groups, not two versions of one. Superseding P9's row made
        # it invisible to `memberships_for_group`, so a second run over the
        # same database re-proposed the group, carried nothing, and handed P11
        # an empty branch.
        group_id=group_id, supersedes=None, supersede_reason=None)


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
        warnings = list(option.warnings)
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
            value = RESIDUAL_REVIEW_BATCH
        elif name == "max_dossier_tokens":
            value = GROUPING_LIMITS.max_dossier_tokens
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

#: The sentence each cause earns. Written out rather than assembled, because a
#: reason a person reads is prose and not a code with a template around it.
WITHHELD_SENTENCE: Mapping[str, str] = MappingProxyType({
    WITHHELD_UNCLASSIFIED:
        "nothing has classified them, and §8.4 makes a handling class a "
        "precondition of asking a model about a file. This is about the "
        "detector, not about your files.",
    WITHHELD_PROTECTED:
        "they are protected material (§8.4), so nothing about them was "
        "assembled for a model. That is a decision about sensitivity and not a "
        "gap in what this run could read.",
    WITHHELD_PRIVACY:
        "this folder's privacy policy does not clear them for the model this "
        "run would ask.",
})


def _print_fact_pass(*, written: int, withheld: Mapping[str, int], files: int,
                     outcomes: Sequence[tuple[str, object]], model_id: str,
                     out) -> None:
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
    for cause, count_ in sorted(withheld.items()):
        print(_wrapped(
            f"{count_} of {files} files were not sent, and were not skipped "
            f"quietly: {WITHHELD_SENTENCE[cause]} Each one has an `unresolved` "
            f"row per open field saying `privacy_withheld`, so none of them is "
            f"recorded as a file with nothing to say.", indent="  "), file=out)
    named = {"CallFailed": "the call did not come back",
             "ValidationUnavailable": "something the check needed was missing",
             "NeedsConsent": "it needs an answer from you first"}
    for kind, count_ in sorted(kinds.items()):
        if kind in named:
            print(f"  {count_} refused: {named[kind]} ({kind}).", file=out)
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


def _print_protected_areas(areas, out) -> None:
    """§1.1's containers: marked, counted, named, and never opened."""
    out = out if out is not None else sys.stdout
    print(f"\nProtected containers: {len(areas)} marked, none opened", file=out)
    for area in areas:
        print(f"  {area.display_label}  ({area.label})", file=out)
        print(f"    {area.path}", file=out)
    if areas:
        print("  Nothing inside these was read, indexed, classified or moved, and "
              "none of them is a place anything can be filed.", file=out)


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
    every edge (`grouping/graph.py` constructs them `weight=None`). With every
    weight equal, §8.6's "reduce to the strongest" cut falls to the file-id
    tiebreak `build_node_local_graph` already applies -- deterministic, and
    honest about ranking nothing.

    `anchor_file_id` is P9's `from_file_id`: the seed the neighbourhood was
    drawn around. `to_file_id` is the OTHER file, whichever end this one is.
    """
    related = []
    for row in conn.execute(
            "SELECT from_file_id, to_file_id, edge_type, weight, "
            "bridge_entity_ref FROM group_edges "
            "WHERE (from_file_id = ? OR to_file_id = ?) "
            "AND superseded_by IS NULL AND hub_suppressed = 0 ORDER BY rowid",
            (file_id, file_id)):
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
        return review_and_accept(db, results, group_category=schema, label=label,
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
                review_decision_ref=None, decided_by=RULES, created_at=clock))

    def set_privacy_policy(db: sqlite3.Connection, plan_version: str) -> None:
        set_policy(db, Policy(
            policy_version=UNSET_POLICY_VERSION, operation_mode=operation_mode,
            consent_grants=(), redaction_settings={},
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

    def evidence_for(file_id: str) -> dict:
        """§6.3's evidence for one file: the facts P6 actually settled about it."""
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
            facts.append(MatchingFact(
                file_fact_id=row["fact_id"], field=row["field_key"],
                value=row["canonical_value"],
                reliability=row["reliability_state"],
                evidence_ref=located[0][0]))
            for ref, location in located:
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
        return dict(
            facts=tuple(facts), evidence_items=tuple(items),
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

    def residual_partition(unplaced: Sequence[str]) -> tuple[dict, ...]:
        """§7.5's review sets. SPEC Open question 10 leaves the taxonomy open, so
        this deployment surfaces the smallest partition that still shows every
        file with a reason -- and protection is the one line it may not cross.

        This used to be ONE set declaring `protected: False` as a literal,
        whatever it actually held. P11 builds a real refusal on that flag:
        `require_set_actionable` reads `residual_set.protected` and raises
        BEFORE any decision, so protection is decided independently of what the
        person chose. Declaring every set unprotected made that refusal
        unreachable -- complete, tested, and never able to fire -- and
        `--send-set` would have filed a passport in one gesture with no
        per-file look.

        So the split is by protection and by nothing else. It is not a taxonomy
        and does not pre-empt Open question 10; it is the one distinction the
        machinery downstream already acts on.
        """
        if not unplaced:
            return ()
        protected = _protected_among(unplaced)
        ordinary = tuple(f for f in unplaced if f not in protected)
        shielded = tuple(f for f in unplaced if f in protected)

        def _set(label: str, members: tuple[str, ...], *, is_protected: bool,
                 reason: str) -> dict:
            return {"label": label, "member_file_ids": members,
                    # Named files, so a person can see WHICH of theirs is here.
                    # Protected files are named and counted like any other: the
                    # rule is that they are never opened, not that they are
                    # never mentioned, and a set that hid them would be the
                    # silent omission the same rule forbids.
                    "representative_examples": members[:3],
                    "file_type_distribution": (), "age_range": (),
                    "evidence_availability": "partial",
                    "sensitivity_status": "protected" if is_protected else "none",
                    "protected": is_protected, "weak_graph_neighbours": (),
                    "reason_not_placed": reason}

        sets: list[dict] = []
        if ordinary:
            sets.append(_set(
                "Not yet placed", ordinary, is_protected=False,
                reason="no destination in this tree matched them well enough "
                       "to decide without asking you."))
        if shielded:
            sets.append(_set(
                "Protected, and not filed in bulk", shielded, is_protected=True,
                reason="these are protected material, so they are counted and "
                       "named here and nothing was assembled about them. They "
                       "are not filed in one gesture with everything else; each "
                       "one is yours to decide."))
        return tuple(sets)

    def _every_destination(frozen) -> tuple[DestinationChoice, ...]:
        """Every place a file can go in this plan, with the path a person reads.

        The `display_path` is the answer's identity -- what a `--answer` line
        carries and what the store keeps -- and the `node_id` is this run's address
        for it. Both come from the same walk so they cannot disagree, which is the
        whole reason the resolution is a lookup rather than a second derivation.

        A node that accepts no placement is not here: an answer naming one would be
        refused by `legal_node_ids` after the person had already given it, which is
        a question whose answer is rejected on the way in.
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

        return tuple(
            DestinationChoice(node_id=node.node_id,
                              display_path=path_of(node.node_id))
            for node in frozen.nodes if node.accepts_placement)

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
            return proposed + ((here,) if here is not None else ())

        return for_folder

    def _node_for(frozen) -> dict[str, str]:
        """Folder chain -> this plan version's node id, built once per tree.

        The answer store holds folder chains and P11 places on node ids, and this
        is the one place the two are joined -- a second one would be a second
        opinion about which folder a person meant.
        """
        return {choice.display_path: choice.node_id
                for choice in _every_destination(frozen)}

    def _home_questions(frozen) -> dict[str, tuple[str, tuple[str, ...]]]:
        """One question per folder nothing could be read from, and the words and
        destinations each of its files carries into P11.

        Recorded HERE rather than in `_raise_blocked_questions`, and the reason is
        the tree: a question offering destinations cannot be written before the
        destinations exist, and they exist when the plan is frozen. The recording
        is idempotent by question id, so the second call for the residual pass adds
        nothing.
        """
        node_for = _node_for(frozen)
        offer_for = _destinations_to_offer(frozen)
        asks: dict[str, tuple[str, tuple[str, ...]]] = {}
        for folder, file_ids, held in folders_nothing_could_be_read_from(
                conn, root=directory):
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
                protected_count=held)
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
        and P10's own floor inside `settled_values_stated_by_every_file` refuses
        a folder of one for the same reason ("a set of one is always unanimous").
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
        made_for: dict[str, str] = {}
        for node in frozen.nodes:
            if node.existing_path is None:
                continue
            here = file_ids_in_directory(conn, directory_path=node.existing_path)
            if len(here) <= TREE_LIMITS.tiny_folder_max_files:
                continue
            if not settled_values_stated_by_every_file(
                    conn, directory_path=node.existing_path):
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
            plan_version=tree.tree.plan_version_id) if fact_authorities else {})
        asks = _home_questions(tree.tree)
        node_of = _node_for(tree.tree)

        def already_answered(subject) -> str | None:
            """The node the person's answer names, in THIS plan version's tree.

            Keyed on the FOLDER the file is in, because that is the scope the
            question was asked at and §13 forbids reading an answer outside its
            stated scope. A file that arrived in the folder after the answer was
            given is covered by it, which is what a person means when they answer
            about a folder rather than about three files.

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
            row = conn.execute("SELECT current_path FROM files WHERE file_id = ?",
                               (subject.file_id,)).fetchone()
            if row is None:
                return None
            try:
                folder = str(PurePosixPath(
                    Path(row[0]).relative_to(directory).as_posix()).parent)
            except ValueError:
                return None
            named = chosen_destination(conn, scope=f"{SCOPE_FOLDER}:{folder}")
            return None if named is None else node_of.get(named)

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
            return
        if (routing.locality_for(A_FACT) == CLOUD
                and operation_mode != CLOUD_ENABLED_MODE):
            # BY LOCALITY, not by mode alone, and the cloud half is unchanged: a
            # cloud target still requires `hybrid`, which still requires this
            # folder's stored consent. What the mode-only test also refused was a
            # model on the person's OWN MACHINE, which `00`:189-193 permits under
            # every mode including `offline` -- "No content leaves the device;
            # only local rules and LOCAL MODELS may run". Nothing is released to a
            # local target that would not be released to a cloud one; the gate
            # makes that decision below, from the same `model_target`, and it is
            # `Gate.release` that reads the locality rather than this line.
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
            return

        policy_version = set_policy(
            conn,
            Policy(policy_version=UNSET_POLICY_VERSION,
                   operation_mode=operation_mode, consent_grants=(),
                   redaction_settings={}, automatic_move_permissions={},
                   plan_version=PLAN_VERSION, set_at=clock),
            component_version=COMPONENT_VERSION, user_id=user_id,
            reason=f"{operation_mode} run: fact extraction, before grouping")

        outcomes: list[tuple[str, object]] = []
        authorities = fact_call_authorities(
            conn, routing=routing, scan_run_id=run_id,
            corpus_file_count=len(roster), policy_version=policy_version,
            wire_handle_key=wire_handle_key, schema=schema,
            folder_levels=folder_levels, user_id=user_id,
            now=now,
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

        written: list[str] = []
        # WHY EACH FILE WAS WITHHELD, not just how many. The route bars for two
        # different reasons and `PRIVACY_BAR` is one word for both, so the screen
        # said "nothing has classified them" about a file that IS classified and
        # was withheld for being protected. `104` R-02 widened the route to bar
        # unclassified files on a cloud target as well, which puts a third
        # sentence behind the same word. The store is asked here, where the file
        # ids still are, and `_print_fact_pass` prints what it is told.
        store = ClassificationStore(conn)
        withheld: dict[str, int] = {}
        for file_id, content_hash in roster:
            result = resolver.resolve(
                conn, file_id=file_id, content_hash=content_hash)
            written.extend(result.fact_ids)
            if result.stages_barred.get(LLM_ROUTE) != PRIVACY_BAR:
                continue
            row = get_file(conn, file_id)
            record = (store.current(file_id, row["content_hash"])
                      if row is not None else None)
            cause = (WITHHELD_UNCLASSIFIED if record is None
                     else WITHHELD_PROTECTED if record.protected
                     else WITHHELD_PRIVACY)
            withheld[cause] = withheld.get(cause, 0) + 1
        _print_fact_pass(
            written=len(written), withheld=withheld,
            files=len(roster), outcomes=outcomes,
            model_id=routing.model_id_for(A_FACT), out=out)

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
        # §8.6's THIRD producer, and the only point in the run where it can stand.
        # See `model_fact_resolver` for why it is a second pass and not the `llm`
        # stage of the pass P1-P7 already ran. BEFORE the three blocks below on
        # purpose: they report what the scan found, and a fact this pass writes is
        # part of what the scan found.
        _model_fact_pass(p1_p7.scan_run_id)
        # AFTER the fact pass, because that is what builds the authorities these
        # borrow, and BEFORE P9 groups, because that is what asks site B.
        observe_b = (observe_group_authorities(
            fact_authorities[0], routing=routing, situation=situation)
            if fact_authorities else (None, None))
        # HERE, and not in `report`. The scan has finished and every design stage
        # after this point can refuse by name -- and `main` reaches `report` only
        # when none of them does. Printed at the end, the count of what was marked
        # and left unopened was dropped from every refused run: the verdict sat in
        # `exclusion_verdicts` and the person was told nothing. "Marked, counted,
        # never silently omitted" has no success-path exception, so it is said as
        # soon as it is known.
        _print_protected_areas(
            protected_areas(conn, scan_run_id=p1_p7.scan_run_id), out)
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
                duplicate_or_version=_duplicate_or_version),
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
    _raise_blocked_questions(conn, detector=detector, asked_at=clock)
    return result


def _raise_blocked_questions(conn: sqlite3.Connection, *, detector,
                             asked_at: str) -> None:
    """Record every question THIS corpus's own ambiguities raise (P15).

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
    for question in tied_readings(conn, explain=detector.explain,
                                  files=files_with_observations(conn),
                                  subject_of=subject_of):
        record_question(conn, question, asked_at=asked_at)


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


#: P4's two ceiling completenesses, and they are NOT interchangeable: `capped` read
#: something and stopped, `deferred` never started. `extractors/stage_output.py`
#: holds them as one tuple because both mean "a budget was reached"; the sentences
#: they earn are different, which is why each is named here.
CAPPED: str = "capped"
DEFERRED: str = "deferred"

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
PROTECTED_SUMMARY: tuple[str, ...] = (
    "{count} protected file{plural}, marked and counted, and none of them "
    "opened. Their names are not printed here, because a list of them is the "
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


def _review_note(items: Sequence, areas: Sequence[str]) -> tuple[str, ...]:
    """Why these sets are being held, and what a person can type about each one.

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
    files, measured. It is said once here and the batches are named beneath it.

    **The batches are not one fact.** `act_on_residual_sets` addresses a set by
    the label the report printed and refuses a bare label that names no surfaced
    set, so one `--send-set` files ONE batch -- and the sentence beside it may
    not say it files them all, which is what it used to say.

    A hold with no command beside it is the product saying it noticed and will do
    nothing. With no residual area enabled the sentence says how to make one
    rather than naming a flag that would refuse.
    """
    by_reason: dict[tuple[bool, str], list] = {}
    for item in items:
        by_reason.setdefault((item.protected, item.reason_not_placed),
                             []).append(item)
    lines: list[str] = []
    for (protected, reason), held in by_reason.items():
        opening = f'Held for review as "{held[0].label}": {reason}'
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
        if areas[1:]:
            lines.append(f'This plan also has {", ".join(areas[1:])}.')
        elif not areas:
            lines.append(
                "This plan has nowhere to put them yet: enable an area with "
                '`--residual "Review Later"` and each of these sets can be sent '
                "there with one command.")
    return tuple(lines)


def report(result: ProductionRun, names: dict[str, str], *, out=None,
           questions: Sequence = (), set_aside: Sequence = (),
           role_moment: Sequence[str] = (),
           roles_held: Sequence[str] = (),
           invite_freeze: bool = False,
           list_every_name: bool = False,
           show_protected: bool = False,
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
        key = (decision.outcome, where, reason, review,
               decision.review_policy if decision.outcome == pv.PLACE else None,
               settled, same_folder)
        members.setdefault(key, []).extend(_files_of(decision))
        shielded[key] = shielded.get(key, False) or _protected(decision, sets)
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

    print(f"\nFiles: {len(decisions)} decided, {placed} ready to file"
          + (f", {awaiting} waiting for you to approve" if awaiting else ""),
          file=out)
    for key in ordered:
        outcome, where, reason, review, policy, settled, same_folder = key
        files = sorted(members[key], key=lambda f: names.get(f, f))
        # A placement's headline comes from its REVIEW POLICY, because that is
        # what says whether anything may happen to the file. An unknown policy
        # falls back to the outcome's word rather than to silence, for the same
        # reason `OUTCOME_WORDS` prints an unknown outcome's own name: a gap in
        # this deployment's vocabulary must never become a file that vanished.
        words = (SAME_FOLDER if same_folder
                 else ALREADY_THERE if settled else PLACEMENT_WORDS)
        sentence = words.get(policy) if outcome == pv.PLACE else None
        if sentence is not None and where:
            heading = sentence.format(where=where)
        else:
            heading = OUTCOME_WORDS.get(outcome, outcome)
            if where:
                heading = f"{heading} into {where}"
        plural = "" if len(files) == 1 else "s"
        print(f"\n  {heading} -- {len(files)} file{plural}", file=out)
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
            for file_id in listed:
                print(f"    {names.get(file_id, file_id)}", file=out)
            rest = len(files) - len(listed)
            if rest:
                print(_wrapped(
                    f"...and {rest} more, counted here rather than listed one by "
                    "one so that the list stays shorter than the folder it "
                    "describes. None of these is protected material: that is "
                    "counted in its own block, with the way to see it printed "
                    "there -- summarised, but never silently", indent="    "),
                    file=out)
        if reason:
            print(_wrapped(f"Same reason for each: {reason}", indent="    "),
                  file=out)
        # `_role_lines`' convention: a line that begins with a space is a line
        # the person is meant to paste, and it is printed exactly as it is.
        for note in _review_note(held_sets.get(key, ()), areas):
            print(note if note.startswith(" ")
                  else _wrapped(note, indent="    "), file=out)

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
        blocking = [q for q in questions
                    if not q.scope.startswith(f"{SCOPE_BRANCH}:")]
        offers = [q for q in questions if q.scope.startswith(f"{SCOPE_BRANCH}:")]

        def ask(question) -> None:
            print(f"\n  {question.prompt}", file=out)
            print(_wrapped(question.evidence_context, indent="    "), file=out)
            for option in question.options:
                print(f"      --answer {_typable(question, option.option_id)}"
                      f"   {option.label}", file=out)
            print(f"      --answer {_typable(question, 'skip')}"
                  f"   Skip for now", file=out)
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
                    already_filed=sorted(plan.file_id for plan in chosen
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
    shown = report(result, file_names(conn, directory, *also_read), out=out,
                   questions=open_now,
                   set_aside=set_aside_questions(conn),
                   role_moment=role_moment_lines(blocked=open_now,
                                                 already_declared=held),
                   roles_held=role_panel_lines(held),
                   invite_freeze=not args.freeze,
                   list_every_name=args.freeze,
                   show_protected=args.show_protected,
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
        high_level_folders={ROOT_ANCHOR: directory,
                            **{str(folder): folder
                               for folder in (*also_read, *candidate_roots)}},
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
