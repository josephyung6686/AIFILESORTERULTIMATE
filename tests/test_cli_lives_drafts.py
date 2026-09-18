# tests/test_cli_lives_drafts.py
"""`00` amendment 12: a life spanning two schemas is drafted as two groups,
both labelled with the life, so `routing.eligible_rows` -- which admits a row
only for a domain the branch's groups carry -- can compose per coverage.

Driven through `_grouped_by_branch` with its one store read patched, as
`tests/test_branch_situation.py` drives the partition: the bucketing rule is
what is pinned, and a corpus would pin the screen instead.
"""
from __future__ import annotations

from types import SimpleNamespace

import cli
from branch_situation import Branch


def _branch(label, life, schemas, files, default=False):
    return Branch(label=label, life=life, schemas=tuple(schemas), situations=(),
                  situation=None, is_default=default, anchor_file_ids=(),
                  file_ids=tuple(files))


def _result(group_id):
    return SimpleNamespace(group=SimpleNamespace(group_id=group_id),
                           stop_rule_outcome=None)


def _members(table):
    return lambda conn, group_id: [SimpleNamespace(file_id=f) for f in table[group_id]]


def test_a_life_holding_two_schemas_yields_two_buckets_wearing_one_label(monkeypatch):
    """SABOTAGE: bucket by `branch.label` alone, category `branch.schemas[0]`.
    One draft, category `academic`; the packet's `college_applications` rows are
    never eligible and the application files sit at Education's root with no
    levels."""
    education = _branch("Education", "Education", ("academic", "college_applications"),
                        ("n1", "n2", "p1"))
    default = _branch("Downloads", None, ("academic",), (), default=True)
    monkeypatch.setattr(cli, "memberships_for_group",
                        _members({"g_notes": ["n1", "n2"], "g_packet": ["p1"]}))
    schema_of = {"n1": "academic", "n2": "academic", "p1": "college_applications"}

    buckets = cli._grouped_by_branch(
        None, [_result("g_notes"), _result("g_packet")],
        branch_for=lambda f: education, default=default,
        schema_of_file=schema_of.get)

    assert [(label, category, [r.group.group_id for r in bucket])
            for _branch_, category, label, bucket in buckets] == [
        ("Education", "academic", ["g_notes"]),
        ("Education", "college_applications", ["g_packet"])]


def test_a_group_whose_members_span_two_schemas_is_the_defaults(monkeypatch):
    """A tie decides nothing -- `_grouped_by_branch`'s own rule for branches,
    applied to the category. SABOTAGE: majority. This module picks a kind."""
    education = _branch("Education", "Education", ("academic", "college_applications"),
                        ("n1", "p1"))
    default = _branch("Downloads", None, ("academic",), (), default=True)
    monkeypatch.setattr(cli, "memberships_for_group", _members({"g_mixed": ["n1", "p1"]}))

    buckets = cli._grouped_by_branch(
        None, [_result("g_mixed")], branch_for=lambda f: education,
        default=default, schema_of_file={"n1": "academic",
                                         "p1": "college_applications"}.get)

    assert [(label, category) for _b, category, label, _k in buckets] == [
        ("Downloads", "academic")]


def test_a_single_schema_branch_drafts_exactly_as_before(monkeypatch):
    """The r37 case: one kind, one draft, the category the branch carries --
    even when no member carries a situation fact at all (an offline run), so
    the category falls back to the branch's only schema."""
    coursework = _branch("Coursework", "Education", ("academic",), ("a", "b"), default=True)
    monkeypatch.setattr(cli, "memberships_for_group", _members({"g1": ["a", "b"]}))

    buckets = cli._grouped_by_branch(
        None, [_result("g1")], branch_for=lambda f: coursework,
        default=coursework, schema_of_file=lambda f: None)

    assert [(label, category) for _b, category, label, _k in buckets] == [
        ("Coursework", "academic")]


def test_the_drafts_label_is_the_branchs_folder_name(monkeypatch):
    """The third item is what the merged draft is CALLED, and it becomes a
    folder: the branch's `folder_name`, which for a life is the life and for
    the default is the person's `--label`."""
    career = Branch(label="Career", life="Career", schemas=("career",),
                    situations=(), situation=None, is_default=False,
                    anchor_file_ids=(), file_ids=("cv",), display_name="Career")
    default = _branch("Coursework", "Education", ("academic",), (), default=True)
    monkeypatch.setattr(cli, "memberships_for_group", _members({"g": ["cv"]}))

    buckets = cli._grouped_by_branch(
        None, [_result("g")], branch_for=lambda f: career, default=default,
        schema_of_file=lambda f: "career")

    assert [(label, category) for _b, category, label, _k in buckets] == [
        ("Career", "career")]
