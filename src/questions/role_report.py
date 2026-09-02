# src/questions/role_report.py
"""What `80` looks like on a screen: the moment, the shortlist, and R6's panel.

`role-1` through `role-5` built every mechanism `80` rules and none of them reached
a person. The proposal step, the declarations, the two gestures and the trigger all
existed, `src/cli.py` imported none of them, and the effect was the failure `84` §5
calls the dominant one in this repo: the parts were right and the wiring was absent,
so R2's once-only friction budget was enforced inside a function no run called.

Three renders, one per moment in the flow, and each is a requirement rather than a
convenience.

**The ask (R1, R2).** `80` §3: the self-description question is triggered by the
first genuinely ambiguous file, never by first run. `80` §4 (R2): the friction budget
is spent ONCE. Both live in `triggers.role_declaration_is_due`, and this module calls
it rather than restating it -- `role_moment_lines` takes the trigger's own two
arguments, neither with a default, so there is no signature under which a caller
prints the ask while forgetting to check whether the person already answered it. R2
is a property of the call rather than a rule somebody has to keep.

**The shortlist (R7).** `80` §5: "position seven versus position one still reads as
ranked to a human". The order arrives injected from the surface that renders it, the
same way `proposal.shortlist_for_question` takes it, and this module supplies none.

**The panel (R6).** `80` §4: "a light, editable settings panel the person can glance
at and adjust anytime, not a one-time gate they went through and now can't see
again." The adjusting half is two gestures that already exist. The panel's whole job
is to show what a person holds and to say those gestures TRULY -- `84` §6: "What the
screen tells a person to type has to be true", which is why the withdrawal line is
tested by running it rather than by reading it.

**Nothing here writes, and nothing here decides.** No connection, no store, no
schema. A render that recorded a role would be a second place a role is established,
and `roles.declare_role` promises to be the only one.

**On words this module does not author.** `80` §6 reserves prompt text to the owner
and R5's no-match WORDING with it. Nothing below is prompt text: none of it is shown
to a model, fingerprinted, or written into an audit record or a cache key. The
no-match case is rendered by SHAPE rather than by a sentence -- same heading, same
offer, no apology -- and the one phrase that names it is `QuestionOption.label`,
which `roles.question_for_role_declaration` already authored and this module reuses
rather than respells.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable

from questions.proposal import ProposalRefused, RoleProposal
from questions.registry import ROLE_KIND
from questions.roles import NOT_LISTED, RoleDeclaration
from questions.triggers import role_declaration_is_due
from questions.vocabulary import SKIPPED_ROLE

#: The two gestures, spelled once. `roles.apply_declarations` and
#: `roles.described_sentences` already name them in their refusals; a third spelling
#: is how a screen comes to tell a person to type a flag that was renamed.
DECLARE_FLAG: str = "--declare-role"
DESCRIBE_FLAG: str = "--describe-role"

#: How a role is withdrawn. Not a third gesture: `--answer <question>=revoke` is
#: P15's general revocation and a role declaration is an ordinary structural
#: question, so the panel names the mechanism that exists rather than asking for one
#: of its own. The question id is built the way `roles._record` builds it, from
#: `ROLE_KIND.kind_id`, so a rename moves both together.
REVOKE_WORD: str = "revoke"


def _withdraw_command(declaration_id: str) -> str:
    return f"--answer {ROLE_KIND.kind_id}:{declaration_id}={REVOKE_WORD}"


def role_moment_lines(*, blocked: Iterable[object],
                      already_declared: Iterable[object]) -> tuple[str, ...]:
    """The ask, when `80` §3's moment has arrived and not otherwise.

    Empty is the normal case and it is most of the time: a run that settled
    everything asks nothing, and a person who has answered once is never asked
    again. Empty rather than a placeholder, because a section that printed "no
    questions about you" every run would be the recurring interruption R2 forbids,
    arriving as reassurance instead of as a question.

    **It promises nothing about where the words go**, and the omission is
    deliberate. `80` §8 suspends the always-local ENFORCEMENT for exactly this one
    item, so "your words stay on this device" is a sentence this build may not be
    able to keep. `proposal.sending_notice` tells the truth about a send in the same
    breath as `00`:200 and tells it on the run that sends, which is the only run that
    knows. This one runs before any sentence exists, so it says what it does know:
    what the answer will not do.
    """
    if not role_declaration_is_due(blocked=blocked,
                                   already_declared=already_declared):
        return ()
    return (
        "Some of what is here could belong to more than one part of your life, and "
        "those are the decisions above that are waiting for you.",
        "If you say what this material is for you, in your own words, this can "
        "offer you the layouts that fit -- and say so plainly when none of them "
        "does.",
        f'    {DESCRIBE_FLAG} me="whatever you would say to somebody who asked"',
        "The name before the = is yours to choose, and it is how you change or "
        "withdraw this later. You can hold as many as you actually hold.",
        "What you say does not become a folder name, and it gives nothing "
        "permission to move, rename or delete a file.",
    )


def _held(role: RoleDeclaration) -> str:
    """One role, said in terms of what it did rather than what it is called."""
    if role.outcome == SKIPPED_ROLE:
        return f"{role.declaration_id} -- put aside for now; nothing is turned on."
    schema = role.activates_schema
    if schema:
        return f'{role.declaration_id} -- turns on the "{schema}" layout.'
    if role.chosen_option is not None and role.chosen_option.option_id == NOT_LISTED:
        # The option's own label, authored where the option was. §16:551 requires
        # this path to be explicit and `80` §6 reserves its wording to the owner, so
        # the panel reuses the one that exists rather than writing a second.
        return (f"{role.declaration_id} -- {role.chosen_option.label.lower()}; "
                "nothing is turned on.")
    return f"{role.declaration_id} -- your own words, kept, and they turn nothing on:"


def _period(role: RoleDeclaration) -> tuple[str, ...]:
    """§16:543's "possibly a time period", shown only when there is one.

    R6's own example is a person who "finishes teaching a course", so a role that
    ends is the case the requirement was written about. A panel that held the period
    and did not show it would make the person guess whether it had taken.
    """
    if role.applies_from and role.applies_until:
        return (f"      true from {role.applies_from} until {role.applies_until}",)
    if role.applies_from:
        return (f"      true from {role.applies_from}",)
    if role.applies_until:
        return (f"      true until {role.applies_until}",)
    return ()


def role_panel_lines(declarations: Iterable[RoleDeclaration]) -> tuple[str, ...]:
    """R6's panel: everything a person currently holds, and how to change each one.

    SEVERAL, in declaration order, and never one. §16:543 is the requirement and the
    shape of this render is the requirement made visible: a panel headed "your role"
    would be the single permanent profession the whole section exists to refuse.

    **Declaration order is not R7's problem.** `80` §5 is about a SHORTLIST -- an
    order the data deliberately does not carry, reintroduced by the geometry of a
    list. These are the person's own declarations in the order they made them, which
    is an order the data does carry and which they chose. Randomising it would move
    a settings panel's rows around between glances.

    Every role carries its own two commands rather than one worked example at the
    foot, because a settings panel where the change control sits next to the thing it
    changes is the shape R6 asks for, and because an example built from the first
    role makes the first role the one the person can act on.
    """
    held = tuple(declarations)
    if not held:
        return ()
    lines = ["Roles you have declared:"]
    for role in held:
        lines.append(f"    {_held(role)}")
        if role.raw_wording:
            lines.append(f'      "{role.raw_wording}"')
        lines.extend(_period(role))
        lines.append(
            f"      {DECLARE_FLAG} {role.declaration_id}=<layout>   change it")
        lines.append(
            f"      {_withdraw_command(role.declaration_id)}   take it back")
    return tuple(lines)


def shortlist_lines(proposal: RoleProposal, *, name: str,
                    order: Callable[[frozenset[str]], Iterable[str]],
                    ) -> tuple[str, ...]:
    """What a proposal offers, in an order the caller supplies, deciding nothing.

    `name` is the declaration id the person's own gesture minted, and it is required
    because without it the commands below would read `--declare-role =academic`,
    which is not a thing anybody can type. `84` §6 again.

    **The no-match case is rendered by shape.** `80` §4 (R5): "none of these" is a
    normal outcome, not an error -- same visual weight, same tone, no apology shape,
    and the raw sentence stays visible. So the sentence is read back either way, the
    heading is the same either way, and the way to declare a role is offered either
    way; the only difference is that there are no candidate lines. The words that
    would NAME the outcome are the owner's under `80` §6 and this module writes none.

    **Nothing here activates anything.** These are lines of text. The person types
    one of the commands or does not, and `roles.apply_declarations` -- which takes
    only strings a person typed -- is the single path to `store.activated_schemas`.
    `80` §7's second forbidden thing stays a property of the import graph.
    """
    if order is None:
        raise ProposalRefused(
            "a shortlist with no order supplied would be rendered in whichever "
            "order this set happens to iterate, and `80` §5 (R7) forbids exactly "
            "that: a presentation must not encode an order the data does not carry")
    shown = tuple(order(proposal.candidates))
    if len(shown) != len(proposal.candidates) or frozenset(shown) != proposal.candidates:
        raise ProposalRefused(
            f"the order returned {sorted(shown)} for candidates "
            f"{sorted(proposal.candidates)}. An order arranges a shortlist; one that "
            "adds, drops or repeats a candidate is a second proposal step in the "
            "layer that renders the first one")
    lines = [
        "What you said about yourself:",
        f'    "{proposal.self_description}"',
        "Layouts this product has that could hold material like that:",
    ]
    lines.extend(f"    {DECLARE_FLAG} {name}={candidate}" for candidate in shown)
    lines.append(
        f"You can name any other layout instead, and `{DECLARE_FLAG} {name}="
        f"{NOT_LISTED}` is an answer of its own that turns nothing on. Your words "
        "above are kept either way.")
    return tuple(lines)
