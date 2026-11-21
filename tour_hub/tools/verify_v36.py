#!/usr/bin/env python3
"""v36 회귀 검증 — 트립픽 전수 점검에서 고친 것들이 다시 어긋나지 않는지 확인한다.

`python3 build.py && python3 build_pages.py --out ../deploy_site --base https://trippick.pages.dev --check-links`
를 먼저 실행한 뒤 이 파일을 돌린다(내부 링크 전수 검사는 build_pages.py --check-links 가 담당).

검사 항목
 1. 데이터 개수(투어·도시·가이드·찐숙소·지역·맛집·필수품)와 허브 페이지·메타 설명에 적힌 숫자 일치
 2. /about 의 숫자가 데이터에서 계산된 값인지(토큰이 남아 있지 않은지)
 3. 404.html 의 모든 href·src 가 루트 절대 경로인지(중첩 주소에서도 CSS·JS·메뉴가 살아야 함)
 4. 모든 페이지의 og:image:width/height 존재, og:image 가 세로 이미지가 아닌지
 5. sitemap.xml 의 URL 이 실제 페이지와 1:1인지
 6. 제휴 링크(rel=sponsored)의 빈 href·트립닷컴 필수 파라미터 누락 여부
 7. 찐숙소 지역의 `top`(최고 평점)이 실제 최고점 숙소인지
 8. 인라인 스크립트 문법(esprima 가 있을 때)
"""
import json
import os
import re
import sys
from pathlib import Path

from PIL import Image
import lxml.html as LH

ROOT = Path(__file__).resolve().parent.parent      # tour_hub/
DATA = ROOT / "data"
OUT = (ROOT / "../deploy_site").resolve()
BASE = "https://trippick.pages.dev"
fails = []


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def check(cond, msg):
    if not cond:
        fails.append(msg)


def page_url(p: Path) -> str:
    rel = os.path.relpath(p, OUT)
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel[: -len(".html")]


def main():
    tours = load("tours.json")
    stays = load("stays.json")
    rest = {c["id"]: c for c in load("restaurants.json")["cities"]}
    gifts = {c["id"]: c for c in load("gifts.json")["countries"]}
    hubs = load("city_hubs.json")["cities"]
    guides = load("guides.json")["guides"]
    ess = load("essentials.json")["products"]
    tripcom = load("tripcom.json")

    print(f"데이터: 투어 {len(tours['tours'])} · 도시 {len(tours['cities'])} · 가이드 {len(guides)} · "
          f"찐숙소 {len(stays['hotels'])} · 지역 {len(stays['regions'])} · "
          f"맛집 {sum(len(c['items']) for c in rest.values())} · 필수품 {len(ess)}")

    # 1. 허브 페이지·메타 숫자
    for h in hubs:
        slug = h["slug"]
        f = OUT / f"{slug}.html"
        if not f.exists():
            check(False, f"허브 페이지 없음: {slug}.html")
            continue
        doc = LH.fromstring(f.read_text(encoding="utf-8"))
        txt = re.sub(r"\s+", " ", doc.text_content())
        n_tour = sum(1 for t in tours["tours"] if t["city"] in set(h["cityIds"]))
        n_stay = sum(1 for x in stays["hotels"] if x["region"] == slug)
        n_guide = len(h.get("guides") or [])
        n_rest = len((rest.get(h.get("restaurants")) or {}).get("items", []))
        n_gift = len((gifts.get(h.get("giftCountry")) or {}).get("items", []))
        pairs = [
            (r"투어·패키지 (\d+)개", n_tour, "투어"),
            (r"찐숙소 (\d+)곳", n_stay, "찐숙소"),
            (r"관련 가이드 (\d+)편", n_guide, "가이드"),
        ]
        for pat, exp, label in pairs:
            m = re.search(pat, txt)
            if m:
                check(int(m.group(1)) == exp, f"{slug}: 페이지 {label} {m.group(1)} ≠ 데이터 {exp}")
        md = h["metaDesc"]
        meta_pairs = [
            (r"투어·패키지 (\d+)개", n_tour, "투어"),
            (r"상품 (\d+)개", n_tour, "상품"),
            (r"숙소 (\d+)곳", n_stay, "숙소"),
            (r"(?:관련 )?가이드 (\d+)편", n_guide, "가이드"),
            (r"맛집 (\d+)곳", n_rest, "맛집"),
            (r"선물 (\d+)종", n_gift, "선물"),
            (r"기념품 (\d+)종", n_gift, "기념품"),
        ]
        for pat, exp, label in meta_pairs:
            m = re.search(pat, md)
            if m:
                check(int(m.group(1)) == exp, f"{slug}: 메타 {label} {m.group(1)} ≠ 데이터 {exp}")

    # 2. /about 숫자
    about = (OUT / "about.html").read_text(encoding="utf-8")
    check("{{" not in about, "about.html 에 치환되지 않은 토큰이 남아 있음")
    for token, exp in [("{{TOURS}}", len(tours["tours"])), ("{{GUIDES}}", len(guides))]:
        check(token not in about, f"about.html 에 {token} 이 남아 있음")
    stats = re.search(r'<div class="about-stats">(.*?)</div>\s*</div>', about, re.S)
    if stats:
        nums = re.findall(r"<b>([\d,]+)</b>", stats.group(1))
        check(nums and nums[0] == f"{len(tours['tours']):,}",
              f"about 통계 첫 값 {nums[:1]} ≠ 투어 {len(tours['tours'])}")

    # 3. 404 절대 경로
    nf = (OUT / "404.html").read_text(encoding="utf-8")
    for attr, val in re.findall(r'(href|src)="([^"]*)"', nf):
        if re.match(r"^(?:[a-z][a-z0-9+.\-]*:|//|/|#)", val, re.I):
            continue
        check(False, f"404.html 상대 경로: {attr}=\"{val}\"")

    # 4. og:image 메타·가로 비율
    pages = [p for p in sorted(OUT.rglob("*.html"))
             if not p.name.startswith(("google", "naver"))]
    for p in pages:
        doc = LH.fromstring(p.read_text(encoding="utf-8"))
        og = doc.xpath('//meta[@property="og:image"]/@content')
        if not og:
            check(False, f"{page_url(p)}: og:image 없음")
            continue
        w = doc.xpath('//meta[@property="og:image:width"]/@content')
        hh = doc.xpath('//meta[@property="og:image:height"]/@content')
        check(bool(w and hh), f"{page_url(p)}: og:image:width/height 없음")
        fp = OUT / og[0].replace(BASE + "/", "")
        if fp.exists() and not fp.name.endswith(".svg"):
            iw, ih = Image.open(fp).size
            check(ih <= iw * 1.05, f"{page_url(p)}: og:image 가 세로 이미지 {iw}×{ih}")
    print(f"페이지 {len(pages)}개 og:image 메타 검사")

    # 5. sitemap 1:1
    sm = (OUT / "sitemap.xml").read_text(encoding="utf-8")
    locs = [u.replace(BASE, "") or "/" for u in re.findall(r"<loc>([^<]+)</loc>", sm)]
    check(len(locs) == len(set(locs)), "sitemap URL 중복")
    actual = {page_url(p) for p in pages if p.name != "404.html"}
    check(set(locs) == actual, f"sitemap 불일치 — sitemap만 {sorted(set(locs)-actual)[:3]} / 페이지만 {sorted(actual-set(locs))[:3]}")
    print(f"sitemap {len(locs)} URL")

    # 6. 제휴 링크
    sponsored = 0
    for p in pages:
        doc = LH.fromstring(p.read_text(encoding="utf-8"))
        for a in doc.xpath('//a[contains(@rel,"sponsored")]'):
            href = (a.get("href") or "").strip()
            sponsored += 1
            if not href.startswith("https://"):
                check(False, f"{page_url(p)}: 제휴 링크가 https 가 아님 {href[:40]}")
                continue
            if re.search(r"(todo|0000|example\.com|undefined|null)", href, re.I):
                check(False, f"{page_url(p)}: 자리표시자 제휴 링크 {href[:60]}")
            if "trip.com" in href:
                for key in ("Allianceid", "SID", "trip_sub3"):
                    check(key in href, f"{page_url(p)}: 트립닷컴 링크에 {key} 없음 {href[:60]}")
    print(f"제휴 링크 {sponsored}개 검사")

    # 7. 찐숙소 최고 평점
    for r in stays["regions"]:
        hs = [x for x in stays["hotels"] if x["region"] == r["id"]]
        if not hs:
            continue
        best = max(hs, key=lambda x: (x["score"], x["reviews"]))
        check(r.get("top") == best["name"],
              f"stays {r['id']}: top '{r.get('top')}' ≠ 최고 평점 {best['name']} ({best['score']})")

    # 8. 인라인 스크립트 문법
    try:
        import esprima
    except ImportError:
        esprima = None
    if esprima:
        n = 0
        for p in pages:
            doc = LH.fromstring(p.read_text(encoding="utf-8"))
            for s in doc.xpath("//script[not(@src)]"):
                if (s.get("type") or "") in ("application/ld+json", "application/json"):
                    continue
                body = s.text or ""
                if not body.strip():
                    continue
                n += 1
                try:
                    esprima.parseScript(body)
                except Exception:
                    try:
                        esprima.parseModule(body)
                    except Exception as e:
                        check(False, f"{page_url(p)}: 인라인 스크립트 문법 오류 {str(e)[:80]}")
        print(f"인라인 스크립트 {n}개 문법 검사")

    if fails:
        print("\n실패", len(fails))
        for f in fails[:40]:
            print(" -", f)
        return 1
    print("\n모든 검사 통과")
    return 0


if __name__ == "__main__":
    sys.exit(main())
