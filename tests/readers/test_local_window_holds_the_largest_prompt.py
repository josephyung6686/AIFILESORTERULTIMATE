"""`104` §18.15 (10 Sep 2026): the local window holds the largest prompt the product
can build, with room for the answer, so a smaller window loses nothing.

`cli.LOCAL_CONTEXT_CEILING` was 32,768, sized when a dossier could be 96 KB. `104`
R-174 bounds the released list in wire bytes, so the largest prompt is now
DERIVABLE: the largest template in the library, plus a dossier frame, plus the
released bound, plus as many evidence items as that bound admits readings. This
test derives it from the library and the limits -- no size is typed -- and holds
that the window fits it beside `MAX_RESPONSE_TOKENS` under the client's own
conservative arithmetic (`_upper_bound`, two bytes per token). A prompt past the
window is refused by `_fits`, never truncated, which is the other half of "nothing
is lost": the owner's condition for the drop.

SABOTAGE: set `LOCAL_CONTEXT_CEILING` to 16,384 and this goes red; set it back to
32,768 and it passes with the memory the drop was made to free.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402
from evidence_shape.canonical import canonical_json  # noqa: E402
from llm_harness.dossier import (  # noqa: E402
    _evidence_item_body, canonical_dossier_bytes, released_item_wire_bytes,
)
from llm_harness.fixtures import SITE_C_REASON_PAIRS  # noqa: E402
from llm_harness.records import EvidenceItem  # noqa: E402
from readers.model_ollama import _fits, _upper_bound  # noqa: E402

LIBRARY = Path(__file__).resolve().parents[2] / "src" / "llm_harness" / "library"
KEY = bytes(32)


def _largest_prompt_bytes() -> int:
    """The bound, from the library and the limits, each part measured off the
    function that writes it."""
    template = max(path.stat().st_size for path in LIBRARY.glob("*template*.txt"))
    # The frame: a real fixture dossier rendered under site A's ratified prompt
    # definition (the largest schema and policy in the library travel with it).
    pair = SITE_C_REASON_PAIRS[0]
    frame = len(canonical_dossier_bytes(pair.dossier, cli.a_fact_prompt(), handle_key=KEY))
    released_bound = cli.GROUPING_LIMITS.max_dossier_tokens
    smallest_reading = released_item_wire_bytes(
        observation_key="sha256:" + "0" * 64, address="body:page=1#0-1", value="x",
        zone="body")
    most_readings = released_bound // smallest_reading
    one_item = len(canonical_json(_evidence_item_body(
        EvidenceItem(evidence_ref="sha256:" + "0" * 64, kind="excerpt",
                     location="body:page=1#0-1", excerpt_span=(0, 1),
                     reliability_state="possible", basis="direct-anchor"),
        handle_key=KEY)))
    return template + frame + released_bound + most_readings * one_item


def test_the_window_holds_the_largest_buildable_prompt_and_its_answer():
    bound = _largest_prompt_bytes()
    assert bound > 0
    needed = _upper_bound(bound) + cli.MAX_RESPONSE_TOKENS
    assert needed <= cli.LOCAL_CONTEXT_CEILING, (bound, needed)
    # The client's own refusal agrees: this prompt is sent, not refused.
    _fits(bound, max_response_tokens=cli.MAX_RESPONSE_TOKENS,
          context_ceiling=cli.LOCAL_CONTEXT_CEILING)


def test_the_window_is_not_slack_by_a_whole_dossier():
    """The drop is a drop: the old window held a second largest prompt on top of
    the first, which is the memory the owner's ruling reclaims."""
    bound = _largest_prompt_bytes()
    assert _upper_bound(2 * bound) + cli.MAX_RESPONSE_TOKENS > cli.LOCAL_CONTEXT_CEILING
