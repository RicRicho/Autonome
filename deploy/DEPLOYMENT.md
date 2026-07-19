# Autonome — deployment (autonome.ricricho.com)

This documents how the public site at **https://autonome.ricricho.com** is actually served,
so the live version is recoverable and future deploys are unambiguous.

## How it is served

- **Not** GitHub Pages, **not** Vercel, **not** the repo `site/` folder.
- Served by a **Cloudflare Worker** named **`autonome-site`**.
  - Cloudflare account: `575417eca8f9e1ed9a77f880c07a057e` (Ric@ricricho.com's Account)
  - Zone: `ricricho.com` (`761fc80f91f56bd8f542446b2089d356`)
  - Binding: DNS record `AAAA autonome.ricricho.com -> 100::` (proxied) with the Worker
    attached as a custom domain. There is **no** classic zone Workers Route.
  - The Worker is a **catch-all**: every path (`/`, `/showcase`, anything) returns the same
    single embedded HTML document. Response headers: `content-type: text/html`,
    `cache-control: public, max-age=300` (5-minute edge cache).

## Source of truth

The live HTML is **embedded inside the Worker script**, hand-authored by Max in prior jobs.
It is a self-contained single file (~175 KB) with inline CSS, an SVG favicon, and one embedded
image; zero JavaScript; no external asset dependencies.

> IMPORTANT: the repo's `site/index.html` (17 KB) and `site/showcase/index.html` (26 KB) are
> **earlier / different variants** and are **NOT** what is live. Do not assume `site/` is deployed.

## Recoverable snapshot

`deploy/live-home-2026-07-19.html` is the exact rendered live homepage captured on
2026-07-19 (08:51 UTC). If the Worker is ever lost, a Worker that returns this file's bytes
reproduces the live site.

## How to (re)deploy

Update the Worker script `autonome-site` via the Cloudflare API (multipart module PUT), e.g.:

```
PUT https://api.cloudflare.com/client/v4/accounts/575417eca8f9e1ed9a77f880c07a057e/workers/scripts/autonome-site
Authorization: Bearer <CLOUDFLARE_API_TOKEN>   # vault: CLOUDFLARE_API_TOKEN
# multipart/form-data: metadata (main_module) + a .mjs module that returns the HTML for all routes
```

The `CLOUDFLARE_API_TOKEN` in Max's vault is scoped to **Workers Scripts edit** (PUT works;
it cannot GET script content — that returns `10405 Method not allowed for this auth scheme`).

After PUT, verify: `curl -sSI https://autonome.ricricho.com/` should be `200`, and the edge
cache clears within `max-age=300` (or purge the zone cache to see changes immediately).
