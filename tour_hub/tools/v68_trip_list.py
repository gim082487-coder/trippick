#!/usr/bin/env python3
"""v68 Trip.com 호텔 목록 파서 — 목록 HTML에 박힌 Next.js flight 데이터(initListData)를 읽는다.

    python3 tools/v68_trip_list.py <cityId> <checkin YYYY-MM-DD> <checkout YYYY-MM-DD> <pages> [out.json]

목록 URL: https://kr.trip.com/hotels/list?city={cityId}&checkin=..&checkout=..&adult=2&curr=KRW
각 행: hotelId·한국어명·성급·평점·리뷰수·세부점수·존·위치설명·1박 최저가(세금 포함)·통화·이미지.
값은 응답에 담긴 값 그대로이고, 환산·추정은 하지 않는다.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")


def fetch(url: str) -> str:
    r = subprocess.run(["curl", "-sS", "-A", UA, "--max-time", "60", url], capture_output=True)
    return r.stdout.decode("utf-8", "ignore")


def flight_buffer(html: str) -> str:
    chunks = re.findall(r'self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)', html)
    return "".join(json.loads(c) for c in chunks)


def slice_object(buf: str, key: str) -> dict:
    i = buf.find(f'"{key}":')
    if i < 0:
        raise SystemExit(f"{key} 없음")
    start = buf.index("{", i + len(key) + 3)
    depth = 0
    instr = esc = False
    for k in range(start, len(buf)):
        c = buf[k]
        if instr:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                instr = False
            continue
        if c == '"':
            instr = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return json.loads(buf[start:k + 1])
    raise SystemExit("JSON 끝을 찾지 못함")


def reviews_number(text: str) -> int:
    m = re.search(r"([\d,]+)", text or "")
    return int(m.group(1).replace(",", "")) if m else 0


def parse_cards(html: str) -> tuple[list[dict], dict]:
    obj = slice_object(flight_buffer(html), "initListData")
    req = obj.get("hotelSearchRequestStr", "{}")
    try:
        req = json.loads(req) if isinstance(req, str) else req
    except json.JSONDecodeError:
        req = {}
    rows = []
    for h in obj.get("hotelList", []):
        hi = h.get("hotelInfo", {})
        names = hi.get("nameInfo", {})
        ci = hi.get("commentInfo", {}) or {}
        pos = hi.get("positionInfo", {}) or {}
        rooms = h.get("roomInfo") or [{}]
        pi = rooms[0].get("priceInfo", {}) or {}
        subs = {}
        for s in ci.get("subScore") or []:
            if s.get("content") and s.get("number"):
                subs[s["content"]] = s["number"]
        rows.append({
            "id": hi.get("summary", {}).get("hotelId", ""),
            "name": names.get("name", ""),
            "en": names.get("enName", ""),
            "star": (hi.get("hotelStar") or {}).get("star"),
            "typeLabel": (hi.get("hotelCategory") or {}).get("categoryName", ""),
            "score": ci.get("commentScore", ""),
            "reviews": reviews_number(ci.get("commenterNumber", "")),
            "sub": subs,
            "zone": ", ".join(pos.get("zoneNames") or []),
            "position": pos.get("positionDesc", ""),
            "price": pi.get("price"),
            "currency": pi.get("currency", ""),
            "priceNote": pi.get("priceExplanation", ""),
            "img": (hi.get("hotelImages") or {}).get("url", ""),
            "cityId": pos.get("cityId"),
            "cityName": pos.get("cityName", ""),
        })
    return rows, req


def main() -> int:
    city, ci, co = sys.argv[1], sys.argv[2], sys.argv[3]
    pages = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    out = sys.argv[5] if len(sys.argv) > 5 else f"/workspace/v68_list_{city}.json"
    all_rows: list[dict] = []
    seen = set()
    for page in range(1, pages + 1):
        url = (f"https://kr.trip.com/hotels/list?city={city}&checkin={ci}&checkout={co}"
               f"&adult=2&curr=KRW&pageIndex={page}")
        html = fetch(url)
        rows, req = parse_cards(html) if "initListData" in html else ([], {})
        if not rows:
            print(f"page {page}: 카드 0 (html {len(html)}B)")
            continue
        print(f"page {page}: {len(rows)} cards · checkIn={req.get('checkIn')} checkOut={req.get('checkOut')} "
              f"· {rows[0]['cityName']}({rows[0]['cityId']})")
        for r in rows:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            all_rows.append(r)
    Path(out).write_text(json.dumps(all_rows, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in all_rows:
        print(f"  {r['id']:>10} {r['star']}성 {r['score']:>4} ({r['reviews']:>5}) {str(r['price']):>8}원 "
              f"{r['zone'][:12]:<12} {r['name'][:30]}")
    print(f"[v68] {len(all_rows)}곳 → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
