"""Makes `tests/p11/` a package so a sibling fixture imports as `p11.<module>`.

`tests/` carries no top-level `__init__.py`, so pytest puts each test directory on
`sys.path`. This file makes `tests/p11/conftest.py` importable as `p11.conftest`
rather than as the top-level module `conftest`, the way `tests/p9/__init__.py` does
for P9 and `tests/p8/__init__.py` does for P8. Without it a second `conftest`
shadows the first in `sys.modules` and a bare `from conftest import ...` silently
resolves against the wrong file (`tests/p1_contract.py:1-7`).
"""
