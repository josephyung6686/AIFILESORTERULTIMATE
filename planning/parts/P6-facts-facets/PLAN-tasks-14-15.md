# P6 — Facts and facets — PLAN, Tasks 14–19

> This is the detail pass for **Wave C (14–16)** and the first three tasks of **Wave D (17–19)**.
> The rules, the verified seams and the file layout are in `PLAN-SKELETON.md`; the `Interfaces:`
> block on each task below is the same contract, honoured name for name. Tasks 1–13 and 20–27 are
> written in parallel by other authors against the same skeleton.

---

## What already exists when Task 14 starts

Tasks 1–13 are green. These tasks import the following and nothing else from `facts`. Every
signature below is the skeleton's `Produces:` line, unchanged:

```text
facts.states        STATES: tuple[str, ...]                       (P4's six, re-exported)
                    strength(state: str) -> int
                    is_stronger(a: str, b: str) -> bool
facts.fields        get_field(conn, field_key) -> sqlite3.Row
                    FieldNotInCatalogue
facts.values        VALUE_ORIGINS: tuple[str, str]                ("automatic", "user")
                    ensure_value(conn, *, field_key, canonical_value,
                                 first_evidence_ref, origin) -> str
facts.file_facts    FACT_ORIGINS: tuple[str, ...]                 (§3.1's five, in §3.1's order)
                    write_fact(conn, *, file_id, content_hash, field_key, value_id,
                               reliability_state, origin, evidence_refs, cache_key,
                               active, ...) -> str
                    facts_for_file(conn, file_id, content_hash) -> list[sqlite3.Row]
                    EvidenceRequired
facts.unresolved    ATTEMPTED_PRODUCERS: tuple[str, str, str]     ("direct", "rule", "llm")
                    write_unresolved(conn, *, file_id, content_hash, field_key, reason,
                                     attempted_producers, evidence_refs, cache_key) -> str
                    unresolved_for_file(conn, file_id, content_hash, *,
                                        field_key=None, reason=None) -> list[sqlite3.Row]
facts.cache         fact_cache_key(*, content_hash, extractor_version, analysis_tier,
                                   model_identifier, prompt_fingerprint) -> str
facts.evidence      observations_for_version(conn, file_id, content_hash) -> tuple[Observation, ...]
                    cite(observation) -> str
                    analysis_tier_for_observation(conn, observation) -> str
facts.facets        Candidate(value, score, evidence_refs)
                    fill_or_abstain(conn, *, file_id, content_hash, field_key, candidates,
                                    minimum_score, minimum_margin) -> str | None
facts.domains       active_field_allowlist(conn, *, file_id, content_hash,
                                           activation_signals) -> tuple[str, ...]
facts.schema        create_facts_schema(conn) -> None
```

**`tests/p6/conftest.py` publishes `p6_conn`** — P1's database with P4's three tables and P6's own
tables created, built on the root `conn` fixture in `tests/conftest.py`, exactly as `tests/p4/conftest.py`
builds `p4_conn`. Every test file below takes `p6_conn` and constructs everything else itself.

**Two spellings are never assumed.** `FACT_ORIGINS` and `ATTEMPTED_PRODUCERS` are addressed **by
index**, in the order the skeleton lists them (`FACT_ORIGINS` = deterministic extractor · rule · LLM
interpretation · user correction · user-approved folder; `ATTEMPTED_PRODUCERS` = direct · rule ·
llm). Task 4 and Task 5 own the literal spelling of each member; a producer that re-spelled one
would be a second home for a closed vocabulary, which is exactly what the skeleton's rule 2 forbids.

**Verified live, 2026-08-22, by import rather than from a document.** `mark_superseded(conn, table,
*, old_id, new_id, reason) -> None`; `chain(conn, table, record_id) -> list[sqlite3.Row]`;
`supersede_ddl(table)` returns `"supersedes TEXT, superseded_by TEXT, supersede_reason TEXT"`;
`RELIABILITY_STATES == ("user_confirmed", "direct", "validated", "llm_supported", "possible",
"rejected")`; `ANALYSIS_TIERS == ("filesystem", "native", "ocr", "llm")`; `SIGNAL_TIERS == (1, 2, 3)`
and its members are **integers**; `observation_key` is a `@property` on `Observation` and returns a
`sha256:`-prefixed string; `Observation.signal_tier` survives a store round trip as an `int`;
`Observation.location.container_path` survives as a tuple of `Segment`; P1's `content_hash` is
**64 lowercase hex characters with no `sha256:` prefix** (`database_agent.identity.is_content_hash`),
and `ExtractionRun.__post_init__` rejects any other shape.

---

## The one cache-key rule these six tasks share

§3.4's key is *"content hash + extractor version + analysis tier + model identifier + prompt
fingerprint"*, and Task 6 publishes it as five scalar keywords. But a fact built from several
observations has **several** extractor versions and **several** analysis tiers, and no task in this
plan owns the reconciliation. These tasks therefore apply one rule, stated here once and written out
identically in each module that needs it:

- **`extractor_version`** is `canonical_json` of the sorted distinct `[extractor_name,
  extractor_version]` pairs of the observations the fact cites. P4's `canonical_json` is the
  project's one deterministic serialization; a second one would be a second answer.
- **`analysis_tier`** is the **last** tier present in `ANALYSIS_TIERS` order — `filesystem` <
  `native` < `ocr` < `llm`. That is a reading of P4's published tuple order, not a new order, and it
  gives preamble rule 5 exactly the property it needs: a fact that cited an `ocr` observation lands
  in a different cache slot from one that cited only `native` observations, so pass 4 supersedes
  rather than overwrites. A single member is passed, not a list, because `fact_cache_key` may check
  the value against `ANALYSIS_TIERS`.
- **`model_identifier` and `prompt_fingerprint` are `None`** on every deterministic fact. P4's
  `sha256_of` is length-prefixed and injective, so `None` is distinguishable from `""` in the digest.

**This is reported, not resolved.** The reconciliation belongs in `facts.cache`, which Task 6 owns;
these tasks cannot add to another task's module without breaking its contract, so the rule is
written out three times, once per producer, with this note above it. See *Contract ambiguities* at
the end.

---

### Wave C — the three fact families P6 was handed (14–16 parallelise)

### Task 14: Duplicate family and version family (G5)

**Files:**
- Create: `src/facts/families.py`
- Test: `tests/p6/test_p6_families.py`

**Interfaces:**
- Consumes: `facts.evidence` — `observations_for_version`, `cite`, `analysis_tier_for_observation`;
  `database_agent.files_table.get_file`; `facts.file_facts` — `write_fact`, `FACT_ORIGINS`;
  `facts.unresolved` — `write_unresolved`, `ATTEMPTED_PRODUCERS`; `facts.values` — `ensure_value`,
  `VALUE_ORIGINS`; `facts.cache.fact_cache_key`; `evidence_shape.canonical` — `canonical_json`,
  `sha256_of`; `evidence_shape.vocabulary` — `ANALYSIS_TIERS`, `check`.
- Produces (`families.py`): `DUPLICATE_FAMILY_FIELD: str`, `VERSION_FAMILY_FIELD: str`,
  `PERCEPTUAL_HASH_LABEL: str`, `VERSION_FAMILY_STATES: tuple[str, str]`,
  `Lineage(family_value, reliability_state, evidence_refs)`,
  `duplicate_family(conn, *, file_ids, perceptual_hash_label, near_match) -> tuple[str, ...]`,
  `version_family(conn, *, file_ids, lineage_rule) -> tuple[str, ...]`.

**Done-means:** 23, 24.

**§8.3, quoted, because the refusal is the sentence:**

> The collision rule must distinguish exact duplicates from different files that happen to share a filename. A content-hash match supports deduplication review; a filename match alone does not.

**§2.6, quoted, because it is where near-duplicates come from:**

> Exact hashes and perceptual hashes can identify duplicates and near-duplicates.

**Version family had no owner anywhere in the design.** §2.9 lists *"duplicate and version-family
signals"* among what basic extraction produces and defines neither; nothing else in the design names
a version-family rule. So this task builds the two ends the design does state — byte identity, and
the refusal — and holds the middle open behind an injected `lineage_rule`. A rule that returns
nothing writes nothing, and that is the default state of the product until someone authors one.

**What the evidence for byte identity actually is, and why it is not the `files` row.** Task 4
requires every non-user fact to carry at least one `evidence_refs[]` entry and every entry to be a
P4 `observation_key` (M14). P1's `content_hash` lives on the `files` row and is **not** an
observation — P5's `filesystem.py` says so in its own source: *"G5 gives duplicate and version-family
signals to P6 'from P1's content hashes' … P6 reads those from `files`; a second copy here would be
two homes for one value."* So the hash decides the family and cannot be cited for it.

The citation is the observations the two versions **share**. `observation_key` hashes
`content_hash · extractor_name · locator · raw_value` and nothing else (P4 MINOR 8, verified), so two
files holding the same bytes produce, for every extractor that reads those bytes, literally the same
keys. That is not a proxy for byte identity; it is a consequence of it, recorded in P4's own
addressing, and a reviewer following the citation lands on the readings that are the same reading for
both files. It is also the property P4's OQ2 closure states outright: the content hash owns the
observation, so two `files` rows holding the same bytes share one observation set.

**When the shared set is empty, P6 abstains rather than asserting.** A fact with no citable evidence
is not a fact (rule 1), so the pair gets an `unresolved` row with `reason = no_candidate_evidence`
rather than a `direct` fact nobody can inspect. This is a real branch, not a defensive one: a file
version with no stored observations at all reaches it.

**A pair the design never asks about gets no row of any kind.** `report (1).pdf` and
`invoice (1).pdf` share a `(1)` suffix and nothing else. Their hashes differ, neither carries a
perceptual-hash observation, and the injected lineage rule returns nothing — so no family fact, and
**no `unresolved` row either**. The SPEC's `unresolved` schema is explicit that `field_key` is *"the
field that was attempted"*; a relation nobody proposed was never attempted, and recording it as a
refusal would make the abstention table a log of every pair in the corpus.

**`PERCEPTUAL_HASH_LABEL` is a parameter name, not a label.** P5 writes the perceptual hash as an
ordinary observation whose only distinguisher is its container-path label — and that label is P5's
string, with a space in it. P6 holding a copy would be two homes for one spelling, so the label
arrives as a required keyword with no default and the module publishes the **name of that keyword**
so the injection site has one address. Task 25's introspection can assert the property directly:
`families.PERCEPTUAL_HASH_LABEL` names a keyword-only parameter of `duplicate_family` with no
default. The test below asserts P5's actual string appears in none of this module's code.

**Two families, two value schemes, and the reason they differ.** An exact family has a natural name —
the content hash itself, which §3.13 names a Direct source and which a reviewer can verify by
hashing the bytes. A near family has none, so its value is `sha256_of(canonical_json(sorted(
perceptual-hash raw values)))`: deterministic, member-derived, and carrying no path. Adding a member
changes the near family's name, which is acceptable for a `possible` clue and is stated rather than
hidden.

**A family is only as strong as its weakest link.** `version_family` collects the injected rule's
edges, unions them into components, and writes one fact per member at the **weakest** state any edge
in that component carried. `Lineage.__post_init__` refuses `direct` outright, so Done-means 24's
*"never receive a `direct` one at all"* is enforced at the type rather than at a call site.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_families.py
"""G5 — Done-means 23 and 24. §8.3's refusal, and the two families P6 was handed."""
from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from evidence_shape.vocabulary import NotInVocabulary

from extractors.image import PERCEPTUAL_HASH_FIELD

from facts import families
from facts.families import (
    DUPLICATE_FAMILY_FIELD, Lineage, PERCEPTUAL_HASH_LABEL, VERSION_FAMILY_FIELD,
    duplicate_family, version_family,
)
from facts.file_facts import facts_for_file
from facts.unresolved import unresolved_for_file

CLOCK = "2026-08-19T12:00:00+00:00"

#: P5 spells the label; P6 injects it. The test is the only place the two meet.
LABEL = PERCEPTUAL_HASH_FIELD


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
             extractor="pdf.text", zone="metadata", source_type="text_document",
             analysis_tier="native"):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name=extractor, extractor_version="1.0.0",
        source_type=source_type, analysis_tier=analysis_tier, config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name=extractor,
        extractor_version="1.0.0", source_type=source_type, raw_value=raw,
        location=Location(zone, (Segment("field", label=label),)),
        occurrence_count=1, observed_at=CLOCK, reliability="direct", run_id=run_id)
    record_observation(conn, observation)
    return observation.observation_key


def _never_near(left: str, right: str) -> bool:
    """The injected near-match predicate that never matches. P6 states no distance."""
    return False


def _no_lineage(conn, left_file_id: str, right_file_id: str):
    """§2.9 lists 'duplicate and version-family signals' and defines neither."""
    return None


@pytest.fixture()
def twins(p6_conn, tmp_path):
    """Two `files` rows over identical bytes: one content hash, two file ids."""
    left, left_hash = _record(p6_conn, tmp_path, name="Syllabus.pdf",
                              body=b"BUSIB 4300 Syllabus, Spring 2026")
    right, right_hash = _record(p6_conn, tmp_path, name="Syllabus copy.pdf",
                                body=b"BUSIB 4300 Syllabus, Spring 2026")
    assert left_hash == right_hash
    key_left = _observe(p6_conn, run_id="r-left", file_id=left,
                        content_hash=left_hash, raw="application/pdf",
                        label="mime_type")
    key_right = _observe(p6_conn, run_id="r-right", file_id=right,
                         content_hash=right_hash, raw="application/pdf",
                         label="mime_type")
    assert key_left == key_right          # the whole point: one key, two files
    return left, right, left_hash, key_left


def test_two_byte_identical_files_share_a_direct_duplicate_family_fact(twins, p6_conn):
    # Done-means 23. §3.13 names the content hash a Direct source.
    left, right, content_hash, _ = twins
    written = duplicate_family(p6_conn, file_ids=(left, right),
                               perceptual_hash_label=LABEL, near_match=_never_near)
    assert len(written) == 2
    for file_id in (left, right):
        rows = [r for r in facts_for_file(p6_conn, file_id, content_hash)
                if r["field_key"] == DUPLICATE_FAMILY_FIELD]
        assert len(rows) == 1
        assert rows[0]["reliability_state"] == "direct"
        assert rows[0]["canonical_value"] == content_hash


def test_the_duplicate_family_cites_the_keys_the_two_versions_share(twins, p6_conn):
    # M14: every entry is an observation key, and the key is what byte identity
    # produces twice. P1's content hash decides; P4's key is what a reviewer follows.
    left, right, content_hash, shared_key = twins
    duplicate_family(p6_conn, file_ids=(left, right),
                     perceptual_hash_label=LABEL, near_match=_never_near)
    row = [r for r in facts_for_file(p6_conn, left, content_hash)
           if r["field_key"] == DUPLICATE_FAMILY_FIELD][0]
    assert json.loads(row["evidence_refs"]) == [shared_key]
    assert shared_key.startswith("sha256:")


def test_a_duplicate_pair_with_nothing_to_cite_abstains(p6_conn, tmp_path):
    # Rule 1: a fact with no citable evidence is not a fact. Two identical files with
    # no stored observations get a refusal that names itself, not a silent gap.
    left, content_hash = _record(p6_conn, tmp_path, name="a.pdf", body=b"same bytes")
    right, _ = _record(p6_conn, tmp_path, name="b.pdf", body=b"same bytes")
    assert duplicate_family(p6_conn, file_ids=(left, right),
                            perceptual_hash_label=LABEL,
                            near_match=_never_near) == ()
    for file_id in (left, right):
        rows = unresolved_for_file(p6_conn, file_id, content_hash,
                                   field_key=DUPLICATE_FAMILY_FIELD)
        assert [r["reason"] for r in rows] == ["no_candidate_evidence"]


def test_a_perceptual_hash_near_match_is_possible_and_never_direct(p6_conn, tmp_path):
    # §2.6 distinguishes "duplicates and near-duplicates"; §8.3 keeps the hash match
    # as the only thing that supports deduplication review.
    left, left_hash = _record(p6_conn, tmp_path, name="photo.jpg", body=b"pixels-one")
    right, right_hash = _record(p6_conn, tmp_path, name="photo-resized.jpg",
                                body=b"pixels-two")
    assert left_hash != right_hash
    _observe(p6_conn, run_id="p-left", file_id=left, content_hash=left_hash,
             raw="phash:00ff00ff", label=LABEL, extractor="image.metadata",
             source_type="image")
    _observe(p6_conn, run_id="p-right", file_id=right, content_hash=right_hash,
             raw="phash:00ff00fe", label=LABEL, extractor="image.metadata",
             source_type="image")
    written = duplicate_family(p6_conn, file_ids=(left, right),
                               perceptual_hash_label=LABEL,
                               near_match=lambda a, b: a[:-1] == b[:-1])
    assert len(written) == 2
    states = {r["reliability_state"]
              for file_id, digest in ((left, left_hash), (right, right_hash))
              for r in facts_for_file(p6_conn, file_id, digest)
              if r["field_key"] == DUPLICATE_FAMILY_FIELD}
    assert states == {"possible"}


def test_the_container_path_label_is_injected_and_the_module_holds_no_copy():
    # P5 owns the spelling and it has a space in it. A copy here would be a second
    # home for one string, which is this project's most expensive defect.
    assert PERCEPTUAL_HASH_LABEL == "perceptual_hash_label"
    parameter = inspect.signature(duplicate_family).parameters[PERCEPTUAL_HASH_LABEL]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is inspect.Parameter.empty
    assert LABEL not in _code_strings(families)
    near = inspect.signature(duplicate_family).parameters["near_match"]
    assert near.default is inspect.Parameter.empty


def test_two_files_sharing_only_a_one_suffix_share_no_family_of_either_kind(
        p6_conn, tmp_path):
    # Done-means 23 and 24, and §8.5's "duplicate suffixes on unrelated files".
    left, left_hash = _record(p6_conn, tmp_path, name="report (1).pdf",
                              body=b"quarterly report")
    right, right_hash = _record(p6_conn, tmp_path, name="invoice (1).pdf",
                                body=b"an invoice")
    _observe(p6_conn, run_id="s-left", file_id=left, content_hash=left_hash,
             raw="report (1).pdf", label="normalized_filename")
    _observe(p6_conn, run_id="s-right", file_id=right, content_hash=right_hash,
             raw="invoice (1).pdf", label="normalized_filename")
    assert duplicate_family(p6_conn, file_ids=(left, right),
                            perceptual_hash_label=LABEL,
                            near_match=_never_near) == ()
    assert version_family(p6_conn, file_ids=(left, right),
                          lineage_rule=_no_lineage) == ()
    for file_id, digest in ((left, left_hash), (right, right_hash)):
        assert facts_for_file(p6_conn, file_id, digest) == []
        # A relation nobody proposed was never attempted; `unresolved` records the
        # field that WAS attempted, not every pair in the corpus.
        assert unresolved_for_file(p6_conn, file_id, digest) == []


def test_identical_hashes_are_a_duplicate_family_and_never_a_version_family(
        twins, p6_conn):
    left, right, content_hash, _ = twins

    def always(conn, a, b):
        return Lineage(family_value="v1", reliability_state="validated",
                       evidence_refs=("sha256:deadbeef",))

    assert version_family(p6_conn, file_ids=(left, right), lineage_rule=always) == ()
    rows = [r for r in facts_for_file(p6_conn, left, content_hash)
            if r["field_key"] == VERSION_FAMILY_FIELD]
    assert rows == []


def test_a_version_family_fact_is_never_direct():
    # Done-means 24: no explicit slot states a version relation, so the refusal is at
    # the type rather than at a call site.
    assert families.VERSION_FAMILY_STATES == ("validated", "possible")
    with pytest.raises(NotInVocabulary):
        Lineage(family_value="v1", reliability_state="direct",
                evidence_refs=("sha256:deadbeef",))
    assert Lineage(family_value="v1", reliability_state="possible",
                   evidence_refs=("sha256:deadbeef",)).reliability_state == "possible"


def test_an_empty_lineage_rule_writes_no_version_family_fact(p6_conn, tmp_path):
    # §2.9 names the signals and defines none, so the default state of the product is
    # a rule that establishes nothing.
    left, left_hash = _record(p6_conn, tmp_path, name="draft v1.docx", body=b"one")
    right, right_hash = _record(p6_conn, tmp_path, name="draft v2.docx", body=b"two")
    assert version_family(p6_conn, file_ids=(left, right),
                          lineage_rule=_no_lineage) == ()
    assert facts_for_file(p6_conn, left, left_hash) == []
    assert facts_for_file(p6_conn, right, right_hash) == []


def test_a_lineage_that_cites_no_evidence_is_refused_rather_than_asserted(
        p6_conn, tmp_path):
    left, left_hash = _record(p6_conn, tmp_path, name="draft v1.docx", body=b"one")
    right, right_hash = _record(p6_conn, tmp_path, name="draft v2.docx", body=b"two")

    def uncited(conn, a, b):
        return Lineage(family_value="draft", reliability_state="validated",
                       evidence_refs=())

    assert version_family(p6_conn, file_ids=(left, right),
                          lineage_rule=uncited) == ()
    for file_id, digest in ((left, left_hash), (right, right_hash)):
        rows = unresolved_for_file(p6_conn, file_id, digest,
                                   field_key=VERSION_FAMILY_FIELD)
        assert [r["reason"] for r in rows] == ["no_candidate_evidence"]


def test_the_result_does_not_depend_on_the_order_the_file_ids_arrive_in(
        twins, p6_conn):
    # P4's reads are in insertion order and P6 must not inherit it (Global
    # Constraints). Two orders, one outcome, compared as sets of stored rows.
    left, right, content_hash, _ = twins
    forward = duplicate_family(p6_conn, file_ids=(left, right),
                               perceptual_hash_label=LABEL, near_match=_never_near)
    reverse = duplicate_family(p6_conn, file_ids=(right, left),
                               perceptual_hash_label=LABEL, near_match=_never_near)
    assert len(forward) == len(reverse) == 2

    def shape(ids):
        return sorted(
            (r["file_id"], r["reliability_state"], r["canonical_value"],
             r["evidence_refs"])
            for file_id in (left, right)
            for r in facts_for_file(p6_conn, file_id, content_hash)
            if r["fact_id"] in ids and r["field_key"] == DUPLICATE_FAMILY_FIELD)

    assert shape(forward) == shape(reverse)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p6/test_p6_families.py -v`
Expected: FAIL — collection error, `ModuleNotFoundError: No module named 'facts.families'`

- [ ] **Step 3: Write `families.py`**

```python
# src/facts/families.py
"""G5 — the duplicate family and the version family (§2.6, §2.9, §3.11, §8.3).

Both are §3.11 universal fields and **version family had no owner anywhere in the
design**. §2.9 lists "duplicate and version-family signals" among what basic
extraction produces and defines neither, so this module builds the two ends the
design does state and holds the middle open:

    byte identity          §8.3: "A content-hash match supports deduplication
                           review; a filename match alone does not."     -> `direct`
    near-duplicates        §2.6: "Exact hashes and perceptual hashes can identify
                           duplicates and near-duplicates."              -> `possible`
    shared lineage         nothing states it                             -> injected

**Why the decision and the citation are different objects.** P1's `content_hash`
lives on the `files` row and is not an observation -- `extractors/filesystem.py`
deliberately does not re-emit it, because "a second copy here would be two homes for
one value". So the hash decides membership and cannot be cited for it. What is cited
is the observations the members SHARE: `observation_key` hashes
`content_hash / extractor_name / locator / raw_value` and nothing else, so two files
holding the same bytes produce literally the same keys for every extractor that read
those bytes. The citation is a consequence of byte identity, not a proxy for it.

When the shared set is empty, this module abstains: a fact with no citable evidence
is not a fact, and the refusal is a row (B7), not a gap.

**No filename ever establishes either family.** `report (1).pdf` and
`invoice (1).pdf` share a suffix and nothing else. That pair produces no fact and no
`unresolved` row: the SPEC's `unresolved` schema records "the field that was
attempted", and a relation nobody proposed was never attempted.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from itertools import combinations
from typing import Any, Callable, Iterable, Mapping

from database_agent.files_table import get_file

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.observation import Observation
from evidence_shape.vocabulary import ANALYSIS_TIERS, check

from facts.cache import fact_cache_key
from facts.evidence import analysis_tier_for_observation, cite, observations_for_version
from facts.file_facts import FACT_ORIGINS, write_fact
from facts.unresolved import ATTEMPTED_PRODUCERS, write_unresolved
from facts.values import VALUE_ORIGINS, ensure_value

#: §3.11's universal field keys, snake_case per D6. Resolved through the catalogue on
#: every write, so a drift raises `FieldNotInCatalogue` rather than inserting a field.
DUPLICATE_FAMILY_FIELD: str = "duplicate_family"
VERSION_FAMILY_FIELD: str = "version_family"

#: The NAME of the required keyword the container-path label arrives under -- not the
#: label. P5 spells the label and it has a space in it; a copy here would be a second
#: home for one string. Task 25 asserts this names a keyword-only parameter of
#: `duplicate_family` with no default.
PERCEPTUAL_HASH_LABEL: str = "perceptual_hash_label"

#: Done-means 24: a version family is never `direct`, because no explicit slot states
#: a version relation. §3.13: a deterministic rule that passes a contextual check is
#: `validated`; anything weaker is `possible`.
VERSION_FAMILY_STATES: tuple[str, str] = ("validated", "possible")


@dataclass(frozen=True)
class Lineage:
    """One injected rule's verdict that two file versions share lineage.

    The rule is the caller's: §2.9 names the signals and states none of them. What
    this type enforces is the half the design DOES state -- that the answer is never
    `direct`.
    """
    family_value: str
    reliability_state: str
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        check(self.reliability_state, VERSION_FAMILY_STATES, name="reliability_state")


@dataclass(frozen=True)
class _Version:
    """One (file, content hash) with its evidence already read once."""
    file_id: str
    content_hash: str
    observations: tuple[Observation, ...]

    @property
    def keys(self) -> frozenset[str]:
        return frozenset(cite(one) for one in self.observations)


def _read(conn: sqlite3.Connection, file_ids: Iterable[str]) -> tuple[_Version, ...]:
    """Every version, in file-id order.

    Sorted before anything is decided. P4's reads are in insertion order (verified by
    execution) and insertion order is a property of one database, not of the corpus;
    a computation that inherited it would make the same corpus resolve differently
    depending on the order it was extracted in.
    """
    versions = []
    for file_id in sorted(set(file_ids)):
        row = dict(get_file(conn, file_id))
        content_hash = row["content_hash"]
        versions.append(_Version(
            file_id=file_id, content_hash=content_hash,
            observations=tuple(observations_for_version(conn, file_id, content_hash))))
    return tuple(versions)


def _cache_key(conn: sqlite3.Connection, *, content_hash: str,
               observations: Iterable[Observation]) -> str:
    """§3.4's five parts for a fact built from several observations.

    §3.4 states one extractor version and one analysis tier; a fact citing several
    observations has several of each, and no task owns the reconciliation. The rule
    is written out here rather than shared because `facts.cache` is another task's
    module: the versions are the canonical JSON of the sorted distinct
    (name, version) pairs, and the tier is the LAST one present in `ANALYSIS_TIERS`
    order -- filesystem < native < ocr < llm -- so a fact that cited an `ocr`
    reading lands outside the cache slot the native pass computed under, which is
    what makes preamble rule 5's pass 4 supersede rather than overwrite.
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


def _abstain(conn: sqlite3.Connection, *, version: _Version, field_key: str,
             producer: str) -> None:
    """B7: a refusal is a row naming the field and the reason it refused."""
    write_unresolved(
        conn, file_id=version.file_id, content_hash=version.content_hash,
        field_key=field_key, reason="no_candidate_evidence",
        attempted_producers=(producer,), evidence_refs=(),
        cache_key=_cache_key(conn, content_hash=version.content_hash,
                             observations=version.observations))


def _write_family(conn: sqlite3.Connection, *, version: _Version, field_key: str,
                  canonical_value: str, reliability_state: str, origin: str,
                  evidence_refs: tuple[str, ...],
                  cited: tuple[Observation, ...]) -> str:
    value_id = ensure_value(conn, field_key=field_key,
                            canonical_value=canonical_value,
                            first_evidence_ref=evidence_refs[0],
                            origin=VALUE_ORIGINS[0])
    return write_fact(
        conn, file_id=version.file_id, content_hash=version.content_hash,
        field_key=field_key, value_id=value_id,
        reliability_state=reliability_state, origin=origin,
        evidence_refs=evidence_refs,
        cache_key=_cache_key(conn, content_hash=version.content_hash,
                             observations=cited),
        active=True)


def duplicate_family(conn: sqlite3.Connection, *, file_ids: Iterable[str],
                     perceptual_hash_label: str,
                     near_match: Callable[[str, str], bool]) -> tuple[str, ...]:
    """Done-means 23. Byte identity is `direct`; a near match is at most `possible`.

    `perceptual_hash_label` and `near_match` are required with no default. §2.6 names
    the perceptual hash and states no distance metric and no threshold, so P6 holds
    neither; the label is P5's string and P6 holds no copy of it.
    """
    versions = _read(conn, file_ids)
    written: list[str] = []

    by_hash: dict[str, list[_Version]] = {}
    for version in versions:
        by_hash.setdefault(version.content_hash, []).append(version)

    exact_members: set[str] = set()
    for content_hash, members in sorted(by_hash.items()):
        if len(members) < 2:
            continue
        exact_members.update(member.file_id for member in members)
        shared = sorted(frozenset.intersection(*(m.keys for m in members)))
        for member in members:
            if not shared:
                _abstain(conn, version=member, field_key=DUPLICATE_FAMILY_FIELD,
                         producer=ATTEMPTED_PRODUCERS[0])
                continue
            cited = tuple(one for one in member.observations
                          if cite(one) in set(shared))
            written.append(_write_family(
                conn, version=member, field_key=DUPLICATE_FAMILY_FIELD,
                canonical_value=content_hash, reliability_state="direct",
                origin=FACT_ORIGINS[0], evidence_refs=tuple(shared), cited=cited))

    written.extend(_near_families(conn, versions=versions,
                                  perceptual_hash_label=perceptual_hash_label,
                                  near_match=near_match))
    return tuple(written)


def _perceptual(version: _Version, label: str) -> tuple[Observation, ...]:
    """Every observation whose container path carries the injected label."""
    return tuple(
        one for one in version.observations
        if any(segment.label == label
               for segment in one.location.container_path))


def _near_families(conn: sqlite3.Connection, *, versions: tuple[_Version, ...],
                   perceptual_hash_label: str,
                   near_match: Callable[[str, str], bool]) -> list[str]:
    """§2.6's near-duplicates, at `possible` and never above.

    Pairs already in one exact family are skipped: they are a duplicate family at
    `direct` already, and a weaker second fact over the same members for the same
    field is noise rather than evidence.
    """
    carriers = {version.file_id: readings
                for version in versions
                if (readings := _perceptual(version, perceptual_hash_label))}
    parent = {file_id: file_id for file_id in carriers}

    def find(file_id: str) -> str:
        while parent[file_id] != file_id:
            parent[file_id] = parent[parent[file_id]]
            file_id = parent[file_id]
        return file_id

    by_id = {version.file_id: version for version in versions}
    for left, right in combinations(sorted(carriers), 2):
        if by_id[left].content_hash == by_id[right].content_hash:
            continue
        if any(near_match(a.raw_value, b.raw_value)
               for a in carriers[left] for b in carriers[right]):
            parent[find(left)] = find(right)

    components: dict[str, list[str]] = {}
    for file_id in sorted(carriers):
        components.setdefault(find(file_id), []).append(file_id)

    written: list[str] = []
    for members in sorted(components.values()):
        if len(members) < 2:
            continue
        raws = sorted({one.raw_value for file_id in members
                       for one in carriers[file_id]})
        canonical_value = sha256_of(canonical_json(raws))
        for file_id in members:
            cited = carriers[file_id]
            refs = tuple(sorted(cite(one) for one in cited))
            written.append(_write_family(
                conn, version=by_id[file_id], field_key=DUPLICATE_FAMILY_FIELD,
                canonical_value=canonical_value, reliability_state="possible",
                origin=FACT_ORIGINS[0], evidence_refs=refs, cited=cited))
    return written


def version_family(conn: sqlite3.Connection, *, file_ids: Iterable[str],
                   lineage_rule: Callable[[sqlite3.Connection, str, str],
                                          Lineage | None]) -> tuple[str, ...]:
    """Done-means 24. Distinct content hashes, never `direct`, never a filename.

    `lineage_rule` is required with no default and receives the connection and the
    two file ids: §2.9 names the signals and defines none, so P6 states nothing about
    what a lineage is and a rule that establishes nothing writes nothing.

    A family is only as strong as its weakest link -- a component joined by one
    `validated` edge and one `possible` edge is written at `possible`, because the
    component is only connected at all through the weaker claim.
    """
    versions = _read(conn, file_ids)
    by_id = {version.file_id: version for version in versions}
    parent = {version.file_id: version.file_id for version in versions}
    edges: dict[str, list[Lineage]] = {}

    def find(file_id: str) -> str:
        while parent[file_id] != file_id:
            parent[file_id] = parent[parent[file_id]]
            file_id = parent[file_id]
        return file_id

    refused: set[str] = set()
    for left, right in combinations(sorted(by_id), 2):
        # Identical hashes are a duplicate family, never a version family.
        if by_id[left].content_hash == by_id[right].content_hash:
            continue
        lineage = lineage_rule(conn, left, right)
        if lineage is None:
            continue
        if not lineage.evidence_refs:
            refused.update((left, right))
            continue
        parent[find(left)] = find(right)
        for file_id in (left, right):
            edges.setdefault(file_id, []).append(lineage)

    for file_id in sorted(refused):
        if file_id not in edges:
            _abstain(conn, version=by_id[file_id], field_key=VERSION_FAMILY_FIELD,
                     producer=ATTEMPTED_PRODUCERS[1])

    components: dict[str, list[str]] = {}
    for file_id in sorted(by_id):
        if file_id in edges:
            components.setdefault(find(file_id), []).append(file_id)

    written: list[str] = []
    for members in sorted(components.values()):
        if len(members) < 2:
            continue
        lineages = [one for file_id in members for one in edges[file_id]]
        canonical_value = min(one.family_value for one in lineages)
        weakest = ("possible" if any(one.reliability_state == "possible"
                                     for one in lineages) else "validated")
        for file_id in members:
            refs = tuple(sorted({ref for one in edges[file_id]
                                 for ref in one.evidence_refs}))
            cited = tuple(one for one in by_id[file_id].observations
                          if cite(one) in set(refs))
            written.append(_write_family(
                conn, version=by_id[file_id], field_key=VERSION_FAMILY_FIELD,
                canonical_value=canonical_value, reliability_state=weakest,
                origin=FACT_ORIGINS[1], evidence_refs=refs, cited=cited))
    return tuple(written)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p6/test_p6_families.py -v`
Expected: PASS — 11 passed

- [ ] **Step 5: Commit**

```bash
git add src/facts/families.py tests/p6/test_p6_families.py
git commit -m "feat(P6): G5 duplicate and version families — a hash decides, a filename never does"
```

---

### Task 15: The bounded download session (G6)

**Files:**
- Create: `src/facts/session.py`
- Test: `tests/p6/test_p6_session.py`

**Interfaces:**
- Consumes: `database_agent.files_table.get_file` (`observed_timestamps`, `directory_position`);
  `facts.evidence` — `observations_for_version`, `cite`, `analysis_tier_for_observation`;
  `facts.file_facts` — `write_fact`, `FACT_ORIGINS`; `facts.unresolved` — `write_unresolved`,
  `ATTEMPTED_PRODUCERS`; `facts.values` — `ensure_value`, `VALUE_ORIGINS`;
  `facts.cache.fact_cache_key`; `evidence_shape.canonical` — `canonical_json`, `sha256_of`;
  `evidence_shape.vocabulary.ANALYSIS_TIERS`.
- Produces (`session.py`): `DOWNLOAD_SESSION_FIELD: str`, `SESSION_STATE: str`,
  `SessionBoundary(window_seconds, require_same_parent_folder_context, minimum_members)` — injected,
  no defaults; `SessionNeverPromoted(ValueError)`, `require_possible(reliability_state) -> str`,
  `bounded_sessions(conn, *, file_ids, boundary) -> Mapping[str, str]`.

**Done-means:** 25.

**§3.9, quoted, because every clause of it binds:**

> Purpose may be supported strongly by an existing user-created folder name or explicit language in a form or portal. It may be supported more weakly by a tightly bounded download session. A session should never be treated as proof of topic, and it should not carry the same confidence as a hash match or a directly extracted document fact. It is a purpose clue and a review aid, not a basis for automatic semantic propagation.

**§4.7, quoted, because it is the other half of the ceiling:**

> A tight download session alone is never sufficient: it is a retrieval clue that may bring the files together, but not proof of their shared purpose.

**The ceiling is enforced at a function, not at a call site.** *"It should not carry the same
confidence as a hash match or a directly extracted document fact"* is a statement about every route,
not about this module's one call. So `require_possible` is the module's only gate to a
`download_session` write and it raises on anything but `possible` — a test can attempt the promotion
directly and require the raise, which is what the skeleton asks for and what inspecting a call site
cannot give. No rule promotes it because no rule can reach the write.

**Being `possible` is what keeps it out of a folder proposal, and that is by construction.** §3.6's
proposal-eligible read excludes `possible` and `rejected`; the session never becomes eligible
because the state it is pinned at is one of the two excluded ones. There is no second mechanism and
there is nothing to remember to switch off.

**`destination_eligible = FALSE` for the field.** §3.9 calls the session *"a purpose clue and a
review aid"*; a folder level built from one would put the download window into the tree. The
catalogue is Task 2's, so this task asserts the property rather than setting it.

**The fact is written for the member file only.** §3.9: *"not a basis for automatic semantic
propagation"*; §4.3 and §4.1 say the same for groups — the graph *"does not automatically copy those
missing facts onto sparse files"*. Membership in a session gives a file one row on one field and
nothing else, ever.

**Half of §3.9's evidence has no observation to cite, and that is a finding rather than a
workaround.** §3.9's two inputs are the timestamps and the parent-folder context. P5's
`filesystem.py` emits the parent-folder context as an ordinary observation at `zone = "path"` —
citable. It deliberately emits **no** timestamp observation, because G6 hands the session to P6
"computed from P3 timestamps" and a second copy would be two homes for one value. So the mtime is
read from P1's `files` row and is not citable, and a session whose members carry no `path`
observation has nothing to cite at all: it abstains with `reason = no_candidate_evidence` rather
than asserting an uninspectable clue. Reported under *Contract ambiguities*.

**The session's name is a digest, not a folder.** A session identifier built from the parent folder's
name would put a path fragment inside a value, which is the same mistake §3.14's negative contract
forbids at the column level. The canonical value is
`sha256_of(canonical_json(sorted(member file ids)))`: deterministic, inspectable, and carrying
nothing about where the files sat. Adding a member renames the session, which is acceptable for a
clue that may never exceed `possible` and is stated rather than hidden.

**Silence is not a refusal.** A file whose two inputs exist but which lands in no session gets no
fact and no `unresolved` row, on the same reading Task 14 applies: `unresolved` records *"the field
that was attempted"*, and a window that simply contained one file was never a proposal.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_session.py
"""G6 — Done-means 25. §3.9's bounded download session, pinned at `possible`."""
from __future__ import annotations

import dataclasses
import inspect
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file

from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run

from facts import session
from facts.fields import get_field
from facts.file_facts import FACT_ORIGINS, facts_for_file, write_fact
from facts.session import (
    DOWNLOAD_SESSION_FIELD, SESSION_STATE, SessionBoundary, SessionNeverPromoted,
    bounded_sessions, require_possible,
)
from facts.unresolved import unresolved_for_file
from facts.values import VALUE_ORIGINS, ensure_value

CLOCK = "2026-08-19T12:00:00+00:00"

#: Every number below is the TEST's, injected. §3.9 requires the clue and states no
#: numbers, so the module holds none.
TIGHT = SessionBoundary(window_seconds=120.0,
                        require_same_parent_folder_context=True,
                        minimum_members=2)


def _download(conn, tmp_path, *, name, body, mtime, parent="Downloads",
              with_path_observation=True, run_id=None):
    path = tmp_path / parent / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": mtime}),
        parent_folder_context=parent, mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    content_hash = get_file(conn, file_id)["content_hash"]
    run_id = run_id or f"run-{name}"
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="filesystem.record", extractor_version="0.1.0",
        source_type="filesystem", analysis_tier="filesystem", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    key = None
    if with_path_observation:
        # P5's `filesystem.py` emits §2.9's parent-folder context at zone `path`.
        observation = Observation(
            file_id=file_id, content_hash=content_hash,
            extractor_name="filesystem.record", extractor_version="0.1.0",
            source_type="filesystem", raw_value=parent,
            location=Location("path"), occurrence_count=1, observed_at=CLOCK,
            reliability="possible", run_id=run_id)
        record_observation(conn, observation)
        key = observation.observation_key
    return file_id, content_hash, key


def _session_rows(conn, file_id, content_hash):
    return [r for r in facts_for_file(conn, file_id, content_hash)
            if r["field_key"] == DOWNLOAD_SESSION_FIELD]


@pytest.fixture()
def one_session(p6_conn, tmp_path):
    left = _download(p6_conn, tmp_path, name="transcript.pdf", body=b"one",
                     mtime=1_700_000_000.0)
    right = _download(p6_conn, tmp_path, name="resume.pdf", body=b"two",
                      mtime=1_700_000_060.0)
    return left, right


def test_a_session_derived_fact_is_possible(one_session, p6_conn):
    # Done-means 25, and §3.13's "a possible fact is a useful but insufficient clue,
    # such as membership in a short download session".
    (left, left_hash, _), (right, right_hash, _) = one_session
    written = bounded_sessions(p6_conn, file_ids=(left, right), boundary=TIGHT)
    assert set(written) == {left, right}
    for file_id, digest in ((left, left_hash), (right, right_hash)):
        rows = _session_rows(p6_conn, file_id, digest)
        assert len(rows) == 1
        assert rows[0]["reliability_state"] == "possible"
    assert SESSION_STATE == "possible"


def test_no_code_path_can_write_the_session_field_at_another_state():
    # §3.9: it "should not carry the same confidence as a hash match or a directly
    # extracted document fact". Attempted, not inspected.
    assert require_possible("possible") == "possible"
    for state in ("validated", "direct", "llm_supported", "user_confirmed"):
        with pytest.raises(SessionNeverPromoted):
            require_possible(state)


def test_a_session_fact_is_absent_from_the_proposal_eligible_read(one_session, p6_conn):
    # §3.6 excludes `possible`, so the exclusion is the state and not a second rule.
    (left, left_hash, _), (right, _, _) = one_session
    bounded_sessions(p6_conn, file_ids=(left, right), boundary=TIGHT)
    read_surface = pytest.importorskip("facts.read_surface")
    eligible = read_surface.proposal_eligible(p6_conn, file_id=left,
                                              content_hash=left_hash)
    assert [r["field_key"] for r in eligible] == []


def test_the_download_session_field_is_never_destination_eligible(p6_conn):
    # §3.9 makes it a purpose clue and a review aid; a folder level built from one
    # would put the download window into the tree.
    row = get_field(p6_conn, DOWNLOAD_SESSION_FIELD)
    assert row["scope"] == "universal"
    assert not row["destination_eligible"]


def test_the_session_fact_is_written_for_the_member_file_only(one_session, p6_conn):
    # §3.9: "not a basis for automatic semantic propagation"; §4.1: the graph "does
    # not automatically copy those missing facts onto sparse files".
    (left, left_hash, left_key), (right, right_hash, _) = one_session
    value_id = ensure_value(p6_conn, field_key="subject",
                            canonical_value="BUSIB 4300",
                            first_evidence_ref=left_key, origin=VALUE_ORIGINS[0])
    write_fact(p6_conn, file_id=left, content_hash=left_hash, field_key="subject",
               value_id=value_id, reliability_state="validated",
               origin=FACT_ORIGINS[1], evidence_refs=(left_key,),
               cache_key="sha256:cache", active=True)
    bounded_sessions(p6_conn, file_ids=(left, right), boundary=TIGHT)
    right_fields = {r["field_key"]
                    for r in facts_for_file(p6_conn, right, right_hash)}
    assert right_fields == {DOWNLOAD_SESSION_FIELD}


def test_the_boundary_is_injected_and_the_module_states_no_window():
    # §3.9 requires the clue and states no numbers, so none is here.
    fields = dataclasses.fields(SessionBoundary)
    assert [f.name for f in fields] == ["window_seconds",
                                        "require_same_parent_folder_context",
                                        "minimum_members"]
    for field in fields:
        assert field.default is dataclasses.MISSING
        assert field.default_factory is dataclasses.MISSING
    parameter = inspect.signature(bounded_sessions).parameters["boundary"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is inspect.Parameter.empty
    # Task 25's technique: runtime introspection of the namespace, not a text search.
    numbers = {name: value for name, value in vars(session).items()
               if isinstance(value, (int, float)) and not isinstance(value, bool)}
    assert numbers == {}


def test_files_outside_the_window_are_not_one_session(p6_conn, tmp_path):
    left = _download(p6_conn, tmp_path, name="a.pdf", body=b"one",
                     mtime=1_700_000_000.0)
    right = _download(p6_conn, tmp_path, name="b.pdf", body=b"two",
                      mtime=1_700_009_999.0)
    assert bounded_sessions(p6_conn, file_ids=(left[0], right[0]),
                            boundary=TIGHT) == {}
    assert _session_rows(p6_conn, left[0], left[1]) == []
    assert _session_rows(p6_conn, right[0], right[1]) == []


def test_a_session_below_the_minimum_is_not_a_session(p6_conn, tmp_path):
    # "Tightly bounded" is the caller's definition, including how many files make one.
    only = _download(p6_conn, tmp_path, name="alone.pdf", body=b"one",
                     mtime=1_700_000_000.0)
    assert bounded_sessions(p6_conn, file_ids=(only[0],), boundary=TIGHT) == {}
    assert _session_rows(p6_conn, only[0], only[1]) == []
    # Silence, not a refusal: a window that contained one file was never a proposal.
    assert unresolved_for_file(p6_conn, only[0], only[1]) == []


def test_a_member_with_no_citable_parent_folder_observation_abstains(
        p6_conn, tmp_path):
    # Rule 1: an uninspectable clue is not a clue. P5 writes no timestamp
    # observation, so a member with no `path` observation has nothing to cite.
    left = _download(p6_conn, tmp_path, name="a.pdf", body=b"one",
                     mtime=1_700_000_000.0, with_path_observation=False)
    right = _download(p6_conn, tmp_path, name="b.pdf", body=b"two",
                      mtime=1_700_000_060.0, with_path_observation=False)
    assert bounded_sessions(p6_conn, file_ids=(left[0], right[0]),
                            boundary=TIGHT) == {}
    for file_id, digest, _ in (left, right):
        rows = unresolved_for_file(p6_conn, file_id, digest,
                                   field_key=DOWNLOAD_SESSION_FIELD)
        assert [r["reason"] for r in rows] == ["no_candidate_evidence"]


def test_the_session_value_is_deterministic_and_carries_no_path(one_session, p6_conn):
    (left, left_hash, _), (right, right_hash, _) = one_session
    bounded_sessions(p6_conn, file_ids=(left, right), boundary=TIGHT)
    values = {_session_rows(p6_conn, file_id, digest)[0]["canonical_value"]
              for file_id, digest in ((left, left_hash), (right, right_hash))}
    assert len(values) == 1
    value = values.pop()
    assert value.startswith("sha256:")
    assert "Downloads" not in value


def test_different_parent_folder_contexts_are_not_one_session(p6_conn, tmp_path):
    left = _download(p6_conn, tmp_path, name="a.pdf", body=b"one",
                     mtime=1_700_000_000.0, parent="Downloads")
    right = _download(p6_conn, tmp_path, name="b.pdf", body=b"two",
                      mtime=1_700_000_060.0, parent="Desktop")
    assert bounded_sessions(p6_conn, file_ids=(left[0], right[0]),
                            boundary=TIGHT) == {}
    relaxed = SessionBoundary(window_seconds=120.0,
                              require_same_parent_folder_context=False,
                              minimum_members=2)
    assert set(bounded_sessions(p6_conn, file_ids=(left[0], right[0]),
                                boundary=relaxed)) == {left[0], right[0]}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p6/test_p6_session.py -v`
Expected: FAIL — collection error, `ModuleNotFoundError: No module named 'facts.session'`

- [ ] **Step 3: Write `session.py`**

```python
# src/facts/session.py
"""G6 — §3.9's tightly bounded download session, pinned at `possible` (§4.2).

§3.9, and every clause binds:

    "It may be supported more weakly by a tightly bounded download session. A session
     should never be treated as proof of topic, and it should not carry the same
     confidence as a hash match or a directly extracted document fact. It is a
     purpose clue and a review aid, not a basis for automatic semantic propagation."

So:

- the ceiling is a FUNCTION, not a call site. `require_possible` is the only gate to
  a `download_session` write and it raises on anything else, so no rule can promote
  the field and no §3.7 margin can reach it;
- being `possible` is what keeps it out of §3.6's proposal-eligible read. There is no
  second mechanism, and nothing to remember to switch off;
- the fact is written for the member file and copies nothing. §4.1: the graph "does
  not automatically copy those missing facts onto sparse files".

**What is citable and what is not.** §3.9's two inputs are the timestamps and the
parent-folder context. P5 emits the parent-folder context as an ordinary observation
at `zone = "path"`; it deliberately emits NO timestamp observation, because G6 hands
the session to P6 "computed from P3 timestamps" and a second copy would be two homes
for one value. The mtime is therefore read from P1's `files` row and is not citable,
and a member with no `path` observation has nothing to cite at all: it abstains
rather than asserting a clue nobody can inspect.

**The session's name is a digest.** A name built from the parent folder would put a
path fragment inside a value, which is §3.14's mistake one layer down.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from database_agent.files_table import get_file

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.observation import Observation
from evidence_shape.vocabulary import ANALYSIS_TIERS

from facts.cache import fact_cache_key
from facts.evidence import analysis_tier_for_observation, cite, observations_for_version
from facts.file_facts import FACT_ORIGINS, write_fact
from facts.unresolved import ATTEMPTED_PRODUCERS, write_unresolved
from facts.values import VALUE_ORIGINS, ensure_value

#: The one universal field this part adds beyond §3.11's six, because §3.9 requires a
#: representation and §4.2 requires it to be retrievable. It is not `purpose`: the
#: session names no purpose value.
DOWNLOAD_SESSION_FIELD: str = "download_session"

#: §3.13's own example of a `possible` fact is "membership in a short download
#: session". The ceiling and the floor are the same value.
SESSION_STATE: str = "possible"

#: P4's zone for §2.9's parent-folder context, as P5 writes it. Read from P4's
#: vocabulary rather than from an extractor name: P6 branches on neither
#: `source_type` nor `extractor_name` anywhere.
PARENT_FOLDER_ZONE: str = "path"


class SessionNeverPromoted(ValueError):
    """§3.9's ceiling, raised rather than documented."""


@dataclass(frozen=True)
class SessionBoundary:
    """What makes a session "tightly bounded". Injected; the design states none.

    Every field is required. §3.9 asks for the clue and gives no window, no folder
    rule and no minimum, so a default here would be P6 answering a deferred question
    inside an implementation.
    """
    window_seconds: float
    require_same_parent_folder_context: bool
    minimum_members: int


def require_possible(reliability_state: str) -> str:
    """The only gate to a `download_session` write.

    §3.9: a session "should not carry the same confidence as a hash match or a
    directly extracted document fact". That is a statement about every route, so it
    is enforced where every route has to pass rather than at the one call this module
    makes -- a test can attempt the promotion and require the raise.
    """
    if reliability_state != SESSION_STATE:
        raise SessionNeverPromoted(
            f"§3.9 pins a download-session clue at {SESSION_STATE!r}; "
            f"{reliability_state!r} would give a retrieval clue the confidence of a "
            "hash match or a directly extracted document fact")
    return reliability_state


@dataclass(frozen=True)
class _Member:
    file_id: str
    content_hash: str
    mtime: float
    parent_folder_context: str
    observations: tuple[Observation, ...]

    @property
    def citable(self) -> tuple[Observation, ...]:
        return tuple(one for one in self.observations
                     if one.zone == PARENT_FOLDER_ZONE)


def _members(conn: sqlite3.Connection,
             file_ids: Iterable[str]) -> tuple[_Member, ...]:
    """Every file that carries §3.9's two inputs, ordered by time then by file id.

    The secondary key is not decoration: two files written in the same second must
    fall in one order for one corpus regardless of the order P4 stored them in.
    """
    members: list[_Member] = []
    for file_id in sorted(set(file_ids)):
        row = dict(get_file(conn, file_id))
        parent = row["directory_position"]
        stamps = json.loads(row["observed_timestamps"] or "{}")
        mtime = stamps.get("mtime")
        if parent is None or mtime is None:
            continue          # §3.9's inputs are absent; nothing was proposed
        content_hash = row["content_hash"]
        members.append(_Member(
            file_id=file_id, content_hash=content_hash, mtime=float(mtime),
            parent_folder_context=parent,
            observations=tuple(observations_for_version(conn, file_id,
                                                        content_hash))))
    return tuple(sorted(members, key=lambda m: (m.mtime, m.file_id)))


def _windows(members: tuple[_Member, ...],
             boundary: SessionBoundary) -> list[list[_Member]]:
    """Consecutive members inside the injected window, as one chain each."""
    runs: list[list[_Member]] = []
    for member in members:
        if runs and _joins(runs[-1][-1], member, boundary):
            runs[-1].append(member)
        else:
            runs.append([member])
    return [run for run in runs if len(run) >= boundary.minimum_members]


def _joins(previous: _Member, candidate: _Member,
           boundary: SessionBoundary) -> bool:
    if candidate.mtime - previous.mtime > boundary.window_seconds:
        return False
    if (boundary.require_same_parent_folder_context
            and previous.parent_folder_context
            != candidate.parent_folder_context):
        return False
    return True


def _cache_key(conn: sqlite3.Connection, *, content_hash: str,
               observations: Iterable[Observation]) -> str:
    """§3.4's five parts. The rule is stated once in the plan and applied here.

    The versions are the canonical JSON of the sorted distinct (name, version) pairs
    of the cited observations; the tier is the last one present in `ANALYSIS_TIERS`
    order, so a fact citing an `ocr` reading lands outside the slot the native pass
    computed under.
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


def bounded_sessions(conn: sqlite3.Connection, *, file_ids: Iterable[str],
                     boundary: SessionBoundary) -> Mapping[str, str]:
    """Done-means 25. `file_id -> fact_id` for every member of a bounded session.

    A file whose two §3.9 inputs exist but which lands in no session gets no fact and
    no `unresolved` row: the abstention record names "the field that was attempted",
    and a window that contained one file was never a proposal. A file that IS in a
    session but has nothing to cite abstains, because a clue nobody can inspect is
    not a clue.
    """
    written: dict[str, str] = {}
    for window in _windows(_members(conn, file_ids), boundary):
        citable = {member.file_id: member.citable for member in window}
        if not all(citable.values()):
            for member in window:
                write_unresolved(
                    conn, file_id=member.file_id,
                    content_hash=member.content_hash,
                    field_key=DOWNLOAD_SESSION_FIELD,
                    reason="no_candidate_evidence",
                    attempted_producers=(ATTEMPTED_PRODUCERS[0],),
                    evidence_refs=(),
                    cache_key=_cache_key(conn,
                                         content_hash=member.content_hash,
                                         observations=member.observations))
            continue
        canonical_value = sha256_of(canonical_json(
            sorted(member.file_id for member in window)))
        for member in window:
            refs = tuple(sorted(cite(one) for one in citable[member.file_id]))
            value_id = ensure_value(
                conn, field_key=DOWNLOAD_SESSION_FIELD,
                canonical_value=canonical_value, first_evidence_ref=refs[0],
                origin=VALUE_ORIGINS[0])
            written[member.file_id] = write_fact(
                conn, file_id=member.file_id, content_hash=member.content_hash,
                field_key=DOWNLOAD_SESSION_FIELD, value_id=value_id,
                reliability_state=require_possible(SESSION_STATE),
                origin=FACT_ORIGINS[0], evidence_refs=refs,
                cache_key=_cache_key(conn, content_hash=member.content_hash,
                                     observations=citable[member.file_id]),
                active=True)
    return written
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p6/test_p6_session.py -v`
Expected: PASS — 11 passed

- [ ] **Step 5: Commit**

```bash
git add src/facts/session.py tests/p6/test_p6_session.py
git commit -m "feat(P6): G6 the bounded download session — a clue, pinned at possible"
```

---
