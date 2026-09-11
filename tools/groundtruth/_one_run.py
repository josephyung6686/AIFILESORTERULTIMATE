"""One `--situation` run of the product, in its own process.

Its own process for two reasons. `cli.main` is the composition root and building
it twice in one interpreter would let one run's imports and caches reach the
next; and a run that dies takes only itself down, which matters when several are
in flight at once.

Usage: python3 -m tools.groundtruth._one_run CORPUS SITUATION LABEL DATABASE REPORT [cloud]

The last argument is the word `cloud` or nothing. Sending is OFF unless it is
there, and the credential is unreadable unless it is there: turning the model on
is one explicit word in one place, never a default and never inherited.

`104` R-175: THIS RUNNER SETS A PER-FILE WALL-CLOCK CEILING AND A PERSON'S OWN RUN
DOES NOT. The difference is who is watching. A person scanning their folder is at
the screen and can stop a run that has stalled; this process walks 199 files for
nine hours with nobody there, and on 10 Sep 2026 r19 spent twenty-six of its last
minutes on one call to a server sitting at 0.4% CPU before the lead stopped it by
hand (§18.22). The ceiling is what turns that into one recorded failure and 198
files still measured.
"""
from __future__ import annotations

import io
import os
import sys
from pathlib import Path


#: Where the scoreboard is told the encoder weights are. Machine state and not
#: project state, so the harness is told where they are rather than knowing.
SEMANTIC_MODEL_ENV = "GRAPH_AGENT_SEMANTIC_MODEL"


def semantic_weights() -> str:
    """The encoder this run recognises with, or `""` when the channel is off.

    **ONE READING OF THE SETTING, AND THAT IS `104` §12.7's WHOLE POINT.** A
    scorecard whose columns do not state the semantic setting is a row nobody can
    reproduce: the same corpus classifies 13 more files with the weights than
    without, and two runs printed side by side look like a regression. The parent
    process records what this line returns beside the databases and the scorecard
    prints it back, so the setting a run WAS GIVEN and the setting a scorecard
    REPORTS are one value read in one place, never the environment read twice at
    two different times.

    Absent means the semantic channel is off and the run is the deterministic one
    -- the same posture `--enable-cloud` takes in `main` below: a capability is
    named or it does not happen.
    """
    return os.environ.get(SEMANTIC_MODEL_ENV, "")


def file_ceiling_seconds(cli) -> float:
    """How long one FILE may hold a scoreboard run. `104` R-175 part b.

    **DERIVED FROM THE DEPLOYMENT'S OWN TWO NUMBERS, and it is not a minute count
    somebody typed.** A number typed here would be a third opinion about how slow
    this machine is, sitting beside the two that already exist, and it would go
    quietly wrong the day either of them moved -- which is the whole class of defect
    `104` calls hardcoding. The two it is built from:

    * `cli.LOCAL_MODEL_TIMEOUT_SECONDS` -- how long ONE local call may take. Since
      R-175 part a that is a deadline over the whole call rather than an idle timer,
      so it is a real bound and not a hope.
    * `cli.PER_FILE_LOCAL_CALL_SITES` -- the local call sites one FILE can be asked
      at within a single pass, read off the code that makes the calls: site G in
      `cli.ask_the_situation` and site A in `model_facts.fact_call_stage`. A tuple
      of sites and not the number two, so the arithmetic follows the wiring.

    The product is the longest a file's turn can honestly take when every call it
    makes runs to its own deadline and none of them is stuck. A file past it is not
    slow; it is a file this run has stopped waiting for.

    **THE LOCAL NUMBER AND NOT THE CLOUD ONE**, on a run whose fact site routes per
    file (`104` §17.13 ruling 3). A file may go to either, the cloud number is the
    smaller of the two, and a ceiling built from it would cut off local files that
    were answering. The ceiling is a bound on the worst honest case, so it takes the
    larger patience.

    **IT IS DELIBERATELY NOT TIGHT.** Too tight and the scoreboard records files as
    failures that the model was busy answering, which is a measurement that lies
    about the product; too loose and a stuck file costs the run its ceiling once
    instead of for ever. Only one of those two errors is recoverable by reading the
    report, so this errs long -- exactly as `LOCAL_MODEL_TIMEOUT_SECONDS` errs long
    for the same asymmetry, in its own words.

    The module is passed in rather than imported, because `cli` is importable only
    after `main` has put `src` on the path.
    """
    return cli.LOCAL_MODEL_TIMEOUT_SECONDS * len(cli.PER_FILE_LOCAL_CALL_SITES)


def main(argv: list[str]) -> int:
    corpus, situation, label, database, report = argv[:5]
    cloud = len(argv) > 5 and argv[5] == "cloud"
    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root / "src"))

    # No run of this harness spends the owner's money by accident. Without the
    # word, the credential is not even readable; with it, this is the ONE place
    # that decides, and the run says so on screen before it sends.
    if not cloud:
        os.environ["GRAPH_AGENT_NO_DOTENV"] = "1"

    import cli

    # The user is imported and not spelled here: `reuse.seed` records a corpus
    # selection under the same name before the run starts, and a selection whose
    # `selected_by` differed from the run's would say two people chose this corpus.
    from tools.groundtruth.reuse import SCOREBOARD_USER

    argv_for_cli = [corpus, "--situation", situation, "--label", label,
                    "--user", SCOREBOARD_USER, "--database", database,
                    # `104` SF-3. A GROUP IS A DRAFT UNTIL SOMEBODY ACCEPTS IT, and
                    # a scoreboard with nobody at the screen would otherwise score a
                    # run that placed nothing: §5.3 builds the top level out of
                    # accepted groups and P11 plans a packet only for a group that
                    # became a branch. So the harness makes the gesture, EXPLICITLY
                    # and through the same flag a person types, rather than the
                    # product making it silently for everyone -- which is the defect
                    # SF-3 names.
                    #
                    # It is defensible here and nowhere else because the LABELS ARE
                    # THE PERSON'S WORD: `labels.py` reads a file the owner wrote by
                    # hand saying where each file belongs, so a run measured against
                    # them is measured against a person's own judgement about this
                    # corpus. What the harness supplies is the ACT, not the opinion.
                    #
                    # The scorecard says so in its own header, because a reader who
                    # cannot tell a scored acceptance from a reviewed one will read
                    # these numbers as a claim about the product's judgement when
                    # they are a claim about its placement.
                    "--accept-groups"]
    model = semantic_weights()
    if model:
        argv_for_cli += ["--semantic-model", model]
    if cloud:
        argv_for_cli.append("--enable-cloud")

    out = io.StringIO()
    try:
        # `104` R-175. A keyword and not a flag: the number is derived from the
        # deployment's own two constants above, so there is nothing for a person to
        # type and nothing they could type that would not be a third opinion.
        code = cli.main(argv_for_cli, out=out,
                        file_ceiling_seconds=file_ceiling_seconds(cli))
    finally:
        Path(report).write_text(out.getvalue(), encoding="utf-8")
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
