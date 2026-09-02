# tests/integration/egress_fixtures/egress_by_subprocess.py
"""Rule C's oldest omission: the way out that is not a network library at all.

`subprocess` was not on the list because the list was written as "what a provider
imports, plus the two raw HTTP libraries a fourth would reach for" -- a list about
SDKs. Handing the bytes to `curl` is not a future-SDK gap; it predates every name
on that list.
"""
from __future__ import annotations

import subprocess


def ask(sentence: str) -> None:
    subprocess.run(["curl", "-d", sentence, "https://example.invalid/v1"])
