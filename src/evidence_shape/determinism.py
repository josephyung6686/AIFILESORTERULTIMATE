# src/evidence_shape/determinism.py
"""Conformance rule 8 -- the compared observation set.

Rule 8: "Same content hash + same extractor version + same config fingerprint =>
byte-identical observation set (§3.4 caching, §8.5 replay)."

Two fields are outside the comparison and rule 8's own premise is what puts them
there. The premise is TWO RUNS: a `run_id` is minted per run and `observed_at` is the
instant a reading was taken, so a comparison carrying either would report every row as
changed on every re-run and the rule could never hold. `file_id` is excluded for a
different reason: OQ2 closed on 2026-08-20 and the CONTENT HASH owns the observation,
so two `files` rows over one set of bytes share one observation set. Comparing
`file_id` would make a duplicate look like a different set and rule 8 could never hold
across one. The field stays ON the observation (§2.8 requires it) -- it says which
copy was opened, not who owns the reading.

SPEC vs design, reported and not resolved here: rule 8 lists THREE key fields and
§3.4 asks for a cache key on "the content hash and the exact process that produced
it", which the `extraction_runs_cache_key` index spells with FOUR -- `extractor_name`
included. Read literally, rule 8's three would require two different extractors at one
version over one file to produce one identical set, and `observation_key` includes
`extractor_name`, so those sets can never be equal. This module keys on the four §3.4
names. Rewriting rule 8's text is a contract revision and is not P4's to make.

This is not a diff. §8.5's cross-version comparison is a different question, answered
on `observation_key`, which excludes `extractor_version` precisely so the two versions'
rows line up (MINOR 8). Rule 8 asks only whether the same process, run twice, produced
the same thing.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Mapping

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.observation import OBSERVATION_FIELDS, Observation
from evidence_shape.runs import ExtractionRun

#: §3.4's "the content hash and the exact process that produced it". See the docstring
#: for why this is four names where rule 8's sentence lists three.
REPLAY_KEY_FIELDS: tuple[str, ...] = (
    "content_hash", "extractor_name", "extractor_version", "config_fingerprint",
)

#: The only exclusion list in this package, and each member is forced -- not chosen.
#: `run_id`: minted per run, and rule 8 compares two runs. `observed_at`: the wall
#: clock at the reading, which no re-run reproduces. `file_id`: OQ2 closed on
#: 2026-08-20 -- the CONTENT HASH owns the observation, so two `files` rows holding
#: the same bytes share one observation set. Comparing `file_id` would report the
#: second copy as a different set and rule 8 could never hold across a duplicate,
#: which is precisely the outcome the ratification forbids. `file_id` remains ON the
#: observation as §2.8 requires -- it records which copy was opened, not who owns it.
EXCLUDED_FROM_COMPARISON: tuple[str, str, str] = ("run_id", "observed_at", "file_id")

#: What "byte-identical observation set" is computed over.
COMPARED_FIELDS: tuple[str, ...] = tuple(
    name for name in OBSERVATION_FIELDS if name not in EXCLUDED_FROM_COMPARISON)


class NotDeterministic(ValueError):
    """Rule 8 does not hold between two runs, or the two are not one replay key."""


def replay_key(run: ExtractionRun) -> tuple[str, ...]:
    """The identity rule 8's premise fixes. `config_fingerprint` is derived (Task 7)."""
    return tuple(str(getattr(run, name)) for name in REPLAY_KEY_FIELDS)


def compared_form(observation) -> dict[str, object]:
    """One observation, reduced to what rule 8 compares. Record or stored row."""
    mapping = (observation.to_mapping() if isinstance(observation, Observation)
               else observation)
    if not isinstance(mapping, Mapping):
        raise NotDeterministic(
            f"an observation is a record or a mapping, not {type(observation).__name__}")
    return {name: mapping[name] for name in COMPARED_FIELDS if name in mapping}


def _lines(observations) -> list[str]:
    """The canonical line per observation, sorted: a set has no order.

    Sorted and NOT deduplicated. D10's collapse key is `(run_id, raw_value, zone)` and
    P4 enforces no uniqueness on it, so two identical readings may both exist and a
    digest that collapsed them would disagree with the table it validates.
    """
    return sorted(canonical_json(compared_form(one)) for one in observations)


def observation_set_bytes(observations) -> str:
    """The bytes rule 8 calls identical. One form per set, from `canonical_json`."""
    return canonical_json(_lines(observations))


def observation_set_digest(observations) -> str:
    """`observation_set_bytes`, addressed. What §3.4's cache compares cheaply."""
    return sha256_of(observation_set_bytes(observations))


def assert_identical_observation_sets(first_run, first_observations,
                                      second_run, second_observations) -> None:
    """Rule 8. Returns None when the two sets are identical; raises otherwise.

    A replay-key mismatch is raised as its own message: rule 8 says nothing at all
    about two different processes, and asserting it between them would be inventing a
    rule the SPEC does not state.
    """
    first_key, second_key = replay_key(first_run), replay_key(second_run)
    if first_key != second_key:
        raise NotDeterministic(
            f"these two runs are not one replay key -- {first_key} and {second_key}. "
            "Rule 8 compares the same process run twice; a comparison across "
            "processes is §8.5's diff, and it is made on observation_key")
    first_lines = Counter(_lines(first_observations))
    second_lines = Counter(_lines(second_observations))
    if first_lines == second_lines:
        return
    only_first = sorted((first_lines - second_lines).elements())
    only_second = sorted((second_lines - first_lines).elements())
    raise NotDeterministic(
        f"rule 8: two runs at replay key {first_key} produced different observation "
        f"sets.\nonly in the first run ({len(only_first)}):\n"
        + "\n".join(only_first)
        + f"\nonly in the second run ({len(only_second)}):\n"
        + "\n".join(only_second))
