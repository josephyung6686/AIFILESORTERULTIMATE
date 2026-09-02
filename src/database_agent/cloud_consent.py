"""The durable record of one decision: may this folder's files reach a cloud model.

**What this is, and what it is not.** It is not §8.4's consent grant. That
mechanism -- `privacy.consent`, `Policy.consent_grants`, the four options *local
model / cloud model / redacted prompt / no model use* -- answers a different
question: which of four ways one specific request for sensitive content may be
answered. Its scope is blocked on P7's Open question 3 (*"What is a corpus area?
... Consent grants cannot be scoped until this is named"*, `privacy/vocabulary.py`),
and P7's no-invention test fails the moment that question is answered inside
`src/privacy/`. This record is a different act: a person, once, turning the model
on for a folder. It is stored beside the ceilings and the learning resets because
it is the same shape -- a durable fact about this deployment that other parts read
and none of them derive.

**No new event type.** `database_agent/events.py` is a closed registry and
registering a name is "a spec-level act (rule 4)" with owner approval recorded at
the member. Nothing here mints one. The act is already in the log where it matters:
a run under an enabled record writes a policy with a non-local operation mode, and
`policy_set` records that mode.

**Append-only, and a revocation is a row.** §8.2 forbids updating or deleting an
event, and the same reasoning binds here even though these are not events: the
question *when was this on, and who turned it off* has to stay answerable. A
revocation that overwrote the grant would destroy the only record that months of
sending had ever been authorised. The decision in force is the newest row; the
older ones are the history that makes the newest one accountable.

**Why a decision carries a person and a time.** The owner accepted, in his own
words, that *"consent outlives the moment it was given"*. That is only an
acceptable risk if a run months later can say **who** decided and **when**, so the
person can recognise a decision they have forgotten making rather than discovering
it from a bill. A boolean is enough to decide and not enough to tell.

**THE SCOPE, which is the whole design.** A record is keyed to the exact corpus
root it was given for, and to nothing else.

* Not the database. Its default path is relative to the working directory, so one
  database is shared by every folder scanned from one shell -- and a decision made
  about one folder would silently cover a later scan of a home directory.
* Not the situation. `--situation` says what KIND of material this is, not which
  files; two different folders can carry one situation.
* **Not a path prefix.** Consent for `~/Desktop` would cover `~/Desktop/tax-returns`,
  which the person never saw when they decided. And the rule with no containment
  reasoning in it is the rule that cannot get containment wrong: a directory ABOVE
  the corpus root once changed classification in this product, and prefix matching
  is that same reasoning wearing a different hat.

So a parent asks again, a child asks again, and `/Users/jy/work` says nothing about
`/Users/jy/work-taxes`. The cost is one flag, once, for a folder the person is
already looking at. The alternative costs them files they never chose to send.

**Two spellings of one folder would defeat all of that**, so an unsettled root is
refused at BOTH ends rather than normalised. Normalising means resolving, resolving
touches the filesystem, and a store that follows a symlink answers about a folder
nobody named. The asymmetric version of this bug is the dangerous one: a writer
that refuses `/a/b/` and a reader that accepts it would answer "not enabled" for a
folder that is, and the run would go quietly local while the person believed
otherwise.

**What it deliberately does not decide.** Which operation mode an enabled record
selects. `84` §1 puts every policy in `src/cli.py`, and what may leave the device is
the largest policy in the product.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

#: The table, named once. `database_agent/db.py` creates it, so it exists as soon
#: as the database does: a person typing the gesture that turns sending OFF must
#: never be stopped by a bootstrap step an earlier refused run did not reach.
CLOUD_CONSENT_TABLE: str = "cloud_consent"

CLOUD_CONSENT_DDL: str = f"""
CREATE TABLE IF NOT EXISTS {CLOUD_CONSENT_TABLE} (
    -- An INTEGER PRIMARY KEY is sqlite's rowid under a name, and the name is the
    -- point: the column that decides which decision is in force has to be one a
    -- query can ORDER BY and an index can carry. `rowid` itself is neither.
    decision_id INTEGER PRIMARY KEY,
    corpus_root TEXT NOT NULL,
    decision    TEXT NOT NULL,
    user_id     TEXT NOT NULL,
    decided_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS cloud_consent_by_root
    ON {CLOUD_CONSENT_TABLE} (corpus_root, decision_id);
"""

#: The closed pair. Two words, because the decision has two states and a third
#: would be a state nobody has ruled on.
ENABLED: str = "enabled"
DISABLED: str = "disabled"
DECISIONS: tuple[str, str] = (ENABLED, DISABLED)

#: Which decision permits sending, one entry per member of `DECISIONS`. A table
#: rather than a comparison, for the reason `privacy.consent.CONSENT_AUTHORIZES` is
#: one -- and the reason is only real because the COVERAGE is checked. With two
#: words a table and `!= DISABLED` agree, so the table buys nothing today; it buys
#: everything the day somebody adds a third. `_PERMITS_SENDING` missing that word
#: is a failing test, where `!= DISABLED` is a silent grant of permission to send
#: a person's files, decided by whoever typed the new word.
_PERMITS_SENDING: dict[str, bool] = {ENABLED: True, DISABLED: False}

_SEPARATOR = "/"


class MalformedConsentRecord(ValueError):
    """A decision that cannot be stored, or a root that cannot be looked up."""


def _require_settled_root(corpus_root: object) -> str:
    """One folder, one string, or nothing at all.

    Both the writer and the reader call this. Asymmetry is how a record silently
    stops being found, and the direction it fails in -- "not enabled" for a folder
    that is -- looks exactly like a person who never granted anything.
    """
    if not isinstance(corpus_root, str) or not corpus_root:
        raise MalformedConsentRecord(
            "a consent record is about one folder and this names none. It must be "
            "the absolute, settled path of the corpus root.")
    if not corpus_root.startswith(_SEPARATOR):
        raise MalformedConsentRecord(
            f"{corpus_root!r} is not absolute. A relative root means the record's "
            f"key depends on the working directory, so a decision made in one "
            f"shell silently follows the person into another -- or silently fails "
            f"to. A record whose meaning depends on where you were standing is not "
            f"a record of a decision.")
    if corpus_root != _SEPARATOR:
        segments = corpus_root.split(_SEPARATOR)[1:]
        if any(segment in ("", ".", "..") for segment in segments):
            raise MalformedConsentRecord(
                f"{corpus_root!r} is not in its settled form -- a trailing "
                f"separator, a doubled one, a `.` or a `..` segment. One folder "
                f"spelled two ways is two rows, and a person who granted once "
                f"would be asked again for a folder they already decided about. "
                f"Pass the path the way `Path.resolve()` spells it. It is refused "
                f"rather than repaired because repairing means resolving, and a "
                f"store that follows a symlink answers about a folder nobody "
                f"named.")
    return corpus_root


def _require_text(value: object, *, name: str, why: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MalformedConsentRecord(f"{name} is required: {why}")
    return value


@dataclass(frozen=True, slots=True)
class CloudConsent:
    """One decision, with everything a screen needs to describe it."""

    corpus_root: str
    decision: str
    user_id: str
    decided_at: str

    def __post_init__(self) -> None:
        # Checked on the way OUT of the store as well as on the way in. The rows
        # live in a file a person can open with any sqlite tool, and a word nobody
        # ruled on must not become permission to send by being read back.
        if self.decision not in _PERMITS_SENDING:
            raise MalformedConsentRecord(
                f"{self.decision!r} is not one of {DECISIONS} and no rule says "
                f"whether it permits sending. Refused rather than assumed: the "
                f"assumption available here is that a word nobody has ruled on "
                f"means a person's files may leave the device.")

    @property
    def permits_sending(self) -> bool:
        """Whether this decision allows a file to reach a cloud model."""
        return _PERMITS_SENDING[self.decision]


def record_cloud_consent(conn: sqlite3.Connection, *, corpus_root: str,
                         decision: str, user_id: str, decided_at: str) -> None:
    """Append one decision. Granting and revoking are the same act, twice.

    Everything is checked BEFORE the insert. A writer that validated afterwards
    would leave the row behind, and a row nobody meant to write is indistinguishable
    from one somebody did.
    """
    root = _require_settled_root(corpus_root)
    if decision not in DECISIONS:
        raise MalformedConsentRecord(
            f"{decision!r} is not one of {DECISIONS}. A value outside a closed set "
            f"is a load error, not a fallback -- and the fallback available here "
            f"would be deciding on a person's behalf whether their files may leave "
            f"the device.")
    actor = _require_text(
        user_id, name="user_id",
        why="a run months from now has to be able to say WHO decided this, or the "
            "person cannot recognise a decision they have forgotten making")
    when = _require_text(
        decided_at, name="decided_at",
        why="a run months from now has to be able to say WHEN this was decided; "
            "that sentence is the only thing standing between a durable consent "
            "and a person discovering it from a bill")
    conn.execute(
        f"INSERT INTO {CLOUD_CONSENT_TABLE} "
        "(corpus_root, decision, user_id, decided_at) VALUES (?, ?, ?, ?)",
        (root, decision, actor, when),
    )


def cloud_consent_for(conn: sqlite3.Connection,
                      corpus_root: str) -> CloudConsent | None:
    """The decision in force for exactly this folder, or `None` if there is none.

    `None` is a fact and not a gap: nobody has decided, so the caller stays with
    whatever its local-first floor is. Ordered by `rowid` and not by `decided_at`,
    because two decisions can carry one timestamp and "which is in force" may not
    be ambiguous -- a person who turns sending off must not have that depend on
    clock resolution.
    """
    root = _require_settled_root(corpus_root)
    row = conn.execute(
        f"SELECT corpus_root, decision, user_id, decided_at "
        f"FROM {CLOUD_CONSENT_TABLE} WHERE corpus_root = ? "
        "ORDER BY decision_id DESC LIMIT 1",
        (root,),
    ).fetchone()
    if row is None:
        return None
    return CloudConsent(corpus_root=row["corpus_root"], decision=row["decision"],
                        user_id=row["user_id"], decided_at=row["decided_at"])
