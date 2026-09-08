# tests/test_cli_a_fact_row.py
"""`104` R-144: site A's text resolves through a manifest row, as the observe sites'.

Before this, `cli.a_fact_prompt` read `a_fact_template_folder_levels.txt` and its
two companions straight off the library by their pinned digests, so a second
version of A's text could not be run locally without editing the ratified file.
Now `cli.A_FACT_ROW` names a row of `drafts_2026-09-06.json` by `(template_id,
candidate)`, and the row's own `status` is what says the text may be applied and
whether it may cross the internet -- `ratified_local` runs here and is refused a
cloud target, exactly as site C's `eliminate-v2` is.

THE FINGERPRINT MUST NOT MOVE. `prompt_fingerprint` hashes the template id with
the bytes, so the row keeps the id every A_fact record since 2026-09-04 carries;
the first test builds the definition the old way, from the library files by
digest, and asserts the row-built one is the same bytes and the same fingerprint.
"""
from __future__ import annotations

import pytest

import cli
from llm_harness import prompt_library
from llm_harness.fingerprint import prompt_fingerprint
from llm_harness.prompt_library import (
    RATIFIED, RATIFIED_LOCAL, UNRATIFIED, a_fact_response_schema_bytes,
    a_fact_shaping_policy_bytes, a_fact_template_folder_levels_bytes,
)
from llm_harness.records import PromptDefinition
from llm_harness.vocabulary import A_FACT
from readers.model_routing import CLOUD, LOCAL


def _as_composed_before_r144() -> PromptDefinition:
    """`a_fact_prompt` as it read before the row: the library files by digest."""
    return PromptDefinition(
        template_id="a_fact.unratified.folder-levels.2026-09-04",
        template_bytes=a_fact_template_folder_levels_bytes(),
        response_schema_bytes=a_fact_response_schema_bytes(),
        call_site=A_FACT, call_site_version="1", ratified=True,
        shaping_policy_bytes=a_fact_shaping_policy_bytes())


def test_the_real_manifest_resolves_a_to_the_same_bytes_and_fingerprint():
    before = _as_composed_before_r144()
    now = cli.a_fact_prompt()

    assert now.template_id == before.template_id
    assert now.template_bytes == before.template_bytes
    assert now.response_schema_bytes == before.response_schema_bytes
    assert now.shaping_policy_bytes == before.shaping_policy_bytes
    assert prompt_fingerprint(now) == prompt_fingerprint(before)
    assert now.ratified is True


def test_the_row_a_runs_under_is_ratified_and_names_the_shipped_glossary():
    row = cli.a_fact_row()
    assert row["status"] == RATIFIED
    assert row["glossary_file"] == "field_glossary.json"
    assert (row["template_id"], row["candidate"]) == cli.A_FACT_ROW


def _pointed_at(monkeypatch, *, status: str | None, candidate: str = "r144-test",
                template_id: str = "a_fact.unratified.folder-levels.2026-09-04",
                glossary: str = "field_glossary.json"):
    """Select a row that exists only in this test's copy of the manifest."""
    manifest = {key: (list(value) if isinstance(value, list) else value)
                for key, value in prompt_library._manifest().items()}
    row = {"site": "A_fact", "candidate": candidate, "template_id": template_id,
           "template_file": "a_fact_template_folder_levels.txt",
           "response_schema_file": "a_fact_response_schema.json",
           "shaping_policy_file": "a_fact_shaping_policy.json",
           "glossary_file": glossary}
    if status is not None:
        row["status"] = status
    # Under a NEW id, so the real rows' words do not speak for this one.
    manifest["drafts"] = [other for other in manifest["drafts"]
                          if other.get("template_id") != template_id] + [row]
    monkeypatch.setattr(prompt_library, "_manifest", lambda: manifest)
    monkeypatch.setattr(cli, "A_FACT_ROW", (template_id, candidate))


def test_a_row_whose_word_is_unratified_is_refused_at_composition(monkeypatch):
    _pointed_at(monkeypatch, status=UNRATIFIED)
    with pytest.raises(cli.AFactRowNotRatified):
        cli.a_fact_prompt()


def test_a_row_with_no_word_inherits_the_packets_and_the_packet_says_unratified(
        monkeypatch):
    _pointed_at(monkeypatch, status=None)
    assert prompt_library.drafts_status() == UNRATIFIED
    with pytest.raises(cli.AFactRowNotRatified):
        cli.a_fact_prompt()


def test_ratified_local_runs_here_and_is_refused_a_cloud_target(monkeypatch):
    """As for C: `ratified_local` APPLIES and does not CROSS."""
    _pointed_at(monkeypatch, status=RATIFIED_LOCAL)
    prompt = cli.a_fact_prompt()
    assert prompt.ratified is True
    assert cli.observe_locality_permits(A_FACT, LOCAL) is True
    assert cli.observe_locality_permits(A_FACT, CLOUD) is False
    with pytest.raises(cli.UnratifiedPromptOnACloudTarget) as refused:
        cli.require_observe_locality(A_FACT, CLOUD)
    assert RATIFIED_LOCAL in str(refused.value)


def test_ratified_may_cross_the_internet(monkeypatch):
    _pointed_at(monkeypatch, status=RATIFIED)
    assert cli.observe_locality_permits(A_FACT, CLOUD) is True
    cli.require_observe_locality(A_FACT, CLOUD)


def test_the_rows_glossary_is_not_checked_against_the_dossiers(monkeypatch):
    """The promptbench swaps `dossier.GLOSSARY_FILE` to run another glossary arm
    under this text, and a check here against that global refused
    `a_fact_prompt` in whichever test followed the swap (the R-144 merge, about
    thirty tests red under `pytest-randomly`). The row's word is data; which
    glossary is in the bytes is the dossier's own fact."""
    from llm_harness import dossier
    monkeypatch.setattr(dossier, "GLOSSARY_FILE",
                        dossier.GLOSSARY_FILE.with_name(
                            "field_glossary_proposal_2026-09-06.json"))
    assert cli.a_fact_prompt().ratified is True
    _pointed_at(monkeypatch, status=RATIFIED,
                glossary="field_glossary_proposal_2026-09-06.json")
    assert cli.a_fact_prompt().ratified is True


def test_a_row_nobody_published_is_refused_and_names_the_candidates(monkeypatch):
    monkeypatch.setattr(cli, "A_FACT_ROW", (cli.A_FACT_ROW[0], "no-such-arm"))
    with pytest.raises(prompt_library.DraftNotInManifest) as refused:
        cli.a_fact_prompt()
    assert "ratified-folder-levels" in str(refused.value)
