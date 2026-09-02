# tests/p7/test_p7_no_invention.py
"""P7 answers no open question in code, and D2's shape holds.

Two techniques and one rule. The rule: an assertion of the form "this token appears
nowhere" is made against the AST, never against `read_text()`, because a comment or a
docstring EXPLAINING why a value is absent matches a text scan for that value. That
failure is recorded in `tests/p3/test_p3_no_invention.py`, which is where
`code_tokens()` comes from and why it exists.

The technique for everything else is `vars(module)`: what a module BINDS is what it
holds, and a number inside a docstring is prose.
"""
import ast
import importlib
import json
import pathlib

import pytest

import privacy
from database_agent.files_table import FILES_COLUMNS, get_file, record_file

from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore, mirror_state
from privacy.learning_seam import assign, reclassify
from privacy.vocabulary import HELD_OPEN, OPEN_QUESTIONS, USER, USER_CONFIRMED

COMPONENT = "0.1.0"
FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
SOURCE_DIR = pathlib.Path(privacy.__file__).parent
SRC_ROOT = pathlib.Path(privacy.__file__).parent.parent

#: Module-level names permitted to be bound to a number. It is EMPTY, and adding a
#: name to it is a P7 contract revision rather than an implementation decision:
#: SPEC *Deferred* puts "Numeric values for every ceiling" outside this contract --
#: §8.6 "names the knobs, states they are 'configurable', and gives no values".
NUMERIC_ALLOWLIST: frozenset[str] = frozenset()

#: Top-level names permitted to bind a P4 text materialiser, each with its reason.
#: Introspected against the live repository, not copied from the plan skeleton, which
#: named `extractors` (which binds none) and omitted `orchestrator` (which binds one).
MATERIALISER_BINDERS = {
    "evidence_shape": "P4 owns them",
    "privacy": "L2 -- `resolve.py` is the ONE place a (key, span) becomes text",
    "orchestrator": (
        "copies text units into P2's replay bundle (§8.5). A local copy, not an "
        "egress -- and whether a bundle may carry excerpt text is P7 Open question 8, "
        "unanswered, so this guard records it and does not rule on it"),
}

MATERIALISERS = ("raw_value_at", "text_units_for_run", "text_unit_at",
                 "unit_for_observation")


def modules():
    return sorted(SOURCE_DIR.glob("*.py"))


def imported():
    """Every module under `src/privacy/`, imported, for namespace introspection."""
    found = []
    for path in modules():
        name = path.stem
        if name == "__init__":
            found.append(privacy)
            continue
        found.append(importlib.import_module(f"privacy.{name}"))
    return found


def _docstrings(tree: ast.AST) -> set[int]:
    """The id() of every node that is a docstring, so it can be skipped."""
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            body = getattr(node, "body", None)
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                found.add(id(body[0].value))
    return found


def code_strings(path: pathlib.Path) -> set[str]:
    """String and numeric literals P7's code USES, docstrings excluded."""
    tree = ast.parse(path.read_text(), filename=str(path))
    skip = _docstrings(tree)
    tokens: set[str] = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Constant) and id(node) not in skip
                and isinstance(node.value, (str, int, float))
                and not isinstance(node.value, bool)):
            tokens.add(str(node.value))
    return tokens


def code_names(path: pathlib.Path) -> set[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    tokens: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            tokens.add(node.id)
        elif isinstance(node, ast.Attribute):
            tokens.add(node.attr)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            tokens.add(node.name)
        elif isinstance(node, ast.arg):
            tokens.add(node.arg)
        elif isinstance(node, ast.keyword) and node.arg:
            tokens.add(node.arg)
        elif isinstance(node, ast.alias):
            tokens.add(node.name)
            if node.asname:
                tokens.add(node.asname)
    return tokens


def code_tokens(path: pathlib.Path) -> set[str]:
    return code_names(path) | code_strings(path)


def imports_of(path: pathlib.Path) -> set[str]:
    """Every dotted name this module imports, from the AST rather than from text."""
    tree = ast.parse(path.read_text(), filename=str(path))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            found.add(module)
            found.update(f"{module}.{alias.name}" for alias in node.names)
            found.update(alias.name for alias in node.names)
    return found


def module_numbers(module) -> dict:
    return {name: value for name, value in vars(module).items()
            if not name.startswith("_")
            and isinstance(value, (int, float)) and not isinstance(value, bool)}


def code_of(path: pathlib.Path, function: str) -> str:
    """One function's source with its DOCSTRING REMOVED.

    `source_of` returns the whole FunctionDef segment, prose included, so a guard
    asserting a token appears in it can be satisfied by a docstring that merely
    MENTIONS the token. `readers.ocr_vision._box`'s docstring contains the literal
    `1.0 - (y + h)`, so the D10 guard below was green whether or not the top-left flip
    existed in the code at all.
    """
    text = path.read_text()
    tree = ast.parse(text, filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function:
            body = node.body
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)):
                body = body[1:]
            return "\n".join(ast.unparse(statement) for statement in body)
    raise AssertionError(f"{function!r} is not defined in {path.name}")


def source_of(path: pathlib.Path, function: str) -> str:
    """One function's source, by AST rather than by `inspect.getsource`.

    `inspect.getsource` needs the module IMPORTED, and three modules under `src/`
    import optional `readers` extras at module scope (`Quartz`, `Vision`,
    `pdfminer`) that this suite does not install -- `tests/readers/` skips them with
    `pytest.importorskip` for exactly this reason. A guard that can only run where an
    optional extra is installed is a guard that does not run.
    """
    text = path.read_text()
    tree = ast.parse(text, filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == function:
                return ast.get_source_segment(text, node) or ""
    raise AssertionError(f"{path.name} defines no {function!r}")


def imported_names(path: pathlib.Path) -> set[str]:
    """Every bare name this module could BIND from an import, plus attribute reads.

    The AST half of the L2 guard, so a module that cannot be imported here is still
    covered rather than silently skipped.
    """
    tree = ast.parse(path.read_text(), filename=str(path))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            found.update(alias.asname or alias.name.split(".")[0]
                         for alias in node.names)
            if isinstance(node, ast.ImportFrom):
                found.update(alias.asname or alias.name for alias in node.names)
        elif isinstance(node, ast.Attribute):
            found.add(node.attr)
    return found


# --- the eleven, present with the SPEC's own text ---------------------------

def test_all_eleven_spec_open_questions_are_present():
    assert set(OPEN_QUESTIONS) == set(range(1, 12))
    for number, text in OPEN_QUESTIONS.items():
        assert text.strip(), number


def test_open_question_11_names_no_winner_between_the_two_local_modes():
    # W1 narrowed it and did not close it: "What remains genuinely open is only WHICH
    # of those two ships, which turns on whether a local model is assumed present."
    #
    # PLAN CONFLICT, resolved for the preamble. The task body asserted that NO module
    # binds a string equal to `"offline"` or `"local_model"`. Preamble section 3.1 requires
    # the opposite: "Every closed vocabulary P7 publishes -- ... operation modes ... is
    # published once with a named constant per member, and every consumer imports the
    # constant." `defaults.OFFLINE` and `defaults.LOCAL_MODEL` are those constants and
    # the task body's clause forbids the convention the preamble settled.
    #
    # A named member is not an answer. What answers OQ11 is a DEFAULT, so that is what
    # this guard forbids: `install_mode` is a required keyword everywhere it appears,
    # `LOCAL_FIRST_MODES` is a floor rather than a choice, and no module binds a name
    # that reads as "the mode we ship".
    import inspect
    from privacy.defaults import LOCAL_FIRST_MODES, LOCAL_MODEL, OFFLINE
    from privacy.vocabulary import OPERATION_MODES
    assert set(LOCAL_FIRST_MODES) == {"offline", "local_model"}
    assert (OFFLINE, LOCAL_MODEL) == LOCAL_FIRST_MODES
    assert set(LOCAL_FIRST_MODES) < set(OPERATION_MODES), (
        "the floor is a proper subset of the vocabulary; if it became the whole "
        "vocabulary, `hybrid` and `cloud_assisted` would have stopped being modes "
        "the user may choose")

    # No module names a winner between the two.
    for module in imported():
        for name in vars(module):
            upper = name.upper()
            if upper.startswith("_"):
                continue
            assert "DEFAULT_MODE" not in upper, (module.__name__, name)
            assert "INSTALL_MODE" not in upper, (module.__name__, name)
            assert upper not in ("DEFAULT_INSTALL", "SHIPPED_MODE"), module.__name__

    # And no callable in the package supplies a mode of its own. A parameter with a
    # default is a build that starts without naming one, which is the answer.
    for module in imported():
        for name, value in vars(module).items():
            if name.startswith("_") or not callable(value):
                continue
            if getattr(value, "__module__", None) != module.__name__:
                continue
            try:
                parameters = inspect.signature(value).parameters
            except (TypeError, ValueError):  # pragma: no cover - builtins
                continue
            for parameter in parameters.values():
                if "mode" not in parameter.name:
                    continue
                assert parameter.default is inspect.Parameter.empty, (
                    module.__name__, name, parameter.name, parameter.default)


def test_no_module_holds_a_bare_hybrid_or_cloud_assisted_default():
    # Done-means 12's negative half, by introspection rather than by grep: both names
    # appear legitimately inside `OPERATION_MODES`, inside `MODE_SEMANTICS`, inside
    # denial messages and inside fixture records, so a text scan either passes
    # vacuously or fails on a comment.
    for module in imported():
        for name, value in vars(module).items():
            if name.startswith("_") or not isinstance(value, str):
                continue
            assert value not in ("hybrid", "cloud_assisted"), (module.__name__, name)


def test_open_question_3_defines_no_corpus_area():
    # "What is a 'corpus area'? ... Consent grants cannot be scoped until this is
    # named." The gate takes an `scope_for` resolver with no default; the only area
    # STRING in the package is the fixture module's single example.
    import inspect
    from privacy.gate import Gate
    parameters = inspect.signature(Gate.__init__).parameters
    assert "scope_for" in parameters
    assert parameters["scope_for"].default is inspect.Parameter.empty
    holders = [m.__name__ for m in imported()
               if any(name.upper().endswith("AREA") or name.upper().endswith("AREAS")
                      for name in vars(m) if not name.startswith("_"))]
    assert holders == ["privacy.fixtures"]
    from privacy.fixtures import FIXTURE_AREA
    assert isinstance(FIXTURE_AREA, str)


def test_open_question_1_never_infers_protected_from_the_handling_class():
    # SPEC §2: "Neighbouring parts should consume the `protected` flag, not infer it
    # from the class."
    #
    # PLAN CONFLICT, resolved for the preamble. The task body pinned this to fixture
    # 10, calling it "a `sensitive_personal` file that is NOT protected". Task 20's
    # shipped fixture 10 is `sensitive_personal` with `protected=True` -- it is the
    # `NeedsConsent` fixture, and reaching the consent branch REQUIRES the flag set.
    # No shipped fixture breaks a class->flag inference; all eighteen are monotone.
    # Preamble §3.9 states the settled instrument instead: "Two tests CONSTRUCT the
    # records that would break an inference -- `public_low` with `protected=True`, and
    # `highly_sensitive_credential_bearing` with `protected=False` -- and assert the
    # flag wins in both directions." Constructed, in both directions, is what runs.
    high = ClassificationRecord(
        file_id="f", content_hash="sha256:abc", handling_class="public_low",
        protected=True, basis=USER, evidence_refs=(),
        reliability_state=USER_CONFIRMED, observed_at=FIXED_CLOCK)
    assert high.protected is True

    low = ClassificationRecord(
        file_id="f", content_hash="sha256:abc",
        handling_class="highly_sensitive_credential_bearing", protected=False,
        basis=USER, evidence_refs=(), reliability_state=USER_CONFIRMED,
        observed_at=FIXED_CLOCK)
    assert low.protected is False

    # And the negative half, which is what actually holds C5 open (preamble §3.9,
    # §6): no module publishes the set that would let a reader DERIVE the flag.
    for module in imported():
        for name in vars(module):
            assert name != "SENSITIVE_CLASSES", module.__name__
            assert "PROTECTED_CLASSES" not in name.upper(), (module.__name__, name)

    # `protected` is a required constructor argument with no default and no
    # derivation: the flag cannot arrive from the class because nothing computes it.
    import inspect
    parameters = inspect.signature(ClassificationRecord).parameters
    assert parameters["protected"].default is inspect.Parameter.empty


def test_open_question_7_counts_no_repetitions():
    # "Does repeated reclassification generalize?" Nothing counts, so nothing widens.
    #
    # Two task-body bugs, both fixed here. `module_numbers` returns a DICT, so
    # `module_numbers(module) - set(...)` raised `TypeError` and the guard never ran a
    # single assertion. And the guard swept `privacy.fixtures`, which the task body's
    # own `test_the_fixture_module_is_a_leaf...` calls "the one module holding
    # numbers" -- the two tests as written contradict each other.
    #
    # The exception is PINNED rather than allowlisted: fixtures is named, and a number
    # appearing in any OTHER module fails. That is stronger than a name-keyed
    # allowlist, which a later author extends by adding a name.
    holders = []
    for module in imported():
        numbers = set(module_numbers(module)) - NUMERIC_ALLOWLIST
        if numbers:
            holders.append(module.__name__)
    assert holders == ["privacy.fixtures"], holders


def test_open_question_10_states_no_retention_period():
    # "How long audit records, consent grants, and superseded classifications are
    # kept. The design states no retention period anywhere."
    for module in imported():
        for name in vars(module):
            upper = name.upper()
            for token in ("RETENTION", "TTL", "EXPIR", "MAX_AGE", "PURGE", "DAYS"):
                assert token not in upper, (module.__name__, name)


# --- the three held open that are not among the eleven ----------------------

def test_held_open_names_exactly_three_and_each_carries_its_source():
    # Three again, but not the same three: D7 and D10 closed two, and the
    # `filename` sixth kind and the five kept round-5 cuts took their places.
    assert set(HELD_OPEN) == {"I6", "filename-sixth-releasable-kind", "round-5-cuts"}
    for key, text in HELD_OPEN.items():
        assert text.strip(), key


def test_i6_is_held_by_delete_derived_refusing_and_not_by_a_sentence():
    from privacy.revocation import DerivedScope, UnratifiedResolution, delete_derived
    with pytest.raises(UnratifiedResolution) as caught:
        delete_derived(DerivedScope("text_units", "text"))
    assert "I6" in str(caught.value)


def test_p7s_classification_record_is_the_sole_home_d7():
    # RULED. D2 made P7's own record authoritative; **D7** then closed the question
    # behind it -- P6 creates no `sensitivity_status` row at all, so P7's Contract-in
    # from P6 is empty. This asserted the question was OPEN; it now asserts the ruled
    # outcome, which is the stronger of the two and needs no change to the body.
    #
    # PLAN CONFLICT, resolved for the preamble. The task body's forbidden list named
    # `fact_id`. Preamble §3.12 publishes that name AS P7's OWN: "P7's classification
    # table projects its published `fact_id` under that name -- exactly as P4's
    # `evidence` table projects `observation_id`." Forbidding it would forbid a device
    # the preamble settled and require rewriting P1's tested supersede functions under
    # a second name, which is the defect §3.12 exists to prevent. The three tokens
    # that are actually P6's stay forbidden.
    for path in modules():
        tokens = code_tokens(path)
        for forbidden in ("file_facts", "field_key", "value_id", "sensitivity_status"):
            assert forbidden not in tokens, (path.name, forbidden)
        assert not [name for name in imports_of(path) if name.startswith("facts")]

    # `fact_id` is P7's own, and it lives on P7's own table only: `classification_store`
    # is the single module holding it as a column literal, and `learning_seam` reaches
    # it only through that store's published methods.
    holders = [path.name for path in modules() if "fact_id" in code_strings(path)]
    assert holders == ["classification_store.py"], holders


def test_the_three_spellings_of_sensitivity_stay_three():
    # `sensitivity` (P7 SPEC), `sensitivity status` (§3.11, P6), `sensitivity_state`
    # (P1's column). C8 calls this "the defect class that has cost this project the
    # most, at the largest scale it has appeared." Three names, one concept, and no
    # code that treats any two as one.
    assert "sensitivity_state" in FILES_COLUMNS
    from privacy.classification import CLASSIFICATION_FIELDS
    assert "handling_class" in CLASSIFICATION_FIELDS
    assert "sensitivity" not in CLASSIFICATION_FIELDS
    assert "sensitivity_state" not in CLASSIFICATION_FIELDS


def test_the_filename_sixth_kind_is_flagged_and_not_treated_as_settled():
    # §8.4's releasable list is FIVE -- "selected excerpts, redacted identifiers,
    # candidate labels, non-sensitive metadata, and evidence references" -- and puts
    # paths in the always-local set. The SPEC adds a sixth and flags it (Open question
    # 2, NEEDS-JOSEPH B5d / C9a). It is Joseph's call and nothing here decides it.
    from privacy.items import Filename
    from privacy.vocabulary import ITEM_KINDS, USER, USER_CONFIRMED
    # Positional, not last: the owner's `self_description` was appended after it on
    # 2026-09-02, which does not settle Open question 2 and must not be read as
    # having. The filename's status is exactly what it was.
    assert ITEM_KINDS[5] == "filename"
    assert len(ITEM_KINDS) == 7
    assert "filename" in OPEN_QUESTIONS[2].lower() or "Filename" in OPEN_QUESTIONS[2]
    assert {f.name for f in __import__("dataclasses").fields(Filename)} == {"file_id"}
    for path in modules():
        tokens = code_tokens(path)
        for settled in ("filename_resolved", "filename_settled",
                        "FILENAME_IS_NOT_A_PATH"):
            assert settled not in tokens, path.name

    # The task body stopped there, and three absent tokens is a guard that cannot
    # fail -- nothing would ever have written those names. The task's own prose names
    # the two assertions that carry the claim: "the SPEC's own flag text is carried
    # beside it", and "the `Filename` item is denied for protected files exactly as
    # §7.3 requires, which is the narrow part the design does settle." Both, executed.
    from privacy.items import (UNRATIFIED_ITEM_KINDS, RATIFIED_ITEM_KINDS,
                               FILENAME_OPEN_QUESTION, ProtectedItemRequested,
                               UnratifiedItemKind, check_item)
    assert UNRATIFIED_ITEM_KINDS == ("filename",)
    assert "filename" not in RATIFIED_ITEM_KINDS
    assert FILENAME_OPEN_QUESTION == OPEN_QUESTIONS[2], (
        "the SPEC's own flag text is carried beside the sixth kind, not paraphrased")

    # `allow_unratified` is required with no default: a caller cannot admit the sixth
    # kind without saying so, which is what makes an unratified reading visible.
    import inspect
    assert (inspect.signature(check_item).parameters["allow_unratified"].default
            is inspect.Parameter.empty)

    item = Filename(file_id="f1")
    # Without the opt-in, the kind is unadmittable in BOTH protection states -- the
    # question is open, not open-for-unprotected-files.
    for protected in (True, False):
        with pytest.raises(UnratifiedItemKind) as caught:
            check_item(item, unit_length=None, zone=None, protected=protected,
                       sensitive_keys=(), allow_unratified=False,
                       suspension_permits_self_description=False)
        assert "B5d" in str(caught.value) and "C9a" in str(caught.value)

    # With the opt-in, §7.3's narrow settled part holds: denied for a protected file,
    # admitted for an unprotected one. `Gate._precheck_items` passes
    # `allow_unratified=True` and its docstring claims exactly this; executed here
    # rather than believed.
    with pytest.raises(ProtectedItemRequested):
        check_item(item, unit_length=None, zone=None, protected=True,
                   sensitive_keys=(),
                   suspension_permits_self_description=False,
                   allow_unratified=True)
    assert check_item(item, unit_length=None, zone=None, protected=False,
                      sensitive_keys=(),
                      suspension_permits_self_description=False,
                      allow_unratified=True) is None


def test_a_normalized_bounding_box_is_measured_from_the_top_left_d10():
    # RULED. This test used to forbid P7 from doing ANY arithmetic on a region field,
    # because no document said which corner `norm` measured from and P7 is the part
    # that would otherwise have answered it by accident. **D10** answered it: `norm`
    # means TOP-LEFT, and `readers.ocr_vision._box` converts Vision's bottom-left
    # rectangles at the adapter (commit 87016b0). Redaction may now rely on it.
    #
    # The guard inverts rather than disappearing. P4's shape is still five keys with
    # no origin field, so the convention lives in exactly one place and P7 must not
    # re-declare it: P7 holds no origin token of its own, and the one place the flip
    # happens stays outside this part.
    from evidence_shape.location import Region
    region_fields = {f.name for f in __import__("dataclasses").fields(Region)}
    assert region_fields == {"x", "y", "w", "h", "unit"}, (
        "D10 was closed at the adapter precisely so P4's shape would not move")

    # The flip is read from the adapter's SOURCE, not from an import. `ocr_vision`
    # imports `Quartz` at module scope and `Quartz` is an optional `readers` extra --
    # `tests/readers/` skips its own suite with `pytest.importorskip` for that reason.
    # `inspect.getsource` needs the import; the AST does not, so this guard runs on
    # every machine rather than only on one with pyobjc installed.
    adapter = SRC_ROOT / "readers" / "ocr_vision.py"
    # `code_of`, not `source_of`: the docstring of `_box` contains the literal
    # `1.0 - (y + h)`, so asserting over the whole segment was satisfied by PROSE and
    # stayed green whether or not the flip existed. This reads the statements only.
    flip = code_of(adapter, "_box")
    assert "1.0 - (" in flip, (
        "the top-left flip lives in the Vision adapter; if it moved, P7's redaction "
        "is reading a convention nothing enforces")
    # and the guard must FAIL on prose alone -- the docstring does contain the token,
    # which is exactly why the previous version of this assertion could not fail.
    docstring = ast.get_docstring(
        next(node for node in ast.walk(ast.parse(adapter.read_text()))
             if isinstance(node, ast.FunctionDef) and node.name == "_box"))
    assert "1.0 - (" in docstring          # the prose that used to satisfy it

    for path in modules():
        tokens = code_tokens(path)
        for origin in ("top_left", "bottom_left", "top-left", "bottom-left"):
            assert origin not in tokens, (path.name, origin)


# --- D2's shape, which is what replaced the OQ11 guard -----------------------

def test_the_classification_record_is_keyed_on_file_id_and_content_hash(
        p7_conn, tmp_path):
    # D2 clause 1: "Keyed on the hash because a classification is about BYTES; new
    # bytes at a path are a new file version and inherit nothing."
    store = ClassificationStore(p7_conn)
    document = tmp_path / "doc.pdf"
    document.write_bytes(b"%PDF-1.4 one")
    file_id = record_file(
        p7_conn, document, filename="doc.pdf", normalized_filename="doc.pdf",
        extension=".pdf", observed_size=document.stat().st_size,
        observed_timestamps='{"mtime": 1.0}', parent_folder_context=str(tmp_path),
        mime_type="application/pdf", detected_format="pdf",
        scan_state="fixture-scan-state", materialized=True)
    first = ClassificationRecord(
        file_id=file_id, content_hash=get_file(p7_conn, file_id)["content_hash"],
        handling_class="sensitive_personal", protected=True, basis=USER,
        evidence_refs=(), reliability_state=USER_CONFIRMED, observed_at=FIXED_CLOCK)
    store.write(first)
    assert store.current(file_id, first.content_hash) == first
    assert store.current(file_id, "sha256:different-bytes") is None


def test_the_column_is_written_only_through_p1s_published_setter():
    # D2 clause 2, and the reason there is no `SensitivityStateWriter`: P1 publishes
    # `set_sensitivity_state`, the twin of `set_extraction_status`. A protocol
    # wrapping a function that exists is a second write path to a column that spent
    # the whole project with none.
    #
    # PLAN CONFLICT, resolved for the shipped code. The task body named
    # `privacy.learning_seam` as the binder. The shipped binder is
    # `privacy.classification_store`, which wraps the setter in `mirror(...)`;
    # `learning_seam` imports `mirror` and never touches the setter itself. That is
    # the SAME obligation -- one module, one write path -- reached through one more
    # published function, and D2's clause is about there being no SECOND path.
    binders = [m.__name__ for m in imported()
               if "set_sensitivity_state" in vars(m)]
    assert binders == ["privacy.classification_store"], binders

    # The one module downstream of it reaches the column only through that module.
    from privacy.classification_store import mirror as store_mirror
    import privacy.learning_seam as seam
    assert "set_sensitivity_state" not in vars(seam)
    assert seam.mirror is store_mirror

    # No injected protocol, in any module. D2: "P7 takes no `SensitivityStateWriter`
    # and no injected protocol."
    for module in imported():
        for name in vars(module):
            assert "SensitivityStateWriter" not in name, module.__name__
            assert "StateWriter" not in name, (module.__name__, name)

    # And the setter is P1's, imported -- not a private copy of P1's UPDATE.
    from database_agent.files_table import set_sensitivity_state
    from privacy.classification_store import set_sensitivity_state as reexported
    assert reexported is set_sensitivity_state


def test_src_privacy_issues_no_update_files_of_its_own():
    # D2 clause 2's negative half. Over the AST's string literals, so a docstring
    # explaining the rule neither satisfies it nor breaks it.
    for path in modules():
        for literal in code_strings(path):
            collapsed = " ".join(literal.lower().split())
            assert "update files" not in collapsed, (path.name, literal[:60])
            assert "insert into files" not in collapsed, (path.name, literal[:60])
            assert "delete from files" not in collapsed, (path.name, literal[:60])


def test_unclassified_never_reaches_the_projection_column(p7_conn, tmp_path):
    # D2 clause 3: "`Unreadable or unclassified` is a GATE OUTCOME, not a file fact.
    # It lives on the release decision and never in that column, so 'nothing has
    # looked' can never be read as 'this file carries nothing'."
    store = ClassificationStore(p7_conn)
    document = tmp_path / "opaque.psd"
    document.write_bytes(b"8BPS fixture bytes")
    file_id = record_file(
        p7_conn, document, filename="opaque.psd", normalized_filename="opaque.psd",
        extension=".psd", observed_size=document.stat().st_size,
        observed_timestamps='{"mtime": 1.0}', parent_folder_context=str(tmp_path),
        mime_type="image/vnd.adobe.photoshop", detected_format="psd",
        scan_state="fixture-scan-state", materialized=True)
    content_hash = get_file(p7_conn, file_id)["content_hash"]
    record = ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class="unreadable_unclassified", protected=False, basis="detector",
        evidence_refs=("sha256:" + "0" * 64,), reliability_state="direct",
        observed_at=FIXED_CLOCK)

    # PLAN CONFLICT, resolved for the shipped code, which is STRICTLY STRONGER than
    # the task body. The body expected `assign` to succeed and the projection to drop
    # the class, then asserted `"unclassified" not in` the stored JSON. Shipped
    # `ClassificationStore.write` and `mirror_state` each RAISE
    # `GateOutcomeNotAFileFact` on that class, so the record never becomes a row and
    # the column is never written at all. "Never reaches the column" holds a fortiori,
    # and it is asserted here as the refusal plus the column's untouched state --
    # never by weakening the claim to match a value that no longer exists.
    from privacy.classification_store import GateOutcomeNotAFileFact, mirror_state

    with pytest.raises(GateOutcomeNotAFileFact) as caught:
        assign(p7_conn, record, store=store, component_version=COMPONENT)
    assert "D2" in str(caught.value)

    with pytest.raises(GateOutcomeNotAFileFact):
        mirror_state(record)

    # The column still says "nothing has looked", which is the distinction D2's third
    # clause exists to protect and Task 20's fixtures 2 and 15 exist to demonstrate.
    stored = get_file(p7_conn, file_id)["sensitivity_state"]
    assert stored is None, stored

    # And a classified file DOES reach it, so the assertion above is about
    # `unreadable_unclassified` and not about `assign` being inert.
    classified = ClassificationRecord(
        file_id=file_id, content_hash=content_hash, handling_class="public_low",
        protected=False, basis="detector", evidence_refs=("sha256:" + "0" * 64,),
        reliability_state="direct", observed_at=FIXED_CLOCK)
    assign(p7_conn, classified, store=store, component_version=COMPONENT)
    written = get_file(p7_conn, file_id)["sensitivity_state"]
    assert written is not None
    assert "unclassified" not in json.dumps(json.loads(written))


def test_the_projection_is_not_the_authoritative_record():
    # `mirror_state` is a PROJECTION: it drops what the column cannot answer. A mirror
    # that carried every field would invite a reader to treat the column as the
    # record, which is the shape D2 replaced.
    # `"sha256:x"` is not a P4 observation key -- Task 3 refuses it (M14: 71
    # characters, `sha256:` plus 64 hex). The task body's literal made this test
    # raise on construction rather than assert anything.
    record = ClassificationRecord(
        file_id="f", content_hash="sha256:abc", handling_class="public_low",
        protected=False, basis="detector", evidence_refs=("sha256:" + "0" * 64,),
        reliability_state="validated", observed_at=FIXED_CLOCK)
    state = mirror_state(record)

    # The task body wrote `set(state) < {f for f in vars(record)} | set(state)`, which
    # is true whenever the record has ANY field the state lacks -- it cannot fail on a
    # projection that gained a field, only on one that gained ALL of them. Stated as
    # the two directions it actually means:
    fields = {f.name for f in __import__("dataclasses").fields(record)}
    assert set(state) < fields, "the projection must drop something"
    assert set(state) <= fields, "and must invent nothing the record does not carry"
    assert "file_id" not in state
    assert "fact_id" not in state


# --- the three refusals stay three ------------------------------------------

def test_src_privacy_imports_none_of_extractors_three_refusals():
    # Reading is refused by P3/P5 (`ProtectedContainerRefused`); materializing is
    # refused by P3/P5 (`DatalessRefused`); a malformed extraction is refused by P5
    # (`ContractViolation`). RELEASE is P7's, and only release has a consent branch.
    # A file that failed either of the first two never acquires the
    # `(file_id, content_hash)` pair P7 keys on, so re-deriving is unconstructible.
    refusals = ("ProtectedContainerRefused", "DatalessRefused", "ContractViolation")
    for path in modules():
        names = imports_of(path)
        for refusal in refusals:
            assert refusal not in names, (path.name, refusal)
            assert f"extractors.safety.{refusal}" not in names, path.name
        assert "extractors.safety" not in names, path.name
        assert "admit" not in names, path.name


def test_the_orchestrator_imports_all_three_so_the_list_is_three_and_not_two():
    # The plan skeleton names two. The live caller names three, side by side, which is
    # how the omission was found.
    orchestrator = importlib.import_module("orchestrator")
    for refusal in ("ProtectedContainerRefused", "DatalessRefused",
                    "ContractViolation"):
        assert refusal in vars(orchestrator), refusal


# --- L2: one materialisation locus, repo-wide -------------------------------

def test_only_one_module_under_src_privacy_binds_a_p4_text_materialiser():
    binders = [m.__name__ for m in imported()
               if any(name in vars(m) for name in MATERIALISERS)]
    assert binders == ["privacy.resolve"]


def test_the_repo_wide_set_of_materialiser_binders_is_the_named_three():
    # Layer L2 of Done-means 3. This passes trivially today and becomes load-bearing
    # the moment P8 lands, which is why it is written now rather than later by someone
    # who wants it to pass.
    from evidence_shape import store as p4_store
    from evidence_shape import text_units as p4_text
    targets = {p4_text.raw_value_at, p4_store.text_units_for_run,
               p4_store.text_unit_at, p4_store.unit_for_observation}
    found: set[str] = set()
    unimportable: list[str] = []
    for path in sorted(SRC_ROOT.rglob("*.py")):
        if "__pycache__" in path.parts or ".egg-info" in str(path):
            continue
        dotted = str(path.relative_to(SRC_ROOT).with_suffix("")).replace("/", ".")
        dotted = dotted[:-9] if dotted.endswith(".__init__") else dotted

        # The AST half runs on EVERY file, importable or not. Three modules under
        # `src/` import optional `readers` extras at module scope (`Quartz`,
        # `Vision`, `pdfminer`), and skipping them would leave a hole in a guard
        # whose whole value is that it is repo-wide.
        if imported_names(path) & set(MATERIALISERS):
            found.add(dotted.split(".")[0])

        try:
            module = importlib.import_module(dotted)
        except ImportError:
            unimportable.append(dotted)
            continue
        # `value in targets` is `==` against a set and raises `TypeError:
        # unhashable type: 'ModuleSpec'` on the first module namespace holding one.
        # Binding is IDENTITY: two functions that compare equal are still one object
        # or two, and only the object matters here.
        if any(any(value is target for target in targets)
               for value in vars(module).values()):
            found.add(dotted.split(".")[0])

    assert found == set(MATERIALISER_BINDERS), sorted(found)
    for binder, reason in MATERIALISER_BINDERS.items():
        assert reason.strip(), binder

    # Optional reader extras vary by deployment.  The guard must scan their ASTs
    # whether or not they import here, while an unexpected unimportable module must
    # still fail visibly.
    allowed_unimportable = {
        "readers.deployment", "readers.ocr_vision", "readers.pdf_pdfminer"
    }
    assert set(unimportable) <= allowed_unimportable, sorted(unimportable)


# --- P7 invents nothing -----------------------------------------------------

def test_no_module_imports_re_so_p7_holds_no_detection_rule():
    # SPEC *Deferred*: "The design states *what* is protected and never *how it is
    # recognised*. The detector rule set, its signals, and its thresholds are
    # hand-authored. P7 publishes the vocabulary the detectors write into."
    for path in modules():
        names = imports_of(path)
        assert "re" not in names, path.name
        assert "regex" not in names, path.name


def test_no_module_enumerates_an_identifier_class_or_holds_a_transform():
    # SPEC *Deferred*: "Which identifier classes exist and how each is transformed is
    # not enumerated anywhere in the design. `redaction_manifest` carries the class as
    # an opaque string until this is authored."
    import inspect
    from privacy import redaction
    assert not hasattr(redaction, "IDENTIFIER_CLASSES")
    assert not hasattr(redaction, "TRANSFORMS")
    parameters = inspect.signature(redaction.apply_redaction).parameters
    for required in ("classifier", "transform"):
        assert parameters[required].default is inspect.Parameter.empty


def test_the_gate_holds_no_threshold_and_reads_p1s_ceiling():
    # SPEC *Deferred*: "Numeric values for every ceiling ... Deferred to configuration,
    # not to this contract." The ceiling is read from `database_agent.budget`; the
    # request field is the caller's echo of it (M9).
    from database_agent.budget import CEILING_KEYS
    assert "model.max_dossier_tokens_per_call" in CEILING_KEYS
    from privacy.release import REQUEST_FIELDS
    assert "max_dossier_tokens" in REQUEST_FIELDS


def test_the_fixture_module_is_a_leaf_so_its_numbers_reach_no_decision():
    # The one module holding numbers holds them INSIDE records, and nothing imports
    # it. A fixture records a value the way a recorded call records one.
    for path in modules():
        if path.stem == "fixtures":
            continue
        assert "privacy.fixtures" not in imports_of(path), path.name
        assert "fixtures" not in imports_of(path), path.name


def test_subsystem_p7_is_written_in_exactly_one_module():
    # M8: "the acting part authors, P1 stores." A second place that writes the author
    # is a second place the two can disagree.
    holders = [path.name for path in modules() if "P7" in code_strings(path)]
    assert holders == ["authorship.py"]


def test_no_module_holds_a_gazetteer():
    # §3.7 names "validated gazetteers" as a mechanism and never enumerates contents.
    for module in imported():
        for name, value in vars(module).items():
            if name.startswith("_") or not isinstance(value, (tuple, frozenset)):
                continue
            assert len(value) <= 20, (module.__name__, name, len(value))


def test_the_retraction_limit_wording_lives_nowhere_in_the_package():
    # SPEC *Deferred*: "Consent-prompt and retraction-limit wording | §8.4 | UX copy."
    # Task 15 enforces PRESENCE; the words are P13's. Asserted package-wide here
    # because the failure mode is a helpful default appearing in a neighbouring module.
    #
    # PLAN CONFLICT, resolved for the shipped code. `fixtures.py` binds
    # `FIXTURE_RETRACTION_LIMIT`, the string fixture 3's revocation supplies as a
    # CALLER ARGUMENT. That is not the failure this guard names -- "a helpful default
    # appearing in a neighbouring module" -- because `revoke` has no default to be
    # helpful with, and `test_the_fixture_module_is_a_leaf...` proves nothing imports
    # fixtures, so the string reaches no decision. The scan therefore covers every
    # module that CAN reach one, and the mechanism is asserted directly.
    for path in modules():
        if path.stem == "fixtures":
            continue
        for literal in code_strings(path):
            # One clause, and deliberately only one. Widening it to "retract" or to
            # "retraction limit" catches `resolve.py` explaining that an upgrade may
            # "have retracted" text and `audit.py` explaining that the limit "is
            # unsatisfiable without the log" -- prose ABOUT the deferral, which is
            # the P3 failure this module's own docstring cites. The wording is a
            # sentence addressed to a user; that is what is scanned for.
            assert "cannot retract" not in literal.lower(), (path.name, literal[:60])

    # The mechanism, which a text scan cannot express: P13 owns the wording and
    # `revoke` only enforces presence, so the parameter is required with no default.
    import inspect
    from privacy.revocation import MissingRetractionLimit, revoke
    parameter = inspect.signature(revoke).parameters["retraction_limit"]
    assert parameter.default is inspect.Parameter.empty
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert MissingRetractionLimit is not None
