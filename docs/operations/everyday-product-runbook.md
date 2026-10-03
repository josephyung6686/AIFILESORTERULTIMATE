# Everyday product runbook (non-UI)

**Supported surface:** installed CLI + local SQLite + assistant runtime. No GUI.

## Installation and encrypted storage

Use Python 3.12 and a fresh virtual environment. Install the `encryption` extra
to use encrypted databases; the base package supports plaintext local storage.
Document readers and cloud model SDKs are separate `readers` and `models` extras.

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install '.[encryption]'
.venv/bin/database-agent --help
```

SQLCipher is required for encryption. A missing driver or incorrect key refuses
access; it never falls back to plaintext. To migrate an existing database, close
its writers and create a new encrypted destination:

```bash
.venv/bin/database-agent db encrypt /path/to/plain.sqlite \
  --database /path/to/encrypted.sqlite --key-file /path/to/private/database.key
export DATABASE_AGENT_KEY_FILE=/path/to/private/database.key
.venv/bin/database-agent search 'query' --database /path/to/encrypted.sqlite
```

The key file contains 32 random bytes and must be owned by the current user with
owner-only permissions. Keep a recoverable copy of the key separately from the
database. Migration preserves the original plaintext database; it does not erase
that source, earlier backups, exported metadata, or the original corpus files.
Encryption protects database storage, including its search index, rather than
encrypting the source files themselves.

## Safe defaults

```bash
# Cloud off / local find
PYTHONPATH=src python3 -m cli ask --database "$DB" --local-only "Where is X?"

# Memory steering stays dark unless deliberately released
unset ASSISTANT_ATOMS_STEER   # or ASSISTANT_ATOMS_STEER=0

# Apply stays locked
unset ASSISTANT_ENABLE_APPLY
```

## Index freshness

```bash
# One-shot refresh happens at start of ask/search
python3 -m cli search "query" --database "$DB"

# Background watcher
python3 -m cli watch --database "$DB" --root "$COPY" --seconds 60
```

## Backup / restore / check

```bash
python3 -m cli db check --database "$DB"
python3 -m cli db backup --database "$DB" /path/to/backup.sqlite
python3 -m cli db restore /path/to/backup.sqlite --database "$DB.new"
python3 -m cli db rebuild-index --database "$DB"
```

## Disable risky features after an incident

1. Unset `ASSISTANT_ENABLE_APPLY`  
2. Set `ASSISTANT_ATOMS_STEER=0`  
3. Prefer `--local-only` or unset API keys  
4. `db check` then `db restore` from last good backup  
5. `db rebuild-index`

## Release gates

```bash
bash tools/run_release_gates.sh
cat docs/operations/release-gate-report.json
```

The release script builds and installs a wheel in a temporary virtual
environment, loads all shipped profiles, checks the installed entry point,
and records each required check in its JSON report. Review the report's scope
and failures before treating a build as ready for a supervised pilot.
The Mac UI is excluded from this non-UI release contract.

For a supervised daily-use check, always pass a corpus directory. The tool
copies it into a disposable temporary workspace before reading it:

```bash
python3 tools/run_daily_use_pilot.py --database "$DB" --corpus "$CORPUS" \
  --cloud off --memory-steering off --apply off
```

This script is a short copied-corpus smoke check. It does not establish the
multi-day zero-incident record required for unsupervised everyday use, and it
does not exercise every approval, recovery, or privacy scenario in the plan.
