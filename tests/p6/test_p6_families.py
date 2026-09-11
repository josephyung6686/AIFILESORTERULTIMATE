# tests/p6/test_p6_families.py
"""G5 — Done-means 23 and 24. §8.3's refusal, and the two families P6 was handed."""
from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from evidence_shape.vocabulary import NotInVocabulary

from extractors.image import PERCEPTUAL_HASH_FIELD

from facts import families
from facts.families import (
    DUPLICATE_FAMILY_FIELD, Lineage, PERCEPTUAL_HASH_LABEL, VERSION_FAMILY_FIELD,
    duplicate_family, version_family,
)
from facts.file_facts import facts_for_file
from facts.unresolved import unresolved_for_file

CLOCK = "2026-08-19T12:00:00+00:00"

#: P5 spells the label; P6 injects it. The test is the only place the two meet.
LABEL = PERCEPTUAL_HASH_FIELD


def _code_strings(module) -> set[str]:
    """Every string literal in a module that is NOT a docstring.

    A source-text search matches comments and docstrings, and a guard that does that
    has broken three tasks on this project already (P5 PLAN, Task 20). This reads the
    code.
    """
    tree = ast.parse(inspect.getsource(module))
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)) and body:
            first = body[0]
            if (isinstance(first, ast.Expr)
                    and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                docstrings.add(id(first.value))
    return {node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
            and id(node) not in docstrings}


def _record(conn, tmp_path, *, name, body, parent="Downloads"):
    """One P1 `files` row over real bytes, so the content hash is P1's own."""
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context=parent, mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, label,
             extractor="pdf.text", zone="metadata", source_type="text_document",
             analysis_tier="native"):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name=extractor, extractor_version="1.0.0",
        source_type=source_type, analysis_tier=analysis_tier, config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name=extractor,
        extractor_version="1.0.0", source_type=source_type, raw_value=raw,
        location=Location(zone, (Segment("field", label=label),)),
        occurrence_count=1, observed_at=CLOCK, reliability="direct", run_id=run_id)
    record_observation(conn, observation)
    return observation.observation_key


def _never_near(left: str, right: str) -> bool:
    """The injected near-match predicate that never matches. P6 states no distance."""
    return False


def _one_near_block(raw: str) -> tuple[str, ...]:
    """The near-blocking key that blocks nothing: every carrier in one block.

    One constant key is a necessary condition of EVERY predicate, so injecting it
    leaves the tests that are about the predicate measuring exactly what they
    measured before blocking existed. `test_the_near_pair_loop_asks_fewer_than_
    every_pair` is the one that measures the cost, and it injects a key that splits.
    """
    return ("",)


def _no_lineage(conn, left_file_id: str, right_file_id: str):
    """§2.9 lists 'duplicate and version-family signals' and defines neither."""
    return None


def _one_block(conn, file_id: str) -> str:
    """The blocking key that blocks nothing: every file in one block.

    The key is a property of whichever lineage rule ships, and `97` rules no rule,
    so the tests below that are ABOUT the rule rather than about the cost inject the
    degenerate key on purpose -- every pair is still offered to the rule, which is
    what those tests measure. `test_the_pair_loop_asks_fewer_than_every_pair` is the
    one that measures the cost, and it injects a key that actually splits.
    """
    return ""


@pytest.fixture()
def twins(p6_conn, tmp_path):
    """Two `files` rows over identical bytes: one content hash, two file ids."""
    left, left_hash = _record(p6_conn, tmp_path, name="Syllabus.pdf",
                              body=b"BUSIB 4300 Syllabus, Spring 2026")
    right, right_hash = _record(p6_conn, tmp_path, name="Syllabus copy.pdf",
                                body=b"BUSIB 4300 Syllabus, Spring 2026")
    assert left_hash == right_hash
    key_left = _observe(p6_conn, run_id="r-left", file_id=left,
                        content_hash=left_hash, raw="application/pdf",
                        label="mime_type")
    key_right = _observe(p6_conn, run_id="r-right", file_id=right,
                         content_hash=right_hash, raw="application/pdf",
                         label="mime_type")
    assert key_left == key_right          # the whole point: one key, two files
    return left, right, left_hash, key_left


def test_two_byte_identical_files_share_a_direct_duplicate_family_fact(twins, p6_conn):
    # Done-means 23. §3.13 names the content hash a Direct source.
    #
    # SHARED is the claim, and it is checked as one value seen twice rather than as a
    # literal. This line read `== content_hash` until 2026-09-04, which asserted the
    # §8.4 defect the two tests at the foot of this file now forbid: the hash decides
    # membership and does not name it. What Done-means 23 actually requires is that
    # both members land in ONE family at `direct` -- not what the family is called.
    left, right, content_hash, _ = twins
    written = duplicate_family(p6_conn, file_ids=(left, right),
                               perceptual_hash_label=LABEL,
                               near_match=_never_near,
                               near_block_keys=_one_near_block)
    assert len(written) == 2
    seen = set()
    for file_id in (left, right):
        rows = [r for r in facts_for_file(p6_conn, file_id, content_hash)
                if r["field_key"] == DUPLICATE_FAMILY_FIELD]
        assert len(rows) == 1
        assert rows[0]["reliability_state"] == "direct"
        seen.add(rows[0]["canonical_value"])
    assert len(seen) == 1


def test_the_duplicate_family_cites_the_keys_the_two_versions_share(twins, p6_conn):
    # M14: every entry is an observation key, and the key is what byte identity
    # produces twice. P1's content hash decides; P4's key is what a reviewer follows.
    left, right, content_hash, shared_key = twins
    duplicate_family(p6_conn, file_ids=(left, right),
                     perceptual_hash_label=LABEL, near_match=_never_near,
                     near_block_keys=_one_near_block)
    row = [r for r in facts_for_file(p6_conn, left, content_hash)
           if r["field_key"] == DUPLICATE_FAMILY_FIELD][0]
    assert json.loads(row["evidence_refs"]) == [shared_key]
    assert shared_key.startswith("sha256:")


def test_a_duplicate_pair_with_nothing_to_cite_abstains(p6_conn, tmp_path):
    # Rule 1: a fact with no citable evidence is not a fact. Two identical files with
    # no stored observations get a refusal that names itself, not a silent gap.
    left, content_hash = _record(p6_conn, tmp_path, name="a.pdf", body=b"same bytes")
    right, _ = _record(p6_conn, tmp_path, name="b.pdf", body=b"same bytes")
    assert duplicate_family(p6_conn, file_ids=(left, right),
                            perceptual_hash_label=LABEL,
                            near_match=_never_near,
                            near_block_keys=_one_near_block) == ()
    for file_id in (left, right):
        rows = unresolved_for_file(p6_conn, file_id, content_hash,
                                   field_key=DUPLICATE_FAMILY_FIELD)
        assert [r["reason"] for r in rows] == ["no_candidate_evidence"]


def test_a_perceptual_hash_near_match_is_possible_and_never_direct(p6_conn, tmp_path):
    # §2.6 distinguishes "duplicates and near-duplicates"; §8.3 keeps the hash match
    # as the only thing that supports deduplication review.
    left, left_hash = _record(p6_conn, tmp_path, name="photo.jpg", body=b"pixels-one")
    right, right_hash = _record(p6_conn, tmp_path, name="photo-resized.jpg",
                                body=b"pixels-two")
    assert left_hash != right_hash
    _observe(p6_conn, run_id="p-left", file_id=left, content_hash=left_hash,
             raw="phash:00ff00ff", label=LABEL, extractor="image.metadata",
             source_type="image")
    _observe(p6_conn, run_id="p-right", file_id=right, content_hash=right_hash,
             raw="phash:00ff00fe", label=LABEL, extractor="image.metadata",
             source_type="image")
    written = duplicate_family(p6_conn, file_ids=(left, right),
                               perceptual_hash_label=LABEL,
                               near_match=lambda a, b: a[:-1] == b[:-1],
                               # The key is a necessary condition of that
                               # predicate: two raws that agree but for the last
                               # character agree on this prefix.
                               near_block_keys=lambda raw: (raw[:-1],))
    assert len(written) == 2
    states = {r["reliability_state"]
              for file_id, digest in ((left, left_hash), (right, right_hash))
              for r in facts_for_file(p6_conn, file_id, digest)
              if r["field_key"] == DUPLICATE_FAMILY_FIELD}
    assert states == {"possible"}


def test_the_container_path_label_is_injected_and_the_module_holds_no_copy():
    # P5 owns the spelling and it has a space in it. A copy here would be a second
    # home for one string, which is this project's most expensive defect.
    assert PERCEPTUAL_HASH_LABEL == "perceptual_hash_label"
    parameter = inspect.signature(duplicate_family).parameters[PERCEPTUAL_HASH_LABEL]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is inspect.Parameter.empty
    assert LABEL not in _code_strings(families)
    near = inspect.signature(duplicate_family).parameters["near_match"]
    assert near.default is inspect.Parameter.empty


def test_two_files_sharing_only_a_one_suffix_share_no_family_of_either_kind(
        p6_conn, tmp_path):
    # Done-means 23 and 24, and §8.5's "duplicate suffixes on unrelated files".
    left, left_hash = _record(p6_conn, tmp_path, name="report (1).pdf",
                              body=b"quarterly report")
    right, right_hash = _record(p6_conn, tmp_path, name="invoice (1).pdf",
                                body=b"an invoice")
    _observe(p6_conn, run_id="s-left", file_id=left, content_hash=left_hash,
             raw="report (1).pdf", label="normalized_filename")
    _observe(p6_conn, run_id="s-right", file_id=right, content_hash=right_hash,
             raw="invoice (1).pdf", label="normalized_filename")
    assert duplicate_family(p6_conn, file_ids=(left, right),
                            perceptual_hash_label=LABEL,
                            near_match=_never_near,
                            near_block_keys=_one_near_block) == ()
    assert version_family(p6_conn, file_ids=(left, right),
                          lineage_rule=_no_lineage, block_key=_one_block) == ()
    for file_id, digest in ((left, left_hash), (right, right_hash)):
        assert facts_for_file(p6_conn, file_id, digest) == []
        # A relation nobody proposed was never attempted; `unresolved` records the
        # field that WAS attempted, not every pair in the corpus.
        assert unresolved_for_file(p6_conn, file_id, digest) == []


def test_identical_hashes_are_a_duplicate_family_and_never_a_version_family(
        twins, p6_conn):
    left, right, content_hash, _ = twins

    def always(conn, a, b):
        return Lineage(family_value="v1", reliability_state="validated",
                       evidence_refs=("sha256:deadbeef",))

    assert version_family(p6_conn, file_ids=(left, right), lineage_rule=always,
                          block_key=_one_block) == ()
    rows = [r for r in facts_for_file(p6_conn, left, content_hash)
            if r["field_key"] == VERSION_FAMILY_FIELD]
    assert rows == []


def test_a_version_family_fact_is_never_direct():
    # Done-means 24: no explicit slot states a version relation, so the refusal is at
    # the type rather than at a call site.
    assert families.VERSION_FAMILY_STATES == ("validated", "possible")
    with pytest.raises(NotInVocabulary):
        Lineage(family_value="v1", reliability_state="direct",
                evidence_refs=("sha256:deadbeef",))
    assert Lineage(family_value="v1", reliability_state="possible",
                   evidence_refs=("sha256:deadbeef",)).reliability_state == "possible"


def test_an_empty_lineage_rule_writes_no_version_family_fact(p6_conn, tmp_path):
    # §2.9 names the signals and defines none, so the default state of the product is
    # a rule that establishes nothing.
    left, left_hash = _record(p6_conn, tmp_path, name="draft v1.docx", body=b"one")
    right, right_hash = _record(p6_conn, tmp_path, name="draft v2.docx", body=b"two")
    assert version_family(p6_conn, file_ids=(left, right),
                          lineage_rule=_no_lineage, block_key=_one_block) == ()
    assert facts_for_file(p6_conn, left, left_hash) == []
    assert facts_for_file(p6_conn, right, right_hash) == []


def test_a_lineage_that_cites_no_evidence_is_refused_rather_than_asserted(
        p6_conn, tmp_path):
    left, left_hash = _record(p6_conn, tmp_path, name="draft v1.docx", body=b"one")
    right, right_hash = _record(p6_conn, tmp_path, name="draft v2.docx", body=b"two")

    def uncited(conn, a, b):
        return Lineage(family_value="draft", reliability_state="validated",
                       evidence_refs=())

    assert version_family(p6_conn, file_ids=(left, right),
                          lineage_rule=uncited, block_key=_one_block) == ()
    for file_id, digest in ((left, left_hash), (right, right_hash)):
        rows = unresolved_for_file(p6_conn, file_id, digest,
                                   field_key=VERSION_FAMILY_FIELD)
        assert [r["reason"] for r in rows] == ["no_candidate_evidence"]


def test_the_result_does_not_depend_on_the_order_the_file_ids_arrive_in(
        twins, p6_conn):
    # P4's reads are in insertion order and P6 must not inherit it (Global
    # Constraints). Two orders, one outcome, compared as sets of stored rows.
    left, right, content_hash, _ = twins
    forward = duplicate_family(p6_conn, file_ids=(left, right),
                               perceptual_hash_label=LABEL,
                               near_match=_never_near,
                               near_block_keys=_one_near_block)
    reverse = duplicate_family(p6_conn, file_ids=(right, left),
                               perceptual_hash_label=LABEL,
                               near_match=_never_near,
                               near_block_keys=_one_near_block)
    assert len(forward) == len(reverse) == 2

    def shape(ids):
        return sorted(
            (r["file_id"], r["reliability_state"], r["canonical_value"],
             r["evidence_refs"])
            for file_id in (left, right)
            for r in facts_for_file(p6_conn, file_id, content_hash)
            if r["fact_id"] in ids and r["field_key"] == DUPLICATE_FAMILY_FIELD)

    assert shape(forward) == shape(reverse)


def _content_hashes(conn) -> set[str]:
    """Every content hash P1 stored, read from the `files` table itself.

    Read rather than passed in, because the claim under test is about the whole
    database and not about the two hashes a fixture happened to hand back.
    """
    return {row["content_hash"]
            for row in conn.execute("SELECT content_hash FROM files")}


def test_no_duplicate_family_value_is_a_content_hash(twins, p6_conn):
    """§8.4 member 4 -- `file_hashes` is one of the nine that never leave the device.

    The family may be COMPUTED from the hash; the hash may not be what the family
    is CALLED. `families`' own header already separates the two -- "the hash decides
    membership and cannot be cited for it" -- and this is the same separation one
    step further on: what decides membership is not what names it.

    Written because the value does not stay in P6. It reaches
    `grouping.seeds.seeds_for_file` (which reads `family_facts` deliberately),
    becomes `Seed.value`, and from there `grouping.naming.label_for` puts it on a
    group's display label and `grouping.dossier` puts it in `key_facts`, which is
    the half of a candidate-group dossier that goes to a model. None of those three
    is P6's to change and none of them is wrong: a fact's value is releasable by
    design, so the fix is that P6 must not write an always-local value into one.
    """
    left, right, _, _ = twins
    duplicate_family(p6_conn, file_ids=(left, right),
                     perceptual_hash_label=LABEL, near_match=_never_near,
                     near_block_keys=_one_near_block)
    hashes = _content_hashes(p6_conn)
    assert hashes                                   # the fixture really stored some
    values = {row["canonical_value"] for row in p6_conn.execute(
        'SELECT canonical_value FROM "values" WHERE field_key = ?',
        (DUPLICATE_FAMILY_FIELD,))}
    assert values                                   # and the family really wrote one
    assert values & hashes == set()


def test_no_family_seed_p9_would_release_carries_a_content_hash(twins, p6_conn):
    """The same claim on the path that actually leaves P6, end to end.

    `_anchor_rows` reads `family_facts` beside `proposal_eligible`, and a
    `duplicate_family` fact is `direct`, so it clears any anchor bar. This asserts
    against the SEED rather than against the stored row because the seed is the
    object P9 hands onward, and a value that were laundered into it by some other
    column would pass the test above and fail here.
    """
    from grouping.seeds import seeds_for_file

    left, right, content_hash, _ = twins
    duplicate_family(p6_conn, file_ids=(left, right),
                     perceptual_hash_label=LABEL, near_match=_never_near,
                     near_block_keys=_one_near_block)
    hashes = _content_hashes(p6_conn)
    seeds = seeds_for_file(p6_conn, file_id=left, content_hash=content_hash,
                           user_seed_for=lambda *_: None)
    family = [seed for seed in seeds if seed.field_key == DUPLICATE_FAMILY_FIELD]
    assert len(family) == 1                         # P9 really does seed on it
    assert family[0].value not in hashes


def test_two_files_in_one_duplicate_family_share_that_field(twins, p6_conn):
    """P9's `duplicate_or_version` authority, answered from the facts themselves.

    `grouping.graph._edge_type` RAISES `ConfigurationRequired` on a
    duplicate-or-version-link edge with no authority — "the wrong answer puts two
    revisions of one document into a group as two documents" — and
    `grouping.retrieval` opens that channel off `family_facts`, which covers BOTH
    fields. So the moment `duplicate_family` is bound the authority stops being
    optional: without it a corpus containing one duplicate pair stops the run.

    P6 answers WHICH FIELD the two share and stops there. Mapping that key onto
    P9's own two words is the composition root's, because P6 naming a P9 vocabulary
    member would be a second home for it.
    """
    left, right, _, _ = twins
    duplicate_family(p6_conn, file_ids=(left, right),
                     perceptual_hash_label=LABEL, near_match=_never_near,
                     near_block_keys=_one_near_block)
    assert families.shared_family_field(
        p6_conn, left_file_id=left, right_file_id=right) == DUPLICATE_FAMILY_FIELD
    # Symmetric: an edge is one relation whichever end asks about it.
    assert families.shared_family_field(
        p6_conn, left_file_id=right, right_file_id=left) == DUPLICATE_FAMILY_FIELD


def test_two_unrelated_files_share_no_family_field(p6_conn, tmp_path):
    """`None`, not a guess. A caller that must produce one of two words has to be
    able to tell that neither is true, or P9's refusal becomes P6's coin toss."""
    left, _ = _record(p6_conn, tmp_path, name="one.pdf", body=b"first")
    right, _ = _record(p6_conn, tmp_path, name="two.pdf", body=b"second")
    assert families.shared_family_field(
        p6_conn, left_file_id=left, right_file_id=right) is None


def test_a_shared_version_family_answers_the_version_field(p6_conn, tmp_path):
    # The other half of the same question, so the reader cannot be a constant.
    left, left_hash = _record(p6_conn, tmp_path, name="draft.pdf", body=b"draft one")
    right, right_hash = _record(p6_conn, tmp_path, name="final.pdf", body=b"draft two")
    key_left = _observe(p6_conn, run_id="v-left", file_id=left,
                        content_hash=left_hash, raw="Report", label="title")
    key_right = _observe(p6_conn, run_id="v-right", file_id=right,
                         content_hash=right_hash, raw="Report", label="title")
    written = version_family(
        p6_conn, file_ids=(left, right),
        lineage_rule=lambda conn, a, b: Lineage(
            family_value="report-lineage", reliability_state="validated",
            evidence_refs=(key_left, key_right)),
        block_key=_one_block)
    assert len(written) == 2
    assert families.shared_family_field(
        p6_conn, left_file_id=left, right_file_id=right) == VERSION_FAMILY_FIELD


# --- the blocking step (`00` Amendments of 2026-09-11 item 4) -------------------
#
# "Duplicate and version-family signals are produced under those rules; perceptual
# hashes are supplied by the image reader; **the comparison is kept sub-quadratic by
# a blocking step**." The blocking step is the half of that sentence that does not
# wait on a rule: whichever lineage rule the owner rules, the pair enumeration it is
# offered has to be bounded, and `cli.py`'s `_family_pass` already names the cost as
# the reason the call is not there -- "on 10,000 files that is 50 million pairs
# enumerated to answer 'no rule' 50 million times ... whoever authors it owns the
# blocking strategy that keeps the comparison bounded."


def _blocked_corpus(conn, tmp_path, *, per_block=4):
    """Two folders of distinct bytes, so a key over the folder splits the corpus."""
    made = []
    for folder in ("Drafts", "Invoices"):
        for n in range(per_block):
            file_id, _hash = _record(
                conn, tmp_path, name=f"{folder}-{n}.pdf",
                body=f"{folder} body {n}".encode(), parent=folder)
            made.append(file_id)
    return tuple(made)


def _folder_block(conn, file_id: str) -> str:
    """A blocking key read off the record, as a real one would be.

    P1 stores the folder under `directory_position`; `record_file`'s keyword for it
    is `parent_folder_context`.
    """
    return get_file(conn, file_id)["directory_position"]


def test_the_pair_loop_asks_fewer_than_every_pair(p6_conn, tmp_path):
    """The measurement, with a counting fake: N files, fewer than N(N-1)/2 asks."""
    files = _blocked_corpus(p6_conn, tmp_path)
    asked: list[tuple[str, str]] = []

    def counting(conn, left, right):
        asked.append((left, right))
        return None

    assert version_family(p6_conn, file_ids=files, lineage_rule=counting,
                          block_key=_folder_block) == ()
    every_pair = len(files) * (len(files) - 1) // 2
    assert len(asked) < every_pair, (
        f"{len(asked)} of {every_pair} pairs asked -- the loop is still quadratic")
    # And the bound is the blocks' own, not an arbitrary smaller number: two blocks
    # of four ask 6 + 6 rather than 28.
    assert len(asked) == 12, asked


def test_no_pair_from_two_different_blocks_is_ever_asked(p6_conn, tmp_path):
    """What makes it cheap is also what makes it wrong if the key is wrong.

    The contract `version_family` states is that the key must be a NECESSARY
    condition of the rule: a pair the rule would have joined must share a key, or
    blocking silently loses the family. This pins the half that is the module's --
    that a pair across two keys is never offered at all.
    """
    files = _blocked_corpus(p6_conn, tmp_path)
    blocks = {file_id: _folder_block(p6_conn, file_id) for file_id in files}
    asked: list[tuple[str, str]] = []

    def counting(conn, left, right):
        asked.append((left, right))
        return None

    version_family(p6_conn, file_ids=files, lineage_rule=counting,
                   block_key=_folder_block)
    crossing = [(a, b) for a, b in asked if blocks[a] != blocks[b]]
    assert crossing == [], crossing


def test_a_file_with_no_block_key_is_compared_against_nothing(p6_conn, tmp_path):
    """`None` is the key's own abstention, and it costs the file every comparison.

    A reader that cannot key a file has not said the file is in no family; it has
    said it cannot cheaply say which files it could be in. The module takes the
    conservative half -- no comparison, therefore no fact and no `unresolved` row,
    because a relation nobody proposed was never attempted.
    """
    left, left_hash = _record(p6_conn, tmp_path, name="keyed.pdf", body=b"one")
    right, right_hash = _record(p6_conn, tmp_path, name="unkeyable.pdf", body=b"two")
    asked: list[tuple[str, str]] = []

    def counting(conn, a, b):
        asked.append((a, b))
        return None

    assert version_family(
        p6_conn, file_ids=(left, right), lineage_rule=counting,
        block_key=lambda conn, file_id: None if file_id == right else "k") == ()
    assert asked == []
    for file_id, digest in ((left, left_hash), (right, right_hash)):
        assert facts_for_file(p6_conn, file_id, digest) == []
        assert unresolved_for_file(p6_conn, file_id, digest) == []


def test_a_family_the_rule_joins_inside_one_block_still_forms(p6_conn, tmp_path):
    """The twin. A blocking step that refused every pair would pass the two above.

    Three files in one block, joined by a rule that answers for every pair it is
    offered: one family of three, and the fourth file -- alone in its own block --
    in none.
    """
    left, left_hash = _record(p6_conn, tmp_path, name="d1.pdf", body=b"one",
                              parent="Drafts")
    middle, middle_hash = _record(p6_conn, tmp_path, name="d2.pdf", body=b"two",
                                  parent="Drafts")
    right, right_hash = _record(p6_conn, tmp_path, name="d3.pdf", body=b"three",
                                parent="Drafts")
    stranger, stranger_hash = _record(p6_conn, tmp_path, name="x.pdf", body=b"four",
                                      parent="Invoices")
    keys = {}
    for run, file_id, digest in (("b1", left, left_hash), ("b2", middle, middle_hash),
                                 ("b3", right, right_hash),
                                 ("b4", stranger, stranger_hash)):
        keys[file_id] = _observe(p6_conn, run_id=run, file_id=file_id,
                                 content_hash=digest, raw="Report", label="title")

    def joins(conn, a, b):
        return Lineage(family_value="report-lineage", reliability_state="validated",
                       evidence_refs=(keys[a], keys[b]))

    written = version_family(p6_conn, file_ids=(left, middle, right, stranger),
                             lineage_rule=joins, block_key=_folder_block)
    assert len(written) == 3
    for file_id, digest in ((left, left_hash), (middle, middle_hash),
                            (right, right_hash)):
        rows = [r for r in facts_for_file(p6_conn, file_id, digest)
                if r["field_key"] == VERSION_FAMILY_FIELD]
        assert [r["canonical_value"] for r in rows] == ["report-lineage"], rows
    assert [r for r in facts_for_file(p6_conn, stranger, stranger_hash)
            if r["field_key"] == VERSION_FAMILY_FIELD] == []


def test_the_blocking_step_is_injected_and_required(p6_conn):
    """Like `lineage_rule` and for the same reason: `97` names no key either.

    A default here would be this module choosing the cheap necessary condition of a
    rule it does not know, which is the same defect one layer down from choosing the
    rule.
    """
    parameter = inspect.signature(version_family).parameters["block_key"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is inspect.Parameter.empty


# --- the near half's blocking step (same amendment, same sentence) --------------


def _carrier(conn, tmp_path, *, name, body, run, hash_value):
    """One file version carrying one perceptual-hash observation."""
    file_id, digest = _record(conn, tmp_path, name=name, body=body)
    _observe(conn, run_id=run, file_id=file_id, content_hash=digest,
             raw=hash_value, label=LABEL, extractor="image.metadata",
             source_type="image")
    return file_id


def test_the_near_pair_loop_asks_fewer_than_every_pair(p6_conn, tmp_path):
    """The same measurement one field over, with a counting fake.

    `_near_families` was always bounded by the CARRIERS rather than the roster, and
    until 11 Sep 2026 that bound was zero because nothing produced a hash. On a photo
    library the carriers ARE the roster, so the bound had to become a real one.
    """
    carriers = [
        _carrier(p6_conn, tmp_path, name=f"IMG_{n}.jpg",
                 body=f"jpeg bytes {n}".encode(), run=f"n-{n}",
                 hash_value=f"{'a' if n < 4 else 'b'}{n}")
        for n in range(8)]
    asked: list[tuple[str, str]] = []

    def counting(left, right):
        asked.append((left, right))
        return False

    assert duplicate_family(
        p6_conn, file_ids=tuple(carriers), perceptual_hash_label=LABEL,
        near_match=counting, near_block_keys=lambda raw: (raw[0],)) == ()
    every_pair = len(carriers) * (len(carriers) - 1) // 2
    assert len(asked) < every_pair, (
        f"{len(asked)} of {every_pair} pairs asked -- the loop is still quadratic")
    assert len(asked) == 12, asked


def test_a_reading_with_no_block_key_is_compared_against_nothing(p6_conn, tmp_path):
    """A hash this deployment's keyer will not key is a hash it will not compare.

    `readers.perceptual_hash.near_block_keys` returns `()` for a value some other
    algorithm produced, and this is what that costs the file: no comparison, so no
    near family and -- a relation nobody proposed having never been attempted -- no
    `unresolved` row either.
    """
    left = _carrier(p6_conn, tmp_path, name="a.jpg", body=b"one", run="k-1",
                    hash_value="dhash64:0")
    right = _carrier(p6_conn, tmp_path, name="b.jpg", body=b"two", run="k-2",
                     hash_value="phash:8f3a")
    asked: list[tuple[str, str]] = []

    def counting(a, b):
        asked.append((a, b))
        return True

    assert duplicate_family(
        p6_conn, file_ids=(left, right), perceptual_hash_label=LABEL,
        near_match=counting,
        near_block_keys=lambda raw: () if raw.startswith("phash") else ("k",)) == ()
    assert asked == []
    for file_id in (left, right):
        digest = get_file(p6_conn, file_id)["content_hash"]
        assert facts_for_file(p6_conn, file_id, digest) == []
        assert unresolved_for_file(p6_conn, file_id, digest) == []


def test_one_pair_is_asked_once_however_many_keys_it_shares(p6_conn, tmp_path):
    """Banding gives a carrier several keys, and a pair must not be asked per key.

    `readers.perceptual_hash` splits 64 bits into six bands, so two near-identical
    photographs usually agree on several of them. Without the guard the same
    comparison would be paid for once per band -- and, worse, `near_match` would be
    a predicate called a variable number of times, which a counting pin like the one
    above could no longer read.
    """
    left = _carrier(p6_conn, tmp_path, name="a.jpg", body=b"one", run="m-1",
                    hash_value="x")
    right = _carrier(p6_conn, tmp_path, name="b.jpg", body=b"two", run="m-2",
                     hash_value="x")
    asked: list[tuple[str, str]] = []

    def counting(a, b):
        asked.append((a, b))
        return False

    duplicate_family(p6_conn, file_ids=(left, right), perceptual_hash_label=LABEL,
                     near_match=counting,
                     near_block_keys=lambda raw: ("b0", "b1", "b2", "b3"))
    assert len(asked) == 1, asked


def test_the_near_blocking_step_is_injected_and_required():
    """Like `near_match`: the cheap necessary condition of a distance is a property
    of the hash that distance is over, and P6 holds neither."""
    parameter = inspect.signature(duplicate_family).parameters["near_block_keys"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is inspect.Parameter.empty
