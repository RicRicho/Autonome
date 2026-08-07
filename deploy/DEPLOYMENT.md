# Autonome — deployment (autonome.ricricho.com)

How the public site at **https://autonome.ricricho.com** is served, so the live version is
recoverable and future deploys are unambiguous.

## How it is served

- **Not** GitHub Pages, **not** Vercel, **not** the repo `site/` folder.
- Served by a **Cloudflare Worker** named **`autonome-site`** (an ES module worker).
  - Cloudflare account: `575417eca8f9e1ed9a77f880c07a057e` (Ric@ricricho.com's Account)
  - Zone: `ricricho.com` (`761fc80f91f56bd8f542446b2089d356`)
  - Binding: DNS record `AAAA autonome.ricricho.com -> 100::` (proxied) with the Worker
    attached as a **custom domain** (this survives script re-uploads).
- **Routes handled by the Worker** (`deploy/worker.mjs`):
  - `POST /api/chat`    → the sandboxed "Talk with Max" public chat endpoint (see below).
  - `POST /api/pv`      → first-party, cookieless analytics beacon (see Analytics).
  - `POST /api/contact` → contact form → AgentMail send + `autonome_contacts` (see Contact).
  - `GET  /og.jpg`      → the social-card image (embedded in the worker, `deploy/og.jpg`).
  - everything else     → the single-page site HTML (`text/html`, `max-age=300`).

## Source of truth (version-controlled)

The worker is **`deploy/worker.mjs`** — a self-contained ES module. The site HTML and the
`og.jpg` bytes are embedded inside it as base64 and decoded once per isolate. `worker.mjs` is
**generated**; do not hand-edit it. Edit the sources and rebuild:

- `deploy/gpt-home-2026-07-19.html` — **the base page**: the "male hero" redesign (a
  self-contained premium black-and-white site, all images inlined as data URIs). This replaced
  the earlier `deploy/live-home-2026-07-19.html` snapshot on 2026-07-19.
- `deploy/build/build_site.py` — injects, on top of the base page: social/canonical meta + the
  hosted `og:image` (worker `/og.jpg`), the first-party cookieless analytics beacon, PostHog,
  the contact form modal, and the "Talk with Max" chat widget. The injected overlays carry their
  own dark-theme CSS variables (scoped to their own containers) so they render correctly on the
  redesign's own design system.
- `deploy/build/widget.html` — the "Talk with Max" widget (markup + CSS + client JS).
- `deploy/build/worker_template.mjs` — the worker logic with `__HTML_B64__` / `__OG_B64__`
  placeholders.
- `deploy/og.jpg` — the social card (the redesign's 1200×630 male-hero card as of 2026-07-19).
- `deploy/live-home-2026-07-19.html` — the previous (pre-redesign) homepage snapshot, kept for
  history.
- `deploy/site-current.html` — the exact HTML the worker currently serves (rendered output).

### Rebuild

```bash
python3 deploy/build/build_site.py          # -> /tmp/site_final.html
python3 - <<'PY'                            # embed HTML + og.jpg into worker.mjs
import base64
tpl=open('deploy/build/worker_template.mjs').read()
tpl=tpl.replace('__HTML_B64__',base64.b64encode(open('/tmp/site_final.html','rb').read()).decode())
tpl=tpl.replace('__OG_B64__',base64.b64encode(open('deploy/og.jpg','rb').read()).decode())
open('deploy/worker.mjs','w').write(tpl)
PY
node --check deploy/worker.mjs
cp /tmp/site_final.html deploy/site-current.html
```

## The "Talk with Max" chat (sandboxed public persona)

`POST /api/chat` `{ "session_id": <uuid|null>, "message": <string> }` → `{ session_id, reply }`.

- **Sandboxed persona.** Calls the Anthropic API directly with a locked-down system prompt
  (public Max: **no tools, no vault, no delegated authority, conversation only**). Structurally
  cannot reach any tool or private system — this is why it is a new minimal endpoint, not a
  route through the full Max Gateway. Model: `claude-sonnet-5`.
- **Provider fallback (added 2026-08-07).** If the Anthropic call fails for any reason —
  non-2xx, network error, missing key — the worker retries the same turn once on OpenAI
  (`gpt-5.5`, binding `OPENAI_API_KEY`) before showing the "I hit a snag" line. The
  `autonome_public_chats.model` column records the model that actually answered, and when
  **both** providers fail it records `FAILED: <upstream status + body snippet>` so an outage is
  visible in the table instead of being silently swallowed.
  - Why this exists: between 2026-08-01 and 2026-08-07 the Anthropic account ran out of credit
    (`400 invalid_request_error: Your credit balance is too low`). The worker caught the error
    and returned the friendly fallback line, so **every** public chat turn for six days was
    "I hit a snag" — including Ric's own tests — with no alert anywhere. Raece Richardson
    reported it by email; nothing in the system had noticed. Triage query:
    `select model, count(*) from autonome_public_chats where model like 'FAILED:%' group by 1`.
- **Every conversation is stored** in Max's Supabase (`warp`, project `uswnbpyiepoaceretjjj`)
  in the dedicated table **`autonome_public_chats`** (`session_id`, `role`, `content`, `model`,
  `ip_hash`, `created_at`). The server is the source of truth for history; the client only holds
  a random session UUID in localStorage. Session id is validated as a UUID (else server-minted).
- **Rate limiting** is per-visitor by a salted SHA-256 hash of the client IP (never the raw IP):
  6 messages/min and 60/hour, counted from `autonome_public_chats`. Salt = binding `IP_SALT`
  (vault `AUTONOME_CHAT_IP_SALT`).
- **Prompt-injection hardening**: all visitor input is untrusted; the persona has no tools so
  injection can at most alter wording; input capped 2000 chars, history 24 msgs, output 512
  tokens; same-origin guard on `Origin`.
- **Disclosure**: the widget shows a visible notice that conversations are stored and that this
  is a sandboxed public Max with no account access.

## Analytics — first-party, cookieless, we control it

`POST /api/pv` `{ event, path, referrer }` → **`autonome_pageviews`** in the same Supabase.
The page fires `pageview` on load (via `navigator.sendBeacon`), and the widget fires
`chat_opened` / `chat_message_sent`. Stored fields: `event`, `path`, `referrer`, salted
`ip_hash`, `user_agent`, `country` (from `cf-ipcountry`), `created_at`. No cookies, no third
party, no banner. (Replaces the earlier PostHog beacon.)

## Contact — form + mailto, delivered via AgentMail

`POST /api/contact` `{ name, email, message }` → sends an email **from** Max's public inbox
`max@mail.ricricho.com` (vault `AGENTMAIL_MAX_DOMAIN_INBOX`, key `AGENTMAIL_API_KEY`) **to** the
same inbox, with the visitor's address as `reply_to`. Because inbound to `max@` routes to the
doer via the existing AgentMail webhook, contact messages reach Max. Every submission is also
mirrored into **`autonome_contacts`** (`name`, `email`, `message`, `delivered`, `agentmail_id`)
so nothing is lost if a send hiccups. Light per-IP rate limit: 5/hour. The nav + footer also
expose a plain `mailto:max@mail.ricricho.com` fallback.

## Supabase tables (Max 'warp', project `uswnbpyiepoaceretjjj`)

All three have **RLS enabled with no public policies** — only the worker's service key (which
bypasses RLS) can read/write; the anon key cannot read them.

| table | purpose |
|---|---|
| `autonome_pageviews`    | page views + widget events (analytics) |
| `autonome_public_chats` | every public chat turn |
| `autonome_contacts`     | contact-form submissions |

## Worker bindings (secrets) — RE-SUPPLY ON EVERY DEPLOY

A full script PUT **wipes all bindings** unless they are re-included. The worker needs six
`secret_text` bindings (values from Max's vault):

| binding | vault secret |
|---|---|
| `ANTHROPIC_API_KEY`    | `ANTHROPIC_API_KEY` |
| `OPENAI_API_KEY`       | `OPENAI_API_KEY` (fallback provider) |
| `SUPABASE_URL`         | (literal) `https://uswnbpyiepoaceretjjj.supabase.co` |
| `SUPABASE_SERVICE_KEY` | `SUPABASE_CANON_KEY` |
| `IP_SALT`              | `AUTONOME_CHAT_IP_SALT` |
| `AGENTMAIL_API_KEY`    | `AGENTMAIL_API_KEY` |

## How to (re)deploy

```
PUT https://api.cloudflare.com/client/v4/accounts/575417eca8f9e1ed9a77f880c07a057e/workers/scripts/autonome-site
Authorization: Bearer <CLOUDFLARE_API_TOKEN>          # vault: CLOUDFLARE_API_TOKEN
# multipart/form-data:
#   metadata = {"main_module":"worker.mjs","compatibility_date":"2025-01-01","bindings":[ ...5 secret_text... ]}
#   worker.mjs = @deploy/worker.mjs ;type=application/javascript+module
```

`CLOUDFLARE_API_TOKEN` is scoped to **Workers Scripts edit** (PUT works; it cannot GET script
content). After PUT: `curl -sSI https://autonome.ricricho.com/` should be `200`; smoke-test the
chat with a `POST /api/chat` carrying `Origin: https://autonome.ricricho.com`.

## Schema changes are governed

The `warp` Supabase blocks raw DDL (`warp_ddl_shield` event trigger). CREATE/ALTER/DROP require
an approved writer: run `set app.writer = 'claude-code';` (or `'ric'` / `'claude-fable'`) in the
same session before the DDL, via the Supabase Management API
(`POST /v1/projects/{ref}/database/query`, bearer `SUPABASE_ACCESS_TOKEN`). Plain INSERT/UPDATE
are not gated.

> The Cloudflare zone serves its own managed `/robots.txt` (AI-crawler content-signals policy),
> which overrides the worker's `/robots.txt` route — expected.

## Canary (cron trigger, added 2026-08-07)

The worker has a `scheduled()` handler wired to a Cloudflare cron trigger **`10 22 * * *`**
(22:10 UTC = 08:10 AEST daily). Each run checks:

1. Anthropic `/v1/messages` answers (4-token ping on `MODEL`),
2. OpenAI `/v1/chat/completions` answers (the fallback provider),
3. `https://patentmachine.com.au/api/chat` returns a real answer rather than its
   "hiccup reaching my brain" error line.

If anything fails it emails `max@mail.ricricho.com` via AgentMail — which routes inbound to the
Max doer, so a degraded chat becomes a job instead of sitting unseen. **Silence means healthy**;
the canary sends nothing when everything works.

Set/inspect the schedule:

```
PUT/GET https://api.cloudflare.com/client/v4/accounts/575417eca8f9e1ed9a77f880c07a057e/workers/scripts/autonome-site/schedules
Authorization: Bearer <CLOUDFLARE_API_TOKEN>
body: [{"cron":"10 22 * * *"}]
```

Note: a script PUT does **not** wipe cron triggers (unlike bindings), but re-check after any
deploy that replaces the script via a different tool.
