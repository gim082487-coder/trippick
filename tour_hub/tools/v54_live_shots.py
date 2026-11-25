#!/usr/bin/env python3
"""v54 라이브 렌더 검증 — 신규 3편 + 도쿄 허브 1280·390 스크린샷, 넘침·깨진 이미지·pageerror."""
from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

SITE = "https://trippick.pages.dev"
OUT = Path("/workspace/trippick_repo/v54_shots")
OUT.mkdir(exist_ok=True)
PAGES = [
    ("/guides/japan-mounjaro-injection-guide", "live_mounjaro"),
    ("/guides/guam-4n5d-course", "live_guam"),
    ("/guides/hawaii-oahu-5n7d-course", "live_hawaii"),
    ("/tokyo", "live_tokyo"),
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
            pg.goto(SITE + path, wait_until="load", timeout=60000)
            pg.wait_for_timeout(1200)
            pg.screenshot(path=str(OUT / f"{tag}_{name}_top.png"))
            pg.evaluate("()=>window.scrollTo(0, document.body.scrollHeight*0.45)")
            pg.wait_for_timeout(600)
            pg.screenshot(path=str(OUT / f"{tag}_{name}_mid.png"))
            data = pg.evaluate("""() => {
              const d = document.documentElement;
              return {
                scrollW: d.scrollWidth, clientW: d.clientWidth,
                broken: [...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.src).slice(0,5),
                faq: document.querySelectorAll('details.fq').length,
                tb: document.querySelectorAll('.tb').length,
                title: document.title,
              };
            }""")
            data["pageerror"] = errs
            report[f"{tag}_{name}"] = data
            print(f"{tag} {path}: {data['scrollW']}/{data['clientW']} · 깨진 {len(data['broken'])} · "
                  f"pageerror {len(errs)} · FAQ {data['faq']} · 표 {data['tb']}")
        ctx.close()
    b.close()

(OUT / "live_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
bad = [k for k, v in report.items() if v["scrollW"] > v["clientW"] + 2 or v["broken"] or v["pageerror"]]
print("이상:", bad if bad else "없음")
