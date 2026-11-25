#!/usr/bin/env python3
"""v54 회귀 검증 — 마운자로 일본 반입 가이드 · 괌 4박5일 · 하와이 5박7일.

    python3 tools/verify_v54.py

1. 가이드 119편 · sitemap 147 URL · lastmod 2026-11-25(KST)
2. 신규 3편 — 본문 2,200자 이상, Article·BreadcrumbList·FAQPage·Organization,
   히어로 1200×800·OG 1200×630·WebP 480/720/960, FAQ 4문항 이상, 도구 바, 제휴 카드 3개, 표 5개 이상
3. 신규 ↔ 기존 양방향 related, guide_extra(지역·요약·확인값), photo_credits, seoTitle 60자 이하
4. 일본 허브(도쿄·오사카·후쿠오카)에 마운자로 가이드 연결 + metaDesc 편수 일치
5. /stays 괌 지역에 4박5일 코스 링크
6. 마운자로 본문 핵심 수치(4펜·수입확인증·21일·12개·100mL) 존재
7. 제휴 링크가 검증된 파트너 파라미터(Allianceid=11407530·trip_sub3)를 유지
8. build.py 산출과 build_pages 산출 sitemap 동일 · IndexNow 키 · action.md 147개
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
LASTMOD = "2026-11-25"
ACTION = ROOT.parent.parent / "scheduled-actions" / "🔍-구글-서치콘솔-색인-요청-재시도" / "action.md"

NEW = ["japan-mounjaro-injection-guide", "guam-4n5d-course", "hawaii-oahu-5n7d-course"]
BACKLINKS = {
    "travel-medication-rules-guide": "japan-mounjaro-injection-guide",
    "entry-immigration-guide": "japan-mounjaro-injection-guide",
    "airport-checkin-customs-guide": "japan-mounjaro-injection-guide",
    "overseas-sick-hospital-insurance-claim": "japan-mounjaro-injection-guide",
    "flight-delay-card-lost-emergency": "japan-mounjaro-injection-guide",
    "guam-resorts": "guam-4n5d-course",
    "guam-vs-saipan-comparison": "guam-4n5d-course",
    "incheon-airport-smartpass-lounge": "guam-4n5d-course",
    "travel-insurance-guide": "guam-4n5d-course",
    "hawaii-hyatt-vs-sheraton": "hawaii-oahu-5n7d-course",
    "luggage-size-weight-airline-guide": "hawaii-oahu-5n7d-course",
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
    check(len(guides) == 119, f"가이드 {len(guides)}편 (기대 119)")

    extra = load("guide_extra.json")
    ex = extra["guides"]
    credits = load("photo_credits.json")["photos"]
    rnames = {r["code"]: r["name"] for r in extra["regions"]}

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
        check(html.count('class="gact"') >= 3, f"{slug}: 제휴 카드 3개 미만")
        check(html.count('rel="noopener sponsored"') >= 3, f"{slug}: sponsored 표기 3건 미만")
        check(html.count('class="tb"') >= 5, f"{slug}: 표 5개 미만 ({html.count('class=\"tb\"')})")
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

    # 4. 일본 허브
    hubs = {c["slug"]: c for c in load("city_hubs.json")["cities"]}
    for slug in ("tokyo", "osaka", "fukuoka"):
        c = hubs.get(slug)
        check(c is not None, f"허브 {slug} 없음")
        if not c:
            continue
        check("japan-mounjaro-injection-guide" in c["guides"], f"/{slug}: 마운자로 가이드 링크 없음")
        check(f"관련 가이드 {len(c['guides'])}편" in (c.get("metaDesc") or ""),
              f"/{slug}: metaDesc 편수({len(c['guides'])}) 미반영")
        page = OUT / f"{slug}.html"
        if page.exists():
            check("japan-mounjaro-injection-guide" in read(page), f"/{slug} 배포본: 마운자로 링크 없음")

    # 5. /stays 괌
    stays = load("stays.json")
    guam = next((r for r in stays["regions"] if r["id"] == "guam"), None)
    check(guam is not None, "stays regions 에 guam 없음")
    if guam:
        check(any(x.get("slug") == "guam-4n5d-course" for x in (guam.get("guides") or [])),
              "stays guam: 4박5일 코스 링크 없음")
    sp = OUT / "stays.html"
    if sp.exists():
        check("guides/guam-4n5d-course" in read(sp), "/stays: 괌 4박5일 코스 링크 없음")

    # 6. 마운자로 핵심 수치
    mp = OUT / "guides" / "japan-mounjaro-injection-guide.html"
    if mp.exists():
        html = read(mp)
        for token in ("수입확인증", "1개월분", "4펜", "2~8℃", "21일", "12개", "100mL", "6병", "폐의약품"):
            check(token in html, f"마운자로: '{token}' 없음")
        for link in ("travel-medication-rules-guide", "entry-immigration-guide", "airport-checkin-customs-guide"):
            check(link in html, f"마운자로: {link} 본문 링크 없음")

    # 7. 제휴 파라미터
    for slug in NEW:
        page = OUT / "guides" / f"{slug}.html"
        if not page.exists():
            continue
        for href in re.findall(r'href="(https://[^"]+)"[^>]*rel="noopener sponsored"', read(page)):
            if "trip.com" in href:
                check("Allianceid=11407530" in href, f"{slug}: 제휴 링크 Allianceid 누락 {href[:70]}")
                check("trip_sub3=" in href, f"{slug}: 제휴 링크 trip_sub3 누락 {href[:70]}")
            else:
                check(href.startswith(("https://link.coupang.com/", "https://naver.me/")),
                      f"{slug}: 검증되지 않은 제휴 도메인 {href[:70]}")

    # 8. 사이트맵·IndexNow·action.md
    sm_out = read(OUT / "sitemap.xml")
    locs = re.findall(r"<loc>([^<]+)</loc>", sm_out)
    lastmods = set(re.findall(r"<lastmod>([^<]+)</lastmod>", sm_out))
    check(len(locs) == 147, f"sitemap {len(locs)} URL (기대 147)")
    check(locs and lastmods == {LASTMOD}, f"lastmod {sorted(lastmods)} (기대 {LASTMOD})")
    for slug in NEW:
        check(f"{SITE}/guides/{slug}" in locs, f"sitemap 에 /guides/{slug} 없음")
    check(read(ROOT / "sitemap.xml") == sm_out, "build.py 산출과 build_pages 산출 sitemap 불일치")
    key = str(load("indexnow.json").get("key") or "")
    kp = OUT / f"{key}.txt"
    check(kp.exists() and read(kp).strip() == key, "IndexNow 키 파일 배포본 없음/불일치")

    if ACTION.exists():
        act = read(ACTION)
        check("147개" in act, "action.md 사이트맵 기준 수(147개) 미갱신")
        for slug in NEW:
            check(slug in act, f"action.md 에 v54 신규 URL({slug}) 없음")
        check(act.startswith("---\ntitle:"), "action.md 프론트매터 손상")
    else:
        fails.append(f"action.md 없음: {ACTION}")

    print(f"가이드 {len(guides)}편 · sitemap {len(locs)} URL · lastmod {sorted(lastmods)} · 신규 {len(NEW)}편")
    if fails:
        print("\n실패:")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("[verify_v54] PASS")


if __name__ == "__main__":
    main()
