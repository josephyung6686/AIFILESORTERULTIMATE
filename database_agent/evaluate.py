"""Held-out evaluation: already-filed files are a labelled dataset."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from database_agent.classify import DEFAULT_MIN_MARGIN, DEFAULT_MIN_SCORE, classify_loose
from database_agent.nodes import assign_file_to_node, build_profiles, iter_destination_folders


@dataclass(frozen=True)
class EvalReport:
    hits: int
    misses: int
    abstains: int
    total: int

    @property
    def precision(self) -> float:
        placed = self.hits + self.misses
        if placed == 0:
            return 1.0
        return self.hits / placed

    @property
    def coverage(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.hits + self.misses) / self.total


@dataclass(frozen=True)
class SyntheticTree:
    desktop: Path
    loose_dir: Path
    filed_files: list[Path]
    dest_folders: list[Path]


def _touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x", encoding="utf-8")
    return path


def make_synthetic_tree(root: Path) -> SyntheticTree:
    desktop = root / "Desktop"
    downloads = root / "Downloads"
    plasmole = desktop / "Work" / "Plasmole"
    cs3134 = desktop / "Courses" / "CS3134"
    taxes = desktop / "Finance" / "Taxes"
    photos = desktop / "Photos"
    work = desktop / "Work"

    distinctive = [
        plasmole / "plasmole-a.md",
        plasmole / "plasmole-b.md",
        plasmole / "plasmole-c.md",
        plasmole / "plasmole-d.md",
        cs3134 / "cs3134-hw1.pdf",
        cs3134 / "cs3134-hw2.pdf",
        cs3134 / "cs3134-lecture-03.pdf",
        cs3134 / "cs3134-syllabus.pdf",
        taxes / "2024-w2-tax.pdf",
        taxes / "2024-1099-tax.pdf",
        taxes / "2023-tax-return.pdf",
        photos / "family-1001.jpg",
        photos / "family-1002.jpg",
    ]
    generic = [
        plasmole / "notes.txt",
        plasmole / "readme.md",
        cs3134 / "homework.pdf",
        cs3134 / "lecture.pdf",
        taxes / "summary.xlsx",
        photos / "vacation.jpg",
        photos / "paris.jpg",
        work / "todo.txt",
    ]
    filed = [_touch(path) for path in distinctive + generic]
    downloads.mkdir(parents=True, exist_ok=True)
    dests = iter_destination_folders([desktop])
    return SyntheticTree(
        desktop=desktop,
        loose_dir=downloads,
        filed_files=filed,
        dest_folders=dests,
    )


def hold_out(
    dest_folders: list[Path],
    filed_files: list[Path],
    *,
    min_score: float = DEFAULT_MIN_SCORE,
    min_margin: float = DEFAULT_MIN_MARGIN,
    identity_tokens: frozenset[str] = frozenset(),
) -> EvalReport:
    hits = misses = abstains = 0
    for held in filed_files:
        truth = assign_file_to_node(held, dest_folders)
        rest = [path for path in filed_files if path != held]
        profiles = build_profiles(dest_folders, rest, identity_tokens=identity_tokens)
        decisions, _ = classify_loose(
            [held],
            profiles,
            min_score=min_score,
            min_margin=min_margin,
            identity_tokens=identity_tokens,
        )
        dest = decisions[0].dest if decisions else None
        if dest is None:
            abstains += 1
        elif truth is not None and dest == truth:
            hits += 1
        else:
            misses += 1
    return EvalReport(hits=hits, misses=misses, abstains=abstains, total=len(filed_files))


def run_synthetic(root: Path) -> EvalReport:
    tree = make_synthetic_tree(root)
    return hold_out(tree.dest_folders, tree.filed_files)


def main() -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        report = run_synthetic(Path(tmp))
        placed = report.hits + report.misses
        print(
            f"{report.precision:.0%} held-out precision at {report.coverage:.0%} coverage "
            f"({report.hits} hit, {report.misses} miss, {report.abstains} abstain, "
            f"{placed}/{report.total} placed)."
        )
        if report.misses:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
