# tools/groundtruth/ideal_tree.py
"""The ideal destination tree a key describes, and how far the product's tree is from it.

    python3 -m tools.groundtruth.ideal_tree --labels KEY [--database DB --corpus-root DIR] [--out FILE]

`104` §18.106: the owner's key grades one question -- which situation a file is --
and nothing past it, because `destination` is never deeper than two folders and
`expected_fields` is empty on every row. This module turns the same key into the
tree the design says a finished sort should build, so that every phase of `106`
that changes depth, branch naming or which facts exist has a number.

The tree is built from RULES, not drawn (`00` amendment 12a: a life appears only
where the person's own files put it; the sixteen are a menu, never a skeleton):

  * the root is the LIFE of the file's situation -- the key's situation, never the
    database's, because the situation is the one column the key is good at;
  * below it, the levels are `production.folder_levels_for(situation)` in the
    library's own order, filled from the key's `expected_fields`;
  * a level is built only where its values DIVIDE the branch (`materialise.py:95`:
    more than one distinct value, counted branch-wide), and then `106` Phase 7 §A's
    two bounds: no folder per file beneath a built node, and a run of single
    children that never divides folds into its top;
  * a file with no value at a built level rests at the parent (`00`:99's scoped
    General); a protected file is counted at the root and never given a path; an
    `uncertain` row is a deferred decision under `98 Review and Unsorted`
    (`00` amendment 13).

WHERE THE KEY IS BLANK, THIS SAYS SO AND NEVER GUESSES. A level the key has no
value for is reported as unfilled -- per level, per file -- and split into cells
that block depth today (the level is built and this file cannot descend it) and
cells that do not yet. Those blanks ARE the measurement `104` §18.106 asks for.
The key may say "no value applies" by writing the empty string: that is a
deliberate none, rests the file at the parent, and is not owed.

Nothing here reads a file of the owner's. Stdout carries counts and aggregates
only; per-file rows go to `--out` and nowhere else, and a `LabelError` -- whose
message names a path -- is reported by its rule, never its text.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, Mapping, Sequence

_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_ROOT), str(_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import production                                                   # noqa: E402
from facts.states import PROPOSAL_ELIGIBLE_STATES                   # noqa: E402
from facts.supersede import preferred_fact                          # noqa: E402
from production import (                                            # noqa: E402
    folder_levels_for, group_level_fields_for, load_shipped_catalogue,
    read_packaged_library_file, shipped_situations,
)
from tools.groundtruth.labels import Label, LabelError, Labels, load_labels  # noqa: E402
from tools.groundtruth.score import _norm                           # noqa: E402
from tree_design.config import ConfigurationRequired                # noqa: E402

#: `00` amendment 13's review root. Read off `tree_design.vocabulary` once `106`
#: Task 7.7 has put it there; spelled here only until then.
try:
    from tree_design import vocabulary as _vocabulary
    REVIEW_ROOT = getattr(_vocabulary, "REVIEW_AND_UNSORTED", "98 Review and Unsorted")
except ImportError:                                                # pragma: no cover
    REVIEW_ROOT = "98 Review and Unsorted"

#: What stands where the life should be while no vocabulary of lives exists. A
#: marker, not a folder name.
NO_LIFE = "<life?>"
#: `00`:99: the name of "rests at the parent" when the product mints a folder for it.
GENERAL = "General"

PLACED = "placed"
PROTECTED = "protected"
UNCERTAIN = "uncertain"
UNRESOLVABLE = "situation the library cannot resolve"
BUCKETS = (PLACED, PROTECTED, UNCERTAIN, UNRESOLVABLE)

DOES_NOT_DIVIDE = "does not divide"
FOLDER_PER_FILE = "folder per file"
SINGLE_RUN = "single-child run"

LifeOf = Callable[[str], "str | None"]


def known_situations(catalogue) -> frozenset[str]:
    return frozenset(row.name for row in shipped_situations(catalogue))


def shipped_life_of(catalogue) -> LifeOf | None:
    """`production.life_of` when the release carries one, else `None`.

    `106` Phase 3 adds `life_of` beside `folder_levels_for`; at the tip this was
    written against it does not exist and no applicability row carries `life`.
    Looked up by name so this module runs either way and SAYS which.
    """
    reader = getattr(production, "life_of", None)
    if reader is None:
        return None
    return lambda situation: reader(catalogue, situation)


@dataclass(frozen=True)
class IdealFile:
    """One key row, resolved against the library. Per file, never printed."""

    path: str
    situation: str
    bucket: str
    life: str | None
    #: Field keys of the situation's levels, library order. Empty unless `PLACED`.
    levels: tuple[str, ...]
    #: Per level: the key's value; `""` for a deliberate none; `None` for a blank.
    values: tuple[str | None, ...]
    group_level: tuple[str, ...]
    aliases: Mapping[str, tuple[str, ...]]

    @property
    def unfilled(self) -> tuple[str, ...]:
        return tuple(f for f, v in zip(self.levels, self.values) if v is None)

    def also(self) -> dict[str, tuple[str, ...]]:
        """Normalised value -> the key's other spellings of it, for `compare`."""
        return {_norm(v): self.aliases[f] for f, v in zip(self.levels, self.values)
                if v and f in self.aliases}


def ideal_files(labels: Labels, catalogue, life_of: LifeOf | None) -> tuple[IdealFile, ...]:
    """Every key row resolved to its life, its levels and the key's values for them."""
    return tuple(_resolve(row, catalogue, life_of) for row in labels.values())


def _resolve(row: Label, catalogue, life_of: LifeOf | None) -> IdealFile:
    def bare(bucket, life=None):
        return IdealFile(path=row.path, situation=row.situation, bucket=bucket,
                         life=life, levels=(), values=(), group_level=(),
                         aliases=row.aliases)

    if row.protected:
        return bare(PROTECTED)
    try:
        levels = folder_levels_for(catalogue, row.situation)
        group = group_level_fields_for(catalogue, row.situation)
        life = life_of(row.situation) if life_of is not None else None
    except ConfigurationRequired:
        return bare(UNRESOLVABLE)
    if row.is_uncertain:
        return bare(UNCERTAIN, life)
    return IdealFile(path=row.path, situation=row.situation, bucket=PLACED, life=life,
                     levels=tuple(level.field for level in levels),
                     values=tuple(row.expected_fields.get(level.field) for level in levels),
                     group_level=tuple(sorted(group)), aliases=row.aliases)


# ---------------------------------------------------------------------------
# Building the tree from the rules
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Fold:
    """One place the rules collapsed a level. `depth` is the level's ordinal in the
    library's order (1-based). `provisional` when a blank among the files it judged
    could change the answer once filled."""
    rule: str
    field: str
    depth: int
    provisional: bool


@dataclass
class Built:
    #: Per key path: the ideal chain, root first. Protected rows are absent.
    chains: dict[str, tuple[str, ...]] = field(default_factory=dict)
    #: Per key path: the built levels this file is blank at, so the blank
    #: stopped it -- the cells that cost depth today.
    blocking: dict[str, tuple[str, ...]] = field(default_factory=dict)
    folds: list[Fold] = field(default_factory=list)
    nodes: set[tuple[str, ...]] = field(default_factory=set)


def build(files: Sequence[IdealFile]) -> Built:
    """Apply the depth rules to the key's values and return every file's chain.

    A BRANCH is the set of `PLACED` files sharing one root and one level
    sequence -- what one template composition builds under one life. Two
    situations under one life with different levels are two branches under one
    root, which is how `routing.py` composes a branch holding two lives' rows
    (`106` §0 item 1).

    Rules, in the order applied:
      divides      -- a level is built iff > 1 distinct filled value in the branch
                      (`materialise.py:95`, counted over the level's own values)
      per parent   -- a level with nothing to say under a parent is skipped for
                      it; beneath a BUILT node, children that would each hold one
                      file are not built (`106` Phase 7 §B.1); at the root the
                      split is kept; a file with no value at a level its siblings
                      have rests at the parent (`00`:99)
      single run   -- a chain of single children each holding all of its
                      parent's files, with nothing built beneath, folds into its
                      top (`106` Phase 7 §B.2)
    """
    built = Built()
    branches: dict[tuple[str, tuple[str, ...]], list[IdealFile]] = {}
    for item in files:
        if item.bucket == PLACED:
            branches.setdefault((item.life or NO_LIFE, item.levels), []).append(item)
        elif item.bucket == UNCERTAIN:
            built.chains[item.path] = (REVIEW_ROOT,)
            built.nodes.add((REVIEW_ROOT,))
    for (root, levels), members in sorted(branches.items()):
        _build_branch(root, levels, members, built)
    return built


def _build_branch(root, levels, members, built: Built) -> None:
    is_built = []
    for depth, level in enumerate(levels):
        distinct = {m.values[depth] for m in members if m.values[depth]}
        is_built.append(len(distinct) > 1)
        if len(distinct) <= 1:
            blank = any(m.values[depth] is None for m in members)
            built.folds.append(Fold(DOES_NOT_DIVIDE, level, depth + 1, blank))
    built.nodes.add((root,))

    chains = {m.path: [root] for m in members}
    fields_of = {m.path: [None] for m in members}   # the level behind each segment
    blocking = {m.path: [] for m in members}
    parents: dict[tuple[str, ...], list[IdealFile]] = {(root,): list(members)}
    for depth, level in enumerate(levels):
        if not is_built[depth]:
            continue
        next_parents: dict[tuple[str, ...], list[IdealFile]] = {}
        for parent, group in parents.items():
            by_value: dict[str, list[IdealFile]] = {}
            for m in group:
                if m.values[depth]:
                    by_value.setdefault(m.values[depth], []).append(m)
            if not by_value:
                next_parents.setdefault(parent, []).extend(group)
                continue
            beneath_built = len(parent) > 1
            if beneath_built and len(by_value) > 1 and all(len(v) == 1 for v in by_value.values()):
                blank = any(m.values[depth] is None for m in group)
                built.folds.append(Fold(FOLDER_PER_FILE, level, depth + 1, blank))
                next_parents.setdefault(parent, []).extend(group)
                continue
            for value, group_here in by_value.items():
                built.nodes.add(parent + (value,))
                for m in group_here:
                    chains[m.path].append(value)
                    fields_of[m.path].append(level)
                next_parents.setdefault(parent + (value,), []).extend(group_here)
            for m in group:
                if m.values[depth] is None:
                    blocking[m.path].append(level)
        parents = next_parents

    _fold_single_runs(members, chains, fields_of, built, levels)
    for m in members:
        built.chains[m.path] = tuple(chains[m.path])
        built.blocking[m.path] = tuple(blocking[m.path])


def _fold_single_runs(members, chains, fields_of, built: Built, levels) -> None:
    children: dict[tuple[str, ...], set[tuple[str, ...]]] = {}
    holders: dict[tuple[str, ...], set[str]] = {}
    for m in members:
        chain = tuple(chains[m.path])
        for i in range(1, len(chain) + 1):
            holders.setdefault(chain[:i], set()).add(m.path)
            if i < len(chain):
                children.setdefault(chain[:i], set()).add(chain[:i + 1])
    for top in sorted(children, key=len):
        run, node = [], top
        while len(children.get(node, ())) == 1:
            (only,) = children[node]
            if holders[only] != holders[node]:
                break
            run.append(only)
            node = only
        if not run or children.get(node):
            continue
        for folded in run:
            built.nodes.discard(folded)
            any_path = next(iter(holders[folded]))
            fld = fields_of[any_path][len(folded) - 1]
            built.folds.append(Fold(SINGLE_RUN, fld, levels.index(fld) + 1, False))
            children.pop(folded, None)
        for path in holders[top]:
            del chains[path][len(top):]
            del fields_of[path][len(top):]
        children[top] = set()


# ---------------------------------------------------------------------------
# Comparing the product's tree to the ideal
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Comparison:
    gradeable: int
    exact: int
    #: Index d-1 -> files whose first d segments agree, the root counted.
    prefix_from_root: tuple[int, ...]
    #: The same with the root dropped from both sides: what Phases 6 and 7 move
    #: while the root is still a schema id (`branch_situation.py:465`).
    prefix_below_root: tuple[int, ...]
    not_placed: int


def compare(ideal: Mapping[str, tuple[str, ...]], actual: Mapping[str, tuple[str, ...]],
            also: Mapping[str, Mapping[str, tuple[str, ...]]] | None = None) -> Comparison:
    """Exact-path and prefix-by-depth agreement between two chains per file.

    Segments compare through `score._norm`, so spelling is not a sorting
    decision. A trailing `General` on the actual side is transparent: `00`:99
    makes it the name of "rests at the parent", which is what an ideal chain that
    stops means. `also` carries, per file, the key's other spellings of a value
    (`Label.aliases`, `IdealFile.also`), accepted anywhere on the chain.
    """
    also = also or {}
    gradeable = exact = not_placed = 0
    deepest = max((len(c) for c in ideal.values()), default=0)
    from_root = [0] * deepest
    below = [0] * max(deepest - 1, 0)
    for path, want in ideal.items():
        gradeable += 1
        got = tuple(actual.get(path, ()))
        if not got:
            not_placed += 1
            continue
        if len(got) > len(want) and _norm(got[-1]) == _norm(GENERAL):
            got = got[:-1]
        spellings = also.get(path, {})
        accept = [{_norm(seg), *(_norm(o) for o in spellings.get(_norm(seg), ()))}
                  for seg in want]
        agree = _agreeing(got, accept)
        if agree == len(want) == len(got):
            exact += 1
        for d in range(agree):
            from_root[d] += 1
        for d in range(_agreeing(got[1:], accept[1:])):
            below[d] += 1
    return Comparison(gradeable, exact, tuple(from_root), tuple(below), not_placed)


def _agreeing(got, accept) -> int:
    n = 0
    for segment, ok in zip(got, accept):
        if _norm(segment) not in ok:
            break
        n += 1
    return n


# ---------------------------------------------------------------------------
# Reading the database: the product's facts and its tree, aggregates only
# ---------------------------------------------------------------------------

@dataclass
class LevelReach:
    field: str
    group_level: bool
    rows: int = 0            # key rows whose situation has this level
    key_filled: int = 0
    key_none: int = 0        # deliberate `""`
    key_blank: int = 0
    db_filled: int = 0       # a preferred fact at a proposal-eligible state
    db_several: int = 0      # live rows naming several values, none preferred
    agree: int = 0
    disagree: int = 0
    db_fills_blank: int = 0  # the key is blank and the database has a value


def read_database(database: str | Path, corpus_root: str | Path, files: Sequence[IdealFile]):
    """`(reach per level, actual chain per key path, joined count, protected files the
    product PLACED)` from a run database. The last must be 0: protected material is
    counted, never moved.

    Read-only, on `measure.py`'s seams: the roster off `files.current_path` made
    relative to the corpus root, the value a reader would show off
    `preferred_fact`, the placement off `placement_decisions` (`subject_ref` =
    `file:<id>:<hash>`, live `place` rows) chained through `tree_nodes`.
    """
    root = str(Path(corpus_root).resolve()).rstrip("/") + "/"
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        by_path = {}
        for row in conn.execute("select file_id, current_path from files"):
            if row["current_path"].startswith(root):
                by_path[row["current_path"][len(root):]] = row["file_id"]
        values = {r["value_id"]: r["canonical_value"]
                  for r in conn.execute('select value_id, canonical_value from "values"')}
        reach: dict[str, LevelReach] = {}
        for item in files:
            file_id = by_path.get(item.path)
            for fld, want in zip(item.levels, item.values):
                cell = reach.setdefault(fld, LevelReach(fld, fld in item.group_level))
                cell.rows += 1
                if want is None:
                    cell.key_blank += 1
                elif want == "":
                    cell.key_none += 1
                else:
                    cell.key_filled += 1
                if file_id is None:
                    continue
                got = _db_value(conn, file_id, fld, values)
                if got == _SEVERAL:
                    cell.db_several += 1
                elif got is not None:
                    cell.db_filled += 1
                    if want is None:
                        cell.db_fills_blank += 1
                    elif want:
                        ok = {_norm(want), *(_norm(o) for o in item.aliases.get(fld, ()))}
                        if _norm(got) in ok:
                            cell.agree += 1
                        else:
                            cell.disagree += 1
        actual, protected_placed = _actual_chains(conn, by_path, files)
        return reach, actual, sum(1 for f in files if f.path in by_path), protected_placed
    finally:
        conn.close()


_SEVERAL = object()


def _db_value(conn, file_id, fld, values):
    row = preferred_fact(conn, file_id=file_id, field_key=fld)
    if row is not None:
        if row["reliability_state"] not in PROPOSAL_ELIGIBLE_STATES:
            return None
        return values.get(row["value_id"])
    n = conn.execute(
        "select count(distinct value_id) from file_facts where file_id = ? and "
        "field_key = ? and active = 1 and superseded_by is null", (file_id, fld)).fetchone()[0]
    return _SEVERAL if n > 1 else None


def _actual_chains(conn, by_path, files):
    """The product's chain per key path, walked INSIDE the decision's own plan version.

    `tree_nodes` is keyed `(plan_version_id, node_id)` and a sort database holds
    many versions; a walk keyed on `node_id` alone would cross into another
    version's tree and COMPARE would lie on the number this tool exists for.
    """
    try:
        nodes = {(r["plan_version_id"], r["node_id"]): (r["display_label"], r["parent_node_id"])
                 for r in conn.execute("select plan_version_id, node_id, display_label, "
                                       "parent_node_id from tree_nodes")}
        decided = {}
        for r in conn.execute("select subject_ref, plan_version, node_id from "
                              "placement_decisions where superseded_by is null and "
                              "outcome = 'place' order by created_at"):
            parts = r["subject_ref"].split(":")
            if len(parts) >= 2 and parts[0] == "file":
                decided[parts[1]] = (r["plan_version"], r["node_id"])
    except sqlite3.OperationalError:
        return {}, 0
    out = {}
    protected_placed = 0
    for item in files:
        placed = decided.get(by_path.get(item.path))
        if placed is None:
            continue
        if item.bucket == PROTECTED:
            protected_placed += 1
            continue
        version, node = placed
        chain, seen = [], set()
        while node and (version, node) in nodes and node not in seen:
            seen.add(node)
            label, node = nodes[(version, node)]
            chain.append(label)
        if chain:
            out[item.path] = tuple(reversed(chain))
    return out, protected_placed


# ---------------------------------------------------------------------------
# The report: counts only
# ---------------------------------------------------------------------------

def render(files: Sequence[IdealFile], built: Built, catalogue, life_reader_present: bool,
           reach=None, comparison=None, joined=None, protected_placed=0) -> str:
    lines = []
    say = lines.append
    say(f"IDEAL TREE  key rows {len(files)}  library release {catalogue.release_id}")
    buckets = Counter(f.bucket for f in files)
    say("  " + "  ".join(f"{b} {buckets.get(b, 0)}" for b in BUCKETS))
    placed = [f for f in files if f.bucket == PLACED]

    if life_reader_present:
        lives = Counter(f.life or NO_LIFE for f in placed)
        say(f"LIVES  {len([k for k in lives if k != NO_LIFE])} named by the key's situations; "
            f"{lives.get(NO_LIFE, 0)} files in a situation the release places in no life")
        for life, n in lives.most_common():
            say(f"  {life}: {n}")
    else:
        say("LIVES  root unfillable: the release carries no `life_of`, so every root below "
            f"reads {NO_LIFE} (`106` Phase 3 owes it)")

    say("LEVELS  per field, over the key rows whose situation builds it")
    say("  field                 rows  filled  none  blank  blank-blocks-depth  group-level")
    per: dict[str, list[int]] = {}
    for f in placed:
        blocks = set(built.blocking.get(f.path, ()))
        for fld, v in zip(f.levels, f.values):
            cell = per.setdefault(fld, [0, 0, 0, 0, 0])
            cell[0] += 1
            cell[1 if v else (2 if v == "" else 3)] += 1
            cell[4] += fld in blocks
    group_fields = {fld for f in placed for fld in f.group_level}
    owed = sum(c[3] for c in per.values())
    cells = sum(c[0] for c in per.values())
    for fld, c in sorted(per.items(), key=lambda kv: (-kv[1][0], kv[0])):
        say(f"  {fld:<20} {c[0]:>5} {c[1]:>7} {c[2]:>5} {c[3]:>6} {c[4]:>19}  "
            f"{'yes' if fld in group_fields else ''}")
    say(f"OWED  {owed} of {cells} level cells are blank"
        + (f" ({100 * owed / cells:.1f} %)" if cells else "")
        + f"; {sum(len(v) for v in built.blocking.values())} of them block depth today")

    depths = Counter(len(c) - 1 for c in built.chains.values())
    say("DEPTH  files by ideal depth below the root: "
        + (", ".join(f"{d}: {n}" for d, n in sorted(depths.items())) or "none"))
    nodes_by_depth = Counter(len(n) - 1 for n in built.nodes)
    roots = sorted({n[0] for n in built.nodes})
    say(f"TREE  roots {len(roots)} (review root {'present' if REVIEW_ROOT in roots else 'absent'}; "
        f"protected counted at root: {buckets.get(PROTECTED, 0)}); nodes by depth: "
        + (", ".join(f"{d}: {n}" for d, n in sorted(nodes_by_depth.items())) or "none"))
    folds = Counter((f.rule, f.provisional) for f in built.folds)
    say("FOLDS  " + (", ".join(
        f"{rule}{' (provisional)' if prov else ''}: {n}"
        for (rule, prov), n in sorted(folds.items())) or "none"))

    if reach is not None:
        say(f"DATABASE  {joined} of {len(files)} key rows joined to the roster; "
            f"protected files the product placed: {protected_placed} (must be 0)")
        say("REACH  field              key-filled  db-filled  agree  disagree  several  db-fills-blank")
        for fld, c in sorted(reach.items(), key=lambda kv: (-kv[1].rows, kv[0])):
            say(f"  {fld:<18} {c.key_filled:>10} {c.db_filled:>10} {c.agree:>6} {c.disagree:>9} "
                f"{c.db_several:>8} {c.db_fills_blank:>15}")
    if comparison is not None:
        c = comparison
        pct = f" ({100 * c.exact / c.gradeable:.1f} %)" if c.gradeable else ""
        say(f"COMPARE  gradeable {c.gradeable}  exact {c.exact}{pct}  not placed {c.not_placed}")
        say("  prefix from root by depth:  " + (", ".join(
            f"{d + 1}: {n}" for d, n in enumerate(c.prefix_from_root)) or "none"))
        say("  prefix below root by depth: " + (", ".join(
            f"{d + 1}: {n}" for d, n in enumerate(c.prefix_below_root)) or "none"))
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--labels", required=True)
    parser.add_argument("--database")
    parser.add_argument("--corpus-root",
                        help="required with --database: the key's paths are relative to it")
    parser.add_argument("--out", help="per-file JSON rows; the only place a path is written")
    args = parser.parse_args(argv)
    if bool(args.database) != bool(args.corpus_root):
        parser.error("--database and --corpus-root go together")

    catalogue = load_shipped_catalogue(read_packaged_library_file)
    try:
        # The library's own names, so this tool needs nothing of `cli`'s.
        labels = load_labels(args.labels, known_situations=known_situations(catalogue))
    except LabelError as refused:
        # The message opens with the offending path; only the rule leaves this process.
        rule = str(refused).split(": ", 1)[-1].split(".")[0]
        print(f"the key was refused by the loader: {rule}", file=sys.stderr)
        return 2
    life_of = shipped_life_of(catalogue)
    files = ideal_files(labels, catalogue, life_of)
    built = build(files)

    reach = comparison = joined = None
    protected_placed = 0
    if args.database:
        reach, actual, joined, protected_placed = read_database(
            args.database, args.corpus_root, files)
        comparison = compare(built.chains, actual, {f.path: f.also() for f in files})
    print(render(files, built, catalogue, life_of is not None, reach, comparison, joined,
                 protected_placed))

    if args.out:
        rows = []
        for f in files:
            row = asdict(f)
            row["aliases"] = dict(f.aliases)
            row["chain"] = built.chains.get(f.path)
            row["blocking"] = built.blocking.get(f.path, ())
            rows.append(row)
        Path(args.out).write_text(json.dumps(rows, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
