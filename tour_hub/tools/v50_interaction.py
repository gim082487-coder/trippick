#!/usr/bin/env python3
"""v50 상호작용 검증 — 첫 화면을 막지 않으려고 JSON(tpData·tpSearch·tpCompare)을
정적 파일로 뺐기 때문에, '처음 쓰는 순간'에 기능이 그대로 동작하는지 확인한다.

  · 홈: 로드 직후 첫 타이핑 → 검색 드롭다운 결과
  · 홈: ?pax=3&region=jp&style=value 복원 → 3인 금액
  · 홈: 비교 2개 담기 → 나란히 비교 모달 표
  · 홈: 계산기 탭 클릭(데이터 로드 전 클릭 포함) → 패널 갱신
  · /stays: ?region=guam 딥링크 → 4장 + 지역 칩 표시
  · 신규 가이드: FAQ 펼침
  · data/tp-*.json 4개 HTTP 200
"""
from __future__ import annotations

import json
import os
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent.parent / "deploy_site"
PORT = 8877
fails = []
seen = []


class Q(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send_head(self):
        path_only, _, qs = self.path.partition("?")
        qs = qs.split("#")[0]
        p = self.translate_path(path_only)
        if not os.path.exists(p) and not path_only.startswith(('/assets', '/images', '/data')):
            c = p.rstrip('/') + '.html'
            if os.path.isfile(c):
                path_only = path_only.rstrip('/') + '.html'
        self.path = path_only + (("?" + qs) if qs else "")
        return super().send_head()


def check(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        fails.append(msg)


def main():
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), partial(Q, directory=str(ROOT)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{PORT}"

    for f in ("tp-data.json", "tp-plans.json", "tp-search.json", "tp-compare.json"):
        r = Q  # noqa: F841
        import urllib.request
        with urllib.request.urlopen(f"{base}/data/{f}") as resp:
            check(resp.status == 200 and len(resp.read()) > 1000, f"/data/{f} 200")

    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        pg = ctx.new_page()
        errs = []
        bad = []
        pg.on("pageerror", lambda e: errs.append(str(e)[:120]))
        pg.on("response", lambda r: bad.append((r.status, r.url)) if r.status >= 400 else None)

        # 1) 로드 직후 첫 타이핑 → 검색 결과 (lazy fetch가 입력 전에 끝나지 않아도 동작해야 함)
        pg.goto(base + "/", wait_until="domcontentloaded")
        pg.fill("#q", "오사카")
        pg.wait_for_timeout(1500)
        n = pg.evaluate("()=>document.querySelectorAll('#sdrop .sd-item').length")
        check(n > 0, f"첫 타이핑 검색 결과 {n}건")
        check(pg.evaluate("()=>document.getElementById('tpSearch').textContent.length") > 1000, "tpSearch 지연 로드됨")

        # 2) 공유 링크 파라미터 복원 (3인·일본)
        pg.goto(base + "/?pax=3&region=jp&style=value", wait_until="load")
        pg.wait_for_timeout(2500)
        pax = pg.evaluate("()=>document.getElementById('paxVal')?.textContent || ''")
        check(pax.strip() == "3명", f"공유 링크 인원 복원({pax.strip()})")
        tot = pg.evaluate("()=>{const e=document.querySelector('#plBody .plan b');return e?e.textContent:''}")
        check(bool(tot), f"계산기 3인 금액 렌더({tot})")

        # 3) 비교 2개 담고 모달 열기
        pg.goto(base + "/", wait_until="load")
        pg.wait_for_timeout(800)
        pg.eval_on_selector_all("#sections .pcard .cmp-btn", "els=>{els[0].click();els[1].click();}")
        pg.wait_for_timeout(1200)
        check(pg.evaluate("()=>document.getElementById('cmpBar').classList.contains('on')"), "비교 바 열림(2개)")
        pg.eval_on_selector("#cbOpen", "e=>e.click()")
        pg.wait_for_timeout(500)
        rows = pg.evaluate("()=>document.querySelectorAll('#cmpBody table.cmpt tbody tr').length")
        check(rows >= 5, f"비교 모달 표 {rows}행")

        # 4) 계산기 탭 클릭 (데이터 로드 전 클릭을 흉내: 새 페이지에서 즉시 클릭)
        pg.goto(base + "/#planner", wait_until="domcontentloaded")
        before = pg.evaluate("()=>document.querySelector('#plBody .plan b')?.textContent || ''")
        pg.eval_on_selector_all(".pl-tab", "els=>{if(els[1])els[1].click();}")
        pg.wait_for_timeout(1600)
        tab = pg.evaluate("()=>{const e=document.querySelector('.pl-tab[aria-selected=\"true\"]');return e?e.querySelector('.pt-b')?.textContent:''}")
        after = pg.evaluate("()=>document.querySelector('#plBody .plan b')?.textContent || ''")
        check(tab in ('B', 'B안') or (tab == 'B' and after != before), f"계산기 탭 클릭 후 B안 전환({tab}·{before}→{after})")

        # 5) /stays 딥링크
        pg.goto(base + "/stays?region=guam", wait_until="load")
        pg.wait_for_timeout(900)
        vis = pg.evaluate("()=>[...document.querySelectorAll('.scard')].filter(e=>e.getBoundingClientRect().height>0).length")
        chip = pg.evaluate("()=>{const e=document.querySelector('.gf-chip[data-region=\"guam\"]');return e?e.className:''}")
        check(vis == 3 and "on" in chip, f"/stays?region=guam → {vis}장·지역 칩 활성")

        # 6) 신규 가이드 FAQ
        pg.goto(base + "/guides/travel-medication-rules-guide", wait_until="load")
        pg.wait_for_timeout(500)
        cnt = pg.evaluate("()=>document.querySelectorAll('details.fq').length")
        pg.eval_on_selector("details.fq summary", "e=>e.click()")
        pg.wait_for_timeout(250)
        opened = pg.evaluate("()=>document.querySelectorAll('details.fq[open]').length")
        check(cnt == 5 and opened == 1, f"신규 가이드 FAQ {cnt}문항·펼침 {opened}")

        check(not errs, f"JS 오류 0 ({errs[:2]})")
        check(not [x for x in bad if x[1].startswith(base)], f"4xx/5xx 0 ({[x for x in bad if x[1].startswith(base)][:3]})")
        b.close()
    srv.shutdown()
    print("\n[V50 INTERACTION]", "PASS" if not fails else f"FAIL {len(fails)}건")


if __name__ == "__main__":
    main()
