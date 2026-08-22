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
from evidence_shape.location import Location
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

### Task 8: Direct facts — §3.5's four explicit slots

**Files:**
- Create: `src/facts/direct.py`
- Test: `tests/p6/test_p6_direct.py`

**Interfaces:**
- Consumes: `facts.evidence` — `observations_for_version`, `cite`, `analysis_tier_for_observation`;
  `facts.file_facts` — `write_fact`, `FACT_ORIGINS`; `facts.values` — `ensure_value`, `VALUE_ORIGINS`;
  `facts.unresolved` — `write_unresolved`, `ATTEMPTED_PRODUCERS`; `facts.states.STATES`;
  `facts.cache.fact_cache_key`; `database_agent.files_table.get_file`;
  `evidence_shape.canonical.canonical_json`; `evidence_shape.vocabulary.ANALYSIS_TIERS`.
- Produces: `direct_facts(conn, *, file_id, content_hash, slots: DirectSlots) -> tuple[str, ...]`,
  `DirectSlots` — an injected frozen dataclass of slot-name predicates, no defaults.
  **Two names are added to the skeleton's block:** `DirectSlot` (the member type `DirectSlots` is a
  dataclass *of*) and `SLOT_KINDS` (its own field names, read off the dataclass so there is no second
  spelling). Neither collides with any other task's surface; both are recorded under *Contract
  additions* at the end.

**Done-means:** 5, and part of 4.

**§3.5, verbatim, because the sentence is the whole task:**

> *"A file fact is not inherently rule-based or LLM-based. It is the common format into which both
> systems write their conclusions. Deterministic extractors create direct facts when the information
> comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a document title,
> or a labeled form field."*

§3.13 says it again in the reliability table: *"A direct fact was read from a reliable and explicit
source, such as a content hash, EXIF timestamp, document title, or labeled form field."* And §3.2
gives the worked pair: *"an EXIF field called DateTimeOriginal is raw metadata; capture date =
2026-07-17 is the file fact derived from it."* That pair is Done-means 5.

**The distinction this task exists to hold: `direct` describes the SLOT, not the value.** The SPEC's
production rule adds the sentence that makes the boundary testable — *"Filesystem timestamps are
direct; dates recovered from text or filenames are not, and take the §3.10 path."* The same date
string in two places is two different reliability states, and which one it gets is decided by where
P4 recorded it, not by what it says. P4's fixture 6 is the same rule seen from the other side:
`raw_value = "python-docx"` at `reliability = "direct"` because the Producer field is a labeled slot,
while §2.2 says the value is worthless — that is Task 9's half and it is not a contradiction.

**P6 holds no slot name, and this is why (finding F8).** P5 emits every image observation with the
EXIF tag name carried **only** as a reader-supplied `container_path` segment label, and spells no tag
name anywhere, deliberately — P4 D7 requires *"the source format's own slot name, verbatim"*. P4's
fixture 7 uses `DateTimeOriginal`, but a fixture is data, not a vocabulary. A literal
`"DateTimeOriginal"` inside `facts` would be P6 inventing a vocabulary member P5 refused to publish,
and Task 7's introspection guard would not catch it. So the slot map is **injected**, and the test
below is the only place in the part where a slot name appears.

**F8 is now half-closed and the plan records it rather than re-reporting it.**
`planning/deferred-catalogues/12-academic-capture-patterns/04-narrow-date-families.json` was authored
2026-08-22 and carries two `family_kind: "metadata_slot"` entries — `fam-exif-datetimeoriginal`
(`slot_names: ["DateTimeOriginal"]`, `may_fill: ["capture_date"]`, `reliability: "direct"`) and
`fam-labeled-creation-date` (`slot_names: ["CreationDate (PDF)", "created (DOCX core properties,
dcterms)"]`, `may_fill: ["creation_date"]`). Its own `owner` line names *"Task 8's direct-fact slot
list for EXIF/metadata dates"*. That is the catalogue F8 said did not exist, for **two** of the four
slots. The document-title and content-hash slots still have none. That file is another agent's and is
read, never edited.

**What `get_file` is for, and the one thing P1 owns here.** §0 makes identity P1's. The content-hash
slot is the only §3.5 source whose true value lives in a column rather than in an observation, so
`direct_facts` reads P1's row once and requires a content-hash slot's normalized value to **equal**
`files.content_hash`. A slot that claims to carry the file's hash and carries something else is not
*"a reliable and explicit source"*, and P6 refuses it with `reason = normalization_failed` rather than
storing a second, disagreeing identity.

**Two refusals that are deliberately different, and the reasoning is the load-bearing part.**

- **A slot that recognises nothing writes NOTHING — no fact and no `unresolved` row.** This looks like
  it contradicts B7, and it does not. §8.6 fixes the producer order — direct, then rule-validated,
  then LLM — so a field with no direct evidence has not been refused, it has not been *finished*. An
  abstention row written here would record a refusal for a field Task 10 then fills, and Done-means
  19 would be false: the `unresolved` row would sit beside an active fact for the same
  `(file_id, content_hash, field_key)`. The abstention belongs at the end of the sequence, which is
  Task 20's resolver. **This is stated here because it is the single most likely place for a
  reviewer to think the plan has dropped B7.**
- **A slot that recognises an observation whose value will not normalize DOES write one.** Evidence
  was present, P6 looked at it, and P6 declined — that is exactly the refusal §8.5 asks about under
  Fact quality, and it carries the observation key it considered.

**No fuzzy anything.** The normalizer is the caller's. `direct.py` parses no date, compiles no
pattern, and holds no regex; it calls `rule.normalize(raw)` and treats `None` as a refusal. §3.10's
*"no fuzzy date parsing, ever"* is therefore not a rule this module can break.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_direct.py
"""Done-means 5, and §3.5's four explicit slots. `direct` describes the slot."""
from __future__ import annotations

import ast
import inspect
import json
import re
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file

from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import observations_for_file, record_observation, record_run

from facts import direct as direct_module
from facts.direct import SLOT_KINDS, DirectSlot, DirectSlots, direct_facts
from facts.file_facts import facts_for_file
from facts.unresolved import unresolved_for_file
from facts.values import values_in_field

CLOCK = "2026-08-19T12:00:00+00:00"

#: The only place in P6 where a format's own slot name is written down. P5 spells none
#: (P4 D7 keeps "the source format's own slot name, verbatim"), so P6 receives them.
#: The two date families come from catalogue 12/04's `metadata_slot` entries.
EXIF_CAPTURE_SLOT = "DateTimeOriginal"
PDF_CREATION_SLOT = "CreationDate"
MIME_SLOT = "mime_type"

#: Catalogue 12/04, `fam-exif-datetimeoriginal.value_pattern`, verbatim.
EXIF_DATETIME = re.compile(
    r"^(19|20)\d{2}:(0[1-9]|1[0-2]):(0[1-9]|[12]\d|3[01])"
    r"( ([01]\d|2[0-3]):[0-5]\d:[0-5]\d)?$")

#: Catalogue 12/04, `fam-labeled-creation-date`, the PDF `D:` half.
PDF_DATETIME = re.compile(r"^D:(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])")


def _code_strings(module) -> set[str]:
    """Every string literal in a module that is NOT a docstring (see Task 7)."""
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


def _record(conn, tmp_path, *, name, body, parent="Photos"):
    """One P1 `files` row over real bytes, so the content hash is P1's own."""
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context=parent, mime_type="image/jpeg",
        detected_format="jpeg", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, zone="metadata",
             label=None, extractor="image.exif", version="1.0.0",
             source_type="image", tier="native", new_run=True):
    if new_run:
        record_run(conn, ExtractionRun(
            run_id=run_id, file_id=file_id, content_hash=content_hash,
            extractor_name=extractor, extractor_version=version,
            source_type=source_type, analysis_tier=tier, config={},
            completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    container = (Segment("field", label=label),) if label else ()
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name=extractor,
        extractor_version=version, source_type=source_type, raw_value=raw,
        location=Location(zone, container), occurrence_count=1, observed_at=CLOCK,
        reliability="direct", run_id=run_id)
    record_observation(conn, observation)
    return observation


# --- the injected slot map: the only place a slot name is written ---------------

def _labelled(*labels):
    """Recognise a labeled metadata slot by the label P4 stored verbatim (D7)."""
    wanted = frozenset(labels)
    def recognises(observation) -> bool:
        return observation.location.zone == "metadata" and any(
            segment.kind == "field" and segment.label in wanted
            for segment in observation.location.container_path)
    return recognises


def _in_zone(zone: str):
    def recognises(observation) -> bool:
        return observation.location.zone == zone
    return recognises


def _exif_date(raw: str) -> str | None:
    """Catalogue 12/04's `exif_datetime` layout -> an ISO date. No fuzzy fallback."""
    if not EXIF_DATETIME.match(raw):
        return None
    return raw[:10].replace(":", "-")


def _pdf_date(raw: str) -> str | None:
    if not PDF_DATETIME.match(raw):
        return None
    return f"{raw[2:6]}-{raw[6:8]}-{raw[8:10]}"


def _verbatim(raw: str) -> str | None:
    return raw.strip() or None


def _slots(*, content_hash=(), exif_timestamp=(), document_title=(),
           labeled_form_field=()) -> DirectSlots:
    return DirectSlots(content_hash=tuple(content_hash),
                       exif_timestamp=tuple(exif_timestamp),
                       document_title=tuple(document_title),
                       labeled_form_field=tuple(labeled_form_field))


CAPTURE = DirectSlot(field_key="capture_date",
                     recognises=_labelled(EXIF_CAPTURE_SLOT),
                     normalize=_exif_date)
CREATED = DirectSlot(field_key="creation_date",
                     recognises=_labelled(PDF_CREATION_SLOT),
                     normalize=_pdf_date)
FILE_TYPE = DirectSlot(field_key="file_type", recognises=_labelled(MIME_SLOT),
                       normalize=_verbatim)
WORK_TYPE = DirectSlot(field_key="work_type", recognises=_in_zone("title"),
                       normalize=lambda raw: raw.strip().casefold() or None)


# --- Done-means 5 ---------------------------------------------------------------

def test_an_exif_datetimeoriginal_observation_produces_capture_date_as_direct(
        p6_conn, tmp_path):
    # §3.2: "an EXIF field called DateTimeOriginal is raw metadata; capture date =
    # 2026-07-17 is the file fact derived from it." P4's fixture 7's raw value.
    file_id, content_hash = _record(p6_conn, tmp_path, name="IMG_0042.jpg",
                                    body=b"jpeg-bytes")
    _observe(p6_conn, run_id="r1", file_id=file_id, content_hash=content_hash,
             raw="2026:07:17 14:03:22", label=EXIF_CAPTURE_SLOT)

    written = direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                           slots=_slots(exif_timestamp=(CAPTURE,)))
    assert len(written) == 1

    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert len(rows) == 1
    assert rows[0]["reliability_state"] == "direct"
    assert [row["canonical_value"] for row in
            values_in_field(p6_conn, "capture_date")] == ["2026-07-17"]


def test_the_exif_observation_stays_readable_with_its_raw_value_unchanged(
        p6_conn, tmp_path):
    # §3.2: "the product must preserve both the original evidence and the conclusion
    # built from it." P4's `evidence_never_overwritten` trigger makes this
    # unfalsifiable; the test asserts the intent so a reviewer sees it stated.
    file_id, content_hash = _record(p6_conn, tmp_path, name="IMG_0042.jpg",
                                    body=b"jpeg-bytes")
    _observe(p6_conn, run_id="r1", file_id=file_id, content_hash=content_hash,
             raw="2026:07:17 14:03:22", label=EXIF_CAPTURE_SLOT)
    direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                 slots=_slots(exif_timestamp=(CAPTURE,)))

    after = observations_for_file(p6_conn, file_id)
    assert [one.raw_value for one in after] == ["2026:07:17 14:03:22"]


def test_every_direct_fact_cites_the_observation_key_that_supported_it(
        p6_conn, tmp_path):
    # Done-means 30 / M14, from the write side.
    file_id, content_hash = _record(p6_conn, tmp_path, name="IMG_0042.jpg",
                                    body=b"jpeg-bytes")
    observation = _observe(p6_conn, run_id="r1", file_id=file_id,
                           content_hash=content_hash, raw="2026:07:17 14:03:22",
                           label=EXIF_CAPTURE_SLOT)
    direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                 slots=_slots(exif_timestamp=(CAPTURE,)))

    row = facts_for_file(p6_conn, file_id, content_hash)[0]
    assert json.loads(row["evidence_refs"]) == [observation.observation_key]


# --- §3.5's distinction: the slot decides, not the string ----------------------

def test_a_labeled_date_slot_is_direct_and_the_same_date_in_body_text_is_not(
        p6_conn, tmp_path):
    # "Filesystem timestamps are direct; dates recovered from text or filenames are
    # not, and take the §3.10 path" (P6 SPEC, production rules). Two observations,
    # one date, two outcomes -- decided by where P4 recorded it.
    file_id, content_hash = _record(p6_conn, tmp_path, name="report.pdf",
                                    body=b"pdf-bytes")
    _observe(p6_conn, run_id="r1", file_id=file_id, content_hash=content_hash,
             raw="D:20260717093000+00'00'", label=PDF_CREATION_SLOT,
             extractor="pdf.text", source_type="text_document")
    _observe(p6_conn, run_id="r2", file_id=file_id, content_hash=content_hash,
             raw="D:20260717093000+00'00'", zone="body", extractor="pdf.text",
             source_type="text_document")

    direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                 slots=_slots(labeled_form_field=(CREATED,)))

    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert len(rows) == 1
    assert rows[0]["reliability_state"] == "direct"
    assert json.loads(rows[0]["evidence_refs"]) == [
        one.observation_key for one in observations_for_file(p6_conn, file_id)
        if one.location.zone == "metadata"]


def test_a_field_with_no_direct_evidence_is_left_for_the_next_producer(
        p6_conn, tmp_path):
    # NOT a B7 hole. §8.6 fixes the order direct -> rule -> LLM, so a field with no
    # direct evidence has not been refused, it has not been finished. An abstention
    # here would sit beside the fact Task 10 writes and break Done-means 19.
    file_id, content_hash = _record(p6_conn, tmp_path, name="report.pdf",
                                    body=b"pdf-bytes")
    _observe(p6_conn, run_id="r1", file_id=file_id, content_hash=content_hash,
             raw="BUSIB 4300", zone="heading", extractor="pdf.text",
             source_type="text_document")

    assert direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                        slots=_slots(exif_timestamp=(CAPTURE,))) == ()
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    assert unresolved_for_file(p6_conn, file_id, content_hash) == []


def test_a_recognised_slot_whose_value_will_not_normalize_is_a_recorded_refusal(
        p6_conn, tmp_path):
    # Catalogue 12/04's own `examples_false`: an ISO layout sitting in the EXIF slot
    # is "normalization_failed, not a guessed parse". Evidence was there and P6
    # declined, so §8.5's "did it abstain when evidence was absent" has a row to read.
    file_id, content_hash = _record(p6_conn, tmp_path, name="IMG_0042.jpg",
                                    body=b"jpeg-bytes")
    observation = _observe(p6_conn, run_id="r1", file_id=file_id,
                           content_hash=content_hash,
                           raw="2026-07-17 09:30:00", label=EXIF_CAPTURE_SLOT)

    assert direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                        slots=_slots(exif_timestamp=(CAPTURE,))) == ()
    assert facts_for_file(p6_conn, file_id, content_hash) == []

    rows = unresolved_for_file(p6_conn, file_id, content_hash,
                               field_key="capture_date")
    assert len(rows) == 1
    assert rows[0]["reason"] == "normalization_failed"
    assert json.loads(rows[0]["evidence_refs"]) == [observation.observation_key]


# --- P1 owns identity (§0) ------------------------------------------------------

def test_a_content_hash_slot_disagreeing_with_p1s_column_is_refused(
        p6_conn, tmp_path):
    # §0 makes identity P1's. A slot claiming the file's hash and carrying another is
    # not "a reliable and explicit source"; storing it would be a second identity.
    file_id, content_hash = _record(p6_conn, tmp_path, name="a.pdf", body=b"one")
    _observe(p6_conn, run_id="r1", file_id=file_id, content_hash=content_hash,
             raw="f" * 64, label="content_hash", extractor="fs.basic",
             source_type="filesystem", tier="filesystem")

    slot = DirectSlot(field_key="duplicate_family",
                      recognises=_labelled("content_hash"), normalize=_verbatim)
    assert direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                        slots=_slots(content_hash=(slot,))) == ()
    rows = unresolved_for_file(p6_conn, file_id, content_hash,
                               field_key="duplicate_family")
    assert [row["reason"] for row in rows] == ["normalization_failed"]


def test_a_content_hash_slot_agreeing_with_p1s_column_is_a_direct_fact(
        p6_conn, tmp_path):
    file_id, content_hash = _record(p6_conn, tmp_path, name="a.pdf", body=b"one")
    _observe(p6_conn, run_id="r1", file_id=file_id, content_hash=content_hash,
             raw=content_hash, label="content_hash", extractor="fs.basic",
             source_type="filesystem", tier="filesystem")

    slot = DirectSlot(field_key="duplicate_family",
                      recognises=_labelled("content_hash"), normalize=_verbatim)
    assert len(direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                            slots=_slots(content_hash=(slot,)))) == 1
    assert facts_for_file(p6_conn, file_id,
                          content_hash)[0]["reliability_state"] == "direct"


# --- one row per (field, value), per §3.12 -------------------------------------

def test_two_observations_carrying_one_value_produce_one_fact_citing_both(
        p6_conn, tmp_path):
    # P6 SPEC, `file_facts`: "One row = one (file, field, value) connection" -- the
    # SPEC's reading of §3.12. Two readings of the same
    # slot are two citations on one fact, not two facts.
    file_id, content_hash = _record(p6_conn, tmp_path, name="a.pdf", body=b"one")
    first = _observe(p6_conn, run_id="r1", file_id=file_id,
                     content_hash=content_hash, raw="application/pdf",
                     label=MIME_SLOT, extractor="fs.basic",
                     source_type="filesystem", tier="filesystem")
    second = _observe(p6_conn, run_id="r2", file_id=file_id,
                      content_hash=content_hash, raw="application/pdf ",
                      label=MIME_SLOT, extractor="pdf.text",
                      source_type="text_document")

    assert len(direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                            slots=_slots(labeled_form_field=(FILE_TYPE,)))) == 1
    row = facts_for_file(p6_conn, file_id, content_hash)[0]
    assert json.loads(row["evidence_refs"]) == sorted(
        [first.observation_key, second.observation_key])


def test_the_result_does_not_depend_on_the_order_the_runs_were_written(
        p6_conn, tmp_path):
    # P4's reads are `ORDER BY rowid` (verified by execution). Two files given the
    # same two readings in opposite order must produce byte-identical citations.
    left, left_hash = _record(p6_conn, tmp_path, name="left.pdf", body=b"same")
    right, right_hash = _record(p6_conn, tmp_path, name="right.pdf", body=b"same")
    for run_id, raw in (("l1", "application/pdf"), ("l2", "application/pdf ")):
        _observe(p6_conn, run_id=run_id, file_id=left, content_hash=left_hash,
                 raw=raw, label=MIME_SLOT, extractor="fs.basic",
                 source_type="filesystem", tier="filesystem")
    for run_id, raw in (("r2", "application/pdf "), ("r1", "application/pdf")):
        _observe(p6_conn, run_id=run_id, file_id=right, content_hash=right_hash,
                 raw=raw, label=MIME_SLOT, extractor="fs.basic",
                 source_type="filesystem", tier="filesystem")

    for file_id, digest in ((left, left_hash), (right, right_hash)):
        direct_facts(p6_conn, file_id=file_id, content_hash=digest,
                     slots=_slots(labeled_form_field=(FILE_TYPE,)))
    rows = [facts_for_file(p6_conn, file_id, digest)[0]
            for file_id, digest in ((left, left_hash), (right, right_hash))]
    assert json.loads(rows[0]["evidence_refs"]) == json.loads(
        rows[1]["evidence_refs"])
    assert rows[0]["cache_key"] == rows[1]["cache_key"]


def test_a_second_version_of_the_file_resolves_on_its_own_evidence(
        p6_conn, tmp_path):
    # §3.4 and §8.2 make the fact per file *version*. Task 7's filter is what makes
    # this true; this is the producer-side assertion of it.
    file_id, content_hash = _record(p6_conn, tmp_path, name="IMG.jpg", body=b"v1")
    _observe(p6_conn, run_id="r1", file_id=file_id, content_hash=content_hash,
             raw="2026:07:17 14:03:22", label=EXIF_CAPTURE_SLOT)
    second = "c" * 64
    _observe(p6_conn, run_id="r2", file_id=file_id, content_hash=second,
             raw="2024:01:02 08:00:00", label=EXIF_CAPTURE_SLOT)

    direct_facts(p6_conn, file_id=file_id, content_hash=second,
                 slots=_slots(exif_timestamp=(CAPTURE,)))
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    assert len(facts_for_file(p6_conn, file_id, second)) == 1
    assert [row["canonical_value"] for row in
            values_in_field(p6_conn, "capture_date")] == ["2024-01-02"]


def test_the_cache_key_carries_the_tier_of_the_observations_the_fact_cited(
        p6_conn, tmp_path):
    # Preamble rule 5: pass 4 must SUPERSEDE, not overwrite. It can only do that if a
    # fact citing an `ocr` reading lands in a different §3.4 slot from one citing only
    # `native` readings, so the tier reconciliation is asserted, not assumed.
    #
    # Identical bytes and an identical extractor on both sides, so content hash and
    # the extractor-version part of the key are equal and `analysis_tier` is the ONLY
    # difference. P4 accepts `pdf.text` at the `ocr` tier -- verified by execution --
    # which is what lets this test isolate the one part it is about.
    left, left_hash = _record(p6_conn, tmp_path, name="a.pdf", body=b"same bytes")
    right, right_hash = _record(p6_conn, tmp_path, name="b.pdf", body=b"same bytes")
    assert left_hash == right_hash
    _observe(p6_conn, run_id="n1", file_id=left, content_hash=left_hash,
             raw="application/pdf", label=MIME_SLOT, extractor="pdf.text",
             source_type="text_document", tier="native")
    _observe(p6_conn, run_id="o1", file_id=right, content_hash=right_hash,
             raw="application/pdf", label=MIME_SLOT, extractor="pdf.text",
             source_type="text_document", tier="ocr")

    for file_id in (left, right):
        direct_facts(p6_conn, file_id=file_id, content_hash=left_hash,
                     slots=_slots(labeled_form_field=(FILE_TYPE,)))
    native = facts_for_file(p6_conn, left, left_hash)[0]
    ocr = facts_for_file(p6_conn, right, right_hash)[0]
    assert native["evidence_refs"] == ocr["evidence_refs"]
    assert native["cache_key"] != ocr["cache_key"]


# --- the injection property (Task 25 asserts the general form) ------------------

def test_slot_kinds_are_3_5s_four_and_are_read_off_the_dataclass():
    assert SLOT_KINDS == ("content_hash", "exif_timestamp", "document_title",
                          "labeled_form_field")


def test_direct_slots_has_no_default_for_any_of_the_four():
    # §3.7 and §3.10's deferred values are held as required keywords with no default,
    # and the slot map is the same shape: omitting one is a TypeError, supplying an
    # empty tuple is a decision the caller made and can be read back.
    with pytest.raises(TypeError):
        DirectSlots(content_hash=(), exif_timestamp=(), document_title=())
    empty = _slots()
    assert empty.labeled_form_field == ()


def test_facts_direct_names_no_slot_and_no_field_of_its_own():
    # F8: P5 spells no EXIF tag name (P4 D7), so a literal here would be P6 inventing
    # a vocabulary member P5 refused to publish. The field keys are the caller's too:
    # §3.5 names the SLOT and never says which field it fills.
    forbidden = {EXIF_CAPTURE_SLOT, PDF_CREATION_SLOT, MIME_SLOT, "content_hash",
                 "capture_date", "creation_date", "file_type", "work_type",
                 "duplicate_family"}
    assert _code_strings(direct_module) & forbidden == set()


def test_facts_direct_holds_no_module_level_slot_table():
    # Task 25 asserts this across the part by runtime introspection; the local half
    # lives with the module that would be tempted to carry one.
    tables = [name for name, value in vars(direct_module).items()
              if isinstance(value, (dict, frozenset, set))
              and not name.startswith("__")]
    assert tables == []
```

- [ ] **Step 2: Run the test and read the failure**

Run: `pytest tests/p6/test_p6_direct.py -v`

Expected: FAIL — collection error, `ModuleNotFoundError: No module named 'facts.direct'`.
`facts.evidence` imports (Task 7 is green), so this is the only missing name.
**16 tests fail to collect, 0 pass.**

- [ ] **Step 3: Write the implementation**

```python
# src/facts/direct.py
"""§3.5's first producer: facts read from a reliable, explicit slot.

§3.5, verbatim: "Deterministic extractors create direct facts when the information
comes from a reliable, explicit source, such as a content hash, EXIF timestamp, a
document title, or a labeled form field." §3.13 repeats the four in the reliability
table, and §3.2 gives the worked pair -- "an EXIF field called DateTimeOriginal is raw
metadata; capture date = 2026-07-17 is the file fact derived from it."

**`direct` describes the SLOT, not the value.** P4's fixture 6 is the same rule from
the other side: `raw_value = "python-docx"` at `reliability = "direct"`, because the
Producer field is a labeled slot -- while §2.2 says the value is worthless. That is
`facts.discount`'s half and it is not a contradiction. The SPEC's production rule
states the boundary this module holds: "Filesystem timestamps are direct; dates
recovered from text or filenames are not, and take the §3.10 path."

**P6 holds no slot name and no field mapping.** P5 emits the EXIF tag name only as a
reader-supplied `container_path` segment label and spells no tag name anywhere (P4 D7:
"the source format's own slot name, verbatim"). A literal here would be P6 inventing a
vocabulary member P5 refused to publish, so `DirectSlots` is injected with no default,
and each slot carries its own `field_key` and its own `normalize` -- §3.5 names the
slot and never says which field it fills. Two of the four slots now have a catalogue:
`12-academic-capture-patterns/04-narrow-date-families.json` names
`fam-exif-datetimeoriginal` -> `capture_date` and `fam-labeled-creation-date` ->
`creation_date`. It is data, loaded by the caller, never imported here.

**No parsing lives here.** `normalize` is the caller's callable and `None` is its
refusal. §3.10's "no fuzzy date parsing, ever" is therefore not a rule this module can
break: it compiles no pattern and reads no date.

**Two refusals, deliberately different.** A slot that recognises nothing writes
nothing -- §8.6 fixes the producer order direct -> rule -> LLM, so a field with no
direct evidence has not been refused, it has not been finished, and an abstention here
would sit beside the fact the rule producer writes and falsify Done-means 19. A slot
that recognises an observation whose value will not normalize writes one `unresolved`
row: evidence was present, P6 looked at it and declined, and §8.5 asks exactly that.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, fields as dataclass_fields
from typing import Callable, Iterable

from database_agent.files_table import get_file

from evidence_shape.canonical import canonical_json
from evidence_shape.observation import Observation
from evidence_shape.vocabulary import ANALYSIS_TIERS

from facts.cache import fact_cache_key
from facts.evidence import analysis_tier_for_observation, cite, observations_for_version
from facts.file_facts import FACT_ORIGINS, write_fact
from facts.states import STATES
from facts.unresolved import ATTEMPTED_PRODUCERS, write_unresolved
from facts.values import VALUE_ORIGINS, ensure_value

#: §3.13's second state, addressed by position so the six literals stay spelled once,
#: in `facts.states`, which re-exports P4's tuple.
_DIRECT = STATES[1]

#: §3.1's first origin: "deterministic extractor". Addressed by position for the same
#: reason -- `facts.file_facts` owns the spelling.
_ORIGIN = FACT_ORIGINS[0]

#: §8.6's first producer.
_PRODUCER = ATTEMPTED_PRODUCERS[0]


@dataclass(frozen=True)
class DirectSlot:
    """One explicit slot: where it is, which field it fills, how its value normalizes.

    `recognises` answers whether an observation sits in this slot. `normalize` turns
    the raw value into the fact's canonical value, or returns `None` to refuse. Both
    are the caller's: P6 spells no slot name (P4 D7) and §3.5 names no field.
    """
    field_key: str
    recognises: Callable[[Observation], bool]
    normalize: Callable[[str], str | None]


@dataclass(frozen=True)
class DirectSlots:
    """§3.5's four explicit sources, injected. Every field is required, none defaults.

    An empty tuple is a decision the caller made and can be read back; an omitted
    keyword is a `TypeError`. This is P3's precedent for a deferred value -- a
    required keyword with no default -- applied to a map rather than a number.
    """
    content_hash: tuple[DirectSlot, ...]
    exif_timestamp: tuple[DirectSlot, ...]
    document_title: tuple[DirectSlot, ...]
    labeled_form_field: tuple[DirectSlot, ...]


#: §3.5's four names, read off the dataclass so there is no second spelling of them.
SLOT_KINDS: tuple[str, ...] = tuple(
    field.name for field in dataclass_fields(DirectSlots))


def direct_facts(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                 slots: DirectSlots) -> tuple[str, ...]:
    """Every §3.5 direct fact this file version's evidence supports. Done-means 5.

    Returns the `fact_id` of each fact written, in the order written. Writes one fact
    per `(field, canonical value)` pair -- the P6 SPEC's reading of §3.12, "One row =
    one (file, field, value) connection" -- citing every observation that carried it.
    """
    identity = dict(get_file(conn, file_id))
    observations = observations_for_version(conn, file_id, content_hash)

    #: (field_key, canonical_value) -> the observations that supported it. `dict`
    #: preserves insertion order and the input is already in P6's total order, so the
    #: write order is a property of the corpus rather than of the database.
    supported: dict[tuple[str, str], list[Observation]] = {}
    refused: list[tuple[str, Observation]] = []

    for kind in SLOT_KINDS:
        for slot in getattr(slots, kind):
            for observation in observations:
                if not slot.recognises(observation):
                    continue
                value = slot.normalize(observation.raw_value)
                if value is None:
                    refused.append((slot.field_key, observation))
                    continue
                if kind == SLOT_KINDS[0] and value != identity["content_hash"]:
                    # §0: identity is P1's. A slot claiming this file's hash and
                    # carrying another is not "a reliable and explicit source", and
                    # storing it would put a second identity in the database.
                    refused.append((slot.field_key, observation))
                    continue
                supported.setdefault((slot.field_key, value), []).append(observation)

    written: list[str] = []
    for (field_key, value), cited in supported.items():
        written.append(_write_direct(
            conn, file_id=file_id, content_hash=content_hash, field_key=field_key,
            canonical_value=value, cited=tuple(cited)))

    for field_key, observation in refused:
        write_unresolved(
            conn, file_id=file_id, content_hash=content_hash, field_key=field_key,
            reason="normalization_failed", attempted_producers=(_PRODUCER,),
            evidence_refs=(cite(observation),),
            cache_key=_cache_key(conn, content_hash=content_hash,
                                 observations=(observation,)))
    return tuple(written)


def _write_direct(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                  field_key: str, canonical_value: str,
                  cited: tuple[Observation, ...]) -> str:
    refs = tuple(sorted(cite(one) for one in cited))
    value_id = ensure_value(conn, field_key=field_key,
                            canonical_value=canonical_value,
                            first_evidence_ref=refs[0], origin=VALUE_ORIGINS[0])
    return write_fact(
        conn, file_id=file_id, content_hash=content_hash, field_key=field_key,
        value_id=value_id, reliability_state=_DIRECT, origin=_ORIGIN,
        evidence_refs=refs,
        cache_key=_cache_key(conn, content_hash=content_hash, observations=cited),
        active=True)


def _cache_key(conn: sqlite3.Connection, *, content_hash: str,
               observations: Iterable[Observation]) -> str:
    """§3.4's five parts for a fact built from several observations.

    §3.4 states one extractor version and one analysis tier; a fact citing several
    observations has several of each, and no task owns the reconciliation. The rule is
    written out here rather than shared because `facts.cache` is another task's
    module: the versions are the canonical JSON of the sorted distinct
    (name, version) pairs, and the tier is the LAST one present in `ANALYSIS_TIERS`
    order -- filesystem < native < ocr < llm -- so a fact that cited an `ocr` reading
    lands outside the cache slot the native pass computed under, which is what makes
    preamble rule 5's pass 4 supersede rather than overwrite.
    """
    observations = tuple(observations)
    pairs = sorted({(one.extractor_name, one.extractor_version)
                    for one in observations})
    tiers = {analysis_tier_for_observation(conn, one) for one in observations}
    tier = max(tiers, key=ANALYSIS_TIERS.index) if tiers else ANALYSIS_TIERS[0]
    return fact_cache_key(
        content_hash=content_hash,
        extractor_version=canonical_json([list(pair) for pair in pairs]),
        analysis_tier=tier, model_identifier=None, prompt_fingerprint=None)
```

- [ ] **Step 4: Run the test and confirm it passes**

Run: `pytest tests/p6/test_p6_direct.py -v`

Expected: PASS — **16 passed**. Done-means 5 is carried by the first three tests together: the fact
is `direct`, its value is `2026-07-17`, and the EXIF observation reads back with its `raw_value`
byte-identical.

- [ ] **Step 5: Run the P6 suite, because Task 7's guards police this module too**

Run: `pytest tests/p6 -q`

Expected: PASS. `test_no_facts_module_names_a_source_type_or_an_extractor_in_code` now walks
`facts.direct`; it holds no format name because every slot recogniser is the caller's.

- [ ] **Step 6: Commit**

```bash
git add src/facts/direct.py tests/p6/test_p6_direct.py
git commit -m "feat(P6): §3.5 direct facts from injected explicit slots; the slot decides, not the value"
```

---

### Task 9: Roles, and the producer/creator discount (M4)

**Files:**
- Create: `src/facts/discount.py`
- Test: `tests/p6/test_p6_discount.py`

**Interfaces:**
- Consumes: `facts.evidence` — `cite`, `analysis_tier_for_observation`;
  `facts.unresolved` — `write_unresolved`, `ATTEMPTED_PRODUCERS`; `facts.cache.fact_cache_key`;
  `evidence_shape.canonical.canonical_json`; `evidence_shape.vocabulary.ANALYSIS_TIERS`.
  The skeleton also lists `facts.fields` — `get_field`, `FieldNotInCatalogue`. It is consumed by
  **this task's test**, which reads `destination_eligible` off all four §3.8 role rows and resolves
  `field_key` for the `unresolved` assertion, and not by the module: `may_populate` takes no
  connection, because a routing rule that needed a database could not be called from inside a
  ranking loop. Nothing in `Produces:` changed.
- Produces: `discount(observation, *, tool_producer_strings, metadata_property_names) -> str`
  returning one of `suppress` | `demote` | `not_metadata`; `AUTHORSHIP_FIELDS: tuple[str, ...]`;
  `is_discount_target(observation, *, metadata_property_names) -> bool`.
  **Three names are added to the skeleton's block:** `DISCOUNT_OUTCOMES` (the three literals
  `discount` returns, published once so a caller never re-spells them), `may_populate` (the demotion
  tier stated as a predicate every producer consults), and `suppress_tool_metadata` (the gate that
  runs before ranking and writes the suppression tier's `unresolved` row — the skeleton gives this
  task `write_unresolved` in `Consumes:` and no writer to use it in). All three are recorded under
  *Contract additions* at the end.

**Done-means:** 22, and the §3.8 half of 13.

**The two tiers are different outcomes, and getting them the wrong way round is the known defect
here.** A generic TOOL string is **suppression**. A HUMAN name is **demotion**. They are not degrees
of the same thing.

| | Tier 1 — **Suppression** | Tier 2 — **Demotion** |
|---|---|---|
| Fires on | a value on the injected tool-producer list | any other value in the same slot |
| Fact written | **none, in any field, including `authored_by`** | may populate `authored_by` **and nothing else** |
| Record | one `unresolved` row, `reason = discounted_tool_metadata` | an ordinary fact with its evidence refs |
| Downgraded to `possible`? | **No.** | n/a — it is retained as supporting evidence |
| Destination-eligible? | n/a — there is no fact | **No.** §3.8 makes every authorship field `destination_eligible = FALSE` |

The design's own sentences, and the reason the split is not negotiable:

> **§2.2:** *"PDF metadata should be treated as supporting evidence, not as truth. Author and creator
> fields may be stale, generic, or generated by a tool rather than a person, so a value such as
> python-docx, Mozilla/5.0, or a browser-generated producer string should not be mistaken for
> meaningful content."*

> **§2.3:** *"DOCX author metadata should remain supporting information only, because it may identify
> a prior editor, a document template, or a script rather than the meaningful subject or purpose of
> the file."*

> **§3.8:** *"The system must separate roles that happen to contain the same entity type. … The agent
> should model these as distinct facets, such as authored_by and target_school, or our_firm and
> client. It should avoid using authorship or creator identity as a destination dimension. A folder
> should not become a collection point for everything produced by the same person or organization.
> Authorship is usually metadata; the document's purpose, project, subject, or target is more
> informative for placement."*

§2.2's *"should not be mistaken for meaningful content"* is why suppression is not a downgrade: a
tool name is **a fact about the software**, not a weak clue about the document, and a `possible`
`authored_by = python-docx` is a false claim held at low confidence rather than no claim. §2.3's
*"a prior editor, a document template, or a script"* is why demotion is not suppression: the value
may be a real person, and §3.8 has a field for exactly that — bounded to the authorship role and
excluded from every destination.

**Done-means 22 asserts both halves in one item**, which is why this plan tests both and why the
suppression test asserts the absence of a `possible` fact explicitly rather than only the absence of
a `direct` one.

**M4, and the reason `direct` is not a contradiction.** P4's fixture 6 is
`raw_value = "python-docx"`, zone `metadata`, locator `metadata:field=Producer`,
`reliability = "direct"`. `direct` describes the **slot** — a labeled metadata field — and not the
value's usefulness, which is P5's SPEC E1 in as many words. There is no marker on the observation;
P5 sets no suppression flag and invents no field. The discount is P6's, and this module is where it
lives. P5 Open question 13 closes here.

**The list is data; the matcher is code, and confusing the two destroys the point.**
`planning/deferred-catalogues/01-tool-producer-strings.json` (115 entries) says it itself:
*"P6 receives this list as data at construction … It is **not** imported as a module-level
constant."* Copying it into `src/facts/` satisfies the letter of Task 25's guard and destroys its
purpose. What P6 *does* own is how an entry is read, because the catalogue specifies that as a rule
rather than as data:

- `normalization_for_matching`: *"Compare against the raw value with Unicode NFC applied and
  leading/trailing whitespace stripped, **for comparison only**."* P4's RAW-1/RAW-2 keep the stored
  `raw_value` byte-for-byte untouched; the normalization lives inside the matcher and never writes
  back.
- `boundary_rule`: a `prefix` entry fires when the normalized value **equals** the prefix, or when it
  begins with the prefix followed by a boundary character and a tail containing at least one ASCII
  digit. Boundary characters are `space tab , ; : / ( ) - _ . + & ® ™ ©` — never a letter or a
  digit, *"which is what stops `Notion` matching `Notional` and `iText` matching `iTextbook`"*. An
  entry may set `tail_required: "any"` to drop the digit requirement; two rows do.
- `match_kind` is `exact` (13 rows), `prefix` (86) or `regex` (16), and `case_sensitive` is per row.

**The matcher below was executed against all 115 entries before this plan was written**: every
`example_true` matches and every `example_false` does not — 0 misses, 0 false positives. Probes
outside the catalogue behave too: `Jane Chen`, `Dr. Amara Okonkwo`, `Mozilla Foundation`,
`Docx Family Trust`, `Microsoft Word skills certificate` and `Notional Advisors` all return `False`,
while `python-docx`, `Python-DocX` and a full Safari user-agent return `True`.

**The rule fires before facet ranking**, so a discounted value never enters §3.7's candidate list and
cannot win a margin it should never have contested. `suppress_tool_metadata` is that gate: it returns
the observations that survive, and Task 11 ranks what it is given.

**A04 as built contradicts Done-means 22 and this plan does not paper over it (finding F5).**
`tests/eval/fixtures/adversarial/A04.json` is worded *"generic author metadata (`python-docx`,
`Mozilla/5.0`, browser producer strings)"* — the **suppression** tier by the values it names — yet
carries `expected_outcome_kind: "produced"` with `expected_value: {"retained_as":
"supporting_evidence"}`, which is the **demotion** tier. Under this plan the named values produce
`abstained`, not `produced`. The fixture is P2's and is not edited here; Done-means 22 is the
authority and the conflict is carried to *Contract ambiguities* below.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_discount.py
"""Done-means 22, M4, §3.8 — suppression is not demotion, and neither is a folder."""
from __future__ import annotations

import ast
import inspect
import json
import unicodedata
from pathlib import Path

import pytest

from evidence_shape.fixtures import by_number
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run

from facts import discount as discount_module
from facts.cache import fact_cache_key
from facts.discount import (
    AUTHORSHIP_FIELDS, DISCOUNT_OUTCOMES, discount, is_discount_target,
    may_populate, suppress_tool_metadata,
)
from facts.evidence import cite, observations_for_version
from facts.fields import get_field
from facts.file_facts import FACT_ORIGINS, facts_for_file, write_fact
from facts.states import STATES
from facts.unresolved import unresolved_for_file
from facts.values import VALUE_ORIGINS, ensure_value

CLOCK = "2026-08-19T12:00:00+00:00"
HASH = "a" * 64

#: Catalogue 01, read as DATA at the injection point. Never imported into `facts`.
CATALOGUE = (Path(__file__).resolve().parents[2]
             / "planning" / "deferred-catalogues"
             / "01-tool-producer-strings.json")

#: §2.2's three literal seeds, authored here so Done-means 22 does not depend on a
#: planning artifact being present. The 115-entry catalogue is exercised separately.
SEEDS = (
    {"id": "tps-python-docx", "match": "python-docx", "match_kind": "exact",
     "case_sensitive": False},
    {"id": "tps-ua-mozilla-5", "match": "Mozilla/5.0", "match_kind": "prefix",
     "case_sensitive": True},
    {"id": "tps-ua-chrome-token", "pattern": r"(?:^|[\s(;])Chrome/\d+(?:\.\d+)*",
     "match_kind": "regex", "case_sensitive": True},
)

#: Catalogue 01's `property_names` blocks, flattened by the caller. P4 D7 stores "the
#: source format's own slot name, verbatim", so these are the formats' spellings.
PROPERTY_NAMES = ("Producer", "Creator", "Author", "pdf:Producer",
                  "xmp:CreatorTool", "dc:creator", "creator", "lastModifiedBy",
                  "Application", "meta:generator", "Software", "PRODID",
                  "X-Mailer", "User-Agent")


def _code_strings(module) -> set[str]:
    """Every string literal in a module that is NOT a docstring (see Task 7)."""
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


def _observe(conn, *, run_id, raw, label=None, zone="metadata", file_id="f1",
             content_hash=HASH, extractor="docx.metadata", new_run=True):
    if new_run:
        record_run(conn, ExtractionRun(
            run_id=run_id, file_id=file_id, content_hash=content_hash,
            extractor_name=extractor, extractor_version="1.0.0",
            source_type="text_document", analysis_tier="native", config={},
            completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    container = (Segment("field", label=label),) if label else ()
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name=extractor,
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location(zone, container), occurrence_count=1, observed_at=CLOCK,
        reliability="direct", run_id=run_id)
    record_observation(conn, observation)
    return observation


def _screen(conn, observations):
    return suppress_tool_metadata(
        conn, file_id="f1", content_hash=HASH, observations=observations,
        tool_producer_strings=SEEDS, metadata_property_names=PROPERTY_NAMES)


# --- Done-means 22, first half: suppression ------------------------------------

def test_a_python_docx_producer_produces_no_fact_in_any_field(p6_conn):
    # §2.2: such a value "should not be mistaken for meaningful content." Not in
    # `authored_by`, not anywhere -- the assertion is over the whole fact table.
    _observe(p6_conn, run_id="r1", raw="python-docx", label="Producer")
    survivors = _screen(p6_conn, observations_for_version(p6_conn, "f1", HASH))

    assert survivors == ()
    assert facts_for_file(p6_conn, "f1", HASH) == []


def test_a_suppressed_producer_writes_exactly_one_unresolved_row(p6_conn):
    # Done-means 22, verbatim: "one `unresolved` row with reason
    # discounted_tool_metadata". One, not one per field.
    observation = _observe(p6_conn, run_id="r1", raw="python-docx",
                           label="Producer")
    _screen(p6_conn, observations_for_version(p6_conn, "f1", HASH))

    rows = unresolved_for_file(p6_conn, "f1", HASH)
    assert len(rows) == 1
    assert rows[0]["reason"] == "discounted_tool_metadata"
    assert rows[0]["field_key"] == get_field(p6_conn, AUTHORSHIP_FIELDS[0])["field_key"]
    assert json.loads(rows[0]["evidence_refs"]) == [observation.observation_key]


def test_a_suppressed_producer_is_not_demoted_to_possible(p6_conn):
    # The tier split, asserted as the thing it is NOT. §2.2 is literal, and a
    # `possible` authored_by = python-docx is a false claim held quietly, which is
    # worse than no claim: §3.6 keeps weak clues, and this is not a weak clue.
    _observe(p6_conn, run_id="r1", raw="python-docx", label="Producer")
    _screen(p6_conn, observations_for_version(p6_conn, "f1", HASH))

    assert [row for row in facts_for_file(p6_conn, "f1", HASH)
            if row["reliability_state"] == STATES[4]] == []


@pytest.mark.parametrize("run_id, raw", [
    ("r-a", "python-docx"),
    ("r-b", "Python-DocX"),
    ("r-c", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"),
    ("r-d", "Mozilla/5.0 (Windows NT 10.0) Chrome/121.0.0.0"),
])
def test_2_2s_named_seeds_all_suppress(p6_conn, run_id, raw):
    observation = _observe(p6_conn, run_id=run_id, raw=raw, label="Producer")
    assert discount(observation, tool_producer_strings=SEEDS,
                    metadata_property_names=PROPERTY_NAMES) == DISCOUNT_OUTCOMES[0]


# --- Done-means 22, second half: demotion --------------------------------------

def test_a_human_name_in_the_same_slot_is_demoted_and_not_suppressed(p6_conn):
    # §2.3: the value "may identify a prior editor, a document template, or a script
    # rather than the meaningful subject or purpose" -- may, not must. It survives.
    observation = _observe(p6_conn, run_id="r1", raw="Jane Chen", label="creator")
    assert discount(observation, tool_producer_strings=SEEDS,
                    metadata_property_names=PROPERTY_NAMES) == DISCOUNT_OUTCOMES[1]

    survivors = _screen(p6_conn, observations_for_version(p6_conn, "f1", HASH))
    assert [one.raw_value for one in survivors] == ["Jane Chen"]
    assert unresolved_for_file(p6_conn, "f1", HASH) == []


def test_a_demoted_value_may_populate_authored_by_and_no_other_field(p6_conn):
    # §2.2/§2.3: it "may populate an authorship role field (§3.8 authored_by) and
    # nothing else; it may never populate a topic, purpose, project, course,
    # institution or target field on its own."
    observation = _observe(p6_conn, run_id="r1", raw="Jane Chen", label="creator")
    assert may_populate(AUTHORSHIP_FIELDS[0], observation,
                        metadata_property_names=PROPERTY_NAMES) is True
    for field_key in ("subject", "purpose", "project", "target_university",
                      "school", "our_firm", "client", "target_school"):
        assert may_populate(field_key, observation,
                            metadata_property_names=PROPERTY_NAMES) is False


def test_a_value_outside_a_discount_slot_may_populate_anything(p6_conn):
    # The rule is keyed on the slot. A heading is not author metadata, so the discount
    # says nothing about it and the ordinary producers decide.
    observation = _observe(p6_conn, run_id="r1", raw="Columbia", zone="heading")
    assert discount(observation, tool_producer_strings=SEEDS,
                    metadata_property_names=PROPERTY_NAMES) == DISCOUNT_OUTCOMES[2]
    assert may_populate("target_university", observation,
                        metadata_property_names=PROPERTY_NAMES) is True


def test_a_demoted_value_becomes_an_authored_by_fact_with_its_evidence(p6_conn):
    # Done-means 22's "may populate authored_by", end to end: the discount permits it
    # and the ordinary fact writer records it with the observation key that supported
    # it. The write is the producer's; the permission is this module's.
    observation = _observe(p6_conn, run_id="r1", raw="Jane Chen", label="creator")
    survivors = _screen(p6_conn, observations_for_version(p6_conn, "f1", HASH))
    assert survivors

    value_id = ensure_value(p6_conn, field_key=AUTHORSHIP_FIELDS[0],
                            canonical_value="Jane Chen",
                            first_evidence_ref=cite(observation),
                            origin=VALUE_ORIGINS[0])
    write_fact(p6_conn, file_id="f1", content_hash=HASH,
               field_key=AUTHORSHIP_FIELDS[0], value_id=value_id,
               reliability_state=STATES[1], origin=FACT_ORIGINS[0],
               evidence_refs=(cite(observation),),
               cache_key=fact_cache_key(
                   content_hash=HASH,
                   extractor_version='[["docx.metadata","1.0.0"]]',
                   analysis_tier="native", model_identifier=None,
                   prompt_fingerprint=None),
               active=True)

    rows = facts_for_file(p6_conn, "f1", HASH)
    assert len(rows) == 1
    assert json.loads(rows[0]["evidence_refs"]) == [observation.observation_key]


# --- §3.8, and the half of Done-means 13 this task owns ------------------------

def test_authorship_fields_are_the_only_fields_a_demoted_value_may_fill():
    # §3.8 names four role fields; only ONE of them is an authorship field. A Creator
    # slot never tells you who the client or the target school is -- that is exactly
    # the role confusion §3.8 exists to prevent.
    assert AUTHORSHIP_FIELDS == ("authored_by",)


def test_every_3_8_role_field_is_destination_ineligible(p6_conn):
    # §3.8: "It should avoid using authorship or creator identity as a destination
    # dimension. A folder should not become a collection point for everything produced
    # by the same person or organization." Done-means 13's §3.8 half.
    for field_key in ("authored_by", "target_school", "our_firm", "client"):
        assert not get_field(p6_conn, field_key)["destination_eligible"]


# --- the rule fires BEFORE ranking ---------------------------------------------

def test_a_suppressed_value_never_reaches_the_candidate_list(p6_conn):
    # "The rule fires before facet ranking, so a discounted value never enters §3.7's
    # candidate list and therefore cannot win a margin it should never have contested."
    # The scorer here is the test's own -- §3.7's weights are Deferred and injected,
    # and Task 11 owns the real ranking. What is asserted is the INPUT to ranking.
    def rank(observations, *, weight):
        # Score descending, then `observation_key` ascending -- the total order the
        # Global Constraints require, so a tie never depends on P4's write order.
        return tuple(sorted(observations,
                            key=lambda one: (-weight(one), cite(one))))

    def weight(one):
        return 10 if one.location.zone == "metadata" else 5

    _observe(p6_conn, run_id="r1", raw="python-docx", label="Producer")
    _observe(p6_conn, run_id="r2", raw="Columbia", zone="heading")
    everything = observations_for_version(p6_conn, "f1", HASH)

    assert rank(everything, weight=weight)[0].raw_value == "python-docx"
    survivors = _screen(p6_conn, everything)
    assert rank(survivors, weight=weight)[0].raw_value == "Columbia"
    assert len(survivors) == 1


# --- M4: `direct` describes the slot -------------------------------------------

def test_p4_fixture_6_is_direct_and_still_suppressed(p6_conn):
    # M4, and P5 SPEC E1: "direct describes the SLOT, not the value's usefulness."
    # There is no marker on the observation; the discount is here.
    fixture = by_number(6)
    record_run(p6_conn, fixture.run)
    for observation in fixture.observations:
        record_observation(p6_conn, observation)
    observation = fixture.observations[0]

    assert observation.reliability == STATES[1]
    assert observation.raw_value == "python-docx"
    assert observation.location.zone == "metadata"
    assert is_discount_target(observation,
                              metadata_property_names=PROPERTY_NAMES) is True
    assert discount(observation, tool_producer_strings=SEEDS,
                    metadata_property_names=PROPERTY_NAMES) == DISCOUNT_OUTCOMES[0]


def test_a_metadata_observation_in_an_unlisted_slot_is_not_a_discount_target(p6_conn):
    # Catalogue 01: "A slot not on this list is not a discount target." A page count
    # or a title lives at zone `metadata` too and is nobody's author metadata.
    observation = _observe(p6_conn, run_id="r1", raw="37", label="page_count")
    assert is_discount_target(observation,
                              metadata_property_names=PROPERTY_NAMES) is False
    assert discount(observation, tool_producer_strings=SEEDS,
                    metadata_property_names=PROPERTY_NAMES) == DISCOUNT_OUTCOMES[2]


# --- the injection property -----------------------------------------------------

def test_the_list_and_the_property_names_have_no_defaults(p6_conn):
    # Catalogue 01: "P6 receives this list as data at construction … It is not
    # imported as a module-level constant." Omitting either is a TypeError.
    observation = _observe(p6_conn, run_id="r1", raw="python-docx", label="Producer")
    with pytest.raises(TypeError):
        discount(observation, tool_producer_strings=SEEDS)
    with pytest.raises(TypeError):
        discount(observation, metadata_property_names=PROPERTY_NAMES)
    with pytest.raises(TypeError):
        is_discount_target(observation)


def test_facts_discount_holds_no_producer_string_and_no_property_name():
    # Copying the catalogue into `src/facts/` satisfies the letter of Task 25's guard
    # and destroys its point. The grammar for READING an entry is code; the entries
    # are data.
    forbidden = {"python-docx", "Mozilla/5.0", "Producer", "Creator", "Author",
                 "lastModifiedBy", "meta:generator", "X-Mailer", "PRODID"}
    assert _code_strings(discount_module) & forbidden == set()


def test_the_matcher_normalizes_for_comparison_only(p6_conn):
    # Catalogue 01: NFC + strip, "for comparison only". P4's RAW-1/RAW-2 keep the
    # stored raw value byte-for-byte, and the trigger `evidence_never_overwritten`
    # makes that unfalsifiable -- so this asserts P6's intent, which is the half a
    # trigger cannot check.
    raw = "  python-docx  "
    observation = _observe(p6_conn, run_id="r1", raw=raw, label="Producer")
    assert discount(observation, tool_producer_strings=SEEDS,
                    metadata_property_names=PROPERTY_NAMES) == DISCOUNT_OUTCOMES[0]
    stored = observations_for_version(p6_conn, "f1", HASH)
    assert [one.raw_value for one in stored] == [raw]
    assert unicodedata.normalize("NFC", raw).strip() == "python-docx"


def test_a_prefix_entry_needs_a_boundary_character_and_a_version_tail(p6_conn):
    # Catalogue 01's `boundary_rule`, which is what stops `Notion` matching `Notional`
    # and `Microsoft Word` matching `Microsoft Word skills certificate`.
    entries = ({"id": "t", "match": "Notion", "match_kind": "prefix",
                "case_sensitive": True},)
    for raw, expected in (("Notion", DISCOUNT_OUTCOMES[0]),
                          ("Notion 2.30.1", DISCOUNT_OUTCOMES[0]),
                          ("Notional Advisors", DISCOUNT_OUTCOMES[1]),
                          ("Notion Labs Incorporated", DISCOUNT_OUTCOMES[1])):
        observation = _observe(p6_conn, run_id=f"r-{raw}", raw=raw, label="Producer")
        assert discount(observation, tool_producer_strings=entries,
                        metadata_property_names=PROPERTY_NAMES) == expected


@pytest.mark.skipif(not CATALOGUE.exists(),
                    reason="catalogue 01 is a planning artifact, injected as data")
def test_the_matcher_agrees_with_every_example_in_catalogue_01(p6_conn):
    # The real 115 entries, each carrying its own example_true and example_false.
    # Run before this plan was written: 0 misses, 0 false positives.
    entries = json.loads(CATALOGUE.read_text())["entries"]

    def outcome(raw, index):
        observation = _observe(p6_conn, run_id=f"c-{index}", raw=raw,
                               label="Producer")
        return discount(observation, tool_producer_strings=entries,
                        metadata_property_names=PROPERTY_NAMES)

    index = 0
    misses, false_positives = [], []
    for entry in entries:
        for good in _examples(entry, "example_true"):
            index += 1
            if outcome(good, index) != DISCOUNT_OUTCOMES[0]:
                misses.append((entry["id"], good))
        for bad in _examples(entry, "example_false"):
            index += 1
            if outcome(bad, index) != DISCOUNT_OUTCOMES[1]:
                false_positives.append((entry["id"], bad))
    assert misses == []
    assert false_positives == []


def _examples(entry, key):
    value = entry.get(key)
    if value is None:
        return ()
    return (value,) if isinstance(value, str) else tuple(value)
```

- [ ] **Step 2: Run the test and read the failure**

Run: `pytest tests/p6/test_p6_discount.py -v`

Expected: FAIL — collection error, `ModuleNotFoundError: No module named 'facts.discount'`.
**21 tests fail to collect, 0 pass** (18 test functions, one of which is parametrized over four
values, so pytest reports 21 items).

- [ ] **Step 3: Write the implementation**

```python
# src/facts/discount.py
"""§2.2/§2.3's producer/creator/author discount, and §3.8's authorship role (M4).

Two tiers, and they are different outcomes rather than degrees of one:

**Suppression.** A value on the injected tool-producer list produces NO fact in any
field, including `authored_by`, and one `unresolved` row with
`reason = discounted_tool_metadata`. §2.2: "a value such as python-docx, Mozilla/5.0,
or a browser-generated producer string should not be mistaken for meaningful content."
It is NOT downgraded to `possible` -- a tool name is a fact about the software, not a
weak clue about the document, and a `possible` authored_by = python-docx is a false
claim held quietly.

**Demotion.** Any other value in the same slot is supporting evidence. §2.3: it "may
identify a prior editor, a document template, or a script rather than the meaningful
subject or purpose of the file." It may populate `authored_by` and nothing else -- not
topic, purpose, project, subject, institution or target -- and §3.8 makes every
authorship field `destination_eligible = FALSE`: "A folder should not become a
collection point for everything produced by the same person or organization."

**`direct` on the observation is not a contradiction** (M4). P4's fixture 6 carries
`raw_value = "python-docx"` at `reliability = "direct"` because the Producer field is
a labeled slot; `direct` describes the SLOT, not the value's usefulness. There is no
marker on the observation -- P5 sets no suppression flag and invents no field -- so
the discount is here and P5 Open question 13 closes as answered.

**The list is data; the grammar for reading it is code.** Catalogue 01
(`planning/deferred-catalogues/01-tool-producer-strings.json`, 115 entries) states its
own injection rule: "P6 receives this list as data at construction … It is not
imported as a module-level constant." What this module owns is `normalization_for_
matching` (NFC + strip, for comparison only -- P4's RAW-1/RAW-2 keep the stored raw
value byte-for-byte) and `boundary_rule` (a prefix fires on equality, or on the prefix
plus a boundary character plus a tail carrying an ASCII digit, "which is what stops
`Notion` matching `Notional`"). Those are rules the catalogue specifies in prose and
cannot express as data; the entries themselves are never spelled here.

**The gate runs before ranking.** `suppress_tool_metadata` returns the observations
that survive, so a discounted value never enters §3.7's candidate list and cannot win
a margin it should never have contested.
"""
from __future__ import annotations

import re
import sqlite3
import unicodedata
from typing import Any, Iterable, Mapping

from evidence_shape.canonical import canonical_json
from evidence_shape.observation import Observation
from evidence_shape.vocabulary import ANALYSIS_TIERS

from facts.cache import fact_cache_key
from facts.evidence import analysis_tier_for_observation, cite
from facts.unresolved import ATTEMPTED_PRODUCERS, write_unresolved

#: What `discount` returns. Published once so no caller re-spells them.
DISCOUNT_OUTCOMES: tuple[str, str, str] = ("suppress", "demote", "not_metadata")

#: §3.8's authorship role -- the ONLY field a demoted producer/creator/author value
#: may populate. `target_school`, `our_firm` and `client` are §3.8's other three role
#: fields and are not authorship fields: a Creator slot never says who the client is,
#: which is exactly the role confusion §3.8 exists to prevent.
AUTHORSHIP_FIELDS: tuple[str, ...] = ("authored_by",)

#: Catalogue 01's `match_field`: "observation.raw_value where location.zone ==
#: metadata and the field-kind segment's label is one of the property names". A zone
#: is P4's vocabulary and P4 validates it at the record; this is the SPEC's own
#: literal for the slot the two-tier rule is keyed on.
_METADATA_ZONE = "metadata"
_FIELD_SEGMENT = "field"

#: Catalogue 01's `boundary_rule`, verbatim: "space, tab, comma, semicolon, colon,
#: slash, parentheses, hyphen, underscore, period, plus, ampersand, registered,
#: trademark, copyright -- never a letter or a digit."
_BOUNDARY = frozenset(" \t,;:/()-_.+&®™©")
_ASCII_DIGITS = frozenset("0123456789")

#: §8.6's first producer. The discount runs inside the deterministic pass.
_PRODUCER = ATTEMPTED_PRODUCERS[0]


def is_discount_target(observation: Observation, *,
                       metadata_property_names: Iterable[str]) -> bool:
    """Does this observation sit in an author/creator/producer metadata slot?

    Catalogue 01: "A slot not on this list is not a discount target." A page count or
    a document title also lives at zone `metadata` and is nobody's author metadata.
    """
    names = frozenset(metadata_property_names)
    if observation.location.zone != _METADATA_ZONE:
        return False
    return any(segment.kind == _FIELD_SEGMENT and segment.label in names
               for segment in observation.location.container_path)


def discount(observation: Observation, *,
             tool_producer_strings: Iterable[Mapping[str, Any]],
             metadata_property_names: Iterable[str]) -> str:
    """Which of §2.2/§2.3's two tiers this observation falls in, or neither."""
    if not is_discount_target(observation,
                              metadata_property_names=metadata_property_names):
        return DISCOUNT_OUTCOMES[2]
    value = _for_matching(observation.raw_value)
    if any(_entry_matches(value, entry) for entry in tool_producer_strings):
        return DISCOUNT_OUTCOMES[0]
    return DISCOUNT_OUTCOMES[1]


def may_populate(field_key: str, observation: Observation, *,
                 metadata_property_names: Iterable[str]) -> bool:
    """§2.2/§2.3's demotion rule, as the predicate every producer consults.

    A value in an author/creator/producer slot may fill an authorship role field and
    nothing else. A value outside such a slot is not this rule's business and the
    ordinary producers decide.
    """
    if not is_discount_target(observation,
                              metadata_property_names=metadata_property_names):
        return True
    return field_key in AUTHORSHIP_FIELDS


def suppress_tool_metadata(conn: sqlite3.Connection, *, file_id: str,
                           content_hash: str,
                           observations: Iterable[Observation],
                           tool_producer_strings: Iterable[Mapping[str, Any]],
                           metadata_property_names: Iterable[str],
                           ) -> tuple[Observation, ...]:
    """The gate that runs before §3.7's ranking. Returns what survives it.

    Each suppressed observation writes exactly one `unresolved` row against §3.8's
    authorship field -- the field the value would have filled had it been a person --
    with `reason = discounted_tool_metadata` and the key it considered (B7: a refusal
    with no record of what it looked at is not inspectable).
    """
    entries = tuple(tool_producer_strings)
    names = frozenset(metadata_property_names)
    survivors: list[Observation] = []
    for observation in observations:
        if discount(observation, tool_producer_strings=entries,
                    metadata_property_names=names) != DISCOUNT_OUTCOMES[0]:
            survivors.append(observation)
            continue
        write_unresolved(
            conn, file_id=file_id, content_hash=content_hash,
            field_key=AUTHORSHIP_FIELDS[0], reason="discounted_tool_metadata",
            attempted_producers=(_PRODUCER,), evidence_refs=(cite(observation),),
            cache_key=_cache_key(conn, content_hash=content_hash,
                                 observations=(observation,)))
    return tuple(survivors)


def _for_matching(raw: str) -> str:
    """Catalogue 01's `normalization_for_matching`: NFC + strip, comparison only.

    P4's RAW-1/RAW-2 keep the stored `raw_value` byte-for-byte and the
    `evidence_never_overwritten` trigger enforces it; this normalization lives inside
    the matcher and never writes back.
    """
    return unicodedata.normalize("NFC", raw).strip()


def _entry_matches(value: str, entry: Mapping[str, Any]) -> bool:
    """One catalogue row against one normalized value. Three `match_kind`s, no fourth."""
    kind = entry["match_kind"]
    sensitive = bool(entry.get("case_sensitive", False))
    if kind == "regex":
        return re.search(entry["pattern"], value,
                         0 if sensitive else re.IGNORECASE) is not None
    needle = entry["match"]
    subject, wanted = ((value, needle) if sensitive
                       else (value.casefold(), needle.casefold()))
    if kind == "exact":
        return subject == wanted
    if kind == "prefix":
        return _prefix_matches(
            subject, wanted, tail_required=str(entry.get("tail_required", "digit")))
    raise ValueError(
        f"{entry.get('id')!r} carries match_kind={kind!r}; catalogue 01 defines "
        f"exact, prefix and regex and P6 invents no fourth"
    )


def _prefix_matches(value: str, prefix: str, *, tail_required: str) -> bool:
    """Catalogue 01's `boundary_rule`.

    Equality, or the prefix followed by a boundary character and a version tail. The
    boundary character is never a letter or a digit -- that is what stops `Notion`
    matching `Notional` -- and the tail must carry an ASCII digit unless the row sets
    `tail_required: "any"`, which is what stops `Microsoft Word` matching
    `Microsoft Word skills certificate`.
    """
    if value == prefix:
        return True
    if not value.startswith(prefix):
        return False
    tail = value[len(prefix):]
    if not tail or tail[0] not in _BOUNDARY:
        return False
    if tail_required == "any":
        return True
    return any(character in _ASCII_DIGITS for character in tail)


def _cache_key(conn: sqlite3.Connection, *, content_hash: str,
               observations: Iterable[Observation]) -> str:
    """§3.4's five parts for a record built from several observations.

    §3.4 states one extractor version and one analysis tier; a record citing several
    observations has several of each, and no task owns the reconciliation. The rule is
    written out here rather than shared because `facts.cache` is another task's
    module: the versions are the canonical JSON of the sorted distinct
    (name, version) pairs, and the tier is the LAST one present in `ANALYSIS_TIERS`
    order -- filesystem < native < ocr < llm -- so a record that cited an `ocr`
    reading lands outside the cache slot the native pass computed under, which is what
    makes preamble rule 5's pass 4 supersede rather than overwrite.
    """
    observations = tuple(observations)
    pairs = sorted({(one.extractor_name, one.extractor_version)
                    for one in observations})
    tiers = {analysis_tier_for_observation(conn, one) for one in observations}
    tier = max(tiers, key=ANALYSIS_TIERS.index) if tiers else ANALYSIS_TIERS[0]
    return fact_cache_key(
        content_hash=content_hash,
        extractor_version=canonical_json([list(pair) for pair in pairs]),
        analysis_tier=tier, model_identifier=None, prompt_fingerprint=None)
```

- [ ] **Step 4: Run the test and confirm it passes**

Run: `pytest tests/p6/test_p6_discount.py -v`

Expected: PASS — **21 passed**. `test_the_matcher_agrees_with_every_example_in_catalogue_01` runs the
real 115 entries; the matcher above was executed against them before this plan was written and
returned 0 misses and 0 false positives, so this test is a regression guard rather than a discovery.

- [ ] **Step 5: Run the P6 suite, because Task 7's guards police this module too**

Run: `pytest tests/p6 -q`

Expected: PASS. `facts.discount` names no source type and no extractor; `_METADATA_ZONE` is a
**zone**, which is a different closed vocabulary and not one Task 7's guard covers.

- [ ] **Step 6: Commit**

```bash
git add src/facts/discount.py tests/p6/test_p6_discount.py
git commit -m "feat(P6): §2.2/§2.3 producer discount — suppression is not demotion; §3.8's authorship role"
```

---

## Contract additions — names these three tasks publish beyond the skeleton's blocks

The skeleton's `Interfaces:` blocks are a contract with the authors writing Tasks 1–6, 10–13 and
14–27 in parallel. **No name in any of those blocks changed.** Six names are *added*, each because
the skeleton's own `Consumes:` line or `Produces:` type demanded something it did not name. They are
listed here so a parallel author sees them without reading the code.

| Task | Added | Why it had to exist |
|---|---|---|
| 7 | `UnknownRun` | `analysis_tier_for_observation` must fail rather than guess: an inferred tier lands in §3.4's cache key, and a wrong cache key is a fact that never invalidates |
| 8 | `DirectSlot` | `DirectSlots` is "a frozen dataclass of slot-name predicates"; a dataclass of things needs the thing |
| 8 | `SLOT_KINDS` | §3.5's four names, read off `dataclasses.fields(DirectSlots)` so there is no second spelling of them |
| 9 | `DISCOUNT_OUTCOMES` | `discount()` returns one of three literals; publishing the tuple stops every caller re-spelling them |
| 9 | `may_populate` | The demotion tier is a routing rule other producers must consult; a rule with no way to ask it is a comment |
| 9 | `suppress_tool_metadata` | The skeleton gives Task 9 `write_unresolved` in `Consumes:` and no writer to use it in. This is the pre-ranking gate and the suppression tier's only write |

**Task 9 writes no fact.** Its `Consumes:` block names `write_unresolved` and not `write_fact`, and
that is read as deliberate: the demotion tier decides *which field a value may fill*, and the fact
write belongs to whichever producer fills it. `tests/p6/test_p6_discount.py` drives `write_fact`
itself to prove Done-means 22's second half end to end.

---

## Contract ambiguities and conflicts found

Reported, not unilaterally resolved. Each was checked against the source or by execution on
2026-08-22.

**1 (carried, now worse). The §3.4 cache-key reconciliation has no owner and now appears five
times.** §3.4 names one extractor version and one analysis tier; a fact citing several observations
has several of each. `PLAN-tasks-14-15.md` wrote the rule out three times with a note; Tasks 8 and 9
make five. It belongs in `facts.cache` (Task 6) as
`fact_cache_key_for(conn, *, content_hash, observations)`. Five copies of a rule is four chances for
one of them to drift.

**2 (HIGH, unresolved by anyone). `PLAN-tasks-14-15.md` spells reliability states as string literals,
which Task 1's guard forbids.** `families.py` in that document contains
`reliability_state="direct"` and `reliability_state="possible"`. Task 1's stated proof is *"the
absence of any string literal spelling a state name anywhere else in `facts`"* — a guard the sibling
plan's code fails on its face. Tasks 8 and 9 here address the six states **by index** into
`facts.states.STATES` (`STATES[1]` is `direct`, `STATES[4]` is `possible`, in §3.13's published
order) so the spelling stays in one module. **Either the sibling's literals change or Task 1's guard
does; they cannot both stand.** Recommendation: index, because §3.13's order is contract and P4's
tuple is the one copy.

**3 (HIGH, F5, unchanged). A04 as built asserts the demotion tier for values that are the suppression
tier.** `tests/eval/fixtures/adversarial/A04.json` names `python-docx`, `Mozilla/5.0` and browser
producer strings and carries `expected_outcome_kind: "produced"` with
`expected_value: {"retained_as": "supporting_evidence"}`. Done-means 22 requires `abstained` and no
fact in any field for exactly those values. Task 9 implements Done-means 22. The fixture is P2's and
is not edited here. **One of the two must move**; the design's §2.2 sentence backs Done-means 22.

**4 (MEDIUM, F8, now half-closed).** `12-academic-capture-patterns/04-narrow-date-families.json`
(authored 2026-08-22) supplies the EXIF and labeled-date slot families for two of §3.5's four slots
and names *"Task 8's direct-fact slot list"* in its own `owner` field. The **document title** and
**content hash** slots still have no catalogue. Reported, not authored: `planning/deferred-catalogues/`
is another agent's.

**5 (MEDIUM, new). §3.5 names the content hash a direct source, and no observation carries it.**
`src/extractors/filesystem.py` emits `normalized_filename`, `extension` and `mime_type` as labeled
`metadata` observations and deliberately emits **no** content-hash observation — its own comment says
so: *"G5 gives duplicate and version-family signals to P6 'from P1's content hashes' … P6 reads those
from `files`; a second copy here would be two homes for one value."* But P6's rule 1 requires every
non-user fact to cite an observation key, so a content-hash fact has nothing to cite. **Task 8
therefore supports the content-hash slot when the caller supplies one and cross-checks it against
P1's column, and the production `DirectSlots` passes an empty tuple for it**; the fact the content
hash actually supports is Task 14's duplicate family, which cites the observations the family members
share. Nothing is broken; the design's four-slot sentence just has one slot with no producer, and it
should be said out loud rather than discovered.

**6 (LOW, new). §3.5's fourth slot is "labeled form field", and the SPEC's extra direct source is
"filesystem timestamps".** Neither is a form. Catalogue 12/04 calls its two direct families
`metadata_slot` and justifies them from §3.13's *"labeled form field"*; P5's `METADATA_SLOTS` writes
filesystem values the same way. Task 8 reads §3.5's fourth slot as **any explicitly labeled slot
whose label the format itself supplies**, which is what P4 D7 stores and what both of those describe,
and the caller's `DirectSlots.labeled_form_field` carries them. If that reading is wrong the fix is a
fifth member on `DirectSlots`, not a change anywhere else.

**7 (LOW, new). The SPEC restricts P3 input to "exactly two computations", both for the bounded
session.** So a filesystem timestamp must reach Task 8 as an **observation**, never by reading
`files.observed_timestamps` — that would be a third computation the Contract in forecloses. Task 8
reads P1's row for `content_hash` only. This is the same class of tension F10 records for §3.9's
folder-name evidence and is noted so nobody "fixes" Task 8 by reaching into P3's column.

**8 (LOW, informational). `unit_for_observation` is in Task 7's `Consumes:` and is not called.** The
text unit is the span substrate §3.6's quote check needs, which is Task 17's; re-deriving context P4
already split is what M5 forbids. Every name in `Produces:` is delivered unchanged.
