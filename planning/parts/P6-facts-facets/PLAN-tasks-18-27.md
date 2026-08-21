### Task 27: Deterministic operation, and the walking-skeleton P6 step

**Files:**
- Test: `tests/p6/test_p6_deterministic.py`, `tests/p6/test_p6_skeleton_step.py`
- Creates and modifies **no** source file. This is the only task in the plan of which that is true,
  and it is the reason the step list below is not the ordinary red-green shape. See *This task
  writes no source file* immediately after the interfaces.

**Interfaces:**
- Consumes: `facts.resolver.FactResolver`; `evidence_shape.fixtures.by_number`; `facts.rules` —
  `Rule`, `apply_rules`; `facts.dates` — `DatePatterns`, `date_candidates`; `facts.facets` —
  `fill_or_abstain`; `facts.file_facts` — `facts_for_file`, `FILE_FACTS_COLUMNS`,
  `FORBIDDEN_COLUMN_SUBSTRINGS`; `facts.unresolved.unresolved_for_file`;
  `database_agent.files_table` — `record_file`, `get_file`; `evidence_shape.store` —
  `record_run`, `record_observation`, `observations_for_file`; `evidence_shape.vocabulary` —
  `RELIABILITY_STATES`, `ZONES`, `SOURCE_TYPES`; `orchestrator` — read-only, for the D5 guard.
  **Not** `orchestrator.run_wave2`, and **not** the Task 26 wiring, which does not exist (D5).
- Produces: nothing.

**Done-means:** 17, and the end-to-end half of 4.

> **The `Consumes` line the skeleton wrote for this task named "the Task 26 wiring". That wiring is
> cut (D5) and there is nothing to consume.** The skeleton's step resolves facts **from stored
> evidence** — P4's `evidence` rows, already written — and does not run through `run_wave2` at any
> point. Nothing in either test file imports `orchestrator.run_wave2`, and one of the tests asserts
> that `facts` appears nowhere in the orchestrator's import graph. See *The integration a reader
> will reach for here* below, which is placed at the exact point a reader would otherwise reach for
> it.

---

**This task writes no source file, and that changes what its red step can be.**

Every other task in this plan writes a module, so its red is guaranteed: the module does not exist
and the import fails. This task writes two test files against code that Tasks 1–25 have already
landed. If those tasks were done correctly, both files pass on their first run — and **a
verification task that passes on its first run has proved nothing about itself.** It could be
asserting `True == True` in nine places and the run would look identical.

So the cycle here is inverted and made explicit, and it is a real red-green rather than a
formality:

1. **Step 2 runs the file and states the expected failure**, which is genuine at the moment this
   task is executed and is stated exactly.
2. **Step 5 is a teeth proof**: the deterministic assertion is re-run once with a model deliberately
   configured, and it is **required to fail**. Then the configuration is removed and it is required
   to pass. Nothing under `src/` is touched in either direction — the mutation is a keyword argument
   in the test's own helper, applied and reverted inside the step. A guard that cannot be made to
   fail on demand is not a guard, and Done-means 17 is the plan's largest single claim.

This is stated rather than smuggled because the brief forbids placeholders and a "run it, it passes"
step would be one wearing a checkbox.

---

**Done-means 17, verbatim, because two halves of it are two different test files:**

> The whole of items 4–10, 13–16 and 18–27 pass with P8 absent and no model configured — the Wave 2
> requirement and the walking skeleton's `P6 resolve it to ONE validated fact (course = X) with its
> evidence link`.

**And the trap inside it: "P8 absent" is trivially true and therefore worth nothing on its own.**
There is no P8 package anywhere in the repository. `importlib.util.find_spec` cannot find one. So
every test in `tests/p6/` already runs with P8 absent, in the same sense that they run with a Mars
lander absent, and asserting it that way would be a green tick over an empty claim. The three things
that are **not** trivial, and that this task asserts separately:

- **No deterministic producer takes a model parameter at all.** Asserted from `inspect.signature`
  over every fact-producing entry point, so it holds for every call rather than for the one call a
  behavioural test happens to make.
- **No deterministic producer can reach the P8 seam.** `facts.llm_seam` appears in no producer
  module's import graph — an AST walk, not a text search. §3.3 puts every model call in P8; a
  producer that could import the seam has a path to a proposal, and then Done-means 17 rests on that
  path not being *taken* rather than on it not *existing*.
- **`llm_supported` is reachable from exactly one module.** §3.5 is why: *"A file fact is not
  inherently rule-based or LLM-based. It is the common format into which both systems write their
  conclusions."* One format, one table, and the producer is a column — so the state is a **value**,
  and the only assertion available is about which module can supply it. Exactly one can, and it is
  the module P8 talks to.

**One thing that will look like a violation and is not.** Every deterministic producer calls
`facts.cache.fact_cache_key(..., model_identifier=None, prompt_fingerprint=None)` — §3.4's key has
five parts and two of them are the model's, so a deterministic fact records them as `None` rather
than omitting them. Those two names therefore appear in every producer's source as **keyword
argument names**. The AST guard below collects `ast.Name`, `ast.Attribute` and import names, and a
keyword argument is an `ast.keyword` with an `arg` attribute, so it is correctly not collected. The
signature guard is the one that binds: no producer *accepts* either name. Written out because a
reviewer who reaches for `grep model_identifier src/facts/` will get thirteen hits and conclude the
guard is broken.

---

**The walking-skeleton step, read from the file rather than remembered.** `planning/02-segmentation-map.md`
line 190, verified byte-exact on 2026-08-22:

```text
P6      resolve it to ONE validated fact (subject = X) with its evidence link  [D6]
```

**It says `subject`, and Done-means 17 above still says `course`.** D6 is ratified — *the academic
field key is `subject`, and every stored field key is `snake_case`* — and the segmentation map has
been reconciled to it while the SPEC's Done-means 17 sentence has not. Per the skeleton's own rule
(*"if you find a line that still contradicts one, that line is the error, not the decision"*), the
stored field key this test asserts is **`subject`**, and `course` survives only inside the quotation
above. This is not a judgement call this task is making: Done-means 4's own amendment already says
so — *"The stored field key is `subject` … The `fields` catalogue carries a `subject` row and no
`course` row."*

Three properties of that one line decide the test:

- **ONE fact.** Not two, not a fact plus a `possible` clue. Fixture 1 carries one observation, and
  the skeleton's claim is that one observation resolves to one fact.
- **`validated`, not `direct`.** §3.13 reserves `direct` for a value read out of a reliable explicit
  slot; a course code recovered from a heading and confirmed by a §3.5 context term is a
  deterministic rule that passed a contextual check, which is `validated`'s own definition. The
  skeleton line says the word.
- **"with its evidence link"** — the `evidence_refs[]` entry, and it must be fixture 1's
  `observation_key` exactly. M14: never an `observation_id`, never a row id.

**Fixture 1 is the walking-skeleton fixture and its context string is what makes the step possible
at all.** Verified live on 2026-08-22 by loading it rather than by reading a document:

```text
by_number(1).design_case  '§2.8 "page 1, heading 2"; §3.2's syllabus'
raw_value                 'BUSIB 4300'
zone                      'heading'
locator                   'heading:page=1/heading=2'
reliability               'possible'
occurrence_count          3
context_before            'Syllabus — '     capital S, U+2014 EM DASH, one space either side
context_after             ' — Spring 2026'
extractor_name            'pdf.text'        source_type 'text_document', analysis_tier 'native'
run.file_id               'file-01'         run.content_hash '042896dc…b95da'
```

`context_before` is `'Syllabus — '` with a **capital S**. §3.5's context check is
case-insensitive — that is N-6, and B8(a) put this string on the fixture for exactly this reason: a
case-sensitive check comparing against a lowercase term list refuses the skeleton's own fixture and
the walking skeleton has no P6 step at all. Task 10 owns `context_check` and its case-insensitivity;
this task asserts the **consequence**, which is that the byte-exact fixture resolves.

**Fixture 1's `file_id` is `'file-01'` and its `content_hash` is P4's, not P1's.** The fixtures are
P4-shaped test data, not rows P1 created. P1's `content_hash` is 64 lowercase hex characters with no
`sha256:` prefix and is computed by `record_file` over real bytes, and `ExtractionRun.__post_init__`
rejects any other shape. So the test writes a real `files` row first and rebinds the fixture's run
and observation onto it with `dataclasses.replace` — the observation is frozen, `replace` is the
supported move, and it was verified to work on both `Observation` and `ExtractionRun` on
2026-08-22. **The `raw_value`, the location, the context pair and the reliability are carried across
untouched**, which is the whole point: the test must resolve P4's fixture, not a convenient
paraphrase of it. Rebinding changes `observation_key`, because the key hashes `content_hash ·
extractor_name · locator · raw_value` — so the test reads the key off the rebound observation and
never off the original.

---

**§3.2, quoted in full, because Done-means 4 is one sentence of it and the rest is the reason:**

> Raw evidence is not yet a fact. For example, the filename Syllabus BUSIB 4300 Spring 2026.pdf, the PDF title BUSIB 4300 Syllabus, and a page-one heading Spring 2026 are observations. From those observations, the system can create facts such as subject = BUSIB 4300, term = Spring 2026, and work type = syllabus. Similarly, an EXIF field called DateTimeOriginal is raw metadata; capture date = 2026-07-17 is the file fact derived from it. This distinction matters because the product must preserve both the original evidence and the conclusion built from it. If a resolver later improves, the system can generate a better interpretation while retaining the original filename, heading, metadata field, text span, or OCR result that supported the earlier interpretation.

Three observations in, three facts out, and **the observations unchanged afterwards** — the last
clause is not decoration, it is rule 1 of this part. P4 makes the assertion unfalsifiable at the
database (`evidence_never_overwritten` and `evidence_no_delete` triggers on the `evidence` table),
so the test asserts the *intent* and the triggers guarantee it cannot be satisfied by accident.

The three field keys are `subject`, `term` and `work_type` — §3.11's Academic row, in D6's
`snake_case`. The design's prose spells the third *"work type"* with a space; a field key is a join
handle and two spellings are two columns, so the stored key is `work_type` and the space survives
inside the quotation.

---

**The integration a reader will reach for here, and why it must not be made.**

This is the task that resolves the walking skeleton end to end, so it is the exact point at which a
reader thinks: *P6 works now — wire `no_usable_facts_for` into `run_wave2` and delete the stub.*

**Do not.** The authoring brief states the consequence in one line and it is not a preference:

> **If P6's resolver is ever passed to `run_wave2` as `no_usable_facts`, the first text-bearing PDF
> ends the scan.**

The mechanism, so it is checkable rather than believed:

- Task 19 has `no_usable_facts_for(...)` raise `FactPassNotRun` when the verdict is asked about a
  `(file_id, content_hash)` whose deterministic pass has not been recorded. `FactPassNotRun`
  inherits `extractors.failure.ContractViolation`, and `orchestrator._extract_one` **re-raises
  `ContractViolation` by name** instead of converting it into a `failed` run. So it does not degrade
  one file; it propagates out of the loop.
- `extractors.ocr_policy.text_layer_state` consults `no_usable_facts` for **every text-bearing PDF**,
  inside the caller's single loop, during extraction — before any deterministic pass could have run
  for that content hash. Worse than early: `document_ocr_decision` is called inside `extract()` on
  the freshly-built `ExtractionResult`, and `_write(sink, result, …)` does not run until
  `orchestrator.py:211`, so the observations P6 would reason about have not reached P4 at all.
- Reordering that loop was Task 26. **Task 26 is cut (D5)**, so nothing reorders it.

Therefore the caller keeps passing `orchestrator.TARGETED_OCR_UNAVAILABLE`, which is **kept, not
deleted** — round 5's simplification, recorded in the Task 26 cut note. P6 publishes
`no_usable_facts_for` as a read surface **its own tests exercise**, and wiring it is the four-pass
work, owed separately. One of the tests below asserts the negative directly: `facts` appears nowhere
in `orchestrator`'s imports, and `run_wave2`'s `no_usable_facts` parameter still has no default, so
nothing can acquire P6 by omission.

---

**The one declaration this task makes, and why it is made here.**

Task 27 is the only task that drives a producer chain end to end, so it is the first place several
sibling tasks' injected dataclasses are **constructed** rather than described. Three of them
(`DirectSlots`, `ActivationSignals`, `SessionBoundary`) are **not** constructed here — the tests
below reach them only through `inspect.signature`, never by instantiating them — so this task fixes
no field name of theirs.

One is constructed, and its field name is declared here because it cannot be avoided:

> **`DatePatterns(patterns: Mapping[str, re.Pattern[str]])`** — one field, `patterns`, keyed by
> **pattern id**. Task 12 already publishes `parse_exact(raw, *, pattern_id) -> str`, so pattern ids
> exist and are the handle; a mapping from id to compiled pattern is the smallest shape that
> supports it. The three ids §3.10 requires are `season_year` (`Spring 2025`), `academic_year`
> (`AY 2024-25`) and `named_term` (`Michaelmas Term 2024`). **Task 12 owns the contents and this
> task owns none of them** — the test injects its own patterns under those ids and asserts nothing
> about what Task 12's catalogue holds.
>
> If Task 12 lands a different field name, this task's `test_the_three_facts_of_the_designs_own_example`
> fails at construction — loudly, at integration, which is the correct behaviour for a contract and
> the reason it is written down rather than guessed at silently.

---

- [ ] **Step 1: Write `tests/p6/test_p6_deterministic.py`**

```python
# tests/p6/test_p6_deterministic.py
"""Done-means 17 -- every fact-producing path, with P8 absent and no model configured.

`02-segmentation-map.md`'s Wave 2 line is `P4 -> P5 -> P6  (deterministic only, no
model)`. This file is the assertion that the parenthesis is a property of the code
rather than of the diagram.

**"P8 absent" is trivially true and therefore worth nothing on its own.** There is no
P8 package in this repository, so every test in `tests/p6/` already runs with P8
absent in the same sense that it runs without a Mars lander. The three non-trivial
claims are asserted separately below: no deterministic producer TAKES a model
parameter, no deterministic producer can REACH the P8 seam, and `llm_supported` is
supplied by exactly one module.

**One thing that looks like a violation and is not.** §3.4's cache key has five parts
and two are the model's, so every deterministic producer calls `fact_cache_key(...,
model_identifier=None, prompt_fingerprint=None)` and those two names appear in every
producer's source. They appear as `ast.keyword` argument names, which the AST guard
below does not collect, and the signature guard is the one that binds: no producer
ACCEPTS either name.
"""
from __future__ import annotations

import ast
import importlib
import importlib.util
import inspect
import os
import subprocess
import sys
from pathlib import Path

import pytest

from evidence_shape.vocabulary import RELIABILITY_STATES

from facts.resolver import FactResolver

TEST_DIR = Path(__file__).resolve().parent
REPO_ROOT = TEST_DIR.parents[1]

#: Set in the child run so the recursive test skips itself. Everything else in this
#: file is cheap and runs in both.
CHILD_MARKER = "P6_DETERMINISTIC_SUITE_CHILD"

#: The state no deterministic path may reach. Read off P4's tuple, never spelled as a
#: literal: the six states have exactly one home (Global Constraints).
LLM_SUPPORTED = RELIABILITY_STATES[3]

#: Every fact-producing entry point in `facts`, module and function. This is the
#: plan's task list read off -- Tasks 8-16, 18 and 19 publish exactly these. It is
#: written out rather than discovered because a producer added later without being
#: added here would be exempt from both guards; `test_the_producer_list_is_the_whole_
#: of_facts` is the guard on that.
PRODUCERS = (
    ("facts.direct", "direct_facts"),
    ("facts.discount", "discount"),
    ("facts.rules", "apply_rules"),
    ("facts.facets", "fill_or_abstain"),
    ("facts.dates", "date_candidates"),
    ("facts.domains", "active_domains"),
    ("facts.families", "duplicate_family"),
    ("facts.families", "version_family"),
    ("facts.session", "bounded_sessions"),
    ("facts.photo_event", "photo_events"),
    ("facts.photo_event", "media_type"),
    ("facts.supersede", "supersede_fact"),
    ("facts.usable", "no_usable_facts_for"),
)

#: Modules in `facts` that are not producers: the tables, the vocabularies, the
#: reads, the seam, and the sequencer. Every name in `File Structure` is in exactly
#: one of these two lists.
NON_PRODUCERS = frozenset({
    "authorship", "budgets", "cache", "evidence", "fields", "file_facts",
    "learning", "llm_seam", "plan_versions", "read_surface", "resolver", "schema",
    "states", "stage_output", "unresolved", "values", "vocabulary",
})

#: The four names that would carry a model into a deterministic producer.
MODEL_PARAMETERS = ("propose", "validate", "model_identifier", "prompt_fingerprint")


def _facts_dir() -> Path:
    return Path(inspect.getfile(importlib.import_module("facts"))).resolve().parent


def _mentioned_names(module) -> set[str]:
    """Every name this module's CODE mentions.

    An AST walk, never a text search: a text search matches comments and docstrings,
    and a guard that does that has broken three tasks on this project already
    (P5 PLAN, Task 20). Keyword ARGUMENT names are deliberately not collected -- see
    the module docstring.
    """
    tree = ast.parse(inspect.getsource(module))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.add(node.module or "")
            names.update(alias.name for alias in node.names)
    return names


def test_no_deterministic_producer_takes_a_model_parameter():
    # "no model configured", proved from the SIGNATURES rather than from one call.
    # A producer that accepted `propose` would be a fact path a caller could turn
    # into a model path without P8 existing, which §3.3 forbids outright.
    offences = []
    for module_name, function_name in PRODUCERS:
        module = importlib.import_module(module_name)
        parameters = inspect.signature(getattr(module, function_name)).parameters
        for name in MODEL_PARAMETERS:
            if name in parameters:
                offences.append(f"{module_name}.{function_name}({name}=...)")
    assert offences == []


def test_no_deterministic_producer_reaches_the_p8_seam():
    # §3.3: every model call is P8's. A producer that can IMPORT the seam has a path
    # to a proposal, and Done-means 17 would then rest on that path not being taken
    # rather than on it not existing.
    for module_name in sorted({name for name, _ in PRODUCERS}):
        mentioned = _mentioned_names(importlib.import_module(module_name))
        assert "facts.llm_seam" not in mentioned, module_name
        assert "llm_seam" not in mentioned, module_name


def test_only_one_module_can_supply_the_llm_supported_state():
    # §3.5: "A file fact is not inherently rule-based or LLM-based. It is the common
    # format into which both systems write their conclusions." One format, one table,
    # and the producer is a COLUMN -- so `llm_supported` is a value, and the only
    # assertion available is about which module can supply it.
    reaching: set[str] = set()
    for path in sorted(_facts_dir().glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and node.value == LLM_SUPPORTED:
                reaching.add(path.stem)
            if (isinstance(node, ast.Subscript)
                    and isinstance(node.value, ast.Name)
                    and node.value.id in {"RELIABILITY_STATES", "STATES"}):
                reaching.add(path.stem)
    # `states` publishes the six once (Task 1); `llm_seam` is the module P8 talks to.
    assert reaching <= {"states", "llm_seam"}


def test_the_producer_list_is_the_whole_of_facts():
    # A guard on the two guards above: a producer module added to `src/facts/`
    # without being added to PRODUCERS would be exempt from both, silently.
    modules = {path.stem for path in _facts_dir().glob("*.py")} - {"__init__"}
    assert modules - NON_PRODUCERS == {name.split(".")[1] for name, _ in PRODUCERS}
    assert not (NON_PRODUCERS & {name.split(".")[1] for name, _ in PRODUCERS})


def test_an_absent_p8_is_an_explicit_none_and_never_an_omitted_argument():
    # Skeleton rule 4: every threshold and every injected surface is a required
    # keyword with no default. P8's two are where a default would be most tempting
    # and most wrong -- a defaulted `propose` is a model path nobody chose to enable.
    parameters = inspect.signature(FactResolver.__init__).parameters
    for name, parameter in parameters.items():
        if name == "self":
            continue
        assert parameter.kind is inspect.Parameter.KEYWORD_ONLY, name
        assert parameter.default is inspect.Parameter.empty, name
        assert parameter.default is not None, name
    for name in ("propose", "validate"):
        assert name in parameters


@pytest.mark.skipif(os.environ.get(CHILD_MARKER) == "1",
                    reason="this IS the child run; the parent asserts on its exit code")
def test_the_whole_p6_suite_passes_with_p8_absent_and_no_model_configured():
    # Done-means 17 in its own words: "The whole of items 4-10, 13-16 and 18-27 pass
    # with P8 absent and no model configured." The only honest way to assert "the
    # whole suite" is to run the whole suite, so it is run -- in a child process, with
    # a marker that stops this one test from recursing.
    assert importlib.util.find_spec("p8") is None
    assert importlib.util.find_spec("llm_harness") is None
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", str(TEST_DIR), "-q",
         "-p", "no:cacheprovider"],
        cwd=REPO_ROOT, env=dict(os.environ, **{CHILD_MARKER: "1"}),
        capture_output=True, text=True, timeout=900, check=False)
    assert completed.returncode == 0, completed.stdout[-4000:]
    assert " failed" not in completed.stdout
```

- [ ] **Step 2: Run it, and state the failure**

Run: `pytest tests/p6/test_p6_deterministic.py -v`

Expected: **FAIL** — `ModuleNotFoundError: No module named 'facts.resolver'` at collection, if this
task is run before Task 20 has landed. Task 20 is in Wave D and this task is in Wave E, so the
ordinary case is that it has landed, and then the expected failure is the one this task exists to
catch: an `AssertionError` from `test_no_deterministic_producer_takes_a_model_parameter` or from
`test_the_producer_list_is_the_whole_of_facts`, naming the producer that got it wrong.

**Neither failure is guaranteed, and Step 5 is where the guarantee comes from.** If all six tests
pass on the first run, that is the good outcome and it is still unproven until Step 5 makes the
central one fail on demand.

- [ ] **Step 3: Write `tests/p6/test_p6_skeleton_step.py`**

```python
# tests/p6/test_p6_skeleton_step.py
"""The walking skeleton's P6 step, and Done-means 4 end to end.

`planning/02-segmentation-map.md`, line 190, verbatim:

    P6      resolve it to ONE validated fact (subject = X) with its evidence link  [D6]

and §3.2's own three-observation example, which is the same step run over the whole of
the design's case rather than over one observation.

**This does not go through `run_wave2`.** Task 26 is cut (D5): the step resolves facts
from evidence P4 has already stored, and `facts` is wired into no caller. The last two
tests assert that negative directly, because this file is the exact place a reader
decides P6 is ready to be wired in. It is not, and the reason is in the plan above
this test: `ocr_policy.text_layer_state` consults `no_usable_facts` for every
text-bearing PDF before any deterministic pass has run, and Task 19's `FactPassNotRun`
is a `ContractViolation`, so the first text-bearing PDF would end the scan.
"""
from __future__ import annotations

import ast
import dataclasses
import inspect
import json
import re
from pathlib import Path

import pytest

import orchestrator

from database_agent.files_table import get_file, record_file

from evidence_shape.fixtures import by_number
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import observations_for_file, record_observation, record_run

from facts.dates import DatePatterns, date_candidates
from facts.facets import fill_or_abstain
from facts.file_facts import FORBIDDEN_COLUMN_SUBSTRINGS, facts_for_file
from facts.rules import Rule, apply_rules
from facts.unresolved import unresolved_for_file

CLOCK = "2026-08-19T14:00:00+00:00"

#: §3.11's Academic row in D6's snake_case. §3.2 spells the third "work type" with a
#: space; a field key is a join handle and two spellings are two columns.
SUBJECT, TERM, WORK_TYPE = "subject", "term", "work_type"

#: The rules the TEST injects. §3.5 states that a course-code-shaped string needs an
#: academic context term; it states no pattern and no term list, and Task 10 takes
#: both as injected `Rule`s for that reason. The terms are lowercase on purpose: the
#: context check is case-insensitive (N-6) and fixture 1's context is capital-S
#: "Syllabus -- ", so a case-sensitive check would refuse the skeleton's own fixture.
SUBJECT_RULE = Rule(pattern=re.compile(r"\b[A-Z]{4,6}\s\d{4}\b"),
                    required_context_terms=("syllabus", "course", "term"),
                    field_key=SUBJECT)
WORK_TYPE_RULE = Rule(pattern=re.compile(r"\b[Ss]yllabus\b"),
                      required_context_terms=("syllabus",),
                      field_key=WORK_TYPE)

#: §3.10's three named academic-term patterns, under the pattern ids Task 12's
#: `parse_exact(raw, *, pattern_id)` addresses them by. The TEST supplies these; the
#: catalogue Task 12 ships is its own and nothing here asserts anything about it.
PATTERNS = DatePatterns(patterns={
    "season_year": re.compile(r"\b(Spring|Summer|Autumn|Fall|Winter)\s(\d{4})\b"),
    "academic_year": re.compile(r"\bAY\s(\d{4})-(\d{2})\b"),
    "named_term": re.compile(r"\b(Michaelmas|Hilary|Trinity)\sTerm\s(\d{4})\b"),
})

#: §3.7's weights and thresholds are Deferred. Every number below is the TEST's.
ZONE_WEIGHT = {zone: 1.0 for zone in
               ("filename", "path", "metadata", "title", "heading", "body", "table",
                "header_footer", "notes", "link", "annotation", "reference_list",
                "manifest", "ocr", "transcript")}
ZONE_WEIGHT.update({"title": 5.0, "filename": 4.0, "heading": 3.0})
MINIMUM_SCORE, MINIMUM_MARGIN = 1.0, 0.5


def _p1_row(conn, tmp_path, *, name, body):
    """A real P1 `files` row over real bytes, so the content hash is P1's own.

    P1's hash is 64 lowercase hex characters with no `sha256:` prefix and
    `ExtractionRun.__post_init__` rejects any other shape, so the fixture's own
    `content_hash` cannot be reused against a P1 database.
    """
    path = tmp_path / name
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Courses", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _rebind(fixture, *, file_id, content_hash):
    """P4's fixture, moved onto a P1 row, with everything else carried across.

    `Observation` and `ExtractionRun` are frozen dataclasses and `dataclasses.replace`
    is the supported move (verified by execution, 2026-08-22). The raw value, the
    location, the context pair and the reliability come across untouched: the point is
    to resolve P4's fixture, not a convenient paraphrase of it.
    """
    run = dataclasses.replace(fixture.run, file_id=file_id,
                              content_hash=content_hash)
    observations = tuple(
        dataclasses.replace(one, file_id=file_id, content_hash=content_hash,
                            run_id=run.run_id)
        for one in fixture.observations)
    return run, observations


def _observe(conn, *, run_id, file_id, content_hash, raw, zone, label,
             extractor="pdf.text", context_before=None, context_after=None):
    """One ordinary P4-shaped observation, for §3.2's three-observation case."""
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name=extractor, extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name=extractor,
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location(zone, (Segment("field", label=label),)),
        occurrence_count=1, observed_at=CLOCK, reliability="possible",
        run_id=run_id, context_before=context_before, context_after=context_after)
    record_observation(conn, observation)
    return observation


@pytest.fixture()
def skeleton(p6_conn, tmp_path):
    """Fixture 1 -- the walking-skeleton fixture -- on a real P1 row."""
    fixture = by_number(1)
    file_id, content_hash = _p1_row(
        p6_conn, tmp_path, name="Syllabus BUSIB 4300 Spring 2026.pdf",
        body=b"one PDF whose title carries a course code")
    run, observations = _rebind(fixture, file_id=file_id,
                                content_hash=content_hash)
    record_run(p6_conn, run)
    for observation in observations:
        record_observation(p6_conn, observation)
    return file_id, content_hash, observations[0]


def test_fixture_one_resolves_to_one_validated_fact_with_its_evidence_link(
        skeleton, p6_conn):
    # The segmentation map's P6 step, whole: "resolve it to ONE validated fact
    # (subject = X) with its evidence link".
    file_id, content_hash, observation = skeleton
    written = apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                          rules=(SUBJECT_RULE,))
    assert len(written) == 1                                       # ONE fact
    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert len(rows) == 1
    row = rows[0]
    assert row["field_key"] == SUBJECT                             # subject = X (D6)
    assert row["canonical_value"] == "BUSIB 4300"
    assert row["reliability_state"] == "validated"                 # validated
    assert json.loads(row["evidence_refs"]) == [observation.observation_key]
    assert observation.observation_key.startswith("sha256:")       # M14, its link


def test_the_step_is_named_in_the_segmentation_map_in_these_words(skeleton, p6_conn):
    # The step is read from the file, not remembered. D6 rewrote `course = X` to
    # `subject = X` there; Done-means 17's sentence still says `course`, and the
    # skeleton's own rule is that the unreconciled line is the error, not the
    # decision.
    repo_root = Path(__file__).resolve().parents[2]
    text = (repo_root / "planning" / "02-segmentation-map.md").read_text(
        encoding="utf-8")
    assert "resolve it to ONE validated fact (subject = X) with its evidence link" \
        in text
    assert "(course = X)" not in text


def test_the_context_that_makes_it_resolvable_is_byte_exact(skeleton):
    # B8(a) put this string on fixture 1 so the skeleton's one fact is resolvable at
    # all, and N-6 is why it is capital-S: §3.5's context check is case-insensitive,
    # and a case-sensitive one comparing against a lowercase term list refuses the
    # walking skeleton's own fixture.
    _, _, observation = skeleton
    assert observation.context_before == "Syllabus — "        # U+2014 EM DASH
    assert observation.context_after == " — Spring 2026"
    assert observation.raw_value == "BUSIB 4300"
    assert observation.location.zone == "heading"
    assert observation.reliability == "possible"                   # a fact is not
    assert observation.occurrence_count == 3
    assert all(term.islower() for term in SUBJECT_RULE.required_context_terms)


def test_a_course_code_with_no_academic_context_produces_no_fact(p6_conn, tmp_path):
    # The negative half of the same rule, and the reason the positive half is not an
    # accident: the identical string in the identical zone, with the context removed.
    file_id, content_hash = _p1_row(p6_conn, tmp_path, name="unlabelled.pdf",
                                    body=b"a heading and nothing around it")
    _observe(p6_conn, run_id="bare", file_id=file_id, content_hash=content_hash,
             raw="BUSIB 4300", zone="heading", label="heading:page=1/heading=2")
    assert apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                       rules=(SUBJECT_RULE,)) == ()
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    rows = unresolved_for_file(p6_conn, file_id, content_hash, field_key=SUBJECT)
    assert [row["reason"] for row in rows] == ["context_check_failed"]


def test_the_three_facts_of_the_designs_own_example(p6_conn, tmp_path):
    # Done-means 4, end to end: "the filename Syllabus BUSIB 4300 Spring 2026.pdf, the
    # PDF title BUSIB 4300 Syllabus, and a page-one heading Spring 2026 are
    # observations. From those observations, the system can create facts such as
    # subject = BUSIB 4300, term = Spring 2026, and work type = syllabus."
    file_id, content_hash = _p1_row(
        p6_conn, tmp_path, name="Syllabus BUSIB 4300 Spring 2026.pdf",
        body=b"the design's own example")
    name = _observe(p6_conn, run_id="fn", file_id=file_id,
                    content_hash=content_hash,
                    raw="Syllabus BUSIB 4300 Spring 2026.pdf", zone="filename",
                    label="filename", extractor="filesystem.name")
    title = _observe(p6_conn, run_id="ti", file_id=file_id,
                     content_hash=content_hash, raw="BUSIB 4300 Syllabus",
                     zone="title", label="title",
                     context_before="Title: ", context_after=" (syllabus)")
    heading = _observe(p6_conn, run_id="hd", file_id=file_id,
                       content_hash=content_hash, raw="Spring 2026", zone="heading",
                       label="heading:page=1/heading=1",
                       context_before="Syllabus — ", context_after="")

    apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                rules=(SUBJECT_RULE, WORK_TYPE_RULE))
    candidates = tuple(candidate
                       for observation in (name, title, heading)
                       for candidate in date_candidates(observation,
                                                        patterns=PATTERNS))
    fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                    field_key=TERM, candidates=candidates,
                    minimum_score=MINIMUM_SCORE, minimum_margin=MINIMUM_MARGIN)

    rows = {row["field_key"]: row
            for row in facts_for_file(p6_conn, file_id, content_hash)}
    assert set(rows) == {SUBJECT, TERM, WORK_TYPE}                 # exactly three
    assert rows[SUBJECT]["canonical_value"] == "BUSIB 4300"
    assert rows[TERM]["canonical_value"] == "Spring 2026"
    assert rows[WORK_TYPE]["canonical_value"] == "syllabus"
    for row in rows.values():
        refs = json.loads(row["evidence_refs"])
        assert refs and all(ref.startswith("sha256:") for ref in refs)


def test_every_observation_is_unchanged_after_resolution(p6_conn, tmp_path):
    # §3.2: "the product must preserve both the original evidence and the conclusion
    # built from it." P4 makes this unfalsifiable at the database -- the `evidence`
    # table carries `evidence_never_overwritten` and `evidence_no_delete` triggers --
    # so this asserts the INTENT and the triggers guarantee it cannot pass by
    # accident.
    file_id, content_hash = _p1_row(p6_conn, tmp_path, name="unchanged.pdf",
                                    body=b"evidence outlives the conclusion")
    original = _observe(p6_conn, run_id="u", file_id=file_id,
                        content_hash=content_hash, raw="BUSIB 4300", zone="heading",
                        label="heading:page=1/heading=2",
                        context_before="Syllabus — ", context_after="")
    apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                rules=(SUBJECT_RULE,))
    after = [one for one in observations_for_file(p6_conn, file_id)
             if one.observation_key == original.observation_key]
    assert len(after) == 1
    assert after[0].raw_value == "BUSIB 4300"
    assert after[0].context_before == "Syllabus — "
    assert after[0].reliability == "possible"
    assert after[0].extractor_version == "1.0.0"


def test_the_resolved_fact_carries_no_path_destination_folder_or_group(
        skeleton, p6_conn):
    # §3.14: "A fact such as subject = BUSIB 4300 does not itself dictate one
    # permanent folder path." Task 4 asserts this of the SCHEMA; this asserts it of a
    # row the walking skeleton actually produced, which is where a reviewer looks.
    file_id, content_hash, _ = skeleton
    apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                rules=(SUBJECT_RULE,))
    row = facts_for_file(p6_conn, file_id, content_hash)[0]
    for column in row.keys():
        assert not [bad for bad in FORBIDDEN_COLUMN_SUBSTRINGS
                    if bad in column.lower()], column


def test_p6_is_not_wired_into_the_wave_2_caller():
    # D5 cut Task 26, and this is the point in the plan where a reader decides P6 is
    # ready to be wired in. It is not. `ocr_policy.text_layer_state` consults
    # `no_usable_facts` for every text-bearing PDF before any deterministic pass has
    # run, and Task 19's `FactPassNotRun` is a `ContractViolation` that
    # `orchestrator._extract_one` re-raises by name -- so passing P6's resolver ends
    # the scan on the first text-bearing PDF.
    tree = ast.parse(inspect.getsource(orchestrator))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
    assert not [name for name in imported if name.split(".")[0] == "facts"]
    # The stub is KEPT, not deleted -- round 5's simplification, in the Task 26 cut
    # note. And nothing can acquire P6 by omission: the parameter has no default.
    assert callable(orchestrator.TARGETED_OCR_UNAVAILABLE)
    parameter = inspect.signature(orchestrator.run_wave2).parameters[
        "no_usable_facts"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is inspect.Parameter.empty


def test_this_step_never_runs_through_run_wave2():
    # The other half of the same negative, from this test module's own imports: the
    # skeleton's P6 step resolves from STORED evidence. `orchestrator` is imported
    # here read-only, for the guard above, and `run_wave2` is not imported at all.
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imported_names.update(f"{node.module}.{alias.name}"
                                  for alias in node.names)
    assert "orchestrator.run_wave2" not in imported_names
    assert not [name for name in imported_names
                if name.startswith("extractors.")]
```

- [ ] **Step 4: Run it, and state the failure**

Run: `pytest tests/p6/test_p6_skeleton_step.py -v`

Expected: **FAIL**. The certain failure is at collection —
`ImportError: cannot import name 'DatePatterns' from 'facts.dates'` if Task 12 named its injected
dataclass differently, which is the contract this task declared above and the reason it declared it
in writing. Absent that, the expected failure is
`test_the_three_facts_of_the_designs_own_example` with `AssertionError: set(rows) == {subject, term,
work_type}` — the design's example is the plan's hardest single end-to-end claim and it is the one
most likely to be short by one field.

- [ ] **Step 5: Prove the deterministic guard has teeth**

The point of Step 5, restated once so nobody skips it: Steps 2 and 4 expect failures that are
*likely*, not *guaranteed*. This step produces a **guaranteed** failure and then removes it, so
Done-means 17's central assertion is known to be capable of failing.

Temporarily add this producer to `PRODUCERS` in `tests/p6/test_p6_deterministic.py`:

```python
    ("facts.llm_seam", "apply_verdict"),
```

Run: `pytest tests/p6/test_p6_deterministic.py::test_no_deterministic_producer_takes_a_model_parameter -v`

Expected: **FAIL** — `AssertionError: assert ['facts.llm_seam.apply_verdict(propose=...)'] == []`,
or the same failure naming whichever of the four model parameters `apply_verdict` carries. The seam
is the one module that legitimately takes them, so adding it to the deterministic list must break
the guard; if the guard stays green with the seam in the list, it is asserting nothing and Task 27
has not been done.

Then **revert that one line** and run the file again:

Run: `pytest tests/p6/test_p6_deterministic.py -v`
Expected: **PASS**

Nothing under `src/` is edited in either direction.

- [ ] **Step 6: Run both files and the whole part**

Run: `pytest tests/p6/test_p6_deterministic.py tests/p6/test_p6_skeleton_step.py -v`
Expected: PASS — 6 passed, 9 passed

Run: `pytest tests/p6 -q`
Expected: PASS — the whole part, and
`test_the_whole_p6_suite_passes_with_p8_absent_and_no_model_configured` runs it a second time in a
child process with `P6_DETERMINISTIC_SUITE_CHILD=1` set, where that one test skips itself.

Run: `pytest -q`
Expected: PASS — 1300 tests plus P6's, and **no P1–P5 test changes status**, which is Done-means
17's silent half: this part touches no file outside `src/facts/` and `tests/p6/` (D5), so a
regression anywhere else is this plan having broken its own boundary.

- [ ] **Step 7: Commit**

```bash
git add tests/p6/test_p6_deterministic.py tests/p6/test_p6_skeleton_step.py
git commit -m "test(P6): deterministic operation with P8 absent, and the walking-skeleton step from stored evidence"
```

---
