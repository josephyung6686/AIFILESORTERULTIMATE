"""What did the 68s run ACTUALLY touch? Honest audit."""
from pathlib import Path
from collections import Counter

HOME=Path.home(); SRC=[HOME/"Downloads",HOME/"Desktop",HOME/"Documents"]
files=[]
for s in SRC:
    if s.exists():
        try: files+=[f for f in s.iterdir() if f.is_file() and not f.name.startswith(".")]
        except Exception: pass

HANDLED_TEXT={'.pdf','.docx'}
HANDLED_META={'.png','.jpg','.jpeg','.heic','.webp','.tif'}
ext=Counter(f.suffix.lower() for f in files)

t=m=skipped=0
print(f"{len(files)} loose files\n")
print(f"{'ext':<10}{'count':>7}   what the 68s run did")
print("-"*62)
for e,c in ext.most_common(24):
    if e in HANDLED_TEXT: what="FULL TEXT extracted"; t+=c
    elif e in HANDLED_META: what="opened, dimensions + EXIF only"; m+=c
    else: what="** NOTHING — counted and skipped **"; skipped+=c
    print(f"{e or '(none)':<10}{c:>7}   {what}")
other=sum(c for e,c in ext.items() if e not in HANDLED_TEXT and e not in HANDLED_META)
print("-"*62)
print(f"\n  full text extracted        {t:>5}  ({100*t/len(files):.0f}%)")
print(f"  metadata only              {m:>5}  ({100*m/len(files):.0f}%)")
print(f"  NOT TOUCHED AT ALL         {other:>5}  ({100*other/len(files):.0f}%)")
