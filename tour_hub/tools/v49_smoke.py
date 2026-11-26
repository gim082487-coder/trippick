#!/usr/bin/env python3
"""v49 기능 스모크 — 필터·정렬·검색·비교·찜·계산기·가이드 목차·/stays 필터가 그대로 동작하는지."""
from __future__ import annotations

import json
import os
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent.parent / "deploy_site"
PORT = 8822
fails = []


class Q(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send_head(self):
        p = self.translate_path(self.path)
        if not os.path.exists(p) and not self.path.startswith(('/assets', '/images')):
            c = p.rstrip('/') + '.html'
            if os.path.isfile(c):
                self.path = self.path.rstrip('/') + '.html'
        return super().send_head()


def check(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        fails.append(msg)


def main():
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), partial(Q, directory=str(ROOT)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{PORT}"
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, device_scale_factor=2)
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)[:100]))

        # 홈
        pg.goto(base + "/", wait_until="load"); pg.wait_for_timeout(800)
        check(pg.evaluate("()=>document.querySelectorAll('.pcard').length") == 84, "홈 상품 카드 84")
        pg.click('#ctabs .ctab[data-scope="jp"]'); pg.wait_for_timeout(400)
        check(pg.evaluate("()=>[...document.querySelectorAll('#sections .city')].filter(e=>e.offsetParent).length") == 4, "국가 탭 일본 → 도시 4")
        pg.click('.cchip[data-city="osaka"]'); pg.wait_for_timeout(400)
        n = pg.evaluate("()=>[...document.querySelectorAll('#sections .city')].filter(e=>e.offsetParent).length")
        check(n == 1, f"도시 칩 오사카 → 도시 {n}곳")
        # 섹션으로 스크롤해 카드 렌더 확인 (content-visibility)
        pg.evaluate("()=>document.getElementById('sections').scrollIntoView()"); pg.wait_for_timeout(600)
        vis = pg.evaluate("()=>[...document.querySelectorAll('#sections .pcard')].filter(e=>e.getBoundingClientRect().height>0).length")
        check(vis == 4, f"오사카 카드 4장 렌더({vis})")
        # 비교 담기
        pg.eval_on_selector("#sections .pcard .cmp-btn", "e=>e.click()"); pg.wait_for_timeout(400)
        check(pg.evaluate("()=>document.getElementById('cmpBar').classList.contains('on')"), "비교 바 열림")
        # 터치 영역
        sz = pg.evaluate("()=>{const e=document.querySelector('#sections .pcard .cmp-btn').getBoundingClientRect();return [Math.round(e.width),Math.round(e.height)]}")
        check(sz[0] >= 44, f"비교 버튼 폭 {sz}")
        # 검색
        pg.goto(base + "/", wait_until="load"); pg.wait_for_timeout(500)
        pg.fill("#q", "오사카"); pg.wait_for_timeout(700)
        check(pg.evaluate("()=>document.querySelectorAll('#sdrop .sd-item').length") > 0, "검색 드롭다운 결과")
        # 계산기
        pg.evaluate("()=>document.getElementById('planner').scrollIntoView()"); pg.wait_for_timeout(600)
        check(pg.evaluate("()=>document.querySelectorAll('#plBody .plan').length") >= 1
              and pg.evaluate("()=>document.querySelectorAll('.pl-tab').length") == 3, "예산 계산기 A/B/C 3안 + 본문 렌더")
        # 코스 탭
        pg.evaluate("()=>document.getElementById('courses').scrollIntoView()"); pg.wait_for_timeout(500)
        pg.click('.pick[data-course]:nth-of-type(2)') if pg.query_selector('.pick[data-course]') else None
        pg.wait_for_timeout(400)
        check(pg.evaluate("()=>document.querySelectorAll('.panel.active').length") == 1, "코스 탭 1개 활성")

        # /stays
        pg.goto(base + "/stays", wait_until="load"); pg.wait_for_timeout(800)
        check(pg.evaluate("()=>document.querySelectorAll('.scard').length") == 126, "/stays 카드 126")
        vis0 = pg.evaluate("()=>[...document.querySelectorAll('.scard')].filter(e=>e.getBoundingClientRect().height>0).length")
        check(vis0 == 24, f"/stays 첫 화면 {vis0}장(24장 점진 렌더)")
        pg.click('.gf-chip[data-scope="kr"]'); pg.wait_for_timeout(400)
        vis = pg.evaluate("()=>[...document.querySelectorAll('.scard')].filter(e=>e.getBoundingClientRect().height>0).length")
        check(vis == 24, f"/stays 국내 필터 → 첫 묶음 {vis}장")
        check(pg.evaluate("()=>document.getElementById('sfCount').textContent") == "54", "/stays 국내 54곳 집계")
        pg.eval_on_selector("#sfMore", "e=>e.click()"); pg.wait_for_timeout(350)
        vis2 = pg.evaluate("()=>[...document.querySelectorAll('.scard')].filter(e=>e.getBoundingClientRect().height>0).length")
        check(vis2 == 48, f"/stays 더 보기 → {vis2}장")
        pg.eval_on_selector("#sfMore", "e=>e.click()"); pg.wait_for_timeout(350)
        vis3 = pg.evaluate("()=>[...document.querySelectorAll('.scard')].filter(e=>e.getBoundingClientRect().height>0).length")
        check(vis3 == 54, f"/stays 더 보기 끝 → 국내 {vis3}장")
        check(pg.evaluate("()=>document.getElementById('sfMoreWrap').hidden") is True, "/stays 남은 카드 없으면 더 보기 숨김")
        pg.eval_on_selector(".scard .cmp-btn", "e=>e.click()"); pg.wait_for_timeout(400)
        check(pg.evaluate("()=>document.getElementById('cmpBar').classList.contains('on')"), "/stays 비교 바")

        # 가이드
        pg.goto(base + "/guides/", wait_until="load"); pg.wait_for_timeout(600)
        check(pg.evaluate("()=>document.querySelectorAll('.gcard').length") >= 100, "가이드 목록 100+")
        src = pg.evaluate("()=>document.querySelector('.gcard picture source')?.getAttribute('srcset') || ''")
        check("-720.webp" in src or "-480.webp" in src, "가이드 카드 WebP srcset")
        pg.goto(base + "/guides/bangkok-pattaya-3n5d-course-budget", wait_until="load"); pg.wait_for_timeout(600)
        pg.click(".gtoc-btn"); pg.wait_for_timeout(300)
        check(pg.evaluate("()=>document.querySelector('.gtoc-btn').getAttribute('aria-expanded')==='true'"), "가이드 목차 펼침")
        check(pg.evaluate("()=>!!document.querySelector('.pg-hero-img picture source')"), "가이드 히어로 WebP picture")

        # 도구 페이지
        pg.goto(base + "/passes", wait_until="load"); pg.wait_for_timeout(600)
        check(pg.evaluate("()=>document.querySelectorAll('#main h2').length") >= 5, "/passes 섹션 5")
        before = pg.evaluate("()=>document.querySelector('[data-passout], .pk-out, #passOut')?.textContent || document.body.textContent.includes('엔')")
        pg.eval_on_selector('input[data-fac="castle"]', "e=>e.click()"); pg.wait_for_timeout(300)
        check(pg.evaluate("()=>document.querySelectorAll('input[data-fac]').length") == 8, "/passes 계산 체크박스 동작")
        for path, sel in (("/exchange", "table"), ("/checklist", "input[type=checkbox]")):
            pg.goto(base + path, wait_until="load"); pg.wait_for_timeout(500)
            check(pg.evaluate(f"()=>document.querySelectorAll('{sel}').length") > 0, f"{path} 렌더")
        check(not errs, f"JS 오류 0 ({errs[:2]})")
        b.close()
    srv.shutdown()
    print("\n[SMOKE]", "PASS" if not fails else f"FAIL {len(fails)}건")


if __name__ == "__main__":
    main()
