#!/usr/bin/env python3
"""v69: 기존 가이드 → 신규 3편 역링크(내부 링크) 추가.

    python3 tools/apply_v69_links.py

- japan-rental-car-etc-guide → usa-rental-car-insurance-guide
- southeast-asia-rental-car-license-guide → usa-rental-car-insurance-guide
- us-esta-application-guide → usa-rental-car-insurance-guide
- spain-barcelona-madrid → barcelona-gaudi-montserrat-3n4d-guide
- visa-free-stay-duration-guide → turkey-istanbul-cappadocia-guide
- travel-insurance-guide → usa-rental-car-insurance-guide
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
G = ROOT / "content" / "guides"

LINKS = {
    "japan-rental-car-etc-guide.html": (
        "미국 렌터카",
        '<p>미국에서 직접 운전할 계획이면 <a href="usa-rental-car-insurance-guide.html">미국 렌터카 보험·통행료</a>를 함께 보세요. 같은 국제면허증이라도 미국은 차량 손해(DW)와 대인·대물(SLP)을 나눠 팔고, 통행료를 렌터카 프로그램으로 처리합니다.</p>',
    ),
    "southeast-asia-rental-car-license-guide.html": (
        "미국 렌터카",
        '<p>미국·유럽처럼 보험 상품이 세분화된 곳은 <a href="usa-rental-car-insurance-guide.html">미국 렌터카 보험·통행료 총정리</a>에 DW·SLP·PCE 요금과 주별 통행료를 정리해 두었습니다.</p>',
    ),
    "us-esta-application-guide.html": (
        "미국 렌터카",
        '<p>입국 뒤 차를 빌린다면 <a href="usa-rental-car-insurance-guide.html">미국 렌터카 보험·통행료</a>에서 주별 면허 요건(캘리포니아·플로리다)과 5일 보험료 계산을 확인하세요.</p>',
    ),
    "spain-barcelona-madrid.html": (
        "바르셀로나 3박4일",
        '<p>바르셀로나만 3박4일로 도는 일정이라면 <a href="barcelona-gaudi-montserrat-3n4d-guide.html">바르셀로나 가우디·몬세라트 3박4일</a>에 사그라다·구엘공원·카사 바트요의 공식 예약 요금과 T-Casual 계산을 따로 정리했습니다.</p>',
    ),
    "visa-free-stay-duration-guide.html": (
        "튀르키예",
        '<p>튀르키예 90일 무비자를 실제 일정으로 옮긴 예는 <a href="turkey-istanbul-cappadocia-guide.html">튀르키예 6박7일 이스탄불·카파도키아</a>에 있습니다. 이스탄불카트·뮤지엄패스·열기구 요금까지 함께 계산했습니다.</p>',
    ),
    "travel-insurance-guide.html": (
        "미국 렌터카",
        '<p>미국에서 렌터카를 빌린다면 현지 보험 상품(DW·SLP·PEC)과 국내 여행자보험이 겹치는 범위를 <a href="usa-rental-car-insurance-guide.html">미국 렌터카 보험 총정리</a>에서 확인하세요.</p>',
    ),
}


def main() -> int:
    for name, (_marker, para) in LINKS.items():
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
