### Task 24: The read surface published to neighbours

**Files:**
- Create: `src/facts/read_surface.py`
- Test: `tests/p6/test_p6_read_surface.py`

**Interfaces:**
- Consumes: `facts.fields` — `FIELD_SCOPES`, `fields_in_scope`, `get_field`, `FieldNotInCatalogue`;
  `facts.file_facts` — `facts_for_file`, `FORBIDDEN_COLUMN_SUBSTRINGS`; `facts.unresolved` —
  `unresolved_for_file`; `facts.values` — `values_in_field`; `facts.states` — `STATES`,
  `STRENGTH_ORDER`; `facts.supersede` — `fact_history`; `facts.domains` —
  `active_field_allowlist`; `facts.families` — `DUPLICATE_FAMILY_FIELD`, `VERSION_FAMILY_FIELD`;
  `facts.session` — `DOWNLOAD_SESSION_FIELD`; `facts.photo_event` — `EVENT_FIELD`;
  `evidence_shape.store.observations_by_key`; `evidence_shape.observation.Observation`;
  `evidence_shape.vocabulary` — `check`, `NotInVocabulary`.
- Produces (`read_surface.py`):
  `facts_for(conn, *, file_id, content_hash, states=None, domain=None) -> list[sqlite3.Row]`,
  `proposal_eligible(conn, *, file_id, content_hash) -> list[sqlite3.Row]`,
  `active_allowlist_for(conn, *, file_id, content_hash, activation_signals) -> tuple[str, ...]`,
  `values_with_counts(conn, *, field_key) -> list[tuple[str, int]]`,
  `evidence_chain(conn, *, fact_id) -> list[Observation]`,
  `history(conn, *, file_id, field_key) -> list[sqlite3.Row]`,
  `unresolved_for(conn, *, file_id, content_hash, field_key=None, reason=None) -> list[sqlite3.Row]`,
  `event_facts(conn, *, file_id, content_hash) -> list[sqlite3.Row]`,
  `session_facts(conn, *, file_id, content_hash) -> list[sqlite3.Row]`,
  `family_facts(conn, *, file_id, content_hash) -> list[sqlite3.Row]`,
  `is_destination_eligible(conn, *, field_key) -> bool`.

**Two additions to the skeleton's `Produces:` line, made here and named so no other author
collides with them.** The skeleton writes four of these signatures with `...` for their keywords;
those are fixed above and nothing is renamed. Beyond that:

- **`PROPOSAL_ELIGIBLE_STATES: tuple[str, ...]`** — §3.6's two exclusions, **derived** from Task 1's
  `STRENGTH_ORDER` rather than spelled. Task 1 requires that no state name appears as a string
  literal anywhere else in `facts`, and `proposal_eligible` is precisely the function that would be
  tempted to spell two. `rejected` is the one member of `STATES` that Task 1 gives no strength, so it
  is absent from `STRENGTH_ORDER` by construction; `possible` is `STRENGTH_ORDER[-1]`, the weakest
  ranked state. `STRENGTH_ORDER[:-1]` is therefore both exclusions at once, with neither named.
- **`DanglingCitation(LookupError)`** — raised when `evidence_chain` meets an `observation_key` that
  resolves to nothing. §3.1 is unconditional — *"Every fact preserves where it came from"* — so a
  citation that resolves to no observation is a broken fact, not an empty result, and returning a
  shorter list would let Done-means 30 pass by counting zero.

**Done-means:** 12, 13, and the read half of 19.

---

**What this module is, stated once, because it decides every line below.** It is the only shape P9,
P10, P11, P13, P2 and the review UI ever see. Three properties follow, and each is a test:

1. **It is a pure read.** No function here writes a row, appends an event or resolves a fact. A read
   surface that could change what it reports is not one.
2. **It returns no filing decision.** §3.14: *"A fact such as subject = BUSIB 4300 does not itself
   dictate one permanent folder path."* Task 4 asserts that from the schema with
   `FORBIDDEN_COLUMN_SUBSTRINGS`; this task asserts the same list against the **keys of every row
   this module hands out**, so a future column named `destination_node_id` fails twice.
3. **It imposes its own total order.** P4's reads are `ORDER BY rowid`, which is insertion order and
   a property of one database rather than of the corpus (skeleton, Global Constraints). Every read
   here sorts before it returns, so the same corpus extracted in a different order produces the same
   read.

**The one carve-out, named rather than left to be discovered.** `evidence_chain` returns P4
`Observation` objects verbatim, and `Observation.location.container_path` contains the word *path*.
That is not a violation and must not be "fixed": §3.2's whole point is that P6 *"preserve both the
original evidence and the conclusion built from it"*, and a container path is a locator **inside a
document** — `heading:page=1/heading=2` — not a filesystem destination. The forbidden-key assertion
therefore runs over the `sqlite3.Row` reads, which are P6's own rows, and `evidence_chain` is
asserted separately: it returns P4's frozen shape unaltered, which is the stronger claim.

**Where `read_surface` queries P6's tables directly, and why that is not a layering break.**
`evidence_chain` is addressed by `fact_id` alone — a reviewer clicking a citation has the fact id and
nothing else — and no module publishes a by-`fact_id` read. `values_with_counts` needs one aggregate
across the whole corpus. Both are `SELECT`s over `file_facts`, which is P6's own table. Everything
else composes the published functions and adds no second answer.

- [ ] **Step 1: Create `tests/p6/test_p6_read_surface.py` with the complete failing test**

```python
# tests/p6/test_p6_read_surface.py
"""Task 24 — the read surface published to neighbours.

Done-means 12 (a `possible` fact is absent from the proposal-eligible read), 13 (an
`authored_by` value is never returned as destination-eligible) and the read half of 19
(an `unresolved` row is absent from every read).
"""
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file

from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from evidence_shape.vocabulary import NotInVocabulary

from facts.cache import fact_cache_key
from facts.families import DUPLICATE_FAMILY_FIELD
from facts.fields import FieldNotInCatalogue
from facts.file_facts import FACT_ORIGINS, FORBIDDEN_COLUMN_SUBSTRINGS, write_fact
from facts.photo_event import EVENT_FIELD
from facts.read_surface import (
    DanglingCitation, PROPOSAL_ELIGIBLE_STATES, active_allowlist_for, evidence_chain,
    event_facts, facts_for, family_facts, history, is_destination_eligible,
    proposal_eligible, session_facts, unresolved_for, values_with_counts,
)
from facts.session import DOWNLOAD_SESSION_FIELD
from facts.states import STATES, STRENGTH_ORDER
from facts.supersede import supersede_fact
from facts.unresolved import ATTEMPTED_PRODUCERS, UNRESOLVED_REASONS, write_unresolved
from facts.values import VALUE_ORIGINS, ensure_value

CLOCK = "2026-08-19T12:00:00+00:00"

#: Addressed by index, never re-spelled. Task 1 owns the order:
#: user_confirmed > direct > validated > llm_supported > possible, and `rejected` has no
#: strength at all, so it is the one member of STATES absent from STRENGTH_ORDER.
USER_CONFIRMED, DIRECT, VALIDATED, LLM_SUPPORTED, POSSIBLE = STRENGTH_ORDER
REJECTED = next(s for s in STATES if s not in STRENGTH_ORDER)

#: Task 4 owns the spelling of each origin; this test owns none of them.
DETERMINISTIC, RULE = FACT_ORIGINS[0], FACT_ORIGINS[1]


def _record(conn, tmp_path, *, name, body, parent="Downloads"):
    """One P1 `files` row over real bytes, so the content hash is P1's own."""
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context=parent, mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, label,
             extractor="pdf.text", zone="metadata", source_type="text_document"):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name=extractor, extractor_version="1.0.0",
        source_type=source_type, analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name=extractor,
        extractor_version="1.0.0", source_type=source_type, raw_value=raw,
        location=Location(zone, (Segment("field", label=label),)),
        occurrence_count=1, observed_at=CLOCK, reliability="direct", run_id=run_id)
    record_observation(conn, observation)
    return observation.observation_key


def _key(content_hash):
    """§3.4's five parts. Deterministic facts carry no model and no prompt."""
    return fact_cache_key(
        content_hash=content_hash,
        extractor_version=json.dumps([["pdf.text", "1.0.0"]], separators=(",", ":")),
        analysis_tier="native", model_identifier=None, prompt_fingerprint=None)


def _fact(conn, *, file_id, content_hash, field_key, value, ref, state, origin=None):
    value_id = ensure_value(conn, field_key=field_key, canonical_value=value,
                            first_evidence_ref=ref, origin=VALUE_ORIGINS[0])
    return write_fact(
        conn, file_id=file_id, content_hash=content_hash, field_key=field_key,
        value_id=value_id, reliability_state=state,
        origin=DETERMINISTIC if origin is None else origin,
        evidence_refs=(ref,), cache_key=_key(content_hash), active=True)


@pytest.fixture()
def syllabus(p6_conn, tmp_path):
    """One file carrying §3.2's worked case, plus the four rows the negatives need:
    a `possible` fact, a `rejected` fact, an `authored_by` fact and an `unresolved` row."""
    file_id, content_hash = _record(
        p6_conn, tmp_path, name="Syllabus BUSIB 4300 Spring 2026.pdf",
        body=b"BUSIB 4300 Syllabus, Spring 2026")
    subject_ref = _observe(p6_conn, run_id="r-1", file_id=file_id,
                           content_hash=content_hash, raw="BUSIB 4300", label="title")
    author_ref = _observe(p6_conn, run_id="r-2", file_id=file_id,
                          content_hash=content_hash, raw="Jane Chen", label="Author")
    weak_ref = _observe(p6_conn, run_id="r-3", file_id=file_id,
                        content_hash=content_hash, raw="Downloads", label="parent")
    dead_ref = _observe(p6_conn, run_id="r-4", file_id=file_id,
                        content_hash=content_hash, raw="Spring 2026", label="heading")
    subject_id = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                       field_key="subject", value="BUSIB 4300", ref=subject_ref,
                       state=VALIDATED, origin=RULE)
    author_id = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                      field_key="authored_by", value="Jane Chen", ref=author_ref,
                      state=DIRECT)
    session_id = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                       field_key=DOWNLOAD_SESSION_FIELD, value="2026-07-17T09:00Z",
                       ref=weak_ref, state=POSSIBLE)
    rejected_id = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                        field_key=EVENT_FIELD, value="Graduation", ref=dead_ref,
                        state=REJECTED)
    write_unresolved(
        p6_conn, file_id=file_id, content_hash=content_hash, field_key="work_type",
        reason=UNRESOLVED_REASONS[0], attempted_producers=(ATTEMPTED_PRODUCERS[0],),
        evidence_refs=(dead_ref,), cache_key=_key(content_hash))
    return {"file_id": file_id, "content_hash": content_hash,
            "subject_ref": subject_ref, "author_ref": author_ref,
            "subject_id": subject_id, "author_id": author_id,
            "session_id": session_id, "rejected_id": rejected_id}


# ---------------------------------------------------------------- Done-means 12 and 19

def test_the_proposal_eligible_read_excludes_possible_and_rejected(syllabus, p6_conn):
    """§3.6: a weak output "may remain a possible clue for review; it must not quietly
    become a folder proposal or an asserted file property". Both negatives at once —
    they are the two §3.6 turns on."""
    rows = proposal_eligible(p6_conn, file_id=syllabus["file_id"],
                             content_hash=syllabus["content_hash"])
    states = {row["reliability_state"] for row in rows}
    assert POSSIBLE not in states
    assert REJECTED not in states
    assert {row["field_key"] for row in rows} == {"subject", "authored_by"}


def test_proposal_eligible_states_are_derived_and_never_spelled(syllabus):
    """The exclusions come from Task 1's published order, so P6 has one spelling of a
    state name and `read_surface` is not a second."""
    assert PROPOSAL_ELIGIBLE_STATES == STRENGTH_ORDER[:-1]
    assert POSSIBLE not in PROPOSAL_ELIGIBLE_STATES
    assert REJECTED not in PROPOSAL_ELIGIBLE_STATES
    assert set(PROPOSAL_ELIGIBLE_STATES) < set(STATES)


def test_an_unresolved_row_is_absent_from_every_fact_read(syllabus, p6_conn):
    """Done-means 19's read half. `unresolved` is not a weak fact: it appears in no fact
    read at all, including the proposal-eligible one, and `work_type` — the field it
    names — comes back from none of them."""
    args = dict(file_id=syllabus["file_id"], content_hash=syllabus["content_hash"])
    reads = (facts_for(p6_conn, **args),
             facts_for(p6_conn, states=STATES, **args),
             proposal_eligible(p6_conn, **args),
             event_facts(p6_conn, **args),
             session_facts(p6_conn, **args),
             family_facts(p6_conn, **args))
    for rows in reads:
        assert "work_type" not in {row["field_key"] for row in rows}
    assert [row["field_key"] for row in unresolved_for(p6_conn, **args)] == ["work_type"]


def test_the_unresolved_read_carries_no_value_and_no_state(syllabus, p6_conn):
    """It is an abstention, not a `possible`. A reader that could read a state off it
    would eventually treat it as one."""
    row = unresolved_for(p6_conn, file_id=syllabus["file_id"],
                         content_hash=syllabus["content_hash"])[0]
    assert "value_id" not in row.keys()
    assert "reliability_state" not in row.keys()


def test_unresolved_for_filters_by_field_and_by_reason(syllabus, p6_conn):
    args = dict(file_id=syllabus["file_id"], content_hash=syllabus["content_hash"])
    assert len(unresolved_for(p6_conn, field_key="work_type", **args)) == 1
    assert unresolved_for(p6_conn, field_key="subject", **args) == []
    assert len(unresolved_for(p6_conn, reason=UNRESOLVED_REASONS[0], **args)) == 1
    assert unresolved_for(p6_conn, reason=UNRESOLVED_REASONS[1], **args) == []


# ------------------------------------------------------------------- Done-means 13, §3.8

def test_an_authored_by_value_is_never_returned_as_destination_eligible(p6_conn):
    """§3.8: "It should avoid using authorship or creator identity as a destination
    dimension." Done-means 13, asserted from the read rather than from the catalogue."""
    assert is_destination_eligible(p6_conn, field_key="authored_by") is False


def test_every_role_field_is_refused_as_a_destination(p6_conn):
    """§3.8 names four — "authored_by and target_school, or our_firm and client" — and the
    rule binds all four, not only the one Done-means 13 spells."""
    for field_key in ("authored_by", "target_school", "our_firm", "client"):
        assert is_destination_eligible(p6_conn, field_key=field_key) is False


def test_a_destination_question_about_an_unknown_field_raises(p6_conn):
    """Silently answering False for a field that does not exist would let a typo read as
    a policy. §3.12 forbids inventing fields; this read does not invent one either."""
    with pytest.raises(FieldNotInCatalogue):
        is_destination_eligible(p6_conn, field_key="destination")


# --------------------------------------------------------------------- the evidence walk

def test_evidence_chain_walks_a_fact_back_to_its_p4_observations(syllabus, p6_conn):
    """Done-means 30's read half: every step resolves, and what comes back is P4's frozen
    shape with its raw value unchanged (§3.2)."""
    chain = evidence_chain(p6_conn, fact_id=syllabus["subject_id"])
    assert [o.observation_key for o in chain] == [syllabus["subject_ref"]]
    assert chain[0].raw_value == "BUSIB 4300"
    assert isinstance(chain[0], Observation)


def test_evidence_chain_returns_p4s_shape_unaltered(syllabus, p6_conn):
    """The carve-out, asserted rather than assumed: this read hands back P4 objects, so
    `container_path` is a locator inside the document and not a P6 column."""
    observation = evidence_chain(p6_conn, fact_id=syllabus["subject_id"])[0]
    assert observation.location.container_path[0].label == "title"
    assert observation.location.zone == "metadata"


def test_a_citation_that_resolves_to_nothing_raises(syllabus, p6_conn):
    """§3.1: "Every fact preserves where it came from." A fact whose citation is gone is
    broken; returning an empty list would let Done-means 30 pass by counting zero."""
    p6_conn.execute("DELETE FROM evidence WHERE observation_key = ?",
                    (syllabus["subject_ref"],))
    with pytest.raises(DanglingCitation):
        evidence_chain(p6_conn, fact_id=syllabus["subject_id"])


def test_evidence_chain_on_an_unknown_fact_raises(p6_conn):
    with pytest.raises(LookupError):
        evidence_chain(p6_conn, fact_id="fact-that-was-never-written")


# -------------------------------------------------------------------- §5.5's branch counts

def test_values_with_counts_supports_the_branch_preview(p6_conn, tmp_path):
    """§5.5: "The interface can state that Option A would create three schools, five terms,
    and twelve course branches". The read has to answer that before the user commits, so
    it counts FILES per value, which is what a branch will hold."""
    seen = []
    for index, (name, subject) in enumerate((
            ("a.pdf", "BUSIB 4300"), ("b.pdf", "BUSIB 4300"),
            ("c.pdf", "BUSIB 4300"), ("d.pdf", "ECON 2100"),
            ("e.pdf", "STAT 1001"))):
        file_id, content_hash = _record(p6_conn, tmp_path, name=name,
                                        body=f"{subject} number {index}".encode())
        ref = _observe(p6_conn, run_id=f"run-{index}", file_id=file_id,
                       content_hash=content_hash, raw=subject, label="title")
        _fact(p6_conn, file_id=file_id, content_hash=content_hash, field_key="subject",
              value=subject, ref=ref, state=VALIDATED, origin=RULE)
        seen.append(file_id)
    assert values_with_counts(p6_conn, field_key="subject") == [
        ("BUSIB 4300", 3), ("ECON 2100", 1), ("STAT 1001", 1)]


def test_branch_counts_are_totally_ordered_so_the_preview_is_stable(p6_conn, tmp_path):
    """Count descending, then canonical value ascending. Ties are broken by the value and
    never by insertion order, which is a property of one database and not of the corpus."""
    for index, (name, subject) in enumerate((
            ("z.pdf", "ZOOL 1000"), ("a.pdf", "ANTH 1000"))):
        file_id, content_hash = _record(p6_conn, tmp_path, name=name,
                                        body=f"{subject}".encode())
        ref = _observe(p6_conn, run_id=f"tie-{index}", file_id=file_id,
                       content_hash=content_hash, raw=subject, label="title")
        _fact(p6_conn, file_id=file_id, content_hash=content_hash, field_key="subject",
              value=subject, ref=ref, state=VALIDATED, origin=RULE)
    assert values_with_counts(p6_conn, field_key="subject") == [
        ("ANTH 1000", 1), ("ZOOL 1000", 1)]


def test_a_value_no_active_fact_points_at_is_not_a_branch(syllabus, p6_conn):
    """§3.12 lets a value auto-create on first sight. A value with no file behind it would
    preview an empty folder, so it is not a branch — the count read shows what will be
    filed, not what has ever been named."""
    ensure_value(p6_conn, field_key="subject", canonical_value="HIST 9999",
                 first_evidence_ref=syllabus["subject_ref"], origin=VALUE_ORIGINS[0])
    assert "HIST 9999" not in dict(values_with_counts(p6_conn, field_key="subject"))


def test_counts_for_an_unknown_field_raise(p6_conn):
    with pytest.raises(FieldNotInCatalogue):
        values_with_counts(p6_conn, field_key="folder")


# ------------------------------------------------------------------- filtering and history

def test_facts_for_filters_by_state(syllabus, p6_conn):
    rows = facts_for(p6_conn, file_id=syllabus["file_id"],
                     content_hash=syllabus["content_hash"], states=(POSSIBLE,))
    assert [row["field_key"] for row in rows] == [DOWNLOAD_SESSION_FIELD]


def test_facts_for_filters_by_domain(syllabus, p6_conn):
    """`domain` is a field scope. §3.11 puts `subject` in Academic; the role fields and
    `download_session` are universal, so the academic read returns one row."""
    rows = facts_for(p6_conn, file_id=syllabus["file_id"],
                     content_hash=syllabus["content_hash"], domain="academic")
    assert [row["field_key"] for row in rows] == ["subject"]


def test_an_unknown_state_or_domain_raises_rather_than_returning_nothing(syllabus, p6_conn):
    """An empty list for a misspelled filter is how a caller concludes there are no facts.
    P4's `check` is the project's one vocabulary gate and this read uses it."""
    args = dict(file_id=syllabus["file_id"], content_hash=syllabus["content_hash"])
    with pytest.raises(NotInVocabulary):
        facts_for(p6_conn, states=("LLM-supported",), **args)
    with pytest.raises(NotInVocabulary):
        facts_for(p6_conn, domain="Academic", **args)


def test_the_unfiltered_read_still_shows_rejected_facts(syllabus, p6_conn):
    """§3.13 makes `rejected` an exclusion from proposals, not from the record. The review
    UI must be able to see what was rejected and why, or §8.5's "Did it abstain when
    evidence was absent?" is unanswerable from the outside."""
    rows = facts_for(p6_conn, file_id=syllabus["file_id"],
                     content_hash=syllabus["content_hash"])
    assert REJECTED in {row["reliability_state"] for row in rows}


def test_history_returns_superseded_rows(syllabus, p6_conn, tmp_path):
    """§8.2's worked example arriving as the ordinary path: the old row stays readable."""
    ref = _observe(p6_conn, run_id="r-ocr", file_id=syllabus["file_id"],
                   content_hash=syllabus["content_hash"], raw="BUSIB 4300",
                   label="heading")
    newer = _fact(p6_conn, file_id=syllabus["file_id"],
                  content_hash=syllabus["content_hash"], field_key="subject",
                  value="BUSIB 4300 Business Analytics", ref=ref, state=VALIDATED,
                  origin=RULE)
    supersede_fact(p6_conn, old_fact_id=syllabus["subject_id"], new_fact_id=newer,
                   reason="a later pass read the heading")
    rows = history(p6_conn, file_id=syllabus["file_id"], field_key="subject")
    assert [row["fact_id"] for row in rows] == [syllabus["subject_id"], newer]


def test_the_three_handed_families_have_their_own_reads(syllabus, p6_conn):
    args = dict(file_id=syllabus["file_id"], content_hash=syllabus["content_hash"])
    assert [row["field_key"] for row in session_facts(p6_conn, **args)] == [
        DOWNLOAD_SESSION_FIELD]
    assert [row["field_key"] for row in event_facts(p6_conn, **args)] == [EVENT_FIELD]
    assert family_facts(p6_conn, **args) == []


def test_the_active_allowlist_is_the_domain_modules_answer(syllabus, p6_conn):
    """§3.12: "it should not invent new fields automatically". The allowlist read adds no
    field of its own — it republishes Task 13's under the name neighbours use."""
    def signals(conn, *, file_id, content_hash):
        return frozenset({"academic"})

    allowlist = active_allowlist_for(
        p6_conn, file_id=syllabus["file_id"], content_hash=syllabus["content_hash"],
        activation_signals=signals)
    assert "subject" in allowlist
    assert "course" not in allowlist


# ----------------------------------------------------------- the negative contract, §3.14

def test_no_read_returns_a_path_a_destination_a_folder_or_a_group(syllabus, p6_conn):
    """§3.14: "A fact such as subject = BUSIB 4300 does not itself dictate one permanent
    folder path." Task 4 asserts this from `PRAGMA table_info`; this asserts it from the
    shapes that leave the package, so a column that reached a neighbour would fail twice."""
    args = dict(file_id=syllabus["file_id"], content_hash=syllabus["content_hash"])
    reads = (facts_for(p6_conn, **args),
             proposal_eligible(p6_conn, **args),
             unresolved_for(p6_conn, **args),
             event_facts(p6_conn, **args),
             session_facts(p6_conn, **args),
             family_facts(p6_conn, **args),
             history(p6_conn, file_id=syllabus["file_id"], field_key="subject"))
    assert all(rows for rows in reads[:2])
    for rows in reads:
        for row in rows:
            for key in row.keys():
                for forbidden in FORBIDDEN_COLUMN_SUBSTRINGS:
                    assert forbidden not in key.lower(), (key, forbidden)


def test_the_read_surface_writes_nothing(syllabus, p6_conn):
    """A read that could change what it reports is not a read. Asserted over the whole
    module by comparing every P6 table before and after every read runs."""
    def snapshot():
        return {table: p6_conn.execute(
                    f"SELECT count(*) FROM {table}").fetchone()[0]
                for table in ("fields", "values", "file_facts", "unresolved")}

    before = snapshot()
    args = dict(file_id=syllabus["file_id"], content_hash=syllabus["content_hash"])
    facts_for(p6_conn, **args)
    proposal_eligible(p6_conn, **args)
    unresolved_for(p6_conn, **args)
    event_facts(p6_conn, **args)
    session_facts(p6_conn, **args)
    family_facts(p6_conn, **args)
    history(p6_conn, file_id=syllabus["file_id"], field_key="subject")
    evidence_chain(p6_conn, fact_id=syllabus["subject_id"])
    values_with_counts(p6_conn, field_key="subject")
    is_destination_eligible(p6_conn, field_key="authored_by")
    assert snapshot() == before


def test_no_read_accepts_a_group(p6_conn):
    """§4.3 and §4.1: the graph "does not automatically copy those missing facts onto
    sparse files". A read that took a group id would be the place that started."""
    import inspect

    from facts import read_surface

    for name, member in vars(read_surface).items():
        if name.startswith("_") or not callable(member):
            continue
        if getattr(member, "__module__", None) != read_surface.__name__:
            continue
        parameters = set(inspect.signature(member).parameters)
        assert not parameters & {"group_id", "group", "group_ids", "members",
                                 "member_ids", "anchor", "anchor_file_id"}, name
```

- [ ] **Step 2: Run the test and watch it fail for the one right reason**

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6/test_p6_read_surface.py -x -q
```

Expected: **collection error**, `ModuleNotFoundError: No module named 'facts.read_surface'`. Not one
test runs. Every other import in the file resolves, because Tasks 1–23 are green when this task
starts — so a different missing name here means a sibling task changed a published signature and
that is the thing to fix first, not this file.

- [ ] **Step 3: Create `src/facts/read_surface.py` with the complete implementation**

```python
# src/facts/read_surface.py
"""P6's read surface — the only shape P9, P10, P11, P13, P2 and the review UI see.

Three properties hold across every function here, and each of them is a test in
`tests/p6/test_p6_read_surface.py`:

* it is a pure read — nothing here writes a row, appends an event or resolves a fact;
* it returns no filing decision — §3.14: "A fact such as subject = BUSIB 4300 does not
  itself dictate one permanent folder path";
* it imposes its own total order — P4's reads are insertion-ordered, which is a property
  of one database and not of the corpus, so every read here sorts before it returns.

`evidence_chain` is the one function that returns something other than P6's own rows: it
returns P4 `Observation` objects verbatim, because §3.2 requires the product to "preserve
both the original evidence and the conclusion built from it".
"""
from __future__ import annotations

import json
import sqlite3
from typing import Iterable, Sequence

from evidence_shape.observation import Observation
from evidence_shape.store import observations_by_key
from evidence_shape.vocabulary import check

from facts.domains import active_field_allowlist
from facts.families import DUPLICATE_FAMILY_FIELD, VERSION_FAMILY_FIELD
from facts.fields import FIELD_SCOPES, fields_in_scope, get_field
from facts.file_facts import facts_for_file
from facts.photo_event import EVENT_FIELD
from facts.session import DOWNLOAD_SESSION_FIELD
from facts.states import STATES, STRENGTH_ORDER
from facts.supersede import fact_history
from facts.unresolved import unresolved_for_file
from facts.values import values_in_field

#: §3.6's two exclusions, DERIVED rather than spelled. `rejected` is the one member of
#: `STATES` that Task 1 gives no strength, so it is absent from `STRENGTH_ORDER`;
#: `possible` is the weakest ranked state, so it is the last member. Slicing the last one
#: off therefore drops both, and no state name is written down in this module.
PROPOSAL_ELIGIBLE_STATES: tuple[str, ...] = STRENGTH_ORDER[:-1]


class DanglingCitation(LookupError):
    """A fact cites an `observation_key` that resolves to no observation.

    §3.1: "Every fact preserves where it came from." A citation that resolves to nothing
    is a broken fact, not an empty result.
    """


def _field_index(conn: sqlite3.Connection) -> dict[str, sqlite3.Row]:
    """`field_key` -> its catalogue row, built from Task 2's published scope read only."""
    index: dict[str, sqlite3.Row] = {}
    for scope in FIELD_SCOPES:
        for row in fields_in_scope(conn, scope):
            index[row["field_key"]] = row
    return index


def _ordered(rows: Iterable[sqlite3.Row]) -> list[sqlite3.Row]:
    """P6's own total order. Never SQLite's, never P4's insertion order."""
    return sorted(rows, key=lambda row: (row["field_key"], str(row["value_id"]),
                                         row["fact_id"]))


def _in_fields(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
               field_keys: Sequence[str]) -> list[sqlite3.Row]:
    wanted = frozenset(field_keys)
    return _ordered(row for row in facts_for_file(conn, file_id, content_hash)
                    if row["field_key"] in wanted)


def facts_for(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
              states: Iterable[str] | None = None,
              domain: str | None = None) -> list[sqlite3.Row]:
    """Every fact for one file version, optionally narrowed by state or by field scope.

    Unfiltered, this includes `rejected` facts: §3.13 makes `rejected` an exclusion from
    proposals, not from the record, and the review UI has to be able to see what was
    rejected. `proposal_eligible` is the read that excludes it.
    """
    if states is not None:
        states = tuple(states)
        for state in states:
            check(state, STATES, name="reliability_state")
        allowed: frozenset[str] | None = frozenset(states)
    else:
        allowed = None
    if domain is not None:
        check(domain, FIELD_SCOPES, name="scope")
        index = _field_index(conn)
    selected: list[sqlite3.Row] = []
    for row in facts_for_file(conn, file_id, content_hash):
        if allowed is not None and row["reliability_state"] not in allowed:
            continue
        if domain is not None:
            field = index.get(row["field_key"])
            if field is None or field["scope"] != domain:
                continue
        selected.append(row)
    return _ordered(selected)


def proposal_eligible(conn: sqlite3.Connection, *, file_id: str,
                      content_hash: str) -> list[sqlite3.Row]:
    """The facts a folder proposal may rest on.

    §3.6: a weak model output "may remain a possible clue for review; it must not quietly
    become a folder proposal or an asserted file property". `unresolved` rows are in a
    different table and are therefore absent by construction rather than by a filter.
    """
    return facts_for(conn, file_id=file_id, content_hash=content_hash,
                     states=PROPOSAL_ELIGIBLE_STATES)


def active_allowlist_for(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                         activation_signals) -> tuple[str, ...]:
    """§3.11's active field allowlist, republished under the name neighbours use. The
    signals are injected and this module adds no field of its own (§3.12)."""
    return active_field_allowlist(conn, file_id=file_id, content_hash=content_hash,
                                  activation_signals=activation_signals)


def values_with_counts(conn: sqlite3.Connection, *,
                       field_key: str) -> list[tuple[str, int]]:
    """§5.5's branch preview: "The interface can state that Option A would create three
    schools, five terms, and twelve course branches."

    Counts FILES per value, because that is what a branch will hold, and omits values no
    active fact points at, because those would preview an empty folder. Ordered by count
    descending then canonical value ascending, so the preview is stable across runs.
    """
    get_field(conn, field_key)
    counts: dict[str, int] = {}
    for row in conn.execute(
            "SELECT value_id, COUNT(DISTINCT file_id) FROM file_facts "
            "WHERE active = 1 GROUP BY value_id"):
        counts[row[0]] = row[1]
    branches = [(row["canonical_value"], counts.get(row["value_id"], 0))
                for row in values_in_field(conn, field_key)]
    return sorted(((value, count) for value, count in branches if count),
                  key=lambda pair: (-pair[1], pair[0]))


def evidence_chain(conn: sqlite3.Connection, *, fact_id: str) -> list[Observation]:
    """One fact walked back to the P4 observations it cites.

    Every entry in `evidence_refs[]` is an `observation_key` (M14), which is
    content-addressed and excludes `extractor_version` by construction — so a citation
    recorded before an extractor upgrade still resolves after one (§8.7).
    """
    row = conn.execute("SELECT evidence_refs FROM file_facts WHERE fact_id = ?",
                       (fact_id,)).fetchone()
    if row is None:
        raise LookupError(f"no fact {fact_id!r}")
    chain: list[Observation] = []
    for key in json.loads(row[0]):
        found = observations_by_key(conn, key)
        if not found:
            raise DanglingCitation(
                f"fact {fact_id!r} cites {key!r}, which resolves to no observation")
        chain.extend(sorted(found, key=lambda o: o.observation_id))
    return chain


def history(conn: sqlite3.Connection, *, file_id: str,
            field_key: str) -> list[sqlite3.Row]:
    """Oldest first, superseded rows included. §8.2 keeps them readable."""
    get_field(conn, field_key)
    return fact_history(conn, file_id=file_id, field_key=field_key)


def unresolved_for(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                   field_key: str | None = None,
                   reason: str | None = None) -> list[sqlite3.Row]:
    """The abstentions, which appear in no fact read. §8.5 asks "Did it abstain when
    evidence was absent?" and an absent row cannot answer it."""
    return unresolved_for_file(conn, file_id, content_hash, field_key=field_key,
                               reason=reason)


def event_facts(conn: sqlite3.Connection, *, file_id: str,
                content_hash: str) -> list[sqlite3.Row]:
    """G7's photo event — a P9 seed, never a placement."""
    return _in_fields(conn, file_id=file_id, content_hash=content_hash,
                      field_keys=(EVENT_FIELD,))


def session_facts(conn: sqlite3.Connection, *, file_id: str,
                  content_hash: str) -> list[sqlite3.Row]:
    """G6's bounded download session. §3.9 makes it "not a basis for automatic semantic
    propagation", so it never exceeds `possible` and never reaches `proposal_eligible`."""
    return _in_fields(conn, file_id=file_id, content_hash=content_hash,
                      field_keys=(DOWNLOAD_SESSION_FIELD,))


def family_facts(conn: sqlite3.Connection, *, file_id: str,
                 content_hash: str) -> list[sqlite3.Row]:
    """G5's duplicate family and version family."""
    return _in_fields(conn, file_id=file_id, content_hash=content_hash,
                      field_keys=(DUPLICATE_FAMILY_FIELD, VERSION_FAMILY_FIELD))


def is_destination_eligible(conn: sqlite3.Connection, *, field_key: str) -> bool:
    """§3.8: the product "should avoid using authorship or creator identity as a
    destination dimension". Raises `FieldNotInCatalogue` on an unknown field rather than
    answering False, so a typo cannot read as a policy."""
    return bool(get_field(conn, field_key)["destination_eligible"])
```

- [ ] **Step 4: Run the test again and watch it pass**

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6/test_p6_read_surface.py -q
```

Expected: **26 passed**. Then the whole part, to prove no sibling read regressed:

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6 -q
```

- [ ] **Step 5: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/facts/read_surface.py tests/p6/test_p6_read_surface.py && \
git commit -m "feat(P6): the read surface published to neighbours — two exclusions derived, never spelled"
```

---
### Task 25: The no-invention guard — every open question and every deferred row held open

**Files:**
- Test only: `tests/p6/test_p6_no_invention.py`
- Creates and modifies **no** source file. If this task has to change a line under `src/facts/` to go
  green, the line it changes is the finding and the change belongs to whichever task owns that module.

**Interfaces:**
- Consumes: every module in `facts`, by runtime introspection of `vars(module)` and of each module's
  compiled code object; `facts.fields` — `FIELD_ROWS`, `FieldRow`, `FIELD_SCOPES`, `UNIVERSAL_FIELDS`,
  `DOMAIN_FIELDS`, `fields_in_scope`, `get_field`, `FieldNotInCatalogue`; `facts.states` — `STATES`,
  `STRENGTH_ORDER`, `is_stronger`; `facts.unresolved` — `UNRESOLVED_REASONS`; `facts.values` —
  `ensure_value`, `VALUE_ORIGINS`; `facts.authorship.SUBSYSTEM`; `facts.evidence` —
  `observations_for_version`; `evidence_shape.vocabulary.SOURCE_TYPES`;
  `planning/deferred-catalogues/01-tool-producer-strings.json` **as a file the test reads**.
- Produces: nothing.

**Done-means:** none numbered. It is what makes the Deferred table true.

---

**Why every guard here is runtime and not textual.** A source-text search matches comments and
docstrings, and scanning text for a token has produced a **false result nine times on this project**
— most recently P5's PLAN Task 20, where a `grep` for a threshold matched the sentence explaining
that there was no threshold. So the guards below use two runtime tools and nothing else:

| Tool | What it can see | What it is used for here |
|---|---|---|
| `vars(module)` walked recursively | every **module-level binding** and everything reachable inside it — tuples, mappings, frozen dataclasses | thresholds, weights, resolutions, aspect ratios, session windows, GPS radii, usable-fact counts, compiled regexes, gazetteers, producer-string lists |
| the module's **compiled code object** (`__loader__.get_code(...)`, recursed through nested code objects) | every literal the compiler kept, **including literals inside function bodies** | catalogue 01's producer strings, and the single home of `subsystem = "P6"` |

The second tool matters because the namespace walk alone cannot see a literal buried in a function
body — and that is exactly where a copied catalogue would end up. A comment can never reach
`co_consts`; a docstring reaches it only as the whole docstring, so an **equality** test against a
short token like `"P6"` or `"python-docx"` cannot be satisfied by prose.

**One exemption, and it is by identity, which is the point.** A `facts` module that does
`from evidence_shape.vocabulary import SIGNAL_TIERS` binds a tuple of integers at module level. That
is a re-export of P4's published vocabulary, not a P6 invention, and the guard exempts it **because
`id(value)` matches an object P4 published** — so a re-export passes and a hand-typed copy of the
same numbers fails. That is Task 1's rule (*"`STATES` **is** P4's tuple rather than a copy"*) applied
to every upstream vocabulary at once. A **contiguous slice** of a published upstream tuple is exempt
on the same grounds: Task 16 reads §2.6's screenshot band as `SIGNAL_TIERS[-1:]` precisely so it does
not have to spell a `3`, and a guard that punished that would push the author back to the literal.

**Two guards INVERT here, and the inversion is the whole reason this task is written last.** OQ4 and
OQ11 are closed. A test asserting they are open passes today and **fails the day the decision is
applied — which is the day this plan is executed.** So they assert the closure. Their residues stay
open by name, and OQ11's residue is named in its own test rather than left implied.

**Contradiction found and reported, not resolved.** P7's SPEC, Contract-in, line 90, says in bold:
*"P6 must accept `sensitivity` as a first-class universal field"*. §3.12 names `sensitivity` in the
design's own field list — *"subject, purpose, target university, project, event, or sensitivity"* —
and §3.11 spells it `sensitivity status`. Against that, D2 makes P7's `ClassificationRecord`
authoritative, round 1's F-2 found the P6 field has **no producer**, and NEEDS-JOSEPH **C5** holds
the question of whether the row survives. The authoring brief's instruction is unambiguous: *"Create
no such row either way."* This task therefore asserts **today's** state — no row, under either
spelling — and its test says in its own body that it settles nothing. If Joseph keeps the row, this
test is where the decision lands and the flip is one line here plus one row in Task 2's catalogue.

- [ ] **Step 1: Create `tests/p6/test_p6_no_invention.py` with the complete failing test**

```python
# tests/p6/test_p6_no_invention.py
"""Task 25 — the no-invention guard.

Every threshold, weight, gazetteer, regex catalogue, producer string, resolution, aspect
ratio, session window, GPS radius and usable-fact count in P6 is injected by the caller
with no default. Every still-open question in P6's SPEC stays open. The two that closed
(OQ4, OQ11) have their guards INVERTED, so this file fails if the closure is ever quietly
un-applied.

Nothing here reads source text. See the two-tool table in this task's plan section.
"""
import dataclasses
import importlib
import inspect
import json
import os
import pkgutil
import re
import subprocess
import sys
import types
from collections.abc import Mapping
from pathlib import Path

import pytest

from evidence_shape.vocabulary import SOURCE_TYPES

import facts
from facts.authorship import SUBSYSTEM
from facts.fields import (
    DOMAIN_FIELDS, FIELD_ROWS, FIELD_SCOPES, FieldNotInCatalogue, FieldRow,
    UNIVERSAL_FIELDS, fields_in_scope, get_field,
)
from facts.states import STATES, STRENGTH_ORDER, is_stronger
from facts.unresolved import UNRESOLVED_REASONS
from facts.values import VALUE_ORIGINS, ensure_value

REPO = Path(__file__).resolve().parents[2]
CATALOGUE_01 = REPO / "planning" / "deferred-catalogues" / "01-tool-producer-strings.json"

#: Task 2 owns the spelling of each scope; this file re-spells none of them.
UNIVERSAL, ACADEMIC, COLLEGE_APPLICATIONS, RESEARCH, FINANCE, PHOTOS, CODE = FIELD_SCOPES

#: The file layout the plan declares, and nothing else. A `catalogues.py` appearing here
#: is how catalogue 01 would arrive as a module-level constant while satisfying the letter
#: of every other guard in this file, so the module set itself is asserted.
DECLARED_MODULES = frozenset({
    "authorship", "budgets", "cache", "dates", "direct", "discount", "domains",
    "evidence", "facets", "families", "fields", "file_facts", "learning", "llm_seam",
    "photo_event", "plan_versions", "read_surface", "resolver", "rules", "schema",
    "session", "states", "stage_output", "supersede", "unresolved", "usable", "values",
    "vocabulary",
})

#: Every module-level COLLECTION P6 is allowed to publish, with the task that owns it.
#: A plain string constant needs no entry — a field key is not a catalogue. A collection
#: does, because a gazetteer, a producer-string list, a zone-weight map and a regex
#: catalogue are all collections, and the only way to tell one from a closed vocabulary is
#: to have written the closed vocabularies down. A name missing from this set is a RED
#: TEST, and the fix is a line here with the task that justifies it — never a widening of
#: the rule.
DECLARED_VOCABULARIES = frozenset({
    "AUTHORED_EVENT_TYPES",                                   # Task 1  §8.2's two names
    "STATES", "STRENGTH_ORDER",                               # Task 1  §3.13
    "FIELD_SCOPES", "UNIVERSAL_FIELDS", "DOMAIN_FIELDS", "FIELD_ROWS",   # Task 2  §3.11
    "VALUE_ORIGINS",                                          # Task 3  §3.12
    "FILE_FACTS_COLUMNS", "FORBIDDEN_COLUMN_SUBSTRINGS", "FACT_ORIGINS",  # Task 4 §3.1
    "UNRESOLVED_REASONS", "ATTEMPTED_PRODUCERS", "NOT_ABSTENTIONS",       # Task 5 B7
    "UNRESOLVED_COLUMNS",                                     # Task 5  the negative half
    "FACTS_TABLES",                                           # Tasks 2-5, 19  schema.py
    "CACHE_KEY_PARTS",                                        # Task 6  §3.4
    "SLOT_KINDS",                                             # Task 8  §3.5's slot kinds
    "VERSION_FAMILY_STATES",                                  # Task 14 §8.3
    "EVENT_INPUTS", "MEDIA_TYPES", "PHOTO_BANDS", "SCREENSHOT_BAND",      # Task 16 §2.6
    "FOUR_CHECKS", "CHECK_REASONS", "LLM_STATES",             # Task 17 §3.6
    "P6_CEILING_KEYS", "DEGRADATION_ORDER",                   # Task 20 §8.6
    "ENVELOPE_FIELDS",                                        # Task 21 §8.5
    "PLAN_VERSIONED", "SHARED_ACROSS_PLAN_VERSIONS",          # Task 23 §8.8
    "PROPOSAL_ELIGIBLE_STATES",                               # Task 24 §3.6
})

#: Field-creating callables §3.12 forbids: "it should not invent new fields automatically".
FIELD_CREATORS = frozenset({"add_field", "create_field", "register_field", "define_field",
                            "new_field", "add_fields"})

#: A group handle, by exact parameter name. §4.3 and §4.1: the graph "does not
#: automatically copy those missing facts onto sparse files". `file_ids` is NOT here — it
#: is an explicit set the caller passes, which is the opposite of a membership lookup —
#: and neither is `clustering`, which is Task 16's injected boundary.
GROUP_PARAMETERS = frozenset({"group_id", "group", "group_ids", "members", "member_ids",
                              "anchor", "anchor_file_id", "group_membership"})

#: Names that would encode an answer to OQ10 instead of refusing. Exact, never substrings:
#: `preferred_fact` is Task 18's legitimate pointer and must not be caught by a guess.
TIE_BREAK_NAMES = frozenset({"TIE_BREAK", "TIEBREAK", "TIE_BREAKER", "TIE_BREAK_ORDER",
                             "CONTRADICTION_WINNER", "EQUAL_RANK_POLICY"})

#: Modules whose objects are re-exports rather than P6 inventions.
UPSTREAM_MODULES = (
    "evidence_shape.vocabulary", "evidence_shape.observation", "evidence_shape.conformance",
    "evidence_shape.runs", "evidence_shape.schema", "evidence_shape.canonical",
    "evidence_shape.location", "evidence_shape.store", "evidence_shape.fixtures",
    "database_agent.events", "database_agent.supersede", "database_agent.budget",
    "database_agent.files_table", "database_agent.db", "database_agent.learning",
    "eval_harness.vocabulary", "eval_harness.run", "eval_harness.replay",
    "eval_harness.stage_output", "eval_harness.adversarial",
)

#: `from __future__ import annotations` binds a `_Feature` object at module level. It is
#: not P6 data and it is the only such binding, so it is named rather than pattern-matched.
IGNORED_BINDINGS = frozenset({"annotations"})

TYPING_HOMES = frozenset({"typing", "collections.abc", "__future__"})


# --------------------------------------------------------------------- the two tools

def facts_modules():
    """Every module in `facts`, imported. `facts/__init__.py` is a package marker and
    re-exports nothing, so it is walked with the rest rather than trusted."""
    modules = [facts]
    for info in pkgutil.iter_modules(facts.__path__):
        modules.append(importlib.import_module(f"facts.{info.name}"))
    return tuple(modules)


def module_constants(module):
    """Module-level DATA bindings: not modules, not classes, not callables, not typing
    machinery. An imported constant still counts — a copied gazetteer is still a gazetteer
    when it arrives through an import, which is why the exemption below is by identity."""
    out = {}
    for name, value in vars(module).items():
        if name.startswith("__") or name in IGNORED_BINDINGS:
            continue
        if isinstance(value, (types.ModuleType, type)):
            continue
        if getattr(value, "__module__", None) in TYPING_HOMES:
            continue
        if callable(value) and not dataclasses.is_dataclass(value):
            continue
        out[name] = value
    return out


def reachable(value, out=None, seen=None):
    """Every object reachable from one binding: through mappings, sequences, sets and
    frozen dataclasses. Materialized into a list so no id is ever reused mid-walk."""
    if out is None:
        out, seen = [], set()
    if id(value) in seen:
        return out
    seen.add(id(value))
    out.append(value)
    if isinstance(value, (str, bytes, bytearray)):
        return out
    if isinstance(value, Mapping):
        for key, item in value.items():
            reachable(key, out, seen)
            reachable(item, out, seen)
    elif dataclasses.is_dataclass(value) and not isinstance(value, type):
        for field in dataclasses.fields(value):
            reachable(getattr(value, field.name), out, seen)
    elif isinstance(value, (tuple, list, set, frozenset)):
        for item in value:
            reachable(item, out, seen)
    return out


def code_constants(module):
    """Every literal the compiler kept for this module — function bodies, comprehensions
    and nested definitions included. Bytecode, never source text: a comment cannot reach
    `co_consts`, and a docstring reaches it only as the whole docstring, so equality
    against a short token cannot be satisfied by prose."""
    loader = module.__loader__
    out, stack = set(), [loader.get_code(module.__name__)]
    while stack:
        current = stack.pop()
        for const in current.co_consts:
            if isinstance(const, types.CodeType):
                stack.append(const)
            elif isinstance(const, (str, bytes, int, float, tuple, frozenset)):
                try:
                    out.add(const)
                except TypeError:      # an unhashable nested constant; nothing to match
                    pass
    return out


@pytest.fixture(scope="module")
def upstream():
    """Every object P1, P2 and P4 publish, held alive and indexed by identity.

    A re-export passes; a hand-typed copy of the same values does not. That is Task 1's
    rule generalized: "`STATES` IS P4's tuple rather than a copy"."""
    held = []
    for name in UPSTREAM_MODULES:
        module = importlib.import_module(name)
        held.extend(vars(module).values())
    return held, frozenset(id(value) for value in held)


def is_upstream(value, upstream):
    """Identity, or a contiguous slice of a published upstream tuple.

    The slice arm exists for exactly one reason and it is a good one: Task 16 reads §2.6's
    screenshot band as `SIGNAL_TIERS[-1:]` so it never has to spell a `3`. Punishing that
    would push the author back to the literal, which is the thing being guarded against."""
    held, ids = upstream
    if id(value) in ids:
        return True
    if not isinstance(value, tuple) or not value:
        return False
    width = len(value)
    for candidate in held:
        if not isinstance(candidate, tuple) or len(candidate) < width:
            continue
        if any(candidate[start:start + width] == value
               for start in range(len(candidate) - width + 1)):
            return True
    return False


def offending(predicate, upstream):
    """Every (module, binding, value) in `facts` matching `predicate`, minus re-exports."""
    found = []
    for module in facts_modules():
        for name, binding in module_constants(module).items():
            if is_upstream(binding, upstream):
                continue
            for value in reachable(binding):
                if predicate(value):
                    found.append((module.__name__, name, repr(value)[:80]))
    return found


# ------------------------------------------- no invented number, regex or catalogue

def test_no_threshold_weight_window_radius_or_count_exists_as_a_module_constant(upstream):
    """Every one of them is a NUMBER, so one predicate covers the lot: minimum score,
    minimum margin, positional weight, signal-tier weight, session window, GPS radius,
    screen resolution, sensor aspect ratio and the usable-fact threshold.

    Each is a Deferred row and each is injected with no default. `bool` is excluded
    because `destination_eligible` and `active` are flags, not quantities."""
    def is_number(value):
        return isinstance(value, (int, float, complex)) and not isinstance(value, bool)

    assert offending(is_number, upstream) == []


def test_no_regex_catalogue_exists_as_a_module_constant(upstream):
    """§3.10 forbids fuzzy date parsing and requires explicit patterns — and Task 12
    receives them as an injected `DatePatterns`, including the three the design names
    (`Spring 2025`, `AY 2024-25`, `Michaelmas Term 2024`). A compiled pattern sitting at
    module level in `facts` is that catalogue having moved in."""
    assert offending(lambda value: isinstance(value, re.Pattern), upstream) == []


def test_every_module_level_collection_is_a_declared_closed_vocabulary(upstream):
    """A gazetteer, a producer-string list, a zone-weight map and a closed vocabulary are
    all collections. The only way to tell them apart is to have written the closed
    vocabularies down, so a new collection is a red test until someone justifies it."""
    undeclared = []
    for module in facts_modules():
        for name, binding in module_constants(module).items():
            if isinstance(binding, (tuple, list, set, frozenset, dict, Mapping)):
                if is_upstream(binding, upstream):
                    continue
                if name not in DECLARED_VOCABULARIES:
                    undeclared.append((module.__name__, name, len(binding)))
    assert undeclared == []


def test_no_producer_string_from_catalogue_01_appears_anywhere_in_facts():
    """Catalogue 01's own `injection` clause: "P6 receives this list as data at
    construction ... It is **not** imported as a module-level constant."

    Copying it into a `facts` module would satisfy every namespace guard above while
    destroying their point, so this one reads the compiled code: a literal inside a
    function body is caught exactly like one at module level. The `property_names` blocks
    are included because "the metadata property names the discount rule reads" is its own
    Deferred row (Task 9), owned by the catalogue and not by `facts`."""
    assert CATALOGUE_01.is_file(), CATALOGUE_01
    catalogue = json.loads(CATALOGUE_01.read_text(encoding="utf-8"))
    banned = {entry["match"].casefold()
              for block in ("entries", "refused", "uncertain")
              for entry in catalogue[block]}
    for value in catalogue["property_names"].values():
        if isinstance(value, list):
            banned.update(name.casefold() for name in value)
    assert len(banned) >= 115

    found = []
    for module in facts_modules():
        for const in code_constants(module):
            if isinstance(const, str) and const.casefold() in banned:
                found.append((module.__name__, const))
    assert found == []


def test_facts_names_no_file_and_holds_no_path(upstream):
    """P6 loads nothing from disk. A `Path`, or a string naming anything under
    `planning/`, is a catalogue arriving by another door."""
    def is_path_like(value):
        if isinstance(value, Path):
            return True
        if not isinstance(value, str):
            return False
        lowered = value.casefold()
        return ("planning/" in lowered or lowered.endswith(".json")
                or "deferred-catalogues" in lowered)

    assert offending(is_path_like, upstream) == []


def test_facts_has_exactly_the_modules_the_plan_declares():
    """The file layout is a contract. A `catalogues.py` is the one new module that would
    pass every other guard in this file on the day it was added."""
    present = {info.name for info in pkgutil.iter_modules(facts.__path__)}
    assert present == DECLARED_MODULES


# ------------------------------------------------------- imports: what P6 may not touch

PROBE = (
    "import importlib, json, pkgutil, sys\n"
    "import facts\n"
    "for info in pkgutil.iter_modules(facts.__path__):\n"
    "    importlib.import_module('facts.' + info.name)\n"
    "print(json.dumps({name: getattr(module, '__file__', None)\n"
    "                  for name, module in sys.modules.items()}))\n"
)
BASELINE = (
    "import json, sys\n"
    "print(json.dumps({name: getattr(module, '__file__', None)\n"
    "                  for name, module in sys.modules.items()}))\n"
)


def _run(source):
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(REPO / "src")
    finished = subprocess.run([sys.executable, "-c", source], cwd=str(REPO),
                              env=environment, capture_output=True, text=True)
    assert finished.returncode == 0, finished.stderr[-2000:]
    return json.loads(finished.stdout)


@pytest.fixture(scope="module")
def import_delta():
    """Exactly what importing every `facts` module pulls in, over a bare interpreter.

    A fresh subprocess, because `sys.modules` inside a pytest run already holds everything
    the rest of the suite imported — asking the live interpreter what P6 imports would
    answer a different question and always answer "everything"."""
    baseline = _run(BASELINE)
    after = _run(PROBE)
    return {name: path for name, path in after.items() if name not in baseline}


def test_nothing_in_facts_imports_planning_domains(import_delta):
    """The skeleton, Task 2: `planning/domains/` is a RESEARCH ARTIFACT — 574 entries,
    2,164 distinct field keys, `proposal` provenance, and its own gate reporting 566
    failures. It is a menu someone may one day draw from entry by entry, with a decision
    each time. It is not this catalogue's source and `facts` must never import it.

    `planning/domains/check.py` is importable — there is a `__pycache__` beside it — so
    this is a live possibility rather than a theoretical one."""
    planning = str(REPO / "planning")
    domains = str(REPO / "planning" / "domains")
    leaked = {name: path for name, path in import_delta.items()
              if path and (path.startswith(domains) or path.startswith(planning))}
    assert leaked == {}


def test_facts_imports_no_grouping_tree_placement_or_model_module(import_delta):
    """P9, P10, P11 and P8 do not exist, and the absence is the contract (§4.1, §4.3,
    §3.3). Stated as an allowlist rather than a blocklist so it still holds on the day
    they are built: the only first-party packages `facts` may reach are these five."""
    allowed = {"facts", "database_agent", "evidence_shape", "eval_harness", "extractors"}
    source_root = str(REPO / "src")
    reached = {name.split(".")[0] for name, path in import_delta.items()
               if path and path.startswith(source_root)}
    assert reached <= allowed
    for forbidden in ("readers", "orchestrator", "scan_agent", "grouping", "tree",
                      "placement", "llm", "model"):
        assert forbidden not in reached


def test_facts_adds_no_third_party_runtime_dependency(import_delta):
    """Python 3.12, stdlib only. Third-party libraries live in `src/readers/` behind the
    `readers` extra and this part may not import one."""
    third_party = {name: path for name, path in import_delta.items()
                   if path and ("site-packages" in path or "dist-packages" in path)}
    assert third_party == {}


# --------------------------------------------------- the other structural single-homes

def test_subsystem_p6_is_written_in_exactly_one_place():
    """M8: P6 authors its events and P1 writes them. A second module spelling the
    subsystem is a second authority over who authored a fact.

    Read from compiled code rather than the namespace, because `from facts.authorship
    import SUBSYSTEM` is a re-export and puts the NAME in `co_consts`, never the value."""
    holders = sorted(module.__name__ for module in facts_modules()
                     if SUBSYSTEM in code_constants(module))
    assert holders == ["facts.authorship"]


def test_no_module_branches_on_source_type_or_extractor_name():
    """§2.8 and Done-means 6: P6 resolves a fixture carrying an unrecognised `source_type`
    with no new code. A per-format branch is how that stops being true, and P6 requires no
    per-format knowledge and must not acquire any."""
    for module in facts_modules():
        for name, member in vars(module).items():
            if name.startswith("_") or not callable(member):
                continue
            if getattr(member, "__module__", None) != module.__name__:
                continue
            try:
                parameters = set(inspect.signature(member).parameters)
            except (TypeError, ValueError):
                continue
            assert "source_type" not in parameters, f"{module.__name__}.{name}"
            assert "extractor_name" not in parameters, f"{module.__name__}.{name}"

    source_types = {value.casefold() for value in SOURCE_TYPES}
    for module in facts_modules():
        for constant_name, binding in module_constants(module).items():
            for value in reachable(binding):
                if isinstance(value, str) and value.casefold() in source_types:
                    pytest.fail(f"{module.__name__}.{constant_name} names a source type")


def test_no_p4_read_is_consumed_in_p4s_order(monkeypatch):
    """P4's reads are `ORDER BY rowid` — insertion order, which is stable within one
    database and is NOT a property of the corpus. Verified by execution on 2026-08-21:
    writing the same three fixtures as runs 1,2,3 and as 3,2,1 returns
    `['BUSIB 4300', 'BUSIB 4300 Syllabus', 'Columbia']` and the reverse.

    Task 7's `observations_for_version` is the one chokepoint every P6 read goes through
    (it is also the per-content-hash filter P4 does not publish), so the guard hands it
    P4's answer in both orders and requires the same result. Behavioural, not structural:
    the question is whether the ORDER changes the RESULT, and only running it can answer
    that. The P4 read is replaced outright, so no database rows are needed."""
    from evidence_shape.location import Location, Segment
    from evidence_shape.observation import Observation

    import facts.evidence
    from facts.evidence import observations_for_version

    digest = "0" * 64
    made = []
    for raw, label in (("BUSIB 4300", "title"),
                       ("BUSIB 4300 Syllabus", "heading"),
                       ("Columbia", "body")):
        made.append(Observation(
            file_id="file-1", content_hash=digest, extractor_name="pdf.text",
            extractor_version="1.0.0", source_type="text_document", raw_value=raw,
            location=Location("metadata", (Segment("field", label=label),)),
            occurrence_count=1, observed_at="2026-08-19T12:00:00+00:00",
            reliability="direct", run_id="run-1"))

    monkeypatch.setattr(facts.evidence, "observations_for_file",
                        lambda conn, file_id: list(made))
    straight = observations_for_version(None, "file-1", digest)

    monkeypatch.setattr(facts.evidence, "observations_for_file",
                        lambda conn, file_id: list(reversed(made)))
    reversed_order = observations_for_version(None, "file-1", digest)

    assert len(straight) == 3
    assert reversed_order == straight


# ================================================================================
# The open questions. One named test each. None of them is answered here.
# ================================================================================

def test_oq3_purpose_is_still_one_row_and_p6_has_not_promoted_it(p6_conn):
    """OQ3, OPEN: "Is `purpose` a universal field or an Applications-domain field? §3.9
    requires it to be 'first-class'; §3.11's universal list omits it and places it only
    under College applications."

    P6 ships §3.11's placement and answers nothing. What it must NOT do is answer the
    question by creating BOTH — a universal `purpose` and a domain `purpose` would be two
    columns for one concept, which is the tie-break rule's exact prohibition: one stored
    key per concept, every other word an alias. Settling OQ3 changes one row's `scope` and
    nothing else, because no module branches on where it lives."""
    rows = [row for row in FIELD_ROWS if row.field_key == "purpose"]
    assert len(rows) == 1
    assert rows[0].scope == COLLEGE_APPLICATIONS
    assert "purpose" not in UNIVERSAL_FIELDS
    assert get_field(p6_conn, "purpose")["scope"] == COLLEGE_APPLICATIONS


def test_oq5_finance_has_a_schema_and_p6_neither_activates_nor_suppresses_it(p6_conn):
    """OQ5, OPEN [seam with P7]: "Finance has a fact schema in §3.11 but is a safety domain
    in §3.15 ... Does the Finance fact schema activate at launch, or does
    detection-and-protection precede any field extraction?"

    P6 holds the schema and decides nothing: activation is entirely the caller's injected
    signals. A module-level constant naming Finance outside the catalogue would be P6
    taking a side, and so would a hard-coded gate on a handling class."""
    assert FINANCE in FIELD_SCOPES
    assert DOMAIN_FIELDS[FINANCE]
    assert fields_in_scope(p6_conn, FINANCE)

    naming = {module.__name__ for module in facts_modules()
              for binding in module_constants(module).values()
              for value in reachable(binding)
              if isinstance(value, str) and value == FINANCE}
    assert naming <= {"facts.fields", "facts.vocabulary"}


def test_oq6_multiplicity_is_a_column_with_no_answer_in_it(p6_conn):
    """OQ6, OPEN: "May one (file, field) hold several simultaneously active values, and if
    so how does the §3.7 margin rule apply when more than one candidate is correct?"

    The column exists so the answer has somewhere to go. Every row's value is `None`, so
    no field has been quietly given a multiplicity, and §3.7's margin rule stays as Task 11
    wrote it: two candidates within the margin fill nothing."""
    assert "multiplicity" in {field.name for field in dataclasses.fields(FieldRow)}
    assert {row.multiplicity for row in FIELD_ROWS} == {None}
    for scope in FIELD_SCOPES:
        for row in fields_in_scope(p6_conn, scope):
            assert row["multiplicity"] is None


def test_oq8_no_producer_can_create_a_field_at_run_time(p6_conn):
    """OQ8, OPEN [seam with P10]: "Does user approval of a custom template create `fields`
    rows, and at what scope — corpus-wide or plan-version-local?"

    Until that is answered, nothing creates one. §3.12: the system "may create new values
    when it sees a new course, project, company, university, or event, but it should not
    invent new fields automatically", and §3.5: "The LLM is not allowed to invent a new
    fact schema, create an unsupported field, or make a free-form filing decision."

    Both halves: no field-creating callable is published, and the attempt raises and
    leaves the catalogue byte for byte unchanged."""
    creators = {f"{module.__name__}.{name}" for module in facts_modules()
                for name in vars(module) if name in FIELD_CREATORS}
    assert creators == set()

    def catalogue():
        return sorted((row["field_key"], row["scope"]) for scope in FIELD_SCOPES
                      for row in fields_in_scope(p6_conn, scope))

    before = catalogue()
    with pytest.raises(FieldNotInCatalogue):
        ensure_value(p6_conn, field_key="admissions_packet", canonical_value="Round 1",
                     first_evidence_ref="sha256:" + "0" * 64, origin=VALUE_ORIGINS[0])
    assert catalogue() == before


def test_oq9_no_write_path_takes_a_group(import_delta):
    """OQ9, OPEN [seam]: "After the user accepts the group, does that purpose become a fact
    on non-anchor members, or does it remain membership only?"

    Until it is settled, P6 writes nothing group-derived — §4.1: the graph "does not
    automatically copy those missing facts onto sparse files"; §3.9: a session is "not a
    basis for automatic semantic propagation". Enforced twice: no grouping module is
    imported at all, and no callable anywhere in `facts` will accept a group handle."""
    assert "grouping" not in {name.split(".")[0] for name in import_delta}

    for module in facts_modules():
        for name, member in vars(module).items():
            if name.startswith("_") or not callable(member):
                continue
            if getattr(member, "__module__", None) != module.__name__:
                continue
            try:
                parameters = set(inspect.signature(member).parameters)
            except (TypeError, ValueError):
                continue
            assert not parameters & GROUP_PARAMETERS, f"{module.__name__}.{name}"


def test_oq10_two_equal_rank_contradicting_facts_are_never_ranked_by_p6():
    """OQ10, OPEN: "§3.13 orders the six states but does not define the comparison for two
    equal-rank contradicting facts ... Reject both, surface both as competing candidates,
    or defer to the internal score?"

    P6 refuses to choose and writes an `unresolved` row instead, which is why the refusal
    is inspectable (§8.5: "Did it abstain when evidence was absent?"). Two halves: a state
    never outranks itself, so the tie is real rather than resolved by an accident of
    comparison; and no constant anywhere encodes a tie-break policy."""
    for state in STRENGTH_ORDER:
        assert is_stronger(state, state) is False

    #: §3.13 makes `rejected` an EXCLUSION, not a rank, so Task 1 gives it no strength and
    #: asking for one raises. That is the reason the loop above is over `STRENGTH_ORDER`
    #: and not over `STATES`: a `rejected` fact is never compared, it is excluded.
    rejected = next(state for state in STATES if state not in STRENGTH_ORDER)
    with pytest.raises(Exception):
        is_stronger(rejected, rejected)

    encoded = {f"{module.__name__}.{name}" for module in facts_modules()
               for name in vars(module) if name in TIE_BREAK_NAMES}
    assert encoded == set()
    assert any("contradict" in reason for reason in UNRESOLVED_REASONS)


# ================================================================================
# The two that CLOSED. Their guards are inverted: they assert the closure.
# ================================================================================

def test_oq4_is_closed_as_subject_and_the_catalogue_carries_no_course_row(p6_conn):
    """OQ4, CLOSED — D6, ratified 2026-08-21. One field, and its key is `subject`.

    §3.1, §3.2 and §3.12 all say `subject`; only §3.11's Academic row says `course`, and
    that is the design's PROSE for the same field. A field key is a join handle, so two
    spellings are two columns — the word `course` survives inside quotations and nowhere
    else. The same rename has already been applied across `planning/domains/` (1,302 keys).

    This guard is INVERTED on purpose. A test asserting OQ4 is open would pass every day
    up to the one this plan is executed and fail on that day, which is the failure mode
    that made the inversion worth writing down."""
    keys = {row.field_key for row in FIELD_ROWS}
    assert "subject" in keys
    assert "course" not in keys
    assert get_field(p6_conn, "subject")["scope"] == ACADEMIC
    with pytest.raises(FieldNotInCatalogue):
        get_field(p6_conn, "course")

    #: Done-means 4's value lands under `subject` and under no other key.
    assert ensure_value(p6_conn, field_key="subject", canonical_value="BUSIB 4300",
                        first_evidence_ref="sha256:" + "1" * 64,
                        origin=VALUE_ORIGINS[0])
    with pytest.raises(FieldNotInCatalogue):
        ensure_value(p6_conn, field_key="course", canonical_value="BUSIB 4300",
                     first_evidence_ref="sha256:" + "1" * 64, origin=VALUE_ORIGINS[0])

    #: And no module keeps the old key alive as a literal, in a body or at module level.
    assert [module.__name__ for module in facts_modules()
            if "course" in code_constants(module)] == []


def test_oq11_is_closed_and_p6_publishes_no_competing_sensitivity_record(p6_conn):
    """OQ11, CLOSED — D2, ratified 2026-08-21, on the question it asked: WHICH record is
    authoritative. The answer is P7's.

    P7's `ClassificationRecord`, keyed `(file_id, content_hash)`, is authoritative;
    `files.sensitivity_state` is its PROJECTION, written through P1's published
    `set_sensitivity_state`; and `Unreadable or unclassified` is a GATE OUTCOME, not a file
    fact — it never enters that column. P6 was the part that made the name count three
    (§3.11's universal fact, §8.2's file-record state, §8.4's handling class). After D2 it
    makes it one: P6 publishes no record, no table, no vocabulary and no writer.

    INVERTED on purpose, for the same reason as OQ4."""
    tables = {row[0] for row in p6_conn.execute(
        "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')")}
    assert [name for name in tables
            if "sensitiv" in name.lower() or "classification" in name.lower()] == []

    published = {f"{module.__name__}.{name}" for module in facts_modules()
                 for name in vars(module)
                 if not name.startswith("_")
                 and ("sensitiv" in name.lower() or "classification" in name.lower())}
    assert published == set()

    #: P1's writer belongs to P7. P6 importing it would make the projection have two
    #: authors, which is precisely what D2 removed.
    assert [module.__name__ for module in facts_modules()
            if "set_sensitivity_state" in vars(module)] == []


def test_the_sensitivity_field_row_is_needs_joseph_c5_and_is_not_settled(p6_conn):
    """OQ11's RESIDUE, still open, held here by name so it cannot be lost.

    D2 did NOT settle whether P6 keeps a `sensitivity` / `sensitivity status` FIELD ROW
    beside P7's authoritative record. The evidence points three ways and that is exactly
    why it is Joseph's:

      * §3.12 names it in the design's own field list — "subject, purpose, target
        university, project, event, or sensitivity" — and §3.11 spells it
        `sensitivity status`;
      * P7's SPEC, Contract-in, says in bold "P6 must accept `sensitivity` as a
        first-class universal field" (§3.11) rather than a domain-scoped one;
      * round 1's F-2 found the field HAS NO PRODUCER — nothing in P6 would ever write it,
        so it would ship as a permanently empty column that a reader could mistake for
        "not sensitive".

    The instruction standing over all three is "Create no such row until asked." So this
    test pins TODAY'S state and SETTLES NOTHING. If the row stays, this test is where the
    decision lands: flipping it is one line here plus one row in Task 2's catalogue, and
    nothing else in P6 branches on the answer — which is what "held open" has to mean to
    be worth anything."""
    keys = {row.field_key for row in FIELD_ROWS}
    assert "sensitivity" not in keys
    assert "sensitivity_status" not in keys
    for field_key in ("sensitivity", "sensitivity_status"):
        with pytest.raises(FieldNotInCatalogue):
            get_field(p6_conn, field_key)
```

- [ ] **Step 2: Run the test and watch it fail**

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6/test_p6_no_invention.py -q
```

Expected on a first run, before Tasks 1–24 are green: **collection error**,
`ModuleNotFoundError: No module named 'facts'`. Run in Wave E order — after Tasks 1–24 — the
expected first failure is
`test_every_module_level_collection_is_a_declared_closed_vocabulary`, listing any collection a
sibling task published that this file does not yet declare. **That failure is the guard working**,
and it is resolved by adding the name to `DECLARED_VOCABULARIES` with the task that owns it — never
by widening the rule to a shape or a length.

- [ ] **Step 3: There is no implementation step**

This task creates no source file. Its "implementation" is the twenty-one tests above holding
against the twenty-four tasks that ran before it. If a guard fails, the fix belongs to the module
that broke it:

| Failing guard | Where the fix goes |
|---|---|
| a module-level number | the producer that introduced it — make it a required keyword with no default, like every other Deferred row |
| a module-level compiled pattern | Task 12's injected `DatePatterns` |
| an undeclared collection | one line in `DECLARED_VOCABULARIES`, naming the task that owns it |
| a catalogue-01 producer string | Task 9 — it is injected at construction, never imported |
| a new module | the file layout is a contract; the module either belongs in it or does not exist |
| an import outside the five packages | the task that added it |
| `subsystem = "P6"` in two places | M8 — one author, one place |
| an open question that has been answered in code | the answer is Joseph's, not this plan's |
| a closed question whose guard did not invert | this file, and only after re-reading the ratified decision |

- [ ] **Step 4: Run it green, then the whole part, then the whole suite**

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6/test_p6_no_invention.py -q
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6 -q
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest -q
```

Expected: **21 passed** for this file; the whole part green; and the pre-existing **1300 tests**
still passing, because P6 touched no file outside `src/facts/` and `tests/p6/` (D5).

- [ ] **Step 5: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add tests/p6/test_p6_no_invention.py && \
git commit -m "feat(P6): the no-invention guard — six questions held open, two closures inverted, every constant checked at run time"
```

---

## Contract notes from Tasks 24 and 25

Reported, not unilaterally resolved. Each was found while writing these two tasks and each belongs to
someone else's decision.

**N1 — Task 1's "no state literal anywhere else in `facts`" is already contradicted by four
sibling tasks, and this guard adopts the narrower rule.** Task 1's skeleton entry asks for *"the
absence of any string literal spelling a state name anywhere else in `facts`"*. As written,
`facts.families` publishes `VERSION_FAMILY_STATES = ("validated", "possible")`, `facts.session`
publishes `SESSION_STATE = "possible"`, `facts.photo_event` publishes `EVENT_STATE = "validated"`
and `facts.llm_seam` publishes `LLM_STATES = ("llm_supported", "possible")`. A guard enforcing Task
1's clause literally would fail on the day this plan is executed — the exact failure mode that made
OQ4's and OQ11's inversions necessary. **What actually matters is the value, not the literal:**
§3.13's risk is a seventh spelling (`LLM-supported`, `User-confirmed`) reaching the database, and
that is closed already — P4's `check` refuses anything outside the six, and every one of the four
constants above is a member of `STATES`. Task 24 nonetheless spells none: `PROPOSAL_ELIGIBLE_STATES`
is derived from `STRENGTH_ORDER`, which is the shape Task 1 wanted. **Owner: Task 1**, to narrow its
clause to "no state name is spelled outside `STATES`'s six members" or to have Tasks 14, 15, 16 and
17 derive theirs by index as Task 24 does.

**N2 — `DECLARED_VOCABULARIES` names two constants no task's `Produces:` line declares.**
`UNRESOLVED_COLUMNS` and `FACTS_TABLES` are listed because Task 5's and Task 4's tests read
`PRAGMA table_info` and Task 19 modifies `schema.py`, so a table-name or column-name tuple is the
natural shape for them — but neither is on a `Produces:` line, so neither is certain. If they are not
built, the two lines are dead entries in an allowlist, which costs nothing. If they are built under
different names, the guard goes red on first run and the fix is one line. **This is the guard
behaving correctly**, and it is written here so that first red is not mistaken for a defect.

**N3 — Task 24 fixes four keyword lists the skeleton left as `...`.** `active_allowlist_for`,
`unresolved_for`, `event_facts`, `session_facts` and `family_facts` are spelled out in this task's
`Interfaces:` block. Nothing is renamed and no signature that another task consumes is changed;
these five are published *by* Task 24 and consumed only by P9–P13, none of which exist.

**N4 — `evidence_chain` and `values_with_counts` are the only two functions in P6 that read another
task's table with SQL.** Both are unavoidable: `evidence_chain` is addressed by `fact_id` alone and
no module publishes a by-`fact_id` read, and `values_with_counts` needs one corpus-wide aggregate.
They read `file_facts`, which is P6's own table, and they write nothing. If Task 4 later publishes
`fact_by_id(conn, fact_id)`, `evidence_chain` should use it. **Owner: Task 4**, optional.

**N5 — the four-pass ordering is not asserted here and must not be.** D5 cut Task 26, so
`no_usable_facts_for` is a read surface P6's own tests exercise and the caller keeps passing
`orchestrator.TARGETED_OCR_UNAVAILABLE`. This guard asserts `facts` imports no `orchestrator`, which
is the correct and only enforceable statement of that today. Wiring it is later, separate work.
