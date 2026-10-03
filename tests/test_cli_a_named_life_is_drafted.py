# tests/test_cli_a_named_life_is_drafted.py
"""A life branch the judge opened is drafted even when P9 formed no group.

Measured on a 33-file Desktop: the partition opened seven life branches from
site G's named situations, P9 formed no group (loose files carry no direct or
validated fact to seed one), `draft_for_review` returned `()`, and the proposed
tree held no branch at all -- 0 of 32 loose files had a folder to go to.

`00` amendment 12 (planning/00:352) puts a life at the top level wherever the
person's files put it, and the 9-10 Sep amendment makes the model the decision
engine; the branch's files are what the judge named, so they are its draft.
"""
from __future__ import annotations

import sqlite3

import cli
from branch_situation import Branch
from grouping.schema import create_grouping_schema
from grouping.store import current_group, memberships_for_group
from grouping.vocabulary import COMPATIBLE_DOCUMENT_TYPE, CONTEXT_SUPPORTED, LLM


def _conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    create_grouping_schema(conn)
    return conn


def _branch(label, files, kinds, *, default=False, schemas=()):
    return Branch(label=label, life=None if default else label,
                  schemas=tuple(schemas), situations=(), situation=None,
                  is_default=default, anchor_file_ids=(), file_ids=tuple(files),
                  display_name=label,
                  kinds_by_file=tuple((f, k) for f, k in kinds.items()))


def _no_group():
    from types import SimpleNamespace
    return SimpleNamespace(group=None, stop_rule_outcome=None)


def test_a_life_the_judge_named_is_drafted_with_no_p9_group():
    conn = _conn()
    default = _branch("career", (), {}, default=True, schemas=("career",))
    education = _branch("Education", ("f1", "f2", "f3"),
                        {"f1": "academic", "f2": "academic", "f3": "academic"},
                        schemas=("academic",))
    branches = (default, education)
    named = {"f1": ("h1", "sha256:o1"), "f2": ("h2", "sha256:o2")}  # f3: none
    told = []

    drafted = cli.draft_for_review(
        conn, [_no_group(), _no_group()], group_category="career",
        label="career", created_at="2026-10-03T00:00:00Z",
        branch_for=lambda f: education if f in education.file_ids else None,
        default_branch=default, on_accepted=lambda g, b: told.append((g, b.label)),
        schema_of_file=lambda f: None, branches=branches,
        situation_evidence_of=lambda f, _k: named.get(f))

    assert len(drafted) == 1
    group = current_group(conn, drafted[0])
    assert (group.display_label, group.group_category) == ("Education", "academic")
    members = memberships_for_group(conn, drafted[0])
    assert sorted(m.file_id for m in members) == ["f1", "f2"]
    for m in members:
        assert (m.basis, m.decision_source) == (CONTEXT_SUPPORTED, LLM)
        assert [s.support_kind for s in m.support] == [COMPATIBLE_DOCUMENT_TYPE]
        assert m.support[0].observation_key == named[m.file_id][1]
    assert told == [(drafted[0], "Education")]


def test_a_file_with_no_kind_the_library_holds_is_not_drafted():
    """A default-branch file no life reached carries no kind: nothing to draft
    it under, so it stays undrafted rather than wearing the folder's name."""
    conn = _conn()
    default = _branch("career", ("f9",), {}, default=True, schemas=("career",))
    drafted = cli.draft_for_review(
        conn, [_no_group()], group_category="career", label="career",
        created_at="2026-10-03T00:00:00Z", branch_for=lambda f: default,
        default_branch=default, schema_of_file=lambda f: None,
        branches=(default,), situation_evidence_of=lambda f, _k: {"f9": ("h", "sha256:o")}.get(f))
    assert drafted == ()


def test_the_situation_is_asked_under_the_kind_the_branch_put_the_file_under():
    """The person answers a KIND's question (`branch:<kind>`), so whether a file
    has a named situation is asked with the kind its branch holds it as."""
    conn = _conn()
    default = _branch("career", (), {}, default=True, schemas=("career",))
    photos = _branch("Photos and Media", ("p1", "p2"),
                     {"p1": "photos", "p2": "photos"}, schemas=("photos",))
    asked = []

    def evidence(file_id, kind):
        asked.append((file_id, kind))
        return ("h" + file_id, "sha256:" + file_id)

    drafted = cli.draft_for_review(
        conn, [_no_group()], group_category="career", label="career",
        created_at="2026-10-03T00:00:00Z",
        branch_for=lambda f: photos if f in photos.file_ids else None,
        default_branch=default, schema_of_file=lambda f: None,
        branches=(default, photos), situation_evidence_of=evidence)

    assert asked == [("p1", "photos"), ("p2", "photos")]
    assert len(drafted) == 1
