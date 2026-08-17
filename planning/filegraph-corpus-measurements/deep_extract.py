"""Proper per-format extraction. Shows what the 68s run SHOULD have produced
for the internship session it skipped."""
import re, zipfile, json, time
from pathlib import Path
from datetime import datetime

HOME=Path.home()
TAG=re.compile(r'<[^>]+>'); WS=re.compile(r'[ \t]*\n[ \t\n]*')

def ooxml_text(p, parts):
    """docx/xlsx/pptx are ZIPs of XML. Strip tags. No library needed."""
    out=[]
    try:
        with zipfile.ZipFile(p) as z:
            names=[n for n in z.namelist() if any(re.match(pat,n) for pat in parts)]
            for n in sorted(names):
                xml=z.read(n).decode('utf8','ignore')
                xml=re.sub(r'</(w:p|a:p|w:tr|row)>','\n',xml)
                xml=re.sub(r'</(w:tc|a:t|c|v|t)>',' ',xml)
                out.append(TAG.sub('',xml))
    except Exception as e:
        return f"[unreadable: {e}]"
    return WS.sub('\n'," ".join(out)).strip()

def extract(p):
    e=p.suffix.lower()
    if e=='.pdf':
        import pypdfium2 as pdfium
        d=pdfium.PdfDocument(str(p))
        t="".join(d[i].get_textpage().get_text_range() for i in range(len(d))); d.close(); return t
    if e=='.docx': return ooxml_text(p,[r'word/document\.xml',r'word/header'])
    if e=='.xlsx': return ooxml_text(p,[r'xl/sharedStrings\.xml',r'xl/worksheets/sheet\d+\.xml'])
    if e=='.pptx': return ooxml_text(p,[r'ppt/slides/slide\d+\.xml',r'ppt/notesSlides/'])
    if e in ('.txt','.md','.csv','.py','.js','.html','.json'):
        return p.read_text('utf8','ignore')
    if e=='.ipynb':
        nb=json.loads(p.read_text('utf8','ignore'))
        return "\n".join("".join(c.get('source',[])) for c in nb.get('cells',[]))
    if e=='.zip':
        with zipfile.ZipFile(p) as z: return "MANIFEST:\n"+"\n".join(z.namelist()[:200])
    return None

# ---------- facts ----------
PAT={
 'course_code': re.compile(r'\b([A-Z]{2,5})\s?-?\s?(\d{3,4})\b'),
 'org_domain' : re.compile(r'\b[\w.+-]+@([\w-]+\.[\w.-]+)\b'),
 'person'     : re.compile(r'\b(?:Name|Full Name|Applicant)\s*[:：]\s*([A-Z][\w\'-]+(?: [A-Z][\w\'-]+){0,3})'),
 'company'    : re.compile(r'\b([A-Z][A-Za-z&.\-]+(?: [A-Z][A-Za-z&.\-]+){0,3})\s+(?:Limited|Ltd|Inc|LLC|Holdings|Securities|Capital|Group|Bank)\b'),
 'doc_kind'   : re.compile(r'\b(questionnaire|declaration|consent|statement|agreement|contract|offer letter|resume|curriculum vitae|invoice|receipt|application form|handbook|policy)\b', re.I),
 'date_iso'   : re.compile(r'\b(20\d{2})[-/](\d{1,2})[-/](\d{1,2})\b'),
 'money'      : re.compile(r'\b(?:HK\$|US\$|\$|USD|HKD)\s?[\d,]+(?:\.\d\d)?\b'),
}
JUNK={'gmail.com','outlook.com','hotmail.com','yahoo.com','icloud.com','w3.org',
      'openxmlformats.org','adobe.com','schemas.microsoft.com','purl.org'}

def facts(name, text):
    hay=f"{name}\n{text}"; out={}
    for k,rx in PAT.items():
        vals=[]
        for m in rx.finditer(hay):
            v=m.group(0) if k in ('date_iso','money') else (m.group(1) if m.lastindex else m.group(0))
            if k=='course_code': v=f"{m.group(1)}{m.group(2)}"
            if k=='org_domain' and v.lower() in JUNK: continue
            vals.append(v.strip())
        if vals:
            seen=[]; 
            for v in vals:
                if v not in seen: seen.append(v)
            out[k]=seen[:5]
    return out

# ---------- run on the internship session ----------
TARGET=datetime(2026,3,19).date()
cands=[]
for s in (HOME/"Downloads", HOME/"Desktop", HOME/"Documents"):
    if s.exists():
        for f in s.iterdir():
            try:
                if f.is_file() and datetime.fromtimestamp(f.stat().st_mtime).date()==TARGET:
                    cands.append(f)
            except Exception: pass
cands.sort(key=lambda f:f.stat().st_mtime)

print(f"THE SESSION THE 68s RUN SKIPPED  —  {len(cands)} files on 2026-03-19\n")
print("="*78)
t0=time.time()
for f in cands[:9]:
    try: text=extract(f)
    except Exception as ex: text=f"[error {ex}]"
    if text is None:
        print(f"\n  {f.name[:66]}")
        print(f"      {f.suffix} → no extractor · filename + mtime only"); continue
    fx=facts(f.name,text)
    print(f"\n  {f.name[:66]}")
    print(f"      {len(text):,} chars extracted")
    for k,v in fx.items():
        print(f"      {k:<12} {', '.join(str(x)[:38] for x in v[:4])}")
print("\n"+"="*78)
print(f"  {time.time()-t0:.2f} s for {len(cands[:9])} files")
