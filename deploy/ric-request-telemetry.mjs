// Imported by a wrapper around each existing public worker's original default export.
// No bodies, cookies, query strings, IP addresses or authorisation headers are collected.
export function recordRequest(request, ctx) {
  const url = new URL(request.url);
  const ua = (request.headers.get('user-agent') || '').slice(0, 1024);
  const payload = {site:url.hostname,path:url.pathname.slice(0,512),event:'request:unknown',ua};
  ctx.waitUntil(fetch('https://uswnbpyiepoaceretjjj.supabase.co/functions/v1/track', {
    method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),signal:AbortSignal.timeout(5000)
  }).then(r => {if (!r.ok) console.warn('Traffic collection failed',r.status);}).catch(() => console.warn('Traffic collection unavailable')));
}
