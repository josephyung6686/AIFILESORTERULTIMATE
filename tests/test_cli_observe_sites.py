"""`104` §7 Phase 1 step 6's constraint, before any of its wiring.

Observe-only means two things at once and only one of them is about behaviour.
The behaviour is that B, C, D and E run and apply nothing. The CONSTRAINT is that
they run HERE and nowhere else: every prompt they would send is a D2 draft, the
packet's own status is `unratified`, and `104` §13 keeps a standing count of "0
cloud calls with unratified prompts".

A count nobody enforces is a hope, so the enforcement is in code and these are its
tests. They are written before the sites are wired on purpose: a guard added after
the callers exist is a guard whose first version was never the one under test.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
for _path in (str(_ROOT), str(_ROOT / "src")):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import cli  # noqa: E402
from llm_harness.prompt_library import (  # noqa: E402
    DraftNotInManifest, draft_bytes, draft_row, drafts_status,
)
from llm_harness.vocabulary import (  # noqa: E402
    A_FACT, B_GROUP, C_PLACEMENT, D_RESIDUAL, E_TEMPLATE,
)
from readers.model_deepseek import CLOUD  # noqa: E402
from readers.model_ollama import LOCAL  # noqa: E402

#: The packet's winner per site, `105` §9. B is `anchors-first-v2` and not the v3
#: the wave named: no v3 file and no v3 row exists in the library or the manifest,
#: and v2 is the newest B row that does. The substitution is recorded here so it is
#: visible to a reader rather than only to whoever read the commit.
WINNERS = {
    B_GROUP: "b_group.unratified.anchors-first-v2.2026-09-06",
    C_PLACEMENT: "c_placement.unratified.eliminate-v2.2026-09-06",
    D_RESIDUAL: "d_residual.unratified.ladder.2026-09-06",
    E_TEMPLATE: "e_template.unratified.what-a-person-opens-v2.2026-09-06",
}


def test_the_observe_set_is_the_four_sites_that_have_no_ratified_text():
    assert cli.OBSERVE_CALL_SITES == frozenset(
        {B_GROUP, C_PLACEMENT, D_RESIDUAL, E_TEMPLATE})


def test_a_site_is_never_both_wired_and_observed():
    """A site in both would apply its answer and discard it, and there is no run
    that could be correct. Asserted in the module as well, so the import fails
    before a corpus is read rather than here."""
    assert not (cli.WIRED_CALL_SITES & cli.OBSERVE_CALL_SITES)
    assert cli.WIRED_CALL_SITES == frozenset({A_FACT})


@pytest.mark.parametrize("site", sorted(WINNERS))
def test_an_observe_site_is_refused_a_cloud_model(site):
    """The count `104` §13 keeps, kept in code. Unratified text is text nobody has
    agreed to send: on this device that is a question of taste, and over the
    internet it is a person's dossier reaching a provider under a prompt their
    owner never approved, and it cannot be taken back."""
    assert cli.observe_locality_permits(site, LOCAL) is True
    assert cli.observe_locality_permits(site, CLOUD) is False
    with pytest.raises(cli.UnratifiedPromptOnACloudTarget, match=site):
        cli.require_observe_locality(site, CLOUD)


def test_the_refusal_says_the_packet_is_unratified_in_the_packets_own_word():
    """Read from the manifest, never remembered here: if the owner ratifies the
    packet the sentence stops claiming otherwise without anyone editing it."""
    with pytest.raises(cli.UnratifiedPromptOnACloudTarget) as caught:
        cli.require_observe_locality(C_PLACEMENT, CLOUD)

    assert drafts_status() in str(caught.value)
    assert cli.LOCAL_MODEL_NAME in str(caught.value)


def test_a_fact_is_untouched_and_may_still_be_asked_over_the_internet():
    """`A_fact`'s text is ratified (`planning/82` §0) and `WIRED_CALL_SITES` is
    what governs it. A guard that caught it too would have turned an observe-mode
    constraint into a cloud outage."""
    assert cli.observe_locality_permits(A_FACT, CLOUD) is True
    cli.require_observe_locality(A_FACT, CLOUD)


def test_the_packet_itself_says_it_is_unratified():
    assert drafts_status() == "unratified"


@pytest.mark.parametrize("site,template_id", sorted(WINNERS.items()))
def test_every_observe_sites_draft_loads_and_says_unratified_in_its_own_id(
        site, template_id):
    """A record written under one of these ids says on its face that the text was
    not ratified. That is what makes an observe run auditable after the fact: the
    id is in `llm_response` and `llm_verdict`, and it carries the word."""
    assert "unratified" in template_id
    assert draft_row(template_id)["site"] == site

    template, schema, policy = draft_bytes(template_id)

    assert template and schema and policy
    assert template.strip().startswith(b"#") or len(template) > 1000


def test_a_template_id_nobody_published_is_refused_and_names_what_there_is():
    """`84` §1: absent means refuse, never guess. A loader that fell back to a
    sibling draft would send text under an id no record could be checked against."""
    with pytest.raises(DraftNotInManifest, match="anchors-first-v3"):
        draft_bytes("b_group.unratified.anchors-first-v3.2026-09-06")
