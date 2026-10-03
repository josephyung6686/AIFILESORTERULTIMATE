"""Sensitivity is decided locally while indexing, by the sorter's own rules."""
from __future__ import annotations

import socket
from pathlib import Path

import pytest

from database_agent.db import open_database
from items.file_identity import item_is_sensitive
from items.hot_index import find_files
from items.indexing import counts, index_folder


def text_pdf(text: str) -> bytes:
    """A one-page PDF whose page carries `text` as real text."""
    stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n"
        + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode()
    out += (f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref}\n%%EOF\n").encode()
    return bytes(out)


@pytest.fixture
def no_network(monkeypatch):
    def refuse(*_args, **_kwargs):
        raise AssertionError("indexing opened a network connection")
    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)


def _item(conn, label: str) -> str:
    return conn.execute("SELECT item_id FROM items WHERE display_label = ?",
                        (label,)).fetchone()["item_id"]


def test_sensitive_files_are_protected_after_indexing(tmp_path, no_network):
    root = tmp_path / "home"
    root.mkdir()
    (root / "HKID_card.pdf").write_bytes(text_pdf("A123456(3)"))
    (root / "vaccination_record.pdf").write_bytes(text_pdf("dose two"))
    (root / "notes.txt").write_text("shopping list", encoding="utf-8")
    conn = open_database(tmp_path / "a.sqlite", scan_roots=[])

    c = index_folder(conn, root)

    assert item_is_sensitive(conn, _item(conn, "HKID_card.pdf"))
    assert item_is_sensitive(conn, _item(conn, "vaccination_record.pdf"))
    assert not item_is_sensitive(conn, _item(conn, "notes.txt"))
    assert c.protected >= 2
    assert counts(conn) == c
    hits = [h for h in find_files(conn, "vaccination", limit=5).hits
            if h.display_label == "vaccination_record.pdf"]
    assert hits and hits[0].protected and hits[0].open_target is None
