"""§8.4's consent moment. Four options, always, and never an abstention.

    "If a model needs text containing sensitive content, the user should see
    that requirement and choose whether to allow a local model, a cloud model,
    a redacted prompt, or no model use."

Three obligations, all binding (P13 SPEC:390-398), and each is enforced rather
than described:

1. **All four options are always presentable.** `consent_item` REFUSES a request
   offering fewer, because "a surface that offers fewer has silently made the
   user's decision for them" -- and the option a surface trying to be helpful is
   most likely to drop is `no_model_use`, which is the one that matters most.
2. **A pending consent request is never rendered as an abstention.** It renders
   as awaiting the user, at `review_policy = blocked_pending_user`, which is a
   live member of P11's `REVIEW_POLICIES`. B2 is explicit that `NeedsConsent`
   must never be mapped to `abstain`, and the rendering is the LAST place that
   mapping could reappear -- so `as_abstention` exists and always raises.
3. **The chosen option is routed to P7**, which authors the §8.4 consent events
   and the consent-aware audit record. P13 records the COLLECTION, not the grant.

SPEC Open question 5 is OPEN: what outcome a user-chosen "no model use" produces
is not settled, and P13 answers it nowhere. The option is presented and collected
exactly like the other three, and this module maps it to no outcome at all.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import NoReturn

from placement.vocabulary import BLOCKED_PENDING_USER
from privacy.consent import CONSENT_OPTIONS, ConsentRequirement, NeedsConsent

from review_surface.collect import collect
from review_surface.records import ReviewAction
from review_surface.vocabulary import (
    ACTION_SELECT_CONSENT_OPTION,
    SURFACE_CONSENT,
    check,
)

#: P7's four, imported. Respelling them here would be a second home for a
#: vocabulary P7 owns and validates against.
FOUR_OPTIONS: tuple[str, ...] = CONSENT_OPTIONS

#: §8.4's own phrasing of each option. The visual copy is deferred by the SPEC's
#: Deferred table; the DISTINCTION between the four is contractual.
#:
#: Keyed by the option's NAME, not by its position. P7 publishes `CONSENT_OPTIONS`
#: as a tuple and no named constant per member, so the four names are spelled here
#: -- which is a second home for P7's vocabulary and is the lesser of two evils.
#: Indexing the tuple instead would couple these sentences to its ORDER, so a
#: reordering upstream would silently swap "allow a cloud model" and "use no model
#: for this" with no test failing. The assertions below are what keep the two in
#: step; P7 publishing a constant per member would remove the second home
#: entirely.
OPTION_SENTENCES: Mapping[str, str] = MappingProxyType({
    "local_model": "Allow a local model to read this text.",
    "cloud_model": "Allow a cloud model to read this text.",
    "redacted_prompt": "Allow a redacted prompt, with identifiers removed.",
    "no_model_use": "Use no model for this.",
})
assert set(OPTION_SENTENCES) == set(FOUR_OPTIONS)
assert len(set(OPTION_SENTENCES.values())) == len(FOUR_OPTIONS)

#: WITHHELD FROM THE SCREEN, on the owner's ruling (`104` §18.7, S1, 9 Sep 2026).
#:
#: "Allow a redacted prompt, with identifiers removed" was a false sentence: no
#: identifier classifier exists in this deployment (`privacy/redaction.py`'s span
#: classifier declines every value and `cli.py` wires a transform nothing calls),
#: so choosing it granted `{local, cloud}` and sent bytes identical to plain cloud
#: consent while the screen said identifiers had been removed. The audit row
#: recorded `redaction_applied: False` truthfully; the person was not told. The
#: owner ruled the option is HIDDEN until a real classifier ships, rather than
#: kept with a warning.
#:
#: Withheld from PRESENTATION, not from P7's vocabulary. `CONSENT_OPTIONS` is P7's
#: closed set and a `NeedsConsent` still carries all four -- `consent_item` still
#: refuses a request that carries fewer, because P7's rule at its own seam is
#: unchanged -- and the surface presents the three that are true. The day a
#: classifier exists this set empties and the fourth sentence returns; it is data
#: so that day is one edit with one test, not a rewrite.
WITHHELD_OPTIONS: frozenset[str] = frozenset({"redacted_prompt"})
assert WITHHELD_OPTIONS < set(FOUR_OPTIONS)

#: What the person is shown and may choose: P7's four less the withheld, in P7's
#: order. `collect_consent_choice` checks the choice against THIS tuple, so a
#: withheld option cannot arrive from a stale screen or a hand-built action.
PRESENTED_OPTIONS: tuple[str, ...] = tuple(
    option for option in FOUR_OPTIONS if option not in WITHHELD_OPTIONS)

#: The one render state. Not a closed vocabulary because there is only ever one
#: value: a pending consent request is in exactly one state, and a tuple of one
#: would invite a second.
AWAITING_USER: str = "awaiting_user"


class ConsentOptionsIncomplete(RuntimeError):
    """A consent request offering fewer than §8.4's four options."""


class ConsentIsNotAnAbstention(RuntimeError):
    """Something tried to map a pending consent request to an abstention."""


@dataclass(frozen=True)
class ConsentSurfaceItem:
    """The requirement, the four options, and the state it is really in."""

    consent_request_id: str
    requirement: ConsentRequirement
    options: tuple[str, ...]
    option_sentences: Mapping[str, str]
    review_policy: str
    render_state: str


def consent_item(needs: NeedsConsent) -> ConsentSurfaceItem:
    """Present the requirement and the options that are true. Refuse a shorter
    request.

    The REQUEST must carry all four (P7's seam, unchanged); the ITEM presents
    `PRESENTED_OPTIONS`, which withholds the redacted-prompt option while no
    classifier exists (`104` §18.7 S1, the owner's ruling). The two checks are
    different questions: the first is whether P7 made the person's decision for
    them, the second is whether the screen tells them the truth.
    """
    offered = tuple(needs.options)
    missing = [option for option in FOUR_OPTIONS if option not in offered]
    if missing:
        raise ConsentOptionsIncomplete(
            f"consent request {needs.consent_request_id!r} offers "
            f"{list(offered)} and omits {missing}. All four §8.4 options are "
            "always presentable: a surface that offers fewer has silently made "
            "the user's decision for them")
    return ConsentSurfaceItem(
        consent_request_id=needs.consent_request_id,
        requirement=needs.requirement,
        options=PRESENTED_OPTIONS,
        option_sentences=MappingProxyType({
            option: OPTION_SENTENCES[option] for option in PRESENTED_OPTIONS}),
        review_policy=BLOCKED_PENDING_USER,
        render_state=AWAITING_USER)


def as_abstention(item: ConsentSurfaceItem) -> NoReturn:
    """Always raises. B2's forbidden mapping must not reappear at the renderer."""
    raise ConsentIsNotAnAbstention(
        f"consent request {item.consent_request_id!r} is awaiting the user. B2 "
        "is explicit that a NeedsConsent return must never be mapped to an "
        "abstention, and the rendering is the last place that mapping could "
        "reappear. It renders as awaiting the user, at review policy "
        f"{BLOCKED_PENDING_USER!r}, and never as a completed decision")


def collect_consent_choice(conn: sqlite3.Connection, item: ConsentSurfaceItem,
                           option: str, *, action_id: str, subject_ref: str,
                           plan_version: str, session_id: str,
                           correction_scope: str, presented_state_ref: str,
                           user_id: str, acted_at: str,
                           component_version: str) -> ReviewAction:
    """Collect the user's choice and route it to P7. P13 grants nothing.

    `correction_scope` is a required keyword with NO default, exactly as in
    `collect`. This is a departure from the P13 PLAN, which pinned the consent
    collector to `file` scope. §8.7's rule holds on every surface: a scope P13
    supplies is an inference wearing a keyword's clothes, and the whole mechanism
    is that no path exists by which one gets supplied.
    """
    # Against what was PRESENTED, not against P7's four: a withheld option is not
    # a choice the person could have made (`104` §18.7 S1).
    check(option, PRESENTED_OPTIONS, name="consent option")
    return collect(
        conn, action_id=action_id, surface=SURFACE_CONSENT,
        subject_ref=subject_ref, plan_version=plan_version,
        session_id=session_id, action=ACTION_SELECT_CONSENT_OPTION,
        correction_scope=correction_scope,
        presented_state_ref=presented_state_ref, user_id=user_id,
        acted_at=acted_at, component_version=component_version,
        payload={"consent_request_id": item.consent_request_id,
                 "consent_option": option})
