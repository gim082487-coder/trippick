#!/usr/bin/env python3
"""v58 라이브 검증 — https://trippick.pages.dev/coupons 1280·390 스크린샷 + 탭 동작·오류 확인."""
from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path("/workspace/trippick_repo/v58_shots")
OUT.mkdir(exist_ok=True)
URL = "https://trippick.pages.dev/coupons"
report = {}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/workspace/.tools/cft/chrome-linux64/chrome",
                          args=["--no-sandbox", "--disable-dev-shm-usage"])
    for w, tag in ((1280, "live_pc"), (390, "live_mo")):
        ctx = b.new_context(viewport={"width": w, "height": 900 if w > 500 else 844}, device_scale_factor=1)
        pg = ctx.new_page()
        errs: list[str] = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(URL, wait_until="load")
        pg.wait_for_timeout(1200)
        pg.screenshot(path=str(OUT / f"{tag}_coupons_top.png"))
        pg.evaluate("()=>window.scrollTo(0, document.body.scrollHeight*0.35)")
        pg.wait_for_timeout(400)
        pg.screenshot(path=str(OUT / f"{tag}_coupons_mid.png"))
        pg.evaluate("()=>window.scrollTo(0, document.body.scrollHeight*0.75)")
        pg.wait_for_timeout(400)
        pg.screenshot(path=str(OUT / f"{tag}_coupons_low.png"))
        data = pg.evaluate("""() => {
          const doc = document.documentElement;
          const over = [];
          document.querySelectorAll('body *').forEach(el => {
            const r = el.getBoundingClientRect();
            if (r.width > 0 && r.right > doc.clientWidth + 2 &&
                getComputedStyle(el).overflowX !== 'auto' &&
                !el.closest('.tb-scroll') && !el.closest('.cpn-tabs'))
              over.push((el.className || el.tagName) + ':' + Math.round(r.right - doc.clientWidth));
          });
          return {
            url: location.href, title: document.title,
            scrollW: doc.scrollWidth, clientW: doc.clientWidth,
            broken: [...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.src),
            overflow: over.slice(0, 6),
            cards: document.querySelectorAll('.cpn[data-cat]').length,
            tabs: [...document.querySelectorAll('.cpn-tab')].map(t => t.textContent.trim()),
            canonical: (document.querySelector('link[rel=canonical]') || {}).href,
          };
        }""")
        pg.evaluate("()=>window.scrollTo(0, 0)")
        pg.click('button.cpn-tab[data-filter="asia"]')
        pg.wait_for_timeout(400)
        data["asia"] = pg.evaluate("""() => ({
          vis: [...document.querySelectorAll('.cpn-sec')].filter(s => !s.hidden).map(s => s.dataset.cat),
          cards: [...document.querySelectorAll('.cpn[data-cat]')].filter(c => c.offsetParent !== null).length,
        })""")
        pg.screenshot(path=str(OUT / f"{tag}_coupons_asia.png"))
        data["pageerrors"] = errs
        report[tag] = data
        ctx.close()
    b.close()
print(json.dumps(report, ensure_ascii=False, indent=1))
