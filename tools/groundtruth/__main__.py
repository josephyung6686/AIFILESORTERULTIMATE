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
from tools.groundtruth.payload import (                             # noqa: E402
    inspect_database as payload_inspect, render as payload_render,
)
from tools.groundtruth.report import (                              # noqa: E402
    breach_detail, per_file_table, scorecard,
)
from tools.groundtruth.protected_evidence import (                  # noqa: E402
    report as protected_evidence_report,
)
from tools.groundtruth.reuse import (                               # noqa: E402
    ReuseRefused, read_seeded, refuse_unless_seedable, write_provenance,
)
from tools.groundtruth.run import label_for, run_situations         # noqa: E402
from tools.groundtruth.score import (                               # noqa: E402
    over_marked, protected_verdict, score_situation,
)
from tools.groundtruth.shadow import shadow_block                   # noqa: E402


def _promised_levels() -> dict[str, tuple[str, ...]]:
    sys.path.insert(0, str(_ROOT / "src"))
    from cli import load_shipped_catalogue, read_packaged_library_file
    from production import shipped_situations

    catalogue = load_shipped_catalogue(read_packaged_library_file)
    return {row.name: tuple(row.folder_levels) for row in shipped_situations(catalogue)}


def _seeding(result, asked_for) -> str:
    """What the seeding did to one run, or nothing at all if it was not asked for.

    Three numbers rather than one, because "reused 172" alone cannot be told from a
    run that silently dropped every file. Seeded is what it was handed, reused is
    what it therefore did not ask, and called is what it paid for anyway.

    Printed on the strength of the FLAG and never of the numbers: `seeded 0, reused
    0` is the most important line this can print -- a directory that answered
    nothing -- and a version that fell silent on three zeros would hide it.
    """
    if asked_for is None:
        return ""
    left = f", {result.skipped} not in this corpus" if result.skipped else ""
    return (f"  seeded {result.seeded}{left}, reused {result.reused}, "
            f"called {result.calls}")


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
        "--reuse-answers-from", type=Path, default=None, metavar="DIR",
        help="seed each fresh run with the MODEL ANSWERS of the run of the same "
             "situation in DIR, so a rerun after a code change does not buy "
             "again what it already paid for (`104` R-123). Five tables are "
             "copied and no others: the four a reuse is decided from -- the call "
             "identity, the dossier it reached, the response and the verdicts -- "
             "and the supersession rows that explain a superseded verdict, when "
             "both of its verdicts travel. It SCANS the corpus into the fresh "
             "database first, with the product's own scan, because R-109's key "
             "carries the file id and that id is minted per database: the scan is "
             "what tells this run's name for a file from the last one's. The run "
             "then scans again and finds those rows unchanged. Keyed by R-109's "
             "identity, whose dimensions include the file's content hash, the "
             "prompt fingerprint, the model and the policy: a file, prompt, model "
             "or policy that moved is a different key and is asked again, and so "
             "is a file that was renamed or is no longer here. Nothing "
             "about placement, structural answers, consent or plan versions is "
             "copied, because keeping those out is why the database is fresh. "
             "The three-run median is a measurement of the MODEL's variance and "
             "must not use this. Refused, before anything runs, if DIR is "
             "missing, if a situation has no database there, or if that "
             "database's llm_* schema is not this checkout's.")
    parser.add_argument(
        "--payload", action="store_true",
        help="also report what the model would be SENT: the largest dossier in "
             "bytes and measured tokens, how many are over the stored ceiling, a "
             "whole-document canary scan, and a `blocked` line counting gate "
             "refusals BY REASON beside route withholding (`104` §7, R-46). It "
             "invokes no model and opens no socket; it works on a copy of each "
             "database, because releasing writes.")
    parser.add_argument(
        "--shadow", action="store_true",
        help="also print what the sorting row WOULD be if site C's observed "
             "verdicts were applied. Since Wave 3 a run with a model configured "
             "records the dossier, the response and the validator's verdict at "
             "site C and applies none of it, because the prompt is not ratified "
             "-- so the row above cannot move until the owner ratifies, and the "
             "owner has to decide BEFORE he can see what it would say. This is "
             "that. It applies nothing, invokes no model, opens no socket, and "
             "prints no file content. Works with `--score-only`.")
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
    # BEFORE `--out` is made and long before the first `unlink`. Every refusal
    # this can raise is about the PRIOR directory, and a run that discovered one
    # halfway would already have deleted the database it was refusing to replace.
    if args.reuse_answers_from is not None:
        try:
            refuse_unless_seedable(args.reuse_answers_from, situations,
                                   out_dir=args.out, score_only=args.score_only)
        except ReuseRefused as refused:
            print(refused, file=sys.stderr)
            return 2
    promised = _promised_levels()
    args.out.mkdir(parents=True, exist_ok=True)
    corpus_files = sum(1 for p in args.corpus.rglob("*") if p.is_file())

    started = time.monotonic()
    if args.score_only:
        print(f"re-scoring {len(situations)} databases in {args.out}")
    else:
        print(f"running {len(situations)} situations over {corpus_files} files, "
              f"{args.workers} at a time. Each run reads the whole corpus.")
        if args.reuse_answers_from is not None:
            # What the seeding DOES, never what it will save. A run that promised
            # a saving on the line above and printed `reused 0` on the line below
            # would be telling a person their key matched when it did not, and
            # which questions were found is the only honest form of the claim.
            print(f"seeding each run's answers from {args.reuse_answers_from}. "
                  f"Each run's database is scanned first, so this run's name for "
                  f"a file is known before a question is looked up under R-109's "
                  f"call identity; `reused` on each line below is how many were "
                  f"found there and `called` is this run's own spend. The "
                  f"scorecard's MODEL line splits every count into fresh and "
                  f"reused, and names the seeded rows beneath it.")
        if args.enable_cloud:
            print(f"!! SENDING TO THE CLOUD MODEL: {len(situations)} runs over "
                  f"{corpus_files} files each. This spends money.", flush=True)
        # Written on every run that runs something, and BEFORE the runs, so a
        # crash halfway still leaves the directory saying what produced what is in
        # it. The product's database records no commit, so without this a
        # directory of databases cannot say what code wrote it -- and the run that
        # needs to know is the next one, which is why it is not written only when
        # `--reuse-answers-from` is passed.
        write_provenance(args.out)
        results = run_situations(
            args.corpus, situations, args.out, workers=args.workers,
            load_ceiling=args.load_ceiling, force=args.force,
            cloud=args.enable_cloud,
            reuse_answers_from=args.reuse_answers_from,
            on_done=lambda r: print(f"  {r.seconds / 60:5.1f} min  exit {r.exit_code}  "
                                    f"{r.situation}"
                                    f"{_seeding(r, args.reuse_answers_from)}",
                                    flush=True))
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
        # Read from the out directory rather than carried from `results`, so
        # `--score-only` over a seeded run months later still knows which rows
        # nobody paid for, and where they came from. `104` R-123.
        seeded_rows, seeded_from = read_seeded(args.out, situation)
        runs.append(observe_run(
            database, args.corpus, situation=situation, label=label_for(situation),
            promised_levels=promised.get(situation, ()),
            seeded=seeded_rows, seeded_from=seeded_from,
            report=report.read_text(encoding="utf-8") if report.exists() else ""))
    if missing:
        print(f"no database for: {', '.join(missing)}", file=sys.stderr)

    scores = [score_situation(run, labels) for run in runs]

    # Protected is checked in EVERY run, not just the one whose situation the
    # label names. A vaccination record that stayed on this machine under
    # `coursework` and was released to a cloud model under `dataset-analysis` has
    # still been released, and the run that did it is not the run being scored.
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
    # `104` §7 Phase 1 step 6, made readable BEFORE the decision it informs. The
    # placement row above cannot move while site C's prompt is unratified, because
    # `_observed_only` rewrites every verdict to an abstention -- so the owner is
    # asked to ratify text whose effect the scoreboard cannot show him. This block
    # is beside the real one and never instead of it, for the reason the payload
    # block is appended rather than folded in: it answers a different question with
    # a different provenance, and a number that needs a paragraph does not belong
    # in the ten-second summary.
    shadow_runs: tuple = ()
    shadow_sources: dict[str, str] = {}
    if args.shadow:
        block, shadow_runs, shadow_sources = shadow_block(
            runs, scores, labels, args.out, args.corpus)
        card = "\n\n".join((card, block))
    # `104` §7 "Instruments": the scoreboard stays the scoreboard, and payload
    # inspection is appended to it. OFF by default and asked for by name, for the
    # reason `--enable-cloud` is: it rebuilds every file's dossier through the real
    # gate, which is a second pass over the corpus's evidence, and it writes -- to a
    # COPY of each database, never to the run's own, because `Gate.release` appends
    # an audit record and mints a release before it returns.
    if args.payload:
        blocks = []
        for situation in situations:
            database = args.out / f"{situation.replace('.', '_')}.sqlite"
            if not database.exists():
                continue
            blocks.append(f"[{situation}]\n" + payload_render(payload_inspect(
                database, args.corpus, situation=situation)))
        if blocks:
            card = "\n\n".join((card, *blocks))
    print()
    print(card)

    (args.out / "scorecard.txt").write_text(card, encoding="utf-8")
    (args.out / "per-file.tsv").write_text(
        per_file_table(runs, labels, shadow_runs, shadow_sources), encoding="utf-8")
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
