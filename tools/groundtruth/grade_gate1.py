"""Grade a gate run against the owner's corrected key. Aggregates only, never rows.

`00` AMENDMENT 29 BROUGHT THIS FILE INTO THE REPOSITORY. It lived in
`.groundtruth/`, which `.gitignore:32` excludes to protect the corpus and the
answer key -- so the logic behind a number quoted in `106` §0 and `108` §5 could
not be reviewed or diffed, and a fix to it died with the session that made it.

**WHAT IS TRACKED AND WHAT IS NOT, and the split is the point.** This file is the
LOGIC and is tracked. Three things stay ignored beside the corpus, because they
are the owner's own material rather than this product's:

  `.groundtruth/answerkey2.json`   their labels, per file
  `.groundtruth/keymap.json`       their key vocabulary -> the library's kinds
  the corpus itself

`keymap.json` used to be a dict literal in this file. Tracking it verbatim would
have committed a list naming the kinds of material the owner keeps -- health
records, immigration documents, travel -- which is a disclosure this file does not
need to make in order to be reviewable. It is read from beside the key instead.

**IT PRINTS AGGREGATES AND NEVER A ROW.** No filename, no folder name, no course
code reaches stdout: `108` §7's rule, and the reason this can be run by anyone who
has the corpus without it leaking anything about the corpus.

Usage:  python -m tools.groundtruth.grade_gate1 [scan.sqlite] [groundtruth_dir]
"""
import json, os, sqlite3, sys
from pathlib import Path
from collections import Counter

#: Default: the repository's own ignored corpus directory.
_GROUNDTRUTH = Path(sys.argv[2]) if len(sys.argv) > 2 else (
    Path(__file__).resolve().parents[2] / ".groundtruth")

db = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
    "~/.graph-agent/lead/corpus2-gate1/scan.sqlite")
c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
key = json.loads((_GROUNDTRUTH / "answerkey2.json").read_text())
name_of = dict(c.execute("select file_id, filename from files"))
#: The owner's key vocabulary -> the library's kinds. `00` amendment 30 rules that
#: site G names a KIND, so a set of kinds is the right unit on the right-hand side
#: and this bridge holds what it should. `108` §5 called it a prefix fallback that
#: would score a disagreement as a match; there is no prefix matching here and
#: never was -- the test below is exact set membership.
MAP = {situation: set(kinds) for situation, kinds
       in json.loads((_GROUNDTRUTH / "keymap.json").read_text()).items()}
cur = {fid: (b, p) for fid, b, p in c.execute("select file_id, basis, protected from classifications where superseded_by is null order by observed_at")}
# 1. protection
pg = Counter(); miss = Counter(); over = Counter(); miss_kinds = Counter()
for fid, name in name_of.items():
    k = key.get(name)
    if not k: continue
    b, p = cur.get(fid, ("none", None))
    if k["protected"]:
        if p == 1: pg["protected caught"] += 1
        else: pg["protected MISSED"] += 1; miss[b] += 1; miss_kinds[k["situation"]] += 1
    else:
        if p == 1: pg["ordinary over-protected"] += 1; over[b] += 1
        else: pg["ordinary right"] += 1
print("PROTECTION:", sorted(pg.items())); print("  misses by basis:", miss.most_common(), "| by key situation:", miss_kinds.most_common())
print("  over-protections by basis:", over.most_common())
print("  rows by basis/protected:", c.execute("select basis, protected, count(*) from classifications where superseded_by is null group by 1,2").fetchall())
# 2. cloud sends vs key
sent = set()
for (fid,) in c.execute("""select distinct d.subject_ref from llm_dossier d join llm_call_usage u using(dossier_id)
      join release_ledger r on r.release_id=u.release_id where r.model_target like '%cloud%'"""):
    sent.add(fid)
leak = [name_of[f] for f in sent if key.get(name_of.get(f), {}).get("protected")]
print("CLOUD: files sent", len(sent), "| key-protected among them:", len(leak))
# 3. gate answers
g = Counter()
for fid, resp, out in c.execute("""select d.subject_ref, r.response_bytes, v.outcome from llm_dossier d join llm_response r using(dossier_id)
      join llm_verdict v using(dossier_id) where d.call_site='H_restricted_kind'"""):
    k = key.get(name_of.get(fid)); 
    try: kind = json.loads(resp.decode())["claims"][0]["payload"].get("restricted_kind")
    except Exception: kind = "?"
    if not k: continue
    g[("key protected" if k["protected"] else "key ordinary", "named kind" if kind not in (None, "none_of_these", "?") else kind, out)] += 1
print("GATE:", sorted(g.items()))
# 4. situation answers
s = Counter()
for fid, resp, out, tgt in c.execute("""select d.subject_ref, r.response_bytes, v.outcome, (select model_target from release_ledger where release_id=r.release_id) from llm_dossier d join llm_response r using(dossier_id)
      join llm_verdict v using(dossier_id) where d.call_site='G_situation_sensitivity'"""):
    k = key.get(name_of.get(fid))
    try: ans = json.loads(resp.decode())["claims"][0]["payload"].get("situation")
    except Exception: ans = "?"
    if not k: continue
    where = "cloud" if tgt and "cloud" in tgt else "local"
    if ans in ("none", "none_of_these", None): s[(where, "none")] += 1
    elif ans in MAP[k["situation"]]: s[(where, "right")] += 1
    else: s[(where, "wrong")] += 1
print("SITUATION:", sorted(s.items()))
print("FAILURES:", c.execute("select failure_class, substr(explanation,1,60), count(*) from llm_call_failure group by 1,2").fetchall())
print("FACTS:", c.execute("select field_key, count(*) from file_facts where active=1 and superseded_by is null group by 1 order by 2 desc").fetchall()[:8])
