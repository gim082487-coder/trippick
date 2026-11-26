#!/usr/bin/env python3
"""v53 회귀 검증 — 신규 가이드 3편 · 홍콩·마카오 찐숙소 · /passes 홍콩 패널 · 도구 페이지 맥락 링크.

    python3 tools/verify_v53.py

1. 가이드 119편 · sitemap 147 URL · 모든 lastmod 2026-11-25(KST)
2. v53 신규 3편 — 본문 2,200자 이상, Article·BreadcrumbList·FAQPage·Organization,
   히어로 1200×800·OG 1200×630·WebP 변형(picture), FAQ 4문항, 도구 바, 제휴 카드, 제목 60자 이하
3. 신규 ↔ 기존 양방향 related, guide_extra(지역·요약·확인값), photo_credits
4. /stays 홍콩·마카오 — 각 4곳·1박 가격·600×600 이미지·파트너스 딥링크·지역 top 일치·가이드 링크
5. /passes 홍콩 패널 — 탭·칩 3역·계산 함수·FAQ·제휴 카드
6. /checklist — v52·v53 가이드 카드
7. build.py 산출과 build_pages 산출 sitemap 동일 · IndexNow 키 배포본
8. 서치콘솔 action.md 사이트맵 기준 수(147개)
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT.parent / "deploy_site"
SITE = "https://trippick.pages.dev"
LASTMOD = "2026-11-27"
ACTION = ROOT.parent.parent / "scheduled-actions" / "🔍-구글-서치콘솔-색인-요청-재시도" / "action.md"

NEW = ["chiang-mai-3n4d-course", "bali-ubud-seminyak-3n4d-course", "shanghai-2n3d-3n4d-course"]
BACKLINKS = {
    "bangkok-3-packages": "chiang-mai-3n4d-course",
    "thailand-souvenir-list": "chiang-mai-3n4d-course",
    "winter-warm-resorts5": "bali-ubud-seminyak-3n4d-course",
    "hongkong-macau-3n4d-course": "shanghai-2n3d-3n4d-course",
    "airport-arrival-city-transfer-guide": "shanghai-2n3d-3n4d-course",
    "entry-immigration-guide": "bali-ubud-seminyak-3n4d-course",
}
fails: list[str] = []


def check(ok, msg):
    if not ok:
        fails.append(msg)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def ld_types(html: str) -> list[dict]:
    out = []
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            out.append(json.loads(raw))
        except ValueError as e:
            fails.append(f"JSON-LD 파싱 실패: {e}")
    return out


def flat_types(objs: list[dict]) -> Counter:
    c: Counter = Counter()
    stack = list(objs)
    while stack:
        o = stack.pop()
        if isinstance(o, dict):
            t = o.get("@type")
            if isinstance(t, str):
                c[t] += 1
            elif isinstance(t, list):
                c.update(t)
            stack += list(o.values())
        elif isinstance(o, list):
            stack += o
    return c


def body_chars(html: str) -> int:
    h = re.sub(r"<nav class=\"toc\".*?</nav>", " ", html, count=1, flags=re.S)
    h = re.sub(r"<script\b.*?</script>", " ", h, flags=re.S)
    h = re.sub(r"<style\b.*?</style>", " ", h, flags=re.S)
    h = re.sub(r"<[^>]+>", " ", h)
    h = re.sub(r"&[a-z]+;", " ", h)
    return len(re.sub(r"\s", "", h))


def main():
    gspec = load("guides.json")
    guides = gspec["guides"]
    by = {g["slug"]: g for g in guides}
    check(len(guides) == 135, f"가이드 {len(guides)}편 (기대 135)")

    extra = load("guide_extra.json")
    ex = extra["guides"]
    credits = load("photo_credits.json")["photos"]
    rnames = {r["code"]: r["name"] for r in extra["regions"]}
    check("id" in rnames, "guide_extra regions 에 인도네시아(id) 없음")

    for slug in NEW:
        g = by.get(slug)
        check(g is not None, f"{slug}: guides.json 에 없음")
        if not g:
            continue
        check(len(g["seoTitle"]) <= 60, f"{slug}: seoTitle {len(g['seoTitle'])}자 (60자 초과)")
        src = ROOT / "content" / "guides" / f"{slug}.html"
        check(src.exists(), f"{slug}: 본문 파일 없음")
        if src.exists():
            chars = body_chars(read(src))
            check(chars >= 2200, f"{slug}: 본문 {chars}자 (2,200자 미만)")
        page = OUT / "guides" / f"{slug}.html"
        check(page.exists(), f"{slug}: 배포본 없음")
        if not page.exists():
            continue
        html = read(page)
        t = flat_types(ld_types(html))
        for want in ("Article", "BreadcrumbList", "FAQPage", "Organization"):
            check(t.get(want, 0) >= 1, f"{slug}: {want} 스키마 없음")
        check(len(g.get("faq") or []) >= 4, f"{slug}: FAQ 문항 {len(g.get('faq') or [])}개 (기대 4+)")
        for img, size in ((g["image"], (1200, 800)), (g["ogImage"], (1200, 630))):
            p = ROOT / img
            check(p.exists(), f"{slug}: 이미지 없음 {img}")
            if p.exists():
                with Image.open(p) as im:
                    check(im.size == size, f"{slug}: {img} 크기 {im.size} (기대 {size})")
        for tool in ("EXCHANGE", "PASS", "SOS"):
            check(tool in html, f"{slug}: 도구 바 {tool} 없음")
        check("gact-k" in html, f"{slug}: 제휴 카드 없음")
        check(html.count('class="tb"') >= 3, f"{slug}: 표 3개 미만")
        check("image/webp" in html and "<picture>" in html, f"{slug}: WebP picture 없음")
        for w in (480, 720, 960):
            vp = ROOT / g["image"].replace(".jpg", f"-{w}.webp")
            check(vp.exists(), f"{slug}: WebP 변형 없음 {vp.name}")
        check(slug in credits, f"{slug}: photo_credits 없음")
        e = ex.get(slug)
        check(e is not None, f"{slug}: guide_extra 없음")
        if e:
            check(len(e.get("takeaway") or "") > 30, f"{slug}: 요약(takeaway) 없음")
            check(len(e.get("facts") or []) >= 2, f"{slug}: 확인값(facts) 2개 미만")
            check(all(c in rnames for c in (e.get("regions") or [])), f"{slug}: 알 수 없는 지역 코드")
        for target in (g.get("related") or []):
            tgt = by.get(target)
            check(tgt is not None, f"{slug}: related {target} 없음")
            if tgt is not None:
                check(slug in (tgt.get("related") or []), f"{slug} → {target} 단방향(역링크 없음)")

    for old, new in BACKLINKS.items():
        check(new in (by[old].get("related") or []), f"{old}: {new} 역링크 없음")

    # 4. 찐숙소 홍콩·마카오
    stays = load("stays.json")
    reg = {r["id"]: r for r in stays["regions"]}
    for rid, city in (("hongkong", "58"), ("macau", "59")):
        r = reg.get(rid)
        check(r is not None, f"stays regions 에 {rid} 없음")
        if not r:
            continue
        hs = [h for h in stays["hotels"] if h["region"] == rid]
        check(len(hs) == 6, f"stays {rid}: {len(hs)}곳 (기대 6)")
        check(r.get("count") == len(hs), f"stays {rid}: count {r.get('count')} ≠ {len(hs)}")
        best = max(hs, key=lambda x: (x["score"], x["reviews"]))
        check(r.get("top") == best["name"], f"stays {rid}: top '{r.get('top')}' ≠ 최고 평점 {best['name']}")
        check(any(g.get("slug") == "hongkong-macau-3n4d-course" for g in (r.get("guides") or [])),
              f"stays {rid}: 홍콩·마카오 가이드 링크 없음")
        for h in hs:
            check(h["price"] > 0, f"stays {rid}/{h['id']}: 가격 0")
            check(f"cityId={city}" in h["url"] and "Allianceid=11407530" in h["url"]
                  and "trip_sub3=" in h["url"], f"stays {rid}/{h['id']}: 파트너스 딥링크 파라미터 누락")
            ip = ROOT / h["img"]
            check(ip.exists(), f"stays {rid}/{h['id']}: 이미지 없음 {h['img']}")
            if ip.exists():
                with Image.open(ip) as im:
                    check(im.size == (600, 600), f"stays {rid}/{h['id']}: 이미지 {im.size} (기대 600×600)")
    page = OUT / "stays.html"
    if page.exists():
        html = read(page)
        for rid in ("hongkong", "macau"):
            check(f'id="{rid}"' in html, f"/stays: {rid} 앵커 없음")
            check(f'data-region="{rid}"' in html, f"/stays: {rid} 필터 칩 없음")
        check("guides/hongkong-macau-3n4d-course" in html, "/stays: 홍콩·마카오 가이드 링크 없음")
        check("guides/fukuoka-yufuin-3n4d-course" in html, "/stays: 후쿠오카·유후인 가이드 링크 없음")
        check("guides/japan-rental-car-etc-guide" in html, "/stays: 일본 렌터카 가이드 링크 없음")

    # 5. /passes 홍콩 패널
    pp = OUT / "passes.html"
    if pp.exists():
        html = read(pp)
        for token in ('data-city="hongkong"', 'data-panel="hongkong"', 'data-hk="kowloon"',
                      "pkHkPax", "pkHkBus", "pkHkTaxi", "function calcHk", "calcHk()",
                      "홍콩 공항철도", "A21", "왕복권", "guides/hongkong-macau-3n4d-course"):
            check(token in html, f"/passes: '{token}' 없음")
        hk = load("passes.json")["hongkong"]
        check(len(hk["stations"]) == 3, "/passes 데이터: 역 3곳 아님")
        check(hk["stations"][0]["round"] == 215, "/passes 데이터: 홍콩역 왕복권 215 아님")
        # JSON-LD FAQ 에 홍콩 문항
        t = flat_types(ld_types(html))
        check(t.get("FAQPage", 0) >= 1, "/passes: FAQPage 없음")

    # 6. /checklist 카드
    cl = OUT / "checklist.html"
    if cl.exists():
        html = read(cl)
        for slug in (*NEW, "fukuoka-yufuin-3n4d-course", "japan-rental-car-etc-guide"):
            check(f"guides/{slug}" in html, f"/checklist: {slug} 카드 없음")

    # 7. 사이트맵·IndexNow
    sm_out = read(OUT / "sitemap.xml")
    locs = re.findall(r"<loc>([^<]+)</loc>", sm_out)
    lastmods = set(re.findall(r"<lastmod>([^<]+)</lastmod>", sm_out))
    check(len(locs) == 177, f"sitemap {len(locs)} URL (기대 177)")
    check(locs and lastmods == {LASTMOD}, f"lastmod {sorted(lastmods)} (기대 {LASTMOD})")
    for slug in NEW:
        check(f"{SITE}/guides/{slug}" in locs, f"sitemap 에 /guides/{slug} 없음")
    check(read(ROOT / "sitemap.xml") == sm_out, "build.py 산출과 build_pages 산출 sitemap 불일치")
    key = str(load("indexnow.json").get("key") or "")
    kp = OUT / f"{key}.txt"
    check(kp.exists() and read(kp).strip() == key, "IndexNow 키 파일 배포본 없음/불일치")

    # 8. 서치콘솔 action.md
    if ACTION.exists():
        act = read(ACTION)
        check("147개" in act, "action.md 사이트맵 기준 수(147개) 미갱신")
        check("chiang-mai-3n4d-course" in act, "action.md 에 v53 신규 URL 없음")
    else:
        fails.append(f"action.md 없음: {ACTION}")

    print(f"가이드 {len(guides)}편 · sitemap {len(locs)} URL · lastmod {sorted(lastmods)} · 신규 {len(NEW)}편 · "
          f"찐숙소 {len(stays['hotels'])}곳")
    if fails:
        print("\n실패:")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("[verify_v53] PASS")


if __name__ == "__main__":
    main()
