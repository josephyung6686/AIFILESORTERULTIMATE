"""P1 through P11 as ONE call, over a real corpus with a protected bundle in it.

`production.run_production_p1_p7` composed seven parts and stopped. P9, P10 and
P11 each grew a chain of their own -- `grouping.pipeline.group_subject`,
`tree_design.pipeline.design_tree`, `placement.pipeline.run_corpus` -- and
nothing joined them, so a person with a directory had nothing to run.

Every test here drives the REAL composition. Nothing between two parts is
hand-assembled: the P6 facts are written by a resolver the live P1--P7 path
called, the groups are P9's own records through P9's own writers, the tree is
what P10 derived from them through the SHIPPED template library, and the
placements are P11's over that tree. A `FrozenTree` literal or a hand-written
`AcceptedGroup` in this file would be the defect it exists to catch.

The corpus carries a `.app` bundle on purpose. The standing rule is that a
protected container is MARKED AND COUNTED, NEVER OPENED -- present but untouched,
with a reachable explanation, never silently omitted. Five parts honour it
separately; this is the only file that asks whether the composed whole still
does, and the last section is nothing but that question.

Four breaks at the joins were found by writing it and are pinned at the end,
under `--- what the joins actually do ---`. Three are somebody else's to fix and
say so by name.
"""
from __future__ import annotations

import dataclasses
import json
from itertools import count
from pathlib import Path

import pytest

from database_agent.budget import set_ceiling
from extractors.archive import ArchiveManifest
from extractors.dispatch import Readers
from extractors.docx import DocxDocument
from extractors.image import ImageRecord
from extractors.long_tail import LongTailFile
from extractors.pdf import PdfDocument, PdfPage
from extractors.reading import Region
from extractors.safety import SafetyPolicy
from extractors.structured_text import TextDocument
from facts.file_facts import DETERMINISTIC_EXTRACTOR, write_fact
from facts.resolver import FactResolver
from facts.states import DIRECT
from facts.usable import record_pass
from facts.values import ensure_value
from grouping.acceptance import record_acceptance
from grouping.config import GroupingLimits
from grouping.embeddings import EmbeddingsOff
from grouping.pipeline import GroupingKnowledge
from grouping.records import GroupAcceptance
from grouping.retrieval import RetrievalKnowledge
from grouping.schema import create_grouping_schema
from grouping.store import memberships_for_group, record_group, record_membership
from grouping.vocabulary import (
    ACCEPTED, COHERENT, ENGINE, P1_INCLUDED_SCAN_STATE, PENDING_REVIEW, USER,
    USER_EDITED,
)
from llm_harness.records import EvidenceItem
from placement import vocabulary as pv
from placement.config import CEILINGS, SupportPolicy, placement_limits
from placement.pipeline import PipelineInputs
from placement.records import MatchingFact
from placement.schema import create_placement_schema
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy
from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.exclusion import is_protected_container
from scan_agent.selection import record_selection
from tree_design.config import TreeLimits
from tree_design.pipeline import (
    SharedMaterialAnswer, TreeDesignAuthorities, TreeDesignDecisions,
)
from tree_design.upstream import handling_class_for
from tree_design.schema import create_tree_schema
from tree_design.vocabulary import (
    MANDATORY_REVIEW, REFINED, SHALLOW_BY_CHOICE, SURFACE_UNATTENDED,
)

from cli import AcceptedGroupEnumeration
from production import (
    LIBRARY_FILES,
    CorpusAuthorities,
    CorpusDecisions,
    InvalidCorpusAuthority,
    MissingCatalogueAuthority,
    P1P7Authorities,
    bootstrap_p1_p7,
    corpus_roster,
    load_shipped_catalogue,
    read_packaged_library_file,
    run_production_corpus,
    shipped_catalogue_manifest,
)

CLOCK = "2026-08-28T12:00:00+00:00"
COMPONENT = "production-corpus-test"
PLAN_0 = "plan_0"
ROOT_ANCHOR = "root_documents"
ORDINARY_CLASS = "personal_non_sensitive"
PROTECTED_CLASS = "highly_sensitive_credential_bearing"
SCHEMA = "academic"
#: The situation the shipped library recognises for this corpus. One row, which
#: is what makes the recipe composable -- the whole `academic` schema unioned
#: would collide on C4.
SIGNAL = "recognition:academic.coursework"
BUNDLE_MARKER = "BUNDLE-INTERIOR-MUST-NOT-BE-READ"

#: The three dimensions this corpus settles, in the order the filename carries
#: them. `term` is deliberately absent: the shipped `ap.academic.coursework` row
#: resolves four dimensions and this corpus answers three, which is the ordinary
#: state of a real folder and the reason `_deep` exists below.
FIELDS = ("school", "subject", "work_type")
CORPUS = ("Columbia PHYS1401 Syllabus.pdf",
          "Columbia PHYS1401 Homework.pdf",
          "NYU BUSIB4300 Syllabus.pdf")
DEEP_FIELDS = ("school", "term", "subject", "work_type")
DEEP_CORPUS = ("Columbia Fall2026 PHYS1401 Syllabus.pdf",
               "Columbia Fall2026 PHYS1401 Homework.pdf",
               "NYU Spring2026 BUSIB4300 Syllabus.pdf")


# ==================================================================================
# G6 -- the shipped library has a caller in `src/`
# ==================================================================================


def test_the_shipped_library_assembles_into_one_release_the_loader_accepts():
    """`load_catalogue` had no caller in `src/` at all.

    Seven files ship under `src/tree_design/library/` and the loader parses ONE
    manifest. Assembling them is the composition's job precisely because
    `catalogue.py` takes an injected reader rather than a path -- "an injected
    reader rather than a path keeps this module out of the filesystem entirely".
    """
    catalogue = load_shipped_catalogue(read_packaged_library_file)

    assert len(catalogue.fragments) == 22
    assert len(catalogue.definitions) == 63
    assert len(catalogue.applicabilities) == 208
    assert catalogue.release_id


def test_the_release_id_is_derived_from_the_bytes_and_not_chosen():
    """Two different libraries must be distinguishable in a frozen tree.

    `load_catalogue` refuses a manifest with no `release_id` for that reason. The
    composition may not invent one, so it digests exactly what it read: a library
    file that changes moves the id, and one that did not cannot.
    """
    baseline = load_shipped_catalogue(read_packaged_library_file).release_id

    def altered(name: str) -> str:
        text = read_packaged_library_file(name)
        return text + " " if name == LIBRARY_FILES[0] else text

    assert load_shipped_catalogue(altered).release_id != baseline
    assert load_shipped_catalogue(read_packaged_library_file).release_id == baseline


def test_a_library_file_that_repeats_a_record_is_refused_rather_than_merged():
    """Seven files, one namespace. A silently-won duplicate would make which
    definition a tree froze depend on the order the files happen to be read."""
    from tree_design.config import ConfigurationRequired

    def doubled(name: str) -> str:
        raw = json.loads(read_packaged_library_file(name))
        if "definitions" in raw:
            raw["definitions"] = list(raw["definitions"]) * 2
        return json.dumps(raw)

    with pytest.raises(ConfigurationRequired):
        shipped_catalogue_manifest(doubled)


def test_a_file_that_is_not_part_of_the_release_is_refused():
    """The negative twin of the reader. P10's rule is that it does not locate,
    scan for, or default to a catalogue; the reader that feeds it may not either."""
    from tree_design.config import ConfigurationRequired

    with pytest.raises(ConfigurationRequired):
        read_packaged_library_file("../../../etc/passwd")


# ==================================================================================
# One real corpus, through one real call
# ==================================================================================


def _readers() -> Readers:
    def read_pdf(path):
        text = Path(path).read_text(errors="ignore")
        return PdfDocument(metadata={}, pages=(PdfPage(
            number=1, text=text,
            regions=(Region(zone="body", start=0, end=len(text)),)),))

    return Readers(
        read_pdf=read_pdf,
        read_docx=lambda path: DocxDocument(core_properties={}),
        read_text_document=lambda path: TextDocument(text="text"),
        read_long_tail=lambda path, transcribe=False: LongTailFile(),
        read_manifest=lambda path: ArchiveManifest(archive_type="zip"),
        read_image=lambda path: ImageRecord(image_format="PNG", dimensions="1x1",
                                            width=1, height=1),
        find_structured_strings=lambda text: (),
        recognize_markers=lambda names: (),
        dimension_signal=lambda width, height: None,
        filename_pattern=lambda name: None, ocr_engine=None)


def _stage(fields):
    """P6's `direct` stage for this corpus: the filename's own tokens, in order.

    The domain producer is the caller's everywhere in this project, and it is
    here too. What matters for the seams below is only that the facts are REAL
    -- written through `write_fact`, citing a real P4 observation, and read back
    by P10 and P11 through their own readers rather than from this file.
    """

    def stage(conn, file_id, content_hash):
        row = conn.execute("SELECT filename FROM files WHERE file_id = ?",
                           (file_id,)).fetchone()
        tokens = Path(row["filename"]).stem.split(" ")
        ref = conn.execute(
            "SELECT observation_key FROM evidence WHERE file_id = ? "
            "ORDER BY rowid LIMIT 1", (file_id,)).fetchone()
        if ref is None or len(tokens) < len(fields):
            return ()
        written = []
        for key, token in zip(fields, tokens):
            value_id = ensure_value(
                conn, field_key=key, canonical_value=token,
                first_evidence_ref=ref[0], origin="automatic")
            written.append(write_fact(
                conn, file_id=file_id, content_hash=content_hash, field_key=key,
                value_id=value_id, reliability_state=DIRECT,
                origin=DETERMINISTIC_EXTRACTOR, evidence_refs=(ref[0],),
                cache_key=f"{key}-v1:{content_hash}", active=True))
        return tuple(written)

    return stage


def _resolver(fields, *, tiers, cache_key) -> FactResolver:
    return FactResolver(
        stages={"direct": _stage(fields), "rule": None, "llm": None},
        pending_fields=lambda conn, f, h: (),
        budget_exhausted=lambda ceiling: False,
        model_route_permitted=lambda f: False,
        record_pass=lambda conn, f, h: record_pass(
            conn, file_id=f, content_hash=h, analysis_tiers=tiers),
        cache_key_for=lambda f, h: f"{cache_key}:{h}",
        screen_metadata=lambda conn, f, h: ())


def _classify(conn, file_id, content_hash):
    ref = conn.execute(
        "SELECT observation_key FROM evidence WHERE file_id = ? "
        "ORDER BY rowid LIMIT 1", (file_id,)).fetchone()
    if ref is None:
        return None
    return ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class=ORDINARY_CLASS, protected=False, basis="detector",
        evidence_refs=(ref[0],), reliability_state="direct", observed_at=CLOCK)


def _classify_passport_protected(conn, file_id, content_hash):
    """Ordinary, except the passport, which P7 marks protected.

    Written as a classifier rather than by widening `_classify`, because what is
    under test is P10's behaviour given a protected member -- not the detector's
    route to deciding one is.
    """
    row = conn.execute("SELECT current_path FROM files WHERE file_id = ?",
                       (file_id,)).fetchone()
    protected = row is not None and "Passport" in row[0]
    ref = conn.execute(
        "SELECT observation_key FROM evidence WHERE file_id = ? "
        "ORDER BY rowid LIMIT 1", (file_id,)).fetchone()
    if ref is None:
        return None
    return ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class=PROTECTED_CLASS if protected else ORDINARY_CLASS,
        protected=protected, basis="safety_domain" if protected else "detector",
        evidence_refs=(ref[0],), reliability_state="direct", observed_at=CLOCK)


def _p1_p7(fields, *, classify=_classify) -> P1P7Authorities:
    return P1P7Authorities(
        native_resolver=_resolver(fields,
                                  tiers=frozenset(("filesystem", "native")),
                                  cache_key="native-v1"),
        ocr_resolver=_resolver(fields,
                               tiers=frozenset(("filesystem", "native", "ocr")),
                               cache_key="ocr-v1"),
        usable_threshold=lambda facts, unresolved: True,
        classify=classify, source=FilesystemCorpusSource(),
        mime_type_for=lambda path: (
            "application/pdf" if Path(path).suffix == ".pdf" else None),
        # The live composition's own value, imported from the constant P9's
        # retrieval reads. A literal here diverged from `cli.py` once already and
        # cost every live run its whole neighbourhood.
        scan_state=P1_INCLUDED_SCAN_STATE, scan_budget_exhausted=lambda: False,
        detect_format=lambda path: (
            "pdf" if Path(path).suffix == ".pdf" else None),
        # THE real predicate, not a stand-in. P3 writes an exclusion verdict for
        # the bundle and never walks inside it.
        policy=SafetyPolicy(is_protected_container=is_protected_container,
                            is_dataless=lambda path: False),
        readers=_readers(), now=lambda: CLOCK, context_window=64,
        transcription_authorized=lambda: False, corpus_form="snapshot",
        policy_settings={}, file_entry_body=lambda row: {"payload_ref": "blob"},
        p7_component_version=COMPONENT)


def _seed(conn, tmp_path: Path, names) -> Path:
    bootstrap_p1_p7(conn)
    create_grouping_schema(conn)
    create_tree_schema(conn)
    create_placement_schema(conn)
    for key in CEILINGS.values():
        set_ceiling(conn, key, 8)
    root = tmp_path / "corpus"
    root.mkdir(parents=True, exist_ok=True)
    for name in names:
        (root / name).write_text(f"%PDF-1.4 {Path(name).stem}")
    (root / "Numbers.app" / "Contents").mkdir(parents=True, exist_ok=True)
    (root / "Numbers.app" / "Contents" / "sheet.numbers").write_text(BUNDLE_MARKER)
    return root


def _review(conn, results, *, category=SCHEMA, label="Coursework"):
    """The review screen: the user MERGES P9's proposals, names them, says what
    they are. Written through P9's own writers as a supersession, so what P9
    proposed and what the user answered are both still on disk."""
    grouped = [r for r in results if r.group is not None]
    if not grouped:
        return ()
    first = grouped[0].group
    merged = f"{PLAN_0}:{label}"
    record_group(conn, dataclasses.replace(
        first, group_id=merged,
        proposed_basis=f"the user confirmed these files are {label!r}",
        anchor_facts=tuple(f for r in grouped for f in r.group.anchor_facts),
        anchor_count=sum(r.group.anchor_count for r in grouped),
        coherence_verdict=COHERENT if category else None,
        coherence_citations=tuple(
            f.observation_key for r in grouped for f in r.group.anchor_facts),
        group_category=category, display_label=label if category else None,
        label_source=USER_EDITED if category else None,
        created_by=USER, supersedes=first.group_id,
        supersede_reason="the user named and categorised this group at review"))
    for result in grouped:
        for membership in memberships_for_group(conn, result.group.group_id):
            record_membership(conn, dataclasses.replace(
                membership, membership_id=f"{membership.membership_id}:{merged}",
                group_id=merged, supersedes=membership.membership_id,
                supersede_reason="carried onto the group the user confirmed"))
    record_acceptance(conn, GroupAcceptance(
        acceptance_id=f"acc:{merged}", plan_version_id=PLAN_0, group_id=merged,
        membership_id=None, acceptance=ACCEPTED, review_state=PENDING_REVIEW,
        user_edited_label=label, aliases=(), review_decision_ref=None,
        decided_by=USER, created_at=CLOCK))
    return (merged,)


def _choose_option(candidate, options) -> str:
    for option in options:
        report = option.validation
        if option.total_child_branches and (report is None or report.accepted):
            return option.option_id
    return options[-1].option_id


def _refinement(node):
    if node.parent_node_id is None:
        return (REFINED, "Populated from facts that were already settled.")
    return (SHALLOW_BY_CHOICE, "Few enough files that a split would not help.")


def run_corpus_through(conn, tmp_path, *, fields=FIELDS, names=CORPUS,
                       catalogue=None, decision_over=None, authority_over=None,
                       classify=_classify, wrap_design_authorities=None):
    """The whole product, in one call, over one real directory."""
    root = _seed(conn, tmp_path, names)
    release = catalogue if catalogue is not None else load_shipped_catalogue(
        read_packaged_library_file)
    selection_id = record_selection(
        conn, sources=[root], candidate_roots=[], cross_folder_moves=False,
        selected_by="jy")
    scan_run_id = [""]
    accepted_ids: list[str] = []

    def design_authorities(cat, accepted):
        ids = count()
        return TreeDesignAuthorities(
            catalogue=cat, group_reader=AcceptedGroupEnumeration(conn),
            limits=TreeLimits(
                max_folder_proposals=5, max_depth=5, max_dossier_tokens=4000,
                excessive_depth_warning=4, tiny_folder_max_files=1,
                tiny_folder_count_warning=2,
                materially_improves_retrieval=lambda option: True),
            root_anchor=ROOT_ANCHOR, selection_id=selection_id,
            scan_run_id=scan_run_id[0], active_domains=(SCHEMA,),
            sensitive_group_ids=frozenset(), privacy_rank=lambda floor: 0,
            satisfies_purpose_profile=lambda ref, groups: True,
            detection_signals_for=lambda group: frozenset({SIGNAL}),
            rank_candidates=lambda candidates: list(candidates),
            # P7's own class, exactly as `cli.py` reads it. This harness used to
            # hardcode ORDINARY_CLASS, which told P10 nothing in the corpus was
            # sensitive and made every protected-member path unreachable from
            # here -- the same defect the composition root had.
            handling_class_for_member=lambda member: handling_class_for(
                ClassificationStore(conn), file_id=member.file_id,
                content_hash=member.content_hash),
            collapse_handling_classes=lambda classes: (
                PROTECTED_CLASS if PROTECTED_CLASS in classes
                else ORDINARY_CLASS),
            handling_class_for_area=lambda area: PROTECTED_CLASS,
            protected_handling_classes=frozenset({PROTECTED_CLASS}),
            collector_field_keys=frozenset({"authored_by", "organization"}),
            value_discloses_protected_material=lambda ref, value: False,
            template_context_for=lambda ref, order: None,
            mint_node_id=lambda: f"node_{next(ids)}",
            mint_version_id=lambda: f"version_{next(ids)}")

    def design_decisions(accepted):
        return TreeDesignDecisions(
            from_plan_version=PLAN_0, branch_group_ids=tuple(accepted),
            choose_option=_choose_option, refinement_for=_refinement,
            residual_library={}, residual_choices=(), residual_configuration={},
            residual_handling_class=lambda name: ORDINARY_CLASS,
            residual_refinement=None,
            shared_material=SharedMaterialAnswer(
                parent_origin_id=None, policy=MANDATORY_REVIEW,
                reason="Nobody was at the screen, so it stays the user's call.",
                display_label="Shared Material", policy_scope=None),
            scoped_general=(), created_at=CLOCK, user_id="jy",
            component_version=COMPONENT,
            # This harness stands in for `src/cli.py`, which shows nobody
            # anything -- the `reason` two lines above already says so.
            surface=SURFACE_UNATTENDED)

    def accept(db, results):
        ids = _review(db, results)
        accepted_ids.extend(ids)
        return ids

    def approve_plan(db, accepted, plan_version):
        for group_id in accepted:
            record_acceptance(db, GroupAcceptance(
                acceptance_id=f"acc:{plan_version}:{group_id}",
                plan_version_id=plan_version, group_id=group_id,
                membership_id=None, acceptance=ACCEPTED,
                review_state=PENDING_REVIEW, user_edited_label="Coursework",
                aliases=(), review_decision_ref=None, decided_by=USER,
                created_at=CLOCK))

    def set_privacy_policy(db, plan_version):
        set_policy(db, Policy(
            policy_version=UNSET_POLICY_VERSION, operation_mode="offline",
            consent_grants=(), redaction_settings={},
            automatic_move_permissions={}, plan_version=plan_version,
            set_at=CLOCK), component_version=COMPONENT, user_id="jy",
            reason="production corpus test")

    def evidence_for(file_id):
        facts, items = [], []
        for row in conn.execute(
                "SELECT ff.fact_id, ff.field_key, ff.evidence_refs, "
                'v.canonical_value FROM file_facts ff JOIN "values" v '
                "ON ff.value_id = v.value_id WHERE ff.file_id = ? "
                "AND ff.active = 1 AND ff.superseded_by IS NULL", (file_id,)):
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
            entity_frequency={fact.value: 1 for fact in facts},
            generic_entity_frequency=200)

    def partition(unplaced):
        if not unplaced:
            return ()
        return ({"label": "Not yet placed", "member_file_ids": tuple(unplaced),
                 "representative_examples": tuple(unplaced)[:3],
                 "file_type_distribution": (), "age_range": (),
                 "evidence_availability": "partial",
                 "sensitivity_status": "none", "protected": False,
                 "weak_graph_neighbours": (),
                 "reason_not_placed": "§6 reached no destination for these"},)

    def placement_inputs(tree):
        return PipelineInputs(
            plan_version=tree.tree.plan_version_id, tree=tree.tree,
            policy=SupportPolicy(policy_id="test-v1", support_scale_max=1.0,
                                 minimum_support_threshold=0.5,
                                 margin_threshold=0.2),
            limits=placement_limits(conn), partition=partition,
            ask_or_abstain=lambda node_ids: pv.ABSTAIN, max_return_cycles=1,
            gate=None, model_client=None, prompt=None, call_dependencies=None,
            model_call_request=None, chosen_node_of=None,
            residual_action_of=None, sensitivity_policy=None, p2=None)

    def downstream(p1_p7):
        scan_run_id[0] = p1_p7.scan_run_id
        values = dict(
            catalogue=release,
            design_authorities=(wrap_design_authorities(design_authorities)
                                if wrap_design_authorities else design_authorities),
            grouping_limits=GroupingLimits(
                max_retrieved_neighbors=50, max_graph_nodes=10,
                max_candidate_members=10, max_dossier_tokens=4000,
                generic_hub_frequency=9, minimum_independent_anchors=1,
                max_excerpt_characters=240),
            grouping_knowledge=GroupingKnowledge(
                retrieval=RetrievalKnowledge(
                    document_compatible=None, channel_weights={},
                    similarity=None, similarity_threshold=None,
                    embedding_identity=None, domain=None),
                active_schema_for=lambda db, f, h: fields,
                signal_evaluator_for=lambda domain: True,
                classification_store=ClassificationStore(conn).current,
                conflicts_for=lambda file_ids: (),
                duplicate_or_version=None),
            user_seed_for=lambda f, h: None, embeddings=EmbeddingsOff(),
            p8_run_call=None, p8_authorities=None,
            placement_inputs=placement_inputs, evidence_for=evidence_for,
            evaluation=None, component_version=COMPONENT, now=lambda: CLOCK)
        values.update(authority_over or {})
        return CorpusAuthorities(**values)

    values = dict(plan_version_id=PLAN_0, accept_groups=accept,
                  design=design_decisions, approve_plan=approve_plan,
                  set_privacy_policy=set_privacy_policy)
    values.update(decision_over or {})
    return run_production_corpus(
        conn, selection_id, authorities=_p1_p7(fields, classify=classify),
        downstream=downstream,
        decisions=CorpusDecisions(**values))


@pytest.fixture()
def result(conn, tmp_path):
    return run_corpus_through(conn, tmp_path)


# --- the spine --------------------------------------------------------------------


def test_a_directory_becomes_a_placement_decision_in_one_call(result, conn):
    """G7, walked. Three real files on disk, one call, and a decision for each.

    Nothing between the parts is a fixture. The destination's label below is read
    back out of P6's own `values` table rather than compared to a string this
    file chose, which is §5.4's own sentence made checkable: "The system does not
    invent PHYS1401 ... those names emerge from validated facts".
    """
    from facts.values import values_in_field

    placed = [d for d in result.placement.decisions if d.outcome == pv.PLACE]
    assert len(result.placement.decisions) == 3
    assert placed, "no file reached a destination P10 built"

    labels = {node.node_id: node.display_label for node in result.tree.tree.nodes}
    # Every field this corpus settles, not `school` alone. The assertion is
    # §5.4's sentence -- "the system does not invent PHYS1401 ... those names
    # emerge from validated facts" -- and that is a claim about where the label
    # CAME FROM, not about which level of the tree it sits at. It read only
    # `school` while the tree was one folder deep and the deepest node a file
    # could reach was therefore always a school; now that a level nobody answered
    # is skipped rather than collapsing its children, files land on `Homework`
    # and `Syllabus`, which P6 settled in `work_type` just as honestly.
    settled = {row["canonical_value"] for field in FIELDS
               for row in values_in_field(conn, field)}
    for decision in placed:
        assert labels[decision.destination.node_id] in settled
        assert decision.destination.node_role == pv.ORDINARY


def test_every_part_ran_and_handed_its_own_output_to_the_next(result):
    """The five chains, each proved by a field only that chain could fill."""
    assert result.p1_p7.scan_run_id and result.p1_p7.bundle_id          # P1--P7
    assert [g for g in result.grouping if g.group is not None]          # P9
    assert result.tree.plan_version_ids                                 # P10
    assert result.destinations                                          # P11 index
    assert result.placement.decisions                                   # P11


def test_the_version_chain_p10_mints_is_what_p11_was_given(result):
    """§8.8 opens a draft per edit, so the version P11 indexes is NOT the version
    P9 wrote against. A composition that handed P11 `plan_0` would index a tree
    that does not exist."""
    frozen = result.tree.tree.plan_version_id
    assert frozen != PLAN_0
    assert frozen in result.tree.plan_version_ids
    assert len(result.tree.plan_version_ids) > 1


def test_the_roster_is_p1s_and_not_the_files_that_happened_to_be_re_extracted(
        conn, tmp_path):
    """`P1P7Run.fact_results` holds only the files THIS run extracted. A REUSE
    file -- unchanged since the last scan, with good stored facts -- is skipped
    by the extraction loop and has no entry, so grouping and placing off that
    list would leave every unchanged file out of the plan with nothing to say so.
    `corpus_roster` reads P3's verdicts instead."""
    result = run_corpus_through(conn, tmp_path)
    roster = corpus_roster(conn, result.p1_p7.scan_run_id)

    assert len(roster) == len(CORPUS)
    assert {file_id for file_id, _hash in roster} == {
        row["file_id"] for row in conn.execute("SELECT file_id FROM files")}
    assert len(result.grouping) == len(roster)
    assert len(result.placement.decisions) == len(roster)


def test_the_tree_was_built_from_the_shipped_template_library(result):
    """G6 and G7 meeting. The recipe that routed this branch is a row in
    `src/tree_design/library/`, reached through `load_shipped_catalogue`."""
    refs = {ref.applicability_id
            for branch in result.tree.branches
            for candidate in branch.routing.candidates
            for ref in candidate.applicability_refs}
    assert "ap.academic.coursework" in refs


# --- the standing rule, over the composed whole -----------------------------------


def test_the_protected_bundle_is_marked_and_counted(result):
    """MARKED AND COUNTED. It is in the tree, it is in the run's own
    `protected_areas`, and it carries P3's verdict label as its explanation."""
    areas = result.protected_areas
    assert [area.display_label for area in areas] == ["Numbers.app"]
    assert areas[0].label == "untouched_protected"
    assert areas[0].rule_subject == "protected_container"

    marked = [node for node in result.tree.tree.nodes
              if node.display_label == "Numbers.app"]
    assert len(marked) == 1, "the container is in the tree exactly once"


def test_the_protected_bundle_is_never_a_destination(result):
    """NEVER OPENED, at the one place it would stop being true. A marked node
    that P11 could index is a folder files can be moved INTO, which is a way of
    opening it."""
    marked = next(node for node in result.tree.tree.nodes
                  if node.display_label == "Numbers.app")

    assert marked.accepts_placement is False
    assert marked.node_id not in {entry.node_id for entry in result.destinations}
    assert marked.node_id not in {
        decision.destination.node_id
        for decision in result.placement.decisions if decision.destination}


def test_nothing_inside_the_protected_bundle_reached_any_part(result, conn):
    """The one that catches a join. Five parts refuse the interior separately;
    this asks whether the composed whole ever let a byte of it through -- into
    P1's index, P4's observations, P6's facts, P7's classifications, P9's
    memberships or P11's decisions."""
    interior = "sheet.numbers"
    assert not conn.execute(
        "SELECT 1 FROM files WHERE filename = ?", (interior,)).fetchall()
    assert not conn.execute(
        "SELECT 1 FROM files WHERE current_path LIKE '%Numbers.app%'").fetchall()
    assert not conn.execute(
        "SELECT 1 FROM evidence WHERE raw_value LIKE ?",
        (f"%{BUNDLE_MARKER}%",)).fetchall()

    placed_files = {decision.subject.file_id
                    for decision in result.placement.decisions}
    indexed = {row["file_id"] for row in conn.execute("SELECT file_id FROM files")}
    assert placed_files <= indexed
    store = ClassificationStore(conn)
    for row in conn.execute("SELECT file_id, content_hash, current_path FROM files"):
        assert "Numbers.app" not in row["current_path"]
        record = store.current(row["file_id"], row["content_hash"])
        assert record is None or "Numbers.app" not in row["current_path"]


def test_the_marked_container_is_never_silently_omitted(result):
    """"Present-but-untouched, with a reachable explanation, never silently
    omitted." Reachability is the half a count cannot prove: the run object hands
    the area up without the caller walking into P10's internals for it."""
    assert result.protected_areas is result.tree.protected_areas
    area = result.protected_areas[0]
    assert area.path.endswith("Numbers.app")
    assert area.observed_at, "an unmarked observation time is an unrecorded mark"


# --- every guard's negative twin ---------------------------------------------------


def test_a_run_with_no_catalogue_is_refused_before_p9_or_p10_writes_anything(
        conn, tmp_path):
    """The twin of `MissingClassificationAuthority`, one layer down.

    `TreeDesignAuthorities` types `catalogue` as `object` and checks it nowhere,
    so `catalogue=None` builds a valid-looking record and fails deep inside
    `route_branch` with a draft plan version already written. Checked when
    `CorpusAuthorities` is constructed instead -- which is as early as it CAN be,
    because the downstream authorities are a factory over the finished P1--P7 run
    and cannot exist before the scan does.

    So the scan HAS happened when this raises, and the assertions below say what
    the check is actually worth: not one group and not one plan version. Nothing
    downstream of the missing authority was written and there is nothing to undo.
    """
    with pytest.raises(MissingCatalogueAuthority):
        run_corpus_through(conn, tmp_path, authority_over={"catalogue": None})

    assert conn.execute("SELECT count(*) FROM groups").fetchone()[0] == 0
    assert conn.execute("SELECT count(*) FROM plan_versions").fetchone()[0] == 0
    assert conn.execute("SELECT count(*) FROM tree_nodes").fetchone()[0] == 0


def test_a_user_decision_that_is_absent_is_refused_rather_than_defaulted(
        conn, tmp_path):
    """Each of the four is the user's, and none of them has an answer this
    module may supply. A composition that accepted P9's own groups, approved its
    own plan, designed its own tree or chose its own operation mode would be the
    engine deciding what §5.7 and §8.4 assign to a person."""
    for name in ("accept_groups", "design", "approve_plan", "set_privacy_policy"):
        with pytest.raises(InvalidCorpusAuthority):
            run_corpus_through(conn, tmp_path, decision_over={name: None})


def test_a_run_with_no_review_to_design_from_is_refused(conn, tmp_path):
    with pytest.raises(InvalidCorpusAuthority):
        run_corpus_through(conn, tmp_path, decision_over={"plan_version_id": ""})


def test_a_design_that_reads_a_different_review_than_p9_wrote_is_refused(
        conn, tmp_path):
    """P9 writes its groups against one plan version and P10 designs FROM one.
    When they differ the tree is designed from groups this run never made, and
    the symptom -- `NothingToDesign` -- names the wrong cause."""
    with pytest.raises(InvalidCorpusAuthority) as excinfo:
        run_corpus_through(conn, tmp_path,
                           decision_over={"plan_version_id": "some_other_review"})
    assert "some_other_review" in str(excinfo.value)


def test_p9s_model_route_is_both_halves_or_neither(conn, tmp_path):
    """A `run_call` with no authorities cannot reach the gate, and authorities
    with no `run_call` name a route nothing takes. Either alone is a deployment
    that thinks it has a model and has not."""
    with pytest.raises(InvalidCorpusAuthority):
        run_corpus_through(conn, tmp_path,
                           authority_over={"p8_run_call": lambda **kw: None})


def test_a_design_factory_that_swaps_the_release_is_refused(conn, tmp_path):
    """The catalogue is checked once, up front. A factory free to return a
    different one would make that check decorative and freeze a tree against a
    library nobody validated."""
    other = load_shipped_catalogue(read_packaged_library_file)

    def swap(factory):
        return lambda release, accepted: dataclasses.replace(
            factory(release, accepted), catalogue=other)

    with pytest.raises(MissingCatalogueAuthority):
        run_corpus_through(conn, tmp_path, wrap_design_authorities=swap)


# --- what the joins actually do ---------------------------------------------------
#
# Four things this file found by driving the real chains, each pinned so a fix
# registers as a change rather than as the same green. Three are somebody else's.


def test_p9_writes_a_category_and_a_label_a_live_run_can_route(conn, tmp_path):
    """THE break at the P9 -> P10 join, fixed, and pinned from the other side.

    This test was written inverted, asserting that `group_category`,
    `display_label` and `coherence_verdict` were `None` on every path -- because
    `src/grouping/pipeline.py:230` was the only originating writer and wrote
    `None` to all of them unconditionally, and `apply_p8_verdict` touched none.

    What that cost was total, which is why it was pinned rather than described:

    * `tree_design.upstream._label` raises `UpstreamUnavailable` for a group with
      no label, so an accepted group was unreadable unless the user typed a name;
    * `AcceptedGroup.domain` IS P9's `group_category`, so it was always `None`,
      so `BranchContext.domains` was always empty, so `route_branch` answered C3
      -- "no applicability row makes any recipe eligible" -- for EVERY branch, on
      every corpus, with any catalogue. All 208 shipped rows were unreachable
      from a live P9 run.

    P9 now writes all three. The assertions are the same three facts read the
    other way round, plus the one that makes it worth asserting: the category is
    a schema the product actually recognises. A category P10 cannot route is the
    same outcome as `None` with an extra step, so `is not None` alone would let
    the defect back in wearing a string.
    """
    from grouping.pipeline import group_subject

    _seed(conn, tmp_path, CORPUS)
    selection_id = record_selection(
        conn, sources=[tmp_path / "corpus"], candidate_roots=[],
        cross_folder_moves=False, selected_by="jy")
    from production import run_production_p1_p7

    run = run_production_p1_p7(conn, selection_id, authorities=_p1_p7(FIELDS))
    made = [group_subject(
        conn, file_id=file_id, content_hash=content_hash,
        plan_version_id=PLAN_0,
        limits=GroupingLimits(
            max_retrieved_neighbors=50, max_graph_nodes=10,
            max_candidate_members=10, max_dossier_tokens=4000,
            generic_hub_frequency=9, minimum_independent_anchors=1,
            max_excerpt_characters=240),
        knowledge=GroupingKnowledge(
            retrieval=RetrievalKnowledge(
                document_compatible=None, channel_weights={}, similarity=None,
                similarity_threshold=None, embedding_identity=None, domain=None),
            active_schema_for=lambda db, f, h: FIELDS,
            signal_evaluator_for=lambda domain: True,
            classification_store=ClassificationStore(conn).current,
            conflicts_for=lambda file_ids: (), duplicate_or_version=None),
        user_seed_for=lambda f, h: None, p8_run_call=None, p8_authorities=None,
        embeddings=EmbeddingsOff(), created_at=CLOCK)
        for file_id, content_hash in corpus_roster(conn, run.scan_run_id)]

    groups = [result.group for result in made if result.group is not None]
    assert groups, "P9 made no group at all, which is a different failure"
    assert all(group.group_category is not None for group in groups), [
        group.group_id for group in groups if group.group_category is None]
    assert all(group.display_label is not None for group in groups), [
        group.group_id for group in groups if group.display_label is None]
    assert all(group.coherence_verdict == COHERENT for group in groups)

    # The assertion that proves P9 MADE the label rather than inheriting one. A
    # user-typed name supersedes P9's proposal and always could; without this,
    # every assertion above would pass on a corpus where the engine still wrote
    # nothing and `--label` supplied the only name there was.
    assert all(group.label_source == ENGINE for group in groups), [
        group.label_source for group in groups]

    # The half that makes the other three worth asserting: a category outside the
    # closed vocabulary routes exactly as badly as `None` did, so a bare
    # `is not None` would readmit the defect wearing a string.
    from facts.domains import SCHEMA_IDS
    assert all(group.group_category in SCHEMA_IDS for group in groups), [
        group.group_category for group in groups
        if group.group_category not in SCHEMA_IDS]

    # And what that buys, at the reader P10 actually uses.
    from tree_design.upstream import UpstreamUnavailable, accepted_groups

    record_acceptance(conn, GroupAcceptance(
        acceptance_id="acc_bare", plan_version_id=PLAN_0,
        group_id=groups[0].group_id, membership_id=None, acceptance=ACCEPTED,
        review_state=PENDING_REVIEW, user_edited_label=None, aliases=(),
        review_decision_ref=None, decided_by=USER, created_at=CLOCK))
    # `user_edited_label=None` on purpose: the user typed nothing, so this reads
    # P9's own label or it reads nothing. It used to raise here.
    upstream = accepted_groups(AcceptedGroupEnumeration(conn),
                               plan_version_id=PLAN_0)
    assert upstream, "an accepted group with a P9 label is still unreadable"
    assert all(group.domain in SCHEMA_IDS for group in upstream), [
        group.domain for group in upstream]
    assert UpstreamUnavailable  # still the refusal for a group with no label


def test_an_acceptance_in_the_review_version_is_invisible_to_p11(conn, tmp_path):
    """The break at the P10 -> P11 join that `approve_plan` exists for.

    `placement.groups.accepted_group_as_of` asks P9 "as of P10's FROZEN plan
    version", and §8.8 mints a new version for every edit -- so the version P11
    asks about is never the version the review wrote into. Without a decision
    that carries the approval forward, §6.8's group pass refuses every group and
    every file is placed alone, with no shared context and no explanation the
    user could act on.
    """
    from placement.groups import GroupNotAcceptedInVersion, accepted_group_as_of

    result = run_corpus_through(conn, tmp_path)
    group_id = next(
        group_id for branch in result.tree.branches
        for group_id in branch.candidate.accepted_group_ids)

    # Accepted in the version P11 was given, because `approve_plan` said so.
    assert accepted_group_as_of(
        conn, group_id=group_id,
        plan_version=result.tree.tree.plan_version_id).state == ACCEPTED
    # And in every OTHER version of the same chain, invisible.
    for version in result.tree.plan_version_ids[:-1]:
        with pytest.raises(GroupNotAcceptedInVersion):
            accepted_group_as_of(conn, group_id=group_id, plan_version=version)


def test_one_unclassified_file_does_not_refuse_the_whole_corpus(conn, tmp_path):
    """The break at the P7 -> P11 join, fixed, and the shape of what replaced it.

    P7's detector leaving a file unclassified is DESIGNED -- it is what stops it
    guessing, and §8.6 says absence resolves to the gate outcome
    `unreadable_unclassified`, never down to `public_low`. P7 publishes
    `resolve_class(None)` to say exactly that.

    `placement.privacy.privacy_state_for` did not ask it. It raised
    `ClassificationRequired`, and `run_corpus` did not catch it -- so ONE file the
    detector said nothing about refused the WHOLE corpus run, and a person with
    ten thousand files and one ambiguous scan got a traceback instead of a plan.

    It now reads P7's answer. The composed run completes, every file comes back,
    and the unrecognised one comes back BLOCKED: `blocked_pending_user` and not
    the ordinary review queue, because a reviewer can confirm a decision that
    merely needs confirming and cannot confirm one whose subject nothing has
    classified. `tests/p11/test_p11_privacy.py` and `test_p11_pipeline.py` hold
    both halves at P11's own boundary.
    """
    from privacy.classification import UNREADABLE_UNCLASSIFIED

    def silent_about_one(conn_, file_id, content_hash):
        row = conn_.execute("SELECT filename FROM files WHERE file_id = ?",
                            (file_id,)).fetchone()
        if row["filename"].startswith("NYU"):
            return None
        return _classify(conn_, file_id, content_hash)

    result = run_corpus_through(conn, tmp_path, classify=silent_about_one)

    by_file = {}
    for decision in result.placement.decisions:
        row = conn.execute("SELECT filename FROM files WHERE file_id = ?",
                           (decision.subject.file_id,)).fetchone()
        by_file[row["filename"]] = decision
    # Every file in the corpus produced a decision, including the one nothing
    # could classify. A run that dropped it would be the silent omission the
    # standing rule forbids just as surely as a run that refused.
    assert set(by_file) == set(CORPUS)

    unclassified = by_file["NYU BUSIB4300 Syllabus.pdf"]
    assert unclassified.privacy.handling_class == UNREADABLE_UNCLASSIFIED
    assert unclassified.review_policy == "blocked_pending_user"
    # And it is not the protected bundle wearing a different name. `protected` is
    # P7's FLAG and nothing raised one here: `00` -- "sensitive personal material
    # is not the same thing as `Numbers.app`" -- and neither is either of them the
    # same thing as a file nothing could read.
    assert unclassified.privacy.protected is False

    # The files the detector DID answer about are untouched by any of this.
    for name in ("Columbia PHYS1401 Syllabus.pdf", "Columbia PHYS1401 Homework.pdf"):
        assert by_file[name].privacy.handling_class == ORDINARY_CLASS
        assert by_file[name].review_policy != "blocked_pending_user"


def test_a_dimension_with_no_settled_value_is_skipped_not_collapsed(
        conn, tmp_path):
    """A level nobody answered is SKIPPED. It does not take its children with it.

    This test used to pin the opposite, and called it "not a defect -- a property
    worth pinning". Running the product over four real persona corpora is what
    changed the verdict: `ap.academic.coursework` resolves school, term, subject,
    work_type IN THAT ORDER, and a person whose files state a course code and
    nothing else answers only the THIRD. Under the old rule the empty `school`
    collapsed everything beneath it, so a corpus that knew `PHYS1401` perfectly
    well was told it could be given no folder at all -- the product DISCARDING
    KNOWLEDGE IT HAS BECAUSE OF KNOWLEDGE IT LACKS.

    `00`:51 is why skipping is the reading that matches the design rather than a
    convenience: the same facts may legitimately be organised
    `Academics/Columbia/2026-Spring/BUSIB 4300` or `Academics/BUSIB 4300/Spring
    2026`. The ORDER of the levels is not rigid, so a gap in it is a gap, not a
    floor.

    The skip is not new machinery. `_project` already recurses past a
    `metadata_only` level with the same parent and the same eligible set; a level
    with no values now takes that same path instead of falling off the end of the
    function.
    """
    shallow = run_corpus_through(conn, tmp_path)
    shallow_labels = {node.display_label for node in shallow.tree.tree.nodes}
    assert "Columbia" in shallow_labels
    assert "PHYS1401" in shallow_labels, (
        "the empty `term` level swallowed `subject`, which the files DID settle")


def test_a_skipped_level_hands_its_children_to_the_level_above_it(
        conn, tmp_path):
    """Skipping must not silently reparent files to the root or drop the ordering.

    The discriminating half of the test above: it is not enough that `PHYS1401`
    exists somewhere in the tree. It has to hang off `Columbia` -- the level that
    WAS settled and sits above the empty one -- because that is what "the level
    was skipped" means, as opposed to "the tree was flattened".
    """
    shallow = run_corpus_through(conn, tmp_path)
    by_id = {node.node_id: node for node in shallow.tree.tree.nodes}
    subject = next(node for node in shallow.tree.tree.nodes
                   if node.display_label == "PHYS1401")

    parent = by_id.get(subject.parent_node_id)
    assert parent is not None, "the subject node was reparented off the branch"
    assert parent.display_label == "Columbia", (
        f"`PHYS1401` hangs off {parent.display_label!r}, not off the settled "
        "level above the skipped one")


def test_a_corpus_that_answers_only_a_late_dimension_still_gets_that_folder(
        conn, tmp_path):
    """The persona case, reduced: every level empty except the third.

    This is what all four personas actually looked like on 2026-08-29 -- files
    stating a course code and nothing else -- and it is the case that produced
    "Proposed folders: 1" for a litigator, a student, a household and a person
    who is all three alike.
    """
    only_subject = run_corpus_through(
        conn, tmp_path, fields=("subject",),
        names=("PHYS1401 Syllabus.pdf", "PHYS1401 Homework.pdf",
               "BUSIB4300 Syllabus.pdf"))
    labels = {node.display_label for node in only_subject.tree.tree.nodes}

    assert "PHYS1401" in labels and "BUSIB4300" in labels, (
        f"a corpus whose files state exactly one dimension got {labels}; the "
        "levels above it were empty and took the answered one down with them")


def test_the_same_corpus_with_every_dimension_answered_nests_all_four(
        conn, tmp_path):
    """The discriminating twin. Same recipe, same chain, one more settled fact."""
    deep = run_corpus_through(conn, tmp_path, fields=DEEP_FIELDS,
                              names=DEEP_CORPUS)
    labels = {node.display_label for node in deep.tree.tree.nodes}

    assert {"Columbia", "Fall2026", "PHYS1401", "Syllabus"} <= labels
    depth = {node.node_id: node.parent_node_id for node in deep.tree.tree.nodes}

    def height(node_id):
        parent = depth[node_id]
        return 0 if parent is None else 1 + height(parent)

    assert max(height(node_id) for node_id in depth) >= 4


# ==================================================================================
# The command a person actually types
# ==================================================================================


def test_the_command_runs_over_a_real_directory_and_leads_with_what_it_did_not_open(
        tmp_path, capsys):
    """`cli.main`, end to end, over files on disk. No fixture anywhere in it.

    The order of the report is the assertion. "Marked and counted, never opened"
    is only true if the count is somewhere the person reads, and a line at the
    bottom of a long report is not that -- so the protected containers come
    first, before the tree and before a single placement.
    """
    import cli

    corpus = tmp_path / "corpus"
    (corpus / "Numbers.app" / "Contents").mkdir(parents=True)
    (corpus / "Numbers.app" / "Contents" / "sheet.numbers").write_text(BUNDLE_MARKER)
    (corpus / "syllabus.txt").write_text("PHYS1401 Syllabus\nColumbia, Fall 2026.\n")
    (corpus / "homework.txt").write_text("PHYS1401 Homework 3\nColumbia.\n")

    code = cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Coursework", "--user", "jy",
                     "--database", str(tmp_path / "plan.sqlite")])
    out = capsys.readouterr().out

    assert code == 0, out
    assert "Protected containers: 1 marked, none opened" in out
    assert "Numbers.app" in out
    assert out.index("Protected containers") < out.index("Plan version")
    assert "[marked, not a destination]" in out
    # Every file gets a line, and a line that is not a placement gets a reason.
    assert "Files: 2 decided" in out
    assert BUNDLE_MARKER not in out, "the bundle's contents reached the report"


def test_the_command_will_not_keep_its_database_inside_the_folder_it_reads(
        tmp_path, capsys):
    """`open_database`'s own refusal, surfaced rather than raised. A plan file
    written inside the corpus is a file the next scan would index."""
    import cli

    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "note.txt").write_text("PHYS1401\n")

    code = cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Coursework",
                     "--database", str(corpus / "plan.sqlite")])
    assert code == 2
    assert "never created inside a scan root" in capsys.readouterr().out


def test_a_situation_the_shipped_library_does_not_carry_is_refused_by_name(
        tmp_path, capsys):
    """Checked against the catalogue rather than against a list in the CLI, so a
    library that gains or loses a situation moves the check with it -- and a typo
    is refused before a single file is read."""
    import cli

    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "note.txt").write_text("PHYS1401\n")

    code = cli.main([str(corpus), "--situation", "academic.courswork",
                     "--label", "Coursework",
                     "--database", str(tmp_path / "plan.sqlite")])
    out = capsys.readouterr().out
    assert code == 2
    assert "names no situation" in out


def test_the_command_can_list_every_situation_it_knows(capsys):
    import cli

    assert cli.main(["--list-situations", "x", "--situation", "a.b",
                     "--label", "L"]) == 0
    listed = capsys.readouterr().out.split()
    assert "academic.coursework" in listed
    assert len(listed) > 100


# ==================================================================================
# §8.5, over the bundle this run sealed
# ==================================================================================


def _version_tuple() -> dict:
    """§8.5's six axes plus the library, which `record_version_tuple` requires by
    name. `template_library_version` is the shipped release's own derived id, so
    a library that changed makes a replay comparable to nothing before it -- which
    is exactly what that axis is for."""
    return {
        "extractor_versions": COMPONENT,
        "prompt_fingerprint": "none",
        "model_identifier": "none",
        "graph_algorithm_version": COMPONENT,
        "placement_scorer_version": COMPONENT,
        "analysis_tiers_enabled": ("filesystem", "native"),
        "template_library_version": load_shipped_catalogue(
            read_packaged_library_file).release_id,
    }


def test_a_run_that_declares_no_evaluation_measures_nothing_and_says_so(result):
    """`None` is a declaration, not an omission. A field that could mean either
    would let a lost measurement read as a run nobody asked to measure."""
    assert result.evaluation is None


def test_the_replay_runs_over_this_runs_own_bundle(conn, tmp_path):
    """P2 joined. `evaluate_bundle` is driven with an EMPTY adapter set, which is
    a legal run its own docstring names -- "a bundle can be evaluated while nine
    of the ten measured stages are still absent" -- so what this binds is the
    seam and not the adapters: the bundle id P1--P7 sealed is the one §8.5
    replays, and the counts come back off that bundle."""
    from production import EvaluationAuthorities

    run = run_corpus_through(conn, tmp_path, authority_over={
        "evaluation": EvaluationAuthorities(
            version_tuple=_version_tuple(), budget_ceilings={},
            run_settings={}, adapters={}, run_kind="replay")})

    assert run.evaluation is not None
    assert run.evaluation.bundle_id == run.p1_p7.bundle_id
    assert run.evaluation.run_id
    assert run.evaluation.counts


def test_an_evaluation_authority_of_the_wrong_type_is_refused(conn, tmp_path):
    with pytest.raises(InvalidCorpusAuthority):
        run_corpus_through(conn, tmp_path,
                           authority_over={"evaluation": {"adapters": {}}})


# --- `65` §4.2's cause: the word P1 writes and the word P9 reads -------------------


def test_two_files_that_state_one_course_reach_each_others_neighbourhood(result):
    """The live seam under `65` §4.2, and no unit test could have found it.

    `CORPUS` has two files stating `subject = PHYS1401`. P9's first retrieval
    channel is the shared validated fact, so each must be in the other's
    neighbourhood, the group's graph must carry the edge, and `anchor_count` --
    the SPEC's "number of files that INDEPENDENTLY state the basis value" --
    must be two.

    It was ONE, and the neighbourhood was empty, because `_corpus` admits only
    files at `scan_state = 'included'` and the live composition writes `scanned`.
    P9's own tests write `included`, so all 5,000 of them agreed with a
    production run that could never form a group of more than one file.
    """
    # `seeds_for_file` orders anchor rows by `field_key`, so the seed of a
    # `Columbia PHYS1401 ...` file is `school=Columbia` -- the identity the two
    # Columbia files share, and the one whose group must therefore hold both.
    shared = [item for item in result.grouping
              if item.group is not None
              and item.group.proposed_basis == "school=Columbia"]
    assert shared, [item.group.proposed_basis for item in result.grouping
                    if item.group is not None]

    # Both files resolved to ONE group -- `65` §4.2's own requirement.
    assert len({item.group.group_id for item in shared}) == 1

    formed = shared[0]
    assert formed.neighborhood is not None
    assert formed.neighborhood.neighbors, (
        "P9 saw no neighbour for a file another file corroborates")
    assert formed.graph.edges, "no typed edge for a shared validated fact"
    anchored = formed.group.anchor_facts[0].file_ids
    assert len(anchored) == 2, anchored
    assert formed.group.anchor_count == 2


def test_the_command_can_be_run_twice_over_the_same_folder(tmp_path, capsys):
    """The shipped command crashed on its own SECOND invocation, with a traceback.

    Nothing about the corpus changes between the two runs. The database path
    defaults to the working directory (`cli.py`), so running the command twice is
    the ordinary thing a person does -- and the second one ended in
    `MalformedGroupRecord: ... a revision supersedes rather than replaces`,
    escaping the named-refusal handler whose own comment says "A traceback here
    would turn an answer the design worked hard to give into a crash."

    Two things differed between the stored record and the re-derived one, and
    NEITHER is a claim about the file:

    * `created_at`, which is this deployment's `now()` and is a fresh value every
      run;
    * `superseded_by` and `supersede_reason`, which the review merge stamped onto
      the membership AFTER it was written.

    A re-derivation asserts CONTENT. It does not re-assert when the conclusion was
    first reached, and it knows nothing about what happened to the record
    afterwards. So the stored row stands and the rerun is not a conflict -- which
    is what `record_group` always said it wanted: "a rerun over unchanged evidence
    is the same group and not a conflict."

    Every existing rerun test passed a FIXED clock, which is how five thousand of
    them agreed with a command that could not be run twice.
    """
    import cli

    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "syllabus.txt").write_text("PHYS1401 Syllabus\nColumbia, Fall 2026.\n")
    (corpus / "homework.txt").write_text("PHYS1401 Homework 3\nColumbia.\n")
    database = tmp_path / "plan.sqlite"
    argv = [str(corpus), "--situation", "academic.coursework",
            "--label", "Coursework", "--user", "jy", "--database", str(database)]

    assert cli.main(argv) == 0, capsys.readouterr().out
    first = capsys.readouterr().out

    # The same folder, the same flags, a later clock. This raised.
    assert cli.main(argv) == 0, capsys.readouterr().out
    second = capsys.readouterr().out

    for report in (first, second):
        assert "Files: 2 decided" in report, report


def test_the_documents_own_text_is_read_here_and_can_leave_by_no_route(
        conn, tmp_path):
    """The whole-text observation is evidence for THIS DEVICE and nothing else.

    `71` established that reading the document and naming a folder after it are
    two different knobs, and the whole-text observation deliberately turns only
    the first. This pins BOTH consequences of that, because they are one property
    and a future direct slot would break them together:

    * it is not a FACT, so no folder can be named after it;
    * it is therefore cited by no fact, so it can never become a dossier excerpt --
      and an excerpt is the only thing that travels to a model.

    The second half is not obvious and two independent audits worried about it.
    `p8_seam.py` builds a `ReleaseExcerpt` with `span=None` when the observation
    has none, and `span=None` legally means "the whole citation" -- so a span-less
    observation that DID reach a dossier would request the entire document. It
    cannot reach one: `dossier.py` builds excerpts from
    `[fact.observation_key for fact in facts]`, and this observation is nobody's
    fact.

    The chain, stated once: an observation becomes a fact only if a deployment's
    slot claims its locator; only a fact-cited observation becomes an excerpt;
    only an excerpt travels. Not a fact means not a folder name AND not egress.
    """
    import sqlite3

    from evidence_shape.store import observations_for_file
    from facts.read_surface import facts_for

    corpus = tmp_path / "corpus"
    corpus.mkdir()
    body = "Course syllabus for PHYS1401. Office hours Tuesday, credits 4.\n"
    (corpus / "syllabus.txt").write_text(body)
    (corpus / "homework.txt").write_text("PHYS1401 problem set 3. Due Friday.\n")

    import cli
    assert cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Coursework", "--user", "jy",
                     "--database", str(tmp_path / "plan.sqlite")]) == 0

    plan = sqlite3.connect(tmp_path / "plan.sqlite")
    plan.row_factory = sqlite3.Row
    row = plan.execute(
        "SELECT file_id, content_hash FROM files WHERE filename = 'syllabus.txt'"
    ).fetchone()

    whole = [o for o in observations_for_file(plan, row["file_id"])
             if o.raw_value == body]
    assert len(whole) == 1, "the document's own text is not being read at all"

    # It is nobody's fact, so nothing can be named after it and nothing cites it.
    cited = {ref for fact in facts_for(plan, file_id=row["file_id"],
                                       content_hash=row["content_hash"])
             for ref in json.loads(fact["evidence_refs"])}
    assert whole[0].observation_key not in cited, (
        "a slot claimed the whole-text observation; it is now a folder name and "
        "an unbounded model excerpt at the same time")



def test_a_file_matching_a_whole_ancestor_chain_is_placed_at_the_deepest_node(
        conn, tmp_path):
    """An ancestor is not a rival home. It is the same home, less specific.

    The seam this pins was invisible while the shipped tree was one folder deep.
    P10 nests -- `Coursework/Columbia/PHYS1401/Homework` -- and a file whose facts
    settle school, subject and work_type therefore matches all THREE nodes on its
    own chain. P11 scored them as competitors, they tied at 0.714 apiece, and the
    file abstained `multiple_supported_homes` and then `privacy_blocked` when the
    tie was escalated to a model that offline mode forbids.

    They are not multiple homes. Filing something in
    `Columbia/PHYS1401/Homework` files it in `Columbia` and in `PHYS1401` too --
    that is what nesting MEANS -- and §6.7 wants the deepest node the evidence
    actually supports. `identify_child_parent_fallback_or_none` is step 6's own
    name for this and had no implementation: `unsupported_levels=()` was
    hardcoded at every construction site in `pipeline.py`.
    """
    result = run_corpus_through(conn, tmp_path, fields=DEEP_FIELDS,
                                names=DEEP_CORPUS)
    by_id = {node.node_id: node for node in result.tree.tree.nodes}
    placed = [d for d in result.placement.decisions if d.outcome == pv.PLACE]

    assert placed, (
        "every file abstained; a nested tree made each file match its own "
        f"ancestor chain and P11 read that as competing homes: "
        f"{[(d.outcome, d.abstention_reason) for d in result.placement.decisions]}")

    for decision in placed:
        node = by_id[decision.destination.node_id]
        children = [n for n in result.tree.tree.nodes
                    if n.parent_node_id == node.node_id]
        assert not children, (
            f"placed at {node.display_label!r}, which still has children "
            f"{[c.display_label for c in children]}; the deepest supported node "
            "is the answer, not the first one that matched")


def test_the_shallower_ancestor_is_not_silently_forgotten(conn, tmp_path):
    """Dropping a rival and dropping an ancestor must not look the same.

    An ancestor removed from the candidate set is removed because it is the SAME
    destination less specific -- not because anything judged it unsuitable. The
    decision has to keep saying which facts carried it, or a person reviewing the
    placement cannot tell "we went deeper" from "we ruled that folder out".
    """
    result = run_corpus_through(conn, tmp_path, fields=DEEP_FIELDS,
                               names=DEEP_CORPUS)
    placed = [d for d in result.placement.decisions if d.outcome == pv.PLACE]
    assert placed

    for decision in placed:
        fields = {fact.field for fact in decision.matching_facts}
        assert "school" in fields, (
            "the deepest node was chosen and the levels above it stopped being "
            f"cited; matching facts name only {sorted(fields)}")
        assert decision.decision_depth.node_depth == (
            decision.decision_depth.supported_depth), (
            "the chosen node and the evidence disagree about depth")


# ==================================================================================
# What "ready to file" is allowed to mean
# ==================================================================================


def test_a_placement_the_person_must_still_confirm_is_not_called_ready_to_file(
        tmp_path, capsys):
    """`place` is P11's answer about WHERE. It is not permission to move anything.

    Three review policies ride on a placement -- `auto_eligible`,
    `review_required` and `blocked_pending_user` -- and the report keyed its
    headline on the OUTCOME alone, so a file nothing had classified, and a file
    carrying protected material, both printed under "Ready to file into X"
    alongside files that genuinely were.

    On the `multi` persona that was eight files of ten. A person reading it would
    have believed the product was ready to move a passport.
    """
    import cli

    corpus = tmp_path / "corpus"
    corpus.mkdir()
    # Nothing in these names a schema the detector ships a rule for, so P7
    # classifies nothing and the placements are `blocked_pending_user`. Two files
    # rather than one, so a PHYS1401 folder really is proposed and the placement
    # really does succeed -- the point is the WORD used for it, not an absence.
    # Neutral NAMES as well as neutral contents. A filename is evidence like any
    # other -- `filesystem.record` writes it as an observation -- so "rubric.txt"
    # and "solutions.txt" carry authored academic terms, and once a structured
    # identifier can corroborate a single term those files classify correctly and
    # really are ready. The point here is the word used for a file that is NOT.
    for name, code_text in (("a.txt", "QQQ1111"), ("b.txt", "QQQ1111"),
                            ("c.txt", "QQQ2222"), ("d.txt", "QQQ2222")):
        (corpus / name).write_text(code_text + "\n")

    code = cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Coursework", "--user", "jy",
                     "--database", str(tmp_path / "plan.sqlite")])
    out = capsys.readouterr().out
    assert code == 0, out

    assert "Ready to file" not in out, (
        "a file nothing has classified was announced as ready to move:\n" + out)
    assert "0 ready to file" in out, (
        "the headline count treats an unconfirmed placement as ready:\n" + out)


def test_the_report_says_where_an_unconfirmed_file_would_go_rather_than_hiding_it(
        tmp_path, capsys):
    """Not being ready is not a reason to withhold the answer.

    The opposite failure to the one above, and the one the north star cares about
    more: a person whose file cannot be moved yet still wants to know where it
    WOULD go and what is being waited on. `00`'s standing rule is that nothing is
    silently omitted -- and a placement demoted to a warning that dropped its
    destination would be exactly that.
    """
    import cli

    corpus = tmp_path / "corpus"
    corpus.mkdir()
    for name, code_text in (("a.txt", "QQQ1111"), ("b.txt", "QQQ1111"),
                            ("c.txt", "QQQ2222"), ("d.txt", "QQQ2222")):
        (corpus / name).write_text(code_text + "\n")

    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Coursework", "--user", "jy",
              "--database", str(tmp_path / "plan.sqlite")])
    out = capsys.readouterr().out

    assert "QQQ1111" in out, f"the destination disappeared from the report:\n{out}"
    assert "a.txt" in out, f"the file itself disappeared:\n{out}"


def test_a_value_only_protected_files_carry_never_mints_a_folder(conn, tmp_path):
    """Marked, counted, never opened -- and never SPOKEN.

    A folder name is public: it is visible in the filesystem and in every prompt
    that names a destination. A name derived from nothing but protected material
    publishes that material, and `X12345678` -- a client's passport number -- was
    a proposed folder on the litigator's corpus.

    Neither existing lever can close this. `protected_handling_classes` MARKS
    rather than removes, deliberately: "a file dropped out of the evidence is
    uncounted, and uncounted is worse than present-but-untouched". V5 refuses the
    WHOLE composition, which is the failure its own docstring records -- "the
    user lost the organisation and kept none of the protection".

    So the rule is stated where a NAME is minted, and it separates the two things
    the standing rule keeps together: the file stays a member and stays counted;
    what it stops doing is contributing a folder name. A value ANY ordinary file
    also carries is untouched, because then the name is not derived from
    protected material.
    """
    result = run_corpus_through(
        conn, tmp_path, fields=("subject",),
        names=("PHYS1401 Notes.pdf", "PHYS1401 Homework.pdf",
               "X12345678 Passport.pdf"),
        classify=_classify_passport_protected)
    labels = {node.display_label for node in result.tree.tree.nodes}

    assert "PHYS1401" in labels, f"the ordinary level did not survive: {labels}"
    assert "X12345678" not in labels, (
        f"a value only a protected file carries became a folder: {labels}")

    # And the file is still counted, not dropped -- the omission the rule forbids.
    decided = {d.subject.file_id for d in result.placement.decisions}
    assert len(decided) == 3, (
        f"a protected file fell out of the run entirely: {len(decided)} of 3")


def test_files_a_level_does_not_cover_still_reach_the_levels_below_it(
        conn, tmp_path):
    """The other half of the truncation fix, and the same mistake in a new place.

    `_project` recursed only INSIDE the per-value loop, so a level that covers
    SOME of a branch's files carried only those files downward and the rest fell
    out of every level beneath. A real household corpus makes this visible: two
    report cards carry a term and no subject, a lease and an insurance claim carry
    a subject and no term, and the term level runs first. The two report cards got
    their folder; the lease and the claim reached nothing.

    An uncovered file is not an unmatched file. The level simply says nothing
    about it, exactly as an EMPTY level says nothing about any file -- and the fix
    is the same one, applied to the members a level leaves behind rather than to
    the level as a whole.
    """
    result = run_corpus_through(
        conn, tmp_path, fields=("term", "subject"),
        names=("Spring2026 Ada Report Card.pdf", "Spring2026 Sam Report Card.pdf",
               "PR20264410 Lease.pdf", "CLM88213 Insurance Claim.pdf"))
    labels = {node.display_label for node in result.tree.tree.nodes}

    assert "Spring2026" in labels, f"the covered files lost their level too: {labels}"
    assert {"PR20264410", "CLM88213"} <= labels, (
        f"the files the term level said nothing about reached no level at all: "
        f"{labels}")


def test_an_uncovered_file_does_not_hang_off_the_covered_ones(conn, tmp_path):
    """The discriminating twin. Carrying uncovered members downward must not put
    them UNDER a value they do not have -- that would be worse than dropping them,
    because a person would find their lease inside a school term."""
    result = run_corpus_through(
        conn, tmp_path, fields=("term", "subject"),
        names=("Spring2026 Ada Report Card.pdf", "Spring2026 Sam Report Card.pdf",
               "PR20264410 Lease.pdf", "CLM88213 Insurance Claim.pdf"))
    by_id = {node.node_id: node for node in result.tree.tree.nodes}
    term = next(n for n in result.tree.tree.nodes if n.display_label == "Spring2026")

    for label in ("PR20264410", "CLM88213"):
        node = next(n for n in result.tree.tree.nodes if n.display_label == label)
        assert node.parent_node_id != term.node_id, (
            f"{label} was filed under a term its files never carried")
        assert by_id[node.parent_node_id].display_label != "Spring2026"


def test_a_level_with_one_value_is_skipped_and_the_levels_below_it_survive(
        conn, tmp_path):
    """A level that distinguishes nothing says nothing, exactly like an empty one.

    V2's own words: "a level with a single child is a folder the user opens to
    find one folder". True -- and it failed the WHOLE candidate for it, so a
    household whose files carry one term and two subjects got NO tree at all
    rather than a tree without the redundant term folder. That is V5's mistake in
    a third place: a per-LEVEL fault used to reject a whole composition.

    `00`:97 lists "create meaningless one-child levels" among the structural
    faults a template must not have. Skipping the level means it does not create
    one; rejecting the tree means the person gets nothing, which the sentence
    never asked for.
    """
    result = run_corpus_through(
        conn, tmp_path, fields=("term", "subject"),
        names=("Spring2026 Ada Report Card.pdf", "Spring2026 Sam Report Card.pdf",
               "Spring2026 PR20264410 Lease.pdf",
               "Spring2026 CLM88213 Insurance Claim.pdf"))
    labels = {node.display_label for node in result.tree.tree.nodes}

    assert "Spring2026" not in labels, (
        f"the single-term level was materialised anyway: {labels}")
    assert {"PR20264410", "CLM88213"} <= labels, (
        f"one redundant level took the whole tree with it: {labels}")


def test_a_level_that_really_does_divide_the_files_is_kept(conn, tmp_path):
    """The negative twin. Skipping a level that distinguishes nothing must not
    become skipping levels, or the tree flattens and the fix is worse than the
    defect."""
    result = run_corpus_through(
        conn, tmp_path, fields=("term", "subject"),
        names=("Fall2026 PHYS1401 Syllabus.pdf", "Fall2026 PHYS1401 Homework.pdf",
               "Spring2026 PHYS2801 Notes.pdf", "Spring2026 PHYS2801 Set.pdf"))
    labels = {node.display_label for node in result.tree.tree.nodes}

    assert {"Fall2026", "Spring2026"} <= labels, (
        f"two real terms were skipped as if they distinguished nothing: {labels}")
