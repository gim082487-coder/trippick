#!/usr/bin/env python3
"""v25 OG 이미지(1200×630) 생성 — /quiz · /stays 공유 미리보기용.

    python3 tools/make_og_v25.py

실사 사진 위에 어두운 그라데이션과 제목을 얹은 브랜드 카드입니다.
카카오톡·인스타·스레드·X 의 큰 이미지 카드(summary_large_image) 규격에 맞춥니다.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "images" / "og"
FONT_BOLD = Path("/workspace/tmp_font/Pretendard-Bold.otf")
FONT_NOTO = Path("/usr/share/fonts/pickle-hwp/NotoSansCJKkr-Regular.otf")
W, H = 1200, 630

CARDS = [
    {
        "file": "quiz.jpg",
        "photo": "images/courses/hero_kyoto_street.jpg",
        "kicker": "트립픽 · 1분 취향 퀴즈",
        "title": "다섯 가지만 고르면",
        "title2": "내 여행지가 나옵니다",
        "sub": "예산 · 일정 · 동행 · 분위기 · 비행시간  |  13개 도시",
    },
    {
        "file": "stays.jpg",
        "photo": "images/stays/busan-108665692.jpg",
        "kicker": "트립픽 · 찐숙소",
        "title": "국내 24 · 해외 26",
        "title2": "테마별 찐숙소 50곳",
        "sub": "평점 · 리뷰 수 · 1박 최저가  |  트립닷컴 제휴 딥링크",
    },
]


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    for p in (path, FONT_NOTO):
        if p.exists():
            return ImageFont.truetype(str(p), size)
    raise SystemExit(f"폰트를 찾지 못했습니다: {path}")


def build(spec: dict) -> Path:
    src = Image.open(ROOT / spec["photo"]).convert("RGB")
    # 1200×630 비율로 중앙 크롭
    target = W / H
    sw, sh = src.size
    if sw / sh > target:
        nw = int(sh * target)
        src = src.crop(((sw - nw) // 2, 0, (sw + nw) // 2, sh))
    else:
        nh = int(sw / target)
        src = src.crop((0, (sh - nh) // 2, sw, (sh + nh) // 2))
    img = src.resize((W, H), Image.LANCZOS)

    # 왼쪽 아래로 갈수록 어두워지는 그라데이션 (텍스트 가독성)
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(shade)
    for x in range(W):
        a = int(196 * max(0.0, 1 - x / (W * 1.18)))
        d.rectangle([x, 0, x + 1, H], fill=(7, 18, 33, a))
    d.rectangle([0, H - 190, W, H], fill=(7, 18, 33, 120))
    img = Image.alpha_composite(img.convert("RGBA"), shade).convert("RGB")

    draw = ImageDraw.Draw(img)
    f_kick = font(FONT_NOTO, 30)
    f_title = font(FONT_BOLD, 74)
    f_title2 = font(FONT_BOLD, 74)
    f_sub = font(FONT_NOTO, 27)

    x = 68
    y = 168
    draw.text((x, y), spec["kicker"], font=f_kick, fill=(196, 219, 255))
    y += 62
    draw.text((x, y), spec["title"], font=f_title, fill=(255, 255, 255))
    y += 96
    draw.text((x, y), spec["title2"], font=f_title2, fill=(255, 255, 255))
    y += 108
    draw.text((x, y), spec["sub"], font=f_sub, fill=(221, 231, 243))

    # 브랜드 점 + 사이트 주소
    draw.ellipse([x, H - 74, x + 15, H - 59], fill=(27, 92, 240))
    draw.text((x + 26, H - 82), "trippick.pages.dev", font=font(FONT_NOTO, 26), fill=(226, 234, 244))

    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / spec["file"]
    img.save(path, "JPEG", quality=88, optimize=True, progressive=True)
    return path


def main() -> int:
    for spec in CARDS:
        p = build(spec)
        im = Image.open(p)
        print(f"  · {p.relative_to(ROOT)} {im.size[0]}×{im.size[1]} {p.stat().st_size // 1024}KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
