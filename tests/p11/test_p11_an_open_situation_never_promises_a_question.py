# tests/p11/test_p11_an_open_situation_never_promises_a_question.py
"""The `situation_unanswered` sentence names a door that always exists.

It said "The question for its branch is printed below" for every such file, and
on a 33-file Desktop no question was recorded for the branch at all: the screen
promised a question that did not exist (`104` §18.3: a false sentence in front
of the person is the worst defect there is). `--situation-of` is the person's
own word about one file (`106` Phase 5.4) and always exists; a question about
the file's kind is mentioned only as something this run may have printed.
"""
from __future__ import annotations

from types import SimpleNamespace

from placement.pipeline import _abstention_explanation
from placement.vocabulary import SITUATION_UNANSWERED

#: An ordinary file: the protected arm answers before the reason is read.
ORDINARY = SimpleNamespace(privacy=SimpleNamespace(protected=False))


def test_the_sentence_does_not_claim_a_question_was_printed():
    said = _abstention_explanation(ORDINARY, reason=SITUATION_UNANSWERED)
    assert "is printed below" not in said
    assert "--situation-of" in said
