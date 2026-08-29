import json
from math import gcd
from pathlib import Path
D = Path("/Users/jy/GRAPH AGENT/planning/deferred-catalogues")
r2 = json.loads((D/"02-screen-resolutions.json").read_text())
r3 = json.loads((D/"03-sensor-aspect-ratios.json").read_text())
res = {e["match"] for e in r2["entries"]}
ratios = {e["match"]: e for e in r3["entries"]}
tol = 0.005

def canon(s):
    w, h = (int(x) for x in s.lower().split("x"))
    return f"{max(w,h)}x{min(w,h)}", max(w,h)/min(w,h)

def reduce_ratio(s):
    w, h = (int(x) for x in s.lower().split("x"))
    a, b = max(w,h), min(w,h); g = gcd(a,b)
    return f"{a//g}:{b//g}"

def signal(dim):
    key, dec = canon(dim)
    if key in res: return "exact display resolution"
    if reduce_ratio(dim) in ratios: return "sensor-shaped dimensions"
    for e in ratios.values():
        if abs(dec - e["decimal"]) / e["decimal"] <= tol: return "sensor-shaped dimensions"
    return None

fails = []
CASES = [
    ("1920x1080", "exact display resolution"), ("1080x1920", "exact display resolution"),
    ("4032x3024", "sensor-shaped dimensions"), ("3024x4032", "sensor-shaped dimensions"),
    ("8064x6048", "sensor-shaped dimensions"), ("6000x4000", "sensor-shaped dimensions"),
    ("4032x2268", "sensor-shaped dimensions"), ("4080x3072", "sensor-shaped dimensions"),
    ("2560x1600", "exact display resolution"), ("1290x2796", "exact display resolution"),
    ("3024x1964", "exact display resolution"), ("847x1291", None), ("1000x317", None),
    # documented near-miss fall-through, unc-near-miss-fallthrough
    ("1919x1080", "sensor-shaped dimensions"),
]
for dim, want in CASES:
    got = signal(dim)
    if got != want: fails.append(f"{dim}: wanted {want!r}, got {got!r}")

anchors = {e["match"] for e in r3["sensor_output_sizes"]}
for a in anchors:
    if canon(a)[0] in res: fails.append(f"anchor {a} is also a catalogue-02 resolution")

e = next(x for x in r2["entries"] if x["match"] == "1920x1080")
if e.get("overlaps_sensor_ratio") != "16:9": fails.append("1920x1080 not flagged 16:9")
if e["false_positive_risk"] != "high": fails.append("1920x1080 not flagged high risk")

# every catalogue-02 example_false must not be a catalogue-02 entry
for x in r2["entries"]:
    if canon(x["example_false"])[0] in res: fails.append(f"{x['id']} example_false is an entry")

print(f"cat02={len(r2['entries'])} ratios={len(ratios)} anchors={len(anchors)} uncertain03={len(r3['uncertain'])}")
if fails:
    print("FAIL:"); [print("  "+f) for f in fails]; raise SystemExit(1)
print("PASS — arbitration, overlap flags, anchor separation all behave")
