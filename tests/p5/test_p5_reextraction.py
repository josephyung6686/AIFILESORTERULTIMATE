# tests/p5/test_p5_reextraction.py
"""Done-means 12 — §8.2 supersession, §8.7's re-run on demand, §8.8's plan
independence, and SPEC Open question 6 held open."""
import importlib
import inspect
from pathlib import Path

import pytest

import extractors
from extractors.ocr import OcrOutput, OcrRegion, extract_ocr
from extractors.reading import StructuredString
from extractors.runs import cache_key
from extractors.safety import SafetyPolicy
from extractors.shape import fingerprint

from conftest import FIXED_CLOCK

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)
FILE_ROW = {"file_id": "f-scan", "content_hash": "bcbb377bc839704c4e4ccf7781cce3dcc88cc8a288c9eebbffa245a3476c56e9",
            "filename": "transcript-scan.pdf"}
CONFIG = {"recognition": "accurate", "languages": ["en-US"]}

GARBLED = "Ui1iversity 0f Cl1icago"
RECOVERED = "University of Chicago"

SOURCE_DIR = Path(extractors.__file__).parent


def p5_modules():
    return [importlib.import_module(f"extractors.{path.stem}")
            for path in sorted(SOURCE_DIR.glob("*.py")) if path.stem != "__init__"]


def find_university(text: str):
    at = text.find("University of Chicago")
    return (StructuredString(kind="identifier", start=at, end=at + 21),) if at != -1 else ()


def an_ocr_pass(*, text, provider_version, path="/corpus/transcript-scan.pdf"):
    output = OcrOutput(provider="apple-vision", provider_version=provider_version,
                       regions=(OcrRegion(page=1, region=1, text=text,
                                          confidence=0.5),),
                       pages_processed=1, pages_total=1)
    return extract_ocr(file_row=FILE_ROW, path=Path(path), policy=OPEN_POLICY,
                       ocr_engine=lambda target, *, config: output, config=CONFIG,
                       find_structured_strings=find_university, now=FIXED_CLOCK,
                       context_window=20)


def test_section_8_2s_own_example_both_records_remain_available(sink):
    first = sink.write(an_ocr_pass(text=GARBLED, provider_version="18.0"))
    second = sink.write(an_ocr_pass(text=RECOVERED, provider_version="19.1"),
                        supersede_reason="a later engine recovered readable text")

    assert first != second
    assert [r["run_id"] for r in sink.runs] == [first, second]
    assert sink.run_for(first)["extractor_version"] == "18.0"
    assert sink.run_for(second)["extractor_version"] == "19.1"
    # The first pass's unreadable text is still reachable.
    assert sink.units_for(first)[0]["text"] == GARBLED
    assert sink.units_for(second)[0]["text"] == RECOVERED
    # And the recovered university name exists only on the second. The FIRST pass
    # now carries its own garbled text as evidence, which is §8.2's point rather
    # than a break in it: "both records remain available", and until 2026-09-04 the
    # unreadable pass was available only as a text unit no reader reaches. What must
    # stay true is that the garbled run never claims the recovered name.
    first_rows = [o["raw_value"] for o in sink.observations_for(first)]
    assert first_rows == [GARBLED], first_rows
    assert RECOVERED not in first_rows
    second_rows = [o["raw_value"] for o in sink.observations_for(second)]
    assert second_rows == [RECOVERED], second_rows
    # ONE row, not two, and P4 D10 is why: "one observation per (run, exact raw
    # value, zone)". Here the whole recognised passage IS the found string -- one
    # region holding exactly `University of Chicago` -- so the span-carrying match
    # and the span-less passage are the same value in the same `ocr` zone and
    # `ExtractionResult.__post_init__` collapses them. The survivor is the FIRST in
    # document order, which is the span-carrying row that existed before 2026-09-04.
    # So the passage adds a row only when it says something the matches did not.
    assert sink.observations_for(second)[0]["location"]["text_span"] is not None
    sink.conforms()


def test_both_runs_text_units_survive(sink):
    # Done-means 12, in G1's terms: bulk text has one home PER RUN, not one home
    # per file that a re-run overwrites.
    first = sink.write(an_ocr_pass(text=GARBLED, provider_version="18.0"))
    second = sink.write(an_ocr_pass(text=RECOVERED, provider_version="19.1"))
    # Two units per run since `104` R-171: the region's, and the whole passage's
    # own (SF-1's docx shape). Each run keeps both; neither run overwrites the other.
    assert len(sink.text_units) == 2 * 2
    assert {u["run_id"] for u in sink.text_units} == {first, second}
    assert all(sum(u["run_id"] == run for u in sink.text_units) == 2
               for run in (first, second))


def test_p5_supplies_the_reason_and_sets_no_supersede_column(sink):
    reason = "a later engine recovered readable text"
    run_id = sink.write(an_ocr_pass(text=RECOVERED, provider_version="19.1"),
                        supersede_reason=reason)
    assert sink.supersessions == [(run_id, reason)]
    for observation in sink.observations:
        for column in ("supersedes", "superseded_by", "supersede_reason",
                       "preferred"):
            assert column not in observation, column


def test_an_extractor_upgrade_changes_the_cache_key():
    keys = {cache_key(content_hash="sha256:scan", extractor_name="ocr.apple-vision",
                      extractor_version=version, analysis_tier="ocr",
                      config_fingerprint=fingerprint(CONFIG))
            for version in ("18.0", "19.1")}
    assert len(keys) == 2


def test_a_rename_is_free():
    # §3.4: there is no path in the key, and that absence IS the guarantee.
    assert "path" not in inspect.signature(cache_key).parameters
    moved = an_ocr_pass(text=RECOVERED, provider_version="19.1",
                        path="/corpus/renamed/somewhere-else.pdf")
    stayed = an_ocr_pass(text=RECOVERED, provider_version="19.1")
    key = lambda result: cache_key(
        content_hash=result.run["content_hash"],
        extractor_name=result.run["extractor_name"],
        extractor_version=result.run["extractor_version"],
        analysis_tier=result.run["analysis_tier"],
        config_fingerprint=result.run["config_fingerprint"])
    assert key(moved) == key(stayed)


def test_a_configuration_change_makes_the_re_run_auditable():
    keys = set()
    for languages in (["en-US"], ["en-US", "ja-JP"]):
        config = dict(CONFIG, languages=languages)
        keys.add(cache_key(content_hash="sha256:scan",
                           extractor_name="ocr.apple-vision",
                           extractor_version="19.1", analysis_tier="ocr",
                           config_fingerprint=fingerprint(config)))
    assert len(keys) == 2


def test_no_p5_record_and_no_p5_function_knows_about_a_plan():
    # §8.8: "The evidence database remains shared across plan versions."
    for module in p5_modules():
        for name, value in vars(module).items():
            if name.startswith("__"):
                continue
            assert "plan" not in name.lower(), f"{module.__name__}.{name}"
            if inspect.isfunction(value) and value.__module__ == module.__name__:
                parameters = inspect.signature(value).parameters
                assert not [p for p in parameters if "plan" in p.lower()], name


def test_p5_publishes_no_deletion_of_any_kind():
    # SPEC Open question 6 is OPEN: whether reclassifying a file as private deletes
    # P5's stored observations and their text units, or only gates them, is §8.4's
    # to settle and P7's to own. P5 answers it nowhere.
    for module in p5_modules():
        for name, value in vars(module).items():
            if name.startswith("__") or not callable(value):
                continue
            for token in ("delete", "purge", "redact", "erase", "overwrite",
                          "scrub"):
                assert token not in name.lower(), f"{module.__name__}.{name}"


def test_re_extraction_needs_nothing_but_the_call():
    # §8.7's first obligation: P5 can be re-run over already-extracted content at any
    # time. Every extractor is a pure function of its arguments — no run registry, no
    # "already extracted" check, nothing to reset.
    parameters = inspect.signature(extract_ocr).parameters
    assert not {"force", "overwrite", "reextract", "if_changed"} & set(parameters)
