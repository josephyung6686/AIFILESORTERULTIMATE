import json
from pathlib import Path

OUT = Path("/Users/jy/GRAPH AGENT/planning/deferred-catalogues/05-repository-markers.json")
CITE = "§2.4 \"structural indicators such as repository markers, package manifests, notebook metadata, and README files\""
CITE25 = "§2.5 \"A source-code archive may reveal a `README.md`, `package.json`, `src` directory, or Python package layout and can be recognized as a code project.\""

# (match, kind, ecosystem, note, risk)
MANIFESTS = [
    ("package.json", "npm / Node.js", "Also §1.1's first exclusion-root marker — see the two-role note.", "low"),
    ("package-lock.json", "npm", None, "low"),
    ("yarn.lock", "Yarn", None, "low"),
    ("pnpm-lock.yaml", "pnpm", None, "low"),
    ("bun.lockb", "Bun", None, "low"),
    ("deno.json", "Deno", None, "low"),
    ("deno.lock", "Deno", None, "low"),
    ("requirements.txt", "Python pip", "Also §1.1's second exclusion-root marker.", "low"),
    ("pyproject.toml", "Python PEP 518", "The modern Python manifest, and a strong project-root signal §1.1 predates.", "low"),
    ("setup.py", "Python setuptools", None, "low"),
    ("setup.cfg", "Python setuptools", None, "low"),
    ("Pipfile", "Python pipenv", None, "low"),
    ("Pipfile.lock", "Python pipenv", None, "low"),
    ("poetry.lock", "Python Poetry", None, "low"),
    ("environment.yml", "conda", "Also used by non-Python conda environments.", "low"),
    ("Cargo.toml", "Rust", "Also §1.1's third exclusion-root marker.", "low"),
    ("Cargo.lock", "Rust", None, "low"),
    ("go.mod", "Go", "Also §1.1's fourth exclusion-root marker.", "low"),
    ("go.sum", "Go", None, "low"),
    ("pom.xml", "Maven / Java", None, "low"),
    ("build.gradle", "Gradle", None, "low"),
    ("build.gradle.kts", "Gradle Kotlin DSL", None, "low"),
    ("settings.gradle", "Gradle", None, "low"),
    ("settings.gradle.kts", "Gradle Kotlin DSL", None, "low"),
    ("Gemfile", "Ruby Bundler", None, "low"),
    ("Gemfile.lock", "Ruby Bundler", None, "low"),
    ("composer.json", "PHP Composer", None, "low"),
    ("composer.lock", "PHP Composer", None, "low"),
    ("CMakeLists.txt", "CMake / C++", "**Rule 5's worked example.** A C++ project marker, and deliberately *not* an exclusion root.", "low"),
    ("Makefile", "make", "Common outside software too (LaTeX, docs, data pipelines), so it is evidence only.", "medium"),
    ("meson.build", "Meson", None, "low"),
    ("configure.ac", "GNU Autotools", None, "low"),
    ("Makefile.am", "GNU Automake", None, "low"),
    ("vcpkg.json", "vcpkg / C++", None, "low"),
    ("conanfile.txt", "Conan / C++", None, "low"),
    ("conanfile.py", "Conan / C++", None, "low"),
    ("pubspec.yaml", "Dart / Flutter", None, "low"),
    ("mix.exs", "Elixir", None, "low"),
    ("Package.swift", "Swift Package Manager", None, "low"),
    ("Podfile", "CocoaPods", None, "low"),
    ("Podfile.lock", "CocoaPods", None, "low"),
    ("Cartfile", "Carthage", None, "low"),
    ("build.sbt", "Scala sbt", None, "low"),
    ("project.clj", "Clojure Leiningen", None, "low"),
    ("deps.edn", "Clojure tools.deps", None, "low"),
    ("rebar.config", "Erlang", None, "low"),
    ("shard.yml", "Crystal", None, "low"),
    ("stack.yaml", "Haskell Stack", None, "low"),
    ("cabal.project", "Haskell Cabal", None, "low"),
    ("DESCRIPTION", "R package", "R's manifest has no extension and the bare word is generic, so it is `exact` and case-sensitive.", "medium"),
    ("renv.lock", "R renv", None, "low"),
    ("packages.config", "NuGet / .NET", None, "low"),
    ("Directory.Build.props", "MSBuild / .NET", None, "low"),
    ("global.json", ".NET SDK", None, "low"),
    ("BUILD.bazel", "Bazel", None, "low"),
    ("WORKSPACE", "Bazel", "Bare uppercase word; case-sensitive exact only.", "medium"),
    ("MODULE.bazel", "Bazel", None, "low"),
    ("flake.nix", "Nix flakes", None, "low"),
    ("default.nix", "Nix", None, "low"),
    ("shell.nix", "Nix", None, "low"),
    ("Chart.yaml", "Helm", None, "low"),
    ("go.work", "Go workspaces", None, "low"),
]

REPO_MARKERS = [
    (".git", "directory_name", "Version control. Present in the *root* of a repository — but see the refusal: this must never become an exclusion root.", "low"),
    (".gitignore", "filename", "Version control config.", "low"),
    (".gitattributes", "filename", "Version control config.", "low"),
    (".gitmodules", "filename", "Submodule config; a strong multi-repo signal.", "low"),
    (".hg", "directory_name", "Mercurial.", "low"),
    (".svn", "directory_name", "Subversion.", "low"),
    (".github", "directory_name", "GitHub workflows and templates.", "low"),
    (".gitlab-ci.yml", "filename", "GitLab CI.", "low"),
    (".travis.yml", "filename", "Travis CI.", "low"),
    ("azure-pipelines.yml", "filename", "Azure Pipelines.", "low"),
    ("Jenkinsfile", "filename", "Jenkins.", "low"),
    (".circleci", "directory_name", "CircleCI config directory.", "low"),
    ("Dockerfile", "filename", "Container build definition.", "low"),
    ("docker-compose.yml", "filename", "Container orchestration.", "low"),
    ("docker-compose.yaml", "filename", "Container orchestration.", "low"),
    (".dockerignore", "filename", "Container build config.", "low"),
    (".editorconfig", "filename", "Editor config, near-universal in repositories.", "low"),
    (".pre-commit-config.yaml", "filename", "Pre-commit hooks.", "low"),
    ("tsconfig.json", "filename", "TypeScript project config.", "low"),
    ("jsconfig.json", "filename", "JavaScript project config.", "low"),
    (".eslintrc.json", "filename", "Lint config.", "low"),
    (".eslintrc.js", "filename", "Lint config.", "low"),
    (".eslintrc.cjs", "filename", "Lint config.", "low"),
    ("eslint.config.js", "filename", "Flat lint config.", "low"),
    (".prettierrc", "filename", "Format config.", "low"),
    ("vite.config.ts", "filename", "Build config.", "low"),
    ("vite.config.js", "filename", "Build config.", "low"),
    ("webpack.config.js", "filename", "Build config.", "low"),
    ("rollup.config.js", "filename", "Build config.", "low"),
    ("babel.config.js", "filename", "Transpiler config.", "low"),
    ("tox.ini", "filename", "Python test matrix config.", "low"),
    ("pytest.ini", "filename", "Python test config.", "low"),
    ("noxfile.py", "filename", "Python task runner.", "low"),
    ("LICENSE", "filename", "Bare uppercase word; exact and case-sensitive.", "medium"),
    ("LICENSE.md", "filename", "Licence file.", "low"),
    ("LICENSE.txt", "filename", "Licence file.", "low"),
    ("COPYING", "filename", "GNU-convention licence file.", "medium"),
    ("CONTRIBUTING.md", "filename", "Repository convention file.", "low"),
    ("CODE_OF_CONDUCT.md", "filename", "Repository convention file.", "low"),
    ("CHANGELOG.md", "filename", "Repository convention file.", "low"),
    ("SECURITY.md", "filename", "Repository convention file.", "low"),
    ("CODEOWNERS", "filename", "Repository ownership file.", "low"),
    ("src", "directory_name", "**§2.5 names this literally** as one of the four things a source-code archive may reveal. Generic on its own; it is one marker among several, never a verdict.", "high"),
    ("__init__.py", "filename", "**§2.5's \"Python package layout\"**, made concrete: the file that makes a directory a Python package.", "low"),
    ("py.typed", "filename", "PEP 561 typing marker inside a Python package.", "low"),
]

READMES = [
    ("README.md", "The §2.5 literal. Markdown is the dominant form.", "low"),
    ("README", "Extensionless form; case-sensitive exact.", "medium"),
    ("README.txt", "Plain-text form.", "low"),
    ("README.rst", "reStructuredText, common in Python projects.", "low"),
    ("README.adoc", "AsciiDoc form.", "low"),
    ("readme.md", "Lowercase form — listed separately because the marker `value` is stored verbatim (P5 `StructuralMarker.value`), so the two spellings are two different recorded values even though matching is case-insensitive.", "low"),
]

NOTEBOOK_KEYS = [
    ("nbformat", "The notebook format version. Its presence at the top level of a JSON document is what makes that document a notebook rather than arbitrary JSON.", "low"),
    ("nbformat_minor", "Notebook format minor version.", "low"),
    ("kernelspec", "The kernel the notebook runs on; carries `name`, `display_name`, `language`.", "low"),
    ("language_info", "The notebook's language and version metadata — §2.4's \"language where relevant\" for notebooks.", "low"),
    ("cells", "The cell array. §2.9 names \"notebook cell types\" as notebook structure; P4's `cell` segment kind addresses them.", "low"),
]

def entry(idx, match, kind, applies_to, rationale, risk, cite, ex_false, case_sensitive=False):
    return {
        "id": idx, "match": match, "match_kind": "exact",
        "case_sensitive": case_sensitive,
        "kind": kind, "applies_to": applies_to,
        "rationale": rationale, "design_cite": cite,
        "false_positive_risk": risk,
        "example_true": match, "example_false": ex_false,
    }

p5 = []
for m, eco, note, risk in MANIFESTS:
    rat = f"{eco} manifest. §2.4 names \"package manifests\" as a structural indicator class."
    if note:
        rat += " " + note
    cs = m in ("DESCRIPTION", "WORKSPACE")
    if cs:
        rat += " Case-sensitive: the lowercase word is ordinary English."
    p5.append(entry(f"p5m-{m.lower().replace('.', '-')}", m, "package manifest", "filename",
                    rat, risk, CITE, f"my-{m}" if not cs else m.lower(), cs))

for m, applies, note, risk in REPO_MARKERS:
    rat = f"{note} §2.4 names \"repository markers\" as a structural indicator class."
    cs = m in ("LICENSE", "COPYING", "CODEOWNERS")
    if cs:
        rat += " Case-sensitive: the lowercase word is ordinary English."
    cite = CITE25 if m in ("src", "__init__.py") else CITE
    p5.append(entry(f"p5r-{m.lower().strip('.').replace('.', '-')}", m, "repository marker", applies,
                    rat, risk, cite, "source" if m == "src" else (m.lower() if cs else f"notes-{m}"), cs))

for m, note, risk in READMES:
    p5.append(entry(f"p5d-{m.lower().replace('.', '-')}", m, "README file", "filename",
                    f"{note} §2.4 names \"README files\" as a structural indicator class; §2.5 names `README.md` literally.",
                    risk, CITE25, "READMEs for the team", m == "README"))

for m, note, risk in NOTEBOOK_KEYS:
    p5.append(entry(f"p5n-{m.replace('_', '-')}", m, "notebook metadata", "notebook_json_key",
                    f"{note} §2.4 names \"notebook metadata\" as a structural indicator class. The `value` P5 stores is the metadata key verbatim, not a filename — `StructuralMarker.value` is documented as \"a file name, a manifest name, a notebook metadata key\".",
                    risk, CITE, "notebook", True))

# de-dup ids
seen = set()
for e in p5:
    if e["id"] in seen:
        e["id"] += "-2"
    seen.add(e["id"])

print("p5_evidence_markers:", len(p5))
print("kinds:", sorted({e["kind"] for e in p5}))
json.dump(p5, open("/private/tmp/claude-501/-Users-jy-GRAPH-AGENT/48f6ea24-f9be-4201-aab1-f68980c524f4/scratchpad/cat/p5markers.json", "w"), indent=2)

# ---------------------------------------------------------------- assemble ----
P3_CITE = "§1.1 \"It should also reject descendants of software project roots indicated by files such as `package.json`, `requirements.txt`, `Cargo.toml`, or `go.mod`. This prevents the proposal engine from mistaking a dependency subdirectory for a meaningful personal destination.\""

p3 = [
  {"id": "p3x-package-json", "match": "package.json", "match_kind": "exact", "case_sensitive": True,
   "role": "project-root marker: P3 emits an R3 exclusion verdict for every **descendant** of the directory holding this file",
   "status": "settled — named literally by §1.1",
   "applies_to": "filename",
   "rationale": "One of §1.1's four literal markers. **This file also appears in `p5_evidence_markers` as `p5m-package-json`, and the two roles are different.** As a P3 exclusion root it means *do not scan below here* — the directory is a dependency tree, not a personal destination. As P5 evidence it means *this file looks like part of a project* — an observation about a file P3 did admit. One name, two jobs, two arrays; conflating them is what rule 5 of this task forbids.",
   "design_cite": P3_CITE, "false_positive_risk": "low",
   "example_true": "package.json", "example_false": "package.json.bak"},
  {"id": "p3x-requirements-txt", "match": "requirements.txt", "match_kind": "exact", "case_sensitive": True,
   "role": "project-root marker: P3 skips descendants",
   "status": "settled — named literally by §1.1", "applies_to": "filename",
   "rationale": "One of §1.1's four literal markers. Also present in `p5_evidence_markers` as `p5m-requirements-txt`, with the same two-role split.",
   "design_cite": P3_CITE, "false_positive_risk": "medium",
   "example_true": "requirements.txt", "example_false": "requirements-for-the-grant.txt"},
  {"id": "p3x-cargo-toml", "match": "Cargo.toml", "match_kind": "exact", "case_sensitive": True,
   "role": "project-root marker: P3 skips descendants",
   "status": "settled — named literally by §1.1", "applies_to": "filename",
   "rationale": "One of §1.1's four literal markers. Also present in `p5_evidence_markers` as `p5m-cargo-toml`.",
   "design_cite": P3_CITE, "false_positive_risk": "low",
   "example_true": "Cargo.toml", "example_false": "cargo-notes.toml"},
  {"id": "p3x-go-mod", "match": "go.mod", "match_kind": "exact", "case_sensitive": True,
   "role": "project-root marker: P3 skips descendants",
   "status": "settled — named literally by §1.1", "applies_to": "filename",
   "rationale": "One of §1.1's four literal markers. Also present in `p5_evidence_markers` as `p5m-go-mod`.",
   "design_cite": P3_CITE, "false_positive_risk": "low",
   "example_true": "go.mod", "example_false": "go.modules.txt"},
]

refused = [
  {"id": "ref-cmakelists-as-exclusion", "match": "CMakeLists.txt", "match_kind": "exact", "case_sensitive": True,
   "role": "REFUSED as a `p3_exclusion_root`; present instead as `p5m-cmakelists-txt`",
   "status": "refused", "applies_to": "filename",
   "rationale": "The task's named worked example, and the clearest case for the split. `CMakeLists.txt` sits at the top of hand-written C++ source trees that a person authored and would want organized. Making it an exclusion root would make P3 emit an R3 verdict for every descendant — the user's own code would silently vanish from the corpus, and §1.1's stated purpose is the opposite: stopping the engine \"mistaking a dependency subdirectory for a meaningful personal destination\". A dependency tree is what §1.1 excludes; a source tree is not one. As P5 evidence the same file is useful and harmless.",
   "design_cite": P3_CITE, "false_positive_risk": "would be severe",
   "example_true": "—", "example_false": "CMakeLists.txt"},
  {"id": "ref-git-as-exclusion-root", "match": ".git", "match_kind": "exact", "case_sensitive": True,
   "role": "REFUSED as a `p3_exclusion_root`; present as `p5r-git`",
   "status": "refused", "applies_to": "directory_name",
   "rationale": "Tempting and wrong. A directory containing `.git` is a repository root — but `.git` is already one of §1.1's **eleven literal directory names**, which means P3 skips the `.git` directory itself, not its parent's descendants. Promoting it to an exclusion root would exclude every git repository, and people keep notes, papers, theses and photo archives in git. This would delete more of a real corpus than any other candidate on this page.",
   "design_cite": "§1.1's eleven literal names include `.git`; the project-root rule is a separate mechanism",
   "false_positive_risk": "would be catastrophic", "example_true": "—", "example_false": ".git"},
  {"id": "ref-makefile-as-exclusion", "match": "Makefile", "match_kind": "exact", "case_sensitive": True,
   "role": "REFUSED as a `p3_exclusion_root`; present as `p5m-makefile`",
   "status": "refused", "applies_to": "filename",
   "rationale": "`Makefile` appears at the top of LaTeX theses, documentation sites, data pipelines and personal scripts as often as it does in software. Excluding its descendants would remove exactly the academic material this product exists to organize.",
   "design_cite": P3_CITE, "false_positive_risk": "would be severe",
   "example_true": "—", "example_false": "Makefile"},
  {"id": "ref-readme-as-exclusion", "match": "README.md", "match_kind": "exact", "case_sensitive": True,
   "role": "REFUSED as a `p3_exclusion_root`; present as `p5d-readme-md`",
   "status": "refused", "applies_to": "filename",
   "rationale": "A README marks a directory a person documented — which is a reason to look *more* carefully, not to stop scanning. §2.5 names it as project **evidence**, never as an exclusion.",
   "design_cite": CITE25, "false_positive_risk": "would be catastrophic",
   "example_true": "—", "example_false": "README.md"},
]

uncertain = [
  {"id": "unc-pyproject-as-exclusion", "match": "pyproject.toml", "match_kind": "exact", "case_sensitive": True,
   "role": "candidate `p3_exclusion_root` — NOT added", "status": "proposed — needs Joseph",
   "applies_to": "filename",
   "rationale": "The strongest candidate for extending §1.1's four, and still not added. §1.1's list is explicitly open (\"files such as\"), it names `requirements.txt`, and `pyproject.toml` has since replaced it as the Python project root marker — so the *intent* of §1.1 arguably covers it. Against: a `pyproject.toml` sits at the top of hand-written analysis code and thesis tooling as well as dependency trees, and excluding descendants would drop them. **Decision needed from Joseph, framed narrowly:** should a directory holding `pyproject.toml` be skipped the way one holding `requirements.txt` is? If yes it is a one-line addition here with `status: proposed` removed; the default answer this file ships with is no.",
   "design_cite": P3_CITE + " — \"files such as\" signals an extensible set", "false_positive_risk": "medium",
   "example_true": "pyproject.toml", "example_false": "pyproject-notes.toml"},
  {"id": "unc-lockfiles-as-exclusion", "match": "package-lock.json / yarn.lock / poetry.lock / Gemfile.lock / composer.lock", "match_kind": "exact", "case_sensitive": True,
   "role": "candidate `p3_exclusion_roots` — NOT added", "status": "proposed — needs Joseph",
   "applies_to": "filename",
   "rationale": "A lock file is a *stronger* dependency-tree signal than a manifest: it is machine-generated and never hand-authored, so a directory holding one is far more likely to be a real dependency tree than a personal folder. That makes lock files the safest possible extension of §1.1's four. Not added anyway, because a lock file always sits beside its manifest, so adding them changes almost no verdict while widening the rule that hides user trees. Recorded so the reasoning is on the record rather than re-derived later.",
   "design_cite": P3_CITE, "false_positive_risk": "low", "example_true": "package-lock.json", "example_false": "my-lock.json"},
  {"id": "unc-other-ecosystems-as-exclusion", "match": "pom.xml / build.gradle / Gemfile / composer.json / mix.exs / pubspec.yaml", "match_kind": "exact", "case_sensitive": True,
   "role": "candidate `p3_exclusion_roots` — NOT added", "status": "proposed — needs Joseph",
   "applies_to": "filename",
   "rationale": "The obvious per-ecosystem extension of §1.1's four. All are in `p5_evidence_markers` already, which is where the task says extra language ecosystems go first. Adding any of them to the exclusion side hides whole trees, and none of them is a case where Joseph would *clearly* want the folder never scanned — which is the bar the task sets. The honest position: revisit after a real scan shows how many files each would remove.",
   "design_cite": P3_CITE, "false_positive_risk": "medium", "example_true": "pom.xml", "example_false": "pom-notes.xml"},
  {"id": "unc-p3-oq9", "match": "does the marker-bearing directory itself get excluded?", "match_kind": "exact", "case_sensitive": False,
   "role": "open question inherited from P3", "status": "open — P3 SPEC Open Question 9",
   "applies_to": "n/a",
   "rationale": "P3 SPEC Open Question 9: \"Does the project-root rule exclude the root directory itself, or only its descendants? §1.1 says 'descendants of software project roots.' Whether the marker-bearing directory can still be a candidate root is unsettled.\" This catalogue supplies the marker names and takes no position on the question — it is P3's, and answering it here would be inventing.",
   "design_cite": "P3 SPEC Open Question 9", "false_positive_risk": "n/a", "example_true": "—", "example_false": "—"},
  {"id": "unc-xcode-bundles", "match": ".xcodeproj / .xcworkspace", "match_kind": "exact", "case_sensitive": True,
   "role": "neither array — already covered elsewhere", "status": "open",
   "applies_to": "directory_name",
   "rationale": "These are directory bundles, and P3's ratified protected-container rule already refuses to descend into macOS packages — \"P3 does not descend into one, does not stat its contents, does not hash a byte of it\". Adding them here would duplicate a stronger rule in a weaker place. Recorded so nobody adds them later thinking they were missed.",
   "design_cite": "P3 SPEC, protected containers (ratified 2026-08-20, closing Q7)", "false_positive_risk": "n/a",
   "example_true": "—", "example_false": "MyApp.xcodeproj"},
  {"id": "unc-notebook-key-collision", "match": "cells / kernelspec as notebook metadata keys", "match_kind": "exact", "case_sensitive": True,
   "role": "`p5_evidence_markers`, kind `notebook metadata`", "status": "open",
   "applies_to": "notebook_json_key",
   "rationale": "These five keys are matched against **top-level JSON object keys**, not filenames — a different match target from every other row in this file, which is why each carries `applies_to: notebook_json_key`. An arbitrary JSON document could contain a top-level `cells` key and be mistaken for a notebook. `nbformat` is the discriminating one and should probably be required before the others are reported; that is the reader's logic, not this catalogue's, so it is flagged rather than decided.",
   "design_cite": CITE + "; P5 `StructuralMarker.value` — \"a file name, a manifest name, a notebook metadata key\"",
   "false_positive_risk": "medium", "example_true": "nbformat", "example_false": "cells"},
]

doc = {
  "list_id": "repository_markers",
  "title": "05 — Repository markers and package manifests (two arrays, two owners)",
  "version": "1.0",
  "authored": "2026-08-20",
  "owner": "`p3_exclusion_roots` → P3 · `p5_evidence_markers` → P5 (injected into the caller's reader)",
  "consumer": "`p3_exclusion_roots` → P3's R3 exclusion verdict, which skips **descendants** of the marker-bearing directory. `p5_evidence_markers` → the `StructuralMarker(kind, value)` tuples that a caller-supplied `read_text_document` returns, and the `recognize_markers` recognizer E4 uses on archive members.",
  "match_field": "a filename, a directory name, or a top-level notebook JSON key — each row says which in `applies_to`. `StructuralMarker.value` stores the marker \"verbatim\" (P5 PLAN Task 12), so the recorded value is the spelling found on disk, not a normalized one.",
  "normalization_for_matching": "Exact string comparison. Case-insensitive by default because macOS and Windows filesystems are case-insensitive; the rows whose bare word is ordinary English (`LICENSE`, `COPYING`, `WORKSPACE`, `DESCRIPTION`, `README`, `CODEOWNERS`) are case-**sensitive** so that a document named `licence` or `description` cannot match.",
  "design_cites": [
    P3_CITE,
    CITE,
    CITE25,
    "§2.4: \"Code-related files should rely heavily on local structural evidence, including repository roots and package files, rather than forcing semantic analysis to infer a project from arbitrary code text.\"",
    "P5 SPEC Deferred: \"Repository markers and package manifests beyond §1.1's four | §2.4, §1.1, §2.5 | `package.json`, `requirements.txt`, `Cargo.toml`, `go.mod` (§1.1); `README.md`, `package.json`, `src`, Python package layout (§2.5) | Everything else; §1.1's list is P3's\"",
    "P3 SPEC Deferred: \"Software-project-root markers beyond §1.1's four … The four literal names are implementable now; any extension is hand-authored.\"",
    "P5 PLAN Task 12: `STRUCTURAL_MARKER_KINDS = (\"repository marker\", \"package manifest\", \"notebook metadata\", \"README file\")` — a fifth class raises `UnknownMarkerKind`."
  ],
  "rules": [
    "**Two arrays, because there are two jobs.** `p3_exclusion_roots` answers *should this whole subtree be skipped before scanning?* `p5_evidence_markers` answers *does this admitted file look like part of a project?* A name may be in both — `package.json` is — and being in one never implies the other.",
    "**Exclusion is destructive; evidence is not.** A wrong entry in `p3_exclusion_roots` makes real user files invisible to the entire product, with no observation, no fact and no review surface. A wrong entry in `p5_evidence_markers` produces one weak observation P6 can outweigh. The two arrays therefore have completely different bars for admission, and this file applies them differently on purpose.",
    "**`p3_exclusion_roots` contains §1.1's four literal names and nothing else.** No addition was made. Every candidate considered is written up under *Uncertain* with the argument on both sides, so Joseph decides rather than discovers.",
    "**Every `p5_evidence_markers` row carries one of exactly four `kind` values** — `repository marker`, `package manifest`, `notebook metadata`, `README file`. P5 raises `UnknownMarkerKind` on a fifth, so a row with any other kind is not merely wrong, it is unloadable.",
    "**P5 emits markers; it does not read code.** §2.4: structural evidence \"rather than forcing semantic analysis to infer a project from arbitrary code text\". Nothing in this file inspects file contents beyond the notebook keys, and nothing concludes that a directory *is* a project — that is a fact, and facts are P6's."
  ],
  "coverage_note": "`p5_evidence_markers` covers roughly thirty language and build ecosystems plus the version-control, CI, container and lint conventions that mark a repository. It is broad on purpose: this side is cheap to be wrong on. `p3_exclusion_roots` is four rows and stays four rows — that side is expensive to be wrong on, and §1.1's four are the only ones the design actually settles.\n\nDeliberately absent from both: `node_modules`, `.git`, `venv`, `build`, `dist`, `target`, `vendor`, `Pods`, `site-packages`, `Library`, `__pycache__`. Those are §1.1's **eleven literal directory names**, a third mechanism that P3 already implements and that neither array duplicates.",
  "sources": [
    {"title": "npm — package.json documentation", "url": "https://docs.npmjs.com/cli/v10/configuring-npm/package-json", "retrieved": "2026-08-20", "note": "Vendor definition of the Node manifest."},
    {"title": "Python Packaging — pyproject.toml specification", "url": "https://packaging.python.org/en/latest/specifications/pyproject-toml/", "retrieved": "2026-08-20", "note": "PEP 518/621 project manifest — the basis for `unc-pyproject-as-exclusion`."},
    {"title": "Rust — The Cargo Book, the manifest format", "url": "https://doc.rust-lang.org/cargo/reference/manifest.html", "retrieved": "2026-08-20", "note": "Vendor definition of `Cargo.toml`."},
    {"title": "Go — Go Modules Reference, go.mod files", "url": "https://go.dev/ref/mod#go-mod-file", "retrieved": "2026-08-20", "note": "Vendor definition of `go.mod`."},
    {"title": "Jupyter — Notebook format (nbformat) specification", "url": "https://nbformat.readthedocs.io/en/latest/format_description.html", "retrieved": "2026-08-20", "note": "Defines the top-level keys `nbformat`, `nbformat_minor`, `metadata` (`kernelspec`, `language_info`) and `cells` — the five notebook-metadata rows."},
    {"title": "Git — gitrepository-layout", "url": "https://git-scm.com/docs/gitrepository-layout", "retrieved": "2026-08-20", "note": "Defines the `.git` directory whose promotion to an exclusion root is refused."}
  ],
  "injection": "Two different injection points, matching the two owners.\n\n**P3** receives `p3_exclusion_roots` as configuration on the scan, alongside §1.1's eleven literal directory names. It is data P3 reads, never a constant in P3's source.\n\n**P5** never receives `p5_evidence_markers` at all. The markers reach P5 as *reader output*: a caller-supplied `read_text_document(path) -> TextDocument` returns `markers=(StructuralMarker(kind=…, value=…), …)`, and E3 places them at `zone = metadata` with the kind as the field label. For archives, E4 takes a caller-supplied `recognize_markers(member_paths)`. Either way the list lives in the caller, and P5 PLAN Task 20's runtime-introspection guard asserts that no marker file name appears in any module-level container inside `src/extractors/`.",
  "p3_exclusion_roots": p3,
  "p5_evidence_markers": p5,
  "refused": refused,
  "uncertain": uncertain,
}
OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
print("wrote", OUT.name, "| p3:", len(p3), "| p5:", len(p5), "| refused:", len(refused), "| uncertain:", len(uncertain))
