"""Assemble P6 / P7 PLAN.md from the per-task section files.

Concatenation, not regeneration. Every task section is copied byte-for-byte from its
winning file; only the mechanical fixes named in the handoff §8 are applied, and each
one is counted so the diff is auditable. Front matter (everything before the first
`### Task N` in a file) is DROPPED here — it is harvested separately into the lead's
single shared preamble, because four P6 files and eight P7 files each wrote one and
one of them states a convention brief §11 later overruled.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path("/Users/jy/GRAPH AGENT")
PARTS = ROOT / "planning/parts"
TASK_RE = re.compile(r"^### Task (\d+)\b")


def back_matter(path: Path) -> list[str]:
    """Everything from the first `## ` heading AFTER the last task, to EOF.

    Task headings are `### `; a file's closing appendices are `## `. Verified across
    all twelve P6 files: every `## ` after the last `### Task` is trailing appendix,
    and there are none inside a task section. Without this split the appendices of a
    file whose last task LOST are dropped silently -- which is what happened to
    `PLAN-tasks-07-09.md` on the first pass.
    """
    lines = path.read_text(encoding="utf-8").split("\n")
    last = max((i for i, l in enumerate(lines) if TASK_RE.match(l)), default=-1)
    for i in range(last + 1, len(lines)):
        if lines[i].startswith("## "):
            tail = lines[i:]
            while tail and not tail[-1].strip():
                tail.pop()
            return tail
    return []


def sections(path: Path) -> dict[int, list[str]]:
    """task number -> its lines, from its `### Task N` heading to the next one.

    The last task's slice is truncated at the file's back matter (see above)."""
    lines = path.read_text(encoding="utf-8").split("\n")
    starts: list[tuple[int, int]] = []
    for i, ln in enumerate(lines):
        m = TASK_RE.match(ln)
        if m:
            starts.append((int(m.group(1)), i))
    out: dict[int, list[str]] = {}
    for k, (num, i) in enumerate(starts):
        end = starts[k + 1][1] if k + 1 < len(starts) else len(lines)
        body = lines[i:end]
        for j, l in enumerate(body):
            if j and l.startswith("## "):
                body = body[:j]
                break
        while body and not body[-1].strip():
            body.pop()
        out[num] = body
    return out


# --- the mechanical fixes, handoff §8. Each is (name, pattern, replacement, where).
# `where` is a predicate on the part name so a P6-only fix never touches P7.
FIXES: list[tuple[str, re.Pattern[str], str, str]] = [
    # brief §17: the column is `field_key` and it holds the field key.
    ("field_id -> field_key", re.compile(r"\bfield_id\b"), "field_key", "P6"),
    # the suite is 1302 (1300 + the two C22 tests), quoted as 1292 in three P7 files.
    ("1292 -> 1302 tests", re.compile(r"\b1292\b"), "1302", "both"),
    ("1300 -> 1302 tests", re.compile(r"\b1300 (tests|passed)\b"), r"1302 \1", "both"),
    # brief §10: the type is a concrete store P7 owns, not an injected protocol.
    ("facts_seam -> classification_store",
     re.compile(r"\bfacts_seam\b"), "classification_store", "P7"),
    ("SensitivityFacts -> ClassificationStore",
     re.compile(r"\bSensitivityFacts\b"), "ClassificationStore", "P7"),
]


def apply_fixes(text: str, part: str) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}
    for name, pat, repl, where in FIXES:
        if where not in (part, "both"):
            continue
        text, n = pat.subn(repl, text)
        if n:
            counts[name] = counts.get(name, 0) + n
    return text, counts


def assemble(part: str, dirname: str, winners: dict[int, str], preamble: Path,
             out: Path) -> None:
    cache: dict[str, dict[int, list[str]]] = {}
    body: list[str] = []
    missing: list[int] = []
    for num in sorted(winners):
        fname = winners[num]
        if fname not in cache:
            cache[fname] = sections(PARTS / dirname / fname)
        secs = cache[fname]
        if num not in secs:
            missing.append(num)
            continue
        body.append("\n".join(secs[num]))
    if missing:
        sys.exit(f"FATAL {part}: tasks {missing} not found in their winner files")

    joined = "\n\n---\n\n".join(body)
    joined, counts = apply_fixes(joined, part)
    text = preamble.read_text(encoding="utf-8").rstrip() + "\n\n---\n\n" + joined + "\n"
    out.write_text(text, encoding="utf-8")

    print(f"\n{part}: {len(winners)} tasks -> {out}")
    print(f"  lines: {text.count(chr(10)) + 1}")
    for k, v in sorted(counts.items()):
        print(f"  fix applied {v:4d}x  {k}")
    # verification: every task present exactly once, in order
    got = [int(m.group(1)) for m in
           (TASK_RE.match(l) for l in text.split("\n")) if m]
    assert got == sorted(winners), f"{part}: task order/duplication broken: {got}"
    print(f"  verified: tasks {got[0]}..{got[-1]}, {len(got)} headings, strictly ascending")


if __name__ == "__main__":
    print(__doc__)
