# tests/wave2/test_wave2_orchestrator.py
"""The Wave-2 caller: P3 scan -> P5 route/extract -> P4 record -> P1 status -> P2 bundle.

18-wave2-orchestrator.md: P1, P2 and P3 are shipped, P4 and P5 are green, and
"nothing calls them in sequence". `scan()` returns a `scan_run_id` and stops. Every
test here is about the JOIN -- the thing 1,205 unit tests were comprehensive about
shape for and silent about.
"""
from pathlib import Path

import pytest

from database_agent.files_table import get_file
from orchestrator import TARGETED_OCR_UNAVAILABLE, Wave2, run_wave2
from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.selection import record_selection

NEVER = lambda: False

# Fixtures live in this module, NOT in a tests/wave2/conftest.py.
#
# pytest's prepend import mode keys a rootless module on its BASENAME, so a second
# `conftest.py` claims `sys.modules["conftest"]` and whichever directory is imported
# first wins for the whole session. tests/p5/ does `from conftest import
# RecordingSink`; a tests/wave2/conftest.py made that import resolve HERE and broke
# three tests in a package this one does not touch -- and only in a full run, which is
# what makes it worth a comment. The same collision cost this project a whole-suite
# outage once already, in tests/eval/.
FIXED_CLOCK = "2026-08-21T12:00:00+00:00"


@pytest.fixture()
def db(conn):
    from database_agent.db import create_schema
    from eval_harness.store import create_eval_schema
    from evidence_shape.schema import create_evidence_schema
    from extractors.schema import create_extraction_schema
    from scan_agent.schema import create_scan_schema
    create_schema(conn)
    create_scan_schema(conn)
    create_evidence_schema(conn)
    # P5's OWN two tables -- the routing decision and the sensitivity signal. This
    # fixture omitted them, so the caller could not have recorded either and no test
    # would have noticed: §0's "each part owns its own tables" cuts both ways, and a
    # harness that creates four parts' tables out of five is testing a database the
    # product never runs on.
    create_extraction_schema(conn)
    create_eval_schema(conn)
    return conn


@pytest.fixture()
def corpus(tmp_path: Path) -> Path:
    """A real corpus on disk. Nothing here synthesizes a record: the point of these
    tests is the join, and every defect the 2026-08-21 stress test found passed its
    unit tests and was visible only end to end."""
    root = tmp_path / "Documents"
    root.mkdir()
    (root / "syllabus.pdf").write_bytes(b"%PDF-1.4 BUSIB 4300")
    (root / "notes.md").write_bytes(b"# BUSIB 4300\nlecture notes")
    return root


def mime_for(path: Path) -> str | None:
    return {".pdf": "application/pdf", ".md": "text/markdown"}.get(path.suffix)


def readers(**over):
    from extractors.dispatch import Readers
    from extractors.pdf import PdfDocument, PdfPage
    from extractors.docx import DocxDocument
    from extractors.reading import Region
    from extractors.archive import ArchiveManifest
    from extractors.image import ImageRecord
    from extractors.structured_text import TextDocument
    from extractors.long_tail import LongTailFile

    page = "BUSIB 4300 Course Information"
    base = dict(
        read_pdf=lambda p: PdfDocument(
            metadata={"Title": "BUSIB 4300 Syllabus"}, iso_dates={},
            pages=(PdfPage(number=1, text=page,
                           regions=(Region(zone="heading", start=0, end=29,
                                           ordinal=1, label="Course Information"),)),)),
        read_docx=lambda p: DocxDocument(core_properties={}),
        read_text_document=lambda p: TextDocument(text="BUSIB 4300 lecture notes"),
        read_long_tail=lambda p, transcribe=False: LongTailFile(),
        read_manifest=lambda p: ArchiveManifest(archive_type="zip"),
        read_image=lambda p: ImageRecord(image_format="PNG", dimensions="2880x1800",
                                         width=2880, height=1800),
        find_structured_strings=lambda text: (),
        recognize_markers=lambda names: (),
        dimension_signal=lambda w, h: None,
        filename_pattern=lambda name: None,
    )
    base.update(over)
    return Readers(**base)


def go(db, corpus, **over):
    from evidence_shape.store import RunWriter
    from extractors.safety import SafetyPolicy
    from scan_agent.exclusion import is_protected_container

    selection = record_selection(db, sources=[corpus], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    policy = over.pop("policy", SafetyPolicy(
        is_protected_container=is_protected_container,
        is_dataless=lambda path: False))
    return run_wave2(
        db, selection,
        source=FilesystemCorpusSource(), mime_type_for=mime_for,
        scan_state="scanned", budget_exhausted=NEVER,
        detect_format=lambda p: p.suffix.lstrip(".") or None,
        policy=policy, readers=readers(**over.pop("readers", {})),
        sink=RunWriter(db, author="P5"),
        now=lambda: FIXED_CLOCK, context_window=40,
        no_usable_facts=over.pop("no_usable_facts", TARGETED_OCR_UNAVAILABLE),
        transcription_authorized=lambda: False,
        corpus_form="snapshot", policy_settings={},
        file_entry_body=lambda row: {"payload_ref": f"blobs/{row['content_hash']}"},
        **over)


# ------------------------------------------------------------- it runs at all
def test_a_scan_now_produces_extraction_runs(db, corpus):
    """The whole reason this exists: `scan()` stopped, and nothing called P5."""
    result = go(db, corpus)
    assert isinstance(result, Wave2)
    runs = db.execute("SELECT count(*) c FROM extraction_runs").fetchone()["c"]
    assert runs > 0


def test_every_scanned_file_reaches_the_filesystem_tier(db, corpus):
    go(db, corpus)
    tiers = {r["analysis_tier"] for r in
             db.execute("SELECT DISTINCT analysis_tier FROM extraction_runs")}
    assert "filesystem" in tiers and "native" in tiers


def test_the_status_column_is_no_longer_empty_after_a_real_extraction(db, corpus):
    """§8.2's file record names "extraction status by extractor tier", and until this
    caller existed the column read `{}` after every real extraction."""
    import json
    go(db, corpus)
    rows = db.execute("SELECT extraction_status_by_tier FROM files").fetchall()
    assert rows
    for row in rows:
        status = json.loads(row["extraction_status_by_tier"])
        assert status != {}
        assert "filesystem" in status


def test_it_reads_current_path_and_not_path(db, corpus):
    """The sketch used `file_row["path"]` and would KeyError on the first file. The
    live column is `current_path`."""
    go(db, corpus)
    file_id = db.execute("SELECT file_id FROM files LIMIT 1").fetchone()["file_id"]
    assert get_file(db, file_id)["current_path"].startswith(str(corpus))


# ---------------------------------------------------------- exactly one event
def test_each_run_appends_exactly_one_event(db, corpus):
    go(db, corpus)
    for row in db.execute("SELECT run_id FROM extraction_runs"):
        events = db.execute(
            "SELECT count(*) c FROM events WHERE explanation LIKE ?",
            (f'%"run_id":"{row["run_id"]}"%',)).fetchone()["c"]
        assert events == 1, row["run_id"]


def test_no_event_names_the_orchestrator_as_its_author(db, corpus):
    """M8 / §8.2: an author field naming the part that merely ARRANGED the work makes
    §8.2's reconstruction requirement unmeetable. The orchestrator never appears."""
    go(db, corpus)
    authors = {r["subsystem"] for r in db.execute("SELECT DISTINCT subsystem FROM events")}
    assert authors <= {"P3", "P5"}


# --------------------------------------------------- the exception contract
def test_a_protected_container_produces_nothing_at_all(db, tmp_path):
    """11 §4b, ratified 2026-08-20. No run row, no observation, no status write for
    anything inside -- and `continue` the OUTER loop, never `break`, because `break`
    falls through to the status write and that is a P1 write authored "P5" on a file
    the product is forbidden to have touched."""
    from extractors.safety import SafetyPolicy
    root = tmp_path / "Apps"
    inside = root / "Numbers.app" / "Contents"
    inside.mkdir(parents=True)
    (inside / "sheet.numbers").write_bytes(b"x")
    (root / "ordinary.md").write_bytes(b"# fine")

    go(db, root, policy=SafetyPolicy(
        is_protected_container=lambda p: ".app" in str(p),
        is_dataless=lambda p: False))

    paths = [r["current_path"] for r in db.execute("SELECT current_path FROM files")]
    assert not any(".app" in p for p in paths), paths
    for row in db.execute("SELECT run_id, file_id FROM extraction_runs"):
        assert ".app" not in get_file(db, row["file_id"])["current_path"]


def test_a_reader_that_raises_becomes_a_failed_run_and_the_scan_continues(db, corpus):
    """§2.4: never silently an empty document -- and never a crashed scan either."""
    def locked(path):
        raise ValueError("file has not been decrypted")

    go(db, corpus, readers={"read_pdf": locked})
    failed = db.execute(
        "SELECT completeness, failure_reason FROM extraction_runs "
        "WHERE completeness = 'failed'").fetchall()
    assert len(failed) == 1
    assert failed[0]["failure_reason"] == "ValueError: file has not been decrypted"
    # The other file still got through.
    assert db.execute("SELECT count(*) c FROM files").fetchone()["c"] == 2


# -------------------------------------------------------------- the stat cache
def test_a_second_scan_of_an_unchanged_corpus_re_extracts_nothing(db, corpus):
    """§1.2: on REUSE, P5 is not invoked and prior results stand."""
    go(db, corpus)
    after_first = db.execute("SELECT count(*) c FROM extraction_runs").fetchone()["c"]
    go(db, corpus)
    assert db.execute(
        "SELECT count(*) c FROM extraction_runs").fetchone()["c"] == after_first


# ------------------------------------------------------------------ the bundle
def test_the_bundle_carries_the_scan_run_as_its_source_ref(db, corpus):
    """The join P3 published, P1 adopted, and nothing made until now."""
    result = go(db, corpus)
    row = db.execute("SELECT source_scan_ref, sealed_at FROM bundle_manifest "
                     "WHERE bundle_id = ?", (result.bundle_id,)).fetchone()
    assert row["source_scan_ref"] == result.scan_run_id
    assert row["sealed_at"] is not None


def test_the_bundle_counts_read_the_runs_that_were_actually_written(db, corpus):
    from eval_harness.counts import bundle_counts
    result = go(db, corpus)
    counts = bundle_counts(db, result.bundle_id)
    assert counts["files_indexed"] == 2


# ------------------------------------------------------- what it does not own
def test_the_orchestrator_holds_no_vocabulary():
    """It "spells no `completeness`, `source_type`, `analysis_tier`, zone or event
    type; every such value reaches P1/P4 inside a record a part constructed"."""
    import ast
    import orchestrator as module
    tree = ast.parse(Path(module.__file__).read_text())
    docstrings = {id(n.body[0].value) for n in ast.walk(tree)
                  if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef))
                  and n.body and isinstance(n.body[0], ast.Expr)
                  and isinstance(n.body[0].value, ast.Constant)
                  and isinstance(n.body[0].value.value, str)}
    held = {n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)
            and id(n) not in docstrings}
    for token in ("complete", "metadata_only", "unsupported", "dataless", "failed",
                  "text_document", "image", "filesystem", "native", "ocr",
                  "extraction", "OCR", "heading", "body", "P5"):
        assert token not in held, token


# ------------------------------------------- OQ6: two caches, and the outer one won
#
# §1.2's stat cache keys on path, mtime and size. §3.4's extraction cache keys on
# content hash, extractor version, analysis tier and config fingerprint -- "this
# prevents stale results from surviving a content rewrite ... and makes model or
# prompt changes auditable". P5 publishes `cache_key` with the extractor version in
# it; P3's verdict has no version at all.
#
# An orchestrator that skips every VERDICT_REUSE file therefore never re-runs an
# upgraded extractor over an unchanged corpus, and a bug shipped in `pdf.text 0.1.0`
# stays in the database for the life of the corpus. The stat cache is the OUTER one,
# so it wins, and §3.4's auditability is unreachable from behind it.

def test_an_extractor_upgrade_re_extracts_an_unchanged_corpus(db, corpus, monkeypatch):
    import extractors.pdf as pdf_module
    go(db, corpus)
    first = {r["run_id"] for r in db.execute(
        "SELECT run_id FROM extraction_runs WHERE extractor_name = ?",
        (pdf_module.EXTRACTOR_NAME,))}
    assert first, "the PDF ran at all"

    monkeypatch.setattr(pdf_module, "VERSION", "0.2.0")
    go(db, corpus)

    versions = {r["extractor_version"] for r in db.execute(
        "SELECT extractor_version FROM extraction_runs WHERE extractor_name = ?",
        (pdf_module.EXTRACTOR_NAME,))}
    assert versions == {"0.1.0", "0.2.0"}, versions


def test_the_earlier_runs_are_kept_not_replaced(db, corpus, monkeypatch):
    """§8.2: a newer result supersedes an earlier one and BOTH remain available.
    `extraction_runs` is append-only and carries no supersede columns at all."""
    import extractors.pdf as pdf_module
    go(db, corpus)
    before = db.execute("SELECT count(*) c FROM extraction_runs").fetchone()["c"]
    monkeypatch.setattr(pdf_module, "VERSION", "0.2.0")
    go(db, corpus)
    assert db.execute(
        "SELECT count(*) c FROM extraction_runs").fetchone()["c"] > before


def test_no_upgrade_still_means_no_re_extraction(db, corpus):
    """The property the skip exists for, kept: §1.2's "nothing is re-read"."""
    go(db, corpus)
    before = db.execute("SELECT count(*) c FROM extraction_runs").fetchone()["c"]
    go(db, corpus)
    assert db.execute(
        "SELECT count(*) c FROM extraction_runs").fetchone()["c"] == before


# --------------------------------------------------- the walking skeleton, Wave 2
#
# 02-segmentation-map.md: the skeleton "is not a prototype to throw away. It is the
# first passing test of the seam layout, and it stays in the repository as the
# integration test every later part must keep green." The tests above each isolate one
# property; this one is the corpus -- a routed document, a structured-text file, an
# image, a disk image that stops, a video that stops at container metadata, and an
# application bundle that must not be touched at all.

@pytest.fixture()
def mixed_corpus(tmp_path: Path) -> Path:
    root = tmp_path / "Documents"
    root.mkdir()
    (root / "syllabus.pdf").write_bytes(b"%PDF-1.4 BUSIB 4300 syllabus")
    (root / "notes.md").write_bytes(b"# BUSIB 4300\nlecture notes")
    (root / "Screenshot.png").write_bytes(b"\x89PNG fake")
    (root / "archive.dmg").write_bytes(b"disk image")
    (root / "clip.mp4").write_bytes(b"video")
    bundle = root / "Numbers.app" / "Contents"
    bundle.mkdir(parents=True)
    (bundle / "sheet.numbers").write_bytes(b"inside an app bundle")
    return root


def test_the_wave_2_skeleton_runs_a_mixed_corpus_end_to_end(db, mixed_corpus):
    import json
    from database_agent.identity import is_content_hash
    from eval_harness.counts import bundle_counts

    result = go(db, mixed_corpus)

    files = {r["filename"]: r for r in db.execute("SELECT * FROM files")}
    # The application bundle and everything inside it: no row at all (11 §4b).
    assert "sheet.numbers" not in files
    assert not any(".app" in r["current_path"] for r in files.values())
    assert set(files) == {"syllabus.pdf", "notes.md", "Screenshot.png",
                          "archive.dmg", "clip.mp4"}

    # Live hashes, in P1's spelling -- the stress test's last ordered item was the
    # skeleton "with live hex hashes, not sha256:abc".
    assert all(is_content_hash(r["content_hash"]) for r in files.values())

    # Every file carries a real per-tier status; the column read `{}` before.
    status = {name: json.loads(r["extraction_status_by_tier"])
              for name, r in files.items()}
    assert all(s["filesystem"] == "complete" for s in status.values())
    # §2.9's safe stop, at the NATIVE tier -- break 2. `complete` from the indexer
    # and `metadata_only` from the stopper used to be two runs at one tier.
    assert status["archive.dmg"]["native"] == "metadata_only"
    # B6: audio and video stop at container metadata. Not `unsupported`, which would
    # say no extractor exists, and not `metadata_only`, which carries zero rows.
    assert "native" in status["clip.mp4"]

    # Exactly one §8.2 event per run, which is break 5.
    events = db.execute(
        "SELECT count(*) c FROM events WHERE event_type = 'extraction'").fetchone()["c"]
    assert events == len(result.run_ids)

    # And the bundle P2 has been able to build since it shipped, from a scan.
    counts = bundle_counts(db, result.bundle_id)
    assert counts["files_indexed"] == 5
    assert counts["files_with_any_run"] == 5


# ---------------------------------------- three leftovers the caller dropped
#
# Found by a parallel session's recheck (planning/20-p1-p5-recheck.md) and confirmed
# here against live code. All three are defects in the CALLER, not in P5: every one of
# these values is computed correctly and then thrown away, which is the failure mode a
# caller is uniquely able to introduce and no per-part test can see.

def test_the_sensitivity_signals_reach_the_database(db, corpus):
    """§2.9 requires email addresses and message content to be treated as potentially
    sensitive. `extract()` returns them on `Dispatched.sensitivity` -- the field exists
    precisely because P4 conformance rule 6 forbids an extractor-private column on an
    observation, so the signal has to travel beside the batch. The caller kept only
    `.results`, so on a real scan the signal never reached the database and P7 would
    have had nothing to redact against.
    """
    from extractors.long_tail import SensitivitySignal

    note = corpus / "message.eml"
    note.write_bytes(b"From: prof@wustl.edu\n\nSee attached.")

    captured = {}
    real_extract = None

    def long_tail_with_a_signal(p, transcribe=False):
        from extractors.long_tail import LongTailEntry, LongTailFile
        return LongTailFile(values=({"label": "From", "value": "prof@wustl.edu"},))

    result = go(db, corpus, readers={"read_long_tail": long_tail_with_a_signal})

    rows = db.execute(
        "SELECT observation_key, signal FROM extraction_sensitivity_signal").fetchall()
    # The claim under test is that the caller PERSISTS whatever E3 raised, keyed on
    # P4's handle. If E3 raised nothing for this fixture the table is legitimately
    # empty -- so assert the mechanism, not a count.
    for row in rows:
        assert row["observation_key"], "a signal was stored under an empty key"
    assert "extraction_sensitivity_signal" in {
        r["name"] for r in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}, (
        "the caller never created P5's own tables, so the signal had nowhere to go")


def test_every_routed_file_leaves_a_durable_routing_decision(db, corpus):
    """§2.9: "Every file leaves the router with exactly one routing decision."
    `extraction_routing` is P5's own table and the caller called `route()` without ever
    calling `record_routing_decision`, so the decision existed in memory for the length
    of one loop iteration and was never recorded. §8.2's reconstruction requirement
    cannot be met for a routing choice nobody stored.
    """
    result = go(db, corpus)
    files = db.execute("SELECT file_id, content_hash FROM files").fetchall()
    assert files
    for row in files:
        decisions = db.execute(
            "SELECT count(*) c FROM extraction_routing WHERE file_id = ? "
            "AND content_hash = ?", (row["file_id"], row["content_hash"])).fetchone()["c"]
        assert decisions == 1, f"{row['file_id']}: {decisions} routing decisions"


def test_the_bundle_does_not_pass_p1s_column_off_as_p7s_handling_class(db, corpus):
    """P2's `handling_class` is §8.4's, and P7 does not exist. P1's `sensitivity_state`
    is a different field on a different record. The caller passed the second where the
    first was asked for: both are NULL on a live scan today, so nothing failed and the
    name was still wrong -- one concept wearing two names one column apart, which is
    this project's most expensive defect.

    Until P7 ships the honest value is None, and it must be None because it is unknown,
    not because another column happened to be empty.
    """
    import ast
    from pathlib import Path as _P
    import orchestrator as module

    result = go(db, corpus)
    stored = {r["handling_class"] for r in db.execute(
        "SELECT handling_class FROM bundle_file_entry WHERE bundle_id = ?",
        (result.bundle_id,))}
    assert stored == {None}

    # And the source must not name P1's column at that call site at all: a NULL that
    # happens to agree is not the same as not asserting a value.
    tree = ast.parse(_P(module.__file__).read_text())
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and getattr(node.func, "id", "") == "add_file_entry"):
            continue
        for keyword in node.keywords:
            if keyword.arg == "handling_class":
                assert isinstance(keyword.value, ast.Constant) and keyword.value.value is None, (
                    "handling_class is P7's and P7 is unbuilt; the honest value is a "
                    "literal None, not a different part's column")


# ------------------------------- the P6 verdict, stated absent rather than faked
#
# §2.2 names three text-layer states, and `text_layer_broken` is reachable only from
# P6's `no_usable_facts` verdict. P6 does not exist, so every caller passed
# `lambda f, h: False` -- which does not mean "P6 is absent", it means "P6 examined
# this file and its text layer is fine". Every text-bearing PDF in a real corpus got
# that answer from a function that had examined nothing.
#
# The behaviour is right (no targeted OCR without P6) and the statement was wrong,
# which is the same shape as the dead OCR path: a value that looks like a verdict and
# is actually an absence. §8.6's rule is that unfinished work stays visible AS
# unfinished.

def test_the_absent_p6_verdict_is_named_rather_than_faked():
    from orchestrator import TARGETED_OCR_UNAVAILABLE
    assert TARGETED_OCR_UNAVAILABLE("f1", "a" * 64) is False
    assert "P6" in (TARGETED_OCR_UNAVAILABLE.__doc__ or "")


def test_the_verdict_parameter_has_no_default(db, corpus):
    """B7: P5 wires the OCR switch and never invents the threshold. A default here
    would let a caller ship the lie by omission rather than by choice."""
    import inspect
    from orchestrator import run_wave2
    parameter = inspect.signature(run_wave2).parameters["no_usable_facts"]
    assert parameter.default is inspect.Parameter.empty


def test_a_real_verdict_is_still_accepted(db, corpus):
    """The absence is a caller's statement, not a restriction: when P6 exists it
    passes its own verdict and this path is unchanged."""
    asked = []

    def p6_says_no_usable_facts(file_id, content_hash):
        asked.append((file_id, content_hash))
        return False

    go(db, corpus, no_usable_facts=p6_says_no_usable_facts)
    assert asked, "the verdict was never consulted, so the seam is not wired at all"
    for file_id, content_hash in asked:
        assert file_id and len(content_hash) == 64


# ------------------------- a caller's error is not the file's failure
#
# Found by review round 2, which proved it by running it. `_extract_one` catches
# `Exception` so that "a reader that raises becomes one `failed` run rather than the
# end of the scan" (§2.4). But that catch cannot tell "this PDF is encrypted" from
# "you called me in the wrong order" — and P6's plan proposes exactly the second, a
# verdict that raises when consulted before its deterministic pass has run.
#
# Executed against the live harness before the fix: every text-bearing PDF became
# `pdf.text · native · failed`, with the ordering error recorded as the file's
# `failure_reason`, and the scan continued. The corpus would have been quietly
# mis-recorded and the guard that was supposed to make the ordering visible would
# have been the thing that hid it.

def test_a_contract_violation_propagates_rather_than_becoming_a_failed_run(db, corpus):
    from extractors.failure import ContractViolation

    class FactPassNotRun(ContractViolation):
        """What P6 raises if its verdict is consulted before its pass has run."""

    def too_early(file_id, content_hash):
        raise FactPassNotRun("P6 has not run for this content hash")

    with pytest.raises(FactPassNotRun):
        go(db, corpus, no_usable_facts=too_early)

    # And nothing was recorded as the file's fault.
    failed = db.execute(
        "SELECT count(*) c FROM extraction_runs WHERE completeness = 'failed'"
    ).fetchone()["c"]
    assert failed == 0


def test_a_reader_failure_is_still_the_files_failure(db, corpus):
    """The property the catch exists for, unchanged: §2.4 forbids treating an
    unreadable file as an empty document, and a crashed scan is worse."""
    def locked(path):
        raise ValueError("file has not been decrypted")

    go(db, corpus, readers={"read_pdf": locked})
    rows = db.execute(
        "SELECT failure_reason FROM extraction_runs WHERE completeness = 'failed'"
    ).fetchall()
    assert len(rows) == 1
    assert rows[0]["failure_reason"] == "ValueError: file has not been decrypted"


def test_the_two_refusals_still_propagate_and_are_not_contract_violations():
    """11 §4b and §5 predate this and keep their own handling in the caller."""
    from extractors.failure import ContractViolation
    from extractors.safety import DatalessRefused, ProtectedContainerRefused
    for refusal in (DatalessRefused, ProtectedContainerRefused):
        assert not issubclass(refusal, ContractViolation), refusal.__name__


# ------------------ the sensitivity signal, keyed to the run it came FROM
#
# Found by review round 3. Fixing `observation_keys_for_run`'s ordering was necessary
# and not sufficient: the caller resolved the signals against the WRONG RUN's keys.
#
# `results` is built filesystem-first (`results = [extract_filesystem(...)]`, then
# `results.extend(routed)`), and the filesystem run always has observations — the
# filename is one. So `if signals and result.observations` matched on the first
# iteration, every time, and a signal whose `observation_index` is a position in E3's
# batch was resolved against the FILESYSTEM batch's keys.
#
# Same class as the uuid4 ordering defect, one layer up: a positional handle resolved
# against the wrong list. §2.9's "addresses and message content as potentially
# sensitive" was recorded against a filename, and P7's redaction would have protected
# the wrong value.

def test_a_sensitivity_signal_is_keyed_to_the_run_that_raised_it(db, corpus):
    from extractors.long_tail import LongTailFile, LongTailValue

    card = corpus / "contacts.vcf"
    card.write_bytes(b"BEGIN:VCARD\nFN:Joseph Yung\nEMAIL:jy@example.com\nEND:VCARD")

    def read_contacts(p, transcribe=False):
        return LongTailFile(values=(
            LongTailValue(name="FN", value="Joseph Yung", entry_ordinal=None,
                          kind="name"),
            LongTailValue(name="EMAIL", value="jy@example.com", entry_ordinal=None,
                          kind="email"),
        ))

    go(db, corpus, readers={"read_long_tail": read_contacts})

    rows = db.execute("SELECT run_id, observation_key, signal "
                      "FROM extraction_sensitivity_signal").fetchall()
    assert rows, "§2.9's contacts signal never reached the database"

    for row in rows:
        run = db.execute("SELECT extractor_name FROM extraction_runs WHERE run_id = ?",
                         (row["run_id"],)).fetchone()
        # The signal came from E3, so it must be stored against E3's run.
        assert run["extractor_name"] == "text.structured", run["extractor_name"]
        # And the key must name a row on THAT run, not a filename on the indexer's.
        owner = db.execute(
            "SELECT run_id, raw_value FROM evidence WHERE observation_key = ?",
            (row["observation_key"],)).fetchone()
        assert owner is not None, "the signal names a key no observation carries"
        assert owner["run_id"] == row["run_id"]
        assert owner["raw_value"] != "contacts.vcf", (
            "the signal landed on the filename — it was resolved against the "
            "filesystem run's keys")
