# tests/p10/multi_life_corpus.py
"""One disk holding three lives at once. TESTS ONLY.

`seam_corpus` seeds ONE accepted group in ONE schema. That is the corpus every
P10 test has run against, and it is the reason `59` §2's finding was invisible
from the suite: with a single group there is exactly one branch, so a chain that
collapses several lives into one and a chain that does not produce the same tree.

This is `59` §2's corpus instead — a practice, a degree, and a child's health
records on one disk, which is the ordinary state of a real person's files:

* `g_columbia_coursework` in `academic`, three files, a shipped recipe;
* `g_acme_matter` in `law_practice`, two files, a different shipped recipe;
* `g_child_health` in `medical`, one file, and `medical` declares no fields and
  no template covers it — `00` §3.15's safety domain. It is here because the
  group whose domain nothing covers is the case that must stay VISIBLE, and a
  corpus with only coverable groups cannot tell whether it does.

Everything is written through the same live writers `seam_corpus` uses, and the
group reader is `seam_corpus`'s, because two enumerations of one plan version's
acceptances would be two things to keep in step.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from facts.states import VALIDATED
from grouping.acceptance import record_acceptance
from grouping.records import AnchorFact, Group, GroupAcceptance, Membership, Support
from grouping.store import record_group, record_membership
from grouping.vocabulary import (
    ACCEPTED, COHERENT, DIRECT_ANCHOR, ENGINE, INCLUDED, NOT_FLAGGED,
    NO_SENSITIVITY, PENDING_REVIEW, RULES, SHARED_VALIDATED_FACT,
    STRONGLY_IDENTIFIED_FILE, SUPPORTED, USER,
)
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from scan_agent.exclusion import APPLIES_TO_CANDIDATE_ROOT, exclusion_for, record_exclusion
from scan_agent.inventory import record_directory
from scan_agent.run import start_scan_run
from scan_agent.selection import record_selection
from scan_agent.traversal import ObservedDirectory

# The private helpers are imported rather than restated: a second copy of the
# `record_file` -> `record_run` -> `record_observation` -> `write_fact` sequence
# is a second place the live writers' argument vocabularies can drift.
from p10.p6_fixtures import CLOCK, _fact, _subject
from p10.seam_corpus import (
    ORDINARY_CLASS, PLAN_0, PROTECTED_CLASS, ROOT_ANCHOR, T0, LiveGroupReader,
)

ACADEMIC_GROUP = "g_columbia_coursework"
LAW_GROUP = "g_acme_matter"
MEDICAL_GROUP = "g_child_health"

ACADEMIC_LABEL = "Columbia coursework"
LAW_LABEL = "Acme Industries matter"
MEDICAL_LABEL = "Ada's health records"

#: The three domains this disk spans. `medical` is one of `00` §3.15's safety
#: domains: it is recognised, it declares no fields, and no template covers it.
ACADEMIC_SCHEMA = "academic"
LAW_SCHEMA = "law_practice"
MEDICAL_SCHEMA = "medical"

#: (friendly name, raw text, facts). One per file, through the live writers.
_FILES = (
    ("syllabus", "BUSIB 4300 Syllabus",
     (("school", "Columbia"), ("subject", "BUSIB 4300"), ("work_type", "Syllabus"))),
    ("hw3", "BUSIB 4300 Homework 3",
     (("school", "Columbia"), ("subject", "BUSIB 4300"), ("work_type", "Homework"))),
    ("lab", "PHYS1401 Lab",
     (("school", "Columbia"), ("subject", "PHYS1401"))),
    ("pleading", "Acme Industries - Motion to Dismiss",
     (("client", "Acme Industries"), ("work_type", "Pleading"))),
    ("retainer", "Acme Industries - Retainer Agreement",
     (("client", "Acme Industries"), ("work_type", "Retainer"))),
    # A second client, so the `client` level has two children. V2 refuses a
    # one-child level and would refuse this branch for a reason that has nothing
    # to do with the corpus spanning three lives.
    ("borden_letter", "Borden Trust - Advice Letter",
     (("client", "Borden Trust"), ("work_type", "Pleading"))),
    # No destination-eligible fact of any kind. `medical` declares no fields
    # (`facts.domains.FIELD_LESS_SCHEMA_IDS`), so this file has nothing a folder
    # level could be built from, which is exactly the point.
    ("immunisation", "Ada - immunisation record", ()),
)

_MEMBERS = {
    ACADEMIC_GROUP: ("syllabus", "hw3", "lab"),
    LAW_GROUP: ("pleading", "retainer", "borden_letter"),
    MEDICAL_GROUP: ("immunisation",),
}

_ANCHORS = {
    ACADEMIC_GROUP: ("school", "Columbia", "syllabus"),
    LAW_GROUP: ("our_firm", "Yung & Co", "pleading"),
    MEDICAL_GROUP: ("subject_of_record", "Ada", "immunisation"),
}

_SCHEMAS = {
    ACADEMIC_GROUP: ACADEMIC_SCHEMA,
    LAW_GROUP: LAW_SCHEMA,
    MEDICAL_GROUP: MEDICAL_SCHEMA,
}

_LABELS = {
    ACADEMIC_GROUP: ACADEMIC_LABEL,
    LAW_GROUP: LAW_LABEL,
    MEDICAL_GROUP: MEDICAL_LABEL,
}


@dataclass(frozen=True)
class MultiLifeCorpus:
    conn: object
    files: dict          # friendly name -> (file_id, content_hash, observation_key)
    selection_id: str
    scan_run_id: str
    protected_path: str
    protected_label: str
    #: §5.10's inventory: one directory the user already made, which the canvas
    #: offers as a branch of its own and which names NO accepted group.
    existing_folder_path: str
    existing_folder_label: str

    def file_id(self, name: str) -> str:
        return self.files[name][0]

    def file_ids(self, *names: str) -> frozenset[str]:
        return frozenset(self.files[name][0] for name in names)

    def group_file_ids(self, group_id: str) -> frozenset[str]:
        return self.file_ids(*_MEMBERS[group_id])

    def reader(self):
        return LiveGroupReader(self.conn)


def seed_multi_life_corpus(conn, tmp_path: Path) -> MultiLifeCorpus:
    """Six files, three accepted groups in three schemas, one protected area."""
    files: dict[str, tuple[str, str, str]] = {}
    for name, raw, facts in _FILES:
        file_id, content_hash, key = _subject(conn, tmp_path, name, raw)
        files[name] = (file_id, content_hash, key)
        for field_key, value in facts:
            _fact(conn, file_id, content_hash, key, field_key, value)

    store = ClassificationStore(conn)
    for name, (file_id, content_hash, key) in files.items():
        # The child's health record is the one file P7 classes as protected. It
        # is MARKED and it is still a member of its group: the standing rule is
        # marked and counted, never removed.
        protected = name == "immunisation"
        store.write(ClassificationRecord(
            file_id=file_id, content_hash=content_hash,
            handling_class=PROTECTED_CLASS if protected else ORDINARY_CLASS,
            protected=protected, basis="detector", evidence_refs=(key,),
            reliability_state="direct", observed_at=CLOCK))

    for group_id in (ACADEMIC_GROUP, LAW_GROUP, MEDICAL_GROUP):
        _accept(conn, files, group_id)

    selection_id = record_selection(
        conn, sources=[tmp_path], candidate_roots=[tmp_path],
        cross_folder_moves=False, selected_by="jy")
    scan_run_id = start_scan_run(conn, selection_id)
    protected_path = str(tmp_path / "Numbers.app")
    verdict = exclusion_for(protected_path, is_dir=True,
                            applies_to=APPLIES_TO_CANDIDATE_ROOT)
    assert verdict is not None and verdict.rule == "protected container", verdict
    record_exclusion(conn, scan_run_id, verdict)

    existing = str(tmp_path / "Matters")
    record_directory(conn, scan_run_id, ObservedDirectory(
        directory_path=existing, parent_directory=str(tmp_path),
        file_count=12, subdirectory_count=0, extension_mix={".pdf": 12},
        project_root_markers=(), applies_to=APPLIES_TO_CANDIDATE_ROOT))

    return MultiLifeCorpus(
        conn=conn, files=files, selection_id=selection_id,
        scan_run_id=scan_run_id, protected_path=protected_path,
        protected_label="Numbers.app", existing_folder_path=existing,
        existing_folder_label="Matters")


def _accept(conn, files, group_id: str) -> None:
    names = _MEMBERS[group_id]
    file_ids = tuple(files[name][0] for name in names)
    field, value, anchor_name = _ANCHORS[group_id]
    anchor_key = files[anchor_name][2]
    record_group(conn, Group(
        group_id=group_id, seed_ref=f"seed_{group_id}",
        seed_kind=STRONGLY_IDENTIFIED_FILE,
        proposed_basis=f"{field} = {value}",
        anchor_facts=(AnchorFact(
            field=field, value=value, file_ids=file_ids,
            reliability_state=VALIDATED, observation_key=anchor_key),),
        pre_model_signals={"anchor_count": 1}, anchor_count=1,
        coherence_verdict=COHERENT, coherence_citations=(anchor_key,),
        group_category=_SCHEMAS[group_id], display_label=_LABELS[group_id],
        label_source=ENGINE, conflicts=(), stop_rule_hits=(), state=SUPPORTED,
        sensitivity_state=NO_SENSITIVITY, dossier_id=None, llm_response_ref=None,
        validation_verdict_ref=None, created_by=RULES, created_at=T0))
    for name in names:
        file_id, content_hash, key = files[name]
        record_membership(conn, Membership(
            membership_id=f"m_{file_id}", group_id=group_id, file_id=file_id,
            content_hash=content_hash, basis=DIRECT_ANCHOR, decision=INCLUDED,
            decision_source=RULES,
            support=(Support(support_kind=SHARED_VALIDATED_FACT,
                             observation_key=key, quote_or_field=field,
                             location="heading", edge_ref=None),),
            insufficient_evidence=False, insufficiency_statement=None,
            conflicts=(), outlier_flag=NOT_FLAGGED, validation_verdict_ref=None,
            created_at=T0))
    record_acceptance(conn, GroupAcceptance(
        acceptance_id=f"acc_{group_id}", plan_version_id=PLAN_0,
        group_id=group_id, membership_id=None, acceptance=ACCEPTED,
        review_state=PENDING_REVIEW, user_edited_label=None, aliases=(),
        review_decision_ref=None, decided_by=USER, created_at=T0))


# --- the two recipes this disk's two coverable lives want ---------------------------


def three_life_catalogue():
    """One recipe for `academic`, one for `law_practice`, NONE for `medical`.

    Two schemas and two definitions, because the collapse `59` §2 describes is a
    collapse ACROSS recipes: with one recipe every branch routes through the same
    rows and the question of whether a composition may span lives never arises.

    Nothing here covers `medical`, and that absence is the fixture's third
    subject. `00` §3.15 keeps that domain out of the tree deliberately, so the
    group is real, accepted, and uncoverable — and it still may not vanish.
    """
    from tree_design.catalogue import load_catalogue
    from tree_design.vocabulary import BUILT_IN, CROSS_DOMAIN, PUBLISHED, REQUIRED

    def order(order_id, roles, rationale):
        return {
            "order_id": order_id, "is_default": True, "rationale": rationale,
            "dimensions": [
                {"role_ref": role, "order_index": index,
                 "requirement": REQUIRED, "metadata_only": False,
                 "retrieval_rationale": f"Users look for work by {role}."}
                for index, role in enumerate(roles)],
        }

    manifest = {
        "release_id": "rel_multi_life",
        "fragments": [
            {"fragment_id": "coursework", "fragment_version": 1,
             "roles": ["subject", "work_type"], "relative_order": [],
             "imports": [], "optional_roles": [], "metadata_only_roles": [],
             "allowed_values": {}, "privacy_floor": "policy.public",
             "provenance": ["row:multi-life"]},
            {"fragment_id": "matter", "fragment_version": 1,
             "roles": ["client", "work_type"], "relative_order": [],
             "imports": [], "optional_roles": [], "metadata_only_roles": [],
             "allowed_values": {}, "privacy_floor": "policy.public",
             "provenance": ["row:multi-life"]},
        ],
        "definitions": [
            {"template_id": "t.coursework", "template_version": 1,
             "origin_kind": BUILT_IN, "scope_kind": CROSS_DOMAIN,
             "publication_state": PUBLISHED,
             "fragment_refs": [{"fragment_id": "coursework",
                                "fragment_version": 1}],
             "candidate_orders": [order(
                 "course_first", ["subject", "work_type"],
                 "A student looks for the course and then the kind of work.")],
             "sole_order_attestation": (
                 "Coursework has one sensible nesting: the course is the thing a "
                 "student names first."),
             "optional_branch_patterns": [],
             "sensitivity_policy_ref": "policy.public",
             "validation_constraints": [], "example_label_chains": []},
            {"template_id": "t.matter", "template_version": 1,
             "origin_kind": BUILT_IN, "scope_kind": CROSS_DOMAIN,
             "publication_state": PUBLISHED,
             "fragment_refs": [{"fragment_id": "matter",
                                "fragment_version": 1}],
             "candidate_orders": [order(
                 "client_first", ["client", "work_type"],
                 "A practitioner looks for the client and then the document.")],
             "sole_order_attestation": (
                 "A matter is named by its client before it is named by anything "
                 "else."),
             "optional_branch_patterns": [],
             "sensitivity_policy_ref": "policy.public",
             "validation_constraints": [], "example_label_chains": []},
        ],
        "applicabilities": [
            {"applicability_id": "a.coursework", "applicability_version": 1,
             "template_id": "t.coursework", "template_version": 1,
             "uses_schema": ACADEMIC_SCHEMA, "purpose_profile_ref": None,
             "allowed_fields": ["subject", "work_type"],
             "detection_signal_refs": ["signal.multi-life"],
             "role_bindings": [
                 {"role_ref": "subject", "field_ref": "subject",
                  "label": "Course"},
                 {"role_ref": "work_type", "field_ref": "work_type",
                  "label": "Assignment type"}],
             "exclusions": [], "provenance": ["row:multi-life"]},
            {"applicability_id": "a.matter", "applicability_version": 1,
             "template_id": "t.matter", "template_version": 1,
             "uses_schema": LAW_SCHEMA, "purpose_profile_ref": None,
             "allowed_fields": ["client", "work_type"],
             "detection_signal_refs": ["signal.multi-life"],
             "role_bindings": [
                 {"role_ref": "client", "field_ref": "client",
                  "label": "Client"},
                 {"role_ref": "work_type", "field_ref": "work_type",
                  "label": "Document type"}],
             "exclusions": [], "provenance": ["row:multi-life"]},
        ],
    }
    return load_catalogue(lambda: json.dumps(manifest))
