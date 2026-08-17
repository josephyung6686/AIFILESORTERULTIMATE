"""Which hand-written templates does THIS corpus actually need? Measure detection signals.
Also: how much would OCR of screenshots add, and what new edge types are provable?"""
import re
from pathlib import Path
from collections import Counter, defaultdict

HOME = Path.home()
SRC = [HOME/"Downloads", HOME/"Desktop", HOME/"Documents"]
files = []
for s in SRC:
    if s.exists():
        files += [f for f in s.iterdir() if f.is_file() and not f.name.startswith(".")]
N = len(files)
names = [f.name for f in files]
low = [n.lower() for n in names]
print(f"loose corpus: {N} files\n")

# ---------- template detection signals (filename-level only, cheap sweep) ----------
SIG = {
 "Academic coursework": [r'\b[a-z]{2,5}\s?\d{3,4}\b', r'\b(hw|homework|pset|problem set|lecture|syllabus|exam|midterm|quiz|final)\b'],
 "Applications":        [r'\b(supplement|supplemental|application|admission|essay|letter of continued interest|loci)\b'],
 "Career":              [r'\b(resume|cv|cover letter|interview|offer letter|portfolio)\b'],
 "Research / lab":      [r'\b(abstract|manuscript|figure|data|assay|sample|protocol|pva|rdp|graft|experiment)\b'],
 "Finance / admin":     [r'\b(invoice|receipt|statement|tax|payment|billing|refund|bank|insurance|order)\b'],
 "Identity / records":  [r'\b(passport|id card|hkid|licence|license|visa|vaccine|immunis|immuniz|transcript|certificate)\b'],
 "Photos / captures":   [r'^(img[_ ]?\d|dsc|photo|screenshot|screen shot|whatsapp image)'],
 "Media / downloads":   [r'\.(mp4|mov|mp3|wav|m4a)$', r'\b(episode|track|recording)\b'],
 "Software / installers":[r'\.(dmg|pkg|exe|msi|zip|app)$'],
 "Code / notebooks":    [r'\.(py|ipynb|js|ts|json|csv)$'],
}
print("=== TEMPLATE FIT (which templates this corpus needs) ===\n")
hits = {}
for t, pats in SIG.items():
    m = {n for n in low if any(re.search(p, n) for p in pats)}
    hits[t] = m
    bar = "█" * int(40*len(m)/N)
    print(f"  {t:<24} {len(m):>5} ({100*len(m)/N:>4.1f}%) {bar}")

covered = set().union(*hits.values())
print(f"\n  any template matches: {len(covered)}/{N} = {100*len(covered)/N:.0f}%")
print(f"  matches NOTHING     : {N-len(covered)}\n")

# ---------- OCR opportunity: what is currently unreadable? ----------
IMGX = {".png",".jpg",".jpeg",".heic",".webp",".tif",".gif"}
imgs = [f for f in files if f.suffix.lower() in IMGX]
shots = [f for f in imgs if re.search(r'screenshot|screen shot|^cleanshot', f.name, re.I)]
opaque_img = [f for f in imgs if re.match(r'^(img[_ ]?\d|dsc|\d+|[0-9a-f]{8,})', f.stem, re.I)]
print("=== OCR OPPORTUNITY ===\n")
print(f"  images total            {len(imgs):>5}")
print(f"  screenshots (by name)   {len(shots):>5}   → OCR yields their entire content")
print(f"  opaque-named images     {len(opaque_img):>5}   → EXIF or vision")
print(f"  est. OCR cost @739ms    {(len(shots)+len(opaque_img))*0.739/60:>5.1f} min\n")

# ---------- provable edge types present in this corpus ----------
print("=== PROVABLE EDGE TYPES (deterministic, no inference) ===\n")
# derived_from: X.docx.pdf  → a PDF exported from a DOCX
derived = [n for n in names if re.search(r'\.(docx|doc|pptx|xlsx|pages|key)\.(pdf|txt)$', n, re.I)]
# sequential: same stem + adjacent integer
seq = defaultdict(list)
for f in files:
    m = re.match(r'^(.*?)[ _\-]?(\d{1,3})$', f.stem)
    if m and len(m.group(1)) > 2: seq[(m.group(1).lower(), f.suffix.lower())].append(int(m.group(2)))
seqg = {k: sorted(v) for k, v in seq.items() if len(v) >= 3}
# containers
arch = [f for f in files if f.suffix.lower() in {".zip",".tar",".gz",".7z",".rar"}]
# same-title-different-format
bystem = defaultdict(set)
for f in files: bystem[f.stem.lower()].add(f.suffix.lower())
multifmt = {k: v for k, v in bystem.items() if len(v) > 1}

print(f"  derived_from (X.docx.pdf)      {len(derived):>5}   e.g. {derived[0][:52] if derived else '-'}")
print(f"  sequential (unit_7,8,9)        {len(seqg):>5} runs")
for k, v in list(sorted(seqg.items(), key=lambda kv: -len(kv[1])))[:4]:
    print(f"        {k[0][:34]:<36} {v[:8]}")
print(f"  contains (archive manifests)   {len(arch):>5} archives → readable without extracting")
print(f"  same_content_diff_format       {len(multifmt):>5}   e.g. {list(multifmt.items())[0][0][:40] if multifmt else '-'}")
