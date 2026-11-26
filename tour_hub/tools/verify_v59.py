#!/usr/bin/env python3
"""v59 회귀 검증 — 신규 가이드 3편 · 도시 허브 3곳 · 찐숙소 15곳.

    python3 tools/verify_v59.py

1. 가이드 125편 · 허브 26곳 · 찐숙소 141곳(지역 35) · sitemap 167 URL · lastmod 2026-11-26
2. 신규 3편 — 본문 3,000자 이상, 표 5개 이상, FAQ 5문항·FAQPage, 제휴 3건 이상,
   히어로 1200×800·OG 1200×630·WebP 480/720/960, guide_extra·photo_credits
3. 신규 허브 3곳 — 페이지 존재, 숙소 카드 5장, 팁 4개, 가이드 링크, 1600×1000·OG 1200×630
4. 찐숙소 — 지역 3곳의 숙소 5곳씩, 가격·기준일·이미지·파트너스 파라미터
5. 신규 3편 ↔ 기존 가이드 양방향 related
6. action.md 사이트맵 수치·신규 URL 반영(프론트매터 유지)
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
LASTMOD = "2026-11-26"
ACTION = ROOT.parent.parent / "scheduled-actions" / "🔍-구글-서치콘솔-색인-요청-재시도" / "action.md"

NEW = ["phu-quoc-3n4d-4n5d-course", "cebu-3n4d-course", "hanoi-halong-3n4d-course"]
HUBS = ["chiangmai", "bali", "shanghai"]
BACKLINKS = {
    "chiang-mai-3n4d-course": "phu-quoc-3n4d-4n5d-course",
    "bali-ubud-seminyak-3n4d-course": "phu-quoc-3n4d-4n5d-course",
    "danang-hoian-3n5d": "phu-quoc-3n4d-4n5d-course",
    "vietnam-esim": "phu-quoc-3n4d-4n5d-course",
    "guam-4n5d-course": "cebu-3n4d-course",
    "singapore-3n4d-course-budget": "cebu-3n4d-course",
    "taipei-3n4d-course-budget": "cebu-3n4d-course",
    "travel-insurance-guide": "cebu-3n4d-course",
    "flight-cheap-booking-baggage": "hanoi-halong-3n4d-course",
    "travel-card-fees-comparison": "hanoi-halong-3n4d-course",
}
fails: list[str] = []


def check(ok, msg):
    if not ok:
        fails.append(msg)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def body_chars(html: str) -> int:
    h = re.sub(r"<nav class=\"toc\".*?</nav>", " ", html, count=1, flags=re.S)
    h = re.sub(r"<script\b.*?</script>", " ", h, flags=re.S)
    h = re.sub(r"<style\b.*?</style>", " ", h, flags=re.S)
    h = re.sub(r"<[^>]+>", " ", h)
    h = re.sub(r"&[a-z]+;", " ", h)
    return len(re.sub(r"\s", "", h))


def main() -> None:
    gspec = load("guides.json")
    guides = gspec["guides"]
    by = {g["slug"]: g for g in guides}
    check(len(guides) == 135, f"가이드 {len(guides)}편 (기대 135)")

    hubs = {c["slug"]: c for c in load("city_hubs.json")["cities"]}
    check(len(hubs) == 26, f"도시 허브 {len(hubs)}곳 (기대 26)")

    stays = load("stays.json")
    check(len(stays["hotels"]) == 141, f"찐숙소 {len(stays['hotels'])}곳 (기대 141)")
    check(len(stays["regions"]) == 35, f"숙소 지역 {len(stays['regions'])}곳 (기대 35)")

    extra = load("guide_extra.json")["guides"]
    credits = load("photo_credits.json")["photos"]

    # 2. 신규 가이드
    for slug in NEW:
        g = by.get(slug)
        check(g is not None, f"{slug}: guides.json 에 없음")
        if not g:
            continue
        check(len(g["seoTitle"]) <= 60, f"{slug}: seoTitle {len(g['seoTitle'])}자")
        check(len(g.get("desc") or "") <= 155, f"{slug}: description {len(g.get('desc') or '')}자 (155자 초과)")
        check(len(g.get("faq") or []) == 5, f"{slug}: FAQ {len(g.get('faq') or [])}문항")
        src = ROOT / "content" / "guides" / f"{slug}.html"
        check(src.exists(), f"{slug}: 본문 파일 없음")
        if src.exists():
            chars = body_chars(read(src))
            check(chars >= 3000, f"{slug}: 본문 {chars}자 (3,000자 미만)")
        page = OUT / "guides" / f"{slug}.html"
        check(page.exists(), f"{slug}: 배포본 없음")
        if page.exists():
            html = read(page)
            for want in ("Article", "BreadcrumbList", "FAQPage", "Organization"):
                check(want in html, f"{slug}: {want} 스키마 없음")
            check(html.count('"@type": "Question"') == 5, f"{slug}: FAQPage 5문항 아님")
            check(html.count('details class="fq"') == 5, f"{slug}: 화면 FAQ 5문항 아님")
            check(html.count('class="tb"') >= 5, f"{slug}: 표 5개 미만 ({html.count('class=\"tb\"')})")
            check(html.count('rel="noopener sponsored"') >= 3, f"{slug}: 제휴 링크 3건 미만")
            check("image/webp" in html and "<picture>" in html, f"{slug}: WebP picture 없음")
            for href in re.findall(r'href="(https://[^"]+)"[^>]*rel="noopener sponsored"', html):
                if "trip.com" in href:
                    check("Allianceid=11407530" in href, f"{slug}: Allianceid 누락 {href[:60]}")
                    check("trip_sub3=" in href, f"{slug}: trip_sub3 누락 {href[:60]}")
                else:
                    check(href.startswith(("https://link.coupang.com/", "https://naver.me/")),
                          f"{slug}: 검증되지 않은 제휴 도메인 {href[:60]}")
        for img, size in ((g["image"], (1200, 800)), (g["ogImage"], (1200, 630))):
            p = ROOT / img
            check(p.exists(), f"{slug}: 이미지 없음 {img}")
            if p.exists():
                with Image.open(p) as im:
                    check(im.size == size, f"{slug}: {img} {im.size} (기대 {size})")
        for w in (480, 720, 960):
            vp = ROOT / g["image"].replace(".jpg", f"-{w}.webp")
            check(vp.exists(), f"{slug}: WebP 변형 없음 {vp.name}")
        check(f"v59/{slug}" in credits, f"{slug}: photo_credits 없음")
        e = extra.get(slug)
        check(e is not None, f"{slug}: guide_extra 없음")
        if e:
            check(len(e.get("takeaway") or "") > 30, f"{slug}: 요약 없음")
            check(len(e.get("facts") or []) >= 2, f"{slug}: 확인값 2개 미만")
        for target in (g.get("related") or []):
            tgt = by.get(target)
            check(tgt is not None, f"{slug}: related {target} 없음")
            if tgt:
                check(slug in (tgt.get("related") or []), f"{slug} → {target} 단방향")

    for old, new in BACKLINKS.items():
        check(old in by and new in (by[old].get("related") or []), f"{old}: {new} 역링크 없음")

    # 제목 유사도 0.43 이하 (신규 3편) — tools/v50_content_audit.py 와 같은 자카드(토큰 집합)
    def toks(t: str) -> set[str]:
        return set(re.findall(r"[가-힣]{2,}|[A-Za-z]{3,}", t))

    for slug in NEW:
        a = toks(by[slug]["seoTitle"])
        for other in guides:
            if other["slug"] == slug:
                continue
            b = toks(other["seoTitle"])
            if not a or not b:
                continue
            r = len(a & b) / len(a | b)
            check(r <= 0.43, f"{slug} vs {other['slug']}: 제목 유사도 {r:.2f} (0.43 초과)")

    # 3. 신규 허브
    for slug in HUBS:
        h = hubs.get(slug)
        check(h is not None, f"허브 {slug} 없음")
        if not h:
            continue
        check(len(h.get("tips") or []) == 4, f"/{slug}: 팁 {len(h.get('tips') or [])}개 (기대 4)")
        check(len(h.get("guides") or []) >= 5, f"/{slug}: 가이드 링크 {len(h.get('guides') or [])}편")
        for gs in (h.get("guides") or []):
            check(gs in by, f"/{slug}: 없는 가이드 링크 {gs}")
        page = OUT / f"{slug}.html"
        check(page.exists(), f"/{slug} 배포본 없음")
        if page.exists():
            html = read(page)
            check(html.count('class="scard"') >= 5, f"/{slug}: 숙소 카드 {html.count('class=\"scard\"')}장 (기대 5)")
            check("FAQPage" in html, f"/{slug}: FAQPage 없음")
            for gs in (h.get("guides") or [])[:3]:
                check(f"guides/{gs}" in html, f"/{slug}: {gs} 링크 없음")
        p = ROOT / h["image"]
        check(p.exists(), f"/{slug}: 이미지 없음 {h['image']}")
        if p.exists():
            with Image.open(p) as im:
                check(im.size == (1600, 1000), f"/{slug}: 이미지 {im.size} (기대 1600×1000)")
        og = ROOT / h["ogImage"]
        check(og.exists(), f"/{slug}: OG 없음")
        if og.exists():
            with Image.open(og) as im:
                check(im.size == (1200, 630), f"/{slug}: OG {im.size}")
        check(f"v59/{slug}" in credits, f"/{slug}: photo_credits 없음")
        region = next((r for r in stays["regions"] if r["id"] == slug), None)
        check(region is not None, f"stays: {slug} 지역 없음")
        if region:
            hs = [x for x in stays["hotels"] if x["region"] == slug]
            check(len(hs) == 5, f"stays {slug}: 숙소 {len(hs)}곳 (기대 5)")
            for x in hs:
                check(bool(x.get("price")) and bool(x.get("priceBasis")), f"stays {slug}-{x['id']}: 가격/기준 없음")
                check((ROOT / x["img"]).exists(), f"stays {slug}-{x['id']}: 이미지 없음")
                check("trip_sub3=" in x["url"] and "Allianceid=11407530" in x["url"], f"stays {slug}-{x['id']}: 파트너스 파라미터 누락")

    # 4. sitemap
    sm = read(OUT / "sitemap.xml")
    locs = re.findall(r"<loc>([^<]+)</loc>", sm)
    lastmods = set(re.findall(r"<lastmod>([^<]+)</lastmod>", sm))
    check(len(locs) == 177, f"sitemap {len(locs)} URL (기대 177)")
    check(lastmods == {LASTMOD}, f"lastmod {sorted(lastmods)}")
    for slug in NEW:
        check(f"{SITE}/guides/{slug}" in locs, f"sitemap 에 /guides/{slug} 없음")
    for slug in HUBS:
        check(f"{SITE}/{slug}" in locs, f"sitemap 에 /{slug} 없음")
    check(read(ROOT / "sitemap.xml") == sm, "build.py 산출과 build_pages 산출 sitemap 불일치")

    # 5. action.md
    if ACTION.exists():
        act = read(ACTION)
        check("177개" in act, "action.md 사이트맵 수(177개) 미갱신")
        for slug in NEW:
            check(slug in act, f"action.md 에 v59 신규 URL({slug}) 없음")
        for slug in HUBS:
            check(f"trippick.pages.dev/{slug}" in act, f"action.md 에 v59 허브(/{slug}) 없음")
        check(act.startswith("---\ntitle:"), "action.md 프론트매터 손상")
    else:
        fails.append(f"action.md 없음: {ACTION}")

    print(f"가이드 {len(guides)}편 · 허브 {len(hubs)}곳 · 숙소 {len(stays['hotels'])}곳 · sitemap {len(locs)} URL · 신규 {len(NEW)}편")
    if fails:
        print("\n실패:")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("[verify_v59] PASS")


if __name__ == "__main__":
    main()
