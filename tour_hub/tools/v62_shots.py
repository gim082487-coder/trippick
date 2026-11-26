#!/usr/bin/env python3
"""v62 렌더 검증 — 홈 다듬기(코스 칩·패널 히어로·외부 CSS) 1280·390 스크린샷.

    python3 tools/v62_shots.py            # 로컬(deploy_site)
    python3 tools/v62_shots.py --live     # 라이브(https://trippick.pages.dev)

확인: 가로 넘침 0 · 깨진 이미지 0 · pageerror 0 · 콘솔 오류 0
      · site.css?v=62 외부 CSS 로딩(body 배경·Pretendard 적용)
      · 코스 칩 21개(모바일만 보임) · 칩 클릭 → 패널 전환 · aria-current 1개
      · 패널 히어로 높이(데스크톱 280 / 모바일 132 이상, 1000px 이미지 원복 금지)
      · /stays · /passes · /coupons · /osaka 렌더
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
OUT = Path("/workspace/trippick_repo/v62_shots")
OUT.mkdir(exist_ok=True)
live = "--live" in sys.argv
prefix = "live_" if live else "v62_"

Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=LOCAL)


class Q(socketserver.TCPServer):
    allow_reuse_address = True


srv = Q(("127.0.0.1", 8141), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = LIVE if live else "http://127.0.0.1:8141"

SAMPLE = ["sydney", "bangkok", "phu_quoc"]
PAGES = [("stays", "/stays"), ("passes", "/passes"), ("coupons", "/coupons"), ("hub_osaka", "/osaka")]
PAGES = [(n, pa if live else pa + ".html") for n, pa in PAGES]

report: dict = {}
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
    for w, tag in ((1280, "pc"), (390, "mo")):
        ctx = b.new_context(viewport={"width": w, "height": 900 if w > 500 else 844}, device_scale_factor=1)
        pg = ctx.new_page()
        errs: list[str] = []
        cons: list[str] = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: cons.append(m.text) if m.type == "error" else None)
        pg.goto(f"{BASE}/index.html", wait_until="load", timeout=60000)
        pg.wait_for_timeout(1500)

        data = pg.evaluate("""() => {
          const doc = document.documentElement;
          const over = [];
          document.querySelectorAll('body *').forEach(el => {
            const r = el.getBoundingClientRect();
            if (r.width > 0 && r.right > doc.clientWidth + 2 &&
                getComputedStyle(el).overflowX !== 'auto' &&
                !el.closest('.tb-scroll') && !el.closest('.toc-scroll') && !el.closest('.picker'))
              over.push((el.className || el.tagName) + ':' + Math.round(r.right - doc.clientWidth));
          });
          const chips = [...document.querySelectorAll('.pick-idx .pidx')];
          const hero = document.querySelector('.panel.active .panel-hero');
          return {
            title: document.title,
            css: [...document.querySelectorAll('link[rel=stylesheet]')].map(l => l.getAttribute('href')),
            bodyBg: getComputedStyle(document.body).backgroundColor,
            font: getComputedStyle(document.body).fontFamily.slice(0, 24),
            picks: document.querySelectorAll('.pick').length,
            panels: document.querySelectorAll('.panel').length,
            active: document.querySelectorAll('.panel.active').length,
            chips: chips.length,
            chipsShown: chips.filter(c => c.getBoundingClientRect().width > 0).length,
            chipCurrent: chips.filter(c => c.getAttribute('aria-current') === 'true').length,
            heroH: hero ? Math.round(hero.getBoundingClientRect().height) : 0,
            inlineStyles: (document.documentElement.innerHTML.match(/<style/g) || []).length,
            htmlKB: Math.round(document.documentElement.outerHTML.length / 1024),
            scrollW: doc.scrollWidth, clientW: doc.clientWidth,
            broken: [...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.src),
            overflow: over.slice(0, 8),
          };
        }""")
        pg.evaluate("()=>{document.documentElement.style.scrollBehavior='auto';document.body.style.scrollBehavior='auto';}")

        def go(sel, off=72):
            for _ in range(3):
                pg.evaluate("([s,o])=>{const el=document.querySelector(s);if(el)window.scrollTo({top: el.getBoundingClientRect().top+window.scrollY-o, behavior:'instant'});}", [sel, off])
                pg.wait_for_timeout(260)
            pg.wait_for_timeout(300)
        go('#courses')
        pg.screenshot(path=str(OUT / f"{prefix}{tag}_courses.png"))

        # 칩(모바일)·카드(데스크톱)로 코스 전환 표본 확인
        switched = []
        for cid in SAMPLE:
            if data["chipsShown"]:
                pg.evaluate("(id)=>{const c=document.querySelector('.pick-idx .pidx[data-course=\"'+id+'\"]');c&&c.click();}", cid)
            else:
                pg.locator(f"#cpick-{cid}").click()
            pg.wait_for_timeout(400)
            on = pg.evaluate("(id)=>document.querySelector('#course-'+id)?.classList.contains('active')", cid)
            cur = pg.evaluate("(id)=>document.querySelector('.pick-idx .pidx[data-course=\"'+id+'\"]')?.getAttribute('aria-current')", cid)
            go('#course-' + cid, 70)
            pg.screenshot(path=str(OUT / f"{prefix}{tag}_course_{cid}.png"))
            switched.append([cid, bool(on), cur])
        data["switch"] = switched
        data["pageerror"] = errs[:5]
        data["console"] = cons[:5]
        report[tag] = data
        print(f"{tag:2} CSS {data['css']} · 카드 {data['picks']}·패널 {data['panels']}(활성 {data['active']}) · "
              f"칩 {data['chips']}(표시 {data['chipsShown']}, 현재 {data['chipCurrent']}) · 히어로 {data['heroH']}px · "
              f"넘침 {len(data['overflow'])} · 깨진 이미지 {len(data['broken'])} · pageerror {len(errs)} · 전환 {switched}")
        pg.close()
        ctx.close()

    # 다른 페이지 렌더 확인(모바일 390 기준)
    ctx = b.new_context(viewport={"width": 390, "height": 844})
    pg = ctx.new_page()
    for name, path in PAGES:
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        r = pg.goto(f"{BASE}{path}", wait_until="load", timeout=60000)
        pg.wait_for_timeout(900)
        info = pg.evaluate("""() => {
          const doc = document.documentElement;
          return {status: 200, css: [...document.querySelectorAll('link[rel=stylesheet]')].map(l=>l.getAttribute('href')),
                  scrollW: doc.scrollWidth, clientW: doc.clientWidth,
                  broken: [...document.images].filter(i => i.complete && i.naturalWidth === 0).length,
                  h1: (document.querySelector('h1')||{}).textContent?.trim().slice(0, 40) || ''};
        }""")
        info["http"] = r.status if r else None
        info["pageerror"] = errs[:3]
        pg.screenshot(path=str(OUT / f"{prefix}mo_{name}.png"))
        report[f"mo_{name}"] = info
        print(f"  {path:10} HTTP {info['http']} · h1 {info['h1'][:24]} · 넘침 {info['scrollW'] - info['clientW']} · 깨진 이미지 {info['broken']}")
    ctx.close()
    b.close()

srv.shutdown()
(OUT / f"{prefix}report_v62.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
bad = [k for k, v in report.items()
       if isinstance(v, dict) and (
           v.get("scrollW", 0) > v.get("clientW", 0) + 2
           or v.get("broken") or v.get("pageerror") or v.get("console")
           or (v.get("picks") is not None and (v["picks"] != 21 or v["panels"] != 21 or v["active"] != 1))
           or (v.get("chips") is not None and (v["chips"] != 21 or v["chipCurrent"] != 1))
           or (v.get("heroH") is not None and v["heroH"] > 420)
           or (v.get("chipsShown") is not None and (v["chipsShown"] > 0) != (v["clientW"] < 500))
           or any((not on) or (cur != "true") for _, on, cur in v.get("switch", []))
           or (v.get("picks") is not None and not any("site.css" in (c or "") for c in v.get("css", []))))
       ]
print("이상:", bad if bad else "없음", "→", OUT)
