# tests/p4/test_p4_raw1.py
"""Done-means 4, at the layer that ships: RAW-1 through the validator six extractor
authors run as their gate, on a CJK fixture and an emoji fixture (D4's code-point
unit).

Task 8 proves the same property on `check_span_anchor`, the primitive. This file
proves that `check_run` — the call an extractor author actually makes — enforces it as
rule 5, on the two scripts D4 was chosen for.
"""
from evidence_shape.conformance import check_run
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.text_units import TextUnit

#: §2.7 requires CJK. Every character here is one code point and three UTF-8 bytes.
CJK_PAGE = "提出書類は慶應義塾大学の入学課に送付してください。締切は二〇二六年三月三十一日です。"
CJK_VALUE = "慶應義塾大学"

#: One astral-plane emoji is ONE code point and TWO UTF-16 units, so an offset
#: counted in UTF-16 lands in the middle of the character and RAW-1 fails.
EMOJI_PAGE = "Submitted 🎓 to Columbia University"
EMOJI_VALUE = "Columbia"


def _run(run_id="r1"):
    return ExtractionRun(
        run_id=run_id, file_id="f1", content_hash="sha256:abc",
        extractor_name="ocr.apple_vision", extractor_version="2.4.1",
        source_type="ocr", analysis_tier="ocr",
        config={"languages": ["ja", "en"]}, completeness="complete",
        started_at="2026-08-19T14:00:00+00:00")


def _pair(page, value, *, start=None, end=None):
    start = page.index(value) if start is None else start
    end = start + len(value) if end is None else end
    observation = Observation(
        file_id="f1", content_hash="sha256:abc", extractor_name="ocr.apple_vision",
        extractor_version="2.4.1", source_type="ocr", raw_value=value,
        location=Location("ocr", (Segment("page", 1),),
                          text_span=TextSpan(start, end)),
        occurrence_count=1, observed_at="2026-08-19T14:03:22+00:00",
        reliability="possible", run_id="r1")
    return [observation], [TextUnit(run_id="r1", container_path=(Segment("page", 1),),
                                    text=page)]


def test_raw_1_holds_through_the_gate_on_a_cjk_fixture():
    observations, units = _pair(CJK_PAGE, CJK_VALUE)
    assert check_run(_run(), observations, units) == ()


def test_a_byte_offset_into_the_cjk_fixture_fails_the_gate():
    # The same value addressed in UTF-8 bytes, which is what a naive extractor would
    # emit. D4 counts code points precisely so this is a failure and not a silent
    # mis-citation.
    byte_start = len(CJK_PAGE[:CJK_PAGE.index(CJK_VALUE)].encode("utf-8"))
    observations, units = _pair(CJK_PAGE, CJK_VALUE, start=byte_start,
                                end=byte_start + len(CJK_VALUE.encode("utf-8")))
    violations = check_run(_run(), observations, units)
    assert [violation.rule for violation in violations] == [5]
    assert "RAW-1" in violations[0].message


def test_raw_1_holds_through_the_gate_across_an_astral_emoji():
    observations, units = _pair(EMOJI_PAGE, EMOJI_VALUE)
    assert check_run(_run(), observations, units) == ()


def test_a_utf_16_offset_across_an_astral_emoji_fails_the_gate():
    # In UTF-16 the emoji occupies two units, so every offset after it is one too
    # large. Nothing in this package converts, which is why the failure is visible.
    utf_16_start = EMOJI_PAGE.index(EMOJI_VALUE) + 1
    observations, units = _pair(EMOJI_PAGE, EMOJI_VALUE, start=utf_16_start,
                                end=utf_16_start + len(EMOJI_VALUE))
    violations = check_run(_run(), observations, units)
    assert [violation.rule for violation in violations] == [5]
    assert "RAW-1" in violations[0].message


def test_the_stored_length_is_counted_in_code_points_not_bytes():
    _, units = _pair(CJK_PAGE, CJK_VALUE)
    assert units[0].length == len(CJK_PAGE)
    assert units[0].length != len(CJK_PAGE.encode("utf-8"))
