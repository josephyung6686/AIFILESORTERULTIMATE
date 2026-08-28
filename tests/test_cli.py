# tests/test_cli.py
"""The command a person actually types.

`--situation` and `--label` are required on a real run and that is deliberate:
nothing upstream can answer them and the command will not guess. But a flag whose
whole purpose is to tell you what to pass to `--situation` cannot itself require
`--situation`, or there is no way in.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cli  # noqa: E402


def _run(argv):
    out = io.StringIO()
    code = cli.main(argv, out=out)
    return code, out.getvalue()


def test_listing_the_situations_needs_nothing_else():
    """The discovery flag is reachable without the answer it exists to supply.

    `--list-situations` prints what `--situation` accepts. Requiring `--situation`
    to reach it is a closed door: the only way to learn a situation name would be
    to already know one.
    """
    code, printed = _run(["--list-situations"])

    assert code == 0, printed
    lines = [line for line in printed.splitlines() if line.strip()]
    assert lines, "the shipped library carries situations and none were printed"
    assert "academic.coursework" in lines, lines[:20]
    # Printed for a human to copy into `--situation`, so no internal prefix.
    assert not [line for line in lines if line.startswith("recognition:")]


def test_a_real_run_still_refuses_to_guess_the_situation():
    """The negative twin. Making the discovery flag reachable must not make the
    two required answers optional on a run that actually designs a tree -- that
    is the whole reason they are required."""
    for argv in (["somewhere"],
                 ["somewhere", "--situation", "academic.coursework"],
                 ["somewhere", "--label", "Coursework"]):
        with pytest.raises(SystemExit) as exited:
            cli.main(argv, out=io.StringIO())
        assert exited.value.code == 2, argv


def test_a_file_the_detector_declines_is_not_written_up_as_a_passport():
    """An unreadable scan and a passport are different things and must stay so.

    This deployment once answered the detector's abstention with
    `highly_sensitive_credential_bearing, protected=True`, as a workaround for
    `placement.privacy` refusing the whole corpus run over one unclassified file.
    That refusal is fixed -- P11 reads P7's own `resolve_class(None)` -- so the
    workaround now only collapses the two: every file the detector declined to
    guess about would enter P7's store indistinguishable from a passport, and
    the honest `unreadable_unclassified` path would be unreachable from the CLI.

    `00`: "sensitive personal material is not the same thing as `Numbers.app`."
    """
    # A real P4 observation key: `sha256:` plus 64 hex. The record validates the
    # shape, so a placeholder would fail this test for the wrong reason.
    key = "sha256:" + "ab" * 32

    classify = cli.classifier(lambda conn, f, c: None,
                              now=lambda: "2026-01-01T00:00:00Z")

    class _Conn:
        def execute(self, *_a):
            class _Cur:
                def fetchone(_self):
                    return {"observation_key": key}
            return _Cur()

    record = classify(_Conn(), "file-1", "sha256:abc")
    assert record is None, (
        "the detector declined and the CLI invented a classification for it: "
        f"{record}. An unclassified file must reach P11 unclassified so P7's "
        "own resolve_class(None) decides, not this deployment.")


def test_a_file_the_detector_does_recognise_still_gets_its_candidate():
    """The negative twin. Returning None for everything would pass the test above
    and disable classification entirely."""
    sentinel = object()
    classify = cli.classifier(lambda conn, f, c: sentinel,
                              now=lambda: "2026-01-01T00:00:00Z")
    assert classify(None, "file-1", "sha256:abc") is sentinel


def test_the_help_says_nothing_is_moved(capsys):
    """`00`'s promise, in the first sentence a person reads. This command reads and
    proposes; P12 is what moves files and P12 does not exist, so a help text that
    left this out would be describing a product that does not ship."""
    with pytest.raises(SystemExit):
        cli.main(["--help"], out=io.StringIO())
    assert "Nothing is moved" in capsys.readouterr().out
