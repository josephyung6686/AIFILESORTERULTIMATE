"""P9 test package.

`tests/` carries no top-level `__init__.py`, so pytest puts each test directory on
`sys.path`. This file makes `tests/p9/conftest.py` importable as `p9.conftest`
rather than as the top-level module `conftest`, the way `tests/p8/__init__.py` does
for P8.
"""
