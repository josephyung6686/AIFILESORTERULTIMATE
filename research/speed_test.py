"""Is 12/s a real limit or a misconfiguration? Test threads + batch + model choice."""
import time, os, re
from pathlib import Path
import numpy as np
from fastembed import TextEmbedding

DL = Path.home() / "Downloads"
files = [p.name for p in DL.iterdir() if p.is_file() and p.name != ".DS_Store"]
DUP = re.compile(r"\s*\((\d+)\)$"); SEP = re.compile(r"[_\-.]+")
texts = [re.sub(r"\s+", " ", SEP.sub(" ", DUP.sub("", Path(n).stem))).strip() for n in files]
texts = texts[:600]
print(f"corpus: {len(texts)} short strings\n", flush=True)

CANDIDATES = [
    ("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", "multilingual, 384d, 12 layers"),
    ("BAAI/bge-small-en-v1.5", "ENGLISH ONLY, 384d — speed reference"),
]

for model_name, note in CANDIDATES:
    for threads in (None, 8):
        for bs in (32, 256):
            try:
                t0 = time.time()
                emb = TextEmbedding(model_name=model_name, threads=threads)
                load = time.time() - t0
                # warm up
                list(emb.embed(texts[:8], batch_size=bs))
                t0 = time.time()
                v = np.array(list(emb.embed(texts, batch_size=bs)), dtype=np.float32)
                dt = time.time() - t0
                print(f"{model_name.split('/')[-1]:<45} threads={str(threads):<5} bs={bs:<4} "
                      f"load={load:6.2f}s  embed={dt:6.2f}s  {len(texts)/dt:7.1f}/s   [{note}]", flush=True)
            except Exception as e:
                print(f"{model_name} threads={threads} bs={bs} FAILED: {type(e).__name__}: {e}", flush=True)
        note = ""
