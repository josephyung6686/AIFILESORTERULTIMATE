"""How often does same-name-different-bytes actually happen?
Decides: `file (1).ext` vs `ask`."""
import hashlib
from pathlib import Path
from collections import defaultdict

HOME = Path.home()
SOURCES = [HOME/"Downloads", HOME/"Desktop", HOME/"Documents"]
ROOTS   = [HOME/"Desktop", HOME/"Documents"]
SKIP = {"node_modules",".git","venv",".venv","build","dist","target","vendor",
        "Pods","site-packages","Library","__pycache__","DerivedData"}

def h(p):
    try:
        return hashlib.sha256(p.read_bytes()).hexdigest()
    except Exception:
        return None

# loose files = candidates to move
loose = []
for s in SOURCES:
    if s.exists():
        try: loose += [f for f in s.iterdir() if f.is_file() and not f.name.startswith(".")]
        except Exception: pass

# every file already filed inside a destination root, by name
filed = defaultdict(list)
n_filed = 0
for root in ROOTS:
    if not root.exists(): continue
    for f in root.rglob("*"):
        try:
            if not f.is_file() or f.name.startswith("."): continue
            if any(p in SKIP for p in f.relative_to(HOME).parts): continue
            if f.parent in SOURCES: continue           # loose, not filed
            filed[f.name].append(f); n_filed += 1
        except Exception: pass

print(f"loose files      {len(loose)}")
print(f"already filed    {n_filed}  ({len(filed)} distinct names)\n")

same_name = [f for f in loose if f.name in filed]
print(f"loose files whose name ALREADY EXISTS somewhere filed: {len(same_name)} "
      f"({100*len(same_name)/max(len(loose),1):.1f}%)\n")

ident = diff = 0
examples = []
for f in same_name:
    fh = h(f)
    if fh is None: continue
    hs = {h(g) for g in filed[f.name]}
    if fh in hs: ident += 1
    else:
        diff += 1
        if len(examples) < 6: examples.append((f, filed[f.name][0]))

print(f"  identical bytes  → skip, already filed : {ident}")
print(f"  DIFFERENT bytes  → the disputed case   : {diff}")
print(f"\n  disputed as a share of all loose files : {100*diff/max(len(loose),1):.2f}%")
for a, b in examples:
    print(f"      · {a.name[:52]}")
    print(f"          loose {str(a.parent).replace(str(HOME),'~')}")
    print(f"          filed {str(b.parent).replace(str(HOME),'~')}")
