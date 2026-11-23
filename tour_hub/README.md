# 트립픽 (tour_hub) — 여행 코스·가이드투어·패키지 비교 사이트 v8

네이버 여행(여행 커넥트) 상품 **49개** + 네이버 쇼핑 커넥트 국내 레저 **8개** = **57개 상품**을
**10개국 22개 도시**로 나눠, 가격·출발 공항·입장료 포함 여부·현장 추가금·취소 규정까지 같은 기준으로 비교하는 정적 웹사이트입니다.
여기에 **일차별 추천 코스 5개**(사진·동선·그날 쓸 투어/eSIM/패스 링크)와 **특가·땡처리 알림 신청 폼**이 붙어 있습니다.

- 운영 주소: https://trippick.pages.dev (Netlify 무료 호스트)
- 모바일 미리보기 하네스: `_preview390.html` (390px iframe + 가로 넘침 측정)
- 기준일: 2026-11-16 (여행 커넥트) / 2026-11-17 (부산·강원 쇼핑 커넥트 레저) / 2026-11-19 (v19 신규 상품 24종·클룩)

## v47 (2026-11-24) — Core Web Vitals CLS · sitemap 날짜 자동화 · 애드센스 점검
1. **CLS 원인 3가지와 수정** — ① `cdn.jsdelivr.net` Pretendard 스타일시트가 `assets/site.css` 앞에서 렌더를 막아, 하위 페이지가 스타일 없이 먼저 그려졌습니다(데스크톱 `/stays` CLS 0.338). → 폰트 CSS·woff2 92개 청크를 `assets/fonts/`로 자체 호스팅하고 `site.css` 다음에 둡니다. ② 폰트 교체(FOUT) 때 긴 리드 문단의 줄 수가 바뀌어 28px씩 밀렸습니다. → `@font-face "Pretendard Fallback"`에 실측 비율 `size-adjust:93.1%`(Pretendard 16,155 : Noto Sans KR 17,355)를 걸어 대체 폰트 폭을 맞춥니다(폰트는 그대로 Pretendard 사용). ③ 홈 `#fdList` 파인더 결과와 내 여행 D-Day 띠가 JS로 뒤늦게 삽입되어 아래 콘텐츠를 밀었습니다. → 파인더 기본 상태(이번 달 시즌·2인·100~200만원)를 `build.py: finder_default_view()`로 서버에서 먼저 렌더(모바일 홈 CLS 0.078→0), D-Day 띠는 흐름에서 빼고 화면 아래 고정 필로 바꿉니다(재방문 CLS 0.027~0.144→0).
2. **측정** — 1280·390, 14개 페이지 × 신규/재방문 시나리오에서 CLS: 모바일 전부 0.000, 데스크톱 0.001 이하(재방문 `/quiz` 0.061·`/checklist` 0.074는 D-Day 카드가 저장 상태로 바뀌며 생기는 값). 수정 전 라이브: 데스크톱 `/stays` 0.338, 모바일 홈 0.078.
3. **sitemap `<lastmod>` 자동화** — `build_pages.py`의 `TODAY = date(2026,11,22)`·`build.py`의 `lastmod = "2026-11-20"` 하드코딩을 없애고 실행 시점 KST(`datetime.now(ZoneInfo("Asia/Seoul"))`)를 씁니다. 가이드 최종 검증일·`sitemap.xml` 128 URL 이 같은 날짜로 나옵니다.
4. **애드센스 점검** — `/_mp`·`/mp`는 `_redirects`의 301 정리(의도된 것)이고 내부 잔재 링크는 0건. 구 미리보기 `/v17m`·`/v18m`(+`.html`) 404도 같은 방식으로 홈 301에 추가했습니다. `/about`·`/privacy`·`/terms`·`/contact` 푸터 링크 131페이지 전부, `ads.txt` 1줄(`pub-9563082990728787`), 로더·`google-adsense-account` 메타 128페이지 확인.
5. **캐시 버전** — `CSS_V 44`, `JS_V43 3`(홈 템플릿 `tp-v43.js?v=3` 도 함께). 폰트는 `assets/fonts/pretendard.css`(원본 CSS의 url()만 로컬 경로로 치환).

## v19 (2026-11-19) — 신규 상품 24종(쿠팡 6 · 트립닷컴 휴양지 16 · 네이버 패키지 2) + 클룩 3
1. **쿠팡 여행필수템 6종** (`data/essentials.json`, `category: "여행필수템"`) — 홈 `#essentials` 새 그룹 '🎒 출발 전 필수템'과 `/baggage#esspack`에 같은 데이터로 나옵니다. 65W GaN 충전기(13,890) · 디지털 캐리어 저울(5,390) · 접이식 보스턴백(12,900) · 샤워기 필터(14,900) · 3단 우양산(24,900) · IPX8 방수팩(9,900). 썸네일은 `assets/ess/cp-*.jpg`(400×400, 쿠팡 상품 이미지).
2. **트립닷컴 휴양지 8곳** (`data/tripcom.json` 의 `resorts`) — 나트랑·푸꾸옥·싱가포르·홍콩·발리·세부·코타키나발루·치앙마이. 도시 허브 없이 홈 `#tcResorts`(탭 '휴양지 8곳')와 `/cities` 하단 카드에서 **입장권·공항픽업 두 링크**로 바로 연결합니다. `tickets`/`transfers` 배열과 섞지 않았습니다(도시 허브가 없는 도시라 필터·허브 렌더를 건드리지 않으려고).
3. **네이버 여행 커넥트 패키지 2종** (`data/packages.json`) — 홍콩/마카오 5일 630,403원 · 나트랑/달랏 5일 759,050원. 홈 `#packages`(v19 신규 섹션)에만 두고 투어 비교표에는 넣지 않습니다(미팅·취소 조건 데이터가 없음). 카드 하단 여행 커넥트 고지 필수.
4. **클룩 3종** (`data/klook.json`, aid=144067) — 오사카·도쿄·다낭. 홈 `#tcKlook`과 해당 도시 허브 `#klook`에 '클룩에서 보기' 카드로 들어갑니다. USJ·디즈니·팀랩처럼 트립닷컴 단건 딥링크가 안 되는 입장권을 보완하는 역할입니다. `about`/`terms`/`privacy` 제휴 표·문구에 클룩을 추가했습니다.
5. **검증** — 쿠팡 6건·트립닷컴 16건·네이버 2건·클룩 3건 HTTP/리다이렉트 확인(2026-11-19), 내부 링크 5,014개 실패 0, JS 229·JSON 113 블록 구문 검사 통과, 1280·390 가로 넘침 0, sitemap 62 URL 유지.

## v9 (2026-11-18) — 가이드 36편 · 출국 준비 체크리스트 · 트립닷컴 필터
1. **가이드 12편 추가 → 총 36편**. 추가 주제: 스페인·포르투갈 9일 vs 11일, 서유럽 4개국 10일 실지출, 미서부 4대캐년, 미동부·캐나다 10일(항공사 차이), 호주·뉴질랜드 ETA/NZeTA, 다낭 54홀 vs 푸꾸옥 36홀, 나트랑 달랏 투어 vs 자유여행, 장가계 특별약관, 도쿄 4일 vs 3일(인천·부산), 제주 패키지 3종 vs 에어카텔, 하와이 하얏트 vs 쉐라톤, 보조배터리·액체류 기내 규정. 모든 숫자는 `data/tours.json`·`planner.json` 실제 값에서 계산했고 `related`를 양방향으로 연결했습니다. 카테고리 '중국' 신설.
2. **출국 준비 체크리스트·입국서류 계산기 `#checklist`** — 나라 8개(일본·베트남·태국·대만·미국·유럽·호주/뉴질랜드·국내)별 입국서류·수수료(Visit Japan Web, ESTA $40.62, 영국 ETA £20, 호주 ETA AUD20, NZeTA NZD117~123, 베트남 e-visa $25, 태국 TDAC, 대만 TWAC), 기내반입 규정, 체크박스(localStorage 저장), mAh→Wh 계산기, eSIM·어댑터·보조배터리·트립닷컴 딥링크. 데이터 원본은 `data/checklist.json`.
3. **트립닷컴 숙소 필터·지역 딥링크** — `#tripcom`에 전체/가성비/가족·리조트/공항 이동 편한 곳/항공권 필터 탭. 지역 섹션마다 '🏨 도시 숙소·항공' 버튼을 넣어 누르면 해당 도시 카드로 이동·강조. 기존 21개 제휴 링크는 그대로.
4. **sitemap 42 URL** (홈 1 + 가이드 인덱스 1 + 가이드 36 + 신뢰 페이지 4).

## v8 (2026-11-18) — 가이드 24편 · 광고 슬롯 · 정적 배포본 분리
1. **가이드 12편 추가 → 총 24편** (`content/guides/*.html` + `data/guides.json`). 추가 주제: 나리타·하네다 공항→시내, 교토 버스투어 vs 자유일정, 비에이 겨울 투어·눈축제, 간사이공항→USJ 이동, 오사카 2박3일 패키지, 울릉도·독도 2박3일, 강릉 당일치기, 방콕 3박5일 3상품 실지출, 베트남 eSIM, 타이베이 예스진지, 괌 리조트 3곳, 이탈리아 9일 3상품.
   모든 금액은 `data/planner.json`의 기준환율(JPY100 940 · USD 1,420 · EUR 1,620 · TWD 44 · VND100 5.5)로 환산해 계산기·카드와 일치시켰습니다.
2. **광고 슬롯** — 홈 3곳(`build.py: ad_slot()` + `template.html`의 `@AD_SLOT_1~3` 마커), 가이드 페이지당 3곳(상단·본문 중간·하단, `build_pages.py: ad_slot()`·`inject_mid_ad()`). 애드센스 승인 전에는 `<ins>` 없이 **내부 추천 배너**만 보이고, 주석을 풀고 `ca-pub-…`/`data-ad-slot`만 넣으면 켜집니다(`.adslot:has(ins.adsbygoogle)`로 폴백 자동 숨김).
3. **sitemap 30 URL** (홈 1 + 가이드 인덱스 1 + 가이드 24 + 신뢰 페이지 4), `/guides/` 인덱스 카테고리 6개(일본·국내·동남아·준비물·경비·대만·권·유럽·장거리).
4. **오사카 주유패스 기한 표기** — 판매 페이지에 `교환기간 2023-04-01~2024-06-30`·`사용기한 2024-06-30`·`[~2024/3/31]` 옵션명이 2026-11-18 현재도 남아 있음을 확인하고, 카드·코스 패널·약관 고지·가이드 본문 4곳에 정확한 날짜와 문의 안내를 표시(`data/essentials.json` caution, `data/courses.json` warn).
5. **배포 구조** — `deploy_site/`가 정적 배포본(197파일). Cloudflare Pages에서는 빌드 명령 없이 출력 디렉터리 `deploy_site`로 바로 서빙합니다.

## v4.1 디자인 — 토스 앱의 UI 구조를 빌려온 리뉴얼 (색은 트립픽 브랜드)
- **구조**: 회색 캔버스(`#F4F6F8`) 위에 흰 라운드 카드(20~24px). 얇은 테두리·그림자 최소화, 섹션 배경은 투명.
- **색**: 토스 블루를 복제하지 않고 여행 브랜드 톤 유지 — 딥네이비 `#10202E`(제목·선택 탭), 오션블루 `#0F5C97`(주요 버튼·링크, hover `#0B4A7C`), 보조 `#4B5C6B`, 캡션 `#8A98A6`, 할인 `#C9503C`, 히어로 포인트 `#E9C08B`(모래색).
- **타이포·숫자**: 제목은 굵고 짧게(자간 -0.045em), 상품 가격 25px·계산기 총액 30px·`tabular-nums`, 보조 정보는 12~13px 회색.
- **1탭 행동**: 카드 CTA 48px 오션블루 버튼, 계산기 결과 아래 큰 총액 → 상품 행 링크, 비교 바는 흰 플로팅 바 + 파란 '나란히 비교'.
- **배지 정리**: 이미지 위 보조 배지(노쇼핑·출발확정)를 없애고 스펙 칩으로 옮김. 유형 필터는 '유형 / 특성' 2줄 그룹으로 고정.
- **모바일**: 히어로 408px(카드형), 카테고리 2×2, 검색 1줄, 필터는 가로 스크롤 1줄, 계산기 스타일 칩 2×2, 버튼 최소 44~54px.

## v4에서 달라진 것 (전환율·비교·SEO)
1. **예산 계산기 `#planner`** — 인원(1~6) × 지역(국내/일본/동남아·중화권/유럽·미주) × 스타일(가성비 자유·노쇼핑 프리미엄·가족·효도·액티비티) 16조합 × 상품 3안. 상품가 + 상세페이지에 적힌 **필수 현장 추가금** + 붙인 eSIM·패스(1인 1개, 공항픽업은 차량 1대)를 합산해 1인·총액을 즉시 계산하고, 항공·숙소 포함 여부와 매칭 코스 링크를 함께 보여준다. 조합 선택 로직과 표시 금액은 `data/planner.json` + `build.py:style_score()`가 원본.
2. **상품 3개 비교 바구니** — 카드마다 '비교' 버튼, 최대 3개. 하단 고정 바 → 표로 1인 상품가·현장 추가금(근거 포함)·**실질 1인가(최저 표시)**·항공·숙소 포함·출발지·소요·쇼핑 횟수·취소 규정·포함 내역·예약 링크를 나란히 비교.
3. **검색 유입 FAQ 8개 + FAQPage 구조화 데이터** — "오사카 3박4일 총경비", "부산 요트 드론쇼 취소", "패키지 현지 추가금 계산법", "노쇼핑 구분", "취소 규정 차이", "최소 출발 인원", "eSIM 며칠짜리", "커넥트 수수료" — 답변 숫자는 `data/tours.json`·`essentials.json` 실제 값에서 계산. 화면 문구와 JSON-LD `mainAnswer`가 같은 원본(`data/faq.json`)을 쓴다.
4. **현장 추가금 실질가 노출** — 카드 가격 아래 "현장 추가금 포함 실질 N원", 스펙 칩 "현장 +N원"(툴팁에 근거). `data/planner.json`의 `extras`가 상품별 금액·근거·별도 항목을 갖는다.
5. **UX 정리** — 상품 1개뿐인 도시는 가로형 카드(2칸)로, 4개 도시는 비교 타일이 2칸을 채워 빈 칸 제거. 모바일에서 도시 칩 가로 스크롤, FAQ 아코디언, 비교 모달은 표만 내부 스크롤(본문 가로 넘침 0).
6. **SEO** — FAQPage 추가(WebSite + 코스 ItemList + FAQPage + 상품 ItemList), hero 기준일 "2026.11.16~17"로 통일, canonical·OG·JSON-LD·robots·sitemap 모두 `https://trippick.pages.dev` 기준.

## v3에서 달라진 것
1. **상단 카테고리 재구성** — 히어로 아래 4개 카드(추천 코스 · 지역/투어 · 필수품 · 특가 알림) + 야놀자/여기어때식 퀵 아이콘 바(sticky)
2. **추천 코스 우선 노출** — 5개 코스(오사카·교토, 도쿄·후지, 다낭·호이안, 삿포로·홋카이도, 제주 2박3일) 매거진형 패널. 코스별 대표컷 + 일차 사진 + "왜 이 코스인가" + 일차별 제휴 링크
3. **지역 구분 강화** — 국가 탭(카운트) → 도시 칩(플래그 + 상품 수) → 상품 유형 칩(레저·액티비티 신설) → 정렬, 전부 즉시 필터
4. **국내 확장** — 제주 2박3일 코스, 제주 3 / 울릉도·독도 1 / 부산 4 / 강원 4 상품. 부산·강원은 쇼핑 커넥트(스마트스토어) 링크
5. **타이포그래피** — Pretendard Variable(CDN dynamic subset) + 시스템 폰트 fallback, 제목 자간 -0.025~-0.035em, 가격 `tabular-nums`
6. **SEO** — 키워드 title/description, canonical, OG/Twitter, JSON-LD(WebSite + 코스 ItemList + 상품 ItemList 57), robots.txt, sitemap.xml(14 URL)
7. **빌드 방식** — `template.html`(셸·CSS·JS) + `build.py`(데이터 치환). `--check`(마커·결과 비교), `--out 파일`(index.html 유지한 미리보기 빌드)

## 디렉터리
```
tour_hub/
├── index.html            ← 생성 산출물 (배포 대상, 직접 수정 금지)
├── template.html         ← 셸·CSS·JS 원본 (스타일/마크업 수정은 여기서)
├── build.py              ← template.html + data/*.json → index.html / sitemap.xml
├── robots.txt
├── data/
│   ├── tours.json        ← 상품 원본 (57개 + 도시 22곳)
│   ├── courses.json      ← 추천 코스 5개 (일차별 일정·링크)
│   ├── essentials.json   ← 여행 필수품 22개 (여행용품 8 = 쿠팡 파트너스 · eSIM·패스·픽업·입장권 14 = 네이버 커넥트)
│   ├── tripcom.json      ← 트립닷컴 파트너스 숙소 15개 도시 · 항공 6개 노선 (v7)
│   └── photo_credits.json← Pexels 사진 출처
├── images/               ← 상품 썸네일(_sm), 코스 사진(courses/), 국내 썸네일(n_*)
├── assets/ess/           ← 쿠팡 파트너스 여행용품 썸네일 8장 (400x400, 쿠팡 상품 이미지)
├── index_v2_backup.html  ← v2 산출물 백업 (참고용)
└── README.md
```

## 빌드
```bash
cd tour_hub
python3 build.py                 # index.html / sitemap.xml 재생성
python3 build.py --check         # 현재 index.html 과 같은지 확인
python3 build.py --out _preview.html   # index.html 을 건드리지 않고 미리보기 빌드
```
`tour_hub/`가 원본입니다. 배포(Netlify)는 호스트 이전 작업에서 `tour_hub/` 산출물을 그대로 올리며,
`index.html`은 생성물이라 직접 수정하지 않습니다.

## 제휴·고지 원칙
- 상단 고지 3줄 고정 (쿠팡 → 여행 커넥트 → 쇼핑 커넥트 순):
  - `이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.` (여행용품 8종 링크)
  - `이 포스팅은 네이버 여행 커넥트 활동의 일환으로, 예약 발생 시 수수료를 제공받습니다...`
  - `이 포스팅은 네이버 쇼핑 커넥트 활동의 일환으로, 판매 발생 시 수수료를 제공받습니다.`
- 쿠팡 파트너스 고지 문구는 **공정위 문구 그대로**를 3곳에 둔다: 상단 고지바 · 필수품 섹션(쿠팡 그룹 카드 바로 아래 `ess-cp-note`) · 푸터 '제휴 및 대가성 고지'(+ about/terms/privacy)
- **아고다 특약 1.5.2 준수**: 숙소 요금 비교표 없음. 코스 패널의 '숙소 추천 지역' 가이드만 유지
- **쇼핑 커넥트 수수료율은 사이트에 하드코딩하지 않음** (판매자 설정으로 매월 변동, 렌탈·정기구독 주문은 실적 제외)
- 국내 패키지(제주·울릉)는 정상가만 노출(할인율 임의 표기 없음), 부산·강원 레저는 판매처 표시 할인율을 그대로 사용
- 제휴 링크: 네이버 `naver.me` 단축 링크 **71개 고유**(여행 49 + 레저 8 + 필수품 14) + 쿠팡 파트너스 `link.coupang.com/a/…` **8개**(여행용품). 모두 `target="_blank" rel="noopener sponsored"`

## 검증 기록 (2026-11-17, v4)
- naver.me 71개 전부 HTTP 200
- `robots.txt` / `sitemap.xml` / OG 이미지(2000×1125) HTTP 200
- 모바일 390: `innerWidth 390 / scrollWidth 375 / body 375` — 가로 넘침 0 (비교표만 컨테이너 내부 스크롤)
- 깨진 이미지 0 (`document.images` naturalWidth=0 → 0건), 실패 리소스 0
- JSON-LD 파싱 정상 (WebSite 1 + 코스 ItemList 5 + FAQPage 8 + 상품 ItemList 57), h1 1개
- 계산기 16조합 × 인원 1~6 경계: 조합 3안·총액·행 모두 정상, JS 오류 0
- 비교 바구니: 3개 담기 → 4번째 거부(토스트), 모달 표 10행 × 3열, ESC 닫힘, '비우기' 동작
- 가로 넘침 0: 390 / 768 / 1024 / 1280 / 1440 모두 `scrollWidth == innerWidth`
- 스크린샷: `screenshots_trippick/v4/` (데스크톱 12장 + 모바일 390 7장)
- 검증 메타: google-site-verification 2개(LcZm…, Y3lr…) + naver-site-verification 2개(de9b42…, ab10e6…) 유지. Netlify 루트의 `naver1a2e72ce656ca4889c08fec3050b4703.html` 필요.

## 데이터 갱신 시
`data/planner.json` — `extras`(상품별 현장 추가금 `krw`·`basis`·`aside`·`partial`), `regions`, `styles`, `fx`(환율 기준), `courseByCity`.
`data/faq.json` — FAQ 문항·답변·보조 목록. `{TOTAL}` `{NOSHOP}` `{MINPAX_KNOWN}` 같은 토큰은 `build.py`가 치환합니다.

`data/tours.json` 의 상품 객체 필드: `id, city, title, seller, price(정가), sale(판매가), url, label, type, guide, duration, meeting, meetingTime, includes, excludes, extraFees[], minPax, maxPax, cancel, cancelDays, rating, reviews, booked, caution, fee, affiliate`
- `caution`: 카드에 경고문으로 노출(예: "드론쇼는 날씨에 따라 취소될 수 있습니다", "전화 문의·날짜 확정 필수")
- `affiliate: "shopping-connect"` 이면 CTA가 "네이버에서 구매"로 바뀜

## 가이드·필수 페이지 (2026-11-17, v5)

`build_pages.py` 가 index.html 외의 페이지를 만듭니다. **`build.py` 다음에 실행**하세요(둘 다 `sitemap.xml`을 쓰므로 순서가 중요합니다. v5부터 `build.py`의 `render_sitemap()`도 `data/guides.json`의 URL을 함께 씁니다).

```bash
python3 build.py                       # index.html + sitemap.xml(가이드 포함)
python3 build_pages.py                 # about/contact/privacy/terms + guides/ + assets/site.css + sitemap.xml
python3 build_pages.py --check-links   # 내부 링크·앵커 전수 검사(실패 0건이어야 함)
python3 build_pages.py --out ../deploy_site_gh --base https://gim082487-coder.github.io
```

- 본문 원본: `content/guides/<slug>.html`(가이드 12편), `content/pages/<slug>.html`(필수 페이지 4종) — HTML 조각만 넣으면 페이지 틀은 빌더가 씁니다.
- 메타데이터: `data/guides.json` (`slug, category, navTitle, h1, seoTitle, dek, desc, updated, read, image, tours[], essentials[], related[], fxNote`)
- 디자인: `template.html`의 `<style>` 블록을 그대로 추출해 `assets/site.css`로 저장하고 `content/pages.css`를 뒤에 붙입니다. 토큰(--blue/--ink/--soft)을 바꾸면 서브페이지도 함께 바뀝니다.
- 페이지 틀: 헤더·푸터·SVG 스프라이트를 index와 동일하게 생성하며, 푸터 '사이트 안내'에 4개 필수 페이지가 항상 들어갑니다.
- 주의: Netlify는 배포 시 내부 링크를 pretty URL(`/about`, `/guides/`)로 리라이트합니다. canonical·sitemap은 `.html` 기준이므로 두 주소 모두 200으로 응답합니다.

## 트립닷컴 파트너스 숙소·항공 (2026-11-18, v7)

`data/tripcom.json` 이 섹션의 원본입니다. 네이버·쿠팡 링크와 섞지 않고 **전용 섹션(`<section id="tripcom">`)** 하나에서만 노출합니다
(`render_tripcom()` → `<!-- @TRIPCOM -->`).

- 계정: AID `11407530` · SID `336341874` (사이트 URL `https://trippick.pages.dev` 등록). 요율은 호텔 5→6→7%(예약 건수), 국제선 항공 0.5→0.8%.
- 숙소 링크 형식: `https://kr.trip.com/hotels/list?city=<도시ID>&display=<도시명>&optionId=<도시ID>&optionType=City&optionName=<도시명>&Allianceid=11407530&SID=336341874&trip_sub1=hotel_<slug>&trip_sub3=D21275837`
- 항공 링크 형식: `https://kr.trip.com/flights/<Seoul-to-City>/tickets-SEL-<IATA>?flighttype=S&dcity=SEL&acity=<IATA>&Allianceid=…&SID=…&trip_sub1=flight_sel_<iata>&trip_sub3=D21275837`
- 링크는 반드시 파트너스 **Affiliate Link → Hotels page / Flights page** 생성기에서 발급하세요(도시 ID·영문 슬러그·`trip_sub3`가 생성기 결과값). 손으로 도시 ID를 추측하지 마세요.
- 검수: 호텔 링크는 `curl -s "<url>" | grep '<title>'` 로 도시명이 맞는지 확인(15개 전부 통과). 항공 링크는 curl이 `Challenge Validation`으로 막히므로 브라우저에서 직접 열어 제목을 확인하세요.
- 공정위·파트너스 고지는 상단 `.disclosure-bar`(트립닷컴 1줄), 섹션 하단 `ess-cp-note`, 푸터 `.disclose`, `about/terms/privacy` 4곳에 들어갑니다.

## 구조화 데이터 (2026-11-18, v7 — GSC '제품 스니펫·판매자 목록' 경고 제거)

상품 57개 JSON-LD를 `Product`+`Offer` → **`TouristTrip`**(+`provider`·`areaServed`·`touristType`)로 바꿨습니다.
트립픽은 판매 당사자가 아니라 제휴 링크를 비교하는 사이트라, `Product`로 두면 구글이 `aggregateRating`·`review`·`hasMerchantReturnPolicy`·`shippingDetails`를 요구합니다.
없는 평점·리뷰·반품정책을 지어내지 않기 위한 변경이며, **가격은 페이지 본문에만** 표시하고 구조화 데이터에는 넣지 않습니다.
`category`·`brand`·`offers`도 함께 제거했습니다. 되돌리지 마세요(되돌리면 GSC 경고가 다시 뜹니다).

## 예산 계산기 팀 단가 (2026-11-18, v7)

`data/tours.json` 상품에 `"priceUnit": "team"`(+`"priceUnitLabel"`)을 넣으면 인원수를 곱하지 않고 1팀 단가로 계산합니다
(`is_team_item()`, `plan_lines()`, `render_tp_data()`의 `ptm`/`ptl`, `template.html`의 `linesOf()`).
현재 대상: `busan_lana_private`(라나요트 단독대여 249,000원). 공항픽업은 기존대로 `category: "공항픽업"` → 차량 1대 기준.

## 쿠팡 파트너스 여행 준비물 (2026-11-17, v6)

`data/essentials.json` 의 상품에 `partner: "coupang"` 과 `url`(link.coupang.com 단축링크)을 넣으면 쿠팡 카드로 렌더됩니다.

```json
{"id":"cp-adapter-nemotab","category":"여행용품","categoryLabel":"해외 멀티어댑터",
 "name":"네모탭 해외여행용 멀티어댑터 PD35W 5포트","officialName":"(쿠팡 원문 상품명)",
 "store":"쿠팡","partner":"coupang","price":12900,"listPrice":28000,
 "url":"https://link.coupang.com/a/…","productId":"8220548823",
 "image":"assets/ess/cp-adapter-nemotab.png"}
```

- `category: "여행용품"` 그룹은 `ESS_GROUPS` 첫 항목이며, `ess-grid-4`(4열)로 렌더되고 썸네일(`.ess-thumb`)이 붙습니다.
- 링크·CTA는 `ess_url()`/`ess_cta()` 헬퍼가 고릅니다(쿠팡=`url`+"쿠팡에서 구매", 네이버=`naverMe`+"네이버에서 구매"). `naverMe`를 직접 참조하는 곳은 없어야 합니다.
- 공정위 고지 문구는 그룹 카드 아래 `ess-cp-note`, 상단 `.disclosure-bar`, 푸터 `.disclose` 3곳에 들어갑니다. 문구를 바꿀 때는 세 곳을 함께 고치세요.
- 썸네일은 쿠팡 상품 이미지(400x400)를 `assets/ess/`에 내려받아 씁니다. 핫링크하지 않습니다.
- 링크를 새로 발급하면 `productId`로 상품을 대조하세요: `curl -s https://link.coupang.com/a/XXXX | grep productId`

## v17 (2026-11-19) — 고요율 eSIM 8종 · 오래 쓰는 여행 장비 6종

### 1. eSIM (네이버 쇼핑 커넥트, `category: "eSIM"`)

- 신규 8건: 일본 2(유심사 KDDI 1일 300원 · 도쿄·오사카 3일 14,620원), 베트남 2(링심 1일 800원·유심사 푸꾸옥·나트랑 3일 14,450원), 태국 2(유심사 1일 300원 · 방콕·치앙마이 3일 14,450원), 대만 2(링심 1일 760원 16% · 유심사 3일 12,580원).
- `channelProductNo`(네이버 상품번호)를 `essentials.json`에 남겨 두면 나중에 `naver.me` 링크가 살아 있는지 대조할 수 있습니다. `curl -sIL https://naver.me/XXXX | grep location` → `/affiliates/{id}?channelProductNo=…`.
- 홈 `#essentials`의 eSIM 그룹은 13종(4열). `build.py: CITY_COUNTRY` 가 카드 도시→국기 코드를 정합니다(태국·대만 추가됨).
- 도시 허브 비교 블록은 `build_pages.py: ESIM_PICK`(나라별 2~3개 id·제목·리드) + `hub_esim_section()`. 도시 허브 목차에 `eSIM n` 칩이 자동으로 붙습니다.
- `/baggage` 하단 「도착해서 바로 쓰려면」은 `BAG_ESIM_IDS`(나라별 3일 무제한 4종).
- 출국 체크리스트는 `data/checklist.json` 의 국가별 `links` 배열에 상품 id를 넣으면 그 나라 패널 하단에 링크 줄로 나옵니다.

### 2. 오래 쓰는 여행 장비 (쿠팡, `category: "여행장비"`)

- `ESS_GROUPS` 두 번째 그룹. 홈에서는 `.ess-grid-4` 카드(썸네일·가격·정가 취소선), `/baggage` `#longuse` 에서는 `.gear` 카드(스펙 3줄·배지)로 같은 데이터를 씁니다.
- 상품에 추가로 쓰는 필드: `badge`("기내 반입(미확장)"·"위탁 전용"·"기내 반입 가능(37Wh)" 등), `specs`(문자열 배열 3줄), `itemId`.
- `/baggage` 카드 렌더는 `build_pages.py: GEAR_IDS` + `gear_cards()`. 순서를 바꾸려면 이 배열만 고치면 됩니다.
- 쿠팡 표시가는 옵션(색상·사이즈)에 따라 달라지므로 `caution` 에 기준 옵션과 확인일을 적어 두었습니다.
