import json, re, sys, unicodedata
from pathlib import Path

D = Path("/Users/jy/GRAPH AGENT/planning/deferred-catalogues")
doc = json.loads((D / "01-tool-producer-strings.json").read_text())

BOUNDARY = set(" \t,;:/()-_.+&\u00ae\u2122\u00a9")

def norm(v):
    return unicodedata.normalize("NFC", v).strip()

def matches(entry, value):
    v = norm(value)
    kind = entry["match_kind"]
    cs = entry["case_sensitive"]
    if kind == "regex":
        flags = 0 if cs else re.IGNORECASE
        return re.search(entry["pattern"], v, flags) is not None
    m = entry["match"]
    hay, needle = (v, m) if cs else (v.lower(), m.lower())
    if kind == "exact":
        return hay == needle
    if kind == "prefix":
        if hay == needle:
            return True
        if not hay.startswith(needle):
            return False
        rest = v[len(m):]
        if rest[0] not in BOUNDARY:
            return False
        if entry.get("tail_required") == "any":
            return True
        return any(c.isdigit() for c in rest)
    raise ValueError(kind)

def first_match(value):
    for e in doc["entries"]:
        if matches(e, value):
            return e["id"]
    return None

fails = []
# Every entry's own examples must behave.
for e in doc["entries"]:
    if not matches(e, e["example_true"]):
        fails.append(f"{e['id']}: example_true {e['example_true']!r} did NOT match")
    if matches(e, e["example_false"]):
        fails.append(f"{e['id']}: example_false {e['example_false']!r} DID match")

# Every example_false must match NO entry at all (cross-entry check).
for e in doc["entries"]:
    hit = first_match(e["example_false"])
    if hit:
        fails.append(f"{e['id']}: example_false {e['example_false']!r} matched by {hit}")

# Refusals and uncertain items must match nothing.
for e in doc["refused"] + doc["uncertain"]:
    hit = first_match(e["example_false"])
    if hit:
        fails.append(f"{e['id']} (refused/uncertain): {e['example_false']!r} matched by {hit}")

# Acceptance cases from the brief.
ACCEPT = [
    ("python-docx", True), ("Mozilla/5.0 (Windows NT 10.0) Chrome/121.0.0.0", True),
    ("Jane Chen", False), ("Docx Family Trust", False), ("Adobe", False),
    ("Prince", False), ("Prince 15.1 (www.princexml.com)", True),
    ("Skia/PDF m121", True), ("macOS Version 14.4 (Build 23E214) Quartz PDFContext", True),
    ("Dr. Sarah Okonkwo-Bell", False), ("María José García", False),
    ("Prof. Chrome Wang", False), ("Word", True), ("Word Association Study", False),
    ("17.5.1", True), ("2025", False), ("Michaelmas Term 2024", False),
    ("Spring 2025", False), ("2024-05-11", False),
]
for value, want in ACCEPT:
    got = first_match(value) is not None
    if got != want:
        fails.append(f"ACCEPT {value!r}: wanted match={want}, got {first_match(value)!r}")

ids = [e["id"] for e in doc["entries"] + doc["refused"] + doc["uncertain"]]
if len(ids) != len(set(ids)):
    fails.append("duplicate ids")

print(f"entries={len(doc['entries'])} refused={len(doc['refused'])} uncertain={len(doc['uncertain'])}")
if fails:
    print("FAIL:"); [print("  " + f) for f in fails]; sys.exit(1)
print("PASS — all examples, refusals and acceptance cases behave")
