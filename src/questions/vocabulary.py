# src/questions/vocabulary.py
"""P15's closed sets. `66` §13's two answer classes, and the states an answer has.

Every set here is closed, and each is closed for the same reason the rest of this
project closes its vocabularies: a value a deployment may invent is a value that
can quietly acquire a meaning nobody designed. §13 in particular draws a boundary
it calls a defect to cross, and a boundary with three sides is not a boundary.
"""
from __future__ import annotations


class OutOfVocabulary(ValueError):
    """A value outside one of P15's closed sets."""


#: `66` §13's two classes and no third.
#:
#: STRUCTURAL: "Resolves a user relationship or policy fact that file evidence
#: cannot safely determine." May "activate a schema, gate a template, resolve role
#: ambiguity, allow or prohibit a category of folder label, or require review".
#:
#: CONTEXTUAL: "Helps the product decide what to offer, explain, or prioritize."
#: May influence "ordering, examples, wording, and non-binding recommendations",
#: and must not "create, remove, hide, or rename folders; gate placement;
#: authorize movement; change privacy state; or silently become a structural
#: rule".
STRUCTURAL: str = "structural"
CONTEXTUAL: str = "contextual"
ANSWER_CLASSES: tuple[str, ...] = (STRUCTURAL, CONTEXTUAL)

#: What state an asked question is in for one scope.
#:
#: `skipped` and `not_applicable` are here because `66` §14 requires them to be
#: FIRST-CLASS answers: "It must preserve 'not about me' and 'skip for now' as
#: first-class answers." First-class means they are states rather than the absence
#: of one -- a question a person declined and a question nobody has been shown are
#: different facts, and a product that stores them the same way will ask again.
CONFIRMED: str = "confirmed"
SKIPPED: str = "skipped"
NOT_APPLICABLE: str = "not_applicable"
REVOKED: str = "revoked"
ANSWER_STATES: tuple[str, ...] = (CONFIRMED, SKIPPED, NOT_APPLICABLE, REVOKED)

#: The states in which an answer still governs anything. A revoked answer stays on
#: disk -- §12 requires answers to be "edited, revoked, or re-run" and a revocation
#: that deleted the row would lose the fact that the person once said otherwise --
#: but it decides nothing.
BINDING_STATES: tuple[str, ...] = (CONFIRMED,)

#: What SHAPE an answer takes. `66` §21 lists "allowed answer types" among the nine
#: obligations, and until 2026-08-30 there was exactly one shape: a pick-one from a
#: list the product authored. Two of §16's requirements cannot be said in that shape
#: -- §16:555's "store the raw user wording" and §16:543's role with "a scope and
#: possibly a time period".
#:
#: Closed at two, and the second is deliberately weak. A FREE_TEXT answer selects no
#: option, so `answered_options` never returns anything for it, so it activates no
#: schema and gates no template. That is §16:547 -- "An unmatched answer must remain
#: unmatched" -- enforced by the data model rather than by a downstream policy
#: somebody has to remember. Turning wording INTO a candidate schema is a separate
#: mechanism the owner has not yet ruled on (`62` §D), and nothing here anticipates it.
#:
#: CHOICE is the default because it is what every row P15 has ever written is.
CHOICE: str = "choice"
FREE_TEXT: str = "free_text"
ANSWER_TYPES: tuple[str, ...] = (CHOICE, FREE_TEXT)

#: Where an answer applies. `66` §12 requires the scope to be RECORDED and §13
#: forbids an answer being "reused outside its stated scope", so this is a prefix
#: vocabulary rather than a fixed list: `corpus` is the whole run, and
#: `organization:columbia` is one named entity the evidence actually produced.
#: A scope naming an entity is checked for its PREFIX only, because the entity
#: half comes from the user's own files and P15 does not hold a list of the world.
SCOPE_CORPUS: str = "corpus"
SCOPE_ORGANIZATION: str = "organization"

#: THE THIRD KIND, added 2026-08-30 under the ruling Joseph gave on 2026-08-29:
#: a closed vocabulary that cannot express what happened is a design gap rather
#: than a discipline, and may gain a member with the approval recorded at it.
#:
#: Why neither existing kind will do. A nesting answer is about ONE BRANCH of the
#: proposed tree -- `00`:78's "how should this branch be organised". `corpus` is
#: the whole run, so recording it there would let the shape somebody chose for
#: their coursework decide the shape of their legal matters, which is exactly what
#: §13's "not reused outside its stated scope" forbids. `organization` is "one
#: named entity THE EVIDENCE ACTUALLY PRODUCED", and a branch label is not that:
#: `Coursework` is a word the person typed on the command line, and calling it an
#: organisation would put a user's label where the vocabulary promises a fact.
SCOPE_BRANCH: str = "branch"
SCOPES: tuple[str, ...] = (SCOPE_CORPUS, SCOPE_ORGANIZATION, SCOPE_BRANCH)


def check(value: str, allowed: tuple[str, ...], *, name: str) -> str:
    if value not in allowed:
        raise OutOfVocabulary(f"{name} {value!r} is not one of {allowed}")
    return value


def check_scope(scope: str) -> str:
    """A scope is `corpus`, or `<kind>:<entity>` for a kind P15 recognises."""
    if not scope:
        raise OutOfVocabulary("an answer with no scope is a global rule")
    kind = scope.split(":", 1)[0]
    if kind not in SCOPES:
        raise OutOfVocabulary(
            f"scope {scope!r} names {kind!r}, which is not one of {SCOPES}")
    if kind != SCOPE_CORPUS and ":" not in scope:
        raise OutOfVocabulary(
            f"scope {scope!r} names a kind and no entity; a scope that names no "
            "entity applies everywhere, which is the one thing a scope exists to "
            "prevent")
    return scope


#: §16:553's four outcomes, and no fifth. APPENDED rather than inserted, so the
#: line numbers everything above this point is cited by do not move.
#:
#: > The matcher should produce one of four outcomes: an exact confirmed schema
#: > activation; a confirmed multiple-role activation; an unmatched answer
#: > preserved without activating a schema; or a skipped answer that leaves the
#: > related organizational decisions unresolved.
#:
#: These are the design's own four, spelled in snake_case and named nowhere else.
#: Closed for the reason §16:547 gives in the same breath: "'I'm a sound engineer'
#: must not silently activate an engineering or software-project schema merely
#: because the words are superficially similar." A fifth outcome -- `probable`,
#: `likely`, `assumed` -- is that snap arriving as a status value rather than as a
#: mapping, and it would be just as invisible to the person it was wrong about.
#:
#: MULTIPLE_ROLE_ACTIVATION is a property of the SET of live declarations and never
#: of one row: §16:543 requires that being more than one thing is normal, and a row
#: that claimed to be "the multiple one" would be a first among equals.
EXACT_ACTIVATION: str = "exact_activation"
MULTIPLE_ROLE_ACTIVATION: str = "multiple_role_activation"
UNMATCHED: str = "unmatched"
SKIPPED_ROLE: str = "skipped_role"
ROLE_OUTCOMES: tuple[str, ...] = (
    EXACT_ACTIVATION, MULTIPLE_ROLE_ACTIVATION, UNMATCHED, SKIPPED_ROLE)
