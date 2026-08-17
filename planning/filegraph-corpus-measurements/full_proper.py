"""Full corpus, ALL formats. The honest total."""
import time, sys
from pathlib import Path
from collections import Counter
sys.path.insert(0,'.')
from deep_extract import extract, facts

HOME=Path.home()
files=[]
for s in (HOME/"Downloads",HOME/"Desktop",HOME/"Documents"):
    if s.exists():
        try: files+=[f for f in s.iterdir() if f.is_file() and not f.name.startswith(".")]
        except Exception: pass

t0=time.time(); chars=0; got=0; nofact=0; nolayer=0; fx_total=Counter(); tier=Counter()
TIER_B={'.png','.jpg','.jpeg','.heic','.webp','.tif','.gif','.mov','.mp4','.mp3','.wav','.m4a'}
for f in files:
    e=f.suffix.lower()
    if e in TIER_B: tier['B media (metadata only)']+=1; continue
    try: t=extract(f)
    except Exception: t=None
    if t is None: tier['D opaque (name only)']+=1; nolayer+=1; continue
    tier['A text-bearing']+=1
    if len(t.strip())<20: nofact+=1; continue
    chars+=len(t); got+=1
    for k,v in facts(f.name,t).items(): fx_total[k]+=len(v)
wall=time.time()-t0

print(f"FULL CORPUS, ALL FORMATS   {wall:.1f} s   for {len(files)} files\n")
for k,v in sorted(tier.items()): print(f"  {k:<28} {v:>5}")
print(f"\n  text recovered        {chars:,} chars from {got} files")
print(f"  empty / no text layer {nofact}  → owe OCR")
print(f"\n  facts by kind:")
for k,v in fx_total.most_common(): print(f"    {k:<14} {v:>6}")
