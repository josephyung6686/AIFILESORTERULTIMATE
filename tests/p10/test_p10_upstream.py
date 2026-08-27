# tests/p10/test_p10_upstream.py
"""P10 Task 4 — the one module allowed to name another part's symbols.

Everything else in `src/tree_design/` reads P10 records. Concentrating the seam
here means a rename upstream breaks one module with a clear error, rather than
seven modules with seven different ones.
"""
from __future__ import annotations

import pytest

# The two membership values are P9's, and Task 1 re-exports P9's SET
# (`MEMBERSHIP_BASES`) under a P10 name — not its members. Importing them from
# their owner is the same rule the fixture follows, and it is what keeps a
# second spelling from existing.
from grouping.vocabulary import (
    CANDIDATE,
    CONTEXT_SUPPORTED,
    DIRECT_ANCHOR,
    NOT_FLAGGED,
    NO_SENSITIVITY,
    RULES,
)
from p10.p9_fixtures import FixtureGroupReader, live_shaped_reader
from scan_agent.selection import record_selection
from tree_design.upstream import (
    UpstreamUnavailable,
    accepted_groups,
    candidate_roots,
    cross_folder_moves,
    handling_class_for,
    rejected_group_ids,
    renders_as_branch,
    resolve_role_to_field,
)


def test_the_user_approved_label_is_the_acceptances_edit_then_the_groups_label():
    reader = FixtureGroupReader()
    groups = {g.group_id: g for g in accepted_groups(reader, plan_version_id="plan_1")}
    # `GroupAcceptance.user_edited_label` wins where the user set one.
    assert groups["g_phys1401"].label == "PHYS 1401 course"
    # Otherwise `Group.display_label`. P10's SPEC calls this field `label`; P9
    # has no such field, and reading one would raise AttributeError at runtime.
    assert groups["g_columbia_app"].label == "Columbia application"


def test_the_domain_is_p9s_group_category_and_p10_requests_no_second_field():
    reader = FixtureGroupReader()
    groups = {g.group_id: g for g in accepted_groups(reader, plan_version_id="plan_1")}
    assert groups["g_phys1401"].domain == "academic"
    assert groups["g_columbia_app"].domain == "college_applications"


def test_membership_basis_is_p9s_axis_and_carries_all_three_values():
    reader = FixtureGroupReader()
    groups = {g.group_id: g for g in accepted_groups(reader, plan_version_id="plan_1")}
    bases = {m.file_id: m.basis for m in groups["g_phys1401"].members}
    assert bases == {"lecture-08": DIRECT_ANCHOR, "hw-3": CONTEXT_SUPPORTED}


def test_excluded_members_are_derived_not_requested():
    reader = FixtureGroupReader()
    groups = {g.group_id: g for g in accepted_groups(reader, plan_version_id="plan_1")}
    assert groups["g_phys1401"].excluded_members == ("duke-essay",)
    assert "duke-essay" not in {m.file_id for m in groups["g_phys1401"].members}


def test_rejection_is_resolved_from_acceptance_never_from_group_state():
    """P10's SPEC derives rejected proposals from `Group.state = rejected`. That
    value cannot exist: `grouping.records.Group.__post_init__` checks `state`
    against `GROUP_STATES`, which is (candidate, supported, tentative-discovery,
    unresolved), and `grouping/vocabulary.py:20` says `rejected` is "never stored
    on a group"."""
    reader = FixtureGroupReader()
    assert rejected_group_ids(reader, plan_version_id="plan_1") == frozenset({"g_random"})
    assert "g_random" not in {
        g.group_id for g in accepted_groups(reader, plan_version_id="plan_1")
    }


def test_a_file_may_belong_to_two_accepted_groups():
    """§4.9. The tree must not force a group to a single branch to make
    membership single-valued."""
    reader = FixtureGroupReader()
    groups = accepted_groups(reader, plan_version_id="plan_1")
    homes = [g.group_id for g in groups
             if any(m.file_id == "transcript" for m in g.members)]
    assert homes == ["g_columbia_app"]
    # And the reader imposes no uniqueness that would prevent a second home.
    assert accepted_groups(reader, plan_version_id="plan_1") == groups


def test_a_tentative_discovery_group_never_becomes_a_branch():
    """§4.9: a group whose only stop rule was SR1 may be shown "only as tentative
    discovery candidates, if at all". A destination branch is the strongest
    presentation P10 has, so the answer is "not at all".

    The signal is `StopRuleOutcome.outcome`, not `Group.state`:
    `src/grouping/graph.py:334` is the only writer of `tentative-discovery` and
    it writes it onto a stop-rule record. A guard reading `group.state` would
    never fire, because `src/grouping/pipeline.py:344-347` — the only originating
    `Group` writer — sets `SUPPORTED` or `CANDIDATE` and nothing else."""
    reader = FixtureGroupReader()
    ids = {g.group_id for g in accepted_groups(reader, plan_version_id="plan_1")}
    assert "g_tentative" not in ids
    assert renders_as_branch(reader, group_id="g_tentative") is False
    # It is accepted — the exclusion is the stop rule, not the acceptance.
    assert "g_tentative" not in rejected_group_ids(reader, plan_version_id="plan_1")
    assert renders_as_branch(reader, group_id="g_phys1401") is True


def test_p10_reads_a_state_p9_actually_emits():
    """`pipeline.py:344-347` writes `SUPPORTED if meets_support_bar(...) else
    CANDIDATE`, and no other code path writes a group state at all.

    The plan recorded that `meets_support_bar` (`graph.py:262`) had no production
    caller and that `candidate` was therefore the only reachable state. It has
    one now, so the honest statement is narrower: `candidate` is what a group
    takes when the support bar is not met, and the whole fixture corpus sits in
    that state deliberately. `supported` is equally emittable and equally
    uninteresting to Tasks 1-14, because no P10 module reads `Group.state`:
    acceptance comes from `GroupAcceptance.acceptance` and renderability from
    `StopRuleOutcome.outcome`. Task 17 owns adding the `supported` shape when it
    adds the labelled one."""
    reader = FixtureGroupReader()
    assert reader.group("g_live").state == CANDIDATE
    assert {reader.group(g).state for g in reader._groups} == {CANDIDATE}


def test_an_unlabelled_live_group_is_refused_loudly_not_rendered_blank():
    """THE BLOCKED SEAM, as a test rather than a paragraph (SPEC corrections 16).

    Live P9 emits `coherence_verdict=None`, and `Group.__post_init__` then forbids
    `display_label` and `group_category`. So every group P9 writes today is
    unlabelled, and P10 cannot name a branch from one. `accepted_groups` raises
    rather than inventing a label or rendering an empty one.

    When P9 ships its labelling path this test changes to assert a label. Until
    then it is the honest record that P10's naming path has no live input."""
    reader = live_shaped_reader()
    with pytest.raises(UpstreamUnavailable) as excinfo:
        accepted_groups(reader, plan_version_id="plan_1")
    assert "carries no label" in str(excinfo.value)


def test_the_live_group_shape_matches_p9s_only_originating_writer():
    """Field-for-field against `src/grouping/pipeline.py:207-243`. If P9 changes
    what it writes, this fails here rather than somewhere downstream.

    `conflicts == ()` is asserted as the value for a seed the injected oracle
    found no conflict for. It is no longer a hardcoded `()` upstream
    (`pipeline.py:338` passes `tuple(knowledge.conflicts_for(...))`), so this
    asserts a real answer rather than a stub."""
    group = FixtureGroupReader().group("g_live")
    assert group.coherence_verdict is None
    assert group.coherence_citations == ()
    assert group.group_category is None
    assert group.display_label is None
    assert group.label_source is None
    assert group.conflicts == ()
    assert group.stop_rule_hits == ()
    assert group.dossier_id is None
    assert group.llm_response_ref is None
    assert group.validation_verdict_ref is None
    assert group.sensitivity_state == NO_SENSITIVITY
    assert group.created_by == RULES
    assert dict(group.pre_model_signals) == {"anchor_count": group.anchor_count}


def test_every_membership_carries_the_only_outlier_flag_p9_writes():
    """`pipeline.py:224` and `p8_seam.py:337` are the two `Membership` writers and
    both set `outlier_flag=NOT_FLAGGED`. A fixture flagging an outlier would test
    a branch of P10 that no P9 output can reach."""
    reader = FixtureGroupReader()
    flags = {m.outlier_flag
             for gid in reader._groups for m in reader.memberships(gid)}
    assert flags == {NOT_FLAGGED}


def test_a_role_resolves_only_to_a_live_destination_eligible_p6_field(conn):
    assert resolve_role_to_field(conn, role_ref="subject", field_ref="subject") == "subject"
    with pytest.raises(UpstreamUnavailable) as excinfo:
        resolve_role_to_field(conn, role_ref="artifact_kind", field_ref="not_a_field")
    assert "not_a_field" in str(excinfo.value)
    assert "P6" in str(excinfo.value)


def test_a_role_may_not_mint_a_field(conn):
    """§3.12: the system "should not invent new fields automatically". A template
    references fields P6 already defines; a semantic role is an organization-layer
    slot, not a new fact."""
    with pytest.raises(UpstreamUnavailable):
        resolve_role_to_field(conn, role_ref="vibe", field_ref="vibe")


def test_a_role_may_not_reach_a_field_p6_keeps_out_of_the_tree(conn):
    """§3.8: an authoring role is supporting evidence, not a folder level. P6
    marks `authored_by` not destination-eligible, and C2 fails closed on it —
    the second refusal in `resolve_role_to_field`, which the plan's printed
    tests never reached."""
    with pytest.raises(UpstreamUnavailable) as excinfo:
        resolve_role_to_field(conn, role_ref="author", field_ref="authored_by")
    assert "destination-eligible" in str(excinfo.value)


def test_the_cross_folder_permission_and_roots_come_from_p3(conn, tmp_path):
    """`conn` is the suite fixture, which has run `create_scan_schema`. A bare
    `open_database` here would raise `no such table: corpus_selections`: P1's
    open creates eight tables and P3's are not among them."""
    selection_id = record_selection(
        conn, sources=[tmp_path / "corpus"],
        candidate_roots=[tmp_path / "corpus" / "Documents"],
        cross_folder_moves=False, selected_by="jy")
    assert cross_folder_moves(conn, selection_id=selection_id) is False
    # P3 returns `list[Path]` (`src/scan_agent/selection.py:79`); P10's adapter
    # is the one place that flattens them to strings.
    assert candidate_roots(conn, selection_id=selection_id) == (
        str(tmp_path / "corpus" / "Documents"),
    )


def test_an_unclassified_file_reads_as_the_gate_outcome_and_is_never_written(conn):
    """D2: `Unreadable or unclassified` is a gate outcome, not a file fact. P7's
    store refuses to write it, so P10 must map an absent record to it for
    display without ever handing it back to P7."""
    from privacy.classification_store import ClassificationStore

    store = ClassificationStore(conn)
    assert handling_class_for(
        store, file_id="never-seen", content_hash="h") == "unreadable_unclassified"


def test_the_existing_folder_inventory_is_carried_with_p3s_three_valued_signal(
        conn, tmp_path):
    """`existing_folders` is one of Task 4's produced surfaces and the plan
    printed no test for it, so this is written against P3's real writers rather
    than a hand-built row.

    `CURATION_SIGNAL_VALUES` is THREE values. `curation_signal`
    (`src/scan_agent/inventory.py:42-53`) returns `undetermined` for every
    directory today and says why: §1.1 gives one worked case and no threshold.
    P10 carries that verbatim — rounding it to `incidental` would be P10
    authoring the threshold P3 deliberately left unauthored.
    """
    from scan_agent.inventory import CURATION_UNDETERMINED, record_directory
    from scan_agent.run import start_scan_run
    from scan_agent.traversal import ObservedDirectory
    from tree_design.upstream import existing_folders

    selection_id = record_selection(
        conn, sources=[tmp_path / "corpus"],
        candidate_roots=[tmp_path / "corpus"],
        cross_folder_moves=True, selected_by="jy")
    scan_run_id = start_scan_run(conn, selection_id)
    record_directory(conn, scan_run_id, ObservedDirectory(
        directory_path=str(tmp_path / "corpus" / "To Sort"),
        parent_directory=str(tmp_path / "corpus"),
        file_count=12, subdirectory_count=0, extension_mix={".pdf": 12},
        project_root_markers=(), applies_to="scan"))

    folders = existing_folders(conn, scan_run_id=scan_run_id)
    assert len(folders) == 1
    assert folders[0].directory_path == str(tmp_path / "corpus" / "To Sort")
    assert folders[0].parent_directory == str(tmp_path / "corpus")
    assert folders[0].file_count == 12
    assert folders[0].curation_signal == CURATION_UNDETERMINED


def test_a_preferred_value_carries_p6s_own_canonical_value_and_display_label(conn):
    """§5.4: the system "does not invent PHYS1401 ... those names emerge from
    validated facts". `preferred_value_for` is the read that carries them, and
    the plan printed no test for it either.

    The join matters and is easy to get wrong: `file_facts` carries NEITHER
    `canonical_value` NOR `display_label` as a column
    (`src/facts/schema.py:117-136`). `preferred_fact` returns the row
    `facts_for_file` built, which aliases both off `"values"`
    (`src/facts/file_facts.py:300-308`). A reader that queried `file_facts`
    directly would raise `IndexError: No item with that key` at runtime.
    """
    from facts.file_facts import RULE, write_fact
    from facts.states import VALIDATED
    from facts.values import VALUE_ORIGINS, ensure_value, set_display_label
    from tree_design.upstream import preferred_value_for

    evidence_ref = "sha256:" + "a" * 64
    value_id = ensure_value(conn, field_key="subject", canonical_value="PHYS1401",
                            first_evidence_ref=evidence_ref,
                            origin=VALUE_ORIGINS[0])
    set_display_label(conn, value_id, "PHYS 1401")
    write_fact(conn, file_id="lecture-08", content_hash="h_lecture-08",
               field_key="subject", value_id=value_id,
               reliability_state=VALIDATED, origin=RULE,
               evidence_refs=(evidence_ref,), cache_key="sha256:" + "b" * 64,
               active=True)

    settled = preferred_value_for(conn, file_id="lecture-08", field_ref="subject")
    assert settled.field_ref == "subject"
    assert settled.canonical_value == "PHYS1401"
    assert settled.display_label == "PHYS 1401"


def test_a_file_with_no_settled_value_is_unresolved_at_that_level_not_a_failure(conn):
    """§5.11: a tree "can be accepted even if some files remain unresolved".
    `None` is that answer and is not an error, so nothing downstream may treat a
    missing value as a reason to refuse the branch."""
    from tree_design.upstream import preferred_value_for

    assert preferred_value_for(conn, file_id="never-seen", field_ref="subject") is None


def test_protected_areas_reach_p10_marked_and_counted_never_opened(conn, tmp_path):
    """The product owner's standing rule: "reports, apps and system files MUST NOT
    BE MOVED OR READ OR ANYTHING SYSTEM OR SENSITIVE IN THAT SENSE." A protected
    container is MARKED AND COUNTED, NEVER OPENED — present-but-untouched, with a
    reachable explanation, never silently omitted.

    P3 honours it: `exclusion_for` checks `is_protected_container` FIRST, records
    `RULE_PROTECTED_CONTAINER` and labels the row `untouched_protected`. P10 read
    none of it — `grep protected src/tree_design/upstream.py` returned nothing —
    so a protected area was pruned by the scan and then appeared nowhere in the
    tree design. Silently omitted is the one outcome the rule forbids.

    Written against P3's real writer, so the row shape cannot drift from P3's.
    """
    from scan_agent.exclusion import (
        APPLIES_TO_SCANNED_SOURCE,
        LABEL_UNTOUCHED_PROTECTED,
        RULE_PROTECTED_CONTAINER,
        exclusion_for,
        record_exclusion,
    )
    from scan_agent.run import start_scan_run
    from tree_design.upstream import protected_areas

    selection_id = record_selection(
        conn, sources=[tmp_path / "corpus"],
        candidate_roots=[tmp_path / "corpus"],
        cross_folder_moves=True, selected_by="jy")
    scan_run_id = start_scan_run(conn, selection_id)

    bundle = tmp_path / "corpus" / "Numbers.app"
    verdict = exclusion_for(bundle, is_dir=True,
                            applies_to=APPLIES_TO_SCANNED_SOURCE)
    assert verdict.rule == RULE_PROTECTED_CONTAINER
    assert verdict.label == LABEL_UNTOUCHED_PROTECTED
    record_exclusion(conn, scan_run_id, verdict)

    # A different §1.1 rule, which is an exclusion but NOT a protected area.
    noise = exclusion_for(tmp_path / "corpus" / "node_modules", is_dir=True,
                          applies_to=APPLIES_TO_SCANNED_SOURCE)
    record_exclusion(conn, scan_run_id, noise)

    areas = protected_areas(conn, scan_run_id=scan_run_id)
    assert len(areas) == 1, "node_modules is excluded but it is not protected"
    assert areas[0].path == str(bundle)
    assert areas[0].label == LABEL_UNTOUCHED_PROTECTED
    assert areas[0].display_label == "Numbers.app"


def test_a_protected_area_is_counted_even_when_the_scan_found_nothing_else(
        conn, tmp_path):
    """"Marked and counted" is not "mentioned if convenient". An empty result is
    only correct when the scan recorded no protected container at all."""
    from scan_agent.run import start_scan_run
    from tree_design.upstream import protected_areas

    selection_id = record_selection(
        conn, sources=[tmp_path / "c"], candidate_roots=[tmp_path / "c"],
        cross_folder_moves=True, selected_by="jy")
    assert protected_areas(
        conn, scan_run_id=start_scan_run(conn, selection_id)) == ()
