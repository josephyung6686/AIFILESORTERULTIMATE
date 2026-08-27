# tests/p10/p9_fixtures.py
"""Accepted P9 groups, built from P9's LIVE records. Tests only.

P9 publishes no accepted-group ENUMERATION, so P10 cannot ask P9 which groups a
plan version accepted. What it can do is refuse to invent their shape: every
object here is a real `grouping.records` instance, so the day P9 publishes that
reader this fixture is replaced and nothing about the shape changes.

Six names in P10's SPEC do not exist in P9's live code and are corrected here:
the user-approved label is `GroupAcceptance.user_edited_label` falling back to
`Group.display_label`, the membership axis is `Membership.basis`, and rejection
is `GroupAcceptance.acceptance`, never `Group.state`.

Three more are corrections to THIS fixture, each verified against the live
record rather than reconstructed:

* `AnchorFact` is `(field, value, file_ids, reliability_state, observation_key)`
  — `src/grouping/records.py:85-89`. There is no `fact_id` and no `field_key`,
  and `file_ids` is required: `__post_init__` raises "an anchor fact no file
  states is not an anchor" on an empty tuple (`:97-100`). The durable handle for
  an anchor is therefore `observation_key`, which is what `AcceptedGroup.
  anchor_facts` carries.
* `Membership` requires `validation_verdict_ref` and `created_at`
  (`src/grouping/records.py:228-230`) and refuses an empty `support`: "a
  membership with no support cannot say why the file belongs" (`:245-248`).
  A `direct-anchor` membership additionally requires a `shared-validated-fact`
  support kind (`:252-260`), so the support tuple here is a real `Support`.
* `sensitivity_state` is P9's, not P7's. `SENSITIVITY_STATES` is
  `(none, sensitive-present)` (`src/grouping/vocabulary.py:207-210`);
  `personal_non_sensitive` is a P7 HANDLING class (`src/privacy/vocabulary.py:
  86-92`). `Group.__post_init__` only checks the field is non-empty, so the
  wrong value would have been stored silently — which is exactly the
  cross-part vocabulary leak this seam exists to stop.
"""
from __future__ import annotations

from grouping.records import (
    AnchorFact,
    Group,
    GroupAcceptance,
    Membership,
    StopRuleOutcome,
    Support,
)
from grouping.vocabulary import (
    ACCEPTED,
    CANDIDATE,
    COHERENT,
    CONTEXT_SUPPORTED,
    DIRECT_ANCHOR,
    ENGINE,
    EXCLUDED,
    INCLUDED,
    NOT_FLAGGED,
    NO_SENSITIVITY,
    REJECTED,
    RULES,
    SHARED_VALIDATED_FACT,
    SR1,
    STRONGLY_IDENTIFIED_FILE,
    TENTATIVE_DISCOVERY,
    USER,
    USER_ACCEPTED,
    VALIDATED_SHARED_FACT,
)

T0 = "2026-08-27T00:00:00Z"


def _live_group(group_id: str, seed_kind: str) -> Group:
    """A record `src/grouping/pipeline.py:207-243` can write today, field for field.

    Every field below is copied from that call site, not chosen here. `_group_for`
    is the ONLY originating `Group` writer in `src/` — `store.py:181` is a
    row-reader that returns whatever was stored, and `p8_seam.apply_p8_verdict`
    writes `Membership` rows and never rewrites a group. So this is the whole of
    what P10 can expect to receive from live P9:

        coherence_verdict  = None
        coherence_citations= ()
        group_category     = None
        display_label      = None
        label_source       = None
        pre_model_signals  = {"anchor_count": n}

    TWO of that call site's fields moved since this plan was written, and both
    were re-verified against live source rather than carried forward:

    * `state` is `SUPPORTED if meets_support_bar(...) else CANDIDATE`
      (`pipeline.py:344-347`). An earlier draft of this fixture recorded that
      `supported` had no production caller; it has one now. The fixture stays on
      `candidate` because it is still the state a group takes when the support
      bar is not met, and because no P10 code in Tasks 1-14 reads `Group.state`
      at all — `accepted_groups` resolves acceptance from `GroupAcceptance` and
      renderability from `StopRuleOutcome`. A `supported` group belongs with
      Task 17's swap, alongside the labelled shape.
    * `conflicts` is `tuple(conflicts)` from the injected oracle
      (`pipeline.py:338`), no longer a hardcoded `()`. `()` here is a seed the
      oracle found no conflict for, which is a real answer rather than a stub.
    """
    facts = (AnchorFact(
        field="subject", value="PHYS1401", file_ids=(f"anchor_{group_id}",),
        reliability_state="validated", observation_key=f"obs_{group_id}",
    ),)
    return Group(
        group_id=group_id, seed_ref=f"f_{group_id}:h_{group_id}",
        seed_kind=seed_kind, proposed_basis="subject=PHYS1401",
        anchor_facts=facts, pre_model_signals={"anchor_count": len(facts)},
        anchor_count=len(facts), coherence_verdict=None, coherence_citations=(),
        group_category=None, display_label=None, label_source=None,
        conflicts=(), stop_rule_hits=(), state=CANDIDATE,
        sensitivity_state=NO_SENSITIVITY, dossier_id=None, llm_response_ref=None,
        validation_verdict_ref=None, created_by=RULES, created_at=T0,
    )


def _labelled_group(group_id: str, label: str, category: str,
                    seed_kind: str) -> Group:
    """The same record once a coherence verdict and a label exist.

    **P9 cannot produce this today** — see SPEC corrections row 16. It is here
    because P10 cannot name a branch without it: `Group.__post_init__` refuses
    `display_label` or `group_category` unless `coherence_verdict == 'coherent'`,
    so the label and the verdict arrive together or not at all. `replace` re-runs
    that check, which is why this is built from the live record rather than
    written out separately: the enriched shape is held to the same record
    contract as the real one, and the day P9 ships the labelling path this
    function is deleted rather than corrected.
    """
    import dataclasses

    return dataclasses.replace(
        _live_group(group_id, seed_kind),
        coherence_verdict=COHERENT, coherence_citations=(f"obs_{group_id}",),
        group_category=category, display_label=label, label_source=ENGINE,
    )


def _tentative_outcome(group_id: str) -> StopRuleOutcome:
    """SR1 fired alone, so §4.9 permits showing the group "only as tentative
    discovery candidates, if at all".

    This is the ONLY way `tentative-discovery` reaches production
    (`src/grouping/graph.py:334`). It is a `StopRuleOutcome.outcome` over
    `STOP_RULE_OUTCOMES`, **not** a `Group.state` — the same string lives in both
    vocabularies and only one of them is written. P10 therefore cannot test its
    no-render rule with `group.state == 'tentative-discovery'`; it has to read
    the stop-rule record, which is why `AcceptedGroupReader` grew a third method.
    """
    return StopRuleOutcome(
        group_id=group_id, rules_fired=(SR1,),
        evidence_refs=(f"obs_{group_id}",), outcome=TENTATIVE_DISCOVERY,
    )


def _membership(group_id: str, file_id: str, basis: str, decision: str) -> Membership:
    return Membership(
        membership_id=f"m_{group_id}_{file_id}", group_id=group_id, file_id=file_id,
        content_hash=f"h_{file_id}", basis=basis, decision=decision,
        decision_source=RULES,
        support=(Support(
            support_kind=SHARED_VALIDATED_FACT, observation_key=f"obs_{group_id}",
            quote_or_field="subject", location="heading", edge_ref=None,
        ),),
        insufficient_evidence=False,
        insufficiency_statement=None, conflicts=(), outlier_flag=NOT_FLAGGED,
        validation_verdict_ref=None, created_at=T0,
    )


def _acceptance(group_id: str, plan_version_id: str, acceptance: str,
                label: str | None) -> GroupAcceptance:
    return GroupAcceptance(
        acceptance_id=f"acc_{group_id}", plan_version_id=plan_version_id,
        group_id=group_id, membership_id=None, acceptance=acceptance,
        review_state=USER_ACCEPTED, user_edited_label=label, aliases=(),
        review_decision_ref=None, decided_by=USER, created_at=T0,
    )


class FixtureGroupReader:
    """Satisfies `upstream.AcceptedGroupReader` with recorded live records."""

    def __init__(self, plan_version_id: str = "plan_1") -> None:
        self.plan_version_id = plan_version_id
        self._groups = {
            # Labelled — the shape P10 needs and P9 cannot emit yet (row 16).
            "g_phys1401": _labelled_group(
                "g_phys1401", "PHYS 1401", "academic", VALIDATED_SHARED_FACT),
            "g_columbia_app": _labelled_group(
                "g_columbia_app", "Columbia application",
                "college_applications", STRONGLY_IDENTIFIED_FILE),
            "g_random": _labelled_group(
                "g_random", "Screenshots from March", "photos",
                STRONGLY_IDENTIFIED_FILE),
            # Live-shaped — exactly what P9 writes TODAY. Unlabelled, candidate.
            # Every test that does not name it still runs past it, which is the
            # point: the state P9 actually produces is in the default corpus.
            "g_live": _live_group("g_live", VALIDATED_SHARED_FACT),
            # SR1 fired alone. §4.9 permits showing this "only as tentative
            # discovery candidates, if at all"; P10's answer is "not at all".
            "g_tentative": _labelled_group(
                "g_tentative", "Loose scans", "photos", STRONGLY_IDENTIFIED_FILE),
        }
        self._stop_rule_outcomes = {
            "g_tentative": _tentative_outcome("g_tentative"),
        }
        self._memberships = {
            "g_phys1401": (
                _membership("g_phys1401", "lecture-08", DIRECT_ANCHOR, INCLUDED),
                _membership("g_phys1401", "hw-3", CONTEXT_SUPPORTED, INCLUDED),
                _membership("g_phys1401", "duke-essay", DIRECT_ANCHOR, EXCLUDED),
            ),
            "g_columbia_app": (
                # The same transcript is a legal member of two accepted groups
                # (§4.9); the tree must not force it to one branch.
                _membership("g_columbia_app", "transcript", DIRECT_ANCHOR, INCLUDED),
            ),
            "g_random": (
                _membership("g_random", "shot-1", DIRECT_ANCHOR, INCLUDED),
            ),
            "g_live": (
                _membership("g_live", "unlabelled-1", DIRECT_ANCHOR, INCLUDED),
            ),
            "g_tentative": (
                _membership("g_tentative", "scan-1", DIRECT_ANCHOR, INCLUDED),
            ),
        }
        self._acceptances = (
            _acceptance("g_phys1401", plan_version_id, ACCEPTED, "PHYS 1401 course"),
            _acceptance("g_columbia_app", plan_version_id, ACCEPTED, None),
            _acceptance("g_random", plan_version_id, REJECTED, None),
            _acceptance("g_tentative", plan_version_id, ACCEPTED, None),
        )

    def accepted(self, plan_version_id: str):
        return tuple(
            a for a in self._acceptances if a.plan_version_id == plan_version_id
        )

    def group(self, group_id: str):
        return self._groups[group_id]

    def memberships(self, group_id: str):
        return self._memberships[group_id]

    def stop_rule_outcome(self, group_id: str):
        """`grouping.store.stop_rule_outcome_for(conn, group_id)` returns exactly
        this, `None` included, so the swap is a signature match."""
        return self._stop_rule_outcomes.get(group_id)


def live_shaped_reader(plan_version_id: str = "plan_1") -> FixtureGroupReader:
    """A reader whose accepted groups are ALL live-shaped — unlabelled candidates.

    This is what P10 faces against P9 as shipped. It exists so the blocked seam
    has a test rather than a paragraph.
    """
    reader = FixtureGroupReader(plan_version_id)
    reader._groups = {"g_live": _live_group("g_live", VALIDATED_SHARED_FACT)}
    reader._memberships = {"g_live": reader._memberships["g_live"]}
    reader._acceptances = (
        _acceptance("g_live", plan_version_id, ACCEPTED, None),)
    reader._stop_rule_outcomes = {}
    return reader
