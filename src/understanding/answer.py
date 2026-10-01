# src/understanding/answer.py
"""What a classification answer is allowed to say.

The model may choose a life area the person declared, or `needs_review`.
It may not invent a category. Business is not a fallback: `business` and
`business_operations` are ordinary names, accepted only when declared.
Low confidence is needs-review, with a reason. Malformed JSON is rejected.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

CONFIDENCE_FLOOR: float = 0.6

REQUIRED: tuple[str, ...] = (
    "kind",
    "life_area",
    "concerns",
    "confidence",
    "evidence_quote",
)
CONCERNS: frozenset[str] = frozenset({"user", "someone_else", "unknown"})
NEEDS_REVIEW: str = "needs_review"


class AnswerRejected(ValueError):
    """The model's output is not an answer."""


@dataclass(frozen=True, slots=True)
class Understanding:
    file_id: str
    kind: str
    life_area: str
    course: str | None
    term: str | None
    company: str | None
    project: str | None
    concerns: str
    confidence: float
    evidence_quote: str
    needs_review: bool
    reason: str


def _object(raw: str) -> dict:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as problem:
        raise AnswerRejected("the model did not return JSON") from problem
    if not isinstance(parsed, dict):
        raise AnswerRejected("the model did not return a JSON object")
    missing = [key for key in REQUIRED if key not in parsed]
    if missing:
        raise AnswerRejected(
            "the model left out " + ", ".join(missing))
    return parsed


def interpret_answer(raw: str, *, file_id: str,
                     declared_areas: set[str]) -> Understanding:
    parsed = _object(raw)
    concerns = parsed["concerns"]
    if concerns not in CONCERNS:
        raise AnswerRejected(
            f"concerns must be one of {sorted(CONCERNS)}")
    try:
        confidence = float(parsed["confidence"])
    except (TypeError, ValueError) as problem:
        raise AnswerRejected("confidence is not a number") from problem
    if not 0.0 <= confidence <= 1.0:
        raise AnswerRejected("confidence is outside 0 to 1")
    quote = parsed["evidence_quote"]
    if not isinstance(quote, str) or "\n" in quote or not quote.strip():
        raise AnswerRejected("evidence_quote must be one non-empty line")
    kind = parsed["kind"]
    if not isinstance(kind, str) or not kind.strip():
        raise AnswerRejected("kind is empty")
    area = parsed["life_area"]
    if not isinstance(area, str) or not area.strip():
        raise AnswerRejected("life_area is empty")
    declared = {name.casefold(): name for name in declared_areas}
    needs = False
    reason = ""
    if area.casefold() == NEEDS_REVIEW:
        needs = True
        reason = "the model returned needs_review"
        canonical = NEEDS_REVIEW
    elif area.casefold() not in declared:
        # Not accepted as a category, including business when it was not declared.
        needs = True
        reason = (
            f"{area!r} is not one of the declared areas "
            f"{sorted(declared_areas)}; needs review")
        canonical = NEEDS_REVIEW
    else:
        canonical = declared[area.casefold()]
    if confidence < CONFIDENCE_FLOOR:
        needs = True
        reason = reason or (
            f"confidence {confidence} is below {CONFIDENCE_FLOOR}")
    def optional(key: str) -> str | None:
        value = parsed.get(key)
        if value is None or value == "":
            return None
        if not isinstance(value, str):
            raise AnswerRejected(f"{key} must be a string or empty")
        return value

    return Understanding(
        file_id=file_id,
        kind=kind.strip(),
        life_area=canonical,
        course=optional("course"),
        term=optional("term"),
        company=optional("company"),
        project=optional("project"),
        concerns=concerns,
        confidence=confidence,
        evidence_quote=quote.strip(),
        needs_review=needs,
        reason=reason,
    )
