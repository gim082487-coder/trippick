#!/usr/bin/env python3
"""v42 회귀 검증 — 찜 견적서 · 어디든지 파인더 · 싱가포르 교통패스 · 신규 가이드 3편.

`python3 build.py && python3 build_pages.py --out ../deploy_site --base https://trippick.pages.dev --check-links`
뒤에 실행한다.

검사 항목
 1. 가이드 편수·v42 신규 3편 파일·OG 이미지(1200×630)·sitemap URL
 2. 신규 3편의 본문 목차(gtoc)·FAQ 5문항·FAQPage JSON-LD·제휴 링크(https·트립닷컴 파라미터)
 3. /passes 싱가포르 패널 — 데이터(passes.json)와 화면·페이로드, v39 싱가포르 가이드 수치 일치
 4. 홈 「어디든지 파인더」 — tpFinder 데이터(도시·시즌·숙소·투어·허브 URL)와 UI 칩
 5. 찜 견적서 — 찜 데이터에 1박·1인 단가(pr·un)가 있고, tp-v43.js 에 견적·복사 기능이 있는지
 6. GSC 재시도 action.md 에 신규 3편 URL 이 들어갔고 프론트매터가 그대로인지
"""
import json
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = (ROOT / "../deploy_site").resolve()
ACTION = ROOT.parent.parent / "scheduled-actions" / "🔍-구글-서치콘솔-색인-요청-재시도" / "action.md"
NEW = ["jeju-3n4d-course-budget", "bangkok-pattaya-3n5d-course-budget", "luggage-size-weight-airline-guide"]
fails = []


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def read(p):
    return p.read_text(encoding="utf-8")


def check(ok, msg):
    if not ok:
        fails.append(msg)


# ---------------------------------------------------------------- 1. 편수·파일·OG·sitemap
guides = load("guides.json")["guides"]
by = {g["slug"]: g for g in guides}
EXPECT_GUIDES = len(guides)
check(len(guides) >= 88, f"가이드 {len(guides)}편 (기대 88편 이상)")
for slug in NEW:
    g = by.get(slug)
    check(g is not None, f"guides.json 에 {slug} 없음")
    check((ROOT / "content" / "guides" / f"{slug}.html").exists(), f"본문 없음: {slug}.html")
    check((OUT / "guides" / f"{slug}.html").exists(), f"배포본 없음: {slug}.html")
    if g:
        check(len(g.get("faq") or []) == 5, f"{slug}: FAQ {len(g.get('faq') or [])}문항 (기대 5)")
        for key in ("image", "ogImage", "seoTitle", "desc", "keywords"):
            check(bool(g.get(key)), f"{slug}: {key} 없음")
        og = OUT / (g.get("ogImage") or "")
        if og.exists():
            w, h = Image.open(og).size
            check((w, h) == (1200, 630), f"{slug}: OG {w}×{h} (기대 1200×630)")
        else:
            fails.append(f"{slug}: OG 파일 없음 {og}")
        hero = OUT / (g.get("image") or "")
        if hero.exists():
            w, h = Image.open(hero).size
            check(w == 1200 and h == 800, f"{slug}: 히어로 {w}×{h} (기대 1200×800)")

sm = read(OUT / "sitemap.xml")
locs = re.findall(r"<loc>([^<]+)</loc>", sm)
# 사이트맵에 들어가는 실제 페이지 수와 1:1인지. deploy_site 에는 noindex 인 404.html 과
# 검색엔진 소유확인용 정적 파일(google….html·naver….html)이 같이 있어서 그것만 뺀다.
_html_pages = [
    p for p in OUT.glob("**/*.html")
    if p.name != "404.html" and not re.fullmatch(r"(?:google|naver)[0-9a-f]+\.html", p.name)
]
check(len(locs) == len(_html_pages), f"sitemap {len(locs)} URL · 실제 페이지 {len(_html_pages)}개 (불일치)")
for slug in NEW:
    check(f"/guides/{slug}" in sm, f"sitemap 에 /guides/{slug} 없음")

# ---------------------------------------------------------------- 2. 신규 가이드 페이지
sponsored_by_guide = {}
for slug in NEW:
    html = read(OUT / "guides" / f"{slug}.html")
    check('class="gtoc"' in html, f"{slug}: 본문 목차(gtoc) 없음")
    check(html.count('<details class="fq">') == 5, f"{slug}: 화면 FAQ {html.count('<details class=\"fq\">')}개 (기대 5)")
    m = re.search(r'<script type="application/ld\+json">(\{"@context": "https://schema.org", "@type": "FAQPage".*?)</script>', html, re.S)
    check(bool(m), f"{slug}: FAQPage JSON-LD 없음")
    if m:
        try:
            faq = json.loads(m.group(1))
            check(len(faq.get("mainEntity") or []) == 5, f"{slug}: FAQPage 문항 {len(faq.get('mainEntity') or [])}")
        except ValueError as e:
            fails.append(f"{slug}: FAQPage JSON 파싱 오류 {e}")
    hrefs = re.findall(r'<a [^>]*rel="noopener sponsored"[^>]*href="([^"]+)"', html)
    hrefs += re.findall(r'<a [^>]*href="([^"]+)"[^>]*rel="noopener sponsored"', html)
    hrefs = [h.replace("&amp;", "&") for h in hrefs]
    sponsored_by_guide[slug] = hrefs
    check(len(hrefs) >= 3, f"{slug}: 제휴 링크 {len(hrefs)}개 (기대 3개 이상)")
    for h in hrefs:
        check(h.startswith("https://"), f"{slug}: 제휴 링크가 https 아님 {h[:50]}")
        if "trip.com" in h:
            for key in ("Allianceid", "SID", "trip_sub3"):
                check(key in h, f"{slug}: 트립닷컴 링크에 {key} 없음 {h[:60]}")
    tags = re.findall(r"trip_sub1=([a-z0-9_]+)", " ".join(hrefs))
    prefix = {"jeju-3n4d-course-budget": "jeju3n4d", "bangkok-pattaya-3n5d-course-budget": "bkk3n5d",
              "luggage-size-weight-airline-guide": None}[slug]
    if prefix:
        # 본문 하단 gacts 는 이 가이드 전용 trip_sub1 을 쓴다(카드·자동 블록은 기존 상품 링크 그대로).
        check(any(t.startswith(prefix) for t in tags), f"{slug}: 가이드 고유 trip_sub1({prefix}_*) 없음")
    else:
        check(len({h.split("/")[2] for h in hrefs}) >= 1, f"{slug}: 제휴 링크 호스트 없음")
        check(any("coupang.com" in h for h in hrefs), f"{slug}: 쿠팡 제휴 링크 없음")

# 같은 제휴 URL 을 두 가이드가 그대로 복사하지 않았는지(고유 링크)
sets = {k: set(v) for k, v in sponsored_by_guide.items()}
if len(sets) == 3:
    a, b, c = (sets[s] for s in NEW)
    check(not (a & b), f"제주·방콕 가이드 제휴 URL 중복 {list(a & b)[:2]}")
    check(not (a & c), f"제주·수하물 가이드 제휴 URL 중복 {list(a & c)[:2]}")
    check(not (b & c), f"방콕·수하물 가이드 제휴 URL 중복 {list(b & c)[:2]}")

# ---------------------------------------------------------------- 3. /passes 싱가포르
passes = load("passes.json")
sg = passes.get("singapore") or {}
check(bool(sg), "passes.json 에 singapore 없음")
if sg:
    check(abs(passes["fx"].get("SGD", 0) - 1043.25) < 0.01, f"fx.SGD {passes['fx'].get('SGD')}")
    check(abs(sg["contactless"]["feePerDay"] - 0.6) < 1e-6, "컨택트리스 하루 수수료 0.60 아님")
    check((sg["contactless"]["fareMin"], sg["contactless"]["fareMax"]) == (1.28, 2.57), "MRT 요금 1.28~2.57 아님")
    tp = {t["days"]: t["price"] for t in sg["touristPass"]}
    check(tp == {1: 17, 2: 24, 3: 29}, f"Tourist Pass {tp} (기대 17/24/29)")
    check(sg["ezlink"]["cardFee"] == 5, "EZ-Link 불환 카드값 5 아님")

# v39 싱가포르 가이드와 수치 일치
v39 = read(ROOT / "content" / "guides" / "singapore-3n4d-course-budget.html")
for token in ("1.28", "2.57", "0.60", "17 / 2일 24 / 3일 29"):
    check(token in v39, f"v39 싱가포르 가이드에 {token} 없음")
check("1,043" in v39, "v39 싱가포르 가이드 환율 1,043 없음")

page = read(OUT / "passes.html")
check('data-panel="singapore"' in page, "/passes 에 싱가포르 패널 없음")
check(page.count('class="pk-tab" data-city="singapore"') == 1, "/passes 싱가포르 탭 없음")
check(page.count("data-sg=") == 3, f"/passes 싱가포르 권종 칩 {page.count('data-sg=')}개 (기대 3)")
m = re.search(r'<script type="application/json" id="pkData">(.*?)</script>', page, re.S)
check(bool(m), "/passes pkData 없음")
if m:
    payload = json.loads(m.group(1).replace("<\\/", "</"))
    check("singapore" in payload, "pkData 에 singapore 없음")
    if "singapore" in payload:
        check(len(payload["singapore"]["touristPass"]) == 3, "pkData Tourist Pass 3종 아님")
check("SGD" in page and "0.60" in page, "/passes 화면에 싱가포르 요금/수수료 문구 없음")

# ---------------------------------------------------------------- 4. 파인더
home = read(OUT / "index.html")
check('id="find"' in home, "홈에 파인더 섹션(#find) 없음")
m = re.search(r'<script type="application/json" id="tpFinder">(.*?)</script>', home, re.S)
check(bool(m), "홈에 tpFinder 데이터 없음")
if m:
    fd = json.loads(m.group(1).replace("<\\/", "</"))
    cities = fd.get("cities") or []
    check(len(cities) >= 10, f"파인더 도시 {len(cities)}곳 (기대 10곳 이상)")
    check([s["code"] for s in fd.get("seasons") or []] == ["spring", "summer", "autumn", "winter"], "파인더 시즌 4개 아님")
    bad = []
    for c in cities:
        for key in ("id", "n", "country", "fare", "se", "stay", "tour", "hub"):
            if not c.get(key):
                bad.append(f"{c.get('id')}:{key}")
        for band in ("off", "shoulder", "peak"):
            if band not in (c.get("fare") or {}):
                bad.append(f"{c.get('id')}:fare.{band}")
        for s in ("spring", "summer", "autumn", "winter"):
            se = (c.get("se") or {}).get(s)
            if not se or se.get("band") not in ("off", "shoulder", "peak"):
                bad.append(f"{c.get('id')}:se.{s}")
        if not str((c.get("stay") or {}).get("u", "")).startswith("https://"):
            bad.append(f"{c.get('id')}:stay.u")
        if "trip_sub3=" not in str((c.get("stay") or {}).get("u", "")):
            bad.append(f"{c.get('id')}:stay.trip_sub3")
        if not str((c.get("tour") or {}).get("u", "")).startswith("https://"):
            bad.append(f"{c.get('id')}:tour.u")
        hub = str(c.get("hub") or "")
        if hub.startswith("/stays#"):
            rid = hub.split("#")[1]
            check(bool(re.search(r'data-region="%s"' % re.escape(rid), read(OUT / "stays.html"))), f"파인더 허브 {hub} 지역 없음")
        elif hub.startswith("/") and hub != "/calendar":
            slug = hub.strip("/")
            check((OUT / slug).exists() or (OUT / (slug + ".html")).exists(), f"파인더 허브 {hub} 페이지 없음")
    check(not bad, f"파인더 데이터 결함 {len(bad)}건: {bad[:5]}")
for chip in ('data-fd-season="spring"', '"summer"', '"autumn"', '"winter"', 'data-fd-season="any"',
             'data-fd-people="1"', 'data-fd-people="2"', 'data-fd-budget="b50"', '"b100"', '"b200"', '"b200p"'):
    check(chip in home, f"파인더 칩 없음 {chip}")

# ---------------------------------------------------------------- 5. 찜 견적서
stay_html = read(OUT / "stays.html")
wish_tour = re.findall(r'data-wish="tour:[^"]+" data-wish-item="([^"]*)"', home)
wish_stay = re.findall(r'data-wish="stay:[^"]+" data-wish-item="([^"]*)"', stay_html)
check(len(wish_tour) == 84 and len(wish_stay) == 171, f"찜 버튼 홈 {len(wish_tour)} · /stays {len(wish_stay)}")
badw = 0
for raw in wish_tour + wish_stay:
    d = json.loads(raw.replace("&quot;", '"').replace("&amp;", "&"))
    if not isinstance(d.get("pr"), int) or d.get("pr") <= 0 or d.get("un") not in ("1인", "1박", "1팀"):
        badw += 1
check(badw == 0, f"찜 데이터에 1박·1인 단가(pr·un) 없는 카드 {badw}개")
tu_bad = 0
tu_n = 0
for raw in wish_tour:
    d = json.loads(raw.replace("&quot;", '"').replace("&amp;", "&"))
    if "tu" in d:
        tu_n += 1
        if not str(d["tu"]).startswith("https://") or "trip_sub3=" not in str(d["tu"]):
            tu_bad += 1
check(tu_bad == 0, f"찜 투어의 트립닷컴 보조 CTA 결함 {tu_bad}건")
check(tu_n >= 20, f"트립닷컴 투어 보조 CTA 를 가진 찜 카드 {tu_n}개 (기대 20개 이상)")
check('data-wl-open' in home, "홈 헤더에 찜 버튼(data-wl-open) 없음")
js = OUT / "assets" / "tp-v43.js"
check(js.exists(), "assets/tp-v43.js 없음")
check(not (OUT / "assets" / "tp-v41.js").exists(), "구 assets/tp-v41.js 가 남아 있음")
check(not (OUT / "assets" / "tp-v42.js").exists(), "구 assets/tp-v42.js 가 남아 있음")
if js.exists():
    src = read(js)
    for token in ("trippick.wish.v1", "data-wl-copy", "data-wl-step", "wl-total", "wl-cta", "data-fd-season", "tpFinder"):
        check(token in src, f"tp-v43.js 에 {token} 없음")
    check("견적 요약 복사" in src, "tp-v43.js 에 견적 요약 복사 버튼 없음")
check("assets/tp-v43.js" in home and "assets/tp-v43.js" in stay_html, "홈·/stays 가 tp-v43.js 를 안 씀")

# ---------------------------------------------------------------- 6. GSC action.md
if ACTION.exists():
    act = read(ACTION)
    check(act.startswith("---\ntitle:"), "action.md 프론트매터가 맨 앞에 없음")
    fm = act.split("---")[1]
    check("kind: scheduled-action" in fm and "schedule:" in fm, "action.md 프론트매터 내용 변경됨")
    for slug in NEW:
        check(f"https://trippick.pages.dev/guides/{slug}" in act, f"action.md 에 {slug} URL 없음")
    check("147개" in act, "action.md 사이트맵 기준 수(147개) 미갱신")
else:
    fails.append(f"action.md 없음: {ACTION}")

print(f"가이드 {len(guides)}편 · 신규 3편 제휴 링크 " + " / ".join(f"{s.split('-')[0]} {len(v)}" for s, v in sponsored_by_guide.items()))
print(f"sitemap {len(locs)} URL · 파인더 {len((json.loads(m.group(1).replace('<\\\\/', '</')).get('cities') or [])) if m else 0}개 도시")
if fails:
    print("\n실패:")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("\n모든 검사 통과")
