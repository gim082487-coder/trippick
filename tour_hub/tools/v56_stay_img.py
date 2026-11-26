#!/usr/bin/env python3
"""v56 찐숙소 이미지 — 트립닷컴 호텔 상세 og:image를 받아 600×600으로 크롭.

    python3 tools/v56_stay_img.py region:cityId:hotelId [...]
"""
from __future__ import annotations
import re, subprocess, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")


def detail(city_id: str, hotel_id: str) -> str:
    return (f"https://kr.trip.com/hotels/detail/?cityId={city_id}&hotelId={hotel_id}&curr=KRW"
            f"&Allianceid=11407530&SID=336341874&trip_sub1=stays_{hotel_id}&trip_sub3=D21372570")


def fetch(url: str):
    r = subprocess.run(["curl", "-sS", "-A", UA, "-w", "\n%{http_code}", url], capture_output=True)
    body, _, code = r.stdout.rpartition(b"\n")
    return int(code or 0), body


def main() -> int:
    for arg in sys.argv[1:]:
        region, city, hid = arg.split(":")
        code, body = fetch(detail(city, hid))
        html = body.decode("utf-8", "ignore")
        m = re.search(r"og:image\\?\"?,?\\?\"?content\\?\"?:\\?\"?(https://ak-d\.tripcdn\.com/[^\\\"']+?\.(?:jpg|webp))", html)
        if not m:
            print(hid, "no image", code)
            continue
        img_url = m.group(1)
        dst = ROOT / "images" / "stays" / f"{region}-{hid}.jpg"
        tmp = ROOT / "images" / "stays" / f"_tmp_{hid}"
        subprocess.run(["curl", "-sS", "-A", UA, "-o", str(tmp), img_url], capture_output=True)
        try:
            im = Image.open(tmp).convert("RGB")
        except Exception as e:
            print(hid, "open fail", e)
            continue
        w, h = im.size
        s = min(w, h)
        im = im.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2)).resize((600, 600), Image.LANCZOS)
        im.save(dst, "JPEG", quality=82, optimize=True, progressive=True)
        tmp.unlink(missing_ok=True)
        print(hid, code, dst.relative_to(ROOT), dst.stat().st_size // 1024, "KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
