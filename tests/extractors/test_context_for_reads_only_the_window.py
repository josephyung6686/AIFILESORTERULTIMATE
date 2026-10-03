"""`extractors.shape.context_for` slices only the window it returns.

It used to copy the whole text before and after every reading, which on a
multi-megabyte machine-generated file with half a million readings was most of the
run. The windowed form must be the same three answers for every position."""
import random

from extractors.shape import context_for


def _whole_text_copy(text, start, end, *, window):
    before_available, after_available = text[:start], text[end:]
    before = before_available[-window:] if window else ""
    after = after_available[:window] if window else ""
    return before, after, (len(before) < len(before_available)
                           or len(after) < len(after_available))


def test_the_window_is_the_same_answer_as_the_whole_text_copy():
    chooser = random.Random(20261003)
    for _ in range(20000):
        text = "".join(chooser.choice("ab c\n") for _ in range(chooser.randint(0, 60)))
        start = chooser.randint(-5, len(text) + 5)
        end = chooser.randint(-5, len(text) + 5)
        window = chooser.randint(0, 20)
        assert (context_for(text, start, end, window=window)
                == _whole_text_copy(text, start, end, window=window))


def test_a_window_reaching_the_edges_is_not_truncated():
    assert context_for("abcdef", 2, 4, window=2) == ("ab", "ef", False)
    assert context_for("abcdef", 2, 4, window=1) == ("b", "e", True)
