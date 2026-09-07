# tools/promptbench/candidates.py
"""The candidate prompts, read from the library manifest and never composed here.

`src/llm_harness/library/drafts_2026-09-06.json` lists every draft the D2
packet puts to the owner: its site, its candidate name, its `template_id`
(which carries `unratified` and the date), the three files a `PromptDefinition`
is built from, and their digests. This module turns one manifest row into a
`PromptDefinition`, refusing a file whose bytes no longer match the manifest --
the same posture `llm_harness.prompt_library` takes for the ratified files.
"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from llm_harness.records import PromptDefinition  # noqa: E402

LIBRARY = _ROOT / "src" / "llm_harness" / "library"
MANIFEST = LIBRARY / "drafts_2026-09-06.json"


class DraftChanged(RuntimeError):
    """A draft file no longer hashes to what the manifest recorded for it."""


@dataclass(frozen=True)
class Candidate:
    site: str
    name: str
    template_id: str
    template_file: str
    response_schema_file: str
    shaping_policy_file: str
    glossary_file: str | None
    note: str
    #: Which stress suite the candidate is measured on (None: the site's own).
    suite: str | None = None
    #: Recognition rows whose `needs_llm` readings ride in a `readings` key, and
    #: the byte layout the bench emulates for them (`canonical` or `frame-first`).
    readings_rows: tuple[str, ...] = ()
    layout: str = "canonical"

    def _read(self, name: str) -> bytes:
        path = LIBRARY / name
        raw = path.read_bytes()
        expected = _manifest()["digests"][name]
        found = hashlib.sha256(raw).hexdigest()
        if found != expected:
            raise DraftChanged(
                f"{path} hashes to {found}; the manifest records {expected}. "
                "A draft's identity is its bytes: re-record the manifest "
                "deliberately or restore the file.")
        return raw

    def prompt(self) -> PromptDefinition:
        return PromptDefinition(
            template_id=self.template_id,
            template_bytes=self._read(self.template_file),
            response_schema_bytes=self._read(self.response_schema_file),
            call_site=self.site,
            call_site_version="1",
            shaping_policy_bytes=self._read(self.shaping_policy_file))

    def response_schema(self) -> dict:
        return json.loads(self._read(self.response_schema_file).decode("utf-8"))

    def glossary_path(self) -> Path | None:
        return None if self.glossary_file is None else LIBRARY / self.glossary_file


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def candidates_for(site: str) -> tuple[Candidate, ...]:
    rows = [row for row in _manifest()["drafts"] if row["site"] == site]
    return tuple(
        Candidate(
            site=row["site"], name=row["candidate"],
            template_id=row["template_id"],
            template_file=row["template_file"],
            response_schema_file=row["response_schema_file"],
            shaping_policy_file=row["shaping_policy_file"],
            glossary_file=row.get("glossary_file"),
            note=row.get("note", ""),
            suite=row.get("suite"),
            readings_rows=tuple(row.get("readings_rows", ())),
            layout=row.get("layout", "canonical"))
        for row in rows
    )


def candidate(site: str, name: str) -> Candidate:
    for item in candidates_for(site):
        if item.name == name:
            return item
    raise KeyError(f"no candidate {name!r} for {site!r} in {MANIFEST}")


def all_candidates() -> tuple[Candidate, ...]:
    return tuple(
        item for row in _manifest()["drafts"]
        for item in candidates_for(row["site"]) if item.name == row["candidate"]
    )


__all__ = ["Candidate", "DraftChanged", "LIBRARY", "MANIFEST", "all_candidates",
           "candidate", "candidates_for"]
