# tests/p6/test_p6_no_invention.py
"""Task 25 -- the no-invention guard.

Every threshold, weight, gazetteer, regex catalogue, producer string, resolution, aspect
ratio, session window, GPS radius and usable-fact count in P6 is injected by the caller
with no default. Every still-open question in P6's SPEC stays open. The two that closed
(OQ4, OQ11) have their guards INVERTED, so this file fails if the closure is ever quietly
un-applied.

Nothing here reads source text. Two runtime tools and nothing else:

  * ``vars(module)`` walked recursively -- every module-level binding and everything
    reachable inside it: tuples, mappings, frozen dataclasses.
  * the module's compiled code object, recursed through nested code objects -- every
    literal the compiler kept, INCLUDING literals inside function bodies.

The second matters because the namespace walk alone cannot see a literal buried in a
function body, and that is exactly where a copied catalogue would end up. A comment can
never reach ``co_consts``; a docstring reaches it only as the whole docstring, so an
EQUALITY test against a short token like ``"P6"`` or ``"python-docx"`` cannot be satisfied
by prose.

One exemption, and it is by identity, which is the point. A ``facts`` module that does
``from evidence_shape.vocabulary import SIGNAL_TIERS`` binds a tuple of integers at module
level. That is a re-export of P4's published vocabulary, not a P6 invention, and the guard
exempts it because ``id(value)`` matches an object P4 published -- so a re-export passes
and a hand-typed copy of the same numbers fails. A CONTIGUOUS SLICE of a published
upstream tuple is exempt on the same grounds: ``facts.photo_event`` reads S2.6's
screenshot band as ``SIGNAL_TIERS[-1:]`` precisely so it does not have to spell a ``3``,
and a guard that punished that would push the author back to the literal.

``test_the_guards_themselves_can_fail`` is a negative control on all four tools. Without
it every assertion in this file could be vacuously true -- an introspection walker that
silently returned nothing would make the whole file green and guard nothing.
"""
from __future__ import annotations

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
from facts.domains import ActivationSignal, ActivationSignals, active_field_allowlist
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
#: `60` J-1 widened FIELD_SCOPES from seven members to twenty-one, so the seven this
#: file names are taken from the front of the tuple rather than unpacking all of it.
#: They are still a prefix, in the SPEC's order -- `facts.vocabulary` says so and
#: `tests/p6/test_p6_vocabulary_adoption.py` asserts it.
UNIVERSAL, ACADEMIC, COLLEGE_APPLICATIONS, RESEARCH, FINANCE, PHOTOS, CODE = \
    FIELD_SCOPES[:7]

#: The file layout the plan declares. A `catalogues.py` appearing here is how catalogue 01
#: would arrive as a module-level constant while satisfying the letter of every other
#: guard in this file, so the module set itself is asserted.
DECLARED_MODULES = frozenset({
    "authorship", "budgets", "cache", "dates", "direct", "discount", "domains",
    "evidence", "facets", "families", "fields", "file_facts", "learning", "llm_seam",
    "photo_event", "plan_versions", "read_surface", "resolver", "rules", "schema",
    "session", "states", "stage_output", "supersede", "unresolved", "usable", "values",
    "vocabulary",
})

#: Every module-level COLLECTION P6 publishes, with the task that owns it. A plain string
#: constant needs no entry -- a field key is not a catalogue. A collection does, because a
#: gazetteer, a producer-string list, a zone-weight map and a regex catalogue are all
#: collections, and the only way to tell one from a closed vocabulary is to have written
#: the closed vocabularies down. A name missing from this set is a RED TEST, and the fix
#: is a line here with the task that justifies it -- never a widening of the rule.
#:
#: A leading underscore does NOT exempt: `module_constants` skips only `__dunder__`
#: names, so a private import alias still needs its line.
DECLARED_VOCABULARIES = frozenset({
    "AUTHORED_EVENT_TYPES",                                   # Task 1  S8.2's two names
    "STATES", "STRENGTH_ORDER",                               # Task 1  S3.13
    "FACTS_TABLES", "_TABLE_DDL",                             # Tasks 1, 19  schema.py
    "FIELD_SCOPES", "UNIVERSAL_FIELDS", "DOMAIN_FIELDS", "FIELD_ROWS",   # Task 2  S3.11
    "FIELDS_COLUMNS", "VALUE_KINDS", "ROLE_FIELDS",           # Task 2  the `fields` table
    "_UNIVERSAL_3_11", "_DOWNLOAD_SESSION", "_ROLES_3_8", "_ACADEMIC",   # Task 2  the
    "_COLLEGE_APPLICATIONS", "_RESEARCH", "_FINANCE", "_PHOTOS", "_CODE",  # authored rows
    "_CAREER", "_BUSINESS_OPERATIONS", "_CONSTRUCTION_PROPERTY",           # `60` S4 the
    "_ENGINEERING", "_MANUFACTURING", "_RESOURCE_OPERATIONS", "_LOGISTICS",  # eighteen
    "_HR", "_LAW_PRACTICE",                                                # minted rows
    "VALUE_ORIGINS", "_VALUE_ORIGINS",                        # Task 3  S3.12
    "FILE_FACTS_COLUMNS", "FORBIDDEN_COLUMN_SUBSTRINGS", "FACT_ORIGINS",  # Task 4 S3.1
    "UNRESOLVED_REASONS", "ATTEMPTED_PRODUCERS", "_ATTEMPTED_PRODUCERS",  # Task 5 B7
    "NOT_ABSTENTIONS", "UNRESOLVED_COLUMNS",                  # Task 5  the negative half
    "CACHE_KEY_PARTS", "_RECORD_TABLES",                      # Task 6  S3.4
    "SLOT_KINDS",                                             # Task 8  S3.5's slot kinds
    "DISCOUNT_OUTCOMES", "AUTHORSHIP_FIELDS",                 # Task 9  M4's three outcomes
    "ACADEMIC_CONTEXT_TERMS",                                 # Task 10 S3.5's five terms
    "REQUIRED_PATTERN_IDS",                                   # Task 12 S3.10's three ids
    "SCHEMA_IDS", "FIELD_LESS_SCHEMA_IDS",                    # Task 13 S3.11 + S3.15
    "VERSION_FAMILY_STATES",                                  # Task 14 S8.3
    "EVENT_INPUTS", "MEDIA_TYPES", "PHOTO_BANDS", "SCREENSHOT_BAND",      # Task 16 S2.6
    "FOUR_CHECKS", "CHECK_REASONS", "LLM_STATES",             # Task 17 S3.6
    "P6_CEILING_KEYS", "DEGRADATION_ORDER", "CEILING_GATED_STAGES",       # Task 20 S8.6
    "REASON_BY_BAR",                                          # Task 20 the two bars
    "ENVELOPE_FIELDS",                                        # Task 21 S8.5
    "POLARITIES",                                             # Task 22 S8.7
    "PLAN_VERSIONED", "SHARED_ACROSS_PLAN_VERSIONS",          # Task 23 S8.8
    "VALUE_RENDERINGS_COLUMNS",                               # Task 23 the owed seam
    "PROPOSAL_ELIGIBLE_STATES",                               # Task 24 S3.6
})

#: The ONLY module-level numbers in `facts`, by exact (module, binding). Every entry is a
#: finding reported to the task that owns it, never a licence to add another.
#:
#: `facts.file_facts._KEY_LENGTH` is `len("sha256:") + 64` -- the shape of a P4
#: observation key, which is `evidence_shape.canonical.sha256_of`'s rule and not P6's. It
#: is a private copy of an upstream format, NOT one of the quantities this guard exists
#: for (minimum score, minimum margin, positional weight, signal-tier weight, session
#: window, GPS radius, screen resolution, sensor aspect ratio, usable-fact threshold).
#: Making a digest length an injected keyword would be nonsense; importing P4's key
#: predicate would remove it. Owner: Task 4.
DECLARED_NUMBERS = frozenset({("facts.file_facts", "_KEY_LENGTH")})

#: Field-creating callables S3.12 forbids: "it should not invent new fields automatically".
FIELD_CREATORS = frozenset({"add_field", "create_field", "register_field", "define_field",
                            "new_field", "add_fields"})

#: A group handle, by exact parameter name. S4.3 and S4.1: the graph "does not
#: automatically copy those missing facts onto sparse files". `file_ids` is NOT here -- it
#: is an explicit set the caller passes, which is the opposite of a membership lookup --
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
    machinery. An imported constant still counts -- a copied gazetteer is still a
    gazetteer when it arrives through an import, which is why the exemption is by
    identity."""
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
    """Every literal the compiler kept for this module -- function bodies, comprehensions
    and nested definitions included. Bytecode, never source text: a comment cannot reach
    `co_consts`, and a docstring reaches it only as the whole docstring, so equality
    against a short token cannot be satisfied by prose.

    Tuple and frozenset constants are FLATTENED, and that is not decoration. The compiler
    folds `X = ("python-docx", "Skia/PDF")` into a single tuple constant, and its members
    never appear in `co_consts` on their own -- so a walker that only collected the tuple
    would miss a copied catalogue written the most natural way there is. Verified against
    this repo: `facts.vocabulary`'s scope tuple puts no member string in `co_consts` at
    all, while `facts.fields`, which passes each scope to a constructor, puts every one
    there."""
    loader = module.__loader__
    out, stack = set(), [loader.get_code(module.__name__)]
    while stack:
        current = stack.pop()
        for const in current.co_consts:
            if isinstance(const, types.CodeType):
                stack.append(const)
                continue
            pending = [const]
            while pending:
                item = pending.pop()
                if isinstance(item, (tuple, frozenset)):
                    pending.extend(item)
                try:
                    out.add(item)
                except TypeError:  # an unhashable nested constant; nothing to match
                    pass
    return out


def public_callables(module):
    """The functions this module DEFINES, with their parameter names. An imported
    callable belongs to the module that defined it and is checked there."""
    for name, member in vars(module).items():
        if name.startswith("_") or not callable(member):
            continue
        if getattr(member, "__module__", None) != module.__name__:
            continue
        try:
            parameters = set(inspect.signature(member).parameters)
        except (TypeError, ValueError):
            continue
        yield name, parameters


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

    The slice arm exists for exactly one reason and it is a good one: `facts.photo_event`
    reads S2.6's screenshot band as `SIGNAL_TIERS[-1:]` so it never has to spell a `3`.
    Punishing that would push the author back to the literal, which is the thing being
    guarded against."""
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


def offending_in(modules, predicate, upstream):
    """Every (module, binding, value) in `modules` matching `predicate`, minus re-exports."""
    found = []
    for module in modules:
        for name, binding in module_constants(module).items():
            if is_upstream(binding, upstream):
                continue
            for value in reachable(binding):
                if predicate(value):
                    found.append((module.__name__, name, repr(value)[:80]))
    return found


def offending(predicate, upstream):
    return offending_in(facts_modules(), predicate, upstream)


def _is_number(value):
    return isinstance(value, (int, float, complex)) and not isinstance(value, bool)


def _is_path_like(value):
    if isinstance(value, Path):
        return True
    if not isinstance(value, str):
        return False
    lowered = value.casefold()
    return ("planning/" in lowered or lowered.endswith(".json")
            or "deferred-catalogues" in lowered)


# ---------------------------------------------------- the guards can actually fail

def test_the_guards_themselves_can_fail(upstream, tmp_path, monkeypatch):
    """Negative control on all four tools, because a walker that silently saw nothing
    would make every other assertion in this file vacuously true.

    S11's FIXTURE_COVERAGE on this project was checked only for its key set and could not
    fail; that is the defect this test exists to not repeat. Each tool is handed a planted
    module that DOES contain the thing, and must report it."""
    planted = types.ModuleType("planted")
    planted.MINIMUM_SCORE = 0.62                      # a threshold
    planted.SESSION_WINDOW = (30, 60)                 # a window, nested in a tuple
    planted.TERM_PATTERN = re.compile(r"Spring \d{4}")
    planted.CATALOGUE = Path("planning/deferred-catalogues/01.json")
    planted.SCOPES = ("universal", "academic")        # an undeclared collection

    assert len(offending_in([planted], _is_number, upstream)) == 3
    assert len(offending_in([planted], lambda v: isinstance(v, re.Pattern), upstream)) == 1
    assert len(offending_in([planted], _is_path_like, upstream)) == 1
    assert [name for name in module_constants(planted)
            if name not in DECLARED_VOCABULARIES] == ["MINIMUM_SCORE", "SESSION_WINDOW",
                                                      "TERM_PATTERN", "CATALOGUE",
                                                      "SCOPES"]

    #: And the compiled-code tool sees a literal buried in a FUNCTION BODY, which is the
    #: only place a copied producer catalogue could hide from the namespace walk.
    source = tmp_path / "planted_code.py"
    source.write_text(
        'FOLDED = ("Skia/PDF", "Quartz PDFContext")\n'
        'def f(v):\n'
        '    return v == "python-docx"\n',
        encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))
    module = importlib.import_module("planted_code")
    try:
        constants = code_constants(module)
        assert "python-docx" in constants          # a literal in a function BODY
        assert "Skia/PDF" in constants             # a member of a FOLDED tuple constant
        assert "Quartz PDFContext" in constants
    finally:
        sys.modules.pop("planted_code", None)


# ------------------------------------------ no invented number, regex or catalogue

def test_no_threshold_weight_window_radius_or_count_exists_as_a_module_constant(upstream):
    """Every one of them is a NUMBER, so one predicate covers the lot: minimum score,
    minimum margin, positional weight, signal-tier weight, session window, GPS radius,
    screen resolution, sensor aspect ratio and the usable-fact threshold.

    Each is a Deferred row and each is injected with no default. `bool` is excluded
    because `destination_eligible` and `active` are flags, not quantities. The single
    entry in `DECLARED_NUMBERS` is a reported finding, not a licence."""
    found = offending(_is_number, upstream)
    assert {(module, name) for module, name, _ in found} <= DECLARED_NUMBERS


def test_no_regex_catalogue_exists_as_a_module_constant(upstream):
    """S3.10 forbids fuzzy date parsing and requires explicit patterns -- and
    `facts.dates` receives them as an injected `DatePatterns`, including the three the
    design names (`Spring 2025`, `AY 2024-25`, `Michaelmas Term 2024`). A compiled pattern
    sitting at module level in `facts` is that catalogue having moved in."""
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
    Deferred row (Task 9), owned by the catalogue and not by `facts`.

    Most of the 115 entries are `prefix` or `regex` and carry a `pattern` rather than a
    `match`; both keys are banned, so a copied regex SOURCE is caught even before it is
    compiled.

    Two match modes, and the split is the catalogue's own. A producer VALUE is compared
    casefolded, because 112 of the rows carry `case_sensitive: false`. A property LABEL is
    compared VERBATIM, because the catalogue says so in as many words: "P4 D7 stores 'the
    source format's own slot name, verbatim', so the label is the format's spelling, not a
    normalized one." That distinction is load-bearing rather than tidy -- `Producer` is a
    PDF info-dictionary slot and `producer` is this codebase's ordinary word for one of
    S8.6's three fact producers, and `facts.families` passes `producer=` as a keyword."""
    assert CATALOGUE_01.is_file(), CATALOGUE_01
    catalogue = json.loads(CATALOGUE_01.read_text(encoding="utf-8"))
    blocks = ("entries", "refused", "uncertain")
    values = {entry["match"].casefold()
              for block in blocks for entry in catalogue[block] if "match" in entry}
    verbatim = {entry["pattern"]
                for block in blocks for entry in catalogue[block] if "pattern" in entry}
    for value in catalogue["property_names"].values():
        if isinstance(value, list):
            verbatim.update(value)
    assert len(catalogue["entries"]) == 115
    assert len(values) + len(verbatim) >= 115
    assert values and verbatim

    found = []
    for module in facts_modules():
        for const in code_constants(module):
            if not isinstance(const, str):
                continue
            if const in verbatim or const.casefold() in values:
                found.append((module.__name__, const))
    assert found == []


def test_facts_names_no_file_and_holds_no_path(upstream):
    """P6 loads nothing from disk. A `Path`, or a string naming anything under
    `planning/`, is a catalogue arriving by another door."""
    assert offending(_is_path_like, upstream) == []


def test_facts_has_exactly_the_modules_the_plan_declares():
    """The file layout is a contract, asserted as an EQUALITY in both directions.

    A `catalogues.py` is the one new module that would pass every other guard in this file
    on the day it was added, and the missing-module half is what catches a task whose
    single source file never landed -- `read_surface.py` was absent from `src/facts/` when
    this guard was first run and arrived while it was being written."""
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
    the rest of the suite imported -- asking the live interpreter what P6 imports would
    answer a different question and always answer "everything"."""
    baseline = _run(BASELINE)
    after = _run(PROBE)
    delta = {name: path for name, path in after.items() if name not in baseline}
    #: The probe must actually have imported P6, or every guard below is vacuous.
    assert "facts" in delta and any(name.startswith("facts.") for name in delta)
    return delta


def test_nothing_in_facts_imports_planning_domains(import_delta):
    """`planning/domains/` is a RESEARCH ARTIFACT -- a menu someone may one day draw from
    entry by entry, with a decision each time. It is not this catalogue's source and
    `facts` must never import it.

    `planning/domains/check.py` is importable, so this is a live possibility rather than a
    theoretical one."""
    planning = str(REPO / "planning")
    leaked = {name: path for name, path in import_delta.items()
              if path and path.startswith(planning)}
    assert leaked == {}


def test_facts_imports_no_grouping_tree_placement_or_model_module(import_delta):
    """P9, P10, P11 and P8 do not exist, and the absence is the contract (S4.1, S4.3,
    S3.3). Stated as an allowlist rather than a blocklist so it still holds on the day
    they are built: the only first-party packages `facts` may reach are these five."""
    allowed = {"facts", "database_agent", "evidence_shape", "eval_harness", "extractors"}
    source_root = str(REPO / "src")
    reached = {name.split(".")[0] for name, path in import_delta.items()
               if path and path.startswith(source_root)}
    assert reached <= allowed
    for forbidden in ("readers", "orchestrator", "scan_agent", "grouping", "tree",
                      "placement", "llm", "model", "privacy"):
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


def test_no_module_branches_on_source_type_or_extractor_name(upstream):
    """S2.8: P6 resolves a fixture carrying an unrecognised `source_type` with no new
    code. A per-format branch is how that stops being true, and P6 requires no per-format
    knowledge and must not acquire any.

    The value half carries the same identity exemption as every other guard here: P4's own
    `ANALYSIS_TIERS` and `ZONES` share the members `filesystem` and `ocr` with
    `SOURCE_TYPES`, and eight `facts` modules re-export one or both. A re-export of P4's
    tuple is not P6 naming a source type; a hand-typed copy of one is, and still fails."""
    for module in facts_modules():
        for name, parameters in public_callables(module):
            assert "source_type" not in parameters, f"{module.__name__}.{name}"
            assert "extractor_name" not in parameters, f"{module.__name__}.{name}"

    source_types = {value.casefold() for value in SOURCE_TYPES}
    named = offending(
        lambda value: isinstance(value, str) and value.casefold() in source_types,
        upstream)
    assert named == []


def test_no_p4_read_is_consumed_in_p4s_order(monkeypatch):
    """P4's reads are `ORDER BY rowid` -- insertion order, which is stable within one
    database and is NOT a property of the corpus.

    `facts.evidence.observations_for_version` is the one chokepoint every P6 read goes
    through (it is also the per-content-hash filter P4 does not publish), so the guard
    hands it P4's answer in both orders and requires the same result. Behavioural, not
    structural: the question is whether the ORDER changes the RESULT, and only running it
    can answer that. The P4 read is replaced outright, so no database rows are needed."""
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
    #: The three raw values differ, so a walker that returned the input untouched would
    #: pass the equality above for the wrong reason.
    assert len({one.raw_value for one in straight}) == 3


# ================================================================================
# The open questions. One named test each. None of them is answered here.
# ================================================================================

def test_oq3_purpose_is_still_one_row_and_p6_has_not_promoted_it(p6_conn):
    """OQ3, OPEN: "Is `purpose` a universal field or an Applications-domain field? S3.9
    requires it to be 'first-class'; S3.11's universal list omits it and places it only
    under College applications."

    P6 ships S3.11's placement and answers nothing. What it must NOT do is answer the
    question by creating BOTH -- a universal `purpose` and a domain `purpose` would be two
    columns for one concept, which is the tie-break rule's exact prohibition: one stored
    key per concept, every other word an alias. Settling OQ3 changes one row's `scope` and
    nothing else, because no module branches on where it lives."""
    rows = [row for row in FIELD_ROWS if row.field_key == "purpose"]
    assert len(rows) == 1
    assert rows[0].scope == COLLEGE_APPLICATIONS
    assert "purpose" not in UNIVERSAL_FIELDS
    assert get_field(p6_conn, "purpose")["scope"] == COLLEGE_APPLICATIONS


def test_oq5_finance_has_a_schema_and_p6_neither_activates_nor_suppresses_it(p6_conn):
    """OQ5, OPEN [seam with P7]: "Finance has a fact schema in S3.11 but is a safety domain
    in S3.15 ... Does the Finance fact schema activate at launch, or does
    detection-and-protection precede any field extraction?"

    P6 holds the schema and decides nothing. Asserted behaviourally, which is the only way
    to tell "holds a schema" from "takes a side": with NO injected signal Finance's fields
    are absent from the allowlist, and with one injected signal they are all present. P6
    supplies neither signal.

    The name half stays too, and it is stated by identity rather than by a module
    allowlist. Three modules AUTHOR the string: `facts.vocabulary` (`FIELD_SCOPES`),
    `facts.fields` (the `_FINANCE` row group) and `facts.domains` (`SCHEMA_IDS`, which is
    S3.11's six plus S3.15's four). Every other module reaches it only by re-exporting one
    of those very objects -- `facts.read_surface.FIELD_SCOPES` IS
    `facts.fields.FIELD_SCOPES` -- and a re-export is not P6 taking a side. A fourth module
    that hand-typed "finance" into a tuple of its own still fails, because a copy is a
    different object."""
    assert FINANCE in FIELD_SCOPES
    assert DOMAIN_FIELDS[FINANCE]
    assert fields_in_scope(p6_conn, FINANCE)

    finance_keys = {row["field_key"] for row in fields_in_scope(p6_conn, FINANCE)}
    silent = active_field_allowlist(p6_conn, file_id="file-1", content_hash="0" * 64,
                                    activation_signals=ActivationSignals(()))
    assert finance_keys & set(silent) == set()

    activated = active_field_allowlist(
        p6_conn, file_id="file-1", content_hash="0" * 64,
        activation_signals=ActivationSignals(
            (ActivationSignal(FINANCE, lambda established: True),)))
    assert finance_keys <= set(activated)

    import facts.domains as domains_module
    import facts.fields as fields_module
    import facts.vocabulary as vocabulary_module
    assert domains_module.FIELD_SCOPES is fields_module.FIELD_SCOPES
    assert domains_module.DOMAIN_FIELDS is fields_module.DOMAIN_FIELDS
    assert vocabulary_module.FIELD_SCOPES is fields_module.FIELD_SCOPES

    #: The catalogue objects themselves. Reaching FINANCE through one of these is a
    #: re-export; reaching it through anything else is a second home for the name.
    catalogue_objects = (vocabulary_module.FIELD_SCOPES, fields_module.FIELD_ROWS,
                         fields_module.DOMAIN_FIELDS, fields_module.UNIVERSAL_FIELDS)
    catalogue_ids = frozenset(id(one) for one in catalogue_objects)

    authoring = set()
    reexporting = set()
    for module in facts_modules():
        for name, binding in module_constants(module).items():
            if not any(isinstance(value, str) and value == FINANCE
                       for value in reachable(binding)):
                continue
            if id(binding) in catalogue_ids:
                reexporting.add(module.__name__)
            else:
                authoring.add(f"{module.__name__}.{name}")

    assert authoring == {"facts.fields._FINANCE", "facts.domains.SCHEMA_IDS"}
    assert reexporting, "the re-export arm never fired; the identity test proves nothing"

    #: And the scope tuple itself has one home. Every module binding `FIELD_SCOPES` binds
    #: the SAME object, so there is nothing for a second spelling of Finance to live in.
    bound = [module.__name__ for module in facts_modules()
             if "FIELD_SCOPES" in vars(module)]
    assert len(bound) > 1
    assert all(vars(importlib.import_module(name))["FIELD_SCOPES"]
               is vocabulary_module.FIELD_SCOPES for name in bound)


def test_oq6_multiplicity_is_a_column_with_no_answer_in_it(p6_conn):
    """OQ6, OPEN: "May one (file, field) hold several simultaneously active values, and if
    so how does the S3.7 margin rule apply when more than one candidate is correct?"

    The column exists so the answer has somewhere to go. Every row's value is `None`, so
    no field has been quietly given a multiplicity, and S3.7's margin rule stays as
    `facts.facets` wrote it: two candidates within the margin fill nothing."""
    assert "multiplicity" in {field.name for field in dataclasses.fields(FieldRow)}
    assert {row.multiplicity for row in FIELD_ROWS} == {None}
    seen = 0
    for scope in FIELD_SCOPES:
        for row in fields_in_scope(p6_conn, scope):
            assert row["multiplicity"] is None
            seen += 1
    assert seen == len(FIELD_ROWS)


def test_oq8_no_producer_can_create_a_field_at_run_time(p6_conn):
    """OQ8, OPEN [seam with P10]: "Does user approval of a custom template create `fields`
    rows, and at what scope -- corpus-wide or plan-version-local?"

    Until that is answered, nothing creates one. S3.12: the system "may create new values
    when it sees a new course, project, company, university, or event, but it should not
    invent new fields automatically", and S3.5: "The LLM is not allowed to invent a new
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
    assert before
    with pytest.raises(FieldNotInCatalogue):
        ensure_value(p6_conn, field_key="admissions_packet", canonical_value="Round 1",
                     first_evidence_ref="sha256:" + "0" * 64, origin=VALUE_ORIGINS[0])
    assert catalogue() == before


def test_oq9_no_write_path_takes_a_group(import_delta):
    """OQ9, OPEN [seam]: "After the user accepts the group, does that purpose become a fact
    on non-anchor members, or does it remain membership only?"

    Until it is settled, P6 writes nothing group-derived -- S4.1: the graph "does not
    automatically copy those missing facts onto sparse files"; S3.9: a session is "not a
    basis for automatic semantic propagation". Enforced twice: no grouping module is
    imported at all, and no callable anywhere in `facts` will accept a group handle."""
    assert "grouping" not in {name.split(".")[0] for name in import_delta}

    for module in facts_modules():
        for name, parameters in public_callables(module):
            assert not parameters & GROUP_PARAMETERS, f"{module.__name__}.{name}"


def test_oq10_two_equal_rank_contradicting_facts_are_never_ranked_by_p6():
    """OQ10, OPEN: "S3.13 orders the six states but does not define the comparison for two
    equal-rank contradicting facts ... Reject both, surface both as competing candidates,
    or defer to the internal score?"

    P6 refuses to choose and writes an `unresolved` row instead, which is why the refusal
    is inspectable (S8.5: "Did it abstain when evidence was absent?"). Two halves: a state
    never outranks itself, so the tie is real rather than resolved by an accident of
    comparison; and no constant anywhere encodes a tie-break policy."""
    assert len(STRENGTH_ORDER) == 5
    for state in STRENGTH_ORDER:
        assert is_stronger(state, state) is False

    #: S3.13 makes `rejected` an EXCLUSION, not a rank, so Task 1 gives it no strength and
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
    """OQ4, CLOSED -- D6, ratified 2026-08-21. One field, and its key is `subject`.

    S3.1, S3.2 and S3.12 all say `subject`; only S3.11's Academic row says `course`, and
    that is the design's PROSE for the same field. A field key is a join handle, so two
    spellings are two columns -- the word `course` survives inside quotations and nowhere
    else.

    This guard is INVERTED on purpose. A test asserting OQ4 is open would pass every day
    up to the one this plan is executed and fail on that day, which is the failure mode
    that made the inversion worth writing down."""
    keys = {row.field_key for row in FIELD_ROWS}
    assert "subject" in keys
    assert "course" not in keys
    assert get_field(p6_conn, "subject")["scope"] == ACADEMIC
    with pytest.raises(FieldNotInCatalogue):
        get_field(p6_conn, "course")

    #: The value lands under `subject` and under no other key.
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
    """OQ11, CLOSED -- D2, ratified 2026-08-21, on the question it asked: WHICH record is
    authoritative. The answer is P7's.

    P7's `ClassificationRecord`, keyed `(file_id, content_hash)`, is authoritative;
    `files.sensitivity_state` is its PROJECTION, written through P1's published
    `set_sensitivity_state`; and `Unreadable or unclassified` is a GATE OUTCOME, not a file
    fact. P6 was the part that made the name count three (S3.11's universal fact, S8.2's
    file-record state, S8.4's handling class). After D2 it makes it one: P6 publishes no
    record, no table, no vocabulary and no writer.

    INVERTED on purpose, for the same reason as OQ4."""
    tables = {row[0] for row in p6_conn.execute(
        "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')")}
    assert tables, "p6_conn built no tables; every assertion below would be vacuous"
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


def test_the_sensitivity_field_row_does_not_exist_and_p7s_contract_in_still_disagrees(p6_conn):
    """OQ11's RESIDUE. D7 rules that P6 creates no `sensitivity_status` field row and P7's
    record is the sole home; NEEDS-JOSEPH C5 is the SPEC-level contradiction that ruling
    leaves standing, and this test settles none of it.

    The evidence points three ways:

      * S3.12 names it in the design's own field list -- "subject, purpose, target
        university, project, event, or sensitivity" -- and S3.11 spells it
        `sensitivity status`;
      * P7's SPEC, Contract-in, says in bold "P6 must accept `sensitivity` as a
        first-class universal field" (S3.11) rather than a domain-scoped one;
      * round 1's F-2 found the field HAS NO PRODUCER -- nothing in P6 would ever write
        it, so it would ship as a permanently empty column a reader could mistake for
        "not sensitive".

    D7 answers the third and the standing instruction is "Create no such row." So this
    test pins TODAY'S state under BOTH spellings and SETTLES NOTHING about P7's
    Contract-in demand, which is Joseph's. If the row ever arrives, this test is where the
    decision lands: flipping it is one line here plus one row in the catalogue, and nothing
    else in P6 branches on the answer -- which is what "held open" has to mean to be worth
    anything."""
    keys = {row.field_key for row in FIELD_ROWS}
    assert "subject" in keys, "the catalogue is loaded; the absences below are real"
    assert "sensitivity" not in keys
    assert "sensitivity_status" not in keys
    assert "sensitivity" not in UNIVERSAL_FIELDS
    for field_key in ("sensitivity", "sensitivity_status"):
        with pytest.raises(FieldNotInCatalogue):
            get_field(p6_conn, field_key)
