# tests/integration/test_ocr_ceilings_reach_the_engine.py
"""R-35, P5's half -- §8.6's two per-file OCR ceilings, wired to the thing that stops.

**What was wrong, measured rather than asserted.** `cli._bootstrap` seeds 7 of P1's
17 published ceiling keys, and the four P5 names are not among them. That half was
already known. The half that matters more is that they were not consumed either:
`extractors/budgets.p5_ceilings` and `extractors/budgets.deferred_result` -- the
reader for those four keys and the constructor for a run a budget stopped -- had no
caller anywhere in `src/`. Seeding the keys alone would have changed nothing.

**The stopping machinery was already built.** `readers/ocr_vision.vision_ocr` honours
`page_cap` and `time_limit_seconds`, reports `capped=True` when either fired, and
`extractors/ocr.py` turns that into `completeness="capped"` with P4's own
`coverage {"processed": n, "total": m}`. `tests/readers/test_ocr_vision.py` has
proved the engine's half since it was written. The one missing link was that
`readers/deployment.VISION_CONFIG` carried languages, dpi and recognition level and
no ceiling, so `page_cap` and `time_limit` were `None` on every run this product has
made and neither limit could fire.

**Why a per-file ceiling and not the scan-level pair.** §8.6 names four P5 ceilings.
Two of them -- `ocr.max_time_per_scan` and `image.max_analysis_ops_per_scan` -- have
no enforcement point anywhere in `src/`: nothing accumulates a per-scan OCR clock and
nothing counts image operations. Seeding those two would publish a number nothing
obeys, which is precisely what `database_agent/budget.py` warns against in its own
first paragraph: "P1 holds and publishes values; P1 enforces none of them. Reading a
ceiling is not enforcing it." A test below asserts they stay unseeded, so the gap
stays visible instead of looking finished.

**The page number is measured.** Read over the owner's ground-truth corpus on
2026-09-06 with pdfium, no OCR and no model: 68 readable PDFs, median 2 pages, one
outlier at 287. A ceiling of 20 leaves 61 of 68 untouched; raising it to 50 buys two
more files and triples the worst case for the tail. The tail is exactly what §8.6's
"a large scanned textbook should not consume the same budget as hundreds of ordinary
PDFs" is about.
"""
from __future__ import annotations

import pathlib
import tempfile

import pytest

from database_agent.budget import CEILING_KEYS, get_ceiling
from database_agent.db import open_database

import cli

def _build_pdf():
    """`tests/readers/pdf_bytes.build_pdf`, loaded by path.

    `tests/` carries no `__init__.py` in every directory, so pytest puts each test
    directory on `sys.path` and `pdf_bytes` is importable from `tests/readers`
    only. Copying the builder here would give the engine's cap test and this one
    two different PDFs, and then a disagreement between them would be a fixture
    difference rather than a finding.
    """
    import importlib.util

    path = (pathlib.Path(__file__).resolve().parents[1] / "readers" / "pdf_bytes.py")
    spec = importlib.util.spec_from_file_location("_pdf_bytes_probe", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_pdf


build_pdf = _build_pdf()

#: The two §8.6 keys that now have both a value and something that obeys it.
ENFORCED = ("ocr.max_pages_per_file", "ocr.max_time_per_file")

#: The two that have a key and no enforcement point. Named so the gap is a fact in
#: the suite rather than an omission someone has to notice.
UNENFORCED = ("ocr.max_time_per_scan", "image.max_analysis_ops_per_scan")


@pytest.fixture()
def bootstrapped():
    directory = pathlib.Path(tempfile.mkdtemp())
    conn = open_database(directory / "agent.sqlite")
    cli._bootstrap(conn)
    yield conn
    conn.close()


@pytest.fixture()
def readers():
    """The readers the composition root actually builds, ceilings and all."""
    return cli.extraction_context().readers


# --- the value P1 publishes is the value the run uses --------------------------

def test_the_two_per_file_ocr_ceilings_are_seeded(bootstrapped):
    for key in ENFORCED:
        assert get_ceiling(bootstrapped, key) is not None, key


def test_what_p1_publishes_is_what_the_engine_is_given(bootstrapped, readers):
    # The failure this rules out is the quiet one: a ceiling stored at one number
    # and enforced at another makes the published value a lie, and P1's table is
    # where anyone would go to find out what bounded their run.
    assert get_ceiling(bootstrapped, "ocr.max_pages_per_file") == \
        readers.ocr_config["page_cap"]
    assert get_ceiling(bootstrapped, "ocr.max_time_per_file") == \
        readers.ocr_config["time_limit_seconds"]


def test_the_scan_level_pair_stays_unseeded_because_nothing_enforces_them(
        bootstrapped):
    """A published ceiling nothing obeys is worse than an absent one: it reads as
    a bound somebody chose. Both keys stay in `CEILING_KEYS` and stay unvalued
    until an enforcement point exists to give them."""
    for key in UNENFORCED:
        assert key in CEILING_KEYS
        assert get_ceiling(bootstrapped, key) is None, key


# --- the ceiling reaches the thing that stops ----------------------------------

def test_the_deployment_config_carries_both_ceilings(readers):
    assert "page_cap" in readers.ocr_config
    assert "time_limit_seconds" in readers.ocr_config


def test_a_ceiling_of_one_stops_a_three_page_document_and_says_so(tmp_path):
    """§8.6's ceiling of one, end to end through the real engine.

    Not a stub: the point of the item is that a number in `cli.py` reaches Vision,
    and a fake engine agreeing with the config would prove only that the config
    exists. `build_pdf` is the same helper `tests/readers/test_ocr_vision.py` uses
    for the engine's own cap test.
    """
    pytest.importorskip("Vision", reason="Apple Vision is macOS-only")
    pytest.importorskip("Quartz", reason="Apple Quartz is macOS-only")
    readers = cli.macos_readers(
        find_structured_strings=cli.find_structured_strings,
        spreadsheet_cell_ceiling=cli.SPREADSHEET_CELL_CEILING,
        ocr_page_ceiling=1, ocr_seconds_per_file=cli.OCR_SECONDS_PER_FILE)
    scan = build_pdf(tmp_path / "textbook.pdf", pages=3)

    output = readers.ocr_engine(scan, config=dict(readers.ocr_config))

    assert output.pages_processed == 1
    assert output.pages_total == 3
    # §2.4 forbids a partial read that calls itself complete. The engine reports
    # the stop; `extractors/ocr.py` is what turns this into `completeness="capped"`.
    assert output.capped is True


def test_a_document_inside_the_ceiling_is_not_reported_as_capped(tmp_path):
    # The control. A ceiling that marked every document partial would make the
    # `capped` count meaningless, which is the other way to lose §8.6's line.
    pytest.importorskip("Vision", reason="Apple Vision is macOS-only")
    pytest.importorskip("Quartz", reason="Apple Quartz is macOS-only")
    readers = cli.macos_readers(
        find_structured_strings=cli.find_structured_strings,
        spreadsheet_cell_ceiling=cli.SPREADSHEET_CELL_CEILING,
        ocr_page_ceiling=5, ocr_seconds_per_file=cli.OCR_SECONDS_PER_FILE)
    scan = build_pdf(tmp_path / "receipt.pdf", pages=2)

    output = readers.ocr_engine(scan, config=dict(readers.ocr_config))

    assert output.pages_processed == 2
    assert output.capped is False


# --- the ceiling that has to fire first ----------------------------------------

def test_ocr_stops_itself_before_the_pool_kills_the_worker():
    """The two clocks are related and the order between them is the whole point.

    R-50 gave `ProcessPool` a per-extraction ceiling that kills a worker wedged
    inside Vision, because a Python timeout cannot interrupt a C dispatch wait.
    That rescue costs the file everything: the worker dies holding whatever it had
    read. OCR's own per-file limit is checked between pages, so when it fires the
    run keeps the pages it finished and records `capped`. The in-process ceiling is
    therefore only useful if it is reached FIRST, and this is the assertion that
    keeps someone raising one of the two numbers from silently inverting them.
    """
    assert cli.OCR_SECONDS_PER_FILE < cli.EXTRACTION_SECONDS_PER_FILE


# --- §8.6's line names the ceiling ---------------------------------------------

def _capped_run(conn, *, source_type: str, run_id: str) -> None:
    """One `capped` run of one extractor family. Only the columns P4 requires."""
    conn.execute(
        "INSERT INTO extraction_runs (run_id, file_id, content_hash, "
        "extractor_name, extractor_version, source_type, analysis_tier, config, "
        "config_fingerprint, completeness, observation_count, started_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (run_id, "f-1", "h-1", f"fixture.{source_type}", "0.1.0", source_type,
         source_type, "{}", "fp-1", "capped", 0, "2026-09-06T12:00:00+00:00"))


def test_the_progress_line_names_the_ceiling_that_actually_fired(bootstrapped):
    """§8.6 requires the cause NAMED, and naming the wrong one is worse than the
    gap it replaces.

    THREE extractors write `capped` -- `ocr.py`, `pdf.py` and `long_tail.py` --
    under three different ceilings, and `review_surface.progress` buckets by state,
    so one bucket holds all three. A sentence that said "OCR stopped at 20 pages"
    for a spreadsheet that stopped at 2,000 cells would be a false cause printed
    with confidence. On the owner's own corpus the pdfium and spreadsheet ceilings
    are the two that had already fired before OCR had any ceiling at all.
    """
    _capped_run(bootstrapped, source_type="ocr", run_id="r-ocr")
    _capped_run(bootstrapped, source_type="spreadsheet", run_id="r-cells")

    sentence = cli._no_extractor_cause(bootstrapped)("capped")

    assert sentence is not None
    assert str(cli.OCR_PAGE_CEILING) in sentence
    assert str(cli.SPREADSHEET_CELL_CEILING) in sentence
    # The one that did NOT fire is not named, or the sentence is a list of every
    # ceiling this deployment holds rather than a cause.
    assert str(cli.PDF_PAGE_CEILING) not in sentence


def test_a_pdf_cap_is_not_reported_as_an_ocr_cap(bootstrapped):
    # The discriminating case. The first version of this fix named OCR for every
    # member of the bucket, and this is the test that would have caught it.
    _capped_run(bootstrapped, source_type="text_document", run_id="r-pdf")

    sentence = cli._no_extractor_cause(bootstrapped)("capped")

    assert str(cli.PDF_PAGE_CEILING) in sentence
    assert "OCR" not in sentence


def test_a_capped_bucket_with_no_recognised_ceiling_says_nothing_rather_than_guess(
        bootstrapped):
    """A future extractor that caps under a ceiling this file does not hold.
    P13's own sentence then says the cause is unrecorded, which is the truth."""
    _capped_run(bootstrapped, source_type="presentation", run_id="r-slides")

    assert cli._no_extractor_cause(bootstrapped)("capped") is None


def test_a_deferral_is_not_told_it_kept_what_it_read(bootstrapped):
    """`deferred` and `capped` are both ceiling states and only one of them read
    anything. `extractors/budgets.deferred_result` builds a run for an extractor
    the budget stopped BEFORE it started, so "what was read before stopping was
    kept" is false of it by definition.

    The unrouted row is what makes this test discriminating. Without it the
    function returns `None` for every label and the assertion passes whatever the
    code does; with it, the no-reader sentence is live and a deferral must not
    collect it -- a budget that stopped an extractor is not a routing failure.
    """
    bootstrapped.execute(
        "INSERT INTO extraction_routing (file_id, content_hash, detected_format, "
        "declared_extension, disagree, source_type, source_type_candidates, "
        "extractor_name, router_version, observed_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
        ("f-2", "h-2", None, ".svg", 0, None, "[]", None, "0.1.0",
         "2026-09-06T12:00:00+00:00"))
    cause_for = cli._no_extractor_cause(bootstrapped)

    assert cause_for("deferred") is None
    # The control: the sentence this deferral must not be given IS live.
    assert cause_for("unreadable") is not None
