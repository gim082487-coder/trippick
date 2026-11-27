#!/usr/bin/env python3
"""v64 이미지 — 신규 가이드 8편 히어로(1200×800+WebP 480/720/960)·OG(1200×630).

    python3 tools/make_v64_images.py

사진은 사이트에서 쓰는 실제 사진(펙셀스·위키미디어)을 소스로 쓴다.
new-york·nagoya·japan-restaurant 3장은 images/v64_src/ 에 내려받아 두었다.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
V64 = ROOT / "images" / "v64"
OG = ROOT / "images" / "og"
FONT_BOLD = Path("/workspace/tmp_font/Pretendard-Bold.otf")
FONT_NOTO = Path("/usr/share/fonts/pickle-hwp/NotoSansCJKkr-Regular.otf")

GUIDES = [
    {
        "slug": "us-esta-application-guide",
        "src": "images/v33/passport-application.jpg",
        "alt": "여권 스탬프가 찍힌 여권 면을 손에 든 모습",
        "credit": "사진: Ekaterina Belinskaya / Pexels",
        "pexels_id": 4922086,
        "og": "v64-esta-og.jpg",
        "kicker": "트립픽 · 미국 ESTA",
        "title": "수수료 $40.62",
        "title2": "72시간을 비워 두세요",
        "sub": "2년 유효  |  90일 체류  |  공식 사이트 한 곳",
    },
    {
        "slug": "uk-eta-application-guide",
        "src": "images/v55/london.jpg",
        "alt": "템스강 위 런던 타워 브리지",
        "credit": "사진: David Pickup / Pexels",
        "pexels_id": 10771574,
        "og": "v64-eta-og.jpg",
        "kicker": "트립픽 · 영국 ETA",
        "title": "£20 · 2년 유효",
        "title2": "한국은 2025년 1월부터",
        "sub": "1회 6개월  |  승인 1일~3영업일  |  landside 환승 주의",
    },
    {
        "slug": "kansai-airport-osaka-kyoto-transfer",
        "src": "images/v43/airport-transfer.jpg",
        "alt": "간사이국제공항 철도역 승강장",
        "credit": "사진: Wikimedia Commons (CC0)",
        "pexels_id": None,
        "og": "v64-kix-og.jpg",
        "kicker": "트립픽 · 간사이공항",
        "title": "난바 970엔",
        "title2": "교토 2,700엔",
        "sub": "라피트 1,410엔~  |  리무진 1,400~2,800엔  |  막차 23:55",
    },
    {
        "slug": "new-york-4n5d-course-budget",
        "src": "images/v64_src/new-york.jpg",
        "alt": "맨해튼 스카이라인과 엠파이어스테이트빌딩",
        "credit": "사진: Craig Adderley / Pexels",
        "pexels_id": 6716427,
        "og": "v64-nyc-og.jpg",
        "kicker": "트립픽 · 뉴욕 4박5일",
        "title": "AirTrain $11.75",
        "title2": "전망대는 하나만",
        "sub": "지하철 $3.00  |  7일 상한 $35  |  2인 173만 원",
    },
    {
        "slug": "nagoya-3n4d-course-budget",
        "src": "images/v64_src/nagoya.jpg",
        "alt": "푸른 하늘 아래 나고야성",
        "credit": "사진: Alen Joe Chacko / Pexels",
        "pexels_id": 40050536,
        "og": "v64-nagoya-og.jpg",
        "kicker": "트립픽 · 나고야 3박4일",
        "title": "지브리파크 3,300엔",
        "title2": "센트레아 1,430엔",
        "sub": "2개월 전 예약  |  시라카와고 3,600~4,700엔  |  2인 58만 원",
    },
    {
        "slug": "japan-restaurant-reservation-guide",
        "src": "images/v64_src/japan-restaurant.jpg",
        "alt": "도쿄 스시집에서 초밥을 만드는 셰프",
        "credit": "사진: Lawrence Lam / Pexels",
        "pexels_id": 34002084,
        "og": "v64-restaurant-og.jpg",
        "kicker": "트립픽 · 일본 식당 예약",
        "title": "예약 수수료 390~440엔",
        "title2": "노쇼는 코스 값 100%",
        "sub": "타베로그 440엔  |  OMAKASE 390엔  |  전화 문장 6개",
    },
    {
        "slug": "macau-1n2d-ferry-bus-guide",
        "src": "images/v55/macau.jpg",
        "alt": "마카오 세나도 광장의 물결 무늬 보도",
        "credit": "사진: Guillaume Kremer / Pexels",
        "pexels_id": 38783880,
        "og": "v64-macau-og.jpg",
        "kicker": "트립픽 · 마카오 1박2일",
        "title": "페리 HK$194",
        "title2": "금바 HK$65",
        "sub": "60~70분 vs 35~40분  |  버스 MOP6  |  2인 15만~24만 원",
    },
    {
        "slug": "paris-metro-navigo-guide",
        "src": "images/v55/paris.jpg",
        "alt": "에펠탑과 파리 시내가 보이는 드론 항공샷",
        "credit": "사진: Mo Eid / Pexels",
        "pexels_id": 18411385,
        "og": "v64-paris-og.jpg",
        "kicker": "트립픽 · 파리 교통권",
        "title": "1회 €2.55",
        "title2": "공항 €14 · 주간 €32.40",
        "sub": "종이 티켓 폐지  |  나비고 이지 €2  |  2인 17만 6천 원",
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
    V64.mkdir(parents=True, exist_ok=True)
    im = crop_ratio(Image.open(ROOT / job["src"]), 1200, 800, 0.45)
    p = V64 / f"{job['slug']}.jpg"
    im.save(p, "JPEG", quality=86, optimize=True, progressive=True)
    for w in (480, 720, 960):
        im.resize((w, round(800 * w / 1200)), Image.LANCZOS).save(
            V64 / f"{job['slug']}-{w}.webp", "WEBP", quality=78, method=6
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
    draw.text((x, y), job["title2"], font=font(FONT_BOLD, 68), fill=(255, 255, 255))
    y += 104
    draw.text((x, y), job["sub"], font=font(FONT_NOTO, 25), fill=(221, 231, 243))
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
        pri["photos"][f"v64/{job['slug']}"] = {
            "source": "Pexels (Pexels License — 무료 상업적 사용)" if job["pexels_id"] else "Wikimedia Commons (CC0)",
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
