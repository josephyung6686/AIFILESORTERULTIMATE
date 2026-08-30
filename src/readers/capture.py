# src/readers/capture.py
"""§2.6's and §2.2's injected catalogues, compiled into the callables that need them.

Four hand-authored catalogues were finished on 2026-08-20, checked, and then read by
nothing: `grep -rn "deferred-catalogues" src` returned nothing at all. This module is
the missing half. It holds no pattern, no resolution, no ratio and no producer string
of its own -- every one of them arrives from a file in `library/`, lifted from
`planning/deferred-catalogues/` with its provenance wrappers removed and its
provenance kept, which is the shape `src/tree_design/library/residuals.json` already
ships.

**Why here and not in `src/extractors/`.** All four catalogues say the same thing in
their own `injection` fields: P5 PLAN's Global Constraints forbid any module-level
gazetteer, regex, screen resolution, producer string or language tag inside
`src/extractors/`, and Task 20 asserts it by RUNTIME INTROSPECTION of every module's
namespace. So these are data the caller loads and injects, and `src/readers/` is the
caller -- the deployment layer that already supplies every reader `extract_image` and
`extract_pdf` require.

**The provenance distinction is enforced, not annotated.** A row marked `design`
claims the design names its literal value; §2.2 does that for exactly two of the 115
producer strings. `ProvenanceMisstated` is raised if a row claims it without carrying
it, because a proposal wearing the design's authority is how an invented value gets
ratified by nobody.

**One number lives here and it is zero.** Catalogue 03's tolerance is a required
keyword with no default, for the reason catalogue 03 gives itself in
`unc-tolerance-value`: "It is a number, so it must not live inside `src/extractors/`
either." It has never been measured against a corpus. The place that decides numbers
injects it.
"""
from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from math import gcd
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

LIBRARY_DIR = Path(__file__).resolve().parent / "library"

#: Catalogue 09's vocabulary, unchanged. `inference` is carried and unused: no row in
#: these four files records a derivation from another row that a rule could read, and
#: assigning one by judgement would be this module authoring what it was given.
PROVENANCE_VALUES: tuple[str, str, str] = ("design", "proposal", "inference")

DESIGN, PROPOSAL = PROVENANCE_VALUES[0], PROVENANCE_VALUES[1]


class ProvenanceMisstated(ValueError):
    """A row claims the design states it, and the quote it cites does not."""


class CatalogueRequired(ValueError):
    """A shipped catalogue is missing or is not the shape its consumer reads."""


def load_capture_catalogue(name: str) -> Mapping[str, Any]:
    """One shipped catalogue, by file stem. No fallback and no empty default.

    `rules.RecognitionRulesRequired` states the reason for the whole family of these:
    "an empty release would make every guard in this package pass by having nothing
    to recognise." A catalogue that silently loads as `{}` claims a corpus contains
    no screenshots, no camera files and no tool metadata, and every downstream count
    would agree with it.
    """
    path = LIBRARY_DIR / f"{name}.json"
    if not path.is_file():
        raise CatalogueRequired(f"{path} is not on disk; this package ships no default")
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded.get("entries"), list) or not loaded["entries"]:
        raise CatalogueRequired(f"{path} carries no entries")
    return loaded


def _check_provenance(row: Mapping[str, Any], literal: str) -> None:
    stated = row.get("provenance")
    if stated not in PROVENANCE_VALUES:
        raise ProvenanceMisstated(
            f"{row.get('id')!r} carries provenance {stated!r}, which is not one of "
            f"{PROVENANCE_VALUES}")
    if stated != DESIGN:
        return
    cite = row.get("design_cite", "")
    if literal.casefold() not in cite.casefold():
        raise ProvenanceMisstated(
            f"{row['id']!r} is marked {DESIGN!r}, which claims the design names "
            f"{literal!r} in as many words -- and the quote it cites does not carry "
            f"it: {cite!r}. It is a {PROPOSAL!r}.")


# ======================================================================================
# Catalogue 04 -- the naming conventions
# ======================================================================================


def _stem(filename: str) -> str:
    """The filename with its FINAL extension removed, catalogue 04's `match_field`.

    `rsplit`, not `os.path.splitext`, and the difference is a recorded trap: macOS
    writes dot-separated times, so `splitext` reads `.45 AM` as the extension of
    `Screenshot 2026-08-20 at 10.30.45 AM` and the `$` anchor then has nowhere to
    land. Both agree on a real filename because P5 passes `file_row["filename"]`,
    which always carries the extension -- that is a property of the caller, and the
    reason it holds is written down rather than assumed.
    """
    return filename.rsplit(".", 1)[0] if "." in filename else filename


def compile_filename_patterns(
        catalogue: Mapping[str, Any]) -> tuple[tuple[re.Pattern[str], int, str], ...]:
    """Compiled in the catalogue's own evaluation order; first match wins."""
    compiled: list[tuple[re.Pattern[str], int, str]] = []
    for row in catalogue["entries"]:
        _check_provenance(row, row["pattern"])
        flags = 0 if row["case_sensitive"] else re.IGNORECASE
        compiled.append((re.compile(row["pattern"], flags), row["capture"], row["id"]))
    return tuple(compiled)


def make_filename_pattern(
        catalogue: Mapping[str, Any] | None = None) -> Callable[[str], str | None]:
    """P5's required `filename_pattern(filename) -> str | None`.

    **Returns the CAPTURE, never the `pattern_label`.** Catalogue 04 leaves the choice
    open as `unc-return-value` and names the two readings; this deployment takes the
    one the catalogue itself calls "the safer reading of P4's RAW rules", because P5
    writes `emit(zone="filename", raw=matched)` and `matched` therefore becomes the
    observation's `raw_value`. P4 RAW-1 makes `raw_value` the source substring. The
    label is the deployment's prose ABOUT the file; putting it in `raw_value` would
    place this module's words into the evidence table as though the file had said
    them. `unc-return-value` stays open for the owner -- this records which way it was
    resolved and why, and nothing else in the catalogue changes either way.

    **A convention is a weak signal by construction.** P5 emits the result at
    `reliability: possible` with NO `signal_tier` -- §2.6's tier table lists camera
    EXIF, capture time, GPS, sensor-shaped dimensions, exact display resolutions, PNG
    format and software metadata, and filenames appear in none of the three bands. So
    a name can never outrank what the image itself says.
    """
    compiled = compile_filename_patterns(
        catalogue if catalogue is not None else load_capture_catalogue(
            "camera_filename_patterns"))

    def filename_pattern(filename: str) -> str | None:
        stem = unicodedata.normalize("NFC", _stem(filename))
        for pattern, capture, _ in compiled:
            found = pattern.match(stem)
            if found is not None:
                return found.group(capture)
        return None

    return filename_pattern


# ======================================================================================
# Catalogues 02 and 03 -- the two readings of the pixel dimensions
# ======================================================================================


def _pair(value: str, separator: str) -> tuple[int, int]:
    left, right = value.split(separator)
    return (int(left), int(right))


def make_dimension_signal(
        resolutions: Mapping[str, Any] | None = None,
        ratios: Mapping[str, Any] | None = None, *,
        tolerance: float) -> Callable[[int, int], str | None]:
    """P5's required `dimension_signal(width, height) -> str | None`.

    Catalogue 02's `arbitration_with_catalogue_03`, in its own order:

    1. the sorted pair matches a display resolution EXACTLY -> `"exact display
       resolution"` (tier 3). §2.6's word is "exact", so there is no tolerance band
       here at all: `1919x1080` matches nothing.
    2. else the reduced ratio matches a sensor shape within `tolerance` ->
       `"sensor-shaped dimensions"` (tier 2).
    3. else `None` -- the dimensions observation is emitted with no `signal_tier`.

    **Why exact wins.** Every 16:9 display resolution is also 16:9, so ratio-first
    would make catalogue 02 unreachable for its commonest members. Nothing is lost: a
    photograph that happens to be exactly 1920x1080 still carries camera EXIF, which
    is tier 1, and §3.7's margin rule weighs tier 1 against tier 3. If the EXIF was
    stripped the file carries one lone tier-3 signal -- which §2.6 says *may* support
    a screenshot hypothesis and which on its own must not clear the margin. That
    abstention is P6's ranking, not a decision taken inside this function.

    The two names are `extractors.image.DIMENSION_SIGNALS` and this function invents
    neither: `extract_image` raises `UnknownSignal` on a third.
    """
    from extractors.image import DIMENSION_SIGNALS
    sensor_shaped, exact_display = DIMENSION_SIGNALS

    resolutions = (resolutions if resolutions is not None
                   else load_capture_catalogue("screen_resolutions"))
    ratios = ratios if ratios is not None else load_capture_catalogue("sensor_aspect_ratios")

    panels = set()
    for row in resolutions["entries"]:
        _check_provenance(row, row["match"])
        width, height = _pair(row["match"], "x")
        panels.add((max(width, height), min(width, height)))

    shapes = []
    for row in ratios["entries"]:
        _check_provenance(row, row["match"])
        longer, shorter = _pair(row["match"], ":")
        shapes.append(((longer, shorter), longer / shorter))

    def dimension_signal(width: int, height: int) -> str | None:
        if width <= 0 or height <= 0:
            return None
        pair = (max(width, height), min(width, height))
        if pair in panels:
            return exact_display
        divisor = gcd(*pair)
        reduced = (pair[0] // divisor, pair[1] // divisor)
        measured = pair[0] / pair[1]
        for shape, nominal in shapes:
            # Exact reduction first -- most sensors reduce cleanly -- then the
            # numeric band, which is the only thing that reaches the Pixel-class
            # 4080x3072 at 0.39 % off nominal 4:3.
            if reduced == shape:
                return sensor_shaped
            if abs(measured - nominal) / nominal <= tolerance:
                return sensor_shaped
        return None

    return dimension_signal


# ======================================================================================
# Catalogue 01 -- the producer strings P6 suppresses
# ======================================================================================


def _boundary_characters(catalogue: Mapping[str, Any]) -> frozenset[str]:
    """The set catalogue 01 states, read off the row it states it in.

    Written as a backticked list because the catalogue's `boundary_rule` is prose:
    the file is the source of truth for WHICH characters, and this reads them rather
    than re-typing them into a constant that could drift.
    """
    return frozenset(part.strip("`").replace("\\t", "\t")
                     for part in catalogue["boundary_characters"].split(", "))


def compile_producer_strings(
        catalogue: Mapping[str, Any]) -> tuple[Callable[[str], bool], ...]:
    """One predicate per row, compiled where `facts.discount` says compiling belongs.

    "`tool_producer_strings` is a collection of compiled predicates, one per catalogue
    entry, because the catalogue declares three `match_kind`s whose semantics (the
    boundary-character set, the version-tail rule) live in its `boundary_rule` field
    as prose with no machine-readable form; compiling belongs with the loader."

    Comparison applies Unicode NFC and strips surrounding whitespace, FOR COMPARISON
    ONLY -- P4 RAW-1/RAW-2 keep the stored `raw_value` byte-for-byte untouched.
    """
    boundary = _boundary_characters(catalogue) if "boundary_characters" in catalogue \
        else frozenset()
    predicates: list[Callable[[str], bool]] = []
    for row in catalogue["entries"]:
        kind = row["match_kind"]
        literal = row.get("pattern") or row["match"]
        _check_provenance(row, literal)
        if kind == "regex":
            flags = 0 if row["case_sensitive"] else re.IGNORECASE
            predicates.append(_regex_predicate(re.compile(literal, flags)))
        elif kind == "exact":
            predicates.append(_exact_predicate(literal, row["case_sensitive"]))
        elif kind == "prefix":
            predicates.append(_prefix_predicate(
                literal, row["case_sensitive"], boundary,
                any_tail=row.get("tail_required") == "any"))
        else:
            raise CatalogueRequired(
                f"{row['id']!r} declares match_kind {kind!r}; catalogue 01 declares "
                "exactly `exact`, `prefix` and `regex`")
    return tuple(predicates)


def _for_comparison(value: str) -> str:
    return unicodedata.normalize("NFC", value).strip()


def _regex_predicate(pattern: re.Pattern[str]) -> Callable[[str], bool]:
    return lambda value: pattern.search(_for_comparison(value)) is not None


def _exact_predicate(literal: str, case_sensitive: bool) -> Callable[[str], bool]:
    def matches(value: str) -> bool:
        candidate = _for_comparison(value)
        if case_sensitive:
            return candidate == literal
        return candidate.casefold() == literal.casefold()
    return matches


def _prefix_predicate(literal: str, case_sensitive: bool,
                      boundary: frozenset[str], *,
                      any_tail: bool) -> Callable[[str], bool]:
    """Catalogue 01's `boundary_rule`, and the defect it was written against.

    Naive prefix matching made `Microsoft Word` claim `Microsoft Word skills
    certificate` -- 68 rows affected. A prefix fires only when the value EQUALS it,
    or begins with it followed by a boundary character that is never a letter or a
    digit, and a remainder holding at least one ASCII digit. `tail_required: "any"`
    drops the digit requirement; one row sets it and carries its own analysis.
    """
    def matches(value: str) -> bool:
        candidate = _for_comparison(value)
        haystack = candidate if case_sensitive else candidate.casefold()
        needle = literal if case_sensitive else literal.casefold()
        if haystack == needle:
            return True
        if not haystack.startswith(needle):
            return False
        rest = candidate[len(literal):]
        if not rest or rest[0] not in boundary:
            return False
        return True if any_tail else any(character.isdigit() for character in rest)
    return matches


@lru_cache(maxsize=1)
def make_tool_producer_strings() -> tuple[Callable[[str], bool], ...]:
    """The `MetadataScreen`'s first half, compiled from the shipped catalogue."""
    return compile_producer_strings(load_capture_catalogue("tool_producer_strings"))


@lru_cache(maxsize=1)
def metadata_property_names() -> tuple[str, ...]:
    """The `MetadataScreen`'s second half: FLAT, in the catalogue's own order.

    `facts.discount`: "the catalogue groups the names by format family, and consuming
    that mapping here would be a lookup keyed by format -- the branching §2.8 exists
    to prevent." The flattening happened at the lift; this reads the result.
    """
    return tuple(load_capture_catalogue("tool_producer_strings")["property_names"])
