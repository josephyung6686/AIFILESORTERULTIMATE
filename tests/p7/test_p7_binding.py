# tests/p7/test_p7_binding.py
"""Done-means 5, and layer L1 of Done-means 3.

SPEC §6: "A release is consumed on first transport use." "The binding tuple is
(model_target, prompt_fingerprint, policy_version)." And the property the part
exists for: "a call that bypasses P7 is not a policy violation to be caught in
review -- it is a call that cannot be constructed."

The last one is testable in exactly one way and this file does it: build a
`Released` by hand, with a `release_id` the gate never minted, and show that
spending it fails. The dataclass is constructible. It is simply inert.
"""
import inspect
import sqlite3
from dataclasses import FrozenInstanceError

import pytest

from privacy.binding import (
    BINDING_TERMS, BindingMismatch, ReleaseAlreadySpent, ReleaseNotIssued,
    consume_release, content_digest, content_digest_of, mint_release,
)
from privacy.policy import Policy
from privacy.release import RELEASED_FIELDS, ModelTarget, Released

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
FINGERPRINT = "fp-1"
CLOUD = ModelTarget(locality="cloud", model_id="acme-large", provider="Acme")
OTHER_CLOUD = ModelTarget(locality="cloud", model_id="acme-small", provider="Acme")
LOCAL = ModelTarget(locality="local", model_id="llama-3-8b", provider="local")

_TYPED_DEFAULTS = {
    "release_id": "release-never-minted",
    "audit_id": 1,
    "policy_version": "policy-1",
    "materialised_items": (),
    "redaction_manifest": (),
    "model_target": CLOUD,
}


def a_released(**over) -> Released:
    """Built from `RELEASED_FIELDS`, never from a literal keyword list.

    Task 11 owns SPEC §6's six field names. Constructing from the published tuple
    means a field this task never reads can be respelled without breaking it, while
    a field it DOES read disappearing fails here, at the seam that cares.
    """
    missing = [name for name in RELEASED_FIELDS if name not in _TYPED_DEFAULTS]
    assert not missing, (
        f"RELEASED_FIELDS names {missing} and this test has no value for them; "
        "SPEC §6 changed and Task 12 needs a value, not a default")
    values = {name: _TYPED_DEFAULTS[name] for name in RELEASED_FIELDS}
    values.update(over)
    return Released(**values)


def a_policy(**over) -> Policy:
    base = dict(policy_version="policy-1", operation_mode="cloud_assisted",
                consent_grants=(("Academics", "cloud_model"),),
                redaction_settings={"names": "redacted", "previews": "redacted",
                                    "thumbnails": "redacted", "ocr_text": "redacted",
                                    "location_data": "redacted"},
                automatic_move_permissions={}, plan_version="plan-1",
                set_at=FIXED_CLOCK)
    base.update(over)
    return Policy(**base)


#: The fourth binding term for a release that materialised nothing, which is what
#: `a_released` builds. Folded through the published function rather than written as
#: a literal: the digest is what the gate and the door must agree on, and a literal
#: here would keep agreeing after they stopped.
NO_ITEMS_DIGEST = content_digest_of(())


def mint(conn, *, policy=None, model_target=CLOUD, prompt_fingerprint=FINGERPRINT,
         content_digest_value=NO_ITEMS_DIGEST, audit_id=1,
         minted_at=FIXED_CLOCK) -> str:
    return mint_release(conn, policy=policy or a_policy(), model_target=model_target,
                        prompt_fingerprint=prompt_fingerprint,
                        content_digest=content_digest_value, audit_id=audit_id,
                        minted_at=minted_at)


def spend(conn, released, **over) -> None:
    base = dict(model_target=CLOUD, prompt_fingerprint=FINGERPRINT,
                policy_version="policy-1",
                content_digest=content_digest_of(released.materialised_items))
    base.update(over)
    consume_release(conn, released, **base)


@pytest.fixture()
def minted(p7_conn) -> Released:
    """One live release, bound to CLOUD / fp-1 / policy-1."""
    return a_released(release_id=mint(p7_conn))


# --- minting ----------------------------------------------------------------

def test_a_minted_release_is_recorded_in_the_ledger(p7_conn, minted):
    row = p7_conn.execute("SELECT * FROM release_ledger WHERE release_id = ?",
                          (minted.release_id,)).fetchone()
    assert row is not None
    assert row["prompt_fingerprint"] == FINGERPRINT
    assert row["policy_version"] == "policy-1"
    assert row["audit_id"] == 1
    assert row["minted_at"] == FIXED_CLOCK
    assert row["spent_at"] is None


def test_two_mints_with_the_same_binding_get_different_ids(p7_conn):
    # The ledger is the authority and the entropy is not. What the entropy buys is
    # that a caller holding one id cannot walk to another one minted in the same run.
    first, second = mint(p7_conn), mint(p7_conn)
    assert first != second
    assert p7_conn.execute("SELECT count(*) c FROM release_ledger").fetchone()["c"] == 2


def test_a_mint_without_an_audit_record_is_refused_by_the_substrate(p7_conn):
    # SPEC §6's ordering guarantee, at its last mile: "the audit record is appended
    # ... BEFORE `Released` is returned." `append_event` returns `lastrowid`, which
    # exists only after the row does, so a mint with no audit_id is a mint whose
    # audit record was never written. SQLite refuses it; P7 does not have to remember.
    with pytest.raises(sqlite3.IntegrityError, match="NOT NULL"):
        mint(p7_conn, audit_id=None)


# --- single use -------------------------------------------------------------

def test_a_release_is_consumed_on_first_use(p7_conn, minted):
    # SPEC §6: "A release is consumed on first transport use."
    spend(p7_conn, minted)
    row = p7_conn.execute("SELECT spent_at FROM release_ledger WHERE release_id = ?",
                          (minted.release_id,)).fetchone()
    assert row["spent_at"] is not None


def test_a_second_use_of_the_same_release_is_refused(p7_conn, minted):
    spend(p7_conn, minted)
    with pytest.raises(ReleaseAlreadySpent):
        spend(p7_conn, minted)


def test_consuming_writes_no_event(p7_conn, minted):
    # C4: the gate writes its audit record and nothing else. The spend is a state
    # change on P7's own capability row, not a second entry in the one log; Task 10's
    # `model_release` is the record that a call was authorized.
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    spend(p7_conn, minted)
    assert p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"] == before


# --- the three binding terms, one test each ---------------------------------

def test_a_different_model_target_is_refused(p7_conn, minted):
    # §8.4's audit record must show "which model received the data". A payload
    # replayable against another model makes that field false.
    replayed = a_released(release_id=minted.release_id, model_target=OTHER_CLOUD)
    with pytest.raises(BindingMismatch):
        spend(p7_conn, replayed, model_target=OTHER_CLOUD)


def test_a_different_prompt_fingerprint_is_refused(p7_conn, minted):
    # §8.4's sixth audit field is "the prompt fingerprint"; B2 puts `call_site`
    # inside it, so one fingerprint is one call site and one prompt.
    with pytest.raises(BindingMismatch):
        spend(p7_conn, minted, prompt_fingerprint="fp-2")


def test_a_different_policy_version_is_refused(p7_conn, minted):
    # SPEC §6: "a release spent under a different policy version is not [the same
    # authorization]". This is the term that makes revocation forward-only rather
    # than retroactive -- see the policy-change test below.
    with pytest.raises(BindingMismatch):
        spend(p7_conn, a_released(release_id=minted.release_id,
                                  policy_version="policy-2"),
              policy_version="policy-2")


def test_a_binding_mismatch_does_not_spend_the_release(p7_conn, minted):
    # A mis-wired caller must not be able to destroy an authorization the user
    # granted, and a release that never reached a model must not be recorded as one
    # that did. The binding is checked before the spend, never after.
    with pytest.raises(BindingMismatch):
        spend(p7_conn, minted, prompt_fingerprint="fp-2")
    assert p7_conn.execute(
        "SELECT spent_at FROM release_ledger WHERE release_id = ?",
        (minted.release_id,)).fetchone()["spent_at"] is None
    spend(p7_conn, minted)


def test_a_released_whose_echo_disagrees_with_the_call_is_refused(p7_conn, minted):
    # `Released` echoes `model_target` and `policy_version` (SPEC §6). If the echo
    # and the checked binding could disagree, one of the audit record's two fields
    # would be false for whichever the transport actually used.
    with pytest.raises(BindingMismatch):
        consume_release(p7_conn, a_released(release_id=minted.release_id,
                                            model_target=LOCAL),
                        model_target=CLOUD, prompt_fingerprint=FINGERPRINT,
                        policy_version="policy-1",
                        content_digest=NO_ITEMS_DIGEST)


# --- audit_id is not a binding term -----------------------------------------

def test_the_binding_terms_are_the_specs_three_and_the_content_added_against_cr02(p7_conn):
    # SPEC §6's tuple is three, and this is the one place the fourth is compared
    # against it. It EXCEEDS the design's stated tuple, deliberately: §6's own reason
    # for binding is "to keep the audit record truthful", and a record naming one
    # redacted excerpt is as false of a call that carried a corpus as of a call to
    # another model. The reason is recorded at the constant.
    assert BINDING_TERMS[:3] == ("model_target", "prompt_fingerprint",
                                 "policy_version")
    assert BINDING_TERMS[3:] == ("content_digest",)
    assert "audit_id" not in BINDING_TERMS


def test_two_releases_differing_only_in_audit_record_both_consume(p7_conn):
    # SPEC §6, constructed exactly: "two releases differing only in audit record are
    # the same authorization".
    first = a_released(release_id=mint(p7_conn, audit_id=11), audit_id=11)
    second = a_released(release_id=mint(p7_conn, audit_id=12), audit_id=12)
    spend(p7_conn, first)
    spend(p7_conn, second)


def test_every_binding_term_is_a_ledger_column(p7_conn):
    # The comparison is driven by BINDING_TERMS. A fourth term added to the tuple
    # without a column to hold it fails here rather than silently comparing nothing.
    columns = {row[1] for row in p7_conn.execute("PRAGMA table_xinfo(release_ledger)")}
    assert set(BINDING_TERMS) <= columns


# --- unforgeability ---------------------------------------------------------

def test_a_hand_constructed_released_is_inert(p7_conn):
    # THE test. "A call that bypasses P7 is not a policy violation to be caught in
    # review -- it is a call that cannot be constructed."
    with pytest.raises(ReleaseNotIssued):
        spend(p7_conn, a_released(release_id="release-deadbeef"))


def test_constructing_a_released_is_permitted_and_useless(p7_conn):
    # The dataclass is not defended and does not need to be. Instantiating it is a
    # normal Python act that buys nothing, which is a stronger property than a
    # constructor that raises: nothing has to guess where the caller came from.
    forged = a_released(release_id="release-deadbeef")
    assert forged.release_id == "release-deadbeef"
    with pytest.raises(FrozenInstanceError):
        forged.release_id = "release-something-else"
    assert p7_conn.execute(
        "SELECT count(*) c FROM release_ledger WHERE release_id = ?",
        ("release-deadbeef",)).fetchone()["c"] == 0


def test_a_refused_consume_leaves_the_ledger_untouched(p7_conn, minted):
    before = p7_conn.execute("SELECT count(*) c FROM release_ledger").fetchone()["c"]
    with pytest.raises(ReleaseNotIssued):
        spend(p7_conn, a_released(release_id="release-deadbeef"))
    assert p7_conn.execute(
        "SELECT count(*) c FROM release_ledger").fetchone()["c"] == before


# --- the policy-version term is what makes revocation forward-only ----------

def test_a_release_minted_before_a_policy_change_still_consumes_against_its_own_version(p7_conn):
    # Task 15's `revoke` mints a new policy version and asserts `effective_from`
    # affects "future gate calls only". That property lives HERE: the ledger row
    # carries the version the release was minted under, so a token issued before the
    # revocation is still spendable against policy-1, while a call presented under
    # policy-2 is a different authorization. The other half -- that a request made
    # AFTER the revocation denies with `policy_revoked` -- is Task 13's.
    early = a_released(release_id=mint(p7_conn, policy=a_policy(policy_version="policy-1")))
    spend(p7_conn, early, policy_version="policy-1")
    late = a_released(release_id=mint(p7_conn, policy=a_policy(policy_version="policy-1")))
    with pytest.raises(BindingMismatch):
        spend(p7_conn, a_released(release_id=late.release_id,
                                  policy_version="policy-2"),
              policy_version="policy-2")


# --- shape ------------------------------------------------------------------

def test_mint_takes_the_policy_and_consume_takes_the_echo():
    # SPEC §6: "the gate owns the policy, so the caller does not supply this value,
    # it echoes it." The minter is inside the gate and holds the object; the
    # transport is outside it and can only echo a string.
    minting = inspect.signature(mint_release).parameters
    assert "policy" in minting and "policy_version" not in minting
    spending = inspect.signature(consume_release).parameters
    assert "policy_version" in spending and "policy" not in spending


def test_the_ledger_holds_no_content(p7_conn):
    # `excerpts_included` is "(observation_key, span) pairs ... not a second copy of
    # the text" (SPEC §7). A ledger that stored the payload would be that second
    # copy, in a table with no reason to have one.
    columns = {row[1] for row in p7_conn.execute("PRAGMA table_xinfo(release_ledger)")}
    # `content_digest` is the fourth binding term, added against CR-02. It is one
    # column wide whatever was released and it never leaves the device, so it is not
    # the "second copy of the text" §7 keeps out of here -- and without it the door
    # had nothing to compare a payload against, which is how a corpus went out under
    # a release whose one item was `"[redacted]"`.
    assert columns == {"release_id", "model_target", "prompt_fingerprint",
                       "policy_version", "content_digest", "audit_id", "minted_at",
                       "spent_at"}


def test_consume_release_is_the_only_spender():
    # Repo-wide, this is Task 21's. Here it is the module's own namespace: there is
    # no second function in `binding` that can mark a release spent.
    import privacy.binding as module
    published = {name for name, value in vars(module).items()
                 if not name.startswith("_") and callable(value)
                 and getattr(value, "__module__", None) == module.__name__}
    # `content_digest` and `content_digest_of` FOLD the fourth binding term; neither
    # touches the connection, and the `UPDATE ... SET spent_at` is still in exactly
    # one function.
    assert published == {"mint_release", "consume_release", "ReleaseNotIssued",
                         "ReleaseAlreadySpent", "BindingMismatch",
                         "content_digest", "content_digest_of"}


def test_p7_adds_no_delete_trigger_to_its_own_ledger(p7_conn):
    # Task 15 counts the tables carrying `BEFORE DELETE ... RAISE(ABORT)` and asserts
    # THIRTEEN. A fourteenth here would fail a sibling task. §8.2's R6 binds `events`;
    # the ledger is a capability record and P7 does not extend R6 by imitation.
    triggers = {row["name"] for row in p7_conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'trigger' "
        "AND tbl_name = 'release_ledger'")}
    assert triggers == set()
