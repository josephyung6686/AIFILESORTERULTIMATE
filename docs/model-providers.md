# AI model providers

The understanding pass (`docs/model-assisted-understanding.md`) uses an API
key. Bring-your-own-key is the supported default: DeepSeek, then any
OpenAI-compatible endpoint, then a local model on loopback. Signing in with
a ChatGPT or Claude subscription is not how that pass authenticates. A
login scraper is not implemented. The notes below say what an official
OAuth route would require if a provider opens one, and what is already
gated off in this tree.

This is the user-facing and engineering description of how a folder picks a
model. Files stay on disk until a freeze and an apply. A cloud model is never
asked about a file the sensitivity gate is holding, and it is never asked
without the folder's own consent. Abstaining is a successful outcome.

The command is `filesorter` or `database-agent`. They are the same program.

## The three lanes

| Lane | What you can do today | What is not built |
| --- | --- | --- |
| Managed / plan-included | The list shows it as **coming later**. Selecting it refuses. | There is no included-plan backend and no fake one. |
| Subscription sign-in | **Continue with ChatGPT** is shown. It runs only when `FILESORTER_OPENAI_SIWC=1`. Claude subscription is shown as not available. | No Claude.ai login. No browser-cookie or `~/.codex/auth.json` import. |
| API key (bring your own) | DeepSeek, OpenAI, Anthropic, and any OpenAI-compatible HTTPS endpoint. | Native Bedrock SigV4 and Vertex OAuth are not implemented. Point an Anthropic-compatible HTTPS URL at the Messages path if you already have one. |

DeepSeek remains the cloud default when `DEEPSEEK_API_KEY` is set and this
folder has not stored a different provider. A scan with no key and no stored
choice does what it did before: it sorts from the files and says no model was
consulted.

## Where this sits in onboarding

The order is the profile questions, then this step, then the first scan.
`filesorter providers` is that middle step. It writes the choice into the
profile record in the plan database. It does not write the secret there.

```
filesorter providers
filesorter providers list
filesorter providers add openai
filesorter providers add anthropic
filesorter providers add deepseek
filesorter providers add openai-compatible --base-url https://example.invalid/v1 --model your-model
filesorter providers remove openai
filesorter providers use byok openai --model your-model
filesorter providers dry-run openai --model your-model
filesorter providers dry-run anthropic --model your-model
FILESORTER_OPENAI_SIWC=1 filesorter providers sign-in-chatgpt
FILESORTER_CLAUDE_CODE=1 filesorter providers claude-code --prompt 'Reply with one JSON object {"ok": true}'
```

`add` asks for the key with no echo. The key is not printed and not stored in
the plan database. `remove` deletes the keychain item; adding again is the
rotation. `dry-run` prints the endpoint, the model, and the request shape. It
sends nothing and reads no file.

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
- `openai-siwc-access`, `openai-siwc-refresh`, `openai-siwc-registration` —
  ChatGPT sign-in, only after a verified token response

The registration item is JSON with the issued client id, host id, expiry,
scopes, and subject. It is still a secret. Nothing in this list is written to
the plan database, a log line, or an exception. On a machine without the
`security` command the keychain commands refuse; they do not fall back to a
file.

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

The flag is off by default. With it off, `filesorter providers` still shows
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

**TODO.** ID-token signature verification against OpenAI's published JWKS for
issuer `https://auth.openai.com` is not implemented. Structural checks (issuer,
audience, expiry, nonce) run, and a token response is refused — not stored —
until a verifier reports the signature good. The live command with the flag on
stops before opening a browser for that reason and tells you to use an API key.
Guessing a JWKS URL was the less safe option, so it was not done.

This program does not read `~/.codex/auth.json`, a Claude Code keychain item,
or a browser cookie.

## Claude subscription

Not shipped, on purpose. Anthropic's legal and compliance page says developers
may not offer Claude.ai login in their own apps, may not route Free, Pro, or
Max credentials, and may not collect, store, or intermediate Claude.ai
credentials or session tokens:

https://code.claude.com/docs/en/legal-and-compliance

The provider list says: **not available — Anthropic policy. Use an API key or
Claude Code.**

The same page says this does not prevent a person from signing in to the
unmodified Claude Code binary. `filesorter providers claude-code` is that
path, and only when `FILESORTER_CLAUDE_CODE=1`. It runs `claude -p` with the
prompt. It does not read Claude Code's tokens. If `claude` is not on `PATH`,
the command says to install it or use an API key. Anthropic can change
enforcement without notice; if they do, turn the flag off. This document does
not say Anthropic approved this product.

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
| ChatGPT subscription | Sign in with ChatGPT | Official OAuth + PKCE, flag off until partner access. No borrowed Codex tokens. |
| Claude subscription | They offer a Claude sign-in | Refused. Anthropic's published policy does not allow it. |
| Claude on the machine | | Optional unmodified `claude -p`, flag off by default. We never see the login. |
| API keys | Bring your own key | DeepSeek, OpenAI, Anthropic, OpenAI-compatible HTTPS. Keychain or environment. |
| Secrets in the plan | | Never. Keychain service `filesorter`, or the environment. |
