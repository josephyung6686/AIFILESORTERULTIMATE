# Privacy inventory

The local database is a SQLite database. Unless the runtime explicitly reports
SQLCipher (or another configured encrypted SQLite implementation), SQLite is
plain text at rest. The product reports that fact and does not claim that file
permissions are encryption.

Stored local data is limited to filesystem metadata, item labels and paths,
search excerpts/chunks, vector embeddings, relationship and decision records,
and fixture headers. Fixture ingestion stores message and event headers only:
message bodies, calendar descriptions, attachment bytes, OAuth access tokens,
refresh tokens, and authorization headers are discarded.

Held/protected item details require a local-authentication callback. If no
callback is configured, access is refused. Export is sanitized by a denylist of
secret fields and every export and deletion writes an append-only audit event.
Deletion removes the item and its dependent relationship, chunk, vector, and
FTS rows where those tables exist.

Live Gmail and Calendar OAuth are disabled in this build. A fixture is a local
JSON input and makes no network call.
