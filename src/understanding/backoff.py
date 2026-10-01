# src/understanding/backoff.py
"""Slow down when the provider says so. No socket, no key.

A 429 is not an answer and not a classification. The caller waits and
tries again, a small number of times. The wait is injected so a test does
not sleep.
"""
from __future__ import annotations

from understanding.provider import CompletionRequest


class RateLimited(RuntimeError):
    """The provider asked the caller to wait. The message has no key in it."""

    def __init__(self, retry_after: float = 1.0):
        super().__init__("the provider asked to slow down")
        self.retry_after = retry_after


def wait_seconds(retry_after: float, delay: float) -> float:
    """Honor a positive Retry-After. Otherwise use the growing delay.

    Capped so a header cannot stall a run. The value is never taken from
    the response body.
    """
    try:
        asked = float(retry_after)
    except (TypeError, ValueError):
        asked = 0.0
    if asked > 0:
        return min(asked, 60.0)
    return min(max(float(delay), 0.0), 60.0)


def complete_with_backoff(provider, request: CompletionRequest, *, sleep,
                          attempts: int = 4):
    """Call `complete`. On RateLimited, wait and try again.

    `attempts` counts tries, not extra retries. The last RateLimited is
    raised. Any other error is raised immediately.
    """
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    delay = 1.0
    last: RateLimited | None = None
    for _ in range(attempts):
        try:
            return provider.complete(request)
        except RateLimited as problem:
            last = problem
            sleep(wait_seconds(problem.retry_after, delay))
            delay = min(delay * 2, 32.0)
    assert last is not None
    raise last
