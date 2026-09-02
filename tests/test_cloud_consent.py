# tests/test_cloud_consent.py
"""The record of a decision a person makes once and lives with for months.

The owner accepted one risk in his own words -- **"consent outlives the moment it
was given"** -- and every test here is one of the three things that have to be true
for that to be an acceptable risk rather than a trap:

1. it can be taken back, by a gesture as small as the one that gave it;
2. it says WHEN it was given and by WHOM, so a run months later can put that on
   screen and a person is never surprised by a bill;
3. it covers what the person could actually SEE when they decided, and nothing
   else -- which is what every scoping test below is about.

The third is the hard one and it is the one the design is bent around. A grant is
keyed to the exact corpus root it was given for. Not the database (whose default
path is relative to the working directory, so one database is shared by every
folder scanned from one shell), not the situation (which says what KIND of material
this is, not which files), and NOT a path prefix -- consent for `~/Desktop` covering
`~/Desktop/tax-returns` is the failure this file exists to make impossible, and
prefix containment is the same reasoning the ancestor-classification bug lived in.
"""
from __future__ import annotations

import pytest

from database_agent.cloud_consent import (
    DECISIONS,
    DISABLED,
    ENABLED,
    CloudConsent,
    MalformedConsentRecord,
    cloud_consent_for,
    record_cloud_consent,
)

ROOT = "/Users/jy/Desktop/coursework"
OTHER = "/Users/jy/Desktop/taxes"
WHEN = "2026-06-14T09:00:00+00:00"
LATER = "2026-09-02T09:00:00+00:00"


def _record(conn, root=ROOT, decision=ENABLED, user_id="jy", decided_at=WHEN):
    return record_cloud_consent(conn, corpus_root=root, decision=decision,
                                user_id=user_id, decided_at=decided_at)


# --- nothing is enabled until somebody says so --------------------------------

def test_a_database_nobody_has_decided_in_returns_nothing(conn):
    """`None` is the answer, and the caller turns it into the local-first mode.
    Absent means refuse, never guess -- and here refusing means staying local,
    which is the direction that cannot spend money or send a file."""
    assert cloud_consent_for(conn, ROOT) is None


def test_the_decision_comes_back_with_who_and_when(conn):
    """Not a boolean. A boolean is enough to DECIDE and not enough to TELL, and
    `80` §8's second condition is that a run which sends says so on screen. "Cloud
    sending is on" is a worse sentence than "you turned this on for this folder on
    14 June", and only the second lets a person recognise a decision they have
    forgotten making."""
    _record(conn)
    consent = cloud_consent_for(conn, ROOT)
    assert consent == CloudConsent(corpus_root=ROOT, decision=ENABLED,
                                   user_id="jy", decided_at=WHEN)


def test_the_record_says_whether_it_permits_sending_rather_than_the_caller_guessing():
    """The word-to-meaning map lives with the words, so no caller writes
    `decision == "enabled"` and then, one refactor later, `!= "disabled"`."""
    assert CloudConsent(corpus_root=ROOT, decision=ENABLED, user_id="jy",
                        decided_at=WHEN).permits_sending is True
    assert CloudConsent(corpus_root=ROOT, decision=DISABLED, user_id="jy",
                        decided_at=WHEN).permits_sending is False


def test_every_decision_word_has_a_ruling_about_sending():
    """THE test that makes the lookup table worth having.

    With two words a table and `!= DISABLED` give the same answers, so nothing
    today can tell them apart -- which is exactly the state in which a guard
    quietly stops guarding. What separates them is the day somebody adds a third
    word: a table with no entry for it fails HERE, and `!= DISABLED` silently reads
    the new word as permission to send a person's files.
    """
    from database_agent.cloud_consent import _PERMITS_SENDING

    assert set(_PERMITS_SENDING) == set(DECISIONS)


def test_a_word_nobody_ruled_on_is_refused_on_the_way_out_of_the_store_too():
    """The rows are in a file any sqlite tool can edit. A decision word that
    reached the table by some other route must not become permission to send by
    being read back -- and the refusal is louder than a `False`, because a record
    that says something unreadable is not the same as one that says no."""
    with pytest.raises(MalformedConsentRecord):
        CloudConsent(corpus_root=ROOT, decision="maybe", user_id="jy",
                     decided_at=WHEN)


# --- it can be taken back, and taking it back is one more row -----------------

def test_the_latest_decision_is_the_one_in_force(conn):
    _record(conn, decision=ENABLED, decided_at=WHEN)
    _record(conn, decision=DISABLED, decided_at=LATER)
    consent = cloud_consent_for(conn, ROOT)
    assert consent.decision == DISABLED
    assert consent.permits_sending is False


def test_it_can_be_turned_back_on_after_being_turned_off(conn):
    """Forward-only, like P7's own revocation: withdrawing is not permanent, or a
    person who turns it off to think would be punished for thinking."""
    _record(conn, decision=ENABLED, decided_at="2026-01-01T00:00:00+00:00")
    _record(conn, decision=DISABLED, decided_at="2026-02-01T00:00:00+00:00")
    _record(conn, decision=ENABLED, decided_at="2026-03-01T00:00:00+00:00")
    assert cloud_consent_for(conn, ROOT).permits_sending is True


def test_revoking_writes_a_row_and_erases_nothing(conn):
    """§8.2 forbids updating or deleting an event and the same reasoning applies
    here: the question "when was this on, and who turned it off" has to stay
    answerable. A revocation that overwrote the grant would destroy the only record
    that the months of sending had ever been authorised."""
    _record(conn, decision=ENABLED, decided_at=WHEN)
    _record(conn, decision=DISABLED, decided_at=LATER)
    rows = list(conn.execute(
        "SELECT decision, decided_at FROM cloud_consent ORDER BY rowid"))
    assert [(row["decision"], row["decided_at"]) for row in rows] == [
        (ENABLED, WHEN), (DISABLED, LATER)]


def test_a_second_decision_at_the_same_instant_is_still_ordered(conn):
    """Two rows one clock tick apart must not make "which is in force" ambiguous.
    `decided_at` alone cannot order them; insertion order can, and does."""
    _record(conn, decision=ENABLED, decided_at=WHEN)
    _record(conn, decision=DISABLED, decided_at=WHEN)
    assert cloud_consent_for(conn, ROOT).decision == DISABLED


# --- THE SCOPE. What the person could see when they decided -------------------

def test_a_grant_for_one_folder_does_not_cover_another(conn):
    _record(conn, root=ROOT, decision=ENABLED)
    assert cloud_consent_for(conn, OTHER) is None


def test_a_grant_for_a_folder_does_not_cover_its_parent(conn):
    """THE failure this whole design is bent around. A person enabling cloud while
    looking at a folder of lecture notes has not agreed to a scan of their home
    directory, and a scan of the parent is a scan of everything they own. It is the
    same shape as the bug where a directory ABOVE the corpus root changed
    classification: what is outside the thing you named must not be decided by it.
    """
    _record(conn, root="/Users/jy/Desktop/coursework", decision=ENABLED)
    assert cloud_consent_for(conn, "/Users/jy/Desktop") is None
    assert cloud_consent_for(conn, "/Users/jy") is None


def test_a_grant_for_a_folder_does_not_cover_its_children_either(conn):
    """The softer direction, refused for the same reason and one more.

    A child IS a subset of what was consented to, so this is arguably safe -- and
    it is still refused, because the rule that has no containment reasoning in it
    is the rule that cannot get containment wrong. `84` §6: a gesture that acts on
    something other than what the person named is worse than one that stops and
    asks. The cost is one flag, once, for a folder the person is looking at anyway.
    """
    _record(conn, root="/Users/jy/Desktop", decision=ENABLED)
    assert cloud_consent_for(conn, "/Users/jy/Desktop/coursework") is None


def test_a_folder_whose_name_merely_starts_the_same_is_a_different_folder(conn):
    """`/Users/jy/work` and `/Users/jy/work-taxes`. A prefix comparison written
    with `LIKE` or `startswith` matches both, and the second is a folder nobody
    said anything about."""
    _record(conn, root="/Users/jy/work", decision=ENABLED)
    assert cloud_consent_for(conn, "/Users/jy/work-taxes") is None


def test_two_decisions_at_two_folders_do_not_interfere(conn):
    _record(conn, root=ROOT, decision=ENABLED, decided_at=WHEN)
    _record(conn, root=OTHER, decision=DISABLED, decided_at=LATER)
    assert cloud_consent_for(conn, ROOT).permits_sending is True
    assert cloud_consent_for(conn, OTHER).permits_sending is False


# --- two spellings of one folder are one folder, or the record is a lie -------

def test_a_relative_root_is_refused(conn):
    """The scoping guard, and the reason it is a refusal rather than a fix-up.

    A relative root means the key depends on the working directory, so consent
    given in one shell silently follows the person into another -- or silently
    fails to. Neither is a thing a person can predict, and a record whose meaning
    depends on where you were standing is not a record of a decision.
    """
    for relative in ("corpus", "./corpus", "../corpus", ""):
        with pytest.raises(MalformedConsentRecord, match="absolute"):
            _record(conn, root=relative)


def test_a_root_that_is_not_in_its_settled_form_is_refused(conn):
    """`/a/b`, `/a/b/`, `/a/./b` and `/a/c/../b` are one folder and four strings.
    Stored as four rows, a person grants once and is asked again on the next run
    for a folder they already decided about -- and `84` §6 says what the screen
    tells a person has to be true. Refused rather than normalised: normalising
    means resolving, resolving touches the filesystem, and a store that follows a
    symlink is a store that answers about a folder nobody named.
    """
    for unsettled in ("/Users/jy/Desktop/", "/Users/jy/./Desktop",
                      "/Users/jy/x/../Desktop", "/Users/jy//Desktop"):
        with pytest.raises(MalformedConsentRecord, match="settled"):
            _record(conn, root=unsettled)


def test_the_filesystem_root_is_a_legal_root_despite_its_trailing_separator(conn):
    """`/` is the one path whose settled form ends in a separator. Refusing it
    would be a rule about strings rather than about folders -- and a person who
    really does scan `/` is exactly the person whose consent must be recorded
    accurately."""
    _record(conn, root="/")
    assert cloud_consent_for(conn, "/").permits_sending is True


# --- a malformed record is refused at the writer, not stored -----------------

def test_a_decision_word_outside_the_closed_pair_is_refused(conn):
    for invented in ("on", "yes", "ENABLED", "granted", "", None):
        with pytest.raises(MalformedConsentRecord):
            _record(conn, decision=invented)


def test_the_closed_pair_is_exactly_two(conn):
    assert DECISIONS == (ENABLED, DISABLED)


def test_a_record_with_no_actor_or_no_time_is_refused(conn):
    """Both exist so a run months later can say who decided and when. A row
    missing either is a row that cannot produce the sentence the record exists to
    produce, and it would be found only when a person needed it."""
    for missing in ("", None, "   "):
        with pytest.raises(MalformedConsentRecord, match="user_id"):
            _record(conn, user_id=missing)
        with pytest.raises(MalformedConsentRecord, match="decided_at"):
            _record(conn, decided_at=missing)


def test_a_refused_record_stores_nothing(conn):
    """A writer that validated after inserting would leave the row behind."""
    with pytest.raises(MalformedConsentRecord):
        _record(conn, decision="on")
    assert conn.execute("SELECT COUNT(*) AS n FROM cloud_consent"
                        ).fetchone()["n"] == 0
    assert cloud_consent_for(conn, ROOT) is None


def test_the_lookup_refuses_a_root_it_could_never_have_stored(conn):
    """Asymmetry here is how a record silently stops being found: a writer that
    refuses `/a/b/` and a reader that accepts it would answer `None` for a folder
    that IS enabled, and the run would go quietly local while the person believed
    otherwise. The same check, on both sides."""
    _record(conn, root="/Users/jy/Desktop")
    for unsettled in ("Desktop", "/Users/jy/Desktop/", "/Users/jy/./Desktop"):
        with pytest.raises(MalformedConsentRecord):
            cloud_consent_for(conn, unsettled)


# --- the table is P1's and exists as soon as the database does ---------------

def test_the_table_exists_without_anyone_bootstrapping_it(conn):
    """`conn` is a bare `open_database`. A person typing `--disable-cloud` on a
    database from a run that refused early must still be able to turn it off, and
    a table created by a bootstrap step they never reached would raise instead."""
    assert conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='cloud_consent'"
    ).fetchone() is not None


def test_the_record_survives_the_connection_that_wrote_it(tmp_path):
    """The whole point of the word "durable". Written in one process, read in the
    next -- which is what a second run of the command is."""
    from database_agent.db import open_database

    path = tmp_path / "plan.sqlite"
    first = open_database(path)
    _record(first)
    first.commit()
    first.close()

    second = open_database(path)
    try:
        assert cloud_consent_for(second, ROOT).permits_sending is True
    finally:
        second.close()


def test_this_module_names_no_operation_mode(conn):
    """`84` §1: `src/cli.py` is the sole composition root and the only file in
    `src/` that picks a policy. WHICH of §8.4's four modes an enabled record
    selects is a policy, so this part answers "did this person enable cloud for
    this folder, when, and is it still in force" and stops there. A mode named
    here would be a part package deciding what may leave the device.
    """
    import inspect

    from privacy.vocabulary import OPERATION_MODES
    import database_agent.cloud_consent as module

    source = inspect.getsource(module)
    assert [mode for mode in OPERATION_MODES if mode in source] == []
