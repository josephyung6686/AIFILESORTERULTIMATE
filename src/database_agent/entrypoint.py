"""Small installed command boundary.

The package contains optional reader and model deployments. Keeping the command
loader small means offline database/search installs can show help and run local
operations without importing optional document readers at process start.
"""
from __future__ import annotations

import sys


HELP = """usage: database-agent                  talk to it: find, ask, sort, undo
       database-agent "where is my CV"  one answer, then exit
       database-agent <FOLDER> [OPTIONS]
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


def _stdin_is_a_terminal() -> bool:
    return sys.stdin.isatty()


def _conversation(args: list[str], out=None) -> int | None:
    """The chat: no arguments, a folder alone in a terminal, a sentence, or
    `--events` for the desktop app. None when the sorter should run."""
    from pathlib import Path
    if args and args != ["--events"]:
        if len(args) != 1 or args[0].startswith("-"):
            return None
        if Path(args[0]).expanduser().is_dir() and not _stdin_is_a_terminal():
            return None
    import os
    import sqlite3
    from assistant import terminal
    from database_agent.db import open_database, shared_database_path
    # `open_database` reads DATABASE_AGENT_KEY_FILE itself, as the
    # subcommands' `--key-file` does. Without it an encrypted file is not
    # a database to plain SQLite, and the person gets one line.
    from database_agent.encryption import EncryptedDatabaseError, EncryptionUnavailable
    shown = out if out is not None else sys.stdout
    key_file = os.environ.get("DATABASE_AGENT_KEY_FILE")
    try:
        conn = open_database(shared_database_path(), scan_roots=[])
    except (FileNotFoundError, PermissionError, ValueError) as problem:
        if not key_file:
            raise
        print(f"I can't use the key file {key_file} ({problem}). Nothing "
              "was opened.", file=shown)
        return 2
    except EncryptionUnavailable:
        print("This database is encrypted, but the encryption package isn't "
              "installed here. Nothing was opened.", file=shown)
        return 2
    except (sqlite3.DatabaseError, EncryptedDatabaseError):
        if key_file:
            print(f"The key in {key_file} doesn't open this database. Nothing "
                  "was opened.", file=shown)
            return 2
        print("This database is encrypted. Set DATABASE_AGENT_KEY_FILE to "
              "your key file, then run database-agent again.", file=shown)
        return 2
    try:
        if not args:
            return terminal.run_terminal(conn, folder=None, stdout=out)
        if args == ["--events"]:
            return terminal.run_events(conn, stdout=out)
        folder = Path(args[0]).expanduser()
        if folder.is_dir():
            return terminal.run_terminal(conn, folder=folder, stdout=out)
        return terminal.run_once(conn, args[0], stdout=out)
    finally:
        conn.close()


def main(argv: list[str] | None = None, *, out=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args == ["--help"] or args == ["-h"]:
        print(HELP, file=out if out is not None else sys.stdout)
        return 0
    local_result = _local_command(args, out=out)
    if local_result is not None:
        return local_result
    chat_result = _conversation(args, out=out)
    if chat_result is not None:
        return chat_result
    from cli import main as legacy_main
    result = legacy_main(args)
    return int(result or 0)


if __name__ == "__main__":
    raise SystemExit(main())
