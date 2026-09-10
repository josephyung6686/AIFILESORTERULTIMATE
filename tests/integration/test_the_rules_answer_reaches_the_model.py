# tests/integration/test_the_rules_answer_reaches_the_model.py
"""`104` §18.2 gap 1: what the rules settled is asked again, flagged, and reconciled.

`00`:42's amendment of 2026-09-05 is one sentence and it is the whole of what is
pinned here: the validator's hard checks are grounding and schema, and *"every other
contradiction check, INCLUDING THE PRECEDENCE OF RULE FACTS OVER MODEL FACTS, is
shown to the model as a flag with its evidence, and the model reconciles."*

Three things were doing the opposite, and each has its own tests below:

* `model_facts.pending_fields_for` took a settled field out of the question, so the
  model was never asked about it -- 16 `subject` and 17 `work_type` facts on r15's
  labelled coursework were written by a regex and shown to no model, three of them
  disagreeing with the label;
* `model_facts.build_fact_request` hardcoded `conflicts=()`, so even a file that WAS
  asked carried no flag and no evidence for one;
* `llm_harness.fact_validation` returned `REJECT CONTRADICTED_BY_STRONGER`, so the
  reconciliation the amendment gives the model was made by code.

The fourth thing pinned here is what did NOT change: the flag carries no VALUE. A
`DossierRequest` is "Reference-only. No materialised content", `llm_harness.dossier`
"authors no content", and the ratified A_fact template tells the model "You cannot
see this file's existing facts" -- so a flag names the field and points at the
reading, and the only text the model reads is what P7 released and redacted.
"""
from __future__ import annotations

import json

import pytest

import cli
from evidence_shape.schema import create_evidence_schema
from facts.domains import ActivationSignal, ActivationSignals
from facts.fields import create_fields
from facts.llm_seam import build_request
from facts.states import LLM_SUPPORTED, POSSIBLE, USER_CONFIRMED, VALIDATED
from facts.values import ensure_value
from facts.file_facts import write_fact
from llm_harness.dossier import _body
from llm_harness.records import (
    Conflict,
    EvidenceItem,
    FolderLevel,
    ReleasedEvidence,
)
from model_facts import (
    open_question,
    pending_fields_for,
    rule_conflicts,
    settled_fields_for,
)
from production import folder_levels_for, load_shipped_catalogue, read_packaged_library_file

from p9.test_p9_retrieval import _fact, _file, _hash

ACADEMIC = ActivationSignals(signals=(
    ActivationSignal(schema_id="academic", activates=lambda rows: True),))
SUBJECT_LEVEL = FolderLevel(field="subject", label="Course", requirement="required")
WORK_TYPE_LEVEL = FolderLevel(field="work_type", label="Kind", requirement="optional")
LEVELS = (SUBJECT_LEVEL, WORK_TYPE_LEVEL)
#: Any non-empty key gives a handle of the same shape; the point of the join tests is
#: that ONE key is used for both slots, which is what the live builder does.
KEY = bytes(32)


@pytest.fixture()
def corpus(conn):
    create_fields(conn)
    create_evidence_schema(conn)
    return conn


def _settled_subject(conn, tmp_path, *, value: str = "PHYS 1401") -> tuple[str, str]:
    """A file the rules already answered `subject` for. Returns (file_id, its key)."""
    file_id = _file(conn, tmp_path, "PHYS 1401 syllabus.pdf")
    key = _fact(conn, file_id, field_key="subject", value=value,
                reliability_state=VALIDATED, run_id=f"r-{file_id}")
    return file_id, key


def _request(conn, file_id: str):
    return build_request(conn, file_id=file_id, content_hash=_hash(conn, file_id),
                         activation_signals=ACADEMIC, normalizers={})


# --- the question ---------------------------------------------------------------


def test_a_settled_level_field_is_still_asked_with_its_flag(corpus, tmp_path):
    """`104` §18.2 gap 1's first half: the regex no longer ends the question.

    SABOTAGE: drop `settled` from `open_question`'s union and `subject` -- the
    REQUIRED level of the situation being run -- disappears from the vocabulary the
    model is shown, exactly as it did on r15. The file is then filed on a pattern
    match that no model ever saw, which is the drift `00`:42 was amended to stop.
    """
    file_id, _key = _settled_subject(corpus, tmp_path)
    content_hash = _hash(corpus, file_id)
    pending = pending_fields_for(corpus, file_id=file_id, content_hash=content_hash,
                                activation_signals=ACADEMIC)
    settled = settled_fields_for(corpus, file_id=file_id, content_hash=content_hash,
                                activation_signals=ACADEMIC)
    assert "subject" not in pending          # the rules answered it
    assert "subject" in settled

    vocabulary, visible = open_question(pending, LEVELS, settled)
    assert "subject" in vocabulary
    assert SUBJECT_LEVEL in visible
    # AND THE OLD ANSWER IS STILL AVAILABLE. A caller that passes no settled set asks
    # what this function asked before gap 1, which is what makes the change a
    # widening rather than a replacement.
    assert "subject" not in open_question(pending, LEVELS)[0]


def test_the_two_reads_stay_inside_the_one_allowlist(corpus, tmp_path):
    """The subset direction, which is what keeps check 1 from punishing obedience.

    Both reads are `active_field_allowlist` narrowed -- `allowed - held` and
    `allowed & rule-settled` -- so everything either one offers is inside the list
    check 1 measures the answer against. If they were two readings the question could
    offer a field `FactRequest.allowlist` does not carry, and the model would be
    rejected for answering what it was asked.

    SABOTAGE: read the settled set from anywhere but the allowlist -- the fact table
    directly, say -- and a field outside §3.5's closed vocabulary reaches
    `allowed_vocabulary`.
    """
    file_id, _key = _settled_subject(corpus, tmp_path)
    content_hash = _hash(corpus, file_id)
    pending = pending_fields_for(corpus, file_id=file_id, content_hash=content_hash,
                                activation_signals=ACADEMIC)
    settled = settled_fields_for(corpus, file_id=file_id, content_hash=content_hash,
                                activation_signals=ACADEMIC)
    request = _request(corpus, file_id)
    assert set(pending) <= set(request.allowlist)
    assert set(settled) <= set(request.allowlist)
    assert not set(pending) & set(settled)
    # AND ON THIS FILE THEY DO COVER IT, because every fact it carries is a rule's.
    # The hole the test below is about needs a `possible` fact to open.
    assert set(pending) | set(settled) == set(request.allowlist)


def test_a_field_held_only_by_a_proposal_is_asked_of_nobody_again(corpus, tmp_path):
    """`00`:298's *"proposed once"*, which the flag must not turn into "every run".

    Gap 3 writes a value the shipped library has not seen as a `possible` fact and
    `cli._print_values_to_confirm` puts it in front of the PERSON. The only thing
    that stops the next run asking the same question again is that the field is not
    pending -- and if gap 1 called it settled, it would be re-asked every run, with
    no flag beside it, because `facts.llm_seam.build_request` builds check 4's
    `existing_facts` from facts STRONGER than an LLM conclusion and a `possible` row
    is not one.

    SABOTAGE: build `settled_fields_for` off the same predicate as
    `pending_fields_for` (active and not `rejected`). The field is then asked again
    with an empty `conflicts` list -- the model reconciling a disagreement nobody
    showed it -- and the review screen grows a second proposal for a value the person
    was already asked about once.
    """
    file_id = _file(corpus, tmp_path, "unlabelled.pdf")
    _fact(corpus, file_id, field_key="subject", value="Introduction to Mechanics",
          reliability_state=POSSIBLE, run_id=f"rp-{file_id}")
    content_hash = _hash(corpus, file_id)
    pending = pending_fields_for(corpus, file_id=file_id, content_hash=content_hash,
                                activation_signals=ACADEMIC)
    settled = settled_fields_for(corpus, file_id=file_id, content_hash=content_hash,
                                activation_signals=ACADEMIC)
    assert "subject" not in pending, "a proposal holds the field against the question"
    assert "subject" not in settled, "a proposal is not what the RULES said"
    vocabulary, _visible = open_question(pending, LEVELS, settled)
    assert "subject" not in vocabulary
    # AND NOTHING WOULD HAVE FLAGGED IT ANYWAY, which is the reason for the line
    # above: check 4's input carries no row for this field.
    assert rule_conflicts(_request(corpus, file_id).existing_facts,
                          file_id=file_id, fields=("subject",)) == ()


def test_every_field_the_question_offers_carries_a_flag_or_is_open(corpus, tmp_path):
    """The invariant that ties the question to the flags, over one real file.

    Gap 1's promise is that a field the rules answered is asked WITH the rules'
    answer beside it. That is only true if the two reads agree about which fields
    those are, and they agree because `settled_fields_for` and `rule_conflicts` are
    built from one predicate.

    SABOTAGE: widen either read without the other and this fails on the first file
    that carries a model's earlier answer -- a field in the offer with no flag, or a
    flag about a field nobody was asked.
    """
    file_id, _key = _settled_subject(corpus, tmp_path)
    _fact(corpus, file_id, field_key="work_type", value="syllabus",
          reliability_state=POSSIBLE, run_id=f"rw-{file_id}")
    content_hash = _hash(corpus, file_id)
    pending = pending_fields_for(corpus, file_id=file_id, content_hash=content_hash,
                                activation_signals=ACADEMIC)
    settled = settled_fields_for(corpus, file_id=file_id, content_hash=content_hash,
                                activation_signals=ACADEMIC)
    vocabulary, _visible = open_question(pending, LEVELS, settled)
    flagged = {flag.kind for flag in rule_conflicts(
        _request(corpus, file_id).existing_facts, file_id=file_id,
        fields=vocabulary)}
    for field in vocabulary:
        assert (field in flagged) == (field in settled), (field, flagged, settled)
    assert flagged <= set(vocabulary)


def test_a_settled_field_that_builds_no_folder_is_still_not_asked(corpus, tmp_path):
    """The falsifying twin: gap 1 re-opens LEVELS, not the whole schema.

    A field the situation builds no folder from decides nothing about where the file
    goes, so re-asking it buys nothing and costs the ratified rule 11 another chance
    to void the answer. `open_question` intersects the settled half with the levels
    exactly as it does the pending half.

    SABOTAGE: union `settled` into the offer without the level intersection, and the
    vocabulary grows every universal field the file happens to carry --
    `file_type`, `creation_date`, `language` -- which is the measured failure the
    constitution-3 note in `open_question` is written against.
    """
    file_id = _file(corpus, tmp_path, "notes.pdf")
    _fact(corpus, file_id, field_key="language", value="en",
          reliability_state=VALIDATED, run_id=f"r-{file_id}")
    content_hash = _hash(corpus, file_id)
    settled = settled_fields_for(corpus, file_id=file_id, content_hash=content_hash,
                                activation_signals=ACADEMIC)
    assert "language" in settled
    vocabulary, _visible = open_question(
        pending_fields_for(corpus, file_id=file_id, content_hash=content_hash,
                           activation_signals=ACADEMIC),
        LEVELS, settled)
    assert "language" not in vocabulary


# --- the flag -------------------------------------------------------------------


def test_the_flag_names_the_field_and_points_at_the_rules_own_reading(
        corpus, tmp_path):
    """`104` §18.2 gap 1's second half: `conflicts` is BUILT, with the evidence.

    `kind` is the field key the rules settled -- a word already in the dossier's
    `allowed_vocabulary` and `field_glossary`, so the flag adds nothing the model was
    not shown -- and `conflict_id` is the observation key of the reading the rule
    read the value from.

    SABOTAGE: restore `conflicts=()` and the model is asked to reconcile a
    disagreement it is never told about, which is the state r15 measured: a regex
    decides, and the model's answer is scored against a fact nobody showed it.
    """
    file_id, key = _settled_subject(corpus, tmp_path)
    flags = rule_conflicts(_request(corpus, file_id).existing_facts,
                           file_id=file_id, fields=("subject", "work_type"))
    assert flags == (Conflict(conflict_id=key, kind="subject"),)


def test_a_flag_is_built_only_for_a_field_this_call_offers(corpus, tmp_path):
    """A flag about a field the model may not propose is a line it cannot use.

    The ratified rule 11 makes every claim a chance to void the whole answer, so a
    dossier that flags a field outside `allowed_vocabulary` spends the risk and buys
    nothing: the model cannot answer the field and cannot act on the flag.

    SABOTAGE: flag every stronger fact regardless of the question, and a file with
    six settled universal fields carries six flags into a call that asks about two.
    """
    file_id, _key = _settled_subject(corpus, tmp_path)
    _fact(corpus, file_id, field_key="language", value="en",
          reliability_state=VALIDATED, run_id=f"r2-{file_id}")
    existing = _request(corpus, file_id).existing_facts
    assert {row["field_key"] for row in existing} >= {"subject", "language"}
    flags = rule_conflicts(existing, file_id=file_id, fields=("subject",))
    assert [flag.kind for flag in flags] == ["subject"]


def test_a_users_own_answer_carries_a_flag_even_with_no_reading_behind_it(
        corpus, tmp_path):
    """§3.1 lets only a `user_confirmed` fact stand uncited, so only it needs this.

    A settled field with no flag at all would be gap 1 re-opened for the one value
    the person cared enough about to type. The id falls back to P9's own shape,
    `f"{subject}:{kind}"`, which is a spelling this product already uses
    (`grouping.p8_seam`) and which `dossier._body` keys like every other.

    SABOTAGE: build flags from `evidence_refs` alone and a confirmed value is settled
    silently -- the model is asked the field, told nothing, and its answer is then
    flagged against a fact it could not have known about.
    """
    file_id = _file(corpus, tmp_path, "confirmed.pdf")
    value_id = ensure_value(corpus, field_key="subject",
                            canonical_value="Introduction to Mechanics",
                            first_evidence_ref=None, origin="user")
    write_fact(corpus, file_id=file_id, content_hash=_hash(corpus, file_id),
               field_key="subject", value_id=value_id,
               reliability_state=USER_CONFIRMED, origin="user_correction",
               evidence_refs=(), cache_key="sha256:the-person-said-so", active=True)
    flags = rule_conflicts(_request(corpus, file_id).existing_facts,
                           file_id=file_id, fields=("subject",))
    assert flags == (Conflict(conflict_id=f"{file_id}:subject", kind="subject"),)


# --- the bytes ------------------------------------------------------------------


def _rendered(flags: tuple[Conflict, ...], key: str, value: str) -> dict:
    """The model-visible body, with one released reading and the flags beside it."""
    item = EvidenceItem(evidence_ref=key, kind="excerpt", location="page:1",
                        excerpt_span=(0, len(value)), reliability_state="direct",
                        basis="direct-anchor")
    return json.loads(_body(
        call_site=cli.A_FACT, subject_ref="file-1",
        eligibility_reason="remains_ambiguous", plan_version=None,
        policy_version="policy-1", max_dossier_tokens=4000, reduction_rung="none",
        allowed_vocabulary=("subject", "work_type"), folder_levels=(),
        evidence_items=(item,), conflicts=flags,
        released_evidence=(ReleasedEvidence(observation_key=key, address="page:1",
                                            value=value, zone="heading"),),
        prompt=cli.a_fact_prompt(), handle_key=KEY).decode("utf-8"))


def test_the_flag_and_the_reading_it_points_at_share_one_handle_in_the_bytes(
        corpus, tmp_path):
    """"...WITH ITS EVIDENCE": the join the model actually reads.

    `dossier._body` keys every `conflict_id` and every `observation_key` through the
    same `wire_handles.wire_handle` with the same run key, so a flag built on the
    rule's cited observation renders as the SAME string the released reading carries.
    That is how "the rules say X because of Y" is said without printing either an
    identifier or a value in the clear.

    SABOTAGE: build `conflict_id` as a compound -- `f"{field}:{observation_key}"`,
    say -- and the two strings stop being equal. The flag still says a field is
    settled and can no longer say from where, which is half of what the amendment
    asks for.
    """
    file_id, key = _settled_subject(corpus, tmp_path)
    flags = rule_conflicts(_request(corpus, file_id).existing_facts,
                           file_id=file_id, fields=("subject",))
    body = _rendered(flags, key, "PHYS 1401 Syllabus")
    assert len(body["conflicts"]) == 1
    assert (body["conflicts"][0]["conflict_id"]
            == body["released_evidence"][0]["observation_key"])
    assert body["conflicts"][0]["kind"] == "subject"


def test_the_flag_carries_no_value_and_no_identifier_in_the_clear(
        corpus, tmp_path):
    """The reference-only bound, which three separate things require.

    `DossierRequest` is documented "Reference-only. No materialised content";
    `llm_harness.dossier` "authors no content"; and the ratified A_fact template
    tells the model "You cannot see this file's existing facts". A flag that carried
    the rule's VALUE would break all three at once -- and it would put a `school`, an
    `instructor` or an `authored_by` into model-visible bytes through no gate, which
    is the release path's whole reason for existing.

    SABOTAGE: put the fact's canonical value into `kind`. The value then reaches a
    cloud provider without passing `privacy.gate`, unredacted and unmeasured, and no
    counter anywhere records that it left.
    """
    file_id, key = _settled_subject(corpus, tmp_path, value="Dr Helen Marchetti")
    flags = rule_conflicts(_request(corpus, file_id).existing_facts,
                           file_id=file_id, fields=("subject",))
    body = _rendered(flags, key, "a released reading with no name in it")
    rendered = json.dumps(body["conflicts"])
    assert "Dr Helen Marchetti" not in rendered
    # The raw observation key is not in the clear either: the flag's id is keyed, so
    # what a recipient sees is a handle it cannot reverse.
    assert key not in rendered
    assert body["conflicts"][0]["conflict_id"].startswith("handle:")
    # AND THE FLAG HAS EXACTLY THE TWO KEYS P9's SEAM SPELLS. A third key would be a
    # key the ratified templates say the dossier does not have.
    assert set(body["conflicts"][0]) == {"conflict_id", "kind"}


def test_the_dossier_keys_are_the_fifteen_the_templates_name(corpus, tmp_path):
    """Nothing about gap 1 adds a key, and the templates are why.

    Every ratified template carries the sentence "The dossier has these keys and no
    others", and `_ordered_body` refuses a sixteenth. The flags travel in the
    `conflicts` key those templates already list.

    SABOTAGE: carry the rule's answer in a new key and `_ordered_body` raises in the
    middle of a live run -- or, worse, the sentence in front of the model becomes
    false.
    """
    file_id, key = _settled_subject(corpus, tmp_path)
    flags = rule_conflicts(_request(corpus, file_id).existing_facts,
                           file_id=file_id, fields=("subject",))
    with_flags = set(_rendered(flags, key, "PHYS 1401 Syllabus"))
    without = set(_rendered((), key, "PHYS 1401 Syllabus"))
    assert with_flags == without
    assert "conflicts" in with_flags


# --- what the person is shown ---------------------------------------------------


def test_the_review_screen_names_the_rules_value_beside_the_models(corpus, tmp_path):
    """`104` §18.2 gap 1's last clause: the disagreement in front of a person.

    A flagged answer is written `possible` beside the rule's fact. `possible` is
    below `PROPOSAL_ELIGIBLE_STATES`, so nothing is filed under it -- and until it is
    printed, the product's answer to "the rules and the model disagree" is a row in a
    table with no line anywhere on the report.

    SABOTAGE: drop the `settled` map from `cli._print_values_to_confirm` and the
    screen shows the model's value alone, under a heading that says none of these is
    in the vocabulary this product ships. It reads as though the model had won, about
    a value that IS in the vocabulary and has not.
    """
    import io

    file_id, _key = _settled_subject(corpus, tmp_path)
    content_hash = _hash(corpus, file_id)
    model_key = _fact(corpus, file_id, field_key="subject",
                      value="Introduction to Mechanics",
                      reliability_state=POSSIBLE, run_id=f"rm-{file_id}")
    assert model_key
    out = io.StringIO()
    cli._print_values_to_confirm(corpus, out)
    printed = out.getvalue()
    assert "Introduction to Mechanics" in printed
    assert "The rules read 'PHYS 1401' for this field" in printed
    assert "still in force" in printed


def test_a_value_the_rules_never_answered_says_nothing_about_rules(
        corpus, tmp_path):
    """The falsifier for the line above: gap 3's own screen is unchanged.

    A `possible` fact on a field nothing else settled is the R-98 review path, not a
    disagreement, and telling a person the rules read something when they read
    nothing would be `84` §6's failure in the other direction.

    SABOTAGE: print the rules line unconditionally and every unseen value acquires an
    invented rival.
    """
    import io

    file_id = _file(corpus, tmp_path, "unlabelled.pdf")
    _fact(corpus, file_id, field_key="subject", value="Mechanics I",
          reliability_state=POSSIBLE, run_id=f"ru-{file_id}")
    out = io.StringIO()
    cli._print_values_to_confirm(corpus, out)
    printed = out.getvalue()
    assert "Mechanics I" in printed
    assert "The rules read" not in printed


def test_a_weaker_rival_never_reads_as_what_the_rules_said(corpus, tmp_path):
    """Only a fact STRONGER than an LLM conclusion is "what the rules said".

    §3.13's ladder is the comparison `facts.llm_seam.build_request` already applies
    to decide which facts check 4 runs against, and this screen has to name the same
    set: an `llm_supported` value from an earlier run is another model's answer, not
    the rules'.

    SABOTAGE: name every non-`possible` row as the rules' value, and the screen
    attributes one model's guess to the deterministic pass.
    """
    import io

    file_id = _file(corpus, tmp_path, "two-models.pdf")
    _fact(corpus, file_id, field_key="subject", value="Mechanics I",
          reliability_state=LLM_SUPPORTED, run_id=f"rl-{file_id}")
    _fact(corpus, file_id, field_key="subject", value="Mechanics II",
          reliability_state=POSSIBLE, run_id=f"rp-{file_id}")
    out = io.StringIO()
    cli._print_values_to_confirm(corpus, out)
    assert "The rules read" not in out.getvalue()
