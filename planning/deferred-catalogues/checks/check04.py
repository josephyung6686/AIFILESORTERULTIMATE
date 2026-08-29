import json, re, sys
from pathlib import Path
D = Path("/Users/jy/GRAPH AGENT/planning/deferred-catalogues")
doc = json.loads((D/"04-camera-filename-patterns.json").read_text())

def stem(name):
    return name.rsplit(".", 1)[0] if "." in name else name

def match(entry, filename):
    flags = 0 if entry.get("case_sensitive") else re.IGNORECASE
    return re.match(entry["pattern"], stem(filename), flags)

def first(filename):
    for e in doc["entries"]:
        if match(e, filename):
            return e
    return None

fails = []
for e in doc["entries"]:
    if not match(e, e["example_true"]):
        fails.append(f"{e['id']}: example_true {e['example_true']!r} did NOT match")
    if match(e, e["example_false"]):
        fails.append(f"{e['id']}: example_false {e['example_false']!r} DID match")
    # capture group must exist and be a real substring of the stem
    m = match(e, e["example_true"])
    if m:
        try:
            got = m.group(e["capture"])
        except Exception as exc:
            fails.append(f"{e['id']}: capture group {e['capture']} invalid ({exc})")
        else:
            if got not in stem(e["example_true"]):
                fails.append(f"{e['id']}: capture {got!r} not a substring of the stem")

# refusals and uncertain: their example_false must match nothing at all
expected = []
for e in doc["refused"] + doc["uncertain"]:
    if e["example_false"] in ("—", "-"):
        continue
    hit = first(e["example_false"])
    if not hit:
        continue
    if e.get("cross_match_expected"):
        expected.append(f"{e['id']}: {e['example_false']!r} -> {hit['id']} (documented)")
    else:
        fails.append(f"{e['id']}: {e['example_false']!r} matched by {hit['id']}")

# GUARD 1 -- the catalogues-finish agent's finding, generalised.
# macOS puts dots in the time, so a bare-stem example is truncated by stem() and
# then fails or passes for the wrong reason. Every example must carry an extension.
for e in doc["entries"] + doc["refused"] + doc["uncertain"]:
    for key in ("example_true", "example_false"):
        v = e.get(key)
        if not v or v in ("\u2014", "-"):
            continue
        if stem(v) != v:                      # something was stripped
            ext = v.rsplit(".", 1)[1]
            if not (ext.isalnum() and " " not in ext and 1 <= len(ext) <= 5):
                fails.append(f"{e['id']}.{key}: {v!r} has dots but no file extension -- "
                             f"stem() truncates it to {stem(v)!r}")

# GUARD 2 -- discriminator collisions must land on exactly the named row.
for e in doc["entries"]:
    hit = first(e["example_false"])
    want = e.get("discriminates_from")
    got = hit["id"] if hit else None
    if got != want:
        fails.append(f"{e['id']}.example_false {e['example_false']!r}: "
                     f"discriminates_from={want!r} but matched {got!r}")

ACCEPT = [
    # the brief's acceptance case: IMG_4821 is CAMERA, not screenshot
    ("IMG_4821.png", "fnp-apple-dcf-img", "camera_file_system"),
    ("IMG_20240115_103045.jpg", "fnp-android-img-timestamp", "camera_timestamp"),
    ("IMG_E4821.jpg", "fnp-apple-img-edited", "camera_file_system"),
    ("IMG-20240115-WA0001.jpg", "fnp-whatsapp-img", "messaging"),
    ("Screenshot 2024-01-15 at 10.30.45.png", "fnp-macos-screenshot", "screen_capture"),
    ("Screenshot (42).png", "fnp-windows-screenshot-numbered", "screen_capture"),
    ("Screenshot_20240115-103045_Chrome.png", "fnp-android-screenshot", "screen_capture"),
    ("DSC01234.ARW", "fnp-sony-dsc", "camera_file_system"),
    ("GX010042.MP4", "fnp-gopro-chaptered", "camera_file_system"),
    # course codes must NOT match anything -- the ref-dcf-generic refusal
    ("MATH2010.png", None, None), ("ECON1001.png", None, None),
    ("FALL2024.png", None, None), ("NOTE2024.jpg", None, None),
    ("CHEM1220.jpg", None, None), ("BUSIB4300.pdf", None, None),
    ("Screenshot of the enrollment error.png", None, None),
    ("IMG_final_v3.jpg", None, None), ("Wash U.docx", None, None),
    ("Hw 5.pdf", None, None),
]
for name, want_id, want_class in ACCEPT:
    e = first(name)
    got_id = e["id"] if e else None
    if got_id != want_id:
        fails.append(f"ACCEPT {name!r}: wanted {want_id!r}, got {got_id!r}")
    elif e and e["class"] != want_class:
        fails.append(f"ACCEPT {name!r}: wanted class {want_class!r}, got {e['class']!r}")

# no entry may be labelled with a media-type verdict
for e in doc["entries"]:
    low = e["pattern_label"].lower()
    for banned in ("is a photo", "is a screenshot", "photograph of", "media type"):
        if banned in low:
            fails.append(f"{e['id']}: pattern_label states a media-type verdict")

ids = [e["id"] for e in doc["entries"] + doc["refused"] + doc["uncertain"]]
if len(ids) != len(set(ids)):
    fails.append("duplicate ids")

print(f"entries={len(doc['entries'])} refused={len(doc['refused'])} uncertain={len(doc['uncertain'])}")
for line in expected:
    print("  expected cross-match: " + line)
if fails:
    print("FAIL:"); [print("  "+f) for f in fails]; sys.exit(1)
print("PASS — IMG_4821 reads as camera; course codes match nothing; captures are real substrings")
