"""FSEvents policy: ignore own moves, iCloud placeholders, debounce."""
from __future__ import annotations

from items.fsevents_feed import ChangeFeedPolicy, FsEvent


def test_ignores_own_plan_echo():
    pol = ChangeFeedPolicy(debounce_ms=0)
    pol.note_own_move("/tmp/a.pdf", "/tmp/b.pdf")
    assert pol.accept(FsEvent("/tmp/a.pdf")) is False
    assert pol.accept(FsEvent("/tmp/b.pdf")) is False
    pol.clear_own_move("/tmp/a.pdf", "/tmp/b.pdf")
    assert pol.accept(FsEvent("/tmp/b.pdf")) is True


def test_skips_icloud_placeholder():
    pol = ChangeFeedPolicy(debounce_ms=0)
    assert pol.accept(FsEvent(
        "/Users/x/iCloud/doc.pdf", is_icloud_placeholder=True)) is False


def test_debounce_collapses_bursts():
    pol = ChangeFeedPolicy(debounce_ms=500)
    t0 = 1000.0
    assert pol.accept(FsEvent("/x/a.txt"), now=t0) is True
    assert pol.accept(FsEvent("/x/a.txt"), now=t0 + 0.1) is False
    assert pol.accept(FsEvent("/x/a.txt"), now=t0 + 0.6) is True
