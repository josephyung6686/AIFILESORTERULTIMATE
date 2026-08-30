"""P13 -- the review and approval surface. It presents and collects; it never decides.

Two rules govern every module here (P13 SPEC, "Two rules govern everything below"):

**P13 presents and collects; it never decides.** Every user action is routed to
the owning part as an §8.7 correction carrying its scope. A collected action never
becomes a fact, a verdict, a group, a placement, a tree edit or a filesystem
mutation inside P13.

**P13 renders only what the boundary released.** Redaction happens in the part
that owns the data -- P7's display policy (§8.4). P13 has no code path that
receives protected content and then hides it; it has code paths that decline to
ask for it.

This package is a DATA AND CONTRACT layer. There is no framework, no HTML, no
TUI and no rendering loop. Layout, components, styling, typography, colour,
iconography, interaction patterns and every word of user-facing copy are
DEFERRED by the SPEC's own Deferred table: it fixes the information contract and
fixes no pixel.
"""
from review_surface.schema import REVIEW_TABLES, create_review_schema
from review_surface.vocabulary import (
    ACTIONS,
    PROGRESS_SOURCES,
    PROGRESS_STATES,
    SUBSYSTEM,
    SURFACES,
    VERDICTS,
    OutOfVocabulary,
    check,
)

__all__ = [
    "ACTIONS", "PROGRESS_SOURCES", "PROGRESS_STATES", "REVIEW_TABLES",
    "SUBSYSTEM", "SURFACES", "VERDICTS", "OutOfVocabulary", "check",
    "create_review_schema",
]
