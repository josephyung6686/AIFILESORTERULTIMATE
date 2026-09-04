# src/readers/embedding_minilm.py
"""DEPLOYMENT. The sentence encoder, and the only file that imports one.

`pyproject.toml` keeps `dependencies = []` and puts every third-party library in
this package, because "every format reader is a caller-supplied callable, so the
libraries are installed by a deployment that chose them, never by the part that
consumes their output". A sentence encoder is the same kind of thing as a PDF
reader: `recognition.semantic` holds every rule and never learns what a vector is
made of, and this holds the model and no rule at all.

WHAT WAS CHOSEN, AND WHAT WAS REJECTED, ON MEASUREMENT.

`all-MiniLM-L6-v2`, as ONNX, run by `onnxruntime`. 6 layers, 384 dimensions,
Apache-2.0, 90.4 MB. It was chosen because `onnxruntime`, `tokenizers`, `numpy`
and `huggingface_hub` are ALREADY installed on this machine and `torch` is not:
the model runs with no new heavyweight dependency and no compiler.

  * `sentence-transformers` was rejected: it pulls `torch`, which is a ~2.5 GB
    install for a 90 MB model, to run the same weights this file runs.
  * `spacy`'s `en_core_web_md` was rejected: it is averaged GloVe word vectors,
    which have no sentence order and no sub-word units, and the case this exists
    to fix is `HW 9.pdf` -- a token GloVe does not have.
  * TF-IDF or hashing plus SVD, from the installed `scikit-learn`, was rejected on
    the same case. It is lexical matching with a rotation applied: `HW` and
    `homework` share no character n-gram worth the name, and the whole reason
    this path exists is that lexical matching answers no on that file.

NOTHING LEAVES THE DEVICE AT INFERENCE. `onnxruntime` opens no socket, and the
weights are read from a LOCAL DIRECTORY this file is handed -- it does not locate,
download or default one. The 90.4 MB was fetched ONCE from huggingface.co (repo
`sentence-transformers/all-MiniLM-L6-v2`), and the deployment that fetched it is
the deployment that names the path.

A VECTOR OF A DOCUMENT IS DERIVED FROM ITS TEXT AND IS NOT RELEASABLE. It is
computed here, stored by P1 and scored locally. Nothing in this file sends one
anywhere, and the nine `ALWAYS_LOCAL` kinds are as local in 384 floats as they are
in words: mean-pooled MiniLM embeddings are invertible enough to recover the gist
of a short document, so a vector of a payslip is a payslip in a lossier coat.
"""
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

#: The two files a run needs, and the names they carry in the published repo.
MODEL_FILE: str = "model.onnx"
TOKENIZER_FILE: str = "tokenizer.json"


class ModelUnavailable(RuntimeError):
    """The weights, the tokenizer or the runtime are not on this machine.

    Raised at CONSTRUCTION and never at classification time. A deployment that
    cannot encode must find out while it is being assembled, not on the four
    hundredth file of somebody's Downloads folder.
    """


class MiniLmEncoder:
    """One loaded model. `encode` is the whole of its interface.

    `max_tokens` and `batch` are the caller's: the first decides how much of a
    document reaches the model at all, and the second is a speed/memory trade the
    machine owns rather than this file.
    """

    def __init__(self, model_dir, *, max_tokens: int, batch: int,
                 threads: int) -> None:
        directory = Path(model_dir)
        model, tokenizer = directory / MODEL_FILE, directory / TOKENIZER_FILE
        for path in (model, tokenizer):
            if not path.is_file():
                raise ModelUnavailable(
                    f"{path} is missing. This file names no download and no "
                    f"default location: the deployment that fetched the weights "
                    f"is the one that says where they are")
        for name, value in (("max_tokens", max_tokens), ("batch", batch),
                            ("threads", threads)):
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        try:
            import onnxruntime  # noqa: PLC0415  a deployment import, by design
            from tokenizers import Tokenizer  # noqa: PLC0415
        except ImportError as problem:  # pragma: no cover - environment shape
            raise ModelUnavailable(
                "onnxruntime and tokenizers are this deployment's choice and are "
                f"not installed: {problem}") from problem

        self._tokenizer = Tokenizer.from_file(str(tokenizer))
        self._tokenizer.enable_truncation(max_length=max_tokens)
        self._tokenizer.enable_padding(length=None)
        options = onnxruntime.SessionOptions()
        options.intra_op_num_threads = threads
        options.inter_op_num_threads = threads
        # CPU only, named rather than left to the provider list. A run must not
        # start using an accelerator because one appeared on the machine.
        self._session = onnxruntime.InferenceSession(
            str(model), options, providers=["CPUExecutionProvider"])
        self._inputs = {spec.name for spec in self._session.get_inputs()}
        self._batch = batch
        self.dimension = int(self._session.get_outputs()[0].shape[-1])
        #: What a vector was computed BY, for P9's `model_version`. The digest of
        #: the weights themselves: a model file swapped in place moves this, and a
        #: reinstall of the same weights does not.
        self.weights_digest = hashlib.sha256(model.read_bytes()).hexdigest()[:16]

    def encode(self, texts: Sequence[str]):
        """Unit-norm mean-pooled vectors, one per text, as a numpy array.

        Mean pooling over the attention mask is what `all-MiniLM-L6-v2` was
        trained and published to be read with; CLS pooling on the same weights is
        a different and worse model. Unit-norm because every consumer here wants a
        cosine, and a normalised dot product IS one.
        """
        import numpy  # noqa: PLC0415

        if not texts:
            return numpy.zeros((0, self.dimension), dtype=numpy.float32)
        out = []
        for start in range(0, len(texts), self._batch):
            chunk = [text for text in texts[start:start + self._batch]]
            encoded = self._tokenizer.encode_batch(chunk)
            ids = numpy.array([one.ids for one in encoded], dtype=numpy.int64)
            mask = numpy.array([one.attention_mask for one in encoded],
                               dtype=numpy.int64)
            feed = {"input_ids": ids, "attention_mask": mask}
            if "token_type_ids" in self._inputs:
                feed["token_type_ids"] = numpy.zeros_like(ids)
            hidden = self._session.run(None, feed)[0]
            weights = mask[..., None].astype(numpy.float32)
            pooled = (hidden * weights).sum(1) / numpy.clip(weights.sum(1), 1e-9, None)
            pooled /= numpy.clip(numpy.linalg.norm(pooled, axis=1, keepdims=True),
                                 1e-9, None)
            out.append(pooled.astype(numpy.float32))
        return numpy.concatenate(out)

    def encode_one(self, text: str) -> tuple[float, ...]:
        """`recognition.semantic`'s `encode` seam: one string, plain floats."""
        return tuple(float(value) for value in self.encode([text])[0])


@dataclass(frozen=True)
class AnchorIndex:
    """The library's own terms as points, and which schema each point belongs to.

    A SCHEMA IS ITS UNNORMALISED CENTROID, and both halves of that were measured
    against the alternatives on the 199-file ground-truth corpus.

    NOT the nearest anchor. Max-over-anchors was written first, on the reasoning
    that `academic` authored `syllabus`, `individualized education program` and
    `seal of the university` and their mean is near none of them. It scores 15.6%
    top-1 where the centroid scores 29.1%, and the reason is arithmetic rather
    than semantic: the schemas are wildly unequal in size -- `law_practice` has
    1,143 anchors and `code` has 41 -- and a maximum over more draws is larger for
    no reason to do with the file. It predicted `law_practice` and
    `construction_property` most often on a corpus that is mostly coursework.

    NOT normalised. Dividing the centroid by its length costs 10 points (29.1% to
    18.6%), because the length is carrying real information: a schema whose anchors
    all point one way has a long centroid, and one whose anchors point everywhere
    -- the prose-heavy rows -- has a short one. Normalising deletes exactly the
    signal that says which schemas are coherent enough to be trusted.
    """

    labels: tuple[str, ...]
    #: (n, d) unit-norm float32, one row per anchor. Kept for `nearest_anchor`,
    #: which is how a proposal gets read; the scoring uses `centroids`.
    matrix: object
    texts: tuple[str, ...]
    #: (schemas, d), UNNORMALISED, in `schemas` order.
    centroids: object
    schemas: tuple[str, ...]

    def scores_for(self, vector: Sequence[float]) -> Mapping[str, float]:
        """Each schema's centroid against this vector. NOT a cosine.

        The document vector is unit-norm and the centroids are not, so this is a
        cosine scaled by each schema's coherence -- bounded above by 1, since a
        mean of unit vectors is no longer than one, but reaching it only for a
        schema whose every anchor points the same way. That scaling is deliberate
        (see the class docstring) and it is why the caller's floors are small
        numbers: 0.10 here is not 0.10 of a cosine.
        """
        import numpy  # noqa: PLC0415

        query = numpy.asarray(vector, dtype=numpy.float32)
        norm = float(numpy.linalg.norm(query))
        if norm == 0.0:
            return {}
        scores = self.centroids @ (query / norm)
        return {schema: float(score)
                for schema, score in zip(self.schemas, scores)}

    def nearest_anchor(self, label: str, vector: Sequence[float]) -> str | None:
        """The anchor TEXT that scored a label, so a proposal can be read."""
        import numpy  # noqa: PLC0415

        query = numpy.asarray(vector, dtype=numpy.float32)
        rows = [i for i, name in enumerate(self.labels) if name == label]
        if not rows:
            return None
        similarities = self.matrix[rows] @ query
        return self.texts[rows[int(numpy.argmax(similarities))]]


def build_anchor_index(anchors: Mapping[str, Sequence[str]], encoder: MiniLmEncoder,
                       *, cache_path=None) -> AnchorIndex:
    """Encode the library's terms once, and keep them.

    CACHED ON THE LIBRARY AND THE MODEL TOGETHER. Either changing makes the stored
    vectors wrong, and the cache is keyed on a digest of both, so a stale one is
    not read rather than being detected later by a similarity that quietly moved.
    The cache is the caller's path or nothing; this file locates none.
    """
    import numpy  # noqa: PLC0415

    labels: list[str] = []
    texts: list[str] = []
    for label in sorted(anchors):
        for text in anchors[label]:
            labels.append(label)
            texts.append(text)
    if not texts:
        raise ValueError(
            "no anchors: the library carries the terms and this encodes them, so "
            "an empty index means the manifest was not loaded")
    digest = hashlib.sha256()
    digest.update(encoder.weights_digest.encode("utf-8"))
    digest.update(json.dumps([labels, texts], sort_keys=True).encode("utf-8"))
    key = digest.hexdigest()

    cache = Path(cache_path) if cache_path is not None else None
    if cache is not None and cache.is_file():
        with numpy.load(cache, allow_pickle=False) as stored:
            if str(stored["key"]) == key:
                return _index(labels, texts, stored["matrix"])
    matrix = encoder.encode(texts)
    if cache is not None:
        cache.parent.mkdir(parents=True, exist_ok=True)
        numpy.savez(cache, key=numpy.array(key), matrix=matrix)
    return _index(labels, texts, matrix)


def _index(labels, texts, matrix) -> AnchorIndex:
    """One centroid per schema, computed once where the anchors are."""
    import numpy  # noqa: PLC0415

    names = sorted(set(labels))
    rows = numpy.asarray(labels)
    centroids = numpy.stack([matrix[rows == name].mean(0) for name in names])
    return AnchorIndex(labels=tuple(labels), matrix=matrix, texts=tuple(texts),
                       centroids=centroids, schemas=tuple(names))
