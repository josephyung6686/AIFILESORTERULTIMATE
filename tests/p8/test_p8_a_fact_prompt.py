# tests/p8/test_p8_a_fact_prompt.py
"""The ratified A_fact prompt: the bytes, and what they are still not enough for.

The owner ratified this text on 2026-09-02 (`planning/82-FACT-PROMPT-DRAFT.md` §0):
`82` §2's block with `planning/90-PROMPT-BAKEOFF.md` C2's one-sentence delta
applied -- 7,349 bytes, 1,242 words, sha256 `e4fe6d12...ae10`.

**The first test is the one that matters.** Pinning the digest alone would say only
that the file has not changed since somebody typed a digest for it; it would pass
just as well over text nobody ratified. So the first test RE-DERIVES the bytes from
the ratification documents themselves -- `82` §2's fenced block, plus `90` C2's
delta applied exactly once -- and asserts the shipped file equals the result. What
is pinned is not a number but a route back to the thing the owner read.

**The last test is the honest half.** These bytes do not make a `PromptDefinition`.
`records.py` refuses an empty `response_schema_bytes` and an empty
`shaping_policy_bytes`, both of which are shown to the model inside the same dossier
(`dossier._body`'s `response_schema` and `shaping_policy` keys) and are the owner's
text on the same grounds as the template (`82` §6.5). Nothing in `src/` authors
either. The refusal is pinned here so the blocker is a red test if someone removes
it, rather than a paragraph in a report.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from llm_harness.prompt_library import (
    A_FACT_TEMPLATE_FILE,
    A_FACT_TEMPLATE_SHA256,
    RatifiedTextChanged,
    RatifiedTextMissing,
    _read,
    a_fact_template_bytes,
)
from llm_harness.records import MalformedRecord, PromptDefinition
from llm_harness.vocabulary import A_FACT


REPO = Path(__file__).resolve().parents[2]
DRAFT = REPO / "planning/82-FACT-PROMPT-DRAFT.md"

#: `90` §3's C2 delta, quoted from `82` §0's ratification note. The sentence that
#: was in `WHAT THE DOSSIER CONTAINS`, and the sentence the owner put in its place.
C2_OLD = ("It is a definition and it is not evidence: nothing written in it may be "
          "quoted, and a word that appears only there is not a value you found.")
C2_NEW = ("Read it to work out which key names the thing you found. It is a "
          "definition and it is not evidence, so no part of it may be cited as a "
          "span and a word that appears only there is not a value you found.")

#: `90` §3's table. C0 is `82` §2 extracted from its fenced block; C2 is C0 plus
#: the delta above.
C0_SHA256 = "e4f92fbadb0d01078f70e526ed0ab0c88521e35a81a1c1d61015795e8fafc547"
C0_BYTES, C0_WORDS = 7289, 1226
C2_BYTES, C2_WORDS = 7349, 1242


def _c0() -> str:
    """`82` §2's block, by `90` §3's method: split on the fence, take part 1."""
    return DRAFT.read_text(encoding="utf-8").split("~~~~\n")[1]


def test_the_shipped_bytes_are_the_text_the_owner_ratified():
    """Re-derived from the documents, not compared against a typed digest.

    The C0 assertions are not decoration: they are what proves the fence split
    found `82` §2 and not some other block. A wrong split that happened to hash to
    the C2 digest is not a thing that can happen, but a wrong split that produced
    plausible-looking prose is, and this is where it would be caught.
    """
    c0 = _c0()
    assert hashlib.sha256(c0.encode("utf-8")).hexdigest() == C0_SHA256
    assert len(c0.encode("utf-8")) == C0_BYTES
    assert len(c0.split()) == C0_WORDS

    # Exactly once. A delta that matched twice, or not at all, would mean the
    # extraction or the quoted sentence is wrong, and applying it anyway would
    # produce bytes nobody ratified.
    assert c0.count(C2_OLD) == 1
    c2 = c0.replace(C2_OLD, C2_NEW)

    assert A_FACT_TEMPLATE_FILE.read_bytes() == c2.encode("utf-8")
    assert len(c2.encode("utf-8")) == C2_BYTES
    assert len(c2.split()) == C2_WORDS
    assert hashlib.sha256(c2.encode("utf-8")).hexdigest() == A_FACT_TEMPLATE_SHA256


def test_the_loader_returns_those_exact_bytes():
    loaded = a_fact_template_bytes()

    assert isinstance(loaded, bytes)
    assert loaded == A_FACT_TEMPLATE_FILE.read_bytes()
    assert hashlib.sha256(loaded).hexdigest() == A_FACT_TEMPLATE_SHA256
    assert len(loaded) == C2_BYTES
    # R1: the template supplies its own terminator and the dossier's `{` is the
    # next byte (`records.assemble` concatenates with no separator).
    assert loaded.endswith(b"\n") and not loaded.endswith(b"\n\n")


def test_a_changed_byte_is_refused_rather_than_loaded(tmp_path):
    """The check earns its place only if it fires. Three ways to break the file."""
    original = A_FACT_TEMPLATE_FILE.read_bytes()

    flipped = tmp_path / "one_byte.txt"
    flipped.write_bytes(original[:-2] + b"X" + original[-1:])
    with pytest.raises(RatifiedTextChanged) as changed:
        _read(flipped, A_FACT_TEMPLATE_SHA256)
    assert A_FACT_TEMPLATE_SHA256 in str(changed.value)
    # Never echo 7KB of prompt into an exception: what a reader needs is which
    # file and which digest.
    assert b"fact extractor" not in str(changed.value).encode("utf-8")

    # The quiet edit this file's shape exists to prevent: a stripped trailing
    # newline, which no reviewer sees in a diff.
    stripped = tmp_path / "no_terminator.txt"
    stripped.write_bytes(original.rstrip(b"\n"))
    with pytest.raises(RatifiedTextChanged):
        _read(stripped, A_FACT_TEMPLATE_SHA256)

    with pytest.raises(RatifiedTextMissing):
        _read(tmp_path / "not_here.txt", A_FACT_TEMPLATE_SHA256)


def test_the_public_loader_is_wired_to_that_same_check(monkeypatch, tmp_path):
    """Not a separate path. The cached entry point refuses what `_read` refuses."""
    sabotaged = tmp_path / "sabotaged.txt"
    sabotaged.write_bytes(A_FACT_TEMPLATE_FILE.read_bytes() + b"\n")
    monkeypatch.setattr(
        "llm_harness.prompt_library.A_FACT_TEMPLATE_FILE", sabotaged)
    a_fact_template_bytes.cache_clear()
    try:
        with pytest.raises(RatifiedTextChanged):
            a_fact_template_bytes()
    finally:
        monkeypatch.undo()
        a_fact_template_bytes.cache_clear()

    # And the real file still loads once the sabotage is undone, so the test
    # leaves no poisoned cache entry behind for whatever runs next.
    assert a_fact_template_bytes() == A_FACT_TEMPLATE_FILE.read_bytes()


def test_the_ratified_bytes_alone_do_not_make_a_prompt_definition():
    """Where installation stops today, and why. `82` §6.5.

    `response_schema_bytes` and `shaping_policy_bytes` are separate injected byte
    strings, both serialised into the dossier the model reads (`dossier._body`), and
    `response_schema_bytes` is also folded into `dossier_content_address`, so it is
    inside every `dossier_id`. If they describe a different shape from the
    template's own `THE SHAPE`, the model is shown two schemas and picks one. They
    are the owner's text on the same grounds as the template, and no part of this
    project may author them on his behalf.
    """
    template = a_fact_template_bytes()

    with pytest.raises(MalformedRecord) as no_schema:
        PromptDefinition(
            template_id="prompt.a_fact.c2", template_bytes=template,
            response_schema_bytes=b"", call_site=A_FACT,
            call_site_version="1", shaping_policy_bytes=b"placeholder")
    assert "response_schema_bytes" in str(no_schema.value)

    with pytest.raises(MalformedRecord) as no_policy:
        PromptDefinition(
            template_id="prompt.a_fact.c2", template_bytes=template,
            response_schema_bytes=b"placeholder", call_site=A_FACT,
            call_site_version="1", shaping_policy_bytes=b"")
    assert "shaping_policy_bytes" in str(no_policy.value)

    # The template half of the same construction is satisfied, which is what the
    # ratification bought and the whole of what it bought.
    with pytest.raises(MalformedRecord) as no_template:
        PromptDefinition(
            template_id="prompt.a_fact.c2", template_bytes=b"",
            response_schema_bytes=b"placeholder", call_site=A_FACT,
            call_site_version="1", shaping_policy_bytes=b"placeholder")
    assert "template_bytes" in str(no_template.value)
