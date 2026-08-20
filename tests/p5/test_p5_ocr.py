# tests/p5/test_p5_ocr.py
"""E6 - §2.7. Done-means 9: "OCR persists all nine §2.7 fields across
`extraction_runs`, the observation and `text_units`, and the 400-page fixture is
marked `capped` rather than `complete`."
"""
import inspect
from pathlib import Path

import pytest

import extractors.ocr as ocr_module
from extractors.ocr import (
    ANALYSIS_TIER, EXTRACTOR_NAME_PREFIX, FIELD_HOMES, OcrOutput, OcrRegion,
    PERSISTED_FIELDS, extract_ocr, extractor_name_for,
)
from extractors.reading import StructuredString
from extractors.runs import analysis_tier_for, cache_key
from extractors.safety import DatalessRefused, ProtectedContainerRefused, SafetyPolicy
from extractors.shape import fingerprint

from conftest import FIXED_CLOCK

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)
FILE_ROW = {"file_id": "f-scan", "content_hash": "bcbb377bc839704c4e4ccf7781cce3dcc88cc8a288c9eebbffa245a3476c56e9",
            "filename": "hw5-photographed.pdf"}

#: Every value here is the CALLER's. §2.7's language list is Deferred and its DPI is
#: named as "such as", so no number and no language code lives in `extractors`.
FIXTURE_CONFIG = {"recognition": "accurate", "languages": ["en-US"], "dpi": 200}

RECOGNIZED = "Homework 5 for BUSIB 4300, due 2026-07-17."


def a_page(number=1, text=RECOGNIZED, confidence=0.94):
    return OcrRegion(page=number, region=1, text=text,
                     box={"x": 0.1, "y": 0.2, "width": 0.8, "height": 0.05},
                     confidence=confidence)


def an_output(**overrides) -> OcrOutput:
    base = dict(provider="apple-vision", provider_version="19.1",
                regions=(a_page(),), pages_processed=1, pages_total=1, capped=False)
    base.update(overrides)
    return OcrOutput(**base)


def find_course_code(text: str):
    at = text.find("BUSIB 4300")
    return (StructuredString(kind="identifier", start=at, end=at + 10),) if at != -1 else ()


def run_it(output=None, *, config=None, finder=find_course_code):
    seen = {}

    def engine(target, *, config):
        seen["config"] = config
        return output if output is not None else an_output()

    result = extract_ocr(
        file_row=FILE_ROW, path=Path("/corpus/hw5-photographed.pdf"),
        policy=OPEN_POLICY, ocr_engine=engine,
        config=FIXTURE_CONFIG if config is None else config,
        find_structured_strings=finder, now=FIXED_CLOCK, context_window=20)
    return result, seen


def test_every_observation_conforms_to_p4s_shape(sink):
    result, _ = run_it()
    sink.write(result)
    sink.conforms()


def test_all_nine_section_2_7_fields_have_a_home_and_are_populated(sink):
    # Done-means 9, and the closing of P5 Open question 2.
    assert len(PERSISTED_FIELDS) == 9
    assert set(FIELD_HOMES) == set(PERSISTED_FIELDS)

    result, _ = run_it()
    run_id = sink.write(result)
    row = sink.run_for(run_id)
    unit = sink.units_for(run_id)[0]
    found = sink.observations_for(run_id)[0]

    assert row["extractor_name"] == "ocr.apple_vision"          # provider
    assert row["extractor_version"] == "19.1"                   # version
    assert row["config"]["languages"] == ["en-US"]              # languages
    assert row["config_fingerprint"] == fingerprint(FIXTURE_CONFIG)  # configuration
    assert unit["container_path"][0] == {"kind": "page", "index": 1,
                                         "label": None}         # page reference
    assert unit["text"] == RECOGNIZED                            # raw recognized text
    assert found["location"]["region"] == {"x": 0.1, "y": 0.2, "width": 0.8,
                                           "height": 0.05}       # bounding box
    assert found["confidence"] == 0.94                           # confidence
    assert row["completeness"] == "complete"                     # complete or capped
    assert row["coverage"] == {"units": "pages", "processed": 1, "total": 1}


def test_the_ocr_specific_fields_are_never_on_the_observation():
    # P5 Open question 2 is CLOSED. Re-opening it is the mistake this test prevents.
    result, _ = run_it()
    for observation in result.observations:
        for name in ("provider", "languages", "config", "capped", "dpi",
                     "ocr_provider", "recognition"):
            assert name not in observation, name


def test_raw_recognized_text_is_a_unit_and_lives_nowhere_else(sink):
    # G1: one home for bulk text.
    result, _ = run_it()
    run_id = sink.write(result)
    assert [u["text"] for u in sink.units_for(run_id)] == [RECOGNIZED]
    assert all(o["raw_value"] != RECOGNIZED for o in sink.observations_for(run_id))


def test_the_span_indexes_into_the_unit_its_container_names(sink):
    result, _ = run_it()
    run_id = sink.write(result)
    found = sink.observations_for(run_id)[0]
    assert found["raw_value"] == "BUSIB 4300"
    assert found["location"]["zone"] == "ocr"
    unit = sink.units_for(run_id)[0]
    span = found["location"]["text_span"]
    assert unit["text"][span["start"]:span["end"]] == "BUSIB 4300"


def test_an_image_region_addresses_by_region_when_there_is_no_page(sink):
    output = an_output(regions=(OcrRegion(page=None, region=2, text="Receipt",
                                          confidence=0.7),),
                       pages_processed=1, pages_total=1)
    result, _ = run_it(output=output, finder=lambda text: ())
    run_id = sink.write(result)
    assert sink.units_for(run_id)[0]["container_path"] == (
        {"kind": "region", "index": 2, "label": None},)


def test_a_screenshot_with_no_structured_strings_is_complete_with_zero_rows(sink):
    result, _ = run_it(finder=lambda text: ())
    run_id = sink.write(result)
    assert sink.observations_for(run_id) == []
    assert sink.run_for(run_id)["completeness"] == "complete"
    assert sink.units_for(run_id)[0]["text"] == RECOGNIZED
    sink.conforms()


def test_the_provider_is_the_engines_and_p5_spells_none():
    # S1: Apple Vision is the one engine §2.7 names and the whole of v1's scope, and
    # §2.7's first persisted field is that the PROVIDER reports its own name.
    assert extractor_name_for("apple-vision") == "ocr.apple_vision"
    # The engine still supplies the name -- a different engine gets a different one.
    assert extractor_name_for("tesseract") == "ocr.tesseract"
    assert analysis_tier_for("ocr.apple-vision") == ANALYSIS_TIER == "ocr"
    # Scoped to real module-level constants, NOT to `__doc__`: the docstring quotes
    # §2.7 and names the engine, and a guard that matched prose would fail on the
    # very sentence it exists to enforce.
    values = [value for name, value in vars(ocr_module).items()
              if not name.startswith("__") and isinstance(value, str)]
    for value in values:
        assert "vision" not in value.lower(), value
        assert "tesseract" not in value.lower(), value


def test_p5_holds_no_dpi_no_language_and_no_confidence_threshold():
    # §2.7 Deferred: the language list, and "a practical rendering resolution such
    # as 200 DPI" is an example. Every value is the caller's.
    for name, value in vars(ocr_module).items():
        if name.startswith("__"):
            continue
        assert not isinstance(value, (int, float)) or isinstance(value, bool), name
    parameter = inspect.signature(extract_ocr).parameters["config"]
    assert parameter.default is inspect.Parameter.empty


def test_the_configuration_reaches_the_engine_and_changes_the_cache_key():
    # §3.4: "Content hash + extractor version + `analysis_tier`, plus provider,
    # version and configuration for OCR."
    _, seen = run_it()
    assert seen["config"] == FIXTURE_CONFIG

    other = dict(FIXTURE_CONFIG, languages=["ja-JP"])
    keys = set()
    for config in (FIXTURE_CONFIG, other):
        result, _ = run_it(config=config)
        keys.add(cache_key(content_hash=result.run["content_hash"],
                           extractor_name=result.run["extractor_name"],
                           extractor_version=result.run["extractor_version"],
                           analysis_tier=result.run["analysis_tier"],
                           config_fingerprint=result.run["config_fingerprint"]))
    assert len(keys) == 2


def test_the_four_hundred_page_book_is_capped_and_keeps_its_text(sink):
    # The SPEC's `scanned-book-400pp.pdf`. §8.6: "A capped OCR run keeps its partial
    # text and is flagged capped — partial evidence is allowed, misrepresented
    # evidence is not."
    regions = tuple(a_page(number=n, text=f"page {n} text") for n in range(1, 51))
    output = an_output(regions=regions, pages_processed=50, pages_total=400,
                       capped=True)
    result, _ = run_it(output=output, finder=lambda text: ())
    run_id = sink.write(result)
    row = sink.run_for(run_id)
    assert row["completeness"] == "capped"
    assert row["completeness"] != "complete"
    assert row["coverage"] == {"units": "pages", "processed": 50, "total": 400}
    assert len(sink.units_for(run_id)) == 50
    sink.conforms()


def test_p5_holds_no_page_cap_of_its_own():
    # §8.6's ceilings are configuration (G4); the engine was given them and reports
    # that it stopped. Nothing in E6 decides to stop.
    source_names = [name for name in vars(ocr_module) if not name.startswith("__")]
    for token in ("MAX_", "_LIMIT", "CEILING", "THRESHOLD", "PAGE_CAP"):
        assert not [n for n in source_names if token in n], token


def test_the_same_content_and_config_produce_the_same_observations(sink):
    first = sink.write(run_it()[0])
    second = sink.write(run_it()[0])
    strip = lambda rows: [{k: v for k, v in r.items() if k != "run_id"} for r in rows]
    assert strip(sink.observations_for(first)) == strip(sink.observations_for(second))


def test_no_extractor_is_reachable_inside_a_protected_container():
    policy = SafetyPolicy(is_protected_container=lambda path: True,
                          is_dataless=lambda path: False)
    with pytest.raises(ProtectedContainerRefused):
        extract_ocr(file_row=FILE_ROW,
                    path=Path("/System/Library/Thing/scan.pdf"), policy=policy,
                    ocr_engine=lambda target, *, config: pytest.fail("engine ran"),
                    config=FIXTURE_CONFIG, find_structured_strings=lambda text: (),
                    now=FIXED_CLOCK, context_window=20)


def test_a_dataless_file_is_never_ocred():
    policy = SafetyPolicy(is_protected_container=lambda path: False,
                          is_dataless=lambda path: True)
    with pytest.raises(DatalessRefused):
        extract_ocr(file_row=FILE_ROW, path=Path("/corpus/hw5-photographed.pdf"),
                    policy=policy,
                    ocr_engine=lambda target, *, config: pytest.fail("engine ran"),
                    config=FIXTURE_CONFIG, find_structured_strings=lambda text: (),
                    now=FIXED_CLOCK, context_window=20)


# --- One engine, one extractor_name (stress test 2026-08-21) ------------------
#
# `extractor_name_for` concatenated the provider string verbatim, so an engine
# reporting `apple-vision` produced `ocr.apple-vision` while P4's nineteen fixtures
# and P2's examples say `ocr.apple_vision`. `extractor_name` is an input to
# `observation_key`, to §3.4's cache key and to rule 8's replay key, so two spellings
# of ONE engine are two citation handles, two cache entries and two replay sets --
# the same defect as the two `config_fingerprint` computations, one layer up.
#
# P5 still spells no provider name: the engine reports it. What P5 refuses is to let
# two spellings of one reported name become two identities.

def test_two_spellings_of_one_engine_are_one_extractor_name():
    from extractors.ocr import extractor_name_for
    names = {extractor_name_for(p) for p in
             ("apple-vision", "apple_vision", "Apple Vision", "APPLE-VISION")}
    assert names == {"ocr.apple_vision"}


def test_the_pinned_spelling_is_the_one_p4s_fixtures_carry():
    from extractors.ocr import extractor_name_for
    from evidence_shape.fixtures import by_number
    ocr_fixture = next(f for f in (by_number(n) for n in range(1, 20))
                       if f.run.analysis_tier == "ocr")
    assert extractor_name_for("apple-vision") == ocr_fixture.run.extractor_name


def test_two_genuinely_different_engines_stay_two_names():
    from extractors.ocr import extractor_name_for
    assert extractor_name_for("apple-vision") != extractor_name_for("tesseract")
