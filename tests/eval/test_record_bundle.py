# tests/eval/test_record_bundle.py
"""`--record`'s second bundle: the first, plus what P9--P11 produced.

The ordering problem this exists for. `run_p1_p7` seals a bundle at the end of
P1--P7, and a sealed bundle is immutable by trigger. §8.5's contents list names
two things that do not exist yet at that moment -- the accepted groups, which are
the user's decision at P9--P11, and the corpus snapshot, which is only assembled
once the scan has finished serving listings. So `bundle.add_accepted_group` had
no caller anywhere in `src/`: there was no lawful moment to call it.

Path (B), ratified 2026-09-02: after P11, `rebuild_bundle` opens a SECOND bundle
that supersedes the first and carries the first's contents plus the snapshot, the
accepted groups and the name. The alternative was moving the seal, which means
`run_p1_p7`'s signature and a restructure of when a bundle becomes immutable;
this respects §8.2's supersede-never-overwrite instead, and `rebuild_bundle`'s
own docstring is written for exactly this -- "the caller re-adds the contents it
wants".

What it does NOT do is author an expectation. P2 SPEC's Deferred table: "the
corpus selection, the labelling, and the per-subject expected values are hand
work. P2 publishes `bundle_expectation`; it does not fill it." A harness that
labelled its own runs would score itself against its own answers. The first
bundle's hand-authored labels are carried FORWARD, because copying is not
authoring and a rebuild that dropped them would lose hand work.
"""
from __future__ import annotations

import json

import pytest

from eval_harness.bundle import (
    RecordingNameTaken, accepted_groups, add_expectation, add_extraction_output,
    add_extraction_run, add_file_entry, add_text_unit, bundle_files, expectations,
    extraction_outputs, extraction_runs, get_bundle, open_bundle, recording_for,
    seal_bundle, text_units,
)
from eval_harness.store import create_eval_schema

from evaluation import record_bundle

CONTENT_HASH = "sha256:" + "a" * 64
SNAPSHOT = {
    "corpus_form": "snapshot", "hash_algorithm": "sha256",
    "selection": {"sources": ["/corpus"]}, "listed_directories": ["/corpus"],
    "entries": [{"parent": "/corpus", "path": "/corpus/a.txt", "name": "a.txt",
                 "kind": "file", "size": 1, "mtime": 0.0, "dataless": False,
                 "content_hash": CONTENT_HASH}],
}
ACCEPTED = ({"group_id": "g1", "plan_version_id": "v1", "acceptance": "accepted"},)


def _p4_row(run_id: str) -> dict:
    return {
        "run_id": run_id, "file_id": "file-1", "content_hash": CONTENT_HASH,
        "extractor_name": "pdf", "extractor_version": "pdf-1",
        "source_type": "document", "analysis_tier": "native", "config": "{}",
        "config_fingerprint": "cfg-1", "completeness": "complete",
        "coverage": json.dumps({"units": "pages", "processed": 1, "total": 1}),
        "observation_count": 3, "started_at": "t", "finished_at": "t",
        "failure_reason": None,
    }


@pytest.fixture()
def sealed(eval_conn):
    """A bundle in exactly the shape `run_p1_p7` leaves one: full, and sealed."""
    create_eval_schema(eval_conn)
    bundle_id = open_bundle(
        eval_conn, corpus_form="snapshot", source_scan_ref="scan-1",
        pinned_plan_id=None, pinned_plan_version=None, policy_settings={"mode": "local"})
    add_file_entry(eval_conn, bundle_id, file_id="file-1", content_hash=CONTENT_HASH,
                   hash_algorithm="sha256", handling_class="ordinary",
                   payload_ref=CONTENT_HASH)
    add_extraction_run(eval_conn, bundle_id, row=_p4_row("run-1"))
    add_text_unit(eval_conn, bundle_id, row={
        "run_id": "run-1", "container_path": "/corpus/a.txt", "unit_locator": "p1",
        "text": "Columbia", "length": 8, "truncated": 0})
    add_extraction_output(eval_conn, bundle_id, content_hash=CONTENT_HASH,
                          extractor_version="pdf-1", observation_key="k1",
                          payload='{"v":1}')
    seal_bundle(eval_conn, bundle_id)
    return bundle_id


def test_the_second_bundle_carries_the_first_and_says_which_it_supersedes(
        eval_conn, sealed):
    """The link is the whole point of path (B): a reader of `bundle_manifest`
    must be able to see this is the first plus what P9--P11 produced, and not
    mistake it for a second recording of the same corpus."""
    recorded = record_bundle(eval_conn, from_bundle_id=sealed,
                             name="before-upgrade", snapshot=SNAPSHOT,
                             accepted=ACCEPTED)

    assert recorded != sealed
    assert get_bundle(eval_conn, recorded)["supersedes_bundle_id"] == sealed
    # The first is RETAINED, not replaced (§8.2), and still sealed.
    assert get_bundle(eval_conn, sealed)["sealed_at"] is not None
    assert get_bundle(eval_conn, recorded)["sealed_at"] is not None


def test_every_content_row_of_the_first_bundle_is_in_the_second(eval_conn, sealed):
    """A rebuild copies nothing on its own -- `rebuild_bundle`'s docstring is
    explicit that "the caller re-adds the contents it wants". A second bundle
    missing the extraction runs would replay as an empty corpus."""
    recorded = record_bundle(eval_conn, from_bundle_id=sealed,
                             name="before-upgrade", snapshot=SNAPSHOT,
                             accepted=ACCEPTED)

    assert [dict(r) | {"bundle_id": None} for r in bundle_files(eval_conn, recorded)] \
        == [dict(r) | {"bundle_id": None} for r in bundle_files(eval_conn, sealed)]
    assert extraction_runs(eval_conn, recorded) == extraction_runs(eval_conn, sealed)
    assert text_units(eval_conn, recorded) == text_units(eval_conn, sealed)
    assert [dict(r) | {"bundle_id": None}
            for r in extraction_outputs(eval_conn, recorded)] \
        == [dict(r) | {"bundle_id": None}
            for r in extraction_outputs(eval_conn, sealed)]


def test_the_second_bundle_carries_the_snapshot_the_accepted_groups_and_the_name(
        eval_conn, sealed):
    """The three things §8.5 names that the first bundle could not hold."""
    recorded = record_bundle(eval_conn, from_bundle_id=sealed,
                             name="before-upgrade", snapshot=SNAPSHOT,
                             accepted=ACCEPTED)

    record = recording_for(eval_conn, recorded)
    assert record["name"] == "before-upgrade"
    assert record["snapshot"] == SNAPSHOT
    assert accepted_groups(eval_conn, recorded) == list(ACCEPTED)
    # None of the three is on the first bundle, which is why the second exists.
    assert recording_for(eval_conn, sealed) is None
    assert accepted_groups(eval_conn, sealed) == []


def test_a_recording_authors_no_expectation(eval_conn, sealed):
    """Ruling B, 2026-09-02, and P2 SPEC's Deferred table. `--record` produces an
    UNLABELLED bundle. A harness that wrote its own labels would score itself
    against its own answers, and the honest thing is an empty
    `bundle_expectation` plus a sentence on screen saying so."""
    recorded = record_bundle(eval_conn, from_bundle_id=sealed,
                             name="before-upgrade", snapshot=SNAPSHOT,
                             accepted=ACCEPTED)

    assert expectations(eval_conn, recorded) == []
    # And there is no argument through which one could be passed.
    import inspect
    assert "expect" not in " ".join(
        inspect.signature(record_bundle).parameters)


def test_hand_authored_labels_on_the_first_bundle_are_carried_forward(eval_conn):
    """Copying is not authoring. A rebuild that dropped the first bundle's
    labels would lose hand work and silently turn a reference corpus back into a
    corpus snapshot."""
    create_eval_schema(eval_conn)
    first = open_bundle(eval_conn, corpus_form="snapshot", source_scan_ref="scan-1",
                        pinned_plan_id=None, pinned_plan_version=None,
                        policy_settings={})
    add_expectation(eval_conn, first, dimension="fact", subject_ref="file-1",
                    expected_value={"field": "school", "value": "Columbia"},
                    expected_outcome_kind="produced", source="hand-labelled")
    seal_bundle(eval_conn, first)

    recorded = record_bundle(eval_conn, from_bundle_id=first, name="labelled",
                             snapshot=SNAPSHOT, accepted=())

    carried = expectations(eval_conn, recorded)
    assert [(row["dimension"], row["subject_ref"], row["expected_value"],
             row["expected_outcome_kind"], row["source"]) for row in carried] == [
        ("fact", "file-1", {"field": "school", "value": "Columbia"},
         "produced", "hand-labelled")]


def test_a_name_already_taken_is_refused_and_opens_no_bundle(eval_conn, sealed):
    """Checked BEFORE the rebuild. A refusal that had already opened the second
    bundle would leave a draft nobody asked for, and a draft bundle is not
    sealed, so nothing would ever make it immutable or remove it."""
    record_bundle(eval_conn, from_bundle_id=sealed, name="before-upgrade",
                  snapshot=SNAPSHOT, accepted=ACCEPTED)
    before = eval_conn.execute(
        "SELECT count(*) AS n FROM bundle_manifest").fetchone()["n"]

    with pytest.raises(RecordingNameTaken):
        record_bundle(eval_conn, from_bundle_id=sealed, name="before-upgrade",
                      snapshot=SNAPSHOT, accepted=ACCEPTED)

    assert eval_conn.execute(
        "SELECT count(*) AS n FROM bundle_manifest").fetchone()["n"] == before


def test_a_metadata_safe_bundle_carries_no_text_units(eval_conn):
    """§8.4 requires full extracted text to stay local and §8.5 offers a
    metadata-safe form without defining it -- SPEC Open question 5, which
    `add_text_unit` refuses to answer.

    `record_bundle` carries no corpus-form guard for this and the absence is
    deliberate. The first version of this test paired one, and sabotaging that
    guard left the suite GREEN: a metadata_safe bundle cannot hold a text unit in
    the first place, so the rebuild has none to copy and the branch was
    unreachable from any state P2's writers can produce. The vacuous half is
    gone; what is pinned below is the property that makes the guard unnecessary,
    including P2's refusal itself, which is the thing actually doing the work."""
    create_eval_schema(eval_conn)
    first = open_bundle(eval_conn, corpus_form="metadata_safe",
                        source_scan_ref="scan-1", pinned_plan_id=None,
                        pinned_plan_version=None, policy_settings={})
    add_file_entry(eval_conn, first, file_id="file-1", content_hash=CONTENT_HASH,
                   hash_algorithm="sha256", handling_class=None,
                   metadata_only='{"size":1}')
    add_extraction_run(eval_conn, first, row=_p4_row("run-1"))
    seal_bundle(eval_conn, first)

    recorded = record_bundle(eval_conn, from_bundle_id=first, name="safe",
                             snapshot=SNAPSHOT, accepted=())

    assert get_bundle(eval_conn, recorded)["corpus_form"] == "metadata_safe"
    assert text_units(eval_conn, recorded) == []
    assert extraction_runs(eval_conn, recorded) == extraction_runs(eval_conn, first)
    # The refusal that makes the above true, rather than a coincidence: there was
    # never a text unit on the first bundle either, because P2 will not write one
    # into this form. Shown on a bundle that is still OPEN, so what refuses is
    # the corpus form and not the seal.
    assert text_units(eval_conn, first) == []
    still_open = open_bundle(eval_conn, corpus_form="metadata_safe",
                             source_scan_ref="scan-2", pinned_plan_id=None,
                             pinned_plan_version=None, policy_settings={})
    with pytest.raises(NotImplementedError):
        add_text_unit(eval_conn, still_open, row={
            "run_id": "run-1", "container_path": "/c/a.txt", "unit_locator": "p1",
            "text": "Columbia", "length": 8, "truncated": 0})


def test_a_bundle_that_does_not_exist_is_refused(eval_conn):
    create_eval_schema(eval_conn)

    with pytest.raises(KeyError):
        record_bundle(eval_conn, from_bundle_id="not-a-bundle", name="x",
                      snapshot=SNAPSHOT, accepted=())


# ======================================================================================
# Naming a recording, and replaying it by that name
# ======================================================================================

def test_a_recording_is_replayable_by_the_name_it_was_recorded_under(
        eval_conn, sealed):
    """`--record` takes a name and `--replay` must accept it, or the name is
    decoration. A bundle id is a uuid4: a gesture whose argument can only be
    obtained by reading it off a previous screen is a gesture nobody uses twice."""
    from evaluation import resolve_bundle

    recorded = record_bundle(eval_conn, from_bundle_id=sealed,
                             name="before-upgrade", snapshot=SNAPSHOT,
                             accepted=ACCEPTED)

    assert resolve_bundle(eval_conn, "before-upgrade") == recorded
    # The id still works. A name is an additional way in, never the only one --
    # every bundle the ordinary run has ever sealed is unnamed.
    assert resolve_bundle(eval_conn, recorded) == recorded
    assert resolve_bundle(eval_conn, sealed) == sealed


def test_neither_a_name_nor_an_id_resolves_to_nothing_rather_than_a_guess(
        eval_conn, sealed):
    """Absent means refuse. There is no nearest match and no most recent."""
    from evaluation import resolve_bundle

    record_bundle(eval_conn, from_bundle_id=sealed, name="before-upgrade",
                  snapshot=SNAPSHOT, accepted=ACCEPTED)

    assert resolve_bundle(eval_conn, "before-upgrad") is None
    assert resolve_bundle(eval_conn, "") is None
    assert resolve_bundle(eval_conn, "not-a-bundle") is None


def test_an_unsealed_bundle_does_not_resolve(eval_conn):
    """A draft is not replayable: its contents can still change under the run
    that measured them, which would make the measurement describe a corpus that
    no longer exists."""
    from evaluation import resolve_bundle

    create_eval_schema(eval_conn)
    draft = open_bundle(eval_conn, corpus_form="snapshot", source_scan_ref="s",
                        pinned_plan_id=None, pinned_plan_version=None,
                        policy_settings={})

    assert resolve_bundle(eval_conn, draft) is None


def test_the_listing_carries_the_name_so_a_person_can_read_one_off_it(
        eval_conn, sealed):
    """`--replay` with no argument prints this. An unnamed bundle -- which is
    every one the ordinary run seals -- is listed with no name rather than
    omitted, because a person looking for their recording needs to see that the
    other rows exist too."""
    from evaluation import recorded_bundles

    recorded = record_bundle(eval_conn, from_bundle_id=sealed,
                             name="before-upgrade", snapshot=SNAPSHOT,
                             accepted=ACCEPTED)

    listed = {row["bundle_id"]: row["name"] for row in recorded_bundles(eval_conn)}

    assert listed == {recorded: "before-upgrade", sealed: None}
