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
bash tools/run_assistant_gates.sh
bash tools/run_release_gates.sh   # grows as T1–T12 land
```
