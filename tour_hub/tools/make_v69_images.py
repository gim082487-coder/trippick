#!/usr/bin/env python3
"""v69 이미지 — 신규 가이드 3편 히어로(1200×800 + WebP 480/720/960)와 OG(1200×630).

    python3 tools/make_v69_images.py

새로 받는 사진 3장은 펙셀스(Pexels License)에서 images/v69_src/로 내려받았다(2026-11-28).
- 미국 렌터카: 모하비 사막 도로(2986512)
- 바르셀로나: 사그라다 파밀리아(33053358)
- 튀르키예: 카파도키아 열기구(38220564)
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
V69 = ROOT / "images" / "v69"
SRC = ROOT / "images" / "v69_src"
OG = ROOT / "images" / "og"
FONT_BOLD = Path("/workspace/tmp_font/Pretendard-Bold.otf")
FONT_NOTO = Path("/usr/share/fonts/pickle-hwp/NotoSansCJKkr-Regular.otf")

GUIDES = [
    {
        "slug": "usa-rental-car-insurance-guide",
        "pexels": 2986512,
        "alt": "모하비 사막을 달리는 차량과 도로",
        "credit": "사진: Pexels (Ricky Esquivel)",
        "og": "v69-usa-car-og.jpg",
        "kicker": "트립픽 · 미국 렌터카",
        "title": "보험 5일 601,135원",
        "title2": "통행료 하루 9.99달러",
        "sub": "국제면허 9,000원  |  휘발유 갤런 3.55달러  |  2026.11 확인",
    },
    {
        "slug": "barcelona-gaudi-montserrat-3n4d-guide",
        "pexels": 33053358,
        "alt": "사그라다 파밀리아 성당의 첨탑과 파사드",
        "credit": "사진: Pexels (Regan Dsouza)",
        "og": "v69-barcelona-og.jpg",
        "kicker": "트립픽 · 바르셀로나 3박4일",
        "title": "가우디 3곳 106,725원",
        "title2": "몬세라트 73,100원",
        "sub": "T-Casual 13유로  |  사그라다 26유로  |  2026.11 확인",
    },
    {
        "slug": "turkey-istanbul-cappadocia-guide",
        "pexels": 38220564,
        "alt": "카파도키아 일출과 열기구",
        "credit": "사진: Pexels (Yasin Onuş)",
        "og": "v69-turkey-og.jpg",
        "kicker": "트립픽 · 튀르키예 6박7일",
        "title": "무비자 90일",
        "title2": "열기구 260유로",
        "sub": "카트 46.20리라  |  뮤지엄패스 105유로  |  2026.11 확인",
    },
]


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


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


def src_path(job: dict) -> Path:
    return SRC / f"pexels-{job['pexels']}.jpg"


def hero(job: dict) -> Path:
    V69.mkdir(parents=True, exist_ok=True)
    im = crop_ratio(Image.open(src_path(job)), 1200, 800, 0.45)
    p = V69 / f"{job['slug']}.jpg"
    im.save(p, "JPEG", quality=86, optimize=True, progressive=True)
    for w in (480, 720, 960):
        im.resize((w, round(800 * w / 1200)), Image.LANCZOS).save(
            V69 / f"{job['slug']}-{w}.webp", "WEBP", quality=78, method=6
        )
    return p


def og(job: dict) -> Path:
    W, H = 1200, 630
    img = crop_ratio(Image.open(src_path(job)), W, H, 0.42)
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
    draw.text((x, y), job["title"], font=font(FONT_BOLD, 62), fill=(255, 255, 255))
    y += 86
    draw.text((x, y), job["title2"], font=font(FONT_BOLD, 62), fill=(255, 255, 255))
    y += 98
    draw.text((x, y), job["sub"], font=font(FONT_NOTO, 24), fill=(221, 231, 243))
    draw.ellipse([x, H - 74, x + 15, H - 59], fill=(27, 92, 240))
    draw.text((x + 26, H - 82), "trippick.pages.dev", font=font(FONT_NOTO, 26), fill=(226, 234, 244))

    OG.mkdir(parents=True, exist_ok=True)
    p = OG / job["og"]
    img.save(p, "JPEG", quality=88, optimize=True, progressive=True)
    return p


def main() -> int:
    pri = json.loads((ROOT / "data" / "photo_credits.json").read_text(encoding="utf-8"))
    for job in GUIDES:
        h = hero(job)
        o = og(job)
        print(f"  · {h.relative_to(ROOT)} {Image.open(h).size} {h.stat().st_size // 1024}KB")
        print(f"  · {o.relative_to(ROOT)} {Image.open(o).size} {o.stat().st_size // 1024}KB")
        pri["photos"][f"v69/{job['slug']}"] = {
            "credit": job["credit"],
            "alt": job["alt"],
            "source": "Pexels (Pexels License — 무료 상업적 사용)",
            "from": f"images/v69_src/pexels-{job['pexels']}.jpg",
            "url": f"https://www.pexels.com/photo/{job['pexels']}/",
        }
    (ROOT / "data" / "photo_credits.json").write_text(
        json.dumps(pri, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
