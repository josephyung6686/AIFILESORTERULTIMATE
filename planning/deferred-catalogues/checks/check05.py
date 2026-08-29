import json, sys
from pathlib import Path
D = Path("/Users/jy/GRAPH AGENT/planning/deferred-catalogues")
doc = json.loads((D/"05-repository-markers.json").read_text())
fails = []

SETTLED_FOUR = {"package.json", "requirements.txt", "Cargo.toml", "go.mod"}
KINDS = {"repository marker", "package manifest", "notebook metadata", "README file"}
APPLIES = {"filename", "directory_name", "notebook_json_key", "n/a"}

p3 = doc["p3_exclusion_roots"]
p5 = doc["p5_evidence_markers"]

# HARD RULE 5: p3_exclusion_roots is exactly section 1.1's four, nothing added
if {e["match"] for e in p3} != SETTLED_FOUR:
    fails.append(f"p3_exclusion_roots is not exactly the four: {sorted(e['match'] for e in p3)}")
for e in p3:
    if "proposed" in e["status"]:
        fails.append(f"{e['id']}: proposed entry present in p3_exclusion_roots without review")
    if "settled" not in e["status"]:
        fails.append(f"{e['id']}: status is not settled")

# every p5 marker kind must be one P5 accepts, or UnknownMarkerKind is raised
for e in p5:
    if e["kind"] not in KINDS:
        fails.append(f"{e['id']}: kind {e['kind']!r} would raise UnknownMarkerKind")
    if e["applies_to"] not in APPLIES:
        fails.append(f"{e['id']}: unknown applies_to {e['applies_to']!r}")

# ACCEPTANCE: package.json in BOTH arrays, with two documented roles
in_p3 = [e for e in p3 if e["match"] == "package.json"]
in_p5 = [e for e in p5 if e["match"] == "package.json"]
if not in_p3: fails.append("package.json missing from p3_exclusion_roots")
if not in_p5: fails.append("package.json missing from p5_evidence_markers")
if in_p3 and "two roles" not in in_p3[0]["rationale"] and "two jobs" not in in_p3[0]["rationale"]:
    fails.append("package.json p3 row does not document its two roles")

# RULE 5: CMakeLists.txt must be p5 evidence, never a p3 exclusion root
if any(e["match"] == "CMakeLists.txt" for e in p3):
    fails.append("CMakeLists.txt is in p3_exclusion_roots -- rule 5 violation")
if not any(e["match"] == "CMakeLists.txt" for e in p5):
    fails.append("CMakeLists.txt missing from p5_evidence_markers")

# section 1.1's eleven literal directory names belong to neither array
ELEVEN = {"node_modules", ".git", "venv", "build", "dist", "target", "vendor",
          "Pods", "site-packages", "Library", "__pycache__"}
for e in p3:
    if e["match"] in ELEVEN:
        fails.append(f"{e['id']}: section 1.1 literal name duplicated in p3_exclusion_roots")

# every uncertain candidate for the exclusion side must be labelled proposed/open
for e in doc["uncertain"]:
    if "p3_exclusion_root" in e["role"] and not any(
            w in e["status"] for w in ("proposed", "open")):
        fails.append(f"{e['id']}: exclusion candidate not labelled proposed/open")

ids = [e["id"] for e in p3 + p5 + doc["refused"] + doc["uncertain"]]
if len(ids) != len(set(ids)):
    dupes = {i for i in ids if ids.count(i) > 1}
    fails.append(f"duplicate ids: {sorted(dupes)}")

by_kind = {}
for e in p5: by_kind[e["kind"]] = by_kind.get(e["kind"], 0) + 1
print(f"p3_exclusion_roots={len(p3)} (settled four, nothing added)")
print(f"p5_evidence_markers={len(p5)} -> {by_kind}")
print(f"refused={len(doc['refused'])} uncertain={len(doc['uncertain'])}")
if fails:
    print("FAIL:"); [print("  "+f) for f in fails]; sys.exit(1)
print("PASS — exclusion side unextended; package.json in both arrays; all kinds loadable")
