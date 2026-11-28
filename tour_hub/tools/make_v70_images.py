#!/usr/bin/env python3
"""v70 이미지 — 신규 가이드 2편 히어로(1200×800 + WebP 480/720/960)와 OG(1200×630).

    python3 tools/make_v70_images.py

새로 받는 사진 2장은 펙셀스(Pexels License)에서 images/v70_src/로 내려받았다(2026-11-28).
- 마운자로 일본 여행지: 교토 기요미즈데라(Belle Co, 402028)
- 대부도: 서해 갯벌 노을(Fu Shan Un, 31683979)
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
V70 = ROOT / "images" / "v70"
SRC = ROOT / "images" / "v70_src"
OG = ROOT / "images" / "og"
FONT_BOLD = Path("/workspace/tmp_font/Pretendard-Bold.otf")
FONT_NOTO = Path("/usr/share/fonts/pickle-hwp/NotoSansCJKkr-Regular.otf")

GUIDES = [
    {
        "slug": "japan-mounjaro-travel-destinations",
        "pexels": 402028,
        "alt": "교토 기요미즈데라의 탑과 단풍",
        "credit": "사진: Pexels (Belle Co)",
        "og": "v70-mounjaro-dest-og.jpg",
        "kicker": "트립픽 · 마운자로 일본 여행",
        "title": "공항에서 숙소까지",
        "title2": "도쿄 41분·삿포로 33분",
        "sub": "스카이라이너 2,470엔  |  규동 小盛 465엔  |  2026.11 확인",
    },
    {
        "slug": "daebudo-daytrip-1n2d-course",
        "pexels": 31683979,
        "alt": "서해 갯벌 위로 지는 노을",
        "credit": "사진: Pexels (Fu Shan Un)",
        "og": "v70-daebudo-og.jpg",
        "kicker": "트립픽 · 대부도 1박2일",
        "title": "물때가 일정표",
        "title2": "바닷길 1.2km",
        "sub": "달전망대 무료  |  버스 1,650원  |  2026.11 확인",
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
    V70.mkdir(parents=True, exist_ok=True)
    im = crop_ratio(Image.open(src_path(job)), 1200, 800, 0.45)
    p = V70 / f"{job['slug']}.jpg"
    im.save(p, "JPEG", quality=86, optimize=True, progressive=True)
    for w in (480, 720, 960):
        im.resize((w, round(800 * w / 1200)), Image.LANCZOS).save(
            V70 / f"{job['slug']}-{w}.webp", "WEBP", quality=78, method=6
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
        pri["photos"][f"v70/{job['slug']}"] = {
            "credit": job["credit"],
            "alt": job["alt"],
            "source": "Pexels (Pexels License — 무료 상업적 사용)",
            "from": f"images/v70_src/pexels-{job['pexels']}.jpg",
            "url": f"https://www.pexels.com/photo/{job['pexels']}/",
        }
    (ROOT / "data" / "photo_credits.json").write_text(
        json.dumps(pri, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
