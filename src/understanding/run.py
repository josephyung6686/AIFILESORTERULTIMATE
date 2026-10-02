# src/understanding/run.py
"""Ask the FAST model about files the deterministic tier did not settle.

Nothing here opens a socket. `complete` is injected. Offline mode and a
missing consent return a report and do not call `complete`. A protected
file, a held file, and a private area never become a call.

A cache hit does not call `complete`. A hard budget stops the rest of the
run and marks those files needs-review. Empty content with finish_reason
length is retried once at four times the token budget, then needs-review.
"""
from __future__ import annotations

import json
import threading
from dataclasses import dataclass, field

from concurrent.futures import ThreadPoolExecutor

from understanding.answer import AnswerRejected, interpret_answer
from understanding.backoff import (
    BALANCE_EMPTY, InsufficientBalance, RateLimited, complete_with_backoff,
)
from understanding.dossier import (
    FIELDS_THAT_LEAVE,
    FileView,
    NotSendable,
    build_dossier,
    dossier_hash,
    estimate_input_tokens,
)
from understanding.provider import CompletionRequest
from understanding.reasoning import CompletionUnreadable, read_completion
from understanding.store import STATEMENT, audit, cache_get, cache_put

CLASSIFICATION_MAX_TOKENS: int = 512
BATCH_LIMIT: int = 8
OUTPUT_TOKENS_PER_FILE: int = CLASSIFICATION_MAX_TOKENS

# A Downloads copy is about 1800 files. A long excerpt is its own call,
# because the batch cap is 800 estimated tokens, so 200 calls stops that
# pass in the middle. These ceilings cover that folder with each file its
# own call, and a second send of the same dossier still fits.
DEFAULT_MAX_CALLS: int = 4000
DEFAULT_MAX_INPUT_TOKENS: int = 4_000_000

# chars/4 for the dossier JSON. The excerpt is already capped at 400 words
# inside the dossier, so this bound cannot grow with the file.
TOKEN_CHARS: int = 4


class ConsentRequired(RuntimeError):
    """Cloud understanding was asked for and the person has not accepted it."""


class OfflineRefused(RuntimeError):
    """offline mode sends nothing. The pass did not call the provider."""


@dataclass
class Budget:
    """How many understanding calls this pass may still make.

    ``max_calls`` counts calls, not files. A cache hit does not spend one.
    ``max_input_tokens`` is ``len(dossier_json) / 4`` summed across calls,
    the same estimate the dry-run prints. Either ceiling stops the rest of
    the pass. The defaults cover about 1800 files when each file is its own
    call. Pass a lower pair to stop a short demo early.
    """

    max_calls: int = DEFAULT_MAX_CALLS
    max_input_tokens: int = DEFAULT_MAX_INPUT_TOKENS
    calls: int = 0
    input_tokens: int = 0

    def __post_init__(self) -> None:
        if (self.max_calls < 0 or self.max_input_tokens < 0
                or self.calls < 0 or self.input_tokens < 0):
            raise ValueError("an understanding budget cannot be negative")

    def room_for(self, tokens: int) -> bool:
        return (self.calls + 1 <= self.max_calls
                and self.input_tokens + tokens <= self.max_input_tokens)

    def spend(self, tokens: int) -> None:
        self.calls += 1
        self.input_tokens += tokens


@dataclass
class FileResult:
    file_id: str
    status: str
    reason: str = ""
    understanding: object | None = None


@dataclass
class PassReport:
    sent: int = 0
    cache_hits: int = 0
    excluded: int = 0
    needs_review: int = 0
    budget_stopped: int = 0
    results: list[FileResult] = field(default_factory=list)
    fields: tuple[str, ...] = FIELDS_THAT_LEAVE
    called_complete: int = 0
    balance_notice: str = ""


def cost_formula() -> str:
    return (
        "cost = input_tokens * input_usd_per_million / 1000000 "
        "+ output_tokens * output_usd_per_million / 1000000. "
        "input_tokens is estimated as len(dossier_json) / 4. "
        "output_tokens is estimated as files * 512. "
        "No price is filled in here."
    )


def dry_run_estimate(dossiers: list[dict]) -> dict:
    input_tokens = sum(estimate_input_tokens(item) for item in dossiers)
    output_tokens = len(dossiers) * OUTPUT_TOKENS_PER_FILE
    return {
        "files": len(dossiers),
        "estimated_input_tokens": input_tokens,
        "estimated_output_tokens": output_tokens,
        "fields": list(FIELDS_THAT_LEAVE),
        "formula": cost_formula(),
        "sent": False,
    }


# Chat completions on these ids accept json_object only. json_schema is
# rejected by that endpoint, so the shape is spelled here and checked here.
_CONCERNS_RULE = (
    '"concerns" is one string, exactly "user" or "someone_else" or '
    '"unknown". It is not an array.'
)


def _prompt(dossier: dict, declared: list[str], profile_note: str = "") -> str:
    areas = ", ".join(sorted(declared)) or "(none declared)"
    note = f" Profile: {profile_note}" if profile_note else ""
    return (
        "Reply with one JSON object and nothing else. "
        f"life_area must be one of: {areas}, or \"needs_review\". "
        "Do not invent a category. Business is not a fallback. "
        "Keys: kind (string), life_area (string), course, term, company, "
        "project (each a string or null), "
        + _CONCERNS_RULE + " "
        "confidence is a number from 0 to 1, not a percent sign and not an "
        "array. evidence_quote is one string and one line. "
        "Dossier: " + json.dumps(dossier, sort_keys=True)
        + note
    )


def _complete_once(provider, *, model_id: str, prompt: str, max_tokens: int,
                   sleep, attempts: int) -> dict:
    return complete_with_backoff(
        provider,
        CompletionRequest(
            model_id=model_id, prompt=prompt, max_tokens=max_tokens,
            thinking="disabled"),
        sleep=sleep, attempts=attempts)


def batch_dossiers(items: list[dict], *, limit: int = BATCH_LIMIT,
                   token_cap: int = 800) -> list[list[dict]]:
    """Group small dossiers. A large one stays in a batch of one."""
    groups: list[list[dict]] = []
    current: list[dict] = []
    current_tokens = 0
    for dossier in items:
        tokens = estimate_input_tokens(dossier)
        if tokens > token_cap:
            if current:
                groups.append(current)
                current = []
                current_tokens = 0
            groups.append([dossier])
            continue
        if current and (len(current) >= limit or current_tokens + tokens > token_cap):
            groups.append(current)
            current = []
            current_tokens = 0
        current.append(dossier)
        current_tokens += tokens
    if current:
        groups.append(current)
    return groups


def ask_one(provider, *, model_id: str, dossier: dict, declared: set[str],
            sleep, max_tokens: int = CLASSIFICATION_MAX_TOKENS, attempts: int = 4,
            profile_note: str = ""):
    """One file. Retries once when the reasoning budget ate the content."""
    prompt = _prompt(dossier, sorted(declared), profile_note)
    payload = _complete_once(
        provider, model_id=model_id, prompt=prompt, max_tokens=max_tokens,
        sleep=sleep, attempts=attempts)
    reading = read_completion(payload)
    calls = 1
    if reading.retry:
        payload = _complete_once(
            provider, model_id=model_id, prompt=prompt,
            max_tokens=max_tokens * 4, sleep=sleep, attempts=attempts)
        reading = read_completion(payload)
        calls = 2
        if reading.retry:
            raise AnswerRejected(reading.reason)
    understood = interpret_answer(
        reading.content, file_id=dossier["file_id"], declared_areas=declared)
    return understood, calls, reading, reading.content


def run_understanding(*, conn, views: list[FileView], declared_areas: set[str],
                      private_areas: set[str], provider, model_id: str,
                      offline: bool, consent: bool, budget: Budget | None = None,
                      now: str = "", dry_run: bool = False, sleep=None,
                      workers: int = 4, attempts: int = 4,
                      profile_note: str = "") -> PassReport:
    if sleep is None:
        import time
        sleep = time.sleep
    if workers < 1:
        raise ValueError("workers must be at least 1")
    budget = budget or Budget()
    report = PassReport()
    if dry_run or offline or not consent:
        # Count what would be eligible. Do not call the provider.
        for view in views:
            try:
                build_dossier(view, private_areas=private_areas)
            except NotSendable:
                report.excluded += 1
                report.results.append(FileResult(view.file_id, "excluded"))
            else:
                report.results.append(FileResult(
                    view.file_id, "would_send" if dry_run or not offline else "not_sent",
                    reason=("dry-run" if dry_run else
                            "offline" if offline else "consent required")))
        if not dry_run and offline:
            report.results = [
                FileResult(item.file_id, "not_sent", reason="offline")
                if item.status != "excluded" else item
                for item in report.results]
        if not dry_run and not offline and not consent:
            raise ConsentRequired(STATEMENT)
        return report

    if provider.locality() == "cloud" and offline:
        raise OfflineRefused("offline")

    waiting: list[tuple[FileView, dict, str, int]] = []
    for view in views:
        try:
            dossier = build_dossier(view, private_areas=private_areas)
        except NotSendable as refusal:
            report.excluded += 1
            report.results.append(FileResult(view.file_id, "excluded", str(refusal)))
            continue
        key = dossier_hash(dossier, model_id=model_id, profile_note=profile_note)
        cached = cache_get(conn, key)
        if cached is not None:
            report.cache_hits += 1
            # This read is on the calling thread, before any worker starts.
            # One stored row that the interpreter did not expect must not
            # abandon the files that follow it.
            exception_class = None
            try:
                understood = interpret_answer(
                    cached, file_id=view.file_id, declared_areas=declared_areas)
            except AnswerRejected as refusal:
                report.needs_review += 1
                report.results.append(FileResult(
                    view.file_id, "needs_review", str(refusal)))
                exception_class = "AnswerRejected"
            except Exception as problem:  # noqa: BLE001 -- one cached row, not the pass
                reason, exception_class = _fault_from(problem)
                report.needs_review += 1
                report.results.append(FileResult(
                    view.file_id, "needs_review", reason=reason))
            else:
                if understood.needs_review:
                    report.needs_review += 1
                report.results.append(FileResult(
                    view.file_id, "cache", understanding=understood))
            audit(conn, file_id=view.file_id, fields=FIELDS_THAT_LEAVE,
                  model_id=model_id, prompt_tokens=None, completion_tokens=None,
                  cache_hit=True, recorded_at=now, exception_class=exception_class)
            continue
        tokens = estimate_input_tokens(dossier)
        waiting.append((view, dossier, key, tokens))

    admitted: list[tuple[list, int]] = []
    for group in batch_dossiers([item[1] for item in waiting]):
        members = waiting[:len(group)]
        waiting = waiting[len(group):]
        tokens = sum(item[3] for item in members)
        if not budget.room_for(tokens):
            for view, _dossier, _key, _tokens in members:
                report.budget_stopped += 1
                report.needs_review += 1
                report.results.append(FileResult(
                    view.file_id, "needs_review", reason="budget stop"))
            continue
        # Reserve this call before the next group is considered, so a pool
        # cannot launch more than the budget allowed.
        budget.spend(tokens)
        admitted.append((members, tokens))

    halted = threading.Event()

    def invoke(item):
        members, tokens = item
        if halted.is_set():
            return {
                "members": members, "tokens": tokens, "calls": 0,
                "error": BALANCE_EMPTY, "exception_class": "InsufficientBalance",
                "reading": None, "items": None, "unsent": True,
            }
        outcome = _invoke_members(
            provider, model_id=model_id, members=members,
            declared=declared_areas, tokens=tokens, sleep=sleep,
            attempts=attempts, profile_note=profile_note)
        if outcome.get("exception_class") == "InsufficientBalance":
            halted.set()
        return outcome

    if len(admitted) <= 1 or workers == 1:
        outcomes = [invoke(item) for item in admitted]
    else:
        with ThreadPoolExecutor(max_workers=min(workers, len(admitted))) as pool:
            outcomes = list(pool.map(invoke, admitted))
    for outcome in outcomes:
        _persist(conn, report, budget, outcome, model_id=model_id, now=now)
    return report


class UnexpectedFault(Exception):
    """A worker failure that is not the model's answer. The message is the class name."""

    def __init__(self, class_name: str):
        super().__init__(class_name)
        self.exception_class = class_name


def _fault_from(problem: BaseException) -> tuple[str, str]:
    """A reason safe to store, and the exception class. No payload, no key."""
    klass = type(problem).__name__
    if isinstance(problem, json.JSONDecodeError):
        return "the model did not return JSON", "JSONDecodeError"
    if isinstance(problem, InsufficientBalance):
        return BALANCE_EMPTY, klass
    if isinstance(problem, (AnswerRejected, CompletionUnreadable, RateLimited)):
        return str(problem), klass
    return klass, klass


def _invoke_members(provider, *, model_id, members, declared, tokens, sleep,
                    attempts: int, profile_note: str = ""):
    """The HTTP part. No database. One bad answer does not escape this function."""
    try:
        return _ask_members(
            provider, model_id=model_id, members=members, declared=declared,
            tokens=tokens, sleep=sleep, attempts=attempts,
            profile_note=profile_note)
    except Exception as problem:  # noqa: BLE001 -- a worker must not kill the pool
        reason, klass = _fault_from(problem)
        return {
            "members": members, "tokens": tokens, "calls": 1,
            "error": reason, "exception_class": klass,
            "reading": None, "items": None,
        }


def _ask_members(provider, *, model_id, members, declared, tokens, sleep,
                 attempts: int, profile_note: str = ""):
    if len(members) == 1:
        view, dossier, key, _tokens = members[0]
        try:
            understood, calls, reading, raw = ask_one(
                provider, model_id=model_id, dossier=dossier, declared=declared,
                sleep=sleep, attempts=attempts, profile_note=profile_note)
        except (AnswerRejected, CompletionUnreadable, RateLimited) as refusal:
            reason, klass = _fault_from(refusal)
            return {
                "members": members, "tokens": tokens, "calls": 1,
                "error": reason, "exception_class": klass,
                "reading": None, "items": None,
            }
        return {
            "members": members, "tokens": tokens, "calls": calls, "error": None,
            "reading": reading,
            "items": [(view, key, raw, understood)],
        }
    prompt = _batch_prompt(members, declared, profile_note)
    try:
        payload = _complete_once(
            provider, model_id=model_id, prompt=prompt,
            max_tokens=CLASSIFICATION_MAX_TOKENS * len(members),
            sleep=sleep, attempts=attempts)
        reading = read_completion(payload)
        calls = 1
        if reading.retry:
            payload = _complete_once(
                provider, model_id=model_id, prompt=prompt,
                max_tokens=CLASSIFICATION_MAX_TOKENS * len(members) * 4,
                sleep=sleep, attempts=attempts)
            reading = read_completion(payload)
            calls = 2
            if reading.retry:
                raise AnswerRejected(reading.reason)
        parsed = json.loads(reading.content)
        files = parsed.get("files") if isinstance(parsed, dict) else None
        if not isinstance(files, list) or len(files) != len(members):
            raise AnswerRejected("the batch did not return one object per file")
    except (AnswerRejected, CompletionUnreadable, RateLimited, json.JSONDecodeError) as refusal:
        reason, klass = _fault_from(refusal)
        return {
            "members": members, "tokens": tokens, "calls": 1,
            "error": reason, "exception_class": klass,
            "reading": None, "items": None,
        }
    items = []
    for (view, dossier, key, _tokens), item in zip(members, files):
        raw = ""
        try:
            raw = json.dumps(item)
            understood = interpret_answer(
                raw, file_id=view.file_id, declared_areas=declared)
        except AnswerRejected as refusal:
            items.append((view, key, raw, refusal))
        except Exception as problem:  # noqa: BLE001 -- one file, not the batch
            items.append((view, key, raw, UnexpectedFault(type(problem).__name__)))
        else:
            items.append((view, key, raw, understood))
    return {
        "members": members, "tokens": tokens, "calls": calls, "error": None,
        "reading": reading, "items": items,
    }


def _batch_prompt(members, declared, profile_note: str = "") -> str:
    payload_dossiers = [item[1] for item in members]
    note = f" Profile: {profile_note}" if profile_note else ""
    return (
        "Reply with one JSON object and nothing else, of the form "
        "{\"files\": [ one object per dossier, in order ]}. "
        "Each object has file_id, kind, life_area, course, term, company, "
        "project, concerns, confidence, evidence_quote. "
        + _CONCERNS_RULE + " "
        f"life_area must be one string, one of {', '.join(sorted(declared))}, "
        "or \"needs_review\". Do not invent a category. Business is not a fallback. "
        "Dossiers: " + json.dumps(payload_dossiers)
        + note
    )


def _persist(conn, report, budget, outcome, *, model_id, now) -> None:
    members = outcome["members"]
    # The reservation already counted one call and its input tokens. A retry
    # is one more call and the same dossier sent again.
    extra_calls = outcome["calls"] - 1
    for _ in range(extra_calls):
        budget.spend(outcome["tokens"])
    report.called_complete += outcome["calls"]
    if outcome["error"] is not None:
        if not outcome.get("unsent"):
            report.sent += len(members)
        klass = outcome.get("exception_class")
        if klass == "InsufficientBalance":
            report.balance_notice = BALANCE_EMPTY
        for view, _dossier, _key, _tokens in members:
            report.needs_review += 1
            report.results.append(FileResult(
                view.file_id, "needs_review", reason=outcome["error"]))
            audit(conn, file_id=view.file_id, fields=FIELDS_THAT_LEAVE,
                  model_id=model_id, prompt_tokens=None, completion_tokens=None,
                  cache_hit=False, recorded_at=now, exception_class=klass)
        return
    reading = outcome["reading"]
    report.sent += len(members)
    for view, key, raw, understood in outcome["items"]:
        if isinstance(understood, (AnswerRejected, UnexpectedFault)):
            report.needs_review += 1
            if isinstance(understood, UnexpectedFault):
                reason = understood.exception_class
                klass = understood.exception_class
            else:
                reason = str(understood)
                klass = "AnswerRejected"
            report.results.append(FileResult(
                view.file_id, "needs_review", reason=reason))
            audit(conn, file_id=view.file_id, fields=FIELDS_THAT_LEAVE,
                  model_id=model_id, prompt_tokens=reading.prompt_tokens,
                  completion_tokens=reading.completion_tokens,
                  cache_hit=False, recorded_at=now, exception_class=klass)
            continue
        cache_put(conn, cache_key=key, model_id=model_id,
                  response_json=raw, stored_at=now)
        if understood.needs_review:
            report.needs_review += 1
        report.results.append(FileResult(
            view.file_id, "answered", understanding=understood))
        audit(conn, file_id=view.file_id, fields=FIELDS_THAT_LEAVE,
              model_id=model_id, prompt_tokens=reading.prompt_tokens,
              completion_tokens=reading.completion_tokens,
              cache_hit=False, recorded_at=now)
