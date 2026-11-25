#!/usr/bin/env python3
"""v53 Trip.com 호텔 목록 수집 — 도시·날짜·인원으로 호텔명/평점/리뷰/1박가/ID 추출."""
from __future__ import annotations
import json, sys, re, time
from playwright.sync_api import sync_playwright

URL = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else "/workspace/.tmp_probe.json"
SCROLLS = int(sys.argv[3]) if len(sys.argv) > 3 else 4

JS = """() => {
  const out = [];
  const seen = new Set();
  const push = (a) => {
    const t = (a.innerText || '').trim();
    if (!t) return;
    const href = a.getAttribute('href') || '';
    const m = href.match(/hotelId=(\\d+)/) || t.match(/(\\d{5,})/);
    const id = m ? m[1] : '';
    const key = id + '|' + t.slice(0, 30);
    if (seen.has(key)) return;
    seen.add(key);
    out.push({id, href, text: t.replace(/\\n+/g, ' | ')});
  };
  document.querySelectorAll('a[href*="hotels/detail"], a[href*="hotelId="]').forEach(push);
  return out;
}"""

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/workspace/.tools/cft/chrome-linux64/chrome",
                          args=["--no-sandbox", "--disable-dev-shm-usage"])
    ctx = b.new_context(viewport={"width": 1280, "height": 1400}, locale="ko-KR",
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36")
    pg = ctx.new_page()
    pg.goto(URL, wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(5000)
    for i in range(SCROLLS):
        pg.mouse.wheel(0, 2200)
        pg.wait_for_timeout(1800)
    rows = pg.evaluate(JS)
    # dedupe by id keeping longest text
    best: dict[str, dict] = {}
    for r in rows:
        k = r["id"] or r["text"][:40]
        if k not in best or len(r["text"]) > len(best[k]["text"]):
            best[k] = r
    data = list(best.values())
    json.dump(data, open(OUT, "w"), ensure_ascii=False, indent=1)
    print(f"TITLE: {pg.title()}  cards: {len(data)}")
    for r in data[:12]:
        print(r["id"], "|", r["text"][:180])
    b.close()
