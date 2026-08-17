"""RECOMMENDATION ENGINE: given existing folders + loose files, propose the frozen tree.
Existing folders = proven destinations. Loose files = what needs a home.
Output = the canvas: existing structure (absorbs N) + proposed additions (covers M)."""
import re, time
from pathlib import Path
from collections import defaultdict, Counter

HOME = Path.home()
ROOTS = [HOME/"Desktop", HOME/"Documents"]
SOURCES = [HOME/"Downloads", HOME/"Desktop", HOME/"Documents"]
STOP = {"the","and","for","with","from","copy","final","draft","new","old","untitled",
        "document","documents","file","files","download","downloads","pdf","docx","img","image"}

def toks(s):
    s = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', s)
    return {w.lower() for w in re.split(r'[^A-Za-z0-9]+', s)
            if len(w) > 2 and not w.isdigit() and w.lower() not in STOP}

# ---------- 1. existing folders = the destination graph ----------
folders = {}
for root in ROOTS:
    if not root.exists(): continue
    for d in root.rglob("*"):
        try:
            if not d.is_dir(): continue
            if any(p.startswith(".") for p in d.relative_to(HOME).parts): continue
            if len(d.relative_to(root).parts) > 3: continue
            fs = [f for f in d.iterdir() if f.is_file() and not f.name.startswith(".")]
            if len(fs) >= 3:
                folders[d] = {"n": len(fs),
                              "tok": toks(d.name) | set().union(*[toks(f.stem) for f in fs[:40]] or [set()]),
                              "name_tok": toks(d.name),
                              "ext": Counter(f.suffix.lower() for f in fs)}
        except Exception: pass
print(f"destination candidates: {len(folders)} existing folders "
      f"({sum(v['n'] for v in folders.values())} files already filed)\n", flush=True)

# ---------- 2. loose files = what needs a home ----------
loose = []
for s in SOURCES:
    if not s.exists(): continue
    try:
        loose += [f for f in s.iterdir() if f.is_file() and not f.name.startswith(".")]
    except Exception: pass
print(f"loose files needing a home: {len(loose)}", flush=True)
for s in SOURCES:
    c = sum(1 for f in loose if f.parent == s)
    print(f"    {c:>5}  {s.name}")
print(flush=True)

# ---------- 3. which existing folder absorbs each loose file ----------
t0 = time.time()
absorbed = defaultdict(list); unmatched = []
for f in loose:
    ft = toks(f.stem)
    if not ft: unmatched.append(f); continue
    best, bs = None, 0.0
    for d, meta in folders.items():
        nm = len(ft & meta["name_tok"])                 # folder-name match weighs most
        ct = len(ft & meta["tok"])
        if nm == 0 and ct < 2: continue
        s = nm * 3.0 + ct * 0.6 + (0.5 if f.suffix.lower() in meta["ext"] else 0)
        if s > bs: best, bs = d, s
    if best and bs >= 3.0: absorbed[best].append(f)
    else: unmatched.append(f)
print(f"matched in {time.time()-t0:.1f}s\n")

cov = sum(len(v) for v in absorbed.values())
print("=" * 78)
print(f"EXISTING FOLDERS ABSORB   {cov:>5} / {len(loose)}  ({100*cov/len(loose):.0f}%)")
print(f"NEED NEW STRUCTURE        {len(unmatched):>5} / {len(loose)}  ({100*len(unmatched)/len(loose):.0f}%)")
print("=" * 78)

print("\n--- TOP EXISTING DESTINATIONS (already on disk, would absorb) ---\n")
for d, fs in sorted(absorbed.items(), key=lambda kv: -len(kv[1]))[:14]:
    rel = d.relative_to(HOME)
    print(f"  {len(fs):>4} ← {str(rel)[:62]}   (has {folders[d]['n']})")
    for f in fs[:2]: print(f"          · {f.name[:64]}")

# ---------- 4. propose NEW folders for the unmatched ----------
print("\n--- PROPOSED NEW FOLDERS (for what fits nowhere) ---\n")
tokgroups = defaultdict(list)
for f in unmatched:
    for t in toks(f.stem): tokgroups[t].append(f)
cand = sorted(((t, fs) for t, fs in tokgroups.items() if len(fs) >= 6),
              key=lambda kv: -len(kv[1]))
claimed, shown = set(), 0
for t, fs in cand:
    fresh = [f for f in fs if f not in claimed]
    if len(fresh) < 6: continue
    shown += 1
    if shown > 12: break
    claimed.update(fresh)
    ex = Counter(f.suffix.lower().lstrip('.') for f in fresh)
    print(f"  + {t:<22} {len(fresh):>4} files   [{', '.join(f'{k}:{v}' for k,v in ex.most_common(3))}]")
    for f in fresh[:2]: print(f"          · {f.name[:64]}")
print(f"\n  still unplaced after proposals: {len(unmatched)-len(claimed)}")
