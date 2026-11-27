#!/usr/bin/env python3
"""v65 이미지 — 신규 가이드 8편 히어로(1200×800 + WebP 480/720/960)와 OG(1200×630).

    python3 tools/make_v65_images.py

사이트가 이미 쓰는 실제 사진(펙셀스·보유 이미지)을 소스로 재사용한다.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
V65 = ROOT / "images" / "v65"
OG = ROOT / "images" / "og"
FONT_BOLD = Path("/workspace/tmp_font/Pretendard-Bold.otf")
FONT_NOTO = Path("/usr/share/fonts/pickle-hwp/NotoSansCJKkr-Regular.otf")

GUIDES = [
    {
        "slug": "london-transport-heathrow-guide",
        "src": "images/v55/london.jpg",
        "alt": "템스강 위 런던 타워 브리지",
        "credit": "사진: Pexels",
        "og": "v65-london-og.jpg",
        "kicker": "트립픽 · 런던 교통",
        "title": "피카딜리 £5.90",
        "title2": "엘리자베스 £15.50",
        "sub": "히드로익스프레스 £26  |  상한 £8.90  |  2인 3일 16만 원",
    },
    {
        "slug": "rome-vatican-colosseum-booking-guide",
        "src": "images/v55/rome.jpg",
        "alt": "로마 콜로세움과 포로 로마노",
        "credit": "사진: Pexels",
        "og": "v65-rome-og.jpg",
        "kicker": "트립픽 · 로마 예약",
        "title": "바티칸 온라인 €25",
        "title2": "콜로세움 €18",
        "sub": "공항 기차 €14  |  로마패스 €38/62.90  |  2인 30만 원",
    },
    {
        "slug": "taiwan-transport-thsr-guide",
        "src": "images/v45/taipei-3n4d.jpg",
        "alt": "타이베이 101과 도심 스카이라인",
        "credit": "사진: 트립픽 보유 이미지(2026)",
        "og": "v65-taiwan-og.jpg",
        "kicker": "트립픽 · 대만 교통",
        "title": "공항 MRT NT$160",
        "title2": "THSR 3일권 2,200",
        "sub": "이지카드 NT$100  |  72시간 380  |  타이난 왕복이면 이득",
    },
    {
        "slug": "cebu-bohol-ferry-transfer-guide",
        "src": "images/v59/cebu-3n4d-course.jpg",
        "alt": "세부 막탄 해변과 리조트",
        "credit": "사진: Pexels (Elaine Bernadine Castro)",
        "og": "v65-cebu-og.jpg",
        "kicker": "트립픽 · 세부·보홀",
        "title": "오션젯 960페소",
        "title2": "2시간·하루 10편",
        "sub": "터미널료 25페소  |  수하물 10kg  |  문에서 문 4시간",
    },
    {
        "slug": "kyoto-2n3d-course-budget",
        "src": "images/courses/hero_kyoto_street.jpg",
        "alt": "교토 기온의 전통 거리",
        "credit": "사진: 트립픽 보유 이미지(2026)",
        "og": "v65-kyoto-og.jpg",
        "kicker": "트립픽 · 교토 2박3일",
        "title": "1일권 1,100엔",
        "title2": "버스 5회면 본전",
        "sub": "지하철 800엔  |  청수사 500엔  |  2인 12만 8천 원",
    },
    {
        "slug": "hongkong-octopus-ael-guide",
        "src": "images/v55/hongkong.jpg",
        "alt": "홍콩 빅토리아 하버 야경",
        "credit": "사진: Pexels",
        "og": "v65-hongkong-og.jpg",
        "kicker": "트립픽 · 홍콩 교통",
        "title": "AEL HK$120",
        "title2": "2인 그룹 HK$170",
        "sub": "A21 HK$34.6  |  옥토퍼스 HK$150  |  2인 16만 원",
    },
    {
        "slug": "vietnam-4cities-comparison-guide",
        "src": "images/v59/phu-quoc-3n4d-4n5d-course.jpg",
        "alt": "푸꾸옥 해변과 리조트",
        "credit": "사진: Pexels (Quang Nguyen Vinh)",
        "og": "v65-vietnam-og.jpg",
        "kicker": "트립픽 · 베트남 4도시",
        "title": "12월은 푸꾸옥",
        "title2": "8월은 나트랑",
        "sub": "우기 달력 3개  |  공항버스 50,000동  |  숙소 5.5만 원~",
    },
    {
        "slug": "thailand-cities-comparison-guide",
        "src": "images/v56/bangkok-3n4d-course.jpg",
        "alt": "방콕 왓아룬과 짜오프라야강",
        "credit": "사진: Pexels (Meaw Zara)",
        "og": "v65-thailand-og.jpg",
        "kicker": "트립픽 · 태국 4도시",
        "title": "9월 방콕 336mm",
        "title2": "12월은 네 도시 건기",
        "sub": "공항철도 45밧  |  치앙마이 150밧  |  숙소 2.3만 원~",
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
    V65.mkdir(parents=True, exist_ok=True)
    im = crop_ratio(Image.open(ROOT / job["src"]), 1200, 800, 0.45)
    p = V65 / f"{job['slug']}.jpg"
    im.save(p, "JPEG", quality=86, optimize=True, progressive=True)
    for w in (480, 720, 960):
        im.resize((w, round(800 * w / 1200)), Image.LANCZOS).save(
            V65 / f"{job['slug']}-{w}.webp", "WEBP", quality=78, method=6
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
    draw.text((x, y), job["title"], font=font(FONT_BOLD, 64), fill=(255, 255, 255))
    y += 88
    draw.text((x, y), job["title2"], font=font(FONT_BOLD, 64), fill=(255, 255, 255))
    y += 100
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
        pri["photos"][f"v65/{job['slug']}"] = {
            "source": "기존 트립픽 사용 이미지(펙셀스 라이선스·보유 이미지)",
            "from": job["src"],
            "credit": job["credit"],
            "alt": job["alt"],
        }
    (ROOT / "data" / "photo_credits.json").write_text(
        json.dumps(pri, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
