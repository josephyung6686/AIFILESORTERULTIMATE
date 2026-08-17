"""Static embeddings (Model2Vec) on the REAL corpus: speed + does clustering still work?"""
import time, re, json
from pathlib import Path
import numpy as np

DL = Path.home() / "Downloads"
files = [p for p in DL.iterdir() if p.is_file() and p.name != ".DS_Store"]
DUP = re.compile(r"\s*\((\d+)\)$"); SEP = re.compile(r"[_\-.]+")


def clean(n):
    s = DUP.sub("", Path(n).stem)
    s = SEP.sub(" ", s)
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", s)
    return re.sub(r"\s+", " ", s).strip()


names = [p.name for p in files]
texts = [clean(n) for n in names]
exts = [p.suffix.lower().lstrip(".") for p in files]
print(f"files: {len(texts)}", flush=True)

from model2vec import StaticModel

MODEL = "minishlab/potion-multilingual-128M"
t0 = time.time(); m = StaticModel.from_pretrained(MODEL); load = time.time() - t0
t0 = time.time(); vecs = m.encode(texts).astype(np.float32); dt = time.time() - t0
print(f"{MODEL}\n  load={load:.2f}s  encode={dt:.3f}s  {len(texts)/dt:,.0f}/s  dim={vecs.shape[1]}", flush=True)

vecs /= np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-9

K = 10
t0 = time.time()
sim = vecs @ vecs.T; np.fill_diagonal(sim, -1.0)
nn = np.argpartition(-sim, K, axis=1)[:, :K]
nbr = [set(r.tolist()) for r in nn]
edges, w = [], []
for i in range(len(nbr)):
    for j in nbr[i]:
        if j > i and i in nbr[j]:
            edges.append((i, int(j))); w.append(float(sim[i, j]))
knn = time.time() - t0

import igraph as ig, leidenalg
t0 = time.time()
g = ig.Graph(n=len(vecs), edges=edges); g.es["weight"] = w
part = leidenalg.find_partition(g, leidenalg.RBConfigurationVertexPartition,
                                weights="weight", resolution_parameter=1.0,
                                seed=42, n_iterations=-1)
leid = time.time() - t0
sizes = sorted((len(c) for c in part), reverse=True)
singles = sum(1 for s in sizes if s == 1)
print(f"  mutual-kNN: {len(edges)} edges {knn:.2f}s  avg_deg={2*len(edges)/len(vecs):.2f}")
print(f"  leiden: {len(part)} communities {leid:.2f}s  singletons={singles} ({100*singles/len(vecs):.1f}%) largest={sizes[0]}")
print(f"  >>> TOTAL WARM PIPELINE: {dt+knn+leid:.2f}s  (vs 166s with neural embeddings)\n", flush=True)

comms = sorted([c for c in part if len(c) >= 4], key=len, reverse=True)
print(f"=== top communities ({len(comms)} with >=4 files) ===\n")
for ci, c in enumerate(comms[:14]):
    ex = {}
    for i in c: ex[exts[i]] = ex.get(exts[i], 0) + 1
    es = ",".join(f"{k}:{v}" for k, v in sorted(ex.items(), key=lambda x: -x[1])[:3])
    print(f"[{ci}] n={len(c)} ({es})")
    for i in list(c)[:5]: print(f"      {names[i][:76]}")
    print(flush=True)
