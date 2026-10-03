"""Small installed command boundary.

The package contains optional reader and model deployments. Keeping the command
loader small means offline database/search installs can show help and run local
operations without importing optional document readers at process start.
"""
from __future__ import annotations

import sys


def _local_command(args: list[str]) -> int | None:
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
    return handlers[args[0]](args[1:])


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args == ["--help"] or args == ["-h"]:
        print("usage: database-agent [OPTIONS] [DIRECTORY]")
        print("Run local file discovery and assistant operations. Use --help for options.")
        return 0
    local_result = _local_command(args)
    if local_result is not None:
        return local_result
    from cli import main as legacy_main
    result = legacy_main(args)
    return int(result or 0)


if __name__ == "__main__":
    raise SystemExit(main())
