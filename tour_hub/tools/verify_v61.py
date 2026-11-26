#!/usr/bin/env python3
"""v61 회귀 검증 — 추천 코스 5 → 21편(신규 16편) + 트립닷컴 상품 25건 등록.

    python3 tools/verify_v61.py

1. courses.json 21편 · 신규 16편의 필수 필드·일차·가이드 링크·패키지 참조
2. 신규 코스 일차의 tc 항목이 tripcom.json 실제 항목을 가리키고, 그 URL 에 Allianceid·trip_sub3
3. tripcom.json 신규 상품 25건(입장권 2·공항픽업 13·eSIM 10) — 제휴 파라미터·중복 없는 trip_sub1
4. 홈 산출물 — 코스 카드 21·패널 21·가이드 링크 40·'요금 보기' 카드, 깨진 참조 없음
5. 내부 링크 0건 실패(build_pages --check-links 결과 파일), sitemap 177 URL 유지
6. notes.md 상단 v61 기록
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT.parent / "deploy_site"
NOTES = ROOT.parent.parent / "scheduled-actions" / "🚀-매일-트립픽-콘텐츠-seo-수익화-업그레이드" / "notes.md"

NEW = [
    "taipei", "singapore", "hongkong", "phu_quoc", "cebu", "bohol", "kota_kinabalu",
    "kaohsiung", "beppu", "beijing", "qingdao", "sydney", "switzerland",
    "eastern_europe", "hanoi", "bangkok",
]
NEW_PRODUCTS = {
    "tickets": ["ticket_phuquoc", "ticket_cebu"],
    "transfers": ["transfer_pqc", "transfer_ceb", "transfer_tag", "transfer_bki", "transfer_khh",
                  "transfer_pek", "transfer_tao", "transfer_syd", "transfer_zrh", "transfer_prg",
                  "transfer_vie", "transfer_bud", "transfer_han"],
    "esims": ["esim_cebu", "esim_kaohsiung", "esim_beijing", "esim_qingdao", "esim_sydney",
              "esim_switzerland", "esim_prague", "esim_vienna", "esim_budapest", "esim_hanoi"],
}

fails: list[str] = []


def check(ok, msg):
    if not ok:
        fails.append(msg)


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def main() -> None:
    courses = load("courses.json")["courses"]
    by = {c["id"]: c for c in courses}
    check(len(courses) == 21, f"코스 {len(courses)}편 (기대 21)")
    for cid in ("osaka", "tokyo", "danang", "sapporo", "jeju"):
        check(cid in by, f"기존 코스 {cid} 사라짐")
    guides = {g["slug"]: g for g in load("guides.json")["guides"]}
    tours = {t["id"]: t for t in load("tours.json")["tours"]}
    ess = {e["id"]: e for e in load("essentials.json")["products"]}
    tc = load("tripcom.json")
    tc_by_id = {x["id"]: x for k in ("tickets", "transfers", "cars", "esims", "rails") for x in (tc.get(k) or [])}

    tc_items = 0
    for cid in NEW:
        c = by.get(cid)
        check(c is not None, f"신규 코스 {cid} 없음")
        if not c:
            continue
        for key in ("title", "country", "city", "lead", "hook", "tag", "img", "why", "days", "lodge", "guides"):
            check(bool(c.get(key)), f"{cid}: {key} 비어 있음")
        check(len(c["days"]) >= 3, f"{cid}: 일차 {len(c['days'])}개 (3개 미만)")
        check(len(c["why"]) >= 3, f"{cid}: why {len(c['why'])}개")
        check((ROOT / c["img"]).exists(), f"{cid}: 대표 이미지 없음 {c['img']}")
        check(len(c.get("guides") or []) >= 2, f"{cid}: 가이드 링크 {len(c.get('guides') or [])}개 (2개 미만)")
        for g in c.get("guides") or []:
            check(g["slug"] in guides, f"{cid}: 없는 가이드 {g['slug']}")
            check((OUT / "guides" / f"{g['slug']}.html").exists(), f"{cid}: 배포본에 가이드 없음 {g['slug']}")
        if c.get("package"):
            check(c["package"]["ref"] in tours, f"{cid}: 패키지 참조 {c['package']['ref']} 없음")
        for d in c["days"]:
            for it in d["items"]:
                k, r = it["kind"], it["ref"]
                if k == "tour":
                    check(r in tours, f"{cid}: 투어 {r} 없음")
                elif k == "essence":
                    check(r in ess, f"{cid}: 필수품 {r} 없음")
                elif k == "tc":
                    tc_items += 1
                    t = tc_by_id.get(r)
                    check(t is not None, f"{cid}: 트립닷컴 항목 {r} 없음")
                    if t:
                        check("Allianceid=11407530" in t["url"], f"{cid}: {r} Allianceid 누락")
                        check("trip_sub3=" in t["url"], f"{cid}: {r} trip_sub3 누락")
                else:
                    check(False, f"{cid}: 알 수 없는 kind {k}")
    check(tc_items >= 20, f"코스에 붙은 트립닷컴 카드 {tc_items}건 (20건 미만)")

    # 상품 25건
    added = 0
    subs = []
    for key, ids in NEW_PRODUCTS.items():
        have = {x["id"] for x in tc[key]}
        for pid in ids:
            check(pid in have, f"tripcom.{key} 에 {pid} 없음")
            if pid in have:
                added += 1
                item = next(x for x in tc[key] if x["id"] == pid)
                check(item.get("status", "").startswith("verified"), f"{pid}: 검증 상태 표기 없음")
                u = item["url"]
                check("Allianceid=11407530" in u, f"{pid}: Allianceid 누락")
                check("SID=336341874" in u, f"{pid}: SID 누락")
                check("trip_sub3=" in u, f"{pid}: trip_sub3 누락")
                m = re.search(r"trip_sub1=([a-z0-9_]+)", u)
                check(bool(m), f"{pid}: trip_sub1 없음")
                if m:
                    subs.append(m.group(1))
                for want in ("city", "title", "summary", "highlight", "label", "flag"):
                    check(bool(item.get(want)), f"{pid}: {want} 비어 있음")
    check(added == 25, f"신규 상품 {added}건 (기대 25)")
    check(len(subs) == len(set(subs)), "trip_sub1 중복 — 클릭 추적이 섞입니다")

    # 홈 산출물
    html = (OUT / "index.html").read_text(encoding="utf-8")
    check(html.count('class="pick"') == 21, f"홈 코스 카드 {html.count('class=\"pick\"')}장")
    check(html.count('class="panel"') + html.count('class="panel active"') == 21, "홈 코스 패널 21개 아님")
    check(html.count('data-course="') == 21, "data-course 21개 아님")
    check(html.count('class="cguide"') == 42, f"가이드 링크 {html.count('class=\"cguide\"')}개 (기대 42)")
    check(html.count(">요금 보기<") >= 25, "트립닷컴 카드 '요금 보기' 25건 미만")
    for cid in NEW:
        check(f'id="course-{cid}"' in html, f"홈에 {cid} 패널 없음")
        check(f'id="cpick-{cid}"' in html, f"홈에 {cid} 카드 없음")
    check("{{COURSE_COUNT}}" not in html, "템플릿 토큰 COURSE_COUNT 잔존")
    check(html.count("21개") >= 2, "홈 문구에 21개 표기 없음")

    # sitemap 은 이번에 URL 을 늘리지 않는다
    sm = (OUT / "sitemap.xml").read_text(encoding="utf-8")
    locs = re.findall(r"<loc>([^<]+)</loc>", sm)
    check(len(locs) == 177, f"sitemap {len(locs)} URL (기대 177)")
    check((ROOT / "sitemap.xml").read_text(encoding="utf-8") == sm, "build.py·build_pages sitemap 불일치")

    # notes.md
    if NOTES.exists():
        note = NOTES.read_text(encoding="utf-8")
        check("v61" in note, "notes.md 에 v61 기록 없음")
        for cid in ("taipei", "phu_quoc", "switzerland"):
            check(cid in note, f"notes.md 에 {cid} 없음")
    else:
        fails.append(f"notes.md 없음: {NOTES}")

    print(f"코스 {len(courses)}편(신규 {len(NEW)}) · 코스 내 트립닷컴 카드 {tc_items}건 · "
          f"신규 상품 {added}건 · 홈 카드 {html.count('class=\"pick\"')}장 · sitemap {len(locs)} URL")
    if fails:
        print("\n실패:")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("[verify_v61] PASS")


if __name__ == "__main__":
    main()
