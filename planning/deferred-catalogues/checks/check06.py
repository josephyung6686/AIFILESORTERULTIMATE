import json, re, sys
from pathlib import Path
D = Path("/Users/jy/GRAPH AGENT/planning/deferred-catalogues")
doc = json.loads((D/"06-citation-identifier-patterns.json").read_text())
fails = []

# --- the checksums the file claims, implemented so the claims are exercised -----
def digits(s):
    return [c for c in s if c.isdigit() or c in "Xx"]

def ok_isbn13(s):
    d = [c for c in s if c.isdigit()]
    if len(d) != 13: return False
    tot = sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(d[:12]))
    return (10 - tot % 10) % 10 == int(d[12])

def ok_isbn10(s):
    d = digits(s)
    if len(d) != 10: return False
    tot = sum((10 - i) * (10 if c in "Xx" else int(c)) for i, c in enumerate(d))
    return tot % 11 == 0

def ok_issn(s):
    d = digits(s)
    if len(d) != 8: return False
    tot = sum((8 - i) * (10 if c in "Xx" else int(c)) for i, c in enumerate(d))
    return tot % 11 == 0

def ok_mod11_2(s):
    d = digits(s)
    if len(d) != 16: return False
    tot = 0
    for c in d[:15]:
        tot = (tot + int(c)) * 2
    want = (12 - tot % 11) % 11
    got = 10 if d[15] in "Xx" else int(d[15])
    return want == got

CHECKS = {"isbn": lambda s: ok_isbn13(s) or ok_isbn10(s),
          "issn": ok_issn, "orcid": ok_mod11_2, "isni": ok_mod11_2}

def hits(text):
    out = []
    for e in doc["entries"]:
        flags = 0 if e["case_sensitive"] else re.IGNORECASE
        m = re.search(e["pattern"], text, flags)
        if not m:
            continue
        # a shape match without a passing checksum is NOT a hit -- the file's rule 3
        check = CHECKS.get(e["kind"]) if e.get("checksum") else None
        if check and not check(m.group(0)):
            continue
        out.append(e["id"])
    return out

# every pattern must compile
for e in doc["entries"]:
    try:
        re.compile(e["pattern"])
    except re.error as exc:
        fails.append(f"{e['id']}: pattern does not compile ({exc})")

# each entry's own examples
for e in doc["entries"]:
    if e["id"] not in hits(e["example_true"]):
        fails.append(f"{e['id']}: example_true {e['example_true']!r} did NOT match")
    if e["id"] in hits(e["example_false"]):
        fails.append(f"{e['id']}: example_false {e['example_false']!r} DID match")

# ACCEPTANCE: no section 3.10 date pattern anywhere in this file
# teammate acceptance case: a version-like string must NOT read as a DOI
for bad in ("10.1.145", "version 10.1.145"):
    if "cid-doi" in hits(bad):
        fails.append(f"DOI over-match: {bad!r} read as a DOI")

DATES = ["Spring 2025", "AY 2024-25", "Michaelmas Term 2024", "2024-05-11", "2025",
         "05/11/2024", "Fall 2023", "2024", "January 2025", "2024-2025", "Q3 2024"]
for d in DATES:
    h = hits(d)
    if h:
        fails.append(f"DATE LEAK: {d!r} matched by {h}")

# ACCEPTANCE: no gazetteer / entity matching
ENTITIES = ["BUSIB 4300", "University of Chicago", "U Chicago", "MATH 2010", "Wash U"]
for x in ENTITIES:
    h = hits(x)
    if h:
        fails.append(f"ENTITY LEAK: {x!r} matched by {h}")

# refused privacy patterns must match nothing
PRIVACY = ["123-45-6789", "4111 1111 1111 1111", "+1 (773) 555-0142"]
for x in PRIVACY:
    h = hits(x)
    if h:
        fails.append(f"PRIVACY LEAK: {x!r} matched by {h}")

# positive smoke tests
POS = [
    ("https://doi.org/10.1038/s41586-021-03819-2", "cid-doi"),
    ("arXiv:2103.02702v2", "cid-arxiv-new"),
    ("https://orcid.org/0000-0002-1825-0097", "cid-orcid"),
    ("ISBN 978-0-13-235088-4", "cid-isbn13"),
    ("ISSN 0028-0836", "cid-issn"),
    ("PMID: 34567890", "cid-pmid"),
    ("PMID: 345678901", "cid-pmid"),          # 9-digit UIs, NLM 2002 onward
    ("10.1145/3372297.3417231", "cid-doi"),   # teammate acceptance case
    ("PMC3084216", "cid-pmcid"),
    ("j.chen@uchicago.edu", "cid-email"),
    ("as shown previously [12, 15-17]", "cid-citation-numeric"),
    ("prior work (Okonkwo et al., 2021) suggests", "cid-citation-authoryear"),
]
for text, want in POS:
    h = hits(text)
    if want not in h:
        fails.append(f"MISS: {text!r} should hit {want}, got {h}")

# every row with a documented checksum must say it is required
for e in doc["entries"]:
    if e.get("checksum") and "Required" not in e["checksum"] and "required" not in e["checksum"]:
        fails.append(f"{e['id']}: checksum documented but not marked required")

ids = [e["id"] for e in doc["entries"] + doc["refused"] + doc["uncertain"]]
if len(ids) != len(set(ids)):
    fails.append("duplicate ids")

ck = sum(1 for e in doc["entries"] if e.get("checksum"))
# the checksum validators must themselves be right
for good in ("9780132350884",): assert ok_isbn13(good), good
for bad in ("9781234567890",): assert not ok_isbn13(bad), bad
assert ok_isbn10("0-13-235088-2"); assert ok_issn("0028-0836")
assert ok_mod11_2("0000-0002-1825-0097")
assert not ok_mod11_2("4111-1111-1111-1111")
print(f"entries={len(doc['entries'])} (with checksums={ck}) refused={len(doc['refused'])} uncertain={len(doc['uncertain'])}")
print("  checksum validators self-verified: ISBN-13, ISBN-10, ISSN, MOD 11-2")
if fails:
    print("FAIL:"); [print("  "+f) for f in fails]; sys.exit(1)
print("PASS — no date leaks, no entity leaks, no privacy leaks; all identifiers found")
