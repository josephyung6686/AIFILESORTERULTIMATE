"""The escalation ladder. How many images survive to the expensive level?
L1 OCR (local) -> L2 Vision classify (local) -> L3 semantic (costs money).
Also: does threading help?"""
import time, re, sys
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import Vision
from Foundation import NSURL

HOME=Path.home(); IMG={'.png','.jpg','.jpeg','.heic','.webp','.tif'}
files=[]
for s in (HOME/"Downloads",HOME/"Desktop",HOME/"Documents"):
    if s.exists():
        try: files+=[f for f in s.iterdir() if f.is_file() and f.suffix.lower() in IMG]
        except Exception: pass
print(f"{len(files)} images\n", flush=True)

def probe(p):
    """One pass: OCR + classify + faces. Returns (ocr_chars, top_label, conf, faces)."""
    try:
        url=NSURL.fileURLWithPath_(str(p))
        h=Vision.VNImageRequestHandler.alloc().initWithURL_options_(url,None)
        tr=Vision.VNRecognizeTextRequest.alloc().init()
        tr.setRecognitionLevel_(1)               # 1 = fast
        cr=Vision.VNClassifyImageRequest.alloc().init()
        fr=Vision.VNDetectFaceRectanglesRequest.alloc().init()
        ok,_=h.performRequests_error_([tr,cr,fr],None)
        if not ok: return None
        txt="".join((o.topCandidates_(1)[0].string() or "")+" "
                    for o in (tr.results() or []) if o.topCandidates_(1))
        res=cr.results() or []
        lab,conf=(res[0].identifier(),res[0].confidence()) if res else (None,0.0)
        return len(txt.strip()), lab, conf, len(fr.results() or [])
    except Exception:
        return None

W=int(sys.argv[1]) if len(sys.argv)>1 else 8
t0=time.time()
with ThreadPoolExecutor(max_workers=W) as ex:
    out=list(ex.map(probe, files))
el=time.time()-t0

OCR_MIN=25; CONF_MIN=0.5
l1=l2=l3=err=0; labs=Counter()
for r in out:
    if r is None: err+=1; continue
    chars,lab,conf,faces=r
    if chars>=OCR_MIN: l1+=1
    elif lab and conf>=CONF_MIN: l2+=1; labs[lab]+=1
    else: l3+=1
n=len(files)
print(f"WALL {el:.1f}s with {W} threads  ({1000*el/n:.0f} ms/image effective)\n")
print(f"  L1  OCR gave >={OCR_MIN} chars  → text IS the content   {l1:>4}  ({100*l1/n:.0f}%)")
print(f"  L2  no text, label >={CONF_MIN}  → coarse kind is enough {l2:>4}  ({100*l2/n:.0f}%)")
print(f"  L3  NEITHER → needs real semantics                      {l3:>4}  ({100*l3/n:.0f}%)")
print(f"      unreadable                                          {err:>4}")
print(f"\n  L2 labels: {', '.join(f'{k} {v}' for k,v in labs.most_common(8))}")
