#!/usr/bin/env python3
"""v54 렌더 검증 — 신규 3편 1280·390 스크린샷, 가로 넘침·깨진 이미지·pageerror 0 확인."""
from __future__ import annotations

import functools
import http.server
import json
import socketserver
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = "/workspace/trippick_repo/deploy_site"
OUT = Path("/workspace/trippick_repo/v54_shots")
OUT.mkdir(exist_ok=True)
Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)


class Q(socketserver.TCPServer):
    allow_reuse_address = True


srv = Q(("127.0.0.1", 8104), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

GUIDES = ["japan-mounjaro-injection-guide", "guam-4n5d-course", "hawaii-oahu-5n7d-course"]
report = {}

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/workspace/.tools/cft/chrome-linux64/chrome",
                          args=["--no-sandbox", "--disable-dev-shm-usage"])
    for w, tag in ((1280, "pc"), (390, "mo")):
        ctx = b.new_context(viewport={"width": w, "height": 900 if w > 500 else 844}, device_scale_factor=1)
        pg = ctx.new_page()
        for slug in GUIDES:
            errs: list[str] = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(f"http://127.0.0.1:8104/guides/{slug}.html", wait_until="load")
            pg.wait_for_timeout(700)
            pg.screenshot(path=str(OUT / f"{tag}_{slug}_top.png"))
            pg.evaluate("()=>window.scrollTo(0, document.body.scrollHeight*0.38)")
            pg.wait_for_timeout(400)
            pg.screenshot(path=str(OUT / f"{tag}_{slug}_mid.png"))
            pg.evaluate("()=>window.scrollTo(0, document.body.scrollHeight*0.78)")
            pg.wait_for_timeout(400)
            pg.screenshot(path=str(OUT / f"{tag}_{slug}_low.png"))
            data = pg.evaluate("""() => {
              const doc = document.documentElement;
              const over = [];
              document.querySelectorAll('body *').forEach(el => {
                const r = el.getBoundingClientRect();
                if (r.width > 0 && r.right > doc.clientWidth + 2 &&
                    getComputedStyle(el).overflowX !== 'auto' &&
                    !el.closest('.tb-scroll') && !el.closest('.toc-scroll'))
                  over.push((el.className || el.tagName) + ':' + Math.round(r.right - doc.clientWidth));
              });
              return {
                scrollW: doc.scrollWidth, clientW: doc.clientWidth,
                broken: [...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.src),
                h2: document.querySelectorAll('.doc h2').length,
                tb: document.querySelectorAll('.doc .tb').length,
                faq: document.querySelectorAll('.doc details.fq').length,
                gact: document.querySelectorAll('.gact').length,
                overflow: over.slice(0, 8),
              };
            }""")
            data["pageerror"] = errs
            report[f"{tag}_{slug}"] = data
            print(f"{tag} {slug}: scrollW {data['scrollW']}/{data['clientW']} · 넘침 {len(data['overflow'])} · "
                  f"깨진 이미지 {len(data['broken'])} · pageerror {len(errs)} · h2 {data['h2']} · 표 {data['tb']} · FAQ {data['faq']}")
        # 허브·가이드 목록
        for path, name in (("tokyo.html", "tokyo"), ("guides/index.html", "guides_index")):
            pg.goto(f"http://127.0.0.1:8104/{path}", wait_until="load")
            pg.wait_for_timeout(700)
            pg.screenshot(path=str(OUT / f"{tag}_{name}.png"))
        ctx.close()
    b.close()

srv.shutdown()
(OUT / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
bad = [k for k, v in report.items() if v["scrollW"] > v["clientW"] + 2 or v["broken"] or v["pageerror"]]
print("이상:", bad if bad else "없음", "→", OUT)
