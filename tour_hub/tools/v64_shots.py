#!/usr/bin/env python3
"""v64 렌더 검증 — 신규 가이드 8편 + 연결 허브(오사카·마카오·파리) + /guides/, 1280·390 스크린샷.

    python3 tools/v64_shots.py            # 로컬(deploy_site)
    python3 tools/v64_shots.py --live     # 라이브(https://trippick.pages.dev)

확인: 신규 8편·허브 3곳·/guides/ HTTP 200 · 가로 넘침 0 · 깨진 이미지 0
      · pageerror 0 · 표·FAQ 개수 · 제휴 링크 rel=sponsored · 사이트맵 200(라이브)
"""
from __future__ import annotations

import functools
import http.server
import json
import os
import socketserver
import sys
import threading
from pathlib import Path

# 이 실행 환경의 Chromium은 시스템 라이브러리를 따로 풀어 둔 디렉터리를 필요로 한다.
_LIBS = [p for p in ("/workspace/.tools/chromelibs/root/usr/lib/x86_64-linux-gnu",
                    "/workspace/.tools/sysroot/usr/lib/x86_64-linux-gnu") if Path(p).is_dir()]
if _LIBS:
    _prev = os.environ.get("LD_LIBRARY_PATH")
    os.environ["LD_LIBRARY_PATH"] = ":".join(_LIBS + ([_prev] if _prev else []))

from playwright.sync_api import sync_playwright

LOCAL = "/workspace/trippick_repo/deploy_site"
LIVE = "https://trippick.pages.dev"
OUT = Path("/workspace/trippick_repo/v64_shots")
OUT.mkdir(exist_ok=True)
live = "--live" in sys.argv
prefix = "live_" if live else "v64_"

Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=LOCAL)


class Q(socketserver.TCPServer):
    allow_reuse_address = True


srv = Q(("127.0.0.1", 8144), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = LIVE if live else "http://127.0.0.1:8144"

PAGES = [
    ("esta", "/guides/us-esta-application-guide"),
    ("eta", "/guides/uk-eta-application-guide"),
    ("kix", "/guides/kansai-airport-osaka-kyoto-transfer"),
    ("nyc", "/guides/new-york-4n5d-course-budget"),
    ("nagoya", "/guides/nagoya-3n4d-course-budget"),
    ("restaurant", "/guides/japan-restaurant-reservation-guide"),
    ("macau", "/guides/macau-1n2d-ferry-bus-guide"),
    ("paris", "/guides/paris-metro-navigo-guide"),
    ("hub_osaka", "/osaka"),
    ("hub_macau", "/macau"),
    ("hub_paris", "/paris"),
    ("guides_index", "/guides/"),
]
PAGES = [(n, pa if live else (pa.rstrip("/") + "/index.html" if pa.endswith("/") else pa + ".html")) for n, pa in PAGES]

report: dict = {}
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
    for w, tag in ((1280, "pc"), (390, "mo")):
        ctx = b.new_context(viewport={"width": w, "height": 900 if w > 500 else 844}, device_scale_factor=1)
        for name, path in PAGES:
            pg = ctx.new_page()
            errs: list[str] = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            resp = pg.goto(f"{BASE}{path}", wait_until="load", timeout=90000)
            pg.wait_for_timeout(800)
            info = pg.evaluate(
                """() => ({
                    status: document.readyState,
                    scrollW: document.documentElement.scrollWidth,
                    clientW: document.documentElement.clientWidth,
                    broken: [...document.images].filter(i => i.complete && i.naturalWidth === 0).length,
                    imgs: document.images.length,
                    tables: document.querySelectorAll('table').length,
                    faq: document.querySelectorAll('details.fq').length,
                    sponsored: document.querySelectorAll('a[rel*="sponsored"]').length,
                    h1: (document.querySelector('h1')||{}).innerText || ''
                })"""
            )
            shot = OUT / f"{prefix}{tag}_{name}.png"
            pg.screenshot(path=str(shot), full_page=(tag == "mo" and name in ("esta", "nyc")))
            report[f"{tag}_{name}"] = {
                "url": path,
                "http": resp.status if resp else None,
                "overflow": info["scrollW"] - info["clientW"],
                "broken": info["broken"],
                "imgs": info["imgs"],
                "tables": info["tables"],
                "faq": info["faq"],
                "sponsored": info["sponsored"],
                "pageerrors": errs,
                "shot": str(shot),
            }
            pg.close()
        ctx.close()

    if live:
        ctx = b.new_context(viewport={"width": 1280, "height": 800})
        pg = ctx.new_page()
        for sm in ("/sitemap.xml", "/sitemap-index.xml", "/sitemap-core.xml",
                   "/sitemap-hubs.xml", "/sitemap-guides.xml", "/robots.txt"):
            r = pg.goto(f"{LIVE}{sm}", wait_until="load", timeout=60000)
            report[f"sitemap{sm}"] = {"http": r.status if r else None,
                                      "ct": r.headers.get("content-type") if r else None}
        ctx.close()
    b.close()

print(json.dumps(report, ensure_ascii=False, indent=1))
(OUT / f"{prefix}report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

bad = []
for k, v in report.items():
    if "http" in v and v.get("http") not in (200,):
        bad.append(f"{k} http {v.get('http')}")
    if v.get("overflow", 0) > 0:
        bad.append(f"{k} 가로 넘침 {v['overflow']}px")
    if v.get("broken", 0) > 0:
        bad.append(f"{k} 깨진 이미지 {v['broken']}")
    if v.get("pageerrors"):
        bad.append(f"{k} pageerror {v['pageerrors']}")
print()
print("실패 없음" if not bad else "실패:\n  - " + "\n  - ".join(bad))
sys.exit(1 if bad else 0)
