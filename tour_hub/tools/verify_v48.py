#!/usr/bin/env python3
"""v48 회귀 검증 — 검색 노출·SEO 강화(구조화 데이터·메타·사이트맵·IndexNow).

    python3 tools/verify_v48.py

1. 가이드 103편 · v48 신규 3편 본문/이미지/OG/FAQPage
2. JSON-LD — 모든 가이드 Article(publisher logo)+BreadcrumbList, 도구·신뢰 페이지 BreadcrumbList,
   모든 콘텐츠 페이지 Organization
3. title ≤60자 · meta description ≤155자 · 중복 0 · img alt 누락 0
4. sitemap 131 URL · build.py 산출(tour_hub/sitemap.xml)과 build_pages 산출(deploy_site) 동일
5. IndexNow 키 파일(data/indexnow.json)이 사이트 루트에 배포본으로 존재
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

NEW = ["travel-card-fees-comparison", "travel-insurance-guide", "incheon-airport-parking-bus"]
VERIFY_FILES = {"googleece2734ba5b7b23a.html", "naver1a2e72ce656ca4889c08fec3050b4703.html", "404.html"}
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


def main():
    gspec = load("guides.json")
    guides = gspec["guides"]
    check(len(guides) == 119, f"가이드 {len(guides)}편 (기대 119)")

    # 1. 신규 3편
    for slug in NEW:
        g = next((x for x in guides if x["slug"] == slug), None)
        check(g is not None, f"{slug}: guides.json 에 없음")
        if not g:
            continue
        check((ROOT / "content" / "guides" / f"{slug}.html").exists(), f"{slug}: 본문 파일 없음")
        page = OUT / "guides" / f"{slug}.html"
        check(page.exists(), f"{slug}: 배포본 없음")
        if not page.exists():
            continue
        html = read(page)
        check('type="application/ld+json"' in html, f"{slug}: JSON-LD 없음")
        t = flat_types(ld_types(html))
        for want in ("Article", "BreadcrumbList", "FAQPage", "Organization"):
            check(t.get(want, 0) >= 1, f"{slug}: {want} 스키마 없음")
        for img in (g["image"], g["ogImage"]):
            p = ROOT / img
            check(p.exists(), f"{slug}: 이미지 없음 {img}")
            if p.exists():
                with Image.open(p) as im:
                    check(im.size == (1200, 630), f"{slug}: {img} 크기 {im.size} (기대 1200×630)")
        check(len(g.get("faq") or []) >= 3, f"{slug}: FAQ 문항 부족")

    # 2. 구조화 데이터 전수
    pages = [p for p in OUT.rglob("*.html") if p.name not in VERIFY_FILES]
    for p in pages:
        html = read(p)
        rel = str(p.relative_to(OUT))
        t = flat_types(ld_types(html))
        if rel.startswith("guides/") and rel != "guides/index.html":
            check(t.get("Article", 0) >= 1, f"{rel}: Article 없음")
            check(t.get("BreadcrumbList", 0) >= 1, f"{rel}: BreadcrumbList 없음")
        check(t.get("Organization", 0) >= 1, f"{rel}: Organization 없음")
    # publisher logo (Article rich result 요구)
    art = 0
    for p in OUT.glob("guides/*.html"):
        if p.name == "index.html":
            continue
        for obj in ld_types(read(p)):
            for node in (obj.get("@graph") or [obj]):
                if node.get("@type") == "Article":
                    art += 1
                    pub = node.get("publisher") or {}
                    check((pub.get("logo") or {}).get("url", "").endswith("/images/logo-512.png"),
                          f"{p.name}: Article publisher logo 없음")
    check(art == len(guides), f"Article 노드 {art}개 (가이드 {len(guides)}편)")

    # 3. title·description·alt
    titles, descs = Counter(), Counter()
    for p in pages:
        html = read(p)
        rel = str(p.relative_to(OUT))
        mt = re.search(r"<title>(.*?)</title>", html, re.S)
        md = re.search(r'<meta name="description" content="(.*?)"', html, re.S)
        title = (mt.group(1).strip() if mt else "")
        desc = (md.group(1).strip() if md else "")
        check(title, f"{rel}: title 없음")
        check(desc, f"{rel}: description 없음")
        check(len(title) <= 60, f"{rel}: title {len(title)}자 (60자 초과)")
        check(len(desc) <= 155, f"{rel}: description {len(desc)}자 (155자 초과)")
        titles[title] += 1
        descs[desc] += 1
        for tag in re.findall(r"<img\b[^>]*>", html):
            check("alt=" in tag and not re.search(r'alt="\s*"', tag), f"{rel}: alt 없는 img {tag[:60]}")
    dup_t = [t for t, n in titles.items() if n > 1]
    dup_d = [d for d, n in descs.items() if n > 1]
    check(not dup_t, f"중복 title {len(dup_t)}개")
    check(not dup_d, f"중복 description {len(dup_d)}개")

    # 4. sitemap
    sm_out = read(OUT / "sitemap.xml")
    locs = re.findall(r"<loc>([^<]+)</loc>", sm_out)
    check(len(locs) == 156, f"sitemap {len(locs)} URL (기대 156)")
    for slug in NEW:
        check(f"{SITE}/guides/{slug}" in locs, f"sitemap 에 /guides/{slug} 없음")
    for tool in ("exchange", "quiz", "baggage", "checklist", "sos", "stays", "passes", "calendar"):
        check(f"{SITE}/{tool}" in locs, f"sitemap 에 도구 페이지 /{tool} 없음")
    src_sm = read(ROOT / "sitemap.xml")
    check(src_sm == sm_out, "build.py 산출(tour_hub/sitemap.xml)과 build_pages 산출(deploy_site/sitemap.xml) 불일치")

    # 5. IndexNow
    key = str(load("indexnow.json").get("key") or "")
    check(re.fullmatch(r"[a-f0-9]{16,64}", key) is not None, "indexnow.json 키 형식 오류")
    kp = OUT / f"{key}.txt"
    check(kp.exists(), f"IndexNow 키 파일 배포본 없음: {key}.txt")
    if kp.exists():
        check(read(kp).strip() == key, "IndexNow 키 파일 내용 불일치")

    print(f"가이드 {len(guides)}편 · 콘텐츠 페이지 {len(pages)}개 · sitemap {len(locs)} URL · "
          f"Article {art}개 · IndexNow {key[:8]}…")
    if fails:
        print("\n실패:")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("[verify_v48] PASS")


if __name__ == "__main__":
    main()
