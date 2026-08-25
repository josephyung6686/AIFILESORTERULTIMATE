# src/llm_harness/fingerprint.py
"""Deterministic prompt fingerprint and dossier content address.

Callers inject prompt text, response schemas, and policy bytes on
`PromptDefinition`. This module hashes those injected sources; it does not
author them. Capability and provenance values (`release_id`, `audit_id`) and
the current evidence-snapshot identity are accepted only so they can be kept
off the digest used as the dossier content address.
"""
from __future__ import annotations

import hashlib
from collections.abc import Sequence

from evidence_shape.canonical import canonical_json
from llm_harness.records import PromptDefinition


def prompt_fingerprint(definition: PromptDefinition) -> str:
    """SHA-256 hex digest of the canonical prompt-definition sources.

    Byte fields are hex-encoded because `canonical_json` cannot encode raw
    `bytes`. Call-site is inside the fingerprint (B2); it is not a separate
    binding term.
    """
    payload = canonical_json({
        "call_site": definition.call_site,
        "call_site_version": definition.call_site_version,
        "response_schema_bytes": definition.response_schema_bytes.hex(),
        "shaping_policy_bytes": definition.shaping_policy_bytes.hex(),
        "template_bytes": definition.template_bytes.hex(),
        "template_id": definition.template_id,
    }).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def dossier_content_address(
    released_material: bytes,
    *,
    allowed_vocabulary: Sequence[str],
    allowed_schema_bytes: bytes,
    evidence_snapshot_id: str | None = None,
    release_id: str | None = None,
    audit_id: int | None = None,
) -> str:
    """SHA-256 hex digest of the canonical model-visible dossier payload.

    Hashed: released material plus allowed schema/vocabulary. Not hashed:
    `release_id`, `audit_id`, and `evidence_snapshot_id`. Snapshot identity is
    a separate argument for later revalidation; it is not part of the address.
    """
    del evidence_snapshot_id, release_id, audit_id
    payload = canonical_json({
        "allowed_schema_bytes": allowed_schema_bytes.hex(),
        "allowed_vocabulary": list(allowed_vocabulary),
        "released_material": released_material.hex(),
    }).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
