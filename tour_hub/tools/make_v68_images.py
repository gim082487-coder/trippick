#!/usr/bin/env python3
"""v68 이미지 — 신규 가이드 3편 히어로(1200×800 + WebP 480/720/960)와 OG(1200×630).

    python3 tools/make_v68_images.py

새로 받는 사진 3장은 펙셀스(Pexels License)에서 images/v68_src/로 내려받았고(2026-11-28),
세 장 모두 새로 받았다.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
V67 = ROOT / "images" / "v68"
SRC = ROOT / "images" / "v68_src"
OG = ROOT / "images" / "og"
FONT_BOLD = Path("/workspace/tmp_font/Pretendard-Bold.otf")
FONT_NOTO = Path("/usr/share/fonts/pickle-hwp/NotoSansCJKkr-Regular.otf")

GUIDES = [
    {
        "slug": "china-visa-free-alipay-wechat-pay-guide",
        "pexels": 20119848,
        "alt": "네온이 켜진 상하이 거리 야경",
        "credit": "사진: Pexels (Wilbur Ludlow)",
        "og": "v68-china-pay-og.jpg",
        "kicker": "트립픽 · 중국 무비자·결제",
        "title": "무비자 30일",
        "title2": "알리페이 3% 기준",
        "sub": "200위안 이하 수수료 0  |  2026.12.31까지  |  2026.11 확인",
    },
    {
        "slug": "boracay-3n4d-course-budget",
        "pexels": 38525284,
        "alt": "보라카이 화이트 비치의 백사장과 청록색 바다",
        "credit": "사진: Pexels (Jeffrey Ligan)",
        "og": "v68-boracay-og.jpg",
        "kicker": "트립픽 · 보라카이 3박4일",
        "title": "제티 500페소",
        "title2": "2인 39만~79만",
        "sub": "환경세 300페소  |  호핑 현장 750페소  |  2026.11 조회",
    },
    {
        "slug": "saipan-3n4d-course-budget",
        "pexels": 2494133,
        "alt": "사이판 해변의 야자수와 노을",
        "credit": "사진: Pexels (Rommell Buenaflor)",
        "og": "v68-saipan-og.jpg",
        "kicker": "트립픽 · 사이판 3박4일",
        "title": "ETA 무료",
        "title2": "마나가하 63달러",
        "sub": "2인 128만~157만  |  렌터카 50~80달러  |  2026.11 조회",
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
            entry["from"] = f"images/v68_src/pexels-{job['pexels']}.jpg"
            entry["url"] = f"https://www.pexels.com/photo/{job['pexels']}/"
        else:
            entry["source"] = "기존 트립픽 사용 이미지(펙셀스 라이선스·보유 이미지)"
            entry["from"] = job["src"]
        pri["photos"][f"v68/{job['slug']}"] = entry
    (ROOT / "data" / "photo_credits.json").write_text(
        json.dumps(pri, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
