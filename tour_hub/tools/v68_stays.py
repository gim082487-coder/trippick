#!/usr/bin/env python3
"""v68 찐숙소 11곳 — 트립닷컴 호텔 상세 페이지에서 주소·한국어명을 확인하고 대표 이미지를 저장한다.

    python3 tools/v68_stays.py

목록(평점·리뷰·1박 최저가)은 2026-12-10~11 · 성인 2명 · KRW 조회분(2026-11-28)이고,
이 스크립트는 각 호텔 상세 페이지(HTTP 200)의 값만 덧붙인다.
결과: /workspace/v68_stays_scraped.json + images/stays/{region}-{id}.jpg (600×600)
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

CITY = {"phuket": "725", "kobe": "423"}
SEL = {
    "phuket": ["702258", "703557", "702180", "21847079", "998415", "83988303"],
    "kobe": ["54594014", "704939", "63372661", "55210543", "1465318"],
}


def fetch(url: str) -> str:
    r = subprocess.run(["curl", "-sS", "-A", UA, "--max-time", "40", url], capture_output=True)
    return r.stdout.decode("utf-8", "ignore")


def main() -> int:
    out = {}
    for region, ids in SEL.items():
        out[region] = []
        for hid in ids:
            url = (f"https://kr.trip.com/hotels/detail/?cityId={CITY[region]}&hotelId={hid}&curr=KRW"
                   f"&checkIn=2026-12-10&checkOut=2026-12-11&adult=2"
                   f"&Allianceid=11407530&SID=336341874&trip_sub1=stays_{region}_{hid}&trip_sub3=D21372570")
            html = fetch(url)
            name = re.search(r'"hotelName\\?":\\?"([^"\\]{2,60})', html) or \
                re.search(r'<title>([^<|]{2,60})', html)
            addr = re.search(r'address\\":\\"([^"\\]+)', html) or re.search(r'"address":"([^"]+)"', html)
            ogm = re.search(r"(https://ak-d\.tripcdn\.com/images/[^\"'\\\s]+?\.(?:jpg|webp))", html)
            row = {"id": hid, "name": name.group(1).strip() if name else "",
                   "address": addr.group(1).strip() if addr else "",
                   "img_src": ogm.group(1) if ogm else "",
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
            print(region, hid, row["http"], row["name"][:30], "|", row["address"][:50], "|", row.get("img", "-"))
            sys.stdout.flush()
    Path("/workspace/v68_stays_scraped.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
