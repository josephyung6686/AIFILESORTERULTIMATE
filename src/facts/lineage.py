# src/facts/lineage.py
"""`97`'s lineage rule, as the owner ruled it on 11 Sep 2026.

`97` was ratified as written (`00`, Amendments of 2026-09-11, item 4) and as written
it ruled none of its four candidate signals -- "Candidate signals, none of them
ruled" (§3). The owner then ruled, in session on 11 Sep 2026:

    Two files are two versions of one document when they share a document title --
    the `title` observation, or the first `heading` observation where there is no
    `title` -- and their content hashes differ. Filenames are never a basis. The
    family's stored name is the shared title itself. The blocking key is the
    canonical form of that title, through the deployment's own canonicaliser.

Each half of that sentence answers one thing `97` left open, and each is honoured
here rather than restated:

**"they share a document title"** -- §8.3's prohibition is respected by
construction, because a title is CONTENT and not a name: "A content-hash match
supports deduplication review; a filename match alone does not." `97`'s own table
says of this signal "not forbidden; it is content, not a filename", and "nothing
new -- both are already extracted". Nothing here reads `filename`, `path` or
`normalized_filename`, and `_title` refuses every zone but the two.

**"their content hashes differ"** -- not checked here, because `version_family`
already excludes identical hashes before the rule is asked. A second check would be
a second home for one rule.

**The family's stored name is the shared title.** `97` §3 calls this "a second
decision" and constrains it only negatively: "it must not be a file hash ...
whatever names a version family must be safe to show and to send." A title passes
both. It is releasable by construction -- it is a value P6 already stores for other
fields and P9 already puts on group labels -- and it is not a hash, so it confirms
possession of nothing. `duplicate_family`'s own answer could not have been reused
even if the owner had not ruled: that names a family after the observation keys its
members SHARE, and an `observation_key` hashes `content_hash / extractor_name /
locator / raw_value`, so two files whose bytes differ share no key at all and the
intersection is always empty.

**The CANONICAL form is stored, not either member's raw spelling.** The two are the
same string on this corpus and need not be -- `Report  v2` and `Report v2` are one
title after the deployment's canonicaliser and two before it. Storing the raw form
would make the family's name depend on which member the union-find happened to
reach first; storing the canonical form makes it a property of the family.

**The family is UNORDERED, and that is said rather than implied.** The owner ruled
"whatever the observations give without inventing (if nothing in the evidence orders
them, record the family unordered and say so)". Nothing in the shared evidence orders
them: a `title` observation carries no sequence, a `heading` carries an ordinal
WITHIN its own document and not across documents, and the two orderings a person
would reach for are both refused -- the filename (`draft` before `final`) is §8.3's
prohibition, and the filesystem timestamp is not an observation at all but a `files`
column that a copy, a restore or a sync rewrites. So `version_family` writes one fact
per member carrying one shared value and no rank, which IS the unordered family; no
order is stored, and a reader of the plan is told the members are of one document
and not which came first.

**The state is `possible`. THE OWNER'S RULING DID NOT NAME IT, and this is a
derivation from `00` rather than a word anybody said.** `97` §2 lists `validated`
and `possible` and rules neither; the ruling of 11 Sep named the rule, the name, the
key and the ordering, and did not reach the state. What settles it is `00`:50's own
ladder, quoted rather than paraphrased:

    "A validated fact was found by a deterministic rule and PASSED CONTEXTUAL
    CHECKS, such as a course-code pattern appearing beside 'lecture,' 'syllabus,'
    or 'semester.' ... A possible fact is a useful but insufficient clue."

A shared title is a deterministic rule with no contextual check beside it -- one
signal, no second corroboration -- so it is not `validated` by that definition, and
`direct` is closed to it outright by Done-means 24 and `Lineage.__post_init__`,
because no explicit slot states a version relation. `possible` is what is left.

**The counter-argument is recorded because it is a real one.** The same sentence of
`00`:50 names "document title" among the reliable and explicit sources a DIRECT fact
is read from. That is about a title fact -- the title is directly stated -- and not
about the version relation the title implies, which nothing states. If the owner
reads it the other way the state becomes `validated` and one consequence follows
immediately, which is the reason the derivation is worth writing down:
`grouping.seeds.ANCHOR_STATES` admits `direct` and `validated` and not `possible`,
so at `possible` a version family does not by itself seed a group -- which is what
keeps a disk full of documents whose first heading is `Notes` or `Untitled` from
becoming one group -- and at `validated` it would. At either state the fact is
written, `shared_family_field` answers, and P9 can type the edge it would otherwise
refuse to type.
"""
from __future__ import annotations

import sqlite3
from typing import Callable

from database_agent.files_table import get_file

from evidence_shape.observation import Observation

from facts.evidence import cite, observations_for_version
from facts.families import VERSION_FAMILY_FIELD, Lineage
from facts.states import POSSIBLE

#: The two zones a document's own title can arrive in, in the order the owner's
#: ruling names them: "the `title` observation, or the first `heading` observation
#: where there is no `title`". Both are members of P4's published `ZONES` and neither
#: is spelled a second time anywhere in this module.
TITLE_ZONE: str = "title"
HEADING_ZONE: str = "heading"

#: `00`:50's ladder, through `facts.states` rather than as a literal. See the module
#: docstring: a shared title is a deterministic rule with no CONTEXTUAL CHECK beside
#: it, which is not what `00`:50 calls `validated`. THE RULING DID NOT NAME THIS
#: STATE -- it is derived, the counter-argument is written out above, and it is the
#: owner's to overturn.
LINEAGE_STATE: str = POSSIBLE


def _heading_ordinals(observation: Observation) -> tuple[int, ...]:
    """A heading's own address in its document, outermost first.

    P4 addresses a `heading` segment "by ordinal within parent" (D3, and
    `INDEXED_SEGMENT_KINDS`), so an H2 under the first H1 is `(1, 2)` and the second
    H1 is `(2,)`. Comparing those tuples is comparing document order.
    """
    return tuple(segment.index for segment in observation.location.container_path
                 if segment.kind == HEADING_ZONE and segment.index is not None)


def _title(conn: sqlite3.Connection, file_id: str) -> Observation | None:
    """This file version's title observation, or `None` where it states none.

    **"THE FIRST HEADING" IS THE DOCUMENT'S FIRST, NOT P6'S.**
    `observations_for_version` returns P6's own total order, which is
    `observation_key` ascending -- content-addressed, so it is a property of the
    corpus rather than of the database, which is exactly what it is for. It is NOT
    document order: a hash sorts `Appendix` before `Introduction` as readily as
    after it. Reading "first" off that order would have made a document's title
    whichever of its headings happened to hash lowest, and -- the failure that
    matters -- two drafts of one document that gained a heading between them could
    then pick different headings and form no family at all.

    So the headings are ordered by their OWN ordinals, which P4 records in the
    container path, and P6's total order breaks a tie. A tie is two headings at one
    address, which is a document that was read twice by two extractors; taking the
    corpus-stable one of those keeps the answer stable across runs.

    `None` is not a defect and not an `unresolved` row: a document that states no
    title has proposed no lineage, and the module's standing rule is that a relation
    nobody proposed was never attempted.
    """
    content_hash = dict(get_file(conn, file_id))["content_hash"]
    observations = observations_for_version(conn, file_id, content_hash)
    stated = [one for one in observations if one.location.zone == TITLE_ZONE]
    if stated:
        return stated[0]
    headings = [one for one in observations if one.location.zone == HEADING_ZONE]
    if not headings:
        return None
    # A heading with no ordinal at all sorts last: it is a heading whose position
    # the reader could not state, and a document that states one positioned heading
    # should be titled by that one.
    return min(headings, key=lambda one: (not _heading_ordinals(one),
                                          _heading_ordinals(one)))


def _canonical_title(conn: sqlite3.Connection, file_id: str,
                     canonical: Callable[[str, str], "str | None"]
                     ) -> tuple[str, Observation] | None:
    """The canonical title and the observation that states it, or `None`.

    `canonical` is the deployment's ONE canonicaliser -- the same
    `callable(field_key, value)` `placement.index` and `placement.retrieval` take,
    so a title that is one string at placement is one string here. A value it
    refuses is a value this deployment holds no canonical form for, and a family
    named by an uncanonicalisable string would be a family whose name depends on
    which member was read first.
    """
    observation = _title(conn, file_id)
    if observation is None:
        return None
    canonical_form = canonical(VERSION_FAMILY_FIELD, observation.raw_value)
    if not canonical_form:
        return None
    return canonical_form, observation


def title_block_key(canonical: Callable[[str, str], "str | None"]
                    ) -> Callable[[sqlite3.Connection, str], "str | None"]:
    """`version_family`'s blocking key: the canonical title.

    **It is a NECESSARY CONDITION of the rule below, which is the contract
    `version_family` states and cannot check.** `title_lineage` answers only when two
    files' canonical titles are EQUAL, so a pair the rule would join always shares
    this key and blocking loses no family. The two are built from one function
    (`_canonical_title`) for exactly that reason: a key and a rule that read the
    title differently would drift apart silently, and the symptom would be a missing
    family rather than a failing call.

    `None` -- no title, or a title this deployment cannot canonicalise -- takes the
    file out of every comparison, which is the key's own abstention.
    """
    def block_key(conn: sqlite3.Connection, file_id: str) -> str | None:
        found = _canonical_title(conn, file_id, canonical)
        return None if found is None else found[0]
    return block_key


def title_lineage(canonical: Callable[[str, str], "str | None"]
                  ) -> Callable[[sqlite3.Connection, str, str], "Lineage | None"]:
    """`97`'s rule under the owner's ruling of 11 Sep 2026: one shared title.

    Returns `None` -- no lineage proposed, and no `unresolved` row -- when either
    file states no title, or when the two titles are not one canonical string.

    The equality is re-checked here and not assumed from the blocking key. This is a
    published rule with `version_family`'s own signature: a caller may inject it
    beside a different key, and a rule that trusted its caller's blocking would then
    join every pair in a block it did not choose.
    """
    def lineage_rule(conn: sqlite3.Connection, left_file_id: str,
                     right_file_id: str) -> Lineage | None:
        left = _canonical_title(conn, left_file_id, canonical)
        right = _canonical_title(conn, right_file_id, canonical)
        if left is None or right is None:
            return None
        left_title, left_observation = left
        right_title, right_observation = right
        if left_title != right_title:
            return None
        return Lineage(
            family_value=left_title,
            reliability_state=LINEAGE_STATE,
            # BOTH titles, so each member's fact cites the observation on its OWN
            # file as well as the one it was matched against. `version_family`
            # intersects nothing here: it unions the refs of every edge a member is
            # on, and `_write_family` then cites the subset that is actually this
            # file's.
            evidence_refs=(cite(left_observation), cite(right_observation)))
    return lineage_rule
