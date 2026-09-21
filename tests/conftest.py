import os
from pathlib import Path

import pytest

from database_agent.db import open_database

#: NO TEST MAY SPEND THE OWNER'S MONEY, and until this line existed every one of
#: them could. `cli.py` read the repository's own `.env` unconditionally, so any
#: test passing `--enable-cloud` found a real credential, built a real client and
#: called a paid API. Measured the day the A_fact site was wired:
#: `test_a_second_source_does_not_send_under_the_first_ones_consent` stopped the
#: whole suite dead for ten minutes with no output, twice, and the suite could not
#: be run at all until this was set.
#:
#: Set at IMPORT, before any test or fixture runs, because `cli.py` reads the file
#: inside the run rather than at import and a fixture would be too late for a test
#: that builds its client first. A test that genuinely wants a live model must
#: unset it deliberately and say why -- which is the point: sending is now a thing
#: a test opts INTO, not something it inherits from the developer's own machine.
os.environ.setdefault("GRAPH_AGENT_NO_DOTENV", "1")

#: AND NO TEST MAY CALL THE DEVELOPER'S OWN LOCAL MODEL EITHER. The line above
#: stops `.env` reaching a run; it does not stop an EXPORTED name, and
#: `GRAPH_AGENT_LOCAL_MODEL` is the one that would be exported -- a local model
#: costs nothing, so a person who set it for a real run has no reason to unset it
#: before running the suite.
#:
#: What that would do is worse than the key, not better. Every integration test
#: that drives `cli.main` would silently acquire a model, the fact pass would fire
#: on synthetic corpora, and a suite that takes five minutes would take hours while
#: appearing merely slow. The failures would be timeouts and non-determinism, read
#: as flakiness rather than as the ambient configuration they are.
#:
#: POPPED, not `setdefault`-ed to empty: `model_route` treats an empty value as
#: absent, but a test that wants a local model sets one with `monkeypatch.setenv`
#: and must start from a name that is genuinely not there. A test that wants the
#: developer's real model must set it deliberately and say why -- which is the
#: same opt-in the note above describes.
os.environ.pop("GRAPH_AGENT_LOCAL_MODEL", None)
os.environ.pop("OLLAMA_BASE_URL", None)

#: The repository root, which is also pytest's working directory.
_ROOT: Path = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _no_ambient_model_server(monkeypatch):
    """AND NO TEST MAY DISCOVER THE DEVELOPER'S OWN OLLAMA, added 20 Sep 2026.

    The two lines above stop an exported name and a `.env` reaching a run. Since
    `model_route` also ASKS the loopback endpoint what is installed when no name
    is set, there is a third way the developer's machine can reach a test, and it
    is one no environment variable can close: the fact that ollama is running.

    What it would do is make the SCREEN machine-dependent. `model_route` prints a
    different sentence when it finds models, so
    `tests/integration/test_r37_single_branch_is_byte_identical.py` -- a fixture
    of the exact bytes a run prints -- would pass on a laptop with no model
    server and fail on the same laptop an hour later with one running. That is
    the failure mode `84` §4 records for corpora and `_no_ambient_key` records
    for credentials, arriving by a third door.

    **A test that wants the real function calls it directly**, holding the
    reference rather than reaching through `cli`: this replaces the module's
    attribute and not the function, so `tests/test_cli_model_route.py`'s
    `_for_real` tests still talk to a real endpoint. A test about the SCREEN
    injects an answer through `model_route(discover=...)`, which is the seam that
    exists for it and which this fixture does not touch.
    """
    import cli

    monkeypatch.setattr(cli, "_discover_local_models", lambda _endpoint: ())


def _databases_in_the_working_directory() -> frozenset[str]:
    return frozenset(path.name for path in _ROOT.glob("*.sqlite*"))


@pytest.fixture(autouse=True)
def _no_database_in_the_working_directory():
    """No test may leave a database in the directory the suite is run from.

    `cli.py` defaults `--database` to `Path.cwd() / "database-agent-plan.sqlite"`,
    and pytest's cwd is this repository -- so a test that calls `cli.main` without
    the flag writes a real 2.4 MB plan database into the working tree. One did.

    Two harms, and the second is the one that cost a day. It is an untracked file
    in a directory several sessions commit into. And it is not cleaned up, so the
    NEXT run reads it: two tests sharing one database with each other and with any
    future test that omits the flag, carrying facts, groups and plan versions
    across pytest invocations while their corpora are rebuilt fresh in `tmp_path`
    each time. State that outlives the run that made it is how a suite acquires an
    order it depends on, and the symptom -- passes alone, fails in company -- is
    read as flakiness rather than as the shared state it is.

    Per test rather than per session, deliberately: a session-scoped check reports
    that SOMETHING wrote one, and the whole difficulty is finding out what. This
    names the test in its own failure.
    """
    before = _databases_in_the_working_directory()
    yield
    new = _databases_in_the_working_directory() - before
    if new:
        for name in new:
            (_ROOT / name).unlink()
        raise AssertionError(
            f"this test left {sorted(new)} in {_ROOT}, the directory the suite "
            "runs from. Pass `--database` (under `tmp_path`) to every `cli.main` "
            "call: the default is `Path.cwd()`, the file is not cleaned up, and "
            "the next run reads it. Deleted, so the rest of this run is clean."
        )


@pytest.fixture()
def conn(tmp_path: Path):
    c = open_database(tmp_path / "agent.sqlite")
    yield c
    c.close()


@pytest.fixture()
def sample_file(tmp_path: Path) -> Path:
    p = tmp_path / "corpus" / "Syllabus.pdf"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"the quick brown fox")
    return p
