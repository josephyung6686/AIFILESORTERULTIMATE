"""Score the product against hand-made ground truth.

    python3 -m tools.groundtruth --corpus DIR --labels FILE --out DIR

Runs the real product over the whole corpus once per labelled situation, reads
each run's plan database, and prints a scorecard plus a per-file table.

It moves nothing, sends nothing and opens no file of the owner's: it reads the
databases the product wrote, and never `text_units.text`.

`--score-only` re-reads databases a previous run left in `--out`, which is what
to use while changing the scoring rules -- the runs are the slow part.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.groundtruth.labels import load_labels                    # noqa: E402
from tools.groundtruth.discrimination import (                      # noqa: E402
    report as discrimination_report,
)
from tools.groundtruth.measure import observe_run                   # noqa: E402
from tools.groundtruth.report import (                              # noqa: E402
    breach_detail, per_file_table, scorecard,
)
from tools.groundtruth.protected_evidence import (                  # noqa: E402
    report as protected_evidence_report,
)
from tools.groundtruth.run import label_for, run_situations         # noqa: E402
from tools.groundtruth.score import (                               # noqa: E402
    over_marked, protected_verdict, score_situation,
)


def _promised_levels() -> dict[str, tuple[str, ...]]:
    sys.path.insert(0, str(_ROOT / "src"))
    from cli import load_shipped_catalogue, read_packaged_library_file
    from production import shipped_situations

    catalogue = load_shipped_catalogue(read_packaged_library_file)
    return {row.name: tuple(row.folder_levels) for row in shipped_situations(catalogue)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools.groundtruth", description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True,
                        help="the labelled corpus to read")
    parser.add_argument("--labels", type=Path, required=True,
                        help="the hand-made ground truth for it")
    parser.add_argument("--out", type=Path, required=True,
                        help="where the run databases and the scorecard go")
    parser.add_argument("--workers", type=int, default=4,
                        help="how many situation runs at once (default 4)")
    # The number lives HERE, at the composition root, and not in the runner --
    # same rule `src/` follows. Eight is one busy core's worth of headroom on
    # this machine and is a policy, not a fact, which is why it is visible and
    # changeable from the command line.
    parser.add_argument("--load-ceiling", type=float, default=8.0,
                        help="refuse to start if the one-minute load average is "
                             "above this (default 8.0). Every run here is six "
                             "processes reading the whole corpus, and starting "
                             "beside somebody else's timing run spoils theirs.")
    parser.add_argument(
        "--force", action="store_true",
        help="start even though the machine is above --load-ceiling. What this "
             "overrides: the check that stops this run contending with work "
             "already on the machine. Anything being TIMED beside it becomes "
             "unreliable -- not slower, wrong -- and the person who finds out "
             "is whoever reads that number later. Pass it only when you know "
             "what else is running.")
    parser.add_argument("--situation", action="append", default=[],
                        help="score only this situation; repeatable")
    parser.add_argument("--score-only", action="store_true",
                        help="re-score the databases already in --out")
    parser.add_argument(
        "--enable-cloud", action="store_true",
        help="let the runs send files to the cloud model, and SPEND THE "
             "OWNER'S MONEY. Off unless you type it; without it the runs "
             "cannot read the credential at all. Score a small sample first: "
             "every situation run reads the whole corpus, so seventeen "
             "situations over two hundred files is seventeen times the spend "
             "of one.")
    args = parser.parse_args(argv)

    labels = load_labels(args.labels)
    situations = tuple(args.situation) or labels.situations()
    promised = _promised_levels()
    args.out.mkdir(parents=True, exist_ok=True)
    corpus_files = sum(1 for p in args.corpus.rglob("*") if p.is_file())

    started = time.monotonic()
    if args.score_only:
        print(f"re-scoring {len(situations)} databases in {args.out}")
    else:
        print(f"running {len(situations)} situations over {corpus_files} files, "
              f"{args.workers} at a time. Each run reads the whole corpus.")
        if args.enable_cloud:
            print(f"!! SENDING TO THE CLOUD MODEL: {len(situations)} runs over "
                  f"{corpus_files} files each. This spends money.", flush=True)
        results = run_situations(
            args.corpus, situations, args.out, workers=args.workers,
            load_ceiling=args.load_ceiling, force=args.force,
            cloud=args.enable_cloud,
            on_done=lambda r: print(f"  {r.seconds / 60:5.1f} min  exit {r.exit_code}  "
                                    f"{r.situation}", flush=True))
        for result in results:
            if result.exit_code != 0:
                print(f"\n!! {result.situation} exited {result.exit_code}\n"
                      f"{result.stderr}", file=sys.stderr)

    runs, missing = [], []
    for situation in situations:
        stem = situation.replace(".", "_")
        database = args.out / f"{stem}.sqlite"
        report = args.out / f"{stem}.report.txt"
        if not database.exists():
            missing.append(situation)
            continue
        runs.append(observe_run(
            database, args.corpus, situation=situation, label=label_for(situation),
            promised_levels=promised.get(situation, ()),
            report=report.read_text(encoding="utf-8") if report.exists() else ""))
    if missing:
        print(f"no database for: {', '.join(missing)}", file=sys.stderr)

    scores = [score_situation(run, labels) for run in runs]

    # Protected is checked in EVERY run, not just the one whose situation the
    # label names. A vaccination record that stays shut under `coursework` and is
    # opened under `dataset-analysis` has still been opened.
    breaches, overmarks = [], set()
    for run in runs:
        breaches.extend(protected_verdict(labels, run.files))
        overmarks.update(over_marked(labels, run.files))

    card = scorecard(runs, scores, labels, breaches, sorted(overmarks),
                     corpus_files=corpus_files, seconds=time.monotonic() - started)
    # Two measurements that answer questions the scorecard cannot: whether the
    # situation changes anything the product concludes, and whether the detector
    # was starved or lacks the word. Appended rather than folded in, because
    # each is an experiment with its own denominators and its own caveats, and
    # a number that needs a paragraph does not belong in a ten-second summary.
    card = "\n\n".join((card,
                         protected_evidence_report(runs, labels),
                         discrimination_report(runs, labels)))
    print()
    print(card)

    (args.out / "scorecard.txt").write_text(card, encoding="utf-8")
    (args.out / "per-file.tsv").write_text(per_file_table(runs, labels), encoding="utf-8")
    if breaches:
        (args.out / "protected-breaches.txt").write_text(
            breach_detail(breaches), encoding="utf-8")
    print(f"\nwritten: {args.out / 'scorecard.txt'}")
    print(f"         {args.out / 'per-file.tsv'}")
    if breaches:
        print(f"         {args.out / 'protected-breaches.txt'}")
    return 1 if breaches else 0


if __name__ == "__main__":
    raise SystemExit(main())
