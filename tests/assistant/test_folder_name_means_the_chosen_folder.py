""""Desktop" means the folder the person chose, not the real one on the Mac
the model happened to know the path of."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from assistant.engine_tools import check_folder


@pytest.fixture()
def chosen(tmp_path, monkeypatch):
    home = tmp_path / "home"
    desktop = home / "Desktop"
    desktop.mkdir(parents=True)
    monkeypatch.setenv("HOME", str(home))
    return desktop.resolve(), SimpleNamespace(chosen_folders={desktop.resolve()})


@pytest.mark.parametrize("arg", ["Desktop", "my desktop", "the Desktop folder",
                                 "~/Desktop", "/Users/jy/Desktop",
                                 "/Users/someone-else/Desktop"])
def test_desktop_resolves_to_the_chosen_folder(conn, chosen, arg):
    desktop, context = chosen
    path, refusal = check_folder(conn, arg, context, "index")
    assert refusal is None and path == desktop


def test_an_unrelated_name_is_not_guessed_into_the_selection(conn, chosen):
    _, context = chosen
    path, refusal = check_folder(conn, "Photos", context, "index")
    assert path is None and refusal is not None
