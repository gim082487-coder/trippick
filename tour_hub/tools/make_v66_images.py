#!/usr/bin/env python3
"""v66 이미지 — 신규 가이드 12편 히어로(1200×800 + WebP 480/720/960)와 OG(1200×630).

    python3 tools/make_v66_images.py

새로 받는 사진 5장은 펙셀스(Pexels License)에서 images/v66_src/로 내려받고,
나머지는 사이트가 이미 쓰는 사진을 그대로 쓴다.
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
V66 = ROOT / "images" / "v66"
SRC = ROOT / "images" / "v66_src"
OG = ROOT / "images" / "og"
FONT_BOLD = Path("/workspace/tmp_font/Pretendard-Bold.otf")
FONT_NOTO = Path("/usr/share/fonts/pickle-hwp/NotoSansCJKkr-Regular.otf")

# slug, 펙셀스 id(새로 받을 때), 기존 이미지(재사용), alt, credit, OG 파일, kicker, 제목 2줄, sub
GUIDES = [
    {
        "slug": "la-las-vegas-grand-canyon-course",
        "pexels": 34921087,
        "alt": "그랜드캐니언 사우스림의 협곡",
        "credit": "사진: Pexels (Rino Adamo)",
        "og": "v66-lasvegas-og.jpg",
        "kicker": "트립픽 · 미서부 6박7일",
        "title": "그랜드캐니언 $35+$100",
        "title2": "라스베이거스 리조트피 $51",
        "sub": "유니버설 $99.95  |  LA 메트로 상한 $5  |  2인 268만 원",
    },
    {
        "slug": "london-4n5d-course-budget",
        "src": "images/v55/london.jpg",
        "alt": "템스강과 런던 시내",
        "credit": "사진: Pexels",
        "og": "v66-london5-og.jpg",
        "kicker": "트립픽 · 런던 4박5일",
        "title": "무료 박물관 2곳",
        "title2": "옥스퍼드 £37.70",
        "sub": "뮤지컬 £21부터  |  지하철 상한 £8.90  |  2인 190만 원",
    },
    {
        "slug": "dubai-stopover-3n4d-guide",
        "pexels": 35791378,
        "alt": "두바이 스카이라인과 부르즈 할리파",
        "credit": "사진: Pexels (San Photography)",
        "og": "v66-dubai-og.jpg",
        "kicker": "트립픽 · 두바이 3박4일",
        "title": "무비자 90일",
        "title2": "부르즈 AED 189",
        "sub": "사파리 AED 99~  |  놀 카드 25  |  2인 60만 원",
    },
    {
        "slug": "melbourne-sydney-6n7d-guide",
        "pexels": 29813638,
        "alt": "멜버른 스카이라인과 야라강",
        "credit": "사진: Pexels (Harry Tucker)",
        "og": "v66-melbourne-og.jpg",
        "kicker": "트립픽 · 멜버른·시드니",
        "title": "오션로드 $107",
        "title2": "펭귄퍼레이드 $34",
        "sub": "스카이버스 $25.90  |  오팔 $19.30  |  2인 243만 원",
    },
    {
        "slug": "japan-small-cities-comparison",
        "src": "images/v60/beppu-onsen-1n2d-course.jpg",
        "alt": "일본 온천 소도시의 거리",
        "credit": "사진: 트립픽 보유 이미지(2026)",
        "og": "v66-smallcities-og.jpg",
        "kicker": "트립픽 · 일본 소도시",
        "title": "공항버스 1,000~1,500엔",
        "title2": "직항 5곳 비교",
        "sub": "다카마쓰·마쓰야마·시즈오카·구마모토·가고시마",
    },
    {
        "slug": "okinawa-rental-car-bus-guide",
        "src": "images/v56/okinawa.jpg",
        "alt": "오키나와 해안 도로와 바다",
        "credit": "사진: Pexels",
        "og": "v66-okinawacar-og.jpg",
        "kicker": "트립픽 · 오키나와 교통",
        "title": "렌터카 24시간 6,600엔",
        "title2": "유이레일 1일권 1,000엔",
        "sub": "ETC 1,040엔  |  현금 1,610엔  |  2인 3박4일 13만 원~",
    },
    {
        "slug": "europe-night-train-ryanair-guide",
        "src": "images/v37/tgv.jpg",
        "alt": "유럽 고속열차 TGV",
        "credit": "사진: 트립픽 보유 이미지(2026)",
        "og": "v66-railtrain-og.jpg",
        "kicker": "트립픽 · 유럽 이동",
        "title": "20kg £21.49부터",
        "title2": "유로스타 £39",
        "sub": "TGV €39  |  이탈로 €19~  |  3시간 이내는 열차",
    },
    {
        "slug": "travel-adapter-voltage-world-guide",
        "pexels": 3639031,
        "alt": "국가별 전원 플러그와 어댑터",
        "credit": "사진: Pexels (Castorly Stock)",
        "og": "v66-adapter-og.jpg",
        "kicker": "트립픽 · 전압·어댑터",
        "title": "220V C/F · 100V A/B",
        "title2": "100–240V면 어댑터만",
        "sub": "드라이기 1,600W  |  120V에서 13.3A  |  어댑터 12,900원",
    },
    {
        "slug": "bali-driver-nusa-penida-guide",
        "src": "images/v59/bali.jpg",
        "alt": "발리 해안과 사원",
        "credit": "사진: Pexels",
        "og": "v66-balicar-og.jpg",
        "kicker": "트립픽 · 발리 이동",
        "title": "기사 하루 55만 루피아",
        "title2": "누사페니다 45분",
        "sub": "그랩 2만~4만  |  배 17만~21만 5천  |  섬 입장 2만 5천",
    },
    {
        "slug": "fukuoka-hakata-tenjin-shopping-guide",
        "src": "images/v52/fukuoka-yufuin-3n4d-course.jpg",
        "alt": "후쿠오카·유후인 여행지 풍경",
        "credit": "사진: 트립픽 보유 이미지(2026)",
        "og": "v66-fukuokashop-og.jpg",
        "kicker": "트립픽 · 후쿠오카 쇼핑",
        "title": "하카타 락커 1,000엔",
        "title2": "토스 버스 280엔",
        "sub": "텐진 10~20시  |  캐널 10~21시  |  면세 5,000엔",
    },
    {
        "slug": "malaysia-kuala-lumpur-2n3d-guide",
        "pexels": 1324500,
        "alt": "쿠알라룸푸르 페트로나스 트윈타워",
        "credit": "사진: Pexels (Humphrey Muleba)",
        "og": "v66-kl-og.jpg",
        "kicker": "트립픽 · 쿠알라룸푸르",
        "title": "KLIA RM55·28분",
        "title2": "바투 KTM RM2.60",
        "sub": "페트로나스 127  |  관광세 10  |  2인 28만 원",
    },
    {
        "slug": "hawaii-island-hopping-guide",
        "src": "images/v54/hawaii-oahu-5n7d-course.jpg",
        "alt": "하와이 해변과 화산 지형",
        "credit": "사진: Pexels",
        "og": "v66-hawaiiisland-og.jpg",
        "kicker": "트립픽 · 하와이 섬",
        "title": "주내선 $49부터",
        "title2": "렌터카 $42~60",
        "sub": "할레아칼라 $30+$1  |  화산 $30  |  2인 386만 원",
    },
]


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def fetch(pid: int, w: int = 2000) -> Path:
    SRC.mkdir(parents=True, exist_ok=True)
    p = SRC / f"pexels-{pid}.jpg"
    if p.exists() and p.stat().st_size > 50_000:
        return p
    url = f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w={w}"
    req = urllib.request.Request(url, headers={"User-Agent": "trippick/6.6 (image fetch)"})
    with urllib.request.urlopen(req, timeout=90) as r:
        p.write_bytes(r.read())
    return p


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
    V66.mkdir(parents=True, exist_ok=True)
    src = fetch(job["pexels"]) if job.get("pexels") else ROOT / job["src"]
    im = crop_ratio(Image.open(src), 1200, 800, 0.45)
    p = V66 / f"{job['slug']}.jpg"
    im.save(p, "JPEG", quality=86, optimize=True, progressive=True)
    for w in (480, 720, 960):
        im.resize((w, round(800 * w / 1200)), Image.LANCZOS).save(
            V66 / f"{job['slug']}-{w}.webp", "WEBP", quality=78, method=6
        )
    return p


def og(job: dict) -> Path:
    W, H = 1200, 630
    src = SRC / f"pexels-{job['pexels']}.jpg" if job.get("pexels") else ROOT / job["src"]
    img = crop_ratio(Image.open(src), W, H, 0.42)
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
        entry = {
            "credit": job["credit"],
            "alt": job["alt"],
        }
        if job.get("pexels"):
            entry["source"] = "Pexels (Pexels License — 무료 상업적 사용)"
            entry["from"] = f"images/v66_src/pexels-{job['pexels']}.jpg"
            entry["url"] = f"https://www.pexels.com/photo/{job['pexels']}/"
        else:
            entry["source"] = "기존 트립픽 사용 이미지(펙셀스 라이선스·보유 이미지)"
            entry["from"] = job["src"]
        pri["photos"][f"v66/{job['slug']}"] = entry
    (ROOT / "data" / "photo_credits.json").write_text(
        json.dumps(pri, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
