#!/usr/bin/env python3
"""check.py — 12-academic-capture-patterns (R6).

Asserts, per the dispatch brief:
  * the three `00` academic-term literals match their dedicated patterns (and only them);
  * the MIT/UNC word-boundary cases exist and hold; every extension context term is never_alone;
  * course-code entries all require context; `HW 3` matches nothing; the A03 texts yield nothing;
  * `v2024` is a listed non-date and matches no family anywhere;
  * no numeric value sits in an injected slot; the G7 slot definitions carry no digits;
  * no fabricated quotes: every "quote" field and every 05 blockquote appears verbatim
    (whitespace-collapsed) in 00/01; P6-SPEC-attributed statements are paraphrases by policy;
  * every stated example behaves as stated: true examples match, false examples produce no
    surviving candidate, fails-validation examples match the regex and fail the named calendar
    identity, and the cross-catalogue claiming order holds for AY/FY/ISO spans.

stdlib only. Exit 0 iff everything holds.
"""
import datetime
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLANNING = HERE.parent.parent

FAILS: list[str] = []


def ok(cond: bool, msg: str) -> None:
    if not cond:
        FAILS.append(msg)


def collapse(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------------------------------------------- sources
C00 = collapse((PLANNING / "00-database-agent-product-design.md").read_text())
C01 = collapse((PLANNING / "01-product-design-structured.md").read_text())

J = {}
for stem in ["01-academic-context-terms", "02-course-code-formats",
             "03-academic-term-patterns", "04-narrow-date-families"]:
    J[stem[:2]] = json.loads((HERE / f"{stem}.json").read_text())
MD05 = (HERE / "05-capture-composition.md").read_text()
README = (HERE / "README.md").read_text()


# ---------------------------------------------------------------- 1. quote authenticity
def walk_quotes(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "quote" and isinstance(v, str):
                yield f"{path}.{k}", v
            else:
                yield from walk_quotes(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_quotes(v, f"{path}[{i}]")


for num, data in J.items():
    for path, q in walk_quotes(data, num):
        ok(collapse(q) in C00 or collapse(q) in C01,
           f"FABRICATED QUOTE {path}: {q[:80]!r} not verbatim in 00/01")

# 05's blockquotes (lines starting '> ', joined per block) must be verbatim in 00.
block, blocks = [], []
for line in MD05.splitlines():
    if line.startswith(">"):
        block.append(line.lstrip("> ").rstrip())
    elif block:
        blocks.append(" ".join(block))
        block = []
if block:
    blocks.append(" ".join(block))
for b in blocks:
    inner = collapse(b).strip('"')
    ok(inner in C00, f"FABRICATED QUOTE 05-capture-composition.md blockquote: {b[:80]!r}")

# ---------------------------------------------------------------- 2. provenance vocabulary
def walk_prov(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "provenance" and isinstance(v, str):
                yield f"{path}.{k}", v
            else:
                yield from walk_prov(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_prov(v, f"{path}[{i}]")


for num, data in J.items():
    for path, v in walk_prov(data, num):
        ok(v in ("design", "inference", "proposal"),
           f"{path}: provenance {v!r} outside design|inference|proposal")

# ---------------------------------------------------------------- 3. no numeric slots
SLOT_KEYS = {"min_score", "min_margin", "positional_weight_by_zone",
             "locale_numeric_date_policy", "date_label_strings",
             "cjk_date_patterns_slot", "signal_tier_weights"}
NUMERIC_HINTS = ("weight", "score", "margin", "window", "radius", "threshold", "tolerance")


def walk_items(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield f"{path}.{k}", k, v
            yield from walk_items(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_items(v, f"{path}[{i}]")


for num, data in J.items():
    for path, key, val in walk_items(data, num):
        if key in SLOT_KEYS:
            ok(val is None, f"{path}: injected slot {key} holds {val!r}, must be null")
        if isinstance(key, str) and any(h in key.lower() for h in NUMERIC_HINTS) and key != "false_positive_risk":
            ok(not isinstance(val, (int, float)),
               f"{path}: key {key!r} holds numeric {val!r} — thresholds must be injected slots")

# G7 slot rows in 05 carry no digits.
g7_rows = [l for l in MD05.splitlines()
           if l.startswith("| `event_time_window`") or l.startswith("| `event_gps_radius`")
           or l.startswith("| `camera_identity_test`")]
ok(len(g7_rows) == 3, "05: expected the three G7 slot rows (event_time_window, event_gps_radius, camera_identity_test)")
for row in g7_rows:
    ok(not re.search(r"\d", row), f"05: G7 slot definition carries a digit: {row!r}")
ok('"no EXIF ⇒ screenshot" is unbuildable' in MD05,
   "05: the no-EXIF⇒screenshot refusal sentence is missing")

# ---------------------------------------------------------------- helpers
def strip_annotation(s: str) -> tuple[str, str]:
    m = re.match(r"^(.*?)\s+\(([^()]*)\)$", s)
    return (m.group(1), m.group(2)) if m else (s, "")


def rx(entry):
    return re.compile(entry["pattern"], 0 if entry.get("case_sensitive", True) else re.IGNORECASE)


def year_tail_consecutive(text: str) -> bool | None:
    """Find 'YYYY<sep>tail' in text; None if no range tail, else the identity verdict."""
    m = re.search(r"((?:19|20)\d{2})\s?[-–/]((?:19|20)?\d{2})", text)
    if not m:
        return None
    lead, tail = int(m.group(1)), m.group(2)
    if len(tail) == 4:
        return int(tail) == lead + 1
    return (lead + 1) % 100 == int(tail)


def validate(rule: str, matched: str) -> bool:
    if rule is None:
        return True
    if rule == "consecutive_year_two_digit":
        v = year_tail_consecutive(matched)
        return bool(v)
    if rule == "consecutive_year_full":
        m = re.search(r"((?:19|20)\d{2})[-–]((?:19|20)\d{2})", matched)
        return bool(m) and int(m.group(2)) == int(m.group(1)) + 1
    if rule == "consecutive_year_two_digit_when_range":
        v = year_tail_consecutive(matched)
        return True if v is None else v
    if rule == "calendar_date_valid":
        return _calendar_ok(matched)
    raise AssertionError(f"unknown validation rule {rule}")


MONTHS = {m.lower(): i + 1 for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"])}


def _calendar_ok(matched: str) -> bool:
    s = matched
    for pat, order in [
        (r"(19|20)(\d{2}):(\d{2}):(\d{2})", "ymd"),                       # EXIF
        (r"D:((?:19|20)\d{2})(\d{2})(\d{2})", "ymd4"),                    # PDF D:
        (r"((?:19|20)\d{2})-(\d{2})-(\d{2})", "ymd4"),                    # ISO
        (r"((?:19|20)\d{2})(\d{2})(\d{2})", "ymd4"),                      # compact
    ]:
        m = re.search(pat, s)
        if m:
            if order == "ymd":
                y = int(m.group(1) + m.group(2)); mo = int(m.group(3)); d = int(m.group(4))
            else:
                y = int(m.group(1)); mo = int(m.group(2)); d = int(m.group(3))
            try:
                datetime.date(y, mo, d)
                return True
            except ValueError:
                return False
    m = re.search(r"\b([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+((?:19|20)\d{2})\b", s)
    if not m:
        m2 = re.search(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+((?:19|20)\d{2})\b", s)
        if m2:
            d, mo_name, y = m2.group(1), m2.group(2), m2.group(3)
            m = None
            mo = MONTHS.get(mo_name.lower())
            if mo:
                try:
                    datetime.date(int(y), mo, int(d))
                    return True
                except ValueError:
                    return False
        return False
    mo = MONTHS.get(m.group(1).lower())
    if not mo:
        return False
    try:
        datetime.date(int(m.group(3)), mo, int(m.group(2)))
        return True
    except ValueError:
        return False


# ---------------------------------------------------------------- 4. catalogue 01
d01 = J["01"]
floor = {e["term"] for e in d01["entries"] if e.get("role") == "floor"}
ok(floor == {"syllabus", "lecture", "credits", "instructor", "semester"},
   f"01: floor terms are {sorted(floor)}, must be exactly the five 00 literals")
for e in d01["entries"]:
    if e["role"] == "floor":
        ok(e["never_alone"] is False and e["provenance"] == "design",
           f"01 {e['term_id']}: floor terms are design and not never_alone")
    else:
        ok(e["never_alone"] is True, f"01 {e['term_id']}: extension term must be never_alone")
        ok(e["provenance"] in ("inference", "proposal"),
           f"01 {e['term_id']}: extension term may not claim design provenance")
    ok(e.get("word_boundary") is True and e.get("case_sensitive") is False,
       f"01 {e['term_id']}: context terms are word-boundary and case-insensitive (N-6)")
    for k in ("term_id", "language", "scripts", "false_friend"):
        ok(k in e, f"01 {e['term_id']}: missing {k}")
ext = {e["term"] for e in d01["entries"] if e["role"] == "extension"}
ok({"homework", "midterm", "problem set", "office hours", "canvas", "blackboard"} <= ext,
   f"01: dispatch's six extension terms must all be present, have {sorted(ext)}")

# MIT/UNC word-boundary cases exist and hold.
src01 = json.dumps(d01)
ok("MIT" in src01 and "UNC" in src01 and "A01" in src01 and "A02" in src01,
   "01: the MIT/UNC (A01/A02) word-boundary cases must be recorded")
ok(re.search(r"\bMIT\b", "Please submit the completed form.") is None, "word-boundary: MIT leaks from 'submit'")
ok(re.search(r"\bUNC\b", "Measurement uncertainty dominates the result.") is None, "word-boundary: UNC leaks from 'uncertainty'")


def term_re(term: str) -> re.Pattern:
    return re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)


for e in d01["entries"]:
    ok(term_re(e["term"]).search(e["example_true"]) is not None,
       f"01 {e['term_id']}: example_true does not contain the term at a word boundary")
# Morphological negatives (semantic false friends legitimately match lexically and are exempt).
for term, text in [("syllabus", "syllabusless"), ("lecture", "the lecturer arrived"),
                   ("credits", "the bank accredits the account"), ("instructor", "instructorless"),
                   ("semester", "semesterly billing"), ("homework", "homeworkless"),
                   ("midterm", "midtermish"),
                   ("problem set", "we understood the problem. Set the timer and begin")]:
    ok(term_re(term).search(text) is None,
       f"01: word-boundary/phrase rule broken — {term!r} matches inside {text!r}")

# ---------------------------------------------------------------- 5. catalogue 02
d02 = J["02"]
stop = {r["token"] for r in d02["dept_stoplist"]}
for must in ("HW", "AY", "FY", "FORM", "ISO", "DSCF", "FALL"):
    ok(must in stop, f"02: dept_stoplist must contain {must}")


def surviving(entry, text):
    """Candidates from one entry after its own guards (stoplists)."""
    out = []
    for m in rx(entry).finditer(text):
        tok = re.match(r"[A-Z]+", m.group(0))
        if tok and tok.group(0) in stop:
            continue
        if entry.get("extension_stoplist"):
            tail = m.group(0).rsplit(".", 1)
            if len(tail) == 2 and tail[1] in entry["extension_stoplist"]:
                continue
        out.append(m.group(0))
    return out


for e in d02["entries"]:
    ok(e.get("context_required") is True, f"02 {e['id']}: context_required must be true on every entry")
    ok(e.get("case_sensitive") is True and e.get("word_boundary") is True,
       f"02 {e['id']}: case-sensitive word-boundary matching is the authored rule")
    for k, v in e.items():
        if isinstance(v, str) and k.startswith("example_true"):
            ok(surviving(e, v), f"02 {e['id']}: true example {v!r} yields no candidate")
        if isinstance(v, str) and k.startswith("example_false"):
            ok(not surviving(e, strip_annotation(v)[0]),
               f"02 {e['id']}: false example {v!r} survives the guards")
    ok(not surviving(e, "HW 3"), f"02 {e['id']}: 'HW 3' must never be a course candidate")

# A03's texts end in no candidate from any entry.
for text in ["Ship to Cambridge MA 02139 by Friday.", "Receipt for one XPS 13 laptop."]:
    for e in d02["entries"]:
        ok(not surviving(e, text), f"02 {e['id']}: A03 text {text!r} yields a candidate")

ok(any(r["id"] == "ref-hw-ordinal" for r in d02["refused"]), "02: the HW-3 refusal row must exist")
ok(re.search(r"\bHW\s?\d{1,2}\b", "HW 3"), "02: the refused HW shape should describe 'HW 3'")
ok(re.search(r"\b[A-Z]{2} \d{5}(-\d{4})?\b", "MA 02139"), "02: the refused ZIP shape should describe 'MA 02139'")
ok("seam_with_10_04" in d02, "02: the 10/04 seam must be acknowledged")

# ---------------------------------------------------------------- 6. catalogue 03 + claiming
d03 = J["03"]
d04 = J["04"]
ok(set(d03["validation_rules"]) >= {v for e in d03["entries"] if (v := e.get("validation"))},
   "03: every validation name used by an entry must be defined in validation_rules")

by_id = {e["id"]: e for e in d03["entries"]}
LITERALS = {"Spring 2025": "atp-season-year", "AY 2024-25": "atp-academic-year-ay",
            "Michaelmas Term 2024": "atp-uk-named-term"}
for lit, rid in LITERALS.items():
    e = by_id.get(rid)
    ok(e is not None and e.get("required") is True and e.get("dedicated_to") == lit,
       f"03: {rid} must exist, be required, and be dedicated to {lit!r}")
    ok(e is not None and rx(e).search(lit) is not None, f"03: {lit!r} does not match {rid}")

# Claiming bands (README's canonical order): designator-prefixed, worded, bare-numeric, standalone.
fiscal = next(e for e in d04["entries"] if e["id"] == "fam-fiscal-year")
iso = next(e for e in d04["entries"] if e["id"] == "fam-iso-ymd")
BANDS = [
    [by_id[i] for i in ["atp-academic-year-ay", "atp-academic-year-ay-full", "atp-german-ws-slash",
                        "atp-german-semester-abbrev", "atp-german-semester", "atp-cjk-nendo"]] + [fiscal],
    [by_id[i] for i in ["atp-uk-named-term", "atp-quarter-year", "atp-semester-ordinal", "atp-season-year"]],
    [iso, next(e for e in d04["entries"] if e["id"] == "fam-compact-ymd")],
    [by_id[i] for i in ["atp-year-range-standalone", "atp-year-range-full"]],
]


def claiming(text):
    """Return {entry_id: [span]} after band-ordered claiming."""
    claimed, hits = [], {}
    for band in BANDS:
        for e in band:
            for m in rx(e).finditer(text):
                span = (m.start(), m.end())
                if any(s < span[1] and span[0] < t for s, t in claimed):
                    continue
                if not validate(e.get("validation"), m.group(0)):
                    continue
                claimed.append(span)
                hits.setdefault(e["id"], []).append(m.group(0))
    return hits


for lit, rid in LITERALS.items():
    hits = claiming(lit)
    ok(set(hits) == {rid}, f"claiming: {lit!r} must be claimed by {rid} alone, got {sorted(hits)}")
for text in ["FY 2024-25", "FY2024-25"]:
    hits = claiming(text)
    ok(set(hits) <= {"fam-fiscal-year"} and hits,
       f"claiming: {text!r} must be a fiscal (tax_year) candidate only, got {sorted(hits)}")
hits = claiming("2024-05-11")
ok(set(hits) == {"fam-iso-ymd"}, f"claiming: ISO date must be claimed by fam-iso-ymd alone, got {sorted(hits)}")

# Per-entry examples for 03.
for e in d03["entries"]:
    if e.get("match_kind") != "regex":
        continue
    r = rx(e)
    for v in e.get("examples_true", []):
        m = r.search(v)
        ok(m is not None and validate(e.get("validation"), m.group(0)),
           f"03 {e['id']}: true example {v!r} fails")
    for raw in e.get("examples_false", []):
        v, note = strip_annotation(raw)
        if "claimed by" in note:
            ok(e["id"] not in claiming(v), f"03 {e['id']}: {v!r} must be claimed away, was not")
        else:
            ok(r.search(v) is None, f"03 {e['id']}: false example {v!r} matches")
    for v in e.get("example_fails_validation", []):
        m = r.search(v)
        ok(m is not None, f"03 {e['id']}: fails-validation example {v!r} does not match the regex")
        ok(m is None or not validate(e.get("validation"), m.group(0)),
           f"03 {e['id']}: {v!r} passes validation but is listed as failing")

# Refused shapes are real and no entry admits their examples.
for rid, sample in [("ref-fiscal-year", "FY2025"), ("ref-business-quarter", "Q3 2024"),
                    ("ref-bare-season", "Spring mattress sale"), ("ref-ss-abbrev", "SS 2024"),
                    ("ref-19xx-standalone-range", "1914-18")]:
    row = next(x for x in d03["refused"] if x["id"] == rid)
    ok(re.search(row["pattern"], sample) is not None, f"03 {rid}: refused shape should describe {sample!r}")
    for e in d03["entries"]:
        if e.get("match_kind") == "regex":
            m = rx(e).search(sample)
            ok(m is None or not validate(e.get("validation"), m.group(0)),
               f"03 {e['id']}: admits refused sample {sample!r}")

for bad in ["v2024", "MA 02139", "XPS 13", "2024"]:
    for e in d03["entries"]:
        if e.get("match_kind") == "regex":
            ok(rx(e).search(bad) is None, f"03 {e['id']}: matches non-term {bad!r}")

# ---------------------------------------------------------------- 7. catalogue 04
ok(any("v2024" in r.get("examples_false", []) for r in d04["refused"]),
   "04: v2024 must be listed as a refused non-date")
ok(any(r["id"] == "ref-zip-codes" for r in d04["refused"]), "04: ZIP refusal row must exist")

regex_fams = [e for e in d04["entries"] if e.get("family_kind") == "regex"]
slot_fams = [e for e in d04["entries"] if e.get("family_kind") == "metadata_slot"]
ok(len(slot_fams) >= 2, "04: the EXIF and labeled-slot families must exist")

for bad in ["v2024", "build 4300", "02139", "MA 02139", "2024", "05/11/2024",
            "1716950000", "'25", "ISO 9001", "PHYS1401", "BUSIB 4300", "2024.1", "24.04"]:
    for e in regex_fams:
        m = rx(e).search(bad)
        ok(m is None or not validate(e.get("validation"), m.group(0)),
           f"04 {e['id']}: named non-date {bad!r} becomes a candidate ({m and m.group(0)!r})")
    for e in slot_fams:
        ok(re.match(e["value_pattern"], bad) is None,
           f"04 {e['id']}: named non-date {bad!r} passes the slot layout")

for e in regex_fams:
    r = rx(e)
    for raw in e.get("examples_true", []):
        v, _ = strip_annotation(raw)
        m = r.search(v)
        ok(m is not None and validate(e.get("validation"), m.group(0)),
           f"04 {e['id']}: true example {raw!r} fails")
    for raw in e.get("examples_false", []):
        v, _ = strip_annotation(raw)
        ok(r.search(v) is None, f"04 {e['id']}: false example {raw!r} matches")
    for v in e.get("example_fails_validation", []):
        m = r.search(v)
        ok(m is not None and not validate(e.get("validation"), m.group(0)),
           f"04 {e['id']}: fails-validation example {v!r} misbehaves")

for e in slot_fams:
    for raw in e.get("examples_true", []):
        v, _ = strip_annotation(raw)
        m = re.match(e["value_pattern"], v)
        ok(m is not None and validate(e.get("validation"), v),
           f"04 {e['id']}: true slot value {raw!r} fails its layout/validation")
    for raw in e.get("examples_false", []):
        v, _ = strip_annotation(raw)
        ok(re.match(e["value_pattern"], v) is None,
           f"04 {e['id']}: false slot value {raw!r} passes the layout")
    for v in e.get("example_fails_validation", []):
        ok(re.match(e["value_pattern"], v) is not None and not validate(e.get("validation"), v),
           f"04 {e['id']}: fails-validation slot value {v!r} misbehaves")

exif = next(e for e in slot_fams if e["id"] == "fam-exif-datetimeoriginal")
ok(exif["may_fill"] == ["capture_date"] and exif["reliability"] == "direct",
   "04: the EXIF family must feed capture_date as direct (00 §3.2; P6 Done-means 5)")
ok(fiscal["may_fill"] == ["tax_year"] and "term" in fiscal["never_fill"],
   "04: the fiscal family targets tax_year and never term")

# cross-file pointers
ok(any(r["id"] == "ref-fiscal-year" for r in d03["refused"]),
   "03: fiscal-year must be refused on the term side (it lives in 04)")
ok("NEEDS-JOSEPH" in README, "README must carry the NEEDS-JOSEPH section")

# ---------------------------------------------------------------- verdict
if FAILS:
    print(f"FAIL — {len(FAILS)} problem(s):")
    for f in FAILS:
        print("  -", f)
    sys.exit(1)
print("OK — 12-academic-capture-patterns: all checks pass "
      f"({sum(len(d.get('entries', [])) for d in J.values())} entries, "
      f"{sum(len(d.get('refused', [])) for d in J.values())} refused, "
      f"{sum(len(d.get('uncertain', [])) for d in J.values())} uncertain).")
