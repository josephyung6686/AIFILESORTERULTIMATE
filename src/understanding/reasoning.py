# src/understanding/reasoning.py
"""Read a chat completion. `reasoning_content` is never the answer.

A small `max_tokens` on a reasoning model comes back with empty `content`,
a `reasoning_content` field, and `finish_reason` `length`, because thinking
spent the budget. That is a retry with a larger budget, not a classification.
"""
from __future__ import annotations

from dataclasses import dataclass


class CompletionUnreadable(ValueError):
    """The payload is not a completion this pass can read."""


@dataclass(frozen=True, slots=True)
class Reading:
    content: str
    retry: bool
    reason: str
    prompt_tokens: int | None
    completion_tokens: int | None


def read_completion(payload: dict) -> Reading:
    if not isinstance(payload, dict):
        raise CompletionUnreadable("the completion was not an object")
    choices = payload.get("choices")
    if not isinstance(choices, list) or len(choices) != 1:
        raise CompletionUnreadable("the completion did not contain one choice")
    choice = choices[0]
    if not isinstance(choice, dict):
        raise CompletionUnreadable("the choice was not an object")
    message = choice.get("message") or {}
    if not isinstance(message, dict):
        raise CompletionUnreadable("the message was not an object")
    content = message.get("content") or ""
    if not isinstance(content, str):
        content = ""
    reason = choice.get("finish_reason")
    usage = payload.get("usage") if isinstance(payload.get("usage"), dict) else {}
    prompt_tokens = usage.get("prompt_tokens")
    completion_tokens = usage.get("completion_tokens")
    if not isinstance(prompt_tokens, int):
        prompt_tokens = None
    if not isinstance(completion_tokens, int):
        completion_tokens = None
    if not content.strip():
        # Empty content is never answered from reasoning_content.
        if reason == "length" or message.get("reasoning_content"):
            return Reading(
                content="", retry=True,
                reason=("empty content with finish_reason length; "
                        "the thinking budget was spent and this is not an answer"),
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens)
        raise CompletionUnreadable("the completion had no content")
    if reason == "length":
        return Reading(
            content="", retry=True,
            reason="finish_reason length; the answer was cut off and is not used",
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens)
    return Reading(
        content=content, retry=False, reason="",
        prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)
