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
OPTION_SENTENCES: Mapping[str, str] = MappingProxyType({
    CONSENT_OPTIONS[0]: "Allow a local model to read this text.",
    CONSENT_OPTIONS[1]: "Allow a cloud model to read this text.",
    CONSENT_OPTIONS[2]: "Allow a redacted prompt, with identifiers removed.",
    CONSENT_OPTIONS[3]: "Use no model for this.",
})
assert set(OPTION_SENTENCES) == set(FOUR_OPTIONS)
assert len(set(OPTION_SENTENCES.values())) == len(FOUR_OPTIONS)

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
    """Present the requirement and all four options. Refuse a shorter list."""
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
        options=FOUR_OPTIONS,
        option_sentences=OPTION_SENTENCES,
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
    check(option, FOUR_OPTIONS, name="consent option")
    return collect(
        conn, action_id=action_id, surface=SURFACE_CONSENT,
        subject_ref=subject_ref, plan_version=plan_version,
        session_id=session_id, action=ACTION_SELECT_CONSENT_OPTION,
        correction_scope=correction_scope,
        presented_state_ref=presented_state_ref, user_id=user_id,
        acted_at=acted_at, component_version=component_version,
        payload={"consent_request_id": item.consent_request_id,
                 "consent_option": option})
