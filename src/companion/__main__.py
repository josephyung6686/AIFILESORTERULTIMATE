"""Open File Companion in a Mac window.

    python3 -m companion

That is the window. It does not open index.html in a browser.
"""
from __future__ import annotations

import sys
from pathlib import Path

_UI = Path(__file__).resolve().parent.parent / "onboarding" / "ui"


def default_support(home: Path) -> Path:
    return home / "Library" / "Application Support" / "File Companion"


def main(argv: list[str] | None = None) -> int:
    del argv
    if not (_UI / "index.html").is_file():
        print(
            "Onboarding screens are not built. "
            "Run python3 src/onboarding/ui/build.py.",
            file=sys.stderr,
        )
        return 2
    if sys.platform != "darwin":
        print(
            "File Companion opens a Mac window. This computer is not macOS.",
            file=sys.stderr,
        )
        print("On a Mac, run: python3 -m companion", file=sys.stderr)
        return 2
    from companion.service import CompanionService
    from companion.window import open_mac_window

    home = Path.home()
    support = default_support(home)
    support.mkdir(parents=True, exist_ok=True)
    service = CompanionService(
        home=home,
        answers=support / "answers.json",
        database=support / "plan.sqlite",
    )
    open_mac_window(ui_dir=_UI, service=service)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
