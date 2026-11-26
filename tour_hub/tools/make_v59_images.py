#!/usr/bin/env python3
"""v59 이미지 — 신규 가이드 3편 히어로(1200×800+WebP 480/720/960)·OG(1200×630)와
도시 허브 3곳(치앙마이·발리·상하이) 1600×1000·OG.

    python3 tools/make_v59_images.py

가이드 사진은 페셀스 원본, 허브 사진은 기존 v53 도시 사진(같은 도시)을 다시 잘라 씁니다.
"""
from __future__ import annotations

import io
import json
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
V59 = ROOT / "images" / "v59"
OG = ROOT / "images" / "og"
FONT_BOLD = Path("/workspace/tmp_font/Pretendard-Bold.otf")
FONT_NOTO = Path("/usr/share/fonts/pickle-hwp/NotoSansCJKkr-Regular.otf")

GUIDES = [
    {
        "slug": "phu-quoc-3n4d-4n5d-course",
        "pid": 14012627,
        "alt": "푸꾸옥 롱비치의 야자수와 백사장",
        "place": "Phu Quoc, Vietnam",
        "credit": "Quang Nguyen Vinh",
        "og": "v59-phu-quoc-og.jpg",
        "kicker": "트립픽 · 푸꾸옥 3박4일",
        "title": "남부 케이블카 vs 북부 사파리",
        "title2": "케이블카 85만동",
        "sub": "숙소 1박 5만 원대  |  공항 무료 버스  |  무비자 45일",
    },
    {
        "slug": "cebu-3n4d-course",
        "pid": 2403531,
        "alt": "세부 모알보알 바다를 헤엄치는 다이버",
        "place": "Moalboal, Cebu, Philippines",
        "credit": "Elaine Bernadine Castro",
        "og": "v59-cebu-og.jpg",
        "kicker": "트립픽 · 세부 3박4일",
        "title": "막탄 3박 vs 세부시티 2박",
        "title2": "오슬롭 1,000페소",
        "sub": "무비자 30일  |  eTravel 무료  |  MyBus 50페소",
    },
    {
        "slug": "hanoi-halong-3n4d-course",
        "pid": 38003935,
        "alt": "하노이 호안끼엠 호수와 응옥썬 사당",
        "place": "Hanoi, Vietnam",
        "credit": "Valeria Drozdova",
        "og": "v59-hanoi-og.jpg",
        "kicker": "트립픽 · 하노이·하롱베이 3박4일",
        "title": "하롱베이 1박을 넣으면",
        "title2": "하노이가 이틀",
        "sub": "86번 버스 50,000동  |  관람료 250,000동  |  1박 크루즈 550,000동",
    },
]

HUBS = [
    {"slug": "chiangmai", "src": "images/v53/chiang-mai-3n4d-course.jpg",
     "alt": "치앙마이 도이수텝 사원의 금탑과 등불", "credit": "사진: Pexels (Vishal Chokkala)"},
    {"slug": "bali", "src": "images/v53/bali-ubud-seminyak-3n4d-course.jpg",
     "alt": "발리 우붓 논과 전통 가옥의 초록 풍경", "credit": "사진: Pexels (Evelin Magnus)"},
    {"slug": "shanghai", "src": "images/v53/shanghai-2n3d-3n4d-course.jpg",
     "alt": "와이탄에서 바라본 상하이 푸둥의 야경", "credit": "사진: Pexels (YFS Visuals)"},
]


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    for p in (path, FONT_NOTO):
        if p.exists():
            return ImageFont.truetype(str(p), size)
    raise SystemExit(f"폰트를 찾지 못했습니다: {path}")


def fetch(pid: int, w: int = 2400) -> Image.Image:
    url = f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w={w}"
    req = urllib.request.Request(url, headers={"User-Agent": "trippick/5.9 (image fetch)"})
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
    V59.mkdir(parents=True, exist_ok=True)
    im = crop_ratio(fetch(job["pid"]), 1200, 800, 0.5)
    p = V59 / f"{job['slug']}.jpg"
    im.save(p, "JPEG", quality=86, optimize=True, progressive=True)
    for w in (480, 720, 960):
        im.resize((w, round(800 * w / 1200)), Image.LANCZOS).save(
            V59 / f"{job['slug']}-{w}.webp", "WEBP", quality=78, method=6
        )
    return p


def og(job: dict, prefix: str = "v59") -> Path:
    W, H = 1200, 630
    img = crop_ratio(fetch(job["pid"]), W, H, 0.45) if job.get("pid") else crop_ratio(
        Image.open(ROOT / job["src"]), W, H, 0.45)
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
    V59.mkdir(parents=True, exist_ok=True)
    src = Image.open(ROOT / job["src"])
    im = crop_ratio(src, 1600, 1000, 0.42)
    p = V59 / f"{job['slug']}.jpg"
    im.save(p, "JPEG", quality=86, optimize=True, progressive=True)
    for w in (480, 720, 960):
        im.resize((w, round(w / 1.6)), Image.LANCZOS).save(
            V59 / f"{job['slug']}-{w}.webp", "WEBP", quality=80, method=5
        )
    ogi = crop_ratio(src, 1200, 630, 0.42)
    ogi.save(OG / f"v59-{job['slug']}-og.jpg", "JPEG", quality=86, optimize=True, progressive=True)
    return p


def main() -> int:
    pri = json.loads((ROOT / "data" / "photo_credits.json").read_text(encoding="utf-8"))
    for job in GUIDES:
        h = hero(job)
        o = og(job)
        print(f"  · {h.relative_to(ROOT)} {Image.open(h).size} {h.stat().st_size // 1024}KB")
        print(f"  · {o.relative_to(ROOT)} {Image.open(o).size} {o.stat().st_size // 1024}KB")
        pri["photos"][f"v59/{job['slug']}"] = {
            "pexels_id": job["pid"], "place": job["place"], "alt": job["alt"],
            "url": f"https://www.pexels.com/photo/{job['pid']}/", "credit": job["credit"],
        }
    for job in HUBS:
        h = hub(job)
        print(f"  · {h.relative_to(ROOT)} {Image.open(h).size} {h.stat().st_size // 1024}KB")
        pri["photos"][f"v59/{job['slug']}"] = {
            "from": job["src"], "alt": job["alt"], "credit": job["credit"],
        }
    (ROOT / "data" / "photo_credits.json").write_text(
        json.dumps(pri, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
