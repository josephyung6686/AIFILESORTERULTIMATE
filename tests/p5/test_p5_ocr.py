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
                     # P4's region shape: (x, y, w, h, unit). This fixture said
                     # `width`/`height` and carried no `unit` at all, so every
                     # OCR observation it produced held a region P4 could not
                     # parse -- and seven tests passed on it, because nothing
                     # validated at the emitter and the P4 stub dropped the field.
                     box={"x": 0.1, "y": 0.2, "w": 0.8, "h": 0.05, "unit": "norm"},
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
    # The fingerprint is of the config the RUN stored, which is the engine's config
    # plus B4's context budget: "the context budget goes in the run's `config` so it
    # is fingerprinted". Restating the engine's half here would fingerprint less than
    # the run was configured with.
    assert row["config_fingerprint"] == fingerprint(row["config"])  # configuration
    assert row["config"] == {**FIXTURE_CONFIG, "context_window": 20}
    assert unit["container_path"][0] == {"kind": "page", "index": 1,
                                         "label": None}         # page reference
    assert unit["text"] == RECOGNIZED                            # raw recognized text
    assert found["location"]["region"] == {"x": 0.1, "y": 0.2, "w": 0.8,
                                           "h": 0.05, "unit": "norm"}   # bounding box
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


def test_raw_recognized_text_is_a_unit_and_reaches_evidence_exactly_once(sink):
    """G1's "one home for bulk text" -- and the ONE deliberate exception §2.4 forces.

    The unit is still the home: `text_units` carries the recognised text and every
    span-carrying observation indexes into it. What changed on 2026-09-04 is that a
    SECOND, span-less copy is emitted as evidence, because the recogniser scans
    observations and never text units (`recognition/detector.py`: "a detector that
    pulled whole text units would be a second materialisation locus"). Without it,
    everything Apple Vision read off a screenshot was stored and unreachable.

    `pdf.py` and `docx.py` made this same exception first and for the same reason.
    Exactly one such row, so the exception cannot quietly become the rule.

    **`104` R-171 (9 Sep 2026): the passage has its OWN text unit as well.** Per
    region the unit list held the regions alone; the whole passage now stands in
    `text_units` at its own container path too, which is SF-1's docx shape and the
    row `resolve.materialise` needs to report the passage's length, so that
    `items.check_item` can call it a whole document past the ceiling and
    `opening_reading_for` can cut its opening. A second copy of the text in
    `text_units`, deliberately; still ONE evidence row.
    """
    result, _ = run_it()
    run_id = sink.write(result)
    units = [u["text"] for u in sink.units_for(run_id)]
    assert units.count(RECOGNIZED) == 2, units
    assert units == [RECOGNIZED, RECOGNIZED] or sorted(units) == sorted(
        [RECOGNIZED, RECOGNIZED]), units
    whole = [o for o in sink.observations_for(run_id) if o["raw_value"] == RECOGNIZED]
    assert len(whole) == 1, "the recognised text reaches evidence once, or not at all"
    assert whole[0]["location"]["text_span"] is None
    assert whole[0]["location"]["container_path"] == ()


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


def test_a_screenshot_with_no_structured_strings_still_yields_what_it_says(sink):
    """THE MEASURED DEFECT, and this test used to assert it as correct behaviour.

    Its old name was `..._is_complete_with_zero_rows` and it passed: a screenshot
    whose recognised text held no URL, no email and no DOI produced a `complete` run,
    a text unit, and NO EVIDENCE AT ALL. §2.7 calls OCR "the main way screenshots and
    opaque loose images become understandable to the pre-sorting engine", and the
    engine reads evidence.

    Measured over the owner's 199-file corpus on 2026-09-04: OCR ran on 52 files and
    produced 2,192 text units for one PDF alone against 17 observations. Eleven image
    files -- regression-line charts, WhatsApp saves, screen captures -- carried 14 to
    27 recognised text units EACH and emitted zero prose. The text was read off the
    pixels, stored, and thrown away.
    """
    result, _ = run_it(finder=lambda text: ())
    run_id = sink.write(result)
    rows = sink.observations_for(run_id)

    assert rows, "OCR read this screenshot and emitted nothing a reader can reach"
    assert [r["raw_value"] for r in rows] == [RECOGNIZED]
    assert sink.run_for(run_id)["completeness"] == "complete"
    assert sink.units_for(run_id)[0]["text"] == RECOGNIZED
    sink.conforms()


def test_the_recognised_text_stays_in_the_always_local_ocr_zone(sink):
    """§8.4 member 3 is `ocr_output` and it NEVER leaves the device.

    `privacy.vocabulary.ALWAYS_LOCAL_ZONES` gained `"ocr"` on 2026-09-04 for exactly
    this data, and every release door reads the zone: `privacy/items.py` refuses to
    construct an excerpt addressing one, and `model_facts.py` and `model_placement.py`
    both check before sending. Emitting the whole recognised text as `body` -- the
    zone `pdf.py` and `docx.py` use for their own prose -- would have handed a scanned
    identity document to a cloud dossier through a door that was already closed.

    Asserted at the emitter as well as at the gate, because the gate cannot refuse a
    zone the emitter never wrote.
    """
    from privacy.vocabulary import ALWAYS_LOCAL_ZONES

    result, _ = run_it(finder=lambda text: ())
    run_id = sink.write(result)

    for row in sink.observations_for(run_id):
        assert row["location"]["zone"] == "ocr", row
        assert row["location"]["zone"] in ALWAYS_LOCAL_ZONES


def test_several_lines_arrive_as_one_readable_passage(sink):
    """Apple Vision returns ONE REGION PER LINE, and that is why this is one row.

    A term the recogniser holds -- `vaccination record`, `medical record` -- routinely
    straddles a line break on a scanned form. Emitting one observation per region
    would give the detector twenty one-line strings and no passage in which those two
    words are ever adjacent, which is the same starvation in a new shape.
    """
    output = an_output(regions=(a_page(number=1, text="COVID-19"),
                                OcrRegion(page=1, region=2, text="Vaccination"),
                                OcrRegion(page=1, region=3, text="Record")),
                       pages_processed=1, pages_total=1)
    result, _ = run_it(output=output, finder=lambda text: ())
    run_id = sink.write(result)

    rows = [r["raw_value"] for r in sink.observations_for(run_id)]
    assert len(rows) == 1, f"one passage per file, got {len(rows)}"
    assert "Vaccination\nRecord" in rows[0], rows


def test_the_passage_carries_its_box_and_its_confidence(sink):
    """`104` §18.2 gap 17, loss (d): §2.7's two fields reached one row and not the one.

    §2.7's nine persisted fields include "locations or bounding boxes where
    available" and "confidence information", and `FIELD_HOMES` maps both onto records
    P4 already publishes -- `location.region` and `evidence.confidence`. They were
    attached inside the structured-string loop alone, so the passage row R-171 added
    -- the ONE row the recogniser actually scans, and the one §8.4 redacts against --
    carried neither. A screenshot's whole reading had no location and no confidence
    while every line it was built from had both.

    THE BOX IS THE UNION AND THE CONFIDENCE IS THE MINIMUM, and both are statements
    the regions support. `passage_region` and `passage_confidence` argue why; the
    tests below are the two conditions.

    SABOTAGE: drop `region=` and `confidence=` from the passage observation, or
    change `min` to a mean -- the mean asserts a confidence no line reported.
    """
    output = an_output(regions=(
        OcrRegion(page=1, region=1, text="COVID-19",
                  box={"x": 0.1, "y": 0.8, "w": 0.3, "h": 0.05, "unit": "norm"},
                  confidence=0.94),
        OcrRegion(page=1, region=2, text="Vaccination Record",
                  box={"x": 0.2, "y": 0.6, "w": 0.5, "h": 0.05, "unit": "norm"},
                  confidence=0.61)))
    result, _ = run_it(output=output, finder=lambda text: ())
    run_id = sink.write(result)

    rows = sink.observations_for(run_id)
    assert len(rows) == 1
    passage = rows[0]
    assert passage["confidence"] == pytest.approx(0.61), (
        "the minimum is the one aggregate every region asserts: no line in this "
        "passage was read below it")
    # The smallest rectangle containing both lines. x: 0.1..0.7, y: 0.6..0.85.
    assert passage["location"]["region"] == {
        "x": pytest.approx(0.1), "y": pytest.approx(0.6),
        "w": pytest.approx(0.6), "h": pytest.approx(0.25), "unit": "norm"}


def test_a_passage_spanning_pages_carries_no_box_and_keeps_its_confidence(sink):
    """The structural condition on loss (d)'s box, and there is no number in it.

    The passage is ONE string over the whole file. A rectangle unioned across pages 1
    and 7 of a scanned book bounds nothing that exists, so it is not written -- and a
    reading with no box is honest where a reading with a false box is not. The
    confidence is unaffected: "no line was read below this" is true however many
    pages the lines are spread over.

    SABOTAGE: delete the `len(pages) != 1` guard in `passage_region`.
    """
    output = an_output(regions=(
        OcrRegion(page=1, region=1, text="Chapter one",
                  box={"x": 0.1, "y": 0.8, "w": 0.3, "h": 0.05, "unit": "norm"},
                  confidence=0.9),
        OcrRegion(page=7, region=1, text="Chapter seven",
                  box={"x": 0.1, "y": 0.8, "w": 0.3, "h": 0.05, "unit": "norm"},
                  confidence=0.8)),
        pages_processed=7, pages_total=7)
    result, _ = run_it(output=output, finder=lambda text: ())
    passage = sink.observations_for(sink.write(result))[0]

    assert passage["location"]["region"] is None
    assert passage["confidence"] == pytest.approx(0.8)


def test_a_passage_whose_engine_reported_neither_carries_neither(sink):
    """An absent box and an absent confidence stay absent.

    §2.7 asks for both "where available", and an engine that reports no confidence
    gets none invented for it -- which is the opposite of recording what it said. One
    region missing a box is enough to withhold the union: a union of the rest is
    SMALLER than the text it claims to bound, which is a false location rather than a
    partial one.

    SABOTAGE: make `passage_region` skip the regions with no box and union the rest.
    """
    output = an_output(regions=(
        OcrRegion(page=None, region=1, text="Receipt", box=None, confidence=None),
        OcrRegion(page=None, region=2, text="Total 41.20",
                  box={"x": 0.1, "y": 0.1, "w": 0.2, "h": 0.05, "unit": "norm"},
                  confidence=None)))
    result, _ = run_it(output=output, finder=lambda text: ())
    passage = sink.observations_for(sink.write(result))[0]

    assert passage["location"]["region"] is None
    assert passage["confidence"] is None


def test_an_engine_that_recognised_nothing_still_emits_nothing(sink):
    """§2.4: an empty result and a missing extractor are different facts. A photo of
    a wall has no text, and a row saying so would be an observation about an
    absence -- which P5 does not write."""
    result, _ = run_it(output=an_output(regions=(), pages_processed=1, pages_total=1),
                       finder=lambda text: ())
    run_id = sink.write(result)

    assert sink.observations_for(run_id) == []
    assert sink.run_for(run_id)["completeness"] == "complete"


def test_whitespace_only_recognition_is_not_a_passage(sink):
    output = an_output(regions=(OcrRegion(page=1, region=1, text="   \n  "),))
    result, _ = run_it(output=output, finder=lambda text: ())
    run_id = sink.write(result)

    assert sink.observations_for(run_id) == []


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
    # Fifty page units, plus the whole passage's own unit (`104` R-171).
    assert len(sink.units_for(run_id)) == 50 + 1
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


# --- two regions on one page -------------------------------------------------------


def test_each_region_on_a_page_is_separately_addressable():
    """P4 D3 makes the container path an ADDRESS, and every region of a paged
    document was given the same one.

    `extract_ocr` built `container_path` from `recognized.page` alone, so three
    regions on page 1 produced three `text_units` all addressed `page[1]`. The
    observations' spans index into "the unit their container path names" -- this
    module's own words -- and that name resolved to whichever unit was stored
    last.

    Every fixture in this file used `region=1`, one region per page, which is the
    one shape that cannot expose it. A REAL scanned page is always several
    regions: Apple Vision returns one per line of text.

    Found by running the command over a genuine image-only PDF. The run did not
    misfile anything -- it crashed, `NonConforming: raw_value 'PHYS1401' is not
    the substring at 0-8, which is 'Due Frid'`, and took the whole corpus with it.
    """
    output = an_output(regions=(
        OcrRegion(page=1, region=1, text="Homework 5 for BUSIB 4300, due 2026-07-17.",
                  box={"x": 0.1, "y": 0.8, "w": 0.8, "h": 0.05, "unit": "norm"},
                  confidence=0.9),
        OcrRegion(page=1, region=2, text="Columbia University, Spring 2026",
                  box={"x": 0.1, "y": 0.6, "w": 0.8, "h": 0.05, "unit": "norm"},
                  confidence=0.9),
    ))
    result, _ = run_it(output)

    paths = [unit["container_path"] for unit in result.text_units]
    assert len(paths) == len(set(map(str, paths))), (
        f"two regions of one page share an address: {paths}")


def test_an_observations_span_indexes_into_its_own_region():
    """The property the conformance rule actually checks, and the one that broke.

    Rule 5: `raw_value` must be the substring of the addressed unit at the stored
    span. With two regions sharing an address, the course code found at 15-25 of
    the FIRST region was checked against the SECOND -- which is shorter than the
    span, so it failed twice over.
    """
    output = an_output(regions=(
        OcrRegion(page=1, region=1, text="Homework 5 for BUSIB 4300, due 2026-07-17.",
                  box={"x": 0.1, "y": 0.8, "w": 0.8, "h": 0.05, "unit": "norm"},
                  confidence=0.9),
        OcrRegion(page=1, region=2, text="Short line",
                  box={"x": 0.1, "y": 0.6, "w": 0.8, "h": 0.05, "unit": "norm"},
                  confidence=0.9),
    ))
    result, _ = run_it(output)

    units = {str(unit["container_path"]): unit["text"]
             for unit in result.text_units}
    # SPAN-CARRYING ROWS ONLY, which is what rule 5 is about and what this test has
    # always been about -- `check_span_anchor` itself opens "rule 10 applies to an
    # observation with a non-null text_span". The whole-passage row added on
    # 2026-09-04 carries no span and no container by design, so there is no unit for
    # it to index into and no anchor for rule 5 to check; asserting one here would
    # be this test claiming a rule the conformance layer does not make.
    anchored = [o for o in result.observations
                if o["location"]["text_span"] is not None]
    assert anchored, "no span-carrying observation left to check the anchor on"
    for observed in anchored:
        text = units[str(observed["location"]["container_path"])]
        span = observed["location"]["text_span"]
        assert text[span["start"]:span["end"]] == observed["raw_value"]

    span_less = [o for o in result.observations
                 if o["location"]["text_span"] is None]
    assert [o["location"]["container_path"] for o in span_less] == [()], (
        "a span-less OCR observation that is NOT the whole passage has appeared; "
        "it would be an unanchored excerpt with a container nobody checks")


def test_the_passage_collapses_into_a_match_it_duplicates(sink):
    """P4 D10 applied to the new row, pinned because it is not obvious.

    "One observation per (run, exact raw value, zone)", applied in
    `ExtractionResult.__post_init__` for every extractor. When a region holds
    nothing but a found string, the whole-passage row and the structured-string row
    are the same value in the same `ocr` zone and become one -- the FIRST in
    document order, which is the span-carrying match that existed before this row
    did. The passage therefore costs a row only when it carries words the matches
    did not, which is the case it was added for.

    Nothing about release changes either way: every OCR row is `zone="ocr"`, which
    `ALWAYS_LOCAL_ZONES` refuses whatever its span says.
    """
    output = an_output(regions=(OcrRegion(page=1, region=1, text="BUSIB 4300",
                                          confidence=0.9),))
    result, _ = run_it(output=output)
    run_id = sink.write(result)

    rows = sink.observations_for(run_id)
    assert [r["raw_value"] for r in rows] == ["BUSIB 4300"]
    assert rows[0]["location"]["text_span"] is not None
    assert rows[0]["location"]["zone"] == "ocr"


# ----------------------------------------------------- §2.4's other outcome, here
def test_an_engine_with_no_decoder_records_unsupported_and_not_failed():
    """§2.4's two words, at the seam every other extractor already has.

    `extract_pdf`, `extract_docx`, `extract_structured_text`, `extract_long_tail` and
    `extract_image` all begin the same way: a reader that returns `None` means *"no
    reader exists for this format in this deployment"* and the run is `unsupported`.
    E6 was the one extractor with no such branch, so an engine that could not decode
    a format had only one way to say so -- raise -- and the dispatcher's catch turned
    every one of them into `failed`, which asserts the file is damaged.

    Measured on the owner's 199-file corpus, 2026-09-04: seven undamaged SVG logos
    recorded `ocr · failed · "no image could be decoded from ..."`. Seven false
    statements about a person's files, in the column §8.6's "18 files remain
    unreadable" sentence is computed from.
    """
    result = extract_ocr(
        file_row=FILE_ROW, path=Path("/corpus/logo.svg"), policy=OPEN_POLICY,
        ocr_engine=lambda target, *, config: None, config=FIXTURE_CONFIG,
        find_structured_strings=find_course_code, now=FIXED_CLOCK,
        context_window=20)

    assert result.run["completeness"] == "unsupported"
    assert result.run["analysis_tier"] == ANALYSIS_TIER
    # P4 conformance rule 9: `unsupported` carries zero observations. A text unit
    # would be worse -- it would put a reading in `text_units` for a file nothing read.
    assert result.observations == ()
    assert result.text_units == ()
    assert result.run["observation_count"] == 0
    # No `failure_reason`: nothing failed. A reason here would read as a failure,
    # which is exactly the confusion the two words exist to prevent.
    assert not result.run.get("failure_reason")


def test_the_unsupported_run_names_no_provider_it_never_heard_from():
    """§2.7's first two persisted fields are the PROVIDER's own name and version.

    An engine that declined reported neither, so neither may be invented. The run
    carries the family name with the provider left off -- `UNREPORTED_PROVIDER_NAME`,
    which already exists for the engine that raised before reporting -- and P5's own
    adapter version, which is the code that actually ran.
    """
    from extractors.ocr import UNREPORTED_PROVIDER_NAME, VERSION

    result = extract_ocr(
        file_row=FILE_ROW, path=Path("/corpus/logo.svg"), policy=OPEN_POLICY,
        ocr_engine=lambda target, *, config: None, config=FIXTURE_CONFIG,
        find_structured_strings=find_course_code, now=FIXED_CLOCK,
        context_window=20)

    assert result.run["extractor_name"] == UNREPORTED_PROVIDER_NAME
    assert result.run["extractor_version"] == VERSION
    assert "." not in UNREPORTED_PROVIDER_NAME, (
        "the family name must not collide with any real `ocr.<provider>`")
