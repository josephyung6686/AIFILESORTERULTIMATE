"""Bake off candidate prompts for one call site under the local and cloud models.

    python3 -m tools.promptbench run --site C_placement --candidates c1,c2 \
        --models local,cloud --out tools/promptbench/out/<run>
    python3 -m tools.promptbench score --out tools/promptbench/out/<run>
    python3 -m tools.promptbench dossier --site C_placement --case C01 --candidate c1
    python3 -m tools.promptbench run --site C_placement --candidates c1 --dry-run

Every call is written to `<out>/calls/<site>/<candidate>/<model>/<case>.json`
as it completes (request bytes, response bytes, verdicts, grounding, latency,
tokens, `num_ctx`), so an interrupted run resumes where it stopped and `score`
re-reads the files without a model. The cloud call ledger is ONE file shared by
every run (`tools/promptbench/out/cloud_ledger.json`): the cap is on the whole
bakeoff. Nothing here reads the owner's corpus; every case is synthetic.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import traceback
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
for entry in (str(_ROOT), str(_ROOT / "src")):
    if entry not in sys.path:
        sys.path.insert(0, entry)

from llm_harness.fingerprint import prompt_fingerprint          # noqa: E402
from llm_harness.vocabulary import A_FACT, E_TEMPLATE            # noqa: E402

from tools.promptbench.candidates import candidate as load_candidate   # noqa: E402
from tools.promptbench.cases import check_cases                        # noqa: E402
from tools.promptbench.clients import (                                # noqa: E402
    CallLedger, CloudCapReached, cloud_client, local_client, num_ctx_for,
)
from tools.promptbench.dossiers import (                                 # noqa: E402
    dossier_of, model_visible_bytes, readings_for,
)
from tools.promptbench.judge import judge, site_dependencies_for         # noqa: E402
from tools.promptbench.report import write_summary                       # noqa: E402
from tools.promptbench.suites import all_cases_for, cases_for             # noqa: E402

DEFAULT_LEDGER = _ROOT / "tools" / "promptbench" / "out" / "cloud_ledger.json"
DEFAULT_CAP = 400


def _catalogue():
    from production import load_shipped_catalogue, read_packaged_library_file
    return load_shipped_catalogue(read_packaged_library_file)


def _prepare(case, candidate, *, site, out: Path, catalogue):
    """The dossier, its authorities and the model-visible bytes for one case."""
    if site == A_FACT:
        from tools.promptbench.site_a import (
            build_world, contradicts_for_a, use_glossary,
        )
        glossary = use_glossary(candidate.glossary_path())
        world = build_world(case, out / "worlds" / candidate.name,
                            catalogue=catalogue)
        dossier = dossier_of(
            world.case, allowed_vocabulary=world.allowed_vocabulary,
            folder_levels=tuple((l.field, l.label, l.requirement)
                                for l in world.folder_levels))
        return dict(case=world.case, dossier=dossier,
                    site_dependencies=world.site_dependencies,
                    resolver=world.resolver, contradicts=contradicts_for_a(),
                    conn=world.conn, glossary=glossary)
    dossier = dossier_of(case)
    return dict(case=case, dossier=dossier,
                site_dependencies=site_dependencies_for(
                    case, catalogue=catalogue if site == E_TEMPLATE else None),
                resolver=None, contradicts=None, conn=None, glossary=None)


def run_site(*, site: str, candidate_names: list[str], model_names: list[str],
             out: Path, case_ids: list[str] | None = None, cap: int = DEFAULT_CAP,
             ledger_path: Path = DEFAULT_LEDGER, clients: dict | None = None,
             dry_run: bool = False, redo: bool = False, log=print) -> Path:
    catalogue = _catalogue()
    out.mkdir(parents=True, exist_ok=True)
    built_clients = dict(clients or {})
    if not dry_run:
        ledger = CallLedger(path=ledger_path, cap=cap)
        for name in model_names:
            if name in built_clients:
                continue
            if name == "local":
                built_clients[name] = local_client()
            elif name == "cloud":
                built_clients[name] = cloud_client(ledger)
            else:
                raise SystemExit(f"unknown model {name!r}; use local, cloud or an "
                                 "injected client")
    for name in candidate_names:
        candidate = load_candidate(site, name)
        prompt = candidate.prompt()
        schema = candidate.response_schema()
        fingerprint = prompt_fingerprint(prompt)
        cases = cases_for(site, candidate.suite)
        check_cases(cases)
        if case_ids:
            wanted = set(case_ids)
            cases = tuple(case for case in cases if case.case_id in wanted)
        per_case_rows = "@case" in candidate.readings_rows
        readings = (None if per_case_rows or not candidate.readings_rows
                    else readings_for(candidate.readings_rows))
        log(f"[{site}] candidate {name} ({candidate.template_id}) "
            f"fingerprint {fingerprint[:16]}"
            + (f" suite {candidate.suite}" if candidate.suite else "")
            + (f" readings {len(readings)} layout {candidate.layout}" if readings else ""))
        for case in cases:
            prepared = _prepare(case, candidate, site=site, out=out,
                                catalogue=catalogue)
            if per_case_rows:
                readings = readings_for(
                    case.authorities.get("readings_rows", ()), strict=False)
            payload = model_visible_bytes(prepared["dossier"], prompt,
                                          readings=readings, layout=candidate.layout)
            if dry_run:
                log(f"  {case.case_id}: {len(payload)} bytes, local num_ctx "
                    f"{num_ctx_for(len(payload))}, should_abstain={case.should_abstain}"
                    f" -- {case.title}")
                continue
            for model in model_names:
                path = out / "calls" / site / name / model / f"{case.case_id}.json"
                if path.exists() and not redo:
                    log(f"  {case.case_id}/{model}: already recorded, skipping")
                    continue
                path.parent.mkdir(parents=True, exist_ok=True)
                record = {
                    "site": site, "case_id": case.case_id, "title": case.title,
                    "candidate": name, "template_id": candidate.template_id,
                    "prompt_fingerprint": fingerprint, "model": model,
                    "glossary_in_force": prepared["glossary"],
                    "request_sha256": hashlib.sha256(payload).hexdigest(),
                    "request_bytes": len(payload),
                    "readings_count": len(readings) if readings else 0,
                    "readings_bytes": (len(json.dumps(readings, ensure_ascii=False)
                                           .encode("utf-8")) if readings else 0),
                    "layout": candidate.layout,
                    "request": payload.decode("utf-8"),
                    "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                }
                try:
                    response, meta = built_clients[model](payload)
                    record["response"] = response.decode("utf-8", "replace")
                    record["meta"] = meta.__dict__
                    judgement = judge(
                        prepared["case"], prepared["dossier"], response,
                        schema=schema,
                        site_dependencies=prepared["site_dependencies"],
                        evidence_resolver=prepared["resolver"],
                        contradicts=prepared["contradicts"],
                        conn=prepared["conn"], model_id=meta.model_id,
                        prompt_fingerprint=fingerprint)
                    record["judgement"] = judgement.as_dict()
                    log(f"  {case.case_id}/{model}: {judgement.worst_outcome} "
                        f"abstained={judgement.abstained} correct={judgement.correct}"
                        f" {meta.latency_seconds:.1f}s")
                except CloudCapReached as stop:
                    log(f"  {case.case_id}/{model}: {stop}")
                    record["error"] = f"cap: {stop}"
                    path.write_text(json.dumps(record, indent=1), encoding="utf-8")
                    return out
                except Exception as problem:  # recorded, never silently dropped
                    record["error"] = f"{type(problem).__name__}: {problem}"[:500]
                    record["traceback"] = traceback.format_exc()[-2000:]
                    log(f"  {case.case_id}/{model}: FAILED {record['error']}")
                path.write_text(json.dumps(record, indent=1, ensure_ascii=False),
                                encoding="utf-8")
            if prepared["conn"] is not None:
                prepared["conn"].close()
    if not dry_run:
        write_summary(out)
    return out


def rejudge_site(*, site: str, out: Path, log=print) -> int:
    """Re-run the judge over every recorded response for a site, without a model.

    The dossier is rebuilt from the case (deterministic), the stored response
    bytes are judged again, and the record's judgement is replaced. This is how
    a corrected reader or an extended expectation reaches numbers already paid
    for; the request and response bytes are never touched.
    """
    cases = {case.case_id: case for case in all_cases_for(site)}
    catalogue = _catalogue()
    prepared_by_candidate: dict[str, dict] = {}
    count = 0
    for path in sorted((out / "calls" / site).rglob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("error") or "response" not in record:
            continue
        candidate = load_candidate(site, record["candidate"])
        key = (record["candidate"], record["case_id"])
        if key not in prepared_by_candidate:
            prepared_by_candidate[key] = _prepare(
                cases[record["case_id"]], candidate, site=site, out=out,
                catalogue=catalogue)
        prepared = prepared_by_candidate[key]
        judgement = judge(
            prepared["case"], prepared["dossier"],
            record["response"].encode("utf-8"), schema=candidate.response_schema(),
            site_dependencies=prepared["site_dependencies"],
            evidence_resolver=prepared["resolver"], contradicts=prepared["contradicts"],
            conn=prepared["conn"], model_id=record["meta"]["model_id"],
            prompt_fingerprint=record["prompt_fingerprint"])
        record["judgement"] = judgement.as_dict()
        record["rejudged_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        path.write_text(json.dumps(record, indent=1, ensure_ascii=False),
                        encoding="utf-8")
        count += 1
    for prepared in prepared_by_candidate.values():
        if prepared["conn"] is not None:
            prepared["conn"].close()
    write_summary(out)
    log(f"[{site}] re-judged {count} records under {out}")
    return count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools.promptbench", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run")
    run.add_argument("--site", required=True)
    run.add_argument("--candidates", required=True,
                     help="comma-separated candidate names from the drafts manifest")
    run.add_argument("--models", default="local,cloud")
    run.add_argument("--out", type=Path, required=False)
    run.add_argument("--cases", default="", help="comma-separated case ids (default all)")
    run.add_argument("--cap", type=int, default=DEFAULT_CAP)
    run.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--redo", action="store_true",
                     help="re-run cases already recorded under --out")

    score = sub.add_parser("score")
    score.add_argument("--out", type=Path, required=True)

    show = sub.add_parser("dossier")
    show.add_argument("--site", required=True)
    show.add_argument("--case", required=True)
    show.add_argument("--candidate", required=True)

    tables = sub.add_parser("tables", help="the packet's stress-case table for one site")
    tables.add_argument("--site", required=True)
    tables.add_argument("--out", type=Path, required=True)
    tables.add_argument("--suite", default=None, help="a named suite instead of the site's own")

    rejudge = sub.add_parser("rejudge", help="re-run the judge over recorded responses")
    rejudge.add_argument("--site", required=True)
    rejudge.add_argument("--out", type=Path, required=True)

    args = parser.parse_args(argv)
    if args.command == "rejudge":
        rejudge_site(site=args.site, out=args.out)
        return 0
    if args.command == "score":
        summary = write_summary(args.out)
        print(json.dumps(summary, indent=1))
        return 0
    if args.command == "tables":
        from tools.promptbench.report import stress_tables
        sys.stdout.write(stress_tables(args.out, cases_for(args.site, args.suite)))
        return 0
    if args.command == "dossier":
        candidate = load_candidate(args.site, args.candidate)
        case = next(c for c in all_cases_for(args.site) if c.case_id == args.case)
        prepared = _prepare(case, candidate, site=args.site,
                            out=Path("/tmp/promptbench-dossier"),
                            catalogue=_catalogue())
        sys.stdout.write(model_visible_bytes(
            prepared["dossier"], candidate.prompt(),
            readings=(readings_for(candidate.readings_rows)
                      if candidate.readings_rows else None),
            layout=candidate.layout).decode("utf-8"))
        sys.stdout.write("\n")
        return 0
    out = args.out or (_ROOT / "tools" / "promptbench" / "out"
                       / f"{args.site}-{time.strftime('%Y%m%d-%H%M%S')}")
    run_site(site=args.site,
             candidate_names=[c for c in args.candidates.split(",") if c],
             model_names=[m for m in args.models.split(",") if m],
             out=out, case_ids=[c for c in args.cases.split(",") if c] or None,
             cap=args.cap, ledger_path=args.ledger, dry_run=args.dry_run,
             redo=args.redo)
    print(f"written under {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
