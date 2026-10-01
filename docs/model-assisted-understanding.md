# Model-assisted understanding

The deterministic tier still runs first. This pass asks a model only about
files that tier did not place, and only after a one-time consent. Whole
files are not sent. Protected files, held files, and areas marked private
are not sent. `offline` sends nothing.

The roles are fixed:

| Role | Env name | Used for |
| --- | --- | --- |
| FAST | `DEEPSEEK_MODEL_FAST` | Per-file classification |
| LOGIC | `DEEPSEEK_MODEL_LOGIC` | Tree and grouping decisions |
| REASONING | `DEEPSEEK_MODEL_REASONING` | Hard conflicts, and the onboarding questions generated from filenames |

A run reads `GET {DEEPSEEK_BASE_URL}/models` once before it sends. The
configured id must be in that list. `deepseek-v4-flash` and `deepseek-flash`
are aliases of each other: if only one is listed, that one is used. Any
other missing id is an error that names the id and the list. There is no
fallback onto another tier.

The template in `.env.example` uses the ids a live `/models` call listed on
2026-10-01 (`deepseek-flash`, `deepseek-v4-pro`) plus `deepseek-chat` for
logic, which is the id chat completions were measured with. This checkout
cannot call the API. The Mac run is the check that those ids still resolve.

## What is sent

A dossier is JSON with only these fields:

- `filename`
- `path_hints` (directory names)
- `kind` (already known, or empty)
- `text_excerpt` (the first 400 words of text or OCR)
- `metadata` (scalar keys the caller already extracted)

The model must answer one JSON object: `kind`, `life_area`, `course`,
`term`, `company`, `project`, `concerns` (`user`, `someone_else`, or
`unknown`), `confidence` (0 to 1), `evidence_quote` (one line).
`life_area` has to be one of the areas declared for this folder, or
`needs_review`. A name that was not declared, including Business, is not
stored as a category. Confidence below 0.6 is needs-review. Malformed JSON
is rejected.

## Reasoning models

The request sets `thinking` to `disabled`. The answer is `content`.
`reasoning_content` is never the answer. Empty `content` with
`finish_reason: length` is a retry at four times the token budget. A second
empty content is needs-review, not a classification.

## Consent, cache, budget, audit

Consent is one row per folder, the sentence in
`understanding.store.STATEMENT`, recorded by
`--accept-cloud-understanding`. It says dossier text goes to the provider's
servers.

The cache key is the SHA-256 of the dossier, the model id, and the prompt
version `understanding-1`. A hit does not call the provider.

The budget defaults to 200 calls and 200,000 estimated input tokens. When
the next call would not fit, the remaining files are needs-review with
reason `budget stop`. The budget is reserved before a call is launched, so
a pool cannot start more calls than the cap.

Small dossiers share a call, up to 8. Separate batches run together, up to
4 at a time. A response of HTTP 429 is not an answer: the call waits for
the provider's Retry-After (or a growing delay, capped at 60 seconds) and
tries again, four tries in all. The wait is not an answer either.

Every call appends an audit row: file id, the field names, the model id,
prompt tokens, completion tokens, and whether it was a cache hit. There is
no key column.

## Dry-run

```
database-agent ~/star-sorter-test/dl --model-dry-run
```

Nothing is read out of the files and nothing is sent. The count is an
upper bound, because the deterministic tier has not run. The output names
the fields, the token estimates, and the cost formula. It does not fill in
a price.

## Onboarding questions

Filenames only. The REASONING model writes a short summary and follow-up
questions. LOGIC is the grouping call (`understanding.roles.group_files`).
REASONING is also the conflict call (`resolve_conflict`). Neither one is
used to classify an ordinary file, and neither one may invent an area.

```
database-agent ~/star-sorter-test/dl --onboarding-questions --enable-cloud --accept-cloud-understanding --declare-life coursework=academic
```

Without those two consent flags the command prints the consent sentence and
sends nothing. It does not open the files.

## A real pass

```
database-agent ~/star-sorter-test/dl --enable-cloud --accept-cloud-understanding --understand --declare-life coursework=academic
```

`--enable-cloud` is the existing per-folder cloud consent. The understanding
pass also requires `--accept-cloud-understanding`. `--declare-life` is the
closed set of areas the model may choose. FAST is the classification model.
Add `--private-area medical` for an area that must not be sent.

## Cost

No price is stored in this repository.

```
input_tokens  = len(dossier_json) / 4
output_tokens = files * 512
cost          = input_tokens  * input_usd_per_million  / 1000000
              + output_tokens * output_usd_per_million / 1000000
```

`input_usd_per_million` and `output_usd_per_million` are the provider's
published prices for the model id `/models` resolved. This document does
not invent them.

## Providers

`ModelProvider` is `complete(request) -> chat completion dict`. DeepSeek,
an OpenAI-compatible HTTPS endpoint (your own key, base URL, and model
ids), and Ollama on `127.0.0.1` or `localhost` only. Keys come from the
environment, `.env`, or the macOS Keychain helper in
`readers/model_keychain.py`. They are not written into the plan database
and not printed.

Sign-in with a ChatGPT or Claude subscription is not this pass. See
`docs/model-providers.md`.
