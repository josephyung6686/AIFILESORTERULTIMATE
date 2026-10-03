"""No developer text reaches the person: database paths, model ids, flags,
internal codes, sums, or the model's own Citations line."""
from __future__ import annotations

import io

from assistant import events as ev
from assistant.session import Session, scrub_developer_text
from assistant.terminal import TerminalRenderer, run_terminal


def test_a_model_reply_is_scrubbed(conn):
    out = []
    reply = ("I used deepseek-chat for this.\n"
             "The index is at /Users/me/.graph-agent/database-agent.sqlite\n"
             "Run it with --stop-after tree to see the plan.\n"
             "That is 0 + 0 + 500 + 12 = 512 files.\n"
             "Reason: low_confidence_abstain.\n"
             "Your essay is in Documents.\n"
             "No citations needed — nothing new was looked up.\n"
             "**Citations:** abc123")
    Session(conn, provider_turn=lambda **k: {"role": "assistant",
                                             "content": reply},
            emit=out.append).say("hi")
    said = [e.text for e in out if isinstance(e, ev.Message)][-1]
    for bad in ("deepseek-chat", ".sqlite", "--stop-after", "0 + 0",
                "low_confidence_abstain", "Citations"):
        assert bad not in said
    assert "Your essay is in Documents." in said


def test_a_file_name_with_underscores_and_dates_stay():
    assert "my_cv_2024.pdf" in scrub_developer_text("Open my_cv_2024.pdf now.")
    line = "Screenshot 2024-05-10 at 11.08.35 PM.png is on 5/10/2024."
    assert scrub_developer_text(line) == line


def test_progress_lines_are_scrubbed(conn):
    out = []
    s = Session(conn, provider_turn=None, emit=out.append)
    s.emit(ev.Progress(stage="organise",
                       line="writing /tmp/x/database-agent.sqlite --freeze"))
    assert ".sqlite" not in out[-1].line and "--freeze" not in out[-1].line


def test_no_indexed_zero_before_a_folder_is_chosen(conn):
    screen = io.StringIO()
    TerminalRenderer(screen)(ev.Counts(0, 0, 0, 0, 0))
    assert "Indexed 0" not in screen.getvalue()
