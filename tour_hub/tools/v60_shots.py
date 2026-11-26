#!/usr/bin/env python3
"""v60 렌더 검증 — 신규 가이드 10편 1280·390 스크린샷, 가로 넘침·깨진 이미지·pageerror 0 확인.

    python3 tools/v60_shots.py            # 로컬(deploy_site)
    python3 tools/v60_shots.py --live     # 라이브(https://trippick.pages.dev)
"""
from __future__ import annotations

import functools
import http.server
import json
import socketserver
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

LOCAL = "/workspace/trippick_repo/deploy_site"
LIVE = "https://trippick.pages.dev"
OUT = Path("/workspace/trippick_repo/v60_shots")
OUT.mkdir(exist_ok=True)
live = "--live" in sys.argv
prefix = "live_" if live else ""

Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=LOCAL)


class Q(socketserver.TCPServer):
    allow_reuse_address = True


srv = Q(("127.0.0.1", 8118), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = LIVE if live else "http://127.0.0.1:8118"

PAGES = [
    ("guides/beppu-onsen-1n2d-course.html", "beppu"),
    ("guides/kaohsiung-tainan-3n4d-course.html", "kaohsiung"),
    ("guides/kota-kinabalu-3n4d-course.html", "kota"),
    ("guides/bohol-3n4d-course.html", "bohol"),
    ("guides/beijing-3n4d-course.html", "beijing"),
    ("guides/qingdao-2n3d-course.html", "qingdao"),
    ("guides/sydney-4n5d-course.html", "sydney"),
    ("guides/switzerland-jungfrau-zermatt-pass.html", "swiss"),
    ("guides/eastern-europe-prague-vienna-budapest.html", "europe"),
    ("guides/japan-shinkansen-jr-pass-guide.html", "jrpass"),
]
EXTRA = [("guides/index.html", "guides"), ("index.html", "home")]

report = {}
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
    for w, tag in ((1280, "pc"), (390, "mo")):
        ctx = b.new_context(viewport={"width": w, "height": 900 if w > 500 else 844}, device_scale_factor=1)
        pg = ctx.new_page()
        for path, name in PAGES:
            errs: list[str] = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(f"{BASE}/{path}", wait_until="load", timeout=60000)
            pg.wait_for_timeout(900)
            pg.screenshot(path=str(OUT / f"{prefix}{tag}_{name}_top.png"))
            pg.evaluate("()=>window.scrollTo(0, document.body.scrollHeight*0.4)")
            pg.wait_for_timeout(400)
            pg.screenshot(path=str(OUT / f"{prefix}{tag}_{name}_mid.png"))
            pg.evaluate("()=>window.scrollTo(0, document.body.scrollHeight*0.85)")
            pg.wait_for_timeout(400)
            pg.screenshot(path=str(OUT / f"{prefix}{tag}_{name}_low.png"))
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
                title: document.title,
                h1: (document.querySelector('h1')||{}).innerText || '',
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
            report[f"{tag}_{name}"] = data
            print(f"{tag:2} {name:10} {data['scrollW']}/{data['clientW']} · 넘침 {len(data['overflow'])} · "
                  f"깨진 이미지 {len(data['broken'])} · pageerror {len(errs)} · h2 {data['h2']} · 표 {data['tb']} · "
                  f"FAQ {data['faq']}")
            pg.remove_listener("pageerror", lambda e: None) if False else None
        for path, name in EXTRA:
            pg.goto(f"{BASE}/{path}", wait_until="load", timeout=60000)
            pg.wait_for_timeout(900)
            pg.screenshot(path=str(OUT / f"{prefix}{tag}_{name}.png"))
        ctx.close()
    b.close()

srv.shutdown()
(OUT / f"{prefix}report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
bad = [k for k, v in report.items() if v["scrollW"] > v["clientW"] + 2 or v["broken"] or v["pageerror"]]
print("이상:", bad if bad else "없음", "→", OUT)
