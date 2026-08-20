# tests/p5/test_p5_authorship.py
import pytest

from database_agent.events import RESERVED_EVENT_TYPES

from extractors.authorship import (
    AUTHORED_EVENT_TYPES, COMPONENT_VERSION, SUBSYSTEM, event_defaults,
)


def test_p5_names_itself_as_the_author():
    # M8: the acting part authors; P1 writes. One value, no default.
    assert SUBSYSTEM == "P5"


def test_p5_authors_exactly_extraction_and_ocr():
    # SPEC Cross-cutting answers -> Provenance: "two of §8.2's enumerated event
    # types: `extraction` ... and `OCR`". No third.
    assert AUTHORED_EVENT_TYPES == ("extraction", "OCR")


def test_the_ocr_event_type_is_spelled_the_way_8_2_spells_it():
    # MINOR 2, 05-minor-resolutions.md: "§8.2 spells it `OCR`. P4 and P5 change.
    # The writer validates against the vocabulary, so this would have failed at
    # runtime." Not a style preference — a rejected INSERT.
    assert "OCR" in AUTHORED_EVENT_TYPES
    assert "ocr" not in AUTHORED_EVENT_TYPES


def test_every_type_p5_authors_is_one_of_8_2s_reserved_nineteen():
    # B5: registration is a spec-level act. Both names are reserved, so P5 declares
    # nothing and registers nothing.
    assert set(AUTHORED_EVENT_TYPES) <= set(RESERVED_EVENT_TYPES)


def test_p5_publishes_no_registration_call():
    import extractors.authorship as module
    assert not [name for name, value in vars(module).items()
                if callable(value) and name.lower().startswith("register")]


def test_event_defaults_fill_in_8_2s_authorship_fields():
    fields = event_defaults(event_type="extraction", file_id="f1",
                            content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124", explanation="{}")
    assert fields["subsystem"] == "P5"
    assert fields["component_version"] == COMPONENT_VERSION
    assert fields["observed_at"]
    assert fields["event_type"] == "extraction"
    assert fields["file_id"] == "f1"


def test_event_defaults_refuse_a_type_p5_does_not_author():
    # P3 authors `discovery`, `stat observation` and `hashing`; P12 authors the
    # move events. P5 puts its name on neither.
    for foreign in ("discovery", "stat observation", "hashing", "executed move"):
        with pytest.raises(ValueError):
            event_defaults(event_type=foreign, file_id="f1", explanation="{}")


def test_event_defaults_reject_the_lowercase_ocr_spelling():
    with pytest.raises(ValueError):
        event_defaults(event_type="ocr", file_id="f1", explanation="{}")


def test_event_defaults_cannot_be_told_to_name_another_subsystem():
    with pytest.raises(ValueError):
        event_defaults(event_type="extraction", file_id="f1", explanation="{}",
                       subsystem="P1")


def test_event_defaults_require_the_structured_explanation_8_2_asks_for():
    # P1's writer refuses an empty `explanation`; §8.2 requires "a structured
    # explanation or evidence reference". Failing here beats failing at the INSERT.
    with pytest.raises(ValueError):
        event_defaults(event_type="extraction", file_id="f1", explanation="")
