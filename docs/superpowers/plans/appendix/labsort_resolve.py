"""Context resolution: date, instrument, experiment.

The schema is raw/{YYYY-MM-DD}/{instrument}/. In the Nutrigene tree only 3 of 53
fully-routable files carry a resolvable date in their own filename; the other 50
inherit it from a parent folder named `0731` (MMDD, no year) or `New Folder-copy-copy`
(no date at all). So this stage gates nearly every automatic route and needs to be a
named component, not a footnote in the rule engine.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

from .model import DateEvidence, ExperimentEvidence, FileRef, InstrumentEvidence

ISO = re.compile(r"(?<!\d)(?P<y>20\d{2})-(?P<m>0[1-9]|1[0-2])-(?P<d>0[1-9]|[12]\d|3[01])(?!\d)")
YYYYMMDD = re.compile(r"^(?P<y>20\d{2})(?P<m>0[1-9]|1[0-2])(?P<d>0[1-9]|[12]\d|3[01])$")
MMDD = re.compile(r"^(?P<m>0[1-9]|1[0-2])(?P<d>0[1-9]|[12]\d|3[01])$")


def _safe(y: int, m: int, d: int) -> Optional[date]:
    try:
        return date(y, m, d)
    except ValueError:
        return None


def _mtime_date(ref: FileRef) -> date:
    return datetime.fromtimestamp(ref.mtime_ns / 1e9, tz=timezone.utc).date()


def infer_year(month: int, day: int, not_after: date) -> tuple[Optional[date], bool]:
    """Resolve an MMDD folder to a real date.

    Capture always precedes the copy that set mtime, so the true year is the
    largest Y for which date(Y, month, day) <= not_after. Checking Y and Y-1 covers
    the year boundary (a 1231 folder copied on 3 January).

    Returns (value, inferred_year). `inferred_year=True` is carried all the way to
    the UI so a wrong guess is visible rather than silent.
    """
    for y in (not_after.year, not_after.year - 1):
        cand = _safe(y, month, day)
        if cand is not None and cand <= not_after:
            return cand, True
    return None, True


class DateResolver:
    """Evidence ladder, strongest first. Stops at the first hit."""

    def resolve(self, ref: FileRef, *, siblings: Iterable[FileRef] = ()) -> Optional[DateEvidence]:
        if (ev := self._from_name(ref.path.name, "filename_iso")) is not None:
            return ev
        if (ev := self._from_siblings(ref, siblings)) is not None:
            return ev
        if (ev := self._from_folders(ref)) is not None:
            return ev
        return DateEvidence(value=_mtime_date(ref), source="mtime")

    def _from_name(self, name: str, source) -> Optional[DateEvidence]:
        if (m := ISO.search(name)) is None:
            return None
        v = _safe(int(m["y"]), int(m["m"]), int(m["d"]))
        return None if v is None else DateEvidence(value=v, source=source)

    def _from_siblings(self, ref: FileRef, siblings: Iterable[FileRef]) -> Optional[DateEvidence]:
        """`New Folder-copy-copy` carries no date; the Leica captures inside it do.

        Only accepted when every dated sibling agrees. A directory holding two
        different capture days is not a day folder, and guessing one would file
        half the images under the wrong date.
        """
        found: set[date] = set()
        for sib in siblings:
            if (ev := self._from_name(sib.path.name, "sibling_filename")) is not None:
                found.add(ev.value)
        if len(found) == 1:
            return DateEvidence(value=found.pop(), source="sibling_filename")
        return None

    def _from_folders(self, ref: FileRef) -> Optional[DateEvidence]:
        """Nearest ancestor wins: raw/0731/sub/x.fcs takes 0731, not a higher folder."""
        not_after = _mtime_date(ref)
        for part in reversed(ref.path.parent.parts):
            if (m := YYYYMMDD.match(part)) is not None:
                v = _safe(int(m["y"]), int(m["m"]), int(m["d"]))
                if v is not None:
                    return DateEvidence(value=v, source="folder_iso")
            if (m := MMDD.match(part)) is not None:
                v, inferred = infer_year(int(m["m"]), int(m["d"]), not_after)
                if v is not None:
                    return DateEvidence(value=v, source="folder_mmdd", inferred_year=inferred)
            if (ev := self._from_name(part, "folder_iso")) is not None:
                return ev
        return None


EVOS = re.compile(r"^QS_\d{4}\.jpe?g$", re.I)
LEICA = re.compile(r"^Leica_", re.I)
PLATE = re.compile(r"^Endpoint Abs @ \d+ ", re.I)
FLOW_EXT = {".fcs", ".xit"}
FLOW_NAMES = {"expsummaryforapi.xml"}


class InstrumentResolver:
    """Instrument is resolved per group, never per directory.

    A single day folder in the Nutrigene tree mixes EVOS and Leica output, so
    picking one instrument for a whole directory would misfile half of it.
    """

    def resolve(self, ref: FileRef) -> Optional[InstrumentEvidence]:
        name, suffix = ref.path.name, ref.path.suffix.lower()
        if LEICA.match(name):
            return InstrumentEvidence("leica", "microscopy/leica", "filename_prefix")
        if EVOS.match(name):
            return InstrumentEvidence("evos", "microscopy/evos", "filename_prefix")
        if PLATE.match(name):
            return InstrumentEvidence("plate_reader", "plate-reader", "filename_prefix")
        if suffix in FLOW_EXT or name.lower() in FLOW_NAMES:
            return InstrumentEvidence("cytoflex", "flow", "extension")
        return None


EXP_DIR = re.compile(r"^Exp[_-]?(?P<stamp>\d{8})[_-](?P<n>\d+)$", re.I)


class ExperimentResolver:
    """Binds the third unbound placeholder in the audit's destination templates.

    `patterns.yaml` routes flow files to `raw/{date}/flow/{experiment}/` but
    captures no `experiment` field anywhere; `cyt_summary` captures no fields at
    all. Left unresolved, every flow destination is a template that cannot render.

    Ladder: a sibling `.xit` names the experiment; failing that, an ancestor
    directory shaped like `Exp_20260806_1`; failing that, the segment is omitted
    and the group lands in `raw/{date}/flow/` rather than being blocked.
    """

    def resolve(
        self, ref: FileRef, *, siblings: Iterable[FileRef] = ()
    ) -> Optional[ExperimentEvidence]:
        stems = {s.path.stem for s in siblings if s.path.suffix.lower() == ".xit"}
        if ref.path.suffix.lower() == ".xit":
            stems.add(ref.path.stem)
        if len(stems) == 1:
            return ExperimentEvidence(stems.pop(), "sibling_xit")
        for part in reversed(ref.path.parent.parts):
            if EXP_DIR.match(part):
                return ExperimentEvidence(part, "folder_name")
        return None
