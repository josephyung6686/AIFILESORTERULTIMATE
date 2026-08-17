"""Classify loose files onto frozen node content profiles."""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from database_agent.nodes import (
    CLASS_CODE_RE,
    WEAK_TOKENS,
    NodeProfile,
    class_codes,
    tokenize,
)

DEFAULT_MIN_SCORE = 1.0
DEFAULT_MIN_MARGIN = 0.4


@dataclass(frozen=True)
class Decision:
    source: Path
    dest: Path | None
    disposition: str
    score: float
    margin: float
    reason: str


@dataclass(frozen=True)
class Proposal:
    label: str
    tokens: tuple[str, ...]
    example_files: tuple[Path, ...]
    created_on_disk: bool = False
    suggested_parent: Path | None = None


def _idf(profiles: dict[Path, NodeProfile]) -> dict[str, float]:
    n_nodes = max(len(profiles), 1)
    df: Counter[str] = Counter()
    for profile in profiles.values():
        df.update(profile.token_counts.keys())
    return {token: math.log((n_nodes + 1) / (count + 1)) + 1.0 for token, count in df.items()}


def _weight(token: str) -> float:
    if CLASS_CODE_RE.match(token):
        return 3.0
    if token in WEAK_TOKENS:
        return 0.15
    return 1.0


def _is_weak(token: str) -> bool:
    return token in WEAK_TOKENS


def score_file(
    filename: str,
    profile: NodeProfile,
    idf: dict[str, float],
    *,
    identity_tokens: frozenset[str] = frozenset(),
) -> tuple[float, int]:
    tokens = tokenize(filename, identity_tokens=identity_tokens)
    total = 0.0
    distinctive = 0
    for token in tokens:
        tf = profile.token_counts[token]
        if tf <= 0:
            continue
        weight = _weight(token)
        total += weight * (1.0 + math.log(tf)) * idf.get(token, 1.0)
        if not _is_weak(token):
            distinctive += 1
    return total, distinctive


def _known_class_codes(profiles: dict[Path, NodeProfile]) -> set[str]:
    known: set[str] = set()
    for profile in profiles.values():
        known.update(class_codes(tuple(profile.token_counts)))
    return known


def classify_loose(
    files: list[Path],
    profiles: dict[Path, NodeProfile],
    *,
    min_score: float = DEFAULT_MIN_SCORE,
    min_margin: float = DEFAULT_MIN_MARGIN,
    identity_tokens: frozenset[str] = frozenset(),
) -> tuple[list[Decision], list[Proposal]]:
    idf = _idf(profiles)
    known_codes = _known_class_codes(profiles)
    decisions: list[Decision] = []
    loose_code_files: dict[str, list[Path]] = defaultdict(list)

    for source in files:
        tokens = tokenize(source.name, identity_tokens=identity_tokens)
        unknown = [code for code in class_codes(tokens) if code not in known_codes]
        for code in unknown:
            loose_code_files[code].append(source)
        if unknown:
            decisions.append(
                Decision(
                    source=source,
                    dest=None,
                    disposition="skip",
                    score=0.0,
                    margin=0.0,
                    reason=f"unknown class token {unknown[0]}",
                )
            )
            continue

        ranked: list[tuple[float, int, Path]] = []
        for dest, profile in profiles.items():
            if profile.file_count == 0:
                continue
            score, distinctive = score_file(
                source.name, profile, idf, identity_tokens=identity_tokens
            )
            if distinctive == 0:
                continue
            ranked.append((score, distinctive, dest))
        ranked.sort(reverse=True)

        if not ranked or ranked[0][0] < min_score:
            decisions.append(
                Decision(
                    source=source,
                    dest=None,
                    disposition="skip",
                    score=ranked[0][0] if ranked else 0.0,
                    margin=0.0,
                    reason="below score gate",
                )
            )
            continue

        best_score, _, best_dest = ranked[0]
        second = ranked[1][0] if len(ranked) > 1 else 0.0
        margin = best_score - second
        if margin < min_margin:
            decisions.append(
                Decision(
                    source=source,
                    dest=None,
                    disposition="skip",
                    score=best_score,
                    margin=margin,
                    reason="top two destinations too close",
                )
            )
            continue

        decisions.append(
            Decision(
                source=source,
                dest=best_dest,
                disposition="match",
                score=best_score,
                margin=margin,
                reason=f"content profile {best_dest.name}",
            )
        )

    proposals: list[Proposal] = []
    for code, examples in sorted(loose_code_files.items()):
        unique_examples = tuple(dict.fromkeys(examples))
        if len(unique_examples) < 2:
            continue
        proposals.append(
            Proposal(
                label=code,
                tokens=(code,),
                example_files=unique_examples,
                created_on_disk=False,
                suggested_parent=None,
            )
        )
    return decisions, proposals
