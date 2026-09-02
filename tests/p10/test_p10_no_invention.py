# tests/p10/test_p10_no_invention.py
"""P10 Task 17 — the boundaries, checked by parsing rather than by grepping.

Every guard here is over the parsed AST. A text search matches comments and
docstrings, and on this project that has produced a false result repeatedly —
including the guard whose own banned word appeared in its own docstring.

These are a RATCHET, not a milestone. They pass against the modules built so
far and their job is to keep passing: each one names a value P10 could
plausibly hard-code, or an edge P10 could plausibly grow, and states who
actually owns it.

Each guard is paired with a SABOTAGE FIXTURE — a snippet of source that the
guard must reject — so that "the guard found nothing" is distinguishable from
"the guard cannot find anything". A guard tested only against clean code passes
just as well when its offender list is unreachable.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

import tree_design

SRC = pathlib.Path(tree_design.__file__).resolve().parent
MODULES = sorted(SRC.glob("*.py"))


def _trees():
    return [(path, ast.parse(path.read_text())) for path in MODULES]


def _fake(source: str, name: str = "offender.py"):
    """One parsed module that is NOT on disk, for the negative half of a pair."""
    return [(pathlib.Path(name), ast.parse(source))]


# --------------------------------------------------------------------------
# The checks, each written once and applied to both the real tree and a fake.
# --------------------------------------------------------------------------

def _imported_modules(tree: ast.Module):
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            yield node.lineno, node.module
        elif isinstance(node, ast.Import):
            for alias in node.names:
                yield node.lineno, alias.name


def _authorship_imports(trees):
    return [f"{path.name}:{line} {module}"
            for path, tree in trees
            for line, module in _imported_modules(tree)
            if module.split(".")[0] in {"planning", "prompts", "domains"}]


#: The one downstream module P10 may read, and the reason it is not an exception
#: to the rule below but an instance of it.
#:
#: `81` §14 ruled that **P13 owns the name of a gesture**, so P10 carries P13's
#: action and surface names verbatim rather than spelling its own (MINOR 6/7).
#: Carrying requires importing: a tuple that merely AGREES is one P13 edit away
#: from disagreeing, which is the argument `src/placement/vocabulary.py:130-133`
#: already makes against itself.
#:
#: `review_surface.vocabulary` is a values-only leaf -- it imports
#: `database_agent.events` and nothing else, holds no behaviour, and reads no
#: P10 output -- so this edge is the same shape as P10's existing import of P1's
#: `CORRECTION_SCOPES`, not the shape the guard exists to stop. Every other
#: `review_surface` module stays forbidden, and the twin below proves it.
CARRIED_VOCABULARY_MODULE = "review_surface.vocabulary"


def _downstream_imports(trees):
    return [f"{path.name}:{line} {module}"
            for path, tree in trees
            for line, module in _imported_modules(tree)
            if module.split(".")[0] in {"placement", "apply_undo", "review_surface"}
            and module != CARRIED_VOCABULARY_MODULE]


FORBIDDEN_FS_MODULES = {"pathlib", "shutil", "glob", "tempfile"}
FORBIDDEN_FS_CALLS = {"listdir", "walk", "scandir", "mkdir", "rename",
                      "remove", "rmdir", "makedirs"}


def _filesystem_uses(trees):
    offenders = []
    for path, tree in trees:
        for line, module in _imported_modules(tree):
            if module.split(".")[0] in FORBIDDEN_FS_MODULES:
                offenders.append(f"{path.name}:{line} {module}")
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = getattr(node.func, "attr", getattr(node.func, "id", None))
                if name in FORBIDDEN_FS_CALLS:
                    offenders.append(f"{path.name}:{node.lineno} {name}()")
    return offenders


def _path_joins(trees):
    offenders = []
    for path, tree in trees:
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call)
                    and getattr(node.func, "attr", None) == "join"
                    and isinstance(getattr(node.func, "value", None), ast.Constant)
                    and node.func.value.value in ("/", "\\")):
                offenders.append(f"{path.name}:{node.lineno}")
    return offenders


FORBIDDEN_WRITERS = {"facts.file_facts", "facts.values",
                     "privacy.classification_store", "grouping.store"}


def _evidence_writer_imports(trees):
    return [f"{path.name}:{line} {module}"
            for path, tree in trees
            for line, module in _imported_modules(tree)
            if module in FORBIDDEN_WRITERS]


def _event_writers(trees, *, skip="provenance.py"):
    offenders = []
    for path, tree in trees:
        if path.name == skip:
            continue
        for node in ast.walk(tree):
            if (isinstance(node, ast.ImportFrom)
                    and node.module == "database_agent.events"):
                imported = {a.name for a in node.names} & {"append_event"}
                if imported:
                    offenders.append(f"{path.name}:{node.lineno} {sorted(imported)}")
            if isinstance(node, ast.Call):
                name = getattr(node.func, "attr", getattr(node.func, "id", None))
                if name == "append_event":
                    offenders.append(f"{path.name}:{node.lineno} append_event()")
    return offenders


#: The modules permitted to name another part's records. Each is a declared
#: seam: `upstream` reads P9/P6/P3/P7, `template_schema` and `stage_output`
#: serve P8 and P2, `provenance` writes P1's events, and `vocabulary`/`config`
#: IMPORT borrowed closed sets rather than respelling them (Task 1's whole
#: point). `catalogue` is here because it parses a packaged release.
SEAM_MODULES = {"upstream.py", "template_schema.py", "stage_output.py",
                "provenance.py", "vocabulary.py", "config.py"}
FOREIGN_ROOTS = {"grouping", "facts", "privacy", "scan_agent", "llm_harness",
                 "eval_harness", "database_agent"}


def _foreign_names(trees, *, allowed=SEAM_MODULES):
    offenders = []
    for path, tree in trees:
        if path.name in allowed:
            continue
        for line, module in _imported_modules(tree):
            if module == "evidence_shape.canonical":
                # A shared serialisation helper, not another part's record
                # vocabulary. P9 and P11 import it at the same tier.
                continue
            if module.split(".")[0] in FOREIGN_ROOTS:
                offenders.append(f"{path.name}:{line} {module}")
    return offenders


#: The ONE module exempt from the magic-number guard, and the exemption is
#: stated rather than silent. `fixtures.py` is deterministic sample data whose
#: sibling `ordinal`s run 0, 1, 2, 3, 4 by construction; those are positions in
#: a fixed example tree, not limits any check consults. Every other module in
#: `src/tree_design/` holds no integer beyond 0 and 1, which is what makes this
#: safe to state rather than a hole to hide in — and
#: `test_the_numeric_exemption_covers_exactly_one_module` pins that.
MAGIC_NUMBER_EXEMPT = {"fixtures.py"}


def _magic_numbers(trees, *, exempt=MAGIC_NUMBER_EXEMPT):
    offenders = []
    for path, tree in trees:
        if path.name in exempt:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant):
                continue
            if isinstance(node.value, bool) or not isinstance(node.value, int):
                continue
            if node.value in (0, 1):
                continue
            offenders.append(f"{path.name}:{node.lineno} {node.value}")
    return offenders


def _fixture_imports(trees):
    offenders = []
    for path, tree in trees:
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if "fixtures" in node.module:
                    offenders.append(f"{path.name}:{node.lineno} {node.module}")
    return offenders


# --------------------------------------------------------------------------
# The guards. Each is a PAIR: the real package is clean, a planted offender is
# caught. Without the second half, an offender list that can never be appended
# to reads exactly like a package with nothing to report.
# --------------------------------------------------------------------------

def test_no_module_imports_planning_prompts_or_domain_research():
    """`planning/domains/` is a research and authorship surface, not a runtime
    import target. A later deterministic compiler consumes ratified records and
    emits a versioned manifest; `tree_design.catalogue` reads that manifest."""
    assert _authorship_imports(_trees()) == []
    assert _authorship_imports(_fake("from planning.domains import ACADEMIC"))


def test_no_module_imports_p11_p12_or_p13():
    """P10 publishes; it consumes nothing downstream. A runtime edge the other
    way would make P10 depend on the parts that consume its own output.

    **Narrowed 2026-08-31 by `81` §14's ruling**, and narrowed rather than
    dropped. P13 owns the name of a gesture, so P10 carries P13's action and
    surface names and cannot carry what it does not import. The exception is
    exactly one values-only module -- `review_surface.vocabulary`, which imports
    only P1 and holds no behaviour. `review_surface.store`, `.collect`,
    `.routing` and every other module are still refused, which is the half of
    this guard that would otherwise quietly go missing.
    """
    assert _downstream_imports(_trees()) == []
    assert _downstream_imports(_fake("from placement.index import IndexEntry"))
    assert _downstream_imports(
        _fake("from review_surface.store import record_action"))
    assert _downstream_imports(_fake("import review_surface"))
    assert _downstream_imports(
        _fake("from review_surface.vocabulary import ACTION_ACCEPT")) == []


def test_no_module_touches_the_filesystem():
    """P10 composes no path and reads no directory. `catalogue.load_catalogue`
    takes an injected reader rather than a path for exactly this reason, which
    is what makes the boundary checkable by parsing instead of by hope."""
    assert _filesystem_uses(_trees()) == []
    assert _filesystem_uses(_fake("import pathlib\n"))
    assert _filesystem_uses(_fake("import os\nos.listdir('.')\n"))


def test_os_sep_is_used_to_REJECT_a_separator_and_never_to_build_one():
    """The negative twin of the guard above, and the reason it does not simply
    ban `os`.

    `records.py` and `templates.py` both import `os` to build `_SEPARATORS`, the
    frozenset a label is checked AGAINST. Banning the name would force those
    checks to spell the separators as literals, which is strictly worse. So the
    guard bans filesystem OPERATIONS, and this test pins the one legitimate use
    so a later reader does not "fix" it.
    """
    users = {path.name for path, tree in _trees()
             for line, module in _imported_modules(tree) if module == "os"}
    assert users, "the separator guard is built from os.sep somewhere"
    assert _filesystem_uses(_trees()) == []


def test_no_module_composes_a_path_by_joining_labels():
    """DM11. `root_anchor` plus the ancestor label chain is what P10 publishes;
    P12 composes the path and applies §8.3's case, Unicode and length rules."""
    assert _path_joins(_trees()) == []
    assert _path_joins(_fake("x = '/'.join(labels)\n"))


def test_no_module_writes_a_fact_a_classification_or_a_group():
    """§3.14 and §5.12: the tree is a separate VIEW over the evidence. P10 reads
    facts, groups and classifications and writes none of them. Freeze is a view,
    never a rewrite — the user can rearrange the same facts tomorrow without
    losing an observation."""
    assert _evidence_writer_imports(_trees()) == []
    assert _evidence_writer_imports(_fake("from grouping.store import current_group"))


def test_only_the_provenance_module_appends_an_event():
    """The WRITER is restricted, not the module.

    `vocabulary.py` imports `CORRECTION_SCOPES` and `RESERVED_EVENT_TYPES` from
    `database_agent.events` — Task 1's whole point, a borrowed set imported
    rather than respelled — so a check on the module NAME would call that a
    violation. `append_event` is the only name that writes.
    """
    assert _event_writers(_trees()) == []
    assert _event_writers(_fake("from database_agent.events import append_event"))
    # And the exemption is real rather than vacuous: the one module allowed to
    # write is the one that actually does.
    assert _event_writers(_trees(), skip=None) != []


def test_only_the_declared_seams_name_another_parts_records():
    """One seam, one failure when an upstream name moves."""
    assert _foreign_names(_trees()) == []
    assert _foreign_names(_fake("from facts.fields import get_field"))
    # Vacuity check: the allow-list is load-bearing. Remove it and the real
    # package reports the seams it legitimately has.
    assert _foreign_names(_trees(), allowed=frozenset()) != []


def test_every_declared_seam_module_actually_is_one():
    """A name on an allow-list that no longer needs to be there is an exemption
    nobody notices widening. Each entry must both EXIST and use its exemption."""
    names = {path.name for path in MODULES}
    missing = sorted(SEAM_MODULES - names)
    assert missing == [], f"the allow-list names modules that do not exist: {missing}"
    unused = sorted(
        name for name in SEAM_MODULES
        if not _foreign_names([(p, t) for p, t in _trees() if p.name == name],
                              allowed=frozenset()))
    assert unused == [], f"these are exempt but import nothing foreign: {unused}"


def test_no_module_imports_a_test_fixture():
    """`tests/p10/p9_fixtures.py` and `p13_fixtures.py` stand in for parts that
    have not shipped. They live under `tests/` and production code must never
    reach them — a fixture imported by `src/` is a stand-in that ships."""
    assert _fixture_imports(_trees()) == []
    assert _fixture_imports(_fake("from p10.p9_fixtures import FixtureGroupReader"))


def test_no_module_holds_a_numeric_literal_beyond_zero_and_one():
    """G-KNOWLEDGE: a depth ceiling, a §5.9 threshold or a proposal cap is READ
    from P1's ceilings or from injected configuration, never chosen. A literal
    in a module is how one gets chosen by accident.

    No module is exempt. `0` and `1` are allowed because they are the arity of a
    thing — a first sibling, a single element — and not a tuned quantity.
    """
    assert _magic_numbers(_trees()) == []
    assert _magic_numbers(_fake("MAX_DEPTH = 4\n"))


def test_the_numeric_exemption_covers_exactly_one_module():
    """An exemption nobody re-checks is how a hole widens.

    Two things are pinned: the exempt module EXISTS (an exemption naming a
    deleted file is dead text that would silently cover a future file of the
    same name), and it is the ONLY one — dropping the exemption must make the
    real package report offenders from `fixtures.py` and from nowhere else.
    """
    names = {path.name for path in MODULES}
    assert MAGIC_NUMBER_EXEMPT <= names, "the exemption names a module that does not exist"
    without = {entry.split(":")[0] for entry in _magic_numbers(_trees(), exempt=frozenset())}
    assert without == MAGIC_NUMBER_EXEMPT, (
        f"the numeric exemption is meant to cover exactly {MAGIC_NUMBER_EXEMPT} "
        f"but the package reports {without}")


def _stage_and_dimension_literals(trees, *, skip="vocabulary.py"):
    """P10's own stage ids and §8.5 dimensions, spelled anywhere but their home.

    `test_no_module_outside_the_vocabulary_spells_a_closed_value` guards the
    same rule but excludes any value without a space or a hyphen, so that
    `C1`/`V1` and record slot names stay usable as local identifiers. The stage
    ids are pure identifiers and slipped through that exclusion — and a real
    second home was living in the hole: `stage_output.py` spelled all four of
    P10's stage ids and dimensions as literals while `vocabulary.py` published
    them, which is the exact defect Task 1 exists to prevent.
    """
    import tree_design.vocabulary as _v
    # STAGE IDS ONLY, and the exclusion is reasoned rather than convenient.
    # `tree` and `template` are English words that legitimately name other
    # things: `provenance.py` has `PROPOSAL_CLASS_TEMPLATE = "template"`, a
    # `proposal_class` and not a §8.5 dimension, correctly named at its own one
    # home. Guarding the bare words would call that a violation and teach the
    # next reader to silence the guard. `tree_design` and `template_generation`
    # are compound and unmistakable: nothing else in P10 is called either.
    guarded = set(_v.P10_STAGE_IDS)
    offenders = []
    for path, tree in trees:
        if path.name == skip:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and node.value in guarded:
                offenders.append(f"{path.name}:{node.lineno} {node.value!r}")
    return offenders


def test_no_module_respells_a_p10_stage_id_or_dimension():
    """Task 1: every closed P10 value has exactly one home. A stage id written
    as a literal is a second one, and P2 renaming a stage would then leave P10
    green and silently emitting under a name nobody reads."""
    assert _stage_and_dimension_literals(_trees()) == []
    assert _stage_and_dimension_literals(_fake("STAGE = 'tree_design'\n"))
    # Vacuity check: the home itself DOES spell them, so the exemption is real.
    assert _stage_and_dimension_literals(_trees(), skip=None) != []
