"""One vocabulary for one concept: P13 names a gesture, everyone else carries it.

`81` §14's ruling, second consequence: *"P9's and P10's sets become re-exports of
P13's, by MINOR 6's own mechanism: the owning part names it, everyone else carries
it verbatim, and a distinct name bound to P13's object is carrying while a distinct
name bound to a fresh string is the parallel vocabulary MINOR 6 forbids."*

The guard is a SOURCE-LEVEL one and that is deliberate. Python interns short
identifier-like strings, so `tree_design.vocabulary.ACCEPT is
review_surface.vocabulary.ACTION_ACCEPT` is true whether the receiver imported the
name or respelled it -- an identity assertion here would pass forever and prove
nothing, which is `84` §5's *"a guard that has never failed is not a guard"* in its
most literal form. What distinguishes carrying from respelling is not the runtime
object, it is the ASSIGNMENT: a name bound to an import is carrying, a name bound
to a string literal is a second home. That is visible only in the source, so the
source is what is read -- the same move `tests/p13/test_p13_vocabulary.py:186`
makes for the same reason.

`src/placement/vocabulary.py:130-133` states the cost this prevents, two hundred
lines above the block that used to break it: *"A tuple that merely agrees is one
P10 edit away from disagreeing."*
"""
from __future__ import annotations

import ast
import pathlib

import pytest

from review_surface import vocabulary as v

#: The receiver packages. Every module in each is read; a package that carries
#: P13's vocabulary may not respell any part of it anywhere.
RECEIVER_PACKAGES = ("grouping", "placement", "tree_design")

#: Every string P13 owns as a gesture or a place a gesture is made. `VERDICTS`,
#: `PROGRESS_STATES` and `PROGRESS_SOURCES` are deliberately out: no receiver
#: carries them, and `deferred` is a P13 verdict AND a P9 acceptance state, which
#: would make this guard fire on a vocabulary that is genuinely P9's own.
def p13_members() -> frozenset[str]:
    return frozenset(v.ACTIONS) | frozenset(v.SURFACES)


#: Names that spell one of P13's strings and mean something else. Each is already
#: documented and pinned at its own site; the exemption is by NAME, so a new
#: respelling under a new name is still caught.
#:
#: `(module basename, constant name)`, with the axis it actually belongs to:
#:
#: * `placement/vocabulary.py` `PLACEMENT` -- §6's ORIGIN STAGE, not the surface.
#:   The file pins the two together with `assert SURFACE_PLACEMENT == PLACEMENT`
#:   precisely so the collision is a published decision.
#: * `placement/vocabulary.py` `DIMENSION_PLACEMENT` -- §8.5's evaluation
#:   dimension.
#: * `placement/vocabulary.py` `POLARITY_ACCEPT` / `POLARITY_REJECT` and
#:   `tree_design/provenance.py` `ACCEPT_POLARITY` / `REJECT_POLARITY` -- §8.7's
#:   polarity, which is what the receiving part RECORDED, not what the user DID.
#:   `defer` proves they are not one axis: it is an action with no polarity.
#: * `tree_design/provenance.py` `PROPOSAL_CLASS_PLAN_VERSION` -- §8.7's proposal
#:   class. A plan version is a thing a correction is ABOUT, not a screen.
#: * `grouping/graph.py` `_REJECT` -- the same polarity again, read back out of
#:   P1's store to decide what "already rejected" means.
DIFFERENT_AXIS: frozenset[tuple[str, str]] = frozenset({
    ("graph.py", "_REJECT"),
    ("vocabulary.py", "PLACEMENT"),
    ("vocabulary.py", "DIMENSION_PLACEMENT"),
    ("vocabulary.py", "POLARITY_ACCEPT"),
    ("vocabulary.py", "POLARITY_REJECT"),
    ("provenance.py", "ACCEPT_POLARITY"),
    ("provenance.py", "REJECT_POLARITY"),
    ("provenance.py", "PROPOSAL_CLASS_PLAN_VERSION"),
})


def _package_sources(package: str) -> list[tuple[str, str]]:
    module = __import__(package)
    root = pathlib.Path(module.__file__).resolve().parent
    return [(f"{package}/{path.name}", path.read_text())
            for path in sorted(root.glob("*.py"))]


def _dicts_in(node: ast.AST) -> list[ast.Dict]:
    """Every dict literal in an assignment's value, `MappingProxyType(...)` included.

    P9's `_ACTIONS` is a plain dict and P11's `_PROPOSAL_CLASS` is wrapped in one
    call; a guard that read only the bare form would pass on the wrapped one for
    no reason a reader could state.
    """
    return [found for found in ast.walk(node) if isinstance(found, ast.Dict)]


def respellings(sources, members) -> list[str]:
    """Module-level bindings of one of P13's strings to a fresh literal.

    Two syntactic positions, because those are the two this project has actually
    produced: a constant bound to a literal (`ACCEPT: str = "accept"`), and a
    dict keyed by literals (P9's `_ACTIONS`, whose keys ARE the vocabulary).
    Both bind the string to a meaning; neither goes through P13.
    """
    offenders: list[str] = []
    for name, source in sources:
        basename = name.split("/")[-1]
        for statement in ast.parse(source).body:
            if not isinstance(statement, (ast.Assign, ast.AnnAssign)):
                continue
            targets = ([statement.target] if isinstance(statement, ast.AnnAssign)
                       else statement.targets)
            bound = tuple(t.id for t in targets if isinstance(t, ast.Name))
            if statement.value is None:
                continue
            if (isinstance(statement.value, ast.Constant)
                    and isinstance(statement.value.value, str)
                    and statement.value.value in members
                    and not any((basename, one) in DIFFERENT_AXIS
                                for one in bound)):
                offenders.append(
                    f"{name}:{statement.lineno} "
                    f"{'/'.join(bound) or '<target>'} = "
                    f"{statement.value.value!r}")
            for mapping in _dicts_in(statement.value):
                for key in mapping.keys:
                    if (isinstance(key, ast.Constant)
                            and isinstance(key.value, str)
                            and key.value in members):
                        offenders.append(
                            f"{name}:{key.lineno} "
                            f"{'/'.join(bound) or '<target>'} key "
                            f"{key.value!r}")
    return offenders


@pytest.mark.parametrize("package", RECEIVER_PACKAGES)
def test_a_receiver_never_respells_a_name_p13_owns(package):
    """`81` §14.1. Every gesture name and every surface name in a receiver must be
    P13's, carried through an import."""
    offenders = respellings(_package_sources(package), p13_members())
    assert offenders == [], (
        f"{package} respells vocabulary P13 owns; MINOR 6 says the owning part "
        f"names it and everyone else carries it verbatim: {offenders}"
    )


def test_every_set_a_receiver_publishes_is_a_subset_of_p13s():
    """The runtime half, and it catches the failure the source guard cannot.

    A receiver can carry P13's names correctly and still publish a set P13 no
    longer covers -- P13 retires a member, the import still resolves through some
    other module, and the receiver goes on offering a gesture nothing collects.
    The source guard reads assignments and would see nothing; a subset assertion
    over the published tuples does.
    """
    from grouping import learning
    from placement import vocabulary as p11
    from tree_design import vocabulary as p10

    actions, surfaces = frozenset(v.ACTIONS), frozenset(v.SURFACES)
    assert frozenset(p11.REVIEW_ACTIONS) <= actions
    assert frozenset(p11.REVIEW_SURFACES) <= surfaces
    assert frozenset(p10.VERSION_ACTIONS) <= actions
    assert frozenset(p10.REVIEW_SURFACES) - {p10.SURFACE_UNATTENDED} <= surfaces
    assert learning.GROUP_PLAN_SURFACE in surfaces

    #: P10's `unattended` is deliberately NOT one of P13's twelve and must stay
    #: out of them: it is the surface where nobody was shown anything, so an
    #: `unattended` P13 could route would be a gesture attributed to a person who
    #: was not there (`tree_design/provenance.py:62-77`).
    assert p10.SURFACE_UNATTENDED not in surfaces


def test_the_guard_can_actually_find_a_respelling():
    """The negative twin. Four modules that are not on disk, and the guard has to
    separate them -- otherwise "no offenders" means "the guard reads nothing"."""
    members = frozenset({"accept", "group_plan"})

    respelt = [("fake/offender.py", 'ACCEPT: str = "accept"\n')]
    assert respellings(respelt, members) == ["fake/offender.py:1 ACCEPT = 'accept'"]

    keyed = [("fake/offender.py",
              'from review_surface.vocabulary import ACTION_ACCEPT\n'
              '_MAP = {"accept": 1}\n')]
    assert respellings(keyed, members) == ["fake/offender.py:2 _MAP key 'accept'"]

    wrapped = [("fake/offender.py",
                'from types import MappingProxyType\n'
                '_MAP = MappingProxyType({"group_plan": 1})\n')]
    assert respellings(wrapped, members) == [
        "fake/offender.py:2 _MAP key 'group_plan'"]

    carried = [("fake/good.py",
                'from review_surface.vocabulary import ACTION_ACCEPT\n'
                'ACCEPT: str = ACTION_ACCEPT\n'
                '_MAP = {ACCEPT: 1}\n')]
    assert respellings(carried, members) == []


def test_the_different_axis_exemption_is_by_name_and_stays_narrow():
    """An exemption that let any `accept` through in `vocabulary.py` would be a
    hole the size of the rule. It is keyed to the constant's name, so the same
    string under a different name is still an offender."""
    members = frozenset({"accept"})
    exempt = [("placement/vocabulary.py", 'POLARITY_ACCEPT: str = "accept"\n')]
    assert respellings(exempt, members) == []

    renamed = [("placement/vocabulary.py", 'ACTION_ACCEPT: str = "accept"\n')]
    assert respellings(renamed, members) == [
        "placement/vocabulary.py:1 ACTION_ACCEPT = 'accept'"]

    elsewhere = [("grouping/learning.py", 'POLARITY_ACCEPT: str = "accept"\n')]
    assert respellings(elsewhere, members) == [
        "grouping/learning.py:1 POLARITY_ACCEPT = 'accept'"]
