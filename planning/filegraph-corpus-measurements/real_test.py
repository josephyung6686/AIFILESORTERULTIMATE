"""Run the proposed pipeline on the REAL Downloads corpus: embed -> mutual-kNN -> Leiden."""
import os, re, time, json, sys
from pathlib import Path
import numpy as np

DL = Path.home() / "Downloads"
files = [p for p in DL.iterdir() if p.is_file() and p.name != ".DS_Store"]
print(f"files: {len(files)}", flush=True)

DUP = re.compile(r"\s*\((\d+)\)$")
SEP = re.compile(r"[_\-.]+")


def clean(name: str) -> str:
    stem = Path(name).stem
    stem = DUP.sub("", stem)                 # strip (1) (2) duplicate markers
    stem = SEP.sub(" ", stem)
    stem = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", stem)  # camelCase split
    stem = re.sub(r"\s+", " ", stem).strip()
    return stem


texts, names, exts = [], [], []
for p in files:
    texts.append(clean(p.name))
    names.append(p.name)
    exts.append(p.suffix.lower().lstrip("."))

# ---- embed ----
from fastembed import TextEmbedding

MODEL = os.environ.get("EMB_MODEL", "intfloat/multilingual-e5-small")
t0 = time.time()
emb = TextEmbedding(model_name=MODEL)
load_s = time.time() - t0
print(f"model={MODEL} load={load_s:.2f}s", flush=True)

t0 = time.time()
vecs = np.array(list(emb.embed(texts)), dtype=np.float32)
embed_s = time.time() - t0
print(f"embedded {len(vecs)} in {embed_s:.2f}s  ({len(vecs)/embed_s:.0f}/s)  dim={vecs.shape[1]}", flush=True)

vecs /= np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-9

# ---- mutual kNN graph ----
K = int(os.environ.get("K", 10))
t0 = time.time()
sim = vecs @ vecs.T
np.fill_diagonal(sim, -1.0)
nn = np.argpartition(-sim, K, axis=1)[:, :K]
nbr = [set(row.tolist()) for row in nn]
edges, weights = [], []
for i in range(len(nbr)):
    for j in nbr[i]:
        if j > i and i in nbr[j]:          # MUTUAL kNN only -> sparsity
            edges.append((i, int(j)))
            weights.append(float(sim[i, j]))
knn_s = time.time() - t0
print(f"mutual-kNN(k={K}): {len(edges)} edges in {knn_s:.2f}s  avg_degree={2*len(edges)/len(vecs):.2f}", flush=True)

# ---- Leiden ----
import igraph as ig, leidenalg
t0 = time.time()
g = ig.Graph(n=len(vecs), edges=edges)
g.es["weight"] = weights
part = leidenalg.find_partition(
    g, leidenalg.RBConfigurationVertexPartition,
    weights="weight", resolution_parameter=float(os.environ.get("RES", 1.0)),
    seed=42, n_iterations=-1,
)
leiden_s = time.time() - t0
sizes = sorted((len(c) for c in part), reverse=True)
singles = sum(1 for s in sizes if s == 1)
print(f"leiden: {len(part)} communities in {leiden_s:.2f}s  "
      f"singletons={singles} ({100*singles/len(vecs):.1f}%)  largest={sizes[0]}", flush=True)
print(f"TOTAL PIPELINE: {load_s+embed_s+knn_s+leiden_s:.2f}s "
      f"(warm, excl. model load: {embed_s+knn_s+leiden_s:.2f}s)", flush=True)

# ---- show real communities ----
comms = sorted([c for c in part if len(c) >= 3], key=len, reverse=True)
print(f"\n=== {len(comms)} communities with >=3 files ===\n", flush=True)
for ci, c in enumerate(comms[:22]):
    ex = {}
    for i in c:
        ex[exts[i]] = ex.get(exts[i], 0) + 1
    extstr = ",".join(f"{k}:{v}" for k, v in sorted(ex.items(), key=lambda x: -x[1])[:4])
    print(f"[{ci}] n={len(c)}  ({extstr})")
    for i in list(c)[:6]:
        print(f"      {names[i][:78]}")
    print(flush=True)

json.dump({"n": len(vecs), "load_s": load_s, "embed_s": embed_s, "knn_s": knn_s,
           "leiden_s": leiden_s, "communities": len(part), "singletons": singles,
           "edges": len(edges)}, open("real_test_result.json", "w"), indent=2)
