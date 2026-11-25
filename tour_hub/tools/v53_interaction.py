#!/usr/bin/env python3
"""v53 상호작용 검증 — /passes 홍콩 계산기 · /stays 홍콩·마카오 필터 · 신규 가이드 렌더."""
from __future__ import annotations
import functools, http.server, socketserver, threading
from playwright.sync_api import sync_playwright

ROOT = "/workspace/trippick_repo/deploy_site"
Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
class Q(socketserver.TCPServer):
    allow_reuse_address = True
srv = Q(("127.0.0.1", 8093), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

fails = []
def check(ok, msg):
    print(("  ok   " if ok else "  FAIL ") + msg)
    if not ok: fails.append(msg)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/workspace/.tools/cft/chrome-linux64/chrome",
                          args=["--no-sandbox", "--disable-dev-shm-usage"])
    pg = b.new_page(viewport={"width": 1280, "height": 1000})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))

    pg.goto("http://127.0.0.1:8093/passes.html", wait_until="load")
    pg.wait_for_timeout(800)
    pg.click('.pk-tab[data-city="hongkong"]')
    pg.wait_for_timeout(500)
    check(pg.evaluate("()=>document.getElementById('pkHongkong').hidden") is False, "홍콩 패널 열림")
    check(pg.evaluate("()=>document.querySelectorAll('[data-hk]').length") == 3, "역 칩 3개")
    round2 = pg.inner_text("#pkHkRound")
    octo = pg.inner_text("#pkHkOcto")
    grp = pg.inner_text("#pkHkGroup")
    best = pg.inner_text("#pkHkBest")
    print("    2인·구룡:", round2, "|", octo, "|", grp, "| best:", best)
    check("390" in round2, "2인 왕복권 390홍콩달러")
    check("420" in octo, "2인 옥토퍼스 420홍콩달러")
    check("300" in grp, "2인 묶음표 왕복 300홍콩달러")
    check("공항버스" in best, "2인 최저는 공항버스 138.4홍콩달러")
    pg.click('.pk-btn[data-hk="hkg"]')
    pg.wait_for_timeout(400)
    check("430" in pg.inner_text("#pkHkRound"), "홍콩역 2인 왕복권 430홍콩달러")
    check(pg.input_value("#pkHkBus").startswith("41.9"), "홍콩역 → A11 41.9 자동")
    pg.fill("#pkHkPax", "4"); pg.dispatch_event("#pkHkPax", "input"); pg.wait_for_timeout(400)
    print("    4인·홍콩역:", pg.inner_text("#pkHkBest"), "| 묶음표", pg.inner_text("#pkHkGroup"))
    check("560" in pg.inner_text("#pkHkGroup"), "4인 묶음표 왕복 560홍콩달러")
    check("묶음표" in pg.inner_text("#pkHkVerdict"), "AEL 중 묶음표가 왕복권보다 싸다는 문구")
    pg.fill("#pkHkPax", "1"); pg.dispatch_event("#pkHkPax", "input"); pg.wait_for_timeout(400)
    check("공항버스" in pg.inner_text("#pkHkVerdict") or "버스" in pg.inner_text("#pkHkBest"), "1인은 버스/판정 문구")
    check(pg.evaluate("()=>document.getElementById('pkHkBestKrw').textContent.includes('원')"), "원화 환산 표시")

    pg.goto("http://127.0.0.1:8093/stays.html", wait_until="load")
    pg.wait_for_timeout(1200)
    n_all = pg.evaluate("()=>document.querySelectorAll('.scard').length")
    check(n_all == 116, f"/stays 카드 {n_all}")
    pg.click('.sf-chips [data-region="hongkong"]')
    pg.wait_for_timeout(600)
    vis = pg.evaluate("()=>[...document.querySelectorAll('.scard')].filter(e=>e.offsetParent).length")
    check(vis == 4, f"/stays 홍콩 필터 {vis}장")
    pg.click('.sf-chips [data-region="macau"]')
    pg.wait_for_timeout(600)
    vis2 = pg.evaluate("()=>[...document.querySelectorAll('.scard')].filter(e=>e.offsetParent).length")
    check(vis2 == 4, f"/stays 마카오 필터 {vis2}장")

    for slug in ("chiang-mai-3n4d-course", "bali-ubud-seminyak-3n4d-course", "shanghai-2n3d-3n4d-course"):
        pg.goto(f"http://127.0.0.1:8093/guides/{slug}.html", wait_until="load")
        pg.wait_for_timeout(500)
        sw = pg.evaluate("()=>document.documentElement.scrollWidth")
        iw = pg.evaluate("()=>innerWidth")
        faq = pg.evaluate("()=>document.querySelectorAll('details.fq').length")
        tables = pg.evaluate("()=>document.querySelectorAll('.tb table').length")
        broken = pg.evaluate("()=>[...document.images].filter(i=>i.complete && i.naturalWidth===0).length")
        check(sw <= iw + 2, f"{slug} 가로 넘침 없음 ({sw}/{iw})")
        check(faq >= 4, f"{slug} FAQ {faq}")
        check(tables >= 3, f"{slug} 표 {tables}")
        check(broken == 0, f"{slug} 깨진 이미지 0")

    check(len(errs) == 0, f"JS 오류 0 ({errs[:2]})")
    b.close()
srv.shutdown()
print("\n[V53-INTERACTION] " + ("PASS" if not fails else f"FAIL {len(fails)}"))
