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
from itertools import count
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Mapping, Sequence

from database_agent.budget import set_ceiling
from database_agent.cloud_consent import (
    DISABLED, ENABLED, CloudConsent, cloud_consent_for, record_cloud_consent,
)
from database_agent.db import DatabaseInsideCorpus, open_database
from extractors.reading import StructuredString
from extractors.structured_text import EXTRACTOR_NAME as STRUCTURED_EXTRACTOR
from extractors.safety import SafetyPolicy
from facts.date_facts import date_facts
from facts.dates import (
    ACADEMIC_YEAR_RANGE, NAMED_TERM_YEAR, SEASON_YEAR, DatePattern, DatePatterns,
)
from facts.direct import DirectSlot, DirectSlots, direct_facts
from facts.discount import MetadataScreen
from facts.learning import NoSuchClaim, reject_claim
from facts.resolver import FactResolver
from facts.unresolved import NO_CANDIDATE_EVIDENCE
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
    ACCEPTED, COHERENT, P1_INCLUDED_SCAN_STATE, PENDING_REVIEW, RULES, USER_EDITED,
)
from llm_harness.budgets import create_budget_schema
from llm_harness.schema import create_llm_schema
from llm_harness.vocabulary import (
    A_FACT, B_GROUP, C_PLACEMENT, D_RESIDUAL, E_TEMPLATE,
)
from placement import vocabulary as pv
from placement.config import CEILINGS, SupportPolicy, placement_limits
from placement.pipeline import (
    PipelineInputs, ResidualSendRefused, act_on_residual_sets,
)
from placement.residual import ProtectedSetNotReadable, prior_set_decisions
from placement.schema import create_placement_schema
from privacy.classification_store import ClassificationStore
from privacy.defaults import LOCAL_FIRST_MODES
from privacy.display import display_policy
from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy
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
    activated_schemas, gated_template, live_answer, live_answer_id, open_questions,
    record_answer,
    record_question, set_aside_questions,
)
from questions.triggers import (
    NestingChoice, question_for_nesting, tied_readings,
)
from questions.vocabulary import CONFIRMED, REVOKED, SCOPE_BRANCH, SKIPPED
from production import (
    CorpusAuthorities, CorpusDecisions, P1P7Authorities, ProductionRun,
    bootstrap_p1_p7, load_shipped_catalogue, nearest_situations,
    read_packaged_library_file, schema_for_situation, shipped_situations,
    run_production_corpus,
)
from readers.deployment import macos_readers
from readers.model_deepseek import BASE_URL_NAME, CREDENTIAL_NAME
from readers.model_routing import (
    FAST, LOGIC, MODEL_NAME_OF_TIER, REASONING, TierRouting, deepseek_routing,
)
from facts.domains import SCHEMA_IDS
from recognition.detector import (
    SAFETY_DOMAIN_HANDLING, Detector, Handling,
)
from recognition.rules import load_rules
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
    UpstreamUnavailable, existing_folders, handling_class_for, protected_areas,
)
from tree_design.schema import create_tree_schema
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
from review_surface.schema import create_review_schema
from review_surface.vocabulary import ACTION_REJECT
from tree_design.residuals import (
    ResidualChoice, ResidualTemplate, build_library,
)
from tree_design.vocabulary import (
    ENABLE, MANDATORY_REVIEW, PHYSICAL_DESTINATION, REFINED,
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
    # months later. `00` §3.6 already demands the model return `unknown` rather
    # than guess, and the model most able to decline is the one worth paying for.
    A_FACT: REASONING,
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
MAX_RESPONSE_TOKENS: int = 2048

#: Where this deployment keeps its own values. Read here and nowhere else in `src/`.
ENV_FILE: Path = Path(__file__).resolve().parents[1] / ".env"

#: Whether any call site in this run can actually reach a model.
#:
#: A ROUTE IS NOT A CALL SITE, and conflating them put an untruth on the one screen
#: that must not carry one. `model_route` builds a client and this file announced
#: that files "may be sent to" three named models -- while `p8_run_call`,
#: `model_client`, `gate`, `prompt` and `call_dependencies` are `None` at every
#: injection point below, so nothing in `src/` can construct a model request at all.
#: A person who read that sentence and turned sending off was acting on a fear the
#: product had given them about something that could not happen; a person who read
#: it and left it on believed they had been told the truth about their files.
#:
#: FALSE until the sites are wired AND a prompt is ratified. `run_call` refuses
#: without a `PromptDefinition` (`llm_harness/records.py:89`), so a route plus a key
#: plus a wired site still sends nothing until the owner ratifies one -- which means
#: flipping this on the strength of the wiring alone would restore the same untruth
#: one step later. `tests/integration/test_cli_cloud_announcement.py` asserts this
#: against the injections themselves, so it cannot drift from what is true.
MODEL_CALL_SITES_WIRED: bool = False

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


def model_route(*, out) -> TierRouting | None:
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

    supplied = _dotenv(ENV_FILE)

    def value(name: str) -> str:
        # The environment first, then the file, then nothing. Never a literal.
        return (environ.get(name) or supplied.get(name) or "").strip()

    if not value(CREDENTIAL_NAME):
        print(f"\nNo model was consulted: {CREDENTIAL_NAME} is not set, so this "
              f"run used only what it could read and decide on this device. Files "
              f"that needed a judgement are named below and say so. To enable one, "
              f"copy `.env.example` to `.env` and put a key in it.", file=out)
        return None
    try:
        routing = deepseek_routing(
            api_key=value(CREDENTIAL_NAME),
            base_url=value(BASE_URL_NAME),
            model_id_of_tier={tier: value(name)
                              for tier, name in MODEL_NAME_OF_TIER.items()},
            tier_of_call_site=TIER_OF_CALL_SITE,
            max_response_tokens=MAX_RESPONSE_TOKENS)
    except (ValueError, RuntimeError) as refusal:
        # Every refusal `readers/` can raise names what was missing and what to
        # set. Printed, not raised: a misconfigured model is not a reason to
        # refuse a scan that needs no model to do most of its work.
        print(f"\nNo model was consulted, and here is what it needed:\n"
              f"  {refusal}", file=out)
        return None
    return routing


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
            print(_wrapped(
                f"Files that need a judgement may be sent to "
                f"{routing.model_id_for(A_FACT)} (facts), "
                f"{routing.model_id_for(C_PLACEMENT)} (checks) and "
                f"{routing.model_id_for(D_RESIDUAL)} (review sets). Protected "
                f"material and §8.4's always-local kinds are refused by P7 and "
                f"are not among them. Turn it off with:", indent="  "), file=out)
        print(_turn_off_line(corpus_root, *other_sources), file=out)
        return
    if routing is None:
        # `model_route` has already said no model is configured. A second sentence
        # about consent would answer a question the person cannot yet be asking.
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
    unwired = ("" if MODEL_CALL_SITES_WIRED else
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
_SEASON_YEAR_SOURCE = (
    rf"\b(?:{_SEASON}[ \-_]?[0-9]{{4}}|[0-9]{{4}}[ \-_]?{_SEASON})\b")
_ACADEMIC_YEAR_SOURCE = r"\bAY[ \-_]?[0-9]{4}[ ]?[-/][ ]?[0-9]{2}\b"
_NAMED_TERM_SOURCE = rf"\b{_TERM_NAME}(?:[ \-_]Term)?[ \-_][0-9]{{4}}\b"

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

#: The field §3.10's producer fills. Spelled once, because `active_schema_for` and
#: `normalize_for_model` both need it and neither may re-spell it.
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
        names=reads_a_structured_string,
        # Everything the term slot does not claim. Without this the two slots
        # would each take the other's readings -- they share every locator there
        # is -- which is why only one of them could ship before `DirectSlot`
        # gained a predicate over the reading itself.
        matches=lambda raw: not _is_term(raw),
        # Whitespace collapsed, THEN the identifier's own separator removed, so
        # the two spellings of one course code canonicalise to one value.
        canonical=lambda raw: _SEPARATOR.sub("", " ".join(raw.split()))),
))

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


def _rule_stage(conn, file_id: str, content_hash: str) -> tuple[str, ...]:
    """§8.6's second producer: §3.10's dates, ranked as §3.7 requires.

    Not `apply_rules`: this deployment still ships no authored rule set, and a
    course code is already read by the `subject` slot above. What it ships is the
    date path, which had been written in full across two modules and called from
    nowhere.
    """
    return date_facts(conn, file_id=file_id, content_hash=content_hash,
                      field_key=TERM_FIELD, patterns=DATE_PATTERNS,
                      zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT,
                      minimum_score=MINIMUM_SCORE, minimum_margin=MINIMUM_MARGIN)


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


def _mime_type_for(path: Path) -> str | None:
    import mimetypes

    return mimetypes.guess_type(str(path))[0]


def _detect_format(path: Path) -> str | None:
    """Which extractor family the bytes belong to, by extension only.

    Extension rather than content sniffing, and that is a choice: sniffing means
    opening the file, and the one class of file this command must never open is
    decided by PATH (`is_protected_container`) before any format question is asked.
    """
    return {".pdf": "pdf", ".txt": "txt", ".md": "md",
            ".docx": "docx",
            # `router` maps "zip" to the `archive` family, which yields the
            # manifest without extracting anything (§2.5).
            ".zip": "zip"}.get(path.suffix.lower())


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


def p1_p7_authorities(*, now, detector,
                      operation_mode: str = OPERATION_MODE,
                      source=None) -> P1P7Authorities:
    # `source` is an ARGUMENT with the live filesystem as its default, because
    # `--record` needs the scan wrapped in a `RecordingCorpusSource` -- the
    # listings it serves ARE the corpus snapshot, and they cannot be recovered
    # afterwards. Not a policy: the default is unchanged and every ordinary run
    # still reads the disk.
    return P1P7Authorities(
        native_resolver=_resolver(tiers=frozenset(("filesystem", "native")),
                                  cache_key="cli-native-v1"),
        ocr_resolver=_resolver(
            tiers=frozenset(("filesystem", "native", "ocr")),
            cache_key="cli-ocr-v1"),
        usable_threshold=_usable,
        classify=classifier(detector, now=now),
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
        corpus_form="snapshot", policy_settings={"operation_mode": operation_mode},
        file_entry_body=lambda row: {"payload_ref": row["content_hash"]},
        p7_component_version=COMPONENT_VERSION)


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
    warnings and their validation report; this takes the first that passes and has
    children, and falls back to the last option -- which is always `no-split` --
    rather than raising, because a branch nobody could nest is still a branch.
    """
    for option in options:
        report = option.validation
        if option.total_child_branches and (report is None or report.accepted):
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
        # Named, so the one that is not a spend ceiling is visibly not one.
        set_ceiling(conn, key,
                    RESIDUAL_REVIEW_BATCH if name == "max_residual_files_per_batch"
                    else CEILING_VALUE)


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


def run(conn: sqlite3.Connection, directory: Path, *, situation: str, label: str,
        user_id: str, now, out=None,
        also_read: Sequence[Path] = (),
        candidate_roots: Sequence[Path] = (),
        cross_folder_moves: bool = False,
        residuals: Sequence[str] = (),
        sends: Mapping[str, str] = MappingProxyType({}),
        operation_mode: str = OPERATION_MODE,
        record: str | None = None) -> ProductionRun:
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
    detector = Detector(load_rules(_RECOGNITION_MANIFEST.read_text),
                        handling_for=HANDLING_POLICY, now=now,
                        is_protected=is_protected_container,
                        corroborating_observations=_identifier_observations,
                        # P15. What the PERSON has confirmed about readings their
                        # own files could not settle. Read fresh on every call
                        # rather than captured, so an answer given by `--answer`
                        # earlier in this same invocation is already in force.
                        settled_by_user=lambda: activated_schemas(conn))

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
            residual_refinement=(
                SHALLOW_BY_CHOICE,
                "This is a home for files that do not belong to any one "
                "folder. It is meant to stay flat, so nothing here will be "
                "split into deeper folders."),
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

    def evidence_for(file_id: str) -> dict:
        """§6.3's evidence for one file: the facts P6 actually settled about it."""
        facts, items = [], []
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

            refs = json.loads(row["evidence_refs"] or "[]")
            ref = refs[0] if refs else None
            facts.append(MatchingFact(
                file_fact_id=row["fact_id"], field=row["field_key"],
                value=row["canonical_value"],
                reliability=row["reliability_state"],
                evidence_ref=ref))
            items.append(EvidenceItem(
                evidence_ref=ref, kind="fact", location="heading",
                excerpt_span=(0, len(row["canonical_value"])),
                reliability_state=row["reliability_state"],
                basis="direct-anchor"))
        return dict(
            facts=tuple(facts), evidence_items=tuple(items),
            group_ids=tuple(accepted_ids),
            curated_folder_labels=_folders_this_file_is_already_in(file_id),
            semantic_neighbours=(), related_files=(),
            # §6.5's generic-entity suppression. A value seen in more files than
            # this is treated as a hub rather than as a discriminator. Both numbers
            # are this deployment's; `00` states neither.
            entity_frequency={fact.value: 1 for fact in facts},
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
                # §4.4's retrieval channels. This deployment runs no embeddings, so
                # every similarity channel is off and retrieval is by shared
                # validated fact alone -- the deterministic path P9 is explicit is
                # a complete path.
                retrieval=RetrievalKnowledge(
                    document_compatible=None, channel_weights={}, similarity=None,
                    similarity_threshold=None, embedding_identity=None,
                    domain=None),
                # `DIRECT_SLOTS` is no longer the whole of the schema: `term`
                # is filled by `_rule_stage` and has no slot (SPEC:409-410). A
                # field missing here is a field P9 will not group on.
                active_schema_for=lambda db, file_id, content_hash: (
                    tuple(slot.field_key for slot in DIRECT_SLOTS.slots)
                    + (TERM_FIELD,)),
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
            now=now, detector=detector, operation_mode=operation_mode,
            source=recording),
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
    files = [(row[0], row[1]) for row in conn.execute(
        "SELECT DISTINCT file_id, content_hash FROM evidence")]
    for question in tied_readings(conn, explain=detector.explain, files=files,
                                  subject_of=subject_of):
        record_question(conn, question, asked_at=asked_at)


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
        rows = conn.execute(
            "SELECT file_id, content_hash, current_path FROM files "
            "WHERE filename = ? ORDER BY current_path", (filename,)).fetchall()
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
     "the top-level folder is treated as fully refined, and everything under it "
     "as deliberately shallow. Nobody was asked whether a branch is short "
     "on purpose or just unfinished."),
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
    """
    ordered = sorted(roots, key=lambda root: len(Path(root).parts), reverse=True)
    names: dict[str, str] = {}
    for row in conn.execute("SELECT file_id, current_path FROM files"):
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
        # `nargs="?"` with a `const` and NOT a bare flag: `--replay` on its own
        # must be a refusal that names the bundles this database holds, not
        # argparse's "expected one argument". A person cannot type an id they
        # have never been shown, and a discovery flag that requires the answer
        # it supplies is the closed door `--list-situations` exists to open.
        # Absent stays absent: `default=None` means the flag was not passed and
        # nothing is replayed.
        "--record", nargs="?", const="", default=None, metavar="NAME",
        help="record this run as a replay bundle you can come back to, e.g. "
             "--record before-upgrade. It runs exactly as it would anyway and "
             "moves nothing; what it adds is a frozen copy of what was read, "
             "which --replay re-reads without touching your folder again. The "
             "name is yours and must not already be taken.")
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
    # BEFORE the run, and printed whichever way it goes. If this deployment cannot
    # call a model the person is told once, at the top, in a sentence about the
    # deployment -- rather than left to infer it from thirty file-level sentences
    # at the bottom that each read as a statement about one of their files.
    routing = model_route(out=out)
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
                     record=args.record)
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
