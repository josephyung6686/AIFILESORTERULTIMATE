"""Small installed command boundary.

The package contains optional reader and model deployments. Keeping the command
loader small means offline database/search installs can show help and run local
operations without importing optional document readers at process start.
"""
from __future__ import annotations

import sys


HELP = """usage: database-agent <FOLDER> [OPTIONS]
       database-agent <command> [OPTIONS]

database-agent <FOLDER>   read a folder and propose how to file it
                          (database-agent <FOLDER> --help for its options)

commands (all use ~/.graph-agent/database-agent.sqlite unless --database is given):
  search QUERY      find files by name or meaning
  ask QUESTION      ask a question about what is indexed
  view [NAME]       folder, table, board, timeline or graph
  suggest           print proposed filings; nothing is moved
  plan ACTION       create, show, approve, apply or undo a filing plan
  preview-plan ID   dry-run a plan; nothing is moved
  watch             keep the index current as files change
  db ACTION         check, backup, restore, rebuild-index or encrypt the database
  memory ACTION     status or release of the assistant memory"""


def _local_command(args: list[str], out=None) -> int | None:
    """Dispatch the real dependency-free product commands lazily."""
    if not args or args[0] not in {"search", "ask", "db", "memory", "view", "suggest", "watch", "plan", "preview-plan"}:
        return None
    from items.commands import ask_main, plan_main, preview_main, search_main, suggest_main, view_main, watch_main
    from items.commands_db import db_main
    from items.commands_memory import memory_main
    handlers = {"search": search_main, "ask": ask_main, "db": db_main,
                "memory": memory_main, "view": view_main,
                "suggest": suggest_main, "watch": watch_main,
                "plan": plan_main, "preview-plan": preview_main}
    return handlers[args[0]](args[1:], out=out)


def main(argv: list[str] | None = None, *, out=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args == ["--help"] or args == ["-h"]:
        print(HELP, file=out if out is not None else sys.stdout)
        return 0
    local_result = _local_command(args, out=out)
    if local_result is not None:
        return local_result
    from cli import main as legacy_main
    result = legacy_main(args)
    return int(result or 0)


if __name__ == "__main__":
    raise SystemExit(main())
