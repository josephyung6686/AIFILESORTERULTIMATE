"""Packaged profile JSON. Loaded by `items.profile_loader`, never by name checks in the detector.

Package data: `*.json` is declared under `[tool.setuptools.package-data]` for
`items.profiles` so an installed wheel ships the profiles `importlib.resources` reads.
"""
