# AI model providers

The understanding pass (`docs/model-assisted-understanding.md`) follows the
provider you stored. Bring-your-own-key is the supported default: DeepSeek,
OpenAI, Anthropic's Messages API, or any OpenAI-compatible endpoint, then a
local model on loopback. Continue with ChatGPT is OpenAI's published OAuth
flow, and it runs on this machine only when `FILESORTER_OPENAI_SIWC=1`.
Claude subscription login is not implemented. A login scraper is not
implemented. This program does not read browser cookies, `~/.codex/auth.json`,
or Claude Code's keychain.

This is the user-facing and engineering description of how a folder picks a
model. Files stay on disk until a freeze and an apply. A cloud model is never
asked about a file the sensitivity gate is holding, and it is never asked
without the folder's own consent. Abstaining is a successful outcome.

The command is `filesorter` or `database-agent`. They are the same program.

## The three lanes

| Lane | What you can do today | What is not built |
| --- | --- | --- |
| Managed / plan-included | The list shows it as **coming later**. Selecting it refuses. | There is no included-plan backend and no fake one. |
| Subscription sign-in | **Continue with ChatGPT** is live on this machine when `FILESORTER_OPENAI_SIWC=1`. Commercial plan usage still waits on OpenAI's partner access. Claude subscription is the sentence "use Claude Code or an API key — Anthropic policy." | No Claude.ai login. No browser-cookie or `~/.codex/auth.json` import. No Free, Pro, or Max OAuth. |
| API key (bring your own) | DeepSeek, OpenAI, Anthropic, and any OpenAI-compatible HTTPS endpoint. | Native Bedrock SigV4 and Vertex OAuth are not implemented. Point an Anthropic-compatible HTTPS URL at the Messages path if you already have one. |

DeepSeek remains the cloud default when `DEEPSEEK_API_KEY` is set and this
folder has not stored a different provider. Understanding runs on a normal
scan. A scan with no key and no stored choice does not sort first and does
not call: it exits and tells you to set up a model provider, naming
`database-agent onboard` and `database-agent providers`, or `DEEPSEEK_API_KEY` and
`DEEPSEEK_MODEL_FAST`.

## Where this sits in onboarding

The order is the profile questions, then this step, then the first scan.
`database-agent providers` is that middle step. It writes the choice into the
profile record in the plan database. It does not write the secret there.

```
database-agent providers
database-agent providers list
database-agent providers status
database-agent providers add openai
database-agent providers add anthropic
database-agent providers add deepseek
database-agent providers add openai-compatible --base-url https://example.invalid/v1 --model your-model
database-agent providers remove openai
database-agent providers use byok openai --model your-model
database-agent providers dry-run openai --model your-model
database-agent providers dry-run anthropic --model your-model
FILESORTER_OPENAI_SIWC=1 database-agent providers sign-in-chatgpt
FILESORTER_CLAUDE_CODE=1 database-agent providers claude-code --prompt 'Reply with one JSON object {"ok": true}'
```

`add` asks for the key with no echo. The key is not printed and not stored in
the plan database. `remove` deletes the keychain item; adding again is the
rotation. `status` prints the stored lane and whether each key is present or
absent. `dry-run` prints the endpoint, the model, and the request shape. It
sends nothing, reads no file, and opens no network connection. Managed still
refuses. Continue with ChatGPT and Claude Code stay behind their flags.

A cloud call during a scan still needs the folder's consent and
`--enable-cloud`, same as DeepSeek. The dry-run does not send a dossier, so it
does not spend that consent.

## API keys

| Provider | Environment variable | Keychain account (`security` service `filesorter`) | Request |
| --- | --- | --- | --- |
| DeepSeek | `DEEPSEEK_API_KEY` | `deepseek-api-key` | OpenAI-compatible Chat Completions, existing client |
| OpenAI | `OPENAI_API_KEY` | `openai-api-key` | `POST https://api.openai.com/v1/chat/completions`, `Authorization: Bearer` |
| Anthropic | `ANTHROPIC_API_KEY` | `anthropic-api-key` | `POST https://api.anthropic.com/v1/messages`, `x-api-key` and `anthropic-version: 2023-06-01` |
| OpenAI-compatible | `OPENAI_COMPATIBLE_API_KEY` | `openai-compatible-api-key` | Same Chat Completions JSON at the HTTPS base URL you set |

Resolution order for a key: the environment, then `.env` for DeepSeek's
existing path, then the keychain when the stored choice says `keychain`.
The environment wins over the keychain, so a shell export overrides a stored
key without printing it.

Model ids are yours. This program does not pick one. Examples you might set,
and then replace, are whatever your account actually offers. The variables are
`OPENAI_MODEL`, `ANTHROPIC_MODEL`, and `OPENAI_COMPATIBLE_MODEL`, or
`--model` on the command. One named model answers every tier, and the record
says that name. That is the same rule as a single local model, not a silent
downgrade from a model nobody chose.

OpenAI's Chat Completions reference is
https://platform.openai.com/docs/api-reference/chat/create.
Anthropic's Messages reference is
https://docs.anthropic.com/en/api/messages.
DeepSeek stays on the client already in `src/readers/model_deepseek.py`.

JSON mode on the OpenAI-shaped calls requires the prompt to contain the word
"json". The product prompts already do. A call whose prompt does not is
refused before it is sent.

## Keychain layout

macOS `security`, service `filesorter`:

- `deepseek-api-key`, `openai-api-key`, `anthropic-api-key`,
  `openai-compatible-api-key` — API keys
- `openai-siwc-host` — this app's `ext_agent_host_id`
- `openai-siwc-access`, `openai-siwc-refresh`, `openai-siwc-registration` —
  ChatGPT sign-in, only after the ID token signature verifies

The registration item is JSON with the issued client id, host id, expiry,
scopes, subject, the ID token (for a later `id_token_hint`), and the model
id when you passed `--model`. It is still a secret. Nothing in this list is
written to the plan database, a log line, or an exception. On a machine
without the `security` command the keychain commands refuse; they do not
fall back to a file.

## Sign in with ChatGPT

Followed:

- https://developers.openai.com/siwc/quickstart
- https://developers.openai.com/siwc/token-sharing-open-source/sign-in
- https://developers.openai.com/cookbook/articles/sign-in-with-chatgpt
- https://developers.openai.com/siwc/token-sharing-open-source/models-and-inference
- https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations

The quickstart says ChatGPT plan usage is available to open-source partners
and selected private clients, and that commercial partners are in a limited
trial. This checkout did not find a separate waitlist form URL on that page,
so the flag-off text links the quickstart itself.

The flag is off by default. With it off, `database-agent providers` still shows
Continue with ChatGPT and explains that an API key is what works today. Set
`FILESORTER_OPENAI_SIWC=1` only after OpenAI's partner access applies to this
app. There is no profile switch that turns the flag on by itself.

What the code builds, from those pages and not from a guessed client:

- Authorize: `https://auth.openai.com/api/accounts/authorize`
- First sign-in uses `client_id=dynamic_agent_client`, `agent_name_hint=filesorter`,
  and an app-generated `ext_agent_host_id`
- Loopback `http://127.0.0.1:<port>/auth/callback` (not `localhost`)
- PKCE S256
- Scopes `openid profile email offline_access resource.invoke chatgpt.tokens.use.direct`
- Resource `https://api.openai.com/v1`
- Token: `POST https://auth.openai.com/api/accounts/oauth/token` with the
  **issued** client id, never `dynamic_agent_client`
- Refresh omits `scope` so the grant is kept
- Inference: `POST https://api.openai.com/v1/responses` with the access token,
  `store: false`, `stream: true`, and `input` as an array
- An expired access token is refreshed. If the refresh is refused, the prompt
  is **Reauthenticate** and the old access token is not sent
- ID tokens are checked as RS256 against the JWKS URI the website page
  publishes for issuer `https://auth.openai.com`:
  `https://auth.openai.com/.well-known/jwks.json`. A bad signature is not
  stored. `alg` other than RS256 fails closed.

With the flag off, `database-agent providers sign-in-chatgpt` exits 2, prints
the quickstart limit, and does not open a browser or a plan database.
`FILESORTER_OPENAI_SIWC=1` is the local sign-in. It binds
`127.0.0.1` on an ephemeral port, opens the authorize URL, exchanges the
issued client id, verifies the ID token, and stores the tokens in the
keychain. That flag is not a grant of commercial rights. OpenAI's quickstart
says ChatGPT plan usage is limited to open-source partners and selected
private clients, and that commercial partners are in a limited trial. This
checkout found no separate waitlist form URL, so both the flag-off text and
this page point at the quickstart.

This program does not read `~/.codex/auth.json`, a Claude Code keychain item,
or a browser cookie.

## Claude subscription

Not shipped, on purpose. Anthropic's legal and compliance page says developers
may not offer Claude.ai login in their own apps, may not route Free, Pro, or
Max credentials, and may not collect, store, or intermediate Claude.ai
credentials or session tokens:

https://code.claude.com/docs/en/legal-and-compliance

The provider list says: **use Claude Code or an API key — Anthropic policy.**
Sign in inside Claude Code. Selecting Claude as a subscription refuses.

Why this program does not ship Claude.ai OAuth:

- Anthropic's page forbids offering Claude.ai login, routing Free, Pro, or
  Max credentials, and collecting or storing those session tokens.
- A cookie scrape of claude.ai would be that ban, so it is not implemented.
- Reading Claude Code's keychain items, or `~/.claude`, would be handling
  those tokens, so the binary is spawned unmodified and its login stays
  inside it.
- Intermediating Anthropic's OAuth in this app is the same ban. The screen
  tells you to sign in inside Claude Code, or to use an API key.

The same page says this does not prevent a person from signing in to the
unmodified Claude Code binary. `database-agent providers use byok claude-code`
stores that choice with no credential. `database-agent providers claude-code`
runs `claude -p` with the prompt, and only when `FILESORTER_CLAUDE_CODE=1`.
The understanding pass uses the same unmodified argv when that choice is
stored and the flag is on. If `claude` is not on `PATH`, the command says
to install it and sign in inside Claude Code, or use an API key. The list
shows whether `claude` is on `PATH`. Being on `PATH` does not switch a scan
over by itself. Anthropic can change enforcement without notice; if they
do, turn the flag off. This document does not say Anthropic approved this
product.

## Consent, audit, cache, budget

API-key and ChatGPT-plan calls go out as a `ModelClient` through the existing
transport. The gate, the dossier, the consent check, the dry-run of a scan,
the cache, and the budget are the ones DeepSeek already uses. A provider
module does not send a file by a side door. `providers dry-run` is not a
dossier call: it prints the shape and stops.

The plan database records the lane, the provider name, whether the secret
lives in the environment or the keychain, and the model id when you set one.
That is the profile record. It is not a copy of the secret.

## How Aside does it, and how this program does it

| | Aside | This program |
| --- | --- | --- |
| Managed plan | A plan included with their product | Shown as coming later. No backend. |
| ChatGPT subscription | Sign in with ChatGPT | Official OAuth + PKCE. Runnable locally when `FILESORTER_OPENAI_SIWC=1`, after the ID token verifies. Commercial use waits on OpenAI's partner access. No borrowed Codex tokens. |
| Claude subscription | They offer a Claude sign-in | Refused: "use Claude Code or an API key — Anthropic policy." No Claude.ai OAuth, no cookie scrape, no keychain token read. |
| Claude on the machine | | Optional unmodified `claude -p`, and only when you choose it and set `FILESORTER_CLAUDE_CODE=1`. Sign in inside Claude Code. We never see the login. |
| API keys | Bring your own key | DeepSeek, OpenAI, Anthropic Messages, OpenAI-compatible HTTPS. Keychain or environment. The provider list is the picker. |
| Secrets in the plan | | Never. Keychain service `filesorter`, or the environment. |

## On a Mac

The plan database stays outside the folder you scan. Fill
`profiles/answers.alana.json` before a first scan; the shipped copy is a
template and a scan refuses it until the TODOs are filled and `confirmed`
is true. Nothing below was run against live OpenAI from this checkout: the
browser redirect, the JWKS fetch, the token endpoint, the Responses stream,
and whether this app is inside the commercial trial are for your machine.

Flag off. `providers` lists the three lanes and exits 0. `sign-in-chatgpt`
exits 2, points at the quickstart, and does not open a browser:

```
database-agent providers
database-agent providers sign-in-chatgpt
```

Local ChatGPT sign-in, then a scan that may send. `<model-the-plan-allows>`
is a model id your ChatGPT plan actually returns. The flag is local use,
not commercial approval:

```
FILESORTER_OPENAI_SIWC=1 database-agent providers sign-in-chatgpt \
  --database ~/star-sorter-test/plan.sqlite \
  --model <model-the-plan-allows>
filesorter ~/star-sorter-test/dl \
  --database ~/star-sorter-test/dl-plan.sqlite \
  --answers ~/star-sorter-test/answers.alana.json
```

Claude Code. Sign in inside Claude Code. This app does not read that login:

```
FILESORTER_CLAUDE_CODE=1 database-agent providers use byok claude-code \
  --database ~/star-sorter-test/plan.sqlite
FILESORTER_CLAUDE_CODE=1 database-agent providers claude-code \
  --prompt 'Reply with one JSON object {"ok": true}'
```

DeepSeek from `.env` does not need the `models` extra. Fact, situation, and
understanding calls post chat completions with the standard library. Reinstall
from the app checkout with `pip install -e '.[dev,readers]'`, then the scan
under "On a Mac" above. The `models` extra is the Anthropic SDK.

API keys. `add` asks for the key with no echo:

```
database-agent providers add deepseek --database ~/star-sorter-test/plan.sqlite
database-agent providers add openai --model your-model --database ~/star-sorter-test/plan.sqlite
database-agent providers add anthropic --model your-model --database ~/star-sorter-test/plan.sqlite
database-agent providers use byok openai --model your-model --database ~/star-sorter-test/plan.sqlite
database-agent providers dry-run anthropic --model your-model
```
