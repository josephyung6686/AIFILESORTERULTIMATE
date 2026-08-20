# tests/p5/test_p5_ocr_policy.py
"""Done-means 5 - §2.2's two states behave differently, and no global
language-quality check exists anywhere."""
from pathlib import Path

import pytest

from extractors.ocr_policy import (
    TEXT_LAYER_STATES, document_ocr_decision, image_ocr_decision, text_layer_state,
)
from extractors.pdf import PdfDocument, PdfPage, extract_pdf
from extractors.reading import Region
from extractors.safety import SafetyPolicy

from conftest import FIXED_CLOCK

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)
FILE_ROW = {"file_id": "f1", "content_hash": "sha256:abc", "filename": "Hw 5.pdf"}


def a_pdf(text: str) -> PdfDocument:
    regions = (Region(zone="body", start=0, end=len(text)),) if text else ()
    return PdfDocument(metadata={}, pages=(PdfPage(number=1, text=text,
                                                   regions=regions),))


def extracted(text: str):
    return extract_pdf(file_row=FILE_ROW, path=Path("/corpus/Hw 5.pdf"),
                       policy=OPEN_POLICY, read_pdf=lambda path: a_pdf(text),
                       find_structured_strings=lambda t: (), now=FIXED_CLOCK,
                       context_window=40)


def test_the_three_states_are_2_2s_own_three():
    assert TEXT_LAYER_STATES == ("text_layer_usable", "text_layer_absent",
                                 "text_layer_broken")


def test_a_photographed_page_has_no_text_layer_and_routes_directly(sink):
    # SPEC fixture: "`hw5-photographed.pdf` - no text layer | §2.1, §2.2 |
    # `text_layer_absent` -> direct OCR route, no language check."
    asked = []
    decision = document_ocr_decision(
        result=extracted(""), file_id="f1", content_hash="sha256:abc",
        no_usable_facts=lambda file_id, content_hash: asked.append(file_id) or True)
    assert decision.state == "text_layer_absent"
    assert decision.run_ocr is True
    assert decision.targeted is False
    # §2.2: "A file with no text should route DIRECTLY to OCR." A document with no
    # evidence has nothing P6 could have failed to make facts from, so P6 is not asked.
    assert asked == []


def test_a_usable_text_layer_does_not_reach_ocr():
    decision = document_ocr_decision(
        result=extracted("Homework 5. Solve for x."), file_id="f1",
        content_hash="sha256:abc",
        no_usable_facts=lambda file_id, content_hash: False)
    assert decision.state == "text_layer_usable"
    assert decision.run_ocr is False


def test_a_broken_text_layer_waits_for_p6_and_is_then_targeted():
    # SPEC fixture: "`corrupt-text-layer.pdf` | §2.2, §8.5 | `text_layer_broken`; NO
    # OCR until P6 returns no-usable-facts."
    result = extracted("�� garbled � text that is not empty")
    still_useful = document_ocr_decision(
        result=result, file_id="f1", content_hash="sha256:abc",
        no_usable_facts=lambda file_id, content_hash: False)
    assert still_useful.state == "text_layer_usable"
    assert still_useful.run_ocr is False

    no_facts = document_ocr_decision(
        result=result, file_id="f1", content_hash="sha256:abc",
        no_usable_facts=lambda file_id, content_hash: True)
    assert no_facts.state == "text_layer_broken"
    assert no_facts.run_ocr is True
    assert no_facts.targeted is True


def test_the_broken_state_is_never_an_observation_and_never_a_run_field(sink):
    # P4: "An extractor may not write an 'EXIF absent', 'NO TEXT LAYER' or 'metadata
    # stripped' observation." The state is a behaviour, not a stored value.
    sink.write(extracted(""))
    sink.conforms()
    assert sink.observations == []
    for state in TEXT_LAYER_STATES:
        assert state not in str(sink.runs[0])
    assert sink.runs[0]["completeness"] == "complete"


def test_p6s_verdict_is_required_and_has_no_default():
    # M11. P6 does not exist yet, and a default here would be P5 answering P6's
    # question.
    import inspect
    parameter = inspect.signature(document_ocr_decision).parameters["no_usable_facts"]
    assert parameter.default is inspect.Parameter.empty


def test_there_is_no_language_quality_check_and_nothing_looks_at_the_text():
    # §2.2: "The system should not use unreliable global language-quality checks that
    # incorrectly punish multilingual or mathematics-heavy documents."
    # §2.7: not "because a broad quality heuristic says the text looks unusual".
    import inspect

    import extractors.ocr_policy as module
    names = {name.lower() for name in vars(module)}
    for forbidden in ("language_quality", "gibberish", "readability", "is_garbled",
                      "text_quality", "looks_like_text", "detect_language",
                      "confidence_of_text", "printable_ratio"):
        assert forbidden not in names
    parameters = set(inspect.signature(document_ocr_decision).parameters)
    assert parameters == {"result", "file_id", "content_hash", "no_usable_facts"}


def test_the_module_holds_no_threshold_because_oq1_is_open():
    # SPEC Open question 1: "What is the 'no usable facts' threshold? ... the design
    # never says how few facts is 'no usable facts'. It is a deferred configuration
    # value." Nothing numeric is bound to a name in this module.
    import extractors.ocr_policy as module
    numeric = {name: value for name, value in vars(module).items()
               if isinstance(value, (int, float)) and not isinstance(value, bool)
               and not name.startswith("__")}
    assert numeric == {}


def test_an_image_with_no_text_and_no_metadata_reaches_ocr(sink):
    # §2.7: "OCR should therefore run when a file yields no usable text AND no usable
    # metadata, including scanned PDFs, confirmed screenshots, and opaque images
    # without EXIF."
    from extractors.shape import run
    from extractors.sink import ExtractionResult
    opaque = ExtractionResult(
        run=run(file_id="f1", content_hash="sha256:abc",
                extractor_name="image.metadata", extractor_version="0.1.0",
                source_type="image", analysis_tier="native", config={},
                completeness="complete",
                coverage={"units": "images", "processed": 1, "total": 1},
                observation_count=0, started_at=FIXED_CLOCK,
                finished_at=FIXED_CLOCK))
    decision = image_ocr_decision(result=opaque)
    assert decision.run_ocr is True
    assert decision.state is None       # §2.2's states are about documents


def test_an_image_with_usable_metadata_does_not_reach_ocr():
    from extractors.shape import location, observation, run, segment
    from extractors.sink import ExtractionResult
    with_exif = ExtractionResult(
        run=run(file_id="f1", content_hash="sha256:abc",
                extractor_name="image.metadata", extractor_version="0.1.0",
                source_type="image", analysis_tier="native", config={},
                completeness="complete",
                coverage={"units": "images", "processed": 1, "total": 1},
                observation_count=1, started_at=FIXED_CLOCK, finished_at=FIXED_CLOCK),
        observations=(observation(
            file_id="f1", content_hash="sha256:abc",
            extractor_name="image.metadata", extractor_version="0.1.0",
            source_type="image", raw_value="Canon",
            location=location(zone="metadata",
                              container_path=(segment("field", label="Make"),)),
            observed_at=FIXED_CLOCK, reliability="direct", signal_tier=1),))
    assert image_ocr_decision(result=with_exif).run_ocr is False


def test_ocr_text_density_is_not_an_input_anywhere_in_the_policy():
    # §2.6: "OCR text density is also not a reliable screenshot detector." Nothing
    # here counts characters, and Task 13 asserts the emission half.
    import inspect

    import extractors.ocr_policy as module
    source = inspect.getsource(module.image_ocr_decision)
    for forbidden in ("len(", "density", "count("):
        assert forbidden not in source, forbidden


def test_text_layer_state_is_available_on_its_own():
    assert text_layer_state(result=extracted(""), file_id="f1",
                            content_hash="sha256:abc",
                            no_usable_facts=lambda f, c: False) == "text_layer_absent"
