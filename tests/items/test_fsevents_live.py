"""P1 live FSEvents availability + PathWatcher backend switch."""
from __future__ import annotations

from pathlib import Path

from items.fsevents_live import fsevents_available
from items.path_watch import PathWatcher


def test_path_watcher_reports_backend(tmp_path: Path):
    w = PathWatcher(root=tmp_path)
    assert w.backend == "polling"
    started = w.start_live()
    if fsevents_available():
        assert started is True
        assert w.backend == "fsevents"
        w.stop_live()
        assert w.backend == "polling"
    else:
        assert started is False
        assert w.backend == "polling"
