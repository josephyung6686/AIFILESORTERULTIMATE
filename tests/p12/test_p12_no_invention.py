"""F4 -- P12's two structural guarantees, checked by running the code objects.

A text search over `src/mutation/` would match a comment, a docstring, or a
module's own explanation of the rule it is keeping -- and on this project that
has produced a false result more than once, including a guard whose banned word
appeared in its own docstring. So neither guard here reads source text. Both
import the package and walk what the interpreter actually holds: `co_names` for
the attribute names a function reaches for, `co_consts` for the values it was
compiled with, and `__defaults__` for the ones sitting in a signature. A removal
reached through `shutil` contains no `unlink`; a bound spelled `0x5A` or
`1_000` matches no search for `90` or `1000`; a number inside a nested lambda is
in no line a reviewer scans for assignments. All of those are visible here.

What this cannot see is a value assembled at run time -- `int("9" + "0")` holds
two strings and no number. Nothing short of executing every branch would catch
that, and this guard does not claim to.

Each guard is paired with a **sabotage fixture** -- a module synthesized at run
time and never on disk -- so that "the guard found nothing" is distinguishable
from "the guard cannot find anything". A guard only ever run against clean code
passes just as well when its offender list is unreachable.
"""
from __future__ import annotations

import importlib
import os
import pkgutil
import types
from pathlib import Path

import mutation
from mutation import cross_volume
from mutation import vocabulary as v
from mutation.execute import apply_plan, result_of

from .conftest import CONSTRAINTS, plan_a_move

PACKAGE = Path(mutation.__file__).resolve().parent


# ---------------------------------------------------------------------------
# Collecting what the interpreter actually holds.
# ---------------------------------------------------------------------------


def _reachable_codes(value, seen):
    """Every code object reachable from one module attribute, nested included."""
    stack = [value]
    while stack:
        item = stack.pop()
        code = getattr(item, "__code__", None)
        if code is not None:
            item = code
        if not isinstance(item, types.CodeType) or id(item) in seen:
            continue
        seen.add(id(item))
        yield item
        stack.extend(constant for constant in item.co_consts
                     if isinstance(constant, types.CodeType))


def _codes_of(module, *, owned: frozenset[str]):
    """`(label, code)` for every code object DEFINED in `module`'s own file.

    Attribution is by `co_filename`, not by which module's namespace the name
    was found in. `execute.py` imports `copy_and_confirm`, so the function
    appears in two namespaces and is defined in one file; counting it twice
    would make the removal guard report a site that does not exist.
    """
    seen: set[int] = set()
    for name, value in vars(module).items():
        for code in _reachable_codes(value, seen):
            filename = Path(code.co_filename).name
            if filename in owned:
                yield f"{filename}:{code.co_name}", code


def _package_codes():
    owned = frozenset(path.name for path in PACKAGE.glob("*.py"))
    for info in pkgutil.iter_modules([str(PACKAGE)]):
        module = importlib.import_module(f"mutation.{info.name}")
        yield from _codes_of(module, owned=owned)


def _package_attributes():
    for info in pkgutil.iter_modules([str(PACKAGE)]):
        module = importlib.import_module(f"mutation.{info.name}")
        for name, value in vars(module).items():
            yield f"{info.name}.{name}", value


#: Every sabotage module is compiled under this name, so `_codes_of` can be
#: pointed at it exactly as it is pointed at a real one.
OFFENDER = frozenset({"offender.py"})


def _sabotage(source: str):
    """One module that is NOT on disk, compiled and introspected like a real one."""
    module = types.ModuleType("offender")
    module.__file__ = "offender.py"
    exec(compile(source, "offender.py", "exec"), module.__dict__)
    return module


# ---------------------------------------------------------------------------
# Guard 1 -- the only removal of a file.
# ---------------------------------------------------------------------------

#: Every name in this process that can remove something from a filesystem.
#: `rmdir` is here too: it cannot remove a file, but a reader checking §7.11
#: wants to see where directory removal lives as well, and leaving it out would
#: make the report look complete when it was not.
REMOVERS = frozenset({"unlink", "remove", "rmtree", "removedirs", "rmdir"})

#: The only two places in P12 that remove anything, and what each removes.
#: `cross_volume.copy_and_confirm` is §8.2's cross-volume source removal, the
#: single exception §7.11 authorizes, unreachable until V4 returned True.
#: `directories.reverse_directories` removes an EMPTY DIRECTORY, which contains
#: no user file, and uses `rmdir` precisely because the kernel refuses a
#: non-empty one.
PERMITTED_REMOVALS = {
    "cross_volume.py:copy_and_confirm": ["unlink"],
    "directories.py:reverse_directories": ["rmdir"],
}


def removal_sites(codes) -> dict[str, list[str]]:
    """Where a removal primitive is reached for, and which one."""
    found: dict[str, list[str]] = {}
    for label, code in codes:
        hit = REMOVERS & set(code.co_names)
        if hit:
            found[label] = sorted(hit)
    return found


def test_the_only_unlink_in_mutation_is_the_cross_volume_source_removal():
    """§7.11 in one assertion. The exception is named; nothing else removes.

    *"The product must not delete files, mark them disposable, or move them out
    of a protected area without explicit user action"* (`00`:128 §7.11). The
    single removal the design authorizes is the source after a cross-volume copy
    whose destination hash has been confirmed (§8.2), and this says so by
    equality rather than by a subset test: a new removal site anywhere in the
    package fails here, including one added to a module that already has one.
    """
    assert removal_sites(_package_codes()) == PERMITTED_REMOVALS


def test_the_removal_guard_finds_a_removal_reached_through_shutil():
    """The sabotage. Not one `os.unlink` in it, and it is caught anyway."""
    offender = _sabotage(
        "import shutil\n"
        "def tidy_up(path):\n"
        "    shutil.rmtree(path)\n")
    sites = removal_sites(_codes_of(offender, owned=OFFENDER))
    assert sites == {"offender.py:tidy_up": ["rmtree"]}


def test_the_removal_guard_finds_a_second_removal_in_a_module_that_already_has_one():
    offender = _sabotage(
        "import os\n"
        "def copy_and_confirm(source, destination):\n"
        "    os.unlink(source)\n"
        "def clean_the_failed_copy(path):\n"
        "    os.unlink(path)\n")
    assert removal_sites(
        _codes_of(offender, owned=OFFENDER)) != {
            "offender.py:copy_and_confirm": ["unlink"]}


def test_the_one_unlink_is_unreachable_until_v4_answered(
        p12_conn, landscape, fixture_root, clock, ids, monkeypatch):
    """The guard above says where the removal is. This says when it may run.

    Watched at `os.unlink` itself rather than asserted about the outcome, so
    that a copy V4 refused cannot lose the person's file through some other
    path either.
    """
    documents = landscape["root_documents"]
    plan, source = plan_a_move(
        p12_conn, landscape, ids,
        volume_of=lambda path: ("vol-archive" if Path(path) == documents
                                else "vol-home"))
    monkeypatch.setattr(cross_volume, "confirm_cross_volume_copy",
                        lambda conn, **kwargs: False)

    removed: list[str] = []
    real_unlink = os.unlink

    def watched(path, *args, **kwargs):
        removed.append(str(path))
        return real_unlink(path, *args, **kwargs)

    monkeypatch.setattr(os, "unlink", watched)

    record = apply_plan(
        p12_conn, plan, legal_destination_ids=frozenset(
            {plan.requested_destination_node}),
        source_root=fixture_root, destination_root=fixture_root,
        extra_protected=None, conflict_copies=lambda path: (),
        dataless_of=lambda path: False, approval_for=lambda plan_id: None,
        constraints=CONSTRAINTS,
        suffix_for=lambda stem, attempt: f"{stem} ({attempt})",
        max_suffix_attempts=8, normalize_filename=lambda name: name,
        unverified_copy_disposition="kept, and named below",
        scan_state="included", materialized=True,
        component_version="p12-test", user_id=None, now=clock, mint_id=ids)

    assert record.result == result_of(v.FAILED, v.V4_DESTINATION_UNCONFIRMED)
    assert removed == [], "V4 said no and something was removed anyway"
    assert source.exists()


# ---------------------------------------------------------------------------
# Guard 2 -- no number P12 was not given.
# ---------------------------------------------------------------------------

#: A7: *"Every threshold, constraint table, suffix format and root path is
#: injected."* A number written into `src/mutation/` is an answer the design did
#: not give, so 0 and 1 are the only values permitted -- nothing, and one.
PERMITTED_NUMBERS = frozenset({0, 1})

#: Four `-1`s that Wave C and Wave D shipped, each named with the code object it
#: lives in rather than permitted as a value anywhere. Three are the
#: "nothing found yet" sentinel of a longest-match search and one is the slice
#: bound `text[:-1]`. None of them is a threshold, a bound, or a period, and none
#: is a quantity the design was asked for -- but they ARE numeric literals, so
#: they are listed here where a reviewer can see them and decide, rather than
#: waved through by widening the permitted set. Anything else, anywhere, fails.
NAMED_EXCEPTIONS = {
    ("names.py:_truncate_to_bytes", -1),
    ("plan.py:_source_high_level_folder", -1),
    ("resolution.py:_source_folder", -1),
    ("resolution.py:resolve_destination", -1),
}


def invented_numbers(codes) -> list[str]:
    """Every numeric constant a code object holds that P12 was not given."""
    offenders: list[str] = []
    for label, code in codes:
        for constant in code.co_consts:
            if isinstance(constant, bool) or not isinstance(constant,
                                                            (int, float)):
                continue
            if constant in PERMITTED_NUMBERS:
                continue
            if (label, constant) in NAMED_EXCEPTIONS:
                continue
            offenders.append(f"{label} = {constant!r}")
    return offenders


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _signature_numbers(value):
    """Numbers sitting in a callable's signature.

    A default is stored on the function object, not in its code, so it is
    invisible to the constant walk above -- and `batch_bound=50` in a signature
    is exactly the shape a bound P12 was not given would take.
    """
    defaults = getattr(value, "__defaults__", None) or ()
    keyword = (getattr(value, "__kwdefaults__", None) or {}).values()
    return [item for item in (*defaults, *keyword) if _is_number(item)]


def module_level_numbers(attributes) -> list[str]:
    """A number bound at module level, held in a container, or in a signature."""
    offenders: list[str] = []
    for label, value in attributes:
        if _is_number(value) and value not in PERMITTED_NUMBERS:
            offenders.append(f"{label} = {value!r}")
        if isinstance(value, Path):
            offenders.append(f"{label} is a Path")
        if isinstance(value, dict):
            offenders.extend(
                f"{label} holds {item!r}" for item in value.values()
                if _is_number(item) and item not in PERMITTED_NUMBERS)
        offenders.extend(
            f"{label} defaults to {item!r}" for item in _signature_numbers(value)
            if item not in PERMITTED_NUMBERS)
    return offenders


def test_no_number_beyond_zero_and_one_is_written_into_the_part_package():
    assert invented_numbers(_package_codes()) == []
    assert module_level_numbers(_package_attributes()) == []


def test_the_number_guard_finds_a_period_a_bound_and_a_number_no_search_would_match():
    """The sabotage: three plausible ways a number gets in, and not a `2` among
    them.

    A retention period inside a mapping, a batch bound sitting in a signature
    where no assignment line shows it, and a threshold spelled in hexadecimal so
    that searching the source for `90` finds nothing at all.
    """
    offender = _sabotage(
        "RETENTION_DAYS = {'ninety_days': 90}\n"
        "BATCH_CEILING = 0x5A\n"
        "def apply_batch(plans, bound=1_000):\n"
        "    return plans[:bound]\n"
        "def scaled(values):\n"
        "    return [value * 1.75 for value in values]\n")
    attributes = [(f"offender.{name}", value)
                  for name, value in vars(offender).items()]
    module_level = module_level_numbers(attributes)
    assert any("90" in item for item in module_level), (
        "the period, inside a module-level mapping")
    assert any("BATCH_CEILING" in item for item in module_level), (
        "the hexadecimal bound, whose value is 90 and whose spelling is not")
    assert any("apply_batch" in item and "1000" in item
               for item in module_level), (
        "the bound in the signature, which no assignment line shows")
    assert any("1.75" in item for item in invented_numbers(
        _codes_of(offender, owned=OFFENDER))), (
        "the factor inside the comprehension")


def test_the_named_exceptions_are_still_real_and_have_not_gone_stale():
    """A ratchet that quietly stops matching is a ratchet that stopped working.

    If one of the four `-1`s is removed or moved, this fails and the list is
    corrected, rather than the exception outliving the code it excused.
    """
    present = {(label, constant)
               for label, code in _package_codes()
               for constant in code.co_consts
               if not isinstance(constant, bool)
               and isinstance(constant, (int, float))
               and constant not in PERMITTED_NUMBERS}
    assert present == NAMED_EXCEPTIONS


# ---------------------------------------------------------------------------
# Guard 3 -- the vocabulary has one home.
# ---------------------------------------------------------------------------


def test_no_module_outside_vocabulary_rebinds_a_closed_set():
    """A6. `vocabulary.py` publishes each closed set; a second home in another
    module would let the two drift and neither would be wrong on its face."""
    closed = {
        name: value for name, value in vars(v).items()
        if isinstance(value, tuple) and value
        and all(isinstance(item, str) for item in value)
        and not name.startswith("_")
    }
    offenders: list[str] = []
    for info in pkgutil.iter_modules([str(PACKAGE)]):
        if info.name == "vocabulary":
            continue
        module = importlib.import_module(f"mutation.{info.name}")
        for name, value in vars(module).items():
            if name.startswith("_") or not isinstance(value, tuple):
                continue
            for label, members in closed.items():
                if value is not members and set(value) == set(members):
                    offenders.append(
                        f"mutation.{info.name}.{name} is a second home for "
                        f"vocabulary.{label}")
    assert offenders == []


def test_p12_registers_no_event_type_of_its_own():
    """Registration is a spec-level act with no run-time call. P12's seven were
    reserved by the owner in `database_agent/events.py`; P12 mints none."""
    from database_agent.events import RESERVED_EVENT_TYPES
    assert set(v.AUTHORED_EVENT_TYPES) <= set(RESERVED_EVENT_TYPES)
