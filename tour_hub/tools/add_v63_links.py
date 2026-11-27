#!/usr/bin/env python3
"""v63: 신규 가이드 3편으로 들어가는 본문 내부 링크(문맥 링크) 추가.

`related` 배열만으로는 본문 in-degree가 오르지 않아, 기존 가이드 본문에
한 문장씩 링크를 넣는다. 출처 박스(<div class="src">) 앞에 삽입한다.

    python3 tools/add_v63_links.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
G = ROOT / "content" / "guides"

LINKS = {
    "tokyo-food-route": (
        "도쿄 3박4일 동선과 교통·전망대 값은 "
        '<a href="tokyo-3n4d-course-budget.html">도쿄 3박4일 코스·경비</a>에 시간표로 정리했습니다.'
    ),
    "narita-haneda-transfer": (
        "공항 이동을 포함한 3박4일 전체 계산은 "
        '<a href="tokyo-3n4d-course-budget.html">도쿄 3박4일 코스·경비</a>에 있습니다.'
    ),
    "tokyo-package-4d-vs-3d": (
        "패키지 대신 직접 짜는 3박4일과 2인 경비는 "
        '<a href="tokyo-3n4d-course-budget.html">도쿄 3박4일 코스·경비</a>에 정리했습니다.'
    ),
    "entry-immigration-guide": (
        "입국 서류와 별개인 무비자 체류기간은 "
        '<a href="visa-free-stay-duration-guide.html">무비자 체류기간 총정리</a>에서 목적지별로 비교했습니다.'
    ),
    "airport-checkin-customs-guide": (
        "목적지별 무비자 체류일수와 여권 6개월 기준은 "
        '<a href="visa-free-stay-duration-guide.html">무비자 체류기간 총정리</a>에 있습니다.'
    ),
    "passport-application-guide": (
        "여권 유효기간을 며칠 기준으로 보는지는 "
        '<a href="visa-free-stay-duration-guide.html">무비자 체류기간 총정리</a>에 나라별로 정리했습니다.'
    ),
    "japan-rental-car-etc-guide": (
        "동남아에서 같은 국제면허가 인정되는지 여부는 "
        '<a href="southeast-asia-rental-car-license-guide.html">동남아 렌터카·국제면허</a>에서 비교했습니다.'
    ),
    "sea-grab-taxi-scam-guide": (
        "자가운전을 검토한다면 나라별 면허 인정 여부가 먼저입니다. "
        '<a href="southeast-asia-rental-car-license-guide.html">동남아 렌터카·국제면허</a>에 태국·베트남·필리핀·발리 기준을 모았습니다.'
    ),
    "bali-ubud-seminyak-3n4d-course": (
        "발리에서 렌터카를 생각했다면 한국 국제면허가 인정되지 않는다는 점부터 확인하세요. "
        '<a href="southeast-asia-rental-car-license-guide.html">동남아 렌터카·국제면허</a>에 이유와 대안이 있습니다.'
    ),
    "bangkok-3n4d-course": (
        "방콕에서 차를 빌릴 계획이면 면허·보증금 조건을 먼저 보세요. "
        '<a href="southeast-asia-rental-car-license-guide.html">동남아 렌터카·국제면허</a>에 정리했습니다.'
    ),
}


def main() -> int:
    for slug, sentence in LINKS.items():
        p = G / f"{slug}.html"
        if not p.exists():
            print("  ! 없는 파일", slug)
            continue
        html = p.read_text(encoding="utf-8")
        if sentence in html:
            continue
        block = f"<p>{sentence}</p>\n\n"
        idx = html.rfind('<div class="src"')
        if idx == -1:
            idx = html.rfind("<!-- @FAQ -->")
        if idx == -1:
            html = html.rstrip("\n") + "\n\n" + block
        else:
            html = html[:idx] + block + html[idx:]
        p.write_text(html, encoding="utf-8")
        print("  +", slug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
