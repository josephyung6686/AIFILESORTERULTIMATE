# Dispatch prompt — R6 · academic and capture pattern catalogues

Copy everything below the line into a new agent. The agent should not need this chat.

Give it read access to the repo. It writes under `planning/deferred-catalogues/12-academic-capture-patterns/`. Patterns are **data**, injected into P6 (facts) and already-existing P5 call sites where relevant. **No fuzzy date parsing** (`00`). No module-level regex in `src/facts/` or `src/extractors/`.

---

You are authoring the **pattern catalogues** `00` named by example and never filled.

## Why you are here

`00` is explicit and small:

- Course fact: `BUSIB 4300` **only when** a course-code pattern co-occurs with academic context such as "syllabus," "lecture," "credits," "instructor," or "semester."
- Academic terms such as `Spring 2025`, `AY 2024-25`, and `Michaelmas Term 2024` require **dedicated patterns** rather than generic parsing.
- Date extraction should be **deliberately narrow**. File names frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values.
- `v2024` / build / ZIP must not become dates.
- Capture: EXIF `DateTimeOriginal` is raw; `capture date = 2026-07-17` is the fact. Photos may use capture year, event, location, people, camera information, media type.
- Images: camera EXIF is strong photo evidence; absence of EXIF is **not** proof of screenshot; OCR density is not a screenshot detector.

P6 SPEC Deferred: "Date and academic-term regex catalogue beyond the three named patterns" and "Rule context-term lists beyond the five literal academic terms." P6 Task 10 treats the five as required-and-extensible; `00` says "such as" (a floor). Overnight R1 F-1 already proved closed lists that ignore other `00` sentences are internally impossible.

P5 already injects: screen resolutions, sensor ratios, camera filename patterns (catalogues 02–04). You **extend** capture/screenshot **fact** patterns for P6, and academic patterns P6 is currently empty on. Do not duplicate 02–04.

## Product constraint

Read:

- `planning/00-database-agent-product-design.md`
- `planning/01-product-design-structured.md` §3.5, §3.7, §3.10, §2.6, §2.7, §3.2
- `planning/parts/P6-facts-facets/SPEC.md` Deferred rows for regex, context terms, photo-event parameters (G7 — **slots only, no numbers**)
- `planning/deferred-catalogues/02-screen-resolutions.json`, `03-sensor-aspect-ratios.json`, `04-camera-filename-patterns.json`
- `planning/parts/P4-evidence-shape/SPEC.md` zones (filename, title, heading, …) — positional weighting consumes zone, you do not invent zones
- `planning/domains/CONNECTION.md` if present
- Adversarial fixtures `tests/eval/fixtures/adversarial/` A01–A03 if present (MIT-in-submit, UNC-in-uncertainty, v2024)

Word-boundary. Rank + margin (injected). Context required for course codes. Three named term patterns are **required** in your catalogue, not optional.

`subject` vs `course` is D6 — **unset**. Patterns match the **value** `BUSIB 4300`; the field key is whoever Joseph picks. Store the pattern against both names as aliases in metadata if you must, do not pick.

## What to research

### A. Academic context terms

Floor (design, required): syllabus, lecture, credits, instructor, semester.

Extend as `proposal` with never_alone: `homework`, `midterm`, `problem set`, `office hours`, `canvas`, `blackboard` — each with a false friend (`canvas` the LMS vs Canvas the product vs a painting).

Per term: `term_id`, `language`, `scripts`, `never_alone`.

### B. Course-code formats

Not a list of courses. Formats: `DEPT 1234`, `DEPT1234`, `1234.DEPT`, with **context required**. False friends: ZIP, years, build numbers, issue numbers, `HW 3`. `HW 3` is a work-type clue, not a course code (`00` worked example).

### C. Academic term patterns

Required: `Spring 2025`, `AY 2024-25`, `Michaelmas Term 2024`.

Research: Fall/Autumn, Winter quarter, FY2025, Semester 1/2, 2024–25 en-dash vs hyphen, CJK term names as **slots** if you cannot author them honestly.

Each pattern: examples that must match, examples that must not (`Spring` the mattress; `Fall` the verb; `AY` inside a word).

### D. Narrow dates

What may become a `creation date` / `capture date` / `term` vs what must never:

- EXIF DateTimeOriginal → capture date (`00`)
- labelled form fields
- forbidden: `v2024`, filenames that are course ids, ZIP, ISO numbers, software versions

Output **named pattern families**, not a single `.*20\d{2}.*`.

### E. Capture / screenshot hypothesis (P6 side)

P5 already classifies dimension/filename signals. P6 needs when those observations support **facts**: `media_type`, `capture_date`, `event` (photo event), and when they must **abstain** (`00`: conflicting signals → abstention).

Photo-event clustering: time window, GPS radius, camera identity — **G7, slots with no numbers**. Name the slots; do not fill 6 hours / 100 m.

Screenshot vs photo: consume catalogues 02–04 as inputs; you write the **composition rule** (EXIF strong; display resolution may support screenshot; never from missing EXIF alone).

## What you must not do

- Fuzzy date parsing (no dateutil-fuzzy, no GPT "this looks like a date").
- Invent min_score numbers.
- Treat `HW 3` as a course.
- Duplicate screen-resolution tables.
- Close D6.
- Edit `src/`.

## Output

```text
planning/deferred-catalogues/12-academic-capture-patterns/
  README.md                 who injects what (P6 resolver; P5 already has 02–04)
  01-academic-context-terms.json
  02-course-code-formats.json
  03-academic-term-patterns.json   # must include the three 00 literals
  04-narrow-date-families.json
  05-capture-composition.md        # rules composing P5 signals into P6 facts; slots for G7
  RESEARCH.md
  check.py                  three 00 term examples match; MIT/UNC never_alone cases exist;
                            v2024 listed as a non-date; no numeric windows;
                            no fabricated 00 quotes
```

## Done when

- The three `00` term strings match dedicated patterns.
- Course code without context cannot validate.
- `HW 3` is not a course format.
- `v2024` cannot become a date.
- Screenshot composition refuses "no EXIF ⇒ screenshot."
- G7 parameters are named slots, not numbers.
- Adversarial A01–A03 (if present) are cited as acceptance tests your patterns must not violate.
