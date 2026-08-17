"""(1) What does a 1000-word head actually cost vs 600 chars?
   (2) How do images split — OCR-able text vs real photos?"""
import sys, re; sys.path.insert(0,'.')
from deep_extract import extract
from pathlib import Path
from collections import Counter
from PIL import Image
import pillow_heif; pillow_heif.register_heif_opener()

HOME=Path.home()
files=[]
for s in (HOME/"Downloads",HOME/"Desktop",HOME/"Documents"):
    if s.exists():
        try: files+=[f for f in s.iterdir() if f.is_file() and not f.name.startswith(".")]
        except Exception: pass

TIER_B={'.png','.jpg','.jpeg','.heic','.webp','.tif','.gif','.mov','.mp4','.mp3','.wav','.m4a'}
IMG={'.png','.jpg','.jpeg','.heic','.webp','.tif','.gif'}

# ---------- (1) head budget ----------
tot600=tot1000w=totfull=0; n=0; short=0
for f in files:
    if f.suffix.lower() in TIER_B: continue
    try: t=extract(f)
    except Exception: t=None
    if not t or len(t.strip())<20: continue
    n+=1; totfull+=len(t)
    tot600 += min(len(t),600)
    words=t.split()
    if len(words)<=1000: short+=1
    tot1000w += len(" ".join(words[:1000]))

print("HEAD BUDGET — text-bearing files only\n")
print(f"  files with text            {n}")
print(f"  full text                  {totfull:>12,} chars  ≈ {totfull//4:>9,} tok")
print(f"  1000-word head             {tot1000w:>12,} chars  ≈ {tot1000w//4:>9,} tok")
print(f"  600-char head              {tot600:>12,} chars  ≈ {tot600//4:>9,} tok")
print(f"\n  docs SHORTER than 1000 words: {short}/{n} ({100*short/n:.0f}%) — head = whole doc")

# ---------- (2) image split ----------
SCREENS={(1170,2532),(1179,2556),(1290,2796),(1284,2778),(1125,2436),(828,1792),
 (1920,1080),(2560,1440),(3840,2160),(1440,900),(2880,1800),(1512,982),(1728,1117),
 (3024,1964),(3456,2234),(2056,1329),(1366,768),(1280,800),(2732,2048),(2388,1668)}
cam=shot=amb=0; rows=Counter()
for f in files:
    if f.suffix.lower() not in IMG: continue
    try:
        with Image.open(f) as im:
            w,h=im.size
            ex=getattr(im,"_getexif",lambda:None)() or {}
            make=any(k in ex for k in (271,272,33437,37386))  # Make/Model/FNumber/FocalLength
    except Exception:
        amb+=1; continue
    named=bool(re.search(r'screenshot|screen shot|cleanshot|^simulator',f.name,re.I))
    scr=(w,h) in SCREENS or (h,w) in SCREENS
    if make: cam+=1; rows['camera EXIF → real photo']+=1
    elif named or scr: shot+=1; rows['screenshot (name or screen size)']+=1
    elif f.suffix.lower()=='.png': shot+=1; rows['PNG, no EXIF → likely capture']+=1
    else: amb+=1; rows['ambiguous → abstain']+=1

print(f"\n\nIMAGE SPLIT — {cam+shot+amb} images\n")
for k,v in rows.most_common(): print(f"  {k:<38} {v:>5}")
print(f"\n  OCR path (text IS the content)      {shot:>5}")
print(f"  EXIF-event path (no useful OCR)     {cam:>5}")
print(f"  abstain / ask                       {amb:>5}")
