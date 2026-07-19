#!/usr/bin/env python3
import re, sys

SRC = "/var/data/max-doer/jobs/997a0896-b854-455d-aa06-9b2729a6d5c5/Autonome/deploy/live-home-2026-07-19.html"
OUT = "/tmp/site_final.html"
html = open(SRC, encoding="utf-8").read()

# ---------- 1. HEAD: social cards, canonical, PostHog ----------
anchor = '<meta property="og:description" content="Autonomous intelligence. Human purpose. Trust that is earned, not simulated.">'
assert anchor in html, "og:description anchor not found"

head_add = anchor + """
<meta property="og:url" content="https://autonome.ricricho.com/">
<meta property="og:site_name" content="Autonome">
<meta property="og:image" content="https://autonome.ricricho.com/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Autonome — an artificial person that grows up.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Autonome — an artificial person that grows up">
<meta name="twitter:description" content="Autonomous intelligence. Human purpose. Trust that is earned, not simulated.">
<meta name="twitter:image" content="https://autonome.ricricho.com/og.jpg">
<link rel="canonical" href="https://autonome.ricricho.com/">
<meta name="theme-color" content="#050506">
<!-- Analytics: PostHog, cookieless (persistence:memory) — no cookie banner required -->
<script>
!function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="init capture register register_once register_for_session unregister unregister_for_session getFeatureFlag getFeatureFlagPayload isFeatureEnabled reloadFeatureFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionRecordingStarted captureException loadToolbar get_property getSessionProperty createPersonProfile opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing clear_opt_in_out_capturing debug getPageViewId".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
posthog.init('phc_xtvCtW7QgBweBxZZxjzoikRcQJDQxPZJZq8LeURXg47s',{api_host:'https://us.i.posthog.com',persistence:'memory',autocapture:false,capture_pageview:true,capture_pageleave:true,disable_session_recording:true});
</script>"""
html = html.replace(anchor, head_add, 1)

# ---------- 2. Mobile nav CSS (replace the display:none rule) ----------
old_rule = "@media(max-width:900px){.navlinks{display:none}}"
assert old_rule in html, "nav media rule not found"
new_rule = """.navactions{display:flex;align-items:center;gap:12px}
  .navtog{display:none}
  .hamb{display:none}
  @media(max-width:900px){
    .hamb{display:inline-flex;flex-direction:column;justify-content:center;gap:5px;width:42px;height:42px;cursor:pointer;border:1px solid var(--line2);border-radius:11px;padding:0 9px}
    .hamb span{display:block;width:20px;height:2px;background:var(--ink);border-radius:2px}
    .navlinks{position:absolute;top:62px;left:0;right:0;display:none;flex-direction:column;gap:0;background:rgba(6,6,8,.97);backdrop-filter:saturate(160%) blur(18px);border-bottom:1px solid var(--line);padding:6px 26px 18px}
    .navtog:checked~.navlinks{display:flex}
    .navlinks a{padding:14px 2px;border-top:1px solid var(--line);font-size:15px}
    .navcta{display:none}
  }"""
html = html.replace(old_rule, new_rule, 1)

# ---------- 3. Nav markup: hamburger + Contact link ----------
old_nav = """<nav><div class="wrap">
  <a class="mark" href="#top"><span class="orbmark"></span><span class="wm">Autonome <span>· by Ric Richardson</span></span></a>
  <div class="navlinks">
    <a href="#idea">Overview</a>
    <a href="#faces">The autonomes</a>
    <a href="#how">How it works</a>
    <a href="#battle">Battle of the bots</a>
    <a href="https://github.com/RicRicho/Autonome/blob/main/wiki/Home.md">Wiki</a>
  </div>
  <a class="navcta" href="#faces">Meet an autonome →</a>
</div></nav>"""
assert old_nav in html, "nav block not found"
new_nav = """<nav><div class="wrap">
  <a class="mark" href="#top"><span class="orbmark"></span><span class="wm">Autonome <span>· by Ric Richardson</span></span></a>
  <input type="checkbox" id="navtog" class="navtog" aria-hidden="true">
  <div class="navlinks">
    <a href="#idea">Overview</a>
    <a href="#faces">The autonomes</a>
    <a href="#how">How it works</a>
    <a href="#battle">Battle of the bots</a>
    <a href="https://github.com/RicRicho/Autonome/blob/main/wiki/Home.md">Wiki</a>
    <a href="mailto:max@mail.ricricho.com">Contact</a>
  </div>
  <div class="navactions">
    <a class="navcta" href="#faces">Meet an autonome →</a>
    <label for="navtog" class="hamb" aria-label="Toggle menu"><span></span><span></span><span></span></label>
  </div>
</div></nav>"""
html = html.replace(old_nav, new_nav, 1)

# ---------- 4. Footer: Contact mailto ----------
old_foot = """  <div class="foothref">
    <a href="https://github.com/RicRicho/Autonome/blob/main/wiki/Home.md">Full wiki</a>
    <a href="https://github.com/RicRicho/Autonome">GitHub</a>
    <a href="#top">Back to top</a>
  </div>"""
assert old_foot in html, "footer href block not found"
new_foot = """  <div class="foothref">
    <a href="https://github.com/RicRicho/Autonome/blob/main/wiki/Home.md">Full wiki</a>
    <a href="https://github.com/RicRicho/Autonome">GitHub</a>
    <a href="mailto:max@mail.ricricho.com">Contact — max@mail.ricricho.com</a>
    <a href="#top" onclick="if(window.Max&&Max.open){Max.open();return false;}">Talk with Max</a>
    <a href="#top">Back to top</a>
  </div>"""
html = html.replace(old_foot, new_foot, 1)

# ---------- 5. Chat widget (before </body>) ----------
widget = open("/tmp/widget.html", encoding="utf-8").read()
html = html.replace("</body>", widget + "\n</body>", 1)

open(OUT, "w", encoding="utf-8").write(html)
print("wrote", OUT, len(html), "bytes")
