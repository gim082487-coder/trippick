#!/usr/bin/env python3
"""v55 라이브 검증 — 신규 도시 허브 9개 + 수정 가이드 1편을 1280·390 에서 렌더.

넘침·깨진 이미지·pageerror·FAQ 섹션을 기록하고 스크린샷을 남긴다.

    python3 tools/v55_live_shots.py
"""
from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

SITE = "https://trippick.pages.dev"
OUT = Path("/workspace/trippick_repo/v55_shots")
OUT.mkdir(exist_ok=True)
PAGES = [
    ("/guam", "guam"),
    ("/saipan", "saipan"),
    ("/singapore", "singapore"),
    ("/hongkong", "hongkong"),
    ("/macau", "macau"),
    ("/paris", "paris"),
    ("/london", "london"),
    ("/rome", "rome"),
    ("/barcelona", "barcelona"),
    ("/", "home"),
    ("/cities/", "cities"),
    ("/guides/bangkok-pattaya-3n5d-course-budget", "bangkok_guide"),
]
report = {}

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/workspace/.tools/cft/chrome-linux64/chrome",
                          args=["--no-sandbox", "--disable-dev-shm-usage"])
    for w, tag in ((1280, "pc"), (390, "mo")):
        ctx = b.new_context(viewport={"width": w, "height": 900 if w > 500 else 844})
        pg = ctx.new_page()
        for path, name in PAGES:
            errs: list[str] = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            resp = pg.goto(SITE + path, wait_until="load", timeout=60000)
            pg.wait_for_timeout(1000)
            pg.screenshot(path=str(OUT / f"{tag}_{name}_top.png"))
            pg.evaluate("() => window.scrollTo(0, document.body.scrollHeight*0.42)")
            pg.wait_for_timeout(400)
            pg.screenshot(path=str(OUT / f"{tag}_{name}_mid.png"))
            data = pg.evaluate("""() => {
              const d = document.documentElement;
              return {
                scrollW: d.scrollWidth, clientW: d.clientWidth,
                broken: [...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.src).slice(0,5),
                faq: document.querySelectorAll('details.fq').length,
                tips: document.querySelectorAll('.hub-tip').length,
                tipsOverflow: [...document.querySelectorAll('.hub-tip')].filter(e => e.scrollWidth > e.clientWidth + 2).length,
                title: document.title,
                h1: (document.querySelector('h1') || {}).textContent || '',
              };
            }""")
            data["status"] = resp.status if resp else None
            data["pageerror"] = errs
            report[f"{tag}_{name}"] = data
            print(f"{tag} {path}: {data['status']} · 넘침 {data['scrollW']}/{data['clientW']} · "
                  f"깨진 {len(data['broken'])} · err {len(errs)} · FAQ {data['faq']} · 정보카드 {data['tips']}")
        ctx.close()
    b.close()

(OUT / "live_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
bad = [k for k, v in report.items()
       if v["status"] != 200 or v["scrollW"] > v["clientW"] + 2 or v["broken"] or v["pageerror"]]
print("이상:", bad if bad else "없음")
