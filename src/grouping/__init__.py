# src/grouping/__init__.py
"""P9 — bounded evidence grouping.

Public surface is narrow by design and grows task by task. P9 owns deterministic
seeds and neighbourhoods, reference-only Site-B dossier construction, and mapping
an accepted P8 result into append-only membership history. It does not call a
model, call `privacy.gate.Gate.release`, validate citations, or define a second
validator vocabulary — those are P8's.

No destination, node, tree, placement or template concept lives in this package.
"""
