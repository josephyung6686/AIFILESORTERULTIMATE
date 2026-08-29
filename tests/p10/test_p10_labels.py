"""P10 Amendment A — the level's display label, authored PER CONTEXT.

`TemplateDimension` carries `role_ref`, `order_index`, `requirement`,
`metadata_only` and `retrieval_rationale`, and no label. So before this
amendment the internal key WAS the shipped string, and the sentence a user reads
under a folder said "3 of this branch's files record work_type = 'Homework'".
`00` §5.1 asks labels to "reflect the user's vocabulary rather than a universal
corporate taxonomy", and nobody says "it's in the work_type folder".

The label belongs on `TemplateApplicability`, not on the definition, because ONE
role reads differently per schema: `work_type` is homework, exams and labs to a
student and figures, drafts and protocols to a researcher. `role_bindings` is
already the per-context row and already has a live reader at `routing.py`, so
that is where the name goes -- next to the field it names.

**The chain this file pins end to end**, because a label with no reader is the
same defect as the missing label it replaces:

    TemplateApplicability.role_bindings[].label   (authored, per schema)
      -> routing.evaluate_composition
        -> ResolvedDimension.display_label        (was hard-coded None)
          -> LevelEvidence.dimension_label
            -> Node.explanation                   (what the user actually reads)
"""
from __future__ import annotations

import pytest

from tree_design.materialise import materialise_branch, project_branch_nodes
from tree_design.routing import evaluate_composition
from tree_design.templates import (
    CompositionConflict,
    FragmentRef,
    MalformedTemplateRecord,
    RoleBinding,
)
from tree_design.vocabulary import C4

from p10.test_p10_materialise import (
    ACCEPTED, ALWAYS_ORDINARY, NO_CONTEXT, ONE_CLASS, PROTECTED_CLASSES,
    _candidate, _ids, _parent, seeded,  # noqa: F401 -- `seeded` is a fixture
)
from p10.test_p10_routing import (
    ALWAYS, KIND, RANK, SUBJECT, _catalogue, _context, _definition, _group, _row,
)


# --------------------------------------------------------------------------
# The record: a binding says how THIS schema names the level it binds.
# --------------------------------------------------------------------------

def test_a_role_binding_names_the_level_in_the_schemas_own_words():
    binding = RoleBinding("work_type", "work_type", "Assignment type")
    assert binding.role_ref == "work_type"
    assert binding.field_ref == "work_type"
    assert binding.label == "Assignment type"


def test_a_binding_with_no_label_ships_the_internal_key_as_the_ui_string():
    """The label is REQUIRED, and its absence is tested rather than assumed.

    An optional label is a label nobody authors: every row would keep shipping
    `work_type`, and the field would join the list of columns with no writer.
    """
    with pytest.raises(TypeError):
        RoleBinding("work_type", "work_type")
    with pytest.raises(MalformedTemplateRecord):
        RoleBinding("work_type", "work_type", "   ")


def test_a_label_is_a_display_name_and_never_a_path_fragment():
    """P12 alone composes paths (resolution B3). A label holding a separator
    would put one into a folder name by the back door."""
    with pytest.raises(MalformedTemplateRecord):
        RoleBinding("work_type", "work_type", "Assignments/Homework")


# --------------------------------------------------------------------------
# Routing: the authored label reaches the composed level.
# --------------------------------------------------------------------------

#: The fixture fragment that defines each role. A definition composing no
#: fragment must state its own privacy floor (Amendment B), so a recipe here
#: names the fragments its roles come from rather than carrying a floor of its
#: own — these tests are about labels, and a second way to satisfy C7 in the
#: fixture would be a second thing that can drift.
FRAGMENT_FOR_ROLE = {"subject": SUBJECT, "artifact_kind": KIND}


def _compose(conn, rows, roles, groups, domains):
    refs = tuple(FragmentRef(FRAGMENT_FOR_ROLE[role].fragment_id, 1)
                 for role in roles)
    definition = _definition("t.fixture", refs, roles)
    catalogue = _catalogue((SUBJECT, KIND), (definition,), rows)
    return evaluate_composition(
        conn, catalogue, _context(domains, groups), rows,
        privacy_rank=RANK, satisfies_purpose_profile=ALWAYS)


def test_the_composed_level_carries_the_label_and_not_the_role_key(conn):
    """RED before the amendment: `routing.py` hard-coded `display_label=None`,
    so the only producer of this field wrote a placeholder and no consumer read
    it."""
    row = _row("a.student", "t.fixture", "academic",
               [("subject", "subject", "Course"),
                ("artifact_kind", "work_type", "Assignment type")])
    candidate = _compose(conn, (row,), ("subject", "artifact_kind"),
                         (_group("g1", "academic", ("f1",)),), ("academic",))

    labels = {d.role_ref: d.display_label for d in candidate.resolved_dimensions}
    assert labels == {"subject": "Course", "artifact_kind": "Assignment type"}
    # The point of the amendment: what ships is not what the key says.
    assert "work_type" not in set(labels.values())


def test_one_role_reads_differently_in_two_schemas(conn):
    """THE amendment, stated as the case that forced it.

    `artifact_kind` binds to the same P6 field in both rows and is named
    differently in each. A label held on the DEFINITION -- one recipe, one name
    -- cannot pass this test, which is precisely why it is not held there.
    """
    student = _row("a.student", "t.fixture", "academic",
                   [("artifact_kind", "work_type", "Assignment type")])
    researcher = _row("a.researcher", "t.fixture", "research",
                      [("artifact_kind", "work_type", "Figure or draft")])

    for row, schema, expected in ((student, "academic", "Assignment type"),
                                  (researcher, "research", "Figure or draft")):
        candidate = _compose(conn, (row,), ("artifact_kind",),
                             (_group("g1", schema, ("f1",)),), (schema,))
        (dimension,) = candidate.resolved_dimensions
        assert dimension.field_ref == "work_type"
        assert dimension.display_label == expected


def test_two_rows_naming_one_field_differently_refuse_rather_than_pick(conn):
    """Two contexts in one branch, one field, two names, and no rule that says
    which is shown. That is C4's shape -- a role resolving more than one way --
    and the answer is the same one C4 already gives: surface it, pick nothing.

    Picking the first would make the shipped name depend on the order the rows
    were listed in, which is the defect `_topological`'s `unordered` already
    refuses one field over.
    """
    student = _row("a.student", "t.fixture", "academic",
                   [("artifact_kind", "work_type", "Assignment type")])
    other = _row("a.other", "t.fixture", "research",
                 [("artifact_kind", "work_type", "Figure or draft")])
    groups = (_group("g1", "academic", ("f1",)),
              _group("g2", "research", ("f2",)))

    with pytest.raises(CompositionConflict) as raised:
        _compose(conn, (student, other), ("artifact_kind",), groups,
                 ("academic", "research"))
    assert raised.value.gate == C4
    assert "artifact_kind" in raised.value.conflicting


def test_two_rows_agreeing_on_the_name_compose_without_complaint(conn):
    """The negative twin of the test above.

    Without it, a router that refused EVERY multi-row composition would pass the
    refusal test and still be wrong: the conflict is two NAMES, not two rows.
    """
    student = _row("a.student", "t.fixture", "academic",
                   [("artifact_kind", "work_type", "Assignment type")])
    other = _row("a.other", "t.fixture", "research",
                 [("artifact_kind", "work_type", "Assignment type")])
    groups = (_group("g1", "academic", ("f1",)),
              _group("g2", "research", ("f2",)))

    candidate = _compose(conn, (student, other), ("artifact_kind",), groups,
                         ("academic", "research"))
    (dimension,) = candidate.resolved_dimensions
    assert dimension.display_label == "Assignment type"


# --------------------------------------------------------------------------
# The consumer: what the user actually reads under the folder.
# --------------------------------------------------------------------------

def _nodes_for(seeded, label):
    candidate = _candidate(("work_type", "work_type"))
    candidate = candidate.__class__(
        **{**candidate.__dict__,
           "resolved_dimensions": tuple(
               d.__class__(**{**d.__dict__, "display_label": label})
               for d in candidate.resolved_dimensions)})
    _, evidence = materialise_branch(
        seeded.conn, candidate, branch_node_id="n_academics",
        members=seeded.members("syllabus", "hw3", "lab"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES)
    return project_branch_nodes(
        evidence, ACCEPTED, parent=_parent(), plan_version_id="plan_1",
        mint_node_id=_ids(), handling_class_for=ALWAYS_ORDINARY,
        template_context_for=NO_CONTEXT)


def test_a_node_explains_itself_in_the_users_words_not_the_field_key(seeded):
    """§5.12 requires every node to state what caused it to appear, and this is
    the sentence that does it. Before the amendment it read `work_type =
    'Homework'`, naming a database column at the user."""
    homework = next(n for n in _nodes_for(seeded, "Assignment type")
                    if n.display_label == "Homework")
    assert "Assignment type" in homework.explanation
    assert "work_type" not in homework.explanation


def test_a_level_with_no_authored_label_still_explains_itself(seeded):
    """The negative twin.

    A level may be constructed without a label -- every direct
    `ResolvedDimension` in the suite is -- and the explanation is REQUIRED by
    `Node.__post_init__`, so the fallback has to name the field rather than
    print `None`. Without this test, a consumer that read the label
    unconditionally would leave a node explaining itself as "record None =".
    """
    homework = next(n for n in _nodes_for(seeded, None)
                    if n.display_label == "Homework")
    assert "work_type" in homework.explanation
    assert "None" not in homework.explanation


def test_the_label_reaches_its_consumer_by_import_and_by_call():
    """The reachability guard. A behavioural test proves the chain works today;
    this proves it is still WIRED, and names where it would break.

    `ResolvedDimension.display_label` spent its whole life with one producer
    writing `None` and no consumer at all, passing every test in the suite. A
    field can be populated, stored, asserted on in a record test and still reach
    nothing. So this parses `materialise.py` and asserts BOTH links by structure:
    the level carries the dimension's label, and the explanation asks `_label_of`
    for a name rather than printing the field key.
    """
    import ast
    import inspect

    from tree_design import materialise

    tree = ast.parse(inspect.getsource(materialise))

    carried = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.keyword) and node.arg == "dimension_label"
        and isinstance(node.value, ast.Attribute)
        and node.value.attr == "display_label"
    ]
    assert carried, (
        "materialise no longer copies ResolvedDimension.display_label into "
        "LevelEvidence.dimension_label; the authored label stops at routing")

    called = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and getattr(node.func, "id", None) == "_label_of"
    ]
    assert called, (
        "nothing calls _label_of, so the level's name reaches no explanation "
        "and the label is a stored value with no reader")
