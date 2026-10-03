"""Serve the onboarding screens and write the answers file they produce.

The page is the product onboarding UI. A finished snapshot is stored with
`prepare_engine_scan`, which writes the existing answers file and does not
start a scan. Opening the folders is still `database-agent FOLDER --answers FILE`.
"""
from __future__ import annotations

import argparse
import json
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from onboarding.snapshot import ScanRefused, prepare_engine_scan

_UI = Path(__file__).resolve().parent / "ui"
_MAX_BODY = 256_000


class _Handler(SimpleHTTPRequestHandler):
    answers_path: Path

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_POST(self) -> None:  # noqa: N802
        if self.path.split("?", 1)[0] != "/answers":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length") or "0")
        if length <= 0 or length > _MAX_BODY:
            self._json(400, {"ok": False, "error": "The snapshot could not be read."})
            return
        try:
            snapshot = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            self._json(400, {"ok": False, "error": "The snapshot could not be read."})
            return
        try:
            prepare_engine_scan(snapshot, self.answers_path)
        except ScanRefused as refused:
            self._json(409, {"ok": False, "error": str(refused)})
            return
        print(f"Answers file: {self.answers_path}", file=sys.stderr)
        self._json(200, {"ok": True})

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        # The snapshot itself is not logged. Request lines stay off stdout.
        return


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m onboarding.ui_app")
    parser.add_argument(
        "--write", type=Path, required=True,
        help="where to write the answers file the scan already reads")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    if not (_UI / "index.html").is_file():
        print("Onboarding UI is not built. Run python3 src/onboarding/ui/build.py.",
              file=sys.stderr)
        return 2
    _Handler.answers_path = args.write.expanduser().resolve()
    handler = partial(_Handler, directory=str(_UI))
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"File companion onboarding: http://{args.host}:{args.port}/", file=sys.stderr)
    print("Nothing is scanned from this page.", file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
