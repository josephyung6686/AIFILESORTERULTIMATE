# tests/test_cli_detects_extensionless_files.py
"""The nine files on the owner's disk with no extension at all, which read as nothing.

`.groundtruth/baseline/scorecard.txt`, 2026-09-04: `(none)  0 of 9  0.0%`. All nine
recorded `unsupported`, and the reason was mechanical rather than interesting --
`route()` keys on a format token, `detect_format` answered None, and the declared
extension of `LICENSE` is the empty string, which is a key in no table. Nothing ever
tried to read them.

Seven of the nine are named by a convention a tool requires by that exact spelling,
and that convention is what this detector reads. It is the SAME kind of statement as
`readers/text_documents._MARKERS_BY_FILENAME` -- "a statement about those tools and
not a judgement about a project" -- and it lives in `cli.py` because §2.9 puts the
mapping from a real-world signal onto the router's token space in the DEPLOYMENT:
"A real deployment maps libmagic's MIME type or macOS's UTType onto that token space,
and THAT mapping belongs to the reader."

THE OTHER TWO STAY UNSUPPORTED and they are asserted here so that stays visible: a
Google-Fonts stylesheet saved as `css2` and Premiere's `LocateDialog Column Settings`
are named by nothing and sniffing them is not available -- reading bytes to decide a
format would open a file before `is_protected_container` has had its say, and that
guard is by PATH and runs after routing. An honest `unsupported` is the answer.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cli  # noqa: E402
from extractors.router import route  # noqa: E402

HASH = "67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124"


def routed(name: str):
    path = Path("/corpus") / name
    return route(file_id="f1", content_hash=HASH, path=path,
                 extension=path.suffix, detect_format=cli._detect_format)


# --------------------------------------------------------------------------- #
# the seven that are named by a convention
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("name,token", [
    # Every one of these is a real path in `.groundtruth/corpus/`.
    ("LICENSE", "txt"),
    ("NOTICE", "txt"),
    ("AUTHORS", "txt"),
    ("THANKS", "txt"),
    ("LICENSE-CC-BY-NC-SA", "txt"),
    ("Dockerfile", "dockerfile"),
    ("Makefile", "makefile"),
])
def test_a_conventionally_named_extensionless_file_is_detected(name, token):
    assert cli._detect_format(Path("/corpus") / name) == token


@pytest.mark.parametrize("name", ["LICENSE", "NOTICE", "AUTHORS", "THANKS",
                                  "LICENSE-CC-BY-NC-SA", "Dockerfile", "Makefile"])
def test_each_of_the_seven_reaches_an_extractor_instead_of_stopping(name):
    decision = routed(name)
    assert decision.extractor_name == "text.structured"
    assert decision.unrouted_completeness is None
    assert decision.disagree is False, (
        "an absent extension is not a wrong one; recording these as disagreements "
        "would put seven false 'this file is misnamed' rows in extraction_routing")


def test_the_licence_and_notice_files_are_prose_and_the_build_files_are_code():
    """§2.4's own split, kept. A LICENCE is a document a person reads; a Dockerfile
    is a recipe, and §2.4 asks for structural evidence from those "rather than
    forcing semantic analysis to infer a project from arbitrary code text"."""
    assert routed("LICENSE").source_type == "text_document"
    assert routed("NOTICE").source_type == "text_document"
    assert routed("Dockerfile").source_type == "code_structured"
    assert routed("Makefile").source_type == "code_structured"


def test_the_licence_variant_spellings_are_the_same_convention():
    """`LICENSE-CC-BY-NC-SA` is how Creative Commons and the GNU licences are
    conventionally spelled, and one is on this disk. The name before the first
    hyphen is what carries the convention."""
    assert cli._detect_format(Path("/x/LICENSE-CC-BY-NC-SA")) == "txt"
    assert cli._detect_format(Path("/x/LICENSE-APACHE")) == "txt"
    assert cli._detect_format(Path("/x/COPYING-LESSER")) == "txt"


def test_the_convention_is_read_case_insensitively():
    """`license`, `LICENSE` and `License` are one convention and three spellings,
    and a real disk holds all three."""
    for spelling in ("license", "LICENSE", "License", "makefile", "MAKEFILE"):
        assert cli._detect_format(Path("/x") / spelling) is not None, spelling


def test_every_name_in_the_table_has_a_file_behind_it_or_a_reason():
    """The rule `extractors/router.py`'s own additions follow: "nothing is here for
    a language the owner does not write". A table that grew by imagination would
    route files nobody has, and the first speculative entry is the one that makes
    the next reviewer stop checking. Seven were counted on the corpus; the two that
    were not are named here with the reason they are exceptions."""
    counted_on_the_corpus = {"license", "notice", "authors", "thanks",
                             "dockerfile", "makefile"}
    named_for_a_stated_reason = {
        "readme",    # `text_documents._markers_for` already knows it by stem
        "copying",   # the GNU spelling of `license`, in the same trees
    }
    assert set(cli._FORMAT_BY_EXTENSIONLESS_NAME) == (counted_on_the_corpus
                                                      | named_for_a_stated_reason)


# --------------------------------------------------------------------------- #
# the guards
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("name", ["css2", "LocateDialog Column Settings"])
def test_the_two_that_no_convention_names_stay_honestly_unsupported(name):
    """Both are real corpus files and neither is guessable from its name. §2.4:
    "The system should never silently treat an unsupported format as an empty
    document" -- and it does not; it says `unsupported`, which is the truth."""
    assert cli._detect_format(Path("/corpus") / name) is None
    assert routed(name).unrouted_completeness == "unsupported"


def test_a_file_that_HAS_an_extension_is_never_renamed_by_this_table():
    """The table answers for extensionless files only. `license.py` is Python and
    `Makefile.md` is Markdown, and letting a stem override a real extension would
    be the detector overruling the thing §2.9 calls the routing signal."""
    assert cli._detect_format(Path("/x/license.py")) is None
    assert cli._detect_format(Path("/x/Makefile.md")) == "md"
    assert cli._detect_format(Path("/x/notice.pdf")) == "pdf"
    # The hyphen rule is the one with teeth here. `license-loader.py` starts with a
    # word the table knows, and without the `path.suffix` guard the split would hand
    # a Python module back as `txt` -- the detector overruling a real extension on
    # the strength of half a filename.
    assert cli._detect_format(Path("/x/license-loader.py")) is None
    assert cli._detect_format(Path("/x/readme-generator.sh")) is None
    assert cli._detect_format(Path("/x/makefile-helper.js")) is None


def test_the_detector_still_opens_nothing():
    """The reason `css2` cannot be rescued, pinned. `is_protected_container` is a
    PATH judgement made by `admit()`, which runs inside the extractor -- after
    routing. A detector that read bytes to name a format would open a protected
    file before the one guard that exists to stop it, so this one answers from the
    path alone and is handed a path that does not exist to prove it."""
    assert cli._detect_format(Path("/nowhere/at/all/LICENSE")) == "txt"
    assert cli._detect_format(Path("/nowhere/at/all/thing.pdf")) == "pdf"
