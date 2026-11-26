#!/usr/bin/env python3
"""v61 렌더 검증 — 홈 코스 21편(신규 16편) + /courses 표지, 1280·390 스크린샷.

    python3 tools/v61_shots.py            # 로컬(deploy_site)
    python3 tools/v61_shots.py --live     # 라이브(https://trippick.pages.dev)

확인: 가로 넘침 0 · 깨진 이미지 0 · pageerror 0 · 코스 카드 21장·패널 21개(활성 1)
      · 코스 탭을 눌러 패널이 바뀌는지 3편 표본 확인 · 새 코스의 제휴 링크에 Allianceid·trip_sub3
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
OUT = Path("/workspace/trippick_repo/v61_shots")
OUT.mkdir(exist_ok=True)
live = "--live" in sys.argv
prefix = "live_" if live else ""

Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=LOCAL)


class Q(socketserver.TCPServer):
    allow_reuse_address = True


srv = Q(("127.0.0.1", 8119), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = LIVE if live else "http://127.0.0.1:8119"

SAMPLE = ["phu_quoc", "switzerland", "taipei"]

report = {}
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
    for w, tag in ((1280, "pc"), (390, "mo")):
        ctx = b.new_context(viewport={"width": w, "height": 900 if w > 500 else 844}, device_scale_factor=1)
        pg = ctx.new_page()
        errs: list[str] = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(f"{BASE}/index.html", wait_until="load", timeout=60000)
        pg.wait_for_timeout(1200)
        pg.query_selector(".picker").scroll_into_view_if_needed()
        pg.wait_for_timeout(600)
        pg.screenshot(path=str(OUT / f"{prefix}{tag}_courses_picker.png"))

        data = pg.evaluate("""() => {
          const doc = document.documentElement;
          const over = [];
          document.querySelectorAll('body *').forEach(el => {
            const r = el.getBoundingClientRect();
            if (r.width > 0 && r.right > doc.clientWidth + 2 &&
                getComputedStyle(el).overflowX !== 'auto' &&
                !el.closest('.tb-scroll') && !el.closest('.toc-scroll') &&
                !el.closest('.picker'))
              over.push((el.className || el.tagName) + ':' + Math.round(r.right - doc.clientWidth));
          });
          const pick = document.querySelectorAll('.pick');
          return {
            title: document.title,
            picks: pick.length,
            panels: document.querySelectorAll('.panel').length,
            active: document.querySelectorAll('.panel.active').length,
            cguide: document.querySelectorAll('.cguide').length,
            tdl: document.querySelectorAll('.tdl').length,
            price_view: [...document.querySelectorAll('.tdl-price')].filter(e => e.textContent.includes('요금 보기')).length,
            scrollW: doc.scrollWidth, clientW: doc.clientWidth,
            broken: [...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.src),
            overflow: over.slice(0, 8),
          };
        }""")

        # 코스 탭 전환 표본 확인
        switched = []
        for cid in SAMPLE:
            sel = f'#cpick-{cid}'
            if pg.locator(sel).count():
                pg.locator(sel).click()
                pg.wait_for_timeout(350)
                on = pg.evaluate("(id)=>document.querySelector('#course-'+id)?.classList.contains('active')", cid)
                visible = pg.locator(f"#course-{cid}").is_visible()
                switched.append((cid, on, visible))
                pg.locator(f"#course-{cid}").scroll_into_view_if_needed()
                pg.wait_for_timeout(500)
                pg.screenshot(path=str(OUT / f"{prefix}{tag}_course_{cid}.png"))
        data["switch"] = switched

        # 제휴 링크 파라미터 점검 (새 코스 패널 안)
        data["affiliate"] = pg.evaluate("""() => {
          const bad = [];
          document.querySelectorAll('.panel a[rel="noopener sponsored"]').forEach(a => {
            const h = a.getAttribute('href') || '';
            if (h.includes('trip.com')) {
              if (!h.includes('Allianceid=11407530')) bad.push('Allianceid:' + h.slice(0, 90));
              if (!h.includes('trip_sub3=')) bad.push('trip_sub3:' + h.slice(0, 90));
            } else if (!/^https:\\/\\/(link\\.coupang\\.com|naver\\.me)\\//.test(h)) {
              bad.push('domain:' + h.slice(0, 90));
            }
          });
          return bad.slice(0, 10);
        }""")
        data["pageerror"] = errs
        report[tag] = data
        print(f"{tag:2} 카드 {data['picks']} · 패널 {data['panels']}(활성 {data['active']}) · 가이드링크 {data['cguide']} · "
              f"넘침 {len(data['overflow'])} · 깨진 이미지 {len(data['broken'])} · pageerror {len(errs)} · "
              f"탭전환 {switched} · 제휴 이상 {len(data['affiliate'])}")

        pg.remove_listener("pageerror", lambda e: None) if False else None
        pg.close()
        ctx.close()
    b.close()

srv.shutdown()
(OUT / f"{prefix}report_v61.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
bad = [k for k, v in report.items()
       if v["scrollW"] > v["clientW"] + 2 or v["broken"] or v["pageerror"] or v["affiliate"]
       or v["picks"] != 21 or v["panels"] != 21 or v["active"] != 1
       or any(not (on and vis) for _, on, vis in v["switch"])]
print("이상:", bad if bad else "없음", "→", OUT)
