# tests/p10/test_p10_existing_folders.py
"""`00`:100 and :102 — the folders the person already made, in the tree they get.

The defect this file pins was found by running the command, not by any test.
`horizontal_candidates` builds a branch card for every directory the scan read,
and `design_tree` then keeps only candidates whose `subject_id` appears in
`branch_group_ids`. A folder candidate's `subject_id` is its DIRECTORY PATH, so
eight cards were built from a real person's eight folders and every one was
dropped unread, with nothing anywhere recording that it happened.

`node_type='existing'` was designed for exactly this and had no writer outside a
test fixture, which made `residuals.REPLACE_WITH_EXISTING` — a live consumer —
dead by construction.

**The tempting fix is the harmful one and these tests forbid it.** Putting folder
paths into `branch_group_ids` and leaving `_top_level_node` alone mints a
`proposed` node at the root wearing the folder's name, so the product would offer
to move `Uni/PHYS1401/lab.txt` into a NEW top-level `PHYS1401` — flattening the
person's hierarchy in the name of honouring it, which `00`:100 forbids by name.
The adopted node has to carry the folder's real place: its type, its path, and
its parent.
"""
from __future__ import annotations

import pytest

from evidence_shape.schema import create_evidence_schema
from grouping.schema import create_grouping_schema
from tree_design.schema import create_tree_schema
from tree_design.store import nodes_for_version
from tree_design.vocabulary import EXISTING, PROPOSED

from p10.seam_corpus import seed_seam_corpus
from p10.test_p10_pipeline import authorities, decisions, design


@pytest.fixture()
def corpus(conn, tmp_path):
    create_evidence_schema(conn)
    create_grouping_schema(conn)
    create_tree_schema(conn)
    return seed_seam_corpus(conn, tmp_path)


def seed_folder(corpus, path: str, parent: str | None, *, files: int = 3) -> None:
    """One directory the person made, as P3 would have recorded it.

    `curation_signal` is `undetermined` because that is what P3 returns for every
    directory today: §1.1 gives one worked case and no threshold, so the signal
    is carried and never rounded. A test that seeded `curated` would be testing a
    corpus this deployment cannot produce.
    """
    corpus.conn.execute(
        "INSERT INTO directory_inventory (scan_run_id, directory_path, "
        "parent_directory, file_count, subdirectory_count, extension_mix, "
        "curation_signal, curation_evidence, applies_to) "
        "VALUES (?, ?, ?, ?, 0, '{}', 'undetermined', '[]', 'both')",
        (corpus.scan_run_id, path, parent, files))


def put_in_folder(corpus, tmp_path, folder: str, names) -> str:
    """Move some of this corpus's files into a folder the person made.

    The seam corpus lays every file in one directory. `current_path` is what P3
    recorded and what every directory read here is derived from, so rewriting it
    IS the corpus having been organised -- and it keeps the fixture honest about
    which files are where without a second corpus to maintain.
    """
    directory = str(tmp_path / folder)
    for name in names:
        file_id = corpus.file_id(name)
        corpus.conn.execute(
            "UPDATE files SET current_path = ? WHERE file_id = ?",
            (f"{directory}/{name}.pdf", file_id))
    return directory


def adopted(result, conn, path: str):
    """The node adopted from one directory, found by its PATH.

    Not by label: this corpus's own template produces a node labelled
    `PHYS1401` too, and that collision is the point — a proposed folder and the
    person's real folder can share a name and are not the same thing.
    """
    return next((node for node in nodes_for_version(
        conn, result.plan_version_ids[-1]) if node.existing_path == path), None)


# --- the adoption ------------------------------------------------------------------


def test_an_adopted_folder_is_an_existing_node_carrying_its_real_path(corpus):
    """`00`:102 makes `existing` a node type that carries the folder's real path.
    Adopting a folder as anything else is a proposal wearing its name."""
    seed_folder(corpus, "Uni", None)
    result = design(corpus, dec=decisions(
        branch_group_ids=("g_columbia_coursework", "Uni")))

    uni = adopted(result, corpus.conn, "Uni")
    assert uni is not None, "the person's folder was read and then dropped"
    assert uni.node_type == EXISTING
    assert uni.display_label == "Uni"


def test_a_folder_inside_an_adopted_folder_is_nested_under_it(corpus):
    """The flattening `00`:100 forbids, pinned. Both folders are adopted, and the
    child hangs off the parent rather than appearing beside it at the root."""
    seed_folder(corpus, "Uni", None)
    seed_folder(corpus, "Uni/PHYS1401", "Uni")
    result = design(corpus, dec=decisions(
        branch_group_ids=("g_columbia_coursework", "Uni", "Uni/PHYS1401")))

    parent = adopted(result, corpus.conn, "Uni")
    child = adopted(result, corpus.conn, "Uni/PHYS1401")
    assert child is not None and parent is not None
    assert child.parent_node_id == parent.node_id


def test_a_folder_whose_parent_was_not_adopted_stays_at_the_top(corpus):
    """The other half of the same rule. A person who adopts one folder deep in a
    tree gets that folder, not an invented chain of ancestors above it."""
    seed_folder(corpus, "Uni", None)
    seed_folder(corpus, "Uni/PHYS1401", "Uni")
    result = design(corpus, dec=decisions(
        branch_group_ids=("g_columbia_coursework", "Uni/PHYS1401")))

    child = adopted(result, corpus.conn, "Uni/PHYS1401")
    assert child is not None
    assert child.parent_node_id is None


# --- the negative twin -------------------------------------------------------------


def test_a_branch_built_from_an_accepted_group_is_still_proposed(corpus):
    """The twin. Adoption reads the candidate's SOURCE, so a branch the engine
    proposed from evidence must be unaffected — it is a folder that does not
    exist yet, and calling it `existing` would claim the person made it."""
    seed_folder(corpus, "Uni", None)
    result = design(corpus, dec=decisions(
        branch_group_ids=("g_columbia_coursework", "Uni")))

    proposed = [node for node in nodes_for_version(
        corpus.conn, result.plan_version_ids[-1])
        if node.node_type == PROPOSED]
    assert proposed, "the accepted group still builds a proposed branch"
    assert all(node.existing_path is None for node in proposed)


# --- two folders that share a name -------------------------------------------------


def test_two_folders_with_the_same_name_both_get_a_card(conn):
    """The standing rule: material is marked and counted, never silently omitted.

    `horizontal_candidates` keyed its folders by the LAST PATH SEGMENT, so a
    person with `Uni/PHYS1401` and `Physics/PHYS1401` -- two real folders, in two
    places, holding different files -- had one of them overwritten in a dict and
    dropped with nothing recording it anywhere.

    This was invisible while every folder candidate was discarded downstream. It
    stops being invisible the moment folders are adopted, because now the dropped
    one is a folder of theirs that the tree does not contain.
    """
    from tree_design.candidates import horizontal_candidates
    from tree_design.upstream import ExistingFolder

    folders = (
        ExistingFolder(directory_path="Uni/PHYS1401", parent_directory="Uni",
                       file_count=4, curation_signal="undetermined"),
        ExistingFolder(directory_path="Physics/PHYS1401",
                       parent_directory="Physics", file_count=9,
                       curation_signal="undetermined"),
    )
    candidates = horizontal_candidates(
        conn, accepted=(), existing_folders=folders, user_labels=(),
        active_domains=(), sensitive_group_ids=frozenset())

    assert {candidate.subject_id for candidate in candidates} == {
        "Uni/PHYS1401", "Physics/PHYS1401"}
    # And each card states its own folder's count, so the two are distinguishable
    # on the canvas rather than merely present in the data.
    assert {candidate.supporting_file_count for candidate in candidates} == {4, 9}


# --- what an adopted folder already holds ------------------------------------------


def test_an_adopted_folder_expects_what_its_own_contents_agree_on(corpus, tmp_path):
    """Adoption is cosmetic until the folder can be CHOSEN, and a node with no
    expected values is never chosen.

    Measured on a real run before this landed: the person's `Uni/CHEM1500` was in
    the tree carrying nothing, the engine's own `Coursework/CHEM1500` carried
    `subject=CHEM1500`, and so the product offered to move a file OUT of the
    right folder and INTO a duplicate it had invented, both wearing the same name
    on screen. That is a worse outcome than never adopting at all.

    Nothing is invented. §5.4 forbids composing a value -- "those names emerge
    from validated facts" -- so the folder is asked what its own files already
    settled, through P6's preferred-fact surface, and gets an expectation only
    where they AGREE. This corpus's three files agree that the school is
    Columbia.
    """
    from tree_design.upstream import settled_values_in_directory

    directory = put_in_folder(corpus, tmp_path, "Business", ("syllabus", "hw3"))
    values = settled_values_in_directory(
        corpus.conn, directory_path=directory)

    assert ("subject", "BUSIB 4300") in {
        (value.field_ref, value.canonical_value) for value in values}


def test_a_folder_whose_files_disagree_expects_nothing_at_that_field(corpus,
                                                                    tmp_path):
    """The negative twin, in the same directory as the test above -- which is
    what makes it a twin rather than a second scenario.

    Those same three files hold TWO subjects between them. A folder holding two
    courses is not a folder about either, and answering with the majority value
    would make the product claim an expectation the person's own filing
    contradicts -- turning a mixed folder into a magnet for half its contents.
    """
    from tree_design.upstream import settled_values_in_directory

    values = settled_values_in_directory(
        corpus.conn, directory_path=str(tmp_path))

    assert not [value for value in values if value.field_ref == "subject"]


def test_the_adopted_node_carries_those_expectations_into_the_tree(corpus,
                                                                  tmp_path):
    """The seam above, reaching the node -- which is the only place it counts.

    §6.2 scores a destination on its expected values, so a folder that agrees
    about something and does not SAY so in the tree is still a folder nothing can
    be filed into. This is the wire between the two.
    """
    directory = put_in_folder(corpus, tmp_path, "Business", ("syllabus", "hw3"))
    seed_folder(corpus, directory, str(tmp_path))
    result = design(corpus, dec=decisions(
        branch_group_ids=("g_columbia_coursework", directory)))

    node = adopted(result, corpus.conn, directory)
    assert node is not None
    assert ("subject", "BUSIB 4300") in {
        (value.field, value.value) for value in node.expected_values}


def test_an_adopted_folder_names_the_accepted_groups_it_already_holds(corpus,
                                                                     tmp_path):
    """`00`:100 lists this by name among what the person should see about their
    own folder: "which extracted facts AND ACCEPTED GROUPS overlap with it".

    It is also what makes adoption work at all. §6.3 scores a destination over
    four weighted channels, and `ACCEPTED_GROUP` is two of the seven points. A
    folder the person made is not built FROM a group, so without this it carries
    only `DIRECT_FACT` -- 3/7, against a 0.5 threshold -- and every file in it
    abstains `no_supported_destination`. Measured exactly that way: adopting the
    folders sent four files that had been placing fine back to abstaining.

    The association is read, not assumed. These files are in the group and in the
    folder; saying so takes nothing from the group and invents nothing about the
    folder.
    """
    directory = put_in_folder(corpus, tmp_path, "Business", ("syllabus", "hw3"))
    seed_folder(corpus, directory, str(tmp_path))
    result = design(corpus, dec=decisions(
        branch_group_ids=("g_columbia_coursework", directory)))

    node = adopted(result, corpus.conn, directory)
    assert node is not None
    assert "g_columbia_coursework" in node.associated_group_ids


def test_a_folder_holding_none_of_a_groups_files_claims_no_group(corpus,
                                                                tmp_path):
    """The negative twin. An association is a fact about overlap, so a folder
    that overlaps nothing claims nothing -- otherwise every adopted folder would
    inherit every accepted group in the corpus and each would score as though it
    held the whole collection."""
    empty = tmp_path / "Somewhere Else"
    empty.mkdir()
    seed_folder(corpus, str(empty), str(tmp_path))
    result = design(corpus, dec=decisions(
        branch_group_ids=("g_columbia_coursework", str(empty))))

    node = adopted(result, corpus.conn, str(empty))
    assert node is not None
    assert node.associated_group_ids == ()


def test_an_expectation_the_whole_corpus_shares_is_not_recorded(corpus,
                                                               tmp_path):
    """The fourth appearance of one mistake, and the reason to name it as a class.

    V5 failed a whole candidate for one level's fault, V2 failed a whole tree for
    one level's, `_project` truncated a whole branch for one level's -- and here a
    folder claims an expectation that distinguishes it from nothing.

    Every file in this corpus is Columbia's. A folder saying "I expect Columbia"
    therefore says nothing about which folder a Columbia file belongs in: it
    matches all of them, and once several adopted folders all match, §6.10 calls
    that multiple supported homes and sends the file to a model. Measured: six
    files, four adopted folders each expecting the one term the whole corpus
    shares, and every file abstained.

    So an expectation is kept only where the corpus DIVIDES on it -- the same
    test V2 applies to a level, applied to a folder.
    """
    from tree_design.upstream import settled_values_in_directory

    values = settled_values_in_directory(
        corpus.conn, directory_path=str(tmp_path))

    assert not [value for value in values if value.field_ref == "school"], (
        "every file in this corpus is Columbia's, so expecting Columbia "
        "distinguishes this folder from none of them")


def test_one_file_agreeing_with_itself_is_not_a_folder_expectation(corpus,
                                                                  tmp_path):
    """The fifth appearance of the same mistake, found by running the command
    over a corpus with a staging folder in it.

    A person had `Scans/` holding one scanned retainer agreement. That single
    file settled `subject=CV20261234`, the folder "agreed" with it unanimously --
    a set of one is always unanimous -- and `Scans` became a legal destination
    expecting that matter. The product then offered to file a deposition
    transcript INTO A FOLDER CALLED SCANS.

    One file agreeing with itself is evidence about the FILE. It becomes evidence
    about the FOLDER only when a second file agrees, which is the difference
    between a folder someone curated and a folder something landed in.
    `TreeLimits.tiny_folder_max_files` already carries this idea: a folder of one
    file is the tiny case, and the design has always known it says little.
    """
    from tree_design.upstream import settled_values_in_directory

    alone = put_in_folder(corpus, tmp_path, "Scans", ("lab",))
    together = put_in_folder(corpus, tmp_path, "Business", ("syllabus", "hw3"))

    assert settled_values_in_directory(corpus.conn, directory_path=alone) == ()
    assert [value.canonical_value for value
            in settled_values_in_directory(corpus.conn, directory_path=together)
            ] == ["BUSIB 4300"]


def test_one_file_speaking_in_a_folder_of_two_is_not_a_folder_expectation(
        corpus, tmp_path):
    """`104` R-87. The sixth appearance, and the half the folder-size floor
    misses.

    The floor above counts the files IN the folder. §5.11 counts a silent file
    as silent -- rightly: a file that says nothing has not disagreed with
    anything -- so a folder holding two files where only ONE settles a field is
    unanimous at that field on the strength of one file, and clears a floor
    written about folder size.

    Measured on the walkthrough: `old stuff` held a PHYS1401 problem set and one
    other thing, claimed `work_type = problem set` from the first, and then tied
    with the course folder the same run had just proposed -- three more problem
    sets abstained between the two, and the folder somebody drops things into
    had become a rival destination profile for a course.

    Here: `syllabus` states `work_type = Syllabus` and `lab` states no
    `work_type` at all. One file agreeing with itself is evidence about the
    FILE, whether the folder around it holds one file or ten.
    """
    from tree_design.upstream import settled_values_in_directory

    one_spoke = put_in_folder(corpus, tmp_path, "old stuff", ("syllabus", "lab"))
    values = settled_values_in_directory(corpus.conn, directory_path=one_spoke)

    assert not [value for value in values if value.field_ref == "work_type"], (
        "one file stated the kind and the other said nothing; the folder claimed "
        f"{[value.canonical_value for value in values]} from it")


def test_two_files_that_agree_still_make_a_folder_expectation(corpus, tmp_path):
    """The discriminating half of `104` R-87: this is a floor, not a ban.

    Two files that both settle the same subject are what the design has always
    meant by a folder the person curated, and the ruling changes nothing about
    them. Stated separately from the floor above so that a change which quietly
    emptied every adopted folder would fail here rather than pass twice.
    """
    from tree_design.upstream import settled_values_in_directory

    together = put_in_folder(corpus, tmp_path, "Business", ("syllabus", "hw3"))
    assert [(value.field_ref, value.canonical_value) for value
            in settled_values_in_directory(corpus.conn, directory_path=together)
            ] == [("subject", "BUSIB 4300")]


def test_the_folder_keeps_its_name_when_it_may_claim_nothing(corpus, tmp_path):
    """`104` R-87 is Q-D's REFINEMENT and not its removal.

    An adopted folder that may no longer claim a value off one file is still in
    the tree, still `existing`, still carrying its real path, and still wearing
    its own name -- which is a channel of its own: `placement.index` writes
    `display_label` as a source field and `retrieve` matches it separately from
    `expected_values`. A folder called `PHYS1401` is found by a file that names
    PHYS1401 whatever its contents have or have not said.
    """
    folder = put_in_folder(corpus, tmp_path, "old stuff", ("syllabus", "lab"))
    seed_folder(corpus, folder, str(tmp_path), files=2)

    result = design(corpus, dec=decisions(
        branch_group_ids=("g_columbia_coursework", folder)))
    node = adopted(result, corpus.conn, folder)

    assert node is not None, "the folder was dropped rather than refined"
    assert node.node_type == EXISTING
    assert node.display_label == "old stuff"
    assert node.expected_values == ()


def test_a_kind_that_merely_leads_is_an_expectation_but_not_what_a_folder_is_for(
        corpus, tmp_path):
    """UNANIMITY IS NOT COVERAGE, and the two answers must stay different.

    A folder holding two syllabi and a lab report: two of them say what kind of
    thing they are and agree, the third says nothing, and a file that says
    nothing has not disagreed -- §5.11 permits a tree "even if some files remain
    unresolved" -- so the folder unanimously expects `Syllabus` and that is the
    right answer for §6.2.

    It is the wrong answer to a different question. `00`:100 treats a folder the
    person made as a strong expression of intent, and P11 refuses to carry a file
    OUT of one on an artifact kind alone -- but only where the kind is what the
    folder IS. Measured on the owner's own disk, 2026-09-05: `Kid` holds two
    files and BOTH are report cards; `Desktop` holds four résumés among eleven
    things. Both fold to one `work_type` unanimously. One was made for that kind
    and the other is where things land, and the nine résumés this product places
    exactly are the difference between the two answers.

    So `settled_values_stated_by_every_file` keeps only what every file states,
    and this is the corpus where the two functions must not agree. Collapse them
    and `Desktop` becomes a folder made for résumés.

    **TWO SPEAKERS AND ONE SILENT FILE, since `104` R-87.** This read `syllabus`
    and `lab` -- one speaker -- and that shape is now refused by both functions,
    because one file agreeing with itself is evidence about the file. The
    distinction this test exists for is untouched by that floor and the measured
    case it comes from was never one file either: `Desktop`'s four résumés among
    eleven things are four speakers and seven silent files. So the fixture is
    the shape the docstring always described.
    """
    from p10.p6_fixtures import SeededCorpus
    from tree_design.upstream import (settled_values_in_directory,
                                      settled_values_stated_by_every_file)

    SeededCorpus(conn=corpus.conn, subjects=corpus.files).add_subject(
        tmp_path, "second syllabus", "BUSIB 4300 Syllabus, second copy",
        (("work_type", "Syllabus"),))
    leading = put_in_folder(corpus, tmp_path, "Desk",
                            ("syllabus", "second syllabus", "lab"))

    assert "Syllabus" in [
        value.canonical_value for value
        in settled_values_in_directory(corpus.conn, directory_path=leading)], (
        "a kind two files name and a third is silent about is still what the "
        "folder expects, and §6.2 needs that answer")
    assert not [value for value
                in settled_values_stated_by_every_file(
                    corpus.conn, directory_path=leading)
                if value.field_ref == "work_type"], (
        "two files of three naming a kind made the folder look built for that "
        "kind, which is `Desktop` described as `Kid`")


def test_a_level_that_makes_no_folder_is_not_counted_in_the_summary():
    """§5.5's sentence is what a person reads before choosing a shape, so it must
    not name folders the shape would not build.

    It read "This option would create 0 school, 1 term, 3 subject, and 0
    work_type" on a real run. Two of those levels produce nothing -- `_project`
    skips a level with no values, and V2 skips one that does not divide -- so the
    sentence offered four levels where the tree has two, and a person choosing
    between shapes was reading about folders neither shape contains.

    THE EXPECTATION BELOW CHANGED 2026-09-04, AND THE DOCSTRING ABOVE IS WHY.
    It used to be `"1 term, and 3 subject"`, which applied only the FIRST of the
    two rules this docstring names: it dropped the zero-value levels and kept
    `term`, a level with exactly one value. One value is one folder and one
    folder divides nothing, so V2 does not build it -- the second rule, stated
    here from the beginning and not implemented until now.

    Verified against the built tree rather than argued: on `00`:78's own path
    (school 1, term 1, course 1, work_type 3) the option's children are
    `Academics/Homework`, `Academics/Lectures`, `Academics/Syllabus` -- three
    folders under one level, while the sentence promised four levels. So `term`
    here is a folder that is not built, exactly like `school` and `work_type` at
    zero.

    This is NOT a relaxation to accommodate a new producer. `work_type` gaining a
    producer is only what made the case REACHABLE: until a third level could
    divide, every branch arriving here had nothing dividing at all, and the
    caller answered those earlier with its own "would create no folders"
    sentence, so this one never spoke for a mixed branch.
    """
    from tree_design.candidates import _summarise

    assert _summarise({"school": 0, "term": 1, "subject": 3, "work_type": 0}) == (
        "3 subject")
    # A level with one value is dropped for the same reason a level with none is.
    assert _summarise({"school": 0, "term": 1}) == "no child branches"
    assert _summarise({"school": 0}) == "no child branches"
