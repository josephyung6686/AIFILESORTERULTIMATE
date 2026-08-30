"""P12 test package.

`tests/` carries no top-level `__init__.py`, so pytest puts each test directory on
`sys.path`. This file makes `tests/p12/conftest.py` importable as `p12.conftest`
rather than as the top-level module `conftest`, the way `tests/p11/__init__.py`
does for P11. Without it a second `conftest` shadows the first in `sys.modules`
and a bare `from conftest import ...` silently resolves against the wrong file.
"""
