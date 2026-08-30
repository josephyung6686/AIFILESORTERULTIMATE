"""P12 — apply and undo (§8.3). The only part that mutates the filesystem.

Nothing is re-exported here. Every consumer imports from the module that owns the
name, so that "who publishes this?" has a one-word answer and a moved name breaks
an import rather than silently resolving through a facade.
"""
from __future__ import annotations

__all__: tuple[str, ...] = ()
