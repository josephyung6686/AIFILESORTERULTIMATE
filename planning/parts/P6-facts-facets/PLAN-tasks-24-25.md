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

Expected: **22 passed**. Then the whole part, to prove no sibling read regressed:

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6 -q
```

- [ ] **Step 5: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/facts/read_surface.py tests/p6/test_p6_read_surface.py && \
git commit -m "feat(P6): the read surface published to neighbours — two exclusions derived, never spelled"
```

---
