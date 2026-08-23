# src/facts/domains.py
"""§3.11 domain activation, and several domains on one file at once.

§3.11, verbatim: *"The product should have a small shared set of universal file facts
... It should then activate domain-specific schemas only when the evidence indicates
that a domain is plausible ... This means target university is not a fact that every
file is expected to have. It is a field available only when the Applications domain is
plausibly active."*

And the worked case this module exists to preserve, also verbatim: *"One file may hold
facts from more than one domain without losing information. An academic abstract
submitted as part of a university application can retain project = PVA/RDP and
document type = abstract while also carrying purpose = university application and
target university = UChicago. At the pre-sorting stage, the product does not need to
decide which of those perspectives will ultimately determine its physical location. It
preserves both so the user can later choose the appropriate organization structure."*

Two things follow and both are structural:

* **Activation adds; it never chooses.** `active_domains` returns a set, not a winner.
  No domain suppresses another, no field is dropped, and nothing here ranks.
* **P6 authors no activation signal.** *"Domain activation signals | §3.11 ("when the
  evidence indicates that a domain is plausible"), §5.7 ("detection signals") | Which
  evidence activates which domain is unauthored."* The signals arrive as an injected
  `ActivationSignals` with no default; an empty one activates nothing, which is the
  honest behaviour of an unauthored rule.

**Schemas are named, fields are not implied.** `SCHEMA_IDS` is the ten domains the
product recognises -- §3.11's six with field rows plus §3.15's remaining safety
domains. Four of the ten have **no field rows at all** (D1, narrowed): activating one
contributes nothing to the allowlist, which is exactly right, because a schema with no
authored fields must not cause fields to be invented. `FIELD_LESS_SCHEMA_IDS` is
derived from `facts.fields.FIELD_SCOPES` rather than written down, so the two
vocabularies cannot drift apart.

**This module reads `planning/domains/` never.** That directory is a research artifact
of 574 proposed entries with its own gate; the catalogue this activates is
`facts.fields`, and Task 25 asserts the import does not exist.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable
from dataclasses import dataclass

from facts.fields import DOMAIN_FIELDS, FIELD_SCOPES, fields_in_scope
from facts.file_facts import facts_for_file

#: §3.11's six domains with field rows, plus §3.15's four safety domains. Named here
#: because a schema id is a closed vocabulary the product recognises; what activates
#: one, and which fields one carries, are elsewhere.
SCHEMA_IDS: tuple[str, ...] = (
    "academic", "college_applications", "research", "career", "photos", "code",
    "finance", "identity", "medical", "legal")

#: `FIELD_SCOPES[0]` is the universal scope. §3.11: the universal set "applies to
#: every file", so it is in every allowlist and is never activated.
UNIVERSAL_SCOPE: str = FIELD_SCOPES[0]

#: Derived, not authored: the schemas the product recognises that carry no field rows.
#: D1 (narrowed): "Do not author career fields ... Career is owed before P10." The
#: same holds for identity, medical and legal, which §3.15 names as safety domains and
#: §3.11 gives no field row.
FIELD_LESS_SCHEMA_IDS: tuple[str, ...] = tuple(
    schema_id for schema_id in SCHEMA_IDS if schema_id not in FIELD_SCOPES)


class UnknownSchema(KeyError):
    """A signal naming a domain the product does not recognise."""


@dataclass(frozen=True, slots=True)
class ActivationSignal:
    """One injected rule: this schema is plausible when this predicate says so.

    The predicate receives the file version's existing facts -- §3.11's "when the
    evidence indicates that a domain is plausible", read as P6's own evidence-derived
    claims, which is also what makes §8.6's degradation order work: direct and
    rule-validated facts are produced first, and the allowlist they activate is what
    bounds the model afterwards.
    """

    schema_id: str
    activates: Callable[[tuple[sqlite3.Row, ...]], bool]

    def __post_init__(self) -> None:
        if self.schema_id not in SCHEMA_IDS:
            raise UnknownSchema(
                f"{self.schema_id!r} is not one of the ten recognised schemas")
        if not callable(self.activates):
            raise TypeError("an activation signal is a predicate over the file's facts")


@dataclass(frozen=True, slots=True)
class ActivationSignals:
    """The injected signal set. No default: P6 authors none of these."""

    signals: tuple[ActivationSignal, ...]

    def __post_init__(self) -> None:
        ids = [signal.schema_id for signal in self.signals]
        if len(set(ids)) != len(ids):
            raise ValueError(f"one signal per schema; duplicates: {sorted(ids)}")


def active_domains(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                   activation_signals: ActivationSignals) -> frozenset[str]:
    """Which domain schemas this file version's own evidence makes plausible.

    A set, deliberately: §3.11 preserves every perspective and "does not need to
    decide which of those perspectives will ultimately determine its physical
    location". Nothing here breaks a tie because nothing here has one to break.
    """
    established = tuple(facts_for_file(conn, file_id, content_hash))
    return frozenset(signal.schema_id for signal in activation_signals.signals
                     if signal.activates(established))


def active_field_allowlist(conn: sqlite3.Connection, *, file_id: str,
                           content_hash: str,
                           activation_signals: ActivationSignals) -> tuple[str, ...]:
    """The universal fields plus every active schema's fields, deduplicated.

    This is the object §3.5's sentence turns on -- the model "can only propose facts
    that belong to the active domain schema" -- and Task 17 hands this exact tuple to
    P8, so the allowlist is one computation and not two.

    Order is deterministic and is the catalogue's: universal first, then each active
    schema in `SCHEMA_IDS` order. `project` and `artifact_type` belong to both Research
    and Code, so a file with both active must list each once and lose neither.
    """
    active = active_domains(conn, file_id=file_id, content_hash=content_hash,
                            activation_signals=activation_signals)
    allowed: list[str] = []
    for scope in (UNIVERSAL_SCOPE,
                  *(schema_id for schema_id in SCHEMA_IDS if schema_id in active)):
        if scope not in FIELD_SCOPES:
            # A recognised schema with no field rows (D1). It activates and
            # contributes nothing; it does not cause a field to be invented.
            continue
        for row in fields_in_scope(conn, scope):
            if row["field_key"] not in allowed:
                allowed.append(row["field_key"])
    return tuple(allowed)


def schema_fields(schema_id: str) -> tuple[str, ...]:
    """The authored field keys of one schema, empty for the four field-less ones."""
    if schema_id not in SCHEMA_IDS:
        raise UnknownSchema(schema_id)
    return tuple(DOMAIN_FIELDS.get(schema_id, ()))
