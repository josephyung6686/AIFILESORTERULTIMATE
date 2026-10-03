#!/usr/bin/env python3
"""Honest search quality evaluation: Recall@10, MRR, nDCG@10, abstention, citations.

Compares hybrid vs FTS-only on the real labeled golden. Records a decision:
hybrid must beat FTS on paraphrases without regressing CJK literal recall;
otherwise ship FTS-only.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _materialize_corpus(data: dict, root: Path) -> dict[str, str]:
    """Write corpus files; return key → filename."""
    key_to_name: dict[str, str] = {}
    for item in data.get("corpus_items") or []:
        name = item["filename"]
        key_to_name[item["key"]] = name
        if "body_prefix" in item:
            body = (item["body_prefix"] * int(item.get("body_prefix_repeat") or 1))
            body += item.get("body_suffix") or ""
        else:
            body = item.get("body") or ""
        (root / name).write_text(body, encoding="utf-8")
    return key_to_name


def _label_maps(conn, key_to_name: dict[str, str]):
    name_to_id = {}
    for row in conn.execute(
        "SELECT item_id, display_label FROM items "
        "WHERE presence='live' AND superseded_by IS NULL"
    ):
        name_to_id[row["display_label"]] = row["item_id"]
    key_to_id = {
        key: name_to_id[name]
        for key, name in key_to_name.items()
        if name in name_to_id
    }
    return key_to_id


def evaluate(
        conn,
        data: dict,
        key_to_id: dict[str, str],
        *,
        mode: str,
        model_dir: Path | None,
        k: int = 10,
) -> dict:
    from items.bakeoff import (
        abstention_correct,
        bootstrap_ci,
        citation_correct,
        mean,
        mrr,
        ndcg_at_k,
        recall_at_k,
    )
    from items.hot_index import find_files

    recalls, mrrs, ndcgs, absts, cites = [], [], [], [], []
    paraphrase_recalls = []
    zh_recalls = []
    per = []
    for q in data["queries"]:
        relevant = {
            key_to_id[key]
            for key in (q.get("relevant_keys") or [])
            if key in key_to_id
        }
        result = find_files(
            conn, q["text"], limit=k, model_dir=model_dir, mode=mode)
        ranked = [h.item_id for h in result.hits]
        r = recall_at_k(ranked, relevant, k=k) if not q.get("negative") else float("nan")
        m = mrr(ranked, relevant) if not q.get("negative") else float("nan")
        n = ndcg_at_k(ranked, relevant, k=k) if not q.get("negative") else float("nan")
        a = abstention_correct(ranked, negative=bool(q.get("negative")), k=k)

        hit = next((h for h in result.hits if h.item_id in relevant), None)
        if q.get("negative"):
            c = a
        elif q.get("expect_citation") == "filename":
            c = (
                1.0
                if hit is not None
                and not hit.claims_body_match
                and "filename" in (hit.match_fields or ())
                else (0.0 if hit is not None else 0.0)
            )
            if hit is None:
                c = 0.0
        else:
            c = citation_correct(
                hit,
                require_chunk=q.get("expect_citation") == "chunk",
                marker=q.get("marker"),
                conn=conn,
            )
            if hit and q.get("min_char_start") is not None and hit.best_chunk_id:
                row = conn.execute(
                    "SELECT char_start FROM item_chunks WHERE chunk_id = ?",
                    (hit.best_chunk_id,),
                ).fetchone()
                if row is None or int(row["char_start"]) < int(q["min_char_start"]):
                    c = 0.0

        if r == r:
            recalls.append(r)
        if m == m:
            mrrs.append(m)
        if n == n:
            ndcgs.append(n)
        if a == a:
            absts.append(a)
        cites.append(c)

        kind = q.get("kind") or ""
        if kind == "paraphrase" and r == r:
            paraphrase_recalls.append(r)
        if str(q.get("lang") or "").startswith("zh") and not q.get("negative") and r == r:
            zh_recalls.append(r)

        per.append({
            "id": q.get("id"),
            "kind": kind,
            "lang": q.get("lang"),
            "recall": None if r != r else r,
            "mrr": None if m != m else m,
            "ndcg": None if n != n else n,
            "abstention": None if a != a else a,
            "citation": c,
            "mode": mode,
        })

    def pack(vals):
        mu, lo, hi = bootstrap_ci(vals)
        return {"mean": mu, "ci95": [lo, hi], "n": len(vals)}

    return {
        "mode": mode,
        "recall_at_10": pack(recalls),
        "mrr": pack(mrrs),
        "ndcg_at_10": pack(ndcgs),
        "abstention": pack(absts),
        "citation_correctness": pack(cites),
        "paraphrase_recall_at_10": pack(paraphrase_recalls),
        "zh_recall_at_10": pack(zh_recalls),
        "per_query": per,
    }


def decide(hybrid: dict, fts: dict) -> dict:
    """Hybrid wins only if paraphrase lift > 0 and CJK does not regress."""
    h_para = hybrid["paraphrase_recall_at_10"]["mean"]
    f_para = fts["paraphrase_recall_at_10"]["mean"]
    h_zh = hybrid["zh_recall_at_10"]["mean"]
    f_zh = fts["zh_recall_at_10"]["mean"]
    # Pairwise paraphrase deltas from per-query when available.
    h_map = {p["id"]: p["recall"] for p in hybrid["per_query"]
             if p.get("kind") == "paraphrase" and p.get("recall") is not None}
    f_map = {p["id"]: p["recall"] for p in fts["per_query"]
             if p.get("kind") == "paraphrase" and p.get("recall") is not None}
    deltas = [h_map[i] - f_map[i] for i in h_map if i in f_map]
    from items.bakeoff import paired_bootstrap_ci
    mean_d, lo, hi = paired_bootstrap_ci(deltas)

    cjk_ok = h_zh >= (f_zh - 1e-9)
    para_wins = mean_d > 0 and lo > 0
    if para_wins and cjk_ok:
        winner = "hybrid"
        reason = (
            f"hybrid paraphrase lift mean={mean_d:.3f} CI=[{lo:.3f},{hi:.3f}]; "
            f"CJK recall hybrid={h_zh:.3f} fts={f_zh:.3f}"
        )
    else:
        winner = "fts"
        reason = (
            f"ship FTS-only: paraphrase hybrid={h_para:.3f} fts={f_para:.3f} "
            f"lift_ci=[{lo:.3f},{hi:.3f}]; CJK hybrid={h_zh:.3f} fts={f_zh:.3f}"
        )
    return {
        "winner": winner,
        "reason": reason,
        "paraphrase_lift_mean": mean_d,
        "paraphrase_lift_ci95": [lo, hi],
        "zh_hybrid": h_zh,
        "zh_fts": f_zh,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--golden", type=Path,
        default=ROOT / "tests/fixtures/search_golden_real.json")
    p.add_argument(
        "--model-dir", type=Path,
        default=Path.home() / ".graph-agent" / "models" / "minilm")
    p.add_argument(
        "--out", type=Path,
        default=ROOT / "docs/superpowers/measurements/"
        "2026-10-03-search-retrieval-decision.json")
    p.add_argument("--embed-chunks", action="store_true", default=True)
    p.add_argument("--no-embed-chunks", action="store_true")
    args = p.parse_args(argv)

    from database_agent.db import open_database
    from items.bakeoff import quality_gate
    from items.hot_index import embed_all_chunks, rebuild_fts
    from items.identity import reconcile_tree
    from items.schema import create_items_schema
    from items.search_mode import write_decision

    data = json.loads(args.golden.read_text(encoding="utf-8"))
    embed = args.embed_chunks and not args.no_embed_chunks

    with tempfile.TemporaryDirectory(prefix="ga-search-eval-") as td:
        root = Path(td) / "lib"
        root.mkdir()
        key_to_name = _materialize_corpus(data, root)
        db = Path(td) / "t.sqlite"
        conn = open_database(db, scan_roots=[])
        create_items_schema(conn)
        reconcile_tree(conn, root)
        rebuild_fts(conn)
        if embed:
            embed_all_chunks(conn, model_dir=args.model_dir)
        conn.commit()
        key_to_id = _label_maps(conn, key_to_name)

        hybrid = evaluate(
            conn, data, key_to_id, mode="hybrid", model_dir=args.model_dir)
        fts = evaluate(
            conn, data, key_to_id, mode="fts", model_dir=args.model_dir)
        gate_failures = quality_gate(conn)
        decision = decide(hybrid, fts)
        conn.close()

    out = {
        "golden": str(args.golden),
        "decision": decision,
        "winner": decision["winner"],
        "reason": decision["reason"],
        "hybrid": {k: hybrid[k] for k in (
            "recall_at_10", "mrr", "ndcg_at_10", "abstention",
            "citation_correctness", "paraphrase_recall_at_10", "zh_recall_at_10")},
        "fts": {k: fts[k] for k in (
            "recall_at_10", "mrr", "ndcg_at_10", "abstention",
            "citation_correctness", "paraphrase_recall_at_10", "zh_recall_at_10")},
        "quality_gate_failures": gate_failures,
        "quality_gate_pass": not gate_failures,
        "model_dir": str(args.model_dir),
        "embedded_chunks": embed,
    }
    write_decision(out, path=args.out)
    print(json.dumps({
        "winner": out["winner"],
        "reason": out["reason"],
        "quality_gate_pass": out["quality_gate_pass"],
        "hybrid_paraphrase": hybrid["paraphrase_recall_at_10"]["mean"],
        "fts_paraphrase": fts["paraphrase_recall_at_10"]["mean"],
        "hybrid_zh": hybrid["zh_recall_at_10"]["mean"],
        "fts_zh": fts["zh_recall_at_10"]["mean"],
    }, ensure_ascii=False, indent=2))
    return 0 if out["quality_gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
