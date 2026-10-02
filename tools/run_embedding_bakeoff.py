#!/usr/bin/env python3
"""EN/ZH embedding bake-off: FTS-only vs MiniLM hybrid on labeled golden.

Decision rule (agent design): pick smallest model that beats FTS on ZH
Recall@10 by ≥15% relative OR keep MiniLM+FTS if FTS already carries ZH
(CJK path) and hybrid does not regress EN.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def recall_at_k(hits, relevant_labels: list[str], k: int = 10) -> float:
    labels = {(h.display_label or "") for h in hits[:k]}
    return 1.0 if any(r in labels for r in relevant_labels) else 0.0


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--golden", type=Path,
        default=ROOT / "tests/fixtures/bakeoff_golden_labeled_zh.json")
    p.add_argument(
        "--model-dir", type=Path,
        default=Path.home() / ".graph-agent" / "models" / "minilm")
    p.add_argument(
        "--out", type=Path,
        default=ROOT / "docs/superpowers/measurements/"
        "2026-10-02-embedding-bakeoff-decision.json")
    args = p.parse_args(argv)

    from items.bakeoff import paired_bootstrap_ci, validate_golden
    from database_agent.db import open_database
    from items.hot_index import find_files, rebuild_fts, _fts_search, ensure_fts
    from items.identity import reconcile_tree
    from items.schema import create_items_schema

    if not args.golden.is_file():
        import subprocess
        subprocess.check_call([
            sys.executable,
            str(ROOT / "tools/gen_bakeoff_golden_zh.py"),
            "--out", str(args.golden),
        ])

    meta = validate_golden(args.golden)
    data = json.loads(args.golden.read_text(encoding="utf-8"))
    if not meta["ok_for_decision"]:
        print("golden too small for decision", meta)
        return 2

    with tempfile.TemporaryDirectory(prefix="ga-bakeoff-") as td:
        root = Path(td) / "lib"
        root.mkdir()
        for item in data.get("corpus_items") or []:
            label = item["label"]
            stem = item.get("stem") or label
            (root / label).write_text(
                f"{stem} {label} content body", encoding="utf-8")
        db = Path(td) / "t.sqlite"
        conn = open_database(db, scan_roots=[])
        create_items_schema(conn)
        reconcile_tree(conn, root)
        rebuild_fts(conn)
        conn.commit()

        zh_h, zh_f, en_h, en_f = [], [], [], []
        per = []
        for q in data["queries"]:
            text = q["text"]
            relevant = q.get("relevant_labels") or []
            hybrid = find_files(
                conn, text, limit=10, model_dir=args.model_dir)
            # FTS-only ranks → fake hits via items table order
            ensure_fts(conn)
            fts_ranks = _fts_search(conn, text, limit=10)
            fts_hits = []
            for item_id, _rank in sorted(fts_ranks.items(), key=lambda kv: kv[1]):
                row = conn.execute(
                    "SELECT display_label, open_target, typing_state "
                    "FROM items WHERE item_id=?", (item_id,)
                ).fetchone()
                if row:
                    from items.hot_index import FindHit
                    fts_hits.append(FindHit(
                        item_id=item_id,
                        display_label=row["display_label"],
                        open_target=row["open_target"],
                        typing_state=row["typing_state"],
                        score=0.0, channels=("fts",), protected=False,
                        citations=(item_id,),
                    ))
            rh = recall_at_k(hybrid.hits, relevant)
            rf = recall_at_k(fts_hits, relevant)
            lang = q.get("lang") or "en"
            if str(lang).startswith("zh"):
                zh_h.append(rh)
                zh_f.append(rf)
            else:
                en_h.append(rh)
                en_f.append(rf)
            per.append({
                "id": q.get("id"), "lang": lang, "text": text,
                "hybrid": rh, "fts": rf,
            })
        conn.close()

    def mean(xs):
        return sum(xs) / len(xs) if xs else 0.0

    zh_hybrid = mean(zh_h)
    zh_fts = mean(zh_f)
    en_hybrid = mean(en_h)
    en_fts = mean(en_f)
    deltas = [h - f for h, f in zip(zh_h, zh_f)]
    mean_d, lo, hi = paired_bootstrap_ci(deltas)

    # Decision
    relative = (
        ((zh_hybrid - zh_fts) / zh_fts) if zh_fts > 0
        else (1.0 if zh_hybrid > 0 else 0.0)
    )
    if relative >= 0.15 and lo > 0:
        winner = "minilm_hybrid"
        reason = (
            f"ZH hybrid beats FTS by {relative:.0%} "
            f"(bootstrap CI [{lo:.3f},{hi:.3f}])"
        )
    elif zh_fts >= 0.85 and en_hybrid >= en_fts - 0.05:
        winner = "minilm_hybrid_plus_cjk_fts"
        reason = (
            "CJK FTS already carries ZH (≥0.85 Recall@10); keep MiniLM for EN "
            "semantic; no larger multilingual model required yet"
        )
    else:
        winner = "needs_multilingual_bakeoff"
        reason = (
            f"ZH hybrid={zh_hybrid:.3f} fts={zh_fts:.3f} — schedule "
            f"paraphrase-multilingual / EmbeddingGemma bake-off"
        )

    out = {
        "golden": str(args.golden),
        "n_zh": len(zh_h),
        "n_en": len(en_h),
        "zh_recall_at_10_hybrid": zh_hybrid,
        "zh_recall_at_10_fts": zh_fts,
        "en_recall_at_10_hybrid": en_hybrid,
        "en_recall_at_10_fts": en_fts,
        "zh_hybrid_minus_fts_mean": mean_d,
        "zh_hybrid_minus_fts_ci95": [lo, hi],
        "winner": winner,
        "reason": reason,
        "model_dir": str(args.model_dir),
        "per_query_sample": per[:12],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in (
        "winner", "reason", "zh_recall_at_10_hybrid", "zh_recall_at_10_fts",
        "en_recall_at_10_hybrid", "n_zh")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
