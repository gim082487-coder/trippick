#!/usr/bin/env python3
"""v67 이미지 — 신규 가이드 5편 히어로(1200×800 + WebP 480/720/960)와 OG(1200×630).

    python3 tools/make_v67_images.py

새로 받는 사진 3장은 펙셀스(Pexels License)에서 images/v67_src/로 내려받았고(2026-11-27),
파리·방콕은 사이트가 이미 쓰는 사진을 그대로 쓴다.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
V67 = ROOT / "images" / "v67"
SRC = ROOT / "images" / "v67_src"
OG = ROOT / "images" / "og"
FONT_BOLD = Path("/workspace/tmp_font/Pretendard-Bold.otf")
FONT_NOTO = Path("/usr/share/fonts/pickle-hwp/NotoSansCJKkr-Regular.otf")

GUIDES = [
    {
        "slug": "paris-4n5d-budget",
        "src": "images/v55/paris.jpg",
        "alt": "에펠탑과 파리 시내 전경",
        "credit": "사진: Pexels",
        "og": "v67-paris5-og.jpg",
        "kicker": "트립픽 · 파리 4박5일",
        "title": "둘이 179만 원",
        "title2": "루브르 €32 · 교통 €70",
        "sub": "숙소 4박 79만 612원  |  항공 제외  |  2026.11 조회",
    },
    {
        "slug": "bangkok-3n4d-budget",
        "src": "images/n_bk_p1.jpg",
        "alt": "노을 진 방콕 왕궁과 사원 지붕",
        "credit": "이미지: 판매처",
        "og": "v67-bangkok4-og.jpg",
        "kicker": "트립픽 · 방콕 3박4일",
        "title": "둘이 131만 원",
        "title2": "사원 1,000밧 · eSIM 2인",
        "sub": "항공 2인 70만  |  숙소 3박 32만 5,833  |  2026.11 조회",
    },
    {
        "slug": "phuket-3n4d-budget",
        "pexels": 29437727,
        "alt": "푸껫 해변과 맑은 바다",
        "credit": "사진: Pexels (Fernando B M)",
        "og": "v67-phuket-og.jpg",
        "kicker": "트립픽 · 푸껫 3박4일",
        "title": "버스 100밧",
        "title2": "피피섬 1,450밧",
        "sub": "공원 입장 400밧 별도  |  숙소 3박 18만~91만  |  2026.11 조회",
    },
    {
        "slug": "rome-south-italy-daytrip-guide",
        "pexels": 10436112,
        "alt": "포지타노의 형형색색 건물과 아말피 해안",
        "credit": "사진: Pexels (Greta Soave)",
        "og": "v67-southitaly-og.jpg",
        "kicker": "트립픽 · 이탈리아 남부",
        "title": "폼페이 기차 €3.30",
        "title2": "폼페이 €20 / €25",
        "sub": "카프리 페리 €14.80~  |  2인 반나절 15만 원  |  2026.11 확인",
    },
    {
        "slug": "osaka-kobe-nara-daytrip-guide",
        "pexels": 35317275,
        "alt": "고베 항구와 포트타워",
        "credit": "사진: Pexels (Dmitry Romanoff)",
        "og": "v67-kobenara-og.jpg",
        "kicker": "트립픽 · 오사카 근교",
        "title": "고베 330엔",
        "title2": "나라 680엔",
        "sub": "도다이지 800엔  |  시티루프 1일 800엔  |  2026.11 확인",
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
    return SRC / f"pexels-{job['pexels']}.jpg" if job.get("pexels") else ROOT / job["src"]


def hero(job: dict) -> Path:
    V67.mkdir(parents=True, exist_ok=True)
    im = crop_ratio(Image.open(src_path(job)), 1200, 800, 0.45)
    p = V67 / f"{job['slug']}.jpg"
    im.save(p, "JPEG", quality=86, optimize=True, progressive=True)
    for w in (480, 720, 960):
        im.resize((w, round(800 * w / 1200)), Image.LANCZOS).save(
            V67 / f"{job['slug']}-{w}.webp", "WEBP", quality=78, method=6
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
        entry = {"credit": job["credit"], "alt": job["alt"]}
        if job.get("pexels"):
            entry["source"] = "Pexels (Pexels License — 무료 상업적 사용)"
            entry["from"] = f"images/v67_src/pexels-{job['pexels']}.jpg"
            entry["url"] = f"https://www.pexels.com/photo/{job['pexels']}/"
        else:
            entry["source"] = "기존 트립픽 사용 이미지(펙셀스 라이선스·보유 이미지)"
            entry["from"] = job["src"]
        pri["photos"][f"v67/{job['slug']}"] = entry
    (ROOT / "data" / "photo_credits.json").write_text(
        json.dumps(pri, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
