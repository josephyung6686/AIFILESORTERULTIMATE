# src/privacy/__init__.py
"""P7 — the privacy and consent gate (§8.4).

The only door through which file content may reach a model or an external connector.
Five handling classes, four operation modes, nine always-local items, six releasable
item kinds, one `Gate.release` with three branches, and a consent-aware audit record
appended before any release is returned.

The package marker re-exports nothing yet: `Gate` and the three decision types arrive
with `gate.py`. `src/evidence_shape/__init__.py` and `src/extractors/__init__.py` are
the same shape, and a marker that imported a module later tasks have not written
would make every task before that one uncollectable.
"""
