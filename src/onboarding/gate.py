# src/onboarding/gate.py
"""A scan of a person's folder waits for a completed profile.

The test suite sets FILESORTER_ONBOARDING_OPTIONAL=1. A person's own run
does not. Without that variable, a folder with no completed record and no
valid --answers file is not scanned.
"""
from __future__ import annotations

import os
from pathlib import Path

from onboarding.answers import (
    AnswersNotReady, apply_answers, load_answers, stored_answers,
)

OPTIONAL_ENV = "FILESORTER_ONBOARDING_OPTIONAL"

REFUSAL = (
    "This folder has no completed onboarding. A scan needs --answers "
    "FILE with confirmed set to true and every TODO filled in, or a "
    "profile already stored for this folder. Nothing was scanned. "
    "Run `filesorter onboard --folder FOLDER --database DATABASE` "
    "to answer the questions in the terminal."
)


def onboarding_optional() -> bool:
    return os.environ.get(OPTIONAL_ENV) == "1"


def allow_scan(conn, *, corpus_root: str, answers: Path | None,
               user_id: str, recorded_at: str) -> str | None:
    """None means the scan may proceed. A string is the refusal to print.

    The caller has already bootstrapped the database. This does not walk
    the folder.
    """
    if answers is not None:
        try:
            data = load_answers(answers)
        except AnswersNotReady as problem:
            return str(problem) + " Nothing was scanned."
        apply_answers(
            conn, data, user_id=user_id, recorded_at=recorded_at,
            corpus_root=corpus_root)
        return None
    if onboarding_optional():
        return None
    if stored_answers(conn, corpus_root) is not None:
        return None
    return REFUSAL
