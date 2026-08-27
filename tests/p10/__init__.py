"""P10 test package.

`tests/` carries no top-level `__init__.py`, so pytest puts each test directory on
`sys.path`. This file makes `tests/p10/p9_fixtures.py` importable as
`p10.p9_fixtures` rather than as the top-level module `p9_fixtures`, the way
`tests/p9/__init__.py` does for P9.
"""
