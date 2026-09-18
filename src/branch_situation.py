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

A file exactly one branch reaches is under it. A file NO branch reaches is the
DEFAULT branch's (`104` R-140): the person said what this folder is with
`--situation`, coverage is sacred, and a model may still decline every field.
Measured on the owner's corpus before R-140, 147 of 199 files met no model at all
and site C had nothing to judge. Only a file TWO branches reach is HELD: it is
asked nothing, and P11 records for it whatever reason it would have recorded
anyway, which is the review set the screen already prints it under.

**With one branch the partition is the folder, byte for byte.** Every file is
under the default branch, nothing is held, and the run is the run it was; that is
ruling (4) and `tests/integration/test_r37_single_branch_is_byte_identical.py`
pins it against a fixture captured before this module existed.

**A branch's situation.** The default branch's is the one the person typed --
and when they typed none (the owner's ruling of 11 Sep 2026; `--situation` is
optional) it is settled by exactly the rule below, because a branch the corpus
named is no more the person's answer than a branch its anchors opened. Any
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
from types import MappingProxyType

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

    #: WHAT A PERSON SEES THIS BRANCH CALLED, where a folder is named from it.
    #: Empty means "the label", which is what every caller that has not been
    #: taught about names gets -- and is exactly today's behaviour.
    display_name: str = ""

    @property
    def scope(self) -> str:
        return f"{SCOPE_BRANCH}:{self.label}"

    @property
    def folder_name(self) -> str:
        """The name to put on a FOLDER. Never the scope key, never empty."""
        return self.display_name or self.label

    @property
    def settled(self) -> bool:
        return self.situation is not None


@dataclass(frozen=True)
class BranchPartition:
    """The run's top-level branches and the files two of them reach.

    `held` is the genuinely ambiguous files: two branches reach each of them and
    nothing decides. A file no branch reaches is under the default branch.
    """

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


def the_one_situation(schema_id: str, *,
                      situations_of: Callable[[str], Sequence[str]],
                      raised: Sequence[str] = ()) -> str | None:
    """WHICH SITUATION A SCHEMA IS, FOR ONE FILE, OR `None`. Never a pick.

    A recogniser and site G both answer in SCHEMAS -- `research`, `finance` -- and
    every reader downstream needs a SITUATION, because the situation is what
    carries the folder levels, the field allowlist and the readings. The
    resolution used to be `situations_of(schema_id)[0]`, in three places, and it
    is a silent first pick: alphabetically first of the eight the library carries
    for `research` is `research.conference-presentation`, and of the eighteen for
    `finance` is `finance.cap-table-equity`. Measured on the shipped release: of
    the twenty-three schemas, NONE carries exactly one situation, four carry none
    and the rest carry between two and twenty-eight -- so the first pick decided
    the fields a file was asked and the folders it was offered, every time, on
    alphabetical order.

    Two arms answer and neither invents a ranking:

    * the library carries EXACTLY ONE situation for the schema -- then it is that
      one, and this is `104` §11.2 step 4's own permission: one situation is an
      answer and not a choice;
    * failing that, exactly one of the schema's situations is one the RECOGNISERS
      RAISED for this file (`recognition.SituationOutcome.candidates` through
      `model_situation.raised_for`, which is what site G was handed about it).
      Evidence about this file, not an order over the library.

    Otherwise `None`, and the caller must say so rather than choose: the person is
    asked which of them this is, and until they answer the file's situation is
    unresolved. `104` §11.2 step 4 in the words it was ruled in -- the person, or a
    model from valid options, decides, never a rule picking the first of
    twenty-six.
    """
    candidates = tuple(dict.fromkeys(situations_of(schema_id)))
    if len(candidates) == 1:
        return candidates[0]
    named = [situation for situation in candidates if situation in raised]
    if len(named) == 1:
        return named[0]
    return None


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


#: A gloss on an authored schema name -- *"Business operations (the
#: organisation's own running record)"* -- tells one schema from another on the
#: MODEL'S menu. It is not part of the name, and a folder called that is worse
#: than the id it replaces.
_GLOSS_OPENS = "("


def folder_name_for_schema(authored: str | None, schema_id: str) -> str:
    """What a PERSON should see this branch called, given the library's own name.

    The owner, 18 Sep 2026: *"the names and folder and stuff all human readable
    and not machine readable."* The tree over their corpus had seven roots and
    five were `nonprofit`, `photos`, `research`, `career`, `finance` -- internal
    identifiers written onto a real disk, because `partition_by_branch` labels a
    branch with its `schema_id` and the label becomes the folder.

    **THE NAMES WERE ALREADY THERE.** Every schema in the recognition rules
    carries an authored `name`, and `cli.py:18267` already hands them to site G so
    the MODEL reads a sentence instead of an id. The person got the id and the
    model got the sentence; this inverts that, which is the whole change.

    **THE ID IS THE FALLBACK AND NEVER SILENCE** (`104` §17.2). A schema the rules
    carry no name for, or name with nothing but a gloss, keeps its id: an unnamed
    folder is a crash at best and a file with nowhere to go at worst.

    This is NOT Phase 3. Phase 3 replaces the KIND with a LIFE as the partition
    key and `research` becomes Education. This changes no file's branch -- only
    what that branch is called -- and until the life lands, a kind should at least
    be spelled the way the library spells it.
    """
    name = (authored or "").strip()
    if _GLOSS_OPENS in name:
        # Split on the bracket itself and not on " (": a name that is NOTHING but
        # a gloss carries no leading space, and taking its head yields the empty
        # string, which falls through to the id below rather than to a folder
        # with no name.
        name = name.split(_GLOSS_OPENS, 1)[0].strip()
    return name or schema_id


def partition_by_branch(
        *,
        roster: Sequence[tuple[str, str]],
        default_label: str,
        default_situation: str | None,
        default_schema: str,
        anchor_facts_of: Callable[[str, str], Sequence[tuple[str, str]]],
        owner_of_term: Mapping[str, str],
        fields_of_schema: Callable[[str], Sequence[str]],
        verdict_of: Callable[[str, str], object],
        situations_of: Callable[[str], Sequence[str]],
        chosen_situation: Callable[[str], str | None],
        named_by_the_model: Mapping[str, str],
        situations_named_by_the_model: Mapping[str, str] = MappingProxyType({}),
        name_of_schema: Callable[[str], str | None] = lambda _schema: None,
        default_display_name: str | None = None,
) -> BranchPartition:
    """The run's branches, from the deterministic signals it already holds.

    `anchor_facts_of(file_id, content_hash)` returns the file's `(field, value)`
    facts at or above P9's anchor bar (`direct`, `validated`); `owner_of_term` is
    `single_owner_terms`' table; `fields_of_schema` is `facts.domains.
    DOMAIN_FIELDS`; `verdict_of` is the term detector's `explain`; `situations_of`
    lists the shipped situations of a schema; `chosen_situation(scope)` is
    `questions.store.selected_situation` bound to the run's database.

    **`named_by_the_model` IS SITE G'S ANSWER PER FILE** (`00` amendment 7): the
    schema of the whole library each file is part of, which is
    `cli._model_fact_pass`'s `situation_pass.named`, and it is EMPTY on the call
    that runs before the model pass. A schema G named for at least one file OPENS
    A BRANCH beside the anchored ones, and G's name is what puts the file under
    it -- AHEAD of the anchor, because the fact pass already asks that file's
    fields under G's schema (`_model_fact_pass`'s `by_schema[answered]`), so a
    branch chosen by the anchor would group and place a file against questions it
    was never asked.

    Measured at HEAD: a research paper in an `--situation academic.coursework`
    run had no branch of its own to be under. Only an anchor opened one, an
    anchor is a single-owner `work_type` term, and the paper's `work_type` says
    `Research Paper`, which no schema owns -- so the paper fell to the default
    branch and was grouped and placed against the coursework tree.

    A named schema the library carries NO situation for opens nothing, which is
    the rule `_model_fact_pass` already applies to the same names one module over:
    such a schema has no folder levels, so there is nothing a branch under it
    could be asked from.

    **`situations_named_by_the_model` IS THE JUDGE'S SECOND ANSWER PER FILE**
    (`00` amendment 1 of 14 Sep): the SITUATION each file is part of, which is
    `cli._model_fact_pass`'s `situation_pass.situations`, and it is EMPTY on the
    call that runs before the model pass. It settles a branch the judge answered
    for -- see `_settled_by_the_judge` -- and it opens none: a branch is opened by
    an anchor or by a KIND, and a situation is a refinement inside one.

    **`default_situation` IS `None` WHEN THE PERSON TYPED NO `--situation`**, on
    the owner's ruling of 11 Sep 2026 (`00` Amendments of 2026-09-11 item 2). The
    default branch is then settled by exactly the rule every other branch already
    has -- the person's own answer at this branch's scope, or the library's single
    situation for the schema, or UNSETTLED with its candidates carried for the
    question -- because with nothing typed there is no reason for the branch the
    corpus named to be treated differently from the branches its anchors opened.
    """
    def _situation_for(schema_id: str,
                       branch_label: str) -> tuple[str | None, tuple[str, ...]]:
        """This branch's situation, and the candidates when it has none.

        The one place the rule is spelled, read by the default branch and by every
        other. `104` §11.2 step 4's ruling stands in the third arm: the person, or
        a model from valid options, decides -- never a rule picking the first of
        twenty-six.

        THE SCOPE IS THE BRANCH'S LABEL and not its schema, because the label is
        what `questions.triggers.question_for_situation` puts the question under
        (`branch:<branch_label>`) and an answer looked for anywhere else is an
        answer the person gave and the run never found. They are the same string
        for every branch but a default one the person named with `--label`.
        """
        candidates = tuple(dict.fromkeys(situations_of(schema_id)))
        chosen = chosen_situation(f"{SCOPE_BRANCH}:{branch_label}")
        if chosen is not None and chosen in candidates:
            return chosen, ()
        # `the_one_situation`'s first arm, and it is the same rule spelled once:
        # a branch is not a file, so there is no per-file raised set to hand it.
        one = the_one_situation(schema_id, situations_of=situations_of)
        if one is not None:
            return one, ()
        return None, candidates

    def _settled_by_the_judge(file_ids: Sequence[str],
                              candidates: Sequence[str]) -> str | None:
        """The one situation the judge named for EVERY file of this branch.

        `00` amendment 1 of 14 Sep: the judge names the situation and "the person
        is asked only where the judge cannot", so a branch the judge answered for
        is a branch with nothing left to ask about -- its question is not
        recorded, its files are asked their own situation's fields, and its
        folders are built. This is the one place that becomes true of a BRANCH;
        `cli._the_situation_this_file_is_under` is where it becomes true of a file.

        UNANIMOUS, AND OVER EVERY FILE RATHER THAN EVERY ANSWERED FILE. One file
        the judge declined is one file whose situation the person still has to
        settle, and the question they are asked is the branch's -- so a branch
        carrying such a file stays unsettled and asks it. Two situations named
        under one branch is the same state seen the other way: the branch is not
        one piece of work, and picking the majority would be this module choosing
        a situation on the person's behalf, which `104` §11.2 step 4 forbids in
        the words the third arm of `_situation_for` already stands on.

        CHECKED AGAINST THE BRANCH'S OWN CANDIDATES, so a stale answer replayed
        out of an earlier run's records cannot settle a branch on a situation this
        release no longer carries under its schema.
        """
        if not file_ids:
            return None
        named = {situations_named_by_the_model.get(file_id)
                 for file_id in file_ids}
        if len(named) != 1:
            return None
        one = next(iter(named))
        return one if one in candidates else None

    def _default() -> tuple[str | None, tuple[str, ...]]:
        if default_situation is not None:
            return default_situation, ()
        return _situation_for(default_schema, default_label)

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

    #: Site G's name for each file, less the ones no branch could be built from.
    named_of = {file_id: named_by_the_model[file_id]
                for file_id, _hash in roster
                if named_by_the_model.get(file_id)
                and situations_of(named_by_the_model[file_id])}
    #: The schemas G opened a branch with, which the anchors did not have to.
    model_named = {schema_id for schema_id in named_of.values()
                   if schema_id != default_schema}

    schemas = [default_schema] + sorted(
        {schema_id for schema_id in anchors_of if schema_id != default_schema}
        | model_named)
    if len(schemas) == 1:
        situation, candidates = _default()
        return BranchPartition(branches=(Branch(
            label=default_label, schema=default_schema,
            display_name=default_display_name or default_label,
            situation=situation, is_default=True,
            anchor_file_ids=tuple(anchors_of.get(default_schema, ())),
            file_ids=tuple(file_id for file_id, _hash in roster),
            candidate_situations=candidates),), held=())

    # The fields that carry a file into each branch: the schema's own, less the
    # two bridges.
    own_fields = {
        schema_id: set(fields_of_schema(schema_id)) - BRIDGES_THAT_DO_NOT_REACH
        for schema_id in schemas}

    under: dict[str, list[str]] = {schema_id: [] for schema_id in schemas}
    held: list[str] = []
    for file_id, content_hash in roster:
        if file_id in named_of:
            # SITE G'S NAME FIRST. See the docstring: the fact pass has already
            # asked this file its fields under that schema, so any other branch
            # would judge it on answers to questions it was never put.
            reached = {named_of[file_id]}
        elif file_id in anchored_to:
            reached = {anchored_to[file_id]}
        else:
            reached = {schema_id for schema_id in schemas
                       if any(field in own_fields[schema_id]
                              for field, _value in facts[file_id])}
            if not reached:
                reached = _named_by(verdict_of(file_id, content_hash)) & set(schemas)
        if len(reached) == 1:
            under[next(iter(reached))].append(file_id)
        elif not reached:
            under[default_schema].append(file_id)
        else:
            held.append(file_id)

    branches: list[Branch] = []
    for schema_id in schemas:
        if schema_id == default_schema:
            situation, candidates = _default()
            branches.append(Branch(
                label=default_label, schema=schema_id,
                display_name=default_display_name or default_label,
                situation=situation, is_default=True,
                anchor_file_ids=tuple(anchors_of.get(schema_id, ())),
                file_ids=tuple(under[schema_id]),
                candidate_situations=candidates))
            continue
        situation, candidates = _situation_for(schema_id, schema_id)
        if situation is None:
            # THE JUDGE'S OWN ANSWER, where it gave one for every file here
            # (`00` amendment 1 of 14 Sep). Third in the order and not first:
            # the person's answer and the library's single situation both still
            # outrank it, which is `104` §17.9's standing rule that the model's
            # answer is a refinement of the person's and never a replacement.
            situation = _settled_by_the_judge(under[schema_id], candidates)
            if situation is not None:
                candidates = ()
        # A BRANCH SITE G OPENED IS SETTLED BY THE SAME RULE AS EVERY OTHER, and
        # `situations_of(schema_id)[0]` used to stand here for it. The argument
        # was that G naming a schema is "a model choosing from valid options" --
        # but G chose a SCHEMA, and which of that schema's situations the branch
        # is was never put to anybody. On the shipped release that took the
        # alphabetically first of eight for `research` and of eighteen for
        # `finance`. So the branch is unsettled like any other, its question is
        # recorded, and the person answers it.
        branches.append(Branch(
            # **THE LABEL IS THE SCOPE KEY AND IS NOT A DISPLAY STRING.**
            # `Branch.scope` is `f"{SCOPE_BRANCH}:{self.label}"`, which is what
            # records this branch's question, what `--answer situation:academic=`
            # matches on, and what every stored answer in an existing database is
            # keyed by. The lead changed it to the authored name on 18 Sep and
            # broke the question-and-answer round trip across sixteen integration
            # tests: a person's typed gesture stopped matching the scope it was
            # recorded at. It stays the id. `display_name` beside it is what a
            # FOLDER is called.
            label=schema_id,
            display_name=folder_name_for_schema(
                name_of_schema(schema_id), schema_id),
            schema=schema_id, situation=situation,
            is_default=False,
            anchor_file_ids=tuple(anchors_of.get(schema_id, ())),
            file_ids=tuple(under[schema_id]),
            candidate_situations=candidates))
    return BranchPartition(branches=tuple(branches), held=tuple(held))


def branch_votes(named: "dict[str, str]", partition: "BranchPartition",
                 ) -> dict[str, str]:
    """`00` Amendments of 2026-09-11 item 2: a branch's situation from site G's
    evidence. For each branch, the schema the model named most often over its
    files; a tie names nothing, a branch with no named file names nothing. A file
    the model could not place inherits this for its fact pass, so a club flyer the
    judge called "none" is asked a club's questions when its folder is a club's.
    """
    votes: dict[str, str] = {}
    for branch in partition.branches:
        tally: dict[str, int] = {}
        for file_id in branch.file_ids:
            schema = named.get(file_id)
            if schema:
                tally[schema] = tally.get(schema, 0) + 1
        if not tally:
            continue
        top = max(tally.values())
        leaders = [schema for schema, n in tally.items() if n == top]
        if len(leaders) == 1:
            votes[branch.label] = leaders[0]
    return votes

