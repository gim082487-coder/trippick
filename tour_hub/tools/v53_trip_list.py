#!/usr/bin/env python3
"""v53 Trip.com 호텔 목록 수집기 — 카드별 호텔명·평점·리뷰·총액(숙박일수 기준) 추출.

    python3 tools/v53_trip_list.py "<trip.com hotels/list URL>" out.json [scrolls]
"""
from __future__ import annotations
import json, re, sys
from playwright.sync_api import sync_playwright

JS = """() => {
  const out = [];
  const seen = new Set();
  document.querySelectorAll('a[href*="hotelId="]').forEach(a => {
    const href = a.getAttribute('href') || '';
    const m = href.match(/hotelId=(\\d+)/);
    const id = m ? m[1] : '';
    if (!id || seen.has(id)) return;
    let n = a, card = null;
    for (let i = 0; i < 14 && n; i++) {
      n = n.parentElement;
      if (!n) break;
      const t = n.innerText || '';
      if ((t.includes('총금액') || t.includes('리뷰')) && t.length < 1500 && /\d원/.test(t)) { card = n; break; }
    }
    if (!card) { for (let i = 0; i < 10 && a; i++) { a = a.parentElement; if (a && (a.innerText||'').includes('리뷰')) card = a; } }
    if (!card) return;
    seen.add(id);
    out.push({ id, href, text: card.innerText.replace(/\\n+/g, ' | ') });
  });
  return out;
}"""

def parse(text: str) -> dict:
    parts = [p.strip() for p in text.split(" | ") if p.strip()]
    d = {"name": parts[0] if parts else "", "raw": text}
    m = re.search(r"리뷰 ([\d,]+)개", text)
    d["reviews"] = int(m.group(1).replace(",", "")) if m else 0
    sc = re.findall(r"\b(\d\.\d)\b", text)
    d["score"] = float(sc[-1]) if sc else 0.0
    tot = re.search(r"총금액:\s*([\d,]+)원", text)
    ps = [int(p[:-1].replace(",", "")) for p in parts if re.fullmatch(r"[\d,]{4,}원", p)]
    if tot:
        d["total"] = int(tot.group(1).replace(",", ""))
    else:
        d["total"] = min(ps) if ps else 0
    d["prices"] = [int(p[:-1].replace(",", "")) for p in parts if re.fullmatch(r"[\d,]{4,}원", p)]
    return d

def main():
    url, out = sys.argv[1], sys.argv[2]
    scrolls = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/workspace/.tools/cft/chrome-linux64/chrome",
                              args=["--no-sandbox", "--disable-dev-shm-usage"])
        ctx = b.new_context(viewport={"width": 1280, "height": 1400}, locale="ko-KR",
                            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36")
        pg = ctx.new_page()
        pg.goto(url, wait_until="domcontentloaded", timeout=60000)
        pg.wait_for_timeout(6000)
        for _ in range(scrolls):
            pg.mouse.wheel(0, 2400)
            pg.wait_for_timeout(1600)
        rows = pg.evaluate(JS)
        data = [parse(r["text"]) | {"id": r["id"], "href": r["href"]} for r in rows]
        data = [d for d in data if d["name"]]
        json.dump(data, open(out, "w"), ensure_ascii=False, indent=1)
        print(f"{pg.title()} cards={len(data)}")
        for d in data[:15]:
            print(f"  {d['id']:>10} {d['score']} ({d['reviews']}) {d['total']:>9,}원 {d['name'][:34]}")
        b.close()

if __name__ == "__main__":
    main()
