"""Done-means 3's instrument, proven in both directions.

§8.4 opens with a sequencing requirement -- "Privacy policy must be enforced before
content reaches any model or external connector" -- and P8's Done-means 1 states the
method: "Exactly one function in the codebase constructs a model request, and its only
parameter type is P7's `Released`. A call without a release is not constructible.
Verified by inspection plus a test that the un-released path does not type-check /
does not exist."

`assert_single_egress` is that inspection. It is an existence proof over a module
namespace, not a runtime check: it answers whether a string-prompt entry point EXISTS,
and it answers by resolving annotations rather than by reading text. The last test in
this file states, by name, what it cannot do.

The fixtures are imported as `p7.transport_fixtures` and not as the top-level module
`transport_fixtures`: `tests/p7/__init__.py` exists, so pytest puts `tests/` on
`sys.path` and this directory is the package `p7`. `tests/p7/conftest.py` records the
same reason for its own name -- two helpers sharing a bare name are one module.
"""
import inspect
from pathlib import Path
from types import ModuleType

import pytest

from evidence_shape.observation import Observation
from evidence_shape.text_units import TextUnit

from privacy.release import Released
from privacy.transport_guard import (
    CONTENT_PARAMETER_TYPES, IS_MODEL_TRANSPORT, EgressGuardFailure,
    MultipleEgressPoints, NoEgressPoint, UnreleasedContentParameter,
    assert_single_egress, egress_functions,
)

from p7 import transport_fixtures as fixtures


# --- the conforming shapes pass -------------------------------------------------

def test_the_conforming_transport_passes():
    # One public function, one parameter, annotated `Released`. A checker only proven
    # on the passing case is an assertion that has never been tested, so this is the
    # first of twenty-nine and not the whole file.
    assert assert_single_egress(fixtures.conforming_transport()) is None


def test_a_non_content_parameter_beside_the_release_is_allowed():
    # Done-means 3 constrains the CONTENT parameter: "No transport function accepts a
    # string, a file path, or an observation record." A timeout is none of those, and
    # a guard that refused one would make the real transport unwritable.
    assert assert_single_egress(fixtures.conforming_transport_with_a_timeout()) is None


def test_a_class_based_transport_passes():
    # The receiver is skipped and the parameter is checked. This is the shape an SDK
    # client wrapper takes, so a module-level-functions-only guard would be blind to
    # the most likely real transport.
    assert assert_single_egress(fixtures.conforming_transport_as_a_class()) is None


def test_a_string_return_annotation_is_allowed():
    # The model's reply comes back as text. The gate governs what LEAVES, and pinning
    # this stops a later tightening from making the real transport unrepresentable.
    module = fixtures.conforming_transport()
    assert_single_egress(module)
    only = egress_functions(module)[0]
    assert inspect.signature(only, eval_str=True).return_annotation is str


def test_an_imported_helper_is_not_counted_as_an_entry_point():
    # A real transport imports things. The guard filters on `__module__`, so a helper
    # the module did not define is not one of its entry points.
    module = fixtures.conforming_transport_with_an_imported_helper()
    assert hasattr(module, "dumps")
    assert [fn.__name__ for fn in egress_functions(module)] == ["send"]
    assert_single_egress(module)


# --- exactly one entry point ----------------------------------------------------

def test_two_entry_points_fail():
    with pytest.raises(MultipleEgressPoints) as caught:
        assert_single_egress(fixtures.transport_with_two_entry_points())
    assert "send" in str(caught.value) and "send_batch" in str(caught.value)


def test_no_entry_point_fails():
    # "Exactly one" is violated by zero as surely as by two, and a module with no
    # entry point is not a transport. Naming this `MultipleEgressPoints` would have
    # been a lie in the exception name, which is why the guard publishes both.
    with pytest.raises(NoEgressPoint):
        assert_single_egress(fixtures.transport_with_no_entry_point())


# --- the content types ----------------------------------------------------------

def test_the_five_content_types_are_the_published_set():
    assert CONTENT_PARAMETER_TYPES == frozenset(
        {str, bytes, Path, Observation, TextUnit})


def test_a_transport_taking_a_string_fails():
    with pytest.raises(UnreleasedContentParameter, match="prompt"):
        assert_single_egress(fixtures.transport_taking_a_string())


def test_a_transport_taking_a_path_fails():
    with pytest.raises(UnreleasedContentParameter, match="document"):
        assert_single_egress(fixtures.transport_taking_a_path())


def test_a_transport_taking_an_observation_fails():
    with pytest.raises(UnreleasedContentParameter, match="observation"):
        assert_single_egress(fixtures.transport_taking_an_observation())


def test_a_transport_taking_a_text_unit_fails():
    with pytest.raises(UnreleasedContentParameter, match="unit"):
        assert_single_egress(fixtures.transport_taking_a_text_unit())


def test_a_transport_taking_bytes_fails():
    with pytest.raises(UnreleasedContentParameter, match="payload"):
        assert_single_egress(fixtures.transport_taking_bytes())


# --- containers and unions, which is where "takes no string" hides ---------------

def test_a_list_of_strings_fails():
    with pytest.raises(UnreleasedContentParameter, match="extra"):
        assert_single_egress(fixtures.transport_taking_a_list_of_strings())


def test_a_sequence_of_strings_fails():
    with pytest.raises(UnreleasedContentParameter, match="extra"):
        assert_single_egress(fixtures.transport_taking_a_sequence_of_strings())


def test_an_optional_path_fails():
    with pytest.raises(UnreleasedContentParameter, match="attachment"):
        assert_single_egress(fixtures.transport_taking_an_optional_path())


# --- the ways a parameter avoids being annotated ---------------------------------

def test_an_unannotated_parameter_fails():
    # An unannotated parameter is not shown to be a `Released`, and "not shown to be"
    # is the only standard an inspection can hold.
    with pytest.raises(UnreleasedContentParameter, match="released"):
        assert_single_egress(fixtures.transport_with_an_unannotated_parameter())


def test_var_keyword_fails():
    with pytest.raises(UnreleasedContentParameter, match="payload"):
        assert_single_egress(fixtures.transport_taking_var_keyword())


def test_var_positional_fails():
    with pytest.raises(UnreleasedContentParameter, match="parts"):
        assert_single_egress(fixtures.transport_taking_var_positional())


def test_a_transport_with_no_released_parameter_fails():
    # Nothing forbidden and no release either. SPEC §6: the payload "is bound to one
    # model target and one prompt fingerprint, and is single-use" -- a call carrying no
    # release is bound to nothing and has no audit record behind it.
    with pytest.raises(UnreleasedContentParameter, match="Released"):
        assert_single_egress(fixtures.transport_with_no_released_parameter())


def test_an_unresolvable_annotation_is_a_failure_and_not_a_crash():
    """A guard that propagated a bare `NameError` would give an ambiguous signal at
    exactly the moment it matters.

    A parameter whose annotation does not resolve cannot be SHOWN to be a `Released`,
    so it is re-raised as `UnreleasedContentParameter` with the original attached.
    Built here rather than in `transport_fixtures.py` so that file's published count
    -- four conforming, seventeen non-conforming -- stays what the plan states.
    """
    namespace: dict = {}
    exec(compile('def send(released: "NoSuchTypeAnywhere") -> str:\n'
                 '    return released\n',
                 "<unresolvable_transport>", "exec"), namespace)
    module = ModuleType("unresolvable_transport")
    send = namespace["send"]
    send.__module__ = "unresolvable_transport"
    module.send = send

    with pytest.raises(UnreleasedContentParameter) as caught:
        assert_single_egress(module)
    assert "could not be resolved" in str(caught.value)
    assert isinstance(caught.value.__cause__, NameError)


def test_an_unhashable_annotation_leaf_does_not_crash_the_guard():
    """`Annotated[int, {...}]` puts a dict in `get_args`, and a set-membership test
    on it raises `TypeError` -- an ambiguous signal from the guard rather than a
    verdict about the transport. The leaf check compares by identity instead, which
    agrees with membership on every leaf that is a type.
    """
    from typing import Annotated

    def send(released: Released, retries: Annotated[int, {"max": 3}] = 0) -> str:
        return released.release_id

    module = ModuleType("transport_with_annotated_metadata")
    send.__module__ = "transport_with_annotated_metadata"
    module.send = send
    assert assert_single_egress(module) is None


# --- the two fixtures a weaker guard would pass ----------------------------------

def test_a_private_string_helper_passes_and_a_private_path_helper_does_not():
    """Amended once P8's transport existed. The old assertion was the reverse.

    This test read "a private `_format(text: str)` fails", on the reasoning that
    inside a module whose whole job is egress there is nothing for a bare string to
    legitimately be. P8's shipped transport says otherwise, and §8.4 says it first:
    "Every model call should be recorded in a consent-aware audit record ... which
    model received the data, and the prompt fingerprint." `transport.py`'s private
    `_record_issued(fingerprint: str, observed_at: str)` and `_explanation(model_id:
    str | None, ...)` write exactly that record, and they are indistinguishable in
    shape from `_format(text: str)`. A rule that forbids them forbids the audit
    record §8.4 mandates -- one §8.4 requirement cannot make another unsatisfiable.

    The old rule was also satisfiable COSMETICALLY: move the helpers into a
    neighbouring module and it passes, having changed nothing about what reaches a
    model. A privacy property a file-move satisfies is not a privacy property.

    What survives is the half with no innocent reading. §8.4's always-local set opens
    with "Paths", and no audit field is a `Path`, so `CORPUS_ONLY_TYPES` is still
    banned at any depth. The string-prompt path a caller can actually reach is caught
    on the egress surface -- see `test_the_check_reads_signatures_and_never_source_text`
    and `test_a_class_method_taking_a_string_fails`, both still red.
    """
    assert assert_single_egress(
        fixtures.transport_with_a_private_string_helper()) is None
    with pytest.raises(UnreleasedContentParameter, match="_load"):
        assert_single_egress(fixtures.transport_with_a_private_path_helper())


def test_a_class_method_taking_a_string_fails():
    with pytest.raises(UnreleasedContentParameter, match="Client.send"):
        assert_single_egress(fixtures.transport_as_a_class_taking_a_string())


def test_the_check_reads_signatures_and_never_source_text():
    """The fixture that decides the technique.

    Its docstring says "Released" four times and its entry point takes a `str`. A
    source scan passes it. `inspect.signature(..., eval_str=True)` does not, because
    it never reads the text -- it resolves the annotation objects.
    """
    module = fixtures.transport_whose_docstring_mentions_released()
    assert "Released" in egress_functions(module)[0].__doc__
    with pytest.raises(UnreleasedContentParameter, match="prompt"):
        assert_single_egress(module)


# --- shape of the guard's own surface --------------------------------------------

def test_egress_functions_returns_only_the_public_entry_points():
    module = fixtures.transport_with_a_private_string_helper()
    assert [fn.__name__ for fn in egress_functions(module)] == ["send"]
    assert hasattr(module, "_format")


def test_every_failure_shares_one_base():
    # A caller that does not care WHICH way a transport failed catches one thing.
    for failure in (MultipleEgressPoints, NoEgressPoint, UnreleasedContentParameter):
        assert issubclass(failure, EgressGuardFailure)
    for factory in (fixtures.transport_with_two_entry_points,
                    fixtures.transport_with_no_entry_point,
                    fixtures.transport_taking_a_string):
        with pytest.raises(EgressGuardFailure):
            assert_single_egress(factory())


def test_the_guard_is_the_instrument_and_declares_itself_not_a_transport():
    # Task 22 greps `src/` for `IS_MODEL_TRANSPORT is True`. P8's transport module is
    # the one writer of `True`; until P8 exists that scan is empty, and this module --
    # which imports the forbidden types by NAME in order to forbid them -- must not be
    # the thing the scan finds.
    import privacy.transport_guard as module
    assert IS_MODEL_TRANSPORT is False
    assert module.IS_MODEL_TRANSPORT is False
    flags = [name for name, value in vars(module).items()
             if isinstance(value, bool) and value is True]
    assert flags == []


# --- the honest limit ------------------------------------------------------------

def test_running_this_over_the_real_transport_is_p8s_obligation():
    """Done-means 3 is NOT closed by this file, and the coverage table says so.

        "**No — and this is a finding.** The transport is P8's. P7 proves the
        instrument, the unforgeable token, and the single materialisation locus. The
        property itself is P8 Done-means 1."

    There is no transport module in this repository to point `assert_single_egress`
    at. Layers L1 and L2 -- the unforgeable single-use release (Task 12) and the
    single materialisation locus (Tasks 9 and 21) -- are proven here; layer L3 is
    proven only to the extent that the instrument is proven, which is what the
    twenty-eight tests above do.

    The call P8 must make, once `src/llm/transport.py` exists, is exactly:

        from privacy.transport_guard import assert_single_egress
        import llm.transport
        assert_single_egress(llm.transport)

    and P8's Done-means 1 -- not this test -- is what fails if it is never made.
    """
    import privacy.transport_guard as module

    assert inspect.isfunction(module.assert_single_egress)
    assert list(inspect.signature(module.assert_single_egress).parameters) == [
        "module"]


def test_a_content_taking_constructor_fails():
    """Rule 3: "every function in the module is checked; only the public ones are
    counted". `__init__` is a function in the module, and skipping it let a
    constructible un-released string path through the one guard that exists to say
    there is no such path."""
    with pytest.raises(UnreleasedContentParameter) as caught:
        assert_single_egress(fixtures.transport_with_a_content_taking_constructor())
    assert "__init__" in str(caught.value) and "prompt" in str(caught.value)


def test_a_dataclass_envelope_fails_when_the_entry_point_can_be_handed_one():
    """The same hole with nothing dunder-shaped in the source to notice -- amended.

    The generated `__init__` is still checked; what changed is WHICH ones are on the
    surface. `transport_with_a_dataclass_envelope` declares `PromptEnvelope` and its
    `send(released: Released)` does not accept one, so a caller who builds an
    envelope has nowhere to put it: no content reaches a model through a class the
    egress function cannot take. P8's `ModelResponse` is that shape -- a public
    frozen dataclass of `bytes` and `str` that `issue` only ever RETURNS -- and §8.4
    sequences one direction only, "before content reaches any model".

    Handed to the entry point, the same envelope is a door, and is red.
    """
    assert assert_single_egress(
        fixtures.transport_with_a_dataclass_envelope()) is None
    with pytest.raises(UnreleasedContentParameter, match="PromptEnvelope.__init__"):
        assert_single_egress(
            fixtures.transport_with_an_envelope_the_entry_point_accepts())


def test_a_constructor_is_checked_but_never_counted_as_an_entry_point():
    """The distinction rule 3 draws. A conforming class with a harmless `__init__`
    must still have EXACTLY ONE egress point — if `__init__` were counted, every
    client wrapper would fail as `MultipleEgressPoints`."""
    module = fixtures.conforming_transport_as_a_class()

    class Client:                                   # same shape, plus a constructor
        def __init__(self, timeout: int = 30) -> None:
            self.timeout = timeout

        def send(self, released: Released) -> str:
            return released.release_id

    Client.__module__ = module.__name__
    Client.__init__.__module__ = module.__name__
    Client.send.__module__ = module.__name__
    module.Client = Client
    assert assert_single_egress(module) is None
