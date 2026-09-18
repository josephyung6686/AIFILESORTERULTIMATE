"""The fact call's offer is ordered for the QUESTION it asks, not for every open field.

`104` §18.2 gap 6 replaced a typed zone table with a measurement: for "the fields
THIS call is asking", where has this corpus already stated them? `fact_call_stage`
measured it off `pending` -- every allowlist field the file does not yet hold,
universal fields included -- while the question it then asks is `open_question`'s:
the situation's own folder levels. `duplicate_family` and `file_type` are pending on
nearly every file and are folders for none, and a corpus-wide count of where THEY
were cited (`metadata`) put the metadata envelopes ahead of the page, and
`fill_reserving_top_reading` then reserved a metadata row as the file's "strongest
reading". Under the ceiling the page was the reading dropped, with no excerpt in its
place, and the model was asked `subject` and `work_type` about a file whose text it
had not been shown.

The measurement is the same function and the same query; what changes is the set
it is asked about.
"""
from __future__ import annotations

import json

import cli
import model_facts
from facts.file_facts import DETERMINISTIC_EXTRACTOR, RULE, write_fact
from facts.states import DIRECT, VALIDATED
from facts.values import ensure_value
from model_facts import fact_call_stage
from test_a_file_that_is_never_asked_is_named import (  # noqa: E402
    CLOCK, SITUATION, _a_file, _classify, _local_routing, _read,
)

#: Six envelopes of metadata and one page. Sized so that under
#: `GROUPING_LIMITS.max_dossier_tokens` (4,000 wire bytes) the page fits beside at
#: most one envelope and the six envelopes fit without the page: whichever zone the
#: order puts first decides whether the file's own text reaches the model.
PAGE = "Course Alpha Homework 3. " + ("Solve the following problems. " * 95)
ENVELOPE = "x" * 300


def _authorities(conn):
    """The sibling fixture's authorities, with a policy row the call identity can
    read: the borrowed tests all return before a call, so their placeholder version
    never had to exist."""
    from production import (
        folder_levels_for, load_shipped_catalogue, read_packaged_library_file,
    )
    policy_version = cli.set_policy(
        conn,
        cli.Policy(policy_version=cli.UNSET_POLICY_VERSION,
                   operation_mode=cli.OPERATION_MODE,
                   consent_grants=cli.standing_consent_grants("run-1"),
                   redaction_settings={}, automatic_move_permissions={},
                   plan_version=cli.PLAN_VERSION, set_at=CLOCK),
        component_version=cli.COMPONENT_VERSION, user_id="t",
        reason="the offer is ordered for the question")
    catalogue = load_shipped_catalogue(read_packaged_library_file)
    return cli.fact_call_authorities(
        conn, routing=_local_routing(), scan_run_id="scan", corpus_file_count=3,
        policy_version=policy_version, wire_handle_key=bytes(32),
        schema="academic", folder_levels=folder_levels_for(catalogue, SITUATION),
        user_id="t", now=lambda: CLOCK)


def _keys_by_zone(conn, file_id: str, content_hash: str) -> dict[str, list[str]]:
    zones: dict[str, list[str]] = {}
    for one in model_facts.observations_for_version(
            conn, file_id=file_id, content_hash=content_hash):
        zones.setdefault(one.location.zone, []).append(one.observation_key)
    return zones


def _plant(conn, *, file_id: str, content_hash: str, field: str, value: str,
           origin: str, state: str, refs) -> None:
    refs = tuple(refs)
    write_fact(
        conn, file_id=file_id, content_hash=content_hash, field_key=field,
        value_id=ensure_value(conn, field_key=field, canonical_value=value,
                              first_evidence_ref=refs[0], origin="automatic"),
        reliability_state=state, origin=origin, evidence_refs=refs,
        cache_key=f"cache-{field}-{file_id}", active=True)


def test_the_page_is_carried_when_the_corpus_states_the_asked_field_in_it(
        conn, tmp_path):
    """SABOTAGE: measure the order off `pending` again at the offer line of
    `fact_call_stage` and the six metadata envelopes -- cited corpus-wide for a
    field this call never asks -- take the ceiling before the page."""
    cli._bootstrap(conn)

    # THE WARM CORPUS. A universal field nobody's folder is built from, stated in
    # `metadata` twice; the asked level `subject`, stated in `body` once.
    other, other_hash = _a_file(conn, tmp_path, "other.pdf", b"other")
    _classify(conn, other, other_hash, protected=False)
    _read(conn, other, other_hash,
          [("metadata", "m0", ENVELOPE), ("metadata", "m1", ENVELOPE + "1")])
    _plant(conn, file_id=other, content_hash=other_hash,
           field="duplicate_family", value="family-1",
           origin=DETERMINISTIC_EXTRACTOR, state=DIRECT,
           refs=_keys_by_zone(conn, other, other_hash)["metadata"])

    stated, stated_hash = _a_file(conn, tmp_path, "stated.pdf", b"stated")
    _classify(conn, stated, stated_hash, protected=False)
    _read(conn, stated, stated_hash, [("body", "p1", "Course Alpha syllabus")])
    _plant(conn, file_id=stated, content_hash=stated_hash,
           field="subject", value="Course Alpha", origin=RULE, state=VALIDATED,
           refs=_keys_by_zone(conn, stated, stated_hash)["body"])

    # THE FILE UNDER TEST: six envelopes and one page, all releasable.
    file_id, content_hash = _a_file(conn, tmp_path, "hw3.pdf", b"homework")
    _classify(conn, file_id, content_hash, protected=False)
    _read(conn, file_id, content_hash,
          [("metadata", f"m{index}", ENVELOPE + str(index)) for index in range(6)]
          + [("body", "p1", PAGE)])

    stage = fact_call_stage(_authorities(conn))
    stage(conn, file_id, content_hash)

    bodies = conn.execute(
        "SELECT payload FROM llm_dossier WHERE call_site = 'A_fact'").fetchall()
    assert bodies, "no site-A dossier was recorded, so this proves nothing"
    released = [item for (payload,) in bodies
                for item in json.loads(payload).get("released_evidence", ())]
    zones = sorted(item["zone"] for item in released)
    assert "body" in zones, (
        "the file's own page did not reach the model: the offer was ordered off "
        f"fields this call does not ask, and the envelopes took the ceiling. {zones}")
