"""Makes this directory a package so its `conftest.py` is imported as `p7.conftest`
and not as the top-level module `conftest`, where it would displace `tests/p5`'s
(which `tests/p5/test_p5_join.py` imports `RecordingSink` from by name). Same reason
`tests/p4/__init__.py`, `tests/p6/__init__.py` and `tests/eval/__init__.py` exist.
"""
