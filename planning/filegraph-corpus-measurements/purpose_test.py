"""Does PURPOSE grouping surface recognisable ACTIVITIES that content similarity cannot see?
Test: group by download session, then look at the file-TYPE constellation.
Mixed-type sessions are exactly where content similarity fails."""
import re, time
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

HOME = Path.home()
SRC = [HOME/"Downloads", HOME/"Desktop", HOME/"Documents"]
files=[]
for s in SRC:
    if s.exists():
        try: files += [f for f in s.iterdir() if f.is_file() and not f.name.startswith(".")]
        except Exception: pass

mt={f: f.stat().st_mtime for f in files}
srt=sorted(files, key=lambda f: mt[f])

# sessions: gap <= 20 min
sess=[]; cur=[srt[0]]
for a,b in zip(srt, srt[1:]):
    if mt[b]-mt[a] <= 1200: cur.append(b)
    else:
        if len(cur)>=4: sess.append(cur)
        cur=[b]
if len(cur)>=4: sess.append(cur)

FAM={'.pdf':'doc','.docx':'doc','.doc':'doc','.txt':'doc','.md':'doc','.pptx':'slides',
     '.xlsx':'sheet','.csv':'sheet','.png':'img','.jpg':'img','.jpeg':'img','.heic':'img',
     '.webp':'img','.gif':'img','.mp4':'video','.mov':'video','.avi':'video',
     '.mp3':'audio','.wav':'audio','.m4a':'audio','.zip':'archive','.dmg':'app','.pkg':'app',
     '.py':'code','.ipynb':'code','.js':'code','.json':'code','.html':'code'}

print(f"{len(files)} loose files → {len(sess)} sessions of 4+\n")
print("="*80)
print("MIXED-TYPE SESSIONS — where content similarity has nothing to work with")
print("="*80)

mixed=[]
for s in sess:
    fams={FAM.get(f.suffix.lower(),'other') for f in s}
    fams.discard('other')
    if len(fams)>=2: mixed.append((s,fams))
mixed.sort(key=lambda x:-len(x[0]))

print(f"\n{len(mixed)} of {len(sess)} sessions span 2+ file families "
      f"({100*len(mixed)/max(len(sess),1):.0f}%)\n")

for s,fams in mixed[:9]:
    when=datetime.fromtimestamp(mt[s[0]]).strftime("%Y-%m-%d %H:%M")
    span=(mt[s[-1]]-mt[s[0]])/60
    ext=Counter(f.suffix.lower().lstrip('.') for f in s)
    print(f"  [{when}]  {len(s)} files over {span:.0f} min   families: {', '.join(sorted(fams))}")
    print(f"      {', '.join(f'{k}:{v}' for k,v in ext.most_common(5))}")
    for f in s[:5]: print(f"      · {f.name[:70]}")
    if len(s)>5: print(f"      · … {len(s)-5} more")
    print()

# ---- era clustering: does mtime separate life periods? ----
print("="*80)
print("TIME ERAS — do the files cluster into life periods?")
print("="*80 + "\n")
years=Counter(datetime.fromtimestamp(mt[f]).year for f in files)
for y in sorted(years):
    bar="#"*int(60*years[y]/max(years.values()))
    print(f"  {y}  {years[y]:>5}  {bar}")
