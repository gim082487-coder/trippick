# 트립픽 (trippick)

여행 코스·가이드투어·숙소·항공을 같은 기준(실질 1인가, 현장 추가금, 취소 규정)으로 비교하는 여행 정보 사이트입니다.
`tour_hub/`에서 정적 HTML을 생성하고, `deploy_site/`가 실제로 서빙되는 산출물입니다.

- 운영 주소: <https://trippick-kr.netlify.app>
- 기술: 파이썬 3로 만든 정적 사이트 생성기 (프레임워크·DB·서버 없음)

## 구성

| 경로 | 내용 |
|---|---|
| `deploy_site/` | 배포본. 이 폴더를 그대로 서빙하면 사이트가 됩니다. |
| `tour_hub/` | 소스. 빌드 스크립트·데이터·본문·이미지 |
| `tour_hub/build.py` | `index.html`(홈) 생성: 상품 카드, 예산 계산기, JSON-LD, 광고 슬롯 |
| `tour_hub/build_pages.py` | 가이드 44편·신뢰 페이지 4종·도시 페이지 7곳·`cities/`·`sitemap.xml`·`assets/site.css` 생성 |
| `tour_hub/template.html` | 홈 템플릿(디자인 토큰·CSS·섹션 마커) |
| `tour_hub/data/tours.json` | 여행 상품 57개 (가격·포함·불포함·취소 규정·제휴 링크) |
| `tour_hub/data/essentials.json` | 여행 필수품·교통패스·eSIM·공항픽업 22종 |
| `tour_hub/data/gifts.json` | 나라별 선물·기념품 6개 지역 35종(가격·구매처·반입 주의) |
| `tour_hub/data/tripcom.json` | 트립닷컴 제휴 링크 44개 — 숙소 15개 도시·항공 6개 노선 + 입장권 7개 도시·공항픽업 8개 공항·렌터카 1곳 + eSIM·유심 5개 도시·공항철도 2개 노선 |
| `tour_hub/data/courses.json` | 추천 코스 5개(일차별 구성) |
| `tour_hub/data/guides.json` | 가이드 44편 메타데이터(제목·설명·관련 상품) |
| `tour_hub/data/guide_extra.json` | 가이드 44편의 검색 필터 메타(지역·주제·연결 도시)와 요약 박스 문구(결론 1줄·확인값 2개) |
| `tour_hub/data/restaurants.json` | 도시 7곳 검증 맛집 35곳(영업 상태·가격·영업시간·휴무·지도 place_id) |
| `tour_hub/data/checklist.json` | 출국 준비 데이터 — 입국서류·기내반입 + 환전 카드 3종·여행자보험 3곳 비교 |
| `tour_hub/data/city_hubs.json` | 도시별 페이지 7곳 정의(오사카·도쿄·후쿠오카·다낭·방콕·타이베이·제주) — 제목·설명·연결할 상품/맛집/선물/숙소/가이드 |
| `tour_hub/content/guides/*.html` | 가이드 본문 (HTML 조각) |
| `tour_hub/content/pages/*.html` | 소개·문의·개인정보·약관 본문 |
| `tour_hub/tools/` | 데이터 가공 스크립트 |

## 빌드

```bash
cd tour_hub

# 홈(index.html) — tour_hub/index.html에 생성
python3 build.py

# 가이드·신뢰 페이지·sitemap — tour_hub/에 생성
python3 build_pages.py

# 배포 폴더로 바로 생성 + 내부 링크 전수 검사
python3 build_pages.py --out ../deploy_site --base https://trippick-kr.netlify.app --check-links
```

홈만 다시 만들 때는 `build.py`를, 가이드·CSS·sitemap만 다시 만들 때는 `build_pages.py`를 실행합니다.
`build_pages.py`는 `deploy_site/assets/site.css`를 `template.html`의 `<style>` + `content/pages.css`로 다시 씁니다.
`index.html`·`sitemap.xml`·`about/privacy/terms/contact.html`은 `build.py`/`build_pages.py`가 만든 것을 `deploy_site/`로 복사합니다.

## 호스팅

정적 사이트라 어디든 올릴 수 있습니다. Cloudflare Pages에서는

- 빌드 명령: 없음(비워 둠)
- 출력 디렉터리: `deploy_site`

로 지정하면 빌드 없이 `deploy_site/`가 그대로 서빙됩니다.

## 도시별 페이지와 사이트맵

`build_pages.py`는 `/osaka`·`/tokyo`·`/fukuoka`·`/danang`·`/bangkok`·`/taipei`·`/jeju`(루트의 `osaka.html` 등)와 `/cities/` 인덱스를 만듭니다.
각 페이지는 그 도시의 투어·패키지, 검증한 현지 맛집, 나라별 선물·기념품, 트립닷컴 숙소·항공권, 관련 가이드를 한 화면에 모읍니다.
`sitemap.xml`은 홈1 + `cities/`1 + 도시 7 + 가이드 인덱스1 + 가이드 44 + 신뢰 페이지 4 = **58 URL**입니다.
홈의 `#tripcom`은 숙소·항공에 이어 **입장권·액티비티(7개 도시)**·**공항픽업·렌터카(8개 공항+제주 렌터카)** 카드를 같은 섹션에 두고, 각 도시 페이지의 숙소 섹션에도 그 도시의 입장권·픽업 카드를 함께 노출합니다.

홈의 ‘지역·투어’ 섹션은 도시 페이지가 있는 7개 도시만 먼저 펼치고, 나머지 15개 도시 36개 상품은 한 번 접어 둡니다(`<details>`).
접힌 안에도 카드·비교표·제휴 링크가 그대로 있어 크롤링에는 영향이 없고, 도시 칩·검색·해시 링크로 들어오면 JS가 해당 접기를 자동으로 엽니다.

## 가이드 검색·필터와 요약 박스 (v15)

`/guides/` 상단에는 실시간 키워드 검색창과 여행지(일본·베트남·태국·대만·괌·국내·유럽·미주·대양주·중국·공통) · 주제(맛집·선물·숙소·교통패스·eSIM·패키지·가성비·시즌·서류) 필터가 있습니다.
검색·필터는 서버 없이 카드의 `data-q`·`data-region`·`data-tags` 속성만으로 동작하고, `?q=`·`?region=`·`?tag=` 주소로 들어와도 같은 결과가 열립니다(`/` 키로 검색창 포커스).

홈 히어로의 검색창은 입력하는 즉시 `#tpSearch` 색인(가이드 44 + 투어 57 + 도시 7)에서 결과를 드롭다운으로 보여 줍니다. 가이드를 누르면 그 글로, 투어를 누르면 `#regions`에서 같은 검색어로 필터된 목록으로 이동합니다.

모든 가이드 본문 맨 위에는 `3줄 요약` 박스(결론 1줄 + 확인값 2개 + 최종 검증일 + 그 도시 페이지 링크)가, 본문 아래에는 `이 여행에서 바로 쓰는 것` 블록(그 도시 eSIM·입장권·공항철도·공항픽업 실링크 3개 + 같은 도시 가이드 3편 + 도시 페이지 링크)이 자동으로 붙습니다.

## 광고 슬롯

애드센스 승인 전에는 광고 코드를 넣지 않았습니다. 슬롯은 `class="adslot"` 컨테이너로 자리를 잡아 두고,
승인 전에는 **내부 추천 배너**가 보입니다(빈 광고 박스·깨진 레이아웃 없음).
승인 후에는 컨테이너 안의 주석을 풀고 `ca-pub-…`와 `data-ad-slot` 값만 바꾸면 됩니다.

- 홈: `build.py`의 `ad_slot()` — 코스/지역/트립닷컴 섹션 사이 3곳
- 가이드: `build_pages.py`의 `ad_slot()` — 상단·본문 중간·하단 3곳
- CSS: `template.html`의 `.adslot` 블록 (`:has(ins.adsbygoogle)`로 폴백 자동 숨김)

## 제휴 고지

이 사이트는 네이버 여행 커넥트·네이버 쇼핑 커넥트·쿠팡 파트너스·트립닷컴 파트너스에 참여하고 있습니다.
링크를 통한 예약·구매 시 판매자로부터 수수료를 받을 수 있으며, 구매자가 지불하는 가격에는 영향을 주지 않습니다.
가격·취소 규정은 각 판매처 상세페이지를 최종 기준으로 안내합니다.

## 변경 기록

- **v15 (2026-11-18)** — `/guides/` 실시간 검색·여행지/주제 필터, 홈 히어로 검색 드롭다운(가이드·투어·도시 색인 108건), 가이드 44편 상단 `3줄 요약` 박스와 `최종 검증일` 표기 통일, 가이드 하단 `이 여행에서 바로 쓰는 것` 블록(도시 허브 + 같은 도시 가이드 3편 + eSIM·입장권·공항철도·공항픽업 실링크 3개). 트립닷컴 eSIM·유심 5개 도시와 공항철도 2개 노선(스카이라이너·난카이 라피트) 7개 링크를 새로 발급해 홈 `#tripcom`·`#checklist`·도시 허브 7곳에 연결.
- **v14 (2026-11-18)** — 트립닷컴 입장권 7개 도시·공항픽업 8개 공항·제주 렌터카 1곳(16종) 추가, 홈 `#tripcom`과 도시 7곳 숙소 섹션에 노출. 제주 맛집 5곳(우진해장국·올래국수·자매국수·돈사돈·미영이네) 검증 추가. 출국 체크리스트 아래에 환전 카드 3종(트래블월렛·트래블로그·토스뱅크 외화통장)과 여행자보험 3곳(카카오페이손해보험·삼성화재 다이렉트·마이뱅크) 비교 카드 신설.
