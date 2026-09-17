# tests/integration/test_captures_are_settled_by_kind.py
"""A picture with no words in it is a capture, and nobody has to be asked.

**THE MEASUREMENT (the owner's corpus, 13 Sep 2026, lead-only).** Of the 242 files
the cloud situation judge was asked about, 50 carried NO TEXT AT ALL: 35 images and
16 audio files whose whole released evidence was a path, a mime type and an
extension. The term detector returned `no_evidence` for 45 of them, because the
`photos` schema carries `file_kind_never_alone` and a JPEG with no words is one
signal; the judge, shown a mime type and nothing else, answered "none" for 36 of
them, honestly -- "the released values show only a mime type". Fifty files came out
of the run with no situation and no facts, and a call had been spent on most of
them to be told what the extension already said.

**THE RULE.** `00`:110 sanctions a deterministic answer for "a direct, unique
match", and this is the one case at this site that is literally that: a file
version with no text of any kind whose source type is image or audio/video IS a
capture, and the recogniser recognises it as `photos` on its file kind alone. Site
G then counts it on its own line -- `settled by kind: N` -- and does not put it to
a model.

**`file_kind_never_alone` IS NOT WEAKENED, and this file is what says so.** Two of
its four files have text -- one JPEG whose OCR yielded words, one PDF -- and both
must go on being asked exactly as they are today. The rule is reached only where
there is no term and no text to hold one, so there is no first signal for the kind
to be a second to.

**WHY THE CORPUS IS SYNTHETIC AND WRITTEN THROUGH THE REAL WRITERS.** A real JPEG
would need this machine's image reader and a real OCR'd JPEG would need its Vision
framework, so a corpus of real bytes would measure which laptop the suite ran on.
What decides this rule is the SHAPE of a file's evidence -- which families are in
it -- and that shape is written here through P1's own `record_file`, P4's own
`RunWriter` and P5's own `route`, so the rows the detector reads are the rows a
scan writes.
"""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import cli  # noqa: E402
from database_agent.db import open_database  # noqa: E402
from database_agent.files_table import record_file  # noqa: E402
from evidence_shape.store import RunWriter  # noqa: E402
from extractors.router import record_routing_decision, route  # noqa: E402
from extractors.runs import coverage  # noqa: E402
from extractors.shape import location, observation, run, segment  # noqa: E402
from extractors.sink import ExtractionResult  # noqa: E402
from llm_harness.vocabulary import G_SITUATION_SENSITIVITY  # noqa: E402
from p1_contract import p3_basic_record  # noqa: E402
from recognition.detector import (  # noqa: E402
    CAPTURE_SCHEMA, Detector, Recognition, settled_by_file_kind,
)
from test_per_file_model_route import _local_only  # noqa: E402

WHEN = "2026-09-13T12:00:00+00:00"

#: The four files, and each one is a different answer.
#:
#: The two captures carry P3's §1.2 record and nothing else, which is what a
#: photograph with no EXIF and a voice memo with no tags actually leave behind. The
#: other two carry one reading each, in the family that says something read words
#: out of the file: `ocr` for a photographed receipt, `text_document` for a PDF.
#:
#: THE WORDS ARE DELIBERATELY ORDINARY. Neither text names an authored term, so
#: both of those files reach site G as `no_evidence` -- which is where they are
#: today, and the point is that they STAY there and stay asked. A term match would
#: measure the recogniser instead of this rule.
#: THE NAMES CARRY NO AUTHORED TERM, and that is a property of the corpus rather
#: than of the rule. A filename IS one of the file's own words -- SPEC 2.2 ranks it
#: beside a page-one heading -- so `Voice Memo 3.mp3` matches `photos`' authored
#: `voice memo`, has a term, and reaches the ordinary arity gate instead of this
#: branch. That is the right answer and it is why the owner's 50 split 45/5: five of
#: them said something in their names. What this file measures is the 45.
CAPTURE_JPEG = "IMG_4471.jpg"
CAPTURE_AUDIO = "REC0032.mp3"
OCR_JPEG = "IMG_5502.jpg"
TEXT_PDF = "Draft 7.pdf"

CORPUS: tuple[tuple[str, str, str, tuple[str, str, str] | None], ...] = (
    (CAPTURE_JPEG, ".jpg", "image/jpeg", None),
    (CAPTURE_AUDIO, ".mp3", "audio/mpeg", None),
    (OCR_JPEG, ".jpg", "image/jpeg",
     ("ocr", "ocr.apple_vision", "handed over at the counter this morning")),
    (TEXT_PDF, ".pdf", "application/pdf",
     ("text_document", "pdf.text", "some remarks jotted down after the walk")),
)


def _write(conn, folder: Path, filename: str, extension: str, mime: str,
           text: tuple[str, str, str] | None) -> tuple[str, str]:
    """One file, its P4 observations and P5's own routing decision.

    The filesystem observations are `extractors.filesystem`'s four, in its own
    zones: the name, the parent folder, the extension and the mime type. They are
    written here rather than by calling that extractor because the extractor stats
    a real file of the format, and the whole point of this corpus is that no real
    JPEG is involved.

    The routing decision is P5's OWN `route`, not a hand-made row: it is the part
    that answers "what family is this file", the detector reads its answer, and a
    record built by hand here would let this test agree with a rule the product
    does not have.
    """
    path = folder / filename
    path.write_bytes(b"not really a picture")
    file_id = record_file(conn, path, parent_folder_context="corpus",
                          mime_type=mime, detected_format=None,
                          scan_state="scanned", materialized=True,
                          **{**p3_basic_record(path), "extension": extension})
    content_hash = conn.execute(
        "SELECT content_hash FROM files WHERE file_id = ?",
        (file_id,)).fetchone()[0]

    observations = [
        observation(file_id=file_id, content_hash=content_hash,
                    extractor_name="filesystem.record", extractor_version="0.1.0",
                    source_type="filesystem", raw_value=filename,
                    location=location(zone="filename"),
                    observed_at=WHEN, reliability="possible"),
        observation(file_id=file_id, content_hash=content_hash,
                    extractor_name="filesystem.record", extractor_version="0.1.0",
                    source_type="filesystem", raw_value=str(folder),
                    location=location(zone="path"),
                    observed_at=WHEN, reliability="possible"),
    ]
    for slot, value in (("extension", extension), ("mime_type", mime)):
        observations.append(observation(
            file_id=file_id, content_hash=content_hash,
            extractor_name="filesystem.record", extractor_version="0.1.0",
            source_type="filesystem", raw_value=value,
            location=location(zone="metadata",
                              container_path=(segment("field", label=slot),)),
            observed_at=WHEN, reliability="direct"))
    if text is not None:
        source_type, extractor_name, body = text
        observations.append(observation(
            file_id=file_id, content_hash=content_hash,
            extractor_name=extractor_name, extractor_version="0.1.0",
            source_type=source_type, raw_value=body,
            location=location(zone="ocr" if source_type == "ocr" else "body"),
            observed_at=WHEN, reliability="possible"))

    RunWriter(conn, author="P5").write(ExtractionResult(
        run=run(file_id=file_id, content_hash=content_hash,
                extractor_name="filesystem.record", extractor_version="0.1.0",
                source_type="filesystem", analysis_tier="filesystem", config={},
                completeness="complete", coverage=coverage("files", 1, 1),
                observation_count=len(observations), started_at=WHEN,
                finished_at=WHEN),
        observations=tuple(observations)))
    record_routing_decision(conn, route(
        file_id=file_id, content_hash=content_hash, path=path,
        extension=extension, detect_format=lambda _path: None))
    return file_id, content_hash


@pytest.fixture(scope="module")
def corpus(tmp_path_factory):
    """The four files in one database, built once.

    `cli._bootstrap` makes every schema the detector and site G read, which is
    what the other direct-call tests at this site do for the same reason: a
    hand-made table is a shape nothing in `src/` writes.
    """
    root = tmp_path_factory.mktemp("captures")
    folder = root / "corpus"
    folder.mkdir()
    conn = open_database(root / "plan.sqlite")
    cli._bootstrap(conn)
    by_name = {}
    for filename, extension, mime, text in CORPUS:
        by_name[filename] = _write(conn, folder, filename, extension, mime, text)
    conn.commit()
    yield conn, by_name
    conn.close()


@pytest.fixture(scope="module")
def detector():
    """The SHIPPED manifest and the SHIPPED handling policy.

    Not a hand-built rule set, because what is under test is that `photos` --
    which sets `file_kind_never_alone`, and is the schema this rule names -- is
    reachable in the release the product actually ships.
    """
    from recognition.rules import load_rules

    return Detector(load_rules(cli._RECOGNITION_MANIFEST.read_text),
                    handling_for=cli.HANDLING_POLICY, now=lambda: WHEN,
                    topic_condition_mentions=cli.TOPIC_CONDITION_MENTIONS)


# --- the recogniser: two captures, and two files that still have words ----------


def test_a_text_less_picture_and_a_text_less_recording_are_recognised_as_captures(
        corpus, detector):
    """`00`:110's direct, unique match, stated as an assertion.

    Before this rule both files came back `Abstention("no_evidence")` -- 45 of the
    owner's 50 did -- and went on to a judge that could only say "none".

    SABOTAGE: delete the `_capture` call from `Detector.explain`. Both assertions
    go red and the corpus's two captures are unclassified again.
    """
    conn, by_name = corpus

    for filename in (CAPTURE_JPEG, CAPTURE_AUDIO):
        file_id, content_hash = by_name[filename]
        outcome = detector.explain(conn, file_id, content_hash)
        assert isinstance(outcome, Recognition), (filename, outcome)
        assert outcome.schema_id == CAPTURE_SCHEMA, (filename, outcome)
        assert settled_by_file_kind(outcome), filename
        # §8.4: the classification is itself evidence-backed, and what this one
        # rests on is the two metadata rows -- the extension and the mime type.
        # A recognition citing nothing is one `ClassificationRecord` refuses.
        assert outcome.evidence_refs, filename


def test_the_rule_reaches_no_file_that_has_text_in_it(corpus, detector):
    """`file_kind_never_alone` STILL MEANS WHAT IT MEANS, and this is the half of
    the change that says so.

    A JPEG whose OCR yielded words is `00`'s own case for a model -- an opaque
    image "may be a screenshot of a receipt, application portal, conversation,
    code error, or research figure" -- and a PDF was never in question. Neither
    is recognised on its kind, and neither answer moved: both are still
    `no_evidence`, which is where they were before this rule existed.

    SABOTAGE: drop the `TEXTLESS_SOURCE_TYPES` test from `_capture`, so the kind
    alone decides. This goes red on the OCR'd JPEG, which would be filed as a
    photo event with a receipt's text sitting unread inside it.
    """
    conn, by_name = corpus

    for filename in (OCR_JPEG, TEXT_PDF):
        file_id, content_hash = by_name[filename]
        outcome = detector.explain(conn, file_id, content_hash)
        assert not settled_by_file_kind(outcome), (filename, outcome)
        assert not (isinstance(outcome, Recognition)
                    and outcome.schema_id == CAPTURE_SCHEMA), (filename, outcome)


def test_a_capture_becomes_a_classification_record_the_gate_can_read(corpus,
                                                                     detector):
    """The producer seam, because a recognition nothing records changes nothing.

    `Detector.__call__` is `orchestrator.ClassificationProducer`; the record it
    writes for a capture carries the shipped policy's class for `photos` and the
    observation keys the recognition cites.

    SABOTAGE: return the `Recognition` with an empty `evidence_refs` tuple.
    `ClassificationRecord` raises `UnbackedClassification` and this errors.
    """
    conn, by_name = corpus
    file_id, content_hash = by_name[CAPTURE_JPEG]

    record = detector(conn, file_id, content_hash)

    assert record is not None, (
        "a capture came back unclassified, so nothing downstream can act on it")
    assert record.protected is False
    assert record.evidence_refs


# --- site G: the captures are counted and not asked -----------------------------


def _ask(conn, roster, detector) -> cli.SituationPass:
    """Site G over the four files, on a deployment with a local model.

    The client is `test_per_file_model_route`'s: it carries a target and answers
    `{"claims": []}` without reaching a network. That is enough for this
    measurement, which is about WHICH files a dossier is built for and not about
    what a model says once one is.
    """
    # THE RUN'S OWN POLICY ROW, through `cli.main`'s own writer: the call identity
    # reads the policy's content, so a version string with no row behind it is a
    # call nothing could be replayed from.
    policy_version = cli.set_policy(
        conn,
        cli.Policy(policy_version=cli.UNSET_POLICY_VERSION,
                   operation_mode=cli.OPERATION_MODE,
                   consent_grants=cli.standing_consent_grants("run-1"),
                   redaction_settings={}, automatic_move_permissions={},
                   plan_version=cli.PLAN_VERSION, set_at=WHEN),
        component_version=cli.COMPONENT_VERSION, user_id="t",
        reason="site G over a corpus of captures")
    routing = _local_only()
    authorities = cli.fact_call_authorities(
        conn, routing=routing, scan_run_id="scan",
        corpus_file_count=len(roster), policy_version=policy_version,
        wire_handle_key=bytes(32), schema="academic", folder_levels=None,
        user_id="t", now=lambda: WHEN)
    return cli.ask_the_situation(
        conn, roster=roster, explain=detector.situation_outcome,
        precaution_of=detector.precaution_report,
        fact_authorities=authorities, routing=routing,
        prompt=cli.prompt_for(G_SITUATION_SENSITIVITY),
        now=lambda: WHEN, user_id="t")


def _dossier_subjects(conn) -> set[str]:
    return {row["subject_ref"] for row in conn.execute(
        "SELECT subject_ref FROM llm_dossier WHERE call_site = ?",
        (G_SITUATION_SENSITIVITY,))}


def test_site_g_counts_the_captures_on_their_own_line_and_asks_nobody(corpus,
                                                                     detector):
    """The whole change, at the site the measurement was taken at.

    THE TWO HALVES HAVE TO BE READ TOGETHER. A run that asked nothing at all would
    satisfy the first assertion and would mean the opposite, so the files that DO
    have text are asserted to have been asked in the same breath.

    SABOTAGE: delete the `settled_by_file_kind` skip from `ask_the_situation`.
    `settled_by_kind` reads 0 and all four files are assembled for a model --
    which is the run the owner measured, where 36 of 50 answers were "none".
    """
    conn, by_name = corpus
    roster = tuple(by_name[name] for name, *_rest in CORPUS)

    situation = _ask(conn, roster, detector)

    assert situation.settled_by_kind == 2, situation
    assert _dossier_subjects(conn) == {by_name[OCR_JPEG][0],
                                       by_name[TEXT_PDF][0]}, (
        "a capture was assembled for a model, or a file with words in it was not")
    # ASKED, and not turned away at some earlier door. Without this line the
    # assertion above would still pass on a run that built the two dossiers and
    # then failed to route, which is a different product.
    #
    # `no_answer_returned` AND NOT `declined`, since `104` §18.96 split the two.
    # The stub answers with no claim at all, so `run_call` hands back a
    # `ValidationUnavailable` and no judgement about either file exists: nothing
    # was named and nothing was declined. `declined` is now reserved for a model
    # that answered and named no situation it could cite -- the file a person has
    # to answer for -- and asserting it here would put run 21's defect into a
    # test, which is a screen saying a model had read a file it never saw.
    assert situation.no_answer_returned == 2, situation
    assert situation.declined == 0, situation
    assert situation.no_route == 0, situation


def test_the_captures_are_not_folded_into_any_other_counter(corpus, detector):
    """The counters PARTITION the roster, so a new bucket has to take its files
    OUT of the old ones rather than beside them.

    `nothing_to_read` is the counter a capture would otherwise land in, and it is
    the wrong sentence for it: a file with nothing to read is one nobody could
    answer about, and a capture is one nobody needed to.

    SABOTAGE: count `settled_by_kind` and fall through instead of `continue`. The
    sum below exceeds the roster and this goes red.
    """
    conn, by_name = corpus
    roster = tuple(by_name[name] for name, *_rest in CORPUS)

    situation = _ask(conn, roster, detector)

    counted = (len(situation.named) + situation.nothing_to_read
               # `104` §18.96's half of the old `declined`; the partition holds
               # both halves or it stops adding up to the roster.
               + situation.declined + situation.no_answer_returned
               + situation.held_not_asked
               + situation.no_route + situation.over_ceiling
               + situation.settled_by_kind)
    assert counted == len(roster), situation
    assert situation.nothing_to_read == 0, situation
    # `recognised_by_rules` is outside the partition and says the rules recognised
    # these files "from their own words". A capture has no words, and is not asked,
    # so it must not be counted there or that sentence stops being true.
    assert situation.recognised_by_rules == 0, situation
