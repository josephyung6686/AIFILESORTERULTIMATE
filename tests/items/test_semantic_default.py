"""Semantic recognition turns on only when local weights are complete."""
from __future__ import annotations

from pathlib import Path

import cli


def test_resolve_off_when_default_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "DEFAULT_SEMANTIC_MODEL_DIR", tmp_path / "missing")
    assert cli.resolve_semantic_model_dir(None) is None


def test_resolve_on_when_default_complete(tmp_path, monkeypatch):
    model_dir = tmp_path / "minilm"
    model_dir.mkdir()
    (model_dir / "model.onnx").write_bytes(b"fake")
    (model_dir / "tokenizer.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(cli, "DEFAULT_SEMANTIC_MODEL_DIR", model_dir)
    assert cli.resolve_semantic_model_dir(None) == model_dir


def test_named_incomplete_does_not_fall_through(tmp_path, monkeypatch):
    good = tmp_path / "good"
    good.mkdir()
    (good / "model.onnx").write_bytes(b"fake")
    (good / "tokenizer.json").write_text("{}", encoding="utf-8")
    bad = tmp_path / "bad"
    bad.mkdir()
    monkeypatch.setattr(cli, "DEFAULT_SEMANTIC_MODEL_DIR", good)
    assert cli.resolve_semantic_model_dir(bad) is None


def test_named_complete_wins(tmp_path, monkeypatch):
    named = tmp_path / "named"
    named.mkdir()
    (named / "model.onnx").write_bytes(b"x")
    (named / "tokenizer.json").write_text("{}", encoding="utf-8")
    other = tmp_path / "other"
    other.mkdir()
    (other / "model.onnx").write_bytes(b"y")
    (other / "tokenizer.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(cli, "DEFAULT_SEMANTIC_MODEL_DIR", other)
    assert cli.resolve_semantic_model_dir(named) == named
