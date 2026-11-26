#!/usr/bin/env python3
"""v56 이미지 — 신규 가이드 3편 히어로(1200×800+WebP 480/720/960)·OG(1200×630)와 오키나와 허브(1600×1000).

    python3 tools/make_v56_images.py

펙셀스 원본만 씁니다. 사진마다 촬영지·alt 를 photo_credits.json 에 기록합니다.
"""
from __future__ import annotations

import io
import json
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
V56 = ROOT / "images" / "v56"
OG = ROOT / "images" / "og"
FONT_BOLD = Path("/workspace/tmp_font/Pretendard-Bold.otf")
FONT_NOTO = Path("/usr/share/fonts/pickle-hwp/NotoSansCJKkr-Regular.otf")

GUIDES = [
    {
        "slug": "okinawa-3n4d-course",
        "pid": 26612928,
        "alt": "오키나와 나하 해변의 파도와 산호초",
        "place": "Naha, Okinawa, Japan",
        "og": "v56-okinawa-guide-og.jpg",
        "kicker": "트립픽 · 오키나와 3박4일",
        "title": "나하 3박 vs 나하 2박+온나 1박",
        "title2": "츄라우미 2,180엔",
        "sub": "유이레일 290엔·13분  |  렌터카 6,600엔  |  eSIM 1일 101원",
    },
    {
        "slug": "southeast-asia-injection-guide",
        "pid": 8670443,
        "alt": "인슐린 펜과 줄자 — 여행 자가주사제 준비",
        "place": "Studio (Mikhail Nilov)",
        "og": "v56-injection-og.jpg",
        "kicker": "트립픽 · 준비물",
        "title": "동남아에 마운자로 들고 가기",
        "title2": "태국 30일 · 베트남 200달러",
        "sub": "원래 용기  |  처방전 사본  |  30℃ 21일",
    },
    {
        "slug": "bangkok-3n4d-course",
        "pid": 28969346,
        "alt": "방콕 왓아룬 사원과 짜오프라야강",
        "place": "Bangkok, Thailand",
        "og": "v56-bangkok-og.jpg",
        "kicker": "트립픽 · 방콕 3박4일",
        "title": "파타야를 넣으면 시내가 하루",
        "title2": "2인 128만~188만 원",
        "sub": "사원 3곳 1,000밧  |  공항철도 45밧  |  버스 144밧",
    },
]

HUB = {
    "slug": "okinawa",
    "pid": 26629179,
    "alt": "오키나와 바다와 해안 도로",
    "place": "Okinawa, Japan",
}


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    for p in (path, FONT_NOTO):
        if p.exists():
            return ImageFont.truetype(str(p), size)
    raise SystemExit(f"폰트를 찾지 못했습니다: {path}")


def fetch(pid: int, w: int = 2400) -> Image.Image:
    url = f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w={w}"
    req = urllib.request.Request(url, headers={"User-Agent": "trippick/5.6 (image fetch)"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return Image.open(io.BytesIO(r.read()))


def crop_ratio(im: Image.Image, tw: int, th: int, top: float = 0.42) -> Image.Image:
    im = ImageOps.exif_transpose(im).convert("RGB")
    target = tw / th
    sw, sh = im.size
    if sw / sh > target:
        nw = int(sh * target)
        im = im.crop(((sw - nw) // 2, 0, (sw + nw) // 2, sh))
    else:
        nh = int(sw / target)
        t = int((sh - nh) * top)
        im = im.crop((0, t, sw, t + nh))
    return im.resize((tw, th), Image.LANCZOS)


def hero(job: dict) -> Path:
    V56.mkdir(parents=True, exist_ok=True)
    im = crop_ratio(fetch(job["pid"]), 1200, 800, 0.5)
    p = V56 / f"{job['slug']}.jpg"
    im.save(p, "JPEG", quality=86, optimize=True, progressive=True)
    for w in (480, 720, 960):
        im.resize((w, round(800 * w / 1200)), Image.LANCZOS).save(
            V56 / f"{job['slug']}-{w}.webp", "WEBP", quality=78, method=6
        )
    return p


def og(job: dict) -> Path:
    W, H = 1200, 630
    img = crop_ratio(fetch(job["pid"]), W, H, 0.45)
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(shade)
    for x in range(W):
        a = int(200 * max(0.0, 1 - x / (W * 1.18)))
        d.rectangle([x, 0, x + 1, H], fill=(7, 18, 33, a))
    d.rectangle([0, H - 190, W, H], fill=(7, 18, 33, 120))
    img = Image.alpha_composite(img.convert("RGBA"), shade).convert("RGB")

    draw = ImageDraw.Draw(img)
    x, y = 68, 150
    draw.text((x, y), job["kicker"], font=font(FONT_NOTO, 30), fill=(196, 219, 255))
    y += 64
    draw.text((x, y), job["title"], font=font(FONT_BOLD, 66), fill=(255, 255, 255))
    y += 90
    draw.text((x, y), job["title2"], font=font(FONT_BOLD, 72), fill=(255, 255, 255))
    y += 108
    draw.text((x, y), job["sub"], font=font(FONT_NOTO, 26), fill=(221, 231, 243))
    draw.ellipse([x, H - 74, x + 15, H - 59], fill=(27, 92, 240))
    draw.text((x + 26, H - 82), "trippick.pages.dev", font=font(FONT_NOTO, 26), fill=(226, 234, 244))

    OG.mkdir(parents=True, exist_ok=True)
    p = OG / job["og"]
    img.save(p, "JPEG", quality=88, optimize=True, progressive=True)
    return p


def hub(job: dict) -> Path:
    V56.mkdir(parents=True, exist_ok=True)
    im = crop_ratio(fetch(job["pid"]), 1600, 1000, 0.42)
    p = V56 / f"{job['slug']}.jpg"
    im.save(p, "JPEG", quality=86, optimize=True, progressive=True)
    for w in (480, 720, 960):
        im.resize((w, round(w / 1.6)), Image.LANCZOS).save(
            V56 / f"{job['slug']}-{w}.webp", "WEBP", quality=80, method=5
        )
    ogi = crop_ratio(fetch(job["pid"]), 1200, 630, 0.42)
    ogi.save(OG / f"v56-{job['slug']}-og.jpg", "JPEG", quality=86, optimize=True, progressive=True)
    return p


def main() -> int:
    pri = json.loads((ROOT / "data" / "photo_credits.json").read_text(encoding="utf-8"))
    for job in GUIDES:
        h = hero(job)
        o = og(job)
        print(f"  · {h.relative_to(ROOT)} {Image.open(h).size} {h.stat().st_size // 1024}KB")
        print(f"  · {o.relative_to(ROOT)} {Image.open(o).size} {o.stat().st_size // 1024}KB")
        pri["photos"][f"v56/{job['slug']}"] = {
            "pexels_id": job["pid"], "place": job["place"], "alt": job["alt"],
            "url": f"https://www.pexels.com/photo/{job['pid']}/",
        }
    h = hub(HUB)
    print(f"  · {h.relative_to(ROOT)} {Image.open(h).size} {h.stat().st_size // 1024}KB")
    pri["photos"][f"v56/{HUB['slug']}"] = {
        "pexels_id": HUB["pid"], "place": HUB["place"], "alt": HUB["alt"],
        "url": f"https://www.pexels.com/photo/{HUB['pid']}/",
    }
    (ROOT / "data" / "photo_credits.json").write_text(
        json.dumps(pri, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
