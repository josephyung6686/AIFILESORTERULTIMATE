# src/privacy/vocabulary.py
"""§8.4's closed vocabularies, and the eleven questions P7 holds open.

Closed means a caller may not add a value. SPEC §1: "A value outside this set is a
load error, not a fallback." Adding a member is a P7 contract revision, not an
implementation decision, and the four `check_*` functions below refuse an outsider
WITHOUT suggesting a neighbour -- a suggestion is how a misspelling becomes a silent
downgrade, and a silent downgrade in this vocabulary is the failure §8.6 names:
"Cost exhaustion must never turn into lower-quality automatic classification."

Every member is the design's, in the design's order, and nothing here is invented.
Where the design writes prose, the prose is carried beside the identifier
(`HANDLING_CLASS_LABELS`, `MODE_SEMANTICS`) so a later paraphrase is a failing test.

**One home per vocabulary, and one named constant per member P7 writes.** Brief §11:
"Never a bare string, never an index." Two vocabularies reach this module from
outside their obvious owners for that reason. §3.13's six reliability states are
RE-EXPORTED from `evidence_shape.vocabulary` -- P4 ships them, `privacy` already
binds `evidence_shape`, and D7 empties P7's Contract-in from P6, so importing P4's
tuple is both the closest home and the only one available. SPEC §10's `shown` /
`redacted` pair lands here rather than in `policy.py` because three sections had
written it out under three names; `policy.py` re-exports these and deletes its own.

**This module holds no detection rule and no number.** SPEC *Deferred*: "The design
states *what* is protected and never *how it is recognised*. The detector rule set,
its signals, and its thresholds are hand-authored. P7 publishes the vocabulary the
detectors write into." There is no regex, no gazetteer, no filename pattern, no
keyword list, no threshold and no ceiling; §8.6 names the knobs, calls them
"configurable", and gives no values.

**Five strings share the stem "protected" and no two of them are the same word.**
P7's `protected` flag (`classification.ClassificationRecord`), P7's
`protected_cloud_target` and `protected_records_template` denial reasons, P3's
`untouched_protected` exclusion label and P3's `protected_container` exclusion reason.
P3's two are about READING -- a file inside a protected container never acquires the
(file_id, content_hash) pair the gate keys on, so `Gate.release` cannot be asked about
it. P7's three are about RELEASE, which is a policy the user can override through
consent, and that is exactly what makes it a different refusal. `src/privacy/` imports
neither of P3's constants; the distinction is pinned in `tests/p7/test_p7_vocabulary.py`.
"""
from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

# §3.13's six reliability states, RE-EXPORTED and not retyped. The import IS the
# publication: rebinding it -- `RELIABILITY_STATES = _RELIABILITY_STATES` -- would put
# a second module-level collection in `privacy` under a private alias, and a leading
# underscore exempts nothing from an introspecting guard. See the block beside
# `USER_CONFIRMED` below for why the states are P4's and not P6's.
from evidence_shape.vocabulary import RELIABILITY_STATES


class OutOfVocabulary(ValueError):
    """A value outside a closed set. SPEC §1: a load error, not a fallback."""


def _check(value: object, closed: tuple[str, ...], what: str) -> str:
    """Refuse an outsider by naming the closed set, never any of its members.

    The set is identified by name and size and its members are NOT enumerated. A
    refusal that printed them would put the nearest match in front of the author of
    the mistake, and `check_handling_class("public")` answering with `public_low` is
    how a misspelling becomes a silent downgrade -- the failure §8.6 names by name:
    "Cost exhaustion must never turn into lower-quality automatic classification."
    The closed tuple is published beside this function for a caller who wants to
    read it deliberately.
    """
    if not isinstance(value, str) or value not in closed:
        raise OutOfVocabulary(
            f"{value!r} is not one of the {len(closed)} {what} the design defines. "
            "The members are not listed here on purpose: a refusal that named the "
            "nearest one would be a suggestion, and a suggestion in this vocabulary "
            "is a silent downgrade. §8.4's vocabularies are closed -- a value "
            "outside the set is a load error, not a fallback, and adding a member is "
            "a P7 contract revision rather than an implementation decision."
        )
    return value


# --- §8.4: five handling classes, assigned before LLM escalation -------------

#: "The system should classify data into handling classes before LLM escalation".
#: The five, in the design's order. Absence of a classification resolves to the last
#: of them and NEVER to the first -- see `classification.resolve_class`.
HANDLING_CLASSES: tuple[str, ...] = (
    "public_low",
    "personal_non_sensitive",
    "sensitive_personal",
    "highly_sensitive_credential_bearing",
    "unreadable_unclassified",
)

#: The design's own five lines, so the snake_case identifiers above are traceable to
#: the words that define them rather than to a P7 author's choice of spelling.
HANDLING_CLASS_LABELS: Mapping[str, str] = MappingProxyType({
    "public_low": "Public or low sensitivity",
    "personal_non_sensitive": "Personal but non-sensitive",
    "sensitive_personal": "Sensitive personal",
    "highly_sensitive_credential_bearing": "Highly sensitive or credential-bearing",
    "unreadable_unclassified": "Unreadable or unclassified",
})


def check_handling_class(value: object) -> str:
    return _check(value, HANDLING_CLASSES, "handling classes")


# --- §8.4: four operation modes ----------------------------------------------

#: "The product should support clear operation modes". Four, in the design's order.
OPERATION_MODES: tuple[str, ...] = (
    "offline", "local_model", "hybrid", "cloud_assisted",
)

#: The design's four sentences, verbatim. A paraphrase can promise less than the
#: original -- "Sensitive files remain local" is the whole of what `hybrid` promises --
#: so the words are pinned and a rewording is a failing test.
MODE_SEMANTICS: Mapping[str, str] = MappingProxyType({
    "offline":
        "No content leaves the device; only local rules and local models may run.",
    "local_model":
        "Local extraction plus a user-installed local LLM for eligible dossiers.",
    "hybrid":
        "Sensitive files remain local; non-sensitive bounded dossiers may use a "
        "cloud LLM.",
    "cloud_assisted":
        "User explicitly permits selected corpus areas to use a cloud model.",
})


def check_mode(value: object) -> str:
    return _check(value, OPERATION_MODES, "operation modes")


# --- §8.4: the always-local set ----------------------------------------------

#: "Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user
#: edits, group memberships, and raw sensitive values should remain local." Nine, in
#: the design's order. Nothing here can be named as a releasable item kind, and Task 7
#: turns an attempt into the `always_local_item` denial.
ALWAYS_LOCAL: tuple[str, ...] = (
    "paths", "complete_extracted_text", "ocr_output", "file_hashes", "image_exif",
    "gps", "user_edits", "group_memberships", "raw_sensitive_values",
)

# --- §8.4: the compact dossier -----------------------------------------------

#: "the engine should send only a compact dossier relevant to the current question:
#: selected excerpts, redacted identifiers, candidate labels, non-sensitive metadata,
#: and evidence references." Five from that sentence; `filename` is the sixth and is
#: the SPEC's flagged reading -- §8.4 puts *paths* in the always-local set, §7.7 puts
#: the filename in the residual dossier, and §7.3 forbids filenames in prompts only
#: for Protected Records, which is vacuous under any reading that forbade them
#: everywhere. Adopted because P8 and P11 cannot build without an answer; held open as
#: Open question 2 rather than treated as settled.
ITEM_KINDS: tuple[str, ...] = (
    "excerpt", "redacted_identifier", "candidate_label", "metadata_field",
    "evidence_reference", "filename",
)


def check_item_kind(value: object) -> str:
    return _check(value, ITEM_KINDS, "releasable item kinds")


# --- §8.4 + §7.3 + §8.6: the eight denial reasons ----------------------------

#: SPEC Contract out §6, in the SPEC's order. `dossier_over_budget` is a backstop that
#: should never fire: M9 puts the ceiling and §8.6's four-rung ladder in P8, BEFORE
#: the call, because a gate-only check runs after the last point at which the dossier
#: could still be reduced. A `dossier_over_budget` denial in a running pipeline is a
#: P8 defect to fix, not a normal outcome.
#:
#: There is no bare `protected` here. `protected_cloud_target` is a protected file
#: with a cloud target; `protected_records_template` is §7.3's residual template,
#: which "should normally remain local-only and must not cause filenames or content
#: to be exposed in model prompts". Collapsing either onto `protected` would produce
#: a denial that cannot say which rule fired.
DENIAL_REASONS: tuple[str, ...] = (
    "protected_cloud_target", "unclassified", "policy_revoked",
    "protected_records_template", "whole_document_requested",
    "dossier_over_budget", "always_local_item", "mode_forbids_target",
)


def check_denial_reason(value: object) -> str:
    return _check(value, DENIAL_REASONS, "denial reasons")


# --- §8.4: the four consent options ------------------------------------------

#: "If a model needs text containing sensitive content, the user should see that
#: requirement and choose whether to allow a local model, a cloud model, a redacted
#: prompt, or no model use." Those four, exactly. `NeedsConsent` is a question only
#: the user can answer, and no caller may absorb it into an abstention (B2).
CONSENT_OPTIONS: tuple[str, ...] = (
    "local_model", "cloud_model", "redacted_prompt", "no_model_use",
)

# --- §8.4: the five configurable display facets ------------------------------

#: "The user can choose whether names, previews, thumbnails, OCR text, or location
#: data are shown." Where the design is silent on a default, W1 makes the more
#: redacting option the default -- that rule is Task 6's and no default lives here.
DISPLAY_FACETS: tuple[str, ...] = (
    "names", "previews", "thumbnails", "ocr_text", "location_data",
)

#: SPEC §10's `display_settings`: "each shown | redacted". The value vocabulary for
#: the facet vocabulary above, and the ONE home for these two strings. They were
#: written three times under three names -- `REDACTION_VALUES` in `policy.py`,
#: `SETTING_VALUES` in Task 18, `FACET_VALUES` in a third section -- and Task 5's own
#: A7 asked for this home: "if Task 2 publishes them, `policy.py` re-exports and
#: deletes its own." `policy.py` re-exports; nothing else respells.
SHOWN: str = "shown"
REDACTED: str = "redacted"
REDACTION_VALUES: tuple[str, str] = (SHOWN, REDACTED)

# --- SPEC §2 and §7: bases, states and outcomes ------------------------------

#: SPEC §2's classification record: "basis  detector | safety_domain | user".
#: `safety_domain` is §3.15's: finance, identity, medical and legal material ship
#: first as safety domains, "meaning the system detects and protects them before any
#: cloud or automated placement decision is allowed". This is NOT P6's five-value
#: `origin` vocabulary (§3.1) and the two are never mapped onto one another here.
CLASSIFICATION_BASES: tuple[str, ...] = ("detector", "safety_domain", "user")

#: The one basis P7 itself writes: Task 16's reclassification records the user's own
#: act. Named rather than spelled at the call site -- brief §11, "never a bare string,
#: never an index" -- because `basis="user"` was a literal in five sections before it.
USER: str = "user"

# §3.13's six reliability states are `RELIABILITY_STATES`, imported at the top of
# this module from `evidence_shape.vocabulary` and re-exported unchanged. A second
# tuple holding the same six strings is the second home the named-constant rule
# exists to prevent, and a re-export means a P4 revision reaches P7 by import rather
# than by memory. P4's order is the design's line 50 read in sequence -- "A user
# confirmed fact ... A direct fact ... A validated fact ... An LLM-supported fact ...
# A possible fact ... A rejected fact" -- and Task 4 ranks against it. The states are
# taken from P4 and not P6 deliberately: `privacy` already binds `evidence_shape`,
# and D7 empties P7's Contract-in from P6, so P7 imports nothing from P6 at all.

#: The one state P7 itself writes, beside `USER`. Task 16's record is the only
#: classification P7 originates; the other five states are read, never written, and
#: membership in the tuple above is what reading needs. Spelled, not indexed: brief
#: §11 bans `STATES[0]` because it couples every consumer to the tuple's ORDER, and
#: a reorder would then change meanings with no test failing. The test asserts
#: membership in P4's tuple instead, so a P4 rename goes red here.
USER_CONFIRMED: str = "user_confirmed"

#: SPEC §7's audit record: "outcome  released | denied | consent_requested". Every
#: model call is recorded -- §8.4 says "Every model call" with no exemption for a
#: local model -- and denials and consent requests are recorded too, on §8.2's "Every
#: significant event affecting a file" and §8.6's requirement that the UI show what
#: has been deferred and why.
AUDIT_OUTCOMES: tuple[str, ...] = ("released", "denied", "consent_requested")


# --- the eleven questions the design leaves open -----------------------------

#: P7's SPEC Open questions 1-11, held open. An entry here means "still unanswered".
#: Task 21 reads this mapping and fails if any of them is answered in an
#: implementation instead of in a SPEC. Where the design leaves a value open -- a
#: threshold, a ceiling, an identifier class, a redaction transform, a detection rule,
#: a retention period -- this part holds a caller-supplied strategy or a required
#: keyword, never a number and never a list.
OPEN_QUESTIONS: Mapping[int, str] = MappingProxyType({
    1: "Is `protected` exactly the top two handling classes? §8.4 lists five classes "
       "and, separately, five kinds of material that enter a protected state "
       "immediately, without stating the relation. Neighbouring parts consume the "
       "flag and never infer it from the class.",
    2: "Filename versus path. §8.4 puts paths in the always-local set, §7.7 puts the "
       "filename in the residual dossier, and §7.3 forbids filenames in prompts only "
       "for Protected Records. The contract adopts the reading that makes §7.3 "
       "non-vacuous and flags it.",
    3: "What is a corpus area? `cloud_assisted` permits a cloud model for selected "
       "corpus areas. A scan root, a frozen tree node, an accepted group, a domain? "
       "Consent grants cannot be scoped until this is named.",
    4: "Deletion versus append-only. §8.4 gives the user the right to review and "
       "delete local derived data; §8.2 forbids updating or deleting an event. "
       "Which wins, what counts as derived, and are audit records themselves "
       "deletable? Tracked as I6.",
    5: "Does `unreadable_unclassified` permit a LOCAL model call? Reading escalation "
       "strictly denies local calls on unclassified files, which may block exactly "
       "the OCR-opaque screenshots §2.7 and §7.8 want a model to interpret.",
    6: "Is a local-model call a consent event or only an audit event? §8.4 audits "
       "every model call and offers a local model as one of the four consent "
       "options. The threshold at which a local call needs a prompt is unstated.",
    7: "Does repeated reclassification generalize? §8.7 allows a repeated residual "
       "destination to become a corpus-level preference; it does not say whether "
       "repeated privacy corrections may raise a sensitivity floor.",
    8: "May a replay bundle carry audit records and excerpt spans? §8.5 allows a "
       "metadata-safe representation and lists policy settings; whether a bundle "
       "intended to leave the machine may carry records that name excerpts is "
       "unstated.",
    9: "What is an external connector besides a model? §8.4 gates any model or "
       "external connector, but no non-model connector is named in the twelve parts. "
       "If one is added later, does it route through `Gate.release`?",
    10: "Retention. How long audit records, consent grants and superseded "
        "classifications are kept. The design states no retention period anywhere.",
    11: "Which of `offline` and `local_model` ships as the install default. W1 closes "
        "the floor -- the default must be one of those two and may never be `hybrid` "
        "or `cloud_assisted` -- and the design names no answer between them.",
})
