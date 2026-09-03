# tests/p5/test_p5_router_code_formats.py
"""§2.9's code/structured family, spelled for the languages a real disk holds.

§2.9 names the family "code/structured" and spells nine formats: `ipynb js json py
sql toml xml yaml yml`. The router's own note records that this is how the table
grows -- `added_by_b6_and_not_by_a_design_sentence` already carries eleven image and
audio formats added on ratification, "§2.9 names the family and no format".

The nine it spells are a web-and-Python selection. Measured across the owner's real
~/Desktop and ~/Documents, the files they do NOT reach:

    cpp   449      swift 299      ts    143      css    33
    hpp   322      h     199      ino    79      cmake  32
    tsx   300      c     162      sh     43      jsx    27
                                  kt     37

2,125 files -- 40% of that Desktop -- arriving as `unrouted / unsupported`: no
extractor, no text, no observations, nothing to classify and nowhere to file. The
owner is an embedded and application developer, and the product could not read a
line of his C, C++, Swift, TypeScript or Arduino code while reading his `.py` and
`.js` perfectly.

Every format here was counted on that disk. Nothing is added for a language he does
not write: an unmet extension costs nothing to omit, and the guard in
`test_p5_router.py` makes any addition declare itself rather than arrive silently.

The handler is unchanged and is the family's own: `code_structured ->
text.structured`, whose reader falls back to plain text for an extension it has no
special opener for -- which is exactly right for source code.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from extractors.router import SOURCE_TYPE_BY_FORMAT, route

#: Every format this change adds, with the count measured on the owner's disk.
AUTHORED = {
    "cpp": 449, "hpp": 322, "tsx": 300, "swift": 299, "h": 199, "c": 162,
    "ts": 143, "ino": 79, "sh": 43, "kt": 37, "css": 33, "cmake": 32, "jsx": 27,
}


def _detect_nothing(path: Path) -> str | None:
    """The deployment's sniffer knows five formats; these arrive by extension."""
    return None


@pytest.mark.parametrize("fmt", sorted(AUTHORED))
def test_each_authored_code_format_reaches_the_family(fmt):
    assert SOURCE_TYPE_BY_FORMAT[fmt][0] == "code_structured"


@pytest.mark.parametrize("fmt", sorted(AUTHORED))
def test_each_authored_code_format_gets_the_familys_extractor(fmt):
    decision = route(file_id="f", content_hash="h", path=Path(f"main.{fmt}"),
                     extension=f".{fmt}", detect_format=_detect_nothing)
    assert decision.extractor_name == "text.structured"
    assert decision.unrouted_completeness is None


def test_the_nine_formats_2_9_spells_are_untouched():
    """The design's own nine still route exactly as they did."""
    for fmt in ("ipynb", "js", "json", "py", "sql", "toml", "xml", "yaml", "yml"):
        assert SOURCE_TYPE_BY_FORMAT[fmt][0] == "code_structured"


def test_a_format_nobody_authored_is_still_unrouted():
    """The negative twin. Adding thirteen names may not turn the table into a
    default-yes: an unknown extension must still say `unsupported` out loud, which
    is §2.4's rule that a format nobody supports is never a silently empty file."""
    decision = route(file_id="f", content_hash="h", path=Path("thing.qqzz"),
                     extension=".qqzz", detect_format=_detect_nothing)
    assert decision.extractor_name is None
    assert decision.unrouted_completeness == "unsupported"


def test_a_binary_format_did_not_become_text(tmp_path):
    """`.exe` was counted on that disk too and is deliberately NOT here."""
    decision = route(file_id="f", content_hash="h", path=Path("setup.exe"),
                     extension=".exe", detect_format=_detect_nothing)
    assert decision.extractor_name is None
