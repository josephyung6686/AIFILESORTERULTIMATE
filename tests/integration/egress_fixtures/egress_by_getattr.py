# tests/integration/egress_fixtures/egress_by_getattr.py
"""Rule B with the attribute name moved into a string, where the AST is not looking.

`getattr(client, "invoke")` builds no `ast.Attribute` at all, and neither does
`operator.methodcaller("invoke")` or a dispatch table keyed on the word. The name
is still spelled in the source; it is spelled as data.
"""
from __future__ import annotations


def ask(client, sentence: str) -> bytes:
    return getattr(client, "invoke")(sentence.encode("utf-8"))
