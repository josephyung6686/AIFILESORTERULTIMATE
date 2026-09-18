"""§8.8's node identity ACROSS RUNS -- SPEC open question 5, answered.

`store.py`'s docstring named the reversible move: "if node ids turn out to be
stable across versions, `origin_node_id` becomes `node_id` and nothing else
changes". This module is the other half. `node_id` is still minted per version;
`origin_node_id` is no longer the fresh mint's own id but the node's KEY, spelled
from what the node already carries. Two runs that build the same folder write
the same origin, and every reader that already compares versions by origin --
`diff.diff_versions`, `placement.versions.reproject`,
`placement.versions.learned_preferences_still_applicable`,
`store.apply_review_action` -- starts working across runs with no change.

WHAT A KEY IS MADE OF, and nothing else:
* a proposed top-level branch   `branch:` + the card's display label. Today that
  is the schema's name or the person's `--label`; under `106` Phase 3 it is the
  LIFE, which is the one moment this key changes and Phase 3 says so. It is the
  label and not the group ids because a group is re-drafted per run and a label
  is what the person recognises.
* an adopted existing folder    `existing:` + the observed path. Two folders
  with one name in two places are two folders.
* a level a value produced      the parent's key + `/` + `field=value`, the same
  pair `cli._node_claim` reads to say what a folder is NAMED BY.
* a template-local level        the parent's key + `/` + `role=label` -- it has
  no P6 field, so its role names it.
* a residual area               `residual:` + the template name.
* a protected area              `protected:` + the observed path.
* the scoped General            the parent's key + `/general`.

Path-shaped rather than `canonical_json`, deliberately: this string is what a
person may one day read beside a folder, and equality is all the readers need.
A `/` inside a value cannot make two different chains equal, because the field
name precedes every value and a field never contains one.

A DISPLAY STRING AND A PRIMARY KEY ARE NOT THE SAME THING even when they are
spelled the same (the lead's lesson of 18 Sep, on `Branch.label`). The key is
spelled from the node's CLAIM -- the observed path, the `field=value` pair --
and the one place a display label enters it, the proposed branch, is the place
where the label IS the claim: a proposal has nothing else it is named by.
"""
from __future__ import annotations

BRANCH_PREFIX: str = "branch:"
EXISTING_PREFIX: str = "existing:"
RESIDUAL_PREFIX: str = "residual:"
PROTECTED_PREFIX: str = "protected:"
GENERAL: str = "general"
SEPARATOR: str = "/"


def branch_key(*, display_label: str, existing_path: str | None) -> str:
    """A top-level card's key: the observed path for an adopted folder, the label
    for a proposal."""
    if existing_path is not None:
        return EXISTING_PREFIX + existing_path
    return BRANCH_PREFIX + display_label


def level_key(parent_key: str, *, field: str | None, value: str,
              role: str) -> str:
    """One level beneath `parent_key`, named by `field=value` -- or by
    `role=label` for a template-local level with no field."""
    return f"{parent_key}{SEPARATOR}{field if field is not None else role}={value}"


def residual_key(template_name: str) -> str:
    return RESIDUAL_PREFIX + template_name


def protected_key(path: str) -> str:
    """A protected area's key is the PATH the scan observed and never opened,
    on `existing:`'s rule: two areas with one basename in two places (`a/
    Library`, `b/Library`) are two areas, and a key on the label would refuse
    the whole design with `DuplicateNodeKey`."""
    return PROTECTED_PREFIX + path


def general_key(parent_key: str) -> str:
    return f"{parent_key}{SEPARATOR}{GENERAL}"


SHARED: str = "shared"


def shared_material_key(parent_key: str) -> str:
    """§6.9's shared branch under `parent_key`. Its own word and not
    `general_key`'s, because `store._write_overlap_answer` writes BOTH roles
    under one parent and two nodes under one key is what `DuplicateNodeKey`
    refuses -- measured on the p10 chain, 35 of 45 reds before this existed."""
    return f"{parent_key}{SEPARATOR}{SHARED}"
