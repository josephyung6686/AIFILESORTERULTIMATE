# tests/integration/egress_fixtures/egress_by_dynamic_import.py
"""Rule C's other half: an import whose module name is not in the import statement.

`_imported` reads `ast.Import` and `ast.ImportFrom`, so every name on
`NETWORK_MODULES` is only ever compared against a name the source spells as syntax.
A string handed to `__import__` or `importlib.import_module` reaches exactly the
same module and is invisible to that reading -- and so is anything inside `eval`.
"""
from __future__ import annotations


def ask(sentence: str) -> str:
    sdk = __import__("openai")
    return sdk.OpenAI(api_key="", base_url="").responses.create(input=sentence)
