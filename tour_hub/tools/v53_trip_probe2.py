#!/usr/bin/env python3
"""v53 Trip.com 호텔 카드 구조 프로브 — 상세링크 주변 카드 텍스트 확인."""
from __future__ import annotations
import json, sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1]
JS = """() => {
  const res = [];
  document.querySelectorAll('a[href*="hotelId="]').forEach(a => {
    let n = a, best = null;
    for (let i = 0; i < 8 && n; i++) {
      n = n.parentElement;
      if (!n) break;
      const t = (n.innerText || '');
      if (t.length > 40 && /원|리뷰|평점/.test(t)) { best = n; break; }
    }
    res.push({href: a.getAttribute('href'), card: best ? best.innerText.replace(/\\n+/g,' | ') : a.innerText});
  });
  return res;
}"""
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/workspace/.tools/cft/chrome-linux64/chrome",
                          args=["--no-sandbox","--disable-dev-shm-usage"])
    ctx = b.new_context(viewport={"width":1280,"height":1400}, locale="ko-KR",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36")
    pg = ctx.new_page(); pg.goto(URL, wait_until="domcontentloaded", timeout=60000); pg.wait_for_timeout(6000)
    for _ in range(2):
        pg.mouse.wheel(0, 2000); pg.wait_for_timeout(2000)
    rows = pg.evaluate(JS)
    json.dump(rows, open(sys.argv[2] if len(sys.argv)>2 else "/workspace/.tmp_c.json","w"), ensure_ascii=False, indent=1)
    for r in rows[:6]: print(r["card"][:400]); print('---')
    b.close()
