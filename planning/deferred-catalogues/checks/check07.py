import json, re, sys
from pathlib import Path
D = Path("/Users/jy/GRAPH AGENT/planning/deferred-catalogues")
doc = json.loads((D/"07-archive-recognizable-markers.json").read_text())
cat05 = json.loads((D/"05-repository-markers.json").read_text())
fails = []

# P5 raises UnknownMarkerKind on anything but these two.
MARKER_KINDS = {"source-code manifest", "document name"}
for e in doc["entries"]:
    if e["kind"] not in MARKER_KINDS:
        fails.append(f"{e['id']}: kind {e['kind']!r} would raise UnknownMarkerKind")

def basename(p):
    return p.rsplit("/", 1)[-1]

def stem(p):
    b = basename(p)
    return b.rsplit(".", 1)[0] if "." in b else b

def matches(e, member_path):
    if e["match_kind"] == "regex":
        target = stem(member_path)
        return re.search(e["pattern"], target, 0 if e["case_sensitive"] else re.IGNORECASE) is not None
    needle = e["match"]
    if e["applies_to"] == "member_path_segment":
        segs = member_path.split("/")
        return (needle in segs) if e["case_sensitive"] else (needle.lower() in [s.lower() for s in segs])
    b = basename(member_path)
    return b == needle if e["case_sensitive"] else b.lower() == needle.lower()

def hits(member_path):
    return [e["id"] for e in doc["entries"] if matches(e, member_path)]

for e in doc["entries"]:
    if e["id"] not in hits(e["example_true"]):
        fails.append(f"{e['id']}: example_true {e['example_true']!r} did NOT match")
    if e["id"] in hits(e["example_false"]):
        fails.append(f"{e['id']}: example_false {e['example_false']!r} DID match")

# section 2.5's five document names must all be present and be exactly five
docs = [e for e in doc["entries"] if e["kind"] == "document name"]
if len(docs) != 5:
    fails.append(f"document-name array is {len(docs)} rows, section 2.5 names five")
for name in ("transcript", "personal-statement", "resume", "certificate", "form"):
    if not any(e["id"] == f"arc-doc-{name}" for e in docs):
        fails.append(f"missing section 2.5 document name: {name}")

# section 2.5's four code revealers must all be recognised
for path, why in [("project/README.md", "README.md"), ("project/package.json", "package.json"),
                  ("project/src/main.py", "src directory"), ("project/pkg/__init__.py", "Python package layout")]:
    if not hits(path):
        fails.append(f"section 2.5 names {why!r} but {path!r} matched nothing")

# the submission.zip worked case: five documents, five markers
SUBMISSION = ["submission/Transcript_Official.pdf", "submission/Personal_Statement_Final.pdf",
              "submission/Resume.pdf", "submission/Certificate.pdf", "submission/Form.pdf"]
got = {h for p in SUBMISSION for h in hits(p)}
if len(got) != 5:
    fails.append(f"submission.zip worked case produced {len(got)} distinct markers, expected 5: {sorted(got)}")

# 'form' must be whole-word only
for bad in ("submission/transformation-notes.pdf", "submission/format-guide.pdf",
            "submission/formula-sheet.pdf", "submission/information.pdf"):
    if "arc-doc-form" in hits(bad):
        fails.append(f"'form' fired on {bad!r} -- whole-word matching failed")
for bad in ("data/opencv-notes.txt", "data/cvs-export.csv"):
    if "arc-doc-resume" in hits(bad):
        fails.append(f"'cv' fired on {bad!r} -- whole-word matching failed")

# no drift: every derived row must correspond to a live catalogue-05 row
c05 = {e["match"] for e in cat05["p5_evidence_markers"]}
for e in doc["entries"]:
    if e["kind"] == "source-code manifest" and e["match"] not in c05:
        fails.append(f"{e['id']}: {e['match']!r} not present in catalogue 05 -- drift")

# no document-type vocabulary beyond section 2.5's five
for bad in ("submission/cover_letter.pdf", "submission/diploma.pdf", "submission/essay.pdf",
            "submission/invoice.pdf", "submission/syllabus.pdf", "submission/thesis.pdf"):
    h = [x for x in hits(bad) if x.startswith("arc-doc-")]
    if h:
        fails.append(f"invented document type: {bad!r} matched {h}")

ids = [e["id"] for e in doc["entries"] + doc["refused"] + doc["uncertain"]]
if len(ids) != len(set(ids)):
    fails.append("duplicate ids")

print(f"entries={len(doc['entries'])} (source-code manifest={len(doc['entries'])-len(docs)}, document name={len(docs)})")
print(f"refused={len(doc['refused'])} uncertain={len(doc['uncertain'])}")
if fails:
    print("FAIL:"); [print("  "+f) for f in fails]; sys.exit(1)
print("PASS — submission.zip yields 5 markers; both kinds loadable; no drift from catalogue 05")
