# src/facts/read_surface.py
"""P6's read surface -- the only shape P9, P10, P11, P13, P2 and the review UI see.

Three properties hold across every function here, and each of them is a test in
`tests/p6/test_p6_read_surface.py`:

* it is a pure read -- nothing here writes a row, appends an event or resolves a fact;
* it returns no filing decision -- §3.14: "A fact such as subject = BUSIB 4300 does not
  itself dictate one permanent folder path". Task 4 asserts that from `PRAGMA
  table_info`; this module is asserted from the KEYS OF EVERY ROW it hands out, so a
  future column named `destination_node_id` fails twice;
* it imposes its own total order -- P4's reads are insertion-ordered, which is a
  property of one database and not of the corpus, so every read here sorts before it
  returns.

`evidence_chain` is the one function that returns something other than P6's own rows: it
returns P4 `Observation` objects verbatim, because §3.2 requires the product to "preserve
both the original evidence and the conclusion built from it". `Observation.location`
carries a `container_path`, and that is NOT a violation of the negative contract -- it is
a locator INSIDE a document (`heading:page=1/heading=2`), never a filesystem destination.
The forbidden-key assertion therefore runs over the `sqlite3.Row` reads, which are P6's
own rows, and the evidence walk is asserted separately: it hands back P4's frozen shape
unaltered, which is the stronger claim.

**CUT 7 is unratified and this module is its target (preamble §2, D13).** The preamble
records that each cut-target task carries its callout; Task 24's section carries none, so
the callout is written here instead of being silently omitted. The evidence a reader
needs to decide the cut: `facts.session` and `facts.llm_seam` already have tests that
call `proposal_eligible`, and until this module existed those two tests were skipped by
`pytest.importorskip` and could not fail. Cutting this module does not remove the
dependence; it only makes it invisible again.

Where this module queries P6's tables directly, and why that is not a layering break:
`evidence_chain` is addressed by `fact_id` alone -- a reviewer clicking a citation has
the fact id and nothing else -- and no module publishes a by-`fact_id` read.
`values_with_counts` needs one aggregate across the whole corpus. Both are `SELECT`s over
`file_facts`, which is P6's own table. Everything else composes the published functions
and adds no second answer.
"""
from __future__ import annotations

import json
import sqlite3
from typing import Iterable, Sequence

from evidence_shape.observation import Observation
from evidence_shape.store import observations_by_key
from evidence_shape.vocabulary import check

from facts.domains import ActivationSignals, active_field_allowlist
from facts.families import DUPLICATE_FAMILY_FIELD, VERSION_FAMILY_FIELD
from facts.fields import FIELD_SCOPES, fields_in_scope, get_field
from facts.file_facts import facts_for_file
from facts.photo_event import EVENT_FIELD
from facts.session import DOWNLOAD_SESSION_FIELD
from facts import states as _states
from facts.states import STRENGTH_ORDER
from facts.supersede import fact_history
from facts.unresolved import unresolved_for_file
from facts.values import values_in_field

#: §3.6's two exclusions, DERIVED rather than spelled. Task 1 publishes the ladder
#: WEAKEST FIRST -- `STRENGTH_ORDER[0]` is the weakest ranked state and
#: `strength(state)` is `STRENGTH_ORDER.index(state)`, which is larger for stronger --
#: so dropping the FIRST member drops the weakest. `rejected` is the one member of
#: `STATES` that Task 1 gives no strength (it is `EXCLUDED_STATE`, an exclusion rather
#: than a rank), so it is absent from `STRENGTH_ORDER` by construction. Slicing the
#: first element off therefore drops both exclusions at once and no state name is
#: written down in this module.
#:
#: `STATES` itself is reached through the MODULE (`_states.STATES`) and never imported
#: by name: Task 1's guard forbids any other module from BINDING a collection whose
#: members are the six, and `from facts.states import STATES` is such a binding.
#:
#: The plan's Task 24 body says `STRENGTH_ORDER[:-1]` and calls the last member the
#: weakest. That is the opposite of the shipped ladder and would have excluded
#: `user_confirmed` -- a user's own answer -- from every folder proposal while still
#: excluding nothing weak. Shipped code outranks the task body; see the conflict report.
PROPOSAL_ELIGIBLE_STATES: tuple[str, ...] = STRENGTH_ORDER[1:]


class DanglingCitation(LookupError):
    """A fact cites an `observation_key` that resolves to no observation.

    §3.1 is unconditional -- "Every fact preserves where it came from" -- so a citation
    that resolves to nothing is a broken fact, not an empty result. Returning a shorter
    list would let an evidence-walk check pass by counting zero.
    """


def _ordered(rows: Iterable[sqlite3.Row]) -> list[sqlite3.Row]:
    """P6's own total order. Never SQLite's, never P4's insertion order.

    `(field_key, canonical_value, fact_id)` -- the same order `facts_for_file`
    publishes, restated here so a filtered or concatenated read still carries it.
    """
    return sorted(rows, key=lambda row: (row["field_key"], row["canonical_value"],
                                         row["fact_id"]))


def _in_fields(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
               field_keys: Sequence[str]) -> list[sqlite3.Row]:
    wanted = frozenset(field_keys)
    return _ordered(row for row in facts_for_file(conn, file_id, content_hash)
                    if row["field_key"] in wanted)


def facts_for(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
              states: Iterable[str] | None = None,
              domain: str | None = None) -> list[sqlite3.Row]:
    """Every fact for one file version, optionally narrowed by state or by field scope.

    Unfiltered, this includes `rejected` facts: §3.13 makes `rejected` an exclusion from
    proposals, not from the record, and the review UI has to be able to see what was
    rejected or §8.5's "Did it abstain when evidence was absent?" is unanswerable from
    the outside. `proposal_eligible` is the read that excludes it.

    A misspelled filter raises rather than returning an empty list: an empty list is how
    a caller concludes there are no facts, and a typo must not read as an answer.
    """
    allowed: frozenset[str] | None = None
    if states is not None:
        checked = tuple(states)
        for state in checked:
            check(state, _states.STATES, name="reliability_state")
        allowed = frozenset(checked)

    in_domain: frozenset[str] | None = None
    if domain is not None:
        check(domain, FIELD_SCOPES, name="scope")
        in_domain = frozenset(row["field_key"] for row in fields_in_scope(conn, domain))

    selected: list[sqlite3.Row] = []
    for row in facts_for_file(conn, file_id, content_hash):
        if allowed is not None and row["reliability_state"] not in allowed:
            continue
        if in_domain is not None and row["field_key"] not in in_domain:
            continue
        selected.append(row)
    return _ordered(selected)


def proposal_eligible(conn: sqlite3.Connection, *, file_id: str,
                      content_hash: str) -> list[sqlite3.Row]:
    """The facts a folder proposal may rest on.

    §3.6: a weak model output "may remain a possible clue for review; it must not quietly
    become a folder proposal or an asserted file property". `unresolved` rows are in a
    different table and are therefore absent by construction rather than by a filter.
    """
    return facts_for(conn, file_id=file_id, content_hash=content_hash,
                     states=PROPOSAL_ELIGIBLE_STATES)


def active_allowlist_for(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                         activation_signals: ActivationSignals) -> tuple[str, ...]:
    """§3.11's active field allowlist, republished under the name neighbours use.

    The signals are injected and this module adds no field of its own (§3.12): it
    returns what `facts.domains` returns, and nothing is appended, dropped or reordered.
    """
    return active_field_allowlist(conn, file_id=file_id, content_hash=content_hash,
                                  activation_signals=activation_signals)


def values_with_counts(conn: sqlite3.Connection, *,
                       field_key: str) -> list[tuple[str, int]]:
    """§5.5's branch preview: "The interface can state that Option A would create three
    schools, five terms, and twelve course branches."

    Counts FILES per value, because that is what a branch will hold. A value no live
    fact points at is omitted, because it would preview an empty folder: that is both
    the value nothing ever concluded (§3.12 lets a value auto-create on first sight) and
    the value a later pass superseded (§8.2 keeps the old row readable, and a readable
    old row is not a folder the product still proposes).

    Ordered by count descending then canonical value ascending, so the preview is stable
    across runs and does not depend on which database it was read from.
    """
    get_field(conn, field_key)
    counts: dict[str, int] = {
        row[0]: row[1]
        for row in conn.execute(
            "SELECT value_id, COUNT(DISTINCT file_id) FROM file_facts "
            "WHERE active = 1 AND superseded_by IS NULL GROUP BY value_id")
    }
    branches = ((row["canonical_value"], counts.get(row["value_id"], 0))
                for row in values_in_field(conn, field_key))
    return sorted(((value, count) for value, count in branches if count),
                  key=lambda pair: (-pair[1], pair[0]))


def _citation_order(observation: Observation) -> tuple[str, str, str, str]:
    """A total order over the rows one `observation_key` can resolve to.

    One key can resolve to several rows: the key hashes `content_hash`,
    `extractor_name`, the locator and the raw value and nothing else, so the same
    observation re-recorded at a later `extractor_version` is a second row under the
    same key (M14). `Observation` publishes no row id -- `observation_id` is the
    `evidence` table's column, not a field or property of the frozen object -- so the
    order is built from published fields.
    """
    return (observation.extractor_name, observation.extractor_version,
            observation.observed_at, observation.run_id)


def evidence_chain(conn: sqlite3.Connection, *, fact_id: str) -> list[Observation]:
    """One fact walked back to the P4 observations it cites.

    Every entry in `evidence_refs[]` is an `observation_key` (M14), which is
    content-addressed and excludes `extractor_version` by construction -- so a citation
    recorded before an extractor upgrade still resolves after one (§8.7).

    Raises `LookupError` for an unknown fact and `DanglingCitation` for a citation that
    resolves to nothing.
    """
    row = conn.execute("SELECT evidence_refs FROM file_facts WHERE fact_id = ?",
                       (fact_id,)).fetchone()
    if row is None:
        raise LookupError(f"no fact {fact_id!r}")
    chain: list[Observation] = []
    for key in json.loads(row[0]):
        found = observations_by_key(conn, key)
        if not found:
            raise DanglingCitation(
                f"fact {fact_id!r} cites {key!r}, which resolves to no observation; "
                "§3.1: every fact preserves where it came from")
        chain.extend(sorted(found, key=_citation_order))
    return chain


def history(conn: sqlite3.Connection, *, file_id: str,
            field_key: str) -> list[sqlite3.Row]:
    """Every row ever written for one slot, oldest first, superseded rows included.

    §8.2 keeps them readable: "a user reviewing a placement should still be able to
    inspect the origin of the conclusion".
    """
    get_field(conn, field_key)
    return fact_history(conn, file_id=file_id, field_key=field_key)


def unresolved_for(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                   field_key: str | None = None,
                   reason: str | None = None) -> list[sqlite3.Row]:
    """The abstentions, which appear in no fact read.

    An abstention is not a weak fact: it carries no value and no reliability state, so
    nothing downstream can read one off it and start treating it as a `possible`.
    """
    return unresolved_for_file(conn, file_id, content_hash, field_key=field_key,
                               reason=reason)


def event_facts(conn: sqlite3.Connection, *, file_id: str,
                content_hash: str) -> list[sqlite3.Row]:
    """G7's photo event -- a P9 seed, never a placement."""
    return _in_fields(conn, file_id=file_id, content_hash=content_hash,
                      field_keys=(EVENT_FIELD,))


def session_facts(conn: sqlite3.Connection, *, file_id: str,
                  content_hash: str) -> list[sqlite3.Row]:
    """G6's bounded download session. §3.9 makes it "not a basis for automatic semantic
    propagation", and `facts.session.require_possible` is what holds it at `possible`,
    so it never reaches `proposal_eligible`."""
    return _in_fields(conn, file_id=file_id, content_hash=content_hash,
                      field_keys=(DOWNLOAD_SESSION_FIELD,))


def family_facts(conn: sqlite3.Connection, *, file_id: str,
                 content_hash: str) -> list[sqlite3.Row]:
    """G5's duplicate family and version family."""
    return _in_fields(conn, file_id=file_id, content_hash=content_hash,
                      field_keys=(DUPLICATE_FAMILY_FIELD, VERSION_FAMILY_FIELD))


def is_destination_eligible(conn: sqlite3.Connection, *, field_key: str) -> bool:
    """§3.8: the product "should avoid using authorship or creator identity as a
    destination dimension".

    Raises `FieldNotInCatalogue` on an unknown field rather than answering False, so a
    typo cannot read as a policy (§3.12 forbids inventing fields; this read does not
    invent one either).
    """
    return bool(get_field(conn, field_key)["destination_eligible"])
