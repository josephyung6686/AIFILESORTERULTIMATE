# tests/p4/test_p4_canonical.py
from evidence_shape.canonical import canonical_json, sha256_of


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
