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
  - `POST /api/chat` → the "Talk with Max" public chat endpoint (see below).
  - `GET /og.jpg` → the social-card image (embedded in the worker, `deploy/og.jpg`).
  - everything else → the single-page site HTML (`content-type: text/html`,
    `cache-control: public, max-age=300`).

## Source of truth (now version-controlled)

The worker is **`deploy/worker.mjs`** — a self-contained ES module. The site HTML and the
`og.jpg` bytes are embedded inside it as base64 and decoded once per isolate. `worker.mjs` is
**generated**; do not hand-edit it. Edit the sources and rebuild:

- `deploy/build/build_site.py` — injects social/canonical meta, cookieless PostHog analytics,
  the mobile nav, the contact links, and the chat widget into the captured live homepage.
- `deploy/build/widget.html` — the "Talk with Max" widget (markup + CSS + client JS).
- `deploy/build/worker_template.mjs` — the worker logic with `__HTML_B64__` / `__OG_B64__`
  placeholders.
- `deploy/site-current.html` — the exact HTML the worker currently serves (rendered output).
- `deploy/live-home-2026-07-19.html` — the pre-2026-07-19 snapshot (kept for history).

### Rebuild

```bash
python3 deploy/build/build_site.py           # -> /tmp/site_final.html (needs widget.html)
# then embed site_final.html + og.jpg (base64) into worker_template.mjs -> worker.mjs
node --check deploy/worker.mjs
```

## The "Talk with Max" chat (sandboxed public persona)

`POST /api/chat` `{ "session_id": <uuid|null>, "message": <string> }` → `{ session_id, reply }`.

- **Sandboxed persona.** The endpoint calls the Anthropic API directly with a locked-down
  system prompt (public Max: **no tools, no vault, no delegated authority, conversation only**).
  It structurally cannot reach any tool or private system — this is why it is a new minimal
  endpoint rather than a route through the full Max Gateway. Model: `claude-haiku-4-5`.
- **Every conversation is stored** in Max's Supabase (`warp`, project `uswnbpyiepoaceretjjj`):
  `wm_conversations` with `mode = 'autonome_public_chat'`, `user_id = 'autonome-public'`, and
  `wm_messages` with `source = 'text'` + `metadata.channel = 'autonome_public'`. The server is
  the source of truth for history; the client only holds a random session UUID in localStorage.
- **Rate limiting** is per-visitor by a salted SHA-256 hash of the client IP (never the raw IP):
  6 messages/min and 60/hour. Salt = binding `IP_SALT` (vault `AUTONOME_CHAT_IP_SALT`).
- **Prompt-injection hardening**: all visitor input is treated as untrusted; the persona has no
  tools so injection can at most alter wording; input capped at 2000 chars, history at 24 msgs,
  output at 512 tokens; same-origin guard on `Origin`.
- **Disclosure**: the widget shows a visible notice that conversations are stored and that this
  is a sandboxed public Max with no account access.

## Analytics

Cookieless **PostHog** (`persistence: 'memory'`) in the page `<head>` — page views, referrers,
`chat_opened` / `chat_message_sent` events. No cookies → no cookie banner needed. Project key is
a public client key (safe to ship). Alternative on the table: Cloudflare Web Analytics.

## Worker bindings (secrets) — RE-SUPPLY ON EVERY DEPLOY

A full script PUT **wipes all bindings** unless they are re-included. The worker needs four
`secret_text` bindings (values from Max's vault):

| binding | vault secret |
|---|---|
| `ANTHROPIC_API_KEY` | `ANTHROPIC_API_KEY` |
| `SUPABASE_URL` | (literal) `https://uswnbpyiepoaceretjjj.supabase.co` |
| `SUPABASE_SERVICE_KEY` | `SUPABASE_CANON_KEY` |
| `IP_SALT` | `AUTONOME_CHAT_IP_SALT` |

## How to (re)deploy

```
PUT https://api.cloudflare.com/client/v4/accounts/575417eca8f9e1ed9a77f880c07a057e/workers/scripts/autonome-site
Authorization: Bearer <CLOUDFLARE_API_TOKEN>          # vault: CLOUDFLARE_API_TOKEN
# multipart/form-data:
#   metadata = {"main_module":"worker.mjs","compatibility_date":"2025-01-01","bindings":[ ...4 secret_text... ]}
#   worker.mjs = @deploy/worker.mjs ;type=application/javascript+module
```

`CLOUDFLARE_API_TOKEN` is scoped to **Workers Scripts edit** (PUT works; it cannot GET script
content). After PUT: `curl -sSI https://autonome.ricricho.com/` should be `200`; the chat can be
smoke-tested with a `POST /api/chat` carrying `Origin: https://autonome.ricricho.com`.

> The Cloudflare zone serves its own managed `/robots.txt` (AI-crawler content-signals policy),
> which overrides the worker's `/robots.txt` route — expected.
