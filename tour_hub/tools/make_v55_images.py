#!/usr/bin/env python3
"""v55 도시 허브(괌·사이판·싱가포르·홍콩·마카오·파리·런던·로마·바르셀로나) 이미지.

펙셀스 원본 → 허브 히어로 1600×1000(+WebP 480/720/960) · OG 1200×630.

    python3 tools/make_v55_images.py
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "images" / "v55"
OG = ROOT / "images" / "og"

# slug, pexels id, 사진 설명(alt), 촬영지
JOBS = [
    ("guam", 24033245, "괌 투몬 만의 리조트와 바다", "Tumon, Guam"),
    ("saipan", 31094871, "사이판 산호초에서 만난 바다거북과 다이버", "Saipan"),
    ("singapore", 31949002, "마리나 베이 샌즈와 싱가포르 스카이라인", "Singapore"),
    ("hongkong", 15748374, "빅토리아 하버에서 본 홍콩 스카이라인", "Hong Kong"),
    ("macau", 38783880, "마카오 세나도 광장의 물결 무늬 보도", "Macao"),
    ("paris", 18411385, "에펠탑과 파리 시내가 보이는 드론 항공샷", "Paris"),
    ("london", 10771574, "템스강 위 런던 타워 브리지", "London"),
    ("rome", 15460829, "로마 콜로세움", "Roma"),
    ("barcelona", 18449847, "바르셀로나 사그라다 파밀리아 성당", "Barcelona"),
]


def fetch(pid: int, w: int = 2400) -> Image.Image:
    url = f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w={w}"
    req = urllib.request.Request(url, headers={"User-Agent": "trippick/5.5 (image fetch)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return Image.open(r).convert("RGB")


def crop(im: Image.Image, ratio: float) -> Image.Image:
    w, h = im.size
    if w / h > ratio:
        nw = int(h * ratio)
        box = ((w - nw) // 2, 0, (w + nw) // 2, h)
    else:
        nh = int(w / ratio)
        top = int((h - nh) * 0.42)
        box = (0, top, w, top + nh)
    return im.crop(box)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pri = json.loads((ROOT / "data" / "photo_credits.json").read_text(encoding="utf-8"))
    for job in JOBS:
        slug, pid, alt, place = job
        im = fetch(pid)
        hero = crop(im, 1.6).resize((1600, 1000), Image.LANCZOS)
        hero.save(OUT / f"{slug}.jpg", quality=86, optimize=True, progressive=True)
        for w in (480, 720, 960):
            h = round(w / 1.6)
            hero.resize((w, h), Image.LANCZOS).save(OUT / f"{slug}-{w}.webp", quality=80, method=5)
        og = crop(im, 1200 / 630).resize((1200, 630), Image.LANCZOS)
        og.save(OG / f"v55-{slug}-og.jpg", quality=86, optimize=True, progressive=True)
        pri["photos"][f"v55/{slug}"] = {
            "pexels_id": pid,
            "place": place,
            "alt": alt,
            "url": f"https://www.pexels.com/photo/{pid}/",
        }
        print(slug, "ok", hero.size)
    (ROOT / "data" / "photo_credits.json").write_text(
        json.dumps(pri, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
