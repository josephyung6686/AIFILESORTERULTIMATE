"""Opt-in timings for one scan. Off unless a run arms it.

Nothing here runs on the ordinary path except the callers' one check for an
armed profile. No trace is installed, no per-file record is kept, and
`Connection.execute` is left as SQLite's own until `arm_scan_profile`.
"""
from __future__ import annotations

import csv
import math
import sqlite3
import sys
import time
from contextlib import contextmanager
from pathlib import Path, PurePath

#: The WAL-reset bug fixed in SQLite 3.51.3. Reported, never upgraded here.
_WAL_RESET_FIX = (3, 51, 3)

#: SQL phase for the parent's read of one file. Named here, not in
#: `orchestrator`, which does not spell P5's stage vocabulary.
PHASE_FILE_READ = "extraction"

_ACTIVE: "ScanProfile | None" = None

_PREFIX_CUTS = (
    " where ", " values ", " set ", " order by ", " group by ",
    " limit ", " returning ",
)

#: Parent-thread stages. `extraction_work` and `db_calls` are called out in the
#: report because they are not slices of that wall clock.
_STAGE_NOTES = {
    "extraction_work": (
        "Sum of time inside the extraction workers. Workers run in parallel, "
        "so this can be longer than the wall clock."
    ),
    "extraction_pool_blocked": (
        "Time the main thread spent blocked in pool.result, waiting for a "
        "file's extraction."
    ),
    "extraction_pool_join": (
        "Time the main thread spent in pool.close, waiting for workers to stop."
    ),
    "db_calls": (
        "Time inside SQLite execute calls. This sits inside the other stages; "
        "it is not a separate slice of the wall clock."
    ),
    "db_writes": (
        "Main-thread time recording walked files, with hashing subtracted, "
        "plus disappearance reconciliation."
    ),
}


def active_scan_profile() -> "ScanProfile | None":
    return _ACTIVE


def statement_prefix(sql: str) -> str:
    """The stable head of a statement, so the same query groups together.

    Whitespace is collapsed and the tail from WHERE / VALUES / SET on is
    dropped. A stack walk per execute would cost more than the statements
    being counted, so the group is the text, not the caller.
    """
    compact = " ".join(sql.split())
    if not compact:
        return ""
    lowered = compact.lower()
    cut = len(compact)
    for marker in _PREFIX_CUTS:
        found = lowered.find(marker)
        if found != -1:
            cut = min(cut, found)
    head = compact[:cut].strip()
    if len(head) > 180:
        head = head[:180].rstrip()
    return head or compact[:80]


def describe_reader(reader) -> str:
    """Which reader a callable is, in words a report can print."""
    if reader is None:
        return "none"
    module = getattr(reader, "__module__", "") or ""
    qualname = getattr(reader, "__qualname__", "") or ""
    if "pdf_pdfium" in module or "pdfium_reader" in qualname:
        return "pdfium text layer (readers.pdf_pdfium.pdfium_reader)"
    if "pdf_pdfminer" in module or "pdfminer" in qualname:
        return "pdfminer text layer (readers.pdf_pdfminer.pdfminer_reader)"
    if "ocr_vision" in module or "vision_ocr" in qualname:
        return "ocr vision (readers.ocr_vision.vision_ocr)"
    if "doc_cocoa" in module or "cocoa_doc" in qualname:
        return "cocoa (readers.doc_cocoa.cocoa_doc_reader)"
    label = f"{module}.{qualname}".strip(".")
    return label or "unknown"


def _percentile(values: list[float], percent: float) -> float | None:
    """Nearest-rank percentile. One observation is that observation."""
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = math.ceil(percent / 100.0 * len(ordered))
    rank = min(max(rank, 1), len(ordered))
    return ordered[rank - 1]


def _sqlite_below_wal_fix(version: str) -> bool:
    parts = []
    for piece in version.split("."):
        digits = ""
        for character in piece:
            if character.isdigit():
                digits += character
            else:
                break
        if not digits:
            break
        parts.append(int(digits))
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3]) < _WAL_RESET_FIX


class ScanProfile:
    """One armed run. Create it through `arm_scan_profile`."""

    def __init__(self) -> None:
        self.t0 = time.perf_counter()
        self.stages: dict[str, float] = {}
        self.files: dict[str, dict] = {}
        self._by_id: dict[str, str] = {}
        self._reader_samples: dict[str, list[float]] = {}
        self._sql_counts: dict[str, dict[str, int]] = {}
        self._sql_seconds: dict[str, float] = {}
        self._commits: dict[str, int] = {}
        self._executes: dict[str, int] = {}
        self.phase_name = "unscoped"
        self._phase_stack: list[str] = []
        self.pool_blocked = 0.0
        self.worker_work = 0.0
        self.pool_wait_beyond = 0.0
        self.pdf_reader = "not recorded"
        self.ocr_engine = "not recorded"
        self._conn = None
        self._originals: dict[str, object] = {}

    def elapsed(self) -> float:
        return time.perf_counter() - self.t0

    def push_phase(self, name: str) -> None:
        self._phase_stack.append(self.phase_name)
        self.phase_name = name

    def pop_phase(self) -> None:
        self.phase_name = self._phase_stack.pop() if self._phase_stack else "unscoped"

    @contextmanager
    def phase(self, name: str):
        self.push_phase(name)
        try:
            yield
        finally:
            self.pop_phase()

    def add_time(self, stage: str, seconds: float) -> None:
        self.stages[stage] = self.stages.get(stage, 0.0) + seconds

    def stages_seconds(self, stage: str) -> float:
        return self.stages.get(stage, 0.0)

    def _file(self, path: str) -> dict:
        record = self.files.get(path)
        if record is None:
            record = {
                "path": path,
                "extension": "",
                "size": None,
                "file_id": None,
                "hash_s": 0.0,
                "extract_work_s": 0.0,
                "pool_blocked_s": 0.0,
                "explain_s": 0.0,
                "readers": [],
            }
            self.files[path] = record
        return record

    def note_file(self, *, path: str, extension: str, size: int | None) -> None:
        record = self._file(path)
        record["extension"] = extension or "(none)"
        record["size"] = size

    def bind(self, path: str, file_id: str) -> None:
        record = self._file(path)
        record["file_id"] = file_id
        self._by_id[file_id] = path

    def note_hash(self, path, seconds: float) -> None:
        self.add_time("hash", seconds)
        record = self._file(str(path))
        record["hash_s"] += seconds
        if not record["extension"]:
            suffix = PurePath(str(path)).suffix.lower()
            record["extension"] = suffix or "(none)"

    def note_extraction(self, *, path: str, extension: str, size: int | None,
                        blocked_s: float, work_s: float, ocr_s: float,
                        readers: tuple[str, ...]) -> None:
        self.add_time("extraction_pool_blocked", blocked_s)
        self.add_time("extraction_work", work_s)
        self.pool_blocked += blocked_s
        self.worker_work += work_s
        self.pool_wait_beyond += max(0.0, blocked_s - work_s)
        record = self._file(path)
        record["extension"] = extension or record["extension"] or "(none)"
        if size is not None:
            record["size"] = size
        record["pool_blocked_s"] += blocked_s
        record["extract_work_s"] += work_s
        if readers:
            record["readers"] = list(readers)
        native = [label for label in readers if "ocr" not in label.lower()]
        ocr = [label for label in readers if "ocr" in label.lower()]
        if ocr and native:
            ocr_part = min(work_s, max(0.0, ocr_s))
            native_part = max(0.0, work_s - ocr_part)
            for label in native:
                self._reader_samples.setdefault(label, []).append(native_part)
            for label in ocr:
                self._reader_samples.setdefault(label, []).append(ocr_part)
        else:
            for label in readers:
                self._reader_samples.setdefault(label, []).append(work_s)

    def note_explain(self, *, file_id: str, seconds: float,
                     path: str | None = None) -> None:
        self.add_time("recognise_explain", seconds)
        resolved = path or self._by_id.get(file_id) or f"file_id:{file_id}"
        record = self._file(resolved)
        record["file_id"] = file_id
        record["explain_s"] += seconds
        self._by_id[file_id] = resolved

    def note_production_readers(self, *, read_pdf, ocr_engine) -> None:
        self.pdf_reader = describe_reader(read_pdf)
        self.ocr_engine = describe_reader(ocr_engine)

    def _note_sql(self, sql: str, seconds: float, n: int = 1) -> None:
        phase = self.phase_name
        prefix = statement_prefix(sql)
        bucket = self._sql_counts.setdefault(phase, {})
        bucket[prefix] = bucket.get(prefix, 0) + n
        self._executes[phase] = self._executes.get(phase, 0) + n
        self._sql_seconds[phase] = self._sql_seconds.get(phase, 0.0) + seconds
        self.add_time("db_calls", seconds)
        if prefix.upper().startswith("COMMIT"):
            self._commits[phase] = self._commits.get(phase, 0) + n

    def sql_phase(self, phase: str) -> dict:
        return {
            "executes": self._executes.get(phase, 0),
            "commits": self._commits.get(phase, 0),
            "seconds": self._sql_seconds.get(phase, 0.0),
            "by_prefix": dict(self._sql_counts.get(phase, {})),
        }

    def install(self, conn: sqlite3.Connection) -> None:
        """Count and time this connection's statements. Call once."""
        self._conn = conn
        raw_execute = conn.execute
        raw_many = conn.executemany
        raw_script = conn.executescript
        self._originals = {
            "execute": raw_execute,
            "executemany": raw_many,
            "executescript": raw_script,
        }

        def execute(sql, parameters=(), /):
            started = time.perf_counter()
            try:
                return raw_execute(sql, parameters)
            finally:
                self._note_sql(sql, time.perf_counter() - started)

        def executemany(sql, seq, /):
            started = time.perf_counter()
            try:
                return raw_many(sql, seq)
            finally:
                count = len(seq) if hasattr(seq, "__len__") else 1
                self._note_sql(sql, time.perf_counter() - started, count)

        def executescript(sql, /):
            started = time.perf_counter()
            try:
                return raw_script(sql)
            finally:
                self._note_sql(sql, time.perf_counter() - started)

        conn.execute = execute
        conn.executemany = executemany
        conn.executescript = executescript

    def disarm(self) -> None:
        global _ACTIVE
        conn = self._conn
        if conn is not None and self._originals:
            conn.execute = self._originals["execute"]
            conn.executemany = self._originals["executemany"]
            conn.executescript = self._originals["executescript"]
        self._originals = {}
        if _ACTIVE is self:
            _ACTIVE = None

    def _own_seconds(self, record: dict) -> float:
        return (record["hash_s"] + record["extract_work_s"]
                + record["explain_s"])

    def by_extension(self) -> dict[str, dict]:
        grouped: dict[str, list[float]] = {}
        for record in self.files.values():
            extension = record["extension"] or "(none)"
            grouped.setdefault(extension, []).append(self._own_seconds(record))
        return {extension: _sample_summary(samples)
                for extension, samples in sorted(grouped.items())}

    def by_reader(self) -> dict[str, dict]:
        return {label: _sample_summary(samples)
                for label, samples in sorted(self._reader_samples.items())}

    def slowest(self, limit: int = 25) -> list[dict]:
        ranked = []
        for record in self.files.values():
            total = self._own_seconds(record) + record["pool_blocked_s"]
            ranked.append((total, record))
        ranked.sort(key=lambda item: (-item[0], item[1]["path"]))
        rows = []
        for total, record in ranked[:limit]:
            rows.append({
                "path": record["path"],
                "extension": record["extension"] or "(none)",
                "size": record["size"],
                "seconds": total,
                "hash_s": record["hash_s"],
                "extract_work_s": record["extract_work_s"],
                "pool_blocked_s": record["pool_blocked_s"],
                "explain_s": record["explain_s"],
                "readers": list(record["readers"]),
            })
        return rows

    def report(self, *, wall_s: float) -> dict:
        version = sqlite3.sqlite_version
        below = _sqlite_below_wal_fix(version)
        stages = {}
        for name, seconds in sorted(self.stages.items()):
            stages[name] = {
                "seconds": seconds,
                "share_of_wall": (seconds / wall_s) if wall_s else 0.0,
            }
            note = _STAGE_NOTES.get(name)
            if note:
                stages[name]["note"] = note
        sql_phases = {
            phase: self.sql_phase(phase)
            for phase in sorted(set(self._executes) | set(self._commits)
                                | set(self._sql_counts))
        }
        return {
            "wall_seconds": wall_s,
            "platform": sys.platform,
            "measured_on": sys.platform,
            "sqlite_version": version,
            "sqlite_below_wal_reset_fix": below,
            "sqlite_note": (
                f"SQLite {version} is below 3.51.3, the release that fixes "
                "the WAL-reset bug. This run did not upgrade it."
                if below else
                f"SQLite {version} includes the 3.51.3 WAL-reset fix."
            ),
            "pdf_reader": {
                "production": self.pdf_reader,
                "ocr_engine": self.ocr_engine,
                "note": (
                    "production read_pdf is whatever extraction_context wired. "
                    "Per-file readers below are what each extraction actually "
                    "called. On Linux, OCR and Cocoa are not wired."
                ),
            },
            "stages": stages,
            "pool": {
                "parent_blocked_seconds": self.pool_blocked,
                "worker_work_seconds": self.worker_work,
                "parent_blocked_beyond_file_work_seconds": self.pool_wait_beyond,
                "note": (
                    "parent_blocked is time the main thread waited inside "
                    "pool.result. worker_work is time inside perform, summed "
                    "across workers. beyond_file_work is blocked minus that "
                    "file's own work, floored at zero, summed."
                ),
            },
            "by_extension": self.by_extension(),
            "by_reader": self.by_reader(),
            "slowest_files": self.slowest(25),
            "sql": {
                "executes": sum(self._executes.values()),
                "commits": sum(self._commits.values()),
                "by_phase": sql_phases,
            },
        }

    def write(self, database: Path, wall_s: float | None = None) -> dict[str, Path]:
        """JSON and CSV beside the plan database. Paths stay in these files."""
        database = Path(database)
        wall = self.elapsed() if wall_s is None else wall_s
        payload = self.report(wall_s=wall)
        json_path = database.parent / f"{database.stem}.scan-profile.json"
        csv_path = database.parent / f"{database.stem}.scan-profile.csv"
        import json
        json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["section", "key", "seconds", "share_of_wall",
                             "count", "p50", "p95", "max", "extension", "size",
                             "path", "phase", "commits", "executes"])
            for name, stage in payload["stages"].items():
                writer.writerow(["stage", name, stage["seconds"],
                                 stage["share_of_wall"], "", "", "", "", "",
                                 "", "", "", "", ""])
            for extension, summary in payload["by_extension"].items():
                writer.writerow(["extension", extension, summary["seconds"], "",
                                 summary["files"], summary["p50"], summary["p95"],
                                 summary["max"], extension, "", "", "", "", ""])
            for label, summary in payload["by_reader"].items():
                writer.writerow(["reader", label, summary["seconds"], "",
                                 summary["files"], summary["p50"], summary["p95"],
                                 summary["max"], "", "", "", "", "", ""])
            for row in payload["slowest_files"]:
                writer.writerow(["slowest", "", row["seconds"], "", "", "", "",
                                 "", row["extension"], row["size"], row["path"],
                                 "", "", ""])
            for phase, bucket in payload["sql"]["by_phase"].items():
                for prefix, count in sorted(bucket["by_prefix"].items()):
                    writer.writerow(["sql", prefix, bucket["seconds"], "", count,
                                     "", "", "", "", "", "", phase,
                                     bucket["commits"], bucket["executes"]])
        return {"json": json_path, "csv": csv_path}


def _sample_summary(samples: list[float]) -> dict:
    return {
        "files": len(samples),
        "seconds": sum(samples),
        "p50": _percentile(samples, 50),
        "p95": _percentile(samples, 95),
        "max": max(samples) if samples else None,
    }


def arm_scan_profile(conn: sqlite3.Connection) -> ScanProfile:
    """Arm `conn` and make this the active profile. One run at a time."""
    global _ACTIVE
    profile = ScanProfile()
    profile.install(conn)
    _ACTIVE = profile
    return profile


def annotate_extraction(outcome, readers, work_s: float):
    """Attach worker time and reader names. The database row is unchanged."""
    labels: list[str] = []
    dispatched = outcome.dispatched
    if dispatched is not None:
        for result in dispatched.results:
            run = result.run
            tier = run.get("analysis_tier") or ""
            name = run.get("extractor_name") or ""
            if tier == "ocr" or name.startswith("ocr"):
                engine = getattr(readers, "ocr_engine", None)
                labels.append(describe_reader(engine) if engine is not None
                              else "ocr (no engine)")
            elif name == "pdf.text" or name.startswith("pdf"):
                labels.append(describe_reader(getattr(readers, "read_pdf", None)))
            elif "cocoa" in name or name.startswith("doc"):
                labels.append(describe_reader(
                    getattr(readers, "read_text_document", None)))
            else:
                labels.append(name or tier or "unknown")
    return type(outcome)(outcome.kind, outcome.dispatched, outcome.message,
                         work_s, tuple(labels))
