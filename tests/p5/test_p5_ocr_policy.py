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
FILE_ROW = {"file_id": "f1", "content_hash": "67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124", "filename": "Hw 5.pdf"}


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
        result=extracted(""), file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
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
        content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
        no_usable_facts=lambda file_id, content_hash: False)
    assert decision.state == "text_layer_usable"
    assert decision.run_ocr is False


def test_a_broken_text_layer_waits_for_p6_and_is_then_targeted():
    # SPEC fixture: "`corrupt-text-layer.pdf` | §2.2, §8.5 | `text_layer_broken`; NO
    # OCR until P6 returns no-usable-facts."
    result = extracted("�� garbled � text that is not empty")
    still_useful = document_ocr_decision(
        result=result, file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
        no_usable_facts=lambda file_id, content_hash: False)
    assert still_useful.state == "text_layer_usable"
    assert still_useful.run_ocr is False

    no_facts = document_ocr_decision(
        result=result, file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
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
        run=run(file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
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
        run=run(file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
                extractor_name="image.metadata", extractor_version="0.1.0",
                source_type="image", analysis_tier="native", config={},
                completeness="complete",
                coverage={"units": "images", "processed": 1, "total": 1},
                observation_count=1, started_at=FIXED_CLOCK, finished_at=FIXED_CLOCK),
        observations=(observation(
            file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
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
                            content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
                            no_usable_facts=lambda f, c: False) == "text_layer_absent"


# --- §2.7's main path was dead (executed 2026-08-21) --------------------------
#
# "OCR is not merely a rescue tool for scanned PDFs. It is the main way screenshots
# and opaque loose images become understandable to the pre-sorting engine." Executed
# against the real E5, no image could reach E6: `extract_image` emits `format` and
# `pixel dimensions` for EVERY image, both at `zone=metadata`, and
# `_has_metadata_observation` counted any metadata row as usable metadata. So
# `image_ocr_decision` returned run_ocr=False for a PNG screenshot with no EXIF, no
# colour and no software -- §2.7's named example.
#
# The tests above passed because they SYNTHESIZE a zero-observation image result,
# which `extract_image` never produces.
#
# §2.6 already ranks these: "camera EXIF is strong photo evidence; capture time, GPS,
# and sensor-shaped dimensions reinforce it; exact display resolutions, PNG format,
# and software metadata may support a screenshot hypothesis." Tier 3 is the level
# every image has, so it cannot distinguish an opaque image from an informative one.
# P5 already stamps the tier on the record (M2: "carried on the record and never
# re-derived downstream"), so reading it here is using the hierarchy, not building a
# second one.

def _real_image(**over):
    """A run from the REAL E5, not a synthesized one."""
    from pathlib import Path as _P
    from extractors.image import ImageRecord, extract_image
    from extractors.safety import SafetyPolicy
    record = ImageRecord(**{"image_format": "PNG", "dimensions": "2880x1800",
                            "width": 2880, "height": 1800,
                            **over.pop("record", {})})
    return extract_image(
        file_row={"file_id": "f1", "filename": "Screenshot.png",
                  "content_hash": "5f7b1a1c9d4e6f2a3b8c0d1e2f3a4b5c6d7e8f90a1b"
                                  "2c3d4e5f60718293a4b5c"},
        path=_P("/c/Screenshot.png"),
        policy=SafetyPolicy(is_protected_container=lambda p: False,
                            is_dataless=lambda p: False),
        read_image=lambda p: record,
        dimension_signal=over.pop("dimension_signal", lambda w, h: None),
        filename_pattern=lambda n: None, now=FIXED_CLOCK, context_window=40).extraction


def test_a_real_opaque_screenshot_reaches_ocr():
    """§2.7's named example: an opaque image without EXIF."""
    result = _real_image()
    assert result.observations, "E5 always emits format and dimensions"
    assert image_ocr_decision(result=result).run_ocr is True


def test_a_real_photograph_with_camera_exif_does_not_reach_ocr():
    """§2.6 tier 1 -- "camera EXIF is strong photo evidence"."""
    from extractors.image import ExifValue
    result = _real_image(record={"exif": (
        ExifValue(name="Make", value="Apple", kind="camera EXIF"),)})
    assert image_ocr_decision(result=result).run_ocr is False


def test_sensor_shaped_dimensions_are_enough_to_hold_ocr_back():
    """§2.6 tier 2 -- "capture time, GPS, and sensor-shaped dimensions reinforce it"."""
    result = _real_image(dimension_signal=lambda w, h: "sensor-shaped dimensions")
    assert image_ocr_decision(result=result).run_ocr is False


def test_an_exact_display_resolution_is_not_enough():
    """§2.6 tier 3, and the whole point: the signal that "may support a screenshot
    hypothesis" must not be read as evidence that the image is already understood."""
    result = _real_image(dimension_signal=lambda w, h: "exact display resolution")
    assert image_ocr_decision(result=result).run_ocr is True
