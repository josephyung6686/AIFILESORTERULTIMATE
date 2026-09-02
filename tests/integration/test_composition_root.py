"""The composition root's database is complete with respect to the source.

`src/cli.py` is the only place a person's run installs its schema, and it is the
one place no part's own test suite looks: every part builds its tables in its own
fixture, so a table that ships in `src/` and is created by nothing outside a test
is invisible to all 5,386 of them at once. This module is that blind spot's test.

It is the database-side twin of `tests/p11/test_p11_groups.py`'s
`_placement_sources_calling`, whose docstring already names the pattern -- "the
four concepts this codebase shipped fully-tested and connected to nothing all had
references" -- and of the strict xfail standing on it in
`tests/p11/test_p11_versions.py:311`, which counts the shape at seven. That
instrument is scoped to `src/placement/`; this one is scoped to the whole tree,
because every instance found since was somewhere else.

There are two censuses here. The first asks whether the run creates every table the
source declares. The second asks the same question of the CODE: whether every public
mechanism `src/` ships is reachable from `cli.main` at all.

LIMITATION of the table census, stated rather than hidden: `_tables_declared_in_source`
reads literal DDL. A table whose name arrives through an f-string placeholder is not
counted, so this test can under-report and never over-report. A missing table it names
is always real.

LIMITATIONS of the reachability census, the same way:

- **It resolves names, not namespaces.** `_definitions_by_name` lets a bare `store`
  reach every `store` in the tree. That over-STATES reachability on purpose, which is
  the direction that makes the verdict safe: a symbol this census calls unreachable is
  genuinely unreachable, and one it calls reachable may not be.
- **It reads source, so a symbol reached only through a string cannot be seen.** A
  `getattr(module, name)` over a computed name, or a registry keyed by strings, would
  be reported dead wrongly. Checked before relying on it: all 102 `getattr` calls in
  `src/` take a literal field name off a record, and none reaches a module symbol.
- **Module-level constants are outside the population.** They are indexed, because
  `STEPS = (first, second)` is often what reaches a mechanism, but a vocabulary term
  nothing reads is a lesser defect than a mechanism nothing runs, and every instance
  this codebase has actually shipped was a function or a whole module.
"""
from __future__ import annotations

import ast
import functools
import re
import sys
from pathlib import Path

import pytest

from database_agent.db import open_database

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402

_SRC = Path(__file__).resolve().parents[2] / "src"
_DECLARATION = re.compile(r'CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+"?([a-z_]+)"?')


def _tables_declared_in_source() -> set[str]:
    """Every table the shipped source declares, by reading its own DDL."""
    return {match.group(1)
            for path in sorted(_SRC.rglob("*.py"))
            for match in _DECLARATION.finditer(path.read_text(encoding="utf-8"))}


def _tables_present(conn) -> set[str]:
    return {row["name"] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}


#: Tables their owning writer creates on demand instead of at bootstrap, each with the
#: reason it may not join `_bootstrap`. A name earns a place here only by being PROVEN
#: created below -- an exemption nothing checks is how a census rots into a whitelist.
LAZY_TABLES: dict[str, str] = {
    "llm_cd_plan_identity":
        "created per C/D verdict write by `_ensure_identity_table` "
        "(`placement_validation.py:461`), which must run inside the caller's open "
        "transaction: `executescript` at bootstrap would commit the harness's "
        "transaction out from under it.",
}


def test_the_bootstrap_creates_every_table_the_source_declares(tmp_path: Path):
    """A part whose tables the run never creates fails at its first write.

    Not at import, not at start-up, and not in any test -- at the first write, in
    front of the person, after their disk has already been read.
    """
    conn = open_database(tmp_path / "agent.sqlite")
    cli._bootstrap(conn)
    missing = sorted(
        _tables_declared_in_source() - _tables_present(conn) - set(LAZY_TABLES))
    assert not missing, (
        "declared in src/ and created by nothing a person runs: " + ", ".join(missing))


def _sources_calling(function_name: str) -> set[str]:
    """Modules anywhere in `src/` that CALL `function_name`, by AST, not by grep.

    The whole-tree twin of `tests/p11/test_p11_groups.py`'s
    `_placement_sources_calling`, and deliberately the same method, including its
    rule: *a reference is not a call and an import is not a use*. Every mechanism
    found unreachable since that helper was written lives outside `src/placement/`,
    which is the only reason it was not caught by it.
    """
    callers = set()
    for path in sorted(_SRC.rglob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = (func.attr if isinstance(func, ast.Attribute)
                    else func.id if isinstance(func, ast.Name) else None)
            if name == function_name:
                callers.add(str(path.relative_to(_SRC)))
    return callers


def test_the_reachability_instrument_can_tell_a_caller_from_a_reference():
    """The falsifying twin for `_sources_calling`, and it is not a formality.

    `create_llm_schema` gained its first production caller in this same change, so
    it proves the instrument SEES a real call. `record_user_level_edit` is named in
    its own module's `__all__` and called by nothing, so it proves the instrument is
    not merely matching the name -- which a grep would, and which is how this gap
    stayed invisible.
    """
    assert "cli.py" in _sources_calling("create_llm_schema")
    assert not _sources_calling("record_user_level_edit")


def test_the_renaming_overlay_has_a_writer_somewhere_in_the_product():
    """`64` §1's rename is readable, appliable, durable -- and unreachable.

    `apply_user_level_edits` is wired into routing (`routing.py:506`) and the
    overlay's own writer refuses an edit nothing can apply, on the grounds that
    "the user would see their edit accepted and never honoured". Nothing calls the
    writer, and `routing.py:303` defaults `user_edits` to `()`, so the person
    cannot rename a level at all: the edit is not honoured because it cannot be
    made. Its owed caller is P13's review surface, which is unbuilt.

    `xfail(strict=True)`: it reports the gap today and turns the suite RED the day
    a writer appears, which forces the marker off.
    """
    assert _sources_calling("record_user_level_edit")


test_the_renaming_overlay_has_a_writer_somewhere_in_the_product = pytest.mark.xfail(
    strict=True,
    reason="P13's review surface is unbuilt; nothing calls record_user_level_edit, "
           "so a person cannot rename a level. XPASSes and fails the suite the "
           "moment a writer appears.",
)(test_the_renaming_overlay_has_a_writer_somewhere_in_the_product)


def test_the_question_that_asks_which_situation_a_branch_is_reaches_a_person():
    """§13's third consequence -- "resolve role ambiguity" -- is built at both ends
    and joined at neither.

    Found by walking the journey. `68` F6 is the case: a graduate student who also
    teaches has her whole disk filed as coursework, "including the material that is
    `academic.teaching`, a situation the shipped library now carries", because
    `--situation` takes ONE string for a whole corpus. `75` §2 names the fix and
    calls it consequence 3; `80` §1.4 (Option 5) says it is the mechanism that
    catches what a declared role structurally cannot -- "knowing both roles doesn't
    tell the system which one a specific ambiguous PDF belongs to; the in-context
    question does."

    Both halves exist. `triggers.question_for_situation` is a finished question --
    prompt, evidence context, the library's own situation names as options, each
    carrying `selects_situation`. `store.selected_situation` is its reader, scoped
    with no default for the reason the docstring gives. `registry.SITUATION_KIND`
    binds the two, so A1's guard -- every kind names the consequence that reads it
    -- passes while the whole kind is dark. **A registry entry is not a call site.**

    Compare the two kinds that DO reach a person: `question_for_nesting` and
    `tied_readings` are both called from `cli.py`, and `activated_schemas` and
    `gated_template` -- §13's other two live consequences -- are read there. This
    one is called by nothing and read by nothing, so a person is never asked which
    of their lives a branch belongs to, and could not be heard if they said.

    BOTH halves in one assertion on purpose. `questions/records.py:46` forbids
    shipping a consequence with no reader, so the ask and the reader land together
    or neither does; a marker that came off when half arrived would license exactly
    the split that rule exists to prevent.

    `xfail(strict=True)`: it turns the suite RED the day either half is wired,
    which forces this marker off and this comment with it.
    """
    assert _sources_calling("question_for_situation"), (
        "nothing asks which situation a branch is")
    assert _sources_calling("selected_situation"), (
        "nothing reads the answer if it were asked")


test_the_question_that_asks_which_situation_a_branch_is_reaches_a_person = (
    pytest.mark.xfail(
        strict=True,
        reason="`75` B1/B2: §13's third consequence is built at both ends and "
               "called at neither. `question_for_situation` is asked by nothing "
               "and `selected_situation` is read by nothing, so `--situation` "
               "stays one string for a whole corpus -- `68` F6's defect. XPASSes "
               "and fails the suite the moment either half is wired.",
    )(test_the_question_that_asks_which_situation_a_branch_is_reaches_a_person))


def test_every_lazily_created_table_is_created_by_the_writer_that_claims_it(tmp_path):
    """The exemption above is proven, not asserted.

    A census with an unchecked exemption list is a census anyone can pass by adding
    a name to it. Each entry must really be created by the call its reason names.
    """
    from llm_harness.placement_validation import _ensure_identity_table

    conn = open_database(tmp_path / "lazy.sqlite")
    cli._bootstrap(conn)
    assert "llm_cd_plan_identity" not in _tables_present(conn)
    _ensure_identity_table(conn)
    assert "llm_cd_plan_identity" in _tables_present(conn)
    assert set(LAZY_TABLES) <= _tables_declared_in_source()


def test_the_census_can_fail(tmp_path: Path):
    """The falsifying twin: an empty database must NOT satisfy the census.

    Without this, a `_tables_declared_in_source` that silently returned nothing --
    a moved directory, a changed DDL spelling -- would make the test above pass by
    measuring nothing, which is the failure mode a census has.
    """
    conn = open_database(tmp_path / "empty.sqlite")
    assert _tables_declared_in_source() - _tables_present(conn)


# --- the whole-tree reachability census ---------------------------------------------

_DEFINITION = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)

#: Marks a work item as "this module got imported", whose top level therefore ran.
#: No module is named this, so it can never collide with a real one.
_IMPORT_TIME = "\0import-time"


def _module_name(path: Path) -> str:
    parts = list(path.relative_to(_SRC).with_suffix("").parts)
    return ".".join(parts[:-1] if parts[-1] == "__init__" else parts)


@functools.cache
def _sources() -> dict[str, ast.Module]:
    return {_module_name(path): ast.parse(path.read_text(encoding="utf-8"))
            for path in sorted(_SRC.rglob("*.py"))
            if "__pycache__" not in path.parts}


@functools.cache
def _packages() -> frozenset[str]:
    """The module names that are packages, which is what a relative import counts from."""
    return frozenset(_module_name(path) for path in _SRC.rglob("__init__.py"))


@functools.cache
def _definitions() -> dict[tuple[str, str], ast.stmt]:
    """Every name `src/` binds at module level, and the statement that binds it.

    Constants are bound here as well as functions and classes, because a constant is
    how a mechanism is often reached -- `STEPS = (first, second)` is what calls them.
    The CENSUS is narrower than this index on purpose; see `_public_callables`.
    """
    definitions: dict[tuple[str, str], ast.stmt] = {}
    for module, tree in _sources().items():
        for statement in tree.body:
            if isinstance(statement, _DEFINITION):
                definitions[(module, statement.name)] = statement
            elif isinstance(statement, (ast.Assign, ast.AnnAssign)):
                targets = (statement.targets if isinstance(statement, ast.Assign)
                           else [statement.target])
                for target in targets:
                    if isinstance(target, ast.Name):
                        definitions[(module, target.id)] = statement
    return definitions


@functools.cache
def _definitions_by_name() -> dict[str, tuple[tuple[str, str], ...]]:
    """A bare name to EVERY top-level symbol anywhere in `src/` that answers to it.

    This is the deliberate over-approximation. A real resolver would follow the
    importing module's namespace; this one lets `store` in one package reach a
    `store` in another, so reachability comes out too LARGE and never too small.
    """
    index: dict[str, list[tuple[str, str]]] = {}
    for key in _definitions():
        index.setdefault(key[1], []).append(key)
    return {name: tuple(keys) for name, keys in index.items()}


def _import_time(body: list[ast.stmt], out: list[ast.AST]) -> list[ast.AST]:
    """What `import module` actually EXECUTES: its top level, minus def bodies.

    Decorators, base classes, default arguments, annotations and class bodies all run
    at import; a function body does not run until something calls it. Traversing the
    whole module instead would make every function a reached module ever defines look
    called, which is precisely the illusion this census exists to strip.
    """
    for statement in body:
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.extend(statement.decorator_list)
            out.append(statement.args)
            if statement.returns is not None:
                out.append(statement.returns)
        elif isinstance(statement, ast.ClassDef):
            out.extend(statement.decorator_list)
            out.extend(statement.bases)
            _import_time(statement.body, out)
        else:
            out.append(statement)
    return out


@functools.cache
def _import_time_nodes() -> dict[str, tuple[ast.AST, ...]]:
    return {module: tuple(_import_time(tree.body, []))
            for module, tree in _sources().items()}


def _imported_modules(module: str, node: ast.stmt) -> set[str]:
    """The `src/` modules one import statement brings in, relative forms included."""
    known = _sources()
    found: set[str] = set()
    if isinstance(node, ast.Import):
        for alias in node.names:
            parts = alias.name.split(".")
            found.update(candidate for candidate in
                         (".".join(parts[:depth]) for depth in range(1, len(parts) + 1))
                         if candidate in known)
    elif isinstance(node, ast.ImportFrom):
        if node.level:
            parts = module.split(".")
            if module not in _packages():
                parts = parts[:-1]
            parts = parts[:len(parts) - node.level + 1]
            base = ".".join(parts)
            if node.module:
                base = f"{base}.{node.module}" if base else node.module
        else:
            base = node.module or ""
        if base in known:
            found.add(base)
        for alias in node.names:
            candidate = f"{base}.{alias.name}" if base else alias.name
            if candidate in known:
                found.add(candidate)
    return found


def _references_and_imports(nodes, module: str) -> tuple[set[str], set[str]]:
    """Names this code READS, and the modules it imports -- one walk, both answers.

    `Name` is counted only in a Load context: `FOO = ...` binds `FOO`, it does not use
    it, and counting the target would make every constant reach itself.
    """
    names: set[str] = set()
    modules: set[str] = set()
    for root in nodes:
        for node in ast.walk(root):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Load):
                    names.add(node.id)
            elif isinstance(node, ast.Attribute):
                names.add(node.attr)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                modules |= _imported_modules(module, node)
    return names, modules


def _reachable(*seeds: tuple[str, str]) -> frozenset[tuple[str, str]]:
    """Everything a run entered at `seeds` can reach, by import and by reference."""
    definitions = _definitions()
    by_name = _definitions_by_name()
    import_time = _import_time_nodes()
    reached: set[tuple[str, str]] = set()
    imported: set[str] = set()
    work: list[tuple[str, str]] = list(seeds)

    def enter(module: str) -> None:
        if module in imported:
            return
        imported.add(module)
        work.append((_IMPORT_TIME, module))
        parts = module.split(".")
        for depth in range(1, len(parts)):        # importing a.b.c runs a and a.b too
            enter(".".join(parts[:depth]))

    for module, _ in seeds:
        enter(module)
    while work:
        item = work.pop()
        if item[0] == _IMPORT_TIME:
            module = item[1]
            nodes: tuple[ast.AST, ...] = import_time.get(module, ())
        else:
            if item in reached:
                continue
            reached.add(item)
            module = item[0]
            enter(module)
            definition = definitions.get(item)
            if definition is None:
                continue
            nodes = (definition,)
        names, modules = _references_and_imports(nodes, module)
        for other in modules:
            enter(other)
        for name in names:
            for key in by_name.get(name, ()):
                if key not in reached:
                    work.append(key)
    return frozenset(reached)


@functools.cache
def _reachable_from_cli_main() -> frozenset[tuple[str, str]]:
    """`cli.main` is the whole product's one entry point: `cli.py` ends by calling it."""
    return _reachable(("cli", "main"))


@functools.cache
def _public_callables() -> frozenset[tuple[str, str]]:
    """The census population: every public function and class `src/` defines.

    Public, because a leading underscore already says "not for anyone else"; top
    level, because that is the granularity a caller wires; and MECHANISMS only --
    a vocabulary constant nothing reads is a lesser defect than a mechanism nothing
    runs, and every instance measured in this codebase was a function or a module.
    """
    return frozenset(key for key, node in _definitions().items()
                     if isinstance(node, _DEFINITION) and not key[1].startswith("_"))


def _unreachable(reachable: frozenset[tuple[str, str]]) -> list[str]:
    """The census, taken against whatever reachable set it is handed."""
    return sorted(f"{module}.{name}"
                  for module, name in _public_callables() - reachable)


def _census_report(unexplained: list[str]) -> str:
    by_module: dict[str, list[str]] = {}
    for qualified in unexplained:
        module, _, name = qualified.rpartition(".")
        by_module.setdefault(module, []).append(name)
    return "\n".join(
        [f"{len(unexplained)} public mechanisms in src/ that no run reaches "
         f"from cli.main, and that EXEMPT does not explain:"]
        + [f"  {module}: {', '.join(names)}" for module, names in sorted(by_module.items())])


#: Public mechanisms that are legitimately unreachable, each with the reason it is.
#: The rule is `LAZY_TABLES`': a name earns a place by a reason that is TRUE OF IT,
#: verified one at a time. Adding a name to silence the census is how this instrument
#: becomes the whitelist it exists to prevent -- the gap it reports is tracked by the
#: strict xfail below instead, which turns red the day the gap closes.
EXEMPT: dict[str, str] = {
    # --- the Wave-2 walking skeleton, kept by `02-segmentation-map.md` -------------
    # Not "legacy to be deleted". `src/orchestrator.py`'s own docstring cites the
    # segmentation map: the walking skeleton "stays in the repository as the
    # integration test every later part must keep green". It is not INTENDED to be
    # reachable from `cli.main`; `production.py` composes `run_p1_p7` for shipped
    # runs. `facts/usable.py:16`'s capitals say do not WIRE new work into it, which
    # is the opposite of an argument for removing it.
    "orchestrator.run_wave2":
        "the Wave-2 walking skeleton. `02-segmentation-map.md` keeps it as the "
        "integration test every later part must keep green; three test files run "
        "it. A shipped run composes `run_p1_p7` instead, so a caller here would "
        "mean the product ran the skeleton rather than the product.",
    "orchestrator.TARGETED_OCR_UNAVAILABLE":
        "the skeleton's injected `no_usable_facts`, which answers False always. "
        "`facts/usable.py:16-23` states why the real verdict must NOT be passed to "
        "`run_wave2`: it would END THE SCAN on the first PDF. It is reachable only "
        "from the skeleton, and only ever as its stand-in.",
    "extractors.dispatch.extract":
        "its own docstring: 'the backward-compatible composition' of "
        "`extract_initial` and `extract_targeted_ocr`. `run_p1_p7` composes those "
        "two directly, because the orchestrator owns ORDER; this is the single-call "
        "form the skeleton uses. Deleting it would leave the skeleton composing the "
        "two halves by hand, which is a second copy of the order rule.",

    # --- the SPECs' published worked examples ---------------------------------------
    # Fixtures live in `src/` rather than a test tree on purpose, and each module says
    # why: a downstream part builds against them BEFORE the part upstream exists, and
    # they are constructed through the real records so they cannot drift from them.
    # A production caller would mean the product was serving hand-authored data.
    "evidence_shape.fixtures.by_number":
        "P4's nineteen worked examples, by SPEC number. Done-means 9 requires P6, P7, "
        "P8 and P2 to be buildable 'from this document plus the fixtures' before any "
        "extractor exists; a run reads a corpus instead.",
    "placement.fixtures.golden_decisions":
        "P11's five golden decisions, 'published for P12 and P13' as contract "
        "witnesses. P12 and P13 are unbuilt, and when they ship they will consume "
        "these in their tests, not at runtime.",
    "privacy.fixtures.by_number":
        "SPEC §11's published request/decision pairs, 'so P8 can be built against P7 "
        "before P8 exists'. The module's own docstring makes being a LEAF the property "
        "that keeps its numbers out of the gate.",
    "privacy.fixtures.gate_arguments":
        "the argument set for §11's fixtures, same module and same reason: it feeds "
        "the published example, not the gate.",
    "tree_design.fixtures.frozen_tree_fixture":
        "P10's golden frozen tree, which 'P11 and P12 build against before P10 runs'.",
    "tree_design.fixtures.realistic_tree":
        "P10's worked realistic tree, published for the same reason -- MINOR 6 moved "
        "it out of `tests/p11/p10_fixtures.py` so two definitions of one record could "
        "not disagree.",
    "tree_design.fixtures.residual_library_fixture":
        "the published residual library a consumer builds against.",
    "tree_design.fixtures.store_fixture_tree":
        "writes the published fixture through the REAL store so the suite can prove "
        "the fixture and the live read are one record. It is the fixture's own proof, "
        "and a product run has a real tree to write.",
    "tree_design.fixtures.template_library_fixture":
        "the published template library a consumer builds against.",
    "tree_design.fixtures.two_version_pair":
        "the published two-version pair, which exists so a consumer can build a "
        "version diff before P10 has produced two versions.",
    "tree_design.fixtures.walking_skeleton_tree":
        "the smallest published tree, for a consumer standing itself up.",

    # --- architectural instruments: assertions ABOUT the code, not behaviour IN it ---
    "privacy.transport_guard.assert_single_egress":
        "P8 Done-means 3, mechanised: 'exactly one function in the codebase constructs "
        "a model request'. Its own docstring calls it 'an EXISTENCE PROOF over a "
        "module namespace, not a runtime check on a call'. A run calls the transport; "
        "this inspects whether the transport could ever take a string.",
    "privacy.transport_guard.assert_single_call_site":
        "the other half of that proof -- the module calls its sink exactly once. Same "
        "module, same standing: it reads a namespace, it does not run one.",
    "privacy.transport_guard.egress_functions":
        "the surface `assert_single_egress` walks. Reachable only from the instrument.",
    "privacy.transport_guard.sink_names":
        "the `Callable`-annotated names on that surface. Reachable only from the "
        "instrument.",
    "privacy.transport_guard.EgressGuardFailure":
        "the base of the three failures the guard raises; never raised at runtime "
        "because the guard never runs at runtime.",
    "privacy.transport_guard.NoEgressPoint":
        "raised by the guard when a module has no egress point at all.",
    "privacy.transport_guard.MultipleEgressPoints":
        "raised by the guard when a module has more than one.",
    "privacy.transport_guard.UnreleasedContentParameter":
        "raised by the guard when an egress point can take content that P7 never "
        "released.",
    "evidence_shape.determinism.assert_identical_observation_sets":
        "P4 conformance rule 8, whose premise is TWO RUNS over one content hash. A "
        "single run has one observation set and nothing to compare it with, so the "
        "rule is checkable only from outside a run.",
    "evidence_shape.determinism.observation_set_bytes":
        "the one canonical form rule 8 calls identical. Reachable only from that "
        "comparison.",
    "evidence_shape.determinism.observation_set_digest":
        "that form, addressed. §3.4's cache does NOT compare digests -- it is keyed in "
        "SQL by the `extraction_runs_cache_key` index (`schema.py:60`) -- so this has "
        "no runtime consumer to lose.",
    "evidence_shape.determinism.replay_key":
        "the four-field identity rule 8's premise fixes, which is what the comparison "
        "is taken ACROSS.",

    # --- a build-time tool, with its own entry point ---------------------------------
    "recognition.compile.compile_rules":
        "BUILD TIME by declaration: 'Nothing at runtime imports this module, and "
        "`tests/recognition/test_boundaries.py` is the guard that says so.' It has its "
        "own `__main__` and emits a versioned manifest that a run then reads.",
    "recognition.compile.MalformedNodeRow":
        "raised by that compiler when a ratified row will not compile. Build time for "
        "the same reason.",

    # --- a type-only declaration ------------------------------------------------------
    "extractors.sink.EvidenceSink":
        "a `typing.Protocol` -- 'P4's writer, as P5 sees it'. Nothing calls a Protocol; "
        "callers construct the concrete sink and are checked against this shape.",
}


def test_every_public_mechanism_in_the_source_is_reachable_from_the_entry_point():
    """The composition census: does a person's run reach what this codebase ships?

    The table census above asks the same question of the schema. This asks it of the
    CODE, and it is the question no part's own suite can ask, because every part
    builds its own fixture and calls its own functions directly. Coverage of an
    unreachable function is perfect -- coverage asks whether a test entered it, and
    the tests do. The defect lives in the composition, and there is exactly one
    composition root that no part's suite is responsible for.
    """
    unexplained = [qualified for qualified in _unreachable(_reachable_from_cli_main())
                   if qualified not in EXEMPT]
    assert not unexplained, _census_report(unexplained)


test_every_public_mechanism_in_the_source_is_reachable_from_the_entry_point = (
    pytest.mark.xfail(
        strict=True,
        reason="measured 2026-08-30: 261 of 1,226 public mechanisms in src/ are "
               "unreachable from cli.main. 26 are explained by EXEMPT; the other 235, "
               "across 97 modules, are not, and they are not a whitelist -- whole "
               "parts are wired to nothing. §8.4's local-first default posture "
               "(privacy/defaults.py, all 4), P7's consent path (4), P11's residual "
               "return cycle (13), P10's freeze, diff, health and template schema, "
               "the stage_output emitter of EVERY part, the eval harness's shadow and "
               "adversarial gates, P5's date grammar, P6's rule stage, and P12/P13's "
               "in-flight modules. 23 modules have no reached mechanism at all. The "
               "count moves as parts land; the assertion prints the live list. "
               "XPASSes -- and fails the suite, forcing this marker off -- the day "
               "the last one is wired, so shrink it here as they are.",
    )(test_every_public_mechanism_in_the_source_is_reachable_from_the_entry_point))


def test_the_reachability_census_can_fail():
    """The falsifying twin, and it has to catch BOTH ways a census stops measuring.

    A closure that returned everything would pass the census while measuring nothing;
    a closure that returned nothing would fail it for no reason. So this pins one
    symbol in each direction against the REAL closure, and then checks that an empty
    reachable set really does condemn a symbol the product wires. A twin that cannot
    fail is worse than no twin: it guards nothing and reads as a guard.

    The dead anchor is `compile_rules` and NOT one of the gaps the xfail above names.
    A twin anchored to a gap breaks on the day the gap closes, which would make this
    instrument punish its own findings being fixed. `recognition/compile.py` is dead
    by DECLARATION instead -- "Nothing at runtime imports this module" -- and
    `tests/recognition/test_boundaries.py` is a second guard saying so.
    """
    reachable = _reachable_from_cli_main()
    assert ("llm_harness.schema", "create_llm_schema") in reachable, (
        "cli._bootstrap calls it: a closure that cannot see this sees no call at all")
    assert ("recognition.compile", "compile_rules") not in reachable, (
        "a build-time compiler no runtime imports: a closure that reaches this "
        "reaches everything, and the census below would be measuring nothing")
    assert "llm_harness.schema.create_llm_schema" in _unreachable(frozenset())
    assert _public_callables()


def test_every_exemption_names_a_symbol_that_is_really_there_and_really_unreachable():
    """The exemptions are proven, not asserted -- `LAZY_TABLES`' rule, applied here.

    Two failures this catches. A name misspelled in `EXEMPT` silently exempts nothing
    and the census under-reports. A name still in `EXEMPT` after someone WIRED it is a
    stale reason that would go on excusing the next symbol to take that name.
    """
    population = {f"{module}.{name}" for module, name in _public_callables()}
    assert set(EXEMPT) <= population, sorted(set(EXEMPT) - population)
    still_unreachable = set(_unreachable(_reachable_from_cli_main()))
    assert set(EXEMPT) <= still_unreachable, sorted(set(EXEMPT) - still_unreachable)
