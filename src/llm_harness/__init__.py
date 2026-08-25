# src/llm_harness/__init__.py
"""P8 — bounded LLM harness and validator.

Task 1 public surface is the frozen records plus P7's exact `NeedsConsent`.
`run_call` is Task 9 and is not exported here. Internal modules import `P8Verdict`
explicitly; this package exports no bare `Verdict`.
"""
from privacy.release import NeedsConsent

from llm_harness.records import Dossier, P8Verdict, Refusal, ValidationUnavailable

__all__ = [
    "Dossier",
    "P8Verdict",
    "Refusal",
    "ValidationUnavailable",
    "NeedsConsent",
]
