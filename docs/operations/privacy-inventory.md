# Privacy inventory

The local database is a SQLite database. Unless the runtime explicitly reports
SQLCipher (or another configured encrypted SQLite implementation), SQLite is
plain text at rest. The product reports that fact and does not claim that file
permissions are encryption.

Stored local data is limited to filesystem metadata, item labels and paths,
search excerpts/chunks, vector embeddings, and relationship and decision records.

Held/protected item details and deletion require a local-authentication callback.
If no callback is configured, access is refused. Export uses an explicit metadata
allowlist for non-held items, headers, versions, linked files, and relationships.
It omits held items and their linked file records, bodies/chunks, vectors, FTS
shadow tables, evidence, audit history, and unknown tables or JSON payloads.
Exports are owner-readable/writable files (0600), not backups of the database.

Deletion atomically removes an active item, its relationships, headers, versions,
chunks, and FTS entries, plus file embeddings for versions not shared by another
item. It preserves immutable identity events, relationship decisions, evidence,
file inventory, and other historical records. The result explicitly reports
`retained_history: true` and `source_files_retained: true`. Original source files
remain on disk and can be rediscovered by a later scan. **This is removal from
active item views and search, not physical erasure or a complete privacy purge.**
Full erasure remains unimplemented under the existing immutable-history contract.

Export and deletion write minimal audit records. Nested database callers retain
ownership of their transaction; neither operation commits unrelated pending
writes. An export file is an external artifact and cannot be rolled back by a
caller's later database rollback.

