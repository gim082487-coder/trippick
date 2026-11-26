#!/usr/bin/env python3
"""v44 회귀 검증 — /sos 「여행 중 위기상황 SOS」 + 새 가이드 3편 + 진입점.

`python3 build.py && python3 build_pages.py --out ../deploy_site --base https://trippick.pages.dev --check-links`
뒤에 실행한다.

검사 항목
 1. 가이드 100편(v45 이후 3편 추가) · v44 신규 3편 본문/이미지/FAQ
 2. /sos 산출물 — 10개국 탭·패널, tel: 링크(공통 2 + 국가별), 현지어 카드 60개, 화면 FAQ 5문항
 3. /sos 진입점 — 헤더 도구 드롭다운·모바일 SOS 버튼·푸터·위기상황 가이드 2편
 4. sitemap 131 URL · search_index 도구(page) 1건 · GSC action.md 131개·/sos
 5. 자산 — assets/tp-v44.js(국가 전환·큰 글씨), site.css 의 .sos- 규칙
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = (ROOT / "../deploy_site").resolve()
ACTION = ROOT.parent.parent / "scheduled-actions" / "🔍-구글-서치콘솔-색인-요청-재시도" / "action.md"
NEW = ["passport-phone-lost-emergency", "overseas-sick-hospital-insurance-claim", "travel-hacks-hotel-flight-restaurant"]
CODES = ["KR", "JP", "TH", "VN", "TW", "SG", "FR", "IT", "ES", "GB"]
fails = []


def check(ok, msg):
    if not ok:
        fails.append(msg)


def read(p):
    return p.read_text(encoding="utf-8")


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


# ---------------------------------------------------------------- 1. 가이드
guides = load("guides.json")["guides"]
check(len(guides) == 122, f"가이드 {len(guides)}편 (기대 122)")
by = {g["slug"]: g for g in guides}
for slug in NEW:
    g = by.get(slug)
    check(bool(g), f"guides.json 에 {slug} 없음")
    if not g:
        continue
    for k in ("seoTitle", "desc", "keywords", "image", "ogImage", "faq"):
        check(bool(g.get(k)), f"{slug}: {k} 없음")
    check(len(g.get("faq") or []) == 5, f"{slug}: FAQ {len(g.get('faq') or [])}문항 (기대 5)")
    src = ROOT / "content" / "guides" / f"{slug}.html"
    check(src.exists(), f"본문 없음 {slug}")
    if src.exists():
        h = read(src)
        check("<!-- @FAQ -->" in h, f"{slug}: @FAQ 마커 없음")
        page = OUT / "guides" / f"{slug}.html"
        check(page.exists(), f"빌드 결과 없음 {slug}")
        if page.exists():
            ph = read(page)
            check(ph.count('details class="fq"') == 5, f"{slug}: 화면 FAQ {ph.count('details class=\"fq\"')}개")
            check('"@type": "Question"' in ph, f"{slug}: FAQPage JSON-LD 없음")

# ---------------------------------------------------------------- 2. /sos
sos = OUT / "sos.html"
check(sos.exists(), "deploy_site/sos.html 없음")
if sos.exists():
    h = read(sos)
    for code in CODES:
        check(f'data-cc="{code}"' in h, f"/sos: 국가 탭 {code} 없음")
        check(f'data-panel-cc="{code}"' in h, f"/sos: 국가 패널 {code} 없음")
    check(h.count('class="sos-tab"') == 10, f"/sos: 탭 {h.count('class=\"sos-tab\"')}개 (기대 10)")
    check(h.count('class="sos-panel"') == 10, f"/sos: 패널 {h.count('class=\"sos-panel\"')}개 (기대 10)")
    check(h.count('class="sos-pc"') == 60, f"/sos: 현지어 카드 {h.count('class=\"sos-pc\"')}개 (기대 60)")
    tel = re.findall(r'href="tel:([^"]+)"', h)
    check(len(tel) >= 80, f"/sos: tel: 링크 {len(tel)}개 (80 이상 필요)")
    for want in ("+82232100404", "+82443200119", "110", "119", "191", "1669", "112", "999"):
        check(want in tel, f"/sos: tel:{want} 없음")
    check("tel:%237119" in h, "/sos: 일본 #7119 인코딩 링크 없음")
    check(h.count('details class="fq"') == 5, f"/sos: FAQ {h.count('details class=\"fq\"')}문항 (기대 5)")
    ld = "".join(re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S))
    for t in ('"WebPage"', '"FAQPage"', '"BreadcrumbList"'):
        check(t in ld, f"/sos: JSON-LD {t} 없음")
    check('id="sosOv"' in h and 'id="sosOvLocal"' in h, "/sos: 큰 글씨 오버레이 없음")
    check("tp-v44.js" in h, "/sos: tp-v44.js 미로드")
    check(h.count("<h1") == 1, f"/sos: h1 {h.count('<h1')}개")
    # 10개국 표(JS 꺼짐·인쇄 대비)
    check(h.count('class="sos-tb"') == 1, "/sos: 전체 번호 표 없음")
    for code in CODES:
        pass
    check(h.count("<tbody>") >= 1 and h.count("sos-tb-n") >= 40, "/sos: 표 행 부족")
    # 국가명·긴급번호 문구가 본문 텍스트로도 있는지(검색 노출)
    for txt in ("영사안전콜센터", "119 재외국민 응급의료상담", "대사관 긴급", "관광경찰"):
        check(txt in h, f"/sos: 본문에 '{txt}' 없음")

# ---------------------------------------------------------------- 3. 진입점
home = read(OUT / "index.html")
for label, h in (("홈", home), ("/sos", read(sos)) if sos.exists() else ("/sos", "")):
    check('class="nav-drop-menu"' in h, f"{label}: 도구 드롭다운 없음")
    check(re.search(r'class="nav-drop-menu">\s*<a href="(?:\.\./)?sos"', h) is not None,
          f"{label}: 도구 드롭다운 첫 항목이 /sos 아님")
    check(re.search(r'class="hd-sos" href="(?:\.\./)?sos"', h) is not None, f"{label}: 모바일 SOS 버튼 없음")
    check(re.search(r'footer[\s\S]*?href="(?:\.\./)?sos"', h) is not None, f"{label}: 푸터 /sos 링크 없음")
for slug in NEW[:2]:
    p = OUT / "guides" / f"{slug}.html"
    if p.exists():
        check('href="../sos"' in read(p), f"{slug}: /sos 콜아웃 없음")

# ---------------------------------------------------------------- 4. sitemap·색인·action
locs = re.findall(r"<loc>([^<]+)</loc>", read(OUT / "sitemap.xml"))
check(len(locs) == 161, f"sitemap {len(locs)} URL (기대 161)")
check("https://trippick.pages.dev/sos" in locs, "sitemap 에 /sos 없음")
idx = json.loads(read(OUT / "search_index.json"))
items = idx.get("items") or []
pages = [it for it in items if it.get("k") == "page"]
check(len(pages) == 1 and pages[0]["u"] == "/sos", f"search_index 도구 항목 {pages[:2]}")
if ACTION.exists():
    act = read(ACTION)
    check(act.startswith("---\ntitle:"), "action.md 프론트매터가 맨 앞에 없음")
    check("147개" in act, "action.md 사이트맵 기준 수(147개) 미갱신")
    check("https://trippick.pages.dev/sos" in act, "action.md 에 /sos URL 없음")
    for slug in NEW:
        check(f"https://trippick.pages.dev/guides/{slug}" in act, f"action.md 에 {slug} URL 없음")
else:
    fails.append(f"action.md 없음: {ACTION}")

# ---------------------------------------------------------------- 5. 자산
js = OUT / "assets" / "tp-v44.js"
check(js.exists(), "assets/tp-v44.js 없음")
if js.exists():
    s = read(js)
    for k in ("sosPanels", "sosCC", "sosOv", "trippick.sos.cc", "Escape"):
        check(k in s, f"tp-v44.js 에 {k} 없음")
css = read(OUT / "assets" / "site.css")
for k in (".sos-top", ".sos-tab", ".sos-num", ".sos-pc", ".sos-ov-big", ".hd-sos"):
    check(k in css, f"site.css 에 {k} 없음")
check("tp-v44.js" in read(OUT / "sos.html"), "/sos 에서 tp-v44.js 미참조")

print(f"가이드 {len(guides)}편 · sitemap {len(locs)} URL · /sos tel {len(tel) if sos.exists() else 0}개")
if fails:
    print("\n실패:")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("[verify_v44] PASS")
