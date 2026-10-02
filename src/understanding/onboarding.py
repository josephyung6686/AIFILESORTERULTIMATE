# src/understanding/onboarding.py
"""Follow-up questions from a names-only harvest.

The harvest is filenames and folder names. No file contents. The same
consent sentence gates this call. The role is reasoning: question
generation, not per-file classification.
"""
from __future__ import annotations

import json
import time

from understanding.backoff import complete_with_backoff
from understanding.provider import CompletionRequest
from understanding.reasoning import read_completion
from understanding.store import STATEMENT


class ConsentRequired(RuntimeError):
    pass


def questions_from_names(names: list[str], *, declared_areas: set[str],
                         provider, model_id: str, consent: bool,
                         sleep=time.sleep, attempts: int = 4) -> dict:
    if not consent:
        raise ConsentRequired(STATEMENT)
    if provider.locality() == "cloud" and not consent:
        raise ConsentRequired(STATEMENT)
    prompt = (
        "Reply with one JSON object and nothing else. Keys: summary "
        "(one paragraph, plain language, what these names suggest), "
        "questions (a list of short follow-up questions). "
        "Use only these names. Do not invent file contents. "
        f"Declared areas: {', '.join(sorted(declared_areas)) or '(none)'}. "
        "Names: " + json.dumps(names)
    )
    payload = complete_with_backoff(provider, CompletionRequest(
        model_id=model_id, prompt=prompt, max_tokens=1024, thinking="disabled"),
        sleep=sleep, attempts=attempts)
    reading = read_completion(payload)
    if reading.retry:
        payload = complete_with_backoff(provider, CompletionRequest(
            model_id=model_id, prompt=prompt, max_tokens=4096,
            thinking="disabled"), sleep=sleep, attempts=attempts)
        reading = read_completion(payload)
        if reading.retry:
            raise ValueError(reading.reason)
    parsed = json.loads(reading.content)
    if not isinstance(parsed, dict) or "summary" not in parsed or "questions" not in parsed:
        raise ValueError("the model did not return a summary and questions")
    if not isinstance(parsed["questions"], list):
        raise ValueError("questions must be a list")
    return {"summary": str(parsed["summary"]),
            "questions": [str(item) for item in parsed["questions"]]}
