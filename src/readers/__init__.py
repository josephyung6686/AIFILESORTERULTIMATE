# src/readers/__init__.py
"""The deployment layer — real libraries filling P5's injected reader shapes.

**Not a part.** It owns no design section, publishes no vocabulary and adds no table.
`src/extractors/` is stdlib-only on purpose: P5's SPEC says *"P5 adds no third-party
runtime dependency"* and that every format reader is *"a caller-supplied callable"*,
because naming a library inside P5 would bind the evidence shape to it. §2.9 puts the
MIME/signature mapping in the reader and the same reasoning covers every library.

So this package is where the choice actually gets made. It depends on
`src/extractors/` for the SHAPES it must fill — that dependency is the point — and
`src/extractors/` must never depend on this. A guard test asserts that direction.

**What an adapter may decide:** anything the library knows. A heading style, a table
cell, a footer, the PDF date syntax, an OCR provider's own name and version.
**What it may not decide:** anything the product means. No source type, no
completeness, no analysis tier, no field name, no reliability. Those are P4's and
P5's vocabularies, and an adapter spelling one is a second home for it.

Install with `pip install -e '.[readers]'`.
"""
