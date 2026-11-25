#!/usr/bin/env python3
"""v54 이미지 — 펙셀스 원본 → 히어로 1200×800(+WebP 480/720/960) · OG 1200×630.

    python3 tools/make_v54_images.py
"""
from __future__ import annotations

import io
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
V54 = ROOT / "images" / "v54"
OG = ROOT / "images" / "og"
FONT_BOLD = Path("/workspace/tmp_font/Pretendard-Bold.otf")
FONT_NOTO = Path("/usr/share/fonts/pickle-hwp/NotoSansCJKkr-Regular.otf")

JOBS = [
    {
        "slug": "japan-mounjaro-injection-guide",
        "pid": 7653660,
        "og": "v54-mounjaro-og.jpg",
        "kicker": "트립픽 · 준비물",
        "title": "마운자로 들고 일본 가기",
        "title2": "1개월분 · 기내 · 보관",
        "sub": "4펜은 서류 면제  |  초과 시 수입확인증  |  귀국 12펜",
    },
    {
        "slug": "guam-4n5d-course",
        "pid": 24033245,
        "og": "v54-guam-og.jpg",
        "kicker": "트립픽 · 괌 4박5일",
        "title": "투몬 4박 + 남부 드라이브",
        "title2": "2인 161만 원",
        "sub": "공항 택시 7.20달러  |  렌터카 45달러  |  피시아이 66달러",
    },
    {
        "slug": "hawaii-oahu-5n7d-course",
        "pid": 36072131,
        "og": "v54-hawaii-og.jpg",
        "kicker": "트립픽 · 하와이 5박7일",
        "title": "예약 3곳이 일정을 정한다",
        "title2": "2인 288만 원",
        "sub": "다이아몬드헤드 5달러  |  하나우마 25달러  |  HOLO 45달러",
    },
]


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    for p in (path, FONT_NOTO):
        if p.exists():
            return ImageFont.truetype(str(p), size)
    raise SystemExit(f"폰트를 찾지 못했습니다: {path}")


def fetch(pid: int, w: int = 2000) -> Image.Image:
    url = f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w={w}"
    req = urllib.request.Request(url, headers={"User-Agent": "trippick/5.4 (image fetch)"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return Image.open(io.BytesIO(r.read()))


def crop_ratio(im: Image.Image, tw: int, th: int) -> Image.Image:
    im = ImageOps.exif_transpose(im).convert("RGB")
    target = tw / th
    sw, sh = im.size
    if sw / sh > target:
        nw = int(sh * target)
        im = im.crop(((sw - nw) // 2, 0, (sw + nw) // 2, sh))
    else:
        nh = int(sw / target)
        im = im.crop((0, (sh - nh) // 2, sw, (sh + nh) // 2))
    return im.resize((tw, th), Image.LANCZOS)


def hero(job: dict) -> Path:
    V54.mkdir(parents=True, exist_ok=True)
    im = crop_ratio(fetch(job["pid"]), 1200, 800)
    p = V54 / f"{job['slug']}.jpg"
    im.save(p, "JPEG", quality=86, optimize=True, progressive=True)
    for w in (480, 720, 960):
        im.resize((w, round(800 * w / 1200)), Image.LANCZOS).save(
            V54 / f"{job['slug']}-{w}.webp", "WEBP", quality=78, method=6
        )
    return p


def og(job: dict) -> Path:
    W, H = 1200, 630
    img = crop_ratio(fetch(job["pid"]), W, H)
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
    draw.text((x, y), job["title"], font=font(FONT_BOLD, 72), fill=(255, 255, 255))
    y += 96
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
    for job in JOBS:
        h = hero(job)
        o = og(job)
        im = Image.open(h)
        print(f"  · {h.relative_to(ROOT)} {im.size[0]}×{im.size[1]} {h.stat().st_size // 1024}KB")
        oi = Image.open(o)
        print(f"  · {o.relative_to(ROOT)} {oi.size[0]}×{oi.size[1]} {o.stat().st_size // 1024}KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
