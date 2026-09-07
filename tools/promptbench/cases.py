# tools/promptbench/cases.py
"""The shape of one stress case, and the helpers that keep cases honest.

A case is a synthetic dossier plus an expectation. Nothing in a case is drawn
from the owner's corpus: every value is authored for the bakeoff, and the four
personas of `planning/68-PERSONA-RERUN.md` (Mara, Priya, Tom, the multi-life
person) plus `00`:239's adversarial list are where the cases come from.

Observation keys are minted with the product's own `observation_key`, so they
have P4's shape and are keyed on the wire exactly as a real dossier's would be
(`llm_harness.wire_handles.wire_ref`). A case whose keys were plain strings
would show the model something the product never sends.
"""
from __future__ import annotations

import hashlib
import sys
from dataclasses import dataclass, field
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from evidence_shape.observation import observation_key  # noqa: E402

#: The one thing every synthetic file version shares: a content hash of the
#: right shape. It is derived from the case's subject so two cases never collide.
def content_hash_for(subject_ref: str) -> str:
    return hashlib.sha256(f"promptbench:{subject_ref}".encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Evidence:
    """One observation the builder describes and (usually) P7 releases.

    `location` is `EvidenceItem.location` -- the zone for an excerpt at A, B, C
    and E, and the SUBJECT REF at D, where `placement_validation._same_file_evidence`
    requires every cited item to name the file being judged.
    """

    key: str
    address: str
    value: str
    zone: str
    location: str
    kind: str = "excerpt"
    span: tuple[int, int] | None = None
    reliability_state: str = "direct"
    basis: str = "direct-anchor"
    released: bool = True


@dataclass(frozen=True)
class Item:
    """A reference-only evidence item with no released text: a B member, a C or
    D candidate node. `evidence_ref` is a file id or node id and stays raw on
    the wire (`wire_ref` keys only observation keys)."""

    evidence_ref: str
    kind: str
    location: str
    reliability_state: str = "direct"
    basis: str = "direct-anchor"


@dataclass(frozen=True)
class Case:
    case_id: str
    site: str
    title: str
    persona: str
    traces: tuple[str, ...]
    subject_ref: str
    allowed_vocabulary: tuple[str, ...]
    evidence: tuple[Evidence, ...]
    expect: dict
    should_abstain: bool
    items: tuple[Item, ...] = ()
    conflicts: tuple[tuple[str, str], ...] = ()
    plan_version: str | None = None
    folder_levels: tuple[tuple[str, str, str], ...] = ()
    authorities: dict = field(default_factory=dict)
    #: Site A only: the schema the activation signal turns on, and the
    #: situation whose folder levels the dossier shows.
    schema_id: str | None = None
    situation: str | None = None
    notes: str = ""

    def released(self) -> tuple[Evidence, ...]:
        return tuple(item for item in self.evidence if item.released)


def evidence(*, subject_ref: str, address: str, value: str, zone: str = "body",
             location: str | None = None, extractor: str = "pdf.text",
             span: tuple[int, int] | None = None, kind: str = "excerpt",
             reliability_state: str = "direct", basis: str = "direct-anchor",
             released: bool = True) -> Evidence:
    """Mint one released observation for a case, keyed the way P4 keys it."""
    key = observation_key(
        content_hash=content_hash_for(subject_ref), extractor_name=extractor,
        locator=address, raw_value=value)
    return Evidence(
        key=key, address=address, value=value, zone=zone,
        location=location if location is not None else zone,
        kind=kind, span=span, reliability_state=reliability_state, basis=basis,
        released=released)


def check_cases(cases: tuple[Case, ...]) -> None:
    """The invariants every case file must hold before a model is paid to see it."""
    ids = [case.case_id for case in cases]
    if len(set(ids)) != len(ids):
        raise ValueError(f"duplicate case ids: {sorted(ids)}")
    for case in cases:
        if not case.released():
            raise ValueError(f"{case.case_id}: a dossier with nothing released "
                             "is refused by build_dossier; release something")
        keys = [item.key for item in case.evidence]
        if len(set(keys)) != len(keys):
            raise ValueError(f"{case.case_id}: two evidence items share a key")
        if not case.traces:
            raise ValueError(f"{case.case_id}: a case names the design line it "
                             "tests or it is not a stress case")


__all__ = ["Case", "Evidence", "Item", "check_cases", "content_hash_for",
           "evidence"]
