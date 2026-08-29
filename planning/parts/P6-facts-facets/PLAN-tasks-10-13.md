# P6 — Facts and facets — PLAN, Tasks 10–13

> This is the detail pass for the four **Wave B** producers that turn P4 observations into
> §3.5 rule-validated facts, §3.7 ranked facets, §3.10 dated terms and §3.11 domain activation.
> The rules, the verified seams and the file layout are in `PLAN-SKELETON.md`; the `Interfaces:`
> block on each task below is the same contract, honoured name for name. Tasks 1–9, 14–19 and
> 20–27 are written in parallel by other authors against the same skeleton.

---

## What already exists when Task 10 starts

Tasks 1–9 are green. These four tasks import the following from `facts` and nothing else. Every
signature below is the skeleton's `Produces:` line, unchanged:

```text
facts.states        STATES: tuple[str, ...]                       (P4's six, re-exported)
facts.fields        FIELD_SCOPES: tuple[str, ...]                 (universal + the six §3.11 domains)
                    DOMAIN_FIELDS: Mapping[str, tuple[str, ...]]
                    fields_in_scope(conn, scope) -> list[sqlite3.Row]
                    FieldNotInCatalogue
facts.values        VALUE_ORIGINS: tuple[str, str]                ("automatic", "user")
                    ensure_value(conn, *, field_key, canonical_value,
                                 first_evidence_ref, origin) -> str
facts.file_facts    FACT_ORIGINS: tuple[str, ...]                 (§3.1's five, in §3.1's order)
                    write_fact(conn, *, file_id, content_hash, field_key, value_id,
                               reliability_state, origin, evidence_refs, cache_key,
                               active, ...) -> str
                    facts_for_file(conn, file_id, content_hash) -> list[sqlite3.Row]
facts.unresolved    ATTEMPTED_PRODUCERS: tuple[str, str, str]     ("direct", "rule", "llm")
                    write_unresolved(conn, *, file_id, content_hash, field_key, reason,
                                     attempted_producers, evidence_refs, cache_key) -> str
                    unresolved_for_file(conn, file_id, content_hash, *,
                                        field_key=None, reason=None) -> list[sqlite3.Row]
facts.cache         fact_cache_key(*, content_hash, extractor_version, analysis_tier,
                                   model_identifier, prompt_fingerprint) -> str
facts.evidence      observations_for_version(conn, file_id, content_hash) -> tuple[Observation, ...]
                    context_pair(observation) -> tuple[str, str, bool]
                    cite(observation) -> str
                    analysis_tier_for_observation(conn, observation) -> str
facts.schema        create_facts_schema(conn) -> None
```

**`tests/p6/conftest.py` publishes `p6_conn`** — P1's database with P4's three tables and P6's own
tables created, built on the root `conn` fixture in `tests/conftest.py`, exactly as
`tests/p4/conftest.py` builds `p4_conn`. Every test file below takes `p6_conn` and `tmp_path` and
constructs everything else itself.

**Verified live by import, 2026-08-22, not read from a document.**
`RELIABILITY_STATES == ("user_confirmed", "direct", "validated", "llm_supported", "possible",
"rejected")`; `ANALYSIS_TIERS == ("filesystem", "native", "ocr", "llm")`;
`ZONES` is fifteen members beginning `filename, path, metadata, title, heading, body`;
`SIGNAL_TIERS == (1, 2, 3)` and its members are **integers**; `observation_key` is a `@property` on
`Observation` returning a `sha256:`-prefixed string and is **not** a `dataclasses.field`;
`Observation.zone` is a property projecting `location.zone`; `dataclasses.replace` works on the
frozen slots `Observation` and recomputes the key; `evidence_shape.store.record_run` /
`record_observation` write with **no** foreign key to `files`; P1's `content_hash` is 64 lowercase
hex characters with no `sha256:` prefix and `ExtractionRun.__post_init__` rejects any other shape;
`fixtures.by_number(1).observations[0]` carries `raw_value == "BUSIB 4300"`,
`context_before == "Syllabus — "` (capital S, U+2014 EM DASH, one space either side),
`zone == "heading"`, `reliability == "possible"`, `occurrence_count == 3`.

**All nineteen P4 fixtures are usable with no extractor present.** Task 10 drives fixture 1
verbatim; the other three tasks author P4-shaped observations directly, which is the same thing
`evidence_shape.fixtures` does.

---

## One ordering edge inside Wave B, and it is the skeleton's own

Wave B parallelises, but the skeleton's `Consumes:` lines declare two directed edges and this plan
does not invent them:

```text
Task 11  facts.facets       word_boundary_match, Candidate, rank, fill_or_abstain
   ├──►  Task 10  facts.rules   "Consumes: … facts.facets (word-boundary matcher)"
   └──►  Task 12  facts.dates   "Consumes: … facts.facets.fill_or_abstain"
Task 13  facts.domains      independent of all three
```

**Execute Task 11 before Task 10 and Task 12.** The tasks are numbered in the skeleton's order and
written here in that order, but Task 10's Step 2 failure is `No module named 'facts.rules'` only
once `facts.facets` exists; run it before Task 11 and the failure is the wrong one and Step 4 cannot
pass. Task 13 may run at any point in the wave.

The reason the edge exists rather than being designed away: §3.7's word-boundary discipline binds
facet values **and** §3.5 context terms — the skeleton's Global Constraints say so in one sentence —
so a second matcher inside `facts.rules` would be a second home for the one rule that `MIT` must not
be found inside "submit".

---

## Two conventions these four tasks share, stated once

**1. The six reliability states are addressed by index into P4's tuple, never spelled.** Rule 2 of
the skeleton: *"The six literals are P4's, already published, and P6 re-spells none of them."* Task
1's test asserts the absence of any string literal spelling a state name anywhere else in `facts`.
So each module that writes a state binds it once, derived:

```python
from facts.states import VALIDATED
#: Task 1 owns the spelling. Never an index into STATES.
_VALIDATED = VALIDATED
```

`FACT_ORIGINS` and `ATTEMPTED_PRODUCERS` are addressed by index for the same reason — `FACT_ORIGINS`
= deterministic extractor · rule · LLM interpretation · user correction · user-approved folder, so
`FACT_ORIGINS[1]` is the rule producer; `ATTEMPTED_PRODUCERS` = direct · rule · llm, so
`ATTEMPTED_PRODUCERS[1]` is the rule route. `unresolved` reasons are passed as literals because
`write_unresolved` checks them against Task 5's closed thirteen and raises on a fourteenth — the
value is validated at the seam, which is where a closed vocabulary is supposed to be enforced.

**2. §3.4's cache key is computed per (file version, deterministic pass), and identically in every
module here.** §3.4's key is *"content hash + extractor version + analysis tier + model identifier +
prompt fingerprint"*, and Task 6 publishes it as five scalar keywords. A pass over one file version
reads several observations with several extractor versions and possibly several analysis tiers, and
no task in this plan owns that reconciliation. These four apply one rule:

- **`extractor_version`** is `canonical_json` of the sorted distinct `[extractor_name,
  extractor_version]` pairs of **every observation of that file version**. P4's `canonical_json` is
  the project's one deterministic serialization; a second one would be a second answer.
- **`analysis_tier`** is the **last** tier present in `ANALYSIS_TIERS` order — `filesystem` <
  `native` < `ocr` < `llm`. That is a reading of P4's published tuple order, not a new order, and it
  gives preamble rule 5 what it needs: a pass over native + OCR evidence lands in a different cache
  slot from the native-only pass, so pass 4 supersedes rather than overwrites.
- **`model_identifier` and `prompt_fingerprint` are `None`** on every fact and every abstention
  here. P4's `sha256_of` is length-prefixed and injective, so `None` is distinguishable from `""`.
- **The fact and the abstention produced by one pass share one key.** The SPEC requires the
  `unresolved` row to carry the *"same composition as `file_facts` (§3.4), so an abstention is
  invalidated by the same events that invalidate a fact"*, and an abstention with no citations has
  no cited observations to compute a key from. One key per pass answers both.

The helper is written out in each module that needs it rather than imported from a sibling: these
tasks cannot add to `facts.cache`, which Task 6 owns. **This diverges from `PLAN-tasks-14-15.md`,
which keys a fact on its cited observations only** — see *Contract ambiguities* at the end. It is
reported, not resolved.

---

### Task 10: Rule-validated facts, and the §3.5 context check (N-6)

**Files:**
- Create: `src/facts/rules.py`
- Test: `tests/p6/test_p6_rules.py`

**Interfaces:**
- Consumes: `facts.evidence` — `observations_for_version`, `context_pair`, `cite`,
  `analysis_tier_for_observation`; `facts.facets.word_boundary_match`; `facts.file_facts` —
  `write_fact`, `FACT_ORIGINS`; `facts.unresolved` — `write_unresolved`, `ATTEMPTED_PRODUCERS`;
  `facts.values` — `ensure_value`, `VALUE_ORIGINS`; `facts.states.STATES`;
  `facts.cache.fact_cache_key`; `evidence_shape.canonical.canonical_json`;
  `evidence_shape.vocabulary.ANALYSIS_TIERS`.
- Produces: `ACADEMIC_CONTEXT_TERMS: tuple[str, str, str, str, str]`, `MalformedRule`,
  `Rule(pattern, required_context_terms, field_key)` — an injected frozen dataclass;
  `context_check(before: str, after: str, terms) -> bool`;
  `apply_rules(conn, *, file_id, content_hash, rules) -> tuple[str, ...]`.

**Done-means:** 8, and the `validated` half of 4.

**The rule is literal, and its five terms are the whole authored vocabulary.** §3.5, verbatim:
*"Rules create validated facts when a candidate passes strict context checks. For example, BUSIB
4300 becomes a course fact only when the engine finds a course-code pattern together with academic
context such as "syllabus," "lecture," "credits," "instructor," or "semester.""* Five terms are
stated. The SPEC's Deferred table says the rest is unauthored — *"Rule context-term lists beyond the
five literal academic terms | §3.5 | Only "syllabus", "lecture", "credits", "instructor",
"semester" are stated. Every other domain's context vocabulary is unauthored."* So this module
publishes exactly those five and every other rule's terms arrive on the `Rule`. **There is no sixth
term**, and "course", "class", "professor" and "seminar" — all of which read as academic context to
a human — are each a test below that must fail the check.

**The stored field key is `subject` (D6), and this module never spells it.** §3.11's Academic row
says "course"; §3.1, §3.2 and §3.12 all say `subject`; D6 ratified `subject` because a field key is
a join handle and two spellings are two columns. `Rule.field_key` is data, so `facts.rules` names no
field at all and the tests supply `subject`.

**The pattern is injected too.** A course-code regex is not among §3.10's three named patterns, so
it is part of the Deferred catalogue. `Rule.pattern` is a **compiled** `re.Pattern`; a string is
refused, because §3.10 requires *"explicit regular expressions"* and a string would let a caller
pass something that is silently treated as a literal by one call site and as syntax by another.

**Case-insensitive, and it does not relax the boundary (N-6, B8(a)).** §3.5 writes its terms in
lowercase and states no matching rule, so P6 states one. P4's fixture 1 carries `context_before`
exactly `"Syllabus — "` with a capital S — B8(a) authored it that way so the walking skeleton's one
fact would resolve — and a case-sensitive check refuses it. But folding case is not relaxing the
boundary: the matcher is `facts.facets.word_boundary_match`, the same one §3.7 facet values go
through, so `semester` still cannot match inside `Semesterly` and A01's `MIT`-inside-"submit" is
refused by the boundary rather than by case.

**A truncated context is a different refusal.** §8.6 forbids silent truncation. A check that fails
on a record with `context_truncated = true` writes `reason = context_truncated`, never
`context_check_failed`: the term may have been cut off, and claiming a clean refusal would be a
claim this module cannot support. A check that **passes** on a truncated record still produces the
fact — if the term is present, it was not the part that got cut.

**A pattern that does not match writes nothing at all.** The SPEC's reason for
`context_check_failed` is *"§3.5 rule matched the pattern, found no required context term"* — the
pattern match is the precondition of the refusal. Without that, `unresolved` would fill with every
field every rule could theoretically have produced, and Done-means 18's *"every refusal … also
writes an `unresolved` row"* would become noise rather than a record.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_rules.py
"""§3.5 rule-validated facts -- Done-means 8, N-6, B8(a), and A03's ZIP-code case."""
import dataclasses
import json
import re
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file
from evidence_shape.fixtures import by_number
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run

from facts.file_facts import facts_for_file
from facts.rules import (
    ACADEMIC_CONTEXT_TERMS, MalformedRule, Rule, apply_rules, context_check,
)
from facts.unresolved import unresolved_for_file

CLOCK = "2026-08-22T00:00:00Z"

#: §3.10's catalogue is Deferred beyond the three named date patterns, and a
#: course-code pattern is not among them -- so the pattern is the test's, injected on
#: the Rule, and `facts.rules` holds no regex of its own.
COURSE_CODE = re.compile(r"\b[A-Z]{2,5} ?\d{2,5}\b")


def _record(conn, tmp_path, *, name, body):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Courses", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _run(conn, *, run_id, file_id, content_hash, analysis_tier="native"):
    if conn.execute("SELECT 1 FROM extraction_runs WHERE run_id = ?",
                    (run_id,)).fetchone() is None:
        record_run(conn, ExtractionRun(
            run_id=run_id, file_id=file_id, content_hash=content_hash,
            extractor_name="pdf.text", extractor_version="1.0.0",
            source_type="text_document", analysis_tier=analysis_tier, config={},
            completeness="complete", started_at=CLOCK, finished_at=CLOCK))


def _observe(conn, *, run_id, file_id, content_hash, raw, zone="heading",
             context_before=None, context_after=None, context_truncated=False):
    _run(conn, run_id=run_id, file_id=file_id, content_hash=content_hash)
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location(zone, (Segment("page", 1), Segment("heading", 2))),
        occurrence_count=1, observed_at=CLOCK, reliability="possible",
        run_id=run_id, context_before=context_before, context_after=context_after,
        context_truncated=context_truncated)
    record_observation(conn, observation)
    return observation


def _course_rule(terms=ACADEMIC_CONTEXT_TERMS):
    # D6: the stored academic key is `subject`. §3.11's word "course" is the design's
    # prose for the same field and survives inside quotations only.
    return Rule(pattern=COURSE_CODE, required_context_terms=tuple(terms),
                field_key="subject")


# --- the five terms are the design's, complete, and closed -------------------

def test_the_five_context_terms_are_exactly_the_designs_five():
    # §3.5, verbatim: "a course-code pattern together with academic context such as
    # "syllabus," "lecture," "credits," "instructor," or "semester."" Five terms are
    # stated literally; a sixth is a design change, not an implementation detail.
    assert ACADEMIC_CONTEXT_TERMS == ("syllabus", "lecture", "credits",
                                      "instructor", "semester")
    assert len(ACADEMIC_CONTEXT_TERMS) == 5
    assert len(set(ACADEMIC_CONTEXT_TERMS)) == 5


def test_no_other_context_vocabulary_is_authored_in_the_module():
    # "Rule context-term lists beyond the five literal academic terms | §3.5 | Only
    # "syllabus", "lecture", "credits", "instructor", "semester" are stated. Every
    # other domain's context vocabulary is unauthored."
    import facts.file_facts
    import facts.rules as module
    import facts.states
    import facts.unresolved
    import facts.values
    import evidence_shape.vocabulary
    foreign = {id(value)
               for source in (evidence_shape.vocabulary, facts.states,
                              facts.file_facts, facts.unresolved, facts.values)
               for value in vars(source).values()}
    catalogues = [name for name, value in vars(module).items()
                  if isinstance(value, tuple) and value and id(value) not in foreign
                  and all(isinstance(entry, str) for entry in value)]
    assert catalogues == ["ACADEMIC_CONTEXT_TERMS"]


def test_a_rule_carries_its_own_terms_and_the_module_supplies_no_default():
    # Every other domain's terms arrive injected; there is no default argument that
    # would quietly lend the academic five to a research or finance rule.
    with pytest.raises(TypeError):
        Rule(pattern=COURSE_CODE, field_key="subject")
    with pytest.raises(MalformedRule):
        Rule(pattern=COURSE_CODE, required_context_terms=(), field_key="subject")
    with pytest.raises(MalformedRule):
        Rule(pattern=r"\b[A-Z]{2,5} ?\d{3,4}\b",
             required_context_terms=ACADEMIC_CONTEXT_TERMS, field_key="subject")


# --- the context check itself ------------------------------------------------

def test_the_context_check_is_case_insensitive():
    # N-6. §3.5 writes its terms lowercase and states no matching rule, so P6 states
    # one: a term matches regardless of the case it appears in.
    for spelling in ("Syllabus", "SYLLABUS", "syllabus", "SyLLaBuS"):
        assert context_check(f"{spelling} - ", "", ACADEMIC_CONTEXT_TERMS) is True


def test_case_insensitivity_does_not_relax_the_word_boundary():
    # The §3.7 discipline is unchanged: a case-insensitive match is not a substring
    # match, so `semester` must not match inside a longer word.
    assert context_check("Semesterly digest", "", ACADEMIC_CONTEXT_TERMS) is False
    assert context_check("", "mid-semester break", ACADEMIC_CONTEXT_TERMS) is True
    assert context_check("lectureship award", "", ACADEMIC_CONTEXT_TERMS) is False


def test_both_halves_of_the_context_pair_are_read_and_never_concatenated():
    # M5: P4 split the context so §8.4 can redact a value without dropping its
    # context. Joining the halves would forge an adjacency the document does not have.
    assert context_check("Instructor: ", "", ACADEMIC_CONTEXT_TERMS) is True
    assert context_check("", " - 3 credits", ACADEMIC_CONTEXT_TERMS) is True
    assert context_check("sylla", "bus", ACADEMIC_CONTEXT_TERMS) is False


def test_an_absent_context_half_is_not_a_match():
    assert context_check("", "", ACADEMIC_CONTEXT_TERMS) is False
    assert context_check(None, None, ACADEMIC_CONTEXT_TERMS) is False


# --- Done-means 8, both halves ----------------------------------------------

def test_a_course_code_with_no_academic_context_produces_no_fact(p6_conn, tmp_path):
    # Done-means 8, negative half: "A course-code-shaped string with no academic
    # context term in its surrounding context produces no course fact."
    file_id, content_hash = _record(p6_conn, tmp_path, name="receipt.pdf",
                                    body=b"receipt")
    _observe(p6_conn, run_id="r-plain", file_id=file_id, content_hash=content_hash,
             raw="BUSIB 4300", context_before="Order ", context_after=" shipped")
    assert apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                       rules=(_course_rule(),)) == ()
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    rows = unresolved_for_file(p6_conn, file_id, content_hash, field_key="subject")
    assert [r["reason"] for r in rows] == ["context_check_failed"]


def test_p4s_fixture_1_verbatim_does_produce_one_validated_fact(p6_conn, tmp_path):
    # Done-means 8, positive half, and B8(a): fixture 1 carries `context_before`
    # exactly "Syllabus - " with a capital S. A case-sensitive check refuses it and
    # the walking skeleton produces no fact at all.
    fixture = by_number(1)
    original = fixture.observations[0]
    file_id, content_hash = _record(p6_conn, tmp_path, name="Syllabus.pdf",
                                    body=b"BUSIB 4300 Syllabus")
    _run(p6_conn, run_id="fixture-1", file_id=file_id, content_hash=content_hash)
    observation = dataclasses.replace(original, file_id=file_id,
                                      content_hash=content_hash, run_id="fixture-1")
    record_observation(p6_conn, observation)

    assert observation.raw_value == "BUSIB 4300"
    assert observation.context_before == "Syllabus — "   # capital S, EM DASH
    assert observation.context_before[0] == "S"

    written = apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                          rules=(_course_rule(),))
    assert len(written) == 1
    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert [(r["field_key"], r["canonical_value"], r["reliability_state"])
            for r in rows] == [("subject", "BUSIB 4300", "validated")]
    assert json.loads(rows[0]["evidence_refs"]) == [observation.observation_key]
    assert unresolved_for_file(p6_conn, file_id, content_hash) == []


def test_the_fact_cites_an_observation_key_and_leaves_the_raw_value_alone(
        p6_conn, tmp_path):
    # §3.2: the conclusion is stored beside the evidence, and the evidence survives.
    file_id, content_hash = _record(p6_conn, tmp_path, name="Syllabus.pdf",
                                    body=b"BUSIB 4300")
    observation = _observe(p6_conn, run_id="r-ok", file_id=file_id,
                           content_hash=content_hash, raw="BUSIB 4300",
                           context_before="Syllabus — ")
    apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                rules=(_course_rule(),))
    refs = json.loads(facts_for_file(p6_conn, file_id, content_hash)[0]["evidence_refs"])
    assert refs == [observation.observation_key]
    assert all(ref.startswith("sha256:") for ref in refs)
    stored = p6_conn.execute("SELECT raw_value FROM evidence WHERE file_id = ?",
                             (file_id,)).fetchone()
    assert stored["raw_value"] == "BUSIB 4300"


def test_every_one_of_the_five_terms_satisfies_the_check_on_its_own(
        p6_conn, tmp_path):
    for index, term in enumerate(ACADEMIC_CONTEXT_TERMS):
        file_id, content_hash = _record(p6_conn, tmp_path, name=f"t{index}.pdf",
                                        body=f"BUSIB 4300 {term}".encode())
        _observe(p6_conn, run_id=f"r{index}", file_id=file_id,
                 content_hash=content_hash, raw="BUSIB 4300",
                 context_after=f" ({term.title()})")
        assert len(apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                               rules=(_course_rule(),))) == 1


def test_a_term_outside_the_five_does_not_satisfy_the_check(p6_conn, tmp_path):
    # "course", "class", "professor" and "seminar" all read as academic context to a
    # human. The design names five and this module authors no sixth.
    for index, near_miss in enumerate(("course", "class", "professor", "seminar")):
        file_id, content_hash = _record(p6_conn, tmp_path, name=f"n{index}.pdf",
                                        body=f"BUSIB 4300 {near_miss}".encode())
        _observe(p6_conn, run_id=f"n{index}", file_id=file_id,
                 content_hash=content_hash, raw="BUSIB 4300",
                 context_before=f"{near_miss} ")
        assert apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                           rules=(_course_rule(),)) == ()
        assert [r["reason"] for r in unresolved_for_file(
            p6_conn, file_id, content_hash)] == ["context_check_failed"]


# --- §8.6: a cut context is not a clean refusal ------------------------------

def test_a_failed_check_on_a_truncated_record_is_context_truncated(
        p6_conn, tmp_path):
    # §8.6 forbids silent truncation. The term may have been cut off, so this is not
    # the same refusal as "the term is not there".
    file_id, content_hash = _record(p6_conn, tmp_path, name="cut.pdf", body=b"cut")
    _observe(p6_conn, run_id="r-cut", file_id=file_id, content_hash=content_hash,
             raw="BUSIB 4300", context_before="...ourse outline for ",
             context_after=" and the", context_truncated=True)
    assert apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                       rules=(_course_rule(),)) == ()
    rows = unresolved_for_file(p6_conn, file_id, content_hash, field_key="subject")
    assert [r["reason"] for r in rows] == ["context_truncated"]
    assert unresolved_for_file(p6_conn, file_id, content_hash,
                               reason="context_check_failed") == []


def test_a_truncated_record_whose_check_passes_still_produces_the_fact(
        p6_conn, tmp_path):
    # Truncation is only a problem for a refusal. If the term is present, it was not
    # the part that got cut.
    file_id, content_hash = _record(p6_conn, tmp_path, name="cut2.pdf", body=b"cut")
    _observe(p6_conn, run_id="r-cut2", file_id=file_id, content_hash=content_hash,
             raw="BUSIB 4300", context_before="...Syllabus — ",
             context_truncated=True)
    assert len(apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                           rules=(_course_rule(),))) == 1
    assert unresolved_for_file(p6_conn, file_id, content_hash) == []


# --- the shape of the refusal set --------------------------------------------

def test_a_pattern_that_does_not_match_writes_no_row_at_all(p6_conn, tmp_path):
    # A rule that does not apply is not a refusal. Writing one would fill
    # `unresolved` with every field every rule could theoretically have produced.
    file_id, content_hash = _record(p6_conn, tmp_path, name="prose.pdf",
                                    body=b"prose")
    _observe(p6_conn, run_id="r-none", file_id=file_id, content_hash=content_hash,
             raw="a paragraph about nothing in particular",
             context_before="Syllabus — ")
    assert apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                       rules=(_course_rule(),)) == ()
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    assert unresolved_for_file(p6_conn, file_id, content_hash) == []


def test_a03s_zip_code_produces_no_subject_fact(p6_conn, tmp_path):
    # A03, `subject_ref: "A03::zip::course"`, `expected_outcome_kind: "abstained"`,
    # `forbidden_value: {"field": "course", "value": "MA 02139"}` -- read on the
    # stored key, which D6 fixes as `subject`. The pattern DOES match; the context
    # check is what refuses it, which is exactly §3.5's point.
    file_id, content_hash = _record(p6_conn, tmp_path, name="A03-zip.txt",
                                    body=b"Ship to Cambridge MA 02139 by Friday.")
    _observe(p6_conn, run_id="A03-zip", file_id=file_id, content_hash=content_hash,
             raw="MA 02139", zone="body", context_before="Ship to Cambridge ",
             context_after=" by Friday.")
    assert COURSE_CODE.search("MA 02139") is not None
    assert apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                       rules=(_course_rule(),)) == ()
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    assert [r["reason"] for r in unresolved_for_file(
        p6_conn, file_id, content_hash)] == ["context_check_failed"]


def test_a03s_device_model_produces_no_subject_fact(p6_conn, tmp_path):
    # A03's second subject: `{"field": "course", "value": "XPS 13"}`.
    file_id, content_hash = _record(p6_conn, tmp_path, name="A03-device.txt",
                                    body=b"Receipt for one XPS 13 laptop.")
    _observe(p6_conn, run_id="A03-device", file_id=file_id,
             content_hash=content_hash, raw="XPS 13", zone="body",
             context_before="Receipt for one ", context_after=" laptop.")
    assert COURSE_CODE.search("XPS 13") is not None
    assert apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                       rules=(_course_rule(),)) == ()
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    assert [r["reason"] for r in unresolved_for_file(
        p6_conn, file_id, content_hash)] == ["context_check_failed"]


def test_rules_do_not_read_another_versions_observations(p6_conn, tmp_path):
    # The abstention and the fact are both per file VERSION (§3.4, §8.2), so the read
    # filters on content hash and a prior version's evidence cannot resolve this one.
    file_id, content_hash = _record(p6_conn, tmp_path, name="v1.pdf", body=b"one")
    _observe(p6_conn, run_id="r-old", file_id=file_id, content_hash=content_hash,
             raw="BUSIB 4300", context_before="Syllabus — ")
    other_hash = "f" * 64
    _run(p6_conn, run_id="r-other", file_id=file_id, content_hash=other_hash)
    record_observation(p6_conn, Observation(
        file_id=file_id, content_hash=other_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document",
        raw_value="ECON 1001", location=Location("heading", (Segment("page", 1),)),
        occurrence_count=1, observed_at=CLOCK, reliability="possible",
        run_id="r-other", context_before="Syllabus — "))
    apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                rules=(_course_rule(),))
    values = {r["canonical_value"]
              for r in facts_for_file(p6_conn, file_id, content_hash)}
    assert values == {"BUSIB 4300"}


def test_the_outcome_does_not_depend_on_p4s_insertion_order(p6_conn, tmp_path):
    # `observations_for_file` orders by rowid. Two observations, written in either
    # order, must produce the same two facts.
    def resolve(order):
        file_id, content_hash = _record(
            p6_conn, tmp_path, name=f"order-{'-'.join(order)}.pdf", body=b"x")
        for index, raw in enumerate(order):
            _observe(p6_conn, run_id=f"o{index}-{raw}", file_id=file_id,
                     content_hash=content_hash, raw=raw,
                     context_before="Syllabus — ")
        apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                    rules=(_course_rule(),))
        return sorted(r["canonical_value"]
                      for r in facts_for_file(p6_conn, file_id, content_hash))

    assert resolve(("BUSIB 4300", "ECON 1001")) == \
        resolve(("ECON 1001", "BUSIB 4300")) == ["BUSIB 4300", "ECON 1001"]


def test_several_rules_over_one_observation_each_write_their_own_row(
        p6_conn, tmp_path):
    # One rule fills, one refuses. The two outcomes are independent and neither
    # suppresses the other.
    file_id, content_hash = _record(p6_conn, tmp_path, name="two.pdf", body=b"two")
    _observe(p6_conn, run_id="r-two", file_id=file_id, content_hash=content_hash,
             raw="BUSIB 4300", context_before="Syllabus — ")
    venue_rule = Rule(pattern=COURSE_CODE,
                      required_context_terms=("proceedings", "conference"),
                      field_key="venue")
    apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                rules=(_course_rule(), venue_rule))
    assert [r["field_key"] for r in facts_for_file(
        p6_conn, file_id, content_hash)] == ["subject"]
    assert [(r["field_key"], r["reason"]) for r in unresolved_for_file(
        p6_conn, file_id, content_hash)] == [("venue", "context_check_failed")]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p6/test_p6_rules.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'facts.rules'`
(if it instead fails with `No module named 'facts.facets'`, Task 11 has not been executed yet — see
the ordering edge above)

- [ ] **Step 3: Write the implementation**

```python
# src/facts/rules.py
"""§3.5 rule-validated facts: a pattern match PLUS a strict context check.

§3.5, verbatim and load-bearing: *"Rules create validated facts when a candidate
passes strict context checks. For example, BUSIB 4300 becomes a course fact only when
the engine finds a course-code pattern together with academic context such as
"syllabus," "lecture," "credits," "instructor," or "semester.""*

Five terms are stated literally and they are the only context vocabulary this module
authors. Every other domain's terms arrive on the `Rule`, because the SPEC defers
them: *"Rule context-term lists beyond the five literal academic terms | §3.5 | Only
"syllabus", "lecture", "credits", "instructor", "semester" are stated. Every other
domain's context vocabulary is unauthored."* There is no sixth term here and adding
one is a design change, not an implementation detail.

**The check is case-insensitive (N-6).** §3.5 writes its five terms in lowercase and
states no matching rule, so P6 states one. P4's fixture 1 carries `context_before`
exactly `"Syllabus - "` with a capital S, and B8(a)'s whole purpose was to make the
walking skeleton's one fact resolvable; a case-sensitive reading refuses that fixture
and the skeleton produces no fact at all.

**Case-insensitivity does not relax the word boundary.** The matcher is
`facts.facets.word_boundary_match`, the same one §3.7's facet values go through, so
`semester` still cannot match inside a longer word. One rule, one implementation.

**A truncated context is not a clean refusal.** §8.6 forbids silent truncation, so a
check that fails on a record with `context_truncated = true` writes
`reason = context_truncated` and never `context_check_failed`: the term may have been
cut off, and reporting a considered refusal would be a claim this module cannot make.
"""
from __future__ import annotations

import re
import sqlite3
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from evidence_shape.canonical import canonical_json
from evidence_shape.vocabulary import ANALYSIS_TIERS

from facts.cache import fact_cache_key
from facts.evidence import (
    analysis_tier_for_observation, cite, context_pair, observations_for_version,
)
from facts.facets import word_boundary_match
from facts.file_facts import FACT_ORIGINS, write_fact, RULE
from facts.states import STATES, VALIDATED
from facts.unresolved import ATTEMPTED_PRODUCERS, write_unresolved
from facts.values import VALUE_ORIGINS, ensure_value

#: §3.5's five academic context terms, quoted from the design and complete. This is
#: the ONLY context vocabulary `facts` authors; everything else is injected on a
#: `Rule`. A sixth term is a design change.
ACADEMIC_CONTEXT_TERMS: tuple[str, str, str, str, str] = (
    "syllabus", "lecture", "credits", "instructor", "semester")

#: Task 1 owns the spelling. Never an index into STATES.
_VALIDATED = VALIDATED


class MalformedRule(ValueError):
    """A rule with no pattern, no context term, or no field. §3.5 requires all three."""


@dataclass(frozen=True, slots=True)
class Rule:
    """One injected §3.5 rule: a pattern, the context it demands, and the field it fills.

    Every one of the three is caller-supplied. `facts.rules` authors no course-code
    regex (§3.10's catalogue beyond the three named date patterns is Deferred and a
    course-code pattern is not among them), and it authors no field key -- D6 fixes
    the academic key as `subject`, and a module that spelled it would be a second home
    for `fields`.
    """

    pattern: re.Pattern[str]
    required_context_terms: tuple[str, ...]
    field_key: str

    def __post_init__(self) -> None:
        if not isinstance(self.pattern, re.Pattern):
            raise MalformedRule("a rule matches a compiled pattern, never a string: "
                                "§3.10 requires explicit regular expressions")
        if not self.required_context_terms:
            raise MalformedRule(
                f"rule for {self.field_key!r} demands no context term; §3.5's whole "
                "point is that a pattern match alone is not a fact")
        if not self.field_key:
            raise MalformedRule("a rule names the field it fills")


def context_check(before: str, after: str, terms: Iterable[str]) -> bool:
    """True when any required term appears in either half of §2.8's context pair.

    The two halves are read together and never concatenated (M5): P4 split them so
    §8.4 can redact a value without dropping its context, and joining them here would
    forge an adjacency that the document does not contain.
    """
    haystacks = (before or "", after or "")
    return any(word_boundary_match(term, haystack)
               for term in terms for haystack in haystacks)


def _pass_cache_key(conn: sqlite3.Connection, *, file_id: str,
                    content_hash: str) -> str:
    """§3.4's key for one deterministic pass over one file version.

    Written out here rather than imported from a producer sibling: the SPEC requires
    an `unresolved` row to carry the "same composition as `file_facts` (§3.4), so an
    abstention is invalidated by the same events that invalidate a fact", and the
    reconciliation of several extractor versions into one key belongs to `facts.cache`
    (Task 6), which does not own it yet. See the plan's contract ambiguities.
    """
    observations = observations_for_version(conn, file_id, content_hash)
    pairs = sorted({(o.extractor_name, o.extractor_version) for o in observations})
    tiers = {analysis_tier_for_observation(conn, o) for o in observations}
    present = [tier for tier in ANALYSIS_TIERS if tier in tiers]
    if not present:
        raise ValueError(
            f"no extraction run for {content_hash!r}: §3.4's key has no analysis tier")
    return fact_cache_key(
        content_hash=content_hash,
        extractor_version=canonical_json([list(pair) for pair in pairs]),
        analysis_tier=present[-1], model_identifier=None, prompt_fingerprint=None)


def apply_rules(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                rules: Sequence[Rule]) -> tuple[str, ...]:
    """Run every rule over every observation of one file version.

    Three outcomes and they are not interchangeable:

    * the pattern does not match -- nothing at all. A rule that does not apply is not
      a refusal, and writing one would fill `unresolved` with every field every rule
      could theoretically have produced;
    * the pattern matches and the context check passes -- one `validated` fact citing
      that observation's key (M14);
    * the pattern matches and the context check fails -- one `unresolved` row, whose
      reason is `context_truncated` when P4 flagged the context as cut and
      `context_check_failed` when it did not.
    """
    written: list[str] = []
    observations = sorted(observations_for_version(conn, file_id, content_hash),
                          key=lambda o: o.observation_key)
    for observation in observations:
        before, after, truncated = context_pair(observation)
        for rule in rules:
            match = rule.pattern.search(observation.raw_value)
            if match is None:
                continue
            if not context_check(before, after, rule.required_context_terms):
                write_unresolved(
                    conn, file_id=file_id, content_hash=content_hash,
                    field_key=rule.field_key,
                    reason="context_truncated" if truncated else "context_check_failed",
                    attempted_producers=(ATTEMPTED_PRODUCERS[1],),
                    evidence_refs=(cite(observation),),
                    cache_key=_pass_cache_key(conn, file_id=file_id,
                                              content_hash=content_hash))
                continue
            value_id = ensure_value(conn, field_key=rule.field_key,
                                    canonical_value=match.group(0),
                                    first_evidence_ref=cite(observation),
                                    origin=VALUE_ORIGINS[0])
            written.append(write_fact(
                conn, file_id=file_id, content_hash=content_hash,
                field_key=rule.field_key, value_id=value_id,
                reliability_state=_VALIDATED, origin=RULE,
                evidence_refs=(cite(observation),),
                cache_key=_pass_cache_key(conn, file_id=file_id,
                                          content_hash=content_hash),
                active=True))
    return tuple(written)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p6/test_p6_rules.py -v`
Expected: PASS — 20 passed

- [ ] **Step 5: Commit**

```bash
git add src/facts/rules.py tests/p6/test_p6_rules.py
git commit -m "feat(P6): §3.5 rule-validated facts — a pattern match plus a strict context check"
```

---

### Task 11: §3.7 facet ranking — word boundary, positional weight, score and margin

**Files:**
- Create: `src/facts/facets.py`
- Test: `tests/p6/test_p6_facets.py`

**Interfaces:**
- Consumes: `facts.evidence` — `observations_for_version`, `analysis_tier_for_observation`;
  `facts.file_facts` — `write_fact`, `FACT_ORIGINS`; `facts.unresolved` — `write_unresolved`,
  `ATTEMPTED_PRODUCERS`; `facts.values` — `ensure_value`, `VALUE_ORIGINS`; `facts.states.STATES`;
  `facts.cache.fact_cache_key`; `evidence_shape.canonical.canonical_json`;
  `evidence_shape.vocabulary` — `ANALYSIS_TIERS`, `ZONES`.
- Produces: `MissingWeight`, `Candidate(value, score, evidence_refs, zone=None, signal_tier=None)`,
  `word_boundary_match(needle, haystack) -> bool`,
  `rank(candidates, *, zone_weight, tier_weight) -> tuple[Candidate, ...]`,
  `fill_or_abstain(conn, *, file_id, content_hash, field_key, candidates, minimum_score,
  minimum_margin) -> str | None` — every threshold and weight a required keyword with no default.

**Done-means:** 7, 9.

**§3.7 in its own words, and this module is all four clauses of it:** *"It should use word-boundary
matching rather than substring matching. Without this rule, names such as MIT can be found inside
"submit," and UNC can be found inside "uncertainty," producing polished but completely false filing
paths. It should use positional weighting because a value in a filename or document title carries
more meaning than the same value in a footer or a late body-page reference. It should rank candidate
matches instead of accepting the first match, and it should require both a minimum score and a
minimum margin over the second-best candidate before it fills a facet."*

**Why the matcher is hand-rolled rather than `\b`.** `\b` is defined against a word character on
*both* sides, which is wrong for a needle whose own first or last character is not one — `C++`,
`PVA/RDP`, `AY 2024-25` are all real facet values and all would be mis-bounded. And the needle is
`re.escape`d before it is searched for: a gazetteer entry is **data**, and a catalogue row compiled
as syntax would let `a+` match `aaaa` and one row match the whole corpus. The boundary is therefore
tested per edge: a word character at the edge of the needle demands a non-word character (or the end
of the string) beside it, and a non-word character at the edge demands nothing.

**Case is folded, and A01 and A02 still fail.** N-6 requires the §3.5 context check to be
case-insensitive and Task 10 shares this matcher, so folding case here is what keeps the rule in one
place. It costs nothing: `mit` inside `submit` and `unc` inside `uncertainty` are both refused by
the boundary, not by case, which is the assertion `test_case_folding_does_not_relax_the_boundary`
makes explicit so a later reader cannot mistake it for luck.

**`Candidate` carries two descriptors beyond the published three.** The skeleton fixes
`Candidate(value, score, evidence_refs)` and `rank(candidates, *, zone_weight, tier_weight)` — but a
weight map has nothing to weight unless the contribution says which zone and which signal tier it
came from. So `zone` and `signal_tier` follow the three, defaulted to `None`, carrying P4's
`location.zone` and P4's integer `signal_tier` unchanged. `rank` clears both on what it returns: a
ranked candidate aggregates several positions and a single zone on it would be a claim about where
it came from that is not true. This is an addition to the skeleton's shape and is listed under
*Contract ambiguities*.

**A null `signal_tier` is not a band.** P4's conformance rule 11 ties a non-null `signal_tier` to
`source_type == "image"`, so most observations have none. `rank` applies no tier factor at all in
that case — not a default weight. §2.6 is the reason and it is unconditional: *"the system must not
mistake the absence of EXIF for proof that an image is a screenshot."* A missing signal contributes
nothing to either candidate; it does not contribute a middling amount.

**Every weight and threshold is required, and an unweighted zone raises.** The SPEC defers
*"Minimum score and minimum margin values"*, *"Positional weight per document zone"* and
*"Signal-tier weights for §2.6's three bands"*. `MissingWeight` is what a zone with no injected
weight produces — a fallback weight would answer a Deferred question silently, which is the failure
mode this plan exists to avoid.

**The total order is this module's, and it is imposed twice.** `evidence_shape.store` reads in
`rowid` order, which is insertion order — verified by execution — and insertion order is a property
of one database, not of the corpus. `rank` sorts by (weighted score descending, smallest cited
observation key ascending, value ascending) and `fill_or_abstain` applies the same key again to its
own input, so a caller that hands the candidates over reversed gets the same fact. Without it a tie
is decided by whichever run was written first and §8.5's replay reports a regression when nothing
changed.

**Three refusals, not one.** `no_candidate_evidence` when nothing was offered,
`below_score_threshold` when the winner is under the floor, `below_margin` when the winner is too
close to the runner-up. §8.5 asks under Fact quality *"Did it abstain when evidence was absent?"* and
a single merged reason cannot answer it — absent evidence and contested evidence are different
events with different fixes.

**The state is `validated` and the signature has no room to say otherwise.** §3.13: a `validated`
fact *"was found by a deterministic rule and passed contextual checks"*, and clearing a minimum score
and a minimum margin over ranked candidates is that check. Nothing here writes `direct` — no explicit
slot states a ranked facet — and nothing here writes `possible`.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_facets.py
"""§3.7 -- Done-means 7 and 9, adversarial cases A01 and A02."""
import itertools
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from evidence_shape.vocabulary import ZONES

from facts.facets import (
    Candidate, MissingWeight, fill_or_abstain, rank, word_boundary_match,
)
from facts.file_facts import facts_for_file
from facts.unresolved import unresolved_for_file

CLOCK = "2026-08-22T00:00:00Z"

#: §3.7's weights are Deferred -- "Positional weight per document zone | §3.7, §2.2 |
#: Zones arrive from P4's `location`; the weights are manual." These are the test's
#: own, injected at every call, and they exist nowhere in `src/facts`.
ZONE_WEIGHT = {"filename": 3.0, "title": 3.0, "heading": 2.0, "body": 1.0,
               "header_footer": 0.25, "metadata": 1.0, "path": 1.0, "table": 1.0,
               "notes": 1.0, "link": 1.0, "annotation": 1.0, "reference_list": 0.5,
               "manifest": 1.0, "ocr": 1.0, "transcript": 1.0}
TIER_WEIGHT = {1: 4.0, 2: 2.0, 3: 1.0}


def _record(conn, tmp_path, *, name, body):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="text/plain",
        detected_format="txt", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, zone, occurrence_count=1,
             signal_tier=None, source_type="text_document", analysis_tier="native"):
    if conn.execute("SELECT 1 FROM extraction_runs WHERE run_id = ?",
                    (run_id,)).fetchone() is None:
        record_run(conn, ExtractionRun(
            run_id=run_id, file_id=file_id, content_hash=content_hash,
            extractor_name="text.plain", extractor_version="1.0.0",
            source_type=source_type, analysis_tier=analysis_tier, config={},
            completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="text.plain",
        extractor_version="1.0.0", source_type=source_type, raw_value=raw,
        location=Location(zone, (Segment("page", 1),)),
        occurrence_count=occurrence_count, observed_at=CLOCK,
        reliability="possible", run_id=run_id, signal_tier=signal_tier)
    record_observation(conn, observation)
    return observation


def _candidate(observation, value, score=1.0):
    return Candidate(value=value, score=score,
                     evidence_refs=(observation.observation_key,),
                     zone=observation.location.zone,
                     signal_tier=observation.signal_tier)


# --- the word-boundary rule, which is the whole of A01 and A02 -----------------

def test_mit_is_not_found_inside_submit():
    # §3.7, verbatim: "names such as MIT can be found inside "submit,"" -- and A01
    # carries that exact sentence as `Please submit the completed form.`
    assert word_boundary_match("MIT", "Please submit the completed form.") is False


def test_unc_is_not_found_inside_uncertainty():
    # §3.7's second named case; A02's text unit verbatim.
    assert word_boundary_match(
        "UNC", "Measurement uncertainty dominates the result.") is False


def test_the_same_needles_do_match_when_they_stand_alone():
    # The refusal has to be a boundary rule and not a blanket "never match", or the
    # facet could never be filled at all.
    assert word_boundary_match("MIT", "Accepted to MIT this spring.") is True
    assert word_boundary_match("UNC", "UNC Chapel Hill, 2024") is True
    assert word_boundary_match("MIT", "MIT") is True


def test_case_folding_does_not_relax_the_boundary():
    # N-6 makes the §3.5 context check case-insensitive and it shares this matcher.
    # If folding case turned the rule into a substring rule, A01 and A02 would both
    # start passing, so this is the assertion that keeps N-6 safe.
    for haystack in ("Please SUBMIT the form.", "please submit the form.",
                     "Submit the form."):
        assert word_boundary_match("mit", haystack) is False
    assert word_boundary_match("syllabus", "Syllabus — ") is True
    assert word_boundary_match("SYLLABUS", "syllabus — ") is True


def test_a_needle_whose_edges_are_not_word_characters_still_bounds_correctly():
    # `\b` is defined against a word character on both sides and would be wrong here;
    # the matcher tests the boundary per edge instead.
    assert word_boundary_match("PVA/RDP", "the PVA/RDP abstract") is True
    assert word_boundary_match("AY 2024-25", "Calendar AY 2024-25 published") is True
    assert word_boundary_match("C++", "written in C++ and Rust") is True


def test_the_needle_is_never_compiled_as_a_pattern():
    # A gazetteer entry is data, not syntax. `.` must match a full stop and nothing
    # else, or one catalogue row would match every file in the corpus.
    assert word_boundary_match("M.I.T", "MXIXT") is False
    assert word_boundary_match("a+", "aaaa") is False


def test_an_empty_needle_or_haystack_matches_nothing():
    assert word_boundary_match("", "anything") is False
    assert word_boundary_match("MIT", "") is False


# --- ranking: never first-match, and never P4's read order --------------------

def test_ranking_is_over_all_candidates_and_never_the_first_match(p6_conn, tmp_path):
    # §3.7: "It should rank candidate matches instead of accepting the first match."
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    footer = _observe(p6_conn, run_id="r1", file_id=file_id,
                      content_hash=content_hash, raw="Duke", zone="header_footer")
    title = _observe(p6_conn, run_id="r1", file_id=file_id,
                     content_hash=content_hash, raw="Columbia", zone="title")
    ranked = rank([_candidate(footer, "Duke"), _candidate(title, "Columbia")],
                  zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    assert [c.value for c in ranked] == ["Columbia", "Duke"]


def test_a_title_outranks_a_footer_and_a_late_body_page(p6_conn, tmp_path):
    # §3.7: "a value in a filename or document title carries more meaning than the
    # same value in a footer or a late body-page reference."
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    in_title = _observe(p6_conn, run_id="r1", file_id=file_id,
                        content_hash=content_hash, raw="Columbia", zone="title")
    in_footer = _observe(p6_conn, run_id="r1", file_id=file_id,
                         content_hash=content_hash, raw="Columbia",
                         zone="header_footer")
    weighted = rank([_candidate(in_footer, "Columbia")], zone_weight=ZONE_WEIGHT,
                    tier_weight=TIER_WEIGHT)[0].score
    stronger = rank([_candidate(in_title, "Columbia")], zone_weight=ZONE_WEIGHT,
                    tier_weight=TIER_WEIGHT)[0].score
    assert stronger > weighted


def test_contributions_for_one_value_are_summed_and_their_refs_merged(
        p6_conn, tmp_path):
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    first = _observe(p6_conn, run_id="r1", file_id=file_id,
                     content_hash=content_hash, raw="Columbia", zone="body")
    second = _observe(p6_conn, run_id="r1", file_id=file_id,
                      content_hash=content_hash, raw="Columbia College",
                      zone="heading")
    ranked = rank([_candidate(first, "Columbia"), _candidate(second, "Columbia")],
                  zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    assert len(ranked) == 1
    assert ranked[0].score == pytest.approx(3.0)
    assert ranked[0].evidence_refs == tuple(sorted(
        (first.observation_key, second.observation_key)))


def test_the_result_does_not_depend_on_p4s_read_order(p6_conn, tmp_path):
    # `observations_for_file` orders by rowid, which is insertion order and not a
    # property of the corpus. Every permutation must produce the same ranking or
    # §8.5's replay compares a run against itself and reports a regression.
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    made = [
        _candidate(_observe(p6_conn, run_id="r1", file_id=file_id,
                            content_hash=content_hash, raw=raw, zone=zone), value)
        for raw, zone, value in (("Columbia", "title", "Columbia"),
                                 ("Duke", "body", "Duke"),
                                 ("Yale", "header_footer", "Yale"),
                                 ("Duke again", "heading", "Duke"))]
    expected = rank(made, zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    for permutation in itertools.permutations(made):
        assert rank(permutation, zone_weight=ZONE_WEIGHT,
                    tier_weight=TIER_WEIGHT) == expected


def test_a_tie_is_broken_by_the_observation_key_and_not_by_insertion_order(
        p6_conn, tmp_path):
    # The case that actually bites: two candidates with identical weighted scores.
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    left = _candidate(_observe(p6_conn, run_id="r1", file_id=file_id,
                               content_hash=content_hash, raw="Duke", zone="body"),
                      "Duke")
    right = _candidate(_observe(p6_conn, run_id="r1", file_id=file_id,
                                content_hash=content_hash, raw="Yale", zone="body"),
                       "Yale")
    forward = rank([left, right], zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    backward = rank([right, left], zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    assert forward == backward
    assert forward[0].score == forward[1].score
    assert forward[0].evidence_refs[0] < forward[1].evidence_refs[0]


def test_a_signal_tier_weights_the_contribution_and_absence_of_one_does_not(
        p6_conn, tmp_path):
    # §2.6, and M2: P6 consumes P4's integer tier and never re-derives it. A null
    # tier is not a band -- "the system must not mistake the absence of EXIF for
    # proof that an image is a screenshot."
    file_id, content_hash = _record(p6_conn, tmp_path, name="photo.jpg", body=b"px")
    tier_one = _observe(p6_conn, run_id="r1", file_id=file_id,
                        content_hash=content_hash, raw="Canon EOS R6",
                        zone="metadata", signal_tier=1, source_type="image")
    untiered = _observe(p6_conn, run_id="r1", file_id=file_id,
                        content_hash=content_hash, raw="Canon EOS R5",
                        zone="metadata", source_type="image")
    assert rank([_candidate(tier_one, "photograph")], zone_weight=ZONE_WEIGHT,
                tier_weight=TIER_WEIGHT)[0].score == pytest.approx(4.0)
    assert rank([_candidate(untiered, "photograph")], zone_weight=ZONE_WEIGHT,
                tier_weight=TIER_WEIGHT)[0].score == pytest.approx(1.0)


def test_an_unweighted_zone_or_tier_raises_rather_than_defaulting(p6_conn, tmp_path):
    # No default weight exists anywhere: §3.7's numbers are Deferred and a fallback
    # would answer them silently.
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    observation = _observe(p6_conn, run_id="r1", file_id=file_id,
                           content_hash=content_hash, raw="Columbia", zone="title")
    with pytest.raises(MissingWeight):
        rank([_candidate(observation, "Columbia")], zone_weight={},
             tier_weight=TIER_WEIGHT)
    with pytest.raises(MissingWeight):
        rank([Candidate(value="Columbia", score=1.0, evidence_refs=("sha256:a",))],
             zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    tiered = _observe(p6_conn, run_id="r1", file_id=file_id,
                      content_hash=content_hash, raw="Canon", zone="metadata",
                      signal_tier=2, source_type="image")
    with pytest.raises(MissingWeight):
        rank([_candidate(tiered, "photograph")], zone_weight=ZONE_WEIGHT,
             tier_weight={})


def test_every_p4_zone_is_weightable_because_the_map_is_the_callers(p6_conn):
    # The map is over P4's fifteen zones; P6 states which zones exist nowhere.
    assert set(ZONE_WEIGHT) == set(ZONES)


# --- the two thresholds, and the three different refusals ---------------------

def test_a_clear_winner_fills_the_facet_as_validated(p6_conn, tmp_path):
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    title = _observe(p6_conn, run_id="r1", file_id=file_id,
                     content_hash=content_hash, raw="Columbia", zone="title")
    footer = _observe(p6_conn, run_id="r1", file_id=file_id,
                      content_hash=content_hash, raw="Duke", zone="header_footer")
    ranked = rank([_candidate(title, "Columbia"), _candidate(footer, "Duke")],
                  zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    fact_id = fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                              field_key="school", candidates=ranked,
                              minimum_score=1.0, minimum_margin=1.0)
    assert fact_id is not None
    rows = [r for r in facts_for_file(p6_conn, file_id, content_hash)
            if r["field_key"] == "school"]
    assert [(r["canonical_value"], r["reliability_state"]) for r in rows] == \
        [("Columbia", "validated")]
    assert unresolved_for_file(p6_conn, file_id, content_hash) == []


def test_two_candidates_within_the_margin_fill_nothing(p6_conn, tmp_path):
    # Done-means 9, and §3.7's "minimum margin over the second-best candidate".
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    left = _observe(p6_conn, run_id="r1", file_id=file_id,
                    content_hash=content_hash, raw="Columbia", zone="heading")
    right = _observe(p6_conn, run_id="r1", file_id=file_id,
                     content_hash=content_hash, raw="Duke", zone="heading")
    ranked = rank([_candidate(left, "Columbia"), _candidate(right, "Duke")],
                  zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    assert fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                           field_key="school", candidates=ranked,
                           minimum_score=1.0, minimum_margin=1.0) is None
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    rows = unresolved_for_file(p6_conn, file_id, content_hash, field_key="school")
    assert [r["reason"] for r in rows] == ["below_margin"]
    assert json.loads(rows[0]["evidence_refs"]) == sorted(
        (left.observation_key, right.observation_key))


def test_failing_the_minimum_score_is_a_different_refusal_from_the_margin(
        p6_conn, tmp_path):
    # Two thresholds, two reasons. §8.5 asks "Did it abstain when evidence was
    # absent?" and one merged reason cannot answer it.
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    footer = _observe(p6_conn, run_id="r1", file_id=file_id,
                      content_hash=content_hash, raw="Columbia",
                      zone="header_footer")
    ranked = rank([_candidate(footer, "Columbia")], zone_weight=ZONE_WEIGHT,
                  tier_weight=TIER_WEIGHT)
    assert fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                           field_key="school", candidates=ranked,
                           minimum_score=1.0, minimum_margin=0.1) is None
    rows = unresolved_for_file(p6_conn, file_id, content_hash, field_key="school")
    assert [r["reason"] for r in rows] == ["below_score_threshold"]


def test_no_candidate_at_all_is_a_third_refusal(p6_conn, tmp_path):
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    _observe(p6_conn, run_id="r1", file_id=file_id, content_hash=content_hash,
             raw="nothing relevant", zone="body")
    assert fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                           field_key="school", candidates=(),
                           minimum_score=1.0, minimum_margin=1.0) is None
    rows = unresolved_for_file(p6_conn, file_id, content_hash, field_key="school")
    assert [r["reason"] for r in rows] == ["no_candidate_evidence"]
    assert json.loads(rows[0]["evidence_refs"]) == []


def test_a_lone_candidate_clears_the_margin_because_there_is_no_second_best(
        p6_conn, tmp_path):
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    title = _observe(p6_conn, run_id="r1", file_id=file_id,
                     content_hash=content_hash, raw="Columbia", zone="title")
    ranked = rank([_candidate(title, "Columbia")], zone_weight=ZONE_WEIGHT,
                  tier_weight=TIER_WEIGHT)
    assert fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                           field_key="school", candidates=ranked,
                           minimum_score=1.0, minimum_margin=1.0) is not None


def test_fill_or_abstain_re_imposes_the_order_on_its_own_input(p6_conn, tmp_path):
    # A caller that hands the candidates over in the wrong order must not change the
    # outcome: `rank` orders, and `fill_or_abstain` orders again before it looks at
    # the first element.
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    title = _observe(p6_conn, run_id="r1", file_id=file_id,
                     content_hash=content_hash, raw="Columbia", zone="title")
    footer = _observe(p6_conn, run_id="r1", file_id=file_id,
                      content_hash=content_hash, raw="Duke", zone="header_footer")
    ranked = rank([_candidate(title, "Columbia"), _candidate(footer, "Duke")],
                  zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                    field_key="school", candidates=tuple(reversed(ranked)),
                    minimum_score=1.0, minimum_margin=1.0)
    rows = [r for r in facts_for_file(p6_conn, file_id, content_hash)
            if r["field_key"] == "school"]
    assert [r["canonical_value"] for r in rows] == ["Columbia"]


def test_a01_and_a02_fill_nothing_end_to_end(p6_conn, tmp_path):
    # The two adversarial cases as built: `expected_outcome_kind: "abstained"`,
    # `forbidden_value: {"field": "school", "value": "MIT"}` / `"UNC"`. The gazetteer
    # is the test's, because §3.7's gazetteer contents are Deferred.
    gazetteer = ("MIT", "UNC", "Columbia")
    for name, text, forbidden in (("A01", "Please submit the completed form.", "MIT"),
                                  ("A02", "Measurement uncertainty dominates the "
                                          "result.", "UNC")):
        file_id, content_hash = _record(p6_conn, tmp_path, name=f"{name}.txt",
                                        body=text.encode())
        observation = _observe(p6_conn, run_id=f"{name}-run", file_id=file_id,
                               content_hash=content_hash, raw=text, zone="body")
        candidates = [_candidate(observation, entry) for entry in gazetteer
                      if word_boundary_match(entry, observation.raw_value)]
        assert candidates == []
        assert fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                               field_key="school",
                               candidates=rank(candidates, zone_weight=ZONE_WEIGHT,
                                               tier_weight=TIER_WEIGHT),
                               minimum_score=1.0, minimum_margin=1.0) is None
        assert facts_for_file(p6_conn, file_id, content_hash) == []
        rows = unresolved_for_file(p6_conn, file_id, content_hash,
                                   field_key="school")
        assert [r["reason"] for r in rows] == ["no_candidate_evidence"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p6/test_p6_facets.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'facts.facets'`

- [ ] **Step 3: Write the implementation**

```python
# src/facts/facets.py
"""§3.7 conservative facet extraction: word boundary, positional weight, score, margin.

§3.7, verbatim and in its own order: *"It should use word-boundary matching rather
than substring matching. Without this rule, names such as MIT can be found inside
"submit," and UNC can be found inside "uncertainty," producing polished but
completely false filing paths. It should use positional weighting because a value in
a filename or document title carries more meaning than the same value in a footer or
a late body-page reference. It should rank candidate matches instead of accepting the
first match, and it should require both a minimum score and a minimum margin over the
second-best candidate before it fills a facet."*

Four obligations, and this module is all four:

1. word-boundary matching, never substring;
2. positional weighting off P4's `location.zone`;
3. ranked candidates, never first-match;
4. a minimum score AND a minimum margin, both cleared, before a facet is filled.

**Every weight and every threshold is a required keyword with no default.** §3.7's
numbers are Deferred -- the SPEC's own table lists "Minimum score and minimum margin
values", "Positional weight per document zone" and "Signal-tier weights for §2.6's
three bands" as manual work. A default here would answer them.

**The total order is this module's, not P4's.** `observations_for_file` orders by
rowid, which is insertion order and is not a property of the corpus. `rank` therefore
sorts by (weighted score descending, smallest cited observation key ascending, value
ascending) before anything looks at the first element, and `fill_or_abstain` applies
the same order again to its own input. Without that, a tie is decided by whichever
run happened to be written first and §8.5's replay reports a regression when nothing
changed.
"""
from __future__ import annotations

import re
import sqlite3
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from evidence_shape.canonical import canonical_json
from evidence_shape.vocabulary import ANALYSIS_TIERS

from facts.cache import fact_cache_key
from facts.evidence import (
    analysis_tier_for_observation, observations_for_version,
)
from facts.file_facts import FACT_ORIGINS, write_fact, RULE
from facts.states import STATES, VALIDATED
from facts.unresolved import ATTEMPTED_PRODUCERS, write_unresolved
from facts.values import VALUE_ORIGINS, ensure_value


#: §3.13's third state. Rule 2: the six literals are P4's and P6 re-spells none of
#: them, so every state in this module is addressed by its index into P4's tuple.
_VALIDATED = VALIDATED


class MissingWeight(KeyError):
    """A zone or signal tier with no injected weight. P6 invents no number."""


@dataclass(frozen=True, slots=True)
class Candidate:
    """One candidate value for one field.

    `value`, `score` and `evidence_refs` are the published three. `zone` and
    `signal_tier` are the two P4 descriptors `rank` weights by; they are present on a
    contribution (one candidate from one observation) and cleared on the aggregate
    `rank` returns, because a ranked candidate spans several positions and a single
    zone would be a lie about where it came from.
    """

    value: str
    score: float
    evidence_refs: tuple[str, ...]
    zone: str | None = None
    signal_tier: int | None = None


def _is_word_character(character: str) -> bool:
    return character.isalnum() or character == "_"


def word_boundary_match(needle: str, haystack: str) -> bool:
    """True when `needle` occurs in `haystack` bounded by non-word characters.

    §3.7's own two cases are the specification: `MIT` must not match inside "submit"
    and `UNC` must not match inside "uncertainty". Both are decided by the boundary
    and not by case, which is why folding case (N-6, required for the §3.5 context
    check that shares this matcher) does not weaken either refusal.

    `re.escape` is applied to the needle: facet values contain `/`, `-`, `+` and `.`
    (`PVA/RDP`, `AY 2024-25`, `C++`), and a needle compiled as a pattern would make
    the value catalogue an injection surface. `\\b` is not used either -- it is
    defined against a word character on both sides, which is wrong for a needle whose
    own first or last character is not one.
    """
    if not needle or not haystack:
        return False
    for match in re.finditer(re.escape(needle), haystack, flags=re.IGNORECASE):
        start, end = match.start(), match.end()
        if _is_word_character(haystack[start]) and start > 0 \
                and _is_word_character(haystack[start - 1]):
            continue
        if _is_word_character(haystack[end - 1]) and end < len(haystack) \
                and _is_word_character(haystack[end]):
            continue
        return True
    return False


def _weight_of(candidate: Candidate, *, zone_weight: Mapping[str, float],
               tier_weight: Mapping[int, float]) -> float:
    if candidate.zone is None:
        raise MissingWeight(
            "a contribution carries P4's location.zone; §3.7's positional weighting "
            "has nothing to weight without it")
    try:
        weight = zone_weight[candidate.zone]
    except KeyError as exc:
        raise MissingWeight(f"no injected weight for zone {candidate.zone!r}") from exc
    if candidate.signal_tier is None:
        # §2.6 is image-scoped (P4 conformance rule 11 ties a non-null signal_tier to
        # source_type == "image"). No tier means the hierarchy does not apply, not
        # that some default band does -- absence is never evidence (§2.6).
        return candidate.score * weight
    try:
        return candidate.score * weight * tier_weight[candidate.signal_tier]
    except KeyError as exc:
        raise MissingWeight(
            f"no injected weight for signal tier {candidate.signal_tier!r}") from exc


def _order(candidate: Candidate) -> tuple[float, str, str]:
    refs = sorted(candidate.evidence_refs)
    return (-candidate.score, refs[0] if refs else "", candidate.value)


def rank(candidates: Iterable[Candidate], *, zone_weight: Mapping[str, float],
         tier_weight: Mapping[int, float]) -> tuple[Candidate, ...]:
    """Aggregate per-observation contributions into weighted, totally ordered candidates.

    Contributions for the same value are summed, so a value stated in a filename and
    again in a heading outranks one stated once in a footer -- which is §3.7's
    positional weighting, expressed as an injected map over P4's fifteen zones rather
    than as a number this module chose.
    """
    weighted: dict[str, float] = {}
    refs: dict[str, set[str]] = {}
    for candidate in candidates:
        score = _weight_of(candidate, zone_weight=zone_weight, tier_weight=tier_weight)
        weighted[candidate.value] = weighted.get(candidate.value, 0.0) + score
        refs.setdefault(candidate.value, set()).update(candidate.evidence_refs)
    aggregated = tuple(
        Candidate(value=value, score=weighted[value],
                  evidence_refs=tuple(sorted(refs[value])))
        for value in weighted)
    return tuple(sorted(aggregated, key=_order))


def _pass_cache_key(conn: sqlite3.Connection, *, file_id: str,
                    content_hash: str) -> str:
    """§3.4's key for one deterministic pass over one file version.

    The SPEC requires an `unresolved` row to carry the "same composition as
    `file_facts` (§3.4), so an abstention is invalidated by the same events that
    invalidate a fact" -- so the fill and the refusal computed by one pass share one
    key. `model_identifier` and `prompt_fingerprint` are None on every deterministic
    fact; P4's `sha256_of` is length-prefixed and injective, so None is
    distinguishable from "" in the digest.
    """
    observations = observations_for_version(conn, file_id, content_hash)
    pairs = sorted({(o.extractor_name, o.extractor_version) for o in observations})
    tiers = {analysis_tier_for_observation(conn, o) for o in observations}
    present = [tier for tier in ANALYSIS_TIERS if tier in tiers]
    if not present:
        raise ValueError(
            f"no extraction run for {content_hash!r}: §3.4's key has no analysis tier")
    return fact_cache_key(
        content_hash=content_hash,
        extractor_version=canonical_json([list(pair) for pair in pairs]),
        analysis_tier=present[-1], model_identifier=None, prompt_fingerprint=None)


def fill_or_abstain(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                    field_key: str, candidates: Iterable[Candidate],
                    minimum_score: float, minimum_margin: float) -> str | None:
    """Fill the facet, or write the refusal that says why it was not filled.

    Three different refusals, never one: no candidate at all is
    `no_candidate_evidence`; a winner under the floor is `below_score_threshold`; a
    winner too close to the runner-up is `below_margin`. §8.5 asks "Did it abstain
    when evidence was absent?" and a single reason cannot answer it.

    The state is `validated`: §3.13 defines it as "found by a deterministic rule and
    passed contextual checks", and clearing a minimum score and a minimum margin over
    ranked candidates is exactly that check. Nothing here produces `direct` -- no
    explicit slot states a ranked facet -- and nothing here produces `possible`.
    """
    ordered = tuple(sorted(candidates, key=_order))
    if not ordered:
        write_unresolved(conn, file_id=file_id, content_hash=content_hash,
                         field_key=field_key, reason="no_candidate_evidence",
                         attempted_producers=(ATTEMPTED_PRODUCERS[1],),
                         evidence_refs=(),
                         cache_key=_pass_cache_key(conn, file_id=file_id,
                                                   content_hash=content_hash))
        return None
    considered = tuple(sorted({ref for candidate in ordered
                               for ref in candidate.evidence_refs}))
    winner = ordered[0]
    if winner.score < minimum_score:
        write_unresolved(conn, file_id=file_id, content_hash=content_hash,
                         field_key=field_key, reason="below_score_threshold",
                         attempted_producers=(ATTEMPTED_PRODUCERS[1],),
                         evidence_refs=considered,
                         cache_key=_pass_cache_key(conn, file_id=file_id,
                                                   content_hash=content_hash))
        return None
    if len(ordered) > 1 and winner.score - ordered[1].score < minimum_margin:
        write_unresolved(conn, file_id=file_id, content_hash=content_hash,
                         field_key=field_key, reason="below_margin",
                         attempted_producers=(ATTEMPTED_PRODUCERS[1],),
                         evidence_refs=considered,
                         cache_key=_pass_cache_key(conn, file_id=file_id,
                                                   content_hash=content_hash))
        return None
    value_id = ensure_value(conn, field_key=field_key,
                            canonical_value=winner.value,
                            first_evidence_ref=winner.evidence_refs[0],
                            origin=VALUE_ORIGINS[0])
    return write_fact(conn, file_id=file_id, content_hash=content_hash,
                      field_key=field_key, value_id=value_id,
                      reliability_state=_VALIDATED, origin=RULE,
                      evidence_refs=winner.evidence_refs,
                      cache_key=_pass_cache_key(conn, file_id=file_id,
                                                content_hash=content_hash),
                      active=True)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p6/test_p6_facets.py -v`
Expected: PASS — 22 passed

- [ ] **Step 5: Commit**

```bash
git add src/facts/facets.py tests/p6/test_p6_facets.py
git commit -m "feat(P6): §3.7 facet ranking — word boundary, positional weight, score and margin"
```

---

### Task 12: §3.10 dates and academic terms — explicit patterns, no fuzzy parsing

**Files:**
- Create: `src/facts/dates.py`
- Test: `tests/p6/test_p6_dates.py`

**Interfaces:**
- Consumes: `facts.evidence.cite`; `facts.facets` — `Candidate`, `fill_or_abstain` (applied by the
  caller and by the tests, not imported into the producer's own path);
  `evidence_shape.observation.Observation`.
- Produces: `SEASON_YEAR: str`, `ACADEMIC_YEAR_RANGE: str`, `NAMED_TERM_YEAR: str`,
  `REQUIRED_PATTERN_IDS: tuple[str, str, str]`, `MissingRequiredPattern`, `NoPatternIdentity`,
  `DatePattern(pattern_id, pattern)`, `DatePatterns(patterns)` — an injected frozen dataclass of
  compiled patterns with the three named academic-term patterns required;
  `DateMatch(pattern_id, raw, value, evidence_ref, zone, signal_tier, occurrence_count)`;
  `date_matches(observation, *, patterns) -> tuple[DateMatch, ...]`;
  `date_candidates(observation, *, patterns) -> tuple[Candidate, ...]`;
  `parse_exact(raw, *, pattern_id) -> str`.

**Done-means:** 10.

**§3.10, verbatim, because every clause of it is a test below:** *"Date extraction should be
deliberately narrow. The product must not use fuzzy date parsing because file names and documents
frequently contain numbers that look like years but are course identifiers, version numbers, build
numbers, ZIP codes, or other unrelated values. Date candidates should be identified with explicit
regular expressions and then parsed without fuzzy matching. Academic terms such as Spring 2025, AY
2024-25, and Michaelmas Term 2024 require dedicated patterns rather than generic parsing."*

**`capture_date` is not this task's field, and it is not `capture_year` either.** Three fields are
in play across P6 and they are three: `creation_date` is §3.11's universal filesystem/document
timestamp; **`capture_date` is the EXIF-derived fact** — §3.2: *"an EXIF field called
DateTimeOriginal is raw metadata; capture date = 2026-07-17 is the file fact derived from it"* — and
it is **Task 8's**, a `direct` fact from an explicit slot; `capture_year` is §3.11's Photos
*destination dimension*. This task owns none of them. It owns the §3.5 contrast's other half:
*"Filesystem timestamps are direct; dates recovered from text or filenames are not, and take the
§3.10 path."* Everything reached from here is a ranked candidate, never a `direct` fact.

**The three ids are authored; not one character of regex is.** The SPEC defers *"Date and
academic-term regex catalogue beyond the three named patterns"*, and which seasons, which term names
and which numeric formats count is exactly that catalogue. So `facts.dates` publishes the three
**ids** the design's three worked cases correspond to — `season_year` for `Spring 2025`,
`academic_year_range` for `AY 2024-25`, `named_term_year` for `Michaelmas Term 2024` — validates that
a `DatePatterns` carries all three, and holds no `re.Pattern` of its own. A test asserts that by
runtime introspection: `[name for name, value in vars(module).items() if isinstance(value,
re.Pattern)] == []`.

**"Dedicated patterns rather than generic parsing" is asserted by identity, not by value.** A single
permissive expression could match all three strings and would satisfy a value-only test. `DateMatch`
therefore carries `pattern_id`, the test asserts that each of the three strings is claimed by its own
id, and a second test asserts that no one pattern claims another's case. `DateMatch` is an addition
to the skeleton's `Produces:` list — `Candidate` has no room for a pattern id and Done-means 10 wants
one — and `date_candidates` is the skeleton's function, unchanged, defined as this record projected
onto §3.7's shape. Listed under *Contract ambiguities*.

**There is no route to a value that a pattern did not claim.** `parse_exact` raises
`NoPatternIdentity` on an empty pattern id and on an empty span, so the fuzzy path is not a
discouraged branch, it is an absent one. And "then parsed without fuzzy matching" is taken at its
word: `parse_exact` collapses runs of whitespace and returns the matched text. No month table, no
locale, no two-digit-year expansion — those would be per-field normalizers, which the SPEC defers
under *"Per-field normalizers and alias tables"*.

**The look-alikes are the point.** `v2024`, `build 20240117`, A03's ZIP code
(`Ship to Cambridge MA 02139 by Friday.`), A03's device model (`Receipt for one XPS 13 laptop.`) and
a bare course identifier (`BUSIB 4300`) each produce no candidate, therefore no fact, therefore one
`unresolved` row with `reason = no_candidate_evidence` — Done-means 18's requirement that the
refusal be a record. A bare `2025` produces nothing either, which is the trap §3.10 exists to close.

**A date is ranked like any other facet and gets no exemption.** Two named terms in one raw value
produce two candidates that tie, and §3.7's margin refuses both — a test asserts `below_margin`
rather than a first-match fill.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_dates.py
"""§3.10 -- Done-means 10, and A03's ZIP code and device model as date candidates."""
import json
import re
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run

from facts.dates import (
    ACADEMIC_YEAR_RANGE, NAMED_TERM_YEAR, REQUIRED_PATTERN_IDS, SEASON_YEAR,
    DateMatch, DatePattern, DatePatterns, MissingRequiredPattern, NoPatternIdentity,
    date_candidates, date_matches, parse_exact,
)
from facts.facets import fill_or_abstain, rank
from facts.file_facts import facts_for_file
from facts.unresolved import unresolved_for_file

CLOCK = "2026-08-22T00:00:00Z"

#: §3.10's catalogue beyond the three named patterns is Deferred, so these three
#: expressions are the TEST's and live nowhere in `src/facts`. Each is dedicated to
#: exactly one of the design's three worked cases.
SPRING_2025 = DatePattern(
    pattern_id=SEASON_YEAR,
    pattern=re.compile(r"\b(?:Spring|Summer|Fall|Autumn|Winter) \d{4}\b"))
AY_2024_25 = DatePattern(
    pattern_id=ACADEMIC_YEAR_RANGE, pattern=re.compile(r"\bAY \d{4}-\d{2}\b"))
MICHAELMAS_TERM_2024 = DatePattern(
    pattern_id=NAMED_TERM_YEAR,
    pattern=re.compile(
        r"\b(?:Michaelmas|Hilary|Trinity|Lent|Easter) Term \d{4}\b"))
PATTERNS = DatePatterns(patterns=(SPRING_2025, AY_2024_25, MICHAELMAS_TERM_2024))

ZONE_WEIGHT = {"filename": 3.0, "title": 3.0, "heading": 2.0, "body": 1.0,
               "header_footer": 0.25, "metadata": 1.0, "path": 1.0, "table": 1.0,
               "notes": 1.0, "link": 1.0, "annotation": 1.0, "reference_list": 0.5,
               "manifest": 1.0, "ocr": 1.0, "transcript": 1.0}
TIER_WEIGHT = {1: 4.0, 2: 2.0, 3: 1.0}


def _record(conn, tmp_path, *, name, body):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Courses", mime_type="text/plain",
        detected_format="txt", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, zone="heading"):
    if conn.execute("SELECT 1 FROM extraction_runs WHERE run_id = ?",
                    (run_id,)).fetchone() is None:
        record_run(conn, ExtractionRun(
            run_id=run_id, file_id=file_id, content_hash=content_hash,
            extractor_name="pdf.text", extractor_version="1.0.0",
            source_type="text_document", analysis_tier="native", config={},
            completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location(zone, (Segment("page", 1),)), occurrence_count=1,
        observed_at=CLOCK, reliability="possible", run_id=run_id)
    record_observation(conn, observation)
    return observation


def _resolve(conn, tmp_path, *, name, raw, field_key="term"):
    file_id, content_hash = _record(conn, tmp_path, name=name, body=raw.encode())
    observation = _observe(conn, run_id=f"run-{name}", file_id=file_id,
                           content_hash=content_hash, raw=raw)
    candidates = date_candidates(observation, patterns=PATTERNS)
    fact_id = fill_or_abstain(
        conn, file_id=file_id, content_hash=content_hash, field_key=field_key,
        candidates=rank(candidates, zone_weight=ZONE_WEIGHT,
                        tier_weight=TIER_WEIGHT),
        minimum_score=1.0, minimum_margin=0.5)
    return file_id, content_hash, fact_id


# --- the three named patterns are required, dedicated, and identified --------

def test_the_three_named_academic_term_patterns_are_required():
    # §3.10: "Academic terms such as Spring 2025, AY 2024-25, and Michaelmas Term 2024
    # require dedicated patterns rather than generic parsing."
    assert REQUIRED_PATTERN_IDS == ("season_year", "academic_year_range",
                                    "named_term_year")
    for dropped in range(3):
        remaining = tuple(one for index, one in enumerate(PATTERNS.patterns)
                          if index != dropped)
        with pytest.raises(MissingRequiredPattern):
            DatePatterns(patterns=remaining)


def test_the_catalogue_beyond_the_three_is_injected_and_empty_by_default():
    # "Date and academic-term regex catalogue beyond the three named patterns |
    # §3.10 | ... The rest is manual."
    assert PATTERNS.extra_pattern_ids == ()
    extended = DatePatterns(patterns=PATTERNS.patterns + (
        DatePattern(pattern_id="iso_day", pattern=re.compile(r"\b\d{4}-\d{2}-\d{2}\b")),))
    assert extended.extra_pattern_ids == ("iso_day",)


def test_duplicate_pattern_ids_are_refused():
    with pytest.raises(ValueError):
        DatePatterns(patterns=PATTERNS.patterns + (SPRING_2025,))


@pytest.mark.parametrize("raw,expected_id", [
    ("Spring 2025", SEASON_YEAR),
    ("AY 2024-25", ACADEMIC_YEAR_RANGE),
    ("Michaelmas Term 2024", NAMED_TERM_YEAR),
])
def test_each_named_term_is_claimed_by_its_own_dedicated_pattern(raw, expected_id):
    # Done-means 10 asserts dedication "by pattern identity in the result rather than
    # by the value alone", which is what `DateMatch.pattern_id` is for.
    observation = Observation(
        file_id="f", content_hash="a" * 64, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location("heading", ()), occurrence_count=1, observed_at=CLOCK,
        reliability="possible", run_id="r")
    found = date_matches(observation, patterns=PATTERNS)
    assert [one.pattern_id for one in found] == [expected_id]
    assert [one.value for one in found] == [raw]


def test_no_pattern_claims_another_patterns_case():
    # Three dedicated patterns, not one general one wearing three ids.
    for one in PATTERNS.patterns:
        claimed = [raw for raw in ("Spring 2025", "AY 2024-25",
                                   "Michaelmas Term 2024")
                   if one.pattern.search(raw)]
        assert len(claimed) == 1


# --- Done-means 10, positive half -------------------------------------------

@pytest.mark.parametrize("raw", ["Spring 2025", "AY 2024-25",
                                 "Michaelmas Term 2024"])
def test_each_named_term_produces_exactly_one_term_fact(raw, p6_conn, tmp_path):
    file_id, content_hash, fact_id = _resolve(
        p6_conn, tmp_path, name=f"{raw.replace(' ', '-')}.txt", raw=raw)
    assert fact_id is not None
    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert [(r["field_key"], r["canonical_value"], r["reliability_state"])
            for r in rows] == [("term", raw, "validated")]
    assert unresolved_for_file(p6_conn, file_id, content_hash) == []


def test_a_term_fact_cites_the_observation_that_carried_the_span(
        p6_conn, tmp_path):
    file_id, content_hash = _record(p6_conn, tmp_path, name="syllabus.txt",
                                    body=b"Spring 2025")
    observation = _observe(p6_conn, run_id="r-cite", file_id=file_id,
                           content_hash=content_hash, raw="Spring 2025")
    fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                    field_key="term",
                    candidates=rank(date_candidates(observation, patterns=PATTERNS),
                                    zone_weight=ZONE_WEIGHT,
                                    tier_weight=TIER_WEIGHT),
                    minimum_score=1.0, minimum_margin=0.5)
    refs = json.loads(
        facts_for_file(p6_conn, file_id, content_hash)[0]["evidence_refs"])
    assert refs == [observation.observation_key]


# --- Done-means 10, negative half: §3.10's four look-alike number kinds ------

@pytest.mark.parametrize("raw,name", [
    ("v2024", "version"),
    ("build 20240117", "build"),
    ("Ship to Cambridge MA 02139 by Friday.", "zip"),
    ("Receipt for one XPS 13 laptop.", "device"),
    ("BUSIB 4300", "course_identifier"),
])
def test_a_number_that_only_looks_like_a_year_produces_no_date_fact(
        raw, name, p6_conn, tmp_path):
    # §3.10: "file names and documents frequently contain numbers that look like years
    # but are course identifiers, version numbers, build numbers, ZIP codes, or other
    # unrelated values." A03's two subjects are the ZIP and the device model.
    file_id, content_hash, fact_id = _resolve(
        p6_conn, tmp_path, name=f"{name}.txt", raw=raw)
    assert fact_id is None
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    rows = unresolved_for_file(p6_conn, file_id, content_hash, field_key="term")
    assert [r["reason"] for r in rows] == ["no_candidate_evidence"]


def test_a_bare_year_is_not_a_candidate_without_a_pattern_that_claims_it(
        p6_conn, tmp_path):
    # The trap §3.10 exists to close: `2025` on its own is a four-digit number, and
    # no pattern in the catalogue claims it.
    assert date_matches(
        Observation(file_id="f", content_hash="a" * 64, extractor_name="pdf.text",
                    extractor_version="1.0.0", source_type="text_document",
                    raw_value="2025", location=Location("heading", ()),
                    occurrence_count=1, observed_at=CLOCK, reliability="possible",
                    run_id="r"),
        patterns=PATTERNS) == ()


# --- no fuzzy path exists ----------------------------------------------------

def test_there_is_no_route_to_a_value_without_a_pattern_id():
    # "no bare four-digit-year regex reachable without a pattern id, and no fallback
    # that accepts a candidate a pattern rejected."
    with pytest.raises(NoPatternIdentity):
        parse_exact("Spring 2025", pattern_id="")
    with pytest.raises(NoPatternIdentity):
        parse_exact("   ", pattern_id=SEASON_YEAR)
    with pytest.raises(NoPatternIdentity):
        DatePattern(pattern_id="", pattern=re.compile(r"x"))


def test_parse_exact_reinterprets_nothing():
    # "then parsed without fuzzy matching" -- whitespace runs collapse and that is
    # the entire transformation. No month table, no locale, no century expansion.
    assert parse_exact("Spring  2025", pattern_id=SEASON_YEAR) == "Spring 2025"
    assert parse_exact("AY 2024-25", pattern_id=ACADEMIC_YEAR_RANGE) == "AY 2024-25"
    assert parse_exact("Michaelmas Term 2024",
                       pattern_id=NAMED_TERM_YEAR) == "Michaelmas Term 2024"
    assert parse_exact("Fall 25", pattern_id=SEASON_YEAR) == "Fall 25"


def test_no_fuzzy_parser_is_imported_or_reachable():
    # Runtime introspection, not a source-text search: a fuzzy parser would arrive as
    # a callable in the module namespace or as an import.
    import facts.dates as module
    names = {name.lower() for name in vars(module)}
    assert not any(marker in name for name in names
                   for marker in ("dateutil", "fuzzy", "guess", "strptime",
                                  "parse_date", "dateparser"))
    import sys
    assert "dateutil" not in sys.modules


def test_the_module_authors_no_regular_expression():
    # §3.10's catalogue is Deferred. The ids are the design's three cases; every
    # expression that recognises them is the caller's.
    import facts.dates as module
    assert [name for name, value in vars(module).items()
            if isinstance(value, re.Pattern)] == []
    assert [name for name, value in vars(module).items()
            if isinstance(value, (DatePattern, DatePatterns))] == []


def test_a_string_is_not_accepted_where_an_explicit_expression_is_required():
    with pytest.raises(ValueError):
        DatePattern(pattern_id=SEASON_YEAR, pattern=r"\bSpring \d{4}\b")


# --- several spans in one observation ----------------------------------------

def test_two_terms_in_one_raw_value_are_two_candidates_and_fill_nothing(
        p6_conn, tmp_path):
    # Two dedicated patterns each claim a span, the two candidates tie, and §3.7's
    # margin refuses -- a date is ranked like any other facet and gets no exemption.
    raw = "Spring 2025 and Michaelmas Term 2024"
    file_id, content_hash = _record(p6_conn, tmp_path, name="both.txt",
                                    body=raw.encode())
    observation = _observe(p6_conn, run_id="r-both", file_id=file_id,
                           content_hash=content_hash, raw=raw)
    candidates = date_candidates(observation, patterns=PATTERNS)
    assert sorted(c.value for c in candidates) == ["Michaelmas Term 2024",
                                                   "Spring 2025"]
    assert fill_or_abstain(
        p6_conn, file_id=file_id, content_hash=content_hash, field_key="term",
        candidates=rank(candidates, zone_weight=ZONE_WEIGHT,
                        tier_weight=TIER_WEIGHT),
        minimum_score=1.0, minimum_margin=0.5) is None
    assert [r["reason"] for r in unresolved_for_file(
        p6_conn, file_id, content_hash, field_key="term")] == ["below_margin"]


def test_a_candidate_carries_p4s_zone_so_the_ranker_can_weight_it(p6_conn, tmp_path):
    # §3.7's positional weighting applies to dates too; the producer supplies the
    # zone and never the weight.
    file_id, content_hash = _record(p6_conn, tmp_path, name="pos.txt",
                                    body=b"Spring 2025")
    observation = _observe(p6_conn, run_id="r-pos", file_id=file_id,
                           content_hash=content_hash, raw="Spring 2025",
                           zone="filename")
    candidate = date_candidates(observation, patterns=PATTERNS)[0]
    assert candidate.zone == "filename"
    assert candidate.signal_tier is None
    assert candidate.score == 1.0


def test_date_candidates_is_date_matches_projected_onto_the_facet_shape(
        p6_conn, tmp_path):
    file_id, content_hash = _record(p6_conn, tmp_path, name="proj.txt",
                                    body=b"Spring 2025")
    observation = _observe(p6_conn, run_id="r-proj", file_id=file_id,
                           content_hash=content_hash, raw="Spring 2025")
    found = date_matches(observation, patterns=PATTERNS)
    candidates = date_candidates(observation, patterns=PATTERNS)
    assert len(found) == len(candidates) == 1
    assert isinstance(found[0], DateMatch)
    assert candidates[0].value == found[0].value
    assert candidates[0].evidence_refs == (found[0].evidence_ref,)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p6/test_p6_dates.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'facts.dates'`

- [ ] **Step 3: Write the implementation**

```python
# src/facts/dates.py
"""§3.10 dates and academic terms: explicit patterns, and no fuzzy parsing anywhere.

§3.10, verbatim: *"Date extraction should be deliberately narrow. The product must not
use fuzzy date parsing because file names and documents frequently contain numbers
that look like years but are course identifiers, version numbers, build numbers, ZIP
codes, or other unrelated values. Date candidates should be identified with explicit
regular expressions and then parsed without fuzzy matching. Academic terms such as
Spring 2025, AY 2024-25, and Michaelmas Term 2024 require dedicated patterns rather
than generic parsing."*

Three consequences, and all three are structural rather than advisory:

* **A candidate exists only where a pattern matched.** There is no scanner, no
  four-digit-year fallback and no "looks like a date" branch. `parse_exact` refuses to
  produce a value without a pattern id, so the only way to a date fact is through a
  pattern that claimed the span.
* **The three named academic terms get three dedicated patterns**, identified by id.
  `Spring 2025` is not `AY 2024-25` parsed loosely, and the result carries which
  pattern claimed it so a test can assert dedication rather than coincidence.
* **The pattern bodies are injected.** Which seasons, which term names, which
  numeric formats -- that is the SPEC's *"Date and academic-term regex catalogue
  beyond the three named patterns"*, which is Deferred. This module authors the three
  **ids** the design names and not one character of regex.

"Parsed without fuzzy matching" is taken at its word: `parse_exact` collapses runs of
whitespace and returns the matched text. Any further normalization is a per-field
normalizer, and those are Deferred too (*"Per-field normalizers and alias tables |
§2.8, §3.6"*).
"""
from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass

from evidence_shape.observation import Observation

from facts.evidence import cite
from facts.facets import Candidate

#: The three academic-term patterns §3.10 names, as ids. The design states
#: `Spring 2025` (a season and a year), `AY 2024-25` (an academic-year range) and
#: `Michaelmas Term 2024` (a named term and a year) and requires "dedicated patterns
#: rather than generic parsing" for each. The ids are the design's three cases; the
#: expressions that recognise them are the caller's.
SEASON_YEAR = "season_year"
ACADEMIC_YEAR_RANGE = "academic_year_range"
NAMED_TERM_YEAR = "named_term_year"
REQUIRED_PATTERN_IDS: tuple[str, str, str] = (
    SEASON_YEAR, ACADEMIC_YEAR_RANGE, NAMED_TERM_YEAR)


class MissingRequiredPattern(ValueError):
    """A `DatePatterns` without one of §3.10's three named academic-term patterns."""


class NoPatternIdentity(ValueError):
    """A parse attempted without a pattern id -- the fuzzy path, refused."""


@dataclass(frozen=True, slots=True)
class DatePattern:
    """One explicit regular expression and the id that identifies it in a result."""

    pattern_id: str
    pattern: re.Pattern[str]

    def __post_init__(self) -> None:
        if not self.pattern_id:
            raise NoPatternIdentity("a pattern is identified by a non-empty id")
        if not isinstance(self.pattern, re.Pattern):
            raise ValueError("§3.10 requires an explicit compiled regular expression")


@dataclass(frozen=True, slots=True)
class DatePatterns:
    """The injected catalogue. The three §3.10 names are required; the rest is the
    Deferred catalogue and is empty unless a caller supplies it."""

    patterns: tuple[DatePattern, ...]

    def __post_init__(self) -> None:
        ids = tuple(one.pattern_id for one in self.patterns)
        if len(set(ids)) != len(ids):
            raise ValueError(f"duplicate pattern ids: {ids}")
        missing = [name for name in REQUIRED_PATTERN_IDS if name not in ids]
        if missing:
            raise MissingRequiredPattern(
                f"§3.10 names three academic-term patterns and requires a dedicated "
                f"one for each; missing: {missing}")

    @property
    def pattern_ids(self) -> tuple[str, ...]:
        return tuple(one.pattern_id for one in self.patterns)

    @property
    def extra_pattern_ids(self) -> tuple[str, ...]:
        """Everything beyond §3.10's three -- the Deferred half, empty by default."""
        return tuple(name for name in self.pattern_ids
                     if name not in REQUIRED_PATTERN_IDS)

    def by_id(self, pattern_id: str) -> re.Pattern[str]:
        for one in self.patterns:
            if one.pattern_id == pattern_id:
                return one.pattern
        raise KeyError(pattern_id)


@dataclass(frozen=True, slots=True)
class DateMatch:
    """One pattern's claim on one span, carrying which pattern claimed it.

    Done-means 10 requires each of the three academic terms to be matched by a
    *dedicated* pattern "asserted by pattern identity in the result rather than by the
    value alone", and `Candidate` has no room for an id -- so the identity lives here
    and `date_candidates` is this record projected onto §3.7's shape.
    """

    pattern_id: str
    raw: str
    value: str
    evidence_ref: str
    zone: str
    signal_tier: int | None
    occurrence_count: int


def parse_exact(raw: str, *, pattern_id: str) -> str:
    """Return the matched text, whitespace-normalized, or refuse.

    This is the whole of "then parsed without fuzzy matching": no month table, no
    locale, no two-digit-year expansion, no reinterpretation of any kind. A caller
    with no pattern id has nothing that claimed the span, and there is no route from
    here to a value without one.
    """
    if not pattern_id:
        raise NoPatternIdentity(
            "§3.10 admits no candidate that a dedicated pattern did not claim")
    if not raw or not raw.strip():
        raise NoPatternIdentity(f"pattern {pattern_id!r} claimed an empty span")
    return " ".join(raw.split())


def date_matches(observation: Observation, *,
                 patterns: DatePatterns) -> tuple[DateMatch, ...]:
    """Every span of this observation's raw value that an explicit pattern claims."""
    found: list[DateMatch] = []
    for one in patterns.patterns:
        for match in one.pattern.finditer(observation.raw_value):
            found.append(DateMatch(
                pattern_id=one.pattern_id, raw=match.group(0),
                value=parse_exact(match.group(0), pattern_id=one.pattern_id),
                evidence_ref=cite(observation), zone=observation.location.zone,
                signal_tier=observation.signal_tier,
                occurrence_count=observation.occurrence_count))
    return tuple(sorted(found, key=lambda one: (one.pattern_id, one.value)))


def date_candidates(observation: Observation, *,
                    patterns: DatePatterns) -> tuple[Candidate, ...]:
    """§3.7 candidates for §3.10 spans, so a date is ranked like any other facet.

    The score is P4's `occurrence_count` and nothing else: §3.7's weights are applied
    by `facts.facets.rank` from an injected map, and a producer that pre-weighted its
    own candidates would be a second place those numbers live.
    """
    return tuple(
        Candidate(value=one.value, score=float(one.occurrence_count),
                  evidence_refs=(one.evidence_ref,), zone=one.zone,
                  signal_tier=one.signal_tier)
        for one in date_matches(observation, patterns=patterns))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p6/test_p6_dates.py -v`
Expected: PASS — 25 passed (17 test functions; three are parametrized and expand to eleven)

- [ ] **Step 5: Commit**

```bash
git add src/facts/dates.py tests/p6/test_p6_dates.py
git commit -m "feat(P6): §3.10 dates and academic terms — explicit patterns, no fuzzy parsing"
```

---

### Task 13: §3.11 domain activation, and several domains on one file at once

**Files:**
- Create: `src/facts/domains.py`
- Test: `tests/p6/test_p6_domains.py`

**Interfaces:**
- Consumes: `facts.fields` — `DOMAIN_FIELDS`, `FIELD_SCOPES`, `fields_in_scope`;
  `facts.file_facts.facts_for_file`.
- Produces: `SCHEMA_IDS: tuple[str, ...]` (ten), `UNIVERSAL_SCOPE: str`,
  `FIELD_LESS_SCHEMA_IDS: tuple[str, ...]` (derived), `UnknownSchema`,
  `ActivationSignal(schema_id, activates)`, `ActivationSignals(signals)` — injected, no defaults;
  `active_domains(conn, *, file_id, content_hash, activation_signals) -> frozenset[str]`;
  `active_field_allowlist(conn, *, file_id, content_hash, activation_signals) -> tuple[str, ...]`;
  `schema_fields(schema_id) -> tuple[str, ...]`.

**Done-means:** 14.

**§3.11's two sentences that this module is:** *"It should then activate domain-specific schemas
only when the evidence indicates that a domain is plausible … This means target university is not a
fact that every file is expected to have. It is a field available only when the Applications domain
is plausibly active."* And the worked case: *"One file may hold facts from more than one domain
without losing information. An academic abstract submitted as part of a university application can
retain project = PVA/RDP and document type = abstract while also carrying purpose = university
application and target university = UChicago. At the pre-sorting stage, the product does not need to
decide which of those perspectives will ultimately determine its physical location. It preserves
both so the user can later choose the appropriate organization structure."*

**`active_domains` returns a set because §3.11 forbids a winner.** Nothing here ranks, nothing here
suppresses, and no field is dropped. That is the whole of Done-means 14 and it is a structural
property rather than a behaviour to remember: a function returning `frozenset[str]` has no tie to
break.

**`document type` is never a key.** F4 settled it: the design uses *"document type"* as the generic
word for whichever specific field the active domain declares — `application_document_type` under
College applications, `artifact_type` under Research and Code. §3.11's own worked case is a research
artifact (*"project = PVA/RDP and document type = abstract"*), so Done-means 14's four fields are
read here as **`project`, `artifact_type`, `purpose`, `target_university`**. Two keys, one prose
word, no third field.

**Ten schemas activate; six of them have field rows.** `SCHEMA_IDS` is `academic`,
`college_applications`, `research`, `career`, `photos`, `code` plus the four safety domains
`finance`, `identity`, `medical`, `legal`. `FIELD_LESS_SCHEMA_IDS` is **derived** —
`tuple(s for s in SCHEMA_IDS if s not in FIELD_SCOPES)` — rather than written down, so the schema
vocabulary and the field-scope vocabulary cannot drift apart, and a test asserts the derivation lands
on exactly `("career", "identity", "medical", "legal")`. Activating one of the four contributes
nothing to the allowlist. That is D1, narrowed, made mechanical: *"Do not author career fields. Not
in this task, not in the domain catalogue as field rows. Career is owed before P10."* A schema with
no authored fields must not cause fields to be invented, and the allowlist skipping it is how that is
guaranteed rather than remembered.

**`src/facts/` never imports `planning/domains/`.** That directory is a 574-entry research artifact
with its own gate and its own owner; the catalogue this module activates is `facts.fields`, which is
§00's own small list. Task 25 asserts the whole directory is imported nowhere in `facts`; the test
below carries the module-local half of the same guard.

**P6 authors no activation signal.** The SPEC defers it outright: *"Domain activation signals |
§3.11 ("when the evidence indicates that a domain is plausible"), §5.7 ("detection signals") | Which
evidence activates which domain is unauthored."* So `ActivationSignals` is a required argument with
no default, an empty one activates nothing, and a test asserts no `ActivationSignal` instance exists
in the module namespace. The predicate reads the file version's **existing facts** — the skeleton's
`Consumes:` line names `facts.file_facts.facts_for_file` and that is the right input: §8.6's
degradation order runs direct and rule-validated facts first, and the allowlist those facts activate
is what bounds the model afterwards.

**The allowlist is one object, computed once.** §3.5: the model *"can only propose facts that belong
to the active domain schema"*, and the skeleton requires that *"the allowlist this produces is the
same object Task 17 hands to P8, so the model … is one computation and not two."* It is deterministic
— universal fields first in catalogue order, then each active schema in `SCHEMA_IDS` order — and
deduplicated, because `project` and `artifact_type` belong to **both** Research and Code and a file
with both active must list each once and lose neither.

**Activation is per file version.** §3.4 and §8.2 make every P6 read per content hash, so a prior
version's facts cannot activate a domain on this one. A test drives that directly.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_domains.py
"""§3.11 domain activation -- Done-means 14, and §3.11's own worked case."""
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file

from facts.domains import (
    FIELD_LESS_SCHEMA_IDS, SCHEMA_IDS, UNIVERSAL_SCOPE, ActivationSignal,
    ActivationSignals, UnknownSchema, active_domains, active_field_allowlist,
    schema_fields,
)
from facts.fields import DOMAIN_FIELDS, FIELD_SCOPES, fields_in_scope
from facts.file_facts import FACT_ORIGINS, facts_for_file, write_fact, RULE
from facts.values import VALUE_ORIGINS, ensure_value

EVIDENCE_REF = "sha256:" + "a" * 64
CACHE_KEY = "sha256:" + "b" * 64


def _record(conn, tmp_path, *, name, body=b"one file, several facts"):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Applications", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _fact(conn, *, file_id, content_hash, field_key, value):
    value_id = ensure_value(conn, field_key=field_key, canonical_value=value,
                            first_evidence_ref=EVIDENCE_REF,
                            origin=VALUE_ORIGINS[0])
    return write_fact(conn, file_id=file_id, content_hash=content_hash,
                      field_key=field_key, value_id=value_id,
                      reliability_state="validated", origin=RULE,
                      evidence_refs=(EVIDENCE_REF,), cache_key=CACHE_KEY,
                      active=True)


def _when_field_present(schema_id, field_key):
    """An injected signal: this schema is plausible when this field is filled.

    The test's rule, not P6's -- "which evidence activates which domain is
    unauthored", so the plan holds the slot and the caller fills it.
    """
    return ActivationSignal(
        schema_id=schema_id,
        activates=lambda rows: any(row["field_key"] == field_key for row in rows))


@pytest.fixture()
def abstract(p6_conn, tmp_path):
    """§3.11's worked case, as facts: a research artifact submitted with an
    application. `project = PVA/RDP`, `artifact_type = abstract`,
    `purpose = university application`, `target_university = UChicago`."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="PVA-RDP abstract.pdf")
    for field_key, value in (("project", "PVA/RDP"),
                             ("artifact_type", "abstract"),
                             ("purpose", "university application"),
                             ("target_university", "UChicago")):
        _fact(p6_conn, file_id=file_id, content_hash=content_hash,
              field_key=field_key, value=value)
    return file_id, content_hash


# --- the ten schemas, and the four that carry no fields ----------------------

def test_the_ten_recognised_schemas_are_named_once():
    assert SCHEMA_IDS == ("academic", "college_applications", "research", "career",
                          "photos", "code", "finance", "identity", "medical",
                          "legal")
    assert len(set(SCHEMA_IDS)) == 10


def test_the_field_bearing_schemas_are_exactly_the_non_universal_field_scopes():
    # One vocabulary, two views: a scope is a field row's home, a schema id is what
    # activates. They cannot drift because the second is derived from the first.
    assert set(FIELD_SCOPES) - {UNIVERSAL_SCOPE} == set(SCHEMA_IDS) - set(
        FIELD_LESS_SCHEMA_IDS)
    assert UNIVERSAL_SCOPE not in SCHEMA_IDS


def test_career_identity_medical_and_legal_carry_no_field_rows(p6_conn):
    # D1 (narrowed): "Do not author career fields. Not in this task, not in the domain
    # catalogue as field rows. Career is owed before P10." Identity, medical and legal
    # are §3.15 safety domains that §3.11 gives no field row.
    assert FIELD_LESS_SCHEMA_IDS == ("career", "identity", "medical", "legal")
    for schema_id in FIELD_LESS_SCHEMA_IDS:
        assert schema_fields(schema_id) == ()
        assert schema_id not in DOMAIN_FIELDS


def test_the_catalogue_constant_and_the_loaded_table_are_the_same_data(p6_conn):
    # `DOMAIN_FIELDS` and the `fields` rows `create_fields` loaded must agree, or the
    # allowlist and the model's schema check would be reading two different lists.
    for schema_id, keys in DOMAIN_FIELDS.items():
        assert {row["field_key"] for row in fields_in_scope(p6_conn, schema_id)} == \
            set(keys)


def test_an_unrecognised_schema_is_refused_rather_than_created():
    with pytest.raises(UnknownSchema):
        ActivationSignal(schema_id="astrology", activates=lambda rows: True)
    with pytest.raises(UnknownSchema):
        schema_fields("astrology")


# --- activation: the universal set always, a domain only on evidence ---------

def test_the_universal_set_applies_to_every_file(p6_conn, tmp_path):
    # §3.11: "a small shared set of universal file facts" -- shared meaning every
    # file, with no signal required.
    file_id, content_hash = _record(p6_conn, tmp_path, name="anything.pdf")
    allowlist = active_field_allowlist(p6_conn, file_id=file_id,
                                       content_hash=content_hash,
                                       activation_signals=ActivationSignals(()))
    universal = {row["field_key"] for row in fields_in_scope(p6_conn,
                                                             UNIVERSAL_SCOPE)}
    assert set(allowlist) == universal
    assert universal


def test_target_university_is_not_a_field_every_file_is_expected_to_have(
        p6_conn, tmp_path):
    # §3.11, verbatim: "This means target university is not a fact that every file is
    # expected to have. It is a field available only when the Applications domain is
    # plausibly active."
    file_id, content_hash = _record(p6_conn, tmp_path, name="plain.pdf")
    assert "target_university" not in active_field_allowlist(
        p6_conn, file_id=file_id, content_hash=content_hash,
        activation_signals=ActivationSignals(()))
    assert "target_university" in DOMAIN_FIELDS["college_applications"]


def test_no_signal_activates_no_domain(p6_conn, abstract):
    # "Domain activation signals ... Which evidence activates which domain is
    # unauthored." An empty signal set is the honest behaviour of an unauthored rule,
    # not a reason to guess.
    file_id, content_hash = abstract
    assert active_domains(p6_conn, file_id=file_id, content_hash=content_hash,
                          activation_signals=ActivationSignals(())) == frozenset()


def test_the_module_authors_no_activation_signal():
    import facts.domains as module
    assert [name for name, value in vars(module).items()
            if isinstance(value, (ActivationSignal, ActivationSignals))] == []
    with pytest.raises(TypeError):
        ActivationSignals()


def test_a_duplicate_signal_for_one_schema_is_refused():
    signal = _when_field_present("research", "project")
    with pytest.raises(ValueError):
        ActivationSignals((signal, signal))


# --- Done-means 14: several domains on one file, none dropped ----------------

def test_one_file_holds_four_facts_across_two_domains(p6_conn, abstract):
    # Done-means 14, as F4 resolves its field names: `document type` is the design's
    # generic word for whichever specific field the active domain declares, and
    # §3.11's own worked case is a research artifact, so it is `artifact_type`.
    file_id, content_hash = abstract
    held = {(row["field_key"], row["canonical_value"])
            for row in facts_for_file(p6_conn, file_id, content_hash)}
    assert held == {("project", "PVA/RDP"), ("artifact_type", "abstract"),
                    ("purpose", "university application"),
                    ("target_university", "UChicago")}

    signals = ActivationSignals((_when_field_present("research", "project"),
                                 _when_field_present("college_applications",
                                                     "target_university")))
    assert active_domains(p6_conn, file_id=file_id, content_hash=content_hash,
                          activation_signals=signals) == frozenset(
        {"research", "college_applications"})


def test_no_domain_is_forced_to_win(p6_conn, abstract):
    # §3.11: "the product does not need to decide which of those perspectives will
    # ultimately determine its physical location. It preserves both."
    file_id, content_hash = abstract
    signals = ActivationSignals((_when_field_present("research", "project"),
                                 _when_field_present("college_applications",
                                                     "target_university")))
    allowlist = active_field_allowlist(p6_conn, file_id=file_id,
                                       content_hash=content_hash,
                                       activation_signals=signals)
    for field_key in ("project", "artifact_type", "purpose", "target_university"):
        assert field_key in allowlist
    assert set(DOMAIN_FIELDS["research"]) <= set(allowlist)
    assert set(DOMAIN_FIELDS["college_applications"]) <= set(allowlist)


def test_no_field_is_dropped_when_two_domains_share_one(p6_conn, abstract):
    # `project` and `artifact_type` belong to Research AND Code. Two active domains
    # must list each once and lose neither.
    file_id, content_hash = abstract
    signals = ActivationSignals((_when_field_present("research", "project"),
                                 _when_field_present("code", "project")))
    allowlist = active_field_allowlist(p6_conn, file_id=file_id,
                                       content_hash=content_hash,
                                       activation_signals=signals)
    assert len(allowlist) == len(set(allowlist))
    assert set(DOMAIN_FIELDS["research"]) <= set(allowlist)
    assert set(DOMAIN_FIELDS["code"]) <= set(allowlist)
    assert allowlist.count("project") == 1
    assert allowlist.count("artifact_type") == 1


def test_an_inactive_domains_fields_stay_out_of_the_allowlist(p6_conn, abstract):
    file_id, content_hash = abstract
    signals = ActivationSignals((_when_field_present("research", "project"),))
    allowlist = active_field_allowlist(p6_conn, file_id=file_id,
                                       content_hash=content_hash,
                                       activation_signals=signals)
    assert "target_university" not in allowlist
    assert "capture_year" not in allowlist
    assert set(DOMAIN_FIELDS["research"]) <= set(allowlist)


def test_a_field_less_schema_activates_and_contributes_nothing(p6_conn, abstract):
    # Activating `career` must not cause a career field to appear. S3's deferral holds
    # and P6 does not un-defer it by side effect.
    file_id, content_hash = abstract
    signals = ActivationSignals((_when_field_present("career", "project"),))
    assert active_domains(p6_conn, file_id=file_id, content_hash=content_hash,
                          activation_signals=signals) == frozenset({"career"})
    allowlist = active_field_allowlist(p6_conn, file_id=file_id,
                                       content_hash=content_hash,
                                       activation_signals=signals)
    assert set(allowlist) == {row["field_key"]
                              for row in fields_in_scope(p6_conn, UNIVERSAL_SCOPE)}


# --- the allowlist is a value, and it is deterministic -----------------------

def test_the_allowlist_is_deterministic_and_ordered_by_the_catalogue(
        p6_conn, abstract):
    file_id, content_hash = abstract
    signals = ActivationSignals((_when_field_present("college_applications",
                                                     "target_university"),
                                 _when_field_present("research", "project")))
    first = active_field_allowlist(p6_conn, file_id=file_id,
                                   content_hash=content_hash,
                                   activation_signals=signals)
    reordered = ActivationSignals(tuple(reversed(signals.signals)))
    assert active_field_allowlist(p6_conn, file_id=file_id,
                                  content_hash=content_hash,
                                  activation_signals=reordered) == first
    universal = tuple(row["field_key"]
                      for row in fields_in_scope(p6_conn, UNIVERSAL_SCOPE))
    assert first[:len(universal)] == universal


def test_activation_is_per_file_version(p6_conn, tmp_path):
    # §3.4 and §8.2 make every P6 read per file VERSION, so a prior version's facts
    # cannot activate a domain on this one.
    file_id, content_hash = _record(p6_conn, tmp_path, name="v1.pdf")
    _fact(p6_conn, file_id=file_id, content_hash=content_hash,
          field_key="project", value="PVA/RDP")
    signals = ActivationSignals((_when_field_present("research", "project"),))
    assert active_domains(p6_conn, file_id=file_id, content_hash=content_hash,
                          activation_signals=signals) == frozenset({"research"})
    assert active_domains(p6_conn, file_id=file_id, content_hash="f" * 64,
                          activation_signals=signals) == frozenset()


def test_domains_imports_nothing_from_the_research_domain_library():
    # `planning/domains/` is a 574-entry research artifact, not this catalogue.
    # Task 25 asserts the whole directory is imported nowhere in `facts`; this is the
    # module-local half of the same guard.
    import facts.domains as module
    assert module.__doc__ is not None
    imported = {value.__name__ for value in vars(module).values()
                if getattr(value, "__module__", None) is None
                and hasattr(value, "__name__")}
    assert not any(name.startswith("domains.") or name == "roster"
                   for name in imported)
    assert all(not getattr(value, "__module__", "").startswith("planning")
               for value in vars(module).values())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p6/test_p6_domains.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'facts.domains'`

- [ ] **Step 3: Write the implementation**

```python
# src/facts/domains.py
"""§3.11 domain activation, and several domains on one file at once.

§3.11, verbatim: *"The product should have a small shared set of universal file facts
... It should then activate domain-specific schemas only when the evidence indicates
that a domain is plausible ... This means target university is not a fact that every
file is expected to have. It is a field available only when the Applications domain is
plausibly active."*

And the worked case this module exists to preserve, also verbatim: *"One file may hold
facts from more than one domain without losing information. An academic abstract
submitted as part of a university application can retain project = PVA/RDP and
document type = abstract while also carrying purpose = university application and
target university = UChicago. At the pre-sorting stage, the product does not need to
decide which of those perspectives will ultimately determine its physical location. It
preserves both so the user can later choose the appropriate organization structure."*

Two things follow and both are structural:

* **Activation adds; it never chooses.** `active_domains` returns a set, not a winner.
  No domain suppresses another, no field is dropped, and nothing here ranks.
* **P6 authors no activation signal.** *"Domain activation signals | §3.11 ("when the
  evidence indicates that a domain is plausible"), §5.7 ("detection signals") | Which
  evidence activates which domain is unauthored."* The signals arrive as an injected
  `ActivationSignals` with no default; an empty one activates nothing, which is the
  honest behaviour of an unauthored rule.

**Schemas are named, fields are not implied.** `SCHEMA_IDS` is the ten domains the
product recognises -- §3.11's six with field rows plus §3.15's remaining safety
domains. Four of the ten have **no field rows at all** (D1, narrowed): activating one
contributes nothing to the allowlist, which is exactly right, because a schema with no
authored fields must not cause fields to be invented. `FIELD_LESS_SCHEMA_IDS` is
derived from `facts.fields.FIELD_SCOPES` rather than written down, so the two
vocabularies cannot drift apart.

**This module reads `planning/domains/` never.** That directory is a research artifact
of 574 proposed entries with its own gate; the catalogue this activates is
`facts.fields`, and Task 25 asserts the import does not exist.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from facts.fields import DOMAIN_FIELDS, FIELD_SCOPES, fields_in_scope
from facts.file_facts import facts_for_file

#: §3.11's six domains with field rows, plus §3.15's four safety domains. Named here
#: because a schema id is a closed vocabulary the product recognises; what activates
#: one, and which fields one carries, are elsewhere.
SCHEMA_IDS: tuple[str, ...] = (
    "academic", "college_applications", "research", "career", "photos", "code",
    "finance", "identity", "medical", "legal")

#: `FIELD_SCOPES[0]` is the universal scope. §3.11: the universal set "applies to
#: every file", so it is in every allowlist and is never activated.
UNIVERSAL_SCOPE: str = FIELD_SCOPES[0]

#: Derived, not authored: the schemas the product recognises that carry no field rows.
#: D1 (narrowed): "Do not author career fields ... Career is owed before P10." The
#: same holds for identity, medical and legal, which §3.15 names as safety domains and
#: §3.11 gives no field row.
FIELD_LESS_SCHEMA_IDS: tuple[str, ...] = tuple(
    schema_id for schema_id in SCHEMA_IDS if schema_id not in FIELD_SCOPES)


class UnknownSchema(KeyError):
    """A signal naming a domain the product does not recognise."""


@dataclass(frozen=True, slots=True)
class ActivationSignal:
    """One injected rule: this schema is plausible when this predicate says so.

    The predicate receives the file version's existing facts -- §3.11's "when the
    evidence indicates that a domain is plausible", read as P6's own evidence-derived
    claims, which is also what makes §8.6's degradation order work: direct and
    rule-validated facts are produced first, and the allowlist they activate is what
    bounds the model afterwards.
    """

    schema_id: str
    activates: Callable[[tuple[sqlite3.Row, ...]], bool]

    def __post_init__(self) -> None:
        if self.schema_id not in SCHEMA_IDS:
            raise UnknownSchema(
                f"{self.schema_id!r} is not one of the ten recognised schemas")
        if not callable(self.activates):
            raise TypeError("an activation signal is a predicate over the file's facts")


@dataclass(frozen=True, slots=True)
class ActivationSignals:
    """The injected signal set. No default: P6 authors none of these."""

    signals: tuple[ActivationSignal, ...]

    def __post_init__(self) -> None:
        ids = [signal.schema_id for signal in self.signals]
        if len(set(ids)) != len(ids):
            raise ValueError(f"one signal per schema; duplicates: {sorted(ids)}")


def active_domains(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                   activation_signals: ActivationSignals) -> frozenset[str]:
    """Which domain schemas this file version's own evidence makes plausible.

    A set, deliberately: §3.11 preserves every perspective and "does not need to
    decide which of those perspectives will ultimately determine its physical
    location". Nothing here breaks a tie because nothing here has one to break.
    """
    established = tuple(facts_for_file(conn, file_id, content_hash))
    return frozenset(signal.schema_id for signal in activation_signals.signals
                     if signal.activates(established))


def active_field_allowlist(conn: sqlite3.Connection, *, file_id: str,
                           content_hash: str,
                           activation_signals: ActivationSignals) -> tuple[str, ...]:
    """The universal fields plus every active schema's fields, deduplicated.

    This is the object §3.5's sentence turns on -- the model "can only propose facts
    that belong to the active domain schema" -- and Task 17 hands this exact tuple to
    P8, so the allowlist is one computation and not two.

    Order is deterministic and is the catalogue's: universal first, then each active
    schema in `SCHEMA_IDS` order. `project` and `artifact_type` belong to both Research
    and Code, so a file with both active must list each once and lose neither.
    """
    active = active_domains(conn, file_id=file_id, content_hash=content_hash,
                            activation_signals=activation_signals)
    allowed: list[str] = []
    for scope in (UNIVERSAL_SCOPE,
                  *(schema_id for schema_id in SCHEMA_IDS if schema_id in active)):
        if scope not in FIELD_SCOPES:
            # A recognised schema with no field rows (D1). It activates and
            # contributes nothing; it does not cause a field to be invented.
            continue
        for row in fields_in_scope(conn, scope):
            if row["field_key"] not in allowed:
                allowed.append(row["field_key"])
    return tuple(allowed)


def schema_fields(schema_id: str) -> tuple[str, ...]:
    """The authored field keys of one schema, empty for the four field-less ones."""
    if schema_id not in SCHEMA_IDS:
        raise UnknownSchema(schema_id)
    return tuple(DOMAIN_FIELDS.get(schema_id, ()))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p6/test_p6_domains.py -v`
Expected: PASS — 18 passed

- [ ] **Step 5: Commit**

```bash
git add src/facts/domains.py tests/p6/test_p6_domains.py
git commit -m "feat(P6): §3.11 domain activation — several domains on one file, none forced to win"
```

---

## Contract ambiguities — reported, not resolved

Five, each verified against the source rather than reconstructed, ordered by what it costs if
nobody looks at it.

**1. `Candidate` needs two fields the skeleton's shape does not give it.** The skeleton publishes
`Candidate(value, score, evidence_refs)` and `rank(candidates, *, zone_weight, tier_weight)`. A
weight map has nothing to weight unless the contribution says which zone and which signal tier it
came from, and `rank` has no `conn` with which to resolve the evidence refs back to observations.
Task 11 therefore appends `zone: str | None = None` and `signal_tier: int | None = None` after the
published three, in that order, defaulted, and clears both on the aggregate `rank` returns. The
three published names, their order and their meaning are unchanged, so no parallel author is broken.
**If the reviewer prefers, the alternative is to give `rank` a `conn` and resolve zones from the
cited observations** — one more database read per candidate and one more reason for a pure function
to need a connection. Recommendation: keep the descriptors.

**2. Two cache-key rules now exist across the P6 plan, and they disagree.** This document keys a
fact and an abstention on **every observation of the file version** (see *Two conventions*, above);
`PLAN-tasks-14-15.md` keys a fact on **the observations that fact cites**. Both are readings of
§3.4's five parts and neither is wrong on its own terms. The difference is visible at pass 4: under
this document's rule every pass-4 fact lands in a new cache slot and supersedes; under the sibling's,
only a fact that cited an OCR observation does. This document's rule additionally answers the case
the sibling's cannot — an `unresolved` row with no citations still needs a key, and the SPEC requires
it to have *"same composition as `file_facts`"*. **`facts.cache` (Task 6) owns the reconciliation and
neither of us may add to it.** Whoever executes Task 6 should publish one helper and both plans
should call it. Recommendation: the pass-level rule, because the abstention case forces it.

**3. `DateMatch` is an addition to Task 12's published surface.** Done-means 10 requires the three
academic terms to be matched by dedicated patterns *"asserted by pattern identity in the result
rather than by the value alone"*, and `Candidate` has no field for a pattern id. `date_candidates`
keeps the skeleton's exact signature and is defined as `date_matches` projected onto §3.7's shape,
so nothing that consumes the published name sees a change.

**4. §3.7's "case discipline" is referred to and never stated.** The SPEC says the §3.5
case-insensitivity of N-6 *"does not relax §3.7 facet matching, whose case discipline is stated below
and unchanged"* — and the section below states word boundaries, positional weighting, ranking,
thresholds and validated gazetteers, and no case rule at all. `word_boundary_match` folds case, on
the reading that §3.7's two named cases (`MIT` in "submit", `UNC` in "uncertainty") are decided by
the boundary and not by case, and that a second, case-sensitive matcher would be a second home for
the one word-boundary rule the skeleton says binds facets **and** context terms. Both named refusals
are asserted under case folding in `test_case_folding_does_not_relax_the_boundary`. **If the intended
discipline was case-sensitive facet matching, this is the line to change**, and the change is one
flag on one function — but it would then need a second decision about how the §3.5 context check
reaches a case-insensitive matcher without owning one.

**5. `fill_or_abstain` cannot be told which reliability state to write.** The skeleton's signature
has no state parameter, so Task 11 writes `validated` for every filled facet, on §3.13's definition
(*"found by a deterministic rule and passed contextual checks"*). Task 16's `media_type` uses this
function and wants `validated`, so nothing is broken today. But §3.11's Photos `people`, and any
future field whose ranked fill should be `possible` rather than `validated`, would need a keyword
this signature does not have. Not changed here, because changing a published signature is exactly
what the `Interfaces:` block exists to prevent. Flagged for whoever owns the next facet-producing
task.

## What these four tasks do NOT do

Stated so a reviewer does not look for it: no module here reads `files`, `learning_records`, an
`events` row or a P3 timestamp; none writes an §8.2 event (Task 4 writes `fact creation` when
`write_fact` is called and that is its own task's contract); none branches on `source_type` or
`extractor_name`; none imports `planning/domains/`, `planning/deferred-catalogues/`, a grouping,
tree, placement or model module; none touches a file outside `src/facts/` and `tests/p6/`; and none
contains a model call of any kind — every fact produced by these four is deterministic and Done-means
17 holds over all of them with P8 absent.
