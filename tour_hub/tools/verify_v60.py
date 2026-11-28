#!/usr/bin/env python3
"""v60 회귀 검증 — 신규 가이드 10편(일본·대만·말레이시아·필리핀·중국·호주·스위스·동유럽).

    python3 tools/verify_v60.py

1. 가이드 138편 · 허브 32곳 · 찐숙소 182곳 · sitemap 180 URL · lastmod 2026-11-26
2. 신규 10편 — 본문 3,000자 이상, 표 5개 이상, FAQ 5문항·FAQPage, 제휴 3건 이상,
   히어로 1200×800·OG 1200×630·WebP 480/720/960, guide_extra·photo_credits
3. 신규 10편 ↔ 기존 가이드 양방향 related, 제목 유사도 0.43 이하
4. 내부 링크 — 트립픽 페이지(숙소·패스·환전·쿠폰·체크리스트·SOS) 링크 각 3종 이상, 가이드 상호 링크 2편 이상
5. action.md 사이트맵 수치·신규 URL 반영, notes.md v60 기록
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT.parent / "deploy_site"
SITE = "https://trippick.pages.dev"
LASTMOD = "2026-11-28"
ACTION = ROOT.parent.parent / "scheduled-actions" / "🔍-구글-서치콘솔-색인-요청-재시도" / "action.md"
NOTES = ROOT.parent.parent / "scheduled-actions" / "🚀-매일-트립픽-콘텐츠-seo-수익화-업그레이드" / "notes.md"

NEW = [
    "beppu-onsen-1n2d-course",
    "kaohsiung-tainan-3n4d-course",
    "kota-kinabalu-3n4d-course",
    "bohol-3n4d-course",
    "beijing-3n4d-course",
    "qingdao-2n3d-course",
    "sydney-4n5d-course",
    "switzerland-jungfrau-zermatt-pass",
    "eastern-europe-prague-vienna-budapest",
    "japan-shinkansen-jr-pass-guide",
]
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
    check(len(guides) == 179, f"가이드 {len(guides)}편 (기대 179)")

    hubs = {c["slug"]: c for c in load("city_hubs.json")["cities"]}
    check(len(hubs) == 32, f"도시 허브 {len(hubs)}곳 (기대 32)")

    stays = load("stays.json")
    check(len(stays["hotels"]) == 182, f"찐숙소 {len(stays['hotels'])}곳 (기대 182)")

    extra = load("guide_extra.json")["guides"]
    credits = load("photo_credits.json")["photos"]

    # build_pages.py 의 clean_site_urls 가 확장자를 떼어 정본 주소(../stays)로 바꾼다
    INTERNAL = ("../stays", "../passes", "../exchange", "../coupons", "../checklist", "../sos")

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
            check(html.count('rel="noopener sponsored"') >= 5, f"{slug}: 제휴 링크 5건 미만")
            check("image/webp" in html and "<picture>" in html, f"{slug}: WebP picture 없음")
            for href in re.findall(r'href="(https://[^"]+)"[^>]*rel="noopener sponsored"', html):
                if "trip.com" in href:
                    check("Allianceid=11407530" in href, f"{slug}: Allianceid 누락 {href[:60]}")
                    check("trip_sub3=" in href, f"{slug}: trip_sub3 누락 {href[:60]}")
                else:
                    check(href.startswith(("https://link.coupang.com/", "https://naver.me/")),
                          f"{slug}: 검증되지 않은 제휴 도메인 {href[:60]}")
            internal = sum(html.count(x) for x in INTERNAL)
            check(internal >= 3, f"{slug}: 트립픽 내부 페이지 링크 {internal}건 (3건 미만)")
            glinks = len(re.findall(r'href="(%s)"' % "|".join(re.escape(x) for x in by), html))
            check(glinks >= 2, f"{slug}: 가이드 상호 링크 {glinks}건 (2건 미만)")
        for img, size in ((g["image"], (1200, 800)), (g["ogImage"], (1200, 630))):
            p = ROOT / img
            check(p.exists(), f"{slug}: 이미지 없음 {img}")
            if p.exists():
                with Image.open(p) as im:
                    check(im.size == size, f"{slug}: {img} {im.size} (기대 {size})")
        for w in (480, 720, 960):
            vp = ROOT / g["image"].replace(".jpg", f"-{w}.webp")
            check(vp.exists(), f"{slug}: WebP 변형 없음 {vp.name}")
        credit = credits.get(f"v60/{slug}")
        check(credit is not None, f"{slug}: photo_credits 없음")
        if credit:
            check(bool(credit.get("license")) and bool(credit.get("artist")),
                  f"{slug}: 사진 라이선스·저작자 미기록")
        e = extra.get(slug)
        check(e is not None, f"{slug}: guide_extra 없음")
        if e:
            check(len(e.get("takeaway") or "") > 30, f"{slug}: 요약 없음")
            check(len(e.get("facts") or []) >= 2, f"{slug}: 확인값 2개 미만")
            for r in (e.get("regions") or []):
                check(r in {"jp", "kr", "vn", "th", "ph", "cn", "twgu", "sg", "gu", "id", "long", "etc"},
                      f"{slug}: 알 수 없는 지역 코드 {r}")
        for target in (g.get("related") or []):
            tgt = by.get(target)
            check(tgt is not None, f"{slug}: related {target} 없음")
            if tgt:
                check(slug in (tgt.get("related") or []), f"{slug} → {target} 단방향")

    # 제목 유사도 0.43 이하 (신규 10편) — tools/v50_content_audit.py 와 같은 자카드(토큰 집합)
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

    # sitemap
    sm = read(OUT / "sitemap.xml")
    locs = re.findall(r"<loc>([^<]+)</loc>", sm)
    lastmods = set(re.findall(r"<lastmod>([^<]+)</lastmod>", sm))
    check(len(locs) == 227, f"sitemap {len(locs)} URL (기대 227)")
    check(lastmods == {LASTMOD}, f"lastmod {sorted(lastmods)}")
    for slug in NEW:
        check(f"{SITE}/guides/{slug}" in locs, f"sitemap 에 /guides/{slug} 없음")
    check(sorted(re.findall(r"<loc>([^<]+)</loc>", read(ROOT / "sitemap.xml"))) == sorted(locs), "build.py 산출과 build_pages 산출 sitemap 불일치")

    # action.md · notes.md
    if ACTION.exists():
        act = read(ACTION)
        check("227개" in act, "action.md 사이트맵 수(227개) 미갱신")
        for slug in NEW:
            check(slug in act, f"action.md 에 v60 신규 URL({slug}) 없음")
        check(act.startswith("---\ntitle:"), "action.md 프론트매터 손상")
    else:
        fails.append(f"action.md 없음: {ACTION}")

    if NOTES.exists():
        note = read(NOTES)
        check("v60" in note, "notes.md 에 v60 기록 없음")
        for slug in NEW:
            check(slug in note, f"notes.md 에 {slug} 없음")
    else:
        fails.append(f"notes.md 없음: {NOTES}")

    print(f"가이드 {len(guides)}편 · 허브 {len(hubs)}곳 · 숙소 {len(stays['hotels'])}곳 · "
          f"sitemap {len(locs)} URL · 신규 {len(NEW)}편")
    if fails:
        print("\n실패:")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("[verify_v60] PASS")


if __name__ == "__main__":
    main()
