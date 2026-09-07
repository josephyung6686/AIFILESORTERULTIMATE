# src/branch_situation.py
"""`104` R-37 with R-100: the situation is answered per top-level branch.

A run used to answer ONE situation for every file in the folder. `--situation
academic.coursework` on a Downloads folder made site A ask the coursework fields of
every file in it: on the owner's corpus 60 of 83 model calls went to files that
are not coursework, and the refused `work_type` answers said what the files were
(`application/pdf`, `notebook`, `survey`, `Research Paper`). On the person's
52-file walkthrough two cover letters were proposed under `Coursework/Summer2026/
cover letter` and a résumé under a course.

The ruling (`104` §15.2, R-100 with R-37): each proposed top-level branch carries
its own situation, derived from the files that ANCHOR it, and site A asks a
branch's fields only of the files under that branch or with an anchor for it in
reach. A file no branch reaches is asked nothing and is held for review.

**The anchor is a signal the deterministic pass already writes.** `facts.kind`
fills `work_type` from the library's own kind-of-file terms, and the compiled
recognition release authors those terms PER SCHEMA: measured over the four schemas
that declare the field, 940 of 942 terms belong to exactly one of them --
`syllabus`, `lecture`, `homework`, `problem set` are academic's; `cover letter`,
`resume`, `job description` are career's. So a validated `work_type` whose term one
schema owns is that schema's anchor, which is exactly "a syllabus anchors
coursework; a cover letter anchors applications". The recogniser's SCHEMA verdict is
deliberately not the anchor: measured on a synthetic Downloads folder it read a
cover letter as `clinical_practice` and a résumé as `college_applications`, and
`tests/integration/test_step4_recognition_as_a_gate.py` records why -- it answers
what a file is made of, not which life it is part of. It is a REACH signal here,
into branches an anchor has already opened, and never opens one.

**Reach, in three forms, each the product's own existing signal, and IN THAT
ORDER -- a fact outranks a reading:**

* an anchor of the branch;
* failing that, a direct or validated fact on one of the branch schema's own
  fields -- `subject` is academic's, `employer` and `job_title` are career's --
  which is P6's own conclusion about the file (a course code beside academic
  context IS a course fact, `00`:57) and needs no anchor to second it. Not
  `term` and not `work_type`: `cli.FIELDS_THAT_CANNOT_ANCHOR_A_MOVE` says those
  two cannot carry a file into a folder, and `Summer2026` shared between a
  syllabus and a cover letter is the bridge that filed the cover letters under
  Coursework;
* failing both, the recogniser's reading of the file -- its settled schema, its
  one near-miss, or the schemas it tied on -- where that names a branch that
  exists.

The order is the finding of the reverted merge 8b9280d. That merge let the
reading stand beside the fact, and a course whose files carried no kind word in
their names -- so no anchor -- but read as `career` to the term recogniser was
carried whole into the career branch: on the owner's corpus the coursework
branch lost its courses and came out flat by kind. The recogniser answers what
a file is made of; a validated `subject` says which course it is part of, and
the second question is the one a branch asks.

A file exactly one branch reaches is under it. A file two reach, or none, is
HELD: it is asked nothing, and P11 records for it whatever reason it would have
recorded anyway, which is the review set the screen already prints it under.

**With one branch the partition is the folder, byte for byte.** Every file is
under the default branch, nothing is held, and the run is the run it was; that is
ruling (4) and `tests/integration/test_r37_single_branch_is_byte_identical.py`
pins it against a fixture captured before this module existed.

**A branch's situation.** The default branch's is the one the person typed. Any
other branch's is the person's own answer to the per-branch question
`questions.triggers.question_for_situation` -- the trigger R-37 says was
registered and never fired, read back through `questions.store.selected_situation`
at scope `branch:<label>` -- or, when the library carries exactly one situation for
that schema, that one. Otherwise it is UNSETTLED: the question is recorded, its
files are asked nothing until it is answered, and the branch is still proposed so
the person sees where those files would go. This module chooses no situation on
the person's behalf: `104` §11.2 step 4's ruling is that the person, or a model
from valid options, decides, never a rule picking the first of twenty-six.

This module reads no database and imports nothing from the composition root. Every
signal arrives as a callable or a table, so `cli.run` remains the one place that
decides what a run may read.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

#: The fields that never carry a file into a branch, spelled once here and
#: asserted equal to `cli.FIELDS_THAT_CANNOT_ANCHOR_A_MOVE` by the composition
#: root's tests rather than imported, so this module stays free of `cli`.
BRIDGES_THAT_DO_NOT_REACH: frozenset[str] = frozenset({"work_type", "term"})

#: The scope a per-branch situation question is asked at, `questions.vocabulary.
#: SCOPE_BRANCH`'s word. Spelled here for the same reason as the set above; the
#: registry test asserts the two agree.
SCOPE_BRANCH: str = "branch"


@dataclass(frozen=True)
class Branch:
    """One proposed top-level branch and the situation it carries."""

    label: str
    schema: str
    #: `None` while the branch's situation is unsettled: the library carries more
    #: than one situation for the schema and the person has not said which.
    situation: str | None
    is_default: bool
    anchor_file_ids: tuple[str, ...]
    #: Every file this branch reaches, anchors included, in roster order.
    file_ids: tuple[str, ...]
    #: The situations the person may choose from when `situation` is `None`.
    candidate_situations: tuple[str, ...] = ()

    @property
    def scope(self) -> str:
        return f"{SCOPE_BRANCH}:{self.label}"

    @property
    def settled(self) -> bool:
        return self.situation is not None


@dataclass(frozen=True)
class BranchPartition:
    """The run's top-level branches and the files none of them reaches."""

    branches: tuple[Branch, ...]
    held: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.branches or not self.branches[0].is_default:
            raise ValueError("the default branch comes first and always exists")
        seen: set[str] = set()
        for branch in self.branches:
            overlap = seen & set(branch.file_ids)
            if overlap:
                raise ValueError(f"a file is under two branches: {sorted(overlap)}")
            seen.update(branch.file_ids)
        if seen & set(self.held):
            raise ValueError("a held file is under a branch")

    @property
    def single(self) -> bool:
        """One branch and nothing held: the run before R-37, exactly."""
        return len(self.branches) == 1 and not self.held

    @property
    def default(self) -> Branch:
        return self.branches[0]

    def branch_of(self, file_id: str) -> Branch | None:
        for branch in self.branches:
            if file_id in branch.file_ids:
                return branch
        return None

    def by_label(self, label: str) -> Branch | None:
        for branch in self.branches:
            if branch.label == label:
                return branch
        return None


def single_owner_terms(
        terms_by_schema: Mapping[str, Sequence[str]]) -> dict[str, str]:
    """`work_type` term -> the one schema that authored it; shared terms dropped.

    `terms_by_schema` is the compiled release's `work_type_terms` for the schemas
    that DECLARE the field, which is `cli.WORK_TYPE_VOCABULARY`'s own join. A term
    two of them author (`reference letter`, `reference list`) anchors neither: it
    would be this module choosing which life a file belongs to.
    """
    owners: dict[str, set[str]] = {}
    for schema_id, terms in terms_by_schema.items():
        for term in terms:
            owners.setdefault(term, set()).add(schema_id)
    return {term: next(iter(schemas)) for term, schemas in owners.items()
            if len(schemas) == 1}


def _named_by(verdict: object) -> frozenset[str]:
    """The schemas a recogniser outcome names, whatever its shape.

    Read by attribute rather than by type: a `Recognition` carries `schema_id`,
    an `Abstention` carries an optional near-miss `schema_id` and the schemas it
    `tied_schema_ids` on, and this module imports neither.
    """
    named: set[str] = set()
    schema_id = getattr(verdict, "schema_id", None)
    if isinstance(schema_id, str):
        named.add(schema_id)
    for tied in getattr(verdict, "tied_schema_ids", ()) or ():
        if isinstance(tied, str):
            named.add(tied)
    return frozenset(named)


def partition_by_branch(
        *,
        roster: Sequence[tuple[str, str]],
        default_label: str,
        default_situation: str,
        default_schema: str,
        anchor_facts_of: Callable[[str, str], Sequence[tuple[str, str]]],
        owner_of_term: Mapping[str, str],
        fields_of_schema: Callable[[str], Sequence[str]],
        verdict_of: Callable[[str, str], object],
        situations_of: Callable[[str], Sequence[str]],
        chosen_situation: Callable[[str], str | None],
) -> BranchPartition:
    """The run's branches, from the deterministic signals it already holds.

    `anchor_facts_of(file_id, content_hash)` returns the file's `(field, value)`
    facts at or above P9's anchor bar (`direct`, `validated`); `owner_of_term` is
    `single_owner_terms`' table; `fields_of_schema` is `facts.domains.
    DOMAIN_FIELDS`; `verdict_of` is the term detector's `explain`; `situations_of`
    lists the shipped situations of a schema; `chosen_situation(scope)` is
    `questions.store.selected_situation` bound to the run's database.
    """
    facts: dict[str, tuple[tuple[str, str], ...]] = {}
    anchors_of: dict[str, list[str]] = {}
    anchored_to: dict[str, str] = {}
    for file_id, content_hash in roster:
        facts[file_id] = tuple(anchor_facts_of(file_id, content_hash))
        owners = {owner_of_term[value] for field, value in facts[file_id]
                  if field == "work_type" and value in owner_of_term}
        if len(owners) == 1:
            schema_id = next(iter(owners))
            anchored_to[file_id] = schema_id
            anchors_of.setdefault(schema_id, []).append(file_id)

    schemas = [default_schema] + sorted(
        schema_id for schema_id in anchors_of if schema_id != default_schema)
    if len(schemas) == 1:
        return BranchPartition(branches=(Branch(
            label=default_label, schema=default_schema,
            situation=default_situation, is_default=True,
            anchor_file_ids=tuple(anchors_of.get(default_schema, ())),
            file_ids=tuple(file_id for file_id, _hash in roster)),), held=())

    # The fields that carry a file into each branch: the schema's own, less the
    # two bridges.
    own_fields = {
        schema_id: set(fields_of_schema(schema_id)) - BRIDGES_THAT_DO_NOT_REACH
        for schema_id in schemas}

    under: dict[str, list[str]] = {schema_id: [] for schema_id in schemas}
    held: list[str] = []
    for file_id, content_hash in roster:
        if file_id in anchored_to:
            reached = {anchored_to[file_id]}
        else:
            reached = {schema_id for schema_id in schemas
                       if any(field in own_fields[schema_id]
                              for field, _value in facts[file_id])}
            if not reached:
                reached = _named_by(verdict_of(file_id, content_hash)) & set(schemas)
        if len(reached) == 1:
            under[next(iter(reached))].append(file_id)
        else:
            held.append(file_id)

    branches: list[Branch] = []
    for schema_id in schemas:
        if schema_id == default_schema:
            branches.append(Branch(
                label=default_label, schema=schema_id,
                situation=default_situation, is_default=True,
                anchor_file_ids=tuple(anchors_of.get(schema_id, ())),
                file_ids=tuple(under[schema_id])))
            continue
        candidates = tuple(dict.fromkeys(situations_of(schema_id)))
        chosen = chosen_situation(f"{SCOPE_BRANCH}:{schema_id}")
        if chosen is not None and chosen in candidates:
            situation: str | None = chosen
        elif len(candidates) == 1:
            situation = candidates[0]
        else:
            situation = None
        branches.append(Branch(
            label=schema_id, schema=schema_id, situation=situation,
            is_default=False,
            anchor_file_ids=tuple(anchors_of.get(schema_id, ())),
            file_ids=tuple(under[schema_id]),
            candidate_situations=candidates if situation is None else ()))
    return BranchPartition(branches=tuple(branches), held=tuple(held))
