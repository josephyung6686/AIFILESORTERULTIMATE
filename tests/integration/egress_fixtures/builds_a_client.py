# tests/integration/egress_fixtures/builds_a_client.py
"""What a composition root does, which must NOT be a finding.

`readers/model_routing.py` in miniature: it assembles the capability and hands it
on. P7's own guard already ruled on this direction -- "a callable sink is not a
content parameter", because the caller hands over no bytes at all. A rule that
could not tell this from `egress_by_invoke.py` would forbid wiring the product up.
"""
from __future__ import annotations

from llm_harness.transport import ModelClient
from privacy.release import ModelTarget


def client_for(model_id: str, *, send) -> ModelClient:
    return ModelClient(
        model_target=ModelTarget(locality="cloud", model_id=model_id,
                                 provider="deepseek"),
        invoke=send)
