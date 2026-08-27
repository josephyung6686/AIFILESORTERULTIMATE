"""Production-only composition of the implemented P1 through P7 authorities.

This module chooses plumbing and lifecycle only. Domain producers, thresholds,
classification, readers, policies, clocks, and payload storage remain mandatory
injected authorities. P8 is deliberately absent; whether an LLM stage exists is a
decision already frozen inside each supplied P6 resolver.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from database_agent.db import create_schema
from eval_harness.store import create_eval_schema
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import RunWriter
from extractors.authorship import SUBSYSTEM as P5_SUBSYSTEM
from extractors.dispatch import Readers
from extractors.safety import SafetyPolicy
from extractors.schema import create_extraction_schema
from facts.fields import create_fields
from facts.resolver import FactResolver
from facts.usable import targeted_ocr_needed_for
from orchestrator import ClassificationProducer, P1P7Run, run_p1_p7
from privacy.classification_store import ClassificationStore
from privacy.schema import create_privacy_schema
from scan_agent.corpus_source import CorpusSource
from scan_agent.schema import create_scan_schema


class InvalidP1P7Authority(ValueError):
    """A required production authority is absent or has the wrong public type."""


class MissingClassificationAuthority(InvalidP1P7Authority):
    """P7 has no detector default; production cannot classify without one."""


@dataclass(frozen=True)
class P1P7Authorities:
    """Every policy-bearing dependency required by the live P1--P7 path."""

    native_resolver: FactResolver
    ocr_resolver: FactResolver
    usable_threshold: Callable[[Any, Any], bool]
    classify: ClassificationProducer
    source: CorpusSource
    mime_type_for: Callable[[Path], str | None]
    scan_state: str
    scan_budget_exhausted: Callable[[], bool]
    detect_format: Callable[[Path], str | None]
    policy: SafetyPolicy
    readers: Readers
    now: Callable[[], str]
    context_window: int
    transcription_authorized: Callable[[], bool]
    corpus_form: str
    policy_settings: Mapping[str, Any]
    file_entry_body: Callable[[Mapping[str, Any]], Mapping[str, str]]
    p7_component_version: str
    #: §8.5's hand-labelled expected side, carried to `_assemble_bundle` and applied
    #: before the seal. Empty by default: an unlabelled scan captures a bundle with
    #: no expectations, which is a corpus snapshot rather than a reference corpus.
    #: P2 SPEC's Deferred table: "P2 publishes `bundle_expectation`; it does not
    #: fill it" -- and neither does this module.
    bundle_expectations: Sequence[Mapping[str, Any]] = ()

    def __post_init__(self) -> None:
        if self.classify is None:
            raise MissingClassificationAuthority(
                "P7 classification requires an explicit producer; no detector or "
                "domain default exists")
        if not isinstance(self.native_resolver, FactResolver):
            raise InvalidP1P7Authority(
                "native_resolver must be a real FactResolver")
        if not isinstance(self.ocr_resolver, FactResolver):
            raise InvalidP1P7Authority("ocr_resolver must be a real FactResolver")
        required_callables = {
            "usable_threshold": self.usable_threshold,
            "classify": self.classify,
            "mime_type_for": self.mime_type_for,
            "scan_budget_exhausted": self.scan_budget_exhausted,
            "detect_format": self.detect_format,
            "now": self.now,
            "transcription_authorized": self.transcription_authorized,
            "file_entry_body": self.file_entry_body,
        }
        for name, authority in required_callables.items():
            if not callable(authority):
                raise InvalidP1P7Authority(
                    f"{name} must be an explicit callable authority")
        for name in ("source", "policy", "readers", "policy_settings"):
            if getattr(self, name) is None:
                raise InvalidP1P7Authority(f"{name} is required")
        for name in ("scan_state", "corpus_form", "p7_component_version"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise InvalidP1P7Authority(f"{name} must be a non-empty string")
        if not isinstance(self.context_window, int) or self.context_window <= 0:
            raise InvalidP1P7Authority("context_window must be a positive integer")


def bootstrap_p1_p7(conn: sqlite3.Connection) -> None:
    """Create implemented schemas in dependency order: P1, P3, P4, P5, P6, P7, P2."""
    create_schema(conn)
    create_scan_schema(conn)
    create_evidence_schema(conn)
    create_extraction_schema(conn)
    # `create_fields` creates P6's schema and installs its closed, source-owned
    # catalogue. It reads no unfinished domain or prompt directory.
    create_fields(conn)
    create_privacy_schema(conn)
    create_eval_schema(conn)


def compose_p1_p7(
        conn: sqlite3.Connection, *, authorities: P1P7Authorities
) -> Callable[[str], P1P7Run]:
    """Bind concrete storage adapters while preserving all injected authorities."""
    # Revalidate here so bypassing dataclass construction cannot let a scan start.
    authorities.__post_init__()
    sink = RunWriter(conn, author=P5_SUBSYSTEM)
    classification_store = ClassificationStore(conn)
    targeted_ocr_needed = targeted_ocr_needed_for(
        conn, usable_threshold=authorities.usable_threshold)

    def resolve(resolver: FactResolver):
        return lambda db, file_id, content_hash: resolver.resolve(
            db, file_id=file_id, content_hash=content_hash)

    def run(selection_id: str) -> P1P7Run:
        return run_p1_p7(
            conn, selection_id, source=authorities.source,
            mime_type_for=authorities.mime_type_for,
            scan_state=authorities.scan_state,
            budget_exhausted=authorities.scan_budget_exhausted,
            detect_format=authorities.detect_format, policy=authorities.policy,
            readers=authorities.readers, sink=sink, now=authorities.now,
            context_window=authorities.context_window,
            transcription_authorized=authorities.transcription_authorized,
            corpus_form=authorities.corpus_form,
            policy_settings=authorities.policy_settings,
            file_entry_body=authorities.file_entry_body,
            resolve_native=resolve(authorities.native_resolver),
            targeted_ocr_needed=targeted_ocr_needed,
            resolve_with_ocr=resolve(authorities.ocr_resolver),
            classify=authorities.classify,
            classification_store=classification_store,
            p7_component_version=authorities.p7_component_version,
            bundle_expectations=authorities.bundle_expectations)

    return run


def run_production_p1_p7(
        conn: sqlite3.Connection, selection_id: str, *,
        authorities: P1P7Authorities) -> P1P7Run:
    """Compose and execute one production P1--P7 run."""
    return compose_p1_p7(conn, authorities=authorities)(selection_id)
