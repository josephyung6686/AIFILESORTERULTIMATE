"""`00` amendment 2 of 13 Sep 2026: the person is asked before the cloud, and a
deployment WITHOUT a local model holds on the rules and asks the person.

The owner, 14 Sep 01:20: "don't use the local model unless absolutely necessary;
use the cloud". Until this arm a file only reached the cloud if the local gate
had cleared it, so a machine with a cloud key and no local model sent nothing
anywhere and asked nobody. Now a file the rules did not hold is cleared on the
rules' word -- counted on its own line, apart from `cleared`, which is a model's
word -- and the files the rules DO hold are the person's question at the end of
the run. A run with neither key nor local model has no routing at all and no
gate pass; that is `main`'s own refusal and not this arm's.
"""
from __future__ import annotations

import io
import sqlite3
import sys
from pathlib import Path

import pytest

import cli

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent / "p7"))
from test_p7_file_released import HELD_NAME, LABEL, SITUATION, _corpus  # noqa: E402
from test_a_fact_call_cache import (  # noqa: E402
    BASE_URL_NAME, CREDENTIAL_NAME, ENV, LOCAL_BASE_URL_NAME, LOCAL_MODEL_NAME,
    MODEL_NAME_OF_TIER, socket,  # noqa: F401  (the fixture, re-exported)
)


@pytest.fixture(autouse=True)
def _cloud_key_and_no_local_model(monkeypatch, tmp_path):
    for name in (CREDENTIAL_NAME, BASE_URL_NAME, *MODEL_NAME_OF_TIER.values(),
                 LOCAL_MODEL_NAME, LOCAL_BASE_URL_NAME):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(cli, "ENV_FILE", tmp_path / "absent.env")
    for name, value in ENV.items():
        monkeypatch.setenv(name, value)


def test_without_a_local_model_the_rules_clear_the_un_held_and_the_person_is_asked(
        tmp_path, socket):
    corpus = _corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", SITUATION, "--label", LABEL,
                     "--user", "t", "--database", str(database),
                     "--enable-cloud"], out=out)
    said = out.getvalue()
    assert code == 0, said
    # The un-held file is cleared on the rules' word and the screen says so.
    assert "1 cleared on the rules' word alone" in said, said
    # The held file is named as the person's question, with both gestures.
    assert HELD_NAME in said and "--release" in said and "--file-held" in said
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    # No gate question was put to any model: no gate dossier exists.
    assert conn.execute("SELECT count(*) FROM llm_dossier WHERE call_site = ?",
                        (cli.H_RESTRICTED_KIND,)).fetchone()[0] == 0
    # The held file is still held; the rules' word never reaches it.
    (held,) = [row["file_id"] for row in conn.execute(
        "SELECT file_id FROM files WHERE filename = ?", (HELD_NAME,))]
    assert held in cli._protected_file_ids(conn)
    # And the cloud was offered only the cleared file's questions, never the held one.
    assert held not in socket.subjects_at(cli.G_SITUATION_SENSITIVITY)
