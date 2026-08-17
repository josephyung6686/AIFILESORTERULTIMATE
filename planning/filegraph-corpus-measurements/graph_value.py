"""Does the graph earn its place on DUPLICATES / VERSIONS / EVENTS rather than facet recall?
Measures what deterministic edges actually deliver on the real corpus."""
import re, hashlib, time
from pathlib import Path
from collections import defaultdict, Counter

DL = Path.home() / "Downloads"
files = [p for p in DL.iterdir() if p.is_file() and p.name != ".DS_Store"]
print(f"corpus: {len(files)} files\n", flush=True)

# ---------- 1. EXACT DUPLICATES (content hash) ----------
t0 = time.time()
bysize = defaultdict(list)
for p in files:
    try: bysize[p.stat().st_size].append(p)
    except Exception: pass
h = defaultdict(list)
hashed = 0
for sz, group in bysize.items():
    if len(group) < 2: continue            # only hash size-collisions
    for p in group:
        try:
            d = hashlib.sha256()
            with open(p, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""): d.update(chunk)
            h[d.hexdigest()].append(p); hashed += 1
        except Exception: pass
dupes = {k: v for k, v in h.items() if len(v) > 1}
wasted = sum(v[0].stat().st_size * (len(v) - 1) for v in dupes.values())
dup_files = sum(len(v) - 1 for v in dupes.values())
print(f"1. EXACT DUPLICATES     {time.time()-t0:5.1f}s  (hashed only {hashed} size-collisions)")
print(f"   {len(dupes)} duplicate sets, {dup_files} redundant files, "
      f"{wasted/1e6:.0f} MB reclaimable")
for k, v in sorted(dupes.items(), key=lambda kv: -len(kv[1]))[:4]:
    print(f"     ×{len(v)}  {v[0].name[:64]}")
print(flush=True)

# ---------- 2. VERSION CHAINS (same stem, (n) / v2 / final / copy) ----------
VER = re.compile(r'\s*(\(\d+\)|copy( \d+)?|v\d+|final\d*|updated?|draft\d*|\d+)\s*$', re.I)
def stem_key(name):
    s = Path(name).stem
    prev = None
    while s != prev:
        prev = s; s = VER.sub("", s).strip()
    return (s.lower(), Path(name).suffix.lower())

chains = defaultdict(list)
for p in files: chains[stem_key(p.name)].append(p)
chains = {k: v for k, v in chains.items() if len(v) > 1}
chain_files = sum(len(v) for v in chains.values())
print(f"2. VERSION CHAINS")
print(f"   {len(chains)} chains covering {chain_files} files "
      f"({100*chain_files/len(files):.0f}% of corpus)")
for k, v in sorted(chains.items(), key=lambda kv: -len(kv[1]))[:5]:
    print(f"     ×{len(v):<3} {k[0][:58]}{k[1]}")
print(flush=True)

# ---------- 3. PHOTO EVENTS (EXIF time, +GPS) ----------
from PIL import Image, ExifTags
try:
    import pillow_heif; pillow_heif.register_heif_opener()
except Exception: pass
T = {v: k for k, v in ExifTags.TAGS.items()}
IMG = {".jpg", ".jpeg", ".png", ".heic", ".tif", ".tiff", ".webp"}
imgs = [p for p in files if p.suffix.lower() in IMG]
t0 = time.time(); stamps = []; with_cam = 0; with_gps = 0
for p in imgs:
    try:
        im = Image.open(p); ex = im.getexif()
        dt = ex.get(T.get("DateTimeOriginal")) or ex.get(T.get("DateTime"))
        cam = ex.get(T.get("Make"))
        gps = bool(ex.get_ifd(0x8825))
        if cam: with_cam += 1
        if gps: with_gps += 1
        if dt:
            ts = time.mktime(time.strptime(str(dt)[:19], "%Y:%m:%d %H:%M:%S"))
            stamps.append((ts, p, bool(cam)))
    except Exception: pass
stamps.sort()
GAP = 4 * 3600          # Microsoft patent worked example: 4 hours
events, cur = [], []
for i, (ts, p, cam) in enumerate(stamps):
    if cur and ts - cur[-1][0] > GAP: events.append(cur); cur = []
    cur.append((ts, p, cam))
if cur: events.append(cur)
multi = [e for e in events if len(e) > 1]
print(f"3. PHOTO EVENTS         {time.time()-t0:5.1f}s")
print(f"   {len(imgs)} images · {with_cam} with camera EXIF · {with_gps} with GPS · "
      f"{len(stamps)} with timestamps")
print(f"   → {len(events)} events, {len(multi)} multi-photo "
      f"({sum(len(e) for e in multi)} images grouped)")
for e in sorted(multi, key=len, reverse=True)[:4]:
    d = time.strftime("%Y-%m-%d", time.localtime(e[0][0]))
    print(f"     {len(e):>3} photos  {d}   e.g. {e[0][1].name[:44]}")
print(flush=True)

total = dup_files + chain_files + sum(len(e) for e in multi)
print("=" * 66)
print(f"FILES THE GRAPH ACTS ON WITH ZERO AI: {total} / {len(files)} = {100*total/len(files):.0f}%")
print("=" * 66)
