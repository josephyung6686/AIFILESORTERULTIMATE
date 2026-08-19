from pathlib import Path

import pytest

from database_agent.db import open_database


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


def p3_basic_record(path: Path) -> dict:
    """The R2 fields P3 computes once (O5) and hands to P1.

    A fixture standing in for P3 legitimately derives these from the filesystem —
    that is P3's job. P1 must not, which is why they arrive as arguments.
    """
    import json
    import unicodedata
    from datetime import datetime, timezone

    stat = path.stat()
    return dict(
        filename=path.name,
        normalized_filename=unicodedata.normalize("NFC", path.name),
        extension=path.suffix,
        observed_size=stat.st_size,
        observed_timestamps=json.dumps({
            "mtime": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
            "ctime": datetime.fromtimestamp(stat.st_ctime, timezone.utc).isoformat(),
        }),
    )
