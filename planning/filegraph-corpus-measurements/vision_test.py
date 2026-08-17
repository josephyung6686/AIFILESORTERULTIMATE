"""If OCR returns nothing and it's a real photo — can macOS tell us WHAT it is,
locally, for free? VNClassifyImageRequest + face detection."""
import time, re
from pathlib import Path
from collections import Counter
import Vision
from Foundation import NSURL
from PIL import Image
import pillow_heif; pillow_heif.register_heif_opener()

HOME=Path.home()
IMG={'.png','.jpg','.jpeg','.heic','.webp','.tif'}
SCREENS={(1170,2532),(1179,2556),(1290,2796),(1284,2778),(1125,2436),(828,1792),
 (1920,1080),(2560,1440),(3840,2160),(1440,900),(2880,1800),(1512,982),(1728,1117),
 (3024,1964),(3456,2234),(2056,1329),(1366,768),(1280,800),(2732,2048),(2388,1668)}

files=[]
for s in (HOME/"Downloads",HOME/"Desktop",HOME/"Documents"):
    if s.exists():
        try: files+=[f for f in s.iterdir() if f.is_file() and f.suffix.lower() in IMG]
        except Exception: pass

# the AMBIGUOUS set: no camera EXIF, not screen-sized, not named screenshot
amb=[]
for f in files:
    try:
        with Image.open(f) as im:
            w,h=im.size
            ex=getattr(im,"_getexif",lambda:None)() or {}
            cam=any(k in ex for k in (271,272,37386))
    except Exception: continue
    if cam: continue
    if (w,h) in SCREENS or (h,w) in SCREENS: continue
    if re.search(r'screenshot|screen shot|cleanshot',f.name,re.I): continue
    amb.append(f)

print(f"ambiguous images (no camera EXIF, not screen-sized): {len(amb)}\n")

def classify(p):
    url=NSURL.fileURLWithPath_(str(p))
    h=Vision.VNImageRequestHandler.alloc().initWithURL_options_(url,None)
    cr=Vision.VNClassifyImageRequest.alloc().init()
    fr=Vision.VNDetectFaceRectanglesRequest.alloc().init()
    ok,err=h.performRequests_error_([cr,fr],None)
    if not ok: return None,0
    res=cr.results() or []
    labs=[(o.identifier(),o.confidence()) for o in res if o.confidence()>0.15][:4]
    return labs, len(fr.results() or [])

sample=amb[:45]
t0=time.time(); toplabs=Counter(); withface=0; shown=0
for p in sample:
    labs,nf=classify(p)
    if labs is None: continue
    if nf: withface+=1
    if labs: toplabs[labs[0][0]]+=1
    if shown<14:
        shown+=1
        tag=f"  {nf} face(s)" if nf else ""
        print(f"  {p.name[:48]:<50} {', '.join(f'{l} {c:.2f}' for l,c in labs[:3])}{tag}")
el=time.time()-t0
print(f"\n  {el:.1f}s for {len(sample)} images = {1000*el/len(sample):.0f} ms/image")
print(f"  images containing faces: {withface}/{len(sample)}")
print(f"\n  top labels across sample:")
for l,c in toplabs.most_common(12): print(f"    {l:<28} {c}")
