import json
from pathlib import Path

D = Path("/Users/jy/GRAPH AGENT/planning/deferred-catalogues")
OUT = D / "07-archive-recognizable-markers.json"

# The source-code half is DERIVED from catalogue 05 so the two files cannot drift.
cat05 = json.loads((D / "05-repository-markers.json").read_text())

CODE_SOURCE_IDS_EXTRA = {"p5r-src", "p5r-__init__-py", "p5r-py-typed", "p5r-git",
                         "p5r-gitignore", "p5r-gitmodules", "p5r-dockerfile"}

CITE25 = ("§2.5 \"A source-code archive may reveal a `README.md`, `package.json`, `src` directory, "
          "or Python package layout and can be recognized as a code project.\"")
CITE25_DOC = ("§2.5 \"A ZIP file named `submission.zip` may contain a transcript, personal statement, "
              "resume, certificate, and form, which is meaningful evidence of a purpose-defined "
              "application packet even when the outer archive name is vague.\"")

manifests = []
for e in cat05["p5_evidence_markers"]:
    take = e["kind"] in ("package manifest", "README file") or e["id"] in CODE_SOURCE_IDS_EXTRA
    if not take:
        continue
    applies = "member_path_segment" if e["applies_to"] == "directory_name" else "member_basename"
    origin = ("§2.5 names this literally as one of the four things a source-code archive may reveal. "
              if e["match"] in ("README.md", "package.json", "src")
              else "")
    manifests.append({
        "id": "arc-" + e["id"].split("-", 1)[1],
        "match": e["match"],
        "match_kind": "exact",
        "case_sensitive": e["case_sensitive"],
        "kind": "source-code manifest",
        "applies_to": applies,
        "rationale": (origin + "Derived from catalogue 05 row `" + e["id"] + "` — the two files share one "
                      "source so they cannot drift. Re-kinded to `source-code manifest` because P5's "
                      "`MARKER_KINDS` offers exactly two classes for archives."),
        "design_cite": CITE25,
        "false_positive_risk": e["false_positive_risk"],
        "example_true": ("project/" + e["match"]) if applies == "member_basename" else ("project/" + e["match"] + "/main.py"),
        "example_false": "notes/" + e["match"] + ".bak",
    })

# The five document names section 2.5 states, and nothing beyond them.
DOCS = [
  ("transcript", ["transcript", "transcripts"],
   "Named literally by §2.5's `submission.zip` example."),
  ("personal statement", ["personal statement", "personal-statement", "personalstatement", "statement of purpose"],
   "Named literally by §2.5. `statement of purpose` is included as the same document under its other "
   "standard name — the only synonym admitted anywhere in this array, and it is admitted because it is "
   "the identical artefact, not a related one."),
  ("resume", ["resume", "résumé", "cv", "curriculum vitae"],
   "Named literally by §2.5. `CV` and `curriculum vitae` are the same document; `cv` is matched only as a "
   "whole word so it cannot fire inside `cvs`, `cvx` or a filename fragment."),
  ("certificate", ["certificate", "certification"],
   "Named literally by §2.5."),
  ("form", ["form"],
   "Named literally by §2.5. Highest false-positive risk in this array by a wide margin — `form` appears "
   "in `format`, `formula`, `information`, `transformation` — so it is matched as a whole word only, and "
   "even then it is one weak marker among several. §2.5's own example depends on **five** documents "
   "co-occurring, not on any one of them."),
]

docs = []
for base, variants, note in DOCS:
    docs.append({
        "id": "arc-doc-" + base.replace(" ", "-"),
        "match": " | ".join(variants),
        "match_kind": "regex",
        "pattern": "(?<![a-z])(?:" + "|".join(v.replace(" ", "[ _-]?") for v in variants) + ")(?![a-z])",
        "case_sensitive": False,
        "kind": "document name",
        "applies_to": "member_basename (extension removed), matched as a whole word",
        "rationale": (note + " Matched against the member's basename with separators normalised, because "
                      "real archives spell it `Personal_Statement.pdf`, `personal-statement-final.docx` "
                      "and `PersonalStatement.pdf`. **This is a name match, not a content claim:** the "
                      "marker records that a member is *called* this, and whether the archive is an "
                      "application packet is a purpose fact (§3.9) and P6's."),
        "design_cite": CITE25_DOC,
        "false_positive_risk": "high" if base == "form" else ("medium" if base == "certificate" else "low"),
        "example_true": "submission/Personal_Statement_Final.pdf" if base == "personal statement" else f"submission/{base.title().replace(' ', '_')}.pdf",
        "example_false": "submission/transformation-notes.pdf" if base == "form" else "submission/readme.txt",
    })

doc = {
  "list_id": "archive_recognizable_markers",
  "title": "07 — Archive recognizable markers (P5 E4's `recognize_markers`)",
  "version": "1.0",
  "authored": "2026-08-20",
  "owner": "P5 (injected) — the observations it produces are consumed by P6",
  "consumer": "the caller-supplied `recognize_markers(member_paths) -> tuple[ArchiveMarker, ...]` that P5's `extract_archive` requires. Each marker becomes one observation at `zone = metadata`, `field = <the marker's kind>`, `reliability: direct`, whose `raw_value` is **the member path that carries the marker** — not the marker word.",
  "match_field": "each entry in the archive manifest's member-path list, read from the manifest. `applies_to` says whether a row matches the member's basename or a path segment.",
  "normalization_for_matching": "Basename comparison after Unicode NFC; case-insensitive except where a row says otherwise. Document-name rows additionally strip the extension and treat `_`, `-` and space as equivalent separators. **Nothing is decompressed to perform any of this** — the member paths come from the manifest, and §2.5's absolute prohibition on extraction is not weakened by a single row here.",
  "kind_vocabulary": "P5 defines `MARKER_KINDS = (\"source-code manifest\", \"document name\")` — §2.5's own two classes — and raises `UnknownMarkerKind` on anything else. Every row therefore carries one of exactly those two strings. **A naming stretch worth flagging:** §2.5 names `README.md`, a `src` directory, and \"Python package layout\" as things a source-code archive reveals, and none of them is literally a *manifest*. They are kinded `source-code manifest` anyway, because that is the only code-side class P5 accepts and inventing a third is a runtime error, not a style choice.",
  "design_cites": [
    CITE25,
    CITE25_DOC,
    "§2.5: \"The engine should read and store the archive type, contained paths, filenames, folder names, extensions, file count, uncompressed size where available, and recognizable markers such as source-code manifests or document names.\"",
    "§2.5, the prohibition this file operates under: \"the normal scan should never extract archive contents to the filesystem, because doing so creates security, storage, and side-effect risks.\"",
    "P5 SPEC Deferred: \"Archive 'recognizable markers' beyond the above | §2.5 | That manifests and document names are markers | The marker set\" — this file is the missing column.",
    "P5 PLAN Task 13: `MARKER_KINDS: tuple[str, ...] = (\"source-code manifest\", \"document name\")`; `UnknownMarkerKind` is raised for any other class; \"WHICH files are markers is Deferred … so no member name appears here and the recognizer is caller-supplied.\""
  ],
  "rules": [
    "**Manifest only, never extraction.** Every row matches a *path string* from the archive manifest. Nothing in this file requires reading a member's bytes, and §2.5's prohibition — never extract to the filesystem, never let a nested or oversized archive become a decompression bomb — is absolute and untouched.",
    "**Exactly two kinds.** `source-code manifest` and `document name`. A third value is not a modelling choice, it is `UnknownMarkerKind` at run time.",
    "**The `raw_value` is the member path, not the marker.** P5 PLAN Task 13 emits `raw_value = marker.member_path`, so an archive containing `project/package.json` stores that path verbatim. The kind goes in the field label. This is what keeps the observation a *reading* rather than a conclusion.",
    "**The document-name vocabulary stops at §2.5's five.** transcript, personal statement, resume, certificate, form. Growing it into a general document-type vocabulary is the 200-300 template library, which is §5.7's, deferred, and **P10's** — not this file's, and not something to seed by accident from the archive side.",
    "**Co-occurrence is the evidence, not any single marker.** §2.5's worked case is `submission.zip` containing *five* documents together. One `form` in an archive means very little. E4 emits each marker as its own observation and never counts them; whether five markers together mean an application packet is a purpose fact (§3.9) and P6's.",
    "**No archive-name inference.** §2.5's point is that the outer name `submission.zip` is *vague* and the members are what carry the evidence. Nothing here matches the archive's own filename."
  ],
  "coverage_note": "Two arrays in one list, matching §2.5's two classes. The **source-code manifest** side is derived mechanically from catalogue 05 — the `package manifest` and `README file` rows plus `src`, `__init__.py`, `py.typed`, `.git`, `.gitignore`, `.gitmodules` and `Dockerfile` — so the two catalogues cannot disagree about what a project marker is. The **document name** side is exactly §2.5's five names plus same-document synonyms, and deliberately goes no further.\n\n**What is not here, and why.** Office-format internals (`word/document.xml`, `xl/workbook.xml`, `[Content_Types].xml`) would identify a `.docx` opened as a ZIP — but that is *routing*, and §2.9 gives routing to R \"signature over extension\", not to E4's marker recogniser. Bomb signals are not markers either: §2.5 makes uncompressed size a safety input that E4 already reads from the manifest, and P5 PLAN Task 13 already specifies the `unreadable`/`partial` outcomes.",
  "sources": [
    {"title": "Catalogue 05 — Repository markers and package manifests", "url": "./05-repository-markers.md", "retrieved": "2026-08-20", "note": "The source-code-manifest array below is generated from catalogue 05's `p5_evidence_markers` by `checks/build07.py`. Add a manifest there, not here."},
    {"title": "PKWARE — APPNOTE.TXT, the .ZIP File Format Specification", "url": "https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT", "retrieved": "2026-08-20", "note": "The central-directory structure that makes manifest-only inspection possible — member paths and uncompressed sizes are readable without decompressing any entry, which is what §2.5's prohibition relies on."},
    {"title": "Python — zipfile.ZipFile.namelist / infolist", "url": "https://docs.python.org/3/library/zipfile.html", "retrieved": "2026-08-20", "note": "The stdlib surface a caller's `read_manifest` would use to produce member paths and declared sizes without extraction."}
  ],
  "injection": "`extract_archive(..., read_manifest=…, recognize_markers=make_archive_recognizer(load('07-archive-recognizable-markers.json')))`. P5 PLAN Task 13 is explicit that \"no member name appears here and the recognizer is caller-supplied\", and Task 20's runtime-introspection guard asserts that no marker file name exists in any module-level container inside `src/extractors/`. E4 additionally validates every returned `kind` against `MARKER_KINDS` and raises `UnknownMarkerKind` otherwise, so a malformed catalogue fails loudly at the boundary rather than silently producing a bad observation.",
  "entries": manifests + docs,
  "refused": [
    {"id": "ref-office-internals", "match": "word/document.xml, xl/workbook.xml, ppt/presentation.xml, [Content_Types].xml", "match_kind": "exact", "case_sensitive": True,
     "kind": "source-code manifest", "applies_to": "member_path_segment",
     "rationale": "These would let E4 recognise that a `.docx` opened as a ZIP is really a Word document. That is real information and it belongs somewhere else: §2.9 assigns routing to R, \"inspect the real MIME type or file signature where possible, and dispatch each file to a type-specific extractor\", and P5 SPEC Done-means 10 requires \"routing follows signature over extension\". Putting it here would put the routing decision in the marker recogniser, in a second place, where it would drift from R's.",
     "design_cite": "§2.9 \"treat the file extension as a routing signal rather than an assumption about meaning, inspect the real MIME type or file signature\"; P5 SPEC Done-means 10",
     "false_positive_risk": "n/a", "example_true": "—", "example_false": "word/document.xml"},
    {"id": "ref-bomb-signals", "match": "high compression ratio, nested archive depth, declared uncompressed size", "match_kind": "exact", "case_sensitive": False,
     "kind": "source-code manifest", "applies_to": "n/a",
     "rationale": "Not markers. §2.5 makes these safety inputs — \"Uncompressed size is read from the manifest where the format declares it, and is itself a bomb signal — it is never established by decompressing\" — and E4 already consumes them to produce `unreadable` or `partial`. A marker is evidence about content; a bomb signal is a refusal to look. Keeping them apart is what stops a safety limit from becoming a fact about the file.",
     "design_cite": "§2.5 \"Password-protected, malformed, nested, or oversized archives should be marked as unreadable or partially inspected rather than forced open\"",
     "false_positive_risk": "n/a", "example_true": "—", "example_false": "—"},
    {"id": "ref-archive-name", "match": "the archive's own filename", "match_kind": "exact", "case_sensitive": False,
     "kind": "document name", "applies_to": "n/a",
     "rationale": "§2.5's example turns on the outer name being *vague*: `submission.zip` is \"meaningful evidence of a purpose-defined application packet **even when the outer archive name is vague**\". The members carry the evidence. The archive's own filename is already an observation at `zone = filename` from the filesystem run, and re-reading it here would double-count it.",
     "design_cite": CITE25_DOC, "false_positive_risk": "n/a", "example_true": "—", "example_false": "submission.zip"},
    {"id": "ref-document-type-vocabulary", "match": "cover letter, diploma, essay, invoice, contract, W-2, syllabus, thesis, …", "match_kind": "regex", "case_sensitive": False,
     "kind": "document name", "applies_to": "member_basename",
     "rationale": "The obvious extension of the document-name array, and refused. A general document-type vocabulary **is** the 200-300 template library (§5.7), which is deferred and owned by P10, and the residual library beyond §7.3's nine names is deferred too. Seeding it here — inside an archive marker list, where nobody would look for it — is exactly how a template library gets invented by accident and then diverges from the real one. §2.5 names five; this file authors five.",
     "design_cite": "§5.7 template library — deferred to P10; P6 SPEC Deferred \"Residual library contents beyond the nine §7.3 names … **P10**\"",
     "false_positive_risk": "would be high", "example_true": "—", "example_false": "submission/cover_letter.pdf"}
  ],
  "uncertain": [
    {"id": "unc-form-word", "match": "form", "match_kind": "regex", "case_sensitive": False,
     "kind": "document name", "applies_to": "member_basename",
     "rationale": "§2.5 names `form` literally, so it is in — but it is the weakest string in either array. Whole-word matching keeps it out of `format`, `formula`, `information` and `transformation`, and the check asserts that. It will still fire on `Feedback Form.pdf`, `Form W-9.pdf` and `Google Form export.csv`, none of which makes an archive an application packet. Recommended handling, for P6 rather than for this file: weight `form` at zero on its own and let it count only alongside another document-name marker, which is what §2.5's five-document example actually describes.",
     "design_cite": CITE25_DOC, "false_positive_risk": "high", "example_true": "submission/Form.pdf", "example_false": "submission/transformation-notes.pdf"},
    {"id": "unc-cv-token", "match": "cv", "match_kind": "regex", "case_sensitive": False,
     "kind": "document name", "applies_to": "member_basename",
     "rationale": "Two characters, matched as a whole word. Safe against `cvs`, `cvx` and `opencv` because of the word boundaries, but a member literally named `cv.csv` in a data folder would match. Kept because `CV.pdf` is overwhelmingly the more common real case in the corpus this product targets. Flagged so it can be dropped cheaply if it proves noisy.",
     "design_cite": CITE25_DOC, "false_positive_risk": "medium", "example_true": "submission/CV.pdf", "example_false": "data/opencv-notes.txt"},
    {"id": "unc-nested-archive-members", "match": "markers inside a nested archive", "match_kind": "exact", "case_sensitive": False,
     "kind": "source-code manifest", "applies_to": "member_path_segment",
     "rationale": "An archive containing `project.zip` cannot have its inner members inspected without opening it, and §2.5 marks nested archives as a case to leave `unreadable` or `partial` rather than force open. So a nested archive's markers are simply not available, and the outer archive gets fewer markers than its contents would justify. This is a recall limit, not a bug, and it is the correct trade — but it should be visible before someone reads a sparse marker set as evidence of absence.",
     "design_cite": "§2.5 \"Password-protected, malformed, nested, or oversized archives should be marked as unreadable or partially inspected rather than forced open\"",
     "false_positive_risk": "n/a", "example_true": "outer/project.zip", "example_false": "—"},
    {"id": "unc-path-depth", "match": "should a marker at any depth count equally?", "match_kind": "exact", "case_sensitive": False,
     "kind": "source-code manifest", "applies_to": "member_path_segment",
     "rationale": "`package.json` at `project/package.json` is a project root marker. The same name at `project/node_modules/left-pad/package.json` is a dependency's manifest and means almost nothing — and a real Node archive contains thousands of them. P4 D10 already collapses repeated identical raw values within a zone, but these are *different* member paths, so they are different raw values and would not collapse. **A depth or path-segment filter is probably needed** — the natural rule being to ignore members under a `node_modules`, `vendor`, `site-packages` or `.venv` segment, reusing §1.1's eleven literal names in a different role. Not adopted unilaterally because it changes observation counts, which P2's replay diffs compare.",
     "design_cite": "§1.1's eleven literal directory names; P4 D10 occurrence collapsing; §8.5 replay comparability",
     "false_positive_risk": "high", "example_true": "project/node_modules/left-pad/package.json", "example_false": "project/package.json"},
    {"id": "unc-python-package-layout", "match": "\"Python package layout\" as a shape rather than a file", "match_kind": "exact", "case_sensitive": False,
     "kind": "source-code manifest", "applies_to": "member_path_segment",
     "rationale": "§2.5 names \"Python package layout\" alongside three concrete files, and a layout is a *relationship* between paths — a directory containing `__init__.py` plus sibling modules — not a single member. This file approximates it with the `__init__.py` row, which is the layout's defining file. A recogniser that genuinely tested the shape would need to reason over the whole member list, which it is given, so this is implementable; it is left out of v1 because a relationship-shaped marker has no obvious `member_path` to put in `raw_value`, and P5 requires one.",
     "design_cite": CITE25, "false_positive_risk": "low", "example_true": "project/pkg/__init__.py", "example_false": "—"},
    {"id": "unc-localized-document-names", "match": "non-English document names", "match_kind": "regex", "case_sensitive": False,
     "kind": "document name", "applies_to": "member_basename",
     "rationale": "`Lebenslauf`, `curriculum`, `expediente`, `relevé de notes` — the same five documents in other languages. Same position as catalogue 04's localized screenshot row: easy to add, impossible to choose correctly without knowing which languages the corpus contains. One question to Joseph settles it.",
     "design_cite": CITE25_DOC, "false_positive_risk": "low", "example_true": "bewerbung/Lebenslauf.pdf", "example_false": "submission/resume.pdf"}
  ],
}
OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
kinds = {}
for e in doc["entries"]:
    kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
print("entries:", len(doc["entries"]), kinds)
