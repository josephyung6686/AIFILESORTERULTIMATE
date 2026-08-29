# tests/p4/test_p4_canonical.py
import pytest

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.determinism import observation_set_bytes
from evidence_shape.runs import config_fingerprint


def test_canonical_json_is_key_ordered_and_unpadded():
    assert canonical_json({"b": 1, "a": [2, 3]}) == '{"a":[2,3],"b":1}'
    assert canonical_json({"a": 1, "b": 2}) == canonical_json({"b": 2, "a": 1})


def test_canonical_json_keeps_non_ascii_as_itself():
    # §2.7 requires CJK; D4 counts code points. Escaping would make the byte length
    # of a record depend on the script it is written in, for no gain.
    assert canonical_json({"t": "提出書類"}) == '{"t":"提出書類"}'


def test_canonical_json_is_stable_across_equal_but_differently_built_values():
    first = {"languages": ["en", "zh-Hans"], "dpi": 200}
    second = {}
    second["dpi"] = 200
    second["languages"] = ["en", "zh-Hans"]
    assert canonical_json(first) == canonical_json(second)


def test_the_digest_carries_its_algorithm_the_way_content_hash_does():
    assert sha256_of("a").startswith("sha256:")


def test_the_digest_is_injective_over_its_parts():
    # Plain concatenation is not: ("ab", "c") and ("a", "bc") would collide, and the
    # collision would be on the one handle §8.7 requires to stay resolvable.
    assert sha256_of("ab", "c") != sha256_of("a", "bc")
    assert sha256_of("", "abc") != sha256_of("abc", "")
    assert sha256_of("a", "b", "c") != sha256_of("a", "bc")


def test_the_digest_is_deterministic():
    assert sha256_of("sha256:abc", "pdf.text", "heading:page=1/heading=2", "BUSIB 4300") == \
           sha256_of("sha256:abc", "pdf.text", "heading:page=1/heading=2", "BUSIB 4300")


def test_the_digest_is_computed_over_utf_8_bytes():
    assert sha256_of("提出") != sha256_of("提")


def test_canonical_json_refuses_a_non_finite_float():
    # `json.dumps` emits the bare tokens NaN, Infinity and -Infinity by default. They
    # are not JSON: Python's own `json.loads` reads them back, a strict consumer in
    # any other language does not, and §8.5's replay diff is a diff between stored
    # forms that other tools read.
    for value in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(ValueError):
            canonical_json({"c": value})


def test_the_refusal_reaches_a_non_finite_float_at_any_depth():
    # The value that reaches the canonical form is a whole config or a whole
    # observation, never a bare float, so a check that only looked at the top level
    # would not be a check.
    with pytest.raises(ValueError):
        canonical_json({"ocr": {"threshold": float("nan")}})
    with pytest.raises(ValueError):
        canonical_json({"weights": [1.0, float("inf")]})
    with pytest.raises(ValueError):
        canonical_json([{"region": {"x": float("nan")}}])


def test_a_finite_float_still_serializes():
    assert canonical_json({"threshold": 0.5}) == '{"threshold":0.5}'
    assert canonical_json({"n": 200}) == '{"n":200}'


def test_the_refusal_is_at_the_canonical_form_because_fingerprint_time_is_bypassable():
    """WHY `canonical_json` and not `config_fingerprint`: three ways in, one door.

    A non-finite float reaches the canonical form down three paths, and only the
    first passes through a fingerprint:

      1. `run.config`   -> `runs.config_fingerprint` (§3.4's cache key, rule 8's
         four-field replay key). `NaN != NaN`, so a config holding one can never
         equal itself and the cache misses a configuration it already ran.
      2. `observation.confidence` -> `determinism.observation_set_bytes`. §2.7 names
         no scale for confidence and P4 asserts no range, so NaN is admitted by the
         record; it then serializes to the token `NaN`, and two DIFFERENT readings
         compare byte-identical. Rule 8 would report determinism that is not there.
      3. `location.region` -> the stored `location` column (`store.record_observation`).
         `Region` accepts any `int | float`.

    Paths 2 and 3 never touch `config_fingerprint`. `canonical_json` is the one place
    all three pass through, so it is the only boundary that cannot be walked around.
    """
    assert config_fingerprint is not None
    with pytest.raises(ValueError):
        config_fingerprint({"threshold": float("nan")})

    # Path 2, executed: rule 8's own comparison, over a field a fingerprint never sees.
    with pytest.raises(ValueError):
        observation_set_bytes([{"raw_value": "BUSIB 4300", "confidence": float("nan")}])
