#!/usr/bin/env python3
"""v45 라이브 화면 캡처 — 1280·390px. (로컬에서만 쓰는 임시 스크립트)"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "https://trippick.pages.dev"
OUT = Path(__file__).parent
JOBS = [
    # (파일명, 경로, 뷰포트, 스크롤 대상 셀렉터, 설명)
    ("tokyo_1280_tools.png", "/tokyo", (1280, 900), ".hub-tools", "도쿄 허브 도구 4개"),
    ("tokyo_1280_pass.png", "/tokyo", (1280, 900), ".hub-tools", "도쿄 허브 도구 4개(패스 1개 더)"),
    ("exchange_1280_preset.png", "/exchange?cur=JPY&city=tokyo", (1280, 900), ".fx-card", "환율 프리셋"),
    ("passes_1280_taipei.png", "/passes?city=taipei", (1280, 900), ".pk-card", "패스 프리셋"),
    ("danang_guide_1280.png", "/guides/danang-hoian-3n5d", (1280, 900), ".pg-hero", "다낭 가이드 상단"),
    ("danang_guide_1280_body.png", "/guides/danang-hoian-3n5d", (1280, 900), "#money", "다낭 가이드 예산표"),
    ("taipei_guide_1280.png", "/guides/taipei-3n4d-course-budget", (1280, 900), ".pg-hero", "타이베이 가이드 상단"),
    ("currency_guide_1280.png", "/guides/currency-payment-fees", (1280, 900), "#cash", "환전 수수료표"),
    ("danang_guide_390.png", "/guides/danang-hoian-3n5d", (390, 844), ".pg-hero", "다낭 가이드 모바일"),
    ("tools_390.png", "/tokyo", (390, 844), ".hub-tools", "도쿄 허브 도구 모바일"),
    ("sos_390_print.png", "/sos?country=JP", (390, 844), ".sos-save", "SOS 프리셋+인쇄"),
]

report = []
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/workspace/.tools/cft/chrome-linux64/chrome', args=['--no-sandbox','--disable-dev-shm-usage'])
    for name, path, vp, sel, desc in JOBS:
        ctx = browser.new_context(viewport={"width": vp[0], "height": vp[1]}, device_scale_factor=1,
                                  locale="ko-KR")
        page = ctx.new_page()
        errors, console = [], []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: console.append(m.text) if m.type == "error" else None)
        page.goto(BASE + path, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(900)
        try:
            page.eval_on_selector(sel, "el => el.scrollIntoView({block:'start'})")
        except Exception:
            pass
        page.wait_for_timeout(500)
        page.screenshot(path=str(OUT / name), full_page=False)
        over = page.evaluate("() => ({sw: document.documentElement.scrollWidth, iw: innerWidth, "
                             "ob: document.body.scrollWidth})")
        sel_state = page.evaluate("""() => {
            const t = document.querySelector('.sos-tab[aria-selected="true"]');
            const cur = document.getElementById('fxCur');
            const tab = document.querySelector('.pk-tab.on');
            const preset = document.getElementById('fxPreset');
            return {
              sosTab: t ? t.textContent.trim() : null,
              fxCur: cur ? cur.value : null,
              fxPreset: preset && !preset.hidden ? preset.textContent.trim().slice(0,90) : null,
              passTab: tab ? tab.textContent.trim() : null,
              print: !!document.getElementById('sosPrint'),
              gtools: document.querySelectorAll('.gtools a').length
            };
        }""")
        report.append({"shot": name, "url": path, "desc": desc, "vp": vp, "overflow": over,
                       "state": sel_state, "pageerrors": errors, "console": console[:3]})
        ctx.close()
    browser.close()

(OUT / "capture_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
for r in report:
    print(r["shot"], r["vp"], "overflow:", r["overflow"], "state:", r["state"],
          "err:", r["pageerrors"], r["console"])
