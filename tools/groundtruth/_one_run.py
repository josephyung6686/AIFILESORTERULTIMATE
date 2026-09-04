"""One `--situation` run of the product, in its own process.

Its own process for two reasons. `cli.main` is the composition root and building
it twice in one interpreter would let one run's imports and caches reach the
next; and a run that dies takes only itself down, which matters when several are
in flight at once.

Usage: python3 -m tools.groundtruth._one_run CORPUS SITUATION LABEL DATABASE REPORT [cloud]

The last argument is the word `cloud` or nothing. Sending is OFF unless it is
there, and the credential is unreadable unless it is there: turning the model on
is one explicit word in one place, never a default and never inherited.
"""
from __future__ import annotations

import io
import os
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    corpus, situation, label, database, report = argv[:5]
    cloud = len(argv) > 5 and argv[5] == "cloud"
    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root / "src"))

    # No run of this harness spends the owner's money by accident. Without the
    # word, the credential is not even readable; with it, this is the ONE place
    # that decides, and the run says so on screen before it sends.
    if not cloud:
        os.environ["GRAPH_AGENT_NO_DOTENV"] = "1"

    import cli

    argv_for_cli = [corpus, "--situation", situation, "--label", label,
                    "--user", "groundtruth", "--database", database]
    if cloud:
        argv_for_cli.append("--enable-cloud")

    out = io.StringIO()
    try:
        code = cli.main(argv_for_cli, out=out)
    finally:
        Path(report).write_text(out.getvalue(), encoding="utf-8")
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
