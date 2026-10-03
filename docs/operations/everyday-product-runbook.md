# Everyday product runbook (non-UI)

**Supported surface:** installed CLI + local SQLite + assistant runtime. No GUI.

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

## Connectors

Live Gmail/Calendar are **scratched**. Fixture import only:

```bash
python3 -m cli sync gmail --fixture FILE --database "$DB"
```

## Release gates

```bash
bash tools/run_release_gates.sh
cat docs/operations/release-gate-report.json
```

The release script is strict: it builds and installs a wheel in a temporary
offline virtual environment, loads all shipped profiles, checks the installed
entry point, and runs the required policy, recovery, relationship, database,
privacy, and provider suites. It fails when a required safety suite is absent.
The Mac UI is excluded from this non-UI release contract, and live Gmail and
Calendar are scratched; fixture connectors remain disabled.

For a supervised daily-use check, always pass a corpus directory. The tool
copies it into a disposable temporary workspace before reading it:

```bash
python3 tools/run_daily_use_pilot.py --database "$DB" --corpus "$CORPUS" \
  --cloud off --memory-steering off --apply off
```
