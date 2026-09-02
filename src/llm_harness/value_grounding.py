# src/llm_harness/value_grounding.py
"""Does the proposed value's text come from the released text the claim cites?

`86` §4 found that **the proposed `value` is never compared to the citation or to
any released text**, and `90` §5 ranks a check that does so first among the things
that would help. A model can copy a real span, propose a value that appears nowhere
in it -- including a word it read off `field_glossary` -- and be accepted.

**What this module claims, exactly.** The value's characters, read without case and
without separators, occur as a whole-token run of a released value THIS CLAIM CITES.
Nothing more. It is a text comparison and it is deliberately not a judgement about
meaning: `90` §2.2 records that a lifted `"screenshot"` and a found one can produce
the identical pair, and several of the glossary's enumerated words are ordinary
English, so this narrows the hazard where the word is absent and cannot close it
where the word is present.

**Why a token RUN and not a substring.** `"form"` is one of
`application_document_type`'s enumerated words and it is inside `"information"`,
`"formal"` and `"performed"`; `"field"` is inside `"fields"`. A substring test over
folded text accepts every one of those, which would be a check that passes the
defect. A token run does not.

**Why separators are dropped rather than matched.** `PHYS 1401`, `PHYS-1401` and
`PHYS1401` are one course code -- `65` §4.2 is on this project's record for what
happens when one identity arrives as several spellings, and `cli.normalize_for_model`
exists to fold them together. A comparison that did not fold them would reject a
correct answer for the spelling of a space, which is the failure mode `84` §5 names:
a guard too strict in one direction is not a guard.

**No threshold, no ratio and no numeric literal.** The rule is a universal
quantification over the cited items, not a score. Where a real deployment fact is
needed -- which characters separate words in a script that does not use spaces --
this module refuses rather than guesses, and the refusal is recorded in
`test_p8_value_grounding.py` rather than hidden.
"""
from __future__ import annotations

from collections.abc import Sequence

from llm_harness.records import Citation, ReleasedEvidence


def grounding_tokens(text: object) -> tuple[str, ...]:
    """The comparable tokens of one piece of text: alphanumeric runs, casefolded.

    Every non-alphanumeric character is a separator and none of them survives, so
    `AY 2024-25` and `AY2024-25` produce token streams that concatenate to the same
    characters. A string with no alphanumeric character produces no tokens, and a
    caller reads that as "nothing to compare", never as "compares equal".

    **The known limitation, stated where the code is rather than in a document.**
    A script that does not separate words -- Han, Kana, Thai -- has no separator to
    split on, so its whole run is ONE token and a value that is a genuine part of it
    will not match. Splitting those per character would be right for them and wrong
    for every script that does use spaces (`форма` is inside `информация`), so which
    characters separate words is a locale fact this package will not invent.
    """
    if not isinstance(text, str):
        return ()
    tokens: list[str] = []
    current: list[str] = []
    for char in text:
        if char.isalnum():
            current.append(char)
        elif current:
            tokens.append("".join(current))
            current = []
    if current:
        tokens.append("".join(current))
    return tuple(token.casefold() for token in tokens)


def occurs_in(value: object, text: object) -> bool:
    """Whether `value`'s characters are a whole-token run of `text`.

    The run must be contiguous and must start and end on token boundaries. Both
    sides are folded first, so `PHYS 1401` occurs in `PHYS1401 Problem Set 4` and
    `PHYS1401` occurs in `PHYS 1401`, and neither `form` nor `field` occurs in
    `information filed under three fields`.
    """
    wanted = "".join(grounding_tokens(value))
    if not wanted:
        return False
    tokens = grounding_tokens(text)
    for start in range(len(tokens)):
        run = ""
        for token in tokens[start:]:
            run += token
            if len(run) > len(wanted):
                break
            if run == wanted:
                return True
    return False


def cited_released_values(
    citations: Sequence[Citation],
    released_evidence: Sequence[ReleasedEvidence],
) -> tuple[str, ...]:
    """The released text of the items THIS CLAIM cites, in the release's own order.

    The bound is the citations and not the whole dossier on purpose. A dossier can
    release several items; a value grounded in one the model did not cite is a value
    the model did not say where it got, and the citation is the only place it says.
    """
    cited = {citation.evidence_ref for citation in citations}
    return tuple(
        item.value for item in released_evidence
        if item.observation_key in cited and isinstance(item.value, str)
    )


def value_is_grounded(
    raw_value: object,
    normalized_value: object,
    *,
    citations: Sequence[Citation],
    released_evidence: Sequence[ReleasedEvidence],
) -> bool:
    """The check: does either spelling of the value occur in a cited released value?

    **Both spellings are tried, and that is the permissive half on purpose.** The
    model proposes what it read; `cli.normalize_for_model` canonicalises it, and the
    canonical form need not resemble the text (`Spring 2026` becomes `Spring2026`).
    Asking only for the canonical form would reject a correct reading for the shape
    of this deployment's own normaliser; asking only for the raw form would reject a
    model that proposed the canonical spelling directly. Either grounds it.

    An empty citation list, a claim citing nothing that was released, or a value with
    no comparable characters is NOT grounded. Absent means refuse.
    """
    texts = cited_released_values(citations, released_evidence)
    if not texts:
        return False
    return any(
        occurs_in(candidate, text)
        for candidate in (raw_value, normalized_value)
        for text in texts
    )
