# src/extractors/entities.py
"""The local entity pass -- `00` Amendments of 2026-09-11, item 7(b).

> "a small local entity encoder (GLiNER-class, ONNX, on the same seam as the
> semantic encoder) names people, diagnoses, dates of birth and identity numbers
> as observations, and a person beside a diagnosis or an identity number holds the
> file without a model call."

This is the half that writes the observations. THE HOLD IS NOT HERE: which
combination of entities holds a file is `recognition/detector.py`'s rule and
another author's, and nothing in this module decides anything about a file.

============================================================================
THE CONTRACT, for the rule that reads these rows
============================================================================

`extractor_name`   `entities.` + the label with every run of non-alphanumeric
                   characters folded to one underscore, lowercased. The eleven the
                   deployment ships (`cli.ENTITY_LABELS`) are therefore
                   `entities.person`, `entities.date_of_birth`,
                   `entities.identity_document_number`,
                   `entities.passport_number`, `entities.account_number`,
                   `entities.medical_record_number`, `entities.medical_condition`,
                   `entities.phone_number`, `entities.email_address`,
                   `entities.home_address`, `entities.organization` -- the last
                   spelled the way the model was trained, because the label is what
                   is put TO the model and a respelling is an unmeasured prompt. The
                   PREFIX is the contract and the label set is the deployment's, so a
                   rule written against `entities.` keeps working when the deployment
                   adds a kind.

`extractor_version` this module's `VERSION`. It moves when what the pass emits
                   changes, under `104` R-164's rule.

`raw_value`        FOR A NAMED THING -- a person, an organisation, a diagnosis, a
                   date of birth, an address, an email -- exactly the characters
                   the model spanned, and RAW-1 holds: `raw_value` IS the substring
                   of the stored text unit at `location.text_span`.

                   FOR A NUMBER -- whatever the deployment lists in
                   `masked_labels`: an identity document number, a passport number,
                   an account number, a medical record number, a phone number --
                   ONLY THE LAST `tail_kept` CHARACTERS, and the span is narrowed to
                   cover exactly those characters. The leading characters are never
                   written anywhere: not to `raw_value`, not to `normalized_value`,
                   not to the context fields, which are left empty for these rows
                   for that reason. So a passport number `N2938471` is recorded as
                   `8471` at the span covering `8471`, and RAW-1 still holds --
                   which is the point of narrowing the span rather than prefixing a
                   mask glyph: a reading whose `raw_value` is not the substring at
                   its own span fails `check_span_anchor` and is a citation that
                   cannot resolve. A number no longer than `tail_kept` is recorded
                   whole, because its tail IS the whole of it and dropping the
                   reading would lose the one thing the rule needs -- that a number
                   of that kind is present.

`location`         The HOST reading's zone and container path, with a `text_span`
                   into the stored unit at that path. Rule 10 holds by construction
                   (below).

`confidence`       The model's sigmoid score for that span and that label, as it
                   came. §3.13 says confidence is not comparable across extractors
                   and P4 asserts no range, so this is stored and not rescaled. The
                   floor a reading had to clear to exist at all is the deployment's
                   (`cli.ENTITY_SCORE_FLOOR`).

`reliability`      `possible`, never `direct`. §2.8: model output is not proof, and
                   P4 D11 leaves an extractor those two words only.

============================================================================
WHY THESE READINGS RIDE ON THE HOST'S RUN
============================================================================

A reading with a `text_span` needs a stored text unit at exactly its container path
ON ITS OWN RUN (conformance rule 10), and its `raw_value` must be the substring
there (RAW-1, rule 5). A pass that opened its own run would have to copy every unit
it read into that run to satisfy them -- the whole corpus stored twice, and "a
second materialisation locus" is the thing `recognition/detector.py` and
`tests/p7/test_p7_no_invention.py` refuse repo-wide.

So this mints onto the run the text already belongs to, which is
`evidence_shape.store.line_reading_for`'s precedent exactly (`104` R-135): a NEW
reading built with `dataclasses.replace` from the host, carrying the host's
`run_id`, `file_id`, `content_hash`, `source_type`, zone and container path, and
its own extractor name, value, span, confidence and time. Nothing about the host
reading changes.

**WHICH READINGS ARE HOSTS, and how rule 10 is proved without reading a unit.** A
host is a reading of this file version that carries NO span and whose `raw_value`
is exactly as long as the stored unit standing at its own container path -- that is
to say, the reading that stands over the whole of a unit, which is the shape every
text extractor emits for a page, a paragraph, a cell or a whole short document.
`evidence_shape.store.unit_length_for_observation` answers the length in SQL
without bringing the text across, so this module binds no P4 text materialiser and
the L2 guard stays true. The equality is the proof: if the host's value is the
whole unit, then an offset into the host's value is the same offset into the unit,
and `raw_value = host.raw_value[start:end]` is the substring at that span by
arithmetic rather than by trust. A reading with a span of its own is skipped -- it
is a substring of a unit some host already offers, and reading it again would ask
the model the same question twice. A reading with no unit at its path (§2.8's EXIF
field, a language marker) is skipped: a span there would dangle.

**A SUPERSEDED HOST IS STILL A HOST, and the agreement is deliberate.** §8.2's own
example is a garbled OCR pass followed by a recovered one, and both rows remain
available; `recognition.semantic.evidence_text` filters `superseded_by IS NULL` and
`facts.evidence.observations_for_version` -- which every fact-layer consumer reads
through -- does not. This follows the fact layer, because that is where these
readings are consumed and one rule with two spellings is this project's costliest
defect. What it costs is one more read of a superseded unit's text and readings
minted onto a superseded run; what it does not cost is duplicate rows, because the
`observation_key` a reading is deduplicated on carries no `run_id`.

**WHAT THE MODEL IS SHOWN: THE WHOLE OF A FILE VERSION, TO A CEILING.** The zones
are the semantic path's (`cli.SEMANTIC_ZONES`) and the budget is this path's own
(`cli.ENTITY_CHAR_BUDGET`), both injected. The budgets differ because the questions
do: a vector of a document's opening IS the vector, and this asks whether a file
names a person or a diagnosis ANYWHERE in it -- `104` §18.56's four released health
forms are what the opening alone bought. `readers.entities_gliner` windows what it
is handed, so a unit longer than the encoder's sequence length is read end to end.
Zone order is spend order, exactly as `recognition.semantic.evidence_text` spends
it, so a file over the ceiling spends it on its headings and its opening pages.

**THE SESSION IS A PHASE, NOT A RESIDENT.** The fp32 weights hold 2.36 GB
resident and the local language model wants the rest of the machine. So the caller
loads the reader, runs this pass over the whole corpus, and drops it before the
model phase begins; this module keeps no module-level cache and holds no reference
to the reader after `record_entity_readings` returns.
"""
from __future__ import annotations

import sqlite3
from dataclasses import replace
from typing import Callable, Iterable, Sequence

from evidence_shape.location import Location, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.store import (
    is_derived_extractor, observations_by_key, observations_for_file,
    record_observation, unit_length_for_observation,
)

#: The namespace every reading this pass writes sits in, and the whole of what a
#: consumer needs to know to find them. A convention rather than a list, for
#: `evidence_shape.store.DERIVED_NAMESPACE`'s reason: a deployment that adds a
#: twelfth label needs no edit anywhere else.
ENTITY_NAMESPACE: str = "entities."

#: This producer's version. `observation_key` does NOT hash it (MINOR 8), so a bump
#: re-reads the same corpus into the same handles; §3.4's cache key DOES read it off
#: the readings a call carries, so a changed pass re-asks the questions that rested
#: on its output.
VERSION: str = "0.1.0"

#: An extractor writes two of §3.13's six words and model output is not one of them
#: (§2.8, P4 D11).
RELIABILITY: str = "possible"


class UnreadableLabel(ValueError):
    """A label that slugs to nothing, so its readings would have no name."""


def label_slug(label: str) -> str:
    """`date of birth` -> `date_of_birth`. The whole of the naming rule.

    Written out rather than as a regular expression because
    `tests/p5/test_p5_no_invention.py` holds P5 to ONE pattern -- P4 D8's mechanical
    repair -- and a naming rule is not a reading rule. ASCII letters and digits
    survive; every other run of characters becomes one underscore.
    """
    parts: list[str] = []
    word: list[str] = []
    for character in label.lower():
        if character.isascii() and character.isalnum():
            word.append(character)
        elif word:
            parts.append("".join(word))
            word = []
    if word:
        parts.append("".join(word))
    slug = "_".join(parts)
    if not slug:
        raise UnreadableLabel(
            f"{label!r} has no alphanumeric characters, so `entities.` plus it is "
            f"not a name a rule could match")
    return slug


def extractor_name_for(label: str) -> str:
    """The `extractor_name` every reading of this label carries."""
    return ENTITY_NAMESPACE + label_slug(label)


def is_entity_extractor(extractor_name: str) -> bool:
    """Whether a reading came from this pass. The row-level spelling of the prefix."""
    return extractor_name.startswith(ENTITY_NAMESPACE)


def host_readings(conn: sqlite3.Connection, file_id: str, content_hash: str, *,
                  zones: Sequence[str], char_budget: int
                  ) -> tuple[tuple[Observation, str], ...]:
    """The units of one file version, as `(whole-unit reading, text to read)` pairs.

    Zone order is spend order and the budget is spent across units, not per unit:
    the last unit that fits is cut at the remaining room and the ones after it are
    not read. Within a zone the order is P4's own insertion order, which is the
    order the document was extracted in, so a truncation keeps the front of the
    document rather than whichever page happened to be written first.
    """
    if not isinstance(char_budget, int) or isinstance(char_budget, bool) \
            or char_budget <= 0:
        raise ValueError("char_budget is a positive count of characters")
    ranked = {zone: order for order, zone in enumerate(zones)}
    candidates: list[tuple[int, int, Observation]] = []
    for order, reading in enumerate(observations_for_file(conn, file_id)):
        if reading.content_hash != content_hash:
            continue
        if reading.location.text_span is not None:
            continue
        if is_derived_extractor(reading.extractor_name):
            continue
        if is_entity_extractor(reading.extractor_name):
            continue
        rank = ranked.get(reading.zone)
        if rank is None or not reading.raw_value.strip():
            continue
        candidates.append((rank, order, reading))

    spent = 0
    chosen: list[tuple[Observation, str]] = []
    for _rank, _order, reading in sorted(candidates, key=lambda row: row[:2]):
        room = char_budget - spent
        if room <= 0:
            break
        if unit_length_for_observation(conn, reading) != len(reading.raw_value):
            # Either no unit stands at this path, or the reading is not the whole of
            # the one that does. Both make an offset into `raw_value` an offset into
            # something else, and a span that means something else is worse than no
            # span at all.
            continue
        chosen.append((reading, reading.raw_value[:room]))
        spent += min(len(reading.raw_value), room)
    return tuple(chosen)


def entity_readings(host: Observation, found: Iterable, *, now: str,
                    masked_labels: Sequence[str], tail_kept: int
                    ) -> tuple[Observation, ...]:
    """One host reading and what the model found in it, as conforming readings.

    Pure: it opens nothing and writes nothing, so the masking rule and the span
    arithmetic are checkable without a database or a model.
    """
    if not isinstance(tail_kept, int) or isinstance(tail_kept, bool) or tail_kept < 1:
        raise ValueError(
            "tail_kept is a positive count of characters -- how much of a number the "
            "deployment is willing to record. Zero would leave an empty raw_value, "
            "which P4 refuses, and the refusal would arrive per file rather than here")
    masked = {label_slug(label) for label in masked_labels}
    minted: list[Observation] = []
    for entity in found:
        slug = label_slug(entity.label)
        whole_start, end = int(entity.start), int(entity.end)
        start = whole_start
        if slug in masked:
            # THE TAIL, AND THE SPAN NARROWED TO IT. See the contract above: a mask
            # glyph in `raw_value` would break RAW-1 against the stored unit, so the
            # characters that are not recorded are not spanned either.
            start = max(whole_start, end - tail_kept)
        value = entity.text[start - whole_start:end - whole_start]
        if not value:
            continue
        minted.append(replace(
            host,
            extractor_name=ENTITY_NAMESPACE + slug,
            extractor_version=VERSION,
            raw_value=value,
            location=Location(host.location.zone, host.location.container_path,
                              text_span=TextSpan(start, end)),
            # No normalized value and no context: for a number, the characters this
            # pass declined to record must not reappear in a neighbouring field, and
            # a rule that treated one kind's context as present and another's as
            # absent would be reading the mask as a signal.
            normalized_value=None,
            context_before=None,
            context_after=None,
            context_truncated=False,
            occurrence_count=1,
            observed_at=now,
            reliability=RELIABILITY,
            confidence=float(entity.score),
            signal_tier=None,
        ))
    return tuple(minted)


def record_entity_readings(conn: sqlite3.Connection, *,
                           file_versions: Sequence[tuple[str, str]],
                           entities: Callable[[str], Iterable],
                           zones: Sequence[str], char_budget: int,
                           masked_labels: Sequence[str], tail_kept: int,
                           now: str) -> tuple[str, ...]:
    """Read every named file version's stored units and record what the model names.

    A CORPUS producer, run once with the reader loaded, like
    `facts.anchor_statements.record_anchor_statements`: the session is expensive to
    build and this pass exists to be the only thing that holds it.

    `entities` is the injected reader -- `readers.entities_gliner.GlinerEntities`'s
    `entities` method in the shipped deployment, and anything returning objects with
    `label`, `start`, `end`, `score` and `text` in a pin. This module names no model,
    no label and no floor.

    Idempotent, so a re-scan of an unchanged corpus writes nothing twice: a reading
    is skipped when its `observation_key` -- content hash, extractor name, locator
    and value -- is already in the database. `record_observation` deduplicates
    nothing on its own and `line_reading_for`'s docstring says so ("recording it
    twice is one row if the caller checks first"); this is the caller checking.

    Returns the ids of the rows written, in the order they were written.
    """
    written: list[str] = []
    for file_id, content_hash in sorted(set(file_versions)):
        for host, text in host_readings(conn, file_id, content_hash,
                                        zones=zones, char_budget=char_budget):
            for reading in entity_readings(
                    host, entities(text), now=now,
                    masked_labels=masked_labels, tail_kept=tail_kept):
                if observations_by_key(conn, reading.observation_key):
                    continue
                written.append(record_observation(conn, reading))
    return tuple(written)
