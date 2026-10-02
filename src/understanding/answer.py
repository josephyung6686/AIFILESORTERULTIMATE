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


def _one_string(value, key: str) -> str:
    """A string, or a one-element list of a string. Anything else is rejected.

    A live model returned `concerns` as `["user"]`. Membership-testing that
    list raises TypeError, and that error is not an answer.
    """
    if isinstance(value, str):
        return value
    if (isinstance(value, (list, tuple)) and len(value) == 1
            and isinstance(value[0], str)):
        return value[0]
    raise AnswerRejected(
        f"{key} must be one string, not {type(value).__name__}")


def _confidence(value) -> float:
    if isinstance(value, (list, tuple)) and len(value) == 1:
        value = value[0]
    if isinstance(value, bool) or isinstance(value, (list, tuple, dict)):
        raise AnswerRejected("confidence is not a number")
    if isinstance(value, str) and value.strip().endswith("%"):
        try:
            number = float(value.strip()[:-1]) / 100.0
        except ValueError as problem:
            raise AnswerRejected("confidence is not a number") from problem
    else:
        try:
            number = float(value)
        except (TypeError, ValueError) as problem:
            raise AnswerRejected("confidence is not a number") from problem
    return number


def interpret_answer(raw: str, *, file_id: str,
                     declared_areas: set[str]) -> Understanding:
    parsed = _object(raw)
    concerns = _one_string(parsed["concerns"], "concerns")
    if concerns not in CONCERNS:
        raise AnswerRejected(
            f"concerns must be one of {sorted(CONCERNS)}")
    confidence = _confidence(parsed["confidence"])
    if not 0.0 <= confidence <= 1.0:
        raise AnswerRejected("confidence is outside 0 to 1")
    quote = _one_string(parsed["evidence_quote"], "evidence_quote")
    if "\n" in quote or not quote.strip():
        raise AnswerRejected("evidence_quote must be one non-empty line")
    kind = _one_string(parsed["kind"], "kind")
    if not kind.strip():
        raise AnswerRejected("kind is empty")
    area = _one_string(parsed["life_area"], "life_area")
    if not area.strip():
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
        if isinstance(value, (list, tuple)) and len(value) == 1 and isinstance(value[0], str):
            value = value[0]
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
