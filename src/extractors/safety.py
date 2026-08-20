# src/extractors/safety.py
"""The one gate every extractor passes through. Two rules, no override path.

11-ops-runtime.md section 4b (ratified 2026-08-20): "An application bundle, a macOS
package, and anything under a system location is a protected container... P12 never
moves one, and no policy, approval, or user gesture makes it movable - this is not a
default that review can override, which is what separates it from every other refusal
in this design." What is recorded is the container, not its contents.

11-ops-runtime.md section 5: "Do not materialize, hash, or extract." A dataless
iCloud item's bytes are not on this machine and OPENING it downloads it.

Both detections belong to P3 (its SPEC authors the protected set; 11 section 5 assigns
dataless detection to P3 "before hashing"), so both arrive here as caller-supplied
predicates. O5's reasoning applies verbatim: a second derivation of a value another
part computes is a contract violation, not an optimization, because the two would
drift. This module therefore reads no bytes, no stat result and no platform constant.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

#: P3's word, quoted rather than coined. A statement about the product's restraint,
#: not about the file.
UNTOUCHED_PROTECTED = "untouched_protected"


class ProtectedContainerRefused(Exception):
    """11 section 4b. There is no argument that turns this off."""


class DatalessRefused(Exception):
    """11 section 5. The bytes are not on this machine; reading would download them."""


@dataclass(frozen=True)
class SafetyPolicy:
    """P3's two verdicts, as P5 consumes them.

    Two fields, and deliberately no third: a `force`, `override` or `approved` field
    would be the override 11 section 4b says does not exist.
    """
    is_protected_container: Callable[[Path], bool]
    is_dataless: Callable[[Path], bool]


def admit(path: Path, *, policy: SafetyPolicy) -> None:
    """Raise if this path may not be read at all. Otherwise return None.

    Called as the FIRST statement of every extractor, before its reader is touched,
    so that "no extractor is reachable for a path inside a protected container" is a
    property of the extractor rather than of one of its callers.

    The protected check runs first: inside a protected container P5 must not even ask
    a question about the file, because asking is a stat of its contents.
    """
    if policy.is_protected_container(path):
        raise ProtectedContainerRefused(
            f"{path} is inside a protected container and is recorded as "
            f"{UNTOUCHED_PROTECTED}; its contents are never entered "
            "(11-ops-runtime.md section 4b). There is no override."
        )
    if policy.is_dataless(path):
        raise DatalessRefused(
            f"{path} is a dataless (not-downloaded) item; reading it would download "
            "it (11-ops-runtime.md section 5). P5 writes no run row for it, and "
            "which completeness such a file carries is P4 Open question 6."
        )
    return None
