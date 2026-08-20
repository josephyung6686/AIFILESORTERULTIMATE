# tests/p3/test_p3_protected_container.py
"""Joseph's ratified rule, 2026-08-20: applications and system items are never read,
never moved, and no gesture makes them movable.

Until now the rule lived only in P3's SPEC and `11-ops-runtime.md` §4b. `exclusion.py`
shipped three rules and not this one, so `SafetyPolicy.is_protected_container` — which
P5's gate calls before every extraction — had no P3 implementation to inject. The gate
passed its tests against a fixture predicate and protected nothing on a real disk.
"""
from pathlib import Path

import pytest

from scan_agent.exclusion import (
    LABEL_UNTOUCHED_PROTECTED, REASON_PROTECTED_CONTAINER, RULE_PROTECTED_CONTAINER,
    exclusion_for, is_protected_container,
)
from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.traversal import walk


def test_an_app_bundle_is_a_protected_container(tmp_path):
    """`.app` is the one literal the design spells (P3 SPEC Q7)."""
    app = tmp_path / "Numbers.app"; app.mkdir()
    verdict = exclusion_for(app, is_dir=True, applies_to="scanned source")
    assert verdict is not None
    assert verdict.rule == RULE_PROTECTED_CONTAINER
    assert verdict.rule_subject == REASON_PROTECTED_CONTAINER


def test_the_verdict_names_the_container_and_nothing_inside_it(tmp_path):
    """§4b: the record is the container. Anything else would require the read the
    rule forbids — a count of its files is already a fact learned by descending."""
    app = tmp_path / "Numbers.app"; (app / "Contents" / "MacOS").mkdir(parents=True)
    (app / "Contents" / "MacOS" / "secret.dylib").write_bytes(b"x")
    verdict = exclusion_for(app, is_dir=True, applies_to="scanned source")
    assert verdict.path == str(app)
    assert "secret" not in str(verdict)
    assert "Contents" not in str(verdict)


def test_traversal_does_not_descend_into_one(tmp_path):
    """"P3 does not descend into one, does not stat its contents" — so nothing inside
    is ever yielded, and no `files` row can exist for it."""
    app = tmp_path / "Mail.app"; (app / "Contents").mkdir(parents=True)
    (app / "Contents" / "inside.txt").write_text("never read")
    (tmp_path / "essay.txt").write_text("a real document")
    seen = [str(getattr(item, "path", ""))
            for item in walk(FilesystemCorpusSource(), sources=[tmp_path],
                             candidate_roots=[], budget_exhausted=lambda: False)]
    assert any("essay.txt" in s for s in seen)
    assert not any("inside.txt" in s for s in seen), "descended into a protected container"


def test_the_label_is_the_products_restraint_not_a_property_of_the_file(tmp_path):
    assert LABEL_UNTOUCHED_PROTECTED == "untouched_protected"
    assert REASON_PROTECTED_CONTAINER == "protected_container"


def test_a_caller_may_add_system_locations_but_none_is_invented(tmp_path):
    """The design names `.app` and the CATEGORY "system location", with no members.
    P3 implements the literal and holds the category as a caller-supplied predicate —
    inventing `/System`, `/Library`, `/usr` here would be a gazetteer P3 may not author."""
    lib = tmp_path / "PrivateFrameworks"; lib.mkdir()
    assert exclusion_for(lib, is_dir=True, applies_to="scanned source") is None
    # `Library` would NOT work here: it is already one of §1.1's eleven literals,
    # which this test discovered by failing. Two rules, one directory.
    assert is_protected_container(lib) is False
    assert is_protected_container(lib, extra=lambda p: p.name == "PrivateFrameworks") is True


def test_there_is_no_override(tmp_path):
    """What separates this from every other refusal: no policy, approval, or user
    gesture makes it movable. A keyword that disabled it would be that gesture."""
    import inspect
    params = set(inspect.signature(exclusion_for).parameters)
    assert not params & {"allow_protected", "override", "force", "include_protected"}


def test_anything_INSIDE_a_protected_container_is_protected_too(tmp_path):
    """The bug my container-only test missed, found by wiring P5's gate to this rule
    and watching it admit `Numbers.app/Contents/sheet.numbers`.

    §4b: P3 "does not create a `files` row for anything inside it." The unit of
    protection is the SUBTREE, not the directory entry. Checking only the path's own
    suffix protects the bundle and admits every file in it — which is the read the
    rule exists to prevent, passing every test that only ever asked about the bundle.
    """
    inside = tmp_path / "Numbers.app" / "Contents" / "Resources" / "sheet.numbers"
    inside.parent.mkdir(parents=True); inside.write_text("never read")
    assert is_protected_container(inside) is True
    assert is_protected_container(tmp_path / "Numbers.app" / "Contents") is True
    assert is_protected_container(tmp_path / "essay.pdf") is False


def test_the_extra_predicate_also_protects_a_whole_subtree(tmp_path):
    deep = tmp_path / "PrivateFrameworks" / "a" / "b.dylib"
    deep.parent.mkdir(parents=True)
    extra = lambda p: p.name == "PrivateFrameworks"
    assert is_protected_container(deep, extra=extra) is True
