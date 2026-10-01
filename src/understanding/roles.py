# src/understanding/roles.py
"""The two calls that are not per-file classification.

LOGIC groups files the FAST pass already classified. REASONING resolves a
hard conflict between two candidate areas. Neither invents a life area.
Both require the same consent. Neither is used for the ordinary file.
"""
from __future__ import annotations

import json
import time

from understanding.answer import interpret_answer
from understanding.backoff import complete_with_backoff
from understanding.provider import CompletionRequest
from understanding.reasoning import read_completion
from understanding.store import STATEMENT


class ConsentRequired(RuntimeError):
    pass


def _finish(provider, request, *, sleep, attempts: int):
    payload = complete_with_backoff(
        provider, request, sleep=sleep, attempts=attempts)
    reading = read_completion(payload)
    if reading.retry:
        wider = CompletionRequest(
            model_id=request.model_id, prompt=request.prompt,
            max_tokens=request.max_tokens * 4, thinking="disabled")
        payload = complete_with_backoff(
            provider, wider, sleep=sleep, attempts=attempts)
        reading = read_completion(payload)
        if reading.retry:
            raise ValueError(reading.reason or "empty content")
    return reading


def group_files(rows: list[dict], *, provider, model_id: str,
                declared_areas: set[str], consent: bool,
                sleep=time.sleep, attempts: int = 4) -> dict:
    """LOGIC. `rows` are already-classified `{file_id, life_area, kind}`.

    The model may only emit a declared area or `needs_review`. A group that
    names anything else is dropped to needs_review.
    """
    if not consent:
        raise ConsentRequired(STATEMENT)
    areas = ", ".join(sorted(declared_areas)) or "(none declared)"
    prompt = (
        "Reply with one JSON object and nothing else, of the form "
        "{\"groups\": [{\"life_area\": \"...\", \"file_ids\": [\"...\"], "
        "\"reason\": \"one line\"}]}. "
        f"life_area must be one of: {areas}, or \"needs_review\". "
        "Do not invent a category. Business is not a fallback. "
        "Rows: " + json.dumps(rows)
    )
    reading = _finish(provider, CompletionRequest(
        model_id=model_id, prompt=prompt, max_tokens=1024, thinking="disabled"),
        sleep=sleep, attempts=attempts)
    parsed = json.loads(reading.content)
    groups = parsed.get("groups") if isinstance(parsed, dict) else None
    if not isinstance(groups, list):
        raise ValueError("the model did not return groups")
    allowed = {name.casefold(): name for name in declared_areas}
    kept = []
    for group in groups:
        if not isinstance(group, dict):
            continue
        area = group.get("life_area")
        file_ids = group.get("file_ids")
        if not isinstance(file_ids, list):
            continue
        if area != "needs_review":
            canonical = allowed.get(str(area).casefold())
            if canonical is None:
                area = "needs_review"
            else:
                area = canonical
        kept.append({
            "life_area": area,
            "file_ids": [str(item) for item in file_ids],
            "reason": str(group.get("reason") or ""),
        })
    return {"groups": kept}


def resolve_conflict(*, file_id: str, dossier: dict, candidates: list[str],
                     provider, model_id: str, declared_areas: set[str],
                     consent: bool, sleep=time.sleep,
                     attempts: int = 4):
    """REASONING. Two candidate areas, one dossier, the same answer schema.

    The result still passes the category gate. A candidate that was not
    declared cannot win.
    """
    if not consent:
        raise ConsentRequired(STATEMENT)
    if len(candidates) < 2:
        raise ValueError("a conflict needs two candidates")
    prompt = (
        "Reply with one JSON object and nothing else. This is a conflict: "
        f"the candidates are {json.dumps(candidates)}. "
        "Pick kind, life_area, course, term, company, project, concerns, "
        "confidence, evidence_quote. "
        f"life_area must be one of {', '.join(sorted(declared_areas)) or '(none)'}, "
        "or \"needs_review\". Do not invent a category. "
        "Business is not a fallback. "
        "Dossier: " + json.dumps(dossier, sort_keys=True)
    )
    reading = _finish(provider, CompletionRequest(
        model_id=model_id, prompt=prompt, max_tokens=1024, thinking="disabled"),
        sleep=sleep, attempts=attempts)
    return interpret_answer(
        reading.content, file_id=file_id, declared_areas=declared_areas)
