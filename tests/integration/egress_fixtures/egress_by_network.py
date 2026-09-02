# tests/integration/egress_fixtures/egress_by_network.py
"""A part that grew its own way out, skipping the `ModelClient` contract entirely.

No client, no flag, no `.invoke`: rules A and B never see this one. It is the shape
a part takes when somebody needs an answer today and the transport is in the way.
"""
from __future__ import annotations


def ask(sentence: str) -> str:
    import openai

    reply = openai.OpenAI(api_key="", base_url="").chat.completions.create(
        model="", messages=[{"role": "user", "content": sentence}])
    return reply.choices[0].message.content
