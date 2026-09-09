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

**STILL FIVE AFTER 2026-09-07, AND THE NEW ONE IS A REUSE RATHER THAN A SIXTH.**
`105` §14.3's privacy classes put the value `protected` in `PRIVACY_CLASSES`, and it
is the FIRST of the five above spelled again -- P7's flag on
`classification.ClassificationRecord` -- not a new word. A class value meaning "this
file is protected" and a flag meaning "this file is protected" must not be two
strings, which is the same argument that keeps the other four apart. What is not
settled by reusing the word is whether the class and the flag pick out the same set
of files; that is SPEC Open question 1, still open, and
`classification.privacy_class_of` consumes the flag rather than inferring it.
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


#: SPEC §6: `model_target { locality: local | cloud, model_id, provider }`.
#:
#: **MOVED HERE FROM `privacy.release` ON 2026-09-08 (`104` R-159), and the reason is
#: an import cycle rather than a change of mind about whose vocabulary this is.**
#: R-159 made `items.check_item` decide two of its arms by the destination, and
#: `items` cannot import `release`: `release` imports `consent`, `consent` imports
#: `policy`, and `policy` imports `items` for `SUSPENDED_ITEM_KINDS`. This module is
#: the leaf every one of them already imports and the one whose whole subject is P7's
#: closed sets, so the vocabulary lives here and `release` re-exports it. Every
#: existing `from privacy.release import CLOUD_LOCALITY` keeps working and
#: `release.__all__` still publishes both names.
LOCALITIES: tuple[str, str] = ("local", "cloud")

#: The member of `LOCALITIES` that means the bytes leave the device. Named because
#: modules were comparing against the literal `"cloud"`, and brief §11 bans a bare
#: string. SPELLED, not indexed: `LOCALITIES[1]` is the other half of that same rule
#: -- an index couples every consumer to the tuple's ORDER, and a reorder would then
#: change what this means with no test failing. The guard below is what ties the two
#: together, so a rename in `LOCALITIES` is an ImportError rather than a comparison
#: that silently stops matching.
CLOUD_LOCALITY: str = "cloud"
if CLOUD_LOCALITY not in LOCALITIES:
    raise ImportError(
        f"{CLOUD_LOCALITY!r} is not one of SPEC §6's localities {LOCALITIES}")


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
#:
#: RULING 2026-08-31 (`80` §2), recorded here because a closed vocabulary carries its
#: own approval at the member. **A person's typed description of themselves -- their
#: roles, what they do -- is a `user_edits` item.** It was not anticipated when these
#: nine were written, and that absence was read for a while as an open question about
#: whether it fell inside them. It is not open. Free text, typed by the person, about
#: themselves, with no schema bounding what is in it, is the same risk class by
#: construction: it may carry a name, a diagnosis, a legal status, an employer under
#: NDA. Sensitive-until-proven-otherwise and fail closed is the test this design
#: already applies everywhere else.
#:
#: NO TENTH MEMBER IS ADDED. This is a scope gap in an existing rule rather than a new
#: rule, which is the whole reason it can be settled by reading rather than by
#: ratifying. It is also a RESTRICTION: it closes a path rather than opening one.
#:
#: Consent does not unlock it -- consent is the wrong instrument for content whose
#: sensitivity the person cannot preview or bound in advance. So a self-description
#: never leaves the device, and any future proposal to send one is a change to
#: `00`:186 and is refused until `00`:186 changes.
#:
#: AMENDED 2026-08-31 (`80` §8). Joseph suspended the ENFORCEMENT of this one
#: reading for development, with the irreversibility put to him first and
#: reaffirmed: the product is being built and the corpora are fixtures. The
#: CLASSIFICATION above is not withdrawn -- a self-description is still a
#: `user_edits` item -- and the other eight kinds are untouched. Three
#: conditions hold it scoped: local stays the DEFAULT and sending is an
#: explicit act; a run that sends says so on screen before it sends; and it
#: reverts before anyone who is not Joseph uses this. A sentence already sent
#: stays sent, and reverting does not recall it.
ALWAYS_LOCAL: tuple[str, ...] = (
    "paths", "complete_extracted_text", "ocr_output", "file_hashes", "image_exif",
    "gps", "user_edits", "group_memberships", "raw_sensitive_values",
)

#: The two members of P4's `evidence_shape.vocabulary.ZONES` that an excerpt may not
#: address. ADDED 2026-09-02 against the security review's CR-01, which reproduced a
#: whole absolute directory reaching the model-visible bytes on the ordinary release
#: path -- `/Users/<name>/Documents/Legal/Divorce`, released as an `Excerpt` because
#: no check in the product ever read `zone`.
#:
#: THIS IS A MAPPING ONTO THE NINE ABOVE, NOT A TENTH MEMBER. `ALWAYS_LOCAL` stays at
#: nine and `80` §2's "NO TENTH MEMBER IS ADDED" is untouched. `"path"` is the ZONE
#: through which member 1, `"paths"`, has a route out: `extractors/filesystem.py`
#: writes one observation per scanned file whose `raw_value` is the parent directory.
#: `"filename"` is here for a different reason -- the filename is §7.7's flagged sixth
#: RELEASABLE kind, admitted only as `items.Filename` under `allow_unratified` and
#: banned outright on a Protected Records file by §7.3. An `Excerpt` addressing a
#: filename zone is that kind arriving through a door where neither check applies, so
#: it is refused HERE and released THERE, which is what "the sixth kind is flagged"
#: was supposed to mean.
#:
#: Not enumerable from `ALWAYS_LOCAL` itself: the nine are kinds of DATA and the
#: fifteen zones are places in a document, and no member-by-member correspondence
#: exists between them (`"gps"` and `"image_exif"` both live in `metadata`, which is
#: releasable). Two names, chosen because §8.4 and §7.7 name exactly these two.
#:
#: **`ocr` ADDED 2026-09-04, AND IT IS THE SAME DEFECT ONE MEMBER ALONG.** CR-01
#: mapped member 1 (`paths`) to the `path` zone and §7.7's filename kind to
#: `filename`, and stopped. Member 3 is `ocr_output`, `extractors/ocr.py` writes
#: every recognised region into `zone="ocr"`, and nothing refused one -- so text
#: Apple Vision read off a scanned identity document was an ordinary releasable
#: excerpt. Measured on the owner's own disk the same night: a scanned HKID and a
#: vaccination record were both OCR'd, and a card number recognised in either was
#: a `Excerpt` the gate would have released.
#:
#: The paragraph above is exactly why it was missed, and it is worth reading twice:
#: "no member-by-member correspondence exists between them". The mapping is made BY
#: HAND, one member at a time, so a member with a zone nobody thought about has no
#: check anywhere. Three of nine are mapped now. THE OTHER SIX HAVE NOT BEEN
#: AUDITED, and whoever does that audit should treat this comment as the reason to.
#:
#: Still a mapping and still no tenth member: `ALWAYS_LOCAL` stays at nine.
#:
#: **WHOSE TARGET, ADDED 2026-09-08 BY THE OWNER'S RULING ON `104` R-159, §15.4 item
#: 14.** Everything above reads §8.4 with no locality in it, and that is the sentence
#: the ruling re-read. `00`:186 says paths, complete extracted text and OCR output
#: "should remain local", and it says that *"when a cloud model is used"* the engine
#: sends "selected excerpts" rather than full documents -- one sentence about a CLOUD
#: destination, applied here to every destination there is. The owner ruled the first
#: of §15.4 item 14's two ways: a LOCAL model may be shown a whole text unit, the
#: person's own folder path and OCR text, within the dossier ceiling; the cloud
#: restrictions stand unchanged for a cloud target. `RELEASED_TO_A_LOCAL_TARGET`
#: below is that ruling transcribed, and `gate.py`'s privacy-CLASS refusal -- already
#: `if locality == CLOUD_LOCALITY else ()` since `104` R-89 -- is the shape it copies.
#:
#: Measured on r15, which is what the ruling was made on: 54 of 199 files had body
#: readings and not one was releasable, 20 of 43 labelled coursework files carried
#: their course code only in the `path` zone, and 29 OCR runs were shown to nobody.
ALWAYS_LOCAL_ZONES: frozenset[str] = frozenset({"path", "filename", "ocr"})

#: The members of `ALWAYS_LOCAL_ZONES` the R-159 ruling releases to a LOCAL target,
#: in the ruling's own two words: "the person's folder path and OCR text".
#:
#: `filename` is NOT here and is refused for every target, which is the one place this
#: split departs from a flat reading of "the zone arm is cloud-only". Its membership
#: above was never §8.4's paths sentence: it is §7.7's flagged SIXTH releasable kind
#: wearing a zone, put here (CR-01) so that an `Excerpt` cannot address a filename and
#: bypass `allow_unratified` and §7.3's protected-records ban -- "refused HERE and
#: released THERE". Three docstrings state that invariant with no locality in them
#: (`gate`'s module text on `_located_zone`, `release.NAME_BEARING`,
#: `model_facts.build_fact_request`), and a local target that admitted a
#: `filename`-zone excerpt would falsify all three while releasing nothing new: the
#: name already arrives through `items.Filename`, the door built for it, and a second
#: copy of it is noise the ceiling pays for.
RELEASED_TO_A_LOCAL_TARGET: frozenset[str] = frozenset({"path", "ocr"})

#: The remainder, spelled rather than derived, so that the guard below has two
#: independently authored sets to compare instead of one and its own complement.
ALWAYS_LOCAL_ZONES_FOR_EVERY_TARGET: frozenset[str] = frozenset({"filename"})

if (RELEASED_TO_A_LOCAL_TARGET | ALWAYS_LOCAL_ZONES_FOR_EVERY_TARGET
        != ALWAYS_LOCAL_ZONES) or (RELEASED_TO_A_LOCAL_TARGET
                                   & ALWAYS_LOCAL_ZONES_FOR_EVERY_TARGET):
    raise ImportError(
        f"every member of {sorted(ALWAYS_LOCAL_ZONES)} belongs to exactly one side "
        f"of the `104` R-159 ruling, and "
        f"{sorted(RELEASED_TO_A_LOCAL_TARGET)} + "
        f"{sorted(ALWAYS_LOCAL_ZONES_FOR_EVERY_TARGET)} does not partition it. A "
        f"FOURTH always-local zone added without a locality decision would default "
        f"to reaching the local model, which is the direction the mapping above says "
        f"has been got wrong once already ('THE OTHER SIX HAVE NOT BEEN AUDITED')")

# --- §8.4: the compact dossier -----------------------------------------------

#: "the engine should send only a compact dossier relevant to the current question:
#: selected excerpts, redacted identifiers, candidate labels, non-sensitive metadata,
#: and evidence references." Five from that sentence; `filename` is the sixth and is
#: the SPEC's flagged reading -- §8.4 puts *paths* in the always-local set, §7.7 puts
#: the filename in the residual dossier, and §7.3 forbids filenames in prompts only
#: for Protected Records, which is vacuous under any reading that forbade them
#: everywhere. Adopted because P8 and P11 cannot build without an answer; held open as
#: Open question 2 rather than treated as settled.
#:
#: THE SEVENTH, `self_description`, ADDED 2026-09-02 WITH THE OWNER'S APPROVAL,
#: RECORDED HERE BECAUSE THAT IS WHERE AN APPROVAL BELONGS.
#:
#: WHAT IT COVERS, and it is narrower than its name: a REFERENCE to a person's
#: typed self-description -- `privacy.items.SelfDescription` carries the role
#: declaration's `question_id` and the gate resolves the wording -- released so a
#: model can propose the role shortlist `80` §1 specifies. It is not an approval
#: for self-description CONTENT to travel in a request, and it admits no second
#: question about the person.
#:
#: `ALWAYS_LOCAL` STAYS AT NINE AND IS UNTOUCHED. `80` §2's "NO TENTH MEMBER IS
#: ADDED" is unaffected by this and remains true. The classification of a typed
#: self-description as a `user_edits` item STANDS; what this member opens is one
#: narrow way for that item to be released, not a reclassification of it. The two
#: vocabularies sit near each other and are easy to confuse from inside only one:
#: this is the releasable-kinds set, that one is the set that never leaves.
#:
#: WHAT HE CHOSE, AND WHAT HE CHOSE IT OVER, because an approval that omits the
#: rejected options is a note rather than a record. Three routes were put to him:
#: this narrow P7 release path; a genuinely LOCAL model, which `readers/model_
#: ollama.py` could already serve with no change to P7 at all; and deferring until
#: a local version existed to compare against. He chose the release path with the
#: irreversibility named -- `00`:200, "revocation cannot necessarily retract data
#: already sent to an external provider" -- and observed that THE SCOPING IS THE
#: HARD PART. This member is the scoping.
#:
#: HE CHOSE IT TWICE, AND THE SECOND TIME KNOWINGLY, which is the part a later
#: reader needs most. `80` §1 rules for a LOCAL model -- once as the mechanism,
#: once as the reason, since §1.1 closes the cloud option because "revocation
#: cannot retract what has already left the device" -- and §2 adds that consent
#: does not unlock it. `80` §8 suspends §2's ENFORCEMENT without replacing §1's
#: mechanism. That conflict was put to the owner explicitly on 2026-09-02, with
#: the local model named as available and the cost recorded as unrecoverable, and
#: he reaffirmed the cloud route. **So `80` §1 was overturned deliberately and not
#: by oversight.** Anybody who finds §1 later and reads this as a mistake should
#: read `88` §5 before acting on it.
#:
#: THE SCOPING IS STRUCTURAL, NOT PROMISED. `items.py` holds one frozen dataclass
#: per releasable kind and takes no kind parameter, so the eight always-local kinds
#: have no type to be named by and never did (`88` §7). `check_item` admits this
#: kind only under `suspension_permits_self_description`, which has no default and
#: which the filename's `allow_unratified` does not imply -- `80` §8.1: "this
#: suspension reaches nothing but the self-description."
#:
#: `80` §8.3's three conditions still bind and are not modified by the ruling:
#: local is the DEFAULT, a run that sends says so on screen BEFORE sending, and it
#: reverts before anyone who is not Joseph uses this.
ITEM_KINDS: tuple[str, ...] = (
    "excerpt", "redacted_identifier", "candidate_label", "metadata_field",
    "evidence_reference", "filename", "self_description",
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
#:
#: **A NINTH REASON, ADDED 2026-09-04 beside `CLASSIFICATION_BASES`' fourth member,
#: and it exists because the eighth would have to lie.** `denial.deny_unclassified`
#: says, in the sentence a person reads, *"no classification record exists"*. A file
#: on `detector_no_safety_evidence` HAS one; answering it with `unclassified` would
#: put `96` §19's untruth into a different column -- telling the owner the product
#: never looked, when what happened is that it looked and found no safety word. The
#: paragraph above is the same argument for `protected`, one reason along.
DENIAL_REASONS: tuple[str, ...] = (
    "protected_cloud_target", "unclassified", "no_safety_evidence",
    "policy_revoked", "protected_records_template", "whole_document_requested",
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
#:
#: **A FOURTH MEMBER, ADDED 2026-09-04, and SPEC §2 names three.** It is a SPLIT of
#: `detector` and not a new kind of authority: both are the detector concluding from
#: the file's own terms, and the split records whether the conclusion rests on
#: anything about SAFETY. `96` §19 is why. Measured over the owner's 199 read files,
#: 78 were stored `personal_non_sensitive, protected=0` and **41 of those matched no
#: safety work type at all** -- among them a Hong Kong identity card read to 21
#: observations. §8.4 makes a handling class a precondition of a model call, so those
#: 41 had been held back by having no class; giving them one turned 41 silences into
#: 41 confident negatives and gained no evidence for any of them.
#:
#: `96` §20 states the property rather than a mechanism: the precondition should be
#: satisfied by *"evidence of having LOOKED, not merely by a class existing"*. The
#: weaker claim needs the weaker word, because `basis` is the only field in SPEC §2's
#: record that can carry it -- `handling_class` would have to lie about the class and
#: `protected` would have to lie about the flag.
#: **A FIFTH MEMBER, ADDED 2026-09-08 WITH THE OWNER'S APPROVAL, and it is the
#: first basis in this vocabulary that is not a rule or a person.** `104` §17.1:
#: the owner ruled that an LLM is the decision engine that sorts files, and named
#: this vocabulary as one of the three the ruling opens. The owner's intent was
#: stated in one line and it is the whole constraint on the spelling: **a model
#: verdict must NEVER be recorded as `detector`.**
#:
#: WHY THE FOUR COULD NOT CARRY IT. `detector` and `detector_no_safety_evidence`
#: both say a deterministic rule concluded from the file's own terms; a model
#: verdict written under either is `96` §19's untruth in a new column -- a sentence
#: claiming a rule fired where none did. `safety_domain` is §3.15's rule about a
#: domain. `user` is the person's own act, which is its own evidence. A model on
#: this device is none of the four, and until today it had nowhere lawful to write.
#:
#: THE SPELLING, AND WHAT IT WAS CHOSEN OVER. `local_model` was the obvious one and
#: is the one this module's own tests measured the refusal with. It was not taken,
#: for `96` §19's reason: **a basis word must not overclaim what was checked.** What
#: was checked is ONE question -- which of a SHORTLIST of situations, raised by the
#: recognisers themselves, this file is part of. The model is not shown the 23
#: schemas (`model_situation.shortlist_for`), is not asked what else the file might
#: be, and is not asked to examine it for anything the shortlist does not carry. A
#: bare `local_model` reads as "a model looked at this file", which is broader than
#: the question that was put, and a reader a run later would take it for a general
#: examination. Naming the question is the narrowing, and it is the same move the
#: fourth member made from the other side.
#:
#: `local` is load-bearing and stays. It says the bytes did not leave the device,
#: which is what makes a record about an UNCLASSIFIED file admissible at all:
#: `denial.UNCLASSIFIED_PERMITS_LOCAL` permits a local call on one and
#: `unclassified_denies` refuses every cloud release of one unconditionally. A
#: cloud model has no basis here and this member does not give it one.
#:
#: WHAT IT ESTABLISHES, AND WHAT IT DOES NOT. It establishes that a model running
#: on this device named one situation from a closed list it was shown, and that the
#: citation it gave resolved against what was released and matched the span -- the
#: same check every other site's answer passes (`llm_harness.validation.
#: check_citations`). It does NOT establish that the file is nothing else, that
#: anything outside the shortlist was considered, or that a person has agreed. It
#: is a `possible`-strength conclusion in `basis` terms: a later `user_confirmed`
#: record supersedes it, and `reliability_state` is where that ranking lives.
LOCAL_MODEL_SITUATION: str = "local_model_situation"

CLASSIFICATION_BASES: tuple[str, ...] = (
    "detector", "detector_no_safety_evidence", "safety_domain", "user",
    LOCAL_MODEL_SITUATION,
)

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

#: The sixth §3.13 state, an exclusion not a rank. Task 4's store keeps rejected
#: rows for §8.7's negative examples and never treats them as current. Published
#: here so `classification_store` does not respell the literal (brief §11).
REJECTED: str = "rejected"
if REJECTED not in RELIABILITY_STATES:
    raise ImportError(
        f"{REJECTED!r} is not one of §3.13's six reliability states "
        f"{RELIABILITY_STATES}; the states are P4's and this module re-exports them"
    )

#: The one basis a detector writes. Named so `classification.py` does not respell
#: `"detector"` beside `USER`.
DETECTOR: str = "detector"

#: The same detector, on a file where NOTHING SAFETY-RELATED WAS FOUND. Not a doubt
#: about the schema that won -- a physics syllabus recognised on ten academic terms
#: is still a physics syllabus -- but a refusal to let that recognition stand in for
#: an examination it never performed.
#:
#: The distinction is one empty-tuple test wide and the detector already computes it:
#: `recognition.detector._safety_readings_in_evidence` returns the safety domains
#: whose OWN WORK TYPES appear in the file's evidence, and it is already on the
#: classify path. `()` from it is the whole of the claim this word makes.
#:
#: WHAT IT IS NOT. It is not a sensitivity finding, so it marks nothing protected,
#: weakens no handling class, and withholds no file from local placement. `96` §19's
#: 41 files stay `personal_non_sensitive, protected=0` and stay placeable. The one
#: thing it does is stop a CLOUD model call standing on it -- see
#: `denial.no_safety_evidence_denies`, which is where the consequence lives, because
#: a vocabulary member that also decided things would be a rule with two homes.
DETECTOR_NO_SAFETY_EVIDENCE: str = "detector_no_safety_evidence"

#: SPEC §7's audit record: "outcome  released | denied | consent_requested". Every
#: model call is recorded -- §8.4 says "Every model call" with no exemption for a
#: local model -- and denials and consent requests are recorded too, on §8.2's "Every
#: significant event affecting a file" and §8.6's requirement that the UI show what
#: has been deferred and why.
AUDIT_OUTCOMES: tuple[str, ...] = ("released", "denied", "consent_requested")


# --- `105` §14.3: the two named lists, and the four privacy classes ----------
#
# THE OWNER'S RULING OF 7 SEPTEMBER 2026 (`105` §14.3, amending §13.3), recorded at
# the members because a closed vocabulary carries its own approval:
#
#   "Keep both lists, apply the most restrictive matching rule to the content and
#    its derivatives regardless of file format, and classify unresolved cases as
#    pending rather than ordinary."
#
# R-89 is why the lists exist. On the owner's own corpus a receipt, an order
# confirmation, a boarding pass and a screenshot were all being called "protected
# material (§8.4)" on a corpus whose `00`:120 names Receipts and Confirmations as
# their DESTINATION -- so the two lists were being read as one, and a file that
# should have been filed by a rule was being held back as if it were a passport.
# Two lists, two names, two different consequences.
#
# STILL NO DETECTION RULE, and this block does not weaken the module docstring's
# paragraph above. There is no regex, no gazetteer, no filename pattern, no keyword
# and no threshold here. These are the NAMES a detector writes; how a receipt is
# recognised as a receipt is hand-authored elsewhere, exactly as SPEC *Deferred*
# says. `privacy.classification.privacy_class_for` reads these names and recognises
# nothing.

#: Shown to NO CLOUD MODEL, and filed by rules and local models. `105` §13.3's own
#: five, in the owner's order. A file on this list is not withheld from the product:
#: it is withheld from the network, which is the whole difference from the list below.
ALWAYS_LOCAL_KIND_RECEIPT: str = "receipt"
ALWAYS_LOCAL_KIND_ORDER_CONFIRMATION: str = "order_confirmation"
ALWAYS_LOCAL_KIND_BOARDING_PASS_OR_TICKET: str = "boarding_pass_or_ticket"
ALWAYS_LOCAL_KIND_OWN_ACCOUNT_SCREENSHOT: str = "own_account_or_message_screenshot"
ALWAYS_LOCAL_KIND_BANK_OR_CARD_NOTIFICATION: str = "bank_or_card_notification"

ALWAYS_LOCAL_KINDS: tuple[str, ...] = (
    ALWAYS_LOCAL_KIND_RECEIPT,
    ALWAYS_LOCAL_KIND_ORDER_CONFIRMATION,
    ALWAYS_LOCAL_KIND_BOARDING_PASS_OR_TICKET,
    ALWAYS_LOCAL_KIND_OWN_ACCOUNT_SCREENSHOT,
    ALWAYS_LOCAL_KIND_BANK_OR_CARD_NOTIFICATION,
)

#: Shown to NO MODEL AT ALL, and filed one at a time by the person. `105` §13.3's
#: own five, in the owner's order.
PROTECTED_KIND_IDENTITY_DOCUMENT: str = "identity_document"
PROTECTED_KIND_MEDICAL_RECORD: str = "medical_record"
PROTECTED_KIND_FINANCIAL_STATEMENT_OR_TAX_RETURN: str = (
    "financial_statement_or_tax_return")
PROTECTED_KIND_CREDENTIALS_OR_PASSWORD_VAULT: str = "credentials_or_password_vault"
PROTECTED_KIND_LEGAL_DOCUMENT_NAMING_THE_PERSON: str = (
    "legal_document_naming_the_person")

PROTECTED_KINDS: tuple[str, ...] = (
    PROTECTED_KIND_IDENTITY_DOCUMENT,
    PROTECTED_KIND_MEDICAL_RECORD,
    PROTECTED_KIND_FINANCIAL_STATEMENT_OR_TAX_RETURN,
    PROTECTED_KIND_CREDENTIALS_OR_PASSWORD_VAULT,
    PROTECTED_KIND_LEGAL_DOCUMENT_NAMING_THE_PERSON,
)

#: The owner's own words for each of the ten, carried beside the snake_case
#: identifier the way `HANDLING_CLASS_LABELS` carries §8.4's five lines. A later
#: paraphrase is a failing test, and the reason is the same one §13.3 was written to
#: settle: "screenshots that show a person's own account or messages" is a narrower
#: promise than "screenshots", and the narrower one is the one that was ruled.
RESTRICTED_KIND_LABELS: Mapping[str, str] = MappingProxyType({
    ALWAYS_LOCAL_KIND_RECEIPT: "receipts",
    ALWAYS_LOCAL_KIND_ORDER_CONFIRMATION: "order confirmations",
    ALWAYS_LOCAL_KIND_BOARDING_PASS_OR_TICKET: "boarding passes and tickets",
    ALWAYS_LOCAL_KIND_OWN_ACCOUNT_SCREENSHOT:
        "screenshots that show a person's own account or messages",
    ALWAYS_LOCAL_KIND_BANK_OR_CARD_NOTIFICATION: "bank or card notifications",
    PROTECTED_KIND_IDENTITY_DOCUMENT:
        "identity documents (passport, licence, national id)",
    PROTECTED_KIND_MEDICAL_RECORD: "medical records",
    PROTECTED_KIND_FINANCIAL_STATEMENT_OR_TAX_RETURN:
        "financial statements and tax returns",
    PROTECTED_KIND_CREDENTIALS_OR_PASSWORD_VAULT: "credentials and password vaults",
    PROTECTED_KIND_LEGAL_DOCUMENT_NAMING_THE_PERSON:
        "legal documents naming the person",
})

#: The ten together. A kind outside it is not an error -- §13.3: "A kind on neither
#: list is ordinary" -- and this is the set a caller checks when it means to name a
#: RESTRICTED one. That distinction is the whole of `check_restricted_kind` below.
RESTRICTED_KINDS: tuple[str, ...] = ALWAYS_LOCAL_KINDS + PROTECTED_KINDS

if set(ALWAYS_LOCAL_KINDS) & set(PROTECTED_KINDS):
    raise ImportError(
        "a document kind is on both of `105` §13.3's lists. The lists are the "
        "owner's and the precedence between them is a rule about a FILE matching "
        "two kinds, never about one kind belonging to two lists"
    )


def check_restricted_kind(value: object) -> str:
    """One of the ten kinds `105` §13.3 restricts, refusing an outsider.

    NOT a check on every document kind, and the difference matters. The universe of
    document kinds is open -- a syllabus, an essay, a photograph -- and P7 publishes
    no list of it; §13.3 closes only the two RESTRICTED lists and rules everything
    else ordinary. So `privacy_class_for` does not call this on the kinds it is
    given, because an unrecognised kind there is an ordinary document and not a
    mistake.

    It exists for the detector writing INTO this vocabulary, which must name a
    restricted kind by the constant beside it and never by a literal (brief §11:
    "Never a bare string, never an index"). That is what stops `"reciept"` from
    becoming an ordinary file in silence: the misspelling is a `NameError` at the
    call site rather than a downgrade three modules away.
    """
    return _check(value, RESTRICTED_KINDS, "restricted document kinds")


#: `105` §14.3's precedence, and THE ORDER IS THE RULE rather than a presentation
#: choice: "Precedence, explicit: protected, then always-local, then ordinary."
#: `privacy_class_for` walks this tuple and returns the first class that matches, so
#: a reorder here changes what the product does -- which is why the test asserts the
#: sequence and not merely the membership.
#:
#: A screenshot of a bank statement is PROTECTED although account screenshots are
#: always-local; a receipt containing credentials is PROTECTED. Both are the owner's
#: own examples and both are the same sentence: the most restrictive matching rule
#: wins, applied to the CONTENT and its derivatives whatever the file format.
#:
#: **`pending` IS THE FOURTH AND IT IS NOT A DEGREE OF SENSITIVITY.** The other three
#: say what was found; `pending` says nothing was looked at. §14.3: "'On neither
#: list' distinguishes an assessed ordinary document from one the detector failed to
#: recognise, which is pending." It is last in the tuple because it is outside the
#: precedence, the way `rejected` is outside §3.13's ranking, and `first match wins`
#: never reaches it -- `privacy_class_for` returns it from its own branch.
#:
#: **`protected` HERE IS DELIBERATELY THE SAME WORD AS P7'S FLAG, not a sixth
#: spelling.** The module docstring counts five strings sharing the stem and says no
#: two are the same word; this one IS one of the five, reused rather than added,
#: because a class value meaning "this file is protected" and a flag meaning "this
#: file is protected" must not be two words. What the ruling does NOT settle is
#: whether the two are the same SET -- that is SPEC Open question 1, still open, and
#: `classification.privacy_class_of` consumes the flag rather than inferring it.
PRIVACY_CLASS_PROTECTED: str = "protected"
PRIVACY_CLASS_ALWAYS_LOCAL: str = "always_local"
PRIVACY_CLASS_ORDINARY: str = "ordinary"
PRIVACY_CLASS_PENDING: str = "pending"

PRIVACY_CLASSES: tuple[str, ...] = (
    PRIVACY_CLASS_PROTECTED,
    PRIVACY_CLASS_ALWAYS_LOCAL,
    PRIVACY_CLASS_ORDINARY,
    PRIVACY_CLASS_PENDING,
)

#: The class each restricted list produces, derived from the two tuples rather than
#: retyped, so a member moved between the lists moves its consequence with it. The
#: owner "may move any kind between the lists" (§13.3) and that move must be one
#: edit.
PRIVACY_CLASS_BY_KIND: Mapping[str, str] = MappingProxyType({
    **{kind: PRIVACY_CLASS_PROTECTED for kind in PROTECTED_KINDS},
    **{kind: PRIVACY_CLASS_ALWAYS_LOCAL for kind in ALWAYS_LOCAL_KINDS},
})


def check_privacy_class(value: object) -> str:
    return _check(value, PRIVACY_CLASSES, "privacy classes")



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


#: The questions held open that are NOT among SPEC Open questions 1-11, each with the
#: document that states it. They are separate from `OPEN_QUESTIONS` because that
#: mapping is keyed by the SPEC's own numbering and these three are not in it: one is
#: a cross-part conflict deferred to this build, one is a residue D2 deliberately left,
#: and one belongs to P4 and reaches P7 only through redaction.
#:
#: Nothing here is answered anywhere under `src/privacy/`, and
#: `tests/p7/test_p7_no_invention.py` fails the moment one of them is.
HELD_OPEN: Mapping[str, str] = MappingProxyType({
    "I6": (
        "§8.4 gives the user the right to 'review and delete local derived data'; "
        "§8.2 forbids updating or deleting an event. D3 (2026-08-21) ratified the "
        "DIRECTION -- events append-only forever, derived projections tombstonable, "
        "'derived' a literal enumerated list -- and ratified that NOTHING IS BUILT "
        "until P13 drives it. `delete_derived` therefore refuses on both sides of the "
        "enumeration and writes nothing. Also open in: P5 OQ6, P13 OQ11, P1 OQ16."
    ),
    "filename-sixth-releasable-kind": (
        "§8.4's releasable list names FIVE kinds and puts 'Paths' in the always-local "
        "set, while §7.7's residual dossier 'includes the filename' and §7.3 forbids "
        "filenames in prompts only for `Protected Records`. P7's SPEC adds a sixth "
        "kind and flags it itself (NEEDS-JOSEPH B5d / C9a). Task 7 builds it and makes "
        "it unadmittable without `allow_unratified`, so a reviewer sees an unratified "
        "reading rather than a shipped one."
    ),
    "round-5-cuts": (
        "Round 5 recommended seven cuts. D5 ratified CUT 1 (P6 Task 26). D13 "
        "(2026-08-22) ruled the remaining five KEPT, including CUT 2 (this part's "
        "Task 19, the transport guard) and CUT 4 (the `Gate` facade). They are held "
        "here because a kept cut is a decision that can be revisited, and the tasks "
        "carry their callouts so a later reader can decide against them with the plan "
        "in front of them."
    ),
})

#: Two entries were REMOVED on 2026-08-22 because Joseph ruled them, and a guard that
#: asserts a ruled question is still open fails the day the plan is executed -- the exact
#: failure this task's own preamble diagnoses for P6 OQ11 under D2.
#:   `P6-sensitivity-field-row` -> **D7**: P6 creates no `sensitivity_status` row and
#:      P7's `ClassificationRecord` is the sole home. C24 and C25 closed.
#:   `P4-region-origin`         -> **D10**: P4's `norm` means TOP-LEFT; the Vision
#:      adapter converts (`readers.ocr_vision._box`, commit 87016b0). C22 closed.
