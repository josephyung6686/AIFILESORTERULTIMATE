import time, sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import Vision
from Foundation import NSURL

HOME=Path.home(); IMG={'.png','.jpg','.jpeg','.heic','.webp','.tif'}
files=[]
for s in (HOME/"Downloads",HOME/"Desktop",HOME/"Documents"):
    if s.exists():
        try: files+=[f for f in s.iterdir() if f.is_file() and f.suffix.lower() in IMG]
        except Exception: pass
sample=files[:70]

def probe(p):
    try:
        h=Vision.VNImageRequestHandler.alloc().initWithURL_options_(NSURL.fileURLWithPath_(str(p)),None)
        tr=Vision.VNRecognizeTextRequest.alloc().init(); tr.setRecognitionLevel_(1)
        cr=Vision.VNClassifyImageRequest.alloc().init()
        h.performRequests_error_([tr,cr],None)
    except Exception: pass

for w in (1,4,8,12):
    t=time.time()
    with ThreadPoolExecutor(max_workers=w) as ex: list(ex.map(probe,sample))
    el=time.time()-t
    print(f"  {w:>2} threads   {el:6.1f}s   {1000*el/len(sample):>5.0f} ms/img   "
          f"→ full 655 = {el*655/len(sample)/60:.1f} min")
