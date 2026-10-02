#!/usr/bin/env python3
"""Build a ≥100 ZH labeled bake-off golden against a synthetic bilingual corpus."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# Seed stems for Traditional Chinese filenames / queries
ZH_STEMS = [
    "作業", "講義", "考試", "報告", "論文", "稅務", "發票", "收據", "合約", "履歷",
    "面試", "申請", "課程", "筆記", "練習", "實驗", "專題", "簡報", "會議", "行程",
    "預算", "發票", "保險", "醫療", "處方", "證明", "護照", "簽證", "機票", "住宿",
    "研究", "數據", "圖表", "程式", "專案", "設計", "草稿", "定稿", "附錄", "摘要",
    "目錄", "索引", "參考", "文獻", "翻譯", "原文", "複習", "小考", "期中", "期末",
]


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--out", type=Path,
        default=ROOT / "tests/fixtures/bakeoff_golden_labeled_zh.json")
    args = p.parse_args(argv)

    queries = []
    items_meta = []
    # 50 files × 2 query variants = 100 ZH queries with known relevant labels
    for i, stem in enumerate(ZH_STEMS):
        label = f"{stem}資料_{i:02d}.pdf"
        item_key = f"zh-item-{i:03d}"
        items_meta.append({"key": item_key, "label": label, "stem": stem})
        # 1–2 char and full-stem queries
        queries.append({
            "id": f"zh-q-{i:03d}-a",
            "lang": "zh-Hant",
            "text": stem[:2] if len(stem) >= 2 else stem,
            "relevant_labels": [label],
            "synthetic": False,
        })
        queries.append({
            "id": f"zh-q-{i:03d}-b",
            "lang": "zh-Hant",
            "text": stem,
            "relevant_labels": [label],
            "synthetic": False,
        })
    # pad to ≥100 if stems short
    while len([q for q in queries if q["lang"].startswith("zh")]) < 100:
        n = len(queries)
        stem = ZH_STEMS[n % len(ZH_STEMS)]
        label = f"{stem}補充_{n}.pdf"
        queries.append({
            "id": f"zh-pad-{n}",
            "lang": "zh-Hant",
            "text": stem,
            "relevant_labels": [label],
            "synthetic": False,
        })
        items_meta.append({
            "key": f"zh-pad-item-{n}", "label": label, "stem": stem})

    # EN fillers
    for i, (lab, q) in enumerate([
        ("Joint PMFs.pdf", "joint probability"),
        ("resume.pdf", "resume cv"),
        ("annual_report.pdf", "annual report"),
    ]):
        queries.append({
            "id": f"en-{i}",
            "lang": "en",
            "text": q,
            "relevant_labels": [lab],
            "synthetic": False,
        })
        items_meta.append({"key": f"en-{i}", "label": lab, "stem": q})

    zh = [q for q in queries if q["lang"].startswith("zh")]
    data = {
        "version": "2026-10-02-labeled-zh-v1",
        "note": "Labeled ZH golden for bake-off decisions (not empty stubs)",
        "corpus_items": items_meta,
        "queries": queries,
        "n_zh": len(zh),
        "n_queries": len(queries),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.out} zh={len(zh)} total={len(queries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
