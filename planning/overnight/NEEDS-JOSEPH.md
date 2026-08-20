# NEEDS JOSEPH — decisions only you can make

Date: 2026-08-21 (overnight run)
Status: **accumulating.** Nothing here was decided for you.

Each row is a question I refused to answer because answering it would be inventing
your product rather than building it. Where I had to proceed to keep working, the
assumption I made is stated so you can overturn it cheaply.

## How to read this

| Column | Meaning |
|---|---|
| **Blocks** | what stays wrong or unbuilt until you answer |
| **My assumption** | what the code/plan does today, so nothing was silently decided |
| **Cost to change** | how expensive your answer is to apply if it differs |

---

## A. Scope and jurisdiction

*(filled by the domain agents)*

## B. Domains — the schema and template calls

*(filled by the domain agents)*

## C. P6 / P7 plan questions

*(filled by the plan agents)*

## D. P1–P5 audit questions

*(filled by the audit agents)*

## E. Carried forward from earlier sessions

| # | Question | Blocks | My assumption |
|---|---|---|---|
| E1 | The 42 `uncertain` rows in `planning/deferred-catalogues/` are still unresolved — entries I could not classify from a citable source. | The gazetteers cannot ship complete. | Left `uncertain`, not guessed. |
| E2 | `.pages`, `.key`, `.swift`, `.ts`, `.go` route as `unsupported`. §2.4 and §2.9 do not name them. | Those files get a filename and nothing else. | Spec-faithful: left unrouted rather than invented. |
| E3 | `.numbers` routes as a spreadsheet, but a real Numbers file is often a **package**. P3 Q7 (packages) is open. | A silent empty extraction on a common Mac format. | Left as the SPEC's routing says. |
| E4 | Filename normalization NFC vs NFD (P3 Q1) is open; macOS stores NFD. | `normalized_filename` is P3's raw `path.name`, so it is not actually normalized. | Passed through unchanged, and P5 labels it `direct` metadata. |
