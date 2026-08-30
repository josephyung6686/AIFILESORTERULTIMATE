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
import json
import re
import shlex
import sqlite3
import sys
import uuid
import textwrap
from itertools import count
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Mapping, Sequence

from database_agent.budget import set_ceiling
from database_agent.db import DatabaseInsideCorpus, open_database
from extractors.reading import StructuredString
from extractors.structured_text import EXTRACTOR_NAME as STRUCTURED_EXTRACTOR
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
    ACCEPTED, COHERENT, P1_INCLUDED_SCAN_STATE, PENDING_REVIEW, RULES, USER_EDITED,
)
from llm_harness.budgets import create_budget_schema
from llm_harness.schema import create_llm_schema
from placement import vocabulary as pv
from placement.config import CEILINGS, SupportPolicy, placement_limits
from placement.pipeline import (
    PipelineInputs, ResidualSendRefused, act_on_residual_sets,
)
from placement.residual import ProtectedSetNotReadable
from placement.schema import create_placement_schema
from privacy.classification_store import ClassificationStore
from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy
from questions.records import StructuralAnswer
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
from facts.domains import SCHEMA_IDS
from recognition.detector import (
    SAFETY_DOMAIN_HANDLING, Detector, Handling,
)
from recognition.rules import load_rules
from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.exclusion import is_protected_container
from scan_agent.selection import record_selection
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
from review_surface.schema import create_review_schema
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
OPERATION_MODE: str = "offline"

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

#: THE SECOND DIMENSION. A term or period, in the two spellings people write:
#: `Fall 2026`, `Spring2026`, and `2026-Spring`. `00`:78's own recommended tree is
#: `Academics/Columbia/2026-Spring/PHYS1401/Homework`, so a term is one of the four
#: levels the design asks for by name -- and until now the pattern above swallowed
#: it: `SPRING2026` is letters-then-digits, so a SEMESTER was read as a course
#: code, and a household's report cards were proposed a folder named after a term
#: pretending to be a subject.
#:
#: Four seasons and a four-digit year, and nothing else. Not a general date
#: parser: §2.2's classes are "URLs, email addresses, DOI values, citations,
#: identifiers", a free date is none of them, and a pattern that matched every
#: number pair would put page numbers and sums of money into the tree.
def _is_term(raw: str) -> bool:
    """Whether a reading is a TERM rather than an identifier.

    Asked of the READING, which is the only place the two can be told apart: they
    sit in the same body text and share every locator prefix.
    """
    return _TERM.fullmatch(raw.strip()) is not None


_TERM = re.compile(
    r"\b(?:(?:Fall|Spring|Summer|Winter)[ -]?[0-9]{4}"
    r"|[0-9]{4}[ -]?(?:Fall|Spring|Summer|Winter))\b", re.IGNORECASE)


def _is_term(raw: str) -> bool:
    """Whether a reading is a term rather than an identifier.

    Asked of the READING, which is the only place the two can be told apart: they
    sit in the same body text and share every locator prefix, so `names` alone
    cannot separate them and a deployment could ship only one text slot.
    """
    return _TERM.fullmatch(raw.strip()) is not None

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
    DirectSlot(
        slot_id="cli.text.term", field_key="term",
        names=reads_a_structured_string,
        matches=lambda raw: _is_term(raw),
        # ONE spelling for `Spring 2026`, `Spring-2026` and `SPRING2026`. The
        # course codes taught this lesson already: `65` §4.2 records four files
        # of one course becoming four one-file groups because one identity
        # arrived as several spellings. `2026-Spring` keeps its own ORDER --
        # which of the two a corpus uses is the corpus's, and reordering it would
        # be inventing a label §5.4 says must emerge from the facts.
        canonical=lambda raw: "".join(raw.split()).replace("-", "").title()),
))

#: THE SECOND DIMENSION, WRITTEN AND NOT SHIPPED. `00`:78's recommended tree is
#: `Academics/Columbia/2026-Spring/PHYS1401/Homework`, so a term is one of the four
#: levels the design asks for by name -- and `_STRUCTURED` swallows it, because
#: `SPRING2026` is letters-then-digits and a SEMESTER therefore reads as a course
#: code. A household's report cards are proposed a folder named after a term
#: pretending to be a subject.
#:
#: Shipping it makes two of four personas WORSE, and the reason is not this
#: pattern. A term level with one value trips V2, which fails the WHOLE candidate
#: rather than skipping the redundant level, so the four-role corpus went from
#: five folders to one. That is V5's mistake in a third place and it is a P10
#: contract decision -- `tests/integration/test_production_corpus.py` carries the
#: strict xfail that states it.
#:
#: This stays here, unwired and named, because the next person to reach for it
#: should find the blocker rather than the idea. P6 already carries the other half
#: (`DirectSlot.matches`), which is what makes two text slots possible at all.
_TERM = re.compile(
    r"\b(?:(?:Fall|Spring|Summer|Winter)[ -]?[0-9]{4}"
    r"|[0-9]{4}[ -]?(?:Fall|Spring|Summer|Winter))\b", re.IGNORECASE)

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
    return bool(facts) or bool(unresolved)


def p1_p7_authorities(*, now, detector) -> P1P7Authorities:
    return P1P7Authorities(
        native_resolver=_resolver(tiers=frozenset(("filesystem", "native")),
                                  cache_key="cli-native-v1"),
        ocr_resolver=_resolver(
            tiers=frozenset(("filesystem", "native", "ocr")),
            cache_key="cli-ocr-v1"),
        usable_threshold=_usable,
        classify=classifier(detector, now=now),
        source=FilesystemCorpusSource(),
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
        corpus_form="snapshot", policy_settings={"operation_mode": OPERATION_MODE},
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
    grouped = [result for result in results if result.group is not None]
    if not grouped:
        return ()
    first = grouped[0].group
    # The category is part of the address, not only the label. Two situations
    # filed under one `--label` are two groups of two different kinds, and an
    # id built from the label alone asks them to be one record -- which P9
    # refuses, correctly, as a revision that supersedes nothing.
    merged_id = f"{PLAN_VERSION}:{group_category}:{label}"
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
    for key in CEILINGS.values():
        set_ceiling(conn, key, CEILING_VALUE)


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


def run(conn: sqlite3.Connection, directory: Path, *, situation: str, label: str,
        user_id: str, now, out=None,
        residuals: Sequence[str] = (),
        sends: Mapping[str, str] = MappingProxyType({})) -> ProductionRun:
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
    selection_id = record_selection(
        conn, sources=[directory], candidate_roots=[], cross_folder_moves=False,
        selected_by=user_id)
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

        def inside_a_protected_area(path: str) -> bool:
            return any(path == area or path.startswith(area.rstrip("/\\") + "/")
                       or path.startswith(area.rstrip("/\\") + "\\")
                       for area in sealed)

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
            and not inside_a_protected_area(folder.directory_path))

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
            policy_version=UNSET_POLICY_VERSION, operation_mode=OPERATION_MODE,
            consent_grants=(), redaction_settings={},
            # §8.4: protected material is not moved automatically without a policy
            # that permits it. This deployment permits none, so nothing protected
            # moves and P11 records the refusal on the decision.
            automatic_move_permissions={}, plan_version=plan_version,
            set_at=clock), component_version=COMPONENT_VERSION, user_id=user_id,
            reason="offline run from the command line")

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
            group_ids=tuple(accepted_ids),
            curated_folder_labels=_folders_this_file_is_already_in(file_id),
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
        # HERE, and not in `report`. The scan has finished and every design stage
        # after this point can refuse by name -- and `main` reaches `report` only
        # when none of them does. Printed at the end, the count of what was marked
        # and left unopened was dropped from every refused run: the verdict sat in
        # `exclusion_verdicts` and the person was told nothing. "Marked, counted,
        # never silently omitted" has no success-path exception, so it is said as
        # soon as it is known.
        _print_protected_areas(
            protected_areas(conn, scan_run_id=p1_p7.scan_run_id), out)
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

    result = run_production_corpus(
        conn, selection_id, authorities=p1_p7_authorities(now=now,
                                                          detector=detector),
        downstream=downstream,
        decisions=CorpusDecisions(
            plan_version_id=PLAN_VERSION, accept_groups=accept_and_remember,
            design=design_decisions, approve_plan=approve_plan,
            set_privacy_policy=set_privacy_policy))
    # AFTER the run, because §7.5's sets do not exist until §6 has finished trying,
    # and IN the same run, because a residual set answer belongs to the plan
    # version it was given in (P11 SPEC, "Plan versioning") and this run has just
    # minted a new one. So `--send-set` is applied to the sets it was typed at and
    # is not remembered between runs: the run that files the files is the run the
    # person named them in.
    if sends:
        result = dataclasses.replace(result, placement=act_on_residual_sets(
            conn, result=result.placement,
            inputs=placement_inputs(result.tree), sends=sends,
            evidence_for=evidence_for, component_version=COMPONENT_VERSION,
            observed_at=now(), user_id=user_id))
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


class AnswerRefused(NotConfigured):
    """`--answer` named something this database has never asked about."""


def apply_answers(conn: sqlite3.Connection, answers: Sequence[str], *,
                  user_id: str, recorded_at: str) -> None:
    """Record what the person typed at `--answer`, before the run reads anything.

    Applied FIRST so an answer takes effect on the very run that supplies it. A
    person who has just been asked a question and answers it should not have to
    run the command a third time to see what their answer did.

    A `question_id` this database has not asked about is REFUSED rather than
    ignored: the person believes they have told the product something, and a
    silently dropped answer is the worst of both -- no effect, and no way to tell.
    """
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


def _wrapped(text: str, *, indent: str, first: str | None = None) -> str:
    """`first` differs from `indent` only for a bullet, whose marker belongs on
    the first line and whose continuation lines must line up past it."""
    return textwrap.fill(text, width=78,
                         initial_indent=indent if first is None else first,
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


def _review_note(item, areas: Sequence[str]) -> str:
    """Why a set is being held, and the one thing a person can type about it.

    A hold with no command beside it is the product saying it noticed and will do
    nothing. With no residual area enabled the sentence says how to make one
    rather than naming a flag that would refuse.
    """
    held = f'Held for review as "{item.label}": {item.reason_not_placed}'
    if areas:
        return (f'{held} To file them all at once, name a home for them: '
                f'--send-set "{item.label}={areas[0]}"'
                + (f' (this plan also has {", ".join(areas[1:])})'
                   if areas[1:] else ""))
    return (f"{held} This plan has nowhere to put them yet: enable an area with "
            '`--residual "Review Later"` and they can all be sent there in one '
            "command.")


def report(result: ProductionRun, names: dict[str, str], *, out=None,
           questions: Sequence = (), set_aside: Sequence = ()) -> None:
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
        review = tuple(_review_note(item, areas)
                       for item in sets
                       if getattr(decision, "residual", None) is None)
        key = (decision.outcome, where, reason, review,
               decision.review_policy if decision.outcome == pv.PLACE else None,
               settled, same_folder)
        members.setdefault(key, []).extend(_files_of(decision))
        shielded[key] = shielded.get(key, False) or _protected(decision, sets)

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

    print(f"\nFiles: {len(decisions)} decided, {placed} ready to file", file=out)
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
    parser.add_argument(
        "--answer", action="append", default=[], metavar="QUESTION=OPTION",
        help="answer one of the questions the last run printed, e.g. "
             "--answer reading.organization:CV20261234=law_practice. Use "
             "`=skip` to put it aside. Answers are remembered between runs and "
             "can be given more than once.")
    parser.add_argument(
        "--residual", action="append", default=[], metavar="NAME",
        help="enable one of §7.3's residual areas as a destination in this "
             "plan, e.g. --residual \"Reading Inbox\". These are the homes for "
             "material that belongs to no folder in particular. None is "
             "created unless you name it, and it can be given more than once. "
             "`--list-residuals` prints them.")
    parser.add_argument(
        "--send-set", action="append", default=[], metavar="SET=AREA",
        help="file a whole review set into one of the residual areas this plan "
             "has, e.g. --send-set \"Not yet placed=Review Later\". Name the "
             "set exactly as the report printed it. No model is consulted -- "
             "the answer names the destination -- and it applies to the run "
             "that prints it, because a plan version's review sets are its own.")
    parser.add_argument(
        "--list-residuals", action="store_true",
        help="print the residual areas `--residual` accepts, and stop.")
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
        # BEFORE the run, so an answer takes effect on the very invocation that
        # supplies it. A person who has just been asked something and answers it
        # should not have to run the command a third time to see what it did.
        if args.answer:
            _bootstrap(conn)
            apply_answers(conn, args.answer, user_id=args.user,
                          recorded_at=now())
        result = run(conn, directory, situation=args.situation, label=args.label,
                     user_id=args.user, now=now, out=out,
                     residuals=_validate_residuals(args.residual),
                     sends=_parse_sends(args.send_set))
    except (NotConfigured, ConfigurationRequired) as refusal:
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
    report(result, file_names(conn, directory), out=out,
           questions=open_questions(conn),
           set_aside=set_aside_questions(conn))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
