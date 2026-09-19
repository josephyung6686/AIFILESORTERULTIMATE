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

**A branch is a LIFE, not a kind** (`00` amendment 12 with 12a, 17 Sep 2026).
The signals above still decide which KIND each file is; the branch it is under
is the LIFE the library places that file's situation in (`production.life_of`,
read off the applicability row exactly as the folder levels are), and a branch
exists only for a life some file reached -- the sixteen the owner ratified are a
menu and never a skeleton. `partition_by_branch`'s docstring spells the five
arms that give a file its life and the one rule that keeps a typed run's own
life at home.

**A branch's situation.** The default branch's is the one the person typed --
and when they typed none (the owner's ruling of 11 Sep 2026; `--situation` is
optional) it is settled by exactly the rule below, because a branch the corpus
named is no more the person's answer than a branch its anchors opened: the
person's own answer to the per-branch question
`questions.triggers.question_for_situation` -- the trigger R-37 says was
registered and never fired, read back through `questions.store.selected_situation`
at scope `branch:<label>`, and at `branch:<kind>` where an earlier run labelled
the branch with its kind -- or, when the library carries exactly one situation for
that schema, that one. Otherwise it is UNSETTLED: the question is recorded, its
files are asked nothing until it is answered, and the branch is still proposed so
the person sees where those files would go. A LIFE branch is settled when every
file under it resolves to one situation -- the person's answer for the file's
kind (at `branch:<kind>`, the scope its question is recorded at), the judge's
fact, or the library's one situation for the kind -- and is otherwise
unsettled. Holding ONE kind, it asks that kind's question under the life's
name; holding two, or files already carrying two situations, it asks nothing:
"which situation is Education?" is not a question when Education holds
coursework and a thesis.
This module chooses no situation on the person's behalf: `104` §11.2 step 4's
ruling is that the person, or a model from valid options, decides, never a rule
picking the first of twenty-six.

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
#: `106` Phase 6.2 added the two other type keys: a `validated` `artifact_type`
#: is declared by five schemas and `record_type` by seven, and a what-kind fact
#: must not hold one file between four branches.
BRIDGES_THAT_DO_NOT_REACH: frozenset[str] = frozenset(
    {"work_type", "artifact_type", "record_type", "term"})

#: The scope a per-branch situation question is asked at, `questions.vocabulary.
#: SCOPE_BRANCH`'s word. Spelled here for the same reason as the set above; the
#: registry test asserts the two agree.
SCOPE_BRANCH: str = "branch"


@dataclass(frozen=True)
class Branch:
    """One proposed top-level branch: a LIFE the corpus put files under, or the
    folder's own default branch."""

    label: str
    #: `00` amendment 12: the life this branch IS, read off the library rows of
    #: its files' situations. `None` only for a default branch whose situation
    #: nothing has settled. It is the partition KEY and, for a life branch, the
    #: label; a situation is never one (amendment 9).
    life: str | None
    #: Every kind its files belong to, first-seen order. PLURAL since amendment
    #: 12: Education holds `academic.coursework` beside
    #: `applications.undergraduate-packet`, and those are two schemas.
    #: `cli._grouped_by_branch` drafts one group per member of this tuple. The
    #: default branch's own kind is always first.
    schemas: tuple[str, ...]
    #: The situations its files' `situation` facts carry, distinct, first-seen
    #: order. Empty on the partition that runs before the judge.
    situations: tuple[str, ...]
    #: `None` while unsettled. A life branch is settled only when every file
    #: under it resolves to one situation (`_settled_by_its_files`: the
    #: person's answer for the file's kind, the judge's fact, or the library's
    #: one); the default branch by the rule `_situation_for` spells.
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
        # THE LABEL IS AN IDENTITY -- the question scope, the draft bucket, the
        # vote key -- so two branches wearing one label would be one branch to
        # every reader and two to this one. It happens when a folder scanned
        # untyped is named exactly as a life its files reach; the person types
        # `--label` and the refusal says so.
        labels = [branch.label for branch in self.branches]
        repeated = sorted({label for label in labels if labels.count(label) > 1})
        if repeated:
            raise ValueError(
                f"two branches wear one label {repeated}: the folder is named as "
                "a life its files belong to, so name it with --label")
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
        life_of: Callable[[str], str | None],
        life_of_kind: Callable[[str], str | None],
        situation_fact_of: Callable[[str], str | None],
        alternatives_of: Callable[[str], Sequence[str]],
        name_of_schema: Callable[[str], str | None] = lambda _schema: None,
        default_display_name: str | None = None,
) -> BranchPartition:
    """The run's branches, from the deterministic signals it already holds.

    **THE TOP LEVEL IS A LIFE, NOT A KIND** (`00` amendment 12, with 12a). Every
    line up to `under` still decides which KIND each file is -- G's name first,
    then the anchor, then the schema's own field, then the recogniser's reading.
    What changes is the last step: kinds are folded into LIVES before branches
    are built, `life_of(situation)` being the library's own word for the life a
    situation is part of. A branch exists only for a life some file reached
    (12a(i)); the sixteen are a menu and never a skeleton.

    `life_of` is `production.life_of` bound to the catalogue and `life_of_kind`
    is `production.life_of_kind`; `situation_fact_of(file_id)` is the file's
    `situation` fact as a reader sees it (a `user_confirmed` row wins);
    `alternatives_of(file_id)` is its live `situation_alternative` values, read
    as a set because the store keeps no rank. `name_of_schema` has had no
    reader since amendment 12 -- no branch is opened for a schema any more --
    and is accepted so the binding site is unchanged; `default_display_name`
    still names the default branch's folder.

    **The life of one file, four arms, none of them a pick:**

    0. THE PERSON'S OWN ANSWER FOR THE FILE'S KIND -- the word they typed when
       the kind is the run's own, else their answer at `branch:<kind>`, the scope
       a kind's question was recorded at while a kind was a branch. Read first
       because `104` §17.9 is not negotiable: the model's answer refines the
       person's and never replaces it, and an answer given across runs 13-23
       must keep reaching the files it was always about.
    1. The `situation` fact -- the judge's first choice.
    2. Failing that, the alternatives: exactly one distinct life among them is
       that life; two is nothing. The tie-break, order-free.
    3. Failing that, THE LIBRARY'S OWN WORD FOR THE KIND (`life_of_kind`): a
       kind belongs to a life just as its situations do, and `academic` is
       Education whether or not anyone has said which coursework it is. This
       is the arm the owner's corpus mostly takes (`104` §18.108: the kind
       pass wrote the schema id and the level pass has mostly not refined
       it), and it is EXPLICIT library data, never the rows' or the corpus's
       agreement -- which said nothing for `academic` and left 218 of 257
       files in no life.
    4. Otherwise the file has no life, and it is the default branch's (R-140).

    **A typed run keeps its own KIND at home.** With `--situation` typed a file
    of the typed situation's life whose kind is the run's own (or none) stays
    in the default branch, under the label they typed -- the byte pin. A file
    of that life but of ANOTHER kind is under its life beside the typed
    branch (`_stays_home` says why). With nothing typed the top level is lives
    and the default branch holds only the residue: files with no life.

    **Single-ness is decided AFTER the fold.** One kind spans several lives
    (Priya's `academic` folder is Education and Teaching), so there is no early
    return on one kind; `BranchPartition.single` is true exactly when the fold
    yielded no life branch.

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

    **THE JUDGE'S SECOND ANSWER PER FILE** (`00` amendment 1 of 14 Sep) -- the
    SITUATION each file is part of -- arrives as the FACT it wrote,
    `situation_fact_of`, and not as the pass object it used to
    (`situations_named_by_the_model`, retired with `106` Phase 3): the fact is
    the same answer written down, it carries the person's `user_confirmed`
    override, and it is what every other reader of the sort reads (`00`
    amendment 11). It settles a life branch the judge answered for -- see
    `_settled_by_its_files` -- and it opens no KIND: a situation is what a file's
    life is read off, not a branch of its own.

    **`default_situation` IS `None` WHEN THE PERSON TYPED NO `--situation`**, on
    the owner's ruling of 11 Sep 2026 (`00` Amendments of 2026-09-11 item 2). The
    default branch is then settled by the person's answer at ITS OWN scope and
    by nothing else (`00` amendment 25) -- see `_situation_for`.
    """
    def _situation_for(schema_id: str,
                       branch_label: str) -> tuple[str | None, tuple[str, ...]]:
        """The UNTYPED default's situation, and the menu when it has none.

        **`00` AMENDMENT 25: AN UNJUDGED FILE STAYS VISIBLY UNJUDGED.** On an
        untyped run `schema_id` is the corpus's MAJORITY KIND
        (`cli._the_corpus_names_a_schema`) and the files under the default are
        the ones no life could be read for -- unreached by any anchor or
        G-named branch, no judge fact, no agreeing alternative. Nothing has
        said what they are. Until `104` §18.114 this read the person's answer
        at the kind's own scope too (`branch:<schema_id>`, on §17.9's "never
        dropped for a rename"), and then the library's one situation for the
        kind -- and 113 of the owner's 371 files were filed `career.recruiting`
        on an answer given for OTHER files. Both arms were a third voice: §17.9
        orders the person above the model and the model above silence and
        licenses no other. So:

        THE PERSON'S ANSWER AT THIS BRANCH'S OWN SCOPE, `branch:<branch_label>`,
        which is where `questions.triggers.question_for_situation` records the
        default's question -- their word about THIS folder's leftover files,
        and it stands. The kind's answer still reaches the kind's files through
        `_persons_answer_for`; it no longer reaches these. `None` otherwise,
        with the menu the question offers: the kind's situations, when there
        are two or more (one is not a question, `question_for_situation`
        refuses it). The menu is the majority kind's because the question needs
        a menu the answer can match (`questions.store.selected_situation`), and
        the screen says so rather than claiming the files' facts fit it.

        Checked against the kind's list as before: an answer naming a situation
        the library has since retired settles nothing rather than crashing the
        run where the promoted situation is read (`cli._the_situation_of_a_run`).
        """
        candidates = tuple(dict.fromkeys(situations_of(schema_id)))
        chosen = chosen_situation(f"{SCOPE_BRANCH}:{branch_label}")
        if chosen is not None and chosen in candidates:
            return chosen, ()
        return None, (candidates if len(candidates) >= 2 else ())

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
    # No early return on one kind: one kind spans several lives (see the
    # docstring), so the reach runs over every file and the fold below decides.

    # The fields that carry a file into each branch: the schema's own, less the
    # two bridges.
    own_fields = {
        schema_id: set(fields_of_schema(schema_id)) - BRIDGES_THAT_DO_NOT_REACH
        for schema_id in schemas}

    under: dict[str, list[str]] = {schema_id: [] for schema_id in schemas}
    held: list[str] = []
    #: Files NO branch reached. R-140 puts them in the default bucket, and that
    #: bucket's kind is not evidence about the file, so the fold reads no kind
    #: for them.
    fell_through: set[str] = set()
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
            fell_through.add(file_id)
        else:
            held.append(file_id)

    default_situation_settled, default_candidates = _default()
    default_life = (None if default_situation_settled is None
                    else life_of(default_situation_settled))
    #: The person's own word for the folder keeps its life at home; with nothing
    #: typed the top level is lives and the default holds the residue.
    typed = default_situation is not None

    def _persons_answer_for(kind: str) -> str | None:
        """Arm 0: the situation the PERSON has said files of this kind are.

        The typed word for the run's own kind, exactly as `cli._the_situation_
        already_settled` reads it; else their answer at the kind's own scope,
        for the default's kind as for every other. NOT the default branch's
        settled situation (`00` amendment 25): on an untyped run that is the
        person's word about the folder's leftover files, and this is their
        word about files of a KIND -- two answers, and each reaches only what
        it was given for. Where no `--label` was typed the default's label IS
        the kind, so the two scopes are one key and one answer serves both.
        Checked against the library's list for `_situation_for`'s reason.
        """
        if kind == default_schema and typed:
            return default_situation
        chosen = chosen_situation(f"{SCOPE_BRANCH}:{kind}")
        return chosen if chosen in situations_of(kind) else None

    def _first_arm_life(file_id: str) -> str | None:
        fact = situation_fact_of(file_id)
        return None if fact is None else life_of(fact)

    def _of_this_life(kind: str, life: str) -> tuple[str, ...]:
        """The kind's situations that ARE this life, in the library's order."""
        return tuple(dict.fromkeys(
            s for s in situations_of(kind) if life_of(s) == life))

    def _resolved_situation(file_id: str, kind: str | None,
                            life: str) -> str | None:
        """WHICH SITUATION THIS FILE IS, in `cli._the_situation_this_file_is_
        under`'s own order: the person's answer for its kind, else the judge's
        fact, else the library's one situation for the kind -- of which the
        one situation the kind has IN THIS LIFE is the same arm read one level
        down: an academic file under Education is the one Education situation
        academic has, if it has exactly one. `None` otherwise; never a pick."""
        if kind is not None:
            answered = _persons_answer_for(kind)
            if answered is not None:
                return answered
        fact = situation_fact_of(file_id)
        if fact is not None:
            return fact
        if kind is not None:
            one = the_one_situation(kind, situations_of=situations_of)
            if one is not None:
                return one
            in_life = _of_this_life(kind, life)
            if len(in_life) == 1:
                return in_life[0]
        return None

    def _settled_by_its_files(life: str, file_ids: Sequence[str]) -> str | None:
        """The one situation EVERY file of this life branch resolves to.

        `00` amendment 1 of 14 Sep: the judge names the situation and "the person
        is asked only where the judge cannot", so a branch answered for is a
        branch with nothing left to ask about -- its files are asked their own
        situation's fields and its folders are built. The person's answer for a
        file's kind and the library's one situation for it are answers of the
        same standing (`the_one_situation`'s first arm: an answer, not a choice).

        UNANIMOUS, AND OVER EVERY FILE RATHER THAN EVERY ANSWERED FILE. One file
        nothing resolves is one file whose situation is still open, and two
        situations under one branch is a branch that is not one piece of work;
        picking the majority would be this module choosing a situation on the
        person's behalf, which `104` §11.2 step 4 forbids.

        CHECKED AGAINST THE LIFE, so a stale fact replayed out of an earlier
        run's records cannot settle a branch on a situation of another life.
        """
        if not file_ids:
            return None
        resolved = {_resolved_situation(file_id, kind_of[file_id], life)
                    for file_id in file_ids}
        if len(resolved) != 1:
            return None
        one = next(iter(resolved))
        return one if one is not None and life_of(one) == life else None

    def _asked_of_a_life(life: str, kinds: Sequence[str],
                         carried: Sequence[str]) -> tuple[str, ...]:
        """WHAT AN UNSETTLED LIFE BRANCH ASKS THE PERSON, or nothing.

        `00` amendment 1 of 14 Sep: the person is asked only where the judge
        cannot -- and IS asked there. A branch of ONE kind whose files carry at
        most one situation is that kind's question under the life's name
        ("which of these is Career?"), offered the kind's situations that are
        this life; `cli._ask_which_situation_each_branch_is` records it at the
        KIND's scope, so the answer is read where every reader of the person's
        answer already reads it (arm 0). A branch of two kinds, or whose files
        already carry two situations, is not one piece of work and has no
        question; the router is handed what its files carry instead. Fewer
        than two options is not a question either (`question_for_situation`).
        """
        if len(kinds) != 1 or len(carried) > 1:
            return ()
        offered = _of_this_life(kinds[0], life)
        return offered if len(offered) >= 2 else ()

    #: file -> the KIND the reach put it under; `None` for a file no branch
    #: reached.
    kind_of: dict[str, str | None] = {
        file_id: (None if file_id in fell_through else schema_id)
        for schema_id, files in under.items() for file_id in files}

    def _life_of_file(file_id: str, kind: str | None) -> str | None:
        """Four arms, none a pick. See the docstring's 'The life of one file'."""
        if kind is not None:
            answered = _persons_answer_for(kind)
            if answered is not None and life_of(answered) is not None:
                return life_of(answered)
        first = _first_arm_life(file_id)
        if first is not None:
            return first
        named = {life_of(a) for a in alternatives_of(file_id)} - {None}
        if len(named) == 1:
            return next(iter(named))
        if kind is None:
            return None
        return life_of_kind(kind)

    def _stays_home(life: str | None, kind: str | None) -> bool:
        """Whether a file is the default branch's rather than its life's.

        A file with no life is (R-140). On a typed run, a file of the typed
        life whose KIND is the run's own -- or no kind at all -- is too: the
        typed word is a statement about the run's own kind of material, and
        `cli._the_situation_this_file_is_under` already treats a kind site G
        named that is not the run's as not covered by it. Such a file -- an
        application packet in a `--situation academic.coursework` folder -- is
        under its LIFE beside the typed branch, the root of its own it had
        before amendment 12: kept home, its group is drafted inside the typed
        branch in its own kind and P11 files an application essay into a
        course folder (R-23). The one exception is the person having typed the
        life itself as the folder's label: that word IS the life, and a second
        branch wearing it would be two branches with one key.
        """
        if life is None:
            return True
        if not typed or life != default_life:
            return False
        return kind in (None, default_schema) or life == default_label

    lives: dict[str, list[str]] = {}
    default_files: list[str] = []
    for file_id, _hash in roster:
        if file_id not in kind_of:
            continue  # held
        life = _life_of_file(file_id, kind_of[file_id])
        if _stays_home(life, kind_of[file_id]):
            default_files.append(file_id)
        else:
            lives.setdefault(life, []).append(file_id)

    def _situations_carried(file_ids: Sequence[str]) -> tuple[str, ...]:
        return tuple(dict.fromkeys(
            fact for fact in (situation_fact_of(f) for f in file_ids)
            if fact is not None))

    def _schemas_carried(file_ids: Sequence[str]) -> tuple[str, ...]:
        return tuple(dict.fromkeys(
            kind for kind in (kind_of[f] for f in file_ids) if kind is not None))

    branches: list[Branch] = [Branch(
        label=default_label, life=default_life,
        display_name=default_display_name or default_label,
        schemas=tuple(dict.fromkeys([default_schema, *_schemas_carried(default_files)])),
        situations=_situations_carried(default_files),
        situation=default_situation_settled, is_default=True,
        anchor_file_ids=tuple(anchors_of.get(default_schema, ())),
        file_ids=tuple(default_files),
        candidate_situations=default_candidates)]
    for life in sorted(lives):
        files = lives[life]
        carried = _situations_carried(files)
        kinds = _schemas_carried(files)
        # The person's answer reaches a life branch through its files' KINDS
        # (`_persons_answer_for`, read inside `_resolved_situation`): the
        # question is recorded at the kind's scope, and no reader looks for one
        # at `branch:<life>`.
        situation = _settled_by_its_files(life, files)
        branches.append(Branch(
            # THE LABEL IS THE SCOPE KEY, and for a life branch the life is the
            # only key it has: a life spanning two schemas has no schema id, and
            # the owner's word is the row's value verbatim (`106` §A). It is
            # also what the folder is called.
            label=life, life=life, display_name=life,
            schemas=kinds, situations=carried,
            situation=situation, is_default=False,
            anchor_file_ids=tuple(f for f in files if f in anchored_to),
            file_ids=tuple(files),
            candidate_situations=(() if situation is not None
                                  else _asked_of_a_life(life, kinds, carried))))
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

