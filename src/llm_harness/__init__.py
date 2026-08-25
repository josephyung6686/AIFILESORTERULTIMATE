# src/llm_harness/__init__.py
"""P8 — bounded LLM harness and validator.

Public surface is `run_call` plus the frozen records and P7's exact `NeedsConsent`.
Internal modules import `P8Verdict` explicitly; this package exports no bare `Verdict`.
"""
from privacy.release import NeedsConsent

from llm_harness.harness import run_call
from llm_harness.records import Dossier, P8Verdict, Refusal, ValidationUnavailable

__all__ = [
    "run_call",
    "Dossier",
    "P8Verdict",
    "Refusal",
    "ValidationUnavailable",
    "NeedsConsent",
]
