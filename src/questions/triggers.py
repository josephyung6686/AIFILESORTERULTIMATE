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

from questions.records import QuestionOption, StructuralQuestion
from questions.vocabulary import SCOPE_ORGANIZATION, STRUCTURAL

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
        question_id=f"reading.{SCOPE_ORGANIZATION}:{subject_value}",
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
    by_subject: dict[str, tuple[set[str], set[str], int]] = {}
    for file_id, content_hash in files:
        subject = subject_of.get(file_id)
        if not subject:
            continue
        outcome = explain(conn, file_id, content_hash)
        tied = tuple(getattr(outcome, "tied_schema_ids", ()) or ())
        if len(tied) < 2:
            continue
        schemas, refs, count = by_subject.setdefault(subject, (set(), set(), 0))
        schemas.update(tied)
        refs.update(getattr(outcome, "evidence_refs", ()) or ())
        by_subject[subject] = (schemas, refs, count + 1)

    out: list[StructuralQuestion] = []
    for subject in sorted(by_subject):
        schemas, refs, count = by_subject[subject]
        if len(schemas) < 2:
            continue
        out.append(question_for_tied_reading(
            subject_value=subject, tied_schema_ids=sorted(schemas),
            file_count=count,
            # An abstention carries no evidence refs of its own, so the subject
            # value stands in as the citation: it IS the observed thing the
            # question is about, and §14 only requires the person be able to see
            # why the question arose.
            evidence_refs=tuple(refs) or (f"subject:{subject}",)))
    return tuple(out)
