"""`66` §4's five states, and the refusal to merge them.

    "'Protected by your privacy policy' means the product deliberately did not
    reveal more. 'Unreadable' means the product could not obtain usable content.
    'Still indexing' means the product has not completed analysis. 'Unsupported
    format' means no approved extractor exists. 'No strong match' means the local
    retrieval system found no result that satisfies the query. These states
    should never share one vague message such as 'could not find.'"

`67` §1 makes this a standing constraint rather than a nicety: protected material
is present-but-untouched with a REACHABLE EXPLANATION, never silently omitted and
never described as "understood and found unimportant". So `explanation_ref` is
required on every notice and an empty one is refused at construction.

The five sentences are the design's own distinctions written down. Every WORD of
them is deferred by the SPEC's Deferred table, so a renderer with copy will
replace them; what is contractual is that there are five of them and that no two
say the same thing. A user who cannot tell these apart cannot tell whether to
change a setting, fix a file, wait, or search differently -- which is the whole
difference between an honest empty result and a shrug.

`one_message_for` exists and always raises. It is the one place a future author
would reach for when asked to "just show a single 'not found' line", and it is
better for that function to exist and say why than for the merge to be written
somewhere new.

A zero count cannot be constructed. `66` §4's requirement is about the states that
DO apply; reporting "0 protected items" on every screen is noise, and the absence
of a notice is what "none of these applies" looks like.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType

from review_surface.vocabulary import check

ABSENCE_PROTECTED: str = "protected"
ABSENCE_UNREADABLE: str = "unreadable"
ABSENCE_UNSUPPORTED: str = "unsupported_format"
ABSENCE_STILL_INDEXING: str = "still_indexing"
ABSENCE_NO_STRONG_MATCH: str = "no_strong_match"

#: In `66` §4's own order, which is the order a screen reads them in.
ABSENCE_STATES: tuple[str, ...] = (
    ABSENCE_PROTECTED, ABSENCE_UNREADABLE, ABSENCE_UNSUPPORTED,
    ABSENCE_STILL_INDEXING, ABSENCE_NO_STRONG_MATCH,
)

#: One sentence per state, each saying what `66` §4 says that state MEANS.
ABSENCE_SENTENCES: Mapping[str, str] = MappingProxyType({
    ABSENCE_PROTECTED:
        "Protected by your privacy policy. The product deliberately did not "
        "reveal more, and did not open these items.",
    ABSENCE_UNREADABLE:
        "Could not be read. The product could not obtain usable content from "
        "these files.",
    ABSENCE_UNSUPPORTED:
        "Unsupported format. No approved extractor exists for these files yet.",
    ABSENCE_STILL_INDEXING:
        "Still indexing. The product has not finished analysing these files.",
    ABSENCE_NO_STRONG_MATCH:
        "No strong match. Nothing here satisfied what you asked for.",
})
assert set(ABSENCE_SENTENCES) == set(ABSENCE_STATES)
assert len(set(ABSENCE_SENTENCES.values())) == len(ABSENCE_STATES)


class StatesCollapsed(RuntimeError):
    """Something asked for one message across two or more states. `66` §4 forbids it."""


@dataclass(frozen=True)
class AbsenceNotice:
    """One state that applies, its count, and the explanation the user can reach."""

    state: str
    count: int
    explanation_ref: str

    def __post_init__(self) -> None:
        check(self.state, ABSENCE_STATES, name="absence state")
        if self.count < 1:
            raise ValueError(
                "a notice reports a state that APPLIES; a zero count is not a "
                "state to report, and printing it on every screen is noise")
        if not self.explanation_ref:
            raise ValueError(
                "`66` §4 requires a reachable explanation of what this state "
                "means and why; a notice without one is the vague message the "
                "section exists to forbid")

    def sentence(self) -> str:
        return ABSENCE_SENTENCES[self.state]


def absence_notices(counts: Mapping[str, int], *,
                    explanation_refs: Mapping[str, str],
                    ) -> tuple[AbsenceNotice, ...]:
    """One notice per state that applies, in `66` §4's order. Zeroes omitted."""
    return tuple(
        AbsenceNotice(state=state, count=counts[state],
                      explanation_ref=explanation_refs[state])
        for state in ABSENCE_STATES
        if counts.get(state, 0) > 0)


def one_message_for(states: Sequence[str]) -> None:
    """Always raises. This is the place the merge is refused, by name."""
    named = ", ".join(sorted(set(states)))
    raise StatesCollapsed(
        f"`66` §4: {named} may not share one message. Each names a different "
        "thing that happened -- a deliberate privacy decision, a reading "
        "failure, a missing extractor, unfinished work, and an honest empty "
        "result -- and a user who cannot tell them apart cannot tell whether "
        "to change a setting, fix a file, wait, or search differently")
