#!/usr/bin/env python3
"""v65 찐숙소 30곳 — 트립닷컴 호텔 상세에서 성급·세부 점수·주소·og:image를 받아 저장한다.

    python3 tools/v65_stays.py

목록(평점·리뷰·1박 최저가)은 2027-01-15~16 · 성인 2명 · KRW 조회분(2026-11-27)이고,
이 스크립트는 각 호텔 상세 페이지(HTTP 200)의 값만 덧붙인다.
결과: /workspace/v65_stays_scraped.json + images/stays/{region}-{id}.jpg (600×600)
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")

SEL = {
    "newyork": ["2092657", "2192841", "105237897", "1565906", "2193990"],
    "nagoya": ["8344318", "5086203", "703777", "72147574", "93970929"],
    "phuquoc": ["10200862", "31583072", "9585235", "91307436", "2562937"],
    "cebu": ["102030816", "759892", "5902851", "10549822", "99386475"],
    "sydney": ["9341526", "29958862", "736187", "734373", "714671"],
    "sapporo": ["705841", "62987948", "31315741", "52762809", "44402748"],
}
CITY = {"newyork": "633", "nagoya": "360", "phuquoc": "5649", "cebu": "1239",
        "sydney": "501", "sapporo": "641"}


def fetch(url: str) -> str:
    r = subprocess.run(["curl", "-sS", "-A", UA, "--max-time", "40", url], capture_output=True)
    return r.stdout.decode("utf-8", "ignore")


def main() -> int:
    out = {}
    for region, ids in SEL.items():
        out[region] = []
        for hid in ids:
            url = (f"https://kr.trip.com/hotels/detail/?cityId={CITY[region]}&hotelId={hid}&curr=KRW"
                   f"&Allianceid=11407530&SID=336341874&trip_sub1=stays_{region}_{hid}&trip_sub3=D21372570")
            html = fetch(url)
            star = re.search(r'starInfo\\":\{\\"level\\":(\d)', html) or re.search(r'star\\":(\d)', html)
            subs = dict(re.findall(r'showName\\":\\"([^\\"]+)\\",\\"showScore\\":\\"([\d.]+)\\"', html))
            addr = re.search(r'address\\":\\"([^\\"]+)\\"', html)
            ogm = re.search(r"og:image\\+?\\?\"?,?\\+?\\?\"?content\\+?\\?\"?:\\+?\\?\"?(https://ak-d\.tripcdn\.com/[^\\\"']+?\.(?:jpg|webp))", html)
            if not ogm:
                ogm = re.search(r"(https://ak-d\.tripcdn\.com/images/[^\\\"'\s]+?\.(?:jpg|webp))", html)
            row = {"id": hid, "star": int(star.group(1)) if star else None, "sub": subs,
                   "address": addr.group(1) if addr else "", "img_src": ogm.group(1) if ogm else "",
                   "http": 200 if len(html) > 50000 else len(html)}
            if row["img_src"]:
                dst = ROOT / "images" / "stays" / f"{region}-{hid}.jpg"
                tmp = ROOT / "images" / "stays" / f"_tmp_{hid}"
                subprocess.run(["curl", "-sS", "-A", UA, "--max-time", "40", "-o", str(tmp), row["img_src"]],
                               capture_output=True)
                try:
                    im = Image.open(tmp).convert("RGB")
                    w, h = im.size
                    s = min(w, h)
                    im = im.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2)).resize((600, 600), Image.LANCZOS)
                    im.save(dst, "JPEG", quality=82, optimize=True, progressive=True)
                    row["img"] = f"images/stays/{region}-{hid}.jpg"
                except Exception as e:  # noqa: BLE001
                    row["img_error"] = str(e)
                finally:
                    tmp.unlink(missing_ok=True)
            out[region].append(row)
            print(region, hid, row["http"], row["star"], row["sub"], row["address"][:40], row.get("img", "-"))
            sys.stdout.flush()
    Path("/workspace/v65_stays_scraped.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
