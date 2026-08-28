# tests/p10/seam_corpus.py
"""One real corpus, written through every upstream part's own writers. TESTS ONLY.

`tests/p10/p6_fixtures.py` seeds P6; `tests/p10/p9_fixtures.py` builds P9 records
with member ids of its own. Neither on its own can drive P10's whole chain,
because routing needs an accepted GROUP whose members are the same files P6 holds
facts for — a group over invented ids materialises nothing and every level comes
back empty, which looks exactly like a broken materialiser and is not one.

So this module joins them: `seed_academics`'s three real files become the members
of a real P9 group, written through `record_group` / `record_membership` /
`record_acceptance`, and read back through P9's own `current_group`,
`memberships_for_group` and `stop_rule_outcome_for`.

**The one stand-in, named as one.** `AcceptedGroupReader.accepted(plan_version_id)`
has no live P9 implementation — P9 publishes acceptance per group
(`group_state_as_of`) and no ENUMERATION of the groups a plan version accepted.
`LiveGroupReader.accepted` below is that missing enumeration and nothing else: it
lists the ids from `group_acceptance` and asks P9's own reader for each verdict.
Every other method delegates. The day P9 publishes the enumeration this class
loses its first method and keeps the rest.

`p3_protected_area` writes a REAL P3 exclusion verdict through `exclusion_for`,
which is what makes `upstream.protected_areas` return something: a hand-written
row with `rule = "protected container"` would prove only that this file and
`upstream.py` agree on a string.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from facts.states import VALIDATED
from grouping.acceptance import group_state_as_of, record_acceptance
from grouping.records import (
    AnchorFact, Group, GroupAcceptance, Membership, Support,
)
from grouping.store import (
    current_group, memberships_for_group, record_group, record_membership,
    stop_rule_outcome_for,
)
from grouping.vocabulary import (
    ACCEPTED, COHERENT, DIRECT_ANCHOR, ENGINE, INCLUDED, NOT_FLAGGED,
    NO_SENSITIVITY, PENDING_REVIEW, RULES, SHARED_VALIDATED_FACT,
    STRONGLY_IDENTIFIED_FILE, SUPPORTED, USER,
)
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from scan_agent.exclusion import (
    APPLIES_TO_CANDIDATE_ROOT, exclusion_for, record_exclusion,
)
from scan_agent.run import start_scan_run
from scan_agent.selection import record_selection

from p10.p6_fixtures import CLOCK, seed_academics

T0 = "2026-08-27T00:00:00Z"
GROUP_ID = "g_columbia_coursework"
PLAN_0 = "plan_0"
ROOT_ANCHOR = "root_documents"
ORDINARY_CLASS = "personal_non_sensitive"
PROTECTED_CLASS = "highly_sensitive_credential_bearing"

#: The one template context this corpus's recipe is authored for. Named here so
#: the two catalogues below and the tests that read the tree agree on it without
#: any of them restating the string.
SCHEMA = "academic"


@dataclass(frozen=True)
class SeamCorpus:
    conn: object
    files: dict          # friendly name -> (file_id, content_hash, observation_key)
    selection_id: str
    scan_run_id: str
    protected_path: str
    protected_label: str

    def file_id(self, name: str) -> str:
        return self.files[name][0]

    def reader(self):
        return LiveGroupReader(self.conn)


class LiveGroupReader:
    """`upstream.AcceptedGroupReader`, over P9's real rows."""

    def __init__(self, conn) -> None:
        self._conn = conn

    def accepted(self, plan_version_id: str):
        # THE stand-in. Everything else on this class delegates to P9.
        rows = self._conn.execute(
            "SELECT DISTINCT group_id FROM group_acceptance "
            "WHERE plan_version_id = ? ORDER BY group_id",
            (plan_version_id,)).fetchall()
        return tuple(
            GroupAcceptance(
                acceptance_id=f"acc_{row['group_id']}",
                plan_version_id=plan_version_id, group_id=row["group_id"],
                membership_id=None,
                acceptance=group_state_as_of(
                    self._conn, group_id=row["group_id"],
                    plan_version_id=plan_version_id),
                review_state=PENDING_REVIEW, user_edited_label=None, aliases=(),
                review_decision_ref=None, decided_by=USER, created_at=T0)
            for row in rows)

    def group(self, group_id: str):
        return current_group(self._conn, group_id)

    def memberships(self, group_id: str):
        return memberships_for_group(self._conn, group_id)

    def stop_rule_outcome(self, group_id: str):
        return stop_rule_outcome_for(self._conn, group_id)


def seed_seam_corpus(conn, tmp_path: Path) -> SeamCorpus:
    """§5.5's three files, one accepted P9 group over them, one protected area.

    The caller has already created P1's, P3's, P4's, P6's, P7's and P9's schemas;
    this writes rows and creates none, so a missing table reports itself as a
    missing table rather than being papered over here.
    """
    corpus = seed_academics(conn, tmp_path)
    _accept_a_group_over(conn, corpus)
    for name in corpus.subjects:
        file_id, content_hash, key = corpus.subjects[name]
        ClassificationStore(conn).write(ClassificationRecord(
            file_id=file_id, content_hash=content_hash,
            handling_class=ORDINARY_CLASS, protected=False, basis="detector",
            evidence_refs=(key,), reliability_state="direct", observed_at=CLOCK))

    selection_id = record_selection(
        conn, sources=[tmp_path], candidate_roots=[tmp_path],
        cross_folder_moves=False, selected_by="jy")
    scan_run_id = start_scan_run(conn, selection_id)
    protected_path = str(tmp_path / "Numbers.app")
    # P3's OWN rule fires here. `is_protected_container` is checked FIRST and
    # takes no keyword that could switch it off, which is why the verdict is
    # produced rather than written: a hand-made row would prove nothing about
    # whether P3 would actually have marked this path.
    verdict = exclusion_for(protected_path, is_dir=True,
                            applies_to=APPLIES_TO_CANDIDATE_ROOT)
    assert verdict is not None and verdict.rule == "protected container", verdict
    record_exclusion(conn, scan_run_id, verdict)

    return SeamCorpus(
        conn=conn, files=dict(corpus.subjects), selection_id=selection_id,
        scan_run_id=scan_run_id, protected_path=protected_path,
        protected_label="Numbers.app")


def _accept_a_group_over(conn, corpus) -> None:
    names = ("syllabus", "hw3", "lab")
    file_ids = tuple(corpus.subjects[name][0] for name in names)
    record_group(conn, Group(
        group_id=GROUP_ID, seed_ref="seed_1", seed_kind=STRONGLY_IDENTIFIED_FILE,
        proposed_basis="school = Columbia",
        anchor_facts=(AnchorFact(
            field="school", value="Columbia", file_ids=file_ids,
            reliability_state=VALIDATED,
            observation_key=corpus.subjects["syllabus"][2]),),
        pre_model_signals={"anchor_count": 1}, anchor_count=1,
        coherence_verdict=COHERENT,
        coherence_citations=(corpus.subjects["syllabus"][2],),
        group_category=SCHEMA, display_label="Columbia coursework",
        label_source=ENGINE, conflicts=(), stop_rule_hits=(), state=SUPPORTED,
        sensitivity_state=NO_SENSITIVITY, dossier_id=None, llm_response_ref=None,
        validation_verdict_ref=None, created_by=RULES, created_at=T0))
    for name in names:
        file_id, content_hash, key = corpus.subjects[name]
        record_membership(conn, Membership(
            membership_id=f"m_{file_id}", group_id=GROUP_ID, file_id=file_id,
            content_hash=content_hash, basis=DIRECT_ANCHOR, decision=INCLUDED,
            decision_source=RULES,
            support=(Support(support_kind=SHARED_VALIDATED_FACT,
                             observation_key=key, quote_or_field="school",
                             location="heading", edge_ref=None),),
            insufficient_evidence=False, insufficiency_statement=None,
            conflicts=(), outlier_flag=NOT_FLAGGED, validation_verdict_ref=None,
            created_at=T0))
    record_acceptance(conn, GroupAcceptance(
        acceptance_id="acc_1", plan_version_id=PLAN_0, group_id=GROUP_ID,
        membership_id=None, acceptance=ACCEPTED, review_state=PENDING_REVIEW,
        user_edited_label=None, aliases=(), review_decision_ref=None,
        decided_by=USER, created_at=T0))


# --- the recipe, and the two nestings it offers ------------------------------------


def two_dimension_catalogue(**over):
    """`two_dimension_manifest`, through the real loader."""
    from tree_design.catalogue import load_catalogue

    return load_catalogue(lambda: json.dumps(two_dimension_manifest(**over)))


def two_dimension_manifest(*, default_order_id: str = "course_first",
                           work_type_label: str = "Assignment type",
                           subject_label: str = "Course",
                           release_id: str = "rel_seam") -> dict:
    """One recipe over `subject` and `work_type`, offering BOTH nestings.

    A DICT rather than a catalogue, because two of its readers need the raw
    records: `load_shipped_catalogue` derives `release_id` as a digest of the
    bytes it read, so a test that wants a genuinely different library has to
    hand it different bytes rather than a different string.

    `subject_label` is the level the user renames in `64` -- the library calls
    it "Course" and the person calls it "Class" -- and it moves for the same
    reason `work_type_label` does: changing exactly one authored value and
    re-running the chain is how a difference is attributed to it.

    `tree_design.fixtures.template_library_fixture()` has a single dimension, so
    ordering can make no difference to the tree it builds and `candidate_orders`
    cannot be observed through it at all. Two dimensions and two orders is the
    smallest recipe where the recommendation is visible in the frozen tree, which
    is what lets a test say whether `candidate_orders` reaches P11.

    `work_type_label` is the authored per-schema name of the work-type LEVEL —
    `RoleBinding.label`, which `ResolvedDimension.display_label` carries into
    every node's §5.12 explanation. It is a parameter for the same reason
    `default_order_id` is: changing exactly one authored value and re-running the
    whole chain is how a test attributes a difference in P10's output to that
    value and to nothing else.

    `default_order_id` selects which order the recipe RECOMMENDS. Flipping it is
    the whole experiment: the corpus, the facts and the groups are identical and
    only the recommendation moves, so any change in the tree P11 indexes is
    attributable to `candidate_orders` and to nothing else.

    The fragment states NO `relative_order`. That is deliberate: a fragment's
    relative order is a constraint the recommendation may not override
    (`routing._recommended_order`), so a fragment that pinned the nesting would
    make the recommendation unobservable — the experiment would come back
    "no difference" for the wrong reason.
    """
    from tree_design.vocabulary import (
        BUILT_IN, CROSS_DOMAIN, PUBLISHED, REQUIRED,
    )

    def order(order_id, roles, rationale):
        return {
            "order_id": order_id, "is_default": order_id == default_order_id,
            "rationale": rationale,
            "dimensions": [
                {"role_ref": role, "order_index": index,
                 "requirement": REQUIRED, "metadata_only": False,
                 "retrieval_rationale": f"Users look for work by {role}."}
                for index, role in enumerate(roles)],
        }

    manifest = {
        "release_id": release_id,
        "fragments": [{
            "fragment_id": "coursework", "fragment_version": 1,
            "roles": ["subject", "work_type"], "relative_order": [],
            "imports": [], "optional_roles": [], "metadata_only_roles": [],
            "allowed_values": {}, "privacy_floor": "policy.public",
            "provenance": ["row:seam"],
        }],
        "definitions": [{
            "template_id": "t.coursework", "template_version": 1,
            "origin_kind": BUILT_IN, "scope_kind": CROSS_DOMAIN,
            "publication_state": PUBLISHED,
            "fragment_refs": [{"fragment_id": "coursework",
                               "fragment_version": 1}],
            "candidate_orders": [
                order("course_first", ["subject", "work_type"],
                      "A student looks for the course and then the kind of work."),
                order("work_type_first", ["work_type", "subject"],
                      "A student who thinks in deadlines looks for all the "
                      "homework first."),
            ],
            "optional_branch_patterns": [],
            "sensitivity_policy_ref": "policy.public",
            "validation_constraints": [], "example_label_chains": [],
        }],
        "applicabilities": [{
            "applicability_id": "a.coursework", "applicability_version": 1,
            "template_id": "t.coursework", "template_version": 1,
            "uses_schema": SCHEMA, "purpose_profile_ref": None,
            "allowed_fields": ["subject", "work_type"],
            "detection_signal_refs": ["signal.seam"],
            "role_bindings": [
                # The two authored, per-schema names. `ResolvedDimension.
                # display_label` carries them and `materialise._label_of` puts
                # them in every node's §5.12 explanation, so a test can read the
                # frozen tree and say whether the authored word crossed.
                {"role_ref": "subject", "field_ref": "subject",
                 "label": subject_label},
                {"role_ref": "work_type", "field_ref": "work_type",
                 "label": work_type_label},
            ],
            "exclusions": [], "provenance": ["row:seam"],
        }],
    }
    return manifest
