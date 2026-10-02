#!/usr/bin/env python3
"""Generate a ≥100 ZH synthetic golden stub for bake-off sample-size gates."""
from __future__ import annotations

import json
from pathlib import Path

CHARS = "作業稅務講義課程筆記概率統計經濟會計報告研究論文"


def main() -> int:
    queries = []
    for i in range(100):
        a = CHARS[i % len(CHARS)]
        b = CHARS[(i + 3) % len(CHARS)]
        queries.append({
            "id": f"zh-{i:03d}",
            "lang": "zh-Hant",
            "text": f"{a}{b}",
            "relevant_item_ids": [],
            "synthetic": True,
        })
    for i in range(40):
        queries.append({
            "id": f"en-{i:03d}",
            "lang": "en",
            "text": f"lecture notes topic {i}",
            "relevant_item_ids": [],
            "synthetic": True,
        })
    out = Path("tests/fixtures/bakeoff_golden_100zh.json")
    out.write_text(json.dumps({
        "version": "2026-10-02-synthetic-100zh",
        "note": "Synthetic size fixture only — not for model winner decisions",
        "queries": queries,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out} n={len(queries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
