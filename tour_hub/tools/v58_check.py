#!/usr/bin/env python3
"""v58 검증 — /coupons 5개 카테고리 탭·필터 동작, 1280·390 렌더, 가로 넘침·pageerror 0."""
from __future__ import annotations

import functools
import http.server
import json
import socketserver
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = "/workspace/trippick_repo/deploy_site"
OUT = Path("/workspace/trippick_repo/v58_shots")
OUT.mkdir(exist_ok=True)
Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)


class Q(socketserver.TCPServer):
    allow_reuse_address = True


srv = Q(("127.0.0.1", 8118), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

report = {}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/workspace/.tools/cft/chrome-linux64/chrome",
                          args=["--no-sandbox", "--disable-dev-shm-usage"])
    for w, tag in ((1280, "pc"), (390, "mo")):
        ctx = b.new_context(viewport={"width": w, "height": 900 if w > 500 else 844}, device_scale_factor=1)
        pg = ctx.new_page()
        errs: list[str] = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto("http://127.0.0.1:8118/coupons.html", wait_until="load")
        pg.wait_for_timeout(900)
        pg.screenshot(path=str(OUT / f"{tag}_coupons_top.png"))
        pg.evaluate("()=>window.scrollTo(0, document.body.scrollHeight*0.33)")
        pg.wait_for_timeout(400)
        pg.screenshot(path=str(OUT / f"{tag}_coupons_mid.png"))
        pg.evaluate("()=>window.scrollTo(0, document.body.scrollHeight*0.72)")
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
            scrollW: doc.scrollWidth, clientW: doc.clientWidth,
            broken: [...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.src),
            overflow: over.slice(0, 6),
            cards: document.querySelectorAll('.cpn[data-cat]').length,
            sections: document.querySelectorAll('.cpn-sec').length,
            visibleSections: [...document.querySelectorAll('.cpn-sec')].filter(s => !s.hidden).length,
            tabs: [...document.querySelectorAll('.cpn-tab')].map(t => t.textContent.trim()),
            ld: [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => s.textContent).join('').match(/"@type":"(CollectionPage|ItemList|FAQPage|BreadcrumbList)"/g),
          };
        }""")
        # 탭 필터 동작
        pg.evaluate("()=>window.scrollTo(0, 0)")
        pg.click('button.cpn-tab[data-filter="japan"]')
        pg.wait_for_timeout(300)
        japan = pg.evaluate("""() => ({
          visible: [...document.querySelectorAll('.cpn-sec')].filter(s => !s.hidden).map(s => s.dataset.cat),
          cards: [...document.querySelectorAll('.cpn[data-cat]')].filter(c => c.offsetParent !== null).length,
          onTab: document.querySelector('.cpn-tab.on').dataset.filter,
        })""")
        pg.evaluate("()=>window.scrollTo(0, 0)")
        pg.screenshot(path=str(OUT / f"{tag}_coupons_japan.png"))
        pg.click('button.cpn-tab[data-filter="all"]')
        pg.wait_for_timeout(300)
        allv = pg.evaluate("() => [...document.querySelectorAll('.cpn-sec')].filter(s => !s.hidden).length")
        # 해시 진입
        pg.goto("http://127.0.0.1:8118/about.html", wait_until="load")
        pg.goto("http://127.0.0.1:8118/coupons.html#airport", wait_until="load")
        pg.wait_for_timeout(600)
        hashv = pg.evaluate("() => ({on: document.querySelector('.cpn-tab.on').dataset.filter, vis: [...document.querySelectorAll('.cpn-sec')].filter(s => !s.hidden).map(s => s.dataset.cat)})")
        data.update({"japan": japan, "allVisible": allv, "hashAirport": hashv, "pageerrors": errs})
        report[tag] = data
        ctx.close()
    b.close()
srv.shutdown()
print(json.dumps(report, ensure_ascii=False, indent=1))
