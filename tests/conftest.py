from pathlib import Path

import pytest

from database_agent.db import open_database

#: The repository root, which is also pytest's working directory.
_ROOT: Path = Path(__file__).resolve().parents[1]


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
