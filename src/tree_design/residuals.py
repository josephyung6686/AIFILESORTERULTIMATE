# src/tree_design/residuals.py
"""§7.2-§7.4: the definitions and the enablement model. P11 runs the workflow.

A residual template is not a domain template. A domain template builds a deep
meaningful hierarchy for a recurring area of life; a residual template provides a
"safe, intentionally broad destination" for a file with no reliable deeper
association. §7.2 names the failure it prevents by example: `Random PDF Things`,
`Important Screenshot`, `Miscellaneous Documents`, `Travel/Gate B12`.

The nine names are fixed. Their slot VALUES are deferred and arrive injected: the
accepted evidence patterns, expected file types, sensitivity restrictions,
optional shallow subfolders and maximum depth per template, plus the five default
parent locations §7.3 leaves unstated. None is invented here.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

from tree_design.config import ConfigurationRequired
from tree_design.records import Node, derive_accepts_placement
from tree_design.vocabulary import (
    DISABLE,
    MERGE_RESIDUAL,
    REPLACE_WITH_EXISTING,
    RESIDUAL,
    RESIDUAL_LIBRARY_ACTIONS,
    RESIDUAL_DEFAULT_PARENTS,
    RESIDUAL_DISPOSITIONS,
    RESIDUAL_SLOTS,
    RESIDUAL_TEMPLATE_NAMES,
    RESIDUAL_TREATMENTS,
    USER_CREATED,
    check,
)

@dataclass(frozen=True)
class ResidualTemplate:
    """§7.2's eight attribute slots, all eight, for one template."""

    template_name: str
    display_name: str
    default_parent_location: tuple[str, ...] | None
    accepted_evidence_patterns: tuple[str, ...]
    expected_file_types: tuple[str, ...]
    sensitivity_restrictions: tuple[str, ...]
    optional_shallow_subfolders: tuple[str, ...]
    max_permitted_depth: int
    treatment: str
    user_defined: bool

    def __post_init__(self) -> None:
        check(self.treatment, RESIDUAL_TREATMENTS, name="treatment")
        if not self.display_name:
            raise ConfigurationRequired(
                f"{self.template_name!r} has no display name; §7.2 makes the "
                "recommended display name one of the eight slots"
            )
        for label in self.default_parent_location or ():
            if "/" in label or "\\" in label:
                raise ConfigurationRequired(
                    "a default parent location is a `display_label` chain — a "
                    "recommended placement in the TREE, not on disk (resolution "
                    "B3). Nothing about a residual node makes it path-bearing."
                )


@dataclass(frozen=True)
class ResidualChoice:
    """One §7.4 decision the user made about one template."""

    template_name: str
    action: str
    disposition: str | None
    display_label: str | None
    parent_node_id: str | None
    root_anchor: str | None
    merge_into: str | None
    replaces_node_id: str | None

    def __post_init__(self) -> None:
        check(self.action, RESIDUAL_LIBRARY_ACTIONS, name="residual action")


def build_library(
    slot_values: Mapping[str, Mapping[str, object]],
    *,
    user_defined: Sequence[ResidualTemplate] = (),
) -> Mapping[str, ResidualTemplate]:
    """The nine, plus whatever residual areas this user authored.

    `default_parent_location` is the one slot whose absence is legal: §7.3 states
    a default for four templates and leaves five unstated, so `None` is a value
    rather than a gap. Every other slot missing is a configuration gap.
    """
    library: dict[str, ResidualTemplate] = {}
    for name in RESIDUAL_TEMPLATE_NAMES:
        values = slot_values.get(name)
        if values is None:
            raise ConfigurationRequired(
                f"the residual library has no slot values for {name!r}. §7.3 fixes "
                "the nine names; their contents are authored and none is invented."
            )
        missing = [
            slot for slot in RESIDUAL_SLOTS
            if slot != "default_parent_location" and slot not in values
        ]
        if missing:
            raise ConfigurationRequired(
                f"{name!r} is missing the slot value(s) {sorted(missing)}. §7.2 "
                "defines eight attributes per template and P10 authors none of "
                "their contents."
            )
        parent = values.get("default_parent_location",
                            RESIDUAL_DEFAULT_PARENTS.get(name))
        library[name] = ResidualTemplate(
            template_name=name,
            display_name=str(values["display_name"]),
            default_parent_location=None if parent is None else tuple(parent),
            accepted_evidence_patterns=tuple(values["accepted_evidence_patterns"]),
            expected_file_types=tuple(values["expected_file_types"]),
            sensitivity_restrictions=tuple(values["sensitivity_restrictions"]),
            optional_shallow_subfolders=tuple(values["optional_shallow_subfolders"]),
            max_permitted_depth=int(values["max_permitted_depth"]),
            treatment=str(values["treatment"]),
            user_defined=False,
        )
    for template in user_defined:
        if not template.user_defined:
            raise ConfigurationRequired(
                f"{template.template_name!r} is offered as a user-defined area but "
                "is not marked as one; the product ships none of §7.3's example "
                "areas and the flag is how a shipped template is told from an "
                "authored one"
            )
        library[template.template_name] = template
    return library


def project_residual_nodes(
    library: Mapping[str, ResidualTemplate],
    choices: Sequence[ResidualChoice],
    *,
    plan_version_id: str,
    handling_class_for_template: Callable[[str], str],
    mint_node_id: Callable[[], str],
    existing_nodes: Mapping[str, Node],
) -> tuple[Node, ...]:
    """Turn the user's §7.4 decisions into nodes. Disabled decisions into none.

    §7.4: "Once the user approves the desired residual branches, those branches
    become legal nodes in the frozen destination tree. The LLM may choose among
    them later, but it may not create additional generic destinations." An
    enabled residual branch is an ordinary member of the legal set through the
    ordinary `accepts_placement` derivation — P11 needs no residual-specific
    legality path — and a template the user did not enable has no node at all.
    """
    nodes: list[Node] = []
    by_name: dict[str, Node] = {}
    ordinal = 0

    decided: set[str] = set()
    for choice in choices:
        if choice.template_name in decided:
            raise ConfigurationRequired(
                f"{choice.template_name!r} carries more than one §7.4 decision. "
                "The user makes ONE decision per residual template; two produced "
                "two branches with the same display name and nothing said which "
                "one P11 would place into."
            )
        decided.add(choice.template_name)
        template = library.get(choice.template_name)
        if template is None:
            raise ConfigurationRequired(
                f"{choice.template_name!r} is not in the residual library. §7.2 "
                "exists to stop exactly this: a plausible-sounding destination "
                "nobody defined."
            )
        if choice.action == DISABLE:
            # §7.4's whole enforcement mechanism, and the only action that makes
            # no node: "a template the user did not enable has no node", so no
            # placement decision can name it and no model can return it. The
            # other five all put a node in the tree.
            #
            # There used to be a second skip here testing membership of a
            # `_CREATING_ACTIONS` set that was exactly the five non-`disable`
            # actions. `ResidualChoice.__post_init__` already closes the action
            # against `RESIDUAL_LIBRARY_ACTIONS`, so the two checks were the same
            # check twice and each made the other unreachable — deleting either
            # one alone left the suite green.
            continue
        if choice.disposition is None:
            raise ConfigurationRequired(
                f"{choice.template_name!r} is enabled without a disposition. §7.4 "
                "makes the user decide whether a residual template is a real "
                "physical destination, a review-only category, or a policy to "
                "leave files in place, and the three behave differently in P11."
            )
        check(choice.disposition, RESIDUAL_DISPOSITIONS, name="disposition")

        if choice.action == MERGE_RESIDUAL:
            target = by_name.get(choice.merge_into or "")
            if target is None:
                raise ConfigurationRequired(
                    f"{choice.template_name!r} merges into "
                    f"{choice.merge_into!r}, which is not an enabled residual "
                    "branch in this plan version"
                )
            by_name[choice.template_name] = target
            continue

        label = choice.display_label or template.display_name
        handling_class = handling_class_for_template(choice.template_name)
        if choice.action != REPLACE_WITH_EXISTING and not (choice.root_anchor or ""):
            raise ConfigurationRequired(
                f"{choice.template_name!r} is enabled without a root anchor. §7.3 "
                "leaves five of the nine default parents unstated, so the anchor "
                "is the user's to choose and P10 has none to fall back on."
            )

        if choice.action == REPLACE_WITH_EXISTING:
            existing = existing_nodes.get(choice.replaces_node_id or "")
            if existing is None:
                raise ConfigurationRequired(
                    f"{choice.template_name!r} replaces node "
                    f"{choice.replaces_node_id!r}, which is not an existing node "
                    "in this plan version"
                )
            node = Node(
                node_id=existing.node_id,
                plan_version_id=plan_version_id,
                node_type=existing.node_type,
                display_label=choice.display_label or existing.display_label,
                parent_node_id=existing.parent_node_id,
                root_anchor=existing.root_anchor,
                ordinal=existing.ordinal,
                associated_group_ids=existing.associated_group_ids,
                explanation=(
                    f"The user mapped the {choice.template_name!r} residual "
                    f"template onto their existing {existing.display_label!r} "
                    "folder rather than creating a new one."
                ),
                node_role=RESIDUAL,
                accepts_placement=existing.accepts_placement,
                handling_class=existing.handling_class,
                origin_node_id=existing.origin_node_id,
                existing_path=existing.existing_path,
                disposition=choice.disposition,
                protected_movement_permitted=existing.protected_movement_permitted,
            )
        else:
            parent_labels = template.default_parent_location or ()
            # A freshly minted node is its OWN lineage origin (open question 5),
            # so the id is bound once and used twice. Constructing with
            # `origin_node_id=""` and patching afterwards cannot work:
            # `Node.__post_init__` runs `_require` over `origin_node_id` and
            # raises `MalformedTreeRecord` before any later `replace` is reached.
            node_id = mint_node_id()
            node = Node(
                node_id=node_id,
                plan_version_id=plan_version_id,
                node_type=USER_CREATED,
                display_label=label,
                parent_node_id=choice.parent_node_id,
                root_anchor=choice.root_anchor,
                ordinal=ordinal,
                associated_group_ids=(),
                explanation=(
                    f"The user enabled the {choice.template_name!r} residual "
                    f"template as a {choice.disposition} destination"
                    + (f", recommended under {' / '.join(parent_labels)}."
                       if parent_labels else ".")
                ),
                node_role=RESIDUAL,
                accepts_placement=derive_accepts_placement(
                    USER_CREATED, protected_movement_permitted=False),
                handling_class=handling_class,
                origin_node_id=node_id,
                disposition=choice.disposition,
            )
            ordinal += 1

        nodes.append(node)
        by_name[choice.template_name] = node

    return tuple(nodes)
