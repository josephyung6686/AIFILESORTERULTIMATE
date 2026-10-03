# Database recovery runbook

The SQLite database is the local source for indexed metadata, assistant state,
and audit records. The selected files remain the source of truth for file
contents. Maintenance commands must be run against a quiescent database when
possible; a backup uses SQLite's online backup API and is safe while readers
are open.

## Check before recovery

Run:

```bash
database-agent db check --database /path/to/agent.sqlite
```

The report includes SQLite integrity, schema version, dirty/indexing/missing
items, and nonterminal assistant journal entries. A `planned`, `moving`, or
`conflicted` journal row is unfinished work and keeps `ok` false. Do not delete
those rows by hand. Reconcile them through assistant recovery, then check
again.

## Backup

```bash
database-agent db backup --database /path/to/agent.sqlite \
  /path/to/backups/agent.sqlite
```

For an encrypted SQLCipher database, pass an owner-only key file. The command
reads the key without putting secret bytes in shell history or the process
listing:

```bash
database-agent db backup --database /path/to/agent.sqlite \
  --key-file ~/Library/Application\ Support/GraphAgent/db.key \
  /path/to/backups/agent.sqlite
```

The destination must not already exist. A JSON sidecar records creation time,
source, schema constant, and a post-backup integrity report. Treat a missing
sidecar or a report whose `integrity` is not `ok` as a failed backup.

## Restore

Restore to a new path first:

```bash
database-agent db restore --database /path/to/new.sqlite \
  /path/to/backups/agent.sqlite
```

Use the same `--key-file` for an encrypted backup. A wrong key fails before a
target is created.

Restoration refuses a corrupt backup and refuses to overwrite an existing target
unless `--replace` is supplied. Replacement is an atomic operation: a failed
copy or rename leaves the previous target in place and removes the temporary
restore file. After restoration, run `db check` before using the database.

## Interrupted maintenance

If a process stops during restore, look for `*.restore-tmp`. It is an incomplete
staging copy and is safe to remove after confirming that no restore process is
running; the target is only replaced after the staged file has been copied and
validated.

If a process stops during assistant work, restart the normal application and
inspect `db check`. Nonterminal journal entries require reconciliation before
new destructive work is approved. A database check that reports failed
integrity must be treated as a failed database: preserve the original file,
copy it for diagnosis, and restore the latest known-good backup to a new path.

## Migration

Opening an older database performs additive schema migration and is
idempotent. Keep a backup before upgrading. The migration must complete before
the database is used; if it fails, retain the original file and retry from a
copy after fixing the reported error. Verify the resulting schema and run the
full release gate before shipping the migrated database.
