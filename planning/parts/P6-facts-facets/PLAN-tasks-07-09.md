# P6 — Facts and facets — PLAN, Tasks 7–9

> This is the detail pass for the first three tasks of **Wave B** — the citation layer and the two
> deterministic producers that sit in front of §3.7's ranking. The rules, the verified seams and the
> file layout are in `PLAN-SKELETON.md`; the `Interfaces:` block on each task below is that
> skeleton's block, honoured name for name. Tasks 1–6, 10–13 and 14–27 are written in parallel by
> other authors against the same skeleton.

---

## What already exists when Task 7 starts

Tasks 1–6 are green. These three tasks import the following and nothing else from `facts`. Every
signature below is the skeleton's `Produces:` line, unchanged:

```text
facts.states        STATES: tuple[str, ...]                       (P4's six, re-exported)
                    strength(state: str) -> int
facts.fields        get_field(conn, field_key) -> sqlite3.Row
                    FieldNotInCatalogue
facts.values        VALUE_ORIGINS: tuple[str, str]                ("automatic", "user")
                    ensure_value(conn, *, field_key, canonical_value,
                                 first_evidence_ref, origin) -> str
facts.file_facts    FACT_ORIGINS: tuple[str, ...]                 (§3.1's five, in §3.1's order)
                    write_fact(conn, *, file_id, content_hash, field_key, value_id,
                               reliability_state, origin, evidence_refs, cache_key,
                               active) -> str
                    facts_for_file(conn, file_id, content_hash) -> list[sqlite3.Row]
                    EvidenceRequired
facts.unresolved    ATTEMPTED_PRODUCERS: tuple[str, str, str]     ("direct", "rule", "llm")
                    UNRESOLVED_REASONS: tuple[str, ...]           (the thirteen)
                    write_unresolved(conn, *, file_id, content_hash, field_key, reason,
                                     attempted_producers, evidence_refs, cache_key) -> str
                    unresolved_for_file(conn, file_id, content_hash, *,
                                        field_key=None, reason=None) -> list[sqlite3.Row]
facts.cache         fact_cache_key(*, content_hash, extractor_version, analysis_tier,
                                   model_identifier, prompt_fingerprint) -> str
facts.schema        create_facts_schema(conn) -> None
```

**`tests/p6/conftest.py` publishes `p6_conn`** — P1's database with P4's three tables, P6's own
tables, and Task 2's `fields` catalogue rows created, built on the root `conn` fixture in
`tests/conftest.py` exactly as `tests/p4/conftest.py` builds `p4_conn`. Every test file below takes
`p6_conn` and constructs everything else itself. This is the same assumption `PLAN-tasks-14-15.md`
records, stated again so the two documents cannot drift.

**Two spellings are never assumed.** `FACT_ORIGINS` and `ATTEMPTED_PRODUCERS` are addressed **by
index**, in the order the skeleton lists them (`FACT_ORIGINS` = deterministic extractor · rule · LLM
interpretation · user correction · user-approved folder; `ATTEMPTED_PRODUCERS` = direct · rule ·
llm). Tasks 4 and 5 own the literal spelling of each member. The thirteen `unresolved` reasons are
spelled at the call site, because Task 5's `write_unresolved` checks the value against
`UNRESOLVED_REASONS` through P4's `check` and a wrong spelling raises `NotInVocabulary` rather than
storing — this is `PLAN-tasks-14-15.md`'s own convention (`reason="no_candidate_evidence"`), followed
here for `discounted_tool_metadata` and `normalization_failed`.

---

## Verified live, 2026-08-22, by import and by execution — not from a document

Every one of these was run before a line of this plan was written, because three defects on this
project came from reading a signature instead of importing it.

```text
observations_for_file(conn, file_id) -> list[Observation]        spans EVERY content hash the file
                                                                 has had; ORDER BY rowid
observations_by_key(conn, observation_key) -> list[Observation]  ORDER BY rowid
runs_for_content(conn, content_hash) -> list[ExtractionRun]
unit_for_observation(conn, observation) -> TextUnit | None
record_run(conn, run) -> str · record_observation(conn, observation) -> str
Observation.observation_key      a @property, sha256:-prefixed, NOT a dataclass field
Observation.locator / .zone      also properties
Observation.__post_init__        raises NotInVocabulary on a source_type outside SOURCE_TYPES
SOURCE_TYPES                     14 members; ZONES 15; ANALYSIS_TIERS ("filesystem","native","ocr","llm")
files_table.get_file(conn, file_id) -> sqlite3.Row               no .get; wrap in dict()
files_table.record_file(conn, path, *, filename, normalized_filename, extension,
                        observed_size, observed_timestamps, parent_folder_context,
                        mime_type, detected_format, scan_state, materialized,
                        content_hash=None) -> str
FILES_COLUMNS                    sixteen; content_hash is 64 lowercase hex, no "sha256:" prefix
```

**Executed, not assumed:** writing fixture 1's observation at `extractor_version = "1.0.0"` and again
at `"2.0.0"` produces the **same** `observation_key` (`observation_key` hashes `content_hash ·
extractor_name · locator · raw_value` and nothing else), and `observations_by_key` then returns both
rows — which is the whole of M14 and Done-means 30, provable rather than asserted. `observations_by_key`
on a key no row carries returns `[]`, not an exception. `record_observation` needs no `files` row, so
Task 7's tests need no P1 file record and Task 8's — which reads one — creates its own.

**Also executed:** `evidence_shape.fixtures.by_number(n)` for all nineteen. The three these tasks use
are pinned here because a fixture is data and a plan that guesses at data is a plan that fails at
Step 2:

| # | design case | the bytes that matter |
|---|---|---|
| 1 | §2.8 "page 1, heading 2"; §3.2's syllabus | `raw_value="BUSIB 4300"`, zone `heading`, `reliability="possible"`, locator `heading:page=1/heading=2`, `context_before="Syllabus — "` (capital S, U+2014, one space either side), `context_after=" — Spring 2026"`, `context_truncated=False`, `occurrence_count=3` |
| 6 | §2.2 — `direct` describes the slot, not the value's usefulness | `raw_value="python-docx"`, zone `metadata`, locator `metadata:field=Producer`, `reliability="direct"`, extractor `docx.metadata/1.0.0` |
| 7 | §2.8's EXIF example; §3.2's capture-date derivation | `raw_value="2026:07:17 14:03:22"`, zone `metadata`, locator `metadata:field=DateTimeOriginal`, `reliability="direct"`, extractor `image.exif/1.0.0` |
| 18 | §2.9 design/creative, indexed-but-unreadable (M3) | `source_type="design_creative"`, zone `metadata`, locator `metadata:layer=3`, `raw_value="Background"` |

---

## The one cache-key rule Tasks 8 and 9 share

§3.4's key is *"content hash + extractor version + analysis tier + model identifier + prompt
fingerprint"*, and Task 6 publishes it as five scalar keywords. A fact built from several
observations has **several** extractor versions and **several** analysis tiers, and no task in this
plan owns the reconciliation. Tasks 8 and 9 therefore apply the rule
`PLAN-tasks-14-15.md` states, written out identically so the two documents cannot disagree:

- **`extractor_version`** is `canonical_json` of the sorted distinct `[extractor_name,
  extractor_version]` pairs of the observations the fact cites.
- **`analysis_tier`** is the **last** tier present in `ANALYSIS_TIERS` order — `filesystem` <
  `native` < `ocr` < `llm`. That is a reading of P4's published tuple order, not a new order, and it
  gives preamble rule 5 what it needs: a fact that cited an `ocr` observation lands in a different
  cache slot from one that cited only `native` observations, so pass 4 supersedes rather than
  overwrites.
- **`model_identifier` and `prompt_fingerprint` are `None`** on every deterministic fact. P4's
  `sha256_of` is length-prefixed and injective, so `None` is distinguishable from `""` in the digest.

**This is reported, not resolved.** The reconciliation belongs in `facts.cache`, which Task 6 owns;
these tasks cannot add to another task's module without breaking its contract. Counting
`PLAN-tasks-14-15.md`'s three copies, the rule now appears in **five** modules. See *Contract
ambiguities* at the end.

---

### Wave B — the citation layer and the deterministic producers (7–13 parallelise)

### Task 7: The evidence read — observation keys, the context pair, and `context_truncated`

**Files:**
- Create: `src/facts/evidence.py`
- Test: `tests/p6/test_p6_evidence.py`

**Interfaces:**
- Consumes: `evidence_shape.store` — `observations_for_file`, `observations_by_key`,
  `runs_for_content`, `unit_for_observation`; `evidence_shape.observation.Observation`.
- Produces: `observations_for_version(conn, file_id, content_hash) -> tuple[Observation, ...]`,
  `context_pair(observation) -> tuple[str, str, bool]`, `cite(observation) -> str`,
  `resolve_citation(conn, observation_key) -> tuple[Observation, ...]`,
  `analysis_tier_for_observation(conn, observation) -> str`.

**Done-means:** 6, 30.

**Why this is the first task of Wave B.** Every producer in Wave B and Wave C cites evidence, and the
one thing that must never be got wrong is *what* it cites. Putting the read first means no later task
has a plausible reason to touch `evidence_shape.store` directly, and the two guards this task
owns — the citation is a key, and no module branches per format — have exactly one place to look.
`PLAN-tasks-14-15.md` already imports `observations_for_version`, `cite` and
`analysis_tier_for_observation` from this module; the names below are that document's contract as
well as the skeleton's.

**The four properties this module exists to hold, each of which is a test rather than a comment.**

1. **The citation is `observation_key`, never `observation_id`.** M14. `observation_key` hashes
   `content_hash · extractor_name · locator · raw_value` and excludes `extractor_version` by
   construction, which is what makes a citation recorded today resolve after an extractor upgrade
   (§8.7: *"Rejected groups, rejected destination matches, rejected labels, and rejected residual
   recommendations must be stored with the evidence that produced them."* A reference that dies on a
   version bump cannot do that.) `observation_id` is per-row and P4-assigned; a fact citing one is a
   fact whose provenance an upgrade silently breaks.

2. **The read is per file *version*, and P4 publishes no such read.** `observations_for_file(conn,
   file_id)` spans every content hash the file has ever had. Every P6 computation is per version —
   the cache key is (§3.4) and the abstention row is (§8.2) — so the `content_hash` filter exists
   **once**, here. This is finding F12 and it is P4's gap, filtered rather than patched.

3. **The context is a pair, and the flag travels with it.** M5 split §2.8's *"surrounding context"*
   into `context_before` / `context_after` / `context_truncated` so §8.4 can redact a value without
   dropping its context. `context_pair` returns three values in one call so no caller can read the
   context without seeing the flag — §8.6, in the design's own words: *"A model prompt that exceeds
   its token budget should not truncate silently in a way that removes the decisive evidence."*
   Task 10 turns that flag into `reason = context_truncated` rather than `context_check_failed`;
   this module makes forgetting it impossible rather than merely discouraged.

4. **P6 branches on no format, ever.** §2.8 exists so downstream logic does not branch per format.
   Done-means 6 asserts P6 resolves a fixture whose `source type` is unknown to it. "Unknown to it"
   means a member of P4's fourteen that P6 has no code for — `Observation.__post_init__` rejects a
   value outside the vocabulary outright, verified by execution, so a genuinely novel string cannot
   even be constructed. The real assertion is the negative one: no module in `facts` holds a
   per-format dispatch table or names a format in code.

**`unit_for_observation` is listed in Consumes and is deliberately not called.** The text unit is the
span substrate §3.6's *quote* check needs, and that check is Task 17's. Calling it here to satisfy the
list would put a second reader of P4's text units in the part, and re-deriving context P4 already
split is exactly what M5 forbids. `Consumes:` states what the module may read; every name in
`Produces:` is delivered unchanged.

**Ordering is P6's, not P4's.** Verified by execution: `observations_for_file` is `ORDER BY rowid`,
which is insertion order, which is a property of the database and not of the corpus — writing the
same three fixtures as runs 1,2,3 and as 3,2,1 returns them in opposite orders. `observations_for_version`
therefore returns a **sorted tuple**, keyed on `observation_key`, so every consumer starts from a
total order that the same corpus produces in any write order. Task 11 sorts again by score before it
ranks; sorting twice is correct and sorting zero times is the defect §8.5's replay would report as a
fact-quality regression when nothing had changed.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_evidence.py
"""M14, Done-means 6 and 30 — keys, the context pair, truncation, and no per-format branching."""
from __future__ import annotations

import ast
import dataclasses
import importlib
import inspect
import pkgutil

import pytest

from evidence_shape.fixtures import by_number
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from evidence_shape.vocabulary import SOURCE_TYPES

import facts
from facts.evidence import (
    UnknownRun, analysis_tier_for_observation, cite, context_pair,
    observations_for_version, resolve_citation,
)

CLOCK = "2026-08-19T12:00:00+00:00"

#: A second content hash for the same `file_id`: the file was edited, so §3.4 puts its
#: facts in a different cache slot and §8.2 makes the old version's rows survive.
SECOND_HASH = "b" * 64

#: Every `extractor_name` P4's nineteen fixtures use. P6 must not contain one of these
#: strings in code: branching on the extractor is branching on the format (§2.8), and
#: F14 records that P4's fixture names and P5's live names already differ.
FIXTURE_EXTRACTORS = frozenset(
    by_number(n).run.extractor_name for n in range(1, 20))


def _run(conn, *, run_id, file_id, content_hash, extractor="pdf.text",
         version="1.0.0", source_type="text_document", tier="native"):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name=extractor, extractor_version=version,
        source_type=source_type, analysis_tier=tier, config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))


def _observe(conn, *, run_id, file_id, content_hash, raw, zone="heading",
             container_path=(), extractor="pdf.text", version="1.0.0",
             source_type="text_document", before=None, after=None,
             truncated=False):
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name=extractor,
        extractor_version=version, source_type=source_type, raw_value=raw,
        location=Location(zone, tuple(container_path)), occurrence_count=1,
        observed_at=CLOCK, reliability="possible", run_id=run_id,
        context_before=before, context_after=after, context_truncated=truncated)
    record_observation(conn, observation)
    return observation


def _code_strings(module) -> set[str]:
    """Every string literal in a module that is NOT a docstring.

    A source-text search matches comments and docstrings, and a guard that does that
    has broken three tasks on this project already (P5 PLAN, Task 20). This reads the
    code.
    """
    tree = ast.parse(inspect.getsource(module))
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)) and body:
            first = body[0]
            if (isinstance(first, ast.Expr)
                    and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                docstrings.add(id(first.value))
    return {node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
            and id(node) not in docstrings}


def _facts_modules():
    """Every module in the `facts` package, imported. Grows as siblings land."""
    for info in pkgutil.iter_modules(facts.__path__):
        yield importlib.import_module(f"facts.{info.name}")


# --- the per-version read (F12) ------------------------------------------------

def test_observations_for_version_does_not_return_a_prior_versions_observations(p6_conn):
    # §3.4 and §8.2 make every P6 computation per file *version*. P4 publishes only
    # `observations_for_file`, which spans content hashes; the filter lives here once.
    fixture = by_number(1)
    _run(p6_conn, run_id="r-old", file_id="file-01",
         content_hash=fixture.run.content_hash)
    _run(p6_conn, run_id="r-new", file_id="file-01", content_hash=SECOND_HASH)
    _observe(p6_conn, run_id="r-old", file_id="file-01",
             content_hash=fixture.run.content_hash, raw="BUSIB 4300")
    _observe(p6_conn, run_id="r-new", file_id="file-01",
             content_hash=SECOND_HASH, raw="PHYS 1401")

    new = observations_for_version(p6_conn, "file-01", SECOND_HASH)
    assert [one.raw_value for one in new] == ["PHYS 1401"]

    old = observations_for_version(p6_conn, "file-01", fixture.run.content_hash)
    assert [one.raw_value for one in old] == ["BUSIB 4300"]


def test_observations_for_version_returns_a_tuple_not_a_list(p6_conn):
    # A tuple is the shape `PLAN-tasks-14-15.md` stores on its `_Version` record, and
    # an immutable read is one fewer way a producer can reorder its own input.
    _run(p6_conn, run_id="r1", file_id="f1", content_hash=SECOND_HASH)
    _observe(p6_conn, run_id="r1", file_id="f1", content_hash=SECOND_HASH, raw="x")
    assert isinstance(observations_for_version(p6_conn, "f1", SECOND_HASH), tuple)


def test_the_read_order_is_p6s_own_and_not_p4s_insertion_order(p6_conn):
    # Verified by execution 2026-08-21: `observations_for_file` is ORDER BY rowid,
    # which is a property of this database and not of the corpus. Two files given the
    # same three values in opposite write orders must read back identically, or §8.5's
    # replay compares a run against itself and reports a regression.
    values = ["Columbia", "BUSIB 4300", "Wash U"]
    _run(p6_conn, run_id="r-fwd", file_id="f-fwd", content_hash=SECOND_HASH)
    _run(p6_conn, run_id="r-rev", file_id="f-rev", content_hash=SECOND_HASH)
    for raw in values:
        _observe(p6_conn, run_id="r-fwd", file_id="f-fwd",
                 content_hash=SECOND_HASH, raw=raw)
    for raw in reversed(values):
        _observe(p6_conn, run_id="r-rev", file_id="f-rev",
                 content_hash=SECOND_HASH, raw=raw)

    forward = observations_for_version(p6_conn, "f-fwd", SECOND_HASH)
    reverse = observations_for_version(p6_conn, "f-rev", SECOND_HASH)
    assert [one.raw_value for one in forward] == [one.raw_value for one in reverse]
    assert [cite(one) for one in forward] == sorted(cite(one) for one in forward)


# --- the citation (M14, Done-means 30) ----------------------------------------

def test_cite_returns_the_observation_key_and_never_the_observation_id(p6_conn):
    # M14. `observation_id` is per-row and P4-assigned; a fact citing one is a fact an
    # extractor upgrade silently orphans.
    _run(p6_conn, run_id="r1", file_id="f1", content_hash=SECOND_HASH)
    observation = _observe(p6_conn, run_id="r1", file_id="f1",
                           content_hash=SECOND_HASH, raw="Columbia")
    assert cite(observation) == observation.observation_key
    assert cite(observation).startswith("sha256:")
    assert not hasattr(observation, "observation_id")


def test_a_citation_stored_before_a_version_bump_still_resolves_after_it(p6_conn):
    # Done-means 30 and §8.7. `observation_key` hashes content_hash · extractor_name ·
    # locator · raw_value and NOT extractor_version, so the same reading re-extracted
    # at 2.0.0 carries the identical key and the stored reference resolves to both.
    fixture = by_number(1)
    _run(p6_conn, run_id="r-1", file_id="file-01",
         content_hash=fixture.run.content_hash)
    before = _observe(p6_conn, run_id="r-1", file_id="file-01",
                      content_hash=fixture.run.content_hash, raw="BUSIB 4300")
    stored = cite(before)

    _run(p6_conn, run_id="r-2", file_id="file-01",
         content_hash=fixture.run.content_hash, version="2.0.0")
    after = _observe(p6_conn, run_id="r-2", file_id="file-01",
                     content_hash=fixture.run.content_hash, raw="BUSIB 4300",
                     version="2.0.0")
    assert cite(after) == stored

    resolved = resolve_citation(p6_conn, stored)
    assert {one.extractor_version for one in resolved} == {"1.0.0", "2.0.0"}
    assert {one.raw_value for one in resolved} == {"BUSIB 4300"}


def test_resolve_citation_returns_empty_for_a_key_no_observation_carries(p6_conn):
    # §3.6 check 2 asks whether a cited quote is present in the evidence. An empty
    # answer is the answer; an exception would make an absent citation a crash.
    assert resolve_citation(p6_conn, "sha256:" + "0" * 64) == ()


def test_resolve_citation_is_ordered_and_not_p4s_rowid_order(p6_conn):
    # The newer extractor version is written FIRST, so P4's rowid order and P6's order
    # disagree and the assertion has something to catch.
    fixture = by_number(1)
    stored = ""
    for run_id, version in (("r-b", "2.0.0"), ("r-a", "1.0.0")):
        _run(p6_conn, run_id=run_id, file_id="file-01",
             content_hash=fixture.run.content_hash, version=version)
        stored = cite(_observe(
            p6_conn, run_id=run_id, file_id="file-01",
            content_hash=fixture.run.content_hash, raw="BUSIB 4300",
            version=version))

    resolved = resolve_citation(p6_conn, stored)
    assert [one.extractor_version for one in resolved] == ["1.0.0", "2.0.0"]


# --- the context pair (M5, §8.6) ----------------------------------------------

def test_context_pair_returns_two_values_and_never_a_concatenation(p6_conn):
    # M5: P4 split §2.8's "surrounding context" into two fields so §8.4 can redact a
    # value without dropping its context. Fixture 1's bytes, verbatim.
    _run(p6_conn, run_id="r1", file_id="f1", content_hash=SECOND_HASH)
    observation = _observe(p6_conn, run_id="r1", file_id="f1",
                           content_hash=SECOND_HASH, raw="BUSIB 4300",
                           before="Syllabus — ", after=" — Spring 2026")
    before, after, truncated = context_pair(observation)
    assert before == "Syllabus — "
    assert after == " — Spring 2026"
    assert truncated is False
    assert before + after not in (before, after)


def test_context_pair_hands_back_the_truncation_flag_with_the_context(p6_conn):
    # §8.6: "A model prompt that exceeds its token budget should not truncate silently
    # in a way that removes the decisive evidence." Three values in one call is how a
    # caller is stopped from reading the context without seeing the flag.
    _run(p6_conn, run_id="r1", file_id="f1", content_hash=SECOND_HASH)
    observation = _observe(p6_conn, run_id="r1", file_id="f1",
                           content_hash=SECOND_HASH, raw="BUSIB 4300",
                           before="…llabus ", after=" — Spri", truncated=True)
    assert context_pair(observation) == ("…llabus ", " — Spri", True)
    assert len(context_pair(observation)) == 3


def test_context_pair_renders_an_absent_context_as_the_empty_string(p6_conn):
    # Fixture 2 (the PDF title) carries context_before=None. A caller doing a
    # substring or word-boundary check on None raises; on "" it simply finds nothing.
    _run(p6_conn, run_id="r1", file_id="f1", content_hash=SECOND_HASH)
    observation = _observe(p6_conn, run_id="r1", file_id="f1",
                           content_hash=SECOND_HASH, raw="BUSIB 4300 Syllabus",
                           zone="title")
    assert observation.context_before is None
    assert context_pair(observation) == ("", "", False)


# --- the analysis tier comes from P4 and is never inferred ---------------------

def test_the_analysis_tier_is_read_from_p4s_run(p6_conn):
    # Global constraint: P6 never re-derives what P4 assigns. Inferring the tier from
    # `extractor_name` would encode the routing table in a second place.
    _run(p6_conn, run_id="r-ocr", file_id="f1", content_hash=SECOND_HASH,
         extractor="ocr.apple_vision", source_type="ocr", tier="ocr")
    observation = _observe(p6_conn, run_id="r-ocr", file_id="f1",
                           content_hash=SECOND_HASH, raw="Your Columbia University",
                           zone="ocr", extractor="ocr.apple_vision",
                           source_type="ocr")
    assert analysis_tier_for_observation(p6_conn, observation) == "ocr"


def test_an_observation_whose_run_was_never_recorded_raises(p6_conn):
    # Guessing a tier here would put the wrong value in §3.4's cache key, and a wrong
    # cache key is a fact that never invalidates. Refusing is the only safe answer.
    observation = Observation(
        file_id="f1", content_hash=SECOND_HASH, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value="x",
        location=Location("heading", ()), occurrence_count=1, observed_at=CLOCK,
        reliability="possible", run_id="run-that-does-not-exist")
    with pytest.raises(UnknownRun):
        analysis_tier_for_observation(p6_conn, observation)


# --- Done-means 6: no per-format branching ------------------------------------

def test_p6_reads_an_observation_whose_source_type_it_has_never_seen(p6_conn):
    # Done-means 6. Fixture 18 is `design_creative`, indexed-but-unreadable (M3) --
    # a source type nothing in `facts` was written against. It reads, it cites, and
    # its tier resolves, with no code added for it.
    fixture = by_number(18)
    record_run(p6_conn, fixture.run)
    for observation in fixture.observations:
        record_observation(p6_conn, observation)

    read = observations_for_version(p6_conn, fixture.run.file_id,
                                    fixture.run.content_hash)
    assert [one.raw_value for one in read] == ["Background"]
    assert cite(read[0]).startswith("sha256:")
    assert analysis_tier_for_observation(p6_conn, read[0]) == "native"
    assert context_pair(read[0]) == ("", "", False)


def test_a_source_type_outside_p4s_vocabulary_cannot_be_constructed_at_all():
    # Why Done-means 6 is read as "unknown to P6" and not "unknown to P4": P4 refuses
    # the latter at the record, so the only reachable case is a member of the fourteen
    # that P6 has no code for. Verified by execution, not by reading the docstring.
    from evidence_shape.vocabulary import NotInVocabulary
    with pytest.raises(NotInVocabulary):
        dataclasses.replace(by_number(1).observations[0],
                            source_type="holographic_scroll")


def test_no_facts_module_holds_a_dispatch_table_keyed_by_source_type():
    # §2.8 exists so downstream logic does not branch per format. "At least two keys,
    # all of them source types" is the shape of a real dispatch table; the bound is
    # two because `ocr` is a member of BOTH SOURCE_TYPES and ZONES, so a zone-keyed
    # map with a single `ocr` entry would otherwise read as a format branch.
    offenders = []
    for module in _facts_modules():
        for name, value in vars(module).items():
            if name.startswith("__") or not isinstance(value, dict):
                continue
            keys = {k for k in value if isinstance(k, str)}
            if len(keys) >= 2 and keys <= set(SOURCE_TYPES):
                offenders.append(f"{module.__name__}.{name}")
    assert offenders == []


def test_no_facts_module_names_a_source_type_or_an_extractor_in_code():
    # The stronger half: a single `if observation.source_type == "image"` is a format
    # branch too. Extractor names are checked against P4's nineteen fixtures because
    # F14 records that P4's fixture names and P5's live names already differ -- only
    # the no-branching rule keeps that harmless.
    forbidden = set(SOURCE_TYPES) | FIXTURE_EXTRACTORS
    offenders = []
    for module in _facts_modules():
        for literal in _code_strings(module) & forbidden:
            offenders.append(f"{module.__name__}: {literal!r}")
    assert offenders == []
```

- [ ] **Step 2: Run the test and read the failure**

Run: `pytest tests/p6/test_p6_evidence.py -v`

Expected: FAIL — collection errors with
`ModuleNotFoundError: No module named 'facts.evidence'`. Tasks 1–6 are green, so `facts`,
`facts.schema`, `facts.fields`, `facts.values`, `facts.file_facts`, `facts.unresolved` and
`facts.cache` all import; `facts.evidence` is the only missing name and it is the one this task
creates. **16 tests fail to collect, 0 pass.**

- [ ] **Step 3: Write the implementation**

```python
# src/facts/evidence.py
"""The read over P4, and the one place P6 turns an observation into a citation.

Four properties live here because each of them must exist exactly once:

* **The citation is `observation_key`** (M14). It hashes `content_hash · extractor_name
  · locator · raw_value` and excludes `extractor_version` by construction, so a
  reference stored today resolves after an extractor upgrade -- which is what §8.7's
  requirement that rejected proposals "must be stored with the evidence that produced
  them" needs in order to still mean something in six months. `observation_id` is
  P4's per-row identity and is never cited.

* **The read is per file version.** §3.4's cache key and §8.2's abstention row are both
  per content hash, and P4 publishes only `observations_for_file`, which spans every
  hash the file has ever had. The filter is here and nowhere else (finding F12).

* **The context is a pair with its flag** (M5, §8.6). `context_before` and
  `context_after` are never concatenated, and `context_truncated` is returned beside
  them so a caller cannot read one without the other. §8.6: a prompt over budget
  "should not truncate silently in a way that removes the decisive evidence."

* **Nothing here branches on a format.** §2.8 exists so downstream logic does not, and
  Done-means 6 asserts P6 resolves a source type it has never seen. There is no
  mapping keyed by `source_type` and no string naming one anywhere in `facts`;
  `tests/p6/test_p6_evidence.py` asserts that by runtime introspection of every
  module in the package, not by reading the source text.

P4's reads are `ORDER BY rowid`, which is insertion order -- a property of the
database, not of the corpus. Every read published here imposes a total order of P6's
own before returning, so the same corpus extracted in a different order produces the
same facts (§8.5 replay).

`unit_for_observation` is part of P4's read surface and is deliberately not called
here: the text unit is the span substrate §3.6's quote check needs, and that check is
the P8 seam's. Re-deriving context P4 already split is what M5 forbids.
"""
from __future__ import annotations

import sqlite3
from typing import Iterable

from evidence_shape.observation import Observation
from evidence_shape.store import (
    observations_by_key, observations_for_file, runs_for_content,
)


class UnknownRun(Exception):
    """An observation whose `run_id` has no `extraction_runs` row.

    P6 never re-derives what P4 assigns, so there is no fallback: an inferred
    `analysis_tier` would land in §3.4's cache key, and a wrong cache key is a fact
    that never invalidates.
    """


def cite(observation: Observation) -> str:
    """M14: the citation handle P6 stores. Content-addressed, version-independent."""
    return observation.observation_key


def observations_for_version(conn: sqlite3.Connection, file_id: str,
                             content_hash: str) -> tuple[Observation, ...]:
    """Every observation P4 holds for one *version* of one file, in P6's own order.

    P4's `observations_for_file` spans content hashes and returns insertion order.
    Both are corrected here: the filter is §3.4's per-version scope, and the sort is
    the total order every downstream ranking starts from.
    """
    return _ordered(one for one in observations_for_file(conn, file_id)
                    if one.content_hash == content_hash)


def resolve_citation(conn: sqlite3.Connection,
                     observation_key: str) -> tuple[Observation, ...]:
    """Every observation carrying this key -- one per extractor version that saw it.

    Returns an empty tuple when nothing carries the key: §3.6 check 2 asks whether a
    cited quote is present in the evidence, and "no" is an answer, not a crash.
    """
    return _ordered(observations_by_key(conn, observation_key))


def context_pair(observation: Observation) -> tuple[str, str, bool]:
    """§2.8's surrounding context, as M5 split it: `(before, after, truncated)`.

    Never a concatenation, and never the pair without the flag. `None` renders as the
    empty string so a word-boundary check over an absent context finds nothing rather
    than raising.
    """
    return (observation.context_before or "",
            observation.context_after or "",
            bool(observation.context_truncated))


def analysis_tier_for_observation(conn: sqlite3.Connection,
                                  observation: Observation) -> str:
    """I4's tier, read from P4's run. Never inferred from the extractor or the zone."""
    for run in runs_for_content(conn, observation.content_hash):
        if run.run_id == observation.run_id:
            return run.analysis_tier
    raise UnknownRun(
        f"observation {observation.observation_key} names run "
        f"{observation.run_id!r}, which has no extraction_runs row; P6 reads "
        f"analysis_tier from P4 and derives it from nothing"
    )


def _ordered(observations: Iterable[Observation]) -> tuple[Observation, ...]:
    """Score-free total order: `observation_key` ascending, then extractor version.

    The key is content-addressed, so this order is a property of the corpus. P4's
    `rowid` order is a property of the database and reverses when the same three runs
    are written in the opposite sequence (verified by execution, 2026-08-21).
    """
    return tuple(sorted(observations,
                        key=lambda one: (one.observation_key,
                                         one.extractor_version, one.run_id)))
```

- [ ] **Step 4: Run the test and confirm it passes**

Run: `pytest tests/p6/test_p6_evidence.py -v`

Expected: PASS — **16 passed**. In particular
`test_a_citation_stored_before_a_version_bump_still_resolves_after_it` passes because
`observation_key` excludes `extractor_version` (executed and confirmed before this plan was
written), and the two introspection guards pass over every `facts` module that exists at the time
the suite runs, including the siblings landing in parallel.

- [ ] **Step 5: Run the whole P6 suite, so a sibling's module is not broken by the guards**

Run: `pytest tests/p6 -q`

Expected: PASS. The two guards in this file walk `pkgutil.iter_modules(facts.__path__)`, so they
police modules this task did not write. A failure here is a real finding — a sibling holding a
format-keyed table — and is reported to that task's author rather than fixed by weakening the guard.

- [ ] **Step 6: Commit**

```bash
git add src/facts/evidence.py tests/p6/test_p6_evidence.py
git commit -m "feat(P6): the evidence read — observation keys, the context pair, context_truncated"
```

---
