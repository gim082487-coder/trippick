#!/usr/bin/env python3
"""v49 모바일(390) UX 프로브 — 필터·비교·검색·터치영역·겹침."""
from __future__ import annotations

import json
import os
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent.parent / "deploy_site"
PORT = 8814


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


def main():
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), partial(Q, directory=str(ROOT)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{PORT}"
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True,
                            device_scale_factor=2,
                            user_agent="Mozilla/5.0 (Linux; Android 14; SM-S911N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131 Mobile Safari/537.36")
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)[:120]))
        pg.goto(base + "/", wait_until="load")
        pg.wait_for_timeout(800)

        # 1) 도시 칩 필터
        chips = pg.eval_on_selector_all("#regions .chip, #regions [data-city]", "els=>els.slice(0,6).map(e=>({t:e.textContent.trim(), w:Math.round(e.getBoundingClientRect().width), h:Math.round(e.getBoundingClientRect().height)}))")
        print("city chips:", json.dumps(chips, ensure_ascii=False)[:400])
        try:
            chip = pg.query_selector('#regions [data-city="osaka"], #regions .chip:has-text("오사카")')
            if chip:
                before = pg.eval_on_selector_all("#regions .pcard", "els=>els.filter(e=>e.offsetParent).length")
                chip.click()
                pg.wait_for_timeout(500)
                after = pg.eval_on_selector_all("#regions .pcard", "els=>els.filter(e=>e.offsetParent).length")
                print(f"filter osaka: visible {before} -> {after}")
        except Exception as e:
            print("chip click fail", e)

        # 2) 필터 바 가로 스크롤 여부
        r = pg.evaluate("""()=>{const out=[];document.querySelectorAll('.filters,.chips,.chiprow,.fbar,[class*=filter]').forEach(el=>{
            if(el.scrollWidth>el.clientWidth+2) out.push({cls:el.className.slice(0,40),sw:el.scrollWidth,cw:el.clientWidth,h:el.clientHeight});});return out.slice(0,6);}""")
        print("h-scroll rows:", json.dumps(r, ensure_ascii=False)[:400])

        # 3) 버튼 터치 영역 44px 미만 (버튼/탭/셀렉트만)
        small = pg.evaluate("""()=>{const out=[];document.querySelectorAll('button,select,a.btn,a.primary,a.ghost,.cmp-btn,.chip,.tabs a,[role=tab]').forEach(el=>{
            const b=el.getBoundingClientRect(); if(!b.width||!b.height) return;
            if(b.width<44||b.height<44) out.push({tag:el.tagName,cls:(el.className||'').toString().slice(0,30),w:Math.round(b.width),h:Math.round(b.height),t:(el.textContent||'').trim().slice(0,18)});});return out;}""")
        print(f"small tap targets (buttons/tabs): {len(small)}")
        for s in small[:12]:
            print("   ", s)

        # 4) 상품 카드 CTA 44px 이상인지
        cta = pg.evaluate("""()=>[...document.querySelectorAll('.pcard')].slice(0,3).map(c=>{const a=c.querySelector('.book'),b=c.querySelector('.cmp-btn'),w=c.querySelector('.wish-btn');const r=e=>e?{w:Math.round(e.getBoundingClientRect().width),h:Math.round(e.getBoundingClientRect().height)}:null;return{book:r(a),cmp:r(b),wish:r(w)};})""")
        print("card cta sizes:", json.dumps(cta, ensure_ascii=False))

        # 5) 비교 담기 → 하단 바 겹침?
        try:
            pg.eval_on_selector(".pcard .cmp-btn", "e=>e.click()")
            pg.wait_for_timeout(400)
            bar = pg.evaluate("""()=>{const el=document.querySelector('.cmpbar,.compare-bar,[class*=cmpbar]');if(!el)return null;const r=el.getBoundingClientRect();const s=getComputedStyle(el);return{top:Math.round(r.top),h:Math.round(r.height),pos:s.position,z:s.zIndex,hidden:el.hidden};}""")
            print("compare bar:", bar)
        except Exception as e:
            print("compare fail", e)

        # 6) 헤더 sticky 높이 / 첫 화면 콘텐츠
        hd = pg.evaluate("""()=>{const h=document.querySelector('header');const r=h.getBoundingClientRect();const hero=document.querySelector('.hero');return{header:Math.round(r.height),pos:getComputedStyle(h).position,hero:hero?Math.round(hero.getBoundingClientRect().height):0,foldSeen:[...document.querySelectorAll('h1,h2')].filter(e=>e.getBoundingClientRect().top<844).map(e=>e.textContent.trim().slice(0,24))};}""")
        print("header/hero:", json.dumps(hd, ensure_ascii=False))

        # 7) 검색 드롭다운 동작
        try:
            pg.fill("#q", "오사카")
            pg.wait_for_timeout(700)
            sd = pg.evaluate("""()=>{const b=document.getElementById('sdrop');if(!b)return null;const r=b.getBoundingClientRect();return{hidden:b.hidden,cls:b.className,w:Math.round(r.width),h:Math.round(r.height),left:Math.round(r.left),right:Math.round(r.right),items:b.querySelectorAll('.sd-item').length};}""")
            print("search dropdown:", sd)
        except Exception as e:
            print("search fail", e)

        # 8) 가이드 페이지
        pg.goto(base + "/guides/bangkok-pattaya-3n5d-course-budget", wait_until="load")
        pg.wait_for_timeout(600)
        g = pg.evaluate("""()=>{const a=document.querySelector('article');const r=a.getBoundingClientRect();
          const ad=[...document.querySelectorAll('.adslot')].map(e=>({h:Math.round(e.getBoundingClientRect().height),hasIns:!!e.querySelector('ins')}));
          const tbl=[...document.querySelectorAll('table')].map(t=>({sw:t.scrollWidth,cw:t.clientWidth}));
          const toc=document.querySelector('.gtoc-btn');const tr=toc?toc.getBoundingClientRect():null;
          return {articleW:Math.round(r.width),fontSize:getComputedStyle(a).fontSize,lineHeight:getComputedStyle(a).lineHeight,
            overflow:document.documentElement.scrollWidth-innerWidth, ad, tables:tbl, tocBtn:tr?{w:Math.round(tr.width),h:Math.round(tr.height)}:null};}""")
        print("guide:", json.dumps(g, ensure_ascii=False))

        # 9) /passes 계산기
        pg.goto(base + "/passes", wait_until="load")
        pg.wait_for_timeout(600)
        ps = pg.evaluate("""()=>{const els=[...document.querySelectorAll('input,select,button')].slice(0,10).map(e=>({tag:e.tagName,type:e.type,w:Math.round(e.getBoundingClientRect().width),h:Math.round(e.getBoundingClientRect().height)}));return {n:document.querySelectorAll('input,select,button').length, els};}""")
        print("passes controls:", json.dumps(ps, ensure_ascii=False)[:500])

        print("page errors:", errs)
        b.close()
    srv.shutdown()


if __name__ == "__main__":
    main()
