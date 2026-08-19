"""The P1 hand-over, for tests that stand in for a neighbouring part.

NOT in `conftest.py` on purpose. Under pytest's default prepend import mode every
`conftest.py` is imported as the top-level module `conftest`, so a second one —
`tests/eval/conftest.py` when P2 is built — shadows the first in `sys.modules`,
and `from conftest import ...` silently resolves against the wrong file. A
uniquely named module cannot be shadowed that way.
"""
from pathlib import Path


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
