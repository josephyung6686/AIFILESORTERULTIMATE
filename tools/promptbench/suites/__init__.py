# tools/promptbench/suites/__init__.py
"""The stress-case suites, one module per site, looked up by call site."""
from __future__ import annotations

import importlib

from llm_harness.vocabulary import A_FACT, B_GROUP, C_PLACEMENT, D_RESIDUAL, E_TEMPLATE

_MODULES = {
    A_FACT: "tools.promptbench.suites.suite_a",
    B_GROUP: "tools.promptbench.suites.suite_b",
    C_PLACEMENT: "tools.promptbench.suites.suite_c",
    D_RESIDUAL: "tools.promptbench.suites.suite_d",
    E_TEMPLATE: "tools.promptbench.suites.suite_e",
}


def cases_for(site: str):
    if site not in _MODULES:
        raise KeyError(f"no suite for {site!r}; the sites are {sorted(_MODULES)}")
    return tuple(importlib.import_module(_MODULES[site]).CASES)


__all__ = ["cases_for"]
