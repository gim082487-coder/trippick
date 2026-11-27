#!/usr/bin/env python3
"""v63 이미지 — 신규 가이드 3편 히어로(1200×800+WebP 480/720/960)·OG(1200×630).

    python3 tools/make_v63_images.py

사진은 이미 사이트에서 쓰고 있는 실제 사진(펙셀스, 저작자 병기)을 그대로 소스로 쓴다.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
V63 = ROOT / "images" / "v63"
OG = ROOT / "images" / "og"
FONT_BOLD = Path("/workspace/tmp_font/Pretendard-Bold.otf")
FONT_NOTO = Path("/usr/share/fonts/pickle-hwp/NotoSansCJKkr-Regular.otf")

GUIDES = [
    {
        "slug": "tokyo-3n4d-course-budget",
        "src": "images/v51/japan-ic-card.jpg",
        "alt": "도쿄 지하철 개찰구에서 IC카드로 통과하는 사람들",
        "credit": "사진: Pexels (Imani Williams)",
        "pexels_id": 5905655,
        "og": "v63-tokyo-og.jpg",
        "kicker": "트립픽 · 도쿄 3박4일",
        "title": "지하철 72시간 1,500엔",
        "title2": "전망대 하나만 고르기",
        "sub": "게이세이 1,060엔  |  스카이트리 1,800엔~  |  2인 7만 3,619원",
    },
    {
        "slug": "visa-free-stay-duration-guide",
        "src": "images/v33/passport-application.jpg",
        "alt": "여권 스탬프가 찍힌 여권 면을 손에 든 모습",
        "credit": "사진: Ekaterina Belinskaya / Pexels",
        "pexels_id": 4922086,
        "og": "v63-visa-og.jpg",
        "kicker": "트립픽 · 무비자 체류기간",
        "title": "90일 · 45일 · 30일",
        "title2": "협정이 기간을 갈랐습니다",
        "sub": "일본·태국 90일  |  베트남 45일  |  인도네시아는 도착비자",
    },
    {
        "slug": "southeast-asia-rental-car-license-guide",
        "src": "images/v52/japan-rental-car-etc-guide.jpg",
        "alt": "렌터카 차 안에서 본 내비게이션과 도로 풍경",
        "credit": "사진: Pexels (Faheem Ahamad)",
        "pexels_id": 40248235,
        "og": "v63-rental-og.jpg",
        "kicker": "트립픽 · 동남아 렌터카",
        "title": "태국은 되고",
        "title2": "발리는 안 됩니다",
        "sub": "국제면허 9,000원  |  베트남 입국일부터 1년  |  필리핀 90일",
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


def hero(job: dict) -> Path:
    V63.mkdir(parents=True, exist_ok=True)
    im = crop_ratio(Image.open(ROOT / job["src"]), 1200, 800, 0.45)
    p = V63 / f"{job['slug']}.jpg"
    im.save(p, "JPEG", quality=86, optimize=True, progressive=True)
    for w in (480, 720, 960):
        im.resize((w, round(800 * w / 1200)), Image.LANCZOS).save(
            V63 / f"{job['slug']}-{w}.webp", "WEBP", quality=78, method=6
        )
    return p


def og(job: dict) -> Path:
    W, H = 1200, 630
    img = crop_ratio(Image.open(ROOT / job["src"]), W, H, 0.42)
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


def main() -> int:
    pri = json.loads((ROOT / "data" / "photo_credits.json").read_text(encoding="utf-8"))
    for job in GUIDES:
        h = hero(job)
        o = og(job)
        print(f"  · {h.relative_to(ROOT)} {Image.open(h).size} {h.stat().st_size // 1024}KB")
        print(f"  · {o.relative_to(ROOT)} {Image.open(o).size} {o.stat().st_size // 1024}KB")
        pri["photos"][f"v63/{job['slug']}"] = {
            "source": "Pexels (Pexels License — 무료 상업적 사용)",
            "from": job["src"],
            "pexels_id": job["pexels_id"],
            "credit": job["credit"],
            "alt": job["alt"],
        }
    (ROOT / "data" / "photo_credits.json").write_text(
        json.dumps(pri, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
