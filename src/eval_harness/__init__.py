# src/eval_harness/__init__.py
"""P2 — evaluation and replay harness (§8.5).

P2 asserts on outcomes. It does not repair them, does not re-rank, and does not
feed its verdicts back into any live decision path.
"""
from eval_harness.driver import EvaluationRun, evaluate_bundle
from eval_harness.store import EVAL_SCHEMA_VERSION, create_eval_schema

__all__ = ["create_eval_schema", "EVAL_SCHEMA_VERSION", "evaluate_bundle",
           "EvaluationRun"]
