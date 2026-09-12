# tests/readers/test_entities_gliner.py
"""`00` amendment 7(b)'s reader: the packing, the decoding, and one real run.

Every pin but the last runs on a FAKE session -- an object with `get_inputs` and
`run` -- because the published weights are 1.1 GB of machine state and a pin that
needs them is a pin that does not run. What the fake cannot check is whether the
arithmetic in this file is the arithmetic the graph was trained with, so the last
pin loads the real weights when they are on this machine and skips when they are
not.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy
import pytest

from readers.entities_gliner import (
    Entity, GlinerEntities, ModelUnavailable, decode, greedy_non_overlapping,
    overlaps, pack, span_grid, weights_in, word_mask, words_of,
)

REAL_WEIGHTS = Path.home() / ".graph-agent" / "models" / "gliner-pii"


class Encoding:
    """What `tokenizers` hands back, in the three fields `pack` reads."""

    def __init__(self, word_ids, ids=None, attention_mask=None):
        self.word_ids = list(word_ids)
        self.ids = list(ids if ids is not None
                        else range(1, len(self.word_ids) + 1))
        self.attention_mask = list(attention_mask if attention_mask is not None
                                   else [1] * len(self.word_ids))


class Specification:
    def __init__(self, name):
        self.name = name


class FakeSession:
    """A session that returns the logits it was given and records what it was fed."""

    def __init__(self, logits_for, *, inputs=None):
        self._logits_for = logits_for
        self._inputs = inputs or ("input_ids", "attention_mask", "words_mask",
                                  "text_lengths", "span_idx", "span_mask")
        self.fed = []

    def get_inputs(self):
        return [Specification(name) for name in self._inputs]

    def run(self, _outputs, feed):
        self.fed.append(feed)
        return [self._logits_for(feed)]


# --- the splitter and the grid ----------------------------------------------

def test_the_word_splitter_keeps_the_characters_it_did_not_split_on():
    text = "Sarah Whitfield, born 14 March 1987."
    found = words_of(text)
    assert [word for word, _, _ in found] == [
        "Sarah", "Whitfield", ",", "born", "14", "March", "1987", "."]
    # Every word is exactly the characters at its own offsets: this is the property
    # the whole span arithmetic rests on, so it is asserted rather than assumed.
    assert all(text[start:end] == word for word, start, end in found)


def test_the_span_grid_holds_every_width_including_the_ones_that_run_off_the_end():
    grid = span_grid(3, 4)
    assert grid.shape == (12, 2)
    # Row `i * max_width + k` is the span starting at word i, k+1 words long. The
    # rows that run past the last word are KEPT and marked, because the graph's
    # output is shaped by the grid.
    assert list(grid[0]) == [0, 0] and list(grid[3]) == [0, 3]
    assert list(grid[4]) == [1, 1] and list(grid[11]) == [2, 5]


# --- packing ------------------------------------------------------------------

def test_the_word_mask_numbers_the_first_sub_token_of_each_document_word():
    # Two labels -> a prompt of five words (<<ENT>> label <<ENT>> label <<SEP>>).
    # Then three document words, the second of which is two sub-tokens.
    word_ids = [None, 0, 1, 2, 3, 4, 5, 6, 6, 7, None]
    assert word_mask(word_ids, prompt_length=5) == [
        0, 0, 0, 0, 0, 0, 1, 2, 0, 3, 0]


def test_packing_shapes_the_six_tensors_the_graph_takes():
    labels = ("person", "phone number")
    encoding = Encoding([None, 0, 1, 2, 3, 4, 5, 6, 6, 7, None])
    feed, word_count = pack(labels, encoding, max_width=4)

    assert word_count == 3
    assert set(feed) == {"input_ids", "attention_mask", "words_mask",
                         "text_lengths", "span_idx", "span_mask"}
    assert feed["input_ids"].shape == (1, 11)
    assert feed["attention_mask"].shape == (1, 11)
    assert feed["words_mask"].tolist() == [[0, 0, 0, 0, 0, 0, 1, 2, 0, 3, 0]]
    assert feed["text_lengths"].tolist() == [[3]]
    assert feed["span_idx"].shape == (1, 3 * 4, 2)
    assert feed["span_mask"].shape == (1, 3 * 4)
    # A span is valid when its LAST word exists. Word 0 may be 1, 2 or 3 words long
    # and not 4; word 2 may only be 1.
    assert feed["span_mask"][0].tolist() == [
        True, True, True, False, True, True, False, False,
        True, False, False, False]


def test_packing_counts_the_words_that_survived_truncation_and_not_the_others():
    """`gliner_config.json` caps the encoder at 384 sub-tokens and the label prompt
    spends some of them. A grid built from the pre-tokenized count asks the graph
    about words whose vectors were never computed."""
    labels = ("person",)                      # prompt of three words
    # Five document words went in; the encoding stops after two of them.
    encoding = Encoding([None, 0, 1, 2, 3, 4])
    feed, word_count = pack(labels, encoding, max_width=3)
    assert word_count == 2
    assert feed["text_lengths"].tolist() == [[2]]
    assert feed["span_idx"].shape == (1, 2 * 3, 2)


def test_packing_a_document_the_prompt_left_no_room_for_counts_nothing():
    feed, word_count = pack(("person",), Encoding([None, 0, 1, 2]), max_width=3)
    assert word_count == 0
    assert feed["text_lengths"].tolist() == [[0]]


# --- decoding -----------------------------------------------------------------

def _logits(word_count, max_width, kinds, high):
    """A logit block that is -8 everywhere except at the rows named in `high`."""
    rows = numpy.full((1, word_count, max_width, kinds), -8.0, dtype=numpy.float32)
    for (first, width, kind), value in high.items():
        rows[0, first, width - 1, kind] = value
    return rows


def test_decoding_turns_a_logit_into_a_score_a_floor_reads_and_a_char_span():
    text = "Sarah Whitfield called us"
    words = words_of(text)
    grid = span_grid(len(words), 3)
    valid = grid[:, 1] < len(words)
    # Words 0-1 are a person at logit 3.0 -> sigmoid ~0.953.
    rows = _logits(len(words), 3, 2, {(0, 2, 0): 3.0})
    found = decode(rows, words=words, grid=grid, valid=valid,
                   labels=("person", "phone number"), text=text, score_floor=0.7)
    assert len(found) == 1
    assert found[0].label == "person"
    assert (found[0].start, found[0].end) == (0, 15)
    assert found[0].text == "Sarah Whitfield" == text[found[0].start:found[0].end]
    assert found[0].score == pytest.approx(1 / (1 + numpy.exp(-3.0)), abs=1e-6)


def test_the_floor_is_the_callers_and_a_span_below_it_is_not_a_reading():
    text = "Sarah Whitfield called us"
    words = words_of(text)
    grid = span_grid(len(words), 3)
    valid = grid[:, 1] < len(words)
    rows = _logits(len(words), 3, 1, {(0, 2, 0): 0.5})     # sigmoid ~0.62
    assert decode(rows, words=words, grid=grid, valid=valid, labels=("person",),
                  text=text, score_floor=0.5)
    assert decode(rows, words=words, grid=grid, valid=valid, labels=("person",),
                  text=text, score_floor=0.7) == ()


def test_an_invalid_span_is_never_a_reading_however_it_scored():
    """The grid's off-the-end rows are fed to the graph and the graph answers them.
    `span_mask` is what keeps the answer out of the result."""
    text = "Sarah Whitfield"
    words = words_of(text)
    grid = span_grid(len(words), 4)
    valid = grid[:, 1] < len(words)
    rows = _logits(len(words), 4, 1, {(0, 4, 0): 9.0})     # words 0..3; only 0-1 exist
    assert decode(rows, words=words, grid=grid, valid=valid, labels=("person",),
                  text=text, score_floor=0.5) == ()


def test_two_readings_that_share_no_character_are_both_kept():
    """GLiNER's own test is on inclusive WORD indices; this is on half-open CHARACTER
    offsets, where `Whitfield` and the comma after it are `(6, 15)` and `(15, 16)`.
    Under the inclusive test they share offset 15 and one is thrown away."""
    assert not overlaps((6, 15), (15, 16))
    assert overlaps((6, 15), (6, 15))
    assert overlaps((6, 15), (14, 20))


def test_greedy_keeps_the_strongest_of_two_overlapping_readings():
    weak = Entity(label="person", start=0, end=15, score=0.80, text="Sarah Whitfield")
    strong = Entity(label="organization", start=6, end=15, score=0.95, text="Whitfield")
    apart = Entity(label="phone number", start=20, end=32, score=0.90, text="415-555-0192")
    kept = greedy_non_overlapping([weak, strong, apart])
    assert [one.label for one in kept] == ["organization", "phone number"]
    # Reading order, not score order: a consumer walks a document forwards.
    assert [one.start for one in kept] == [6, 20]


# --- the loaded reader --------------------------------------------------------

def _model_directory(root: Path, *, weights=("model.onnx",), max_len=64):
    """A directory shaped like the published one, with a real tokenizer in it."""
    from tokenizers import Tokenizer, models, pre_tokenizers

    vocab = {"[UNK]": 0, "Sarah": 1, "Whit": 2, "##field": 3, "born": 4,
             "1987": 5, "passport": 6, "N2938471": 7}
    tokenizer = Tokenizer(models.WordPiece(vocab=vocab, unk_token="[UNK]",
                                           max_input_chars_per_word=100))
    tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()
    root.mkdir(parents=True, exist_ok=True)
    tokenizer.save(str(root / "tokenizer.json"))
    (root / "gliner_config.json").write_text(json.dumps({
        "ent_token": "<<ENT>>", "sep_token": "<<SEP>>", "max_width": 4,
        "max_len": max_len}), encoding="utf-8")
    (root / "onnx").mkdir(exist_ok=True)
    for name in weights:
        (root / "onnx" / name).write_bytes(b"not the weights; the session is injected")
    return root


def test_an_int8_only_directory_is_refused_with_the_measurement_that_refuses_it(tmp_path):
    """`model_int8.onnx` loads and finds nothing (recall 0.04). A reader that fell
    back to it would report itself on while being off."""
    directory = _model_directory(tmp_path / "pii", weights=("model_int8.onnx",))
    with pytest.raises(ModelUnavailable) as refusal:
        weights_in(directory)
    assert "model_int8.onnx" in str(refusal.value)
    assert "recall 0.04" in str(refusal.value)


def test_a_directory_with_no_tokenizer_is_refused_at_construction(tmp_path):
    directory = _model_directory(tmp_path / "pii")
    (directory / "tokenizer.json").unlink()
    with pytest.raises(ModelUnavailable):
        GlinerEntities(directory, labels=("person",), score_floor=0.5, threads=1)


def test_a_graph_taking_other_inputs_is_refused_rather_than_fed_noise(tmp_path):
    directory = _model_directory(tmp_path / "pii")
    session = FakeSession(lambda feed: None, inputs=("input_ids", "attention_mask"))
    with pytest.raises(ModelUnavailable) as refusal:
        GlinerEntities(directory, labels=("person",), score_floor=0.5, threads=1,
                       session=session)
    assert "words_mask" in str(refusal.value)


def test_the_reader_names_the_weights_it_read_by_for_the_audit(tmp_path):
    directory = _model_directory(tmp_path / "pii")
    reader = GlinerEntities(directory, labels=("person",), score_floor=0.5,
                            threads=1, session=FakeSession(lambda feed: None))
    name, _, digest = reader.weights.partition("@")
    assert name == "model.onnx"
    assert len(digest) == 16


def test_the_reader_packs_prompt_and_document_and_reads_the_span_back(tmp_path):
    directory = _model_directory(tmp_path / "pii")
    text = "Sarah Whitfield born 1987"

    def logits(feed):
        word_count = int(feed["text_lengths"][0][0])
        # Words 0-1 are the person, at a logit the 0.7 floor clears.
        return _logits(word_count, 4, 2, {(0, 2, 0): 4.0})

    session = FakeSession(logits)
    reader = GlinerEntities(directory, labels=("person", "date of birth"),
                            score_floor=0.7, threads=1, session=session)
    found = reader.entities(text)

    fed = session.fed[0]
    # The prompt is five words -- <<ENT>> person <<ENT>> date of birth <<SEP>> --
    # and four document words follow it; `Whitfield` is two sub-tokens and only its
    # first carries a number.
    assert fed["text_lengths"].tolist() == [[4]]
    assert max(fed["words_mask"][0].tolist()) == 4
    assert fed["span_idx"].shape == (1, 4 * 4, 2)
    assert [(one.label, one.text) for one in found] == [("person", "Sarah Whitfield")]
    assert text[found[0].start:found[0].end] == found[0].text


def test_a_text_with_no_words_asks_the_model_nothing(tmp_path):
    directory = _model_directory(tmp_path / "pii")
    session = FakeSession(lambda feed: None)
    reader = GlinerEntities(directory, labels=("person",), score_floor=0.5,
                            threads=1, session=session)
    assert reader.entities("   \n  ") == ()
    assert session.fed == []


# --- the windows --------------------------------------------------------------

def test_a_document_longer_than_the_encoder_is_read_in_overlapping_windows(tmp_path):
    """The gate exists to catch a diagnosis on page three, so the whole unit is read.

    `max_len` here is 64 sub-tokens against a 300-word document, so the reader must
    come back for the rest -- and the windows must overlap by `max_width` words, the
    longest span this model can name, or an entity on a boundary is two fragments.
    """
    directory = _model_directory(tmp_path / "pii", max_len=64)
    text = " ".join(f"word{index}" for index in range(300))
    session = FakeSession(
        lambda feed: _logits(int(feed["text_lengths"][0][0]), 4, 1, {}))
    reader = GlinerEntities(directory, labels=("person",), score_floor=0.7,
                            threads=1, session=session)
    reader.entities(text)

    read = [int(feed["text_lengths"][0][0]) for feed in session.fed]
    assert len(read) > 1, "one window cannot hold a 300-word document at max_len 64"
    assert sum(read) > 300, "the windows overlap, so they cover more than the text"
    # Every window but the last is a full one, and the step between them is that
    # window less the overlap -- the config's own `max_width`, which is 4 here.
    assert all(count == read[0] for count in read[:-1])
    assert (len(read) - 1) * (read[0] - 4) < 300 <= len(read) * (read[0] - 4) + 4


def test_a_reading_on_a_window_boundary_is_observed_once_and_not_twice(tmp_path):
    """Two windows both see what lies in their overlap. The greedy pass at the end
    -- over ALL the windows, not one per window -- is what makes it one reading."""
    directory = _model_directory(tmp_path / "pii", max_len=64)
    text = " ".join(f"word{index}" for index in range(300))
    # EVERY word is a person, at a logit the floor clears. So every word in every
    # overlap is returned twice by construction, which is the case under test.
    session = FakeSession(lambda feed: _logits(
        int(feed["text_lengths"][0][0]), 4, 1,
        {(first, 1, 0): 6.0 for first in range(int(feed["text_lengths"][0][0]))}))
    reader = GlinerEntities(directory, labels=("person",), score_floor=0.7,
                            threads=1, session=session)
    found = reader.entities(text)

    assert len(session.fed) > 1, "the premise is that there were several windows"
    spans = [(one.start, one.end) for one in found]
    assert len(spans) == len(set(spans)), "a boundary reading was recorded twice"
    assert len(found) == 300, "every word is a person and every word is read once"
    assert [one.text for one in found] == [f"word{index}" for index in range(300)]
    assert all(text[one.start:one.end] == one.text for one in found)


def test_an_empty_label_list_is_refused_because_it_asks_the_model_nothing(tmp_path):
    directory = _model_directory(tmp_path / "pii")
    with pytest.raises(ValueError):
        GlinerEntities(directory, labels=(), score_floor=0.5, threads=1,
                       session=FakeSession(lambda feed: None))


# --- the one pin that uses the real weights -----------------------------------

@pytest.mark.skipif(not (REAL_WEIGHTS / "onnx" / "model.onnx").is_file(),
                    reason="the published GLiNER weights are machine state, not "
                           "repository state; this deployment has not fetched them")
def test_the_real_weights_find_a_planted_name_and_date_of_birth():
    """The one pin the fake session cannot stand in for: whether the arithmetic in
    `entities_gliner.py` is the arithmetic these weights were trained with.

    Slow by design -- about 1.5 s to load and 0.1 s to read -- and skipped outright
    where the 1.1 GB file is absent.
    """
    reader = GlinerEntities(
        REAL_WEIGHTS, labels=("person", "date of birth", "medical condition"),
        score_floor=0.7, threads=2)
    text = ("Patient intake summary. Sarah Whitfield, born on 14 March 1987, was "
            "admitted for evaluation of type 2 diabetes mellitus.")
    found = reader.entities(text)
    by_label = {one.label: one for one in found}

    assert "Sarah Whitfield" == by_label["person"].text
    assert "14 March 1987" in by_label["date of birth"].text
    # Every reading is exactly the characters at its own offsets, which is what the
    # extractor's RAW-1 arithmetic depends on.
    assert all(text[one.start:one.end] == one.text for one in found)
    assert all(one.score > 0.7 for one in found)


@pytest.mark.skipif(not (REAL_WEIGHTS / "onnx" / "model.onnx").is_file(),
                    reason="the published GLiNER weights are machine state, not "
                           "repository state; this deployment has not fetched them")
def test_a_diagnosis_on_page_three_of_a_unit_is_read():
    """THE CASE THE GATE EXISTS FOR, against the real weights.

    `104` §18.56: four health forms were released to the cloud on the rules' word
    alone. A reader that encoded once would see the first 384 sub-tokens of each and
    report its silence about the rest as an absence -- so this plants a person and a
    diagnosis at character 3,000 of a 4,000-character unit, which is the fourth
    window, and asks for them back. Measured while writing it: 1.1 s for the 4,000
    characters, and both are found at 1.000 and 0.992.
    """
    filler = (
        "The quarterly infrastructure review focused on latency improvements across "
        "the regional caching layer. Further testing is planned before the change is "
        "rolled out to every availability zone. The team agreed to reconvene after "
        "the next sprint to compare results against the baseline configuration. ")
    planted = ("The patient, Marcus Lindqvist, was assessed and found to have "
               "generalized anxiety disorder.")
    page = (filler * 40)[:4_000]
    page = (page[:3_000] + planted + page[3_000 + len(planted):])[:4_000]
    assert page[3_000:3_000 + len(planted)] == planted, "the fixture plants it there"

    reader = GlinerEntities(
        REAL_WEIGHTS, labels=("person", "medical condition"), score_floor=0.7,
        threads=2)
    found = reader.entities(page)
    by_label = {one.label: one for one in found}

    assert by_label["person"].text == "Marcus Lindqvist"
    assert by_label["medical condition"].text == "generalized anxiety disorder"
    assert by_label["person"].start > 3_000, "the point is that it is late in the unit"
    assert all(page[one.start:one.end] == one.text for one in found)


@pytest.mark.skipif(not (REAL_WEIGHTS / "onnx" / "model.onnx").is_file(),
                    reason="the published GLiNER weights are machine state, not "
                           "repository state; this deployment has not fetched them")
def test_a_dense_thousand_characters_is_read_whole_and_not_a_shape_error():
    """The window arithmetic, against the graph rather than against a stub.

    `gliner_config.json` caps the encoder at 384 sub-tokens, and a thousand
    characters of account numbers, hyphenated addresses and punctuation is far more
    than 384 word-pieces -- so this text takes several windows where the prose above
    takes fewer. A `text_lengths` built from the PRE-tokenized word count asks the
    graph about words whose vectors were never computed, which is a shape error on
    the fortieth file of a real corpus or, worse, spans over text the model did not
    read.
    """
    reader = GlinerEntities(
        REAL_WEIGHTS, labels=("person", "date of birth", "account number",
                              "home address", "email address"),
        score_floor=0.7, threads=2)
    dense = ("Acct 4471-9928-1130-2265/MRN-88231045-Z;DOB 02/29/1992;"
             "+1(415)555-0192;sarah.whitfield.records@example.co.uk;"
             "56-Cambridge-Court,Flat-2,Manchester,M14-5TP;") * 12
    dense = dense[:1_000]

    found = reader.entities(dense)
    assert found, "the truncated prefix still holds entities"
    assert all(one.end <= len(dense) for one in found)
    assert all(dense[one.start:one.end] == one.text for one in found)
