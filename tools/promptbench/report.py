# tools/promptbench/report.py
"""Per candidate, per model: the numbers `103` §28.1 step 4 asks for.

Reads the per-call JSON files a run wrote and aggregates them. Re-runnable
without a model (`python3 -m tools.promptbench score --out DIR`), which is what
to use while a scoring rule is being argued about -- the calls are the slow and
the paid part.
"""
from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path


def load_calls(out: Path) -> list[dict]:
    calls = []
    for path in sorted((out / "calls").rglob("*.json")):
        calls.append(json.loads(path.read_text(encoding="utf-8")))
    return calls


def _rate(numerator: int, denominator: int) -> float | None:
    return None if denominator == 0 else round(numerator / denominator, 3)


def aggregate(calls: list[dict]) -> dict:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for call in calls:
        groups[(call["site"], call["candidate"], call["model"])].append(call)
    rows = []
    for (site, candidate, model), items in sorted(groups.items()):
        judged = [c for c in items if c.get("judgement")]
        failed = [c for c in items if not c.get("judgement")]
        n = len(items)
        j = [c["judgement"] for c in judged]
        should_abstain = [x for x in j if x["should_abstain"]]
        should_answer = [x for x in j if not x["should_abstain"]]
        answerable = [x for x in should_answer if x["correct"] is not None]
        cit_total = sum(x["citations_total"] for x in j)
        cit_matched = sum(x["citations_span_matched"] for x in j)
        latencies = [c["meta"]["latency_seconds"] for c in items
                     if c.get("meta") and c["meta"].get("latency_seconds") is not None]
        prompt_tokens = [c["meta"].get("prompt_tokens") for c in items
                         if c.get("meta") and c["meta"].get("prompt_tokens")]
        completion_tokens = [c["meta"].get("completion_tokens") for c in items
                             if c.get("meta") and c["meta"].get("completion_tokens")]
        num_ctx = sorted({c["meta"].get("num_ctx") for c in items
                          if c.get("meta") and c["meta"].get("num_ctx")})
        rows.append({
            "site": site, "candidate": candidate, "model": model,
            "cases": n, "calls_failed": len(failed),
            "parsed_rate": _rate(sum(1 for x in j if x["parsed"]), n),
            "json_schema_valid_rate": _rate(
                sum(1 for x in j if x["json_schema_valid"]), n),
            "validator_schema_ok_rate": _rate(
                sum(1 for x in j if not any(
                    "SCHEMA_INVALID" in v["reasons"] for v in x["verdicts"])), n),
            "accepted_rate": _rate(sum(1 for x in j if x["accepted"]), n),
            "grounding_rate": _rate(cit_matched, cit_total),
            "citations_total": cit_total,
            "abstain_rate_on_should_abstain": _rate(
                sum(1 for x in should_abstain if x["abstained"]), len(should_abstain)),
            "should_abstain_cases": len(should_abstain),
            "correct_rate_on_should_answer": _rate(
                sum(1 for x in answerable if x["correct"]), len(answerable)),
            "correct_and_accepted_rate": _rate(
                sum(1 for x in answerable if x["correct"] and x["accepted"]),
                len(answerable)),
            "false_abstain_rate_on_should_answer": _rate(
                sum(1 for x in answerable if x["abstained"]), len(answerable)),
            "should_answer_cases": len(answerable),
            "median_latency_s": (round(statistics.median(latencies), 2)
                                 if latencies else None),
            "prompt_tokens_total": sum(prompt_tokens) if prompt_tokens else None,
            "completion_tokens_total": (sum(completion_tokens)
                                        if completion_tokens else None),
            "num_ctx_used": num_ctx,
            "worst_outcomes": dict(sorted(
                _count(x["worst_outcome"] for x in j).items())),
            "reasons": dict(sorted(_count(
                r for x in j for v in x["verdicts"] for r in v["reasons"]).items())),
        })
    return {"rows": rows}


def _count(values) -> dict:
    counts: dict = defaultdict(int)
    for value in values:
        counts[str(value)] += 1
    return counts


def per_case_table(calls: list[dict]) -> list[dict]:
    rows = []
    for call in sorted(calls, key=lambda c: (c["site"], c["case_id"],
                                             c["candidate"], c["model"])):
        j = call.get("judgement") or {}
        rows.append({
            "site": call["site"], "case": call["case_id"],
            "candidate": call["candidate"], "model": call["model"],
            "should_abstain": j.get("should_abstain"),
            "abstained": j.get("abstained"), "correct": j.get("correct"),
            "accepted": j.get("accepted"), "worst": j.get("worst_outcome"),
            "reasons": sorted({r for v in j.get("verdicts", []) for r in v["reasons"]}),
            "schema": j.get("json_schema_valid"),
            "grounding": f"{j.get('citations_span_matched')}/{j.get('citations_total')}",
            "answer": _short(j.get("answer")),
            "error": call.get("error"),
            "latency_s": round(call["meta"]["latency_seconds"], 1)
            if call.get("meta") else None,
        })
    return rows


def _short(answer) -> str:
    if not isinstance(answer, dict):
        return ""
    keep = {k: v for k, v in answer.items()
            if k in ("destination", "action", "target", "coherent", "label",
                     "category", "members", "outliers", "dimensions", "fields",
                     "support", "next_support", "refinement")}
    text = json.dumps(keep, separators=(",", ":"), ensure_ascii=False)
    return text if len(text) <= 160 else text[:157] + "..."


def markdown(summary: dict, table: list[dict]) -> str:
    lines = ["# promptbench summary", ""]
    lines.append("| site | candidate | model | cases | failed | schema | validator ok | accepted | grounding | abstain (should) | correct (should answer) | correct+accepted | false abstain | median s | prompt tok | completion tok | num_ctx |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in summary["rows"]:
        lines.append(
            f"| {r['site']} | {r['candidate']} | {r['model']} | {r['cases']} | "
            f"{r['calls_failed']} | {r['json_schema_valid_rate']} | "
            f"{r['validator_schema_ok_rate']} | {r['accepted_rate']} | "
            f"{r['grounding_rate']} ({r['citations_total']}) | "
            f"{r['abstain_rate_on_should_abstain']} ({r['should_abstain_cases']}) | "
            f"{r['correct_rate_on_should_answer']} ({r['should_answer_cases']}) | "
            f"{r['correct_and_accepted_rate']} | "
            f"{r['false_abstain_rate_on_should_answer']} | {r['median_latency_s']} | "
            f"{r['prompt_tokens_total']} | {r['completion_tokens_total']} | "
            f"{','.join(str(x) for x in r['num_ctx_used'])} |")
    lines.append("")
    lines.append("## Per case")
    lines.append("")
    lines.append("| site | case | candidate | model | should abstain | abstained | correct | accepted | worst | reasons | schema | grounding | answer | error |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in table:
        lines.append(
            f"| {r['site']} | {r['case']} | {r['candidate']} | {r['model']} | "
            f"{r['should_abstain']} | {r['abstained']} | {r['correct']} | "
            f"{r['accepted']} | {r['worst']} | {','.join(r['reasons'])} | "
            f"{r['schema']} | {r['grounding']} | `{r['answer']}` | {r['error'] or ''} |")
    return "\n".join(lines) + "\n"


def _cell(call: dict | None) -> str:
    """One arm's result for one case, short enough for a table cell."""
    if call is None:
        return "—"
    if call.get("error"):
        return "ERR"
    j = call.get("judgement") or {}
    if j.get("should_abstain"):
        mark = "abstained" if j.get("abstained") else "ANSWERED"
    else:
        mark = ("correct" if j.get("correct") else
                ("false abstain" if j.get("abstained") else "WRONG"))
    outcome = (j.get("worst_outcome") or "?").replace("accept_", "acc_")
    reasons = sorted({r for v in j.get("verdicts", []) for r in v["reasons"]})
    tail = f" {','.join(reasons)}" if reasons else ""
    return f"{mark} / {outcome}{tail}"


def stress_tables(out: Path, cases) -> str:
    """The packet's per-site stress-case table: one row per case, one column per
    candidate x model, rendered from the recorded calls."""
    calls = load_calls(out)
    by_key = {(c["case_id"], c["candidate"], c["model"]): c for c in calls}
    arms = sorted({(c["candidate"], c["model"]) for c in calls})
    lines = ["| case | persona | traces | expectation | " +
             " | ".join(f"{cand} / {model}" for cand, model in arms) + " |",
             "|---|---|---|---|" + "---|" * len(arms)]
    for case in cases:
        expect = json.dumps(case.expect, separators=(",", ":"), ensure_ascii=False)
        if len(expect) > 90:
            expect = expect[:87] + "..."
        kind = "abstain" if case.should_abstain else "answer"
        cells = [_cell(by_key.get((case.case_id, cand, model))) for cand, model in arms]
        lines.append(
            f"| {case.case_id} — {case.title} | {case.persona} | "
            f"{', '.join(case.traces)} | {kind}: `{expect}` | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def write_summary(out: Path) -> dict:
    calls = load_calls(out)
    summary = aggregate(calls)
    table = per_case_table(calls)
    (out / "summary.json").write_text(
        json.dumps({"summary": summary, "per_case": table}, indent=1),
        encoding="utf-8")
    (out / "summary.md").write_text(markdown(summary, table), encoding="utf-8")
    return summary


__all__ = ["aggregate", "load_calls", "markdown", "per_case_table", "stress_tables",
           "write_summary"]
