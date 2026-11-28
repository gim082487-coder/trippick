#!/usr/bin/env python3
"""v70: 기존 가이드 → 신규 2편 역링크(내부 링크) 추가.

    python3 tools/apply_v70_links.py

- japan-mounjaro-injection-guide → japan-mounjaro-travel-destinations
- kyoto-2n3d-course-budget → japan-mounjaro-travel-destinations
- fukuoka-yufuin-3n4d-course → japan-mounjaro-travel-destinations
- sapporo-hokkaido-3n4d-winter → japan-mounjaro-travel-destinations
- incheon-yeongjongdo-2d → daebudo-daytrip-1n2d-course
- gangwon-gangneung-winter-sea-2d → daebudo-daytrip-1n2d-course
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
G = ROOT / "content" / "guides"

LINKS = {
    "japan-mounjaro-injection-guide.html": (
        '<p>어느 도시로 갈지 정하는 단계라면 <a href="japan-mounjaro-travel-destinations.html">마운자로 일본 여행지 TOP 4</a>를 함께 보세요. '
        '공항에서 숙소까지 걸리는 시간(후쿠오카 5분·삿포로 33분·도쿄 41분·교토 80분)과 숙소 냉장고, '
        '규동 小盛 465엔 같은 소식 메뉴까지 도시별로 비교했습니다.</p>'
    ),
    "kyoto-2n3d-course-budget.html": (
        '<p>복용 중인 자가주사제를 들고 교토에 오는 일정이라면 <a href="japan-mounjaro-travel-destinations.html">마운자로 일본 여행지 TOP 4</a>에 '
        '하루카 2,700엔, 사찰 요금, 아라시야마 후후노유 1,100엔과 냉장 보관 기준을 정리해 두었습니다.</p>'
    ),
    "fukuoka-yufuin-3n4d-course.html": (
        '<p>약을 들고 다니는 일정이라면 <a href="japan-mounjaro-travel-destinations.html">마운자로 일본 여행지 TOP 4</a>에서 '
        '후쿠오카 공항→하카타 5분·260엔과 숙소 냉장고, 단품 식사 기준을 확인하세요.</p>'
    ),
    "sapporo-hokkaido-3n4d-winter.html": (
        '<p>조잔케이 료칸과 시내 호텔을 견줘 보려면 <a href="japan-mounjaro-travel-destinations.html">마운자로 일본 여행지 TOP 4</a>를 보세요. '
        '료칸 1박 694,357원 vs 시내 87,205원 + 당일 온천 57,948원 계산이 들어 있습니다.</p>'
    ),
    "incheon-yeongjongdo-2d.html": (
        '<p>바다 쪽으로 하루 더 움직인다면 <a href="daebudo-daytrip-1n2d-course.html">대부도 당일치기·1박2일</a>에 '
        '탄도항 물때, 시화나래 달전망대(무료·10:00~20:00), 해솔길 1코스 11.5km를 정리해 두었습니다.</p>'
    ),
    "gangwon-gangneung-winter-sea-2d.html": (
        '<p>수도권에서 당일로 바다를 보려면 <a href="daebudo-daytrip-1n2d-course.html">대부도 당일치기·1박2일</a>이 가깝습니다. '
        '버스 1,650원, 입장료 무료 3곳, 2인 확정 지출 10,600원입니다.</p>'
    ),
}


def main() -> int:
    for name, para in LINKS.items():
        p = G / name
        html = p.read_text(encoding="utf-8")
        href = para.split('href="', 1)[1].split('"', 1)[0]
        if href in html:
            print(f"  · {name} 이미 연결됨")
            continue
        if "<!-- @FAQ -->" in html:
            html = html.replace("<!-- @FAQ -->", para + "\n\n<!-- @FAQ -->", 1)
        else:
            html = html.rstrip("\n") + "\n\n" + para + "\n"
        p.write_text(html, encoding="utf-8")
        print(f"  · {name} 역링크 추가")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
