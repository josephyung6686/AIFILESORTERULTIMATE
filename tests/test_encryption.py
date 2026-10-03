from __future__ import annotations

import sqlite3

import pytest
import cli

from database_agent.encryption import (
    EncryptionUnavailable,
    EncryptedDatabaseError,
    key_from_file,
    open_encrypted,
)
from database_agent.db import open_database


def test_key_file_is_created_private_and_reused(tmp_path):
    path = tmp_path / "db.key"
    first = key_from_file(path)
    second = key_from_file(path)
    assert first == second and len(first) == 32
    assert oct(path.stat().st_mode & 0o777) == "0o600"


def test_existing_key_file_must_be_regular_private_and_is_not_chmodded(tmp_path):
    path = tmp_path / "db.key"
    path.write_bytes(b"a" * 32)
    path.chmod(0o644)
    with pytest.raises(PermissionError):
        key_from_file(path)
    link = tmp_path / "link.key"
    link.symlink_to(path)
    with pytest.raises(PermissionError):
        key_from_file(link)


def test_sqlcipher_roundtrip_and_wrong_key_refusal(tmp_path):
    path = tmp_path / "secret.sqlite"
    conn = open_encrypted(path, b"a" * 32)
    conn.execute("CREATE TABLE secret (value TEXT)")
    conn.execute("INSERT INTO secret VALUES ('confidential')")
    conn.commit(); conn.close()
    assert b"SQLite format 3" not in path.read_bytes()
    reopened = open_encrypted(path, b"a" * 32)
    assert reopened.execute("SELECT value FROM secret").fetchone()[0] == "confidential"
    reopened.close()
    with pytest.raises(EncryptedDatabaseError):
        open_encrypted(path, b"b" * 32)


def test_plain_sqlite_driver_is_never_used_for_encryption(tmp_path, monkeypatch):
    import database_agent.encryption as encryption
    monkeypatch.setattr(encryption, "_DRIVER", None)
    monkeypatch.setattr(encryption, "_DRIVER_ERROR", ImportError("missing"))
    with pytest.raises(EncryptionUnavailable):
        open_encrypted(tmp_path / "secret.sqlite", b"a" * 32)


def test_open_database_encryption_mode_uses_cipher_and_key_file(tmp_path):
    key_file = tmp_path / "agent.key"
    path = tmp_path / "agent.sqlite"
    conn = open_database(path, encryption=True, encryption_key_file=key_file)
    conn.execute("CREATE TABLE marker (value TEXT)")
    conn.execute("INSERT INTO marker VALUES ('ok')")
    conn.close()
    reopened = open_database(path, encryption=True, encryption_key_file=key_file)
    assert reopened.execute("SELECT value FROM marker").fetchone()["value"] == "ok"
    reopened.close()


def test_cli_search_reads_real_encrypted_index(tmp_path):
    root = tmp_path / "files"
    root.mkdir()
    (root / "resume.txt").write_text("unique encrypted needle", encoding="utf-8")
    plain = tmp_path / "plain.sqlite"
    from items.identity import reconcile_tree
    from items.hot_index import rebuild_fts
    conn = open_database(plain, scan_roots=[root])
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    conn.close()
    encrypted = tmp_path / "encrypted.sqlite"
    key = tmp_path / "agent.key"
    from items.commands_db import db_main
    assert db_main(["encrypt", str(plain), "--database", str(encrypted),
                    "--key-file", str(key)]) == 0
    out = __import__("io").StringIO()
    assert cli.main(["search", "encrypted needle", "--database", str(encrypted),
                     "--key-file", str(key)], out=out) == 0
    assert "resume.txt" in out.getvalue()


def test_database_key_environment_reaches_all_openers_without_creating_missing_key(
    tmp_path, monkeypatch
):
    key = tmp_path / "agent.key"
    path = tmp_path / "agent.sqlite"
    first = open_database(path, encryption=True, encryption_key_file=key)
    first.close()
    key.unlink()
    monkeypatch.setenv("DATABASE_AGENT_KEY_FILE", str(key))
    with pytest.raises(FileNotFoundError):
        open_database(path)


def test_migration_preserves_fts_named_user_table_blob_and_trigger(tmp_path):
    source = tmp_path / "source.sqlite"
    destination = tmp_path / "encrypted.sqlite"
    key_file = tmp_path / "key"
    conn = open_database(source)
    conn.execute("CREATE TABLE item_fts_notes (label TEXT, payload BLOB)")
    conn.execute("CREATE TABLE audit (label TEXT)")
    conn.execute("CREATE TRIGGER audit_insert AFTER INSERT ON item_fts_notes "
                 "BEGIN INSERT INTO audit VALUES (new.label); END")
    conn.execute("INSERT INTO item_fts_notes VALUES (?, ?)", ("item_fts text", b"\\x00\\x01"))
    conn.commit(); conn.close()
    from items.commands_db import db_main
    assert db_main(["encrypt", str(source), "--database", str(destination),
                    "--key-file", str(key_file)]) == 0
    migrated = open_database(destination, encryption=True, encryption_key_file=key_file)
    assert migrated.execute("SELECT label, payload FROM item_fts_notes").fetchone()[1] == b"\\x00\\x01"
    assert migrated.execute("SELECT label FROM audit").fetchone()[0] == "item_fts text"
    migrated.close()


def test_migration_preserves_user_item_fts_name_alongside_real_product_fts(tmp_path):
    source = tmp_path / "source.sqlite"
    destination = tmp_path / "encrypted.sqlite"
    key_file = tmp_path / "key"
    root = tmp_path / "files"
    root.mkdir()
    document = root / "resume.txt"
    document.write_text("encrypted snapshot needle", encoding="utf-8")
    conn = open_database(source, scan_roots=[root])
    from items.identity import reconcile_tree
    from items.hot_index import rebuild_fts
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    conn.execute("CREATE TABLE item_fts_notes (label TEXT, payload BLOB)")
    conn.execute("CREATE TABLE audit (label TEXT)")
    conn.execute("CREATE TRIGGER audit_insert AFTER INSERT ON item_fts_notes "
                 "BEGIN INSERT INTO audit VALUES (new.label); END")
    conn.execute("INSERT INTO item_fts_notes VALUES (?, ?)",
                 ("item_fts text", b"\x00\x01"))
    conn.commit()
    source_rows = [tuple(row) for row in conn.execute(
        "SELECT label, hex(payload) FROM item_fts_notes").fetchall()]
    source_audit = [tuple(row) for row in conn.execute("SELECT label FROM audit").fetchall()]
    snapshots = {
        table: [tuple(row) for row in conn.execute(f'SELECT * FROM "{table}"')]
        for table in ("items", "item_chunks", "item_fts", "item_chunk_fts")
    }
    conn.close()
    # Migration must copy the captured database, even when its source corpus
    # is unavailable. It must not regenerate chunks by rereading source files.
    document.unlink()
    from items.commands_db import db_main
    assert db_main(["encrypt", str(source), "--database", str(destination),
                    "--key-file", str(key_file)]) == 0
    migrated = open_database(destination, encryption=True,
                             encryption_key_file=key_file)
    assert [tuple(row) for row in migrated.execute(
        "SELECT label, hex(payload) FROM item_fts_notes").fetchall()] == source_rows
    assert [tuple(row) for row in migrated.execute("SELECT label FROM audit").fetchall()] == source_audit
    for table, expected in snapshots.items():
        assert [tuple(row) for row in migrated.execute(f'SELECT * FROM "{table}"')] == expected
    migrated.execute("INSERT INTO item_fts_notes VALUES ('later', X'AB')")
    assert migrated.execute("SELECT label FROM audit ORDER BY rowid DESC LIMIT 1").fetchone()[0] == "later"
    from items.search import meaning_search
    result = meaning_search(migrated, "encrypted snapshot needle")
    assert any("resume.txt" in hit.display_label for hit in result.hits)
    migrated.close()


def test_migration_preserves_source_and_refuses_destination_race(tmp_path):
    source = tmp_path / "source.sqlite"
    destination = tmp_path / "encrypted.sqlite"
    key_file = tmp_path / "key"
    conn = open_database(source)
    conn.execute("CREATE TABLE marker (value TEXT)")
    conn.execute("INSERT INTO marker VALUES ('source stays')")
    conn.commit()
    conn.close()
    source_bytes = source.read_bytes()
    destination.write_bytes(b"raced destination")
    from items.commands_db import db_main
    assert db_main(["encrypt", str(source), "--database", str(destination),
                    "--key-file", str(key_file)]) == 2
    assert source.read_bytes() == source_bytes
    assert destination.read_bytes() == b"raced destination"


def test_migration_publication_failure_cleans_staging_and_preserves_source(
    tmp_path, monkeypatch
):
    source = tmp_path / "source.sqlite"
    destination = tmp_path / "encrypted.sqlite"
    key_file = tmp_path / "key"
    conn = open_database(source)
    conn.execute("CREATE TABLE marker (value TEXT)")
    conn.execute("INSERT INTO marker VALUES ('source stays')")
    conn.commit()
    conn.close()
    source_bytes = source.read_bytes()
    import database_agent.encryption as encryption
    real_link = encryption.os.link
    def fail_link(*args, **kwargs):
        raise OSError("injected publication failure")
    monkeypatch.setattr(encryption.os, "link", fail_link)
    from database_agent.encryption import migrate_plaintext
    with pytest.raises(OSError, match="publication"):
        migrate_plaintext(source, destination, b"a" * 32)
    assert source.read_bytes() == source_bytes
    assert not destination.exists()
    assert not list(tmp_path.glob(".encrypted.sqlite.encrypting-*"))
    monkeypatch.setattr(encryption.os, "link", real_link)


def test_migration_destination_created_during_publication_is_preserved(tmp_path, monkeypatch):
    import database_agent.encryption as encryption
    source = tmp_path / "source.sqlite"
    destination = tmp_path / "encrypted.sqlite"
    conn = open_database(source)
    conn.close()
    real_link = encryption.os.link

    def racing_link(staging, target):
        target.write_bytes(b"other writer")
        real_link(staging, target)

    monkeypatch.setattr(encryption.os, "link", racing_link)
    with pytest.raises(FileExistsError):
        encryption.migrate_plaintext(source, destination, b"a" * 32)
    assert destination.read_bytes() == b"other writer"
    assert not list(tmp_path.glob(".encrypted.sqlite.encrypting-*"))
