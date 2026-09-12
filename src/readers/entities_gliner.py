# src/readers/entities_gliner.py
"""DEPLOYMENT. The local entity encoder, and the only file that imports one.

`00`'s Amendments of 2026-09-11, item 7(b): "a small local entity encoder
(GLiNER-class, ONNX, on the same seam as the semantic encoder) names people,
diagnoses, dates of birth and identity numbers as observations". This is that
encoder and it holds no rule at all: the LABELS it looks for and the SCORE FLOOR
it keeps are the caller's, exactly as `embedding_minilm.MiniLmEncoder` takes its
`max_tokens` from the deployment and never names one.

`pyproject.toml` keeps `dependencies = []` and puts every third-party library in
this package. `onnxruntime`, `tokenizers` and `numpy` are already installed on
this machine and `torch` is not, so this reimplements in numpy the pre- and
post-processing GLiNER 0.2.29 does in torch -- `UniEncoderSpanProcessor`,
`prepare_word_mask`, `prepare_span_idx` and `SpanDecoder.greedy_search` -- rather
than pulling a 2.5 GB framework to run a 1.1 GB model. `gliner` itself was
rejected for exactly that: it is a thin wrapper over these six tensors and one
sigmoid, and the wrapper costs more than the model.

WHICH WEIGHTS, MEASURED, 12 SEP 2026 (the spike, 20 documents, 52 planted
entities, onnxruntime 1.24.4 on the CPU provider). The published repo ships eight
ONNX files and SEVEN OF THEM ARE REFUSED BY NAME:

  * `model.onnx` (fp32) is the one that works: median 115 ms per document, 1.5 s
    to load, 2.36 GB resident, precision/recall 0.72/0.90 at a floor of 0.5 and
    0.80/0.90 at 0.7. This is the file this reader looks for.
  * `model_int8.onnx`, `model_uint8.onnx`, `model_quantized.onnx` LOAD and then
    find nothing: dynamic quantisation collapsed the span head's calibration, the
    best span in the whole corpus scores about 0.35, and recall is 0.04 at a floor
    of 0.5 and zero at 0.7. A reader that fell back to these would be off while
    reporting itself on, which is the one failure mode `ModelUnavailable` exists
    to prevent -- so an int8 file present WITHOUT `model.onnx` is a refusal
    carrying that measurement, never a run.
  * `model_fp16.onnx` and `model_q4f16.onnx` fail at session creation on this
    provider (`SimplifiedLayerNormFusion` names a cast node the graph does not
    have). `model_bnb4.onnx` and `model_q4.onnx` are unmeasured.

NOTHING LEAVES THE DEVICE AT INFERENCE. `onnxruntime` opens no socket, and the
weights are read from a LOCAL DIRECTORY this file is handed -- it does not locate,
download or default one. The deployment that fetched the model is the deployment
that names the path.

AN ENTITY IS THE PERSON'S OWN TEXT AND IS NOT RELEASABLE BECAUSE IT CAME FROM
HERE. This returns spans and scores; whether a span may be recorded whole, as a
tail, or not at all is `extractors/entities.py`'s contract and the privacy gate's
ruling, not this file's.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

#: The three files a run needs, and the names they carry in the published repo.
TOKENIZER_FILE: str = "tokenizer.json"
CONFIG_FILE: str = "gliner_config.json"
WEIGHTS_DIR: str = "onnx"

#: The one weights file measured to work. See this module's docstring for the other
#: seven and the number that refuses each.
WEIGHTS_FILE: str = "model.onnx"

#: The files that are present, load, and are still not usable -- each with the
#: measurement that says so, printed in the refusal so a deployment that fetched only
#: a quantised variant is told what its recall would have been rather than left to
#: discover it as an empty result set.
REFUSED_WEIGHTS: dict[str, str] = {
    "model_int8.onnx": "recall 0.04 at a 0.5 floor, 0.00 at 0.7 (dynamic "
                       "quantisation collapsed the span head: best span ~0.35)",
    "model_uint8.onnx": "the int8 graph under another name; same calibration",
    "model_quantized.onnx": "the int8 graph under another name; same calibration",
    "model_fp16.onnx": "fails at session creation on the CPU provider "
                       "(SimplifiedLayerNormFusion names a cast node the graph "
                       "does not have)",
    "model_q4f16.onnx": "fails at session creation for `model_fp16.onnx`'s reason",
}

#: The graph's own input names, inspected from the published export. Checked at
#: construction rather than trusted: a differently-exported GLiNER would take the
#: same tensors under other names and this reader would silently feed it nothing.
GRAPH_INPUTS: tuple[str, ...] = (
    "input_ids", "attention_mask", "words_mask", "text_lengths", "span_idx",
    "span_mask")

#: GLiNER's `WhitespaceTokenSplitter`, character for character. The word list this
#: produces is the model's coordinate system: `text_lengths`, `span_idx` and the
#: decoded character offsets are all counted in these words, so a different splitter
#: is a different model.
WORD_PATTERN = re.compile(r"\w+(?:[-_]\w+)*|\S")


class ModelUnavailable(RuntimeError):
    """The weights, the tokenizer, the config or the runtime are not on this machine.

    Raised at CONSTRUCTION and never at entity time, for `embedding_minilm`'s
    reason: a deployment that cannot read entities must find out while it is being
    assembled, not on the four hundredth file of somebody's Downloads folder.
    """


@dataclass(frozen=True)
class Entity:
    """One span the model named, in the coordinates of the text it was handed.

    `start` and `end` are half-open character offsets into that text and `text` is
    exactly `source[start:end]`, so a caller can anchor the reading without asking
    this file where it came from. `score` is the sigmoid of the span logit for
    `label` -- the model's own number, on no published scale.
    """

    label: str
    start: int
    end: int
    score: float
    text: str


def weights_in(model_dir) -> Path:
    """`onnx/model.onnx` under this directory, or a refusal naming what was there.

    Module-level and not a method, so a run can say in its header WHICH weights it
    is about to read without building the 2.36 GB session to ask. A filesystem
    question, answered as one.
    """
    directory = Path(model_dir) / WEIGHTS_DIR
    weights = directory / WEIGHTS_FILE
    if weights.is_file():
        return weights
    others = sorted(path.name for path in directory.glob("*.onnx")
                    ) if directory.is_dir() else []
    measured = "; ".join(f"{name}: {REFUSED_WEIGHTS[name]}"
                         for name in others if name in REFUSED_WEIGHTS)
    raise ModelUnavailable(
        f"{weights} is missing and no other export in that directory is usable. "
        f"Present: {others or 'nothing'}."
        + (f" Measured 12 Sep 2026 -- {measured}." if measured else "")
        + " A reader that ran one of those would report itself on and find nothing, "
          "which is worse than being off.")


def available_in(model_dir) -> tuple[Path, dict]:
    """Every check construction makes that does not need the runtime, and the two
    things it found: the weights file and the published config.

    **Separate from `__init__` so a run can be REFUSED before it reads a corpus.**
    Building the reader costs 2.36 GB resident, so `extractors/entities.py`'s pass
    builds it late -- after the scan -- and a person who named a folder with the
    wrong contents would otherwise learn it from a traceback with their whole
    corpus already read. `cli.announce_entity_reader` calls this in the run header
    instead and refuses there, which is `MiniLmEncoder`'s rule ("raised at
    CONSTRUCTION and never at classification time") kept for a reader whose
    construction cannot happen that early.

    The two libraries are checked FIRST and not only the files, so the header's
    promise is exact: everything that can refuse this reader short of the graph
    itself opening has refused by the time this returns.
    """
    try:
        import onnxruntime  # noqa: F401,PLC0415  a deployment import, by design
        import tokenizers  # noqa: F401,PLC0415
    except ImportError as problem:  # pragma: no cover - environment shape
        raise ModelUnavailable(
            "onnxruntime and tokenizers are this deployment's choice and are not "
            f"installed: {problem}") from problem
    directory = Path(model_dir)
    tokenizer_path = directory / TOKENIZER_FILE
    config_path = directory / CONFIG_FILE
    for path in (tokenizer_path, config_path):
        if not path.is_file():
            raise ModelUnavailable(
                f"{path} is missing. This file names no download and no default "
                f"location: the deployment that fetched the weights is the one "
                f"that says where they are")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    for key in ("ent_token", "sep_token", "max_width", "max_len"):
        if key not in config:
            raise ModelUnavailable(
                f"{config_path} carries no {key!r}. The packing is built from the "
                f"config the weights were published with, and guessing one is how a "
                f"model gets fed a sequence it was not trained on")
    return weights_in(directory), config


def words_of(text: str) -> tuple[tuple[str, int, int], ...]:
    """`(word, start, end)` for every word GLiNER's splitter finds, in order."""
    return tuple((found.group(), found.start(), found.end())
                 for found in WORD_PATTERN.finditer(text))


def span_grid(word_count: int, max_width: int):
    """Every span of 1 to `max_width` words, as `(first_word, last_word)` pairs.

    A port of `gliner.data_processing.utils.prepare_span_idx`. The grid is
    `word_count x max_width` rows in a fixed order, INCLUDING the rows that run off
    the end of the text -- the graph's output is shaped by that grid, so the invalid
    rows are kept and marked in `span_mask` rather than dropped, which is what makes
    row `i * max_width + k` mean "the span starting at word i, k+1 words long" for
    both the caller and the model.
    """
    import numpy  # noqa: PLC0415  a deployment import, as everywhere in `readers`

    starts = numpy.repeat(numpy.arange(word_count, dtype=numpy.int64), max_width)
    offsets = numpy.tile(numpy.arange(max_width, dtype=numpy.int64), word_count)
    return numpy.stack([starts, starts + offsets], axis=1)


def word_mask(word_ids: Sequence[int | None], prompt_length: int) -> list[int]:
    """Which sub-token carries each DOCUMENT word, 1-based, 0 for everything else.

    A port of `gliner.data_processing.utils.prepare_word_mask` at
    `subtoken_pooling = "first"`, which is what `gliner_config.json` says this model
    was trained with. Every sub-token that is not the first of its word is 0, and so
    is every word of the label prompt, so the graph pools one vector per document
    word and the prompt's own words are addressed separately by the label head.
    """
    mask: list[int] = []
    previous = None
    seen = 0
    for word_id in word_ids:
        if word_id is None:
            mask.append(0)
        else:
            first = word_id != previous
            if first:
                seen += 1
            mask.append(seen - prompt_length if first and seen > prompt_length else 0)
        previous = word_id
    return mask


def overlaps(one: tuple[int, int], other: tuple[int, int]) -> bool:
    """Whether two word spans touch. `gliner.decoding.utils.has_overlapping`."""
    return not (one[0] > other[1] or other[0] > one[1])


def greedy_non_overlapping(found: Sequence[Entity]) -> tuple[Entity, ...]:
    """The highest-scoring spans that do not overlap, in reading order.

    `gliner.decoding.decoder.BaseDecoder.greedy_search` at `flat_ner = True`, which
    is the mode this reader wants: a passport number that is ALSO scored as an
    account number is one thing in the document, and offering both would let a
    consumer count one identifier twice. The strongest reading wins and the rest of
    the overlap goes; ties keep the earlier row, which is `sorted`'s own stability
    over the grid's fixed order, so two runs of one corpus decide the same way.
    """
    kept: list[Entity] = []
    taken: list[tuple[int, int]] = []
    for entity in sorted(found, key=lambda one: -one.score):
        here = (entity.start, entity.end)
        if any(overlaps(here, other) for other in taken):
            continue
        kept.append(entity)
        taken.append(here)
    return tuple(sorted(kept, key=lambda one: (one.start, one.end)))


def pack(text: str, labels: Sequence[str], encoding, *, max_width: int):
    """The six tensors the graph takes, from one tokenizer encoding of one text.

    `encoding` is what `tokenizers` returned for the prompt-and-document sequence;
    this function does the arithmetic and opens nothing, so a pin can hand it a
    hand-built encoding and check the packing without a model on disk.

    **THE WORD COUNT IS THE ONE THAT SURVIVED TRUNCATION, and that is the whole
    reason this is not four lines.** `gliner_config.json` caps the encoder at 384
    sub-tokens; the label prompt spends some of them and a dense page can spend the
    rest, so the pre-tokenized word list and the words the model actually saw are
    two different numbers. `text_lengths` and `span_idx` are built from the SURVIVING
    count -- `max(words_mask)`, which is the last document word that kept a first
    sub-token -- because a grid built from the other one asks the graph about words
    whose vectors were never computed, and the answer comes back as spans over text
    the model did not read.
    """
    import numpy  # noqa: PLC0415

    prompt_length = 2 * len(labels) + 1
    mask = word_mask(encoding.word_ids, prompt_length)
    word_count = max(mask) if mask else 0
    grid = span_grid(word_count, max_width)
    valid = grid[:, 1] < word_count
    feed = {
        "input_ids": numpy.array([encoding.ids], dtype=numpy.int64),
        "attention_mask": numpy.array([encoding.attention_mask], dtype=numpy.int64),
        "words_mask": numpy.array([mask], dtype=numpy.int64),
        "text_lengths": numpy.array([[word_count]], dtype=numpy.int64),
        "span_idx": grid[None, :, :],
        "span_mask": valid[None, :],
    }
    return feed, word_count


def decode(logits, *, words, grid, valid, labels: Sequence[str], text: str,
           score_floor: float) -> tuple[Entity, ...]:
    """`logits` (1, L, K, C) to entities, through the sigmoid, the floor and greed.

    The graph emits a logit per (start word, width, label). A sigmoid makes each one
    a probability of its own -- the head is trained with binary cross-entropy per
    label, so these are NOT a distribution over labels and are not normalised across
    C. `score_floor` is the caller's and there is no default: a floor is a
    deployment's measured trade between precision and recall, and this file has
    measured nothing about the caller's corpus.
    """
    import numpy  # noqa: PLC0415

    rows = numpy.asarray(logits)[0]
    length, width, kinds = rows.shape
    scores = 1.0 / (1.0 + numpy.exp(-rows.reshape(length * width, kinds)))
    above = numpy.asarray(valid)[:, None] & (scores > score_floor)
    found = []
    for row, column in zip(*numpy.where(above)):
        first, last = int(grid[row, 0]), int(grid[row, 1])
        start, end = words[first][1], words[last][2]
        found.append(Entity(label=labels[column], start=start, end=end,
                            score=float(scores[row, column]), text=text[start:end]))
    return greedy_non_overlapping(found)


class GlinerEntities:
    """One loaded model. `entities` is the whole of its interface.

    `labels` and `score_floor` are the caller's for `MiniLmEncoder`'s reason: the
    library of kinds a deployment cares about and the number it accepts a reading at
    are both measurements about a corpus, and this file has seen none. `threads` is
    required rather than defaulted for the same reason -- a default here would be a
    deployment number invented inside `src/`.

    `session` exists so a pin can drive the packing and the decoding without 1.1 GB
    of weights: hand in anything with `get_inputs()` and `run()` and the directory is
    still read for the tokenizer and the config, which is what the packing depends
    on. A caller that passes one is responsible for what it returns.
    """

    def __init__(self, model_dir, *, labels: Sequence[str], score_floor: float,
                 threads: int, session=None) -> None:
        directory = Path(model_dir)
        self.labels = tuple(labels)
        if not self.labels:
            raise ValueError(
                "labels are the caller's whole question: this reader asks the model "
                "which of THESE kinds a span is, and an empty list asks nothing")
        if not isinstance(score_floor, (int, float)) or isinstance(score_floor, bool):
            raise ValueError("score_floor is the deployment's measured number")
        if not isinstance(threads, int) or isinstance(threads, bool) or threads <= 0:
            raise ValueError("threads must be a positive integer")
        self.score_floor = float(score_floor)
        weights, config = available_in(directory)
        self._ent_token = str(config["ent_token"])
        self._sep_token = str(config["sep_token"])
        self._max_width = int(config["max_width"])

        # Present, because `available_in` above refused if they were not.
        import onnxruntime  # noqa: PLC0415  a deployment import, by design
        from tokenizers import Tokenizer  # noqa: PLC0415

        self._tokenizer = Tokenizer.from_file(str(directory / TOKENIZER_FILE))
        # The encoder's own ceiling, from its own config. Without it a dense page
        # reaches the graph longer than the position embeddings it was trained with.
        self._tokenizer.enable_truncation(max_length=int(config["max_len"]))
        if session is None:
            options = onnxruntime.SessionOptions()
            options.intra_op_num_threads = threads
            options.inter_op_num_threads = threads
            # CPU only, named rather than left to the provider list, for
            # `embedding_minilm`'s reason: a run must not start using an accelerator
            # because one appeared on the machine.
            session = onnxruntime.InferenceSession(
                str(weights), options, providers=["CPUExecutionProvider"])
        self._session = session
        present = {spec.name for spec in self._session.get_inputs()}
        if present != set(GRAPH_INPUTS):
            raise ModelUnavailable(
                f"the graph at {weights} takes {sorted(present)}; this reader packs "
                f"{sorted(GRAPH_INPUTS)}. A GLiNER export with different inputs is a "
                f"different pre-processing and this file would be feeding it noise")
        #: WHAT AN ENTITY WAS READ BY, for the audit and for the run header. The file
        #: chosen and a digest of its bytes: a model swapped in place moves this, and
        #: a reinstall of the same weights does not.
        self.weights = f"{weights.name}@{_digest_of(weights)}"

    def entities(self, text: str) -> tuple[Entity, ...]:
        """Every entity in `text` above the caller's floor, in reading order."""
        words = words_of(text)
        if not words:
            return ()
        prompt: list[str] = []
        for label in self.labels:
            prompt.extend((self._ent_token, label))
        prompt.append(self._sep_token)
        encoding = self._tokenizer.encode(prompt + [word for word, _, _ in words],
                                          is_pretokenized=True)
        feed, word_count = pack(text, self.labels, encoding,
                                max_width=self._max_width)
        if word_count == 0:
            # The label prompt filled the encoder on its own: nothing of the document
            # reached the graph, so there is nothing to say about it. Silence, not a
            # crash and not an empty claim that the text holds no entities.
            return ()
        logits = self._session.run(None, feed)[0]
        return decode(logits, words=words[:word_count], grid=feed["span_idx"][0],
                      valid=feed["span_mask"][0], labels=self.labels, text=text,
                      score_floor=self.score_floor)


def _digest_of(path: Path) -> str:
    """A digest of the weights, in one-megabyte blocks.

    `MiniLmEncoder` reads its 90 MB model whole; this file is 1.1 GB, so it is read
    in blocks and never held. About two seconds, once per run, which a pass that
    loads a 2.36 GB session and reads a whole corpus can afford and an audit that
    has to say WHICH bytes read the person's documents cannot do without.
    """
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()[:16]
