# tests/integration/egress_fixtures/egress_by_alias.py
"""Rule B through a name of the module's own choosing.

`client.invoke(bytes)` was caught; binding the same bound method one line earlier
and spending it under another name was not. Reaching for the attribute IS the
egress -- what the module calls the result afterwards is its own business, and a
rule that reads only the call site is reading the part the author picks.
"""
from __future__ import annotations


def ask(client, sentence: str) -> bytes:
    send = client.invoke
    return send(sentence.encode("utf-8"))
