#!/usr/bin/env python3
"""v34 로컬 검증 — 홈/캘린더/체크리스트/패스/환율/숙소 페이지를 1280·390px 로 열어
   묶음 CTA·유럽 링크·클릭 추적(tp_clicks_v1)·가로 넘침·콘솔 에러를 확인한다.

   LD_LIBRARY_PATH=/workspace/.tools/sysroot/usr/lib/x86_64-linux-gnu python3 tools/verify_v34.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT.parent / "deploy_site"
SHOTS = Path("/workspace/v34_shots")
SHOTS.mkdir(exist_ok=True)
FAIL = []


def check(cond, msg):
    print(("  ✓ " if cond else "  ✗ ") + msg)
    if not cond:
        FAIL.append(msg)


def open_page(ctx, name, width):
    page = ctx.new_page()
    errors = []
    # file:// 로 열면 사이트 루트 절대경로(/images/...) 리소스만 실패한다(라이브에서는 200). 그건 제외한다.
    page.on("console", lambda m: errors.append(m.text) if (m.type == "error" and "Failed to load resource" not in m.text) else None)
    page.on("pageerror", lambda e: errors.append("PAGEERROR " + str(e)))
    page.on("requestfailed", lambda r: errors.append("REQFAIL " + r.url[-70:]) if not r.url.startswith("file:///") else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto((SITE / name).as_uri(), wait_until="load")
    page.wait_for_timeout(400)
    return page, errors


def no_overflow(page):
    return page.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth + 1")


def run(width):
    print(f"\n=== {width}px ===")
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": width, "height": 900 if width > 500 else 780},
                            locale="ko-KR", device_scale_factor=2 if width < 500 else 1)
        # ---- 홈 예산 계산기
        page, errs = open_page(ctx, "index.html", width)
        page.wait_for_selector("#plBody .plan", timeout=8000)
        page.wait_for_timeout(300)
        info = page.evaluate("""() => {
            const h = document.getElementById('plBundle');
            return {hidden: h.hidden, cards: h.querySelectorAll('.tp-b-card').length,
                    head: (h.querySelector('.tp-b-head b')||{}).textContent||'',
                    hrefs: [...h.querySelectorAll('.tp-b-card')].map(a=>a.getAttribute('href'))};
        }""")
        check(not info["hidden"] and info["cards"] >= 3, f"홈 #planner 묶음 CTA {info['cards']}개 · {info['head']}")
        check(all(h.startswith(("https://kr.trip.com", "https://link.coupang.com", "https://naver.me", "/stays")) for h in info["hrefs"]),
              "홈 묶음 링크가 모두 검증된 제휴/내부 링크")
        check(no_overflow(page), "홈 가로 넘침 없음")
        check(not errs, f"홈 콘솔 에러 {len(errs)}건 " + (errs[0][:120] if errs else ""))
        page.evaluate("() => document.getElementById('planner').scrollIntoView()")
        page.screenshot(path=str(SHOTS / f"home-planner-{width}.png"), clip=None)
        # 유럽 지역으로 바꿔도 다시 그려지는지
        page.click('.pc-chip[data-region="west"]')
        page.wait_for_timeout(300)
        west = page.evaluate("""() => {
            const h = document.getElementById('plBundle');
            return {cards:[...h.querySelectorAll('.tp-b-card b')].map(b=>b.textContent), hidden:h.hidden};
        }""")
        check(not west["hidden"], f"유럽·미주 선택 시 묶음 CTA 유지 · 예: {west['cards'][:2]}")
        page.close()

        # ---- /calendar 파리·런던
        page, errs = open_page(ctx, "calendar.html", width)
        page.click('[data-city-btn="paris"]')
        page.wait_for_timeout(400)
        cal = page.evaluate("""() => ({
            links:[...document.querySelectorAll('#scLinks .sc-link')].map(a=>({k:a.querySelector('.sc-link-k').textContent, h:a.getAttribute('href')})),
            noLink: !document.getElementById('scNoLink').hidden
        })""")
        kinds = [l["k"] for l in cal["links"]]
        for k in ("항공권", "숙소", "입장권·투어", "공항픽업", "찐숙소"):
            check(k in kinds, f"/calendar 파리 '{k}' 버튼 활성 ({len(cal['links'])}개 링크)")
        check(not cal["noLink"], "/calendar 파리 '제휴 링크 없음' 안내 사라짐")
        page.click('[data-city-btn="london"]')
        page.wait_for_timeout(300)
        lon = page.evaluate("() => [...document.querySelectorAll('#scLinks .sc-link-k')].map(e=>e.textContent)")
        check(all(k in lon for k in ("항공권", "숙소", "입장권·투어", "공항픽업")), f"/calendar 런던 버튼 {len(lon)}개")
        check(no_overflow(page), "/calendar 가로 넘침 없음")
        check(not errs, f"/calendar 콘솔 에러 {len(errs)}건")
        page.screenshot(path=str(SHOTS / f"calendar-paris-{width}.png"), full_page=False)
        page.close()

        # ---- /checklist
        page, errs = open_page(ctx, "checklist.html", width)
        page.wait_for_selector('[data-tp-bundle="checklist"] .tp-b-card', timeout=8000)
        cl = page.evaluate("""() => {
            const h = document.querySelector('[data-tp-bundle="checklist"]');
            return {chips:h.querySelectorAll('.tp-b-chip').length, cards:h.querySelectorAll('.tp-b-card').length,
                    head:(h.querySelector('.tp-b-head b')||{}).textContent||''};
        }""")
        check(cl["cards"] >= 3, f"/checklist 묶음 카드 {cl['cards']}개 · 칩 {cl['chips']}개 · {cl['head']}")
        page.click('.tp-b-chip[data-tp-chip="paris"]')
        page.wait_for_timeout(300)
        clp = page.evaluate("""() => {
            const h = document.querySelector('[data-tp-bundle="checklist"]');
            return {head:(h.querySelector('.tp-b-head b')||{}).textContent||'',
                    hrefs:[...h.querySelectorAll('.tp-b-card')].map(a=>a.getAttribute('href'))};
        }""")
        check("파리" in clp["head"], f"/checklist 칩 전환 → {clp['head']}")
        check(any("kr.trip.com" in h for h in clp["hrefs"]), "/checklist 파리 카드에 트립닷컴 링크")
        check(no_overflow(page), "/checklist 가로 넘침 없음")
        check(not errs, f"/checklist 콘솔 에러 {len(errs)}건")
        page.evaluate("() => document.querySelector('[data-tp-bundle=\"checklist\"]').scrollIntoView({block:'center'})")
        page.screenshot(path=str(SHOTS / f"checklist-bundle-{width}.png"))
        page.close()

        # ---- /passes
        page, errs = open_page(ctx, "passes.html", width)
        page.wait_for_timeout(500)
        ps = page.evaluate("""() => [...document.querySelectorAll('[data-tp-bundle="kit"]')].map(h=>({
            city:h.getAttribute('data-tp-city'), hidden:h.hidden, cards:h.querySelectorAll('.tp-b-card').length}))""")
        check(all((not h["hidden"]) and h["cards"] >= 2 for h in ps), f"/passes 도시별 묶음 {len(ps)}개 · " + ", ".join(f"{h['city']}:{h['cards']}" for h in ps))
        check(no_overflow(page), "/passes 가로 넘침 없음")
        check(not errs, f"/passes 콘솔 에러 {len(errs)}건")
        page.evaluate("() => document.querySelector('[data-tp-bundle=\"kit\"]').scrollIntoView({block:'center'})")
        page.screenshot(path=str(SHOTS / f"passes-bundle-{width}.png"))
        page.close()

        # ---- /exchange
        page, errs = open_page(ctx, "exchange.html", width)
        page.wait_for_selector('[data-tp-bundle="exchange"] .tp-b-card', timeout=8000)
        fx = page.evaluate("""() => {
            const h = document.querySelector('[data-tp-bundle="exchange"]');
            return {head:(h.querySelector('.tp-b-head b')||{}).textContent||'', cards:h.querySelectorAll('.tp-b-card').length};
        }""")
        check(fx["cards"] >= 2, f"/exchange 기본(엔) 묶음 {fx['cards']}개 · {fx['head']}")
        page.select_option("#fxCur", "EUR")
        page.wait_for_timeout(300)
        fxe = page.evaluate("""() => (document.querySelector('[data-tp-bundle="exchange"] .tp-b-head b')||{}).textContent||''""")
        check("파리" in fxe, f"/exchange 유로 선택 → {fxe}")
        check(no_overflow(page), "/exchange 가로 넘침 없음")
        check(not errs, f"/exchange 콘솔 에러 {len(errs)}건")
        page.evaluate("() => document.querySelector('[data-tp-bundle=\"exchange\"]').scrollIntoView({block:'center'})")
        page.screenshot(path=str(SHOTS / f"exchange-bundle-{width}.png"))
        page.close()

        # ---- /stays 배지 겹침 + 클릭 추적
        page, errs = open_page(ctx, "stays.html", width)
        page.wait_for_timeout(500)
        geo = page.evaluate("""() => {
            const card = document.querySelector('.scard[data-region="paris"]');
            if (!card) return null;
            const badge = card.querySelector('.sc-flag');
            const fl = badge.querySelector('.sc-fl');
            const r = badge.getBoundingClientRect(), f = fl ? fl.getBoundingClientRect() : null;
            const range = document.createRange();
            range.selectNodeContents(badge);
            const rects = [...range.getClientRects()];
            const textRect = rects[rects.length-1];
            return {badge:[r.x,r.width], flag:f?[f.x,f.width]:null, text:textRect?[textRect.x,textRect.width]:null};
        }""")
        if geo and geo["flag"] and geo["text"]:
            gap = geo["text"][0] - (geo["flag"][0] + geo["flag"][1])
            check(gap >= 1.5, f"/stays 해외 배지 국기·텍스트 간격 {gap:.1f}px (겹침 없음)")
        else:
            check(False, "/stays 파리 카드 배지를 찾지 못함")
        check(no_overflow(page), "/stays 가로 넘침 없음")
        check(not errs, f"/stays 콘솔 에러 {len(errs)}건 " + (errs[0][:160] if errs else ""))
        # 클릭 추적: 실제 이동은 막고 capture 리스너가 먼저 기록하는지 확인
        page.evaluate("""() => {
            localStorage.removeItem('tp_clicks_v1');
            document.addEventListener('click', e => e.preventDefault(), true);
        }""")
        page.evaluate("""() => document.querySelector('.scard[data-region="paris"] .sc-cta').click()""")
        page.wait_for_timeout(200)
        clicks = page.evaluate("() => JSON.parse(localStorage.getItem('tp_clicks_v1')||'null')")
        ok = bool(clicks and clicks.get("total") == 1 and clicks.get("last", {}).get("partner") == "trip")
        check(ok, "제휴 클릭 → localStorage tp_clicks_v1 기록 " + json.dumps((clicks or {}).get("last", {}), ensure_ascii=False)[:160])
        page.evaluate("() => document.querySelector('.scard[data-region=\"paris\"]').scrollIntoView({block:'center'})")
        page.screenshot(path=str(SHOTS / f"stays-paris-{width}.png"))
        page.close()
        b.close()


if __name__ == "__main__":
    for w in (1280, 390):
        run(w)
    print("\n실패:", len(FAIL))
    for f in FAIL:
        print(" -", f)
    sys.exit(1 if FAIL else 0)
