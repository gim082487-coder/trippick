#!/usr/bin/env python3
"""v69: 신규 가이드 3편 메타데이터(guides.json·guide_extra.json).

    python3 tools/apply_v69_guides.py

값은 2026-11-28 확인분이다.
- 미국 렌터카: 국제면허 9,000원·1년, DW $26.99~49.99, SLP $8.44~42.38, PEC $5.99~15.67,
  PAI $2.68~8.50, SunPass Toll-by-Plate $2.50, Golden Gate $10.25/10.50/11.25,
  MTA 혼잡통행료 $9/$2.25(E-ZPass), PlatePass FL $9.99/$14.99, Enterprise TollPass $4.95,
  AAA 전국 평균 $3.5476/갤런(2026-11-27)
- 바르셀로나: 사그라다 26/36/40유로, 구엘 18유로(7~12세 13.50), 카사 바트요 29유로~,
  T-Casual 13유로, 단권 2.90, 공항 지하철 5.90, Aerobús 7.75/13.30,
  몬세라트 Trans 50·Tot 71.50·산악철도 15유로 왕복
- 튀르키예: 무비자 180일 중 90일, 이스탄불카트 165리라+46.20리라, Havaist 470리라,
  하기아 소피아 25유로, 톱카프 2,750리라, 갈라타 30유로, 뮤지엄패스 105유로,
  괴레메 20유로+암흑교회 6유로, 열기구 260/160유로, 그린투어 50~65유로
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"


def load(n):
    return json.loads((D / n).read_text(encoding="utf-8"))


def save(n, o):
    (D / n).write_text(json.dumps(o, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


NEW = [
    {
        "slug": "usa-rental-car-insurance-guide",
        "category": "준비물·경비",
        "navTitle": "미국 렌터카 보험 — DW·SLP·통행료까지, 5일 60만 원",
        "h1": "미국 렌터카, <em>차값보다 보험</em>이 큽니다",
        "seoTitle": "미국 렌터카 보험·통행료 총정리 — SLP·SunPass (2026) | 트립픽",
        "dek": ("미국 렌터카는 하루 $39 요금표에 보험과 통행료가 붙어 5일 60만 원까지 올라갑니다. "
                "차량 손해 면제(DW)는 보험이 아니고, 대인·대물(SLP)은 카드 혜택으로 대체되지 않습니다. "
                "국제운전면허 9,000원, 주유 갤런 계산, SunPass·FasTrak·E-ZPass 통행료와 렌터카 프로그램 요금을 정리했습니다."),
        "desc": ("미국 렌터카 보험·통행료(2026-11). DW $26.99~49.99, SLP $8.44~42.38, PEC $5.99~15.67, "
                 "5일 보험 439,786~601,135원, 골든게이트 $10.25, 혼잡통행료 $9, PlatePass FL $9.99/$14.99."),
        "keywords": ("미국 렌터카 보험, 미국 렌터카 CDW, LDW 뜻, SLP 렌터카, LIS 보험, 미국 렌터카 면책, "
                     "국제운전면허증 9000원, 미국 렌터카 통행료, SunPass 렌터카, FasTrak 골든게이트, "
                     "E-ZPass 뉴욕 혼잡통행료, PlatePass 수수료, 미국 주유 갤런 계산"),
        "published": "2026-11-28",
        "updated": "2026-11-28",
        "read": 12,
        "image": "images/v69/usa-rental-car-insurance-guide.jpg",
        "ogImage": "images/og/v69-usa-car-og.jpg",
        "imageAlt": "모하비 사막을 달리는 차량과 도로",
        "imageCredit": "사진: Pexels (Ricky Esquivel)",
        "tours": [],
        "essentials": ["cp-adapter-nemotab", "cp-powerbank-spidy"],
        "related": ["us-esta-application-guide", "travel-insurance-guide", "travel-card-fees-comparison",
                    "us-west-4canyons", "japan-rental-car-etc-guide", "southeast-asia-rental-car-license-guide"],
        "ctaTitle": "미국 항공·렌터카 비교",
        "ctaText": "출발일과 픽업 지점을 넣으면 항공권과 렌터카(보험 포함 총액)를 같은 기준으로 비교합니다.",
        "fxNote": "1달러 1,335.11원 · 2026-11 고정 환산 기준",
        "faq": [
            ["미국 렌터카 보험은 꼭 들어야 하나요?",
             "법으로 의무는 아니지만, SLP(대인·대물 보충)를 넣지 않으면 제3자 배상이 계약의 최소 책임 한도에 머뭅니다. 카드사 무료 차량 손해 담보는 내가 빌린 차만 다루므로, 대인·대물은 따로 판단해야 합니다."],
            ["CDW/LDW와 SLP는 무엇이 다른가요?",
             "DW/LDW는 내가 빌린 차의 손상·도난·견인·휴차료를 면제하는 상품이고(보험이 아님), SLP/LIS는 상대방 상해·재산 손해를 최대 $300,000까지 보장하는 제3자 배상입니다. Enterprise 공개 요금은 DW $26.99~49.99, SLP $8.44~42.38(1일)입니다."],
            ["국제운전면허증이 없으면 못 빌리나요?",
             "캘리포니아는 방문객이 자국 면허만으로 운전할 수 있고 IDP를 법적으로 요구하지 않습니다. 플로리다 핸드북은 자국 면허와 함께 IDP를 소지하는 경우를 명시합니다. 렌터카 회사가 요구할 수 있으니 9,000원짜리 IDP(유효 1년)를 챙기고, 면허 원본은 반드시 함께 다니세요."],
            ["통행료는 어떻게 내나요?",
             "렌터카 회사 프로그램을 쓰면 됩니다. 플로리다 PlatePass는 통행한 날만 $9.99, 올인클루시브는 하루 $14.99이고, Enterprise TollPass는 하루 $4.95(대여 1건 최대 $34.65)입니다. 뉴욕 올인클루시브는 하루 $33.99로 비쌉니다."],
            ["5일 렌터카에서 보험료만 얼마인가요?",
             "Enterprise 공개 상한가로 DW+SLP가 $329.40(439,786원), 여기에 PEC·PAI까지 넣으면 $450.25(601,135원)입니다. 보험료가 차값을 넘는 경우가 흔하니 예약 단계에서 총액을 먼저 비교하세요."],
        ],
    },
    {
        "slug": "barcelona-gaudi-montserrat-3n4d-guide",
        "category": "유럽·장거리",
        "navTitle": "바르셀로나 3박4일 — 가우디 3곳 106,725원, 몬세라트 73,100원",
        "h1": "바르셀로나 3박4일, <em>가우디는 예약 순서</em>가 일정입니다",
        "seoTitle": "바르셀로나 3박4일 가우디·몬세라트 — 사그라다 26유로 (2026) | 트립픽",
        "dek": ("사그라다 파밀리아 26유로, 구엘공원 18유로, 카사 바트요 29유로부터. 세 곳 다 시간 지정 예약이라 "
                "순서를 잘못 잡으면 하루가 비어 버립니다. T-Casual 13유로 계산, 공항버스 7.75유로, "
                "몬세라트 결합권 50유로와 산악철도 요금까지 확인값으로 정리했습니다."),
        "desc": ("바르셀로나 3박4일(2026-11). 사그라다 26/36/40유로, 구엘 18유로, 카사 바트요 29유로~, "
                 "T-Casual 13유로, 공항 지하철 5.90유로, 몬세라트 Trans 50유로, 2인 입장·교통 436,550원."),
        "keywords": ("바르셀로나 3박4일, 바르셀로나 여행 경비, 사그라다 파밀리아 예약, 사그라다 파밀리아 가격, "
                     "구엘공원 예약, 구엘공원 입장료, 카사 바트요 가격, 가우디 투어, T-Casual 13유로, "
                     "바르셀로나 교통권, 몬세라트 가는 법, 몬세라트 Trans Montserrat, 아에로부스 7.75유로"),
        "published": "2026-11-28",
        "updated": "2026-11-28",
        "read": 12,
        "image": "images/v69/barcelona-gaudi-montserrat-3n4d-guide.jpg",
        "ogImage": "images/og/v69-barcelona-og.jpg",
        "imageAlt": "사그라다 파밀리아 성당의 첨탑과 파사드",
        "imageCredit": "사진: Pexels (Regan Dsouza)",
        "tours": [],
        "essentials": ["cp-adapter-nemotab", "cp-passport-reindeer"],
        "related": ["spain-barcelona-madrid", "europe-pickpocket-tax-refund-guide", "europe-train-eurail-vs-point",
                    "europe-shopping-tax-refund", "travel-insurance-guide", "airport-arrival-city-transfer-guide"],
        "ctaTitle": "바르셀로나 항공·투어 비교",
        "ctaText": "출발일을 넣으면 인천–바르셀로나 항공과 가우디 가이드 투어를 같은 기준으로 비교합니다.",
        "fxNote": "1유로 1,461.99원 · 2026-11 고정 환산 기준",
        "faq": [
            ["사그라다 파밀리아 티켓은 얼마인가요?",
             "공식 사이트 기준 성당만 26유로(38,012원), 타워 포함 36유로, 가이드 투어+타워 40유로입니다. 개인 티켓은 9명까지이고 시간 지정 예약이므로 매진되면 현장에서 살 수 없습니다."],
            ["구엘공원은 예약 없이 들어갈 수 있나요?",
             "유료 구역은 온라인 판매만 합니다. 성인 18유로, 7~12세·65세 이상 13.50유로, 0~6세는 무료지만 티켓은 있어야 합니다. 30분 단위 입장이고 한 번 나오면 재입장이 안 됩니다."],
            ["T-Casual로 공항까지 갈 수 있나요?",
             "지하철 L9 Sud 공항역(T1·T2)은 T-Casual로 이용할 수 없고 공항 전용권 5.90유로를 따로 사야 합니다. 시내는 T-Casual 10회권 13유로(1회당 1,901원)가 단권 2.90유로보다 쌉니다."],
            ["몬세라트는 어떻게 가나요?",
             "스페인 광장에서 FGC R5로 1시간 5분, 몬이스트롤에서 산악철도(왕복 15유로)나 아에리에서 케이블카(왕복 15유로)로 갈아탑니다. Trans Montserrat 50유로면 왕복 열차·산악철도·푸니쿨라가 모두 포함됩니다."],
            ["2인 3박4일 입장·교통비는?",
             "사그라다 52유로, 구엘 36유로, 카사 바트요 58유로, 몬세라트 100유로, 공항버스 왕복 26.60유로, T-Casual 2장 26유로로 모두 298.60유로(436,550원)입니다. 숙소·식비·항공은 별도입니다."],
        ],
    },
    {
        "slug": "turkey-istanbul-cappadocia-guide",
        "category": "유럽·장거리",
        "navTitle": "튀르키예 6박7일 — 무비자 90일·열기구 260유로, 2인 64만",
        "h1": "튀르키예 6박7일, <em>무비자 90일</em>로 이스탄불·카파도키아",
        "seoTitle": "튀르키예 6박7일 이스탄불·카파도키아 — 열기구 260유로 (2026) | 트립픽",
        "dek": ("튀르키예는 180일 중 90일 무비자입니다. 이스탄불카트 165리라에 1회 46.20리라, "
                "하기아 소피아 25유로, 톱카프 궁전 2,750리라, 뮤지엄패스 105유로의 본전 계산, "
                "카파도키아 열기구 260유로와 그린·레드투어 50~65유로, 국내선 1시간 25분까지 정리했습니다."),
        "desc": ("튀르키예 6박7일(2026-11). 무비자 180일 중 90일, 이스탄불카트 165리라·46.20리라, "
                 "하기아 25유로, 톱카프 2,750리라, 열기구 260/160유로, 2인 확정 지출 638,743원."),
        "keywords": ("튀르키예 여행, 이스탄불 카파도키아, 튀르키예 무비자, 이스탄불카트 가격, 하기아 소피아 입장료, "
                     "톱카프 궁전 입장료, 뮤지엄패스 이스탄불, 갈라타 탑 입장료, 카파도키아 열기구 가격, "
                     "카파도키아 그린투어, 레드투어 가격, 이스탄불 공항버스 하바이스트, 카이세리 국내선"),
        "published": "2026-11-28",
        "updated": "2026-11-28",
        "read": 13,
        "image": "images/v69/turkey-istanbul-cappadocia-guide.jpg",
        "ogImage": "images/og/v69-turkey-og.jpg",
        "imageAlt": "카파도키아 일출과 열기구",
        "imageCredit": "사진: Pexels (Yasin Onuş)",
        "tours": [],
        "essentials": ["cp-adapter-nemotab", "cp-powerbank-spidy"],
        "related": ["visa-free-stay-duration-guide", "europe-ees-etias-guide", "travel-insurance-guide",
                    "airport-arrival-city-transfer-guide", "europe-pickpocket-tax-refund-guide", "travel-medication-rules-guide"],
        "ctaTitle": "튀르키예 항공·숙소 비교",
        "ctaText": "출발일을 넣으면 인천–이스탄불 항공과 술탄아흐메트·카파도키아 숙소를 같은 기준으로 비교합니다.",
        "fxNote": "1리라 26.31원 · 1유로 1,461.99원 · 2026-11-28 고시 기준",
        "faq": [
            ["튀르키예는 비자가 필요한가요?",
             "한국 일반여권은 180일 중 90일 무비자입니다. 여권은 체류기간에 60일을 더한 기간(90일 체류 시 150일) 이상 남아야 하고, 6개월 이상 남은 여권을 권장합니다. 왕복 항공권을 요구받을 수 있습니다."],
            ["이스탄불카트는 얼마인가요?",
             "카드 165리라(4,340원)에 잔액을 따로 충전하고, 지하철·트램·버스 1회가 46.20리라(1,215원)입니다. 카드가 없으면 1회 65리라이고, 한 장으로 최대 5명까지 개찰구를 통과할 수 있습니다."],
            ["뮤지엄패스 이스탄불은 본전인가요?",
             "105유로(153,509원)로 5일·13곳을 1회씩 봅니다. 톱카프(2,750리라)+갈라타(30유로) 두 곳만이면 개별권이 3만 7천 원 싸고, 고고학·튀르크이슬람미술관까지 4곳을 넘기면 패스가 유리해집니다. 하기아 소피아와 바실리카 시스턴은 포함되지 않습니다."],
            ["카파도키아 열기구는 얼마인가요?",
             "Voyager Balloons 공식 요금은 성수기(4/1~11/1) 260유로(380,117원), 겨울(~4/1) 160유로이고 60분 비행입니다. 업체에 따라 140~330유로까지 차이가 나므로 비행 시간과 승객 보험을 함께 비교하세요."],
            ["2인 6박7일 경비는?",
             "입장·교통·투어만 638,743원입니다. 바실리카 시스턴과 레드투어를 넣으면 88만~93만 원, 열기구(2인 520유로)까지 넣으면 140만~169만 원입니다. 숙소·항공·식비는 별도입니다."],
        ],
    },
]

EXTRA = {
    "usa-rental-car-insurance-guide": {
        "hub": "",
        "regions": ["long"],
        "tags": ["시즌·서류", "준비물"],
        "stayRegions": [],
        "takeaway": ("미국 렌터카는 DW(차량 손해)와 SLP(대인·대물)를 나눠 봐야 합니다. "
                     "5일 기준 DW+SLP가 439,786원, 전부 넣으면 601,135원이고, 통행료는 "
                     "플로리다 사용일 $9.99·뉴욕 올인클루시브 $33.99입니다."),
        "facts": [["국제운전면허증", "9,000원 · 1년"], ["SLP 1일", "$8.44~42.38"]],
    },
    "barcelona-gaudi-montserrat-3n4d-guide": {
        "hub": "",
        "regions": ["long"],
        "tags": ["일정", "가성비"],
        "stayRegions": ["barcelona"],
        "takeaway": ("가우디 3곳은 사그라다 26유로·구엘 18유로·카사 바트요 29유로부터이고 모두 시간 지정 예약입니다. "
                     "T-Casual 13유로면 3박4일 시내 이동이 해결되고, 몬세라트는 Trans 50유로가 가장 간단합니다."),
        "facts": [["가우디 3곳 1인", "73유로 · 106,725원"], ["몬세라트 Trans", "50유로 · 73,100원"]],
    },
    "turkey-istanbul-cappadocia-guide": {
        "hub": "",
        "regions": ["long"],
        "tags": ["일정", "가성비"],
        "stayRegions": [],
        "takeaway": ("튀르키예는 180일 중 90일 무비자이고, 이스탄불카트 165리라에 1회 46.20리라입니다. "
                     "톱카프·갈라타만 보면 뮤지엄패스(105유로)보다 개별권이 싸고, 카파도키아 열기구는 성수기 260유로입니다."),
        "facts": [["무비자", "180일 중 90일"], ["열기구 성수기", "260유로 · 380,117원"]],
    },
}


def main() -> int:
    g = load("guides.json")
    slugs = {x["slug"] for x in g["guides"]}
    added = 0
    for item in NEW:
        if item["slug"] in slugs:
            continue
        g["guides"].append(item)
        added += 1
    save("guides.json", g)

    ex = load("guide_extra.json")
    for slug, row in EXTRA.items():
        ex["guides"][slug] = row
    save("guide_extra.json", ex)

    for item in NEW:
        print(f"  · {item['slug']} seoTitle {len(item['seoTitle'])}자 · desc {len(item['desc'])}자 · FAQ {len(item['faq'])}")
    print(f"[v69] guides {len(g['guides'])}편 (+{added}) · guide_extra {len(ex['guides'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
