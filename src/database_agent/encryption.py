"""SQLCipher-backed encrypted SQLite connections.

Encryption is opt-in at the connection boundary.  If requested, a real
SQLCipher DB-API driver is mandatory; silently opening plain SQLite would make
the product claim protection it did not provide.
"""
from __future__ import annotations

import os
import secrets
import sqlite3
import stat
import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

try:
    import sqlcipher3.dbapi2 as _DRIVER
    _DRIVER_ERROR: Exception | None = None
except ImportError as first_error:  # pragma: no cover - environment dependent
    try:
        import pysqlcipher3.dbapi2 as _DRIVER
        _DRIVER_ERROR = None
    except ImportError as second_error:  # pragma: no cover
        _DRIVER = None
        _DRIVER_ERROR = second_error


class EncryptionUnavailable(RuntimeError):
    """Encryption was requested but no SQLCipher driver is installed."""


class EncryptedDatabaseError(RuntimeError):
    """A SQLCipher database could not be opened with the supplied key."""


class CipherRow:
    """sqlite3.Row-compatible mapping for SQLCipher's distinct cursor type."""

    def __init__(self, columns: tuple[str, ...], values: tuple[Any, ...]):
        self._columns, self._values = columns, values
        self._index = {name: i for i, name in enumerate(columns)}

    def __getitem__(self, key: str | int) -> Any:
        if isinstance(key, int):
            return self._values[key]
        return self._values[self._index[key]]

    def __iter__(self) -> Iterator[Any]:
        return iter(self._values)

    def keys(self) -> list[str]:
        return list(self._columns)

    def __len__(self) -> int:
        return len(self._values)


def _row_factory(cursor: Any, values: tuple[Any, ...]) -> CipherRow:
    return CipherRow(tuple(column[0] for column in cursor.description), values)


class _EncryptedConnection(_DRIVER.Connection if _DRIVER else object):
    _graph_agent_encrypted = False


def key_from_file(path: Path) -> bytes:
    """Read or generate an owner-only exactly-256-bit key file.

    Existing files are never chmodded or followed through symlinks. This keeps a
    deployment mistake visible instead of silently broadening access.
    """
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        info = os.lstat(path)
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
            raise PermissionError("database key file must be a regular file")
        if info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise PermissionError("database key file must be owned by the user with mode 0600")
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        try:
            opened = os.fstat(fd)
            if opened.st_uid != os.getuid() or not stat.S_ISREG(opened.st_mode) or opened.st_mode & 0o077:
                raise PermissionError("database key file changed during open")
            key = os.read(fd, 64)
            if len(key) != 32 or os.read(fd, 1):
                raise ValueError("database key file must contain exactly 256 bits")
        finally:
            os.close(fd)
    else:
        key = secrets.token_bytes(32)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        fd = os.open(path, flags, 0o600)
        try:
            os.write(fd, key)
            os.fsync(fd)
        finally:
            os.close(fd)
        try:
            dir_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        except OSError:
            pass
    return key


def read_key_file(path: Path) -> bytes:
    """Read an existing owner-only key; never create or replace it."""
    path = Path(path).expanduser()
    info = os.lstat(path)
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise FileNotFoundError(path)
    if info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise PermissionError(f"database key file must be owner-only: {path}")
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        opened = os.fstat(fd)
        if opened.st_uid != os.getuid() or not stat.S_ISREG(opened.st_mode) or opened.st_mode & 0o077:
            raise PermissionError("database key file changed during open")
        key = os.read(fd, 64)
        if len(key) != 32 or os.read(fd, 1):
            raise ValueError("database key file must contain exactly 256 bits")
    finally:
        os.close(fd)
    return key


def _key_pragma(key: bytes) -> str:
    if not isinstance(key, (bytes, bytearray)) or len(key) != 32:
        raise ValueError("database encryption key must contain exactly 256 bits")
    return "PRAGMA key = \"x'%s'\"" % bytes(key).hex()


def open_encrypted(path: Path, key: bytes, **kwargs: Any):
    """Open and validate a SQLCipher database before any schema operation."""
    if _DRIVER is None:
        raise EncryptionUnavailable(
            "encrypted storage requires the sqlcipher3 or pysqlcipher3 package"
        ) from _DRIVER_ERROR
    key_statement = _key_pragma(key)
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = None
    try:
        conn = _DRIVER.connect(str(path), factory=_EncryptedConnection, **kwargs)
        conn.row_factory = _row_factory
        conn.execute(key_statement)
        conn.execute("PRAGMA temp_store = MEMORY")
        version = conn.execute("PRAGMA cipher_version").fetchone()[0]
        if not version:
            raise EncryptedDatabaseError("SQLCipher driver did not report cipher_version")
        conn.execute("SELECT count(*) FROM sqlite_master").fetchone()
        conn._graph_agent_encrypted = True
        return conn
    except EncryptedDatabaseError:
        try:
            conn.close()
        except Exception:
            pass
        raise
    except Exception as error:
        try:
            conn.close()
        except Exception:
            pass
        raise EncryptedDatabaseError(
            "unable to open encrypted database; key may be wrong or database corrupt"
        ) from error


def open_encrypted_existing(path: Path, key: bytes):
    """Open an existing encrypted database read-only, without creating it."""
    path = Path(path).expanduser()
    if not path.is_file():
        raise FileNotFoundError(path)
    if _DRIVER is None:
        raise EncryptionUnavailable(
            "encrypted storage requires the sqlcipher3 or pysqlcipher3 package"
        ) from _DRIVER_ERROR
    conn = None
    try:
        conn = _DRIVER.connect(path.resolve().as_uri() + "?mode=ro", uri=True,
                               factory=_EncryptedConnection)
        conn.row_factory = _row_factory
        conn.execute(_key_pragma(key))
        conn.execute("PRAGMA temp_store = MEMORY")
        if not conn.execute("PRAGMA cipher_version").fetchone()[0]:
            raise EncryptedDatabaseError("SQLCipher driver did not report cipher_version")
        conn.execute("SELECT count(*) FROM sqlite_master").fetchone()
        conn._graph_agent_encrypted = True
        return conn
    except EncryptedDatabaseError:
        if conn is not None:
            conn.close()
        raise
    except Exception as error:
        if conn is not None:
            conn.close()
        raise EncryptedDatabaseError(
            "unable to open encrypted database; key may be wrong or database corrupt"
        ) from error


def is_encrypted_runtime() -> bool:
    return _DRIVER is not None


def migrate_plaintext(source: Path, destination: Path, key: bytes) -> None:
    """Copy one read-only snapshot, including stored FTS content, into SQLCipher.

    No source files are read to regenerate data during migration. Virtual-table
    rows are copied through their public table interfaces, never their internal
    shadow-page formats, which may differ between SQLite builds.
    """
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if source == destination or destination.exists():
        raise FileExistsError("migration requires an existing source and new destination")
    _key_pragma(key)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{destination.name}.encrypting-",
                                dir=destination.parent)
    os.close(fd)
    staging = Path(name)
    plain = sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)
    encrypted = None
    quote = lambda identifier: '"' + identifier.replace('"', '""') + '"'
    try:
        plain.execute("BEGIN")
        user_version = plain.execute("PRAGMA user_version").fetchone()[0]
        app_id = plain.execute("PRAGMA application_id").fetchone()[0]
        table_info = {row[1]: row for row in plain.execute("PRAGMA main.table_list")}
        objects = plain.execute(
            "SELECT type, name, sql FROM sqlite_master WHERE sql IS NOT NULL"
        ).fetchall()
        encrypted = open_encrypted(staging, key)
        encrypted.execute("BEGIN")
        copied = []
        for kind, table, sql in objects:
            if kind != "table" or table.startswith("sqlite_"):
                continue
            info = table_info[table]
            if info[2] == "shadow":
                continue
            copied.append(table)
            encrypted.execute(sql)
            columns = [r[1] for r in plain.execute(f"PRAGMA table_xinfo({quote(table)})")
                       if r[6] == 0]
            # Preserve virtual-table rowids used by MATCH/ranking and ordinary
            # rowids when the schema has not shadowed their public aliases.
            if not info[4]:
                aliases = {column.casefold() for column in columns}
                alias = next((a for a in ("rowid", "_rowid_", "oid")
                              if a not in aliases), None)
                if alias:
                    columns.insert(0, alias)
            names = ", ".join(map(quote, columns))
            placeholders = ", ".join("?" for _ in columns)
            encrypted.executemany(
                f"INSERT INTO {quote(table)} ({names}) VALUES ({placeholders})",
                plain.execute(f"SELECT {names} FROM {quote(table)}"))
        # AUTOINCREMENT's high-water mark can exceed MAX(id) after deletion.
        if "sqlite_sequence" in table_info:
            encrypted.execute("DELETE FROM sqlite_sequence")
            encrypted.executemany("INSERT INTO sqlite_sequence VALUES (?, ?)",
                                  plain.execute("SELECT * FROM sqlite_sequence"))
        for kind in ("index", "view", "trigger"):
            for object_kind, name, sql in objects:
                if object_kind != kind or name.startswith("sqlite_"):
                    continue
                encrypted.execute(sql)
        encrypted.execute(f"PRAGMA user_version = {int(user_version)}")
        encrypted.execute(f"PRAGMA application_id = {int(app_id)}")
        if encrypted.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("encrypted migration integrity check failed")
        if encrypted.execute("PRAGMA foreign_key_check").fetchone() is not None:
            raise RuntimeError("encrypted migration foreign-key check failed")
        for table in copied:
            query = f"SELECT count(*) FROM {quote(table)}"
            if encrypted.execute(query).fetchone()[0] != plain.execute(query).fetchone()[0]:
                raise RuntimeError(f"encrypted migration row count failed for {table}")
        encrypted.commit()
        encrypted.close()
        encrypted = None
        fd = os.open(staging, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        os.link(staging, destination)
        directory = os.open(destination.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        plain.close()
        if encrypted is not None:
            encrypted.close()
        staging.unlink(missing_ok=True)
