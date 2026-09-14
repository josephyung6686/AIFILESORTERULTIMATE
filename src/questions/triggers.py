# src/questions/triggers.py
"""Where a question comes from: a decision the evidence cannot settle.

`66` §14 is the rule this module implements, and it is a rule about WHEN, not
about what to ask:

> When the engine encounters a repeated ambiguity that prevents a useful template,
> group interpretation, or destination proposal, it asks a narrow, evidence-linked
> question. The question should name the visible context and the precise
> consequence.

So no question is written down anywhere. Each one is DERIVED from a specific
blocked decision in a specific run, and a run with nothing blocked asks nothing --
which is the difference between this and the "generic list of questions such as
'What do you do?'" that §12 rejects.

**The one trigger this deployment ships.** `recognition.detector` abstains with
`tied_schema_ids` when a file's own words support two readings equally, and `00`
requires that abstention because both readings really are supported by the
evidence. But a tie in the EVIDENCE is not a tie in the world: the file is one
thing, and the person knows which. That is §13's "resolves a user relationship or
policy fact that file evidence cannot safely determine", exactly.

The tied schemas become the options, so the question can only ever offer readings
the file's own words support. A product that offered more would be guessing on the
person's behalf about what their file might be; one that offered fewer would be
hiding a reading its own evidence produced.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from privacy.vocabulary import check_handling_class

from questions.records import QuestionOption, StructuralQuestion
from questions.registry import (
    HOME_KIND, NESTING_KIND, READING_KIND, ROLE_KIND, SITUATION_KIND, kind_of,
)
from questions.vocabulary import (
    SCOPE_BRANCH, SCOPE_FOLDER, SCOPE_ORGANIZATION, STRUCTURAL,
)

#: `66` §14 keeps these two answers first-class, so every derived question carries
#: them and no caller may drop them. "Not about me" is a real answer about whose
#: material this is; skipping is recorded separately as an answer STATE, because
#: a person who declines has told the product something and must not be asked
#: again next run.
NOT_ABOUT_ME = QuestionOption("not_mine", "It is not about me")

#: The promise §12 requires every question to make. This deployment can keep it
#: absolutely: it moves nothing at all, so no answer to any question can move
#: anything either.
WILL_NOT_DO: str = (
    "Answering will not move, rename or delete anything. It changes which "
    "folders this run is allowed to propose, and nothing else.")

#: §21's "data classifications", for the two kinds this deployment ships.
#:
#: Both questions quote something the person's own material produced -- a course
#: code, a matter number, a branch label they typed -- so neither is `public_low`.
#: Neither collects a person's NAME, a credential, or anything §8.4 puts in the
#: two classes above this one; a question that did (§15's household question is
#: the case) declares its own, higher class at its own builder rather than
#: inheriting this.
#:
#: This is a classification of what the QUESTION holds, and it is deliberately not
#: a classification of the files behind it: P7 has already classified those, and a
#: second opinion here would be a second spelling of the same fact.
SUBJECT_DRAWN_FROM_THE_CORPUS: str = check_handling_class(
    "personal_non_sensitive")


def _schema_words(schema_id: str) -> str:
    """A schema id in a person's words rather than the catalogue's.

    Underscores out, capitalised. Deliberately mechanical: inventing a friendly
    name per schema here would be this module authoring vocabulary that the
    template library owns, and a wrong friendly name is worse than a plain one.
    """
    return schema_id.replace("_", " ")


def question_for_tied_reading(*, subject_value: str, tied_schema_ids: Iterable[str],
                              file_count: int,
                              evidence_refs: Iterable[str]) -> StructuralQuestion:
    """One question, from one ambiguity the file's own words could not settle.

    `subject_value` is the identifier the group formed around -- a course code, a
    matter number -- so the question names something the person will recognise
    from their own files rather than an internal id.
    """
    tied = tuple(dict.fromkeys(tied_schema_ids))
    if len(tied) < 2:
        raise ValueError(
            "a question is asked where the evidence supports TWO readings; one "
            "reading is not an ambiguity and needs no question")
    files = "file mentions" if file_count == 1 else "files mention"
    return StructuralQuestion(
        question_id=f"{READING_KIND.kind_id}.{SCOPE_ORGANIZATION}:{subject_value}",
        answer_class=STRUCTURAL,
        prompt=f"What kind of material is {subject_value}?",
        evidence_context=(
            f"{file_count} {files} {subject_value}, and its own words support "
            f"{len(tied)} readings equally." if file_count == 1 else
            f"{file_count} {files} {subject_value}, and their own words support "
            f"{len(tied)} readings equally."),
        unlocks=(
            "This decides which folder layout is offered for these files. Until "
            "it is answered they stay where they are, unfiled."),
        will_not_do=WILL_NOT_DO,
        handling_class=SUBJECT_DRAWN_FROM_THE_CORPUS,
        scope=f"{SCOPE_ORGANIZATION}:{subject_value}",
        options=tuple(
            QuestionOption(schema_id, f"{_schema_words(schema_id)} material",
                           activates_schema=schema_id)
            for schema_id in tied) + (NOT_ABOUT_ME,),
        evidence_refs=tuple(dict.fromkeys(evidence_refs)))


def tied_readings(conn: sqlite3.Connection, *, explain,
                  files: Iterable[tuple[str, str]],
                  subject_of: Mapping[str, str],
                  ) -> tuple[StructuralQuestion, ...]:
    """Every question this corpus's own ambiguities raise, deduplicated by subject.

    `explain` is the detector's, injected rather than imported so this module has
    no opinion about which detector is running -- the same reason every other
    authority in this project arrives from the caller.

    Grouped by SUBJECT rather than by file, because §14 asks for a question on a
    "repeated ambiguity" and four files of one course tying the same way is one
    ambiguity, asked once. A person answering the same question four times would
    rightly conclude the product was not listening.
    """
    return tuple(question for question, _files
                 in tied_readings_and_the_files_they_reach(
                     conn, explain=explain, files=files, subject_of=subject_of))


def tied_readings_and_the_files_they_reach(
        conn: sqlite3.Connection, *, explain,
        files: Iterable[tuple[str, str]],
        subject_of: Mapping[str, str],
) -> tuple[tuple[StructuralQuestion, tuple[str, ...]], ...]:
    """The same questions, each with the files whose tie it would settle.

    `104` R-92. The report said "Would go into lecture, once you say what these
    are" over five files and offered no `--answer` that reached any of them: the
    two whose own words tied were reachable, and three whose words matched nothing
    were not, and one sentence covered all five. The screen cannot tell them apart
    without knowing which files each question is FOR, and that is the fact this
    loop already holds and used to throw away.

    WHICH FILES A READING QUESTION REACHES IS EXACTLY THE FILES IT WAS RAISED
    FROM, and it must be read here rather than re-derived from the subject alone.
    A file can carry a subject the question names and still be untouched by any
    answer to it -- `hw2_starter.py` sat under `CS3134` with no reading of its own
    -- so "the subject matches" would put the same broken promise back on the
    screen with a citation.

    The questions are the ones `tied_readings` returns, in the same order, so no
    caller can be shown a question this does not account for.
    """
    by_subject: dict[str, tuple[set[str], set[str], list[str]]] = {}
    for file_id, content_hash in files:
        subject = subject_of.get(file_id)
        if not subject:
            continue
        outcome = explain(conn, file_id, content_hash)
        tied = tuple(getattr(outcome, "tied_schema_ids", ()) or ())
        if len(tied) < 2:
            continue
        schemas, refs, reached = by_subject.setdefault(subject,
                                                       (set(), set(), []))
        schemas.update(tied)
        refs.update(getattr(outcome, "evidence_refs", ()) or ())
        if file_id not in reached:
            reached.append(file_id)
        by_subject[subject] = (schemas, refs, reached)

    out: list[tuple[StructuralQuestion, tuple[str, ...]]] = []
    for subject in sorted(by_subject):
        schemas, refs, reached = by_subject[subject]
        if len(schemas) < 2:
            continue
        out.append((question_for_tied_reading(
            subject_value=subject, tied_schema_ids=sorted(schemas),
            file_count=len(reached),
            # An abstention carries no evidence refs of its own, so the subject
            # value stands in as the citation: it IS the observed thing the
            # question is about, and §14 only requires the person be able to see
            # why the question arose.
            evidence_refs=tuple(refs) or (f"subject:{subject}",)),
            tuple(reached)))
    return tuple(out)


@dataclass(frozen=True)
class NestingChoice:
    """One shape a branch could take, as the person would see it.

    A projection of P10's `VerticalOption`, not that record: this module must not
    import P10, and what a question needs is the four things `00`:99 says the
    canvas shows -- what it would build, how many files land under each child, and
    what is wrong with it. `chain` is the composition's identity, ordered.
    """

    chain: tuple[str, ...]
    summary: str
    child_counts: tuple[tuple[str, int], ...]
    warnings: tuple[str, ...]

    @property
    def key(self) -> str:
        """The stable id, and the value an answer records.

        The CHAIN and never a position: `00`:99's options are built per run, so
        `opt_2` names a different shape the moment the corpus changes, and a
        person would get a tree they did not pick from an answer they did give.
        """
        return ">".join(self.chain)


def question_for_nesting(*, branch_label: str,
                         choices: Iterable[NestingChoice],
                         file_count: int,
                         waits_for_the_answer: bool = False,
                         ) -> StructuralQuestion:
    """`00`:78's own moment: the engine proposes shapes and the person picks one.

    §5.5 already builds these options and shows what each would create. The
    command then took `options[0]` and disclosed that it had -- "a person looking
    at the counts and warnings would reasonably pick another" -- which is honest
    and is not the same as asking. This asks.

    Structural, not contextual, and the records enforce it: the answer decides
    which folders the branch has, which §13 forbids a contextual answer to touch.

    `waits_for_the_answer` says which of two true things `unlocks` should say,
    and the caller is the only part that knows: the run either builds the first
    shape meanwhile or builds nothing inside the branch at all (`104` §18.42
    item 1, R-92). It defaults to `False` because that is what every caller
    written before the wait existed does, so the sentence they produce stays the
    sentence that is true of them.
    """
    offered = tuple(choices)
    if len(offered) < 2:
        raise ValueError(
            "a question is asked where the engine found TWO shapes the branch "
            "could take; one nesting is not a choice and needs no question")
    files = "file" if file_count == 1 else "files"
    return StructuralQuestion(
        question_id=f"{NESTING_KIND.kind_id}:{branch_label}",
        answer_class=STRUCTURAL,
        prompt=f"How should {branch_label} be organised?",
        evidence_context=(
            f"{file_count} {files} {'sits' if file_count == 1 else 'sit'} under "
            f"{branch_label}, and {'its' if file_count == 1 else 'their'} own facts "
            f"support {len(offered)} different shapes."),
        unlocks=(
            f"This decides the folders inside {branch_label}. No folder is built "
            "inside it until you answer, so the files that would go there wait "
            "with it."
            if waits_for_the_answer else
            f"This decides the folders inside {branch_label}. Until it is "
            "answered the first shape that passed every check is used, which may "
            "not be the one you would pick."),
        will_not_do=WILL_NOT_DO,
        handling_class=SUBJECT_DRAWN_FROM_THE_CORPUS,
        scope=f"{SCOPE_BRANCH}:{branch_label}",
        options=tuple(
            QuestionOption(choice.key, _nesting_label(choice),
                           gates_template=choice.key)
            for choice in offered),
        evidence_refs=(f"branch:{branch_label}",))


def _nesting_label(choice: NestingChoice) -> str:
    """What this shape would build, in the words `00`:99 asks for.

    The counts and the warnings are not decoration. The disclosure this question
    replaces said in as many words that "a person looking at the counts and
    warnings would reasonably pick another" -- so a question offering the shapes
    WITHOUT them would be strictly worse than the default it replaced, because it
    would move the decision to the person and keep the information here.
    """
    parts = [choice.summary]
    if choice.child_counts:
        inside = ", ".join(f"{name} ({count})" for name, count in choice.child_counts)
        parts.append(f"builds {inside}")
    for warning in choice.warnings:
        parts.append(f"warning: {warning}")
    return " -- ".join(parts)


def question_for_situation(*, branch_label: str, situations: Iterable[str],
                           file_count: int) -> StructuralQuestion:
    """§13's third consequence: the person says which of their lives a branch is.

    `--situation` takes ONE string for a whole disk and derives the schema from it.
    `68` F6 measured the cost on a real corpus: Priya's entire disk is
    `academic.coursework` "including the material that is `academic.teaching`, a
    situation the shipped library now carries". She is a graduate student who also
    teaches, and the command line made her choose which of her two lives to file.
    §16:543 says the same thing from the other end -- "being more than one thing is
    normal".

    So this asks per BRANCH, where the ambiguity actually is, and only when two
    situations the shipped library carries both fire on that branch's evidence.

    **The labels are the library's own names, verbatim.** Not a friendlier phrasing
    of them: `_schema_words` already records why this module does not invent
    vocabulary the template library owns, and `--list-situations` prints these exact
    strings, so they are what the person has already been shown.
    """
    offered = tuple(dict.fromkeys(situations))
    if len(offered) < 2:
        raise ValueError(
            "a question is asked where TWO situations both fire on one branch; "
            "one situation is an answer and not a question, and asking anyway "
            "would be the generic questionnaire §12 rejects, one branch at a time")
    files = "file" if file_count == 1 else "files"
    return StructuralQuestion(
        question_id=f"{SITUATION_KIND.kind_id}:{branch_label}",
        answer_class=STRUCTURAL,
        prompt=f"Which of these is {branch_label}?",
        evidence_context=(
            f"{file_count} {files} {'sits' if file_count == 1 else 'sit'} under "
            f"{branch_label}, and {'its' if file_count == 1 else 'their'} own facts "
            f"fit {len(offered)} of the situations this library carries equally."),
        unlocks=(
            f"This decides which templates {branch_label} is offered, and so which "
            "folders it can have. Until it is answered the situation you gave on "
            "the command line is used for this branch as well as the rest."),
        will_not_do=WILL_NOT_DO,
        scope=f"{SCOPE_BRANCH}:{branch_label}",
        handling_class=SUBJECT_DRAWN_FROM_THE_CORPUS,
        options=tuple(QuestionOption(situation, situation,
                                     selects_situation=situation)
                      for situation in offered),
        evidence_refs=(f"{SCOPE_BRANCH}:{branch_label}",))


@dataclass(frozen=True)
class DestinationChoice:
    """One folder the person could name, as they would see it.

    A projection of P10's index entry rather than that record, for `NestingChoice`'s
    reason: this module must not import P10, and what a question needs is the two
    things a person reads -- the id the answer records, and the path they recognise.
    """

    node_id: str
    display_path: str

    def __post_init__(self) -> None:
        for name in ("node_id", "display_path"):
            if not getattr(self, name):
                raise ValueError(f"a destination choice needs a {name}")


def question_for_unreadable_folder(*, folder: str,
                                   choices: Iterable[DestinationChoice],
                                   file_count: int,
                                   protected_count: int,
                                   shown_as: str | None = None) -> StructuralQuestion:
    """The product opened these and read nothing. Only the person knows what they are.

    **Why this is a question and 73% of a corpus going unplaced is not.** §12
    permits a question "only when a specific decision is blocked", and most unplaced
    files are not blocked on the person -- they are blocked on evidence the product
    has and has not yet used well. These are different: every text-producing
    extractor ran and recovered nothing, so there is no evidence to use better and
    no reading for the product to be wrong about. Measured against a hand-labelled
    corpus, 76% of the files this describes are ones a human labeller independently
    marked "the right answer is ask the person", against a 41% base rate.

    **Why the FOLDER and not the file.** §14 asks for a question on a "repeated
    ambiguity", and `tied_readings` above reads that as "four files of one course
    tying the same way is one ambiguity, asked once". Seven unreadable assets in one
    folder are one ambiguity for the same reason: a person who has to answer seven
    identical questions about one folder learns that nothing is listening.

    **`protected_count` is carried and the names are not.** §8.4 marks protected
    material so it is not assembled for anything, and `00`:201 says a visible list of
    protected specifics "may not be" safe to show. A protected file in this folder is
    therefore counted here and asked about nowhere -- but it is COUNTED, because
    dropping it silently would make the question claim the folder holds fewer files
    than it does, and "marked and counted, never opened, never silently omitted" is
    the whole rule rather than its first two thirds.
    """
    offered = tuple(choices)
    if len(offered) < 2:
        raise ValueError(
            "a question offers the person somewhere to choose BETWEEN; one "
            "destination is a placement wearing a question mark, and offering it "
            "as a choice would make the engine's own decision look like theirs")
    if file_count < 1:
        raise ValueError(
            "a question about no file is the profile interview §12 rejects, "
            "asked about a folder instead of about a person")
    files = "file" if file_count == 1 else "files"
    were = "was" if file_count == 1 else "were"
    them = "it" if file_count == 1 else "them"
    what = "what it is" if file_count == 1 else "what they are"
    # `folder` is the SCOPE -- relative to the scan root, so the folder the
    # person typed is `.` -- and it stays in the id and the scope because an
    # answer is stored against it. What the person READS is `shown_as` when the
    # caller has a better name: "Where should the files in . go?" was on a real
    # screen, and `.` names nothing to anyone.
    named = shown_as or folder
    held = ("" if not protected_count else
            f" {protected_count} more {'is' if protected_count == 1 else 'are'} "
            "protected material: counted here, not opened, and not named.")
    return StructuralQuestion(
        question_id=f"{HOME_KIND.kind_id}:{folder}",
        answer_class=STRUCTURAL,
        prompt=f"Where should the files in {named} go?",
        evidence_context=(
            f"{file_count} {files} in {named} {were} opened and nothing readable "
            f"came out of {them}, so nothing but you can say {what}.{held}"),
        unlocks=(
            f"This decides where that {file_count} {files} is filed. Until it is "
            f"answered {them} stays where {them} is, unfiled." if file_count == 1
            else
            f"This decides where those {file_count} {files} are filed. Until it is "
            "answered they stay where they are, unfiled."),
        # NOT `WILL_NOT_DO`, and this is the one place in the module where that
        # shared sentence would be a lie. It promises the answer "changes which
        # folders this run is allowed to propose, and nothing else" -- true of a
        # nesting, a situation and a reading, and false of this one, which changes
        # where a file goes and no folder at all. §12 requires a question to "state
        # what it will not affect", and a promise that names the wrong thing is
        # worse than none: it is the product being trusted about the wrong risk.
        will_not_do=(
            "Answering will not move, rename or delete anything, and creates no "
            "folder. It records where you want these filed, in a plan you still "
            "have to approve, and it can be changed by answering again."),
        handling_class=SUBJECT_DRAWN_FROM_THE_CORPUS,
        scope=f"{SCOPE_FOLDER}:{folder}",
        options=tuple(QuestionOption(choice.display_path, choice.display_path,
                                     chooses_destination=choice.display_path)
                      for choice in offered),
        evidence_refs=(f"{SCOPE_FOLDER}:{folder}",))


def role_declaration_is_due(*, blocked: Iterable[StructuralQuestion],
                            already_declared: Iterable[object]) -> bool:
    """`80` §3 (R1): WHEN the self-description question may be introduced.

    The brief this ruling answers assumed onboarding. The ruling rejects that:

    > A brand-new user doesn't yet trust the product enough to answer an identity
    > question about themselves. Seamless would mean: let the person run the tool
    > once, see it do something correct and small first, and ask the
    > self-description question only once there's evidence the product needs it --
    > i.e. precisely when it hits its first genuinely ambiguous file.

    So this is a moment, not a question. It returns a BOOL and mints nothing: no
    `declaration_id`, no `StructuralQuestion`, no answer. That is deliberate and it
    is the whole reason R1 can be satisfied without breaking §12. A run may now say
    *this is the moment*; only the person's own gesture may say *and here is who I
    am*, and `roles.py` is still reached from nowhere in this module.

    **The two conditions, and the second one is R2.**

    Due when at least one decision this run could not settle is open -- the first
    genuinely ambiguous file, in the same sense every other question in this module
    means it: raised from a finished run, never up front, and a run with nothing
    blocked asks nothing.

    NEVER due once the person has declared anything at all. `80` §4 (R2): "the
    friction budget is spent ONCE. Confirmation happens at the moment the roles are
    established. It does not recur per file."

    > If the design implies confirming every time the context gets used later ...
    > that becomes death by a thousand tiny interruptions, and a user will start
    > clicking through without reading, which defeats the entire safety rationale.

    A confirmed role therefore operates SILENTLY afterwards, and so does a skipped
    one -- `live_roles` returns a skipped declaration too, and §14 makes "skip for
    now" a first-class answer that §12 forbids re-asking. Changing a role later is
    R6's small localised edit through `roles.declare_role`, not this moment coming
    back around.

    `already_declared` is `roles.live_roles(conn)` and arrives injected, so nothing
    a run consults imports the role module. It is read as a presence and never
    counted, because one role and six roles are the same fact here: the person has
    been asked.

    A blocked ROLE question does not make itself due. It is already open; treating
    it as the ambiguity would be the moment triggering on its own consequence.

    **AN OFFER IS NOT AN AMBIGUITY**, and this was wrong here until the product was
    run. A first run over two coursework files raised no blocked reading at all --
    both came back "needed a model" -- and left one `00`:78 nesting offer open. The
    moment fired on it and told the person that the decisions above were waiting for
    them, when nothing was. `src/cli.py` already draws this line for its own report
    and records the reason: "A blocked reading STOPS something ... A nesting offer
    stops nothing -- the branch has a shape either way." So a branch-scoped question
    is settled, R1 puts the moment at "the first genuinely AMBIGUOUS file", and an
    offer is not one. Discriminated on the scope kind, which already carries the
    distinction, rather than on a second list somebody has to keep in step.

    **AND NEITHER IS A FILE NOBODY COULD READ** (`104` R-39). A `home:` question is
    raised when every text-producing extractor opened the files in one folder and
    recovered nothing from any of them -- `question_for_unreadable_folder` says so
    in its own evidence sentence: "nothing readable came out of them, so nothing
    but you can say what they are". A role is what a person IS, and R1 puts the
    moment at the first genuinely ambiguous file because knowing the person is a
    student narrows what an ambiguous file might be. It narrows nothing about a
    file with no words in it: the answer to a `home:` question is a destination,
    typed, and no declaration on any corpus could supply it.

    So the moment fired on the one question a role cannot help with, and told the
    person that the decisions above were waiting on a declaration that would
    unblock none of them -- the same defect the nesting offer had, one kind along.
    Discriminated on the KIND, beside `ROLE_KIND`, and not on the scope: `folder:`
    is `HOME_KIND`'s scope and a second kind could take it, which is the corner
    `branch` painted itself into and `SITUATION_KIND` had to climb out of.
    """
    if tuple(already_declared):
        return False
    return any(kind_of(question.question_id) not in (ROLE_KIND, HOME_KIND)
               and not question.scope.startswith(f"{SCOPE_BRANCH}:")
               for question in blocked)
