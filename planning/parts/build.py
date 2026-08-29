"""Reproducible assembly for both parts. Preamble + winner sections + appendix."""
import sys, re, pathlib; sys.path.insert(0, '.')
import assemble as A
A.FIXES = []

def build(part_dir, winners, order, labels, appendix_header=None):
    D = A.PARTS / part_dir
    body, cache = [], {}
    for n in sorted(winners):
        f = winners[n]; cache.setdefault(f, A.sections(D / f))
        assert n in cache[f], f"task {n} not in {f}"
        body.append("\n".join(cache[f][n]))
    hdr = (D / appendix_header).read_text().rstrip() if appendix_header else None
    app = [hdr] if hdr else []
    for f in order:
        bm = A.back_matter(D / f)
        if bm:
            app.append(f"---\n\n# Reported by the {labels[f]} section\n")
            app.append("\n".join(bm))
    text = (D / "PLAN-PREAMBLE.md").read_text().rstrip() + "\n\n---\n\n" \
         + "\n\n---\n\n".join(body)
    if app:
        text += "\n\n---\n\n" + "\n\n".join(app)
    text += "\n"
    (D / "PLAN.md").write_text(text, encoding="utf-8")
    got = [int(m.group(1)) for m in (re.match(r'^### Task (\d+)\b', l) for l in text.split("\n")) if m]
    assert got == sorted(winners), got
    print(f"{part_dir}: {text.count(chr(10))+1} lines, {len(got)} tasks, "
          f"{len(set(winners.values()))} source files, {sum(1 for f in order if A.back_matter(D/f))} appendices")

P6 = {**{n: "PLAN-tasks-01-02.md" for n in (1,2)}, **{n: "PLAN-tasks-03-04.md" for n in (3,4)},
      **{n: "PLAN-tasks-05-06.md" for n in (5,6)}, 7: "PLAN-tasks-07-09.md",
      **{n: "PLAN-tasks-08-09.md" for n in (8,9)}, **{n: "PLAN-tasks-10-13.md" for n in (10,11,12,13)},
      **{n: "PLAN-tasks-14-15.md" for n in (14,15)}, **{n: "PLAN-tasks-16-19.md" for n in (16,17,18,19)},
      **{n: "PLAN-tasks-20-21.md" for n in (20,21)}, **{n: "PLAN-tasks-22-23.md" for n in (22,23)},
      **{n: "PLAN-tasks-24-25.md" for n in (24,25)}, 27: "PLAN-task-27.md"}
P6_ORDER = ["PLAN-tasks-05-06.md","PLAN-tasks-07-09.md","PLAN-tasks-08-09.md",
            "PLAN-tasks-10-13.md","PLAN-tasks-16-19.md","PLAN-tasks-24-25.md"]
P6_LAB = {"PLAN-tasks-05-06.md":"Tasks 5–6","PLAN-tasks-07-09.md":"Tasks 7–9","PLAN-tasks-08-09.md":"Tasks 8–9",
          "PLAN-tasks-10-13.md":"Tasks 10–13","PLAN-tasks-16-19.md":"Tasks 16–19","PLAN-tasks-24-25.md":"Tasks 24–25"}

P7 = {**{n: "PLAN-tasks-01-03.md" for n in (1,2,3)}, **{n: "PLAN-tasks-04-07.md" for n in (4,5,6)},
      7: "PLAN-tasks-07.md", **{n: "PLAN-tasks-08-11.md" for n in (8,9,10)}, 11: "PLAN-tasks-11.md",
      **{n: "PLAN-tasks-12-14.md" for n in (12,13,14)}, 15: "PLAN-tasks-15-22.md", 16: "PLAN-tasks-15-22.md",
      17: "PLAN-tasks-17-19.md", 18: "PLAN-tasks-15-22.md", 19: "PLAN-tasks-17-19.md",
      **{n: "PLAN-tasks-20-22.md" for n in (20,21,22)}}
P7_ORDER = ["PLAN-tasks-01-03.md","PLAN-tasks-04-07.md","PLAN-tasks-12-14.md",
            "PLAN-tasks-15-22.md","PLAN-tasks-17-19.md","PLAN-tasks-20-22.md"]
P7_LAB = {"PLAN-tasks-01-03.md":"Tasks 1–3","PLAN-tasks-04-07.md":"Tasks 4–7","PLAN-tasks-12-14.md":"Tasks 12–14",
          "PLAN-tasks-15-22.md":"Tasks 15–22","PLAN-tasks-17-19.md":"Tasks 17–19","PLAN-tasks-20-22.md":"Tasks 20–22"}

build("P6-facts-facets", P6, P6_ORDER, P6_LAB, "PLAN-APPENDIX-HEADER.md")
build("P7-privacy-consent-gate", P7, P7_ORDER, P7_LAB, "PLAN-APPENDIX-HEADER.md")
