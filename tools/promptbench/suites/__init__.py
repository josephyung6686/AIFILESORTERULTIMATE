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


#: Suites a manifest row may name instead of the site's own.
_NAMED = {
    "a_readings": "tools.promptbench.suites.suite_a_readings",
}


def cases_for(site: str, suite: str | None = None):
    if suite is not None:
        if suite not in _NAMED:
            raise KeyError(f"no suite named {suite!r}; the names are {sorted(_NAMED)}")
        return tuple(importlib.import_module(_NAMED[suite]).CASES)
    if site not in _MODULES:
        raise KeyError(f"no suite for {site!r}; the sites are {sorted(_MODULES)}")
    return tuple(importlib.import_module(_MODULES[site]).CASES)


def all_cases_for(site: str):
    """Every case a candidate of this site could have been measured on."""
    cases = list(cases_for(site))
    for name in _NAMED:
        cases.extend(c for c in cases_for(site, name) if c.site == site)
    return tuple(cases)


__all__ = ["all_cases_for", "cases_for"]
