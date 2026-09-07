# src/llm_harness/prompt_library.py
"""The ratified prompt bytes, read from disk and refused if they have changed.

**This module authors nothing and decides nothing.** It holds one file the owner
ratified and one digest of it, and it hands back the bytes or it raises. It picks
no `template_id`, no `call_site_version`, no tier and no model; those are the
composition root's, and `PromptDefinition` is constructed there and not here.

**Why the bytes are a file and not a string literal.** The prompt's identity IS
its bytes: `PromptDefinition.template_bytes` is hashed into every audit record,
onto every fact row and into every cache key
(`llm_harness.fingerprint.prompt_fingerprint`, `facts.llm_seam.apply_verdict`), so
one changed character is a different prompt whose fingerprint cannot be re-pointed
at the records already written under the old one
(`planning/82-FACT-PROMPT-DRAFT.md` §1, §6.2). Seven kilobytes of prose inside a
Python source file is the one shape in which that change happens quietly: an editor
strips a trailing space, a formatter re-wraps a line, a reviewer scrolls past a
diff nobody can read. A data file next to `library/field_glossary.json` -- which is
the existing home for text that is shown to a model, quoted rather than authored,
and verified by test -- keeps the bytes where a diff over them is legible.

**Why the digest is pinned HERE and not supplied by the caller.** A caller-supplied
digest would be more consistent with the rule that a part holds no values. It is
also quieter: it puts the check in one consumer, and a second consumer that forgot
to pass one would load an edited file happily. Pinned in the package, an edit fails
every consumer at the moment it is read. Loudness is what the ratification needs, so
the digest is here.

A hex digest is not a threshold, a ceiling or a batch size. It is the identity of
the bytes beside it -- the same status as a schema version -- so it is not a policy
this package is choosing on the deployment's behalf.

**A revision is a new file, never an edit to this one.** `82` §6.3: revising the
text strands every record that references the old digest, so the sane form of a
revision is a second file with its own `template_id` alongside this one, and the
old kept readable for the records that point at it. Editing `a_fact_template.txt`
in place is the failure that convention exists to prevent, and the digest below is
what makes the attempt loud rather than silent.
"""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path


#: The A_fact template the owner ratified on 2026-09-02, recorded at
#: `planning/82-FACT-PROMPT-DRAFT.md` §0: `82` §2's text with
#: `planning/90-PROMPT-BAKEOFF.md` C2's one-sentence delta applied.
A_FACT_TEMPLATE_FILE = (
    Path(__file__).resolve().parent / "library" / "a_fact_template.txt")

#: sha256 of the file above, from `90` §3's candidate table (`e4fe6d12...ae10`).
#: 7,349 bytes, 1,242 words. The counts are asserted in the test rather than bound
#: here: the digest already carries them, and a second copy is a second thing to
#: keep true.
A_FACT_TEMPLATE_SHA256: str = (
    "e4fe6d12c27e701ca9e55f51fb4125d68c573659649687fd570c84c790b2ae10")


#: The response schema and the shaping policy the A_fact dossier carries beside the
#: template. `PromptDefinition` refuses an empty one of either
#: (`llm_harness/records.py:89`), and until 2026-09-03 neither existed anywhere in
#: `src/` -- so the ratified template could not be turned into a `PromptDefinition`
#: at all, and the one call site the owner ratified a prompt for could not be built.
#:
#: **THESE TWO ARE NOT RATIFIED AND THIS COMMENT IS WHERE THAT IS SAID.** The
#: template is the owner's, recorded at `planning/82-FACT-PROMPT-DRAFT.md` §0. These
#: are an agent's reading of what that template already asks the model for, written
#: so the ratified text could be used: the schema is `82`'s THE SHAPE and THE RULES
#: in JSON Schema, and the policy is a description of the shaping this deployment
#: actually does, in the terms the template's own paragraph about the dossier uses.
#: Neither adds an instruction the template does not give. Both are model-visible --
#: `dossier._body` writes them into the bytes under `response_schema` and
#: `shaping_policy` -- so they are the owner's to read and to change.
#:
#: They are digest-pinned for the same reason the template is, and NOT because a
#: digest confers ratification: `prompt_fingerprint` hashes both
#: (`llm_harness/fingerprint.py:43`), so one changed character is a different prompt
#: and every fact row already written under the old fingerprint points at text that
#: would no longer exist. The pin makes an edit loud.
#: **THE REVISION, AND IT IS NOT RATIFIED. THIS COMMENT IS WHERE THAT IS SAID.**
#: The module docstring above names the only sane form of a revision -- "a second
#: file with its own `template_id` alongside this one, and the old kept readable for
#: the records that point at it" -- and this is that second file. The ratified bytes
#: above are untouched, still loaded by `a_fact_template_bytes`, and still verified
#: against the digest the owner's text hashes to.
#:
#: What it adds is four lines, and `tests/p8/test_p8_a_fact_prompt_folder_levels.py`
#: re-derives them from the ratified file rather than pinning them by digest alone:
#: `folder_levels` in the key list, `Five` -> `Six`, and two paragraphs saying what
#: that key is. It adds no description of any FIELD -- meanings live in
#: `library/field_glossary.json`, transcribed and never authored -- and the two
#: sentences that keep a `required` level from being filled with a guess are quoted
#: from the ratified text itself: "Declining is a correct answer and it is recorded
#: as one" and "A field you get wrong becomes a permanent property of someone's
#: file."
#:
#: The `template_id` the composition root gives it says `unratified` out loud, so
#: every audit row, fact row and cache key written under it tells the owner that the
#: prompt in force is not one they read. Ratifying it means recording the text and
#: renaming the id, and nothing here may do either.
A_FACT_TEMPLATE_FOLDER_LEVELS_FILE = (
    Path(__file__).resolve().parent / "library"
    / "a_fact_template_folder_levels.txt")

#: sha256 of the file above. 8,020 bytes, 1,359 words.
A_FACT_TEMPLATE_FOLDER_LEVELS_SHA256: str = (
    "102acdaf53a656433548b3b6c3c9c4af3200ba3eca268435f744a5148b32aa41")


A_FACT_RESPONSE_SCHEMA_FILE = (
    Path(__file__).resolve().parent / "library" / "a_fact_response_schema.json")

A_FACT_RESPONSE_SCHEMA_SHA256: str = (
    "3412b6f728374643c8d12453035f9ed00aa0a9e93fb9badb2c2bbea630fa72b4")

A_FACT_SHAPING_POLICY_FILE = (
    Path(__file__).resolve().parent / "library" / "a_fact_shaping_policy.json")

A_FACT_SHAPING_POLICY_SHA256: str = (
    "d0076055bacaac330935f405b089b9fdac4a431239f7a017503fa443ecc15bdb")


class RatifiedTextMissing(RuntimeError):
    """A ratified prompt file is not on disk. This package ships no default text."""


class RatifiedTextChanged(RuntimeError):
    """A ratified prompt file is not the bytes that were ratified."""


def _read(path: Path, expected_sha256: str) -> bytes:
    """The bytes at `path`, or a refusal naming which of the two things went wrong.

    Never a fallback, never a repair, and the contents are never echoed into the
    exception: what a reader needs is which file and which digest, and a 7KB
    message would bury both.
    """
    if not path.is_file():
        raise RatifiedTextMissing(
            f"{path} is not on disk; this package ships no default prompt text")
    raw = path.read_bytes()
    found = hashlib.sha256(raw).hexdigest()
    if found != expected_sha256:
        raise RatifiedTextChanged(
            f"{path} hashes to {found}, and the text ratified for it hashes to "
            f"{expected_sha256}. A prompt's identity is its bytes, and every "
            f"record already written under the ratified digest points at text "
            f"that would no longer exist. A revision is a new file beside this "
            f"one, never an edit to it."
        )
    return raw


@lru_cache(maxsize=1)
def a_fact_template_bytes() -> bytes:
    """The ratified A_fact template, verified against its digest on first read."""
    return _read(A_FACT_TEMPLATE_FILE, A_FACT_TEMPLATE_SHA256)


@lru_cache(maxsize=1)
def a_fact_template_folder_levels_bytes() -> bytes:
    """The revision that describes `folder_levels`, verified against its digest.

    Same loader, same refusal, same reason: a prompt's identity is its bytes.
    """
    return _read(A_FACT_TEMPLATE_FOLDER_LEVELS_FILE,
                 A_FACT_TEMPLATE_FOLDER_LEVELS_SHA256)


@lru_cache(maxsize=1)
def a_fact_response_schema_bytes() -> bytes:
    """The A_fact response schema, verified against its digest on first read."""
    return _read(A_FACT_RESPONSE_SCHEMA_FILE, A_FACT_RESPONSE_SCHEMA_SHA256)


@lru_cache(maxsize=1)
def a_fact_shaping_policy_bytes() -> bytes:
    """The A_fact shaping policy, verified against its digest on first read."""
    return _read(A_FACT_SHAPING_POLICY_FILE, A_FACT_SHAPING_POLICY_SHA256)


# --- the D2 drafts, by id, and NONE of them is ratified -----------------------

#: The manifest `planning/105-D2-PROMPT-PACKET.md` put to the owner. It is an
#: INDEX and not a ratification: its own `status` is `unratified` and every
#: `template_id` in it carries that word, so any record written under one says so
#: on its face.
#:
#: The manifest itself is read as-is and carries the digests that verify the FILES
#: it names. That asymmetry is deliberate and worth stating: a digest of the index
#: would have to live somewhere, and the only somewhere is this file, which would
#: make adding a draft an edit to `src/` -- exactly what `104` §13 wants a packet
#: to avoid. What must not drift is the TEXT a record points at, and that is what
#: `digests` pins.
DRAFTS_FILE = (
    Path(__file__).resolve().parent / "library" / "drafts_2026-09-06.json")


class DraftNotInManifest(RuntimeError):
    """No row in the packet carries this template id."""


class DraftManifestAmbiguous(RuntimeError):
    """Two rows share a template id and disagree about which files it is."""


@lru_cache(maxsize=1)
def _manifest() -> dict:
    if not DRAFTS_FILE.is_file():
        raise RatifiedTextMissing(
            f"{DRAFTS_FILE} is not on disk; this package ships no default "
            f"prompt text, draft or otherwise")
    return json.loads(DRAFTS_FILE.read_text(encoding="utf-8"))


def drafts_status() -> str:
    """The one word the whole packet is under. Read, never assumed.

    `cli.py` prints it in the refusal it raises when an observe-only site is
    pointed at a cloud model, so the sentence a person sees is the manifest's own
    word rather than this module's memory of it.
    """
    status = _manifest().get("status")
    if not isinstance(status, str) or not status.strip():
        raise DraftNotInManifest(
            f"{DRAFTS_FILE} carries no `status`. The packet's status is what says "
            f"whether its text may be sent, and absent means refuse.")
    return status


def draft_row(template_id: str) -> dict:
    """The manifest row for one template id, or a refusal naming what is there.

    TWO ROWS MAY SHARE AN ID and that is not an error by itself: A_fact's
    `ratified-glossary` and `proposed-glossary` are two GLOSSARIES over one
    template, so they name the same text. What is an error is two rows sharing an
    id and disagreeing about which files it is, because then the id does not
    identify bytes and a record written under it points at nothing definite.
    """
    rows = [row for row in _manifest().get("drafts", ())
            if isinstance(row, dict) and row.get("template_id") == template_id]
    if not rows:
        known = sorted({row.get("template_id") for row in
                        _manifest().get("drafts", ()) if isinstance(row, dict)})
        raise DraftNotInManifest(
            f"no draft in {DRAFTS_FILE.name} carries template_id "
            f"{template_id!r}. A prompt is named by its id and this package "
            f"invents none. The ids it holds are {known}.")
    files = {(row.get("template_file"), row.get("response_schema_file"),
              row.get("shaping_policy_file")) for row in rows}
    if len(files) > 1:
        raise DraftManifestAmbiguous(
            f"template_id {template_id!r} appears on {len(rows)} rows naming "
            f"{len(files)} different sets of files: {sorted(files)}. An id that "
            f"does not identify bytes cannot be recorded against a call.")
    return rows[0]


def draft_bytes(template_id: str) -> tuple[bytes, bytes, bytes]:
    """The template, response schema and shaping policy for one draft id.

    Each verified against the manifest's digest by the same `_read` the ratified
    text uses, and for the same reason: a prompt's identity is its bytes, and a
    revision is a new file and a new row rather than an edit to a row a run has
    already recorded.
    """
    row = draft_row(template_id)
    digests = _manifest().get("digests")
    if not isinstance(digests, dict):
        raise DraftNotInManifest(
            f"{DRAFTS_FILE.name} carries no `digests` map, so its text cannot be "
            f"verified and is not read")
    out: list[bytes] = []
    for key in ("template_file", "response_schema_file", "shaping_policy_file"):
        name = row.get(key)
        if not isinstance(name, str) or not name:
            raise DraftNotInManifest(
                f"the row for {template_id!r} names no {key}; a call needs all "
                f"three and a partial prompt is not a smaller prompt")
        if name not in digests:
            raise DraftNotInManifest(
                f"{name} has no digest in {DRAFTS_FILE.name}, so the bytes on "
                f"disk cannot be shown to be the bytes the packet described")
        out.append(_read(DRAFTS_FILE.parent / name, digests[name]))
    return out[0], out[1], out[2]
