"""Native watcher lifecycle cleanup for item tests."""
from __future__ import annotations

import pytest

from items.path_watch import PathWatcher


@pytest.fixture(autouse=True)
def close_native_watchers():
    PathWatcher._lifecycle_registry = []
    yield
    # Every test gets a deterministic owner boundary. Native watchdog threads
    # must be stopped before the next test touches SQLite or the interpreter's
    # C extension teardown can race the next test.
    for watcher in list(PathWatcher._lifecycle_registry):
        watcher.close()
    PathWatcher._lifecycle_registry.clear()
    PathWatcher._lifecycle_registry = None
